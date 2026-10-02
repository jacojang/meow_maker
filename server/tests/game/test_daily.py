import json
import random
from fractions import Fraction

import pytest

from app.game import SLOTS_PER_MONTH, Activity, CatStats, GameRun
from app.game.daily import (
    MONTH_DAYS,
    VARIANCE_ACTIVITIES,
    DailyRules,
    DayOutcome,
    DayYield,
    days_in_month,
    outcome_weights,
    pick_outcome,
    slot_day_counts,
)
from app.rng import NeverRng


class _ScriptedDayRng(random.Random):
    def __init__(self, values):
        super().__init__()
        self._values = list(values)

    def random(self):
        return self._values.pop(0) if self._values else 1.0


def _advance(run, *activities, day_rng=None):
    run.assign_month(list(activities))
    run.advance_month(rng=NeverRng(), day_rng=day_rng or NeverRng())


def test_month_table_matches_the_client_calendar_literal():
    assert MONTH_DAYS == (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    assert days_in_month(2) == 28


@pytest.mark.parametrize(
    "days, expected",
    [(30, [10, 10, 10]), (31, [10, 10, 11]), (28, [9, 9, 10]), (29, [9, 9, 11])],
)
def test_slot_day_counts_follow_the_client_split(days, expected):
    assert slot_day_counts(days, 3) == expected
    assert sum(slot_day_counts(days, 3)) == days


def test_roll_thresholds():
    assert pick_outcome(0.0, 0.25, 0.25) is DayOutcome.FAIL
    assert pick_outcome(0.2499, 0.25, 0.25) is DayOutcome.FAIL
    assert pick_outcome(0.25, 0.25, 0.25) is DayOutcome.GREAT
    assert pick_outcome(0.4999, 0.25, 0.25) is DayOutcome.GREAT
    assert pick_outcome(0.5, 0.25, 0.25) is DayOutcome.NORMAL
    assert pick_outcome(1.0, 0.25, 0.25) is DayOutcome.NORMAL


def test_low_stress_keeps_the_base_weights():
    assert outcome_weights(0) == (0.25, 0.25)
    assert outcome_weights(DailyRules().stress_threshold) == (0.25, 0.25)


def test_high_stress_moves_weight_from_normal_to_fail_only():
    p_fail, p_great = outcome_weights(100)

    assert p_fail > 0.25
    assert p_great == 0.25
    assert p_fail + p_great <= 1.0


def test_stress_shift_is_capped():
    rules = DailyRules()
    assert outcome_weights(100)[0] == pytest.approx(rules.fail_weight + rules.max_fail_shift)


def test_data_file_loads_and_rejects_unknown_keys(tmp_path):
    assert DailyRules.load().fail_weight == 0.25
    bad = tmp_path / "daily.json"
    bad.write_text(json.dumps({"nope": 1}))
    with pytest.raises(ValueError):
        DailyRules.load(bad)


def test_day_yield_sums_to_the_base_on_normal_days():
    yields = DayYield({"discipline": 5, "stress": 8, "refinement": -2}, 11)
    totals = {}
    for _ in range(11):
        for name, delta in yields.next_day(DayOutcome.NORMAL, rolled=True).items():
            totals[name] = totals.get(name, 0) + delta

    assert totals == {"discipline": 5, "stress": 8, "refinement": -2}


def test_fail_days_give_no_growth_and_great_days_double_it():
    fail, great = DayYield({"discipline": 5}, 10), DayYield({"discipline": 5}, 10)

    assert sum(fail.next_day(DayOutcome.FAIL, rolled=True).get("discipline", 0) for _ in range(10)) == 0
    assert sum(great.next_day(DayOutcome.GREAT, rolled=True).get("discipline", 0) for _ in range(10)) == 10


def test_negative_deltas_and_stress_ignore_the_multiplier():
    for outcome in (DayOutcome.FAIL, DayOutcome.GREAT):
        yields = DayYield({"refinement": -2, "stress": 12}, 10)
        totals = {"refinement": 0, "stress": 0}
        for _ in range(10):
            for name, delta in yields.next_day(outcome, rolled=True).items():
                totals[name] += delta
        assert totals == {"refinement": -2, "stress": 12}


def test_unrolled_activity_ignores_the_outcome():
    yields = DayYield({"affection": 4}, 4)

    assert sum(yields.next_day(DayOutcome.GREAT, rolled=False).get("affection", 0) for _ in range(4)) == 4


def test_cumulative_rounding_matches_the_rounded_running_total():
    yields = DayYield({"curiosity": 3}, 10)
    given = 0
    raw = Fraction(0)
    for _ in range(10):
        given += yields.next_day(DayOutcome.GREAT, rolled=True).get("curiosity", 0)
        raw += Fraction(6, 10)
        assert given in (int(raw), int(raw) + 1)
    assert given == 6


def test_rest_and_outing_have_no_variance():
    assert Activity.REST not in VARIANCE_ACTIVITIES
    assert Activity.OUTING not in VARIANCE_ACTIVITIES


def test_never_rng_gives_exactly_the_base_effects():
    run = GameRun()
    _advance(run, Activity.TRAIN, Activity.TRAIN, Activity.TRAIN)

    log = run.last_month_log
    assert [entry["slot"] for entry in log] == [0, 1, 2]
    assert all(day["outcome"] == "normal" for entry in log for day in entry["days"])
    total = sum(day["deltas"].get("discipline", 0) for entry in log for day in entry["days"])
    assert total == 15


def test_log_covers_every_day_of_the_month_in_order():
    run = GameRun(month=2)
    _advance(run, Activity.PLAY, Activity.REST, Activity.OUTING)

    days = [day["day"] for entry in run.last_month_log for day in entry["days"]]
    assert days == list(range(1, 29))
    assert [len(entry["days"]) for entry in run.last_month_log] == [9, 9, 10]
    assert [entry["activity"] for entry in run.last_month_log] == ["play", "rest", "outing"]


def test_a_fail_day_cancels_growth_and_great_doubles_it():
    fail_run, great_run = GameRun(), GameRun()
    _advance(fail_run, Activity.TRAIN, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([0.0] * 10))
    _advance(great_run, Activity.TRAIN, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([0.3] * 10))

    assert fail_run.stats.discipline == 10
    assert great_run.stats.discipline == 20
    assert {d["outcome"] for d in fail_run.last_month_log[0]["days"]} == {"fail"}
    assert {d["outcome"] for d in great_run.last_month_log[0]["days"]} == {"great"}


def test_variance_does_not_change_stress():
    fail_run, great_run = GameRun(), GameRun()
    _advance(fail_run, Activity.TRAIN, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([0.0] * 10))
    _advance(great_run, Activity.TRAIN, Activity.REST, Activity.REST, day_rng=_ScriptedDayRng([0.3] * 10))

    assert fail_run.stats.stress == great_run.stats.stress


def test_rest_consumes_no_day_rolls():
    rng = _ScriptedDayRng([])
    run = GameRun()
    _advance(run, Activity.REST, Activity.OUTING, Activity.REST, day_rng=rng)

    assert all(d["outcome"] == "normal" for e in run.last_month_log for d in e["days"])


def test_sick_halving_is_read_at_slot_start():
    run = GameRun(stats=CatStats(health=10, stress=30))
    _advance(run, Activity.TRAIN, Activity.REST, Activity.REST)

    assert sum(d["deltas"].get("discipline", 0) for d in run.last_month_log[0]["days"]) == 2


def test_log_round_trips_and_old_saves_default_to_empty():
    run = GameRun()
    _advance(run, Activity.PLAY, Activity.TRAIN, Activity.REST)

    restored = GameRun.from_dict(json.loads(json.dumps(run.to_dict())))
    assert restored.last_month_log == run.last_month_log

    old = run.to_dict()
    del old["last_month_log"]
    assert GameRun.from_dict(old).last_month_log == []


def test_log_is_replaced_each_month():
    run = GameRun()
    _advance(run, Activity.REST, Activity.REST, Activity.REST)
    _advance(run, Activity.REST, Activity.REST, Activity.REST)

    assert len(run.last_month_log) == SLOTS_PER_MONTH
    assert run.last_month_log[0]["days"][0]["day"] == 1


def test_mean_multiplier_is_one_at_low_stress():
    from app.game.daily import OUTCOME_MULTIPLIER

    p_fail, p_great = outcome_weights(0)
    mean = (
        p_fail * OUTCOME_MULTIPLIER[DayOutcome.FAIL]
        + (1 - p_fail - p_great) * OUTCOME_MULTIPLIER[DayOutcome.NORMAL]
        + p_great * OUTCOME_MULTIPLIER[DayOutcome.GREAT]
    )
    assert mean == pytest.approx(1.0)
