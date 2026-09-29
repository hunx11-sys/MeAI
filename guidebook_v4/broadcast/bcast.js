// MeAI 대문 30분 방송용 PPT — 가이드북 v4 디자인 부품(lib.js)과 캡처를 다시 쓴다.
// 사용: node bcast.js out.pptx   (CAPTURES 환경변수로 캡처 폴더 지정 가능)
const path = require('path'); const fs = require('fs');
const L = require(process.env.LIB || path.join(__dirname,'..','build','lib.js'));
const { C, W, H, M } = L;
const F = process.env.CAPTURES || path.join(__dirname,'..','captures');
const HERO=n=>`${F}/hero/${n}.png`, LEG=n=>`${F}/legacy/${n}.png`, AG=(d,n)=>`${F}/${d}/${n}.png`;
const SCRIPT = require('./script.js');
const CH = ['왜 바뀌나','대문','고객찾기','대화','오늘부터'];
const FOOT = 'MeAI 대문 · 30분 방송 · 2026.10';
const T=(s,t,o)=>L.T(s,t,o), R=(s,o)=>L.R(s,o);
const mmss = t=>`${String(Math.floor(t/60)).padStart(2,'0')}:${String(t%60).padStart(2,'0')}`;

function foot(s,no,dark){
  T(s,FOOT,{x:M,y:H-0.42,w:6,h:0.25,fontSize:10,color:dark?'FFFFFF':C.g500,transparency:dark?20:0});
  T(s,String(no),{x:W-M-1,y:H-0.42,w:1,h:0.25,fontSize:10,color:dark?'FFFFFF':C.g500,align:'right'});
}
function head(pres,{kicker,title,sub,ch=-1,bg=C.white}){
  const s=pres.addSlide(); s.background={color:bg};
  T(s,kicker,{x:M,y:0.38,w:6.2,h:0.34,fontSize:13,bold:true,color:C.blue,valign:'middle'});
  const cw=1.1,gap=0.08, x0=W-M-(CH.length*cw+(CH.length-1)*gap);
  CH.forEach((c,i)=>{ const on=i===ch, x=x0+i*(cw+gap);
    R(s,{x,y:0.38,w:cw,h:0.34,fill:on?C.blue:C.g100,line:null,radius:0.17});
    T(s,`${i+1} ${c}`,{x,y:0.38,w:cw,h:0.34,fontSize:11,bold:on,color:on?'FFFFFF':C.g700,align:'center',valign:'middle'}); });
  T(s,title,{x:M,y:0.82,w:W-2*M,h:0.78,fontSize:34,bold:true,color:C.navy,valign:'middle'});
  if (sub) T(s,sub,{x:M,y:1.6,w:W-2*M,h:0.42,fontSize:17,color:C.g600,valign:'middle'});
  return s;
}
function badge(s,x,y,n,{d=0.46,color=C.blue,size=16}={}){ s.addShape('ellipse',{x,y,w:d,h:d,fill:{color},line:{color:'FFFFFF',width:1.5}}); T(s,String(n),{x,y,w:d,h:d,fontSize:size,bold:true,color:'FFFFFF',align:'center',valign:'middle'}); }
function pin(s,g,px,py,n,{clip={x:0,y:0},dsf=2,d=0.44,color=C.blue}={}){ const X=g.x+(px-clip.x)*dsf*g.scale, Y=g.y+(py-clip.y)*dsf*g.scale; badge(s,X-d/2,Y-d/2,n,{d,color,size:15}); }
function item(s,{x,y,w,n,title,desc,color=C.blue,ts=20,ds=15}){ badge(s,x,y+0.02,n,{color}); T(s,title,{x:x+0.62,y,w:w-0.62,h:0.46,fontSize:ts,bold:true,color:C.navy,valign:'middle'}); if(desc) T(s,desc,{x:x+0.62,y:y+0.46,w:w-0.62,h:0.4,fontSize:ds,color:C.g600,valign:'top'}); }
function bar(s,{x=M,y,w=W-2*M,h=0.8,text,label,size=20,tone='dark'}){
  const bg=tone==='dark'?C.navy:tone==='blue'?C.blue50:tone==='yellow'?C.yellow50:C.g100, fg=tone==='dark'?'FFFFFF':C.navy, lc=tone==='dark'?C.blue100:tone==='blue'?C.blue:tone==='yellow'?'B7791F':C.g700;
  R(s,{x,y,w,h,fill:bg,line:null,radius:0.14});
  const runs=[]; if(label) runs.push({text:label+'   ',options:{bold:true,color:lc,fontSize:size,fontFace:L.FONT}}); runs.push({text,options:{bold:tone==='dark',color:fg,fontSize:size,fontFace:L.FONT}});
  s.addText(runs,{x:x+0.35,y,w:w-0.7,h,isTextBox:true,margin:0,valign:'middle'});
}
function note2(s,x,y,w,text='※ 추천 고객은 2차 오픈부터 · 화면의 이름·숫자는 예시',align='right'){ T(s,text,{x,y,w,h:0.3,fontSize:12,color:C.g600,align,valign:'middle'}); }
// 2차 오픈 안내 스티커 — 캡처 위나 카드 머리에 크게 붙인다
function open2(s,{x,y,right,text='2차 오픈부터 보여요',size=15,h=0.44}){ const w=L.textW(text,size)+0.5; const x0=right!=null?right-w:x; R(s,{x:x0,y,w,h,fill:C.navy,line:'FFFFFF',radius:h/2}); T(s,text,{x:x0,y,w,h,fontSize:size,bold:true,color:'FFFFFF',align:'center',valign:'middle'}); return w; }
function src(s,text,y=6.62){ T(s,text,{x:M,y,w:W-2*M,h:0.28,fontSize:12,color:C.g500,valign:'middle'}); }
function chipX(s,{x,y,text,fill,color,size=13,h=0.4}){ const w=L.textW(text,size)+0.4; R(s,{x,y,w,h,fill,line:null,radius:h/2}); T(s,text,{x,y,w,h,fontSize:size,bold:true,color,align:'center',valign:'middle'}); return w; }

const S=[]; // 슬라이드 함수, 대본과 같은 순서
// 1 표지
S.push((pres,no)=>{ const s=pres.addSlide(); s.background={color:C.navy};
  chipX(s,{x:M+0.2,y:0.95,text:'10월 MeAI 대문 오픈 · 30분 방송',fill:'2B3340',color:'FFFFFF',size:13});
  T(s,'찾는 영업에서,\n찾아가는 영업으로',{x:M+0.2,y:1.65,w:6.6,h:2.3,fontSize:50,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.1});
  T(s,'오늘 만날 고객과 첫 마디를\nMeAI 대문이 먼저 준비해요.',{x:M+0.2,y:4.15,w:6.4,h:1.1,fontSize:21,bold:true,color:C.blue100,valign:'top',lineSpacingMultiple:1.25});
  T(s,'메리츠화재 세일즈혁신TF · 2026.10',{x:M+0.2,y:5.95,w:6,h:0.35,fontSize:14,color:'FFFFFF',transparency:30});
  L.img(s,HERO('gate_full'),{x:7.25,y:0.8,w:5.5,h:5.9,valign:'middle',align:'right'});
  foot(s,no,true); });
// 2 순서
S.push((pres,no)=>{ const s=head(pres,{kicker:'오늘의 순서',title:'오늘 30분, 이 순서로 봐요'});
  const it=[['왜 바뀌나','4분','찾는 영업에서\n찾아가는 영업으로'],['대문','6분','문 6개 ·\n카드 한 장 읽기'],['고객찾기','5분','그룹 · 태그 색 ·\n동의'],['대화','4분','맞춤대화 ·\n새 기능 · 리포트'],['오늘부터','9분','3분 시연 · 약속 ·\n첫 5일']];
  const gap=0.2, cw=(W-2*M-gap*4)/5;
  it.forEach((c,i)=>{ const x=M+i*(cw+gap), y=1.95, h=3.45; R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.16,shadow:true});
    T(s,String(i+1),{x:x+0.3,y:y+0.28,w:1,h:0.7,fontSize:40,bold:true,color:C.blue,valign:'middle'});
    T(s,c[0],{x:x+0.3,y:y+1.1,w:cw-0.5,h:0.55,fontSize:24,bold:true,color:C.navy,valign:'middle'});
    chipX(s,{x:x+0.3,y:y+1.75,text:c[1],fill:C.blue50,color:C.blue,size:13,h:0.36});
    T(s,c[2],{x:x+0.3,y:y+2.3,w:cw-0.5,h:0.95,fontSize:15,color:C.g600,valign:'top',lineSpacingMultiple:1.25}); });
  bar(s,{y:5.75,h:0.95,label:'끝나고 할 일은 하나',text:'대문이 열리면, 매일 아침 대문 열기',size:24});
  foot(s,no); });
// 3 찾는 일
S.push((pres,no)=>{ const s=head(pres,{kicker:'1 · 왜 바뀌나',title:'영업은 늘 "찾는 일"부터였어요',ch:0});
  const q=[['누구에게','연락하지?'],['왜','지금이지?'],['무슨 말로','시작하지?']]; const gap=0.2, cw=(W-2*M-gap*2)/3;
  q.forEach((c,i)=>{ const x=M+i*(cw+gap); R(s,{x,y:1.9,w:cw,h:1.7,fill:C.g50,line:null,radius:0.16});
    s.addText([{text:c[0]+' ',options:{bold:true,color:C.navy,fontSize:28,fontFace:L.FONT}},{text:c[1],options:{color:C.g700,fontSize:28,fontFace:L.FONT}}],{x:x+0.35,y:1.9,w:cw-0.5,h:1.7,isTextBox:true,margin:0,valign:'middle'}); });
  [['7%','보유 고객 중 영업 시도 비율'],['2%','이관 고객 중 영업 시도 비율']].forEach((c,i)=>{ const x=M+i*(cw+gap), y=3.85, h=2.55; R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.16});
    s.addText([{text:c[0],options:{fontSize:72,bold:true,color:C.red,fontFace:L.FONT}},{text:'  미만',options:{fontSize:24,bold:true,color:C.red,fontFace:L.FONT}}],{x:x+0.35,y:y+0.25,w:cw-0.5,h:1.3,isTextBox:true,margin:0,valign:'middle'});
    T(s,c[1],{x:x+0.35,y:y+1.65,w:cw-0.5,h:0.5,fontSize:19,bold:true,color:C.navy,valign:'middle'}); });
  R(s,{x:M+2*(cw+gap),y:3.85,w:cw,h:2.55,fill:C.navy,line:null,radius:0.16});
  T(s,'문제는 의지가 아니라\n순서예요.',{x:M+2*(cw+gap)+0.4,y:3.85,w:cw-0.7,h:2.55,fontSize:26,bold:true,color:'FFFFFF',valign:'middle',lineSpacingMultiple:1.3});
  src(s,'출처: 세일즈혁신TF 「MeAI CRM 대문 고도화 제안」 2026.09');
  foot(s,no); });
// 4 MeAI가 먼저
S.push((pres,no)=>{ const s=head(pres,{kicker:'1 · 왜 바뀌나',title:'이제는 MeAI가 먼저 찾아와요',ch:0});
  const rows=[['누구에게','오늘의 추천 고객이 보여줘요'],['왜 지금','이유 한 문장이 붙어 있어요'],['첫 마디','카드 문장이 곧 첫 마디예요']];
  rows.forEach((r,i)=>{ const y=1.95+i*1.3; R(s,{x:M,y,w:7.3,h:1.12,fill:C.g50,line:null,radius:0.16});
    T(s,r[0],{x:M+0.35,y,w:1.7,h:1.12,fontSize:19,bold:true,color:C.g700,valign:'middle'});
    T(s,'›',{x:M+1.95,y,w:0.4,h:1.12,fontSize:28,color:C.blue,valign:'middle',align:'center'});
    T(s,r[1],{x:M+2.45,y,w:4.75,h:1.12,fontSize:23,bold:true,color:C.navy,valign:'middle'}); });
  const g4=L.img(s,HERO('reco1_card1'),{x:8.25,y:1.95,w:4.48,h:3.5,valign:'top',align:'right'});
  open2(s,{right:g4.x+g4.w-0.15,y:g4.y-0.24});
  note2(s,8.0,5.5,4.73,'※ 화면의 이름·숫자는 예시');
  bar(s,{y:5.95,h:0.85,label:'기억할 것',text:'발굴은 시스템이, 설득은 사람이.',size:22});
  foot(s,no); });

// 5 숫자
S.push((pres,no)=>{ const s=head(pres,{kicker:'1 · 왜 바뀌나',title:'MeAI를 쓴 경우 체결전환율이 2.8배 높았어요',sub:'MeAI 권한을 받은 분 열 명 중 아홉 분(91.1%)이 한 번 이상 써봤어요.',ch:0});
  const it=[['2.8배','체결전환율','안 쓴 경우 12.7%\n→ 쓴 경우 35.4%',C.blue],['4배','같은 FP의 고객끼리 비교','안 쓴 경우 9.0%\n→ 쓴 경우 36.0%',C.navy],['2.3배','질문 3개 이상 이어 쓰면','가계약 11.99건\n→ 27.79건 (질문 1개 대비)',C.purple]];
  const gap=0.25, cw=(W-2*M-gap*2)/3;
  it.forEach((c,i)=>{ const x=M+i*(cw+gap), y=2.3, h=3.95; R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.18,shadow:true});
    T(s,c[0],{x:x+0.4,y:y+0.3,w:cw-0.6,h:1.45,fontSize:80,bold:true,color:c[3],valign:'middle'});
    T(s,c[1],{x:x+0.4,y:y+1.95,w:cw-0.6,h:0.55,fontSize:22,bold:true,color:C.navy,valign:'middle'});
    T(s,c[2],{x:x+0.4,y:y+2.6,w:cw-0.6,h:1.0,fontSize:17,color:C.g600,valign:'top',lineSpacingMultiple:1.25}); });
  src(s,'출처: 데이터분석팀 「MeAI 사용 실태 분석」·「MeAI 효과 분석」, 2026.08 · TA 개인영업 채널 기준');
  foot(s,no); });
// 6 진입점
S.push((pres,no)=>{ const s=head(pres,{kicker:'2 · 대문',title:'10월 2일부터, MeAI로 가는 문이 6개예요',ch:1});
  L.img(s,HERO('portal_entry_full'),{x:M,y:1.85,w:8.35,h:4.75,valign:'top',align:'left'});
  const x=9.25, w=W-M-x;
  T(s,'새로 생긴 문',{x,y:1.9,w,h:0.45,fontSize:20,bold:true,color:C.blue,valign:'middle'});
  const row=(n,t,y,sub)=>{ T(s,n,{x,y,w:0.45,h:0.5,fontSize:22,bold:true,color:C.red,valign:'middle'}); T(s,t,{x:x+0.5,y,w:w-0.5,h:0.5,fontSize:17,bold:true,color:C.navy,valign:'middle'}); if(sub) T(s,sub,{x:x+0.5,y:y+0.45,w:w-0.5,h:0.36,fontSize:13.5,color:C.g600,valign:'middle'}); };
  row('③','롤링배너',2.42); row('④','CRM 리스트 · 고객 줄마다',2.98,'[MeAI 일반대화] [MeAI 맞춤대화]'); row('⑤','떠 있는 MeAI 버튼',3.9);
  R(s,{x,y:4.5,w,h:0.52,fill:C.blue50,line:null,radius:0.12}); T(s,'권한과 상관없이 누구나*',{x:x+0.2,y:4.5,w:w-0.3,h:0.52,fontSize:16,bold:true,color:C.blue,valign:'middle'});
  T(s,'원래 있던 문',{x,y:5.22,w,h:0.4,fontSize:18,bold:true,color:C.g600,valign:'middle'});
  T(s,'①② 왼쪽 위 · ⑥ 오른쪽 메뉴\n사용권한이 있어야 열려요',{x,y:5.62,w,h:0.8,fontSize:15,color:C.g600,valign:'top',lineSpacingMultiple:1.25});
  src(s,'* 적용 시점은 IT 개발 일정에 따라 달라질 수 있어요.');
  foot(s,no); });
// 7 대문 한 화면
S.push((pres,no)=>{ const s=head(pres,{kicker:'2 · 대문',title:'대문 한 화면에 오늘 할 일이 다 있어요',ch:1});
  const g=L.img(s,HERO('gate_full'),{x:M,y:1.8,w:6.2,h:5.05,valign:'top',align:'left'});
  const c={clip:{x:0,y:0}}; pin(s,g,60,110,1,c); pin(s,g,60,245,2,c); pin(s,g,60,400,3,c); pin(s,g,60,800,4,c); pin(s,g,60,1200,5,c); pin(s,g,1412,100,6,c);
  const x=6.85, w=W-M-x;
  [['인사 · 업데이트 시각','오른쪽 시각이 데이터 기준'],['대화 카드 두 장','일반대화 · 맞춤대화'],['내 고객 숫자 4개','"사전조회 동의 필요"가 늘었나'],['오늘의 추천 고객','카드 3장 × 3세트 · 2차 오픈부터'],['범례','AI 추천 고객 리본 · 동의 · 고객 유형'],['오른쪽 위','[글씨 확대] · [고객 동의] · [게시판]']].forEach((r,i)=> item(s,{x,y:1.85+i*0.84,w,n:i+1,title:r[0],desc:r[1],ts:19,ds:14.5}));
  foot(s,no); });
// 8 카드 한 장
S.push((pres,no)=>{ const s=head(pres,{kicker:'2 · 대문',title:'카드 한 장에 누구·왜·다음 행동이 있어요',ch:1});
  const g=L.img(s,HERO('gate_card_z'),{x:M,y:1.8,w:5.3,h:4.72,valign:'top',align:'left'});
  const o={clip:{x:160,y:625},dsf:3}; pin(s,g,163,718,1,o); pin(s,g,163,864,2,{...o,d:0.38}); pin(s,g,163,903,3,{...o,d:0.38}); pin(s,g,163,966,4,o);
  open2(s,{right:g.x+g.w-0.2,y:g.y-0.2});
  note2(s,M,6.58,g.w+0.3,'※ 예시 데이터','left');
  const x=6.35, w=W-M-x;
  [['연락할 이유','"부담보 해제가 5일 남았습니다."'],['태그','#이벤트 임박 · #보장 공백 · #당월 타겟'],['사전조회동의 D-n','만료까지 남은 날 · 보이면 바로 시작'],['[MeAI 고객찾기에서 열기]','이 고객 카드로 바로 이동']].forEach((r,i)=> item(s,{x,y:1.9+i*0.9,w,n:i+1,title:r[0],desc:r[1],ts:20,ds:15}));
  bar(s,{x,y:5.62,w,h:1.2,label:'전화로는',text:'"고객님, 제한됐던 담보가 5일 뒤 풀려요.\n그때 부족한 보장도 봐 드릴게요."',size:17});
  foot(s,no); });

// 9 두 가지 길
S.push((pres,no)=>{ const s=head(pres,{kicker:'2 · 대문',title:'맞춤대화로 가는 길은 두 가지예요',ch:1});
  const cw=(W-2*M-0.3)/2, y=1.85, h=4.25;
  [[ '길 1 · 이름을 알면','대문 [맞춤대화] → 고객 검색','이름 한 글자면\n목록이 좁혀져요.\n\n회색 줄 =\n오늘 철회',HERO('bc_search_top'),3.3],
   [ '길 2 · 누구에게 할지 모를 때','추천 카드 → 고객찾기 → 시작','[MeAI 고객찾기에서\n열기] → [이 고객으로\n맞춤대화 시작]\n\n클릭 두 번',HERO('reco1_card1'),2.75]].forEach((c,i)=>{ const x=M+i*(cw+0.3);
    R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.18,shadow:true});
    T(s,c[0],{x:x+0.35,y:y+0.25,w:cw-0.6,h:0.42,fontSize:17,bold:true,color:C.blue,valign:'middle'});
    if(i===1) open2(s,{right:x+cw-0.3,y:y+0.24,text:'2차 오픈부터',size:14,h:0.42});
    T(s,c[1],{x:x+0.35,y:y+0.68,w:cw-0.6,h:0.5,fontSize:21,bold:true,color:C.navy,valign:'middle'});
    L.img(s,c[3],{x:x+0.3,y:y+1.35,w:c[4],h:2.7,valign:'top',align:'left',shadow:false});
    T(s,c[2],{x:x+c[4]+0.5,y:y+1.35,w:cw-c[4]-0.75,h:2.7,fontSize:15.5,color:C.g700,valign:'top',lineSpacingMultiple:1.3}); });
  bar(s,{y:6.42,h:0.55,text:'남은 날짜(D-n)가 보이면 바로 시작, "동의 필요"면 동의부터.',size:17,tone:'blue'});
  foot(s,no); });

// 10 고객찾기 세 단
S.push((pres,no)=>{ const s=head(pres,{kicker:'3 · 고객찾기',title:'왼쪽 그룹, 가운데 카드, 오른쪽 다음 행동',ch:2});
  const g=L.img(s,HERO('find_full'),{x:M,y:2.25,w:8.4,h:4.6,valign:'top',align:'left'});
  const k=2*g.scale, zones=[[6,62,288,832],[303,62,686,832],[996,62,440,832]];
  zones.forEach((z,i)=>{ s.addShape('roundRect',{x:g.x+z[0]*k,y:g.y+z[1]*k,w:z[2]*k,h:z[3]*k,fill:{type:'none'},line:{color:C.blue,width:2.5},rectRadius:0.08}); badge(s,g.x+z[0]*k+z[2]*k/2-0.23,1.74,i+1,{d:0.46}); });
  const x=9.3, w=W-M-x;
  [['고객 그룹','연락 이유별로 묶여 있어요'],['고객 카드','이유 · 태그 · 한눈에 보기 6칸'],['다음 행동','추천 질문 · [맞춤대화 시작]']].forEach((r,i)=> item(s,{x,y:2.0+i*1.25,w,n:i+1,title:r[0],desc:r[1],ts:21,ds:15}));
  R(s,{x,y:5.85,w,h:0.9,fill:C.g50,line:null,radius:0.12}); T(s,'검색창엔 이름도,\n"암진단비" 같은 조건도.',{x:x+0.2,y:5.85,w:w-0.3,h:0.9,fontSize:14,color:C.g700,valign:'middle',lineSpacingMultiple:1.25});
  foot(s,no); });
// 11 그룹 · 태그 색
S.push((pres,no)=>{ const s=head(pres,{kicker:'3 · 고객찾기',title:'그룹이 곧 연락 이유, 태그 색으로 한눈에',ch:2});
  const x1=M, w1=6.55;
  [['우선순위 1','당월 영업 타겟','이번 달 회사가 집중하는 담보의 대상 고객',C.purple],['우선순위 2','우량 고객 · 날짜 임박','증권 5건 이상 · 월 50만원 이상 · 상령일 · 생일 · 동의 만료',C.blue],['우선순위 3','부족 7종','암 · 뇌 · 심 · 표적항암 · 종수술비 · 지원일당 · 치아',C.g700]].forEach((r,i)=>{ const y=1.85+i*1.4, h=1.25;
    R(s,{x:x1,y,w:w1,h,fill:C.g50,line:null,radius:0.14});
    badge(s,x1+0.3,y+0.37,i+1,{d:0.52,color:r[3],size:18});
    T(s,r[1],{x:x1+1.05,y:y+0.14,w:w1-1.3,h:0.52,fontSize:22,bold:true,color:C.navy,valign:'middle'});
    T(s,r[2],{x:x1+1.05,y:y+0.68,w:w1-1.3,h:0.42,fontSize:14.5,color:C.g700,valign:'middle'}); });
  R(s,{x:x1,y:6.05,w:w1,h:0.85,fill:C.blue50,line:null,radius:0.14});
  T(s,'언제 열까',{x:x1+0.3,y:6.05,w:1.2,h:0.85,fontSize:15,bold:true,color:C.blue,valign:'middle'});
  T(s,'월초 → 당월 영업 타겟 · 매주 월요일 → 상령일·생일\n한 달에 한 번 → 사전동의 만료',{x:x1+1.45,y:6.05,w:w1-1.6,h:0.85,fontSize:14,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.2});
  const x2=7.5, w2=W-M-x2;
  R(s,{x:x2,y:1.85,w:w2,h:5.05,fill:C.white,line:C.g200,radius:0.16});
  chipX(s,{x:x2+0.3,y:2.05,text:'NEW',fill:C.blue50,color:C.blue,size:12,h:0.36});
  T(s,'부족 태그 7색',{x:x2+1.15,y:2.03,w:w2-1.3,h:0.4,fontSize:20,bold:true,color:C.navy,valign:'middle'});
  ['cancer','brain','heart','target','surgery','daily','tooth'].forEach((n,i)=>{ const col=i<4?0:1, row=i<4?i:i-4; L.img(s,HERO('v2_chip_'+n),{x:x2+0.3+col*2.55,y:2.6+row*0.5,w:2.4,h:0.4,round:false,shadow:false,align:'left',valign:'top'}); });
  const g=L.img(s,HERO('v2_card_tags_z'),{x:x2+0.25,y:4.72,w:w2-0.5,h:1.65,valign:'top',align:'left',shadow:false});
  s.addShape('roundRect',{x:g.x+62*g.scale,y:g.y+338*g.scale,w:1030*g.scale,h:96*g.scale,fill:{type:'none'},line:{color:C.blue,width:2},rectRadius:0.06});
  T(s,'여러 개 붙어도 색으로 바로 구분돼요',{x:x2+0.3,y:6.45,w:w2-0.5,h:0.32,fontSize:13.5,color:C.g600,valign:'middle'});
  foot(s,no); });

// 12 동의
S.push((pres,no)=>{ const s=head(pres,{kicker:'3 · 고객찾기',title:'"D-n"이면 바로, "필요"면 알림톡 한 통',ch:2});
  const rows=[['유효 · D-n',C.blue,C.blue50,AG('gate020','31_row_normal_zoom'),'바로 [맞춤대화]'],['필요 · 만료',C.red,C.red50,HERO('fix_c_consent_request_btn'),'[사전조회동의 요청하기]\n→ 휴대폰 번호 → 알림톡'],['오늘 철회',C.g600,C.g100,AG('gate020','34_row_revoked_zoom'),'정보 확인 불가 · 다시 동의']];
  rows.forEach((r,i)=>{ const y=1.85+i*1.35, h=1.18;
    R(s,{x:M,y,w:W-2*M,h,fill:C.white,line:C.g200,radius:0.14});
    chipX(s,{x:M+0.3,y:y+h/2-0.22,text:r[0],fill:r[2],color:r[1],size:15,h:0.44});
    L.img(s,r[3],{x:2.75,y:y+0.12,w:5.9,h:h-0.24,valign:'middle',align:'left',shadow:false});
    T(s,r[4],{x:8.9,y,w:W-M-8.9-0.2,h,fontSize:18,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.2}); });
  bar(s,{y:5.95,h:0.82,label:'반영',text:'동의하면 15분 안팎에 반영 · 대문 [고객 동의]에서도 보내요',size:17,tone:'blue'});
  foot(s,no); });
// 13 맞춤대화
S.push((pres,no)=>{ const s=head(pres,{kicker:'4 · 대화',title:'질문이 채워진 채로 대화가 열려요',ch:3});
  const g=L.img(s,HERO('fix_c_custom_q'),{x:M+0.3,y:1.8,w:6.0,h:5.05,valign:'top',align:'left'});
  const o={clip:{x:445,y:0},dsf:2}; pin(s,g,432,128,1,o); pin(s,g,432,541,2,o); pin(s,g,432,798,3,o);
  const x=7.2, w=W-M-x;
  [['가입 계약이 먼저 보여요','약관 자료 준비 상태도 함께'],['MeAI가 볼 내용을 알려줘요','이번 대화에서 쓰일 보험 가입 내역'],['추천 질문이 들어가 있어요','전송만 누르면 돼요']].forEach((r,i)=> item(s,{x,y:1.9+i*0.95,w,n:i+1,title:r[0],desc:r[1],ts:19,ds:14.5}));
  R(s,{x,y:4.85,w,h:1.95,fill:C.g50,line:null,radius:0.14});
  T(s,'답변은 이 순서로 와요',{x:x+0.3,y:4.97,w:w-0.5,h:0.4,fontSize:15,bold:true,color:C.g600,valign:'middle'});
  [['잘 갖춘 것',C.green],['비어 있는 것',C.red],['이제 할 일',C.blue]].forEach((c,i)=>{ const cw=(w-0.6-0.3)/3, cx=x+0.3+i*(cw+0.15); R(s,{x:cx,y:5.5,w:cw,h:1.0,fill:C.white,line:null,radius:0.12}); T(s,c[0],{x:cx,y:5.5,w:cw,h:1.0,fontSize:17,bold:true,color:c[1],align:'center',valign:'middle'}); });
  foot(s,no); });
// 14 새 기능 세 가지
S.push((pres,no)=>{ const s=head(pres,{kicker:'4 · 대화',title:'새로 생긴 기능 세 가지',ch:3});
  const it=[['글씨 확대',HERO('v2_switch_on_z'),'대문 · 고객찾기 · 게시판 오른쪽 위.\n기본 ON, 끄면 원래 크기.',false],['용어 설명',HERO('fix_term_tooltip'),'[용어]를 켜고 표시된 말을 누르면\n고객 눈높이 뜻풀이가 떠요.',true],['모드 변경',HERO('bc_mode_dropdown'),'고객 앞에선 간편 분석,\n약관 따질 땐 상세 분석.',true]];
  const gap=0.25, cw=(W-2*M-gap*2)/3;
  it.forEach((c,i)=>{ const x=M+i*(cw+gap), y=1.85, h=4.95; R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.18,shadow:true});
    T(s,c[0],{x:x+0.3,y:y+0.25,w:cw-0.5,h:0.55,fontSize:24,bold:true,color:C.navy,valign:'middle'});
    chipX(s,{x:x+0.3,y:y+0.88,text:c[3]?'개발 진행 중 · 오픈 시 세부 변경 가능':'NEW · 10월',fill:c[3]?C.red50:C.blue50,color:c[3]?C.red:C.blue,size:11,h:0.34});
    R(s,{x:x+0.25,y:y+1.4,w:cw-0.5,h:2.2,fill:C.g50,line:null,radius:0.12});
    L.img(s,c[1],{x:x+0.35,y:y+1.5,w:cw-0.7,h:2.0,valign:'middle',align:'center',shadow:false});
    T(s,c[2],{x:x+0.3,y:y+3.8,w:cw-0.5,h:0.95,fontSize:16,color:C.g700,valign:'top',lineSpacingMultiple:1.3}); });
  foot(s,no); });
// 15 요약 리포트
S.push((pres,no)=>{ const s=head(pres,{kicker:'4 · 대화',title:'상담 내용은 요약 리포트로 카톡에',ch:3});
  const st=[['요약 생성',LEG('report_step1')],['골라서 편집',LEG('report_step2')],['리포트 생성',LEG('report_step3')],['카톡 도착 · 7일 열람',HERO('bc_kakao')]];
  const gap=0.3, cw=(W-2*M-gap*3)/4;
  st.forEach((c,i)=>{ const x=M+i*(cw+gap); if(i<3) L.phone(s,c[1],{x,y:1.8,w:cw,h:3.75}); else L.img(s,c[1],{x,y:2.3,w:cw,h:2.9,valign:'top',align:'center'});
    badge(s,x+0.05,5.72,i+1,{d:0.42,size:15}); T(s,c[0],{x:x+0.55,y:5.7,w:cw-0.55,h:0.46,fontSize:18,bold:true,color:C.navy,valign:'middle'});
    if(i<3) T(s,'›',{x:x+cw+0.02,y:3.3,w:gap-0.04,h:0.6,fontSize:28,color:C.g400,align:'center',valign:'middle'}); });
  bar(s,{y:6.3,h:0.55,label:'보내기 전',text:'숫자 · 약관 근거 · 개인정보 확인. "AI로 생성된 보조자료" 표시가 붙어요.',size:15,tone:'yellow'});
  T(s,'2026.06 실제 화면 · 이름은 가렸어요',{x:W-M-4,y:5.25,w:4,h:0.3,fontSize:11,color:C.g500,align:'right',valign:'middle'});
  foot(s,no); });
// 16 시연
S.push((pres,no)=>{ const s=head(pres,{kicker:'5 · 오늘부터 · 시연',title:'최수영 고객, 3분이면 돼요',sub:'부담보 해제 D-5 · 대문에서 리포트까지 그대로 따라 해 보세요. (추천 카드는 2차 오픈부터)',ch:4});
  const st=[['대문 카드 읽기','30초',HERO('reco1_card1')],['카드 펼치기','30초',HERO('bc_choi_card_z')],['맞춤대화 시작','30초',HERO('find_right_choi')],['질문 · 꼬리질문','1분 30초',null]];
  const gap=0.28, cw=(W-2*M-gap*3)/4;
  st.forEach((c,i)=>{ const x=M+i*(cw+gap); R(s,{x,y:2.15,w:cw,h:2.75,fill:C.g50,line:null,radius:0.14});
    if (c[2]) L.img(s,c[2],{x:x+0.15,y:2.22,w:cw-0.3,h:2.6,valign:'middle',align:'center',shadow:false});
    if (i===1){ const t='장기 4건 · 부족 1,000만원'; const w=L.textW(t,13)+0.4; R(s,{x:x+(cw-w)/2,y:4.3,w,h:0.44,fill:C.navy,line:null,radius:0.22}); T(s,t,{x:x+(cw-w)/2,y:4.3,w,h:0.44,fontSize:13,bold:true,color:'FFFFFF',align:'center',valign:'middle'}); }
    if (i===3){ R(s,{x:x+0.2,y:2.4,w:cw-0.4,h:1.75,fill:C.white,line:C.blue,radius:0.16}); T(s,'MeAI에게',{x:x+0.4,y:2.52,w:cw-0.8,h:0.3,fontSize:12,bold:true,color:C.blue,valign:'middle'});
      T(s,'"부담보가 해제되는\n담보와 다시 설계할\n특약을 정리해줘"',{x:x+0.4,y:2.85,w:cw-0.8,h:1.2,fontSize:15,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.25});
      T(s,'→ 꼬리질문 · 통화 후 리포트',{x:x+0.2,y:4.3,w:cw-0.4,h:0.4,fontSize:14,bold:true,color:C.g700,align:'center',valign:'middle'}); }
    badge(s,x,5.02,i+1,{d:0.42,size:15}); T(s,c[0],{x:x+0.52,y:5.0,w:cw-0.52,h:0.46,fontSize:18,bold:true,color:C.navy,valign:'middle'});
    T(s,c[1],{x:x+0.52,y:5.44,w:cw-0.52,h:0.32,fontSize:14,bold:true,color:C.blue,valign:'middle'});
    if(i<3) T(s,'›',{x:x+cw,y:3.2,w:gap,h:0.6,fontSize:26,color:C.g400,align:'center',valign:'middle'}); });
  const bw=(W-2*M-0.25)/2;
  bar(s,{x:M,y:5.95,w:bw,h:0.9,label:'고객에게',text:'"제한됐던 담보가 5일 뒤 풀려요."',size:16});
  bar(s,{x:M+bw+0.25,y:5.95,w:bw,h:0.9,label:'3분이면',text:'전화할 준비가 끝나요',size:17,tone:'blue'});
  foot(s,no); });

// 17 관리자
S.push((pres,no)=>{ const s=head(pres,{kicker:'5 · 오늘부터 · 관리자',title:'아침 조회에서는 세 문장이면 충분해요',ch:4});
  const q=[['숫자로','"같은 FP 안에서 비교해도 체결전환율이 9%에서 36%로 올라갑니다."',C.blue,C.blue50],['타겟으로','"다시 권한부여 받을 분, 한동안 안 쓰신 분 계실까요?"',C.green,C.green50],['행동으로','"10월부터 MeAI 대문이 열립니다. 조회 때 함께 열어보겠습니다."','FFFFFF',C.blue]];
  q.forEach((c,i)=>{ const y=1.85+i*1.42, h=1.25, w=8.2, dark=i===2; R(s,{x:M,y,w,h,fill:dark?C.blue:C.white,line:dark?null:C.g200,radius:0.16,shadow:!dark});
    chipX(s,{x:M+0.3,y:y+0.2,text:c[0],fill:dark?'FFFFFF':c[3],color:dark?C.blue:c[2],size:13,h:0.36});
    T(s,c[1],{x:M+0.3,y:y+0.58,w:w-0.55,h:0.6,fontSize:18.5,bold:true,color:dark?'FFFFFF':C.navy,valign:'middle'}); });
  const x=9.1, w=W-M-x;
  R(s,{x,y:1.85,w,h:2.7,fill:C.navy,line:null,radius:0.16});
  T(s,'이번 달 최우선',{x:x+0.3,y:2.0,w:w-0.5,h:0.4,fontSize:15,bold:true,color:C.blue100,valign:'middle'});
  T(s,'한동안 안 쓰신 4,912명께\n"대문 열어 보세요"',{x:x+0.3,y:2.42,w:w-0.5,h:0.85,fontSize:16.5,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.25});
  T(s,'12차월 넘은 기존 FP\n먼저 챙기기\n(체결전환율 격차 3.9배)',{x:x+0.3,y:3.3,w:w-0.5,h:1.2,fontSize:16.5,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.25});
  R(s,{x,y:4.7,w,h:1.55,fill:C.red50,line:null,radius:0.16});
  T(s,'과장은 금물',{x:x+0.3,y:4.82,w:w-0.5,h:0.4,fontSize:15,bold:true,color:C.red,valign:'middle'});
  T(s,'"빨라진다" 대신\n"성사된다"',{x:x+0.3,y:5.22,w:w-0.5,h:0.9,fontSize:18,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.2});
  src(s,'출처: 데이터분석팀 「MeAI 사용 실태 분석」·「MeAI 효과 분석」, 2026.08');
  foot(s,no); });
// 18 약속
S.push((pres,no)=>{ const s=head(pres,{kicker:'5 · 오늘부터',title:'오래 잘 쓰는 다섯 가지 약속',ch:4});
  const it=[['답변은\n검증 후 사용','약관·증권으로\n직접 확인해요'],['개인정보\n입력 금지','이름·연락처·주소·\n주민번호 입력 금지'],['동의 없으면\n보지 않기','우회 말고\n동의부터'],['미검증 책임은\n사용자에게','금융소비자보호법 등\n법령상 책임'],['자료 외부\n반출 금지','답변·화면·자료\n외부 제공 금지']];
  const gap=0.2, cw=(W-2*M-gap*4)/5;
  it.forEach((c,i)=>{ const x=M+i*(cw+gap), y=1.9, h=3.7; R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.16,shadow:true});
    T(s,String(i+1),{x:x+0.3,y:y+0.25,w:1,h:0.7,fontSize:36,bold:true,color:i<2?C.red:C.blue,valign:'middle'});
    T(s,c[0],{x:x+0.3,y:y+1.05,w:cw-0.45,h:1.2,fontSize:21,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15});
    T(s,c[1],{x:x+0.3,y:y+2.4,w:cw-0.45,h:1.1,fontSize:14.5,color:C.g600,valign:'top',lineSpacingMultiple:1.3}); });
  R(s,{x:M,y:5.8,w:W-2*M,h:0.95,fill:C.g50,line:null,radius:0.14});
  T(s,'MeAI 화면 하단 안내문  "MeAI의 답변은 생성형 AI를 통해 작성되어 오류가 있을 수 있으므로, 반드시 직접 근거자료를 확인하여 진위를 검증하시기 바랍니다. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다."',{x:M+0.3,y:5.8,w:W-2*M-0.6,h:0.95,fontSize:12,color:C.g700,valign:'middle',lineSpacingMultiple:1.25});
  foot(s,no); });
// 19 첫 5일
S.push((pres,no)=>{ const s=head(pres,{kicker:'5 · 오늘부터',title:'첫 5일, 하루 하나씩만 해보세요',sub:'첫 사용이 빠를수록 오래 써요(데이터분석팀 2026.08).',ch:4});
  const it=[['대문 열기','숫자 4개와\n추천 카드 읽기'],['카드 → 고객찾기','추천 카드에서\n고객찾기로 이동'],['맞춤대화 시작','"보장분석 해줘"\n→ 꼬리질문 2번'],['그룹으로 찾기','[사전동의 만료]에서\nD-n 짧은 1명 상담'],['리포트 보내기','요약 리포트를\n내 카톡으로 받기']];
  const gap=0.2, cw=(W-2*M-gap*4)/5;
  it.forEach((c,i)=>{ const x=M+i*(cw+gap), y=2.25, h=3.2, on=i===0; R(s,{x,y,w:cw,h,fill:on?C.blue:C.white,line:on?null:C.g200,radius:0.16,shadow:!on});
    T(s,`DAY ${i+1}`,{x:x+0.3,y:y+0.28,w:cw-0.5,h:0.4,fontSize:14,bold:true,color:on?C.blue100:C.blue,valign:'middle'});
    T(s,c[0],{x:x+0.3,y:y+0.8,w:cw-0.45,h:0.9,fontSize:21,bold:true,color:on?'FFFFFF':C.navy,valign:'top',lineSpacingMultiple:1.15});
    T(s,c[1],{x:x+0.3,y:y+1.8,w:cw-0.45,h:1.2,fontSize:15,color:on?'FFFFFF':C.g600,valign:'top',lineSpacingMultiple:1.3}); });
  T(s,'※ 추천 카드는 2차 오픈부터. 그 전엔 고객찾기 "당월 영업 타겟" 그룹에서 골라요.',{x:M,y:5.55,w:W-2*M,h:0.32,fontSize:13,color:C.g600,valign:'middle'});
  bar(s,{y:6.02,h:0.8,label:'5일 뒤',text:'"대문에서 하루를 시작하는 사람"이 돼요.',size:21});
  foot(s,no); });

// 20 FAQ
S.push((pres,no)=>{ const s=head(pres,{kicker:'5 · 오늘부터',title:'가장 많이 물으실 세 가지',ch:4});
  const it=[['대문은 어디서 여나요?','10월부터 PC 영업포탈에서 MeAI로 들어오면 먼저 열려요.\n10/2부터 배너·CRM 리스트·떠 있는 버튼으로도.\n휴대폰 앱은 PC 오픈 뒤 순차 적용 예정.'],['추천 고객이 안 보여요','CRM 데이터 반입이 끝나는 2차 오픈부터 보여요.\n추천 결과는 매일 계산돼 다음 날 반영돼요.'],['동의 없는 고객은요?','[고객 동의]나 [사전조회동의 요청하기]로 알림톡을 보내요.\n동의하면 15분 안팎에 반영돼요.']];
  it.forEach((c,i)=>{ const y=1.85+i*1.62, h=1.45; R(s,{x:M,y,w:W-2*M,h,fill:C.white,line:C.g200,radius:0.16,shadow:true});
    T(s,'Q',{x:M+0.3,y,w:0.6,h,fontSize:30,bold:true,color:C.blue,valign:'middle'});
    T(s,c[0],{x:M+0.95,y,w:3.6,h,fontSize:22,bold:true,color:C.navy,valign:'middle'});
    T(s,c[1],{x:M+4.6,y,w:W-2*M-4.8,h,fontSize:16,color:C.g700,valign:'middle',lineSpacingMultiple:1.3}); });
  foot(s,no); });
// 21 클로징
S.push((pres,no)=>{ const s=pres.addSlide(); s.background={color:C.blue};
  T(s,'MeAI',{x:W-6.2,y:0.8,w:5.6,h:2.4,fontSize:120,bold:true,color:'FFFFFF',transparency:82,align:'right',valign:'top'});
  T(s,'오늘 만날 고객은,\n대문에 있어요',{x:M+0.2,y:1.55,w:9,h:2.4,fontSize:54,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.12});
  T(s,'찾는 일은 MeAI가, 만나는 일은 여러분이.',{x:M+0.2,y:4.15,w:9,h:0.6,fontSize:24,color:'FFFFFF',valign:'middle'});
  let cx=M+0.2; ['대문이 열리면, 매일 아침','문의 · 세일즈혁신TF'].forEach(t=>{ cx+=chipX(s,{x:cx,y:5.05,text:t,fill:'1B64DA',color:'FFFFFF',size:15,h:0.5})+0.2; });
  T(s,'본 자료의 전부·일부(수정 포함)의 외부 제공·배포·게시(온/오프라인)는 금지됩니다. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다. 화면 속 고객 이름·숫자는 예시 데이터입니다.',{x:M+0.2,y:6.1,w:W-2*M-0.4,h:0.55,fontSize:11.5,color:'FFFFFF',transparency:10,valign:'middle',lineSpacingMultiple:1.2});
  foot(s,no,true); });
// 22 큐시트(송출 제외)
S.push((pres,no)=>{ const s=head(pres,{kicker:'진행용 · 송출 제외',title:'30분 큐시트',sub:'대본 낭독 약 22분 + 시연·화면 전환·질문 약 8분. 대본 전문은 각 장의 발표자 노트에 있어요.'});
  let t=0; const rows=[['시간','장','화면','진행 메모']];
  SCRIPT.forEach((x,i)=>{ rows.push([`${mmss(t)}–${mmss(t+x.sec)}`,String(i+1),x.screen,x.cue]); t+=x.sec; });
  const colW=[1.45,0.5,2.7,W-2*M-4.65];
  const data=rows.map((r,ri)=>r.map(c=>({text:String(c),options:{fontFace:L.FONT,fontSize:9.5,bold:ri===0,color:ri===0?C.g700:C.navy,fill:{color:ri===0?C.g100:C.white},valign:'middle',margin:[1,5,1,5]}})));
  s.addTable(data,{x:M,y:2.15,w:W-2*M,colW,rowH:0.19,border:{type:'solid',color:C.g200,pt:0.5}});
  foot(s,no); });

// 빌드
if (S.length!==SCRIPT.length+1) { console.error('슬라이드 수와 대본 수가 맞지 않음', S.length, SCRIPT.length); process.exit(1); }
const pres=L.newPres(); pres.title='MeAI 대문 30분 방송'; 
let t=0; const notes=[];
S.forEach((fn,i)=>{ const s0=pres._slides ? pres._slides.length : 0; fn(pres,i+1); const s=pres._slides[pres._slides.length-1];
  let n;
  if (i<SCRIPT.length){ const x=SCRIPT[i]; n=`[${mmss(t)}–${mmss(t+x.sec)} · ${x.sec}초] ${x.screen}\n진행: ${x.cue}\n\n${x.text}`; t+=x.sec; }
  else n='진행용 큐시트 · 방송 송출 제외';
  s.addNotes(n); notes.push(n); });
const out=process.argv[2]||'bcast.pptx';
fs.writeFileSync(out.replace(/\.pptx$/,'_notes.json'), JSON.stringify(notes,null,1));
pres.writeFile({fileName:out}).then(()=>{ console.log('written',out,S.length,'slides · total',mmss(t)); if(L.MISSING.length) console.log('MISSING',L.MISSING); else console.log('no missing images'); });
