// Toss-style design helpers for pptxgenjs
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const React = require('react');
const ReactDOMServer = require('react-dom/server');

const FONT = '맑은 고딕';
const W = 13.333, H = 7.5;

const C = {
  g50:'F9FAFB', g100:'F2F4F6', g200:'E5E8EB', g300:'D1D6DB', g400:'B0B8C1', g500:'8B95A1',
  g600:'6B7684', g700:'4E5968', g800:'333D4B', g900:'191F28', white:'FFFFFF',
  blue:'3182F6', blueL:'E8F3FF', blueD:'1B64DA',
  red:'F04452', redL:'FFEEEE', redD:'D22030',
  orange:'FF8A00', orangeL:'FFF3E0',
  yellow:'FFC107', yellowL:'FFF8E1',
  green:'00C471', greenL:'E5F8EF', greenD:'059B5B',
  teal:'00B8A9', tealL:'E0F7F5',
  purple:'7C5CFC', purpleL:'F1EDFF',
  pink:'FF5C8D', pinkL:'FFE9F0',
  navy:'0F1B3D', indigo:'2D3E77',
};
const COLORS = ['blue','red','orange','green','purple','teal','pink','yellow'];
const LIGHT = { blue:C.blueL, red:C.redL, orange:C.orangeL, green:C.greenL, purple:C.purpleL, teal:C.tealL, pink:C.pinkL, yellow:C.yellowL };

function shadow(op=0.10, blur=10, off=2){ return {type:'outer', color:'000000', blur, offset:off, angle:90, opacity:op}; }

// ---------- image cache ----------
const cacheDir = path.join(__dirname, 'cache'); if(!fs.existsSync(cacheDir)) fs.mkdirSync(cacheDir);
const memo = {};
async function svgToPng(key, svg, width){
  const f = path.join(cacheDir, key + '.png');
  if(!fs.existsSync(f)){ await sharp(Buffer.from(svg)).resize(width).png().toFile(f); }
  return f;
}
async function gradientBg(name, stops, angle=135){
  const id = 'grad_'+name;
  const stopsSvg = stops.map((s,i)=>`<stop offset="${(i/(stops.length-1))*100}%" stop-color="#${s}"/>`).join('');
  // angle to x1,y1,x2,y2
  const a = angle*Math.PI/180; const x1 = 50-50*Math.cos(a), y1 = 50-50*Math.sin(a), x2=50+50*Math.cos(a), y2=50+50*Math.sin(a);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><defs><linearGradient id="g" x1="${x1}%" y1="${y1}%" x2="${x2}%" y2="${y2}%">${stopsSvg}</linearGradient></defs><rect width="1600" height="900" fill="url(#g)"/></svg>`;
  return svgToPng(id, svg, 1600);
}
async function blob(name, color, w=600, h=600){
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs><radialGradient id="r"><stop offset="0%" stop-color="#${color}" stop-opacity="0.55"/><stop offset="100%" stop-color="#${color}" stop-opacity="0"/></radialGradient></defs><rect width="${w}" height="${h}" fill="url(#r)"/></svg>`;
  return svgToPng('blob_'+name, svg, w);
}
// icons from react-icons
async function iconPng(setName, iconName, color, size=256){
  const key = `ic_${setName}_${iconName}_${color}`;
  const f = path.join(cacheDir, key+'.png');
  if(!fs.existsSync(f)){
    const set = require('react-icons/'+setName);
    const Icon = set[iconName]; if(!Icon) throw new Error('icon not found '+setName+'/'+iconName);
    let svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Icon, {color:'#'+color, size: size}));
    if(!svg.includes('xmlns')) svg = svg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
    await sharp(Buffer.from(svg)).resize(size, size).png().toFile(f);
  }
  return f;
}

// ---------- primitives ----------
function rect(s, p, x,y,w,h, fill, opt={}){
  s.addShape(p.ShapeType.rect, Object.assign({x,y,w,h, fill:{color:fill}, line:{color:fill, width:0}}, opt));
}
function card(s, p, x,y,w,h, opt={}){
  const fill = opt.fill || C.white; const r = opt.radius ?? 0.22;
  const o = {x,y,w,h, fill:{color:fill}, rectRadius:r, line:{color: opt.lineColor || fill, width: opt.lineWidth ?? 0}};
  if(opt.transparency){ o.fill.transparency = opt.transparency; o.line = {color: fill, width: 0, transparency: 100}; }
  if(opt.shadow !== false) o.shadow = shadow(opt.shadowOp ?? 0.08, opt.blur ?? 14, 3);
  s.addShape(p.ShapeType.roundRect, o);
}
function circle(s, p, x,y,d, fill, opt={}){
  s.addShape(p.ShapeType.ellipse, Object.assign({x,y,w:d,h:d, fill:{color:fill}, line:{color:fill, width:0}}, opt));
}
function text(s, x,y,w,h, t, opt={}){
  const o = Object.assign({x,y,w,h, fontFace:FONT, fontSize:14, color:C.g800, isTextBox:true, margin:0, valign:'top', align:'left', paraSpaceAfter:0, lineSpacingMultiple: 1.15}, opt);
  s.addText(t, o);
}
function pill(s, p, x,y, t, colorKey, opt={}){
  const fs = opt.fontSize || 11; const w = opt.w || (t.length*fs*0.0165 + 0.34); const h = opt.h || (fs*0.028+0.05);
  const bg = opt.solid ? C[colorKey] : (LIGHT[colorKey] || C.g100);
  const fg = opt.solid ? C.white : (C[colorKey+'D'] || C[colorKey] || C.g700);
  s.addShape(p.ShapeType.roundRect, {x,y,w,h, fill:{color:bg}, rectRadius: h/2, line:{color:bg,width:0}});
  text(s, x,y,w,h, t, {fontSize:fs, bold:true, color:fg, align:'center', valign:'middle'});
  return w;
}
async function icon(s, p, x,y,d, setName, iconName, colorKey, opt={}){
  // colored circle with white icon, or light circle with colored icon
  const solid = opt.solid ?? false;
  const bg = solid ? C[colorKey] : (LIGHT[colorKey] || C.g100);
  const ic = solid ? C.white : C[colorKey];
  if(opt.circle !== false) circle(s,p,x,y,d,bg);
  const f = await iconPng(setName, iconName, ic);
  const pad = opt.circle===false ? 0 : d*0.24;
  s.addImage({path:f, x:x+pad, y:y+pad, w:d-2*pad, h:d-2*pad});
}

// ---------- slide chrome ----------
let pageNo = 0;
function base(p, opt={}){
  const s = p.addSlide(); pageNo++;
  s.background = {color: opt.bg || C.g100};
  if(opt.dark){ s.background = {color: opt.bg || C.g900}; }
  if(!opt.noChrome){
    const fg = opt.dark ? C.g500 : C.g500;
    if(opt.chapter){ pill(s,p,0.6,0.42,opt.chapter, opt.chapterColor||'blue', {fontSize:10.5}); }
    text(s, 0.6, H-0.42, 8, 0.3, '세일즈혁신TF 이헌수 · 본 자료는 교육용으로 고객 교부·배포 및 온라인 게시가 불가하며, 계약의 세부사항은 약관을 따릅니다.', {fontSize:8.5, color:fg});
    text(s, W-1.6, H-0.42, 1.0, 0.3, String(pageNo), {fontSize:10, color:fg, align:'right', bold:true});
  }
  s._page = pageNo;
  return s;
}
function kLen(t){ let n=0; for(const ch of t){ n += /[\u3131-\uD79D\u4E00-\u9FFF\uFF00-\uFFEF「」]/.test(ch) ? 1 : (ch===' ' ? 0.35 : 0.62); } return n; }
function title(s, t, sub, opt={}){
  const y = opt.y ?? 0.85; const color = opt.color || C.g900; const w = opt.w || 12;
  let size = opt.size || 30; const maxSize = Math.floor((w-0.2)*72/(kLen(t)*0.98)); if(maxSize < size) size = Math.max(20, maxSize);
  text(s, 0.6, y, w, size*0.02+0.15, t, {fontSize:size, bold:true, color, valign:'top'});
  if(sub){ let ss = opt.subSize||14; const ms = Math.floor((w-0.2)*72/(kLen(sub)*0.98)); if(ms < ss) ss = Math.max(10.5, ms);
    text(s, 0.6, y + size*0.02+0.22, w, 0.5, sub, {fontSize: ss, color: opt.subColor || C.g600}); }
}
// chat with avatar. returns height used
function chat(s, p, y, t, side='left', opt={}){
  const fs = opt.fontSize || 12; const w = opt.w || 8.4; const av = 0.44;
  const charsPerLine = Math.max(8, Math.floor((w-0.4)/(fs*0.0136)));
  const lines = t.split('\n').reduce((n,l)=>n+Math.max(1,Math.ceil(kLen(l)/charsPerLine)),0);
  const h = Math.max(av, lines*fs*0.0225 + 0.24);
  const left = side==='left';
  const bx = left ? 0.6+av+0.15 : W-0.6-av-0.15-w;
  const ax = left ? 0.6 : W-0.6-av;
  const bg = left ? C.white : C.blue; const fg = left ? C.g900 : C.white;
  circle(s,p,ax,y,av, left ? C.orange : C.g800);
  text(s,ax,y,av,av, left ? '고객' : 'FP', {fontSize:8.5,bold:true,color:C.white,align:'center',valign:'middle'});
  s.addShape(p.ShapeType.roundRect, {x:bx,y,w,h, fill:{color:bg}, rectRadius:0.16, line:{color:bg,width:0}, shadow: shadow(0.06,8,2)});
  text(s, bx+0.2, y+0.12, w-0.4, h-0.24, t, {fontSize:fs, color:fg, valign:'middle'});
  return h;
}
function bullets(s, x,y,w,h, items, opt={}){
  const fs = opt.fontSize || 14;
  const arr = items.map((it,i)=>{
    const o = {text: (typeof it==='string'?it:it.text), options: Object.assign({bullet: opt.bullet===false?false:{indent:fs*1.2}, breakLine: i<items.length-1, paraSpaceAfter: opt.gap ?? fs*0.45}, (typeof it==='object'?it.options:{}))};
    return o;
  });
  text(s, x,y,w,h, arr, Object.assign({fontSize:fs, color: opt.color||C.g800, valign: opt.valign||'top'}, opt.textOpt||{}));
}
function stat(s, p, x,y,w,h, num, label, colorKey, opt={}){
  card(s,p,x,y,w,h,{fill: opt.fill || C.white});
  const nf = opt.numSize || 40;
  text(s, x+0.3, y+0.28, w-0.6, nf*0.02+0.15, num, {fontSize:nf, bold:true, color:C[colorKey]||colorKey});
  text(s, x+0.3, y+0.28+nf*0.02+0.2, w-0.6, h-(nf*0.02+0.6), label, {fontSize: opt.labelSize||13, color: C.g700});
  if(opt.tag) pill(s,p,x+0.3,y+h-0.5, opt.tag, colorKey, {fontSize:10});
}
function chatBubble(s, p, x,y,w, t, side='left', opt={}){
  const fs = opt.fontSize || 13;
  const charsPerLine = Math.max(8, Math.floor((w-0.5)/(fs*0.0138)));
  const lines = t.split('\n').reduce((n,l)=>n+Math.max(1,Math.ceil(l.length/charsPerLine)),0);
  const h = opt.h || (lines*fs*0.0235 + 0.36);
  const bg = side==='left' ? (opt.bg || C.white) : (opt.bg || C.blue);
  const fg = side==='left' ? C.g900 : C.white;
  s.addShape(p.ShapeType.roundRect, {x,y,w,h, fill:{color:bg}, rectRadius:0.18, line:{color:bg,width:0}, shadow: shadow(0.06,8,2)});
  text(s, x+0.25, y+0.17, w-0.5, h-0.34, t, {fontSize:fs, color:fg, valign:'middle'});
  if(opt.who) text(s, side==='left'?x:x+w-2.5, y-0.27, 2.5, 0.25, opt.who, {fontSize:9.5, color:C.g500, bold:true, align: side==='left'?'left':'right'});
  return h;
}
function table(s, rows, x,y,w, opt={}){
  const fs = opt.fontSize || 12; const colW = opt.colW; const headFill = opt.headFill || C.g800;
  const data = rows.map((r,ri)=> r.map((c,ci)=>({
    text: typeof c==='object' ? c.text : String(c),
    options: Object.assign({fontFace:FONT, fontSize: fs, color: ri===0 ? C.white : C.g800, bold: ri===0 || (opt.boldFirstCol && ci===0), fill:{color: ri===0 ? headFill : (ri%2 ? C.white : C.g50)}, align: ci===0 ? 'left' : 'center', valign:'middle', margin: [0.06,0.1,0.06,0.1]}, (typeof c==='object'?c.options:{}))
  })));
  s.addTable(data, {x,y,w, colW, rowH: opt.rowH || 0.42, border:{type:'solid', color:C.g200, pt:0.75}, fontFace:FONT});
}
function numBadge(s,p,x,y,d,n,colorKey,opt={}){
  circle(s,p,x,y,d,C[colorKey]);
  text(s,x,y,d,d,String(n),{fontSize:opt.fontSize|| d*30, bold:true, color:C.white, align:'center', valign:'middle'});
}
function arrowRight(s,p,x,y,w,h,color){
  s.addShape(p.ShapeType.rightArrow,{x,y,w,h,fill:{color},line:{color,width:0}});
}
function notes(s, t){ s.addNotes(t); }

module.exports = { FONT, W, H, C, COLORS, LIGHT, shadow, gradientBg, blob, iconPng, rect, card, circle, text, pill, icon, base, title, bullets, stat, chatBubble, chat, kLen, table, numBadge, arrowRight, notes, resetPage:()=>{pageNo=0;} };
