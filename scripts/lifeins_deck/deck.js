const pptxgen = require('pptxgenjs');
const L = require('./lib.js');
const parts = (process.env.PARTS ? process.env.PARTS.split(',') : ['p0_open','p1_market','p2_anatomy','p3_compare','p4_mind','p5_break','p6_solution']);
(async()=>{
  const p = new pptxgen(); p.layout = 'LAYOUT_WIDE'; p.title = '생명보험 파헤치기 2026'; p.author='메리츠화재 개인영업교육';
  L.resetPage();
  for(const name of parts){ await require('./parts/'+name+'.js')(p, L); }
  const out = process.env.OUT || 'deck.pptx';
  await p.writeFile({fileName: out});
  console.log('written', out);
})().catch(e=>{console.error(e); process.exit(1);});
