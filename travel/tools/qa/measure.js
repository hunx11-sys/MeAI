// 지금 화면 측정 : 첫 화면·목적지 화면의 길이, 주요 요소 위치, 44px 미만 탭 대상, 15px 미만 글자, 핀 사이 거리
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const html = process.argv[2];
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ko-KR' });
  const page = await ctx.newPage();
  await page.route(/^https?:/, r => r.abort());
  await page.goto('file://' + path.resolve(html) + '#home', { waitUntil: 'load' });
  await page.waitForTimeout(600);
  const stat = () => page.evaluate(() => {
    const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
    const y = sel => { const e = document.querySelector(sel); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null; };
    const taps = [...document.querySelectorAll('button,a,[role=button],summary,[data-act]')].filter(vis);
    const small = taps.filter(el => { const r = el.getBoundingClientRect(); return r.height < 44 || r.width < 44; });
    // 글자 크기별 글자 수
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const bySize = {}; let total = 0;
    while (walker.nextNode()) { const n = walker.currentNode; const t = n.textContent.replace(/\s+/g, ''); if (!t) continue; const p = n.parentElement; if (!p || !vis(p) || p.closest('svg,script,style')) continue; const fs = parseFloat(getComputedStyle(p).fontSize); const k = fs < 12 ? '<12' : fs < 15 ? '12-14.9' : '>=15'; bySize[k] = (bySize[k] || 0) + t.length; total += t.length; }
    return { H: document.documentElement.scrollHeight, vh: innerHeight, taps: taps.length, small: small.length, smallEx: [...new Set(small.map(el => el.className && typeof el.className === 'string' ? el.className.split(' ')[0] : el.tagName))].slice(0, 12), chars: total, bySize,
      y_search: y('.search, #q'), y_map: y('.mapcard'), y_filters: y('.filters'), y_firstcard: y('.dcard'), cards: document.querySelectorAll('.dcard').length,
      cardH: (() => { const c = [...document.querySelectorAll('.dcard')].map(e => e.getBoundingClientRect().height); return c.length ? Math.round(c.reduce((a, b) => a + b, 0) / c.length) : 0; })(),
      y_pick: y('.pick'), y_dgrid: y('.dgrid'), y_stops: y('.stops'), stops: document.querySelectorAll('.stops > li').length, y_accs: y('.accs') };
  });
  const home = await stat();
  // 핀 사이 화면 거리(전체 지도)
  const pins = await page.evaluate(() => [...document.querySelectorAll('#jpmap .cpin')].map(g => { const c = g.querySelector('.pc').getBoundingClientRect(); return { k: g.dataset.v, x: c.left + c.width / 2, y: c.top + c.height / 2, hit: Math.round(g.querySelector('.ph').getBoundingClientRect().width) }; }));
  const close = [];
  for (let i = 0; i < pins.length; i++) for (let j = 0; j < i; j++) { const d = Math.hypot(pins[i].x - pins[j].x, pins[i].y - pins[j].y); if (d < 44) close.push(pins[i].k + '-' + pins[j].k + ':' + Math.round(d)); }
  const mapBox = await page.evaluate(() => { const r = document.querySelector('#jpmap svg').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; });
  console.log('HOME', JSON.stringify(home));
  console.log('MAP px', mapBox, 'pin hit px', pins[0] && pins[0].hit, 'pairs<44px', close.length, close.join(' '));
  for (const k of ['kyoto', 'hakodate', 'fukuoka']) {
    await page.goto('file://' + path.resolve(html) + '#' + k, { waitUntil: 'load' });
    await page.waitForTimeout(500);
    console.log('DEST ' + k, JSON.stringify(await stat()));
  }
  await browser.close();
})();
