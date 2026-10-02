// MeAI 홈 화면별 사용 매뉴얼 (MeAI 홈 공지사항 게시용)
// 가이드북 v4 의 '화면 + 번호 핀 + 기능 설명' 쪽만 골라 화면 순서(들어가기 → 홈 → 검색 → 고객찾기 → 게시판·동의 → 대화)로 엮는다.
// 쪽 내용은 가이드북 parts/*.js 를 그대로 불러 그리므로, 가이드북을 고치면 매뉴얼도 다시 만들기만 하면 따라간다.
// 사용: node manual.js out.pptx      (NODE_PATH 에 pptxgenjs 가 있어야 함)
const path = require('path');
const B = path.join(__dirname, '..', 'build');
const L = require(path.join(B, 'lib.js'));
const { C, W, H, M } = L;
const F = process.env.CAPTURES || path.join(__dirname, '..', 'captures');
const HERO = n => `${F}/hero/${n}.png`;
L.setFooterText('MeAI 홈 사용 매뉴얼 · 세일즈혁신TF');

// 1) 가이드북 79쪽을 순서대로 모아 둔다(deck.js 와 같은 방식)
const ctx = { L, C, W, H, M, HERO, LEG:n=>`${F}/legacy/${n}.png`, AG:(s,n)=>`${F}/${s}/${n}.png`, parts:{} };
const S = [];
for (const p of ['p0','p1','p2','p3','p4','p5','p6','p7','p8','p9']) require(path.join(B,'parts',p+'.js'))(S, ctx);
S.forEach((s,i)=>{ if (s.part) ctx.parts[s.part] = i+1; });

// 2) 장 구성: [장 제목, 한 줄 설명, 가이드북 쪽 번호들]
// [장 제목, 한 줄 설명, 가이드북 쪽 번호들, 목차에 적을 '이 장에서 배우는 기능']
const CH = [
  ['영업포탈에서 들어가기', 'MeAI 홈으로 들어오는 길', [13,14], '진입로 6곳 · 새 버튼 3개(롤링배너 · CRM 리스트 · 떠 있는 버튼)'],
  ['MeAI 홈', '하루가 시작되는 첫 화면', [15,16,17,18,19,20,23,24], '화면 구성 · 글씨 확대 · 대화 카드 · 숫자 4개 · 추천 카드 · 범례 · 가는 곳'],
  ['고객 검색 팝업', '이름으로 고객을 골라 맞춤대화', [26,27,28], '팝업 구성 · 이름 검색 · 동의 상태(D-n · 회색)'],
  ['MeAI 고객찾기', '그룹으로 묶인 내 고객과 다음 행동', [31,32,33,35,36,37,38,39,40,41], '화면 구성 · 그룹 · 고객 카드 6칸 · 태그 색 · 다음 행동 · 동의별 행동 · 검색'],
  ['게시판 · 사전조회 동의', '공지 확인과 동의 요청', [44,45,46], '게시판 목록 · 글 본문과 첨부파일 · 사전조회 동의 알림톡'],
  ['일반대화 · 맞춤대화', '묻고, 읽고, 보내기', [48,49,60,50,51,52,53,54,55,56,57,58,59], '대화 열기 · 일반/맞춤대화 화면 · 답변 읽기 · 용어 · 간편/상세 · 꼬리질문 · 요약 리포트 · 모바일'],
];
// 가이드북 PART 번호 → 매뉴얼 장 번호(본문 속 '(PART 3)' 같은 안내를 매뉴얼 장으로 바꿈). PART 8 은 매뉴얼에 없어 지움
const PART2CH = { '2':2, '3':3, '4':4, '5':5, '6':6 };
// 가이드북 쪽 번호 → 매뉴얼 쪽 번호(아래 plan 계산 뒤 채움). 본문 속 '태그 색은 36쪽' 같은 가이드북 쪽 안내를 매뉴얼 쪽으로
const GP2M = {};
const fixText = t => typeof t!=='string' ? t : t
  .replace(/(태그 색은 |자세한 설명은 )(\d+)쪽/g, (m,a,n)=> GP2M[n] ? `${a}${GP2M[n]}쪽` : m)
  .replace('고객찾기 그룹 태그는 PART 4', ()=>`고객찾기 그룹 태그 색은 ${GP2M[ctx.parts['04']+6]}쪽 참고`)
  .replace('누른 뒤 화면은 PART 4', ()=>`누른 뒤 화면은 ${GP2M[ctx.parts['04']+1]}쪽 참고`)
  .replace(/\s*\(PART 8\)/g, '')
  .replace(/PART (\d)/g, (m,d)=> PART2CH[d] ? `${PART2CH[d]}장 ${CH[PART2CH[d]-1][0]}` : m);

// 3) 쪽 그리기 도우미: 머리글(kicker)을 매뉴얼 장 이름으로, 본문 속 PART 안내를 매뉴얼 장으로
let curCh = 0;
const base0 = L.base;
// 매뉴얼에서 뜻이 안 통하는 가이드북 머리글은 바꿔 씀. 오른쪽 위에 NEW 표가 따로 있으면 머리글의 NEW 는 뺌
const KICK = { '길 1':'팝업 화면 구성', '모바일':'모바일에서 들어가기', '검색 · 필터 · 페이지':'검색·필터·페이지' };
const fx = v => Array.isArray(v) ? v.map(r=>Object.assign({}, r, { text: fixText(r.text) })) : fixText(v);
L.base = (pres, o) => { let k = o.kicker ? o.kicker.replace(/^PART \d+ · /,'') : o.kicker;
  if (k && o.tag && o.tag.text==='NEW') k = k.replace(/^NEW\s+/,'');
  return base0(pres, Object.assign({}, o, { kicker: k ? `${curCh}장 · ${KICK[k]||k}` : o.kicker, title: fx(o.title) })); };
const pres = L.newPres(); pres.title = 'MeAI 홈 사용 매뉴얼';
const add0 = pres.addSlide.bind(pres);
pres.addSlide = (...a) => { const s = add0(...a); const at = s.addText.bind(s);
  s.addText = (txt, opt) => at(Array.isArray(txt) ? txt.map(r => Object.assign({}, r, { text: fixText(r.text) })) : fixText(txt), opt);
  return s; };

// 4) 쪽 번호 미리 계산: 표지 1 · 목차 2 · 장마다 [나눔 1 + 화면들] · 마지막 1
let no = 3; const plan = CH.map(([t,d,pages,f],i)=>{ const start = no; no += 1 + pages.length; return { i:i+1, t, d, pages, f, start }; });
plan.forEach(c=>c.pages.forEach((gp,k)=>{ GP2M[gp] = c.start+1+k; }));
const LAST = no;
// 가이드북 쪽 제목(목차·나눔용): PDF 책갈피와 같은 글자. 그리기 전에 알아야 하므로 한 번 그려서 얻는다
const TITLES = {};
{ const tmp = new (require('pptxgenjs'))(); tmp.layout='LAYOUT_WIDE'; const n0 = L.NAV.length;
  plan.forEach(c=>c.pages.forEach(gp=>{ curCh = c.i; const before = L.NAV.length; S[gp-1].fn(tmp, 900+gp); const e = L.NAV.slice(before).find(x=>x.title); if (e) TITLES[gp] = e.title; }));
  L.NAV.length = n0; L.LINKS.length = 0; }

// 표지
L.cover(pres, { title:'MeAI 홈\n사용 매뉴얼', sub:'화면별 기능 안내', line3:'영업포탈에서 들어가기부터\n대화 · 요약 리포트 발송까지 · 영업가족 편', meta:['세일즈혁신TF'], file:HERO('gb5_gate_full_m'), pageNo:1 });

// 목차
{ const s = base0(pres, { kicker:'CONTENTS', title:'목차', sub:'화면 그림의 번호와 옆·아래 설명의 번호가 짝 · 화면 속 이름·숫자는 모두 예시', pageNo:2 });
  const cw = (W-2*M-0.3)/2, rh = 1.42;
  plan.forEach((c,k)=>{ const x = M + (k%2)*(cw+0.3), y = 1.95 + Math.floor(k/2)*(rh+0.14);
    L.R(s,{x,y,w:cw,h:rh,fill:C.white,line:C.g200,radius:0.16,shadow:true});
    L.T(s,String(c.i).padStart(2,'0'),{x:x+0.3,y:y+0.22,w:0.8,h:0.5,fontSize:24,bold:true,color:C.blue,valign:'middle'});
    L.T(s,c.t,{x:x+1.1,y:y+0.2,w:cw-2.2,h:0.36,fontSize:16,bold:true,color:C.navy,valign:'middle'});
    L.T(s,`p.${c.start}`,{x:x+cw-1.2,y:y+0.2,w:0.9,h:0.36,fontSize:12,color:C.g500,align:'right',valign:'middle'});
    L.T(s,c.d,{x:x+1.1,y:y+0.58,w:cw-1.4,h:0.28,fontSize:11.5,color:C.blue,valign:'middle'});
    L.T(s,`화면 ${c.pages.length}쪽 · ${c.f}`,{x:x+1.1,y:y+0.9,w:cw-1.4,h:0.36,fontSize:10.5,color:C.g600,valign:'top'});
    L.link(2,{x,y,w:cw,h:rh},c.start); });
}

// 장 나눔 + 화면 쪽
function chapterPage(c){
  const s = pres.addSlide(); s.background = { path:L.BG.divider };
  L.NAV.push({ pageNo:c.start, part:String(c.i).padStart(2,'0'), title:c.t }); // PDF 책갈피 1단
  L.T(s, String(c.i).padStart(2,'0'), { x:W-6.2, y:0.9, w:5.6, h:3.2, fontSize:170, bold:true, color:'FFFFFF', transparency:82, align:'right', valign:'top' });
  L.T(s, `${c.i}장`, { x:M+0.2, y:1.5, w:6, h:0.35, fontSize:12, bold:true, color:'FFFFFF', transparency:25 });
  L.T(s, c.t, { x:M+0.2, y:1.9, w:8.5, h:0.9, fontSize:36, bold:true, color:'FFFFFF', valign:'top' });
  L.T(s, c.d, { x:M+0.2, y:2.85, w:8.5, h:0.5, fontSize:15, color:'FFFFFF', transparency:10 });
  L.T(s, '이 장의 화면', { x:M+0.2, y:3.75, w:6, h:0.3, fontSize:11, bold:true, color:'FFFFFF', transparency:25 });
  const col = c.pages.length > 7 ? 2 : 1, per = Math.ceil(c.pages.length/col), cw = 5.9;
  c.pages.forEach((gp,k)=>{ const x = M+0.2 + Math.floor(k/per)*(cw+0.3), y = 4.15 + (k%per)*0.4;
    L.T(s, `p.${c.start+1+k}`, { x, y, w:0.75, h:0.32, fontSize:11.5, bold:true, color:'FFFFFF', transparency:30, valign:'middle' });
    L.T(s, (TITLES[gp]||'').replace(/[“”"]/g,''), { x:x+0.75, y, w:cw-0.8, h:0.32, fontSize:12.5, color:'FFFFFF', valign:'middle' });
    L.link(c.start,{x,y,w:cw,h:0.32},c.start+1+k); });
  L.T(s, 'MeAI 홈 사용 매뉴얼 · 세일즈혁신TF', { x:M, y:H-0.42, w:8, h:0.25, fontSize:9, color:'FFFFFF', transparency:15 });
  L.T(s, String(c.start), { x:W-M-1, y:H-0.42, w:1, h:0.25, fontSize:9, color:'FFFFFF', align:'right' });
}
plan.forEach(c=>{ curCh = c.i; chapterPage(c); c.pages.forEach((gp,k)=> S[gp-1].fn(pres, c.start+1+k)); });

// 마지막: 지킬 것 · 문의
{ curCh = 0; const s = base0(pres, { kicker:'꼭 지켜 주세요', title:'MeAI를 쓸 때 지킬 것 네 가지', sub:'자세한 활용법은 「MeAI 활용 가이드북(영업가족 편)」 참고', pageNo:LAST });
  const rules = [['개인정보 넣지 않기','이름·연락처·주소·주민번호는 질문에도 메모에도 넣지 않음'],['답변은 검증 후 사용','숫자·약관 근거를 직접 확인한 뒤 사용. 미검증으로 인한 관련 법령상 책임은 사용자에게 있음'],['동의 없으면 보지 않기','동의가 없거나 철회된 고객은 우회하지 않고 동의부터'],['자료 외부 반출 금지','MeAI 답변·화면 캡처·이 매뉴얼은 외부에 제공·배포·게시 금지']];
  const gap = 0.22, cw = (W-2*M-gap)/2, ch = 1.55;
  rules.forEach(([a,b],i)=>{ const x = M+(i%2)*(cw+gap), y = 1.95+Math.floor(i/2)*(ch+gap);
    L.R(s,{x,y,w:cw,h:ch,fill:C.white,line:C.g200,radius:0.16,shadow:true});
    L.badge(s,{x:x+0.3,y:y+0.3,n:i+1,d:0.44,color:C.red});
    L.T(s,a,{x:x+0.95,y:y+0.25,w:cw-1.2,h:0.5,fontSize:18,bold:true,color:C.navy,valign:'middle'});
    L.T(s,b,{x:x+0.95,y:y+0.8,w:cw-1.2,h:0.6,fontSize:12.5,color:C.g700,valign:'top',lineSpacingMultiple:1.2}); });
  L.R(s,{x:M,y:5.5,w:W-2*M,h:1.0,fill:C.navy,line:null,radius:0.16});
  L.T(s,'문의  세일즈혁신TF',{x:M+0.4,y:5.5,w:W-2*M-0.8,h:1.0,fontSize:20,bold:true,color:'FFFFFF',valign:'middle'});
  L.T(s,'화면 속 고객 이름·숫자는 모두 예시',{x:M+0.4,y:5.5,w:W-2*M-0.8,h:1.0,fontSize:12,color:'FFFFFF',align:'right',valign:'middle',transparency:20});
}
const out = process.argv[2] || 'manual.pptx';
pres.writeFile({ fileName: out }).then(()=>{
  require('fs').writeFileSync(out+'.nav.json', JSON.stringify({ pages:LAST, part_fmt:'{n}장', toc_page:2, parts:Object.fromEntries(plan.map(c=>[String(c.i).padStart(2,'0'),c.start])), nav:L.NAV, links:L.LINKS }, null, 1));
  console.log('written', out, LAST, 'slides'); if (L.MISSING.length) console.log('MISSING', L.MISSING); });
