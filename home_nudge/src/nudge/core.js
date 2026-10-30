/* MeAI 홈 넛지 v5 · 공통 기반 (도구 · 아이콘 · 소리 · 상태 저장소)
 * 넛지 화면 파일들(core → fx → ui → cards → talks → dash → index)은 window.__NZ 하나를 같이 쓴다.
 * 바깥에 드러나는 것은 index.js 의 window.MeAINudge 뿐이다.
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ = G.__NZ || {};
  NZ.version = '5.0.0';

  // ── DOM 도구 ───────────────────────────────────────────────
  NZ.$ = (s, r) => (r || document).querySelector(s);
  NZ.$$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  NZ.esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  NZ.el = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return NZ.vars(t.content.firstElementChild); };
  // data-v="p:0.4;x:.2" → CSS 변수 --p · --x (HTML 안 style="" 없이 값 넣기 = 엄격한 CSP 에서도 동작)
  NZ.vars = (root) => {
    if (!root) return root;
    const set = (e) => { e.getAttribute('data-v').split(';').forEach((kv) => { const i = kv.indexOf(':'); if (i > 0) e.style.setProperty('--' + kv.slice(0, i).trim(), kv.slice(i + 1).trim()); }); };
    if (root.hasAttribute && root.hasAttribute('data-v')) set(root);
    root.querySelectorAll && root.querySelectorAll('[data-v]').forEach(set);
    return root;
  };
  NZ.html = (node, html) => { node.innerHTML = html; NZ.vars(node); return node; };
  NZ.wait = (ms) => new Promise((r) => setTimeout(r, ms));
  NZ.rect = (e) => e && e.getBoundingClientRect ? e.getBoundingClientRect() : null;
  NZ.isMobile = () => G.matchMedia('(max-width: 760px)').matches;
  NZ.reduced = () => G.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── 숫자 · 시간 ────────────────────────────────────────────
  const DOW = ['일', '월', '화', '수', '목', '금', '토'];
  NZ.fmt = {
    n: (x) => Number(x || 0).toLocaleString('ko-KR'),
    pct: (p, d) => (p * 100).toFixed(d == null ? 1 : d) + '%',
    md: (ymd) => { const p = ymd.split('-'); const dt = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])); return (+p[1]) + '/' + (+p[2]) + '(' + DOW[dt.getUTCDay()] + ')'; },
    dow: (i) => DOW[i],
    hm: (ms) => { const d = new Date(ms + 9 * 3600e3); return String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0'); },
    left: (ms) => {
      if (ms <= 0) return '지금';
      const m = Math.floor(ms / 60000), d = Math.floor(m / 1440), h = Math.floor((m % 1440) / 60), mi = m % 60;
      return d ? d + '일 ' + h + '시간' : h ? h + '시간 ' + mi + '분' : mi + '분';
    },
    clock: (ms) => { const s = Math.max(0, Math.floor(ms / 1000)); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = s % 60; return (h ? h + ':' : '') + String(m).padStart(2, '0') + ':' + String(x).padStart(2, '0'); }
  };
  NZ.ballCls = (n) => n <= 10 ? '' : n <= 20 ? ' b2' : n <= 30 ? ' b3' : n <= 40 ? ' b4' : ' b5';
  NZ.ball = (n, extra) => '<span class="ball' + NZ.ballCls(n) + (extra ? ' ' + extra : '') + '">' + n + '</span>';

  // ── 그림 · 걱정인형 ────────────────────────────────────────
  // 목업(한 파일)은 window.NZ_ASSETS 에 data: 주소가 들어 있고, 사내 서버판은 assetBase + 파일 이름을 쓴다.
  NZ.assetBase = '';
  NZ.tarotBase = null; // 타로 그림 자리가 따로 있으면(예 : 저장소의 fortune/assets/tarot/) mount({ tarotBase }) 로 준다
  NZ.asset = (name) => (G.NZ_ASSETS && G.NZ_ASSETS[name]) || (NZ.tarotBase && name.indexOf('tarot/') === 0 ? NZ.tarotBase + name.slice(6) : NZ.assetBase + name);
  NZ.mascot = (id) => NZ.asset('mascots/' + id + '.webp');

  const P = (d, extra) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' + (extra || '') + '>' + d + '</svg>';
  NZ.I = {
    flame: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12.6 2.3c.4 2.9-1 4.6-2.4 6.2C8.7 10.2 7 12 7 15.1A5 5 0 0 0 12 20a5 5 0 0 0 5-4.9c0-1.8-.7-3-1.5-4.1-.2 1.2-.8 2.1-1.8 2.6.3-3.6-.8-7.3-1.1-11.3z"/><path fill="#fff" opacity=".55" d="M12.2 12.6c-1 1-1.9 1.9-1.9 3.3a1.8 1.8 0 0 0 3.6.1c0-1.1-.6-1.9-1.7-3.4z"/></svg>',
    ticket: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 6.5A1.5 1.5 0 0 1 5.5 5h13A1.5 1.5 0 0 1 20 6.5V9a2.5 2.5 0 0 0 0 5v2.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 16.5V14a2.5 2.5 0 0 0 0-5z"/><path stroke="#fff" stroke-width="1.6" stroke-dasharray="1.6 1.8" d="M14.5 6.5v11"/><path fill="#fff" d="M8.4 9.3c.4-.9 2-.9 2 .4 0 1.6-2 1.9-2 3.1h2"/></svg>',
    quiz: P('<circle cx="12" cy="12" r="9"/><path d="M9.3 9.3a2.8 2.8 0 1 1 4.1 2.5c-.9.5-1.4 1-1.4 2M12 17.2v.1"/>'),
    quote: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 11.5C5 8.4 6.8 6.3 9.6 5.6l.5 1.5C8.6 7.7 7.8 8.8 7.7 10H10v6H5zm8.6 0c0-3.1 1.8-5.2 4.6-5.9l.5 1.5c-1.5.6-2.3 1.7-2.4 2.9h2.3v6h-5z"/></svg>',
    trophy: P('<path d="M8 4h8v5a4 4 0 0 1-8 0zM8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8.5 20h7M10 17h4"/>'),
    lotto: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="currentColor" opacity=".18"/><circle cx="12" cy="12" r="6.2" fill="currentColor"/><circle cx="10" cy="9.6" r="1.8" fill="#fff" opacity=".7"/></svg>',
    ring: P('<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/>'),
    check: P('<path d="M5 12.5l4.2 4.2L19 7"/>', ' stroke-width="3"'),
    x: P('<path d="M6 6l12 12M18 6L6 18"/>'),
    arrow: P('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    chev: P('<path d="M9 6l6 6-6 6"/>'),
    gear: P('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z"/>'),
    dots: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="2" fill="currentColor"/><circle cx="12" cy="12" r="2" fill="currentColor"/><circle cx="19" cy="12" r="2" fill="currentColor"/></svg>',
    pin: P('<path d="M9 4h6l-1 6 3 3H7l3-3zM12 13v7"/>'),
    heart: P('<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>'),
    heartF: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>',
    bookmark: P('<path d="M7 4h10v16l-5-3.5L7 20z"/>'),
    hand: P('<path d="M8 13V6.5a1.5 1.5 0 0 1 3 0V12M11 11V5a1.5 1.5 0 0 1 3 0v6M14 11V6.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-.5A5.5 5.5 0 0 1 6 17.4L4.3 14a1.5 1.5 0 0 1 2.6-1.5L8 14"/>'),
    clap: P('<path d="M7.5 12.5l4-4a1.4 1.4 0 0 1 2 2l-1 1M10 15l5.5-5.5a1.4 1.4 0 0 1 2 2L12 17a6 6 0 0 1-8.5 0 1.9 1.9 0 0 1 0-2.6L7 11a1.4 1.4 0 0 1 2 2M15 3.5V2M18.5 5l1-1M20 8.5h1.5"/>'),
    shield: P('<path d="M12 3l7 3v5c0 4.6-3 8.3-7 10-4-1.7-7-5.4-7-10V6z"/><path d="M9 12l2 2 4-4"/>'),
    spark: P('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>'),
    chart: P('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
    gift: P('<path d="M4 11h16v9H4zM3 7h18v4H3zM12 7v13M12 7c-2-3-5.5-3-5.5-.8C6.5 7 9 7 12 7zm0 0c2-3 5.5-3 5.5-.8C17.5 7 15 7 12 7z"/>'),
    lock: P('<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>'),
    cal: P('<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4M16 3v4M3 10h18"/>'),
    users: P('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6 6 0 0 1 3.5 6"/>'),
    send: P('<path d="M4 12l16-8-6 16-2.5-6.5z"/>'),
    sound: P('<path d="M4 9h4l5-4v14l-5-4H4zM16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/>'),
    mute: P('<path d="M4 9h4l5-4v14l-5-4H4zM17 9l5 5M22 9l-5 5"/>'),
    info: P('<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.1"/>'),
    star: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3l2.7 5.6 6.1.8-4.5 4.2 1.1 6-5.4-2.9-5.4 2.9 1.1-6L3.2 9.4l6.1-.8z"/></svg>',
    medal: P('<circle cx="12" cy="14" r="6"/><path d="M8.5 9L6 3h4l2 4 2-4h4l-2.5 6M12 11.5v5M10.5 13l1.5-1.5"/>'),
    moon: P('<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>'),
    copy: P('<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>'),
    route: P('<circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="5" r="2.5"/><path d="M8.5 19H16a3 3 0 0 0 0-6H8a3 3 0 0 1 0-6h7.5"/>'),
    play: P('<path d="M7 5l12 7-12 7z"/>'),
    search: P('<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>'),
    refresh: P('<path d="M20 11a8 8 0 0 0-14.7-4.3L4 8M4 4v4h4M4 13a8 8 0 0 0 14.7 4.3L20 16M20 20v-4h-4"/>'),
    dash: P('<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>'),
    wand: P('<path d="M15 4V2M15 10V8M11 6h2M17 6h2M4 20l9-9M12 12l1-1"/>'),
    // 행운 존
    clover: '<svg viewBox="0 0 24 24" aria-hidden="true"><g fill="currentColor"><circle cx="8.6" cy="8.4" r="3.7"/><circle cx="15.4" cy="8.4" r="3.7"/><circle cx="8.6" cy="15.2" r="3.7"/><circle cx="15.4" cy="15.2" r="3.7"/></g><path d="M13.4 13.4l5.6 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="11.8" r="1.7" fill="#fff" opacity=".75"/></svg>',
    wheel: P('<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4"/><circle cx="12" cy="12" r="2.2" fill="currentColor"/>'),
    slot: P('<rect x="2.5" y="5" width="15.5" height="14" rx="2.5"/><path d="M7.7 5v14M12.9 5v14"/><path d="M21 9.5v5"/><circle cx="21" cy="7.5" r="1.6"/>'),
    ox: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="6.8" cy="12" r="4.3"/><path d="M14 7.6l7.6 8.8M21.6 7.6L14 16.4"/></svg>',
    cards: P('<rect x="8.5" y="3" width="11" height="16" rx="2" transform="rotate(12 14 11)"/><rect x="4" y="5" width="11" height="16" rx="2" fill="currentColor" fill-opacity=".12"/><path d="M9.5 9.6l1 2 2.2.3-1.6 1.5.4 2.2-2-1.1-2 1.1.4-2.2-1.6-1.5 2.2-.3z"/>'),
    scratch: P('<rect x="2.5" y="6" width="19" height="12" rx="2.5"/><path d="M6.5 13c1.4-2.2 2.9-2.2 4.3 0s2.9 2.2 4.3 0 2.2-1.6 2.9-1.2"/><path d="M17 3.5l2.5 2.5"/>'),
    grid: P('<rect x="3.5" y="3.5" width="17" height="17" rx="2.5"/><path d="M9.2 3.5v17M14.8 3.5v17M3.5 9.2h17M3.5 14.8h17"/>'),
    cake: P('<path d="M4 20h16M5 20v-6.5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2V20"/><path d="M5 15.6c1.4 1 2.8 1 4.2 0 1.4 1 2.8 1 4.2 0 1.4 1 2.8 1 4.2 0"/><path d="M12 11.5V8"/><path d="M12 3.8c1 1.1 1 2.2 0 2.9-1-.7-1-1.8 0-2.9z" fill="currentColor"/>'),
    clock: P('<circle cx="12" cy="13" r="8"/><path d="M12 9v4.2l2.8 1.8"/><path d="M4.8 4.8l2 1.5M19.2 4.8l-2 1.5"/>'),
    mail: P('<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3.6 7.2l8.4 6 8.4-6"/>'),
    bolt: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.4 2.5L4.8 13.6h6l-1.2 7.9 8.6-11.1h-6z"/></svg>'
  };

  // ── 소리 (파일 없이 Web Audio 로 합성 · 기본 꺼짐) ──────────
  let AC = null;
  function tone(f, t0, dur, type, vol) {
    try {
      AC = AC || new (G.AudioContext || G.webkitAudioContext)();
      const o = AC.createOscillator(), g = AC.createGain(), t = AC.currentTime + t0;
      o.type = type || 'sine'; o.frequency.setValueAtTime(f, t);
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol || 0.08, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      o.connect(g); g.connect(AC.destination); o.start(t); o.stop(t + dur + 0.02);
    } catch (e) { /* 소리를 못 내는 환경은 조용히 넘어간다 */ }
  }
  NZ.sfx = {
    on: () => !!(NZ.home && NZ.home.settings && NZ.home.settings.sound),
    tick() { if (this.on()) tone(1400, 0, 0.03, 'square', 0.02); },
    ding() { if (this.on()) { tone(1318, 0, 0.18, 'triangle', 0.07); tone(1976, 0.04, 0.22, 'sine', 0.04); } },
    stamp() { if (this.on()) { tone(120, 0, 0.12, 'square', 0.12); tone(80, 0.02, 0.2, 'sine', 0.12); } },
    pop() { if (this.on()) tone(880, 0, 0.08, 'sine', 0.06); },
    win() { if (this.on()) [523, 659, 784, 1046].forEach((f, i) => tone(f, i * 0.09, 0.28, 'triangle', 0.07)); },
    clear() { if (this.on()) [784, 988, 1318].forEach((f, i) => tone(f, i * 0.07, 0.24, 'triangle', 0.06)); }
  };

  // ── 화면 읽기 프로그램 안내 ────────────────────────────────
  let live = null;
  NZ.say = (text) => {
    if (!live) { live = NZ.el('<div class="nz nz-sr" aria-live="polite" role="status"></div>'); document.body.appendChild(live); }
    live.textContent = ''; setTimeout(() => { live.textContent = text.replace(/<[^>]+>/g, ''); }, 30);
  };

  // ── 숨쉬는 유도 : 같은 박자로 (Web Animations, 시작점 0 에 맞춤) ──
  NZ.breathe = (el, on, gold) => {
    if (!el) return;
    let halo = el.querySelector(':scope > .nz-halo');
    if (!on) { if (halo) { halo.getAnimations && halo.getAnimations().forEach((a) => a.cancel()); halo.remove(); } el.classList.remove('nz-todo', 'gold'); return; }
    el.classList.add('nz-todo'); el.classList.toggle('gold', !!gold);
    if (halo) return;
    halo = document.createElement('i'); halo.className = 'nz-halo'; halo.setAttribute('aria-hidden', 'true'); el.appendChild(halo);
    if (NZ.reduced() || !halo.animate) return;
    const a = halo.animate([{ opacity: 0 }, { opacity: 1 }, { opacity: 0 }], { duration: 3200, iterations: Infinity, easing: 'ease-in-out' });
    try { a.startTime = 0; } catch (e) { /* 구형 브라우저 : 박자만 어긋난다 */ }
  };

  // ── 상태 저장소 ────────────────────────────────────────────
  // 화면은 서버가 준 요약(home) 하나만 보고 그린다. 행동 → 서버 → 새 요약 + 연출 목록(fx).
  const subs = [];
  NZ.home = null;
  NZ.onChange = (fn) => subs.push(fn);
  NZ.setHome = (h) => { NZ.home = h; NZ.homeAt = Date.now(); subs.forEach((fn) => { try { fn(h); } catch (e) { console.error('[넛지]', e); } }); };
  NZ.load = async () => { NZ.setHome(await NZ.api.getHome()); return NZ.home; };
  const REASON = {
    already: '오늘은 이미 했어요', not_bizday: '오늘은 쉬는 날이에요. 연속 기록은 그대로 이어져요', limit: '오늘 응원은 모두 보냈어요',
    lotto_daily_max: '오늘 받을 수 있는 세트(5세트)를 모두 받았어요', not_done: '조금만 더 맞게 써 보세요', no_quiz: '오늘의 퀴즈가 아직 열리지 않았어요',
    no_plays: '오늘 기회를 모두 썼어요. 일일 미션 · 올클리어를 하면 한 번 더 생겨요', no_customers: '지금 고를 고객이 부족해요. 내일 다시 해 보세요',
    no_target: '이 고객은 오늘 룰렛 · 슬롯 결과에 없어요', expired: '받은 지 7일이 지나 쓸 수 없는 복권이에요', no_scratch: '복권을 찾지 못했어요'
  };
  // 행동 하나 : 서버 응답을 받아 화면 · 연출 · 사용 기록까지 한 번에
  NZ.run = async (promise, ctx) => {
    const r = await NZ.ask(promise);
    return r ? NZ.settle(r, ctx) : null;
  };
  // 응답만 먼저 받기 (게임처럼 연출이 끝난 뒤에 반영할 때) → 나중에 NZ.settle(r)
  NZ.ask = async (promise) => {
    try { return await promise; } catch (e) { NZ.toast('지금은 연결이 원활하지 않아요. 잠시 뒤 다시 해 주세요'); console.error('[넛지]', e); return null; }
  };
  NZ.settle = (r, ctx) => {
    if (r.home) NZ.setHome(r.home);
    if (!r.ok && r.reason && REASON[r.reason] && !(ctx && ctx.quiet)) NZ.toast(REASON[r.reason]);
    if ((r.fx && r.fx.length) || (r.grants && r.grants.length)) NZ.fx.play(r.fx || [], r.grants || [], ctx || {});
    return r;
  };
  // 이 기기에만 두는 값(예 : 내 생년월일). 사생활 보호 모드 등으로 막혀 있으면 조용히 없는 것으로 본다.
  NZ.local = {
    get(k) { try { return G.localStorage.getItem('meai.nudge.' + k); } catch (e) { return null; } },
    set(k, v) { try { if (v == null) G.localStorage.removeItem('meai.nudge.' + k); else G.localStorage.setItem('meai.nudge.' + k, v); return true; } catch (e) { return false; } }
  };

  // ── 사용 기록(대시보드 원천) : 화면에서 일어난 일을 모아 한꺼번에 보낸다 ──
  const Q = [];
  NZ.log = (el, action, meta) => {
    const e = { ts: Date.now(), el: el, action: action, meta: meta || {}, v: NZ.version };
    Q.push(e); NZ.logs.push(e); if (NZ.logs.length > 400) NZ.logs.shift();
    if (Q.length >= 20) NZ.flushLog();
  };
  NZ.logs = [];
  NZ.flushLog = () => { if (!Q.length || !NZ.api || !NZ.api.log) return; const b = Q.splice(0, Q.length); try { NZ.api.log(b); } catch (e) { /* 기록 실패는 화면에 영향 없음 */ } };
  G.addEventListener('pagehide', () => NZ.flushLog());
  setInterval(() => NZ.flushLog(), 15000);
})(window);
