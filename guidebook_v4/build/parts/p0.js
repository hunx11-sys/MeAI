module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  // 표지
  S.push({ fn:(pres,no)=> L.cover(pres,{ title:'MeAI\n활용 가이드북', sub:'찾는 영업에서,\n찾아가는 영업으로', line3:'오늘 만날 고객과 첫 마디를 MeAI 홈이 먼저 준비해요.\n영업가족 편', meta:['v4 · MeAI 홈 편','2026.10 오픈 화면','2026.09.29 확정'], file:HERO('gb5_gate_full_m'), pageNo:no }) });
  // 이렇게 보세요
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'HOW TO USE',title:'이 가이드북, 이렇게 보세요',sub:'영업가족이 직접 보는 책이에요. 내 상황에 맞는 곳부터 펼쳐 보세요.',pageNo:no});
    const items = [
      ['1','MeAI 홈이 처음이라면','PART 1 · 2','영업포탈에서 들어가는 길,\nMeAI 홈 화면과\n카드 한 장 읽는 법.'],
      ['2','오늘 바로 써보고 싶다면','PART 3 · 4 · 7','추천 카드에서 맞춤대화까지\n클릭 두 번. 매일 아침 루틴.'],
      ['3','대화 기능이 궁금하다면','PART 6','MeAI 홈에서 누르면 열리는\n일반대화·맞춤대화, 새 기능,\n카카오톡 리포트.'],
      ['4','MeAI에게 어떻게 물을지 궁금하다면','PART 8','질문은 고르는 것,\n누구에게 + 무엇을 묻는 법,\n고객에게 할 말 초안까지.'],
    ];
    items.forEach((it,i)=>{ const x = M + i*3.08, y = 1.85, w = 2.9, h = 2.7;
      L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true});
      L.badge(s,{x:x+0.25,y:y+0.25,n:it[0],d:0.42,color: i===1? C.blue : C.navy});
      L.T(s,it[2],{x:x+0.78,y:y+0.28,w:w-1,h:0.36,fontSize:11,bold:true,color:C.blue,valign:'middle'});
      L.T(s,it[1],{x:x+0.25,y:y+0.85,w:w-0.5,h:0.7,fontSize:16,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15});
      L.T(s,it[3],{x:x+0.25,y:y+1.62,w:w-0.5,h:0.95,fontSize:12.5,color:C.g600,lineSpacingMultiple:1.35});
    });
    L.note(s,{x:M,y:4.78,w:W-2*M,h:0.76,label:'기억할 것',text:'카드 문장은 고객에게 첫 말, 추천 질문은 MeAI에게 첫 질문.\n찾기 → 고르기 → 묻기 → 터치하기. 앞의 세 걸음은 MeAI 홈에서 시작해 누르기만 하면 돼요.',tone:'blue',size:11.5});
    L.note(s,{x:M,y:5.64,w:W-2*M,h:0.52,label:'화면 기준',text:'2026.09.29 확정 화면이에요. PART 6의 새 기능(용어 설명·모드 변경)은 개발 중이라 바뀔 수 있어요.',tone:'grey',size:11.5});
    L.note(s,{x:M,y:6.26,w:W-2*M,h:0.52,label:'예시 데이터',text:'화면 속 고객 이름·나이·숫자는 모두 예시예요.',tone:'grey',size:11.5});
  }});
  // 목차
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'CONTENTS',title:'목차',sub:'영업가족 편',pageNo:no});
    const parts = [
      ['01','영업의 방향이 바뀝니다'],
      ['02','MeAI 홈 · 하루가 시작되는 곳'],
      ['03','맞춤대화로 가는 두 길'],
      ['04','고객찾기 · 그룹으로 묶어줘요'],
      ['05','게시판 · 사전조회 동의'],
      ['06','대화 이어가기 · 일반대화 · 맞춤대화'],
      ['07','찾아가는 영업의 하루'],
      ['08','MeAI 활용 방법 · 이렇게 물어보세요'],
      ['09','지켜야 할 것 · FAQ · 용어'],
    ];
    // 파트 시작 쪽은 deck.js 가 각 파트 구분 장의 part 키('01'~'09')로 ctx.parts 에 채운다
    const hotKeys = ['02','03','04','08'];
    parts.forEach((p,i)=>{ const col = i<5?0:1; const row = i<5? i : i-5; const x = M + col*6.2, y = 1.85 + row*0.9, w = 5.95, h = 0.76;
      const hot = hotKeys.includes(p[0]);
      L.R(s,{x,y,w,h,fill: hot? C.blue50 : C.white, line: hot? null : C.g200, radius:0.12, shadow:!hot});
      L.T(s,p[0],{x:x+0.25,y,w:0.7,h,fontSize:20,bold:true,color: hot? C.blue : C.g400,valign:'middle'});
      L.T(s,p[1],{x:x+1.0,y,w:w-1.95,h,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,'p.'+(ctx.parts[p[0]]||'-'),{x:x+w-0.95,y,w:0.75,h,fontSize:11,color:C.g500,align:'right',valign:'middle'});
    });
    L.T(s,'파란 칸(PART 2·3·4·8)부터 보면 MeAI 홈을 바로 쓸 수 있어요.',{x:M+6.2,y:1.85+4*0.9,w:5.95,h:0.76,fontSize:12,color:C.g600,valign:'middle'});
  }});
};
