def test_advance_returns_the_per_day_log(client):
    client.post("/api/game")

    body = client.post(
        "/api/game/advance",
        json={"activities": ["train", "rest", "outing"], "diet": "normal"},
    ).json()

    log = body["last_month_log"]
    assert [entry["activity"] for entry in log] == ["train", "rest", "outing"]
    assert sum(len(entry["days"]) for entry in log) == 31
    assert set(log[0]["days"][0]) == {"day", "outcome", "deltas"}


def test_log_survives_a_reload(client):
    client.post("/api/game")
    advanced = client.post(
        "/api/game/advance", json={"activities": ["play", "play", "play"]}
    ).json()

    assert client.get("/api/game").json()["last_month_log"] == advanced["last_month_log"]
