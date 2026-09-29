module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG, LEG } = ctx;
  const capUnder = (s,g,text,o={})=> L.caption(s,Object.assign({x:g.x,y:g.y+g.h+0.03,w:g.w,text,size:10},o));
  S.push({ part:'06', fn:(pres,no)=> L.divider(pres,{num:'06',title:'대화 이어가기\n일반대화 · 맞춤대화와 새 기능',sub:'대문에서 들어온 대화 화면과 새 기능을 익혀요.',learn:['두 가지 대화와 화면 구성','NEW 용어 설명 · 모드 변경','꼬리질문 · 요약 리포트','모바일에서 들어가기'],pageNo:no}) });
  // 6-1 두 가지 대화
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 두 가지 대화',title:'일반대화 vs 맞춤대화',sub:'고객을 정하지 않으면 일반대화, 정하면 맞춤대화예요.',pageNo:no});
    const col=(x,kicker,title,items,entry,accent,fill)=>{
      L.R(s,{x,y:1.85,w:5.95,h:4.3,fill,line:null,radius:0.16});
      L.T(s,kicker,{x:x+0.4,y:2.1,w:5.2,h:0.3,fontSize:11.5,bold:true,color:accent});
      L.T(s,title,{x:x+0.4,y:2.42,w:5.2,h:0.55,fontSize:20,bold:true,color:C.navy,valign:'middle'});
      items.forEach((t,i)=>{ L.T(s,'✓',{x:x+0.4,y:3.12+i*0.47,w:0.35,h:0.4,fontSize:13,bold:true,color:accent,valign:'middle'}); L.T(s,t,{x:x+0.8,y:3.12+i*0.47,w:4.8,h:0.4,fontSize:13.5,color:C.g800,valign:'middle'}); });
      L.T(s,'들어가는 곳',{x:x+0.4,y:5.08,w:5.2,h:0.28,fontSize:11,bold:true,color:C.g500});
      L.T(s,entry,{x:x+0.4,y:5.38,w:5.2,h:0.6,fontSize:11.5,color:C.g700,valign:'top',lineSpacingMultiple:1.25});
    };
    col(M,'일반대화','무엇이든 물어보는 창',['상품·특약 개념 질문','자사·타사 보장 비교','고객 설득 화법 만들기','약관 지식 확인'],'대문 [일반대화] 카드 · 모바일 [MeAI 일반대화]\n영업포탈 CRM 리스트 [MeAI 일반대화] (10/2부터)',C.blue,C.blue50);
    col(M+6.18,'맞춤대화','이 고객에게 무엇을 제안할까',['고객 선택 → 보장분석','부족 보장 · 제안 우선순위','상세설계 · 가계약 요청','요약 리포트 → 카카오톡'],'대문 [맞춤대화] 카드 · 고객찾기 · 모바일 [MeAI]\n영업포탈 CRM 리스트 [MeAI 맞춤대화] (10/2부터)',C.red,C.red50);
    L.note(s,{x:M,y:6.3,w:W-2*M,h:0.6,label:'',text:'고객을 만나기 전에는 꼭 맞춤대화로 준비하세요.',tone:'dark',size:12.5});
  }});
  // 6-2 PC 화면 구성
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · PC 맞춤대화 화면',title:'메뉴·대화·입력창, 세 덩어리예요',pageNo:no});
    const g = L.img(s,HERO('term_pc_full'),{x:M,y:1.5,w:8.75,h:5.45,valign:'top',align:'left'});
    const clip={x:0,y:0};
    L.pin(s,g,272,155,1,{clip}); L.pin(s,g,272,305,2,{clip}); L.pin(s,g,272,480,3,{clip}); L.pin(s,g,150,788,4,{clip}); L.pin(s,g,1012,27,5,{clip}); L.pin(s,g,456,215,6,{clip}); L.pin(s,g,456,500,7,{clip}); L.pin(s,g,1270,726,8,{clip}); L.pin(s,g,456,800,9,{clip});
    // 번호 간격을 일정하게(설명 없는 ④·⑨도 한 칸을 차지), ①만 설명이 두 줄
    const evenList=(x,y,w,pitch,items)=>{ let cy=y; items.forEach(it=>{ L.badge(s,{x,y:cy+0.02,n:it.n,d:0.3}); L.T(s,it.title,{x:x+0.42,y:cy,w:w-0.42,h:0.32,fontSize:13,bold:true,color:C.navy,valign:'middle'}); const nl=it.desc?it.desc.split('\n').length:1; if(it.desc) L.T(s,it.desc,{x:x+0.42,y:cy+0.33,w:w-0.42,h:nl*0.21+0.04,fontSize:11,color:C.g600,lineSpacingMultiple:1.1}); cy += pitch + (nl-1)*0.21; }); };
    evenList(9.55,1.5,3.18,0.6,[
      {n:1,title:'담당 고객',desc:"사전조회동의 남은 일수\n(화면엔 '보장분석 동의')"},
      {n:2,title:'약관 검색·사용 가이드',desc:'전사 약관 원문과 화면 안내'},
      {n:3,title:'대화 이력',desc:'월별 목록, 누르면 이어가요'},
      {n:4,title:'새로 대화하기'},
      {n:5,title:'상단 버튼 3개',desc:'보장 분석 · 사용중인 정보 수정 · 요약 리포트'},
      {n:6,title:'내 질문',desc:'복사·편집·저장 아이콘'},
      {n:7,title:'MeAI 답변',desc:'잘 갖춰진 것 → 비어 있는 것 → 할 일'},
      {n:8,title:'NEW [용어] 버튼',desc:'입력창 오른쪽 위'},
      {n:9,title:'입력창'}]);
  }});
  // 6-2b 맞춤대화 시작 화면
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 맞춤대화 시작 화면',title:'먼저 고객 정보와 상품을 정해요',pageNo:no});
    // 위 = 담당 고객 + 고객 정보 입력 카드(CSS y12~532), 아래 = 총 보험료~첫 상품 줄(CSS x424~, y688~1109)을 크게
    const gt = L.img(s,HERO('fix_custom_top'),{x:M,y:1.5,w:5.82,h:2.45,valign:'top',align:'left'});
    const gb = L.img(s,HERO('fix_custom_bottom'),{x:M,y:gt.y+gt.h+0.12,w:5.82,h:6.95-(gt.y+gt.h+0.12),valign:'top',align:'left'});
    const ot={clip:{x:0,y:12},dsf:2}, ob={clip:{x:424,y:688},dsf:2};
    L.pin(s,gt,218,157,1,ot); L.pin(s,gt,470,81,2,ot); L.pin(s,gt,470,290,3,ot); L.pin(s,gt,470,470,4,ot);
    L.pin(s,gb,457,760,5,ob); L.pin(s,gb,818,758,6,ob); L.pin(s,gb,457,911,7,ob); L.pin(s,gb,457,983,8,ob);
    const lx = M+5.82+0.4, lw = 12.73-lx;
    L.numList(s,{x:lx,y:1.5,w:lw,gap:0.02,titleSize:13.5,descSize:11.5,items:[
      {n:1,title:'담당 고객',desc:'고객이 정해진 채로 열렸다는 표시예요.'},
      {n:2,title:'고객 정보 입력',desc:'미리 넣으면 고객 맥락을 살려 답해요.'},
      {n:3,title:'다섯 칸, 아는 것만',desc:'병력·가족력이 핵심, 이름·연락처는 넣지 않아요.'},
      {n:4,title:'[입력 완료]로 반영',desc:'비울 땐 [입력하지 않고 넘어가기].'}]});
    L.numList(s,{x:lx,y:gb.y+0.08,w:lw,gap:0.1,titleSize:13.5,descSize:11.5,items:[
      {n:5,title:'선택 계약 총 보험료',desc:'"지금 매달 이만큼 내고 계세요"로 시작해요.'},
      {n:6,title:'약관DB 확보 표시',desc:'미확보 상품은 답이 부정확할 수 있어요.'},
      {n:7,title:'담보별로 거르기',desc:'암 · 뇌/심장 · 치료비 등 버튼으로 골라요.'},
      {n:8,title:'상품 전체 선택',desc:'관계없는 계약은 체크를 풀면 분석에서 빠져요.'},
    ]});
  }});
  // 6-3 답변 읽는 법
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 답변 읽는 법',title:'답변은 이 순서로 와요',sub:'잘 갖춰진 것 → 비어 있는 것 → 이제 할 일',pageNo:no});
    // term/36_pc_tall_full_off(dsf 2)에서 CSS x420 부터 다시 자름 → 글자(x490) 왼쪽에 핀 자리
    const g1 = L.img(s,HERO('fix_answer_top'),{x:M,y:1.85,w:5.95,h:4.35,valign:'top',align:'left'});
    const g2 = L.img(s,HERO('fix_answer_bottom'),{x:M+6.2,y:1.85,w:5.95,h:4.35,valign:'top',align:'left'});
    const o1={clip:{x:420,y:75},dsf:2,d:0.3}, o2={clip:{x:420,y:683},dsf:2,d:0.3};
    // ① 굵은 결론 줄 ② 잘 갖춘 것 제목 ③ 비어 있는 것 제목 ④ 표의 '미가입' 두 줄 바로 옆 ⑤ '이제 하면 되는 일' 제목 ⑥ 용어 설명·아이콘 줄
    L.pin(s,g1,461,321,1,o1); L.pin(s,g1,461,430,2,o1); L.pin(s,g1,461,619,3,o1); L.pin(s,g2,1090,808,4,o2); L.pin(s,g2,461,1001,5,o2); L.pin(s,g2,461,1162,6,o2);
    L.pinStrip(s,{x:M,y:6.32,w:W-2*M,cols:6,rowH:0.6,size:11,items:[{n:1,text:'한 줄 결론 = 상담 주제'},{n:2,text:'잘 갖춘 것 → 안심부터'},{n:3,text:'비어 있는 것 → 제안 주제'},{n:4,text:'"미가입" 줄 = 제안 포인트'},{n:5,text:'이제 할 일 → 다음 행동'},{n:6,text:'[용어 설명 N] · 복사·출처'}]});
  }});
  // 6-4 용어 설명 PC
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 용어 설명 (PC)',title:'[용어] 버튼 하나로 뜻이 풀려요',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    const a = L.img(s,HERO('term_pc_input_z'),{x:M,y:1.5,w:5.9,h:1.55,valign:'top',align:'left'}); capUnder(s,a,'입력창 오른쪽 위 [용어] 버튼');
    const b = L.img(s,HERO('fix_term_on'),{x:M,y:3.45,w:5.9,h:3.2,valign:'top',align:'left'}); capUnder(s,b,'켜면 어려운 말에 표시가 붙어요');
    const c = L.img(s,AG('term','14_pc_glossary6_open'),{x:6.75,y:1.5,w:5.98,h:3.6,valign:'top',align:'center'}); capUnder(s,c,'답변 끝 [용어 설명 6] · 뜻을 한 번에');
    const d = L.img(s,HERO('fix_term_tooltip'),{x:6.75,y:5.5,w:2.6,h:1.15,valign:'top',align:'left'}); capUnder(s,d,'용어를 누르면 뜻이 떠요');
    L.note(s,{x:d.x+d.w+0.3,y:5.5,w:12.73-(d.x+d.w+0.3),h:1.15,label:'현장에서',text:'뜻풀이는 고객 눈높이 문장이라 그대로 읽어 주세요.',tone:'blue',size:12});
  }});
  // 6-5 용어 설명 모바일
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 용어 설명 (모바일)',title:'모바일은 오른쪽 아래 [용어]',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    [[HERO('term_mo_phone'),'답변 화면 · 오른쪽 아래 [용어]'],[HERO('term_mo_phone_2'),'[용어]를 켜면 용어에 표시'],[AG('term','70_mo_glossary6_open'),'답변 끝 [용어 설명 6] 목록']].forEach(([f,t],i)=>{ const x=M+i*2.95; L.phone(s,f,{x,y:1.5,w:2.75,h:5.1}); L.caption(s,{x,y:6.64,w:2.75,text:t,size:10}); });
    L.numList(s,{x:9.5,y:1.75,w:3.23,gap:0.24,titleSize:14,descSize:12,items:[
      {n:1,title:'위치만 달라요',desc:'PC는 입력창 오른쪽 위,\n모바일은 오른쪽 아래.'},
      {n:2,title:'켜고 끄기',desc:'한 번 누르면 표시, 다시 누르면 원래대로.'},
      {n:3,title:'목록으로 보기',desc:'답변 끝 [용어 설명 N]에서 한 번에.'},
      {n:4,title:'고객에게 그대로',desc:'뜻풀이를 그대로 읽어 주세요.'}]});
  }});
  // 6-6 모드 변경 PC
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 모드 변경 (PC)',title:'질문마다 간편·상세를 골라요',sub:'고객 앞에서는 간편, 약관을 따질 때는 상세예요.',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    const g = L.img(s,HERO('mode_pc_dropdown_z'),{x:M,y:1.85,w:7.5,h:4.5,valign:'top',align:'left'}); capUnder(s,g,'[간편 분석]을 누르면 두 가지가 펼쳐져요');
    const rx = 8.35, rw = 12.73-rx;
    L.card(s,{x:rx,y:1.85,w:rw,h:1.6,kicker:'고객 상담 · 직관적 검토용',title:'간편 분석',desc:'처음 설정이에요. 고객과 함께 보는 화면, 첫 상담에 맞아요.',titleSize:16,descSize:12});
    L.card(s,{x:rx,y:3.6,w:rw,h:1.6,kicker:'약관 · 담보 정밀 검토용',title:'상세 분석',desc:'약관 근거를 확인하거나 자사·타사 담보를 숫자로 비교할 때.',titleSize:16,descSize:12,accent:C.navy});
    L.note(s,{x:rx,y:5.35,w:rw,h:0.85,label:'바꾸면',text:'대화에 아래 안내줄이 붙고, 다음 질문부터 그 모드로 답해요.',tone:'grey',size:11.5});
    L.img(s,HERO('fix_mode_notice'),{x:rx,y:6.3,w:rw,h:0.55,valign:'top',align:'left'});
  }});
  // 6-7 모드 변경 모바일
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 모드 변경 (모바일)',title:'모바일도 입력창 아래에 있어요',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    [[HERO('mode_mo_phone'),'입력창 아래 [간편 분석] · [상품 선택]'],[HERO('mode_mo_phone_2'),'"분석 모드" 선택창 · 간편 / 상세'],[AG('mode','47_mo_mode_detailed'),'고른 뒤 · 버튼과 안내줄이 바뀌어요']].forEach(([f,t],i)=>{ const x=M+i*2.95; L.phone(s,f,{x,y:1.5,w:2.75,h:5.1}); L.caption(s,{x,y:6.64,w:2.75,text:t,size:10}); });
    L.numList(s,{x:9.5,y:1.9,w:3.23,gap:0.3,titleSize:14,descSize:12,items:[
      {n:1,title:'버튼을 누르면',desc:'아래에서 "분석 모드" 선택창이 올라와요.'},
      {n:2,title:'고르면 끝',desc:'선택창이 닫히고 버튼 이름이 바뀌어요.'},
      {n:3,title:'질문마다 바꿔도 돼요',desc:'고객 앞에서는 간편, 약관을 따질 땐 상세.'}]});
  }});
  // 6-8 꼬리질문
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 답변 아래',title:'꼬리질문 버튼으로 이어가세요',sub:'타이핑 없이 버튼만 누르면 대화가 깊어져요.',pageNo:no});
    const g = L.img(s,HERO('mode_pc_bottom2_z'),{x:M,y:1.85,w:7.4,h:5.0,valign:'top',align:'left'});
    const clip={x:480,y:340}, o={clip,dsf:3};
    L.pin(s,g,470,367,1,o); L.pin(s,g,470,494,2,o); L.pin(s,g,470,638,3,o); L.pin(s,g,470,750,4,o); L.pin(s,g,470,800,5,o);
    const rx = 8.2, rw = 12.73-rx;
    L.numList(s,{x:rx,y:1.85,w:rw,gap:0.06,titleSize:13.5,descSize:11.5,items:[
      {n:1,title:'답변 아래 아이콘',desc:'복사 · 출처 · 좋아요 · 싫어요'},
      {n:2,title:'꼬리질문 3개',desc:'누르면 그 질문이 바로 전송돼요.'},
      {n:3,title:'질문 더보기',desc:'미리 만든 질문 모음에서 골라 써요.'},
      {n:4,title:'입력창',desc:'직접 쓰거나, 모바일은 마이크로 말해요.'},
      {n:5,title:'모드 · 상품 선택',desc:'간편/상세를 고르고 분석할 상품을 좁혀요.'}]});
    const by = 5.3, bh = 1.6;
    L.R(s,{x:rx,y:by,w:rw,h:bh,fill:C.navy,line:null,radius:0.14});
    L.T(s,'왜 중요할까요?',{x:rx+0.3,y:by+0.18,w:rw-0.6,h:0.26,fontSize:11,bold:true,color:C.blue100});
    L.T(s,'2.3배',{x:rx+0.3,y:by+0.46,w:1.45,h:0.7,fontSize:34,bold:true,color:'FFFFFF',valign:'middle'});
    L.T(s,'3개 이상 이어 쓴 분의 가계약\n(질문 1개만 쓴 분 대비)',{x:rx+1.8,y:by+0.46,w:rw-2.0,h:0.7,fontSize:11,color:'FFFFFF',valign:'middle',lineSpacingMultiple:1.25});
    L.T(s,'데이터분석팀 「MeAI 효과 분석」 2026.08',{x:rx+0.3,y:by+1.2,w:rw-0.6,h:0.26,fontSize:9.5,color:C.g400,valign:'middle'});
  }});
  // 6-9 요약 리포트
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 요약 리포트',title:'요약 리포트는 네 단계로 보내요',sub:'핸드폰 하나로 발송까지 끝나요. PC는 오른쪽 위 [요약 리포트].',pageNo:no});
    const st=[['요약 생성','대화 화면 상단 [요약 생성]'],['선택 → 편집하기','넣을 답변만 체크, 내부용은 빼요'],['리포트 생성하기','카카오톡으로 링크가 전송돼요'],['알림톡 도착','[요약레포트 확인하기] · 열람 D+7일']];
    st.forEach((t,i)=>{ const x=M+i*3.08,w=2.9; const f = i<3 ? LEG('report_step'+(i+1)) : HERO('report_kakao_crop'); L.phone(s,f,{x,y:1.85,w,h:3.9,valign:i<3?'top':'middle'}); L.badge(s,{x,y:5.86,n:i+1,d:0.3}); L.T(s,t[0],{x:x+0.4,y:5.84,w:w-0.4,h:0.34,fontSize:13.5,bold:true,color:C.navy,valign:'middle'}); L.T(s,t[1],{x,y:6.19,w,h:0.3,fontSize:11.5,color:C.g600}); if(i<3) L.arrow(s,{x:x+w-0.08,y:3.55,w:0.35}); });
    L.note(s,{x:M,y:6.54,w:7.4,h:0.4,label:'보내기 전',text:'숫자·약관 근거·개인정보 확인. "AI로 생성된 보조자료" 표시가 붙어요.',tone:'yellow',size:11});
    L.caption(s,{x:8.2,y:6.6,w:12.73-8.2,text:'2026.06 실제 화면 · 이름은 가렸어요',align:'right',size:10});
  }});
  // 6-10 모바일 진입
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 모바일',title:'앱 홈 → 보장분석 → MeAI',sub:'모바일 대문·고객찾기·게시판은 PC 오픈 뒤 순차 적용 예정이에요.',pageNo:no});
    L.phone(s,LEG('mobile_app_home'),{x:M,y:1.85,w:2.4,h:4.75}); L.caption(s,{x:M,y:6.64,w:2.4,text:'① 앱 홈 · [보장분석]',size:10});
    L.phone(s,HERO('fix_mobile_customer_list'),{x:M+2.55,y:1.85,w:2.4,h:4.75}); L.caption(s,{x:M+2.55,y:6.64,w:2.4,text:'② 상단 버튼 · ③ 카드 [MeAI]',size:10});
    L.phone(s,AG('mode','55_mo_menu_drawer'),{x:M+5.1,y:1.85,w:2.3,h:4.75}); L.caption(s,{x:M+5.1,y:6.64,w:2.3,text:'④ 대화 화면 ≡ 메뉴',size:10});
    const rx = 8.2, rw = 12.73-rx;
    L.numList(s,{x:rx,y:1.85,w:rw,gap:0.14,titleSize:13.5,descSize:11.5,items:[
      {n:1,title:'[보장분석] 터치',desc:'앱 홈 아이콘 묶음의 첫 번째예요.'},
      {n:2,title:'[MeAI 일반대화]',desc:'고객 목록 위, 무엇이든 묻는 창이에요.'},
      {n:3,title:'카드의 [MeAI]',desc:'누르면 그 고객 맞춤대화가 열려요.'},
      {n:4,title:'≡ 메뉴',desc:'약관 검색 · 사용 가이드 · 월별 대화 목록'}]});
    L.note(s,{x:rx,y:4.95,w:rw,h:0.85,label:'공통',text:'대화 이력·저장한 나의 질문은 PC와 모바일이 같아요.',tone:'blue',size:11.5});
    L.note(s,{x:rx,y:5.95,w:rw,h:0.9,label:'TIP',text:'고객 목록 위 "오늘 보장분석 활용"에서\n일일 300회 한도를 확인해요.',tone:'grey',size:11.5});
  }});
};
