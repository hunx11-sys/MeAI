module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  const SRC = '출처: 데이터분석팀 「MeAI 사용 실태 분석」·「MeAI 효과 분석」, 2026.08';
  S.push({ part:'08', fn:(pres,no)=> L.divider(pres,{num:'08',title:'영업관리자 편\n대문을 조회 자료로',sub:'본부장님이 전파하고, 조직장님이 정착시킵니다. 대문이 열리면 조회 자료는 따로 만들 필요가 없어요.',learn:['도구는 손에, 정착은 조직이 · 누구부터 챙길까','대문 숫자 4개와 당월 영업 타겟 그룹을 조회 자료로 쓰는 법','이번 달 체크리스트 · 조회 스크립트 · 4주 도입 플랜'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 왜 관리자인가',title:'도구는 이미 손에 있어요. 정착은 조직이 만듭니다',sub:'개인이 알아서 쓰게 두면 절반이 사라지고, 본부가 함께 시작하면 셋 중 둘이 남았어요.',pageNo:no});
    [['4,912명','과거엔 썼는데 이번 달은 한 번도 안 쓴 분','권한 부여자의 40.8%. 새로 가르칠 필요 없이 "다시 켜기"만 하면 되는 분들이에요. 대문이 그 "다시 켜기" 버튼이에요.',C.red],['65.2%','본부 단위로 시작한 분들의 7개월 잔존','개별로 들어온 분은 35~41%만 남았어요. 날짜를 정해 같이 시작하는 것이 두 배 가까이 더 남겨요.',C.blue],['26.9%','권한 받은 뒤 30일 안에 첫 사용','첫 사용까지 짧을수록 정착률이 높았어요. 권한 부여 첫 주가 관리자의 골든타임이에요.',C.green]].forEach((d,i)=> L.stat(s,{x:M+i*4.1,y:1.95,w:3.9,h:2.2,value:d[0],label:d[1],desc:d[2],accent:d[3]}));
    L.note(s,{x:M,y:4.4,w:W-2*M,h:1.1,label:'대화의 시작',text:'"도입이 안 됐다"가 아니라 "이미 다 써봤다"에서 시작하세요. 사용률은 연차·직책과 무관했고, 효과는 기존 FP에서 더 컸어요(12차월 초과 3.9배). 10월부터는 "대문 열어보셨어요?" 한 마디면 충분해요.',tone:'dark',size:11});
    L.caption(s,{x:M,y:5.7,w:W-2*M,text:SRC,align:'left'});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 대문을 조회 자료로',title:'10월부터 MeAI 대문이 조회 자료가 됩니다',sub:'관리자가 따로 리스트를 뽑지 않아도, 대문 숫자와 고객찾기 그룹이 그날의 영업 방향을 보여줘요.',pageNo:no});
    L.img(s,HERO('gate_stats'),{x:M,y:1.85,w:7.4,h:1.35,valign:'top',align:'left'}); L.caption(s,{x:M,y:3.2,w:7.4,text:'조회 첫 화면 · 팀원의 숫자 4개'});
    L.img(s,HERO('find_groups_both'),{x:M,y:3.55,w:2.6,h:3.15,valign:'top',align:'left'}); L.caption(s,{x:M,y:6.72,w:2.6,text:'고객 그룹 · 보장 기준 / 영업 기회',size:8.5});
    L.img(s,HERO('find_header'),{x:M+2.75,y:3.55,w:4.65,h:1.2,valign:'top',align:'left'}); L.caption(s,{x:M+2.75,y:4.75,w:4.65,text:'그룹 제목 · 인원 · 설명 문구',align:'left'});
    L.note(s,{x:M+2.75,y:5.1,w:4.65,h:1.2,label:'조회에서 읽는 순서',text:'① 숫자 4개 → "동의 필요"가 늘었나 ② 당월 영업 타겟 그룹 인원과 설명 ③ 이번 주 상령일·생일 임박 ④ 추천 카드 1장 같이 읽기',tone:'blue',size:10});
    L.numList(s,{x:8.4,y:1.85,w:4.3,gap:0.1,titleSize:11.5,descSize:9.8,items:[{n:1,title:'숫자 4개',desc:'"사전조회 동의 필요"가 곧 이번 주 동의를 받아야 할 목표 인원. "맞춤대화 가능"이 이번 주 상담 가능 인원.'},{n:2,title:'당월 영업 타겟 그룹',desc:'우선순위 1. 이달 캠페인 대상이에요. 그룹 인원과 이유 문장을 함께 읽어요.'},{n:3,title:'상령일 · 생일 임박',desc:'날짜형 그룹은 주간 접촉 계획표로 그대로. "이번 주 상령일 고객 몇 명?"'},{n:4,title:'사전동의 만료',desc:'D-n 짧은 순으로 팀원과 대응 순서를 정해요. 동의 없이는 맞춤대화가 안 열려요.'},{n:5,title:'게시판',desc:'운영 이슈(응답 지연·결과 누락)는 조회에서 먼저 공유해 혼선을 줄여요.'}]});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 누구부터 챙길까',title:'타겟은 속성이 아니라 사용 이력으로 잡으세요',sub:'"신인들이 안 쓴다", "팀원은 안 쓰고 관리자만 쓴다"는 데이터와 달랐어요. 이력이 말해주는 네 그룹부터.',pageNo:no});
    [['4,912명','이탈','과거엔 썼는데 이번 달 한 번도 안 쓴 분','"대문 한 번 열어 보세요" 한 마디. 새 교육이 필요 없는 가장 효율 높은 그룹.',C.red],['3.9배','기존 FP','12차월 초과, 아직 미활용','효과가 가장 큰 층(10.0% → 38.6%). 신인용 도구라는 선입견을 깨주세요.',C.blue],['2,156명','단발','"보장분석 해줘" 하나만 쓰는 분','꼬리질문 버튼과 고객찾기 추천 질문을 알려주세요. 질문 하나 더에 가계약 11.99 → 17.02건.',C.purple],['30일','신규 승인','권한 받은 지 30일 안 된 분','첫 사용이 정착을 가르고, 첫 7일이 골든타임이에요. 본부장님이 직접 안내해 주세요.',C.green]].forEach((d,i)=>{ const x=M+i*3.08,w=2.9,y=1.95,h=3.3; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.chip(s,{x:x+0.25,y:y+0.25,text:d[1],fill:C.g100,color:d[4]}); L.T(s,d[0],{x:x+0.25,y:y+0.65,w:w-0.5,h:0.55,fontSize:24,bold:true,color:d[4],valign:'middle'}); L.T(s,d[2],{x:x+0.25,y:y+1.25,w:w-0.5,h:0.6,fontSize:11.5,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15}); L.T(s,d[3],{x:x+0.25,y:y+1.9,w:w-0.5,h:1.7,fontSize:10,color:C.g600,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:5.5,w:W-2*M,h:0.75,label:'',text:'데이터로 보면 "신인이 안 쓴다"는 오해예요. 6차월 미만도 52.6%가 사용했고, 팀원과 관리자의 활용률 차이는 1.3배에 그쳤어요.',tone:'grey',size:10.5});
    L.caption(s,{x:M,y:6.4,w:W-2*M,text:SRC,align:'left'});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 이번 달 체크리스트',title:'이번 달, 여덟 줄만 부탁드립니다',sub:'위 두 줄이 데이터가 말하는 최우선이에요. 나머지는 여유가 될 때.',pageNo:no});
    const items=[['한동안 안 쓰신 분께 "대문 한 번 열어 보세요"','과거엔 썼는데 이번 달 안 쓴 4,912명. 새 교육 없이 다시 켜기만 하면 돼요','최우선',C.red],['기존 FP(12차월 초과)를 먼저 챙겨 주세요','전환율 격차가 3.9배로 가장 크게 나는 층이에요','최우선',C.red],['권한부여가 안 된 분을 찾아 주세요','대문은 권한이 있어야 열려요','온보딩',C.blue],['권한 받은 분께 본부장님이 직접 안내해 주세요','30일이 지나면 정착이 어려워요. 첫 사용이 정착을 갈라요','온보딩',C.blue],['조회에서 MeAI 대문을 함께 열어 주세요','숫자 4개와 당월 영업 타겟 그룹, 추천 카드 1장을 팀과 공유해요','조회',C.blue],['"질문 하나만 더"를 안내해 주세요','꼬리질문 버튼과 고객찾기 추천 질문. 성과가 2.3배 달라져요','확장',C.purple],['본부 단위로 날짜를 정해 같이 시작해 주세요','개별 독려보다 잔존율이 두 배 가까이 높아요','정착',C.green],['도입 설명회에 MeAI 대문을 보여 주세요','"오늘 만날 고객을 회사가 찾아 준다"는 타사가 못 내미는 한 마디예요','리크루팅',C.g700]];
    items.forEach((it,i)=>{ const y=1.9+i*0.62; L.R(s,{x:M,y,w:W-2*M,h:0.55,fill:C.white,line:C.g200,radius:0.1,shadow:false}); L.T(s,'✓',{x:M+0.2,y,w:0.4,h:0.55,fontSize:13,bold:true,color:it[3],valign:'middle'}); L.T(s,it[0],{x:M+0.7,y,w:5.4,h:0.55,fontSize:11.5,bold:true,color:C.navy,valign:'middle'}); L.T(s,it[1],{x:M+6.2,y,w:4.7,h:0.55,fontSize:9.8,color:C.g600,valign:'middle'}); L.chip(s,{x:W-M-1.25,y:y+0.135,text:it[2],fill: it[3]===C.red? C.red50 : it[3]===C.blue? C.blue50 : it[3]===C.purple? C.purple50 : it[3]===C.green? C.green50 : C.g100,color:it[3]}); });
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 조회에서 말씀해 보세요',title:'길게 설명하지 않아도 돼요. 세 문장이면 충분해요',sub:'숫자로 한 줄, 타깃으로 한 줄, 행동으로 한 줄. 그리고 현장 반론 셋에 대한 답을 준비해 두세요.',pageNo:no});
    const lines=[['숫자로','"같은 FP 안에서 비교해도 체결전환율이 9%에서 36%로 올라갑니다."','가장 강한 한 줄이에요. "같은 FP 비교"라는 조건을 꼭 함께 말씀해 주세요.'],['타깃으로','"우리 본부에서 다시 권한부여 받을 분, 그리고 한동안 안 쓰신 분 계실까요?"','다음 행동을 바로 만들어 드리는 질문이에요.'],['행동으로','"10월부터 MeAI 대문이 열립니다. 추천 고객은 CRM 데이터가 들어오는 대로 보이고요. 조회 때 함께 열어보겠습니다."','대문 오픈을 조회 습관과 연결하는 한 줄이에요.']];
    lines.forEach((l,i)=>{ const y=1.9+i*1.45; L.R(s,{x:M,y,w:7.3,h:1.3,fill: i===2? C.blue : C.white,line: i===2? null : C.g200,radius:0.14,shadow:i!==2}); L.chip(s,{x:M+0.25,y:y+0.2,text:l[0],fill: i===2?'2B6FE0':C.blue50,color: i===2?'FFFFFF':C.blue}); L.T(s,l[1],{x:M+0.25,y:y+0.5,w:6.8,h:0.42,fontSize:11.5,bold:true,color: i===2?'FFFFFF':C.navy,valign:'middle'}); L.T(s,l[2],{x:M+0.25,y:y+0.9,w:6.8,h:0.35,fontSize:9.5,color: i===2?'FFFFFF':C.g600,valign:'middle'}); });
    L.R(s,{x:8.2,y:1.9,w:4.5,h:4.2,fill:C.g50,line:C.g200,radius:0.14});
    L.T(s,'현장 반론 3가지, 정확하게 답하기',{x:8.45,y:2.05,w:4.0,h:0.35,fontSize:12,bold:true,color:C.navy});
    [['Q. 원래 될 고객이라 켠 것 아닌가요?','같은 FP 관리 고객끼리 비교해도 9.0% → 36.0%. PART 1의 숫자를 그대로 보여주세요.'],['Q. 계약이 더 빨라지나요?','속도는 큰 차이 없어요(12일 vs 13일). "빨라진다"가 아니라 "성사된다"로.'],['Q. 신인용 도구 아닌가요?','12차월 초과 기존 FP에서 격차가 더 커요(10.0% → 38.6%). 경력자부터 권해도 되는 근거예요.']].forEach((q,i)=>{ const y=2.5+i*1.2; L.T(s,q[0],{x:8.45,y,w:4.0,h:0.3,fontSize:10.5,bold:true,color:C.blue}); L.T(s,q[1],{x:8.45,y:y+0.3,w:4.0,h:0.85,fontSize:9.8,color:C.g700,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:6.3,w:W-2*M,h:0.5,label:'',text:'과장하지 않는 것이 신뢰를 만들어요. "빨라진다"·"많이 판다"가 아니라 "성사된다"·"좋은 상품을 고른다"가 데이터가 지지하는 표현이에요.',tone:'grey',size:10});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 4주 도입 플랜',title:'조직 단위 4주 플랜, 이 순서면 정착합니다',sub:'본부 단위로 같은 날 시작하는 것이 핵심이에요. 주차별로 한 가지씩만.',pageNo:no});
    const wk=[['1주','권한 점검 + 대문 소개',['권한 미부여·이탈 명단 확인','조회에서 PART 1 핵심 숫자 3개 공유','대문 화면(PART 2) 함께 열어 보기']],['2주','5일 미션 전원 시작',['PART 7 첫 5일 미션 시작','추천 카드 1장 → 고객찾기 열어 보기','본부장님의 한마디 "대문 열어보셨어요?"']],['3주','고객 한 명 맞춤대화',['추천 고객 1명 → 맞춤대화 → 보장분석','요약 리포트 1건 내 카톡으로 먼저','당월 영업 타겟 그룹 전원 접촉']],['4주','성과 공유와 뽐내기',['활용일수·가계약 변화 공유','우수 사례 3건 조회에서 발표','다음 달 당월 영업 타겟 그룹 미리 보기']]];
    wk.forEach((w,i)=>{ const x=M+i*3.08,cw=2.9,y=1.9,h=3.9; L.R(s,{x,y,w:cw,h,fill: i===1? C.blue : C.white,line: i===1? null : C.g200,radius:0.14,shadow:i!==1}); const fg=i===1?'FFFFFF':C.navy; L.T(s,w[0],{x:x+0.25,y:y+0.2,w:cw-0.5,h:0.3,fontSize:10,bold:true,color:i===1?'FFFFFF':C.blue,transparency:i===1?20:0}); L.T(s,w[1],{x:x+0.25,y:y+0.5,w:cw-0.5,h:0.5,fontSize:14,bold:true,color:fg,valign:'middle'}); w[2].forEach((t,k)=>{ L.T(s,'✓',{x:x+0.25,y:y+1.2+k*0.85,w:0.3,h:0.3,fontSize:11,bold:true,color:i===1?'FFFFFF':C.blue}); L.T(s,t,{x:x+0.55,y:y+1.2+k*0.85,w:cw-0.75,h:0.8,fontSize:10.2,color:i===1?'FFFFFF':C.g700,lineSpacingMultiple:1.3}); }); if(i<3) L.arrow(s,{x:x+cw-0.08,y:y+1.6,w:0.35,color: C.g300}); });
    L.note(s,{x:M,y:6.05,w:W-2*M,h:0.75,label:'',text:'본질은 그대로, 바뀌는 건 도구뿐이에요. MeAI가 지식을 채우고, 대문이 고객을 찾고, 관리자님이 정착을 만들어 주세요.',tone:'dark',size:11});
  }});
};
