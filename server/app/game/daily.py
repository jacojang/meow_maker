from __future__ import annotations

import json
import math
import random
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path

from .activities import Activity

DATA_DIR = Path(__file__).resolve().parent / "data"

# Fixed 2026 month lengths; web/src/utils/gameCalendar.js uses the same year.
MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

VARIANCE_ACTIVITIES = frozenset(
    {Activity.PLAY, Activity.TRAIN, Activity.GROOM, Activity.EDUCATE}
)


class DayOutcome(str, Enum):
    FAIL = "fail"
    NORMAL = "normal"
    GREAT = "great"


OUTCOME_MULTIPLIER: Mapping[DayOutcome, int] = {
    DayOutcome.FAIL: 0,
    DayOutcome.NORMAL: 1,
    DayOutcome.GREAT: 2,
}


@dataclass(frozen=True)
class DailyRules:
    fail_weight: float = 0.25
    great_weight: float = 0.25
    stress_threshold: int = 60
    stress_fail_shift_per_point: float = 0.005
    max_fail_shift: float = 0.2

    @classmethod
    def load(cls, path: Path = DATA_DIR / "daily.json") -> DailyRules:
        with open(path, encoding="utf-8") as handle:
            raw = json.load(handle)
        unknown = sorted(set(raw) - set(cls.__dataclass_fields__))
        if unknown:
            raise ValueError(f"{path}: unknown keys: {unknown}")
        return cls(**raw)


RULES = DailyRules.load()


def days_in_month(month: int) -> int:
    return MONTH_DAYS[month - 1]


def slot_day_counts(days: int, slot_count: int) -> list[int]:
    """Same split as `daySlots` in web/src/utils/calendar.js."""
    if slot_count <= 0:
        return []
    base = days // slot_count
    return [base] * (slot_count - 1) + [days - base * (slot_count - 1)]


def outcome_weights(stress: int, rules: DailyRules = RULES) -> tuple[float, float]:
    """Returns (p_fail, p_great); the rest is normal."""
    over = max(0, stress - rules.stress_threshold)
    shift = min(rules.max_fail_shift, over * rules.stress_fail_shift_per_point)
    p_fail = min(rules.fail_weight + shift, 1.0 - rules.great_weight)
    return p_fail, rules.great_weight


def pick_outcome(u: float, p_fail: float, p_great: float) -> DayOutcome:
    if u < p_fail:
        return DayOutcome.FAIL
    if u < p_fail + p_great:
        return DayOutcome.GREAT
    return DayOutcome.NORMAL


def roll_outcome(rng: random.Random, stress: int, rules: DailyRules = RULES) -> DayOutcome:
    p_fail, p_great = outcome_weights(stress, rules)
    return pick_outcome(rng.random(), p_fail, p_great)


def _round_half_up(value: Fraction) -> int:
    return math.floor(value + Fraction(1, 2))


class DayYield:
    """Spreads a slot's base effects over its days, rounding cumulatively so
    the integer deltas always sum to the rounded running total."""

    def __init__(self, base: Mapping[str, int], days: int) -> None:
        self._base = dict(base)
        self._days = days
        self._raw = {name: Fraction(0) for name in base}
        self._given = {name: 0 for name in base}

    def next_day(self, outcome: DayOutcome, *, rolled: bool) -> dict[str, int]:
        deltas: dict[str, int] = {}
        for name, value in self._base.items():
            share = Fraction(value, self._days)
            if rolled and name != "stress" and value > 0:
                share *= OUTCOME_MULTIPLIER[outcome]
            self._raw[name] += share
            total = _round_half_up(self._raw[name])
            delta = total - self._given[name]
            self._given[name] = total
            if delta:
                deltas[name] = delta
        return deltas

