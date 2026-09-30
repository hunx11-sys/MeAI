module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  S.push({ part:'09', fn:(pres,no)=> L.divider(pres,{num:'09',title:'지켜야 할 것 · FAQ\n용어 정리',sub:'오래 잘 쓰는 조건, 한 번만 제대로 읽어 두세요.',learn:['다섯 가지 약속','자주 묻는 질문','용어 한 장 정리'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · 꼭 지켜주세요',title:'오래 잘 쓰는 다섯 가지 약속',sub:'1·4번은 화면 하단 안내문에도 나와요.',pageNo:no});
    const items=[['1','답변은 검증 후 사용','오류가 있을 수 있어요. 약관·증권으로 직접 확인한 뒤 안내해요.',C.blue],['2','개인정보 입력 금지','이름·연락처·주소·주민번호는 질문에도, 메모에도 넣지 않아요.',C.blue],['3','동의 없으면 보지 않기','동의가 없거나 철회된 고객은 막혀요. 우회하지 말고 동의부터 받아요.',C.blue],['4','미검증 책임은 사용자에게','검증 없이 안내하면 금융소비자보호법 등 법령상 책임은 사용자에게 있어요.',C.blue],['5','자료 외부 반출 금지','MeAI 답변·화면 캡처·이 가이드북,\n외부 제공·배포·게시는 금지예요.',C.blue]];
    items.forEach((it,i)=>{ const col=i%3,row=Math.floor(i/3); const x=M+col*4.1,y=1.85+row*2.42,w=3.9,h=2.25; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.badge(s,{x:x+0.28,y:y+0.3,n:it[0],d:0.44,color:it[3]}); L.T(s,it[1],{x:x+0.88,y:y+0.28,w:w-1.1,h:0.48,fontSize:15,bold:true,color:C.navy,valign:'middle'}); L.T(s,it[2],{x:x+0.28,y:y+1.0,w:w-0.56,h:1.1,fontSize:13,color:C.g600,lineSpacingMultiple:1.35}); });
    L.note(s,{x:M+8.2,y:4.27,w:3.9,h:2.25,label:'화면 하단 안내문 원문',text:'"MeAI의 답변은 생성형 AI를 통해 작성되어 오류가 있을 수 있으므로, 반드시 직접 근거자료를 확인하여 진위를 검증하시기 바랍니다. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다."',tone:'dark',size:11});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · FAQ',title:'처음에 가장 많이 묻는 질문',sub:'이 아홉 개면 첫 주 질문은 대부분 해결돼요.',pageNo:no});
    const qa=[['MeAI 홈은 어디서 열어요?','10월부터 PC 영업포탈에서 MeAI로 들어오면 먼저 열려요(모바일은 순차 적용). 어느 화면이든 왼쪽 위 [MeAI 홈]을 누르면 돌아와요.'],['추천 고객이 안 보여요','오늘의 추천 고객은 CRM 데이터 반입이 끝난 뒤부터 보여요(게시판 공지). 추천은 매일 새로 계산돼 다음 날 반영돼요.'],['추천 고객이\n오늘 연락할 분이 아닌 것 같아요','추천은 지시가 아니라 "이유가 있는 고객"이에요. 고객 그룹에서 직접 골라도 돼요.'],['동의 없는 고객은요?','[고객 동의]나 [사전조회동의 요청하기]를 눌러 번호를 넣으면 알림톡이 가요. 반영까지 약 15분 걸려요.'],['검색 팝업에 고객이 없어요 · 회색이에요','고객 검색 팝업엔 동의가 유효한 고객만 나와요. 회색은 오늘 동의를 철회한 고객이에요.'],['숫자가 내 고객 수와 달라요','MeAI 홈에는 사전조회 동의일로부터 1년 이내 고객만 보여요(범례 안내). 다음 날 반영돼요.'],['한 고객이 여러 그룹에 있어요','정상이에요. 우선순위는 당월 영업 타겟 →\n증권 5건 이상·월 50만원 이상·상령일·\n생일·동의 만료 → 보장 부족 순이에요.'],['PC 대화를 폰에서 이어가나요?','네. 대화 이력과 나의 질문이 PC·모바일에 똑같이 보여요.'],['글씨가 너무 커요 · 작아요','오른쪽 위 [글씨 확대]를 끄면 원래 크기, 켜면 한 단계 커요(기본 ON).']];
    qa.forEach((q,i)=>{ const col=i%3,row=Math.floor(i/3); const x=M+col*4.1,y=1.85+row*1.72,w=3.9,h=1.58; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.12,shadow:false}); const ql = q[0].split('\n').length, ay = y+0.6+(ql-1)*0.26; /* 두 줄 질문은 답을 한 줄만큼 내림. Q·A 글자는 본문과 같은 크기·줄간격으로 첫 줄 높이를 맞춘다 */ L.T(s,'Q',{x:x+0.22,y:y+0.17,w:0.3,h:0.34,fontSize:13,bold:true,color:C.blue,valign:'top',lineSpacingMultiple:1.1}); L.T(s,q[0],{x:x+0.55,y:y+0.17,w:w-0.72,h:0.34+(ql-1)*0.26,fontSize:13,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.1}); L.T(s,'A',{x:x+0.22,y:ay,w:0.3,h:0.3,fontSize:11.5,bold:true,color:C.g400,lineSpacingMultiple:1.3}); L.T(s,q[1],{x:x+0.55,y:ay,w:w-0.72,h:y+h-ay-0.08,fontSize:11.5,color:C.g700,lineSpacingMultiple:1.3}); });
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · 용어 정리',title:'이 책에 나온 말, 한 장 정리',sub:'MeAI 화면에 그대로 쓰이는 이름이에요.',pageNo:no});
    const rows=[['용어','뜻','어디서 보나'],['MeAI 홈','MeAI에 들어오면 처음 열리는 화면. 추천 고객·고객 그룹·대화 카드가 한곳에 있어요.','MeAI 첫 화면 · 어느 화면이든 왼쪽 위 [MeAI 홈]'],['일반대화 · 맞춤대화','일반대화는 무엇이든 묻는 창. 맞춤대화는 고객 한 명의 보장 내역으로 답해요.','MeAI 홈 대화 카드(흰색 · 검은색) · 고객찾기'],['사전조회 동의','보장 내역 조회 동의. 1년 유효, 있어야 맞춤대화가 열려요.','카드 D-n 칩 · MeAI 홈 "사전조회 동의 필요"'],['사전조회동의 D-n','만료까지 남은 날. 만료되면 "필요", 철회하면 "철회".','MeAI 홈 카드 · 검색 팝업 · 고객찾기'],['상품소개 동의 · AI 추천 고객','상품 소개에 동의한 고객. 카드에 빨간 리본이 붙어요.','MeAI 홈 "상품제안 가능" · 카드 리본'],['보유 · 가망 · 이관','계약 있음 · 등록만 · 넘겨받음. 고객마다 셋 중 하나예요.','카드의 유형 칩'],['오늘의 추천 고객','이유가 붙은 카드 3장 × 세트 3개. 매일 새로 계산돼요.','MeAI 홈 가운데'],['보장 기준 · 영업 기회','고객 그룹 탭. 보장 부족 7종 등 10개 / 날짜형 3개.','고객찾기 왼쪽'],['당월 영업 타겟','이번 달 영업 목표 대상. 우선순위 1(보라 태그).','고객찾기 그룹 · 카드 태그'],['상령일','보험 나이가 한 살 오르는 날. 그 전 가입이 유리해요.','고객찾기 [상령일 임박]'],['이 고객 한눈에 보기','펼친 카드의 여섯 칸. 가입·납입·부족 금액 등.','고객찾기 가운데'],['간편 분석 · 상세 분석 (개발 중)','답변 모드. 일상 언어 / 약관·담보 정밀 비교.','대화 입력창 아래 (NEW)'],['용어 설명 (개발 중)','답변 속 전문용어의 뜻을 목록으로 보여줘요.','PC 입력창 오른쪽 위 · 모바일 오른쪽 아래 (NEW)'],['글씨 확대','작은 글씨를 한 단계 크게. 기본 ON, 이 PC에 기억돼요.','MeAI 홈·고객찾기·게시판 오른쪽 위']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?11:11, bold: ri===0||ci===0, color: ri===0? C.g600 : (ci===0? C.navy : C.g800), fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[3,8,3,8]}})));
    s.addTable(data,{x:M,y:1.85,w:W-2*M,colW:[2.9,5.4,3.83],rowH:0.32,border:{type:'solid',color:C.g200,pt:0.75}});
  }});
  // 마무리
  S.push({ fn:(pres,no)=>{
    const s = pres.addSlide(); s.background={color:C.blue};
    L.T(s,'MeAI',{x:W-6.5,y:1.2,w:5.9,h:2.4,fontSize:120,bold:true,color:'FFFFFF',transparency:82,align:'right'});
    // 방송판 마무리와 같은 틀: 위에 '마무리' + 네 걸음 칩(어느 것도 켜지 않음)
    L.T(s,'마무리',{x:M+0.2,y:0.55,w:4,h:0.34,fontSize:13,bold:true,color:C.blue100,valign:'middle'});
    let sx = M+0.2; ['1 찾기','2 고르기','3 묻기','4 터치하기'].forEach(t=>{ sx += L.chip(s,{x:sx,y:0.98,text:t,fill:C.blue700,color:'FFFFFF',size:12,h:0.38})+0.12; });
    L.T(s,'오늘 만날 고객은,\nMeAI 홈에 있어요',{x:M+0.2,y:1.65,w:9,h:2.2,fontSize:44,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.15});
    L.T(s,'찾는 일은 MeAI가, 만나는 일은 여러분이.',{x:M+0.2,y:3.95,w:9,h:0.6,fontSize:20,color:'FFFFFF',transparency:5,valign:'middle'});
    const cw = L.chip(s,{x:M+0.2,y:5.0,text:'매일 아침 MeAI 홈 · 오늘 한 분께 터치',fill:C.blue700,color:'FFFFFF',size:12,h:0.4});
    L.chip(s,{x:M+0.2+cw+0.15,y:5.0,text:'문의 · 세일즈혁신TF',fill:C.blue700,color:'FFFFFF',size:12,h:0.4});
    L.T(s,'MeAI 홈을 만든 분들 · AI추진파트 문현우님 · 이경복님',{x:M+0.2,y:5.62,w:9,h:0.32,fontSize:12,color:'FFFFFF',transparency:20,valign:'middle'});
    L.T(s,'본 자료의 전부·일부(수정 포함)의 외부 제공·배포·게시(온/오프라인)는 금지됩니다. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다. 화면 속 고객 이름·숫자는 예시 데이터입니다.',{x:M+0.2,y:6.3,w:W-2*M-0.2,h:0.5,fontSize:9.5,color:'FFFFFF',transparency:5,lineSpacingMultiple:1.3});
    L.T(s,'MeAI 활용 가이드북 v4 · MeAI 홈 편 · 2026.10',{x:M,y:H-0.42,w:8,h:0.25,fontSize:9,color:'FFFFFF',transparency:15}); L.T(s,String(no),{x:W-M-1,y:H-0.42,w:1,h:0.25,fontSize:9,color:'FFFFFF',align:'right'});
  }});
};
