from app.game import CatStats, resolve_festival


def test_the_highest_festival_stat_wins():
    stats, winner = resolve_festival(
        CatStats(affection=50, discipline=10, curiosity=20, refinement=5)
    )

    assert winner == "affection"
    assert stats.affection == 55


def test_ties_break_toward_the_first_listed_stat():
    stats, winner = resolve_festival(
        CatStats(affection=50, discipline=50, curiosity=10, refinement=10)
    )

    assert winner == "affection"


def test_bonus_does_not_touch_other_stats():
    stats, winner = resolve_festival(
        CatStats(affection=10, discipline=90, curiosity=5, refinement=5)
    )

    assert winner == "discipline"
    assert stats.discipline == 95
    assert stats.affection == 10


def test_health_weight_age_and_stress_are_not_eligible_to_win():
    stats, winner = resolve_festival(
        CatStats(
            health=100,
            weight=100,
            age=100,
            stress=100,
            affection=5,
            discipline=1,
            curiosity=1,
            refinement=1,
        )
    )

    assert winner == "affection"
