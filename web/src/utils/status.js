const WARNING_SEVERITY = {
  hospital_risk: 6,
  runaway_risk: 6,
  sick: 5,
  near_sick: 4,
  delinquent: 3,
  overweight: 2,
  near_delinquent: 1,
};

export function topWarning(codes = []) {
  const known = codes.filter((code) => code in WARNING_SEVERITY);
  if (known.length === 0) return null;
  return known.reduce((best, code) =>
    WARNING_SEVERITY[code] > WARNING_SEVERITY[best] ? code : best,
  );
}

export function statusBadges(state) {
  const badges = [];
  if (state?.is_sick) badges.push('sick');
  if (state?.is_bedridden) badges.push('bedridden');
  if (state?.is_delinquent) badges.push('delinquent');
  if (state?.is_overweight) badges.push('overweight');
  return badges;
}

export function lockedPicks(state, picks) {
  const forced = state?.forced_slots;
  return Array.isArray(forced) && forced.length > 0 ? [...forced] : picks;
}

export function isPickerLocked(state) {
  return Array.isArray(state?.forced_slots) && state.forced_slots.length > 0;
}
