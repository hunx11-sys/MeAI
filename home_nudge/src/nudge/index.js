/* MeAI 홈 넛지 v5 · 붙이기 (바깥에 드러나는 유일한 이름 : window.MeAINudge)
 *
 *   MeAINudge.mount({ api, host, assetBase })
 *     api  : src/api/client.js(실서버) 또는 src/api/mock.js(모의 서버), 같은 함수 이름
 *     host : 홈 화면과 넛지를 잇는 다리 (자리 4곳 · 추천 고객 카드 · 이동 · 질문 넣기). 정식 연동 예시는 docs/INTEGRATION.md,
 *            목업은 src/host/dom-adapter.js(원본 홈 빌드를 고치지 않고 DOM 에 얹는 방식)
 *   MeAINudge.report(kind, payload)  : 홈 쪽에서 일어난 영업 행동을 알린다
 *     'reco.open' {customerId} · 'chat.custom' {customerId} · 'chat.general' · 'notice.read' {ref} · 'consent.request' {customerId}
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ;
  let mounted = false;

  function prefetchTalks(h) {
    (h.talk.ticker || []).slice(0, 6).forEach((t, i) => setTimeout(() => {
      if (!NZ.talkCache[t.id]) NZ.api.getTalk(t.id).then((x) => { NZ.talkCache[t.id] = x; });
    }, 800 + i * 150));
  }

  const MeAINudge = {
    version: NZ.version,
    async mount(o) {
      if (mounted) return MeAINudge;
      NZ.api = o.api; NZ.host = o.host; if (o.assetBase != null) NZ.assetBase = o.assetBase;
      const nodes = NZ.ui.build(o.host);
      o.host.attach(nodes);                       // 자리 : 머리 띠(cap) · 인사말 아래(dock) · 인사말 옆(buddy) · 추천 고객 제목(recHint)
      NZ.onChange((h) => { NZ.ui.render(h); document.documentElement.classList.toggle('nz-calm', h.settings.fx === 'off'); });
      const h = await NZ.load();
      NZ.ui.startTicker();
      prefetchTalks(h);
      mounted = true;
      NZ.log('home', 'view');
      return MeAINudge;
    },
    // 홈에서 일어난 영업 행동 → 서버 평가 → 연출
    report(kind, payload) {
      if (!NZ.api) return Promise.resolve(null);
      NZ.log('host_' + kind, 'event', payload && payload.customerId ? { c: 1 } : {});
      return NZ.run(NZ.api.event(kind, payload || {}), { quiet: true });
    },
    refresh() { return NZ.load(); },
    render() { if (NZ.home) NZ.ui.render(NZ.home); },
    open(key) { NZ.ui.go(key); },
    close() { NZ.ui.close(); },
    home() { return NZ.home; },
    fx: (list, grants) => NZ.fx.play(list, grants || [], {}),
    logs: () => NZ.logs.slice(),
    _nz: NZ
  };
  G.MeAINudge = MeAINudge;
})(window);
