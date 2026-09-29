module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  // 표지
  S.push({ fn:(pres,no)=> L.cover(pres,{ title:'MeAI\n활용 가이드북', sub:'찾는 영업에서,\n찾아가는 영업으로', line3:'오늘 만날 고객을 MeAI 대문이 먼저 추천하고, 첫 마디와 다음 행동까지 준비해 둡니다.\n영업가족 편 + 관리자 편', meta:['v4 · CRM 대문 편','2026.10 오픈 화면 기준','2026.09.29 확정 화면'], file:HERO('gate_full'), pageNo:no }) });
  // 이렇게 보세요
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'HOW TO USE',title:'이 가이드북, 이렇게 보세요',sub:'영업가족과 영업관리자가 함께 보는 책이에요. 이번 판은 10월에 열리는 MeAI 대문(CRM)을 중심으로 다시 썼어요.',pageNo:no});
    const items = [
      ['1','MeAI 대문이 처음이라면','PART 1 · 2','왜 영업의 방향이 바뀌는지, 대문 화면이 어떻게 생겼는지부터. 카드 한 장 읽는 법만 알면 절반은 끝이에요.'],
      ['2','오늘 바로 써보고 싶다면','PART 3 · 4 · 7','추천 카드에서 맞춤대화까지 클릭 두 번. 고객찾기 그룹으로 이번 달 연락할 사람을 정하고, 아침 3분 루틴을 시작하세요.'],
      ['3','대화 기능이 궁금하다면','PART 6','일반대화·맞춤대화 화면 구성과 새로 추가되는 용어 설명·모드 변경, 요약 리포트를 카카오톡으로 보내기까지.'],
      ['4','본부장·조직장이라면','PART 1 · 8','숫자로 보는 효과, 대문을 조회 자료로 쓰는 법, 누구부터 챙길지, 4주 도입 플랜.'],
    ];
    items.forEach((it,i)=>{ const x = M + i*3.08, y = 1.95, w = 2.9, h = 2.75;
      L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true});
      L.badge(s,{x:x+0.25,y:y+0.25,n:it[0],d:0.4,color: i===1? C.blue : C.navy});
      L.T(s,it[2],{x:x+0.75,y:y+0.28,w:w-1,h:0.34,fontSize:10.5,bold:true,color:C.blue,valign:'middle'});
      L.T(s,it[1],{x:x+0.25,y:y+0.85,w:w-0.5,h:0.7,fontSize:14.5,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15});
      L.T(s,it[3],{x:x+0.25,y:y+1.5,w:w-0.5,h:1.2,fontSize:10.5,color:C.g600,lineSpacingMultiple:1.3});
    });
    L.note(s,{x:M,y:5.05,w:W-2*M,h:0.72,label:'화면 기준',text:'이 책의 대문·고객찾기·게시판 화면은 2026년 9월 29일 확정된 MeAI 대문 화면이에요. 용어 설명·모드 변경은 개발이 진행 중인 기능이라 오픈 시 세부가 조금 달라질 수 있어요.',tone:'blue',size:10.5});
    L.note(s,{x:M,y:5.9,w:W-2*M,h:0.6,label:'예시 데이터',text:'화면 속 고객 이름·나이·숫자(342명, D-25 등)는 모두 예시예요. 실제 화면에는 내 고객 데이터가 보여요.',tone:'grey',size:10.5});
  }});
  // 목차
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'CONTENTS',title:'목차',sub:'아홉 개 파트예요. 영업가족 편(1~7, 9)과 관리자 편(8)을 함께 담았어요.',pageNo:no});
    const parts = [
      ['01','영업의 방향이 바뀝니다 · 찾는 영업에서 찾아가는 영업으로'],
      ['02','MeAI 대문 · 하루가 시작되는 곳'],
      ['03','맞춤대화로 가는 두 길 · 고객 검색 팝업과 추천 카드'],
      ['04','고객찾기 · 내 고객을 MeAI가 그룹으로 묶어줘요'],
      ['05','게시판 · 사전조회 동의'],
      ['06','대화 이어가기 · 일반대화·맞춤대화와 새 기능'],
      ['07','찾아가는 영업의 하루 · 루틴과 시나리오'],
      ['08','영업관리자 편 · 대문을 조회 자료로'],
      ['09','지켜야 할 것 · FAQ · 용어 정리'],
    ];
    parts.forEach((p,i)=>{ const col = i<5?0:1; const row = i<5? i : i-5; const x = M + col*6.2, y = 1.95 + row*0.88, w = 5.95, h = 0.74;
      const hot = ['02','03','04'].includes(p[0]);
      L.R(s,{x,y,w,h,fill: hot? C.blue50 : C.white, line: hot? null : C.g200, radius:0.12, shadow:!hot});
      L.T(s,p[0],{x:x+0.25,y,w:0.6,h,fontSize:18,bold:true,color: hot? C.blue : C.g400,valign:'middle'});
      L.T(s,p[1],{x:x+0.95,y,w:w-1.9,h,fontSize:12,bold:true,color:C.navy,valign:'middle'});
      L.T(s,'p.'+(ctx.parts[p[0]]||'-'),{x:x+w-0.95,y,w:0.75,h,fontSize:10.5,color:C.g500,align:'right',valign:'middle'});
    });
    L.T(s,'파란 칸(PART 2·3·4)이 이번 판의 핵심이에요. 10월 오픈 화면을 크게 실었어요.',{x:M+6.2,y:1.95+4*0.88,w:5.95,h:0.74,fontSize:10.5,color:C.g600,valign:'middle'});
  }});
};
