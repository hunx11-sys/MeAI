const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); p.setDefaultTimeout(8000);
  await p.goto('file://'+ROOT+'/index.html'); await sleep(2500);
  // 스크롤 올라오기 숨김 풀기
  await p.evaluate(()=>{document.documentElement.classList.remove('mu-js'); document.querySelectorAll('.mu-rv').forEach(e=>e.classList.remove('mu-rv'));});
  await p.screenshot({path:path.join(OUT,'idx_hero.png')});
  const hs=await p.evaluate(()=>[...document.querySelectorAll('h2')].map(e=>[e.textContent.trim().replace(/\s+/g,' ').slice(0,24),Math.round(e.getBoundingClientRect().top+scrollY)]));
  console.log(JSON.stringify(hs));
  let k=1; for(const [t,y] of hs){ await p.evaluate(v=>window.scrollTo(0,v),y-140); await sleep(700); await p.screenshot({path:path.join(OUT,'idx_s'+(k++)+'.png')}); }
  await b.close();
})();
