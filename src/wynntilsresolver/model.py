"""
Author       : FYWinds i@windis.cn
Date         : 2023-05-01 09:20:21
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2023-05-01 12:31:40
FilePath     : /src/wynntilsresolver/model.py

Copyright (c) 2023 by FYWinds
All Rights Reserved.
Any modifications or distributions of the file
should mark the original author's name.
"""

import dataclasses
from enum import Enum
import json


class Powder(Enum):
    EARTH = 0
    THUNDER = 1
    WATER = 2
    FIRE = 3
    AIR = 4

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


@dataclasses.dataclass(frozen=True)
class Item:
    name: str
    """The name of the item"""
    ids: list[float]
    """The roll values of the item, sorted in wynntils' item identification order
    Can calculate by multiplying the id's base value"""
    powders: list[Powder]
    """Powders on the item, without tier"""
    rerolls: int
    """Rerolls of the item"""


class CustomeEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is Powder:
            return str(obj)
        elif dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        else:
            return json.JSONEncoder.default(self, obj)


__all__ = ["Item", "CustomeEncoder", "Powder"]