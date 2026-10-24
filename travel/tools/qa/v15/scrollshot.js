// 실제처럼 아래로 내리며 화면을 찍어 이어 붙인다(스크롤하면 떠오르는 요소 확인용)
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const [,, html, route, out, w, pages] = process.argv;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext(w && +w !== 390 ? { viewport: { width: +w, height: 700 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true } : { ...devices['iPhone 13'], deviceScaleFactor: 2 });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(html) + '#' + route); await p.waitForTimeout(1600);
  const H = await p.evaluate(() => innerHeight), n = +(pages || 4);
  for (let k = 0; k < n; k++){
    await p.evaluate(y => window.scrollTo({ top: y, behavior: 'instant' }), k * (H - 60)); await p.waitForTimeout(1300);
    await p.screenshot({ path: `${out}_${k}.png` });
  }
  if (errs.length) console.log(errs);
  await b.close();
})();
