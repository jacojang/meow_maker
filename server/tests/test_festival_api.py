from test_api import advance, start_run

from app.game import FESTIVAL_MONTH

REST = ["rest", "rest", "rest"]


def reach_festival_month(client):
    state = start_run(client)
    while state["month"] < FESTIVAL_MONTH:
        state = advance(client, REST).json()
    return state


def test_festival_endpoint_lists_contests_rivals_prizes_and_ribbons(client):
    data = client.get("/api/festival").json()

    assert data["month"] == FESTIVAL_MONTH
    assert [contest["id"] for contest in data["contests"]] == [
        "charm",
        "obedience",
        "exploration",
        "grace",
    ]
    assert all(len(contest["rivals"]) == 3 for contest in data["contests"])
    assert data["prizes"] == {"1": 300, "2": 150, "3": 50, "4": 0}
    assert data["ribbon_scores"] == {"1": 75, "2": 60, "3": 50, "4": 0}


def test_contest_outside_the_festival_month_is_a_400(client):
    start_run(client)

    response = client.post("/api/game/advance", json={"contest": "charm"})

    assert response.status_code == 400


def test_unknown_contest_is_a_400(client):
    start_run(client)

    response = client.post("/api/game/advance", json={"contest": "nap"})

    assert response.status_code == 400


def test_a_missing_schedule_without_a_contest_is_still_rejected(client):
    start_run(client)

    assert client.post("/api/game/advance", json={}).status_code == 422


def test_entering_via_the_api_needs_no_activities_and_reports_the_result(client):
    reach_festival_month(client)

    response = client.post("/api/game/advance", json={"contest": "charm"})

    assert response.status_code == 200
    state = response.json()
    result = state["festival_result"]
    assert result["contest"] == "charm"
    assert 1 <= result["rank"] <= 4
    assert len(result["rivals"]) == 3
    assert state["last_month_log"] == []
    assert state["month"] == FESTIVAL_MONTH + 1


def test_skipping_via_the_api_is_a_normal_month(client):
    reach_festival_month(client)

    state = advance(client, REST).json()

    assert state["festival_result"] is None
    assert len(state["last_month_log"]) == 3
