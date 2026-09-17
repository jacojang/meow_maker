import { daySlots } from './calendar.js';

export function resolutionSteps(daysPerMonth, picks, activities, dietId, diets) {
  const ranges = daySlots(daysPerMonth, picks.length);

  const activitySteps = ranges.map((range, index) => {
    const activityId = picks[index];
    const activity = activities.find((entry) => entry.id === activityId);
    return {
      id: activityId,
      kind: 'activity',
      title: `${range.start}~${range.end}일`,
      effects: activity ? activity.effects : {},
    };
  });

  const diet = diets.find((entry) => entry.id === dietId);
  const dietStep = {
    id: dietId,
    kind: 'diet',
    title: '식단',
    effects: diet ? diet.effects : {},
  };

  return [...activitySteps, dietStep];
}
