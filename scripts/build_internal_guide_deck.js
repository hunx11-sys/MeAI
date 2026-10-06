// 세일즈북 자동 생성기 부서 내부 공유용 사용 가이드(PPT) 조립 스크립트 — 캡처(shots/)·아이콘(icons/)은 세션 작업폴더에서 만들어 썼다. 재조립 : NODE_PATH=node_modules node build_internal_guide_deck.js
// 세일즈북 자동 생성기 — 부서 내부 공유용 사용 가이드 · 기획 취지 (담백한 판)
const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/d9a1f0fe-3185-43c1-bc3d-15404e2e2f87_522276b5-baa1-4dab-b0a1-db621f094787/pptx/scripts/apply_theme.js');

const SH = 'shots/'; const IC = 'icons/';
const THEME = {
  name: 'Plain Guide', headFontFace: 'Malgun Gothic', bodyFontFace: 'Malgun Gothic',
  colors: { dk1: '191F28', lt1: 'FFFFFF', dk2: '4E5968', lt2: 'F4F5F7', accent1: '334155', accent2: '990011', accent3: 'E9EDF2',
            accent4: 'B91C1C', accent5: '0F766E', accent6: '8B95A1', hlink: '334155', folHlink: '334155' } };
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = '세일즈북 자동 생성기 — 사용 가이드 및 기획 취지 (부서 내부 공유용)'; pres.author = '세일즈혁신TF'; pres.company = 'Meritz';
const W = 13.333, M = 0.7;
const K = THEME.colors;

pres.defineSlideMaster({ title: 'CONTENT', background: { color: 'FFFFFF' }, objects: [
  { placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.45, w: W - 2 * M, h: 0.7, fontSize: 24, bold: true, color: K.dk1, margin: 0, valign: 'top', align: 'left' }, text: '제목' } },
  { placeholder: { options: { name: 'lead', type: 'body', x: M, y: 1.08, w: W - 2 * M, h: 0.45, fontSize: 13, color: K.dk2, margin: 0, valign: 'top', align: 'left' }, text: '' } },
  { text: { text: '세일즈북 자동 생성기 · 사용 가이드 및 기획 취지 · 세일즈혁신TF · 부서 내부 공유용', options: { x: M, y: 7.05, w: 9, h: 0.3, fontSize: 9, color: K.accent6, margin: 0 } } },
], slideNumber: { x: W - M - 0.8, y: 7.05, w: 0.8, h: 0.3, fontSize: 9, color: K.accent6, align: 'right' } });
pres.defineSlideMaster({ title: 'PLAIN', background: { color: 'FFFFFF' }, objects: [] });

let n = 0; const nm = p => `${p}-${++n}`;
const text = (s, t, x, y, w, h, o = {}) => s.addText(t, Object.assign({ x, y, w, h, isTextBox: true, margin: 0, fontSize: 13, color: K.dk1, valign: 'top', objectName: nm('t') }, o));
const box = (s, x, y, w, h, fill = K.lt2) => s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: nm('b') });
const rule = (s, x, y, w, col = 'D1D6DB') => s.addShape(pres.ShapeType.line, { x, y, w, h: 0, line: { color: col, width: 0.75 }, objectName: nm('r') });
const pic = (s, f, x, y, w, h) => { s.addShape(pres.ShapeType.rect, { x: x - 0.03, y: y - 0.03, w: w + 0.06, h: h + 0.06, fill: { color: 'FFFFFF' }, line: { color: 'D1D6DB', width: 0.75 }, objectName: nm('f') }); s.addImage({ path: SH + f, x, y, w, h, objectName: nm('p') }); };
const icon = (s, k, x, y, size = 0.34) => s.addImage({ path: `${IC}${k}_k.png`, x, y, w: size, h: size, objectName: nm('i') });
function table(s, rows, x, y, w, colW, o = {}) {
  const head = rows[0].map(t => ({ text: t, options: { bold: true, color: K.dk1, fill: { color: K.lt2 }, fontSize: o.fs || 11.5, valign: 'middle' } }));
  const body = rows.slice(1).map(r => r.map((t, i) => ({ text: t, options: { color: i === 0 && o.boldFirst ? K.dk1 : K.dk2, bold: i === 0 && o.boldFirst, fontSize: o.fs || 11.5, valign: 'middle' } })));
  s.addTable([head, ...body], { x, y, w, colW, border: { type: 'solid', color: 'E5E8EB', pt: 0.75 }, margin: 0.06, fontFace: 'Malgun Gothic', autoPage: false, objectName: nm('tbl'), rowH: o.rowH });
}
function content(title, lead, sec) { const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: sec }); s.addText(title, { placeholder: 'title' }); if (lead) s.addText(lead, { placeholder: 'lead' }); return s; }
const numbered = (s, k, x, y) => { s.addShape(pres.ShapeType.ellipse, { x, y, w: 0.32, h: 0.32, fill: { color: K.accent1 }, line: { color: K.accent1, width: 0 }, objectName: nm('d') }); text(s, String(k), x, y, 0.32, 0.32, { fontSize: 11, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' }); };

// 1. 표지
pres.addSection({ title: '시작' });
{
  const s = pres.addSlide({ masterName: 'PLAIN', sectionTitle: '시작' });
  text(s, '세일즈혁신TF  ·  부서 내부 공유용', M, 1.6, 8, 0.4, { fontSize: 13, color: K.dk2 });
  text(s, '세일즈북 자동 생성기', M, 2.1, 9, 0.9, { fontSize: 40, bold: true });
  text(s, '사용 가이드 및 기획 취지', M, 3.0, 9, 0.6, { fontSize: 24, color: K.dk2 });
  rule(s, M, 3.9, 5.5, K.dk1);
  text(s, '상품설명서(설계서) PDF 를 넣으면 담보표 · 설명문 · Key Point · 면책감액표를 묶은\n컨설팅 가이드북을 만들어 주는 오프라인 HTML 도구입니다.', M, 4.1, 8.5, 0.9, { fontSize: 14, color: K.dk2 });
  text(s, '2026년 10월  ·  생성기 빌드 2026-10-02  ·  특약 마스터 4,338건  ·  Key Point 36종', M, 6.5, 9, 0.4, { fontSize: 11, color: K.accent6 });
  pic(s, 'page_01.png', 9.6, 1.5, 3.1, 4.4);
}
// 2. 이 문서는
{
  const s = content('이 문서는', '처음 쓰는 분은 1부부터, 배경이 궁금한 분은 2부부터 읽으면 됩니다', '시작');
  const parts = [['1부  사용 가이드', '3 ~ 9쪽', '준비물 · 파일 넣기 · 상태창 읽는 법 · 옵션 · 인쇄와 PDF 저장 · 결과물 읽는 법'],
                 ['2부  기획 취지', '10 ~ 12쪽', '왜 만들었나 · 무엇을 만들었나 · 지키는 원칙 · 데이터는 어디서 오나'],
                 ['3부  자주 묻는 질문 · 문의', '13 ~ 14쪽', '담보가 적게 읽힐 때 · 글자가 깨질 때 · 지원 상품 밖일 때 · 개인정보 · 갱신 방법']];
  parts.forEach(([h, p, b], i) => {
    const y = 1.9 + i * 1.5;
    box(s, M, y, 11.9, 1.25);
    text(s, h, M + 0.3, y + 0.22, 4.2, 0.4, { fontSize: 16, bold: true });
    text(s, p, M + 0.3, y + 0.68, 4.2, 0.35, { fontSize: 11.5, color: K.accent6 });
    text(s, b, M + 4.6, y + 0.22, 7.0, 0.9, { fontSize: 13, color: K.dk2, valign: 'middle' });
  });
  text(s, '읽는 데 10분이면 충분합니다. 생성기 파일(guidebook_proto.html)은 메일에 함께 붙어 있습니다.', M, 6.5, 11.9, 0.4, { fontSize: 12, color: K.dk2 });
}

// ── 1부 사용 가이드 ──
pres.addSection({ title: '1부 사용 가이드' });
{
  const s = content('1. 준비물과 실행 환경', '설치할 것은 없습니다. 파일 하나와 브라우저면 됩니다', '1부 사용 가이드');
  table(s, [['항목', '내용', '비고'],
            ['생성기 파일', 'guidebook_proto.html (약 4.7MB) 1개', '메일 첨부 또는 저장소 docs/ 폴더. 바탕화면 등 아무 곳에 두고 더블클릭'],
            ['브라우저', '크롬 또는 엣지(최신판)', '인터넷 연결 불필요. 사내 폐쇄망 · 외근 노트북에서도 동작'],
            ['넣을 파일', '고객 상품설명서(설계서) PDF', '「가입담보」 표와 뒤쪽 「가입담보 및 보장내용」 설명문이 들어 있는 통상의 설계서'],
            ['지원 상품', '아래 8개 상품 계열', '그 밖의 상품은 담보명은 읽히지만 약관 분류번호 · Key Point 가 비어 나옵니다'],
            ['출력', '브라우저 인쇄 → PDF 저장 또는 종이 인쇄', 'A4 세로 · 20쪽 안팎']],
        M, 1.8, 11.9, [1.8, 4.1, 6.0], { boldFirst: true });
  text(s, '지원 상품 8개', M, 4.7, 4, 0.35, { fontSize: 13, bold: true });
  const prods = ['통합간편건강보험(세만기형) · 일반 / 통합간편 / 355 심사형', '케어프리보험 M-Basket', '또 걸려도 또 받는 암보험 · 간편한 암보험', '내Mom대로 보장보험 · 내Mom같은 어린이보험',
                 '간편31 건강보험', 'The건강한 내Mom대로 5.10.5 · The건강한 5.10.5', 'The좋은 내Mom대로 보장보험', 'The가벼운 간편355건강보험'];
  prods.forEach((p, i) => text(s, '·  ' + p, M + (i % 2) * 6.0, 5.1 + Math.floor(i / 2) * 0.36, 5.8, 0.34, { fontSize: 11.5, color: K.dk2 }));
}
{
  const s = content('2. 파일 열기와 설계서 넣기', '생성기 파일을 열면 왼쪽에 조작부, 오른쪽에 빈 미리보기가 보입니다', '1부 사용 가이드');
  pic(s, 'crop_panel_start.png', M, 1.8, 3.4, 4.87);
  const steps = [['생성기 파일을 더블클릭해 엽니다', '브라우저가 열리며 「세일즈혁신 가이드북 생성기」 화면이 나옵니다. 처음 열 때 글꼴 · 데이터를 읽느라 2~3초 걸릴 수 있습니다.'],
                 ['설계서 PDF 를 점선 상자에 끌어다 놓습니다', '탐색기에서 PDF 를 끌어 점선 상자 위에 놓거나, 상자를 클릭해 파일을 고릅니다. 한 번에 한 파일입니다.'],
                 ['설계서가 없으면 샘플 버튼을 누릅니다', '「샘플 ① 통합간편」 「샘플 ② 내Mom대로 5.10.5」 두 개가 들어 있어 결과물 모양을 먼저 볼 수 있습니다. 샘플은 설명문이 없어 설명문 칸이 비어 나옵니다.'],
                 ['30초~1분 기다립니다', '쪽수가 많은 설계서(30~40쪽)는 「읽는 중 … 10/36쪽」처럼 진행이 표시됩니다. 끝나면 오른쪽에 가이드북이 그려집니다.']];
  steps.forEach(([h, b], i) => {
    const y = 1.85 + i * 1.2;
    numbered(s, i + 1, 4.5, y + 0.02);
    text(s, h, 4.95, y, 7.6, 0.4, { fontSize: 14, bold: true });
    text(s, b, 4.95, y + 0.4, 7.6, 0.75, { fontSize: 12, color: K.dk2 });
  });
  text(s, '파일은 브라우저 안에서만 읽힙니다. 어떤 서버로도 올라가지 않으므로 고객 정보가 든 설계서를 그대로 써도 됩니다.', 4.5, 6.65, 8.1, 0.4, { fontSize: 11.5, color: K.accent2 });
}
{
  const s = content('3. 상태창 읽는 법', '생성이 끝나면 상태창에 무엇을 몇 건 읽었는지 적힙니다. 이 숫자로 결과를 믿어도 되는지 판단합니다', '1부 사용 가이드');
  pic(s, 'crop_status.png', M, 1.8, 5.3, 2.53);
  table(s, [['상태창 줄', '뜻', '이럴 때 확인'],
            ['총 N쪽 · 글자 추출 완료', '설계서 PDF 에서 글자를 다 읽었다', '0쪽이거나 오류면 스캔 이미지 PDF 일 수 있음(글자 없는 PDF 는 못 읽음)'],
            ['상품 : …', '첫 쪽에서 읽은 정식 상품명', '상품명이 이상하면 설계서 첫 쪽 표기가 다른 것. 「가이드 제목」에 직접 적으면 표지에 그 이름이 쓰임'],
            ['담보 N건', '가입담보 표에서 읽은 담보 수', '설계서 담보 수보다 크게 적으면 표 형식이 다른 설계서. 세일즈혁신TF 에 PDF 와 함께 알려 주세요'],
            ['특약 마스터 매칭 N건 (○○ 우선)', '약관 분류번호를 붙인 담보 수와 기준 약관', '매칭 수가 담보 수보다 적으면 그 담보는 분류번호 · Key Point 없이 이름만 실림'],
            ['설명문 읽힘 N건', '설계서 뒤쪽 설명문을 붙인 담보 수', '0건이면 설계서에 「가입담보 및 보장내용」이 없는 것. 설명문 · 면책감액표가 빈칸'],
            ['가이드북 N쪽 생성 완료 · 빈 자리 카드 N장', '만들어진 쪽수와 여백에 넣은 연관 정보 카드 수', '「한 쪽을 넘겨 잘린 블록」 문구가 있으면 그 쪽을 확인하고 알려 주세요']],
        6.3, 1.8, 6.35, [1.9, 1.95, 2.5], { fs: 10 });
  text(s, '마스터에 없는 담보가 있으면 「마스터에 없는 담보(N) : …」로 이름이 그대로 나열됩니다. 이 목록이 다음 데이터 보강 대상입니다.', M, 4.6, 5.3, 0.8, { fontSize: 12, color: K.dk2 });
  text(s, '매칭 기준 약관(「○○ 우선」)은 첫 쪽 상품명으로 자동 판별합니다. 같은 이름의 특약이라도 상품마다 약관이 다를 수 있어, 설계 상품의 약관 레코드를 먼저 찾고 없을 때만 다른 상품의 같은 이름 특약을 씁니다.', M, 5.45, 5.3, 1.2, { fontSize: 12, color: K.dk2 });
}
{
  const s = content('4. 옵션 세 개와 가이드 제목', '기본값으로 두면 됩니다. 상황에 따라 끄는 경우만 적습니다', '1부 사용 가이드');
  table(s, [['옵션', '켜면(기본)', '끄면 · 언제 끄나'],
            ['Key Point 가 없는 담보도 싣기', '설계서의 모든 담보가 갈래별 해설에 실린다(Key Point 상자 없이 담보표만)', '주요 담보만 추려 얇게 만들고 싶을 때. 담보 지도에는 모든 담보가 그대로 남는다'],
            ['약관 별표 분류번호 표시', '담보표 아래에 「약관 별표 분류번호 : C44 기타 피부의 악성신생물 …」 줄이 붙는다', '고객용으로 가볍게 보일 때. 분류번호는 교육 · 검증용 성격이 강하다'],
            ['설계서 설명문 싣기', '설계서 뒤쪽 보장내용 설명문을 요약해 담보표 안에 싣고, 면책 · 감액 조건을 표로 뽑는다', '설명문이 깨져 읽힌 설계서일 때. 끄면 「설계서 설명문 없음」으로 표시되고 면책감액표가 비는 점을 알고 쓴다']],
        M, 1.8, 11.9, [2.6, 4.6, 4.7], { boldFirst: true });
  text(s, '가이드 제목', M, 4.75, 4, 0.35, { fontSize: 13, bold: true });
  text(s, '비워 두면 설계서의 정식 상품명이 표지에 들어갑니다. 상품명이 「(무)메리츠 The건강한 내Mom대로 5.10.5 보장보험2607(3.0)(해약환급금지급형)…」처럼 길어 표지가 답답하면 「The건강한 내Mom대로 5.10.5」처럼 짧게 적습니다. 정식 상품명은 표지 아래와 「상품 한눈에 보기」에 그대로 남습니다.', M, 5.1, 11.9, 0.9, { fontSize: 12, color: K.dk2 });
  text(s, '옵션이나 제목을 바꾼 뒤에는 「다시 만들기」를 누릅니다. 설계서를 다시 넣을 필요는 없습니다.', M, 6.1, 11.9, 0.4, { fontSize: 12, color: K.accent2 });
}
{
  const s = content('5. 인쇄와 PDF 저장', '브라우저 인쇄창 설정 세 가지만 맞추면 지면이 그대로 나옵니다', '1부 사용 가이드');
  table(s, [['인쇄창 항목', '값', '왜'],
            ['대상(프린터)', 'PDF로 저장  (종이는 사무실 프린터)', 'PDF 로 저장하면 메일 · 태블릿에서 그대로 열 수 있다'],
            ['용지 · 방향', 'A4 · 세로', '지면이 A4 세로 기준으로 그려져 있다'],
            ['여백', '없음', '기본값(보통)으로 두면 지면이 줄어들고 아래 잘린다'],
            ['배경 그래픽', '켬', '끄면 머리띠 · 카드 바탕색 · 점선 상자가 사라져 흰 바탕에 글자만 남는다'],
            ['머리글 · 바닥글', '끔', '브라우저가 날짜 · 파일 경로를 찍는 것을 막는다']],
        M, 1.8, 7.2, [1.6, 2.6, 3.0], { boldFirst: true });
  text(s, '자주 겪는 일', 8.3, 1.8, 4.3, 0.4, { fontSize: 14, bold: true });
  const faq = [['쪽이 21~22쪽으로 늘고 끝이 잘린다', '여백이 「없음」이 아닙니다. 여백을 없음으로 바꾸고 다시 인쇄창을 엽니다.'],
               ['바탕색 · 머리띠가 안 나온다', '「배경 그래픽」이 꺼져 있습니다(크롬은 「설정 더보기」 안에 있음).'],
               ['첫 쪽 위에 날짜 · 경로가 찍힌다', '「머리글 및 바닥글」을 끕니다.'],
               ['PDF 파일이 너무 크다', '글꼴이 내장되어 보통 2~5MB 입니다. 그 이상이면 인쇄창 「대상」이 프린터 드라이버의 PDF 가 아닌지 확인합니다.']];
  faq.forEach(([q, a], i) => { const y = 2.3 + i * 0.98; text(s, q, 8.3, y, 4.3, 0.35, { fontSize: 12, bold: true, color: K.dk1 }); text(s, a, 8.3, y + 0.36, 4.3, 0.65, { fontSize: 11, color: K.dk2 }); });
  text(s, '저장 파일명은 영문 · 숫자로 두는 편이 사내 메일 첨부와 윈도우 공유 폴더에서 탈이 없습니다. 예) guide_mom5105_40F_202610.pdf', M, 6.45, 11.9, 0.45, { fontSize: 11.5, color: K.dk2 });
}
{
  const s = content('6. 결과물 읽는 법 — 20쪽의 구성', '쪽 순서가 상담 순서입니다. 쪽마다 어디서 온 내용인지 함께 적습니다', '1부 사용 가이드');
  table(s, [['쪽', '내용', '어디서 온 데이터'],
            ['표지', '가이드 제목 · 정식 상품명 · 예시 설계(피보험자 · 나이 · 계약사항) · 가입담보 수 · 월 보험료 · Key Point 수', '설계서 첫 쪽 · 담보 목록 집계'],
            ['1장 요약', '상품 한 장 요약 · 5갈래 타일(건수 · 대표 담보 4개) · 가입 첫 해 조건 · 상담 3층 구조 · Key Point 칩 8개', '담보 목록 · 설명문에서 읽은 면책 · 감액'],
            ['용어 풀이 · 상품 한눈에', '본문에 나오는 용어 17개 한 줄 정의 · 상품 정보표 · 가이드 읽는 법', '내장 용어 창고 · 설계서'],
            ['담보 지도', '갈래별로 담보 · 면책감액 · 가입금액(만원) 표. 24줄마다 「— 계속」 상자', '담보 목록 · 설명문'],
            ['갈래별 담보 해설(1~5장)', '왼쪽 담보표(담보명 · 금액 · 설명문 요약 · 약관 별표 분류번호) · 오른쪽 Key Point · 장 끝 자주 나오는 질문', '설계서 · 특약 마스터(약관 별표) · Key Point 창고'],
            ['면책기간 / 감액기간', '보장개시일(면책)과 1년 미만 · 90일 미만 감액을 담보별 한 표로. 첫 해에 짚어 줄 세 가지', '설명문에서 읽은 것만'],
            ['빈 자리 카드', '여백이 남는 쪽에 그 갈래의 연관 정보 카드(후유장해란 · 산정특례란 등 25종)', '내장 카드 창고'],
            ['뒷표지', '이 가이드는 이렇게 만들어졌습니다(출처 · 생성 일자 · 원본 파일명) · 문의처', '생성기']],
        M, 1.8, 11.9, [2.1, 6.4, 3.4], { fs: 10.5, boldFirst: true });
}
{
  const s = content('7. 갈래별 담보 쪽을 뜯어 보면', '왼쪽은 「사실」, 오른쪽은 「말하는 법」입니다. 두 칸의 출처가 다릅니다', '1부 사용 가이드');
  pic(s, 'crop_ridertable.png', M, 1.8, 5.6, 2.28);
  pic(s, 'crop_kpbox.png', 6.65, 1.8, 6.0, 2.46);
  const L = [['담보명 · 가입금액 · 보험기간', '설계서 가입담보 표 그대로. 「2백만원 / 20년/100세」'],
             ['설명문 요약', '설계서 뒤쪽 보장내용 설명문을 380자 안으로 줄인 것. 지급금액표가 있으면 항목 · 금액 · 횟수 표로. ※ 뒤 노란 표시는 면책 · 감액 · 한도 문장'],
             ['약관 별표 분류번호', '특약 마스터(약관에서 뽑은 것)의 질병코드와 이름. 10개까지 보이고 나머지는 「외 N개」. 제외코드는 「(제외 : …)」']];
  const R = [['Key Point 상자', '담보 이름으로 창고(36종)에서 찾은 상담 글 상자. 같은 Key Point 를 쓰는 담보가 이어지면 왼쪽에 담보표를 쌓고 상자는 한 번만'],
             ['상담 포인트 — 자주 나오는 질문', '장마다 끝에 붙는 Q&A. 갈래별로 3개 안팎'],
             ['Key Point 가 없는 담보', '왼쪽 담보표만 실립니다(옵션으로 뺄 수 있음). 이 담보들이 Key Point 창고 보강 후보입니다']];
  L.forEach(([h, b], i) => { const y = 4.4 + i * 0.78; text(s, h, M, y, 5.6, 0.3, { fontSize: 12, bold: true }); text(s, b, M, y + 0.3, 5.6, 0.5, { fontSize: 10.5, color: K.dk2 }); });
  R.forEach(([h, b], i) => { const y = 4.4 + i * 0.78; text(s, h, 6.65, y, 6.0, 0.3, { fontSize: 12, bold: true }); text(s, b, 6.65, y + 0.3, 6.0, 0.5, { fontSize: 10.5, color: K.dk2 }); });
}

// ── 2부 기획 취지 ──
pres.addSection({ title: '2부 기획 취지' });
{
  const s = content('8. 왜 만들었나', '설계사가 고객 앞에서 쓰는 「한 권」을 사람이 만들고 있었습니다', '2부 기획 취지');
  const items = [['상품설명서는 나열이다', '담보명과 가입금액이 수십 줄 이어질 뿐, 왜 이 담보가 중요한지 · 언제 못 받는지(면책 90일, 1년 미만 50% 감액)는 적혀 있지 않습니다. 설계사가 머릿속에서 다시 조립해야 합니다.'],
                 ['약관은 수백~천 쪽이다', '질병코드 별표 · 감액 조건 · 수가코드는 약관 깊숙이 흩어져 있어 상담 중 열어 볼 수 없습니다. 기억에 의존하면 같은 상품을 설계사마다 다르게 설명하게 됩니다.'],
                 ['가이드북은 손으로 만든다', '본사가 상품별 가이드북을 수작업으로 편집해 일부 상품에만 있습니다. 상품 개정 · 신상품마다 처음부터 다시 만들어야 하고, 고객별 설계안에 맞춘 판은 없습니다.']];
  items.forEach(([h, b], i) => {
    const y = 1.9 + i * 1.45;
    text(s, h, M, y, 3.6, 0.5, { fontSize: 16, bold: true });
    text(s, b, 4.5, y, 8.1, 1.2, { fontSize: 12.5, color: K.dk2, lineSpacingMultiple: 1.2 });
    if (i < 2) rule(s, M, y + 1.25, 11.9);
  });
  box(s, M, 6.3, 11.9, 0.6, K.accent3);
  text(s, '그래서 「설계서 한 장을 넣으면 그 설계에 맞는 가이드북이 나오는 도구」를 만들었습니다. 수작업 초판(The건강한 내Mom대로 5.10.5 · 15쪽)을 먼저 만들어 모양을 정하고, 그 모양을 프로그램으로 옮겼습니다.', M + 0.25, 6.33, 11.4, 0.55, { fontSize: 12, color: K.dk1, valign: 'middle' });
}
{
  const s = content('9. 무엇을 만들었나', '네 단계로 동작하는 HTML 파일 하나입니다. 서버도 설치도 없습니다', '2부 기획 취지');
  const steps = [['설계서 읽기', '상품설명서 PDF 에서 담보명 · 가입금액 · 보장내용 설명문을 읽습니다. 줄바꿈으로 끊긴 긴 담보명도 이어 붙입니다.'],
                 ['특약 마스터 매칭', '8개 상품 약관에서 뽑은 특약 4,338건과 이름을 맞춰 약관 별표 분류번호 · 제외코드를 붙입니다. 설계 상품의 약관을 먼저 봅니다.'],
                 ['Key Point 결합', '상담 글 상자(36종) · 용어 풀이(17개) · 자주 묻는 질문을 담보에 맞게 끼워 넣고, 설명문에서 면책 · 감액 조건을 뽑아 표로 세웁니다.'],
                 ['지면 조립', '쪽 높이를 재 가며 블록을 배치해 글자가 지면을 넘지 않게 하고, 남는 여백에는 연관 정보 카드를 넣습니다. 쪽 머리띠에 장 이름 · 쪽수를 찍습니다.']];
  steps.forEach(([h, b], i) => {
    const x = M + i * 3.0;
    box(s, x, 1.9, 2.8, 3.1);
    numbered(s, i + 1, x + 0.25, 2.15);
    text(s, h, x + 0.25, 2.6, 2.3, 0.4, { fontSize: 14.5, bold: true });
    text(s, b, x + 0.25, 3.05, 2.3, 1.9, { fontSize: 11.5, color: K.dk2, lineSpacingMultiple: 1.2 });
  });
  pic(s, 'page_02.png', M, 5.2, 1.2, 1.7); pic(s, 'page_04.png', M + 1.35, 5.2, 1.2, 1.7); pic(s, 'page_08.png', M + 2.7, 5.2, 1.2, 1.7);
  text(s, '만든 것의 범위', 4.95, 5.2, 7.6, 0.35, { fontSize: 13, bold: true });
  text(s, '· 생성기 본체 : docs/guidebook_proto.html (pdf.js · 글꼴 · 아이콘 · 특약 마스터 · Key Point 창고를 한 파일에 내장)\n· 데이터 : 특약 마스터(db.json · db_terms_extra.json)는 특약검색기 데이터와 약관 PDF 에서 자동 추출. 스마트 제안서 · 영업지원도구와 같은 마스터를 씁니다\n· 글 상자 창고 : scripts/guidebook_kp.json (Key Point 36 · 용어 17 · 빈 자리 카드 25) — 내용을 보태면 생성기를 다시 조립해 반영', 4.95, 5.55, 7.65, 1.4, { fontSize: 11, color: K.dk2 });
}
{
  const s = content('10. 지키는 원칙과 데이터의 출처', '보험 설명 자료이므로 「그럴듯함」보다 「근거」를 앞에 둡니다', '2부 기획 취지');
  table(s, [['원칙', '구체적으로'],
            ['추정하지 않는다', '질병코드와 금액은 약관 별표 · 특약 마스터 · 설계서에서만 옵니다. 목록이 없으면 빈칸으로 두고 그 사실을 적습니다. 오류가 「틀린 숫자」가 아니라 「빈칸」으로 드러나게 합니다.'],
            ['PC 밖으로 나가지 않는다', '설계서는 브라우저 안에서만 읽히고 어떤 서버로도 보내지 않습니다. 인터넷이 끊겨도 동작합니다.'],
            ['약관이 기준이다', '규칙표와 마스터가 서로 달라 보이면 약관 원문이 맞습니다. 같은 이름의 특약은 상품이 달라도 같은 별표를 씁니다. 다르면 데이터 오류로 보고 약관으로 바로잡습니다.'],
            ['세 산출물이 함께 간다', '세일즈북 · 스마트 제안서 · 영업지원도구가 같은 특약 마스터를 씁니다. 약관이 바뀌면 명령 하나로 셋이 같이 갱신됩니다.']],
        M, 1.8, 6.4, [1.9, 4.5], { fs: 10.5, boldFirst: true });
  table(s, [['가이드북의 이 내용은', '여기서 옵니다'],
            ['담보명 · 가입금액 · 보험기간', '설계서 「가입담보」 표'],
            ['상품명 · 피보험자 · 계약사항 · 월 보험료', '설계서 첫 쪽'],
            ['설명문 요약 · 지급금액표', '설계서 뒤쪽 「가입담보 및 보장내용」'],
            ['면책 · 감액 조건', '위 설명문에서 읽은 문장(읽은 것만)'],
            ['약관 별표 분류번호 · 제외코드', '특약 마스터(약관 PDF 에서 추출 · 특약검색기 감수본)'],
            ['Key Point · 용어 풀이 · Q&A · 빈 자리 카드', '내장 글 상자 창고(세일즈혁신TF 작성)'],
            ['5갈래 분류 · 3층 구조', '담보명 규칙으로 자동 분류']],
        7.4, 1.8, 5.25, [2.6, 2.65], { fs: 10.5 });
  text(s, '한계도 적어 둡니다 : ① 8개 상품 밖은 분류번호 · Key Point 가 비어 나옵니다 ② 설명문이 없는 설계서는 면책감액표가 비어 나옵니다 ③ 지급액 계산은 하지 않습니다(그건 스마트 제안서의 몫) ④ Key Point 는 36종이라 담보의 절반 안팎에만 붙습니다 — 창고를 키우는 중입니다.', M, 6.0, 11.9, 0.9, { fontSize: 11.5, color: K.dk2 });
}

// ── 3부 FAQ · 문의 ──
pres.addSection({ title: '3부 자주 묻는 질문' });
{
  const s = content('11. 자주 묻는 질문', '', '3부 자주 묻는 질문');
  table(s, [['질문', '답'],
            ['담보가 설계서보다 적게 읽혔어요', '설계서 표 형식이 다른 경우입니다. 상태창 숫자와 함께 PDF 를 세일즈혁신TF 로 보내 주세요. 읽기 규칙을 보강합니다. 개인정보가 있으니 사내 메일로만.'],
            ['「마스터에 없는 담보」가 여럿 나와요', '그 담보는 이름만 실리고 분류번호 · Key Point 가 빠집니다. 지원 상품 8개 밖이거나, 지원 상품인데 담보명 표기가 약관과 다른 경우입니다. 목록을 알려 주시면 마스터를 보강합니다.'],
            ['설명문 칸이 전부 「설계서 설명문 없음」이에요', '설계서에 뒤쪽 「가입담보 및 보장내용」이 없거나(요약 설계서), 샘플 버튼으로 만든 경우입니다. 상세 설계서로 다시 넣으세요.'],
            ['고객에게 그대로 줘도 되나요', '지금 판은 「교육용 · 사내 자료」 표시가 찍힌 설계사용입니다. 고객 교부용으로 쓰려면 준법 검토 후 문구 · 표시를 바꾼 판을 따로 만들어야 합니다.'],
            ['회사 밖에서도 열리나요', '파일 하나라 어디서든 열립니다. 다만 설계서에는 고객 · 설계사 정보가 있으니 사외 PC 에서는 쓰지 않습니다.'],
            ['상품이 개정되면 어떻게 하나요', '세일즈혁신TF 가 약관을 받아 특약 마스터를 다시 뽑고 생성기 파일을 다시 배포합니다. 받는 분은 새 파일로 바꾸기만 하면 됩니다. 파일 안 「빌드 일자」로 판을 구분합니다.'],
            ['Key Point 내용을 고치고 싶어요', '담보명과 고칠 문장을 보내 주세요. 글 상자 창고(guidebook_kp.json)에 반영하고 다음 배포판에 넣습니다.']],
        M, 1.3, 11.9, [3.4, 8.5], { fs: 10.5, boldFirst: true });
}
{
  const s = content('12. 문의 · 피드백 · 버전', '', '3부 자주 묻는 질문');
  box(s, M, 1.4, 11.9, 1.4, K.accent3);
  text(s, '문의 · 수정 요청', M + 0.3, 1.6, 5, 0.4, { fontSize: 14, bold: true });
  text(s, '세일즈혁신TF 이헌수 (AI추진파트)\n담보 설명이 약관과 다르거나 Key Point 를 보태고 싶을 때는 「담보명 + 설계 상품 + 고칠 내용」을 함께 보내 주세요. 설계서 PDF 는 사내 메일로만.', M + 0.3, 2.0, 11.3, 0.8, { fontSize: 12, color: K.dk2 });
  text(s, '피드백으로 받고 싶은 것', M, 3.1, 6, 0.4, { fontSize: 14, bold: true });
  const fb = ['상담에서 실제로 쓴 쪽과 안 쓴 쪽 (쪽 번호로)', 'Key Point 가 틀렸거나 아쉬운 담보 (담보명으로)', '설계서를 넣었는데 담보 · 설명문이 덜 읽힌 사례 (상태창 숫자 + PDF)', '고객에게 설명할 때 더 있었으면 하는 용어 · Q&A'];
  fb.forEach((t, i) => text(s, '·  ' + t, M, 3.55 + i * 0.4, 6.2, 0.38, { fontSize: 12, color: K.dk2 }));
  table(s, [['항목', '값'], ['생성기 빌드', '2026-10-02'], ['특약 마스터', '4,338건 (8개 상품 · 약관 별표 질병코드 포함)'], ['Key Point 창고', '36종 · 용어 17개 · 빈 자리 카드 25종'], ['파일', 'docs/guidebook_proto.html · 약 4.7MB'], ['저장소', 'GitHub hunx11-sys/MeAI · main']],
        7.3, 3.1, 5.35, [1.6, 3.75], { fs: 10.5, boldFirst: true });
  text(s, '이 문서와 생성기 파일은 부서 내부 공유용입니다. 사외 반출 시 설계서 캡처(피보험자 · 설계사 정보)를 가립니다.', M, 6.5, 11.9, 0.4, { fontSize: 11, color: K.accent6 });
}

(async () => {
  const out = 'salesbook-generator-internal-guide.pptx';
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('written', out);
})();
