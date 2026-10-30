// 오늘의 운세 장표 공통 부품 · 토스(TDS) 시각 언어 · 장마다 통이미지(글꼴이 깨지지 않게)
// build_guide.js(사용 가이드) · build_contest.js(사내 공모전) 가 함께 쓴다.
// 글꼴 : Pretendard (npm pack pretendard@1.3.9, OFL) · 그림 글자 : 토스페이스 (github.com/toss/tossface, 판매 금지 · 자유 사용)
const { chromium } = require('playwright');
const pptxgen = require('pptxgenjs');
const fs = require('fs'), path = require('path');

module.exports = function kit({ CAP, FONT, FACE, FOOT }) {
  const R = JSON.parse(fs.readFileSync(path.join(CAP, 'rects.json'), 'utf8'));
  const img = n => 'file://' + path.join(CAP, n + '.png');

  const PW = 360, SC = PW / 390;                      // 휴대폰 화면 폭 · 캡처(390px) 대비 배율
  function phone(n, opt) {
    opt = opt || {};
    const marks = (opt.marks || []).map(([key, num, dx, dy]) => {
      const r = R[n][key]; const x = 12 + (r[0] + (dx || 0)) * SC, y = 12 + (r[1] + (dy || 0)) * SC;
      return `<b class="mk" style="left:${x - 22}px;top:${y - 22}px">${num}</b>`;
    }).join('');
    return `<div class="phone" style="${opt.style || ''}"><div class="scr"><img src="${img(n)}"></div><i class="isl"></i>${marks}</div>`;
  }
  const chip = t => `<span class="chip">${t}</span>`;
  const PH = Math.round(PW * 844 / 390) + 24, PWO = PW + 24;           // 휴대폰 바깥 크기
  const panel = (x, w) => `<div class="panel" style="left:${x}px;width:${w}px"></div>`;
  const at1 = () => `position:absolute;left:${1000 + (808 - PWO) / 2}px;top:${64 + (952 - PH) / 2}px`;       // 오른쪽 판 가운데
  const at2 = k => `position:absolute;left:${840 + (968 - 2 * PWO - 48) / 2 + k * (PWO + 48)}px;top:${64 + (952 - PH) / 2}px`;  // 넓은 판에 둘
  const asset = (e, cls) => `<span class="asset ${cls || ''}">${e}</span>`;
  const step = (n, t, d) => `<div class="step"><b class="num">${n}</b><div><div class="st">${t}</div>${d ? `<div class="sd">${d}</div>` : ''}</div></div>`;
  const head = (c, t, s) => `<div class="hd">${chip(c)}<h2 class="title">${t}</h2>${s ? `<p class="sub">${s}</p>` : ''}</div>`;
  const foot = n => `<div class="foot"><span>${FOOT}</span><span>${String(n).padStart(2, '0')}</span></div>`;

  const CSS = `
@font-face { font-family: "Pretendard Variable"; src: url("file://${FONT}") format("woff2-variations"); font-weight: 45 920; }
@font-face { font-family: "Tossface"; src: url("file://${FACE}"); }
:root { --blue: #3182F6; --blue50: #E8F3FF; --g900: #191F28; --g800: #333D4B; --g700: #4E5968; --g600: #6B7684; --g500: #8B95A1; --g400: #B0B8C1; --g200: #E5E8EB; --g100: #F2F4F6; --g50: #F9FAFB; }
* { box-sizing: border-box; margin: 0; }
body { background: #ddd; font-family: "Pretendard Variable", "Tossface", sans-serif; color: var(--g900); word-break: keep-all; }
.slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #fff; margin: 0 0 20px; }
.hd { position: absolute; left: 112px; top: 96px; }
.chip { display: inline-flex; align-items: center; height: 46px; padding: 0 22px; border-radius: 999px; background: var(--g100); color: var(--g700); font-size: 22px; font-weight: 600; }
.title { margin-top: 28px; font-size: 64px; font-weight: 700; line-height: 1.28; letter-spacing: -0.03em; }
.sub { margin-top: 18px; font-size: 28px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.panel { position: absolute; top: 64px; height: 952px; border-radius: 48px; background: var(--g100); }
.foot { position: absolute; left: 112px; right: 112px; bottom: 44px; display: flex; justify-content: space-between; font-size: 18px; font-weight: 600; color: var(--g500); letter-spacing: -0.01em; }
.asset { display: inline-flex; align-items: center; justify-content: center; width: 96px; height: 96px; border-radius: 26px; background: var(--g100); font-family: "Tossface"; font-size: 56px; line-height: 1; flex: none; }
.asset.sm { width: 76px; height: 76px; border-radius: 22px; font-size: 44px; }
.info { display: inline-flex; align-items: center; height: 52px; padding: 0 24px; border-radius: 999px; background: var(--blue50); color: var(--blue); font-size: 24px; font-weight: 700; }
.b { color: var(--blue); font-weight: 700; }
/* 휴대폰 */
.phone { position: absolute; width: ${PW + 24}px; padding: 12px; border-radius: 62px; background: #191F28; box-shadow: 0 40px 80px rgba(25, 31, 40, .16), 0 8px 24px rgba(25, 31, 40, .10); }
.phone .scr { width: ${PW}px; height: ${Math.round(PW * 844 / 390)}px; border-radius: 50px; overflow: hidden; background: #000; }
.phone .scr img { display: block; width: 100%; height: 100%; }
.phone .isl { position: absolute; left: 50%; top: 22px; width: 92px; height: 26px; margin-left: -46px; border-radius: 16px; background: #000; }
.mk { position: absolute; width: 44px; height: 44px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 22px; font-weight: 700; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 4px #fff, 0 6px 16px rgba(49, 130, 246, .35); z-index: 3; }
/* 단계 목록 */
.steps { position: absolute; left: 112px; width: 820px; display: flex; flex-direction: column; gap: 34px; }
.steps.tight { gap: 24px; }
.step { display: flex; gap: 24px; align-items: flex-start; }
.num { flex: none; width: 48px; height: 48px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 24px; font-weight: 700; display: flex; align-items: center; justify-content: center; margin-top: 2px; }
.st { font-size: 34px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.35; }
.sd { margin-top: 6px; font-size: 25px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.note { position: absolute; left: 112px; display: inline-flex; align-items: center; min-height: 64px; padding: 14px 28px; border-radius: 20px; background: var(--g100); color: var(--g700); font-size: 24px; font-weight: 600; line-height: 1.45; }
/* 표지 */
.cover .cv-l { position: absolute; left: 112px; top: 120px; width: 760px; }
.cover h1 { margin-top: 40px; font-size: 112px; font-weight: 700; line-height: 1.16; letter-spacing: -0.035em; }
.cover .cv-s { margin-top: 36px; font-size: 36px; font-weight: 500; color: var(--g700); line-height: 1.5; letter-spacing: -0.015em; }
.cover .cv-m { position: absolute; top: 760px; display: flex; flex-direction: column; gap: 26px; align-items: flex-start; }
.cover .meta { font-size: 22px; font-weight: 600; color: var(--g500); }
.cover .cv-r { position: absolute; right: 96px; top: 64px; width: 880px; height: 952px; border-radius: 48px; background: var(--g100); overflow: hidden; }
.cover .asset.float { position: absolute; left: 40px; bottom: 40px; background: #fff; box-shadow: 0 8px 24px rgba(25, 31, 40, .08); }
/* 한눈에 */
.row2 { position: absolute; left: 112px; right: 112px; top: 420px; display: grid; grid-template-columns: 1fr 1.1fr; gap: 64px; }
.stats { display: flex; flex-direction: column; gap: 22px; }
.stat { display: grid; grid-template-columns: 200px 1fr; align-items: center; gap: 24px; padding: 28px 32px; border-radius: 28px; background: var(--g50); border: 1px solid var(--g200); }
.stat b { font-size: 84px; font-weight: 800; color: var(--blue); letter-spacing: -0.04em; line-height: 1; font-variant-numeric: tabular-nums; }
.stat b small { font-size: 40px; font-weight: 700; margin-left: 4px; color: var(--g900); }
.stat span { font-size: 28px; font-weight: 700; line-height: 1.4; }
.stat em { font-style: normal; font-size: 22px; font-weight: 500; color: var(--g600); }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.card { padding: 36px 32px; border-radius: 28px; background: #fff; border: 1px solid var(--g200); box-shadow: 0 4px 12px rgba(25, 31, 40, .04); }
.card .ct { margin-top: 22px; font-size: 32px; font-weight: 700; letter-spacing: -0.02em; }
.card .cd { margin-top: 10px; font-size: 24px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.tags { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
.tags span { height: 42px; padding: 0 18px; border-radius: 999px; background: var(--g100); color: var(--g700); font-size: 20px; font-weight: 600; display: inline-flex; align-items: center; }
/* 여는 방법 · 지켜 주세요 */
.list, .rules { display: flex; flex-direction: column; gap: 18px; }
.lr { display: flex; gap: 28px; align-items: center; padding: 26px 32px; border-radius: 28px; background: #fff; border: 1px solid var(--g200); }
.lt { font-size: 32px; font-weight: 700; letter-spacing: -0.02em; }
.ld { margin-top: 6px; font-size: 23px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.ld code { font-family: inherit; font-weight: 700; color: var(--g800); background: var(--g100); padding: 2px 10px; border-radius: 8px; }
.open { top: 400px; grid-template-columns: 1.15fr .85fr; }
.callout { padding: 40px; border-radius: 32px; background: var(--g100); display: flex; flex-direction: column; align-items: flex-start; }
.callout .ct { margin-top: 24px; font-size: 32px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.35; }
.callout .cd { margin-top: 14px; font-size: 25px; font-weight: 500; color: var(--g700); line-height: 1.6; }
.callout .info { margin-top: 32px; }
.rules { position: absolute; left: 112px; right: 112px; top: 420px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
/* 2x2 카드 */
.grid4 { position: absolute; left: 112px; top: 396px; width: 840px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.grid4 .card { padding: 30px 32px; }
.grid4 .card .ct { margin-top: 18px; font-size: 30px; }
.grid4.pos { left: 112px; top: 384px; width: 820px; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid4.pos .card { padding: 28px 30px 30px; }
.rn { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 20px; background: var(--blue50); color: var(--blue); font-size: 26px; font-weight: 800; letter-spacing: 0.02em; }
.grid4.pos .card .ct { margin-top: 20px; font-size: 32px; }
.shot { position: absolute; border-radius: 28px; overflow: hidden; box-shadow: 0 30px 60px rgba(25, 31, 40, .16), 0 0 0 1px rgba(25, 31, 40, .06); }
.shot img { display: block; width: 100%; }
.fitbox { display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 22px; }
.shot.fit { position: relative; width: 100%; border-radius: 24px; }
.cap2 { font-size: 22px; font-weight: 600; color: var(--g500); }
.cap { position: absolute; text-align: center; font-size: 22px; font-weight: 600; color: var(--g500); }
/* 대화 */
.chat { position: absolute; left: 112px; top: 384px; width: 860px; height: 600px; padding: 28px 40px; border-radius: 36px; background: var(--g50); border: 1px solid var(--g200); display: flex; flex-direction: column; gap: 14px; }
.bb { max-width: 620px; padding: 16px 26px; font-size: 25px; font-weight: 500; line-height: 1.5; letter-spacing: -0.01em; }
.bb.me { align-self: flex-end; background: var(--blue); color: #fff; border-radius: 26px 26px 6px 26px; }
.bb.you { align-self: flex-start; background: var(--g200); color: var(--g900); border-radius: 26px 26px 26px 6px; }
/* 질문 */
.faq { position: absolute; left: 112px; right: 112px; top: 330px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.qa { padding: 36px 34px; border-radius: 28px; background: #fff; border: 1px solid var(--g200); min-height: 250px; }
.q { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.4; }
.q::before { content: 'Q'; display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; margin-right: 14px; border-radius: 12px; background: var(--blue50); color: var(--blue); font-size: 22px; font-weight: 800; vertical-align: 3px; }
.a { margin-top: 18px; font-size: 25px; font-weight: 500; color: var(--g600); line-height: 1.55; }
/* 마무리 */
.end { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.end .asset.hero { width: 140px; height: 140px; border-radius: 40px; font-size: 84px; margin-bottom: 8px; }
.end .title { font-size: 76px; }
.flow { display: flex; align-items: center; gap: 22px; margin-top: 56px; }
.flow span { display: inline-flex; align-items: center; gap: 14px; height: 76px; padding: 0 32px 0 18px; border-radius: 999px; background: var(--g100); font-size: 30px; font-weight: 700; }
.flow span b { display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 22px; }
.flow i { width: 40px; height: 2px; background: var(--g400); }
.end .sub { margin-top: 56px; font-size: 26px; }
`;

  /* 장표를 그림으로 굽고 PPTX(장마다 그림 한 장 + 발표자 메모) · PDF 로 묶는다 */
  async function build(S, { OUT, name, title, subject, extraCss }) {
    const slidesDir = path.join(OUT, name + '_slides');
    fs.rmSync(slidesDir, { recursive: true, force: true });
    fs.mkdirSync(slidesDir, { recursive: true });
    const html = `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>${CSS}${extraCss || ''}</style></head><body>${S.map(s => s.html).join('\n')}</body></html>`;
    fs.writeFileSync(path.join(OUT, name + '.html'), html);
    const b = await chromium.launch();
    const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
    await p.goto('file://' + path.join(OUT, name + '.html'));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(500);
    const fontsOk = await p.evaluate(() => [document.fonts.check('700 40px "Pretendard Variable"', '가'), document.fonts.check('40px Tossface', '🔮')]);
    const over = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s, i) => {
      const R = s.getBoundingClientRect(), bad = [];
      s.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.width && (r.right > R.right + 1 || r.bottom > R.bottom + 1 || r.left < R.left - 1)) bad.push(e.className || e.tagName); });
      return bad.length ? (i + 1) + ':' + [...new Set(bad)].slice(0, 4).join(',') : null;
    }).filter(Boolean));
    const els = await p.$$('.slide');
    const files = [];
    for (let i = 0; i < els.length; i++) {
      const f = path.join(slidesDir, String(i + 1).padStart(2, '0') + '.png');
      await els[i].screenshot({ path: f });
      files.push(f);
    }
    await b.close();
    const pres = new pptxgen();
    pres.layout = 'LAYOUT_WIDE';
    pres.title = title;
    pres.author = '세일즈혁신TF';
    pres.company = 'MeAI';
    pres.subject = subject;
    files.forEach((f, i) => {
      const s = pres.addSlide();
      s.background = { color: 'FFFFFF' };
      s.addImage({ path: f, x: 0, y: 0, w: 13.333, h: 7.5, altText: S[i].notes });
      s.addNotes(S[i].notes);
    });
    const pptx = path.join(OUT, name + '.pptx');
    await pres.writeFile({ fileName: pptx });
    console.log('글꼴', fontsOk, '| 넘침', over.length ? over : 0, '| 장', files.length, '|', pptx, (fs.statSync(pptx).size / 1048576).toFixed(1) + 'MB');
    return files;
  }

  return { R, img, PW, SC, PH, PWO, phone, chip, panel, at1, at2, asset, step, head, foot, CSS, build };
};
