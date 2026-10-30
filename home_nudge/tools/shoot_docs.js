// 설계도 그림 만들기 : 목업을 열어 번호 붙인 홈 배치 · 카드 견본 · 연출 견본을 docs/img/ 에 저장한다.
// 쓰는 법 : node home_nudge/tools/shoot_docs.js [목업.html]   (목업을 다시 만든 뒤)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const PKG = path.join(__dirname, '..', 'mockup', 'meai_home_nudge_v5.html');
const FILE = path.resolve(process.argv[2] || (fs.existsSync(PKG) ? PKG : path.join(__dirname, '..', '..', 'dist', 'meai_home_nudge_v5.html')));
const OUT = path.join(__dirname, '..', 'docs', 'img');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  await p.goto('file://' + FILE + '#/mg-gate-010');
  await p.waitForSelector('.nz-dock .nz-di'); await p.waitForTimeout(1600);
  // ① ~ ⑥ 번호
  await p.evaluate(() => {
    const mk = (sel, n, dx, dy) => { const e = document.querySelector(sel); if (!e) return; const r = e.getBoundingClientRect(); const d = document.createElement('div');
      d.textContent = n; Object.assign(d.style, { position: 'fixed', left: (r.left + (dx || 0) - 13) + 'px', top: (r.top + (dy || 0) - 13) + 'px', width: '26px', height: '26px', borderRadius: '50%', background: '#2563c9', color: '#fff', font: '700 14px/26px sans-serif', textAlign: 'center', zIndex: 2147483600, boxShadow: '0 0 0 3px #fff, 0 2px 6px rgba(0,0,0,.3)' }); document.body.appendChild(d); };
    mk('.nz-capb', '1', 0, 0); mk('.nz-dashb', '2', 0, 0); mk('.nz-buddy', '3', 0, 0); mk('.nz-dock', '4', 0, 0); mk('.nz-rechint', '5', 0, 0); mk('.nz-recb', '6', 0, 0);
  });
  await p.screenshot({ path: path.join(OUT, 'home_1440.png') });
  await p.evaluate(() => document.querySelectorAll('body > div[style*="2147483600"]').forEach((d) => d.remove()));
  const card = async (k, name, pre) => {
    if (pre) await pre();
    await p.click('.nz-di[data-k="' + k + '"], .nz-capb[data-k="' + k + '"]'); await p.waitForTimeout(700);
    const r = await p.evaluate(() => { const e = document.querySelector('.nz-pop.on .nz-card'); const b = e.getBoundingClientRect(); return { x: b.left - 8, y: b.top - 8, width: b.width + 16, height: b.height + 16 }; });
    await p.screenshot({ path: path.join(OUT, name + '.png'), clip: r });
    await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  };
  await card('quest', 'card_quest'); await card('attend', 'card_attend'); await card('quiz', 'card_quiz'); await card('talk', 'card_talk');
  await card('lotto', 'card_lotto'); await card('league', 'card_league'); await card('wallet', 'card_wallet'); await card('fun', 'card_fun');
  // 넛지 설정 (행운 존 카드 아래 → 설정)
  await p.click('.nz-di[data-k="fun"]'); await p.waitForTimeout(500); await p.click('.nz-pop [data-open="more"]'); await p.waitForTimeout(600);
  { const r = await p.evaluate(() => { const e = document.querySelector('.nz-pop.on .nz-card'); const b = e.getBoundingClientRect(); return { x: b.left - 8, y: b.top - 8, width: b.width + 16, height: b.height + 16 }; }); await p.screenshot({ path: path.join(OUT, 'card_more.png'), clip: r }); }
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  // 행운 존 게임 화면
  const esc = async () => { for (let i = 0; i < 6 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(350); } };
  const game = async (g, name, act) => {
    await p.evaluate((g) => MeAINudge._nz.fun.go(g), g); await p.waitForTimeout(700); if (act) await act();
    const r = await p.evaluate(() => { const e = document.querySelector('.nz-scrim .nz-game'); e.scrollTop = 0; const b = e.getBoundingClientRect(); return { x: Math.max(0, b.left - 8), y: Math.max(0, b.top - 8), width: b.width + 16, height: Math.min(b.height + 16, 900 - Math.max(0, b.top - 8)) }; });
    await p.screenshot({ path: path.join(OUT, name + '.png'), clip: r }); await esc();
  };
  await game('roulette', 'fun_roulette', async () => { await p.click('[data-spin]'); await p.waitForTimeout(5600); });
  await game('cslot', 'fun_cslot', async () => { await p.click('[data-pull]'); await p.waitForTimeout(3600); });
  await game('challenge', 'fun_ox', async () => { await p.click('[data-start]'); await p.waitForTimeout(2300); const a = await p.evaluate(() => { const q = document.querySelector('.nz-oxc .q').textContent; const it = window.NZ_DATA.ox.items.filter((x) => x.q === q)[0]; return it ? it.a : 'O'; }); await p.click('.nz-oxc [data-ans="' + a + '"]'); await p.waitForTimeout(700); });
  await game('tarot', 'fun_tarot', async () => { await p.click('.nz-tarot [data-pick="1"]'); await p.waitForTimeout(2400); });
  await game('scratch', 'fun_scratch', async () => { if (await p.$('.nz-scr [data-all]')) { await p.click('.nz-scr [data-all]'); await p.waitForTimeout(1500); } });
  await game('fortune-card', 'fun_fortune', null);
  await p.evaluate(() => { MeAINudge.fx([{ type: 'bingo', lines: [0], fresh: [0], count: 1, filled: 4 }]); }); await p.waitForTimeout(1100);
  await p.screenshot({ path: path.join(OUT, 'fx_bingo.png'), clip: { x: 420, y: 250, width: 600, height: 360 } }); await esc();
  // 연출 : 슬롯 · 일일 미션
  await p.evaluate(() => { MeAINudge._nz.fx.slot({ nums: [3, 11, 19, 27, 34, 42], nth: 5 }); }); await p.waitForTimeout(3300);
  await p.screenshot({ path: path.join(OUT, 'fx_slot.png'), clip: { x: 420, y: 150, width: 600, height: 520 } }); await p.keyboard.press('Escape'); await p.waitForTimeout(600);
  await p.evaluate(() => { MeAINudge.fx([{ type: 'mission' }]); }); await p.waitForTimeout(900);
  await p.screenshot({ path: path.join(OUT, 'fx_mission.png'), clip: { x: 470, y: 180, width: 500, height: 420 } }); await p.keyboard.press('Escape'); await p.waitForTimeout(600);
  await p.evaluate(() => MeAINudge._nz.dash.open()); await p.waitForTimeout(1200);
  await p.screenshot({ path: path.join(OUT, 'dash_me.png') }); await p.keyboard.press('Escape');
  await b.close();
  console.log('docs/img 그림 저장');
})();
