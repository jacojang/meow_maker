import random

import pytest
from simulation import (
    STRATEGIES,
    MonthPlan,
    careless,
    careful,
    ending_rates,
    format_report,
    mean_score,
    play_run,
    rate_of,
    simulate,
    targeted,
)

from app.game import SLOTS_PER_MONTH, Activity, Ending, GameRun

RUNS = 200


def test_every_named_strategy_is_registered():
    assert {"careless", "grinder", "random", "balanced", "careful"} <= set(STRATEGIES)


@pytest.mark.parametrize("name", sorted(STRATEGIES))
def test_each_strategy_plans_a_full_month(name):
    plan = STRATEGIES[name](GameRun(), random.Random(0))

    assert len(plan.activities) == SLOTS_PER_MONTH
    assert all(isinstance(activity, Activity) for activity in plan.activities)


def test_same_seed_gives_the_same_result():
    first = play_run(STRATEGIES["random"], seed=7)
    second = play_run(STRATEGIES["random"], seed=7)

    assert first == second


def test_runs_are_configurable_and_use_consecutive_seeds():
    results = simulate(careless, runs=5, base_seed=100)

    assert [result.seed for result in results] == [100, 101, 102, 103, 104]


def test_every_run_finishes_with_an_ending_and_a_score_in_range():
    for result in simulate(STRATEGIES["random"], runs=RUNS):
        assert result.ending is not None
        assert 0 <= result.score <= 1000


def test_run_factory_lets_a_slice_start_from_its_own_run():
    results = simulate(careless, runs=3, run_factory=lambda: GameRun(month=12))

    assert len(results) == 3


def test_custom_strategies_plug_in():
    always_rest = lambda run, rng: MonthPlan([Activity.REST] * SLOTS_PER_MONTH)

    assert rate_of(simulate(always_rest, runs=20), Ending.NEGLECTED) == 0.0


def test_ending_rates_sum_to_one():
    rates = ending_rates(simulate(STRATEGIES["random"], runs=RUNS))

    assert sum(rates.values()) == pytest.approx(1.0)


def test_report_is_readable():
    report = format_report("careless", simulate(careless, runs=10))

    assert report.startswith("careless: n=10 mean_score=")


@pytest.mark.parametrize("name", ["careless", "grinder", "random", "balanced", "careful"])
def test_default_play_rarely_reaches_balanced(name):
    results = simulate(STRATEGIES[name], runs=RUNS)

    assert rate_of(results, Ending.BALANCED) < 0.10


def test_deliberate_stat_balancing_often_reaches_balanced():
    results = simulate(targeted, runs=RUNS)

    assert rate_of(results, Ending.BALANCED) >= 0.5


def test_careless_and_grinder_runs_fail_hard():
    for strategy in (careless, STRATEGIES["grinder"]):
        results = simulate(strategy, runs=RUNS)
        failed = rate_of(results, Ending.NEGLECTED) + rate_of(results, Ending.HOSPITALIZED)
        assert failed > 0.9


def test_careful_play_avoids_the_failure_endings_and_beats_careless_on_score():
    careful_results = simulate(careful, runs=RUNS)

    assert rate_of(careful_results, Ending.NEGLECTED) == 0.0
    assert rate_of(careful_results, Ending.DELINQUENT) == 0.0
    assert mean_score(careful_results) > mean_score(simulate(careless, runs=RUNS))
