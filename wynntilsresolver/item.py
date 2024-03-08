"""
Author       : FYWinds i@windis.cn
Date         : 2024-03-08 15:24:12
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-03-08 15:53:44
FilePath     : /wynntilsresolver/item.py
"""

# This file contains several pre-built resolver for specific items.

from __future__ import annotations

from typing import List, Optional

from .blocks import GearItem, Identification, Identifications, Name, Powder, Reroll, Shiny
from .resolver import Resolver


class GearItemResolver(Resolver):
    item_type: GearItem
    _name: Name
    _identifications: Optional[Identifications]
    powder: Optional[Powder]
    shiny: Optional[Shiny]
    _reroll: Optional[Reroll]

    @classmethod
    def create(
        cls,
        name: Name,
        identifications: Optional[Identifications] = None,
        powder: Optional[Powder] = None,
        shiny: Optional[Shiny] = None,
        reroll: Optional[Reroll] = None,
    ) -> "GearItemResolver":
        c = cls()
        c._name = name
        c._identifications = identifications
        c.powder = powder
        c.shiny = shiny
        c._reroll = reroll
        return c

    @property
    def name(self) -> str:
        return self._name.name

    @property
    def identifications(self) -> Optional[List[Identification]]:
        if self._identifications:
            return self._identifications.identifications

    @property
    def reroll(self) -> int:
        # According to current Artemis Algorithm, None means 0 rerolls
        if self._reroll:
            return self._reroll.rerolls
        return 0


__all__ = ["GearItemResolver"]
