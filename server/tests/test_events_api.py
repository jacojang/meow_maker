from app.game import EVENT_EFFECTS, Event


def test_list_events_returns_the_event_table(client):
    response = client.get("/api/events")

    assert response.status_code == 200
    events = response.json()["events"]
    assert [entry["id"] for entry in events] == [event.value for event in Event]
    assert all(
        entry["effects"] == dict(EVENT_EFFECTS[Event(entry["id"])]) for entry in events
    )


def test_state_includes_warnings(client):
    client.post("/api/game")

    state = client.get("/api/game").json()

    assert state["warnings"] == []
