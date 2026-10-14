const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await (await b.newContext({ ...devices['iPhone 13'] })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(process.argv[2]) + '#home'); await p.waitForTimeout(500);
  await p.evaluate(() => {
    document.body.innerHTML = '<div id="t" style="display:grid;grid-template-columns:1fr;gap:10px;padding:16px;background:#FFFCFA"></div>';
    const t = document.getElementById('t');
    for (const f of ['', '간사이', '규슈', '오키나와', '홋카이도', '주부']) { const d = document.createElement('div'); d.style.cssText = 'border:1px solid #eee;border-radius:16px;overflow:hidden;background:#fff'; d.innerHTML = window.__jp.rmapSvg({ focus: f, cw: 358, ar: f ? 4 / 3 : undefined, sel: f === '간사이' ? 'kyoto' : '' }); t.appendChild(d); }
  });
  await p.screenshot({ path: process.argv[3], fullPage: true });
  console.log(JSON.stringify(errs));
  await b.close();
})();
