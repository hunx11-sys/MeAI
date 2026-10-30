/* MeAI 홈 넛지 v5 · 모의 서버
 *
 * src/api/client.js(실서버 호출)와 함수 이름 · 응답 모양이 똑같다. 목업과, 서버가 아직 없을 때의 화면 개발에 쓴다.
 * 계산은 전부 src/core/rules.js 에 맡기고, 여기서는 (1) 예시 기록 만들기 (2) 화면용 요약(home) 만들기 (3) 데모 시계만 한다.
 * 화면에 나가는 숫자 중 seed.baseline 만 실제 분석값이고 나머지는 모두 예시다.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('../core/rules.js'));
  else root.NZMock = factory(root.NZRules);
})(typeof self !== 'undefined' ? self : this, function (R) {
  'use strict';

  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function mod(a, n) { return ((a % n) + n) % n; }
  var DEFAULT_SETTINGS = { fx: 'full', sound: false, hideRank: false, buddy: true, tickerSec: 8, tickerCats: null, tickerOrder: 'mix', showBlocked: false, showShort: false };
  var ELEMENTS = [['일반대화', 'chat.general'], ['맞춤대화', 'chat.custom'], ['MeAI 고객찾기', 'find'], ['오늘의 추천 고객', 'reco.open'], ['고객 동의', 'consent'], ['게시판', 'board'],
    ['출석', 'attend'], ['오늘의 퀴즈', 'quiz'], ['오늘의 화법', 'talk'], ['퀘스트', 'quest'], ['로또(행운번호)', 'lotto'], ['리그', 'league'], ['MeAI 대시보드', 'dash']];

  function createMockApi(data, opts) {
    opts = opts || {};
    var cfg0 = data.cfg, cal = data.cal, seed = data.seed;
    var cfg, st, user, peers, peersPrev, clock, dismissed, quizSwap, recapForce, latency = opts.latency == null ? 40 : opts.latency;
    var talks = data.talks.items, talkById = {};
    talks.forEach(function (t) { talkById[t.id] = t; });
    var mine = []; // 내가 제출한 화법(검수 대기)
    var logs = []; // 화면이 보낸 사용 기록(대시보드 원천)
    var recoList = (seed.reco || []).map(function (c) { return { id: c.id, name: c.name, tags: c.tags || [] }; }); // 오늘의 추천 고객 (화면 어댑터가 실제 카드로 바꿔 넣는다)

    // ── 화법 순서 : 카테고리를 번갈아 섞는다 (배너 기본 = 검토 필요 제외)
    function interleave(list) {
      var by = {}, cats = Object.keys(data.talks.cats), out = [], more = true;
      list.forEach(function (t) { (by[t.cat] = by[t.cat] || []).push(t); });
      for (var i = 0; more; i++) { more = false; cats.forEach(function (c) { if (by[c] && by[c][i]) { out.push(by[c][i]); more = true; } }); }
      return out;
    }
    function bannerList() {
      var s = st.settings, cats = s.tickerCats;
      var list = talks.filter(function (t) { return (s.showBlocked || t.review !== 'block') && (s.showShort || !t.noise) && (!cats || cats.indexOf(t.cat) >= 0); });
      if (s.tickerOrder === 'rec') list = list.slice().sort(function (a, b) { return (b.grade === 'rec') - (a.grade === 'rec'); });
      else if (s.tickerOrder === 'random') { var rr = R.rng(R.diffDays('2026-01-01', today())); list = list.slice().sort(function () { return rr() - 0.5; }); }
      else list = interleave(list);
      return list.length ? list : interleave(talks.filter(bannerOk));
    }
    function bannerOk(t) { return t.review !== 'block' && !t.noise; }
    // 오늘의 화법 = 추천(rec) 화법을 카테고리 번갈아 하루 한 건
    function talkOfDay(day) { var l = interleave(talks.filter(function (t) { return bannerOk(t) && t.grade === 'rec'; })); return l[mod(R.diffDays('2026-10-01', day) * 7, l.length)]; }

    // ── 퀴즈 : 날짜에 맞는 문항, 없으면 돌려 쓴다 (9시 공개)
    function quizOfDay(day) {
      var items = data.quiz.items, q = null;
      items.forEach(function (x) { if (x.date === day) q = x; });
      if (quizSwap && day === today()) q = items.filter(function (x) { return x.type === 'choice'; })[0];
      if (q) return q;
      // 날짜별 문항이 없는 날 : OX 문제 은행에서 갈래를 번갈아 하루 한 문항 (id 는 그날 것으로)
      var ox = data.ox && data.ox.items, cats = data.ox && data.ox.cats;
      if (ox && ox.length) {
        var x = interleaveOx()[mod(R.diffDays('2026-10-01', day), ox.length)];
        return { id: 'q-' + x.id + '@' + day, date: day, type: 'ox', category: cats[x.cat].label, question: x.q, answer: x.a, explain: [x.why].concat(x.more || []), source: x.src, ask: x.q + ' 이 내용을 고객에게 쉽게 설명해 줘' };
      }
      q = clone(items[mod(R.diffDays('2026-10-01', day), items.length)]); q.id = q.id + '@' + day; q.date = day;
      return q;
    }
    var oxOrder = null;
    function interleaveOx() {
      if (oxOrder) return oxOrder;
      var by = {}, keys = [];
      data.ox.items.forEach(function (x) { if (!by[x.cat]) { by[x.cat] = []; keys.push(x.cat); } by[x.cat].push(x); });
      oxOrder = [];
      for (var i = 0; oxOrder.length < data.ox.items.length; i++) keys.forEach(function (k) { if (by[k][i]) oxOrder.push(by[k][i]); });
      return oxOrder;
    }
    function today() { return R.kst(clock.now).ymd; }
    // 데모 시계 : 정한 시각부터 실제 시간처럼 흐른다 (opts.frozen 이면 멈춘 시계)
    function makeClock(base) {
      var at = Date.now();
      return { get now() { return opts.frozen ? base : base + (Date.now() - at); }, set now(v) { base = v; at = Date.now(); } };
    }
    function recoToday() { return recoList.map(function (c) { return c.id; }); }
    function seedOf(round) { return R.sha256hex('meai-demo-seed|' + round); } // 목업 전용. 실서버는 회차 시작 때 CSPRNG 로 만든다.

    function ctx(now, extra) {
      var c = { cfg: cfg, cal: cal, now: now, rand: R.rng(Math.floor(now / 1000)), user: user, recoToday: recoToday(),
        quiz: quizOfDay(R.kst(now).ymd), talk: null, league: { me: user, peers: peers }, crm: seed.crm || [], oxBank: (data.ox && data.ox.items) || [] };
      for (var k in extra) c[k] = extra[k];
      return c;
    }

    // ── 예시 기록 만들기 : 7월 1일부터 어제까지 규칙 엔진에 행동을 차례로 넣는다
    function seedHistory() {
      var hc = clone(cfg); hc.streak.shieldsPerMonth = 0;
      hc.pass.forEach(function (p) { if (p.reward.shield) p.reward = {}; });
      var r = R.rng(7741), end = R.addDays(seed.today, -1), d = '2026-07-01';
      // 23영업일 연속(최고 기록) → 9/28 끊김 → … → 10/13 끊김 → 10/14 부터 어제까지 연속
      var runEnd = '2026-09-23', runStart = runEnd;
      for (var i = 0; i < 22; i++) runStart = R.prevBizDay(runStart, cal);
      var beforeRun = R.prevBizDay(runStart, cal), forcedMiss = {}, wkMon = R.weekMonday(seed.today);
      forcedMiss[beforeRun] = 1; forcedMiss['2026-09-28'] = 1; forcedMiss['2026-10-13'] = 1;
      var n = 0;
      for (; d <= end; d = R.addDays(d, 1)) {
        if (!R.isBizDay(d, cal)) continue;
        var forced = (d >= runStart && d <= runEnd) || d >= '2026-10-14';
        var lit = forcedMiss[d] ? false : forced ? true : r() < 0.72;
        var at = function (hm) { return R.toMs(d, hm); };
        var c = { cfg: hc, cal: cal, rand: R.rng(++n * 977), user: user, recoToday: [], quiz: null, talk: null, league: null };
        var evs = [], ids = [d.replace(/-/g, '') + 'a', d.replace(/-/g, '') + 'b', d.replace(/-/g, '') + 'c'];
        c.recoToday = ids;
        var attend = lit && (d >= wkMon || r() < 0.86);
        if (attend) evs.push(['08:' + (30 + Math.floor(r() * 29)), { kind: 'attend' }]);
        if (r() < (lit ? 0.82 : 0.2)) {
          var qz = quizOfDay(d), ok = r() < 0.76;
          c.quiz = qz;
          var wrong = qz.type === 'ox' ? (qz.answer === 'O' ? 'X' : 'O') : String((+qz.answer + 1) % 4);
          evs.push(['09:' + (10 + Math.floor(r() * 40)), { kind: 'quiz.answer', quizId: qz.id, choice: ok ? qz.answer : wrong }]);
          if (!ok && r() < 0.7) evs.push(['09:55', { kind: 'quiz.explained' }]);
        }
        if (lit) {
          var nr = 1 + Math.floor(r() * 2.2);
          for (var k = 0; k < nr; k++) {
            evs.push(['1' + (0 + k) + ':' + (10 + Math.floor(r() * 40)), { kind: 'reco.open', customerId: ids[k], tags: r() < 0.3 ? ['age_up'] : [] }]);
            if (r() < 0.55) evs.push(['1' + (0 + k) + ':55', { kind: 'chat.custom', customerId: ids[k] }]);
          }
          for (var g = Math.floor(r() * 3); g > 0; g--) evs.push(['13:' + (10 + g * 9), { kind: 'chat.general' }]);
          if (r() < 0.35) evs.push(['11:20', { kind: 'notice.read', ref: 'n-' + d }]);
          if (r() < 0.38) { c.talk = talkOfDay(d); evs.push(['12:40', { kind: 'talk.copy', talkId: c.talk.id, typed: c.talk.head }]); }
          if (r() < 0.14) evs.push(['15:30', { kind: 'consent.request', customerId: ids[0] }]);
        }
        evs.sort(function (a, b) { return a[0] < b[0] ? -1 : 1; }).forEach(function (e) { c.now = at(e[0]); c.rand = R.rng(++n * 131); R.evaluate(st, e[1], c); });
        if (d >= wkMon && lit) { // 이번 주 : 고객 룰렛을 돌리고 한 명을 챙김 (행운 존 · 빙고 예시)
          c.crm = seed.crm || []; c.now = at('10:40'); c.rand = R.rng(++n * 131);
          var sp = R.evaluate(st, { kind: 'roulette.spin' }, c);
          if (sp.ok && sp.data.customers[0]) { c.now = at('10:48'); R.evaluate(st, { kind: 'crm.done', ref: 'r:' + sp.data.spinId, customerId: sp.data.customers[0] }, c); }
        }
      }
      // 이번 주 패스 2단계 보상(보호권)을 다시 반영하고 10월 보호권 상태를 맞춘다
      st.wallet.shields = 1; st.wallet.shieldMonth = R.kst(clock.now).ymd.slice(0, 7);
      st.fun.scratch.forEach(function (x, i, all) { if (i < all.length - 1) x.revealed = R.toMs(x.day, '18:00'); });   // 지난 스크래치는 긁은 것으로 · 어제 받은 1장만 남김
      st.preparedDay = '';
      st.ledger = st.ledger.filter(function (g) { return g.amount; });
    }

    function boot(persona) {
      cfg = clone(cfg0);
      if (opts.issueOn) cfg.lotto.issueOn = opts.issueOn;
      if (opts.altName != null) cfg.labels.useAltLottoName = !!opts.altName;
      user = clone(seed.users[persona || 'fp']);
      if (user.role !== 'FP') user = Object.assign(clone(seed.users.fp), { viewer: user });
      clock = makeClock(R.toMs(seed.today, seed.startTime));
      dismissed = {}; quizSwap = false; recapForce = false; mine = [];
      st = R.emptyState(user.id);
      st.settings = clone(DEFAULT_SETTINGS);
      if (cfg.fx && cfg.fx.soundDefault) st.settings.sound = true;
      peers = []; peersPrev = {};
      if (persona === 'rookie') { user = clone(seed.users.rookie); st = R.emptyState(user.id); st.settings = clone(DEFAULT_SETTINGS); st.wallet.shields = 2; st.wallet.shieldMonth = '2026-10'; }
      else seedHistory();
      var myXp = (st.weeks[R.weekId(seed.today)] || { xp: 0 }).xp, pr = R.rng(99);
      peers = seed.peers.map(function (p) { return { id: p.id, name: p.name, xp: Math.max(12, myXp + p.offset + (persona === 'rookie' ? -40 : 0)), at: p.at }; });
      peers.forEach(function (p) { peersPrev[p.id] = Math.floor(pr() * 10) + 1; });
      st.persona = persona || 'fp';
    }

    // ── 화면용 요약 ─────────────────────────────────────────────
    function settingsOf() { var s = clone(DEFAULT_SETTINGS); for (var k in st.settings) s[k] = st.settings[k]; return s; }
    function weekView(day, now) {
      return R.weekDays(day).map(function (d) {
        var rec = st.days[d], hol = cal.holidays[d];
        var state = hol ? 'holiday' : d > day ? 'future' : rec && rec.attend ? 'stamp' : d === day ? 'today' : rec && rec.lit ? 'lit' : rec && rec.shield ? 'shield' : 'miss';
        return { day: d, dow: R.dow(d), state: state, holiday: hol || '' };
      });
    }
    function lottoView(now) {
      var lw = R.lottoWindow(now, cfg), cur = st.weeks[lw.round] || { sets: [] }, pool = cfg.lotto.pool, pick = cfg.lotto.pick;
      var p3 = R.probAtLeast(pool, pick, 3), draw = null, prevRound = R.weekId(R.addDays(R.weekMonday(today()), -7));
      if (lw.phase === 'drawn') draw = R.drawNumbers(seedOf(lw.round), lw.round, pool, pick);
      var sets = cur.sets.map(function (s, i) {
        var o = { no: i + 1, nums: s.nums, ts: s.ts, customer: customerLabel(s.customerId) };
        if (draw) { o.match = R.matchCount(s.nums, draw); var tr = R.tierFor(o.match, cfg); o.prize = tr ? tr.prize : ''; }
        return o;
      });
      var next = lw.issueRound !== lw.round ? (st.weeks[lw.issueRound] || { sets: [] }).sets.length : 0;
      var pd = R.drawNumbers(seedOf(prevRound), prevRound, pool, pick), ps = (st.weeks[prevRound] || { sets: [] }).sets, best = 0;
      ps.forEach(function (s) { best = Math.max(best, R.matchCount(s.nums, pd)); });
      var bestTier = R.tierFor(best, cfg);
      var r = st.days[today()] || { lotto: 0 };
      return {
        name: R.labelLotto(cfg), round: lw.round, label: lw.label, phase: lw.phase, cutoffAt: lw.cutoffAt, drawAt: lw.drawAt,
        sets: sets, nextRoundSets: next, todayIssued: r.lotto || 0, dailyMax: cfg.lotto.dailyMax, issueOn: cfg.lotto.issueOn,
        commit: R.sha256hex(seedOf(lw.round)), seed: lw.phase === 'drawn' ? seedOf(lw.round) : '',
        draw: draw, drawSeen: !!(st.seen.draw && st.seen.draw[lw.round]),
        last: { round: prevRound, label: R.weekLabel(R.addDays(R.weekMonday(today()), -7)), nums: pd, sets: ps.length, best: best, prize: bestTier ? bestTier.prize : '' },
        odds: { pool: pool, pick: pick, p3: p3, p4: R.probAtLeast(pool, pick, 4), p5: R.probAtLeast(pool, pick, 5), mine: R.probAnyOf(sets.length, p3), ten: R.probAnyOf(10, p3), ten35: R.probAnyOf(10, R.probAtLeast(35, pick, 3)) },
        tiers: cfg.lotto.tiers
      };
    }
    function customerLabel(id) { var c = recoList.filter(function (x) { return x.id === id; })[0]; return c ? R.maskName(c.name) + ' 고객' : '추천 고객'; }
    function leagueView(now) {
      var wid = R.weekId(today()), lr = R.leagueRank(st, wid, ctx(now)), w = st.weeks[wid] || { xp: 0, pass: {} };
      var cheersToday = st.cheers[today()] || {};
      var list = lr.list.map(function (x) {
        return { id: x.id, rank: x.rank, name: x.me ? user.name : R.maskName(x.name), xp: x.xp, me: x.me,
          frame: x.me ? (w.frame || '') : x.rank === 1 ? 'gold' : '', trend: x.me ? 0 : (peersPrev[x.id] || x.rank) - x.rank, cheered: !!cheersToday[x.id] };
      });
      var hint = R.catchUpHint(lr.gap, cfg);
      var pass = cfg.pass.map(function (m, i) { return { xp: m.xp, label: m.label, reached: w.xp >= m.xp }; });
      var nextPass = null; for (var i = 0; i < pass.length; i++) if (!pass[i].reached) { nextPass = pass[i]; break; }
      return { scope: 'branch', branch: user.branch, week: wid, weekLabel: R.weekLabel(today()), rank: lr.rank, total: lr.total, gap: lr.gap, hint: hint,
        goldCut: cfg.league.goldCut, list: list, xp: w.xp, pass: pass, nextPass: nextPass, frame: w.frame || '',
        cheersLeft: cfg.cheer.dailyMax - Object.keys(cheersToday).length, cheersReceived: seed.cheersReceived.map(function (c) { return { from: R.maskName(c.from), at: c.at }; }) };
    }
    // ── 행운 존 요약 (룰렛 · 슬롯 · 스크래치 · OX 챌린지 · 타로 · 빙고 · 피버)
    function funView(now) {
      var day = R.kst(now).ymd, f = st.fun, fd = R.funDay(st, day), F = cfg.fun, pl = R.funPlays(st, day, cfg);
      var bg = R.bingoState(st, day, cfg), wb = (st.weeks[R.weekId(day)] || {}).bingo || {}, crmById = {};
      (seed.crm || []).forEach(function (c) { crmById[c.id] = c; });
      function cust(id, doneMap) { var c = crmById[id]; return c ? { id: id, name: R.maskName(c.name), age: c.age, sym: c.sym, note: c.note, done: !!(doneMap && doneMap[id]) } : null; }
      function pct(list) { var sum = list.reduce(function (a, x) { return a + x.weight; }, 0); return list.map(function (x) { return Math.round(x.weight / sum * 1000) / 10; }); }
      var segs = F.roulette.segments, sp = pct(segs), tp = pct(F.cslot.tiers), zp = pct(F.scratch.prizes);
      return {
        plays: pl, fever: R.feverInfo(st, now, cfg, cal), capLeft: Math.max(0, F.ticketCapDaily - fd.tickets), cap: F.ticketCapDaily,
        roulette: { segments: segs.map(function (x, i) { return { id: x.id, label: x.label, color: x.color, pct: sp[i], bonus: !!x.prize, xp: x.xp || 0 }; }),
          spins: fd.spins.map(function (x) { var g = segs[x.seg]; return { id: x.id, seg: x.seg, segId: g.id, label: g.label, tpl: g.tpl || '', xp: g.xp || 0, bonus: !!g.prize, fallback: x.fallback,
            customers: x.customers.map(function (c) { return cust(c, x.done); }).filter(Boolean) }; }) },
        cslot: { symbols: F.cslot.symbols, odds: F.cslot.tiers.map(function (x, i) { return { id: x.id, label: x.label, pct: tp[i] }; }), prizes: F.cslot.prizes, xpContact: F.cslot.xpContact, clearXp: F.cslot.clearXp,
          pulls: fd.pulls.map(function (x) { return { id: x.id, tier: x.tier, reels: x.reels, cleared: !!x.cleared, customers: x.customers.map(function (c) { return cust(c, x.done); }).filter(Boolean) }; }) },
        scratch: { cards: f.scratch.filter(function (x) { return !x.revealed && R.diffDays(x.day, day) <= F.scratch.validDays; }).map(function (x) { return { id: x.id, from: x.from, day: x.day }; }),
          today: f.scratch.filter(function (x) { return x.revealed && R.kst(x.revealed).ymd === day; }).map(function (x) { return { id: x.id, label: F.scratch.prizes[x.prize].label }; }),
          odds: F.scratch.prizes.map(function (x, i) { return { label: x.label, pct: zp[i] }; }), issueOn: F.scratch.issueOn },
        challenge: { best: f.best || 0, runsToday: fd.runs, perfectToday: !!fd.perfect, n: F.challenge.n, sec: F.challenge.sec, bank: ((data.ox && data.ox.items) || []).length,
          cats: data.ox ? data.ox.cats : {}, max: F.challenge.n * (F.challenge.base + F.challenge.sec * F.challenge.speed) + F.challenge.combo * (F.challenge.n - 1) * F.challenge.n / 2 },
        tarot: { today: fd.tarot ? { card: fd.tarot.card, pick: fd.tarot.pick, three: fd.tarot.three } : null, cards: F.tarot.cards },
        bingo: { week: bg.week, cells: bg.cells, lines: bg.lines, count: bg.count, filled: bg.filled,
          rewards: cfg.bingo.rewards.map(function (m, i) { return { lines: m.lines, ticket: m.ticket, label: m.label, got: !!wb[i] }; }) },
        fortune: { example: seed.fortuneExample || null, sentToday: !!(st.days[day] && st.days[day].kinds['fortune.send']) }
      };
    }
    function buddyView(now, s, q, lotto) {
      if (!st.settings.buddy) return null;
      var t = R.kst(now), r = st.days[t.ymd] || {}, d = dismissed[t.ymd] || {};
      var facts = { attended: !!r.attend, quizDone: !!r.quizDone, talkCopied: !!r.talkCopied, lit: !!r.lit,
        drawSeen: lotto.drawSeen, questLeft: q.total - q.done, nextStreak: s.nextStreak, bizDay: R.isBizDay(t.ymd, cal), rouletteLeft: R.funPlays(st, t.ymd, cfg).roulette.left };
      if (!R.isBizDay(t.ymd, cal) && !(t.dow === 5)) return null;
      var b = R.pickBuddy(cfg.buddy, facts, t.hm, t.dow, d);
      if (!b) return null;
      return { id: b.id, mascot: b.mascot, text: b.text.replace('{nextStreak}', s.nextStreak), cta: b.cta };
    }
    function home() {
      var now = clock.now, t = R.kst(now), day = t.ymd, wid = R.weekId(day);
      R.prepareDay(st, day, cal, cfg, null);
      var s = R.streakInfo(st, day, now, cal, cfg), q = R.questSummary(st, day, cfg), r = R.dayRec(st, day), w = R.weekRec(st, wid);
      var qz = quizOfDay(day), h = st.quizHist[qz.id], open = t.hm >= '09:00' || day !== seed.today && t.hm >= '09:00';
      var quiz = { id: qz.id, type: qz.type, category: qz.category, question: qz.question, options: qz.options || null, open: t.hm >= '09:00', openAt: R.toMs(day, '09:00'),
        answered: !!h, combo: st.combo || 0 };
      if (h) {
        quiz.choice = h.choice; quiz.correct = h.correct; quiz.explained = h.explained; quiz.answer = qz.answer; quiz.explain = qz.explain; quiz.source = qz.source; quiz.ask = qz.ask;
        var br = R.rng(qz.id.length * 31 + qz.id.charCodeAt(qz.id.length - 1));
        quiz.stats = { branchRate: 52 + Math.floor(br() * 30), companyRate: 48 + Math.floor(br() * 25), participants: 3200 + Math.floor(br() * 2400), example: true };
      }
      var bl = bannerList(), ti = mod(R.diffDays('2026-10-01', day), bl.length);
      var ticker = []; for (var i = 0; i < Math.min(12, bl.length); i++) ticker.push(talkLite(bl[(ti + i) % bl.length]));
      var lotto = lottoView(now), league = leagueView(now);
      var todayTickets = st.ledger.filter(function (g) { return g.day === day && g.type === 'ticket'; }).reduce(function (a, g) { return a + g.amount; }, 0);
      var recoIssued = {};
      Object.keys(r.reco).forEach(function (cid) { recoIssued[cid] = { opened: true, lotto: !!r.reco[cid].lotto }; });
      var ob = null;
      if (user.joinMonth <= cfg.onboarding.maxJoinMonth) ob = { joinMonth: user.joinMonth, steps: cfg.onboarding.steps.map(function (x) { return { kind: x.kind, title: x.title, text: x.text, done: !!st.firsts[x.kind] }; }) };
      var cmpMe = seed.compare.me + (r.kinds['chat.custom'] || 0);
      return {
        serverTime: now, today: day, hm: t.hm, dow: t.dow, bizDay: R.isBizDay(day, cal), holiday: cal.holidays[day] || '', version: cfg.version,
        user: { id: user.id, name: user.name, branch: user.branch, hq: user.hq, role: user.role, joinMonth: user.joinMonth, rookie: !!ob, viewer: user.viewer ? { role: user.viewer.role, name: user.viewer.name } : null },
        labels: { lotto: R.labelLotto(cfg), ticket: cfg.labels.ticket, shield: cfg.labels.shield },
        settings: settingsOf(),
        streak: { current: s.current, best: s.best, todayLit: s.todayLit, nextStreak: s.nextStreak, nextMilestone: s.nextMilestone, atRisk: s.atRisk, shields: s.shields, last10: s.last10, topPercent: seed.topPercent,
          nextBadge: (cfg.badges.filter(function (b) { return b.type === 'streak' && b.n > s.current; })[0] || null) },
        week: { id: wid, label: R.weekLabel(day), days: weekView(day, now), attended: R.weekDays(day).filter(function (d) { return st.days[d] && st.days[d].attend; }).length,
          bizDays: R.weekDays(day).filter(function (d) { return R.isBizDay(d, cal); }).length, perfect: !!w.perfect, xp: w.xp },
        attendedToday: !!r.attend,
        wallet: { tickets: w.tickets, todayTickets: todayTickets, sets: lotto.sets.length + lotto.nextRoundSets, shields: st.wallet.shields, badges: Object.keys(st.wallet.badges).length,
          today: st.ledger.filter(function (g) { return g.day === day; }).slice(-12).reverse(), coffee: { winners: cfg.coffeeDraw.winners, prize: cfg.coffeeDraw.prize, poolAssumed: 38000 } },
        quests: Object.assign(q, { next: (function () { var nd = R.addDays(day, 1); while (!R.isBizDay(nd, cal)) nd = R.addDays(nd, 1); return { date: nd, titles: R.questIds(nd, cfg).map(function (id) { return cfg.quests[id].title; }), changed: !!cfg.questSchedule[nd] }; })() }),
        quiz: quiz,
        talk: { today: talkFull(talkOfDay(day)), ticker: ticker, copiedToday: !!r.talkCopied, total: data.talks.stats.src, banner: data.talks.stats.banner },
        lotto: lotto,
        league: league,
        team: { branch: user.branch, title: seed.team.title, metric: seed.team.metric, value: seed.team.value + (r.kinds['chat.custom'] || 0), target: seed.team.target, members: seed.team.members, joined: seed.team.joined, example: true },
        compare: { metric: seed.compare.metric, me: cmpMe, branchAvg: seed.compare.branchAvg, nonUser: seed.compare.nonUser, ratio: Math.round(cmpMe / seed.compare.nonUser * 10) / 10, example: true },
        reco: { issued: recoIssued, todayIssued: r.lotto || 0, dailyMax: cfg.lotto.dailyMax, issueOn: cfg.lotto.issueOn },
        buddy: buddyView(now, s, q, lotto),
        notices: { unread: seed.notices.filter(function (n) { return n.unread && !(st.seen.notice && st.seen.notice[n.id]); }).length },
        onboarding: ob,
        recap: { available: recapForce || (t.dow === 5 && t.hm >= cfg.lotto.drawAt) || t.dow === 6 || t.dow === 0, week: wid, seen: !!(st.seen.recap && st.seen.recap[wid]) },
        myCustomers: seed.myCustomers,
        fun: funView(now)
      };
    }
    function talkLite(t) { return { id: t.id, cat: t.cat, catName: data.talks.cats[t.cat].name, head: t.head, review: t.review }; }
    function talkFull(t) {
      if (!t) return null;
      var o = clone(t); o.catName = data.talks.cats[t.cat].name;
      o.liked = !!st.talks.liked[t.id]; o.saved = !!st.talks.saved[t.id]; o.usedByMe = !!st.talks.used[t.id]; o.copied = !!st.talks.copied[t.id];
      o.likes = t.likes + (o.liked ? 1 : 0); o.usedCount = t.used + (o.usedByMe ? 1 : 0);
      return o;
    }

    // ── 공통 : 행동 하나를 규칙 엔진에 넣고 새 요약을 돌려준다 ──────────
    function act(ev, extra) {
      var out = R.evaluate(st, ev, ctx(clock.now, extra || {}));
      return reply({ ok: out.ok, reason: out.reason, grants: out.grants, fx: out.fx, data: out.data || null, home: home() });
    }
    function reply(v) { return new Promise(function (res) { setTimeout(function () { res(clone(v)); }, latency); }); }

    // ── 대시보드용 예시 숫자 (결정적 난수) ──────────────────────────
    function recordView() {
      var day = today(), from = '2026-07-01', cells = [], months = {}, nums = { days: 0, questions: 0, customers: 0, attend: 0, talks: 0, quizOk: 0, quizN: 0 };
      for (var d = from; d <= R.addDays(day, 0); d = R.addDays(d, 1)) {
        var rec = st.days[d], hol = cal.holidays[d], biz = R.isBizDay(d, cal);
        if (R.dow(d) === 0 || R.dow(d) === 6) continue;
        var stt = hol ? 'holiday' : !rec ? (d === day ? 'today' : 'miss') : rec.attend ? 'attend' : rec.lit ? 'lit' : rec.shield ? 'shield' : (d === day ? 'today' : 'miss');
        var lvl = rec ? Math.min(4, Math.ceil(((rec.kinds['chat.custom'] || 0) * 2 + (rec.kinds['reco.open'] || 0) + (rec.kinds['chat.general'] || 0) + (rec.attend ? 1 : 0)) / 2)) : 0;
        cells.push({ day: d, state: stt, level: lvl, holiday: hol || '' });
        var m = d.slice(0, 7); months[m] = months[m] || { biz: 0, lit: 0 };
        if (biz) { months[m].biz++; if (rec && rec.lit) months[m].lit++; }
        if (rec) {
          if (rec.lit) nums.days++;
          nums.questions += (rec.kinds['chat.custom'] || 0) + (rec.kinds['chat.general'] || 0);
          nums.customers += Object.keys(rec.reco).length;
          if (rec.attend) nums.attend++;
          if (rec.talkCopied) nums.talks++;
        }
      }
      Object.keys(st.quizHist).forEach(function (k) { nums.quizN++; if (st.quizHist[k].correct) nums.quizOk++; });
      var badges = (cfg.badges || []).map(function (b) {
        var have = st.wallet.badges[b.id], prog = 0;
        if (b.type === 'streak') prog = Math.max(st.streak.best || 0, R.streakInfo(st, day, clock.now, cal, cfg).current);
        else if (b.type === 'combo') prog = st.combo || 0;
        else if (b.type === 'counter') prog = (st.counters || {})[b.key] || 0;
        else if (b.type === 'pass') { var w = st.weeks[R.weekId(day)] || { pass: {} }; prog = Object.keys(w.pass || {}).length; }
        return { id: b.id, label: b.label, desc: b.desc, have: !!have, at: have || 0, progress: Math.min(prog, b.n), n: b.n };
      });
      var wid = R.weekId(day), wk = st.weeks[wid] || { xp: 0 };
      var thisWeek = R.weekDays(day), sum = function (k) { return thisWeek.reduce(function (a, d) { return a + ((st.days[d] && st.days[d].kinds[k]) || 0); }, 0); };
      var goals = [
        { title: '출석 도장', value: thisWeek.filter(function (d) { return st.days[d] && st.days[d].attend; }).length, target: thisWeek.filter(function (d) { return R.isBizDay(d, cal); }).length },
        { title: '퀴즈 풀기', value: Object.keys(st.quizHist).filter(function (k) { return R.weekId(st.quizHist[k].day) === wid; }).length, target: 5 },
        { title: '맞춤대화', value: sum('chat.custom'), target: 10 },
        { title: '화법 따라 쓰기', value: sum('talk.copy'), target: 3 }
      ];
      var shown = nums.days * 6, opened = nums.customers, chats = Object.keys(st.days).reduce(function (a, d) { return a + (st.days[d].kinds['chat.custom'] || 0); }, 0);
      return {
        from: from, to: day, cells: cells, months: months, nums: nums, badges: badges, goals: goals,
        streak: R.streakInfo(st, day, clock.now, cal, cfg), best: st.streak.best, xp: wk.xp,
        funnel: [['추천 노출', shown], ['고객 열람', opened], ['맞춤대화', chats], ['상품 제안', Math.round(chats * 0.38)], ['가입설계', Math.round(chats * 0.14)]],
        funnelNote: '상품 제안 · 가입설계는 영업포탈 연동 후 실제 값(지금은 예시 비율)',
        questions: [['이 고객 보장에서 비어 있는 곳만 알려줘', 14], ['표적항암 치료비 지급 조건을 쉽게 설명해 줘', 9], ['상령일 전에 점검할 항목을 정리해 줘', 7], ['간병인 보장 약관에서 입원 조건 찾아줘', 6], ['보상 청구 서류를 고객에게 안내하는 문자 만들어 줘', 5]],
        prompts: [['보장 공백 3줄 요약', 21], ['고객 맞춤 문자 만들기', 17], ['약관 조항 찾기', 12]]
      };
    }
    function orgView(scope) {
      var r = R.rng(scope === 'team' ? 31 : scope === 'branch' ? 37 : 41), rows = seed.branches.map(function (b, i) {
        var n = 34 + Math.floor(r() * 30), used = Math.round(n * (0.48 + r() * 0.42)), q = Math.round(used * (6 + r() * 14));
        return { name: b, members: n, used: used, rate: Math.round(used / n * 1000) / 10, delta: Math.round((r() * 16 - 4) * 10) / 10, perFp: Math.round(q / Math.max(used, 1) * 10) / 10,
          customers: Math.round(used * (2 + r() * 5)), attend: Math.round((0.42 + r() * 0.45) * 1000) / 10, quizJoin: Math.round((0.35 + r() * 0.5) * 1000) / 10,
          quizOk: Math.round((0.55 + r() * 0.3) * 1000) / 10, idle: n - used, mine: b === user.branch };
      });
      var members = seed.peers.concat([{ id: user.id, name: user.name }]).map(function (p, i) {
        var q = Math.floor(r() * 60), st2 = q > 25 ? '활성' : q > 6 ? '저조' : '미사용';
        return { name: R.maskName(p.name), last: q ? R.addDays(today(), -Math.floor(r() * (q > 6 ? 3 : 20))) : '', questions: q, customers: Math.floor(q / 3), streak: q > 6 ? Math.floor(r() * 14) : 0,
          main: ['맞춤대화', '일반대화', '추천 고객', '오늘의 퀴즈'][Math.floor(r() * 4)], status: st2 };
      });
      var tot = rows.reduce(function (a, x) { a.n += x.members; a.u += x.used; a.idle += x.idle; a.q += x.perFp * x.used; return a; }, { n: 0, u: 0, idle: 0, q: 0 });
      var quizzes = data.quiz.items.slice(0, 5).map(function (qq) { return { id: qq.id, date: qq.date, question: qq.question, rows: rows.map(function (x) { return Math.round((0.3 + r() * 0.6) * 100); }) }; });
      var sales = [['~50만', 0.8], ['50~100만', 1.4], ['100~200만', 2.3], ['200~400만', 3.1], ['400만~', 3.6]].map(function (s) { return { band: s[0], perFp: Math.round((s[1] * (4 + r() * 2)) * 10) / 10, fps: 20 + Math.floor(r() * 60) }; });
      return { scope: scope, hq: user.hq, kpi: { rate: Math.round(tot.u / tot.n * 1000) / 10, used: tot.u, total: tot.n, questions: Math.round(tot.q), perFp: Math.round(tot.q / tot.u * 10) / 10, idle: tot.idle },
        rows: rows, members: members, quizzes: quizzes, sales: sales,
        popular: [['상령일 임박 고객 점검 항목', 128], ['표적항암 치료비 지급 조건', 97], ['간병인 보장 비교', 84], ['사전조회동의 재요청 문자', 66], ['보상 청구 서류 안내', 51]], example: true };
    }
    function hqView() {
      var r = R.rng(53), rows = seed.hqs.map(function (h) {
        var n = h[2], used = Math.round(n * (0.5 + r() * 0.35));
        return { name: h[0], region: h[1], members: n, used: used, rate: Math.round(used / n * 1000) / 10, delta: Math.round((r() * 14 - 3) * 10) / 10,
          perFp: Math.round((5 + r() * 12) * 10) / 10, attend: Math.round((0.4 + r() * 0.45) * 1000) / 10, quizOk: Math.round((0.55 + r() * 0.3) * 1000) / 10,
          top: ELEMENTS[Math.floor(r() * 6)][0] };
      });
      var regions = {};
      rows.forEach(function (x) { var g = regions[x.region] = regions[x.region] || { name: x.region, n: 0, u: 0 }; g.n += x.members; g.u += x.used; });
      var trend = [], d = '2026-09-01', base = 52;
      for (; d <= today(); d = R.addDays(d, 1)) { if (!R.isBizDay(d, cal)) continue; base += (r() - 0.45) * 2.2; trend.push([d, Math.round(Math.max(35, Math.min(85, base)) * 10) / 10]); }
      var heat = []; for (var w = 1; w <= 5; w++) { var row = []; for (var h = 8; h <= 19; h++) row.push(Math.round(Math.max(0, Math.sin((h - 7) / 12 * Math.PI) * 80 + r() * 30 - (w === 5 && h > 16 ? 30 : 0)))); heat.push(row); }
      var events = [];
      ['출석 도장', '퀴즈 정답', '추천 고객 열기', '맞춤대화', '화법 따라 쓰기', '공지 읽기', '로또 세트 발급'].forEach(function (k, i) { events.push({ at: R.kst(clock.now - i * 47000).hm, kind: k, org: rows[i % rows.length].name, who: R.maskName(['김수진', '박도우', '정민재', '한예린', '오세훈', '윤가람', '서지호'][i]) }); });
      return { kpi: { perFp: 11.4, rate: 61.2, used: rows.reduce(function (a, x) { return a + x.used; }, 0), questions: 48210, attend: 58.6, idle: rows.reduce(function (a, x) { return a + x.members - x.used; }, 0) },
        rows: rows, regions: Object.keys(regions).map(function (k) { var g = regions[k]; return { name: g.name, rate: Math.round(g.u / g.n * 1000) / 10, n: g.n }; }),
        elements: ELEMENTS.map(function (e, i) { return { name: e[0], key: e[1], value: Math.round(9000 / (i + 1.6) + r() * 900) }; }),
        trend: trend, heat: heat, events: events, baseline: seed.baseline, example: true };
    }

    boot(opts.persona);

    // ── 공개 함수 (client.js 와 같은 모양) ───────────────────────
    var api = {
      kind: 'mock',
      getHome: function () { return reply(home()); },
      attend: function () { return act({ kind: 'attend' }); },
      event: function (kind, payload) {
        payload = payload || {};
        var ev = { kind: kind, customerId: payload.customerId, tags: payload.tags, ref: payload.ref };
        if (kind === 'reco.open' || kind === 'chat.custom') { var c = recoList.filter(function (x) { return x.id === payload.customerId; })[0]; if (c) ev.tags = c.tags; }
        if (kind === 'notice.read') { st.seen.notice = st.seen.notice || {}; st.seen.notice[payload.ref] = true; }
        return act(ev);
      },
      answerQuiz: function (id, choice) { return act({ kind: 'quiz.answer', quizId: id, choice: choice }); },
      // 행운 존
      spinRoulette: function () { return act({ kind: 'roulette.spin' }); },
      pullSlot: function () { return act({ kind: 'cslot.pull' }); },
      crmDone: function (ref, customerId) { return act({ kind: 'crm.done', ref: ref, customerId: customerId }); },
      revealScratch: function (id) { return act({ kind: 'scratch.reveal', ref: id }); },
      startChallenge: function () { return act({ kind: 'challenge.start' }); },
      answerChallenge: function (runId, idx, choice, ms) { return act({ kind: 'challenge.answer', ref: runId, idx: idx, choice: choice, ms: ms }); },
      drawTarot: function (pick) { return act({ kind: 'tarot.draw', choice: pick }); },
      explainQuiz: function (id) { return act({ kind: 'quiz.explained', quizId: id }); },
      listTalks: function (p) {
        p = p || {};
        var q = (p.q || '').trim(), list = talks.concat(mine).filter(function (t) {
          if (p.cat && t.cat !== p.cat) return false;
          if (p.sit && t.sit !== p.sit) return false;
          if (p.only === 'rec' && t.grade !== 'rec') return false;
          if (p.only === 'best' && t.src === 'FP 응답') return false;
          if (p.only === 'short' && !t.noise) return false;
          if (p.only === 'copied' && !st.talks.copied[t.id]) return false;
          if (p.only === 'saved' && !st.talks.saved[t.id]) return false;
          if (p.only === 'block' && t.review !== 'block') return false;
          if (p.only === 'mine' && !t.mine) return false;
          if (q && (t.head + t.body + (t.tags || []).join(' ') + t.org + t.author).indexOf(q) < 0) return false;
          return true;
        });
        if (p.sort === 'likes') list.sort(function (a, b) { return b.likes - a.likes; });
        else if (p.sort === 'used') list.sort(function (a, b) { return b.used - a.used; });
        else if (p.sort === 'short') list.sort(function (a, b) { return a.head.length - b.head.length; });
        else list = interleave(list.filter(function (t) { return t.grade === 'rec'; })).concat(interleave(list.filter(function (t) { return t.grade !== 'rec'; })));
        var cats = {}; Object.keys(data.talks.cats).forEach(function (k) { cats[k] = { name: data.talks.cats[k].name, all: data.talks.cats[k].all, banner: data.talks.cats[k].banner, sample: talks.filter(function (t) { return t.cat === k; }).length }; });
        var hot = talks.filter(bannerOk).sort(function (a, b) { return b.used - a.used; }).slice(0, 5).map(talkLite);
        var page = p.page || 0, size = p.size || 40;
        return reply({ items: list.slice(page * size, (page + 1) * size).map(talkFull), total: list.length, page: page, size: size, cats: cats, stats: data.talks.stats, hot: hot });
      },
      getTalk: function (id) { return reply(talkFull(talkById[id])); },
      copyTalk: function (id, typed) { return act({ kind: 'talk.copy', talkId: id, typed: typed }, { talk: talkById[id] && talkById[id].review !== 'block' ? talkById[id] : null }); },
      reactTalk: function (id, type, on) {
        var m = { like: 'liked', save: 'saved', used: 'used' }[type];
        if (m) { if (on) st.talks[m][id] = clock.now; else delete st.talks[m][id]; }
        return reply({ ok: true, talk: talkFull(talkById[id]), home: home() });
      },
      submitTalk: function (t) {
        var o = { id: 'my-' + (mine.length + 1), cat: t.cat || 'H', sit: t.sit || '오프닝', tags: [], grade: 'normal', review: 'pending', head: t.head, body: t.body || t.head, why: '', tip: '', author: user.name, org: user.branch, likes: 0, used: 0, mine: true };
        mine.push(o); talkById[o.id] = o;
        return reply({ ok: true, id: o.id, status: 'pending', message: '검수 대기로 올라갔어요. 채택되면 화법 마트에 들어가요.' });
      },
      markDrawSeen: function (round) { st.seen.draw = st.seen.draw || {}; st.seen.draw[round] = true; return reply({ ok: true, home: home() }); },
      markRecapSeen: function (week) { st.seen.recap = st.seen.recap || {}; st.seen.recap[week] = true; return reply({ ok: true, home: home() }); },
      getLeague: function (scope) {
        if (!scope || scope === 'branch') return reply(leagueView(clock.now));
        var r = R.rng(scope === 'hq' ? 11 : 13), v;
        if (scope === 'hq') v = seed.branches.map(function (b) { return { name: b, value: Math.round(120 + r() * 160), mine: b === user.branch }; });
        else v = seed.hqs.map(function (h) { return { name: h[0], value: Math.round((48 + r() * 30) * 10) / 10, mine: h[0] === user.hq, region: h[1] }; });
        v.sort(function (a, b) { return b.value - a.value; }); v.forEach(function (x, i) { x.rank = i + 1; });
        return reply({ scope: scope, unit: scope === 'hq' ? '인당 XP' : '활성 사용률 %', list: v, example: true });
      },
      cheer: function (peerId) { return act({ kind: 'cheer.send', to: peerId }); },
      getRecord: function () { R.evaluate(st, { kind: 'dash.open' }, ctx(clock.now)); return reply(recordView()); },
      openDash: function () { return act({ kind: 'dash.open' }); },
      getRecap: function (week) { var wid = week || R.weekId(today()), lr = R.leagueRank(st, wid, ctx(clock.now)); var rc = R.recap(st, wid, cal); rc.rank = lr.rank; rc.total = lr.total; rc.weekLabel = R.weekLabel(today()); rc.streak = R.streakInfo(st, today(), clock.now, cal, cfg).current; rc.lotto = lottoView(clock.now); return reply(rc); },
      getOrgDash: function (scope) { return reply(orgView(scope || 'hq')); },
      getHqDash: function () { return reply(hqView()); },
      saveSettings: function (s) { for (var k in s) st.settings[k] = s[k]; return reply({ ok: true, home: home() }); },
      dismissBuddy: function (id) { var d = today(); dismissed[d] = dismissed[d] || {}; dismissed[d][id] = true; return reply({ ok: true, home: home() }); },
      getNotices: function () { return reply(seed.notices.map(function (n) { var o = clone(n); o.unread = n.unread && !(st.seen.notice && st.seen.notice[n.id]); return o; })); },
      getReco: function () { return reply(recoList); },
      log: function (events) { logs.push.apply(logs, events); if (logs.length > 2000) logs.splice(0, logs.length - 2000); return reply({ ok: true, n: events.length }); },
      // ── 데모 전용 (실서버에는 없다) ──
      demo: {
        now: function () { return clock.now; },
        setTime: function (ymd, hm) { clock.now = R.toMs(ymd, hm); return reply(home()); },
        setReco: function (list) { recoList = list.map(function (c) { return { id: c.id, name: c.name, tags: c.tags || [] }; }); return reply(home()); },
        advance: function (min) { clock.now += min * 60000; return reply(home()); },
        persona: function (p) { boot(p); return reply(home()); },
        reset: function () { boot(st.persona); return reply(home()); },
        setIssueOn: function (k) { cfg.lotto.issueOn = k; opts.issueOn = k; return reply(home()); },
        setAltName: function (b) { cfg.labels.useAltLottoName = !!b; opts.altName = !!b; return reply(home()); },
        swapQuiz: function () { quizSwap = !quizSwap; return reply(home()); },
        forceRecap: function (b) { recapForce = b !== false; return reply(home()); },
        refillFun: function () { // 데모 : 오늘의 행운 존 기회를 다시 채우고 스크래치 1장을 준다
          var d = today(); st.fun.days[d] = null; delete st.fun.days[d]; R.funDay(st, d);
          st.fun.scratch.push({ id: 'sc-demo-' + (st.fun.scratch.length + 1), day: d, from: 'demo', prize: R.pickWeighted(R.rng(clock.now % 9973), cfg.fun.scratch.prizes), at: clock.now, revealed: 0 });
          return reply(home());
        },
        state: function () { return st; },
        logs: function () { return logs; },
        cfg: function () { return cfg; }
      }
    };
    return api;
  }

  return { createMockApi: createMockApi };
});
