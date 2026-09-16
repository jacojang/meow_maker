export function fitStep(count, maxStep, available) {
  if (count <= 0) return maxStep;
  return Math.min(maxStep, available / count);
}
