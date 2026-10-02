import json
from pathlib import Path

import pytest

from app.game import Activity
from app.game.economy import (
    ECONOMY,
    START_MONEY,
    Economy,
    cost_of,
    income_per_day,
    total_cost,
    with_perfect_bonus,
)


def _raw():
    path = Path(__file__).resolve().parents[2] / "app/game/data/economy.json"
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def test_shipped_table_covers_every_activity():
    assert set(ECONOMY.activities) == set(Activity)


def test_the_job_is_the_only_earner_and_free_options_cost_nothing():
    for activity in (Activity.PLAY, Activity.GROOM, Activity.REST, Activity.JOB):
        assert cost_of(activity) == 0
    assert [a for a in Activity if income_per_day(a, sick=False) > 0] == [Activity.JOB]


def test_start_money_comes_from_the_data_file():
    assert START_MONEY == ECONOMY.start_money


def test_total_cost_sums_slots():
    assert total_cost([Activity.TRAIN, Activity.TRAIN, Activity.REST]) == 2 * cost_of(
        Activity.TRAIN
    )


def test_sick_income_is_halved_rounding_down():
    assert income_per_day(Activity.JOB, sick=True) == income_per_day(Activity.JOB, sick=False) // 2


def test_perfect_bonus_adds_the_configured_percent_rounding_down():
    assert with_perfect_bonus(80) == 120
    assert with_perfect_bonus(5) == 7


def test_a_missing_activity_is_rejected():
    raw = _raw()
    del raw["activities"]["job"]

    with pytest.raises(ValueError, match="missing=\\['job'\\]"):
        Economy.from_raw(raw)


def test_an_unknown_activity_is_rejected():
    raw = _raw()
    raw["activities"]["shop"] = {"cost": 1, "income_per_day": 0}

    with pytest.raises(ValueError, match="unknown=\\['shop'\\]"):
        Economy.from_raw(raw)


def test_an_unknown_entry_key_is_rejected():
    raw = _raw()
    raw["activities"]["train"]["tip"] = 3

    with pytest.raises(ValueError, match="'train' keys"):
        Economy.from_raw(raw)


def test_a_missing_entry_key_is_rejected():
    raw = _raw()
    del raw["activities"]["train"]["cost"]

    with pytest.raises(ValueError, match="'train' keys"):
        Economy.from_raw(raw)


def test_a_missing_or_unknown_top_level_key_is_rejected():
    raw = _raw()
    del raw["start_money"]
    with pytest.raises(ValueError, match="missing=\\['start_money'\\]"):
        Economy.from_raw(raw)

    raw = _raw()
    raw["stipend"] = 5
    with pytest.raises(ValueError, match="unknown=\\['stipend'\\]"):
        Economy.from_raw(raw)


@pytest.mark.parametrize("bad", [-1, 1.5, "3", True])
def test_values_must_be_non_negative_integers(bad):
    raw = _raw()
    raw["activities"]["train"]["cost"] = bad

    with pytest.raises(ValueError, match="non-negative integers"):
        Economy.from_raw(raw)
