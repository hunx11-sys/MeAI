// 공용 머리 부분: 영업가족 방송판(v3). bcast.js 가 require 한다.
const path = require('path');
const L = require(process.env.LIB || path.join(__dirname,'..','build','lib.js'));
const { C, W, H, M } = L;
const CH = ['찾기','고르기','묻기','터치하기'];
const FOOT = 'MeAI 홈 · 영업가족 방송 · 2026.10';
const T=(s,t,o)=>L.T(s,t,o), R=(s,o)=>L.R(s,o);
function foot(s,no,dark){
  T(s,FOOT,{x:M,y:H-0.42,w:6,h:0.25,fontSize:10,color:dark?'FFFFFF':C.g500,transparency:dark?20:0});
  T(s,String(no),{x:W-M-1,y:H-0.42,w:1,h:0.25,fontSize:10,color:dark?'FFFFFF':C.g500,align:'right'});
}
// ch: 0~3 = 챕터 강조, -1 = 강조 없음
function head(pres,{kicker,title,sub,ch=-1,bg=C.white,kcolor}){
  const s=pres.addSlide(); s.background={color:bg};
  T(s,kicker,{x:M,y:0.38,w:6.4,h:0.34,fontSize:13,bold:true,color:kcolor||C.blue,valign:'middle'});
  const cw=1.3,gap=0.08, x0=W-M-(CH.length*cw+(CH.length-1)*gap);
  CH.forEach((c,i)=>{ const on=i===ch, x=x0+i*(cw+gap);
    R(s,{x,y:0.38,w:cw,h:0.34,fill:on?C.blue:C.g100,line:null,radius:0.17});
    T(s,`${i+1} ${c}`,{x,y:0.38,w:cw,h:0.34,fontSize:11.5,bold:on,color:on?'FFFFFF':C.g700,align:'center',valign:'middle'}); });
  T(s,title,{x:M,y:0.82,w:W-2*M,h:0.78,fontSize:34,bold:true,color:C.navy,valign:'middle'});
  if (sub) T(s,sub,{x:M,y:1.6,w:W-2*M,h:0.42,fontSize:17,color:C.g600,valign:'middle'});
  return s;
}
function badge(s,x,y,n,{d=0.46,color=C.blue,size=16}={}){ s.addShape('ellipse',{x,y,w:d,h:d,fill:{color},line:{color:'FFFFFF',width:1.5}}); T(s,String(n),{x,y,w:d,h:d,fontSize:size,bold:true,color:'FFFFFF',align:'center',valign:'middle'}); }
function pin(s,g,px,py,n,{clip={x:0,y:0},dsf=2,d=0.44,color=C.blue}={}){ const X=g.x+(px-clip.x)*dsf*g.scale, Y=g.y+(py-clip.y)*dsf*g.scale; badge(s,X-d/2,Y-d/2,n,{d,color,size:15}); }
function item(s,{x,y,w,n,title,desc,color=C.blue,ts=20,ds=15,dh=0.4}){ badge(s,x,y+0.02,n,{color}); T(s,title,{x:x+0.62,y,w:w-0.62,h:0.46,fontSize:ts,bold:true,color:C.navy,valign:'middle'}); if(desc) T(s,desc,{x:x+0.62,y:y+0.46,w:w-0.62,h:dh,fontSize:ds,color:C.g600,valign:'top',lineSpacingMultiple:1.15}); }
function bar(s,{x=M,y,w=W-2*M,h=0.8,text,label,size=20,tone='dark'}){
  const bg=tone==='dark'?C.navy:tone==='blue'?C.blue50:tone==='yellow'?C.yellow50:C.g100, fg=tone==='dark'?'FFFFFF':C.navy, lc=tone==='dark'?C.blue100:tone==='blue'?C.blue:tone==='yellow'?'B7791F':C.g700;
  R(s,{x,y,w,h,fill:bg,line:null,radius:0.14});
  const runs=[]; if(label) runs.push({text:label+'   ',options:{bold:true,color:lc,fontSize:size,fontFace:L.FONT}}); runs.push({text,options:{bold:tone==='dark',color:fg,fontSize:size,fontFace:L.FONT}});
  s.addText(runs,{x:x+0.35,y,w:w-0.7,h,isTextBox:true,margin:0,valign:'middle'});
}
function note2(s,x,y,w,text='※ 화면의 이름·숫자는 예시',align='right'){ T(s,text,{x,y,w,h:0.3,fontSize:12,color:C.g600,align,valign:'middle'}); }
function src(s,text,y=6.62){ T(s,text,{x:M,y,w:W-2*M,h:0.28,fontSize:12,color:C.g500,valign:'middle'}); }
function chipX(s,{x,y,text,fill,color,size=13,h=0.4}){ const w=L.textW(text,size)+0.4; R(s,{x,y,w,h,fill,line:null,radius:h/2}); T(s,text,{x,y,w,h,fontSize:size,bold:true,color,align:'center',valign:'middle'}); return w; }
module.exports = { L, C, W, H, M, CH, FOOT, T, R, foot, head, badge, pin, item, bar, note2, src, chipX };
