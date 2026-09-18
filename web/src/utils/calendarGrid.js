import { dateForDay, daysInMonth } from './gameCalendar.js';

export const WEEKDAY_LABELS = ['일', '월', '화', '수', '목', '금', '토'];

export function slotIndexForDay(ranges, day) {
  return ranges.findIndex((range) => day >= range.start && day <= range.end);
}

export function calendarWeeks(month, ranges) {
  const total = daysInMonth(month);
  const startWeekday = dateForDay(month, 1).getDay();

  const cells = Array.from({ length: startWeekday }, () => null);
  for (let day = 1; day <= total; day += 1) {
    cells.push({ day, slotIndex: slotIndexForDay(ranges, day) });
  }
  while (cells.length % 7 !== 0) cells.push(null);

  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }
  return weeks;
}
