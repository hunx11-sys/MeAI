module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  S.push({ part:'02', fn:(pres,no)=> L.divider(pres,{num:'02',title:'MeAI 대문\n하루가 시작되는 곳',sub:'PC 영업포탈에서 MeAI로 들어오면 이 화면이 먼저 열려요. 오늘 만날 고객과 첫 마디가 이미 준비돼 있어요.',learn:['대문 다섯 구역과 오른쪽 위 버튼 두 개','내 고객 숫자 4개의 뜻 · 오늘의 추천 고객 읽는 법','태그 · 동의 표시 · 고객 유형 범례'],pageNo:no}) });
  // 2-1 전체 화면
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 대문 화면 구성',title:'MeAI 대문, 한 화면에 오늘 할 일이 다 있어요',sub:'위에서 아래로 다섯 구역, 오른쪽 위에 버튼 두 개예요. 이름만 익혀 두면 다음 장부터는 술술 읽혀요.',pageNo:no});
    const g = L.img(s,HERO('gate_full'),{x:M,y:1.9,w:7.4,h:5.0,valign:'top',align:'left'});
    const clip={x:0,y:0};
    L.pin(s,g,60,110,1,{clip}); L.pin(s,g,720,265,2,{clip}); L.pin(s,g,60,400,3,{clip}); L.pin(s,g,720,610,4,{clip}); L.pin(s,g,60,1200,5,{clip}); L.pin(s,g,960,40,6,{clip});
    L.numList(s,{x:8.35,y:1.9,w:4.35,gap:0.1,titleSize:12,descSize:10,items:[
      {n:1,title:'인사 + 최근 업데이트',desc:'"OO님 안녕하세요, 무엇을 도와드릴까요?" 오른쪽 시각이 데이터 기준 시점이에요.'},
      {n:2,title:'일반대화 · 맞춤대화 카드',desc:'무엇이든 묻는 일반대화, 고객 한 명을 위한 맞춤대화. 맞춤대화를 누르면 고객 검색 팝업이 떠요.'},
      {n:3,title:'내 고객 찾기 · 숫자 4개',desc:'내 전체 고객 · 맞춤대화 가능 · 사전조회 동의 필요 · 상품제안 가능. [MeAI 고객찾기 →] 버튼으로 그룹 화면 이동.'},
      {n:4,title:'오늘의 추천 고객',desc:'연락할 이유가 한 문장으로 붙은 카드 3장. 화살표로 세트 3개를 넘겨 봐요.'},
      {n:5,title:'범례',desc:'태그 색, 사전조회 동의 상태, 고객 유형(보유·가망·이관)의 뜻.'},
      {n:6,title:'고객 동의 · 게시판',desc:'오른쪽 위 버튼 두 개. 고객 동의는 휴대폰 번호로 동의 요청 알림톡을 보내는 창, 게시판의 빨간 점은 새 글 표시.'},
    ]});
  }});
  // 2-2 대화 카드
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 대화 카드',title:'먼저 어떤 대화를 시작할지 골라요. 나머지는 MeAI가 준비해요',sub:'대문 맨 위 카드 두 장. 고객을 정하지 않은 질문은 왼쪽, 고객 한 명을 위한 질문은 오른쪽이에요.',pageNo:no});
    const g = L.img(s,HERO('gate_cards'),{x:M,y:1.9,w:W-2*M,h:1.75,valign:'top'});
    L.card(s,{x:M,y:3.95,w:5.95,h:1.95,kicker:'일반대화 · 왼쪽 카드',title:'약관, 보장내용, 상담 포인트를 확인할 수 있어요',desc:'고객을 특정하지 않아요. 상품·특약 개념, 화법, 약관 지식, 자사·타사 보장 비교처럼 공부하고 준비할 때 써요. 누르면 바로 일반대화 화면이 열려요.',titleSize:13});
    L.card(s,{x:M+6.2,y:3.95,w:5.95,h:1.95,kicker:'맞춤대화 · 오른쪽(검은) 카드',title:'고객의 보장 내역을 기반으로 맞춤형 답변을 받을 수 있어요',desc:'고객 한 명의 보장분석을 MeAI가 함께 봐요. 누르면 고객 검색 팝업이 먼저 뜨고, 고객을 고르면 그 고객의 맞춤대화가 시작돼요(PART 3).',titleSize:13,accent:C.red});
    L.note(s,{x:M,y:6.1,w:W-2*M,h:0.5,label:'TIP',text:'처음엔 일반대화로 감을 익히고, 고객을 만나기 전에는 꼭 맞춤대화로 준비하세요. 어느 카드든 화면 왼쪽 위 [MeAI 홈]으로 대문에 돌아와요.',tone:'grey',size:10.5});
  }});
  // 2-3 숫자 4개
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 내 고객 찾기',title:'내 고객 숫자 4개, 매일 아침 한 번만 훑어보세요',sub:'"사전조회 동의 필요"가 늘었는지, "맞춤대화 가능"이 몇 명인지. 이 숫자가 오늘 할 일의 크기예요.',pageNo:no});
    L.img(s,HERO('gate_stats'),{x:M,y:1.9,w:W-2*M,h:2.05,valign:'top'});
    const cards=[['342명','내 전체 고객','내가 담당하는 고객 전부. 보유·가망·이관을 모두 더한 수예요.',C.navy],['137명','맞춤대화 가능','사전조회 동의가 유효한 고객. 지금 바로 맞춤대화를 시작할 수 있어요.',C.blue],['186명','사전조회 동의 필요','동의가 없거나 만료된 고객. 이 숫자가 곧 동의 재취득 캠페인 목록이에요.',C.red],['84명','상품제안 가능','상품 소개에 동의한 고객. 카드에 "AI 추천 고객" 리본이 붙어요.',C.green]];
    cards.forEach((c,i)=>{ const x=M+i*3.08, y=4.2, w=2.9, h=2.0; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,c[0],{x:x+0.25,y:y+0.2,w:w-0.5,h:0.5,fontSize:22,bold:true,color:c[3],valign:'middle'}); L.T(s,c[1],{x:x+0.25,y:y+0.72,w:w-0.5,h:0.3,fontSize:12,bold:true,color:C.navy}); L.T(s,c[2],{x:x+0.25,y:y+1.05,w:w-0.5,h:0.9,fontSize:10,color:C.g600,lineSpacingMultiple:1.3}); });
    L.caption(s,{x:M,y:6.35,w:W-2*M,text:'※ 숫자는 예시예요. [MeAI 고객찾기 →] 빨간 버튼을 누르면 그룹별 고객 목록(PART 4)으로 이동해요. 데이터는 매일 새로 계산되어 익일 반영돼요.',align:'left'});
  }});
  // 2-4 오늘의 추천 고객 hero
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 오늘의 추천 고객',title:'오늘 연락할 사람을 MeAI가 먼저 골라 놓았어요',sub:'카드 3장이 한 세트, 세트 3개. 좌우 화살표로 넘기고, 카드 아래 [MeAI 고객찾기에서 열기]로 들어가요.',pageNo:no});
    const g = L.img(s,HERO('gate_reco1'),{x:M,y:1.85,w:W-2*M,h:4.35,valign:'top'});
    const clip={x:150,y:580};
    L.pin(s,g,335,600,1,{clip}); L.pin(s,g,418,672,2,{clip}); L.pin(s,g,505,760,3,{clip}); L.pin(s,g,282,865,4,{clip}); L.pin(s,g,335,900,5,{clip}); L.pin(s,g,372,965,6,{clip}); L.pin(s,g,1168,663,7,{clip}); L.pin(s,g,1279,770,8,{clip}); L.pin(s,g,780,1030,9,{clip});
    L.pinStrip(s,{x:M,y:6.3,w:W-2*M,cols:5,rowH:0.34,size:9.5,items:[{n:1,text:'"오늘의 추천 고객" 구역'},{n:2,text:'이름 · 나이 · 유형 · 담당'},{n:3,text:'연락할 이유 한 문장 + 근거'},{n:4,text:'태그(#이벤트 임박 등)'},{n:5,text:'사전조회동의 D-n'},{n:6,text:'[MeAI 고객찾기에서 열기]'},{n:7,text:'AI 추천 고객 리본(상품제안 가능)'},{n:8,text:'다음 세트로 넘기기'},{n:9,text:'세트 위치(3개)'}]});
  }});
  // 2-5 카드 읽는 법
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 추천 카드 읽는 법',title:'카드 한 장에 "누구 · 왜 · 언제까지 · 다음"이 다 들어 있어요',sub:'이 카드를 읽을 수 있으면 대문의 절반은 끝이에요. 이유 문장은 그대로 첫 말로 써도 돼요.',pageNo:no});
    const g = L.img(s,HERO('gate_card_z'),{x:M,y:1.85,w:5.0,h:5.0,valign:'top',align:'left'});
    const clip={x:160,y:625}, o={clip,dsf:3};
    L.pin(s,g,163,672,1,o); L.pin(s,g,519,672,2,o); L.pin(s,g,163,718,3,o); L.pin(s,g,163,790,4,o); L.pin(s,g,163,866,5,o); L.pin(s,g,163,901,6,o); L.pin(s,g,163,966,7,o);
    L.numList(s,{x:6.0,y:1.85,w:6.7,gap:0.08,titleSize:12,descSize:10,items:[
      {n:1,title:'이름 · 나이',desc:'고객 이름과 나이. 긴 이름은 줄여서 보여요.'},
      {n:2,title:'유형 · 담당',desc:'보유 / 가망 / 이관 중 하나와 담당자. 한 고객은 하나의 유형으로만 분류돼요.'},
      {n:3,title:'연락할 이유 (굵은 한 문장)',desc:'"부담보 해제가 5일 남았습니다." 이 문장이 고객에게 하는 첫 말이에요.'},
      {n:4,title:'근거 설명',desc:'왜 지금 좋은 기회인지 서너 줄로 풀어 줘요. 상담 방향이 여기서 정해져요.'},
      {n:5,title:'태그',desc:'#이벤트 임박(파랑) · #보장 공백(빨강) · #당월 타겟(보라). 색으로 성격을 구분해요.'},
      {n:6,title:'사전조회동의 D-n',desc:'동의 만료까지 남은 날. 만료되면 "사전조회동의 필요"로 바뀌고 재동의부터 받아야 해요.'},
      {n:7,title:'[MeAI 고객찾기에서 열기]',desc:'고객찾기 화면의 이 고객 카드로 바로 이동. 거기서 [이 고객으로 맞춤대화 시작].'},
    ]});
  }});
  // 2-6a 세트 2·3 카드 6장
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 추천 세트 3개',title:'추천은 매일 새로 계산돼요. 세트 3개, 카드 9장',sub:'화살표를 두 번 누르면 세트 2·3이 나와요. 세트 2·3의 카드 여섯 장이에요. 이유의 종류를 보면 MeAI가 무엇을 보고 고르는지 알 수 있어요.',pageNo:no});
    const cards=[['reco2_card1','세트 2'],['reco2_card2','세트 2'],['reco2_card3','세트 2'],['reco3_card1','세트 3'],['reco3_card2','세트 3'],['reco3_card3','세트 3']];
    cards.forEach((c,i)=>{ const col=i%3,row=Math.floor(i/3); const x=M+col*4.1, y=1.85+row*2.5; L.img(s,HERO(c[0]),{x,y,w:3.9,h:2.3,valign:'top',align:'left'}); });
    L.caption(s,{x:M,y:6.9-0.25,w:W-2*M,text:'위 줄: 세트 2 (박준호 · 노현정 · 오미선) · 아래 줄: 세트 3 (김민수 · 정재민 · 서은아) · 이름과 숫자는 예시예요',align:'left'});
  }});
  // 2-6b 이유 유형
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 추천 이유의 종류',title:'MeAI는 이런 이유로 추천해요',sub:'카드 9장의 이유 문장을 세 갈래로 나눠 봤어요. 어떤 정보를 보고 고르는지 알면 카드가 더 잘 읽혀요.',pageNo:no});
    const rows=[['이유 유형','카드의 이유 문장 (예시)','무엇을 보고 골랐나'],['일정형 · 이벤트','부담보 해제가 5일 남았습니다 / 가입설계동의가 이달 말 만료됩니다 / 자동차보험 만기가 9일 뒤이고 운전자보험은 없습니다 / 상령일이 2주 남았고 암진단비가 1천만원뿐입니다','부담보 해제일 · 동의 만료일 · 자동차 만기 · 상령일'],['보장 공백형','실손이 없어 의료비 본인부담이 큽니다 / 상령일이 25일 남았고 수술비 담보가 비어 있습니다 / 8개월간 접촉이 없었던 우량 고객입니다(뇌·심장 진단비 공백)','실손 · 수술비 · 진단비처럼 비어 있는 담보'],['관계·정리형','암진단비가 중복 가입돼 있어 보험료 부담이 큽니다 / 보상 완료 후 후속 상담이 없었습니다','계약 중복 · 보상 이력 · 접촉 공백']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?10.5:10.5, bold: ri===0||ci===0, color: ri===0? C.g600 : C.g800, fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[4,8,4,8]}})));
    s.addTable(data,{x:M,y:1.9,w:W-2*M,colW:[1.9,7.2,3.03],rowH:0.7,border:{type:'solid',color:C.g200,pt:0.75}});
    L.note(s,{x:M,y:5.0,w:W-2*M,h:0.9,label:'읽는 법',text:'일정형은 "언제까지"가 정해진 카드라 오늘 연락해야 해요. 보장 공백형은 "무엇을 제안할지"가 이미 정해진 카드예요. 관계·정리형은 만남의 명분이 있는 카드예요. 태그와 동의 D-n은 카드에서 함께 확인하세요.',tone:'blue',size:10.5});
    L.caption(s,{x:M,y:6.1,w:W-2*M,text:'※ 게시판 공지 기준, 오늘의 추천 고객은 CRM 데이터 반입이 완료되는 2차 오픈부터 보여요. 일정은 대문 게시판 공지를 확인하세요.',align:'left'});
  }});
  // 2-7 범례
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 범례',title:'태그 3종 · 동의 표시 3종 · 고객 유형 3종, 색으로 읽어요',sub:'대문 맨 아래 범례예요. 카드에 붙는 표시의 뜻이 전부 여기 있어요.',pageNo:no});
    L.img(s,HERO('gate_legend_z'),{x:M,y:1.85,w:W-2*M,h:1.65,valign:'top'});
    // 태그
    L.R(s,{x:M,y:3.75,w:3.9,h:2.95,fill:C.white,line:C.g200,radius:0.14,shadow:true});
    L.T(s,'추천 카드 태그 3종',{x:M+0.25,y:3.95,w:3.4,h:0.3,fontSize:12,bold:true,color:C.navy});
    [['#보장 공백',C.red50,C.red,'부족한 담보가 있어요'],['#당월 타겟',C.purple50,C.purple,'이번 달 영업 목표 대상'],['#이벤트 임박',C.blue50,C.blue,'만기·해제·상령일이 코앞']].forEach((t,i)=>{ const y=4.4+i*0.62; L.chip(s,{x:M+0.25,y,text:t[0],fill:t[1],color:t[2]}); L.T(s,t[3],{x:M+1.75,y,w:2.0,h:0.28,fontSize:10.5,color:C.g700,valign:'middle'}); });
    L.T(s,'화면 태그 분류표 기준 · 고객찾기 그룹 태그는 PART 4',{x:M+0.25,y:6.3,w:3.4,h:0.3,fontSize:9,color:C.g500});
    // 동의
    L.R(s,{x:M+4.1,y:3.75,w:3.9,h:2.95,fill:C.white,line:C.g200,radius:0.14,shadow:true});
    L.T(s,'동의 표시 3종',{x:M+4.35,y:3.95,w:3.4,h:0.3,fontSize:12,bold:true,color:C.navy});
    [['사전조회동의 D-n',C.g100,C.g700,'유효 · 만료까지 남은 일수'],['사전조회동의 필요',C.red50,C.red,'만료 · 재동의가 필요'],['AI 추천 고객',C.meritz,'FFFFFF','상품 소개 동의 · 제안 가능']].forEach((t,i)=>{ const y=4.4+i*0.62; L.chip(s,{x:M+4.35,y,text:t[0],fill:t[1],color:t[2]}); L.T(s,t[3],{x:M+6.0,y,w:1.95,h:0.28,fontSize:10.5,color:C.g700,valign:'middle'}); });
    L.T(s,'대문에 보이는 고객은 사전조회 동의일로부터 1년 이내 고객이에요.',{x:M+4.35,y:6.3,w:3.4,h:0.3,fontSize:9,color:C.g500});
    // 유형
    L.R(s,{x:M+8.2,y:3.75,w:3.93,h:2.95,fill:C.white,line:C.g200,radius:0.14,shadow:true});
    L.T(s,'고객 유형 3종',{x:M+8.45,y:3.95,w:3.4,h:0.3,fontSize:12,bold:true,color:C.navy});
    [['보유','계약이 있는 내 고객'],['가망','아직 계약 전, 등록만 된 고객'],['이관','다른 담당자에게서 넘겨받은 고객']].forEach((t,i)=>{ const y=4.4+i*0.62; L.chip(s,{x:M+8.45,y,text:t[0],fill:C.g100,color:C.g700}); L.T(s,t[1],{x:M+9.3,y,w:2.7,h:0.28,fontSize:10.5,color:C.g700,valign:'middle'}); });
    L.T(s,'한 고객은 보유·가망·이관 중 하나로만 분류돼요.',{x:M+8.45,y:6.3,w:3.4,h:0.3,fontSize:9,color:C.g500});
  }});
  // 2-8 대문에서 갈 수 있는 곳
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 2 · 길 안내',title:'대문에서 갈 수 있는 곳은 다섯 군데예요',sub:'모두 대문으로 돌아오는 [MeAI 홈] 버튼이 왼쪽 위에 있어요. 길을 잃을 걱정은 없어요.',pageNo:no});
    L.R(s,{x:5.2,y:3.6,w:2.95,h:1.3,fill:C.navy,line:null,radius:0.16,shadow:true});
    L.T(s,'MeAI 대문',{x:5.2,y:3.65,w:2.95,h:0.7,fontSize:18,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
    L.T(s,'영업포탈 → MeAI',{x:5.2,y:4.25,w:2.95,h:0.4,fontSize:10.5,color:'FFFFFF',transparency:25,align:'center',valign:'middle'});
    const dest=[[M,1.9,'일반대화','[일반대화] 카드','무엇이든 물어보는 창. 상품·약관·화법.',C.blue],[M,4.9,'맞춤대화','[맞춤대화] 카드 → 고객 검색 팝업','고객을 고르면 그 고객의 대화가 열려요. (PART 3)',C.red],[8.9,1.9,'MeAI 고객찾기','[MeAI 고객찾기 →] 버튼 · 카드의 [열기]','그룹별 고객 목록과 다음 행동. (PART 4)',C.blue],[8.9,3.55,'게시판','오른쪽 위 [게시판] 버튼','공지·이슈·기능안내. 빨간 점은 새 글. (PART 5)',C.g700],[8.9,5.2,'고객 동의','오른쪽 위 [고객 동의] 버튼','휴대폰 번호를 넣고 [보내기] → 동의 요청 알림톡. (PART 5)',C.g700]];
    dest.forEach(d=>{ L.R(s,{x:d[0],y:d[1],w:3.85,h:1.45,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,d[2],{x:d[0]+0.25,y:d[1]+0.13,w:3.4,h:0.36,fontSize:14,bold:true,color:d[5]}); L.T(s,d[3],{x:d[0]+0.25,y:d[1]+0.5,w:3.4,h:0.3,fontSize:10,bold:true,color:C.g600}); L.T(s,d[4],{x:d[0]+0.25,y:d[1]+0.82,w:3.4,h:0.55,fontSize:10,color:C.g600,lineSpacingMultiple:1.25}); });
    [[4.45,2.62,5.2,3.75,false],[4.45,5.62,5.2,4.75,true],[8.9,2.62,8.15,3.75,true],[8.9,4.27,8.15,4.27,false],[8.9,5.92,8.15,4.75,false]].forEach(l=> s.addShape('line',{x:Math.min(l[0],l[2]),y:Math.min(l[1],l[3]),w:Math.abs(l[2]-l[0]),h:Math.max(0.01,Math.abs(l[3]-l[1])),line:{color:C.g300,width:1.25,dashType:'dash'},flipV:l[4]}));
    L.note(s,{x:M,y:6.55,w:4.5,h:0.42,label:'',text:'대문 이후 화면의 왼쪽 위 [MeAI 홈]으로 언제든 돌아와요.',tone:'grey',size:9.5});
  }});
};
