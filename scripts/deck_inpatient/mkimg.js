const pptxgen = require('pptxgenjs'); const fs=require('fs');
const pres = new pptxgen(); pres.layout='LAYOUT_WIDE'; pres.title='입원적정성 교안(그림판)'; pres.author='세일즈혁신';
const files = fs.readdirSync('png').filter(f=>f.endsWith('.png')).sort();
files.forEach((f,i)=>{ const s=pres.addSlide(); s.addImage({ path:'png/'+f, x:0, y:0, w:13.333, h:7.5 }); });
pres.writeFile({ fileName:'inpatient_adequacy_lecture_img.pptx' }).then(()=>console.log('img deck', files.length));
