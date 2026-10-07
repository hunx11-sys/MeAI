// 메리츠드림 MeAI 장 덧붙임 1장 — "타사는 임직원을 위한 AI 개발에 집중할 때, 메리츠는 영업가족을 위한 AI를 개발했다"(소유자 문장)
// 왼쪽(타사)은 어둡게, 오른쪽(메리츠)은 금빛으로 — 한눈에 대비. 행사 PPT 톤(검정 · 금색 · 맑은 고딕), 애니메이션 없음.
// node dream_contrast.js out.pptx [재료폴더]   (재료 = assets.py 의 glow_wide.png)
const pptxgen = require('pptxgenjs'); const path = require('path');
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server'); const sharp = require('sharp');
const { LuBuilding2, LuUsers } = require('react-icons/lu');
const A = process.argv[3] || path.join(__dirname, 'assets');
const FONT = '맑은 고딕', GOLD = 'FFC000', MUTE = '8C8C8C', MUTE2 = 'A6A6A6', CARD = '111111';
const run = (text, o={}) => ({ text, options:Object.assign({ fontFace:FONT, color:'FFFFFF', bold:true, lang:'ko-KR' }, o) });
async function icon(C, color){ const svg = renderToStaticMarkup(React.createElement(C, { size:512, color:'#'+color, strokeWidth:1.6 }));
  return 'image/png;base64,' + (await sharp(Buffer.from(svg)).png().toBuffer()).toString('base64'); }
(async()=>{
  const pres = new pptxgen(); pres.layout = 'LAYOUT_16x9'; pres.title = '메리츠드림 · MeAI';
  const s = pres.addSlide(); s.background = { color:'000000' };
  s.addNotes('다른 회사들이 임직원을 위한 AI 개발에 집중할 때, 메리츠는 영업가족을 위한 AI를 개발했습니다. 현장에서 고객을 만나는 여러분을 위한 AI, 그것이 MeAI입니다.');
  const cw = 4.45, ch = 3.85, cy = 0.88, lx = 0.4, rx = 10-0.4-cw;
  // 오른쪽 뒤 금빛(메리츠 쪽만 빛나게)
  s.addImage({ path:path.join(A,'glow_wide.png'), x:rx-1.5, y:cy-1.0, w:cw+3.0, h:ch+2.0, altText:'배경 빛' });
  // 왼쪽 — 타사
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:lx, y:cy, w:cw, h:ch, rectRadius:0.1, fill:{ color:CARD }, line:{ color:'333333', width:0.75 } });
  s.addText([ run('타사는', { fontSize:20, color:MUTE }) ], { x:lx, y:cy+0.35, w:cw, h:0.4, isTextBox:true, margin:0, align:'center', valign:'middle' });
  s.addImage({ data:await icon(LuBuilding2,'6B6B6B'), x:lx+cw/2-0.55, y:cy+0.9, w:1.1, h:1.1, altText:'건물(임직원)' });
  s.addText([ run('임직원을 위한 AI', { fontSize:28, color:MUTE2, breakLine:true }), run('개발에 집중할 때', { fontSize:20, color:MUTE }) ],
    { x:lx+0.1, y:cy+2.2, w:cw-0.2, h:1.25, isTextBox:true, margin:0, align:'center', valign:'middle', lineSpacingMultiple:1.25 });
  // 오른쪽 — 메리츠
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:rx, y:cy, w:cw, h:ch, rectRadius:0.1, fill:{ color:'141414' }, line:{ color:GOLD, width:1.5 } });
  s.addText([ run('메리츠는', { fontSize:20, color:GOLD }) ], { x:rx, y:cy+0.35, w:cw, h:0.4, isTextBox:true, margin:0, align:'center', valign:'middle' });
  s.addImage({ data:await icon(LuUsers, GOLD), x:rx+cw/2-0.55, y:cy+0.9, w:1.1, h:1.1, altText:'사람들(영업가족)' });
  s.addText([ run('영업가족을 위한 AI를', { fontSize:28, color:GOLD, breakLine:true }), run('개발했습니다', { fontSize:20 }) ],
    { x:rx+0.1, y:cy+2.2, w:cw-0.2, h:1.25, isTextBox:true, margin:0, align:'center', valign:'middle', lineSpacingMultiple:1.25 });
  // 가운데 — 방향 표시
  const d = 0.42, mx = 5 - d/2, my = cy + ch/2 - d/2;
  s.addShape(pres.shapes.OVAL, { x:mx, y:my, w:d, h:d, fill:{ color:GOLD }, line:{ color:'000000', width:2 } });
  s.addText('›', { x:mx, y:my-0.03, w:d, h:d, fontFace:FONT, lang:'ko-KR', fontSize:22, bold:true, color:'000000', align:'center', valign:'middle', margin:0, isTextBox:true });
  await pres.writeFile({ fileName: process.argv[2] || 'dream_contrast.pptx' }); console.log('written', process.argv[2]);
})();
