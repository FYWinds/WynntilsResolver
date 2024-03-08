"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-29 13:23:08
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-08 15:47:46
FilePath     : /wynntilsresolver/blocks/identification.py
"""

import json
from dataclasses import dataclass
from typing import Dict, List

from wynntilsresolver.exception import MissingInfo
from wynntilsresolver.startup import ID_TABLE_PATH, ITEMDB_PATH

from .block import Block
from .name import Name

with open(ITEMDB_PATH, encoding="utf-8") as f:
    ITEMDB = json.load(f)

with open(ID_TABLE_PATH, encoding="utf-8") as f:
    ID_TABLE = json.load(f)


def _extract_item_name(blocks: List[Block]) -> str:
    for block in blocks:
        if isinstance(block, Name):
            return block.name
    else:
        raise MissingInfo("Item name not found when trying to parse identifications.")


def _id_from_str(id: str) -> int:
    return ID_TABLE[id]


def _id_from_int(id: int) -> str:
    return next(k for k, v in ID_TABLE.items() if v == id)


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
        id_value = round(id_base * (roll / 100))
        return cls(id, internal_id, id_base, roll, id_value)

    @classmethod
    def from_extend(cls, id, data: List[int]) -> "Identification":
        base = Block.decode_variable_sized_int(data)
        roll = data[0]
        del data[0]
        id_name = _id_from_int(id)
        id_value = round(base * (roll / 100))
        return cls(id_name, id, base, roll, id_value)

    def to_simple(self) -> List[int]:
        # TODO
        raise NotImplementedError

    def to_extend(self) -> List[int]:
        # TODO
        raise NotImplementedError


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

        identifications: List[Identification] = []
        name = _extract_item_name(parsed_blocks)
        item_identifications_meta = ITEMDB[name]["identifications"]

        if not extend:
            for id, meta in item_identifications_meta.items():
                if isinstance(meta, int):
                    # pre-identified
                    identifications.append(Identification(id, _id_from_str(id), meta, -1, meta))

            # Truncate data to the length of ids
            id_data = data[: id_num * 2]
            del data[: id_num * 2]

            for id, roll in zip(id_data[::2], id_data[1::2]):
                id_name = _id_from_int(id)
                id_meta = item_identifications_meta[id_name]
                identifications.append(Identification.from_simple(id_name, id, id_meta, roll))

        else:
            # Number of pre-identified ids
            id_num_pre = data[0]
            del data[0]
            for _ in range(id_num_pre):
                id = data[0]
                del data[0]
                id_str = _id_from_int(id)
                value = cls.decode_variable_sized_int(data)
                identifications.append(Identification(id_str, id, value, -1, value))
            for _ in range(id_num):
                id = data[0]
                del data[0]
                identifications.append(Identification.from_extend(id, data))

        return cls(identifications)

    def to_bytes(self, parsed_blocks: List[Block], extend: bool = False) -> List[int]:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"Identifications({self.identifications})"

    def __str__(self) -> str:
        return f"{self.identifications}"
