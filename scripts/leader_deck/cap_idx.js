// 영업지원도구 대문(index.html) 화면 캡처 · 1440x900 @2x
// node cap_idx.js <index.html 절대경로> <저장할 png>
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.waitForTimeout(1500);
  await p.screenshot({ path: process.argv[3] });
  await b.close();
})();
