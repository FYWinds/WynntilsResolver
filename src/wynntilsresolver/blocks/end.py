"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-28 23:09:43
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-02-29 18:18:53
FilePath     : /src/wynntilsresolver/blocks/end.py
"""

from typing import List

from .block import Block


class End(Block):
    _start_byte = 255

    @classmethod
    def from_bytes(cls, data: List[int], **kwargs) -> "End":
        super().from_bytes(data)
        return cls()

    def to_bytes(self) -> List[int]:
        return self.encode_with_start([])

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"End({self._start_byte})"
