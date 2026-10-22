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
  var REVEAL = '[data-reveal], .cards > .card, .p, .card, .panel, .kpis > *';
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
  var go = function () { (w.requestAnimationFrame || setTimeout)(function () { setTimeout(reveal, 0); }); };
  if (d.readyState === 'complete') go(); else w.addEventListener('load', go);
})();
