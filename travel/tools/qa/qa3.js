// 전 목적지 × 박 수 × 대체 플랜 × 일차 를 눌러 보며 오류·가로 넘침·빈 지도·빈 식당 후보를 찾는다
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const [,, html] = process.argv;
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ko-KR' });
  await ctx.route(/cartocdn|jsdelivr|googleapis|gstatic/, r => r.abort());
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
  const keys = await page.evaluate(() => [...document.querySelectorAll('.dcard')].map(c => c.dataset.v));
  const problems = []; let views = 0;
  for (const k of keys) {
    await page.evaluate(k => { location.hash = '#' + k; }, k); await page.waitForTimeout(120);
    const nN = await page.$$eval('.nseg button', b => b.length);
    for (let n = 0; n < nN; n++) {
      await page.$$eval('.nseg button', (b, n) => b[n].click(), n); await page.waitForTimeout(40);
      const nV = await page.$$eval('.vchips .chip', b => b.length);
      for (let v = 0; v < Math.max(1, nV); v++) {
        if (nV) { await page.$$eval('.vchips .chip', (b, v) => b[v].click(), v); await page.waitForTimeout(40); }
        const nD = await page.$$eval('.tile', b => b.length);
        for (let d = 0; d < nD; d++) {
          await page.$$eval('.tile', (b, d) => b[d].click(), d); await page.waitForTimeout(30);
          views++;
          const r = await page.evaluate(() => {
            const out = [];
            if (document.documentElement.scrollWidth > window.innerWidth + 1) out.push('가로넘침');
            if (!document.querySelector('.stops li')) out.push('일정없음');
            document.querySelectorAll('.scard h3').forEach(h => { if (!h.textContent.trim()) out.push('빈제목'); });
            document.querySelectorAll('.opts').forEach(o => { if (o.children.length < 1) out.push('식당후보없음'); });
            const m = document.getElementById('daymap'); if (m && !m.querySelector('.sketch, .leaflet-container, .empty')) out.push('지도없음');
            if (/undefined|NaN|\[object/.test(document.getElementById('planarea').innerText)) out.push('undefined/NaN 노출');
            return out;
          });
          if (r.length) problems.push(`${k} 박${n} 대체${v} ${d + 1}일차: ${[...new Set(r)].join(',')}`);
        }
      }
    }
    // 아코디언 전부 열어 undefined 노출 확인
    const acc = await page.evaluate(() => { document.querySelectorAll('details.acc').forEach(d => d.open = true); const t = document.querySelector('.accs').innerText; return /undefined|NaN|\[object/.test(t); });
    if (acc) problems.push(`${k} 아코디언: undefined/NaN 노출`);
  }
  console.log(JSON.stringify({ destinations: keys.length, views, problems: problems.slice(0, 60), nProblems: problems.length, errors: [...new Set(errors)].slice(0, 20) }, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
