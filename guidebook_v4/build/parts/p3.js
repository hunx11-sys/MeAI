module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  S.push({ part:'03', fn:(pres,no)=> L.divider(pres,{num:'03',title:'맞춤대화로 가는 두 길\n고객 검색 팝업과 추천 카드',sub:'이름을 알면 검색 팝업, 고민이면 추천 카드.',learn:['길 1 · 고객 검색 팝업','길 2 · 추천 카드 → 고객찾기','D-n이면 바로, 회색이면 동의부터'],pageNo:no}) });
  // 3-1 팝업 hero
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 길 1',title:'이름을 알면, 고객 검색 팝업으로',sub:'대문의 검은 카드를 누르면 떠요. 고객을 고르면 바로 시작.',pageNo:no});
    const g = L.img(s,HERO('gate_search'),{x:M,y:1.85,w:5.0,h:5.05,valign:'top',align:'left'});
    const clip={x:360,y:40};
    L.pin(s,g,568,102,1,{clip}); L.pin(s,g,690,210,2,{clip}); L.pin(s,g,510,283,3,{clip}); L.pin(s,g,725,332,4,{clip}); L.pin(s,g,968,281,5,{clip}); L.pin(s,g,528,1015,6,{clip}); L.pin(s,g,978,96,7,{clip});
    L.numList(s,{x:4.75,y:1.85,w:7.98,gap:0.1,titleSize:14,descSize:12,items:[
      {n:1,title:'고객 검색',desc:'"고객을 선택하면 맞춤대화를 시작합니다"'},
      {n:2,title:'검색창',desc:'한 글자만 넣어도, 담당자 이름으로도 찾아져요.'},
      {n:3,title:'고객 61명',desc:'사전조회 동의가 유효한 고객만, 가나다순.'},
      {n:4,title:'사전조회동의 D-n',desc:'만료까지 남은 날. 오늘 철회한 고객은 회색.'},
      {n:5,title:'[맞춤대화] 버튼',desc:'누르면 팝업이 닫히고 그 고객의 맞춤대화가 열려요.'},
      {n:6,title:'페이지',desc:'한 쪽에 10명. 이름으로 찾으면 넘길 일이 거의 없어요.'},
      {n:7,title:'닫기(X)',desc:'대문으로 돌아와요. 검색어는 초기화.'},
    ]});
  }});
  // 3-2 검색
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 이름으로 찾기',title:'한 글자만 넣어도 목록이 좁혀져요',sub:'성만 알아도 괜찮아요. 담당자 이름으로도 찾아요.',pageNo:no});
    const gk = L.img(s,HERO('gate_search_kim'),{x:M,y:1.85,w:4.5,h:4.75,valign:'top',align:'left'}); L.caption(s,{x:M,y:6.63,w:gk.w,text:'"김" 입력 → 김씨 고객 + 담당자 김OO',size:10});
    const ck={x:360,y:40};
    L.pin(s,gk,488,210,1,{clip:ck}); L.pin(s,gk,640,430,2,{clip:ck});
    L.numList(s,{x:4.45,y:1.85,w:8.28,gap:0.14,titleSize:14,descSize:12,items:[{n:1,title:'한 글자부터',desc:'"김"만 넣어도 김씨 고객이 모두 보여요. 즉시 걸러져요.'},{n:2,title:'이름이 같아도',desc:'나이·담당자가 함께 보여서 구분돼요.'}]});
    const gn = L.img(s,HERO('fix_noresult_popup'),{x:4.45,y:3.6,w:7.63,h:2.95,valign:'top',align:'left'}); L.caption(s,{x:4.45,y:6.6,w:gn.w,text:'없는 이름 → "조건에 맞는 고객이 없습니다"',size:10});
    L.pin(s,gn,125,338,3,{clip:{x:12,y:12}});
    L.numList(s,{x:gn.x+gn.w+0.35,y:3.6,w:W-M-(gn.x+gn.w+0.35),gap:0.1,titleSize:14,descSize:12,items:[{n:3,title:'결과가 없으면',desc:'"조건에 맞는 고객이 없습니다."\n등록·동의부터 확인해요.'}]});
  }});
  // 3-3 동의 상태
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 동의 상태',title:'D-n이면 바로, 회색이면 동의부터',sub:'만료된 고객은 목록에 없고, 오늘 철회한 고객은 회색.',pageNo:no});
    [['31_row_normal_zoom','동의 유효 · D-26 · [맞춤대화] 활성'],['33_row_d1_zoom','만료 하루 전 · D-1 · 아직 시작 가능'],['34_row_revoked_zoom','오늘 철회 · 회색 · [맞춤대화] 비활성']].forEach((r,i)=>{ const y=1.85+i*1.45; L.img(s,AG('gate020',r[0]),{x:M,y,w:8.0,h:1.0,valign:'top',align:'left'}); L.label(s,{x:M,y:y+0.98,w:8.0,text:r[1],size:11}); });
    L.note(s,{x:M,y:6.1,w:8.0,h:0.8,label:'만료된 고객은',text:'고객찾기 [사전동의 만료] 그룹이나 대문 [고객 동의]로 재동의 요청.',tone:'grey',size:11.5});
    L.note(s,{x:8.9,y:1.85,w:3.83,h:2.1,label:'왜 동의가 먼저인가요?',text:'\n맞춤대화는 보장 내역을 읽어요.\n동의는 약 15분 내외로 반영돼요.\n(게시판 공지)',tone:'blue',size:13.5});
    L.note(s,{x:8.9,y:4.15,w:3.83,h:2.75,label:'현장 화법',text:'\n"보장을 정확히 보고\n말씀드리려면 동의가 필요해요.\n알림톡으로 금방 끝나요."',tone:'dark',size:14.5});
  }});
  // 3-4 길 2
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 길 2',title:'고민이면 추천 카드, 클릭 두 번',sub:'고객 타겟팅이 끝난 상태로 맞춤대화 화면에 들어가요.',pageNo:no});
    const st=[['1','대문 · 추천 카드','[MeAI 고객찾기에서 열기]를 눌러요.',HERO('gate_card_z')],['2','고객찾기 · 펼친 카드','한눈에 보기 6칸과 태그를 확인해요.',HERO('fix_find_card_choi')],['3','[이 고객으로 맞춤대화 시작]','오른쪽 패널 · 추천 질문을 그대로.',HERO('find_right_choi')],['4','맞춤대화 화면','고객이 정해진 채로 열려요.\n※ 예시 화면이라 이름이 달라요',HERO('fix_custom_q_tight')]];
    st.forEach((t,i)=>{ const x=M+i*3.08, w=2.9; L.img(s,t[3],{x,y:1.85,w,h:3.4,valign:'middle'}); L.badge(s,{x,y:5.37,n:t[0],d:0.3}); L.T(s,t[1],{x:x+0.4,y:5.35,w:w-0.4,h:0.55,fontSize:13,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15}); L.T(s,t[2],{x,y:5.85,w,h:0.55,fontSize:12,color:C.g600,lineSpacingMultiple:1.3}); if(i<3) L.arrow(s,{x:x+w-0.08,y:3.3,w:0.35}); });
    L.note(s,{x:M,y:6.5,w:W-2*M,h:0.42,label:'두 길의 차이',text:'길 1은 "이 고객"이 정해진 날, 길 2는 "오늘 한 명"인 날. 도착은 같아요.',tone:'grey',size:11.5});
  }});
};
