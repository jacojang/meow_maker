import Phaser from 'phaser';
import { ALL_PORTRAIT_KEYS } from '../utils/portrait.js';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('BootScene');
  }

  preload() {
    this.load.image('opening-bg', 'assets/opening-background.jpg');
    ALL_PORTRAIT_KEYS.forEach((key) => {
      this.load.image(`cat-${key}`, `assets/cats/cat-${key}.jpg`);
    });
  }

  create() {
    this.scene.start('OpeningScene');
  }
}
