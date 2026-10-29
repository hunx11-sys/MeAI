// 규칙 엔진 점검 : (1) 바깥에서 확인된 사실(표준 SHA-256 값 · 조합 확률 · 달력) (2) 기준 벡터(vectors.json)와 같은지
// 쓰는 법 : node home_nudge/tests/rules.test.js   → 끝에 「통과 n / 실패 0」
const R = require('../src/core/rules.js');
const V = require('./vectors.json');
const cfg = require('../config/nudge.config.json');
const cal = require('../data/calendar.json');
let pass = 0, fail = 0;
function eq(name, got, exp) {
  const a = JSON.stringify(got), b = JSON.stringify(exp);
  if (a === b) pass++; else { fail++; console.log('✗', name, '\n   기대', b, '\n   실제', a); }
}

// 1) 바깥 사실
eq('sha256 빈 문자열(FIPS 180-4)', R.sha256hex(''), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
eq('sha256 abc(FIPS 180-4)', R.sha256hex('abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
eq('3개 일치 확률 C(6,3)C(39,3)/C(45,6)', +R.probMatch(45, 6, 3).toFixed(6), +(20 * 9139 / 8145060).toFixed(6));
eq('주 10세트 3개 이상 21.4%(기획안 v3)', +(R.probAnyOf(10, R.probAtLeast(45, 6, 3)) * 100).toFixed(1), 21.4);
eq('번호 35개 · 10세트 39.4%(기획안 v3)', +(R.probAnyOf(10, R.probAtLeast(35, 6, 3)) * 100).toFixed(1), 39.4);
eq('2026-10-29 는 ISO 44주', R.weekId('2026-10-29'), '2026-W44');
eq('2027-01-01 은 ISO 2026-W53', R.weekId('2027-01-01'), '2026-W53');
eq('한글날은 쉬는 날', R.isBizDay('2026-10-09', cal), false);
eq('개천절 대체공휴일', R.isBizDay('2026-10-05', cal), false);
eq('추첨 번호는 1~45 서로 다른 6개', (() => { const d = R.drawNumbers('x', 'r', 45, 6); return d.length === 6 && new Set(d).size === 6 && d.every(n => n >= 1 && n <= 45); })(), true);
eq('배지 · 퀘스트 설정이 엔진과 맞음', cfg.questSchedule.default.every(q => cfg.quests[q]), true);

// 2) 기준 벡터
V.dates.forEach(t => eq('날짜 ' + t.in, { weekId: R.weekId(t.in), weekLabel: R.weekLabel(t.in), monday: R.weekMonday(t.in), bizDay: R.isBizDay(t.in, cal), prevBizDay: R.prevBizDay(t.in, cal) },
  { weekId: t.weekId, weekLabel: t.weekLabel, monday: t.monday, bizDay: t.bizDay, prevBizDay: t.prevBizDay }));
V.sha256.forEach(t => eq('sha256 ' + JSON.stringify(t.in), R.sha256hex(t.in), t.out));
V.draw.forEach(t => eq('추첨 ' + t.in.slice(1).join(' '), R.drawNumbers.apply(null, t.in), t.out));
V.prob.forEach(t => eq('확률 ' + t.in.join(' '), +R.probAtLeast(t.in[0], t.in[1], t.in[2]).toFixed(8), t.atLeast));
V.copy.forEach(t => eq('따라 쓰기 ' + t.in[1], R.copyScore(t.in[0], t.in[1]), t.out));
V.mask.forEach(t => eq('이름 가리기 ' + t.in, R.maskName(t.in), t.out));

(function () {
  const st = R.emptyState('u-test'), quiz = { id: 'q1', answer: 'X' }, talk = { id: 't1', head: '고객이 먼저 떠올리는 한 사람이 되자.' }, user = { id: 'u-test', name: '시험', joinMonth: 2 };
  let n = 0;
  V.scenario.steps.forEach(s => {
    const [d, hm] = s.at.split(' '), now = R.toMs(d, hm);
    const out = R.evaluate(st, s.ev, { cfg, cal, now, rand: R.rng(1000 + (++n)), user, recoToday: ['c1', 'c2'], quiz: Object.assign({}, quiz, { id: s.ev.quizId || 'q1' }), talk, league: null });
    const si = R.streakInfo(st, d, now, cal, cfg), qs = R.questSummary(st, d, cfg);
    eq('시나리오 ' + s.at + ' ' + s.ev.kind, {
      ok: out.ok, reason: out.reason, grants: out.grants.map(g => [g.type, g.amount, g.rule]), fx: out.fx.map(f => f.type),
      after: { streak: si.current, best: si.best, shields: st.wallet.shields, quests: qs.done, weekXp: (st.weeks[R.weekId(d)] || {}).xp, tickets: (st.weeks[R.weekId(d)] || {}).tickets,
        sets: Object.keys(st.weeks).reduce((a, w) => a + st.weeks[w].sets.length, 0) }
    }, { ok: s.ok, reason: s.reason, grants: s.grants, fx: s.fx, after: s.after });
  });
})();

V.shield.forEach(t => {
  const st = R.emptyState('u-s'), c = d => ({ cfg, cal, now: R.toMs(d, '09:00'), rand: R.rng(1), user: {}, recoToday: [], quiz: null, talk: null, league: null });
  ['2026-11-02', '2026-11-03'].forEach(d => R.evaluate(st, { kind: 'attend' }, c(d)));
  const out = R.evaluate(st, { kind: 'attend' }, c(t.back));
  eq('보호권 빈 영업일 ' + t.missDays + '일', { fx: out.fx.map(f => f.type), shieldsLeft: st.wallet.shields, streak: R.streakInfo(st, t.back, R.toMs(t.back, '09:00'), cal, cfg).current },
    { fx: t.fx, shieldsLeft: t.shieldsLeft, streak: t.streak });
});
eq('빈 영업일 2일 = 보호권 2장으로 메움', V.shield[1].shieldsLeft === 0 && V.shield[1].streak === 3, true);
eq('빈 영업일 3일 = 보호권을 쓰지 않고 새로 시작', V.shield[2].shieldsLeft === 2 && V.shield[2].streak === 1, true);
eq('올클리어 = 하루 5개', V.scenario.steps.some(s => s.fx.indexOf('allclear') >= 0), true);

console.log('\n통과 ' + pass + ' / 실패 ' + fail);
process.exit(fail ? 1 : 0);
