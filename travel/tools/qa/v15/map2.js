const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path'), fs = require('fs');
const [,, html, out] = process.argv; const url = 'file://' + path.resolve(html);
const tile = fs.readFileSync(path.join(out, 'tile.png'));
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const mk = async (opt) => { const c = await b.newContext(Object.assign({ ...devices['iPhone 13'], deviceScaleFactor: 2 }, opt || {})); const p = await c.newPage();
    await p.route(/cyberjapandata|openstreetmap/, r => r.fulfill({ status: 200, contentType: 'image/png', body: tile }));
    await p.route(/maps\.google\.com/, r => r.fulfill({ status: 200, contentType: 'text/html', body: '<html><body style="margin:0;background:#e8f0e0">G</body></html>' }));
    p.errs = []; p.on('pageerror', e => p.errs.push(e.message)); return p; };
  const R = {};
  // race : open then close fast
  let p = await mk();
  await p.goto(url + '#kyoto/n3/d2'); await p.waitForTimeout(700);
  await p.click('[data-act="bigmap"]'); await p.waitForTimeout(100); await p.keyboard.press('Escape'); await p.waitForTimeout(80);
  if (await p.evaluate(() => document.getElementById('sheet').classList.contains('on'))) await p.goBack();
  await p.waitForTimeout(1500);
  R.race = await p.evaluate(() => [document.querySelectorAll('#sheet .leaflet-container,#sheet .rt-run').length, document.getAnimations().filter(a => a.playState === 'running' && a.effect && a.effect.target && a.effect.target.closest && a.effect.target.closest('#sheet')).length]);
  // zoom then switch mode quickly
  await p.click('[data-act="bigmap"]'); await p.waitForTimeout(1300);
  await p.click('.mapc >> nth=4'); await p.waitForTimeout(60); await p.click('.mapmode [data-v="google"]'); await p.waitForTimeout(600);
  await p.click('.mapmode [data-v="route"]'); await p.waitForTimeout(80); await p.click('.mapmode [data-v="google"]'); await p.waitForTimeout(600);
  await p.click('.mapmode [data-v="route"]'); await p.waitForTimeout(900);
  R.zoomSwitchErrs = p.errs.slice();
  R.pinSpread = await p.evaluate(() => [...document.querySelectorAll('.leaflet-marker-pane .pin')].filter(e => e.style.translate).length);
  await p.screenshot({ path: out + '/m2_route.png' });
  // still mode
  await p.goto(url + '#home'); await p.waitForTimeout(500); await p.evaluate(() => { localStorage.setItem('jp_still', '1'); }); await p.goto(url + '#kyoto/n3/d2'); await p.reload(); await p.waitForTimeout(700);
  await p.click('[data-act="bigmap"]'); await p.waitForTimeout(1300);
  R.still = await p.evaluate(() => [document.querySelectorAll('.rt-run').length, getComputedStyle(document.querySelector('.rt-flow')).animationName, getComputedStyle(document.querySelector('.mfl')).animationName]);
  await p.evaluate(() => localStorage.removeItem('jp_still'));
  // sheet fits : card visible
  for (const [w, h] of [[320, 568], [375, 667], [390, 664]]){
    const q = await mk({ viewport: { width: w, height: h } });
    await q.goto(url + '#kyoto/n3/d2'); await q.waitForTimeout(600); await q.click('[data-act="bigmap"]'); await q.waitForTimeout(1300);
    R['fit' + w] = await q.evaluate(() => { const c = document.querySelector('.mapc'), r = c.getBoundingClientRect(), m = document.getElementById('daymap').getBoundingClientRect(); return [Math.round(m.height), Math.round(r.bottom), innerHeight, r.bottom <= innerHeight]; });
    if (w === 320) await q.screenshot({ path: out + '/m2_320.png' });
  }
  console.log(JSON.stringify(R));
  await b.close();
})();
