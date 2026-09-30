module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG, LEG } = ctx;
  S.push({ part:'07', fn:(pres,no)=> L.divider(pres,{num:'07',title:'찾아가는 영업의 하루\n루틴과 시나리오',sub:'매일 아침 MeAI 홈을 열면 오늘 연락할 고객과 첫 말이 정해져요.',learn:['아침 루틴 4단계','카드에서 시작하는 시나리오 3가지','주간·월간 루틴 · 첫 5일 미션'],pageNo:no}) });
  // 7-1 아침 루틴
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 7 · 아침 루틴',title:'MeAI 홈만 열면 첫 말까지 정해져요',sub:'매일 아침 화면 순서대로 누르기만 하면 돼요. 서은아 고객(예시)으로 따라가 봐요. 화면 속 질문 문장도 예시예요.',pageNo:no});
    // 한 고객(서은아)으로 네 단계를 잇는다: 01 = MeAI 홈 전체(게시판 빨간 점까지), 02 = 서은아 카드, 03 = 고객찾기에서 펼친 카드, 04 = 오른쪽 추천 질문 패널
    const st=[['MeAI 홈 열기','숫자 4개와 게시판 빨간 점을 확인해요.',HERO('gb5_gate_full_m')],['추천 카드 3장 읽기','#이벤트 임박, #당월 타겟 카드부터 읽어요.',HERO('gb5_card_seo_z')],['고객찾기에서 열기','카드를 누르면 펼쳐져요. 상황을 보고 추천 질문을 골라요.',HERO('gb5_find_seo_card')],['맞춤대화 → 리포트','빨간 질문을 누르면 맞춤대화가 열려요. 리포트는 카카오톡으로.',HERO('gb5_find_seo_right')]];
    st.forEach((t,i)=>{ const x=M+i*3.08,w=2.9,y=1.85; L.R(s,{x,y,w,h:4.3,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,'0'+(i+1),{x:x+0.22,y:y+0.15,w:1,h:0.4,fontSize:18,bold:true,color:C.blue}); L.T(s,t[0],{x:x+0.22,y:y+0.55,w:w-0.44,h:0.36,fontSize:14.5,bold:true,color:C.navy,valign:'middle'});
      const g = L.img(s,t[2],{x:x+0.12,y:y+1.0,w:w-0.24,h:2.5,valign:'middle'});
      if (i===0){ // 게시판 빨간 점(화면 좌표 1279,25 · dsf 2)에 빨간 테두리 원
        const d=0.24, cx=g.x+1279*2*g.scale, cy=g.y+25*2*g.scale;
        s.addShape('ellipse',{x:cx-d/2,y:cy-d/2,w:d,h:d,line:{color:C.red,width:1.75}});
      }
      L.T(s,t[1],{x:x+0.22,y:y+3.6,w:w-0.44,h:0.55,fontSize:12,color:C.g600,lineSpacingMultiple:1.3}); });
    L.note(s,{x:M,y:6.3,w:W-2*M,h:0.6,label:'기억할 것',text:'카드 문장은 고객에게 첫 말, 추천 질문은 MeAI에게 첫 질문.',tone:'dark',size:12.5});
  }});
  // 시나리오 helper — 단계 흐름은 글자를 키우려고 이 파일 안에서 직접 그린다
  const flow = (s,{x,y,w,h,items,activeIdx=-1})=>{
    const gap=0.22, cw=(w-gap*(items.length-1))/items.length;
    items.forEach((it,i)=>{ const cx=x+i*(cw+gap), act=i===activeIdx;
      L.R(s,{x:cx,y,w:cw,h,fill:act?C.blue:C.white,line:act?null:C.g200,radius:0.14,shadow:!act});
      L.T(s,it.step,{x:cx+0.2,y:y+0.2,w:cw-0.3,h:0.28,fontSize:10.5,bold:true,color:act?'FFFFFF':C.blue,transparency:act?20:0});
      L.T(s,it.title,{x:cx+0.2,y:y+0.5,w:cw-0.3,h:0.4,fontSize:14.5,bold:true,color:act?'FFFFFF':C.navy,valign:'middle'});
      L.T(s,it.desc,{x:cx+0.2,y:y+1.0,w:cw-0.3,h:h-1.1,fontSize:11.5,color:act?'FFFFFF':C.g600,lineSpacingMultiple:1.3});
      if (i<items.length-1) L.T(s,'›',{x:cx+cw-0.02,y:y+h/2-0.2,w:gap+0.04,h:0.4,fontSize:16,color:C.g400,align:'center',valign:'middle'});
    });
  };
  const scenario = (kicker,title,sub,cardImg,cardCaption,steps,talk,pageNo)=>{
    const s = L.base(ctx.pres,{kicker,title,sub,pageNo});
    const g = L.img(s,cardImg,{x:M,y:1.85,w:3.9,h:4.3,valign:'top',align:'left'}); L.caption(s,{x:M,y:g.y+g.h+0.08,w:3.9,text:cardCaption,size:10});
    const rx=M+4.2, rw=W-M-rx;
    flow(s,{x:rx,y:1.85,w:rw,h:2.15,items:steps,activeIdx:1});
    L.note(s,{x:rx,y:4.2,w:rw,h:1.35,label:'첫 말 → 고객에게',text:talk[0],tone:'blue',size:14});
    L.note(s,{x:rx,y:5.72,w:rw,h:0.9,label:'MeAI에게 첫 질문',text:talk[1],tone:'grey',size:12.5});
    return s;
  };
  // 시나리오 1 · 박준호(세트 2 첫 카드): 자동차보험 만기를 계기로 비어 있는 운전자 보장 점검
  S.push({ fn:(pres,no)=>{ ctx.pres=pres; scenario('PART 7 · 시나리오 1 · 이벤트 임박','자동차보험 만기 9일 전, 운전자 보장까지','만기 안내를 계기로 비어 있는 운전자 보장을 함께 점검해요.',HERO('gb5_card_park_z'),'MeAI 홈 추천 카드(세트 2) · #이벤트 임박 · 예시 화면',[{n:1,step:'MeAI 홈',title:'카드 읽기',desc:'자동차보험 만기 9일,\n운전자보험 없음.\n동의 D-18로 유효.'},{n:2,step:'고객찾기',title:'카드 펼치기',desc:'한눈에 보기 6칸,\n추천 질문 확인.'},{n:3,step:'맞춤대화',title:'운전자 보장 점검',desc:'"보장분석 해줘"\n→ 운전자 보장 빈 곳.'},{n:4,step:'리포트',title:'카카오톡 발송',desc:'운전자 보장이\n필요한 이유를\n리포트로.'}],['"고객님, 자동차보험 만기가 9일 뒤예요.\n갱신 안내 드리면서 운전자 보장도 같이 봐 드릴게요."','"자동차보험만 있고 운전자보험이 없는 고객에게\n운전자 보장이 필요한 이유를 쉽게 설명해줘"'],no); }});
  S.push({ fn:(pres,no)=>{ ctx.pres=pres; scenario('PART 7 · 시나리오 2 · 동의 만료 임박','동의 만료 전, 재동의로 보장 점검','재동의를 계기로 신담보와 보장 공백을 함께 점검해요.',HERO('reco1_card2'),'※ D-90은 사전조회동의(가입설계동의와 별개) · 예시 화면',[{n:1,step:'MeAI 홈',title:'카드 읽기',desc:'가입설계동의\n이달 말 만료.\n연락 명분이 돼요.'},{n:2,step:'재동의',title:'동의 먼저',desc:'만료 전에\n연장 부탁.\n보장 점검도 약속.'},{n:3,step:'맞춤대화',title:'보장 공백 점검',desc:'"보장분석 해줘"\n→ 신담보와 비교.'},{n:4,step:'리포트',title:'점검 결과 발송',desc:'신담보 기준\n점검 요약을 보내요.'}],['"고객님, 이달 말 동의가 만료돼 연장 부탁드려요.\n새로 나온 보장도 봐 드릴게요."','"최근 신담보 기준으로 이 고객 보장의 빈 곳을 알려줘"'],no); }});
  S.push({ fn:(pres,no)=>{ ctx.pres=pres; scenario('PART 7 · 시나리오 3 · 동의부터 · AI 추천 고객','상령일 2주 전, 동의부터 받아요','AI 추천 고객이지만 사전조회동의가 필요해요. 알림톡부터 보내요.',HERO('gb5_card_kim_z'),'MeAI 홈 추천 카드(세트 3) · AI 추천 고객 · 예시 화면',[{n:1,step:'MeAI 홈',title:'카드 읽기',desc:'암진단비 1천만원,\n상령일 2주.\n동의 필요 표시.'},{n:2,step:'동의 요청',title:'알림톡 보내기',desc:'고객찾기 오른쪽\n[사전조회동의\n요청하기] 누르고\n휴대폰 번호 입력.'},{n:3,step:'맞춤대화',title:'진단비 점검',desc:'동의 반영 뒤\n"보장분석 해줘".'},{n:4,step:'리포트',title:'상령일 전 제안',desc:'인상 전 가입의\n이점을 리포트로.'}],['"고객님, 2주 뒤 보험 나이가 올라가요.\n그 전에 점검하려고 동의 알림톡 보내요."','"상령일 전에 암진단비를 늘려야 하는 이유를 쉽게 설명해줘"'],no); }});
  // 7-5 주간·월간 루틴
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 7 · 주간 · 월간 루틴',title:'하루는 카드로, 한 주는 그룹으로',sub:'MeAI 홈 카드는 매일, 고객찾기 그룹은 주기별로 챙겨요.',pageNo:no});
    const rows=[['주기','어디서','무엇을','이렇게 해 보세요'],['매일 아침','MeAI 홈 · 오늘의 추천 고객','카드 3~9장 읽고 1명 맞춤대화','추천 고객 1명 접촉'],['매주 월요일','고객찾기 · 상령일 임박 · 생일 임박','이번 주 연락할 고객 정리','상령일 가까운 고객부터 연락'],['월초','고객찾기 · 당월 영업 타겟','이달 타겟 고객 확인 · 연락 순서 정하기','추천 이유를 첫 말로 연락'],['매달','고객찾기 · 사전동의 만료','D-n 짧은 순으로 재동의','"사전조회 동의 필요" 줄이기'],['수시','고객찾기 · 신규 등록 고객','등록 → 동의 → 첫 맞춤대화','등록한 날 동의 요청']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: 12, bold: ri===0||ci===0, color: ri===0? C.g600 : (ci===0? C.blue : C.g800), fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[4,8,4,8]}})));
    s.addTable(data,{x:M,y:1.85,w:W-2*M,colW:[1.75,3.95,3.6,2.83],rowH:0.5,border:{type:'solid',color:C.g200,pt:0.75}});
    const by=5.07, bh=1.7;
    L.R(s,{x:M,y:by,w:2.6,h:bh,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.T(s,'영업 기회 탭',{x:M+0.22,y:by+0.14,w:2.2,h:0.32,fontSize:12,bold:true,color:C.navy}); [['상령일 임박','11'],['생일 임박','7'],['사전동의 만료','35']].forEach((g,i)=>{ L.chip(s,{x:M+0.22,y:by+0.52+i*0.37,text:g[0],fill:C.orange50,color:C.orange,size:10.5,h:0.32}); L.T(s,g[1]+'명',{x:M+1.85,y:by+0.52+i*0.37,w:0.6,h:0.32,fontSize:12,bold:true,color:C.g700,valign:'middle'}); });
    L.note(s,{x:M+2.8,y:by,w:4.75,h:bh,label:'10/2~ 영업포탈 CRM',text:'생일·상령일 목록에서 [MeAI 맞춤대화]를 누르면 고객 대화가 바로 열려요.',tone:'blue',size:12});
    L.note(s,{x:M+7.75,y:by,w:W-2*M-7.75,h:bh,label:'숫자는 예시',text:'그룹 인원은 화면 예시예요. 실제로는 내 고객 기준으로 매일 새로 계산돼요.',tone:'grey',size:12});
  }});
  // 7-6 첫 주 미션
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 7 · 첫 5일 미션',title:'첫 5일, 하루 하나씩만 해보세요',sub:'첫 사용까지 짧을수록 정착률이 높았어요(데이터분석팀 2026.08).',pageNo:no});
    const days=[['DAY 1','MeAI 홈 열기','숫자 4개와\n추천 카드 3장 읽기','일반대화 질문 예시\n하나 눌러 보기'],['DAY 2','카드에서 고객찾기','[MeAI 고객찾기에서 열기]\n→ 한눈에 보기 6칸 확인','추천 질문 눌러 보기'],['DAY 3','맞춤대화 시작','"보장분석 해줘" →\n꼬리질문 2번','부족 보장 3개 메모'],['DAY 4','그룹으로 찾기','[사전동의 만료]\n그룹 확인','D-n 짧은 1명께\n재동의 부탁하기'],['DAY 5','리포트 보내기','요약 리포트를\n내 카톡으로 받아 보기','좋았던 질문을\n나의 질문으로 저장']];
    days.forEach((d,i)=>{ const x=M+i*2.45,w=2.3,y=1.85,h=3.8; L.R(s,{x,y,w,h,fill: i===0? C.blue : C.white,line: i===0? null : C.g200,radius:0.14,shadow:i!==0}); const fg = i===0?'FFFFFF':C.navy; L.T(s,d[0],{x:x+0.2,y:y+0.22,w:w-0.4,h:0.3,fontSize:11,bold:true,color: i===0?'FFFFFF':C.blue,transparency:i===0?20:0}); L.T(s,d[1],{x:x+0.2,y:y+0.55,w:w-0.35,h:0.45,fontSize:16,bold:true,color:fg,valign:'middle'}); [d[2],d[3]].forEach((t,k)=>{ const ty=y+1.3+k*1.3; /* ☐ 는 글자와 같은 크기·줄간격으로 두어 첫 줄과 높이를 맞춘다. 글 칸은 버튼 이름 [MeAI 고객찾기에서 열기] 가 한 줄에 들어가게 넓힘 */ L.T(s,'☐',{x:x+0.16,y:ty,w:0.24,h:0.4,fontSize:12,color: i===0?'FFFFFF':C.g500,lineSpacingMultiple:1.3}); L.T(s,t,{x:x+0.40,y:ty,w:w-0.44,h:1.1,fontSize:12,color: i===0?'FFFFFF':C.g700,lineSpacingMultiple:1.3}); }); });
    L.note(s,{x:M,y:5.9,w:W-2*M,h:0.8,label:'5일 뒤',text:'"MeAI 홈에서 하루를 시작하는 사람"이 됐어요. 이제 매일 아침 루틴으로 이어가요.',tone:'dark',size:13});
  }});
};
