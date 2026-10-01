// 정재민 카드(추천 세트 3 둘째): 목업 원문(중복 보장 정리 권유)을 가리는 대신 같은 형식의 예시 문장으로 바꿔 다시 찍는다.
// 문장은 정재민의 그룹(G008 당월 영업 타겟: "당월 회사 전략 담보(수술비·표적항암 등) 대상 고객")에 맞춘 예시(소유자 요청 2026.10.02 "암 관련으로")
import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
import fs from 'fs';
const O='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/gb5/';
const NOARROW=`html.noarrow button[aria-label="이전 추천"], html.noarrow button[aria-label="다음 추천"] { visibility:hidden !important; }`;
const BOLD_OLD='암진단비가 중복 가입돼 있어 보험료 부담이 큽니다.';
const BOLD_NEW='암진단비는 있지만 표적항암 치료비가 비어 있습니다.';
const DESC_NEW='진단 이후 표적항암 치료가 이어지면 비급여 약제비 부담이 커지므로, 이번 달 전략 담보인 표적항암 치료비를 기존 진단비와 함께 점검해 채워 드리기 좋은 고객입니다.';
async function prep(page){
  for(let i=1;i<3;i++){ await page.getByLabel('다음 추천').first().click(); await page.waitForTimeout(700); }
  return await page.evaluate(([bo,bn,dn])=>{ let n=0; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let x; const nodes=[]; while((x=w.nextNode())) nodes.push(x);
    for(const t of nodes){ const v=t.nodeValue.trim(); if(v===bo){ t.nodeValue=bn; n++; } else if(v.startsWith('중복 보장을 정리해')){ t.nodeValue=dn; n++; } } return n; },[BOLD_OLD,BOLD_NEW,DESC_NEW]);
}
const out={};
{ const {browser,page}=await open(ROUTES.gate010,{width:1440,height:1290,dsf:2}); await page.addStyleTag({content:NOARROW});
  out.replaced=await prep(page); await page.waitForTimeout(300);
  out.jae=await page.evaluate(()=>{ const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='정재민'); let el=t; for(let i=0;i<10&&el;i++){ const cs=getComputedStyle(el); const r=el.getBoundingClientRect(); if(parseFloat(cs.borderTopWidth)>0&&r.width>300) return {x:r.x,y:r.y,w:r.width,h:r.height}; el=el.parentElement; } return null; });
  await shot(page,O+'gb5_gate_full_r.png');                                  // 가이드북용(뷰포트 1440×1290)
  await shot(page,O+'bc2_gate_full_s3_r.png',{fullPage:true});               // 방송판용(전체 페이지)
  await page.evaluate(()=>document.documentElement.classList.add('noarrow')); await page.waitForTimeout(150);
  await shot(page,O+'gb5_gate_reco3_r.png',{clip:{x:150,y:580,width:1140,height:509}});
  await browser.close(); }
fs.writeFileSync(O+'cap_gb5_jae.json',JSON.stringify(out,null,1)); console.log(JSON.stringify(out));
