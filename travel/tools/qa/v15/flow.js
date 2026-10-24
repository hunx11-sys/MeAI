const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const [,, html, out] = process.argv;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ ...devices['iPhone 13'] });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const R = {}; const hash = () => p.evaluate(() => location.hash);
  await p.goto('file://' + path.resolve(html)); await p.waitForTimeout(400);
  R.start = await hash();
  await p.click('.ncard[data-v="3"]'); await p.waitForTimeout(500); R.afterNights = await hash();
  await p.click('.obtn[data-v="PUS"]'); await p.waitForTimeout(400); R.afterOrigin = await hash();
  R.pillText = await p.$$eval('.pills .pill', e => e.map(x => x.innerText.replace(/\s+/g, ' ')));
  await p.click('.rl[data-v="간사이"]', { force: true }); await p.waitForTimeout(700); R.afterRegion = await hash();
  await p.screenshot({ path: out + '/f_region.png' });
  await p.click('.cp[data-v="kyoto"] .pc', { force: true }); await p.waitForTimeout(250); R.pingo = await p.$eval('#pingo', e => e.innerText.trim());
  await p.click('.pingob'); await p.waitForTimeout(500); R.afterCity = await hash();
  R.cityNights = await p.$eval('[data-act="sh-n"]', e => e.innerText.replace(/\s+/g, ' '));
  await p.click('.tabbar [data-v="food"]'); await p.waitForTimeout(300); R.afterTab = await hash();
  await p.goBack(); await p.waitForTimeout(400); R.back1 = await hash();
  await p.goBack(); await p.waitForTimeout(400); R.back2 = await hash();
  await p.goBack(); await p.waitForTimeout(400); R.back3 = await hash();
  // 앱 뒤로 버튼(쌓인 기록 없이 바로 들어온 경우)
  const p2 = await ctx.newPage(); p2.on('pageerror', e => errs.push(e.message));
  await p2.goto('file://' + path.resolve(html) + '#nara'); await p2.waitForTimeout(400);
  await p2.click('.topbar [data-act="back"]'); await p2.waitForTimeout(500); R.directBack = await p2.evaluate(() => location.hash);
  await p2.click('.topbar [data-act="back"]'); await p2.waitForTimeout(500); R.directBack2 = await p2.evaluate(() => location.hash);
  // 김포 출발 : 직항 없는 지역 → 시트
  await p2.evaluate(() => { localStorage.clear(); });
  await p2.goto('file://' + path.resolve(html) + '#map'); await p2.waitForTimeout(300);
  await p2.click('[data-act="sh-o"]'); await p2.waitForTimeout(400); await p2.click('#sheet .obtn[data-v="GMP"]'); await p2.waitForTimeout(500);
  R.gmpPills = await p2.$$eval('.rl.zero', e => e.length);
  await p2.click('.rl[data-v="규슈"]', { force: true }); await p2.waitForTimeout(500);
  R.noDirectSheet = await p2.evaluate(() => document.getElementById('sh-t').textContent);
  await p2.screenshot({ path: out + '/f_nodirect.png' }); await p2.goBack(); await p2.waitForTimeout(300);
  // 검색 Enter
  await p2.goto('file://' + path.resolve(html) + '#home'); await p2.waitForTimeout(300);
  await p2.click('.quick'); await p2.waitForTimeout(300); await p2.fill('#q', 'ㅅㅍㄹ'); await p2.waitForTimeout(100); await p2.press('#q', 'Enter'); await p2.waitForTimeout(400); R.searchEnter = await p2.evaluate(() => location.hash);
  // 다시 첫 화면 : 이어 보기 카드
  await p2.goto('file://' + path.resolve(html) + '#home'); await p2.waitForTimeout(300); R.resume = await p2.$eval('.resume', e => e.innerText.replace(/\s+/g, ' ')).catch(() => '');
  // 작은 탭 목표 · 작은 글자 (주요 화면)
  const met = {};
  for (const r of ['home', 'from', 'map', 'map/kansai', 'kyoto', 'kyoto/food', 'kyoto/prep']){
    await p2.goto('file://' + path.resolve(html) + '#' + r); await p2.waitForTimeout(300);
    met[r] = await p2.evaluate(() => {
      const small = [...document.querySelectorAll('button,a,[role="button"],[data-act]')].filter(e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0 && (b.height < 43.5 || b.width < 43.5) && !e.closest('svg'); }).map(e => (e.className.baseVal !== undefined ? e.className.baseVal : e.className) + ':' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height));
      let tiny = 0; const w = document.createTreeWalker(document.querySelector('.scr') || document.body, NodeFilter.SHOW_TEXT);
      while (w.nextNode()){ const t = w.currentNode; if (!t.textContent.trim() || t.parentElement.closest('svg,.leaflet-container,footer')) continue; const fs = parseFloat(getComputedStyle(t.parentElement).fontSize); if (fs < 12) tiny += t.textContent.trim().length; }
      const first = document.querySelector('.tl .row'); return { small: small.slice(0, 8), nSmall: small.length, tinyChars: tiny, firstRowY: first ? Math.round(first.getBoundingClientRect().top + scrollY) : null, firstScreenChars: (() => { let n = 0; const w2 = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); while (w2.nextNode()){ const r = w2.currentNode.parentElement.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0 && !w2.currentNode.parentElement.closest('svg')) n += w2.currentNode.textContent.replace(/\s/g, '').length; } return n; })() };
    });
  }
  console.log(JSON.stringify({ R, met, errs }, null, 1));
  await b.close();
})();
