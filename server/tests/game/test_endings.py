import pytest

from app.game import CatStats, Ending, compute_score, determine_ending

DEFAULT = {
    "health": 50,
    "affection": 20,
    "discipline": 10,
    "curiosity": 30,
    "refinement": 10,
    "stress": 0,
}


def stats(**overrides):
    return CatStats(**{**DEFAULT, **overrides})


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        (stats(health=90, stress=95), Ending.NEGLECTED),
        (stats(discipline=5, stress=10), Ending.DELINQUENT),
        (stats(health=90, affection=10, discipline=10, curiosity=10, refinement=10), Ending.HEALTHY),
        (stats(health=10, affection=90, discipline=10, curiosity=10, refinement=10), Ending.BELOVED),
        (stats(health=10, affection=10, discipline=90, curiosity=10, refinement=10), Ending.DISCIPLINED),
        (stats(health=10, affection=10, discipline=10, curiosity=90, refinement=10), Ending.CURIOUS),
        (stats(health=10, affection=10, discipline=10, curiosity=10, refinement=90), Ending.REFINED),
    ],
)
def test_determine_ending_table(given, expected):
    assert determine_ending(given) is expected


def test_neglected_takes_priority_over_delinquent():
    # Both is_sick (stress > health) and is_delinquent (stress > discipline)
    # are true here; neglected must win.
    given = stats(health=10, discipline=10, stress=50)
    assert given.is_sick
    assert given.is_delinquent

    assert determine_ending(given) is Ending.NEGLECTED


def test_ties_break_toward_the_first_listed_stat():
    given = stats(health=50, affection=50, discipline=10, curiosity=10, refinement=10)

    assert determine_ending(given) is Ending.HEALTHY


def test_score_at_the_minimum():
    assert compute_score(stats(health=0, affection=0, discipline=0, curiosity=0, refinement=0)) == 0


def test_score_at_the_maximum():
    assert (
        compute_score(
            stats(health=100, affection=100, discipline=100, curiosity=100, refinement=100)
        )
        == 1000
    )


def test_score_is_the_doubled_sum_of_the_five_core_stats():
    given = stats(health=50, affection=20, discipline=10, curiosity=30, refinement=10)

    assert compute_score(given) == (50 + 20 + 10 + 30 + 10) * 2


def test_score_ignores_weight_age_and_stress():
    base = stats()
    heavier = CatStats(**{**base.to_dict(), "weight": 90, "age": 50, "stress": 40})

    assert compute_score(heavier) == compute_score(base)
