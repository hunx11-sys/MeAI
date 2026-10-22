/* MeAI 사이트 셸 — 규칙 design/DESIGN-MeAI.md 「11. 사이트 셸 · 움직임」
   이 파일이 원본이다. 화면에는 python3 scripts/apply_ui.py 가 script#meai-site 로 본문 끝에 끼워 넣는다.
   하는 일 : 머리 띠(현재 도구 알약 · 마우스 따라 미끄러지는 알약 · 스크롤 그림자 · 긴 화면 진행 막대) · 휴대폰 메뉴 시트 ·
            스크롤해 보일 때 올라오는 카드. 자료(DATA) · 검색 · 계산에는 손대지 않는다.
   다른 화면 안(iframe)에 든 보상시뮬레이터처럼 이미 머리 띠가 있는 화면 안에서는 머리 띠를 지우고 움직임만 쓴다.
   ES5 로 쓴다(구형 브라우저에서 문법 오류로 화면 전체가 멈추지 않게). */
(function () {
  'use strict';
  var d = document, h = d.documentElement, w = window;
  if (w.__meaiSite) return; w.__meaiSite = 1;
  h.classList.add('mu-js');
  var reduce = false;
  try { reduce = w.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  function $(id) { return d.getElementById(id); }
  function drop(el) { if (el && el.parentNode) el.parentNode.removeChild(el); }
  function each(list, fn) { for (var i = 0; i < list.length; i++) fn(list[i], i); }

  /* ── 1) 다른 MeAI 화면 안에 들어 있으면 머리 띠를 쓰지 않는다 ── */
  var framed = false;
  try { framed = w.self !== w.top; } catch (e) { framed = true; }
  var embedded = false;
  if (framed) {
    if (h.getAttribute('data-tool') === 'eco') embedded = true;          // 특약검색기 안의 보상시뮬레이터
    try { if (w.parent.document.getElementById('mu-nav')) embedded = true; } catch (e) {}
  }
  var nav = $('mu-nav'), sheet = $('mu-sheet');
  if (embedded) { drop(nav); drop(sheet); drop($('mu-amb')); nav = sheet = null; h.classList.add('mu-embed'); }

  /* ── 2) 머리 띠 ── */
  if (nav) {
    var links = nav.querySelector('.mu-links'), pill = nav.querySelector('.mu-pill');
    var curLabel = nav.querySelector('.mu-cur');
    var page = nav.getAttribute('data-page') || '';
    var hot = null;

    var current = function () { return links ? links.querySelector('.mu-l[aria-current="page"]') : null; };
    var place = function (a, still) {
      if (!pill || !links) return;
      if (!a || !a.offsetWidth) { links.classList.remove('mu-pill-on'); return; }
      if (still) pill.classList.add('mu-still');
      pill.className = pill.className.replace(/\bmu-(home|merry|eco|rara|indi|tata|zizi)\b/g, '').replace(/\s+/g, ' ');
      pill.classList.add('mu-' + a.getAttribute('data-k'));
      pill.style.setProperty('--pill-x', a.offsetLeft + 'px');
      pill.style.setProperty('--pill-w', a.offsetWidth + 'px');
      links.classList.add('mu-pill-on');
      if (still) { void pill.offsetWidth; pill.classList.remove('mu-still'); }
    };
    var rest = function (still) {
      if (hot) { hot.classList.remove('mu-hot'); hot = null; }
      place(current(), still);
    };

    /* 특약검색기 ↔ 보상시뮬레이터 : 같은 화면 안의 탭이라 body.sim-on 을 보고 현재 표시를 바꾼다 */
    var setCurrent = function (k) {
      var all = d.querySelectorAll('#mu-nav .mu-l, #mu-sheet .mu-si');
      each(all, function (a) {
        if (a.getAttribute('data-k') === k) a.setAttribute('aria-current', 'page');
        else a.removeAttribute('aria-current');
      });
      if (curLabel) {
        var src = nav.querySelector('.mu-l[data-k="' + k + '"]');
        curLabel.className = 'mu-cur mu-' + k;
        curLabel.innerHTML = src ? '<i></i>' + src.textContent.replace(/^\s+|\s+$/g, '') : '';
      }
      rest(false);
    };
    if (page === 'merry' && d.body) {
      var simOn = null;
      var syncSim = function () {
        var on = d.body.classList.contains('sim-on');
        if (on !== simOn) { simOn = on; setCurrent(on ? 'eco' : 'merry'); }
      };
      if (w.MutationObserver) new MutationObserver(syncSim).observe(d.body, { attributes: true, attributeFilter: ['class'] });
      syncSim();
    }

    if (links) {
      each(links.querySelectorAll('.mu-l'), function (a) {
        var on = function () {
          if (hot && hot !== a) hot.classList.remove('mu-hot');
          hot = a; a.classList.add('mu-hot'); place(a, false);
        };
        a.addEventListener('mouseenter', on);
        a.addEventListener('focus', on);
      });
      links.addEventListener('mouseleave', function () { rest(false); });
      links.addEventListener('focusout', function (e) { if (!links.contains(e.relatedTarget)) rest(false); });
      rest(true);
      try { if (d.fonts && d.fonts.ready) d.fonts.ready.then(function () { rest(true); }); } catch (e) {}
      if (w.ResizeObserver) new ResizeObserver(function () { rest(true); }).observe(links);
      else w.addEventListener('resize', function () { rest(true); });
    }

    /* 스크롤 그림자 : 맨 위 1px 표지가 화면 밖으로 나가면 html.mu-scrolled */
    var top = d.createElement('div');
    top.id = 'mu-top'; top.setAttribute('aria-hidden', 'true');
    top.style.cssText = 'position:absolute;left:0;top:0;width:1px;height:1px;pointer-events:none;visibility:hidden';
    d.body.insertBefore(top, d.body.firstChild);
    if (w.IntersectionObserver) {
      new IntersectionObserver(function (es) {
        h.classList.toggle('mu-scrolled', !es[es.length - 1].isIntersecting);
      }).observe(top);
    }

    /* 진행 막대는 화면 높이의 2.5배가 넘는 긴 화면에서만 */
    var longChk = function () { h.classList.toggle('mu-long', h.scrollHeight > w.innerHeight * 2.5); };
    longChk();
    if (w.ResizeObserver) new ResizeObserver(longChk).observe(d.body);
    w.addEventListener('resize', longChk);
  }

  /* ── 3) 휴대폰 메뉴 시트 ── */
  if (nav && sheet) {
    var btn = nav.querySelector('.mu-menu'), lastFocus = null;
    var isOpen = function () { return sheet.classList.contains('mu-open'); };
    var open = function () {
      lastFocus = d.activeElement;
      sheet.classList.add('mu-open'); sheet.removeAttribute('aria-hidden');
      if (btn) btn.setAttribute('aria-expanded', 'true');
      var first = sheet.querySelector('.mu-si[aria-current="page"]') || sheet.querySelector('.mu-si');
      setTimeout(function () { try { first && first.focus({ preventScroll: true }); } catch (e) {} }, 60);
    };
    var close = function (keepFocus) {
      if (!isOpen()) return;
      sheet.classList.remove('mu-open'); sheet.setAttribute('aria-hidden', 'true');
      if (btn) btn.setAttribute('aria-expanded', 'false');
      if (!keepFocus && lastFocus && lastFocus.focus) { try { lastFocus.focus({ preventScroll: true }); } catch (e) {} }
    };
    if (btn) btn.addEventListener('click', function () { if (isOpen()) close(); else open(); });
    sheet.addEventListener('click', function (e) {
      var t = e.target;
      if (t.closest && (t.closest('.mu-scrim') || t.closest('.mu-x'))) close();
    });
    /* 링크를 누르면 닫는다. 올인원 판은 문서(document) 단계에서 링크를 가로채므로 그보다 앞선 창(window) 단계에서 닫는다 */
    w.addEventListener('click', function (e) {
      var a = e.target && e.target.closest && e.target.closest('#mu-sheet a[href]');
      if (a) close(true);
    }, true);
    d.addEventListener('keydown', function (e) {
      if (!isOpen()) return;
      if (e.key === 'Escape' || e.key === 'Esc') { e.preventDefault(); close(); return; }
      if (e.key === 'Tab') {                              /* 시트 안에서만 초점이 돈다 */
        var f = sheet.querySelectorAll('a[href],button');
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    w.addEventListener('resize', function () { if (w.innerWidth > 760) close(true); });
    w.addEventListener('pageshow', function () { close(true); });
  }

  /* ── 4) 스크롤해 보일 때 올라오기 ──
     처음 화면에 보이는 것은 건드리지 않는다(빈 화면이 생기지 않게). 화면 아래에 있는 카드만 숨겼다가 보일 때 올린다.
     인쇄할 때와 움직임 줄이기 설정에서는 하지 않는다. */
  /* 대문 같은 꾸밈 구역에 [data-reveal] 을 붙인 것만 — 도구 화면의 목록 · 결과 · 상품 카드는 절대 숨기지 않는다
     (빠르게 넘길 때 빈 카드가 번쩍이고, 카드마다 움직임이 겹쳐 스크롤이 끊기던 원인) */
  var REVEAL = '[data-reveal]';
  var SKIP = '#mu-nav, #mu-sheet, .ov, #hov, #mapov, #oncoov, #scov, .modal-overlay, #ex-mask, .sheet, .dim, [role="dialog"], .sim-pick-wrap, .cmpbar';
  function reveal() {
    if (reduce || !w.IntersectionObserver) return;
    var vh = w.innerHeight || h.clientHeight, list = [];
    each(d.querySelectorAll(REVEAL), function (el) {
      if (el.closest(SKIP)) return;
      var p = el.parentNode && el.parentNode.closest ? el.parentNode.closest(REVEAL) : null;
      if (p) return;                                      /* 바깥 카드만 움직인다 */
      var r = el.getBoundingClientRect();
      if (!r.height || r.top < vh + 8) return;            /* 첫 화면 · 이미 지나간 것은 그대로 */
      list.push(el);
    });
    if (!list.length) return;
    var io = new IntersectionObserver(function (es) {
      var batch = [];
      each(es, function (en) { if (en.isIntersecting) { batch.push(en.target); io.unobserve(en.target); } });
      batch.sort(function (a, b) {
        var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        return (ra.top - rb.top) || (ra.left - rb.left);
      });
      each(batch, function (el, i) {
        el.style.setProperty('--mu-d', Math.min(i, 5) * 70 + 'ms');
        el.classList.add('mu-in');
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.01 });
    each(list, function (el) {
      el.classList.add('mu-rv');
      el.addEventListener('animationend', function done(e) {
        if (e.target !== el) return;
        el.classList.remove('mu-rv', 'mu-in'); el.style.removeProperty('--mu-d');
        el.removeEventListener('animationend', done);
      });
      io.observe(el);
    });
    var showAll = function () { each(list, function (el) { el.classList.remove('mu-rv', 'mu-in'); }); };
    w.addEventListener('beforeprint', showAll);
  }

  /* ── 5) 다듬기 : 미끄러지는 탭 표시 · 결과 차례로 나타나기 · 접기 높이 · 모달 초점 돌려주기 ──
     화면별로 「어디에」만 아래 표에 적는다. 화면 코드(검색 · 계산)는 그대로 두고, 바뀐 결과(class · 자식 요소)를 보고 따라 움직인다. */
  var tool = h.getAttribute('data-tool') || '';
  var SPRING = 'cubic-bezier(.16,1,.3,1)';
  var raf = w.requestAnimationFrame ? function (f) { return w.requestAnimationFrame(f); } : function (f) { return setTimeout(f, 16); };
  var MO = w.MutationObserver;
  function kids(box, sel) {
    var out = [], c = box.children;
    for (var i = 0; i < c.length; i++) if (c[i].className !== 'mu-ind' && c[i].matches && c[i].matches(sel)) out.push(c[i]);
    return out;
  }

  /* 5-1) 미끄러지는 탭 · 세그먼트 표시 : root(늘 있는 요소) 안의 box 에서 .on 인 칸으로 표시가 미끄러진다.
          carry : 화면이 box 를 통째로 다시 그리는 곳(통합치료비 시트) — 같은 자리에 다시 생기면 앞 자리에서 이어 미끄러진다 */
  var SLIDE = {
    merry: [{ root: '#modal', box: '.tabs', item: 'button' }, { root: '#seg', item: 'button' }],
    rara: [{ root: '.tabs', item: '.tab', mode: 'line', inset: function () { return w.matchMedia && w.matchMedia('(max-width:640px)').matches ? 8 : 0; } },
           { root: '#ex-rule', box: '.seg', item: 'button' }, { root: '#ex-ptabs', item: 'button' }],
    zizi: [{ root: '#shB', box: '.seg', item: 'button', carry: 1 }],
    home: [{ root: '#period', item: 'button' }, { root: '#gran', item: 'button' }, { root: '#dzmode', item: 'button' }],
    tata: [{ root: '.seg', all: 1, item: 'button' }]
  };
  var MEM = {};
  function slidePut(st, p, still) {
    var ind = st.ind;
    if (still) ind.classList.add('mu-still');
    ind.style.transform = 'translate3d(' + p.x + 'px,' + p.y + 'px,0)';
    ind.style.width = p.w + 'px'; ind.style.height = p.h + 'px'; ind.style.opacity = '1';
    if (still) { void ind.offsetWidth; ind.classList.remove('mu-still'); }
  }
  function slideSync(box, cfg, key, root) {
    var items = kids(box, cfg.item);
    if (!items.length) return;
    var on = null;
    for (var i = 0; i < items.length; i++) if (items[i].classList.contains('on')) { on = items[i]; break; }
    var st = box.__muSl, fresh = false;
    if (!st) {
      if (!box.offsetWidth) return;                 /* 아직 안 보이면 다음 기회에 */
      var ind = d.createElement('span');
      ind.className = 'mu-ind'; ind.setAttribute('aria-hidden', 'true');
      if (cfg.mode !== 'line' && on) {              /* 선택된 칸의 바탕 · 그림자 · 모서리를 그대로 옮겨 입힌다 */
        var cs = w.getComputedStyle(on);
        ind.style.backgroundColor = cs.backgroundColor; ind.style.boxShadow = cs.boxShadow; ind.style.borderRadius = cs.borderRadius;
      }
      box.appendChild(ind);                          /* 맨 뒤에 둔다 — :first-child · nth-child 규칙과 화면 코드가 그대로 듣게 */
      box.classList.add('mu-sl', cfg.mode === 'line' ? 'mu-sl-line' : 'mu-sl-pill');
      st = box.__muSl = { ind: ind };
      fresh = true;
      if (w.ResizeObserver) new ResizeObserver(function () { slideSync(box, cfg, key, root); }).observe(box);
    }
    if (!on || !on.offsetWidth) { st.ind.style.opacity = '0'; return; }
    var p = { x: on.offsetLeft, y: on.offsetTop, w: on.offsetWidth, h: on.offsetHeight };
    if (cfg.mode === 'line') { var k = cfg.inset ? cfg.inset() : 0; p.x += k; p.w -= 2 * k; p.y = on.offsetTop + on.offsetHeight - 1; p.h = 2; }
    if (st.p && st.p.x === p.x && st.p.y === p.y && st.p.w === p.w && st.p.h === p.h) return;
    var r = box.getBoundingClientRect(), m = MEM[key];
    if (root && root !== box) { var rr = root.getBoundingClientRect(); r = { left: r.left - rr.left, top: r.top - rr.top }; }   /* 시트가 움직여도 그 안 자리로 비교 */
    if (fresh && cfg.carry && m && (Date.now() - m.t) < 1500 && Math.abs(r.left - m.bx) < 3 && Math.abs(r.top - m.by) < 3 && m.p) {
      slidePut(st, m.p, true); fresh = false;       /* 다시 그려진 box : 앞 자리에서 출발 */
    }
    slidePut(st, p, fresh);
    st.p = p; MEM[key] = { p: p, bx: r.left, by: r.top, t: Date.now() };
  }
  function slideScan() {
    var list = SLIDE[tool]; if (!list) return;
    each(list, function (cfg, n) {
      var roots = cfg.all ? d.querySelectorAll(cfg.root) : [d.querySelector(cfg.root)];
      each(roots, function (root, j) {
        if (!root) return;
        var key = tool + n + '-' + j;
        var run = function () {
          if (cfg.box) each(root.querySelectorAll(cfg.box), function (b) { slideSync(b, cfg, key, root); });
          else slideSync(root, cfg, key, root);
        };
        if (!root.__muSlObs && MO) {
          root.__muSlObs = 1;
          var pend = false;
          new MO(function () { if (!pend) { pend = true; raf(function () { pend = false; run(); }); } })
            .observe(root, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
        }
        run();
      });
    });
  }

  /* 5-2) 검색 · 필터 바로 뒤 화면에 보이는 앞 8장만 160ms 옅게 나타난다(이동 없음). 스크롤과는 무관(목록을 다시 그릴 때만),
          연달아 다시 그리면(타자 중) 건너뛴다 */
  var STAGGER = {
    merry: [{ root: '#results', item: '.cards>.card, .empty' }],
    eco: [{ root: '#timeline', item: '.stage, .no-result' }],
    rara: [{ root: '#list', item: '.p, .empty' }, { root: '#viewDuty', item: '.dcard' }],
    indi: [{ root: '#grid', item: '.card, .empty' }]
  };
  function stagger(root, cfg) {
    var now = Date.now(), quick = now - (root.__muLast || 0) < 450;
    root.__muLast = now;
    if (reduce || quick || h.classList.contains('mu-enter') || d.hidden) return;
    var list = root.querySelectorAll(cfg.item), vh = w.innerHeight || h.clientHeight, n = 0;
    for (var i = 0; i < list.length && n < 8; i++) {
      var el = list[i];
      if (el.classList.contains('mu-rv')) continue;
      var r = el.getBoundingClientRect();
      if (!r.height || r.bottom < 0) continue;
      if (r.top > vh) break;
      el.classList.add('mu-st');
      el.addEventListener('animationend', function fin(e) {
        if (e.target !== this) return;
        this.classList.remove('mu-st');
        this.removeEventListener('animationend', fin);
      });
      n++;
    }
  }
  function staggerInit() {
    var list = STAGGER[tool]; if (!list || !MO) return;
    each(list, function (cfg) {
      var root = d.querySelector(cfg.root);
      if (!root || root.__muSt) return;
      root.__muSt = 1; root.__muLast = 0;
      new MO(function (recs) {
        for (var i = 0; i < recs.length; i++) if (recs[i].addedNodes.length) { stagger(root, cfg); return; }
      }).observe(root, { childList: true });
    });
  }

  /* 5-3) 접기 · 펴기 높이 : 화면 코드는 class(open)만 바꾸고, 여기서 높이를 부드럽게 잇는다(Web Animations) */
  var EXPAND = {
    merry: [{ root: '#modal', el: '.foot', body: '.foot-body', mode: 'foot' }, { root: '#modal', el: '.exp', body: '.exbody', mode: 'clamp' }],
    rara: [{ root: '#list', el: '.p', body: '.pb', mode: 'body' }]
  };
  var EXP_MS = 420;
  function anim(el, frames, done) {
    var a;
    try { a = el.animate(frames, { duration: EXP_MS, easing: SPRING }); } catch (e) { done(); return; }
    a.onfinish = a.oncancel = done;
  }
  function expand(cfg, el, opening, obs) {
    var body = el.querySelector(cfg.body);
    if (!body || reduce || !body.animate) return;
    if (body.getAnimations) each(body.getAnimations(), function (a) { a.cancel(); });
    if (cfg.mode === 'body') {                       /* 상품 카드 : 닫힌 쪽은 display:none */
      if (opening) {
        var hO = body.offsetHeight; if (!hO) return;
        body.style.overflow = 'hidden';
        anim(body, [{ height: '0px', opacity: 0 }, { height: hO + 'px', opacity: 1 }], function () { body.style.overflow = ''; });
      } else {
        body.style.display = 'block'; body.style.overflow = 'hidden';
        var hC = body.offsetHeight;
        anim(body, [{ height: hC + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], function () { body.style.display = ''; body.style.overflow = ''; });
      }
    } else if (cfg.mode === 'foot') {                /* 특약 상세의 보장 코드 칸 : 칸 높이(max-height)를 잇는다 */
      if (el.getAnimations) each(el.getAnimations(), function (a) { a.cancel(); });
      var bar = el.firstElementChild ? el.firstElementChild.offsetHeight : 48;
      if (opening) {
        var to = el.offsetHeight;
        anim(el, [{ maxHeight: bar + 'px' }, { maxHeight: to + 'px' }], function () {});
      } else {
        el.classList.add('open'); var from = el.offsetHeight; el.classList.remove('open');   /* 열려 있던 높이 */
        if (obs) obs.takeRecords();
        el.style.flex = '1 1 0'; body.style.display = 'block'; body.style.overflow = 'hidden';
        anim(el, [{ maxHeight: from + 'px' }, { maxHeight: bar + 'px' }], function () { el.style.flex = ''; body.style.display = ''; body.style.overflow = ''; });
      }
    } else if (cfg.mode === 'clamp') {               /* 약관 · 코드 「전체 펼치기」 : 잘린 높이 ↔ 다 펼친 높이 */
      var now = body.offsetHeight;
      el.classList.toggle('open'); var before = body.offsetHeight; el.classList.toggle('open');
      if (obs) obs.takeRecords();
      if (before === now) return;
      body.style.maxHeight = 'none'; body.style.overflow = 'hidden';
      anim(body, [{ height: before + 'px' }, { height: now + 'px' }], function () { body.style.maxHeight = ''; body.style.overflow = ''; });
    }
  }
  function expandInit() {
    var list = EXPAND[tool]; if (!list || !MO) return;
    each(list, function (cfg) {
      var root = d.querySelector(cfg.root);
      if (!root) return;
      var obs = new MO(function (recs) {
        each(recs, function (r) {
          var t = r.target;
          if (!t.matches || !t.matches(cfg.el)) return;
          var was = /(^|\s)open(\s|$)/.test(r.oldValue || ''), is = t.classList.contains('open');
          if (was !== is) expand(cfg, t, is, obs);
        });
      });
      obs.observe(root, { subtree: true, attributes: true, attributeFilter: ['class'], attributeOldValue: true });
    });
  }

  /* 5-4) 모달 · 시트가 닫히면 초점을 연 단추로 돌려준다(Esc · 바깥 누름 · ✕ 모두) */
  var OVSEL = '.ov, #hov, #mapov, #oncoov, #scov, .modal-overlay, #ex-mask, #sheet';
  var lastPress = null, ovState = [];
  d.addEventListener('pointerdown', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('a[href],button,[tabindex],input,select,textarea,summary') : null;
    if (t) lastPress = t;
  }, true);
  function ovOpen(el) { return el.classList.contains('show') || el.classList.contains('on'); }
  function ovWatch(recs) {
    each(recs, function (r) {
      var el = r.target;
      if (!el.matches || !el.matches(OVSEL)) return;
      var rec = null;
      for (var i = 0; i < ovState.length; i++) if (ovState[i].el === el) rec = ovState[i];
      if (!rec) { rec = { el: el, open: false, back: null }; ovState.push(rec); }
      var now = ovOpen(el);
      if (now === rec.open) return;
      rec.open = now;
      if (now) {
        var a = d.activeElement;
        rec.back = (a && a !== d.body && !el.contains(a)) ? a : (lastPress && !el.contains(lastPress) ? lastPress : null);
      } else {
        var b = rec.back, cur = d.activeElement; rec.back = null;
        if (b && b.isConnected !== false && d.body.contains(b) && (!cur || cur === d.body || el.contains(cur))) {
          try { b.focus({ preventScroll: true }); } catch (e) {}
        }
      }
    });
  }
  if (MO) new MO(ovWatch).observe(d.documentElement, { subtree: true, attributes: true, attributeFilter: ['class'] });

  var polish = function () {
    slideScan(); staggerInit(); expandInit();
    try { if (d.fonts && d.fonts.ready) d.fonts.ready.then(slideScan); } catch (e) {}
    /* 나중에 생기는 탭(시트 · 상세 창)을 위해 누를 때마다 한 번 더 살핀다 */
    d.addEventListener('click', function () { raf(slideScan); }, true);
  };
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', polish); else polish();

  var go = function () { (w.requestAnimationFrame || setTimeout)(function () { setTimeout(reveal, 0); }); };
  if (d.readyState === 'complete') go(); else w.addEventListener('load', go);
})();
