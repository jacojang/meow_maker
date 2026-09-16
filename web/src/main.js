import Phaser from 'phaser';
import { BootScene } from './scenes/BootScene.js';
import { OpeningScene } from './scenes/OpeningScene.js';
import { GameScene } from './scenes/GameScene.js';

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  width: 960,
  height: 600,
  scene: [BootScene, OpeningScene, GameScene],
});
