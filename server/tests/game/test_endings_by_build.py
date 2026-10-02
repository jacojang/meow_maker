import dataclasses
import json

import pytest

from app.game import CatStats, Ending, GameRun, RunSummary, compute_score, determine_ending
from app.game.endings import RULES, is_balanced, load_ending_rules

OVERWEIGHT_WEIGHT = 90
DEFAULT = {
    "health": 50,
    "affection": 50,
    "discipline": 50,
    "curiosity": 50,
    "refinement": 50,
    "stress": 0,
}


def stats(**overrides):
    return CatStats(**{**DEFAULT, **overrides})


def spread(low, **overrides):
    return stats(
        health=low + RULES.balance_gap,
        affection=low,
        discipline=low,
        curiosity=low,
        refinement=low,
        **overrides,
    )


@pytest.mark.parametrize(
    ("extra_gap", "expected"),
    [(0, True), (1, False)],
)
def test_balanced_boundary(extra_gap, expected):
    given = stats(health=40 + RULES.balance_gap + extra_gap, affection=40, discipline=40,
                  curiosity=40, refinement=40)

    assert is_balanced(given) is expected


def test_balanced_ending_when_gap_equals_the_limit():
    assert determine_ending(spread(40)) is Ending.BALANCED


def test_gap_one_over_the_limit_is_not_balanced():
    given = stats(health=40 + RULES.balance_gap + 1, affection=40, discipline=40,
                  curiosity=40, refinement=40)

    assert determine_ending(given) is Ending.HEALTHY


@pytest.mark.parametrize(
    ("extra_gap", "expect_pair"),
    [(0, True), (1, False)],
)
def test_pair_boundary(extra_gap, expect_pair):
    top = 80
    given = stats(health=top, affection=top - RULES.pair_gap - extra_gap,
                  discipline=10, curiosity=10, refinement=10)

    ending = determine_ending(given)

    assert (ending is Ending.PAIR_HEALTH_AFFECTION) is expect_pair
    if not expect_pair:
        assert ending is Ending.HEALTHY


PAIRS = [
    ("health", "affection", Ending.PAIR_HEALTH_AFFECTION),
    ("health", "discipline", Ending.PAIR_HEALTH_DISCIPLINE),
    ("health", "curiosity", Ending.PAIR_HEALTH_CURIOSITY),
    ("health", "refinement", Ending.PAIR_HEALTH_REFINEMENT),
    ("affection", "discipline", Ending.PAIR_AFFECTION_DISCIPLINE),
    ("affection", "curiosity", Ending.PAIR_AFFECTION_CURIOSITY),
    ("affection", "refinement", Ending.PAIR_AFFECTION_REFINEMENT),
    ("discipline", "curiosity", Ending.PAIR_DISCIPLINE_CURIOSITY),
    ("discipline", "refinement", Ending.PAIR_DISCIPLINE_REFINEMENT),
    ("curiosity", "refinement", Ending.PAIR_CURIOSITY_REFINEMENT),
]


@pytest.mark.parametrize(("first", "second", "expected"), PAIRS)
def test_every_pair_maps_to_its_ending_in_either_order(first, second, expected):
    base = dict(health=5, affection=5, discipline=5, curiosity=5, refinement=5)
    forward = stats(**{**base, first: 90, second: 90 - RULES.pair_gap})
    reverse = stats(**{**base, second: 90, first: 90 - RULES.pair_gap})

    assert determine_ending(forward) is expected
    assert determine_ending(reverse) is expected


def test_pair_endings_are_ten_distinct_values():
    assert len({ending for _, _, ending in PAIRS}) == 10


def test_priority_order_neglected_over_delinquent_over_balanced():
    sick = spread(40, stress=95)
    delinquent = stats(discipline=40, health=45, affection=45, curiosity=45,
                       refinement=45, stress=41)

    assert is_balanced(sick)
    assert determine_ending(sick) is Ending.NEGLECTED
    assert is_balanced(delinquent)
    assert determine_ending(delinquent) is Ending.DELINQUENT


def test_balanced_takes_priority_over_pair():
    given = stats(health=50, affection=48, discipline=45, curiosity=45, refinement=45)

    assert determine_ending(given) is Ending.BALANCED


def test_third_stat_close_to_the_top_does_not_matter_only_top_two():
    given = stats(health=90, affection=88, discipline=86, curiosity=10, refinement=10)

    assert determine_ending(given) is Ending.PAIR_HEALTH_AFFECTION


def test_tie_for_second_place_uses_stat_priority_order():
    given = stats(health=90, affection=10, discipline=84, curiosity=84, refinement=10)

    assert determine_ending(given) is Ending.PAIR_HEALTH_DISCIPLINE


def test_tie_for_first_place_uses_stat_priority_order():
    given = stats(health=10, affection=10, discipline=80, curiosity=80, refinement=10)

    assert determine_ending(given) is Ending.PAIR_DISCIPLINE_CURIOSITY


def test_single_ending_when_the_second_stat_is_far_behind():
    given = stats(health=10, affection=10, discipline=10, curiosity=10, refinement=90)

    assert determine_ending(given) is Ending.REFINED


def test_run_summary_and_bare_stats_give_the_same_result():
    given = spread(40)

    assert determine_ending(RunSummary(stats=given)) is determine_ending(given)
    assert compute_score(RunSummary(stats=given)) == compute_score(given)


def test_game_run_exposes_a_summary_of_its_stats():
    run = GameRun()

    assert run.summary == RunSummary(stats=run.stats)


def test_score_gets_the_balance_bonus():
    given = spread(40)
    base = sum(getattr(given, n) for n in ("health", "affection", "discipline", "curiosity", "refinement")) * 2

    assert compute_score(given) == base + RULES.balance_bonus


def test_score_overweight_penalty():
    given = spread(40, weight=OVERWEIGHT_WEIGHT)

    assert compute_score(given) == compute_score(spread(40)) - RULES.overweight_penalty


def test_score_high_stress_penalty_applies_above_the_threshold_only():
    at_threshold = spread(40, stress=RULES.stress_threshold)
    above = spread(40, stress=RULES.stress_threshold + 1)

    assert compute_score(at_threshold) == compute_score(spread(40))
    assert compute_score(above) == compute_score(spread(40)) - RULES.high_stress_penalty


def test_score_penalties_stack():
    given = spread(40, weight=OVERWEIGHT_WEIGHT, stress=RULES.stress_threshold + 1)

    expected = compute_score(spread(40)) - RULES.overweight_penalty - RULES.high_stress_penalty
    assert compute_score(given) == expected


def test_score_never_exceeds_the_cap_with_the_bonus():
    given = stats(health=100, affection=100, discipline=100, curiosity=100, refinement=100)

    assert compute_score(given) == 1000


def test_score_never_goes_below_zero_with_penalties():
    given = stats(health=0, affection=0, discipline=0, curiosity=0, refinement=0,
                  weight=100, stress=0)
    harsh = dataclasses.replace(RULES, balance_bonus=0, overweight_penalty=500)

    assert compute_score(given, harsh) == 0


def test_rules_are_loaded_from_a_data_file(tmp_path):
    path = tmp_path / "endings.json"
    path.write_text(json.dumps({
        "balance_gap": 3,
        "pair_gap": 2,
        "score": {"balance_bonus": 1, "overweight_penalty": 2,
                  "stress_threshold": 3, "high_stress_penalty": 4},
    }))

    rules = load_ending_rules(path)

    assert (rules.balance_gap, rules.pair_gap) == (3, 2)
    assert rules.high_stress_penalty == 4


def test_custom_rules_change_the_outcome():
    given = stats(health=60, affection=50, discipline=50, curiosity=50, refinement=50)
    strict = dataclasses.replace(RULES, balance_gap=0, pair_gap=0)

    assert determine_ending(given, strict) is Ending.HEALTHY
