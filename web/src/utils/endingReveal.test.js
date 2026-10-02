import { describe, expect, it } from 'vitest';
import {
  FINAL_REVEAL_STEP,
  REVEAL_STEPS,
  ROLL_TICKS_PER_STAT,
  initialRevealStep,
  isFinalRevealStep,
  nextRevealStep,
  revealed,
  rollTotalTicks,
  rolledValues,
} from './endingReveal.js';

describe('reveal steps', () => {
  it('runs stats, title, flavor, score in order', () => {
    expect(REVEAL_STEPS).toEqual(['stats', 'title', 'flavor', 'score']);
  });

  it('starts at the first step after a fresh finish and at the last on reload', () => {
    expect(initialRevealStep(true)).toBe(0);
    expect(initialRevealStep(false)).toBe(FINAL_REVEAL_STEP);
  });

  it('advances one step at a time and stops at the last', () => {
    expect(nextRevealStep(0)).toBe(1);
    expect(nextRevealStep(FINAL_REVEAL_STEP)).toBe(FINAL_REVEAL_STEP);
  });

  it('knows the final step', () => {
    expect(isFinalRevealStep(2)).toBe(false);
    expect(isFinalRevealStep(3)).toBe(true);
  });

  it('keeps earlier sections visible', () => {
    expect(revealed(0, 'stats')).toBe(true);
    expect(revealed(0, 'title')).toBe(false);
    expect(revealed(2, 'title')).toBe(true);
    expect(revealed(2, 'score')).toBe(false);
    expect(revealed(3, 'score')).toBe(true);
  });
});

describe('rolledValues', () => {
  it('starts at zero', () => {
    expect(rolledValues([50, 20], 0)).toEqual([0, 0]);
  });

  it('counts the stats up one after another', () => {
    const half = ROLL_TICKS_PER_STAT / 2;

    expect(rolledValues([50, 20], half)).toEqual([25, 0]);
    expect(rolledValues([50, 20], ROLL_TICKS_PER_STAT)).toEqual([50, 0]);
    expect(rolledValues([50, 20], ROLL_TICKS_PER_STAT + half)).toEqual([50, 10]);
  });

  it('finishes on the exact final values', () => {
    expect(rolledValues([50, 20, 7], rollTotalTicks(3))).toEqual([50, 20, 7]);
    expect(rolledValues([50, 20, 7], rollTotalTicks(3) + 99)).toEqual([50, 20, 7]);
  });
});
