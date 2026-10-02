// 방송판 새 장: 감이 아니라 데이터로 고른 고객 (소유자 교안 8장 뒤에 끼움)
// node s_data.js out.pptx <쪽번호>   (NODE_PATH 에 pptxgenjs 가 있어야 함)
const path=require('path');
const H_=require(path.join(__dirname,'..','head.js'));
const { L, C, W, M, T, R, head, foot, bar, chipX } = H_;
const out=process.argv[2]||'s_data.pptx', no=Number(process.argv[3]||9);
const pres=L.newPres(); pres.title='MeAI 홈 영업가족 방송';
const s=head(pres,{kicker:'1 · 찾기',title:'감이 아니라 데이터로 고른 고객',sub:'오늘의 추천 고객은 데이터 기반 AI 추천 · 고객찾기 목록은 타겟 가능성 높은 순이 기본',ch:0});
const dot=(x,y,col,d=0.11)=>s.addShape('ellipse',{x,y,w:d,h:d,fill:{color:col},line:{color:col,width:0}});
// ── 왼쪽: 오늘의 추천 고객, 감 vs 데이터
const top=2.2;
T(s,'오늘의 추천 고객',{x:M,y:top,w:3,h:0.34,fontSize:14,bold:true,color:C.blue,valign:'middle'});
const cy=top+0.46, ch=2.92;
// 감으로 고를 때
const ax=M, aw=2.72;
R(s,{x:ax,y:cy,w:aw,h:ch,fill:C.g50,line:C.g200,radius:0.16});
T(s,'감으로 고를 때',{x:ax+0.26,y:cy+0.2,w:aw-0.4,h:0.4,fontSize:16.5,bold:true,color:C.g700,valign:'middle'});
['생각나는 고객부터','최근 연락한 고객부터','긴 목록을 넘겨 가며'].forEach((t,i)=>{ const y=cy+0.78+i*0.42; dot(ax+0.3,y+0.12,C.g400); T(s,t,{x:ax+0.52,y,w:aw-0.65,h:0.34,fontSize:14,color:C.g600,valign:'middle'}); });
R(s,{x:ax+0.2,y:cy+ch-0.84,w:aw-0.4,h:0.64,fill:C.white,line:C.g200,radius:0.12});
T(s,'누구 · 왜 · 언제를\n매번 혼자 판단',{x:ax+0.2,y:cy+ch-0.84,w:aw-0.4,h:0.64,fontSize:13,bold:true,color:C.g700,align:'center',valign:'middle',lineSpacingMultiple:1.05});
// 화살표
const bx=ax+aw+0.5, bw=M+6.55-bx;
s.addShape('ellipse',{x:ax+aw+0.04,y:cy+ch/2-0.21,w:0.42,h:0.42,fill:{color:C.blue},line:{color:'FFFFFF',width:1.5}});
T(s,'→',{x:ax+aw+0.04,y:cy+ch/2-0.21,w:0.42,h:0.42,fontSize:16,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
// 데이터 기반 AI 추천
R(s,{x:bx,y:cy,w:bw,h:ch,fill:C.blue50,line:C.blue100,radius:0.16});
T(s,'데이터 기반 AI 추천',{x:bx+0.26,y:cy+0.2,w:bw-0.4,h:0.4,fontSize:16.5,bold:true,color:C.blue700,valign:'middle'});
['계약·동의·상령일·생일·CRM','매일 밤 계산 · 다음 날 반영','연락할 이유를 한 문장으로'].forEach((t,i)=>{ const y=cy+0.78+i*0.42; dot(bx+0.3,y+0.12,C.blue); T(s,t,{x:bx+0.52,y,w:bw-0.65,h:0.34,fontSize:14,bold:i===0,color:C.navy,valign:'middle'}); });
R(s,{x:bx+0.2,y:cy+ch-0.84,w:bw-0.4,h:0.64,fill:C.blue,line:null,radius:0.12});
T(s,'전반적으로 타겟률이 더 높음',{x:bx+0.2,y:cy+ch-0.84,w:bw-0.4,h:0.64,fontSize:16,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
// ── 오른쪽: 고객찾기 목록 기본 순서(도식)
const px=M+6.55+0.4, pw=W-M-px, py=top, ph=cy+ch-top;
R(s,{x:px,y:py,w:pw,h:ph,fill:C.white,line:C.g200,radius:0.16,shadow:true});
T(s,'MeAI 고객찾기 목록',{x:px+0.28,y:py+0.2,w:2.3,h:0.32,fontSize:14,bold:true,color:C.blue,valign:'middle'});
chipX(s,{x:px+0.28+L.textW('MeAI 고객찾기 목록',14)+0.12,y:py+0.2,text:'기본 설정',fill:C.blue50,color:C.blue700,size:11.5,h:0.32});
T(s,'보유 고객 중 타겟 가능성 높은 순',{x:px+0.28,y:py+0.58,w:pw-0.5,h:0.46,fontSize:19,bold:true,color:C.navy,valign:'middle'});
const rx=px+0.28, rw=pw-0.56, barX=rx+1.42, barMax=1.65;
T(s,'고객',{x:rx+0.48,y:py+1.06,w:1,h:0.24,fontSize:11,color:C.g500,valign:'middle'});
T(s,'타겟 가능성',{x:barX,y:py+1.06,w:1.5,h:0.24,fontSize:11,color:C.g500,valign:'middle'});
const ord=['1B64DA','3182F6','5E9BF3','8FB8F5'], frac=[1,0.8,0.6,0.4];
ord.forEach((col,i)=>{ const y=py+1.34+i*0.42, h=0.34;
  R(s,{x:rx,y,w:rw,h,fill:i===0?C.blue50:C.g50,line:null,radius:0.08});
  s.addShape('ellipse',{x:rx+0.08,y:y+0.03,w:0.28,h:0.28,fill:{color:col},line:{color:col,width:0}});
  T(s,String(i+1),{x:rx+0.08,y:y+0.03,w:0.28,h:0.28,fontSize:11,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
  R(s,{x:rx+0.5,y:y+0.12,w:0.5-i*0.03,h:0.12,fill:C.g300,line:null,radius:0.06});
  R(s,{x:rx+0.5+0.56-i*0.03,y:y+0.12,w:0.22,h:0.12,fill:C.g200,line:null,radius:0.06});
  R(s,{x:barX,y:y+0.1,w:barMax*frac[i],h:0.16,fill:col,line:null,radius:0.08});
  if(i===0) T(s,'여기부터 연락',{x:barX+barMax+0.08,y,w:rx+rw-(barX+barMax+0.08)-0.08,h,fontSize:11.5,bold:true,color:C.blue700,align:'right',valign:'middle'});
});
T(s,'※ 순서를 보여 주는 도식 · 실제 화면 모양과 다름',{x:rx,y:py+2.98,w:rw,h:0.26,fontSize:11,color:C.g500,valign:'middle'});
bar(s,{y:6.05,h:0.72,label:'기억할 것',text:'추천 카드부터, 고객찾기 목록은 위에서부터 연락',size:18});
foot(s,no);
s.addNotes('NOTES_PLACEHOLDER');
pres.writeFile({fileName:out}).then(()=>console.log('written',out));
