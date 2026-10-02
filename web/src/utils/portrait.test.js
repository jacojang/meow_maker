import { describe, expect, it } from 'vitest';
import { ALL_PORTRAIT_KEYS, portraitKey, portraitKeyCandidates } from './portrait.js';

describe('portraitKey', () => {
  it('picks kitten for the youngest ages', () => {
    expect(portraitKey({ age: 1, weight: 50 }, false)).toBe('kitten-healthy-normal');
    expect(portraitKey({ age: 4, weight: 50 }, false)).toBe('kitten-healthy-normal');
  });

  it('switches to young right after the kitten cutoff', () => {
    expect(portraitKey({ age: 5, weight: 50 }, false)).toBe('young-healthy-normal');
    expect(portraitKey({ age: 8, weight: 50 }, false)).toBe('young-healthy-normal');
  });

  it('switches to adult right after the young cutoff', () => {
    expect(portraitKey({ age: 9, weight: 50 }, false)).toBe('adult-healthy-normal');
    expect(portraitKey({ age: 40, weight: 50 }, false)).toBe('adult-healthy-normal');
  });

  it('reflects sickness', () => {
    expect(portraitKey({ age: 1, weight: 50 }, true)).toBe('kitten-sick-normal');
  });

  it('is chubby only strictly above the threshold', () => {
    expect(portraitKey({ age: 1, weight: 70 }, false)).toBe('kitten-healthy-normal');
    expect(portraitKey({ age: 1, weight: 71 }, false)).toBe('kitten-healthy-chubby');
  });

  it('combines sickness and weight', () => {
    expect(portraitKey({ age: 9, weight: 90 }, true)).toBe('adult-sick-chubby');
  });
});

describe('ALL_PORTRAIT_KEYS', () => {
  it('lists 12 age x health x weight combinations plus bedridden and delinquent per age, once each', () => {
    expect(ALL_PORTRAIT_KEYS).toHaveLength(18);
    expect(new Set(ALL_PORTRAIT_KEYS).size).toBe(18);
    expect(ALL_PORTRAIT_KEYS).toContain('adult-bedridden');
    expect(ALL_PORTRAIT_KEYS).toContain('kitten-delinquent');
  });
});

describe('portraitKeyCandidates', () => {
  it('prefers the bedridden variant and falls back to the sick portrait', () => {
    expect(portraitKeyCandidates({ age: 5, weight: 90 }, true, true)).toEqual([
      'young-bedridden',
      'young-sick-chubby',
    ]);
  });

  it('is just the normal key when not bedridden', () => {
    expect(portraitKeyCandidates({ age: 1, weight: 50 }, false)).toEqual(['kitten-healthy-normal']);
  });

  it('uses the delinquent portrait when warned and not sick, falling back to the base key', () => {
    expect(portraitKeyCandidates({ age: 9, weight: 90 }, false, false, ['delinquent'])).toEqual([
      'adult-delinquent',
      'adult-healthy-chubby',
    ]);
  });

  it('ignores near_delinquent and missing warnings', () => {
    expect(portraitKeyCandidates({ age: 1, weight: 50 }, false, false, ['near_delinquent'])).toEqual([
      'kitten-healthy-normal',
    ]);
    expect(portraitKeyCandidates({ age: 1, weight: 50 }, false, false, undefined)).toEqual([
      'kitten-healthy-normal',
    ]);
  });

  it('ranks sick above delinquent', () => {
    expect(portraitKeyCandidates({ age: 1, weight: 50 }, true, false, ['sick', 'delinquent'])).toEqual([
      'kitten-sick-normal',
    ]);
  });

  it('ranks bedridden above sick and delinquent', () => {
    expect(portraitKeyCandidates({ age: 1, weight: 50 }, true, true, ['delinquent'])).toEqual([
      'kitten-bedridden',
      'kitten-sick-normal',
    ]);
  });
});
