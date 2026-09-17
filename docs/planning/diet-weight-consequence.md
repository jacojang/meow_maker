---
status: deployed
updated: 2026-09-17
---

# Diet/Weight Consequence (modify)

## Goal

Give the diet mechanic a real trade-off. As shipped
(`docs/planning/stateful-portrait.md`, part 2a), every diet option is pure
upside or neutral: HEARTY (weight +3, health +1) strictly dominates NORMAL
(weight +1) and LIGHT (weight −1), because weight has no downside anywhere
in the game — it only ever changes which of the 12 portrait images is shown.
A rational player has no reason to ever pick anything but HEARTY. PM2's
diet system (`references/princess-maker-2/status-system.md`, `Diet` table
and `Overweight` status effect) is a real monthly trade-off: every diet
option moves Constitution up or down alongside weight, and being overweight
carries its own ongoing penalty (Charisma −2/month, dress lock-out). Meow
Maker currently keeps the cosmetic half of that system (the portrait swap)
but not the mechanical half (the trade-off), which removes one of the game's
few standing monthly decisions.

## Scope

**In**

- A stat consequence tied to weight, checked like the existing sick check,
  so being overweight costs something the way PM2's Overweight status does.
- Whatever change is needed to HEARTY/LIGHT/NORMAL so at least one of them
  carries a real downside instead of pure upside — restoring diet to an
  actual choice rather than a dominant strategy.

**Out**

- Age/weight feeding into final scoring or endings — Roadmap Phase 5.
- New diet options beyond the existing three.
- Delinquency itself (Roadmap Phase 3 already names this separately).

## Mechanics

**Decision: standing overweight penalty only** (mirrors PM2's Overweight
status effect), not a per-diet cost. This is the minimal fix: `weight` was
already free to raise, so making it costly to *sustain* above a threshold —
rather than costly to raise at all — restores the tension without adding a
cost to every diet choice. HEARTY stays attractive short-term (weight +3,
health +1) but risky if used every month; LIGHT and NORMAL become the tools
for managing weight back down.

- New `OVERWEIGHT_THRESHOLD = 80` in `server/app/game/stats.py` — a
  separate, backend-only constant from the frontend's cosmetic
  `CHUBBY_MIN_WEIGHT = 70` in `web/src/utils/portrait.js` (portrait "chubby"
  is deliberately a lower, purely visual threshold, so the player sees the
  cat visibly filling out before the mechanical penalty hits).
- `CatStats.is_overweight` property (`weight > OVERWEIGHT_THRESHOLD`), same
  shape as the existing `is_sick` property.
- `server/app/game/weight.py`: `OVERWEIGHT_PENALTY = {"affection": -2}` and
  `apply_overweight_penalty(stats)`, applied in `GameRun.advance_month()`
  right after `apply_diet` (so a diet choice that pushes weight over the
  threshold this month costs affection that same month, for immediate
  feedback) — mirrors PM2's Charisma −2/month for being overweight, mapped
  to `affection` since Meow Maker has no Charisma stat and affection is the
  closest read of "how much people like the cat." Chosen over discipline/
  curiosity because it doesn't fight or cancel any diet's own stated
  benefit (health would have, since HEARTY itself grants +1 health).
- Exposed at the API as `is_overweight` in `_state()`, alongside `is_sick`.

## Open questions

None — resolved above.
