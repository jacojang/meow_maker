import Phaser from 'phaser';
import { daySlots } from '../utils/calendar.js';
import { calendarWeeks, WEEKDAY_LABELS } from '../utils/calendarGrid.js';
import {
  CARE_NONE_LABEL,
  careAffordable,
  careButtonLabel,
  careCharge,
  careHint,
  careResultCopy,
  sendableCare,
} from '../utils/care.js';
import { coverScale } from '../utils/coverScale.js';
import {
  SKIP_LABEL,
  contestRowLabel,
  contestRows,
  festivalCardCopy,
  festivalStage,
  sendableContest,
} from '../utils/festival.js';
import { dateForDay, daysInMonth, formatDate, seasonForMonth } from '../utils/gameCalendar.js';
import { gameApi } from '../utils/gameApi.js';
import {
  FINAL_REVEAL_STEP,
  initialRevealStep,
  isFinalRevealStep,
  nextRevealStep,
  revealed,
  rollTotalTicks,
  rolledValues,
} from '../utils/endingReveal.js';
import { endingFlavor, endingLabel } from '../utils/endingText.js';
import { fitStep } from '../utils/layout.js';
import {
  UNAFFORDABLE_LINE,
  affordablePicks,
  buildMoneySteps,
  canAffordPick,
  priceLabel,
} from '../utils/money.js';
import { portraitKey, portraitKeyCandidates } from '../utils/portrait.js';
import { placeLegacyPortrait, placePortrait } from '../utils/portraitPlacement.js';
import { buildResultCards } from '../utils/resultCards.js';
import { OUTCOME_COLORS, OUTCOME_TINTS, buildDaySteps } from '../utils/dayLog.js';
import { SPEEDS, dayDelayMs, saveSpeed, startingSpeed } from '../utils/playbackSpeed.js';
import { STAT_NAMES, formatDelta, statDeltas } from '../utils/statDeltas.js';
import { isPickerLocked, lockedPicks, statusBadges, topWarning } from '../utils/status.js';
import { addFullscreenButton } from './fullscreenButton.js';

const RESOLUTION_STEP_MS = 700;
const PORTRAIT_GROUND_MARGIN = 6;
const FRAME_SUFFIXES = ['', '-b', '-c', '-d', '-e'];
const FRAME_PING_PONG = [0, 1, 2, 3, 4, 3, 2, 1];
const SPEED_LABELS = { normal: '보통', fast: '빠르게', skip: '건너뛰기' };
const DIET_VIGNETTE_COLOR = 0x8a8f4d;

const CANVAS_WIDTH = 960;
const CANVAS_HEIGHT = 750;

const COLUMN_X = [24, 504];
const COLUMN_WIDTH = 432;
const TOP_PANEL_Y = 80;
const TOP_PANEL_HEIGHT = 358;
const PICKER_Y = 454;
const PICKER_HEIGHT = 216;

const PICKER_COLUMN_X = [24, 256, 488, 720];
const PICKER_COLUMN_WIDTH = 216;
const PLAY_BUTTON_Y = 710;
const DIET_PANEL_HEIGHT = 76;
const PANEL_GAP = 6;
const CARE_BUTTON_HEIGHT = 30;

const CORE_STATS = STAT_NAMES.slice(0, 5);
const REVEAL_STEP_MS = 1800;
const ROLL_TICK_MS = 50;

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
  outing: '나들이',
  job: '쥐잡이 알바',
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
  outing: 0xe0708a,
  job: 0xc9a23c,
};

const ACTIVITY_FLAVOR = {
  play: '신나게 뛰어놀며 하루를 보냈다.',
  train: '진지한 얼굴로 훈련에 몰두했다.',
  groom: '단정하게 털을 골랐다.',
  rest: '햇살 아래서 늘어지게 낮잠을 잤다.',
  educate: '새로운 것을 배우며 눈을 반짝였다.',
  outing: '설레는 마음으로 나들이를 떠났다.',
  job: '쥐를 잡으며 부지런히 일당을 벌었다.',
};

const DIET_FLAVOR = {
  normal: '적당히 챙겨 먹었다.',
  light: '가볍게 먹으며 몸매를 관리했다.',
  hearty: '든든하게 배를 채웠다.',
};

const EVENT_COPY = {
  visitor: { title: '손님 방문', body: '반가운 손님이 찾아와 고양이를 쓰다듬어 주었다.' },
  good_mood: { title: '기분 좋은 날', body: '고양이가 기분 좋게 그르렁거렸다.' },
  bad_mood: { title: '심술 난 날', body: '고양이가 괜히 심술을 부렸다.' },
  mishap: { title: '말썽', body: '고양이가 집안에서 한바탕 사고를 쳤다.' },
  gift: { title: '선물', body: '누군가 고양이에게 선물을 두고 갔다.' },
};

const OUTING_COPY = {
  success: { title: '나들이 성공', body: '즐거운 나들이를 무사히 마치고 돌아왔다.' },
  failure: { title: '나들이 실패', body: '나들이 중에 일이 꼬여 지친 채 돌아왔다.' },
};

const STATUS_BADGE_STYLE = {
  delinquent: { label: '말썽', fill: 0xb5651d },
  overweight: { label: '통통', fill: 0x8a6d1d },
  bedridden: { label: '앓아누움', fill: 0x6b2d6b },
};

const ADVISOR_TEXT = {
  near_sick: '조심하세요. 스트레스가 쌓여 곧 아플지도 몰라요.',
  sick: '고양이가 아파요. 푹 쉬게 해 주세요.',
  near_delinquent: '규율에 비해 스트레스가 높아요. 말썽을 부릴지도 몰라요.',
  delinquent: '고양이가 말썽을 부리고 있어요. 스트레스를 풀어 주세요.',
  overweight: '조금 통통해졌어요. 식단을 살펴보세요.',
  hospital_risk: '위험해요! 이번 달에 낫지 않으면 입원할 수도 있어요.',
  runaway_risk: '위험해요! 말썽이 이번 달에도 이어지면 집을 나갈지도 몰라요.',
};

const BEDRIDDEN_PICKER_TEXT = '푹 쉬어야 해요';

const FESTIVAL_TITLE = '수확 축제 · 참가할 대회를 고르세요';
const FESTIVAL_BACK_LABEL = '← 대회 고르기';
const FESTIVAL_ENTER_LABEL = '대회 참가';

function cardCopy(card) {
  if (card.kind === 'care') return careResultCopy(card);
  if (card.kind === 'outing') return OUTING_COPY[card.key];
  if (card.kind === 'event') return EVENT_COPY[card.key] ?? { title: card.key, body: '' };
  return festivalCardCopy(card);
}

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
    this.care = data?.care ?? [];
    this.festival = data?.festival ?? null;
    this.contestChoice = null;
    this.carePick = null;
    this.eventTable = data?.events ?? [];
    this.resultCards = [];
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
    this.animationFrameIndex = 0;
    this.speed = 'normal';
    this.showActivityInfo = false;
    this.endingStep = initialRevealStep(false);
    this.rollTick = rollTotalTicks(CORE_STATS.length);
    this.revealToken = 0;
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
    if (this.busy) return;
    const stage = this.festivalStage();
    if (stage === 'choose') return;
    const contest = sendableContest(stage, this.contestChoice);
    this.picks = lockedPicks(this.state, this.picks);
    if (!isPickerLocked(this.state) && !contest) {
      this.picks = affordablePicks(this.scheduleBudget(), this.activities, this.picks);
    }
    if (this.picks.length === 0) return;
    const sentPicks = contest ? [] : this.picks;
    const care = sendableCare(this.carePick, this.care, this.state, this.activities, sentPicks);

    const before = this.state?.stats;
    const processedMonth = this.state?.month;
    this.busy = true;
    this.message = '';
    this.render();

    try {
      const next = await this.api.advanceMonth([...sentPicks], this.dietPick, care, contest);

      try {
        await this.playResolutionAnimation(next, before);
      } catch {
        // The animation is cosmetic only; never let it mask an
        // already-successful advance with a false error message.
      }

      if (!this.alive) return;
      this.deltas = statDeltas(before, next.stats);
      this.hasPlayedMonth = true;
      this.state = next;
      this.resultCards = buildResultCards({
        processedMonth,
        state: next,
        events: this.eventTable,
      });
      if (next.finished) this.startEndingReveal();
    } catch (error) {
      this.message = describeError(error);
    } finally {
      this.carePick = null;
      this.contestChoice = null;
      this.busy = false;
      this.safeRender();
    }
  }

  festivalStage() {
    return festivalStage(this.state, this.festival, this.contestChoice);
  }

  scheduleBudget() {
    const money = this.state?.money ?? 0;
    const entry = this.care.find((candidate) => candidate.id === this.carePick);
    return money - careCharge(entry, this.state);
  }

  buildResolutionSteps(next, before) {
    const moneySteps = buildMoneySteps(next.last_month_log, this.state.money ?? 0);
    const days = buildDaySteps(next.last_month_log, before, this.activities).map((step, index) => ({
      ...step,
      money: moneySteps[index]?.money,
      moneyDelta: moneySteps[index]?.delta ?? 0,
      kind: 'day',
      label: activityLabel(step.activityId),
      color: activityColor(step.activityId),
      textureKey: `scene-${step.activityId}`,
    }));
    const diet = this.diets.find((entry) => entry.id === this.dietPick);
    const dietStep = {
      kind: 'diet',
      id: this.dietPick,
      title: '식단',
      label: dietLabel(this.dietPick),
      flavor: dietFlavor(this.dietPick),
      color: DIET_VIGNETTE_COLOR,
      effectsText: effectsSummary(diet?.effects),
      textureKey: `cat-${portraitKey(this.state.stats, this.state.is_sick)}`,
    };
    return [...days, dietStep];
  }

  setSpeed(speed) {
    this.speed = speed;
    saveSpeed(speed);
    if (this.alive && this.animating) this.render();
  }

  async playResolutionAnimation(next, before) {
    this.animationSteps = this.buildResolutionSteps(next, before);
    this.speed = startingSpeed(this.hasPlayedMonth);
    this.animating = true;
    try {
      for (let index = 0; index < this.animationSteps.length; index += 1) {
        if (!this.alive || this.speed === 'skip') return;
        this.animationIndex = index;
        const step = this.animationSteps[index];
        this.animationFrameIndex =
          step.kind === 'day' ? FRAME_PING_PONG[step.dayInSlot % FRAME_PING_PONG.length] : 0;
        this.render();
        await this.delay(step.kind === 'day' ? dayDelayMs(this.speed) : RESOLUTION_STEP_MS);
      }
    } finally {
      this.animating = false;
    }
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

    this.picks = lockedPicks(this.state, this.picks);
    if (!isPickerLocked(this.state) && !this.state.finished) {
      this.picks = affordablePicks(this.scheduleBudget(), this.activities, this.picks);
    }
    this.renderStats();
    this.renderPortrait();

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

    if (this.showActivityInfo) {
      this.renderActivityInfoPopup();
    }

    if (this.resultCards.length > 0) {
      this.renderResultCard(this.resultCards[0]);
    }
  }

  dismissResultCard() {
    this.resultCards.shift();
    this.render();
  }

  renderResultCard(card) {
    const copy = cardCopy(card);
    const backdrop = this.add
      .rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, 0x000000, 0.6)
      .setOrigin(0, 0)
      .setInteractive({ useHandCursor: true });
    backdrop.on('pointerdown', () => this.dismissResultCard());
    this.ui.add(backdrop);

    const width = 560;
    const height = copy.lines ? 400 : 300;
    const x = (CANVAS_WIDTH - width) / 2;
    const y = (CANVAS_HEIGHT - height) / 2;
    this.panel(x, y, width, height, 1);
    this.text(CANVAS_WIDTH / 2, y + 24, copy.title, {
      fontSize: '26px',
      fontStyle: 'bold',
      color: '#ffd479',
    }).setOrigin(0.5, 0);
    this.text(CANVAS_WIDTH / 2, y + 78, copy.body, {
      fontSize: '18px',
      wordWrap: { width: width - 64 },
      align: 'center',
    }).setOrigin(0.5, 0);

    if (copy.lines) {
      copy.lines.forEach((line, index) => {
        this.text(CANVAS_WIDTH / 2, y + 130 + index * 28, line, { fontSize: '18px' }).setOrigin(0.5, 0);
      });
      this.text(CANVAS_WIDTH / 2, y + 130 + copy.lines.length * 28 + 12, copy.footer, {
        fontSize: '18px',
        fontStyle: 'bold',
        color: '#ffd479',
      }).setOrigin(0.5, 0);
    }

    const effects = card.chips ?? {};
    STAT_NAMES.filter((stat) => stat in effects).forEach((stat, index) => {
      const delta = effects[stat];
      this.text(x + 40 + index * 120, y + 160, `${statLabel(stat)}${formatDelta(delta)}`, {
        fontSize: '17px',
        fontStyle: 'bold',
        color: (stat === 'stress' ? delta < 0 : delta > 0) ? '#8fe0a8' : '#ff9a9a',
      });
    });

    this.text(CANVAS_WIDTH / 2, y + height - 36, '클릭해서 계속', {
      fontSize: '14px',
      color: '#9a9db8',
    }).setOrigin(0.5, 0);
  }

  renderHeader() {
    this.panel(0, 0, CANVAS_WIDTH, 64, 1);
    this.text(24, 18, 'Meow Maker', { fontSize: '24px', fontStyle: 'bold' });

    if (!this.state) return;

    const animationDay = this.animating ? this.animationSteps[this.animationIndex]?.day : null;
    const displayDate = animationDay
      ? dateForDay(this.state.month, animationDay)
      : this.state.finished
        ? dateForDay(this.state.month, daysInMonth(this.state.month))
        : dateForDay(this.state.month, 1);
    this.text(CANVAS_WIDTH - 24, 18, formatDate(displayDate), {
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
    this.renderActivityInfoButton(x + COLUMN_WIDTH - 28, TOP_PANEL_Y + 22);
    this.text(x + COLUMN_WIDTH - 52, TOP_PANEL_Y + 12, `소지금 ${this.displayMoney()}`, {
      fontSize: '17px',
      fontStyle: 'bold',
      color: '#ffd479',
    }).setOrigin(1, 0);

    const step = fitStep(STAT_NAMES.length, 44, TOP_PANEL_HEIGHT - 58);
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

  displayMoney() {
    const step = this.animating ? this.animationSteps[this.animationIndex] : null;
    return step?.money ?? this.state.money ?? 0;
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

    const areaTop = TOP_PANEL_Y + 40;
    const areaHeight = TOP_PANEL_HEIGHT - 52;
    const areaWidth = COLUMN_WIDTH - 24;
    const areaLeft = x + 12;
    const areaCenterX = x + COLUMN_WIDTH / 2;
    const areaCenterY = areaTop + areaHeight / 2;

    const seasonKey = `season-${seasonForMonth(this.state.month)}`;
    if (this.textures.exists(seasonKey)) {
      const bg = this.add.image(areaCenterX, areaCenterY, seasonKey);
      bg.setScale(coverScale(areaWidth, areaHeight, bg.width, bg.height));
      this.ui.add(bg);

      const maskShape = this.add.graphics();
      maskShape.fillStyle(0xffffff);
      maskShape.fillRect(areaLeft, areaTop, areaWidth, areaHeight);
      maskShape.setVisible(false);
      this.ui.add(maskShape);
      bg.setMask(maskShape.createGeometryMask());
    }

    this.renderAdvisor(areaLeft, areaTop, areaWidth);
    this.renderStatusBadges(areaLeft + 8, areaTop + areaHeight - 30);

    const textureKey = portraitKeyCandidates(
      this.state.stats,
      this.state.is_sick,
      this.state.is_bedridden,
      this.state.warnings,
    )
      .map((key) => `cat-${key}`)
      .find((key) => this.textures.exists(key));
    if (!textureKey) return;

    const area = {
      centerX: areaCenterX,
      floorY: areaTop + areaHeight - PORTRAIT_GROUND_MARGIN,
      width: areaWidth,
      height: areaHeight,
    };
    const portraitKeyName = textureKey.replace(/^cat-/, '');
    const source = this.textures.get(textureKey).getSourceImage();
    const placement =
      placePortrait(portraitKeyName, area) ?? placeLegacyPortrait(area, source);

    if (placement.shadow) {
      const { x, y, width, height, alpha } = placement.shadow;
      const shadow = this.add.ellipse(x, y, width, height, 0x000000, alpha);
      this.ui.add(shadow);
    }
    const image = this.add.image(placement.x, placement.y, textureKey);
    image.setScale(placement.scale);
    image.setOrigin(placement.originX, placement.originY);
    this.ui.add(image);
  }

  renderAdvisor(left, top, width) {
    const code = topWarning(this.state.warnings);
    if (!code || this.animating) return;
    this.text(left + width / 2, top + 6, ADVISOR_TEXT[code], {
      fontSize: '15px',
      color: '#ffe9b0',
      backgroundColor: '#1c1e33',
      padding: { x: 8, y: 4 },
      wordWrap: { width: width - 24 },
      align: 'center',
    }).setOrigin(0.5, 0);
  }

  renderStatusBadges(x, y) {
    let offset = 0;
    statusBadges(this.state)
      .filter((id) => id in STATUS_BADGE_STYLE)
      .forEach((id) => {
        const { label, fill } = STATUS_BADGE_STYLE[id];
        const chip = this.add
          .rectangle(x + offset, y, 64, 24, fill, 1)
          .setOrigin(0, 0)
          .setStrokeStyle(1, 0xffffff, 0.6);
        this.ui.add(chip);
        this.text(x + offset + 32, y + 12, label, { fontSize: '14px', fontStyle: 'bold' }).setOrigin(
          0.5,
        );
        offset += 72;
      });
  }

  renderActivityInfoButton(x, y) {
    const radius = 12;
    const bg = this.add
      .circle(x, y, radius, 0x2a2c48, 1)
      .setStrokeStyle(1, 0xffffff, 0.5)
      .setInteractive({ useHandCursor: true });
    this.ui.add(bg);
    this.text(x, y, 'i', { fontSize: '14px', fontStyle: 'bold italic', color: '#ffd479' }).setOrigin(
      0.5,
    );

    bg.on('pointerover', () => bg.setFillStyle(0x393c5e, 1));
    bg.on('pointerout', () => bg.setFillStyle(0x2a2c48, 1));
    bg.on('pointerdown', () => this.openActivityInfo());
  }

  openActivityInfo() {
    this.showActivityInfo = true;
    this.render();
  }

  closeActivityInfo() {
    this.showActivityInfo = false;
    this.render();
  }

  renderActivityInfoPopup() {
    const backdrop = this.add
      .rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, 0x000000, 0.6)
      .setOrigin(0, 0)
      .setInteractive();
    backdrop.on('pointerdown', () => this.closeActivityInfo());
    this.ui.add(backdrop);

    const width = 520;
    const height = 340;
    const x = (CANVAS_WIDTH - width) / 2;
    const y = (CANVAS_HEIGHT - height) / 2;

    const modal = this.panel(x, y, width, height, 0.98);
    modal.setInteractive();

    this.text(x + 20, y + 16, '활동 효과', { fontSize: '20px', fontStyle: 'bold' });
    this.renderActivityEffectsList(x + 20, y + 56, width - 40, height - 96);
    this.renderCloseButton(x + width - 20, y + 16);
  }

  renderActivityEffectsList(x, y, width, availableHeight) {
    const step = fitStep(this.activities.length, 40, availableHeight);
    const effectOffset = Math.min(18, step - 14);
    this.activities.forEach((activity, index) => {
      const rowY = y + index * step;
      this.text(x, rowY, activityLabel(activity.id), {
        fontSize: '17px',
        fontStyle: 'bold',
        color: '#ffd479',
      });
      this.text(x, rowY + effectOffset, `${effectsSummary(activity.effects)}  ·  ${priceLabel(activity)}`, {
        fontSize: '14px',
        color: '#cfd2e6',
        wordWrap: { width },
      });
    });
  }

  renderCloseButton(rightX, topY) {
    const size = 24;
    const bg = this.add
      .rectangle(rightX, topY, size, size, 0x2a2c48, 1)
      .setOrigin(1, 0)
      .setStrokeStyle(1, 0xffffff, 0.4)
      .setInteractive({ useHandCursor: true });
    this.ui.add(bg);
    this.text(rightX - size / 2, topY + size / 2, '✕', { fontSize: '14px' }).setOrigin(0.5);

    bg.on('pointerover', () => bg.setFillStyle(0x393c5e, 1));
    bg.on('pointerout', () => bg.setFillStyle(0x2a2c48, 1));
    bg.on('pointerdown', () => this.closeActivityInfo());
  }

  renderPickers() {
    const stage = this.festivalStage();
    if (stage === 'choose' || stage === 'enter' || stage === 'locked') {
      this.renderFestivalPanel(stage);
    } else {
      this.renderCalendar();
      this.renderCalendarChoices();
      if (stage === 'skip') this.renderFestivalBackButton();
    }
    this.renderDietPicker();
  }

  festivalPanelWidth() {
    return PICKER_COLUMN_X[2] + PICKER_COLUMN_WIDTH - PICKER_COLUMN_X[0];
  }

  renderFestivalPanel(stage) {
    const x = PICKER_COLUMN_X[0];
    const width = this.festivalPanelWidth();
    this.panel(x, PICKER_Y, width, PICKER_HEIGHT);
    this.text(x + 16, PICKER_Y + 10, FESTIVAL_TITLE, { fontStyle: 'bold' });

    const locked = stage === 'locked';
    const rowHeight = 30;
    const rowStep = rowHeight + 4;
    const rows = contestRows(this.festival, this.state.stats);
    rows.forEach((row, index) => {
      this.choiceButton(
        x + 16,
        PICKER_Y + 38 + index * rowStep,
        width - 32,
        rowHeight,
        contestRowLabel(row),
        this.contestChoice === row.id,
        () => (locked ? this.refuseFestival() : this.chooseContest(row.id)),
        { fontSize: '15px', dimmed: locked },
      );
    });
    this.choiceButton(
      x + 16,
      PICKER_Y + 38 + rows.length * rowStep,
      width - 32,
      rowHeight,
      SKIP_LABEL,
      false,
      () => (locked ? this.refuseFestival() : this.chooseContest('skip')),
      { fontSize: '15px', dimmed: locked },
    );
    if (locked) {
      this.text(x + width - 16, PICKER_Y + 10, BEDRIDDEN_PICKER_TEXT, {
        fontSize: '16px',
        fontStyle: 'bold',
        color: '#ffb4e8',
      }).setOrigin(1, 0);
    }
  }

  renderFestivalBackButton() {
    const x = PICKER_COLUMN_X[0] + this.festivalPanelWidth() - 16;
    const label = this.text(x, PICKER_Y + 10, FESTIVAL_BACK_LABEL, {
      fontSize: '14px',
      color: '#ffd479',
    }).setOrigin(1, 0);
    label.setInteractive({ useHandCursor: true });
    label.on('pointerdown', () => this.chooseContest(null));
  }

  chooseContest(choice) {
    if (this.busy) return;
    this.contestChoice = choice;
    this.message = '';
    this.render();
  }

  refuseFestival() {
    if (this.busy) return;
    this.message = BEDRIDDEN_PICKER_TEXT;
    this.render();
  }

  renderCalendar() {
    const x = PICKER_COLUMN_X[0];
    const width =
      PICKER_COLUMN_X[2] + PICKER_COLUMN_WIDTH - PICKER_COLUMN_X[0];
    this.panel(x, PICKER_Y, width, PICKER_HEIGHT);
    this.text(x + 16, PICKER_Y + 10, '이번 달 일정', { fontStyle: 'bold' });

    this.renderCalendarLegend(x, width);
    this.renderCalendarWeekdayHeader(x, width);
    this.renderCalendarGrid(x, width);
  }

  renderCalendarLegend(x, width) {
    const ranges = daySlots(daysInMonth(this.state.month), this.picks.length);
    const y = PICKER_Y + 38;
    const gap = 8;
    const chipWidth = (width - 32 - gap * (ranges.length - 1)) / ranges.length;

    ranges.forEach((range, slot) => {
      const pick = this.picks[slot];
      const focused = this.focusedSlot === slot;
      const chipX = x + 16 + slot * (chipWidth + gap);

      const swatch = this.add
        .rectangle(chipX, y, 10, 10, activityColor(pick), 1)
        .setOrigin(0, 0.5);
      this.ui.add(swatch);

      const label = this.text(
        chipX + 16,
        y,
        `${range.start}~${range.end}일 ${activityLabel(pick)}`,
        {
          fontSize: '12px',
          color: focused ? '#ffd479' : '#cfd2e6',
          fontStyle: focused ? 'bold' : 'normal',
        },
      ).setOrigin(0, 0.5);
      label.setInteractive({ useHandCursor: true });
      label.on('pointerdown', () => this.focusSlot(slot));
    });
  }

  renderCalendarWeekdayHeader(x, width) {
    const y = PICKER_Y + 58;
    const cellWidth = (width - 32) / 7;

    WEEKDAY_LABELS.forEach((label, index) => {
      this.text(x + 16 + index * cellWidth + cellWidth / 2, y, label, {
        fontSize: '11px',
        color: index === 0 ? '#e08a8a' : '#9ea1c2',
      }).setOrigin(0.5);
    });
  }

  renderCalendarGrid(x, width) {
    const ranges = daySlots(daysInMonth(this.state.month), this.picks.length);
    const weeks = calendarWeeks(this.state.month, ranges);
    const cellGap = 2;
    const cellWidth = (width - 32) / 7;
    const rowsTop = PICKER_Y + 72;
    const rowHeight = fitStep(weeks.length, 22, this.calendarChoicesY() - 8 - rowsTop);

    weeks.forEach((week, rowIndex) => {
      const y = rowsTop + rowIndex * rowHeight;

      week.forEach((cell, colIndex) => {
        if (!cell) return;
        const slot = cell.slotIndex;
        const pick = this.picks[slot];
        const focused = this.focusedSlot === slot;
        const cellX = x + 16 + colIndex * cellWidth;
        const fill = activityColor(pick);

        const box = this.add
          .rectangle(cellX, y, cellWidth - cellGap, rowHeight - cellGap, fill, focused ? 1 : 0.5)
          .setOrigin(0, 0)
          .setStrokeStyle(focused ? 2 : 1, 0xffffff, focused ? 0.9 : 0.25);
        this.ui.add(box);
        this.text(cellX + (cellWidth - cellGap) / 2, y + (rowHeight - cellGap) / 2, `${cell.day}`, {
          fontSize: '10px',
          color: '#10111c',
        }).setOrigin(0.5);

        box.setInteractive({ useHandCursor: true });
        box.on('pointerover', () => box.setFillStyle(fill, 1));
        box.on('pointerout', () => box.setFillStyle(fill, focused ? 1 : 0.5));
        box.on('pointerdown', () => this.focusSlot(slot));
      });
    });
  }

  calendarChoicesY() {
    return PICKER_Y + PICKER_HEIGHT - 56;
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

    if (isPickerLocked(this.state)) {
      this.text(x + width / 2, y + 18, BEDRIDDEN_PICKER_TEXT, {
        fontSize: '20px',
        fontStyle: 'bold',
        color: '#ffb4e8',
      }).setOrigin(0.5);
      return;
    }

    this.activities.forEach((activity, index) => {
      const affordable = canAffordPick(
        this.scheduleBudget(),
        this.activities,
        this.picks,
        this.focusedSlot,
        activity.id,
      );
      this.choiceButton(
        x + 16 + index * (buttonWidth + gap),
        y,
        buttonWidth,
        44,
        activityLabel(activity.id),
        activity.id === pick,
        () =>
          affordable
            ? this.choose(this.focusedSlot, activity.id)
            : this.refuseChoice(),
        {
          fontSize: '15px',
          sublabel: priceLabel(activity),
          sublabelColor: affordable ? '#cfd2e6' : '#ff7a7a',
          dimmed: !affordable,
        },
      );
    });
  }

  renderDietPicker() {
    const x = PICKER_COLUMN_X[3];
    this.panel(x, PICKER_Y, PICKER_COLUMN_WIDTH, DIET_PANEL_HEIGHT);
    this.text(x + 16, PICKER_Y + 8, '식단', { fontStyle: 'bold', fontSize: '15px' });

    const gap = 6;
    const width = (PICKER_COLUMN_WIDTH - 32 - gap * (this.diets.length - 1)) / this.diets.length;
    this.diets.forEach((diet, index) => {
      this.choiceButton(
        x + 16 + index * (width + gap),
        PICKER_Y + 34,
        width,
        CARE_BUTTON_HEIGHT,
        dietLabel(diet.id),
        diet.id === this.dietPick,
        () => this.chooseDiet(diet.id),
        { fontSize: '13px' },
      );
    });
    this.renderCarePicker(x);
  }

  renderCarePicker(x) {
    const y = PICKER_Y + DIET_PANEL_HEIGHT + PANEL_GAP;
    const height = PICKER_HEIGHT - DIET_PANEL_HEIGHT - PANEL_GAP;
    this.panel(x, y, PICKER_COLUMN_WIDTH, height);
    this.text(x + 16, y + 6, '돌봄 (달에 한 번)', { fontStyle: 'bold', fontSize: '15px' });

    const gap = 6;
    const width = (PICKER_COLUMN_WIDTH - 32 - gap) / 2;
    const options = [{ id: null, cost: 0 }, ...this.care];
    options.forEach((entry, index) => {
      const affordable =
        entry.id === null ||
        careAffordable(entry, this.state, this.activities, this.festivalStage() === 'enter' ? [] : this.picks);
      this.choiceButton(
        x + 16 + (index % 2) * (width + gap),
        y + 30 + Math.floor(index / 2) * (CARE_BUTTON_HEIGHT + gap),
        width,
        CARE_BUTTON_HEIGHT,
        entry.id === null ? CARE_NONE_LABEL : careButtonLabel(entry),
        entry.id === this.carePick,
        () => (affordable ? this.chooseCare(entry.id) : this.refuseChoice()),
        { fontSize: '13px', dimmed: !affordable },
      );
    });

    const hint = careHint(this.carePick, this.state);
    if (hint) {
      this.text(x + 16, y + height - 20, hint, { fontSize: '11px', color: '#ffe9b0' });
    }
  }

  renderResolutionOverlay() {
    const x = PICKER_COLUMN_X[0];
    const width = CANVAS_WIDTH - 48;
    const step = this.animationSteps[this.animationIndex];
    if (!step) return;

    this.panel(x, PICKER_Y, width, PICKER_HEIGHT);
    const dayCount = this.animationSteps.length - 1;
    const header =
      step.kind === 'day'
        ? `${formatDate(dateForDay(this.state.month, step.day))} · ${step.day}일 (${step.day}/${daysInMonth(this.state.month)}) · ${step.label}`
        : '한 달을 마무리하는 중…';
    this.text(x + 16, PICKER_Y + 10, header, { fontStyle: 'bold', color: '#ffd479' });
    this.renderSpeedButtons(x + width - 16, PICKER_Y + 8);

    const vignetteWidth = 340;
    const vignetteHeight = PICKER_HEIGHT - 60;
    const vignetteX = x + 16;
    const vignetteY = PICKER_Y + 44;
    this.ui.add(
      this.add
        .rectangle(vignetteX, vignetteY, vignetteWidth, vignetteHeight, step.color, 0.35)
        .setOrigin(0, 0)
        .setStrokeStyle(2, 0xffffff, 0.6),
    );

    const frameSuffix = step.kind === 'day' ? FRAME_SUFFIXES[this.animationFrameIndex] : '';
    const textureKey = `${step.textureKey}${frameSuffix}`;
    if (this.textures.exists(textureKey)) {
      const areaWidth = vignetteWidth - 16;
      const areaHeight = vignetteHeight - 36;
      const image = this.add.image(
        vignetteX + vignetteWidth / 2,
        vignetteY + areaHeight / 2,
        textureKey,
      );
      image.setScale(Math.min(areaWidth / image.width, areaHeight / image.height));
      if (step.kind === 'day') image.setTint(OUTCOME_TINTS[step.outcome]);
      this.ui.add(image);
    }

    this.text(vignetteX + vignetteWidth / 2, vignetteY + vignetteHeight - 14, step.label, {
      fontSize: '15px',
      fontStyle: 'bold',
      align: 'center',
      wordWrap: { width: vignetteWidth - 16 },
    }).setOrigin(0.5, 1);

    const textX = vignetteX + vignetteWidth + 24;
    const textWidth = width - vignetteWidth - 64;
    if (step.kind === 'day') {
      this.text(textX, vignetteY + 2, `${step.day}일째 - ${step.line}`, {
        fontSize: '18px',
        fontStyle: 'bold',
        color: OUTCOME_COLORS[step.outcome],
        wordWrap: { width: textWidth },
      });
      this.renderDayGauges(step, textX, vignetteY + 38, textWidth);
      this.renderMoneyBox(step, textX, vignetteY + vignetteHeight - 4);
      this.text(textX + textWidth, vignetteY + vignetteHeight - 4, `${dayCount}일 중 ${step.day}일째`, {
        fontSize: '12px',
        color: '#8f93b3',
      }).setOrigin(1, 1);
      return;
    }
    this.text(textX, vignetteY + 4, step.title, { fontSize: '20px', fontStyle: 'bold' });
    this.text(textX, vignetteY + 40, step.flavor, {
      fontSize: '16px',
      color: '#e7e9f5',
      wordWrap: { width: textWidth },
    });
    this.text(textX, vignetteY + 90, step.effectsText, { fontSize: '14px', color: '#cfd2e6' });
  }

  renderMoneyBox(step, x, bottomY) {
    if (step.money === undefined) return;
    const change = step.moneyDelta;
    const suffix = change === 0 ? '' : `  (${formatDelta(change)})`;
    this.text(x, bottomY, `소지금 ${step.money}${suffix}`, {
      fontSize: '15px',
      fontStyle: 'bold',
      color: change > 0 ? '#8fe0a8' : change < 0 ? '#ff9a9a' : '#ffd479',
      backgroundColor: '#1c1e33',
      padding: { x: 8, y: 3 },
    }).setOrigin(0, 1);
  }

  renderDayGauges(step, x, y, width) {
    const rowHeight = 26;
    const barX = x + 64;
    const barWidth = width - 64 - 56;
    step.gauges.forEach((gauge, index) => {
      const rowY = y + index * rowHeight;
      this.text(x, rowY, statLabel(gauge.stat), { fontSize: '14px', color: '#cfd2e6' });
      this.statBar(
        barX,
        rowY + 5,
        barWidth,
        10,
        gauge.value / 100,
        gauge.stat === 'stress' ? 0xe05c5c : 0x4d9a6e,
      );
      const changed = gauge.delta !== 0;
      this.text(barX + barWidth + 8, rowY, changed ? `${gauge.value} (${formatDelta(gauge.delta)})` : `${gauge.value}`, {
        fontSize: '13px',
        color: changed ? '#ffd479' : '#8f93b3',
      });
    });
  }

  renderSpeedButtons(rightX, y) {
    let x = rightX;
    [...SPEEDS].reverse().forEach((speed) => {
      const selected = this.speed === speed;
      const button = this.add
        .rectangle(x, y, 84, 26, selected ? CHOICE_SELECTED_FILL : CHOICE_FILL, 1)
        .setOrigin(1, 0)
        .setStrokeStyle(1, 0xffffff, 0.5)
        .setInteractive({ useHandCursor: true });
      button.on('pointerdown', () => this.setSpeed(speed));
      this.ui.add(button);
      this.text(x - 42, y + 13, SPEED_LABELS[speed], { fontSize: '13px' }).setOrigin(0.5);
      x -= 92;
    });
  }

  choose(slot, activityId) {
    if (this.busy || isPickerLocked(this.state)) return;
    this.picks[slot] = activityId;
    this.message = '';
    this.render();
  }

  refuseChoice() {
    if (this.busy) return;
    this.message = UNAFFORDABLE_LINE;
    this.render();
  }

  focusSlot(slot) {
    if (this.busy) return;
    this.focusedSlot = slot;
    this.render();
  }

  chooseCare(careId) {
    if (this.busy) return;
    this.carePick = careId;
    this.render();
  }

  chooseDiet(dietId) {
    if (this.busy) return;
    this.dietPick = dietId;
    this.render();
  }

  renderPlayButton() {
    const entering = this.festivalStage() === 'enter';
    const label = this.busy ? '진행 중…' : entering ? FESTIVAL_ENTER_LABEL : '한 달 보내기';
    const enabled = !this.busy && this.picks.length > 0 && this.festivalStage() !== 'choose';
    const fill = enabled ? 0x3f7d5a : 0x3a3c4f;

    const button = this.add
      .rectangle(CANVAS_WIDTH / 2, PLAY_BUTTON_Y, 280, 48, fill, 1)
      .setStrokeStyle(2, 0xffffff, 0.6);
    this.ui.add(button);
    this.text(CANVAS_WIDTH / 2, PLAY_BUTTON_Y, label, {
      fontSize: '22px',
      fontStyle: 'bold',
    }).setOrigin(0.5);

    if (!enabled) return;
    button.setInteractive({ useHandCursor: true });
    button.on('pointerover', () => button.setFillStyle(0x4d9a6e, 1));
    button.on('pointerout', () => button.setFillStyle(fill, 1));
    button.on('pointerdown', () => this.playMonth());
  }

  startEndingReveal() {
    this.endingStep = initialRevealStep(true);
    this.rollTick = 0;
    this.runStatRoll(++this.revealToken);
  }

  async runStatRoll(token) {
    const total = rollTotalTicks(CORE_STATS.length);
    while (this.rollTick < total) {
      await this.delay(ROLL_TICK_MS);
      if (!this.alive || token !== this.revealToken) return;
      this.rollTick += 1;
      this.safeRender();
    }
    this.scheduleAutoAdvance(token);
  }

  scheduleAutoAdvance(token) {
    if (isFinalRevealStep(this.endingStep)) return;
    this.delay(REVEAL_STEP_MS).then(() => {
      if (!this.alive || token !== this.revealToken) return;
      this.advanceReveal();
    });
  }

  advanceReveal() {
    if (isFinalRevealStep(this.endingStep)) return;
    this.rollTick = rollTotalTicks(CORE_STATS.length);
    this.endingStep = nextRevealStep(this.endingStep);
    this.scheduleAutoAdvance(++this.revealToken);
    this.safeRender();
  }

  skipReveal() {
    this.revealToken += 1;
    this.rollTick = rollTotalTicks(CORE_STATS.length);
    this.endingStep = FINAL_REVEAL_STEP;
    this.safeRender();
  }

  async restartGame() {
    if (this.busy) return;
    this.busy = true;
    try {
      const state = await this.api.startGame();
      this.scene.start('GameScene', {
        state,
        activities: this.activities,
        diets: this.diets,
        care: this.care,
        festival: this.festival,
        events: this.eventTable,
      });
    } catch (error) {
      this.message = describeError(error);
      this.busy = false;
      this.safeRender();
    }
  }

  renderEndOfRun() {
    const x = COLUMN_X[0];
    const width = CANVAS_WIDTH - 48;
    const step = this.endingStep;
    const panel = this.panel(x, PICKER_Y, width, PICKER_HEIGHT);

    if (!isFinalRevealStep(step)) {
      panel.setInteractive({ useHandCursor: true });
      panel.on('pointerdown', () => this.advanceReveal());
    }

    this.text(x + 24, PICKER_Y + 14, '육성을 마쳤습니다', {
      fontSize: '22px',
      fontStyle: 'bold',
      color: '#ffd479',
    });

    const rolled = rolledValues(
      CORE_STATS.map((stat) => this.state.stats[stat]),
      this.rollTick,
    );
    const summary = CORE_STATS.map((stat, index) => `${statLabel(stat)} ${rolled[index]}`).join(
      '   ',
    );
    this.text(x + 24, PICKER_Y + 48, summary, { fontSize: '18px', fontStyle: 'bold' });

    if (revealed(step, 'title')) {
      this.text(x + 24, PICKER_Y + 82, endingLabel(this.state.ending), {
        fontSize: '30px',
        fontStyle: 'bold',
        color: '#8ce3a5',
      });
    }
    if (revealed(step, 'flavor')) {
      this.text(x + 24, PICKER_Y + 128, endingFlavor(this.state.ending), {
        fontSize: '17px',
        color: '#cfd2e6',
        lineSpacing: 6,
        wordWrap: { width: width - 300 },
      });
    }
    if (revealed(step, 'score')) {
      this.text(x + width - 24, PICKER_Y + 14, `점수 ${this.state.score} / 1000`, {
        fontSize: '20px',
        fontStyle: 'bold',
        color: '#cfd2e6',
      }).setOrigin(1, 0);
      this.endButton(x + width - 24 - 70, PICKER_Y + PICKER_HEIGHT - 40, 140, '다시 시작', () =>
        this.restartGame(),
      );
    } else {
      this.endButton(x + width - 24 - 50, PICKER_Y + 10, 100, '건너뛰기', () => this.skipReveal());
    }
  }

  endButton(centerX, centerY, width, label, onClick) {
    const button = this.add
      .rectangle(centerX, centerY, width, 34, CHOICE_FILL, 1)
      .setStrokeStyle(1, 0xffffff, 0.5);
    this.ui.add(button);
    this.text(centerX, centerY, label, { fontSize: '16px', fontStyle: 'bold' }).setOrigin(0.5);
    button.setInteractive({ useHandCursor: true });
    button.on('pointerdown', (_pointer, _x, _y, event) => {
      event?.stopPropagation?.();
      onClick();
    });
  }

  renderMessage() {
    const isError = !!this.message;
    const text = this.message || this.lastMonthSummary();
    if (!text) return;

    this.text(CANVAS_WIDTH / 2, PICKER_Y + PICKER_HEIGHT + 6, text, {
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

  choiceButton(x, y, width, height, label, selected, onClick, options = {}) {
    const { fontSize = '17px', sublabel, sublabelColor, dimmed = false } = options;
    const alpha = dimmed ? 0.45 : 1;
    const fill = selected ? CHOICE_SELECTED_FILL : CHOICE_FILL;
    const button = this.add
      .rectangle(x, y, width, height, fill, alpha)
      .setOrigin(0, 0)
      .setStrokeStyle(selected ? 2 : 1, 0xffffff, selected ? 0.9 : 0.3);
    this.ui.add(button);
    const labelY = sublabel ? y + height * 0.34 : y + height / 2;
    this.text(x + width / 2, labelY, label, {
      fontSize,
      fontStyle: selected ? 'bold' : 'normal',
    })
      .setOrigin(0.5)
      .setAlpha(alpha);
    if (sublabel) {
      this.text(x + width / 2, y + height * 0.76, sublabel, {
        fontSize: '12px',
        color: sublabelColor,
      }).setOrigin(0.5);
    }

    button.setInteractive({ useHandCursor: true });
    button.on('pointerover', () => button.setFillStyle(selected ? 0x4d9a6e : 0x393c5e, dimmed ? 0.6 : 1));
    button.on('pointerout', () => button.setFillStyle(fill, alpha));
    button.on('pointerdown', onClick);
    return button;
  }
}
