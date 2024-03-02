"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-28 23:03:21
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-02-29 22:17:02
FilePath     : /src/wynntilsresolver/blocks/name.py
"""

from typing import List

from .block import Block


class Name(Block):
    _start_byte: int = 2
    name: str

    def __init__(self, name) -> None:
        self.name = name

    @classmethod
    def from_bytes(cls, data: List[int], **kwargs) -> "Name":
        super().from_bytes(data)
        return cls(name=cls.decode_string(data))

    def to_bytes(self) -> List[int]:
        return self.encode_with_start(self.encode_string(self.name))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Name({self.name})"
