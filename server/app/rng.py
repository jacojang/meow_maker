from __future__ import annotations

import random


def get_rng() -> random.Random:
    return random.Random()


class NeverRng(random.Random):
    """A random.Random whose .random() always returns 1.0.

    Used by tests that don't care about random events/festivals and want
    advance_month() to behave deterministically regardless of chance-based
    rolls, without hand-writing a fake for every call site.
    """

    def random(self) -> float:
        return 1.0
