import { describe, expect, it } from 'vitest';
import { endingFlavor, endingLabel } from './endingText.js';

const SERVER_ENDINGS = [
  'neglected',
  'delinquent',
  'balanced',
  'healthy',
  'beloved',
  'disciplined',
  'curious',
  'refined',
];
const STATS = ['health', 'affection', 'discipline', 'curiosity', 'refinement'];
const PAIRS = STATS.flatMap((first, index) =>
  STATS.slice(index + 1).map((second) => `pair_${first}_${second}`),
);

describe('ending text', () => {
  it('has a label and flavor for every server ending', () => {
    for (const id of [...SERVER_ENDINGS, ...PAIRS]) {
      expect(endingLabel(id)).not.toBe(id);
      expect(endingFlavor(id).length).toBeGreaterThan(0);
    }
  });

  it('covers all ten pairs with distinct labels', () => {
    expect(PAIRS).toHaveLength(10);
    expect(new Set(PAIRS.map(endingLabel)).size).toBe(10);
  });

  it('tolerates endings added later', () => {
    expect(endingLabel('future_ending')).toBe('future_ending');
    expect(endingFlavor('future_ending')).toBe('');
  });
});

describe('hospitalized ending', () => {
  it('has its own label and flavor', () => {
    expect(endingLabel('hospitalized')).toBe('입원한 고양이');
    expect(endingFlavor('hospitalized').length).toBeGreaterThan(0);
  });
});
