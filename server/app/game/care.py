from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType

from .stats import STAT_NAMES, CatStats

DATA_DIR = Path(__file__).resolve().parent / "data"

_WORKS_WHEN = {"always", "healthy", "delinquent"}
_ENTRY_KEYS = {"cost", "works_when", "works", "otherwise", "otherwise_sick"}
_REQUIRED_KEYS = {"cost", "works_when", "works"}


class Care(str, Enum):
    PET = "pet"
    TREAT = "treat"
    SCOLD = "scold"


@dataclass(frozen=True)
class CareRule:
    cost: int
    works_when: str
    works: Mapping[str, int]
    otherwise: Mapping[str, int]
    otherwise_sick: Mapping[str, int]


@dataclass(frozen=True)
class CareOutcome:
    worked: bool
    cost: int
    effects: Mapping[str, int]


def _load_effects(source: str, where: str, effects: object) -> Mapping[str, int]:
    if not isinstance(effects, Mapping):
        raise ValueError(f"{source}: {where} must be an object")
    unknown = sorted(set(effects) - set(STAT_NAMES))
    if unknown:
        raise ValueError(f"{source}: unknown stats for {where!r}: {unknown}")
    for value in effects.values():
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{source}: {where}: effects must be integers")
    return MappingProxyType(dict(effects))


def parse_care_table(raw: Mapping[str, object], source: str = "care") -> Mapping[Care, CareRule]:
    expected = {member.value for member in Care}
    if set(raw) != expected:
        raise ValueError(
            f"{source}: keys must exactly match Care values "
            f"(missing={sorted(expected - set(raw))}, unknown={sorted(set(raw) - expected)})"
        )
    table = {}
    for key, entry in raw.items():
        keys = set(entry)
        if not _REQUIRED_KEYS <= keys <= _ENTRY_KEYS:
            raise ValueError(
                f"{source}: {key!r} keys must include {sorted(_REQUIRED_KEYS)} "
                f"and only {sorted(_ENTRY_KEYS)}, got {sorted(keys)}"
            )
        cost = entry["cost"]
        if isinstance(cost, bool) or not isinstance(cost, int) or cost < 0:
            raise ValueError(f"{source}: {key!r}: cost must be a non-negative integer")
        if entry["works_when"] not in _WORKS_WHEN:
            raise ValueError(f"{source}: {key!r}: works_when must be one of {sorted(_WORKS_WHEN)}")
        otherwise = _load_effects(source, f"{key}.otherwise", entry.get("otherwise", {}))
        table[Care(key)] = CareRule(
            cost=cost,
            works_when=entry["works_when"],
            works=_load_effects(source, f"{key}.works", entry["works"]),
            otherwise=otherwise,
            otherwise_sick=_load_effects(
                source, f"{key}.otherwise_sick", entry.get("otherwise_sick", otherwise)
            ),
        )
    return MappingProxyType(table)


def load_care_table(path: Path = DATA_DIR / "care.json") -> Mapping[Care, CareRule]:
    with open(path, encoding="utf-8") as handle:
        return parse_care_table(json.load(handle), str(path))


CARE_RULES = load_care_table()


def _works(rule: CareRule, stats: CatStats) -> bool:
    if rule.works_when == "always":
        return True
    if rule.works_when == "delinquent":
        return stats.is_delinquent
    return not stats.is_sick and not stats.is_delinquent


def care_outcome(care: Care, stats: CatStats, rules: Mapping[Care, CareRule] = CARE_RULES) -> CareOutcome:
    rule = rules[care]
    if _works(rule, stats):
        return CareOutcome(worked=True, cost=rule.cost, effects=rule.works)
    effects = rule.otherwise_sick if stats.is_sick else rule.otherwise
    return CareOutcome(worked=False, cost=0, effects=effects)
