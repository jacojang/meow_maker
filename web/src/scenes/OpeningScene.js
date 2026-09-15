import Phaser from 'phaser';

const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 600;

export class OpeningScene extends Phaser.Scene {
  constructor() {
    super('OpeningScene');
  }

  create() {
    const bg = this.add.image(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, 'opening-bg');
    const coverScale = Math.max(
      CANVAS_WIDTH / bg.width,
      CANVAS_HEIGHT / bg.height
    );
    bg.setScale(coverScale);

    this.add
      .text(CANVAS_WIDTH / 2, CANVAS_HEIGHT * 0.15, 'Meow Maker', {
        fontFamily: 'sans-serif',
        fontSize: '64px',
        fontStyle: 'bold',
        color: '#ffffff',
        stroke: '#1a1a2e',
        strokeThickness: 8,
      })
      .setOrigin(0.5);

    const startButton = this.add
      .text(CANVAS_WIDTH / 2, CANVAS_HEIGHT * 0.85, '시작', {
        fontFamily: 'sans-serif',
        fontSize: '40px',
        fontStyle: 'bold',
        color: '#ffffff',
        stroke: '#1a1a2e',
        strokeThickness: 6,
      })
      .setOrigin(0.5)
      .setInteractive({ useHandCursor: true });

    startButton.on('pointerover', () => startButton.setColor('#ffd166'));
    startButton.on('pointerout', () => startButton.setColor('#ffffff'));
    startButton.on('pointerdown', () => {});
  }
}
