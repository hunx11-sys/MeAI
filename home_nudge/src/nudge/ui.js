/* MeAI 홈 넛지 v5 · 홈 위의 부품 (오늘의 MeAI 막대 · 머리 띠 캡슐 · 버디 말풍선 · 추천 고객 배지 · 펼침 카드)
 * 홈의 기본 구성(대화 카드 · 내 고객 찾기 · 오늘의 추천 고객)은 건드리지 않는다. 막대 한 줄만 더하고, 카드는 그 위에 뜬다.
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ, I = NZ.I, esc = NZ.esc, F = NZ.fmt;
  const ui = NZ.ui = {};
  let dock, cap, buddy, pop, popScrim, recHint, host;
  const items = {};   // 막대의 단추들 (key → element)
  const POP = { key: null, mode: null, t: 0, anchor: null };

  // ── 만들기 ───────────────────────────────────────────────
  ui.build = (h) => {
    host = h;
    dock = NZ.el('<div class="nz nz-dockwrap"><div class="nz-dock" role="toolbar" aria-label="오늘의 MeAI"></div></div>');
    cap = NZ.el('<div class="nz nz-cap"></div>');
    buddy = NZ.el('<div class="nz nz-buddy" role="status"></div>');
    pop = NZ.el('<div class="nz nz-pop" role="dialog" aria-modal="false"><div class="nz-arr"></div><div class="nz-card"></div></div>');
    popScrim = NZ.el('<div class="nz nz-pop-scrim"></div>');
    recHint = NZ.el('<span class="nz nz-rechint"></span>');
    document.body.appendChild(pop); document.body.appendChild(popScrim);
    wire();
    return { dock: dock, cap: cap, buddy: buddy, recHint: recHint };
  };
  ui.nodes = () => ({ dock: dock, cap: cap, buddy: buddy, recHint: recHint });

  // ── 막대(독) 그리기 : 단추는 그대로 두고 안쪽 글만 바꾼다(마우스 올림 · 초점 유지) ──
  function setItem(key, cls, html, label, todo, gold) {
    const box = dock.firstElementChild;
    let b = items[key];
    if (!b) { b = NZ.el('<button type="button" class="nz-di ' + cls + '" data-k="' + key + '" aria-expanded="false" aria-haspopup="dialog"></button>'); items[key] = b; }
    if (b._html !== html) { b._html = html; const halo = b.querySelector(':scope > .nz-halo'); NZ.html(b, html); if (halo) b.appendChild(halo); }
    b.setAttribute('aria-label', label);
    NZ.breathe(b.querySelector('.nz-ic, .nz-ringwrap'), !!todo, gold);
    return b;
  }
  // 고리 3개 (바깥 = 오기 · 가운데 = 배우기 · 안 = 영업하기). 큰 고리는 가운데에 숫자를 넣을 자리를 비운다.
  function ringSvg(q, size) {
    const big = size >= 80, R = big ? [0.45, 0.35, 0.25] : [0.43, 0.31, 0.19], sw = size * (big ? 0.075 : 0.1), c = size / 2;
    let s = '<svg viewBox="0 0 ' + size + ' ' + size + '" aria-hidden="true">';
    ['come', 'learn', 'sell'].forEach((k, i) => {
      const g = q.rings[k] || { done: 0, total: 1 }, rr = R[i] * size, len = 2 * Math.PI * rr, p = g.total ? g.done / g.total : 0;
      s += '<circle class="bg" cx="' + c + '" cy="' + c + '" r="' + rr.toFixed(2) + '" stroke-width="' + sw.toFixed(2) + '"/>';
      s += '<circle cx="' + c + '" cy="' + c + '" r="' + rr.toFixed(2) + '" stroke="' + g.color + '" stroke-width="' + sw.toFixed(2) + '" stroke-dasharray="' + len.toFixed(2) + '" stroke-dashoffset="' + (len * (1 - p)).toFixed(2) + '"/>';
    });
    return s + '</svg>';
  }
  ui.ringSvg = ringSvg;

  ui.render = (h) => {
    if (!dock) return;
    const box = dock.firstElementChild, q = h.quests, s = h.streak, lo = h.lotto, lg = h.league, tk = h.talk;
    const order = [];
    // ① 오늘의 루틴 (퀘스트 고리 3개)
    order.push(setItem('quest', 'nz-di-ring', '<span class="nz-ringwrap">' + ringSvg(q, 42) + '</span>' +
      '<span class="nz-tx"><b>오늘의 루틴 ' + q.done + '/' + q.total + '</b><small>' + (q.allclear ? '올클리어 완료' : q.mission ? '일일 미션 달성 · 올클리어까지 ' + (q.total - q.done) : (q.need - q.done) + '개 더 하면 <em>응모권</em>') + '</small></span>',
      '오늘의 루틴 ' + q.done + '/' + q.total, false));
    order.push('sep');
    // ② 출석 · 연속 기록
    const wk = h.week.days.map((d) => '<i class="' + (d.state === 'stamp' ? 'on' : d.state === 'today' ? 'today' : d.state === 'holiday' ? 'hol' : '') + '"></i>').join('');
    order.push(setItem('attend', 'nz-di-attend', '<span class="nz-ic' + (s.todayLit ? '' : ' off') + '">' + I.flame + (h.attendedToday ? '<i class="nz-check">' + I.check + '</i>' : '') + '</span>' +
      '<span class="nz-tx"><b>' + (s.current ? s.current + '영업일 연속' : '연속 기록 시작') + '</b><small>' + (h.attendedToday ? '오늘 출석 완료' : h.bizDay ? '오늘 도장 전' : '쉬는 날') + ' <span class="nz-week5">' + wk + '</span></small></span>',
      '출석 · 연속 ' + s.current + '영업일', h.bizDay && !h.attendedToday));
    // ③ 오늘의 퀴즈
    const qz = h.quiz;
    order.push(setItem('quiz', 'nz-di-quiz', '<span class="nz-ic">' + I.quiz + (qz.answered ? '<i class="nz-check">' + I.check + '</i>' : '') + '</span>' +
      '<span class="nz-tx"><b>오늘의 퀴즈</b><small>' + (!qz.open ? '9시에 열려요' : qz.answered ? (qz.correct ? '정답 · 해설 보기' : qz.explained ? '해설 확인 완료' : '해설 읽으면 인정') : esc(qz.category) + ' · ' + (qz.type === 'ox' ? 'O / X' : '객관식')) + '</small></span>',
      '오늘의 퀴즈', qz.open && (!qz.answered || (!qz.correct && !qz.explained))));
    // ④ 오늘의 화법 (한 줄이 굴러 바뀜)
    order.push(setItem('talk', 'nz-di-talk', '<span class="nz-ic">' + I.quote + (tk.copiedToday ? '<i class="nz-check">' + I.check + '</i>' : '') + '</span>' +
      '<span class="nz-tx"><b>오늘의 화법 <span class="nz-note">· ' + F.n(tk.total) + '건</span></b><small class="nz-tick"><span>' + esc(tickHead()) + '</span></small></span>',
      '오늘의 화법', !tk.copiedToday));
    // ⑤ 로또(행운번호)
    const left = lo.phase === 'collect' ? lo.cutoffAt - h.serverTime : lo.drawAt - h.serverTime;
    const lsub = lo.phase === 'drawn' ? (lo.drawSeen ? '이번 주 결과 보기' : '<em>당첨번호 발표</em>') : lo.phase === 'closed' ? '17시 추첨 · ' + F.left(left) + ' 뒤' : '금 17시 추첨 · 마감 ' + F.left(left);
    order.push(setItem('lotto', 'nz-di-lotto', '<span class="nz-ic">' + I.lotto + (lo.phase === 'drawn' && !lo.drawSeen ? '<i class="nz-new"></i>' : '') + '</span>' +
      '<span class="nz-tx"><b>' + esc(lo.name.replace('MeAI ', '')) + ' ' + lo.sets.length + '세트</b><small>' + lsub + '</small></span>',
      lo.name + ' ' + lo.sets.length + '세트', lo.phase === 'drawn' && !lo.drawSeen, true));
    // ⑥ 리그 (신인은 첫 7일 여정)
    if (h.onboarding) {
      const dn = h.onboarding.steps.filter((x) => x.done).length;
      order.push(setItem('journey', 'nz-di-league', '<span class="nz-ic">' + I.route + '</span><span class="nz-tx"><b>첫 7일 여정</b><small>' + dn + ' / ' + h.onboarding.steps.length + ' 완료</small></span>', '첫 7일 여정', dn < h.onboarding.steps.length));
    } else {
      const hide = h.settings.hideRank;
      order.push(setItem('league', 'nz-di-league', '<span class="nz-ic">' + I.trophy + '</span><span class="nz-tx"><b>' + (hide ? '주간 패스' : '지점 ' + lg.rank + '위') + '</b><small>' +
        (hide ? F.n(lg.xp) + ' XP' : lg.rank === 1 ? '1위 유지 중 · ' + F.n(lg.xp) + ' XP' : '▲ ' + (lg.rank - 1) + '위까지 ' + lg.gap + ' XP') + '</small></span>', '리그', false));
    }
    // ⑦ 주간 리캡 (금요일 17시 뒤)
    if (h.recap.available) order.push(setItem('recap', 'nz-di-recap', '<span class="nz-ic">' + I.play + (h.recap.seen ? '' : '<i class="nz-new"></i>') + '</span><span class="nz-tx"><b>이번 주 리캡</b><small>' + esc(h.week.label) + '</small></span>', '이번 주 리캡', !h.recap.seen));
    // ⑧ 더보기 (운세 보내기 · 넛지 설정)
    order.push(setItem('more', 'nz-di-more', I.dots, '더보기 · 오늘의 운세 · 넛지 설정', false));

    // 순서대로 꽂기 (이미 있는 것은 옮기지 않는다)
    let i = 0;
    order.forEach((it) => {
      let node = it === 'sep' ? (box._sep || (box._sep = NZ.el('<i class="nz-sep" aria-hidden="true"></i>'))) : it;
      if (box.children[i] !== node) box.insertBefore(node, box.children[i] || null);
      i++;
    });
    while (box.children.length > i) box.removeChild(box.lastElementChild);
    Object.keys(items).forEach((k) => { if (!items[k].isConnected) delete items[k]; });

    renderCap(h); renderBuddy(h); renderReco(h);
    if (POP.key && pop.classList.contains('on')) ui.refreshPop();
  };

  // ── 화법 한 줄 굴리기 ─────────────────────────────────────
  let tickI = 0, tickT = 0;
  function tickList() { return (NZ.home && NZ.home.talk.ticker) || []; }
  function tickHead() { const l = tickList(); return l.length ? l[tickI % l.length].head : ''; }
  ui.tickTalk = () => tickList()[tickI % Math.max(1, tickList().length)];
  function startTicker() {
    clearTimeout(tickT);
    const sec = NZ.home ? NZ.home.settings.tickerSec : 8;
    if (!sec) return;
    tickT = setTimeout(function roll() {
      const b = items.talk, sp = b && b.querySelector('.nz-tick');
      if (sp && !b.matches(':hover') && POP.key !== 'talk' && !NZ.reduced()) {
        tickI++;
        const cur = sp.firstElementChild, nx = document.createElement('span'); nx.className = 'in'; nx.textContent = tickHead();
        sp.appendChild(nx); void nx.offsetWidth; cur.classList.add('out'); nx.classList.remove('in');
        setTimeout(() => { cur.remove(); b._html = null; }, 520);
      }
      tickT = setTimeout(roll, (NZ.home ? NZ.home.settings.tickerSec || 8 : 8) * 1000);
    }, sec * 1000);
  }
  ui.startTicker = startTicker;
  ui.nextTalk = () => { tickI++; return ui.tickTalk(); };

  // ── 머리 띠 캡슐 ─────────────────────────────────────────
  function renderCap(h) {
    const html = '<button type="button" class="nz-capb" data-k="wallet" aria-haspopup="dialog" aria-expanded="' + (POP.key === 'wallet') + '" aria-label="내 MeAI 지갑 : 연속 ' + h.streak.current + '영업일, 응모권 ' + h.wallet.tickets + '장, ' + esc(h.labels.lotto) + ' ' + h.wallet.sets + '세트">' +
      '<span class="seg flame' + (h.streak.todayLit ? '' : ' off') + '" data-a="cap-flame">' + I.flame + h.streak.current + '</span>' +
      '<span class="seg tix" data-a="cap-ticket">' + I.ticket + h.wallet.tickets + '<span class="lb">장</span></span>' +
      '<span class="seg" data-a="cap-lotto">' + NZ.ball(Math.max(1, (h.lotto.sets[h.lotto.sets.length - 1] || { nums: [7] }).nums[0]), 'sm') + h.wallet.sets + '<span class="lb">세트</span></span></button>' +
      '<button type="button" class="nz-dashb" data-k="dash">' + I.dash + '<span>MeAI 대시보드</span></button>';
    if (cap._html !== html) { cap._html = html; NZ.html(cap, html); }
  }

  // ── 버디 말풍선 (시간대별 한 문장 · 닫으면 그날은 끝) ───────────
  let buddyId = null;
  function renderBuddy(h) {
    const b = h.buddy;
    if (!b) { buddy.classList.remove('show'); buddyId = null; return; }
    if (buddyId === b.id + b.text) return;
    buddyId = b.id + b.text;
    NZ.html(buddy, '<img src="' + esc(NZ.mascot(b.mascot)) + '" alt=""><div class="nz-bub"><p>' + esc(b.text) + '</p>' +
      (b.cta ? '<button type="button" class="nz-go" data-go="' + esc(b.cta.go) + '" data-buddy="' + esc(b.id) + '">' + esc(b.cta.label) + I.chev + '</button>' : '') +
      '<button type="button" class="nz-x" data-dismiss="' + esc(b.id) + '" aria-label="말풍선 닫기">' + I.x + '</button></div>');
    buddy.classList.remove('show');
    setTimeout(() => buddy.classList.add('show'), 500);
    NZ.log('buddy', 'show', { id: b.id });
  }

  // ── 추천 고객 카드 배지 ───────────────────────────────────
  function renderReco(h) {
    const r = h.reco, onReco = r.issueOn === 'reco.open';
    const hint = NZ.ball(7, 'sm') + (onReco ? '고객을 열면 <b>' + esc(h.labels.lotto) + ' 1세트</b> 자동 응모' : '추천 고객과 <b>맞춤대화</b>를 하면 ' + esc(h.labels.lotto) + ' 1세트') + ' · 오늘 ' + r.todayIssued + '/' + r.dailyMax;
    if (recHint._html !== hint) { recHint._html = hint; NZ.html(recHint, hint); }
    (host.recoCards() || []).forEach((c) => {
      let b = c.el.querySelector('.nz-recb');
      if (!b) { b = NZ.el('<span class="nz nz-recb"></span>'); host.placeRecoBadge(c.el, b); }
      const st = r.issued[c.id], full = r.todayIssued >= r.dailyMax;
      const html = st && st.lotto ? I.check + '응모 완료' : full ? '오늘 ' + r.dailyMax + '세트 완료' : st && !onReco ? NZ.ball(7, 'sm') + '맞춤대화 하면 +1' : NZ.ball(7, 'sm') + h.labels.lotto.replace('MeAI ', '') + ' +1';
      if (b._html !== html) { b._html = html; NZ.html(b, html); }
      b.classList.toggle('done', !!(st && st.lotto)); b.classList.toggle('full', !st && full);
      NZ.breathe(b, !(st && st.lotto) && !full, true);
    });
  }

  // ── 펼침 카드 : 올리면 0.2초 뒤 열림 · 누르면 고정 · 바깥 · Esc 로 닫힘 ──
  function anchorOf(key) { return key === 'wallet' ? cap.querySelector('.nz-capb') : items[key]; }
  ui.open = (key, mode) => {
    if (key === 'dash') return NZ.dash && NZ.dash.open();
    if (key === 'recap') return ui.go('recap');
    const card = NZ.cards && NZ.cards[key];
    if (!card || !NZ.home) return;
    const a = anchorOf(key);
    if (POP.key && POP.key !== key) closePop(true);
    POP.key = key; POP.mode = mode || 'peek'; POP.anchor = a;
    pop.classList.toggle('wide', !!card.wide);
    pop.classList.toggle('pinned', POP.mode === 'pin');
    pop.setAttribute('aria-label', card.title);
    ui.refreshPop(true);
    place();
    pop.classList.add('on');
    if (NZ.isMobile()) popScrim.classList.add('on');
    Object.keys(items).forEach((k) => items[k].setAttribute('aria-expanded', String(k === key)));
    const cb = cap.querySelector('.nz-capb'); if (cb) cb.setAttribute('aria-expanded', String(key === 'wallet'));
    if (POP.mode === 'pin') setTimeout(() => { const f = pop.querySelector('[data-autofocus]') || pop.querySelector('.nz-card button, .nz-card textarea'); if (f && !NZ.isMobile()) try { f.focus({ preventScroll: true }); } catch (e) { /* 무시 */ } }, 60);
    NZ.log('dock_' + key, POP.mode === 'pin' ? 'open_pin' : 'open_hover');
    if (card.opened) card.opened(pop.querySelector('.nz-card'), NZ.home);
  };
  ui.refreshPop = (force) => {
    const card = NZ.cards[POP.key]; if (!card) return;
    const box = pop.querySelector('.nz-card');
    if (!force && box.querySelector('[data-busy="1"]')) { if (card.update) card.update(box, NZ.home); return; }
    const st = box.querySelector('.nz-cb'), y = st ? st.scrollTop : 0;
    NZ.html(box, '<button type="button" class="nz-pin" data-pin aria-label="' + (POP.mode === 'pin' ? '닫기' : '고정하기') + '">' + (POP.mode === 'pin' ? I.x : I.pin) + '</button>' + card.render(NZ.home));
    if (card.mount) card.mount(box, NZ.home);
    const st2 = box.querySelector('.nz-cb'); if (st2) { st2.scrollTop = y; st2.tabIndex = 0; st2.setAttribute('aria-label', card.title + ' 내용'); }  // 넘치는 내용도 키보드로 내린다
    NZ.vars(box);
  };
  function place() {
    const a = POP.anchor;
    if (!a || NZ.isMobile()) return;
    const r = a.getBoundingClientRect(), w = pop.offsetWidth || 400;
    let left = r.left + scrollX + r.width / 2 - 60;
    left = Math.max(12 + scrollX, Math.min(left, scrollX + document.documentElement.clientWidth - w - 12));
    pop.style.left = left + 'px';
    pop.style.top = (r.bottom + scrollY + 12) + 'px';
    const ax = Math.max(16, Math.min(w - 30, r.left + scrollX + r.width / 2 - left - 7));
    pop.style.setProperty('--ax', ax + 'px'); pop.style.setProperty('--ox', ax + 'px');
  }
  function closePop(silent) {
    if (!POP.key) return;
    const k = POP.key, a = POP.anchor;
    const card = NZ.cards[k]; if (card && card.closed) card.closed();
    POP.key = null; POP.mode = null; pop.classList.remove('on'); popScrim.classList.remove('on');
    Object.keys(items).forEach((x) => items[x].setAttribute('aria-expanded', 'false'));
    const cb = cap.querySelector('.nz-capb'); if (cb) cb.setAttribute('aria-expanded', 'false');
    if (!silent && a && pop.contains(document.activeElement)) try { a.focus({ preventScroll: true }); } catch (e) { /* 무시 */ }
  }
  ui.close = closePop;
  ui.current = () => POP.key;

  function wire() {
    const hoverable = () => G.matchMedia('(hover: hover) and (pointer: fine)').matches && !NZ.isMobile();
    const enter = (key) => { clearTimeout(POP.t); if (!hoverable() || POP.mode === 'pin') return; POP.t = setTimeout(() => { if (POP.key !== key) ui.open(key, 'peek'); }, POP.key ? 60 : 200); };
    const leave = () => { clearTimeout(POP.t); if (POP.mode !== 'peek') return; POP.t = setTimeout(() => { if (POP.mode === 'peek' && !pop.matches(':hover') && !pop.contains(document.activeElement)) closePop(true); }, 260); };
    [dock, cap].forEach((root) => {
      root.addEventListener('pointerover', (e) => { const b = e.target.closest('[data-k]'); if (b && root.contains(b) && b.dataset.k !== 'dash' && b.dataset.k !== 'more' && b.dataset.k !== 'recap') enter(b.dataset.k); });
      root.addEventListener('pointerout', (e) => { const b = e.target.closest('[data-k]'); if (b && !b.contains(e.relatedTarget)) leave(); });
      root.addEventListener('click', (e) => {
        const b = e.target.closest('[data-k]'); if (!b) return;
        const k = b.dataset.k; clearTimeout(POP.t);
        if (k === 'dash') { NZ.log('header_dash', 'click'); return NZ.dash && NZ.dash.open(); }
        if (k === 'recap') return ui.go('recap');
        if (POP.key === k && POP.mode === 'pin') return closePop();
        ui.open(k, 'pin');
      });
    });
    pop.addEventListener('pointerenter', () => clearTimeout(POP.t));
    pop.addEventListener('pointerleave', leave);
    popScrim.addEventListener('click', () => closePop());
    document.addEventListener('pointerdown', (e) => {
      if (!POP.key) return;
      const t = e.target;
      if (pop.contains(t) || dock.contains(t) || cap.contains(t) || (t.closest && t.closest('.nz-layer, .nz-demo'))) return;
      closePop(true);
    }, true);
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && POP.key && !document.querySelector('.nz-scrim')) { closePop(); } });
    G.addEventListener('resize', () => POP.key && place());
    G.addEventListener('scroll', () => POP.key && !NZ.isMobile() && place(), { passive: true });
    // 카드 안 단추들
    document.addEventListener('click', onAct);
  }

  function onAct(e) {
    const t = e.target.closest && e.target.closest('[data-act], [data-go], [data-pin], [data-dismiss], [data-open]');
    if (!t || !(t.closest('.nz'))) return;
    if (t.closest('.nz-scrim') && !t.closest('[data-act]')) return; // 덮개 안 단추는 덮개가 처리
    if (t.hasAttribute('data-pin')) { if (POP.mode === 'pin') closePop(); else { POP.mode = 'pin'; pop.classList.add('pinned'); ui.refreshPop(true); } return; }
    if (t.hasAttribute('data-dismiss')) { buddy.classList.remove('show'); NZ.log('buddy', 'dismiss', { id: t.dataset.dismiss }); NZ.run(NZ.api.dismissBuddy(t.dataset.dismiss), { quiet: true }); return; }
    if (t.hasAttribute('data-open')) { ui.open(t.dataset.open, 'pin'); return; }
    if (t.hasAttribute('data-go')) { if (t.dataset.buddy) NZ.log('buddy', 'cta', { id: t.dataset.buddy }); ui.go(t.dataset.go, t); return; }
    const act = t.dataset.act, card = NZ.cards[POP.key];
    if (NZ.acts[act]) { e.preventDefault(); NZ.acts[act](t, e); return; }
    if (card && card.act) card.act(act, t, e);
  }
  NZ.acts = {};

  // ── 「하러 가기」 : 넛지 → 원래 기능으로 ───────────────────────
  ui.go = (target, from) => {
    NZ.log('go', target);
    const inside = { attend: 1, quiz: 1, talk: 1, quest: 1, lotto: 1, league: 1, journey: 1, wallet: 1, more: 1 };
    if (inside[target]) {
      if (host && host.isHome && !host.isHome()) { host.go('home'); setTimeout(() => ui.go(target, from), 600); return; }
      const d = dock.getBoundingClientRect();
      if (d.top < 60 || d.bottom > innerHeight) { dock.scrollIntoView({ behavior: NZ.reduced() ? 'auto' : 'smooth', block: 'center' }); setTimeout(() => ui.open(target, 'pin'), 450); }
      else ui.open(target, 'pin');
      return;
    }
    if (target === 'dash') return NZ.dash && NZ.dash.open();
    if (target === 'draw') { closePop(true); return NZ.acts['lotto-draw'](); }
    if (target === 'recap') { closePop(true); return NZ.api.getRecap().then((rc) => { NZ.fx.recap(rc); NZ.run(NZ.api.markRecapSeen(rc.week), { quiet: true }); }); }
    closePop(true);
    if (host && host.go) host.go(target);
  };

  // ── 연출이 쓰는 자리 ──────────────────────────────────────
  ui.anchor = (k) => {
    if (k === 'cap-ticket' || k === 'cap-lotto' || k === 'cap-flame') return cap.querySelector('[data-a="' + k + '"]') || items.quest;
    return items[k] || null;
  };
  ui.fxSource = (type) => {
    if (POP.key) {
      const box = pop.querySelector('.nz-card');
      const m = { stamp: '.nz-stamps .s.today, .nz-stamps .s', quiz: '.nz-qres, .nz-ox', talk: '.nz-copy', pass: '.nz-pass' }[type];
      const e = m && box.querySelector(m); if (e) return e;
      return box;
    }
    return items[{ stamp: 'attend', quiz: 'quiz', talk: 'talk', pass: 'league' }[type]] || items.quest;
  };
  ui.bump = (kind) => {
    const e = kind === 'ticket' ? ui.anchor('cap-ticket') : kind === 'lotto' ? ui.anchor('cap-lotto') : items[kind];
    if (!e) return; e.classList.remove('nz-bump'); void e.offsetWidth; e.classList.add('nz-bump');
  };
  ui.ignite = () => {
    const f = items.attend && items.attend.querySelector('.nz-ic'); if (f) { f.classList.remove('off'); ui.bump('attend'); }
    const c = cap.querySelector('.seg.flame'); if (c) { c.classList.remove('off'); c.classList.remove('nz-bump'); void c.offsetWidth; c.classList.add('nz-bump'); }
    const fl = pop.querySelector('.nz-flame'); if (fl) { fl.classList.remove('off'); fl.classList.add('lit'); }
  };
  ui.stampAnim = () => new Promise((res) => {
    const box = POP.key === 'attend' && pop.querySelector('.nz-card');
    const slot = box && box.querySelector('.nz-stamps [data-day="' + NZ.home.today + '"] .s');
    if (!slot) return res();
    let seal = slot.querySelector('.nz-seal');
    if (!seal) { const d = NZ.home.today; seal = NZ.el('<span class="nz-seal">출석<br>' + (+d.slice(5, 7)) + '.' + (+d.slice(8, 10)) + '</span>'); slot.appendChild(seal); }
    seal.classList.remove('slam'); void seal.offsetWidth; seal.classList.add('slam');
    setTimeout(() => { NZ.sfx.stamp(); slot.appendChild(NZ.el('<i class="nz-ink"></i>')); box.classList.remove('nz-shake'); void box.offsetWidth; box.classList.add('nz-shake'); NZ.confettiAt(slot, 36, 7); }, 300);
    setTimeout(res, 700);
  });
})(window);
