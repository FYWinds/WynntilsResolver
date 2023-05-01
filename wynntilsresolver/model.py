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
    ids: list[float]
    powders: list[Powder]
    rerolls: int


__all__ = ["Item"]
