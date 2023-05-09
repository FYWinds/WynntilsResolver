"""
Author       : FYWinds i@windis.cn
Date         : 2023-05-01 09:08:08
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2023-05-09 12:38:27
FilePath     : /src/wynntilsresolver/resolver.py

Copyright (c) 2023 by FYWinds
All Rights Reserved.
Any modifications or distributions of the file
should mark the original author's name.
"""
import dataclasses
import math
import re
from re import Pattern
from typing import List

from .exceptions import ItemNotValidError
from .model import Item, Powder

_START = chr(0xF5FF0)
_END = chr(0xF5FF1)
_SEP = chr(0xF5FF2)
_RANGE = "[" + chr(0xF5000) + "-" + chr(0xF5F00) + "]"
_OFFSET = chr(0xF5000)

_ENCODED_PATTERN = (
    _START
    + r"(?P<Name>.+?)"
    + _SEP
    + r"(?P<Ids>"
    + _RANGE
    + r"*)(?:"
    + _SEP
    + r"(?P<Powders>"
    + _RANGE
    + r"+))?(?P<Rerolls>"
    + _RANGE
    + r")"
    + _END
)


class Resolver:
    def __init__(self, pattern: str = _ENCODED_PATTERN):
        self.pattern = re.compile(pattern)

    def get_pattern(self) -> Pattern:
        return self.pattern

    def decode(self, text: str) -> Item:
        if m := self.pattern.match(text):
            name = m.group("Name")
            ids = self._decode_numbers(m.group("Ids"))
            powders = self._decode_numbers(m.group("Powders"))
            rerolls = self._decode_numbers(m.group("Rerolls"))[0]
            return Item(name, ids, self._decode_powders(powders), rerolls)
        else:
            raise ItemNotValidError(f"Given text {text} is not a valid encoded item.")

    def decode_to_json(self, text: str) -> dict:
        return dataclasses.asdict(self.decode(text))

    def _decode_powders(self, powders: List[int]) -> List[Powder]:
        powders.reverse()
        plist = []
        for powderNum in powders:
            while powderNum > 0:
                plist.append(Powder(powderNum % 6 - 1))
                powderNum = math.floor(powderNum / 6)
        return plist

    def _decode_string(self, text: str) -> str:
        if not text:
            return ""
        decoded: str = ""
        for i in text:
            value = ord(i) - ord(_OFFSET) + 32
            decoded += chr(value)
        return decoded

    def _decode_numbers(self, text: str) -> List[int]:
        if not text:
            return []
        decoded: list[int] = []
        for i in text:
            decoded.append(ord(i) - ord(_OFFSET))
        return decoded


__all__ = ["Resolver"]
