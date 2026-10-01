from __future__ import annotations

import json
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

DATA_DIR = Path(__file__).resolve().parent / "data"

FESTIVAL_MONTH = 10
CONTEST_STATS = ("affection", "discipline", "curiosity", "refinement")

_TOP_KEYS = {"variance", "entry_stress", "prizes", "ribbon_scores", "contests"}
_CONTEST_KEYS = {"stat", "rivals"}
_RIVAL_KEYS = {"id", "base"}


@dataclass(frozen=True)
class Rival:
    id: str
    base: int


@dataclass(frozen=True)
class Contest:
    id: str
    stat: str
    rivals: tuple[Rival, ...]


@dataclass(frozen=True)
class FestivalRules:
    variance_low: float
    variance_high: float
    entry_stress: int
    prizes: Mapping[int, int]
    ribbon_scores: Mapping[int, int]
    contests: Mapping[str, Contest]

    @classmethod
    def load(cls, path: Path = DATA_DIR / "festival.json") -> FestivalRules:
        with open(path, encoding="utf-8") as handle:
            raw = json.load(handle)
        return cls.from_raw(raw, str(path))

    @classmethod
    def from_raw(cls, raw: Mapping[str, object], source: str = "festival") -> FestivalRules:
        _require_keys(source, "top level", raw, _TOP_KEYS)
        variance = raw["variance"]
        _require_keys(source, "variance", variance, {"low", "high"})
        low, high = variance["low"], variance["high"]
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (low, high)):
            raise ValueError(f"{source}: variance values must be numbers")
        if not 0 < low <= high:
            raise ValueError(f"{source}: variance must satisfy 0 < low <= high")
        _require_int(source, "entry_stress", raw["entry_stress"])

        contests = _parse_contests(source, raw["contests"])
        places = {len(contest.rivals) + 1 for contest in contests.values()}
        if len(places) != 1:
            raise ValueError(f"{source}: every contest needs the same number of rivals")
        expected = {str(rank) for rank in range(1, places.pop() + 1)}
        prizes = _parse_by_rank(source, "prizes", raw["prizes"], expected)
        ribbons = _parse_by_rank(source, "ribbon_scores", raw["ribbon_scores"], expected)
        return cls(
            variance_low=float(low),
            variance_high=float(high),
            entry_stress=raw["entry_stress"],
            prizes=prizes,
            ribbon_scores=ribbons,
            contests=contests,
        )


def _require_keys(source: str, where: str, value: object, expected: set[str]) -> None:
    if not isinstance(value, Mapping) or set(value) != expected:
        actual = set(value) if isinstance(value, Mapping) else set()
        raise ValueError(
            f"{source}: {where} keys must be {sorted(expected)} "
            f"(missing={sorted(expected - actual)}, unknown={sorted(actual - expected)})"
        )


def _require_int(source: str, where: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{source}: {where} must be a non-negative integer")


def _parse_by_rank(
    source: str, where: str, raw: object, expected: set[str]
) -> Mapping[int, int]:
    _require_keys(source, where, raw, expected)
    for value in raw.values():
        _require_int(source, where, value)
    return MappingProxyType({int(rank): value for rank, value in raw.items()})


def _parse_contests(source: str, raw: object) -> Mapping[str, Contest]:
    if not isinstance(raw, Mapping) or not raw:
        raise ValueError(f"{source}: contests must be a non-empty object")
    contests = {}
    seen_rivals: set[str] = set()
    for contest_id, entry in raw.items():
        _require_keys(source, f"contest {contest_id!r}", entry, _CONTEST_KEYS)
        if entry["stat"] not in CONTEST_STATS:
            raise ValueError(f"{source}: contest {contest_id!r} stat must be one of {CONTEST_STATS}")
        if not entry["rivals"]:
            raise ValueError(f"{source}: contest {contest_id!r} needs at least one rival")
        rivals = []
        for rival in entry["rivals"]:
            _require_keys(source, f"rival in {contest_id!r}", rival, _RIVAL_KEYS)
            _require_int(source, f"rival {rival['id']!r} base", rival["base"])
            if rival["id"] in seen_rivals:
                raise ValueError(f"{source}: duplicate rival id {rival['id']!r}")
            seen_rivals.add(rival["id"])
            rivals.append(Rival(**rival))
        contests[contest_id] = Contest(contest_id, entry["stat"], tuple(rivals))
    return MappingProxyType(contests)


RULES = FestivalRules.load()
FESTIVAL_STATS = tuple(contest.stat for contest in RULES.contests.values())


@dataclass(frozen=True)
class ContestResult:
    contest: str
    stat: str
    score: int
    rank: int
    prize: int
    rivals: tuple[tuple[str, int], ...]

    @property
    def ribbon(self) -> bool:
        return ribbon_score(self.rank) > 0

    def to_dict(self) -> dict[str, object]:
        return {
            "contest": self.contest,
            "stat": self.stat,
            "score": self.score,
            "rank": self.rank,
            "prize": self.prize,
            "rivals": [{"id": rival, "score": score} for rival, score in self.rivals],
        }


def contest_score(base: int, roll: float, rules: FestivalRules = RULES) -> int:
    factor = rules.variance_low + (rules.variance_high - rules.variance_low) * roll
    return round(base * factor)


def rank_among(own: int, rival_scores: Sequence[int]) -> int:
    """A tie is shared, and the player takes the better place."""
    return 1 + sum(score > own for score in rival_scores)


def prize_for(rank: int, rules: FestivalRules = RULES) -> int:
    return rules.prizes[rank]


def ribbon_score(rank: int, rules: FestivalRules = RULES) -> int:
    return rules.ribbon_scores[rank]


def resolve_contest(
    contest_id: str,
    stat_value: int,
    rng: random.Random,
    rules: FestivalRules = RULES,
) -> ContestResult:
    """Rolls the player first, then the rivals in data order, one rng.random() each."""
    contest = rules.contests[contest_id]
    own = contest_score(stat_value, rng.random(), rules)
    rivals = tuple(
        (rival.id, contest_score(rival.base, rng.random(), rules)) for rival in contest.rivals
    )
    rank = rank_among(own, [score for _, score in rivals])
    return ContestResult(
        contest=contest_id,
        stat=contest.stat,
        score=own,
        rank=rank,
        prize=prize_for(rank, rules),
        rivals=rivals,
    )
