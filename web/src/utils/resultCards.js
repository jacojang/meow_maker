import { FESTIVAL_MONTH, buildFestivalCard } from './festival.js';

export { FESTIVAL_MONTH };

export function buildResultCards({ processedMonth, state, events = [] }) {
  const cards = [];

  if (state?.last_care) {
    const { action, worked, effects } = state.last_care;
    cards.push({ kind: 'care', key: action, worked, chips: effects ?? {} });
  }

  if (state?.last_outing_result) {
    cards.push({ kind: 'outing', key: state.last_outing_result, chips: [] });
  }

  if (state?.last_event) {
    const entry = events.find((event) => event.id === state.last_event);
    cards.push({ kind: 'event', key: state.last_event, chips: entry?.effects ?? {} });
  }

  const festival = processedMonth === FESTIVAL_MONTH ? buildFestivalCard(state) : null;
  if (festival) cards.push(festival);

  return cards;
}
