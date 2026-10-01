module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO } = ctx;
  // 마무리 장은 L.base를 쓰지 않아 꼬리말을 직접 쓴다. lib.js의 꼬리말 문구가 바뀌면 같이 따라가도록 lib.js에서 읽는다.
  const FOOT = (()=>{ try { const m = require('fs').readFileSync(require('path').join(__dirname,'..','lib.js'),'utf8').match(/FOOTER_TEXT\s*=\s*'([^']+)'/); if (m) return m[1]; } catch(e){} return 'MeAI 활용 가이드북 · MeAI 홈 편'; })();
  S.push({ part:'09', fn:(pres,no)=> L.divider(pres,{num:'09',title:'지켜야 할 것 · FAQ\n용어 정리',sub:'오래 잘 쓰는 조건, 한 번만 제대로 읽어 두기',learn:['다섯 가지 약속','자주 묻는 질문','용어 한 장 정리'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · 꼭 지킬 것',title:'오래 잘 쓰는 다섯 가지 약속',sub:'1·4번은 화면 하단 안내문에도 있음',pageNo:no});
    const items=[['1','답변은 검증 후 사용','오류가 있을 수 있음.\n약관·증권으로 직접 확인한 뒤 안내.',C.blue],['2','개인정보 입력 금지','이름·연락처·주소·주민번호는\n질문에도, 메모에도 넣지 않음.',C.blue],['3','동의 없으면 보지 않기','동의가 없거나 철회된 고객은 막힘.\n우회 말고 동의부터 받기.',C.blue],['4','미검증 책임은 사용자에게','검증 없이 안내하면 금융소비자보호법 등\n법령상 책임은 사용자에게 있음.',C.blue],['5','자료 외부 반출 금지','MeAI 답변·화면 캡처·이 가이드북,\n외부 제공·배포·게시 모두 금지.',C.blue]];
    items.forEach((it,i)=>{ const col=i%3,row=Math.floor(i/3); const x=M+col*4.1,y=1.85+row*2.42,w=3.9,h=2.25; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true}); L.badge(s,{x:x+0.28,y:y+0.3,n:it[0],d:0.44,color:it[3]}); L.T(s,it[1],{x:x+0.88,y:y+0.28,w:w-1.1,h:0.48,fontSize:15,bold:true,color:C.navy,valign:'middle'}); L.T(s,it[2],{x:x+0.28,y:y+1.0,w:w-0.56,h:1.1,fontSize:13,color:C.g600,lineSpacingMultiple:1.35}); });
    L.note(s,{x:M+8.2,y:4.27,w:3.9,h:2.25,label:'화면 하단 안내문 원문',text:'"MeAI의 답변은 생성형 AI를 통해 작성되어 오류가 있을 수 있으므로, 반드시 직접 근거자료를 확인하여 진위를 검증하시기 바랍니다. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다."',tone:'dark',size:11});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · FAQ',title:'처음에 가장 많이 묻는 질문',sub:'이 아홉 개면 첫 주 질문은 대부분 해결',pageNo:no});
    // 동의 기간은 둘로 나눠 적는다: 맞춤대화 가능 = 동의일부터 90일 / MeAI 홈 노출 = 사전조회 동의일로부터 3년 이내(범례)
    const qa=[['MeAI 홈은 어디서 열리나?','PC 영업포탈에서 MeAI로 들어오면\n가장 먼저 열림.\n다른 화면에선 왼쪽 위 [MeAI 홈]을 누르면 이동.'],['추천 고객이 안 보임','오늘의 추천 고객은 CRM 데이터 반입이\n끝난 뒤부터 보임(게시판 공지).\n추천은 매일 밤 새로 계산해 다음 날 반영.'],['추천 고객이\n오늘 연락할 분이 아닌 것 같음','추천은 지시가 아니라 "이유가 있는 고객".\n고객 그룹에서 직접 골라도 됨.'],['동의 없는 고객은?','[고객 동의]나 [사전조회동의 요청하기]를 눌러\n번호를 넣으면 알림톡 발송. 동의하면\n15분 안팎으로 반영, 90일 동안 맞춤대화 가능.'],['검색 팝업에 고객이 없거나 회색','고객 검색 팝업엔 동의가 유효한 고객만 나옴.\n회색은 오늘 동의를 철회한 고객으로\n정보를 볼 수 없음.'],['숫자가 내 고객 수와 다름','MeAI 홈에는 사전조회 동의일로부터\n3년 이내 고객만 보임(범례 안내).\n고객 데이터는 다음 날 반영.'],['한 고객이 여러 그룹에 있음','정상. 우선순위는 당월 영업 타겟 →\n증권 5건 이상·월 50만원 이상·상령일·\n생일·동의 만료 → 보장 부족 순.'],['PC 대화를 폰에서 이어갈 수 있나?','가능. 대화 이력과 나의 질문이\nPC·모바일에 똑같이 보임.'],['글씨가 너무 크거나 작음','오른쪽 위 [글씨 확대]를 끄면 원래 크기,\n켜면 한 단계 커짐(기본 ON).']];
    qa.forEach((q,i)=>{ const col=i%3,row=Math.floor(i/3); const x=M+col*4.1,y=1.85+row*1.72,w=3.9,h=1.58; L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.12,shadow:false}); const ql = q[0].split('\n').length, ay = y+0.6+(ql-1)*0.26; /* 두 줄 질문은 답을 한 줄만큼 내림. Q·A 글자는 본문과 같은 크기·줄간격으로 첫 줄 높이를 맞춘다 */ L.T(s,'Q',{x:x+0.22,y:y+0.17,w:0.3,h:0.34,fontSize:13,bold:true,color:C.blue,valign:'top',lineSpacingMultiple:1.1}); L.T(s,q[0],{x:x+0.55,y:y+0.17,w:w-0.72,h:0.34+(ql-1)*0.26,fontSize:13,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.1}); L.T(s,'A',{x:x+0.22,y:ay,w:0.3,h:0.3,fontSize:11.5,bold:true,color:C.g400,lineSpacingMultiple:1.3}); L.T(s,q[1],{x:x+0.55,y:ay,w:w-0.72,h:y+h-ay-0.08,fontSize:11.5,color:C.g700,lineSpacingMultiple:1.3}); });
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 9 · 용어 정리',title:'이 책에 나온 말, 한 장 정리',sub:'MeAI 화면에 그대로 쓰이는 이름',pageNo:no});
    const rows=[['용어','뜻','어디서 보나'],['MeAI 홈','MeAI에 들어오면 처음 열리는 화면. 추천 고객·고객 그룹·대화 카드가 한곳에 있음.','MeAI 첫 화면 · 어느 화면이든 왼쪽 위 [MeAI 홈]'],['일반대화 · 맞춤대화','일반대화는 무엇이든 묻는 창. 맞춤대화는 선택한 고객의 보장 내역을 읽고 답변.','MeAI 홈 대화 카드(흰색 · 검은색) · 고객찾기'],['사전조회 동의','보장 내역 조회 동의. 동의일부터 90일 동안 MeAI 맞춤대화 가능.','카드 D-n 칩 · MeAI 홈 "사전조회 동의 필요"'],['사전조회동의 D-n','동의 만료(90일)까지 남은 날. 만료되면 "필요", 철회하면 "철회".','MeAI 홈 카드 · 검색 팝업 · 고객찾기'],['MeAI 홈 노출 기간','사전조회 동의일로부터 3년 이내 고객만 MeAI 홈에 보임(맞춤대화 90일과 별개).','MeAI 홈 범례 안내'],['상품소개 동의 · AI 추천 고객','상품 소개에 동의한 고객. 카드에 빨간 리본이 붙음.','MeAI 홈 "상품제안 가능" · 카드 리본'],['보유 · 가망 · 이관','계약 있음 · 등록만 · 넘겨받음. 고객마다 셋 중 하나.','카드의 유형 칩'],['오늘의 추천 고객','이유가 붙은 카드 3장 × 세트 3개. 매일 밤 새로 계산해 다음 날 반영.','MeAI 홈 가운데'],['보장 기준 · 영업 기회','고객 그룹 탭. 보장 부족 7종 등 10개 / 날짜형 3개.','고객찾기 왼쪽'],['당월 영업 타겟','이번 달 영업 목표 대상. 우선순위 1(보라 태그).','고객찾기 그룹 · 카드 태그'],['상령일','보험 나이가 한 살 오르는 날. 그 전에 가입하면 유리.','고객찾기 [상령일 임박]'],['이 고객 한눈에 보기','펼친 카드의 여섯 칸. 가입·납입·부족 금액 등.','고객찾기 가운데'],['간편 분석 · 상세 분석','답변 모드. 일상 언어 / 약관·담보 정밀 비교.','대화 입력창 아래 (NEW)'],['용어 설명','답변 속 전문용어의 뜻을 목록으로 보여 줌.','PC 입력창 오른쪽 위 · 모바일 오른쪽 아래 (NEW)'],['글씨 확대','작은 글씨를 한 단계 크게. 기본 ON, 이 PC에 기억됨.','MeAI 홈·고객찾기·게시판 오른쪽 위']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?11:11, bold: ri===0||ci===0, color: ri===0? C.g600 : (ci===0? C.navy : C.g800), fill:{color: ri===0? C.g100 : C.white}, valign:'middle', margin:[3,8,3,8]}})));
    s.addTable(data,{x:M,y:1.85,w:W-2*M,colW:[2.9,5.4,3.83],rowH:0.3,border:{type:'solid',color:C.g200,pt:0.75}});
  }});
  // 한 장 요약 — 뽑아서 책상 옆에 두는 쪽. part 키 'sum' 은 deck.js 가 ctx.parts.sum 으로 적고(목차 '바쁘면 한 장 요약부터' 칸),
  // nav.py 가 1단 책갈피 '한 장 요약' 으로 넣는다. 목차는 '01'~'09' 만 읽으니 다른 쪽 번호는 그대로.
  // 버튼 이름·문구·숫자는 모두 책 본문에 이미 있는 것만 씀(PART 2·3·4·5·6·8·9 본문). 인쇄용이라 글자는 모두 10pt 이상.
  S.push({ part:'sum', fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'한 장 요약',title:'MeAI 홈, 이 한 장이면 시작',sub:'매일 아침 네 걸음 · 동의 칩 읽는 법 · 기억할 숫자 · 지킬 것 — 뽑아서 책상 옆에',pageNo:no});
    // 쪽 번호는 파트 첫 쪽 + 상대 위치(p0 목차와 같은 방식)라 쪽이 밀려도 따라감. ONLY=p9 빌드처럼 그 파트가 없으면 'p.-'(링크 없음)
    const rel = (k,d=0)=> ctx.parts[k] ? ctx.parts[k]+d : null;
    const pg = (n)=> 'p.'+(n||'-')+' →';
    // ① 매일 아침 네 걸음 — 번호 원 사이를 잇는 선. 걸음 이름 뒤엔 흰 바탕을 깔아 선이 글자를 지나가지 않게 함
    s.addShape('line',{x:0.82,y:2.07,w:10.2-0.82,h:0,line:{color:C.blue100,width:3}});
    const steps = [
      ['찾기','MeAI 홈 · 오늘의 추천 고객','[MeAI 고객찾기에서 열기]','카드 문장 = 고객에게 첫 말', rel('02')],
      ['고르기','고객찾기 · 한눈에 보기 6칸','[이 고객으로 맞춤대화 시작]','"사전조회동의 필요"면\n[사전조회동의 요청하기]', rel('04')],
      ['묻기','맞춤대화 · 추천 질문','"보장분석 해줘"','답 아래 꼬리질문 버튼으로 이어 묻기', rel('06')],
      ['연락하기','요약 리포트 · 카카오톡','[요약 리포트]','숫자·약관 근거 확인 뒤 내 말로 발송', rel('06',12)],
    ];
    steps.forEach(([name,screen,chip,tip,ref],i)=>{ const x = 0.6+i*3.08, w = 2.9;
      const nw = L.textW(name,16)*0.95+0.12;
      s.addShape('rect',{x:x+0.42,y:1.9,w:nw+0.13,h:0.34,fill:{color:C.white},line:{color:C.white,width:0}});
      L.circle(s,{x,y:1.85,d:0.44,fill:C.blue});
      L.T(s,String(i+1),{x,y:1.85,w:0.44,h:0.44,fontSize:13,bold:true,color:C.white,align:'center',valign:'middle'});
      L.T(s,name,{x:x+0.55,y:1.85,w:w-0.55,h:0.44,fontSize:16,bold:true,color:C.navy,valign:'middle'}); // 글자 상자는 넉넉히(파워포인트 줄바꿈 방지), 흰 바탕만 글자 폭
      L.T(s,screen,{x,y:2.45,w,h:0.28,fontSize:11,bold:true,color:C.blue,valign:'middle'});
      L.chip(s,{x,y:2.8,text:chip,fill:C.g100,color:C.navy,size:10.5,h:0.3});
      L.T(s,tip,{x,y:3.2,w,h:0.5,fontSize:11.5,color:C.g700,lineSpacingMultiple:1.15});
      L.T(s,pg(ref),{x,y:3.7,w:1.2,h:0.25,fontSize:10,color:C.g500,valign:'middle'});
      L.link(no,{x:x-0.05,y:3.68,w:0.9,h:0.29},ref);
    });
    // ② 동의 칩 → 다음 행동 (왼쪽 아래) — 칩 모양은 화면의 동의 칩을 흉내 냄. 유효 D-n 은 파랑(PART 4 동의 상태 세 패널과 같은 색)
    const consentPg = rel('05',3);
    L.T(s,'동의 칩 → 다음 행동',{x:0.6,y:4.15,w:4,h:0.3,fontSize:12.5,bold:true,color:C.navy,valign:'middle'});
    L.T(s,pg(consentPg),{x:6.55-1.2,y:4.15,w:1.2,h:0.3,fontSize:10,color:C.g500,align:'right',valign:'middle'});
    L.link(no,{x:6.55-0.85,y:4.13,w:0.9,h:0.34},consentPg);
    [['사전조회동의 D-n',C.blue,C.g300,'바로 [이 고객으로 맞춤대화 시작]'],
     ['사전조회동의 필요',C.red,C.red,'[사전조회동의 요청하기] → 15분 안팎 반영'],
     ['사전조회동의 철회',C.g400,C.g300,'회색 · 정보를 볼 수 없음 · 새 동의부터']].forEach(([c,tc,lc,t],i)=>{ const y = 4.52+i*0.6, rw = 6.55-0.6;
      L.R(s,{x:0.6,y,w:rw,h:0.5,fill:C.g50,line:null,radius:0.1});
      L.R(s,{x:0.72,y:y+0.09,w:1.75,h:0.32,fill:C.white,line:lc,radius:0.06});
      L.T(s,c,{x:0.72,y:y+0.09,w:1.75,h:0.32,fontSize:10.5,bold:true,color:tc,align:'center',valign:'middle'});
      L.T(s,'→',{x:2.55,y,w:0.3,h:0.5,fontSize:11.5,color:C.g400,align:'center',valign:'middle'});
      L.T(s,t,{x:2.92,y,w:6.55-2.92-0.1,h:0.5,fontSize:11.5,color:C.g800,valign:'middle'});
    });
    // ③ 기억할 숫자 (오른쪽 아래) — 운영 기준 네 개. 2×2 타일. 왼쪽 끝을 위 3·4번 걸음 칸(6.76 · 9.84)에 맞춤 — 6.8로 두면 0.04인치 어긋나 보임
    const gx3 = 0.6+2*3.08, gx4 = 0.6+3*3.08;
    L.T(s,'기억할 숫자',{x:gx3,y:4.15,w:4,h:0.3,fontSize:12.5,bold:true,color:C.navy,valign:'middle'});
    [['90일','맞춤대화 가능 · 동의일부터'],['3년 이내','MeAI 홈 노출 · 동의일부터'],['15분 안팎','동의 반영'],['9명','오늘의 추천 고객 · 3명 × 3세트']].forEach(([v,l],i)=>{
      const tw = W-M-gx4, x = i%2 ? gx4 : gx3, y = 4.52+Math.floor(i/2)*0.9;
      L.R(s,{x,y,w:tw,h:0.8,fill:C.white,line:C.g200,radius:0.1});
      L.T(s,v,{x:x+0.2,y:y+0.06,w:tw-0.3,h:0.42,fontSize:22,bold:true,color:C.navy,valign:'middle'});
      L.T(s,l,{x:x+0.2,y:y+0.48,w:tw-0.3,h:0.24,fontSize:10.5,color:C.g600,valign:'middle'});
    });
    // 띠 — 지킬 것(PART 9 다섯 가지 약속 줄임). 오른쪽 쪽 번호를 누르면 약속 쪽으로
    const promisePg = rel('09',1);
    L.R(s,{x:M,y:6.35,w:W-2*M,h:0.5,fill:C.navy,line:null,radius:0.1});
    L.T(s,[{text:'지킬 것',options:{bold:true}},{text:'     개인정보 넣지 않기 · 답변은 검증 후 사용 · 동의 없으면 보지 않기 · 자료 외부 반출 금지'}],{x:M+0.25,y:6.35,w:W-2*M-1.6,h:0.5,fontSize:12,color:C.white,valign:'middle'});
    L.T(s,pg(promisePg),{x:W-M-1.3,y:6.35,w:1.1,h:0.5,fontSize:10,color:C.white,transparency:30,align:'right',valign:'middle'});
    L.link(no,{x:W-M-0.95,y:6.35,w:0.95,h:0.5},promisePg);
  }});
  // 마무리 — 소유자 방송교안 23장: 나만의 영업비서, "MeAI 홈" OPEN / 찾는 영업에서 찾아가는 영업으로, MeAI가 함께합니다
  S.push({ fn:(pres,no)=>{
    L.NAV.push({ pageNo:no, title:'마무리' }); // PDF 책갈피 1단 '마무리'(nav.py)
    const s = pres.addSlide(); s.background={path:L.BG.closing};
    L.T(s,'MeAI',{x:W-6.5,y:1.2,w:5.9,h:2.4,fontSize:120,bold:true,color:'FFFFFF',transparency:82,align:'right'});
    // 위에 '마무리' + 네 걸음 칩(어느 것도 켜지 않음)
    L.T(s,'마무리',{x:M+0.2,y:0.55,w:4,h:0.34,fontSize:13,bold:true,color:C.blue100,valign:'middle'});
    let sx = M+0.2; ['1 찾기','2 고르기','3 묻기','4 연락하기'].forEach(t=>{ sx += L.chip(s,{x:sx,y:0.98,text:t,fill:C.blue700,color:'FFFFFF',size:12,h:0.38})+0.12; });
    L.T(s,'나만의 영업비서,\n“MeAI 홈” OPEN',{x:M+0.2,y:1.65,w:9,h:2.2,fontSize:44,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.15});
    L.T(s,'찾는 영업에서 찾아가는 영업으로, MeAI가 함께합니다',{x:M+0.2,y:3.95,w:9,h:0.6,fontSize:20,color:'FFFFFF',transparency:5,valign:'middle'});
    L.brandPill(s,{x:M+0.2,y:5.0});
    L.T(s,'본 자료의 전부·일부(수정 포함) 외부 제공·배포·게시(온/오프라인) 금지. 미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있음. 화면 속 고객 이름·숫자는 예시 데이터.',{x:M+0.2,y:6.1,w:W-2*M-0.2,h:0.5,fontSize:9.5,color:'FFFFFF',transparency:5,lineSpacingMultiple:1.3});
    L.T(s,FOOT,{x:M,y:H-0.42,w:8,h:0.25,fontSize:9,color:'FFFFFF',transparency:15}); L.T(s,String(no),{x:W-M-1,y:H-0.42,w:1,h:0.25,fontSize:9,color:'FFFFFF',align:'right'});
  }});
};
