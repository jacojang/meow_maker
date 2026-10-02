import pytest
from simulation import STRATEGIES, rate_of, simulate

from app.game import Ending

RUNS = 200


def early_or_neglected(results):
    return rate_of(results, Ending.HOSPITALIZED) + rate_of(results, Ending.NEGLECTED)


def test_careful_play_never_ends_early_or_neglected():
    assert early_or_neglected(simulate(STRATEGIES["careful"], runs=RUNS)) == 0.0


def test_deliberate_balancing_almost_never_ends_early_or_neglected():
    assert early_or_neglected(simulate(STRATEGIES["targeted"], runs=RUNS)) < 0.05


@pytest.mark.parametrize("name", ["careless", "grinder"])
def test_careless_and_grinder_end_hospitalized(name):
    assert rate_of(simulate(STRATEGIES[name], runs=RUNS), Ending.HOSPITALIZED) > 0.9


def test_forced_rest_breaks_the_neglect_cycle_of_pure_rotation():
    assert rate_of(simulate(STRATEGIES["balanced"], runs=RUNS), Ending.NEGLECTED) < 0.05


def test_random_play_ends_early_or_neglected_in_a_minority_of_runs():
    assert early_or_neglected(simulate(STRATEGIES["random"], runs=RUNS)) < 0.6


def test_forced_rest_is_not_a_free_reset():
    # Playing straight through sickness never gets the run to a normal ending.
    results = simulate(STRATEGIES["careless"], runs=RUNS)

    assert all(result.score <= 300 for result in results)
