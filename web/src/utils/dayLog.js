import { STAT_NAMES } from './statDeltas.js';

export const OUTCOME_COLORS = {
  fail: '#d98a8a',
  normal: '#e7e9f5',
  great: '#ffd479',
};

export const OUTCOME_TINTS = {
  fail: 0x9a6a6a,
  normal: 0xffffff,
  great: 0xffe08a,
};

const DAY_LINES = {
  play: {
    fail: '시큰둥해서 놀이가 시들했어요',
    normal: '신나게 놀았어요',
    great: '온몸으로 뛰어놀았어요!',
  },
  train: {
    fail: '집중이 안 돼서 허탕이었어요',
    normal: '꾸준히 훈련했어요',
    great: '착착 따라와서 대성공!',
  },
  groom: {
    fail: '가만히 있지 않아서 소득이 없었어요',
    normal: '얌전히 빗질을 받았어요',
    great: '털이 반짝반짝, 기분 최고!',
  },
  educate: {
    fail: '딴청만 피웠어요',
    normal: '차분히 배웠어요',
    great: '쏙쏙 배워서 놀라웠어요!',
  },
  rest: { normal: '푹 쉬었어요' },
  outing: { normal: '바깥 구경을 했어요' },
  job: {
    fail: '쥐를 놓쳐서 허탕이었어요',
    normal: '쥐를 잡아 일당을 벌었어요',
    great: '쥐를 한가득 잡았어요!',
  },
};

export function dayResultLine(activityId, outcome) {
  const lines = DAY_LINES[activityId];
  if (!lines) return '';
  return lines[outcome] ?? lines.normal ?? '';
}

export function gaugeStatsFor(effects = {}, slotDays = []) {
  const touched = new Set(
    Object.entries(effects)
      .filter(([, value]) => value !== 0)
      .map(([stat]) => stat),
  );
  slotDays.forEach((day) => Object.keys(day.deltas ?? {}).forEach((stat) => touched.add(stat)));
  return STAT_NAMES.filter((stat) => touched.has(stat));
}

const clampStat = (value) => Math.max(0, Math.min(100, value));

export function buildDaySteps(log, startStats, activities = []) {
  const running = { ...startStats };
  const effectsOf = (id) => activities.find((entry) => entry.id === id)?.effects ?? {};

  return (log ?? []).flatMap((entry) => {
    const stats = gaugeStatsFor(effectsOf(entry.activity), entry.days);
    return entry.days.map((day, index) => {
      Object.entries(day.deltas ?? {}).forEach(([stat, delta]) => {
        running[stat] = clampStat((running[stat] ?? 0) + delta);
      });
      return {
        slot: entry.slot,
        activityId: entry.activity,
        day: day.day,
        dayInSlot: index,
        outcome: day.outcome,
        line: dayResultLine(entry.activity, day.outcome),
        gauges: stats.map((stat) => ({
          stat,
          value: running[stat],
          delta: day.deltas?.[stat] ?? 0,
        })),
      };
    });
  });
}
