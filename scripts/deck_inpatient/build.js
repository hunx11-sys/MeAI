const L = require('./lib');
(async()=>{
  const N = 40; const pg = { n: 4 };
  const pres = L.makePres();
  require('./parts/p0')(pres, L, N);
  require('./parts/p1')(pres, L, N, pg);
  require('./parts/p2')(pres, L, N, pg);
  require('./parts/p3')(pres, L, N, pg);
  require('./parts/p4')(pres, L, N, pg);
  require('./parts/p5')(pres, L, N, pg);
  require('./parts/p6')(pres, L, N, pg);
  console.log('slides numbered through', pg.n-1);
  await pres.writeFile({ fileName: '../../dist/inpatient_adequacy_lecture.pptx' });
  await L.applyTheme('../../dist/inpatient_adequacy_lecture.pptx', L.THEME);
  console.log('written');
})().catch(e=>{ console.error(e); process.exit(1); });
