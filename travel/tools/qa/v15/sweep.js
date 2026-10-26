// 모든 도시 × 박 수 × 대체 플랜 × 일차 × 탭, 시트 몇 개까지 열어 오류·가로 넘침 점검
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const [,, html, w] = process.argv;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await (await b.newContext(w ? { viewport: { width: +w, height: 640 }, isMobile: true, hasTouch: true } : { ...devices['iPhone 13'] })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.text().startsWith('progress')) process.stderr.write(m.text() + '\n'); });
  await p.goto('file://' + path.resolve(html) + '#home'); await p.waitForTimeout(400);
  const res = await p.evaluate(async () => {
    const J = window.__jp, out = { views: 0, hs: [], empty: [] };
    const G = JSON.parse(document.getElementById('DATA').textContent).guides;
    const check = tag => { out.views++; if (out.views % 500 === 0) console.log('progress ' + out.views + ' ' + tag); if (document.documentElement.scrollWidth > innerWidth + 1) out.hs.push(tag); };
    for (const key of Object.keys(G)){
      const g = G[key];
      for (const t of ['food', 'spot', 'hotel', 'prep']){ J.applyRoute(J.parseRoute(`${key}/${t}`)); J.render({}); check(`${key}/${t}`); }
      for (const pl of g.plans){
        const vs = (g.variants || []).filter(v => v.for_nights === pl.nights);
        for (let v = 0; v <= vs.length; v++){
          const days = v ? vs[v - 1].days.length : pl.days.length;
          for (let d = 0; d < days; d++){
            J.applyRoute(J.parseRoute(`${key}/n${pl.nights}${v ? '/v' + v : ''}/d${d + 1}`)); J.render({});
            check(`${key}/n${pl.nights}/v${v}/d${d + 1}`);
            if (!document.querySelector('.tl .row')) out.empty.push(`${key}/n${pl.nights}/v${v}/d${d + 1}`);
            // 행마다 펼쳐 보기
            const rows = [...document.querySelectorAll('.rw[data-act="row"]')].map(r => r.dataset.v);
            for (const i of rows){ J.st.open = Number(i); J.render({}); check(`${key}/open${i}`); }
            J.st.open = -1;
          }
        }
      }
    }
    for (const r of ['home', 'from', 'map', 'all', 'search', 'map/hokkaido', 'map/tohoku', 'map/kanto', 'map/chubu', 'map/kansai', 'map/chugoku', 'map/shikoku', 'map/kyushu', 'map/okinawa']){ J.applyRoute(J.parseRoute(r)); J.render({}); check(r); }
    return out;
  });
  // 시트 몇 가지
  for (const [r, sel] of [['kyoto', '.cand'], ['kyoto', '[data-act="intro"]'], ['kyoto', '[data-act="planb"]'], ['kyoto', '[data-act="planinfo"]'], ['kyoto', '[data-act="sh-fly"]'], ['kyoto', '[data-act="sh-n"]'], ['kyoto/food', '.gcard'], ['kyoto/spot', '.gcard'], ['kyoto/hotel', '.hcard2'], ['map', '[data-act="sh-o"]']]){
    await p.goto('file://' + path.resolve(html) + '#' + r); await p.waitForTimeout(250);
    const el = await p.$(sel); if (!el){ errs.push('no ' + sel + ' on ' + r); continue; }
    await el.click(); await p.waitForTimeout(350);
    const open = await p.evaluate(() => document.getElementById('sheet').classList.contains('on'));
    if (!open) errs.push('sheet not open ' + r + ' ' + sel);
    await p.goBack(); await p.waitForTimeout(250);
    const still = await p.evaluate(() => document.getElementById('sheet').classList.contains('on'));
    if (still) errs.push('sheet not closed by back ' + r + ' ' + sel);
    const h = (await p.evaluate(() => location.hash)).replace(/\/n\d+/, ''); if (h !== '#' + r) errs.push(`hash after sheet back ${h} != #${r}`);
  }
  console.log(JSON.stringify({ views: res.views, hs: res.hs.slice(0, 10), nhs: res.hs.length, empty: res.empty.slice(0, 10), errs: [...new Set(errs)].slice(0, 20) }, null, 1));
  await b.close();
})();
