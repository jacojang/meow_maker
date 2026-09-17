import random

from app.game import EVENT_CHANCE, CatStats, Event, apply_event, roll_event


class FakeRng:
    def __init__(self, random_value, choice_value=None):
        self._random_value = random_value
        self._choice_value = choice_value

    def random(self):
        return self._random_value

    def choice(self, seq):
        return self._choice_value


def test_no_event_when_the_roll_is_at_or_above_the_chance():
    assert roll_event(FakeRng(random_value=EVENT_CHANCE)) is None
    assert roll_event(FakeRng(random_value=1.0)) is None


def test_an_event_is_chosen_from_the_pool_when_the_roll_is_below_the_chance():
    rng = FakeRng(random_value=0.0, choice_value=Event.GIFT)

    assert roll_event(rng) is Event.GIFT


def test_apply_event_with_none_is_a_noop():
    stats = CatStats()

    assert apply_event(stats, None) == stats


def test_apply_event_applies_the_matching_effects():
    stats = apply_event(CatStats(), Event.VISITOR)

    assert stats.affection == 20 + 3


def test_a_fixed_seed_always_rolls_the_same_event():
    first = roll_event(random.Random(7))
    second = roll_event(random.Random(7))

    assert first == second
