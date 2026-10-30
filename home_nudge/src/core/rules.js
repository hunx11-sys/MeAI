/* MeAI 홈 넛지 v5 · 규칙 엔진 (기준 구현)
 *
 * 서버 · 모의 서버(src/api/mock.js) · 테스트(tests/rules.test.js)가 이 파일 하나를 같이 쓴다.
 * 화면(DOM)을 모르는 순수 계산만 둔다. 서버를 자바 · 파이썬 등으로 만들 때는 이 파일을 그대로 옮기고
 * tests/vectors.json 의 기대값과 같은 결과가 나오는지 확인한다.
 *
 * 약속
 *  - 날짜는 한국 시간 'YYYY-MM-DD' 문자열, 시각은 epoch ms(밀리초).
 *  - 보상 · 한도 · 경품 숫자는 코드에 두지 않는다. 전부 config/nudge.config.json 에서 온다.
 *  - 같은 행동이 두 번 와도 보상은 한 번(멱등). 한도를 넘으면 오류가 아니라 '보상 없음'으로 끝낸다.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NZRules = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var KST = 9 * 3600 * 1000, DAY = 86400000;

  // ───────────────────────────── 날짜 · 영업일 ─────────────────────────────
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function kst(ms) {
    var d = new Date(ms + KST);
    var y = d.getUTCFullYear(), m = d.getUTCMonth() + 1, dd = d.getUTCDate();
    return { y: y, m: m, d: dd, hh: d.getUTCHours(), mi: d.getUTCMinutes(), dow: d.getUTCDay(),
      ymd: y + '-' + pad(m) + '-' + pad(dd), hm: pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()) };
  }
  function toMs(ymd, hm) {
    var p = ymd.split('-'), t = (hm || '00:00').split(':');
    return Date.UTC(+p[0], +p[1] - 1, +p[2], +t[0], +t[1]) - KST;
  }
  function addDays(ymd, n) { return kst(toMs(ymd) + n * DAY).ymd; }
  function dow(ymd) { return new Date(toMs(ymd) + KST).getUTCDay(); }
  function diffDays(a, b) { return Math.round((toMs(b) - toMs(a)) / DAY); }
  function isBizDay(ymd, cal) {
    var w = dow(ymd);
    if (w === 0 || w === 6) return false;
    if (cal && cal.holidays && cal.holidays[ymd]) return false;
    if (cal && cal.personalOff && cal.personalOff[ymd]) return false; // 근태 연동 : 휴가 · 교육일은 쉬는 날로 본다
    return true;
  }
  function prevBizDay(ymd, cal) {
    var x = addDays(ymd, -1);
    for (var i = 0; i < 60 && !isBizDay(x, cal); i++) x = addDays(x, -1);
    return x;
  }
  function weekMonday(ymd) { var w = dow(ymd); return addDays(ymd, w === 0 ? -6 : 1 - w); }
  function weekDays(ymd) { var mon = weekMonday(ymd), a = []; for (var i = 0; i < 5; i++) a.push(addDays(mon, i)); return a; }
  function weekId(ymd) { // ISO 8601 주 번호 (월요일 시작)
    var mon = weekMonday(ymd), thu = addDays(mon, 3), y = +thu.slice(0, 4);
    var w1 = weekMonday(y + '-01-04');
    return y + '-W' + pad(Math.floor(diffDays(w1, mon) / 7) + 1);
  }
  function weekLabel(ymd) { // 그 주 목요일이 속한 달 기준 'n월 n주차'
    var thu = addDays(weekMonday(ymd), 3);
    return (+thu.slice(5, 7)) + '월 ' + Math.ceil(+thu.slice(8, 10) / 7) + '주차';
  }
  function monthId(ymd) { return ymd.slice(0, 7); }
  function hmGE(hm, ref) { return hm >= ref; }

  // ───────────────────────────── 난수 · SHA-256 ─────────────────────────────
  // 모의 서버 · 테스트용 결정적 난수(mulberry32). 실제 서버의 세트 발급은 암호학적 난수(CSPRNG)를 쓴다.
  function rng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function utf8(s) {
    var out = [];
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c < 0x80) out.push(c);
      else if (c < 0x800) out.push(0xC0 | (c >> 6), 0x80 | (c & 63));
      else if (c >= 0xD800 && c < 0xDC00 && i + 1 < s.length) {
        var c2 = s.charCodeAt(++i), cp = 0x10000 + ((c - 0xD800) << 10) + (c2 - 0xDC00);
        out.push(0xF0 | (cp >> 18), 0x80 | ((cp >> 12) & 63), 0x80 | ((cp >> 6) & 63), 0x80 | (cp & 63));
      } else out.push(0xE0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
    }
    return out;
  }
  var K256 = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
  function sha256(msg) { // 문자열 → 32바이트 배열
    var b = utf8(msg), l = b.length * 8;
    b.push(0x80);
    while (b.length % 64 !== 56) b.push(0);
    for (var s = 56; s >= 0; s -= 8) b.push(s >= 32 ? Math.floor(l / Math.pow(2, s)) & 255 : (l >>> s) & 255);
    var H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19], W = new Array(64);
    for (var o = 0; o < b.length; o += 64) {
      for (var t = 0; t < 16; t++) W[t] = (b[o + 4 * t] << 24) | (b[o + 4 * t + 1] << 16) | (b[o + 4 * t + 2] << 8) | b[o + 4 * t + 3];
      for (t = 16; t < 64; t++) {
        var x = W[t - 15], y = W[t - 2];
        var s0 = ((x >>> 7) | (x << 25)) ^ ((x >>> 18) | (x << 14)) ^ (x >>> 3);
        var s1 = ((y >>> 17) | (y << 15)) ^ ((y >>> 19) | (y << 13)) ^ (y >>> 10);
        W[t] = (W[t - 16] + s0 + W[t - 7] + s1) | 0;
      }
      var a = H[0], bb = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (t = 0; t < 64; t++) {
        var S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
        var ch = (e & f) ^ (~e & g), t1 = (h + S1 + ch + K256[t] + W[t]) | 0;
        var S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
        var mj = (a & bb) ^ (a & c) ^ (bb & c), t2 = (S0 + mj) | 0;
        h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = bb; bb = a; a = (t1 + t2) | 0;
      }
      H[0] = (H[0] + a) | 0; H[1] = (H[1] + bb) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
      H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
    }
    var out = [];
    for (var i = 0; i < 8; i++) out.push((H[i] >>> 24) & 255, (H[i] >>> 16) & 255, (H[i] >>> 8) & 255, H[i] & 255);
    return out;
  }
  function hex(bytes) { var s = ''; for (var i = 0; i < bytes.length; i++) s += (bytes[i] < 16 ? '0' : '') + bytes[i].toString(16); return s; }
  function sha256hex(msg) { return hex(sha256(msg)); }

  // ───────────────────────────── 로또(행운번호) ─────────────────────────────
  function pickSet(rand, pool, pick) { // 1~pool 에서 pick 개, 오름차순
    var a = [], i;
    for (i = 1; i <= pool; i++) a.push(i);
    for (i = 0; i < pick; i++) { var j = i + Math.floor(rand() * (pool - i)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a.slice(0, pick).sort(function (x, y) { return x - y; });
  }
  // 공정성 : 회차 시작 때 sha256(seed) 지문을 먼저 공개하고, 추첨 뒤 seed 를 공개한다.
  // 누구나 drawNumbers(seed, round) 를 다시 돌려 같은 번호가 나오는지 확인할 수 있다.
  function drawNumbers(seed, round, pool, pick) {
    var buf = [], ctr = 0, ptr = 0;
    function u32() {
      if (ptr + 4 > buf.length) { buf = sha256(seed + ':' + round + ':' + (ctr++)); ptr = 0; }
      var v = ((buf[ptr] << 24) >>> 0) + (buf[ptr + 1] << 16) + (buf[ptr + 2] << 8) + buf[ptr + 3];
      ptr += 4;
      return v;
    }
    var a = [], i;
    for (i = 1; i <= pool; i++) a.push(i);
    for (i = 0; i < pick; i++) {
      var r = pool - i, lim = Math.floor(4294967296 / r) * r, v;
      do { v = u32(); } while (v >= lim);            // 나머지 치우침 없이 고르게
      var j = i + (v % r), t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a.slice(0, pick).sort(function (x, y) { return x - y; });
  }
  function matchCount(set, draw) { var n = 0; for (var i = 0; i < set.length; i++) if (draw.indexOf(set[i]) >= 0) n++; return n; }
  function tierFor(match, cfg) {
    var best = null;
    (cfg.lotto.tiers || []).forEach(function (t) { if (match >= t.match && (!best || t.match > best.match)) best = t; });
    return best;
  }
  function comb(n, k) { if (k < 0 || k > n) return 0; var r = 1; for (var i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; }
  function probMatch(pool, pick, m) { return comb(pick, m) * comb(pool - pick, pick - m) / comb(pool, pick); }
  function probAtLeast(pool, pick, m) { var p = 0; for (var k = m; k <= pick; k++) p += probMatch(pool, pick, k); return p; }
  function probAnyOf(sets, p) { return 1 - Math.pow(1 - p, sets); }
  function lottoWindow(now, cfg) {
    var t = kst(now), mon = weekMonday(t.ymd), fri = addDays(mon, 4);
    var cutoff = toMs(fri, cfg.lotto.cutoff), drawAt = toMs(fri, cfg.lotto.drawAt);
    var phase = now < cutoff ? 'collect' : now < drawAt ? 'closed' : 'drawn';
    return { round: weekId(t.ymd), label: weekLabel(t.ymd), phase: phase, cutoffAt: cutoff, drawAt: drawAt,
      issueRound: now < cutoff ? weekId(t.ymd) : weekId(addDays(mon, 7)) };
  }

  // ───────────────────────────── 화법 따라 쓰기 채점 ─────────────────────────────
  // 띄어쓰기 · 문장부호는 틀려도 인정 → 글자 · 숫자만 남겨 앞에서부터 한 글자씩 비교한다.
  var SIG = /[0-9A-Za-zㄱ-ㆎ가-힣一-鿿]/;
  function sigChars(s) { var a = []; s = String(s).toLowerCase(); for (var i = 0; i < s.length; i++) if (SIG.test(s[i])) a.push(s[i]); return a; }
  function copyScore(target, typed) {
    var T = sigChars(target), Y = sigChars(typed || ''), ok = 0, wrong = 0;
    for (var i = 0; i < T.length && i < Y.length; i++) { if (T[i] === Y[i]) ok++; else wrong++; }
    var total = T.length;
    return { ok: ok, wrong: wrong, typed: Y.length, total: total, done: Y.length >= total && total > 0 && ok / total >= 0.95 };
  }

  // ───────────────────────────── 이름 가리기 ─────────────────────────────
  function maskName(n) {
    if (!n) return '';
    if (n.length <= 1) return n;
    if (n.length === 2) return n[0] + '○';
    return n[0] + new Array(n.length - 1).join('○') + n[n.length - 1];
  }

  // ───────────────────────────── 사용자 상태 ─────────────────────────────
  // 서버에서는 표(DB)로 나뉘어 있는 것을 한 객체로 묶은 모양. 표 정의는 docs/schema.sql.
  function emptyState(userId) {
    return { userId: userId, days: {}, weeks: {}, wallet: { shields: 0, shieldMonth: '', badges: {} },
      streak: { best: 0 }, ledger: [], quizHist: {}, combo: 0,
      talks: { liked: {}, saved: {}, used: {}, copied: {} }, cheers: {}, firsts: {}, seen: {}, settings: {}, counters: {},
      fun: emptyFun() };
  }
  function emptyFun() { return { days: {}, best: 0, scratch: [], feverUntil: 0, runs: {}, seenOx: {} }; }
  function dayRec(st, ymd) {
    return st.days[ymd] || (st.days[ymd] = { lit: false, attend: false, shield: false, kinds: {}, tags: {}, xp: 0, xpCount: {},
      reco: {}, lotto: 0, quizDone: false, talkCopied: false, quests: {}, mission: false, allclear: false });
  }
  function weekRec(st, wid) { return st.weeks[wid] || (st.weeks[wid] = { xp: 0, pass: {}, perfect: false, tickets: 0, sets: [] }); }

  // 매달 첫 평가 때 보호권을 채운다 (월 n장, 최대 보유 m장)
  function refillShields(st, ymd, cfg, out) {
    var mid = monthId(ymd);
    if (st.wallet.shieldMonth === mid) return;
    var before = st.wallet.shields;
    st.wallet.shields = Math.min(cfg.streak.shieldMax, before + cfg.streak.shieldsPerMonth);
    st.wallet.shieldMonth = mid;
    if (out && st.wallet.shields > before) out.grants.push({ type: 'shield', amount: st.wallet.shields - before, rule: 'shield.monthly', label: '이달의 보호권' });
  }

  // 지난 영업일 중 불이 꺼진 날을 보호권으로 메운다. 보호권이 모자라면 하나도 쓰지 않는다(어차피 끊기므로).
  function settleMissed(st, today, cal, cfg) {
    var missed = [], d = prevBizDay(today, cal), seenLit = false;
    for (var i = 0; i < 40; i++) {
      var r = st.days[d];
      if (r && (r.lit || r.shield)) { seenLit = true; break; }
      if (diffDays(d, today) > 40) break;
      missed.push(d);
      d = prevBizDay(d, cal);
    }
    if (!seenLit || !missed.length || missed.length > st.wallet.shields) return [];
    missed.forEach(function (m) { dayRec(st, m).shield = true; });
    st.wallet.shields -= missed.length;
    st.ledger.push({ ts: toMs(today, '00:00'), day: today, type: 'shield', amount: -missed.length, rule: 'shield.use', label: '보호권으로 연속 기록 지킴', ref: missed.join(',') });
    return missed;
  }

  // 그날 첫 계산 때 한 번 : 보호권 채우기 → 지난 빈 영업일 메우기 (서버는 새벽 배치로 돌려도 된다)
  function prepareDay(st, today, cal, cfg, out) {
    if (st.preparedDay === today) return [];
    refillShields(st, today, cfg, out);
    var used = settleMissed(st, today, cal, cfg);
    if (used.length && out) out.fx.push({ type: 'shield', days: used });
    st.preparedDay = today;
    return used;
  }

  function streakInfo(st, today, now, cal, cfg) {
    var todayRec = st.days[today], todayLit = !!(todayRec && todayRec.lit);
    var start = (isBizDay(today, cal) && todayLit) ? today : prevBizDay(today, cal), cur = 0, d = start;
    for (var i = 0; i < 400; i++) {
      var r = st.days[d];
      if (!r || !(r.lit || r.shield)) break;
      if (r.lit) cur++;
      d = prevBizDay(d, cal);
    }
    var ms = cfg.streak.milestones, next = null;
    for (var k = 0; k < ms.length; k++) if (ms[k] > cur) { next = ms[k]; break; }
    var last = [], x = isBizDay(today, cal) ? today : prevBizDay(today, cal);
    for (var j = 0; j < 10; j++) {
      var rr = st.days[x];
      last.unshift({ day: x, state: x === today && !todayLit ? 'today' : rr && rr.lit ? 'lit' : rr && rr.shield ? 'shield' : 'miss' });
      x = prevBizDay(x, cal);
    }
    var t = kst(now);
    return { current: cur, best: Math.max(st.streak.best || 0, cur), todayLit: todayLit, bizToday: isBizDay(today, cal),
      nextStreak: todayLit ? cur : cur + 1, nextMilestone: next,
      atRisk: isBizDay(today, cal) && !todayLit && hmGE(t.hm, cfg.streak.riskFrom), shields: st.wallet.shields, last10: last };
  }

  // ───────────────────────────── 행운 존 (v5.1) ─────────────────────────────
  // 룰렛 · 슬롯 · 스크래치 · OX 챌린지 · 타로 · 빙고 · 피버 타임. 결과는 모두 서버(이 엔진)가 정하고 화면은 보여 주기만 한다.
  // 확률은 설정(cfg.fun)의 가중치 그대로이고 화면에 공개한다. 운에 따른 응모권은 하루 한도(cfg.fun.ticketCapDaily)가 있다.
  function pickWeighted(rand, list) {
    var sum = 0, i;
    for (i = 0; i < list.length; i++) sum += list[i].weight;
    var x = rand() * sum;
    for (i = 0; i < list.length; i++) { x -= list[i].weight; if (x < 0) return i; }
    return list.length - 1;
  }
  function shuffle(rand, arr) { var a = arr.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rand() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function funOf(st) { return st.fun || (st.fun = emptyFun()); }
  function funDay(st, ymd) {
    var f = funOf(st);
    return f.days[ymd] || (f.days[ymd] = { spins: [], pulls: [], runs: 0, tarot: null, tickets: 0, contacted: {}, perfect: false });
  }
  // 오늘 남은 기회 : 기본 횟수 + 조건 보너스(일일 미션 · 올클리어 등을 하면 한 번 더)
  function funPlays(st, today, cfg) {
    var f = cfg.fun, r = dayRec(st, today), d = funDay(st, today), out = {};
    ['roulette', 'cslot', 'challenge', 'tarot'].forEach(function (g) {
      var total = f.plays[g] || 0;
      (f.playsBonus || []).forEach(function (b) { if (b.game === g && r[b.when]) total += b.n; });
      var used = g === 'roulette' ? d.spins.length : g === 'cslot' ? d.pulls.length : g === 'challenge' ? d.runs : (d.tarot ? 1 : 0);
      out[g] = { total: total, used: used, left: Math.max(0, total - used) };
    });
    return out;
  }
  // 피버 타임 : 영업일의 정한 시간대(모두) 또는 스크래치 · 룰렛으로 받은 나만의 피버. 두 개가 겹치면 큰 배수 하나만.
  function feverInfo(st, now, cfg, cal) {
    var fv = cfg.fever, t = kst(now), res = { on: false, mult: 1, until: 0, label: '', kind: '', next: null };
    if (!fv) return res;
    var f = funOf(st);
    if (f.feverUntil > now) res = { on: true, mult: fv.personalMult, until: f.feverUntil, label: '나만의 피버', kind: 'personal', next: null };
    if (isBizDay(t.ymd, cal)) (fv.daily || []).forEach(function (w) {
      var a = toMs(t.ymd, w.from), b = toMs(t.ymd, w.to);
      if (now >= a && now < b) { if (w.mult >= res.mult) res = { on: true, mult: w.mult, until: Math.max(b, res.until), label: w.label, kind: 'daily', next: null }; }
      else if (now < a && !res.next) res.next = { at: a, until: b, label: w.label, mult: w.mult };
    });
    return res;
  }
  // 영업 빙고 : 이번 주(ISO 주) 행동을 칸마다 세어 3×3 판을 채운다. 줄 = 가로 3 · 세로 3 · 대각선 2.
  var BINGO_LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];
  function bingoState(st, ymd, cfg) {
    var wid = weekId(ymd), sums = {};
    Object.keys(st.days).forEach(function (d) {
      if (weekId(d) !== wid) return;
      var r = st.days[d];
      Object.keys(r.kinds).forEach(function (k) { sums[k] = (sums[k] || 0) + r.kinds[k]; });
      if (r.quizDone) sums.quiz = (sums.quiz || 0) + 1;
    });
    var cells = cfg.bingo.cells.map(function (c) { var v = sums[c.kind] || 0; return { id: c.id, label: c.label, kind: c.kind, go: c.go || '', n: c.n, progress: Math.min(v, c.n), done: v >= c.n }; });
    var lines = [];
    BINGO_LINES.forEach(function (l, i) { if (l.every(function (x) { return cells[x] && cells[x].done; })) lines.push(i); });
    return { week: wid, cells: cells, lines: lines, count: lines.length, filled: cells.filter(function (c) { return c.done; }).length };
  }
  // 오늘의 타로 : 사람 · 날짜마다 정해진 세 장 중 하나를 고른다(다시 뽑아도 같음). 카드 번호 0~(n-1) = 메이저 아르카나.
  function tarotOfDay(userId, ymd, n) {
    var h = sha256hex('tarot|' + userId + '|' + ymd), rand = rng(parseInt(h.slice(0, 8), 16));
    var a = [], i; for (i = 0; i < n; i++) a.push(i);
    return shuffle(rand, a).slice(0, 3);
  }
  // OX 챌린지 문제 고르기 : 갈래를 번갈아, 최근에 푼 문제는 뒤로
  function pickChallenge(bank, rand, n, seen) {
    var by = {}, cats = [];
    shuffle(rand, bank).sort(function (a, b) { return (seen[a.id] || '') < (seen[b.id] || '') ? -1 : (seen[a.id] || '') > (seen[b.id] || '') ? 1 : 0; })
      .forEach(function (q) { if (!by[q.cat]) { by[q.cat] = []; cats.push(q.cat); } by[q.cat].push(q); });
    var out = [];
    for (var i = 0; out.length < n && i < bank.length; i++) cats.forEach(function (c) { if (out.length < n && by[c][i]) out.push(by[c][i].id); });
    return out;
  }
  function challengePoints(ok, ms, combo, cc) {
    if (!ok) return 0;
    var left = Math.max(0, Math.floor((cc.sec * 1000 - Math.max(0, ms || 0)) / 1000));
    return cc.base + left * cc.speed + (combo > 1 ? (combo - 1) * cc.combo : 0);
  }

  // ───────────────────────────── 퀘스트 ─────────────────────────────
  function questIds(today, cfg) { return (cfg.questSchedule[today] || cfg.questSchedule['default']).slice(0, 5); }
  function questProgress(id, r, cfg) {
    var q = cfg.quests[id], n = 0;
    if (!q) return { progress: 0, target: 1 };
    q.on.forEach(function (k) {
      if (k === 'quiz') n += r.quizDone ? 1 : 0;
      else n += q.tag ? (r.tags[k + ':' + q.tag] || 0) : (r.kinds[k] || 0);
    });
    return { progress: Math.min(n, q.target), target: q.target };
  }
  function questSummary(st, today, cfg) {
    var r = dayRec(st, today), items = questIds(today, cfg).map(function (id) {
      var q = cfg.quests[id], p = questProgress(id, r, cfg);
      return { id: id, title: q.title, ring: q.ring, note: q.note || '', go: q.go, progress: p.progress, target: p.target, done: p.progress >= p.target };
    });
    var rings = {};
    Object.keys(cfg.rings).forEach(function (k) { rings[k] = { label: cfg.rings[k].label, color: cfg.rings[k].color, done: 0, total: 0 }; });
    items.forEach(function (it) { var g = rings[it.ring]; if (g) { g.total++; if (it.done) g.done++; } });
    var done = items.filter(function (i) { return i.done; }).length;
    return { date: today, items: items, done: done, total: items.length, rings: rings,
      need: cfg.rewards.dailyMission.need, mission: r.mission, allclear: r.allclear };
  }

  // ───────────────────────────── 보상 평가 (핵심) ─────────────────────────────
  /* evaluate(st, ev, ctx) → { grants: [...], fx: [...], ok, reason }
   *   ev  : { kind, ref?, customerId?, tags?, choice?, quizId?, typed?, talkId?, to?, ts? }
   *   ctx : { cfg, cal, now, rand, quiz(오늘 문제, answer 포함), talk(오늘/대상 화법), recoToday(오늘 추천 고객 id 목록), user, league(peers) }
   * 서버는 이 함수를 한 트랜잭션 안에서 부르고, grants 를 원장(nz_ledger)에, 바뀐 상태를 각 표에 쓴다.
   * fx 는 화면 연출 목록(도장 · 슬롯 · 미션 달성 …). 서버는 그대로 응답에 실어 보낸다.
   */
  function evaluate(st, ev, ctx) {
    var cfg = ctx.cfg, cal = ctx.cal, now = ctx.now, t = kst(now), today = t.ymd, wid = weekId(today);
    var out = { ok: true, reason: '', grants: [], fx: [] };
    prepareDay(st, today, cal, cfg, out);
    var r = dayRec(st, today), w = weekRec(st, wid), kind = ev.kind;
    var beforeQuest = questSummary(st, today, cfg);
    var beforeStreak = streakInfo(st, today, now, cal, cfg);
    var beforeRank = ctx.league ? leagueRank(st, wid, ctx) : null;
    var beforeBingo = cfg.bingo ? bingoState(st, today, cfg) : null;

    function grant(type, amount, rule, label, ref) {
      if (!amount) return;
      var g = { ts: now, day: today, type: type, amount: amount, rule: rule, label: label, ref: ref || '' };
      st.ledger.push(g); out.grants.push(g);
      if (type === 'ticket') w.tickets += amount;
      if (type === 'shield') st.wallet.shields = Math.min(cfg.streak.shieldMax, st.wallet.shields + amount);
    }
    // 배지는 설정(cfg.badges)에 있는 것만 준다. type : streak(연속 n일) · combo(퀴즈 n연속 정답) · counter(누적 n회) · pass(주간 패스 n단계)
    function badgeCheck(type, value, key) {
      var got = null;
      (cfg.badges || []).forEach(function (b) {
        if (b.type !== type || (b.key && b.key !== key) || st.wallet.badges[b.id]) return;
        if (type === 'streak' || type === 'pass' ? value === b.n : value >= b.n) {
          st.wallet.badges[b.id] = now;
          grant('badge', 1, 'badge.' + b.id, b.label, b.id);
          got = b;
        }
      });
      return got;
    }
    function count(key) { st.counters = st.counters || {}; st.counters[key] = (st.counters[key] || 0) + 1; return st.counters[key]; }
    function addXp(k, amount) {
      if (!amount) return 0;
      var cap = cfg.xpDailyCount[k];
      r.xpCount[k] = (r.xpCount[k] || 0) + 1;
      if (cap && r.xpCount[k] > cap) return 0;
      if (cfg.fever && cfg.fever.kinds.indexOf(k) >= 0) amount = amount * feverInfo(st, now, cfg, cal).mult;   // 피버 타임 : 영업 행동 XP 배수
      r.xp += amount; w.xp += amount;
      return amount;
    }
    function fail(reason) { out.ok = false; out.reason = reason; return out; }
    // 운으로 받는 응모권(룰렛 · 슬롯 · 스크래치 · OX 만점)은 하루 한도까지만. 넘친 만큼은 XP 로 바꿔 준다.
    function funTicket(n, rule, label, ref) {
      var fd = funDay(st, today), cap = cfg.fun.ticketCapDaily, okN = Math.max(0, Math.min(n, cap - fd.tickets));
      if (okN) { fd.tickets += okN; grant('ticket', okN, rule, label, ref); }
      if (okN < n) { var xp = addXp('fun.capXp', cfg.fun.capXp * (n - okN)); out.fx.push({ type: 'capped', xp: xp, cap: cap }); }
      return okN;
    }
    function applyPrize(pz, rule, ref) {
      if (pz.type === 'xp') return { xp: addXp('fun.prize', pz.n) };
      if (pz.type === 'ticket') return { ticket: funTicket(pz.n, rule, pz.label, ref) };
      if (pz.type === 'shield') { grant('shield', pz.n, rule, pz.label, ref); return { shield: pz.n }; }
      if (pz.type === 'fever') {
        var f = funOf(st); f.feverUntil = Math.max(now, f.feverUntil || 0) + pz.min * 60000;
        out.fx.push({ type: 'fever', until: f.feverUntil, min: pz.min, mult: cfg.fever.personalMult });
        return { fever: f.feverUntil };
      }
      return {};
    }
    function issueScratch(from) {
      var sc = cfg.fun.scratch, f = funOf(st), id = 'sc-' + today.replace(/-/g, '') + '-' + (f.scratch.length + 1);
      f.scratch.push({ id: id, day: today, from: from, prize: pickWeighted(ctx.rand, sc.prizes), at: now, revealed: 0 });
      out.fx.push({ type: 'scratchNew', id: id, from: from });
    }


    // 1) 행동별 처리 ------------------------------------------------------
    if (kind === 'attend') {
      if (!isBizDay(today, cal)) return fail('not_bizday');
      if (r.attend) return fail('already');
      r.attend = true; r.kinds.attend = 1;
      grant('ticket', cfg.rewards.attend.ticket, 'attend', '출석 도장', today);
      out.fx.push({ type: 'stamp', day: today });
      // 이번 주 영업일을 모두 출석하면 보너스 (그 주 마지막 출석 때 한 번)
      var wd = weekDays(today).filter(function (d) { return isBizDay(d, cal); });
      var all = wd.every(function (d) { return st.days[d] && st.days[d].attend; });
      if (all && !w.perfect) { w.perfect = true; grant('ticket', cfg.rewards.perfectWeek.ticket, 'attend.perfect', '이번 주 개근 보너스', wid); out.fx.push({ type: 'perfect' }); }
      addXp('attend', cfg.xp.attend);
    } else if (kind === 'quiz.answer') {
      var qz = ctx.quiz;
      if (!qz || qz.id !== ev.quizId) return fail('no_quiz');
      if (st.quizHist[qz.id]) return fail('already');
      var correct = String(ev.choice) === String(qz.answer);
      st.quizHist[qz.id] = { choice: ev.choice, correct: correct, explained: false, ts: now, day: today };
      st.combo = correct ? (st.combo || 0) + 1 : 0;
      if (correct) { r.quizDone = true; grant('ticket', cfg.rewards.quizCorrect.ticket, 'quiz.correct', '퀴즈 정답', qz.id); }
      addXp('quiz.answer', cfg.xp['quiz.answer'] + (correct ? cfg.xp.quizCorrectBonus : 0));
      out.fx.push({ type: 'quiz', correct: correct, combo: st.combo });
      var cb = correct && badgeCheck('combo', st.combo);
      if (cb) out.fx.push({ type: 'badge', id: cb.id, label: cb.label, desc: cb.desc });
    } else if (kind === 'quiz.explained') {
      var h = ctx.quiz && st.quizHist[ctx.quiz.id];
      if (!h) return fail('not_answered');
      if (h.explained) return fail('already');
      h.explained = true; r.quizDone = true;      // 틀려도 해설을 읽으면 퀘스트 인정 (목적은 시험이 아니라 전달)
    } else if (kind === 'talk.copy') {
      var tk = ctx.talk;
      if (!tk || tk.id !== ev.talkId) return fail('no_talk');
      var sc = copyScore(tk.head, ev.typed || '');
      if (!sc.done) return fail('not_done');
      st.talks.copied[tk.id] = now;
      if (!r.talkCopied) { r.talkCopied = true; grant('ticket', cfg.rewards.talkCopy.ticket, 'talk.copy', '화법 따라 쓰기', tk.id); addXp('talk.copy', cfg.xp['talk.copy']); }
      r.kinds['talk.copy'] = (r.kinds['talk.copy'] || 0) + 1;
      out.fx.push({ type: 'talk', rewarded: out.grants.some(function (g) { return g.rule === 'talk.copy'; }) });
      var tb = badgeCheck('counter', count('talk.copy'), 'talk.copy');
      if (tb) out.fx.push({ type: 'badge', id: tb.id, label: tb.label, desc: tb.desc });
    } else if (kind === 'cheer.send') {
      var cd = st.cheers[today] || (st.cheers[today] = {});
      var sent = Object.keys(cd).length;
      if (cd[ev.to]) return fail('already');
      if (sent >= cfg.cheer.dailyMax) return fail('limit');
      cd[ev.to] = now;
      addXp('cheer.send', cfg.xp['cheer.send']);
      out.fx.push({ type: 'cheer', to: ev.to });
      var chb = badgeCheck('counter', count('cheer.send'), 'cheer.send');
      if (chb) out.fx.push({ type: 'badge', id: chb.id, label: chb.label, desc: chb.desc });
    } else if (kind === 'roulette.spin') {
      // CRM 룰렛 : 칸(고객 활동)을 가중치로 고르고, 그 활동이 어울리는 내 고객을 붙여 준다. 보너스 칸은 바로 보상.
      if (!isBizDay(today, cal)) return fail('not_bizday');
      if (!funPlays(st, today, cfg).roulette.left) return fail('no_plays');
      var rc0 = cfg.fun.roulette, si = pickWeighted(ctx.rand, rc0.segments), sg = rc0.segments[si], fdr = funDay(st, today);
      var free = (ctx.crm || []).filter(function (c) { return !fdr.contacted[c.id]; });
      var fit = sg.tag ? shuffle(ctx.rand, free.filter(function (c) { return (c.tags || []).indexOf(sg.tag) >= 0; })) : [];
      var spin = { id: 'r' + (fdr.spins.length + 1), seg: si, at: now, customers: [], fallback: false, done: {} };
      if (sg.tag) {
        spin.customers = fit.slice(0, rc0.pick).map(function (c) { return c.id; });
        if (!spin.customers.length) { spin.fallback = true; spin.customers = shuffle(ctx.rand, free).slice(0, rc0.pick).map(function (c) { return c.id; }); }
      }
      fdr.spins.push(spin);
      var bonus = sg.prize ? applyPrize(sg.prize, 'roulette.bonus', spin.id) : null;
      out.data = { spinId: spin.id, seg: si, segId: sg.id, customers: spin.customers, fallback: spin.fallback, bonus: bonus };
      out.fx.push({ type: 'roulette', seg: si, id: sg.id, label: sg.label, bonus: !!sg.prize });
    } else if (kind === 'cslot.pull') {
      // 추천 고객 슬롯 : 결과 단계(잭팟 · 짝 · 보통)를 가중치로 먼저 정하고, 그 단계에 맞게 고객 3명을 고른다.
      if (!isBizDay(today, cal)) return fail('not_bizday');
      if (!funPlays(st, today, cfg).cslot.left) return fail('no_plays');
      var cs = cfg.fun.cslot, fds = funDay(st, today);
      var avail = shuffle(ctx.rand, (ctx.crm || []).filter(function (c) { return !fds.contacted[c.id]; }));
      if (avail.length < 3) return fail('no_customers');
      var bySym = {}; avail.forEach(function (c) { (bySym[c.sym] = bySym[c.sym] || []).push(c); });
      var syms = Object.keys(bySym), ti = pickWeighted(ctx.rand, cs.tiers), tier = cs.tiers[ti].id, pickC = null;
      var big = syms.filter(function (k) { return bySym[k].length >= 3; }), two = syms.filter(function (k) { return bySym[k].length >= 2; });
      if (tier === 'jackpot' && !big.length) tier = 'pair';
      if (tier === 'pair' && (!two.length || syms.length < 2)) tier = 'mix';
      if (tier === 'mix' && syms.length < 3) tier = two.length && syms.length >= 2 ? 'pair' : 'jackpot';
      if (tier === 'jackpot') { var k0 = big[Math.floor(ctx.rand() * big.length)]; pickC = bySym[k0].slice(0, 3); }
      else if (tier === 'pair') { var k1 = two[Math.floor(ctx.rand() * two.length)], oth = avail.filter(function (c) { return c.sym !== k1; }); pickC = shuffle(ctx.rand, bySym[k1].slice(0, 2).concat([oth[0]])); }
      else { pickC = shuffle(ctx.rand, syms).slice(0, 3).map(function (k) { return bySym[k][0]; }); }
      var pull = { id: 's' + (fds.pulls.length + 1), tier: tier, at: now, reels: pickC.map(function (c) { return c.sym; }), customers: pickC.map(function (c) { return c.id; }), done: {}, cleared: 0 };
      fds.pulls.push(pull);
      var won = cs.prizes[tier] || {}, got = { xp: 0, ticket: 0 };
      if (won.xp) got.xp = addXp('cslot.bonus', won.xp);
      if (won.ticket) got.ticket = funTicket(won.ticket, 'cslot.' + tier, won.label, pull.id);
      out.data = { pullId: pull.id, tier: tier, reels: pull.reels, customers: pull.customers, prize: got };
      out.fx.push({ type: 'cslot', tier: tier, reels: pull.reels });
    } else if (kind === 'crm.done') {
      // 룰렛 · 슬롯이 골라 준 고객에게 연락했다고 표시 (화면 신고 → XP 만. 응모권은 주지 않는다)
      var fdc = funDay(st, today), m = String(ev.ref || '').split(':'), src = m[0] === 'r' ? fdc.spins : m[0] === 's' ? fdc.pulls : null;
      var it = src && src.filter(function (x) { return x.id === m[1]; })[0];
      if (!it || it.customers.indexOf(ev.customerId) < 0) return fail('no_target');
      if (it.done[ev.customerId] || fdc.contacted[ev.customerId]) return fail('already');
      it.done[ev.customerId] = now; fdc.contacted[ev.customerId] = now;
      r.kinds['crm.done'] = (r.kinds['crm.done'] || 0) + 1;
      var base = m[0] === 'r' ? (cfg.fun.roulette.segments[it.seg].xp || cfg.xp['crm.done']) : cfg.fun.cslot.xpContact;
      var gx = addXp('crm.done', base), fm = feverInfo(st, now, cfg, cal);
      out.data = { ref: ev.ref, customerId: ev.customerId, xp: gx, mult: fm.mult };
      out.fx.push({ type: 'crm', xp: gx, mult: fm.mult });
      var cb2 = badgeCheck('counter', count('crm.done'), 'crm.done');
      if (cb2) out.fx.push({ type: 'badge', id: cb2.id, label: cb2.label, desc: cb2.desc });
      if (m[0] === 's' && !it.cleared && it.customers.every(function (c) { return it.done[c]; })) {
        it.cleared = now;
        var cx = addXp('cslot.clear', cfg.fun.cslot.clearXp);
        out.fx.push({ type: 'cslotClear', xp: cx });
      }
    } else if (kind === 'scratch.reveal') {
      var fs0 = funOf(st), sc0 = fs0.scratch.filter(function (x) { return x.id === ev.ref; })[0];
      if (!sc0) return fail('no_scratch');
      if (sc0.revealed) return fail('already');
      if (diffDays(sc0.day, today) > cfg.fun.scratch.validDays) return fail('expired');   // 받은 날부터 n일 안에 긁는다
      sc0.revealed = now;
      var pz = cfg.fun.scratch.prizes[sc0.prize], res = applyPrize(pz, 'scratch', sc0.id);
      out.data = { id: sc0.id, prize: { id: pz.id, label: pz.label, type: pz.type }, result: res };
      out.fx.push({ type: 'scratch', id: sc0.id, label: pz.label, prize: pz.type });
    } else if (kind === 'challenge.start') {
      var cc0 = cfg.fun.challenge, bank = ctx.oxBank || [];
      if (!funPlays(st, today, cfg).challenge.left) return fail('no_plays');
      if (bank.length < cc0.n) return fail('no_bank');
      var fdq = funDay(st, today), fq = funOf(st), ids = pickChallenge(bank, ctx.rand, cc0.n, fq.seenOx), runId = 'c' + today.replace(/-/g, '') + '-' + (fdq.runs + 1);
      fdq.runs++;
      fq.runs[runId] = { ids: ids, ans: [], start: now, day: today, combo: 0, score: 0, ok: 0, done: 0 };
      var keys = Object.keys(fq.runs); if (keys.length > 20) delete fq.runs[keys[0]];     // 지난 판은 20개까지만 둔다
      var byId = {}; bank.forEach(function (q) { byId[q.id] = q; });
      out.data = { runId: runId, sec: cc0.sec, items: ids.map(function (id) { return { id: id, cat: byId[id].cat, q: byId[id].q }; }) };
    } else if (kind === 'challenge.answer') {
      var cc1 = cfg.fun.challenge, fr = funOf(st), run = fr.runs[ev.ref];
      if (!run || run.day !== today) return fail('no_run');
      if (run.done) return fail('already');
      var idx = run.ans.length;
      if (ev.idx != null && +ev.idx !== idx) return fail('order');
      var qq = (ctx.oxBank || []).filter(function (q) { return q.id === run.ids[idx]; })[0];
      if (!qq) return fail('no_bank');
      var okA = ev.choice === qq.a, ms = Math.max(0, Math.min(cc1.sec * 1000, +ev.ms || 0));
      run.combo = okA ? run.combo + 1 : 0;
      var pts = challengePoints(okA, ms, run.combo, cc1);
      run.score += pts; if (okA) run.ok++;
      run.ans.push({ choice: ev.choice == null ? null : ev.choice, ok: okA, ms: ms, pts: pts });
      fr.seenOx[qq.id] = today;
      var last = run.ans.length === run.ids.length;
      out.data = { idx: idx, correct: okA, a: qq.a, why: qq.why, src: qq.src, pts: pts, score: run.score, combo: run.combo, last: last };
      if (last) {
        run.done = now;
        var fdz = funDay(st, today), newBest = run.score > (fr.best || 0);
        if (newBest) fr.best = run.score;
        r.kinds['challenge.finish'] = (r.kinds['challenge.finish'] || 0) + 1;
        var cxp = addXp('challenge.finish', Math.round(run.score / cc1.xpDiv)), perfect = run.ok === run.ids.length, tk = 0;
        if (perfect && !fdz.perfect) {
          fdz.perfect = true; tk = funTicket(cc1.perfectTicket, 'challenge.perfect', 'OX 챌린지 만점', ev.ref);
          var pb2 = badgeCheck('counter', count('challenge.perfect'), 'challenge.perfect');
          if (pb2) out.fx.push({ type: 'badge', id: pb2.id, label: pb2.label, desc: pb2.desc });
        }
        out.data.summary = { score: run.score, ok: run.ok, n: run.ids.length, best: fr.best, newBest: newBest, xp: cxp, ticket: tk, perfect: perfect };
        out.fx.push({ type: 'challenge', score: run.score, ok: run.ok, n: run.ids.length, newBest: newBest, perfect: perfect });
      }
    } else if (kind === 'tarot.draw') {
      var fdt = funDay(st, today);
      if (fdt.tarot) return fail('already');
      var three = tarotOfDay(st.userId, today, cfg.fun.tarot.cards), pk = Math.max(0, Math.min(2, Math.floor(+ev.choice) || 0));
      fdt.tarot = { card: three[pk], pick: pk, three: three, at: now };
      r.kinds['tarot.draw'] = 1;
      addXp('tarot.draw', cfg.xp['tarot.draw']);
      out.data = { card: three[pk], pick: pk, three: three };
      out.fx.push({ type: 'tarot', card: three[pk] });
    } else if (['reco.open', 'chat.custom', 'chat.general', 'notice.read', 'consent.request', 'fortune.send', 'fortune.open', 'dash.open'].indexOf(kind) >= 0) {
      // 같은 고객을 하루에 여러 번 열면 한 번만 센다
      if (kind === 'reco.open' && ev.customerId) {
        if (r.reco[ev.customerId]) { out.reason = 'same_customer'; }
        else {
          r.reco[ev.customerId] = { ts: now, lotto: false };
          r.kinds[kind] = (r.kinds[kind] || 0) + 1;
          (ev.tags || []).forEach(function (tg) { r.tags[kind + ':' + tg] = (r.tags[kind + ':' + tg] || 0) + 1; });
          addXp(kind, cfg.xp[kind]);
          var rb = badgeCheck('counter', count('reco.open'), 'reco.open');
          if (rb) out.fx.push({ type: 'badge', id: rb.id, label: rb.label, desc: rb.desc });
        }
      } else {
        r.kinds[kind] = (r.kinds[kind] || 0) + 1;
        (ev.tags || []).forEach(function (tg) { r.tags[kind + ':' + tg] = (r.tags[kind + ':' + tg] || 0) + 1; });
        addXp(kind, cfg.xp[kind]);
      }
      // 로또 세트 발급 : 설정한 행동(기본 = 추천 고객 맞춤대화)에서만, 하루 n세트 · 같은 고객 하루 1회
      if (kind === cfg.lotto.issueOn && ev.customerId) {
        var inReco = !cfg.lotto.onlyTodayReco || (ctx.recoToday || []).indexOf(ev.customerId) >= 0;
        var rc = r.reco[ev.customerId] || (r.reco[ev.customerId] = { ts: now, lotto: false });
        if (inReco && !rc.lotto && r.lotto < cfg.lotto.dailyMax) {
          var lw = lottoWindow(now, cfg), wr = weekRec(st, lw.issueRound);
          var nums = pickSet(ctx.rand, cfg.lotto.pool, cfg.lotto.pick);
          rc.lotto = true; r.lotto++;
          wr.sets.push({ nums: nums, ts: now, customerId: ev.customerId, round: lw.issueRound });
          grant('lotto', 1, 'lotto.issue', labelLotto(cfg) + ' 1세트', ev.customerId);
          out.fx.push({ type: 'slot', nums: nums, nth: wr.sets.length, round: lw.issueRound, nextRound: lw.issueRound !== lw.round });
        } else if (inReco && !rc.lotto) out.reason = 'lotto_daily_max';
      }
    } else return fail('unknown_kind');

    // 2) 연속 기록 ---------------------------------------------------------
    if (cfg.streak.litBy.indexOf(kind) >= 0 && isBizDay(today, cal) && !r.lit) {
      r.lit = true;
      var s = streakInfo(st, today, now, cal, cfg);
      if (s.current > (st.streak.best || 0)) st.streak.best = s.current;
      out.fx.push({ type: 'flame', from: beforeStreak.current, to: s.current });
      if (cfg.streak.milestones.indexOf(s.current) >= 0) {
        var sb = badgeCheck('streak', s.current);
        out.fx.push({ type: 'streak', days: s.current, badge: sb ? sb.label : '' });
      }
    }

    // 3) 퀘스트 ------------------------------------------------------------
    var after = questSummary(st, today, cfg);
    after.items.forEach(function (it, i) {
      if (it.done && !beforeQuest.items[i].done && !r.quests[it.id]) {
        r.quests[it.id] = now;
        addXp('questClear', cfg.xp.questClear);
        out.fx.push({ type: 'quest', id: it.id, title: it.title, ring: it.ring, n: after.done, total: after.total });
      }
    });
    if (after.done >= cfg.rewards.dailyMission.need && !r.mission) {
      r.mission = true; grant('ticket', cfg.rewards.dailyMission.ticket, 'quest.mission', '일일 미션 달성', today);
      out.fx.push({ type: 'mission' });
      if (cfg.fun && cfg.fun.scratch.issueOn.indexOf('mission') >= 0) issueScratch('mission');
    }
    if (after.done >= cfg.rewards.allClear.need && after.done === after.total && !r.allclear) {
      r.allclear = true; grant('ticket', cfg.rewards.allClear.ticket, 'quest.allclear', '퀘스트 올클리어', today);
      out.fx.push({ type: 'allclear' });
      if (cfg.fun && cfg.fun.scratch.issueOn.indexOf('allclear') >= 0) issueScratch('allclear');
    }

    // 3-2) 영업 빙고 (이번 주) ---------------------------------------------
    if (beforeBingo) {
      var bg = bingoState(st, today, cfg), wbg = w.bingo || (w.bingo = {});
      var fresh = bg.lines.filter(function (l) { return beforeBingo.lines.indexOf(l) < 0; });
      if (fresh.length) out.fx.push({ type: 'bingo', lines: bg.lines, fresh: fresh, count: bg.count, filled: bg.filled });
      cfg.bingo.rewards.forEach(function (m, i) {
        if (bg.count >= m.lines && !wbg[i]) {
          wbg[i] = now;
          grant('ticket', m.ticket, 'bingo.' + i, m.label, wid);
          if (m.lines >= BINGO_LINES.length) { var bb = badgeCheck('counter', count('bingo.blackout'), 'bingo.blackout'); if (bb) out.fx.push({ type: 'badge', id: bb.id, label: bb.label, desc: bb.desc }); }
        }
      });
    }

    // 4) 주간 패스 ---------------------------------------------------------
    cfg.pass.forEach(function (m, i) {
      if (w.xp >= m.xp && !w.pass[i]) {
        w.pass[i] = now;
        if (m.reward.ticket) grant('ticket', m.reward.ticket, 'pass.' + i, '주간 패스 ' + (i + 1) + '단계', wid);
        if (m.reward.shield) grant('shield', m.reward.shield, 'pass.' + i, '주간 패스 ' + (i + 1) + '단계', wid);
        if (m.reward.frame) w.frame = m.reward.frame;   // 이번 주 리그 이름 테두리(골드 · MVP)
        var pb = badgeCheck('pass', i + 1);
        out.fx.push({ type: 'pass', step: i + 1, xp: m.xp, label: m.label, badge: pb ? pb.label : '' });
      }
    });

    // 5) 첫 경험 (신인만) ---------------------------------------------------
    var ob = cfg.onboarding, jm = ctx.user && ctx.user.joinMonth;
    var firstKind = kind === 'quiz.answer' || kind === 'quiz.explained' ? 'quiz' : kind;
    if (jm && jm <= ob.maxJoinMonth && !st.firsts[firstKind] && (firstKind !== 'quiz' || r.quizDone || kind === 'quiz.answer')) {
      var step = ob.steps.filter(function (x) { return x.kind === firstKind; })[0];
      if (step) { st.firsts[firstKind] = now; out.fx.push({ type: 'first', kind: firstKind, title: step.title, text: step.text }); }
    }

    // 6) 리그 순위 ---------------------------------------------------------
    if (beforeRank) {
      var ar = leagueRank(st, wid, ctx);
      if (ar.rank < beforeRank.rank) out.fx.push({ type: 'rankup', from: beforeRank.rank, to: ar.rank });
    }
    return out;
  }
  function labelLotto(cfg) { return cfg.labels.useAltLottoName ? cfg.labels.lottoAlt : cfg.labels.lotto; }

  // ───────────────────────────── 리그 · 비교 · 리캡 ─────────────────────────────
  // ctx.league = { me: {id,name}, peers: [{id, name, xp, at}] }  (같은 지점 · 이번 주)
  function leagueRank(st, wid, ctx) {
    var me = { id: st.userId, name: ctx.league.me.name, xp: (st.weeks[wid] || { xp: 0 }).xp, at: 0, me: true };
    var list = ctx.league.peers.map(function (p) { return { id: p.id, name: p.name, xp: p.xp, at: p.at || 0, me: false }; }).concat([me]);
    list.sort(function (a, b) { return b.xp - a.xp || a.at - b.at || (a.me === b.me ? 0 : a.me ? 1 : -1); }); // 같은 점수면 먼저 도달한 사람이 위(나는 동점이면 아래)
    var rank = 0;
    list.forEach(function (x, i) { x.rank = i + 1; if (x.me) rank = i + 1; });
    var above = rank > 1 ? list[rank - 2] : null;
    return { rank: rank, total: list.length, list: list, gap: above ? above.xp - me.xp + 1 : 0 };
  }
  // 위 사람을 따라잡는 데 필요한 행동을 XP 로 골라 준다 (안내 문구용)
  function catchUpHint(gap, cfg) {
    if (gap <= 0) return null;
    var acts = [['chat.custom', '맞춤대화 1회'], ['reco.open', '추천 고객 1명 열기'], ['talk.copy', '화법 따라 쓰기'], ['quiz.answer', '퀴즈 풀기'], ['attend', '출석 도장']];
    for (var i = acts.length - 1; i >= 0; i--) if ((cfg.xp[acts[i][0]] || 0) >= gap) return { kind: acts[i][0], label: acts[i][1], xp: cfg.xp[acts[i][0]] };
    return { kind: 'chat.custom', label: '맞춤대화 ' + Math.ceil(gap / cfg.xp['chat.custom']) + '회', xp: cfg.xp['chat.custom'] };
  }

  function recap(st, wid, cal, peersRankHist) {
    var w = st.weeks[wid] || { xp: 0, tickets: 0, sets: [] }, days = [], cust = {}, chats = 0, quizOk = 0, quizN = 0, talks = 0, lit = 0, best = null;
    Object.keys(st.days).forEach(function (d) {
      if (weekId(d) !== wid) return;
      var r = st.days[d]; days.push(d);
      if (r.lit) lit++;
      Object.keys(r.reco).forEach(function (c) { cust[c] = 1; });
      chats += r.kinds['chat.custom'] || 0;
      if (r.talkCopied) talks++;
      if (!best || r.xp > best.xp) best = { day: d, xp: r.xp };
    });
    Object.keys(st.quizHist).forEach(function (q) { var h = st.quizHist[q]; if (weekId(h.day) === wid) { quizN++; if (h.correct) quizOk++; } });
    var tips = [];
    if (quizN < 3) tips.push('퀴즈를 3번 이상 풀어 보세요. 신상품 이슈가 먼저 와요.');
    if (Object.keys(cust).length < 5) tips.push('추천 고객을 하루 1명씩만 열어도 주 5명이에요.');
    if (talks < 2) tips.push('화법 따라 쓰기를 두 번 해 보세요. 손으로 쓴 문장은 오래 남아요.');
    if (!tips.length) tips.push('이번 주처럼만 하면 다음 주 리그 상위권이에요.');
    return { week: wid, litDays: lit, customers: Object.keys(cust).length, chats: chats, quiz: { ok: quizOk, n: quizN }, talks: talks,
      tickets: w.tickets, sets: w.sets.length, xp: w.xp, bestDay: best, tips: tips.slice(0, 2) };
  }

  // 시간대 말풍선 : 설정 목록을 위에서부터 보고 처음 맞는 것 하나 (닫은 것은 그날 다시 안 띄움)
  function pickBuddy(list, facts, hm, dw, dismissed) {
    for (var i = 0; i < list.length; i++) {
      var b = list[i];
      if (dismissed && dismissed[b.id]) continue;
      if (b.dow && b.dow !== dw) continue;
      if (hm < b.from || hm > b.to) continue;
      if (!testWhen(b.when, facts)) continue;
      return b;
    }
    return null;
  }
  function testWhen(expr, f) { // '!attended' · 'attended&!quizDone' · 'questLeft==1' · 'true'
    if (!expr || expr === 'true') return true;
    return expr.split('&').every(function (p) {
      p = p.trim();
      var m = p.match(/^(\w+)==(\d+)$/);
      if (m) return Number(f[m[1]]) === Number(m[2]);
      if (p[0] === '!') return !f[p.slice(1)];
      return !!f[p];
    });
  }

  return {
    KST: KST, DAY: DAY, kst: kst, toMs: toMs, addDays: addDays, dow: dow, diffDays: diffDays,
    isBizDay: isBizDay, prevBizDay: prevBizDay, weekMonday: weekMonday, weekDays: weekDays, weekId: weekId, weekLabel: weekLabel,
    rng: rng, sha256hex: sha256hex, pickSet: pickSet, drawNumbers: drawNumbers, matchCount: matchCount, tierFor: tierFor,
    comb: comb, probMatch: probMatch, probAtLeast: probAtLeast, probAnyOf: probAnyOf, lottoWindow: lottoWindow, labelLotto: labelLotto,
    sigChars: sigChars, copyScore: copyScore, maskName: maskName,
    emptyState: emptyState, dayRec: dayRec, weekRec: weekRec, refillShields: refillShields, settleMissed: settleMissed, prepareDay: prepareDay,
    streakInfo: streakInfo, questIds: questIds, questSummary: questSummary, evaluate: evaluate,
    leagueRank: leagueRank, catchUpHint: catchUpHint, recap: recap, pickBuddy: pickBuddy, testWhen: testWhen,
    pickWeighted: pickWeighted, shuffle: shuffle, funDay: funDay, funPlays: funPlays, feverInfo: feverInfo, bingoState: bingoState, BINGO_LINES: BINGO_LINES,
    tarotOfDay: tarotOfDay, pickChallenge: pickChallenge, challengePoints: challengePoints
  };
});
