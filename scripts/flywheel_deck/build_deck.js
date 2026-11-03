// MeAI 영업 플라이휠 장표 · 메리츠 빨강(#C8102E) + 토스 시각 언어 · 장마다 통이미지 + 발표자 메모
// 쓰는 법 : node build_deck.js <캡처 폴더(W)> <Pretendard 가변 woff2> <출력 폴더>
const path = require('path'), fs = require('fs');
const W = process.argv[2], FONT = process.argv[3], OUT = process.argv[4];
const { chromium } = require('playwright');
const pptxgen = require(path.join(W, 'node', 'node_modules', 'pptxgenjs'));
const SZ = JSON.parse(fs.readFileSync(path.join(W, 'sizes.json'), 'utf8'));
const ROOT = path.resolve(__dirname, '../..');
const url = f => 'file://' + (f.startsWith('/') ? f : path.join(W, f));
const MAS = n => url(path.join(ROOT, 'ui/mascots', n + '.webp'));
const TOTAL = 36;

/* ── 부품 ── */
// 캡처 한 장 : crop 은 캡처 css 좌표 [x,y,w,h], marks 는 [x,y,번호] (캡처 css 좌표)
function shot(file, o) {
  o = o || {};
  const [nw, nh] = SZ[file]; const dpr = o.dpr || 2;
  const cw = nw / dpr, ch = nh / dpr;
  const [cx, cy, cwid, chei] = o.crop || [0, 0, cw, ch];
  const sc = o.w / cwid, H = o.h || Math.round(chei * sc);
  const marks = (o.marks || []).map(([x, y, n]) => `<b class="mk" style="left:${Math.round((x - cx) * sc - 20)}px;top:${Math.round((y - cy) * sc - 20)}px">${n}</b>`).join('');
  const cap = o.cap ? `<span class="scap">${o.cap}</span>` : '';
  return `<div class="shot ${o.cls || ''}" style="left:${o.x}px;top:${o.y}px;width:${o.w}px;height:${H}px;${o.style || ''}"><img src="${url(file)}" style="width:${Math.round(cw * sc)}px;left:${Math.round(-cx * sc)}px;top:${Math.round(-cy * sc)}px">${marks}${cap}</div>`;
}
// 휴대폰 틀 (운세 캡처 390x844 @3x)
function phone(file, o) {
  const w = o.w, h = Math.round(w * 844 / 390);
  const marks = (o.marks || []).map(([x, y, n]) => `<b class="mk" style="left:${Math.round(10 + x * w / 390 - 20)}px;top:${Math.round(10 + y * w / 390 - 20)}px">${n}</b>`).join('');
  return `<div class="phone" style="left:${o.x}px;top:${o.y}px;width:${w + 20}px"><div class="scr" style="width:${w}px;height:${h}px"><img src="${url(file)}"></div>${marks}</div>`;
}
const STAGES = ['고객발굴', '터치', '클로징', '계약체결', '관리·소개', '새 고객발굴'];
function stepper(cur) {
  return `<div class="stepper">${STAGES.map((s, i) => {
    const c = i < cur ? 'done' : i === cur ? 'cur' : '';
    return `<div class="sn ${c}"><i>${i < cur ? '✓' : i + 1}</i><span>${s}</span></div>`;
  }).join('<em></em>')}</div>`;
}
function head(chip, title, sub, o) {
  o = o || {};
  return `<div class="hd"><span class="chip ${o.chipGrey ? 'grey' : ''}">${chip}</span><h2 class="title">${title}</h2>${sub ? `<p class="sub">${sub}</p>` : ''}</div>`;
}
const pts = (items, o) => `<div class="pts" style="left:${o.x}px;top:${o.y}px;width:${o.w}px;gap:${o.gap || 26}px">${items.map(([n, t, d]) => `<div class="pt">${n ? `<b class="num">${n}</b>` : '<b class="dot"></b>'}<div><div class="pt-t">${t}</div>${d ? `<div class="pt-d">${d}</div>` : ''}</div></div>`).join('')}</div>`;
const note = (t, o) => `<div class="note" style="left:${o.x}px;top:${o.y}px;${o.w ? 'width:' + o.w + 'px;' : ''}">${t}</div>`;
const tag = (t, k) => `<span class="tag ${k || ''}">${t}</span>`;
const foot = n => `<div class="foot"><span>MeAI 영업 플라이휠 · 세일즈혁신TF</span>@@MINI@@<span>${String(n).padStart(2, '0')} / ${TOTAL}</span></div>`;
const lab = (t, x, y, o) => `<div class="lab" style="left:${x}px;top:${y}px;${(o && o.w) ? 'width:' + o.w + 'px;' : ''}">${t}</div>`;
const doll = (n, x, y, h) => `<img class="doll" src="${MAS(n)}" style="left:${x}px;top:${y}px;height:${h}px">`;

// 플라이휠 그림 : size 정사각, 노드 6개 · 화살표 · 가운데 축
function wheel(size, x, y, o) {
  o = o || {};
  const c = size / 2, r = size * 0.37, nr = o.nr || size * 0.095;
  const ang = i => (-90 + i * 60) * Math.PI / 180;
  const P = (a, rr) => [c + rr * Math.cos(a), c + rr * Math.sin(a)];
  const gap = (nr + 10) / r;
  let arcs = '';
  for (let i = 0; i < 6; i++) {
    const a1 = ang(i) + gap, a2 = ang(i + 1) - gap - 0.02;
    const [x1, y1] = P(a1, r), [x2, y2] = P(a2, r);
    arcs += `<path d="M${x1.toFixed(1)} ${y1.toFixed(1)} A${r} ${r} 0 0 1 ${x2.toFixed(1)} ${y2.toFixed(1)}" fill="none" stroke="${i === 5 ? '#C8102E' : '#D1D6DB'}" stroke-width="${i === 5 ? 5 : 3}" marker-end="url(#ah${i === 5 ? 'r' : 'g'})" ${i === 5 ? 'stroke-dasharray="2 0"' : ''}/>`;
  }
  const nodes = STAGES.map((s, i) => {
    const [nx, ny] = P(ang(i), r);
    const on = o.cur === i;
    return `<div class="wn ${on ? 'on' : o.all ? 'done' : ''}" style="left:${nx - nr}px;top:${ny - nr}px;width:${nr * 2}px;height:${nr * 2}px"><b>${i + 1}</b><span style="font-size:${Math.round(nr * 0.27)}px">${s}</span></div>`;
  }).join('');
  const ax = size * 0.15;
  const axle = o.axle === false ? '' : `<div class="axle ${o.axleRed ? 'red' : ''}" style="left:${c - ax}px;top:${c - ax}px;width:${ax * 2}px;height:${ax * 2}px"><small style="font-size:${Math.round(ax * 0.15)}px">축</small><b style="font-size:${Math.round(ax * 0.2)}px">약관 하나</b><span style="font-size:${Math.round(ax * 0.14)}px">특약 마스터</span></div>`;
  return `<div class="wheel" style="left:${x}px;top:${y}px;width:${size}px;height:${size}px">
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><defs>
<marker id="ahg" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M1 1 L8 5 L1 9" fill="none" stroke="#B0B8C1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker>
<marker id="ahr" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M1 1 L8 5 L1 9" fill="none" stroke="#C8102E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
<circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#F2F4F6" stroke-width="${size * 0.06}"/>${arcs}</svg>${axle}${nodes}</div>`;
}

const CSS = `
@font-face { font-family: "Pretendard Variable"; src: url("file://${FONT}") format("woff2-variations"); font-weight: 45 920; }
:root { --red:#C8102E; --red-s:#A50D26; --red-w:#FDECEE; --red-l:#F5C2CA; --ink:#191F28; --ink2:#333D4B; --sub:#4E5968; --muted:#6B7684; --faint:#8B95A1; --dis:#B0B8C1; --line-s:#D1D6DB; --line:#E5E8EB; --soft:#F2F4F6; --s1:#F9FAFB; }
* { box-sizing: border-box; margin: 0; }
body { background: #ccc; font-family: "Pretendard Variable", sans-serif; color: var(--ink); word-break: keep-all; overflow-wrap: anywhere; }
.slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #fff; margin: 0 0 20px; }
.hd { position: absolute; left: 96px; top: 64px; width: 1180px; }
.chip { display: inline-flex; align-items: center; height: 40px; padding: 0 18px; border-radius: 999px; background: var(--red-w); color: var(--red-s); font-size: 19px; font-weight: 700; letter-spacing: -0.01em; }
.chip.grey { background: var(--soft); color: var(--sub); }
.title { margin-top: 20px; font-size: 50px; font-weight: 700; line-height: 1.28; letter-spacing: -0.03em; }
.sub { margin-top: 12px; font-size: 23px; font-weight: 400; color: var(--muted); line-height: 1.5; letter-spacing: -0.01em; }
.foot { position: absolute; left: 96px; right: 96px; bottom: 34px; display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: 600; color: var(--faint); }
/* 일반 장표 바닥 진척 막대 : 간지와 같은 8구간을 얇게, 지금 구간은 장 위치만큼 채우고 점 */
.mini { flex: 1; display: flex; align-items: center; gap: 16px; margin: 0 56px; }
.mini .mr { flex: 1; display: flex; gap: 4px; }
.mini .ms { position: relative; height: 6px; border-radius: 999px; background: var(--line); }
.mini .ms.done { background: var(--red-l); }
.mini .ms.cur i { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 999px; background: var(--red); }
.mini .ms.cur b { position: absolute; top: 50%; width: 12px; height: 12px; margin: -6px 0 0 -6px; border-radius: 50%; background: var(--red); box-shadow: 0 0 0 3px #fff, 0 0 0 5px var(--red-w); }
.mini .ml { flex: none; font-size: 16px; font-weight: 700; color: var(--red-s); white-space: nowrap; }
/* 진행 표시 */
.stepper { position: absolute; right: 96px; top: 70px; display: flex; align-items: flex-start; }
.stepper em { width: 34px; height: 2px; background: var(--line); margin-top: 15px; }
.sn { display: flex; flex-direction: column; align-items: center; gap: 8px; width: 74px; }
.sn i { font-style: normal; width: 32px; height: 32px; border-radius: 50%; background: var(--line); color: var(--faint); font-size: 16px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.sn span { font-size: 16px; font-weight: 600; color: var(--faint); white-space: nowrap; }
.sn.done i { background: var(--red-w); color: var(--red-s); }
.sn.cur i { background: var(--red); color: #fff; box-shadow: 0 0 0 5px var(--red-w); }
.sn.cur span { color: var(--ink); font-weight: 700; }
/* 캡처 */
.shot { position: absolute; overflow: hidden; border-radius: 16px; border: 1px solid var(--line); background: #fff; box-shadow: 0 12px 32px rgba(15,23,42,.10), 0 2px 6px rgba(15,23,42,.06); }
.shot img { position: absolute; max-width: none; display: block; }
.shot.flat { box-shadow: none; }
.shot.doc { border-radius: 10px; }
.scap { position: absolute; left: 12px; bottom: 12px; padding: 6px 12px; border-radius: 999px; background: rgba(25,31,40,.86); color: #fff; font-size: 16px; font-weight: 600; }
.mk { position: absolute; width: 40px; height: 40px; border-radius: 50%; background: var(--red); color: #fff; font-size: 20px; font-weight: 700; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 4px #fff, 0 6px 16px rgba(200,16,46,.35); z-index: 3; }
.phone { position: absolute; padding: 10px; border-radius: 52px; background: #191F28; box-shadow: 0 24px 56px rgba(25,31,40,.18), 0 6px 16px rgba(25,31,40,.10); }
.phone .scr { border-radius: 42px; overflow: hidden; background: #000; }
.phone .scr img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: top; }
.panel { position: absolute; border-radius: 40px; background: var(--soft); }
.lab { position: absolute; font-size: 18px; font-weight: 700; color: var(--sub); letter-spacing: -0.01em; }
/* 글 목록 */
.pts { position: absolute; display: flex; flex-direction: column; }
.pt { display: flex; gap: 16px; align-items: flex-start; }
.num { flex: none; width: 34px; height: 34px; border-radius: 50%; background: var(--red); color: #fff; font-size: 17px; font-weight: 700; display: flex; align-items: center; justify-content: center; margin-top: 1px; }
.dot { flex: none; width: 8px; height: 8px; border-radius: 50%; background: var(--red); margin: 13px 13px 0; }
.pt-t { font-size: 24px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.38; }
.pt-d { margin-top: 5px; font-size: 19px; font-weight: 400; color: var(--sub); line-height: 1.55; }
.note { position: absolute; padding: 14px 22px; border-radius: 16px; background: var(--soft); color: var(--sub); font-size: 17px; font-weight: 600; line-height: 1.5; }
.tag { display: inline-flex; align-items: center; height: 30px; padding: 0 12px; border-radius: 8px; background: var(--soft); color: var(--sub); font-size: 16px; font-weight: 700; margin-right: 6px; }
.tag.red { background: var(--red-w); color: var(--red-s); }
.tag.dark { background: var(--ink); color: #fff; }
.b { color: var(--red-s); font-weight: 700; }
.doll { position: absolute; width: auto; }
/* 플라이휠 */
.wheel { position: absolute; }
.wheel svg { position: absolute; left: 0; top: 0; }
.wn { position: absolute; border-radius: 50%; background: #fff; border: 1px solid var(--line); box-shadow: 0 4px 12px rgba(15,23,42,.06), 0 1px 2px rgba(15,23,42,.04); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; }
.wn b { font-size: 18px; font-weight: 700; color: var(--red); }
.wn span { font-weight: 700; letter-spacing: -0.02em; text-align: center; line-height: 1.2; }
.wn.on { background: var(--red); border-color: var(--red); }
.wn.on b, .wn.on span { color: #fff; }
.wn.done { background: var(--red-w); border-color: var(--red-l); }
.wn.done b, .wn.done span { color: var(--red-s); }
.axle.red { background: var(--red); }
.axle.red small, .axle.red span { color: #FDECEE; }
.axle { position: absolute; border-radius: 50%; background: var(--ink); color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 2px; }
.axle small { font-weight: 600; color: var(--dis); }
.axle b { font-weight: 700; letter-spacing: -0.02em; }
.axle span { font-weight: 400; color: var(--dis); }
/* 카드 */
.card { position: absolute; border-radius: 24px; background: #fff; border: 1px solid var(--line); padding: 26px 28px; }
.card.g { background: var(--s1); }
.card h4 { font-size: 24px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.35; }
.card p { margin-top: 8px; font-size: 18px; font-weight: 400; color: var(--sub); line-height: 1.55; }
.card .k { display: inline-flex; align-items: center; gap: 8px; font-size: 17px; font-weight: 700; color: var(--red-s); }
.card .k i { font-style: normal; width: 30px; height: 30px; border-radius: 50%; background: var(--red); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 15px; }
.card .to { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--line); font-size: 17px; font-weight: 600; color: var(--ink2); line-height: 1.45; }
.card .to b { color: var(--red-s); }
/* 도구 지도 카드 */
.tc { position: absolute; border-radius: 18px; background: #fff; border: 1px solid var(--line); overflow: hidden; }
.tc .th { position: relative; height: 112px; overflow: hidden; border-bottom: 1px solid var(--line); background: var(--s1); }
.tc .th img { position: absolute; max-width: none; }
.tc .tb { padding: 12px 16px 0; }
.tc .tn { font-size: 20px; font-weight: 700; letter-spacing: -0.02em; }
.tc .td { margin-top: 3px; font-size: 16px; font-weight: 400; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tc .sp { display: flex; gap: 5px; padding: 10px 16px 0; }
.tc .sp i { font-style: normal; width: 28px; height: 24px; border-radius: 6px; background: var(--soft); color: var(--dis); font-size: 14px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.tc .sp i.on { background: var(--red-w); color: var(--red-s); }
.tc .sp i.x { width: auto; padding: 0 8px; background: var(--ink); color: #fff; }
/* 숫자 */
.big { font-size: 58px; font-weight: 700; letter-spacing: -0.04em; line-height: 1; font-variant-numeric: tabular-nums; white-space: nowrap; }
.big small { font-size: 32px; font-weight: 600; margin-left: 4px; letter-spacing: -0.02em; }
/* 표 */
.tbl { position: absolute; border: 1px solid var(--line); border-radius: 16px; overflow: hidden; }
.tbl table { border-collapse: collapse; width: 100%; }
.tbl th { background: var(--s1); color: var(--sub); font-size: 17px; font-weight: 700; text-align: left; padding: 14px 18px; border-bottom: 1px solid var(--line-s); }
.tbl td { font-size: 19px; font-weight: 400; color: var(--ink2); padding: 13px 18px; border-bottom: 1px solid var(--soft); line-height: 1.45; vertical-align: top; }
.tbl td.st { font-weight: 700; color: var(--ink); white-space: nowrap; }
.tbl td.st i { font-style: normal; display: inline-flex; width: 30px; height: 30px; border-radius: 50%; background: var(--red); color: #fff; font-size: 15px; align-items: center; justify-content: center; margin-right: 10px; }
.tbl tr:last-child td { border-bottom: 0; }
.tbl.t2 td { padding: 21px 18px; font-size: 20px; }
/* 표지 */
.cv h1 { font-size: 96px; font-weight: 700; line-height: 1.14; letter-spacing: -0.04em; }
.cv .lead { margin-top: 30px; font-size: 30px; font-weight: 400; color: var(--sub); line-height: 1.5; letter-spacing: -0.015em; }
.arrow { position: absolute; color: var(--dis); font-size: 34px; font-weight: 700; }
/* 간지 */
.sec-no { margin-top: 34px; font-size: 120px; font-weight: 700; color: var(--red); letter-spacing: -0.04em; line-height: 1; font-variant-numeric: tabular-nums; }
.sec-t { margin-top: 18px; font-size: 88px; font-weight: 700; letter-spacing: -0.04em; line-height: 1.1; }
.sec-g { margin-top: 22px; font-size: 30px; font-weight: 400; color: var(--sub); line-height: 1.5; letter-spacing: -0.015em; }
.sec-l { margin-top: 44px; font-size: 20px; font-weight: 600; color: var(--muted); }
.sec-l b { color: var(--red-s); font-weight: 700; }
.sec-chips { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 10px; }
.prog { position: absolute; display: flex; align-items: flex-start; gap: 28px; }
.prog .pg-row { flex: 1; display: flex; gap: 6px; }
.prog .seg { position: relative; min-width: 0; }
.prog .seg i { display: block; height: 12px; border-radius: 999px; background: var(--line); }
.prog .seg.done i { background: var(--red-l); }
.prog .seg.cur i { background: var(--red); box-shadow: 0 0 0 4px var(--red-w); }
.prog .seg span { display: block; margin-top: 14px; font-size: 16px; font-weight: 600; color: var(--faint); white-space: nowrap; letter-spacing: -0.01em; }
.prog .seg.done span { color: var(--sub); }
.prog .seg.cur span { color: var(--ink); font-weight: 700; }
.prog .seg em { position: absolute; left: -2px; top: -48px; font-style: normal; white-space: nowrap; padding: 7px 13px; border-radius: 10px; background: var(--ink); color: #fff; font-size: 15px; font-weight: 700; box-shadow: 0 4px 12px rgba(15,23,42,.10); }
.prog .seg em::after { content: ""; position: absolute; left: 16px; bottom: -6px; border: 6px solid transparent; border-bottom: 0; border-top-color: var(--ink); }
.prog .pg-n { flex: none; margin-top: -9px; font-size: 26px; font-weight: 700; color: var(--ink); letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.prog .pg-n small { font-size: 18px; font-weight: 600; color: var(--faint); margin-left: 2px; }
.sec-chips span { display: inline-flex; align-items: center; height: 48px; padding: 0 20px; border-radius: 999px; background: var(--soft); color: var(--ink2); font-size: 21px; font-weight: 600; letter-spacing: -0.01em; }
`;

/* ── 장표 ── */
const S = [];
const add = (html, notes) => S.push({ html: `<section class="slide">${html}${foot(S.length + 1)}</section>`, notes });
// 영업 프로세스 간지 : 단계 번호 · 이름 · 목표 한 줄 · 이 단계 도구와 쪽수 · 지금 단계를 칠한 바퀴
const DIV = [];
const DOLL_W = { merry_detective: 229, hello_wave: 278, eco_point: 271, tata_ok: 275, eco_doctor: 272, success_thumbs: 261, group_lineup: 720 };
const DOLL_H = { group_lineup: 180 };
function sect(k, goal, tools, mascot, o) {
  o = o || {};
  DIV.push(S.length);
  const title = o.title || STAGES[k - 1];
  const mh = o.mh || 180, mw = Math.round(mh * DOLL_W[mascot] / (DOLL_H[mascot] || 360));
  add(`<div style="position:absolute;left:96px;top:96px;width:900px">
<span class="chip">${o.chip || `영업 프로세스 ${k} / 6`}</span>
<div class="sec-no">0${k}</div>
<h1 class="sec-t">${title}</h1>
<p class="sec-g">${goal}</p>
<div class="sec-l">${o.label || '이 단계에서 꺼내는 도구'} · <b>@@RANGE${k}@@</b></div>
<div class="sec-chips">${tools.map(t => `<span>${t}</span>`).join('')}</div></div>
<div class="panel" style="left:1080px;top:64px;width:744px;height:766px"></div>
${wheel(500, 1202, 92, o.wheel || { cur: k - 1 })}
${doll(mascot, 1452 - Math.round(mw / 2), 830 - mh - 26, mh)}
@@PROG@@`,
    `간지 · ${k} ${title}
- ${o.chip ? '이 부분에서 보는 것' : '이 단계 목표'} : ${goal.replace(/<br>/g, ' ')}
- 다음 장부터 ${tools.join(' · ')}
- 아래 막대는 발표 진행. 진한 빨강이 지금 구간`);
}
// 발표 진척도 막대 : 도입 · 영업 6단계 · 정리 8구간, 구간 길이는 장 수에 비례
const CHAPTERS = ['도입', '고객발굴', '터치', '클로징', '계약체결', '관리·소개', '새 고객발굴', '정리'];
function prog(cur, page, bounds) {
  const segs = CHAPTERS.map((c, i) => {
    const cls = i < cur ? 'done' : i === cur ? 'cur' : '';
    return `<div class="seg ${cls}" style="flex:${bounds[i + 1] - bounds[i]}"><i></i><span>${c}</span>${i === cur ? '<em>지금 여기</em>' : ''}</div>`;
  }).join('');
  return `<div class="prog" style="left:96px;top:906px;width:1728px"><div class="pg-row">${segs}</div><div class="pg-n">${Math.round(page / TOTAL * 100)}<small>%</small></div></div>`;
}
let HABIT_AT = 0;

// 1 표지
add(`<div class="cv">
<div style="position:absolute;left:96px;top:120px;width:860px">
<span class="chip">세일즈혁신TF · 2026.11</span>
<h1 style="margin-top:40px;font-size:84px">플라이휠,<br>영업지원도구를 통한<br>영업프로세스 <span style="color:var(--red)">선순환</span></h1>
<p class="lead">고객발굴부터 터치, 클로징, 계약체결, 관리와 소개를 거쳐<br>새 고객발굴까지. 단계마다 꺼내 쓰는 보조도구 11종을<br>실제 화면으로 정리함</p>
</div>
<div style="position:absolute;left:96px;top:880px;display:flex;gap:10px">${tag('영업지원도구 6종', 'red')}${tag('설계서 생성기 3종')}${tag('MeAI 홈 2종')}</div>
<div class="panel" style="left:1000px;top:64px;width:824px;height:952px"></div>
${wheel(640, 1092, 110, {})}
${doll('group_hello', 1232, 818, 198)}
</div>`,
  `표지
- 직접 만든 보조도구 11종을 영업 순서(플라이휠)에 맞춰 놓은 자료임
- 도구 소개가 아니라 "어느 단계에서 무엇을 꺼내는지"가 중심임
- 화면은 모두 실제 도구를 열어 찍은 것. 고객 이름·숫자는 예시`);

// 2 한 장 요약
add(`${head('한 장 요약', '도구마다 맡은 단계가 있고,<br>단계가 이어지면 한 바퀴가 됨', null, { chipGrey: true })}
${wheel(700, 96, 300, {})}
<div class="tbl t2" style="left:860px;top:96px;width:964px">
<table><tr><th style="width:250px">단계</th><th>꺼내 쓰는 도구</th></tr>
<tr><td class="st"><i>1</i>고객발굴</td><td>MeAI 홈 넛지(추천 고객 슬롯 · CRM 룰렛) · 프롬프트 「고객발굴」</td></tr>
<tr><td class="st"><i>2</i>터치</td><td>오늘의 운세(사주 + 타로) · 오늘의 화법 798건 · 프롬프트 「고객터치」</td></tr>
<tr><td class="st"><i>3</i>클로징</td><td>특약검색기 · 보상시뮬레이터 · 통합치료비 · 스마트 제안서(끼움판 · GA 디자인판) · 세일즈북 · 수술비 비교</td></tr>
<tr><td class="st"><i>4</i>계약체결</td><td>상품 라인업(알릴의무 · 예외질환 판정) · 상품 히스토리 · 상급종합 지도 · 세일즈북 면책·감액표</td></tr>
<tr><td class="st"><i>5</i>관리·소개</td><td>보상시뮬레이터 청구 안내 · 상급종합 지도 · 상품 히스토리 · 프롬프트 「사후관리」 · CRM 룰렛</td></tr>
<tr><td class="st"><i>6</i>새 고객발굴</td><td>명패 제작기(초청 세미나) · 추천 슬롯 「동의 필요」 → 다시 1단계</td></tr>
</table></div>
<div style="position:absolute;left:860px;top:760px;width:964px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
<div class="card g" style="position:relative"><span class="k">축</span><h4 style="margin-top:6px">약관 하나</h4><p>세 갈래 산출물이 같은 특약 마스터를 씀</p></div>
<div class="card g" style="position:relative"><span class="k">미는 힘</span><h4 style="margin-top:6px">매일 여는 습관</h4><p>홈 넛지가 오늘 연락할 고객을 먼저 내밈</p></div>
<div class="card g" style="position:relative"><span class="k">가속</span><h4 style="margin-top:6px">소개</h4><p>관리에서 나온 소개가 다음 바퀴 첫 고객</p></div>
</div>`,
  `한 장 요약
- 왼쪽 바퀴 : 영업 6단계. 6에서 1로 넘어가는 빨간 화살표가 소개로 생긴 새 고객
- 오른쪽 표 : 단계별로 꺼내 쓰는 도구. 한 도구가 여러 단계에 나오기도 함(보상시뮬레이터는 클로징과 관리 둘 다)
- 축은 약관. 질병코드와 금액은 약관 별표와 특약 마스터에서만 가져옴
- 미는 힘은 매일 홈을 여는 습관, 가속은 소개`);

// 3 멈추는 자리
const stops = [
  ['1', '고객발굴', '오늘 누구에게 연락할지 매일 아침 처음부터 고민함', '홈 넛지 추천 고객 · CRM 룰렛'],
  ['2', '터치', '보험 얘기 말고 먼저 꺼낼 말이 마땅치 않음', '오늘의 운세 · 오늘의 화법'],
  ['3', '클로징', '약관은 상품마다 수백~천 쪽인데 설계서는 담보 이름과 금액을 나열만 함', '특약검색기 · 스마트 제안서 · 세일즈북'],
  ['4', '계약체결', '병력 · 바뀐 담보 · 병원 조건을 청약 뒤에야 알게 되면 분쟁이 됨', '예외질환 판정 · 상품 히스토리 · 상급종합 지도'],
  ['5', '관리·소개', '아플 때 받을 특약을 하나라도 놓치면 신뢰가 깨지고 소개도 끊김', '보상시뮬레이터 · 상급종합 지도'],
  ['6', '새 고객발굴', '소개 받은 고객과 다시 맨손으로 시작함', '초청 세미나 명패 · 추천 슬롯'],
];
add(`${head('지금 모습', '지금은 단계마다 바퀴가 한 번씩 멈춤', '멈추는 이유와 그 자리에 넣은 도구', { chipGrey: true })}
${stops.map(([n, s, why, to], i) => `<div class="card" style="left:${96 + (i % 3) * 584}px;top:${300 + Math.floor(i / 3) * 330}px;width:560px;height:306px">
<span class="k"><i>${n}</i>${s}</span><h4 style="margin-top:16px;font-size:27px;line-height:1.42">${why}</h4><div class="to" style="position:absolute;left:28px;right:28px;bottom:24px">바꾸는 도구 <b>${to}</b></div></div>`).join('')}`,
  `지금 모습
- 단계마다 멈추는 이유가 다름. 아침 고민, 첫마디, 약관 두께, 인수 불확실, 청구 누락, 소개 뒤 다시 시작
- 카드 아래쪽이 그 자리에 넣은 도구
- 다음 장부터 도구 전체 지도 → 단계별 실제 화면 순서로 봄`);

// 4 도구 지도
const TOOLS = [
  ['특약검색기', '약관 원문 · 수술비 비교 · 지도 · 히스토리', [3, 4, 5], 'cap/tool_search.png', [140, 150, 1160, 396]],
  ['보상시뮬레이터', '진단부터 사망까지 보장 순서', [3, 5], 'cap/sim_stages.png', [140, 170, 1160, 396]],
  ['상품 라인업', '50종 · 알릴의무 · 예외질환', [3, 4], 'cap/pr_ex_result.png', [200, 50, 1060, 362]],
  ['통합치료비 시뮬레이터', '치료 과정별 1년 수령액', [3], 'cap/zz_path.png', [580, 120, 700, 239]],
  ['프롬프트 라이브러리', 'MeAI 질문 272개 · 영업 단계별', [1, 2, 3, 5], 'cap/pm_s1.png', [100, 60, 1240, 423]],
  ['명패 제작기', '엑셀 명단 → 명패 · 라벨', [6], 'cap/np_plates.png', [0, 0, 1076, 367]],
  ['스마트 제안서', '설계서 → 맞춤 보장 9쪽', [3, 5], 'sp/sp_p01.png', [0, 0, 794, 271]],
  ['스마트 제안서 GA 디자인판', 'GA 디자인 · TA PA부문도 출력', [3], 'sp/ga_p02.png', [0, 20, 794, 271]],
  ['세일즈북 생성기', '설계서 → 상담 가이드북', [3, 4], 'cap/gb/gb_p02.png', [0, 30, 794, 271]],
  ['MeAI 홈 넛지 플레이', '추천 고객 · 루틴 · 행운 존', [1, 2, 5, 6], 'cap/nz/home_1440.png', [150, 20, 1140, 389]],
  ['오늘의 운세', '사주 + 타로 · 카톡 공유', [2, 5], 'cap/unse/saju_share.png', [0, 0, 390, 133]],
];
const DPR = { 'cap/unse/saju_share.png': 3 };
function thumb(file, crop, w, h) {
  const [nw] = SZ[file]; const dpr = DPR[file] || 2; const cw = nw / dpr; const sc = w / crop[2];
  return `<img src="${url(file)}" style="width:${Math.round(cw * sc)}px;left:${Math.round(-crop[0] * sc)}px;top:${Math.round(-crop[1] * sc)}px">`;
}
add(`${head('도구 지도', '보조도구 11종과 맡은 단계', '숫자 칸은 플라이휠 단계(1 발굴 · 2 터치 · 3 클로징 · 4 체결 · 5 관리·소개 · 6 새 발굴)', { chipGrey: true })}
${TOOLS.map(([n, d, st, f, crop], i) => `<div class="tc" style="left:${96 + (i % 4) * 438}px;top:${296 + Math.floor(i / 4) * 238}px;width:418px;height:222px">
<div class="th">${thumb(f, crop, 418, 112)}</div><div class="tb"><div class="tn">${n}</div><div class="td">${d}</div></div>
<div class="sp">${st[0] === '관리' ? '<i class="x">관리자용</i>' : [1, 2, 3, 4, 5, 6].map(k => `<i class="${st.includes(k) ? 'on' : ''}">${k}</i>`).join('')}</div></div>`).join('')}`,
  `도구 지도
- 영업지원도구 6종(특약검색기 · 보상시뮬레이터 · 상품 라인업 · 통합치료비 · 프롬프트 · 명패) + 설계서 생성기 3종 + MeAI 홈 2종
- 빨간 숫자 칸이 그 도구를 쓰는 단계. 프롬프트와 홈 넛지는 여러 단계에 걸침
- 특약검색기는 위쪽 수술비 비교 · 상급종합 지도 · 상품 히스토리 단추 덕분에 체결 · 관리 단계에도 걸침`);

// 5 대문
add(`${head('출발점', '모든 도구는 대문 한 화면에서 열림', '영업지원도구 6종 · 인터넷이 없는 내부망 배포판과 휴대폰에서도 같은 화면', { chipGrey: true })}
${shot('cap/idx_hero.png', { x: 96, y: 300, w: 860, crop: [0, 56, 1440, 760], marks: [[112, 505, 1], [812, 470, 2]] })}
${shot('cap/idx_s2.png', { x: 990, y: 300, w: 834, crop: [100, 56, 1240, 520], marks: [[150, 330, 3]] })}
${pts([[1, '첫 화면에서 특약검색으로 바로 들어감', null], [2, '걱정인형 여섯이 도구를 하나씩 맡음(셔츠 글자를 이으면 MERITZ)', null], [3, '도구 안 자료 : 특약 1,155종 · 상품 50종 · 프롬프트 272개 · 용어 풀이 907개', '2026년 10월 대문 표시 기준']], { x: 990, y: 690, w: 834, gap: 18 })}`,
  `출발점
- 대문(index.html)이 6종 도구의 입구. 머리 띠 메뉴로 도구끼리 오감
- 내부망 배포판(영업지원도구6종.zip)은 파일만 열면 동작함
- 숫자는 대문 화면에 적힌 값. 특약 수는 세는 방식(세부보장 포함 여부)에 따라 화면마다 조금 다름`);

sect(1, '오늘 연락할 고객을 고르고,<br>연락할 이유를 붙임', ['MeAI 홈 넛지 · 추천 고객 슬롯', 'CRM 룰렛', '프롬프트 「고객발굴」'], 'merry_detective');

// 6 [1] 홈 넛지 추천
add(`${head('1 고객발굴', '아침에 홈을 열면<br>오늘 챙길 고객이 먼저 떠 있음')}${stepper(0)}
${pts([
    [1, '「오늘의 MeAI」 막대', '출석 · 퀴즈 · 화법 · 추천 · 리그 칸과 오기·배우기·영업하기 세 고리로 오늘 할 일을 보여 줌'],
    [2, '버디 말풍선', '시간대마다 걱정인형이 다음 행동을 한 문장으로 권함'],
    [3, '오늘의 추천 고객', 'MeAI 홈 기본 영역. 넛지는 이 카드로 손이 가게 만듦'],
    [4, '추천 고객 슬롯', '생일 · 상령일 · 갱신 · 보장 공백 · 동의 필요 다섯 사유로 오늘 연락할 3명을 뽑음. 같은 사유 3명이면 응모권'],
  ], { x: 96, y: 330, w: 560, gap: 22 })}
${shot('cap/nz/home_1440.png', { x: 700, y: 330, w: 760, crop: [0, 0, 1440, 900], marks: [[175, 187, 1], [835, 114, 2], [175, 687, 3]] })}
${shot('cap/nz/fun_cslot.png', { x: 1490, y: 330, w: 334, marks: [[30, 30, 4]] })}
${note('목업 단계 · 개발 패키지(API 28개 · DB 표 35개 · 배치 11개) 준비됨. 고객 이름은 예시', { x: 700, y: 856, w: 760 })}`,
  `1 고객발굴 · 홈 넛지 추천
- MeAI 홈 위에 한 줄(오늘의 MeAI 막대)만 더한 목업. 기존 홈 구성은 그대로
- 추천 고객 슬롯 : 릴 3개를 당기면 오늘 챙길 고객 3명. 「맞춤대화」 「연락했어요」 단추가 바로 붙음
- 지금은 목업. 넛지 서버를 새로 만들어야 하고 명세(API · DB · 테스트 112건)는 준비됨`);

// 7 [1] CRM 룰렛 + 프롬프트
add(`${head('1 고객발굴', '연락할 이유와 첫 문장까지 붙여서 줌')}${stepper(0)}
${shot('cap/nz/fun_roulette.png', { x: 96, y: 250, w: 520, crop: [0, 0, 576, 820] })}
${pts([
    [1, 'CRM 룰렛', '8칸 돌림판이 생일 축하 · 상령일 · 갱신 · 보장 점검 · 건강검진 · 감사 인사 중 하나를 고르면, 어울리는 내 고객 3명과 안부 문구가 붙음'],
    [2, '확률은 화면에 숫자로 공개', '운으로 받는 응모권은 하루 3장까지. 문구는 보내기 전에 설계사가 확인함'],
    [3, '프롬프트 「고객발굴/CRM선정」 16개', '보장이 약한 고객 유형 정의, 리모델링 체크리스트처럼 MeAI에 붙이면 되는 질문'],
  ], { x: 660, y: 270, w: 470, gap: 26 })}
${shot('cap/pm_s1.png', { x: 1170, y: 250, w: 654, h: 420, crop: [90, 150, 1260, 756], marks: [[226, 247, 3]] })}
<div class="card g" style="left:1170px;top:700px;width:654px;height:250px"><span class="k">P038 · 고객발굴/CRM선정</span><h4 style="margin-top:10px;font-size:22px;line-height:1.5;font-weight:600">뇌·심장 보장이 취약한 고객 유형을 5가지로 정의하고 각 유형별로 자연스럽게 보험 필요성을 꺼낼 수 있는 대화 오프닝을 만들어줘</h4><p style="font-size:16px">라이브러리 원문 그대로. 복사해서 MeAI에 붙임</p></div>`,
  `1 고객발굴 · CRM 룰렛과 프롬프트
- 룰렛 결과는 항상 "오늘 연락할 고객"으로 끝남. 재미 장치가 영업 행동으로 이어지게 설계함
- 확률 공개, 하루 한도는 준법 검토 항목으로 따로 정리해 둠
- 오른쪽은 프롬프트 라이브러리에서 영업단계 「고객발굴/CRM선정」을 고른 화면(16개)`);

sect(2, '보험 얘기 전에<br>안부와 첫마디로 대화를 엶', ['오늘의 운세', '오늘의 화법 798건', '프롬프트 「고객터치」'], 'hello_wave');

// 8 [2] 오늘의 운세
add(`${head('2 터치', '보험 얘기 전에 운세 한 장으로 안부를 엶')}${stepper(1)}
${pts([
    [1, '이름과 생년월일만 넣음', '사주팔자 · 오늘의 운세 점수 · 행운 색 · 대운까지 나옴'],
    [2, '타로 4장', '78장 중 4장을 뽑아 지금의 나 · 걸림돌 · 도움의 열쇠 · 다가올 흐름으로 풀이(1909년 원판 그림)'],
    [3, '그림 한 장으로 보냄', '결과를 이미지로 저장해 카톡 · 문자로 전달'],
    ['', '입력 정보는 휴대폰 밖으로 나가지 않음', '한 파일(약 3.5MB) · 인터넷 없이 더블클릭으로 열림'],
  ], { x: 96, y: 300, w: 520, gap: 24 })}
${phone('cap/unse/saju_fortune.png', { x: 680, y: 236, w: 330, marks: [[30, 70, 1]] })}
${phone('cap/unse/tarot_reads.png', { x: 1050, y: 236, w: 330, marks: [[30, 40, 2]] })}
${shot('cap/unse/saju_share.png', { x: 1424, y: 300, w: 400, dpr: 3, h: 600, cls: 'flat', marks: [[30, 30, 3]] })}`,
  `2 터치 · 오늘의 운세
- 설계사가 고객에게 보내는 재미용 안부 도구. 보험 이야기를 꺼내기 전 대화를 여는 용도
- 화면 속 「김하늘」은 가상 인물
- 사내 웹서버 탑재 패키지도 있음(가장 엄격한 보안정책 점검 통과)`);

// 9 [2] 화법
add(`${head('2 터치', '첫마디는 동료들이 써 본 화법에서 고름')}${stepper(1)}
${shot('cap/nz/card_talk.png', { x: 96, y: 250, w: 560 })}
${shot('cap/nz/fun_fortune.png', { x: 690, y: 250, w: 520, crop: [0, 0, 576, 700] })}
${pts([
    [1, '오늘의 화법 798건', '9월 필살 화법 공모 제출작(이름 가림). 공감 · 저장 · 「고객에게 써봤어요」가 쌓여 현장 인기 순이 생김'],
    [2, '오늘의 운세 카드', '홈 행운 존에서 내 운세와 함께 「오늘의 대화 한마디」를 받아 안부 문장으로 씀'],
    [3, '프롬프트 「고객터치」', '3분 요약 멘트, 간편 인수 확대 안내처럼 첫 통화 문구를 MeAI로 다듬음'],
  ], { x: 1260, y: 270, w: 564, gap: 28 })}`,
  `2 터치 · 화법
- 왼쪽 : 홈 넛지의 오늘의 화법 카드. 따라 쓰기를 마치면 응모권
- 가운데 : 행운 존의 오늘의 운세 카드. 고객에게 건넬 한마디가 같이 나옴
- 화법 798건은 제출자 이름을 가린 판만 저장소에 둠`);

sect(3, '고객 질문에 약관 근거로 답하고,<br>고객 맞춤 자료를 건넴', ['특약검색기', '보상시뮬레이터', '통합치료비 시뮬레이터', '스마트 제안서', '스마트 제안서 GA 디자인판', '세일즈북 생성기', '수술비 비교'], 'eco_point');

// 10 [3] 상담 한 장면
const flow = [
  ['특약검색기로 찾기', '「위암」이나 C16을 치면 걸리는 특약과 지급 조건이 나옴', 'cap/tool_search.png', [140, 150, 1160, 740]],
  ['보상시뮬레이터로 순서 보기', '위암 보상 가능 특약 299개를 진단 28 · 검사 8 · 수술 33 · 입원 18 순서로 보여 줌', 'cap/sim_stages.png', [140, 170, 1160, 740]],
  ['통합치료비로 금액 계산', '진행성 위암 복강경 수술 + 항암이면 1년 동안 2,020만원', 'cap/zz_path.png', [580, 170, 700, 446]],
  ['프롬프트로 설명 정리', '단계에 맞는 질문을 복사해 MeAI에 붙이면 고객용 설명이 나옴', 'cap/pm_modal.png', [400, 380, 640, 408]],
];
add(`${head('3 클로징', '"위암이면 얼마 받아요?"<br>질문 하나에 도구 네 개가 이어짐')}${stepper(2)}
${flow.map(([t, d, f, crop], i) => `${shot(f, { x: 96 + i * 440, y: 330, w: 410, h: 262, crop })}
<div style="position:absolute;left:${96 + i * 440}px;top:620px;width:410px"><b class="num" style="display:inline-flex">${i + 1}</b><div class="pt-t" style="margin-top:12px">${t}</div><div class="pt-d">${d}</div></div>`).join('')}
${[0, 1, 2].map(i => `<div class="arrow" style="left:${96 + i * 440 + 412}px;top:436px">›</div>`).join('')}
${note('금액은 화면의 예시 조합(암 기본형 1억원) 기준. 실제 지급은 약관 지급사유와 가입 내역을 따름', { x: 96, y: 880 })}`,
  `3 클로징 · 상담 한 장면
- 대문에도 같은 흐름이 실려 있음. 고객 질문 하나에 네 도구를 차례로 엶
- 299개는 같은 특약을 한 번으로 센 값(상품별로 세면 659건)
- 2,020만원은 통합치료비 화면의 기본 조합 기준 예시`);

// 11 [3] 특약검색기 구조
add(`${head('3 클로징', '특약검색기는 병명 하나로<br>6개 상품 특약을 다 훑음')}${stepper(2)}
${shot('cap/tool_search.png', { x: 96, y: 330, w: 1010, h: 500, crop: [130, 150, 1180, 750], marks: [[152, 192, 1], [175, 370, 2], [430, 420, 3]] })}
${shot('cap/tool_modal.png', { x: 1144, y: 330, w: 680, h: 500, crop: [290, 64, 860, 632], marks: [[322, 198, 4], [322, 292, 5], [322, 676, 6]] })}
${pts([
    [1, '병명 · 질병코드 · 특약명 검색', null], [2, '상품 6갈래와 보장 분류로 좁힘', null], [3, '카드 : 상품 배지 · 보장 코드 칩 · 비교 · 즐겨찾기', null],
  ], { x: 96, y: 852, w: 1010, gap: 8 })}
${pts([
    [4, '같은 특약 · 다른 상품을 한 카드로 묶음', null], [5, '약관 본문 · 별표 · 보장 분석 탭(지급표는 약관 그대로)', null], [6, '보장 질병코드와 보장 제외 코드', null],
  ], { x: 1144, y: 852, w: 680, gap: 8 })}`,
  `3 클로징 · 특약검색기
- 통합간편 · 케어프리 · 운전자 · 치아 · 또또암 · 또또암간편 6개 상품의 특약을 한 번에 찾음
- 카드를 누르면 약관 본문이 열리고, 지급금액표도 약관에 있는 그대로 보임
- 질병코드는 약관 별표에서만 옴. 별표에 없으면 비워 둠`);

// 12 [3] 특약검색기 부가 기능
const extra = [
  ['보험용어 풀이 907개', '약관 밑줄 단어에 올리면 쉬운 설명', 'cap/tool_gloss.png', [480, 60, 630, 560]],
  ['상급종합 지도', '상급종합 47 · 암중점 16 · 권역심뇌 15 · 권역외상 17', 'cap/tool_map.png', [290, 20, 630, 560]],
  ['표적항암 종류', '작용 기전별 6가지와 대표 약제', 'cap/tool_onco.png', [300, 40, 630, 560]],
  ['수술비 비교', '1-5종 · 1-7종 · 131대 수술비를 한 번에', 'cap/tool_surg.png', [250, 170, 420, 560]],
  ['상품 히스토리', '출시 · 개정 이슈를 시간 순으로', 'cap/tool_hist.png', [340, 20, 630, 560]],
];
add(`${head('3 클로징', '상담 중 막히는 질문은 단추 하나로 답함', '특약검색기 머리 단추와 약관 밑줄')}${stepper(2)}
${extra.map(([t, d, f, crop], i) => { const x = 96 + i * 350; return `${shot(f, { x, y: 300, w: 330, h: 440, crop: [crop[0], crop[1], crop[2], crop[2] * 440 / 330] })}
<div style="position:absolute;left:${x}px;top:766px;width:330px"><div class="pt-t" style="font-size:22px">${t}</div><div class="pt-d" style="font-size:18px">${d}</div></div>`; }).join('')}
${note('NEW 표시가 붙은 표적항암 종류 · 수술비 비교는 새로 붙인 단추. 같은 단추 넷이 보상시뮬레이터 화면 위에도 있음', { x: 96, y: 880 })}`,
  `3 클로징 · 특약검색기 부가 기능
- 용어 풀이 : 보장개시일, 유사암처럼 고객이 되묻는 말에 바로 쉬운 설명
- 상급종합 지도 : "큰 병원 가면요?" 질문에 권역별 병원 목록으로 답함
- 표적항암 · 수술비 비교 · 상품 히스토리는 새로 붙인 단추`);

const SIM_AT = S.length;
// 13 [3] 보상시뮬레이터
add(`${head('3 클로징', '병명 하나 넣으면<br>진단부터 사망까지 보장 순서가 나옴')}${stepper(2)}
${shot('cap/sim_stages.png', { x: 96, y: 330, w: 900, h: 496, crop: [130, 60, 1180, 700], marks: [[160, 95, 1], [170, 190, 2], [170, 370, 3], [170, 640, 4]] })}
${shot('cap/sim_surgery.png', { x: 1030, y: 330, w: 794, h: 496, crop: [140, 100, 1170, 620], marks: [[1270, 150, 5]] })}
${pts([[1, '병명 · KCD · 초성 검색', null], [2, '보장 타임라인 : 단계별 특약 수', null]], { x: 96, y: 852, w: 440, gap: 8 })}${pts([[3, '보장유형 필터', null], [4, '단계를 펼쳐 특약 카드 보기', null]], { x: 556, y: 852, w: 440, gap: 8 })}
${pts([[5, '카드마다 약관 원문 단추 · 1년 내 50% 감액 · 보장 제외 코드(C44 · C73)', null]], { x: 1030, y: 852, w: 794 })}`,
  `3 클로징 · 보상시뮬레이터
- 위암 기준 진단 28 · 검사 8 · 수술 33 · 입원 18 · 통원 3 · 치료 122 · 간병 29 · 후유장해 17 · 사망 3
- 카드의 빨간 줄은 그 특약에서 보장하지 않는 코드
- 실제 지급 여부와 금액은 약관 지급사유, 인수심사, 실제 가입 내역으로 정해짐(화면 안내 문구 그대로)`);

// 14 [3] 통합치료비
add(`${head('3 클로징', '치료 과정을 고르면<br>1년 동안 받는 금액이 계산됨')}${stepper(2)}
${shot('cap/zz_path.png', { x: 96, y: 330, w: 820, h: 496, crop: [130, 60, 1180, 720], marks: [[600, 150, 1], [655, 405, 2]] })}
${shot('cap/zz_steps.png', { x: 950, y: 330, w: 420, h: 496, crop: [550, 120, 680, 803], marks: [[580, 150, 3]] })}
${shot('cap/zz_amount.png', { x: 1404, y: 330, w: 420, h: 496, crop: [550, 30, 680, 803], marks: [[580, 60, 4]] })}
${pts([[1, '치료 과정 다섯 갈래 중 하나를 고름', null], [2, '이 과정이라면 1년 동안 2,020만원', null]], { x: 96, y: 852, w: 820, gap: 8 })}
${pts([[3, '검사 · 수술 · 항암 단계마다 더해짐', null], [4, '가입금액별 비교 : 1,015 · 1,520 · 2,020만원', null]], { x: 950, y: 852, w: 874, gap: 8 })}`,
  `3 클로징 · 통합치료비 시뮬레이터
- 암 · 뇌 · 심장 통합치료비 특약 12종을 치료 단계별로 계산함
- 예시는 진행성 위암 복강경 수술 + 항암, 암 기본형 1억원 조합
- 가입금액 4,000만원이면 1,015만원, 8,000만원이면 1,520만원. 증액 상담 자리에서 씀`);

// 15 [3] 스마트 제안서
const SPN = ['한장요약', '암 세부', '뇌·심혈관', '질병코드 지도', '통합치료비', '수술비 · 입원', '다빈도 질환', '치료 사례', '상해 · 사망'];
add(`${head('3 클로징', '설계서 PDF를 넣으면<br>고객 맞춤 보장 9쪽이 설계서 안에 들어감')}${stepper(2)}
${pts([
    ['', '설계서 한 건에 30~60초', 'AI를 쓰지 않아 외부 통신이 없음'],
    ['', '가입한 담보만 계산함', '0원 칸이 인쇄되지 않음. 금액 옆에 담보번호를 적음'],
    ['', '근거가 없으면 계산하지 않음', '틀린 금액 대신 빈칸과 사유 기록'],
    ['', '원본 설계서 담보사항 바로 뒤에 끼움', null],
  ], { x: 96, y: 330, w: 470, gap: 24 })}
${SPN.map((t, i) => { const x = 610 + (i % 5) * 245, y = i < 5 ? 300 : 650; return `${shot('sp/sp_p0' + (i + 1) + '.png', { x, y, w: 225, h: 300, cls: 'doc', crop: [0, 0, 794, 1059] })}<div class="lab" style="left:${x}px;top:${y + 308}px">${i + 1} ${t}</div>`; }).join('')}
${note('예시 고객 자료(이름 · 설계사 정보 가림)로 만든 9쪽', { x: 1590, y: 650, w: 234 })}`,
  `3 클로징 · 스마트 제안서
- 설계서는 담보를 나열만 함. 스마트 제안서는 "어떤 병이면 얼마"를 사례로 계산해 보여 줌
- 그 고객이 가입한 담보만 계산하므로 안 든 담보가 0원으로 찍히지 않음
- 질병코드와 금액은 약관에서만 가져옴. 근거가 없으면 빈칸 + 사유 로그`);

// 16 [3] 스마트 제안서 GA 디자인판 (디자인만 GA 가 정함 · TA채널 PA부문도 출력)
const GAN = ['표지', '보장 요약', '암 보장', '뇌·심 보장', '보장금액 세부내역'];
add(`${head('3 클로징', 'GA가 정한 디자인 그대로,<br>TA채널 PA부문도 같이 뽑음')}${stepper(2)}
${GAN.map((t, i) => { const x = 96 + i * 352; return `${shot('sp/ga_p0' + (i + 1) + '.png', { x, y: 310, w: 330, h: 467, cls: 'doc', crop: [0, 0, 794, 1123] })}<div class="lab" style="left:${x}px;top:790px">${t}</div>`; }).join('')}
${pts([
    ['', '디자인만 GA가 정함 · 채널 구분 없이 씀', 'TA채널 PA부문도 청약서 출력 · 상품설명서 출력 단계에서 같은 양식으로 출력'],
    ['', '보장 요약 칸 : 암 · 뇌심 · 주요수술 12 · 간병인', null],
  ], { x: 96, y: 840, w: 820, gap: 10 })}
${pts([
    ['', '세부내역은 빠지지 않음(2026-10-02 확정)', '보장 요약 칸마다 어느 특약 몇 원이 더해졌는지 보여 주는 계산서'],
  ], { x: 960, y: 840, w: 864 })}`,
  `3 클로징 · 스마트 제안서 GA 디자인판
- 디자인을 GA가 정했을 뿐 GA 전용이 아님. TA채널 PA부문도 청약서 출력 · 상품설명서 출력 단계에서 같은 양식으로 출력함
- GA 디자인 가안 그림 위에 값 글자만 얹는 방식. GA지원센터 수정사항(2026-10-22)까지 반영한 칸 구성
- 세부내역을 못 만들면 생성 자체를 실패로 처리함(빼고 내보내지 않음)
- 화면 값은 설계서 없이 지면 모양만 보는 미리보기의 가정값. 이름 · 번호는 가안 표기`);

// 17 [3] 세일즈북
const GBP = [['gb_p01', '표지'], ['gb_p02', '1장 요약'], ['gb_p04', '담보 지도'], ['gb_p06', '담보 해설'], ['gb_p08', '자주 묻는 질문']];
add(`${head('3 클로징', '같은 설계서로 상담용 가이드북도 만듦', '세일즈북 생성기 · 내장 샘플(통합간편 40세 남성)로 만든 18쪽')}${stepper(2)}
${shot('cap/gb/gb_app.png', { x: 96, y: 330, w: 520, h: 380, crop: [0, 0, 700, 640], marks: [[40, 100, 1], [40, 330, 2]] })}
${GBP.map(([f, t], i) => { const x = 650 + i * 238; return `${shot('cap/gb/' + f + '.png', { x, y: 330, w: 222, h: 314, cls: 'doc', crop: [0, 0, 794, 1123] })}<div class="lab" style="left:${x}px;top:654px">${t}</div>`; }).join('')}
${pts([[1, '설계서 PDF를 끌어다 놓거나 샘플을 고름', null], [2, '옵션 고르고 인쇄 · PDF로 저장', null]], { x: 96, y: 740, w: 520, gap: 10 })}
${pts([
    ['', '1장 요약 한 쪽만 들고도 상담을 시작함', '가입 담보 수 · 월 보험료 · 5갈래 타일 · 가입 첫 해 조건 · 상담 3층 구조'],
    ['', '담보 해설은 왼쪽에 약관 사실, 오른쪽에 고객에게 하는 말', '인터넷 없는 HTML 파일 하나. 설계서가 PC 밖으로 나가지 않음'],
  ], { x: 650, y: 720, w: 1174, gap: 16 })}`,
  `3 클로징 · 세일즈북 생성기
- 상품설명서(설계서) PDF를 넣으면 담보표 · 설명문 · Key Point · 면책감액표를 묶은 가이드북이 나옴
- 상담 전날 이걸로 말할 거리를 준비하고, 상담 날 스마트 제안서로 금액을 보여 주는 순서를 권함
- KT 제안 : 맞춤대화 요약리포트에 「내 보장 쉽게 보기」 장으로 붙이는 안`);

// 18 [3] 수술비 비교 (특약검색기 · 보상시뮬레이터 위 단추)
add(`${head('3 클로징', '"이 수술 몇 종이에요?"는<br>수술비 비교 단추로 바로 답함')}${stepper(2)}
${shot('cap/surg_q.png', { x: 96, y: 330, w: 840, h: 520, crop: [242, 27, 956, 847], marks: [[1110, 296, 1], [560, 392, 2]] })}
${shot('cap/surg_q2.png', { x: 984, y: 330, w: 840, h: 520, crop: [242, 280, 956, 592], marks: [[560, 690, 3]] })}
${pts([[1, '신체부위 · 질병 · 수술명 입력(예 : 백내장)', null], [2, '1-7종 · 131대 · 1-5종Ⅱ 세 특약에서 찾은 건수와 종 · 코드', null]], { x: 96, y: 874, w: 840, gap: 8 })}
${pts([[3, '1-5종Ⅱ는 수술명 기준 · 급여 비급여 무관', '같은 단추가 특약검색기와 보상시뮬레이터 화면 위에 함께 있음']], { x: 984, y: 874, w: 840 })}`,
  `3 클로징 · 수술비 비교
- 엑셀을 따로 열지 않고 도구 안 「수술비 비교」 단추로 답함
- 예 : 백내장 → 1-7종 2건(수정체 소절개 수술 · 후발성 백내장 수술, 둘 다 1종) · 131대 4건 · 1-5종Ⅱ 1건(백내장 · 수정체 관혈수술 1종)
- 같은 수술이라도 특약마다 지급 조건 · 등급이 다를 수 있음. 실제 지급은 약관 · 담보 구성으로 확인(화면 안내 문구 그대로)`);

sect(4, '청약 전에 인수 가능성과<br>바뀐 담보 · 병원 조건을 확인함', ['상품 라인업 · 알릴의무', '예외질환 판정', '상품 히스토리', '상급종합 지도'], 'tata_ok');

// 19 [4] 상품 라인업 · 알릴의무
add(`${head('4 계약체결', '청약 전에 상품과 알릴의무부터 맞춰 봄')}${stepper(3)}
${shot('cap/pr_card.png', { x: 96, y: 300, w: 840, h: 556, crop: [130, 40, 1180, 860], marks: [[170, 90, 1], [190, 525, 2]] })}
${shot('cap/pr_notice.png', { x: 984, y: 300, w: 840, h: 556, crop: [190, 60, 1060, 860], marks: [[230, 120, 3]] })}
${pts([[1, '장기상품 50종 카드 : 가입 연령 · 갱신/만기 · 종구분', null], [2, '상품마다 알릴의무 표', null]], { x: 96, y: 880, w: 840, gap: 8 })}
${pts([[3, '알릴의무 유형별 보기 : 같은 고지 유형 상품을 묶어 봄', null]], { x: 984, y: 880, w: 840 })}`,
  `4 계약체결 · 상품 라인업
- 상품구분(통합 · 간편 · 전용 · 단품 등)과 심사 · 고지유형으로 50종을 걸러 봄
- 알릴의무 유형별 탭은 3개월 · 1년 · 5년 고지 대상과 해당 상품 목록
- 케어프리 M-Basket(세만기)과 The좋은 M-Basket(연만기)은 다른 상품으로 따로 나옴`);

// 20 [4] 예외질환 판정
add(`${head('4 계약체결', '병력 고객은 청약 전에<br>간편보험 5개 설계유형을 한 번에 판정함')}${stepper(3)}
${shot('cap/pr_ex_treat.png', { x: 96, y: 330, w: 820, h: 526, crop: [160, 60, 1120, 760], marks: [[200, 160, 1], [200, 290, 2]] })}
${shot('cap/pr_ex_result.png', { x: 950, y: 330, w: 874, h: 526, crop: [190, 60, 1060, 760], marks: [[230, 120, 3]] })}
${pts([[1, '질환 검색 : 병명 · 흔한 이름 · 초성 · 질병코드', null], [2, '치료 이력 : 입원만/수술 · 일수 · 5년 내 수술 횟수', null]], { x: 96, y: 880, w: 820, gap: 8 })}
${pts([[3, '일반설계 · 3대진단 · 어깨/무릎/디스크 · 정기 · 유병자 실손 동시 판정', '예시 : 대장용종(양성) 완전제거 · 입원 2일 → 5개 모두 가능']], { x: 950, y: 880, w: 874 })}`,
  `4 계약체결 · 예외질환 판정
- 2026.10.16 시행 신기준과 종전 기준을 바꿔 볼 수 있음
- 결과 복사로 MeAI나 메신저에 붙임
- 참고용. 최종 인수 여부는 청약 심사 결과를 따름`);

// 21 [4] 불완전판매 사전 방지 : 상품 히스토리 · 병원 조건 특약
add(`${head('4 계약체결', '바뀐 담보와 병원 조건까지 짚어<br>설계 단계에서 불완전판매를 미리 막음')}${stepper(3)}
${shot('cap/hist_stop.png', { x: 96, y: 330, w: 840, h: 520, crop: [342, 27, 755, 847], marks: [[368, 351, 1]] })}
${shot('cap/cond_modal.png', { x: 984, y: 330, w: 840, h: 520, crop: [290, 56, 857, 840], marks: [[318, 245, 2]] })}
${pts([[1, '상품 히스토리 : 판매중단 · 신설 · 상품명 변경을 시간 순으로', '예 : 2026.10 통합간편 간병인지원 · 사용 입원일당(Ⅶ) 18종 삭제. 없어진 담보를 있다고 설명하는 실수를 막음']], { x: 96, y: 874, w: 840 })}
${pts([[2, '병원 조건이 붙은 특약 : 「지도 보기」로 병원까지 확인', '상급종합병원 · 권역심뇌혈관질환센터 · 암중점치료기관에서만 주는 특약은 고객이 다니는 병원이 해당하는지 설계 때 짚음']], { x: 984, y: 874, w: 840 })}`,
  `4 계약체결 · 불완전판매 사전 방지
- 상품 히스토리 : 2610 약관(2026.10.31) 기준 판매중단 2건(통합간편 간병인(Ⅶ) 18종 · 케어프리 장기요양급여금 3종)과 신설 · 상품명 변경이 시간 순으로 정리돼 있음
- "큰 병원이면 다 된다"는 오해를 설계 때 바로잡음. 특약 창의 「지도 보기」가 상급종합 지도로 이어짐
- 바뀐 내용과 병원 조건을 청약 전에 설명해 두면 나중 분쟁을 줄일 수 있음`);

sect(5, '아플 때 받을 특약과 병원 조건까지 챙기고,<br>갱신 · 상령일에 먼저 연락함', ['보상시뮬레이터 청구 안내', '상급종합 지도', '상품 히스토리', '프롬프트 「사후관리」 111개', 'CRM 룰렛 갱신 칸'], 'eco_doctor');

// 22 [5] 관리·소개
add(`${head('5 관리·소개', '아플 때 받을 특약을 빠짐없이 짚어 주면<br>소개가 나옴')}${stepper(4)}
${shot('cap/pm_s6.png', { x: 96, y: 330, w: 620, h: 430, crop: [90, 180, 1260, 815], marks: [[110, 200, 1]] })}
${shot('cap/tool_modal_cov.png', { x: 750, y: 330, w: 560, h: 430, crop: [290, 330, 860, 660], marks: [[320, 360, 2]] })}
${shot('cap/nz/fun_roulette.png', { x: 1344, y: 330, w: 480, h: 430, crop: [0, 304, 576, 516], marks: [[40, 519, 3]] })}
${pts([[1, '프롬프트 「사후관리/소개요청」 111개', '272개 중 가장 많음. 유방암 단계별 청구(수술 · 항암 · 방사선 · 재건) 같은 질문'], [2, '보장 분석 탭', '특약마다 사각지대 · 상위호환 특약. 보장 점검 자리에서 씀']], { x: 96, y: 790, w: 1214, gap: 14 })}
${pts([[3, 'CRM 룰렛 갱신 칸', '갱신 · 상령일이 다가온 고객 3명과 문구']], { x: 1344, y: 790, w: 480 })}`,
  `5 관리·소개
- 고객이 아프다고 연락하면 보상시뮬레이터에서 그 병명의 단계별 특약을 처음부터 확인함(@@SIMPAGE@@쪽 화면)
- 청구를 놓치지 않게 챙기는 것이 소개로 이어짐
- 1~2년 뒤 보장 점검 때는 스마트 제안서를 다시 뽑아 비교함`);

// 22-2 [5] 보상 안내 : 상급종합 지도 · 병원 조건 특약 · 상품 히스토리
add(`${head('5 관리·소개', '입원할 병원과 바뀐 이력을 확인해<br>보상 안내가 매끄러움', '병원 조건이 붙은 특약은 상급종합 지도로, 가입 뒤 바뀐 담보는 상품 히스토리로 확인함')}${stepper(4)}
${shot('cap/map_onco.png', { x: 96, y: 340, w: 880, h: 510, crop: [131, 24, 1177, 830], marks: [[160, 147, 1], [590, 207, 2]] })}
${shot('cap/cond_search.png', { x: 1010, y: 340, w: 814, h: 510, crop: [395, 290, 900, 590], marks: [[402, 322, 3], [448, 513, 4]] })}
${pts([[1, '지도 : 상급종합병원 47 · 암중점치료기관 16 · 권역심뇌혈관질환센터 15 · 권역외상센터 17', null], [2, '권역별 병원 목록 : 입원 · 수술할 병원이 해당하는지 바로 확인', null]], { x: 96, y: 874, w: 880, gap: 8 })}
${pts([[3, '「상급종합」 검색 : 병원 조건이 붙은 특약 52개', null], [4, '카드의 병원 표시(심뇌센터 · 암중점기관)로 함께 청구할 특약을 빠짐없이 안내', null]], { x: 1010, y: 874, w: 814, gap: 8 })}`,
  `5 관리·소개 · 보상 안내
- 고객이 수술 · 입원할 병원을 알려 오면 지도에서 상급종합 · 암중점치료기관 · 권역심뇌혈관질환센터인지 확인
- 해당하면 병원 조건이 붙은 특약까지 함께 청구 안내. 빠뜨리기 쉬운 보험금임
- 가입 당시 판과 지금 판이 다르면 상품 히스토리로 언제 무엇이 바뀌었는지 확인하고 설명`);

sect(6, '소개 받은 고객을<br>다음 바퀴의 첫 고객으로 들임', ['명패 제작기', '추천 슬롯 「동의 필요」'], 'success_thumbs');

// 23 [6] 새 고객발굴
add(`${head('6 새 고객발굴', '소개 받은 고객이 다음 바퀴의 첫 고객이 됨')}${stepper(5)}
${shot('cap/np_1.png', { x: 96, y: 300, w: 760, crop: [130, 60, 1180, 760], marks: [[175, 205, 1], [175, 365, 2]] })}
${shot('cap/np_plates.png', { x: 890, y: 300, w: 420, crop: [0, 0, 1076, 1440] })}
${pts([
    [1, '엑셀 명단 올리기', '이름 · 소속 · 기타 세 칸. 샘플 양식 제공'],
    [2, '행사명 · 테마 · 출력 방식', '삼각대 명패(150×70mm) 또는 폼텍 라벨. A4 인쇄'],
    ['', '초청 세미나 · 감사 모임', '소개 받은 고객과 기존 고객을 함께 부르는 자리에 씀'],
    ['', '추천 슬롯 「동의 필요」 사유', '아직 동의를 받지 않은 고객도 챙길 대상으로 띄움 → 다시 1단계'],
  ], { x: 1354, y: 300, w: 470, gap: 22 })}
${note('명패 명단은 가상 이름', { x: 890, y: 880 })}`,
  `6 새 고객발굴
- 명패 제작기는 원래 행사 · 시상식용. 고객 초청 세미나에 그대로 씀
- 소개 받은 고객은 터치 단계(운세 안부)부터 다시 시작
- 이 장에서 바퀴가 1단계로 돌아감`);

sect(7, '매일 미는 습관과 약관이라는 축,<br>한 바퀴 이야기와 지금 상태를 봄', ['미는 힘 · 홈 넛지 습관', '축 · 약관 하나', '가상 고객 한 바퀴', '지금 상태', '정리'], 'group_lineup',
  { chip: '마무리', title: '바퀴를 굴리는 힘', label: '이 부분에서 보는 것', mh: 110, wheel: { all: true, axleRed: true } });
HABIT_AT = S.length;
// 24 습관
add(`${head('미는 힘', '바퀴를 매일 미는 힘은 홈을 여는 습관에서 나옴', null, { chipGrey: true })}
${pts([
    ['', '오기 · 배우기 · 영업하기 세 고리', '출석 · 퀴즈 · 공지 · 화법 따라 쓰기 · 추천 고객 열기. 3개면 커피 응모권, 5개 다 하면 응모권 2장 더(예시값)'],
    ['', 'OX 스피드 챌린지 39문항', '약관 문항 15개는 특약검색기 약관 원문과 글자 대조'],
    ['', '빙고 · 지점 리그 · 주간 리캡 · 신인 7일 여정', '재미 장치 끝은 늘 "오늘 연락할 고객"이나 "오늘 배울 것"'],
  ], { x: 96, y: 290, w: 520, gap: 34 })}
${shot('cap/nz/card_quest.png', { x: 660, y: 250, w: 380 })}
${shot('cap/nz/fun_ox.png', { x: 1070, y: 250, w: 380, crop: [0, 0, 576, 576] })}
${shot('cap/nz/fx_bingo.png', { x: 1070, y: 660, w: 380 })}
${shot('cap/nz/card_league.png', { x: 1480, y: 250, w: 344 })}`,
  `미는 힘 · 습관
- 홈 넛지는 매일 홈을 열 이유를 만드는 장치임
- 오기 · 배우기 · 영업하기 세 고리를 매일 채우게 함
- 보상 · 경품 숫자는 확정 전 예시값. 「로또」 명칭은 「MeAI 행운번호」 대체안 있음`);

// 26 축
add(`${head('축', '바퀴의 축은 약관 하나임', '약관이 바뀌면 명령 하나로 세 갈래 산출물을 함께 다시 만듦', { chipGrey: true })}
<div class="card g" style="left:96px;top:330px;width:330px;height:300px"><span class="k">원천</span><h4 style="margin-top:10px">약관 PDF</h4><p>2610 판(판매개시 2026.10.31). 상품마다 최신 판 하나</p></div>
<div class="arrow" style="left:440px;top:450px">›</div>
<div class="card" style="left:480px;top:330px;width:420px;height:300px;border-color:var(--red-l)"><span class="k">특약 마스터</span><h4 style="margin-top:10px">tool.html 감수본 + 약관 파싱</h4><p>질병코드 · 지급표 · 같은 이름 특약 묶음</p></div>
<div class="arrow" style="left:914px;top:450px">›</div>
${[['영업지원도구 6종', '배포판 · 올인원 · 인터넷판'], ['스마트 제안서 · GA 디자인판', '설계서 → 맞춤 보장 지면'], ['세일즈북 생성기', '설계서 → 상담 가이드북']].map(([t, d], i) => `<div class="card" style="left:954px;top:${330 + i * 104}px;width:420px;height:92px;padding:18px 24px"><h4 style="font-size:22px">${t}</h4><p style="margin-top:2px;font-size:17px">${d}</p></div>`).join('')}
${pts([
    ['', '질병코드는 만들거나 짐작하지 않음', '약관 별표와 특약 마스터에서만 옴. 목록이 없으면 지급하지 않고 사유를 남김'],
    ['', '금액도 짐작하지 않음', '지급금액표에 없는 가입금액 · 항목은 계산에서 빼고 기록'],
    ['', '오류는 빈칸으로 드러나게 함', '틀린 금액은 그대로 고객에게 가지만 빈칸은 눈에 띄어 바로 고칠 수 있음'],
    ['', '설계서는 PC 밖으로 나가지 않음', '세일즈북 · 운세는 인터넷 없는 파일. 캡처의 설계사 정보는 가림'],
  ], { x: 1420, y: 300, w: 404, gap: 20 })}
${shot('cap/tool_modal_tab2.png', { x: 96, y: 680, w: 1278, h: 200, crop: [290, 430, 860, 280] })}
${note('특약검색기 「별표 · 분류표」 탭 : 보장 질병코드가 약관 별표에서 온다는 것을 화면에서 바로 확인', { x: 96, y: 902, w: 1278 })}`,
  `축 · 약관 하나
- 세 산출물(영업지원도구 · 스마트 제안서 · 세일즈북)이 같은 특약 마스터를 씀
- 약관 · tool.html · 추출기 중 무엇을 바꿔도 sync_all 한 번으로 세 갈래를 맞춤
- 질병코드 · 금액을 추정하지 않는 원칙이 모든 도구에 똑같이 걸려 있음`);

// 27 가상 고객 한 바퀴
const story = [
  ['고객발굴', '월요일 아침 추천 슬롯에 「상령일 2주」 사유로 뜸', 'cap/nz/fun_cslot.png', [0, 80, 576, 330]],
  ['터치', '오늘의 운세 그림을 카톡으로 보냄. 저녁에 답장이 옴', 'cap/unse/saju_share.png', [0, 0, 390, 223], 3],
  ['클로징', '"위암이면 얼마?" 질문에 네 도구로 답하고 스마트 제안서 9쪽으로 설명', 'sp/sp_p02.png', [0, 80, 794, 455]],
  ['계약체결', '대장용종 이력은 예외질환 판정으로 확인. 바뀐 담보 · 병원 조건까지 짚고 청약', 'cap/pr_ex_result.png', [200, 60, 520, 657]],
  ['관리·소개', '1년 뒤 입원할 병원이 상급종합인지 지도로 확인해 청구 안내. 언니를 소개함', 'cap/sim_stages.png', [150, 170, 520, 657]],
  ['새 고객발굴', '언니 부부를 초청 세미나에 초대. 명패에 이름을 넣음', 'cap/np_plates.png', [0, 0, 1076, 616]],
];
add(`${head('가상 사례', '가상 고객 김하늘 님으로 한 바퀴 돌려 봄', '1988년생 여성 · 이름과 상황은 모두 예시', { chipGrey: true })}
${story.map(([s, d, f, crop, dpr], i) => { const x = 96 + (i % 3) * 584, y = 300 + Math.floor(i / 3) * 340; return `<div class="card" style="left:${x}px;top:${y}px;width:560px;height:316px;padding:0;overflow:hidden">
<div style="position:absolute;left:0;top:0;width:250px;height:316px;overflow:hidden;background:var(--s1);border-right:1px solid var(--line)">${(() => { const [nw] = SZ[f]; const cw = nw / (dpr || 2); const sc = 250 / crop[2]; return `<img src="${url(f)}" style="position:absolute;max-width:none;width:${Math.round(cw * sc)}px;left:${Math.round(-crop[0] * sc)}px;top:${Math.round(-crop[1] * sc)}px">`; })()}</div>
<div style="position:absolute;left:276px;top:26px;right:24px"><span class="k" style="display:inline-flex;align-items:center;gap:8px;font-size:17px;font-weight:700;color:var(--red-s)"><b class="num" style="width:30px;height:30px;font-size:15px">${i + 1}</b>${s}</span><div class="pt-t" style="margin-top:14px;font-size:22px;line-height:1.45">${d}</div></div></div>`; }).join('')}`,
  `가상 사례
- 앞 장들의 화면을 한 사람 이야기로 이어 본 것
- 6단계 끝에서 소개 받은 언니가 다음 바퀴 1단계로 들어감
- 실제 고객 정보는 쓰지 않음`);

// 28 상태
add(`${head('지금 상태', '바로 쓰는 것과 개발이 필요한 것', null, { chipGrey: true })}
${[
    ['바로 사용', 'red', ['영업지원도구 6종(배포판 zip · 인터넷 없이 동작)', '특약검색기 · 보상시뮬레이터 위 수술비 비교 · 상급종합 지도 · 상품 히스토리 단추', '상품 라인업 예외질환 판정(2026.10.16 신기준)', '오늘의 운세 한 파일판']],
    ['프로토타입 · 시범 운영 전', '', ['스마트 제안서 생성기', '스마트 제안서 GA 디자인판(설계도 · IT 인계 문서 준비)', '세일즈북 생성기']],
    ['목업 · 개발 필요', 'dark', ['MeAI 홈 넛지 플레이 v5.1(API 28 · DB 표 35 · 배치 11 명세)', '오늘의 운세 사내 웹서버 탑재(패키지 준비)', '세일즈북 → 맞춤대화 요약리포트 「내 보장 쉽게 보기」']],
  ].map(([t, k, list], i) => `<div class="card" style="left:${96 + i * 584}px;top:280px;width:560px;height:540px">${tag(t, k)}
<div style="margin-top:22px;display:flex;flex-direction:column;gap:16px">${list.map(s => `<div style="display:flex;gap:12px"><b class="dot" style="margin:11px 4px 0 0"></b><span style="font-size:22px;font-weight:600;line-height:1.45;letter-spacing:-0.01em">${s}</span></div>`).join('')}</div></div>`).join('')}
${note('KT 제안 적용 순서(안) : 오늘의 운세 → 요약리포트 「내 보장 쉽게 보기」 → 홈 넛지 1차(출석 · 퀴즈 · 화법 · 루틴) → 2차(추첨 · 리그 · 행운 존)', { x: 96, y: 870, w: 1728 })}`,
  `지금 상태
- 바로 사용 : 현장에서 오늘 쓸 수 있는 것
- 프로토타입 : 실제 설계서로 점검 중이고 시범 운영 전
- 목업 · 개발 필요 : 사내 시스템(로그인 · 맞춤대화 · CRM · 알림톡) 연결이 필요해 KT 개발 공수 확인이 다음 일`);

// 29 마무리
add(`<div style="position:absolute;left:96px;top:250px;width:900px">
<span class="chip">정리</span>
<h2 class="title" style="font-size:72px;margin-top:28px;line-height:1.2">다음 바퀴는<br>소개에서 시작함</h2>
<p class="sub" style="font-size:28px;margin-top:30px">오늘 바로 쓸 수 있는 도구부터 현장에 풀고,<br>홈 넛지와 요약리포트 연동은 개발 협의로 넘김</p>
<div style="margin-top:56px;display:flex;flex-direction:column;gap:12px;font-size:22px;font-weight:600;color:var(--sub)">
<span>업데이트 · 오류 문의 : 세일즈혁신TF</span><span style="color:var(--faint);font-size:18px">내부 설계사 교육 · 업무용. 실제 보장 여부와 지급금액은 약관으로 확인해야 함</span></div></div>
<div class="panel" style="left:1080px;top:64px;width:744px;height:926px"></div>
${wheel(600, 1152, 120, { cur: 0 })}
${doll('group_lineup', 1152, 812, 150)}`,
  `정리
- 6단계가 끊기지 않게 이어지면 소개가 다음 바퀴를 엶
- 오늘 바로 쓸 수 있는 것부터 현장에 퍼뜨리고, 홈 넛지 · 요약리포트 연동은 개발 협의로 넘김
- 문의 : 세일즈혁신TF`);

if (S.length !== TOTAL) { console.error('장 수가 다름', S.length); process.exit(1); }
S.forEach(x => { x.notes = x.notes.replace('@@SIMPAGE@@', String(SIM_AT + 1)); });
{ // 바닥 진척 막대 채우기 (표지 · 간지는 빼고)
  const B = [0, ...DIV, S.length];
  S.forEach((x, i) => {
    let mini = '';
    if (i > 0 && !DIV.includes(i)) {
      const c = B.findIndex((b, k) => k < B.length - 1 && i >= b && i < B[k + 1]);
      const f = Math.round((i - B[c] + 1) / (B[c + 1] - B[c]) * 1000) / 10;
      mini = `<div class="mini"><div class="mr">${CHAPTERS.map((t, k) => `<div class="ms ${k < c ? 'done' : k === c ? 'cur' : ''}" style="flex:${B[k + 1] - B[k]}">${k === c ? `<i style="width:${f}%"></i><b style="left:${f}%"></b>` : ''}</div>`).join('')}</div><span class="ml">${CHAPTERS[c]}</span></div>`;
    }
    x.html = x.html.replace('@@MINI@@', mini);
  });
}
const BOUNDS = [0, ...DIV, S.length];                              // 구간 c = BOUNDS[c] ~ BOUNDS[c+1]-1 (0 부터 세는 장 번호)
DIV.forEach((d, i) => {
  S[d].html = S[d].html.replace('@@PROG@@', prog(i + 1, d + 1, BOUNDS));
  const end = i + 1 < DIV.length ? DIV[i + 1] : S.length;           // 다음 간지 바로 앞까지(마지막은 끝 장까지)
  const a = String(d + 2).padStart(2, '0'), b = String(end).padStart(2, '0');
  S[d].html = S[d].html.replace(`@@RANGE${i + 1}@@`, a === b ? `${a}쪽` : `${a}~${b}쪽`);
});

/* ── 굽기 ── */
(async () => {
  const name = process.argv[5] || 'meai_flywheel';
  const dir = path.join(OUT, name + '_slides'); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const html = `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>${CSS}</style></head><body>${S.map(s => s.html).join('\n')}</body></html>`;
  fs.writeFileSync(path.join(OUT, name + '.html'), html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1.5 });
  await p.goto('file://' + path.join(OUT, name + '.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
  const fontOk = await p.evaluate(() => document.fonts.check('700 40px "Pretendard Variable"', '가'));
  const broken = await p.evaluate(() => [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src.slice(-60)));
  const over = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s, i) => {
    const R = s.getBoundingClientRect(), bad = [];
    s.querySelectorAll('.pts,.pt,.card,.note,.lab,.tbl,.hd,.stepper,.tc,.shot,.phone').forEach(e => { const r = e.getBoundingClientRect(); if (r.width && (r.right > R.right - 40 || r.bottom > R.bottom - 70 || r.left < R.left + 40)) bad.push((e.className || e.tagName) + '@' + Math.round(r.right - R.left) + ',' + Math.round(r.bottom - R.top)); });
    // 글 상자끼리 겹침(같은 장 안 pts/card/note/lab) 점검
    const boxes = [...s.querySelectorAll(':scope > .pts, :scope > .note, :scope > .lab, :scope > .card, :scope > .shot, :scope > .phone, :scope > .tc')].map(e => [e.className.split(' ')[0], e.getBoundingClientRect()]);
    for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) { const A = boxes[a][1], B = boxes[c][1]; if (A.left < B.right - 2 && B.left < A.right - 2 && A.top < B.bottom - 2 && B.top < A.bottom - 2) bad.push('겹침 ' + boxes[a][0] + '×' + boxes[c][0]); }
    return bad.length ? (i + 1) + ': ' + [...new Set(bad)].slice(0, 6).join(' | ') : null;
  }).filter(Boolean));
  const els = await p.$$('.slide'); const files = [];
  for (let i = 0; i < els.length; i++) { const f = path.join(dir, String(i + 1).padStart(2, '0') + '.jpg'); await els[i].screenshot({ path: f, type: 'jpeg', quality: 90 }); files.push(f); }
  await b.close();
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.title = '플라이휠, 영업지원도구를 통한 영업프로세스 선순환'; pres.author = '세일즈혁신TF'; pres.company = '메리츠화재'; pres.subject = '고객발굴부터 소개까지 보조도구로 돌리는 영업 한 바퀴';
  files.forEach((f, i) => { const s = pres.addSlide(); s.background = { color: 'FFFFFF' }; s.addImage({ path: f, x: 0, y: 0, w: 13.333, h: 7.5, altText: S[i].notes.split('\n')[0] }); s.addNotes(S[i].notes); });
  const pptx = path.join(OUT, name + '.pptx'); await pres.writeFile({ fileName: pptx });
  fs.writeFileSync(path.join(OUT, name + '_files.json'), JSON.stringify(files));
  console.log('글꼴', fontOk, '| 깨진 그림', broken.length ? broken : 0, '| 점검', over.length ? '\n' + over.join('\n') : 0, '| 장', files.length, '|', pptx, (fs.statSync(pptx).size / 1048576).toFixed(1) + 'MB');
})();
