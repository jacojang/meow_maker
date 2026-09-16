import Phaser from 'phaser';
import { coverScale } from '../utils/coverScale.js';
import { gameApi } from '../utils/gameApi.js';
import { fitStep } from '../utils/layout.js';
import { portraitKey } from '../utils/portrait.js';
import { STAT_NAMES, formatDelta, statDeltas } from '../utils/statDeltas.js';
import { addFullscreenButton } from './fullscreenButton.js';

const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 600;

const COLUMN_X = [24, 344, 664];
const COLUMN_WIDTH = 272;
const TOP_PANEL_Y = 80;
const TOP_PANEL_HEIGHT = 208;
const PICKER_Y = 304;
const PICKER_HEIGHT = 216;

const PICKER_COLUMN_X = [24, 256, 488, 720];
const PICKER_COLUMN_WIDTH = 216;

const PANEL_FILL = 0x11121f;
const PANEL_ALPHA = 0.85;
const CHOICE_FILL = 0x2a2c48;
const CHOICE_SELECTED_FILL = 0x3f7d5a;

const STAT_LABELS = {
  health: '건강',
  affection: '애정',
  discipline: '규율',
  curiosity: '호기심',
  refinement: '기품',
  weight: '체중',
  stress: '스트레스',
};

const ACTIVITY_LABELS = {
  play: '놀아주기',
  train: '훈련',
  groom: '단장',
  rest: '휴식',
  educate: '교육',
};

const DIET_LABELS = {
  normal: '보통',
  light: '저칼로리',
  hearty: '든든하게',
};

function statLabel(stat) {
  return STAT_LABELS[stat] ?? stat;
}

function activityLabel(id) {
  return ACTIVITY_LABELS[id] ?? id;
}

function dietLabel(id) {
  return DIET_LABELS[id] ?? id;
}

function effectsSummary(effects = {}) {
  return STAT_NAMES.filter((stat) => stat in effects)
    .map((stat) => `${statLabel(stat)}${formatDelta(effects[stat])}`)
    .join('  ');
}

function describeError(error) {
  return error?.detail || error?.message || '알 수 없는 오류가 발생했습니다.';
}

export class GameScene extends Phaser.Scene {
  constructor(api = gameApi) {
    super('GameScene');
    this.api = api;
  }

  init(data) {
    this.state = data?.state ?? null;
    this.activities = data?.activities ?? [];
    this.diets = data?.diets ?? [];
    this.picks = this.defaultPicks();
    this.dietPick = this.diets[0]?.id ?? 'normal';
    this.deltas = [];
    this.hasPlayedMonth = false;
    this.message = '';
    this.busy = false;
  }

  create() {
    this.alive = true;
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.alive = false;
    });
    this.events.once(Phaser.Scenes.Events.DESTROY, () => {
      this.alive = false;
    });

    this.drawBackground();
    this.ui = this.add.container(0, 0);
    this.render();
    addFullscreenButton(this);
  }

  drawBackground() {
    if (this.textures.exists('opening-bg')) {
      const bg = this.add.image(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, 'opening-bg');
      bg.setScale(coverScale(CANVAS_WIDTH, CANVAS_HEIGHT, bg.width, bg.height));
    }
    this.add
      .rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, 0x05060f, 0.72)
      .setOrigin(0, 0);
  }

  defaultPicks() {
    const slots = this.state?.slots_per_month ?? 3;
    const first = this.activities[0]?.id;
    return first ? Array.from({ length: slots }, () => first) : [];
  }

  safeRender() {
    if (!this.alive) return;
    this.render();
  }

  async playMonth() {
    if (this.busy || this.picks.length === 0) return;

    const before = this.state?.stats;
    this.busy = true;
    this.message = '';
    this.render();

    try {
      const next = await this.api.advanceMonth([...this.picks], this.dietPick);
      this.deltas = statDeltas(before, next.stats);
      this.hasPlayedMonth = true;
      this.state = next;
    } catch (error) {
      this.message = describeError(error);
    } finally {
      this.busy = false;
      this.safeRender();
    }
  }

  render() {
    this.ui.removeAll(true);
    this.renderHeader();

    if (!this.state) {
      this.panel(COLUMN_X[0], TOP_PANEL_Y, CANVAS_WIDTH - 48, TOP_PANEL_HEIGHT);
      this.text(COLUMN_X[0] + 16, TOP_PANEL_Y + 16, '진행 중인 게임이 없습니다.');
      return;
    }

    this.renderStats();
    this.renderPortrait();
    this.renderActivityTable();

    if (this.state.finished) {
      this.renderEndOfRun();
    } else {
      this.renderPickers();
      this.renderPlayButton();
    }

    this.renderMessage();
  }

  renderHeader() {
    this.panel(0, 0, CANVAS_WIDTH, 64, 1);
    this.text(24, 18, 'Meow Maker', { fontSize: '24px', fontStyle: 'bold' });

    if (!this.state) return;

    const monthLabel = `${this.state.month} / ${this.state.months_per_run}`;
    this.text(CANVAS_WIDTH - 24, 18, `${monthLabel} 개월`, {
      fontSize: '24px',
      fontStyle: 'bold',
      color: '#ffd479',
    }).setOrigin(1, 0);

    if (this.state.is_sick) {
      const badge = this.add
        .rectangle(CANVAS_WIDTH - 200, 32, 200, 34, 0xa11d1d, 1)
        .setOrigin(1, 0.5)
        .setStrokeStyle(2, 0xffb4b4, 0.9);
      this.ui.add(badge);
      this.text(CANVAS_WIDTH - 300, 32, '아픔 · 효과 절반', {
        fontSize: '18px',
        fontStyle: 'bold',
        color: '#ffe8e8',
      }).setOrigin(0.5, 0.5);
    }
  }

  renderStats() {
    const x = COLUMN_X[0];
    this.panel(x, TOP_PANEL_Y, COLUMN_WIDTH, TOP_PANEL_HEIGHT);
    this.text(x + 16, TOP_PANEL_Y + 12, '능력치', { fontStyle: 'bold' });

    const step = fitStep(STAT_NAMES.length, 34, TOP_PANEL_HEIGHT - 58);
    STAT_NAMES.forEach((stat, index) => {
      const y = TOP_PANEL_Y + 44 + index * step;
      const value = this.state.stats[stat];
      this.text(x + 16, y, statLabel(stat), { fontSize: '15px', color: '#cfd2e6' });
      this.text(x + COLUMN_WIDTH - 16, y, `${value}`, {
        fontSize: '15px',
        fontStyle: 'bold',
      }).setOrigin(1, 0);
      this.statBar(
        x + 16,
        y + 18,
        COLUMN_WIDTH - 32,
        6,
        value / 100,
        stat === 'stress' ? 0xe05c5c : 0x4d9a6e,
      );
    });
  }

  statBar(x, y, width, height, fraction, color) {
    const clamped = Math.max(0, Math.min(1, fraction));
    this.ui.add(this.add.rectangle(x, y, width, height, 0x2a2c48, 1).setOrigin(0, 0));
    if (clamped > 0) {
      this.ui.add(
        this.add.rectangle(x, y, width * clamped, height, color, 1).setOrigin(0, 0),
      );
    }
  }

  renderPortrait() {
    const x = COLUMN_X[1];
    this.panel(x, TOP_PANEL_Y, COLUMN_WIDTH, TOP_PANEL_HEIGHT);
    this.text(x + COLUMN_WIDTH / 2, TOP_PANEL_Y + 12, '고양이 상태', {
      fontStyle: 'bold',
    }).setOrigin(0.5, 0);

    const textureKey = `cat-${portraitKey(this.state.stats, this.state.is_sick)}`;
    if (!this.textures.exists(textureKey)) return;

    const areaTop = TOP_PANEL_Y + 40;
    const areaHeight = TOP_PANEL_HEIGHT - 52;
    const areaWidth = COLUMN_WIDTH - 24;
    const image = this.add.image(x + COLUMN_WIDTH / 2, areaTop + areaHeight / 2, textureKey);
    image.setScale(Math.min(areaWidth / image.width, areaHeight / image.height));
    this.ui.add(image);
  }

  renderActivityTable() {
    const x = COLUMN_X[2];
    this.panel(x, TOP_PANEL_Y, COLUMN_WIDTH, TOP_PANEL_HEIGHT);
    this.text(x + 16, TOP_PANEL_Y + 12, '활동 효과', { fontStyle: 'bold' });

    const step = fitStep(this.activities.length, 34, TOP_PANEL_HEIGHT - 56);
    const effectOffset = Math.min(16, step - 12);
    this.activities.forEach((activity, index) => {
      const y = TOP_PANEL_Y + 44 + index * step;
      this.text(x + 16, y, activityLabel(activity.id), {
        fontSize: '15px',
        color: '#ffd479',
      });
      this.text(x + 16, y + effectOffset, effectsSummary(activity.effects), {
        fontSize: '12px',
        color: '#cfd2e6',
        wordWrap: { width: COLUMN_WIDTH - 32 },
      });
    });
  }

  renderPickers() {
    this.picks.forEach((pick, slot) => {
      const x = PICKER_COLUMN_X[slot] ?? PICKER_COLUMN_X[PICKER_COLUMN_X.length - 1];
      this.panel(x, PICKER_Y, PICKER_COLUMN_WIDTH, PICKER_HEIGHT);
      this.text(x + 16, PICKER_Y + 10, `슬롯 ${slot + 1}`, { fontStyle: 'bold' });

      const top = PICKER_Y + 44;
      const available = PICKER_HEIGHT - 56;
      const step = Math.min(42, available / Math.max(this.activities.length, 1));

      this.activities.forEach((activity, index) => {
        this.choiceButton(
          x + 16,
          top + index * step,
          PICKER_COLUMN_WIDTH - 32,
          step - 6,
          activityLabel(activity.id),
          activity.id === pick,
          () => this.choose(slot, activity.id),
        );
      });
    });

    this.renderDietPicker();
  }

  renderDietPicker() {
    const x = PICKER_COLUMN_X[3];
    this.panel(x, PICKER_Y, PICKER_COLUMN_WIDTH, PICKER_HEIGHT);
    this.text(x + 16, PICKER_Y + 10, '식단', { fontStyle: 'bold' });

    const top = PICKER_Y + 44;
    const available = PICKER_HEIGHT - 56;
    const step = Math.min(42, available / Math.max(this.diets.length, 1));

    this.diets.forEach((diet, index) => {
      this.choiceButton(
        x + 16,
        top + index * step,
        PICKER_COLUMN_WIDTH - 32,
        step - 6,
        dietLabel(diet.id),
        diet.id === this.dietPick,
        () => this.chooseDiet(diet.id),
      );
    });
  }

  choose(slot, activityId) {
    if (this.busy) return;
    this.picks[slot] = activityId;
    this.render();
  }

  chooseDiet(dietId) {
    if (this.busy) return;
    this.dietPick = dietId;
    this.render();
  }

  renderPlayButton() {
    const label = this.busy ? '진행 중…' : '한 달 보내기';
    const enabled = !this.busy && this.picks.length > 0;
    const fill = enabled ? 0x3f7d5a : 0x3a3c4f;

    const button = this.add
      .rectangle(CANVAS_WIDTH / 2, 560, 280, 48, fill, 1)
      .setStrokeStyle(2, 0xffffff, 0.6);
    this.ui.add(button);
    this.text(CANVAS_WIDTH / 2, 560, label, {
      fontSize: '22px',
      fontStyle: 'bold',
    }).setOrigin(0.5);

    if (!enabled) return;
    button.setInteractive({ useHandCursor: true });
    button.on('pointerover', () => button.setFillStyle(0x4d9a6e, 1));
    button.on('pointerout', () => button.setFillStyle(fill, 1));
    button.on('pointerdown', () => this.playMonth());
  }

  renderEndOfRun() {
    const x = COLUMN_X[0];
    const width = CANVAS_WIDTH - 48;
    this.panel(x, PICKER_Y, width, PICKER_HEIGHT);

    this.text(x + 24, PICKER_Y + 28, '육성을 마쳤습니다', {
      fontSize: '30px',
      fontStyle: 'bold',
      color: '#ffd479',
    });
    this.text(
      x + 24,
      PICKER_Y + 80,
      `${this.state.months_per_run}개월을 모두 보냈습니다.`,
      { fontSize: '18px', color: '#cfd2e6' },
    );

    const summary = STAT_NAMES.map(
      (stat) => `${statLabel(stat)} ${this.state.stats[stat]}`,
    ).join('   ');
    this.text(x + 24, PICKER_Y + 124, summary, {
      fontSize: '20px',
      fontStyle: 'bold',
      wordWrap: { width: width - 48 },
    });
  }

  renderMessage() {
    const isError = !!this.message;
    const text = this.message || this.lastMonthSummary();
    if (!text) return;

    this.text(CANVAS_WIDTH / 2, 526, text, {
      fontSize: '16px',
      color: isError ? '#ffd7d7' : '#cfd2e6',
      backgroundColor: isError ? '#5a1111' : '#1c1e33',
      padding: { x: 10, y: 4 },
      wordWrap: { width: CANVAS_WIDTH - 96 },
      align: 'center',
    }).setOrigin(0.5, 0);
  }

  lastMonthSummary() {
    if (this.deltas.length === 0) return '';
    return `지난 달 변화  ${this.deltas
      .map(({ stat, delta }) => `${statLabel(stat)}${formatDelta(delta)}`)
      .join('  ')}`;
  }

  panel(x, y, width, height, alpha = PANEL_ALPHA) {
    const rect = this.add
      .rectangle(x, y, width, height, PANEL_FILL, alpha)
      .setOrigin(0, 0)
      .setStrokeStyle(1, 0xffffff, 0.25);
    this.ui.add(rect);
    return rect;
  }

  text(x, y, value, style = {}) {
    const text = this.add.text(x, y, value, {
      fontFamily: 'sans-serif',
      fontSize: '18px',
      color: '#ffffff',
      ...style,
    });
    this.ui.add(text);
    return text;
  }

  choiceButton(x, y, width, height, label, selected, onClick) {
    const fill = selected ? CHOICE_SELECTED_FILL : CHOICE_FILL;
    const button = this.add
      .rectangle(x, y, width, height, fill, 1)
      .setOrigin(0, 0)
      .setStrokeStyle(selected ? 2 : 1, 0xffffff, selected ? 0.9 : 0.3);
    this.ui.add(button);
    this.text(x + width / 2, y + height / 2, label, {
      fontSize: '17px',
      fontStyle: selected ? 'bold' : 'normal',
    }).setOrigin(0.5);

    button.setInteractive({ useHandCursor: true });
    button.on('pointerover', () => button.setFillStyle(selected ? 0x4d9a6e : 0x393c5e, 1));
    button.on('pointerout', () => button.setFillStyle(fill, 1));
    button.on('pointerdown', onClick);
    return button;
  }
}
