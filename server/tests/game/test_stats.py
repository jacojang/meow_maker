import pytest

from app.game import STAT_MAX, STAT_MIN, STAT_NAMES, CatStats


def test_default_stats_are_the_starting_values():
    stats = CatStats()

    assert stats.to_dict() == {
        "health": 50,
        "affection": 20,
        "discipline": 10,
        "curiosity": 30,
        "refinement": 10,
        "age": 1,
        "weight": 50,
        "stress": 0,
    }


def test_apply_adds_deltas():
    stats = CatStats().apply({"affection": 4, "curiosity": 3, "stress": 12})

    assert stats.affection == 24
    assert stats.curiosity == 33
    assert stats.stress == 12


def test_apply_leaves_the_original_untouched():
    original = CatStats()

    original.apply({"stress": 30})

    assert original.stress == 0


@pytest.mark.parametrize("name", STAT_NAMES)
def test_stats_clamp_at_the_floor(name):
    stats = CatStats().apply({name: -1000})

    assert getattr(stats, name) == STAT_MIN


@pytest.mark.parametrize("name", STAT_NAMES)
def test_stats_clamp_at_the_ceiling(name):
    stats = CatStats().apply({name: 1000})

    assert getattr(stats, name) == STAT_MAX


@pytest.mark.parametrize("name", STAT_NAMES)
def test_construction_clamps_out_of_range_values(name):
    assert getattr(CatStats(**{name: 400}), name) == STAT_MAX
    assert getattr(CatStats(**{name: -400}), name) == STAT_MIN


def test_repeated_deltas_never_escape_the_range():
    stats = CatStats()
    for _ in range(50):
        stats = stats.apply({name: 37 for name in STAT_NAMES})
    for name in STAT_NAMES:
        assert getattr(stats, name) == STAT_MAX

    for _ in range(50):
        stats = stats.apply({name: -37 for name in STAT_NAMES})
    for name in STAT_NAMES:
        assert getattr(stats, name) == STAT_MIN


def test_apply_rejects_unknown_stats():
    with pytest.raises(ValueError):
        CatStats().apply({"charisma": 5})


def test_is_sick_only_once_stress_exceeds_health():
    assert not CatStats(health=40, stress=39).is_sick
    assert not CatStats(health=40, stress=40).is_sick
    assert CatStats(health=40, stress=41).is_sick


def test_stats_round_trip_through_dict():
    stats = CatStats(
        health=61, affection=12, discipline=99, curiosity=3, refinement=7, stress=44
    )

    assert CatStats.from_dict(stats.to_dict()) == stats


def test_from_dict_rejects_missing_or_unknown_stats():
    complete = CatStats().to_dict()

    with pytest.raises(ValueError):
        CatStats.from_dict({k: v for k, v in complete.items() if k != "stress"})

    with pytest.raises(ValueError):
        CatStats.from_dict({**complete, "charisma": 1})
