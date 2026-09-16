from app.game import Activity, GameRun
from app.repository import InMemoryGameRepository


def test_get_returns_none_for_an_unknown_player():
    assert InMemoryGameRepository().get("nobody") is None


def test_save_then_get_restores_the_run():
    repository = InMemoryGameRepository()
    run = GameRun()
    run.assign_month([Activity.PLAY, Activity.REST, Activity.REST])
    run.advance_month()

    repository.save("player-1", run)
    restored = repository.get("player-1")

    assert restored.to_dict() == run.to_dict()


def test_saves_are_kept_per_player():
    repository = InMemoryGameRepository()
    repository.save("player-1", GameRun(month=4))

    assert repository.get("player-1").month == 4
    assert repository.get("player-2") is None


def test_saved_runs_are_detached_from_the_caller():
    repository = InMemoryGameRepository()
    run = GameRun()
    repository.save("player-1", run)

    run.assign_month([Activity.REST, Activity.REST, Activity.REST])
    run.advance_month()

    assert repository.get("player-1").month == 1
