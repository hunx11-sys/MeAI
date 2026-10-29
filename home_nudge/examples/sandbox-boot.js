/* 연습 화면 켜기 : 설정 · 예시 데이터를 같은 서버에서 받아(connect-src 'self') 모의 서버로 넛지를 붙인다.
 * 실서버가 생기면 NZMock.createMockApi(...) 한 줄을 NZClient.createHttpApi('/api/nudge/v1') 로 바꾸면 된다. */
(function () {
  'use strict';
  const get = (p) => fetch(p).then((r) => { if (!r.ok) throw new Error(p + ' ' + r.status); return r.json(); });
  const log = (t) => { const li = document.createElement('li'); li.textContent = new Date().toTimeString().slice(0, 8) + '  ' + t; const ol = document.getElementById('evlog'); ol.insertBefore(li, ol.firstChild); };
  // 걱정인형 그림 자리 : <html data-asset-base> (저장소 = ../../ui/, 개발 패키지 = ../assets/ 로 조립 때 바뀐다)
  const assetBase = document.documentElement.getAttribute('data-asset-base') || '../assets/';
  const tarotBase = document.documentElement.getAttribute('data-tarot-base') || '../assets/tarot/';
  Promise.all(['../config/nudge.config.json', '../data/calendar.json', '../data/quiz.json', '../data/talks798.json', '../data/seed.json', '../data/ox_bank.json'].map(get))
    .then(async (d) => {
      const data = { cfg: d[0], cal: d[1], quiz: d[2], talks: d[3], seed: d[4], ox: d[5] };
      data.seed.reco = [{ id: 'c-501', name: '김민수', tags: ['age_up'] }, { id: 'c-502', name: '정재민', tags: [] }, { id: 'c-503', name: '서은아', tags: [] }];
      const api = NZMock.createMockApi(data, { issueOn: 'chat.custom' });   // 운영 권장값 : 맞춤대화를 시작할 때 세트 발급
      const host = NZSimpleHost.createSimpleHost({
        onGo: (t) => { log('host.go("' + t + '")'); if (t === 'reco') document.querySelector('.reco').scrollIntoView({ behavior: 'smooth' }); },
        onAsk: (text) => log('host.ask → 일반대화 입력칸에 : ' + text.replace(/\n/g, ' '))
      });
      await MeAINudge.mount({ api: api, host: host, assetBase: assetBase, tarotBase: tarotBase });
      log('MeAINudge.mount 완료 · 모의 서버 · 그림 ' + assetBase);
      // 홈 쪽 행동 → report
      document.addEventListener('click', (e) => {
        const a = e.target.closest('article[data-nz-reco]'); const h = e.target.closest('[data-host]');
        if (a && e.target.closest('[data-open-reco]')) { MeAINudge.report('reco.open', { customerId: a.dataset.nzReco }); log("report('reco.open', { customerId: '" + a.dataset.nzReco + "' })"); }
        if (a && e.target.closest('[data-chat]')) { MeAINudge.report('chat.custom', { customerId: a.dataset.nzReco }); log("report('chat.custom', { customerId: '" + a.dataset.nzReco + "' })"); }
        if (h && h.dataset.host === 'general') { MeAINudge.report('chat.general', {}); log("report('chat.general')"); }
        if (h && h.dataset.host === 'board') { MeAINudge.report('notice.read', { ref: 'n-1029' }); log("report('notice.read', { ref: 'n-1029' })"); }
        if (h && h.dataset.host === 'consent') { MeAINudge.report('consent.request', {}); log("report('consent.request')"); }
      });
    })
    .catch((e) => { log('불러오기 실패 : ' + e.message + ' · 파일로 열지 말고 웹서버로 열어 주세요 (예 : python -m http.server, home_nudge 폴더에서)'); });
})();
