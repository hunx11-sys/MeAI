/* MeAI 홈 넛지 v5 · 연출 (색종이 · 알림 · 날아가기 · 슬롯머신 · 미션 달성 · 추첨 발표 · 주간 리캡 · 행운 존 알림)
 * 원칙 : 화면을 오래 막지 않는다(누르면 바로 닫힘 · Esc · 자동 닫힘), 겹치지 않고 하나씩, 설정에 따라 줄이거나 끈다.
 *   설정 fx = 'full'(화려하게) · 'simple'(알림만) · 'off'(숫자만 바뀜)
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ, I = NZ.I, esc = NZ.esc;

  // ── 층(layer) : 모든 연출은 body 끝의 한 층에 그린다 ──────────────
  let layer = null;
  function L() { if (!layer || !layer.isConnected) { layer = NZ.el('<div class="nz nz-layer" aria-live="off"></div>'); document.body.appendChild(layer); } return layer; }
  NZ.layer = L;

  // ── 알림(토스트) : 한 번에 하나 ───────────────────────────────
  let toastEl = null, toastT = 0;
  NZ.toast = (html, opt) => {
    opt = opt || {};
    if (!toastEl || !toastEl.isConnected) { toastEl = NZ.el('<div class="nz nz-toast" role="status"></div>'); L().appendChild(toastEl); }
    const icon = opt.img ? '<img src="' + esc(opt.img) + '" alt="">' : opt.icon ? '<span class="ti">' + (I[opt.icon] || '') + '</span>' : '';
    NZ.html(toastEl, icon + '<span>' + html + '</span>');
    toastEl.classList.remove('on'); void toastEl.offsetWidth; toastEl.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('on'), opt.ms || 2800);
    NZ.say(html);
  };

  // ── 색종이 ───────────────────────────────────────────────
  const COLORS = ['#e0282f', '#f5b301', '#3a64dc', '#0e9b67', '#ff8a3d', '#ffffff', '#8a3fb0'];
  NZ.confetti = (x, y, n, power) => {
    if (NZ.reduced() || mode() === 'off') return;
    const cv = document.createElement('canvas'); cv.className = 'nz-conf'; const dpr = Math.min(2, G.devicePixelRatio || 1);
    cv.width = innerWidth * dpr; cv.height = innerHeight * dpr; L().appendChild(cv);
    const c = cv.getContext('2d'); c.scale(dpr, dpr);
    const P = [], pw = power || 9;
    for (let i = 0; i < (n || 80); i++) {
      const a = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 1.1, v = pw * (0.45 + Math.random() * 0.75);
      P.push({ x: x, y: y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, w: 6 + Math.random() * 6, h: 4 + Math.random() * 6, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4, c: COLORS[i % COLORS.length], life: 0 });
    }
    let t0 = performance.now();
    (function step(t) {
      const dt = Math.min(32, t - t0) / 16.7; t0 = t; c.clearRect(0, 0, innerWidth, innerHeight); let alive = 0;
      P.forEach((p) => {
        p.life += dt; if (p.life > 110) return; alive++;
        p.vy += 0.32 * dt; p.vx *= 0.99; p.x += p.vx * dt; p.y += p.vy * dt; p.r += p.vr * dt;
        c.save(); c.globalAlpha = Math.max(0, 1 - p.life / 110); c.translate(p.x, p.y); c.rotate(p.r); c.fillStyle = p.c; c.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.abs(Math.cos(p.life / 6))); c.restore();
      });
      if (alive) requestAnimationFrame(step); else cv.remove();
    })(t0);
  };
  NZ.confettiAt = (el, n, power) => { const r = NZ.rect(el); if (r) NZ.confetti(r.left + r.width / 2, r.top + r.height / 2, n, power); };
  NZ.burst = () => { NZ.confetti(innerWidth * 0.3, innerHeight * 0.55, 90, 12); NZ.confetti(innerWidth * 0.7, innerHeight * 0.55, 90, 12); };

  // ── 날아가기 : 응모권 · 세트가 머리 띠 캡슐로 ──────────────────
  NZ.fly = (from, to, kind) => new Promise((res) => {
    const a = NZ.rect(from), b = NZ.rect(to);
    if (!a || !b || NZ.reduced() || mode() !== 'full' || !b.width) { NZ.ui && NZ.ui.bump(kind); return res(); }
    const f = NZ.el('<div class="nz nz-fly' + (kind === 'lotto' ? ' lotto' : '') + '">' + (kind === 'lotto' ? NZ.ball(7, 'sm') : I.ticket) + '</div>');
    L().appendChild(f);
    const x0 = a.left + a.width / 2 - 14, y0 = a.top + a.height / 2 - 14, x1 = b.left + b.width / 2 - 14, y1 = b.top + b.height / 2 - 14;
    const mx = (x0 + x1) / 2, my = Math.min(y0, y1) - 120;
    const an = f.animate([
      { transform: 'translate(' + x0 + 'px,' + y0 + 'px) scale(.6)', opacity: 0 },
      { transform: 'translate(' + x0 + 'px,' + (y0 - 20) + 'px) scale(1.15)', opacity: 1, offset: 0.15 },
      { transform: 'translate(' + mx + 'px,' + my + 'px) scale(1)', opacity: 1, offset: 0.55 },
      { transform: 'translate(' + x1 + 'px,' + y1 + 'px) scale(.7)', opacity: 0.9 }
    ], { duration: 820, easing: 'cubic-bezier(.5,0,.3,1)' });
    an.onfinish = () => { f.remove(); NZ.ui && NZ.ui.bump(kind); NZ.sfx.pop(); res(); };
  });

  // ── 덮개(오버레이) 열기 : 바깥 누르기 · Esc · 자동 닫힘 ────────────
  NZ.overlay = (inner, opt) => {
    opt = opt || {};
    const back = document.activeElement;
    const s = NZ.el('<div class="nz nz-scrim" role="dialog" aria-modal="true" tabindex="-1" aria-label="' + esc(opt.label || '알림') + '"></div>');
    s.appendChild(typeof inner === 'string' ? NZ.el(inner) : inner);
    if (opt.skip !== false) s.appendChild(NZ.el('<button type="button" class="nz-skip" data-skip>' + (opt.skipLabel || '건너뛰기') + '</button>'));
    L().appendChild(s);
    let done, closed = false, timer = 0;
    const p = new Promise((r) => { done = r; });
    function close(v) {
      if (closed) return; closed = true; clearTimeout(timer); document.removeEventListener('keydown', onKey, true);
      s.classList.remove('on'); setTimeout(() => s.remove(), 280);
      if (back && back.focus && opt.restoreFocus !== false) try { back.focus({ preventScroll: true }); } catch (e) { /* 포커스를 돌려줄 곳이 없으면 그대로 */ }
      done(v);
    }
    function onKey(e) { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); (opt.onSkip || close)('esc'); } }
    document.addEventListener('keydown', onKey, true);
    s.addEventListener('click', (e) => {
      if (e.target.closest('[data-skip]')) return (opt.onSkip || close)('skip');
      if (opt.clickClose !== false && (e.target === s || opt.clickAnywhere)) (opt.onSkip || close)('click');
    });
    requestAnimationFrame(() => { s.classList.add('on'); try { s.focus({ preventScroll: true }); } catch (e) { /* 무시 */ } });
    const api = { el: s, close: close, done: p, hold() { clearTimeout(timer); }, auto(ms) { clearTimeout(timer); timer = setTimeout(() => close('auto'), ms); } };
    if (opt.auto) api.auto(opt.auto);
    return api;
  };

  function mode() { return (NZ.home && NZ.home.settings && NZ.home.settings.fx) || 'full'; }
  NZ.fxMode = mode;

  // ── 슬롯머신 : 세트 발급 ─────────────────────────────────────
  function slot(f) {
    return new Promise((res) => {
      const label = (NZ.home && NZ.home.labels.lotto) || 'MeAI 로또';
      const reels = f.nums.map((n) => {
        const seq = []; for (let i = 0; i < 16; i++) seq.push(1 + Math.floor(Math.random() * 45)); seq.push(n);
        return '<div class="nz-reel"><div class="nz-strip">' + seq.map((x) => '<div>' + x + '</div>').join('') + '</div></div>';
      }).join('');
      const m = NZ.el('<div class="nz-machine spin" role="img" aria-label="' + esc(label) + ' 번호 ' + f.nums.join(', ') + '">' +
        '<div class="lamp">' + '<i></i>'.repeat(9) + '</div>' +
        '<div class="t1">추천 고객 맞춤 영업 보너스</div><h3>' + esc(label) + ' 1세트 자동 응모</h3>' +
        '<div class="nz-reels">' + reels + '</div><div class="nz-balls">' + f.nums.map((n) => NZ.ball(n, 'lg')).join('') + '</div>' +
        '<div class="nz-mstamp">응모<br>완료</div>' +
        '<div class="cap">릴을 누르면 바로 멈춰요</div>' +
        '<div class="acts"><button type="button" class="nz-btn sec sm" data-open="lotto">내 번호 모두 보기</button><button type="button" class="nz-btn pri sm" data-close>계속 영업하기</button></div></div>');
      const ov = NZ.overlay(m, { label: label + ' 응모', clickClose: false, skipLabel: '바로 멈추기' });
      const anims = [];
      let stopped = 0, finished = false, tickT = setInterval(() => NZ.sfx.tick(), 90);
      NZ.$$('.nz-reel', m).forEach((rl, i) => {
        const st = rl.querySelector('.nz-strip'), h = 84, dist = 16 * h;
        if (NZ.reduced()) { st.style.transform = 'translateY(' + (-dist) + 'px)'; stopped++; return; }
        const a = st.animate([{ transform: 'translateY(0)' }, { transform: 'translateY(' + (-dist) + 'px)' }], { duration: 900 + i * 300, easing: 'cubic-bezier(.12,.6,.2,1)', fill: 'forwards' });
        anims.push(a);
        a.onfinish = () => { rl.classList.add('stop'); NZ.sfx.ding(); const b = m.querySelectorAll('.nz-balls .ball')[i]; if (b) b.classList.add('pop'); if (++stopped === 6) finish(); };
      });
      if (stopped === 6) finish();
      function finish() {
        if (finished) return; finished = true; clearInterval(tickT);
        m.classList.remove('spin'); NZ.$$('.nz-balls .ball', m).forEach((b) => b.classList.add('pop'));
        const sp = m.querySelector('.nz-mstamp'); sp.classList.add('on'); NZ.sfx.stamp();
        const t = NZ.home && NZ.home.lotto;
        NZ.html(m.querySelector('.cap'), '이번 주 <b>' + f.nth + '번째</b> 세트 · ' + (f.nextRound ? '마감이 지나 <b>다음 주 회차</b>로 응모돼요' : '금요일 <b>17:00</b> 추첨') + (t ? ' · 오늘 ' + t.todayIssued + '/' + t.dailyMax + '세트' : ''));
        m.querySelector('.acts').classList.add('on');
        setTimeout(() => NZ.confettiAt(sp, 60, 9), 200);
        const flyFrom = m.querySelector('.nz-balls');
        setTimeout(() => { NZ.fly(flyFrom, NZ.ui && NZ.ui.anchor('cap-lotto'), 'lotto'); }, 600);
        let hover = false; m.addEventListener('pointerenter', () => { hover = true; ov.hold(); }); m.addEventListener('pointerleave', () => { hover = false; ov.auto(1600); });
        if (!hover) ov.auto(2600);
      }
      function stopNow() { anims.forEach((a) => { try { a.finish(); } catch (e) { /* 이미 끝남 */ } }); finish(); }
      m.addEventListener('click', (e) => {
        if (e.target.closest('[data-close]')) return ov.close();
        if (e.target.closest('[data-open]')) { ov.close(); NZ.ui && NZ.ui.open('lotto', 'pin'); return; }
        if (!finished) stopNow();
      });
      const origSkip = () => { if (!finished) stopNow(); else ov.close(); };
      ov.el.querySelector('[data-skip]').addEventListener('click', (e) => { e.stopPropagation(); origSkip(); }, true);
      ov.done.then(() => { clearInterval(tickT); res(); });
    });
  }

  // ── 미션 하나 달성 : 카드가 쾅 → 루틴 고리로 쏙 ───────────────────
  function questClear(f) {
    return new Promise((res) => {
      const ringColor = { come: '#e0282f', learn: '#3a64dc', sell: '#0e9b67' }[f.ring] || '#0e9b67';
      const pips = Array.from({ length: f.total }, (_, i) => '<i class="' + (i < f.n ? 'on' : '') + '"></i>').join('');
      const c = NZ.el('<div class="nz-clear" data-v="c:' + ringColor + '"><div class="medal">' + I.check + '</div><div class="k">MISSION CLEAR</div><h3>' + esc(f.title) + '</h3><p>오늘의 루틴 ' + f.n + ' / ' + f.total + (f.n < 3 ? ' · ' + (3 - f.n) + '개 더 하면 응모권 +1' : f.n < f.total ? ' · ' + (f.total - f.n) + '개 더 하면 올클리어' : '') + '</p><div class="pips">' + pips + '</div></div>');
      const ov = NZ.overlay(c, { label: '미션 달성', skip: false, clickAnywhere: true, restoreFocus: false });
      ov.el.classList.add('quiet');
      requestAnimationFrame(() => c.classList.add('in'));
      NZ.sfx.clear();
      setTimeout(() => NZ.confettiAt(c, 40, 7), 260);
      const shake = NZ.$('#root') || document.body;
      if (!NZ.reduced() && shake.animate) shake.animate([{ transform: 'translate(0)' }, { transform: 'translate(-4px,2px)' }, { transform: 'translate(4px,-2px)' }, { transform: 'translate(0)' }], { duration: 260, delay: 220 });
      const target = NZ.ui && NZ.ui.anchor('quest');
      let t = setTimeout(go, 1500);
      function go() {
        clearTimeout(t);
        const a = NZ.rect(c), b = NZ.rect(target);
        if (a && b && b.width && b.top > -50 && b.top < innerHeight) {
          c.style.setProperty('--tx', (b.left + b.width / 2 - (a.left + a.width / 2)) + 'px');
          c.style.setProperty('--ty', (b.top + b.height / 2 - (a.top + a.height / 2)) + 'px');
          c.classList.add('fly');
          setTimeout(() => { ov.close(); NZ.ui && NZ.ui.bump('quest'); }, 520);
        } else ov.close();
      }
      ov.done.then(res);
      ov.el.addEventListener('click', () => go(), { once: true });
    });
  }

  // ── 큰 축하(일일 미션 · 올클리어 · 연속 기록 · 첫 경험 · 당첨) ──────
  function hero(o) {
    return new Promise((res) => {
      const h = NZ.el('<div class="nz-hero ' + (o.cls || '') + '"><div class="rays"></div>' +
        '<div class="medal">' + (o.img ? '<img src="' + esc(o.img) + '" alt="">' : (o.icon || I.star)) + '</div>' +
        (o.big ? '<div class="big">' + o.big + '</div>' : '') +
        '<div class="k">' + esc(o.k) + '</div><h3>' + o.title + '</h3>' + (o.text ? '<p>' + o.text + '</p>' : '') +
        (o.gift ? '<div class="gift">' + I.ticket + ' ' + o.gift + '</div>' : '') +
        (o.btn ? '<div><button type="button" class="nz-btn pri" data-go="' + esc(o.btn.go) + '">' + esc(o.btn.label) + '</button></div>' : '') + '</div>');
      const ov = NZ.overlay(h, { label: o.k, auto: o.ms || 2800, clickAnywhere: true });
      NZ.sfx.win();
      if (o.confetti) setTimeout(() => NZ.burst(), 250);
      h.addEventListener('click', (e) => { const g = e.target.closest('[data-go]'); if (g) { ov.close(); NZ.ui && NZ.ui.go(g.getAttribute('data-go')); } });
      ov.done.then(res);
    });
  }

  // ── 연출 대기열 ───────────────────────────────────────────
  let chain = Promise.resolve();
  const TICKET_FX = { 'attend': 'stamp', 'quiz.correct': 'quiz', 'talk.copy': 'talk', 'quest.mission': 'mission', 'quest.allclear': 'allclear', 'attend.perfect': 'perfect' };
  NZ.fx = {
    play(fx, grants, ctx) { chain = chain.then(() => run(fx, grants, ctx)).catch((e) => console.error('[넛지 연출]', e)); return chain; },
    slot: slot, questClear: questClear, hero: hero,
    draw: (data) => (chain = chain.then(() => drawShow(data))),
    recap: (data) => (chain = chain.then(() => story(data)))
  };

  async function run(fx, grants, ctx) {
    const m = mode(), tickets = grants.filter((g) => g.type === 'ticket');
    const fromOf = (type) => (ctx && ctx.from) || (NZ.ui && NZ.ui.fxSource(type));
    const flyTickets = async (type) => {
      for (const g of tickets.filter((x) => TICKET_FX[x.rule] === type || (type === 'pass' && /^pass\./.test(x.rule)))) {
        g._flown = true;
        await NZ.fly(fromOf(type), NZ.ui && NZ.ui.anchor('cap-ticket'), 'ticket');
      }
    };
    grants.filter((g) => g.rule === 'shield.monthly').forEach((g) => NZ.toast('이달의 <b>보호권 ' + g.amount + '장</b>이 들어왔어요. 휴가 · 교육 날 연속 기록을 지켜 줘요', { icon: 'shield' }));
    const hasMilestone = fx.some((f) => f.type === 'streak');
    for (const f of fx) {
      if (m === 'off') continue;
      const simple = m === 'simple';
      switch (f.type) {
        case 'stamp':
          if (!simple && NZ.ui) await NZ.ui.stampAnim();
          await flyTickets('stamp');
          break;
        case 'flame':
          NZ.ui && NZ.ui.ignite();
          if (!hasMilestone) NZ.toast('<b>' + f.to + '영업일 연속</b> · 오늘도 고객을 찾아가고 있어요', { icon: 'flame' });
          break;
        case 'perfect':
          NZ.toast('이번 주 <b>개근</b> · 커피 응모권 <b>+3</b>', { icon: 'ticket' }); await flyTickets('perfect'); break;
        case 'quiz':
          if (f.correct) { if (!simple) NZ.confettiAt(fromOf('quiz'), 50, 8); NZ.sfx.win(); await flyTickets('quiz'); }
          if (f.combo >= 3 && f.correct) NZ.toast('퀴즈 <b>' + f.combo + '연속</b> 정답', { icon: 'spark' });
          break;
        case 'talk':
          if (!simple) NZ.confettiAt(fromOf('talk'), 50, 8);
          NZ.sfx.clear();
          if (f.rewarded) await flyTickets('talk'); else NZ.toast('잘 썼어요. 오늘 응모권은 이미 받았어요 · 연습은 얼마든지', { icon: 'quote' });
          break;
        case 'quest':
          if (simple) NZ.toast('미션 달성 · <b>' + esc(f.title) + '</b> (' + f.n + '/' + f.total + ')', { icon: 'check' });
          else await questClear(f);
          break;
        case 'mission':
          if (simple) NZ.toast('오늘의 <b>일일 미션 달성</b> · 응모권 +1', { icon: 'medal' });
          else await hero({ k: 'DAILY MISSION', title: '오늘의 일일 미션 달성', text: '루틴 3개를 채웠어요. 2개 더 하면 올클리어 보너스까지.', gift: '커피 응모권 +1', icon: I.medal, ms: 2600 });
          await flyTickets('mission');
          break;
        case 'allclear':
          if (simple) NZ.toast('<b>퀘스트 올클리어</b> · 응모권 +2', { icon: 'star' });
          else await hero({ k: 'ALL CLEAR', title: '퀘스트 올클리어', text: '오늘 할 일을 모두 마쳤어요. 내일도 이 흐름 그대로.', gift: '보너스 응모권 +2', icon: I.star, confetti: true, ms: 3200 });
          await flyTickets('allclear');
          break;
        case 'slot':
          if (simple) NZ.toast((NZ.home ? NZ.home.labels.lotto : 'MeAI 로또') + ' 1세트 응모 · ' + f.nums.map((n) => '<b>' + n + '</b>').join(' '), { icon: 'lotto', ms: 3600 });
          else await slot(f);
          break;
        case 'streak':
          if (simple) NZ.toast('<b>' + f.days + '영업일 연속</b> 달성' + (f.badge ? ' · 배지 「' + esc(f.badge) + '」' : ''), { icon: 'flame' });
          else await hero({ cls: 'flame', k: 'STREAK', big: f.days, title: '영업일 연속', text: f.badge ? '배지 「' + esc(f.badge) + '」를 받았어요. 다음 목표까지 계속 이어가요.' : '연속 기록 달성. 오늘도 불을 켰어요.', icon: I.flame, confetti: true, ms: 3000 });
          break;
        case 'pass':
          NZ.toast('주간 패스 <b>' + f.step + '단계</b> · ' + esc(f.label) + (f.badge ? ' · 배지 「' + esc(f.badge) + '」' : ''), { icon: 'gift' });
          NZ.ui && NZ.ui.bump('league'); await flyTickets('pass');
          break;
        case 'rankup':
          NZ.toast('지점 리그 <b>' + f.from + '위 → ' + f.to + '위</b>로 올랐어요', { icon: 'trophy' }); NZ.ui && NZ.ui.bump('league'); break;
        case 'badge':
          NZ.toast('배지 <b>「' + esc(f.label) + '」</b> · ' + esc(f.desc), { icon: 'medal', ms: 3400 }); break;
        case 'first':
          if (simple) NZ.toast('<b>' + esc(f.title) + '</b> · ' + esc(f.text), { img: NZ.mascot('success_thumbs') });
          else await hero({ cls: 'blue', k: '첫 경험', title: esc(f.title), text: esc(f.text), img: NZ.mascot(f.kind === 'attend' ? 'hello_wave' : f.kind === 'quiz' ? 'tata_ok' : f.kind === 'talk.copy' ? 'indi_idea' : 'success_thumbs'), ms: 2600 });
          break;
        case 'shield':
          NZ.toast('<b>보호권 ' + f.days.length + '장</b>으로 연속 기록을 지켰어요 (' + f.days.map((d) => NZ.fmt.md(d)).join(', ') + ')', { icon: 'shield', ms: 3600 }); break;
        case 'cheer':
          NZ.toast('응원을 보냈어요. 오늘 남은 응원 ' + Math.max(0, (NZ.home && NZ.home.league.cheersLeft) || 0) + '번', { icon: 'clap' }); break;
        // 행운 존 : 게임 화면이 직접 보여 주는 결과(roulette · cslot · challenge · tarot · scratch · crm)는 여기서 다시 그리지 않는다
        case 'scratchNew':
          NZ.toast('<b>스크래치 복권 1장</b>이 생겼어요 · 행운 존에서 긁어 보세요', { icon: 'gift', ms: 3600 }); NZ.ui && NZ.ui.bump('fun'); break;
        case 'fever':
          if (NZ.fun) await NZ.fun.fx.fever(f); break;
        case 'bingo':
          if (simple || !NZ.fun) NZ.toast('영업 빙고 <b>' + f.count + '줄</b> 완성', { icon: 'star' }); else await NZ.fun.fx.bingo(f);
          break;
        case 'cslotClear':
          NZ.toast('슬롯 고객 3명을 모두 챙겼어요 · <b>XP +' + f.xp + '</b>', { icon: 'check' }); break;
        case 'capped':
          NZ.toast('오늘 행운 존 응모권 ' + f.cap + '장을 모두 받았어요 · 대신 <b>XP +' + f.xp + '</b>', { icon: 'info', ms: 3600 }); break;
        default: break;
      }
    }
    // 연출과 짝이 없는 응모권은 한꺼번에 날린다
    for (const g of tickets.filter((x) => !x._flown)) { if (m === 'full') await NZ.fly(fromOf('any'), NZ.ui && NZ.ui.anchor('cap-ticket'), 'ticket'); else NZ.ui && NZ.ui.bump('ticket'); }
    if (fx.length) NZ.say(fx.map((f) => ({ stamp: '출석 도장 완료', quest: '미션 달성 ' + (f.title || ''), mission: '일일 미션 달성', allclear: '퀘스트 올클리어', slot: '로또 1세트 응모', streak: f.days + '영업일 연속', bingo: '영업 빙고 ' + f.count + '줄', scratchNew: '스크래치 복권 1장', fever: '피버 타임' }[f.type] || '')).filter(Boolean).join(' · '));
  }

  // ── 금요일 17시 추첨 발표 ──────────────────────────────────
  function drawShow(d) {
    return new Promise((res) => {
      const lotto = d.lotto, draw = d.draw, sets = d.sets;
      const rows = sets.length ? sets.map((s) => '<div class="row" data-no="' + s.no + '"><span class="no">' + s.no + '번</span>' + s.nums.map((n) => NZ.ball(n, 'sm')).join('') + '<span class="res"></span></div>').join('')
        : '<div class="empty">이번 주에 받은 세트가 없어요. 다음 주에는 추천 고객으로 세트를 모아 보세요.</div>';
      const box = NZ.el('<div class="nz-draw"><div class="k">' + esc(lotto.label) + ' · ' + esc(lotto.name) + (d.example ? ' · 예시 화면' : '') + '</div><h3>이번 주 당첨번호</h3>' +
        '<div class="wins">' + draw.map((n) => NZ.ball(n, 'lg')).join('') + '</div><div class="nz-sets mine">' + rows + '</div><div class="dres"></div>' +
        '<div class="nz-note">' + (d.example ? '당첨 장면을 보여 주는 예시예요. ' : '') + '추첨 씨앗 지문 <code>' + esc((lotto.commit || '').slice(0, 16)) + '…</code> · 씨앗 공개 <code>' + esc((d.seed || lotto.seed || '').slice(0, 16)) + '…</code></div></div>');
      const ov = NZ.overlay(box, { label: '이번 주 당첨번호', clickClose: true });
      const balls = NZ.$$('.wins .ball', box);
      let i = 0, best = 0, prize = '';
      (function next() {
        if (i < balls.length) { balls[i].classList.add('roll'); NZ.sfx.ding(); i++; setTimeout(next, NZ.reduced() ? 40 : 620); return; }
        sets.forEach((s) => {
          const row = box.querySelector('[data-no="' + s.no + '"]'); if (!row) return;
          const hit = s.nums.filter((n) => draw.indexOf(n) >= 0).length;
          NZ.$$('.ball', row).forEach((b, k) => b.classList.add(draw.indexOf(s.nums[k]) >= 0 ? 'hit' : 'dim'));
          const tr = (lotto.tiers || []).filter((t) => hit >= t.match).sort((a, b) => b.match - a.match)[0];
          row.querySelector('.res').textContent = hit + '개 일치' + (tr ? ' · ' + tr.prize : '');
          if (tr) row.classList.add('win');
          if (hit > best) { best = hit; prize = tr ? tr.prize : ''; }
        });
        const r = box.querySelector('.dres');
        if (prize) { NZ.html(r, '<div class="banner on">' + I.gift + ' ' + esc(prize) + ' 당첨 · ' + best + '개 일치</div>'); NZ.burst(); NZ.sfx.win(); }
        else NZ.html(r, '<div class="banner miss on">이번 주는 최고 ' + best + '개 일치 · 다음 주에 다시 도전해요</div>');
      })();
      ov.done.then(res);
    });
  }

  // ── 주간 리캡 (금요일 17시 뒤 · 이야기 다섯 장) ─────────────────
  function story(rc) {
    return new Promise((res) => {
      const nm = NZ.home ? NZ.home.user.name : '';
      const slides = [
        '<div class="sl s1"><div class="k">' + esc(rc.weekLabel) + ' 나의 MeAI</div><h3>' + esc(nm) + '님의<br>이번 주를 모아 봤어요</h3><div class="huge">' + rc.litDays + '<small>일</small></div><p>이번 주 MeAI 불을 켠 영업일<br>연속 기록 <b>' + rc.streak + '영업일</b> 이어가는 중</p></div>',
        '<div class="sl s2"><div class="k">고객</div><h3>MeAI 로 준비한 고객</h3><div class="huge">' + rc.customers + '<small>명</small></div><p>맞춤대화 <b>' + rc.chats + '번</b> · 추천 고객을 열 때마다 영업이 한 걸음씩</p></div>',
        '<div class="sl s3"><div class="k">배움</div><h3>퀴즈와 화법</h3><div class="grid"><div><b>' + rc.quiz.ok + '/' + rc.quiz.n + '</b><small>퀴즈 정답</small></div><div><b>' + rc.talks + '번</b><small>화법 따라 쓰기</small></div><div><b>' + NZ.fmt.n(rc.xp) + '</b><small>이번 주 XP</small></div><div><b>' + rc.rank + '위</b><small>지점 리그 (' + rc.total + '명)</small></div></div></div>',
        '<div class="sl s4"><div class="k">보상</div><h3>이번 주 모은 것</h3><div class="grid"><div><b>' + rc.tickets + '장</b><small>커피 응모권</small></div><div><b>' + rc.sets + '세트</b><small>' + esc(NZ.home ? NZ.home.labels.lotto : '로또') + '</small></div></div><img src="' + esc(NZ.mascot('rara_present')) + '" alt=""></div>',
        '<div class="sl s5"><div class="k">다음 주</div><h3>이렇게 해 보면 어때요?</h3><div class="tips">' + rc.tips.map((t) => '<div>' + esc(t) + '</div>').join('') + '</div><img src="' + esc(NZ.mascot('ziziri_cheer')) + '" alt=""></div>'
      ];
      const n = slides.length;
      const box = NZ.el('<div class="nz-story" data-v="dur:5s"><div class="bars">' + '<i><b></b></i>'.repeat(n) + '</div>' + slides.join('') +
        '<button type="button" class="tap l" aria-label="이전"></button><button type="button" class="tap r" aria-label="다음"></button><button type="button" class="x" aria-label="닫기">' + I.x + '</button></div>');
      const ov = NZ.overlay(box, { label: '이번 주 리캡', clickClose: true, skip: false });
      let k = -1, t = 0;
      function show(i) {
        if (i >= n) return ov.close(); if (i < 0) i = 0; k = i; clearTimeout(t);
        NZ.$$('.sl', box).forEach((s, j) => s.classList.toggle('on', j === k));
        NZ.$$('.bars i', box).forEach((b, j) => { b.classList.toggle('done', j < k); b.classList.remove('cur'); if (j === k) { void b.offsetWidth; b.classList.add('cur'); } });
        t = setTimeout(() => show(k + 1), 5000);
      }
      box.querySelector('.tap.l').addEventListener('click', (e) => { e.stopPropagation(); show(k - 1); });
      box.querySelector('.tap.r').addEventListener('click', (e) => { e.stopPropagation(); show(k + 1); });
      box.querySelector('.x').addEventListener('click', (e) => { e.stopPropagation(); ov.close(); });
      ov.el.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') show(k + 1); if (e.key === 'ArrowLeft') show(k - 1); });
      show(0);
      ov.done.then(() => { clearTimeout(t); res(); });
    });
  }
})(window);
