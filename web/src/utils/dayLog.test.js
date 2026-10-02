import { describe, expect, it } from 'vitest';
import { buildDaySteps, dayResultLine, gaugeStatsFor } from './dayLog.js';
import { daysInMonth } from './gameCalendar.js';

const ACTIVITIES = [
  { id: 'play', effects: { affection: 4, refinement: -2, stress: 12 } },
  { id: 'rest', effects: { stress: -20 } },
];

const LOG = [
  {
    slot: 0,
    activity: 'play',
    days: [
      { day: 1, outcome: 'great', deltas: { affection: 2, stress: 4 } },
      { day: 2, outcome: 'fail', deltas: { refinement: -1, stress: 4 } },
    ],
  },
  {
    slot: 1,
    activity: 'rest',
    days: [{ day: 3, outcome: 'normal', deltas: { stress: -20 } }],
  },
];

describe('buildDaySteps', () => {
  const steps = buildDaySteps(LOG, { affection: 10, refinement: 5, stress: 30, health: 50 }, ACTIVITIES);

  it('makes one step per logged day, in order', () => {
    expect(steps.map((step) => step.day)).toEqual([1, 2, 3]);
    expect(steps.map((step) => step.slot)).toEqual([0, 0, 1]);
    expect(steps.map((step) => step.dayInSlot)).toEqual([0, 1, 0]);
  });

  it('ticks gauges only for stats the activity changes', () => {
    expect(steps[0].gauges.map((gauge) => gauge.stat)).toEqual(['affection', 'refinement', 'stress']);
    expect(steps[2].gauges.map((gauge) => gauge.stat)).toEqual(['stress']);
  });

  it('carries running values from the start stats', () => {
    expect(steps[0].gauges).toEqual([
      { stat: 'affection', value: 12, delta: 2 },
      { stat: 'refinement', value: 5, delta: 0 },
      { stat: 'stress', value: 34, delta: 4 },
    ]);
    expect(steps[1].gauges[1]).toEqual({ stat: 'refinement', value: 4, delta: -1 });
  });

  it('clamps running values to 0..100', () => {
    expect(steps[2].gauges[0].value).toBe(18);
    const low = buildDaySteps(LOG.slice(1), { stress: 5 }, ACTIVITIES);
    expect(low[0].gauges[0].value).toBe(0);
  });

  it('uses the outcome for the result line', () => {
    expect(steps[0].line).toBe(dayResultLine('play', 'great'));
    expect(steps[0].line).not.toBe(steps[1].line);
  });

  it('does not invent days for an empty or missing log', () => {
    expect(buildDaySteps([], {}, ACTIVITIES)).toEqual([]);
    expect(buildDaySteps(undefined, {}, ACTIVITIES)).toEqual([]);
  });
});

describe('gaugeStatsFor', () => {
  it('includes stats seen in the log even if absent from the effects', () => {
    expect(gaugeStatsFor({ stress: 3 }, [{ deltas: { health: 1 } }])).toEqual(['health', 'stress']);
  });
});

describe('dayResultLine', () => {
  it('falls back to the normal line when an outcome has no copy', () => {
    expect(dayResultLine('rest', 'great')).toBe(dayResultLine('rest', 'normal'));
  });

  it('has distinct fail and great lines for rolled activities', () => {
    for (const id of ['play', 'train', 'groom', 'educate']) {
      expect(new Set(['fail', 'normal', 'great'].map((o) => dayResultLine(id, o))).size).toBe(3);
    }
  });
});

describe('server calendar parity', () => {
  it('matches the literal month-length table used by the server', () => {
    const literal = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    expect(Array.from({ length: 12 }, (_, i) => daysInMonth(i + 1))).toEqual(literal);
  });
});
