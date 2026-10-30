/* MeAI 홈 넛지 v5 · 행운 존 (v5.1)
 * 막대의 「행운 존」 칸 → 허브 카드(피버 · 게임 6종 · 영업 빙고) → 게임은 덮개(오버레이) 위에서 연출한다.
 *   CRM 룰렛 · 추천 고객 슬롯 · OX 스피드 챌린지 · 오늘의 타로 · 스크래치 복권 · 오늘의 운세(사주)
 * 결과(칸 · 릴 · 문제 · 카드 · 경품)는 전부 서버(규칙 엔진)가 정한다. 화면은 응답을 받은 뒤 멈출 자리만 맞춰 보여 준다.
 * 사주 · 타로 풀이는 오늘의 운세 엔진(window.NZ_SAJU · NZ_TAROT, fortune/src/engine.js 원본 그대로)을 읽기만 한다.
 * 내 생년월일은 이 기기(localStorage)에만 두고 서버로 보내지 않는다.
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ, I = NZ.I, esc = NZ.esc, F = NZ.fmt, C = NZ.cards;
  const SYM = { birthday: I.cake, age_up: I.clock, renew: I.refresh, gap: I.shield, consent: I.mail };
  const SYM_CLS = { birthday: 'r', age_up: 'g', renew: 'b', gap: 'e', consent: 'p' };
  const head = (icon, title, meta, cls) => '<div class="nz-ch"><span class="nz-ic' + (cls ? ' ' + cls : '') + '">' + icon + '</span><h3>' + title + '</h3>' + (meta ? '<span class="meta">' + meta + '</span>' : '') + '</div>';
  const fun = () => NZ.home && NZ.home.fun;
  const leftAll = (f) => f.plays.roulette.left + f.plays.cslot.left + f.plays.challenge.left + f.plays.tarot.left + f.scratch.cards.length;
  const tarot = () => G.NZ_TAROT || null;
  const SAJU = () => G.NZ_SAJU || null;
  const card = (id) => { const T = tarot(); return T && T.deck[id]; };
  const tarotImg = (id) => NZ.asset('tarot/' + (id < 10 ? '0' : '') + id + '.webp');
  const pctTxt = (p) => (Math.round(p * 10) / 10) + '%';
  const nameOf = (c) => c.name + ' 고객';
  NZ.fun = {};

  // ═════ 허브 카드 ═════
  function feverBar(f) {
    const v = f.fever;
    if (v.on) return '<div class="nz-fever on"><span class="fl">' + I.flame + '</span><div><b>피버 ×' + v.mult + ' · ' + esc(v.label) + '</b><small>추천 고객 · 맞춤대화 · 사전조회동의 · 고객 챙기기 XP ' + v.mult + '배</small></div><span class="t" data-fever-left="' + v.until + '">' + F.clock(v.until - NZ.home.serverTime) + '</span></div>';
    if (v.next) return '<div class="nz-fever"><span class="fl">' + I.flame + '</span><div><b>' + F.hm(v.next.at) + ' ' + esc(v.next.label) + ' ×' + v.next.mult + '</b><small>영업 행동 XP ×' + v.next.mult + ' · 나만의 피버는 스크래치 · 룰렛에서</small></div><span class="t sm">' + F.left(v.next.at - NZ.home.serverTime) + ' 뒤</span></div>';
    return '<div class="nz-fever off"><span class="fl">' + I.flame + '</span><div><b>오늘 피버 타임은 끝났어요</b><small>스크래치 · 룰렛에서 나만의 피버 30분이 나올 수 있어요</small></div></div>';
  }
  function tile(key, icon, cls, title, sub, left, btn, done) {
    return '<button type="button" class="nz-ftile ' + cls + (left ? ' has' : '') + (done ? ' done' : '') + '" data-act="fun-go" data-g="' + key + '">' +
      '<span class="ic">' + icon + '</span><span class="tt"><b>' + title + '</b><small>' + sub + '</small></span>' +
      '<span class="lf">' + (left ? '<em>' + left + '</em>' + btn : done || btn) + '</span></button>';
  }
  function bingoMini(b) {
    const cells = b.cells.map((c, i) => '<button type="button" class="c' + (c.done ? ' on' : '') + (i === 4 ? ' mid' : '') + '" data-act="fun-go" data-g="' + esc(c.go) + '" aria-label="' + esc(c.label + ' ' + c.progress + '/' + c.n + (c.done ? ' 완료' : '')) + '">' +
      '<span>' + esc(c.label) + '</span><small>' + (c.done ? I.check : c.progress + '/' + c.n) + '</small></button>').join('');
    const lines = b.lines.map((l) => '<i class="ln l' + l + '"></i>').join('');
    const rw = b.rewards.map((m) => '<span class="' + (m.got ? 'got' : '') + '">' + (m.lines >= 8 ? '9칸' : m.lines + '줄') + ' · 응모권 +' + m.ticket + (m.got ? ' ' + I.check : '') + '</span>').join('');
    return '<div class="nz-bingo"><div class="bd">' + cells + lines + '</div><div class="side"><div class="cnt"><b>' + b.count + '</b>줄</div><p>이번 주 영업 행동으로 칸이 저절로 채워져요. 줄을 만들면 커피 응모권.</p><div class="rw">' + rw + '</div></div></div>';
  }
  C.fun = {
    title: '행운 존',
    wide: true,
    render(h) {
      const f = h.fun, P = f.plays, ch = f.challenge, sc = f.scratch, tt = f.tarot.today;
      const lastSpin = f.roulette.spins[f.roulette.spins.length - 1], lastPull = f.cslot.pulls[f.cslot.pulls.length - 1];
      const spinSub = lastSpin ? (lastSpin.bonus ? '보너스 「' + esc(lastSpin.label) + '」' : esc(lastSpin.label) + ' · ' + lastSpin.customers.filter((c) => c.done).length + '/' + lastSpin.customers.length + '명 챙김') : '오늘 연락할 고객을 골라 줘요';
      const pullSub = lastPull ? ({ jackpot: '트리플!', pair: '더블', mix: '3명 뽑음' }[lastPull.tier]) + ' · ' + lastPull.customers.filter((c) => c.done).length + '/3명 챙김' : '3명 뽑기 · 트리플이면 응모권';
      const fo = fortuneToday();
      const tiles = [
        tile('roulette', I.wheel, 't-r', 'CRM 룰렛', spinSub, P.roulette.left, '<span class="go">돌리기</span>', lastSpin ? '<span class="go">결과 보기</span>' : ''),
        tile('cslot', I.slot, 't-s', '추천 고객 슬롯', pullSub, P.cslot.left, '<span class="go">당기기</span>', lastPull ? '<span class="go">결과 보기</span>' : ''),
        tile('challenge', I.ox, 't-o', 'OX 스피드 챌린지', ch.best ? '최고 ' + ch.best + '점 · 5문제 10초' : '약관 · 메디컬 · 제도 OX', P.challenge.left, '<span class="go">도전</span>', '<span class="go">내일 또</span>'),
        tile('tarot', I.cards, 't-t', '오늘의 타로', tt && card(tt.card) ? '「' + esc(card(tt.card).ko) + '」 · ' + esc(card(tt.card).up[0]) : '카드 한 장으로 오늘을 열어요', P.tarot.left, '<span class="go">뽑기</span>', '<span class="go">다시 보기</span>'),
        tile('scratch', I.scratch, 't-c', '스크래치 복권', sc.cards.length ? sc.cards.length + '장 있어요 · 꽝 없음' : sc.today.length ? '오늘 ' + esc(sc.today[sc.today.length - 1].label) : '일일 미션 · 올클리어 때 1장씩', sc.cards.length, '<span class="go">긁기</span>', '<span class="go">미션 하러</span>'),
        tile('fortune-card', I.moon, 't-f', '오늘의 운세', fo ? '★'.repeat(fo.f.stars) + ' ' + fo.f.total + '점 · 오늘의 대화 한마디' : '사주로 보는 나의 오늘 · 대화 팁', 0, '', '<span class="go">' + (fo ? '보기' : '열기') + '</span>')
      ].join('');
      const left = leftAll(f);
      return head(I.clover, '행운 존', '오늘 남은 기회 <b>' + left + '</b>', 'gold') +
        '<div class="nz-cb">' + feverBar(f) + '<div class="nz-ftiles">' + tiles + '</div>' +
        '<div class="nz-kicker">영업 빙고 · ' + esc(h.week.label) + '<span class="r">' + f.bingo.filled + ' / 9칸</span></div>' + bingoMini(f.bingo) +
        '<p class="nz-note">확률은 모두 공개해요(각 게임 화면). 운으로 받는 응모권은 하루 ' + f.cap + '장까지예요 · 오늘 ' + f.capLeft + '장 남음 <span class="nz-ex">예시값</span></p></div>' +
        '<div class="nz-cf split"><span class="nz-note">룰렛 · 슬롯은 오늘 연락할 고객을 골라 주는 도구예요</span><button type="button" class="nz-btn ghost" data-open="more">' + I.gear + '넛지 설정</button></div>';
    }
  };
  NZ.acts['fun-go'] = (t) => { const g = t.dataset.g; NZ.log('fun', 'open', { g: g }); NZ.fun.go(g); };

  // 하러 가기 대상 → 게임 · 기능
  NZ.fun.go = (g) => {
    const map = { roulette: roulette, cslot: cslot, challenge: challenge, tarot: tarotDraw, scratch: scratch, 'fortune-card': fortuneCard };
    if (map[g]) { NZ.ui.close(true); setTimeout(() => map[g](), 60); return true; }
    if (g === 'fun') { NZ.ui.go('fun'); return true; }
    if (g === 'bingo') { NZ.ui.go('fun'); return true; }
    NZ.ui.go(g);
    return true;
  };

  // ── 게임 덮개 공통 ─────────────────────────────────────────
  function stage(cls, label, inner) {
    const el = NZ.el('<div class="nz-game ' + cls + '"><button type="button" class="nz-gx" data-gclose aria-label="닫기">' + I.x + '</button>' + inner + '</div>');
    const ov = NZ.overlay(el, { label: label, skip: false, clickClose: false });
    el.addEventListener('click', (e) => { if (e.target.closest('[data-gclose]')) ov.close(); });
    requestAnimationFrame(() => el.classList.add('in'));
    return { el: el, ov: ov };
  }
  function floatTxt(anchor, text, cls) {
    const r = NZ.rect(anchor); if (!r) return;
    const e = NZ.el('<span class="nz-float ' + (cls || '') + '">' + text + '</span>');
    NZ.layer().appendChild(e);
    e.style.setProperty('--x', (r.left + r.width / 2) + 'px'); e.style.setProperty('--y', (r.top) + 'px');
    setTimeout(() => e.remove(), 1300);
  }
  NZ.fun.float = floatTxt;
  function copy(text, done) { const d = () => done && done(); if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(d, d); else d(); }
  // 고객 목록(룰렛 · 슬롯 결과) : 문구 복사 → MeAI로 다듬기 → 연락했어요
  function custList(list, ref, tpl) {
    return '<ul class="nz-clist">' + list.map((c) => '<li data-cid="' + esc(c.id) + '" class="' + (c.done ? 'done' : '') + '"><span class="sy ' + (SYM_CLS[c.sym] || '') + '">' + (SYM[c.sym] || I.users) + '</span>' +
      '<span class="nm"><b>' + esc(nameOf(c)) + '</b><small>' + c.age + '세 · ' + esc(c.note) + '</small></span>' +
      (tpl ? '<button type="button" class="nz-btn sm sec" data-gact="copy" data-cid="' + esc(c.id) + '">' + I.copy + '문구</button>' : '<button type="button" class="nz-btn sm sec" data-gact="chat" data-cid="' + esc(c.id) + '">' + I.send + '맞춤대화</button>') +
      (c.done ? '<span class="ok">' + I.check + '챙김</span>' : '<button type="button" class="nz-btn sm pri" data-gact="done" data-ref="' + esc(ref) + '" data-cid="' + esc(c.id) + '">연락했어요</button>') + '</li>').join('') + '</ul>';
  }
  function wireCust(box, getTpl) {
    box.addEventListener('click', async (e) => {
      const b = e.target.closest('[data-gact]'); if (!b) return;
      const cid = b.dataset.cid, li = b.closest('li'), nm = li ? li.querySelector('b').textContent : '';
      if (b.dataset.gact === 'copy') {
        const txt = (getTpl() || '').replace('{name}', nm.replace(' 고객', ''));
        copy(txt, () => { NZ.toast('문구를 복사했어요. 이름을 확인하고 카톡 · 문자로 보내 보세요', { icon: 'copy' }); NZ.log('fun', 'tpl_copy', { cid: cid }); });
        const p = box.querySelector('.nz-tplbox'); if (p) { NZ.html(p, '<p>' + esc(txt) + '</p><button type="button" class="nz-btn sm ghost" data-gact="refine">' + I.wand + 'MeAI로 다듬기</button>'); p.classList.add('on'); }
        return;
      }
      if (b.dataset.gact === 'refine') { const p = box.querySelector('.nz-tplbox p'); NZ.host && NZ.host.ask('이 안부 문자를 고객 상황에 맞게 부드럽게 다듬어 줘 : ' + (p ? p.textContent : ''), 'general'); return; }
      if (b.dataset.gact === 'chat') { NZ.log('fun', 'chat', { cid: cid }); NZ.toast('맞춤대화에서 ' + esc(nm) + '을 고르면 보장을 바로 볼 수 있어요', { icon: 'send' }); return; }
      if (b.dataset.gact === 'done') {
        b.disabled = true;
        const r = await NZ.ask(NZ.api.crmDone(b.dataset.ref, cid));
        if (!r) { b.disabled = false; return; }
        if (r.ok) {
          li.classList.add('done');
          b.replaceWith(NZ.el('<span class="ok">' + I.check + '챙김</span>'));
          floatTxt(li, '+' + r.data.xp + ' XP' + (r.data.mult > 1 ? ' ×' + r.data.mult : ''), r.data.mult > 1 ? 'hot' : '');
          NZ.sfx.ding();
        }
        NZ.settle(r);
      }
    });
  }

  // ═════ ① CRM 룰렛 ═════
  function wheelSvg(segs) {
    const n = segs.length, R = 150, c = 160, a = 360 / n;
    let s = '<svg class="wh" viewBox="0 0 320 320" aria-hidden="true"><circle cx="160" cy="160" r="158" fill="#17181c"/>';
    segs.forEach((g, i) => {
      const a0 = (i * a - 90) * Math.PI / 180, a1 = ((i + 1) * a - 90) * Math.PI / 180;
      const x0 = c + R * Math.cos(a0), y0 = c + R * Math.sin(a0), x1 = c + R * Math.cos(a1), y1 = c + R * Math.sin(a1);
      s += '<path d="M160 160L' + x0.toFixed(1) + ' ' + y0.toFixed(1) + 'A' + R + ' ' + R + ' 0 0 1 ' + x1.toFixed(1) + ' ' + y1.toFixed(1) + 'Z" fill="' + esc(g.color) + '" stroke="#17181c" stroke-width="2"/>';
      // 글자는 원을 따라 가로로 : 바늘(맨 위)에 멈춘 칸의 글자가 바로 서서 읽힌다
      const mid = i * a + a / 2;
      s += '<g transform="rotate(' + mid + ' 160 160)"><text x="160" y="50" text-anchor="middle" class="lb' + (g.bonus ? ' bo' : '') + '">' + esc(g.label) + '</text>' +
        '<text x="160" y="68" text-anchor="middle" class="pc">' + pctTxt(g.pct) + '</text></g>';
    });
    for (let i = 0; i < n * 2; i++) { const t = (i * a / 2 - 90) * Math.PI / 180; s += '<circle cx="' + (c + 154 * Math.cos(t)).toFixed(1) + '" cy="' + (c + 154 * Math.sin(t)).toFixed(1) + '" r="3" class="bulb' + (i % 2 ? ' b2' : '') + '"/>'; }
    return s + '<circle cx="160" cy="160" r="34" fill="#17181c"/><circle cx="160" cy="160" r="28" fill="#fff"/></svg>';
  }
  function roulette() {
    const f = fun(); if (!f) return;
    const segs = f.roulette.segments, P = f.plays.roulette, last = f.roulette.spins[f.roulette.spins.length - 1];
    const g = stage('nz-roul', 'CRM 룰렛',
      '<div class="gk">CRM ROULETTE</div><h3>오늘 누구에게 연락할까?</h3><p class="gs">룰렛이 고객 활동을 고르면, 그 활동이 어울리는 내 고객을 붙여 드려요</p>' +
      '<div class="wrap"><div class="ptr" aria-hidden="true"></div><div class="rot">' + wheelSvg(segs) + '</div><button type="button" class="hub" data-spin aria-label="룰렛 돌리기"' + (P.left ? '' : ' disabled') + '>' + (P.left ? 'SPIN' : '끝') + '</button></div>' +
      '<div class="gleft">' + (P.left ? '오늘 <b>' + P.left + '번</b> 남음' : '오늘 기회를 모두 썼어요 · 일일 미션을 하면 1번 더') + ' · 칸의 숫자는 확률이에요</div>' +
      '<div class="res" aria-live="polite"></div>');
    const el = g.el, rot = el.querySelector('.rot'), res = el.querySelector('.res');
    let spinning = false, curDeg = 0;
    if (last) showResult(last, false);
    wireCust(res, () => { const sp = fun().roulette.spins[fun().roulette.spins.length - 1]; return sp && sp.tpl; });
    el.querySelector('[data-spin]').addEventListener('click', spin);
    async function spin() {
      if (spinning || !fun().plays.roulette.left) return;
      spinning = true; el.classList.add('spinning'); NZ.html(res, '');
      NZ.log('fun', 'roulette_spin');
      const r = await NZ.ask(NZ.api.spinRoulette());
      if (!r || !r.ok) { spinning = false; el.classList.remove('spinning'); if (r) NZ.settle(r); return; }
      const n = segs.length, a = 360 / n, mid = r.data.seg * a + a / 2, jitter = (Math.random() - 0.5) * a * 0.6;
      const target = curDeg + 360 * 6 + ((360 - mid - jitter - (curDeg % 360)) + 360) % 360;
      const dur = NZ.reduced() || NZ.fxMode() === 'off' ? 10 : 4600;
      const an = rot.animate([{ transform: 'rotate(' + curDeg + 'deg)' }, { transform: 'rotate(' + target + 'deg)' }], { duration: dur, easing: 'cubic-bezier(.12,.62,.08,1)', fill: 'forwards' });
      let lastSeg = -1, raf = 0;
      const ptr = el.querySelector('.ptr');
      (function tick() {
        const m = getComputedStyle(rot).transform; let deg = curDeg;
        if (m && m !== 'none') { const v = m.split('(')[1].split(')')[0].split(','); deg = Math.atan2(+v[1], +v[0]) * 180 / Math.PI; }
        const seg = Math.floor((((360 - deg) % 360) + 360) % 360 / a);
        if (seg !== lastSeg) { lastSeg = seg; NZ.sfx.tick(); ptr.classList.remove('kick'); void ptr.offsetWidth; ptr.classList.add('kick'); }
        raf = requestAnimationFrame(tick);
      })();
      an.onfinish = () => {
        cancelAnimationFrame(raf); curDeg = target % 360;
        rot.getAnimations().forEach((x) => { try { x.commitStyles(); } catch (e) { /* 이전 브라우저 */ } x.cancel(); });
        spinning = false; el.classList.remove('spinning');
        const sg = segs[r.data.seg];
        NZ.sfx.win(); if (NZ.fxMode() !== 'off') NZ.confettiAt(el.querySelector('.wrap'), sg.bonus ? 120 : 50, sg.bonus ? 12 : 8);
        NZ.settle(r);
        const sp = fun().roulette.spins.filter((x) => x.id === r.data.spinId)[0];
        if (sp) showResult(sp, true);
        const hb = el.querySelector('[data-spin]'); const L = fun().plays.roulette.left;
        hb.disabled = !L; hb.textContent = L ? 'SPIN' : '끝';
        NZ.html(el.querySelector('.gleft'), L ? '오늘 <b>' + L + '번</b> 남음 · 칸의 숫자는 확률이에요' : '오늘 기회를 모두 썼어요 · 일일 미션을 하면 1번 더');
      };
    }
    function showResult(sp, fresh) {
      if (sp.bonus) {
        NZ.html(res, '<div class="rbig' + (fresh ? ' pop' : '') + '"><span class="k">BONUS</span><b>' + esc(sp.label) + '</b><p>' + (sp.segId === 'bonus_fever' ? '지금부터 30분 동안 영업 행동 XP가 2배예요' : '커피 응모권 1장을 바로 넣었어요') + '</p></div>');
        return;
      }
      NZ.html(res, '<div class="rhead' + (fresh ? ' pop' : '') + '"><span class="k">오늘의 활동</span><b>' + esc(sp.label) + '</b><span class="xp">고객 1명당 +' + sp.xp + ' XP</span></div>' +
        (sp.fallback ? '<p class="nz-note">이 활동이 딱 맞는 고객이 없어 요즘 연락이 뜸한 고객을 골랐어요</p>' : '') +
        custList(sp.customers, 'r:' + sp.id, true) + '<div class="nz-tplbox"></div><p class="nz-note">문구는 예시예요 · 보내기 전에 고객 이름과 내용을 꼭 확인해요 <span class="nz-ex">준법 검토 전</span></p>');
    }
  }

  // ═════ ② 추천 고객 슬롯 ═════
  function cslot() {
    const f = fun(); if (!f) return;
    const P = f.plays.cslot, cs = f.cslot, last = cs.pulls[cs.pulls.length - 1];
    const symLabel = {}; cs.symbols.forEach((s) => { symLabel[s.id] = s.label; });
    const reelHtml = (sym) => '<div class="nz-sreel"><div class="strip"><div class="sy ' + (SYM_CLS[sym] || '') + '">' + (SYM[sym] || '') + '<span>' + esc(symLabel[sym] || '') + '</span></div></div></div>';
    const odds = cs.odds.map((o) => '<span><b>' + esc(o.label) + '</b> ' + pctTxt(o.pct) + '</span>').join('');
    const g = stage('nz-cslot', '추천 고객 슬롯',
      '<div class="lamp">' + '<i></i>'.repeat(11) + '</div><div class="gk">CUSTOMER SLOT</div><h3>오늘의 고객 3명 뽑기</h3>' +
      '<div class="reels">' + (last ? last.reels : ['birthday', 'age_up', 'renew']).map(reelHtml).join('') + '</div>' +
      '<div class="lever"><button type="button" class="nz-btn pri" data-pull' + (P.left ? '' : ' disabled') + '>' + I.slot + (P.left ? '레버 당기기 · ' + P.left + '번 남음' : '오늘 기회를 모두 썼어요') + '</button></div>' +
      '<div class="odds">' + odds + '<span class="r">트리플 = 응모권 +1 · XP +' + cs.prizes.jackpot.xp + ' · 더블 = XP +' + cs.prizes.pair.xp + '</span></div>' +
      '<div class="res" aria-live="polite"></div>');
    const el = g.el, res = el.querySelector('.res');
    if (last) show(last, false);
    wireCust(res, () => null);
    el.querySelector('[data-pull]').addEventListener('click', async (e) => {
      const btn = e.currentTarget; if (btn.disabled) return;
      btn.disabled = true; el.classList.add('spin'); NZ.html(res, '');
      NZ.log('fun', 'cslot_pull');
      const r = await NZ.ask(NZ.api.pullSlot());
      if (!r || !r.ok) { el.classList.remove('spin'); btn.disabled = false; if (r) NZ.settle(r); return; }
      const syms = cs.symbols.map((s) => s.id), reels = el.querySelectorAll('.nz-sreel');
      let stopped = 0, tickT = setInterval(() => NZ.sfx.tick(), 80);
      r.data.reels.forEach((sym, i) => {
        const strip = reels[i].querySelector('.strip'), seq = [];
        for (let k = 0; k < 14 + i * 4; k++) seq.push(syms[Math.floor(Math.random() * syms.length)]);
        seq.push(sym);
        NZ.html(strip, seq.map((x) => '<div class="sy ' + (SYM_CLS[x] || '') + '">' + (SYM[x] || '') + '<span>' + esc(symLabel[x] || '') + '</span></div>').join(''));
        const h = reels[i].offsetHeight || 112, dist = (seq.length - 1) * h;
        if (NZ.reduced() || NZ.fxMode() === 'off') { strip.style.transform = 'translateY(' + (-dist) + 'px)'; if (++stopped === 3) done(); return; }
        const an = strip.animate([{ transform: 'translateY(0)' }, { transform: 'translateY(' + (-dist) + 'px)' }], { duration: 1100 + i * 520, easing: 'cubic-bezier(.15,.65,.2,1)', fill: 'forwards' });
        an.onfinish = () => { reels[i].classList.add('stop'); NZ.sfx.ding(); if (++stopped === 3) done(); };
      });
      function done() {
        clearInterval(tickT); el.classList.remove('spin');
        const tier = r.data.tier;
        if (tier === 'jackpot') { el.classList.add('jack'); NZ.sfx.win(); if (NZ.fxMode() !== 'off') { NZ.burst(); setTimeout(() => NZ.burst(), 500); } }
        else if (tier === 'pair') { NZ.sfx.clear(); if (NZ.fxMode() !== 'off') NZ.confettiAt(el.querySelector('.reels'), 60, 9); }
        NZ.settle(r);
        const pl = fun().cslot.pulls.filter((x) => x.id === r.data.pullId)[0];
        if (pl) show(pl, true);
        const L = fun().plays.cslot.left; btn.disabled = !L; NZ.html(btn, I.slot + (L ? '레버 당기기 · ' + L + '번 남음' : '오늘 기회를 모두 썼어요'));
      }
    });
    function show(pl, fresh) {
      const t = { jackpot: ['TRIPLE', '트리플! 같은 사유 고객 3명', '응모권 +1 · XP +' + cs.prizes.jackpot.xp], pair: ['DOUBLE', '더블! 같은 사유 고객 2명', 'XP +' + cs.prizes.pair.xp], mix: ['3명 뽑았어요', '오늘 챙길 고객 3명', '3명 모두 챙기면 XP +' + cs.clearXp] }[pl.tier];
      NZ.html(res, '<div class="rhead ' + pl.tier + (fresh ? ' pop' : '') + '"><span class="k">' + t[0] + '</span><b>' + t[1] + '</b><span class="xp">' + t[2] + '</span></div>' +
        custList(pl.customers, 's:' + pl.id, false) + '<p class="nz-note">한 명씩 연락할 때마다 +' + cs.xpContact + ' XP · 3명 모두면 +' + cs.clearXp + ' XP 더' + (pl.cleared ? ' · <b>클리어!</b>' : '') + '</p>');
    }
  }

  // ═════ ③ OX 스피드 챌린지 ═════
  const markO = '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="15" fill="none" stroke="currentColor" stroke-width="6"/></svg>';
  const markX = '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M12 12l24 24M36 12L12 36" stroke="currentColor" stroke-width="6" stroke-linecap="round"/></svg>';
  function challenge() {
    const f = fun(); if (!f) return;
    const ch = f.challenge, P = f.plays.challenge, cats = ch.cats || {};
    const g = stage('nz-oxc', 'OX 스피드 챌린지', '<div class="scr"></div>');
    const el = g.el, scr = el.querySelector('.scr');
    let run = null, idx = 0, t0 = 0, timer = null, bar = null, locked = false, combo = 0, score = 0;
    intro();
    function intro() {
      const L = fun().plays.challenge.left;
      const chips = Object.keys(cats).map((k) => '<span class="nz-chip" data-v="c:' + cats[k].color + '"><i class="dot"></i>' + esc(cats[k].label) + '</span>').join('');
      NZ.html(scr, '<div class="gk">OX SPEED CHALLENGE</div><h3>5문제 · 10초 · 콤보</h3><p class="gs">약관 원문 · 메디컬 · 보험 제도 · 준법 문제 은행 ' + ch.bank + '문항에서 골라요</p>' +
        '<div class="chips">' + chips + '</div>' +
        '<div class="rules"><div><b>+' + 20 + '</b><small>정답</small></div><div><b>+남은 초</b><small>빠를수록</small></div><div><b>+5 · 10 · 15</b><small>연속 정답</small></div><div><b>응모권 +1</b><small>5문제 만점(하루 1번)</small></div></div>' +
        '<div class="best">내 최고 기록 <b>' + (fun().challenge.best || 0) + '점</b> · 만점 ' + ch.max + '점</div>' +
        '<button type="button" class="nz-btn pri big" data-start' + (L ? ' data-autofocus' : ' disabled') + '>' + (L ? '시작하기 · 오늘 ' + L + '판 남음' : '오늘 3판을 모두 했어요') + '</button>');
      NZ.vars(scr);
      const b = scr.querySelector('[data-start]'); if (b) { b.addEventListener('click', start); setTimeout(() => { try { b.focus({ preventScroll: true }); } catch (e) { /* 무시 */ } }, 80); }
    }
    async function start() {
      const r = await NZ.ask(NZ.api.startChallenge());
      if (!r || !r.ok) { if (r) NZ.settle(r); return; }
      NZ.settle(r, { quiet: true });
      run = r.data; idx = 0; combo = 0; score = 0;
      NZ.log('fun', 'challenge_start', { run: run.runId });
      countdown(3);
    }
    function countdown(n) {
      NZ.html(scr, '<div class="cd">' + n + '</div>'); NZ.sfx.pop();
      if (n > 1) setTimeout(() => countdown(n - 1), 600); else setTimeout(ask, 600);
    }
    function ask() {
      const q = run.items[idx], ct = cats[q.cat] || { label: q.cat, color: '#61646b' };
      locked = false;
      NZ.html(scr, '<div class="top"><span class="nz-chip" data-v="c:' + ct.color + '"><i class="dot"></i>' + esc(ct.label) + '</span><span class="no">' + (idx + 1) + ' / ' + run.items.length + '</span><span class="sc"><b>' + score + '</b>점</span></div>' +
        '<div class="tbar"><i></i></div><p class="q">' + esc(q.q) + '</p>' +
        '<div class="ox"><button type="button" class="o" data-ans="O" aria-label="O, 맞다">' + markO + '<small>키보드 O · ←</small></button><button type="button" class="x" data-ans="X" aria-label="X, 아니다">' + markX + '<small>키보드 X · →</small></button></div>' +
        '<div class="combo' + (combo > 1 ? ' on' : '') + '">' + I.flame + '<b>' + combo + '</b> 콤보</div><div class="fb" aria-live="polite"></div>');
      NZ.vars(scr);
      NZ.say((idx + 1) + '번 문제. ' + q.q);
      bar = scr.querySelector('.tbar i');
      t0 = performance.now();
      if (bar.animate) { const a = bar.animate([{ transform: 'scaleX(1)' }, { transform: 'scaleX(0)' }], { duration: run.sec * 1000, easing: 'linear', fill: 'forwards' }); a.onfinish = () => answer(null); timer = a; }
      else timer = setTimeout(() => answer(null), run.sec * 1000);
      scr.querySelectorAll('[data-ans]').forEach((b) => b.addEventListener('click', () => answer(b.dataset.ans)));
    }
    function onKey(e) {
      if (!run || locked || !scr.querySelector('[data-ans]')) return;
      const k = e.key.toLowerCase();
      if (k === 'o' || k === 'arrowleft') { e.preventDefault(); answer('O'); }
      else if (k === 'x' || k === 'arrowright') { e.preventDefault(); answer('X'); }
    }
    document.addEventListener('keydown', onKey, true);
    g.ov.done.then(() => { document.removeEventListener('keydown', onKey, true); if (timer && timer.cancel) timer.cancel(); else clearTimeout(timer); });
    async function answer(choice) {
      if (locked) return; locked = true;
      const ms = Math.round(performance.now() - t0);
      if (timer && timer.pause) timer.pause(); else clearTimeout(timer);
      scr.querySelectorAll('[data-ans]').forEach((b) => { b.disabled = true; if (b.dataset.ans === choice) b.classList.add('mine'); });
      const r = await NZ.ask(NZ.api.answerChallenge(run.runId, idx, choice, ms));
      if (!r) return;
      if (!r.ok) { NZ.settle(r); return; }
      const d = r.data; score = d.score; combo = d.combo;
      scr.querySelector('[data-ans="' + d.a + '"]').classList.add('ans');
      scr.classList.remove('good', 'bad'); void scr.offsetWidth; scr.classList.add(d.correct ? 'good' : 'bad');
      NZ.html(scr.querySelector('.fb'), '<b>' + (choice == null ? '시간 초과 · ' : d.correct ? '정답 +' + d.pts + ' · ' : '아쉬워요 · ') + '답은 ' + d.a + '</b><p>' + esc(d.why) + '</p><small>출처 · ' + esc(d.src) + '</small>');
      NZ.html(scr.querySelector('.sc'), '<b>' + score + '</b>점');
      const cb = scr.querySelector('.combo'); NZ.html(cb, I.flame + '<b>' + combo + '</b> 콤보'); cb.classList.toggle('on', combo > 1);
      if (d.correct) { NZ.sfx.ding(); floatTxt(scr.querySelector('.sc'), '+' + d.pts, combo > 2 ? 'hot' : ''); if (combo >= 3 && NZ.fxMode() === 'full') NZ.confettiAt(cb, 24, 6); }
      else NZ.sfx.stamp();
      NZ.say((d.correct ? '정답. ' : '오답. ') + d.why);
      const next = NZ.el('<button type="button" class="nz-btn dark" data-next>' + (d.last ? '결과 보기' : '다음 문제') + I.chev + '</button>');
      scr.querySelector('.fb').appendChild(next);
      let moved = false; const go = () => { if (moved) return; moved = true; d.last ? finish(r) : (idx++, ask()); };
      next.addEventListener('click', go);
      try { next.focus({ preventScroll: true }); } catch (e) { /* 무시 */ }
      setTimeout(go, d.correct ? 1700 : 3200);
    }
    function finish(r) {
      const s = r.data.summary, stars = s.ok >= 5 ? 3 : s.ok >= 4 ? 2 : s.ok >= 3 ? 1 : 0;
      NZ.html(scr, '<div class="gk">RESULT</div><div class="stars">' + [0, 1, 2].map((i) => '<i class="' + (i < stars ? 'on' : '') + '">' + I.star + '</i>').join('') + '</div>' +
        '<div class="total"><b data-count="' + s.score + '">0</b><small>점</small></div>' + (s.newBest ? '<div class="newbest">최고 기록 경신!</div>' : '<div class="bestl">최고 ' + s.best + '점</div>') +
        '<div class="sum"><div><small>정답</small><b>' + s.ok + ' / ' + s.n + '</b></div><div><small>받은 XP</small><b>+' + s.xp + '</b></div><div><small>응모권</small><b>' + (s.ticket ? '+' + s.ticket : s.perfect ? '오늘 받음' : '만점이면 +1') + '</b></div></div>' +
        '<div class="acts"><button type="button" class="nz-btn sec" data-gclose>닫기</button><button type="button" class="nz-btn pri" data-again' + (fun().plays.challenge.left ? '' : ' disabled') + '>' + (fun().plays.challenge.left ? '한 판 더 · ' + fun().plays.challenge.left + '판 남음' : '오늘은 끝 · 내일 또') + '</button></div>');
      const num = scr.querySelector('[data-count]'), t = performance.now(), dur = 900;
      (function step() { const p = Math.min(1, (performance.now() - t) / dur); num.textContent = Math.round(s.score * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(step); })();
      if (s.perfect || s.newBest) { NZ.sfx.win(); if (NZ.fxMode() !== 'off') NZ.burst(); } else NZ.sfx.clear();
      NZ.settle(r);
      const ag = scr.querySelector('[data-again]'); if (ag) ag.addEventListener('click', () => { if (fun().plays.challenge.left) start(); });
      run = null;
    }
  }

  // ═════ ④ 오늘의 타로 한 장 ═════
  const TAROT_MSG = (c) => '고객님, 오늘의 카드는 「' + c.ko + '」래요. ' + c.up[0].replace(/·/g, ' · ') + '의 하루 되세요! 사주 · 타로로 보는 오늘의 운세도 재미로 한번 보세요.';
  function tarotDraw() {
    const T = tarot(), f = fun(); if (!f) return;
    if (!T) { NZ.toast('타로 풀이 엔진을 불러오지 못했어요'); return; }
    const today = f.tarot.today;
    const backs = [0, 1, 2].map((i) => '<button type="button" class="tc" data-pick="' + i + '" aria-label="' + (i + 1) + '번째 카드 고르기"><span class="in"><span class="bk"></span><span class="fr"></span></span></button>').join('');
    const g = stage('nz-tarot', '오늘의 타로',
      '<div class="gk">TODAY\'S TAROT</div><h3>' + (today ? '오늘의 카드' : '마음 가는 카드 한 장을 고르세요') + '</h3><p class="gs">1909년 라이더-웨이트-스미스 원판 · 메이저 아르카나 22장 중 하루 한 장</p>' +
      '<div class="fan">' + backs + '</div><div class="res" aria-live="polite"></div>');
    const el = g.el, res = el.querySelector('.res');
    if (today) { reveal(today.pick, today.card, false); return; }
    el.querySelectorAll('[data-pick]').forEach((b) => b.addEventListener('click', async () => {
      if (el.classList.contains('picked')) return;
      el.classList.add('picked');
      const r = await NZ.ask(NZ.api.drawTarot(+b.dataset.pick));
      if (!r || !r.ok) { el.classList.remove('picked'); if (r) NZ.settle(r); return; }
      reveal(r.data.pick, r.data.card, true, r.data.three);
      setTimeout(() => NZ.settle(r), 900);
    }));
    function reveal(pick, id, fresh, three) {
      const c = card(id);
      el.classList.add('picked');
      el.querySelectorAll('.tc').forEach((b, i) => {
        const fr = b.querySelector('.fr');
        if (i === pick) { NZ.html(fr, '<img src="' + esc(tarotImg(id)) + '" alt="' + esc(c.ko + ' (' + c.en + ')') + '">'); b.classList.add('me'); setTimeout(() => b.classList.add('flip'), fresh ? 120 : 0); }
        else b.classList.add('dim');
        b.disabled = true;
      });
      NZ.html(el.querySelector('h3'), '오늘의 카드 · ' + esc(T.ROMAN[c.no]) + ' ' + esc(c.ko));
      setTimeout(() => {
        NZ.html(res, '<div class="tres' + (fresh ? ' pop' : '') + '"><div class="kw">' + esc(c.sym) + ' ' + esc(c.up[0]) + '</div><p>' + esc(c.up[1]) + '</p></div>' +
          '<div class="nz-kicker">고객에게 보낼 한마디</div><div class="nz-tpl">' + esc(TAROT_MSG(c)) + '</div>' +
          '<div class="acts"><button type="button" class="nz-btn sec" data-gact="send">' + I.copy + '안부 문구 복사</button><button type="button" class="nz-btn dark" data-gact="full">' + I.moon + '전체 운세 · 타로 4장 보기</button></div>' +
          '<p class="nz-note">재미로 보는 풀이예요 · 오늘의 운세 화면과 같은 풀이를 써요</p>');
        res.querySelector('[data-gact="send"]').addEventListener('click', () => sendFortune(TAROT_MSG(c)));
        res.querySelector('[data-gact="full"]').addEventListener('click', () => { g.ov.close(); NZ.ui.go('fortune'); });
        if (fresh) { NZ.sfx.win(); if (NZ.fxMode() !== 'off') NZ.confettiAt(el.querySelector('.tc.me'), 50, 8); }
      }, fresh ? 900 : 0);
    }
  }
  function sendFortune(msg) {
    copy(msg, () => { NZ.toast('안부 문구를 복사했어요. 카톡 · 문자에 붙여 넣어 보내 보세요', { icon: 'copy' }); NZ.log('fortune', 'copy'); NZ.run(NZ.api.event('fortune.send', {}), { quiet: true }); });
  }
  NZ.fun.sendFortune = sendFortune;

  // ═════ ⑤ 스크래치 복권 ═════
  function scratch() {
    const f = fun(); if (!f) return;
    const sc = f.scratch, cardx = sc.cards[0];
    const odds = sc.odds.map((o) => '<span>' + esc(o.label) + ' <b>' + pctTxt(o.pct) + '</b></span>').join('');
    const g = stage('nz-scr', '스크래치 복권',
      '<div class="gk">LUCKY SCRATCH</div><h3>' + (cardx ? '은박을 긁어 보세요' : '지금 가진 복권이 없어요') + '</h3><p class="gs">' + (cardx ? '손가락 · 마우스로 문지르면 벗겨져요 · 꽝 없음' : '일일 미션(루틴 3개)과 올클리어 때 1장씩 생겨요 · 받은 날부터 7일 안에 긁어요') + '</p>' +
      '<div class="tk' + (cardx ? '' : ' empty') + '"><div class="pz"><span class="q">?</span></div>' + (cardx ? '<canvas width="560" height="260" aria-label="스크래치 복권 은박"></canvas>' : '') + '</div>' +
      '<div class="acts">' + (cardx ? '<button type="button" class="nz-btn sec" data-all>한 번에 벗기기</button>' : '<button type="button" class="nz-btn pri" data-goq>오늘의 루틴 보기</button>') + '</div>' +
      '<div class="odds">' + odds + '</div>' + (sc.cards.length > 1 ? '<p class="nz-note">남은 복권 ' + (sc.cards.length - 1) + '장 더</p>' : ''));
    const el = g.el;
    if (!cardx) { el.querySelector('[data-goq]').addEventListener('click', () => { g.ov.close(); NZ.ui.go('quest'); }); return; }
    const cv = el.querySelector('canvas'), ctx = cv.getContext('2d'), pz = el.querySelector('.pz');
    // 은박 그리기
    const gr = ctx.createLinearGradient(0, 0, 560, 260); gr.addColorStop(0, '#b9bec7'); gr.addColorStop(0.5, '#e8ebef'); gr.addColorStop(1, '#a9afb9');
    ctx.fillStyle = gr; ctx.fillRect(0, 0, 560, 260);
    ctx.fillStyle = 'rgba(255,255,255,.55)'; ctx.font = '700 30px Pretendard, "Malgun Gothic", sans-serif'; ctx.textAlign = 'center';
    for (let y = 40; y < 260; y += 56) for (let x = 40 + (y % 112 ? 60 : 0); x < 560; x += 120) ctx.fillText('MeAI', x, y);
    ctx.fillStyle = '#5b6069'; ctx.font = '800 34px Pretendard, "Malgun Gothic", sans-serif'; ctx.fillText('여기를 긁어 보세요', 280, 142);
    let asked = false, done = false, down = false, result = null, lastP = null;
    async function askPrize() {
      if (asked) return; asked = true;
      const r = await NZ.ask(NZ.api.revealScratch(cardx.id));
      if (!r) { asked = false; return; }
      result = r;
      if (!r.ok) { NZ.settle(r); g.ov.close(); return; }
      const p = r.data.prize;
      NZ.html(pz, '<span class="ic">' + ({ xp: I.star, ticket: I.ticket, shield: I.shield, fever: I.flame }[p.type] || I.gift) + '</span><b>' + esc(p.label) + '</b><small>' + ({ xp: '이번 주 리그 · 패스에 바로 더해요', ticket: '금요일 커피 추첨에 응모돼요', shield: '빈 영업일을 지켜 주는 보호권', fever: '지금부터 30분 영업 행동 XP 2배' }[p.type] || '') + '</small>');
      pz.classList.add('t-' + p.type);
      if (done) finish();
    }
    function pos(e) { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * 560 / r.width, (e.clientY - r.top) * 260 / r.height]; }
    function scrape(e) {
      const [x, y] = pos(e);
      ctx.globalCompositeOperation = 'destination-out'; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 46;
      ctx.beginPath(); if (lastP) ctx.moveTo(lastP[0], lastP[1]); else ctx.moveTo(x - 0.1, y); ctx.lineTo(x, y); ctx.stroke();
      lastP = [x, y];
      if (Math.random() < 0.3) NZ.sfx.tick();
    }
    function cleared() {
      const d = ctx.getImageData(0, 0, 560, 260).data; let n = 0, t = 0;
      for (let i = 3; i < d.length; i += 4 * 32) { t++; if (d[i] < 20) n++; }
      return n / t;
    }
    cv.addEventListener('pointerdown', (e) => { down = true; lastP = null; cv.setPointerCapture && cv.setPointerCapture(e.pointerId); askPrize(); scrape(e); });
    cv.addEventListener('pointermove', (e) => { if (down) scrape(e); });
    const up = () => { if (!down) return; down = false; lastP = null; if (!done && cleared() > 0.5) { done = true; if (result) finish(); } };
    cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
    el.querySelector('[data-all]').addEventListener('click', () => { done = true; askPrize(); if (result) finish(); });
    function finish() {
      if (!result || !result.ok || cv.classList.contains('gone')) return;
      cv.classList.add('gone'); pz.classList.add('win');
      NZ.sfx.win(); if (NZ.fxMode() !== 'off') NZ.confettiAt(pz, 90, 10);
      const a = el.querySelector('.acts'); NZ.html(a, '<button type="button" class="nz-btn sec" data-gclose>닫기</button>' + (fun().scratch.cards.length > 1 ? '<button type="button" class="nz-btn pri" data-more>다음 복권 긁기</button>' : ''));
      NZ.settle(result);
      const m = a.querySelector('[data-more]'); if (m) m.addEventListener('click', () => { g.ov.close(); setTimeout(scratch, 320); });
    }
  }

  // ═════ ⑥ 오늘의 운세 (사주) ═════
  function birthOf() {
    const v = NZ.local.get('birth'), gd = NZ.local.get('gender');
    if (v && /^\d{4}-\d{2}-\d{2}$/.test(v)) return { v: v, g: gd === 'M' ? 'M' : 'F', example: false };
    const ex = fun() && fun().fortune.example;
    return ex ? { v: ex.birth, g: ex.gender, example: true } : null;
  }
  function fortuneToday() {
    const S = SAJU(), b = birthOf(); if (!S || !b || !NZ.home) return null;
    const p = b.v.split('-').map(Number), t = NZ.home.today.split('-').map(Number);
    try { return { b: b, f: S.fortune(p[0], p[1], p[2], b.g === 'M', t[0], t[1], t[2]), p: S.pillars(p[0], p[1], p[2]) }; } catch (e) { return null; }
  }
  NZ.fun.fortuneToday = fortuneToday;
  function fortuneCard() {
    const S = SAJU();
    const g = stage('nz-fort2', '오늘의 운세', '<div class="body"></div>');
    const el = g.el, body = el.querySelector('.body');
    draw();
    function draw() {
      const fo = fortuneToday();
      if (!S || !fo) { NZ.html(body, '<p>운세 엔진을 불러오지 못했어요.</p>'); return; }
      const f = fo.f, b = fo.b, meters = [['재물', 0], ['대화', 1], ['일', 2], ['컨디션', 3]].map((k) => '<div class="m"><span>' + k[0] + '</span><span class="tr"><i data-v="p:' + (f.scores[k[1]] / 100).toFixed(2) + '"></i></span><b>' + f.scores[k[1]] + '</b></div>').join('');
      const len = 2 * Math.PI * 44;
      NZ.html(body, '<div class="gk">오늘의 운세 · ' + F.md(NZ.home.today) + '</div>' +
        '<div class="top"><div class="ring"><svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="44" class="bg"/><circle cx="50" cy="50" r="44" class="fg" stroke-dasharray="' + len.toFixed(1) + '" stroke-dashoffset="' + (len * (1 - f.total / 100)).toFixed(1) + '"/></svg><div><b>' + f.total + '</b><small>' + '★'.repeat(f.stars) + '</small></div></div>' +
        '<div class="hd"><small>' + esc(S.ANIMAL[fo.p.yb]) + '띠 · ' + esc(S.gz(fo.p.di)) + '일주 · ' + (b.g === 'M' ? '남' : '여') + (b.example ? ' · <em>예시 생년월일</em>' : '') + '</small><h3>' + esc(f.head) + '</h3><p>' + esc(f.dayLine) + '</p></div></div>' +
        '<div class="meters">' + meters + '</div>' +
        '<div class="lucky"><div><small>행운 색</small><b><i class="sw" data-v="c:' + f.colorHex + '"></i>' + esc(f.color) + '</b></div><div><small>행운 숫자</small><b>' + esc(f.number) + '</b></div><div><small>좋은 방향</small><b>' + esc(f.direction) + '</b></div><div><small>키워드</small><b>' + f.keys.map(esc).join(' · ') + '</b></div></div>' +
        '<div class="tip"><span class="k">' + I.quote + '오늘의 대화 한마디</span><b>「' + esc(f.tip) + '」</b><small>오늘 만나는 고객에게 이렇게 먼저 물어보세요</small></div>' +
        '<details class="me"><summary>내 생년월일 ' + (b.example ? '넣기' : '바꾸기') + '</summary><div class="frm"><label>생년월일 (양력)<input type="date" value="' + esc(b.v) + '" min="1930-01-01" max="2010-12-31" data-bd></label>' +
        '<div class="nz-seg" role="group" aria-label="성별"><button type="button" data-gd="F" aria-pressed="' + (b.g === 'F') + '">여</button><button type="button" data-gd="M" aria-pressed="' + (b.g === 'M') + '">남</button></div>' +
        '<button type="button" class="nz-btn sm dark" data-save>저장</button></div><p class="nz-note">생년월일은 이 기기에만 저장돼요 · 서버로 보내지 않아요</p></details>' +
        '<div class="acts"><button type="button" class="nz-btn sec" data-send>' + I.copy + '고객에게 운세 보내기</button><button type="button" class="nz-btn pri" data-full>' + I.moon + '전체 운세 · 타로 4장</button></div>' +
        '<p class="nz-note">재미로 보는 풀이예요 · 오늘의 운세(사주 + 타로) 엔진 그대로</p>');
      NZ.vars(body);
      let gd = b.g;
      body.querySelectorAll('[data-gd]').forEach((x) => x.addEventListener('click', () => { gd = x.dataset.gd; body.querySelectorAll('[data-gd]').forEach((y) => y.setAttribute('aria-pressed', String(y === x))); }));
      body.querySelector('[data-save]').addEventListener('click', () => {
        const v = body.querySelector('[data-bd]').value;
        if (!/^\d{4}-\d{2}-\d{2}$/.test(v)) { NZ.toast('생년월일을 골라 주세요'); return; }
        NZ.local.set('birth', v); NZ.local.set('gender', gd); NZ.log('fortune', 'birth_set');
        draw(); NZ.ui.refreshPop && NZ.ui.current() && NZ.ui.refreshPop(true);
        NZ.toast('이 기기에 저장했어요. 내일부터는 바로 보여요', { icon: 'check' });
      });
      body.querySelector('[data-send]').addEventListener('click', () => sendFortune('고객님, 오늘 운세 한번 보실래요? 이름과 생년월일만 넣으면 사주와 타로로 오늘 하루를 알려 줘요. 재미로 가볍게 보세요.'));
      body.querySelector('[data-full]').addEventListener('click', () => { g.ov.close(); NZ.ui.go('fortune'); });
    }
    NZ.run(NZ.api.event('fortune.open', {}), { quiet: true });
  }

  // ═════ 전체 운세 화면을 덮개 안에 띄우기 (목업 · 사내 웹서버판 공용) ═════
  NZ.fun.openFrame = (url, title) => {
    const el = NZ.el('<div class="nz-frame"><div class="bar"><b>' + esc(title || '오늘의 운세') + '</b><a class="nz-btn sm ghost" href="' + esc(url) + '" target="_blank" rel="noopener">새 창으로</a><button type="button" class="nz-btn sm sec" data-gclose>닫기</button></div><iframe src="' + esc(url) + '" title="' + esc(title || '오늘의 운세') + '"></iframe></div>');
    const ov = NZ.overlay(el, { label: title || '오늘의 운세', skip: false, clickClose: true });
    el.addEventListener('click', (e) => { if (e.target.closest('[data-gclose]')) ov.close(); });
    return ov;
  };

  // ═════ 연출 (규칙 엔진 fx) ═════
  NZ.fun.fx = {
    bingo(f) {
      return new Promise((res) => {
        const letters = 'BINGO'.split('').map((c, i) => '<span data-v="d:' + (i * 0.09) + 's">' + c + '</span>').join('');
        const reward = (NZ.home && NZ.home.fun.bingo.rewards.filter((m) => m.got && f.count >= m.lines).pop()) || null;
        const el = NZ.el('<div class="nz-bingofx"><div class="lt">' + letters + '</div><h3>' + (f.count >= 8 ? '9칸 모두 채웠어요!' : f.count + '줄 완성') + '</h3><p>이번 주 영업 빙고 · ' + f.filled + ' / 9칸' + (reward ? ' · ' + esc(reward.label) + ' 응모권 +' + reward.ticket : '') + '</p></div>');
        const ov = NZ.overlay(el, { label: '영업 빙고', auto: 2800, clickAnywhere: true });
        NZ.vars(el); NZ.sfx.win();
        if (NZ.fxMode() === 'full') setTimeout(() => NZ.burst(), 300);
        ov.done.then(res);
      });
    },
    fever(f) {
      if (NZ.fxMode() !== 'full') { NZ.toast('<b>나만의 피버 ' + f.min + '분</b> · 영업 행동 XP ×' + f.mult, { icon: 'flame' }); return Promise.resolve(); }
      return NZ.fx.hero({ cls: 'flame', k: 'FEVER TIME', big: '×' + f.mult, title: '나만의 피버 ' + f.min + '분', text: '지금부터 추천 고객 · 맞춤대화 · 고객 챙기기 XP가 ' + f.mult + '배예요. 연락할 고객부터 볼까요?', icon: I.flame, ms: 2600 });
    }
  };

  // ── 피버 남은 시간 · 시작 알림 ────────────────────────────────
  let wasFever = null;
  NZ.onChange((h) => {
    if (!h.fun) return;
    const on = h.fun.fever.on;
    if (wasFever === false && on && h.fun.fever.kind === 'daily') NZ.toast('<b>' + esc(h.fun.fever.label) + '</b> 시작 · 지금부터 영업 행동 XP ×' + h.fun.fever.mult, { icon: 'flame', ms: 3600 });
    wasFever = on;
  });
  setInterval(() => {
    if (!NZ.home || !NZ.home.fun) return;
    const now = NZ.home.serverTime + (Date.now() - (NZ.homeAt || Date.now()));
    document.querySelectorAll('[data-fever-left]').forEach((e) => { e.textContent = F.clock(+e.dataset.feverLeft - now); });
  }, 1000);
})(window);
