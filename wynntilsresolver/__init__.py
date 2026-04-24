"""
Author       : FYWinds i@windis.cn
Date         : 2023-12-14 10:47:00
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-21 13:01:18
FilePath     : /wynntilsresolver/__init__.py
"""

from .datastore import data_store

data_store.bootstrap()

from .item import GearItemResolver as GearItemResolver
from .resolver import Resolver as Resolver

__all__ = ["Resolver", "GearItemResolver"]
