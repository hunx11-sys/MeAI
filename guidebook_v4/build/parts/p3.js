module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  S.push({ part:'03', fn:(pres,no)=> L.divider(pres,{num:'03',title:'맞춤대화로 가는 두 길\n고객 검색 팝업과 추천 카드',sub:'이름을 알면 검색 팝업, 누구를 만날지 고민이면 추천 카드. 어느 길이든 고객이 정해진 상태로 대화가 열려요.',learn:['길 1 · [맞춤대화] 카드 → 고객 검색 팝업 → [맞춤대화]','길 2 · 추천 카드 → 고객찾기 → [이 고객으로 맞춤대화 시작]','D-n이 보이면 바로, 회색이면 동의부터'],pageNo:no}) });
  // 3-1 팝업 hero
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 길 1',title:'이름을 알면, [맞춤대화] 카드 → 고객 검색 팝업',sub:'대문의 검은 카드를 누르면 팝업이 떠요. 고객을 고르는 순간 그 고객의 맞춤대화가 시작돼요.',pageNo:no});
    const g = L.img(s,HERO('gate_search'),{x:M,y:1.85,w:5.0,h:5.0,valign:'top',align:'left'});
    const clip={x:350,y:30};
    L.pin(s,g,560,105,1,{clip}); L.pin(s,g,975,210,2,{clip}); L.pin(s,g,505,283,3,{clip}); L.pin(s,g,745,332,4,{clip}); L.pin(s,g,1058,332,5,{clip}); L.pin(s,g,900,810,6,{clip}); L.pin(s,g,1032,145,7,{clip});
    L.numList(s,{x:6.0,y:1.85,w:6.7,gap:0.08,titleSize:12,descSize:10,items:[
      {n:1,title:'고객 검색',desc:'"고객을 선택하면 맞춤대화를 시작합니다". 팝업 제목 아래 안내 그대로예요.'},
      {n:2,title:'검색창',desc:'이름을 입력하면 목록이 즉시 좁혀져요. 한 글자만 넣어도 되고, 담당자 이름으로도 찾아져요. (예: 홍길동)'},
      {n:3,title:'고객 61명',desc:'사전조회 동의가 유효한 내 고객 수. 이름 가나다순이고, 담당자가 여럿이면 담당마다 한 줄씩 보여요.'},
      {n:4,title:'사전조회동의 D-n',desc:'동의 만료까지 남은 날. D-1까지는 바로 시작할 수 있어요. 오늘 철회한 고객은 회색으로 표시돼요.'},
      {n:5,title:'[맞춤대화] 버튼',desc:'누르면 팝업이 닫히고 그 고객의 맞춤대화 화면으로 들어가요. 목록 아래 안내: "고객을 선택하면 팝업이 닫히고 해당 고객의 맞춤대화가 시작됩니다."'},
      {n:6,title:'페이지',desc:'한 페이지에 10명. 이름으로 검색하면 페이지를 넘길 일이 거의 없어요.'},
      {n:7,title:'닫기(X)',desc:'대문으로 돌아와요. 검색어와 페이지는 초기화돼요.'},
    ]});
  }});
  // 3-2 검색
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 이름으로 찾기',title:'이름 한 글자만 넣어도 목록이 좁혀져요',sub:'성만 알아도, 이름 일부만 알아도 괜찮아요. 담당자 이름을 넣으면 그 담당자의 고객이 나와요.',pageNo:no});
    L.img(s,HERO('gate_search_kim'),{x:M,y:1.85,w:4.6,h:4.6,valign:'top',align:'left'}); L.caption(s,{x:M,y:6.5,w:4.6,text:'"김"을 입력한 상태 · 김씨 고객과 담당자가 김OO인 고객'});
    L.img(s,HERO('search_noresult_crop'),{x:5.4,y:1.85,w:4.6,h:4.6,valign:'top',align:'left'}); L.caption(s,{x:5.4,y:6.5,w:4.6,text:'없는 이름을 넣은 상태 · "조건에 맞는 고객이 없습니다"'});
    L.numList(s,{x:10.25,y:1.85,w:2.5,gap:0.12,titleSize:11.5,descSize:9.5,items:[{n:1,title:'한 글자부터',desc:'"김"만 넣어도 김씨 고객이 모두 보여요. 타이핑하는 즉시 걸러져요.'},{n:2,title:'이름이 같아도',desc:'나이·담당자가 함께 보여서 구분할 수 있어요.'},{n:3,title:'결과가 없으면',desc:'"조건에 맞는 고객이 없습니다. 다른 이름으로 찾아보세요." 등록됐는지, 동의가 있는지 먼저 확인해요.'},{n:4,title:'바로 시작',desc:'찾았으면 오른쪽 [맞춤대화]. 두 번 누를 일이 없어요.'}]});
  }});
  // 3-3 동의 상태
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 동의 상태',title:'D-n이 보이면 바로 시작, 회색이면 동의부터',sub:'팝업에는 사전조회 동의가 유효한 고객만 나와요. 만료된 고객은 목록에 없고, 오늘 철회한 고객은 회색으로 남아요.',pageNo:no});
    [['31_row_normal_zoom','동의 유효 · 사전조회동의 D-26 · [맞춤대화] 활성'],['33_row_d1_zoom','만료 하루 전 · D-1 · 아직 시작할 수 있어요'],['34_row_revoked_zoom','오늘 철회 · 회색 · [맞춤대화] 비활성']].forEach((r,i)=>{ const y=1.85+i*1.25; L.img(s,AG('gate020',r[0]),{x:M,y,w:7.5,h:0.9,valign:'top',align:'left'}); L.caption(s,{x:M,y:y+0.92,w:7.5,text:r[1],align:'left'}); });
    const rows=[['줄 모양','뜻','할 일'],['검은 글씨 · 사전조회동의 D-n','동의가 유효해요. n일 뒤 만료.','[맞춤대화]로 바로 시작. D-7 이하면 재동의도 함께 안내.'],['회색 · 사전조회동의 철회','고객이 오늘 동의를 철회했어요.','정보 확인이 막혀요. 새 동의 없이는 진행할 수 없어요.'],['목록에 없음 · 동의 만료','만료된 고객은 팝업에 나오지 않아요.','고객찾기 [사전동의 만료] 그룹이나 대문 [고객 동의]로 재동의 요청.']];
    L.table(s,{x:M,y:5.55,w:7.5,rows,colW:[2.3,2.2,3.0],size:9.3,rowH:0.28});
    L.note(s,{x:8.4,y:1.85,w:4.3,h:2.2,label:'왜 동의가 먼저인가요?',text:'맞춤대화는 고객의 보장 내역을 읽어서 답해요. 사전조회 동의가 있어야 그 내역을 볼 수 있어요. 동의는 준실시간(약 15분)으로 반영돼요(게시판 공지 기준).',tone:'blue',size:10.5});
    L.note(s,{x:8.4,y:4.2,w:4.3,h:2.6,label:'현장 화법',text:'"고객님 보장을 정확히 보고 말씀드리려면 사전조회 동의가 필요해요. 알림톡 보내드릴게요, 1분이면 끝나요." 동의는 상담의 시작이지, 절차가 아니에요. 재동의를 받으면 D-n이 다시 채워져요.',tone:'dark',size:10.5});
  }});
  // 3-4 길 2
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 3 · 길 2',title:'누구를 만날지 고민이면, 추천 카드 → 고객찾기 → 맞춤대화 시작',sub:'클릭 두 번이에요. 고객 타겟팅이 끝난 상태로 맞춤대화 화면에 들어가요.',pageNo:no});
    const st=[['1','대문 · 추천 카드','[MeAI 고객찾기에서 열기]를 눌러요.',HERO('gate_card_z')],['2','고객찾기 · 그 고객이 맨 위에 펼쳐져요','이 고객 한눈에 보기 6칸과 태그를 확인해요.',AG('gate010','25_find_from_card_choi')],['3','다음 행동 · [이 고객으로 맞춤대화 시작]','같은 고객의 오른쪽 패널. 추천 질문을 그대로 쓰면 돼요.',HERO('find_right_choi')],['4','맞춤대화 화면','고객이 정해진 채로 열려요. 정보 입력 → 상품 선택 → 질문.',HERO('custom_start_crop')]];
    st.forEach((t,i)=>{ const x=M+i*3.08, w=2.9; L.img(s,t[3],{x,y:1.85,w,h:3.4,valign:'middle'}); L.badge(s,{x,y:5.37,n:t[0],d:0.3}); L.T(s,t[1],{x:x+0.4,y:5.35,w:w-0.4,h:0.55,fontSize:11.5,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.15}); L.T(s,t[2],{x,y:5.95,w,h:0.6,fontSize:10,color:C.g600,lineSpacingMultiple:1.3}); if(i<3) L.arrow(s,{x:x+w-0.08,y:3.3,w:0.35}); });
    L.note(s,{x:M,y:6.55,w:W-2*M,h:0.42,label:'두 길의 차이',text:'길 1은 "이 고객"이 정해진 날, 길 2는 "누구든 오늘 한 명"인 날. 어느 길이든 도착하는 화면은 같아요.',tone:'grey',size:10});
  }});
};
