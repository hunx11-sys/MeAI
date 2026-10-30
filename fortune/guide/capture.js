// 사용 가이드 PPT 용 화면 캡처 → <cap 폴더>/*.png (390x844 @3x) + rects.json (번호 표시 자리)
//   가상의 고객 「김하늘」(1988-03-21, 여) · 타로는 시험용 고정 씨앗(1213)으로 섞어 늘 같은 4장
//   (운명의 수레바퀴 · 컵 여왕 역방향 · 힘 · 소드 에이스). 도구 자체의 무작위는 바꾸지 않는다 (이 캡처에서만 crypto 를 바꿔 끼움)
// 쓰는 법 : node fortune/guide/capture.js $PWD/dist/unse_saju_tarot.html <cap 폴더>
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const [, , FILE, OUT] = process.argv;
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, acceptDownloads: true, reducedMotion: 'reduce' });
  await ctx.addInitScript(() => {
    let a = 1213; const r = () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0); };
    crypto.getRandomValues = function (arr) { for (let i = 0; i < arr.length; i++) arr[i] = r(); return arr; };
  });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const shot = (n, opt) => p.screenshot(Object.assign({ path: path.join(OUT, n + '.png') }, opt || {}));
  const el = (sel, n) => p.locator(sel).first().screenshot({ path: path.join(OUT, n + '.png') });
  const top = y => p.evaluate(y => window.scrollTo(0, y), y);
  const R = {}; // 화면 캡처 안에서 각 부분의 위치 (CSS px, 뷰포트 기준)
  const rects = (n, sels) => p.evaluate(sels => { const o = {}; for (const k in sels) { const e = document.querySelector(sels[k]); if (e) { const r = e.getBoundingClientRect(); o[k] = [r.left, r.top, r.width, r.height].map(v => Math.round(v)); } } return o; }, sels).then(o => { R[n] = o; });
  const notoast = () => p.evaluate(() => document.getElementById('toast').classList.remove('on'));
  await p.goto('file://' + FILE); await sleep(1500);
  await rects('gate', { today: '#gToday', saju: '.door-saju', tarot: '.door-tarot' }); await shot('gate');
  await p.evaluate(() => window.scrollTo(0, 560)); await sleep(300); await shot('gate_doors'); await top(0);
  // 사주
  await p.click('[data-go=saju]'); await sleep(700);
  await p.fill('#nm', '김하늘'); await p.click('#gender [data-v=F]');
  await p.fill('#bd', '19880321'); await p.dispatchEvent('#bd', 'input'); await sleep(1600);
  await top(0); await sleep(200); await rects('saju_form', { nm: '#nm', gender: '#gender', bd: '#bd', pick: '#saju .dpick' }); await shot('saju_form');
  const y1 = await p.evaluate(() => document.querySelector('#result').getBoundingClientRect().top + scrollY - 12);
  await top(y1); await sleep(300); await rects('saju_result', { who: '#who', pls: '#pls', me: '#pls .pl.me', ohs: '#ohs' }); await shot('saju_result');
  const y2 = await p.evaluate(() => document.querySelector('#result .card:nth-of-type(2)').getBoundingClientRect().top + scrollY - 12);
  await top(y2); await sleep(300); await rects('saju_fortune', { ring: '.ring', head: '#head', meters: '#meters', lucky: '#lucky', du: '#du' }); await shot('saju_fortune');
  await el('#result .card:nth-of-type(1)', 'saju_card1');
  await el('#result .card:nth-of-type(2)', 'saju_card2');
  await el('#result .card.send', 'saju_send');
  let [dl] = await Promise.all([p.waitForEvent('download'), p.click('#bImg')]); await dl.saveAs(path.join(OUT, 'saju_share.png'));
  // 타로
  await p.click('#saju .cross'); await sleep(800); await top(0); await notoast(); await sleep(200); await rects('tarot_form', { form: '.t-form .row', birth: '#tBirth', go: '#tGo' });
  await shot('tarot_form');
  await p.click('#tGo'); await sleep(900);
  const ys = await p.evaluate(() => document.getElementById('stage').getBoundingClientRect().top + scrollY - 90);
  await top(ys); await sleep(300); await rects('tarot_spread', { msg: '#tmsg', slot0: '#slot0', slot3: '#slot3' }); await shot('tarot_spread');
  for (let k = 0; k < 4; k++) { const cs = await p.$$('.tc.sp'); await cs[14 + k * 12].click({ force: true }); await sleep(400); }
  await sleep(800);
  await top(ys); await sleep(300); await shot('tarot_picked');
  await el('#stage', 'tarot_stage');
  await el('#trd0', 'tarot_read0'); await el('#trd1', 'tarot_read1');
  const yr = await p.evaluate(() => document.getElementById('trd0').getBoundingClientRect().top + scrollY - 16);
  await top(yr); await sleep(300); await shot('tarot_reads');
  await p.click('#trd2 .trd-card'); await sleep(600); await shot('tarot_zoom'); await p.keyboard.press('Escape'); await sleep(300);
  await notoast(); const yt = await p.evaluate(() => document.getElementById('tsum').getBoundingClientRect().top + scrollY - 16);
  await top(yt); await sleep(300); await shot('tarot_sum');
  await el('#tsum', 'tarot_sum_card');
  [dl] = await Promise.all([p.waitForEvent('download'), p.click('#tImg')]); await dl.saveAs(path.join(OUT, 'tarot_share.png'));
  const picks = await p.evaluate(() => [...document.querySelectorAll('.tc.picked .fc')].map(f => f.getAttribute('aria-label')));
  fs.writeFileSync(path.join(OUT, 'rects.json'), JSON.stringify(R, null, 1));
  console.log('picks', picks, 'errors', errs);
  await b.close();
})();
