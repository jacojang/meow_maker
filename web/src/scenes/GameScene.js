import Phaser from 'phaser';
import { daySlots } from '../utils/calendar.js';
import { coverScale } from '../utils/coverScale.js';
import { gameApi } from '../utils/gameApi.js';
import { fitStep } from '../utils/layout.js';
import { portraitKey } from '../utils/portrait.js';
import { resolutionSteps } from '../utils/resolutionSteps.js';
import { STAT_NAMES, formatDelta, statDeltas } from '../utils/statDeltas.js';
import { addFullscreenButton } from './fullscreenButton.js';

const DAYS_PER_MONTH = 30;
const RESOLUTION_STEP_MS = 700;
const DIET_VIGNETTE_COLOR = 0x8a8f4d;

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

const ACTIVITY_COLORS = {
  play: 0xdc8a3c,
  train: 0x3c6fdc,
  groom: 0xb15fc9,
  rest: 0x3ca6a0,
  educate: 0x7ec93c,
};

const ACTIVITY_FLAVOR = {
  play: '신나게 뛰어놀며 하루를 보냈다.',
  train: '진지한 얼굴로 훈련에 몰두했다.',
  groom: '단정하게 털을 골랐다.',
  rest: '햇살 아래서 늘어지게 낮잠을 잤다.',
  educate: '새로운 것을 배우며 눈을 반짝였다.',
};

const DIET_FLAVOR = {
  normal: '적당히 챙겨 먹었다.',
  light: '가볍게 먹으며 몸매를 관리했다.',
  hearty: '든든하게 배를 채웠다.',
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

function activityColor(id) {
  return ACTIVITY_COLORS[id] ?? CHOICE_FILL;
}

function activityFlavor(id) {
  return ACTIVITY_FLAVOR[id] ?? '';
}

function dietFlavor(id) {
  return DIET_FLAVOR[id] ?? '';
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
    this.focusedSlot = 0;
    this.dietPick = this.diets[0]?.id ?? 'normal';
    this.deltas = [];
    this.hasPlayedMonth = false;
    this.message = '';
    this.busy = false;
    this.animating = false;
    this.animationSteps = [];
    this.animationIndex = 0;
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

      try {
        await this.playResolutionAnimation();
      } catch {
        // The animation is cosmetic only; never let it mask an
        // already-successful advance with a false error message.
      }

      if (!this.alive) return;
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

  buildResolutionSteps() {
    return resolutionSteps(
      DAYS_PER_MONTH,
      this.picks,
      this.activities,
      this.dietPick,
      this.diets,
    ).map((step) => ({
      ...step,
      label: step.kind === 'diet' ? dietLabel(step.id) : activityLabel(step.id),
      flavor: step.kind === 'diet' ? dietFlavor(step.id) : activityFlavor(step.id),
      color: step.kind === 'diet' ? DIET_VIGNETTE_COLOR : activityColor(step.id),
      effectsText: effectsSummary(step.effects),
    }));
  }

  async playResolutionAnimation() {
    this.animationSteps = this.buildResolutionSteps();
    this.animating = true;
    for (let index = 0; index < this.animationSteps.length; index += 1) {
      if (!this.alive) return;
      this.animationIndex = index;
      this.render();
      await this.delay(RESOLUTION_STEP_MS);
    }
    this.animating = false;
  }

  delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
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
    } else if (this.animating) {
      this.renderResolutionOverlay();
      this.renderPlayButton();
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
    this.renderCalendar();
    this.renderCalendarChoices();
    this.renderDietPicker();
  }

  renderCalendar() {
    const x = PICKER_COLUMN_X[0];
    const width =
      PICKER_COLUMN_X[2] + PICKER_COLUMN_WIDTH - PICKER_COLUMN_X[0];
    this.panel(x, PICKER_Y, width, PICKER_HEIGHT);
    this.text(x + 16, PICKER_Y + 10, '이번 달 일정', { fontStyle: 'bold' });

    const slots = daySlots(DAYS_PER_MONTH, this.picks.length);
    const labelWidth = 132;
    const cellGap = 3;
    const rowsTop = PICKER_Y + 40;
    const rowHeight = Math.min(32, (this.calendarChoicesY() - 8 - rowsTop) / slots.length);

    slots.forEach((range, slot) => {
      const y = rowsTop + slot * rowHeight;
      const pick = this.picks[slot];
      const focused = this.focusedSlot === slot;
      const cellsWidth = width - 32 - labelWidth;
      const cellWidth = (cellsWidth - cellGap * (range.days.length - 1)) / range.days.length;

      const label = this.text(
        x + 16,
        y + (rowHeight - 6) / 2,
        `${range.start}~${range.end}일  ${activityLabel(pick)}`,
        {
          fontSize: '13px',
          color: focused ? '#ffd479' : '#cfd2e6',
          fontStyle: focused ? 'bold' : 'normal',
        },
      ).setOrigin(0, 0.5);
      label.setInteractive({ useHandCursor: true });
      label.on('pointerdown', () => this.focusSlot(slot));

      range.days.forEach((day, index) => {
        const cellX = x + 16 + labelWidth + index * (cellWidth + cellGap);
        const fill = activityColor(pick);
        const cell = this.add
          .rectangle(cellX, y, cellWidth, rowHeight - 6, fill, focused ? 1 : 0.5)
          .setOrigin(0, 0)
          .setStrokeStyle(focused ? 2 : 1, 0xffffff, focused ? 0.9 : 0.25);
        this.ui.add(cell);
        this.text(cellX + cellWidth / 2, y + (rowHeight - 6) / 2, `${day}`, {
          fontSize: '10px',
          color: '#10111c',
        }).setOrigin(0.5);

        cell.setInteractive({ useHandCursor: true });
        cell.on('pointerover', () => cell.setFillStyle(fill, 1));
        cell.on('pointerout', () => cell.setFillStyle(fill, focused ? 1 : 0.5));
        cell.on('pointerdown', () => this.focusSlot(slot));
      });
    });
  }

  calendarChoicesY() {
    return PICKER_Y + PICKER_HEIGHT - 48;
  }

  renderCalendarChoices() {
    const x = PICKER_COLUMN_X[0];
    const width =
      PICKER_COLUMN_X[2] + PICKER_COLUMN_WIDTH - PICKER_COLUMN_X[0];
    const y = this.calendarChoicesY();
    const gap = 8;
    const buttonWidth =
      (width - 32 - gap * (this.activities.length - 1)) / this.activities.length;
    const pick = this.picks[this.focusedSlot];

    this.activities.forEach((activity, index) => {
      this.choiceButton(
        x + 16 + index * (buttonWidth + gap),
        y,
        buttonWidth,
        36,
        activityLabel(activity.id),
        activity.id === pick,
        () => this.choose(this.focusedSlot, activity.id),
      );
    });
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

  renderResolutionOverlay() {
    const x = PICKER_COLUMN_X[0];
    const width = CANVAS_WIDTH - 48;
    const step = this.animationSteps[this.animationIndex];
    if (!step) return;

    this.panel(x, PICKER_Y, width, PICKER_HEIGHT);
    this.text(
      x + 16,
      PICKER_Y + 10,
      `한 달을 보내는 중… (${this.animationIndex + 1}/${this.animationSteps.length})`,
      { fontStyle: 'bold', color: '#ffd479' },
    );

    const vignetteWidth = 220;
    const vignetteHeight = PICKER_HEIGHT - 60;
    const vignetteX = x + 16;
    const vignetteY = PICKER_Y + 44;
    this.ui.add(
      this.add
        .rectangle(vignetteX, vignetteY, vignetteWidth, vignetteHeight, step.color, 0.9)
        .setOrigin(0, 0)
        .setStrokeStyle(2, 0xffffff, 0.6),
    );
    this.text(vignetteX + vignetteWidth / 2, vignetteY + vignetteHeight / 2, step.label, {
      fontSize: '26px',
      fontStyle: 'bold',
      color: '#10111c',
      align: 'center',
      wordWrap: { width: vignetteWidth - 24 },
    }).setOrigin(0.5);

    const textX = vignetteX + vignetteWidth + 24;
    this.text(textX, vignetteY + 4, step.title, { fontSize: '20px', fontStyle: 'bold' });
    this.text(textX, vignetteY + 40, step.flavor, {
      fontSize: '16px',
      color: '#e7e9f5',
      wordWrap: { width: width - vignetteWidth - 64 },
    });
    this.text(textX, vignetteY + 90, step.effectsText, { fontSize: '14px', color: '#cfd2e6' });
  }

  choose(slot, activityId) {
    if (this.busy) return;
    this.picks[slot] = activityId;
    this.render();
  }

  focusSlot(slot) {
    if (this.busy) return;
    this.focusedSlot = slot;
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
