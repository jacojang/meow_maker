from __future__ import annotations

import random
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator

from .game import (
    ACTIVITY_EFFECTS,
    CARE_RULES,
    Care,
    DIET_EFFECTS,
    EVENT_EFFECTS,
    FESTIVAL_MONTH,
    FESTIVAL_RULES,
    MONTHS_PER_RUN,
    SLOTS_PER_MONTH,
    Activity,
    Diet,
    GameRun,
    IncompleteMonthError,
    InsufficientMoneyError,
    InvalidContestError,
    RunFinishedError,
    cost_of,
    income_per_day,
)
from .repository import GameRepository, get_game_repository
from .rng import get_day_rng, get_rng
from .session import get_current_player

router = APIRouter(prefix="/api")


class AdvanceRequest(BaseModel):
    activities: list[str] | None = None
    diet: str = Diet.NORMAL.value
    care: str | None = None
    contest: str | None = None

    @model_validator(mode="after")
    def _needs_a_schedule_or_a_contest(self) -> "AdvanceRequest":
        if self.activities is None and self.contest is None:
            raise ValueError("activities are required unless entering a contest")
        return self


def _state(run: GameRun) -> dict[str, Any]:
    return {
        **run.to_dict(),
        "is_sick": run.is_sick,
        "is_overweight": run.is_overweight,
        "is_delinquent": run.is_delinquent,
        "is_bedridden": run.is_bedridden,
        "forced_slots": None
        if run.forced_slots is None
        else [slot.value for slot in run.forced_slots],
        "warnings": run.warnings,
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
    rng: random.Random = Depends(get_rng),
    day_rng: random.Random = Depends(get_day_rng),
) -> dict[str, Any]:
    run = _load_run(repository, player_id)
    try:
        activities = [Activity(name) for name in payload.activities or []]
        diet = Diet(payload.diet)
        care = None if payload.care is None else Care(payload.care)
    except ValueError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    try:
        if payload.contest is None:
            run.assign_month(activities)
        run.assign_diet(diet)
        run.advance_month(rng=rng, day_rng=day_rng, care=care, contest=payload.contest)
    except RunFinishedError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    except (IncompleteMonthError, InsufficientMoneyError, InvalidContestError) as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    repository.save(player_id, run)
    return _state(run)


@router.get("/activities")
def list_activities() -> dict[str, Any]:
    return {
        "activities": [
            {
                "id": activity.value,
                "effects": dict(effects),
                "cost": cost_of(activity),
                "income_per_day": income_per_day(activity, sick=False),
            }
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


@router.get("/care")
def list_care() -> dict[str, Any]:
    return {
        "care": [
            {
                "id": care.value,
                "cost": rule.cost,
                "works_when": rule.works_when,
                "effects": dict(rule.works),
                "otherwise_effects": dict(rule.otherwise),
            }
            for care, rule in CARE_RULES.items()
        ]
    }


@router.get("/events")
def list_events() -> dict[str, Any]:
    return {
        "events": [
            {"id": event.value, "effects": dict(effects)}
            for event, effects in EVENT_EFFECTS.items()
        ]
    }


@router.get("/festival")
def read_festival() -> dict[str, Any]:
    return {
        "month": FESTIVAL_MONTH,
        "entry_stress": FESTIVAL_RULES.entry_stress,
        "prizes": {str(rank): prize for rank, prize in FESTIVAL_RULES.prizes.items()},
        "ribbon_scores": {
            str(rank): score for rank, score in FESTIVAL_RULES.ribbon_scores.items()
        },
        "contests": [
            {
                "id": contest.id,
                "stat": contest.stat,
                "rivals": [{"id": rival.id, "base": rival.base} for rival in contest.rivals],
            }
            for contest in FESTIVAL_RULES.contests.values()
        ],
    }
