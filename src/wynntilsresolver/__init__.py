"""
Author       : FYWinds i@windis.cn
Date         : 1969-12-31 19:00:00
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2023-05-07 17:42:30
FilePath     : /src/wynntilsresolver/__init__.py

Copyright (c) 2023 by FYWinds
All Rights Reserved.
Any modifications or distributions of the file
should mark the original author's name.
"""

from .resolver import Resolver as Resolver

resolver = Resolver()
__all__ = ["Resolver", "resolver"]
