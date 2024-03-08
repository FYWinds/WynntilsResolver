"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-29 18:50:29
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-02-29 22:43:35
FilePath     : /src/wynntilsresolver/blocks/reroll.py
"""

from .block import Block


class Reroll(Block):
    _start_byte = 5
    rerolls: int

    def __init__(self, rerolls: int) -> None:
        self.rerolls = rerolls

    @classmethod
    def from_bytes(cls, data, **kwargs) -> "Reroll":
        super().from_bytes(data)
        reroll = cls(data[0])
        del data[0]
        return reroll

    def to_bytes(self):
        return self.encode_with_start([self.rerolls])

    def __str__(self) -> str:
        return f"{self.rerolls}"

    def __repr__(self) -> str:
        return f"Reroll({self.rerolls})"
