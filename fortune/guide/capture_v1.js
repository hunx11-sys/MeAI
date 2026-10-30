// 공모전 PPT 의 v1 → v2 비교용 v1 화면 캡처 (capture.js 와 같은 가상 고객 · 같은 씨앗 → 같은 사주 · 같은 4장)
// 쓰는 법 : node fortune/guide/capture_v1.js $PWD/fortune/legacy/unse_v1_261016.html <cap 폴더>   → v1_gate · v1_saju_result · v1_tarot_picked
const { chromium } = require('playwright'); const path = require('path');
const [, , FILE, OUT] = process.argv; const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, reducedMotion: 'reduce' });
  await ctx.addInitScript(() => { let a = 1213; const r = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0); };
    crypto.getRandomValues = function (arr) { for (let i = 0; i < arr.length; i++) arr[i] = r(); return arr; }; });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + FILE); await sleep(1200);
  await p.screenshot({ path: path.join(OUT, 'v1_gate.png') });
  await p.click('[data-go=saju]'); await sleep(600);
  await p.fill('#nm', '김하늘'); await p.click('#gender [data-v=F]'); await p.fill('#bd', '19880321'); await p.dispatchEvent('#bd', 'input'); await sleep(1500);
  const y1 = await p.evaluate(() => document.querySelector('#result').getBoundingClientRect().top + scrollY - 12);
  await p.evaluate(y => scrollTo(0, y), y1); await sleep(300); await p.screenshot({ path: path.join(OUT, 'v1_saju_result.png') });
  await p.click('#saju .cross'); await sleep(800);
  await p.click('#tGo'); await sleep(900);
  for (let k = 0; k < 4; k++) { const cs = await p.$$('.tc.sp'); await cs[14 + k * 12].click({ force: true }); await sleep(400); }
  await sleep(800);
  const ys = await p.evaluate(() => document.getElementById('stage').getBoundingClientRect().top + scrollY - 90);
  await p.evaluate(y => scrollTo(0, y), ys); await sleep(300); await p.screenshot({ path: path.join(OUT, 'v1_tarot_picked.png') });
  console.log('v1 errors', errs); await b.close();
})();
