import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
const H='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero/';
const HIDE = `button[aria-label="이전 추천"], button[aria-label="다음 추천"] { visibility:hidden !important; }`;
async function cardBox(page){
  return await page.evaluate(()=>{
    const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0 && e.textContent.trim()==='최수영');
    let el=t; for (let i=0;i<8 && el;i++){ const cs=getComputedStyle(el); if (parseFloat(cs.borderTopWidth)>0 && el.getBoundingClientRect().width>300) break; el=el.parentElement; }
    const r=el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};
  });
}
for (const mode of ['on','off']){
  const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
  await page.addStyleTag({content:HIDE});
  if (mode==='off'){ await page.locator('label:has(input[aria-label="게이트 폰트 확대 토글"])').first().click(); await page.waitForTimeout(500); }
  const b = await cardBox(page); console.log(mode, JSON.stringify(b));
  const pad=14; await shot(page, H+`v2_font_${mode}_card.png`, {clip:{x:b.x-pad, y:b.y-pad-44, width:b.w+pad*2, height:b.h+pad*2+44}});
  await browser.close();
}
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:3});
  await shot(page, H+'v2_switch_on_z.png', {clip:{x:900,y:14,width:390,height:54}});
  await page.locator('label:has(input[aria-label="게이트 폰트 확대 토글"])').first().click(); await page.waitForTimeout(400);
  await shot(page, H+'v2_switch_off_z.png', {clip:{x:900,y:14,width:390,height:54}});
  await page.locator('label:has(input[aria-label="게이트 폰트 확대 토글"])').first().click(); await page.waitForTimeout(300);
  await browser.close(); }
console.log('ok');
