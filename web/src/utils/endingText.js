const ENDING_TEXT = {
  hospitalized: {
    label: '입원한 고양이',
    flavor: '몸이 많이 약해져 병원 신세를 지게 되었어요.\n푹 쉬고 나면 다시 기운을 차릴 거예요.',
  },
  ran_away: {
    label: '가출한 고양이',
    flavor: '말썽이 이어지다 어느 날 훌쩍 집을 나갔어요.\n골목 어딘가에서 잘 지내고 있기를 바랍니다.',
  },
  neglected: {
    label: '방치된 고양이',
    flavor: '돌봄이 모자랐던 한 해였어요.\n고양이는 몸도 마음도 지쳐 있습니다.',
  },
  delinquent: {
    label: '말썽꾸러기 고양이',
    flavor: '스트레스가 쌓여 말을 듣지 않아요.\n집 안 물건이 남아나질 않습니다.',
  },
  balanced: {
    label: '골고루 자란 고양이',
    flavor: '어느 한쪽에 치우치지 않고 쑥쑥 컸어요.\n무엇을 맡겨도 든든한 고양이가 되었습니다.',
  },
  healthy: {
    label: '튼튼한 고양이',
    flavor: '털에 윤이 나고 눈빛이 맑아요.\n지붕 위도 단숨에 오르는 건강한 고양이입니다.',
  },
  beloved: {
    label: '사랑받는 고양이',
    flavor: '온 동네가 이 고양이를 아껴요.\n쓰다듬어 달라며 골골송을 부릅니다.',
  },
  disciplined: {
    label: '모범생 고양이',
    flavor: '약속한 시간에 밥 앞에 앉아요.\n스크래처 말고는 건드리지 않는 의젓한 고양이입니다.',
  },
  curious: {
    label: '호기심 많은 탐험가',
    flavor: '상자도 창밖도 그냥 지나치지 않아요.\n오늘도 새로운 모험을 찾아 나섭니다.',
  },
  refined: {
    label: '우아한 고양이',
    flavor: '걸음걸이마다 품위가 흘러요.\n앉은 자세만으로도 눈길을 끕니다.',
  },
  pair_health_affection: {
    label: '포근한 난로 고양이',
    flavor: '튼튼하고 다정해서 곁에 있으면 따뜻해요.\n겨울밤 무릎 위 자리는 언제나 이 고양이 차지입니다.',
  },
  pair_health_discipline: {
    label: '씩씩한 순찰대 고양이',
    flavor: '체력도 규칙도 빈틈이 없어요.\n매일 같은 시간에 동네 한 바퀴를 돕니다.',
  },
  pair_health_curiosity: {
    label: '들판을 달리는 고양이',
    flavor: '튼튼한 다리로 어디든 달려가요.\n나비를 쫓다 보면 해가 저물어 있습니다.',
  },
  pair_health_refinement: {
    label: '윤기 나는 귀족 고양이',
    flavor: '건강한 털결에 품위까지 더했어요.\n사진 한 장이면 모두가 감탄합니다.',
  },
  pair_affection_discipline: {
    label: '듬직한 집사의 단짝',
    flavor: '다정하면서도 의젓해요.\n집사가 부르면 꼬리를 세우고 달려옵니다.',
  },
  pair_affection_curiosity: {
    label: '장난꾸러기 껌딱지',
    flavor: '신기한 걸 찾으면 꼭 집사에게 보여줘요.\n어디를 가든 졸졸 따라다닙니다.',
  },
  pair_affection_refinement: {
    label: '무릎 위의 공주님',
    flavor: '애교와 기품을 함께 갖췄어요.\n쓰다듬는 손길마저 우아하게 받아들입니다.',
  },
  pair_discipline_curiosity: {
    label: '영리한 수색대장',
    flavor: '궁금한 건 규칙대로 차근차근 파헤쳐요.\n사라진 장난감은 이 고양이가 찾아냅니다.',
  },
  pair_discipline_refinement: {
    label: '단정한 궁정 고양이',
    flavor: '자세도 예절도 흠잡을 데가 없어요.\n식사 시간에도 발끝 하나 흐트러지지 않습니다.',
  },
  pair_curiosity_refinement: {
    label: '꿈꾸는 예술가 고양이',
    flavor: '창가에 앉아 세상을 오래 바라봐요.\n그 눈에 담긴 것들이 작품이 됩니다.',
  },
};

export function endingLabel(id) {
  return ENDING_TEXT[id]?.label ?? id;
}

export function endingFlavor(id) {
  return ENDING_TEXT[id]?.flavor ?? '';
}
