// FM 교안용 영업지원도구 화면 캡처 · 1440x900 @2x
// node cap_tools.js <저장폴더>  → index.png · tool_search.png · tool_map.png · tool_history.png · tool_sim.png · itc.png
const { chromium } = require('playwright');
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), OUT = process.argv[2];
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  const p = await ctx.newPage(); p.setDefaultTimeout(8000);
  const shot = n => p.screenshot({ path: path.join(OUT, n + '.png') });
  await p.goto('file://' + ROOT + '/index.html'); await sleep(1500); await shot('index');
  await p.goto('file://' + ROOT + '/tool.html'); await sleep(2500);
  await p.fill('#q', '위암'); await sleep(1500); await p.keyboard.press('Escape'); await p.mouse.click(1380, 600); await sleep(600);
  await p.evaluate(() => scrollTo(0, 0)); await sleep(300); await shot('tool_search');
  for (const [t, n] of [['상급종합 지도', 'tool_map'], ['상품 히스토리', 'tool_history']]) {
    await p.goto('file://' + ROOT + '/tool.html'); await sleep(2500);
    await p.getByText(t, { exact: false }).first().click(); await sleep(1500); await shot(n);
  }
  await p.goto('file://' + ROOT + '/tool.html#sim'); await sleep(3500);
  const f = p.frames().find(x => x.url() === 'about:srcdoc');
  if (f) { const v = f.locator('input:visible').first(); await v.fill('위암'); await sleep(800); await v.press('Enter'); await sleep(2000); }
  await p.evaluate(() => scrollTo(0, 0)); await sleep(300); await shot('tool_sim');
  await p.goto('file://' + ROOT + '/통합치료비.html'); await sleep(2500); await shot('itc');
  await b.close();
})();
