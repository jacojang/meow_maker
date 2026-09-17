from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from .stats import CatStats

DELINQUENT_PENALTY: Mapping[str, int] = MappingProxyType({"discipline": -1})


def apply_delinquent_penalty(stats: CatStats) -> CatStats:
    if not stats.is_delinquent:
        return stats
    return stats.apply(dict(DELINQUENT_PENALTY))
