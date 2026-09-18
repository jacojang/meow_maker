export const CALENDAR_YEAR = 2026;

const SEASON_BY_MONTH = {
  1: 'winter',
  2: 'winter',
  3: 'spring',
  4: 'spring',
  5: 'spring',
  6: 'summer',
  7: 'summer',
  8: 'summer',
  9: 'autumn',
  10: 'autumn',
  11: 'autumn',
  12: 'winter',
};

export function daysInMonth(month) {
  return new Date(CALENDAR_YEAR, month, 0).getDate();
}

export function dateForDay(month, day) {
  return new Date(CALENDAR_YEAR, month - 1, day);
}

export function formatDate(date) {
  const y = date.getFullYear();
  const m = `${date.getMonth() + 1}`.padStart(2, '0');
  const d = `${date.getDate()}`.padStart(2, '0');
  return `${y}/${m}/${d}`;
}

export function seasonForMonth(month) {
  return SEASON_BY_MONTH[month];
}
