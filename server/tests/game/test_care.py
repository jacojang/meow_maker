import pytest

from app.game import (
    CARE_RULES,
    SLOTS_PER_MONTH,
    Activity,
    CatStats,
    GameRun,
    InsufficientMoneyError,
    care_outcome,
    cost_of,
)
from app.game.care import Care, parse_care_table
from app.rng import NeverRng

HEALTHY = CatStats(health=80, discipline=50, stress=30)
SICK = CatStats(health=20, discipline=50, stress=30)
DELINQUENT = CatStats(health=80, discipline=10, stress=30)
SICK_AND_DELINQUENT = CatStats(health=20, discipline=10, stress=30)
GROOM_MONTH = [Activity.GROOM] * SLOTS_PER_MONTH
TREAT_COST = CARE_RULES[Care.TREAT].cost


def advance(run, care=None, slots=GROOM_MONTH):
    run.assign_month(slots)
    run.advance_month(rng=NeverRng(), care=care)


@pytest.mark.parametrize("stats", [HEALTHY, SICK, DELINQUENT, SICK_AND_DELINQUENT])
def test_pet_always_works_and_is_free(stats):
    outcome = care_outcome(Care.PET, stats)

    assert (outcome.worked, outcome.cost, dict(outcome.effects)) == (True, 0, {"stress": -8})


def test_treat_works_when_healthy_and_charges():
    outcome = care_outcome(Care.TREAT, HEALTHY)

    assert (outcome.worked, outcome.cost, dict(outcome.effects)) == (True, 20, {"stress": -20})


@pytest.mark.parametrize("stats", [SICK, DELINQUENT, SICK_AND_DELINQUENT])
def test_treat_does_nothing_and_is_free_when_sick_or_delinquent(stats):
    outcome = care_outcome(Care.TREAT, stats)

    assert (outcome.worked, outcome.cost, dict(outcome.effects)) == (False, 0, {})


def test_scold_calms_a_delinquent_cat():
    outcome = care_outcome(Care.SCOLD, DELINQUENT)

    assert outcome.worked
    assert dict(outcome.effects) == {"stress": -15, "discipline": 2}


def test_scold_backfires_on_a_healthy_well_behaved_cat():
    outcome = care_outcome(Care.SCOLD, HEALTHY)

    assert not outcome.worked
    assert dict(outcome.effects) == {"affection": -3, "stress": 3}


def test_scold_backfires_harder_on_a_sick_cat():
    outcome = care_outcome(Care.SCOLD, SICK)

    assert dict(outcome.effects) == {"affection": -3, "stress": 5}


def test_scold_on_a_sick_delinquent_cat_still_works():
    assert care_outcome(Care.SCOLD, SICK_AND_DELINQUENT).worked


def run_with(stats, care, **kwargs):
    run = GameRun(stats=stats, **kwargs)
    reference = GameRun(stats=stats, **kwargs)
    advance(reference)
    advance(run, care)
    return run, reference


def test_no_care_leaves_last_care_empty():
    run, _ = run_with(HEALTHY, None)

    assert run.last_care is None


def test_pet_lowers_stress_by_its_effect_and_records_the_result():
    run, reference = run_with(HEALTHY, Care.PET)

    assert run.stats.stress == reference.stats.stress - 8
    assert run.last_care == {"action": "pet", "worked": True, "cost": 0, "effects": {"stress": -8}}
    assert run.money == reference.money


def test_treat_charges_money_and_lowers_stress():
    run, reference = run_with(HEALTHY, Care.TREAT)

    assert run.stats.stress == reference.stats.stress - 20
    assert run.money == reference.money - TREAT_COST
    assert run.last_care["worked"] is True and run.last_care["cost"] == TREAT_COST


def test_treat_while_sick_is_ignored_and_charges_nothing():
    run, reference = run_with(SICK, Care.TREAT)

    assert run.stats == reference.stats
    assert run.money == reference.money
    assert run.last_care == {"action": "treat", "worked": False, "cost": 0, "effects": {}}


def test_scold_while_delinquent_cuts_stress_and_raises_discipline():
    run, reference = run_with(DELINQUENT, Care.SCOLD)

    assert run.stats.stress == reference.stats.stress - 15
    assert run.stats.discipline == reference.stats.discipline + 2


def test_failed_scold_costs_affection_and_adds_stress():
    run, reference = run_with(HEALTHY, Care.SCOLD)

    assert run.stats.affection == reference.stats.affection - 3
    assert run.stats.stress == reference.stats.stress + 3
    assert run.last_care["worked"] is False


def test_care_applies_before_the_slots_so_it_changes_that_months_sickness():
    start = CatStats(health=20, discipline=100, stress=25)
    petted = GameRun(stats=start)
    plain = GameRun(stats=start)
    advance(plain)
    advance(petted, Care.PET)

    assert petted.stats.health > plain.stats.health


def test_care_is_reset_every_month():
    run = GameRun(stats=HEALTHY)
    advance(run, Care.PET)
    advance(run)

    assert run.last_care is None


def test_unaffordable_treat_is_rejected_and_nothing_changes():
    run = GameRun(stats=HEALTHY, money=TREAT_COST - 1)
    run.assign_month(GROOM_MONTH)

    with pytest.raises(InsufficientMoneyError):
        run.advance_month(rng=NeverRng(), care=Care.TREAT)

    assert run.money == TREAT_COST - 1
    assert run.month == 1 and run.last_care is None


def test_treat_plus_schedule_must_fit_together_at_the_exact_boundary():
    schedule = [Activity.EDUCATE, Activity.REST, Activity.REST]
    needed = cost_of(Activity.EDUCATE) + TREAT_COST
    short = GameRun(stats=HEALTHY, money=needed - 1)
    short.assign_month(schedule)
    with pytest.raises(InsufficientMoneyError):
        short.advance_month(rng=NeverRng(), care=Care.TREAT)

    exact = GameRun(stats=HEALTHY, money=needed)
    exact.assign_month(schedule)
    exact.advance_month(rng=NeverRng(), care=Care.TREAT)
    assert exact.money == 0


def test_a_treat_that_will_not_work_is_never_rejected_for_money():
    run = GameRun(stats=SICK, money=0)
    advance(run, Care.TREAT, slots=[Activity.REST] * 3)

    assert run.last_care["worked"] is False


def test_pet_works_and_is_free_while_bedridden_and_treat_does_not():
    bedridden = dict(stats=CatStats(health=20, discipline=50, stress=100), sick_streak=2)
    petted = GameRun(**bedridden)
    treated = GameRun(**bedridden)
    plain = GameRun(**bedridden)
    for run, care in ((petted, Care.PET), (treated, Care.TREAT), (plain, None)):
        run.advance_month(rng=NeverRng(), care=care)

    assert petted.stats.stress == plain.stats.stress - 8
    assert petted.money == plain.money
    assert treated.last_care["worked"] is False
    assert treated.money == plain.money


def test_care_survives_a_round_trip():
    run = GameRun(stats=HEALTHY)
    advance(run, Care.PET)

    assert GameRun.from_dict(run.to_dict()).last_care == run.last_care


def test_old_saves_without_care_fields_load_with_defaults():
    data = GameRun().to_dict()
    del data["last_care"]
    del data["delinquent_streak"]

    run = GameRun.from_dict(data)

    assert run.last_care is None
    assert run.delinquent_streak == 0


def test_care_table_validation_rejects_unknown_and_missing_entries():
    good = {
        "pet": {"cost": 0, "works_when": "always", "works": {"stress": -1}},
        "treat": {"cost": 1, "works_when": "healthy", "works": {"stress": -1}},
        "scold": {"cost": 0, "works_when": "delinquent", "works": {"stress": -1}},
    }
    assert set(parse_care_table(good)) == set(Care)
    with pytest.raises(ValueError):
        parse_care_table({k: v for k, v in good.items() if k != "pet"})
    with pytest.raises(ValueError):
        parse_care_table({**good, "hug": good["pet"]})
    with pytest.raises(ValueError):
        parse_care_table({**good, "pet": {**good["pet"], "works": {"mood": 1}}})
    with pytest.raises(ValueError):
        parse_care_table({**good, "pet": {**good["pet"], "works_when": "never"}})
    with pytest.raises(ValueError):
        parse_care_table({**good, "pet": {**good["pet"], "cost": -1}})
