const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path'), fs = require('fs');
const [,, html, out] = process.argv; const url = 'file://' + path.resolve(html);
const tile = fs.readFileSync(path.join(out, 'tile.png'));
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const mk = async (opt, tiles) => { const c = await b.newContext(Object.assign({ ...devices['iPhone 13'], deviceScaleFactor: 2 }, opt || {})); const p = await c.newPage();
    if (tiles) await p.route(/cyberjapandata|openstreetmap/, r => r.fulfill({ status: 200, contentType: 'image/png', body: tile }));
    else await p.route(/cyberjapandata|openstreetmap/, r => r.abort());
    await p.route(/maps\.google\.com/, r => r.fulfill({ status: 200, contentType: 'text/html', body: '<html><body style="margin:0;background:#e8f0e0;font:16px sans-serif;display:grid;place-items:center;height:100vh">GOOGLE EMBED ' + r.request().url().replace(/&/g, ' &amp;') + '</body></html>' }));
    p.errs = []; p.on('pageerror', e => p.errs.push(e.message)); return p; };
  const R = {};
  // 1) Leaflet with tiles
  let p = await mk({}, true);
  await p.goto(url + '#kyoto/n3/d2'); await p.waitForTimeout(800);
  await p.click('[data-act="bigmap"]'); await p.waitForTimeout(1600);
  R.leaf = await p.evaluate(() => ({ flow: document.querySelectorAll('.rt-flow').length, arr: document.querySelectorAll('.rt-arr').length, run: document.querySelectorAll('.rt-run').length, pins: document.querySelectorAll('.leaflet-marker-pane .pin').length, note: document.getElementById('mapnote').textContent.slice(0, 20), gd: [...document.querySelectorAll('.gdir')].map(a => [a.innerText.trim(), decodeURIComponent(a.href).slice(0, 160)]), go: [...document.querySelectorAll('.mapc .go')].slice(0, 3).map(a => [a.innerText.trim(), a.href.slice(0, 120)]) }));
  const pos1 = await p.evaluate(() => { const i = document.querySelector('.rt-run i'); return getComputedStyle(i).transform + '|' + i.getAnimations().length; });
  await p.waitForTimeout(700);
  const pos2 = await p.evaluate(() => { const i = document.querySelector('.rt-run i'); return getComputedStyle(i).transform + '|' + i.getAnimations().length; }); R.pos = [pos1, pos2];
  R.runnerMoves = pos1 !== pos2;
  await p.screenshot({ path: out + '/m_leaf.png' });
  // 2) Google mode
  await p.click('.mapmode [data-v="google"]'); await p.waitForTimeout(800);
  R.g1 = await p.evaluate(() => { const f = document.getElementById('gframe'); return [!!f, f && f.getAttribute('src'), document.querySelectorAll('.leaflet-container').length, document.getElementById('mapnote').textContent.slice(0, 18), localStorage.getItem('jp_mapMode') || Object.keys(localStorage).filter(k => /mapMode/.test(k)).map(k => k + '=' + localStorage.getItem(k)).join()]; });
  await p.click('.mapc >> nth=2'); await p.waitForTimeout(400);
  R.g2 = await p.evaluate(() => document.getElementById('gframe').getAttribute('src'));
  await p.screenshot({ path: out + '/m_google.png' });
  await p.click('.mapmode [data-v="route"]'); await p.waitForTimeout(800);
  R.back = await p.evaluate(() => [document.querySelectorAll('.leaflet-container').length, document.querySelectorAll('.rt-run').length, !!document.getElementById('gframe')]);
  // reopen : remembered mode
  await p.click('.mapmode [data-v="google"]'); await p.waitForTimeout(300);
  await p.goBack(); await p.waitForTimeout(500);
  await p.click('[data-act="bigmap"]'); await p.waitForTimeout(1200);
  R.remember = await p.evaluate(() => [!!document.getElementById('gframe'), document.querySelector('.mapmode [aria-pressed="true"]').dataset.v]);
  await p.click('.mapmode [data-v="route"]'); await p.waitForTimeout(600);
  await p.goBack(); await p.waitForTimeout(600);
  await p.waitForTimeout(800); const t1 = await p.evaluate(() => [document.querySelectorAll('#sheet .leaflet-container,#sheet .rt-run,#gframe').length, document.getAnimations().filter(a => a.playState === 'running').length]);
  const t2 = t1;
  R.afterClose = t1;
  R.errs1 = p.errs;
  // 3) sketch fallback (tiles blocked)
  p = await mk({}, false);
  await p.goto(url + '#kyoto/n3/d2'); await p.waitForTimeout(800);
  await p.click('[data-act="bigmap"]'); await p.waitForTimeout(3500);
  R.sketch = await p.evaluate(() => ({ sk: !!document.querySelector('#daymap .sketch'), arr: document.querySelectorAll('.sketch .ar').length, run: document.querySelectorAll('.sketch .run animateMotion').length, lf: getComputedStyle(document.querySelector('.sketch .lf')).animationName }));
  await p.screenshot({ path: out + '/m_sketch.png' }); R.errs2 = p.errs;
  // 4) reduced motion
  p = await mk({ reducedMotion: 'reduce' }, true);
  await p.goto(url + '#kyoto/n3/d2'); await p.waitForTimeout(600);
  await p.click('[data-act="bigmap"]'); await p.waitForTimeout(1400);
  R.reduced = await p.evaluate(() => ({ run: document.querySelectorAll('.rt-run').length, arr: document.querySelectorAll('.rt-arr').length, flow: getComputedStyle(document.querySelector('.rt-flow')).animationName, mini: getComputedStyle(document.querySelector('.mfl') || document.body).animationName }));
  R.errs3 = p.errs;
  // 5) mini map anim
  p = await mk({}, true); await p.goto(url + '#kyoto/n3/d2'); await p.waitForTimeout(600);
  R.mini = await p.evaluate(() => getComputedStyle(document.querySelector('.mfl')).animationName);
  console.log(JSON.stringify(R, null, 1));
  await b.close();
})();
