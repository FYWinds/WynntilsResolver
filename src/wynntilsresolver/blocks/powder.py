"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-29 18:42:50
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-01 20:49:32
FilePath     : /src/wynntilsresolver/blocks/powder.py
"""

import math
from typing import List

from .block import Block

_POWDER_ELEMENTS = ["E", "T", "W", "F", "A"]


class Powder(Block):
    _start_byte = 4
    powder_slots: int
    powders: List[str]

    def __init__(self, powder_slots: int, powders: List[str]) -> None:
        self.powder_slots = powder_slots
        self.powders = powders

    @classmethod
    def from_bytes(cls, data: List[int], **kwargs) -> "Powder":
        super().from_bytes(data)
        powder_slots = data[0]
        del data[0]
        powder_num = data[0]
        del data[0]

        # change the bytes to binary and pad it to 8 bits
        powder_binary = "".join([format(powder, "b").zfill(8) for powder in data[: math.ceil(powder_num * 5 / 8)]])
        del data[: math.ceil(powder_num * 5 / 8)]

        # 5 bit per powder
        powders_raw = [powder_binary[i : i + 5] for i in range(0, len(powder_binary), 5)]

        # convert to int
        powders_bin = [int(powder, 2) - 1 for powder in powders_raw if int(powder) != 0]
        powders = [f"{_POWDER_ELEMENTS[powder // 6]}{powder % 6 + 1}" for powder in powders_bin]

        return cls(powder_slots, powders)

    def to_bytes(self) -> List[int]:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.powders}, slots: {len(self.powders)}/{self.powder_slots}"

    def __repr__(self) -> str:
        return f"Powder({self.powders}, slots: {len(self.powders)}/{self.powder_slots})"
