// 공통 스타일 도우미 : 첨부 HTML(55 PLAN, 토스 스타일)의 토큰을 그대로 옮김
const pptxgen = require('pptxgenjs');
const path = require('path');
const { applyTheme } = require(process.env.PPTX_APPLY_THEME || './apply_theme.js');

const T = {
  fg:'191F28', fg2:'4E5968', fg3:'8B95A1', fg4:'B0B8C1',
  bg:'FFFFFF', bg2:'F9FAFB', bg3:'F2F4F6', bg4:'E5E8EB', line:'E5E8EB', line2:'D1D6DB',
  blue:'3182F6', blueDark:'1B64DA', blueBg:'E8F3FF', blueBg2:'C9E2FF',
  red:'F04452', redBg:'FFEEF0', ink:'191F28', ink2:'2A3240', ink3:'333D4B', green:'4ADE80', amber:'F59E0B', amberBg:'FFF4E0',
};
const THEME = {
  name: 'MeAI Toss',
  headFontFace: 'Pretendard', bodyFontFace: 'Pretendard',
  colors: { dk1: T.fg, lt1: T.bg, dk2: T.fg2, lt2: T.bg3, accent1: T.blue, accent2: T.blueDark, accent3: T.red,
    accent4: T.blueBg, accent5: T.fg3, accent6: T.green, hlink: T.blueDark, folHlink: T.blueDark },
};
const W = 13.333, H = 7.5, M = 0.7;           // 16:9 와이드, 좌우 여백 0.7in
const CW = W - 2*M;                           // 본문 폭 11.93in
const FOOT = '입원적정성 교안 · 메리츠화재 세일즈혁신 · 2026. 10';

function makePres(total){
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = '세일즈혁신'; pres.title = '입원적정성 교안';
  const C = pres.SchemeColor;
  const foot = (fg, fgN) => ([
    { text: FOOT, options: { x: M, y: H-0.45, w: 7, h: 0.3, fontSize: 9, color: fg, margin: 0, fontFace:'Pretendard' } },
  ]);
  const num = (col) => ({ x: W-M-1.2, y: H-0.45, w: 1.2, h: 0.3, fontSize: 9, color: col, align:'right', margin:0, fontFace:'Pretendard' });
  pres.defineSlideMaster({ title:'LIGHT', background:{ color: T.bg }, objects:[ {text:{text:FOOT,options:{x:M,y:H-0.45,w:7,h:0.3,fontSize:9,color:T.fg4,margin:0}}} ], slideNumber: num(T.fg4) });
  pres.defineSlideMaster({ title:'ALT',   background:{ color: T.bg2 }, objects:[ {text:{text:FOOT,options:{x:M,y:H-0.45,w:7,h:0.3,fontSize:9,color:T.fg4,margin:0}}} ], slideNumber: num(T.fg4) });
  pres.defineSlideMaster({ title:'INK',   background:{ color: T.ink }, objects:[ {text:{text:FOOT,options:{x:M,y:H-0.45,w:7,h:0.3,fontSize:9,color:'6B7684',margin:0}}} ], slideNumber: num('6B7684') });
  pres.defineSlideMaster({ title:'BLUE',  background:{ color: T.blue }, objects:[ {text:{text:FOOT,options:{x:M,y:H-0.45,w:7,h:0.3,fontSize:9,color:'BFD9FF',margin:0}}} ], slideNumber: num('BFD9FF') });
  return pres;
}

// ---- 기본 글 도우미 -------------------------------------------------------
function txt(s, text, o){
  const base = { fontFace:'Pretendard', isTextBox:true, margin:0, valign:'top', color:T.fg, fontSize:14, breakLine:false };
  s.addText(text, Object.assign(base, o));
}
// 머리띠(kicker) : 둥근 알약 번호 + 제목, 오른쪽 쪽수 표시
function kicker(s, label, pg, dark){
  const pillW = Math.max(0.55, 0.16*label.length + 0.3);
  const fill = dark==='blue' ? '5B9BF8' : (dark ? '2F3A4A' : T.blueBg);
  s.addShape('roundRect', { x:M, y:0.52, w:pillW, h:0.3, fill:{ color: fill }, line:{ color: fill }, rectRadius:0.15 });
  txt(s, label, { x:M, y:0.52, w:pillW, h:0.3, fontSize:10, bold:true, color: dark ? 'FFFFFF' : T.blueDark, align:'center', valign:'middle' });
  if (pg) txt(s, pg, { x:W-M-2, y:0.52, w:2, h:0.3, fontSize:10, bold:true, color: dark==='blue' ? 'BFD9FF' : (dark ? '7A8594' : T.fg4), align:'right', valign:'middle' });
}
// 제목(주장 한 문장) : 왼쪽 정렬, 굵게
function title(s, text, o={}){
  txt(s, text, Object.assign({ x:M, y:0.95, w:CW, h:1.0, fontSize:24, bold:true, color:T.fg, charSpacing:-1, lineSpacingMultiple:1.18 }, o));
}
function sub(s, text, o={}){
  txt(s, text, Object.assign({ x:M, y:1.95, w:CW*0.85, h:0.5, fontSize:13, color:T.fg2, lineSpacingMultiple:1.3 }, o));
}
// 바닥 출처·주석
function note(s, text, o={}){
  txt(s, text, Object.assign({ x:M, y:H-0.9, w:CW, h:0.4, fontSize:9, color:T.fg3, lineSpacingMultiple:1.25, valign:'bottom' }, o));
}
// 카드
function card(s, x,y,w,h, variant='white'){
  const v = { white:{fill:T.bg, line:T.line}, soft:{fill:T.bg3, line:T.bg3}, bl:{fill:T.blueBg, line:T.blueBg}, rd:{fill:T.redBg, line:T.redBg},
              blue:{fill:T.blue, line:T.blue}, ink:{fill:T.ink, line:T.ink}, ink2:{fill:T.ink2, line:'3A4453'}, amber:{fill:T.amberBg, line:T.amberBg}, glass:{fill:'FFFFFF', line:'FFFFFF'} }[variant];
  const o = { x,y,w,h, fill:{ color:v.fill }, line:{ color:v.line, width:0.75 }, rectRadius:0.14 };
  if (variant==='glass') { o.fill = { color:'FFFFFF', transparency:84 }; o.line = { color:'FFFFFF', transparency:70, width:0.75 }; }
  if (variant==='white') o.shadow = { type:'outer', color:'191F28', blur:14, offset:3, angle:90, opacity:0.08 };
  s.addShape('roundRect', o);
}
// 알약 칩
function chip(s, x,y, text, variant='b', o={}){
  const v = { b:{fill:T.blueBg, c:T.blueDark}, g:{fill:T.bg3, c:T.fg2}, r:{fill:T.redBg, c:T.red}, k:{fill:T.fg, c:'FFFFFF'}, w:{fill:'3B4556', c:'FFFFFF'}, wb:{fill:'5B9BF8', c:'FFFFFF'}, a:{fill:T.amberBg, c:'B45309'}, gr:{fill:'E6F7EC', c:'1B7F3B'} }[variant];
  const fs = o.fontSize || 10;
  const w = o.w || (text.length*fs*0.0135 + 0.32);
  s.addShape('roundRect', { x,y,w,h:o.h||0.3, fill:{color:v.fill}, line:{color:v.fill}, rectRadius:0.15 });
  txt(s, text, { x,y,w,h:o.h||0.3, fontSize:fs, bold:true, color:v.c, align:'center', valign:'middle' });
  return w;
}
// 큰 숫자 통계
function stat(s, x,y,w, value, desc, o={}){
  txt(s, value, { x,y,w,h:0.75, fontSize:o.vs||36, bold:true, color:o.vc||T.fg, charSpacing:-2, valign:'bottom' });
  txt(s, desc, { x,y:y+0.8,w,h:o.dh||0.55, fontSize:o.ds||11, color:o.dc||T.fg2, lineSpacingMultiple:1.25 });
}
// 바닥 '한 줄 정리'(파란 점 + 굵은 문장)
function take(s, text, dark){
  const y = H-1.55;
  s.addShape('line', { x:M, y:y-0.15, w:CW, h:0, line:{ color: dark ? '3A4453' : T.line, width:0.75 } });
  s.addShape('ellipse', { x:M, y:y+0.13, w:0.14, h:0.14, fill:{color:T.blue}, line:{color:T.blue} });
  s.addShape('ellipse', { x:M-0.06, y:y+0.07, w:0.26, h:0.26, fill:{color:T.blue, transparency:80}, line:{color:T.blue, transparency:100} });
  txt(s, text, { x:M+0.38, y, w:CW-0.4, h:0.55, fontSize:14, bold:true, color: dark ? 'FFFFFF' : T.fg, lineSpacingMultiple:1.25, valign:'top' });
}
// 번호 동그라미
function numDot(s, x,y, n, color=T.fg, d=0.3){
  s.addShape('ellipse', { x,y,w:d,h:d, fill:{color}, line:{color} });
  txt(s, String(n), { x,y,w:d,h:d, fontSize:d>0.28?10:9, bold:true, color:'FFFFFF', align:'center', valign:'middle' });
}
// 흐름 상자 (→ 로 이어지는)
function flow(s, x,y, items, o={}){
  const h = o.h||0.42, fs=o.fs||11, gap=0.34; let cx=x;
  items.forEach((it,i)=>{
    const t = typeof it==='string' ? {t:it} : it;
    const w = t.w || (t.t.length*fs*0.0135+0.4);
    const v = { b:{f:T.blue,c:'FFFFFF'}, k:{f:T.fg,c:'FFFFFF'}, x:{f:T.redBg,c:T.red}, w:{f:'FFFFFF',c:T.fg}, g:{f:T.bg3,c:T.fg}, d:{f:'3B4556',c:'FFFFFF'} }[t.v||'g'];
    s.addShape('roundRect', { x:cx,y,w,h, fill:{color:v.f}, line:{color: t.v==='w'?T.line:v.f}, rectRadius:0.08 });
    txt(s, t.t, { x:cx,y,w,h, fontSize:fs, bold:true, color:v.c, align:'center', valign:'middle' });
    cx += w;
    if (i<items.length-1){ txt(s,'→',{x:cx,y,w:gap,h,fontSize:fs+1,bold:true,color:o.dark?'7A8594':T.fg4,align:'center',valign:'middle'}); cx+=gap; }
  });
  return cx;
}
// 표
function table(s, x,y,w, head, rows, o={}){
  const fs = o.fs||10.5, dark=o.dark;
  const hdr = head.map(h=>({ text:h, options:{ bold:true, fontSize:fs-1, color: dark?'9AA5B4':T.fg3, fill:{color: dark?'222B38':T.bg2}, valign:'middle' } }));
  const body = rows.map((r,ri)=> r.map((c,ci)=>{
    const cell = typeof c==='object' && c!==null && !Array.isArray(c) ? c : { text:String(c) };
    const op = Object.assign({ fontSize:fs, color: dark?'E5E8EB':T.fg, valign:'middle', bold: ci===0 || !!cell.bold, fill:{ color: cell.hl ? T.blueBg : (dark? T.ink2 : 'FFFFFF') } }, cell.options||{});
    if (cell.color) op.color = cell.color;
    if (cell.hl && !cell.color) op.color = T.blueDark;
    return { text: cell.text, options: op };
  }));
  s.addTable([hdr, ...body], { x,y,w, colW:o.colW, fontFace:'Pretendard', border:{ type:'solid', color: dark?'3A4453':T.line, pt:0.5 }, margin:[0.07,0.1,0.07,0.1], rowH:o.rowH||0.36, autoPage:false });
}
// 세로 막대(간단 비교)
function vbars(s, x,y,w,h, items, o={}){
  const n=items.length, gap=o.gap||0.25, bw=(w-gap*(n-1))/n, max=o.max||Math.max(...items.map(i=>i.v));
  items.forEach((it,i)=>{
    const bh = Math.max(0.08,(it.v/max)*(h-0.75)); const bx=x+i*(bw+gap); const by=y+(h-0.75)-bh;
    s.addShape('roundRect', { x:bx, y:by, w:bw, h:bh, fill:{color: it.c||T.blue}, line:{color: it.c||T.blue}, rectRadius:0.06 });
    txt(s, it.label, { x:bx-0.2, y:by-0.34, w:bw+0.4, h:0.3, fontSize:o.vfs||12, bold:true, color:o.dark?'FFFFFF':T.fg, align:'center', valign:'bottom' });
    txt(s, it.k, { x:bx-0.3, y:y+h-0.68, w:bw+0.6, h:0.6, fontSize:o.kfs||10, color:o.dark?'B0B8C1':T.fg2, align:'center', lineSpacingMultiple:1.2 });
  });
}
// 가로 막대 비교(라벨 | 막대 | 값)
function hbars(s, x,y,w, items, o={}){
  const lw=o.lw||2.2, vw=o.vw||1.0, bw=w-lw-vw-0.3, rh=o.rh||0.46, max=o.max||Math.max(...items.map(i=>i.v));
  items.forEach((it,i)=>{
    const cy=y+i*rh;
    txt(s, it.k, { x, y:cy, w:lw, h:rh-0.1, fontSize:o.fs||11, color:o.dark?'E5E8EB':T.fg, valign:'middle', bold:!!it.b });
    s.addShape('roundRect', { x:x+lw, y:cy+0.1, w:bw, h:rh-0.3, fill:{color:o.dark?'2F3A4A':T.bg4}, line:{color:o.dark?'2F3A4A':T.bg4}, rectRadius:0.1 });
    s.addShape('roundRect', { x:x+lw, y:cy+0.1, w:Math.max(0.12,bw*it.v/max), h:rh-0.3, fill:{color:it.c||T.blue}, line:{color:it.c||T.blue}, rectRadius:0.1 });
    txt(s, it.label, { x:x+lw+bw+0.15, y:cy, w:vw, h:rh-0.1, fontSize:o.fs||11, bold:true, color:o.dark?'FFFFFF':T.fg, valign:'middle' });
  });
}
const PARTS=[['01','입원적정성이란'],['02','고객이 손해 보는 사례'],['03','네 가지 배경'],['04','실손 재매입과 5세대'],['05','당사 특약 점검'],['06','현장 실천']];
// 부 구분 슬라이드 : 왼쪽 제목, 오른쪽 전체 순서(현재 부 강조, 지난 부는 초록 번호)
function divider(s, idx, ttl, subText){
  txt(s, 'PART '+PARTS[idx][0], { x:M, y:2.3, w:4, h:0.4, fontSize:12, bold:true, color:T.blue, charSpacing:3 });
  txt(s, ttl, { x:M, y:2.75, w:7.6, h:1.2, fontSize:50, bold:true, color:'FFFFFF', charSpacing:-3, valign:'top' });
  txt(s, subText, { x:M, y:4.0, w:7.4, h:1.1, fontSize:16, color:'B9C2CF', lineSpacingMultiple:1.4 });
  const x=M+8.4, w=CW-8.4;
  PARTS.forEach((p,i)=>{ const y=2.2+i*0.52; const on=i===idx, done=i<idx;
    if(on) s.addShape('roundRect',{x,y,w,h:0.46,fill:{color:'2A3240'},line:{color:'3A4453',width:0.75},rectRadius:0.08});
    txt(s,p[0],{x:x+0.2,y,w:0.45,h:0.46,fontSize:10,bold:true,color: on?T.blue:(done?T.green:'5B6573'),valign:'middle'});
    txt(s,p[1],{x:x+0.65,y,w:w-0.8,h:0.46,fontSize:12,bold:on,color: on?'FFFFFF':(done?'A9B3C1':'6B7684'),valign:'middle'}); });
}
module.exports = { divider, pptxgen, applyTheme, THEME, T, W, H, M, CW, makePres, txt, kicker, title, sub, note, card, chip, stat, take, numDot, flow, table, vbars, hbars };
