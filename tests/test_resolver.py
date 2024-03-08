"""
Author       : FYWinds i@windis.cn
Date         : 2024-03-01 22:17:20
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-07 18:59:57
FilePath     : /tests/test_resolver.py
"""

from typing import Optional

import pytest
from wynntilsresolver import Resolver
from wynntilsresolver.blocks import End, GearItem, ItemType, Name, Reroll, Version
from wynntilsresolver.exception import ParseFailed, ResolverDefinitionError
from wynntilsresolver.utils import encode_utf16


def test_resolver_creation():
    with pytest.raises(ResolverDefinitionError):
        # using start attribute
        class TestResolver1(Resolver):
            start: int

    with pytest.raises(ResolverDefinitionError):
        # using end attribute
        class TestResolver2(Resolver):
            item_type: ItemType
            end: int

    with pytest.raises(ResolverDefinitionError):
        # wrong type item_type
        class TestResolver3(Resolver):
            item_type: int

    class ResolverTest(Resolver):
        item_type: ItemType

    assert ResolverTest.item_type == ItemType
    assert ResolverTest._attrs == {"start": Version, "item_type": ItemType, "end": End}
    assert ResolverTest.__annotations__ == {"item_type": ItemType, "start": Version, "end": End}


def test_resolver_optional_block():
    class TestItemType(ItemType):
        _required_blocks = [Name]
        _optional_blocks = []

    with pytest.raises(ResolverDefinitionError):
        # optional attribute is in required blocks
        class TestResolver1(Resolver):
            item_type: TestItemType
            name: Optional[Name]

    class TestResolver2(Resolver):
        item_type: TestItemType
        name: Name
        reroll: Optional[Reroll]

    assert TestResolver2._attrs == {
        "start": Version,
        "item_type": TestItemType,
        "name": Name,
        "reroll": Reroll,
        "end": End,
    }
    assert TestResolver2.__annotations__ == {
        "item_type": TestItemType,
        "start": Version,
        "name": Name,
        "reroll": Optional[Reroll],
        "end": End,
    }


def test_resolver_decode(capsys):
    class TestResolver(Resolver):
        item_type: GearItem
        name: Name

    test_item = encode_utf16([0, 0, 1, 0, 2, 66, 111, 110, 100, 101, 114, 0, 255])
    item = TestResolver.from_utf16(test_item)
    print(item)  # noqa
    captured = capsys.readouterr()
    assert captured.out == "<class 'TestResolver' {start=Version(0), item_type=GearItem, name=Bonder, end=End(255)} >\n"
    print(item.__repr__())  # noqa
    captured = capsys.readouterr()
    assert (
        captured.out
        == "<class 'TestResolver' {start=Version(0), item_type=GearItem, name=Name(Bonder), end=End(255)} >\n"
    )

    # Test drop unkonwn bytes
    test_item = [0, 0, 1, 0, 2, 66, 111, 110, 100, 101, 114, 0, 3, 2, 1, 255]
    item = TestResolver(test_item, drop_unknown=True)
    assert item.name.name == "Bonder"
    with pytest.raises(ParseFailed):
        TestResolver(test_item, drop_unknown=False)

    # Missing bytes for required blocks
    test_item = [0, 0, 1, 0, 255]
    with pytest.raises(ParseFailed):
        TestResolver(test_item)

    # Missing bytes for optional blocks, setting to None
    class TestResolver2(Resolver):
        item_type: ItemType
        name: Optional[Name]

    test_item = [0, 0, 1, 255]
    item = TestResolver2(test_item)
    assert item.name is None


def test_resolver_encode(capsys):
    class TestResolver(Resolver):
        item_type: GearItem
        name: Name

    test_item = [0, 0, 1, 0, 2, 66, 111, 110, 100, 101, 114, 0, 255]
    item = TestResolver.from_utf16(encode_utf16(test_item))
    assert item.to_bytes() == test_item

    item_utf16 = encode_utf16(test_item)
    assert item.to_utf16() == item_utf16
