// 메리츠드림 MeAI 장 덧붙임 — '기존 영업포탈 12단계 vs MeAI 한 화면 3단계'(WOW 비교 장)
// 왼쪽: 영업포탈 실제 화면 5장을 어둡게 겹쳐 쌓고, 그 위를 12개 단계가 이리저리 오감(메뉴 5곳 · 정보 다시 입력)
// 오른쪽: MeAI 맞춤대화 한 화면에 ①고객 정보 입력 ②보장분석 해줘 ③설계안 만들어줘 — 금빛
// 기존 단계 근거: 세일즈혁신TF 영업포탈 현황 진단(2026.7) — 고객 등록 3(고객등록·직업코드 조회·질문톡 직업 확인) ·
//   보장 확인 4(고객정보조회·장기계약조회·자동차 계약조회·사고진행관리) · 설계 5(가입설계 진입·상품/플랜 선택·실손정액 조회 팝업·상품 시뮬레이션·담보 패키지 선택)
// node dream_portal_vs_meai.js out.pptx <재료폴더>   (재료 = assets_portal.py + glow_wide.png)
const pptxgen = require('pptxgenjs'); const path = require('path');
const A = process.argv[3] || path.join(__dirname, 'assets'); const P = n => path.join(A, n);
const FONT = '맑은 고딕', LATIN = 'Arial', GOLD = 'FFC000', GRAY = 'B5B5B5', MUTE = '8C8C8C', MUTE2 = 'A6A6A6';
const T = (s, text, o) => s.addText(text, Object.assign({ fontFace:FONT, lang:'ko-KR', isTextBox:true, margin:0, color:'FFFFFF', bold:true, valign:'middle' }, o));
const pres = new pptxgen(); pres.layout = 'LAYOUT_16x9'; pres.title = '메리츠드림 · MeAI';
const s = pres.addSlide(); s.background = { color:'000000' };
s.addNotes('기존 영업포탈에서는 고객 한 분을 등록하고, 보장을 확인하고, 설계하기까지 메뉴 다섯 곳을 오가며 열두 단계를 거쳐야 했습니다. 화면을 옮길 때마다 고객 정보도 다시 넣었습니다. '
  + 'MeAI에서는 한 화면입니다. 고객 정보를 넣고, "보장분석 해줘", 그리고 "월 5만 원 안에서 설계안 만들어줘". 세 단계면 됩니다. '
  + '(참고 — 기존 12단계: 고객 등록 3 · 보장 확인 4 · 설계 5, 세일즈혁신TF 영업포탈 현황 진단 기준. MeAI 설계안은 초안이며 청약은 영업포탈에서 이어집니다.)');
// 제목(행사 PPT 에 끼울 때 원래 제목 자리로 바뀜)
T(s, '고객 등록부터 설계까지, 12단계가 3단계로', { x:0.27, y:0.12, w:9.45, h:0.55, fontSize:28, objectName:'TITLE_PREVIEW' });

// ── 왼쪽: 기존 영업포탈 ─────────────────────────────
const LX = 0.3, LR = 4.8;
T(s, '기존 영업포탈', { x:LX, y:0.84, w:2.4, h:0.42, fontSize:16, color:MUTE });
T(s, '12단계', { x:LR-2.0, y:0.8, w:2.0, h:0.5, fontSize:28, color:MUTE2, align:'right' });
const wins = [ // [그림, x, y, 너비, 기울기]
  ['L1_customer_dim.png', 0.30, 1.42, 2.15, -4], ['L8_contract_dim.png', 1.48, 1.33, 2.15, 3], ['L9_claim_dim.png', 2.62, 1.50, 2.12, -3],
  ['L4_product_dim.png', 0.62, 2.55, 2.15, 3], ['L6_design_cover_dim.png', 2.22, 2.60, 2.15, -2] ];
const AR = { 'L1_customer_dim.png':982/1247, 'L8_contract_dim.png':982/1247, 'L9_claim_dim.png':982/1247, 'L4_product_dim.png':1043/1448, 'L6_design_cover_dim.png':1043/1448 };
wins.forEach(([f,x,y,w,r]) => s.addImage({ path:P(f), x, y, w, h:w*AR[f], rotate:r, altText:'기존 영업포탈 화면' }));
// 12단계가 화면 사이를 오가는 길
const nodes = [[0.62,1.80],[1.12,2.10],[0.72,2.42], [1.86,1.70],[2.38,2.00],[3.08,1.78],[3.86,2.08], [1.05,3.00],[1.62,3.36],[2.52,3.00],[3.22,3.40],[3.96,3.08]];
for (let i=0;i<nodes.length-1;i++){ const [x1,y1]=nodes[i], [x2,y2]=nodes[i+1];
  s.addShape(pres.shapes.LINE, { x:Math.min(x1,x2), y:Math.min(y1,y2), w:Math.abs(x2-x1)||0.001, h:Math.abs(y2-y1)||0.001,
    flipV:(x2<x1)!==(y2<y1), line:{ color:'D9D9D9', width:2.25 } }); }
nodes.forEach(([x,y],i)=>{ const d=0.3;
  s.addShape(pres.shapes.OVAL, { x:x-d/2, y:y-d/2, w:d, h:d, fill:{ color:'4D4D4D' }, line:{ color:'BFBFBF', width:1 } });
  T(s, String(i+1), { x:x-d/2, y:y-d/2, w:d, h:d, fontFace:LATIN, fontSize:10, align:'center', color:'FFFFFF' }); });
T(s, '메뉴 5곳을 오가며 · 고객정보 다시 입력', { x:LX, y:4.3, w:LR-LX, h:0.36, fontSize:14, color:MUTE });

// ── 가운데 화살표 ───────────────────────────────────
{ const d=0.42, cx=5.0, cy=2.74; s.addShape(pres.shapes.OVAL, { x:cx-d/2, y:cy-d/2, w:d, h:d, fill:{ color:GOLD }, line:{ color:'000000', width:2 } });
  T(s, '›', { x:cx-d/2, y:cy-d/2-0.03, w:d, h:d, fontSize:22, color:'000000', align:'center' }); }

// ── 오른쪽: MeAI 한 화면 ────────────────────────────
const RX = 5.2, RW = 4.5, RY = 1.33, RH = RW*1800/2880;
s.addImage({ path:P('glow_wide.png'), x:RX-0.75, y:RY-0.75, w:RW+1.5, h:RH+1.5, altText:'배경 빛' });
s.addText([{ text:'MeAI', options:{ fontFace:LATIN, bold:true, color:GOLD, fontSize:16 } }], { x:RX, y:0.84, w:2.0, h:0.42, isTextBox:true, margin:0, valign:'middle' });
T(s, '한 화면 3단계', { x:RX+RW-2.6, y:0.8, w:2.6, h:0.5, fontSize:28, color:GOLD, align:'right' });
s.addImage({ path:P('meai_one_screen.png'), x:RX, y:RY, w:RW, h:RH, altText:'MeAI 맞춤대화 화면' });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:RX, y:RY, w:RW, h:RH, rectRadius:0.06, fill:{ type:'none' }, line:{ color:GOLD, width:1.5 } });
// 입력창에 설계 요청(예시)
const ix = RX+981/2880*RW, iw = (2499-981)/2880*RW, iy = RY+1548/1800*RH, ih = 0.17;
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:ix+0.04, y:iy, w:iw-0.3, h:ih, rectRadius:0.05, fill:{ color:'F7F8FA' }, line:{ color:'F7F8FA', width:0 } });
T(s, '월 5만 원 안에서 설계안 만들어줘', { x:ix+0.08, y:iy, w:iw-0.3, h:ih, fontSize:9, color:'222222', bold:false });
// 단계 표시(①②③)
const pill = (n, text, x, y) => { const w=2.05, h=0.38;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius:0.19, fill:{ color:'111111' }, line:{ color:GOLD, width:1.5 } });
  s.addText([{ text:n+'  ', options:{ color:GOLD, bold:true, fontFace:FONT, fontSize:14 } }, { text, options:{ color:'FFFFFF', bold:true, fontFace:FONT, fontSize:14 } }],
    { x, y, w, h, isTextBox:true, margin:0, align:'center', valign:'middle', lang:'ko-KR' }); };
pill('①', '고객 정보 입력', RX+2.35, RY+0.2);
pill('②', '보장분석 해줘', RX+1.55, RY+1.12);
pill('③', '설계안 만들어줘', RX+1.55, RY+2.0);
T(s, '한 화면에서 · 다시 입력 없이', { x:RX, y:4.3, w:RW, h:0.36, fontSize:14, color:GOLD });

// 출처
T(s, '기존 단계: 세일즈혁신TF 영업포탈 현황 진단(2026.7) 기준 · 화면 속 이름·숫자는 예시', { x:0.3, y:4.98, w:8.6, h:0.28, fontSize:12, color:GRAY, bold:false });
pres.writeFile({ fileName: process.argv[2] || 'dream_portal_vs_meai.pptx' }).then(()=>console.log('written', process.argv[2]));
