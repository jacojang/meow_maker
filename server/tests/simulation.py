"""Shared simulation harness for balance checks.

A strategy is a function `(run, rng) -> MonthPlan` called once per month with
the live GameRun. `simulate` plays full runs over consecutive seeds and returns
one `RunResult` per run, so slices can reuse it with their own strategies,
run counts and (via `run_factory`) their own starting runs.
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from statistics import mean

from app.game.endings import SCORE_STATS
from app.game import (
    ACTIVITY_EFFECTS,
    SLOTS_PER_MONTH,
    Activity,
    CatStats,
    Care,
    Diet,
    Ending,
    FESTIVAL_MONTH,
    FESTIVAL_RULES,
    GameRun,
    cost_of,
)
from app.game.economy import total_cost

ROTATION = (
    Activity.TRAIN,
    Activity.PLAY,
    Activity.EDUCATE,
    Activity.GROOM,
    Activity.REST,
)
CAREFUL_MARGIN = 5
LAST_MONTHS_FROM = 11
# Pre-economy strategies and baselines assume money never binds.
LEGACY_MONEY = 1_000_000
PAID_ACTIVITIES = tuple(a for a in Activity if cost_of(a) > 0)
CHEAPEST_PAID = min(cost_of(a) for a in PAID_ACTIVITIES)


def unlimited_money_run() -> GameRun:
    return GameRun(money=LEGACY_MONEY)


@dataclass(frozen=True)
class MonthPlan:
    activities: Sequence[Activity]
    diet: Diet = Diet.NORMAL
    fallback: Activity = Activity.REST
    care: Care | None = None
    contest: str | None = None


Strategy = Callable[[GameRun, random.Random], MonthPlan]


@dataclass(frozen=True)
class RunResult:
    seed: int
    ending: Ending
    score: int
    stats: CatStats
    denied_months: int = 0
    broke_months: int = 0
    final_money: int = 0
    months: int = 0
    festival_rank: int | None = None


def careless(run: GameRun, rng: random.Random) -> MonthPlan:
    return MonthPlan([Activity.PLAY] * SLOTS_PER_MONTH)


def grinder(run: GameRun, rng: random.Random) -> MonthPlan:
    return MonthPlan([Activity.TRAIN] * SLOTS_PER_MONTH)


_NON_JOB = [a for a in Activity if a is not Activity.JOB]


def random_strategy(run: GameRun, rng: random.Random) -> MonthPlan:
    return MonthPlan([rng.choice(_NON_JOB) for _ in range(SLOTS_PER_MONTH)])


def balanced(run: GameRun, rng: random.Random) -> MonthPlan:
    start = (run.month - 1) * SLOTS_PER_MONTH
    return MonthPlan([ROTATION[(start + i) % len(ROTATION)] for i in range(SLOTS_PER_MONTH)])


def _stress_aware(
    run: GameRun, choose: Callable[[GameRun, int], Activity]
) -> MonthPlan:
    stats = run.stats
    limit = stats.health
    if run.month >= LAST_MONTHS_FROM:
        limit = min(limit, stats.discipline)
    stress = stats.stress
    start = (run.month - 1) * SLOTS_PER_MONTH
    plan = []
    for index in range(SLOTS_PER_MONTH):
        activity = choose(run, start + index)
        stress_after = stress + ACTIVITY_EFFECTS[activity].get("stress", 0)
        if stress_after > limit - CAREFUL_MARGIN:
            activity = Activity.REST
        stress = max(0, stress + ACTIVITY_EFFECTS[activity].get("stress", 0))
        plan.append(activity)
    return MonthPlan(plan)


def careful(run: GameRun, rng: random.Random) -> MonthPlan:
    """Rotation, but a slot becomes REST when its stress would eat the headroom."""
    return _stress_aware(run, lambda _run, slot: ROTATION[slot % len(ROTATION)])


_ACTIVITY_FOR_STAT = {
    "health": Activity.GROOM,
    "affection": Activity.GROOM,
    "discipline": Activity.TRAIN,
    "curiosity": Activity.OUTING,
    "refinement": Activity.EDUCATE,
}


def _train_lowest(run: GameRun, slot: int) -> Activity:
    lowest = min(SCORE_STATS, key=lambda name: getattr(run.stats, name))
    return _ACTIVITY_FOR_STAT[lowest]


def targeted(run: GameRun, rng: random.Random) -> MonthPlan:
    """Deliberate balancing: always work on the weakest stat, rest when stress is near."""
    return _stress_aware(run, _train_lowest)


def _with_fallback(plan: MonthPlan, fallback: Activity) -> MonthPlan:
    return MonthPlan(plan.activities, plan.diet, fallback, plan.care, plan.contest)


def all_job(run: GameRun, rng: random.Random) -> MonthPlan:
    return _with_fallback(_stress_aware(run, lambda _r, _s: Activity.JOB), Activity.REST)


def all_train(run: GameRun, rng: random.Random) -> MonthPlan:
    return _with_fallback(_stress_aware(run, lambda _r, _s: Activity.TRAIN), Activity.REST)


_SPEND_ROTATION = (Activity.EDUCATE, Activity.TRAIN, Activity.OUTING)


def spend_everything(run: GameRun, rng: random.Random) -> MonthPlan:
    """Every paid option each month, no job."""
    return _with_fallback(
        _stress_aware(run, lambda _r, slot: _SPEND_ROTATION[slot % 3]), Activity.REST
    )


def mixed(run: GameRun, rng: random.Random) -> MonthPlan:
    """Works the weakest stat; a slot it cannot pay for becomes a job."""
    return _with_fallback(_stress_aware(run, _train_lowest), Activity.JOB)


def neglectful(run: GameRun, rng: random.Random) -> MonthPlan:
    """Plays all month, resting only to avoid falling sick: delinquent but never ill."""
    return _stress_aware(run, lambda _r, _s: Activity.PLAY)


def attentive(run: GameRun, rng: random.Random) -> MonthPlan:
    """Same schedule as neglectful, but scolds whenever the cat is delinquent."""
    plan = neglectful(run, rng)
    care = Care.SCOLD if run.is_delinquent else None
    return MonthPlan(plan.activities, plan.diet, plan.fallback, care, plan.contest)


CARE_STRATEGIES: dict[str, Strategy] = {
    "neglectful": neglectful,
    "attentive": attentive,
}

ECONOMY_STRATEGIES: dict[str, Strategy] = {
    "all_job": all_job,
    "all_train": all_train,
    "spend_everything": spend_everything,
    "mixed": mixed,
}

STRATEGIES: dict[str, Strategy] = {
    "careless": careless,
    "grinder": grinder,
    "random": random_strategy,
    "balanced": balanced,
    "careful": careful,
    "targeted": targeted,
}


def best_contest(run: GameRun) -> str:
    """The contest whose keyed stat is currently highest (first listed wins ties)."""
    return max(
        FESTIVAL_RULES.contests,
        key=lambda contest_id: getattr(run.stats, FESTIVAL_RULES.contests[contest_id].stat),
    )


def enter_festival(base: Strategy) -> Strategy:
    """Plays `base` all year, but enters the best-fit contest in the festival month."""

    def strategy(run: GameRun, rng: random.Random) -> MonthPlan:
        plan = base(run, rng)
        if run.month != FESTIVAL_MONTH:
            return plan
        return MonthPlan(plan.activities, plan.diet, plan.fallback, plan.care, best_contest(run))

    return strategy


def downgrade_to_affordable(
    activities: Sequence[Activity], money: int, fallback: Activity
) -> list[Activity]:
    """Swaps paid slots, last first, for `fallback` until the month is affordable."""
    chosen = list(activities)
    for index in reversed(range(len(chosen))):
        if total_cost(chosen) <= money:
            break
        if cost_of(chosen[index]) > 0:
            chosen[index] = fallback
    return chosen


def play_run(
    strategy: Strategy,
    seed: int,
    run_factory: Callable[[], GameRun] = unlimited_money_run,
    day_rng_factory: Callable[[int], random.Random] | None = None,
) -> RunResult:
    game_rng = random.Random(seed)
    day_rng = (day_rng_factory or (lambda s: random.Random(f"day-{s}")))(seed)
    strategy_rng = random.Random(f"strategy-{seed}")
    run = run_factory()
    denied = broke = months = 0
    while not run.finished:
        plan = strategy(run, strategy_rng)
        activities = list(plan.activities)
        entering = plan.contest is not None and run.forced_slots is None
        if run.forced_slots is None and not entering:
            months += 1
            broke += run.money < CHEAPEST_PAID
            if total_cost(activities) > run.money:
                denied += 1
                activities = downgrade_to_affordable(activities, run.money, plan.fallback)
        if not entering:
            run.assign_month(activities)
        run.assign_diet(plan.diet)
        run.advance_month(game_rng, day_rng, care=plan.care, contest=plan.contest)
    return RunResult(
        seed=seed,
        ending=run.ending,
        score=run.score,
        stats=run.stats,
        denied_months=denied,
        broke_months=broke,
        final_money=run.money,
        months=months,
        festival_rank=None if run.festival_result is None else run.festival_result["rank"],
    )


def simulate(
    strategy: Strategy,
    runs: int = 500,
    base_seed: int = 0,
    run_factory: Callable[[], GameRun] = unlimited_money_run,
    day_rng_factory: Callable[[int], random.Random] | None = None,
) -> list[RunResult]:
    return [
        play_run(strategy, base_seed + offset, run_factory, day_rng_factory)
        for offset in range(runs)
    ]


def ending_rates(results: Iterable[RunResult]) -> dict[Ending, float]:
    results = list(results)
    counts = Counter(result.ending for result in results)
    return {ending: count / len(results) for ending, count in counts.items()}


def rate_of(results: Iterable[RunResult], ending: Ending) -> float:
    return ending_rates(results).get(ending, 0.0)


def mean_score(results: Iterable[RunResult]) -> float:
    return mean(result.score for result in results)


def format_report(name: str, results: Sequence[RunResult]) -> str:
    rates = ", ".join(
        f"{ending.value} {rate:.0%}"
        for ending, rate in sorted(ending_rates(results).items(), key=lambda kv: -kv[1])
    )
    return f"{name}: n={len(results)} mean_score={mean_score(results):.0f} | {rates}"


def denied_month_rate(results: Iterable[RunResult]) -> float:
    results = list(results)
    return sum(r.denied_months for r in results) / sum(r.months for r in results)


def broke_run_rate(results: Iterable[RunResult]) -> float:
    results = list(results)
    return sum(r.broke_months > 0 for r in results) / len(results)
