import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import InMemoryGameRepository, get_game_repository
from app.rng import NeverRng, get_rng
from app.session import InMemorySessionPlayers, get_session_players


@pytest.fixture
def api_app():
    repository = InMemoryGameRepository()
    players = InMemorySessionPlayers()
    app.dependency_overrides[get_game_repository] = lambda: repository
    app.dependency_overrides[get_session_players] = lambda: players
    # Deterministic by default: existing exact-value tests predate random
    # events/festivals and shouldn't have to account for them. Tests that
    # specifically want an event to fire override get_rng again locally.
    app.dependency_overrides[get_rng] = lambda: NeverRng()
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(api_app):
    with TestClient(api_app) as test_client:
        yield test_client


@pytest.fixture
def other_client(api_app):
    with TestClient(api_app) as test_client:
        yield test_client
