import { describe, expect, it } from 'vitest';
import { formatDelta, statDeltas } from './statDeltas.js';

const BEFORE = { health: 50, affection: 20, discipline: 10, curiosity: 30, stress: 0 };

describe('statDeltas', () => {
  it('reports only the stats that moved, in stat order', () => {
    const after = { ...BEFORE, affection: 27, health: 51, stress: 18 };

    expect(statDeltas(BEFORE, after)).toEqual([
      { stat: 'health', before: 50, after: 51, delta: 1 },
      { stat: 'affection', before: 20, after: 27, delta: 7 },
      { stat: 'stress', before: 0, after: 18, delta: 18 },
    ]);
  });

  it('reports negative movement', () => {
    const before = { ...BEFORE, stress: 40 };
    const after = { ...before, stress: 20 };

    expect(statDeltas(before, after)).toEqual([
      { stat: 'stress', before: 40, after: 20, delta: -20 },
    ]);
  });

  it('returns nothing when the month changed no stats', () => {
    expect(statDeltas(BEFORE, { ...BEFORE })).toEqual([]);
  });

  it('ignores stats missing from either side', () => {
    expect(statDeltas({ health: 50 }, { health: 60, affection: 20 })).toEqual([
      { stat: 'health', before: 50, after: 60, delta: 10 },
    ]);
  });

  it('ignores keys that are not stats', () => {
    expect(statDeltas({ ...BEFORE, mood: 1 }, { ...BEFORE, mood: 9 })).toEqual([]);
  });

  it('returns nothing when either side is missing', () => {
    expect(statDeltas(null, BEFORE)).toEqual([]);
    expect(statDeltas(BEFORE, undefined)).toEqual([]);
  });
});

describe('formatDelta', () => {
  it('signs a rise', () => {
    expect(formatDelta(4)).toBe('+4');
  });

  it('signs a fall', () => {
    expect(formatDelta(-20)).toBe('-20');
  });

  it('leaves zero unsigned', () => {
    expect(formatDelta(0)).toBe('0');
  });
});
