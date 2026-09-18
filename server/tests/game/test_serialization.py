import json

import pytest

from app.game import (
    MONTHS_PER_RUN,
    SLOTS_PER_MONTH,
    Activity,
    CatStats,
    Diet,
    Ending,
    Event,
    GameRun,
)
from app.rng import NeverRng


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
            "age": 1,
            "weight": 50,
            "stress": 40,
        },
        "month": 4,
        "finished": False,
        "slots": [None, "train", None],
        "diet": "normal",
        "last_event": None,
        "last_festival_winner": None,
        "ending": None,
        "score": None,
        "last_outing_result": None,
    }
    assert json.loads(json.dumps(data)) == data


def test_round_trip_preserves_a_non_default_diet():
    run = GameRun()
    run.assign_diet(Diet.HEARTY)

    restored = GameRun.from_dict(json.loads(json.dumps(run.to_dict())))

    assert restored.diet == Diet.HEARTY
    assert restored == run


def test_round_trip_preserves_a_run_in_progress():
    run = GameRun()
    run.assign_month([Activity.PLAY, Activity.TRAIN, Activity.REST])
    run.advance_month(rng=NeverRng())
    run.assign_slot(0, Activity.GROOM)

    restored = GameRun.from_dict(json.loads(json.dumps(run.to_dict())))

    assert restored == run
    assert restored.to_dict() == run.to_dict()


def test_round_trip_preserves_a_finished_run():
    run = GameRun(month=MONTHS_PER_RUN)
    run.assign_month([Activity.REST] * SLOTS_PER_MONTH)
    run.advance_month(rng=NeverRng())

    restored = GameRun.from_dict(run.to_dict())

    assert restored.finished is True
    assert restored.ending is not None
    assert restored.score is not None
    assert restored == run


def test_restored_run_keeps_playing_from_where_it_stopped():
    run = GameRun()
    run.assign_month([Activity.TRAIN] * SLOTS_PER_MONTH)
    run.advance_month(rng=NeverRng())

    restored = GameRun.from_dict(run.to_dict())
    restored.assign_month([Activity.REST] * SLOTS_PER_MONTH)
    restored.advance_month(rng=NeverRng())

    assert restored.month == 3
    assert restored.stats.discipline == 25
    assert restored.stats.stress == 0


def test_round_trip_preserves_a_recorded_event():
    run = GameRun()
    run.last_event = Event.GIFT

    restored = GameRun.from_dict(json.loads(json.dumps(run.to_dict())))

    assert restored.last_event is Event.GIFT


def test_from_dict_defaults_last_event_and_festival_winner_when_absent():
    data = GameRun().to_dict()
    del data["last_event"]
    del data["last_festival_winner"]

    restored = GameRun.from_dict(data)

    assert restored.last_event is None
    assert restored.last_festival_winner is None


def test_round_trip_preserves_an_ending_and_score():
    run = GameRun()
    run.ending = Ending.BELOVED
    run.score = 742

    restored = GameRun.from_dict(json.loads(json.dumps(run.to_dict())))

    assert restored.ending is Ending.BELOVED
    assert restored.score == 742


def test_from_dict_defaults_ending_and_score_when_absent():
    data = GameRun().to_dict()
    del data["ending"]
    del data["score"]

    restored = GameRun.from_dict(data)

    assert restored.ending is None
    assert restored.score is None


def test_round_trip_preserves_a_recorded_outing_result():
    run = GameRun()
    run.last_outing_result = "success"

    restored = GameRun.from_dict(json.loads(json.dumps(run.to_dict())))

    assert restored.last_outing_result == "success"


def test_from_dict_defaults_outing_result_when_absent():
    data = GameRun().to_dict()
    del data["last_outing_result"]

    restored = GameRun.from_dict(data)

    assert restored.last_outing_result is None


def test_from_dict_rejects_incomplete_data():
    complete = GameRun().to_dict()

    with pytest.raises(ValueError):
        GameRun.from_dict({k: v for k, v in complete.items() if k != "month"})


def test_from_dict_rejects_an_unknown_activity():
    data = GameRun().to_dict()
    data["slots"] = ["nap", None, None]

    with pytest.raises(ValueError):
        GameRun.from_dict(data)
