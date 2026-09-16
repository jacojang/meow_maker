export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `request failed (${status})`);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail ?? null;
  }
}

async function readJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export function createGameApi({
  fetch: fetchImpl,
  baseUrl = '/api',
  credentials = 'same-origin',
} = {}) {
  async function send(path, { method = 'GET', body } = {}) {
    const doFetch = fetchImpl ?? globalThis.fetch;
    const options = { method, credentials };

    if (body !== undefined) {
      options.headers = { 'Content-Type': 'application/json' };
      options.body = JSON.stringify(body);
    }

    const response = await doFetch(`${baseUrl}${path}`, options);
    const payload = await readJson(response);

    if (!response.ok) {
      throw new ApiError(response.status, payload?.detail);
    }
    return payload;
  }

  return {
    startGame: () => send('/game', { method: 'POST' }),
    readGame: () => send('/game'),
    advanceMonth: (activities, diet = 'normal') =>
      send('/game/advance', { method: 'POST', body: { activities, diet } }),
    listActivities: async () => {
      const payload = await send('/activities');
      return payload?.activities ?? [];
    },
    listDiets: async () => {
      const payload = await send('/diets');
      return payload?.diets ?? [];
    },
  };
}

export const gameApi = createGameApi();
