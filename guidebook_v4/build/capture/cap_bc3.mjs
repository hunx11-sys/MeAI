// 방송판 v3 — 일반대화·맞춤대화 화면 설명 장(12~14장)용 캡처. 목업 v2, 1440×900, dsf 2.
import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
const H='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero/';
const out={};
const txt=async p=>(await p.evaluate(()=>document.body.innerText));
{ // 일반대화 첫 화면: MeAI 홈 [일반대화] 카드를 눌러 들어온 화면
  const {browser,page}=await open(ROUTES.gate010,{width:1440,height:900,dsf:2});
  await page.getByText('일반대화',{exact:true}).first().click(); await page.waitForTimeout(1500);
  out.generalRoute=decodeURIComponent(page.url().split('#')[1]); const t=await txt(page); out.generalHasBudambo=t.includes('부담보');
  await shot(page,H+'bc3_general_home.png');
  await page.getByText('MeAI 홈',{exact:true}).first().click(); await page.waitForTimeout(1000); out.homeButtonRoute=page.url().split('#')[1];
  await browser.close(); }
{ // 맞춤대화 화면: 고객찾기 오른쪽 맞춤대화 추천 질문을 눌러 들어온 김도윤 화면
  const {browser,page}=await open(ROUTES.find010,{width:1440,height:900,dsf:2});
  await page.locator('[role=button]',{hasText:'맞춤대화'}).first().click(); await page.waitForTimeout(1600);
  out.customRoute=decodeURIComponent(page.url().split('#')[1]);
  // 목업 고정 안내문 속 예시 이름(정메리)을 왼쪽 담당 고객(김도윤)과 맞춘다 — 실제 화면은 선택한 고객 이름이 들어간다
  out.replaced=await page.evaluate(()=>{ let n=0; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let x; while((x=w.nextNode())){ if(x.nodeValue.includes('정메리')){ x.nodeValue=x.nodeValue.replaceAll('정메리','김도윤'); n++; } } return n; });
  await page.waitForTimeout(300);
  const t=await txt(page); out.customHasBudambo=t.includes('부담보'); out.customText=t.replace(/\n+/g,' | ').slice(0,700);
  await shot(page,H+'bc3_custom_main.png');
  await browser.close(); }
console.log(JSON.stringify(out,null,1));
