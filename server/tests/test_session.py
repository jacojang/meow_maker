import pytest

from app.db import init_db
from app.session import InMemorySessionPlayers, SQLiteSessionPlayers


def test_the_same_token_always_resolves_to_the_same_player():
    players = InMemorySessionPlayers()

    assert players.player_for("token-a") == players.player_for("token-a")


def test_different_tokens_resolve_to_different_players():
    players = InMemorySessionPlayers()

    assert players.player_for("token-a") != players.player_for("token-b")


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


def test_sqlite_the_same_token_always_resolves_to_the_same_player(db_path):
    players = SQLiteSessionPlayers(db_path)

    assert players.player_for("token-a") == players.player_for("token-a")


def test_sqlite_different_tokens_resolve_to_different_players(db_path):
    players = SQLiteSessionPlayers(db_path)

    assert players.player_for("token-a") != players.player_for("token-b")


def test_sqlite_player_survives_a_fresh_instance_pointed_at_the_same_file(db_path):
    first_player_id = SQLiteSessionPlayers(db_path).player_for("token-a")

    second_lookup = SQLiteSessionPlayers(db_path).player_for("token-a")

    assert second_lookup == first_player_id
