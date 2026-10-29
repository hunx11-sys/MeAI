/* MeAI 홈 넛지 v5 · 목업용 홈 어댑터 (원본 MeAI 홈 React 빌드 260929 를 고치지 않고 DOM 에 얹는다)
 *
 * 정식 개발에서는 이 파일 대신 홈 컴포넌트에 자리 3곳을 만들고 이벤트 5개를 MeAINudge.report 로 보낸다 (docs/INTEGRATION.md).
 * 이 어댑터가 하는 일
 *   1) 자리 찾기 : 머리 띠 오른쪽(캡슐) · 인사말 아래(막대) · 인사말 옆(버디) · 추천 고객 제목 옆(안내) · 추천 고객 카드(배지)
 *   2) 원본 화면의 행동을 넛지 행동으로 바꾸기 : 추천 고객 카드 → reco.open · 맞춤대화 화면 진입 → chat.custom ·
 *      일반대화 전송 → chat.general · 게시판 → notice.read · 고객 동의 「보내기」 → consent.request
 *   3) 넛지에서 원래 기능으로 가기 (하러 가기 · MeAI에게 묻기)
 * React 가 화면을 다시 그려 넛지 부품이 떨어져 나가면 MutationObserver 로 다시 붙인다(부품은 그대로라 상태 유지).
 */
(function (G) {
  'use strict';
  const HOME = /^#\/mg-gate-010(?:$|\?)/;
  const $ = (s, r) => (r || document).querySelector(s), $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const byText = (sel, txt, root) => $$(sel, root).find((e) => (e.innerText || e.textContent || '').trim().indexOf(txt) === 0);
  function hash32(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36); }
  const idOf = (name) => 'c-' + hash32(name.trim());

  function createDomHost(opt) {
    opt = opt || {};
    let nodes = null, ready = null, lastReco = null, boardSeen = '', customSeen = '';
    const recoMeta = {};   // id → {name, tags}

    const host = {
      isHome: () => HOME.test(location.hash),
      attach(n) { nodes = n; ensure(); },
      // 추천 고객 카드 목록 (이름으로 고객 id 를 만든다 · 실제 연동은 추천 서비스의 고객 id 를 그대로 쓴다)
      recoCards() {
        const sec = sections()[1]; if (!sec) return [];
        return $$('.grid > div', sec).map((el) => {
          const nm = el.querySelector('span'), name = nm ? nm.textContent.trim() : '';
          const txt = el.innerText || '';
          const id = idOf(name), tags = /상령일/.test(txt) ? ['age_up'] : [];
          recoMeta[id] = { name: name, tags: tags };
          return { el: el, id: id, name: name, tags: tags };
        }).filter((c) => c.name);
      },
      placeRecoBadge(card, badge) {
        const chip = $$('span', card).find((s) => /사전조회동의/.test(s.textContent || '') && s.children.length < 3);
        const row = chip ? chip.parentElement : card.querySelector('.mt-auto') || card;
        badge.classList.add('nz-recb-inline'); row.appendChild(badge);
      },
      go(target) {
        const W = G.__NZ;
        if (target === 'home') { location.hash = '#/mg-gate-010'; return; }
        if (!host.isHome() && ['reco', 'board', 'consent', 'custom', 'general', 'find'].indexOf(target) >= 0 && target !== 'board') { location.hash = '#/mg-gate-010'; setTimeout(() => host.go(target), 700); return; }
        if (target === 'reco') {
          const sec = sections()[1]; if (!sec) return;
          sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
          const g = $('.grid', sec); if (g) { g.classList.remove('nz-spot'); void g.offsetWidth; g.classList.add('nz-spot'); }
          W && W.toast('추천 고객 카드를 열어 보세요 · ' + (W.home && W.home.reco.issueOn === 'reco.open' ? '열면' : '맞춤대화를 하면') + ' <b>' + (W.home ? W.home.labels.lotto : '로또') + ' 1세트</b>', { icon: 'lotto' });
          return;
        }
        if (target === 'board') { const b = byText('#root button', '게시판'); if (b) b.click(); else location.hash = '#/mg-board-010'; return; }
        if (target === 'consent') { const b = byText('#root button', '고객 동의'); if (b) b.click(); return; }
        if (target === 'custom') { const c = byText('#root [class*="cursor-pointer"]', '맞춤대화'); if (c) c.click(); return; }
        if (target === 'general') { const c = byText('#root [class*="cursor-pointer"]', '일반대화'); if (c) c.click(); return; }
        if (target === 'find') { const b = byText('#root button', 'MeAI 고객찾기'); if (b) b.click(); return; }
        if (target === 'fortune') { // 목업 : 옆 파일(unse_saju_tarot.html)을 홈 위 덮개 안에 띄운다 (새 창으로도 열 수 있음)
          const url = opt.fortuneUrl || 'unse_saju_tarot.html';
          if (W && W.fun && W.fun.openFrame) { W.fun.openFrame(url, '오늘의 운세 · 사주 + 타로'); return; }
          const w = G.open(url, '_blank'); if (!w && W) W.toast('운세 화면은 dist/unse_saju_tarot.html 이에요'); return;
        }
      },
      // 일반대화 입력칸에 질문을 넣어 둔다 (보내기는 사람이 누른다)
      ask(text) {
        const W = G.__NZ;
        const put = () => {
          const t = $('#root textarea'); if (!t) return false;
          const set = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
          set.call(t, text); t.dispatchEvent(new Event('input', { bubbles: true })); t.focus();
          W && W.toast('일반대화에 질문을 넣어 두었어요. <b>전송</b>만 누르면 돼요', { icon: 'send' });
          return true;
        };
        if (/^#\/gc-home-010/.test(location.hash) && put()) return;
        location.hash = '#/gc-home-010';
        let n = 0; const t = setInterval(() => { if (put() || ++n > 30) clearInterval(t); }, 100);
      }
    };

    function wrap() { return $('#root .gate-fontscale'); }
    function sections() { const w = wrap(); return w ? $$('section', w).filter((s) => !s.closest('.nz')) : []; }
    function ensure() {
      if (!nodes) return;
      const on = host.isHome();
      document.documentElement.classList.toggle('nz-on-home', on);
      if (!on) return;
      const w = wrap(); if (!w) return;
      const secs = sections(), s1 = secs[0], s2 = secs[1];
      if (s1) {
        const h1 = s1.querySelector(':scope > h1');
        if (h1 && nodes.dock.previousElementSibling !== h1) h1.insertAdjacentElement('afterend', nodes.dock);
        s1.classList.add('nz-host-s1');
        if (nodes.buddy.parentElement !== s1) s1.appendChild(nodes.buddy);
      }
      const fs = $('.gate-fontscale-reset', w);
      if (fs && fs.parentElement && nodes.cap.nextElementSibling !== fs) fs.parentElement.insertBefore(nodes.cap, fs);
      if (s2) { const h2 = s2.querySelector('h2'); if (h2 && nodes.recHint.parentElement !== h2) h2.appendChild(nodes.recHint); }
      // 추천 고객 목록이 바뀌었으면 모의 서버에 알려 준다 (실서버는 추천 서비스가 이미 안다)
      const cards = host.recoCards(), key = cards.map((c) => c.id).join(',');
      if (key && key !== host._recoKey) {
        host._recoKey = key;
        const all = Object.keys(recoMeta).map((id) => ({ id: id, name: recoMeta[id].name, tags: recoMeta[id].tags }));
        if (G.__NZ && G.__NZ.api && G.__NZ.api.demo) G.__NZ.api.demo.setReco(all).then((h) => G.__NZ.setHome(h));
      }
      if (G.MeAINudge && G.__NZ.home) G.__NZ.ui.render(G.__NZ.home);
    }
    let pend = false;
    const schedule = () => { if (pend) return; pend = true; requestAnimationFrame(() => { pend = false; ensure(); }); };

    // ── 원본 화면 행동 → 넛지 행동 ───────────────────────────
    document.addEventListener('click', (e) => {
      const t = e.target; if (!t || !t.closest || t.closest('.nz')) return;
      const N = G.MeAINudge; if (!N) return;
      const card = host.isHome() && t.closest('#root section .grid > div');
      if (card) {
        const nm = card.querySelector('span'), name = nm ? nm.textContent.trim() : '';
        if (name) { lastReco = idOf(name); N.report('reco.open', { customerId: lastReco }); }
        return;
      }
      const btn = t.closest('#root button, [role="dialog"] button, body > div button');
      if (!btn) return;
      const label = (btn.innerText || '').trim();
      if (/^#\/gc-home-010/.test(location.hash) && label === '전송') { const ta = $('#root textarea'); if (ta && ta.value.trim()) N.report('chat.general', {}); return; }
      if (label === '보내기' && $$('button').some((b) => (b.innerText || '').trim() === '고객 동의')) { N.report('consent.request', {}); return; }
      if (label === '대화 시작하기' && /^#\/pc-home-010/.test(location.hash)) { N.report('chat.custom', { customerId: customFromHash() }); }
    }, true);
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter' || e.shiftKey || e.isComposing) return;
      const t = e.target; if (!t || t.tagName !== 'TEXTAREA' || !t.closest('#root') || !t.value.trim()) return;
      if (/^#\/gc-home-010/.test(location.hash)) G.MeAINudge && G.MeAINudge.report('chat.general', {});
      else if (/^#\/pc-home-010/.test(location.hash)) G.MeAINudge && G.MeAINudge.report('chat.custom', { customerId: customFromHash() });
    }, true);
    function customFromHash() {
      const m = location.hash.match(/[?&]cn=([^&]+)/);
      if (m) { try { return idOf(decodeURIComponent(m[1])); } catch (x) { /* 이름을 못 읽으면 마지막으로 연 고객 */ } }
      return lastReco || '';
    }
    function onRoute() {
      schedule();
      const N = G.MeAINudge; if (!N) return;
      const day = new Date().toDateString();
      // 맞춤대화 화면에 고객과 함께 들어오면 = 추천 고객 맞춤대화 시작
      if (/^#\/pc-home-010/.test(location.hash)) {
        const id = customFromHash(), key = day + id;
        if (id && customSeen !== key) { customSeen = key; setTimeout(() => N.report('chat.custom', { customerId: id }), 400); }
      }
      if (/^#\/mg-board/.test(location.hash) && boardSeen !== day) { boardSeen = day; setTimeout(() => N.report('notice.read', { ref: 'n-1029' }), 1200); }
    }
    G.addEventListener('hashchange', onRoute);

    function boot() {
      if (!location.hash || location.hash === '#/' || location.hash === '#') location.hash = '#/mg-gate-010';
      const root = document.getElementById('root');
      if (root) new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
      schedule();
    }
    ready = new Promise((res) => {
      const go = () => { boot(); const t = setInterval(() => { if (wrap()) { clearInterval(t); res(); } }, 50); setTimeout(() => { clearInterval(t); res(); }, 4000); };
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
    });
    host.ready = ready;
    return host;
  }
  G.NZHost = { createDomHost: createDomHost, idOf: idOf };
})(window);
