from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

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


_repository = InMemoryGameRepository()


def get_game_repository() -> GameRepository:
    return _repository
