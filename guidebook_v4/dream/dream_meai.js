// 메리츠드림(개인영업채널 대형 행사) PPT 안의 MeAI 장 5장. 행사 PPT 톤(검정 바탕 · 금색 강조 · 굵은 고딕 · 큰 그림)에 맞춤.
// 큰 화면에서 수천 명이 보는 장이라 글은 최소, 화면 캡처 중심. 행사 키워드 YOUR TURN(이제, 당신이 주인공)으로 열고 닫는다.
//   0 여는 장 : 영업가족이 꿈꿔 온 것 3가지 → YOUR TURN, 이제 MeAI로 그 꿈이 현실이 될 차례
//   1 MeAI 홈 : 아침마다 MeAI가 먼저 고객을 찾아온다(추천 이유 한 문장을 크게)
//   2 흐름   : MeAI 홈 → 일반·맞춤대화 → AI 보장분석 → AI 설계 → AI 리포트, MeAI 하나로
//   3 숫자   : 체결률 2.8배 · 같은 FP 고객끼리 4배 · 질문 3개 이상 가계약 2.3배(출처 표기)
//   4 닫는 장 : 주인공을 꿈꾸는 사람들에게, 주인공으로 만들어주는 AI를 → MeAI
// node dream_meai.js out.pptx [재료폴더]   (재료 = assets.py 가 만든 그림)
const pptxgen = require('pptxgenjs'); const path = require('path');
const A = process.argv[3] || path.join(__dirname, 'assets');
const P = n => path.join(A, n);
const FONT = '맑은 고딕', LATIN = 'Arial', GOLD = 'FFC000', GRAY = 'B5B5B5', LIGHT = 'D9D9D9', CARD = '141414', RED = 'E5252A';
const W = 10;
const pres = new pptxgen(); pres.layout = 'LAYOUT_16x9'; pres.title = '메리츠드림 · MeAI';
const T = (s, text, o) => s.addText(text, Object.assign({ fontFace:FONT, isTextBox:true, margin:0, color:'FFFFFF', valign:'top' }, o));
const run = (text, o={}) => ({ text, options:Object.assign({ fontFace:FONT, color:'FFFFFF' }, o) });
const glow = (s, name, o) => s.addImage(Object.assign({ path:P(name), altText:'배경 빛' }, o));
const EXAMPLE = '※ 화면 속 이름·숫자는 예시';
// 제목: 행사 PPT 제목 자리(28pt 굵게, 왼쪽 위). 행사 PPT 에 끼울 때는 원래 제목 자리로 바뀜(objectName TITLE_PREVIEW)
function slide(title, notes){ const s = pres.addSlide(); s.background = { color:'000000' };
  if (title) T(s, title, { x:0.27, y:0.12, w:9.45, h:0.55, fontSize:28, bold:true, valign:'middle', objectName:'TITLE_PREVIEW' });
  if (notes) s.addNotes(notes); return s; }

// 0) 여는 장 — 영업가족이 꿈꿔 온 것 → YOUR TURN
{ const s = slide(null,
  '영업하며 한 번쯤, 이런 꿈 꿔 보셨을 겁니다. 고객을 매일 아침 누가 추천해 준다면. 약관을 공시실에 들어갈 필요 없이 바로 볼 수 있다면. 보장분석, 설계, 리포트까지 자동으로 만들어 준다면. YOUR TURN. 이제, MeAI로 그 꿈이 현실이 될 차례입니다.');
  glow(s, 'glow_wide.png', { x:1.0, y:3.0, w:8.0, h:2.5, transparency:30 });
  T(s, '영업하며 한 번쯤, 이런 꿈 꿔 보셨죠?', { x:0.3, y:0.5, w:W-0.6, h:0.5, fontSize:24, bold:true, align:'center', valign:'middle' });
  [ [run('고객을 '), run('매일 아침', { color:GOLD }), run(' 추천해준다면?')],
    [run('약관을 '), run('공시실에 들어갈 필요 없이', { color:GOLD }), run(' 볼 수 있다면?')],
    [run('자동으로', { color:GOLD }), run(' 보장분석, 설계, 리포트까지 만들어준다면?')],
  ].forEach((r,i)=> s.addText(r.map(t=>({ text:t.text, options:Object.assign({}, t.options, { fontSize:26, bold:true }) })),
      { x:0.3, y:1.22+i*0.7, w:W-0.6, h:0.6, isTextBox:true, margin:0, align:'center', valign:'middle' }));
  s.addText([ run('YOUR TURN', { fontFace:LATIN, fontSize:40, bold:true, color:GOLD }) ], { x:0.3, y:3.42, w:W-0.6, h:0.7, isTextBox:true, margin:0, align:'center', valign:'middle' });
  s.addText([ run('이제, ', { fontSize:24, bold:true }), run('MeAI', { fontFace:LATIN, fontSize:24, bold:true, color:GOLD }), run('로 그 꿈이 현실이 될 차례입니다', { fontSize:24, bold:true }) ],
    { x:0.3, y:4.12, w:W-0.6, h:0.5, isTextBox:true, margin:0, align:'center', valign:'middle' });
}

// 1) MeAI 홈 — 아침마다 MeAI가 먼저 고객을 찾아온다
{ const s = slide('AI 시대, MeAI는 타사에 없는 강력한 무기',
  'MeAI 홈 화면입니다. 아침에 MeAI를 열면, 오늘 연락할 추천 고객 아홉 분이 이유와 함께 먼저 와 있습니다. 예를 들어 이 고객은 상령일이 2주 남았고 암진단비가 1천만원뿐이라는 이유가 한 문장으로 적혀 있습니다. 누구에게, 왜 지금 연락할지 고민하던 시간을 MeAI가 대신합니다. 그리고 홈에서 바로 대화로 이어지고, 약관도 대화로 바로 확인합니다.');
  const hx = 4.75, hy = 0.98, hw = 4.75, hs = hw/2320, hh = 2000*hs;        // hero_home.png 2320x2000
  glow(s, 'glow_wide.png', { x:3.7, y:0.5, w:6.9, h:5.0 });
  s.addImage({ path:P('hero_home.png'), x:hx, y:hy, w:hw, h:hh, altText:'MeAI 홈 화면(오늘의 추천 고객)' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:hx, y:hy, w:hw, h:hh, rectRadius:0.08, fill:{ type:'none' }, line:{ color:GOLD, width:1, transparency:45 } });
  // 추천 카드(김민수) 테두리 · 왼쪽 인용 카드와 잇는 선
  const kx = hx+38*hs, ky = hy+1120*hs, kw = (770-38)*hs, kh = (1920-1120)*hs;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:kx, y:ky, w:kw, h:kh, rectRadius:0.06, fill:{ type:'none' }, line:{ color:GOLD, width:2.25 } });
  T(s, 'MeAI 홈  ·  오늘의 추천 고객 9명', { x:0.4, y:1.05, w:4.2, h:0.34, fontSize:15, bold:true, color:GOLD, valign:'middle' });
  s.addText([ run('아침마다', { fontSize:32, bold:true, breakLine:true }), run('MeAI가 먼저', { fontSize:32, bold:true, breakLine:true }), run('고객을 찾아옵니다', { fontSize:32, bold:true, color:GOLD }) ],
    { x:0.4, y:1.5, w:4.2, h:1.8, isTextBox:true, margin:0, valign:'top', lineSpacingMultiple:1.05 });
  const qx = 0.4, qy = 3.55, qw = 3.95, qh = 1.22;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:qx, y:qy, w:qw, h:qh, rectRadius:0.08, fill:{ color:CARD }, line:{ color:GOLD, width:1, transparency:30 } });
  T(s, '왜 지금 연락할지, 이유 한 문장', { x:qx+0.22, y:qy+0.14, w:qw-0.4, h:0.28, fontSize:12, bold:true, color:GRAY, valign:'middle' });
  s.addText([ run('“상령일이 2주 남았고', { fontSize:16, bold:true, breakLine:true }), run('암진단비가 1천만원뿐입니다.”', { fontSize:16, bold:true }) ],
    { x:qx+0.22, y:qy+0.46, w:qw-0.36, h:0.66, isTextBox:true, margin:0, valign:'middle', lineSpacingMultiple:1.1 });
  const lx1 = qx+qw, ly1 = qy+qh/2, lx2 = kx, ly2 = ky+0.42;              // 인용 카드 → 추천 카드 이유 줄
  s.addShape(pres.shapes.LINE, { x:lx1, y:Math.min(ly1,ly2), w:lx2-lx1, h:Math.abs(ly2-ly1)||0.001, flipV: ly2<ly1, line:{ color:GOLD, width:1.5 } });
  T(s, EXAMPLE, { x:0.4, y:5.0, w:3.95, h:0.28, fontSize:12, color:GRAY, valign:'middle' });
}

// 2) 영업의 처음부터 끝까지 — MeAI 홈 → 대화 → AI 보장분석 → AI 설계 → AI 리포트
{ const s = slide('MeAI 홈에서 리포트까지, 모든 영업 과정이 하나로',
  'MeAI 홈이 오늘 연락할 고객을 추천하고, 홈에서 바로 일반대화와 맞춤대화로 이어집니다. 일반대화에서는 공시실에 들어가지 않아도 약관을 바로 확인합니다. 맞춤대화에서 AI가 고객의 부족한 보장을 분석하고, 예산을 말하면 설계안을 잡아 줍니다. 고객에게 보여 줄 답변을 골라 확인하면, 리포트가 카카오톡으로 고객에게 갑니다. 찾고, 묻고, 분석하고, 설계하고, 보내는 일. 이 모든 과정이 MeAI 하나로 됩니다.');
  const steps = [
    ['01', [run('MeAI 홈')], '오늘 연락할 고객 추천', 't1_reco.png'],
    ['02', [run('일반 · 맞춤대화')], '공시실 없이 약관 확인', 't2_chat.png'],
    ['03', [run('AI ', { color:GOLD }), run('보장분석')], '부족한 보장을 한눈에', 't3_analysis.png'],
    ['04', [run('AI ', { color:GOLD }), run('설계')], '예산을 말하면 설계안', 't4_design.png'],
    ['05', [run('AI ', { color:GOLD }), run('리포트')], '카카오톡으로 발송', 't5_report.png'],
  ];
  const x0 = 0.27, gap = 0.24, tw = (9.46 - gap*4)/5, th = 2.15, ty = 1.18;
  steps.forEach(([n, name, sub, img], i)=>{ const x = x0 + i*(tw+gap), cw = i<4 ? tw+gap-0.02 : tw;   // 아래 글은 옆 칸 사이까지 넓게(맑은 고딕 폭 여유)
    T(s, n, { x, y:0.78, w:tw, h:0.34, fontSize:20, bold:true, color:GOLD, valign:'middle' });
    s.addImage({ path:P(img), x, y:ty, w:tw, h:th, altText:sub });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y:ty, w:tw, h:th, rectRadius:0.06, fill:{ type:'none' }, line:{ color:GOLD, width:0.75, transparency:35 } });
    s.addText(name.map(r=>({ text:r.text, options:Object.assign({}, r.options, { fontSize:17, bold:true }) })), { x, y:ty+th+0.1, w:cw, h:0.36, isTextBox:true, margin:0, valign:'middle' });
    T(s, sub, { x, y:ty+th+0.47, w:cw, h:0.3, fontSize:13, color:LIGHT, valign:'middle' });
    if (i<4){ const cx = x+tw+gap/2, cy = ty+th/2, d = 0.3;
      s.addShape(pres.shapes.OVAL, { x:cx-d/2, y:cy-d/2, w:d, h:d, fill:{ color:GOLD }, line:{ color:'000000', width:1.5 } });
      T(s, '›', { x:cx-d/2, y:cy-d/2-0.02, w:d, h:d, fontSize:16, bold:true, color:'000000', align:'center', valign:'middle' }); }
    if (i===2){ // 보장분석: 표 아래 '미가입 2건'
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x+0.2, y:ty+1.32, w:tw-0.4, h:0.4, rectRadius:0.2, fill:{ color:RED }, line:{ color:RED, width:0 } });
      T(s, '미가입 2건', { x:x+0.2, y:ty+1.32, w:tw-0.4, h:0.4, fontSize:15, bold:true, align:'center', valign:'middle' }); }
    if (i===3){ // 설계: 맞춤대화 입력 말풍선(예시 요청 · 답은 만들지 않음)
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x+0.06, y:ty+0.86, w:tw-0.12, h:0.9, rectRadius:0.12, fill:{ color:'FFFFFF' }, line:{ color:GOLD, width:2 } });
      s.addText([ run('월 5만 원 안에서', { fontSize:14, bold:true, color:'111111', breakLine:true }), run('설계안 만들어줘', { fontSize:14, bold:true, color:'111111' }) ],
        { x:x+0.06, y:ty+0.86, w:tw-0.12, h:0.9, isTextBox:true, margin:0, align:'center', valign:'middle', lineSpacingMultiple:1.15 }); }
  });
  s.addText([ run('이 모든 과정이, ', { fontSize:28, bold:true }), run('MeAI 하나로', { fontSize:28, bold:true, color:GOLD }) ],
    { x:0.27, y:4.32, w:9.46, h:0.6, isTextBox:true, margin:0, align:'center', valign:'middle' });
  T(s, EXAMPLE, { x:0.27, y:5.05, w:4, h:0.28, fontSize:12, color:GRAY, valign:'middle' });
}

// 3) 숫자로 — 체결률 2.8배 (소유자 원안의 질문 장치: 효과가 있어? / 원래 잘하는 사람 아니야? / 질문이 의미가 있어?)
{ const s = slide('MeAI는 이미 차이를 만들어내고 있음',
  '숫자로 보겠습니다. MeAI를 활용한 경우 체결률이 12.7%에서 35.4%, 2.8배였습니다. 원래 잘하는 사람이라서일까요? 같은 FP의 고객끼리 비교해도 9.0%에서 36.0%, 4배였습니다. 질문이 의미가 있을까요? 질문을 한 개만 한 경우보다 세 개 이상 한 경우 평균 가계약이 12건에서 28건, 2.3배였습니다. (출처: 2026년 8월 TA채널 MeAI 사용 데이터 분석)');
  T(s, '효과가 있어?', { x:0.55, y:1.02, w:4.6, h:0.32, fontSize:15, bold:true, color:GOLD, valign:'middle' });
  T(s, 'MeAI 활용 시 체결률', { x:0.55, y:1.36, w:4.6, h:0.4, fontSize:19, bold:true, valign:'middle' });
  s.addText([ run('2.8', { fontSize:118, bold:true, color:GOLD }), run('배', { fontSize:44, bold:true, color:GOLD }) ], { x:0.45, y:1.72, w:4.9, h:1.85, isTextBox:true, margin:0, valign:'middle' });
  s.addText([ run('미활용 12.7%', { fontSize:18, color:GRAY }), run('   →   ', { fontSize:18, color:GOLD, bold:true }), run('활용 35.4%', { fontSize:18, bold:true }) ], { x:0.55, y:3.67, w:4.8, h:0.4, isTextBox:true, margin:0, valign:'middle' });
  const cx = 5.55, cw = 9.73-cx, ch = 1.38;
  [[ '4.0', '원래 잘하는 사람 아니야?', '같은 FP 고객끼리도', '미활용 9.0% → 활용 36.0%' ],
   [ '2.3', '질문이 의미가 있어?', '질문 1개 → 3개 이상', '평균 가계약 12건 → 28건' ]].forEach(([v,q,a,b],i)=>{ const y = 1.1 + i*1.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y, w:cw, h:ch, rectRadius:0.08, fill:{ color:CARD }, line:{ color:GOLD, width:0.75, transparency:40 } });
    s.addText([ run(v, { fontSize:46, bold:true, color:GOLD }), run('배', { fontSize:20, bold:true, color:GOLD }) ], { x:cx+0.25, y, w:1.5, h:ch, isTextBox:true, margin:0, valign:'middle' });
    T(s, q, { x:cx+1.8, y:y+0.2, w:cw-1.9, h:0.3, fontSize:13, bold:true, color:GOLD, valign:'middle' });
    T(s, a, { x:cx+1.8, y:y+0.5, w:cw-1.9, h:0.36, fontSize:15, bold:true, valign:'middle' });
    T(s, b, { x:cx+1.8, y:y+0.88, w:cw-1.9, h:0.3, fontSize:12, color:GRAY, valign:'middle' }); });
  T(s, '출처: 2026년 8월 TA채널 MeAI 사용 데이터 분석', { x:0.55, y:4.6, w:9.18, h:0.3, fontSize:12, color:GRAY, valign:'middle' });
}

// 4) 닫는 장 — 주인공으로 만들어주는 AI, MeAI
{ const s = slide(null, '주인공을 꿈꾸는 사람들에게, 주인공으로 만들어주는 AI를. 메리츠의 MeAI입니다.');
  glow(s, 'glow_wide.png', { x:1.0, y:2.2, w:8.0, h:3.1, transparency:20 });
  s.addText([ run('주인공을 꿈꾸는 사람들에게,', { fontSize:34, bold:true, breakLine:true }), run('주인공으로 만들어주는 AI를', { fontSize:34, bold:true, color:GOLD }) ],
    { x:0.3, y:0.85, w:W-0.6, h:1.75, isTextBox:true, margin:0, align:'center', valign:'middle', lineSpacingMultiple:1.2 });
  s.addText([ run('MeAI', { fontFace:LATIN, fontSize:84, bold:true, color:GOLD }) ], { x:0.3, y:2.95, w:W-0.6, h:1.55, isTextBox:true, margin:0, align:'center', valign:'middle' });
}
pres.writeFile({ fileName: process.argv[2] || 'dream_meai.pptx' }).then(()=>console.log('written', process.argv[2]));
