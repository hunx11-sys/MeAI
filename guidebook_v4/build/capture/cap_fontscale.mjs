import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
import fs from 'fs';
const D='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/v2new/';
const info={};
async function measure(page){ return await page.evaluate(()=>{ const pick=t=>{ const el=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0 && e.textContent.trim()===t); return el? parseFloat(getComputedStyle(el).fontSize):null; }; return {htmlOff: document.documentElement.classList.contains('gate-fontscale-off'), greeting: pick('내 고객 찾기'), legendTitle: pick('범례'), stored: localStorage.getItem('meai.gateFontScaleOff')}; }); }
// 대문 ON
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
  info.gate_on = await measure(page);
  await shot(page, D+'gate_on_full.png', {clip:{x:0,y:0,width:1440,height:1290}});
  await shot(page, D+'gate_on_card.png', {clip:{x:150,y:570,width:400,height:470}});
  await shot(page, D+'gate_on_top.png', {clip:{x:150,y:80,width:1140,height:460}});
  const sw = page.getByLabel('게이트 폰트 확대 토글').first();
  const bb = await sw.boundingBox(); info.switch_box = bb;
  // 스위치 확대 (dsf3 별도)
  await browser.close(); }
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:3});
  await shot(page, D+'gate_switch_z.png', {clip:{x:900,y:14,width:390,height:54}});
  await page.getByText('글씨 확대',{exact:true}).first().click().catch(async()=>{});
  await page.waitForTimeout(300);
  info.after_label_click = await measure(page);
  if (!info.after_label_click.htmlOff){ await page.locator('label:has(input[aria-label="게이트 폰트 확대 토글"])').first().click(); await page.waitForTimeout(400); }
  info.gate_off = await measure(page);
  await shot(page, D+'gate_switch_off_z.png', {clip:{x:900,y:14,width:390,height:54}});
  await browser.close(); }
// 대문 OFF (dsf2) — 토글 후 같은 위치
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
  await page.locator('label:has(input[aria-label="게이트 폰트 확대 토글"])').first().click(); await page.waitForTimeout(500);
  info.gate_off2 = await measure(page);
  await shot(page, D+'gate_off_full.png', {clip:{x:0,y:0,width:1440,height:1290}});
  await shot(page, D+'gate_off_card.png', {clip:{x:150,y:570,width:400,height:470}});
  await shot(page, D+'gate_off_top.png', {clip:{x:150,y:80,width:1140,height:460}});
  // 다시 켜 두기
  await page.locator('label:has(input[aria-label="게이트 폰트 확대 토글"])').first().click(); await page.waitForTimeout(300);
  await browser.close(); }
// 고객찾기·게시판 머리줄 스위치
{ const {browser, page} = await open(ROUTES.find010, {width:1440, height:900, dsf:3});
  await shot(page, D+'find_switch_z.png', {clip:{x:880,y:0,width:560,height:58}});
  await shot(page, D+'find_topbar_z.png', {clip:{x:0,y:0,width:1440,height:58}});
  await browser.close(); }
{ const {browser, page} = await open(ROUTES.board010, {width:1440, height:900, dsf:3});
  await shot(page, D+'board_topbar_z.png', {clip:{x:0,y:0,width:1440,height:70}});
  await browser.close(); }
fs.writeFileSync(D+'fontscale_info.json', JSON.stringify(info,null,1)); console.log(JSON.stringify(info));
