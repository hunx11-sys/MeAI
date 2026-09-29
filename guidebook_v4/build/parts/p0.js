module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  // 표지
  S.push({ fn:(pres,no)=> L.cover(pres,{ title:'MeAI\n활용 가이드북', sub:'찾는 영업에서,\n찾아가는 영업으로', line3:'오늘 만날 고객과 첫 마디를 MeAI 대문이 먼저 준비해요.\n영업가족 편 + 관리자 편', meta:['v4 · CRM 대문 편','2026.10 오픈 화면','2026.09.29 확정'], file:HERO('gate_full'), pageNo:no }) });
  // 이렇게 보세요
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'HOW TO USE',title:'이 가이드북, 이렇게 보세요',sub:'영업가족과 영업관리자가 함께 보는 책이에요. 내 상황부터 펼치세요.',pageNo:no});
    const items = [
      ['1','MeAI 대문이 처음이라면','PART 1 · 2','영업포탈에서 들어가는 길, 대문 화면과 카드 한 장 읽는 법.'],
      ['2','오늘 바로 써보고 싶다면','PART 3 · 4 · 7','추천 카드에서 맞춤대화까지 클릭 두 번. 아침 3분 루틴.'],
      ['3','대화 기능이 궁금하다면','PART 6','일반대화·맞춤대화, 용어 설명·모드 변경, 카카오톡 리포트.'],
      ['4','본부장·조직장이라면','PART 1 · 8','숫자로 보는 효과, 누구부터 챙길지, 4주 도입 플랜.'],
    ];
    items.forEach((it,i)=>{ const x = M + i*3.08, y = 1.85, w = 2.9, h = 2.7;
      L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true});
      L.badge(s,{x:x+0.25,y:y+0.25,n:it[0],d:0.42,color: i===1? C.blue : C.navy});
      L.T(s,it[2],{x:x+0.78,y:y+0.28,w:w-1,h:0.36,fontSize:11,bold:true,color:C.blue,valign:'middle'});
      L.T(s,it[1],{x:x+0.25,y:y+0.85,w:w-0.5,h:0.7,fontSize:16,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15});
      L.T(s,it[3],{x:x+0.25,y:y+1.5,w:w-0.5,h:1.05,fontSize:12.5,color:C.g600,lineSpacingMultiple:1.35});
    });
    L.note(s,{x:M,y:4.85,w:W-2*M,h:0.72,label:'화면 기준',text:'2026.09.29 확정 화면이에요. 용어 설명·모드 변경은 개발 중이라 바뀔 수 있어요.',tone:'blue',size:11.5});
    L.note(s,{x:M,y:5.7,w:W-2*M,h:0.6,label:'예시 데이터',text:'화면 속 고객 이름·나이·숫자는 모두 예시예요.',tone:'grey',size:11.5});
  }});
  // 목차
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'CONTENTS',title:'목차',sub:'영업가족 편(1~7·9) + 관리자 편(8)',pageNo:no});
    const parts = [
      ['01','영업의 방향이 바뀝니다'],
      ['02','MeAI 대문 · 영업포탈에서 들어가기'],
      ['03','맞춤대화로 가는 두 길'],
      ['04','고객찾기 · 그룹으로 묶어줘요'],
      ['05','게시판 · 사전조회 동의'],
      ['06','대화 이어가기 · 새 기능'],
      ['07','찾아가는 영업의 하루'],
      ['08','영업관리자 편'],
      ['09','지켜야 할 것 · FAQ · 용어'],
    ];
    parts.forEach((p,i)=>{ const col = i<5?0:1; const row = i<5? i : i-5; const x = M + col*6.2, y = 1.85 + row*0.9, w = 5.95, h = 0.76;
      const hot = ['02','03','04'].includes(p[0]);
      L.R(s,{x,y,w,h,fill: hot? C.blue50 : C.white, line: hot? null : C.g200, radius:0.12, shadow:!hot});
      L.T(s,p[0],{x:x+0.25,y,w:0.7,h,fontSize:20,bold:true,color: hot? C.blue : C.g400,valign:'middle'});
      L.T(s,p[1],{x:x+1.0,y,w:w-1.95,h,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,'p.'+(ctx.parts[p[0]]||'-'),{x:x+w-0.95,y,w:0.75,h,fontSize:11,color:C.g500,align:'right',valign:'middle'});
    });
    L.T(s,'파란 칸(PART 2·3·4)이 이번 판의 핵심이에요.',{x:M+6.2,y:1.85+4*0.9,w:5.95,h:0.76,fontSize:12,color:C.g600,valign:'middle'});
  }});
};
