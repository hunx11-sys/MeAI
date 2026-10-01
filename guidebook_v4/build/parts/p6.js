module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG, LEG } = ctx;
  const capUnder = (s,g,text,o={})=> L.caption(s,Object.assign({x:g.x,y:g.y+g.h+0.03,w:g.w,text,size:10},o));
  // 캡처 위 테두리(CSS 좌표) — 클립 원점·배율 반영
  const outline=(s,g,x1,y1,x2,y2,{clip={x:0,y:0},dsf=2,color=C.blue,width=1.75,radius=0.06}={})=>{ const k=dsf*g.scale; s.addShape('roundRect',{x:g.x+(x1-clip.x)*k,y:g.y+(y1-clip.y)*k,w:(x2-x1)*k,h:(y2-y1)*k,fill:{type:'none'},line:{color,width},rectRadius:radius}); };
  // 캡처 속 해지·전환·정리로 읽히는 문장을 그 자리 바탕색으로 덮는다(방송판과 같은 곳). rects = 캡처 픽셀 [x1,y1,x2,y2]
  const mask=(s,g,rects,color='F8F9FA')=>rects.forEach(([x1,y1,x2,y2])=>s.addShape('rect',{x:g.x+x1*g.scale,y:g.y+y1*g.scale,w:(x2-x1)*g.scale,h:(y2-y1)*g.scale,fill:{color},line:{color,width:0}}));
  // 번호 목록(한 줄 설명 + 필요하면 빨간 주의 줄). desc 는 '\n' 으로 줄을 나눈다
  const miniList=(s,{x,y,w,items,ts=13.5,ds=11,gap=0.09})=>{ const lh=ds*1.2*1.15/72; let cy=y;
    items.forEach(it=>{ L.badge(s,{x,y:cy+0.01,n:it.n,d:0.3}); L.T(s,it.title,{x:x+0.42,y:cy,w:w-0.42,h:0.32,fontSize:ts,bold:true,color:C.navy,valign:'middle'});
      const runs=[]; const dl=it.desc?it.desc.split('\n'):[]; dl.forEach((t,i)=>runs.push({text:t,options:{color:C.g600,fontSize:ds,fontFace:L.FONT,breakLine:i<dl.length-1||!!it.warn}}));
      if(it.warn) runs.push({text:it.warn,options:{color:C.red,bold:true,fontSize:ds,fontFace:L.FONT}});
      const nl=dl.length+(it.warn?1:0); if(nl) s.addText(runs,{x:x+0.42,y:cy+0.32,w:w-0.42,h:nl*lh+0.04,isTextBox:true,margin:0,valign:'top',lineSpacingMultiple:1.15});
      cy += 0.32 + nl*lh + gap; });
    return cy; };
  S.push({ part:'06', fn:(pres,no)=> L.divider(pres,{num:'06',title:'대화 이어가기\n일반대화 · 맞춤대화와 새 기능',sub:'MeAI 홈에서 들어온 대화 화면과 새 기능 익히기',learn:['MeAI 홈에서 누르기만 하면 열리는 대화','일반대화 · 맞춤대화 화면 구성','NEW 용어 설명 · 모드 변경','꼬리질문 · 요약 리포트','모바일에서 들어가기'],pageNo:no}) });
  // 6-0 MeAI 홈에서 대화 열기 — 클릭 세 길 (방송판 12장)
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 대화 열기',title:'MeAI 홈에서 누르기만 하면 MeAI 시작',sub:'MeAI 즉시 대화 = 흰 카드, 검은 카드, 추천 카드',pageNo:no});
    const lw = 6.3;
    // 홈 인사 문구 + 대화 카드 두 장 (clip 150,85 · 흰 카드 160..712 / 검은 카드 728..1280, y 200..332)
    const g = L.img(s,HERO('bc3_home_cards'),{x:M,y:1.85,w:lw,h:1.45,valign:'top',align:'left'});
    const oc = {clip:{x:150,y:85},dsf:2};
    outline(s,g,158,198,714,334,oc); outline(s,g,726,198,1282,334,oc);
    L.pin(s,g,160,200,1,oc); L.pin(s,g,728,200,2,oc);
    let y = g.y+g.h+0.18;
    L.R(s,{x:M,y,w:lw,h:0.98,fill:C.blue50,line:null,radius:0.14});
    L.T(s,'화면 문구',{x:M+0.25,y:y+0.13,w:2,h:0.26,fontSize:11,bold:true,color:C.blue,valign:'middle'});
    L.T(s,'“어떤 대화를 시작할지만 고르면, 나머지는 MeAI가 준비합니다.”',{x:M+0.25,y:y+0.45,w:lw-0.45,h:0.38,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
    y += 0.98+0.15;
    L.R(s,{x:M,y,w:lw,h:1.0,fill:C.white,line:C.g200,radius:0.14});
    L.img(s,HERO('bc3_home_btn'),{x:M+0.25,y:y+0.26,w:1.3,h:0.48,round:false,shadow:false,align:'left'});
    L.T(s,'길을 잃으면',{x:M+1.8,y:y+0.13,w:4.2,h:0.28,fontSize:13,bold:true,color:C.navy,valign:'middle'});
    L.T(s,'어느 화면이든 왼쪽 위 [MeAI 홈]을 누르면\n처음 화면으로 이동',{x:M+1.8,y:y+0.45,w:4.3,h:0.44,fontSize:11.5,color:C.g700,valign:'top',lineSpacingMultiple:1.1});
    L.caption(s,{x:M,y:y+1.06,w:lw,text:'※ 화면의 이름·숫자는 예시',align:'left',size:10});
    // 오른쪽: 대화를 여는 세 길
    const x = 7.15, w = W-M-x;
    const paths = [
      [HERO('bc3_general_home'),'일반대화','[일반대화] 카드\n→ 질문 예시 누르기','무엇이든 질문 · 바로 시작'],
      [HERO('bc3_popup_modal'),'맞춤대화','[맞춤대화] 카드 → 이름 한 글자\n→ [맞춤대화]','고객 한 명의 보장 내역으로 답변'],
      [HERO('bc3_find_km_right'),'추천 카드에서','[MeAI 고객찾기에서 열기]\n→ 추천 질문 → 전송(↑)','질문이 채워진 채로 열림'],
    ];
    paths.forEach(([f,title,stp,desc],i)=>{ const yy=1.85+i*1.42, h=1.3;
      L.R(s,{x,y:yy,w,h,fill:C.white,line:C.g200,radius:0.14,shadow:true});
      const t = L.img(s,f,{x:x+w-1.72,y:yy+0.1,w:1.6,h:1.1,align:'right',radius:14});
      const tw = t.x-(x+0.62)-0.12;
      L.badge(s,{x:x+0.18,y:yy+0.14,n:i+1,d:0.34});
      L.T(s,title,{x:x+0.62,y:yy+0.12,w:tw,h:0.36,fontSize:14.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,stp,{x:x+0.62,y:yy+0.5,w:tw,h:0.44,fontSize:12,bold:true,color:C.blue,valign:'top',lineSpacingMultiple:1.05});
      L.T(s,desc,{x:x+0.62,y:yy+0.96,w:tw,h:0.24,fontSize:11,color:C.g600,valign:'middle'}); });
    L.R(s,{x:M,y:6.14,w:W-2*M,h:0.66,fill:C.navy,line:null,radius:0.14});
    s.addText([{text:'기억할 것   ',options:{bold:true,color:C.blue100,fontSize:14,fontFace:L.FONT}},{text:'누르고 → 고르고 → 보내기. 클릭만으로 편하게 시작하는 MeAI 대화',options:{bold:true,color:'FFFFFF',fontSize:15,fontFace:L.FONT}}],{x:M+0.3,y:6.14,w:W-2*M-0.6,h:0.66,isTextBox:true,margin:0,valign:'middle'});
  }});
  // 6-1 두 가지 대화
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 두 가지 대화',title:'일반대화 vs 맞춤대화',sub:'고객을 정하지 않으면 일반대화, 정하면 맞춤대화',pageNo:no});
    const col=(x,kicker,title,items,entry,accent,fill)=>{
      L.R(s,{x,y:1.85,w:5.95,h:4.3,fill,line:null,radius:0.16});
      L.T(s,kicker,{x:x+0.4,y:2.1,w:5.2,h:0.3,fontSize:11.5,bold:true,color:accent});
      L.T(s,title,{x:x+0.4,y:2.42,w:5.2,h:0.55,fontSize:20,bold:true,color:C.navy,valign:'middle'});
      items.forEach((t,i)=>{ L.T(s,'✓',{x:x+0.4,y:3.12+i*0.47,w:0.35,h:0.4,fontSize:13,bold:true,color:accent,valign:'middle'}); L.T(s,t,{x:x+0.8,y:3.12+i*0.47,w:4.8,h:0.4,fontSize:13.5,color:C.g800,valign:'middle'}); });
      L.T(s,'들어가는 곳',{x:x+0.4,y:5.08,w:5.2,h:0.28,fontSize:11,bold:true,color:C.g500});
      L.T(s,entry,{x:x+0.4,y:5.38,w:5.2,h:0.6,fontSize:11.5,color:C.g700,valign:'top',lineSpacingMultiple:1.25});
    };
    col(M,'일반대화','무엇이든 물어보는 창',['상품·특약 개념 질문','자사·타사 보장 비교','고객 설득 화법 만들기','약관 지식 확인'],'MeAI 홈 [일반대화] 카드 · 모바일 [MeAI 일반대화]\n영업포탈 CRM 리스트 [MeAI 일반대화] (10/2부터)',C.blue,C.blue50);
    col(M+6.18,'맞춤대화','고객 1명에 맞춘 보장분석부터 설계까지',['고객 선택 → 보장분석','부족 보장 · 제안 우선순위','상세설계 · 가계약 요청','요약 리포트 → 카카오톡'],'MeAI 홈 [맞춤대화] 카드 · 고객찾기 · 모바일 [MeAI]\n영업포탈 CRM 리스트 [MeAI 맞춤대화] (10/2부터)',C.red,C.red50);
    L.note(s,{x:M,y:6.3,w:W-2*M,h:0.6,label:'',text:'고객을 만나기 전에는 꼭 맞춤대화로 준비',tone:'dark',size:12.5});
  }});
  // 6-1b 일반대화 화면 (방송판 13장)
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 일반대화 화면',title:'일반대화는 “무엇이든 물어보세요”',sub:'고객을 정하지 않고 상품·약관·화법을 일반대화에서',pageNo:no});
    const g = L.img(s,HERO('bc3_general_crop'),{x:M,y:1.85,w:6.6,h:4.72,valign:'top',align:'left'});
    const o = {clip:{x:0,y:0},dsf:2,d:0.34};
    [[182,48],[165,161],[165,285],[445,487],[445,776],[150,768]].forEach(([px,py],i)=>L.pin(s,g,px,py,i+1,o));
    outline(s,g,484,689,898,716,{color:C.red,width:1.5,radius:0.03});
    capUnder(s,g,'MeAI 홈 [일반대화] 카드로 들어온 첫 화면',{align:'left'});
    const x = g.x+g.w+0.4, w = W-M-x;
    const endY = miniList(s,{x,y:1.85,w,items:[
      {n:1,title:'[MeAI 홈]',desc:'누르면 MeAI 홈으로 이동'},
      {n:2,title:'약관 검색 · 사용 가이드',desc:'약관 원문 찾기 · 화면 사용법'},
      {n:3,title:'대화 이력',desc:'월별로 쌓임 · 누르면 이어서 질문'},
      {n:4,title:'질문 예시 탭 3개',desc:'보장 비교 · 지식 검색 · 자주하는 질문 → 누르면 시작'},
      {n:5,title:'입력창',desc:'말하듯 쓰고 전송(↑) · [상품 선택]으로 상품 고르기',warn:'빨간 테두리 안내대로 이름·연락처는 넣지 않음'},
      {n:6,title:'[새로 대화하기]',desc:'주제가 바뀌면 새로 열기'}]});
    // 이럴 때 사용
    const py = Math.max(endY+0.02, 5.8), ph = 0.84;
    L.R(s,{x,y:py,w,h:ph,fill:C.blue50,line:null,radius:0.14});
    const lbl='이럴 때 사용', lbw=L.textW(lbl,12)+0.25;
    L.T(s,lbl,{x:x+0.2,y:py+0.1,w:lbw,h:0.3,fontSize:12,bold:true,color:C.blue,valign:'middle'});
    let cx=x+0.2+lbw, cy=py+0.1; const ph1=0.3;
    ['상품·특약 개념','자사·타사 보장 비교','고객 설득 화법','약관 지식 확인'].forEach(t=>{ const pw=L.textW(t,11)+0.36; if(cx+pw>x+w-0.15){ cx=x+0.2+lbw; cy+=ph1+0.08; }
      L.R(s,{x:cx,y:cy,w:pw,h:ph1,fill:C.white,line:C.blue100,radius:ph1/2}); L.T(s,t,{x:cx,y:cy,w:pw,h:ph1,fontSize:11,bold:true,color:C.navy,align:'center',valign:'middle'}); cx+=pw+0.1; });
  }});
  // 6-2 PC 화면 구성
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · PC 맞춤대화 화면',title:'맞춤대화는 “고객 1명에 맞춘 보장분석부터 설계까지”',sub:'선택한 고객의 보장 내역을 읽고 답변',pageNo:no});
    const g = L.img(s,HERO('term_pc_full'),{x:M,y:1.85,w:8.75,h:5.1,valign:'top',align:'left'});
    const clip={x:0,y:0};
    L.pin(s,g,272,155,1,{clip}); L.pin(s,g,272,305,2,{clip}); L.pin(s,g,272,480,3,{clip}); L.pin(s,g,150,788,4,{clip}); L.pin(s,g,1012,27,5,{clip}); L.pin(s,g,456,215,6,{clip}); L.pin(s,g,456,500,7,{clip}); L.pin(s,g,1270,726,8,{clip}); L.pin(s,g,456,800,9,{clip});
    L.caption(s,{x:W-M-6,y:1.37,w:6,text:'※ 이름·숫자는 예시 · 개발 중 화면이라 왼쪽 위 [MeAI 홈] 자리에 로고가 보임',align:'right',size:10});
    // 번호 간격을 일정하게(설명 없는 ④·⑨도 한 칸을 차지), ①만 설명이 두 줄
    const evenList=(x,y,w,pitch,items)=>{ let cy=y; items.forEach(it=>{ L.badge(s,{x,y:cy+0.02,n:it.n,d:0.3}); L.T(s,it.title,{x:x+0.42,y:cy,w:w-0.42,h:0.32,fontSize:13,bold:true,color:C.navy,valign:'middle'}); const nl=it.desc?it.desc.split('\n').length:1; if(it.desc) L.T(s,it.desc,{x:x+0.42,y:cy+0.33,w:w-0.42,h:nl*0.21+0.04,fontSize:11,color:C.g600,lineSpacingMultiple:1.1}); cy += pitch + (nl-1)*0.21; }); };
    evenList(g.x+g.w+0.45,1.85,W-M-(g.x+g.w+0.45),0.56,[
      {n:1,title:'담당 고객',desc:"사전조회동의 남은 일수\n(화면엔 '보장분석 동의')"},
      {n:2,title:'약관 검색·사용 가이드',desc:'전사 약관 원문과 화면 안내'},
      {n:3,title:'대화 이력',desc:'월별 목록 · 누르면 이어서 질문'},
      {n:4,title:'새로 대화하기'},
      {n:5,title:'상단 버튼 3개',desc:'보장 분석 · 사용중인 정보 수정 · 요약 리포트'},
      {n:6,title:'내 질문',desc:'복사·편집·저장 아이콘'},
      {n:7,title:'MeAI 답변',desc:'잘 갖춰진 것 → 비어 있는 것 → 할 일'},
      {n:8,title:'NEW [용어] 버튼',desc:'입력창 오른쪽 위'},
      {n:9,title:'입력창'}]);
  }});
  // 6-2b 맞춤대화 시작 화면
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 맞춤대화 시작 화면',title:'맞춤대화는 “보장분석 해줘” 한 마디로 시작',pageNo:no});
    // 위 = 담당 고객 + 고객 정보 입력 카드(CSS y12~532), 아래 = 총 보험료~첫 상품 줄(CSS x424~, y688~1109)을 크게
    const gt = L.img(s,HERO('fix_custom_top'),{x:M,y:1.5,w:5.82,h:2.45,valign:'top',align:'left'});
    const gb = L.img(s,HERO('fix_custom_bottom'),{x:M,y:gt.y+gt.h+0.12,w:5.82,h:6.95-(gt.y+gt.h+0.12),valign:'top',align:'left'});
    const ot={clip:{x:0,y:12},dsf:2}, ob={clip:{x:424,y:688},dsf:2};
    L.pin(s,gt,218,157,1,ot); L.pin(s,gt,470,81,2,ot); L.pin(s,gt,470,290,3,ot); L.pin(s,gt,470,470,4,ot);
    L.pin(s,gb,457,760,5,ob); L.pin(s,gb,818,758,6,ob); L.pin(s,gb,457,911,7,ob); L.pin(s,gb,457,983,8,ob);
    const lx = M+5.82+0.4, lw = 12.73-lx;
    L.caption(s,{x:lx,y:1.12,w:12.73-lx,text:'※ 이름·숫자는 예시 · 정보 칸이 열려 있으면 아래가 흐림(^로 접으면 밝아짐)',align:'right',size:10});
    // 제목 왼쪽 · 설명 오른쪽 한 줄씩(방송교안 15장 배치). desc 의 '\n' 은 두 줄
    const tw = 2.4, dx = lx+0.42+tw+0.1, dw = 12.73-dx;
    const row=(y,n,title,desc)=>{ const nl=desc.split('\n').length, h=nl>1?0.52:0.36;
      L.badge(s,{x:lx,y:y+(h-0.3)/2,n,d:0.3});
      L.T(s,title,{x:lx+0.42,y,w:tw,h,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,desc,{x:dx,y,w:dw,h,fontSize:11.5,color:C.g600,valign:'middle',lineSpacingMultiple:1.1});
      return y+h+0.14; };
    let ry = 1.55;
    ry = row(ry,1,'담당 고객','고객이 정해진 채로 열렸다는 표시');
    ry = row(ry,2,'고객 정보 입력','미리 넣으면 고객 맥락을 살려 답변');
    ry = row(ry,3,'다섯 칸, 아는 것만','병력·가족력이 핵심\n이름·연락처는 넣지 않음');
    ry = row(ry,4,'[입력 완료]로 반영','고칠 땐 [사용중인 정보 수정]');
    // 소유자 문구(방송교안 15장)
    L.R(s,{x:lx,y:ry-0.04,w:lw,h:0.46,fill:C.blue50,line:null,radius:0.12});
    s.addText([{text:'아직 고객에 대한 정보를 잘 모르겠다면 ',options:{color:C.g800,fontSize:11.5,fontFace:L.FONT}},{text:'“입력하지 않고 넘어가기”',options:{color:C.blue,bold:true,fontSize:11.5,fontFace:L.FONT}}],{x:lx+0.22,y:ry-0.04,w:lw-0.4,h:0.46,isTextBox:true,margin:0,valign:'middle'});
    ry = Math.max(ry+0.56, gb.y+0.05);
    ry = row(ry,5,'선택 계약 총 보험료','"지금 매달 이만큼 내고 계세요"로 시작');
    ry = row(ry,6,'약관DB 준비 상태','구성 안 된 상품은 답이 부정확할 수 있음');
    ry = row(ry,7,'담보별로 거르기','암 · 뇌/심장 · 치료비 등 버튼으로 고르기');
    ry = row(ry,8,'상품 전체 선택','관계없는 계약은 체크를 풀면 분석에서 빠짐');
    // 다 정한 뒤 첫 질문
    const by = Math.max(ry+0.02, 6.3), bh = 6.95-by;
    L.R(s,{x:lx,y:by,w:lw,h:bh,fill:C.navy,line:null,radius:0.12});
    s.addText([{text:'첫 질문은 버튼 하나   ',options:{bold:true,color:C.blue100,fontSize:12,fontFace:L.FONT}},{text:'입력창 위 [보장분석 해줘]로 전체 그림부터',options:{bold:true,color:'FFFFFF',fontSize:12.5,fontFace:L.FONT}}],{x:lx+0.25,y:by,w:lw-0.4,h:bh,isTextBox:true,margin:0,valign:'middle'});
  }});
  // 6-3 답변 읽는 법
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 답변 읽는 법',title:'맞춤대화는 분석 → 제안 → 다음 행동 순서',sub:'상담 순서에 맞춘 답변 구성',pageNo:no});
    // term/36_pc_tall_full_off(dsf 2)에서 CSS x420 부터 다시 자름 → 글자(x490) 왼쪽에 핀 자리
    const g1 = L.img(s,HERO('bc2_answer_top'),{x:M,y:1.85,w:5.95,h:3.62,valign:'top',align:'left'});
    const g2 = L.img(s,HERO('bc2_answer_bottom'),{x:M+6.2,y:1.85,w:5.95,h:3.62,valign:'top',align:'left'});
    const o1={clip:{x:420,y:180},dsf:2}, o2={clip:{x:420,y:683},dsf:2};
    // 방송교안 17장과 같은 네 칸 · 색: ① 결론(남색) ② 잘 갖춰진 것(초록) ③ '미가입' 두 줄(빨강) ④ 이제 하면 되는 일(파랑)
    const K=[C.navy,C.green,C.red,C.blue];
    outline(s,g1,478,412,1262,596,Object.assign({color:K[1]},o1));
    outline(s,g2,996,770,1252,848,Object.assign({color:K[2]},o2));
    outline(s,g2,484,986,640,1018,Object.assign({color:K[3]},o2));
    L.pin(s,g1,461,321,1,Object.assign({color:K[0],d:0.3},o1)); L.pin(s,g1,461,430,2,Object.assign({color:K[1],d:0.3},o1)); L.pin(s,g2,975,809,3,Object.assign({color:K[2],d:0.3},o2)); L.pin(s,g2,461,1001,4,Object.assign({color:K[3],d:0.3},o2));
    L.caption(s,{x:W-M-4,y:1.37,w:4,text:'※ 화면 속 금액은 예시',align:'right',size:10});
    // 네 칸
    const lab=[['한 줄 결론','오늘 상담 주제'],['잘 갖춰진 것','보장분석'],['비어 있는 것',"'미가입' 줄이 제안 포인트"],['이제 하면 되는 일','다음 해야 할 액션']];
    const gap=0.28, bw=(W-2*M-3*gap)/4, by=Math.max(g1.y+g1.h,g2.y+g2.h)+0.2, bh=0.66;
    lab.forEach(([t,d],i)=>{ const bx=M+i*(bw+gap);
      L.R(s,{x:bx,y:by,w:bw,h:bh,fill:C.white,line:K[i],radius:0.12});
      L.badge(s,{x:bx+0.16,y:by+(bh-0.34)/2,n:i+1,color:K[i],d:0.34});
      L.T(s,t,{x:bx+0.62,y:by+0.07,w:bw-0.72,h:0.3,fontSize:13.5,bold:true,color:C.navy,valign:'middle'});
      L.T(s,d,{x:bx+0.62,y:by+0.37,w:bw-0.72,h:0.24,fontSize:11,color:C.g600,valign:'middle'});
      if(i<3) L.arrow(s,{x:bx+bw-0.02,y:by+0.09,w:gap+0.04,size:16}); });
    // TIP
    const ty=by+bh+0.14, th=0.44;
    L.R(s,{x:M,y:ty,w:W-2*M,h:th,fill:C.blue50,line:null,radius:0.12});
    s.addText([{text:'TIP  ',options:{bold:true,color:C.blue,fontSize:12,fontFace:L.FONT}},{text:'MeAI 사용자가 가장 많이 사용하는 질문  ',options:{bold:true,color:C.navy,fontSize:12,fontFace:L.FONT}},{text:'“가입증권 별로 핵심만 표로 요약해줘”',options:{bold:true,color:C.blue,fontSize:13,fontFace:L.FONT}}],{x:M+0.25,y:ty,w:W-2*M-0.5,h:th,isTextBox:true,margin:0,valign:'middle'});
  }});
  // 6-4 용어 설명 PC
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 용어 설명 (PC)',title:'[용어] 버튼 하나로 바로 뜻풀이',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    const a = L.img(s,HERO('term_pc_input_z'),{x:M,y:1.5,w:5.9,h:1.55,valign:'top',align:'left'}); capUnder(s,a,'입력창 오른쪽 위 [용어] 버튼');
    const b = L.img(s,HERO('fix_term_on'),{x:M,y:3.45,w:5.9,h:3.2,valign:'top',align:'left'}); capUnder(s,b,'켜면 어려운 말에 표시');
    const c = L.img(s,AG('term','14_pc_glossary6_open'),{x:6.75,y:1.5,w:5.98,h:3.6,valign:'top',align:'center'}); capUnder(s,c,'답변 끝 [용어 설명 6] · 뜻을 한 번에');
    const d = L.img(s,HERO('fix_term_tooltip'),{x:6.75,y:5.5,w:2.6,h:1.15,valign:'top',align:'left'}); capUnder(s,d,'용어를 누르면 뜻 표시');
    L.note(s,{x:d.x+d.w+0.3,y:5.5,w:12.73-(d.x+d.w+0.3),h:1.15,label:'현장에서',text:'고객 눈높이 뜻풀이라\n그대로 읽어 주기',tone:'blue',size:12});
  }});
  // 6-5 용어 설명 모바일
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 용어 설명 (모바일)',title:'모바일은 오른쪽 아래 [용어]',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    [[HERO('term_mo_phone'),'답변 화면 · 오른쪽 아래 [용어]'],[HERO('term_mo_phone_2'),'[용어]를 켜면 용어에 표시'],[AG('term','70_mo_glossary6_open'),'답변 끝 [용어 설명 6] 목록']].forEach(([f,t],i)=>{ const x=M+i*2.95; const g=L.phone(s,f,{x,y:1.5,w:2.75,h:5.1}); if(i===2) mask(s,g,[[140,350,1010,410]],'FFFFFF'); L.caption(s,{x,y:6.64,w:2.75,text:t,size:10}); });
    L.numList(s,{x:9.5,y:1.75,w:3.23,gap:0.24,titleSize:14,descSize:12,items:[
      {n:1,title:'위치만 다름',desc:'PC는 입력창 오른쪽 위,\n모바일은 오른쪽 아래'},
      {n:2,title:'켜고 끄기',desc:'한 번 누르면 표시,\n다시 누르면 원래대로'},
      {n:3,title:'목록으로 보기',desc:'답변 끝 [용어 설명 N]에서 한 번에'},
      {n:4,title:'고객에게 그대로',desc:'뜻풀이를 그대로 읽어 주기'}]});
  }});
  // 6-6 모드 변경 PC
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 모드 변경 (PC)',title:'질문마다 간편·상세 선택',sub:'고객 앞에서는 간편, 약관을 따질 때는 상세',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    const g = L.img(s,HERO('mode_pc_dropdown_z'),{x:M,y:1.85,w:7.5,h:4.5,valign:'top',align:'left'}); mask(s,g,[[140,312,1116,362],[140,441,1298,468],[979,441,1298,494]]); capUnder(s,g,'[간편 분석]을 누르면 두 가지가 펼쳐짐 · ※ 답 아래 질문 버튼 일부는 가림');
    const rx = 8.35, rw = 12.73-rx;
    L.card(s,{x:rx,y:1.85,w:rw,h:1.6,kicker:'고객 상담 · 직관적 검토용',title:'간편 분석',desc:'기본 모드. 고객과 함께 보는 화면, 첫 상담용',titleSize:16,descSize:12});
    L.card(s,{x:rx,y:3.6,w:rw,h:1.6,kicker:'약관 · 담보 정밀 검토용',title:'상세 분석',desc:'약관 근거를 확인하거나 자사·타사 담보를 숫자로 비교할 때',titleSize:16,descSize:12,accent:C.navy});
    L.note(s,{x:rx,y:5.35,w:rw,h:0.85,label:'바꾸면',text:'대화에 아래 안내줄이 붙고,\n다음 질문부터 그 모드로 답변',tone:'grey',size:11.5});
    L.img(s,HERO('fix_mode_notice'),{x:rx,y:6.3,w:rw,h:0.55,valign:'top',align:'left'});
  }});
  // 6-7 모드 변경 모바일
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · NEW 모드 변경 (모바일)',title:'모바일도 입력창 아래 [간편 분석]',pageNo:no,tag:{text:'개발 진행 중 · 오픈 시 세부 변경 가능'}});
    [[HERO('mode_mo_phone'),'입력창 아래 [간편 분석] · [상품 선택]'],[HERO('mode_mo_phone_2'),'"분석 모드" 선택창 · 간편 / 상세'],[AG('mode','47_mo_mode_detailed'),'고른 뒤 · 버튼과 안내줄이 바뀜']].forEach(([f,t],i)=>{ const x=M+i*2.95; const g=L.phone(s,f,{x,y:1.5,w:2.75,h:5.1}); if(i===0) mask(s,g,[[204,1352,1022,1460],[204,1538,1022,1649]]); if(i===1) mask(s,g,[[204,1352,1022,1386]],'8B8C8D'); if(i===2) mask(s,g,[[201,1196,1019,1304],[201,1382,1019,1493]]); L.caption(s,{x,y:6.64,w:2.75,text:t,size:10}); });
    L.numList(s,{x:9.5,y:1.9,w:3.23,gap:0.3,titleSize:14,descSize:12,items:[
      {n:1,title:'버튼을 누르면',desc:'아래에서 "분석 모드" 선택창이 올라옴'},
      {n:2,title:'고르면 끝',desc:'선택창이 닫히고 버튼 이름이 바뀜'},
      {n:3,title:'질문마다 바꾸기 가능',desc:'고객 앞에서는 간편, 약관을 따질 땐 상세'}]});
    L.caption(s,{x:9.5,y:6.64,w:3.23,text:'※ 답 아래 질문 버튼 일부는 가림',align:'left',size:10});
  }});
  // 6-8 꼬리질문
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 답변 아래',title:'꼬리질문 버튼으로 이어가기',sub:'이어서 물을 질문은 꼬리질문이 제시 · 타이핑 없이 버튼만 누르기',pageNo:no});
    const g = L.img(s,HERO('mode_pc_bottom2_z'),{x:M,y:1.85,w:7.4,h:5.0,valign:'top',align:'left'});
    mask(s,g,[[140,552,1116,602],[140,681,1298,731]]);
    L.caption(s,{x:W-M-4.5,y:1.37,w:4.5,text:'※ 꼬리질문 둘째·셋째 줄 글자는 가림',align:'right',size:10});
    const clip={x:480,y:340}, o={clip,dsf:3};
    L.pin(s,g,470,367,1,o); L.pin(s,g,470,494,2,o); L.pin(s,g,470,638,3,o); L.pin(s,g,470,750,4,o); L.pin(s,g,470,800,5,o);
    const rx = 8.2, rw = 12.73-rx;
    L.numList(s,{x:rx,y:1.85,w:rw,gap:0.02,titleSize:13.5,descSize:11.5,items:[
      {n:1,title:'답변 아래 아이콘',desc:'복사 · 출처 · 좋아요/싫어요 평가'},
      {n:2,title:'꼬리질문 3개',desc:'화면 글자는 ‘질문 예시’ · 누르면 바로 전송'},
      {n:3,title:'질문 더보기',desc:'미리 만든 질문 모음에서 골라 쓰기'},
      {n:4,title:'입력창',desc:'직접 쓰거나, 모바일은 마이크로 말하기'},
      {n:5,title:'모드 · 상품 선택',desc:'간편/상세를 고르고 분석할 상품 좁히기'}]});
    // 방송교안 16장과 같은 숫자·문구·출처
    const by = 5.05, bh = 1.9;
    L.R(s,{x:rx,y:by,w:rw,h:bh,fill:C.navy,line:null,radius:0.14});
    L.T(s,'많이 질문할수록 늘어나는 영업기회',{x:rx+0.3,y:by+0.14,w:rw-0.6,h:0.28,fontSize:12,bold:true,color:C.blue100,valign:'middle'});
    L.T(s,'2.3배',{x:8.5,y:5.5,w:1.7,h:0.62,fontSize:34,bold:true,color:'FFFFFF',valign:'middle'});
    L.T(s,'질문 1건 대비\n3건 이상 평균 가계약 수',{x:8.5,y:6.12,w:1.85,h:0.45,fontSize:10.5,color:C.g300,valign:'top'});
    // 질문 개수별 평균 가계약 수 · 길이가 값에 비례하는 막대(9·68쪽과 같은 꼴) · 셋째 막대만 강조
    // 비강조 막대는 남색 바탕 위라 밝은 회색 대신 한 단계 어두운 g700
    L.bars(s,{x:10.35,y:5.45,w:2.1,h:0.95,dir:'col',plot:{x:0,y:0.2,w:1,h:0.8},
      labels:['1개','2개','3개 이상'],values:[11.99,17.02,27.79],colors:['4E5968','4E5968',C.purple],
      max:30,gap:45,fmt:v=>v.toFixed(2)+'건',valueSize:10,valueColor:'FFFFFF',catSize:9.5,catColor:C.g400,baseline:'4E5968'});
    L.T(s,'출처: 2026년 8월 TA채널 MeAI 사용 데이터 분석',{x:rx+0.3,y:6.7,w:rw-0.6,h:0.2,fontSize:9,color:C.g500,valign:'middle'});
  }});
  // 6-9 요약 리포트
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 요약 리포트',title:'요약 리포트는 네 단계로 발송',sub:'휴대폰 하나로 발송까지 완료 · PC는 오른쪽 위 [요약 리포트]',pageNo:no});
    const st=[['요약 생성','대화 화면 상단 [요약 생성]'],['선택 → 편집하기','넣을 답변만 체크, 내부용은 빼기'],['리포트 생성하기','카카오톡으로 링크 전송'],['알림톡 도착','[요약레포트 확인하기] · 받은 날부터 7일']];
    st.forEach((t,i)=>{ const x=M+i*3.08,w=2.9; const f = i===0 ? HERO('bc2_report_step1') : i<3 ? LEG('report_step'+(i+1)) : HERO('report_kakao_crop'); const gp = L.phone(s,f,{x,y:1.85,w,h:3.9,valign:i<3?'top':'middle'}); if(i===0){ mask(s,gp,[[24,328,382,378]],'FFFFFF'); outline(s,gp,240,114,307,144,{dsf:1,color:C.red,width:1.5,radius:0.03}); } L.badge(s,{x,y:5.86,n:i+1,d:0.3}); L.T(s,t[0],{x:x+0.4,y:5.84,w:w-0.4,h:0.34,fontSize:13.5,bold:true,color:C.navy,valign:'middle'}); L.T(s,t[1],{x,y:6.19,w,h:0.3,fontSize:11.5,color:C.g600}); if(i<3) L.arrow(s,{x:x+w-0.08,y:3.55,w:0.35}); });
    L.note(s,{x:M,y:6.54,w:7.4,h:0.4,label:'보내기 전',text:'숫자·약관 근거·개인정보 확인. "AI로 생성된 보조자료" 표시가 붙음',tone:'yellow',size:11});
    L.caption(s,{x:8.2,y:6.6,w:12.73-8.2,text:'2026.06 실제 화면 · 이름과 일부 글자는 가림',align:'right',size:10});
  }});
  // 6-10 모바일 진입
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 6 · 모바일',title:'앱 홈 → 보장분석 → MeAI',sub:'모바일 MeAI 홈·고객찾기·게시판은 PC 오픈 뒤 순차 적용 예정',pageNo:no});
    L.phone(s,LEG('mobile_app_home'),{x:M,y:1.85,w:2.4,h:4.75}); L.caption(s,{x:M,y:6.64,w:2.4,text:'① 앱 홈 · [보장분석]',size:10});
    // 인사 줄 끝의 제한 횟수 괄호는 책에서 쓰지 않는 숫자라 머리 띠 색으로 덮는다
    const gm = L.phone(s,HERO('fix_mobile_customer_list'),{x:M+2.55,y:1.85,w:2.4,h:4.75}); mask(s,gm,[[344,185,568,217]],'37383C'); L.caption(s,{x:M+2.55,y:6.64,w:2.4,text:'② 상단 버튼 · ③ 카드 [MeAI]',size:10});
    L.phone(s,AG('mode','55_mo_menu_drawer'),{x:M+5.1,y:1.85,w:2.3,h:4.75}); L.caption(s,{x:M+5.1,y:6.64,w:2.3,text:'④ 대화 화면 ≡ 메뉴',size:10});
    const rx = 8.2, rw = 12.73-rx;
    L.numList(s,{x:rx,y:1.85,w:rw,gap:0.14,titleSize:13.5,descSize:11.5,items:[
      {n:1,title:'[보장분석] 누르기',desc:'앱 홈 아이콘 묶음의 첫 번째'},
      {n:2,title:'[MeAI 일반대화]',desc:'고객 목록 위, 무엇이든 묻는 창'},
      {n:3,title:'카드의 [MeAI]',desc:'누르면 그 고객 맞춤대화가 열림'},
      {n:4,title:'≡ 메뉴',desc:'약관 검색 · 사용 가이드 · 월별 대화 목록'}]});
    L.note(s,{x:rx,y:4.8,w:rw,h:0.78,label:'공통',text:'대화 이력·저장한 나의 질문은 PC와 모바일이 같음',tone:'blue',size:11.5});
    L.note(s,{x:rx,y:5.72,w:rw,h:0.84,label:'TIP',text:'고객 목록 위 "오늘 보장분석 활용"에서\n오늘 쓴 횟수 확인',tone:'grey',size:11.5});
    L.caption(s,{x:rx,y:6.64,w:rw,text:'※ 화면 속 이름은 예시 · 일부 글자는 가림',align:'right',size:10});
  }});
};
