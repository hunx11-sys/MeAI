// 게시판 목록·글 상세를 다시 찍는다(2026.10, 가이드북 5부 43·44쪽): 화면 속 '대문'·'8월 12일'·'9개 진입점'·'2차 오픈' 글자를 없앰.
// 목업(index_260929_v2) 안의 글자만 바꿔 찍음. 바꾸는 문구는 가이드북 FAQ 표현(영업포탈에서 MeAI로 들어오면 MeAI 홈이 가장 먼저 열림)만 씀 — 새 날짜·개수 없음.
// 실행: CAP_SRC=file://<scratchpad>/src/index_260929_v2.html node cap_gb5_home_board.mjs
// 결과(원본 화면, 새 이름 · 옛 파일 덮어쓰지 않음): final/gb5/gb5_board_list_home.png, final/gb5/gb5_board_detail_home.png, final/gb5/cap_gb5_home_board.json(핀 자리용 좌표, CSS px)
// 자르기: bc2/crops_gb5.py 11) → gb5/captures/hero/board_list_crop.png · gb5_board_detail_1370.png
import { open, shot, ROUTES } from '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/cap.mjs';
import fs from 'fs';
const O='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/gb5/';
const BANNED=['대문','9개','8월 12일','2차'];
const {browser,page}=await open(ROUTES.board010,{width:1440,height:900,dsf:2});
// 잎 노드(자식 요소 없음)에서 글이 정확히 같은 것만 바꿈. 바뀐 개수를 돌려받아 0 이면 멈춤
const swap=async(pairs)=>await page.evaluate((pairs)=>pairs.map(([a,b])=>{ const els=[...document.querySelectorAll('body *')].filter(e=>e.childElementCount===0&&e.textContent.trim()===a); els.forEach(e=>{ e.textContent=b; }); return [a,els.length]; }),pairs);
const need=(res)=>{ for (const [a,n] of res) if (n<1) throw new Error('not found: '+a); };
const check=async(tag)=>{ const t=await page.evaluate(()=>document.body.innerText); const hit=BANNED.filter(w=>t.includes(w)); if (hit.length) throw new Error(tag+' still has '+hit.join(',')); };
const rect=async(fn,arg)=>await page.evaluate(([src,arg])=>{ const f=eval(src); const e=f(arg); if(!e) return null; const r=e.getBoundingClientRect(); return {x:+r.x.toFixed(1),y:+r.y.toFixed(1),w:+r.width.toFixed(1),h:+r.height.toFixed(1)}; },[fn.toString(),arg]);
const leaf=(t)=>[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()===t);
const R={};
// ---- 목록 ----
need(await swap([['MeAI 대문 페이지 오픈 안내','MeAI 홈 오픈 안내'],['8월 12일부터 영업포탈에서 MeAI 대문으로 진입합니다.','영업포탈에서 MeAI로 들어오면 MeAI 홈이 먼저 열립니다.']]));
await page.waitForTimeout(300);
await check('list');
R.list={ clip:{x:270,y:85},
  title: await rect((t)=>[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()===t),'MeAI 홈 오픈 안내'),
  desc: await rect((t)=>[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()===t),'영업포탈에서 MeAI로 들어오면 MeAI 홈이 먼저 열립니다.'),
  newBadge: await rect(()=>{ const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='MeAI 홈 오픈 안내'); let row=t; for(let i=0;i<4;i++) row=row.parentElement; return [...row.querySelectorAll('*')].find(e=>e.childElementCount===0&&e.textContent.trim()==='NEW'); }),
  clipCount: await rect(()=>{ const t=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='MeAI 홈 오픈 안내'); let row=t; for(let i=0;i<4;i++) row=row.parentElement; const n=[...row.querySelectorAll('*')].find(e=>e.childElementCount===0&&e.textContent.trim()==='1'); return n&&n.parentElement; }),
  date1: await rect((t)=>[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()===t),'2026-08-04'),
};
await shot(page,O+'gb5_board_list_home.png',{clip:{x:0,y:0,width:1440,height:900}});
// ---- 글 상세 ----
await page.getByText('MeAI 홈 오픈 안내',{exact:true}).first().click(); await page.waitForTimeout(1200);
need(await swap([
  ['MeAI 대문 페이지 오픈 안내','MeAI 홈 오픈 안내'],
  ['8월 12일 오전 9시부터 영업포탈의 MeAI 진입점이 MeAI 대문으로 통합됩니다. 기존 9개 진입점은 당분간 함께 유지되며, 전환 일정은 별도 공지합니다.','영업포탈에서 MeAI로 들어오면 MeAI 홈이 가장 먼저 열립니다.'],
  ['MeAI 대문 오픈 안내.pdf','MeAI 홈 오픈 안내.pdf'],
]));
// 둘째 문단은 앞의 '대문에서는'만 'MeAI 홈에서는'으로
const p2=await page.evaluate(()=>{ const e=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim().startsWith('대문에서는')); if(!e) return 0; e.textContent=e.textContent.replace('대문에서는','MeAI 홈에서는'); return 1; });
if (!p2) throw new Error('not found: 대문에서는');
// '2차 오픈' 문장(셋째 문단) 지움 — cap_gb5_board.mjs 와 같은 방법
const removed=await page.evaluate(()=>{ const els=[...document.querySelectorAll('body *')].filter(e=>e.childElementCount===0&&e.textContent.includes('2차 오픈')); els.forEach(e=>e.remove()); return els.length; });
if (removed!==1) throw new Error('2차 오픈 leaf count '+removed);
await page.waitForTimeout(300);
await check('detail');
const near=(t,up)=>[t,up];
R.detail={ clip:{x:270,y:95},
  h1: await rect(()=>document.querySelector('h1')),
  newBadge: await rect(()=>{ const h=document.querySelector('h1'); return [...h.parentElement.querySelectorAll('*')].find(e=>e.childElementCount===0&&e.textContent.trim()==='NEW'); }),
  p1: await rect((t)=>[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()===t),'영업포탈에서 MeAI로 들어오면 MeAI 홈이 가장 먼저 열립니다.'),
  p2: await rect(()=>[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim().startsWith('MeAI 홈에서는'))),
  attachHead: await rect((t)=>[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()===t),'첨부파일 1건'),
  // 첨부 카드: 파일 이름에서 위로 올라가며 테두리가 있는 첫 상자
  attachCard: await rect(()=>{ let e=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='MeAI 홈 오픈 안내.pdf'); while(e&&e!==document.body){ const cs=getComputedStyle(e); if(parseFloat(cs.borderTopWidth)>0) return e; e=e.parentElement; } return null; }),
  prevCard: await rect(()=>{ let e=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='이전 글'); while(e&&e!==document.body){ const r=e.getBoundingClientRect(); if(r.height>60) return e; e=e.parentElement; } return null; }),
  nextCard: await rect(()=>{ let e=[...document.querySelectorAll('body *')].find(e=>e.childElementCount===0&&e.textContent.trim()==='다음 글'); while(e&&e!==document.body){ const r=e.getBoundingClientRect(); if(r.height>60) return e; e=e.parentElement; } return null; }),
};
await shot(page,O+'gb5_board_detail_home.png');
fs.writeFileSync(O+'cap_gb5_home_board.json', JSON.stringify(R,null,1));
console.log(JSON.stringify({removed, ...R}));
await browser.close();
