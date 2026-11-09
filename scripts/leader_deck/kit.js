// 강의안 공통 부품 : 검은 바탕 · 한 장 한 메시지 · 큰 글자 · 빨간 강조 상자 · 장마다 통이미지(글꼴이 깨지지 않게) + 발표자 메모
// build_leader.js(초급리더과정 60분) · build_fm.js(MeAI × FM 90분) 가 함께 쓴다.
const { chromium } = require('playwright');
const pptxgen = require('pptxgenjs');
const fs = require('fs'), path = require('path');

const REPO = path.resolve(__dirname, '..', '..');
const CAPDIR = path.join(REPO, 'guidebook_v4', 'captures');
const AS = path.join(__dirname, 'assets');
const url = p => 'file://' + p;
const cap = r => url(path.join(CAPDIR, r));
const asset = f => url(path.join(AS, f));

// 캡처 일부만 보이기 : 원본 크기(sw,sh) · 자를 곳(x,y,w,h) · 보일 폭 dw
function crop(src, sw, sh, x, y, w, h, dw, style) {
  const k = dw / w;
  return `<div class="crop" style="width:${Math.round(dw)}px;height:${Math.round(h * k)}px;${style || ''}"><img src="${src}" style="width:${Math.round(sw * k)}px;margin-left:${-Math.round(x * k)}px;margin-top:${-Math.round(y * k)}px"></div>`;
}

// 간지 : 큰 번호(배경) · PART · 빨간 상자 낱말 · 부제 · 한 줄
const sec = (num, word, sub, small) => `
<div class="bgn" style="right:40px;top:40px;font-size:640px">${num}</div>
<div class="box" style="position:absolute;left:140px;top:300px">
  <div class="kick">PART ${num}</div>
  <div style="font-size:200px;font-weight:900;line-height:1.1;letter-spacing:-0.04em;margin-top:24px"><span class="r">${word}</span></div>
  <div class="h3" style="margin-top:44px">${sub}</div>
  <div class="p" style="margin-top:20px">${small}</div>
</div>`;

const css = FONT => `
@font-face { font-family: "P"; src: url("file://${FONT}") format("woff2-variations"); font-weight: 45 920; }
:root { --red: #E60023; --yel: #FFD43B; --g1: #A9ABB0; --g2: #6E7076; --g3: #2A2B2F; --g4: #141416; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #444; font-family: "P", sans-serif; color: #fff; word-break: keep-all; }
.slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #000; margin: 0 0 20px; }
.foot { position: absolute; left: 64px; right: 64px; bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.foot .law { font-size: 12.5px; color: #3c3d41; font-weight: 500; letter-spacing: -0.01em; }
.foot .pg { font-size: 16px; color: #55575c; font-weight: 600; }
.src { position: absolute; left: 64px; bottom: 44px; font-size: 15px; color: #5d5f64; font-weight: 500; letter-spacing: -0.01em; }
.ctr { position: absolute; left: 0; right: 0; top: 0; bottom: 80px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.kick { font-size: 28px; font-weight: 600; color: var(--g1); letter-spacing: 0.02em; }
.h0 { font-size: 132px; font-weight: 900; line-height: 1.16; letter-spacing: -0.04em; }
.h1 { font-size: 96px; font-weight: 900; line-height: 1.24; letter-spacing: -0.035em; }
.h2 { font-size: 72px; font-weight: 800; line-height: 1.36; letter-spacing: -0.03em; }
.h3 { font-size: 56px; font-weight: 700; line-height: 1.5; letter-spacing: -0.025em; }
.h4 { font-size: 40px; font-weight: 700; line-height: 1.5; letter-spacing: -0.02em; }
.p { font-size: 30px; font-weight: 500; color: var(--g1); line-height: 1.6; letter-spacing: -0.015em; }
.ps { font-size: 24px; font-weight: 500; color: var(--g1); line-height: 1.55; letter-spacing: -0.01em; }
.r { background: var(--red); color: #fff; padding: 0 0.14em; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
.y { color: var(--yel); }
.g { color: var(--g2); }
.w { color: #fff; }
.k { text-decoration: line-through; text-decoration-color: #6E7076; text-decoration-thickness: 2px; color: #6E7076; }
.crop { overflow: hidden; position: relative; }
.crop img { display: block; }
.scr { position: absolute; border-radius: 18px; overflow: hidden; box-shadow: 0 0 0 1px rgba(255,255,255,.10), 0 40px 120px rgba(0,0,0,.85), 0 0 160px rgba(255,255,255,.07); }
.spot { position: absolute; border-radius: 50%; background: radial-gradient(closest-side, rgba(255,255,255,.11), rgba(255,255,255,0)); pointer-events: none; }
.bgn { position: absolute; font-weight: 900; color: #101012; letter-spacing: -0.06em; line-height: 1; }
.line { height: 1px; background: #2A2B2F; }
.dh { position: absolute; left: 0; right: 0; top: 110px; text-align: center; font-size: 32px; font-weight: 700; color: #8E9095; letter-spacing: 0.02em; }
.diary { font-size: 64px; font-weight: 700; line-height: 1.62; letter-spacing: -0.03em; }
.tag { display: inline-block; font-size: 22px; font-weight: 700; color: var(--yel); border: 1.5px solid #4a3f12; border-radius: 999px; padding: 4px 16px; }
.num { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; background: var(--red); font-size: 32px; font-weight: 800; flex: none; }
.row { display: flex; align-items: center; }
.bub { display: inline-block; padding: 22px 34px; border-radius: 30px; font-size: 32px; font-weight: 600; line-height: 1.45; letter-spacing: -0.02em; }
`;

// 굽기 : HTML → 장마다 JPG(2880x1620) → PPTX(통이미지 + 발표자 메모) · 점검(글꼴 · 깨진 그림 · 장 밖 · 겹침)
// S : [{h, n, src}] · meta : {FONT, OUT, name, LAW, title, subject, css(덧붙일 스타일, 없어도 됨)}
async function build(S, meta) {
  const { FONT, OUT, name, LAW } = meta;
  const dir = path.join(OUT, name + '_slides'); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const body = S.map((s, i) => `<section class="slide">${s.h}${s.src ? `<div class="src">${s.src}</div>` : ''}<div class="foot"><span class="law">${LAW}</span><span class="pg">${i + 1}</span></div></section>`).join('\n');
  const html = `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>${css(FONT)}${meta.css || ''}</style></head><body>${body}</body></html>`;
  fs.writeFileSync(path.join(OUT, name + '.html'), html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1.5 });
  await p.goto('file://' + path.join(OUT, name + '.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
  const fontOk = await p.evaluate(() => document.fonts.check('800 40px "P"', '가'));
  const broken = await p.evaluate(() => [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src.slice(-60)));
  const over = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s, i) => {
    const R = s.getBoundingClientRect(), bad = [], cl = e => (e.getAttribute('class') || '').split(' ')[0];
    const all = [...s.querySelectorAll('.box,.src,.foot')];
    const top = all.filter(e => !all.some(o => o !== e && o.contains(e)));
    top.forEach(e => { const r = e.getBoundingClientRect(); if (r.left < R.left + 30 || r.right > R.right - 30 || r.top < R.top + 20 || r.bottom > R.bottom - 6) bad.push('밖 ' + cl(e) + '@' + [r.left - R.left, r.top - R.top, r.right - R.left, r.bottom - R.top].map(Math.round).join(',')); });
    for (let a = 0; a < top.length; a++) for (let c = a + 1; c < top.length; c++) { const A = top[a].getBoundingClientRect(), B = top[c].getBoundingClientRect(); if (A.left < B.right - 2 && B.left < A.right - 2 && A.top < B.bottom - 2 && B.top < A.bottom - 2) bad.push('겹침 ' + cl(top[a]) + '×' + cl(top[c]) + '@' + Math.round(A.top - R.top) + '/' + Math.round(B.top - R.top)); }
    return bad.length ? (i + 1) + ': ' + [...new Set(bad)].slice(0, 6).join(' | ') : null;
  }).filter(Boolean));
  const els = await p.$$('.slide'); const files = [];
  for (let i = 0; i < els.length; i++) { const f = path.join(dir, String(i + 1).padStart(2, '0') + '.jpg'); await els[i].screenshot({ path: f, type: 'jpeg', quality: 88 }); files.push(f); }
  await b.close();
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.title = meta.title; pres.author = '세일즈혁신TF'; pres.company = '메리츠화재'; pres.subject = meta.subject;
  files.forEach((f, i) => { const s = pres.addSlide(); s.background = { color: '000000' }; s.addImage({ path: f, x: 0, y: 0, w: 13.333, h: 7.5, altText: S[i].n.split('\n')[0] }); s.addNotes(S[i].n); });
  const pptx = path.join(OUT, name + '.pptx'); await pres.writeFile({ fileName: pptx });
  fs.writeFileSync(path.join(OUT, name + '_files.json'), JSON.stringify(files));
  console.log('글꼴', fontOk, '| 깨진 그림', broken.length ? broken : 0, '| 점검', over.length ? '\n' + over.join('\n') : 0, '\n| 장', files.length, '|', pptx, (fs.statSync(pptx).size / 1048576).toFixed(1) + 'MB');
}

module.exports = { url, cap, asset, crop, sec, css, build, AS };
