import { describe, expect, it, vi } from 'vitest';
import { endingFlavor, endingLabel } from './endingText.js';
import { createGameApi } from './gameApi.js';
import { buildResultCards } from './resultCards.js';
import { topWarning } from './status.js';

const ok = (body) => vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => body });

describe('advanceMonth with care', () => {
  it('sends the care id only when one is chosen', async () => {
    const fetch = ok({});
    const api = createGameApi({ fetch });

    await api.advanceMonth(['rest', 'rest', 'rest'], 'normal', 'pet');
    await api.advanceMonth(['rest', 'rest', 'rest'], 'normal', null);

    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      activities: ['rest', 'rest', 'rest'],
      diet: 'normal',
      care: 'pet',
    });
    expect(JSON.parse(fetch.mock.calls[1][1].body)).not.toHaveProperty('care');
  });

  it('unwraps the care list', async () => {
    const care = [{ id: 'pet', cost: 0 }];
    const api = createGameApi({ fetch: ok({ care }) });

    expect(await api.listCare()).toEqual(care);
  });
});

describe('care result card', () => {
  it('comes first and carries the effects', () => {
    const state = {
      last_outing_result: 'success',
      last_care: { action: 'treat', worked: true, cost: 20, effects: { stress: -20 } },
    };

    const cards = buildResultCards({ processedMonth: 2, state, events: [] });

    expect(cards.map((card) => card.kind)).toEqual(['care', 'outing']);
    expect(cards[0]).toEqual({ kind: 'care', key: 'treat', worked: true, chips: { stress: -20 } });
  });

  it('is absent when no care was given', () => {
    expect(buildResultCards({ processedMonth: 2, state: { last_care: null }, events: [] })).toEqual([]);
  });
});

describe('ran away', () => {
  it('has its own ending label and flavor', () => {
    expect(endingLabel('ran_away')).toBe('가출한 고양이');
    expect(endingFlavor('ran_away').length).toBeGreaterThan(0);
  });

  it('runaway_risk is a known warning that outranks near_sick', () => {
    expect(topWarning(['near_sick', 'runaway_risk'])).toBe('runaway_risk');
  });
});
