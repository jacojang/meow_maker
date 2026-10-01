import { describe, expect, it } from 'vitest';
import { isPickerLocked, lockedPicks, statusBadges, topWarning } from './status.js';

describe('topWarning', () => {
  it('returns null for no codes', () => {
    expect(topWarning([])).toBeNull();
    expect(topWarning(undefined)).toBeNull();
  });

  it('picks the highest severity', () => {
    expect(topWarning(['near_delinquent', 'overweight', 'near_sick'])).toBe('near_sick');
    expect(topWarning(['overweight', 'sick', 'delinquent'])).toBe('sick');
  });

  it('ignores unknown codes', () => {
    expect(topWarning(['bedridden'])).toBeNull();
    expect(topWarning(['bedridden', 'overweight'])).toBe('overweight');
  });
});

describe('statusBadges', () => {
  it('lists active statuses in a fixed order', () => {
    expect(statusBadges({ is_sick: true, is_delinquent: true, is_overweight: true })).toEqual([
      'sick',
      'delinquent',
      'overweight',
    ]);
  });

  it('is empty when nothing is active', () => {
    expect(statusBadges({})).toEqual([]);
    expect(statusBadges(null)).toEqual([]);
  });
});

describe('bedridden', () => {
  it('shows a bedridden badge right after sick', () => {
    expect(statusBadges({ is_sick: true, is_bedridden: true, is_overweight: true })).toEqual([
      'sick',
      'bedridden',
      'overweight',
    ]);
  });

  it('ranks hospital_risk above every other warning', () => {
    expect(topWarning(['sick', 'hospital_risk'])).toBe('hospital_risk');
  });
});

describe('picker lock', () => {
  it('replaces picks with the forced slots while bedridden', () => {
    const state = { forced_slots: ['rest', 'rest', 'rest'] };
    expect(isPickerLocked(state)).toBe(true);
    expect(lockedPicks(state, ['play', 'train', 'groom'])).toEqual(['rest', 'rest', 'rest']);
  });

  it('leaves picks alone when nothing is forced', () => {
    const picks = ['play', 'train', 'groom'];
    expect(isPickerLocked({ forced_slots: null })).toBe(false);
    expect(isPickerLocked(undefined)).toBe(false);
    expect(lockedPicks({ forced_slots: null }, picks)).toBe(picks);
  });
});
