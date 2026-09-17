// Part 0: 오프닝
module.exports = async function(p, L){
  const {C, W, H, text, card, pill, icon, base, title, bullets, circle, chatBubble, chat, numBadge, notes, gradientBg, blob} = L;

  // 1. 표지 ------------------------------------------------------------
  {
    const s = base(p, {noChrome:true, bg:C.g900});
    s.addImage({path: await gradientBg('cover', ['0B1E4D','1B64DA','7C5CFC'], 25), x:0,y:0,w:W,h:H});
    s.addImage({path: await blob('pink', 'FF5C8D'), x:8.5, y:-1.5, w:6.5, h:6.5});
    s.addImage({path: await blob('teal', '00E0C7'), x:-1.5, y:3.5, w:5.5, h:5.5});
    pill(s,p,0.8,0.8,'메리츠화재 영업가족 컨설팅 교안', 'blue', {solid:true, fontSize:12});
    text(s, 0.8, 1.55, 11, 1.0, '생명보험 파헤치기', {fontSize:54, bold:true, color:C.white});
    text(s, 0.8, 2.6, 11.5, 0.9, '고객의 종신보험 증권, 어떻게 읽고 어떻게 제안할까', {fontSize:26, color:'DCE6FF'});
    text(s, 0.8, 3.65, 11.5, 0.5, '2026년 최신 통계와 트렌드로 다시 쓴 「지피지기 백전백승」 편', {fontSize:15, color:'B8C7F0'});
    // 3 feature chips
    const chips = [['📊','2026 최신 통계'],['🧬','상품 해부'],['💬','실전 화법'],['🤖','MeAI 활용']];
    chips.forEach((c,i)=>{
      const x = 0.8 + i*2.55;
      card(s,p,x,5.0,2.35,1.25,{fill:'FFFFFF', transparency:86, shadow:false});
      text(s, x+0.25, 5.15, 1.9, 0.5, c[0], {fontSize:22, color:C.white});
      text(s, x+0.25, 5.7, 2.0, 0.4, c[1], {fontSize:13, bold:true, color:C.white});
    });
    text(s, 0.8, H-0.75, 8, 0.3, '세일즈혁신TF 이헌수 · 2026.09', {fontSize:11, color:'B8C7F0'});
    notes(s,'표지. 2026년 최신 통계·규제·시장 트렌드로 구성한 생명보험 컨설팅 교안입니다.');
  }

  // 2. 왜 다시 배워야 하나 --------------------------------------------
  {
    const s = base(p, {chapter:'PROLOGUE'});
    title(s, '왜 지금, 다시 생명보험을 배워야 할까요?', '판이 바뀌었습니다. 생보의 무기가 바뀌었고, 고객의 지갑 사정도 바뀌었습니다.');
    const items = [
      ['fa6','FaArrowTrendUp','blue','금리가 다시 오릅니다','2026년 8월 기준금리 3.00%, 정기예금 3.4%대. 생보의 「이자 붙는 보험」 화법이 되살아나는 시기입니다. 예금을 못 이기는 이유를 설명할 수 있어야 합니다.'],
      ['fa6','FaShieldHeart','red','생보사가 손보 영역으로 들어왔습니다','종신보험이 안 팔리자 생보사들이 암·뇌·심장 「건강보험」을 주력으로 팝니다. 이제 경쟁 상대는 종신보험만이 아닙니다.'],
      ['fa6','FaHouseCrack','orange','단기납 종신 열풍의 후폭풍','「10년 지나면 120% 돌려받는다」로 팔린 계약이 수백만 건. 이 고객들이 지금 보장분석 테이블에 올라옵니다.'],
      ['fa6','FaUserClock','purple','초고령사회, 아픈 채로 사는 시간','기대수명은 늘었지만 건강수명은 그대로. 「사망」보다 「생존 중 치료비」가 진짜 리스크가 되었습니다.'],
    ];
    for(let i=0;i<items.length;i++){
      const [set,ic,col,h,b] = items[i];
      const x = 0.6 + (i%2)*6.15, y = 2.15 + Math.floor(i/2)*2.2;
      card(s,p,x,y,5.95,1.95);
      await icon(s,p,x+0.3,y+0.35,0.9,set,ic,col);
      text(s, x+1.45, y+0.3, 4.3, 0.5, h, {fontSize:16, bold:true, color:C.g900});
      text(s, x+1.45, y+0.8, 4.3, 1.1, b, {fontSize:12, color:C.g700});
    }
    notes(s,'도입부. 4가지 변화 요인을 짚고, 왜 지금 생명보험을 다시 배워야 하는지 공감대를 만듭니다.');
  }

  // 3. 목차 -------------------------------------------------------------
  {
    const s = base(p, {chapter:'CONTENTS'});
    title(s, '오늘의 여정', '생명보험을 해부하고 → 고객의 마음을 읽고 → 메리츠로 다시 설계합니다');
    const ch = [
      ['01','판이 바뀌었다','2026 시장 지형도 · 통계','blue','📈'],
      ['02','상품 해부학','이름만 봐도 아는 생보 상품','purple','🔬'],
      ['03','정면 비교','생보 vs 메리츠 · 만기까지 사망 vs 생존','red','⚖️'],
      ['04','고객의 마음','왜 종신보험을 가입했나','orange','🧠'],
      ['05','파훼법 5','거절을 녹이는 실전 화법','green','🗝️'],
      ['06','MeAI 솔루션','약관 조회 → 맞춤대화 → 가계약 설계','teal','🤖'],
    ];
    ch.forEach((c,i)=>{
      const x = 0.6 + (i%3)*4.1, y = 2.15 + Math.floor(i/3)*2.35;
      card(s,p,x,y,3.9,2.1);
      text(s, x+0.3, y+0.25, 1.5, 0.5, c[0], {fontSize:28, bold:true, color:C[c[3]]});
      text(s, x+2.9, y+0.2, 0.8, 0.6, c[4], {fontSize:26, align:'right'});
      text(s, x+0.3, y+0.95, 3.3, 0.45, c[1], {fontSize:18, bold:true, color:C.g900});
      text(s, x+0.3, y+1.4, 3.3, 0.5, c[2], {fontSize:12, color:C.g600});
    });
  }

  // 4. 아이스브레이킹: 생보 증권을 만나면 ------------------------------
  {
    const s = base(p, {chapter:'PROLOGUE'});
    title(s, '보장분석 중 생명보험 증권을 만나면, 어떤 기분이세요?');
    // two faces
    card(s,p,0.6,2.0,5.9,3.9,{fill:C.redL, shadow:false});
    text(s, 0.9, 2.3, 5.3, 0.8, '😰', {fontSize:44});
    text(s, 0.9, 3.25, 5.3, 0.6, '"생소한데… 어떻게 이야기하지?"', {fontSize:20, bold:true, color:C.redD});
    bullets(s, 0.9, 3.95, 5.3, 1.8, ['상품명이 외계어 같다 (변액·유니버셜·CI·달러…)','생보 설계사가 이미 「좋다」고 설득해 놓은 상태','괜히 건드렸다가 고객 기분만 상할까 걱정'], {fontSize:13, color:C.g800});
    card(s,p,6.85,2.0,5.9,3.9,{fill:C.greenL, shadow:false});
    text(s, 7.15, 2.3, 5.3, 0.8, '😎', {fontSize:44});
    text(s, 7.15, 3.25, 5.3, 0.6, '"아싸! 잘 걸렸다!"', {fontSize:20, bold:true, color:C.greenD});
    bullets(s, 7.15, 3.95, 5.3, 1.8, ['이름만 봐도 구조와 약점이 보인다','고객이 왜 가입했는지 3분 대화로 읽어낸다','사망은 정기로, 생존은 메리츠로 — 제안이 저절로 나온다'], {fontSize:13, color:C.g800});
    text(s, 0.6, 6.15, 12, 0.5, '오늘 교육이 끝나면 왼쪽 얼굴이 오른쪽 얼굴로 바뀝니다. 생보 증권은 「위기」가 아니라 「가장 좋은 대화 소재」입니다.', {fontSize:14, bold:true, color:C.g800, align:'center'});
    notes(s,'아이스브레이킹. 손을 들어보게 하세요. 대부분 왼쪽입니다.');
  }

  // 5. 워밍업: 10억 버스 이야기 -----------------------------------------
  {
    const s = base(p, {chapter:'WARM-UP', chapterColor:'orange'});
    title(s, '워밍업 퀴즈 — "저는 사망하면 10억 나와요"', '고객이 기억하는 건 숫자 하나. 약관이 기억하는 건 단서 조항 전부.');
    let y = 2.2;
    y += chat(s,p,y,'FP님, 저는 옛날에 생보에서 가입해서요. 사망하면 10억 나옵니다. 더 필요 없어요.','left') + 0.16;
    y += chat(s,p,y,'오, 든든하시겠어요! 그런데 혹시 그 10억이 「언제, 어떤 상황」의 사망인지 증권에서 같이 확인해 볼까요?','right') + 0.16;
    y += chat(s,p,y,'…확인해 보니 「평일에, 대중교통 버스를 이용하다가, 사고로」 사망하면 10억이네요. 일반 사망은 5천만원이고요.','left') + 0.16;
    const by=Math.min(Math.max(y+0.35,4.6),5.55); card(s,p,0.6,by,12.1,1.3,{fill:C.orangeL, shadow:false});
    text(s, 0.9, by+0.15, 11.5, 0.5, '🚌  "사망하면 10억"과 "평일 대중교통 사고로 사망하면 10억"은 완전히 다른 보험입니다.', {fontSize:15, bold:true, color:'B25E00'});
    text(s, 0.9, by+0.65, 11.5, 0.55, '좋은 보험의 정의는 단순합니다. 단서 조항이 적고, 명확하고, 보험금 받기 쉬운 보험. 오늘 우리는 생보 증권의 「단서 조항」을 읽는 법을 배웁니다.', {fontSize:12.5, color:C.g800});
    notes(s,'현장 실제 사례. 교통재해사망특약(대중교통 이용 중 재해사망 시 고액)을 「사망 시 10억」으로 기억하는 고객 이야기입니다.');
  }
};
