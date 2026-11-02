const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
// 화면 구조 시연용 가상 로그(가정값) : 정해진 씨앗으로 만든 숫자
let a=20261102; const rnd=()=>{a=(a*1103515245+12345)&0x7fffffff; return a/0x7fffffff;};
const W={search:.34,simulator:.18,products:.14,prompts:.13,care:.12,nameplate:.03,home:.06};
const EV=['open','search','rider','disease','click','copy','view'];
function rows(since,until){ const out=[]; for(let t=+since;t<+until;t+=3600e3){ const d=new Date(t); const h=d.getHours(), wd=d.getDay(); let base=(wd===0||wd===6)?0.3:1; base*= (h>=9&&h<=18)?(h>=13&&h<=15?5:3.2):(h>=7&&h<=21?0.8:0.05); const n=Math.round(base*(1+rnd())*1.6); for(let i=0;i<n;i++){ let r=rnd(),acc=0,tool='home'; for(const k in W){acc+=W[k]; if(r<acc){tool=k;break;}} out.push({created_at:new Date(t+rnd()*3600e3).toISOString(),tool,event:EV[Math.floor(rnd()*EV.length)],term:null,rider_name:null,disease:null}); } } return out.sort((x,y)=>y.created_at<x.created_at?-1:1); }
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); p.setDefaultTimeout(8000); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.route(/rest\/v1\/usage_logs/, async route=>{
    const u=new URL(route.request().url()); const h=route.request().headers();
    const from=+((h['range']||'0-999').split('-')[0]);
    const g=(u.searchParams.getAll('created_at'));
    let since=new Date(Date.now()-400*864e5), until=new Date();
    g.forEach(x=>{ if(x.startsWith('gte.')) since=new Date(x.slice(4)); if(x.startsWith('lt.')) until=new Date(x.slice(3)); });
    const all=from===0?rows(since,until):[];
    route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(all)});
  });
  await p.goto('file://'+ROOT+'/stats.html'); await sleep(4000);
  await p.screenshot({path:path.join(OUT,'stats_1.png')});
  await p.evaluate(()=>window.scrollTo(0,700)); await sleep(800); await p.screenshot({path:path.join(OUT,'stats_2.png')});
  await p.evaluate(()=>window.scrollTo(0,1450)); await sleep(800); await p.screenshot({path:path.join(OUT,'stats_3.png')});
  console.log(errs); await b.close();
})();
