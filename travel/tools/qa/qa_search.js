// 검색·지역 확대·도시 핀·카드·목적지 '한눈에' 점검. 사용: node qa_search.js <html> <폴더>
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path'), fs = require('fs');
const [,, html, out] = process.argv;
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ko-KR', deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('console ' + m.text()); });
  await page.goto('file://' + path.resolve(html) + '#home', { waitUntil: 'load' });
  await page.waitForTimeout(800);
  fs.mkdirSync(out, { recursive: true });
  await page.screenshot({ path: path.join(out, 'home_top.png') });
  const R = {};
  const qs = ['구마몬', '나하', 'USJ', '교또', '하우스텐보스', '후시미', 'ㅅㅍㄹ', '삿폴', '사포', 'FUK', 'osaka', '라멘', '사슴', '규슈', '온천', '小樽', 'おたる', '오타루', '하카타', 'zzzz', '나'];
  for (const q of qs){
    await page.fill('#q', q);
    await page.waitForTimeout(60);
    R[q] = await page.$$eval('#sres .sitem', els => els.map(e => e.dataset.v + (e.querySelector('em') ? '(' + e.querySelector('em').textContent + ')' : '')).slice(0, 5));
    if (q === '후시미' || q === 'zzzz' || q === 'ㅅㅍㄹ') await page.screenshot({ path: path.join(out, `search_${encodeURIComponent(q)}.png`) });
  }
  await page.click('.sbox .sx');
  // 지도로
  const map = await page.$('.mapcard');
  await map.scrollIntoViewIfNeeded();
  await page.screenshot({ path: path.join(out, 'map_full.png'), clip: await map.boundingBox().then(b => ({ x: 0, y: b.y, width: 390, height: b.height })) }).catch(() => {});
  R.labels_full = await page.$$eval('.jpmap .pl', e => e.map(x => x.textContent));
  for (const rg of ['간사이', '규슈', '오키나와', '홋카이도']){
    await page.click(`.rchips .chip[data-v="${rg}"]`);
    await page.waitForTimeout(700);
    R['labels_' + rg] = await page.$$eval('.jpmap .pl', e => e.map(x => x.textContent));
    R['cards_' + rg] = await page.$$eval('.dcard', e => e.length);
    const m2 = await page.$('.mapcard'); const b = await m2.boundingBox();
    await page.screenshot({ path: path.join(out, `map_${encodeURIComponent(rg)}.png`), clip: { x: 0, y: Math.max(0, b.y), width: 390, height: b.height } });
  }
  // 핀 누르기
  await page.click('.rchips .chip[data-v="간사이"]'); await page.waitForTimeout(700);
  await page.click('.jpmap .cpin[data-v="kyoto"] .pc', { force: true });
  await page.waitForTimeout(200);
  R.tip = await page.$eval('#maptip', e => e.textContent.trim().slice(0, 120)).catch(() => '');
  const m3 = await page.$('.mapcard'); const b3 = await m3.boundingBox();
  await page.screenshot({ path: path.join(out, 'map_tip.png'), clip: { x: 0, y: Math.max(0, b3.y), width: 390, height: b3.height } });
  await page.click('.rchips .chip[data-v=""]'); await page.waitForTimeout(700);
  // 카드
  const c = await page.$('#card-hakodate'); await c.scrollIntoViewIfNeeded(); const cb = await c.boundingBox();
  await page.screenshot({ path: path.join(out, 'card.png'), clip: { x: 0, y: cb.y - 10, width: 390, height: cb.height + 20 } });
  // 목적지
  await page.click('#card-hakodate'); await page.waitForTimeout(900);
  await page.screenshot({ path: path.join(out, 'dest_top.png') });
  await page.evaluate(() => window.scrollTo(0, 600)); await page.waitForTimeout(200);
  await page.screenshot({ path: path.join(out, 'dest_2.png') });
  R.hscroll = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  R.errs = errs;
  console.log(JSON.stringify(R, null, 1));
  await browser.close();
})();
