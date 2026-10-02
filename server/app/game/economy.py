from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from .activities import Activity

DATA_DIR = Path(__file__).resolve().parent / "data"

_TOP_KEYS = {"start_money", "perfect_bonus_percent", "activities"}
_ENTRY_KEYS = {"cost", "income_per_day"}


@dataclass(frozen=True)
class ActivityEconomy:
    cost: int
    income_per_day: int


@dataclass(frozen=True)
class Economy:
    start_money: int
    perfect_bonus_percent: int
    activities: Mapping[Activity, ActivityEconomy]

    @classmethod
    def load(cls, path: Path = DATA_DIR / "economy.json") -> Economy:
        with open(path, encoding="utf-8") as handle:
            raw = json.load(handle)
        return cls.from_raw(raw, str(path))

    @classmethod
    def from_raw(cls, raw: Mapping[str, object], source: str = "economy") -> Economy:
        if set(raw) != _TOP_KEYS:
            raise ValueError(
                f"{source}: keys must be {sorted(_TOP_KEYS)} "
                f"(missing={sorted(_TOP_KEYS - set(raw))}, unknown={sorted(set(raw) - _TOP_KEYS)})"
            )
        entries = raw["activities"]
        expected = {member.value for member in Activity}
        if set(entries) != expected:
            raise ValueError(
                f"{source}: activities must exactly match Activity values "
                f"(missing={sorted(expected - set(entries))}, unknown={sorted(set(entries) - expected)})"
            )
        table = {}
        for key, entry in entries.items():
            if set(entry) != _ENTRY_KEYS:
                raise ValueError(
                    f"{source}: {key!r} keys must be {sorted(_ENTRY_KEYS)}, got {sorted(entry)}"
                )
            _require_non_negative_ints(source, key, entry.values())
            table[Activity(key)] = ActivityEconomy(**entry)
        _require_non_negative_ints(
            source, "top level", [raw["start_money"], raw["perfect_bonus_percent"]]
        )
        return cls(
            start_money=raw["start_money"],
            perfect_bonus_percent=raw["perfect_bonus_percent"],
            activities=MappingProxyType(table),
        )


def _require_non_negative_ints(source: str, where: str, values: Iterable[object]) -> None:
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{source}: {where}: values must be non-negative integers")


ECONOMY = Economy.load()
START_MONEY = ECONOMY.start_money


def cost_of(activity: Activity, economy: Economy = ECONOMY) -> int:
    return economy.activities[activity].cost


def total_cost(activities: Iterable[Activity], economy: Economy = ECONOMY) -> int:
    return sum(cost_of(activity, economy) for activity in activities)


def income_per_day(activity: Activity, *, sick: bool, economy: Economy = ECONOMY) -> int:
    base = economy.activities[activity].income_per_day
    return base // 2 if sick else base


def with_perfect_bonus(total: int, economy: Economy = ECONOMY) -> int:
    return total + total * economy.perfect_bonus_percent // 100
