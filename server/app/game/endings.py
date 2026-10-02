from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from pathlib import Path

from .festival import ribbon_score
from .stats import CatStats

DATA_DIR = Path(__file__).resolve().parent / "data"

SCORE_STATS = ("health", "affection", "discipline", "curiosity", "refinement")
SCORE_MAX = 1000

ENDING_STAT_PRIORITY = ("health", "affection", "discipline", "curiosity", "refinement")


class Ending(str, Enum):
    HOSPITALIZED = "hospitalized"
    RAN_AWAY = "ran_away"
    NEGLECTED = "neglected"
    DELINQUENT = "delinquent"
    BALANCED = "balanced"
    PAIR_HEALTH_AFFECTION = "pair_health_affection"
    PAIR_HEALTH_DISCIPLINE = "pair_health_discipline"
    PAIR_HEALTH_CURIOSITY = "pair_health_curiosity"
    PAIR_HEALTH_REFINEMENT = "pair_health_refinement"
    PAIR_AFFECTION_DISCIPLINE = "pair_affection_discipline"
    PAIR_AFFECTION_CURIOSITY = "pair_affection_curiosity"
    PAIR_AFFECTION_REFINEMENT = "pair_affection_refinement"
    PAIR_DISCIPLINE_CURIOSITY = "pair_discipline_curiosity"
    PAIR_DISCIPLINE_REFINEMENT = "pair_discipline_refinement"
    PAIR_CURIOSITY_REFINEMENT = "pair_curiosity_refinement"
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

_ENDING_BY_PAIR = {
    pair: Ending(f"pair_{pair[0]}_{pair[1]}")
    for pair in combinations(ENDING_STAT_PRIORITY, 2)
}


@dataclass(frozen=True)
class EndingRules:
    balance_gap: int
    pair_gap: int
    balance_bonus: int
    overweight_penalty: int
    stress_threshold: int
    high_stress_penalty: int
    bedridden_streak: int = 2
    hospital_limit: int = 3
    neglect_total: int = 6
    sick_month_penalty: int = 15
    early_end_score_cap: int = 300
    runaway_streak: int = 8


def load_ending_rules(path: Path = DATA_DIR / "endings.json") -> EndingRules:
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    score = raw["score"]
    sickness = {
        key: int(value)
        for key, value in raw.get("sickness", {}).items()
        if key in EndingRules.__dataclass_fields__
    }
    delinquency = {
        key: int(value)
        for key, value in raw.get("delinquency", {}).items()
        if key in EndingRules.__dataclass_fields__
    }
    return EndingRules(
        **sickness,
        **delinquency,
        balance_gap=int(raw["balance_gap"]),
        pair_gap=int(raw["pair_gap"]),
        balance_bonus=int(score["balance_bonus"]),
        overweight_penalty=int(score["overweight_penalty"]),
        stress_threshold=int(score["stress_threshold"]),
        high_stress_penalty=int(score["high_stress_penalty"]),
    )


RULES = load_ending_rules()


@dataclass(frozen=True)
class RunSummary:
    """What the ending and score are computed from. Later slices add
    counters here (with defaults) instead of changing the function signatures."""

    stats: CatStats
    sick_months_total: int = 0
    bedridden_months: int = 0
    delinquent_streak: int = 0
    ribbon_ranks: tuple[int, ...] = ()


def _as_summary(value: RunSummary | CatStats) -> RunSummary:
    return value if isinstance(value, RunSummary) else RunSummary(stats=value)


def _ranked_stats(stats: CatStats) -> list[str]:
    return sorted(
        ENDING_STAT_PRIORITY,
        key=lambda name: (-getattr(stats, name), ENDING_STAT_PRIORITY.index(name)),
    )


def is_balanced(stats: CatStats, rules: EndingRules = RULES) -> bool:
    values = [getattr(stats, name) for name in SCORE_STATS]
    return max(values) - min(values) <= rules.balance_gap


def is_hospitalized(summary: RunSummary | CatStats, rules: EndingRules = RULES) -> bool:
    return _as_summary(summary).bedridden_months >= rules.hospital_limit


def is_ran_away(summary: RunSummary | CatStats, rules: EndingRules = RULES) -> bool:
    return _as_summary(summary).delinquent_streak >= rules.runaway_streak


def is_early_ending(summary: RunSummary | CatStats, rules: EndingRules = RULES) -> bool:
    return is_hospitalized(summary, rules) or is_ran_away(summary, rules)


def determine_ending(summary: RunSummary | CatStats, rules: EndingRules = RULES) -> Ending:
    summary = _as_summary(summary)
    stats = summary.stats
    if is_hospitalized(summary, rules):
        return Ending.HOSPITALIZED
    if is_ran_away(summary, rules):
        return Ending.RAN_AWAY
    if stats.is_sick or summary.sick_months_total >= rules.neglect_total:
        return Ending.NEGLECTED
    if stats.is_delinquent:
        return Ending.DELINQUENT
    if is_balanced(stats, rules):
        return Ending.BALANCED
    first, second = _ranked_stats(stats)[:2]
    if getattr(stats, first) - getattr(stats, second) <= rules.pair_gap:
        pair = tuple(sorted((first, second), key=ENDING_STAT_PRIORITY.index))
        return _ENDING_BY_PAIR[pair]
    return _ENDING_BY_STAT[first]


def compute_score(summary: RunSummary | CatStats, rules: EndingRules = RULES) -> int:
    summary = _as_summary(summary)
    stats = summary.stats
    raw = sum(getattr(stats, name) for name in SCORE_STATS) * 2
    if is_balanced(stats, rules):
        raw += rules.balance_bonus
    if stats.is_overweight:
        raw -= rules.overweight_penalty
    if stats.stress > rules.stress_threshold:
        raw -= rules.high_stress_penalty
    raw -= rules.sick_month_penalty * summary.sick_months_total
    raw += sum(ribbon_score(rank) for rank in summary.ribbon_ranks)
    score = max(0, min(SCORE_MAX, raw))
    if is_early_ending(summary, rules):
        score = min(score, rules.early_end_score_cap)
    return score
