export const UNAFFORDABLE_LINE = '소지금이 모자라요. 쥐잡이 알바로 벌어 보세요.';

const findActivity = (activities, id) => activities.find((entry) => entry.id === id);

export function activityCost(activities, id) {
  return findActivity(activities, id)?.cost ?? 0;
}

export function scheduleCost(activities, picks) {
  return picks.reduce((sum, id) => sum + activityCost(activities, id), 0);
}

export function canAffordPick(money, activities, picks, slot, id) {
  const next = picks.map((pick, index) => (index === slot ? id : pick));
  return scheduleCost(activities, next) <= money;
}

export function priceLabel(activity) {
  if (!activity) return '';
  if (activity.income_per_day > 0) return `+${activity.income_per_day}/일`;
  if (activity.cost > 0) return `-${activity.cost}`;
  return '무료';
}

export function firstFreeActivity(activities) {
  return activities.find((entry) => (entry.cost ?? 0) === 0 && !(entry.income_per_day > 0))?.id;
}

// Picks persist across months while money changes; swap the last paid slots
// for a free option so the schedule is always one the server will accept.
export function affordablePicks(money, activities, picks) {
  const free = firstFreeActivity(activities);
  if (free === undefined) return picks;
  const next = [...picks];
  for (let index = next.length - 1; index >= 0; index -= 1) {
    if (scheduleCost(activities, next) <= money) break;
    if (activityCost(activities, next[index]) > 0) next[index] = free;
  }
  return next;
}

// One entry per logged day, in order: cost lands on a slot's first day, the
// perfect-session bonus on its last, income on the day it was earned.
export function buildMoneySteps(log, startMoney) {
  let running = startMoney;
  return (log ?? []).flatMap((entry) =>
    entry.days.map((day, index) => {
      let delta = day.income ?? 0;
      if (index === 0) delta -= entry.cost ?? 0;
      if (index === entry.days.length - 1) delta += entry.bonus ?? 0;
      running += delta;
      return { money: running, delta };
    }),
  );
}
