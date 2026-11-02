const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); p.setDefaultTimeout(8000); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  const shot=(n,o)=>p.screenshot(Object.assign({path:path.join(OUT,n+'.png')},o||{}));
  await p.goto('file://'+ROOT+'/products.html'); await sleep(2500);
  // 상품 카드 하나 펼치기
  await p.locator('text=M-Basket').first().click(); await sleep(1000);
  await p.evaluate(()=>window.scrollTo(0,560)); await sleep(400); await shot('pr_card');
  await p.locator('[role=tab]:visible, button:visible',{hasText:'알릴의무 유형별'}).first().click(); await sleep(1200);
  await p.evaluate(()=>window.scrollTo(0,0)); await shot('pr_notice');
  await p.locator('[role=tab]:visible, button:visible',{hasText:'예외질환 판정'}).first().click(); await sleep(1200);
  await p.evaluate(()=>window.scrollTo(0,0)); await shot('pr_ex0');
  const ui=await p.evaluate(()=>[...document.querySelectorAll('input,select,button')].filter(e=>e.offsetParent&&e.getBoundingClientRect().top+scrollY>200).slice(0,40).map(e=>e.tagName+'#'+e.id+'.'+String(e.className).slice(0,20)+':'+(e.placeholder||e.textContent.trim().replace(/\s+/g,' ').slice(0,24))+'@'+Math.round(e.getBoundingClientRect().top+scrollY)));
  console.log(ui.join('\n'));
  console.log(errs); await b.close();
})();
