import Phaser from 'phaser';
import { coverScale } from '../utils/coverScale.js';
import { gameApi } from '../utils/gameApi.js';
import { addFullscreenButton } from './fullscreenButton.js';

const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 750;

export class OpeningScene extends Phaser.Scene {
  constructor(api = gameApi) {
    super('OpeningScene');
    this.api = api;
  }

  create() {
    this.starting = false;
    const bg = this.add.image(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, 'opening-bg');
    bg.setScale(coverScale(CANVAS_WIDTH, CANVAS_HEIGHT, bg.width, bg.height));

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

    const buttonX = CANVAS_WIDTH / 2;
    const buttonY = CANVAS_HEIGHT * 0.9;

    const buttonBg = this.add
      .rectangle(buttonX, buttonY, 200, 56, 0x1a1a2e, 0.75)
      .setStrokeStyle(2, 0xffffff, 0.8);

    const buttonLabel = this.add
      .text(buttonX, buttonY, '시작', {
        fontFamily: 'sans-serif',
        fontSize: '32px',
        fontStyle: 'bold',
        color: '#ffffff',
      })
      .setOrigin(0.5);

    this.errorText = this.add
      .text(CANVAS_WIDTH / 2, buttonY - 60, '', {
        fontFamily: 'sans-serif',
        fontSize: '18px',
        color: '#ffd7d7',
        backgroundColor: '#5a1111',
        padding: { x: 12, y: 6 },
        align: 'center',
        wordWrap: { width: CANVAS_WIDTH - 160 },
      })
      .setOrigin(0.5)
      .setVisible(false);

    buttonBg.setInteractive({ useHandCursor: true });
    buttonBg.on('pointerover', () => buttonBg.setFillStyle(0x1a1a2e, 0.95));
    buttonBg.on('pointerout', () => buttonBg.setFillStyle(0x1a1a2e, 0.75));
    buttonBg.on('pointerdown', () => this.startRun(buttonLabel));

    addFullscreenButton(this);
  }

  async startRun(buttonLabel) {
    if (this.starting) return;
    this.starting = true;
    this.errorText.setVisible(false);
    buttonLabel.setText('시작 중…');

    try {
      const [state, activities, diets] = await Promise.all([
        this.api.startGame(),
        this.api.listActivities(),
        this.api.listDiets(),
      ]);
      this.scene.start('GameScene', { state, activities, diets });
    } catch (error) {
      const detail = error?.detail || error?.message || '';
      this.errorText.setText(`게임을 시작하지 못했습니다. ${detail}`.trim()).setVisible(true);
      buttonLabel.setText('시작');
      this.starting = false;
    }
  }
}
