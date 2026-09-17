from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from .db import connect, ensure_initialized, get_db_path
from .game import GameRun


class GameRepository(ABC):
    @abstractmethod
    def get(self, player_id: str) -> GameRun | None: ...

    @abstractmethod
    def save(self, player_id: str, run: GameRun) -> None: ...


class InMemoryGameRepository(GameRepository):
    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}

    def get(self, player_id: str) -> GameRun | None:
        data = self._runs.get(player_id)
        return None if data is None else GameRun.from_dict(data)

    def save(self, player_id: str, run: GameRun) -> None:
        self._runs[player_id] = run.to_dict()


class SQLiteGameRepository(GameRepository):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def get(self, player_id: str) -> GameRun | None:
        with connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT state_json FROM game WHERE player_id = ?", (player_id,)
            ).fetchone()
        return None if row is None else GameRun.from_dict(json.loads(row[0]))

    def save(self, player_id: str, run: GameRun) -> None:
        with connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO game (player_id, state_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(player_id) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
                """,
                (player_id, json.dumps(run.to_dict()), datetime.now(UTC).isoformat()),
            )


def get_game_repository() -> GameRepository:
    db_path = get_db_path()
    ensure_initialized(db_path)
    return SQLiteGameRepository(db_path)
