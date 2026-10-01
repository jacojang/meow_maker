from simulation import (
    ECONOMY_STRATEGIES,
    broke_run_rate,
    denied_month_rate,
    downgrade_to_affordable,
    mean_score,
    simulate,
)

from app.game import Activity, GameRun, cost_of

RUNS = 300


def _play(name):
    return simulate(ECONOMY_STRATEGIES[name], runs=RUNS, run_factory=GameRun)


def test_downgrade_swaps_paid_slots_from_the_end_until_affordable():
    plan = [Activity.EDUCATE, Activity.TRAIN, Activity.OUTING]

    result = downgrade_to_affordable(plan, cost_of(Activity.EDUCATE), Activity.JOB)

    assert result == [Activity.EDUCATE, Activity.JOB, Activity.JOB]


def test_downgrade_leaves_an_affordable_plan_alone():
    plan = [Activity.TRAIN, Activity.REST, Activity.PLAY]

    assert downgrade_to_affordable(plan, 1000, Activity.JOB) == plan


def test_mixed_play_is_sometimes_but_not_mostly_denied_a_paid_slot():
    assert 0.10 <= denied_month_rate(_play("mixed")) <= 0.30


def test_spending_on_every_paid_option_runs_out_of_money():
    results = _play("spend_everything")

    assert denied_month_rate(results) > 0.5
    assert broke_run_rate(results) > 0.5
    assert sum(r.final_money for r in results) / len(results) < 20


def test_mixed_beats_all_job_and_all_train_on_score():
    mixed = mean_score(_play("mixed"))

    assert mixed > mean_score(_play("all_job"))
    assert mixed > mean_score(_play("all_train"))
