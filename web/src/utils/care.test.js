import { describe, expect, it } from 'vitest';
import {
  careAffordable,
  careButtonLabel,
  careCharge,
  careHint,
  careResultCopy,
  careWorks,
  sendableCare,
} from './care.js';

const PET = { id: 'pet', cost: 0, works_when: 'always' };
const TREAT = { id: 'treat', cost: 20, works_when: 'healthy' };
const SCOLD = { id: 'scold', cost: 0, works_when: 'delinquent' };
const CARE = [PET, TREAT, SCOLD];
const ACTIVITIES = [
  { id: 'rest', cost: 0 },
  { id: 'educate', cost: 35 },
];
const HEALTHY = { money: 100, is_sick: false, is_delinquent: false };

describe('careWorks', () => {
  it('pet always works', () => {
    expect(careWorks(PET, { is_sick: true, is_delinquent: true })).toBe(true);
  });

  it('treat needs a cat that is neither sick nor delinquent', () => {
    expect(careWorks(TREAT, HEALTHY)).toBe(true);
    expect(careWorks(TREAT, { ...HEALTHY, is_sick: true })).toBe(false);
    expect(careWorks(TREAT, { ...HEALTHY, is_delinquent: true })).toBe(false);
  });

  it('scold works only when delinquent', () => {
    expect(careWorks(SCOLD, HEALTHY)).toBe(false);
    expect(careWorks(SCOLD, { ...HEALTHY, is_delinquent: true })).toBe(true);
  });

  it('is false for an unknown entry', () => {
    expect(careWorks(undefined, HEALTHY)).toBe(false);
  });
});

describe('careCharge', () => {
  it('charges a working treat and nothing for one that cannot work', () => {
    expect(careCharge(TREAT, HEALTHY)).toBe(20);
    expect(careCharge(TREAT, { ...HEALTHY, is_sick: true })).toBe(0);
    expect(careCharge(PET, HEALTHY)).toBe(0);
  });
});

describe('careAffordable', () => {
  it('counts the schedule and the treat together, exactly at the boundary', () => {
    const picks = ['educate', 'rest', 'rest'];

    expect(careAffordable(TREAT, { ...HEALTHY, money: 55 }, ACTIVITIES, picks)).toBe(true);
    expect(careAffordable(TREAT, { ...HEALTHY, money: 54 }, ACTIVITIES, picks)).toBe(false);
  });

  it('ignores the schedule cost while forced rest is active', () => {
    const state = { ...HEALTHY, money: 20, forced_slots: ['rest', 'rest', 'rest'] };

    expect(careAffordable(TREAT, state, ACTIVITIES, ['educate', 'educate', 'educate'])).toBe(true);
  });

  it('is always affordable for a treat that will not work', () => {
    const sick = { ...HEALTHY, money: 0, is_sick: true };

    expect(careAffordable(TREAT, sick, ACTIVITIES, ['rest', 'rest', 'rest'])).toBe(true);
  });
});

describe('sendableCare', () => {
  const picks = ['educate', 'rest', 'rest'];

  it('passes an affordable pick through', () => {
    expect(sendableCare('pet', CARE, HEALTHY, ACTIVITIES, picks)).toBe('pet');
  });

  it('drops a treat that no longer fits', () => {
    expect(sendableCare('treat', CARE, { ...HEALTHY, money: 40 }, ACTIVITIES, picks)).toBeNull();
  });

  it('returns null for none or an unknown id', () => {
    expect(sendableCare(null, CARE, HEALTHY, ACTIVITIES, picks)).toBeNull();
    expect(sendableCare('hug', CARE, HEALTHY, ACTIVITIES, picks)).toBeNull();
  });
});

describe('careButtonLabel', () => {
  it('shows the cost only for paid actions', () => {
    expect(careButtonLabel(TREAT)).toBe('간식 -20');
    expect(careButtonLabel(PET)).toBe('쓰다듬기');
  });
});

describe('careHint', () => {
  it('explains why a treat will not work', () => {
    expect(careHint('treat', { is_sick: true })).toBe('아플 때는 소용없어요');
    expect(careHint('treat', { is_delinquent: true })).toContain('소용없어요');
    expect(careHint('treat', HEALTHY)).toBe('');
  });

  it('warns that scolding only helps a delinquent cat', () => {
    expect(careHint('scold', HEALTHY)).toContain('말썽');
    expect(careHint('scold', { is_delinquent: true })).toBe('');
  });

  it('gives state advice when nothing is selected', () => {
    expect(careHint(null, { is_delinquent: true })).toContain('혼내기');
    expect(careHint(null, { is_sick: true })).toContain('쓰다듬기');
    expect(careHint(null, HEALTHY)).toBe('');
  });
});

describe('careResultCopy', () => {
  it('picks the worked or failed line', () => {
    expect(careResultCopy({ key: 'treat', worked: true }).body).toBe('간식을 먹고 기분이 좋아졌다.');
    expect(careResultCopy({ key: 'scold', worked: false }).body).toContain('혼내도 소용없었다');
  });

  it('tolerates an unknown action', () => {
    expect(careResultCopy({ key: 'hug', worked: true }).body).toBe('');
  });
});
