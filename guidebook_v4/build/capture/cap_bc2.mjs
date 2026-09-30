// 방송판 v2(영업가족용) — 부담보 예시를 쓰지 않도록 MeAI 홈을 추천 세트 3(김민수·정재민·서은아)으로 넘겨 다시 찍는다.
import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
import fs from 'fs';
const H='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero/';
const out={};
{ const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
  for (let i=0;i<2;i++){ await page.getByLabel('다음 추천').first().click(); await page.waitForTimeout(700); }
  const txt = await page.evaluate(()=>document.body.innerText);
  out.hasBudambo = txt.includes('부담보'); out.first = txt.slice(txt.indexOf('오늘의 추천 고객'), txt.indexOf('오늘의 추천 고객')+80);
  await shot(page, H+'bc2_gate_full_s3.png', {fullPage:true});
  await browser.close(); }
{ // 김민수 카드 → 고객찾기(펼친 카드·오른쪽 패널)
  const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
  for (let i=0;i<2;i++){ await page.getByLabel('다음 추천').first().click(); await page.waitForTimeout(700); }
  await page.getByText('MeAI 고객찾기에서 열기').first().click(); await page.waitForTimeout(1500);
  const t = await page.evaluate(()=>document.body.innerText); out.findHasBudambo = t.includes('부담보'); out.findHasKim = t.includes('김민수');
  await shot(page, H+'bc2_find_km_full.png', {clip:{x:0,y:0,width:1440,height:900}});
  await browser.close(); }
console.log(JSON.stringify(out));
