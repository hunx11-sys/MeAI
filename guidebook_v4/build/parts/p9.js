module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  S.push({ part:'09', fn:(pres,no)=> L.divider(pres,{num:'09',title:'지켜야 할 것 · FAQ\n용어 정리',sub:'오래 잘 쓰는 조건이에요. 한 번만 제대로 읽어 두세요.',learn:['다섯 가지 약속','대문·고객찾기에서 자주 묻는 질문','이 책에 나온 용어 한 장 정리'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · 꼭 지켜주세요',title:'다섯 가지 약속, MeAI를 오래 잘 쓰는 조건이에요',sub:'화면 하단 안내문에도 나오는 내용이에요. 대문이 생겨도 약속은 같아요.',pageNo:no});
    const items=[['1','답변은 반드시 검증 후 사용','MeAI 답변은 생성형 AI가 작성해 오류가 있을 수 있어요. 근거자료(약관·증권)를 직접 확인한 뒤 고객에게 안내해요.',C.blue],['2','개인정보 입력 금지','이름·연락처·주소·주민번호는 질문에도, 메모에도 넣지 않아요. 고객찾기 추천 질문도 "고객 성명·연락처는 넣지 말 것"이라고 적혀 있어요.',C.blue],['3','동의 없는 고객 정보는 보지 않아요','사전조회 동의가 없거나 철회된 고객은 정보 확인이 막혀요. 우회하지 말고 동의부터 받아요.',C.blue],['4','미검증 책임은 사용자에게','검증 없이 안내해 생긴 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있어요.',C.blue],['5','자료 외부 반출 금지','MeAI 답변, 화면 캡처, 이 가이드북을 포함한 교육자료의 외부 제공·배포·게시(온/오프라인)는 금지돼요.',C.blue]];
    items.forEach((it,i)=>{ const col=i%3,row=Math.floor(i/3); const x=M+col*4.1,y=1.9+row*2.05,w=3.9,h=1.9; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.badge(s,{x:x+0.25,y:y+0.25,n:it[0],d:0.4,color:it[3]}); L.T(s,it[1],{x:x+0.8,y:y+0.22,w:w-1.0,h:0.45,fontSize:12.5,bold:true,color:C.navy,valign:'middle'}); L.T(s,it[2],{x:x+0.25,y:y+0.85,w:w-0.5,h:h-1.0,fontSize:10,color:C.g600,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M+8.2,y:3.95,w:3.93,h:1.9,label:'화면 하단 안내문 원문',text:'"MeAI의 답변은 생성형 AI를 통해 작성되어 오류가 있을 수 있으므로, 반드시 직접 근거자료를 확인하여 진위를 검증하시기 바랍니다. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다."',tone:'dark',size:9.5});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · FAQ',title:'대문과 고객찾기, 처음 쓰는 분들이 가장 많이 묻는 질문',sub:'이 여덟 개면 첫 주 질문의 대부분이 해결돼요.',pageNo:no});
    const qa=[['MeAI 대문은 어디서 열어요?','PC 영업포탈에서 MeAI로 들어오면 대문이 먼저 열려요(10월 오픈). 모바일 대문은 순차 적용 예정이라 우선 앱 홈 → 보장분석 → MeAI로 쓰세요.'],['추천 고객이 안 보여요','게시판 공지 기준, 오늘의 추천 고객은 CRM 데이터 반입이 끝나는 2차 오픈부터 보여요. 데이터는 매일 계산돼 익일 반영돼요.'],['카드의 고객이 오늘 연락할 사람이 아니에요','추천은 "이유가 있는 고객"이지 지시가 아니에요. 세트 3개(9장)를 넘겨 보고 고객찾기 그룹에서 직접 골라도 돼요.'],['동의가 없는 고객은 어떻게 하나요?','고객찾기 오른쪽 패널의 [사전조회동의 요청하기]나 대문 [고객 동의]에서 휴대폰 번호를 넣고 [보내기]. 고객에게 동의 요청 알림톡이 가고, 동의하면 약 15분 내외로 반영돼요.'],['팝업에 고객이 없어요 · 회색이에요','팝업에는 사전조회 동의가 유효한 고객만 나와요(검색은 고객 이름·담당자 이름 모두). 회색은 오늘 동의를 철회한 고객이라 눌러도 열리지 않아요.'],['숫자가 내 고객 수와 달라요','대문에 보이는 고객은 사전조회 동의일로부터 1년 이내 고객이에요. 화면의 "최근 업데이트" 시각 기준이고, 익일 반영이에요.'],['한 고객이 여러 그룹에 있어요','정상이에요. 태그 칩은 우선순위 순으로 보여요. 당월 영업 타겟(1) → 증권 5건 이상·월 50만원 이상·상령일·생일·사전동의 만료(2) → 보장 부족 7종(3).'],['PC에서 시작한 대화를 폰에서 이어갈 수 있나요?','네. 대화 이력과 저장한 나의 질문은 PC·모바일에서 똑같이 보여요.']];
    qa.forEach((q,i)=>{ const col=i%2,row=Math.floor(i/2); const x=M+col*6.2,y=1.85+row*1.22,w=5.95,h=1.1; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.12,shadow:false}); L.T(s,'Q',{x:x+0.2,y:y+0.1,w:0.3,h:0.3,fontSize:11,bold:true,color:C.blue}); L.T(s,q[0],{x:x+0.5,y:y+0.1,w:w-0.7,h:0.3,fontSize:11,bold:true,color:C.navy,valign:'middle'}); L.T(s,'A',{x:x+0.2,y:y+0.42,w:0.3,h:0.3,fontSize:11,bold:true,color:C.g400}); L.T(s,q[1],{x:x+0.5,y:y+0.42,w:w-0.7,h:0.65,fontSize:9.5,color:C.g700,lineSpacingMultiple:1.25}); });
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · 용어 정리',title:'이 책에 나온 말, 한 장으로 정리했어요',sub:'대문·고객찾기 화면에 그대로 쓰이는 이름이에요.',pageNo:no});
    const rows=[['용어','뜻','어디서 보나'],['사전조회 동의','고객의 보장 내역을 조회해도 된다는 동의. 동의일로부터 1년 유효. 있어야 맞춤대화가 열려요.','카드의 D-n 칩 · 대문 숫자 "사전조회 동의 필요"'],['사전조회동의 D-n','동의 만료까지 남은 날. 만료되면 "필요", 고객이 철회하면 "철회".','대문 카드 · 검색 팝업 · 고객찾기'],['상품소개 동의 · AI 추천 고객','상품 소개에 동의한 고객. 상품 제안이 가능해 카드에 빨간 리본이 붙어요.','대문 숫자 "상품제안 가능" · 카드 리본'],['보유 · 가망 · 이관','계약이 있는 고객 · 등록만 된 고객 · 넘겨받은 고객. 한 고객은 하나로만 분류.','카드의 유형 칩'],['오늘의 추천 고객','이유가 붙은 고객 카드 3장 × 세트 3개. 매일 새로 계산.','대문 가운데'],['고객 그룹 · 보장 기준 / 영업 기회','담보 부족 7종 + 당월 영업 타겟 · 증권 5건 이상 · 월 50만원 이상 / 상령일·생일·사전동의 만료 같은 시점 그룹.','고객찾기 왼쪽'],['당월 영업 타겟','이번 달 영업 목표 대상 그룹. 우선순위 1(보라 태그).','고객찾기 그룹 · 카드 태그'],['상령일','보험 나이가 한 살 오르는 날. 그 전에 가입하면 보험료가 유리해요.','고객찾기 [상령일 임박] 그룹'],['이 고객 한눈에 보기','펼친 카드의 여섯 칸. 가입·납입·접촉기회·부족 금액·주요 담보.','고객찾기 가운데'],['간편 분석 · 상세 분석','질문마다 고르는 답변 모드. 일상 언어 / 약관·담보 정밀 비교.','대화 입력창 아래 (NEW)'],['용어 설명','답변 속 전문용어에 표시를 붙이고 뜻을 목록으로 보여주는 기능.','PC 입력창 오른쪽 위 · 모바일 오른쪽 아래 (NEW)']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?10:9.8, bold: ri===0||ci===0, color: ri===0? C.g600 : (ci===0? C.navy : C.g800), fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[3,8,3,8]}})));
    s.addTable(data,{x:M,y:1.85,w:W-2*M,colW:[2.6,6.2,3.33],rowH:0.4,border:{type:'solid',color:C.g200,pt:0.75}});
  }});
  // 마무리
  S.push({ fn:(pres,no)=>{
    const s = pres.addSlide(); s.background={color:C.blue};
    L.T(s,'MeAI',{x:W-6.5,y:1.2,w:5.9,h:2.4,fontSize:120,bold:true,color:'FFFFFF',transparency:82,align:'right'});
    L.T(s,'오늘 만날 고객은,\n대문에 있어요',{x:M+0.2,y:1.6,w:9,h:2.2,fontSize:40,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.15});
    L.T(s,'찾는 일은 MeAI가, 만나는 일은 여러분이.\n지식은 MeAI가 채우고, 대문이 고객을 찾아줘요.\n여러분은 고객을 향한 마음만 가져오면 됩니다.',{x:M+0.2,y:4.0,w:9,h:1.4,fontSize:15,color:'FFFFFF',transparency:10,lineSpacingMultiple:1.4});
    L.chip(s,{x:M+0.2,y:5.7,text:'10월, MeAI 대문에서 만나요',fill:'2B6FE0',color:'FFFFFF',size:11,h:0.36});
    L.chip(s,{x:M+3.2,y:5.7,text:'문의 · 세일즈혁신TF',fill:'2B6FE0',color:'FFFFFF',size:11,h:0.36});
    L.T(s,'본 자료의 전부·일부(수정 포함)의 외부 제공·배포·게시(온/오프라인)는 금지됩니다. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다. 화면 속 고객 이름·숫자는 예시 데이터입니다.',{x:M+0.2,y:6.3,w:W-2*M,h:0.5,fontSize:9.5,color:'FFFFFF',transparency:5,lineSpacingMultiple:1.3});
    L.T(s,'MeAI 활용 가이드북 v4 · CRM 대문 편 · 2026.10',{x:M,y:H-0.42,w:8,h:0.25,fontSize:9,color:'FFFFFF',transparency:15}); L.T(s,String(no),{x:W-M-1,y:H-0.42,w:1,h:0.25,fontSize:9,color:'FFFFFF',align:'right'});
  }});
};
