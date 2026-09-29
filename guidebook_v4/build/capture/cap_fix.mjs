import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
const H='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero/';
const NOARROW = `html.noarrow button[aria-label="이전 추천"], html.noarrow button[aria-label="다음 추천"] { visibility:hidden !important; }`;
const hide = p => p.evaluate(()=>document.documentElement.classList.add('noarrow'));
const show = p => p.evaluate(()=>document.documentElement.classList.remove('noarrow'));
const out={};
// 1) 추천 카드 세트 1~3 (화살표 숨김) — 원래 clip 그대로
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
  await page.addStyleTag({content:NOARROW}); await hide(page); await page.waitForTimeout(200);
  await shot(page, H+'gate_reco1.png', {clip:{x:150,y:580,width:1140,height:460}});
  for (const n of [2,3]){ await show(page); await page.getByLabel('다음 추천').first().click(); await page.waitForTimeout(700);
    await hide(page); await page.waitForTimeout(150);
    await shot(page, H+`gate_reco${n}.png`, {clip:{x:150,y:580,width:1140,height:460}}); }
  await browser.close(); }
// 2) 대문 카드 확대(화살표 숨김) — gate_card_z 와 같은 clip
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:3});
  await page.addStyleTag({content:NOARROW}); await hide(page); await page.waitForTimeout(200);
  await shot(page, H+'gate_card_z.png', {clip:{x:150,y:625,width:382,height:385}});
  await browser.close(); }
// 3) 고객 검색 팝업: 팝업 상자 전체(페이지 번호까지), 뒤 화면 스위치 제외
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
  await page.getByText('맞춤대화',{exact:true}).first().click(); await page.waitForTimeout(900);
  const box = await page.evaluate(()=>{ const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0 && e.textContent.trim()==='고객 검색'); let el=t; for(let i=0;i<12&&el;i++){ const r=el.getBoundingClientRect(); if(r.width>500 && r.height>500) return {x:r.x,y:r.y,w:r.width,h:r.height}; el=el.parentElement;} return null; });
  out.popup=box;
  const pad=14; const clip={x:Math.round(box.x-pad), y:Math.round(box.y-pad), width:Math.round(box.w+pad*2), height:Math.round(box.h+pad*2)};
  out.popup_clip=clip;
  await shot(page, H+'gate_search.png', {clip});
  await page.getByPlaceholder(/이름/).first().fill('김'); await page.waitForTimeout(700);
  const box2 = await page.evaluate(()=>{ const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0 && e.textContent.trim()==='고객 검색'); let el=t; for(let i=0;i<12&&el;i++){ const r=el.getBoundingClientRect(); if(r.width>500 && r.height>400) return {x:r.x,y:r.y,w:r.width,h:r.height}; el=el.parentElement;} return null; });
  out.popup_kim=box2;
  await shot(page, H+'gate_search_kim.png', {clip:{x:clip.x,y:clip.y,width:clip.width,height:Math.round(box2.h+pad*2)}});
  await browser.close(); }
// 4) 게시판 윗줄
{ const {browser, page} = await open(ROUTES.board010, {width:1440, height:900, dsf:3});
  await shot(page, H+'v2_board_topbar_z.png', {clip:{x:0,y:0,width:1440,height:64}});
  await browser.close(); }
console.log(JSON.stringify(out));
