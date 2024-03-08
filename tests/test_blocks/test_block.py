from typing import List

import pytest
from wynntilsresolver.blocks import Block
from wynntilsresolver.exception import InvalidStartByte


def test_block_decoding():
    # Decode string
    assert Block.decode_string([67, 68, 69, 70, 0]) == "CDEF"

    # Decode variable sized int
    assert Block.decode_variable_sized_int([0b11010000, 0b00001111]) == 1000

    class TestBlock(Block):
        _start_byte = 1

    # Decode block with start byte
    with pytest.raises(InvalidStartByte):
        TestBlock.from_bytes([0])
    assert TestBlock.from_bytes([1]) is None


def test_block_encoding():
    with pytest.raises(TypeError):
        b = Block()  # type: ignore # noqa

    # Encode string
    class TestBlock(Block):
        _start_byte = 1

        def to_bytes(self, **kwargs) -> List[int]:
            return self.encode_with_start([0, 2, 3])

        def __str__(self) -> str:
            return "TestBlock"

        def __repr__(self) -> str:
            return f"TestBlock({self._start_byte})"

    tb = TestBlock()
    assert tb.to_bytes() == [1, 0, 2, 3]
    assert tb.encode_string("Test") == [84, 101, 115, 116, 0]
    assert tb.encode_variable_sized_int(1000) == [0b11010000, 0b00001111]
