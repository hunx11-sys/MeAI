import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
const H='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero/';
const info={};
// 1) 최수영 카드 → 고객찾기(펼친 카드) dsf3
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:3});
  await page.getByText('MeAI 고객찾기에서 열기').first().click(); await page.waitForTimeout(1500);
  const box = await page.evaluate(()=>{ const t=[...document.querySelectorAll('body *')].filter(e=>e.childElementCount===0 && e.textContent.trim()==='최수영'); 
    for (const n of t){ let el=n; for(let i=0;i<10&&el;i++){ const r=el.getBoundingClientRect(); const cs=getComputedStyle(el); if(r.width>500 && r.width<760 && parseFloat(cs.borderTopWidth)>0) return {x:r.x,y:r.y,w:r.width,h:r.height}; el=el.parentElement; } } return null; });
  info.card=box;
  if (box){ await shot(page, H+'bc_choi_card_z.png', {clip:{x:box.x-6,y:box.y-6,width:box.w+12,height:box.h+12}}); }
  // 한눈에 보기 여섯 칸
  const six = await page.evaluate(()=>{ const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0 && e.textContent.trim()==='가입한 보험'); let el=t; for(let i=0;i<8&&el;i++){ const r=el.getBoundingClientRect(); if(r.width>450 && r.height>100) return {x:r.x,y:r.y,w:r.width,h:r.height}; el=el.parentElement; } return null; });
  info.six=six;
  if (six) await shot(page, H+'bc_choi_six_z.png', {clip:{x:six.x-4,y:six.y-4,width:six.w+8,height:six.h+8}});
  info.url = page.url();
  await browser.close(); }
console.log(JSON.stringify(info));
