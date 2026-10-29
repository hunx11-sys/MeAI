/* MeAI 홈 넛지 v5 · 실서버 호출 (모의 서버 src/api/mock.js 와 함수 이름 · 응답 모양이 같다)
 *
 *   const api = NZClient.createHttpApi('/api/nudge/v1', { headers: () => ({ 'X-CSRF-TOKEN': token }) });
 *   MeAINudge.mount({ api, host });
 *
 * 약속 (자세한 것은 docs/openapi.yaml)
 *  - 모든 쓰기 요청에 idem(멱등 키)을 붙인다. 같은 키가 두 번 오면 서버는 첫 결과를 그대로 돌려준다(두 번 누름 · 재전송 방지).
 *  - 쓰기 응답 = { ok, reason, grants[], fx[], home }. home 은 새 홈 요약. 화면은 이것만 보고 다시 그린다.
 *  - 사용자 · 조직은 서버가 로그인 세션으로 안다. 화면이 사용자 id 를 보내지 않는다(남의 기록을 쓸 수 없게).
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NZClient = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  function createHttpApi(base, opts) {
    opts = opts || {};
    const enc = encodeURIComponent;
    const qs = (p) => Object.keys(p || {}).filter((k) => p[k] !== '' && p[k] != null).map((k) => enc(k) + '=' + enc(p[k])).join('&');
    const idem = () => (self.crypto && crypto.randomUUID) ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2);
    async function req(method, path, body) {
      const headers = Object.assign({ 'Content-Type': 'application/json', 'X-Requested-With': 'MeAINudge' }, opts.headers ? opts.headers() : {});
      const ctl = typeof AbortController !== 'undefined' ? new AbortController() : null;
      const t = ctl ? setTimeout(() => ctl.abort(), opts.timeout || 8000) : 0;
      try {
        const r = await fetch(base + path, { method: method, headers: headers, credentials: 'include', body: body ? JSON.stringify(body) : undefined, signal: ctl ? ctl.signal : undefined });
        if (r.status === 401 && opts.onAuth) opts.onAuth();
        if (!r.ok) throw new Error('넛지 API ' + method + ' ' + path + ' → ' + r.status);
        return await r.json();
      } finally { clearTimeout(t); }
    }
    const post = (path, body) => req('POST', path, Object.assign({ idem: idem() }, body || {}));
    return {
      kind: 'http',
      getHome: () => req('GET', '/home'),
      attend: () => post('/attend'),
      event: (kind, p) => post('/events', Object.assign({ kind: kind }, p || {})),
      answerQuiz: (id, choice) => post('/quiz/' + enc(id) + '/answer', { choice: choice }),
      explainQuiz: (id) => post('/quiz/' + enc(id) + '/explained'),
      listTalks: (p) => req('GET', '/talks?' + qs(p)),
      getTalk: (id) => req('GET', '/talks/' + enc(id)),
      copyTalk: (id, typed) => post('/talks/' + enc(id) + '/copy', { typed: typed }),
      reactTalk: (id, type, on) => req('PUT', '/talks/' + enc(id) + '/reactions/' + enc(type), { on: !!on }),
      submitTalk: (t) => post('/talks', t),
      markDrawSeen: (round) => post('/lotto/' + enc(round) + '/seen'),
      markRecapSeen: (week) => post('/recap/' + enc(week) + '/seen'),
      getLeague: (scope) => req('GET', '/league?scope=' + enc(scope || 'branch')),
      cheer: (to) => post('/cheers', { to: to }),
      getRecord: () => req('GET', '/me/record'),
      openDash: () => post('/events', { kind: 'dash.open' }),
      getRecap: (week) => req('GET', '/recap' + (week ? '?week=' + enc(week) : '')),
      getOrgDash: (scope) => req('GET', '/dash/org?scope=' + enc(scope || 'hq')),
      getHqDash: () => req('GET', '/dash/hq'),
      saveSettings: (s) => req('PATCH', '/settings', s),
      dismissBuddy: (id) => post('/buddy/' + enc(id) + '/dismiss'),
      // 사용 기록 : 화면을 떠날 때도 잃지 않게 sendBeacon 우선
      log: (events) => {
        const body = JSON.stringify({ events: events });
        if (navigator.sendBeacon && navigator.sendBeacon(base + '/logs', new Blob([body], { type: 'application/json' }))) return Promise.resolve({ ok: true });
        return req('POST', '/logs', { events: events });
      }
    };
  }
  return { createHttpApi: createHttpApi };
});
