from app.game import START_MONEY, cost_of, Activity


def test_state_reports_the_starting_money(client):
    assert client.post("/api/game").json()["money"] == START_MONEY


def test_activities_list_includes_cost_income_and_the_job(client):
    entries = {e["id"]: e for e in client.get("/api/activities").json()["activities"]}

    assert entries["job"]["income_per_day"] > 0
    assert entries["job"]["effects"] == {"curiosity": 2, "refinement": -2, "stress": 8}
    assert entries["educate"]["cost"] == cost_of(Activity.EDUCATE)
    assert entries["rest"]["cost"] == 0


def test_an_unaffordable_schedule_is_rejected_with_400_and_state_is_unchanged(client):
    client.post("/api/game")
    for _ in range(3):
        client.post("/api/game/advance", json={"activities": ["educate", "educate", "rest"]})

    before = client.get("/api/game").json()
    response = client.post(
        "/api/game/advance", json={"activities": ["educate", "educate", "educate"]}
    )

    assert response.status_code == 400
    assert client.get("/api/game").json() == before


def test_money_is_charged_and_earned_through_the_api(client):
    client.post("/api/game")

    body = client.post(
        "/api/game/advance", json={"activities": ["train", "job", "rest"]}
    ).json()

    income = sum(e["income"] for e in body["last_month_log"])
    assert body["money"] == START_MONEY - cost_of(Activity.TRAIN) + income
    assert income > 0
