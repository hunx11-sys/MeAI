// 메리츠드림(개인영업채널 대형 행사) PPT 안의 MeAI 장 4장. 행사 PPT 톤(검정 바탕 · 금색 강조 · 굵은 고딕 · 큰 그림)에 맞춤.
// 큰 화면에서 수천 명이 보는 장이라 글은 최소, 화면 캡처 중심.
// node dream_meai.js out.pptx [재료폴더]   (재료 = assets.py 가 만든 그림)
const pptxgen = require('pptxgenjs'); const path = require('path');
const A = process.argv[3] || path.join(__dirname, 'assets');
const P = n => path.join(A, n);
const FONT = '맑은 고딕', GOLD = 'FFC000', GOLD2 = 'FFD21C', GRAY = 'B5B5B5', DIM = '737373', CARD = '141414';
const pres = new pptxgen(); pres.layout = 'LAYOUT_16x9'; pres.title = '메리츠드림 · MeAI';
const T = (s, text, o) => s.addText(text, Object.assign({ fontFace:FONT, isTextBox:true, margin:0, color:'FFFFFF', valign:'top' }, o));
const run = (text, o={}) => ({ text, options:Object.assign({ fontFace:FONT, color:'FFFFFF' }, o) });
// 제목: 행사 PPT 제목 자리(28pt 굵게, 왼쪽 위). 행사 PPT 에 끼울 때는 원래 제목 자리로 바뀜(objectName TITLE_PREVIEW)
function slide(title, notes){ const s = pres.addSlide(); s.background = { color:'000000' };
  if (title) T(s, title, { x:0.27, y:0.12, w:9.45, h:0.55, fontSize:28, bold:true, valign:'middle', objectName:'TITLE_PREVIEW' });
  if (notes) s.addNotes(notes); return s; }

// 1) MeAI 홈 — 아침마다 MeAI가 먼저 고객을 찾아온다
{ const s = slide('AI 시대, MeAI는 타사에 없는 강력한 무기',
  'MeAI 홈 화면입니다. 아침에 MeAI를 열면, 오늘 연락할 고객 아홉 분이 이유와 함께 먼저 와 있습니다. 누구에게 연락할지 고민하던 시간을 MeAI가 대신합니다. 찾는 영업에서, 찾아가는 영업으로.');
  s.addImage({ path:P('glow_wide.png'), x:3.55, y:0.55, w:6.9, h:4.9 });
  s.addImage({ path:P('hero_home.png'), x:4.62, y:1.0, w:4.9, h:4.1, altText:'MeAI 홈 화면' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:4.62, y:1.0, w:4.9, h:4.1, rectRadius:0.08, fill:{ type:'none' }, line:{ color:GOLD, width:1, transparency:45 } });
  T(s, 'MeAI 홈', { x:0.4, y:1.3, w:3.9, h:0.35, fontSize:15, bold:true, color:GOLD });
  s.addText([ run('아침마다', { fontSize:32, bold:true, breakLine:true }), run('MeAI가 먼저', { fontSize:32, bold:true, breakLine:true }), run('고객을 찾아옵니다', { fontSize:32, bold:true, color:GOLD }) ],
    { x:0.4, y:1.7, w:4.2, h:1.85, isTextBox:true, margin:0, valign:'top', lineSpacingMultiple:1.05 });
  [['오늘의 추천 고객 9명'],['왜 지금인지, 이유 한 문장'],['클릭 한 번이면 바로 대화']].forEach(([t],i)=>{ const y = 3.85 + i*0.42;
    s.addShape(pres.shapes.OVAL, { x:0.42, y:y+0.1, w:0.13, h:0.13, fill:{ color:GOLD }, line:{ color:GOLD, width:0 } });
    T(s, t, { x:0.68, y, w:3.7, h:0.33, fontSize:16, bold:true, valign:'middle' }); });
}

// 2) 영업의 처음부터 끝까지 — MeAI 홈 → 대화 → AI 보장분석 → AI 설계 → AI 리포트
{ const s = slide('MeAI 홈에서 리포트까지, 영업의 모든 과정이 하나로',
  '영업의 처음부터 끝까지가 MeAI 안에서 이어집니다. MeAI 홈이 오늘 연락할 고객을 추천하고, 클릭 한 번이면 일반대화와 맞춤대화가 열립니다. 맞춤대화에서 AI가 고객의 부족한 보장을 분석하고, 예산 안에서 설계안을 잡고, 고객에게 보낼 리포트까지 만들어 카카오톡으로 보냅니다. 찾고, 묻고, 분석하고, 설계하고, 보내는 일. 이 모든 과정이 MeAI 하나로 됩니다.');
  const steps = [
    ['01', [run('MeAI 홈')], '오늘 연락할 고객 추천', 't1_reco.png'],
    ['02', [run('일반 · 맞춤대화')], '홈에서 클릭 한 번', 't2_chat.png'],
    ['03', [run('AI ', { color:GOLD }), run('보장분석')], '부족한 보장을 한눈에', 't3_analysis.png'],
    ['04', [run('AI ', { color:GOLD }), run('설계')], '예산 안에서 설계안', 't4_design.png'],
    ['05', [run('AI ', { color:GOLD }), run('리포트')], '카카오톡으로 고객에게', 't5_report.png'],
  ];
  const x0 = 0.27, gap = 0.24, tw = (9.46 - gap*4)/5, th = tw/1.3, ty = 1.42;
  s.addImage({ path:P('glow_wide.png'), x:-0.4, y:0.9, w:10.8, h:3.6 });
  steps.forEach(([n, name, sub, img], i)=>{ const x = x0 + i*(tw+gap);
    T(s, n, { x, y:0.98, w:tw, h:0.36, fontSize:20, bold:true, color:GOLD, valign:'middle' });
    s.addImage({ path:P(img), x, y:ty, w:tw, h:th, altText:sub });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y:ty, w:tw, h:th, rectRadius:0.06, fill:{ type:'none' }, line:{ color:GOLD, width:0.75, transparency:35 } });
    s.addText(name.map(r=>({ text:r.text, options:Object.assign({}, r.options, { fontSize:17, bold:true }) })), { x, y:ty+th+0.14, w:tw, h:0.38, isTextBox:true, margin:0, valign:'middle' });
    T(s, sub, { x, y:ty+th+0.52, w:tw, h:0.3, fontSize:12, color:GRAY, valign:'middle' });
    if (i<4){ const cx = x+tw+gap/2, cy = ty+th/2, d = 0.3;
      s.addShape(pres.shapes.OVAL, { x:cx-d/2, y:cy-d/2, w:d, h:d, fill:{ color:GOLD }, line:{ color:'000000', width:1.5 } });
      T(s, '›', { x:cx-d/2, y:cy-d/2-0.02, w:d, h:d, fontSize:16, bold:true, color:'000000', align:'center', valign:'middle' }); }
  });
  s.addText([ run('이 모든 과정이, ', { fontSize:30, bold:true }), run('MeAI 하나로', { fontSize:30, bold:true, color:GOLD }) ],
    { x:0.27, y:4.1, w:9.46, h:0.7, isTextBox:true, margin:0, align:'center', valign:'middle' });
}

// 3) 숫자로 — 체결률 2.8배
{ const s = slide('MeAI는 이미 차이를 만들어내고 있음',
  '숫자가 증명합니다. MeAI를 활용한 경우 체결률이 12.7%에서 35.4%, 2.8배입니다. 원래 잘하는 사람이라서가 아닙니다. 같은 FP의 고객끼리 비교해도 9.0%에서 36.0%, 4배입니다. 그리고 질문을 많이 할수록 가계약이 늘어납니다. 질문을 한 개만 할 때보다 세 개 이상 할 때 가계약이 2.3배입니다. (출처: 2026년 8월 TA채널 MeAI 사용 데이터 분석)');
  s.addImage({ path:P('glow_round.png'), x:-0.2, y:0.75, w:5.2, h:4.6 });
  T(s, 'MeAI 활용 시 체결률', { x:0.55, y:1.3, w:4.6, h:0.4, fontSize:19, bold:true });
  s.addText([ run('2.8', { fontSize:118, bold:true, color:GOLD }), run('배', { fontSize:44, bold:true, color:GOLD }) ], { x:0.45, y:1.65, w:4.9, h:1.85, isTextBox:true, margin:0, valign:'middle' });
  s.addText([ run('미활용 12.7%', { fontSize:18, color:GRAY }), run('   →   ', { fontSize:18, color:GOLD, bold:true }), run('활용 35.4%', { fontSize:18, bold:true }) ], { x:0.55, y:3.6, w:4.8, h:0.4, isTextBox:true, margin:0, valign:'middle' });
  const cx = 5.55, cw = 9.73-cx;
  [[ '4.0', '같은 FP 고객끼리 비교', '미활용 9.0%  →  활용 36.0%' ], [ '2.3', '질문 1개 → 3개 이상', '가계약 11.99건  →  27.79건' ]].forEach(([v,a,b],i)=>{ const y = 1.3 + i*1.5;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y, w:cw, h:1.3, rectRadius:0.08, fill:{ color:CARD }, line:{ color:GOLD, width:0.75, transparency:40 } });
    s.addText([ run(v, { fontSize:46, bold:true, color:GOLD }), run('배', { fontSize:20, bold:true, color:GOLD }) ], { x:cx+0.25, y, w:1.5, h:1.3, isTextBox:true, margin:0, valign:'middle' });
    T(s, a, { x:cx+1.8, y:y+0.3, w:cw-1.9, h:0.38, fontSize:15, bold:true, valign:'middle' });
    T(s, b, { x:cx+1.8, y:y+0.7, w:cw-1.9, h:0.32, fontSize:12, color:GRAY, valign:'middle' }); });
  T(s, '출처: 2026년 8월 TA채널 MeAI 사용 데이터 분석', { x:0.55, y:4.9, w:6, h:0.25, fontSize:9, color:DIM, valign:'middle' });
}

// 4) 한 문장으로 마무리
{ const s = slide(null, '찾는 영업에서, 찾아가는 영업으로. 메리츠에만 있는 영업 AI, MeAI입니다.');
  s.addImage({ path:P('glow_wide.png'), x:0.6, y:0.7, w:8.8, h:4.2 });
  s.addText([ run('찾는 영업에서,', { fontSize:40, bold:true, breakLine:true }), run('찾아가는 영업으로', { fontSize:40, bold:true, color:GOLD }) ],
    { x:1.06, y:1.45, w:7.8, h:1.9, isTextBox:true, margin:0, align:'center', valign:'middle', lineSpacingMultiple:1.15 });
  s.addText([ run('메리츠에만 있는 영업 AI,  ', { fontSize:20, bold:true }), run('MeAI', { fontSize:24, bold:true, color:GOLD }) ],
    { x:1.06, y:3.6, w:7.8, h:0.5, isTextBox:true, margin:0, align:'center', valign:'middle' });
}
pres.writeFile({ fileName: process.argv[2] || 'dream_meai.pptx' }).then(()=>console.log('written', process.argv[2]));
