// 목업 점검 : node home_nudge/tools/check_mockup.js [목업.html] [캡처 폴더]
// 1440×900 첫 화면 · 콘솔 오류 · 핵심 흐름(출석 → 퀴즈 → 추천 고객 → 화법) · 휴대폰 폭 가로 넘침을 본다.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const PKG = path.join(__dirname, '..', 'mockup', 'meai_home_nudge_v5.html');   // 개발 패키지 안
const FILE = path.resolve(process.argv[2] || (fs.existsSync(PKG) ? PKG : path.join(__dirname, '..', '..', 'dist', 'meai_home_nudge_v5.html')));
const OUT = process.argv[3] || '';
let fail = 0; const ok = (c, m) => { console.log((c ? '✓ ' : '✗ ') + m); if (!c) fail++; };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  p.on('pageerror', (e) => errs.push('pageerror ' + e.message));
  p.on('console', (m) => { if (m.type() === 'error') errs.push('console ' + m.text()); });
  await p.goto('file://' + FILE + '#/mg-gate-010');
  await p.waitForSelector('.nz-dock .nz-di', { timeout: 8000 });
  await p.waitForTimeout(1400);
  const shot = async (n) => { if (OUT) await p.screenshot({ path: path.join(OUT, n + '.png') }); };
  await shot('01_first');
  const geo = await p.evaluate(() => {
    const r = (s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return { y: Math.round(b.top), b: Math.round(b.bottom), w: Math.round(b.width) }; };
    const secs = [...document.querySelectorAll('#root .gate-fontscale section')];
    const h2 = secs[1] && secs[1].querySelector('h2'), card = secs[1] && secs[1].querySelector('.grid > div');
    return { dock: r('.nz-dock'), cap: r('.nz-cap'), reco: h2 ? Math.round(h2.getBoundingClientRect().top) : null, card: card ? Math.round(card.getBoundingClientRect().top) : null,
      items: [...document.querySelectorAll('.nz-dock .nz-di')].map((e) => e.dataset.k), sw: document.documentElement.scrollWidth,
      dockFit: (() => { const d = document.querySelector('.nz-dock'), m = document.querySelector('.nz-di-more'); return m.getBoundingClientRect().right <= d.getBoundingClientRect().right + 0.5; })() };
  });
  console.log(JSON.stringify(geo));
  ok(geo.dock && geo.dock.y < 220, '막대가 인사말 아래 첫 화면 위쪽에 있음 (y=' + (geo.dock && geo.dock.y) + ')');
  ok(geo.card && geo.card < 900, '오늘의 추천 고객 카드가 1440×900 첫 화면 안에서 시작 (y=' + geo.card + ')');
  ok(geo.sw <= 1440, '가로 넘침 없음');
  ok(geo.dockFit, '막대 단추가 막대 안에 모두 들어감');
  // 출석 카드 → 도장
  await p.hover('.nz-di[data-k="attend"]'); await p.waitForTimeout(450); await shot('02_attend_hover');
  await p.click('.nz-di[data-k="attend"]'); await p.waitForTimeout(300);
  await p.click('[data-act="attend"]'); await p.waitForTimeout(900); await shot('03_stamp');
  await p.waitForTimeout(2600); await shot('04_after_attend');
  for (let i = 0; i < 6 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(400); }
  let h = await p.evaluate(() => MeAINudge.home());
  ok(h.attendedToday && h.streak.current === 12, '출석 후 12영업일 연속 (' + h.streak.current + ')');
  ok(h.league.rank === 2, '리그 3위 → 2위 (' + h.league.rank + ')');
  // 퀴즈
  await p.click('.nz-di[data-k="quiz"]'); await p.waitForTimeout(400); await shot('05_quiz');
  await p.click('[data-act="quiz-ans"][data-v="X"]'); await p.waitForTimeout(1400); await shot('06_quiz_result');
  for (let i = 0; i < 6 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(400); }
  h = await p.evaluate(() => MeAINudge.home());
  ok(h.quiz.answered && h.quiz.correct, '퀴즈 정답 처리');
  await p.keyboard.press('Escape');
  // 추천 고객 → 슬롯
  await p.evaluate(() => window.scrollTo(0, 300)); await p.waitForTimeout(300); await shot('07_reco');
  await p.click('#root section:nth-of-type(2) .grid > div'); await p.waitForTimeout(1600); await shot('08_slot');
  await p.waitForTimeout(3600);
  for (let i = 0; i < 8 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(500); }
  h = await p.evaluate(() => MeAINudge.home());
  ok(h.lotto.sets.length === 5, '추천 고객을 열어 로또 1세트 (' + h.lotto.sets.length + '세트)');
  ok(h.quests.done >= 3 && h.quests.mission, '퀘스트 3개 → 일일 미션 (' + h.quests.done + ')');
  // 화법
  await p.evaluate(() => { location.hash = '#/mg-gate-010'; }); await p.waitForTimeout(1200);
  await p.click('.nz-di[data-k="talk"]'); await p.waitForTimeout(500); await shot('09_talk');
  const head = await p.evaluate(() => document.querySelector('.nz-talk-q').textContent);
  await p.type('.nz-copy textarea', head.replace(/[.,!?]/g, ''), { delay: 2 }); await p.waitForTimeout(1500); await shot('10_talk_done');
  for (let i = 0; i < 6 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(400); }
  h = await p.evaluate(() => MeAINudge.home());
  ok(h.talk.copiedToday, '화법 따라 쓰기 완료');
  await p.keyboard.press('Escape');
  // 리그 · 로또 · 대시보드 · 화법 목록
  await p.click('.nz-di[data-k="league"]'); await p.waitForTimeout(500); await shot('11_league');
  await p.click('.nz-di[data-k="lotto"]'); await p.waitForTimeout(500); await shot('12_lotto');
  await p.click('.nz-di[data-k="quest"]'); await p.waitForTimeout(500); await shot('13_quest');
  await p.keyboard.press('Escape');
  await p.click('.nz-dashb'); await p.waitForTimeout(900); await shot('14_dash_me');
  await p.click('.nz-dash [data-tab="org"]'); await p.waitForTimeout(700); await shot('15_dash_org');
  await p.click('.nz-dash [data-tab="hq"]'); await p.waitForTimeout(700); await shot('16_dash_hq');
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  await p.evaluate(() => MeAINudge._nz.talks.open()); await p.waitForTimeout(800); await shot('17_talks');
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  // 금요일 17시 : 추첨 · 리캡
  await p.evaluate(() => MeAINudge._nz.api.demo.setTime('2026-10-30', '17:05').then((x) => MeAINudge._nz.setHome(x))); await p.waitForTimeout(800); await shot('18_friday');
  await p.click('.nz-di[data-k="lotto"]'); await p.waitForTimeout(400); await p.click('[data-act="lotto-draw"]'); await p.waitForTimeout(4800); await shot('19_draw');
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  ok(errs.length === 0, '콘솔 오류 없음' + (errs.length ? ' : ' + errs.slice(0, 5).join(' | ') : ''));
  // 휴대폰
  const m = await b.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await m.goto('file://' + FILE + '#/mg-gate-010'); await m.waitForSelector('.nz-dock .nz-di'); await m.waitForTimeout(1200);
  if (OUT) await m.screenshot({ path: path.join(OUT, '20_mobile.png') });
  const msw = await m.evaluate(() => document.documentElement.scrollWidth);
  ok(msw <= 390 + 1, '휴대폰 390px 가로 넘침 없음 (' + msw + ')');
  await m.tap('.nz-di[data-k="attend"]'); await m.waitForTimeout(600); if (OUT) await m.screenshot({ path: path.join(OUT, '21_mobile_sheet.png') });
  await b.close();
  console.log(fail ? '\n실패 ' + fail : '\n모두 통과');
  process.exit(fail ? 1 : 0);
})();
