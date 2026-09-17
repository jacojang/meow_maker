from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from pathlib import Path

from .content import load_effects_table
from .stats import STAT_NAMES, CatStats

DATA_DIR = Path(__file__).resolve().parent / "data"


class Diet(str, Enum):
    NORMAL = "normal"
    LIGHT = "light"
    HEARTY = "hearty"


DIET_EFFECTS: Mapping[Diet, Mapping[str, int]] = load_effects_table(
    DATA_DIR / "diets.json", Diet, STAT_NAMES
)


def apply_diet(stats: CatStats, diet: Diet) -> CatStats:
    return stats.apply(dict(DIET_EFFECTS[diet]))
