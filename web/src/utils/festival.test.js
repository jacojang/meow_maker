import { describe, expect, it, vi } from 'vitest';
import {
  buildFestivalCard,
  contestRowLabel,
  contestRows,
  festivalCardCopy,
  festivalStage,
  rankedEntries,
  sendableContest,
} from './festival.js';
import { createGameApi } from './gameApi.js';
import { buildResultCards } from './resultCards.js';

const festival = {
  month: 10,
  contests: [
    { id: 'charm', stat: 'affection', rivals: [] },
    { id: 'grace', stat: 'refinement', rivals: [] },
  ],
};
const result = {
  contest: 'charm',
  stat: 'affection',
  score: 80,
  rank: 2,
  prize: 150,
  rivals: [
    { id: 'nabi', score: 40 },
    { id: 'cheese', score: 95 },
    { id: 'boli', score: 60 },
  ],
};

describe('festivalStage', () => {
  const state = (extra = {}) => ({ month: 10, finished: false, forced_slots: null, ...extra });

  it('is none outside the festival month or without festival data', () => {
    expect(festivalStage(state({ month: 9 }), festival, null)).toBe('none');
    expect(festivalStage(state(), null, null)).toBe('none');
    expect(festivalStage(state({ finished: true }), festival, null)).toBe('none');
  });

  it('asks the player to choose, then enters or skips', () => {
    expect(festivalStage(state(), festival, null)).toBe('choose');
    expect(festivalStage(state(), festival, 'charm')).toBe('enter');
    expect(festivalStage(state(), festival, 'skip')).toBe('skip');
  });

  it('is locked while forced rest applies', () => {
    const forced = state({ forced_slots: ['rest', 'rest', 'rest'] });

    expect(festivalStage(forced, festival, 'charm')).toBe('locked');
  });
});

describe('contest helpers', () => {
  it('lists rows with the keyed stat value', () => {
    const rows = contestRows(festival, { affection: 62, refinement: 10 });

    expect(rows.map(contestRowLabel)).toEqual(['재롱 대회 · 애정 62', '기품 대회 · 기품 10']);
  });

  it('sends a contest only when entering', () => {
    expect(sendableContest('enter', 'charm')).toBe('charm');
    expect(sendableContest('skip', 'skip')).toBeNull();
    expect(sendableContest('choose', null)).toBeNull();
  });

  it('ranks the player ahead of equal scores', () => {
    const tied = { ...result, score: 95 };

    expect(rankedEntries(tied)[0].player).toBe(true);
    expect(rankedEntries(result).map((entry) => entry.score)).toEqual([95, 80, 60, 40]);
  });
});

describe('festival card', () => {
  it('has no card without a result', () => {
    expect(buildFestivalCard({ festival_result: null })).toBeNull();
  });

  it('shows rank, rival scores, prize and ribbon', () => {
    const card = buildFestivalCard({
      festival_result: result,
      ribbons: [{ contest: 'charm', rank: 2 }],
    });
    const copy = festivalCardCopy(card);

    expect(copy.title).toBe('축제 · 재롱 대회');
    expect(copy.body).toContain('2위');
    expect(copy.lines).toHaveLength(4);
    expect(copy.lines[1]).toContain('우리 고양이');
    expect(copy.footer).toBe('상금 +150  리본 획득');
  });

  it('says so when there is no prize or ribbon', () => {
    const last = { ...result, rank: 4, prize: 0 };
    const copy = festivalCardCopy(buildFestivalCard({ festival_result: last, ribbons: [] }));

    expect(copy.footer).toBe('상금 없음');
    expect(copy.body).toContain('순위권');
  });

  it('joins the result cards only for the festival month just processed', () => {
    const state = { festival_result: result, ribbons: [] };

    expect(buildResultCards({ processedMonth: 10, state }).map((card) => card.kind)).toEqual([
      'festival',
    ]);
    expect(buildResultCards({ processedMonth: 11, state })).toEqual([]);
  });
});

describe('api', () => {
  const ok = (body) => vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => body });

  it('sends the contest only when one is chosen', async () => {
    const fetch = ok({});
    const api = createGameApi({ fetch });

    await api.advanceMonth([], 'normal', null, 'charm');
    await api.advanceMonth(['rest', 'rest', 'rest'], 'normal');

    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      activities: [],
      diet: 'normal',
      contest: 'charm',
    });
    expect(JSON.parse(fetch.mock.calls[1][1].body)).not.toHaveProperty('contest');
  });

  it('reads the festival table', async () => {
    const api = createGameApi({ fetch: ok(festival) });

    expect(await api.readFestival()).toEqual(festival);
  });
});
