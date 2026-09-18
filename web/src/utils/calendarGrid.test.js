import { describe, expect, it } from 'vitest';
import { daySlots } from './calendar.js';
import { calendarWeeks, slotIndexForDay, WEEKDAY_LABELS } from './calendarGrid.js';

describe('slotIndexForDay', () => {
  const ranges = daySlots(30, 3);

  it('finds the slot containing a day', () => {
    expect(slotIndexForDay(ranges, 1)).toBe(0);
    expect(slotIndexForDay(ranges, 15)).toBe(1);
    expect(slotIndexForDay(ranges, 30)).toBe(2);
  });

  it('returns -1 for a day outside every range', () => {
    expect(slotIndexForDay(ranges, 0)).toBe(-1);
    expect(slotIndexForDay(ranges, 31)).toBe(-1);
  });
});

describe('calendarWeeks', () => {
  it('pads leading blanks up to the 1st’s real weekday (Jan 1, 2026 is a Thursday)', () => {
    const ranges = daySlots(31, 3);
    const weeks = calendarWeeks(1, ranges);

    expect(weeks[0]).toEqual([null, null, null, null, { day: 1, slotIndex: 0 }, { day: 2, slotIndex: 0 }, { day: 3, slotIndex: 0 }]);
  });

  it('needs no leading blanks when the 1st falls on Sunday (Feb 1, 2026)', () => {
    const ranges = daySlots(28, 3);
    const weeks = calendarWeeks(2, ranges);

    expect(weeks[0][0]).toEqual({ day: 1, slotIndex: 0 });
  });

  it('every week is exactly 7 cells, real days included exactly once in order', () => {
    const ranges = daySlots(31, 3);
    const weeks = calendarWeeks(1, ranges);

    expect(weeks.every((week) => week.length === 7)).toBe(true);
    const days = weeks.flat().filter(Boolean).map((cell) => cell.day);
    expect(days).toEqual(Array.from({ length: 31 }, (_, i) => i + 1));
  });

  it('pads trailing blanks so the last week is still 7 cells (April 1, 2026 is a Wednesday, 30 days)', () => {
    const ranges = daySlots(30, 3);
    const weeks = calendarWeeks(4, ranges);
    const lastWeek = weeks[weeks.length - 1];

    expect(lastWeek).toHaveLength(7);
    expect(lastWeek).toEqual([
      { day: 26, slotIndex: 2 },
      { day: 27, slotIndex: 2 },
      { day: 28, slotIndex: 2 },
      { day: 29, slotIndex: 2 },
      { day: 30, slotIndex: 2 },
      null,
      null,
    ]);
  });

  it('tags each day with the slot index covering it', () => {
    const ranges = daySlots(31, 3);
    const weeks = calendarWeeks(1, ranges);
    const day15 = weeks.flat().find((cell) => cell?.day === 15);

    expect(day15.slotIndex).toBe(1);
  });
});

describe('WEEKDAY_LABELS', () => {
  it('has seven labels starting from Sunday', () => {
    expect(WEEKDAY_LABELS).toHaveLength(7);
    expect(WEEKDAY_LABELS[0]).toBe('일');
    expect(WEEKDAY_LABELS[6]).toBe('토');
  });
});
