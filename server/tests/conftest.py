import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import InMemoryGameRepository, get_game_repository
from app.session import InMemorySessionPlayers, get_session_players


@pytest.fixture
def api_app():
    repository = InMemoryGameRepository()
    players = InMemorySessionPlayers()
    app.dependency_overrides[get_game_repository] = lambda: repository
    app.dependency_overrides[get_session_players] = lambda: players
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
