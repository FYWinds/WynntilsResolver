"""
Author       : FYWinds i@windis.cn
Date         : 2024-01-13 23:06:52
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-02-29 18:20:02
FilePath     : /src/wynntilsresolver/blocks/version.py
"""

from typing import FrozenSet, List

from wynntilsresolver.exception import UnsupportedVersion

from .block import Block

SUPPORTED_VERSIONS: FrozenSet[int] = frozenset({0, 1, 2})
"""Version bytes this resolver can decode. Mirrors Artemis' ItemTransformingVersion ids:
0 -> VERSION_1, 1 -> VERSION_2 (shiny rerolls), 2 -> VERSION_3 (identifications encode the value).
"""


class Version(Block):
    version: int

    _start_byte: int = 0

    def __init__(self, version) -> None:
        self.version = version

    @classmethod
    def from_bytes(cls, data: List[int], **kwargs) -> "Version":
        super().from_bytes(data)
        version = data[0]
        if version not in SUPPORTED_VERSIONS:
            raise UnsupportedVersion(f"Unsupported encoding version {version}, supported: {sorted(SUPPORTED_VERSIONS)}")
        del data[0]
        return cls(version)

    def to_bytes(self) -> List[int]:
        return self.encode_with_start([self.version])

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"Version({self.version})"


def extract_version(parsed_blocks: List[Block]) -> int:
    for block in parsed_blocks:
        if isinstance(block, Version):
            return block.version
    return 0
