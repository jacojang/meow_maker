export const SPEEDS = ['normal', 'fast', 'skip'];
export const DEFAULT_SPEED = 'normal';
export const SPEED_STORAGE_KEY = 'meow-maker.playback-speed';

const DAY_MS = { normal: 250, fast: 80, skip: 0 };

export function isSpeed(value) {
  return SPEEDS.includes(value);
}

export function dayDelayMs(speed) {
  return DAY_MS[speed] ?? DAY_MS[DEFAULT_SPEED];
}

export function defaultStorage() {
  try {
    return globalThis.localStorage ?? null;
  } catch {
    return null;
  }
}

export function loadSpeed(storage = defaultStorage()) {
  try {
    const value = storage?.getItem(SPEED_STORAGE_KEY);
    return isSpeed(value) ? value : DEFAULT_SPEED;
  } catch {
    return DEFAULT_SPEED;
  }
}

export function saveSpeed(speed, storage = defaultStorage()) {
  if (!isSpeed(speed)) return;
  try {
    storage?.setItem(SPEED_STORAGE_KEY, speed);
  } catch {
    // Storage can be blocked or full; the choice then lasts only this session.
  }
}

// The first month always plays at normal speed; later months use the saved choice.
export function startingSpeed(hasPlayedMonth, storage = defaultStorage()) {
  return hasPlayedMonth ? loadSpeed(storage) : DEFAULT_SPEED;
}
