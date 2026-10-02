from test_api import advance, start_run

REST = ["rest", "rest", "rest"]


def advance_with_care(client, care, activities=REST):
    return client.post("/api/game/advance", json={"activities": activities, "care": care})


def test_care_endpoint_lists_actions_with_cost_and_rule(client):
    entries = {e["id"]: e for e in client.get("/api/care").json()["care"]}

    assert set(entries) == {"pet", "treat", "scold"}
    assert entries["pet"]["cost"] == 0
    assert entries["treat"]["cost"] == 20
    assert entries["treat"]["works_when"] == "healthy"
    assert entries["scold"]["effects"] == {"stress": -15, "discipline": 2}


def test_advance_without_care_still_works_and_reports_no_care(client):
    start_run(client)

    state = advance(client).json()

    assert state["last_care"] is None


def test_advance_with_treat_charges_money_and_reports_the_result(client):
    start_run(client)

    state = advance_with_care(client, "treat").json()

    assert state["money"] == 180
    assert state["last_care"]["action"] == "treat"
    assert state["last_care"]["worked"] is True


def test_pet_is_free(client):
    start_run(client)

    state = advance_with_care(client, "pet").json()

    assert state["money"] == 200
    assert state["last_care"] == {"action": "pet", "worked": True, "cost": 0, "effects": {"stress": -8}}


def test_unknown_care_is_a_400(client):
    start_run(client)

    assert advance_with_care(client, "hug").status_code == 400


def test_unaffordable_treat_is_a_400_and_state_is_unchanged(client):
    start_run(client)
    for _ in range(3):
        client.post("/api/game/advance", json={"activities": ["educate", "educate", "rest"]})
    before = client.get("/api/game").json()

    response = advance_with_care(client, "treat", ["educate", "educate", "educate"])

    assert response.status_code == 400
    assert client.get("/api/game").json() == before


def test_state_exposes_streak_and_runaway_risk(client):
    state = start_run(client)

    assert state["delinquent_streak"] == 0
    assert "runaway_risk" not in state["warnings"]
