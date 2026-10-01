from simulation import CARE_STRATEGIES, STRATEGIES, rate_of, simulate

from app.game import Ending

RUNS = 200


def ran_away(strategy):
    return rate_of(simulate(strategy, runs=RUNS), Ending.RAN_AWAY)


def test_a_deliberately_neglectful_schedule_runs_away():
    assert ran_away(CARE_STRATEGIES["neglectful"]) > 0.9


def test_scolding_the_same_neglectful_schedule_prevents_it():
    assert ran_away(CARE_STRATEGIES["attentive"]) == 0.0


def test_normal_strategies_do_not_run_away_by_default():
    for name in ("careless", "grinder", "balanced", "careful"):
        assert ran_away(STRATEGIES[name]) == 0.0, name


def test_random_and_targeted_play_almost_never_runs_away():
    for name in ("random", "targeted"):
        assert ran_away(STRATEGIES[name]) < 0.03, name
