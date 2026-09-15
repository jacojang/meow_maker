import { describe, expect, it } from 'vitest';
import { coverScale } from './coverScale.js';

describe('coverScale', () => {
  it('picks the width-bound scale when the image is taller than the canvas ratio', () => {
    expect(coverScale(960, 600, 1536, 1024)).toBeCloseTo(0.625);
  });

  it('picks the height-bound scale when the image is wider than the canvas ratio', () => {
    expect(coverScale(960, 600, 2000, 600)).toBe(1);
  });

  it('returns 1 when the image already matches the canvas size', () => {
    expect(coverScale(960, 600, 960, 600)).toBe(1);
  });
});
