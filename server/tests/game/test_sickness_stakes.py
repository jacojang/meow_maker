import dataclasses

import pytest

from app.game import (
    SLOTS_PER_MONTH,
    Activity,
    apply_activity,
    CatStats,
    Ending,
    GameRun,
    RunSummary,
    compute_score,
    determine_ending,
)
from app.game.endings import RULES, load_ending_rules
from app.game.warnings import compute_warnings
from app.rng import NeverRng

SICK = CatStats(health=10, stress=50, discipline=100)
HEALTHY = CatStats(health=80, stress=0, discipline=100)
REST_MONTH = [Activity.REST] * SLOTS_PER_MONTH
PLAY_MONTH = [Activity.PLAY] * SLOTS_PER_MONTH


def advance(run, activities=None):
    run.assign_month(activities or PLAY_MONTH)
    run.advance_month(rng=NeverRng())


def sick_run(**counters):
    return GameRun(stats=SICK, **counters)


def test_fresh_run_has_zero_counters():
    run = GameRun()

    assert (run.sick_streak, run.sick_months_total, run.bedridden_months) == (0, 0, 0)
    assert run.is_bedridden is False


def test_sick_month_end_raises_streak_and_total():
    run = sick_run()

    advance(run, [Activity.PLAY] * SLOTS_PER_MONTH)

    assert run.is_sick
    assert (run.sick_streak, run.sick_months_total) == (1, 1)


def test_healthy_month_end_resets_streak_but_keeps_total():
    run = GameRun(stats=HEALTHY, sick_streak=1, sick_months_total=3)

    advance(run, REST_MONTH)

    assert (run.sick_streak, run.sick_months_total) == (0, 3)


def test_not_bedridden_below_streak_and_bedridden_at_it():
    below = GameRun(sick_streak=RULES.bedridden_streak - 1)
    at = GameRun(sick_streak=RULES.bedridden_streak)

    assert below.is_bedridden is False
    assert at.is_bedridden is True


def test_forced_slots_are_exposed_only_while_bedridden():
    assert GameRun().forced_slots is None
    assert GameRun(sick_streak=2).forced_slots == REST_MONTH


def test_bedridden_month_replaces_hostile_client_slots_with_rest():
    run = GameRun(stats=HEALTHY, sick_streak=2)
    run.assign_month([Activity.PLAY, Activity.TRAIN, Activity.OUTING])

    run.advance_month(rng=NeverRng())

    expected = HEALTHY
    for activity in REST_MONTH:
        expected = apply_activity(expected, activity)
    assert run.stats.stress == expected.stress
    assert run.bedridden_months == 1


def test_bedridden_month_ignores_incomplete_slots():
    run = GameRun(stats=HEALTHY, sick_streak=2)

    run.advance_month(rng=NeverRng())

    assert run.bedridden_months == 1


def test_normal_month_does_not_count_as_bedridden():
    run = GameRun(stats=HEALTHY, sick_streak=1)

    advance(run, REST_MONTH)

    assert run.bedridden_months == 0


def test_forced_rest_can_cure_and_resets_streak():
    run = GameRun(stats=dataclasses.replace(SICK, stress=60), sick_streak=2)

    advance(run)

    assert run.is_sick is False
    assert run.sick_streak == 0
    assert run.bedridden_months == 1


def test_hospitalized_at_the_limit_ends_the_run_without_advancing_month():
    run = GameRun(stats=SICK, month=5, sick_streak=2, bedridden_months=RULES.hospital_limit - 1)
    run.stats = dataclasses.replace(SICK, stress=100)

    advance(run)

    assert run.bedridden_months == RULES.hospital_limit
    assert run.finished is True
    assert run.month == 5
    assert run.ending is Ending.HOSPITALIZED
    assert run.score <= RULES.early_end_score_cap
    assert run.forced_slots is None


def test_one_below_the_limit_keeps_playing():
    run = GameRun(stats=HEALTHY, month=5, sick_streak=2, bedridden_months=RULES.hospital_limit - 2)

    advance(run)

    assert run.finished is False
    assert run.month == 6


def test_early_ending_score_is_capped_but_other_scores_are_not():
    strong = CatStats(health=100, affection=100, discipline=100, curiosity=100, refinement=100)
    hospitalized = RunSummary(stats=strong, bedridden_months=RULES.hospital_limit)

    assert determine_ending(hospitalized) is Ending.HOSPITALIZED
    assert compute_score(hospitalized) == RULES.early_end_score_cap
    assert compute_score(RunSummary(stats=strong)) > RULES.early_end_score_cap


def test_neglected_by_total_even_when_healed_at_the_end():
    healed = RunSummary(stats=HEALTHY, sick_months_total=RULES.neglect_total)
    almost = RunSummary(stats=HEALTHY, sick_months_total=RULES.neglect_total - 1)

    assert determine_ending(healed) is Ending.NEGLECTED
    assert determine_ending(almost) is not Ending.NEGLECTED


def test_score_loses_a_penalty_per_sick_month_and_floors_at_zero():
    stats = CatStats(health=60, affection=60, discipline=60, curiosity=60, refinement=60)
    base = compute_score(RunSummary(stats=stats))

    assert compute_score(RunSummary(stats=stats, sick_months_total=2)) == base - 2 * RULES.sick_month_penalty
    assert compute_score(RunSummary(stats=CatStats(), sick_months_total=50)) == 0


def test_sickness_numbers_load_from_the_data_file(tmp_path):
    path = tmp_path / "endings.json"
    path.write_text(
        '{"balance_gap": 1, "pair_gap": 1, "score": {"balance_bonus": 0,'
        ' "overweight_penalty": 0, "stress_threshold": 0, "high_stress_penalty": 0},'
        ' "sickness": {"hospital_limit": 9, "neglect_total": 8}}'
    )

    rules = load_ending_rules(path)

    assert (rules.hospital_limit, rules.neglect_total) == (9, 8)
    assert rules.bedridden_streak == RULES.bedridden_streak


def test_bedridden_warning_while_bedridden():
    assert "bedridden" in GameRun(stats=SICK, sick_streak=2).warnings
    assert "bedridden" not in GameRun(stats=SICK, sick_streak=1).warnings


def test_hospital_risk_fires_on_the_last_actionable_month():
    at_trigger = GameRun(
        stats=SICK,
        sick_streak=RULES.bedridden_streak - 1,
        bedridden_months=RULES.hospital_limit - 1,
    )
    too_early = GameRun(
        stats=SICK,
        sick_streak=RULES.bedridden_streak - 1,
        bedridden_months=RULES.hospital_limit - 2,
    )
    healed = GameRun(
        stats=HEALTHY,
        sick_streak=RULES.bedridden_streak - 1,
        bedridden_months=RULES.hospital_limit - 1,
    )

    assert "hospital_risk" in at_trigger.warnings
    assert "hospital_risk" not in too_early.warnings
    assert "hospital_risk" not in healed.warnings


def test_hospital_risk_is_replaced_by_bedridden_once_forced():
    run = GameRun(stats=SICK, sick_streak=2, bedridden_months=RULES.hospital_limit - 1)

    assert "bedridden" in run.warnings
    assert "hospital_risk" not in run.warnings


def test_warning_helper_flags_default_off():
    assert compute_warnings(SICK) == ["sick"]


def test_counters_round_trip_and_old_saves_default_to_zero():
    run = GameRun(sick_streak=2, sick_months_total=4, bedridden_months=1)
    restored = GameRun.from_dict(run.to_dict())
    legacy = run.to_dict()
    for key in ("sick_streak", "sick_months_total", "bedridden_months"):
        del legacy[key]

    assert (restored.sick_streak, restored.sick_months_total, restored.bedridden_months) == (2, 4, 1)
    old = GameRun.from_dict(legacy)
    assert (old.sick_streak, old.sick_months_total, old.bedridden_months) == (0, 0, 0)


def test_warning_trace_matches_the_planning_doc():
    run = GameRun(stats=SICK)
    advance(run)
    advance(run)
    assert run.is_bedridden

    month_before = run.month
    advance(run, REST_MONTH)
    assert run.bedridden_months == 1
    assert run.finished is False or run.month == month_before


@pytest.mark.parametrize("finished_month", [12])
def test_hospital_check_wins_over_normal_finish_at_month_twelve(finished_month):
    run = GameRun(
        stats=SICK, month=finished_month, sick_streak=2,
        bedridden_months=RULES.hospital_limit - 1,
    )
    run.stats = dataclasses.replace(SICK, stress=100)

    advance(run)

    assert run.ending is Ending.HOSPITALIZED
