from test_api import advance, start_run

PLAY = ["play", "play", "play"]


def advance_until_bedridden(client):
    state = start_run(client)
    for _ in range(11):
        if state["is_bedridden"]:
            return state
        state = advance(client, PLAY).json()
    raise AssertionError("never became bedridden")


def test_fresh_state_is_not_bedridden(client):
    state = start_run(client)

    assert state["is_bedridden"] is False
    assert state["forced_slots"] is None
    assert state["sick_months_total"] == 0


def test_bedridden_state_exposes_forced_rest_and_warning(client):
    state = advance_until_bedridden(client)

    assert state["forced_slots"] == ["rest", "rest", "rest"]
    assert "bedridden" in state["warnings"]


def test_server_forces_rest_even_if_client_sends_other_activities(client):
    state = advance_until_bedridden(client)
    before = state["bedridden_months"]

    after = advance(client, PLAY).json()

    assert after["bedridden_months"] == before + 1
    assert after["stats"]["stress"] < state["stats"]["stress"]
