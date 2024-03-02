"""
Author       : FYWinds i@windis.cn
Date         : 2024-03-01 16:01:35
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-01 20:08:24
FilePath     : /src/wynntilsresolver/blocks/shiny.py
"""

import json
from typing import Dict, List

from wynntilsresolver.startup import SHINY_TABLE_PATH

from .block import Block

with open(SHINY_TABLE_PATH, encoding="utf-8") as f:
    shiny_table: List[Dict] = json.load(f)


class Shiny(Block):
    _start_byte: int = 6

    name: str
    """Key of the shiny. From Artemis Data."""
    internal_id: int
    """Internal ID of the shiny. From Artemis Data."""
    display_name: str
    """Display name of the shiny. From Artemis Data."""
    value: int

    def __init__(self, name: str, internal_id: int, display_name: str, value: int) -> None:
        self.name = name
        self.internal_id = internal_id
        self.display_name = display_name
        self.value = value

    @classmethod
    def from_bytes(cls, data, **kwargs) -> "Shiny":
        super().from_bytes(data)
        internal_id = data[0]
        del data[0]
        value = cls.decode_variable_sized_int(data)
        for shiny in shiny_table:
            if shiny["id"] == internal_id:
                return cls(shiny["key"], internal_id, shiny["displayName"], value)

        raise ValueError(f"Shiny with internal ID {internal_id} not found in shiny table.")

    def to_bytes(self, **kwargs) -> List[int]:
        return self.encode_with_start([self.internal_id] + self.encode_variable_sized_int(self.value))

    def __str__(self) -> str:
        return f"{self.display_name}: {self.value}"

    def __repr__(self) -> str:
        return f"Shiny({self.display_name}, {self.value})"
