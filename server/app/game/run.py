from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .activities import Activity, apply_activity
from .diet import Diet, apply_diet
from .stats import CatStats

MONTHS_PER_RUN = 12
SLOTS_PER_MONTH = 3

FIRST_MONTH = 1


class GameRuleError(Exception):
    pass


class RunFinishedError(GameRuleError):
    pass


class IncompleteMonthError(GameRuleError):
    pass


def _empty_slots() -> list[Activity | None]:
    return [None] * SLOTS_PER_MONTH


@dataclass
class GameRun:
    stats: CatStats = field(default_factory=CatStats)
    month: int = FIRST_MONTH
    finished: bool = False
    slots: list[Activity | None] = field(default_factory=_empty_slots)
    diet: Diet = Diet.NORMAL

    def __post_init__(self) -> None:
        if not FIRST_MONTH <= self.month <= MONTHS_PER_RUN:
            raise ValueError(f"month out of range: {self.month}")
        if len(self.slots) != SLOTS_PER_MONTH:
            raise ValueError(f"expected {SLOTS_PER_MONTH} slots, got {len(self.slots)}")

    @property
    def is_sick(self) -> bool:
        return self.stats.is_sick

    def assign_slot(self, index: int, activity: Activity) -> None:
        self._require_active()
        if not 0 <= index < SLOTS_PER_MONTH:
            raise IndexError(f"slot index out of range: {index}")
        self.slots[index] = Activity(activity)

    def assign_month(self, activities: Sequence[Activity]) -> None:
        self._require_active()
        if len(activities) != SLOTS_PER_MONTH:
            raise IncompleteMonthError(
                f"expected {SLOTS_PER_MONTH} activities, got {len(activities)}"
            )
        self.slots = [Activity(activity) for activity in activities]

    def assign_diet(self, diet: Diet) -> None:
        self._require_active()
        self.diet = Diet(diet)

    def advance_month(self) -> None:
        self._require_active()
        if any(slot is None for slot in self.slots):
            raise IncompleteMonthError("every slot must be assigned before advancing")

        for activity in self.slots:
            self.stats = apply_activity(self.stats, activity)

        self.stats = apply_diet(self.stats, self.diet)
        self.stats = self.stats.apply({"age": 1})

        self.slots = _empty_slots()
        if self.month == MONTHS_PER_RUN:
            self.finished = True
        else:
            self.month += 1

    def _require_active(self) -> None:
        if self.finished:
            raise RunFinishedError("the run is over")

    def to_dict(self) -> dict[str, Any]:
        return {
            "stats": self.stats.to_dict(),
            "month": self.month,
            "finished": self.finished,
            "slots": [None if slot is None else slot.value for slot in self.slots],
            "diet": self.diet.value,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> GameRun:
        missing = sorted({"stats", "month", "finished", "slots", "diet"} - set(data))
        if missing:
            raise ValueError(f"missing keys: {missing}")
        slots = data["slots"]
        return cls(
            stats=CatStats.from_dict(data["stats"]),
            month=int(data["month"]),
            finished=bool(data["finished"]),
            slots=[None if slot is None else Activity(slot) for slot in slots],
            diet=Diet(data["diet"]),
        )
