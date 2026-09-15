import Phaser from 'phaser';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('BootScene');
  }

  preload() {
    this.load.image('opening-bg', 'assets/opening-background.jpg');
  }

  create() {
    this.scene.start('OpeningScene');
  }
}
