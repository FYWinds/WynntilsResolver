"""
Author       : FYWinds i@windis.cn
Date         : 2024-01-13 23:06:52
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-02-29 18:20:02
FilePath     : /src/wynntilsresolver/blocks/version.py
"""

from typing import List

from .block import Block


class Version(Block):
    version: int

    _start_byte: int = 0

    def __init__(self, version) -> None:
        self.version = version

    @classmethod
    def from_bytes(cls, data: List[int], **kwargs) -> "Version":
        super().from_bytes(data)
        v = cls(data[0])
        del data[0]
        return v

    def to_bytes(self) -> List[int]:
        return self.encode_with_start([self.version])

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"Version({self.version})"
