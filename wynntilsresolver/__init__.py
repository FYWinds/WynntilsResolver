"""
Author       : FYWinds i@windis.cn
Date         : 2023-12-14 10:47:00
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-06 20:06:06
FilePath     : /src/wynntilsresolver/__init__.py
"""

from .resolver import Resolver as Resolver
from .startup import startup

__all__ = ["Resolver"]

startup()
