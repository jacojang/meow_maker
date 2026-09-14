import Phaser from 'phaser';
import { BootScene } from './scenes/BootScene.js';

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  width: 960,
  height: 600,
  scene: [BootScene],
});
