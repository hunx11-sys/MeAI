// 연습 화면 점검 : 가장 엄격한 보안정책(CSP)을 거는 작은 서버를 띄워 examples/sandbox.html 을 열고
// CSP 위반 · 콘솔 오류 · 바깥 요청 · 핵심 흐름(출석 · 고객 열기 · 맞춤대화 → 세트)을 본다.
// 쓰는 법 : node home_nudge/tools/check_sandbox.js [home_nudge 폴더]
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const REPO_UI = path.resolve(ROOT, '..', 'ui');
const CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; font-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'self'";
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
let fail = 0; const ok = (c, m) => { console.log((c ? '✓ ' : '✗ ') + m); if (!c) fail++; };
const srv = http.createServer((q, s) => {
  let u = decodeURIComponent(q.url.split('?')[0]);
  let f = u.startsWith('/ui/') ? path.join(REPO_UI, u.slice(4)) : path.join(ROOT, u);
  if (!f.startsWith(ROOT) && !f.startsWith(REPO_UI)) { s.writeHead(403); return s.end(); }
  fs.readFile(f, (e, d) => {
    if (e) { s.writeHead(404); return s.end('없음'); }
    s.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Content-Security-Policy': CSP, 'X-Content-Type-Options': 'nosniff' });
    s.end(d);
  });
}).listen(0, async () => {
  const port = srv.address().port, base = 'http://127.0.0.1:' + port;
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [], ext = [];
  await p.addInitScript(() => { document.addEventListener('securitypolicyviolation', (e) => console.error('CSP ' + e.violatedDirective + ' ' + (e.blockedURI || '') + ' ' + (e.sourceFile || '') + ':' + (e.lineNumber || ''))); });
  p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('pageerror', (e) => errs.push('pageerror ' + e.message));
  p.on('request', (r) => { if (!r.url().startsWith(base) && !r.url().startsWith('data:') && !r.url().startsWith('blob:')) ext.push(r.url()); });
  await p.goto(base + '/examples/sandbox.html');
  await p.waitForSelector('.nz-dock .nz-di', { timeout: 8000 });
  await p.waitForTimeout(1200);
  await p.click('.nz-di[data-k="attend"]'); await p.waitForTimeout(300); await p.click('[data-act="attend"]'); await p.waitForTimeout(3500);
  for (let i = 0; i < 6 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(400); }
  await p.click('article[data-nz-reco="c-501"] [data-open-reco]'); await p.waitForTimeout(600);
  await p.click('article[data-nz-reco="c-501"] [data-chat]'); await p.waitForTimeout(4200);
  for (let i = 0; i < 8 && await p.$('.nz-scrim'); i++) { await p.keyboard.press('Escape'); await p.waitForTimeout(500); }
  const h = await p.evaluate(() => MeAINudge.home());
  ok(h.attendedToday, '출석 도장');
  ok(h.reco.issued['c-501'] && h.reco.issued['c-501'].lotto, '추천 고객 맞춤대화 → 세트 발급 (issueOn = chat.custom)');
  const img = await p.evaluate(() => { const i = document.querySelector('.nz-buddy img'); return i ? i.naturalWidth : -1; });
  ok(img !== 0, '걱정인형 그림이 파일로 불러와짐');
  await p.evaluate(() => MeAINudge._nz.dash.open()); await p.waitForTimeout(800); await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  await p.evaluate(() => MeAINudge._nz.talks.open()); await p.waitForTimeout(800); await p.keyboard.press('Escape');
  ok(errs.filter((e) => e.startsWith('CSP')).length === 0, '가장 엄격한 CSP 위반 0건' + (errs.length ? ' : ' + errs.slice(0, 4).join(' | ') : ''));
  ok(errs.length === 0, '콘솔 오류 0건');
  ok(ext.length === 0, '바깥 주소 요청 0건' + (ext.length ? ' : ' + ext.slice(0, 3).join(' ') : ''));
  await b.close(); srv.close();
  console.log(fail ? '\n실패 ' + fail : '\n모두 통과'); process.exit(fail ? 1 : 0);
});
