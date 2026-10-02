export const REVEAL_STEPS = ['stats', 'title', 'flavor', 'score'];
export const FINAL_REVEAL_STEP = REVEAL_STEPS.length - 1;

export const ROLL_TICKS_PER_STAT = 8;

export function initialRevealStep(justFinished) {
  return justFinished ? 0 : FINAL_REVEAL_STEP;
}

export function nextRevealStep(step) {
  return Math.min(step + 1, FINAL_REVEAL_STEP);
}

export function isFinalRevealStep(step) {
  return step >= FINAL_REVEAL_STEP;
}

export function revealed(step, section) {
  return REVEAL_STEPS.indexOf(section) <= step;
}

export function rollTotalTicks(count) {
  return count * ROLL_TICKS_PER_STAT;
}

// Stats count up one after another: stat i starts at tick i * ROLL_TICKS_PER_STAT.
export function rolledValues(finalValues, tick) {
  return finalValues.map((value, index) => {
    const progress = (tick - index * ROLL_TICKS_PER_STAT) / ROLL_TICKS_PER_STAT;
    return Math.round(value * Math.max(0, Math.min(1, progress)));
  });
}
