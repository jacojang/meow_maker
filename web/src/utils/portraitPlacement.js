import catMetrics from '../data/catMetrics.json';

// Provisional (AC-1): fractions of the adult height taken from the old files.
// Final values are set after AC-3 regenerates the portraits.
export const STAGE_HEIGHT_FRACTION = { kitten: 0.55, young: 0.75, adult: 1.0 };

const LEGACY_SCALE = 0.4;
const ADULT_HEIGHT_RATIO = 0.94;
const SHADOW_WIDTH_RATIO = 0.7;
const SHADOW_HEIGHT_PX = 12;
const SHADOW_ALPHA = 0.25;

export function stageOf(portraitKey) {
  return portraitKey.split('-')[0];
}

export function placePortrait(portraitKey, area, metrics = catMetrics.cats) {
  const { centerX, floorY, width, height } = area;
  const entry = metrics[portraitKey];
  const stageFraction = STAGE_HEIGHT_FRACTION[stageOf(portraitKey)];
  if (!entry || stageFraction === undefined) return null;

  const adultHeightPx = Math.min(width, height) * LEGACY_SCALE * ADULT_HEIGHT_RATIO;
  const scale = (adultHeightPx * stageFraction) / entry.bboxHeight;
  const catWidthPx = entry.bboxWidth * scale;

  return {
    x: centerX,
    y: floorY,
    scale,
    originX: entry.bboxCenterX / entry.width,
    originY: entry.floorY / entry.height,
    shadow: {
      x: centerX,
      y: floorY,
      width: catWidthPx * SHADOW_WIDTH_RATIO,
      height: SHADOW_HEIGHT_PX,
      alpha: SHADOW_ALPHA,
    },
  };
}

export function placeLegacyPortrait(area, imageSize) {
  const { centerX, floorY, width, height } = area;
  const contain = Math.min(width / imageSize.width, height / imageSize.height);
  return { x: centerX, y: floorY, scale: contain * LEGACY_SCALE, originX: 0.5, originY: 1, shadow: null };
}
