"""
Author       : FYWinds i@windis.cn
Date         : 2023-05-01 09:20:21
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2023-05-09 12:36:10
FilePath     : /src/wynntilsresolver/model.py

Copyright (c) 2023 by FYWinds
All Rights Reserved.
Any modifications or distributions of the file
should mark the original author's name.
"""

import dataclasses
import json
from enum import Enum
from typing import List


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
    ids: List[int] = dataclasses.field(default_factory=list)
    """The roll values of the item, sorted in wynntils' item identification order
    Can calculate by multiplying the id's base value"""
    powders: List[Powder] = dataclasses.field(default_factory=list)
    """Powders on the item, without tier"""
    rerolls: int = 0
    """Rerolls of the item"""


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is Powder:
            return str(obj)
        elif dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        else:
            return json.JSONEncoder.default(self, obj)


__all__ = ["Item", "CustomEncoder", "Powder"]
