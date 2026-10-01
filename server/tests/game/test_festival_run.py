import pytest

from app.game import (
    FESTIVAL_MONTH,
    FESTIVAL_RULES,
    SLOTS_PER_MONTH,
    Activity,
    CatStats,
    GameRun,
    InsufficientMoneyError,
    InvalidContestError,
    RunFinishedError,
    compute_score,
)
from app.game.care import Care
from app.game.endings import RunSummary
from app.rng import NeverRng

STRONG = CatStats(health=70, affection=100, discipline=90, curiosity=90, refinement=90)
FESTIVAL_RUN = dict(month=FESTIVAL_MONTH, stats=STRONG)


def enter(run, contest="charm", **kwargs):
    run.advance_month(rng=NeverRng(), contest=contest, **kwargs)


def test_entering_pays_the_prize_and_records_result_and_ribbon():
    run = GameRun(**FESTIVAL_RUN)

    enter(run)

    assert run.festival_result["contest"] == "charm"
    assert run.festival_result["rank"] == 1
    assert run.festival_result["prize"] == 300
    assert run.money == 200 + 300
    assert run.ribbons == [{"contest": "charm", "rank": 1}]


def test_entering_replaces_the_slots_and_charges_nothing_for_them():
    run = GameRun(month=FESTIVAL_MONTH, stats=STRONG, money=0)
    run.assign_month([Activity.REST] * SLOTS_PER_MONTH)

    enter(run, "obedience")

    assert run.last_month_log == []
    assert run.slots == [None] * SLOTS_PER_MONTH
    assert run.money == 300


def test_entering_needs_no_assigned_slots():
    run = GameRun(**FESTIVAL_RUN)

    enter(run)

    assert run.month == FESTIVAL_MONTH + 1


def test_entering_costs_the_entry_stress():
    run = GameRun(month=FESTIVAL_MONTH, stats=CatStats(affection=100, stress=10))

    enter(run)

    assert run.stats.stress == 10 + FESTIVAL_RULES.entry_stress


def test_a_poor_cat_enters_and_places_last_with_no_ribbon():
    run = GameRun(month=FESTIVAL_MONTH, stats=CatStats(affection=5))

    enter(run)

    assert run.festival_result["rank"] == 4
    assert run.festival_result["prize"] == 0
    assert run.ribbons == []
    assert run.money == 200


def test_the_contest_stat_decides_the_score():
    run = GameRun(month=FESTIVAL_MONTH, stats=CatStats(affection=100, curiosity=0))

    enter(run, "exploration")

    assert run.festival_result["stat"] == "curiosity"
    assert run.festival_result["rank"] == 4


def test_skipping_is_a_normal_month_with_no_result_and_no_stress_cost():
    run = GameRun(month=FESTIVAL_MONTH, stats=STRONG)
    run.assign_month([Activity.REST] * SLOTS_PER_MONTH)

    run.advance_month(rng=NeverRng())

    assert len(run.last_month_log) == SLOTS_PER_MONTH
    assert run.festival_result is None
    assert run.ribbons == []
    assert run.money == 200


def test_a_contest_outside_the_festival_month_is_rejected_without_changes():
    run = GameRun(month=FESTIVAL_MONTH - 1, stats=STRONG)
    before = run.to_dict()

    with pytest.raises(InvalidContestError):
        enter(run)

    assert run.to_dict() == before


def test_an_unknown_contest_is_rejected():
    run = GameRun(**FESTIVAL_RUN)

    with pytest.raises(InvalidContestError):
        enter(run, "nap")


def test_a_bedridden_cat_cannot_enter_and_rests_instead():
    run = GameRun(**FESTIVAL_RUN, sick_streak=2)
    assert run.is_bedridden

    enter(run)

    assert run.festival_result is None
    assert [entry["activity"] for entry in run.last_month_log] == ["rest"] * SLOTS_PER_MONTH
    assert run.bedridden_months == 1


def test_a_contest_in_a_finished_run_is_rejected():
    run = GameRun(**FESTIVAL_RUN, finished=True)

    with pytest.raises(RunFinishedError):
        enter(run)


def test_care_cost_is_still_checked_when_entering():
    run = GameRun(month=FESTIVAL_MONTH, stats=STRONG, money=0)

    with pytest.raises(InsufficientMoneyError):
        enter(run, care=Care.TREAT)


def test_result_and_ribbons_persist_through_the_rest_of_the_run():
    run = GameRun(**FESTIVAL_RUN)
    enter(run)
    result = run.festival_result

    while not run.finished:
        run.assign_month([Activity.REST] * SLOTS_PER_MONTH)
        run.advance_month(rng=NeverRng())

    assert run.festival_result == result
    assert run.ribbons == [{"contest": "charm", "rank": 1}]


def test_ribbons_add_to_the_score_by_rank_and_leftover_money_does_not():
    stats = CatStats(health=40, affection=40, discipline=40, curiosity=40, refinement=40)
    base = compute_score(RunSummary(stats=stats))

    scores = {rank: compute_score(RunSummary(stats=stats, ribbon_ranks=(rank,))) for rank in (1, 2, 3, 4)}

    assert scores == {1: base + 40, 2: base + 25, 3: base + 10, 4: base}
    assert compute_score(RunSummary(stats=stats)) == base


def test_ribbon_score_still_clamps_to_the_maximum():
    stats = CatStats(health=100, affection=100, discipline=100, curiosity=100, refinement=100)

    assert compute_score(RunSummary(stats=stats, ribbon_ranks=(1,))) == 1000


def test_game_run_summary_carries_the_ribbons():
    run = GameRun(ribbons=[{"contest": "charm", "rank": 2}])

    assert run.summary.ribbon_ranks == (2,)


def test_old_saves_without_the_new_fields_load_with_defaults():
    data = GameRun().to_dict()
    del data["festival_result"]
    del data["ribbons"]
    data["last_festival_winner"] = "affection"

    restored = GameRun.from_dict(data)

    assert restored.festival_result is None
    assert restored.ribbons == []
    assert "last_festival_winner" not in restored.to_dict()


def test_result_and_ribbons_round_trip():
    run = GameRun(**FESTIVAL_RUN)
    enter(run)

    restored = GameRun.from_dict(run.to_dict())

    assert restored.festival_result == run.festival_result
    assert restored.ribbons == run.ribbons
