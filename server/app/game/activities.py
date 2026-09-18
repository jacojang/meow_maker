from __future__ import annotations

import math
from collections.abc import Mapping
from enum import Enum
from pathlib import Path

from .content import load_effects_table
from .stats import STAT_NAMES, CatStats

DATA_DIR = Path(__file__).resolve().parent / "data"


class Activity(str, Enum):
    PLAY = "play"
    TRAIN = "train"
    GROOM = "groom"
    REST = "rest"
    EDUCATE = "educate"
    OUTING = "outing"


ACTIVITY_EFFECTS: Mapping[Activity, Mapping[str, int]] = load_effects_table(
    DATA_DIR / "activities.json", Activity, STAT_NAMES
)


def _halve_toward_zero(value: int) -> int:
    return math.trunc(value / 2)


def effects_for(activity: Activity, *, sick: bool) -> dict[str, int]:
    effects = ACTIVITY_EFFECTS[activity]
    if not sick:
        return dict(effects)
    return {
        name: value if name == "stress" else _halve_toward_zero(value)
        for name, value in effects.items()
    }


def apply_activity(stats: CatStats, activity: Activity) -> CatStats:
    return stats.apply(effects_for(activity, sick=stats.is_sick))
