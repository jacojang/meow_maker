from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from .game import (
    ACTIVITY_EFFECTS,
    DIET_EFFECTS,
    MONTHS_PER_RUN,
    SLOTS_PER_MONTH,
    Activity,
    Diet,
    GameRun,
    IncompleteMonthError,
    RunFinishedError,
)
from .repository import GameRepository, get_game_repository
from .session import get_current_player

router = APIRouter(prefix="/api")


class AdvanceRequest(BaseModel):
    activities: list[str]
    diet: str = Diet.NORMAL.value


def _state(run: GameRun) -> dict[str, Any]:
    return {
        **run.to_dict(),
        "is_sick": run.is_sick,
        "is_overweight": run.is_overweight,
        "is_delinquent": run.is_delinquent,
        "months_per_run": MONTHS_PER_RUN,
        "slots_per_month": SLOTS_PER_MONTH,
    }


def _load_run(repository: GameRepository, player_id: str) -> GameRun:
    run = repository.get(player_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no run in progress")
    return run


@router.post("/game")
def start_game(
    player_id: str = Depends(get_current_player),
    repository: GameRepository = Depends(get_game_repository),
) -> dict[str, Any]:
    run = GameRun()
    repository.save(player_id, run)
    return _state(run)


@router.get("/game")
def read_game(
    player_id: str = Depends(get_current_player),
    repository: GameRepository = Depends(get_game_repository),
) -> dict[str, Any]:
    return _state(_load_run(repository, player_id))


@router.post("/game/advance")
def advance_game(
    payload: AdvanceRequest,
    player_id: str = Depends(get_current_player),
    repository: GameRepository = Depends(get_game_repository),
) -> dict[str, Any]:
    run = _load_run(repository, player_id)
    try:
        activities = [Activity(name) for name in payload.activities]
        diet = Diet(payload.diet)
    except ValueError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    try:
        run.assign_month(activities)
        run.assign_diet(diet)
        run.advance_month()
    except RunFinishedError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    except IncompleteMonthError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    repository.save(player_id, run)
    return _state(run)


@router.get("/activities")
def list_activities() -> dict[str, Any]:
    return {
        "activities": [
            {"id": activity.value, "effects": dict(effects)}
            for activity, effects in ACTIVITY_EFFECTS.items()
        ]
    }


@router.get("/diets")
def list_diets() -> dict[str, Any]:
    return {
        "diets": [
            {"id": diet.value, "effects": dict(effects)}
            for diet, effects in DIET_EFFECTS.items()
        ]
    }
