from app.game import CatStats, apply_delinquent_penalty


def test_no_penalty_while_stress_is_at_or_below_discipline():
    stats = apply_delinquent_penalty(CatStats(discipline=10, stress=10))

    assert stats.discipline == 10


def test_penalty_applies_once_stress_exceeds_discipline():
    stats = apply_delinquent_penalty(CatStats(discipline=10, stress=11))

    assert stats.discipline == 9


def test_penalty_does_not_touch_stress_itself():
    stats = apply_delinquent_penalty(CatStats(discipline=10, stress=11))

    assert stats.stress == 11
