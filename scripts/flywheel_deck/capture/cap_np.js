const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2], XL=process.argv[3];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); p.setDefaultTimeout(8000); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  const shot=(n,o)=>p.screenshot(Object.assign({path:path.join(OUT,n+'.png')},o||{}));
  await p.goto('file://'+ROOT+'/명패생성기.html'); await sleep(2500);
  await p.setInputFiles('input[type=file]', XL); await sleep(2000);
  const ev=await p.$$eval('input:not([type=file]), select',a=>a.filter(e=>e.offsetParent).map(e=>e.tagName+'#'+e.id+':'+e.placeholder+'='+e.value));
  console.log(ev);
  const t=p.locator('#eventName');
  if (await t.count()) { await t.fill('2026 고객 초청 건강 세미나'); await sleep(1200); }
  const hs=await p.evaluate(()=>[...document.querySelectorAll('h2,h3,[class*=preview],[class*=plate]')].filter(e=>e.offsetParent).slice(0,12).map(e=>e.tagName+'.'+String(e.className).slice(0,24)+'@'+Math.round(e.getBoundingClientRect().top+scrollY)));
  console.log(hs);
  await shot('np_1');
  await p.evaluate(()=>window.scrollTo(0,700)); await sleep(500); await shot('np_2');
  await p.locator('.plates').first().screenshot({path:require('path').join(OUT,'np_plates.png')});
  console.log(errs); await b.close();
})();
