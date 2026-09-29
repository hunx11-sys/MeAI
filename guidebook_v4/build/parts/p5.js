module.exports = (S, ctx) => {
  const { L, C, W, H, M, HERO, AG } = ctx;
  S.push({ part:'05', fn:(pres,no)=> L.divider(pres,{num:'05',title:'게시판 · 사전조회 동의',sub:'공지는 게시판에서, 동의는 알림톡 요청으로. 대문 오른쪽 위 버튼 두 개만 알면 돼요.',learn:['게시판 목록과 글 상세 · 새 글 빨간 점','사전조회 동의가 왜 먼저인지 · 요청부터 반영까지','[고객 동의] 버튼과 [사전조회동의 요청하기]'],pageNo:no}) });
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 게시판',title:'공지 · 이슈 · 기능안내, 게시판 한 곳에서 봐요',pageNo:no});
    const g = L.img(s,HERO('board_list_crop'),{x:M,y:1.45,w:8.75,h:5.5,valign:'top',align:'left'});
    const clip={x:270,y:85}, o={clip,dsf:2,d:0.3};
    L.pin(s,g,588,122,1,o); L.pin(s,g,1058,122,2,o); L.pin(s,g,300,224,3,o); L.pin(s,g,735,192,4,o); L.pin(s,g,942,192,5,o); L.pin(s,g,620,823,6,o);
    L.numList(s,{x:9.6,y:1.45,w:3.15,gap:0.07,titleSize:11,descSize:9.5,items:[{n:1,title:'분류 필터',desc:'전체 · 공지사항 · 이슈 · 기능안내.'},{n:2,title:'정렬',desc:'최신순이 기본, 조회순으로 바꿀 수 있어요.'},{n:3,title:'분류 표시',desc:'공지사항(파랑) · 이슈(노랑) · 기능안내(초록).'},{n:4,title:'제목 · 핀 · NEW · 첨부',desc:'핀은 고정 글(항상 맨 위), NEW는 7일 이내 새 글, 클립은 첨부 수.'},{n:5,title:'날짜 · 조회',desc:'게시일과 조회수.'},{n:6,title:'페이지',desc:'한 쪽 6건. ‹ 1 2 › 로 넘겨요.'}]});
    L.note(s,{x:9.6,y:5.6,w:3.15,h:1.2,label:'[MeAI 홈]',text:'화면 왼쪽 위 빨간 [MeAI 홈] 버튼으로 대문에 돌아가요. 오른쪽에는 "게시판 · MeAI 공지와 활용 안내를 확인하세요" 제목이 있어요.',tone:'grey',size:9.5});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 글 상세',title:'글을 누르면 본문과 첨부파일이 열려요',sub:'대문 오픈 안내, 동의 절차 변경, 고객찾기 사용 방법처럼 꼭 읽어야 할 공지가 올라와요.',pageNo:no});
    const g = L.img(s,HERO('board_detail_crop'),{x:M,y:1.85,w:6.2,h:5.0,valign:'top',align:'left'});
    const clip={x:380,y:135}, o={clip,dsf:2,d:0.3};
    L.pin(s,g,490,165,1,o); L.pin(s,g,955,332,2,o); L.pin(s,g,418,595,3,o); L.pin(s,g,1022,885,4,o); L.pin(s,g,765,1065,5,o);
    L.numList(s,{x:7.0,y:1.85,w:5.7,gap:0.08,titleSize:12,descSize:10,items:[{n:1,title:'‹ 목록',desc:'글 목록으로 돌아가요. 분류·정렬 상태는 그대로 유지돼요.'},{n:2,title:'분류 · 제목 · NEW · 날짜 · 조회',desc:'제목 앞 핀은 고정 글이에요.'},{n:3,title:'본문',desc:'"맞춤대화는 고객을 먼저 선택해야 시작되며, 사전조회동의가 없는 고객은 동의를 받은 뒤 진행할 수 있습니다." 같은 운영 기준이 여기 적혀요.'},{n:4,title:'첨부파일',desc:'카드를 누르면 바로 내려받아요(PDF·엑셀·PPT·워드·한글). 파일명·용량이 함께 보여요.'},{n:5,title:'이전 글 · 다음 글',desc:'목록으로 나가지 않고 이어서 읽어요.'}]});
    L.note(s,{x:7.0,y:5.35,w:5.7,h:1.35,label:'빨간 점',text:'새 글이 올라오면 대문 오른쪽 위 [게시판] 버튼에 빨간 점이 붙어요. 아침에 대문을 열 때 점이 보이면 먼저 읽어 두세요. 이슈(응답 지연·결과 누락 조치)는 여기서 확인해요.',tone:'red',size:10.5});
  }});
  S.push({ fn:(pres,no)=>{
    const s = L.base(pres,{kicker:'PART 5 · 사전조회 동의',title:'동의가 있어야 맞춤대화가 열려요. 요청은 알림톡 한 통이면 돼요',sub:'맞춤대화는 고객의 보장 내역을 읽어서 답해요. 그 내역을 보려면 사전조회 동의가 필요해요.',pageNo:no});
    L.steps(s,{x:M,y:1.85,w:W-2*M,h:1.95,items:[{n:1,step:'요청',title:'알림톡 요청',desc:'대문 [고객 동의] 또는 고객찾기 [사전조회동의 요청하기]에 휴대폰 번호 입력 → [보내기].'},{n:2,step:'동의',title:'고객이 동의',desc:'고객이 안내 문자에서 동의를 완료하면 상태가 바뀌어요.'},{n:3,step:'반영',title:'약 15분 · D-n',desc:'준실시간(약 15분 내외) 반영. 동의일로부터 1년 동안 D-n으로 보여요.'},{n:4,step:'만료 전',title:'재요청',desc:'[사전동의 만료] 그룹과 대문 "사전조회 동의 필요" 숫자로 챙겨요.'},{n:5,step:'철회',title:'정보 확인 불가',desc:'고객이 철회하면 회색으로 표시되고 정보 확인이 막혀요.'}],activeIdx:0});
    L.img(s,AG('gate010','12_consent_modal'),{x:M,y:4.05,w:3.9,h:2.15,valign:'top',align:'left'}); L.caption(s,{x:M,y:6.22,w:3.9,text:'대문 [고객 동의] → 팝업 · 번호를 넣으면 [보내기]가 켜져요',size:9});
    L.img(s,AG('find010','32_right_panel_kimminsu'),{x:M+4.1,y:4.05,w:3.9,h:2.45,valign:'top',align:'left'}); L.caption(s,{x:M+4.1,y:6.52,w:3.9,text:'고객찾기 · 동의 필요 고객의 [사전조회동의 요청하기]',size:9});
    L.img(s,HERO('consent_toast_crop'),{x:M+8.2,y:4.05,w:3.93,h:0.7,valign:'top',align:'left'}); L.caption(s,{x:M+8.2,y:4.78,w:3.93,text:'보내기 뒤 알림 · 고객에게 사전조회동의 요청 알림톡을 발송했습니다',size:9});
    L.note(s,{x:M+8.2,y:5.25,w:3.93,h:1.3,label:'상품소개 동의',text:'상품 소개에 동의한 고객은 상품 제안이 가능해요. 대문 숫자 "상품제안 가능"이 이 고객 수이고, 카드에 "AI 추천 고객" 리본이 붙어요.',tone:'grey',size:9.8});
  }});
};
