// 주요 화면 : 44px 미만 누름칸 · 12px 미만 글자 · 가로 넘침 · 지도 알약/이름표 겹침
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const [,, html, w] = process.argv;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext(+w !== 390 ? { viewport: { width: +w, height: 640 }, isMobile: true, hasTouch: true, reducedMotion: process.env.RM ? 'reduce' : 'no-preference' } : { ...devices['iPhone 13'], reducedMotion: process.env.RM ? 'reduce' : 'no-preference' });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const out = {};
  const routes = ['home', 'from', 'map', 'all', 'search', 'map/hokkaido', 'map/tohoku', 'map/kanto', 'map/chubu', 'map/kansai', 'map/chugoku', 'map/shikoku', 'map/kyushu', 'map/okinawa', 'kyoto', 'kyoto/food', 'kyoto/spot', 'kyoto/hotel', 'kyoto/prep', 'fukuoka', 'fukuoka/food', 'okinawa', 'sapporo/n3/d2'];
  for (const r of routes){
    await p.goto('file://' + path.resolve(html) + '#' + r); await p.waitForTimeout(250);
    out[r] = await p.evaluate(() => {
      const ov = (a, c) => a.left < c.right - 0.5 && a.right > c.left + 0.5 && a.top < c.bottom - 0.5 && a.bottom > c.top + 0.5;
      const small = [...document.querySelectorAll('button,a,[role="button"],[data-act]')].filter(e => { if (e.closest('svg')) return false; const q = e.getBoundingClientRect(); return q.width > 0 && q.height > 0 && (q.height < 43.5 || q.width < 43.5); }).map(e => (e.className && e.className.baseVal !== undefined ? e.className.baseVal : e.className) + ':' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height));
      let tiny = []; const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (tw.nextNode()){ const t = tw.currentNode; if (!t.textContent.trim() || t.parentElement.closest('.leaflet-container,#sheet,#langmenu,script,style')) continue; const el = t.parentElement; const q = el.getBoundingClientRect(); if (!q.width) continue; let fs = parseFloat(getComputedStyle(el).fontSize); const sv = el.closest('svg'); if (sv){ const ctm = el.getScreenCTM && el.getScreenCTM(); if (ctm) fs = fs * ctm.a; } if (fs > 0 && fs < 11.9) tiny.push(t.textContent.trim().slice(0, 12) + '@' + fs.toFixed(1)); }
      // 지도 알약 : 누름칸 높이, 서로 겹침
      const hits = [...document.querySelectorAll('.rl .hit')].map(e => e.getBoundingClientRect());
      const pills = [...document.querySelectorAll('.rl rect:not(.hit)')].map(e => e.getBoundingClientRect());
      let pillOv = 0; for (let i = 0; i < pills.length; i++) for (let j = i + 1; j < pills.length; j++) if (ov(pills[i], pills[j])) pillOv++;
      let hitOv = 0; for (let i = 0; i < hits.length; i++) for (let j = i + 1; j < hits.length; j++) if (ov(hits[i], hits[j])) hitOv++;
      // 도시 이름표 : 이름표끼리 · 남의 핀과 겹침 · 화면 밖 · 전체 지도 단추 아래
      const labs = [...document.querySelectorAll('.cp .pl')].map(e => ({ k: e.closest('.cp').dataset.v, r: e.getBoundingClientRect() }));
      const pins = [...document.querySelectorAll('.cp .pc')].map(e => ({ k: e.closest('.cp').dataset.v, r: e.getBoundingClientRect() }));
      const map = document.querySelector('#bigmap'), mr = map && map.getBoundingClientRect(), wb = document.querySelector('.whole'), wr = wb && wb.getBoundingClientRect();
      const labIss = [];
      labs.forEach((a, i) => { labs.forEach((c, j) => { if (j > i && ov(a.r, c.r)) labIss.push(a.k + '~' + c.k); }); pins.forEach(c => { if (c.k !== a.k && ov(a.r, c.r)) labIss.push(a.k + '>pin ' + c.k); }); if (mr && (a.r.left < mr.left || a.r.right > mr.right || a.r.top < mr.top || a.r.bottom > mr.bottom)) labIss.push(a.k + ' out'); if (wr && ov(a.r, wr)) labIss.push(a.k + ' under btn'); });
      pins.forEach(c => { if (wr && ov(c.r, wr)) labIss.push(c.k + ' pin under btn'); if (mr && (c.r.left < mr.left || c.r.right > mr.right || c.r.top < mr.top || c.r.bottom > mr.bottom)) labIss.push(c.k + ' pin out'); });
      const noLab = pins.filter(c => !labs.some(a => a.k === c.k)).map(c => c.k);
      return { hs: document.documentElement.scrollWidth > innerWidth + 1, nSmall: small.length, small: small.slice(0, 6), tiny: tiny.slice(0, 6), nTiny: tiny.length, minHit: hits.length ? Math.round(Math.min(...hits.map(h => h.height))) : null, pillOv, hitOv, labIss, noLab };
    });
  }
  const bad = Object.fromEntries(Object.entries(out).filter(([, v]) => v.hs || v.nSmall || v.nTiny || v.pillOv || v.hitOv || v.labIss.length || v.noLab.length || (v.minHit !== null && v.minHit < 44)));
  console.log(JSON.stringify({ w, bad, mapMinHit: out.map.minHit, errs }, null, 1));
  await b.close();
})();
