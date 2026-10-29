// 사주 결과 대조 : v1(fortune/legacy)과 새 판(dist)의 사주 칸 값이 같은지 날짜 120개 × 남/여로 비교
// 쓰는 법 : node fortune/tools/regress_saju.js fortune/legacy/unse_v1_261016.html dist/unse_saju_tarot.html  (절대 경로로 넘긴다)
const { chromium } = require('playwright');
(async () => {
  const [,, OLD, NEW] = process.argv;
  const b = await chromium.launch();
  const open = async f => { const p = await b.newPage({ viewport: { width: 400, height: 860 } }); await p.goto('file://' + f + '#saju'); await p.waitForTimeout(800); return p; };
  const po = await open(OLD), pn = await open(NEW);
  const dates = ['19360101', '19360204', '19451231', '19600815', '19700204', '19700205', '19800101', '19850315', '19900928', '19991231', '20000101', '20040204', '20100505', '20201231', '20240229', '20261029', '20270115', '20350606', '20461231'];
  let seed = 7; const rnd = n => (seed = (seed * 1103515245 + 12345) % 2147483648) % n;
  while (dates.length < 120) { const y = 1936 + rnd(111), m = 1 + rnd(12), d = 1 + rnd(28); dates.push('' + y + String(m).padStart(2, '0') + String(d).padStart(2, '0')); }
  const grab = async (p, d, g) => {
    await p.evaluate(g => { const b = document.querySelector('#gender [data-v="' + g + '"]'); b.click(); }, g);
    await p.fill('#bd', ''); await p.fill('#bd', d); await p.dispatchEvent('#bd', 'input'); await p.waitForTimeout(40);
    return p.evaluate(() => {
      const t = id => (document.getElementById(id) || {}).textContent;
      const pl = [...document.querySelectorAll('#pls .pl')].map(e => [...e.querySelectorAll('.lb,.god,.c,.k')].map(x => x.textContent).join('|'));
      return { pl, warn: t('warn'), head: t('head'), keys: t('keys'), lines: t('lines'), meters: t('meters'), lucky: t('lucky'), du: t('du'), tgDu: t('tgDu'), tgDay: t('tgDay'), gz: document.querySelector('#who .gz').textContent,
        bd: document.querySelector('#who .bd').textContent, unborn: t('unborn'), score: document.getElementById('ringFg').style.strokeDashoffset ? 'x' : 'x' };
    });
  };
  let n = 0, bad = [];
  for (const d of dates) for (const g of ['M', 'F']) {
    const a = await grab(po, d, g), c = await grab(pn, d, g); n++;
    for (const k of Object.keys(a)) if (JSON.stringify(a[k]) !== JSON.stringify(c[k])) bad.push([d, g, k, a[k], c[k]]);
  }
  console.log('비교', n, '건 · 다른 칸', bad.length); bad.slice(0, 8).forEach(x => console.log(JSON.stringify(x).slice(0, 400)));
  await b.close();
})();
