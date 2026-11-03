const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); p.setDefaultTimeout(15000); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  const shot=(n,o)=>p.screenshot(Object.assign({path:path.join(OUT,n+'.png')},o||{}));
  await p.goto('file://'+ROOT+'/docs/guidebook_proto.html'); await sleep(2500);
  await p.click('#sampleA'); await sleep(6000);
  await shot('gb_app');
  const pages=await p.$$('.page'); console.log('pages',pages.length);
  for(let i=0;i<pages.length;i++){ await pages[i].scrollIntoViewIfNeeded(); await sleep(150); await pages[i].screenshot({path:path.join(OUT,'gb_p'+String(i+1).padStart(2,'0')+'.png')}); }
  const cand=await p.evaluate(()=>{const m={}; document.querySelectorAll('[class]').forEach(e=>{const c=String(e.className).split(' ')[0]; const r=e.getBoundingClientRect(); if(r.width>500&&r.height>600){m[c]=(m[c]||0)+1;}}); return m;});
  console.log(JSON.stringify(cand));
  console.log(errs); await b.close();
})();
