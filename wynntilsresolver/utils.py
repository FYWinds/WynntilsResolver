import asyncio
import functools
import inspect
import sys
import types
from typing import Any, Callable, Coroutine, Dict, List, TypeVar


def get_annotations_meta(annotation: Dict[str, Any], *, globals=None, locals=None, eval_str=False) -> Dict[str, Any]:
    """Compute the annotations dict for an __annotations__ dict.

    Args:
        annotation (Dict[str, Any]): The __annotations__ dict.
        globals (_type_, optional): globals for eval. Defaults to None.
        locals (_type_, optional): locals for eval. Defaults to None.
        eval_str (bool, optional): Eval the stringlized type. Defaults to False.

    Returns:
        _type_: The computed annotations dict.
    """
    # get the trigger class of the caller
    frame = inspect.currentframe()
    if frame is None:
        return annotation
    for _ in range(2):
        frame = frame.f_back
        if frame is None:
            return annotation

    module = inspect.getmodule(frame)
    if module is None:
        return annotation
    else:
        obj_globals = globals or getattr(module, "__dict__", None)
        obj_locals = locals or frame.f_locals
        return_value = {
            key: value if not isinstance(value, str) else eval(value, obj_globals, obj_locals)
            for key, value in annotation.items()
        }
        return return_value


def get_annotations(obj, *, globals=None, locals=None, eval_str=False):
    """Compute the annotations dict for an object.
    Copied directly from cpython/Lib/inspect.py#L175

    obj may be a callable, class, or module.
    Passing in an object of any other type raises TypeError.

    Returns a dict.  get_annotations() returns a new dict every time
    it's called; calling it twice on the same object will return two
    different but equivalent dicts.

    This function handles several details for you:

      * If eval_str is true, values of type str will
        be un-stringized using eval().  This is intended
        for use with stringized annotations
        ("from __future__ import annotations").
      * If obj doesn't have an annotations dict, returns an
        empty dict.  (Functions and methods always have anw
        annotations dict; classes, modules, and other types of
        callables may not.)
      * Ignores inherited annotations on classes.  If a class
        doesn't have its own annotations dict, returns an empty dict.
      * All accesses to object members and dict values are done
        using getattr() and dict.get() for safety.
      * Always, always, always returns a freshly-created dict.

    eval_str controls whether or not values of type str are replaced
    with the result of calling eval() on those values:

      * If eval_str is true, eval() is called on values of type str.
      * If eval_str is false (the default), values of type str are unchanged.

    globals and locals are passed in to eval(); see the documentation
    for eval() for more information.  If either globals or locals is
    None, this function may replace that value with a context-specific
    default, contingent on type(obj):

      * If obj is a module, globals defaults to obj.__dict__.
      * If obj is a class, globals defaults to
        sys.modules[obj.__module__].__dict__ and locals
        defaults to the obj class namespace.
      * If obj is a callable, globals defaults to obj.__globals__,
        although if obj is a wrapped function (using
        functools.update_wrapper()) it is first unwrapped.
    """
    if isinstance(obj, type):
        # class
        obj_dict = getattr(obj, "__dict__", None)
        if obj_dict and hasattr(obj_dict, "get"):
            ann = obj_dict.get("__annotations__", None)
            if isinstance(ann, types.GetSetDescriptorType):
                ann = None
        else:
            ann = None

        obj_globals = None
        module_name = getattr(obj, "__module__", None)
        if module_name:
            module = sys.modules.get(module_name, None)
            if module:
                obj_globals = getattr(module, "__dict__", None)
        obj_locals = dict(vars(obj))
        unwrap = obj
    elif isinstance(obj, types.ModuleType):
        # module
        ann = getattr(obj, "__annotations__", None)
        obj_globals = getattr(obj, "__dict__")
        obj_locals = None
        unwrap = None
    elif callable(obj):
        # this includes types.Function, types.BuiltinFunctionType,
        # types.BuiltinMethodType, functools.partial, functools.singledispatch,
        # "class funclike" from Lib/test/test_inspect... on and on it goes.
        ann = getattr(obj, "__annotations__", None)
        obj_globals = getattr(obj, "__globals__", None)
        obj_locals = None
        unwrap = obj
    else:
        raise TypeError(f"{obj!r} is not a module, class, or callable.")

    if ann is None:
        return {}

    if not isinstance(ann, dict):
        raise ValueError(f"{obj!r}.__annotations__ is neither a dict nor None")

    if not ann:
        return {}

    if not eval_str:
        return dict(ann)

    if unwrap is not None:
        while True:
            if hasattr(unwrap, "__wrapped__"):
                unwrap = unwrap.__wrapped__
                continue
            if isinstance(unwrap, functools.partial):
                unwrap = unwrap.func
                continue
            break
        if hasattr(unwrap, "__globals__"):
            obj_globals = unwrap.__globals__

    if globals is None:
        globals = obj_globals
    if locals is None:
        locals = obj_locals

    return_value = {
        key: value if not isinstance(value, str) else eval(value, globals, locals) for key, value in ann.items()
    }
    return return_value


R = TypeVar("R")


def run_async(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., R]:
    """A decorator to run a async function synchronously."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> R:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.run_until_complete(func(*args, **kwargs))
        else:
            return asyncio.run(func(*args, **kwargs))

    return wrapper


def decode_utf16(data: str) -> List[int]:
    """Decode the int array from utf16 string.

    Args:
        utf16 (str): The utf16 string.

    Returns:
        List[int]: The int array.
    """
    return [int(format(ord(char), "x")[-4:][i : i + 2], 16) for char in data for i in range(0, 4, 2)]
    # li: List[int] = []
    # for char in data:
    #     hex_num = format(ord(char), "04x")
    #     li.append(int(hex_num[-4:-2], 16))
    #     li.append(int(hex_num[-2:], 16))

    # return li


def encode_utf16(data: List[int]) -> str:
    """Encode the utf16 string from int array.

    Args:
        data (List[int]): The int array.

    Returns:
        str: The utf16 string.
    """
    encoded_chars = []

    # remove the possible 0xEE padding when directly converting back
    if data[-1] != 255:
        del data[-1]

    for i in range(0, len(data), 2):
        # more than two byte left
        if i + 1 < len(data):
            # use PUA-A
            char_code = 0xF0000 + (data[i] << 8) + data[i + 1]
        else:
            # use PUA-B and a padding 0xEE
            char_code = 0x100000 + (data[i] << 8) + 0xEE
        encoded_chars.append(chr(char_code))
    return "".join(encoded_chars)
