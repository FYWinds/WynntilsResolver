"""
Author       : FYWinds i@windis.cn
Date         : 2024-03-02 12:39:02
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-06 22:41:07
FilePath     : /tests/test_utils.py
"""

from __future__ import annotations

from typing import List, Optional

from wynntilsresolver.utils import decode_utf16, encode_utf16, get_annotations_meta


def test_utf16():
    bonder = "󰀀󰄀󰉂󶽮󶑥󷈀󰌇󰀘󲜢󷴑󵅇󸀙󶹈󵠡󶰄󰐂󶌀󰔂􏿮"
    b_data = decode_utf16(bonder)
    data = [
        0,
        0,
        1,
        0,
        2,
        66,
        111,
        110,
        100,
        101,
        114,
        0,
        3,
        7,
        0,
        24,
        39,
        34,
        125,
        17,
        81,
        71,
        128,
        25,
        110,
        72,
        88,
        33,
        108,
        4,
        4,
        2,
        99,
        0,
        5,
        2,
        255,
    ]
    data_b = encode_utf16(data)
    assert b_data == [
        0,
        0,
        1,
        0,
        2,
        66,
        111,
        110,
        100,
        101,
        114,
        0,
        3,
        7,
        0,
        24,
        39,
        34,
        125,
        17,
        81,
        71,
        128,
        25,
        110,
        72,
        88,
        33,
        108,
        4,
        4,
        2,
        99,
        0,
        5,
        2,
        255,
        238,
    ]
    assert data_b == bonder


def test_get_annotations_meta():
    class MetaClass(type):
        def __new__(cls, name, bases, attrs):
            annotations: dict[str, type] = get_annotations_meta(attrs.get("__annotations__", {}), eval_str=True)
            assert annotations == {
                "test_int": int,
                "test_str": str,
                "test_list": List[int],
                "test_optional": Optional[str],
            }
            return super().__new__(cls, name, bases, attrs)

    class TestClass(metaclass=MetaClass):
        test_int: int
        test_str: str
        test_list: List[int]
        test_optional: Optional[str]
