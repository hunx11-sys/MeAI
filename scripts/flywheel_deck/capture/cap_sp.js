const { chromium } = require('playwright'); const path=require('path');
const [,,FILE,OUT,PFX,SEL]=process.argv;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:+(process.env.VW||1000),height:1400},deviceScaleFactor:2});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file://'+FILE); await p.evaluate(()=>document.fonts.ready); await sleep(1500);
  const pages=await p.$$(SEL||'.page'); console.log('pages',pages.length);
  for(let i=0;i<pages.length;i++){ await pages[i].screenshot({path:path.join(OUT,PFX+String(i+1).padStart(2,'0')+'.png')}); }
  console.log(errs); await b.close();
})();
