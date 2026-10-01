import { scheduleCost } from './money.js';

export const CARE_NONE_LABEL = '안 함';

export const CARE_LABELS = {
  pet: '쓰다듬기',
  treat: '간식',
  scold: '혼내기',
};

const RESULT_COPY = {
  pet: {
    worked: { title: '쓰다듬기', body: '쓰다듬어 주자 마음이 한결 편해졌다.' },
    failed: { title: '쓰다듬기', body: '쓰다듬어 주었지만 별 차이가 없었다.' },
  },
  treat: {
    worked: { title: '간식 주기', body: '간식을 먹고 기분이 좋아졌다.' },
    failed: { title: '간식 주기', body: '간식도 소용없었다. 입맛이 없는 모양이다.' },
  },
  scold: {
    worked: { title: '혼내기', body: '따끔하게 혼내자 고양이가 반성했다.' },
    failed: { title: '혼내기', body: '혼내도 소용없었다. 고양이가 시무룩해졌다.' },
  },
};

export function careLabel(id) {
  return CARE_LABELS[id] ?? id;
}

export function careWorks(entry, state) {
  if (!entry) return false;
  if (entry.works_when === 'always') return true;
  if (entry.works_when === 'delinquent') return Boolean(state?.is_delinquent);
  return !state?.is_sick && !state?.is_delinquent;
}

// What the server will charge: a treat that cannot work is free.
export function careCharge(entry, state) {
  return careWorks(entry, state) ? (entry?.cost ?? 0) : 0;
}

export function careAffordable(entry, state, activities, picks) {
  const schedule = state?.forced_slots ? 0 : scheduleCost(activities, picks);
  return schedule + careCharge(entry, state) <= (state?.money ?? 0);
}

export function careButtonLabel(entry) {
  const name = careLabel(entry.id);
  return entry.cost > 0 ? `${name} -${entry.cost}` : name;
}

// Picks that no longer fit once the care is paid for are dropped to "none".
export function sendableCare(id, care, state, activities, picks) {
  if (!id) return null;
  const entry = care.find((candidate) => candidate.id === id);
  if (!entry) return null;
  return careAffordable(entry, state, activities, picks) ? id : null;
}

export function careHint(id, state) {
  if (id === 'treat' && state?.is_sick) return '아플 때는 소용없어요';
  if (id === 'treat' && state?.is_delinquent) return '말썽을 부릴 때는 소용없어요';
  if (id === 'scold' && !state?.is_delinquent) return '말썽을 부릴 때만 효과가 있어요';
  if (id) return '';
  if (state?.is_delinquent) return '말썽 중이에요. 혼내기가 통해요';
  if (state?.is_sick) return '아플 땐 쓰다듬기가 좋아요';
  return '';
}

export function careResultCopy(card) {
  const copies = RESULT_COPY[card?.key];
  if (!copies) return { title: '돌봄', body: '' };
  return card.worked ? copies.worked : copies.failed;
}
