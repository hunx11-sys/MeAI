module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  S.push({ part:'04', fn:(pres,no)=> L.divider(pres,{num:'04',title:'고객찾기\nMeAI가 그룹으로 묶어 둔 내 고객',sub:'"암진단비 부족 35명", 그룹을 누르면 그 고객만 모아 보기',learn:['왼쪽에서 오른쪽으로 읽는 3단 화면','그룹 14개와 설명 문구','고객 카드 · 한눈에 보기 6칸','동의별 다음 행동 · 검색'],pageNo:no}) });
  // 4-1 전체
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 화면 구성',title:'고객찾기는 왼쪽에서 오른쪽으로',sub:'고르고 → 펼쳐 보고 → MeAI 대화하고',pageNo:no});
    const g = L.img(s,HERO('find_full'),{x:M,y:1.85,w:8.5,h:5.05,valign:'top',align:'left'});
    const clip={x:0,y:0};
    L.pin(s,g,150,100,1,{clip}); L.pin(s,g,275,226,2,{clip}); L.pin(s,g,522,105,3,{clip}); L.pin(s,g,955,220,4,{clip}); L.pin(s,g,309,632,5,{clip}); L.pin(s,g,1211,146,6,{clip}); L.pin(s,g,1424,444,7,{clip}); L.pin(s,g,395,31,8,{clip}); L.pin(s,g,1150,75,9,{clip});
    // 캡처 속 '최근 업데이트 2026-08-06 06:00' — 10월 책이라 날짜·시각만 흰 상자로 가림(라벨은 남김, 2쪽과 같은 원칙)
    s.addShape('rect',{x:7.70, y:1.965, w:0.73, h:0.12, fill:{color:'FFFFFF'}, line:{color:'FFFFFF',width:0}});
    L.numList(s,{x:9.15,y:1.8,w:3.58,gap:0,titleSize:12,descSize:10,items:[
      {n:1,title:'고객 그룹',desc:'연락할 이유별로 묶인 그룹'},
      {n:2,title:'탭 전환',desc:'보장 기준 10개 · 영업 기회 3개'},
      {n:3,title:'그룹 설명',desc:'묶인 이유 한 줄 · [전체] 필터'},
      {n:4,title:'펼친 카드',desc:'이유 · 태그 · 한눈에 보기 6칸'},
      {n:5,title:'접힌 카드',desc:'누르면 펼쳐지고 오른쪽 패널도 바뀜'},
      {n:6,title:'추천 질문',desc:'일반대화용 · 맞춤대화용'},
      {n:7,title:'다음 버튼',desc:'[보장분석] · [맞춤대화 시작]'},
      {n:8,title:'검색창',desc:'이름·조건으로 검색'},
      {n:9,title:'[글씨 확대]',desc:'기본 ON, 끄면 원래 크기'},
    ]});
  }});
  // 4-2 그룹 목록
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 고객 그룹',title:'그룹 이름이 곧 연락 이유',sub:'보장 기준 10개 · 영업 기회 3개 · 신규 등록. 인원은 예시',pageNo:no});
    const g1 = L.img(s,HERO('find_groups_z'),{x:M,y:1.85,w:1.9,h:4.72,valign:'top',align:'left'}); L.caption(s,{x:M,y:g1.y+g1.h+0.05,w:g1.w,text:'보장 기준 탭',size:10});
    const g2 = L.img(s,HERO('find_left_opp_top_z'),{x:M+2.0,y:1.85,w:2.15,h:4.6,valign:'top',align:'left'}); L.caption(s,{x:g2.x,y:g2.y+g2.h+0.05,w:g2.w,text:'영업 기회 탭',size:10});
    const tagPg = (ctx.parts['04']||1)+6; // NEW 태그 색 장
    L.note(s,{x:M+2.0,y:5.3,w:2.15,h:0.55,text:`태그 색은 ${tagPg}쪽 참고`,tone:'blue',size:10.5});
    const rows=[['그룹','누가 들어오나','우선순위'],['신규 등록 고객','아직 분류 전인 신규 고객 · 다음 날 반영','-'],['암·뇌·심진단비 부족','진단비 2천만원 이하','3'],['표적항암 · 종수술비 부족','표적항암 5천만원 이하 · 종수술비 없음','3'],['지원일당 없음 · 치아 부족','간병인지원 입원일당 · 치아보철 없음','3'],['당월 영업 타겟|NEW','당월 회사 전략 담보 대상','1 (최상)'],['증권 5건 이상 · 월 50만원 이상','증권이 많거나 보험료가 큰 우량 고객','2'],['상령일 임박|NEW| · 생일 임박','30일 안에 보험 나이가 오름 · 곧 생일','2'],['사전동의 만료|NEW','만료 임박 · 재동의 대상','2']];
    // 'A|NEW|B' → NEW 만 작은 빨간 글씨
    const runs = (c)=> c.split('|').map(t=> t==='NEW'? {text:' NEW',options:{fontSize:8,bold:true,color:C.red}} : {text:t,options:{}});
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text: c.includes('|')? runs(c) : c, options:{fontFace:L.FONT,fontSize: 11, bold: ri===0||ci===0, color: ri===0? C.g600 : (ci===2? C.blue : C.g800), fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[3,8,3,8], align: ci===2?'center':'left'}})));
    s.addTable(data,{x:M+4.4,y:1.85,w:7.73,colW:[2.7,3.98,1.05],rowH:0.5,border:{type:'solid',color:C.g200,pt:0.75}});
    L.caption(s,{x:M+4.4,y:6.45,w:7.73,text:'한 고객이 여러 그룹에 들 수 있음',align:'left',size:10});
  }});
  // 4-3 그룹 설명 문구
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 그룹 설명',title:'그룹 설명 한 줄이 곧 상담 화법',sub:'그룹을 누르면 설명이 생성. 앞은 그룹 기준, 뒤는 고객 맞춤 화법',pageNo:no});
    const h1 = L.img(s,HERO('find_header'),{x:M,y:1.85,w:7.4,h:1.45,valign:'top',align:'left'});
    const h2 = L.img(s,AG('find010','11_group_brain_header'),{x:M,y:3.45,w:7.4,h:1.45,valign:'top',align:'left'});
    const px={dsf:1}; // 캡처 픽셀 좌표 그대로
    L.pin(s,h1,365,72,1,px); L.pin(s,h1,125,195,2,px); L.pin(s,h2,315,186,3,px);
    // 셋째 캡처: 생일 임박(방송교안 10장과 같은 예) — 화법 문장 끝에 핀 4
    const h3 = L.img(s,AG('find010','21_group_birthday_header'),{x:M,y:5.05,w:7.4,h:1.45,valign:'top',align:'left'});
    L.pin(s,h3,152,186,4,px);
    [{n:1,title:'그룹 이름 · 인원',desc:'"암진단비 부족 35명" · [전체]로 동의 고객만 골라 보기'},{n:2,title:'설명 한 줄',desc:'앞은 묶인 기준, 뒤는 말할 방향(화법)'},{n:3,title:'그대로 첫 말로',desc:'"재활·간병 기간이 길어 진단비가 곧 생활비예요."'},{n:4,title:'생일 임박이면',desc:'축하 인사로 열고, MeAI 맞춤대화 보장 점검'},{n:5,title:'문자 초안은 MeAI에게',desc:'오른쪽 일반대화 추천 질문을 누르면\n이 그룹에 보낼 안내 문자 초안이 완성(PART 8)'}].forEach((it,i)=> L.numList(s,{x:8.4,y:1.95+i*0.95,w:4.33,titleSize:14,descSize:12,items:[it]}));
  }});
  // 4-3b 그룹 설명 전체 표
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 그룹 설명 문구 모음',title:'그룹별 한 줄 화법 모음',sub:'화면 설명 문구에서 기준 문장 뒤의 화법만 모음',pageNo:no});
    const rows=[['그룹','화면의 화법 문장 (그대로)'],['암진단비 부족','치료비 실제 부담액을 기준으로 설명하면 필요가 분명해집니다.'],['뇌진단비 부족','뇌질환은 재활·간병 기간이 길어 진단비가 곧 생활비 대체 수단이 됩니다.'],['심진단비 부족','심장질환은 시술 반복과 재발이 잦아 한 번의 진단비로는 부족합니다.'],['표적항암 부족','표적·면역 항암은 회차당 비용이 커서 별도 특약 없이는 감당이 어렵습니다.'],['종수술비 부족','수술은 암보다 발생 빈도가 높아 실제 청구가 가장 많이 일어나는 담보입니다.'],['지원일당 없음','간병비는 하루 단위로 나가는 실지출이라 일당이 없으면 부담이 그대로 남습니다.'],['치아 부족','임플란트·브릿지는 실손으로 보장되지 않아 전액 본인 부담입니다.'],['당월 영업 타겟','이번 달 안에 우선 접촉하는 것이 유리합니다.'],['증권 5건 이상','보험에 대한 관심과 니즈가 높은 고객입니다.'],['월 50만원 이상','납입 규모가 큰 편이므로 보험료 대비 보장 수준을 점검할 대상입니다.'],['상령일 임박','같은 보장을 더 싸게 준비할 수 있는 마지막 구간입니다.'],['생일 임박','축하 인사로 대화를 열고 자연스럽게 보장 점검으로 이어가기 좋은 시점입니다.'],['사전동의 만료','만료 전에 재동의를 받아야 이후에도 안내와 연락을 이어갈 수 있습니다.'],['신규 등록 고객','상세 정보는 익일 반영됩니다.']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?10.5:11.5, bold: ri===0||ci===0, color: ri===0? C.g600 : (ci===0? C.navy : C.g800), fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[2,10,2,10]}})));
    s.addTable(data,{x:M,y:1.85,w:W-2*M,colW:[2.3,9.83],rowH:0.31,border:{type:'solid',color:C.g200,pt:0.75}});
    L.caption(s,{x:M,y:6.6,w:W-2*M,text:'2026.09.29 확정 화면 기준 · 오픈 시 바뀔 수 있음',align:'left',size:10});
  }});
  // 4-4 카드 접힌/펼친
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 고객 카드',title:'카드를 누르면 펼쳐지는 여섯 칸',pageNo:no});
    const a = L.img(s,HERO('find_aicard_z'),{x:M,y:1.5,w:7.4,h:1.3,valign:'top',align:'left'}); L.caption(s,{x:M,y:a.y+a.h+0.04,w:7.4,text:'접힌 카드 · AI 추천 고객 리본',size:10});
    const g = L.img(s,HERO('find_card_z'),{x:M,y:3.2,w:7.4,h:3.7,valign:'top',align:'left'});
    const clip={x:320,y:195}, o={clip,dsf:3};
    const sixPg = (ctx.parts['04']||1)+7; // 여섯 칸 장(NEW 태그 색 장 다음)
    L.pin(s,g,321,228,1,o); L.pin(s,g,321,275,2,o); L.pin(s,g,962,268,3,o); L.pin(s,g,321,320,4,o); L.pin(s,g,321,370,5,o); L.pin(s,g,962,470,6,o);
    [{n:1,title:'이름 · 나이 · 유형',desc:'담당자가 다르면 "담당 OOO" 표시'},{n:2,title:'이유 한 문장',desc:'"암진단비가 1천만원대에 머물러 있습니다."'},{n:3,title:'사전조회동의 D-n',desc:'동의 만료(90일)까지 남은 날. 만료면 "필요", 철회면 "철회"'},{n:4,title:'태그 (우선순위 순)',desc:'보라 = 당월 타겟. 부족 그룹은 그룹마다 색이 다름'},{n:5,title:'이 고객 한눈에 보기',desc:`여섯 칸 자세한 설명은 ${sixPg}쪽`},{n:6,title:'점선 칸 · 미확인',desc:'자료가 없으면 "미확인". 추정하지 않음'}].forEach((it,i)=> L.numList(s,{x:8.4,y:1.6+i*0.9,w:4.33,titleSize:13.5,descSize:11.5,items:[it]}));
  }});
  // 4-x NEW 부족 태그 색 (새 목업 v2)
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · NEW 태그 색',title:'부족 태그는 이제 색으로 구분',sub:'부족 그룹 7개가 저마다 다른 색. 여러 개 붙어도 한눈에 구분',pageNo:no,tag:{text:'NEW',fill:C.blue50,color:C.blue}});
    const chip=(n,x,y)=> L.img(s,HERO('v2_chip_'+n),{x,y,w:1.7,h:0.36,round:false,shadow:false,align:'left',valign:'top'});
    L.R(s,{x:M,y:1.9,w:5.75,h:4.95,fill:C.white,line:C.g200,radius:0.14});
    L.T(s,'부족 그룹 · 색 7가지',{x:M+0.25,y:2.05,w:3.2,h:0.34,fontSize:13,bold:true,color:C.navy,valign:'middle'});
    L.T(s,'우선순위 3',{x:M+3.6,y:2.05,w:1.9,h:0.34,fontSize:11,color:C.g600,align:'right',valign:'middle'});
    ['cancer','brain','heart','target'].forEach((n,i)=>chip(n,M+0.25,2.5+i*0.46));
    ['surgery','daily','tooth'].forEach((n,i)=>chip(n,M+2.2,2.5+i*0.46));
    const grp=[['당월 영업 타겟','1',['monthly']],['증권 · 납입','2',['policy5','premium50']],['날짜 임박','2',['ageup','birthday','consentexp']]];
    grp.forEach((g,k)=>{ const x=M+0.25+k*1.85; L.T(s,g[0],{x,y:4.5,w:1.8,h:0.3,fontSize:11.5,bold:true,color:C.navy,valign:'middle'}); L.T(s,'우선순위 '+g[1],{x,y:4.8,w:1.8,h:0.26,fontSize:10,color:C.g600,valign:'middle'}); g[2].forEach((n,i)=>chip(n,x,5.15+i*0.46)); });
    L.label(s,{x:6.65,y:1.95,w:6.1,text:'고객 카드에는 우선순위 순서대로 표시',color:C.blue,size:12});
    const g=L.img(s,HERO('v2_card_tags_z'),{x:6.65,y:2.3,w:6.08,h:2.3,valign:'top',align:'left'});
    s.addShape('roundRect',{x:g.x+62*g.scale,y:g.y+338*g.scale,w:1030*g.scale,h:96*g.scale,fill:{type:'none'},line:{color:C.blue,width:2},rectRadius:0.06});
    [['1','보라','이번 달 목표',C.purple,C.purple50],['2','파랑 · 주황','우량 · 날짜 임박',C.blue,C.blue50],['3','색 7가지','부족한 보장',C.red,C.red50]].forEach((c,k)=>{ const x=6.65+k*2.07, y=4.95, w=1.94, h=1.9;
      L.R(s,{x,y,w,h,fill:c[4],line:null,radius:0.14});
      L.T(s,'우선순위 '+c[0],{x:x+0.2,y:y+0.18,w:w-0.4,h:0.3,fontSize:11,bold:true,color:c[3],valign:'middle'});
      L.T(s,c[1],{x:x+0.2,y:y+0.6,w:w-0.4,h:0.5,fontSize:18,bold:true,color:C.navy,valign:'middle'});
      L.T(s,c[2],{x:x+0.2,y:y+1.15,w:w-0.4,h:0.4,fontSize:13,color:C.g700,valign:'middle'}); });
  }});
  // 4-5 여섯 칸
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 이 고객 한눈에 보기',title:'여섯 칸으로 보는 이 고객의 상황',pageNo:no});
    const g = L.img(s,HERO('find_six_z'),{x:M,y:1.5,w:W-2*M,h:2.7,valign:'top'});
    L.caption(s,{x:g.x,y:g.y+g.h+0.04,w:g.w,text:'숫자는 예시',size:10});
    const cells=[['가입한 보험','보유 계약 수. "지금 세 건 갖고 계세요"로 대화 시작'],['보험료 납입','연간 납입액. 예산 감각을 잡는 기준'],['접촉기회','최근 고객 행동. 계약변경조회는 관심 신호'],['부족 금액','권장 기준 대비 부족한 진단비. 이 금액이 곧 제안 크기'],['1-5종수술비(plus)','수술 담보 유무. "없음"이 곧 제안 포인트'],['표적항암약물허가치료비(비급여)','자료가 없으면 미확인. 보장분석에서 확인']];
    cells.forEach((c,i)=>{ const col=i%3,row=Math.floor(i/3); const x=M+col*4.115,y=4.62+row*1.2,w=3.9,h=1.08; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.12,shadow:true}); L.T(s,c[0],{x:x+0.22,y:y+0.13,w:w-0.4,h:0.3,fontSize:13.5,bold:true,color:C.navy,valign:'middle'}); L.T(s,c[1],{x:x+0.22,y:y+0.48,w:w-0.4,h:0.52,fontSize:11.5,color:C.g600,lineSpacingMultiple:1.2}); });
  }});
  // 4-6 다음 행동
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 다음 행동',title:'오른쪽 패널에서 고르는 다음 행동',pageNo:no});
    const g = L.img(s,HERO('find_right_z'),{x:M,y:1.5,w:5.2,h:5.4,valign:'top',align:'left'});
    const clip={x:1000,y:75}, o={clip,dsf:3};
    const o2={clip,dsf:3,d:0.28};
    L.pin(s,g,1004,102,1,o2); L.pin(s,g,1004,190,2,o2); L.pin(s,g,1004,317,3,o2); L.pin(s,g,1436,416,4,o2); L.pin(s,g,1436,478,5,o2); L.pin(s,g,1004,527,6,o2);
    L.numList(s,{x:6.2,y:1.6,w:6.5,gap:0.24,titleSize:14,descSize:12,items:[{n:1,title:'선택한 고객',desc:'카드를 바꾸면 패널도 바뀜'},{n:2,title:'일반대화용 추천 질문',desc:'그룹 조건에 맞는 안내 문자 문안 요청'},{n:3,title:'맞춤대화용 추천 질문',desc:'누르면 질문이 채워진 채로 이 고객의 맞춤대화 시작'},{n:4,title:'[보장분석]',desc:'영업포탈의 이 고객 보장분석 화면으로 이동'},{n:5,title:'[이 고객으로 맞춤대화 시작]',desc:'고객을 고른 상태로 맞춤대화 시작.\n동의가 필요한 고객은 이 자리에 [사전조회동의 요청하기]'},{n:6,title:'안내 문구',desc:'고객을 다시 찾을 필요가 없다는 뜻'}]});
  }});
  // 4-6b 추천 질문 클릭 결과
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 추천 질문 → 대화',title:'질문이 채워진 채로 열리는 대화',pageNo:no});
    // 앞 장 김도윤 패널에서 맞춤대화 추천 질문을 눌러 들어온 화면(bc3_custom_main = CSS 1440×900 전체, dsf 2)
    const g = L.img(s,HERO('bc3_custom_main'),{x:M,y:1.5,w:7.9,h:5.3,valign:'top',align:'left'});
    const o={clip:{x:0,y:0},dsf:2,d:0.28};
    L.pin(s,g,180,153,1,o); L.pin(s,g,456,128,2,o); L.pin(s,g,1284,123,3,o); L.pin(s,g,456,541,4,o); L.pin(s,g,456,743,5,o); L.pin(s,g,456,798,6,o); L.pin(s,g,1030,28,7,o);
    L.caption(s,{x:g.x,y:g.y+g.h+0.05,w:g.w,text:'김도윤 패널에서 맞춤대화 추천 질문을 누른 화면 · 이름·계약·남은 날은 예시',size:10});
    const rx = g.x+g.w+0.35, rw = W-M-rx;
    let cy=1.55;
    [{n:1,title:'담당 고객',desc:'고른 고객이 이미 들어와 있음.\n사전조회동의 남은 날(화면엔 \'보장분석 동의\')',two:true},{n:2,title:'정상 계약 리스트',desc:'상품명 · 보험료 · 납입기간 · 기납입보험료'},{n:3,title:'약관 자료 준비 상태',desc:'구성 완료 · 구성 중 · 미확보.\n구성 완료가 아닌 상품은 답이 부정확할 수 있음',two:true},{n:4,title:'MeAI 안내',desc:'"김도윤님의 보험 가입 내역이에요…"'},{n:5,title:'[보장분석 해줘]',desc:'입력창 위 버튼 하나로 전체 그림부터'},{n:6,title:'채워진 질문',desc:'누른 추천 질문이 이미 입력됨. 전송(↑)만 누르면 시작'},{n:7,title:'상단 버튼',desc:'보장 분석 · 사용중인 정보 수정 · 요약 리포트'}].forEach(it=>{ L.numList(s,{x:rx,y:cy,w:rw,titleSize:13,descSize:11,items:[{n:it.n,title:it.title,desc:it.desc}]}); cy += 0.72 + (it.two?0.24:0); });
  }});
  // 4-7 동의 상태별
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 동의 상태별',title:'동의 상태별로 달라지는 다음 행동',sub:'맞춤대화는 보장 내역을 읽기 때문에 동의가 먼저. "D-n"이면 바로, "필요"면 알림톡 한 통',pageNo:no});
    const trio=[['사전조회동의 D-30 · 유효','30_right_panel_kimdoyun','[이 고객으로 맞춤대화 시작]으로 바로 시작.\n동의일부터 90일 동안 MeAI 맞춤대화 가능',C.blue,3.45],['사전조회동의 필요 · 만료','32_right_panel_kimminsu','[사전조회동의 요청하기] → 휴대폰 번호 입력 → 알림톡\n예: 김민수 고객',C.red,3.45],['사전조회동의 철회','34_right_panel_kimboram','회색 · 정보를 볼 수 없음. 버튼도 없음.\n우회 말고 새 동의부터',C.g700,1.4]];
    const gs = trio.map((t,i)=>{ const x=M+i*4.115,w=3.9; L.label(s,{x,y:1.85,w,text:t[0],color:t[3],size:12}); const gg=L.img(s,AG('find010',t[1]),{x,y:2.2,w,h:t[4],valign:'top',align:'left'}); L.T(s,t[2],{x,y:gg.y+gg.h+0.12,w,h:0.62,fontSize:12,color:C.g700,lineSpacingMultiple:1.25}); return gg; });
    // 186명 상자는 가운데 '필요 · 만료' 열의 이야기 → 빨강 톤 + 가운데 [사전조회동의 요청하기] 버튼 쪽을 가리키는 꼬리
    const bx=M+2*4.115, by=4.4, bw=3.9, bh=1.85, ty=gs[1].y+648*gs[1].scale; // ty = 가운데 캡처 속 요청 버튼 높이(캡처 px 648)
    L.R(s,{x:bx,y:by,w:bw,h:bh,fill:C.red50,line:null,radius:0.14});
    s.addShape('triangle',{x:bx-0.27,y:ty-0.1,w:0.34,h:0.2,rotate:270,fill:{color:C.red},line:{color:C.red,width:0}}); // ◀ 가운데 열을 가리킴
    L.T(s,'필요 · 만료 고객 수는\nMeAI 홈 "사전조회 동의 필요"에 표시',{x:bx+0.3,y:by+0.12,w:bw-0.45,h:0.56,fontSize:11,bold:true,color:C.red,valign:'middle',lineSpacingMultiple:1.15});
    s.addText([{text:'186',options:{fontSize:40,bold:true,color:C.navy,fontFace:L.FONT}},{text:' 명',options:{fontSize:16,bold:true,color:C.g700,fontFace:L.FONT}},{text:'   예시',options:{fontSize:10,color:C.g500,fontFace:L.FONT}}],{x:bx+0.3,y:by+0.66,w:bw-0.6,h:0.72,isTextBox:true,margin:0,valign:'middle'});
    L.T(s,'동의를 받아야 맞춤대화가 열리는 고객',{x:bx+0.3,y:by+1.38,w:bw-0.35,h:0.35,fontSize:12,color:C.g700,valign:'middle'});
    L.T(s,'동의하면 15분 안팎으로 반영 · MeAI 홈 [고객 동의]에서도 사전조회동의 발송 가능',{x:M,y:6.55,w:W-2*M,h:0.3,fontSize:11.5,color:C.g600,valign:'middle'});
  }});
  // 4-8 검색·필터
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 검색 · 필터 · 페이지',title:'이름으로도, 조건으로도 검색',sub:'검색창을 누르면 추천 속성, 글자를 치면 연관검색어 표시',pageNo:no});
    const a = L.img(s,HERO('gb5_search_attr_m'),{x:M,y:1.85,w:5.95,h:1.5,valign:'top',align:'left'}); L.caption(s,{x:M,y:a.y+a.h+0.04,w:5.95,text:'빈 검색창 → 추천 속성(암진단비 · 실손 · 상령일 · 자동차)',size:10});
    const b = L.img(s,HERO('search_suggest_crop'),{x:M+6.2,y:1.85,w:5.93,h:2.4,valign:'top',align:'left'}); L.caption(s,{x:M+6.2,y:b.y+b.h+0.04,w:5.93,text:'"암진단비" 입력 → 연관검색어',size:10});
    L.img(s,HERO('fix_c_filter_dropdown'),{x:M,y:3.9,w:2.3,h:2.3,valign:'top',align:'left'});
    [{n:1,title:'[전체] 드롭다운',desc:'사전조회동의 · 상품소개동의 고객만 골라 보기'},{n:2,title:'검색 결과 N명',desc:'그룹 제목이 "검색 결과 N명"으로 바뀜\n없으면 0명'},{n:3,title:'페이지',desc:'목록 아래 ‹ 1 2 ›로 넘기기'}].forEach((it,i)=> L.numList(s,{x:M+2.55,y:[3.95,4.75,5.78][i],w:3.45,titleSize:13,descSize:11,items:[it]})); // 2번 설명은 한 줄이면 3.45 폭을 넘어 '0/명'으로 끊김 → 두 줄로 나누고 3번을 0.23 내림
    const c = L.img(s,AG('find010','53_search_no_result'),{x:M+6.2,y:4.72,w:5.93,h:1.85,valign:'top',align:'left'}); L.caption(s,{x:M+6.2,y:c.y+c.h+0.04,w:5.93,text:'결과가 없을 때',size:10});
  }});
  // 4-9 시나리오
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 4 · 그룹 활용',title:'영업 타이밍에 따라 활용하는 그룹',sub:'그룹 하나가 곧 연락 목록. 월초 · 매주 · 매달 · 수시, 네 그룹을 습관으로. 인원은 예시',pageNo:no});
    const sc=[['월초','당월 영업 타겟','7명','우선순위 1위.\n추천 이유를 그대로 첫 말로',C.purple,C.purple50],['매주','상령일 · 생일 임박','11명 · 7명','보험료가 오르기 전 점검.\n생일엔 축하 인사로 열고,\nMeAI 맞춤대화 보장 점검',C.orange,C.orange50],['매달','사전동의 만료','35명','만료 전에 미리 안내.\n만료되면\n[사전조회동의 요청하기]',C.orange,C.orange50],['수시','신규 등록 고객','4명','상세는 다음 날 반영.\n바로 보려면\n[이 고객으로 맞춤대화 시작]',C.blue,C.blue50]];
    sc.forEach((c,i)=>{ const x=M+i*3.077,w=2.9,y=1.9,h=3.35; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.chip(s,{x:x+0.25,y:y+0.25,text:c[0],fill:c[5],color:c[4],size:11,h:0.32}); L.T(s,c[1],{x:x+0.25,y:y+0.78,w:w-0.5,h:0.36,fontSize:16,bold:true,color:C.navy,valign:'middle'}); L.T(s,c[2],{x:x+0.25,y:y+1.18,w:w-0.5,h:0.66,fontSize:30,bold:true,color:c[4],valign:'middle'}); L.T(s,c[3],{x:x+0.25,y:y+2.05,w:w-0.5,h:1.15,fontSize:12.5,color:C.g600,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:5.55,w:W-2*M,h:0.95,label:'보장 부족 그룹은',text:'주력 상품 담보부터. 이번 달 주력 상품이 정해지면 그 담보의 부족 그룹을 먼저 열기',tone:'dark',size:13});
  }});
};
