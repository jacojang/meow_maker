export function daySlots(daysPerMonth, slotCount) {
  if (slotCount <= 0) return [];

  const base = Math.floor(daysPerMonth / slotCount);
  let start = 1;

  return Array.from({ length: slotCount }, (_, slot) => {
    const isLast = slot === slotCount - 1;
    const end = isLast ? daysPerMonth : start + base - 1;
    const days = Array.from({ length: end - start + 1 }, (_, i) => start + i);
    const range = { start, end, days };
    start = end + 1;
    return range;
  });
}
