const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); p.setDefaultTimeout(8000);
  const shot=(n,o)=>p.screenshot(Object.assign({path:path.join(OUT,n+'.png')},o||{}));
  await p.goto('file://'+ROOT+'/prompts.html'); await sleep(2500);
  const stages=['고객발굴/CRM선정','고객터치(전화,판촉)','초회면담/방문','보장분석/리모델링','가입제안/클로징/거절처리','사후관리/소개요청'];
  for (let i=0;i<stages.length;i++){
    await p.locator('#filter-stage .chip',{hasText:stages[i]}).first().click(); await sleep(900);
    const n=await p.evaluate(()=>document.querySelectorAll('.card').length);
    const first=await p.evaluate(()=>[...document.querySelectorAll('.card .card-text')].slice(0,3).map(e=>e.textContent.trim().slice(0,60)));
    console.log(stages[i], n, JSON.stringify(first));
    await p.evaluate(()=>window.scrollTo(0,150)); await sleep(300);
    await shot('pm_s'+(i+1));
  }
  await p.locator('#filter-stage .chip',{hasText:'사후관리/소개요청'}).first().click(); await sleep(600);
  await p.locator('.card').first().click(); await sleep(1000); await shot('pm_modal');
  await b.close();
})();
