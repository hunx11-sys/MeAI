// 질병 검색 사전(ui/meai-lex.js) 점검 — 사전 값마다 공식 병명(DATA.codenames)에서 1개 이상 찾아지는지 본다.
//   node scripts/check_lex.js            (실패가 있으면 1 로 끝난다)
//   node scripts/check_lex.js --list     (사전 키마다 찾은 코드 · 병명을 모두 보여 준다)
// 사전은 코드를 갖지 않는다 — 여기서 찾은 코드는 모두 tool.html DATA 에서 온 것이다.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'tool.html'), 'utf8');
const m = html.match(/<script id="DATA"[^>]*>([\s\S]*?)<\/script>/);
const D = JSON.parse(m[1]);
const Lex = require(path.join(ROOT, 'ui', 'meai-lex.js'));
const L = Lex.create(D.codenames, D.synonyms);
const list = process.argv.includes('--list');
let bad = 0, n = 0;
for (const k of Object.keys(Lex.LAY)) {
  n++;
  for (const t of Lex.LAY[k]) {
    const c = L.byTarget(t);
    if (!c.length) { bad++; console.log('✗ 찾지 못함', k, '→', t); }
  }
  if (list) {
    const ex = L.expand(k);
    console.log(k, '→', ex.codes.map(c => c + ' ' + D.codenames[c]).join(' · '));
  }
}
// 낱말표 : 값 표기가 병명 어딘가에는 있어야 한다(없으면 쓸모없는 낱말)
const names = Object.keys(D.codenames).filter(c => /^[A-Z]\d/.test(c)).map(c => Lex.norm(D.codenames[c]));
let wbad = 0;
for (const [k, alts] of Object.entries(Lex.WORD)) {
  if (!alts.some(a => names.some(nm => nm.indexOf(Lex.norm(a)) >= 0))) { wbad++; console.log('· 낱말표 값이 병명에 없음', k, alts.join('|')); }
}
console.log(`사전 ${n}개 키 · 값 실패 ${bad} · 낱말표 ${Object.keys(Lex.WORD).length}개(병명에 없는 값 ${wbad})`);
process.exit(bad ? 1 : 0);
