// 표지 · 한 장 요약 · 목차
module.exports = function(pres, L, N){
  const {T,W,H,M,CW} = L;
  pres.addSection({ title:'도입' });
  // 00 표지
  let s = pres.addSlide({ masterName:'LIGHT', sectionTitle:'도입' });
  // 배경 번짐(토스 hero mesh 느낌) : 큰 연한 원 두 개
  s.addShape('ellipse', { x:W-4.2, y:-1.6, w:5.2, h:5.2, fill:{ color:T.blueBg2, transparency:45 }, line:{ color:T.blueBg2, transparency:100 } });
  s.addShape('ellipse', { x:-1.4, y:H-2.6, w:3.6, h:3.6, fill:{ color:'DCEBFF', transparency:50 }, line:{ color:'DCEBFF', transparency:100 } });
  let cx = M; cx += L.chip(s, cx, 1.55, '세일즈혁신 교안', 'b', {fontSize:11,h:0.34}) + 0.12; L.chip(s, cx, 1.55, '설계사 교육  ·  입원적정성 편', 'g', {fontSize:11,h:0.34});
  L.txt(s, '입원인 줄 알았는데 통원이었다', { x:M, y:2.1, w:8.6, h:0.9, fontSize:44, bold:true, color:T.fg, charSpacing:-3, lineSpacingMultiple:1.05 });
  L.txt(s, '입원적정성, 입원이 통원이 되는 시대의 보장 설계', { x:M, y:3.0, w:8.6, h:0.7, fontSize:26, bold:true, color:T.blue, charSpacing:-1.5 });
  L.txt(s, [ {text:'메리츠화재 세일즈혁신', options:{bold:true, color:T.fg}}, {text:'   2026. 10. 23 (금)', options:{color:T.fg2}} ], { x:M, y:3.95, w:8, h:0.35, fontSize:13 });
  L.txt(s, '왜 논란인가 · 고객이 손해 보는 사례 · 의료·건보·실손의 배경 · 실손 재매입 · 당사 특약 점검과 트렌드', { x:M, y:4.35, w:8.2, h:0.6, fontSize:12, color:T.fg3, lineSpacingMultiple:1.3 });
  // 오른쪽 숫자 카드 (bz 느낌 : 회색 틀 + 흰 카드)
  s.addShape('roundRect', { x:W-M-3.45, y:1.5, w:3.45, h:3.4, fill:{color:T.bg3}, line:{color:T.bg3}, rectRadius:0.2 });
  L.card(s, W-M-3.33, 1.62, 3.21, 3.16, 'white');
  L.txt(s, '병원 침대에 누웠다고 입원이 아니다', { x:W-M-3.05, y:1.9, w:2.8, h:0.3, fontSize:11, bold:true, color:T.red });
  L.txt(s, '6h', { x:W-M-3.05, y:2.25, w:2.8, h:1.5, fontSize:92, bold:true, color:T.blue, charSpacing:-6, valign:'middle' });
  L.txt(s, '병원에 머문 시간이 짧으면 입원이 아니라 통원으로 본 분쟁 사례의 기준선. 자세한 내용은 2부', { x:W-M-3.05, y:3.85, w:2.8, h:0.75, fontSize:10.5, color:T.fg2, lineSpacingMultiple:1.3 });

  // 01 한 장 요약
  s = pres.addSlide({ masterName:'ALT', sectionTitle:'도입' });
  L.kicker(s, '한 장 요약', `02 / ${N}`);
  L.title(s, '한 장 요약. 입원은 줄고 심사는 는다, 그래서 보장은 「입원」이 아니라 「치료 행위」에 걸어야 한다');
  L.sub(s, '주: 수치는 출처를 붙였고, 출처가 없는 값은 「추정」으로 표시했다. 특약 이름은 당사 약관 명칭 그대로다');
  const cards = [
    ['01','왜 논란인가','입원의 뜻은 약관이 정하고, 판정은 심평원과 보험사가 한다. 고객은 침대에 누운 사실만 기억한다. 세 시선이 다르니 분쟁이 생긴다','1부'],
    ['02','고객이 손해 보는 사례','백내장 다초점, 당일 입퇴원, 도수치료 입원, 하이푸·맘모톰, 요양·한방병원, 응급실 체류. 여섯 사례 모두 「입원」이 「통원」으로 바뀌며 한도가 줄었다','2부'],
    ['03','네 가지 배경','의료기술은 재원일수를 줄이고, 건보 재정은 입원을 억제하고, 실손 손해율은 심사를 늘리고, 제도는 비급여를 관리한다. 네 힘이 한 방향이다','3부·4부'],
    ['04','당사 특약과 트렌드','입원이 지급 조건인 특약(입원일당 계열)은 설명 의무가 커지고, 치료 행위가 조건인 특약(수술비·치료비·통원일당·통합치료비)은 가치가 오른다','5부·6부'],
  ];
  const cw=(CW-0.3)/2, ch=1.45;
  cards.forEach((c,i)=>{
    const x = M + (i%2)*(cw+0.3), y = 2.55 + Math.floor(i/2)*(ch+0.18);
    const dark = i===3;
    L.card(s, x,y,cw,ch, dark?'ink':'white');
    L.chip(s, x+0.3, y+0.25, c[0], dark?'w':'b');
    L.chip(s, x+cw-0.3-1.0, y+0.25, c[3], dark?'w':'g', {w:1.0});
    L.txt(s, c[1], { x:x+0.3, y:y+0.62, w:cw-0.6, h:0.35, fontSize:15, bold:true, color:dark?'FFFFFF':T.fg });
    L.txt(s, c[2], { x:x+0.3, y:y+0.95, w:cw-0.6, h:0.5, fontSize:10.5, color:dark?'C9D2DF':T.fg2, lineSpacingMultiple:1.3 });
  });
  L.take(s, '설계 한 줄 정리: 「며칠 입원했나」가 아니라 「무슨 치료를 받았나」로 보장을 설명하고 설계한다');

  // 02 목차 (INK)
  s = pres.addSlide({ masterName:'INK', sectionTitle:'도입' });
  L.kicker(s, '교육 순서', `03 / ${N}`, true);
  L.txt(s, '여섯 부분, 질문 하나', { x:M, y:1.1, w:6, h:0.8, fontSize:36, bold:true, color:'FFFFFF', charSpacing:-2 });
  L.txt(s, '「고객이 입원했다고 믿는 순간, 보험은 무엇을 보고 있는가」', { x:M, y:1.95, w:6.2, h:0.9, fontSize:16, color:'B9C2CF', lineSpacingMultiple:1.4 });
  const ag = [['01','입원적정성이란','약관의 입원 정의 · 심사 제도 · 세 시선'],['02','고객이 손해 보는 사례','여섯 장면, 입원이 통원이 되는 순간'],['03','네 가지 배경','의료기술 · 건보 재정 · 실손 손해율 · 제도'],['04','실손 재매입과 5세대','1~2세대 재매입 · 5세대 구조 · 고객 선택'],['05','당사 특약 점검','논란 소지 특약 · 가치가 오르는 특약 · 잠재력 순위'],['06','현장 실천','상담 화법 · 입원 전 안내 5가지 · 정리']];
  ag.forEach((a,i)=>{
    const y = 1.15 + i*0.78; const x = M+6.6; const w = CW-6.6;
    s.addShape('roundRect', { x, y, w, h:0.66, fill:{ color: i===0 ? '2A3240' : T.ink }, line:{ color: i===0 ? '3A4453' : T.ink, width:0.75 }, rectRadius:0.1 });
    L.txt(s, a[0], { x:x+0.25, y, w:0.5, h:0.66, fontSize:11, bold:true, color: i===0 ? T.blue : '6B7684', valign:'middle' });
    L.txt(s, a[1], { x:x+0.75, y:y+0.08, w:w-1, h:0.3, fontSize:14, bold:true, color: i===0 ? 'FFFFFF' : 'C9D2DF', valign:'middle' });
    L.txt(s, a[2], { x:x+0.75, y:y+0.36, w:w-1, h:0.26, fontSize:10, color: '8B95A1', valign:'middle' });
  });
  L.txt(s, '진행 90분 기준. 각 부 끝의 「한 줄 정리」만 모아도 교육의 뼈대가 된다', { x:M, y:5.9, w:6, h:0.5, fontSize:11, color:'6B7684' });
};
