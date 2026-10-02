import json
import random

import pytest

from app.game import (
    START_MONEY,
    Activity,
    CatStats,
    GameRun,
    InsufficientMoneyError,
    cost_of,
)
from app.game.daily import OUTCOME_MULTIPLIER, DayOutcome
from app.rng import NeverRng

JOB_DAYS_FIRST_SLOT = 10


class _ScriptedDayRng(random.Random):
    def __init__(self, values):
        super().__init__()
        self._values = list(values)

    def random(self):
        return self._values.pop(0) if self._values else 1.0


FAIL, GREAT, NORMAL = 0.0, 0.3, 0.6


def _advance(run, *activities, day_rng=None):
    run.assign_month(list(activities))
    run.advance_month(rng=NeverRng(), day_rng=day_rng or NeverRng())


def test_a_new_run_starts_with_the_starting_money():
    assert GameRun().money == START_MONEY


def test_old_saves_without_money_load_with_the_starting_amount():
    data = GameRun().to_dict()
    del data["money"]

    assert GameRun.from_dict(data).money == START_MONEY


def test_money_round_trips():
    run = GameRun(money=77)

    assert GameRun.from_dict(json.loads(json.dumps(run.to_dict()))).money == 77


def test_money_can_never_be_constructed_negative():
    with pytest.raises(ValueError):
        GameRun(money=-1)


def test_a_schedule_costing_exactly_the_money_is_accepted():
    run = GameRun(money=2 * cost_of(Activity.TRAIN))

    run.assign_month([Activity.TRAIN, Activity.TRAIN, Activity.REST])

    assert run.slots[0] == Activity.TRAIN


def test_one_over_the_money_is_rejected_and_changes_nothing():
    run = GameRun(money=2 * cost_of(Activity.TRAIN) - 1)

    with pytest.raises(InsufficientMoneyError):
        run.assign_month([Activity.TRAIN, Activity.TRAIN, Activity.REST])

    assert run.slots == [None, None, None]


def test_advance_month_also_refuses_an_unaffordable_schedule_set_by_slot():
    run = GameRun(money=0)
    for index in range(3):
        run.assign_slot(index, Activity.EDUCATE)

    with pytest.raises(InsufficientMoneyError):
        run.advance_month(rng=NeverRng(), day_rng=NeverRng())

    assert run.money == 0
    assert run.month == 1


def test_free_options_and_the_job_are_always_available():
    run = GameRun(money=0)

    run.assign_month([Activity.PLAY, Activity.GROOM, Activity.JOB])


def test_cost_is_charged_per_slot_whatever_the_outcomes():
    fail_run, great_run = GameRun(money=500), GameRun(money=500)
    _advance(fail_run, Activity.TRAIN, Activity.EDUCATE, Activity.REST, day_rng=_ScriptedDayRng([FAIL] * 40))
    _advance(great_run, Activity.TRAIN, Activity.EDUCATE, Activity.REST, day_rng=_ScriptedDayRng([GREAT] * 40))

    spent = cost_of(Activity.TRAIN) + cost_of(Activity.EDUCATE)
    assert fail_run.money == great_run.money == 500 - spent


def test_the_log_records_each_slots_cost():
    run = GameRun(money=500)
    _advance(run, Activity.TRAIN, Activity.REST, Activity.OUTING)

    assert [entry["cost"] for entry in run.last_month_log] == [
        cost_of(Activity.TRAIN),
        0,
        cost_of(Activity.OUTING),
    ]


def test_forced_rest_is_free_and_ignores_an_unaffordable_payload():
    run = GameRun(money=0, sick_streak=2, stats=CatStats(health=10, stress=30))

    _advance(run, Activity.EDUCATE, Activity.EDUCATE, Activity.EDUCATE)

    assert run.money == 0
    assert [e["activity"] for e in run.last_month_log] == ["rest"] * 3


def test_all_normal_days_pay_per_day_plus_the_perfect_bonus():
    run = GameRun(money=0)
    _advance(run, Activity.JOB, Activity.REST, Activity.REST)

    entry = run.last_month_log[0]
    assert (entry["income"], entry["bonus"]) == (120, 40)
    assert run.money == 120
    assert all(day["income"] == 8 for day in entry["days"])


def test_a_fail_day_pays_nothing_and_forfeits_the_bonus():
    run = GameRun(money=0)
    rolls = [FAIL] + [NORMAL] * 9
    _advance(run, Activity.JOB, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng(rolls))

    entry = run.last_month_log[0]
    assert entry["days"][0]["income"] == 0
    assert (entry["income"], entry["bonus"]) == (72, 0)
    assert run.money == 72


def test_great_days_pay_the_same_as_normal_days():
    run = GameRun(money=0)
    _advance(run, Activity.JOB, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([GREAT] * 10))

    assert run.last_month_log[0]["income"] == 120


def test_an_all_fail_slot_pays_nothing():
    run = GameRun(money=0)
    _advance(run, Activity.JOB, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([FAIL] * 10))

    assert run.money == 0


def test_job_stat_effects_apply_whatever_the_outcome():
    totals = {}
    for name, roll in (("fail", FAIL), ("normal", NORMAL), ("great", GREAT)):
        run = GameRun(money=0, stats=CatStats(curiosity=30, refinement=30, stress=0))
        _advance(run, Activity.JOB, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([roll] * 10))
        totals[name] = (run.stats.curiosity, run.stats.refinement)

    assert totals["fail"] == totals["normal"] == totals["great"] == (32, 28)


def test_job_stress_is_not_scaled_by_the_outcome():
    run = GameRun(money=0, stats=CatStats(stress=0))
    _advance(run, Activity.JOB, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([GREAT] * 10))

    assert run.stats.stress == 0  # +8 job, then -20 rest, floored at 0
    run = GameRun(money=0, stats=CatStats(stress=0))
    _advance(run, Activity.JOB, Activity.JOB, Activity.JOB, day_rng=_ScriptedDayRng([FAIL] * 31))
    assert run.stats.stress == 24


def test_outcome_multiplier_table_is_untouched_by_the_job():
    assert OUTCOME_MULTIPLIER[DayOutcome.GREAT] == 2


def test_a_sick_cat_earns_half_per_day_and_gets_halved_stat_effects_but_full_stress():
    run = GameRun(money=0, stats=CatStats(health=10, stress=30, curiosity=30, refinement=30))
    _advance(run, Activity.JOB, Activity.REST, Activity.REST)

    entry = run.last_month_log[0]
    assert all(day["income"] == 4 for day in entry["days"])
    assert entry["income"] == 60
    assert sum(d["deltas"].get("curiosity", 0) for d in entry["days"]) == 1
    assert sum(d["deltas"].get("refinement", 0) for d in entry["days"]) == -1
    assert sum(d["deltas"].get("stress", 0) for d in entry["days"]) == 8


def test_non_job_days_carry_no_income_key():
    run = GameRun()
    _advance(run, Activity.TRAIN, Activity.REST, Activity.PLAY)

    assert all("income" not in day for e in run.last_month_log for day in e["days"])
    assert all(e["income"] == 0 for e in run.last_month_log)


def test_the_job_rolls_days_so_the_outcome_can_drive_pay():
    run = GameRun(money=0)
    _advance(run, Activity.JOB, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([GREAT] * 10))

    assert {d["outcome"] for d in run.last_month_log[0]["days"]} == {"great"}


def test_money_never_goes_negative_over_a_run_of_the_priciest_options():
    run = GameRun()
    while not run.finished:
        affordable = [
            a for a in (Activity.EDUCATE, Activity.TRAIN, Activity.OUTING) if cost_of(a) <= run.money
        ]
        pick = affordable[0] if affordable else Activity.REST
        _advance(run, pick, Activity.REST, Activity.REST)
        assert run.money >= 0
