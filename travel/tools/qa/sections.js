// 목적지 화면을 세로로 잘라 여러 장으로 찍는다. 사용: node sections.js <html> <hash> <폴더> [조각수]
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path'), fs = require('fs');
const [,, html, hash, out, nStr] = process.argv; const n = Number(nStr || 6);
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ko-KR', deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(html) + '#' + hash, { waitUntil: 'load' });
  await page.waitForTimeout(1200);
  fs.mkdirSync(out, { recursive: true });
  const H = await page.evaluate(() => document.documentElement.scrollHeight);
  const step = 1500;
  for (let i = 0; i < n && i * step < H; i++) {
    await page.evaluate(y => window.scrollTo(0, y), i * step);
    await page.waitForTimeout(250);
    await page.screenshot({ path: path.join(out, `s${i}.png`), clip: { x: 0, y: i * step, width: 390, height: Math.min(step, H - i * step) }, fullPage: true });
  }
  console.log('height', H, 'shots', Math.min(n, Math.ceil(H / step)));
  await browser.close();
})();
