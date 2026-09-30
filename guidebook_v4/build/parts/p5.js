module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  S.push({ part:'05', fn:(pres,no)=> L.divider(pres,{num:'05',title:'게시판 · 사전조회 동의',sub:'공지는 게시판에서, 동의는 알림톡 한 통으로 받아요.',learn:['게시판 목록과 글 상세','사전조회 동의가 먼저인 이유','알림톡 요청부터 반영까지'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 게시판',title:'공지·이슈·기능안내를 한 곳에서',pageNo:no});
    const g = L.img(s,HERO('board_list_crop'),{x:M,y:1.45,w:6.5,h:5.15,valign:'top',align:'left'});
    L.caption(s,{x:M,y:g.y+g.h+0.04,w:g.w,text:'※ 글 제목·날짜·내용은 예시예요. MeAI 홈으로 가는 실제 문 6개(10/2부터)는 PART 2에서 봐요.',align:'left',size:10});
    const clip={x:270,y:85}, o={clip,dsf:2,d:0.3};
    L.pin(s,g,588,122,1,o); L.pin(s,g,1058,122,2,o); L.pin(s,g,300,224,3,o); L.pin(s,g,735,192,4,o); L.pin(s,g,942,192,5,o); L.pin(s,g,610,823,6,o);
    [{n:1,title:'분류 필터',desc:'전체 · 공지사항 · 이슈 · 기능안내'},{n:2,title:'정렬',desc:'최신순이 기본, 조회순으로도 봐요.'},{n:3,title:'분류 표시',desc:'공지사항 파랑 · 이슈 주황 · 기능안내 초록'},{n:4,title:'핀 · NEW · 첨부',desc:'핀 = 고정 글 · NEW = 7일 이내 · 클립 = 첨부 수'},{n:5,title:'날짜 · 조회',desc:'게시일과 조회수예요.'},{n:6,title:'페이지',desc:'한 쪽 6건, ‹ 1 2 ›로 넘겨요.'}].forEach((it,i)=> L.numList(s,{x:7.2,y:1.5+i*0.7,w:5.53,titleSize:14,descSize:12,items:[it]}));
    // 화면 위쪽 : 게시판 윗줄 캡처(v2_board_topbar_z 에서 왼쪽·오른쪽 끝만 잘라 씀) + 한 줄
    const tx=7.2, ty=5.72, tw=W-M-7.2, th=1.18;
    L.R(s,{x:tx,y:ty,w:tw,h:th,fill:C.g100,line:null,radius:0.12});
    const tl = L.img(s,HERO('fix_c_board_top_left'),{x:tx+0.2,y:ty+0.16,w:3.2,h:0.36,radius:14,shadow:false,align:'left',valign:'top'});
    L.img(s,HERO('fix_c_board_top_right'),{x:tx+tw-0.2-1.2,y:ty+0.16,w:1.2,h:0.36,radius:14,shadow:false,align:'right',valign:'top'});
    L.T(s,'· · ·',{x:tl.x+tl.w,y:ty+0.16,w:(tx+tw-0.2-0.98)-(tl.x+tl.w),h:0.36,fontSize:11,color:C.g400,align:'center',valign:'middle'});
    s.addText([{text:'화면 위쪽  ',options:{bold:true,color:C.g700,fontSize:11,fontFace:L.FONT}},{text:'[MeAI 홈]을 누르면 MeAI 홈으로, [글씨 확대]는 기본 ON이에요.',options:{color:C.g800,fontSize:11,fontFace:L.FONT}}],{x:tx+0.2,y:ty+0.64,w:tw-0.4,h:0.4,isTextBox:true,margin:0,valign:'middle'});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 글 상세',title:'글을 누르면 본문과 첨부파일이 열려요',pageNo:no});
    const g = L.img(s,HERO('gb5_board_detail_1370'),{x:M,y:1.5,w:6.8,h:5.1,valign:'top',align:'left'}); L.caption(s,{x:M,y:6.66,w:g.w,text:'※ 오픈 안내 공지를 예로 든 화면이고, 글 내용은 예시예요. MeAI 홈으로 가는 실제 문 6개(10/2부터)는 PART 2에서 봐요.',align:'left',size:9.5});
    const clip={x:270,y:95}, o={clip,dsf:2,d:0.3};
    L.pin(s,g,362,119,1,o); L.pin(s,g,692,240,2,o); L.pin(s,g,297,355,3,o); L.pin(s,g,742,593,4,o); L.pin(s,g,720,724,5,o); // 본문 한 줄을 뺀 캡처라 첨부파일·이전/다음 글이 45px 위로
    [{n:1,title:'‹ 목록',desc:'분류·정렬 상태 그대로 목록으로 돌아가요.'},{n:2,title:'제목 줄',desc:'분류 · NEW · 날짜 · 조회. 핀은 고정 글이에요.'},{n:3,title:'본문',desc:'맞춤대화 시작 조건 같은 운영 기준이 적혀요.'},{n:4,title:'첨부파일',desc:'카드를 누르면 바로 내려받아요.'},{n:5,title:'이전 글 · 다음 글',desc:'목록으로 나가지 않고 이어서 읽어요.'}].forEach((it,i)=> L.numList(s,{x:7.65,y:1.6+i*0.85,w:5.08,titleSize:14,descSize:12,items:[it]}));
    L.note(s,{x:7.65,y:5.85,w:5.08,h:1.05,label:'빨간 점',text:'새 글이 오면 MeAI 홈 [게시판] 버튼에 빨간 점이 붙어요. 보이면 먼저 읽어요.',tone:'red',size:12});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 사전조회 동의',title:'동의는 알림톡 한 통으로 받아요',sub:'맞춤대화는 보장 내역을 읽어요. 그래서 사전조회 동의가 먼저예요.',pageNo:no});
    const st=[['요청','알림톡 요청','휴대폰 번호를 넣고\n[보내기]를 눌러요.'],['동의','고객이 동의','고객이 안내 문자에서 동의를 완료해요.'],['반영','약 15분 · D-n','금방 반영돼요.\n동의일부터 1년간\nD-n으로 보여요.'],['만료 전','재요청','[사전동의 만료] 그룹으로 미리 챙겨요.'],['철회','정보 확인 불가','회색으로 표시되고 정보 확인이 막혀요.']];
    const gap=0.22, sw=(W-2*M-gap*4)/5, sy=1.85, sh=1.8;
    st.forEach((t,i)=>{ const x=M+i*(sw+gap), on=i===0; L.R(s,{x,y:sy,w:sw,h:sh,fill:on?C.blue:C.white,line:on?null:C.g200,radius:0.14,shadow:!on}); L.T(s,t[0],{x:x+0.2,y:sy+0.18,w:sw-0.4,h:0.26,fontSize:10.5,bold:true,color:on?'FFFFFF':C.blue}); L.T(s,t[1],{x:x+0.2,y:sy+0.46,w:sw-0.4,h:0.36,fontSize:15,bold:true,color:on?'FFFFFF':C.navy,valign:'middle'}); L.T(s,t[2],{x:x+0.2,y:sy+0.9,w:sw-0.35,h:sh-1.0,fontSize:11.5,color:on?'FFFFFF':C.g600,lineSpacingMultiple:1.25}); if(i<st.length-1) L.T(s,'›',{x:x+sw-0.06,y:sy+sh/2-0.25,w:gap+0.12,h:0.5,fontSize:22,bold:true,color:C.g700,align:'center',valign:'middle'}); });
    // 아래 줄 : 팝업만 잘라낸 그림 | 요청 버튼 크게 + [보내기] 뒤 알림 | 상품소개 동의 안내
    const a = L.img(s,HERO('fix_c_consent_modal'),{x:M,y:3.95,w:4.3,h:2.55,valign:'top',align:'left'}); L.caption(s,{x:M,y:a.y+a.h+0.05,w:a.w,text:'MeAI 홈 [고객 동의] 팝업',size:10});
    const bx=M+4.55, bw=3.75;
    const b = L.img(s,HERO('fix_c_consent_request_btn'),{x:bx,y:3.95,w:bw,h:1.3,valign:'top',align:'left'}); L.caption(s,{x:b.x,y:b.y+b.h+0.05,w:b.w,text:'고객찾기에서 요청',size:10});
    const c = L.img(s,HERO('consent_toast_crop'),{x:bx,y:b.y+b.h+0.5,w:bw,h:0.7,valign:'top',align:'left'}); L.caption(s,{x:c.x,y:c.y+c.h+0.05,w:c.w,text:'[보내기] 뒤 뜨는 알림',size:10});
    const nx=bx+bw+0.25;
    L.note(s,{x:nx,y:3.95,w:W-M-nx,h:a.h,label:'상품소개 동의',text:'\n상품 소개에 동의한 고객에게는\n"AI 추천 고객" 리본이 붙어요.\nMeAI 홈 "상품제안 가능"\n숫자에도 들어가요.',tone:'grey',size:12});
  }});
};
