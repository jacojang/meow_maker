from app.game import Activity, CatStats, GameRun
from app.game.warnings import DELINQUENT_MARGIN, SICK_MARGIN, compute_warnings


def test_fresh_cat_has_no_warnings():
    assert compute_warnings(CatStats()) == []


def test_near_sick_at_the_margin_boundary():
    at_margin = CatStats(health=50, stress=50 - SICK_MARGIN, discipline=100)
    above_margin = CatStats(health=50, stress=50 - SICK_MARGIN - 1, discipline=100)

    assert compute_warnings(at_margin) == ["near_sick"]
    assert compute_warnings(above_margin) == []


def test_sick_replaces_near_sick():
    assert compute_warnings(CatStats(health=10, stress=11, discipline=100)) == ["sick"]


def test_near_delinquent_at_the_margin_boundary():
    at_margin = CatStats(discipline=20, stress=20 - DELINQUENT_MARGIN)
    above_margin = CatStats(discipline=20, stress=20 - DELINQUENT_MARGIN - 1)

    assert compute_warnings(at_margin) == ["near_delinquent"]
    assert compute_warnings(above_margin) == []


def test_delinquent_replaces_near_delinquent():
    assert compute_warnings(CatStats(discipline=10, stress=11)) == ["delinquent"]


def test_overweight_warning():
    assert compute_warnings(CatStats(weight=81)) == ["overweight"]


def test_run_exposes_warnings():
    assert GameRun(stats=CatStats(weight=90)).warnings == ["overweight"]


class _Never:
    def random(self):
        return 0.99


def test_advance_month_clears_event_and_outing_but_keeps_festival_result():
    run = GameRun()
    run.last_event = "stale"
    run.festival_result = {"contest": "charm", "rank": 1}
    run.last_outing_result = "stale"
    run.assign_month([Activity.REST] * 3)

    run.advance_month(rng=_Never())

    assert run.last_event is None
    assert run.last_outing_result is None
    assert run.festival_result == {"contest": "charm", "rank": 1}
