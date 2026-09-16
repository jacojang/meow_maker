import json

import pytest

from app.game import (
    MONTHS_PER_RUN,
    SLOTS_PER_MONTH,
    Activity,
    CatStats,
    GameRun,
)


def test_to_dict_is_plain_json_safe_data():
    run = GameRun(stats=CatStats(health=33, stress=40), month=4)
    run.assign_slot(1, Activity.TRAIN)

    data = run.to_dict()

    assert data == {
        "stats": {
            "health": 33,
            "affection": 20,
            "discipline": 10,
            "curiosity": 30,
            "refinement": 10,
            "stress": 40,
        },
        "month": 4,
        "finished": False,
        "slots": [None, "train", None],
    }
    assert json.loads(json.dumps(data)) == data


def test_round_trip_preserves_a_run_in_progress():
    run = GameRun()
    run.assign_month([Activity.PLAY, Activity.TRAIN, Activity.REST])
    run.advance_month()
    run.assign_slot(0, Activity.GROOM)

    restored = GameRun.from_dict(json.loads(json.dumps(run.to_dict())))

    assert restored == run
    assert restored.to_dict() == run.to_dict()


def test_round_trip_preserves_a_finished_run():
    run = GameRun(month=MONTHS_PER_RUN)
    run.assign_month([Activity.REST] * SLOTS_PER_MONTH)
    run.advance_month()

    restored = GameRun.from_dict(run.to_dict())

    assert restored.finished is True
    assert restored == run


def test_restored_run_keeps_playing_from_where_it_stopped():
    run = GameRun()
    run.assign_month([Activity.TRAIN] * SLOTS_PER_MONTH)
    run.advance_month()

    restored = GameRun.from_dict(run.to_dict())
    restored.assign_month([Activity.REST] * SLOTS_PER_MONTH)
    restored.advance_month()

    assert restored.month == 3
    assert restored.stats.discipline == 25
    assert restored.stats.stress == 0


def test_from_dict_rejects_incomplete_data():
    complete = GameRun().to_dict()

    with pytest.raises(ValueError):
        GameRun.from_dict({k: v for k, v in complete.items() if k != "month"})


def test_from_dict_rejects_an_unknown_activity():
    data = GameRun().to_dict()
    data["slots"] = ["nap", None, None]

    with pytest.raises(ValueError):
        GameRun.from_dict(data)
