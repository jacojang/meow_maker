from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from types import MappingProxyType

from .stats import CatStats


class Activity(str, Enum):
    PLAY = "play"
    TRAIN = "train"
    GROOM = "groom"
    REST = "rest"


ACTIVITY_EFFECTS: Mapping[Activity, Mapping[str, int]] = MappingProxyType(
    {
        Activity.PLAY: MappingProxyType({"affection": 4, "curiosity": 3, "stress": 12}),
        Activity.TRAIN: MappingProxyType({"discipline": 5, "stress": 8}),
        Activity.GROOM: MappingProxyType({"affection": 3, "health": 1, "stress": 3}),
        Activity.REST: MappingProxyType({"stress": -20}),
    }
)


def effects_for(activity: Activity, *, sick: bool) -> dict[str, int]:
    effects = ACTIVITY_EFFECTS[activity]
    if not sick:
        return dict(effects)
    return {
        name: value if name == "stress" else value // 2
        for name, value in effects.items()
    }


def apply_activity(stats: CatStats, activity: Activity) -> CatStats:
    return stats.apply(effects_for(activity, sick=stats.is_sick))
