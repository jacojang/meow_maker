from app.session import InMemorySessionPlayers


def test_the_same_token_always_resolves_to_the_same_player():
    players = InMemorySessionPlayers()

    assert players.player_for("token-a") == players.player_for("token-a")


def test_different_tokens_resolve_to_different_players():
    players = InMemorySessionPlayers()

    assert players.player_for("token-a") != players.player_for("token-b")
