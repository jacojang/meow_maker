import { describe, expect, it } from 'vitest';
import { daysInMonth, dateForDay, formatDate, seasonForMonth } from './gameCalendar.js';

describe('daysInMonth', () => {
  it('returns 31 for January', () => {
    expect(daysInMonth(1)).toBe(31);
  });

  it('returns 28 for February in the fixed non-leap calendar year', () => {
    expect(daysInMonth(2)).toBe(28);
  });

  it('returns 30 for April', () => {
    expect(daysInMonth(4)).toBe(30);
  });
});

describe('dateForDay', () => {
  it('builds the first day of January', () => {
    const date = dateForDay(1, 1);
    expect(formatDate(date)).toBe('2026/01/01');
  });

  it('builds the last day of February', () => {
    const date = dateForDay(2, 28);
    expect(formatDate(date)).toBe('2026/02/28');
  });

  it('builds a mid-year date', () => {
    const date = dateForDay(7, 15);
    expect(formatDate(date)).toBe('2026/07/15');
  });
});

describe('seasonForMonth', () => {
  it('treats december, january, and february as winter', () => {
    expect(seasonForMonth(12)).toBe('winter');
    expect(seasonForMonth(1)).toBe('winter');
    expect(seasonForMonth(2)).toBe('winter');
  });

  it('treats march through may as spring', () => {
    expect(seasonForMonth(3)).toBe('spring');
    expect(seasonForMonth(4)).toBe('spring');
    expect(seasonForMonth(5)).toBe('spring');
  });

  it('treats june through august as summer', () => {
    expect(seasonForMonth(6)).toBe('summer');
    expect(seasonForMonth(7)).toBe('summer');
    expect(seasonForMonth(8)).toBe('summer');
  });

  it('treats september through november as autumn', () => {
    expect(seasonForMonth(9)).toBe('autumn');
    expect(seasonForMonth(10)).toBe('autumn');
    expect(seasonForMonth(11)).toBe('autumn');
  });
});
