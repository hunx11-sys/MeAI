module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  // 표지 — 셋째 줄은 소유자 방송교안 1장 문구("나만의 영업비서, "MeAI 홈" OPEN") + 영업가족 편
  S.push({ fn:(pres,no)=> L.cover(pres,{ title:'MeAI\n활용 가이드북', sub:'찾는 영업에서\n찾아가는 영업으로',
    line3:[
      {text:'나만의 영업비서, “MeAI 홈” OPEN', options:{bold:true,fontSize:15,breakLine:true}},
      {text:'영업가족 편', options:{fontSize:12.5}},
    ],
    meta:['v4 · MeAI 홈 편','2026.10 오픈 화면','2026.09.29 확정'], file:HERO('gb5_gate_full_m'), pageNo:no }) });
  // 읽는 법
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'HOW TO USE',title:'이 가이드북 읽는 법',sub:'영업가족이 직접 보는 책. 내 상황에 맞는 곳부터 펼쳐 보기.',pageNo:no});
    const items = [
      ['1','MeAI 홈이 처음이라면','PART 1 · 2','영업포탈에서 MeAI 홈으로\n가는 진입로, 화면 구성과\n카드 한 장 읽는 법'],
      ['2','오늘 바로 써보고 싶다면','PART 3 · 4 · 7','추천 카드에서 맞춤대화까지\n클릭 두 번 · 매일 아침 루틴'],
      ['3','대화 기능이 궁금하다면','PART 6','MeAI 홈에서 누르면 열리는\n일반대화·맞춤대화, 새 기능,\n카카오톡 리포트'],
      ['4','묻는 법이 궁금하다면','PART 8','질문은 클릭으로 고르기,\n누구에게 + 무엇을 묻는 법,\n고객에게 할 말 초안까지'],
    ];
    const cy = 1.85, ch = 2.0;
    const cardKeys = ['01','03','06','08']; // PDF 에서 카드를 누르면 가는 파트 첫 쪽(모양은 그대로)
    items.forEach((it,i)=>{ const x = M + i*3.08, y = cy, w = 2.9, h = ch;
      L.link(no,{x,y,w,h},ctx.parts[cardKeys[i]]);
      L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true});
      L.badge(s,{x:x+0.25,y:y+0.18,n:it[0],d:0.4,color: i===1? C.blue : C.navy});
      L.T(s,it[2],{x:x+0.76,y:y+0.2,w:w-1,h:0.36,fontSize:11,bold:true,color:C.blue,valign:'middle'});
      L.T(s,it[1],{x:x+0.25,y:y+0.66,w:w-0.4,h:0.36,fontSize:16,bold:true,color:C.navy,valign:'middle'});
      L.T(s,it[3],{x:x+0.25,y:y+1.08,w:w-0.4,h:0.74,fontSize:12,color:C.g600,valign:'top',lineSpacingMultiple:1.2});
    });
    // 네 걸음 — 소유자 방송교안 2장 "MeAI로 완성된 영업 사이클"
    const hy = 3.98;
    s.addText([
      {text:'MeAI로 완성된 영업 사이클', options:{bold:true,color:C.navy,fontSize:13}},
      {text:'   내 고객을 MeAI 홈에서 찾아, MeAI에게 묻고, 고객 연락까지', options:{color:C.g600,fontSize:11.5}},
    ],{x:M,y:hy,w:W-2*M,h:0.3,fontFace:L.FONT,isTextBox:true,margin:0,valign:'middle'});
    const steps = [
      ['1 찾기','MeAI 홈','PART 2','오늘 연락할 내 고객을\n추천 카드로 찾기'],
      ['2 고르기','MeAI 고객찾기','PART 3 · 4','상황을 한눈에 보고\n연락할 고객 선택'],
      ['3 묻기','일반대화 · 맞춤대화','PART 6 · 8','MeAI 활용 방법\n기능으로 확인하기'],
      ['4 연락하기','고객에게 연락','PART 6 · 7','카드의 첫 말로 연락하고\n리포트까지 발송하기'],
    ];
    const sy = 4.38, sh = 1.34, gap = 0.22, sw = (W-2*M-gap*3)/4;
    const stepKeys = ['02','03','06','07'];
    steps.forEach((st,i)=>{ const x = M + i*(sw+gap); const on = i===2;
      L.link(no,{x,y:sy,w:sw,h:sh},ctx.parts[stepKeys[i]]);
      L.R(s,{x,y:sy,w:sw,h:sh,fill: on? C.blue : C.white, line: on? null : C.g200, radius:0.14, shadow:!on});
      L.T(s,st[0],{x:x+0.22,y:sy+0.12,w:sw-1.2,h:0.34,fontSize:15,bold:true,color: on?'FFFFFF':C.navy,valign:'middle'});
      L.T(s,st[2],{x:x+sw-1.12,y:sy+0.12,w:0.9,h:0.34,fontSize:10,color: on?'FFFFFF':C.g500,transparency: on?25:0,align:'right',valign:'middle'});
      L.T(s,st[1],{x:x+0.22,y:sy+0.47,w:sw-0.4,h:0.26,fontSize:10.5,bold:true,color: on? C.blue100 : C.blue,valign:'middle'});
      L.T(s,st[3],{x:x+0.22,y:sy+0.78,w:sw-0.4,h:0.46,fontSize:11,color: on?'FFFFFF':C.g600,valign:'top',lineSpacingMultiple:1.2});
    });
    L.note(s,{x:M,y:5.84,w:W-2*M,h:0.44,label:'기억할 것',text:'카드 문장은 고객에게 첫 말, 추천 질문은 MeAI에게 첫 질문. 찾기·고르기·묻기는 MeAI 홈에서 시작해 누르기만 하면 됨.',tone:'blue',size:11.5});
    // 화면 기준 · 예시 데이터 (회색 안내 한 줄)
    L.R(s,{x:M,y:6.38,w:W-2*M,h:0.42,fill:C.g100,line:null,radius:0.12});
    s.addText([
      {text:'화면 기준  ', options:{bold:true,color:C.g700}},
      {text:'2026.09.29 확정 화면. PART 6의 새 기능(용어 설명·모드 변경)은 개발 중이라 바뀔 수 있음', options:{color:C.g800}},
      {text:'      ', options:{color:C.g800}},
      {text:'예시 데이터  ', options:{bold:true,color:C.g700}},
      {text:'화면 속 고객 이름·나이·숫자는 모두 예시', options:{color:C.g800}},
    ],{x:M+0.25,y:6.38,w:W-2*M-0.5,h:0.42,fontFace:L.FONT,fontSize:10.5,isTextBox:true,margin:0,valign:'middle'});
  }});
  // 목차
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'CONTENTS',title:'목차',sub:'영업가족 편',pageNo:no});
    const parts = [
      ['01','바뀌는 영업의 방향'],
      ['02','MeAI 홈 · 하루가 시작되는 곳'],
      ['03','맞춤대화로 가는 두 길'],
      ['04','고객찾기 · MeAI가 그룹으로 묶어 둔 내 고객'],
      ['05','게시판 · 사전조회 동의'],
      ['06','대화 이어가기 · 일반대화 · 맞춤대화'],
      ['07','찾아가는 영업의 하루'],
      ['08','MeAI 활용 방법 · 이렇게 묻기'],
      ['09','지켜야 할 것 · FAQ · 용어'],
    ];
    // 파트 시작 쪽은 deck.js 가 각 파트 구분 장의 part 키('01'~'09')로 ctx.parts 에 채운다
    const hotKeys = ['02','03','04','08'];
    // 줄 간격 0.74 · 높이 0.62 (아래 '이럴 땐 여기' 자리를 만들려고 줄였음, 글자 크기는 그대로). PDF 에서 줄을 누르면 그 파트로
    const rowY = (row)=> 1.85 + row*0.74, rh = 0.62, rw = 5.95;
    parts.forEach((p,i)=>{ const col = i<5?0:1; const row = i<5? i : i-5; const x = M + col*6.2, y = rowY(row), w = rw, h = rh;
      const hot = hotKeys.includes(p[0]);
      L.R(s,{x,y,w,h,fill: hot? C.blue50 : C.white, line: hot? null : C.g200, radius:0.12, shadow:!hot});
      L.T(s,p[0],{x:x+0.25,y,w:0.7,h,fontSize:20,bold:true,color: hot? C.blue : C.g400,valign:'middle'});
      L.T(s,p[1],{x:x+1.0,y,w:w-1.95,h,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,'p.'+(ctx.parts[p[0]]||'-'),{x:x+w-0.95,y,w:0.75,h,fontSize:11,color:C.g500,align:'right',valign:'middle'});
      L.link(no,{x,y,w,h},ctx.parts[p[0]]);
    });
    // 오른쪽 다섯째 칸: '한 장 요약' 쪽(p9 의 part:'sum') 바로가기. ctx.parts.sum 은 전체 빌드에만 있음 —
    // ONLY=p0 빌드에선 'p.-'(링크 없음). 전체 빌드인데 요약 쪽이 없으면 칸을 비워 둠(없는 쪽을 가리키지 않게.
    // 예전 회색 안내 '파란 칸(PART 2·3·4·8)부터…' 는 아래 '이럴 땐 여기' 오른쪽 줄로 옮겨 갔으니 되살리지 않음)
    const sumPg = ctx.parts.sum, sx = M+6.2, sy = rowY(4);
    if (sumPg || !ctx.parts['09']){
      L.R(s,{x:sx,y:sy,w:rw,h:rh,fill:C.navy,line:null,radius:0.12});
      L.T(s,'바쁘면 한 장 요약부터',{x:sx+0.25,y:sy,w:rw-1.4,h:rh,fontSize:13.5,bold:true,color:'FFFFFF',valign:'middle'});
      L.T(s,'p.'+(sumPg||'-'),{x:sx+rw-0.95,y:sy,w:0.75,h:rh,fontSize:11,color:'FFFFFF',transparency:30,align:'right',valign:'middle'});
      L.link(no,{x:sx,y:sy,w:rw,h:rh},sumPg);
    }
    // 이럴 땐 여기 — 상황별 바로가기 8칸. 쪽 번호는 파트 첫 쪽 + 상대 위치(p4 의 tagPg 와 같은 방식)라 쪽이 밀려도 따라감
    const rel = (k,d)=> ctx.parts[k] ? ctx.parts[k]+d : null;
    const hy = 5.55;
    L.T(s,'이럴 땐 여기',{x:M,y:hy,w:3,h:0.3,fontSize:12,bold:true,color:C.navy,valign:'middle'});
    const faqPg = rel('09',2), termPg = rel('09',3);
    const faqS = `FAQ p.${faqPg||'-'}`, termS = `용어 p.${termPg||'-'}`;
    L.T(s,`파란 칸(PART 2·3·4·8) = MeAI 홈 화면과 묻는 법 · ${faqS} · ${termS}`,{x:W-M-8,y:hy,w:8,h:0.3,fontSize:10.5,color:C.g600,align:'right',valign:'middle'});
    // 오른쪽 끝 'FAQ p.N · 용어 p.N' 도 누르면 이동. 오른쪽 정렬이라 끝에서 거꾸로 잼(textW 는 실제 폭보다 약 10% 넓게 나와 0.9 를 곱함)
    const kW = 0.9, cut = W-M - L.textW(termS,10.5)*kW - L.textW(' · ',10.5)*kW/2;
    L.link(no,{x:cut,y:hy,w:W-M+0.05-cut,h:0.3},termPg);
    L.link(no,{x:cut-L.textW(faqS,10.5)*kW-0.12,y:hy,w:L.textW(faqS,10.5)*kW+0.12,h:0.3},faqPg);
    const idx = [
      ['"사전조회동의 필요"가 뜸', rel('05',3)],
      ['숫자 4개의 뜻', rel('02',6)],
      ['카드 한 장 읽기', rel('02',8)],
      ['검색 팝업에 없음 · 회색', rel('03',3)],
      ['그룹별 한 줄 화법', rel('04',4)],
      ['직접 묻는 공식', rel('08',2)],
      ['고객에게 첫 말 모음', rel('08',5)],
      ['모바일에서 쓰기', rel('06',13)],
    ];
    const cg = 0.15, cw = (W-2*M-0.45)/4, chh = 0.4;
    idx.forEach(([t,pg],i)=>{ const x = M + (i%4)*(cw+cg), y = i<4? 5.95 : 6.43;
      L.R(s,{x,y,w:cw,h:chh,fill:C.g50,line:C.g200,radius:0.1});
      L.T(s,t,{x:x+0.18,y,w:cw-0.75,h:chh,fontSize:11,color:C.g800,valign:'middle'});
      L.T(s,'p.'+(pg||'-'),{x:x+cw-0.78,y,w:0.6,h:chh,fontSize:11,bold:true,color:C.blue,align:'right',valign:'middle'});
      L.link(no,{x,y,w:cw,h:chh},pg);
    });
  }});
};
