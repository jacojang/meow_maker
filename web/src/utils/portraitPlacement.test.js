import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import catMetrics from '../data/catMetrics.json';
import { ALL_PORTRAIT_KEYS, isLyingPortrait } from './portrait.js';
import { STAGE_HEIGHT_FRACTION, placeLegacyPortrait, placePortrait } from './portraitPlacement.js';

const CATS_DIR = new URL('../../public/assets/cats/', import.meta.url);
const AREA = { centerX: 200, floorY: 300, width: 400, height: 300 };

describe('cat metrics staleness', () => {
  it('lists every portrait key', () => {
    expect(Object.keys(catMetrics.cats).sort()).toEqual([...ALL_PORTRAIT_KEYS].sort());
  });

  it.each(Object.entries(catMetrics.cats))('%s hash matches the asset file', (key, entry) => {
    const bytes = readFileSync(fileURLToPath(new URL(entry.file, CATS_DIR)));
    const hash = createHash('sha256').update(bytes).digest('hex');
    expect(hash, `${entry.file} changed; run measure_portraits.py`).toBe(entry.sha256);
  });
});

describe('placePortrait', () => {
  it('puts the paws on the floor line and centers by the bbox', () => {
    const entry = catMetrics.cats['adult-healthy-normal'];
    const placed = placePortrait('adult-healthy-normal', AREA);
    expect(placed.x).toBe(AREA.centerX);
    expect(placed.y).toBe(AREA.floorY);
    expect(placed.originX).toBeCloseTo(entry.bboxCenterX / entry.width);
    expect(placed.originY).toBeCloseTo(entry.floorY / entry.height);
  });

  it('gives every portrait of a stage the same on-screen height', () => {
    const heightOf = (key) => placePortrait(key, AREA).scale * catMetrics.cats[key].bboxHeight;
    const adults = ALL_PORTRAIT_KEYS.filter((k) => k.startsWith('adult') && !isLyingPortrait(k)).map(heightOf);
    adults.forEach((h) => expect(h).toBeCloseTo(adults[0]));
    const chubby = heightOf('adult-healthy-chubby');
    expect(chubby).toBeCloseTo(heightOf('adult-healthy-normal'));
  });

  it('scales stages by the provisional fractions', () => {
    const heightOf = (key) => placePortrait(key, AREA).scale * catMetrics.cats[key].bboxHeight;
    const adult = heightOf('adult-healthy-normal');
    expect(heightOf('kitten-healthy-normal') / adult).toBeCloseTo(STAGE_HEIGHT_FRACTION.kitten);
    expect(heightOf('young-sick-chubby') / adult).toBeCloseTo(STAGE_HEIGHT_FRACTION.young);
  });

  it('draws a shadow at the paws, 70% of cat width', () => {
    const key = 'young-sick-chubby';
    const placed = placePortrait(key, AREA);
    const catWidth = catMetrics.cats[key].bboxWidth * placed.scale;
    expect(placed.shadow.x).toBe(AREA.centerX);
    expect(placed.shadow.y).toBe(AREA.floorY);
    expect(placed.shadow.width).toBeCloseTo(catWidth * 0.7);
  });

  it('returns null for unlisted keys, never a stale fallback for listed ones', () => {
    expect(placePortrait('adult-unknown', AREA)).toBeNull();
    expect(placePortrait('adult-healthy-normal', AREA, {})).toBeNull();
    expect(placePortrait('adult-healthy-normal', AREA)).not.toBeNull();
  });
});

describe('on-screen heights for all portraits', () => {
  const heightOf = (key) => placePortrait(key, AREA).scale * catMetrics.cats[key].bboxHeight;
  const seated = ALL_PORTRAIT_KEYS.filter((k) => !isLyingPortrait(k));

  it('shares one height per age across all seated portraits', () => {
    ['kitten', 'young', 'adult'].forEach((stage) => {
      const heights = seated.filter((k) => k.startsWith(stage)).map(heightOf);
      heights.forEach((h) => expect(h).toBeCloseTo(heights[0]));
    });
  });

  it('keeps source seated bbox heights within 15% per age so scaling stays gentle', () => {
    ['kitten', 'young', 'adult'].forEach((stage) => {
      const raw = seated.filter((k) => k.startsWith(stage)).map((k) => catMetrics.cats[k].bboxHeight);
      expect(Math.max(...raw) / Math.min(...raw)).toBeLessThan(1.15);
    });
  });

  it('keeps a lying cat lower than the seated height of its age and its body length equal to it', () => {
    ['kitten', 'young', 'adult'].forEach((stage) => {
      const key = `${stage}-bedridden`;
      const seatedHeight = heightOf(`${stage}-healthy-normal`);
      const placed = placePortrait(key, AREA);
      expect(heightOf(key)).toBeLessThan(seatedHeight * 0.8);
      expect(catMetrics.cats[key].bboxWidth * placed.scale).toBeCloseTo(seatedHeight);
    });
  });

  it('places every key', () => {
    ALL_PORTRAIT_KEYS.forEach((k) => expect(placePortrait(k, AREA)).not.toBeNull());
  });
});

describe('placeLegacyPortrait', () => {
  it('keeps the old bottom-center contain placement', () => {
    const placed = placeLegacyPortrait(AREA, { width: 640, height: 640 });
    expect(placed).toMatchObject({ x: 200, y: 300, originX: 0.5, originY: 1, shadow: null });
    expect(placed.scale).toBeCloseTo((300 / 640) * 0.4);
  });
});
