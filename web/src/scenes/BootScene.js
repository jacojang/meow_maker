import Phaser from 'phaser';
import { ALL_PORTRAIT_KEYS } from '../utils/portrait.js';

const ACTIVITY_SCENE_IDS = ['play', 'train', 'groom', 'rest', 'educate', 'outing'];
const SEASON_IDS = ['winter', 'spring', 'summer', 'autumn'];
const FRAME_SUFFIXES = ['', '-b', '-c'];

export class BootScene extends Phaser.Scene {
  constructor() {
    super('BootScene');
  }

  preload() {
    this.load.image('opening-bg', 'assets/opening-background.jpg');
    ALL_PORTRAIT_KEYS.forEach((key) => {
      this.load.image(`cat-${key}`, `assets/cats/cat-${key}.png`);
    });
    ACTIVITY_SCENE_IDS.forEach((id) => {
      FRAME_SUFFIXES.forEach((suffix) => {
        this.load.image(`scene-${id}${suffix}`, `assets/scenes/scene-${id}${suffix}.jpg`);
      });
    });
    SEASON_IDS.forEach((id) => {
      this.load.image(`season-${id}`, `assets/seasons/season-${id}.jpg`);
    });
  }

  create() {
    this.scene.start('OpeningScene');
  }
}
