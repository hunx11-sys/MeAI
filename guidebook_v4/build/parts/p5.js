module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  S.push({ part:'05', fn:(pres,no)=> L.divider(pres,{num:'05',title:'게시판 · 사전조회 동의',sub:'공지는 게시판에서, 동의는 알림톡 한 통으로.',learn:['게시판 목록과 글 상세','사전조회 동의가 먼저인 이유','알림톡 요청부터 반영까지'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 게시판',title:'공지·이슈·기능안내를 한 곳에서',pageNo:no});
    const g = L.img(s,HERO('board_list_crop'),{x:M,y:1.45,w:6.5,h:5.15,valign:'top',align:'left'});
    L.caption(s,{x:M,y:g.y+g.h+0.04,w:g.w,text:'※ 글 제목·날짜·내용은 예시.',align:'left',size:10});
    const clip={x:270,y:85}, o={clip,dsf:2,d:0.3};
    L.pin(s,g,588,122,1,o); L.pin(s,g,1058,122,2,o); L.pin(s,g,300,224,3,o); L.pin(s,g,671,188,4,o); L.pin(s,g,942,188,5,o); L.pin(s,g,610,823,6,o); // 첫 줄 제목이 'MeAI 홈 오픈 안내'로 짧아져 NEW·클립이 64px 왼쪽으로(cap_gb5_home_board.json). ④ 바로 아래로 설명 줄이 지나가 ④⑤ 를 4px 올림. 날짜 자리는 그대로
    [{n:1,title:'분류 필터',desc:'전체 · 공지사항 · 이슈 · 기능안내'},{n:2,title:'정렬',desc:'최신순이 기본, 조회순도 가능.'},{n:3,title:'분류 표시',desc:'공지사항 파랑 · 이슈 주황 · 기능안내 초록'},{n:4,title:'핀 · NEW · 첨부',desc:'핀 = 고정 글 · NEW = 7일 이내 · 클립 = 첨부 수'},{n:5,title:'날짜 · 조회',desc:'게시일과 조회수.'},{n:6,title:'페이지',desc:'한 쪽 6건, ‹ 1 2 ›로 넘기기.'}].forEach((it,i)=> L.numList(s,{x:7.2,y:1.5+i*0.7,w:5.53,titleSize:14,descSize:12,items:[it]}));
    // 화면 위쪽 : 게시판 윗줄 캡처(v2_board_topbar_z 에서 왼쪽·오른쪽 끝만 잘라 씀) + 한 줄
    const tx=7.2, ty=5.72, tw=W-M-7.2, th=1.18;
    L.R(s,{x:tx,y:ty,w:tw,h:th,fill:C.g100,line:null,radius:0.12});
    const tl = L.img(s,HERO('fix_c_board_top_left'),{x:tx+0.2,y:ty+0.16,w:3.2,h:0.36,radius:14,shadow:false,align:'left',valign:'top'});
    L.img(s,HERO('fix_c_board_top_right'),{x:tx+tw-0.2-1.2,y:ty+0.16,w:1.2,h:0.36,radius:14,shadow:false,align:'right',valign:'top'});
    L.T(s,'· · ·',{x:tl.x+tl.w,y:ty+0.16,w:(tx+tw-0.2-0.98)-(tl.x+tl.w),h:0.36,fontSize:11,color:C.g400,align:'center',valign:'middle'});
    s.addText([{text:'화면 위쪽  ',options:{bold:true,color:C.g700,fontSize:11,fontFace:L.FONT}},{text:'[MeAI 홈]을 누르면 MeAI 홈으로 이동, [글씨 확대]는 기본 ON.',options:{color:C.g800,fontSize:11,fontFace:L.FONT}}],{x:tx+0.2,y:ty+0.64,w:tw-0.4,h:0.4,isTextBox:true,margin:0,valign:'middle'});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 글 상세',title:'글을 누르면 열리는 본문과 첨부파일',pageNo:no});
    const g = L.img(s,HERO('gb5_board_detail_1370'),{x:M,y:1.5,w:6.8,h:5.1,valign:'top',align:'left'}); L.caption(s,{x:M,y:6.66,w:g.w,text:'※ 오픈 안내 공지를 예로 든 화면 · 글 내용은 예시.',align:'left',size:9.5});
    const clip={x:270,y:95}, o={clip,dsf:2,d:0.3};
    L.pin(s,g,362,119,1,o); L.pin(s,g,602,240,2,o); L.pin(s,g,297,355,3,o); L.pin(s,g,742,564,4,o); L.pin(s,g,720,695,5,o); // 다시 찍은 캡처(cap_gb5_home_board.json): 제목이 짧아져 NEW 오른쪽 끝 578 · 본문 첫 문단이 한 줄이 되어 첨부 카드 가운데 564 · 이전/다음 글 카드 가운데 695
    [{n:1,title:'‹ 목록',desc:'분류·정렬 상태 그대로 목록으로 이동.'},{n:2,title:'제목 줄',desc:'분류 · NEW · 날짜 · 조회. 핀은 고정 글.'},{n:3,title:'본문',desc:'맞춤대화 시작 조건 같은 운영 기준 안내.'},{n:4,title:'첨부파일',desc:'카드를 누르면 바로 내려받기.'},{n:5,title:'이전 글 · 다음 글',desc:'목록으로 나가지 않고 이어서 읽기.'}].forEach((it,i)=> L.numList(s,{x:7.65,y:1.6+i*0.85,w:5.08,titleSize:14,descSize:12,items:[it]}));
    L.note(s,{x:7.65,y:5.85,w:5.08,h:1.05,label:'빨간 점',text:'새 글이 오면 MeAI 홈 [게시판] 버튼에 빨간 점 표시.\n보이면 먼저 읽기.',tone:'red',size:12});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 사전조회 동의',title:'동의는 알림톡 한 통으로',sub:'맞춤대화는 보장 내역을 읽고 답변. 그래서 사전조회 동의가 먼저.',pageNo:no});
    // 위 : 기간을 길이로 — 맞춤대화 90일 막대와 MeAI 홈 노출 1년 막대를 같은 눈금(1년 = 10인치)에 그림. 막대 길이는 기간에 정확히 비례
    const X0=2.55, LEN=10.0, X1=X0+LEN, k=LEN/365, X90=X0+90*k;
    // 시작 카드 : 요청 → 동의
    L.R(s,{x:0.6,y:1.95,w:1.62,h:1.3,fill:C.blue,line:null,radius:0.14});
    L.T(s,'요청',{x:0.8,y:2.07,w:1.3,h:0.26,fontSize:10.5,bold:true,color:'FFFFFF',transparency:20});
    L.T(s,'알림톡 한 통',{x:0.8,y:2.36,w:1.4,h:0.36,fontSize:14.5,bold:true,color:'FFFFFF',valign:'middle'});
    L.T(s,'[보내기] →\n고객 동의',{x:0.8,y:2.76,w:1.35,h:0.42,fontSize:10.5,color:'FFFFFF',lineSpacingMultiple:1.1});
    L.T(s,'›',{x:2.2,y:2.3,w:0.3,h:0.5,fontSize:22,bold:true,color:C.g700,align:'center',valign:'middle'});
    L.T(s,'맞춤대화 가능 · 동의일부터 90일 · 칩의 D-n = 남은 날',{x:X0,y:1.88,w:6.4,h:0.3,fontSize:12,bold:true,color:C.navy,valign:'middle'});
    // 철회 칩 : 시점이 아니라 상태라 눈금 밖(오른쪽 위)에 둠
    // 칩 폭 : 글자 몫을 추정치의 0.93 으로 잡음. 실측 글자 폭 LibreOffice 2.08인치 · PowerPoint 약 2.25인치(×1.08) → 오른쪽 여백 PDF 약 0.30 · PowerPoint 약 0.13인치(점 쪽 0.14와 비슷). 글 상자는 추정치 그대로 둬 줄바꿈을 막음(왼쪽 정렬이라 글자는 칩 안에 머묾)
    const wdT='철회 → 즉시 회색 · 정보를 볼 수 없음', wdTw=L.textW(wdT,10.5), wdW=0.14+0.12+0.1+wdTw*0.93+0.16, wdX=12.73-wdW, wdY=1.87;
    L.R(s,{x:wdX,y:wdY,w:wdW,h:0.32,fill:C.red50,line:null,radius:0.16});
    L.circle(s,{x:wdX+0.14,y:wdY+0.1,d:0.12,fill:C.red});
    L.T(s,wdT,{x:wdX+0.36,y:wdY,w:wdTw,h:0.32,fontSize:10.5,color:C.g800,valign:'middle'});
    // 눈금선 : 동의일 · 90일 · 1년 — 막대·빨간 점보다 먼저 그려 그 아래에 깔림(선이 점을 가르지 않게)
    // 1년 눈금은 줄 B 에만 걸치게 2.68부터(2.22부터 올리면 바로 위 철회 칩 밑단에 0.03인치로 붙어 칩이 '1년 시점'처럼 보임)
    [[X0,2.22],[X90,2.22],[X1,2.68]].forEach(([X,y])=> s.addShape('line',{x:X,y,w:0,h:3.0-y,line:{color:C.g400,width:0.75}}));
    // 줄 A : 맞춤대화 90일
    L.R(s,{x:X0,y:2.28,w:90*k,h:0.34,fill:C.blue,line:null,radius:0.06});
    s.addShape('ellipse',{x:X90-0.07,y:2.28+0.17-0.07,w:0.14,h:0.14,fill:{color:C.red},line:{color:'FFFFFF',width:1.5}});
    L.T(s,'만료 전 → [사전동의 만료] 그룹에서 미리 재요청',{x:X90+0.2,y:2.28,w:7.2,h:0.34,fontSize:11.5,color:C.g700,valign:'middle'});
    // 줄 B : MeAI 홈 노출 1년
    L.R(s,{x:X0,y:2.74,w:LEN,h:0.2,fill:C.blue100,line:null,radius:0.05});
    L.T(s,'MeAI 홈 노출 · 사전조회 동의일로부터 1년 이내',{x:X1-5.6,y:2.98,w:5.6,h:0.28,fontSize:11,color:C.g700,align:'right',valign:'middle'});
    // 눈금 글자 : 동의일 · 90일 · 1년
    L.T(s,'동의일 · 15분 안팎 반영',{x:X0,y:3.3,w:2.3,h:0.28,fontSize:10.5,color:C.g600,valign:'middle'});
    L.T(s,'90일 · 만료 → "사전조회동의 필요"',{x:X90,y:3.3,w:3.0,h:0.28,fontSize:10.5,bold:true,color:C.navy,valign:'middle'});
    L.T(s,'1년',{x:X1-1.0,y:3.3,w:1.0,h:0.28,fontSize:10.5,color:C.g600,align:'right',valign:'middle'});
    L.T(s,'막대 길이는 기간에 비례 (90일 : 1년)',{x:7.73,y:3.6,w:5.0,h:0.26,fontSize:9.5,color:C.g500,align:'right',valign:'middle'});
    // 아래 줄 : 팝업만 잘라낸 그림 | 요청 버튼 크게 + [보내기] 뒤 알림 | 상품소개 동의 안내
    const a = L.img(s,HERO('fix_c_consent_modal'),{x:M,y:3.95,w:4.3,h:2.55,valign:'top',align:'left'}); L.caption(s,{x:M,y:a.y+a.h+0.05,w:a.w,text:'MeAI 홈 [고객 동의]에서도 사전조회동의 발송 가능',size:10});
    const bx=M+4.55, bw=3.75;
    const b = L.img(s,HERO('fix_c_consent_request_btn'),{x:bx,y:3.95,w:bw,h:1.3,valign:'top',align:'left'}); L.caption(s,{x:b.x,y:b.y+b.h+0.05,w:b.w,text:'고객찾기에서 요청',size:10});
    const c = L.img(s,HERO('consent_toast_crop'),{x:bx,y:b.y+b.h+0.5,w:bw,h:0.7,valign:'top',align:'left'}); L.caption(s,{x:c.x,y:c.y+c.h+0.05,w:c.w,text:'[보내기] 뒤 뜨는 알림',size:10});
    const nx=bx+bw+0.25;
    L.note(s,{x:nx,y:3.95,w:W-M-nx,h:a.h,label:'상품소개 동의',text:'\n상품 소개에 동의한 고객은\n"AI 추천 고객" 리본 표시.\nMeAI 홈 "상품제안 가능"\n숫자에도 포함.',tone:'grey',size:12});
  }});
};
