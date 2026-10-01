// 방송판 새 장: 동의가 없어도, 첫 연락 준비는 MeAI가 (소유자 교안 v2 의 12장 '동의 상태' 뒤에 끼움)
// node s_consent.js out.pptx <쪽번호>   (NODE_PATH 에 pptxgenjs 가 있어야 함)
const path=require('path');
const H_=require(path.join(__dirname,'..','head.js'));
const { L, C, W, M, T, R, head, foot, bar, badge, chipX } = H_;
const CAP=process.env.CAPTURES||path.join(__dirname,'..','..','captures');
const out=process.argv[2]||'s_consent.pptx', no=Number(process.argv[3]||13);
const pres=L.newPres(); pres.title='MeAI 홈 영업가족 방송';
const s=head(pres,{kicker:'2 · 고르기',title:'동의가 없어도, 첫 연락 준비는 MeAI가',sub:'사전조회동의 필요 고객엔 일반대화 최적화 프롬프트가 자동 세팅',ch:1});
// ── 왼쪽: 김민수(동의 필요) 고객찾기 오른쪽 칸
const top=2.2;
const g=L.img(s,path.join(CAP,'find010','32_right_panel_kimminsu.png'),{x:M,y:top,w:3.45,h:3.45,align:'left',valign:'top',radius:20});
const k=g.scale, P=(px,py,n,color)=>badge(s,g.x+px*k-0.21,g.y+py*k-0.21,n,{d:0.42,size:15,color});
s.addShape('roundRect',{x:g.x+24*k,y:g.y+176*k,w:782*k,h:241*k,fill:{type:'none'},line:{color:C.blue,width:2},rectRadius:0.06});
P(770,186,1); P(806,372,2); P(24,634,3,C.red);
T(s,'김민수 고객(사전조회동의 필요) · 고객찾기 오른쪽 · 이름은 예시',{x:g.x,y:g.y+g.h+0.06,w:g.w+0.4,h:0.26,fontSize:11,color:C.g500,valign:'middle'});
// ── 오른쪽 위: 자동으로 들어가는 조건
const rx=M+3.45+0.5, rw=W-M-rx;
R(s,{x:rx,y:top,w:rw,h:2.02,fill:C.white,line:C.g200,radius:0.16,shadow:true});
badge(s,rx+0.24,top+0.2,1,{d:0.36,size:13});
T(s,'MeAI가 자동으로 넣는 조건',{x:rx+0.72,y:top+0.2,w:4,h:0.36,fontSize:16,bold:true,color:C.navy,valign:'middle'});
const tags=[['#암진단비 부족','고객 그룹 = 연락할 이유'],['#50대','나이대'],['#보유','보유 · 가망 · 이관']];
let tx=rx+0.3; const ty=top+0.74;
tags.forEach(([t,d])=>{ const w=chipX(s,{x:tx,y:ty,text:t,fill:C.blue50,color:C.blue700,size:13.5,h:0.42}), lw=L.textW(d,11.5)+0.1; T(s,d,{x:tx,y:ty+0.47,w:Math.max(w,lw),h:0.26,fontSize:11.5,color:C.g600,valign:'middle'}); tx+=Math.max(w,lw)+0.18; });
T(s,'→',{x:tx-0.02,y:ty,w:0.3,h:0.42,fontSize:16,bold:true,color:C.g500,align:'center',valign:'middle'});
R(s,{x:tx+0.32,y:ty-0.04,w:rx+rw-0.25-(tx+0.32),h:0.78,fill:C.g50,line:null,radius:0.12});
T(s,'안내 문자 문안 3~4줄\n부담스럽지 않은 톤',{x:tx+0.45,y:ty-0.04,w:rx+rw-0.4-(tx+0.45),h:0.78,fontSize:13,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.1});
badge(s,rx+0.24,top+1.5,2,{d:0.36,size:13});
s.addText([{text:'(고객 성명·연락처는 넣지 말 것)',options:{bold:true,color:C.red,fontSize:13,fontFace:L.FONT}},{text:'  이름 대신 조건으로 · 동의 전에도 일반대화로',options:{color:C.g700,fontSize:12.5,fontFace:L.FONT}}],{x:rx+0.72,y:top+1.47,w:rw-0.9,h:0.42,isTextBox:true,margin:0,valign:'middle'});
// ── 오른쪽 아래: 네 칸 흐름
const fy=top+2.2, fh=1.5, steps=[['파란 질문 누르기','고객찾기 오른쪽\n[일반대화] 추천 질문'],['입력창에 채워짐','일반대화 화면이 열림\n전송(↑)만 누르기'],['안내 문자 초안','숫자·내용 확인 뒤\n내 말투로 다듬어 연락'],['동의 요청','[사전조회동의 요청하기]\n동의되면 맞춤대화']];
const gap=0.14, sw=(rw-gap*3)/4;
steps.forEach(([t,d],i)=>{ const x=rx+i*(sw+gap), last=i===3;
  R(s,{x,y:fy,w:sw,h:fh,fill:last?C.red50:C.blue50,line:null,radius:0.14});
  T(s,'STEP '+(i+1),{x:x+0.2,y:fy+0.16,w:sw-0.3,h:0.24,fontSize:11,bold:true,color:last?C.red:C.blue,valign:'middle'});
  T(s,t,{x:x+0.2,y:fy+0.42,w:sw-0.3,h:0.36,fontSize:14.5,bold:true,color:C.navy,valign:'middle'});
  T(s,d,{x:x+0.2,y:fy+0.82,w:sw-0.3,h:0.56,fontSize:11.5,color:C.g700,valign:'top',lineSpacingMultiple:1.1});
  if(!last) T(s,'›',{x:x+sw-0.02,y:fy+fh/2-0.2,w:gap+0.04,h:0.4,fontSize:16,bold:true,color:C.g400,align:'center',valign:'middle'}); });
badge(s,rx+rw-0.3,fy-0.12,3,{d:0.36,size:13,color:C.red});
bar(s,{y:6.1,h:0.68,label:'기억할 것',text:'동의 전엔 일반대화로 다가가고, 동의 후엔 맞춤대화로 깊게',size:18});
foot(s,no);
s.addNotes('NOTES_PLACEHOLDER');
pres.writeFile({fileName:out}).then(()=>console.log('written',out));
