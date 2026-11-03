const { chromium } = require('playwright'); const path=require('path');
const ROOT=require('path').resolve(__dirname,'../../..'), OUT=process.argv[2];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2,reducedMotion:'reduce'});
  const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  const shot=(n,o)=>p.screenshot(Object.assign({path:path.join(OUT,n+'.png')},o||{}));
  const fresh=async(h)=>{await p.goto('file://'+ROOT+'/tool.html'+(h||'')); await sleep(2500);};
  await fresh();
  await p.fill('#q','위암'); await sleep(1500);
  let names=await p.$$eval('#results .card .pname',a=>a.map(x=>x.textContent));
  let cards=await p.$$('#results .card');
  await cards[names.indexOf('암진단비(유사암제외)')].click(); await sleep(1200);
  // 지급표 보이게 모달 본문 스크롤
  await p.evaluate(()=>{const t=document.querySelector('#modal .clause-tbl-wrap'); t&&t.scrollIntoView({block:'center'});}); await sleep(400);
  await shot('tool_modal_tbl');
  // 용어 풀이 : 밑줄 단어에 마우스
  const gl=await p.evaluate(()=>{const e=[...document.querySelectorAll('#modal .m-body *')].find(x=>getComputedStyle(x).textDecorationStyle==='dashed'||getComputedStyle(x).borderBottomStyle==='dashed'); return e? (e.className+'|'+e.tagName+'|'+e.textContent):null});
  console.log('gloss el', gl);
  // 탭 : 보장 분석
  await p.getByText('보장 분석',{exact:true}).first().click(); await sleep(800); await p.evaluate(()=>document.querySelector('#modal').scrollTo(0,0)); await shot('tool_modal_cov');
  await p.getByText('별표 · 분류표',{exact:true}).first().click(); await sleep(800); await shot('tool_modal_tab2');
  await p.keyboard.press('Escape'); await sleep(500);
  // 머리 단추들
  for (const [t,n] of [['상품 히스토리','tool_hist'],['상급종합 지도','tool_map'],['수술비 비교','tool_surg'],['표적항암 종류','tool_onco']]) {
    try { await fresh(); await p.getByText(t,{exact:true}).first().click(); await sleep(1800); await shot(n); console.log('ok',t); } catch(e){ console.log('fail',t,e.message.slice(0,100)); }
  }
  // 비교 : 두 카드 담고 비교
  await fresh(); await p.fill('#q','암진단비'); await sleep(1500);
  const cmps=await p.$$('#results .cmp-btn'); await cmps[0].click(); await sleep(300); await cmps[1].click(); await sleep(300); await cmps[2].click(); await sleep(500);
  await shot('tool_cmpbar'); await p.click('#cmpGo'); await sleep(1500); await shot('tool_cmp');
  // 보상시뮬레이터
  await fresh('#sim'); await sleep(1500); await shot('sim_home');
  console.log('frames', p.frames().map(f=>f.url().slice(-60)));
  console.log(errs);
  await b.close();
})();
