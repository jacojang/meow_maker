import random

from fastapi.testclient import TestClient

from app.game import (
    ACTIVITY_EFFECTS,
    DIET_EFFECTS,
    MONTHS_PER_RUN,
    SLOTS_PER_MONTH,
    Activity,
    CatStats,
    Diet,
    Event,
    apply_activity,
    apply_delinquent_penalty,
    apply_overweight_penalty,
)
from app.rng import get_rng
from app.session import SESSION_COOKIE_NAME

A_MONTH = ["play", "train", "groom"]


def start_run(client):
    response = client.post("/api/game")
    assert response.status_code == 200
    return response.json()


def advance(client, activities=A_MONTH, diet=None):
    body: dict[str, object] = {"activities": activities}
    if diet is not None:
        body["diet"] = diet
    return client.post("/api/game/advance", json=body)


def test_start_game_returns_a_fresh_run(client):
    state = start_run(client)

    assert state["month"] == 1
    assert state["finished"] is False
    assert state["is_sick"] is False
    assert state["last_event"] is None
    assert state["last_festival_winner"] is None
    assert state["slots"] == [None] * SLOTS_PER_MONTH
    assert state["stats"] == CatStats().to_dict()
    assert state["months_per_run"] == MONTHS_PER_RUN
    assert state["slots_per_month"] == SLOTS_PER_MONTH


def test_start_game_sets_a_session_cookie(client):
    response = client.post("/api/game")

    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Secure" not in cookie


def test_read_game_returns_the_started_run(client):
    started = start_run(client)

    response = client.get("/api/game")

    assert response.status_code == 200
    assert response.json() == started


def test_read_game_without_a_run_returns_404(client):
    response = client.get("/api/game")

    assert response.status_code == 404


def test_read_game_without_a_run_still_sets_a_session_cookie(client):
    response = client.get("/api/game")

    assert response.status_code == 404
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Secure" not in cookie


def test_a_cookieless_read_keeps_the_session_it_was_given(client):
    assert client.get("/api/game").status_code == 404
    issued = client.cookies[SESSION_COOKIE_NAME]

    started = start_run(client)
    assert client.cookies[SESSION_COOKIE_NAME] == issued

    response = client.get("/api/game")

    assert response.status_code == 200
    assert response.json() == started
    assert client.cookies[SESSION_COOKIE_NAME] == issued


def test_start_game_replaces_an_existing_run(client):
    start_run(client)
    advance(client)

    restarted = start_run(client)

    assert restarted["month"] == 1
    assert restarted["stats"] == CatStats().to_dict()
    assert client.get("/api/game").json()["month"] == 1


def test_advance_applies_every_activity_and_moves_to_the_next_month(client):
    start_run(client)

    response = advance(client)

    assert response.status_code == 200
    state = response.json()
    expected = CatStats()
    for name in A_MONTH:
        expected = apply_activity(expected, Activity(name))
    expected = expected.apply(dict(DIET_EFFECTS[Diet.NORMAL]))
    expected = apply_overweight_penalty(expected)
    expected = apply_delinquent_penalty(expected)
    expected = expected.apply({"age": 1})
    assert state["stats"] == expected.to_dict()
    assert state["month"] == 2
    assert state["slots"] == [None] * SLOTS_PER_MONTH
    assert state["finished"] is False


def test_advance_persists_the_new_state(client):
    start_run(client)

    advanced = advance(client).json()

    assert client.get("/api/game").json() == advanced


def test_advance_without_a_run_returns_404(client):
    response = advance(client)

    assert response.status_code == 404


def test_playing_every_month_finishes_the_run(client):
    start_run(client)

    for month in range(1, MONTHS_PER_RUN + 1):
        state = advance(client, ["rest", "rest", "rest"]).json()
        assert state["month"] == min(month + 1, MONTHS_PER_RUN)

    assert state["finished"] is True
    assert state["ending"] is not None
    assert state["score"] is not None

    rejected = advance(client, ["rest", "rest", "rest"])
    assert rejected.status_code == 409


def test_advance_rejects_the_wrong_number_of_activities(client):
    start_run(client)

    assert advance(client, ["play", "rest"]).status_code == 400
    assert advance(client, ["play", "rest", "rest", "rest"]).status_code == 400


def test_advance_rejects_an_unknown_activity(client):
    start_run(client)

    response = advance(client, ["play", "nap", "rest"])

    assert response.status_code == 400


def test_advance_rejects_a_malformed_body(client):
    start_run(client)

    response = client.post("/api/game/advance", json={})

    assert response.status_code == 422


def test_sessions_get_independent_runs(client, other_client):
    start_run(client)
    start_run(other_client)
    advance(client)

    mine = client.get("/api/game").json()
    theirs = other_client.get("/api/game").json()

    assert (
        client.cookies[SESSION_COOKIE_NAME]
        != other_client.cookies[SESSION_COOKIE_NAME]
    )
    assert mine["month"] == 2
    assert theirs["month"] == 1
    assert theirs["stats"] == CatStats().to_dict()


def test_a_session_without_a_run_does_not_see_another_players_run(client, other_client):
    start_run(client)

    assert other_client.get("/api/game").status_code == 404


def test_list_activities_returns_the_activity_table(client):
    response = client.get("/api/activities")

    assert response.status_code == 200
    activities = response.json()["activities"]
    assert [entry["id"] for entry in activities] == [
        activity.value for activity in Activity
    ]
    assert all(
        entry["effects"] == dict(ACTIVITY_EFFECTS[Activity(entry["id"])])
        for entry in activities
    )


def test_list_diets_returns_the_diet_table(client):
    response = client.get("/api/diets")

    assert response.status_code == 200
    diets = response.json()["diets"]
    assert [entry["id"] for entry in diets] == [diet.value for diet in Diet]
    assert all(
        entry["effects"] == dict(DIET_EFFECTS[Diet(entry["id"])]) for entry in diets
    )


def test_advance_without_a_diet_field_defaults_to_normal(client):
    start_run(client)

    state = advance(client).json()

    assert state["diet"] == "normal"
    assert state["stats"]["weight"] == 51


def test_advance_accepts_an_explicit_diet_field(client):
    start_run(client)

    state = advance(client, diet="hearty").json()

    assert state["diet"] == "hearty"
    assert state["stats"]["weight"] == 53
    assert state["stats"]["health"] == 52


def test_advance_rejects_an_unknown_diet(client):
    start_run(client)

    response = advance(client, diet="junk-food")

    assert response.status_code == 400


def test_state_reports_overweight_once_hearty_diet_pushes_past_the_threshold(client):
    start_run(client)

    for _ in range(11):
        state = advance(client, diet="hearty").json()

    assert state["stats"]["weight"] > 80
    assert state["is_overweight"] is True


def test_state_reports_delinquent_once_stress_exceeds_discipline(client):
    start_run(client)

    state = advance(client, activities=["play", "play", "play"]).json()

    assert state["stats"]["stress"] > state["stats"]["discipline"]
    assert state["is_delinquent"] is True


def test_state_reports_an_event_when_the_rng_forces_one(api_app):
    class _AlwaysGift(random.Random):
        def random(self):
            return 0.0

        def choice(self, seq):
            return Event.GIFT

    api_app.dependency_overrides[get_rng] = lambda: _AlwaysGift()
    with TestClient(api_app) as client:
        start_run(client)
        state = advance(client).json()

    assert state["last_event"] == "gift"


def test_state_reports_a_successful_outing_when_the_rng_forces_one(api_app):
    class _AlwaysSucceed(random.Random):
        def random(self):
            return 0.0

    api_app.dependency_overrides[get_rng] = lambda: _AlwaysSucceed()
    with TestClient(api_app) as client:
        start_run(client)
        state = advance(client, activities=["outing", "rest", "rest"]).json()

    assert state["last_outing_result"] == "success"
