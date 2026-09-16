import { describe, expect, it, vi } from 'vitest';
import { ApiError, createGameApi } from './gameApi.js';

const STATE = {
  stats: { health: 50, affection: 20, discipline: 10, curiosity: 30, stress: 0 },
  month: 1,
  finished: false,
  slots: [null, null, null],
  is_sick: false,
  months_per_run: 12,
  slots_per_month: 3,
};

function fakeFetch(...responses) {
  const queue = [...responses];
  return vi.fn(async () => {
    const entry = queue.shift() ?? {};
    const status = entry.status ?? 200;
    return {
      ok: status >= 200 && status < 300,
      status,
      json: async () => {
        if (!('body' in entry)) throw new Error('not json');
        return entry.body;
      },
    };
  });
}

describe('createGameApi', () => {
  it('starts a run with a credentialed POST', async () => {
    const fetch = fakeFetch({ body: STATE });
    const api = createGameApi({ fetch });

    await expect(api.startGame()).resolves.toEqual(STATE);
    expect(fetch).toHaveBeenCalledWith('/api/game', {
      method: 'POST',
      credentials: 'same-origin',
    });
  });

  it('reads the current run with a credentialed GET', async () => {
    const fetch = fakeFetch({ body: STATE });
    const api = createGameApi({ fetch });

    await expect(api.readGame()).resolves.toEqual(STATE);
    expect(fetch).toHaveBeenCalledWith('/api/game', {
      method: 'GET',
      credentials: 'same-origin',
    });
  });

  it('sends the three picks as a json body when advancing', async () => {
    const fetch = fakeFetch({ body: { ...STATE, month: 2 } });
    const api = createGameApi({ fetch });

    const state = await api.advanceMonth(['play', 'train', 'rest']);

    expect(state.month).toBe(2);
    expect(fetch).toHaveBeenCalledWith('/api/game/advance', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ activities: ['play', 'train', 'rest'] }),
    });
  });

  it('unwraps the activity list', async () => {
    const activities = [{ id: 'play', effects: { affection: 4 } }];
    const fetch = fakeFetch({ body: { activities } });
    const api = createGameApi({ fetch });

    await expect(api.listActivities()).resolves.toEqual(activities);
    expect(fetch).toHaveBeenCalledWith('/api/activities', {
      method: 'GET',
      credentials: 'same-origin',
    });
  });

  it('returns an empty list when the activities payload has no list', async () => {
    const api = createGameApi({ fetch: fakeFetch({ body: {} }) });

    await expect(api.listActivities()).resolves.toEqual([]);
  });

  it('throws an ApiError carrying the status and detail', async () => {
    const fetch = fakeFetch({ status: 404, body: { detail: 'no run in progress' } });
    const api = createGameApi({ fetch });

    const error = await api.readGame().catch((caught) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(404);
    expect(error.detail).toBe('no run in progress');
    expect(error.message).toBe('no run in progress');
  });

  it('falls back to a status message when the error body is not json', async () => {
    const fetch = fakeFetch({ status: 409 });
    const api = createGameApi({ fetch });

    const error = await api.advanceMonth(['rest', 'rest', 'rest']).catch((caught) => caught);

    expect(error.status).toBe(409);
    expect(error.detail).toBeNull();
    expect(error.message).toBe('request failed (409)');
  });

  it('honours a custom base url and credentials mode', async () => {
    const fetch = fakeFetch({ body: STATE });
    const api = createGameApi({
      fetch,
      baseUrl: 'http://localhost:8000/api',
      credentials: 'include',
    });

    await api.startGame();

    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/game', {
      method: 'POST',
      credentials: 'include',
    });
  });

  it('uses the global fetch when none is injected', async () => {
    const fetch = fakeFetch({ body: STATE });
    vi.stubGlobal('fetch', fetch);

    await createGameApi().startGame();

    expect(fetch).toHaveBeenCalledOnce();
    vi.unstubAllGlobals();
  });
});
