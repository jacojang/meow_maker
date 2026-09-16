import Phaser from 'phaser';
import './style.css';
import { BootScene } from './scenes/BootScene.js';
import { OpeningScene } from './scenes/OpeningScene.js';
import { GameScene } from './scenes/GameScene.js';

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  width: 960,
  height: 600,
  backgroundColor: '#05060f',
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  scene: [BootScene, OpeningScene, GameScene],
});
