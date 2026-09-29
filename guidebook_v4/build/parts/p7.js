module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG, LEG } = ctx;
  S.push({ part:'07', fn:(pres,no)=> L.divider(pres,{num:'07',title:'찾아가는 영업의 하루\n루틴과 시나리오',sub:'아침 3분 루틴, 카드 세 장으로 보는 시나리오, 주간·월간 그룹 루틴, 첫 5일 미션.',learn:['아침 3분 · 대문 → 카드 → 고객찾기 → 맞춤대화 → 리포트','시나리오 3가지 · 카드의 이유가 곧 첫 말이 되는 과정','주간·월간 그룹 루틴 · 첫 5일 미션'],pageNo:no}) });
  // 7-1 아침 3분
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 7 · 아침 3분 루틴',title:'아침 3분, 대문만 열면 오늘 연락할 사람과 첫 말이 정해져요',sub:'10월부터 권해 드리는 아침 루틴이에요. 화면 순서 그대로예요.',pageNo:no});
    const st=[['대문 열기','영업포탈 → MeAI. 숫자 4개를 훑고 게시판 빨간 점을 확인해요.',HERO('gate_top')],['추천 카드 3장 읽기','이유 문장과 태그를 읽어요. #이벤트 임박·#당월 타겟부터.',HERO('reco1_card1')],['고객찾기에서 열기','펼친 카드의 한눈에 보기 6칸으로 상황 파악, 추천 질문을 복사해요.',HERO('find_card_z')],['맞춤대화 → 리포트','[이 고객으로 맞춤대화 시작] → "보장분석 해줘" → 꼬리질문 → 요약 리포트를 카카오톡으로.',HERO('find_right_z')]];
    st.forEach((t,i)=>{ const x=M+i*3.08,w=2.9; L.R(s,{x,y:1.85,w,h:4.55,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,'0'+(i+1),{x:x+0.25,y:2.0,w:1,h:0.4,fontSize:18,bold:true,color:C.blue}); L.T(s,t[0],{x:x+0.25,y:2.42,w:w-0.5,h:0.36,fontSize:12.5,bold:true,color:C.navy,valign:'middle'}); L.img(s,t[2],{x:x+0.25,y:2.9,w:w-0.5,h:1.9,valign:'middle'}); L.T(s,t[1],{x:x+0.25,y:4.9,w:w-0.5,h:1.4,fontSize:10,color:C.g600,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:6.55,w:W-2*M,h:0.45,label:'기억할 것',text:'추천 카드의 이유 문장은 고객에게 하는 첫 말, 고객찾기의 추천 질문은 MeAI에게 하는 첫 질문. 두 문장이 준비돼 있으니 망설일 이유가 없어요.',tone:'dark',size:10});
  }});
  // 시나리오 helper
  const scenario = (kicker,title,sub,cardImg,cardCaption,steps,talk,pageNo)=>{
    const s = L.base(ctx.pres,{kicker,title,sub,pageNo});
    L.img(s,cardImg,{x:M,y:1.85,w:3.7,h:3.9,valign:'top',align:'left'}); L.caption(s,{x:M,y:5.78,w:3.7,text:cardCaption});
    L.steps(s,{x:4.65,y:1.85,w:8.05,h:2.6,items:steps,activeIdx:1});
    L.note(s,{x:4.65,y:4.65,w:8.05,h:1.35,label:'첫 말 (카드의 이유 문장 → 고객에게)',text:talk[0],tone:'blue',size:10.5});
    L.note(s,{x:4.65,y:6.1,w:8.05,h:0.8,label:'MeAI에게 첫 질문',text:talk[1],tone:'grey',size:10.5});
    return s;
  };
  S.push({ fn:(pres,no)=>{ ctx.pres=pres; scenario('PART 7 · 시나리오 1 · 이벤트 임박','"부담보 해제가 5일 남았습니다" — 재설계 제안의 타이밍','해제 시점에 맞춰 부족한 보장을 다시 설계하고 필요한 특약을 함께 제안하기 좋은 기회예요.',HERO('reco1_card1'),'대문 추천 카드 · #이벤트 임박 · 사전조회동의 D-25',[{n:1,step:'대문',title:'카드 읽기',desc:'이유: 부담보 해제 D-5. 동의 D-25라 바로 진행.'},{n:2,step:'고객찾기',title:'카드 펼치기',desc:'가입 보험·납입·부족 금액 확인. 추천 질문 복사.'},{n:3,step:'맞춤대화',title:'설계안 요청',desc:'해제되는 담보와 채울 특약을 정리해 달라고 해요.'},{n:4,step:'리포트',title:'카카오톡 발송',desc:'해제 일정과 제안 요약을 리포트로.'}],['"고객님, 그동안 보장이 제한됐던 담보가 5일 뒤 정상화돼요. 이 시점에 맞춰 부족한 보장을 함께 점검해 드리고 싶어요."','"부담보가 해제되는 담보와, 해제 시점에 맞춰 다시 설계할 특약을 정리해줘"'],no); }});
  S.push({ fn:(pres,no)=>{ ctx.pres=pres; scenario('PART 7 · 시나리오 2 · 동의 만료 임박','"가입설계동의가 이달 말 만료됩니다" — 재동의를 계기로 보장 점검','만료 전에 재동의를 받아야 이후에도 안내와 제안을 이어갈 수 있어요. 갱신을 계기로 신담보와 보장 공백을 함께 점검해요.',HERO('reco1_card2'),'대문 추천 카드 · #이벤트 임박 · 사전조회동의 D-90',[{n:1,step:'대문',title:'카드 읽기',desc:'이유: 가입설계동의 이달 말 만료. 연락 명분이 분명해요.'},{n:2,step:'재동의',title:'동의 먼저',desc:'재동의 안내 → 동의 상태는 약 15분 안에 반영.'},{n:3,step:'맞춤대화',title:'보장 공백 점검',desc:'"보장분석 해줘" → 최근 신담보와 비교.'},{n:4,step:'리포트',title:'점검 결과 발송',desc:'재동의 감사 인사와 점검 요약을 함께.'}],['"고객님, 이달 말에 동의가 만료돼서 연장 부탁드리려고요. 겸사겸사 최근에 새로 나온 보장이 고객님께 맞는지도 한번 봐 드릴게요." ※ 가입설계동의(설계용)와 사전조회동의(보장 조회용, 카드의 D-90)는 서로 다른 동의예요.','"이 고객의 보장에서 최근 신담보 기준으로 비어 있는 곳을 알려줘"'],no); }});
  S.push({ fn:(pres,no)=>{ ctx.pres=pres; scenario('PART 7 · 시나리오 3 · 동의부터 · AI 추천 고객','"상령일이 2주 남았고 암진단비가 1천만원뿐입니다" — 동의부터 받고 상령일 전에 제안','상품 소개에 동의한 AI 추천 고객이지만 사전조회동의가 만료됐어요. 알림톡으로 동의를 받은 뒤, 보험 나이가 오르기 전에 진단비 공백을 채워요.',HERO('reco3_card1'),'대문 추천 카드(세트 3) · AI 추천 고객 · 사전조회동의 필요',[{n:1,step:'대문',title:'카드 읽기',desc:'이유: 상령일 2주 · 암진단비 1천만원. 동의 필요 표시.'},{n:2,step:'동의 요청',title:'알림톡 보내기',desc:'고객찾기 오른쪽 [사전조회동의 요청하기] → 휴대폰 번호 → [보내기].'},{n:3,step:'맞춤대화',title:'진단비 공백 점검',desc:'동의 반영 뒤 [이 고객으로 맞춤대화 시작] → "보장분석 해줘".'},{n:4,step:'리포트',title:'상령일 전 제안',desc:'인상 전 가입의 이점과 제안 요약을 리포트로.'}],['"고객님, 2주 뒤에 보험 나이가 한 살 올라가요. 그 전에 진단비를 점검해 드리고 싶은데, 먼저 동의 알림톡 하나만 보내 드릴게요."','"이 고객에게 상령일 전에 암진단비를 늘려야 하는 이유를 쉽게 설명해줘"'],no); }});
  // 7-5 주간·월간 루틴
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 7 · 주간 · 월간 루틴',title:'하루는 추천 카드로, 한 주와 한 달은 그룹으로 움직여요',sub:'대문 카드는 매일, 고객찾기 그룹은 주기별로. 달력에 넣어 두면 잊지 않아요.',pageNo:no});
    const rows=[['주기','어디서','무엇을','목표 예시'],['매일 아침','대문 · 오늘의 추천 고객','카드 3~9장 읽고 1명 이상 맞춤대화','추천 고객 1명 접촉'],['매주 월요일','고객찾기 · 상령일 임박 · 생일 임박','이번 주 날짜형 고객 목록 정리','상령일 고객 전원 연락'],['월초','고객찾기 · 당월 영업 타겟','이번 달 목표 대상 확인, 조회에서 공유','타겟 7명 전원 제안'],['매달','대문 "사전조회 동의 필요" · 고객찾기 · 사전동의 만료','D-n 짧은 순으로 재동의 캠페인','동의 필요 숫자 줄이기'],['수시','고객찾기 · 신규 등록 고객','등록 → 동의 → 첫 맞춤대화','등록 후 3일 내 동의']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: 10.5, bold: ri===0||ci===0, color: ri===0? C.g600 : (ci===0? C.blue : C.g800), fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[4,8,4,8]}})));
    s.addTable(data,{x:M,y:1.9,w:W-2*M,colW:[1.6,4.0,4.0,2.53],rowH:0.5,border:{type:'solid',color:C.g200,pt:0.75}});
    L.R(s,{x:M,y:5.1,w:2.3,h:1.75,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,'영업 기회 탭',{x:M+0.2,y:5.2,w:2.0,h:0.3,fontSize:10.5,bold:true,color:C.navy}); [['상령일 임박','11'],['생일 임박','7'],['사전동의 만료','35']].forEach((g,i)=>{ L.chip(s,{x:M+0.2,y:5.55+i*0.4,text:g[0],fill:C.orange50,color:C.orange}); L.T(s,g[1]+'명',{x:M+1.7,y:5.55+i*0.4,w:0.5,h:0.28,fontSize:10.5,bold:true,color:C.g700,valign:'middle'}); });
    L.note(s,{x:M+2.5,y:5.1,w:4.7,h:1.75,label:'날짜형 그룹은',text:'주간 접촉 계획표로 그대로 써요. "이번 주 상령일 고객 몇 명?" 한 마디면 조회가 끝나요. 보험 나이가 오르기 전이 제안 타이밍이에요.',tone:'blue',size:10.5});
    L.note(s,{x:M+7.4,y:5.1,w:4.73,h:1.75,label:'숫자는 예시',text:'그룹 인원(35명, 11명…)은 화면 예시예요. 실제 화면에서는 내 고객 기준으로 매일 새로 계산돼요. 오른쪽 위 "최근 업데이트" 시각을 확인하세요.',tone:'grey',size:10.5});
  }});
  // 7-6 첫 주 미션
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 7 · 첫 5일 미션',title:'첫 5일, 하루 하나씩만 해보세요',sub:'첫 사용까지 짧을수록 정착률이 높았어요(데이터분석팀 2026.08). 체크하며 따라가 보세요.',pageNo:no});
    const days=[['DAY 1','대문 열기','영업포탈 → MeAI 대문. 숫자 4개와 추천 카드 3장 읽기','게시판 새 글 1개 읽기'],['DAY 2','카드에서 고객찾기','추천 카드 [MeAI 고객찾기에서 열기] → 펼친 카드 숫자 6개 확인','추천 질문 복사해 두기'],['DAY 3','맞춤대화 시작','[이 고객으로 맞춤대화 시작] → "보장분석 해줘" → 꼬리질문 2번','부족 보장 3개 메모'],['DAY 4','그룹으로 찾기','고객찾기 그룹 하나 골라 D-n 짧은 고객 1명 맞춤대화','[사전동의 만료] 그룹 확인'],['DAY 5','리포트 보내기','요약 리포트 만들어 내 카톡으로 먼저 받아 보기','좋았던 질문 나의 질문으로 저장']];
    days.forEach((d,i)=>{ const x=M+i*2.45,w=2.3,y=1.9,h=3.7; L.R(s,{x,y,w,h,fill: i===0? C.blue : C.white,line: i===0? null : C.g200,radius:0.14,shadow:i!==0}); const fg = i===0?'FFFFFF':C.navy; L.T(s,d[0],{x:x+0.2,y:y+0.2,w:w-0.4,h:0.3,fontSize:10,bold:true,color: i===0?'FFFFFF':C.blue,transparency:i===0?20:0}); L.T(s,d[1],{x:x+0.2,y:y+0.5,w:w-0.4,h:0.4,fontSize:14,bold:true,color:fg,valign:'middle'}); [d[2],d[3]].forEach((t,k)=>{ L.T(s,'☐',{x:x+0.2,y:y+1.05+k*1.2,w:0.3,h:0.3,fontSize:12,color: i===0?'FFFFFF':C.g500}); L.T(s,t,{x:x+0.5,y:y+1.05+k*1.2,w:w-0.7,h:1.1,fontSize:10,color: i===0?'FFFFFF':C.g700,lineSpacingMultiple:1.3}); }); });
    L.note(s,{x:M,y:5.85,w:W-2*M,h:0.5,label:'',text:'5일 뒤, 여러분은 이미 "대문에서 하루를 시작하는 사람"이에요. 그 다음은 PART 7 첫 장의 아침 3분 루틴으로 이어가세요.',tone:'dark',size:10.5});
  }});
};
