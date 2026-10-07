// 메리츠드림 MeAI 장 덧붙임 — '기존 영업포탈 12단계 vs MeAI 두 화면'(WOW 비교 장)
// 왼쪽: 영업포탈 실제 화면 5장을 어둡게 겹쳐 쌓고, 그 위를 12개 단계가 이리저리 오감(메뉴 5곳 · 정보 다시 입력)
// 오른쪽: MeAI 홈(①고객 등록 = [고객 동의] 휴대폰번호 · ②고객 조회 = [맞춤대화] → 고객 검색 창) → 맞춤대화(③보장분석 ④설계 ⑤리포트) — 금빛
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
  + 'MeAI는 두 화면입니다. MeAI 홈의 [고객 동의]에 휴대폰 번호를 넣으면 사전조회동의 알림톡이 가고, 고객이 동의하면 신규 등록 고객으로 들어옵니다. [맞춤대화]를 누르면 뜨는 고객 검색 창에서 이름으로 고객을 찾아 고릅니다. '
  + '맞춤대화가 열리면 "이 고객 보험 어디가 부족한지 알려줘" 한마디(또는 [보장 분석] 버튼)로 보장분석, "암 치료비 중심으로, 월 보험료 5만 원 안에서 설계안 만들어줘"로 설계, 그리고 [요약 리포트]로 고객에게 보낼 리포트까지 만듭니다. 고객 등록부터 리포트까지, 두 화면이면 됩니다. '
  + '(참고 — 기존 12단계: 고객 등록 3 · 보장 확인 4 · 설계 5, 세일즈혁신TF 영업포탈 현황 진단 기준. 신규 등록 고객의 상세 정보는 다음 날 반영. 설계는 맞춤대화에 요청하는 장면이며 설계안 답 화면은 목업에 없어 넣지 않음.)');
// 제목(행사 PPT 에 끼울 때 원래 제목 자리로 바뀜)
T(s, '고객 등록부터 리포트까지, MeAI 두 화면으로', { x:0.27, y:0.12, w:9.45, h:0.55, fontSize:28, objectName:'TITLE_PREVIEW' });

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
const nodes = [[0.62,1.80],[0.72,2.42],[1.12,2.10], [1.86,1.70],[2.38,2.00],[3.08,1.78],[3.86,2.08], [1.05,3.00],[1.62,3.36],[2.52,3.00],[3.22,3.40],[3.96,3.08]];
for (let i=0;i<nodes.length-1;i++){ const [x1,y1]=nodes[i], [x2,y2]=nodes[i+1];
  s.addShape(pres.shapes.LINE, { x:Math.min(x1,x2), y:Math.min(y1,y2), w:Math.abs(x2-x1)||0.001, h:Math.abs(y2-y1)||0.001,
    flipV:(x2<x1)!==(y2<y1), line:{ color:'D9D9D9', width:2.25 } }); }
nodes.forEach(([x,y],i)=>{ const d=0.3;
  s.addShape(pres.shapes.OVAL, { x:x-d/2, y:y-d/2, w:d, h:d, fill:{ color:'4D4D4D' }, line:{ color:'BFBFBF', width:1 } });
  T(s, String(i+1), { x:x-d/2, y:y-d/2, w:d, h:d, fontFace:LATIN, fontSize:10, align:'center', color:'FFFFFF' }); });
T(s, '메뉴 5곳을 오가며 · 고객정보 다시 입력', { x:LX, y:4.62, w:LR-LX, h:0.36, fontSize:14, color:MUTE });

// ── 가운데 화살표 ───────────────────────────────────
{ const d=0.38, cx=4.8, cy=3.40; s.addShape(pres.shapes.OVAL, { x:cx-d/2, y:cy-d/2, w:d, h:d, fill:{ color:GOLD }, line:{ color:'000000', width:2 } });
  T(s, '›', { x:cx-d/2, y:cy-d/2-0.03, w:d, h:d, fontSize:22, color:'000000', align:'center' }); }

// ── 오른쪽: MeAI 두 화면(홈 → 맞춤대화) ─────────────
const AX = 5.05, AY = 1.33, AW = 3.15, AH = AW*1450/2340;          // MeAI 홈(위쪽) — meai_home_top.png 2340x1450
const BX = 6.55, BY = 2.55, BW = 3.15, BH = BW*1800/2880;          // 맞춤대화 — meai_one_screen.png 2880x1800
const MX = 8.33, MY = 1.36, MW = 1.32, MH = MW*484/960;            // '고객 동의' 창
const SX = MX, SW = MW, SH = SW*360/1440, SY = 2.11;               // [맞춤대화] → '고객 검색' 창
const a2s = (px,py)=>[AX+px/2340*AW, AY+py/1450*AH], b2s = (px,py)=>[BX+px/2880*BW, BY+py/1800*BH];
s.addImage({ path:P('glow_wide.png'), x:AX-1.0, y:AY-0.9, w:9.75-AX+2.0, h:BY+BH-AY+1.8, altText:'배경 빛' });
s.addText([{ text:'MeAI', options:{ fontFace:LATIN, bold:true, color:GOLD, fontSize:16 } }], { x:AX, y:0.84, w:2.0, h:0.42, isTextBox:true, margin:0, valign:'middle' });
T(s, '두 화면', { x:9.7-2.6, y:0.8, w:2.6, h:0.5, fontSize:28, color:GOLD, align:'right' });
s.addImage({ path:P('meai_home_top.png'), x:AX, y:AY, w:AW, h:AH, altText:'MeAI 홈 화면' });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:AX, y:AY, w:AW, h:AH, rectRadius:0.06, fill:{ type:'none' }, line:{ color:GOLD, width:1, transparency:30 } });
// 홈의 [맞춤대화] 카드 → 고객 검색 창 → 맞춤대화 화면
{ const [x1,y1]=a2s(1185,399), [x2,y2]=a2s(2289,660);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x1-0.03, y:y1-0.03, w:x2-x1+0.06, h:y2-y1+0.06, rectRadius:0.04, fill:{ type:'none' }, line:{ color:GOLD, width:2 } });
  s.addShape(pres.shapes.LINE, { x:x2+0.03, y:(y1+y2)/2, w:SX-(x2+0.03), h:SY+SH/2-(y1+y2)/2, line:{ color:GOLD, width:1.5 } }); }
s.addImage({ path:P('meai_search_popup.png'), x:SX, y:SY, w:SW, h:SH, altText:'고객 검색 창(이름으로 찾기)' });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:SX, y:SY, w:SW, h:SH, rectRadius:0.05, fill:{ type:'none' }, line:{ color:GOLD, width:1.25 } });
{ const ax=SX+SW/2; s.addShape(pres.shapes.LINE, { x:ax, y:SY+SH+0.01, w:0.001, h:BY-(SY+SH+0.01)-0.01, line:{ color:GOLD, width:2.5, endArrowType:'triangle' } }); }
s.addImage({ path:P('meai_one_screen.png'), x:BX, y:BY, w:BW, h:BH, altText:'MeAI 맞춤대화 화면' });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:BX, y:BY, w:BW, h:BH, rectRadius:0.06, fill:{ type:'none' }, line:{ color:GOLD, width:1.5 } });
// [고객 동의] 버튼 → 휴대폰번호 창
{ const [x1,y1]=a2s(1884,51), [x2,y2]=a2s(2091,111);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x1-0.02, y:y1-0.02, w:x2-x1+0.04, h:y2-y1+0.04, rectRadius:0.03, fill:{ type:'none' }, line:{ color:GOLD, width:1.75 } });
  s.addShape(pres.shapes.LINE, { x:x2+0.02, y:(y1+y2)/2, w:MX-(x2+0.02), h:MY+0.25-(y1+y2)/2, line:{ color:GOLD, width:1.5 } }); }
s.addImage({ path:P('meai_consent_modal.png'), x:MX, y:MY, w:MW, h:MH, altText:'고객 동의 창(휴대폰번호 입력)' });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:MX, y:MY, w:MW, h:MH, rectRadius:0.06, fill:{ type:'none' }, line:{ color:GOLD, width:1.25 } });
// 번호 표시(화면 위) + 목록(왼쪽 아래 빈 곳)
const badge = (n, cx, cy) => { const d=0.3;
  s.addShape(pres.shapes.OVAL, { x:cx-d/2, y:cy-d/2, w:d, h:d, fill:{ color:GOLD }, line:{ color:'000000', width:1.5 } });
  T(s, n, { x:cx-d/2, y:cy-d/2, w:d, h:d, fontSize:12, color:'000000', align:'center' }); };
badge('1', MX-0.09, MY+0.07);
badge('2', SX-0.09, SY+0.06);
{ const [x,y]=b2s(981,640); badge('3', x-0.17, y); }
{ const [x,y]=b2s(981,1597); badge('4', x-0.17, y); }
{ const [x,y]=b2s(2732,84); badge('5', x, y+0.17); }
[['1','고객 등록'],['2','고객 조회'],['3','MeAI 보장분석'],['4','MeAI 설계'],['5','MeAI 리포트']].forEach(([n,t],i)=>{ const y=3.44+i*0.215, d=0.19;
  s.addShape(pres.shapes.OVAL, { x:AX+0.02, y:y+0.015, w:d, h:d, fill:{ color:GOLD }, line:{ color:GOLD, width:0 } });
  T(s, n, { x:AX+0.02, y:y+0.015, w:d, h:d, fontSize:9, color:'000000', align:'center' });
  T(s, t, { x:AX+0.26, y, w:BX-AX-0.28, h:0.22, fontSize:12, color:'FFFFFF' }); });
T(s, 'MeAI 홈 → 맞춤대화 · 다시 입력 없이', { x:AX, y:4.62, w:9.7-AX, h:0.36, fontSize:14, color:GOLD });

// 출처
T(s, '기존 단계: 세일즈혁신TF 영업포탈 현황 진단(2026.7) 기준 · 화면 속 이름·숫자는 예시', { x:0.3, y:5.04, w:8.6, h:0.28, fontSize:12, color:GRAY, bold:false });
pres.writeFile({ fileName: process.argv[2] || 'dream_portal_vs_meai.pptx' }).then(()=>console.log('written', process.argv[2]));
