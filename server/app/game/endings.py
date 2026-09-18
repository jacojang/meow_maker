from __future__ import annotations

from enum import Enum

from .stats import CatStats

SCORE_STATS = ("health", "affection", "discipline", "curiosity", "refinement")
SCORE_MAX = 1000

ENDING_STAT_PRIORITY = ("health", "affection", "discipline", "curiosity", "refinement")


class Ending(str, Enum):
    NEGLECTED = "neglected"
    DELINQUENT = "delinquent"
    HEALTHY = "healthy"
    BELOVED = "beloved"
    DISCIPLINED = "disciplined"
    CURIOUS = "curious"
    REFINED = "refined"


_ENDING_BY_STAT = {
    "health": Ending.HEALTHY,
    "affection": Ending.BELOVED,
    "discipline": Ending.DISCIPLINED,
    "curiosity": Ending.CURIOUS,
    "refinement": Ending.REFINED,
}


def determine_ending(stats: CatStats) -> Ending:
    if stats.is_sick:
        return Ending.NEGLECTED
    if stats.is_delinquent:
        return Ending.DELINQUENT
    best = max(ENDING_STAT_PRIORITY, key=lambda name: getattr(stats, name))
    return _ENDING_BY_STAT[best]


def compute_score(stats: CatStats) -> int:
    raw = sum(getattr(stats, name) for name in SCORE_STATS) * 2
    return max(0, min(SCORE_MAX, raw))
