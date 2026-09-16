const SIZE = 40;
const MARGIN = 16;

export function addFullscreenButton(scene) {
  if (!scene.scale.fullscreen.available) return;

  const width = scene.scale.gameSize.width;
  const height = scene.scale.gameSize.height;
  const x = width - MARGIN - SIZE / 2;
  const y = height - MARGIN - SIZE / 2;

  const bg = scene.add
    .circle(x, y, SIZE / 2, 0x11121f, 0.75)
    .setStrokeStyle(2, 0xffffff, 0.7)
    .setInteractive({ useHandCursor: true });
  const icon = scene.add
    .text(x, y, '⛶', { fontSize: '20px', color: '#ffffff' })
    .setOrigin(0.5);

  bg.on('pointerover', () => bg.setFillStyle(0x11121f, 0.95));
  bg.on('pointerout', () => bg.setFillStyle(0x11121f, 0.75));
  bg.on('pointerdown', () => scene.scale.toggleFullscreen());

  return { background: bg, icon };
}
