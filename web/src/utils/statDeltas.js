export const STAT_NAMES = ['health', 'affection', 'discipline', 'curiosity', 'stress'];

export function statDeltas(before, after) {
  if (!before || !after) return [];

  return STAT_NAMES.flatMap((stat) => {
    const from = before[stat];
    const to = after[stat];
    if (!Number.isFinite(from) || !Number.isFinite(to) || from === to) return [];
    return [{ stat, before: from, after: to, delta: to - from }];
  });
}

export function formatDelta(delta) {
  return delta > 0 ? `+${delta}` : `${delta}`;
}
