from __future__ import annotations

import random
from collections.abc import Mapping
from types import MappingProxyType

from .stats import CatStats

OUTING_SUCCESS_CHANCE = 0.7
OUTING_SUCCESS_BONUS: Mapping[str, int] = MappingProxyType({"curiosity": 5, "discipline": 5})
OUTING_FAILURE_PENALTY: Mapping[str, int] = MappingProxyType({"stress": 5})


def resolve_outing(rng: random.Random) -> bool:
    return rng.random() < OUTING_SUCCESS_CHANCE


def apply_outing_result(stats: CatStats, succeeded: bool) -> CatStats:
    effects = OUTING_SUCCESS_BONUS if succeeded else OUTING_FAILURE_PENALTY
    return stats.apply(dict(effects))
