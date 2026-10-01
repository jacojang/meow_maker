from app.game import SLOTS_PER_MONTH, Activity, Care, CatStats, Ending, GameRun, RunSummary
from app.game.endings import RULES, compute_score, determine_ending
from app.game.warnings import compute_warnings
from app.rng import NeverRng

LIMIT = RULES.runaway_streak
GROOM_MONTH = [Activity.GROOM] * SLOTS_PER_MONTH
REST_MONTH = [Activity.REST] * SLOTS_PER_MONTH
# Stress ends the month above discipline but below health: acting out, not ill.
ACTING_OUT = CatStats(health=90, discipline=10, stress=40)
CALM = CatStats(health=90, discipline=60, stress=0)
SICK = CatStats(health=20, discipline=10, stress=40)


def advance(run, slots=GROOM_MONTH, care=None):
    run.assign_month(slots)
    run.advance_month(rng=NeverRng(), care=care)


def test_new_run_has_no_streak():
    assert GameRun().delinquent_streak == 0


def test_streak_grows_each_month_the_cat_ends_delinquent_and_healthy():
    run = GameRun(stats=ACTING_OUT)

    advance(run)
    advance(run)

    assert run.delinquent_streak == 2


def test_streak_resets_when_the_cat_ends_the_month_calm():
    run = GameRun(stats=ACTING_OUT, delinquent_streak=3)

    advance(run, REST_MONTH)

    assert run.delinquent_streak == 0


def test_streak_resets_when_the_cat_ends_the_month_sick():
    run = GameRun(stats=SICK, delinquent_streak=3)

    advance(run)

    assert run.is_sick
    assert run.delinquent_streak == 0


def test_ran_away_at_the_streak_boundary():
    run = GameRun(stats=ACTING_OUT, delinquent_streak=LIMIT - 1, month=5)

    advance(run)

    assert run.delinquent_streak == LIMIT
    assert run.finished
    assert run.ending == Ending.RAN_AWAY
    assert run.month == 5


def test_not_ran_away_one_below_the_boundary():
    run = GameRun(stats=ACTING_OUT, delinquent_streak=LIMIT - 2, month=5)

    advance(run)

    assert run.delinquent_streak == LIMIT - 1
    assert not run.finished
    assert run.month == 6


def test_ran_away_score_is_capped_like_other_early_endings():
    summary = RunSummary(
        stats=CatStats(health=90, affection=90, discipline=90, curiosity=90, refinement=90),
        delinquent_streak=LIMIT,
    )

    assert compute_score(summary) == RULES.early_end_score_cap


def test_hospitalized_wins_when_both_trigger_together():
    summary = RunSummary(
        stats=ACTING_OUT, bedridden_months=RULES.hospital_limit, delinquent_streak=LIMIT
    )

    assert determine_ending(summary) == Ending.HOSPITALIZED


def test_runaway_risk_is_the_last_actionable_month():
    assert GameRun(stats=ACTING_OUT, delinquent_streak=LIMIT - 1).warnings.count("runaway_risk") == 1
    assert "runaway_risk" not in GameRun(stats=ACTING_OUT, delinquent_streak=LIMIT - 2).warnings


def test_runaway_risk_needs_a_delinquent_healthy_cat():
    assert "runaway_risk" not in GameRun(stats=CALM, delinquent_streak=LIMIT - 1).warnings
    assert "runaway_risk" not in GameRun(stats=SICK, delinquent_streak=LIMIT - 1).warnings


def test_runaway_risk_code_is_exposed_by_compute_warnings():
    assert compute_warnings(ACTING_OUT, runaway_risk=True)[-1] == "runaway_risk"


def test_finished_run_has_no_runaway_risk():
    run = GameRun(stats=ACTING_OUT, delinquent_streak=LIMIT - 1)
    advance(run)

    assert "runaway_risk" not in run.warnings


def test_scolding_in_the_risk_month_avoids_the_ending():
    run = GameRun(stats=ACTING_OUT, delinquent_streak=LIMIT - 1)

    advance(run, REST_MONTH, care=Care.SCOLD)

    assert not run.finished
    assert run.delinquent_streak == 0


def test_streak_round_trips_and_old_saves_default_to_zero():
    run = GameRun(delinquent_streak=4)
    assert GameRun.from_dict(run.to_dict()).delinquent_streak == 4

    data = run.to_dict()
    del data["delinquent_streak"]
    assert GameRun.from_dict(data).delinquent_streak == 0
