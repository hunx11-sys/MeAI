const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); p.setDefaultTimeout(8000);
  const shot=(n,o)=>p.screenshot(Object.assign({path:path.join(OUT,n+'.png')},o||{}));
  await p.goto('file://'+ROOT+'/tool.html#sim'); await sleep(3500);
  const f=p.frames().find(x=>x.url()==='about:srcdoc');
  const vis=f.locator('input:visible').first(); await vis.fill('위암'); await sleep(800); await vis.press('Enter'); await sleep(2000);
  const ifTop=await p.evaluate(()=>document.querySelector('iframe').getBoundingClientRect().top+scrollY);
  await f.evaluate(()=>document.querySelector('.stage.open .stage-head').click()); await sleep(800);
  const y=await f.evaluate(()=>document.querySelector('h2').getBoundingClientRect().top+scrollY);
  await f.evaluate(v=>window.scrollTo(0,v),y-24); await sleep(600); await shot('sim_stages');
  // 수술 단계 펼치기
  await f.evaluate(()=>{const s=[...document.querySelectorAll('.stage-head')].find(h=>h.textContent.includes('수술 시')); s.click();}); await sleep(900);
  const y2=await f.evaluate(()=>{const s=[...document.querySelectorAll('.stage-head')].find(h=>h.textContent.includes('수술 시')); return s.getBoundingClientRect().top+scrollY;});
  await f.evaluate(v=>window.scrollTo(0,v),y2-24); await sleep(600); await shot('sim_surgery');
  await b.close();
})();
