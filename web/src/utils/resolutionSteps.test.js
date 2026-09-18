import { describe, expect, it } from 'vitest';
import { resolutionSteps } from './resolutionSteps.js';

const ACTIVITIES = [
  { id: 'play', effects: { affection: 4, stress: 12 } },
  { id: 'train', effects: { discipline: 5, stress: 8 } },
  { id: 'rest', effects: { stress: -20 } },
];

const DIETS = [
  { id: 'normal', effects: { weight: 1 } },
  { id: 'hearty', effects: { weight: 3, health: 1 } },
];

describe('resolutionSteps', () => {
  it('returns one step per pick plus a trailing diet step', () => {
    const picks = ['play', 'train', 'rest'];
    const steps = resolutionSteps(30, picks, ACTIVITIES, 'normal', DIETS);

    expect(steps).toHaveLength(picks.length + 1);
    expect(steps.map((step) => step.kind)).toEqual([
      'activity',
      'activity',
      'activity',
      'diet',
    ]);
  });

  it('pairs each pick with its day range in order', () => {
    const picks = ['play', 'train', 'rest'];
    const steps = resolutionSteps(30, picks, ACTIVITIES, 'normal', DIETS);

    expect(steps.slice(0, 3).map((step) => [step.id, step.title])).toEqual([
      ['play', '1~10일'],
      ['train', '11~20일'],
      ['rest', '21~30일'],
    ]);
  });

  it('carries each activity step effects from the matching activity entry', () => {
    const steps = resolutionSteps(30, ['play'], ACTIVITIES, 'normal', DIETS);

    expect(steps[0].effects).toBe(ACTIVITIES[0].effects);
  });

  it('carries each activity step\'s real days so playback can tick through them', () => {
    const picks = ['play', 'train', 'rest'];
    const steps = resolutionSteps(30, picks, ACTIVITIES, 'normal', DIETS);

    expect(steps[0].days).toEqual(Array.from({ length: 10 }, (_, i) => i + 1));
    expect(steps[1].days).toEqual(Array.from({ length: 10 }, (_, i) => i + 11));
    expect(steps[2].days).toEqual(Array.from({ length: 10 }, (_, i) => i + 21));
  });

  it('appends the diet step last with the matching diet entry effects', () => {
    const steps = resolutionSteps(30, ['play'], ACTIVITIES, 'hearty', DIETS);
    const dietStep = steps.at(-1);

    expect(dietStep.kind).toBe('diet');
    expect(dietStep.id).toBe('hearty');
    expect(dietStep.title).toBe('식단');
    expect(dietStep.effects).toBe(DIETS[1].effects);
  });

  it('falls back to empty effects when an id has no matching entry', () => {
    const steps = resolutionSteps(30, ['unknown-activity'], [], 'unknown-diet', []);

    expect(steps[0].effects).toEqual({});
    expect(steps[1].effects).toEqual({});
  });
});
