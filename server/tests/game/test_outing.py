from app.game import CatStats, OUTING_SUCCESS_CHANCE, apply_outing_result, resolve_outing


class FakeRng:
    def __init__(self, random_value):
        self._random_value = random_value

    def random(self):
        return self._random_value


def test_succeeds_when_the_roll_is_below_the_chance():
    assert resolve_outing(FakeRng(random_value=0.0)) is True


def test_fails_when_the_roll_is_at_or_above_the_chance():
    assert resolve_outing(FakeRng(random_value=OUTING_SUCCESS_CHANCE)) is False
    assert resolve_outing(FakeRng(random_value=1.0)) is False


def test_success_applies_the_bonus():
    stats = apply_outing_result(CatStats(curiosity=30, discipline=10), True)

    assert stats.curiosity == 35
    assert stats.discipline == 15


def test_failure_applies_the_penalty():
    stats = apply_outing_result(CatStats(stress=0), False)

    assert stats.stress == 5


def test_failure_does_not_touch_curiosity_or_discipline():
    stats = apply_outing_result(CatStats(curiosity=30, discipline=10), False)

    assert stats.curiosity == 30
    assert stats.discipline == 10
