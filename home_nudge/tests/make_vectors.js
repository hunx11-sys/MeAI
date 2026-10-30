// 테스트 벡터 만들기 : 기준 구현(src/core/rules.js)의 결과를 tests/vectors.json 으로 적는다.
// 서버를 다른 언어로 만들면 이 파일의 입력을 넣어 기대값과 똑같이 나오는지 확인한다.
// 쓰는 법 : node home_nudge/tests/make_vectors.js   (규칙을 일부러 바꿨을 때만 다시 만든다)
const R = require('../src/core/rules.js');
const fs = require('fs'), path = require('path');
const cfg = require('../config/nudge.config.json');
const cal = require('../data/calendar.json');

const V = { $comment: 'MeAI 홈 넛지 규칙 엔진 테스트 벡터. 만든 곳 : tests/make_vectors.js · 확인 : node tests/rules.test.js', version: cfg.version };

V.dates = ['2026-10-29', '2026-10-30', '2026-11-02', '2026-12-31', '2027-01-01', '2026-01-01', '2026-10-05', '2026-10-09'].map(d => ({
  in: d, weekId: R.weekId(d), weekLabel: R.weekLabel(d), monday: R.weekMonday(d), bizDay: R.isBizDay(d, cal), prevBizDay: R.prevBizDay(d, cal)
}));
V.sha256 = ['', 'abc', '메리츠 MeAI', 'meai-demo-seed|2026-W44'].map(s => ({ in: s, out: R.sha256hex(s) }));
V.draw = [['seed-test', '2026-W44', 45, 6], ['seed-test', '2026-W45', 45, 6], ['a'.repeat(64), '2026-W44', 35, 6]].map(a => ({ in: a, out: R.drawNumbers(a[0], a[1], a[2], a[3]) }));
V.prob = [[45, 6, 3], [45, 6, 4], [45, 6, 5], [35, 6, 3]].map(a => ({ in: a, atLeast: +R.probAtLeast(a[0], a[1], a[2]).toFixed(8) }));
V.copy = [
  ['보험료가 오르기 전에, 점검해요!', '보험료가오르기전에 점검해요'],
  ['보험료가 오르기 전에, 점검해요!', '보험료가 오르기 전에'],
  ['안녕하세요 고객님', '안녕하세요 고갱님'],
  ['ABC 123 가나다', 'abc123가나다']
].map(a => ({ in: a, out: R.copyScore(a[0], a[1]) }));
V.mask = ['김민수', '이수', '남궁민수', 'Krishnamurthy', '최'].map(n => ({ in: n, out: R.maskName(n) }));

// 시나리오 : 빈 사용자 하나가 2026-10-26(월) ~ 10-30(금)에 하는 행동 → 보상 · 연출 · 상태
function scenario() {
  const st = R.emptyState('u-test'), quiz = { id: 'q1', answer: 'X' }, talk = { id: 't1', head: '고객이 먼저 떠올리는 한 사람이 되자.' };
  const user = { id: 'u-test', name: '시험', joinMonth: 2 };
  const steps = [
    ['2026-10-26', '08:50', { kind: 'attend' }],
    ['2026-10-26', '09:10', { kind: 'quiz.answer', quizId: 'q1', choice: 'O' }],
    ['2026-10-26', '09:12', { kind: 'quiz.explained', quizId: 'q1' }],
    ['2026-10-26', '10:00', { kind: 'reco.open', customerId: 'c1', tags: ['age_up'] }],
    ['2026-10-26', '10:05', { kind: 'chat.custom', customerId: 'c1' }],
    ['2026-10-26', '10:06', { kind: 'chat.custom', customerId: 'c1' }],
    ['2026-10-26', '11:00', { kind: 'notice.read', ref: 'n1' }],
    ['2026-10-26', '12:00', { kind: 'talk.copy', talkId: 't1', typed: '고객이 먼저 떠올리는 한 사람이 되자' }],
    ['2026-10-27', '09:00', { kind: 'attend' }],
    ['2026-10-27', '09:01', { kind: 'attend' }],
    ['2026-10-28', '09:00', { kind: 'chat.general' }],
    ['2026-10-29', '09:00', { kind: 'attend' }],
    ['2026-10-30', '08:59', { kind: 'attend' }],
    ['2026-10-30', '09:30', { kind: 'cheer.send', to: 'p1' }],
    ['2026-10-30', '09:31', { kind: 'cheer.send', to: 'p1' }],
    ['2026-11-02', '09:00', { kind: 'attend' }]
  ];
  let n = 0;
  return steps.map(([d, hm, ev]) => {
    const now = R.toMs(d, hm);
    const q = Object.assign({}, quiz, { id: ev.quizId || 'q1' });
    const out = R.evaluate(st, ev, { cfg, cal, now, rand: R.rng(1000 + (++n)), user, recoToday: ['c1', 'c2'], quiz: q, talk, league: null });
    const s = R.streakInfo(st, d, now, cal, cfg), qs = R.questSummary(st, d, cfg);
    return { at: d + ' ' + hm, ev, ok: out.ok, reason: out.reason,
      grants: out.grants.map(g => [g.type, g.amount, g.rule]), fx: out.fx.map(f => f.type),
      after: { streak: s.current, best: s.best, shields: st.wallet.shields, quests: qs.done, weekXp: (st.weeks[R.weekId(d)] || {}).xp, tickets: (st.weeks[R.weekId(d)] || {}).tickets,
        sets: Object.keys(st.weeks).reduce((a, w) => a + st.weeks[w].sets.length, 0) } };
  });
}
V.scenario = { rand: 'mulberry32(1000 + 단계 번호)', user: { joinMonth: 2 }, recoToday: ['c1', 'c2'], steps: scenario() };

// 보호권 : 월 1회 채움(2장) → 빈 영업일 2일을 메움 → 3일이면 하나도 안 씀
function shieldCase(missDays) {
  const st = R.emptyState('u-s');
  const lit = ['2026-11-02', '2026-11-03'];
  lit.forEach(d => R.evaluate(st, { kind: 'attend' }, { cfg, cal, now: R.toMs(d, '09:00'), rand: R.rng(1), user: {}, recoToday: [], quiz: null, talk: null, league: null }));
  let back = '2026-11-03';
  for (let i = 0; i <= missDays; i++) { back = R.addDays(back, 1); while (!R.isBizDay(back, cal)) back = R.addDays(back, 1); } // 빈 영업일 missDays 개 뒤의 영업일
  const out = R.evaluate(st, { kind: 'attend' }, { cfg, cal, now: R.toMs(back, '09:00'), rand: R.rng(1), user: {}, recoToday: [], quiz: null, talk: null, league: null });
  return { missDays, back, fx: out.fx.map(f => f.type), shieldsLeft: st.wallet.shields, streak: R.streakInfo(st, back, R.toMs(back, '09:00'), cal, cfg).current };
}
V.shield = [1, 2, 3].map(shieldCase);

// 행운 존 (v5.1) : 고정 고객 목록 · 작은 문제 은행으로 하루 동안의 룰렛 · 슬롯 · 고객 챙기기 · 피버 · OX 챌린지 · 타로 · 스크래치
const FUN_CRM = [
  { id: 'k1', sym: 'birthday', tags: ['birthday', 'thanks'] }, { id: 'k2', sym: 'age_up', tags: ['age_up', 'gap'] }, { id: 'k3', sym: 'age_up', tags: ['age_up'] },
  { id: 'k4', sym: 'renew', tags: ['renew', 'health'] }, { id: 'k5', sym: 'gap', tags: ['gap', 'health'] }, { id: 'k6', sym: 'consent', tags: ['thanks'] },
  { id: 'k7', sym: 'age_up', tags: ['age_up', 'birthday'] }, { id: 'k8', sym: 'renew', tags: ['renew'] }, { id: 'k9', sym: 'gap', tags: ['gap', 'thanks'] }];
const FUN_BANK = [
  { id: 'x1', cat: 'terms', a: 'O' }, { id: 'x2', cat: 'terms', a: 'X' }, { id: 'x3', cat: 'medical', a: 'O' },
  { id: 'x4', cat: 'medical', a: 'X' }, { id: 'x5', cat: 'system', a: 'O' }, { id: 'x6', cat: 'comply', a: 'X' }, { id: 'x7', cat: 'meai', a: 'O' }].map(q => Object.assign({ q: q.id + ' 문제', why: q.id + ' 해설', src: '시험' }, q));
function funScenario() {
  const st = R.emptyState('u-fun'), user = { id: 'u-fun', name: '시험', joinMonth: 20 }, quiz = { id: 'q-f', answer: 'O' };
  const d = '2026-11-03', steps = [];
  let n = 0;
  const bankById = {}; FUN_BANK.forEach(q => { bankById[q.id] = q; });
  function go(hm, ev) {
    const out = R.evaluate(st, ev, { cfg, cal, now: R.toMs(d, hm), rand: R.rng(5000 + (++n)), user, recoToday: ['c1'], quiz, talk: null, league: null, crm: FUN_CRM, oxBank: FUN_BANK });
    steps.push({ at: hm, ev, ok: out.ok, reason: out.reason, grants: out.grants.map(g => [g.type, g.amount, g.rule]), fx: out.fx.map(f => f.type), data: out.data || null,
      after: { weekXp: (st.weeks[R.weekId(d)] || {}).xp, tickets: (st.weeks[R.weekId(d)] || {}).tickets, best: st.fun.best } });
    return out;
  }
  const s1 = go('10:00', { kind: 'roulette.spin' });
  go('10:01', { kind: 'roulette.spin' });                                              // 기회 없음
  if (s1.data && s1.data.customers[0]) go('10:05', { kind: 'crm.done', ref: 'r:' + s1.data.spinId, customerId: s1.data.customers[0] });
  if (s1.data && s1.data.customers[1]) go('14:10', { kind: 'crm.done', ref: 'r:' + s1.data.spinId, customerId: s1.data.customers[1] });   // 오후 피버 ×2
  go('14:11', { kind: 'crm.done', ref: 'r:' + (s1.data && s1.data.spinId), customerId: 'nobody' });        // 룰렛이 고르지 않은 고객
  const p1 = go('14:20', { kind: 'cslot.pull' });
  (p1.data ? p1.data.customers : []).forEach((c, i) => go('14:2' + (1 + i), { kind: 'crm.done', ref: 's:' + p1.data.pullId, customerId: c }));
  const c1 = go('15:10', { kind: 'challenge.start' });
  (c1.data ? c1.data.items : []).forEach((it, i) => go('15:1' + (1 + i), { kind: 'challenge.answer', ref: c1.data.runId, idx: i, choice: i === 2 ? (bankById[it.id].a === 'O' ? 'X' : 'O') : bankById[it.id].a, ms: 1500 + i * 700 }));
  const c2 = go('15:20', { kind: 'challenge.start' });
  (c2.data ? c2.data.items : []).forEach((it, i) => go('15:2' + (1 + i), { kind: 'challenge.answer', ref: c2.data.runId, idx: i, choice: bankById[it.id].a, ms: 900 }));
  go('16:00', { kind: 'tarot.draw', choice: 1 });
  go('16:01', { kind: 'tarot.draw', choice: 2 });                                      // 하루 한 장
  go('16:10', { kind: 'attend' }); go('16:11', { kind: 'quiz.answer', quizId: 'q-f', choice: 'O' }); go('16:12', { kind: 'reco.open', customerId: 'c1' });   // 일일 미션 → 스크래치
  const sc = st.fun.scratch[0];
  if (sc) { go('16:20', { kind: 'scratch.reveal', ref: sc.id }); go('16:21', { kind: 'scratch.reveal', ref: sc.id }); }
  go('16:30', { kind: 'roulette.spin' });                                              // 일일 미션 보너스 기회
  return { crm: FUN_CRM, bank: FUN_BANK.map(q => ({ id: q.id, cat: q.cat, a: q.a })), day: d, rand: 'mulberry32(5000 + 단계 번호)', steps,
    bingo: R.bingoState(st, d, cfg), plays: R.funPlays(st, d, cfg) };
}
V.fun = {
  weighted: (() => { const r = R.rng(42), c = cfg.fun.roulette.segments.map(() => 0); for (let i = 0; i < 10000; i++) c[R.pickWeighted(r, cfg.fun.roulette.segments)]++; return { seed: 42, n: 10000, counts: c }; })(),
  tarot: ['2026-11-03', '2026-11-04'].map(dd => ({ in: ['u-fun', dd, 22], out: R.tarotOfDay('u-fun', dd, 22) })),
  points: [[true, 1500, 1], [true, 900, 3], [false, 500, 0], [true, 12000, 2]].map(a => ({ in: a, out: R.challengePoints(a[0], a[1], a[2], cfg.fun.challenge) })),
  fever: [['2026-11-03', '13:59'], ['2026-11-03', '14:00'], ['2026-11-03', '14:59'], ['2026-11-03', '15:00'], ['2026-11-07', '14:30']].map(a => ({ in: a, out: R.feverInfo(R.emptyState('u'), R.toMs(a[0], a[1]), cfg, cal) })),
  scenario: funScenario()
};

fs.writeFileSync(path.join(__dirname, 'vectors.json'), JSON.stringify(V, null, 1));
console.log('vectors.json 만듦 · 시나리오', V.scenario.steps.length, '단계 · 행운 존', V.fun.scenario.steps.length, '단계');
