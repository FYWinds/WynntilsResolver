"""
Author       : FYWinds i@windis.cn
Date         : 2023-12-14 09:22:08
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-01-13 23:01:57
FilePath     : /src/wynntilsresolver/item.py
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

_SUPPORTED_VERSION = [1]

_TYPE_GEAR_ITEM = 0
_TYPE_CUSTOM_ITEM = 1
_TYPE_RECIPE_ITEM = 2
Data = List[int]


def utf16_to_array(utf16: str) -> List[int]:
    """Decode the int array from utf16 string.

    Args:
        utf16 (str): The utf16 string from Artemis.

    Returns:
        List[int]: The int array.
    """
    li: List[int] = []
    for char in utf16:
        hex_num = format(ord(char), "x")
        li.append(int(hex_num[-4:-2], 16))
        li.append(int(hex_num[-2:], 16))

    return li


def parse_name(data: Data) -> Tuple[str, Data]:
    # Name
    if data[0] != 2:
        raise ValueError(f"Corrupted Block Indicator: {data[0]} - name")
    name = ""
    for index, v in enumerate(data[1:]):
        if v == 0:
            data = data[index + 2 :]  # chop off the letter and the null terminator
            break
        name += chr(v)
    return name, data


def parse_identification(
    data: Data, item_metadata: Dict[str, Dict], id_map: Dict[str, int]
) -> Tuple[List["Identification"], Data]:
    # Identifications
    if data[0] != 3:
        raise ValueError(f"Corrupted Block Indicator: {data[0]} - identifications")
    id_num = data[1]
    id_type = data[2]

    data = data[3:]  # chop off the identification header

    identifications = []
    # Simple
    if id_type == 0:
        id_data = [data[i : i + 2] for i in range(0, id_num * 2, 2)]

        for id in item_metadata["identifications"].keys():
            if id_map[id] not in {x[0] for x in id_data}:
                identifications.append(
                    Identification(
                        id=id,
                        internal_id=id_map[id],
                        base=item_metadata["identifications"][id],
                        roll=-1,  # -1 represents pre-identified
                        value=item_metadata["identifications"][id],
                    )
                )
            else:
                id_numeric = id_map[id]
                id_roll = [x[1] for x in id_data if x[0] == id_numeric][0]
                try:
                    id_metadata: Dict[str, int] = item_metadata["identifications"][id]
                    id_base = id_metadata["raw"]
                except KeyError:
                    raise ValueError(f"Data Not Given: {id}")
                id_value = round(id_base * (id_roll / 100))
                identifications.append(
                    Identification(id=id, internal_id=id_numeric, base=id_base, roll=id_roll, value=id_value)
                )
        data = data[id_num * 2 :]

    # Extended
    elif id_type == 1:
        raise NotImplementedError("Extended identification is not supported yet.")
    else:
        raise ValueError(f"Unknown identification type: {id_type}")

    return identifications, data


_POWDER_ELEMENTS = ["E", "T", "W", "F", "A"]


def parse_powders(data: Data):
    # Powders
    if data[0] != 4:
        raise ValueError(f"Corrupted Block Indicator: {data[0]} - powders")
    powder_bytes = data[1]

    # change the bytes to binary and pad it to 8 bits
    powder_binary = "".join([format(powder, "b").zfill(8) for powder in data[2 : 2 + powder_bytes]])
    # 5 bit per powder
    powders_raw = [powder_binary[i : i + 5] for i in range(0, len(powder_binary), 5)]
    # convert to int
    powders_bin = [int(powder, 2) for powder in powders_raw]
    powders = [f"{_POWDER_ELEMENTS[powder // 6]}{powder % 6}" for powder in powders_bin]

    return powders, data[2 + powder_bytes :]


def parse_rerolls(data: Data) -> Tuple[int, Data]:
    # Rerolls
    rerolls = -1
    if data[0] == 5:
        rerolls = data[1]
        data = data[2:]
    return rerolls, data


def parse_shiny(data: Data, shiny_map: List[Dict]) -> Tuple[Union[None, "Shiny"], Data]:
    # Shiny
    shiny = None
    if data[0] == 6:
        shiny_data = [x for x in shiny_map if x["id"] == data[1]][0]
        shiny = Shiny(
            name=shiny_data["key"],
            internal_id=data[1],
            display_name=shiny_data["displayName"],
            value=shiny_data[data[2]]["value"],
        )
        data = data[3:]
    return shiny, data


@dataclass
class Identification:
    id: str
    """Key of the identification. From Wynncraft official API."""
    internal_id: int
    """Numeric ID of the identification. From Artemis Data."""
    base: int
    roll: int
    """Roll of the identification. -1 represents pre-identified."""
    value: int


@dataclass
class Shiny:
    name: str
    """Key of the shiny. From Artemis Data."""
    internal_id: int
    """Internal ID of the shiny. From Artemis Data."""
    display_name: str
    """Display name of the shiny. From Artemis Data."""
    value: int


class Item:
    version: int
    type: int

    data: Data

    @staticmethod
    def from_bytes(
        data: List[int], id_map: Dict[str, int], shiny_map: List[Dict], item_map: Dict
    ) -> Union["GearItem", "CustomItem", "RecipeItem"]:
        """Decode the item from bytes.

        Args:
            bytes (List[int]): The bytes from Artemis.

        Raises:
            ValueError: Version not supported
            ValueError: Unknown item type
            ValueError: Unknown version

        Returns:
            Union[Item, GearItem, CustomItem, RecipeItem]: The Item Object.
        """
        if data[0] != 0:
            raise ValueError(f"Corrupted Block Indicator: {data[0]} - start")
        if (version := data[2]) not in _SUPPORTED_VERSION:
            raise ValueError(f"Unsupported version: {data[0]}")

        # V1 support
        if version == 1:
            if data[2] != 1:
                raise ValueError(f"Corrupted Block Indicator: {data[3]} - type")
            if (item_type := data[3]) == _TYPE_GEAR_ITEM:
                return GearItem.from_data(data, id_map, shiny_map, item_map)
            elif item_type == _TYPE_CUSTOM_ITEM:
                return CustomItem.from_data(data, id_map, shiny_map, item_map)
            elif item_type == _TYPE_RECIPE_ITEM:
                return RecipeItem.from_data(data, id_map, shiny_map, item_map)
            else:
                raise ValueError(f"Unknown item type: {item_type}")

        raise ValueError(f"Unknown version: {version}")

    @staticmethod
    def from_utf16(
        utf16: str, id_map: Dict[str, int], shiny_map: List[Dict], item_map: Dict
    ) -> Union["GearItem", "CustomItem", "RecipeItem"]:
        """Decode the item from utf16 string.

        Args:
            utf16 (str): The utf16 string from Artemis.

        Raises:
            ValueError: Version not supported
            ValueError: Unknown item type
            ValueError: Unknown version

        Returns:
            Union[Item, GearItem, CustomItem, RecipeItem]: The Item Object.
        """
        data = utf16_to_array(utf16)
        return Item.from_bytes(data, id_map, shiny_map, item_map)

    @staticmethod
    def from_data(
        data: Data, id_map: Dict[str, int], shiny_map: List[Dict], item_map: Dict
    ) -> Union["GearItem", "CustomItem", "RecipeItem"]:
        raise NotImplementedError("This type of item is not supported yet.")

    def dump(self) -> Dict:
        """Convert the item to json.

        Returns:
            Dict: The json object.
        """
        raise NotImplementedError("This type of item is not supported yet.")


class GearItem(Item):
    name: str
    identifications: List[Identification]
    """Ordered identifications of the item."""
    powders: List[str]
    """Powders in the form of `["F6", "F6"]`"""
    rerolls: int
    """Number of rerolls, `-1` represents non-identified."""
    shiny: Union[None, Shiny]
    """Shiny stat, `None` if not shiny."""

    def __init__(
        self,
        name: str,
        identifications: List[Identification],
        powders: List[str],
        rerolls: int,
        shiny: Union[None, Shiny],
        data: Data,
    ) -> None:
        self.data = data
        self.name = name
        self.identifications = identifications
        self.powders = powders
        self.rerolls = rerolls
        self.shiny = shiny

    @staticmethod
    def from_data(data: Data, id_map: Dict[str, int], shiny_map: List[Dict], item_map: Dict) -> "GearItem":
        original_data = data.copy()

        data = data[4:]  # chop off the header

        name, data = parse_name(data)

        try:
            item_metadata = item_map[name]
        except KeyError:
            raise ValueError(f"Unknown item name: {name}")

        identifications, data = parse_identification(data, item_metadata, id_map)

        rerolls, data = parse_rerolls(data)

        # Shiny
        shiny, data = parse_shiny(data, shiny_map)

        return GearItem(
            name=name, identifications=identifications, powders=[], rerolls=rerolls, shiny=shiny, data=original_data
        )

    def dump(self) -> Dict:
        return {
            "name": self.name,
            "identifications": [x.__dict__ for x in self.identifications],
            "powders": self.powders,
            "rerolls": self.rerolls,
            "shiny": self.shiny.__dict__ if self.shiny else None,
        }


class CustomItem(Item): ...


class RecipeItem(Item): ...
