"""
Author       : FYWinds i@windis.cn
Date         : 2024-01-13 23:06:55
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-01 16:55:14
FilePath     : /src/wynntilsresolver/blocks/block.py
"""

from abc import ABC, abstractmethod
from typing import List

from wynntilsresolver.exception import InvalidStartByte


class Block(ABC):
    _start_byte: int

    @classmethod
    def from_bytes(cls, data: List[int], **kwargs):
        # Using deque internally to allow for efficient popping from the left
        if data[0] != cls._start_byte:
            raise InvalidStartByte(f"Invalid start byte for block {cls.__name__}")
        del data[0]

    @abstractmethod
    def to_bytes(self, **kwargs) -> List[int]:
        raise NotImplementedError

    def encode_with_start(self, data: List[int]) -> List[int]:
        return [self._start_byte] + data

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @classmethod
    def decode_string(cls, data: List[int]) -> str:
        name = ""
        for i, byte in enumerate(data):
            if byte == 0:
                break
            name += chr(byte)
        del data[: i + 1]
        return name

    def encode_string(self, string: str) -> List[int]:
        return [ord(x) for x in string] + [0]

    @classmethod
    def decode_variable_sized_int(cls, data: List[int]) -> int:
        """
        Decode an integer using the variable-size encoding scheme.

        The encoding scheme is as follows:
        - The most significant bit is used as a continuation bit
        - The remaining 7 bits are used to store the actual value
        - The number is then decoded using the ZigZag encoding scheme
        """
        num = 0
        shift = 0
        for byte in data:
            num |= (byte & 0x7F) << shift
            if not byte & 0x80:
                break
            shift += 7
        else:
            raise ValueError("Invalid variable-sized integer")
        del data[: (shift // 7) + 1]
        return (num >> 1) ^ -(num & 1)

    def encode_variable_sized_int(self, num: int) -> List[int]:
        """
        Encode an integer using the variable-size encoding scheme.

        The encoding scheme is as follows:
        - The number is encoded using the ZigZag encoding scheme
        - The most significant bit is used as a continuation bit
        - The remaining 7 bits are then used to store the actual value
        """
        # ZigZag encoding
        num = (num << 1) ^ (num >> 0x3F)

        # Encode the integer
        result = []
        while num >= 0x80:
            result.append((num & 0x7F) | 0x80)
            num >>= 7
        result.append(num)
        return result
