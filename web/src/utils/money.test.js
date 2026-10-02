import { describe, expect, it } from 'vitest';
import {
  UNAFFORDABLE_LINE,
  activityCost,
  affordablePicks,
  buildMoneySteps,
  canAffordPick,
  firstFreeActivity,
  priceLabel,
  scheduleCost,
} from './money.js';

const ACTIVITIES = [
  { id: 'play', cost: 0, income_per_day: 0 },
  { id: 'train', cost: 25, income_per_day: 0 },
  { id: 'educate', cost: 35, income_per_day: 0 },
  { id: 'job', cost: 0, income_per_day: 8 },
];

describe('costs', () => {
  it('reads cost from the activity table, 0 when unknown', () => {
    expect(activityCost(ACTIVITIES, 'educate')).toBe(35);
    expect(activityCost(ACTIVITIES, 'nope')).toBe(0);
  });

  it('sums a schedule', () => {
    expect(scheduleCost(ACTIVITIES, ['train', 'educate', 'play'])).toBe(60);
  });
});

describe('canAffordPick', () => {
  it('accepts a schedule that costs exactly the money', () => {
    expect(canAffordPick(60, ACTIVITIES, ['train', 'play', 'play'], 1, 'educate')).toBe(true);
  });

  it('rejects one coin over', () => {
    expect(canAffordPick(59, ACTIVITIES, ['train', 'play', 'play'], 1, 'educate')).toBe(false);
  });

  it('counts a replaced slot at its new price, not its old one', () => {
    expect(canAffordPick(25, ACTIVITIES, ['educate', 'play', 'play'], 0, 'train')).toBe(true);
  });
});

describe('priceLabel', () => {
  it('labels cost, income and free options', () => {
    expect(priceLabel(ACTIVITIES[2])).toBe('-35');
    expect(priceLabel(ACTIVITIES[3])).toBe('+8/일');
    expect(priceLabel(ACTIVITIES[0])).toBe('무료');
    expect(priceLabel(undefined)).toBe('');
  });
});

describe('affordablePicks', () => {
  it('leaves an affordable schedule alone', () => {
    const picks = ['train', 'play', 'play'];
    expect(affordablePicks(100, ACTIVITIES, picks)).toEqual(picks);
  });

  it('swaps paid slots from the end until affordable', () => {
    expect(affordablePicks(30, ACTIVITIES, ['train', 'educate', 'train'])).toEqual([
      'train',
      'play',
      'play',
    ]);
  });

  it('never mutates its input', () => {
    const picks = ['educate', 'educate', 'educate'];
    affordablePicks(0, ACTIVITIES, picks);
    expect(picks).toEqual(['educate', 'educate', 'educate']);
  });

  it('first free activity is the first option with no cost and no income', () => {
    expect(firstFreeActivity(ACTIVITIES)).toBe('play');
    expect(firstFreeActivity([{ id: 'train', cost: 5 }])).toBeUndefined();
  });
});

describe('buildMoneySteps', () => {
  const log = [
    {
      cost: 25,
      bonus: 0,
      days: [{ day: 1 }, { day: 2 }],
    },
    {
      cost: 0,
      bonus: 6,
      days: [{ day: 3, income: 8 }, { day: 4, income: 0 }, { day: 5, income: 8 }],
    },
  ];

  it('charges the cost on the first day of the slot', () => {
    expect(buildMoneySteps(log, 100)[0]).toEqual({ money: 75, delta: -25 });
  });

  it('adds income per day and the bonus on the last day', () => {
    const steps = buildMoneySteps(log, 100);
    expect(steps.map((step) => step.money)).toEqual([75, 75, 83, 83, 97]);
    expect(steps[4].delta).toBe(14);
  });

  it('ends at the server total', () => {
    expect(buildMoneySteps(log, 100).at(-1).money).toBe(100 - 25 + 16 + 6);
  });

  it('handles an empty or missing log', () => {
    expect(buildMoneySteps([], 50)).toEqual([]);
    expect(buildMoneySteps(undefined, 50)).toEqual([]);
  });
});

describe('copy', () => {
  it('has an advisor line for unaffordable picks', () => {
    expect(UNAFFORDABLE_LINE.length).toBeGreaterThan(0);
  });
});
