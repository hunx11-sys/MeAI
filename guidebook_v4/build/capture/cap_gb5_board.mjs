// 게시판 글 상세: 목업 공지 본문의 '2차 오픈' 문장을 빼고 다시 찍는다(소유자 요청: '2차 오픈'이란 말은 쓰지 않음)
import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
const O='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/gb5/';
const {browser,page}=await open(ROUTES.board010,{width:1440,height:900,dsf:2});
await page.getByText('MeAI 대문 페이지 오픈 안내').first().click(); await page.waitForTimeout(1200);
const pos=async()=>await page.evaluate(()=>{ const f=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='첨부파일 1건'); const n=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='다음 글'); const r=x=>x?Math.round(x.getBoundingClientRect().y):null; return {attach:r(f), next:r(n)}; });
const before=await pos();
const removed=await page.evaluate(()=>{ const els=[...document.querySelectorAll('body *')].filter(e=>e.childElementCount===0&&e.textContent.includes('2차 오픈')); els.forEach(e=>e.remove()); return els.length; });
await page.waitForTimeout(300);
const after=await pos(); const t=await page.evaluate(()=>document.body.innerText);
await shot(page,O+'gb5_board_detail.png');
console.log(JSON.stringify({removed,before,after,still2cha:t.includes('2차')}));
await browser.close();
