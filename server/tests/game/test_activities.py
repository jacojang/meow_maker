import pytest

from app.game import ACTIVITY_EFFECTS, Activity, CatStats, apply_activity, effects_for


def test_every_activity_has_an_effect_entry():
    assert set(ACTIVITY_EFFECTS) == set(Activity)


def test_play_raises_affection_curiosity_and_stress():
    stats = apply_activity(CatStats(), Activity.PLAY)

    assert stats.affection == 24
    assert stats.curiosity == 33
    assert stats.stress == 12
    assert stats.health == 50
    assert stats.discipline == 10


def test_train_raises_discipline_and_stress():
    stats = apply_activity(CatStats(), Activity.TRAIN)

    assert stats.discipline == 15
    assert stats.stress == 8
    assert stats.affection == 20
    assert stats.curiosity == 30
    assert stats.health == 50


def test_groom_raises_affection_and_health_for_little_stress():
    stats = apply_activity(CatStats(), Activity.GROOM)

    assert stats.affection == 23
    assert stats.health == 51
    assert stats.stress == 3
    assert stats.discipline == 10
    assert stats.curiosity == 30


def test_rest_only_lowers_stress():
    before = CatStats(stress=30)

    stats = apply_activity(before, Activity.REST)

    assert stats.stress == 10
    assert stats.health == before.health
    assert stats.affection == before.affection
    assert stats.discipline == before.discipline
    assert stats.curiosity == before.curiosity


def test_rest_cannot_push_stress_below_zero():
    stats = apply_activity(CatStats(stress=5), Activity.REST)

    assert stats.stress == 0


@pytest.mark.parametrize("activity", list(Activity))
def test_sickness_halves_stat_gains_but_not_stress(activity):
    healthy = effects_for(activity, sick=False)
    sick = effects_for(activity, sick=True)

    assert set(sick) == set(healthy)
    for name, value in healthy.items():
        if name == "stress":
            assert sick[name] == value
        else:
            assert sick[name] == value // 2


def test_sick_cat_gains_half_as_much_rounded_down():
    sick = CatStats(health=20, stress=40)
    assert sick.is_sick

    after = apply_activity(sick, Activity.PLAY)

    assert after.affection == 22
    assert after.curiosity == 31
    assert after.stress == 52
