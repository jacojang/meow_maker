import pytest

from app.game import (
    MONTHS_PER_RUN,
    SLOTS_PER_MONTH,
    Activity,
    CatStats,
    Diet,
    GameRun,
    IncompleteMonthError,
    RunFinishedError,
)


def play_month(run, *activities):
    run.assign_month(list(activities))
    run.advance_month()


def test_new_run_starts_at_month_one_with_empty_slots():
    run = GameRun()

    assert run.month == 1
    assert run.finished is False
    assert run.slots == [None] * SLOTS_PER_MONTH
    assert run.stats == CatStats()


def test_advancing_a_month_resolves_all_three_slots():
    run = GameRun()

    play_month(run, Activity.TRAIN, Activity.TRAIN, Activity.GROOM)

    assert run.stats.discipline == 20
    assert run.stats.affection == 23
    assert run.stats.health == 51
    assert run.stats.stress == 19
    assert run.month == 2


def test_slots_resolve_in_order():
    forward = GameRun()
    play_month(forward, Activity.PLAY, Activity.PLAY, Activity.REST)

    backward = GameRun()
    play_month(backward, Activity.REST, Activity.PLAY, Activity.PLAY)

    assert forward.stats.stress == 4
    assert backward.stats.stress == 24


def test_sickness_is_recomputed_between_slots():
    run = GameRun(stats=CatStats(health=10, stress=0))

    play_month(run, Activity.TRAIN, Activity.TRAIN, Activity.TRAIN)

    assert run.stats.discipline == 10 + 5 + 5 + 2
    assert run.stats.stress == 24


def test_slots_reset_after_advancing():
    run = GameRun()

    play_month(run, Activity.REST, Activity.REST, Activity.REST)

    assert run.slots == [None] * SLOTS_PER_MONTH


def test_assign_slot_fills_one_position():
    run = GameRun()

    run.assign_slot(0, Activity.PLAY)
    run.assign_slot(2, Activity.REST)

    assert run.slots == [Activity.PLAY, None, Activity.REST]


def test_advancing_with_unassigned_slots_is_rejected():
    run = GameRun()
    run.assign_slot(0, Activity.PLAY)

    with pytest.raises(IncompleteMonthError):
        run.advance_month()

    assert run.month == 1


def test_assign_month_rejects_a_wrong_number_of_activities():
    run = GameRun()

    with pytest.raises(IncompleteMonthError):
        run.assign_month([Activity.PLAY, Activity.REST])


def test_assign_slot_rejects_an_out_of_range_index():
    run = GameRun()

    with pytest.raises(IndexError):
        run.assign_slot(SLOTS_PER_MONTH, Activity.PLAY)


def test_the_cat_becomes_sick_once_stress_passes_health():
    run = GameRun(stats=CatStats(health=20, stress=12))
    assert not run.is_sick

    play_month(run, Activity.PLAY, Activity.GROOM, Activity.GROOM)

    assert run.is_sick
    assert run.stats.stress == 30
    assert run.stats.affection == 26
    assert run.stats.health == 20


def test_sickness_degrades_gains_until_rest_recovers():
    run = GameRun(stats=CatStats(health=20, stress=16))

    run.assign_month([Activity.TRAIN, Activity.TRAIN, Activity.REST])
    run.advance_month()

    assert run.stats.discipline == 10 + 5 + 2
    assert run.stats.stress == 12
    assert not run.is_sick

    play_month(run, Activity.TRAIN, Activity.REST, Activity.REST)

    assert run.stats.discipline == 22
    assert run.stats.stress == 0
    assert not run.is_sick


def test_run_finishes_after_twelve_months():
    run = GameRun()

    for month in range(1, MONTHS_PER_RUN + 1):
        assert run.month == month
        assert run.finished is False
        play_month(run, Activity.REST, Activity.REST, Activity.REST)

    assert run.month == MONTHS_PER_RUN
    assert run.finished is True


def test_advancing_past_the_end_is_rejected():
    run = GameRun(month=MONTHS_PER_RUN)
    play_month(run, Activity.REST, Activity.REST, Activity.REST)
    assert run.finished is True

    with pytest.raises(RunFinishedError):
        run.advance_month()

    with pytest.raises(RunFinishedError):
        run.assign_month([Activity.REST] * SLOTS_PER_MONTH)

    with pytest.raises(RunFinishedError):
        run.assign_slot(0, Activity.REST)


def test_new_run_defaults_to_the_normal_diet():
    run = GameRun()

    assert run.diet == Diet.NORMAL


def test_assign_diet_changes_the_active_diet():
    run = GameRun()

    run.assign_diet(Diet.HEARTY)

    assert run.diet == Diet.HEARTY


def test_assign_diet_is_rejected_once_the_run_is_finished():
    run = GameRun(month=MONTHS_PER_RUN)
    play_month(run, Activity.REST, Activity.REST, Activity.REST)
    assert run.finished is True

    with pytest.raises(RunFinishedError):
        run.assign_diet(Diet.LIGHT)


def test_advance_month_applies_the_active_diet():
    run = GameRun()

    run.assign_diet(Diet.LIGHT)
    play_month(run, Activity.REST, Activity.REST, Activity.REST)

    assert run.stats.weight == 49


def test_advance_month_increments_age_by_one_regardless_of_diet_or_activities():
    run = GameRun()

    run.assign_diet(Diet.HEARTY)
    play_month(run, Activity.PLAY, Activity.TRAIN, Activity.REST)

    assert run.stats.age == 2


def test_age_clamps_at_the_ceiling():
    run = GameRun(stats=CatStats(age=100))

    play_month(run, Activity.REST, Activity.REST, Activity.REST)

    assert run.stats.age == 100


def test_diet_effects_are_not_halved_while_the_slot_effects_are():
    run = GameRun(stats=CatStats(health=20, stress=40, weight=50))
    assert run.is_sick

    run.assign_diet(Diet.HEARTY)
    play_month(run, Activity.TRAIN, Activity.TRAIN, Activity.TRAIN)

    # TRAIN {"discipline": 5, "stress": 8}, halved for sickness except stress.
    assert run.stats.discipline == 10 + 2 + 2 + 2
    assert run.stats.stress == 40 + 8 + 8 + 8
    # HEARTY {"weight": 3, "health": 1} applies at full strength despite sickness.
    assert run.stats.weight == 50 + 3
    assert run.stats.health == 20 + 1


def test_run_rejects_an_impossible_month_or_slot_count():
    with pytest.raises(ValueError):
        GameRun(month=0)

    with pytest.raises(ValueError):
        GameRun(month=MONTHS_PER_RUN + 1)

    with pytest.raises(ValueError):
        GameRun(slots=[None, None])


def test_full_twelve_month_simulation():
    run = GameRun()
    plan = [
        [Activity.PLAY, Activity.GROOM, Activity.REST],
        [Activity.TRAIN, Activity.TRAIN, Activity.REST],
    ] * 6

    for month_plan in plan:
        run.assign_month(month_plan)
        run.advance_month()

    assert run.finished is True
    assert run.month == MONTHS_PER_RUN
    assert not run.is_sick
    assert run.stats.to_dict() == {
        "health": 56,
        "affection": 62,
        "discipline": 70,
        "curiosity": 48,
        "refinement": 0,
        "age": 13,
        "weight": 62,
        "stress": 0,
    }
