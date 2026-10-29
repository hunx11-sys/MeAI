/* MeAI 홈 넛지 v5 · MeAI 대시보드 (① 나의 MeAI 기록 ② 본부 현황 ③ 본사 현황)
 * 보는 사람에 맞게 나눈다 : 나의 기록 = 본인만 · 본부 현황 = 본부장 · 지점장 · 팀장(자기 조직, 질문 원문 비열람) · 본사 현황 = 본사 데이터 담당.
 * 목업에서는 세 탭을 모두 열어 두었다. 실제로는 권한(roles)에 맞는 탭만 보인다.
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ, I = NZ.I, esc = NZ.esc, F = NZ.fmt;
  let ov = null, root = null, tab = 'me', orgScope = 'hq', orgFilter = '', memberFilter = '', hqSort = 'rate', liveT = 0;
  const kpi = (label, val, unit, delta, cls) => '<div class="nz-panel' + (cls ? ' ' + cls : '') + '"><div class="nz-kpi"><small>' + label + '</small><b>' + val + (unit ? '<small>' + unit + '</small>' : '') + '</b>' + (delta != null ? '<div class="d ' + (delta >= 0 ? 'up' : 'dn') + '">' + (delta >= 0 ? '▲ ' : '▼ ') + Math.abs(delta) + '</div>' : '') + '</div></div>';
  const bar = (p, cls) => '<span class="nz-bar' + (cls ? ' ' + cls : '') + '"><i data-v="p:' + Math.max(0, Math.min(1, p)).toFixed(3) + '"></i></span>';
  const EX = '<span class="nz-ex">예시 숫자</span>';

  NZ.dash = {
    open(t) {
      tab = t || 'me';
      root = NZ.el('<div class="nz-modal nz-dash" role="document"><div class="nz-mh"><h2>MeAI 대시보드</h2><span class="meta">' + esc(NZ.home.user.name) + ' · ' + esc(NZ.home.user.branch) + '</span>' +
        '<div class="nz-tabs" role="tablist">' + [['me', '나의 MeAI 기록'], ['org', '본부 현황'], ['hq', '본사 현황']].map((x) => '<button type="button" role="tab" data-tab="' + x[0] + '" aria-selected="' + (tab === x[0]) + '">' + x[1] + '</button>').join('') + '</div>' +
        '<button type="button" class="x" data-x aria-label="닫기">' + I.x + '</button></div><div class="nz-mb"><div class="nz-lock">불러오는 중…</div></div></div>');
      ov = NZ.overlay(root, { label: 'MeAI 대시보드', skip: false });
      ov.done.then(() => clearInterval(liveT));
      root.addEventListener('click', onClick);
      NZ.log('dash', 'open', { tab: tab });
      if (NZ.api.openDash && tab === 'me') NZ.run(NZ.api.openDash(), { quiet: true });
      show();
    }
  };
  function show() {
    clearInterval(liveT);
    NZ.$$('[data-tab]', root).forEach((b) => b.setAttribute('aria-selected', String(b.dataset.tab === tab)));
    const mb = root.querySelector('.nz-mb');
    if (tab === 'me') NZ.api.getRecord().then((r) => NZ.html(mb, me(r, NZ.home)));
    else if (tab === 'org') NZ.api.getOrgDash(orgScope).then((r) => { root._org = r; NZ.html(mb, org(r)); });
    else NZ.api.getHqDash().then((r) => { root._hq = r; NZ.html(mb, hq(r)); live(r); });
  }
  function onClick(e) {
    const t = e.target.closest('button, tr[data-row]'); if (!t) return;
    if (t.hasAttribute('data-x')) return ov.close();
    if (t.dataset.tab) { tab = t.dataset.tab; NZ.log('dash', 'tab', { tab: tab }); show(); return; }
    if (t.dataset.scope) { orgScope = t.dataset.scope; orgFilter = ''; show(); return; }
    if (t.dataset.row != null) { orgFilter = orgFilter === t.dataset.row ? '' : t.dataset.row; NZ.html(root.querySelector('.nz-mb'), org(root._org)); return; }
    if (t.dataset.mf != null) { memberFilter = t.dataset.mf; NZ.html(root.querySelector('.nz-mb'), org(root._org)); return; }
    if (t.dataset.sort) { hqSort = t.dataset.sort; NZ.html(root.querySelector('.nz-mb'), hq(root._hq)); live(root._hq); return; }
    if (t.dataset.reask) { ov.close(); NZ.host && NZ.host.ask(t.dataset.reask, 'general'); return; }
    if (t.hasAttribute('data-csv')) { csv(); return; }
  }

  // ── ① 나의 MeAI 기록 ─────────────────────────────────────
  function me(r, h) {
    const s = r.streak, L = h.league, C2 = h.compare, n = r.nums, mx = Math.max(C2.me, C2.branchAvg, C2.nonUser);
    const minis = s.last10.map((x) => '<i class="' + x.state + '"></i>').join('');
    const cal = r.cells.map((c) => '<i class="' + (c.state === 'holiday' ? 'holiday' : c.state === 'today' ? 'today' : c.state === 'shield' ? 'shield' : c.state === 'miss' ? 'miss' : 'l' + Math.max(1, c.level)) + '" title="' + esc(F.md(c.day) + (c.holiday ? ' ' + c.holiday : '')) + '"></i>').join('');
    const months = Object.keys(r.months).map((m) => '<span>' + (+m.slice(5)) + '월 <b>' + r.months[m].lit + '</b>/' + r.months[m].biz + '일</span>').join('');
    const fmax = r.funnel[0][1] || 1;
    return '<div class="nz-dgrid c3">' +
      '<div class="nz-panel dark"><h3>' + I.flame + ' 연속 사용 영업일<span class="r">최고 ' + r.best + '일</span></h3><div class="nz-kpi"><b>' + s.current + '<small>영업일</small></b></div><div class="nz-minis">' + minis + '</div><p class="nz-note">전사 상위 ' + h.streak.topPercent + '% ' + EX + ' · 출석 · 추천 고객 · 대화 중 하나로 불이 켜져요</p></div>' +
      '<div class="nz-panel"><h3>' + I.trophy + ' 이번 주 지점 리그<span class="r">' + esc(L.weekLabel) + '</span></h3><div class="nz-kpi"><b>' + L.rank + '<small>위 / ' + L.total + '명</small></b></div><p class="nz-sub">' + F.n(L.xp) + ' XP · ' + (L.rank > 1 ? '위 사람까지 ' + L.gap + ' XP' : '1위') + (L.nextPass ? ' · 패스 다음 보상 ' + (L.nextPass.xp - L.xp) + ' XP' : '') + '</p></div>' +
      '<div class="nz-panel"><h3>' + I.users + ' 미사용 동료 대비<span class="r">' + esc(C2.metric) + '</span></h3><p class="nz-bigline">미사용 동료보다 <b>' + C2.ratio + '배</b></p><div class="nz-cmp">' +
      [['me', '나', C2.me], ['av', '지점 평균', C2.branchAvg], ['no', '미사용 동료', C2.nonUser]].map((x) => '<div class="r ' + x[0] + '"><span>' + x[1] + '</span>' + bar(x[2] / mx) + '<b>' + x[2] + '</b></div>').join('') + '</div><p class="nz-note">참고용 · 인과 아님 ' + EX + '</p></div></div>' +
      '<div class="nz-dgrid c6">' + kpi('사용 영업일', n.days, '일') + kpi('MeAI 질문', n.questions, '건') + kpi('준비한 고객', n.customers, '명') + kpi('출석 도장', n.attend, '번') + kpi('화법 따라 쓰기', n.talks, '번') + kpi('퀴즈 정답률', n.quizN ? Math.round(n.quizOk / n.quizN * 100) : 0, '%') + '</div>' +
      '<div class="nz-panel"><h3>' + I.cal + ' 출석 · 사용 달력<span class="r">' + F.md(r.from) + ' ~ 오늘 · 영업일 한 칸 · 진할수록 많이 씀</span></h3><div class="nz-cal">' + cal + '</div><div class="nz-calm">' + months + '<span>· 흰 칸 = 공휴일 · 파란 테두리 = 보호권</span></div></div>' +
      '<div class="nz-dgrid c21"><div class="nz-panel"><h3>' + I.medal + ' 업적 배지<span class="r">' + r.badges.filter((b) => b.have).length + ' / ' + r.badges.length + '</span></h3><div class="nz-badges">' +
      r.badges.map((b) => '<div class="nz-badge' + (b.have ? ' have' : '') + '"><div class="em">' + (b.id.indexOf('streak') === 0 ? I.flame : b.id.indexOf('quiz') === 0 ? I.quiz : b.id.indexOf('talk') === 0 ? I.quote : b.id.indexOf('reco') === 0 ? I.users : b.id.indexOf('cheer') === 0 ? I.clap : I.star) + '</div><b>' + esc(b.label) + '</b><small>' + esc(b.desc) + '</small>' + (b.have ? '' : bar(b.progress / b.n, 'gold')) + '</div>').join('') + '</div></div>' +
      '<div class="nz-panel"><h3>' + I.ring + ' 이번 주 목표</h3><div class="nz-funnel">' + r.goals.map((g) => '<div class="r"><span>' + esc(g.title) + '</span>' + bar(g.value / g.target, g.value >= g.target ? 'green' : '') + '<b>' + g.value + '/' + g.target + '</b></div>').join('') + '</div><p class="nz-note">달성하면 응모권이 들어와요 (주간 패스와 같은 XP)</p></div></div>' +
      '<div class="nz-dgrid c2"><div class="nz-panel"><h3>' + I.chart + ' 고객 활용 흐름<span class="r">7월부터</span></h3><div class="nz-funnel">' + r.funnel.map((f) => '<div class="r"><span>' + f[0] + '</span>' + bar(f[1] / fmax, 'ink') + '<b>' + F.n(f[1]) + '</b></div>').join('') + '</div><p class="nz-note">' + esc(r.funnelNote) + '</p></div>' +
      '<div class="nz-panel"><h3>' + I.send + ' 자주 쓰는 질문 · 추천 프롬프트</h3><ul class="nz-mini-list">' + r.questions.map((q, i) => '<li><span class="n">' + (i + 1) + '</span><span>' + esc(q[0]) + '</span><span class="v">' + q[1] + '번</span><button type="button" class="nz-btn sm sec" data-reask="' + esc(q[0]) + '">다시 묻기</button></li>').join('') + '</ul>' +
      '<div class="nz-cheers">' + r.prompts.map((p) => '<span class="nz-chip blue">' + esc(p[0]) + ' · ' + p[1] + '번</span>').join('') + '</div><p class="nz-note">질문 문구는 예시예요. 실제로는 내 질문에서 개인정보를 가린 뒤 모아요.</p></div></div>' +
      '<p class="nz-src-line">' + I.lock.replace('<svg', '<svg class="gold"') + ' 이 화면은 본인만 볼 수 있어요. 리더 화면에는 집계만 가요 · 목업에서는 세 탭을 모두 열어 두었고, 실제로는 권한에 맞는 탭만 보여요.</p>';
  }

  // ── ② 본부 현황 (리더) ───────────────────────────────────
  function org(r) {
    const K = r.kpi, rows = r.rows, sel = orgFilter;
    const mem = r.members.filter((m) => !memberFilter || m.status === memberFilter);
    const heat = '<div class="nz-tblwrap"><table class="nz-tbl"><thead><tr><th>퀴즈 (최근 5일)</th>' + rows.map((x) => '<th class="num">' + esc(x.name.replace('지점', '')) + '</th>').join('') + '</tr></thead><tbody>' +
      r.quizzes.map((q) => '<tr><td>' + F.md(q.date) + ' ' + esc(q.question.slice(0, 22)) + '…</td>' + q.rows.map((v) => '<td class="num"><span class="nz-chip ' + (v < 45 ? 'red' : v < 65 ? 'gold' : 'green') + '">' + v + '%</span></td>').join('') + '</tr>').join('') + '</tbody></table></div>';
    return '<div class="nz-panel"><h3>' + I.users + ' 보기 범위<span class="r">기간 : 최근 30일 · ' + esc(r.hq) + '</span></h3><div class="nz-seg" role="group">' + [['hq', '본부 전체'], ['branch', '우리 지점'], ['team', '우리 팀']].map((x) => '<button type="button" data-scope="' + x[0] + '" aria-pressed="' + (orgScope === x[0]) + '">' + x[1] + '</button>').join('') + '</div></div>' +
      '<div class="nz-dgrid c4">' + kpi('활성 사용률', K.rate, '%', 3.4) + kpi('사용 FP', F.n(K.used), '/ ' + F.n(K.total) + '명') + kpi('누적 질문', F.n(K.questions), '건') + kpi('사용자 1인당', K.perFp, '건') + '</div>' +
      '<div class="nz-dgrid c21"><div class="nz-panel"><h3>' + I.chart + ' 지점별 사용 · 넛지 참여<span class="r">줄을 누르면 아래 팀원 목록이 좁혀져요 ' + EX + '</span></h3><div class="nz-tblwrap"><table class="nz-tbl"><thead><tr><th>지점</th><th class="num">인원</th><th class="num">사용</th><th class="num">사용률</th><th class="num">증감</th><th class="num">인당 질문</th><th class="num">출석률</th><th class="num">퀴즈 참여</th><th class="num">정답률</th><th class="num">미사용</th></tr></thead><tbody>' +
      rows.map((x) => '<tr data-row="' + esc(x.name) + '" class="' + (x.mine ? 'mine' : '') + '" tabindex="0"' + (sel === x.name ? ' aria-selected="true"' : '') + '><td>' + esc(x.name) + '</td><td class="num">' + x.members + '</td><td class="num">' + x.used + '</td><td class="num">' + x.rate + '%</td><td class="num">' + (x.delta >= 0 ? '▲' : '▼') + Math.abs(x.delta) + '</td><td class="num">' + x.perFp + '</td><td class="num">' + x.attend + '%</td><td class="num">' + x.quizJoin + '%</td><td class="num">' + x.quizOk + '%</td><td class="num">' + x.idle + '</td></tr>').join('') + '</tbody></table></div></div>' +
      '<div class="nz-panel dark"><h3>미사용 집중관리<span class="r">최근 30일</span></h3><div class="nz-kpi"><b>' + F.n(K.idle) + '<small>명</small></b></div><p class="nz-note">이름 대신 지점별 인원만 보여요. 연락은 지점장 판단으로.</p><ul class="nz-live">' + rows.slice().sort((a, b) => b.idle - a.idle).slice(0, 5).map((x) => '<li><b>' + esc(x.name) + '</b><span>' + x.idle + '명</span></li>').join('') + '</ul></div></div>' +
      '<div class="nz-panel"><h3>' + I.quiz + ' 전달 도달 지도 · 지점별 퀴즈 참여율<span class="r">빨강 = 전달이 약한 곳 ' + EX + '</span></h3>' + heat + '</div>' +
      '<div class="nz-dgrid c2"><div class="nz-panel"><h3>매출 규모별 설계사당 질문<span class="r">금액 대신 구간만</span></h3><div class="nz-funnel">' + r.sales.map((s) => '<div class="r"><span>' + esc(s.band) + '</span>' + bar(s.perFp / 25, 'blue') + '<b>' + s.perFp + '</b></div>').join('') + '</div></div>' +
      '<div class="nz-panel"><h3>인기 질문 TOP 5<span class="r">5건 이상 · 개인이 특정되는 질문 제외</span></h3><ul class="nz-mini-list">' + r.popular.map((p, i) => '<li><span class="n">' + (i + 1) + '</span><span>' + esc(p[0]) + '</span><span class="v">' + p[1] + '</span></li>').join('') + '</ul></div></div>' +
      '<div class="nz-panel"><h3>팀원별 현황' + (sel ? ' · ' + esc(sel) : '') + '<span class="r"><span class="nz-seg">' + [['', '전체'], ['활성', '활성'], ['저조', '저조'], ['미사용', '미사용']].map((x) => '<button type="button" data-mf="' + x[0] + '" aria-pressed="' + (memberFilter === x[0]) + '">' + x[1] + '</button>').join('') + '</span> <button type="button" class="nz-btn sm sec" data-csv>CSV</button></span></h3>' +
      '<div class="nz-tblwrap"><table class="nz-tbl"><thead><tr><th>이름</th><th>최근 사용</th><th class="num">기간 질문</th><th class="num">준비 고객</th><th class="num">연속 사용</th><th>주로 쓰는 기능</th><th>상태</th></tr></thead><tbody>' +
      mem.map((m) => '<tr><td>' + esc(m.name) + '</td><td>' + (m.last ? F.md(m.last) : '–') + '</td><td class="num">' + m.questions + '</td><td class="num">' + m.customers + '</td><td class="num">' + m.streak + '일</td><td>' + esc(m.main) + '</td><td><span class="st ' + (m.status === '활성' ? 'on' : m.status === '저조' ? 'low' : 'off') + '">' + m.status + '</span></td></tr>').join('') + '</tbody></table></div></div>' +
      '<div class="nz-principle">' + ['질문 원문 · 고객 정보는 볼 수 없어요', '매출은 금액 대신 구간만', '5건 이상 모인 것만 보여요', '실적 · 인사 평가 지표로 쓰지 않아요'].map((x) => '<span>' + I.check + esc(x) + '</span>').join('') + '</div>';
  }
  function csv() {
    const r = root._org; if (!r) return;
    const lines = [['이름', '최근 사용', '기간 질문', '준비 고객', '연속 사용', '주 기능', '상태']].concat(r.members.map((m) => [m.name, m.last, m.questions, m.customers, m.streak, m.main, m.status]));
    const blob = new Blob(['﻿' + lines.map((l) => l.join(',')).join('\n')], { type: 'text/csv' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'meai_members_example.csv'; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    NZ.log('dash', 'csv');
  }

  // ── ③ 본사 현황 ─────────────────────────────────────────
  function line(tr, w, hgt) {
    const xs = tr.map((_, i) => 8 + i * (w - 16) / Math.max(1, tr.length - 1)), mn = 30, mxv = 90;
    const ys = tr.map((p) => hgt - 20 - (p[1] - mn) / (mxv - mn) * (hgt - 40));
    const d = xs.map((x, i) => (i ? 'L' : 'M') + x.toFixed(1) + ' ' + ys[i].toFixed(1)).join(' ');
    const ar = d + ' L' + xs[xs.length - 1].toFixed(1) + ' ' + (hgt - 20) + ' L' + xs[0].toFixed(1) + ' ' + (hgt - 20) + ' Z';
    const ix = tr.findIndex((p) => p[0] >= '2026-10-12');
    const mk = ix >= 0 ? '<line x1="' + xs[ix] + '" x2="' + xs[ix] + '" y1="10" y2="' + (hgt - 20) + '" stroke="#e0282f" stroke-dasharray="4 4"/><text x="' + (xs[ix] + 6) + '" y="22" font-size="11" fill="#e0282f">넛지 오픈 표시 자리(예시)</text>' : '';
    const lab = tr.filter((_, i) => i % 6 === 0).map((p, k) => '<text x="' + xs[k * 6] + '" y="' + (hgt - 4) + '" font-size="10.5" fill="#61646b" text-anchor="middle">' + (+p[0].slice(5, 7)) + '/' + (+p[0].slice(8)) + '</text>').join('');
    return '<svg class="nz-line" viewBox="0 0 ' + w + ' ' + hgt + '" preserveAspectRatio="none" role="img" aria-label="일별 활성 사용률 추이"><path d="' + ar + '" fill="rgba(224,40,47,.08)"/><path d="' + d + '" fill="none" stroke="#e0282f" stroke-width="2"/>' + mk + lab + '</svg>';
  }
  function hq(r) {
    const K = r.kpi, B = r.baseline, rows = r.rows.slice().sort((a, b) => (b[hqSort] || 0) - (a[hqSort] || 0) || (a.name < b.name ? -1 : 1));
    const em = Math.max.apply(null, r.elements.map((e) => e.value));
    const hmax = Math.max.apply(null, B.heavy.map((x) => x[1]));
    const th = (k, label) => '<th class="num"><button type="button" data-sort="' + k + '" class="nz-btn ghost sm">' + label + (hqSort === k ? ' ▼' : '') + '</button></th>';
    return '<div class="nz-dgrid c6">' + kpi('설계사당 질문', K.perFp, '건', 1.2, 'dark') + kpi('활성 사용률', K.rate, '%', 2.1) + kpi('사용 설계사', F.n(K.used), '명') + kpi('총 질문', F.n(K.questions), '건') + kpi('홈 출석률', K.attend, '%') + kpi('미사용 설계사', F.n(K.idle), '명') + '</div>' +
      '<div class="nz-dgrid c12"><div class="nz-panel"><h3>' + I.info + ' 출발점 (실제 분석값)<span class="r">' + esc(B.source) + '</span></h3><div class="nz-funnel">' + B.heavy.map((x) => '<div class="r"><span>' + x[0] + ' 헤비유저</span>' + bar(x[1] / hmax, x[0] === '8월' ? '' : 'ink') + '<b>' + F.n(x[1]) + '</b></div>').join('') + '</div>' +
      '<p class="nz-sub">침투율 <b>' + B.penetration[0] + '% → ' + B.penetration[1] + '%</b> · MAU ' + F.n(B.mau[0]) + ' → ' + F.n(B.mau[1]) + '명 · 라이트유저 ' + F.n(B.light[0]) + ' → ' + F.n(B.light[1]) + '명</p><p class="nz-note">헤비유저 = 월 3주 이상 반복 사용 · 6월 → 8월 −58.4%. 이 두 숫자가 회복되는지를 가장 먼저 봐요.</p></div>' +
      '<div class="nz-panel"><h3>' + I.chart + ' 일별 활성 사용률<span class="r">파일럿 지점 · 9월부터 ' + EX + '</span></h3>' + line(r.trend, 720, 190) + '</div></div>' +
      '<div class="nz-panel"><h3>본부 비교<span class="r">머리글을 누르면 정렬 ' + EX + '</span></h3><div class="nz-tblwrap"><table class="nz-tbl"><thead><tr><th>본부</th><th>지역</th>' + th('members', '인원') + th('rate', '사용률') + th('delta', '증감') + th('perFp', '인당 질문') + th('attend', '출석률') + th('quizOk', '퀴즈 정답률') + '<th>가장 많이 쓴 요소</th></tr></thead><tbody>' +
      rows.map((x) => '<tr><td>' + esc(x.name) + '</td><td>' + esc(x.region) + '</td><td class="num">' + x.members + '</td><td class="num">' + x.rate + '%</td><td class="num">' + (x.delta >= 0 ? '▲' : '▼') + Math.abs(x.delta) + '</td><td class="num">' + x.perFp + '</td><td class="num">' + x.attend + '%</td><td class="num">' + x.quizOk + '%</td><td>' + esc(x.top) + '</td></tr>').join('') + '</tbody></table></div></div>' +
      '<div class="nz-dgrid c3"><div class="nz-panel"><h3>홈 요소 13종 사용량<span class="r">최근 7일</span></h3><div class="nz-funnel">' + r.elements.map((e) => '<div class="r"><span>' + esc(e.name) + '</span>' + bar(e.value / em, /출석|퀴즈|화법|퀘스트|로또|리그/.test(e.name) ? 'gold' : 'ink') + '<b>' + F.n(e.value) + '</b></div>').join('') + '</div><p class="nz-note">금색 = 이번에 더한 넛지 요소</p></div>' +
      '<div class="nz-panel"><h3>요일 · 시간대<span class="r">8시 ~ 19시</span></h3><div class="nz-heat"><span></span>' + Array.from({ length: 12 }, (_, i) => '<span>' + (8 + i) + '</span>').join('') +
      r.heat.map((row, i) => '<span>' + ['월', '화', '수', '목', '금'][i] + '</span>' + row.map((v) => '<i data-v="a:' + Math.min(1, v / 110).toFixed(2) + '" title="' + v + '"></i>').join('')).join('') + '</div><p class="nz-note">9시 출석 · 퀴즈 공개 직후가 가장 진해요 ' + EX + '</p>' +
      '<h3>지역별 사용률</h3><div class="nz-funnel">' + r.regions.map((g) => '<div class="r"><span>' + esc(g.name) + '</span>' + bar(g.rate / 100, 'blue') + '<b>' + g.rate + '%</b></div>').join('') + '</div></div>' +
      '<div class="nz-panel dark"><h3>실시간 이벤트<span class="r">개인정보 가림</span></h3><ul class="nz-live" id="nz-live">' + r.events.map(liveRow).join('') + '</ul><p class="nz-note">수집하는 이벤트 정의는 설계도 「사용 기록」 장에 있어요.</p></div></div>';
  }
  function liveRow(e) { return '<li><span class="t">' + esc(e.at) + '</span><b>' + esc(e.kind) + '</b><span>' + esc(e.org) + ' ' + esc(e.who) + '</span></li>'; }
  function live(r) {
    clearInterval(liveT);
    const kinds = ['출석 도장', '퀴즈 정답', '추천 고객 열기', '맞춤대화', '화법 따라 쓰기', '공지 읽기', '로또 세트 발급', '동료 응원'];
    liveT = setInterval(() => {
      const ul = root && root.querySelector('#nz-live'); if (!ul) return clearInterval(liveT);
      const mine = NZ.logs.slice(-1)[0];
      const e = { at: F.hm(Date.now()), kind: kinds[Math.floor(Math.random() * kinds.length)], org: r.rows[Math.floor(Math.random() * r.rows.length)].name, who: ['김○진', '박○우', '정○재', '오○훈', '서○호'][Math.floor(Math.random() * 5)] };
      const li = NZ.el(liveRow(e)); li.classList.add('new'); ul.insertBefore(li, ul.firstChild);
      while (ul.children.length > 14) ul.removeChild(ul.lastChild);
      void mine;
    }, 2400);
  }
})(window);
