from app.game import CatStats, apply_overweight_penalty


def test_no_penalty_at_or_below_the_threshold():
    stats = apply_overweight_penalty(CatStats(weight=80, affection=20))

    assert stats.affection == 20


def test_penalty_applies_once_over_the_threshold():
    stats = apply_overweight_penalty(CatStats(weight=81, affection=20))

    assert stats.affection == 18


def test_penalty_does_not_touch_weight_itself():
    stats = apply_overweight_penalty(CatStats(weight=81))

    assert stats.weight == 81
