"""
Author       : FYWinds i@windis.cn
Date         : 2024-03-01 16:01:35
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-01 20:08:24
FilePath     : /src/wynntilsresolver/blocks/shiny.py
"""

from typing import List

from wynntilsresolver.blocks.version import Version
from wynntilsresolver.datastore import data_store

from .block import Block


def extract_version(parsed_blocks: List["Block"]) -> int:
    for block in parsed_blocks:
        if isinstance(block, Version):
            return block.version
    return 0


class Shiny(Block):
    _start_byte: int = 6

    name: str
    """Key of the shiny. From Artemis Data."""
    internal_id: int
    """Internal ID of the shiny. From Artemis Data."""
    display_name: str
    """Display name of the shiny. From Artemis Data."""
    value: int
    """Value of the shiny."""
    reroll: int = 0
    """Reroll count of the shiny."""

    def __init__(self, name: str, internal_id: int, display_name: str, value: int, reroll: int) -> None:
        self.name = name
        self.internal_id = internal_id
        self.display_name = display_name
        self.value = value
        self.reroll = reroll

    @classmethod
    def from_bytes(cls, data, parsed_blocks: List["Block"], **kwargs) -> "Shiny":
        super().from_bytes(data)
        internal_id = data[0]
        del data[0]

        reroll = 0
        if extract_version(parsed_blocks) >= 1:
            reroll = data[0]
            del data[0]
        value = cls.decode_variable_sized_int(data)
        for shiny in data_store.shiny_table:
            if shiny["id"] == internal_id:
                return cls(shiny["key"], internal_id, shiny["displayName"], value, reroll)

        raise ValueError(f"Shiny with internal ID {internal_id} not found in shiny table.")

    def to_bytes(self, **kwargs) -> List[int]:
        return self.encode_with_start([self.internal_id] + self.encode_variable_sized_int(self.value))

    def __str__(self) -> str:
        return (
            f"Shiny("
            f"name={self.name}, "
            f"internal_id={self.internal_id}, "
            f"display_name={self.display_name}, "
            f"value={self.value}, "
            f"reroll={self.reroll}"
            f")"
        )

    def __repr__(self) -> str:
        return (
            f"Shiny("
            f"name={self.name}, "
            f"internal_id={self.internal_id}, "
            f"display_name={self.display_name}, "
            f"value={self.value}, "
            f"reroll={self.reroll}"
            f")"
        )
