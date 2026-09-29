// 방송판 통이미지판: 렌더된 JPG 를 한 장씩 꽉 채우고, 발표자 노트(대본)를 그대로 붙인다.
// 사용: node images_deck_notes.js <jpg폴더> <notes.json> <out.pptx>
const pptxgen = require('pptxgenjs'); const fs = require('fs'); const path = require('path');
const [dir, notesFile, out] = process.argv.slice(2);
const notes = JSON.parse(fs.readFileSync(notesFile,'utf8'));
const files = fs.readdirSync(dir).filter(f=>/^s-\d+\.jpg$/.test(f)).sort((a,b)=>parseInt(a.match(/\d+/)[0])-parseInt(b.match(/\d+/)[0]));
if (files.length!==notes.length) { console.error('장 수와 노트 수가 다름', files.length, notes.length); process.exit(1); }
const pres = new pptxgen(); pres.layout='LAYOUT_WIDE'; pres.title='MeAI 대문 30분 방송 (이미지판)'; pres.author='세일즈혁신TF';
files.forEach((f,i)=>{ const s = pres.addSlide(); s.addImage({path:path.join(dir,f), x:0, y:0, w:13.333, h:7.5}); s.addNotes(notes[i]); });
pres.writeFile({fileName:out}).then(()=>console.log('images deck', files.length, 'slides + notes →', out));
