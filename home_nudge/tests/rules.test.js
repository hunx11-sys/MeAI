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

// 3) 행운 존 (v5.1)
(function () {
  const F = V.fun, segs = cfg.fun.roulette.segments, wsum = segs.reduce((a, x) => a + x.weight, 0);
  eq('룰렛 가중치 그대로 나옴(1만 번 · 칸마다 ±1.5%p)', F.weighted.counts.every((c, i) => Math.abs(c / F.weighted.n - segs[i].weight / wsum) < 0.015), true);
  { const r = R.rng(F.weighted.seed), c = segs.map(() => 0); for (let i = 0; i < F.weighted.n; i++) c[R.pickWeighted(r, segs)]++; eq('룰렛 벡터', c, F.weighted.counts); }
  F.tarot.forEach(t => eq('오늘의 타로 ' + t.in[1], R.tarotOfDay.apply(null, t.in), t.out));
  eq('타로 세 장은 0~21 서로 다른 카드', F.tarot.every(t => t.out.length === 3 && new Set(t.out).size === 3 && t.out.every(x => x >= 0 && x < 22)), true);
  F.points.forEach(t => eq('OX 점수 ' + t.in.join(' '), R.challengePoints(t.in[0], t.in[1], t.in[2], cfg.fun.challenge), t.out));
  F.fever.forEach(t => eq('피버 ' + t.in.join(' '), R.feverInfo(R.emptyState('u'), R.toMs(t.in[0], t.in[1]), cfg, cal), t.out));
  eq('피버는 14:00~14:59 만, 주말은 없음', F.fever.map(t => t.out.on), [false, true, true, false, false]);
  eq('슬롯 · 스크래치 가중치 합 100', [cfg.fun.cslot.tiers, cfg.fun.scratch.prizes, segs].map(l => l.reduce((a, x) => a + x.weight, 0)), [100, 100, 100]);
  eq('빙고 9칸 · 줄 8개', [cfg.bingo.cells.length, R.BINGO_LINES.length], [9, 8]);
  const S = F.scenario, st = R.emptyState('u-fun'), user = { id: 'u-fun', name: '시험', joinMonth: 20 }, quiz = { id: 'q-f', answer: 'O' };
  const bank = S.bank.map(q => Object.assign({ q: q.id + ' 문제', why: q.id + ' 해설', src: '시험' }, q));
  let n = 0;
  S.steps.forEach(s => {
    const out = R.evaluate(st, s.ev, { cfg, cal, now: R.toMs(S.day, s.at), rand: R.rng(5000 + (++n)), user, recoToday: ['c1'], quiz, talk: null, league: null, crm: S.crm, oxBank: bank });
    eq('행운 존 ' + s.at + ' ' + s.ev.kind, { ok: out.ok, reason: out.reason, grants: out.grants.map(g => [g.type, g.amount, g.rule]), fx: out.fx.map(f => f.type), data: out.data || null,
      after: { weekXp: (st.weeks[R.weekId(S.day)] || {}).xp, tickets: (st.weeks[R.weekId(S.day)] || {}).tickets, best: st.fun.best } },
      { ok: s.ok, reason: s.reason, grants: s.grants, fx: s.fx, data: s.data, after: s.after });
  });
  eq('행운 존 빙고 상태', R.bingoState(st, S.day, cfg), S.bingo);
  eq('행운 존 남은 기회', R.funPlays(st, S.day, cfg), S.plays);
  eq('룰렛은 하루 1번 + 일일 미션 보너스 1번', S.steps.filter(s => s.ev.kind === 'roulette.spin').map(s => s.ok), [true, false, true]);
  eq('OX 만점은 응모권 +1 (하루 한 번)', S.steps.filter(s => s.grants.some(g => g[2] === 'challenge.perfect')).length, 1);
  eq('오후 피버에 고객 챙기기 XP 2배', S.steps.filter(s => s.ev.kind === 'crm.done' && s.ok && s.at >= '14:00' && s.at < '15:00').every(s => s.data.mult === 2), true);
  eq('스크래치는 일일 미션 때 발급 · 한 번만 긁힘', S.steps.filter(s => s.ev.kind === 'scratch.reveal').map(s => s.ok), [true, false]);
  // 운으로 받는 응모권 하루 한도 : 넘치면 XP 로
  const st2 = R.emptyState('u-cap'), c2 = (hm, i) => ({ cfg, cal, now: R.toMs('2026-11-03', hm), rand: () => 0.99, user, recoToday: [], quiz: null, talk: null, league: null, crm: S.crm, oxBank: bank });
  const capCfg = JSON.parse(JSON.stringify(cfg)); capCfg.fun.plays.roulette = 5; capCfg.fun.roulette.segments.forEach(x => { x.weight = x.id === 'bonus_ticket' ? 1 : 0; });
  const spins = [1, 2, 3, 4].map(i => R.evaluate(st2, { kind: 'roulette.spin' }, Object.assign(c2('10:0' + i), { cfg: capCfg })));
  eq('운 응모권 하루 3장까지 · 4번째는 XP', spins.map(o => o.grants.filter(g => g.type === 'ticket').length + (o.fx.some(f => f.type === 'capped') ? 'x' : '')), ['1', '1', '1', '0x']);
})();

console.log('\n통과 ' + pass + ' / 실패 ' + fail);
process.exit(fail ? 1 : 0);
