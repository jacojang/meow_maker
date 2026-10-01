import { describe, expect, it } from 'vitest';
import { buildResultCards, FESTIVAL_MONTH } from './resultCards.js';

const result = { contest: 'charm', stat: 'affection', score: 90, rank: 1, prize: 300, rivals: [] };
const events = [{ id: 'gift', effects: { affection: 2, weight: 1 } }];

describe('buildResultCards', () => {
  it('returns no cards when nothing happened', () => {
    expect(buildResultCards({ processedMonth: 3, state: {}, events })).toEqual([]);
  });

  it('orders outing, event, festival', () => {
    const state = {
      last_outing_result: 'success',
      last_event: 'gift',
      festival_result: result,
    };
    const cards = buildResultCards({ processedMonth: FESTIVAL_MONTH, state, events });

    expect(cards.map((card) => card.kind)).toEqual(['outing', 'event', 'festival']);
    expect(cards[1].chips).toEqual({ affection: 2, weight: 1 });
  });

  it('skips a stale festival result outside the festival month', () => {
    const state = { festival_result: result };

    expect(buildResultCards({ processedMonth: FESTIVAL_MONTH + 1, state, events })).toEqual([]);
  });

  it('tolerates an unknown event id', () => {
    const cards = buildResultCards({ processedMonth: 1, state: { last_event: 'x' }, events });

    expect(cards).toEqual([{ kind: 'event', key: 'x', chips: {} }]);
  });
});
