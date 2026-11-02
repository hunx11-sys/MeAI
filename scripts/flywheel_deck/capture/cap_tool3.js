const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  p.setDefaultTimeout(8000);
  const shot=(n,o)=>p.screenshot(Object.assign({path:path.join(OUT,n+'.png')},o||{}));
  const fresh=async(h)=>{await p.goto('file://'+ROOT+'/tool.html'+(h||'')); await sleep(2500);};
  const step=async(n,f)=>{try{await f();console.log('ok',n);}catch(e){console.log('FAIL',n,e.message.split('\n')[0]);}};
  await step('gloss',async()=>{
    await fresh(); await p.fill('#q','위암'); await sleep(1500);
    const names=await p.$$eval('#results .card .pname',a=>a.map(x=>x.textContent));
    const cards=await p.$$('#results .card'); await cards[names.indexOf('암진단비(유사암제외)')].click(); await sleep(1200);
    const g=p.locator('#modal .m-body .mg-t',{hasText:'보장개시일'}).first();
    await g.hover(); await sleep(800); await shot('tool_gloss');
    await p.keyboard.press('Escape'); await sleep(400);
  });
  for (const [sel,n] of [['#histBtn','tool_hist'],['#mapBtn','tool_map'],['.sc-btn','tool_surg'],['#oncoBtn','tool_onco']]) {
    await step(n,async()=>{await fresh(); await p.click(sel); await sleep(2000); await shot(n);});
  }
  await step('cmp',async()=>{
    await fresh(); await p.fill('#q','암진단비'); await sleep(1500);
    await p.evaluate(()=>{const c=[...document.querySelectorAll('#results .cmp-btn')]; c.slice(0,3).forEach(x=>x.click());}); await sleep(800);
    await shot('tool_cmpbar'); await p.evaluate(()=>document.querySelector('#cmpGo').click()); await sleep(1500); await shot('tool_cmp');
  });
  await step('sim',async()=>{await fresh('#sim'); await sleep(1500); await shot('sim_home'); console.log(p.frames().map(f=>f.url().slice(-50)));});
  console.log(errs);
  await b.close();
})();
