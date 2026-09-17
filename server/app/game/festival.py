from __future__ import annotations

from .stats import CatStats

FESTIVAL_MONTH = 10
FESTIVAL_STATS = ("affection", "discipline", "curiosity", "refinement")
FESTIVAL_BONUS = 5


def resolve_festival(stats: CatStats) -> tuple[CatStats, str]:
    winner = max(FESTIVAL_STATS, key=lambda name: getattr(stats, name))
    return stats.apply({winner: FESTIVAL_BONUS}), winner
