module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  S.push({ part:'02', fn:(pres,no)=> L.divider(pres,{num:'02',title:'MeAI 홈\n하루가 시작되는 곳',sub:'오늘 연락할 내 고객과 첫 마디가 미리 준비된 곳 · 누르기만 하면 시작',learn:['영업포탈에서 MeAI 홈으로 가는 진입로 6곳','MeAI 홈 다섯 구역 · 스위치와 버튼','숫자 4개와 추천 카드 읽는 법','태그 · 동의 · 유형 범례'],pageNo:no}) });
  // 2-0a 영업포탈 진입점 6군데 (10/2)
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 영업포탈에서 들어가기',title:'영업포탈에서 MeAI 홈으로 가는 진입로',sub:'중앙 배너와 CRM 통해 들어가는 MeAI는 누구나 사용 가능 · 10월 2일부터 새 문 ③④⑤',pageNo:no,tag:{text:'10/2 반영',fill:C.blue50,color:C.blue}});
    L.img(s,HERO('bc2_portal_masked'),{x:M,y:1.85,w:8.3,h:5.1,valign:'top',align:'left'});
    L.numList(s,{x:9.15,y:1.85,w:3.58,gap:0.06,titleSize:13.5,descSize:11.5,items:[
      {n:1,title:'왼쪽 위 [MeAI 홈]',desc:'기존 · 사용권한이 있어야 사용 가능'},
      {n:2,title:'왼쪽 위 [보장분석]',desc:'기존 · 사용권한이 있어야 사용 가능'},
      {n:3,title:'중앙 롤링배너',desc:'신설 · [MeAI 홈 바로가기]'},
      {n:4,title:'CRM 리스트',desc:'신설 · [MeAI 일반대화] [MeAI 맞춤대화]'},
      {n:5,title:'떠 있는 MeAI 버튼',desc:'신설 · 목록 위 둥근 버튼'},
      {n:6,title:'오른쪽 [MeAI 홈]',desc:'기존 · 사용권한이 있어야 사용 가능'}]});
    L.note(s,{x:9.15,y:5.85,w:3.58,h:0.52,label:'신설 ③④⑤',text:'권한과 상관없이 누구나 사용 가능',tone:'blue',size:11});
  }});
  // 2-0b 새 문 3개 확대
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 새로 생긴 문 3개',title:'새로 생긴 문 ③④⑤ 한눈에 보기',sub:'고객 목록에서 바로 대화를 시작하는 ④가 핵심',pageNo:no,tag:{text:'10/2 반영',fill:C.blue50,color:C.blue}});
    L.label(s,{x:M,y:1.85,w:4.6,text:'③ 롤링배너 → [MeAI 홈 바로가기]',color:C.blue,size:11.5});
    L.img(s,HERO('portal_entry_banner'),{x:M,y:2.2,w:4.6,h:1.3,valign:'top',align:'left'});
    L.img(s,HERO('fix_banner_left_z'),{x:M,y:3.68,w:4.6,h:3.22,valign:'top',align:'left'});
    L.label(s,{x:5.5,y:1.85,w:7.23,text:'④ CRM 리스트 [MeAI 일반대화] [MeAI 맞춤대화] · ⑤ 떠 있는 MeAI 버튼',color:C.red,size:11.5});
    L.img(s,HERO('portal_entry_crm'),{x:5.5,y:2.2,w:7.23,h:3.5,valign:'top',align:'left'});
    L.note(s,{x:5.5,y:5.85,w:7.23,h:1.05,label:'④가 핵심인 이유',text:'내 고객 생일·상령일 목록에서 바로 [MeAI 맞춤대화]를 눌러서 시작.\n그 고객 대화가 한 번에 열림.',tone:'dark',size:12.5});
  }});
  // 2-1 전체 화면
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · MeAI 홈 화면 구성',title:'MeAI 홈 한 화면에 담길 오늘 연락할 고객',pageNo:no});
    const g = L.img(s,HERO('gb5_gate_full_m'),{x:M,y:1.5,w:7.4,h:5.4,valign:'top',align:'left'});
    const clip={x:0,y:0};
    L.pin(s,g,60,110,1,{clip}); L.pin(s,g,720,166,2,{clip}); L.pin(s,g,60,442,3,{clip}); L.pin(s,g,720,603,4,{clip}); L.pin(s,g,60,1172,5,{clip}); L.pin(s,g,1338,42,6,{clip});
    L.numList(s,{x:7.1,y:1.5,w:5.63,gap:0.16,titleSize:14,descSize:12,items:[
      {n:1,title:'인사 + 최근 업데이트',desc:'"OO님 안녕하세요" · 오른쪽 \'최근 업데이트\' = 데이터 기준 시각'},
      {n:2,title:'대화 카드 두 장',desc:'일반대화는 바로 질문 창, 맞춤대화는 고객 검색 팝업이 먼저 뜸.'},
      {n:3,title:'내 고객 숫자 4개',desc:'전체 · 맞춤대화 가능 · 동의 필요 · 상품제안 가능'},
      {n:4,title:'오늘의 추천 고객',desc:'연락할 이유가 붙은 카드 3장 × 세트 3개. 화살표로 넘김.'},
      {n:5,title:'범례',desc:'태그 색 · 동의 상태 · 고객 유형의 뜻.'},
      {n:6,title:'오른쪽 위 스위치·버튼',desc:'[글씨 확대] ON/OFF · [고객 동의] · [게시판]'},
    ]});
    L.note(s,{x:7.1,y:6.3,w:5.63,h:0.6,label:'',text:'데이터와 추천 결과는 매일 새로 계산해 다음 날 반영.',tone:'grey',size:11.5});
    L.caption(s,{x:W-M-6.2,y:1.12,w:6.2,text:'※ 이름과 숫자는 예시 · 정재민 카드 문구와 업데이트 시각은 가림',align:'right',size:10});
  }});
  // 2-1b NEW 글씨 확대 스위치 (새 목업 v2)
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · NEW 글씨 확대',title:'글씨가 작으면, 오른쪽 위 스위치 하나로',sub:'MeAI 홈·고객찾기·게시판 오른쪽 위 [글씨 확대]. 기본은 ON.',pageNo:no,tag:{text:'NEW',fill:C.blue50,color:C.blue}});
    L.label(s,{x:M,y:1.95,w:4.7,text:'ON · 기본 (글씨 한 단계 크게)',color:C.blue,size:12});
    L.img(s,HERO('v2_switch_on_z'),{x:M,y:2.3,w:4.7,h:0.7,valign:'top',align:'left'});
    L.label(s,{x:M,y:3.25,w:4.7,text:'OFF · 원래 크기',color:C.g700,size:12});
    L.img(s,HERO('v2_switch_off_z'),{x:M,y:3.6,w:4.7,h:0.7,valign:'top',align:'left'});
    L.note(s,{x:M,y:4.6,w:4.7,h:1.25,label:'한 번만 바꾸면 끝',text:'세 화면이 같이 바뀜.\n이 PC에서는 다음에도 그대로 유지.',tone:'blue',size:12});
    L.note(s,{x:M,y:6.0,w:4.7,h:0.85,label:'OFF는 언제?',text:'한 화면에 더 많이 보고 싶을 때.',tone:'grey',size:11.5});
    L.label(s,{x:5.75,y:1.95,w:3.35,text:'ON',color:C.blue,size:12});
    L.img(s,HERO('gb5_font_on_card'),{x:5.75,y:2.3,w:3.35,h:4.55,valign:'top',align:'left'});
    L.label(s,{x:9.35,y:1.95,w:3.35,text:'OFF',color:C.g700,size:12});
    L.img(s,HERO('gb5_font_off_card'),{x:9.35,y:2.3,w:3.35,h:4.55,valign:'top',align:'left'});
    L.caption(s,{x:5.75,y:6.55,w:6.95,text:'※ 이름과 숫자는 예시',align:'left',size:10});
  }});
  // 2-2 대화 카드
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 대화 카드',title:'어떤 대화를 시작할지 먼저 고르기',sub:'MeAI 홈에서 카드 하나만 누르면, 나머지는 MeAI가 준비',pageNo:no});
    const g = L.img(s,HERO('gate_cards'),{x:M,y:1.85,w:W-2*M,h:1.75,valign:'top'});
    L.card(s,{x:M,y:3.85,w:5.95,h:1.7,kicker:'일반대화 · 왼쪽 카드',title:'고객을 정하지 않은 질문',desc:'누르면 바로 질문 창이 열림.\n상품·특약, 화법, 약관, 자사·타사 보장 비교까지.',titleSize:18,descSize:13.5});
    L.card(s,{x:M+6.2,y:3.85,w:5.93,h:1.7,kicker:'맞춤대화 · 오른쪽(검은) 카드',title:'고객 한 명의 보장을 함께 보기',desc:'누르면 고객 검색 팝업이 뜸.\n이름을 고르면 그 고객 대화가 열림. (PART 3)',titleSize:18,descSize:13.5,accent:C.red});
    L.note(s,{x:M,y:5.8,w:W-2*M,h:0.75,label:'TIP',text:'처음엔 일반대화로 감을 익히고, 내 고객을 만나기 전엔 꼭 맞춤대화.',tone:'grey',size:12.5});
  }});
  // 2-3 숫자 4개
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 내 고객 찾기',title:'매일 아침, 숫자 4개만 훑어보기',sub:'이 숫자가 오늘 할 일의 크기',pageNo:no});
    L.img(s,HERO('gate_stats'),{x:M,y:1.85,w:W-2*M,h:2.1,valign:'top'});
    const cards=[['342명','내 전체 고객','보유·가망·이관을 모두 더한 수.',C.navy],['137명','맞춤대화 가능','사전조회 동의일부터\n90일이 지나지 않은 고객.\n지금 바로 시작.',C.blue],['186명','사전조회 동의 필요','동의가 없거나 만료된 고객.\n동의 알림톡부터 보낼 고객.',C.red],['84명','상품제안 가능','상품 소개에 동의한 고객.\n"AI 추천 고객" 리본.',C.green]];
    cards.forEach((c,i)=>{ const x=M+i*3.08, y=4.2, w=2.9, h=2.1; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,c[0],{x:x+0.25,y:y+0.2,w:w-0.5,h:0.55,fontSize:26,bold:true,color:c[3],valign:'middle'}); L.T(s,c[1],{x:x+0.25,y:y+0.8,w:w-0.5,h:0.32,fontSize:13.5,bold:true,color:C.navy}); L.T(s,c[2],{x:x+0.25,y:y+1.18,w:w-0.5,h:0.85,fontSize:12,color:C.g600,lineSpacingMultiple:1.3}); });
    L.caption(s,{x:M,y:6.45,w:6,text:'※ 숫자는 예시',align:'left',size:10});
    L.caption(s,{x:W-M-6,y:6.45,w:6,text:'[MeAI 고객찾기 →] 누른 뒤 화면은 PART 4',align:'right',size:10});
  }});
  // 2-4 오늘의 추천 고객 hero
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 오늘의 추천 고객',title:'MeAI가 먼저 고른 오늘 연락할 고객',sub:'카드 3장 × 세트 3개 · 화살표로 다음 세트',pageNo:no});
    const g = L.img(s,HERO('gb5_gate_reco3_m'),{x:M,y:1.85,w:W-2*M,h:4.3,valign:'top'});
    const clip={x:150,y:580};
    L.pin(s,g,330,603,1,{clip}); L.pin(s,g,410,672,2,{clip}); L.pin(s,g,161,735,3,{clip}); L.pin(s,g,340,890,4,{clip}); L.pin(s,g,705,925,5,{clip}); L.pin(s,g,372,992,6,{clip}); L.pin(s,g,866,629,7,{clip}); L.pin(s,g,776,1056,8,{clip});
    L.pinStrip(s,{x:M,y:6.3,w:W-2*M,cols:4,rowH:0.31,size:10.5,items:[{n:1,text:'오늘의 추천 고객 구역'},{n:2,text:'이름 · 나이 · 유형 · 담당'},{n:3,text:'연락할 이유 + 근거'},{n:4,text:'태그'},{n:5,text:'사전조회동의 D-n / 필요'},{n:6,text:'[MeAI 고객찾기에서 열기]'},{n:7,text:'AI 추천 고객 리본'},{n:8,text:'세트 위치'}]});
    L.caption(s,{x:W-M-6,y:1.37,w:6,text:'※ 이름과 숫자는 예시 · 일부 카드 문구는 가림',align:'right',size:10});
  }});
  // 2-5 카드 읽는 법
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 추천 카드 읽는 법',title:'카드 한 문장이 고객에게 건네는 명분',sub:'누구 · 왜 · 언제 · 다음이 카드 한 장에. 이유 문장을 내 말로 풀면 곧 첫 말.',pageNo:no});
    const g = L.img(s,HERO('gb5_card_kim_z'),{x:M,y:1.85,w:5.2,h:5.05,valign:'top',align:'left'});
    const clip={x:150,y:624.05}, o={clip,dsf:3};
    L.pin(s,g,163,672,1,o); L.pin(s,g,424,663,2,o); L.pin(s,g,163,718,3,o); L.pin(s,g,163,800,4,o); L.pin(s,g,163,891,5,o); L.pin(s,g,163,926,6,o); L.pin(s,g,163,992,7,o);
    L.numList(s,{x:6.05,y:1.85,w:6.68,gap:0.06,titleSize:14,descSize:12,items:[
      {n:1,title:'이름 · 나이 · 유형 · 담당',desc:'유형은 보유·가망·이관 중 하나. 긴 이름은 줄여서 표시.'},
      {n:2,title:'AI 추천 고객 리본',desc:'상품 소개에 동의한 고객. 상품 제안까지 가능.'},
      {n:3,title:'연락할 이유',desc:'이름 아래 굵은 한 문장. "상령일이 2주 남았고 암진단비가 1천만원뿐입니다."'},
      {n:4,title:'근거 설명',desc:'왜 지금 좋은 기회인지. 여기서 상담 방향이 정해짐.'},
      {n:5,title:'태그',desc:'#이벤트 임박(파랑) #보장 공백(빨강) #당월 타겟(보라)'},
      {n:6,title:'사전조회동의 필요 · D-n',desc:'\'필요\'면 알림톡으로 동의부터, D-n(남은 날)이 보이면 바로 시작.'},
      {n:7,title:'[MeAI 고객찾기에서 열기]',desc:'한 번 누르면 고객찾기의 이 고객 카드로 바로 이동.'},
    ]});
    L.caption(s,{x:6.05,y:6.62,w:6.68,text:'※ 이름과 숫자는 예시',align:'left',size:10});
  }});
  // 2-6a 세트 2·3 카드 6장
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 추천 세트 3개',title:'매일 새로 계산되는 카드 9장',pageNo:no});
    const cards=[['reco2_card1','세트 2'],['reco2_card2','세트 2'],['reco2_card3','세트 2'],['gb5_reco3_card1','세트 3'],['gb5_reco3_card2','세트 3'],['gb5_reco3_card3','세트 3']];
    const cw=2.3, ch=2.48, x0=1.95, pitch=cw+0.28;
    cards.forEach((c,i)=>{ const col=i%3,row=Math.floor(i/3); const x=x0+col*pitch, y=1.5+row*(ch+0.15); L.img(s,HERO(c[0]),{x,y,w:cw,h:ch,valign:'top',align:'left'}); });
    [['세트 2',1.5],['세트 3',1.5+ch+0.15]].forEach(r=>{ L.T(s,r[0],{x:M,y:r[1]+ch/2-0.25,w:1.2,h:0.5,fontSize:16,bold:true,color:C.navy,valign:'middle'}); });
    const px=9.7, pw=3.03, ph=2*ch+0.15;
    L.R(s,{x:px,y:1.5,w:pw,h:ph,fill:C.blue50,line:null,radius:0.14});
    L.T(s,'9장',{x:px+0.3,y:1.95,w:pw-0.6,h:0.85,fontSize:44,bold:true,color:C.blue,valign:'middle'});
    L.T(s,'카드 3장 × 세트 3개',{x:px+0.3,y:2.88,w:pw-0.6,h:0.35,fontSize:15,bold:true,color:C.navy});
    L.T(s,'화살표를 누를 때마다\n다음 세트 3장이 나옴.',{x:px+0.3,y:3.3,w:pw-0.6,h:0.75,fontSize:12.5,color:C.g700,lineSpacingMultiple:1.3});
    s.addShape('line',{x:px+0.3,y:4.4,w:pw-0.6,h:0,line:{color:C.blue100,width:1}});
    L.T(s,'다음 날 반영',{x:px+0.3,y:4.75,w:pw-0.6,h:0.35,fontSize:15,bold:true,color:C.navy});
    L.T(s,'고객 데이터와 추천 결과는\n다음 날 MeAI 홈에 반영.',{x:px+0.3,y:5.12,w:pw-0.6,h:0.6,fontSize:12.5,color:C.g700,lineSpacingMultiple:1.3});
    L.T(s,'카드를 누르면 고객찾기의\n그 고객으로 바로 이동.',{x:px+0.3,y:5.8,w:pw-0.6,h:0.6,fontSize:11.5,bold:true,color:C.blue,lineSpacingMultiple:1.3});
    L.caption(s,{x:M,y:6.65,w:8.8,text:'※ 이름과 숫자는 예시 · 세트 1은 생략 · 정재민 카드 문구 일부는 가림',align:'left',size:10});
  }});
  // 2-6b 이유 유형
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 추천 이유의 종류',title:'MeAI가 고객을 추천하는 이유 세 갈래',sub:'카드 9장의 이유를 세 갈래로 나눔. 카드 태그와는 다른 분류.',pageNo:no});
    const rows=[['이유 유형','카드의 이유 문장 (예시)','무엇을 보고 골랐나'],['일정형 · 이벤트','"자동차보험 만기가 9일 뒤이고 운전자보험은 없습니다"','동의 만료 · 만기 · 상령일'],['보장 공백형','"실손이 없어 의료비 본인부담이 큽니다"','실손 · 수술비 · 진단비, 비어 있는 담보'],['관계형','"보상 완료 후 후속 상담이 없었습니다"','CRM 상담 이력 · 접촉 공백']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?11:12.5, bold: ri===0||ci===0, color: ri===0? C.g600 : C.g800, fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[4,10,4,10]}})));
    s.addTable(data,{x:M,y:1.85,w:W-2*M,colW:[2.3,5.6,4.23],rowH:0.88,border:{type:'solid',color:C.g200,pt:0.75}});
    L.note(s,{x:M,y:5.6,w:W-2*M,h:1.0,label:'읽는 법',text:'일정형은 오늘 연락 · 공백형은 제안이 정해진 카드 · 관계형은 만남의 명분',tone:'blue',size:12.5});
  }});
  // 2-7 범례
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 범례',title:'태그·동의·유형, 색으로 읽기',sub:'MeAI 홈 맨 아래 범례. 추천 카드 태그 3종은 아래에 따로 정리.',pageNo:no});
    L.img(s,HERO('fix_legend_tight'),{x:M,y:1.85,w:W-2*M,h:2.1,valign:'top'});
    // 추천 카드 태그 3종 (범례 캡처에 없는 것만)
    const cy=4.3, chh=2.6;
    L.R(s,{x:M,y:cy,w:W-2*M,h:chh,fill:C.white,line:C.g200,radius:0.14,shadow:true});
    L.T(s,'추천 카드 태그 3종',{x:M+0.35,y:cy+0.28,w:6,h:0.36,fontSize:15,bold:true,color:C.navy});
    const cw=(W-2*M-0.7)/3;
    [['#보장 공백',C.red50,C.red,'부족한 담보가 있음'],['#당월 타겟',C.purple50,C.purple,'이번 달 영업 목표 대상'],['#이벤트 임박',C.blue50,C.blue,'만기·동의 만료·상령일이 코앞']].forEach((t,i)=>{ const x=M+0.35+i*cw, y=cy+0.95; L.chip(s,{x,y,text:t[0],fill:t[1],color:t[2],size:13,h:0.42}); L.T(s,t[3],{x,y:y+0.58,w:cw-0.3,h:0.36,fontSize:13.5,color:C.g700,valign:'middle'}); });
    L.T(s,'고객찾기 그룹 태그는 PART 4',{x:M+0.35,y:cy+chh-0.5,w:6,h:0.3,fontSize:11,color:C.g500});
  }});
  // 2-8 MeAI 홈에서 갈 수 있는 곳
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 길 안내',title:'MeAI 홈에서 가는 곳, 다섯 군데',sub:'카드나 버튼을 한 번 누르면 이동. 돌아올 땐 어디서든 왼쪽 위 [MeAI 홈].',pageNo:no});
    L.R(s,{x:5.2,y:3.6,w:2.95,h:1.3,fill:C.navy,line:null,radius:0.16,shadow:true});
    L.T(s,'MeAI 홈',{x:5.2,y:3.65,w:2.95,h:0.7,fontSize:20,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
    L.T(s,'영업포탈 → MeAI',{x:5.2,y:4.25,w:2.95,h:0.4,fontSize:11,color:'FFFFFF',transparency:25,align:'center',valign:'middle'});
    const dest=[[M,2.7,'일반대화','[일반대화] 카드','무엇이든 물어보는 창. 상품·약관·화법.',C.blue],[M,4.35,'맞춤대화','[맞춤대화] 카드 → 고객 검색 팝업','고객을 고르면 그 고객의 대화가 열림. (PART 3)',C.red],[8.9,1.9,'MeAI 고객찾기','[MeAI 고객찾기 →] 버튼 · 추천 카드','그룹별 고객 목록과 다음 행동. (PART 4)',C.blue],[8.9,3.55,'게시판','오른쪽 위 [게시판] 버튼','공지·이슈·기능안내. 빨간 점은 새 글. (PART 5)',C.g700],[8.9,5.2,'고객 동의','오른쪽 위 [고객 동의] 버튼','휴대폰 번호 → 동의 요청 알림톡. (PART 5)',C.g700]];
    dest.forEach(d=>{ L.R(s,{x:d[0],y:d[1],w:3.85,h:1.45,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,d[2],{x:d[0]+0.25,y:d[1]+0.12,w:3.4,h:0.38,fontSize:16,bold:true,color:d[5]}); L.T(s,d[3],{x:d[0]+0.25,y:d[1]+0.52,w:3.4,h:0.3,fontSize:11,bold:true,color:C.g600}); L.T(s,d[4],{x:d[0]+0.25,y:d[1]+0.85,w:3.4,h:0.55,fontSize:11.5,color:C.g600,lineSpacingMultiple:1.25}); });
    [[4.45,3.425,5.2,3.9,false],[4.45,5.075,5.2,4.6,true],[8.9,2.62,8.15,3.75,true],[8.9,4.27,8.15,4.27,false],[8.9,5.92,8.15,4.75,false]].forEach(l=> s.addShape('line',{x:Math.min(l[0],l[2]),y:Math.min(l[1],l[3]),w:Math.abs(l[2]-l[0]),h:Math.max(0.01,Math.abs(l[3]-l[1])),line:{color:C.g300,width:1.25,dashType:'dash'},flipV:l[4]}));
  }});
};
