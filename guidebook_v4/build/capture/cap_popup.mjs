import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
const H='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero/';
const {browser, page} = await open(ROUTES.gate010, {width:1440, height:1290, dsf:2});
await page.getByText('맞춤대화',{exact:true}).first().click(); await page.waitForTimeout(900);
const clip={x:346,y:38,width:748,height:1226};
await shot(page, H+'gate_search.png', {clip});
await page.getByPlaceholder(/이름/).first().fill('김'); await page.waitForTimeout(700);
await shot(page, H+'gate_search_kim.png', {clip});
// 페이지 번호 위치 확인
const pg = await page.evaluate(()=>{ const r=[]; document.querySelectorAll('button').forEach(b=>{ const t=b.textContent.trim(); const bb=b.getBoundingClientRect(); if(/^\d$/.test(t) && bb.y>900) r.push([t,Math.round(bb.x),Math.round(bb.y)]); }); return r; });
console.log(JSON.stringify({clip, pages:pg}));
await browser.close();
