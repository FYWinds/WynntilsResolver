"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-28 21:53:42
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-08 15:29:44
FilePath     : /wynntilsresolver/resolver.py
"""

import inspect
from collections import OrderedDict
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union, get_args, get_origin

from .blocks import Block, End, ItemType, Version
from .exception import InvalidStartByte, ParseFailed, ResolverDefinitionError
from .utils import decode_utf16, encode_utf16, get_annotations_meta


class ResolverMeta(type):
    def __prepare__(cls, name: str, **kwargs):
        return OrderedDict()

    def __new__(cls, name: str, bases: Tuple[type], attrs: Dict[str, Any]):
        annotations: dict[str, type] = get_annotations_meta(attrs.get("__annotations__", {}), eval_str=True)

        # Add _attrs to track all blocks
        if "_attrs" not in attrs:
            attrs["_attrs"] = {}

        if "start" in annotations:
            raise ResolverDefinitionError("start attribute is reserved for Version block")

        # Add start block
        attrs["_attrs"]["start"] = Version
        annotations = {**{"start": Version}, **annotations}

        # type must be provided
        if "item_type" not in annotations or not issubclass(annotations["item_type"], ItemType):
            raise ResolverDefinitionError("Resolver must have a ItemType attribute")

        # Set item_type
        item_type = annotations["item_type"]
        attrs["item_type"] = item_type

        # Add required and optional blocks
        for k, v in annotations.items():
            # If the block is Optional[Block]
            if get_origin(v) == Union and type(None) in (vtype := get_args(v)):
                v = next((x for x in vtype if issubclass(x, Block)), None)
                if v:
                    if v in item_type._required_blocks:
                        raise ResolverDefinitionError(
                            f"Block {k} is in ItemType's required blocks, cannot be optional."
                        )
                    else:
                        if v not in item_type._optional_blocks:
                            item_type._optional_blocks.append(v)
                        attrs["_attrs"][k] = v

            # If the block is Block
            if inspect.isclass(v) and issubclass(v, Block):
                attrs["_attrs"][k] = v

        # Add end block
        if "end" in annotations:
            raise ResolverDefinitionError("end attribute is reserved for end of the resolver")

        attrs["_attrs"]["end"] = End
        annotations = {**annotations, **{"end": End}}

        attrs["__annotations__"] = annotations

        return super().__new__(cls, name, bases, attrs)


T = TypeVar("T", bound="Resolver")


class Resolver(metaclass=ResolverMeta):
    """A wrapper for ResolverMeta."""

    _attrs: Dict[str, Type[Block]]
    item_type: ItemType

    @classmethod
    def from_bytes(cls: Type[T], data: List[int], drop_unknown: bool = False) -> T:
        self = cls()
        data = data.copy()
        attrs = self._attrs.copy()
        required_blocks = {k: v for k, v in attrs.items() if v in self.item_type._required_blocks}
        optional_blocks = {k: v for k, v in attrs.items() if v in self.item_type._optional_blocks}
        parsed_blocks = []

        while data:
            try:
                for k, v in attrs.items():
                    if data[0] == v._start_byte:
                        required_blocks.pop(k, None)
                        optional_blocks.pop(k, None)
                        setattr(self, k, attrs.pop(k).from_bytes(data=data, parsed_blocks=parsed_blocks))

                        parsed_blocks.append(getattr(self, k))

                        # ignore the padding 0xEE or other unknown bytes
                        if v == End:
                            data = []
                        break
                else:
                    if drop_unknown:
                        del data[0]
                    else:
                        raise InvalidStartByte(f"Unknown registered start byte {data[0]}")
            except Exception as e:
                raise ParseFailed(f"Failed to parse. Error during parsing block: {k}") from e

        # Ended with unparsed required blocks
        if required_blocks:
            raise ParseFailed(f"Failed to parse. Missing blocks: {required_blocks}")

        # Set all unparsed optional block to None
        for k, v in optional_blocks.items():
            setattr(self, k, None)

        return self

    def to_bytes(self) -> List[int]:
        data = []
        for k, v in self._attrs.items():
            if (block := getattr(self, k)) is not None:
                data.extend(block.to_bytes())
        return data

    @classmethod
    def from_utf16(cls: Type[T], data: str, drop_unknown: bool = False) -> T:
        return cls.from_bytes(decode_utf16(data), drop_unknown)

    def to_utf16(self):
        return encode_utf16(self.to_bytes())

    def __repr__(self) -> str:
        repr = f"<class '{self.__class__.__name__}' {{"
        for k, v in self._attrs.items():
            repr += f"{k}={getattr(self, k).__repr__()}, "

        repr = repr[:-2] + "} >"
        return repr

    def __str__(self) -> str:
        repr = f"<class '{self.__class__.__name__}' {{"
        for k, v in self._attrs.items():
            repr += f"{k}={getattr(self, k)}, "

        repr = repr[:-2] + "} >"
        return repr
