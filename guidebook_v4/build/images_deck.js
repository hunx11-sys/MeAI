// 이미지판: 렌더된 슬라이드 JPG를 한 장씩 꽉 채운 pptx 로 만든다. 사용: node images_deck.js <jpg폴더> <out.pptx>
const pptxgen = require('pptxgenjs'); const fs = require('fs'); const path = require('path');
const dir = process.argv[2], out = process.argv[3];
const files = fs.readdirSync(dir).filter(f=>/^s-\d+\.jpg$/.test(f)).sort((a,b)=>parseInt(a.match(/\d+/)[0])-parseInt(b.match(/\d+/)[0]));
const pres = new pptxgen(); pres.layout='LAYOUT_WIDE'; pres.title='MeAI 활용 가이드북 v4 · MeAI 홈 편 (이미지판)';
files.forEach(f=>{ const s = pres.addSlide(); s.addImage({path:path.join(dir,f), x:0, y:0, w:13.333, h:7.5}); });
pres.writeFile({fileName:out}).then(()=>console.log('images deck', files.length, 'slides →', out));
