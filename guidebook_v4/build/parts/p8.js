module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  const SRC_DATA = '출처: 2026년 8월 TA채널 MeAI 사용 데이터 분석';
  // 캡처 위 테두리(캡처 픽셀 좌표, dsf 1)
  const box = (s,g,x1,y1,x2,y2,{color=C.blue,width=1.5,radius=0.04}={}) => s.addShape('roundRect',{x:g.x+x1*g.scale,y:g.y+y1*g.scale,w:(x2-x1)*g.scale,h:(y2-y1)*g.scale,fill:{type:'none'},line:{color,width},rectRadius:radius});
  // 캡처 위 밑줄(캡처 픽셀 좌표, dsf 1)
  const ul = (s,g,x1,x2,y,color,width=2.25) => s.addShape('line',{x:g.x+x1*g.scale,y:g.y+y*g.scale,w:(x2-x1)*g.scale,h:0,line:{color,width}});
  const P1 = {dsf:1, d:0.3};

  // ---- 구분 장 ----
  S.push({ part:'08', fn:(pres,no)=> L.divider(pres,{num:'08',title:'MeAI 활용 방법\n이렇게 묻기',sub:'질문을 고민할 필요 없이 클릭으로',learn:['질문 창구 네 곳 · 추천 프롬프트 · 꼬리질문','직접 물을 땐 "누구에게 + 무엇을"','고객에게 할 말 초안 · 이렇게는 묻지 않기','카드마다 고객에게 첫 말, MeAI에게 첫 질문'],pageNo:no}) });

  // ---- 8-1 질문은 고르는 것 (방송판 15장) ----
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 질문 고르기',title:'질문을 고민할 필요 없이 클릭으로',sub:'추천 프롬프트와 프롬프트 라이브러리, 꼬리질문을 통해 클릭으로 진행하는 MeAI',pageNo:no});
    const gap = 0.2, cw = (W-2*M-gap*3)/4, cy = 1.85, chh = 3.55;
    const cols = [
      {title:'시작할 때', pill:'질문 예시 탭', desc:'보장비교 · 지식검색 · 자주하는 질문\n예시를 누르면 바로 대화 시작'},
      {title:'고객이 정해졌을 때', pill:'MeAI에 이렇게 물어보세요', desc:'고객찾기에 고객별 맞춤 프롬프트 세팅\n누르면 입력창에 채워짐 → 전송(↑)'},
      {title:'답을 받은 뒤', pill:'답 아래 질문 버튼 3개', desc:'다음 프롬프트를 꼬리질문이 제시\n누르면 그 질문이 바로 전송'},
      {title:'더 필요할 때', pill:'프롬프트 라이브러리 · 나의 질문', desc:'[질문 더보기]에서 클릭\n좋았던 질문은 저장 → 나의 질문'},
    ];
    const gs = [];
    cols.forEach((c,i)=>{ const x = M+i*(cw+gap);
      L.R(s,{x,y:cy,w:cw,h:chh,fill:C.g50,line:null,radius:0.14});
      L.badge(s,{x:x+0.18,y:cy+0.17,n:i+1,d:0.3});
      L.T(s,c.title,{x:x+0.56,y:cy+0.14,w:cw-0.66,h:0.36,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      L.chip(s,{x:x+0.18,y:cy+0.6,text:c.pill,size:10,h:0.28});
      L.T(s,c.desc,{x:x+0.18,y:cy+2.88,w:cw-0.3,h:0.6,fontSize:10.5,color:C.g700,valign:'top',lineSpacingMultiple:1.2});
      gs.push(x); });
    const ib = (i)=>({x:gs[i]+0.14,y:cy+1.0,w:cw-0.28,h:1.78});
    // ① 일반대화 첫 화면 — 질문 예시 탭 3개
    const g1 = L.img(s,HERO('bc2_general_home'),Object.assign(ib(0),{valign:'middle',align:'center',shadow:false}));
    box(s,g1,44,624,1012,726); L.pin(s,g1,1125,675,1,P1);
    // ② 고객찾기 오른쪽 'MeAI에 이렇게 물어보세요'
    const g2 = L.img(s,HERO('bc2_find_right_top'),Object.assign(ib(1),{valign:'middle',align:'center',shadow:false}));
    box(s,g2,70,195,530,247); L.pin(s,g2,640,221,2,P1);
    // ③ 답 아래 질문 버튼 · ④ [질문 더보기]
    const g3 = L.img(s,HERO('bc2_mo_examples'),Object.assign(ib(2),{valign:'middle',align:'center',shadow:false}));
    L.pin(s,g3,10,215,3,P1); L.pin(s,g3,10,795,4,P1);
    // ④ 내 질문 아래 저장 아이콘
    const x4 = gs[3];
    const g4 = L.img(s,AG('term','35_pc_message_actions'),{x:x4+0.35,y:cy+1.0,w:cw-0.7,h:0.95,valign:'middle',align:'center',shadow:false});
    box(s,g4,186,56,230,102,{color:C.red}); L.pin(s,g4,262,40,4,P1);
    L.T(s,'내 질문 아래 복사 · 편집 · 저장',{x:x4+0.18,y:g4.y+g4.h+0.04,w:cw-0.3,h:0.24,fontSize:9.5,color:C.g500,align:'center',valign:'middle'});
    L.R(s,{x:x4+0.18,y:cy+2.3,w:cw-0.36,h:0.5,fill:C.white,line:C.g200,radius:0.1});
    L.T(s,'대화 이력 · 나의 질문은\nPC · 휴대폰에서 똑같이 보임',{x:x4+0.18,y:cy+2.3,w:cw-0.36,h:0.5,fontSize:10,color:C.g700,align:'center',valign:'middle',lineSpacingMultiple:1.1});
    // 아래 띠: 질문을 이어 쓸수록
    const by = 5.55, bh = 0.8;
    L.R(s,{x:M,y:by,w:W-2*M,h:bh,fill:C.purple50,line:null,radius:0.14});
    L.T(s,'많이 질문할수록\n늘어나는 영업기회',{x:M+0.3,y:by,w:1.9,h:bh,fontSize:13,bold:true,color:C.purple,valign:'middle',lineSpacingMultiple:1.1});
    // 질문 수별 평균 가계약 — 원본 가로막대(강조형: 3개 이상만 보라, 나머지 회색 · 값 라벨 필수)
    L.bars(s,{x:4.05,y:5.61,w:4.6,h:0.68,dir:'bar',plot:{x:0,y:0,w:0.8,h:1},
      labels:['질문 1개','질문 2개','질문 3개 이상'],values:[11.99,17.02,27.79],colors:['B0B8C1','B0B8C1',C.purple],
      max:30,gap:45,fmt:v=>v.toFixed(2)+'건',valueSize:11,catW:1.07,catSize:11,catColor:C.g700,catBoldIdx:2});
    L.T(s,'2.3배',{x:M+8.75,y:by,w:1.3,h:bh,fontSize:30,bold:true,color:C.navy,valign:'middle'});
    L.T(s,'질문 1건 대비 3건 이상\n평균 가계약 수',{x:M+10.05,y:by,w:W-2*M-10.1,h:bh,fontSize:11.5,color:C.g700,valign:'middle',lineSpacingMultiple:1.1});
    L.caption(s,{x:M,y:6.45,w:8.6,text:SRC_DATA,align:'left',size:10});
    L.caption(s,{x:W-M-3.4,y:6.45,w:3.4,text:'※ 화면의 이름 · 질문 문장은 예시',align:'right',size:10});
  }});

  // ---- 8-2 직접 묻는 공식 (방송판 18장) ----
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 직접 묻기',title:'직접 물을 땐 “누구에게 + 무엇을”',sub:'말하듯 편하게 입력하면 MeAI가 답변 · 형식은 없어도 괜찮음',pageNo:no});
    const ws = [2.95,2.65,2.95,3.0], pg = 0.19, y = 1.9, h = 1.3;
    const blocks = [
      ['누구에게','“40대 자녀 둘 가장,\n암진단비만 있는 고객에게”',C.blue50,C.blue,null],
      ['무엇을','“암 통합치료비가\n왜 필요한지 설명해줘”',C.white,C.navy,C.navy],
      ['형식 추가하면 더 깔끔하게','“표로” · “구어체로”\n“카톡 6줄로”',C.white,C.g600,C.g300],
      ['안전장치 한 마디','“자료에 없으면 추정하지 말고\n‘확인필요’로 표시해”',C.yellow50,'B7791F',null],
    ];
    let x = M;
    blocks.forEach((b,i)=>{ const w = ws[i];
      L.R(s,{x,y,w,h,fill:b[2],line:b[4],lw:i===1?1.25:1,radius:0.14});
      L.T(s,b[0],{x:x+0.22,y:y+0.14,w:w-0.35,h:0.32,fontSize:12.5,bold:true,color:b[3],valign:'middle'});
      L.T(s,b[1],{x:x+0.22,y:y+0.52,w:w-0.35,h:0.68,fontSize:12.5,bold:i<2||i===3,color:C.navy,valign:'top',lineSpacingMultiple:1.15});
      x += w; if (i<3){ L.T(s,'+',{x,y,w:pg,h,fontSize:18,bold:true,color:C.g400,align:'center',valign:'middle'}); x += pg; } });
    // 전과 후
    L.T(s,'한 줄만 바꿔도 달라지는 답변의 수준',{x:M,y:3.38,w:8,h:0.36,fontSize:14,bold:true,color:C.navy,valign:'middle'});
    const cy = 3.82, ch = 1.3, bw = 3.6;
    L.R(s,{x:M,y:cy,w:bw,h:ch,fill:C.g100,line:null,radius:0.14});
    L.chip(s,{x:M+0.22,y:cy+0.16,text:'전',fill:C.g600,color:'FFFFFF',size:10.5,h:0.28});
    L.T(s,'“실손 설명해줘”',{x:M+0.22,y:cy+0.5,w:bw-0.4,h:0.36,fontSize:15,bold:true,color:C.g700,valign:'middle'});
    L.T(s,'→ 실손의 일반 개념을 길게 설명',{x:M+0.22,y:cy+0.9,w:bw-0.4,h:0.3,fontSize:11.5,color:C.g600,valign:'middle'});
    L.T(s,'›',{x:M+bw,y:cy,w:0.45,h:ch,fontSize:26,color:C.blue,align:'center',valign:'middle'});
    const ax = M+bw+0.45, aw = W-M-ax;
    L.R(s,{x:ax,y:cy,w:aw,h:ch,fill:C.white,line:C.blue,lw:1.5,radius:0.14});
    L.chip(s,{x:ax+0.22,y:cy+0.16,text:'후',fill:C.blue,color:'FFFFFF',size:10.5,h:0.28});
    const f = (t,o)=>({text:t,options:Object.assign({fontFace:L.FONT,fontSize:12.5,bold:true,color:C.navy},o||{})});
    s.addText([f('“'),f('3세대 실손 가입한 50대 고객에게',{color:C.blue}),f(', 4세대와 비교해서 자기부담과 비급여 한도의 차이를 '),f('표 1개로',{color:C.g600}),f(' 정리하고, 유지가 유리한 경우 3가지를 '),f('구어체로',{color:C.g600}),f(' 알려줘”')],
      {x:ax+0.22,y:cy+0.46,w:aw-0.4,h:0.5,isTextBox:true,margin:0,valign:'middle',lineSpacingMultiple:1.12});
    L.T(s,'→ 고객 세대 기준 비교표 + 바로 말할 수 있는 3가지',{x:ax+0.22,y:cy+0.96,w:aw-0.4,h:0.28,fontSize:12,bold:true,color:C.blue,valign:'middle'});
    // 아래 띠: 고쳐 묻기 · 휴대폰 마이크
    const by = 5.28, bh = 1.2;
    L.R(s,{x:M,y:by,w:W-2*M,h:bh,fill:C.g50,line:null,radius:0.14});
    const g = L.img(s,AG('mode','43_mo_zoom_input'),{x:M+0.3,y:by+0.08,w:2.8,h:0.84,valign:'top',align:'left',shadow:false});
    L.pin(s,g,875,22,1,{dsf:1,d:0.26,color:C.red}); L.pin(s,g,983,212,2,{dsf:1,d:0.26,color:C.red});
    L.T(s,'휴대폰 MeAI 입력창',{x:g.x,y:g.y+g.h+0.03,w:g.w,h:0.22,fontSize:9.5,color:C.g500,align:'center',valign:'middle'});
    const tx = M+3.35, tw = W-M-tx-0.25, r = (t,o)=>({text:t,options:Object.assign({fontFace:L.FONT,fontSize:13,bold:true,color:C.navy},o||{})});
    s.addText([r('안 맞으면 “더 쉽게” · “표로 다시” 한 마디',{breakLine:true}),
      r('휴대폰이라 타이핑이 어렵다면? '),r('①',{color:C.red}),r(' 마이크를 눌러 말하고 '),r('②',{color:C.red}),r(' 전송(↑)')],
      {x:tx,y:by,w:tw,h:bh,isTextBox:true,margin:0,valign:'middle',lineSpacingMultiple:1.45});
    L.caption(s,{x:M,y:6.58,w:W-2*M,text:'예시 문장 출처: 이전 판 「MeAI 활용 가이드북 · 영업가족 편」(2026.09)',align:'left',size:10});
  }});

  // ---- 8-3 고객에게 할 말 초안 (방송판 19장) ----
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 고객에게 할 말',title:'고객에게 할 말도 MeAI가 초안 작성',sub:'한 줄만 부탁하면 초안이 완성 · 이름 대신 조건으로 요청',pageNo:no});
    // 위 띠: 파란 추천 질문
    const ty = 1.85, th = 1.85;
    L.R(s,{x:M,y:ty,w:W-2*M,h:th,fill:C.white,line:C.g200,radius:0.14});
    L.T(s,'카톡용 / 전화용 요청만 하면',{x:M+0.25,y:ty+0.14,w:3.1,h:0.34,fontSize:14,bold:true,color:C.navy,valign:'middle'});
    L.T(s,'고객찾기 오른쪽 파란 [일반대화]\n추천 질문을 누르면 이렇게 채워짐',{x:M+0.25,y:ty+0.5,w:3.1,h:0.44,fontSize:10.5,color:C.g700,valign:'top',lineSpacingMultiple:1.15});
    const lg = [['그룹 · 나이대 · 유형 조건',C.blue],['3~4줄 · 부담스럽지 않은 톤',C.purple],['고객 성명 · 연락처는 제외',C.red]];
    lg.forEach(([t,col],i)=>{ const ly = ty+1.03+i*0.26; s.addShape('line',{x:M+0.25,y:ly+0.19,w:0.24,h:0,line:{color:col,width:3}}); L.T(s,t,{x:M+0.58,y:ly,w:2.8,h:0.24,fontSize:10.5,bold:true,color:C.g700,valign:'middle'}); });
    const gx = M+3.45, gw = W-M-gx-0.15;
    const g = L.img(s,HERO('bc2_general_input'),{x:gx,y:ty+0.1,w:gw,h:th-0.2,valign:'middle',align:'left',shadow:false,round:false});
    ul(s,g,62,456,101,C.blue); ul(s,g,1280,1493,101,C.purple); ul(s,g,63,458,146,C.purple); ul(s,g,461,854,146,C.red);
    // 왼쪽 아래: 직접 부탁
    const by = 3.88, lw = 6.0;
    L.T(s,'직접 부탁해도 가능',{x:M,y:by,w:lw,h:0.34,fontSize:14,bold:true,color:C.navy,valign:'middle'});
    [['카톡 안내문','“보장분석 결과를 고객에게 보낼 카톡 안내문 6줄로 써줘. 존댓말, 단정 표현은 빼고”'],['첫 미팅 전','“이 고객에게 첫 만남에서 꺼낼 질문 3개 만들어줘”']].forEach(([lab,t],i)=>{ const yy = by+0.42+i*0.9;
      L.R(s,{x:M,y:yy,w:lw,h:0.8,fill:C.white,line:C.blue,lw:1.25,radius:0.14});
      L.T(s,lab,{x:M+0.22,y:yy+0.07,w:2.5,h:0.24,fontSize:10,bold:true,color:C.g500,valign:'middle'});
      L.T(s,t,{x:M+0.22,y:yy+0.31,w:lw-0.4,h:0.44,fontSize:12,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.05}); });
    // 오른쪽 아래: 고객 앞에서는 두 버튼
    const rx = M+lw+0.35, rw = W-M-rx, hw = (rw-0.2)/2;
    L.T(s,'고객 앞에서는 두 버튼',{x:rx,y:by,w:3,h:0.34,fontSize:14,bold:true,color:C.navy,valign:'middle'});
    const ct = '개발 중 · 바뀔 수 있음'; L.chip(s,{x:W-M-(L.textW(ct,10)+0.3),y:by+0.03,text:ct,fill:C.red50,color:C.red,size:10,h:0.28});
    const gA = L.img(s,HERO('bc2_mode_simple'),{x:rx,y:by+0.45,w:hw,h:0.82,valign:'middle',align:'center',shadow:false});
    const gB = L.img(s,HERO('fix_term_tooltip'),{x:rx+hw+0.2,y:by+0.42,w:hw,h:0.8,valign:'middle',align:'center',shadow:false});
    L.T(s,'화면 속 숫자는 예시',{x:gB.x-0.3,y:gB.y+gB.h+0.01,w:gB.w+0.6,h:0.2,fontSize:9,color:C.g500,align:'center',valign:'middle'});
    [['[간편 분석]','어려운 보험 용어를 일상 언어로\n약관을 따질 땐 상세 분석',rx],['[용어]','켜고 표시된 말을 누르면 뜻풀이\n고객 눈높이 문장, 그대로 읽기',rx+hw+0.2]].forEach(([t,d,xx])=>{
      L.T(s,t,{x:xx,y:by+1.5,w:hw,h:0.3,fontSize:13,bold:true,color:C.navy,valign:'middle'});
      L.T(s,d,{x:xx,y:by+1.8,w:hw,h:0.42,fontSize:10,color:C.g600,valign:'top',lineSpacingMultiple:1.15}); });
    // 노란 띠
    L.R(s,{x:M,y:6.2,w:W-2*M,h:0.44,fill:C.yellow50,line:null,radius:0.12});
    s.addText([{text:'답은 초안   ',options:{bold:true,color:'B7791F',fontSize:12.5,fontFace:L.FONT}},{text:'숫자와 약관 근거를 확인하고, 내 말투로 다듬어 발송',options:{bold:true,color:C.navy,fontSize:12.5,fontFace:L.FONT}}],{x:M+0.25,y:6.2,w:W-2*M-0.5,h:0.44,isTextBox:true,margin:0,valign:'middle'});
    L.caption(s,{x:M,y:6.7,w:W-2*M,text:'출처: MeAI 확정 화면 · 이전 판 「MeAI 활용 가이드북 · 영업가족 편」(2026.09) · [간편 분석]·[용어] 자세히는 PART 6',align:'left',size:9.5});
  }});

  // ---- 8-4 이렇게는 묻지 않기 (방송판 20장) ----
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 묻지 말 것',title:'이렇게는 묻지 않기',sub:'답도 나빠지고, 규정에도 어긋남',pageNo:no});
    const gap = 0.14, cw = (W-2*M-gap)/2, ch = 1.45;
    const items = [
      ['개인정보를 넣는 질문','“김OO(연락처) 고객 보장분석”','맞춤대화에선 “이 고객”이라고만'],
      ['여러 질문을 한 번에','“보장분석하고 화법도 만들고 카톡도 써줘”','하나씩 이어서 묻기 · 고객·주제가 바뀌면 [새로 대화하기]'],
      ['답을 그대로 고객에게','답변 복사 → 바로 카톡 전송','숫자 · 약관 근거를 확인하고 내 말로'],
      ['단정을 강요하는 질문','“무조건 가입 가능하다고 말해줘”','“가능성과 확인할 조건을 알려줘”'],
    ];
    items.forEach((it,i)=>{ const x = M+(i%2)*(cw+gap), y = 1.85+Math.floor(i/2)*(ch+0.12);
      L.R(s,{x,y,w:cw,h:ch,fill:C.white,line:C.g200,radius:0.14,shadow:true});
      L.badge(s,{x:x+0.22,y:y+0.15,n:i+1,d:0.3});
      L.T(s,it[0],{x:x+0.62,y:y+0.12,w:cw-0.8,h:0.36,fontSize:14,bold:true,color:C.navy,valign:'middle'});
      s.addText([{text:'✕  ',options:{bold:true,color:C.red,fontSize:12.5,fontFace:L.FONT}},{text:it[1],options:{color:C.g600,fontSize:12,fontFace:L.FONT}}],{x:x+0.62,y:y+0.52,w:cw-0.8,h:0.3,isTextBox:true,margin:0,valign:'middle'});
      s.addText([{text:'○  ',options:{bold:true,color:C.green,fontSize:12.5,fontFace:L.FONT}},{text:it[2],options:{bold:true,color:C.navy,fontSize:12.5,fontFace:L.FONT}}],{x:x+0.62,y:y+0.84,w:cw-0.8,h:0.3,isTextBox:true,margin:0,valign:'middle'});
      if (i===0){ const gp = L.img(s,HERO('bc2_privacy_line'),{x:x+0.62,y:y+1.12,w:cw-0.9,h:0.26,valign:'middle',align:'left',round:false,shadow:false}); box(s,gp,4,4,826,51,{color:C.red,width:1.25,radius:0.02}); }
    });
    // 입력창 아래 안내문
    const dy = 4.98;
    L.T(s,'입력창 아래 안내문 (화면 그대로)',{x:M,y:dy,w:6,h:0.26,fontSize:10.5,bold:true,color:C.g600,valign:'middle'});
    const gd = L.img(s,HERO('bc2_disclaimer'),{x:M,y:dy+0.3,w:W-2*M-0.5,h:0.62,valign:'top',align:'left',round:false,shadow:false});
    ul(s,gd,585,1082,102,C.red,1.75);
    // 함께 지킬 약속
    const by = 6.08, bh = 0.48;
    L.R(s,{x:M,y:by,w:W-2*M,h:bh,fill:C.g100,line:null,radius:0.12});
    const cwid = L.chip(s,{x:M+0.15,y:by+0.1,text:'함께 지킬 약속',fill:C.navy,color:'FFFFFF',size:10.5,h:0.28});
    L.T(s,'동의 없으면 보지 않기 · 자료 외부 반출 금지 · 미검증 책임은 사용자에게',{x:M+0.35+cwid,y:by,w:W-2*M-cwid-0.5,h:bh,fontSize:12,bold:true,color:C.navy,valign:'middle'});
    L.caption(s,{x:M,y:6.64,w:W-2*M,text:'출처: 이전 판 「MeAI 활용 가이드북 · 영업가족 편」(2026.09) · MeAI 화면 안내문 · 다섯 가지 약속은 PART 9',align:'left',size:10});
  }});

  // ---- 8-5 첫 말 · 첫 질문 짝 (방송판 22장) ----
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 8 · 첫 말 · 첫 질문',title:'고객에게 첫 말, MeAI에게 첫 질문',sub:'오늘부터 시작하는 손쉬운 영업 타겟 탐색 · 카드가 달라도 짝은 같음',pageNo:no});
    const cw = [2.95,5.2,3.78], gx = 0.1, xs = [M, M+cw[0]+gx, M+cw[0]+cw[1]+2*gx];
    ['상황','고객에게 첫 말','MeAI에게 첫 질문'].forEach((t,i)=>{ L.R(s,{x:xs[i],y:1.88,w:cw[i],h:0.36,fill:C.g100,line:null,radius:0.1}); L.T(s,t,{x:xs[i]+0.15,y:1.88,w:cw[i]-0.2,h:0.36,fontSize:12,bold:true,color:C.g700,valign:'middle'}); });
    const rows = [
      {th:HERO('fix_reco3_card1'),bx:[45,572,266,620],title:'상령일 2주 전',desc:'사전조회동의 만료',chip:'사전조회동의 필요',
       first:'“고객님, 2주 뒤 보험 나이가 올라가요.\n그 전에 점검하려고 사전조회동의 알림톡 보내요.”',qtag:'동의 반영 뒤',q:'상령일 전에 암진단비를 늘려야 하는\n이유를 쉽게 설명해줘'},
      {th:HERO('reco1_card2'),bx:[45,522,284,568],title:'동의 만료 임박',desc:'이달 말 만료',
       first:'“고객님, 이달 말 동의가 만료돼 연장 부탁드려요.\n새로 나온 보장도 봐 드릴게요.”',q:'최근 신담보 기준으로\n이 고객 보장의 빈 곳을 알려줘'},
      {th:HERO('bc2_groups_opp'),bx:[16,240,510,340],title:'생일 임박 그룹',desc:'고객찾기 · 영업 기회 탭',ftag:'화면 안내 → 내 말로 풀기',
       first:'화면 안내: 축하 인사로 대화를 열고 자연스럽게\n보장 점검으로 이어가기 좋은 시점입니다.',qtag:'파란 일반대화 추천 질문(틀)',q:'#생일 임박, #나이대, #고객유형 —\n… 안내 문자 문안을 작성해줘 …',qfill:C.blue50},
    ];
    rows.forEach((r,i)=>{ const y = 2.32+i*1.18, h = 1.1;
      [0,1,2].forEach(j=>L.R(s,{x:xs[j],y,w:cw[j],h,fill:C.white,line:C.g200,radius:0.12}));
      const g = L.img(s,r.th,{x:xs[0]+0.1,y:y+0.07,w:0.95,h:0.96,valign:'middle',align:'center',shadow:false,round:false});
      box(s,g,r.bx[0],r.bx[1],r.bx[2],r.bx[3],{color:C.red,width:1.25,radius:0.01});
      L.badge(s,{x:xs[0]-0.1,y:y-0.1,n:i+1,d:0.3});
      L.T(s,r.title,{x:xs[0]+1.12,y:y+0.1,w:cw[0]-1.2,h:0.34,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,r.desc,{x:xs[0]+1.12,y:y+0.45,w:cw[0]-1.2,h:0.28,fontSize:10.5,color:C.g600,valign:'middle'});
      if (r.chip) L.chip(s,{x:xs[0]+1.12,y:y+0.76,text:r.chip,fill:C.red50,color:C.red,size:10,h:0.26});
      if (r.ftag){ L.chip(s,{x:xs[1]+0.15,y:y+0.1,text:r.ftag,fill:C.g100,color:C.g700,size:10,h:0.26});
        L.T(s,r.first,{x:xs[1]+0.15,y:y+0.42,w:cw[1]-0.3,h:0.6,fontSize:12,color:C.g700,valign:'top',lineSpacingMultiple:1.12}); }
      else L.T(s,r.first,{x:xs[1]+0.15,y,w:cw[1]-0.3,h,fontSize:13,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.15});
      let qy = y+0.1, qh = h-0.2;
      if (r.qtag){ L.T(s,r.qtag,{x:xs[2]+0.15,y:y+0.06,w:cw[2]-0.3,h:0.24,fontSize:10,bold:true,color:C.blue,valign:'middle'}); qy = y+0.33; qh = h-0.42; }
      L.R(s,{x:xs[2]+0.12,y:qy,w:cw[2]-0.24,h:qh,fill:r.qfill||C.white,line:C.blue,lw:1,radius:0.1});
      L.T(s,r.q,{x:xs[2]+0.26,y:qy,w:cw[2]-0.45,h:qh,fontSize:12,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.1}); });
    L.R(s,{x:M,y:5.94,w:W-2*M,h:0.52,fill:C.navy,line:null,radius:0.14});
    s.addText([{text:'기억할 것   ',options:{bold:true,color:C.blue100,fontSize:13,fontFace:L.FONT}},{text:'카드 문장은 고객에게 첫 말, 추천 질문은 MeAI에게 첫 질문.',options:{bold:true,color:'FFFFFF',fontSize:14.5,fontFace:L.FONT}}],{x:M+0.3,y:5.94,w:W-2*M-0.6,h:0.52,isTextBox:true,margin:0,valign:'middle'});
    L.caption(s,{x:M,y:6.54,w:W-2*M,text:'※ 1번 김민수 · 2번 윤태기 고객 카드(이름·숫자는 예시) · 2번 빨간 네모 = 사전조회동의 D-90(이달 말 만료되는 가입설계동의와 별개) · 출처: MeAI 확정 화면 · 자세한 흐름: 1번 PART 7 시나리오 3, 2번 시나리오 2',align:'left',size:10});
  }});
};
