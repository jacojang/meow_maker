const AGE_STAGES = ['kitten', 'young', 'adult'];
const HEALTH_CONDITIONS = ['healthy', 'sick'];
const WEIGHT_CONDITIONS = ['normal', 'chubby'];

const KITTEN_MAX_AGE = 4;
const YOUNG_MAX_AGE = 8;
const CHUBBY_MIN_WEIGHT = 70;

export function ageStage(age) {
  if (age <= KITTEN_MAX_AGE) return 'kitten';
  if (age <= YOUNG_MAX_AGE) return 'young';
  return 'adult';
}

export function weightCondition(weight) {
  return weight > CHUBBY_MIN_WEIGHT ? 'chubby' : 'normal';
}

export function healthCondition(isSick) {
  return isSick ? 'sick' : 'healthy';
}

export function portraitKey(stats, isSick) {
  return [ageStage(stats.age), healthCondition(isSick), weightCondition(stats.weight)].join('-');
}

const BASE_PORTRAIT_KEYS = AGE_STAGES.flatMap((age) =>
  HEALTH_CONDITIONS.flatMap((health) =>
    WEIGHT_CONDITIONS.map((weight) => `${age}-${health}-${weight}`),
  ),
);

const SPECIAL_CONDITIONS = ['bedridden', 'delinquent'];

export const ALL_PORTRAIT_KEYS = [
  ...BASE_PORTRAIT_KEYS,
  ...AGE_STAGES.flatMap((age) => SPECIAL_CONDITIONS.map((condition) => `${age}-${condition}`)),
];

export function isLyingPortrait(key) {
  return key.endsWith('-bedridden');
}

// Priority: bedridden > sick > delinquent > health/body. Flags come from the server.
export function portraitKeyCandidates(stats, isSick, isBedridden = false, warnings = []) {
  const base = portraitKey(stats, isSick);
  const stage = ageStage(stats.age);
  if (isBedridden) return [`${stage}-bedridden`, base];
  const delinquent = !isSick && (warnings ?? []).includes('delinquent');
  return delinquent ? [`${stage}-delinquent`, base] : [base];
}
