import { describe, expect, it } from 'vitest';
import { ALL_PORTRAIT_KEYS, portraitKey } from './portrait.js';

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
  it('lists all 12 age x health x weight combinations exactly once', () => {
    expect(ALL_PORTRAIT_KEYS).toHaveLength(12);
    expect(new Set(ALL_PORTRAIT_KEYS).size).toBe(12);
  });
});
