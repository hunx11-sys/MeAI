/* MeAI 홈 넛지 v5 · 정식 연동용 홈 어댑터 (예시)
 *
 * 실제 MeAI 홈(React)을 고칠 때의 모양 : 홈 화면에 자리 4곳을 만들고, 추천 고객 카드에 data-nz-reco 를 붙인다.
 *   <div id="nz-slot-cap">      머리 띠 오른쪽 (글씨 확대 앞)
 *   <div id="nz-slot-buddy">    인사말 줄 오른쪽 (position: relative 인 부모 안)
 *   <div id="nz-slot-dock">     인사말 바로 아래
 *   <span id="nz-slot-rechint"> 「오늘의 추천 고객」 제목 옆
 *   <article data-nz-reco="고객id" data-name="이름" data-tags="age_up"> … <span data-nz-badge></span></article>
 * React 예시는 docs/INTEGRATION.md. 이 파일은 그 약속을 그대로 지키는 가장 작은 다리다(examples/sandbox.html 에서 씀).
 */
(function (G) {
  'use strict';
  function createSimpleHost(o) {
    o = o || {};
    const $ = (s) => document.querySelector(s);
    return {
      isHome: () => true,
      attach(n) {
        const put = (sel, node) => { const s = $(sel); if (s && node.parentElement !== s) s.appendChild(node); };
        put(o.cap || '#nz-slot-cap', n.cap); put(o.buddy || '#nz-slot-buddy', n.buddy); put(o.dock || '#nz-slot-dock', n.dock); put(o.recHint || '#nz-slot-rechint', n.recHint);
      },
      recoCards: () => Array.from(document.querySelectorAll('[data-nz-reco]')).map((el) => ({ el: el, id: el.getAttribute('data-nz-reco'), name: el.getAttribute('data-name') || '', tags: (el.getAttribute('data-tags') || '').split(',').filter(Boolean) })),
      placeRecoBadge(card, badge) { (card.querySelector('[data-nz-badge]') || card).appendChild(badge); },
      go: (target) => (o.onGo ? o.onGo(target) : console.log('[넛지] 이동 요청', target)),
      ask: (text, mode) => (o.onAsk ? o.onAsk(text, mode) : console.log('[넛지] MeAI 질문 넣기', mode, text))
    };
  }
  G.NZSimpleHost = { createSimpleHost: createSimpleHost };
})(window);
