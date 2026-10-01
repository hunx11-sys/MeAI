// MeAI 홈 공지사항용 사용 안내 PPT (5장). 가이드북 v4 의 디자인 부품(build/lib.js)과 캡처(captures/)를 그대로 씀.
// node notice.js out.pptx      (NODE_PATH 에 pptxgenjs 가 있어야 함)
const path = require('path');
const L = require(path.join(__dirname,'..','build','lib.js'));
const { C, W, H, M } = L;
const F = path.join(__dirname,'..','captures');
const HERO = n => path.join(F,'hero',n+'.png');
L.setFooterText('MeAI 홈 사용 안내 · 세일즈혁신TF');
const pres = L.newPres(); pres.title = 'MeAI 홈 사용 안내';
const NO = 5;
// 1 표지
L.cover(pres,{ title:'MeAI 홈\n사용 안내', sub:'찾는 영업에서\n찾아가는 영업으로', line3:'나만의 영업비서, “MeAI 홈” OPEN\n영업가족 편', meta:['세일즈혁신TF'], file:HERO('gb5_gate_full_m'), pageNo:1 });
// 2 들어가는 길
{ const s = L.base(pres,{ kicker:'1 · 들어가기', title:'영업포탈에서 MeAI로 들어오면 MeAI 홈이 가장 먼저 열림', sub:'새로 생긴 문 ③④⑤는 권한과 상관없이 누구나 사용 가능', pageNo:2 });
  L.img(s,HERO('bc2_portal_masked'),{x:M,y:1.95,w:7.9,h:4.85,valign:'top',align:'left'});
  const x = 8.85, w = W-M-x;
  L.numList(s,{ x, y:2.0, w, gap:0.12, titleSize:14.5, descSize:12, items:[
    {n:3,title:'중앙 롤링배너',desc:'[MeAI 홈 바로가기]'},
    {n:4,title:'CRM 리스트',desc:'고객 목록의 [MeAI 일반대화] [MeAI 맞춤대화]\n생일·상령일 목록에서 바로 시작'},
    {n:5,title:'떠 있는 MeAI 버튼',desc:'목록 위 둥근 버튼'}]});
  L.note(s,{ x, y:5.2, w, h:1.4, label:'함께 알아 두기', text:'①②⑥은 기존 메뉴(사용권한 필요). 휴대폰은 앱 홈 → 보장분석 → MeAI 순서. 어느 화면에서든 왼쪽 위 [MeAI 홈]을 누르면 처음으로.', tone:'blue', size:11.5 });
}
// 3 네 걸음
{ const s = L.base(pres,{ kicker:'2 · 쓰는 법', title:'찾기 · 고르기 · 묻기 · 연락하기', sub:'매일 아침 MeAI 홈에서 시작', pageNo:3 });
  L.img(s,HERO('bc3_home_cards'),{x:M,y:1.9,w:W-2*M,h:1.5,valign:'top',align:'center'});
  const steps = [['1','찾기','오늘의 추천 고객','이름 아래 굵은 한 문장이\n연락할 이유'],['2','고르기','[MeAI 고객찾기에서 열기]','상황을 보고\n연락할 고객 선택'],['3','묻기','추천 질문 누르기','질문이 채워진 채로 열려\n전송만 누르면 됨'],['4','연락하기','카드 문장 + 요약 리포트','카드 문장을 내 말로 풀어\n첫 말로 연락']];
  const gap = 0.22, cw = (W-2*M-gap*3)/4, y = 3.7, ch = 2.2;
  steps.forEach(([n,t,sub,d],i)=>{ const x = M+i*(cw+gap);
    L.R(s,{x,y,w:cw,h:ch,fill:C.white,line:C.g200,radius:0.16,shadow:true});
    L.badge(s,{x:x+0.25,y:y+0.25,n,d:0.42,color:C.blue});
    L.T(s,t,{x:x+0.8,y:y+0.22,w:cw-1,h:0.48,fontSize:20,bold:true,color:C.navy,valign:'middle'});
    L.T(s,sub,{x:x+0.25,y:y+0.9,w:cw-0.4,h:0.4,fontSize:12.5,bold:true,color:C.blue,valign:'middle'});
    L.T(s,d,{x:x+0.25,y:y+1.35,w:cw-0.4,h:0.7,fontSize:12,color:C.g700,valign:'top',lineSpacingMultiple:1.2}); });
  L.note(s,{ x:M, y:6.1, w:W-2*M, h:0.52, label:'기억할 것', text:'카드 문장은 고객에게 첫 말, 추천 질문은 MeAI에게 첫 질문', tone:'blue', size:13 });
}
// 4 알아 둘 것
{ const s = L.base(pres,{ kicker:'3 · 알아 둘 것', title:'추천 고객과 사전조회 동의', sub:'맞춤대화는 보장 내역을 읽기 때문에 동의가 먼저', pageNo:4 });
  const cw = (W-2*M-0.3)/2, y = 1.95;
  L.R(s,{x:M,y,w:cw,h:4.6,fill:C.white,line:C.g200,radius:0.18,shadow:true});
  L.T(s,'오늘의 추천 고객',{x:M+0.35,y:y+0.28,w:cw-0.7,h:0.4,fontSize:18,bold:true,color:C.blue});
  [['9명','3명 × 3세트, 화살표로 넘김'],['이유 한 문장','왜 지금 이 고객인지 카드에 표시'],['매일 밤 계산','다음 날 MeAI 홈에 반영'],['직접 골라도 됨','추천은 지시가 아니라 이유가 있는 고객']].forEach(([a,b],i)=>{ const yy = y+0.95+i*0.9;
    L.T(s,a,{x:M+0.35,y:yy,w:cw-0.7,h:0.4,fontSize:17,bold:true,color:C.navy,valign:'middle'});
    L.T(s,b,{x:M+0.35,y:yy+0.4,w:cw-0.7,h:0.34,fontSize:12.5,color:C.g600,valign:'middle'}); });
  const x2 = M+cw+0.3;
  L.R(s,{x:x2,y,w:cw,h:4.6,fill:C.white,line:C.g200,radius:0.18,shadow:true});
  L.T(s,'사전조회 동의',{x:x2+0.35,y:y+0.28,w:cw-0.7,h:0.4,fontSize:18,bold:true,color:C.blue});
  [[C.blue,'사전조회동의 D-n','바로 [이 고객으로 맞춤대화 시작]'],[C.red,'사전조회동의 필요','[사전조회동의 요청하기] → 알림톡 → 15분 안팎 반영']].forEach(([col,a,b],i)=>{ const yy = y+0.95+i*1.05;
    L.chip(s,{x:x2+0.35,y:yy,text:a,fill:col===C.blue?C.blue50:C.red50,color:col,size:12.5,h:0.38});
    L.T(s,b,{x:x2+0.35,y:yy+0.45,w:cw-0.7,h:0.4,fontSize:12.5,color:C.g700,valign:'middle'}); });
  L.R(s,{x:x2+0.35,y:y+3.2,w:cw-0.7,h:1.0,fill:C.g50,line:null,radius:0.12});
  L.T(s,'맞춤대화 가능  동의일부터 90일\nMeAI 홈 노출  동의일로부터 3년 이내',{x:x2+0.55,y:y+3.2,w:cw-1.1,h:1.0,fontSize:13,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.35});
}
// 5 지킬 것 · 문의
{ const s = L.base(pres,{ kicker:'4 · 꼭 지켜 주세요', title:'MeAI를 쓸 때 지킬 것 네 가지', sub:'자세한 사용법은 MeAI 활용 가이드북(영업가족 편)을 참고', pageNo:5 });
  const rules = [['개인정보 넣지 않기','이름·연락처·주소·주민번호는 질문에도 메모에도 넣지 않음'],['답변은 검증 후 사용','숫자·약관 근거를 직접 확인한 뒤 사용'],['동의 없으면 보지 않기','동의가 없거나 철회된 고객은 우회하지 않고 동의부터'],['자료 외부 반출 금지','MeAI 답변·화면 캡처·가이드북은 외부에 제공·배포·게시 금지']];
  const gap = 0.22, cw = (W-2*M-gap)/2, ch = 1.55;
  rules.forEach(([a,b],i)=>{ const x = M+(i%2)*(cw+gap), y = 1.95+Math.floor(i/2)*(ch+gap);
    L.R(s,{x,y,w:cw,h:ch,fill:C.white,line:C.g200,radius:0.16,shadow:true});
    L.badge(s,{x:x+0.3,y:y+0.3,n:i+1,d:0.44,color:C.red});
    L.T(s,a,{x:x+0.95,y:y+0.25,w:cw-1.2,h:0.5,fontSize:18,bold:true,color:C.navy,valign:'middle'});
    L.T(s,b,{x:x+0.95,y:y+0.8,w:cw-1.2,h:0.55,fontSize:12.5,color:C.g700,valign:'top',lineSpacingMultiple:1.2}); });
  L.R(s,{x:M,y:5.5,w:W-2*M,h:1.0,fill:C.navy,line:null,radius:0.16});
  L.T(s,'문의  세일즈혁신TF',{x:M+0.4,y:5.5,w:W-2*M-0.8,h:1.0,fontSize:20,bold:true,color:'FFFFFF',valign:'middle'});
  L.T(s,'화면 속 고객 이름·숫자는 모두 예시',{x:M+0.4,y:5.5,w:W-2*M-0.8,h:1.0,fontSize:12,color:'FFFFFF',align:'right',valign:'middle',transparency:20});
}
pres.writeFile({fileName:process.argv[2]||'notice.pptx'}).then(()=>{ console.log('written', process.argv[2]||'notice.pptx'); if (L.MISSING.length) console.log('MISSING', L.MISSING); });
