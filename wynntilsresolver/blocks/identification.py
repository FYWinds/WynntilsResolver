"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-29 13:23:08
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-25 02:39:22
FilePath     : /wynntilsresolver/blocks/identification.py
"""

import math
from dataclasses import dataclass
from typing import Dict, Iterator, List, Union

from wynntilsresolver.datastore import data_store
from wynntilsresolver.exception import MissingInfo

from .block import Block
from .name import Name
from .version import extract_version

# Flag bits of a V3 identification entry; bit 1 (icon prefix) only affects Artemis' rendering.
_PERFECT_INTERNAL_ROLL_FLAG = 1
_VANILLA_METER_FLAG = 1 << 2


def _extract_item_name(blocks: List[Block]) -> str:
    for block in blocks:
        if isinstance(block, Name):
            return block.name
    else:
        raise MissingInfo("Item name not found when trying to parse identifications.")


def _is_inverted(id_name: str) -> bool:
    """Artemis keeps spell costs on the opposite sign of the API (SpellStatType.calculateAsInverted)."""
    return id_name.endswith("SpellCost")


_IdMeta = Union[int, Dict[str, int]]
"""Item database entry of one identification: a fixed value, or `{"min", "raw", "max"}` when rolled."""


def _pre_identified(meta: Dict[str, _IdMeta]) -> Iterator["Identification"]:
    for id_name, id_meta in meta.items():
        if isinstance(id_meta, int):
            yield Identification(id_name, data_store.id_from_str(id_name), id_meta, -1, id_meta)


def _rolled_meta(meta: Dict[str, _IdMeta], id_name: str) -> Dict[str, int]:
    id_meta = meta[id_name]
    if isinstance(id_meta, int):
        raise MissingInfo(f"{id_name} is pre-identified in the item database but encoded as rolled.")
    return id_meta


def estimate_internal_roll(base: int, value: int, perfect: bool, inverted: bool) -> int:
    """Estimate the internal roll that produced `value` from `base`, both on the API's sign.

    Port of Artemis' StatCalculator.calculateInternalRollRange with plain float math:
    the valid roll bounds are computed, then the roll closest to value / base is picked within them.
    """
    # The roll range and the perfect roll are decided on Artemis' sign, the bounds on the API's sign.
    artemis_base = -base if inverted else base
    roll_min, roll_max = (30, 130) if artemis_base > 0 else (70, 130)
    if perfect:
        return roll_max if artemis_base > 0 else roll_min

    lower = (value * 100 - 50) / base
    higher = (value * 100 + 49) / base
    if base < 0:
        lower, higher = higher, lower

    # Not flagged perfect: exclude the perfect roll from the range when another roll still fits.
    if artemis_base > 0 and higher >= roll_max and math.ceil(lower) <= roll_max - 1:
        roll_max -= 1
    elif artemis_base < 0 and lower <= roll_min and math.floor(higher) >= roll_min + 1:
        roll_min += 1

    low = max(math.ceil(lower), roll_min)
    high = max(low, min(math.floor(higher), roll_max))
    return min(max(round(value * 100 / base), low), high)


@dataclass
class Identification:
    id: str
    """Key of the identification. From Wynncraft official API."""
    internal_id: int
    """Numeric ID of the identification. From Artemis Data."""
    base: int
    """Base value of the identification. same as value if pre-identified."""
    roll: int
    """Roll of the identification. -1 represents pre-identified."""
    value: int
    """Value of the identification. Two digits after the decimal point are povided if comes from roll."""

    @classmethod
    def from_simple(cls, id: str, internal_id: int, meta: Dict[str, int], roll: int) -> "Identification":
        id_base = meta["raw"]
        id_value = cls.special_round(id_base * (roll / 100))
        return cls(id, internal_id, id_base, roll, id_value)

    @classmethod
    def from_extend(cls, id, data: List[int]) -> "Identification":
        base = Block.decode_variable_sized_int(data)
        roll = data[0]
        del data[0]
        id_name = data_store.id_from_int(id)
        id_value = cls.special_round(base * (roll / 100))
        return cls(id_name, id, base, roll, id_value)

    def to_simple(self) -> List[int]:
        # TODO
        raise NotImplementedError

    def to_extend(self) -> List[int]:
        # TODO
        raise NotImplementedError

    @classmethod
    def from_value(cls, id_name: str, internal_id: int, base: int, data: List[int]) -> "Identification":
        """V3 entry: `[value varint][flags][meter]?`, value on Artemis' sign; `base` already on the API's sign."""
        value = Block.decode_variable_sized_int(data)
        flags = data[0]
        del data[0]
        if flags & _VANILLA_METER_FLAG:
            # Vanilla meter offset (0-35): a coarser percentage than what the value yields, so it is dropped.
            del data[0]

        inverted = _is_inverted(id_name)
        if inverted:
            value = -value
        roll = estimate_internal_roll(base, value, bool(flags & _PERFECT_INTERNAL_ROLL_FLAG), inverted)
        return cls(id_name, internal_id, base, roll, value)

    @staticmethod
    def special_round(num: float) -> int:
        return math.floor(num + 0.5)


class Identifications(Block):
    _start_byte = 3
    identifications: List[Identification]

    def __init__(self, identifications: List[Identification]) -> None:
        self.identifications = identifications

    @classmethod
    def from_bytes(cls, data: List[int], parsed_blocks: List[Block], **kwargs) -> "Identifications":
        super().from_bytes(data)
        # number of non-pre-identified ids
        id_num = data[0]
        del data[0]
        # 1 -> extended encoding
        extend = bool(data[0])
        del data[0]

        name = _extract_item_name(parsed_blocks)
        item_identifications_meta = data_store.itemdb[name]["identifications"]

        if extract_version(parsed_blocks) >= 2:
            return cls(cls._decode_v3(data, id_num, extend, item_identifications_meta))
        return cls(cls._decode_v1(data, id_num, extend, item_identifications_meta))

    @staticmethod
    def _decode_v1(data: List[int], id_num: int, extend: bool, meta: Dict[str, _IdMeta]) -> List[Identification]:
        """V1/V2: each id is `[id][base varint]?[roll]`."""
        identifications: List[Identification] = []

        if not extend:
            identifications.extend(_pre_identified(meta))

            # Truncate data to the length of ids
            id_data = data[: id_num * 2]
            del data[: id_num * 2]

            for id, roll in zip(id_data[::2], id_data[1::2]):
                id_name = data_store.id_from_int(id)
                identifications.append(Identification.from_simple(id_name, id, _rolled_meta(meta, id_name), roll))

        else:
            # Number of pre-identified ids
            id_num_pre = data[0]
            del data[0]
            for _ in range(id_num_pre):
                id = data[0]
                del data[0]
                id_str = data_store.id_from_int(id)
                value = Block.decode_variable_sized_int(data)
                identifications.append(Identification(id_str, id, value, -1, value))
            for _ in range(id_num):
                id = data[0]
                del data[0]
                identifications.append(Identification.from_extend(id, data))

        return identifications

    @staticmethod
    def _decode_v3(data: List[int], id_num: int, extend: bool, meta: Dict[str, _IdMeta]) -> List[Identification]:
        """V3: each id is `[id][base varint]?[value varint][flags][meter]?`; the roll is estimated from the value."""
        identifications: List[Identification] = []

        if extend:
            # Number of pre-identified ids, each `[id][base varint]`
            id_num_pre = data[0]
            del data[0]
            for _ in range(id_num_pre):
                id = data[0]
                del data[0]
                id_name = data_store.id_from_int(id)
                base = Block.decode_variable_sized_int(data)
                if _is_inverted(id_name):
                    base = -base
                identifications.append(Identification(id_name, id, base, -1, base))
        else:
            identifications.extend(_pre_identified(meta))

        for _ in range(id_num):
            id = data[0]
            del data[0]
            id_name = data_store.id_from_int(id)
            if extend:
                base = Block.decode_variable_sized_int(data)
                if _is_inverted(id_name):
                    base = -base
            else:
                base = _rolled_meta(meta, id_name)["raw"]
            identifications.append(Identification.from_value(id_name, id, base, data))

        return identifications

    def to_bytes(self, parsed_blocks: List[Block], extend: bool = False) -> List[int]:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"Identifications({self.identifications})"

    def __str__(self) -> str:
        return f"{self.identifications}"
