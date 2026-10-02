"""S6b acceptance: entering the festival pays for prepared cats, not for last-place ones."""

from statistics import mean

import pytest

from app.game import GameRun
from simulation import (
    enter_festival,
    grinder,
    mixed,
    random_strategy,
    simulate,
    targeted,
    unlimited_money_run,
)

RUNS = 150


def paired(base, factory):
    skipped = simulate(base, RUNS, 0, factory)
    entered = simulate(enter_festival(base), RUNS, 0, factory)
    return list(zip(entered, skipped))


@pytest.fixture(scope="module")
def pooled():
    pairs = []
    for base, factory in [
        (grinder, unlimited_money_run),
        (random_strategy, unlimited_money_run),
        (targeted, unlimited_money_run),
        (mixed, GameRun),
    ]:
        pairs += paired(base, factory)
    return pairs


def test_a_prepared_cat_gains_more_by_entering_than_by_skipping():
    pairs = paired(grinder, unlimited_money_run)

    first_place = sum(entered.festival_rank == 1 for entered, _ in pairs) / len(pairs)
    assert first_place > 0.5
    assert mean(entered.score - skipped.score for entered, skipped in pairs) > 0


def test_first_place_beats_skipping_and_last_place_does_not(pooled):
    by_rank = {
        rank: [e.score - s.score for e, s in pooled if e.festival_rank == rank]
        for rank in (1, 4)
    }

    assert len(by_rank[4]) > 0
    assert mean(by_rank[1]) > 0
    assert mean(by_rank[4]) < 0


def test_prizes_pay_out_to_cats_that_enter(pooled):
    assert mean(e.final_money - s.final_money for e, s in pooled) > 0
