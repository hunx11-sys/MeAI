// PART 6 덧붙임 — 실제 MeAI 화면으로 따라 하기(2026.10, 소유자가 준 운영 화면 캡처 10장)
// MeAI 홈에서 시작하는 두 갈래(일반대화 · 맞춤대화)를 실제 화면 순서대로 따라간다. 쪽마다 맨 위에 'MeAI 홈에서 오는 길'.
// 캡처: captures/real (build/capture/prep_real.py — 주소창(접속 토큰) 잘라 냄 · 이름 가림 · 관리자 메뉴 지움 · 리포트 본문 흐림)
// PART 6 끝(모바일 쪽 뒤)에 붙어서 1~60쪽 번호는 그대로(공지 매뉴얼이 쓰는 쪽 번호 유지).
module.exports = (S, ctx) => {
  const { L, C, W, M, HERO, AG } = ctx;
  const REAL = n => AG('real', n);
  const P = { clip:{x:0,y:0}, dsf:1, d:0.34 };
  const IX = M, IY = 1.92, IW = 7.6, IH = 4.78;          // 실제 화면 자리(1531x963 ≒ 1.59:1)
  const RX = 8.62, RW = W - M - RX;                         // 오른쪽 설명 자리
  const kick = t => 'PART 6 · 실제 화면 따라 하기 · ' + t;
  // MeAI 홈에서 오는 길: 칩 › 칩 › … › [지금 화면]
  function crumbs(s, items, y = 1.3){
    L.T(s, 'MeAI 홈에서 오는 길', { x:M, y, w:1.75, h:0.32, fontSize:10.5, bold:true, color:C.g500, valign:'middle' });
    let x = M + 1.78;
    items.forEach((t, i) => { const last = i === items.length - 1, sz = 10.5, w = L.textW(t, sz) + 0.32;
      L.R(s, { x, y, w, h:0.32, fill: last ? C.navy : (i === 0 ? C.blue : C.blue50), line:null, radius:0.16 });
      L.T(s, t, { x, y, w, h:0.32, fontSize:sz, bold:true, color: (last || i === 0) ? 'FFFFFF' : C.blue, align:'center', valign:'middle' });
      x += w; if (!last){ L.T(s, '›', { x, y, w:0.26, h:0.32, fontSize:13, bold:true, color:C.g400, align:'center', valign:'middle' }); x += 0.26; } });
  }
  // 번호 목록(제목 한 줄 + 설명 + 빨간 주의 줄)
  function list(s, items, { x = RX, y = IY, w = RW, ts = 13, ds = 10.5, gap = 0.08 } = {}){
    const lh = ds * 1.2 * 1.15 / 72; let cy = y;
    items.forEach(it => { L.badge(s, { x, y:cy + 0.01, n:it.n, d:0.3 });
      L.T(s, it.title, { x:x + 0.42, y:cy, w:w - 0.42, h:0.32, fontSize:ts, bold:true, color:C.navy, valign:'middle' });
      const runs = [], dl = it.desc ? it.desc.split('\n') : [];
      dl.forEach((t, i) => runs.push({ text:t, options:{ color:C.g600, fontSize:ds, fontFace:L.FONT, breakLine: i < dl.length - 1 || !!it.warn } }));
      if (it.warn) runs.push({ text:it.warn, options:{ color:C.red, bold:true, fontSize:ds, fontFace:L.FONT } });
      const nl = dl.length + (it.warn ? 1 : 0);
      if (nl) s.addText(runs, { x:x + 0.42, y:cy + 0.31, w:w - 0.42, h:nl * lh + 0.04, isTextBox:true, margin:0, valign:'top', lineSpacingMultiple:1.15 });
      cy += 0.31 + nl * lh + gap; });
    return cy;
  }
  function shot(s, file, cap){ const g = L.img(s, REAL(file), { x:IX, y:IY, w:IW, h:IH, valign:'top', align:'left', radius:18, alt:'실제 MeAI 화면' });
    L.caption(s, { x:g.x, y:g.y + g.h + 0.03, w:g.w, text:cap || '실제 MeAI 화면 · 이름은 가림', align:'left', size:9.5 }); return g; }
  function pins(s, g, pts, o = P){ pts.forEach(([px, py], i) => L.pin(s, g, px, py, i + 1, o)); }
  function box(s, g, x1, y1, x2, y2, color = C.blue){ const k = g.scale; s.addShape('roundRect', { x:g.x + x1 * k, y:g.y + y1 * k, w:(x2 - x1) * k, h:(y2 - y1) * k, fill:{ type:'none' }, line:{ color, width:1.75 }, rectRadius:0.04 }); }
  function tip(s, y, label, text, tone = 'blue', h){ const hh = h || 0.62;
    if (y + hh > 6.95) throw new Error('p6r tip "' + label + '" bottom ' + (y + hh).toFixed(2) + 'in > 6.95 (쪽 번호 7.08 위)');
    L.note(s, { x:RX, y, w:RW, h:hh, label, text, tone, size:10.5 }); return y + hh; }

  // ── 0. 지도: MeAI 홈 → 두 갈래 → 실제 화면 ──────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('한눈에'), title:'MeAI 홈에서 실제 화면까지, 두 갈래 길', sub:'홈의 카드 한 장에서 시작해 요약 리포트까지 — 다음 9쪽이 실제 화면 순서', pageNo:no, tag:{ text:'NEW 실제 화면', fill:C.blue50, color:C.blue } });
    // 왼쪽: MeAI 홈(인사 + 대화 카드 두 장)
    const lw = 3.75;
    L.R(s, { x:M, y:1.92, w:lw, h:4.55, fill:C.g50, line:C.g200, radius:0.16 });
    L.T(s, '출발', { x:M + 0.25, y:2.05, w:2, h:0.3, fontSize:11, bold:true, color:C.blue, valign:'middle' });
    L.T(s, 'MeAI 홈', { x:M + 0.25, y:2.33, w:3, h:0.42, fontSize:18, bold:true, color:C.navy, valign:'middle' });
    const g = L.img(s, HERO('bc3_home_cards'), { x:M + 0.18, y:2.85, w:lw - 0.36, h:1.0, valign:'top', radius:12 });
    const k = g.scale, cx = (px) => g.x + px * k, cy = (py) => g.y + py * k;   // bc3_home_cards.png 그림 픽셀(2280x510)
    // A·B 표시는 각 카드 화살표 왼쪽 빈자리(카드 이름·설명을 가리지 않게)
    L.badge(s, { x:cx(880) - 0.16, y:cy(290) - 0.16, n:0, text:'A', color:C.blue, d:0.32 });
    L.badge(s, { x:cx(2030) - 0.16, y:cy(290) - 0.16, n:0, text:'B', color:C.red, d:0.32 });
    let y = g.y + g.h + 0.22;
    [['A', C.blue, '흰 [일반대화] 카드', '고객을 정하지 않고 바로 질문'], ['B', C.red, '검은 [맞춤대화] 카드', '고객 검색 → [맞춤대화]\n또는 추천 카드 → 고객찾기 →\n[이 고객으로 맞춤대화 시작]']].forEach(([t, col, a, b]) => {
      L.badge(s, { x:M + 0.25, y, n:0, text:t, color:col, d:0.3 });
      L.T(s, a, { x:M + 0.68, y:y - 0.02, w:lw - 0.85, h:0.34, fontSize:12.5, bold:true, color:C.navy, valign:'middle' });
      const nl = b.split('\n').length;
      L.T(s, b, { x:M + 0.68, y:y + 0.32, w:lw - 0.85, h:nl * 0.21 + 0.04, fontSize:10, color:C.g600, valign:'top', lineSpacingMultiple:1.1 });
      y += 0.42 + nl * 0.21 + 0.18; });
    // 오른쪽: 두 갈래(실제 화면 썸네일) → 둘 다 요약 리포트로 모임
    const lx = M + lw + 0.35, tw = 1.12, th = tw * 963 / 1531, gap = 0.24;
    const lanes = [
      { key:'A', col:C.blue, name:'일반대화', y:2.0, items:[['r01_general_home','첫 화면',1], ['r02_prompt_lib_reco','질문 모음',2], ['r04_general_answer','답 읽기',3]] },
      { key:'B', col:C.red, name:'맞춤대화', y:4.2, items:[['r06_custom_start','계약 고르기',4], ['r07_custom_info','고객 정보',5], ['r08_custom_answer','보장분석 답',6], ['r09_custom_precontract','설계 → 가계약',7]] } ];
    lanes.forEach(ln => {
      L.badge(s, { x:lx, y:ln.y, n:0, text:ln.key, color:ln.col, d:0.3 });
      L.T(s, ln.name, { x:lx + 0.4, y:ln.y - 0.02, w:2, h:0.34, fontSize:13, bold:true, color:C.navy, valign:'middle' });
      ln.items.forEach(([f, lab, off], i) => { const x = lx + i * (tw + gap), ty = ln.y + 0.42;
        const t = L.img(s, REAL(f), { x, y:ty, w:tw, h:th, radius:10 });
        L.T(s, lab, { x, y:ty + th + 0.05, w:tw, h:0.26, fontSize:10.5, bold:true, color:C.navy, align:'center', valign:'middle' });
        L.T(s, 'p.' + (no + off), { x, y:ty + th + 0.3, w:tw, h:0.22, fontSize:9.5, color:C.g500, align:'center', valign:'middle' });
        L.link(no, { x, y:ty, w:tw, h:th + 0.52 }, no + off);
        if (i < ln.items.length - 1) L.T(s, '›', { x:x + tw, y:ty + th / 2 - 0.2, w:gap, h:0.4, fontSize:16, bold:true, color:C.g400, align:'center', valign:'middle' }); }); });
    // 모이는 곳: 두 길 모두 [요약 리포트] → 고르기 → 편집·저장
    const ex = lx + 4 * (tw + gap) + 0.3, mg = 0.24, mw = (W - M - 0.12 - ex - mg) / 2, ey = 3.2;
    L.R(s, { x:ex - 0.12, y:ey - 0.48, w:W - M - ex + 0.12, h:mw * 963 / 1531 + 1.12, fill:C.g50, line:C.g200, radius:0.12 });
    L.T(s, '두 길 모두 → [요약 리포트]', { x:ex - 0.12, y:ey - 0.42, w:W - M - ex + 0.12, h:0.3, fontSize:10.5, bold:true, color:C.g600, align:'center', valign:'middle' });
    [['r05_report_select','리포트 고르기',8], ['r11_report_edit','편집 · 저장',9]].forEach(([f, lab, off], i) => { const x = ex + i * (mw + mg), mh = mw * 963 / 1531;
      L.img(s, REAL(f), { x, y:ey, w:mw, h:mh, radius:10 });
      L.T(s, lab, { x, y:ey + mh + 0.05, w:mw, h:0.26, fontSize:10.5, bold:true, color:C.navy, align:'center', valign:'middle' });
      L.T(s, 'p.' + (no + off), { x, y:ey + mh + 0.3, w:mw, h:0.22, fontSize:9.5, color:C.g500, align:'center', valign:'middle' });
      L.link(no, { x, y:ey, w:mw, h:mh + 0.52 }, no + off);
      if (i === 0) L.T(s, '›', { x:x + mw, y:ey + mh / 2 - 0.2, w:mg, h:0.4, fontSize:16, bold:true, color:C.g400, align:'center', valign:'middle' }); });
    L.T(s, '↘', { x:ex - 0.36, y:2.95, w:0.3, h:0.3, fontSize:14, bold:true, color:C.g400, align:'center', valign:'middle' });
    L.T(s, '↗', { x:ex - 0.36, y:4.55, w:0.3, h:0.3, fontSize:14, bold:true, color:C.g400, align:'center', valign:'middle' });
    L.R(s, { x:M, y:6.62, w:W - 2 * M, h:0.36, fill:C.g100, line:null, radius:0.1 });
    L.T(s, '어느 화면이든 왼쪽 위(실제 화면에서는 meritz 로고 자리)의 [MeAI 홈]을 누르면 처음 화면으로 돌아갑니다. 실제 화면의 이름은 가렸습니다.', { x:M + 0.2, y:6.62, w:W - 2 * M - 0.4, h:0.36, fontSize:10, color:C.g700, valign:'middle' });
  }});

  // ── 1. 일반대화 첫 화면 ─────────────────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('일반대화 1/3'), title:'일반대화 첫 화면 — 고르거나, 말하듯 묻거나', pageNo:no });
    crumbs(s, ['MeAI 홈', '[일반대화] 카드', '일반대화 첫 화면']);
    const g = shot(s, 'r01_general_home');
    pins(s, g, [[490,418],[890,476],[490,630],[490,714],[915,834],[672,862],[145,169],[180,901]]);
    box(s, g, 528, 694, 767, 734);
    const end = list(s, [
      { n:1, title:'질문 예시 탭 3개', desc:'보장비교 · 지식 검색 · 자주하는 질문' },
      { n:2, title:'질문 예시', desc:'누르면 그 문장으로 바로 대화 시작' },
      { n:3, title:'개인정보 안내', warn:'이름·연락처·주소·주민번호·계좌번호는 넣지 않음' },
      { n:4, title:'[질문 더보기 (프롬프트 라이브러리)]', desc:'잘 만든 질문 모음 → 다음 쪽' },
      { n:5, title:'입력창', desc:'말하듯 쓰고 오른쪽 ↑로 보내기' },
      { n:6, title:'[상품 선택]', desc:'상품을 골라 두면 그 상품 기준으로 답' },
      { n:7, title:'약관 검색 · 사용 가이드', desc:'약관 원문 찾기 · 화면 사용법' },
      { n:8, title:'[새로 대화하기]', desc:'주제가 바뀌면 새 대화로' } ], { ds:10, gap:0.03 });
    tip(s, Math.max(end + 0.02, 6.05), '주의', '예시 질문은 타사 비교. 타사보다 좋다·유리하다는 답은 공부용 — 고객 설명·리포트엔 쓰지 않음', 'red', 0.72);
  }});

  // ── 2. 프롬프트 라이브러리 ───────────────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('일반대화 2/3'), title:'NEW 프롬프트 라이브러리 — 잘 만든 질문을 골라 쓰기', pageNo:no });
    crumbs(s, ['MeAI 홈', '[일반대화] 카드', '[질문 더보기]', '프롬프트 라이브러리']);
    const g = shot(s, 'r02_prompt_lib_reco');
    pins(s, g, [[292,217],[520,308],[625,362],[961,480],[820,826],[1204,107]]);
    const end = list(s, [
      { n:1, title:'탭 3개', desc:'추천: 갈래별 추천 질문 · 최신: 최근 질문(오늘·어제 순)\n나의 질문: 저장 아이콘으로 모아 둔 질문' },
      { n:2, title:'갈래 4개', desc:'실전영업 · 상품지식 · 배경지식 · 업무지원\n꺾쇠(∨)로 펼치고 접기\n처음이면 [실전영업]부터 · 니즈 환기·설득·거절 화법' },
      { n:3, title:'질문 고르기', desc:'누르면 분홍색 · 오른쪽에 전체 문장' },
      { n:4, title:'미리보기', desc:'무엇을 묻는 질문인지 먼저 확인' },
      { n:5, title:'[이 질문 사용하기]', desc:'그대로 MeAI에게 물음 · 직접 쓸 필요 없음' },
      { n:6, title:'닫기(X)', desc:'창을 닫고 대화 화면으로' } ]);
    tip(s, Math.max(end + 0.04, 6.05), '확인', '질문 속 판단(예: 전이암 분류)은 상품·약관마다 다름 → 약관으로 확인', 'yellow', 0.62);
  }});

  // ── 3. 일반대화 답 ─────────────────────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('일반대화 3/3'), title:'일반대화 답 — 핵심부터 읽고, 이어서 묻기', pageNo:no });
    crumbs(s, ['MeAI 홈', '[일반대화] 카드', '질문 보내기(↑)', '답 화면']);
    const g = shot(s, 'r04_general_answer');
    pins(s, g, [[1316,225],[817,293],[652,598],[722,813],[1449,80],[145,346],[907,925]]);
    const end = list(s, [
      { n:1, title:'질문 아래 아이콘', desc:'복사 · 고쳐 묻기 · 저장 → 나의 질문(p.' + (no - 1) + ')' },
      { n:2, title:'첫 단락 = 결론', desc:'아이콘 붙은 소제목별로 나뉨 · 결론부터 읽기' },
      { n:3, title:'[접기]', desc:'긴 답은 접어서 짧게' },
      { n:4, title:'입력창에서 이어 묻기', desc:'같은 대화 안에서 앞 내용을 이어서 답함' },
      { n:5, title:'[요약 리포트]', desc:'이 대화를 리포트로 → p.' + (no + 5) },
      { n:6, title:'대화 기록', desc:'지금 대화는 빨간 글씨 + [현재 대화]' },
      { n:7, title:'아래 안내문', warn:'AI 답 · 근거자료로 꼭 확인 · 미검증 책임은 사용자' } ], { gap:0.04 });
    tip(s, Math.max(end + 0.04, 5.75), '예시 답', "'타사 1회성 담보보다 유리'는 AI의 비교 답 — 공부용. 타사보다 좋다·유리하다는 말은 고객 설명·리포트엔 쓰지 않음. 우리 담보 횟수·금액도 약관 지급표로 확인", 'red', 1.05);
  }});

  // ── 4. 맞춤대화 시작 — 계약 고르기 ───────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('맞춤대화 1/4'), title:'맞춤대화 시작 — 분석할 계약과 담보 고르기', pageNo:no });
    crumbs(s, ['MeAI 홈', '[맞춤대화] 카드', '고객 검색', '[맞춤대화]', '시작 화면']);
    const g = shot(s, 'r06_custom_start', '실제 MeAI 화면 · 이름·가입기간·납입 횟수는 가림 · 계약·금액은 한 고객의 예시');
    pins(s, g, [[258,200],[1150,92],[490,402],[1064,346],[490,543],[548,621],[914,901]]);
    const end = list(s, [
      { n:1, title:'담당 고객 · 동의 남은 날', desc:'보장분석 동의 N일 남음 · 0일이면 다시 동의' },
      { n:2, title:'고객 정보 카드', desc:'∨를 누르면 펼침 → 다음 쪽' },
      { n:3, title:'선택한 계약의 총 보험료', desc:'체크한 정상 계약의 월 보험료 합' },
      { n:4, title:'약관DB 점 색', desc:'파랑 = 준비 완료 · 노랑 = 준비 중 · 회색 = 없음', warn:'파랑이 아니면 답이 부정확할 수 있음' },
      { n:5, title:'담보 칩 9개', desc:'암 · 뇌/심장 · 치료비 · 수술비 등 보고 싶은 담보만' },
      { n:6, title:'계약 체크', desc:'[전체 선택] · 관계없는 계약은 체크 해제' },
      { n:7, title:'[대화 시작하기]', desc:'마지막에 누름 → 첫 질문 "보장분석 해줘"(p.52)' } ], { ds:10 });
    tip(s, Math.max(end + 0.02, 6.05), '열리는 고객', '사전조회(보장분석) 동의가 살아 있는 고객만 · 동의 후 90일', 'blue', 0.62);
  }});

  // ── 5. 고객 정보 입력 ──────────────────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('맞춤대화 2/4'), title:'고객 정보 다섯 칸 — 아는 것만 적어도 답이 달라짐', pageNo:no });
    crumbs(s, ['MeAI 홈', '[맞춤대화] 카드', '시작 화면', '고객 정보 카드 ∨ ([대화 시작하기] 전에)']);
    const g = shot(s, 'r07_custom_info', '실제 MeAI 화면 · 이름은 가림 · 칸 속 회색 글씨는 화면의 입력 예시');
    pins(s, g, [[497,229],[497,282],[497,335],[497,388],[497,440],[497,542],[1094,543]], { ...P, d:0.24 });
    const end = list(s, [
      { n:1, title:'직업', desc:'고객 상황에 맞춘 답에 반영' },
      { n:2, title:'병력', desc:'고객 본인이 앓았던 병' },
      { n:3, title:'가족력', desc:'가족의 병 → 더 챙길 보장' },
      { n:4, title:'신규 제안 월 보험료', desc:'새로 제안할 월 예산 → 그 안에서 설계 방향' },
      { n:5, title:'메모', desc:'가족 행사 · 요즘 걱정거리 등 상담 참고' },
      { n:6, title:'[입력하지 않고 넘어가기]', desc:'정보 없이도 맞춤대화는 됨' },
      { n:7, title:'[입력 완료]', desc:'저장하면 답에 반영 · 고칠 땐 [사용중인 정보 수정]' } ], { gap:0.05 });
    tip(s, Math.max(end + 0.04, 5.85), '지킬 것', '이름·연락처·주소·주민번호·계좌번호는 넣지 않음. 건강정보는 고객이 동의한 범위에서 필요한 만큼만 · 가족 등 다른 사람의 건강정보는 이름 없이, 특히 조심', 'red', 1.05);
  }});

  // ── 6. 맞춤대화 답 → 다음 질문 ────────────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('맞춤대화 3/4'), title:'보장분석 답 — 보완 방향을 읽고, 버튼으로 다음 질문', pageNo:no });
    crumbs(s, ['MeAI 홈', '[맞춤대화] 카드', '[대화 시작하기]', '"보장분석 해줘"', '보장분석 답']);
    const g = shot(s, 'r08_custom_answer', '실제 MeAI 화면 · 이름은 가림 · 금액은 AI 제안 예시');
    pins(s, g, [[500,98],[556,258],[495,531],[1000,611],[800,762],[1045,28],[914,848]]);
    box(s, g, 520, 597, 965, 625, C.red);
    const end = list(s, [
      { n:1, title:'보완 제안 표', desc:'담보 · 지금 금액 · 제안 금액 · 이유(위로 올리면 앞부분)' },
      { n:2, title:'보완 방향 · 유의사항', desc:'무엇을 먼저 보완할지 다섯 줄\n마지막 줄 "기존 보장은 유지하면서 보완"까지 읽기' },
      { n:3, title:'질문 예시 4개', desc:'누르기만 하면 다음 질문이 보내짐' },
      { n:4, title:'"이 제안대로 가계약 제안서를 만들어줘"', desc:'설계 → 가계약으로 이어짐 → 다음 쪽' },
      { n:5, title:'[질문 더보기]', desc:'프롬프트 라이브러리 → p.' + (no - 4) },
      { n:6, title:'위 버튼 3개', desc:'보장분석 데이터 · 사용중인 정보 수정 · 요약 리포트' },
      { n:7, title:'입력창', desc:'예) "월 보험료 4만 원에 맞춰 줘"' } ], { ds:10 });
    tip(s, Math.max(end + 0.02, 6.05), '확인', '제안 금액·"유리합니다" 같은 문장은 AI 제안. 약관·설계 화면으로 확인하고 그대로 옮기지 않음', 'yellow', 0.62);
  }});

  // ── 7. 설계 → 가계약 생성 ───────────────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('맞춤대화 4/4'), title:'NEW 설계안에서 가계약까지 — [생성하기] 한 번', pageNo:no });
    crumbs(s, ['MeAI 홈', '[맞춤대화] 카드', '보장분석 답', '"이 제안대로 가계약 제안서를 만들어줘"']);
    const g = shot(s, 'r09_custom_precontract', '실제 MeAI 화면 · 이름은 가림 · 담보·금액은 AI 제안 예시');
    pins(s, g, [[909,274],[492,572],[422,604],[492,757],[1328,757]]);
    box(s, g, 1189, 729, 1285, 785, C.red);
    const end = list(s, [
      { n:1, title:'가계약 제안서 표', desc:'담보와 가입금액(위로 올리면 앞부분)' },
      { n:2, title:"'가계약 제안서'라는 안내", desc:'실제 가계약 생성 뒤 조건이 바뀔 수 있음' },
      { n:3, title:'고치고 싶으면', desc:'목표 보험료·담보별 금액을 입력창에 쓰면 다시 만듦' },
      { n:4, title:'"이 정보로 가계약을 생성할까요?"', desc:'만들기 직전 확인 카드' },
      { n:5, title:'[생성하기]', desc:'실제 가계약 생성', warn:'최대 5분 · 그동안 MeAI 사용 불가' } ]);
    // 순서 세 칸
    const sy = Math.max(end + 0.06, 4.75), sw = (RW - 0.3) / 3;
    [['1','표 확인'],['2','고칠 것 요청'],['3','[생성하기]']].forEach(([n, t], i) => { const x = RX + i * (sw + 0.15);
      L.R(s, { x, y:sy, w:sw, h:0.78, fill: i === 2 ? C.navy : C.blue50, line:null, radius:0.12 });
      L.T(s, n, { x, y:sy + 0.06, w:sw, h:0.28, fontSize:11, bold:true, color: i === 2 ? C.blue100 : C.blue, align:'center', valign:'middle' });
      L.T(s, t, { x, y:sy + 0.36, w:sw, h:0.32, fontSize:12, bold:true, color: i === 2 ? 'FFFFFF' : C.navy, align:'center', valign:'middle' });
      if (i < 2) L.T(s, '›', { x:x + sw - 0.02, y:sy + 0.2, w:0.19, h:0.36, fontSize:14, bold:true, color:C.g400, align:'center', valign:'middle' }); });
    tip(s, sy + 0.95, '금액', '앞 쪽 보완 제안과 다를 수 있음 → 가계약 제안서에서 조정된 것. 확정 금액처럼 말하지 않음', 'yellow', 0.8);
  }});

  // ── 8. 요약 리포트 ① 넣을 내용 고르기 ─────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('요약 리포트 1/2'), title:'요약 리포트 — 넣을 질문·답 고르기', pageNo:no });
    crumbs(s, ['MeAI 홈', '일반대화 · 맞춤대화', '답 화면 오른쪽 위 [요약 리포트]']);
    const g = shot(s, 'r05_report_select');
    pins(s, g, [[522,54],[854,139],[356,220],[515,298],[722,409],[962,900]]);
    box(s, g, 398, 206, 427, 235, C.red);
    const end = list(s, [
      { n:1, title:'고르는 단계', desc:'리포트에 넣을 질문·답을 고름' },
      { n:2, title:'[전체 편집하기 >]', desc:'대화 전부를 한 번에' },
      { n:3, title:'체크', desc:'넣을 질문 묶음마다 체크' },
      { n:4, title:'질문 #1', desc:'질문 원문 · 보낸 시각' },
      { n:5, title:'답변 #1', desc:'리포트에 실릴 답을 미리 확인' },
      { n:6, title:'[편집하기]', desc:'체크한 뒤에 눌림 → 다음 쪽' } ]);
    tip(s, Math.max(end + 0.06, 5.55), '고를 때', '고객에게 나갈 내용만. 이 화면의 예시 답(타사보다 유리)처럼 비교·권유로 읽히는 답은 넣지 않음', 'red', 0.9);
  }});

  // ── 9. 요약 리포트 ② 편집 · 저장 ─────────────────────────────
  S.push({ fn:(pres, no) => {
    const s = L.base(pres, { kicker:kick('요약 리포트 2/2'), title:'NEW 리포트 편집 — 모양을 고르고 PDF · Word로 저장', pageNo:no });
    crumbs(s, ['MeAI 홈', '답 화면 [요약 리포트]', '고르기 → [편집하기]', '편집 화면']);
    const g = L.img(s, REAL('r11_report_edit'), { x:IX, y:IY, w:IW, h:IH, valign:'top', align:'left', radius:18, alt:'실제 MeAI 화면' });
    L.caption(s, { x:g.x, y:g.y + g.h + 0.03, w:g.w, text:'실제 MeAI 화면 · 이름은 가림 · 리포트 본문은 흐리게 처리', align:'left', size:9.5 });
    pins(s, g, [[150,210],[205,327],[170,503],[790,89],[428,54],[278,853],[278,925]]);
    box(s, g, 18, 844, 240, 933);
    const end = list(s, [
      { n:1, title:'방향', desc:'세로 · 가로' },
      { n:2, title:'글자 크기(− 14px +)', desc:'어르신 고객이면 크게' },
      { n:3, title:'구성 요소 — 체크를 끄면 빠짐', desc:'고객 정보 · AI 요약 · 질문 · 답변 · 이미지(기본 꺼짐)' },
      { n:4, title:'미리보기', desc:'설정이 바로 반영 · 끝까지 읽고 숫자·약관 확인' },
      { n:5, title:"'AI로 생성된 보조자료입니다.'", desc:'리포트 맨 위 안내 · 지우지 않음' },
      { n:6, title:'[PDF로 저장 / 인쇄]', desc:'아래 확인을 마친 뒤 고객에게 줄 파일' },
      { n:7, title:'[Word로 저장]', desc:'문장을 고쳐 보낼 때(PDF는 미리보기 그대로)' } ], { ds:10, gap:0.06 });
    tip(s, Math.max(end + 0.02, 5.95), '보내기 전', 'AI 요약에 계약별 유지·해지 의견이 들어갈 수 있음 → 구성 요소에서 AI 요약 끄기, 또는 Word로 저장해 그 문장 지우고 보내기. 휴대폰은 카카오톡(p.' + (ctx.parts['06'] ? ctx.parts['06'] + 12 : '-') + ')', 'red', 0.95);
  }});
};
