from __future__ import annotations

import random
from collections.abc import Mapping
from enum import Enum
from pathlib import Path

from .content import load_effects_table
from .stats import STAT_NAMES, CatStats

DATA_DIR = Path(__file__).resolve().parent / "data"

EVENT_CHANCE = 0.4


class Event(str, Enum):
    VISITOR = "visitor"
    GOOD_MOOD = "good_mood"
    BAD_MOOD = "bad_mood"
    MISHAP = "mishap"
    GIFT = "gift"


EVENT_EFFECTS: Mapping[Event, Mapping[str, int]] = load_effects_table(
    DATA_DIR / "events.json", Event, STAT_NAMES
)


def roll_event(rng: random.Random) -> Event | None:
    if rng.random() >= EVENT_CHANCE:
        return None
    return rng.choice(list(Event))


def apply_event(stats: CatStats, event: Event | None) -> CatStats:
    if event is None:
        return stats
    return stats.apply(dict(EVENT_EFFECTS[event]))
