from __future__ import annotations

from .stats import CatStats

SICK_MARGIN = 15
DELINQUENT_MARGIN = 5


def compute_warnings(
    stats: CatStats,
    *,
    is_bedridden: bool = False,
    hospital_risk: bool = False,
    runaway_risk: bool = False,
) -> list[str]:
    codes: list[str] = []
    if stats.is_sick:
        codes.append("sick")
    elif stats.health - stats.stress <= SICK_MARGIN:
        codes.append("near_sick")
    if stats.is_delinquent:
        codes.append("delinquent")
    elif stats.discipline - stats.stress <= DELINQUENT_MARGIN:
        codes.append("near_delinquent")
    if stats.is_overweight:
        codes.append("overweight")
    if is_bedridden:
        codes.append("bedridden")
    if hospital_risk:
        codes.append("hospital_risk")
    if runaway_risk:
        codes.append("runaway_risk")
    return codes
