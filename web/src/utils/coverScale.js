export function coverScale(canvasWidth, canvasHeight, imageWidth, imageHeight) {
  return Math.max(canvasWidth / imageWidth, canvasHeight / imageHeight);
}
