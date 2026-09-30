module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, LEG } = ctx;
  const SRC1 = '출처: 데이터분석팀 「MeAI 사용 실태 분석」·「MeAI 효과 분석」, 2026.08 · TA 개인영업 채널 기준';
  // 큰 글씨 단계 흐름(파트 안에서만 쓰는 도우미)
  function bigSteps(s,{x,y,w,h,items,activeIdx=-1}){
    const gap=0.22, cw=(w-gap*(items.length-1))/items.length;
    items.forEach((it,i)=>{ const cx=x+i*(cw+gap), active=i===activeIdx;
      L.R(s,{x:cx,y,w:cw,h,fill:active?C.blue:C.white,line:active?null:C.g200,radius:0.14,shadow:!active});
      L.T(s,`STEP ${it.n}`,{x:cx+0.24,y:y+0.22,w:cw-0.48,h:0.28,fontSize:10.5,bold:true,color:active?'FFFFFF':C.blue,transparency:active?20:0});
      L.T(s,it.title,{x:cx+0.24,y:y+0.52,w:cw-0.48,h:0.5,fontSize:15,bold:true,color:active?'FFFFFF':C.navy,valign:'top'});
      L.T(s,it.desc,{x:cx+0.24,y:y+1.1,w:cw-0.48,h:h-1.25,fontSize:11.5,color:active?'FFFFFF':C.g600,lineSpacingMultiple:1.35});
      if(i<items.length-1) L.T(s,'›',{x:cx+cw-0.02,y:y+h/2-0.2,w:gap+0.04,h:0.4,fontSize:16,color:C.g400,align:'center',valign:'middle'});
    });
  }
  // 폭이 다른 칸으로 그림+설명을 가로로 나열. st = [번호|null, 제목, 설명, [그림...], 폭]
  function flowRow(s, list, {y, h, ty}){
    const total = W-2*M, gap = (total - list.reduce((a,st)=>a+st[4],0))/(list.length-1);
    let x = M;
    list.forEach((st,i)=>{ const w = st[4], files = st[3], vg = 0.12;
      if (files.length===1) L.img(s,files[0],{x,y,w,h,valign:'middle'});
      else { // 쌓을 때: 각 그림을 폭에 맞춘 높이를 더해 가운데 정렬
        const hs = files.map(f=>{ const z = L.imgSize(f); return w*z.h/z.w; });
        let cy = y + (h - (hs.reduce((a,b)=>a+b,0) + vg*(files.length-1)))/2;
        files.forEach((f,k)=>{ L.img(s,f,{x,y:cy,w,h:hs[k],valign:'top'}); cy += hs[k]+vg; });
      }
      if (st[0]){ L.badge(s,{x,y:ty+0.01,n:st[0],d:0.3}); L.T(s,st[1],{x:x+0.4,y:ty,w:w-0.4,h:0.34,fontSize:13.5,bold:true,color:C.navy}); }
      else L.T(s,st[1],{x,y:ty,w,h:0.34,fontSize:13.5,bold:true,color:C.navy});
      L.T(s,st[2],{x,y:ty+0.37,w,h:0.65,fontSize:12,color:C.g600,lineSpacingMultiple:1.3});
      if (i<list.length-1) L.arrow(s,{x:x+w+gap/2-0.175,y:y+h/2-0.25,w:0.35});
      x += w + gap;
    });
  }
  S.push({ part:'01', fn:(pres,no)=> L.divider(pres,{num:'01',title:'영업의 방향이 바뀝니다\n찾는 영업에서 찾아가는 영업으로',sub:'누구에게, 왜, 무슨 말로 연락할지, 이제 MeAI가 먼저 골라요.',learn:['영업의 절반이 "찾는 일"이었던 이유','MeAI 홈이 바꾸는 하루의 순서','숫자로 보는 효과 · 매일 아침 루틴'],pageNo:no}) });
  // 1-1
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 지금까지',title:'영업의 절반은 "찾는 일"이었어요',sub:'고객을 만나기 전에 세 가지를 스스로 정해야 했어요.',pageNo:no});
    const qs = [['?','누구에게 연락하지?','목록을 하나씩 뒤져 오늘 연락할 사람을 골라야 했어요.'],['!','왜 지금이지?','연락할 명분을 스스로 만들어야 했어요.'],['"','무슨 말로 시작하지?','첫 마디를 고민하다 하루를 넘기기 일쑤였어요.']];
    qs.forEach((q,i)=> L.card(s,{x:M+i*4.1,y:1.85,w:3.9,h:2.05,icon:q[0],iconFill:C.g100,iconColor:C.g700,title:q[1],desc:q[2],titleSize:16,descSize:13}));
    L.stat(s,{x:M,y:4.2,w:3.9,h:2.05,value:'7%',unit:'미만',label:'보유 고객 중 영업 시도 비율',desc:'열 명 중 아홉 명 넘게 연락조차 못 하고 있어요.',accent:C.red});
    L.stat(s,{x:M+4.1,y:4.2,w:3.9,h:2.05,value:'2%',unit:'미만',label:'이관 고객 중 영업 시도 비율',desc:'넘겨받은 고객은 더 묵혀 두게 돼요.',accent:C.red});
    L.note(s,{x:M+8.2,y:4.2,w:3.9,h:2.05,label:'',text:'문제는 의지가 아니라 순서예요. 찾는 일이 앞에 있으면 만나는 일은 뒤로 밀려요.',tone:'dark',size:12.5});
    L.caption(s,{x:M,y:6.4,w:8,text:'출처: 세일즈혁신TF 「MeAI CRM 대문 고도화 제안」 2026.09',align:'left',size:10});
  }});
  // 1-2
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 이제는',title:'이제는 MeAI가 먼저 찾아옵니다',sub:'바뀌는 것은 화면이 아니라 하루의 순서예요.',pageNo:no});
    const rows = [['','찾는 영업 (지금까지)','찾아가는 영업 (MeAI 홈)'],['누구에게','목록을 뒤져 내가 고른다','MeAI 홈이 오늘의 추천 고객을 보여준다'],['왜 지금','명분을 스스로 만든다','"상령일이 2주 남았고…" 이유가 붙는다'],['첫 마디','고민하다 미룬다','카드의 이유 문장이 곧 첫 말'],['다음 행동','메뉴를 찾아 헤맨다','[MeAI 고객찾기에서 열기] →\n[이 고객으로 맞춤대화 시작]']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?11:12.5, bold: ri===0 || ci===0, color: ri===0? C.g600 : (ci===2? C.blue700 : C.g800), fill:{color: ri===0? C.g100 : (ci===2? C.blue50 : C.white)}, valign:'middle', margin:[4,8,4,8]}})));
    s.addTable(data,{x:M,y:1.85,w:7.6,colW:[1.2,2.4,4.0],rowH:0.7,border:{type:'solid',color:C.g200,pt:0.75}});
    L.img(s,HERO('gb5_card_kim_z'),{x:8.5,y:1.85,w:4.2,h:4.45,valign:'top'});
    L.caption(s,{x:8.5,y:6.38,w:4.2,text:'「오늘의 추천 고객」 김민수 카드 (예시)',size:10});
    L.note(s,{x:M,y:5.6,w:7.6,h:0.8,label:'기억할 것',text:'발굴은 시스템이, 설득은 사람이 해요. 오른쪽 김민수 고객처럼 "사전조회동의 필요"가 붙으면 맞춤대화 전에 동의 알림톡부터 보내요(PART 5).',tone:'blue',size:12});
  }});
  // 1-3 카드에서 리포트까지
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 한 흐름',title:'클릭 두 번이면 대화가 열려요',sub:'서은아 고객(예시) 한 분으로 따라가 봐요. 화면 속 추천 질문 문장은 예시예요.',pageNo:no});
    const steps = [['1','MeAI 홈 · 추천 카드','이유 문장을 읽고\n[MeAI 고객찾기에서 열기]',[HERO('gb5_card_seo_z')],2.45],['2','고객찾기 · 펼친 카드','한눈에 보기 6칸과 태그로\n상황을 파악해요',[HERO('gb5_find_seo_card')],3.75],['3','맞춤대화 시작','추천 질문을 확인하고\n[이 고객으로 맞춤대화 시작]',[HERO('gb5_find_seo_right')],2.45],['4','요약 리포트 · 카카오톡','좋았던 답만 골라\n고객에게 보내요',[HERO('gb5_kakao_clean')],2.6]];
    flowRow(s, steps, {y:1.85, h:3.05, ty:5.05});
    L.note(s,{x:M,y:6.12,w:W-2*M,h:0.72,label:'',text:'서은아 고객은 사전조회 동의가 아직 유효해서(D-7) [이 고객으로 맞춤대화 시작]을 누르면 바로 열려요.\n"사전조회동의 필요"가 붙은 고객은 동의 알림톡부터 보내요(PART 5).',tone:'grey',size:12});
  }});
  // 1-4 MeAI는 이렇게 준비해요
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · MeAI가 하는 일',title:'MeAI는 매일 이렇게 준비해요',sub:'고객 정보를 모아 그룹을 다시 계산하고, MeAI 홈 카드로 알려줘요.',pageNo:no});
    bigSteps(s,{x:M,y:1.85,w:W-2*M,h:2.55,items:[{n:1,title:'고객 정보 모으기',desc:'계약·보상·동의·상령일·생일·접촉 이력을 모아요.'},{n:2,title:'그룹으로 묶기',desc:'"암진단비 부족"\n"상령일 임박" 같은\n그룹을 매일 다시\n계산해요.'},{n:3,title:'MeAI 홈 카드로 알려주기',desc:'추천 카드를 3장씩\n세 세트로 보여줘요.\n이유 한 문장·태그·\n동의 상태가 붙어요.'},{n:4,title:'고르고 · 묻고 · 터치하기',desc:'고객찾기에서 고르고,\n맞춤대화로 묻고,\n카드 문장으로 연락해\n리포트까지 보내요.'},{n:5,title:'다음 날 다시 계산',desc:'오늘 바뀐 계약·동의 상태를 반영해 다음 날 MeAI 홈에 보여줘요.'}],activeIdx:2});
    const pr = [['발굴은 시스템, 설득은 사람','고르는 시간을 없애고, 만나는 일에 집중해요.'],['추천에는 반드시 이유가 붙어요','"상령일이 2주 남았고…"처럼\n왜 지금인지 한 문장으로 알려줘요.'],['클릭 두 번이면 시작','[MeAI 고객찾기에서 열기] →\n[이 고객으로 맞춤대화 시작]']];
    pr.forEach((p,i)=> L.card(s,{x:M+i*4.1,y:4.65,w:3.9,h:1.55,title:p[0],desc:p[1],titleSize:15,descSize:12}));
    L.caption(s,{x:M,y:6.35,w:W-2*M,text:'※ 데이터·추천 결과는 다음 날 반영돼요. 화면의 "최근 업데이트" 시각을 확인하세요.',align:'left',size:10});
  }});
  // 1-5 숫자로 보기
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 숫자로 보기',title:'MeAI를 쓴 경우 계약 성사율이 2.8배 높았어요',sub:'열 명 중 아홉 분이 써봤어요. MeAI 홈은 매일 아침 열어 볼 이유를 만들어 줘요.',pageNo:no});
    [['91.1%','','MeAI 사용 경험','10,968명이 한 번 이상 사용',C.navy],['2.8배','','계약 성사율(체결전환율)','미활용 12.7% → 활용 35.4%',C.blue],['4배','','같은 FP의 고객끼리 비교','미활용 9.0% → 활용 36.0%',C.blue],['2.3배','','질문을 3개 이상 이어 쓰면','평균 가계약 11.99건 → 27.79건\n(질문 1개 → 3개 이상)',C.navy]].forEach((d,i)=> L.stat(s,{x:M+i*3.08,y:1.85,w:2.9,h:1.85,value:d[0],unit:d[1],label:d[2],desc:d[3],accent:d[4]}));
    const rows=[['7월 활동일','인원','매출 보유율','평균 가계약(건)','매출자 평균'],['미사용','5,987명','53.1%','10.22','256,194원'],['1일','1,835명','79.6%','19.81','310,383원'],['2~4일','2,487명','85.7%','26.35','328,237원'],['5~9일','1,372명','92.5%','38.47','378,083원'],['10일 이상','362명','94.8%','55.04','408,166원']];
    L.table(s,{x:M,y:3.95,w:7.6,rows,colW:[1.5,1.4,1.5,1.6,1.6],size:11,rowH:0.36});
    L.R(s,{x:8.4,y:3.95,w:4.3,h:2.16,fill:C.blue50,line:null,radius:0.12});
    s.addText([
      {text:'한 달에 며칠 쓰느냐', options:{bold:true,color:C.blue,fontSize:12,breakLine:true}},
      {text:'매출 보유율 1.8배 · 평균 가계약 5.4배', options:{bold:true,color:C.g800,fontSize:12,breakLine:true}},
      {text:'(10일 이상 vs 미사용)', options:{color:C.g600,fontSize:11,breakLine:true}},
      {text:'MeAI 홈을 아침마다 여는 습관이 곧 활동일이에요.', options:{color:C.g800,fontSize:12}},
    ],{x:8.65,y:4.05,w:3.8,h:1.96,fontFace:L.FONT,isTextBox:true,margin:0,valign:'middle',lineSpacingMultiple:1.35,paraSpaceAfter:2});
    L.caption(s,{x:M,y:6.28,w:W-2*M,text:SRC1,align:'left',size:10});
  }});
  // 1-6 매일 아침 미리보기
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 그래서 이 책은',title:'매일 아침, MeAI 홈에서 시작해요',sub:'버튼만 누르면 다음 화면으로 이어져요(화면 속 질문 문장은 예시). PART 2~4 화면 · PART 7 루틴 · PART 8 묻는 법.',pageNo:no});
    // 네 걸음(찾기·고르기·묻기·터치하기)에 칸을 맞춘다. 터치하기는 아래 안내 줄에서.
    const items=[[null,'MeAI 홈 열기','내 고객 숫자 4개와\n"사전조회 동의 필요"를 봐요.',[HERO('fix_gate_stats_2row')],2.75],['1','찾기 · 추천 카드','오늘 연락할 고객과\n이유 한 문장을 읽어요.',[HERO('gb5_card_seo_z')],2.45],['2','고르기 · 고객찾기','한눈에 보기 6칸과 태그로\n상황을 보고 한 분을 골라요.',[HERO('gb5_find_seo_card')],3.5],['3','묻기 · 추천 질문','추천 질문을 누르거나\n[이 고객으로 맞춤대화 시작]',[HERO('gb5_find_seo_right')],2.45]];
    flowRow(s, items, {y:1.85, h:2.95, ty:4.9});
    L.note(s,{x:M,y:6.02,w:W-2*M,h:0.8,label:'기억할 것',text:'찾기 → 고르기 → 묻기 → 터치하기. 터치는 카드 문장으로 연락하고 요약 리포트를 보내는 거예요.\n카드 문장은 고객에게 첫 말, 추천 질문은 MeAI에게 첫 질문이에요.',tone:'dark',size:12});
  }});
};
