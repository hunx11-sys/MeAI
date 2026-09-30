// 가이드북 v4 영업가족판 — 부담보 예시(추천 세트 1 최수영)를 빼고 세트 3(김민수·서은아)·세트 2(박준호)로 다시 찍는다. 목업 v2.
import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
import fs from 'fs';
const O='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/gb5/';
const NOARROW=`html.noarrow button[aria-label="이전 추천"], html.noarrow button[aria-label="다음 추천"] { visibility:hidden !important; }`;
const out={};
async function toSet(page,n){ for(let i=1;i<n;i++){ await page.getByLabel('다음 추천').first().click(); await page.waitForTimeout(700); } }
async function box(page,name){ return await page.evaluate((name)=>{
  const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0 && e.textContent.trim()===name);
  if(!t) return null; let el=t; for(let i=0;i<10&&el;i++){ const cs=getComputedStyle(el); const r=el.getBoundingClientRect(); if(parseFloat(cs.borderTopWidth)>0 && r.width>300) return {x:r.x,y:r.y,w:r.width,h:r.height}; el=el.parentElement; } return null; },name); }
async function textBox(page,start){ return await page.evaluate((start)=>{ const els=[...document.querySelectorAll('body *')].filter(e=>e.childElementCount===0 && e.textContent.trim().startsWith(start)); return els.map(e=>{const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,t:e.textContent.trim().slice(0,30)};}); },start); }
// A. MeAI 홈 추천 세트 3
{ const {browser,page}=await open(ROUTES.gate010,{width:1440,height:1290,dsf:2});
  await page.addStyleTag({content:NOARROW}); await toSet(page,3);
  const t=await page.evaluate(()=>document.body.innerText); out.s3HasBudambo=t.includes('부담보');
  await shot(page,O+'gb5_gate_full.png');
  out.kim=await box(page,'김민수'); out.jae=await box(page,'정재민'); out.seo=await box(page,'서은아');
  out.jaeText=await textBox(page,'암진단비가 중복'); out.jaeText2=await textBox(page,'중복 보장을');
  out.date=await textBox(page,'최근 업데이트');
  out.dots=await page.evaluate(()=>{ const b=document.querySelector('button[aria-label="다음 추천"]'); const r=b?b.getBoundingClientRect():null; return r?{x:r.x,y:r.y,w:r.width,h:r.height}:null; });
  await page.evaluate(()=>document.documentElement.classList.add('noarrow')); await page.waitForTimeout(150);
  const bottom=Math.max(out.kim.y+out.kim.h,out.jae.y+out.jae.h,out.seo.y+out.seo.h);
  out.recoClip={x:150,y:580,width:1140,height:Math.ceil(bottom-580+60)};
  await shot(page,O+'gb5_gate_reco3.png',{clip:out.recoClip});
  await browser.close(); }
// 카드 확대(dsf 3, 화살표 숨김): 김민수·서은아(세트 3), 박준호(세트 2)
for (const [set,name,file] of [[3,'김민수','gb5_card_kim_z'],[3,'서은아','gb5_card_seo_z'],[2,'박준호','gb5_card_park_z']]){
  const {browser,page}=await open(ROUTES.gate010,{width:1440,height:1290,dsf:3});
  await page.addStyleTag({content:NOARROW}); await toSet(page,set); await page.evaluate(()=>document.documentElement.classList.add('noarrow')); await page.waitForTimeout(150);
  const b=await box(page,name); out[file]=b; const pad=10;
  await shot(page,O+file+'.png',{clip:{x:b.x-pad,y:b.y-pad,width:b.w+pad*2,height:b.h+pad*2}});
  await browser.close(); }
// 글씨 확대 ON/OFF 비교(김민수 카드, dsf 2)
for (const mode of ['on','off']){
  const {browser,page}=await open(ROUTES.gate010,{width:1440,height:1290,dsf:2});
  await page.addStyleTag({content:NOARROW}); await toSet(page,3); await page.evaluate(()=>document.documentElement.classList.add('noarrow'));
  if(mode==='off'){ await page.locator('label:has(input[aria-label="게이트 폰트 확대 토글"])').first().click(); await page.waitForTimeout(500); }
  const b=await box(page,'김민수'); out['font_'+mode]=b; const pad=14;
  await shot(page,O+`gb5_font_${mode}_card.png`,{clip:{x:b.x-pad,y:b.y-pad-44,width:b.w+pad*2,height:b.h+pad*2+44}});
  await browser.close(); }
// 고객찾기: 서은아(세트 3 셋째 카드) · 박준호(세트 2 첫 카드)
for (const [set,idx,name,tag] of [[3,2,'서은아','seo'],[2,0,'박준호','park']]){
  const {browser,page}=await open(ROUTES.gate010,{width:1440,height:900,dsf:2});
  await toSet(page,set);
  await page.getByText('MeAI 고객찾기에서 열기').nth(idx).click(); await page.waitForTimeout(1600);
  const t=await page.evaluate(()=>document.body.innerText); out['find_'+tag]={route:decodeURIComponent(page.url().split('#')[1]).slice(0,120), has:t.includes(name), budambo:t.includes('부담보')};
  await shot(page,O+`gb5_find_${tag}.png`);
  // 오른쪽 패널의 맞춤대화 추천 질문 → 맞춤대화(질문이 채워진 화면). 목업 고정 안내문 속 예시 이름을 이 고객으로 맞춘다
  const btn=page.locator('[role=button]',{hasText:'맞춤대화'}); out['find_'+tag].customBtns=await btn.count();
  if(await btn.count()){ await btn.first().click(); await page.waitForTimeout(1600);
    out['custom_'+tag]={route:decodeURIComponent(page.url().split('#')[1]).slice(0,140)};
    out['custom_'+tag].replaced=await page.evaluate((nm)=>{ let n=0; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let x; while((x=w.nextNode())){ if(x.nodeValue.includes('정메리')){ x.nodeValue=x.nodeValue.replaceAll('정메리',nm); n++; } } return n; },name);
    await page.waitForTimeout(200); await shot(page,O+`gb5_custom_${tag}.png`); }
  await browser.close(); }
fs.writeFileSync(O+'cap_gb5.json',JSON.stringify(out,null,1));
console.log(JSON.stringify(out,null,1));
