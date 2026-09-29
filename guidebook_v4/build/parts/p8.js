module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  const SRC = '출처: 데이터분석팀 「MeAI 사용 실태 분석」·「MeAI 효과 분석」, 2026.08';
  S.push({ part:'08', fn:(pres,no)=> L.divider(pres,{num:'08',title:'영업관리자 편\n대문을 아침 조회(회의) 자료로',sub:'본부장님은 전파, 조직장님은 정착. 조회 자료는 대문이에요.',learn:['누구부터 챙길까','대문으로 조회하는 법','체크리스트 · 스크립트 · 4주 플랜'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 왜 관리자인가',title:'도구는 손에, 정착은 조직이',sub:'본부가 함께 시작하면 셋 중 둘이 남았어요.',pageNo:no});
    [['4,912명','과거엔 썼는데 이번 달 안 쓴 분','권한 부여자의 40.8%. 새 교육 없이 "다시 켜기"만 하면 돼요.',C.red],['65.2%','본부 단위로 시작한 분의 7개월 잔존','개별로 들어온 분은 35~41%만 남았어요.',C.blue],['26.9%','권한 받은 뒤 30일 안에 첫 사용','첫 사용이 빠를수록 정착률이 높아요. 첫 주가 골든타임.',C.green]].forEach((d,i)=>{ const x=M+i*4.1,y=1.95,w=3.9,h=2.95; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,d[0],{x:x+0.32,y:y+0.3,w:w-0.64,h:0.85,fontSize:40,bold:true,color:d[3],valign:'middle'}); L.T(s,d[1],{x:x+0.32,y:y+1.3,w:w-0.64,h:0.4,fontSize:14,bold:true,color:C.navy,valign:'middle'}); L.T(s,d[2],{x:x+0.32,y:y+1.82,w:w-0.64,h:0.95,fontSize:12,color:C.g600,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:5.2,w:W-2*M,h:1.0,label:'대화의 시작',text:'"도입이 안 됐다"가 아니라 "이미 다 써봤다"에서 시작하세요.',tone:'dark',size:14});
    L.caption(s,{x:M,y:6.45,w:W-2*M,text:SRC,align:'left',size:10});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 대문을 조회 자료로',title:'10월부터 대문이 조회 자료예요',sub:'리스트를 따로 뽑지 않아도, 대문이 영업 방향을 보여줘요.',pageNo:no});
    // 왼쪽: 고객 그룹(보장 기준 탭) 세로 캡처를 크게
    const gg = L.img(s,HERO('find_groups_z'),{x:M,y:1.85,w:2.0,h:4.72,valign:'top',align:'left'}); L.caption(s,{x:M,y:gg.y+gg.h+0.06,w:gg.w,text:'고객 그룹 · 보장 기준 탭',size:10});
    // 가운데: 숫자 4개 · 그룹 제목 · 물어볼 말(작게)
    const mx = M+gg.w+0.3, mw = 8.75-mx;
    const g1 = L.img(s,HERO('gate_stats'),{x:mx,y:1.85,w:mw,h:1.2,valign:'top',align:'left'}); L.caption(s,{x:mx,y:g1.y+g1.h+0.06,w:mw,text:'조회 첫 화면 · 팀원의 숫자 4개',size:10});
    const g2 = L.img(s,HERO('find_header'),{x:mx,y:3.72,w:mw,h:1.2,valign:'top',align:'left'}); L.caption(s,{x:mx,y:g2.y+g2.h+0.06,w:mw,text:'그룹 제목 · 인원 · 설명 문구',align:'left',size:10});
    L.note(s,{x:mx,y:5.72,w:mw,h:0.85,label:'이렇게 물어보세요',text:'"이번 주 상령일 고객 몇 명?"',tone:'dark',size:13});
    // 오른쪽: 번호 없이 굵은 제목 + 한 줄 설명
    const rx = 9.1, rw = W-M-rx;
    [['숫자 4개','"사전조회 동의 필요"가 이번 주 동의 목표 인원.'],['당월 영업 타겟','우선순위 1. 인원과 설명 문장을 함께 읽어요.'],['상령일 · 생일 임박','영업 기회 탭. 그대로 이번 주 접촉 계획표가 돼요.'],['사전동의 만료','D-n 짧은 순으로 대응 순서를 정해요.'],['게시판','응답 지연 같은 운영 이슈를 먼저 공유해요.']].forEach((it,i)=>{ const y=1.9+i*0.96;
      L.R(s,{x:rx,y:y+0.06,w:0.06,h:0.26,fill:C.blue,line:null,radius:0.03});
      L.T(s,it[0],{x:rx+0.2,y,w:rw-0.2,h:0.38,fontSize:14,bold:true,color:C.navy,valign:'middle'});
      L.T(s,it[1],{x:rx+0.2,y:y+0.4,w:rw-0.2,h:0.48,fontSize:12,color:C.g600,lineSpacingMultiple:1.2}); });
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 누구부터 챙길까',title:'타겟은 사용 이력으로 잡으세요',sub:'이력이 말해주는 네 그룹부터 챙기세요.',pageNo:no});
    [['4,912명','이탈','이번 달 쉬고 있는 사용자','"대문 한 번 열어 보세요" 한 마디면 돼요.',C.red],['3.9배','기존 FP','12차월 초과, 아직 미활용','10.0% → 38.6%.\n효과가 가장 큰 층이에요.',C.blue,'체결전환율 격차'],['2,156명','단발','"보장분석 해줘" 하나만 쓰는 분','꼬리질문을 알려주세요.\n질문 1개 11.99건 →\n2개 17.02건(가계약).',C.purple],['30일','신규 승인','권한 받은 지 30일 안 된 분','첫 7일이 골든타임. 본부장님이 직접 안내해 주세요.',C.green]].forEach((d,i)=>{ const x=M+i*3.08,w=2.9,y=1.85,h=3.25; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.chip(s,{x:x+0.25,y:y+0.25,text:d[1],fill:C.g100,color:d[4],size:10.5,h:0.32}); if (d[5]) s.addText([{text:d[0],options:{fontSize:30,bold:true,color:d[4],fontFace:L.FONT}},{text:'  '+d[5],options:{fontSize:11.5,bold:true,color:C.g600,fontFace:L.FONT}}],{x:x+0.25,y:y+0.7,w:w-0.4,h:0.65,isTextBox:true,margin:0,valign:'middle'}); else L.T(s,d[0],{x:x+0.25,y:y+0.7,w:w-0.5,h:0.65,fontSize:30,bold:true,color:d[4],valign:'middle'}); L.T(s,d[2],{x:x+0.25,y:y+1.42,w:w-0.5,h:0.62,fontSize:13.5,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15}); L.T(s,d[3],{x:x+0.25,y:y+1.98,w:w-0.5,h:1.15,fontSize:12.5,color:C.g600,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:5.35,w:W-2*M,h:0.85,label:'"신인이 안 쓴다"는 오해',text:'6차월 미만도 52.6%가 썼고, 팀원·관리자 차이는 1.3배뿐이에요.',tone:'grey',size:12});
    L.caption(s,{x:M,y:6.4,w:W-2*M,text:SRC,align:'left',size:10});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 이번 달 체크리스트',title:'이번 달, 여덟 줄만 부탁드립니다',sub:'위 두 줄이 최우선, 나머지는 여유가 될 때.',pageNo:no});
    const items=[['한동안 안 쓰신 분께 "대문 열어 보세요"','4,912명. 다시 켜기만 하면 돼요','최우선',C.red],['기존 FP(12차월 초과)를 먼저 챙겨 주세요','체결전환율 격차 3.9배, 가장 커요','최우선',C.red],['권한부여가 안 된 분을 찾아 주세요','기존 메뉴는 권한 필요 · 10/2 새 입구 3곳은 누구나','온보딩',C.blue,'적용 시점은 IT 일정에 따라 달라질 수 있어요'],['권한 받은 분께 직접 안내해 주세요','30일 안 첫 사용이 정착을 갈라요','온보딩',C.blue],['조회에서 대문을 함께 열어 주세요','숫자 4개 · 당월 타겟 · 추천 카드 1장','조회',C.blue],['"질문 이어 쓰기"를 안내해 주세요','꼬리질문 · 추천 질문. 질문 3개 이상이면 가계약 2.3배','확장',C.purple],['본부가 날짜를 정해 같이 시작해 주세요','7개월 잔존율 65.2% 대 개별 35~41%','정착',C.green],['도입 설명회에서 대문을 보여 주세요','"오늘 만날 고객을 회사가 찾아 준다"','리크루팅',C.g700]];
    const rh=0.52, rp=0.58; // 출처 줄 자리를 만들려고 줄 간격을 조금 줄임
    items.forEach((it,i)=>{ const y=1.85+i*rp; L.R(s,{x:M,y,w:W-2*M,h:rh,fill:C.white,line:C.g200,radius:0.1,shadow:false}); L.T(s,'✓',{x:M+0.22,y,w:0.4,h:rh,fontSize:14,bold:true,color:it[3],valign:'middle'}); L.T(s,it[0],{x:M+0.7,y,w:5.6,h:rh,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      if (it[4]) s.addText([{text:it[1],options:{fontSize:11.5,color:C.g600,fontFace:L.FONT,breakLine:true}},{text:it[4],options:{fontSize:10,color:C.g500,fontFace:L.FONT}}],{x:M+6.5,y,w:4.15,h:rh,isTextBox:true,margin:0,valign:'middle',lineSpacingMultiple:1.05});
      else L.T(s,it[1],{x:M+6.5,y,w:4.15,h:rh,fontSize:11.5,color:C.g600,valign:'middle'});
      L.chip(s,{x:W-M-1.35,y:y+(rh-0.31)/2,text:it[2],size:10.5,h:0.31,fill: it[3]===C.red? C.red50 : it[3]===C.blue? C.blue50 : it[3]===C.purple? C.purple50 : it[3]===C.green? C.green50 : C.g100,color:it[3]}); });
    L.caption(s,{x:M,y:1.85+7*rp+rh+0.1,w:W-2*M,text:SRC,align:'left',size:10});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 조회에서 말씀해 보세요',title:'조회에선 세 문장이면 충분해요',sub:'숫자로, 타겟으로, 행동으로 한 줄씩. 반론 셋은 미리 준비.',pageNo:no});
    const lines=[['숫자로','"같은 FP 안에서 비교해도 체결전환율이 9%에서 36%로 올라갑니다."','"같은 FP 비교"라는 조건을 꼭 함께 말해요.'],['타겟으로','"다시 권한부여 받을 분, 한동안 안 쓰신 분 계실까요?"','다음 행동을 바로 만드는 질문이에요.'],['행동으로','"10월부터 MeAI 대문이 열립니다. 조회 때 함께 열어보겠습니다."','대문 오픈을 조회 습관과 잇는 한 줄이에요.']];
    lines.forEach((l,i)=>{ const y=1.85+i*1.36; L.R(s,{x:M,y,w:7.4,h:1.24,fill: i===2? C.blue : C.white,line: i===2? null : C.g200,radius:0.14,shadow:i!==2}); L.chip(s,{x:M+0.25,y:y+0.18,text:l[0],size:10.5,h:0.3,fill: i===2?'2B6FE0':C.blue50,color: i===2?'FFFFFF':C.blue}); L.T(s,l[1],{x:M+0.25,y:y+0.5,w:6.9,h:0.4,fontSize:13.5,bold:true,color: i===2?'FFFFFF':C.navy,valign:'middle'}); L.T(s,l[2],{x:M+0.25,y:y+0.88,w:6.9,h:0.3,fontSize:11,color: i===2?'FFFFFF':C.g600,valign:'middle'}); });
    L.R(s,{x:8.3,y:1.85,w:4.43,h:3.96,fill:C.g50,line:C.g200,radius:0.14});
    L.T(s,'현장 반론 3가지',{x:8.55,y:2.02,w:3.95,h:0.38,fontSize:14,bold:true,color:C.navy});
    [['Q. 원래 될 고객이라 켠 거 아닌가요?','같은 FP 고객끼리 비교해도 9.0% → 36.0%예요.'],['Q. 계약이 더 빨라지나요?','속도 차이는 거의 없어요(12일 vs 13일).'],['Q. 신인용 도구 아닌가요?','연차별로는 기존 FP에서 격차가 가장 커요(미활용 10.0% → 활용 38.6%).']].forEach((q,i)=>{ const y=2.55+i*1.08; L.T(s,q[0],{x:8.55,y,w:3.95,h:0.32,fontSize:12,bold:true,color:C.blue,valign:'middle'}); L.T(s,q[1],{x:8.55,y:y+0.36,w:3.95,h:0.6,fontSize:11.5,color:C.g700,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:5.98,w:W-2*M,h:0.62,label:'과장은 금물',text:'"빨라진다"·"많이 판다" 대신 "성사된다"·"좋은 상품을 고른다".',tone:'grey',size:12});
    L.caption(s,{x:M,y:6.68,w:W-2*M,text:SRC,align:'left',size:10});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 4주 도입 플랜',title:'4주 플랜, 이 순서면 정착해요',sub:'본부가 같은 날 시작하고, 주마다 한 가지씩만.',pageNo:no});
    const wk=[['1주','권한 점검 · 대문 소개',['권한 미부여·이탈 명단 확인','PART 1 핵심 숫자 4개 공유','대문(PART 2) 함께 열기']],['2주','5일 미션 전원 시작',['PART 7 첫 5일 미션 시작','추천 카드 → 고객찾기 열기','"대문 열어보셨어요?" 한마디']],['3주','고객 한 명 맞춤대화',['추천 고객 1명 맞춤대화','요약 리포트 내 카톡으로 먼저','당월 영업 타겟 전원 접촉']],['4주','성과 공유와 뽐내기',['활용일수·가계약 변화 공유','우수 사례 3건 조회에서 발표','다음 달 타겟 그룹 미리 보기']]];
    wk.forEach((w,i)=>{ const x=M+i*3.08,cw=2.9,y=1.85,h=3.8; L.R(s,{x,y,w:cw,h,fill: i===1? C.blue : C.white,line: i===1? null : C.g200,radius:0.14,shadow:i!==1}); const fg=i===1?'FFFFFF':C.navy; L.T(s,w[0],{x:x+0.25,y:y+0.22,w:cw-0.5,h:0.3,fontSize:11,bold:true,color:i===1?'FFFFFF':C.blue,transparency:i===1?20:0}); L.T(s,w[1],{x:x+0.25,y:y+0.55,w:cw-0.5,h:0.5,fontSize:15,bold:true,color:fg,valign:'middle'}); w[2].forEach((t,k)=>{ L.T(s,'✓',{x:x+0.25,y:y+1.35+k*0.8,w:0.3,h:0.4,fontSize:12.5,bold:true,color:i===1?'FFFFFF':C.blue,lineSpacingMultiple:1.3}); L.T(s,t,{x:x+0.55,y:y+1.35+k*0.8,w:cw-0.75,h:0.7,fontSize:12.5,color:i===1?'FFFFFF':C.g700,lineSpacingMultiple:1.3}); }); if(i<3) L.arrow(s,{x:x+cw-0.08,y:y+1.6,w:0.35,color: C.g300}); });
    L.note(s,{x:M,y:5.95,w:W-2*M,h:0.85,label:'',text:'본질은 그대로, 바뀌는 건 도구뿐. 정착은 관리자님이 만들어 주세요.',tone:'dark',size:13});
  }});
};
