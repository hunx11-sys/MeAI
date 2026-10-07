// 메리츠드림 MeAI 장: 'AI 설계' 장면 — 맞춤대화 입력창에 설계 요청 문장을 넣은 모습(답은 만들지 않음)
// CAP_LIB=<캡처 도구 cap.mjs 경로> node cap_design.mjs <저장 폴더>   → <저장 폴더>/design_full.png (= captures/hero/dream_design_full.png)
const { open, shot, ROUTES } = await import(process.env.CAP_LIB);
const O=(process.argv[2]||'.')+'/';
const Q='암 치료비 중심으로, 월 보험료 5만 원 안에서 설계안 만들어줘';
const out={};
const {browser,page}=await open(ROUTES.find010,{width:1440,height:900,dsf:2});
await page.locator('[role=button]',{hasText:'맞춤대화'}).first().click(); await page.waitForTimeout(1600);
out.route=decodeURIComponent(page.url().split('#')[1]);
out.replaced=await page.evaluate(()=>{ let n=0; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let x; while((x=w.nextNode())){ if(x.nodeValue.includes('정메리')){ x.nodeValue=x.nodeValue.replaceAll('정메리','김도윤'); n++; } } return n; });
const ta=page.locator('textarea').first(); out.ta=await ta.count();
await ta.fill(Q); await page.waitForTimeout(400);
out.box=await ta.boundingBox();
await shot(page,O+'design_full.png');
await browser.close();
console.log(JSON.stringify(out));
