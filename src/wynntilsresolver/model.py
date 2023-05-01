from dataclasses import dataclass
from enum import Enum


class Powder(Enum):
    EARTH = 0
    THUNDER = 1
    WATER = 2
    FIRE = 3
    AIR = 4


@dataclass(frozen=True)
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


__all__ = ["Item"]
