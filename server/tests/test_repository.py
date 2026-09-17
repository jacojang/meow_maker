import pytest

from app.db import init_db
from app.game import Activity, GameRun
from app.repository import InMemoryGameRepository, SQLiteGameRepository


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


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


def test_sqlite_get_returns_none_for_an_unknown_player(db_path):
    assert SQLiteGameRepository(db_path).get("nobody") is None


def test_sqlite_save_then_get_restores_the_run(db_path):
    run = GameRun()
    run.assign_month([Activity.PLAY, Activity.REST, Activity.REST])
    run.advance_month()

    SQLiteGameRepository(db_path).save("player-1", run)
    restored = SQLiteGameRepository(db_path).get("player-1")

    assert restored.to_dict() == run.to_dict()


def test_sqlite_saves_are_kept_per_player(db_path):
    SQLiteGameRepository(db_path).save("player-1", GameRun(month=4))

    assert SQLiteGameRepository(db_path).get("player-1").month == 4
    assert SQLiteGameRepository(db_path).get("player-2") is None


def test_sqlite_save_overwrites_the_same_players_previous_run(db_path):
    repository = SQLiteGameRepository(db_path)
    repository.save("player-1", GameRun(month=2))
    repository.save("player-1", GameRun(month=7))

    assert repository.get("player-1").month == 7


def test_sqlite_run_survives_a_fresh_repository_instance(db_path):
    SQLiteGameRepository(db_path).save("player-1", GameRun(month=3))

    restored = SQLiteGameRepository(db_path).get("player-1")

    assert restored.month == 3
