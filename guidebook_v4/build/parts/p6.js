module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG, LEG } = ctx;
  S.push({ part:'06', fn:(pres,no)=> L.divider(pres,{num:'06',title:'대화 이어가기\n일반대화 · 맞춤대화와 새 기능',sub:'대문에서 들어온 대화 화면이에요. 새로 추가되는 용어 설명과 모드 변경까지 함께 익혀요.',learn:['두 가지 대화의 차이 · PC 대화 화면 구성','NEW 용어 설명 · NEW 모드 변경(간편/상세) · 상품 선택','꼬리질문 · 질문 더보기 · 요약 리포트 → 카카오톡 · 모바일 진입'],pageNo:no}) });
  // 6-1 두 가지 대화
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 두 가지 대화',title:'일반대화와 맞춤대화, 두 가지만 구분하면 돼요',sub:'고객을 정하지 않고 묻는 대화와, 특정 고객의 보장분석을 옆에 두고 하는 대화예요.',pageNo:no});
    const col=(x,kicker,title,items,entry,accent,fill)=>{ L.R(s,{x,y:1.9,w:5.95,h:4.4,fill,line:null,radius:0.16}); L.T(s,kicker,{x:x+0.35,y:2.1,w:5.2,h:0.3,fontSize:10.5,bold:true,color:accent}); L.T(s,title,{x:x+0.35,y:2.42,w:5.2,h:0.45,fontSize:16,bold:true,color:C.navy,valign:'middle'}); items.forEach((t,i)=>{ L.T(s,'✓',{x:x+0.35,y:3.05+i*0.42,w:0.3,h:0.36,fontSize:11,bold:true,color:accent,valign:'middle'}); L.T(s,t,{x:x+0.7,y:3.05+i*0.42,w:4.9,h:0.36,fontSize:11.5,color:C.g800,valign:'middle'}); }); L.T(s,entry,{x:x+0.35,y:5.55,w:5.2,h:0.6,fontSize:10,color:C.g600,lineSpacingMultiple:1.3}); };
    col(M,'일반대화','무엇이든 물어보는 창',['상품·특약 개념 질문','자사·타사 보장 비교','고객 설득 화법 만들기','약관 지식 확인 · 여러 고객용 안내 문안'],'진입: 대문 [일반대화] 카드 · 고객찾기 오른쪽 "일반대화용" 추천 질문 · 모바일 고객 목록 상단 [MeAI 일반대화]',C.blue,C.blue50);
    col(M+6.2,'맞춤대화','이 고객에게 무엇을 제안할 것인가',['고객 선택 → 보장분석','부족 보장 · 제안 우선순위','상세설계 · 가계약 요청','요약 리포트 → 카카오톡'],'진입: 대문 [맞춤대화] 카드 → 고객 검색 팝업 · 고객찾기 [이 고객으로 맞춤대화 시작] · 모바일 고객 카드 [MeAI]',C.red,C.red50);
    L.note(s,{x:M,y:6.5,w:W-2*M,h:0.45,label:'',text:'처음엔 일반대화로 감을 익히고, 고객을 만나기 전에는 꼭 맞춤대화로 준비하세요. 대문 이후로는 맞춤대화가 고객이 정해진 상태로 열려요.',tone:'grey',size:10});
  }});
  // 6-2 PC 화면 구성
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · PC 맞춤대화 화면',title:'왼쪽은 메뉴, 가운데는 대화, 아래는 입력창. 세 덩어리예요',pageNo:no});
    const g = L.img(s,HERO('term_pc_full'),{x:M,y:1.45,w:8.75,h:5.5,valign:'top',align:'left'});
    const clip={x:0,y:0};
    L.pin(s,g,272,155,1,{clip}); L.pin(s,g,272,305,2,{clip}); L.pin(s,g,272,480,3,{clip}); L.pin(s,g,150,788,4,{clip}); L.pin(s,g,1012,27,5,{clip}); L.pin(s,g,456,215,6,{clip}); L.pin(s,g,456,500,7,{clip}); L.pin(s,g,1270,726,8,{clip}); L.pin(s,g,456,800,9,{clip});
    L.numList(s,{x:9.6,y:1.45,w:3.15,gap:0.06,titleSize:11,descSize:9.5,items:[{n:1,title:'담당 고객 · 동의 남은 일수',desc:'"이민호님 · 보장분석 동의 79일 남음".'},{n:2,title:'약관 검색 · 사용 가이드',desc:'전사 약관 원문과 화면 안내.'},{n:3,title:'대화 이력 (월별)',desc:'지난 대화를 눌러 이어가요.'},{n:4,title:'새로 대화하기',desc:'주제가 바뀌면 새 대화.'},{n:5,title:'상단 버튼 3개',desc:'보장 분석 · 사용중인 정보 수정 · 요약 리포트.'},{n:6,title:'내 질문',desc:'복사·편집·저장 아이콘이 붙어요.'},{n:7,title:'MeAI 답변',desc:'잘 갖춰진 것 → 비어 있는 것 → 할 일 순서.'},{n:8,title:'NEW [용어] 버튼',desc:'입력창 오른쪽 위. 이 파트의 용어 설명 장에서 자세히.'},{n:9,title:'입력창',desc:'"궁금한 점을 자유롭게 질문해 주세요".'}]});
  }});
  // 6-2b 맞춤대화 시작 화면
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 맞춤대화 시작 화면',title:'맞춤대화가 열리면 고객 정보와 분석할 상품부터 정해요',pageNo:no});
    const g = L.img(s,HERO('custom_start_full'),{x:M,y:1.45,w:6.15,h:5.5,valign:'top',align:'left'});
    const clip={x:0,y:0};
    L.pin(s,g,218,157,1,{clip}); L.pin(s,g,470,81,2,{clip}); L.pin(s,g,470,290,3,{clip}); L.pin(s,g,470,470,4,{clip}); L.pin(s,g,470,756,5,{clip}); L.pin(s,g,905,752,6,{clip}); L.pin(s,g,470,911,7,{clip}); L.pin(s,g,470,1058,8,{clip});
    L.numList(s,{x:7.0,y:1.45,w:5.7,gap:0.07,titleSize:11.5,descSize:9.8,items:[
      {n:1,title:'담당 고객 · 보장분석 동의 남은 일수',desc:'"김도윤님 · 79일 남음". 고객이 정해진 채로 열렸다는 표시예요.'},
      {n:2,title:'분석할 고객 정보를 입력하세요 (미입력)',desc:'"고객 정보를 미리 설정하고 시작하면 고객의 맥락을 고려한 답변을 할 수 있습니다."'},
      {n:3,title:'다섯 칸, 아는 것만',desc:'직업 · 병력 · 가족력 · 설계사 희망 보험료 · 메모. 병력과 가족력이 답의 방향을 가장 크게 바꿔요. 이름·연락처 같은 개인정보는 넣지 않아요.'},
      {n:4,title:'[입력하지 않고 넘어가기] · [입력 완료]',desc:'비워도 대화는 돼요. 채웠으면 꼭 [입력 완료]를 눌러야 반영돼요.'},
      {n:5,title:'선택된 정상 계약의 총 보험료',desc:'"지금 매달 이만큼 내고 계세요"로 대화를 열 수 있는 숫자예요.'},
      {n:6,title:'약관DB 구성 완료 · 구성 중 · 미확보',desc:'상품 옆 점 색. 약관DB가 없는 상품은 답이 부정확할 수 있어요.'},
      {n:7,title:'담보 버튼으로 걸러요',desc:'암 · 뇌/심장 · 치료비 · 수술비 · 입원일당 · 실비 · 운전자 · 치매/간병 · 사망/후유장해.'},
      {n:8,title:'상품 목록 · 전체 선택',desc:'기본은 전체 선택. 이번 상담과 관계없는 계약은 체크를 풀면 분석에서 빠져요.'},
    ]});
  }});
  // 6-3 답변 읽는 법
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 답변 읽는 법',title:'답변은 "잘 갖춰진 것 → 비어 있는 것 → 이제 할 일" 순서로 와요',sub:'"이 고객 보험 어디가 부족한지 알려줘" 한 마디에 대한 실제 답변이에요. 왼쪽이 앞부분, 오른쪽이 뒷부분이에요.',pageNo:no});
    const g1 = L.img(s,HERO('term_answer_top'),{x:M,y:1.85,w:5.95,h:4.45,valign:'top',align:'left'});
    const g2 = L.img(s,HERO('term_answer_bottom'),{x:M+6.2,y:1.85,w:5.95,h:4.45,valign:'top',align:'left'});
    const o1={clip:{x:465,y:75},dsf:2,d:0.3}, o2={clip:{x:465,y:700},dsf:2,d:0.3};
    L.pin(s,g1,505,208,1,o1); L.pin(s,g1,505,425,2,o1); L.pin(s,g1,505,618,3,o1); L.pin(s,g2,505,760,4,o2); L.pin(s,g2,505,1085,5,o2); L.pin(s,g2,505,1215,6,o2);
    L.pinStrip(s,{x:M,y:6.4,w:W-2*M,cols:6,rowH:0.45,size:9.5,items:[{n:1,text:'한 줄 결론이 곧 상담 주제'},{n:2,text:'잘 갖춰진 것 → 안심시키는 말부터'},{n:3,text:'비어 있는 것 → 제안 주제'},{n:4,text:'표의 "미가입" 두 줄이 제안 포인트'},{n:5,text:'이제 하면 되는 일 → 다음 행동'},{n:6,text:'[용어 설명 N] · 복사·출처·좋아요'}]});
  }});
  // 6-4 용어 설명 PC
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 용어 설명 (PC)',title:'모르는 용어가 나오면 [용어] 버튼 하나로 바로 풀려요',sub:'입력창 오른쪽 위 [용어]를 켜면 답변 속 전문용어에 표시가 붙고, 답변 끝 [용어 설명 N]에서 뜻을 한꺼번에 볼 수 있어요.',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    L.img(s,HERO('term_pc_input_z'),{x:M,y:1.85,w:5.9,h:1.55,valign:'top',align:'left'}); L.caption(s,{x:M,y:3.4,w:5.9,text:'입력창 오른쪽 위 [용어] 버튼'});
    L.img(s,HERO('term_pc_on_z'),{x:M,y:3.75,w:5.9,h:3.0,valign:'top',align:'left'}); L.caption(s,{x:M,y:6.75,w:5.9,text:'[용어]를 켠 뒤 · 일반암 진단비 · 비급여 · 실손 의료비에 표시'});
    L.img(s,AG('term','14_pc_glossary6_open'),{x:6.75,y:1.85,w:5.95,h:2.85,valign:'top',align:'left'}); L.caption(s,{x:6.75,y:4.72,w:5.95,text:'[용어 설명 6]을 누르면 · 용어와 뜻이 목록으로. "용어를 누르면 본문 위치로 이동해요"'});
    L.img(s,HERO('term_tooltip_crop'),{x:6.75,y:5.05,w:2.6,h:1.35,valign:'top',align:'left'}); L.caption(s,{x:6.75,y:6.42,w:2.6,text:'표시된 용어를 누르면 뜻이 떠요',size:9});
    L.note(s,{x:9.55,y:5.05,w:3.15,h:1.75,label:'현장에서',text:'고객이 비급여가 뭐냐고 물으면 [용어 설명]의 문장을 그대로 읽어 주세요. 예: 건강보험이 적용되지 않아 병원비 전액을 환자가 직접 부담해야 하는 치료. 고객 눈높이 문장이에요.',tone:'blue',size:9.5});
  }});
  // 6-5 용어 설명 모바일
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 용어 설명 (모바일)',title:'모바일에서는 화면 오른쪽 아래 [용어] 버튼이에요',sub:'하는 일은 PC와 같아요. 위치만 달라요. 엄지로 닿는 자리에 있어요.',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    L.phone(s,HERO('term_mo_phone'),{x:M,y:1.85,w:2.9,h:4.75}); L.caption(s,{x:M,y:6.62,w:2.9,text:'답변 화면 · 오른쪽 아래 [용어]'});
    L.phone(s,HERO('term_mo_phone_2'),{x:M+3.1,y:1.85,w:2.9,h:4.75}); L.caption(s,{x:M+3.1,y:6.62,w:2.9,text:'[용어]를 켜면 용어에 표시'});
    L.phone(s,AG('term','70_mo_glossary6_open'),{x:M+6.2,y:1.85,w:2.9,h:4.75}); L.caption(s,{x:M+6.2,y:6.62,w:2.9,text:'답변 끝 [용어 설명 6]을 펼친 목록'});
    L.numList(s,{x:M+9.4,y:1.85,w:2.75,gap:0.12,titleSize:11.5,descSize:9.5,items:[{n:1,title:'PC는 입력창 오른쪽 위',desc:'모바일은 화면 오른쪽 아래. 같은 아이콘이에요.'},{n:2,title:'켜고 끄기',desc:'한 번 누르면 표시, 다시 누르면 원래대로.'},{n:3,title:'목록으로 보기',desc:'답변 끝 [용어 설명 N]을 누르면 용어와 뜻을 한 번에.'},{n:4,title:'고객에게 그대로',desc:'뜻풀이는 고객 눈높이 문장이라 읽어 주기만 하면 돼요.'}]});
  }});
  // 6-6 모드 변경 PC
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 모드 변경 (PC)',title:'질문마다 "간편 분석"과 "상세 분석"을 골라요',sub:'입력창 아래 [간편 분석] 버튼을 누르면 두 가지 중 고를 수 있어요. 고객 앞에서는 간편, 약관을 따질 때는 상세. 질문할 때마다 바꿔도 돼요.',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    L.img(s,HERO('mode_pc_dropdown_z'),{x:M,y:1.85,w:6.7,h:4.1,valign:'top',align:'left'}); L.caption(s,{x:M,y:5.95,w:6.7,text:'[간편 분석 ⌄]을 누르면 두 가지가 펼쳐져요'});
    L.img(s,AG('mode','24_pc_zoom_mode_notice'),{x:7.6,y:5.65,w:5.1,h:0.5,valign:'top',align:'left'});
    L.card(s,{x:7.6,y:1.85,w:5.1,h:1.75,kicker:'간편 분석 · 고객 상담 · 직관적 검토용',title:'어려운 보험 용어를 일상 언어로 풀어서 보여줍니다',desc:'처음 설정이에요. 고객과 함께 보는 화면, 첫 상담, 안내 문안 만들기에 맞아요.',titleSize:12.5,descSize:10});
    L.card(s,{x:7.6,y:3.75,w:5.1,h:1.75,kicker:'상세 분석 · 약관 · 담보 정밀 검토용',title:'보장 금액, 지급 조건, 세부 담보를 전문적으로 비교합니다',desc:'약관 근거를 확인하거나 자사·타사 담보를 숫자로 비교할 때. 리모델링 판단에 맞아요.',titleSize:12.5,descSize:10,accent:C.navy});
    L.note(s,{x:M,y:6.25,w:W-2*M,h:0.55,label:'바꾸면',text:'대화 끝에 "지금부터 상세 분석 모드로 답변합니다" 안내줄이 붙고, 다음 질문부터 그 모드로 답해요. 옆의 [상품 선택]은 분석할 상품을 고르는 버튼이에요(세부 화면은 오픈 시 안내).',tone:'grey',size:10});
  }});
  // 6-7 모드 변경 모바일
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 모드 변경 (모바일)',title:'모바일에서도 입력창 아래 같은 자리에 있어요',sub:'[간편 분석] 버튼을 누르면 아래에서 "분석 모드" 선택창이 올라와요. 고르면 선택창이 닫히고 다음 질문부터 그 모드로 답해요.',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    L.phone(s,HERO('mode_mo_phone'),{x:M,y:1.85,w:2.9,h:4.75}); L.caption(s,{x:M,y:6.62,w:2.9,text:'입력창 아래 [간편 분석] · [상품 선택]'});
    L.phone(s,HERO('mode_mo_phone_2'),{x:M+3.1,y:1.85,w:2.9,h:4.75}); L.caption(s,{x:M+3.1,y:6.62,w:2.9,text:'"분석 모드" 선택창 · 간편 / 상세'});
    L.phone(s,AG('mode','47_mo_mode_detailed'),{x:M+6.2,y:1.85,w:2.9,h:4.75}); L.caption(s,{x:M+6.2,y:6.62,w:2.9,text:'상세 분석 선택 뒤 · 버튼과 안내줄이 바뀌어요'});
    L.numList(s,{x:M+9.4,y:1.85,w:2.75,gap:0.12,titleSize:11.5,descSize:9.5,items:[{n:1,title:'버튼을 누르면',desc:'아래에서 "분석 모드" 선택창이 올라와요. 체크가 현재 모드예요.'},{n:2,title:'고르면 끝',desc:'선택창이 닫히고 버튼 이름이 "상세 분석"으로 바뀌어요. 대화에는 지금부터 상세 분석 모드로 답변한다는 안내줄이 붙어요.'},{n:3,title:'질문마다 바꿔도 돼요',desc:'고객 앞에서는 간편, 약관을 따질 땐 상세. 되돌리면 안내줄이 다시 붙어요.'},{n:4,title:'마이크 · 전송',desc:'입력창 오른쪽 마이크로 말하고, 글자가 들어가면 전송 버튼이 켜져요.'}]});
  }});
  // 6-8 꼬리질문
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 답변 아래',title:'답이 오면, 꼬리질문 버튼으로 이어가세요',sub:'답변 아래 MeAI가 다음 질문 3개를 미리 만들어 둬요. 타이핑 없이 버튼만 누르면 대화가 깊어져요.',pageNo:no});
    const g = L.img(s,HERO('mode_pc_bottom2_z'),{x:M,y:1.85,w:7.4,h:5.0,valign:'top',align:'left'});
    const clip={x:480,y:340}, o={clip,dsf:3};
    L.pin(s,g,470,367,1,o); L.pin(s,g,470,494,2,o); L.pin(s,g,470,638,3,o); L.pin(s,g,470,750,4,o); L.pin(s,g,470,800,5,o);
    L.numList(s,{x:8.4,y:1.85,w:4.3,gap:0.08,titleSize:11.5,descSize:9.8,items:[{n:1,title:'답변 아래 아이콘',desc:'복사 · 출처 · 좋아요 · 싫어요. 복사로 답을 메모장이나 카톡에 옮겨요. 출처로 근거를 확인해요.'},{n:2,title:'꼬리질문 3개',desc:'대화 흐름을 읽고 다음 질문을 제안해요. 누르면 그 질문이 바로 전송돼요.'},{n:3,title:'질문 더보기 (프롬프트 라이브러리)',desc:'미리 만들어 둔 질문 모음이에요. 추천 · 최신 · 나의 질문 탭에서 골라 [이 질문 사용하기].'},{n:4,title:'입력창',desc:'직접 쓰거나(모바일은 마이크) 그대로 보내요.'},{n:5,title:'모드 · 상품 선택',desc:'질문마다 간편/상세를 고르고 분석할 상품을 좁혀요.'}]});
    L.note(s,{x:8.4,y:5.45,w:4.3,h:1.35,label:'왜 중요할까요?',text:'질문을 하나만 쓴 분보다 두 개 이상 이어 쓴 분의 가계약이 2.3배였어요(2026.08). 버튼 한 번 더가 차이를 만들어요.',tone:'dark',size:10});
  }});
  // 6-9 요약 리포트
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 요약 리포트',title:'요약 생성 → 선택·편집 → 리포트 생성 → 카카오톡 도착',sub:'핸드폰 하나로 상담부터 발송까지 끝나요. PC에서는 오른쪽 위 [요약 리포트] 버튼이에요.',pageNo:no});
    const st=[['요약 생성 버튼','대화 화면 상단 [요약 생성]. 대화가 어느 정도 쌓인 뒤가 좋아요.'],['질문·답변 선택 → 편집하기','리포트에 넣을 답변만 체크해요. 내부 판단용 답변은 빼요.'],['리포트 생성하기','"완료되면 카카오톡으로 다운로드 링크가 전송됩니다" 안내가 떠요.'],['카카오톡 알림톡 도착','"MeAI 요약레포트 안내" [요약레포트 확인하기]. 열람 기간 D+7일. (이름은 가렸어요)']];
    st.forEach((t,i)=>{ const x=M+i*3.08,w=2.9; const f = i<3 ? LEG('report_step'+(i+1)) : HERO('report_kakao_crop'); L.phone(s,f,{x,y:1.85,w,h:3.95}); L.badge(s,{x,y:5.9,n:i+1,d:0.3}); L.T(s,t[0],{x:x+0.4,y:5.88,w:w-0.4,h:0.34,fontSize:12,bold:true,color:C.navy}); L.T(s,t[1],{x,y:6.21,w,h:0.55,fontSize:9.5,color:C.g600,lineSpacingMultiple:1.25}); if(i<3) L.arrow(s,{x:x+w-0.08,y:3.7,w:0.35}); });
    L.caption(s,{x:M,y:6.76,w:W-2*M,text:'실제 모바일 화면(2026.06, v3 가이드북과 같은 캡처) · 리포트에는 "AI로 생성된 보조자료입니다" 문구가 표시돼요. 보내기 전 숫자·약관 근거·개인정보를 확인하세요.',align:'left'});
  }});
  // 6-10 모바일 진입
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 모바일',title:'핸드폰에서는 앱 홈 → 보장분석 → MeAI, 세 번 터치예요',sub:'모바일 대문·고객찾기·게시판은 PC 오픈 뒤 순차 적용 예정이에요. 우선 PC 대문에서 시작하고, 현장에서는 모바일로 이어가세요.',pageNo:no});
    L.phone(s,LEG('mobile_app_home'),{x:M,y:1.85,w:2.4,h:4.75}); L.caption(s,{x:M,y:6.62,w:2.4,text:'① 앱 홈 · [보장분석]',size:9});
    L.phone(s,HERO('mobile_customer_list'),{x:M+2.55,y:1.85,w:2.4,h:4.75}); L.caption(s,{x:M+2.55,y:6.62,w:2.4,text:'② ③ 고객 목록 · [MeAI 일반대화] · 카드 [MeAI]',size:9});
    L.phone(s,AG('mode','55_mo_menu_drawer'),{x:M+5.1,y:1.85,w:2.3,h:4.75}); L.caption(s,{x:M+5.1,y:6.62,w:2.3,text:'④ 대화 화면 ≡ 메뉴',size:9});
    L.numList(s,{x:8.2,y:1.85,w:4.5,gap:0.06,titleSize:11,descSize:9.5,items:[{n:1,title:'앱 홈에서 [보장분석] 아이콘 터치',desc:'홈 화면 가운데 아이콘 묶음의 첫 번째. 여기가 MeAI로 들어가는 문이에요.'},{n:2,title:'상단 [MeAI 일반대화] = 무엇이든 묻는 창',desc:'고객 목록 위, 고객등록 버튼 옆에 있어요.'},{n:3,title:'고객 카드의 [MeAI] = 그 고객 맞춤대화',desc:'보라색 MeAI 버튼을 누르면 그 고객의 보장분석을 옆에 둔 맞춤대화가 열려요.'},{n:4,title:'대화 화면의 ≡ 메뉴',desc:'약관 검색 · 사용 가이드 · 월별 대화 목록, 맨 아래 [영업지원 모바일]로 나가기.'}]});
    L.note(s,{x:8.2,y:5.15,w:4.5,h:0.85,label:'공통',text:'대화 이력과 저장한 나의 질문은 PC와 모바일에서 똑같이 보여요. 사무실에서 대문으로 준비하고, 현장에서 폰으로 이어가세요.',tone:'blue',size:10.5});
    L.note(s,{x:8.2,y:6.1,w:4.5,h:0.75,label:'TIP',text:'고객 목록 상단에 "오늘 보장분석 활용 : N회 (제한 횟수 : 일일 300회)"가 보여요. 하루 한도를 확인하는 곳이에요.',tone:'grey',size:10});
  }});
};
