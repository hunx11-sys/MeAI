// 세일즈북 자동 생성기 공모전 설명서(PPT) 조립 스크립트 — 캡처(shots/)·아이콘(icons/)은 세션 작업폴더에서 만들어 썼다. 재조립 : 같은 폴더 구조에서 NODE_PATH=node_modules node build_contest_deck.js
const pptxgen = require('pptxgenjs');
const fs = require('fs');
const { applyTheme } = require('/root/.claude/skills/synced/d9a1f0fe-3185-43c1-bc3d-15404e2e2f87_522276b5-baa1-4dab-b0a1-db621f094787/pptx/scripts/apply_theme.js');

const SH = 'shots/'; const IC = 'icons/';
const THEME = {
  name: 'Toss Clean', headFontFace: 'Malgun Gothic', bodyFontFace: 'Malgun Gothic',
  colors: { dk1: '191F28', lt1: 'FFFFFF', dk2: '4E5968', lt2: 'F2F4F6', accent1: '3182F6', accent2: '1B64DA', accent3: 'E8F3FF',
            accent4: 'F04452', accent5: '03B26C', accent6: '8B95A1', hlink: '3182F6', folHlink: '1B64DA' } };
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';            // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = '세일즈북 자동 생성기 — 사용 가이드 및 제작 취지'; pres.author = '세일즈혁신TF'; pres.company = 'Meritz';
const C = pres.SchemeColor;
const W = 13.333, Hh = 7.5, M = 0.6;

// ── 레이아웃 ──────────────────────────────────────────────
pres.defineSlideMaster({ title: 'TITLE', background: { color: THEME.colors.accent1 }, objects: [] });
pres.defineSlideMaster({ title: 'CONTENT', background: { color: 'FFFFFF' }, objects: [
  { placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.42, w: W - 2 * M, h: 0.8, fontSize: 28, bold: true, color: THEME.colors.dk1, margin: 0, valign: 'top', align: 'left' }, text: '제목' } },
  { placeholder: { options: { name: 'lead', type: 'body', x: M, y: 1.12, w: W - 2 * M, h: 0.5, fontSize: 14, color: THEME.colors.dk2, margin: 0, valign: 'top', align: 'left' }, text: '' } },
  { text: { text: '세일즈북 자동 생성기 · 세일즈혁신TF · 사내 공모전 제출용', options: { x: M, y: 7.02, w: 8, h: 0.3, fontSize: 9, color: THEME.colors.accent6, margin: 0 } } },
], slideNumber: { x: W - M - 0.8, y: 7.02, w: 0.8, h: 0.3, fontSize: 9, color: THEME.colors.accent6, align: 'right' } });
pres.defineSlideMaster({ title: 'SECTION', background: { color: THEME.colors.lt2 }, objects: [] });

// ── 도우미 ─────────────────────────────────────────────
let n = 0; const nm = p => `${p}-${++n}`;
function card(s, x, y, w, h, o = {}) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: o.r ?? 0.16, fill: { color: o.fill || THEME.colors.lt2 },
    line: o.line ? { color: o.line, width: 0.75 } : { color: o.fill || THEME.colors.lt2, width: 0 }, objectName: nm('card'),
    shadow: o.shadow ? { type: 'outer', color: '191F28', blur: 6, offset: 2, angle: 90, opacity: 0.08 } : undefined });
}
function text(s, t, x, y, w, h, o = {}) {
  s.addText(t, Object.assign({ x, y, w, h, isTextBox: true, margin: 0, fontSize: 14, color: THEME.colors.dk1, valign: 'top', objectName: nm('text') }, o));
}
function icon(s, k, col, x, y, size = 0.42, circle = null) {
  if (circle) s.addShape(pres.ShapeType.ellipse, { x: x - 0.17, y: y - 0.17, w: size + 0.34, h: size + 0.34, fill: { color: circle }, line: { color: circle, width: 0 }, objectName: nm('circ') });
  s.addImage({ path: `${IC}${k}_${col}.png`, x, y, w: size, h: size, objectName: nm('icon') });
}
function pic(s, f, x, y, w, h, o = {}) {
  if (o.frame !== false) s.addShape(pres.ShapeType.roundRect, { x: x - 0.06, y: y - 0.06, w: w + 0.12, h: h + 0.12, rectRadius: 0.1, fill: { color: 'FFFFFF' }, line: { color: THEME.colors.lt2, width: 1 }, objectName: nm('frame'),
    shadow: { type: 'outer', color: '191F28', blur: 8, offset: 2, angle: 90, opacity: 0.10 } });
  s.addImage({ path: SH + f, x, y, w, h, objectName: nm('pic') });
}
function stat(s, num, unit, label, x, y, w, o = {}) {
  card(s, x, y, w, 1.45, { fill: o.fill || THEME.colors.lt2 });
  s.addText([{ text: num, options: { fontSize: 34, bold: true, color: o.color || THEME.colors.accent1 } }, { text: ' ' + unit, options: { fontSize: 14, color: THEME.colors.dk2 } }],
    { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.75, isTextBox: true, margin: 0, valign: 'middle', objectName: nm('stat') });
  text(s, label, x + 0.25, y + 0.95, w - 0.5, 0.4, { fontSize: 12, color: THEME.colors.dk2 });
}
function badge(s, t, x, y, w, col = THEME.colors.accent1, bg = THEME.colors.accent3) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.34, rectRadius: 0.17, fill: { color: bg }, line: { color: bg, width: 0 }, objectName: nm('badge') });
  text(s, t, x, y, w, 0.34, { fontSize: 11, bold: true, color: col, align: 'center', valign: 'middle' });
}
function numdot(s, k, x, y, col = THEME.colors.accent1) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: 0.36, h: 0.36, fill: { color: col }, line: { color: col, width: 0 }, objectName: nm('dot') });
  text(s, String(k), x, y, 0.36, 0.36, { fontSize: 13, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
}
function content(title, lead, section) {
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: section });
  s.addText(title, { placeholder: 'title' });
  if (lead) s.addText(lead, { placeholder: 'lead' });
  return s;
}

// ══════════════ 1. 표지 ══════════════
pres.addSection({ title: '시작' });
{
  const s = pres.addSlide({ masterName: 'TITLE', sectionTitle: '시작' });
  badge(s, '사내 공모전 제출 · 세일즈혁신TF', M, 0.9, 3.3, 'FFFFFF', THEME.colors.accent2);
  text(s, '세일즈북 자동 생성기', M, 1.6, 7.4, 1.2, { fontSize: 48, bold: true, color: 'FFFFFF' });
  text(s, '상품설명서 PDF 한 장을 넣으면\n약관 기준 컨설팅 가이드북이 1분 안에 나옵니다', M, 2.95, 7.2, 1.3, { fontSize: 22, color: 'FFFFFF' });
  text(s, '사용 가이드 및 제작 취지  ·  2026년 10월', M, 4.5, 7, 0.4, { fontSize: 14, color: 'D6E6FF' });
  text(s, '오프라인 단일 HTML  ·  8개 상품  ·  특약 4,338건  ·  설치 없음', M, 6.5, 7.4, 0.4, { fontSize: 12, color: 'D6E6FF' });
  pic(s, 'page_01.png', 8.55, 0.75, 4.25, 6.0, { frame: false });
  s.addNotes('세일즈북 자동 생성기 소개 덱. 발표 시 표지 오른쪽은 실제 생성 결과(표지)입니다.');
}

// ══════════════ 2. 한 줄 요약 ══════════════
pres.addSection({ title: '왜 만들었나' });
{
  const s = content('한 줄로 말하면', '설계사가 고객 앞에서 쓰는 「상품 가이드북」을 사람이 아니라 프로그램이 만듭니다', '왜 만들었나');
  text(s, '상품설명서 PDF 를 끌어다 놓으면', M, 1.85, 7.4, 0.5, { fontSize: 20, color: THEME.colors.dk2 });
  s.addText([{ text: '담보표 · 설명문 · Key Point · 면책감액표', options: { bold: true, color: THEME.colors.accent1 } }, { text: '를 묶은\n20쪽 안팎의 가이드북이 자동으로 나옵니다.', options: { color: THEME.colors.dk1 } }],
    { x: M, y: 2.35, w: 7.6, h: 1.4, isTextBox: true, margin: 0, fontSize: 21, bold: true, valign: 'top', objectName: nm('hero') });
  stat(s, '8', '개 상품', '통합간편 · 케어프리 · 또또암 등 약관 내장', M, 4.05, 2.35);
  stat(s, '4,338', '건', '특약 마스터 · 약관 별표 질병코드 포함', M + 2.55, 4.05, 2.35);
  stat(s, '0', '개', '추정한 질병코드·금액 — 전부 약관·설계서에서', M + 5.1, 4.05, 2.35, { color: THEME.colors.accent5 });
  text(s, '이 생성기는 MeAI 고도화를 위한 선행 과제입니다 — 약관을 읽어 만든 데이터와 지면 틀을 MeAI 리포트 생성의 재료로 잇는 제언을 뒤에 적었습니다.', M, 5.7, 7.4, 0.5, { fontSize: 11.5, color: THEME.colors.accent1, bold: true });
  text(s, '※ 생성 소요시간은 테스트 환경(노트북 · 36쪽 설계서) 기준 30~60초. 이 덱의 화면은 개인정보가 없는 테스트용 설계서로 만든 것입니다.', M, 6.25, 7.4, 0.5, { fontSize: 10.5, color: THEME.colors.accent6 });
  pic(s, 'page_02.png', 8.55, 1.75, 3.7, 5.1);
  badge(s, '자동 생성된 「1장 요약」', 8.55, 6.6, 2.4);
}

// ══════════════ 3. AS-IS ══════════════
{
  const s = content('지금은 이렇습니다 (AS-IS)', '상품은 많고 약관은 두꺼운데, 고객에게 설명할 「한 권」은 누군가 손으로 만들어야 했습니다', '왜 만들었나');
  const items = [
    ['warn', '상품설명서는 「나열」이다', '담보명과 가입금액이 수십 줄 이어질 뿐, 왜 이 담보가 중요한지·언제 못 받는지는 적혀 있지 않습니다. 설계사가 머릿속에서 다시 조립해야 합니다.'],
    ['book', '약관은 수백~천 쪽이다', '질병코드 별표·감액 조건·수가코드는 약관 깊숙이 있습니다. 상담 중 열어 볼 수 없고, 기억에 의존하면 설명이 설계사마다 달라집니다.'],
    ['clock', '가이드북은 사람이 만든다', '본사가 상품별 가이드북을 수작업으로 편집합니다. 상품 개정·신상품마다 처음부터 다시 만들고, 고객별 설계안에 맞춘 판은 아예 없습니다.'],
  ];
  items.forEach(([ic, h, b], i) => {
    const x = M + i * 4.1;
    card(s, x, 1.95, 3.85, 3.75, { fill: 'FFFFFF', line: THEME.colors.lt2, shadow: true });
    icon(s, ic, 'r', x + 0.47, 2.4, 0.42, 'FFECEC');
    text(s, h, x + 0.3, 3.2, 3.25, 0.5, { fontSize: 17, bold: true });
    text(s, b, x + 0.3, 3.75, 3.25, 2.5, { fontSize: 13, color: THEME.colors.dk2, lineSpacingMultiple: 1.25 });
  });
  text(s, '결과 : 같은 상품을 설계사마다 다르게 설명하고, 좋은 가이드북은 일부 상품에만 존재합니다.', M, 6.05, 12, 0.4, { fontSize: 13, bold: true, color: THEME.colors.accent4 });
}

// ══════════════ 4. TO-BE ══════════════
{
  const s = content('이렇게 바뀝니다 (TO-BE)', '설계서 한 장이 들어오면 네 단계를 거쳐 가이드북이 나옵니다 · 전부 설계사 PC 안에서', '왜 만들었나');
  const steps = [
    ['upload', '설계서 읽기', '상품설명서 PDF 에서 담보명 · 가입금액 · 보장내용 설명문을 읽습니다. 줄바꿈으로 끊긴 긴 담보명도 이어 붙입니다.'],
    ['search', '특약 마스터 매칭', '8개 상품 약관에서 뽑은 특약 4,338건과 이름을 맞춰 약관 별표 분류번호 · 제외코드를 붙입니다.'],
    ['spark', 'Key Point 결합', '상담 글 상자 창고(36종)와 용어 풀이 · 자주 묻는 질문을 담보에 맞게 끼워 넣습니다. 빈 자리는 연관 정보로 채웁니다.'],
    ['printer', '가이드북 출력', '표지 → 1장 요약 → 용어 → 담보 지도 → 갈래별 해설 → 면책감액표 → 뒷표지. 인쇄 또는 PDF 저장.'],
  ];
  steps.forEach(([ic, h, b], i) => {
    const x = M + i * 3.1;
    card(s, x, 1.95, 2.85, 3.9, { fill: THEME.colors.lt2 });
    icon(s, ic, 'b', x + 0.42, 2.35, 0.44, 'FFFFFF');
    numdot(s, i + 1, x + 2.3, 2.15);
    text(s, h, x + 0.25, 3.15, 2.4, 0.45, { fontSize: 16, bold: true });
    text(s, b, x + 0.25, 3.65, 2.4, 2.1, { fontSize: 12, color: THEME.colors.dk2, lineSpacingMultiple: 1.25 });
    if (i < 3) icon(s, 'arrow', 'b', x + 2.88, 3.7, 0.22);
  });
  card(s, M, 6.05, 12.1, 0.8, { fill: THEME.colors.accent3 });
  icon(s, 'lock', 'b', M + 0.25, 6.24, 0.4);
  text(s, '파일은 PC 밖으로 나가지 않습니다. 인터넷 없이 동작하는 HTML 파일 하나(4.7MB)라서 설치 · 서버 · 로그인이 없고, 사내 메일로 보내 바로 쓸 수 있습니다.', M + 0.85, 6.1, 11, 0.7, { fontSize: 13, color: THEME.colors.dk1, valign: 'middle' });
}

// ══════════════ 5. 화면 ══════════════
pres.addSection({ title: '사용 가이드' });
{
  const s = content('화면은 이것이 전부입니다', '왼쪽 조작부 하나 · 오른쪽은 생성된 가이드북 미리보기', '사용 가이드');
  pic(s, 'crop_panel_start.png', M, 1.85, 3.45, 4.95);
  const pts = [
    ['상품설명서 PDF 끌어다 놓기', '점선 상자에 파일을 놓거나 클릭해서 고릅니다. 파일은 이 PC 안에서만 읽힙니다.'],
    ['샘플 2건 내장', '설계서가 없어도 「통합간편 · 내Mom대로 5.10.5」 샘플로 바로 결과를 볼 수 있습니다.'],
    ['가이드 제목 · 옵션 3개', 'Key Point 없는 담보 싣기 · 약관 별표 분류번호 표시 · 설계서 설명문 싣기. 비우면 상품명이 제목이 됩니다.'],
    ['다시 만들기 · 인쇄 · PDF 저장', '옵션을 바꾼 뒤 다시 만들고, 브라우저 인쇄창에서 「PDF로 저장」을 고르면 끝입니다.'],
  ];
  pts.forEach(([h, b], i) => {
    const y = 1.95 + i * 1.22;
    numdot(s, i + 1, 4.6, y + 0.02);
    text(s, h, 5.1, y - 0.02, 7.6, 0.4, { fontSize: 15, bold: true });
    text(s, b, 5.1, y + 0.4, 7.6, 0.7, { fontSize: 12.5, color: THEME.colors.dk2 });
  });
  text(s, '설명문은 설계서 뒤쪽 「가입담보 및 보장내용」에서, 분류번호는 약관 별표(특약 마스터)에서, Key Point 는 내장 글 상자 창고에서 옵니다.', 4.6, 6.75, 8.1, 0.3, { fontSize: 10.5, color: THEME.colors.accent6 });
}

// ══════════════ 6. 사용법 3단계 ══════════════
{
  const s = content('사용법은 세 단계', '처음 쓰는 설계사도 안내 없이 1분이면 끝납니다', '사용 가이드');
  const st = [
    ['upload', '1. 넣는다', 'guidebook_proto.html 을 더블클릭해 열고, 고객 설계서(상품설명서 PDF)를 점선 상자에 끌어다 놓습니다.'],
    ['eye', '2. 확인한다', '상태창에 「담보 ○건 · 특약 마스터 매칭 ○건 · 설명문 읽힘 ○건」이 찍힙니다. 매칭 안 된 담보가 있으면 이름이 그대로 나열됩니다.'],
    ['printer', '3. 저장한다', '「인쇄 · PDF로 저장」 → 대상 : PDF로 저장 · 여백 : 없음 · 배경 그래픽 : 켬. A4 세로 20쪽 안팎의 PDF 가 저장됩니다.'],
  ];
  st.forEach(([ic, h, b], i) => {
    const y = 1.95 + i * 1.6;
    card(s, M, y, 6.3, 1.4, { fill: i === 1 ? THEME.colors.accent3 : THEME.colors.lt2 });
    icon(s, ic, 'b', M + 0.35, y + 0.47, 0.44);
    text(s, h, M + 1.1, y + 0.22, 5, 0.4, { fontSize: 16, bold: true });
    text(s, b, M + 1.1, y + 0.62, 5, 0.75, { fontSize: 12, color: THEME.colors.dk2 });
  });
  pic(s, 'crop_status.png', 7.5, 1.95, 5.2, 2.48);
  badge(s, '상태창 — 무엇을 몇 건 읽었는지 그대로 보여 줍니다', 7.5, 4.65, 5.2);
  text(s, '설계서가 바뀌거나 상품이 개정돼도 설계사가 할 일은 같습니다. 데이터는 파일을 새로 받으면 갱신됩니다. 매칭 안 된 담보는 이름이 그대로 나열되므로 어느 담보를 보강해야 하는지도 바로 보입니다.', 7.5, 5.2, 5.2, 1.4, { fontSize: 12, color: THEME.colors.dk2 });
}

// ══════════════ 7. 결과물 구성 ══════════════
pres.addSection({ title: '결과물' });
{
  const s = content('결과물 : 20쪽 가이드북의 구성', '순서가 곧 상담 순서입니다 — 요약으로 시작해 갈래별 해설로 깊어지고 면책·감액표로 닫습니다', '결과물');
  const pages = [['page_01.png', '① 표지'], ['page_02.png', '② 1장 요약'], ['page_03.png', '③ 용어 풀이 · 상품 한눈에'], ['page_04.png', '④ 담보 지도'], ['page_08.png', '⑤ 갈래별 담보 해설 (1~5장)'], ['page_19.png', '⑥ 면책·감액표 · 뒷표지']];
  pages.forEach(([f, l], i) => {
    const x = M + i * 2.05;
    pic(s, f, x, 1.9, 1.85, 2.62);
    text(s, l, x, 4.62, 1.85, 0.6, { fontSize: 11.5, bold: true, color: THEME.colors.dk1 });
  });
  const notes = [['layers', '5갈래', '암 · 뇌심장순환기 · 수술비치료비 · 입원간병 · 상해운전배상기타'], ['tag', '쪽마다 장 이름', '쪽 머리띠에 「1장 암」처럼 장 이름과 쪽수가 붙어 넘기기 쉽습니다'], ['puzzle', '빈 자리 자동 채움', '여백이 남으면 그 갈래의 연관 정보 카드(25종)를 넣어 빈 쪽을 만들지 않습니다']];
  notes.forEach(([ic, h, b], i) => {
    const x = M + i * 4.1;
    icon(s, ic, 'b', x + 0.05, 5.5, 0.36);
    text(s, h, x + 0.55, 5.45, 3.3, 0.4, { fontSize: 14, bold: true });
    text(s, b, x + 0.55, 5.85, 3.3, 0.9, { fontSize: 11.5, color: THEME.colors.dk2 });
  });
}

// ══════════════ 8. 표지 · 1장 요약 ══════════════
{
  const s = content('표지와 「1장 요약」이 자동으로 써집니다', '상품명 · 피보험자 · 계약사항은 설계서에서, 숫자는 담보 목록을 세어서', '결과물');
  pic(s, 'page_01.png', M, 1.85, 3.5, 4.95);
  pic(s, 'page_02.png', 4.5, 1.85, 3.5, 4.95);
  const b = [['상품 한 장 요약', '가입 담보 수 · 월 보험료 · Key Point 수를 큰 숫자로. 지급액 계산은 하지 않습니다(설계서에 있는 숫자만).'],
             ['5갈래 타일', '갈래마다 담보 건수와 대표 담보 4개(가입금액 큰 순). 어느 층이 두터운 설계인지 한눈에.'],
             ['가입 첫 해 조건', '설명문에서 읽은 보장개시일(면책) · 1년 미만 감액 · 90일 미만 감액 담보 수. 읽은 것만 셉니다.'],
             ['상담 3층 구조', '걸리면 한 번 크게(진단비) → 치료할 때마다(치료비·수술비) → 병원에 있는 동안(입원일당·간병). 담보를 세 층으로 재분류.']];
  b.forEach(([h, t], i) => {
    const y = 1.9 + i * 1.22;
    text(s, h, 8.5, y, 4.3, 0.4, { fontSize: 14.5, bold: true, color: THEME.colors.accent1 });
    text(s, t, 8.5, y + 0.4, 4.3, 0.8, { fontSize: 12, color: THEME.colors.dk2 });
  });
}

// ══════════════ 9. 1장 요약 자세히 ══════════════
{
  const s = content('「1장 요약」 안쪽 : 설계사가 첫 3분에 말할 것', '타일 → 첫 해 조건 → 3층 구조 → Key Point 8개. 이 한 쪽만 들고도 상담이 시작됩니다', '결과물');
  pic(s, 'crop_tiles.png', M, 1.85, 7.6, 2.25);
  pic(s, 'crop_firstyear.png', M, 4.35, 7.6, 2.3);
  const b = [['갈래 색이 곧 장 색', '암은 빨강, 뇌·심장은 파랑, 수술비는 초록, 입원·간병은 주황, 상해·기타는 회색. 본문 장 머리띠도 같은 색입니다.'],
             ['「읽은 것만」 세는 원칙', '면책 4건 · 1년 미만 감액 5건 · 90일 미만 0건은 설명문에서 실제로 읽힌 담보만 센 숫자입니다. 설명문이 없는 샘플에서는 0으로 나오고, 그 사실을 옆에 적습니다.'],
             ['Key Point 칩 8개', '전체 Key Point 중 8개를 칩으로 미리 보여 주고, 본문 오른쪽 점선 상자에서 자세히 설명합니다.']];
  b.forEach(([h, t], i) => {
    const y = 1.9 + i * 1.6;
    icon(s, 'check', 'g', 8.5, y + 0.02, 0.3);
    text(s, h, 8.9, y, 3.9, 0.4, { fontSize: 14.5, bold: true });
    text(s, t, 8.9, y + 0.42, 3.9, 1.1, { fontSize: 12, color: THEME.colors.dk2 });
  });
}

// ══════════════ 10. 용어 풀이 · 상품 한눈에 ══════════════
{
  const s = content('용어 풀이 · 상품 한눈에 보기', '고객에게 쓰는 말부터 통일합니다 — 본문에 나오는 용어 17개를 한 쪽에', '결과물');
  pic(s, 'page_03.png', M, 1.85, 3.5, 4.95);
  const b = [['bulb', '용어 17개를 「고객 말」로', '유사암 · 암보장개시일 · 통합치료비 · 비급여 · 전액본인부담 · 산정특례 … 한 줄 정의로. 설계사마다 다르던 설명이 같아집니다.'],
             ['doc', '상품 한눈에 보기', '상품명 · 피보험자 · 계약사항 · 월 보험료 · 가입담보(갈래별 건수) · 특약 마스터 매칭 결과. 어느 약관으로 읽었는지 적어 둡니다.'],
             ['chat', '이 가이드 읽는 법', '왼쪽은 설계서의 담보명·금액과 약관 요약 설명문, 오른쪽은 Key Point. 「추정한 코드·금액은 없다」는 문장이 매 가이드에 들어갑니다.'],
             ['layers', '세 층으로 설명하면 쉽습니다', '진단비 → 치료비 → 입원일당의 3층 구조를 상담 틀로 제안합니다.']];
  b.forEach(([ic, h, t], i) => {
    const y = 1.9 + i * 1.22;
    icon(s, ic, 'b', 4.55, y + 0.02, 0.34, THEME.colors.accent3);
    text(s, h, 5.2, y, 7.5, 0.4, { fontSize: 14.5, bold: true });
    text(s, t, 5.2, y + 0.42, 7.5, 0.75, { fontSize: 12, color: THEME.colors.dk2 });
  });
}

// ══════════════ 11. 담보 지도 ══════════════
{
  const s = content('담보 지도 : 갈래별 담보 · 면책·감액 · 가입금액', '설계서의 긴 담보 목록을 갈래별로 다시 묶고, 가운데에 면책·감액 조건을 세웁니다', '결과물');
  pic(s, 'crop_map.png', M, 1.85, 7.3, 4.45);
  const b = [['가운데 칸 = 면책 · 감액', '「면책 90일」 「1년 미만 50%」 처럼 설명문에서 읽은 조건만 적습니다. 읽은 것이 없으면 빈 줄(—)로 두고 추정하지 않습니다.'],
             ['한 상자가 쪽을 넘지 않게', '24줄씩 끊어 「— 계속」 상자로 이어집니다. 글자가 지면 밖으로 밀리는 일이 없도록 자동 점검합니다.'],
             ['단위 만원 · 가입금액 큰 글씨', '고객이 묻는 「그래서 얼마짜리예요?」에 바로 답할 수 있게 오른쪽 끝에 굵게.']];
  b.forEach(([h, t], i) => {
    const y = 1.9 + i * 1.5;
    numdot(s, i + 1, 8.2, y + 0.02);
    text(s, h, 8.7, y, 4.1, 0.4, { fontSize: 14.5, bold: true });
    text(s, t, 8.7, y + 0.42, 4.1, 1.0, { fontSize: 12, color: THEME.colors.dk2 });
  });
  text(s, '※ 처음 설계에는 「최대 가입금액 막대」가 있었으나 현장 의견으로 빼고 면책·감액 칸으로 바꿨습니다.', M, 6.45, 12, 0.35, { fontSize: 10.5, color: THEME.colors.accent6 });
}

// ══════════════ 12. 갈래별 담보 해설 ══════════════
{
  const s = content('갈래별 담보 해설 : 왼쪽은 사실, 오른쪽은 말하는 법', '담보표(설계서·약관) + Key Point(상담 글 상자) + 자주 나오는 질문', '결과물');
  pic(s, 'crop_ridertable.png', M, 1.85, 5.9, 2.4);
  pic(s, 'crop_kpbox.png', 6.85, 1.85, 5.85, 2.4);
  pic(s, 'crop_faq.png', M, 4.9, 6.0, 1.2);
  badge(s, '왼쪽 : 담보명 · 가입금액 · 설명문 · 약관 별표 분류번호', M, 4.38, 5.9, THEME.colors.dk2, THEME.colors.lt2);
  badge(s, '오른쪽 : Key Point — 고객에게 이렇게 말합니다', 6.85, 4.38, 5.85);
  const b = [['분류번호는 약관 별표에서만', 'C44 · C73 처럼 코드와 이름을 함께 적고, 제외코드는 「(제외 : …)」로 표시합니다.'],
             ['같은 Key Point 는 한 번만', '세부보장이 여럿인 담보는 왼쪽에 쌓고 오른쪽 Key Point 는 한 번만 둡니다.'],
             ['자주 나오는 질문', '「갑상선암도 암진단비가 나오나요?」 같은 Q&A 를 장 끝에 붙입니다.']];
  b.forEach(([h, t], i) => {
    const y = 4.8 + i * 0.64;
    text(s, h, 6.95, y, 5.8, 0.3, { fontSize: 12.5, bold: true, color: THEME.colors.accent1 });
    text(s, t, 6.95, y + 0.3, 5.8, 0.3, { fontSize: 10.5, color: THEME.colors.dk2 });
  });
  text(s, '※ 담보 하나가 혼자 한 쪽을 넘기면(지급금액표가 긴 통합치료비) 설명문을 줄인 판으로 다시 그립니다.', M, 6.3, 6.0, 0.5, { fontSize: 10.5, color: THEME.colors.accent6 });
}

// ══════════════ 13. 면책·감액표 · 빈 자리 ══════════════
{
  const s = content('면책기간 / 감액기간 표와 빈 자리 채우기', '「언제 못 받는가」를 마지막에 한 표로 — 그리고 남는 여백은 연관 정보로', '결과물');
  pic(s, 'crop_exempt.png', M, 1.85, 7.6, 3.77);
  const b = [['shield', '면책 · 감액을 한 표로', '보장개시일(면책)과 「계약일부터 1년 미만 · 90일 미만 감액」을 담보별로. 설명문에서 읽은 담보만 싣고 나머지는 「조항 없음」이라고 적습니다.'],
             ['bulb', '가입 첫 해에 짚어 줄 세 가지', '① 암(유사암제외)은 90일 뒤부터 ② 1년 미만 50% 담보는 첫 해 절반 ③ 수술비·입원일당·유사암은 처음부터 100%.'],
             ['puzzle', '빈 자리 카드 25종', '「후유장해란」 「산정특례란」 같은 연관 설명 카드가 여백 크기에 맞춰 들어갑니다. 갈래가 맞는 카드부터, 그래도 남으면 공통 카드.']];
  b.forEach(([ic, h, t], i) => {
    const y = 1.9 + i * 1.55;
    icon(s, ic, 'b', 8.5, y + 0.02, 0.34, THEME.colors.accent3);
    text(s, h, 9.15, y, 3.65, 0.4, { fontSize: 14, bold: true });
    text(s, t, 9.15, y + 0.42, 3.65, 1.1, { fontSize: 11.5, color: THEME.colors.dk2 });
  });
  pic(s, 'page_20.png', M, 5.85, 0.75, 1.05, { frame: false });
  text(s, '뒷표지 : 「이 가이드는 이렇게 만들어졌습니다」(데이터 출처 · 생성 일자 · 원본 파일명)와 문의처(세일즈혁신TF)를 적어, 어떤 가이드북이든 근거를 되짚을 수 있습니다.', 1.5, 5.9, 6.7, 1.0, { fontSize: 11.5, color: THEME.colors.dk2 });
}

// ══════════════ 14. 데이터 원칙 ══════════════
pres.addSection({ title: '원칙과 구조' });
{
  const s = content('지키는 원칙 네 가지', '보험 설명 자료이기 때문에 「그럴듯함」보다 「근거」를 앞에 둡니다', '원칙과 구조');
  const p = [['ban', '추정하지 않는다', '질병코드와 금액은 약관 별표 · 특약 마스터 · 설계서에서만 옵니다. 목록이 없으면 빈칸으로 두고 그 사실을 적습니다. 오류가 「틀린 숫자」가 아니라 「빈칸」으로 나타나게.'],
             ['lock', 'PC 밖으로 나가지 않는다', '설계서에는 고객 · 설계사 정보가 있습니다. 파일은 브라우저 안에서만 읽히고 어떤 서버로도 보내지 않습니다. 인터넷이 끊겨도 됩니다.'],
             ['scale', '약관이 맞다', '규칙표와 마스터가 서로 달라 보이면 약관 원문이 기준입니다. 같은 이름의 특약은 상품이 달라도 같은 별표를 씁니다(소유자 확인).'],
             ['sync', '세 산출물이 함께 간다', '세일즈북 · 스마트 제안서 · 영업지원도구가 같은 특약 마스터를 씁니다. 약관이 바뀌면 명령 하나로 셋이 같이 갱신됩니다.']];
  p.forEach(([ic, h, t], i) => {
    const x = M + (i % 2) * 6.15, y = 1.95 + Math.floor(i / 2) * 2.45;
    card(s, x, y, 5.95, 2.25, { fill: 'FFFFFF', line: THEME.colors.lt2, shadow: true });
    icon(s, ic, 'b', x + 0.45, y + 0.42, 0.42, THEME.colors.accent3);
    text(s, h, x + 1.3, y + 0.35, 4.4, 0.45, { fontSize: 17, bold: true });
    text(s, t, x + 1.3, y + 0.85, 4.4, 1.3, { fontSize: 12, color: THEME.colors.dk2, lineSpacingMultiple: 1.2 });
  });
}

// ══════════════ 15. 지원 상품 · 데이터 흐름 ══════════════
{
  const s = content('지원 상품 8개와 데이터 흐름', '원천은 약관입니다 — 약관 PDF 를 읽어 특약 마스터를 만들고, 그 마스터를 세 도구가 함께 씁니다', '원칙과 구조');
  const prods = ['통합간편건강보험(3종 심사형)', '케어프리보험 M-Basket', '또 걸려도 또 받는 암보험', '또 걸려도 또 받는 간편한 암보험', '내Mom대로 보장보험', '내Mom같은 어린이보험', '간편31 건강보험', 'The건강한 내Mom대로 5.10.5 외 3종*'];
  card(s, M, 1.9, 5.6, 4.95, { fill: THEME.colors.lt2 });
  text(s, '내장 특약 마스터', M + 0.3, 2.1, 5, 0.4, { fontSize: 15, bold: true });
  prods.forEach((p, i) => {
    const y = 2.6 + i * 0.5;
    icon(s, 'check', 'b', M + 0.3, y + 0.03, 0.26);
    text(s, p, M + 0.7, y, 4.7, 0.4, { fontSize: 12.5, color: THEME.colors.dk1, valign: 'middle' });
  });
  text(s, '* The건강한 5.10.5 · The좋은 내Mom대로 · The가벼운 간편355 (2026-10 추가)', M + 0.3, 6.5, 5.1, 0.3, { fontSize: 10, color: THEME.colors.accent6 });
  // 흐름도
  const fx = 6.75;
  const boxes = [['doc', '약관 PDF\n(저장소 루트)', THEME.colors.lt2, THEME.colors.dk1], ['sync', '특약 마스터\n질병코드 · 제외코드 · 수가코드', THEME.colors.accent1, 'FFFFFF']];
  boxes.forEach(([ic, t, bg, col], i) => {
    const y = 1.9 + i * 1.5;
    card(s, fx, y, 6.0, 1.15, { fill: bg });
    icon(s, ic, i ? 'w' : 'b', fx + 0.3, y + 0.36, 0.42);
    text(s, t, fx + 0.95, y + 0.15, 4.9, 0.9, { fontSize: 13.5, bold: true, color: col, valign: 'middle' });
  });
  text(s, '▼', fx + 2.85, 3.05, 0.3, 0.3, { fontSize: 12, color: THEME.colors.accent6, align: 'center' });
  text(s, '▼', fx + 2.85, 4.55, 0.3, 0.3, { fontSize: 12, color: THEME.colors.accent6, align: 'center' });
  const outs = [['book', '세일즈북 생성기', '이 덱의 주제'], ['doc', '스마트 제안서', '설계서에 보장 지면 삽입'], ['search', '영업지원도구', '특약검색 · 시뮬레이터']];
  outs.forEach(([ic, h, t], i) => {
    const x = fx + i * 2.05;
    card(s, x, 4.9, 1.9, 1.95, { fill: 'FFFFFF', line: THEME.colors.lt2, shadow: true });
    icon(s, ic, 'b', x + 0.72, 5.1, 0.42);
    text(s, h, x + 0.1, 5.65, 1.7, 0.4, { fontSize: 12.5, bold: true, align: 'center' });
    text(s, t, x + 0.1, 6.05, 1.7, 0.7, { fontSize: 10.5, color: THEME.colors.dk2, align: 'center' });
  });
}

// ══════════════ 16. 기대 효과 ══════════════
pres.addSection({ title: '효과와 다음' });
{
  const s = content('기대 효과', '정량 효과는 가정값으로 산출했습니다 — 시범 운영에서 실측으로 바꿉니다', '효과와 다음');
  card(s, M, 1.9, 6.0, 4.95, { fill: THEME.colors.accent3 });
  text(s, '정량 효과 (연환산 · 가정값)', M + 0.3, 2.1, 5.4, 0.4, { fontSize: 15, bold: true, color: THEME.colors.accent2 });
  s.addText([{ text: '약 4.6억원', options: { fontSize: 40, bold: true, color: THEME.colors.accent1 } }, { text: '  / 년', options: { fontSize: 16, color: THEME.colors.dk2 } }],
    { x: M + 0.3, y: 2.55, w: 5.4, h: 0.9, isTextBox: true, margin: 0, valign: 'middle', objectName: nm('big') });
  const rows = [['A. 본사 가이드북 제작', '수작업 16h → 검수 2h · 연 20건 × 14h × 5만원', '1,400만원'],
                ['B. 설계사 상담 준비', '건당 30분 → 5분 · 300명 × 월 10건 × 12개월 × 25분 × 3만원/h', '4억5,000만원']];
  rows.forEach(([h, t, v], i) => {
    const y = 3.6 + i * 1.3;
    text(s, h, M + 0.3, y, 3.9, 0.35, { fontSize: 13, bold: true });
    text(s, t, M + 0.3, y + 0.35, 3.9, 0.8, { fontSize: 11, color: THEME.colors.dk2 });
    text(s, v, M + 3.6, y, 2.1, 0.5, { fontSize: 14, bold: true, color: THEME.colors.accent1, align: 'right' });
  });
  text(s, '※ 시간 · 인원 · 단가는 모두 가정값. 산출식은 공모 양식 「정량 산출 로직」에 그대로 적었습니다.', M + 0.3, 6.35, 5.4, 0.45, { fontSize: 10, color: THEME.colors.dk2 });
  const q = [['users', '설명의 표준화', '같은 상품을 어느 설계사가 설명해도 같은 용어 · 같은 Key Point · 같은 면책 안내. 불완전판매 소지가 줄어듭니다.'],
             ['heart', '고객 경험', '고객별 설계안에 맞춘 「내 가이드북」. 담보 나열이 아니라 왜 이 담보인지, 언제 받는지가 적힌 한 권.'],
             ['bolt', '신상품 대응 속도', '약관이 올라오면 마스터를 다시 뽑는 것으로 끝. 신상품 · 개정 당일 가이드북이 가능합니다.'],
             ['chart', '본사 자원 재배치', '편집 노동 대신 Key Point 창고 · 용어 풀이 등 「내용」을 다듬는 데 시간을 씁니다.']];
  q.forEach(([ic, h, t], i) => {
    const y = 1.9 + i * 1.25;
    icon(s, ic, 'b', 7.0, y + 0.02, 0.34, THEME.colors.lt2);
    text(s, h, 7.65, y, 5.1, 0.38, { fontSize: 14, bold: true });
    text(s, t, 7.65, y + 0.4, 5.1, 0.8, { fontSize: 11.5, color: THEME.colors.dk2 });
  });
}

// ══════════════ 16-2. 제언 : MeAI 리포트 생성과 잇기 ══════════════
{
  const s = content('제언 : MeAI 리포트 생성과 잇는다', '이 생성기는 MeAI 고도화를 위한 선행 과제로 만들었습니다 — 여기서 만든 데이터와 조립 틀을 MeAI 리포트의 재료로 씁니다', '효과와 다음');
  // 왼쪽 : 지금 MeAI 리포트가 어려운 점 → 생성기가 가진 것
  card(s, M, 1.9, 5.7, 4.45, { fill: THEME.colors.lt2 });
  text(s, 'MeAI 가 설계 리포트를 쓸 때 막히는 곳', M + 0.3, 2.1, 5.1, 0.4, { fontSize: 15, bold: true });
  const gaps = [['근거', '어떤 담보가 어느 질병코드를 보장하는지 — 약관 별표를 모르면 그럴듯한 추정이 섞인다'],
                ['입력', '설계서 PDF 를 그대로 주면 담보명 · 금액 · 설명문이 섞여 들어가 구조를 잃는다'],
                ['출력', '답은 글인데 설계사가 원하는 것은 고객 앞에 놓을 「지면」이다'],
                ['검증', '생성된 글이 약관과 맞는지 확인할 장치가 없다']];
  gaps.forEach(([h, t], i) => {
    const y = 2.6 + i * 0.92;
    badge(s, h, M + 0.3, y + 0.02, 0.9, THEME.colors.accent4, 'FFECEC');
    text(s, t, M + 1.35, y, 4.0, 0.85, { fontSize: 11.5, color: THEME.colors.dk2 });
  });
  // 오른쪽 : 생성기가 MeAI 에 넘겨 줄 네 가지
  const give = [['layers', '특약 마스터 4,338건', '질병코드 · 제외코드 · 수가코드가 붙은 약관 데이터와 Key Point · 용어 창고를 MeAI 지식 자료로 연결 → 리포트 문장에 「약관 별표 ○○」 근거가 붙는다'],
                ['upload', '설계서 읽기 · 갈래 분류', '설계서 PDF → 담보 · 금액 · 설명문 · 면책감액 조건이 정리된 구조 데이터. MeAI 는 이것을 입력으로 받아 고객 맞춤 서술만 맡는다'],
                ['book', '지면 조립 틀', 'MeAI 가 쓴 문장을 Key Point 상자 자리에 넣으면 그대로 20쪽 PDF. 표지 · 요약 · 담보 지도 · 면책감액표는 생성기가 채운다'],
                ['shield', '검증 장치', '「추정하지 않는다」 규칙 · 약관 분류번호 대조 · 회귀 점검을 MeAI 출력에도 적용 → 틀린 숫자 대신 빈칸과 사유']];
  give.forEach(([ic, h, t], i) => {
    const y = 1.9 + i * 1.25;
    icon(s, ic, 'b', 6.75, y + 0.05, 0.34, THEME.colors.accent3);
    text(s, h, 7.4, y, 5.3, 0.38, { fontSize: 14, bold: true });
    text(s, t, 7.4, y + 0.4, 5.3, 0.8, { fontSize: 11.5, color: THEME.colors.dk2 });
  });
  text(s, '단계 제안 : ① 지금 — 오프라인 생성기로 현장 검증  ② 프롬프트 라이브러리 · 특약검색기의 「MeAI 프롬프트 자동 생성」과 연결  ③ MeAI 리포트 생성에 특약 마스터 · 조립 틀 연동', M, 6.5, 12.1, 0.45, { fontSize: 11, color: THEME.colors.accent2 });
  s.addNotes('MeAI 리포트 생성 기능의 세부는 담당 부서와 맞춰야 한다. 여기서는 생성기가 넘겨 줄 수 있는 네 가지(데이터 · 입력 구조화 · 출력 틀 · 검증)를 제안한다.');
}

// ══════════════ 17. 다음 단계 · 문의 ══════════════
{
  const s = content('다음 단계', '프로토타입은 완성돼 있습니다 — 이제 현장에서 써 보고 내용을 키울 차례', '효과와 다음');
  const steps = [['① 시범 운영', '세일즈혁신TF 인접 조직 설계사 30명 · 4주. 생성 시간 · 매칭률 · 상담 활용도를 실측해 가정값을 대체합니다.'],
                 ['② Key Point 창고 확장', '36종 → 상품별 주요 특약 전부. 현장에서 「이 담보 설명이 아쉽다」는 의견을 창고에 바로 반영합니다.'],
                 ['③ 전 상품 확대 · MeAI 연동 준비', '판매 중 상품 약관을 순차 추가하고, 특약 마스터 · 조립 틀을 MeAI 리포트 생성에 넘길 수 있는 형태로 정리합니다(앞 쪽 제언).'],
                 ['④ 배포 방식 정비', '사내 메일 첨부 가능한 단일 파일 유지, 또는 사내 포털 게시. 버전 · 데이터 일자는 파일 안에 찍힙니다.']];
  steps.forEach(([h, t], i) => {
    const x = M + (i % 2) * 6.15, y = 1.95 + Math.floor(i / 2) * 1.85;
    card(s, x, y, 5.95, 1.65, { fill: THEME.colors.lt2 });
    text(s, h, x + 0.3, y + 0.22, 5.4, 0.4, { fontSize: 15, bold: true, color: THEME.colors.accent1 });
    text(s, t, x + 0.3, y + 0.65, 5.4, 0.95, { fontSize: 12, color: THEME.colors.dk2 });
  });
  card(s, M, 5.85, 12.1, 1.0, { fill: THEME.colors.accent1 });
  icon(s, 'chat', 'w', M + 0.3, 6.14, 0.42);
  text(s, '문의 · 수정 요청 : 세일즈혁신TF 이헌수 (AI추진파트)', M + 0.95, 5.95, 7, 0.45, { fontSize: 15, bold: true, color: 'FFFFFF' });
  text(s, '담보 설명이 약관과 다르거나 Key Point 를 보태고 싶을 때는 담보명과 함께 알려 주세요.', M + 0.95, 6.4, 11, 0.4, { fontSize: 12, color: 'D6E6FF' });
}

(async () => {
  const out = 'salesbook-generator-guide.pptx';
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('written', out);
})();
