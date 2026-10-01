export const FESTIVAL_MONTH = 10;
export const SKIP_LABEL = '불참';
export const PLAYER_LABEL = '우리 고양이';

export const CONTEST_LABELS = {
  charm: '재롱 대회',
  obedience: '복종 대회',
  exploration: '탐험 대회',
  grace: '기품 대회',
};

export const RIVAL_NAMES = {
  nabi: '나비',
  cheese: '치즈',
  boli: '보리',
  dubu: '두부',
  mukmul: '먹물',
  gomi: '고미',
  mackerel: '고등어',
  baduk: '바둑이',
  tori: '토리',
  samsaek: '삼색이',
  yuri: '유리',
  nuri: '누리',
};

const STAT_LABELS = {
  affection: '애정',
  discipline: '규율',
  curiosity: '호기심',
  refinement: '기품',
};

const RANK_LINES = {
  1: '1위! 모두가 박수를 보냈다.',
  2: '2위! 아깝게 우승을 놓쳤다.',
  3: '3위. 입상은 했지만 아쉬웠다.',
};
const LAST_PLACE_LINE = '순위권에 들지 못했다. 내년을 노려 보자.';

export const contestLabel = (id) => CONTEST_LABELS[id] ?? id;
export const rivalName = (id) => RIVAL_NAMES[id] ?? id;

// 'none' outside the festival; 'locked' when forced rest overrides it;
// 'choose' until the player picks; then 'enter' or 'skip'.
export function festivalStage(state, festival, choice) {
  if (!festival || state?.finished || state?.month !== festival.month) return 'none';
  if (Array.isArray(state.forced_slots) && state.forced_slots.length > 0) return 'locked';
  if (choice === 'skip') return 'skip';
  if (choice) return 'enter';
  return 'choose';
}

export function contestRows(festival, stats) {
  return (festival?.contests ?? []).map((contest) => ({
    id: contest.id,
    label: contestLabel(contest.id),
    stat: contest.stat,
    statLabel: STAT_LABELS[contest.stat] ?? contest.stat,
    value: stats?.[contest.stat] ?? 0,
  }));
}

export function contestRowLabel(row) {
  return `${row.label} · ${row.statLabel} ${row.value}`;
}

export function sendableContest(stage, choice) {
  return stage === 'enter' ? choice : null;
}

// The server places the player ahead of equal scores, so a stable sort with
// the player first reproduces its ranking.
export function rankedEntries(result) {
  const entries = [
    { name: PLAYER_LABEL, score: result.score, player: true },
    ...result.rivals.map((rival) => ({ name: rivalName(rival.id), score: rival.score, player: false })),
  ];
  return entries.sort((a, b) => b.score - a.score);
}

export function buildFestivalCard(state) {
  const result = state?.festival_result;
  if (!result) return null;
  const ribbon = (state.ribbons ?? []).some((entry) => entry.contest === result.contest);
  return { kind: 'festival', key: result.contest, result, ribbon, chips: {} };
}

export function festivalCardCopy(card) {
  const { result, ribbon } = card;
  const lines = rankedEntries(result).map(
    (entry, index) => `${index + 1}위  ${entry.name}  ${entry.score}${entry.player ? '  ◀' : ''}`,
  );
  const rewards = [result.prize > 0 ? `상금 +${result.prize}` : '상금 없음'];
  if (ribbon) rewards.push('리본 획득');
  return {
    title: `축제 · ${contestLabel(result.contest)}`,
    body: RANK_LINES[result.rank] ?? LAST_PLACE_LINE,
    lines,
    footer: rewards.join('  '),
  };
}
