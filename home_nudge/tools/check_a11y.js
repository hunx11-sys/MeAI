// 접근성 점검 (axe-core) : node home_nudge/tools/check_a11y.js <axe-core 폴더> [목업.html]
// 준비 : npm pack axe-core@4.10.2 → 압축을 풀어 package 폴더를 넘긴다. 넛지 부품(막대 · 카드 7종 · 대시보드 · 화법 전체 보기)만 본다.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const AXE = path.join(process.argv[2], 'axe.min.js');
const PKG = path.join(__dirname, '..', 'mockup', 'meai_home_nudge_v5.html');
const FILE = path.resolve(process.argv[3] || (fs.existsSync(PKG) ? PKG : path.join(__dirname, '..', '..', 'dist', 'meai_home_nudge_v5.html')));
let total = 0;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('file://' + FILE + '#/mg-gate-010'); await p.waitForSelector('.nz-dock .nz-di'); await p.waitForTimeout(1200);
  await p.addScriptTag({ path: AXE });
  const run = async (label, sel) => {
    const r = await p.evaluate(async (sel) => { const res = await axe.run({ include: sel.map((s) => [s]) }, { resultTypes: ['violations'] }); return res.violations.map((v) => ({ id: v.id, impact: v.impact, n: v.nodes.length, help: v.help, ex: v.nodes.slice(0, 2).map((x) => x.target.join(' ') + ' :: ' + (x.failureSummary || '').split('\n').slice(1, 2).join(' ')) })); }, sel);
    total += r.length; console.log('[' + label + ']', r.length ? '' : '위반 0'); r.forEach((v) => console.log('  ', v.impact, v.id, v.n, v.help, '\n     ', v.ex.join('\n      ')));
  };
  await run('막대 · 캡슐 · 버디 · 배지', ['.nz-dockwrap', '.nz-cap', '.nz-buddy', '.nz-rechint', '.nz-recb']);
  for (const k of ['quest', 'attend', 'quiz', 'talk', 'lotto', 'league', 'more']) { await p.click('.nz-di[data-k="' + k + '"]'); await p.waitForTimeout(500); await run('카드 ' + k, ['.nz-pop']); }
  await p.keyboard.press('Escape');
  await p.evaluate(() => MeAINudge._nz.dash.open()); await p.waitForTimeout(900); await run('대시보드', ['.nz-dash']); await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  await p.evaluate(() => MeAINudge._nz.talks.open()); await p.waitForTimeout(900); await run('화법 전체 보기', ['.nz-talks']);
  await b.close();
  console.log(total ? '\n위반 ' + total : '\n모두 통과'); process.exit(total ? 1 : 0);
})();
