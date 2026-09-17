from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace

STAT_NAMES = (
    "health",
    "affection",
    "discipline",
    "curiosity",
    "refinement",
    "age",
    "weight",
    "stress",
)
STAT_MIN = 0
STAT_MAX = 100
OVERWEIGHT_THRESHOLD = 80


def clamp(value: int) -> int:
    return max(STAT_MIN, min(STAT_MAX, value))


@dataclass(frozen=True)
class CatStats:
    health: int = 50
    affection: int = 20
    discipline: int = 10
    curiosity: int = 30
    refinement: int = 10
    age: int = 1
    weight: int = 50
    stress: int = 0

    def __post_init__(self) -> None:
        for name in STAT_NAMES:
            object.__setattr__(self, name, clamp(getattr(self, name)))

    @property
    def is_sick(self) -> bool:
        return self.stress > self.health

    @property
    def is_overweight(self) -> bool:
        return self.weight > OVERWEIGHT_THRESHOLD

    def apply(self, deltas: Mapping[str, int]) -> CatStats:
        unknown = sorted(set(deltas) - set(STAT_NAMES))
        if unknown:
            raise ValueError(f"unknown stats: {unknown}")
        changed = {name: getattr(self, name) + delta for name, delta in deltas.items()}
        return replace(self, **changed)

    def to_dict(self) -> dict[str, int]:
        return {name: getattr(self, name) for name in STAT_NAMES}

    @classmethod
    def from_dict(cls, data: Mapping[str, int]) -> CatStats:
        missing = sorted(set(STAT_NAMES) - set(data))
        if missing:
            raise ValueError(f"missing stats: {missing}")
        unknown = sorted(set(data) - set(STAT_NAMES))
        if unknown:
            raise ValueError(f"unknown stats: {unknown}")
        return cls(**{name: int(data[name]) for name in STAT_NAMES})
