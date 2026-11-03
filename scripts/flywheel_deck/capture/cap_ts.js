const { chromium } = require('playwright'); const path=require('path');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{ const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'}); const p=await ctx.newPage();
 await p.goto('file://'+require('path').resolve(__dirname,'../../../tool.html')); await sleep(2500); await p.fill('#q','위암'); await sleep(1500);
 await p.keyboard.press('Escape'); await p.mouse.click(1380,600); await sleep(600);
 const vis=await p.evaluate(()=>{const s=document.querySelector('#sug'); return s?getComputedStyle(s).display+'/'+s.offsetHeight:'none'}); console.log('sug',vis);
 await p.evaluate(()=>scrollTo(0,0)); await sleep(300); await p.screenshot({path:path.join(process.argv[2],'tool_search.png')}); await b.close(); })();
