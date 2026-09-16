from app.game import DIET_EFFECTS, CatStats, Diet
from app.game.diet import apply_diet


def test_every_diet_has_an_effect_entry():
    assert set(DIET_EFFECTS) == set(Diet)


def test_normal_diet_raises_weight_only():
    stats = apply_diet(CatStats(), Diet.NORMAL)

    assert stats.weight == 51
    assert stats.health == 50


def test_light_diet_lowers_weight():
    stats = apply_diet(CatStats(), Diet.LIGHT)

    assert stats.weight == 49


def test_hearty_diet_raises_weight_and_health():
    stats = apply_diet(CatStats(), Diet.HEARTY)

    assert stats.weight == 53
    assert stats.health == 51
