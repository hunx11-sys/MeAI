module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, LEG } = ctx;
  const SRC1 = '출처: 2026년 8월 TA채널 MeAI 사용 데이터 분석';
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
  S.push({ part:'01', fn:(pres,no)=> L.divider(pres,{num:'01',title:'바뀌는 영업의 방향\n찾는 영업에서 찾아가는 영업으로',sub:'누구에게, 왜, 무슨 말로 연락할지 이제 MeAI가 먼저 골라 줌',learn:['보유 고객 열에 아홉이 방치상태인 이유','MeAI 홈이 바꾸는 하루의 순서 · 작동 원리','숫자로 보는 효과 · 매일 아침 루틴'],pageNo:no}) });
  // 1-1
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 지금까지',title:'보유 고객 열에 아홉은 방치상태',sub:'고객 한 명 영업하려면 누구에게 · 왜 지금 · 무슨 말을 할지 고민해야 했던 현실',pageNo:no});
    const qs = [['?','누구에게 연락하지?','목록을 하나씩 뒤져\n오늘 연락할 사람을 직접 골라야 했음'],['!','왜 지금이지?','연락할 명분을 스스로 만들어야 했음'],['"','무슨 말로 시작하지?','첫 마디를 고민하다 하루를 넘기기 일쑤']];
    qs.forEach((q,i)=> L.card(s,{x:M+i*4.1,y:1.85,w:3.9,h:2.05,icon:q[0],iconFill:C.g100,iconColor:C.g700,title:q[1],desc:q[2],titleSize:16,descSize:13}));
    // 7% · 2% 를 점 100개로: 빨간 점(영업 시도)보다 회색 점(방치)이 압도적으로 많음을 눈으로 보이게.
    // 숫자 글자는 글자색(navy), 빨강은 점에만. '미만'을 그대로 둬 점 7개가 '딱 7%'로 읽히지 않게 함
    [[7,'보유 고객 중 영업 시도','100명 중 7명도 안 됨'],[2,'이관 고객 중 영업 시도','100명 중 2명도 안 됨.\n넘겨받은 고객은\n더 묵혀 두게 됨']].forEach((q,i)=>{
      const x=M+i*4.1, y=4.2, w=3.9, h=2.05, n=q[0];
      L.R(s,{x,y,w,h,fill:C.white,line:C.g200,radius:0.14});
      for (let k=0;k<100;k++){ const r=Math.floor(k/10), c=k%10; L.circle(s,{x:x+0.25+c*0.168,y:y+0.2+r*0.168,d:0.13,fill:k<n?C.red:C.g200}); }
      L.T(s,'점 1개 = 1%',{x:x+0.25,y:y+1.86,w:1.7,h:0.17,fontSize:9,color:C.g500,valign:'middle'});
      s.addText([{text:n+'%',options:{fontSize:30,bold:true,color:C.navy,fontFace:L.FONT}},{text:' 미만',options:{fontSize:13,color:C.g600,fontFace:L.FONT}}],{x:x+2.1,y:y+0.2,w:1.72,h:0.55,isTextBox:true,margin:0,valign:'middle'});
      L.T(s,q[1],{x:x+2.1,y:y+0.8,w:1.72,h:0.3,fontSize:11.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,q[2],{x:x+2.1,y:y+1.15,w:1.72,h:0.75,fontSize:10.5,color:C.g600,lineSpacingMultiple:1.25});
    });
    // 셋째 칸: 소유자 방송교안 3장 문구
    L.R(s,{x:M+8.2,y:4.2,w:3.9,h:2.05,fill:C.navy,line:null,radius:0.12});
    L.T(s,'누구, 왜, 무엇을',{x:M+8.48,y:4.52,w:3.4,h:0.45,fontSize:18,bold:true,color:'FFFFFF',valign:'middle'});
    L.T(s,'1명에게 영업하기 위해\n준비해야 하는 많은 고민과 결정',{x:M+8.48,y:5.12,w:3.4,h:0.8,fontSize:12.5,color:'FFFFFF',transparency:12,lineSpacingMultiple:1.35});
    L.caption(s,{x:M,y:6.4,w:9,text:'출처: 2026년 3월 TA채널 보유고객 대비 설계/청약 진행 고객 비율',align:'left',size:10});
  }});
  // 1-2
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 이제는',title:'MeAI가 먼저 찾아오는 영업',sub:'바뀌는 것은 화면이 아니라 하루의 순서',pageNo:no});
    const rows = [['','찾는 영업 (지금까지)','찾아가는 영업 (MeAI 홈)'],['누구에게','목록을 뒤져 내가 고름','MeAI 홈이 오늘의 추천 고객을 보여 줌'],['왜 지금','명분을 스스로 만듦','"상령일이 2주 남았고…" 이유가 붙음'],['첫 마디','고민하다 미룸','카드의 이유 문장이 곧 첫 말'],['다음 행동','메뉴를 찾아 헤맴','[MeAI 고객찾기에서 열기] →\n[이 고객으로 맞춤대화 시작]']];
    const data = rows.map((r,ri)=> r.map((c,ci)=>({text:c, options:{fontFace:L.FONT,fontSize: ri===0?11:12.5, bold: ri===0 || ci===0, color: ri===0? C.g600 : (ci===2? C.blue700 : C.g800), fill:{color: ri===0? C.g100 : (ci===2? C.blue50 : C.white)}, valign:'middle', margin:[4,8,4,8]}})));
    s.addTable(data,{x:M,y:1.85,w:7.6,colW:[1.2,2.4,4.0],rowH:0.7,border:{type:'solid',color:C.g200,pt:0.75}});
    L.img(s,HERO('gb5_card_kim_z'),{x:8.5,y:1.85,w:4.2,h:4.45,valign:'top'});
    L.caption(s,{x:8.5,y:6.38,w:4.2,text:'「오늘의 추천 고객」 김민수 카드 (예시)',size:10});
    L.note(s,{x:M,y:5.6,w:7.6,h:0.8,label:'기억할 것',text:'발굴은 시스템이, 설득은 사람이. 오른쪽 김민수 고객처럼 "사전조회동의 필요"가 붙으면 맞춤대화 전에 동의 알림톡부터 발송(PART 5).',tone:'blue',size:12});
  }});
  // 1-3 카드에서 리포트까지
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 한 흐름',title:'클릭 두 번이면 대화 시작',sub:'서은아 고객(예시) 한 분으로 따라가 보기 · 화면 속 추천 질문 문장은 예시',pageNo:no});
    const steps = [['1','MeAI 홈 · 추천 카드','이유 문장을 읽고\n[MeAI 고객찾기에서 열기]',[HERO('gb5_card_seo_z')],2.45],['2','고객찾기 · 펼친 카드','한눈에 보기 6칸과 태그로\n상황 파악',[HERO('gb5_find_seo_card')],3.75],['3','맞춤대화 시작','추천 질문을 확인하고\n[이 고객으로 맞춤대화 시작]',[HERO('gb5_find_seo_right')],2.45],['4','요약 리포트 · 카카오톡','좋았던 답만 골라\n고객에게 발송',[HERO('gb5_kakao_clean')],2.6]];
    flowRow(s, steps, {y:1.85, h:3.05, ty:5.05});
    L.note(s,{x:M,y:6.12,w:W-2*M,h:0.72,label:'',text:'서은아 고객은 사전조회 동의 기간이 남아 있어(D-7) [이 고객으로 맞춤대화 시작]을 누르면 바로 열림.\n"사전조회동의 필요"가 붙은 고객은 동의 알림톡부터 발송(PART 5).',tone:'grey',size:12});
  }});
  // 1-4 MeAI 홈의 작동 원리 (소유자 방송교안 5장 문구)
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · MeAI가 하는 일',title:'MeAI 홈의 작동 원리',sub:'매일 밤 계산하고, 다음 날 이유와 함께 화면 구성',pageNo:no});
    bigSteps(s,{x:M,y:1.85,w:W-2*M,h:2.55,items:[{n:1,title:'고객 데이터',desc:'계약 · 동의 · 상령일 ·\n생일 · CRM'},{n:2,title:'매일 밤 계산',desc:'추천 고객과\n고객찾기 그룹을\n매일 자동으로\n다시 계산'},{n:3,title:'오늘의\n추천 고객 9명',desc:'3명 × 3세트로\nMeAI 홈에 표시'},{n:4,title:'점수 대신\n이유 한 문장',desc:'왜 지금 이 고객인지,\n한 문장과 태그로\n(동의 상태 칩도 함께)'},{n:5,title:'고객찾기에서 열기',desc:'카드 버튼으로\n고객찾기 이동\n→ 동의 고객은\n바로 맞춤대화 시작'}],activeIdx:3});
    const pr = [['발굴은 시스템, 설득은 사람','고르는 시간을 없애고,\n만나는 일에 집중'],['고객찾기 그룹은 두 갈래','보장 기준 · 영업 기회\n(예: 암진단비 부족 · 상령일 임박)'],['결과는 다음 날 반영','고객 데이터와 추천 결과 모두 해당\n기준 시각은 화면의 "최근 업데이트"']];
    pr.forEach((p,i)=> L.card(s,{x:M+i*4.1,y:4.65,w:3.9,h:1.55,title:p[0],desc:p[1],titleSize:15,descSize:12}));
    L.caption(s,{x:M,y:6.35,w:W-2*M,text:'※ MeAI 홈에 노출되는 고객은 사전조회 동의일로부터 1년 이내 · 맞춤대화는 동의일부터 90일 동안 가능',align:'left',size:10});
  }});
  // 1-5 숫자로 보기
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 숫자로 보기',title:'MeAI를 쓴 경우, 체결전환율 2.8배',sub:'열 명 중 아홉 명이 사용 경험 있음 · MeAI 홈은 매일 아침 열어 볼 이유를 만들어 줌',pageNo:no});
    // 세 칸: 사용 경험(링) · 체결전환율(짝 막대 둘, 같은 눈금 0~40) · 질문 수별 가계약(계단 막대). 활동일 표는 다음 쪽으로
    const pw=[3.2,5.3,3.35], pg=(W-2*M-pw.reduce((a,b)=>a+b,0))/2, py=1.85, ph=4.45;
    let px=M; const P=pw.map(w=>{ const p={x:px,w}; px+=w+pg; return p; });
    P.forEach(p=> L.R(s,{x:p.x,y:py,w:p.w,h:ph,fill:C.white,line:C.g200,radius:0.14}));
    { const p=P[0], d=2.3, RD=2.0, rx=p.x+(p.w-d)/2, ry=2.57;
      L.T(s,'MeAI 사용 경험',{x:p.x+0.28,y:2.07,w:p.w-0.5,h:0.3,fontSize:13,bold:true,color:C.navy});
      s.addChart('doughnut',[{name:'사용 경험',labels:['사용','미사용'],values:[91.1,8.9]}],{x:rx,y:ry,w:d,h:d,layout:{x:(d-RD)/2/d,y:(d-RD)/2/d,w:RD/d,h:RD/d},holeSize:78,chartColors:['3182F6','F2F4F6'],showLegend:false,showValue:false,showPercent:false,showLabel:false,firstSliceAng:0,dataBorder:{pt:1.5,color:'FFFFFF'}});
      // LibreOffice(PDF 를 만드는 쪽)는 holeSize 를 무시하고 구멍을 바깥 지름의 약 50% 로 그림 → 26pt 글자도 고리에 닿음.
      // 그래서 흰 원을 가운데 덮어 두 프로그램 모두 holeSize 78 모양이 되게 함.
      // 고리 바깥 지름은 layout 으로 RD(2.0in)에 고정(자동 배치면 PowerPoint 와 LibreOffice 의 지름이 달라 흰 원이 고리를 먹을 수 있음).
      // 흰 원은 RD 의 77% — PowerPoint 의 실제 구멍(78%)보다 조금 작아 거기서는 보이지 않음
      { const hd=RD*0.77; L.circle(s,{x:rx+d/2-hd/2,y:ry+d/2-hd/2,d:hd,fill:C.white}); }
      // 30pt 는 시제품에서 고리에 닿아 26pt
      L.T(s,'91.1%',{x:rx,y:ry+d/2-0.32,w:d,h:0.64,fontSize:26,bold:true,color:C.navy,align:'center',valign:'middle'});
      L.T(s,'10,968명이\n한 번 이상 사용',{x:p.x+0.28,y:5.15,w:p.w-0.56,h:0.6,fontSize:12,color:C.g600,align:'center',lineSpacingMultiple:1.25});
    }
    { const p=P[1], cw2=(p.w-0.5)/2;
      L.T(s,'체결전환율 · 미활용 → 활용',{x:p.x+0.28,y:2.07,w:p.w-0.5,h:0.3,fontSize:13,bold:true,color:C.navy});
      [['전체',[12.7,35.4],'2.8배'],['같은 FP 고객끼리',[9.0,36.0],'4배']].forEach((q,i)=>{ const cx=p.x+0.25+i*cw2;
        L.T(s,q[2],{x:cx+0.1,y:2.63,w:cw2-0.2,h:0.55,fontSize:28,bold:true,color:C.navy,align:'center',valign:'middle'});
        L.bars(s,{x:cx+0.15,y:3.2,w:cw2-0.3,h:2.3,dir:'col',labels:['미활용','활용'],values:q[1],colors:[C.g300,C.blue],max:40,gap:55,fmt:v=>v.toFixed(1)+'%',valueSize:13,catSize:11.5});
        L.T(s,q[0],{x:cx,y:5.85,w:cw2,h:0.3,fontSize:12,bold:true,color:C.g700,align:'center',valign:'middle'});
      });
    }
    { const p=P[2];
      L.T(s,'많이 질문할수록\n늘어나는 영업기회',{x:p.x+0.28,y:2.07,w:p.w-0.5,h:0.5,fontSize:12.5,bold:true,color:C.navy,lineSpacingMultiple:1.1});
      L.T(s,'2.3배',{x:p.x+0.28,y:2.63,w:p.w-0.5,h:0.55,fontSize:28,bold:true,color:C.navy,valign:'middle'});
      L.bars(s,{x:p.x+0.2,y:3.2,w:p.w-0.4,h:2.3,dir:'col',labels:['질문 1개','2개','3개 이상'],values:[11.99,17.02,27.79],colors:[C.g300,C.g300,C.purple],max:32,fmt:v=>v.toFixed(2)+'건',valueSize:12,catSize:11,catBoldIdx:2});
      L.T(s,'질문 1건 대비 3건 이상 · 평균 가계약 수',{x:p.x+0.15,y:5.85,w:p.w-0.3,h:0.3,fontSize:10.5,color:C.g600,align:'center',valign:'middle'});
    }
    L.caption(s,{x:M,y:6.42,w:8,text:SRC1,align:'left',size:10});
    const nx={x:8.73,y:6.42,w:4,h:0.28};
    L.T(s,'활동일별 비교는 다음 쪽 →',Object.assign({fontSize:10,color:C.g500,align:'right',valign:'middle'},nx));
    L.link(no,nx,no+1);
  }});
  // 1-5b 활동일별 비교 (새 쪽 · 파트 키 없음 — 목차 쪽 번호는 ctx.parts 로 계산되어 자동으로 밀림)
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 숫자로 보기 · 활동일',title:'한 달에 10일 이상 쓰면, 평균 가계약 5.4배',sub:'7월 MeAI 활동일별 비교 · 10일 이상 vs 미사용 · MeAI 홈을 아침마다 여는 습관이 곧 활동일',pageNo:no});
    const labels=['미사용','1일','2~4일','5~9일','10일 이상'];
    const bx0=2.15, bw0=8.2, slot=bw0/5;
    L.T(s,'평균 가계약(건)',{x:M,y:1.95,w:1.5,h:0.3,fontSize:11,bold:true,color:C.g700});
    // 미사용은 회색 기준, 쓴 날은 연한 파랑, 10일 이상만 강조. 항목 이름은 아래 숫자 줄 첫 행이 대신함
    L.bars(s,{x:bx0,y:1.95,w:bw0,h:3.0,dir:'col',plot:{x:0,y:0.1,w:1,h:0.9},labels,values:[10.22,19.81,26.35,38.47,55.04],colors:[C.g300,C.blue100,C.blue100,C.blue100,C.blue],max:60,gap:70,fmt:v=>v.toFixed(2),valueSize:14,cats:false});
    // 숫자 줄(옛 표의 25개 숫자 그대로): 칸 i 는 막대 칸(2.15+1.64*i)에 맞춤. 둘째 축은 쓰지 않음
    const rows=[
      ['7월 활동일',labels,{h:0.34,size:12.5,bold:true,color:C.navy}],
      ['인원',['5,987명','1,835명','2,487명','1,372명','362명'],{h:0.34,size:11,color:C.g600}],
      ['매출 보유율',['53.1%','79.6%','85.7%','92.5%','94.8%'],{h:0.5,size:11.5,bold:true,color:C.navy,meter:[53.1,79.6,85.7,92.5,94.8]}],
      ['매출자 평균',['256,194원','310,383원','328,237원','378,083원','408,166원'],{h:0.34,size:11,color:C.g600}],
    ];
    let ry=5.03;
    rows.forEach((r,ri)=>{ const o=r[2];
      if (ri>0) s.addShape('line',{x:M,y:ry,w:10.35-M,h:0,line:{color:C.g200,width:0.75}});
      L.T(s,r[0],{x:M,y:ry,w:1.5,h:o.h,fontSize:10.5,bold:true,color:C.g600,valign:'middle'});
      r[1].forEach((t,i)=>{ const sx=bx0+slot*i;
        if (o.meter){
          L.T(s,t,{x:sx,y:ry+0.04,w:slot,h:0.26,fontSize:o.size,bold:true,color:o.color,align:'center',valign:'middle'});
          const gw=slot*0.62, gx=sx+(slot-gw)/2;
          L.R(s,{x:gx,y:ry+0.34,w:gw,h:0.07,fill:C.g100,line:null,radius:0.035});
          L.R(s,{x:gx,y:ry+0.34,w:gw*o.meter[i]/100,h:0.07,fill:i===0?C.g400:C.blue,line:null,radius:0.035});
        } else L.T(s,t,{x:sx,y:ry,w:slot,h:o.h,fontSize:o.size,bold:!!o.bold,color:o.color,align:'center',valign:'middle'});
      });
      ry+=o.h;
    });
    // 오른쪽 결론 칸
    const cx0=10.55, cw0=2.18, tx=cx0+0.25, tw=cw0-0.4;
    L.R(s,{x:cx0,y:1.95,w:cw0,h:4.55,fill:C.blue50,line:null,radius:0.14});
    L.T(s,'10일 이상 vs 미사용',{x:tx,y:2.15,w:tw,h:0.3,fontSize:11,bold:true,color:C.blue});
    L.T(s,'5.4배',{x:tx,y:2.5,w:tw,h:0.75,fontSize:40,bold:true,color:C.navy,valign:'middle'});
    L.T(s,'평균 가계약\n10.22건 → 55.04건',{x:tx,y:3.25,w:tw,h:0.6,fontSize:11.5,color:C.g700,lineSpacingMultiple:1.25});
    s.addShape('line',{x:tx,y:4.05,w:cw0-0.5,h:0,line:{color:C.blue100,width:0.75}});
    L.T(s,'1.8배',{x:tx,y:4.2,w:tw,h:0.6,fontSize:30,bold:true,color:C.navy,valign:'middle'});
    L.T(s,'매출 보유율\n53.1% → 94.8%',{x:tx,y:4.8,w:tw,h:0.6,fontSize:11.5,color:C.g700,lineSpacingMultiple:1.25});
    L.T(s,'한 달에 며칠 쓰느냐',{x:tx,y:5.75,w:tw,h:0.5,fontSize:11.5,bold:true,color:C.g800});
    L.caption(s,{x:M,y:6.62,w:9,text:SRC1,align:'left',size:10});
  }});
  // 1-6 매일 아침 미리보기
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 1 · 그래서 이 책은',title:'매일 아침, MeAI 홈에서 시작',sub:'버튼만 누르면 다음 화면으로 연결(화면 속 질문 문장은 예시) · PART 2~4 화면 · PART 7 루틴 · PART 8 묻는 법',pageNo:no});
    // 네 걸음(찾기·고르기·묻기·연락하기)에 칸을 맞춘다. 연락하기는 아래 안내 줄에서.
    const items=[[null,'MeAI 홈 열기','내 고객 숫자 4개와\n"사전조회 동의 필요" 확인',[HERO('fix_gate_stats_2row')],2.75],['1','찾기 · 추천 카드','오늘 연락할 내 고객을\n추천 카드로 찾기',[HERO('gb5_card_seo_z')],2.45],['2','고르기 · 고객찾기','한눈에 보기 6칸과 태그로\n상황을 보고 연락할 고객 선택',[HERO('gb5_find_seo_card')],3.5],['3','묻기 · 추천 질문','추천 질문을 누르거나\n[이 고객으로 맞춤대화 시작]',[HERO('gb5_find_seo_right')],2.45]];
    flowRow(s, items, {y:1.85, h:2.95, ty:4.9});
    L.note(s,{x:M,y:6.02,w:W-2*M,h:0.8,label:'기억할 것',text:'찾기 → 고르기 → 묻기 → 연락하기. 마지막 걸음은 카드의 첫 말로 연락하고 리포트까지 발송.\n카드 문장은 고객에게 첫 말, 추천 질문은 MeAI에게 첫 질문.',tone:'dark',size:12});
  }});
};
