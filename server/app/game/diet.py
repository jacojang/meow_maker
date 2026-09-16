from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType

from .stats import CatStats


class Diet(str, Enum):
    NORMAL = "normal"
    LIGHT = "light"
    HEARTY = "hearty"


DIET_EFFECTS: Mapping[Diet, Mapping[str, int]] = MappingProxyType(
    {
        Diet.NORMAL: MappingProxyType({"weight": 1}),
        Diet.LIGHT: MappingProxyType({"weight": -1}),
        Diet.HEARTY: MappingProxyType({"weight": 3, "health": 1}),
    }
)


def apply_diet(stats: CatStats, diet: Diet) -> CatStats:
    return stats.apply(dict(DIET_EFFECTS[diet]))
