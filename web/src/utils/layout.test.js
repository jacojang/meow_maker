import { describe, expect, it } from 'vitest';
import { fitStep } from './layout.js';

describe('fitStep', () => {
  it('returns maxStep when count * maxStep fits within available', () => {
    expect(fitStep(4, 30, 150)).toBe(30);
  });

  it('shrinks below maxStep when it would overflow', () => {
    expect(fitStep(5, 34, 96)).toBe(96 / 5);
  });

  it('returns maxStep when count is zero or negative', () => {
    expect(fitStep(0, 30, 150)).toBe(30);
  });
});
