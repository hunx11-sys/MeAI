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
      dockFit: (() => { const d = document.querySelector('.nz-dock'), m = d.lastElementChild; return m.getBoundingClientRect().right <= d.getBoundingClientRect().right + 0.5; })() };
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
  // 행운 존 : 허브 → 룰렛 → 고객 슬롯 → OX 챌린지 → 타로 → 스크래치 → 운세 → 피버
  const esc = async () => { for (let i = 0; i < 8 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(350); } };
  await p.click('.nz-di[data-k="fun"]'); await p.waitForTimeout(500); await shot('22_fun');
  ok(await p.$$eval('.nz-ftile', (x) => x.length) === 6, '행운 존 카드 : 게임 6칸 · 빙고판');
  await p.click('[data-g="roulette"]'); await p.waitForTimeout(700); await shot('23_roulette');
  await p.click('[data-spin]'); await p.waitForTimeout(1800); await shot('24_roulette_spin'); await p.waitForTimeout(3600); await shot('25_roulette_result');
  h = await p.evaluate(() => MeAINudge.home());
  ok(h.fun.roulette.spins.length === 1 && h.fun.plays.roulette.left >= 0, '룰렛 1회 · 결과 칸 「' + (h.fun.roulette.spins[0] || {}).label + '」');
  if (await p.$('.nz-roul [data-gact="done"]')) {
    await p.click('.nz-roul [data-gact="copy"]'); await p.waitForTimeout(300);
    await p.click('.nz-roul [data-gact="done"]'); await p.waitForTimeout(800); await shot('26_roulette_done');
    h = await p.evaluate(() => MeAINudge.home());
    ok(h.fun.roulette.spins[0].customers.some((c) => c.done), '룰렛 고객 「연락했어요」 → 챙김 표시 · XP');
  }
  await esc();
  await p.evaluate(() => MeAINudge._nz.fun.go('cslot')); await p.waitForTimeout(600);
  await p.click('[data-pull]'); await p.waitForTimeout(900); await shot('27_cslot_spin'); await p.waitForTimeout(2600); await shot('28_cslot_result');
  h = await p.evaluate(() => MeAINudge.home());
  ok(h.fun.cslot.pulls.length === 1 && h.fun.cslot.pulls[0].customers.length === 3, '고객 슬롯 : 3명 · ' + (h.fun.cslot.pulls[0] || {}).tier);
  await esc();
  await p.evaluate(() => MeAINudge._nz.fun.go('challenge')); await p.waitForTimeout(600); await shot('29_ox_intro');
  await p.click('[data-start]'); await p.waitForTimeout(2300); await shot('30_ox_q');
  for (let i = 0; i < 5; i++) {
    const a = await p.evaluate(() => { const q = document.querySelector('.nz-oxc .q').textContent; const it = window.NZ_DATA.ox.items.filter((x) => x.q === q)[0]; return it ? it.a : 'O'; });
    await p.click('.nz-oxc [data-ans="' + a + '"]'); await p.waitForTimeout(500);
    if (i === 0) await shot('31_ox_answer');
    await p.click('.nz-oxc [data-next]'); await p.waitForTimeout(i === 4 ? 1400 : 300);
  }
  await shot('32_ox_result');
  h = await p.evaluate(() => MeAINudge.home());
  ok(h.fun.challenge.runsToday === 1 && h.fun.challenge.best >= 100 && h.fun.challenge.perfectToday, 'OX 챌린지 5문제 만점 · 최고 ' + h.fun.challenge.best + '점');
  await esc();
  await p.evaluate(() => MeAINudge._nz.fun.go('tarot')); await p.waitForTimeout(600); await shot('33_tarot');
  await p.click('.nz-tarot [data-pick="1"]'); await p.waitForTimeout(2200); await shot('34_tarot_card');
  const tw = await p.evaluate(() => { const i = document.querySelector('.nz-tarot .tc.me img'); return i ? i.naturalWidth : -1; });
  ok(tw > 0, '오늘의 타로 : 원판 그림 · 풀이 (' + tw + 'px)');
  await esc();
  await p.evaluate(() => MeAINudge._nz.fun.go('scratch')); await p.waitForTimeout(600); await shot('35_scratch');
  const cv = await p.$('.nz-scr canvas');
  if (cv) {
    const bb = await cv.boundingBox();
    await p.mouse.move(bb.x + 20, bb.y + 30); await p.mouse.down();
    for (let k = 0; k < 6; k++) { await p.mouse.move(bb.x + bb.width - 20, bb.y + 30 + k * 36, { steps: 8 }); await p.mouse.move(bb.x + 20, bb.y + 48 + k * 36, { steps: 8 }); }
    await p.mouse.up(); await p.waitForTimeout(400); await shot('36_scratching');
    if (await p.$('.nz-scr [data-all]')) await p.click('.nz-scr [data-all]');
    await p.waitForTimeout(1200); await shot('37_scratch_win');
  }
  h = await p.evaluate(() => MeAINudge.home());
  ok(h.fun.scratch.today.length === 1, '스크래치 복권 긁기 → ' + ((h.fun.scratch.today[0] || {}).label || '없음'));
  await esc();
  await p.evaluate(() => MeAINudge._nz.fun.go('fortune-card')); await p.waitForTimeout(700); await shot('38_fortune');
  ok(await p.evaluate(() => /오늘의 대화 한마디/.test(document.querySelector('.nz-fort2').textContent)), '오늘의 운세 : 사주 점수 · 대화 한마디');
  await esc();
  await p.evaluate(() => MeAINudge._nz.api.demo.setTime('2026-10-29', '14:05').then((x) => MeAINudge._nz.setHome(x))); await p.waitForTimeout(800);
  ok(await p.$('.nz-di-fun.fever') !== null, '14시 오후 피버 : 막대에 피버 ×2 표시');
  await p.click('.nz-di[data-k="fun"]'); await p.waitForTimeout(500); await shot('39_fever_fun');
  await p.keyboard.press('Escape');
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
