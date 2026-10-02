import { describe, expect, it } from 'vitest';
import {
  DEFAULT_SPEED,
  dayDelayMs,
  loadSpeed,
  saveSpeed,
  startingSpeed,
} from './playbackSpeed.js';

const memoryStorage = (initial = {}) => {
  const data = { ...initial };
  return {
    getItem: (key) => (key in data ? data[key] : null),
    setItem: (key, value) => {
      data[key] = value;
    },
  };
};

const brokenStorage = {
  getItem: () => {
    throw new Error('blocked');
  },
  setItem: () => {
    throw new Error('blocked');
  },
};

describe('playback speed', () => {
  it('round trips a saved choice', () => {
    const storage = memoryStorage();
    saveSpeed('fast', storage);
    expect(loadSpeed(storage)).toBe('fast');
  });

  it('ignores unknown stored values and unknown saves', () => {
    const storage = memoryStorage();
    saveSpeed('warp', storage);
    expect(loadSpeed(storage)).toBe(DEFAULT_SPEED);
    expect(loadSpeed(memoryStorage({ 'meow-maker.playback-speed': 'warp' }))).toBe(DEFAULT_SPEED);
  });

  it('never throws when storage is blocked', () => {
    expect(() => saveSpeed('fast', brokenStorage)).not.toThrow();
    expect(loadSpeed(brokenStorage)).toBe(DEFAULT_SPEED);
    expect(loadSpeed(null)).toBe(DEFAULT_SPEED);
  });

  it('plays the first month at normal speed and later months at the saved speed', () => {
    const storage = memoryStorage();
    saveSpeed('skip', storage);
    expect(startingSpeed(false, storage)).toBe('normal');
    expect(startingSpeed(true, storage)).toBe('skip');
  });

  it('gets faster from normal to fast to skip', () => {
    expect(dayDelayMs('normal')).toBeGreaterThan(dayDelayMs('fast'));
    expect(dayDelayMs('skip')).toBe(0);
  });
});
