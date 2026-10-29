// 웹서버판 자동 점검 : 가장 엄격한 보안정책(CSP) 서버에 띄우고 대문 → 사주 → 타로 → 크게 보기 → 이미지 저장까지 돌린다.
//   · CSP 위반 0 · 콘솔 오류 0 · 같은 출처 밖 요청 0 · 저장 이미지(PNG) 2장 · iframe 안에서도 동작
//   · --no-fonts 를 함께 돌려 글꼴이 막힌 회사 정책에서도 화면이 깨지지 않는지 본다
// 쓰는 법 : node fortune/tools/check_web.js <web 폴더>      (node · playwright · python3 필요)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');

const WEB = path.resolve(process.argv[2] || path.join(__dirname, '..', 'web'));
const SERVER = path.join(__dirname, 'csp_test_server.py');
const sleep = ms => new Promise(r => setTimeout(r, ms));

function serve(port, dir, noFonts) {
  const p = spawn('python3', [SERVER, String(port), dir].concat(noFonts ? ['--no-fonts'] : []), { stdio: 'ignore' });
  return sleep(700).then(() => p);
}

async function flow(page, base, out, tag) {
  const r = {};
  await page.goto(base); await sleep(1500);
  r.gate = await page.evaluate(() => document.body.className === 'v-gate' && /丙|甲|乙|丁|戊|己|庚|辛|壬|癸/.test(document.getElementById('gToday').textContent));
  r.fontSerif = await page.evaluate(() => document.fonts.check('700 20px UnseSerif', '오늘'));
  await page.click('[data-go=saju]'); await sleep(700);
  await page.fill('#nm', '홍길동'); await page.fill('#bd', '19900928'); await page.dispatchEvent('#bd', 'input'); await sleep(1800);
  r.saju = await page.evaluate(() => document.querySelectorAll('#pls .pl').length === 3 && !!document.getElementById('scoreN').textContent);
  let [dl] = await Promise.all([page.waitForEvent('download', { timeout: 8000 }).catch(() => null), page.click('#bImg')]);
  if (dl) { const f = path.join(out, tag + '_saju.png'); await dl.saveAs(f); r.sajuPng = fs.statSync(f).size; }
  await page.click('#saju .cross'); await sleep(900);
  await page.click('#tGo'); await sleep(4700);
  for (let k = 0; k < 4; k++) { const cs = await page.$$('.tc.sp'); await cs[8 + k * 13].click({ force: true }); await sleep(1900); }
  await sleep(700);
  r.tarot = await page.evaluate(() => document.querySelectorAll('.trd').length === 4 && document.getElementById('tsum').classList.contains('on'));
  r.cardImg = await page.evaluate(() => /url\(/.test(document.querySelector('.tc.picked .fc .art').style.backgroundImage));
  await page.click('#trd0 .trd-card'); await sleep(700);
  r.zoom = await page.evaluate(() => document.getElementById('lb').classList.contains('on'));
  await page.keyboard.press('Escape'); await sleep(300);
  [dl] = await Promise.all([page.waitForEvent('download', { timeout: 8000 }).catch(() => null), page.click('#tImg')]);
  if (dl) { const f = path.join(out, tag + '_tarot.png'); await dl.saveAs(f); r.tarotPng = fs.statSync(f).size; }
  await page.screenshot({ path: path.join(out, tag + '_tarot.png.view.png') });
  return r;
}

(async () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'unse-check-'));
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'unse-site-'));      // iframe 시험용 : /unse/ + /parent.html
  fs.cpSync(WEB, path.join(root, 'unse'), { recursive: true });
  fs.writeFileSync(path.join(root, 'parent.html'), '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>사내 포털 시험</title></head>' +
    '<body><h1>사내 포털</h1><iframe id="f" src="unse/" title="오늘의 운세" width="400" height="900" allow="clipboard-write; web-share"></iframe></body></html>');
  const b = await chromium.launch();
  let fail = 0;
  for (const [tag, noFonts, port] of [['csp', false, 8791], ['csp_nofont', true, 8792]]) {
    const srv = await serve(port, WEB, noFonts);
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, acceptDownloads: true });
    const csp = [], errs = [], foreign = [];
    await ctx.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window.__csp = window.__csp || []).push(e.violatedDirective + ' ' + e.blockedURI)));
    const page = await ctx.newPage();
    const origin = 'http://127.0.0.1:' + port;
    page.on('request', q => { const u = q.url(); if (!u.startsWith(origin) && !u.startsWith('blob:')) foreign.push(u); });
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    page.on('pageerror', e => errs.push(e.message));
    const r = await flow(page, origin + '/', out, tag);
    const v = await page.evaluate(() => window.__csp || []);
    const fontErr = errs.filter(e => /font/i.test(e)); const otherErr = errs.filter(e => !/font/i.test(e));
    const ok = r.gate && r.saju && r.tarot && r.cardImg && r.zoom && r.sajuPng > 50000 && r.tarotPng > 200000 && !foreign.length && !otherErr.length &&
      (noFonts ? true : (r.fontSerif && !v.length));
    console.log('[' + tag + ']', ok ? '통과' : '실패', JSON.stringify(r), '| CSP 위반', v.length ? v.slice(0, 3) : 0, '| 바깥 요청', foreign.length, '| 오류', otherErr.slice(0, 3), noFonts ? '| (글꼴 차단 경고 ' + v.filter(x => /font/.test(x)).length + '건 · 기본 글꼴로 표시)' : '');
    if (!ok) fail++;
    await ctx.close(); srv.kill();
  }
  // iframe
  const srv = await serve(8793, root, false);
  const ctx = await b.newContext({ viewport: { width: 500, height: 1000 } });
  const page = await ctx.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await page.goto('http://127.0.0.1:8793/parent.html'); await sleep(1800);
  const f = page.frames().find(x => /\/unse\/(index.html)?$/.test(x.url()));
  if (!f) { console.log('[iframe] 실패 · 프레임 없음', page.frames().map(x => x.url())); process.exit(1); }
  await f.click('[data-go=tarot]'); await sleep(900);
  await f.fill('#tbd', '19851224'); await f.dispatchEvent('#tbd', 'input'); await sleep(200);
  await f.click('#tGo'); await sleep(4700);
  for (let k = 0; k < 4; k++) { const cs = await f.$$('.tc.sp'); await cs[10 + k * 12].click({ force: true }); await sleep(1900); }
  const ok = await f.evaluate(() => document.querySelectorAll('.trd').length === 4);
  console.log('[iframe]', ok && !errs.length ? '통과' : '실패', '풀이', ok ? 4 : 0, '| 오류', errs.slice(0, 3));
  if (!(ok && !errs.length)) fail++;
  await page.screenshot({ path: path.join(out, 'iframe.png') });
  await ctx.close(); srv.kill(); await b.close();
  console.log('캡처 · 저장 이미지 :', out);
  process.exit(fail ? 1 : 0);
})();
