from __future__ import annotations

import secrets
from abc import ABC, abstractmethod
from uuid import uuid4

from fastapi import Depends, Request

SESSION_COOKIE_NAME = "meow_session"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 365
SESSION_TOKEN_BYTES = 32


class SessionPlayers(ABC):
    @abstractmethod
    def player_for(self, session_token: str) -> str: ...


class InMemorySessionPlayers(SessionPlayers):
    def __init__(self) -> None:
        self._player_ids: dict[str, str] = {}

    def player_for(self, session_token: str) -> str:
        player_id = self._player_ids.get(session_token)
        if player_id is None:
            player_id = str(uuid4())
            self._player_ids[session_token] = player_id
        return player_id


_session_players = InMemorySessionPlayers()


def get_session_players() -> SessionPlayers:
    return _session_players


def get_current_player(
    request: Request,
    players: SessionPlayers = Depends(get_session_players),
) -> str:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
        request.state.new_session_token = token
    return players.player_for(token)


async def issue_session_cookie(request: Request, call_next):
    response = await call_next(request)
    token = getattr(request.state, "new_session_token", None)
    if token:
        # No secure flag: the deployment is plain HTTP and would drop the cookie.
        response.set_cookie(
            SESSION_COOKIE_NAME,
            token,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
            path="/",
        )
    return response
