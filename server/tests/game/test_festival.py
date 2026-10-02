import copy
import json
import random

import pytest

from app.game.festival import (
    FESTIVAL_STATS,
    RULES,
    FestivalRules,
    contest_score,
    prize_for,
    rank_among,
    resolve_contest,
    ribbon_score,
)
from app.rng import NeverRng


class _Rolls(random.Random):
    def __init__(self, values):
        super().__init__()
        self._values = list(values)

    def random(self):
        return self._values.pop(0)


def raw_rules():
    with open(
        __import__("app.game.festival", fromlist=["DATA_DIR"]).DATA_DIR / "festival.json",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def test_the_four_contests_are_keyed_to_the_four_festival_stats():
    assert FESTIVAL_STATS == ("affection", "discipline", "curiosity", "refinement")
    assert all(len(contest.rivals) == 3 for contest in RULES.contests.values())


@pytest.mark.parametrize(
    "roll, expected",
    [(0.0, 70), (0.5, 100), (1.0, 130)],
)
def test_score_is_the_stat_times_a_factor_from_0_7_to_1_3(roll, expected):
    assert contest_score(100, roll) == expected


def test_score_of_a_zero_stat_is_zero():
    assert contest_score(0, 1.0) == 0


@pytest.mark.parametrize(
    "own, rivals, rank",
    [
        (100, [10, 20, 30], 1),
        (25, [10, 20, 30], 2),
        (15, [10, 20, 30], 3),
        (5, [10, 20, 30], 4),
        (20, [20, 20, 20], 1),
        (20, [30, 20, 20], 2),
        (20, [30, 30, 30], 4),
    ],
)
def test_rank_is_the_place_among_four_and_ties_favor_the_player(own, rivals, rank):
    assert rank_among(own, rivals) == rank


def test_prize_and_ribbon_score_by_rank():
    assert [prize_for(rank) for rank in (1, 2, 3, 4)] == [300, 150, 50, 0]
    assert [ribbon_score(rank) for rank in (1, 2, 3, 4)] == [75, 60, 50, 0]


def test_resolve_rolls_the_player_first_then_rivals_in_data_order():
    contest = RULES.contests["charm"]
    rng = _Rolls([0.0, 1.0, 1.0, 1.0])

    result = resolve_contest("charm", 100, rng)

    assert result.score == 70
    assert result.rivals == tuple((r.id, round(r.base * 1.3)) for r in contest.rivals)
    assert rng._values == []


def test_resolve_with_never_rng_gives_everyone_the_top_factor():
    result = resolve_contest("grace", 100, NeverRng())

    assert result.score == 130
    assert result.rank == 1
    assert result.prize == 300
    assert result.ribbon is True
    assert result.stat == "refinement"


def test_a_weak_cat_is_last_and_wins_nothing():
    result = resolve_contest("charm", 0, NeverRng())

    assert (result.rank, result.prize, result.ribbon) == (4, 0, False)


def test_result_dict_is_json_ready():
    data = resolve_contest("charm", 60, NeverRng()).to_dict()

    assert json.loads(json.dumps(data)) == data
    assert set(data) == {"contest", "stat", "score", "rank", "prize", "rivals"}


def test_loader_accepts_the_shipped_file():
    assert FestivalRules.from_raw(raw_rules()).entry_stress == 5


@pytest.mark.parametrize(
    "mutate",
    [
        lambda raw: raw.pop("prizes"),
        lambda raw: raw.update(extra=1),
        lambda raw: raw["prizes"].pop("4"),
        lambda raw: raw["ribbon_scores"].update({"5": 1}),
        lambda raw: raw["prizes"].update({"1": -1}),
        lambda raw: raw["variance"].update(low=1.5),
        lambda raw: raw["contests"]["charm"].update(stat="health"),
        lambda raw: raw["contests"]["charm"]["rivals"].pop(),
        lambda raw: raw["contests"]["charm"]["rivals"][0].update(id="dubu"),
        lambda raw: raw["contests"]["charm"]["rivals"][0].pop("base"),
    ],
)
def test_loader_rejects_bad_data(mutate):
    raw = copy.deepcopy(raw_rules())
    mutate(raw)

    with pytest.raises(ValueError):
        FestivalRules.from_raw(raw)
