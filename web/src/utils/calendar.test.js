import { describe, expect, it } from 'vitest';
import { daySlots } from './calendar.js';

describe('daySlots', () => {
  it('splits an evenly divisible month into equal ranges', () => {
    expect(daySlots(30, 3)).toEqual([
      { start: 1, end: 10, days: Array.from({ length: 10 }, (_, i) => i + 1) },
      { start: 11, end: 20, days: Array.from({ length: 10 }, (_, i) => i + 11) },
      { start: 21, end: 30, days: Array.from({ length: 10 }, (_, i) => i + 21) },
    ]);
  });

  it('folds the remainder into the last slot', () => {
    const ranges = daySlots(31, 3);

    expect(ranges.map((range) => [range.start, range.end])).toEqual([
      [1, 10],
      [11, 20],
      [21, 31],
    ]);
    expect(ranges[2].days).toHaveLength(11);
  });

  it('covers every day exactly once', () => {
    const ranges = daySlots(30, 3);
    const allDays = ranges.flatMap((range) => range.days);

    expect(allDays).toEqual(Array.from({ length: 30 }, (_, i) => i + 1));
  });

  it('returns an empty list for zero slots', () => {
    expect(daySlots(30, 0)).toEqual([]);
  });

  it('handles a single slot spanning the whole month', () => {
    expect(daySlots(30, 1)).toEqual([
      { start: 1, end: 30, days: Array.from({ length: 30 }, (_, i) => i + 1) },
    ]);
  });
});
