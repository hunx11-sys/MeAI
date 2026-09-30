// MeAI 활용 가이드북 v4 · MeAI 홈 편 — 생성기
const L = require('./lib.js');
const path = require('path');
const F = process.env.CAPTURES || path.join(__dirname, '..', 'captures');
const ctx = { L, C:L.C, W:L.W, H:L.H, M:L.M, HERO:(n)=>`${F}/hero/${n}.png`, LEG:(n)=>`${F}/legacy/${n}.png`, AG:(s,n)=>`${F}/${s}/${n}.png`, parts:{} };
const S = []; // {fn(pres, pageNo), part?}
const ONLY = process.env.ONLY; // ONLY=p4 → 그 파트만 만들어 빠르게 확인
for (const p of ['p0','p1','p2','p3','p4','p5','p6','p7','p8','p9']) { if (ONLY && p!==ONLY) continue; require('./parts/'+p+'.js')(S, ctx); }
// 파트 시작 페이지 계산
S.forEach((s,i)=>{ if (s.part) ctx.parts[s.part] = i+1; });
const pres = L.newPres();
S.forEach((s,i)=> s.fn(pres, i+1));
const out = process.argv[2] || 'MeAI_guidebook_v4.pptx';
pres.writeFile({ fileName: out }).then(()=>{ console.log('written', out, S.length, 'slides'); if (L.MISSING.length) console.log('MISSING:', L.MISSING); else console.log('no missing images'); });
