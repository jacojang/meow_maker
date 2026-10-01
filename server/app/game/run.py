from __future__ import annotations

import copy
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .activities import Activity, effects_for
from .daily import (
    VARIANCE_ACTIVITIES,
    DayOutcome,
    DayYield,
    days_in_month,
    roll_outcome,
    slot_day_counts,
)
from .care import Care, care_outcome
from .delinquency import apply_delinquent_penalty
from .diet import Diet, apply_diet
from .economy import START_MONEY, cost_of, income_per_day, total_cost, with_perfect_bonus
from .endings import RULES, Ending, RunSummary, compute_score, determine_ending, is_early_ending
from .events import Event, apply_event, roll_event
from .festival import FESTIVAL_MONTH, RULES as FESTIVAL_RULES, resolve_contest
from .outing import apply_outing_result, resolve_outing
from .stats import CatStats
from .warnings import compute_warnings
from .weight import apply_overweight_penalty

MONTHS_PER_RUN = 12
SLOTS_PER_MONTH = 3

FIRST_MONTH = 1


class GameRuleError(Exception):
    pass


class RunFinishedError(GameRuleError):
    pass


class IncompleteMonthError(GameRuleError):
    pass


class InsufficientMoneyError(GameRuleError):
    pass


class InvalidContestError(GameRuleError):
    pass


def _empty_slots() -> list[Activity | None]:
    return [None] * SLOTS_PER_MONTH


@dataclass
class GameRun:
    stats: CatStats = field(default_factory=CatStats)
    month: int = FIRST_MONTH
    finished: bool = False
    slots: list[Activity | None] = field(default_factory=_empty_slots)
    diet: Diet = Diet.NORMAL
    last_event: Event | None = None
    ending: Ending | None = None
    score: int | None = None
    last_outing_result: str | None = None
    sick_streak: int = 0
    sick_months_total: int = 0
    bedridden_months: int = 0
    last_month_log: list[dict[str, Any]] = field(default_factory=list)
    money: int = START_MONEY
    delinquent_streak: int = 0
    last_care: dict[str, Any] | None = None
    festival_result: dict[str, Any] | None = None
    ribbons: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not FIRST_MONTH <= self.month <= MONTHS_PER_RUN:
            raise ValueError(f"month out of range: {self.month}")
        if len(self.slots) != SLOTS_PER_MONTH:
            raise ValueError(f"expected {SLOTS_PER_MONTH} slots, got {len(self.slots)}")
        if self.money < 0:
            raise ValueError(f"money cannot be negative: {self.money}")

    @property
    def is_sick(self) -> bool:
        return self.stats.is_sick

    @property
    def is_overweight(self) -> bool:
        return self.stats.is_overweight

    @property
    def is_delinquent(self) -> bool:
        return self.stats.is_delinquent

    @property
    def summary(self) -> RunSummary:
        return RunSummary(
            stats=self.stats,
            sick_months_total=self.sick_months_total,
            bedridden_months=self.bedridden_months,
            delinquent_streak=self.delinquent_streak,
            ribbon_ranks=tuple(ribbon["rank"] for ribbon in self.ribbons),
        )

    @property
    def is_bedridden(self) -> bool:
        return self.sick_streak >= RULES.bedridden_streak

    @property
    def forced_slots(self) -> list[Activity] | None:
        if self.finished or not self.is_bedridden:
            return None
        return [Activity.REST] * SLOTS_PER_MONTH

    @property
    def hospital_risk(self) -> bool:
        return (
            not self.finished
            and self.is_sick
            and not self.is_bedridden
            and self.bedridden_months == RULES.hospital_limit - 1
            and self.sick_streak == RULES.bedridden_streak - 1
        )

    @property
    def runaway_risk(self) -> bool:
        return (
            not self.finished
            and self.is_delinquent
            and not self.is_sick
            and self.delinquent_streak == RULES.runaway_streak - 1
        )

    @property
    def warnings(self) -> list[str]:
        if self.finished:
            return compute_warnings(self.stats)
        return compute_warnings(
            self.stats,
            is_bedridden=self.is_bedridden,
            hospital_risk=self.hospital_risk,
            runaway_risk=self.runaway_risk,
        )

    def assign_slot(self, index: int, activity: Activity) -> None:
        self._require_active()
        if not 0 <= index < SLOTS_PER_MONTH:
            raise IndexError(f"slot index out of range: {index}")
        self.slots[index] = Activity(activity)

    def assign_month(self, activities: Sequence[Activity]) -> None:
        self._require_active()
        if len(activities) != SLOTS_PER_MONTH:
            raise IncompleteMonthError(
                f"expected {SLOTS_PER_MONTH} activities, got {len(activities)}"
            )
        chosen = [Activity(activity) for activity in activities]
        if self.forced_slots is None:
            self._require_affordable(chosen)
        self.slots = chosen

    def _require_affordable(self, activities: Sequence[Activity], extra: int = 0) -> None:
        cost = total_cost(activities) + extra
        if cost > self.money:
            raise InsufficientMoneyError(
                f"schedule costs {cost} but only {self.money} is available"
            )

    def assign_diet(self, diet: Diet) -> None:
        self._require_active()
        self.diet = Diet(diet)

    def advance_month(
        self,
        rng: random.Random | None = None,
        day_rng: random.Random | None = None,
        care: Care | None = None,
        contest: str | None = None,
    ) -> None:
        self._require_active()
        forced = self.forced_slots
        self._require_valid_contest(contest)
        entering = contest is not None and forced is None
        if forced is not None:
            self.slots = forced
        elif entering:
            self.slots = _empty_slots()
        if not entering and any(slot is None for slot in self.slots):
            raise IncompleteMonthError("every slot must be assigned before advancing")
        care = None if care is None else Care(care)
        care_cost = 0 if care is None else care_outcome(care, self.stats).cost
        if forced is None:
            self._require_affordable([] if entering else self.slots, extra=care_cost)
        elif care_cost > self.money:
            raise InsufficientMoneyError(f"care costs {care_cost} but only {self.money} is available")
        rng = rng or random.Random()
        day_rng = day_rng or rng

        self.last_event = None
        self.last_outing_result = None
        played_bedridden = forced is not None

        self._apply_care(care)

        self.last_month_log = []
        if entering:
            self.stats = self.stats.apply({"stress": FESTIVAL_RULES.entry_stress})
        counts = slot_day_counts(days_in_month(self.month), SLOTS_PER_MONTH)
        first_day = 1
        for index, activity in enumerate([] if entering else self.slots):
            self._play_slot(index, activity, first_day, counts[index], day_rng)
            first_day += counts[index]
            if activity == Activity.OUTING:
                succeeded = resolve_outing(rng)
                self.stats = apply_outing_result(self.stats, succeeded)
                self.last_outing_result = "success" if succeeded else "failure"

        event = roll_event(rng)
        self.stats = apply_event(self.stats, event)
        self.last_event = event

        self.stats = apply_diet(self.stats, self.diet)
        self.stats = apply_overweight_penalty(self.stats)
        self.stats = apply_delinquent_penalty(self.stats)

        if entering:
            self._hold_contest(contest, rng)

        self._update_sick_counters(played_bedridden)

        self.stats = self.stats.apply({"age": 1})

        self.slots = _empty_slots()
        if is_early_ending(self.summary):
            self._finish()
        elif self.month == MONTHS_PER_RUN:
            self._finish()
        else:
            self.month += 1

    def _require_valid_contest(self, contest: str | None) -> None:
        if contest is None:
            return
        if self.month != FESTIVAL_MONTH:
            raise InvalidContestError("contests are only held in the festival month")
        if contest not in FESTIVAL_RULES.contests:
            raise InvalidContestError(f"unknown contest: {contest}")

    def _hold_contest(self, contest: str, rng: random.Random) -> None:
        stat = FESTIVAL_RULES.contests[contest].stat
        result = resolve_contest(contest, getattr(self.stats, stat), rng)
        self.money += result.prize
        if result.ribbon:
            self.ribbons.append({"contest": result.contest, "rank": result.rank})
        self.festival_result = result.to_dict()

    def _apply_care(self, care: Care | None) -> None:
        self.last_care = None
        if care is None:
            return
        outcome = care_outcome(care, self.stats)
        self.money -= outcome.cost
        self.stats = self.stats.apply(dict(outcome.effects))
        self.last_care = {
            "action": care.value,
            "worked": outcome.worked,
            "cost": outcome.cost,
            "effects": dict(outcome.effects),
        }

    def _play_slot(
        self,
        index: int,
        activity: Activity,
        first_day: int,
        days: int,
        day_rng: random.Random,
    ) -> None:
        rolled = activity in VARIANCE_ACTIVITIES
        sick = self.stats.is_sick
        cost = cost_of(activity)
        self.money -= cost
        pay = income_per_day(activity, sick=sick)
        pays = pay > 0
        yields = DayYield(effects_for(activity, sick=sick), days)
        log_days = []
        earned = 0
        all_succeeded = True
        for offset in range(days):
            outcome = (
                roll_outcome(day_rng, self.stats.stress)
                if rolled or pays
                else DayOutcome.NORMAL
            )
            deltas = yields.next_day(outcome, rolled=rolled)
            self.stats = self.stats.apply(deltas)
            entry = {"day": first_day + offset, "outcome": outcome.value, "deltas": deltas}
            if pays:
                day_income = 0 if outcome == DayOutcome.FAIL else pay
                all_succeeded = all_succeeded and outcome != DayOutcome.FAIL
                earned += day_income
                entry["income"] = day_income
            log_days.append(entry)
        bonus = with_perfect_bonus(earned) - earned if pays and all_succeeded else 0
        self.money += earned + bonus
        self.last_month_log.append(
            {
                "slot": index,
                "activity": activity.value,
                "days": log_days,
                "cost": cost,
                "income": earned + bonus,
                "bonus": bonus,
            }
        )

    def _update_sick_counters(self, played_bedridden: bool) -> None:
        if self.is_sick:
            self.sick_streak += 1
            self.sick_months_total += 1
        else:
            self.sick_streak = 0
        acting_out = self.is_delinquent and not self.is_sick
        self.delinquent_streak = self.delinquent_streak + 1 if acting_out else 0
        if played_bedridden:
            self.bedridden_months += 1

    def _finish(self) -> None:
        self.finished = True
        self.ending = determine_ending(self.summary)
        self.score = compute_score(self.summary)

    def _require_active(self) -> None:
        if self.finished:
            raise RunFinishedError("the run is over")

    def to_dict(self) -> dict[str, Any]:
        return {
            "stats": self.stats.to_dict(),
            "month": self.month,
            "finished": self.finished,
            "slots": [None if slot is None else slot.value for slot in self.slots],
            "diet": self.diet.value,
            "last_event": None if self.last_event is None else self.last_event.value,
            "ending": None if self.ending is None else self.ending.value,
            "score": self.score,
            "last_outing_result": self.last_outing_result,
            "sick_streak": self.sick_streak,
            "sick_months_total": self.sick_months_total,
            "bedridden_months": self.bedridden_months,
            "last_month_log": copy.deepcopy(self.last_month_log),
            "money": self.money,
            "delinquent_streak": self.delinquent_streak,
            "last_care": copy.deepcopy(self.last_care),
            "festival_result": copy.deepcopy(self.festival_result),
            "ribbons": copy.deepcopy(self.ribbons),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> GameRun:
        missing = sorted({"stats", "month", "finished", "slots", "diet"} - set(data))
        if missing:
            raise ValueError(f"missing keys: {missing}")
        slots = data["slots"]
        last_event = data.get("last_event")
        ending = data.get("ending")
        return cls(
            stats=CatStats.from_dict(data["stats"]),
            month=int(data["month"]),
            finished=bool(data["finished"]),
            slots=[None if slot is None else Activity(slot) for slot in slots],
            diet=Diet(data["diet"]),
            last_event=None if last_event is None else Event(last_event),
            ending=None if ending is None else Ending(ending),
            score=data.get("score"),
            last_outing_result=data.get("last_outing_result"),
            sick_streak=int(data.get("sick_streak", 0)),
            sick_months_total=int(data.get("sick_months_total", 0)),
            bedridden_months=int(data.get("bedridden_months", 0)),
            last_month_log=copy.deepcopy(list(data.get("last_month_log", []))),
            money=int(data.get("money", START_MONEY)),
            delinquent_streak=int(data.get("delinquent_streak", 0)),
            last_care=copy.deepcopy(data.get("last_care")),
            festival_result=copy.deepcopy(data.get("festival_result")),
            ribbons=copy.deepcopy(list(data.get("ribbons", []))),
        )
