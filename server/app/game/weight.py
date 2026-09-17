from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from .stats import CatStats

OVERWEIGHT_PENALTY: Mapping[str, int] = MappingProxyType({"affection": -2})


def apply_overweight_penalty(stats: CatStats) -> CatStats:
    if not stats.is_overweight:
        return stats
    return stats.apply(dict(OVERWEIGHT_PENALTY))
