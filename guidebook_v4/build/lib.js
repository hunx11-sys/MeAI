// Toss 스타일 디자인 시스템 + 슬라이드 도우미 (pptxgenjs)
const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const sharp = require('sharp');

const C = {
  navy:'191F28', g800:'333D4B', g700:'4E5968', g600:'6B7684', g500:'8B95A1', g400:'B0B8C1', g300:'D1D6DB', g200:'E5E8EB', g100:'F2F4F6', g50:'F9FAFB', white:'FFFFFF',
  blue:'3182F6', blue700:'1B64DA', blue50:'E8F3FF', blue100:'C9E2FF',
  red:'F04452', red50:'FFF0F0', meritz:'E4262C',
  green:'00A86B', green50:'E9F9F1', orange:'FF8A00', orange50:'FFF4E6', purple:'7048E8', purple50:'F0EDFF', yellow:'FFC043', yellow50:'FFF8E1',
};
const FONT = '맑은 고딕';
const W = 13.333, H = 7.5, M = 0.6;
const FOOTER_TEXT = 'MeAI 활용 가이드북 v4 · CRM 대문 편 · 2026.10';
const IMG_CACHE = path.join(__dirname, 'img');
fs.mkdirSync(IMG_CACHE, {recursive:true});

function newPres(){ const p = new pptxgen(); p.layout = 'LAYOUT_WIDE'; p.lang = 'ko-KR'; p.author = '세일즈혁신TF'; p.title = 'MeAI 활용 가이드북 v4 · CRM 대문 편'; return p; }

// 텍스트 폭 추정(인치). 한글 1em, 영문/숫자 0.56em, 공백 0.3em
function textW(s, pt){ let w=0; for (const ch of s){ if (/[가-힣]/.test(ch)) w+=1.0; else if (ch===' ') w+=0.3; else if (/[A-Z0-9]/.test(ch)) w+=0.62; else if (/[·•]/.test(ch)) w+=0.4; else w+=0.52; } return w*pt/72; }

function T(slide, text, o){
  const base = { fontFace:FONT, isTextBox:true, margin:0, color:C.g700, fontSize:12, valign:'top', paraSpaceAfter:0 };
  slide.addText(text, Object.assign(base, o));
}
function R(slide, o){ // rounded rect
  const {x,y,w,h,fill=C.white,line=C.g200,lw=0.75,radius=0.12,shadow=false} = o;
  const opt = { x,y,w,h, fill:{color:fill}, rectRadius:radius };
  if (line) opt.line = {color:line, width:lw}; else opt.line = {color:fill, width:0};
  if (shadow) opt.shadow = { type:'outer', blur:8, offset:2, angle:90, color:'000000', opacity:0.07 };
  slide.addShape('roundRect', opt);
}
function circle(slide, {x,y,d,fill,line}){ slide.addShape('ellipse', {x,y,w:d,h:d, fill:{color:fill}, line:{color:line||fill, width:0}}); }
function footer(slide, pageNo, dark){
  T(slide, FOOTER_TEXT, { x:M, y:H-0.42, w:8, h:0.25, fontSize:9, color: dark?'FFFFFF':C.g500, transparency: dark?15:0 });
  T(slide, String(pageNo), { x:W-M-1, y:H-0.42, w:1, h:0.25, fontSize:9, color: dark?'FFFFFF':C.g500, align:'right' });
}
// 기본 콘텐츠 슬라이드: kicker(파랑) / 제목 / 부제
function base(pres, {kicker, title, sub, pageNo, bg=C.white, tag}){
  const s = pres.addSlide(); s.background = {color:bg};
  if (kicker) T(s, kicker, { x:M, y:0.42, w:9, h:0.28, fontSize:10.5, bold:true, color:C.blue });
  if (title) T(s, title, { x:M, y:0.68, w:W-2*M, h:0.6, fontSize:24, bold:true, color:C.navy, valign:'middle' });
  if (sub) T(s, sub, { x:M, y:1.3, w:W-2*M, h:0.42, fontSize:12.5, color:C.g600, valign:'middle' });
  if (tag){ const tw = textW(tag.text, 9.5)+0.4; R(s,{x:W-M-tw, y:0.42, w:tw, h:0.3, fill:tag.fill||C.red50, line:null, radius:0.15}); T(s, tag.text, {x:W-M-tw, y:0.42, w:tw, h:0.3, fontSize:9.5, bold:true, color:tag.color||C.red, align:'center', valign:'middle'}); }
  footer(s, pageNo, false);
  return s;
}
// 파트 구분 슬라이드
function divider(pres, {num, title, sub, learn=[], pageNo, color=C.blue}){
  const s = pres.addSlide(); s.background = {color};
  T(s, num, { x:W-6.2, y:0.9, w:5.6, h:3.2, fontSize:170, bold:true, color:'FFFFFF', transparency:82, align:'right', valign:'top' });
  T(s, `PART ${num}`, { x:M+0.2, y:1.5, w:6, h:0.35, fontSize:12, bold:true, color:'FFFFFF', transparency:25 });
  T(s, title, { x:M+0.2, y:1.9, w:8.5, h:1.6, fontSize:34, bold:true, color:'FFFFFF', valign:'top', lineSpacingMultiple:1.15 });
  if (sub) T(s, sub, { x:M+0.2, y:3.55, w:8.5, h:0.5, fontSize:14, color:'FFFFFF', transparency:15 });
  if (learn.length){
    T(s, '이 파트에서 배우는 것', { x:M+0.2, y:4.45, w:6, h:0.3, fontSize:11, bold:true, color:'FFFFFF', transparency:25 });
    learn.forEach((t,i)=>{ circle(s,{x:M+0.2,y:4.9+i*0.42+0.05,d:0.16,fill:'FFFFFF'}); T(s, t, { x:M+0.5, y:4.9+i*0.42, w:9, h:0.32, fontSize:12.5, color:'FFFFFF', valign:'middle' }); });
  }
  footer(s, pageNo, true);
  return s;
}
// 이미지: 둥근 모서리 프레임 처리 후 삽입. box 안에 비율 유지(contain). 반환 geometry
function frameImg(file, radius){
  const key = crypto.createHash('md5').update(file+'|'+radius+'|'+fs.statSync(file).mtimeMs).digest('hex').slice(0,10);
  const out = path.join(IMG_CACHE, path.basename(file, path.extname(file)) + '_' + key + '.png');
  if (!fs.existsSync(out)) execFileSync('python3', [path.join(__dirname,'frame.py'), file, out, String(radius)]);
  return out;
}
function imgSize(file){ const k = 'sz_'+file; if (!imgSize.c) imgSize.c={}; if (!imgSize.c[k]){ const buf = fs.readFileSync(file); const m = pngSize(buf); imgSize.c[k]=m; } return imgSize.c[k]; }
function pngSize(buf){ if (buf.readUInt32BE(0)===0x89504E47) return {w:buf.readUInt32BE(16), h:buf.readUInt32BE(20)}; throw new Error('not png'); }
const MISSING = [];
function img(slide, file, {x,y,w,h,round=true,radius=28,align='center',valign='middle',shadow=true,border=true}){
  if (!fs.existsSync(file)){ MISSING.push(file); R(slide,{x,y,w,h,fill:C.g100,line:C.g300,radius:0.12}); T(slide,'캡처 준비 중\n'+path.basename(file),{x,y,w,h,fontSize:9,color:C.g500,align:'center',valign:'middle'}); return {x,y,w,h,scale:0.001}; }
  const src = round ? frameImg(file, radius) : file;
  const {w:pw,h:ph} = imgSize(file);
  const sc = Math.min(w/pw, h/ph);
  const dw = pw*sc, dh = ph*sc;
  const dx = align==='left'? x : align==='right'? x+w-dw : x+(w-dw)/2;
  const dy = valign==='top'? y : valign==='bottom'? y+h-dh : y+(h-dh)/2;
  if (shadow) slide.addShape('roundRect', {x:dx, y:dy, w:dw, h:dh, fill:{color:C.white}, line:{color:C.white,width:0}, rectRadius:Math.min(0.14, dw*0.02), shadow:{type:'outer', blur:10, offset:3, angle:90, color:'000000', opacity:0.10}});
  slide.addImage({ path:src, x:dx, y:dy, w:dw, h:dh });
  return { x:dx, y:dy, w:dw, h:dh, scale: dw/pw };
}
// 캡처 좌표(원본 CSS px, dsf 반영 전) → 슬라이드 인치. g = img() 반환값, clip = 캡처 시 clip {x,y}, dsf
function pin(slide, g, px, py, n, {clip={x:0,y:0}, dsf=2, color=C.blue, d=0.34}={}){
  const X = g.x + (px-clip.x)*dsf*g.scale, Y = g.y + (py-clip.y)*dsf*g.scale;
  badge(slide, {x:X-d/2, y:Y-d/2, n, color, d});
}
function badge(slide, {x,y,n,color=C.blue,d=0.34,text}){
  slide.addShape('ellipse', {x,y,w:d,h:d, fill:{color}, line:{color:'FFFFFF', width:1.5}, shadow:{type:'outer', blur:4, offset:1, angle:90, color:'000000', opacity:0.25}});
  T(slide, text||String(n), {x,y,w:d,h:d, fontSize: d>0.3?11:9.5, bold:true, color:'FFFFFF', align:'center', valign:'middle'});
}
// 번호 설명 목록: items [{n, title, desc}]
function numList(slide, {x,y,w,items,gap=0.16,titleSize=12.5,descSize=10.5,color=C.blue, h}){
  let cy = y;
  const lineH = descSize*1.5/72;
  items.forEach(it=>{
    const descLines = Math.max(1, Math.ceil(textW(it.desc||'', descSize)/(w-0.5)));
    const bh = 0.3 + (it.desc? descLines*lineH + 0.06 : 0);
    badge(slide, {x, y:cy+0.02, n:it.n, color, d:0.3});
    T(slide, it.title, {x:x+0.42, y:cy, w:w-0.42, h:0.32, fontSize:titleSize, bold:true, color:C.navy, valign:'middle'});
    if (it.desc) T(slide, it.desc, {x:x+0.42, y:cy+0.32, w:w-0.42, h:descLines*lineH+0.05, fontSize:descSize, color:C.g600, lineSpacingMultiple:1.25});
    cy += bh + gap;
  });
  return cy;
}
// 칩
function chip(slide, {x,y,text,fill=C.blue50,color=C.blue,size=9.5,h=0.28,bold=true}){
  const w = textW(text,size)+0.3;
  R(slide,{x,y,w,h,fill,line:null,radius:h/2});
  T(slide,text,{x,y,w,h,fontSize:size,bold,color,align:'center',valign:'middle'});
  return w;
}
// 큰 숫자 타일
function stat(slide, {x,y,w,h,value,unit='',label,desc,accent=C.navy,fill=C.white,line=C.g200}){
  R(slide,{x,y,w,h,fill,line,radius:0.14});
  slide.addText([{text:value, options:{fontSize:30,bold:true,color:accent,fontFace:FONT}}, {text:unit?(' '+unit):'', options:{fontSize:13,color:C.g600,fontFace:FONT}}], {x:x+0.28,y:y+0.22,w:w-0.5,h:0.6,isTextBox:true,margin:0,valign:'middle'});
  T(slide,label,{x:x+0.28,y:y+0.88,w:w-0.5,h:0.3,fontSize:11.5,bold:true,color:C.navy});
  if (desc) T(slide,desc,{x:x+0.28,y:y+1.18,w:w-0.5,h:h-1.3,fontSize:10,color:C.g600,lineSpacingMultiple:1.25});
}
// 안내 박스
function note(slide, {x,y,w,h,label,text,tone='blue',size=11}){
  const tones = { blue:[C.blue50,C.blue], red:[C.red50,C.red], yellow:[C.yellow50,'B7791F'], grey:[C.g100,C.g700], dark:[C.navy,'FFFFFF'], green:[C.green50,C.green] };
  const [bg,fg] = tones[tone];
  R(slide,{x,y,w,h,fill:bg,line:null,radius:0.12});
  const runs = [];
  if (label) runs.push({text:label+'  ', options:{bold:true,color:fg,fontSize:size,fontFace:FONT}});
  runs.push({text, options:{color: tone==='dark'?'FFFFFF':C.g800, fontSize:size, fontFace:FONT}});
  slide.addText(runs, {x:x+0.25,y:y+0.1,w:w-0.5,h:h-0.2,isTextBox:true,margin:0,valign:'middle',lineSpacingMultiple:1.3});
}
// 단계 흐름: items [{n,title,desc,icon}] 가로 배치
function steps(slide, {x,y,w,h,items,accent=C.blue,activeIdx=-1}){
  const gap = 0.22; const cw = (w - gap*(items.length-1))/items.length;
  items.forEach((it,i)=>{
    const cx = x + i*(cw+gap);
    const active = i===activeIdx;
    R(slide,{x:cx,y,w:cw,h,fill: active?accent:C.white, line: active?null:C.g200, radius:0.14, shadow:!active});
    T(slide, it.step||`STEP ${it.n}`, {x:cx+0.22,y:y+0.2,w:cw-0.4,h:0.26,fontSize:9.5,bold:true,color: active?'FFFFFF':accent, transparency: active?20:0});
    T(slide, it.title, {x:cx+0.22,y:y+0.48,w:cw-0.4,h:0.5,fontSize:13.5,bold:true,color: active?'FFFFFF':C.navy, valign:'top', lineSpacingMultiple:1.15});
    if (it.desc) T(slide, it.desc, {x:cx+0.22,y:y+1.02,w:cw-0.4,h:h-1.15,fontSize:10,color: active?'FFFFFF':C.g600, lineSpacingMultiple:1.3});
    if (i<items.length-1) T(slide,'›',{x:cx+cw-0.02,y:y+h/2-0.2,w:gap+0.04,h:0.4,fontSize:16,color:C.g400,align:'center',valign:'middle'});
  });
}
// 불릿 목록
function bullets(slide, {x,y,w,h,items,size=11.5,color=C.g700,gap=6}){
  slide.addText(items.map((t,i)=>({text:t, options:{bullet:{indent:14}, breakLine:i<items.length-1, paraSpaceAfter:gap}})), {x,y,w,h,fontFace:FONT,fontSize:size,color,isTextBox:true,margin:0,valign:'top',lineSpacingMultiple:1.25});
}
// 표
function table(slide, {x,y,w,rows,colW,size=10,headFill=C.g100,rowH=0.32}){
  const data = rows.map((r,ri)=> r.map(c=>({text:String(c), options:{ fontFace:FONT, fontSize:size, bold:ri===0, color: ri===0?C.g700:C.navy, fill:{color: ri===0?headFill:C.white}, valign:'middle', margin:[3,6,3,6] }})));
  slide.addTable(data, {x,y,w,colW,rowH,border:{type:'solid',color:C.g200,pt:0.75}});
}
// 아이콘 원 (텍스트 심볼)
function iconCircle(slide,{x,y,d=0.5,symbol,fill=C.blue50,color=C.blue,size=16}){ circle(slide,{x,y,d,fill}); T(slide,symbol,{x,y,w:d,h:d,fontSize:size,bold:true,color,align:'center',valign:'middle'}); }

module.exports = { MISSING, C, FONT, W, H, M, newPres, T, R, circle, base, divider, img, pin, badge, numList, chip, stat, note, steps, bullets, table, iconCircle, textW, imgSize };

// ---- 추가 도우미 ----
// 번호 설명을 가로로 나열 (이미지 아래 범례)
function pinStrip(slide, {x,y,w,items,cols,size=10.5,rowH=0.5,color=C.blue}){
  cols = cols || items.length; const cw = w/cols;
  items.forEach((it,i)=>{ const cx = x + (i%cols)*cw, cy = y + Math.floor(i/cols)*rowH; badge(slide,{x:cx,y:cy+0.02,n:it.n,color,d:0.28}); T(slide, it.text, {x:cx+0.36,y:cy,w:cw-0.42,h:rowH,fontSize:size,color:C.g800,valign:'top',lineSpacingMultiple:1.2}); });
}
// 텍스트 카드
function card(slide, {x,y,w,h,kicker,title,desc,fill=C.white,line=C.g200,accent=C.blue,titleSize=13.5,descSize=10.5,icon,iconFill,iconColor,shadow=true,titleColor}){
  R(slide,{x,y,w,h,fill,line,radius:0.14,shadow});
  let ty = y+0.22;
  if (icon){ iconCircle(slide,{x:x+0.25,y:ty,d:0.46,symbol:icon,fill:iconFill||C.blue50,color:iconColor||accent,size:15}); ty += 0.6; }
  if (kicker){ T(slide,kicker,{x:x+0.25,y:ty,w:w-0.5,h:0.26,fontSize:9.5,bold:true,color:accent}); ty += 0.28; }
  if (title){ const lines = Math.max(1, Math.ceil(textW(title,titleSize)/(w-0.5))); T(slide,title,{x:x+0.25,y:ty,w:w-0.5,h:0.3*lines+0.05,fontSize:titleSize,bold:true,color:titleColor||C.navy,valign:'top',lineSpacingMultiple:1.15}); ty += 0.3*lines+0.12; }
  if (desc){ T(slide,desc,{x:x+0.25,y:ty,w:w-0.5,h:y+h-ty-0.15,fontSize:descSize,color:C.g600,valign:'top',lineSpacingMultiple:1.3}); }
}
function caption(slide,{x,y,w,text,align='center',size=9.5}){ T(slide,text,{x,y,w,h:0.28,fontSize:size,color:C.g500,align,valign:'middle'}); }
function label(slide,{x,y,w,text,color=C.g700,size=10.5}){ T(slide,text,{x,y,w,h:0.28,fontSize:size,bold:true,color,valign:'middle'}); }
function arrow(slide,{x,y,dir='›',size=22,color=C.g400,w=0.4,h=0.5}){ T(slide,dir,{x,y,w,h,fontSize:size,color,align:'center',valign:'middle'}); }
// 폰 캡처(이미 검은 프레임 포함) — 라운딩·그림자 없이
function phone(slide,file,{x,y,w,h,align='center',valign='top'}){ return img(slide,file,{x,y,w,h,round:false,shadow:false,align,valign}); }
// 표지
function cover(pres,{title,sub,line3,meta,file,pageNo}){
  const s = pres.addSlide(); s.background={color:C.navy};
  T(s,'메리츠화재 · 세일즈혁신TF',{x:M+0.2,y:0.8,w:6,h:0.3,fontSize:11,bold:true,color:'FFFFFF',transparency:35});
  T(s,title,{x:M+0.2,y:1.4,w:6.6,h:1.9,fontSize:44,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.12});
  T(s,sub,{x:M+0.2,y:3.45,w:6.6,h:0.9,fontSize:20,bold:true,color:C.blue100,valign:'top',lineSpacingMultiple:1.2});
  T(s,line3,{x:M+0.2,y:4.5,w:6.6,h:0.8,fontSize:12.5,color:'FFFFFF',transparency:20,valign:'top',lineSpacingMultiple:1.35});
  meta.forEach((m,i)=>{ const tw = textW(m,10)+0.4; const cx = M+0.2 + meta.slice(0,i).reduce((a,t)=>a+textW(t,10)+0.4+0.12,0); R(s,{x:cx,y:5.65,w:tw,h:0.32,fill:'2B3340',line:null,radius:0.16}); T(s,m,{x:cx,y:5.65,w:tw,h:0.32,fontSize:10,color:'FFFFFF',align:'center',valign:'middle'}); });
  if (file) img(s,file,{x:7.15,y:0.55,w:5.9,h:6.3,valign:'middle',align:'right'});
  footer(s,pageNo,true);
  return s;
}
module.exports.pinStrip = pinStrip; module.exports.card = card; module.exports.caption = caption; module.exports.label = label; module.exports.arrow = arrow; module.exports.phone = phone; module.exports.cover = cover;
