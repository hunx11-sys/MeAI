(function () {
  'use strict';
  var S = window.NZ_SAJU, TA = window.NZ_TAROT, IMG = window.NZ_TAROT_IMG || [], $ = function (id) { return document.getElementById(id); };
  var WEEK = ['일', '월', '화', '수', '목', '금', '토'], MIN_D = 19360101, MAX_D = 20461231;
  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SANS = '"Pretendard", -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif';
  var SERIF = '"UnseSerif", "UnseHan", "AppleMyungjo", "Noto Serif KR", "Batang", serif';
  var CINZEL = '"UnseCinzel", Georgia, serif';
  function kstNow() { var k = new Date(Date.now() + 9 * 3600e3); return { y: k.getUTCFullYear(), m: k.getUTCMonth() + 1, d: k.getUTCDate(), w: WEEK[k.getUTCDay()] }; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function toast(t) { var e = $('toast'); e.textContent = t; e.classList.add('on'); clearTimeout(e._t); e._t = setTimeout(function () { e.classList.remove('on'); }, 2200); }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, RM ? Math.min(ms, 30) : ms); }); }
  function copy(t) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(t);
    return new Promise(function (res) { var ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0, t.length); try { document.execCommand('copy'); } catch (e) {} ta.remove(); res(); });
  }
  /* 'YYYY-MM-DD' → {y,m,d} (1936-01-01 ~ 2046-12-31) */
  function parseD(v, quiet) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(v || '')) return null;
    var a = v.split('-').map(Number), n = a[0] * 1e4 + a[1] * 100 + a[2];
    var t = new Date(Date.UTC(a[0], a[1] - 1, a[2]));
    if (t.getUTCMonth() !== a[1] - 1 || t.getUTCDate() !== a[2]) { if (!quiet) toast('없는 날짜예요 · 다시 확인해 주세요'); return null; }
    if (n < MIN_D || n > MAX_D) { if (!quiet) toast('1936년 1월 1일부터 2046년 12월 31일까지 고를 수 있어요'); return null; }
    return { y: a[0], m: a[1], d: a[2], n: n };
  }
  /* 그림 저장(캔버스)에 쓰는 글꼴은 미리 불러 둔다 (파일 안에 심은 글꼴이라 금방 끝남) */
  function fontsReady() {
    if (!document.fonts || !document.fonts.load) return Promise.resolve();
    return Promise.all([document.fonts.load('700 20px UnseSerif', '오늘의 운세'), document.fonts.load('700 20px UnseHan', '甲子'), document.fonts.load('700 20px UnseCinzel', 'TAROT')]).catch(function () {});
  }
  fontsReady();

  /* 생년월일 칸: 숫자만 쳐도 '1990-09-28' 꼴로 자동 하이픈, 8자리가 맞으면 키보드 내림. 달력 아이콘(투명 date 칸)으로 고르면 칸에 채움.
     다른 'input' 리스너보다 먼저 등록해야 정리된 값이 넘어감 */
  function bindDate(id) {
    var t = $(id), p = $(id + 'Pick');
    t.addEventListener('input', function () {
      var d = this.value.replace(/[^0-9]/g, '').slice(0, 8);
      var v = d.length > 6 ? d.slice(0, 4) + '-' + d.slice(4, 6) + '-' + d.slice(6) : d.length > 4 ? d.slice(0, 4) + '-' + d.slice(4) : d;
      if (v !== this.value) this.value = v;
      if (d.length === 8 && parseD(v, true)) { p.value = v; if (!this._fromPick) this.blur(); }
    });
    t.addEventListener('blur', function () { var n = this.value.replace(/[^0-9]/g, '').length; if (n && n < 8) toast('생년월일 숫자 8자리로 넣어 주세요 (예: 19900928)'); });
    t.addEventListener('keydown', function (e) { if (e.key === 'Enter') this.blur(); });
    p.addEventListener('click', function () { try { if (this.showPicker) this.showPicker(); } catch (e) {} });
    p.addEventListener('change', function () {
      if (!this.value) return;
      t.value = this.value; t._fromPick = true; t.dispatchEvent(new Event('input')); t.dispatchEvent(new Event('change')); t._fromPick = false;
    });
  }
  bindDate('bd'); bindDate('tbd');

  var T = kstNow(), TN = T.y * 1e4 + T.m * 100 + T.d, tp = S.pillars(T.y, T.m, T.d);
  var todayHtml = T.m + '월 ' + T.d + '일 (' + T.w + ') · <b>' + S.gz(tp.di) + '</b>일 ' + S.gzK(tp.di) + '일';
  $('gToday').innerHTML = todayHtml; $('today').innerHTML = todayHtml;

  /* ================= 타로 카드 앞면 =================
     크림색 테두리 + 1909년 원판 그림(window.NZ_TAROT_IMG, deck id 순서) + 한글 이름판.
     그림은 style 속성 대신 CSSOM 으로 넣음 (보안정책 CSP 대응) */
  function lenCls(s) { return s.length >= 7 ? ' l2' : s.length >= 5 ? ' l1' : ''; }
  function paintFace(el, c, rev) {
    el.innerHTML = '<div class="art"></div><div class="np' + lenCls(c.ko) + '"><b>' + c.ko + '</b><small>' + c.en + '</small></div>';
    if (IMG[c.id]) el.querySelector('.art').style.backgroundImage = 'url("' + IMG[c.id] + '")';
    el.setAttribute('role', 'img');
    el.setAttribute('aria-label', (c.major ? TA.ROMAN[c.no] + ' ' : '') + c.ko + ' 카드' + (rev ? ' · 역방향' : ''));
  }
  function makeFace(c, w, rev, cls) {
    var d = document.createElement('div');
    d.className = 'face' + (rev ? ' rev' : '') + (cls ? ' ' + cls : '');
    if (w) d.style.setProperty('--w', w);
    paintFace(d, c, rev);
    return d;
  }
  var imgCache = {};
  function cardImg(id) {
    if (!imgCache[id]) imgCache[id] = new Promise(function (res) {
      if (!IMG[id]) return res(null);
      var im = new Image(); im.onload = function () { res(im); }; im.onerror = function () { res(null); }; im.src = IMG[id];
    });
    return imgCache[id];
  }
  /* 대문 타로 문: 마법사 · 운명의 수레바퀴 · 달 */
  [1, 10, 18].forEach(function (id) { $('gFan').appendChild(makeFace(TA.deck[id], '66px')); });

  /* ================= 화면 이동 (#saju · #tarot · 대문) ================= */
  var THEME = { gate: '#0d0826', saju: '#f4efe4', tarot: '#0d0826' };
  function route() {
    var v = (location.hash || '').replace('#', '');
    if (v !== 'saju' && v !== 'tarot') v = 'gate';
    closeLb(true);
    document.body.className = 'v-' + v; $('themeColor').setAttribute('content', THEME[v]);
    $('gate').classList.remove('leaving'); [].forEach.call(document.querySelectorAll('.door'), function (d) { d.classList.remove('chosen'); });
    window.scrollTo(0, 0);
    if (v !== 'gate') carry(v);   // 주소(#saju·#tarot)로 바로 들어와도 이름·생년월일 이어받기
    if (v === 'tarot') tarotEnter();
    if (v === 'saju') sajuEnter();
  }
  /* 생년월일·이름은 두 화면이 같이 씀 */
  function carry(to) {
    var nm = to === 'saju' ? ['tnm', 'nm'] : ['nm', 'tnm'], bd = to === 'saju' ? ['tbd', 'bd'] : ['bd', 'tbd'];
    if (!$(nm[1]).value && $(nm[0]).value) $(nm[1]).value = $(nm[0]).value;
    if (!$(bd[1]).value && $(bd[0]).value) { $(bd[1]).value = $(bd[0]).value; if (parseD($(bd[1]).value, true)) $(bd[1] + 'Pick').value = $(bd[1]).value; }
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-go]'); if (!b) return;
    var to = b.getAttribute('data-go');
    if (b.classList.contains('door') && !RM) {
      b.classList.add('chosen'); $('gate').classList.add('leaving');
      setTimeout(function () { location.hash = to; }, 320);
    } else location.hash = to === 'gate' ? '' : to;
  });
  window.addEventListener('hashchange', route);

  /* ================= 사주 ================= */
  var DM = ['큰 나무처럼 곧고 시작을 잘하는 사람', '풀꽃처럼 유연하고 어디서든 잘 어울리는 사람', '태양처럼 밝고 열정이 넘치는 사람', '촛불처럼 섬세하고 따뜻한 사람', '큰 산처럼 듬직하고 믿음직한 사람',
            '너른 들처럼 포용력 있고 실속 있는 사람', '바위처럼 결단력 있고 의리 있는 사람', '보석처럼 예리하고 깔끔한 사람', '바다처럼 지혜롭고 마음이 넓은 사람', '이슬비처럼 총명하고 감성이 풍부한 사람'];
  var ECOL = [['#2f9e62', '#e7f5ec'], ['#e0402f', '#fcebe8'], ['#b67d00', '#fbf1d6'], ['#5f6873', '#eceef1'], ['#2b4a8b', '#e7edf8']];
  var st = { g: 'M', last: null };
  function sajuEnter() { if ($('bd').value && (!st.last || st.lastDate !== $('bd').value)) run(true); }
  $('gender').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    st.g = b.getAttribute('data-v'); [].forEach.call(this.children, function (x) { x.classList.toggle('on', x === b); x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); run(false);
  });
  ['input', 'change'].forEach(function (ev) { $('bd').addEventListener(ev, function () { run(true); }); });
  $('nm').addEventListener('input', function () { if (st.last) renderWho(); });
  $('ph').addEventListener('input', function () { var v = this.value.replace(/[^0-9]/g, '').slice(0, 11); this.value = v.length > 7 ? v.slice(0, 3) + '-' + v.slice(3, v.length - 4) + '-' + v.slice(-4) : v.length > 3 ? v.slice(0, 3) + '-' + v.slice(3) : v; });
  function name() { return $('nm').value.trim(); }
  function daysBetween(a, b) { return Math.round((Date.UTC(b.y, b.m - 1, b.d) - Date.UTC(a.y, a.m - 1, a.d)) / 864e5); }

  function run(anim) {
    var b = parseD($('bd').value); if (!b) return;
    if (anim && st.lastDate === $('bd').value) anim = false;   // 사파리는 날짜 칸을 벗어날 때도 change 를 보내므로 같은 날짜면 연출 생략
    st.lastDate = $('bd').value;
    var p = S.pillars(b.y, b.m, b.d), f = S.fortune(b.y, b.m, b.d, st.g === 'M', T.y, T.m, T.d), du = S.daeun(p, st.g === 'M');
    st.last = { b: b, p: p, f: f, du: du, unborn: b.n > TN, dday: daysBetween(T, b) };
    render(anim);
  }
  function age(b) { return T.y - b.y - ((T.m * 100 + T.d) < (b.m * 100 + b.d) ? 1 : 0); }
  function renderWho() {
    var L = st.last, p = L.p, b = L.b, nm = name();
    var tag = L.unborn ? '<small class="due">출생 예정 D-' + L.dday + '</small>' : '<small>' + (st.g === 'M' ? '남' : '여') + ' · 만 ' + age(b) + '세</small>';
    $('who').innerHTML = '<div class="tti" aria-hidden="true">' + S.ANIMAL_E[p.yb] + '<i>' + S.BR[p.yb] + '</i></div><div><div class="nm">' + (nm ? esc(nm) : (L.unborn ? '아기' : '이름 없음')) + tag + '</div>' +
      '<div class="bd">' + b.y + '년 ' + b.m + '월 ' + b.d + '일' + (L.unborn ? ' 출생 예정' : '생') + ' (양력) · <em>' + S.ANIMAL[p.yb] + '띠</em></div>' +
      '<div class="gz">' + S.gz(S.gzIndex(p.ys, p.yb)) + '년 ' + S.gz(S.gzIndex(p.ms, p.mb)) + '월 ' + S.gz(p.di) + '일</div></div>';
  }
  function tile(lb, s, b, god, me) {
    var es = S.stemEl(s), eb = S.BR_EL[b];
    return '<div class="pl' + (me ? ' me' : '') + '"><span class="lb">' + lb + '</span><span class="god">' + god + '</span>' +
      '<span class="c e' + es + '">' + S.STEM[s] + '</span><span class="c e' + eb + '">' + S.BR[b] + '</span>' +
      '<span class="k">' + S.STEM_K[s] + S.BR_K[b] + '</span><span class="el">' + S.EL_H[es] + '·' + S.EL_H[eb] + '</span></div>';
  }
  /* 오행 상생 고리: 木(위)부터 시계 방향 火 土 金 水. 바깥 원 화살표 = 상생, 안쪽 점선 별 = 상극. 동그라미 크기 = 글자 수 */
  function ohDiagram(c, ds) {
    var cx = 160, cy = 146, R = 90, P = [], h = '', k, a;
    for (k = 0; k < 5; k++) { a = (-90 + k * 72) * Math.PI / 180; P.push([cx + R * Math.cos(a), cy + R * Math.sin(a), Math.cos(a), Math.sin(a)]); }
    h += '<polygon points="' + [0, 2, 4, 1, 3].map(function (i) { return P[i][0].toFixed(1) + ',' + P[i][1].toFixed(1); }).join(' ') + '" fill="none" stroke="#dccfb3" stroke-width="1" stroke-dasharray="3 5"/>';
    h += '<circle cx="' + cx + '" cy="' + cy + '" r="' + R + '" fill="none" stroke="#e2d6bc" stroke-width="1.3"/>';
    h += '<g fill="none" stroke="#c4ab76" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">';
    for (k = 0; k < 5; k++) {
      a = -90 + k * 72 + 36; var r = a * Math.PI / 180, x = cx + R * Math.cos(r), y = cy + R * Math.sin(r);
      h += '<path d="M-4 -4.5L1.5 0L-4 4.5" transform="translate(' + x.toFixed(1) + ' ' + y.toFixed(1) + ') rotate(' + (a + 90) + ')"/>';
    }
    h += '</g>';
    var de = S.stemEl(ds);
    h += '<circle cx="' + cx + '" cy="' + cy + '" r="27" fill="#fffdf8" stroke="#d6c8aa"/><text x="' + cx + '" y="' + (cy - 7) + '" text-anchor="middle" dominant-baseline="central" font-size="21" font-weight="700" fill="' + ECOL[de][0] + '">' + S.STEM[ds] + '</text>' +
      '<text x="' + cx + '" y="' + (cy + 13) + '" text-anchor="middle" dominant-baseline="central" font-size="12" font-weight="700" fill="#736d86" style="font-family:' + "'Pretendard',sans-serif" + '">일간</text>';
    for (k = 0; k < 5; k++) {
      var n = c[k], rr2 = 19 + Math.min(n, 4) * 4.5, q = P[k], col = ECOL[k];
      var lx = q[0] + q[2] * (rr2 + 16), ly = q[1] + q[3] * (rr2 + 13);
      h += '<g class="node"><circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="' + rr2 + '" fill="' + col[1] + '" stroke="' + col[0] + '" stroke-width="' + (n ? 1.6 : 1.2) + '"' + (n ? '' : ' stroke-dasharray="3 3" opacity=".55"') + '/>' +
        '<text x="' + q[0].toFixed(1) + '" y="' + q[1].toFixed(1) + '" text-anchor="middle" dominant-baseline="central" font-size="' + Math.round(15 + Math.min(n, 4) * 2.5) + '" font-weight="700" fill="' + col[0] + '"' + (n ? '' : ' opacity=".55"') + '>' + S.EL_H[k] + '</text>' +
        '<text x="' + lx.toFixed(1) + '" y="' + ly.toFixed(1) + '" text-anchor="middle" dominant-baseline="central" font-size="13" font-weight="700" fill="' + (n ? '#4b4560' : '#77718a') + '" style="font-family:' + "'Pretendard',sans-serif" + '">' + S.EL[k] + ' ' + n + '</text></g>';
    }
    return '<svg class="ohg" viewBox="0 0 320 292" role="img" aria-label="오행 분포 ' + c.map(function (v, i) { return S.EL[i] + ' ' + v; }).join(', ') + '">' + h + '</svg>';
  }
  function render(anim) {
    var L = st.last, p = L.p, f = L.f, d = p.ds;
    renderWho();
    $('pls').innerHTML = tile('일주', p.ds, p.db, '나 (일간)', true) + tile('월주', p.ms, p.mb, S.tenGod(d, p.ms)) + tile('년주', p.ys, p.yb, S.tenGod(d, p.ys));
    var j = p.jieToday, bef = j && j.kst.hh * 60 + j.kst.mm <= 720, ip = j && j.name === '입춘';
    $('warn').innerHTML = j ? '<div class="warn">' + j.name + ' 당일' + (L.unborn ? ' 출생 예정' : ' 출생') + '이에요. ' + j.name + ' 시각(' + pad(j.kst.hh) + ':' + pad(j.kst.mm) + ') ' +
      (bef ? '전에' : '뒤에') + ' 태어나면 ' + (ip ? '띠·년주·월주' : '월주') + '가 ' + (bef ? (ip ? '앞 해' : '앞 달') : (ip ? '다음 해' : '다음 달')) + ' 기준으로 바뀌어요 (지금은 정오 출생으로 계산).</div>' : '';
    var c = S.counts(p);
    $('ohs').innerHTML = ohDiagram(c, d);
    var mx = Math.max.apply(null, c), mn = Math.min.apply(null, c);
    $('meDesc').innerHTML = '나를 나타내는 일간은 <b class="h">' + S.STEM[d] + S.EL_H[S.stemEl(d)] + '</b>, ' + DM[d] + '이에요. ' +
      '<b>' + c.map(function (v, k) { return v === mx ? S.EL[k] : null; }).filter(Boolean).join('·') + '</b> 기운이 많고, ' +
      (mn === 0 ? '<b>' + c.map(function (v, k) { return v === 0 ? S.EL[k] : null; }).filter(Boolean).join('·') + '</b> 기운이 비어 있어요.' : '오행이 고루 있는 편이에요.');
    $('result').classList.toggle('is-unborn', L.unborn);
    $('fTitle').textContent = L.unborn ? '태어날 아기의 기운' : '오늘의 운세';
    $('tgDay').textContent = L.unborn ? 'D-' + L.dday : T.m + '/' + T.d + ' ' + S.gz(tp.di) + '일';
    if (L.unborn) {
      var le = c.indexOf(Math.min.apply(null, c));
      $('unborn').innerHTML = '<span class="dd">D-' + L.dday + '</span>' + L.b.y + '년 ' + L.b.m + '월 ' + L.b.d + '일에 태어나면 <b>' + S.ANIMAL[p.yb] + '띠</b>, 일간 <b>' + S.STEM[d] + S.EL_H[S.stemEl(d)] + '</b>의 아이예요. ' +
        DM[d] + '으로 자랄 기운이에요.<br>아직 태어나기 전이라 오늘의 운세 대신 타고난 기운을 보여 드려요. 채워 주면 좋은 기운은 <b>' + S.EL[le] + '(' + S.EL_H[le] + ')</b>이에요.';
    }
    var stars = ''; for (var i = 0; i < 5; i++) stars += '<i class="' + (i < f.stars ? 'on' : '') + '">★</i>';
    $('stars').innerHTML = stars; $('stars').setAttribute('role', 'img'); $('stars').setAttribute('aria-label', '별 5개 중 ' + f.stars + '개'); $('head').textContent = '“' + f.head + '”';
    $('keys').innerHTML = '<span class="god">' + f.god + '의 날</span>' + f.keys.map(function (k) { return '<span>#' + k + '</span>'; }).join('');
    $('lines').innerHTML = [f.dayLine, f.ttiLine, f.balLine].map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
    $('meters').innerHTML = [['재물', 0], ['대화', 1], ['일', 2], ['컨디션', 3]].map(function (k) { return '<div class="m"><span>' + k[0] + '</span><span class="tr"><i data-w="' + f.scores[k[1]] + '"></i></span><b>' + f.scores[k[1]] + '</b></div>'; }).join('');
    $('lucky').innerHTML = '<div>행운 색<b><i class="dot"></i>' + f.color + '</b></div><div>행운 숫자<b>' + f.number + '</b></div><div>행운 방향<b>' + f.direction + '</b></div>';
    $('lucky').querySelector('.dot').style.background = f.colorHex;   // style 속성 대신 CSSOM (보안정책 CSP 대응)
    var a = L.unborn ? -1 : age(L.b), cur = null; L.du.list.forEach(function (x) { if (x.age <= a) cur = x; });
    $('tgDu').textContent = L.du.n + '세 시작 · ' + (L.du.fwd ? '순행' : '역행');
    $('du').innerHTML = L.du.list.map(function (x) { return '<div class="' + (cur === x ? 'cur' : '') + '"><b>' + S.gz(x.i) + '</b>' + x.age + '세~</div>'; }).join('');
    var R = 46, C = 2 * Math.PI * R, fg = $('ringFg');
    fg.style.strokeDasharray = C.toFixed(1);
    var res = $('result'), first = !res.classList.contains('on');
    res.classList.add('on'); res.classList.toggle('anim', !!anim);
    if (anim || first) { fg.style.transition = 'none'; fg.style.strokeDashoffset = C; void fg.getBoundingClientRect(); fg.style.transition = ''; }
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      fg.style.strokeDashoffset = (C * (1 - f.total / 100)).toFixed(1);
      [].forEach.call(document.querySelectorAll('#meters i'), function (x) { x.style.width = x.getAttribute('data-w') + '%'; });
    }); });
    var n = $('scoreN'), to = f.total, t0 = performance.now();
    if (anim || first) (function step(now) { var k = Math.min(1, (now - t0) / 900); n.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); })(t0); else n.textContent = to;
    if (anim && first) setTimeout(function () { res.scrollIntoView({ behavior: RM ? 'auto' : 'smooth', block: 'start' }); }, 250);
  }

  function shareText() {
    var L = st.last, p = L.p, f = L.f, b = L.b, nm = name() || (L.unborn ? '아기' : '고객');
    var head = '[오늘의 사주] ' + nm + '님\n' + b.y + '년 ' + b.m + '월 ' + b.d + '일' + (L.unborn ? ' 출생 예정' : '생') + '(양력) · ' + S.ANIMAL[p.yb] + '띠\n' +
      '사주: ' + S.gz(p.di) + '일 ' + S.gz(S.gzIndex(p.ms, p.mb)) + '월 ' + S.gz(S.gzIndex(p.ys, p.yb)) + '년\n\n';
    if (L.unborn) return head + '출생까지 D-' + L.dday + ' · 일간 ' + S.STEM[p.ds] + S.EL_H[S.stemEl(p.ds)] + ', ' + DM[p.ds] + '\n\n재미로 보는 사주예요 :)';
    return head + T.m + '월 ' + T.d + '일 오늘의 운세 ' + f.total + '점 ' + '★★★★★'.slice(0, f.stars) + '\n“' + f.head + '”\n· ' + f.dayLine + '\n· ' + f.ttiLine +
      '\n행운 색 ' + f.color + ' · 숫자 ' + f.number + ' · 방향 ' + f.direction + '\n\n재미로 보는 사주예요 :)';
  }
  function wrapText(ctx, text, x, y, maxW, lh, maxLines) {
    var line = '', lines = [];
    text.split(' ').forEach(function (w) { var t = line ? line + ' ' + w : w; if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; });
    if (line) lines.push(line);
    lines.slice(0, maxLines).forEach(function (l, i) { ctx.fillText(l, x, y + i * lh); });
    return Math.min(lines.length, maxLines) * lh;
  }
  function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
  function starsOn(x, W, H, n, seed) {
    for (var i = 0; i < n; i++) { x.fillStyle = 'rgba(255,255,255,' + (0.18 + ((i + seed) * 37 % 50) / 100) + ')'; x.beginPath(); x.arc((i * 173 + seed) % W, (i * 97 + seed) % H, (i % 3) * 0.8 + 0.9, 0, 7); x.fill(); }
  }
  function makeImage() {
    var L = st.last, p = L.p, f = L.f, b = L.b, nm = name() || (L.unborn ? '아기' : '고객');
    var W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    var x = cv.getContext('2d');
    x.fillStyle = '#f4efe4'; x.fillRect(0, 0, W, H);
    var g = x.createRadialGradient(W / 2, 0, 60, W / 2, 240, 760); g.addColorStop(0, '#3d2793'); g.addColorStop(0.5, '#22165c'); g.addColorStop(1, '#120a35');
    x.fillStyle = g; x.fillRect(0, 0, W, 640);
    starsOn(x, W, 600, 64, 7);
    /* 일월: 왼쪽 달 · 오른쪽 해 */
    [[884, '#f6ecd0', '#e9dcb8'], [972, '#ff7a52', '#c9392a']].forEach(function (q) {
      x.strokeStyle = 'rgba(232,199,122,.55)'; x.lineWidth = 2; x.beginPath(); x.arc(q[0], 112, 44, 0, 7); x.stroke();
      var sg = x.createRadialGradient(q[0] - 10, 100, 4, q[0], 112, 32); sg.addColorStop(0, q[1]); sg.addColorStop(1, q[2]);
      x.fillStyle = sg; x.beginPath(); x.arc(q[0], 112, 30, 0, 7); x.fill();
    });
    x.fillStyle = '#e8c77a'; x.font = '700 28px ' + CINZEL; x.fillText('MeAI · SAJU', 72, 98);
    x.fillStyle = '#fff'; x.font = '700 62px ' + SERIF; x.fillText(nm + '님의 ' + (L.unborn ? '사주' : '오늘의 사주'), 72, 176);
    x.fillStyle = '#e4dcff'; x.font = '600 31px ' + SANS; x.fillText(b.y + '년 ' + b.m + '월 ' + b.d + '일' + (L.unborn ? ' 출생 예정' : '생') + '(양력) · ' + S.ANIMAL[p.yb] + '띠 ' + S.ANIMAL_E[p.yb], 72, 232);
    var cols = [['일주', p.ds, p.db], ['월주', p.ms, p.mb], ['년주', p.ys, p.yb]], cw = 256, gap = 28, sx = (W - (cw * 3 + gap * 2)) / 2;
    cols.forEach(function (c, k) {
      var cx = sx + k * (cw + gap), y0 = 276, ch = 328;
      x.shadowColor = 'rgba(0,0,0,.35)'; x.shadowBlur = 30; x.shadowOffsetY = 10;
      var tg = x.createLinearGradient(0, y0, 0, y0 + ch); tg.addColorStop(0, k === 0 ? '#fff8e4' : '#fffcf4'); tg.addColorStop(1, k === 0 ? '#f8ead0' : '#faf2e1');
      x.fillStyle = tg; rr(x, cx, y0, cw, ch, 28); x.fill(); x.shadowColor = 'transparent';
      if (k === 0) { x.strokeStyle = '#b8913f'; x.lineWidth = 4; rr(x, cx, y0, cw, ch, 28); x.stroke(); }
      x.textAlign = 'center'; x.fillStyle = k === 0 ? '#7d5f22' : '#736d86'; x.font = '700 27px ' + SANS; x.fillText(c[0] + (k === 0 ? ' · 나' : ''), cx + cw / 2, y0 + 46);
      [[c[1], S.stemEl(c[1]), S.STEM], [c[2], S.BR_EL[c[2]], S.BR]].forEach(function (q, j) {
        var col = ECOL[q[1]]; x.fillStyle = col[1]; rr(x, cx + 50, y0 + 66 + j * 106, cw - 100, 96, 22); x.fill();
        x.fillStyle = col[0]; x.font = '700 66px ' + SERIF; x.fillText(q[2][q[0]], cx + cw / 2, y0 + 138 + j * 106);
      });
      x.fillStyle = '#4b4560'; x.font = '700 27px ' + SANS; x.fillText(S.STEM_K[c[1]] + S.BR_K[c[2]], cx + cw / 2, y0 + 304);
      x.textAlign = 'left';
    });
    x.fillStyle = '#fffdf8'; rr(x, 60, 664, W - 120, 626, 36); x.fill();
    x.strokeStyle = '#e7ddc8'; x.lineWidth = 2; rr(x, 60, 664, W - 120, 626, 36); x.stroke();
    if (L.unborn) {
      x.fillStyle = '#2a1c6e'; x.font = '700 104px ' + SERIF; x.fillText('D-' + L.dday, 110, 800);
      x.fillStyle = '#1c1730'; x.font = '700 42px ' + SERIF; var h2 = wrapText(x, '일간 ' + S.STEM[p.ds] + S.EL_H[S.stemEl(p.ds)] + ', ' + DM[p.ds], 110, 890, W - 220, 60, 3);
      x.fillStyle = '#4b4560'; x.font = '500 31px ' + SANS; wrapText(x, '아직 태어나기 전이라 오늘의 운세 대신 타고난 기운을 담았어요.', 110, 910 + h2, W - 220, 46, 3);
    } else {
      x.fillStyle = '#2a1c6e'; x.font = '700 116px ' + SERIF; x.fillText(String(f.total), 106, 794);
      var tw = x.measureText(String(f.total)).width; x.fillStyle = '#736d86'; x.font = '700 34px ' + SANS; x.fillText('점', 116 + tw, 794);
      x.fillStyle = '#e0a51f'; x.font = '40px ' + SANS; x.fillText('★★★★★'.slice(0, f.stars), 360, 752); x.fillStyle = '#e6dfcf'; x.fillText('★★★★★'.slice(f.stars), 360 + x.measureText('★★★★★'.slice(0, f.stars)).width, 752);
      x.fillStyle = '#4b2fb0'; x.font = '700 29px ' + SANS; x.fillText(T.m + '월 ' + T.d + '일 ' + S.gz(tp.di) + '일 · ' + f.god + '의 날', 360, 798);
      x.fillStyle = '#1c1730'; x.font = '700 40px ' + SERIF; var hh = wrapText(x, '“' + f.head + '”', 110, 884, W - 220, 56, 3);
      x.fillStyle = '#4b4560'; x.font = '500 30px ' + SANS; var yy = 884 + hh + 16;
      yy += wrapText(x, '· ' + f.dayLine, 110, yy, W - 220, 44, 2) + 8;
      yy += wrapText(x, '· ' + f.ttiLine, 110, yy, W - 220, 44, 2) + 14;
      x.fillStyle = '#f3eefc'; rr(x, 110, yy, W - 220, 70, 22); x.fill();
      x.fillStyle = f.colorHex; x.beginPath(); x.arc(150, yy + 35, 14, 0, 7); x.fill();
      x.fillStyle = '#2a1c6e'; x.font = '700 30px ' + SANS; x.fillText('행운 색 ' + f.color + '  ·  숫자 ' + f.number + '  ·  ' + f.direction, 178, yy + 46);
    }
    x.fillStyle = '#736d86'; x.font = '500 25px ' + SANS; x.textAlign = 'center'; x.fillText('재미로 보는 사주예요 · 양력 · 한국 표준시 기준', W / 2, H - 22); x.textAlign = 'left';
    return cv;
  }
  function toBlob(cv) { return new Promise(function (res) { cv.toBlob(function (b) { res(b); }, 'image/png'); }); }
  function sajuBlob() { return fontsReady().then(function () { return toBlob(makeImage()); }); }
  function ready() { if (!st.last) { toast('먼저 생년월일을 골라 주세요'); $('bd').focus(); return false; } return true; }
  function fileName() { var b = st.last.b; return '오늘의사주_' + (name() || '고객') + '_' + b.y + pad(b.m) + pad(b.d) + '.png'; }
  $('bKakao').addEventListener('click', function () {
    if (!ready()) return;
    var text = shareText();
    sajuBlob().then(function (blob) {
      var file = new File([blob], fileName(), { type: 'image/png' });
      if (navigator.canShare && navigator.canShare({ files: [file] })) return navigator.share({ files: [file], text: text, title: '오늘의 사주' });
      if (navigator.share) return navigator.share({ text: text, title: '오늘의 사주' });
      return copy(text).then(function () { toast('내용을 복사했어요 · 카카오톡 대화창에 붙여 넣으세요'); });
    }).catch(function (e) { if (e && e.name !== 'AbortError') copy(text).then(function () { toast('공유가 안 돼서 내용을 복사했어요'); }); });
  });
  $('bPdf').addEventListener('click', function () {
    if (!ready()) return;
    var nm = name() || '고객', b = st.last.b, old = document.title;
    document.title = '오늘의사주_' + nm + '_' + b.y + pad(b.m) + pad(b.d);
    $('result').classList.remove('anim');
    setTimeout(function () { window.print(); setTimeout(function () { document.title = old; }, 800); }, 60);
  });
  $('bSms').addEventListener('click', function () {
    if (!ready()) return;
    var num = $('ph').value.replace(/[^0-9]/g, '');
    if (num && !/^01[016789]\d{7,8}$/.test(num)) { toast('휴대폰 번호를 다시 확인해 주세요'); $('ph').focus(); return; }
    var ios = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    location.href = 'sms:' + num + (ios ? '&' : '?') + 'body=' + encodeURIComponent(shareText());
  });
  $('bImg').addEventListener('click', function () {
    if (!ready()) return;
    sajuBlob().then(function (blob) {
      var file = new File([blob], fileName(), { type: 'image/png' });
      if (navigator.canShare && navigator.canShare({ files: [file] })) return navigator.share({ files: [file] }).catch(function () {});
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = fileName(); document.body.appendChild(a); a.click(); a.remove();
      toast('이미지를 저장했어요');
    });
  });

  /* ================= 타로 =================
     흐름: 생년월일 → [카드 섞기] (가운데 더미에서 좌우로 3번 섞음) → 78장이 초승달 모양으로 펼쳐짐
           → 한 장 누를 때마다: 바깥으로 들림 → 아래 자리(1~4)로 날아감 → 뒤집힘(역방향이면 거꾸로) → 풀이 등장
           → 남은 카드는 빈자리를 메우며 다시 정렬 → 4장째에 종합 메시지
     카드 배정: 섞을 때 78장 순서를 crypto 난수로 정하고, 고른 순서대로 그 순서의 카드를 엶 (매번 새로) */
  function yeyo(w) { var c = w.charCodeAt(w.length - 1); return c >= 0xAC00 && c <= 0xD7A3 && (c - 0xAC00) % 28 ? '이에요' : '예요'; }
  function rnd(n) {
    var cr = window.crypto || window.msCrypto;
    if (cr && cr.getRandomValues) { var a = new Uint32Array(1), lim = Math.floor(4294967296 / n) * n; do { cr.getRandomValues(a); } while (a[0] >= lim); return a[0] % n; }
    return Math.floor(Math.random() * n);
  }
  function shuffledOrder() { var o = [], i; for (i = 0; i < 78; i++) o.push(i); for (i = 77; i > 0; i--) { var j = rnd(i + 1), t = o[i]; o[i] = o[j]; o[j] = t; } return o; }
  function kwHtml(txt) { return txt[0].split('·').map(function (w) { return '#' + w; }).join(' '); }
  function fullName(c) { return (c.major ? TA.ROMAN[c.no] + ' ' : '') + c.ko; }

  var TT = { phase: 'idle', cards: [], spread: [], picks: [], order: null, lock: false, G: null, built: false, birth: null };
  var stage = $('stage'), ROM = ['I', 'II', 'III', 'IV'];
  function tname() { return $('tnm').value.trim(); }

  function buildStage() {
    var h = '', i;
    for (i = 0; i < 4; i++) h += '<div class="t-slot" id="slot' + i + '"><span class="no">' + ROM[i] + '</span></div><div class="t-slab" id="slab' + i + '">' + TA.POS[i].k + '<em></em></div>';
    h += '<div class="t-msg" id="tmsg"></div>';
    for (i = 0; i < 78; i++) h += '<div class="tc" data-i="' + i + '"><div class="in"><div class="bk"></div><div class="fc face"></div></div></div>';
    stage.innerHTML = h;
    TT.cards = [].slice.call(stage.querySelectorAll('.tc'));
    TT.built = true;
  }
  /* 무대 크기에 맞춰 초승달·자리 좌표 계산 */
  function geom() {
    var W = stage.clientWidth, sw = Math.min(92, Math.floor((W - 24 - 30) / 4)), sh = Math.round(sw * 1.72);
    var k0 = 0.54, smin = 0.4, amax = 74 * Math.PI / 180, Lt = sh * k0 * smin;
    var R = Math.max(90, (W / 2 - 8) / Math.sin(amax) - Lt);
    var cy = R + sh * k0 + 16, slotsY = Math.round(cy - R * Math.cos(amax) + 24), gap = Math.round((W - 24 - sw * 4) / 3);
    var G = { W: W, sw: sw, sh: sh, k0: k0, smin: smin, amax: amax, R: R, cy: cy, slotsY: slotsY, gap: gap, H: slotsY + sh + 40 };
    stage.style.height = G.H + 'px'; stage.style.setProperty('--sw', sw + 'px');
    TT.cards.forEach(function (el) { el.style.width = sw + 'px'; el.style.height = sh + 'px'; });
    for (var i = 0; i < 4; i++) {
      var sx = 12 + i * (sw + gap), s = $('slot' + i), l = $('slab' + i);
      s.style.left = sx + 'px'; s.style.top = slotsY + 'px'; s.style.width = sw + 'px'; s.style.height = sh + 'px';
      l.style.left = (sx - 12) + 'px'; l.style.width = (sw + 24) + 'px'; l.style.top = (slotsY + sh + 7) + 'px';
    }
    var m = $('tmsg'); m.style.top = Math.round(cy - R + sh * 0.22) + 'px';
    TT.G = G; return G;
  }
  function setT(el, p) { el._p = p; el.style.transform = 'translate(' + p.x.toFixed(1) + 'px,' + p.y.toFixed(1) + 'px) rotate(' + p.r.toFixed(2) + 'deg) scale(' + p.s.toFixed(3) + ')'; }
  /* 초승달: 원호를 따라 놓되 가운데는 크고 양 끝은 작게 → 바깥 테두리가 가늘어지는 초승달 실루엣 */
  function spreadPos(i, n) {
    var G = TT.G, t = n <= 1 ? 0.5 : i / (n - 1), a = -G.amax + 2 * G.amax * t, s = G.smin + (1 - G.smin) * Math.sin(Math.PI * t);
    var L = G.sh * G.k0 * s, r = G.R + L / 2;
    return { x: G.W / 2 + r * Math.sin(a) - G.sw / 2, y: G.cy - r * Math.cos(a) - G.sh / 2, r: a * 180 / Math.PI, s: G.k0 * s };
  }
  function stackPos(i) { var G = TT.G; return { x: G.W / 2 - G.sw / 2, y: G.cy - G.R * 0.62 - G.sh / 2 - i * 0.18, r: (i % 5 - 2) * 0.6, s: G.k0 * 1.35 }; }
  function slotPos(k) { var G = TT.G; return { x: 12 + k * (G.sw + G.gap), y: G.slotsY, r: 0, s: 1 }; }
  function msg(html) { var m = $('tmsg'); m.innerHTML = html; m.style.opacity = html ? 1 : 0; }
  function counter() { return '<span class="cnt">' + TT.picks.length + ' / 4</span>'; }

  function tarotEnter() {
    if (!TT.built) { buildStage(); geom(); TT.cards.forEach(function (el, i) { el.style.transition = 'none'; setT(el, stackPos(i)); }); void stage.offsetWidth; TT.cards.forEach(function (el) { el.style.transition = ''; }); msg(''); }
    else relayout();
    tBirthUpdate();
  }
  function relayout() {
    if (!TT.built) return;
    geom();
    TT.cards.forEach(function (el) { el.style.transition = 'none'; });
    if (TT.phase === 'idle' || TT.phase === 'shuffling') TT.cards.forEach(function (el, i) { setT(el, stackPos(i)); });
    else { TT.spread.forEach(function (el, i) { setT(el, spreadPos(i, TT.spread.length)); }); TT.picks.forEach(function (p, k) { setT(p.el, slotPos(k)); }); }
    void stage.offsetWidth; TT.cards.forEach(function (el) { el.style.transition = ''; });
  }
  var rzT; window.addEventListener('resize', function () { clearTimeout(rzT); rzT = setTimeout(function () { if (document.body.className === 'v-tarot' && TT.G && stage.clientWidth !== TT.G.W) relayout(); }, 120); });

  function tBirthUpdate() {
    var b = parseD($('tbd').value, true), go = $('tGo');
    if (!b) { $('tBirth').classList.remove('on'); TT.birth = null; if (TT.phase === 'idle') { go.disabled = true; go.textContent = '생년월일을 넣어 주세요'; } return; }
    var n = TA.birthCard(b.y, b.m, b.d), c = TA.deck[n]; TT.birth = n;
    $('tBirth').innerHTML = '<span>나의 탄생 카드는 <b>' + TA.ROMAN[n] + ' ' + c.ko + '</b>' + yeyo(c.ko) + '<br>' + c.up[0] + '</span>';
    $('tBirth').insertBefore(makeFace(c, '44px'), $('tBirth').firstChild);
    $('tBirth').classList.add('on');
    if (TT.phase === 'idle') { go.disabled = false; go.textContent = '카드 섞기'; }
  }
  ['input', 'change'].forEach(function (ev) { $('tbd').addEventListener(ev, function () { if (/^\d{4}-\d{2}-\d{2}$/.test(this.value)) parseD(this.value); tBirthUpdate(); }); });

  $('tGo').addEventListener('click', function () {
    if (!TT.birth && TT.birth !== 0) { toast('먼저 생년월일을 넣어 주세요'); return; }
    if (TT.phase === 'idle') shuffle();
    else if (TT.phase === 'done' || TT.phase === 'spread') resetAndShuffle();
  });

  async function shuffle() {
    if (TT.lock) return; TT.lock = true; TT.phase = 'shuffling';
    var go = $('tGo'); go.disabled = true; go.textContent = '카드를 섞는 중…';
    msg('');
    stage.scrollIntoView({ behavior: RM ? 'auto' : 'smooth', block: 'center' });
    TT.order = shuffledOrder(); TT.picks = [];
    var G = TT.G, cards = TT.cards;
    for (var round = 0; round < 3; round++) {
      cards.forEach(function (el, i) {
        var side = ((i + round) % 2) ? 1 : -1, b = stackPos(i);
        el.style.transitionDuration = '.24s'; el.style.transitionDelay = (i % 13) * 6 + 'ms';
        setT(el, { x: b.x + side * G.sw * 0.62, y: b.y - (i % 9) * 1.2, r: side * 9, s: b.s });
      });
      await wait(320);
      cards.forEach(function (el, i) { setT(el, stackPos(i)); });
      await wait(300);
    }
    /* 초승달로 펼치기 (왼쪽 끝부터 차례로) */
    TT.spread = cards.slice();
    cards.forEach(function (el, i) { el.style.transitionDuration = '.7s'; el.style.transitionDelay = (i * 9) + 'ms'; setT(el, spreadPos(i, 78)); });
    await wait(720 + 78 * 9);
    cards.forEach(function (el) { el.style.transitionDuration = ''; el.style.transitionDelay = ''; el.classList.add('sp'); });
    TT.phase = 'spread'; TT.lock = false;
    go.disabled = false; go.textContent = '다시 섞기';
    msg('<b>마음속 질문을 떠올리고</b><span>끌리는 카드 4장을 차례로 눌러 주세요</span>' + counter());
  }

  stage.addEventListener('click', function (e) {
    var el = e.target.closest('.tc'); if (!el) return;
    if (el.classList.contains('picked')) { var k = +el.getAttribute('data-k'); if (TT.picks[k]) openLb(k); return; }
    if (TT.phase === 'spread' && el.classList.contains('sp')) pick(el);
    else if (TT.phase === 'idle' && !TT.lock) { if (TT.birth == null) { toast('먼저 생년월일을 넣어 주세요'); $('tbd').focus(); } else shuffle(); }
  });

  stage.addEventListener('keydown', function (e) {
    if (e.target !== stage || (e.key !== 'Enter' && e.key !== ' ')) return;
    e.preventDefault();
    if (TT.phase === 'spread' && !TT.lock && TT.spread.length) pick(TT.spread[Math.floor(TT.spread.length / 2)]);
    else if (TT.phase === 'idle' && !TT.lock) { if (TT.birth == null) { toast('먼저 생년월일을 넣어 주세요'); $('tbd').focus(); } else shuffle(); }
    else if (TT.phase === 'done') openLb(0);
  });

  async function pick(el) {
    if (TT.lock || TT.picks.length >= 4) return;
    TT.lock = true;
    var k = TT.picks.length, card = TA.deck[TT.order[k]], rev = rnd(2) === 1;
    TT.spread.splice(TT.spread.indexOf(el), 1);
    el.classList.remove('sp'); el.classList.add('picked'); el.setAttribute('data-k', k); el.style.zIndex = 300 + k;
    var fc = el.querySelector('.fc'); paintFace(fc, card, rev); fc.classList.toggle('rv', rev);
    var img = cardImg(card.id);
    /* ① 바깥으로 쏙 들림 */
    var p = el._p, a = p.r * Math.PI / 180;
    el.style.transitionDuration = '.22s';
    setT(el, { x: p.x + 34 * Math.sin(a), y: p.y - 34 * Math.cos(a), r: p.r, s: p.s * 1.3 });
    await wait(230);
    /* ② 남은 카드가 빈자리를 메우고, 고른 카드는 자리로 날아감 */
    TT.spread.forEach(function (c, i) { setT(c, spreadPos(i, TT.spread.length)); });
    el.style.transitionDuration = '.62s';
    setT(el, slotPos(k));
    await wait(640);
    /* ③ 뒤집기 */
    el.classList.add('flip');
    await wait(600);
    el.style.transitionDuration = '';
    el.classList.add('glow'); fc.classList.add('sheen'); setTimeout(function () { el.classList.remove('glow'); }, 900);
    var sl = $('slab' + k); sl.querySelector('em').textContent = rev ? '역방향' : '정방향'; sl.querySelector('em').className = rev ? 'rv' : 'up'; sl.classList.add('on');
    TT.picks.push({ el: el, card: card, rev: rev, img: img });
    addReading(k);
    TT.lock = false;
    if (TT.picks.length === 4) finish();
    else msg('<b>' + ['', '좋아요, 두 번째 카드를', '세 번째 카드를', '마지막 한 장을'][TT.picks.length] + '</b><span>' + TA.POS[TT.picks.length].k + ' · ' + TA.POS[TT.picks.length].d + '</span>' + counter());
  }

  function addReading(k) {
    var P = TT.picks[k], c = P.card, txt = P.rev ? c.rv : c.up, pos = TA.POS[k];
    var div = document.createElement('article'); div.className = 'trd'; div.id = 'trd' + k;
    div.innerHTML = '<div class="trd-h"><span class="n">' + (k + 1) + '</span><b>' + pos.k + '</b> · ' + pos.d + '</div>' +
      '<div class="trd-b"><button type="button" class="trd-card" data-k="' + k + '" aria-label="' + c.ko + ' 카드 크게 보기"></button><div>' +
      '<div class="trd-nm">' + fullName(c) + '</div><span class="trd-en">' + c.en + '</span>' +
      '<span class="ori ' + (P.rev ? 'rv' : 'up') + '">' + (P.rev ? '역방향' : '정방향') + '</span>' +
      '<div class="trd-kw">' + kwHtml(txt) + '</div><p>' + txt[1] + '</p></div></div>';
    div.querySelector('.trd-card').appendChild(makeFace(c, '76px', P.rev));
    $('reads').appendChild(div);
  }

  function summary() {
    var P = TT.picks, majors = P.filter(function (p) { return p.card.major; }), revs = P.filter(function (p) { return p.rev; }).length;
    var sc = [0, 0, 0, 0]; P.forEach(function (p) { if (!p.card.major) sc[p.card.suit]++; });
    var top = sc.indexOf(Math.max.apply(null, sc)), lines = [];
    if (majors.length >= 2) lines.push('메이저 카드가 ' + majors.length + '장이나 나왔어요. 오늘 일어나는 일은 생각보다 오래, 크게 영향을 줄 수 있어요.');
    else if (majors.length === 1) { var mj = majors[0]; lines.push('오늘의 중심은 메이저 카드 <b>「' + mj.card.ko + '」</b>. ' + (mj.rev ? '「' + mj.card.rv[0].split('·')[0] + '」 쪽으로 기울지 않게 조심하세요.' : '「' + mj.card.up[0].split('·')[0] + '」의 기운을 믿고 움직이세요.')); }
    else lines.push('모두 마이너 카드예요. 큰 사건보다 일상의 작은 선택이 쌓여 흐름을 만드는 날이에요.');
    if (sc[top] >= 2) lines.push(TA.SUIT_SUM[top]);
    lines.push(revs === 0 ? '모든 카드가 정방향이에요. 막힘 없이 흐르는 기운이니 망설이지 말고 움직이세요.' : revs <= 2 ? '역방향이 ' + revs + '장 있어요. 살짝 엇박자가 나는 부분만 점검하면 충분해요.' : '역방향이 ' + revs + '장이에요. 속도를 늦추고 한 번 돌아보면 오히려 길이 보여요.');
    var bc = TA.deck[TT.birth], hit = P.some(function (p) { return p.card.id === TT.birth; });
    lines.push(hit ? '<b>탄생 카드 ' + bc.ko + '</b>가 직접 나왔어요! 오늘은 나다움이 가장 큰 무기예요.' : '나의 탄생 카드 <b>' + TA.ROMAN[TT.birth] + ' ' + bc.ko + '</b>의 힘(' + bc.up[0] + ')을 떠올리면 도움이 돼요.');
    var key = P[2].rev ? P[2].card.rv[0] : P[2].card.up[0], flow = P[3].rev ? P[3].card.rv[0] : P[3].card.up[0];
    var one = (P[2].rev ? '「' + key.split('·')[0] + '」에 귀 기울이면, ' : '「' + key.split('·')[0] + '」의 힘을 빌리면, ') +
      (P[3].rev ? '「' + flow.split('·')[0] + '」의 신호를 살필수록 흐름이 풀려요.' : '「' + flow.split('·')[0] + '」의 흐름이 다가와요.');
    var tags = P.map(function (p) { return (p.rev ? p.card.rv[0] : p.card.up[0]).split('·')[0]; });
    return { lines: lines, one: one, tags: tags };
  }
  function finish() {
    TT.phase = 'done';
    TT.spread.forEach(function (el) { el.classList.remove('sp'); el.classList.add('dim'); });
    msg('<b>오늘의 카드 4장이 모두 열렸어요</b><span>카드를 누르면 크게 볼 수 있어요</span>');
    var S2 = summary(), nm = tname();
    $('tsum').innerHTML = '<div class="orn" aria-hidden="true"><svg><use href="#spark"/></svg></div><h3>' + (nm ? '<span class="nm">' + esc(nm) + '</span>님의 ' : '') + '오늘의 타로 메시지</h3>' +
      '<div class="t-row" id="tRow"></div>' +
      '<p class="one">' + S2.one + '</p><div class="tags">' + S2.tags.map(function (t) { return '<span>#' + t + '</span>'; }).join('') + '</div>' +
      '<ul>' + S2.lines.map(function (l) { return '<li>' + l + '</li>'; }).join('') + '</ul>' +
      '<div class="t-btns"><button type="button" class="btn again" id="tAgain">다시 뽑기</button><button type="button" class="btn kakao" id="tShare">카톡으로 보내기</button><button type="button" class="btn timg" id="tImg">이미지로 저장</button></div>' +
      '<p class="t-hint">카톡으로 보내기 → 공유 창에서 <b>카카오톡</b>을 고르면 카드 4장과 점괘가 담긴 이미지가 함께 가요.</p>';
    TT.picks.forEach(function (P, k) {
      var b = document.createElement('button'); b.type = 'button'; b.setAttribute('data-k', k); b.setAttribute('aria-label', TA.POS[k].k + ' · ' + P.card.ko + ' 크게 보기');
      b.appendChild(makeFace(P.card, '64px', P.rev)); b.appendChild(document.createTextNode(TA.POS[k].k)); $('tRow').appendChild(b);
    });
    $('tsum').classList.add('on');
    $('tAgain').addEventListener('click', resetAndShuffle);
    $('tShare').addEventListener('click', function () { shareTarot(S2, true); });
    $('tImg').addEventListener('click', function () { shareTarot(S2, false); });
    $('tGo').textContent = '다시 뽑기';
    setTimeout(function () { $('tsum').scrollIntoView({ behavior: RM ? 'auto' : 'smooth', block: 'start' }); }, 500);
  }

  /* ---------- 카드 크게 보기 ---------- */
  var lastFocus = null;
  function openLb(k) {
    var P = TT.picks[k]; if (!P) return;
    var c = P.card, txt = P.rev ? c.rv : c.up;
    $('lbIn').innerHTML = '<div class="lb-pos">' + (k + 1) + ' · ' + TA.POS[k].k + '</div><div id="lbCard"></div>' +
      '<div class="lb-nm" id="lbNm">' + fullName(c) + '</div><div class="lb-en">' + c.en + '</div>' +
      '<span class="ori ' + (P.rev ? 'rv' : 'up') + '">' + (P.rev ? '역방향' : '정방향') + '</span>' +
      '<div class="lb-kw">' + kwHtml(txt) + '</div><p class="lb-tx">' + txt[1] + '</p><button type="button" class="lb-x" id="lbX">닫기</button>';
    $('lbCard').appendChild(makeFace(c, '', P.rev, 'big sheen'));
    lastFocus = document.activeElement;
    $('lb').classList.add('on'); document.body.style.overflow = 'hidden';
    $('lbX').focus();
  }
  function closeLb(quiet) {
    if (!$('lb').classList.contains('on')) return;
    $('lb').classList.remove('on'); $('lbIn').innerHTML = ''; document.body.style.overflow = '';
    if (!quiet && lastFocus && lastFocus.focus) lastFocus.focus();
  }
  $('lb').addEventListener('click', function (e) { if (e.target === this || e.target.id === 'lbX') closeLb(); });
  document.addEventListener('keydown', function (e) {
    if (!$('lb').classList.contains('on')) return;
    if (e.key === 'Escape') closeLb();
    else if (e.key === 'Tab') { e.preventDefault(); $('lbX').focus(); }
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.trd-card, .t-row button'); if (!b) return;
    openLb(+b.getAttribute('data-k'));
  });

  /* ---------- 타로 결과 이미지 (카드 4장 + 점괘) ----------
     카드 그림은 파일 안의 그림(data:)이라 캔버스가 오염되지 않음 → 오프라인·보안정책(CSP)에서도 저장 가능 */
  function drawFace(x, c, rev, X, Y, w, img) {
    var h = w * 1.72, p = w * 0.06, aw = w - 2 * p, ah = aw * 1.6923;
    x.save(); x.translate(X + w / 2, Y + h / 2); if (rev) x.rotate(Math.PI); x.translate(-w / 2, -h / 2);
    x.shadowColor = 'rgba(0,0,0,.5)'; x.shadowBlur = 28; x.shadowOffsetY = rev ? -10 : 10;
    var g = x.createLinearGradient(0, 0, w, h); g.addColorStop(0, '#fcf6e6'); g.addColorStop(0.6, '#f3e7c9'); g.addColorStop(1, '#ead9b2');
    x.fillStyle = g; rr(x, 0, 0, w, h, w * 0.055); x.fill(); x.shadowColor = 'transparent';
    x.strokeStyle = 'rgba(184,145,63,.8)'; x.lineWidth = 2; rr(x, w * 0.028, w * 0.028, w - w * 0.056, h - w * 0.056, w * 0.035); x.stroke();
    if (img) x.drawImage(img, p, p, aw, ah); else { x.fillStyle = '#e9dcc0'; x.fillRect(p, p, aw, ah); }
    x.strokeStyle = 'rgba(42,31,14,.65)'; x.lineWidth = 1.5; x.strokeRect(p, p, aw, ah);
    var py = p + ah, ph = h - py, fs = c.ko.length >= 7 ? 0.094 : c.ko.length >= 5 ? 0.108 : 0.125;
    x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillStyle = '#2a1f0e';
    x.font = '700 ' + Math.round(w * fs) + 'px ' + SERIF; x.fillText(c.ko, w / 2, py + ph * 0.52);
    x.restore(); x.textAlign = 'left'; x.textBaseline = 'alphabetic';
  }
  function makeTarotImage(S2, imgs, H) {   // H 없이 부르면 한 번 그려 본 뒤 내용 길이에 맞춰 다시 그림
    if (!H) H = makeTarotImage(S2, imgs, 2600).end + 100;
    var W = 1080, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    var x = cv.getContext('2d'), nm = tname() || '고객', i;
    var g = x.createRadialGradient(W / 2, 0, 40, W / 2, H * 0.3, H); g.addColorStop(0, '#3a2391'); g.addColorStop(0.45, '#1d1247'); g.addColorStop(1, '#0d0826');
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    starsOn(x, W, 900, 80, 3);
    x.strokeStyle = 'rgba(232,199,122,.55)'; x.lineWidth = 2; rr(x, 24, 24, W - 48, H - 48, 28); x.stroke();
    x.strokeStyle = 'rgba(232,199,122,.25)'; x.lineWidth = 1; rr(x, 36, 36, W - 72, H - 72, 20); x.stroke();
    x.textAlign = 'center';
    x.fillStyle = '#e8c77a'; x.font = '700 28px ' + CINZEL; x.fillText('MeAI · TAROT', W / 2, 104);
    x.fillStyle = '#fff'; x.font = '700 58px ' + SERIF; x.fillText(nm + '님의 오늘의 타로', W / 2, 180);
    var bc = TA.deck[TT.birth];
    x.fillStyle = '#d6cdf6'; x.font = '600 28px ' + SANS; x.fillText(T.y + '년 ' + T.m + '월 ' + T.d + '일 (' + T.w + ') · 탄생 카드 ' + TA.ROMAN[TT.birth] + ' ' + bc.ko, W / 2, 230);
    /* 카드 4장 */
    var cw = 222, ch = cw * 1.72, gap = 22, sx = (W - cw * 4 - gap * 3) / 2, cyTop = 280;
    TT.picks.forEach(function (P, k) {
      var X = sx + k * (cw + gap);
      drawFace(x, P.card, P.rev, X, cyTop, cw, imgs[k]);
      x.textAlign = 'center'; x.fillStyle = '#e8e1ff'; x.font = '700 26px ' + SANS; x.fillText((k + 1) + ' ' + TA.POS[k].k, X + cw / 2, cyTop + ch + 46);
      x.fillStyle = P.rev ? '#ffaaa5' : '#9fe6bd'; x.font = '700 24px ' + SANS; x.fillText(P.rev ? '역방향' : '정방향', X + cw / 2, cyTop + ch + 80);
    });
    /* 점괘 */
    var py = cyTop + ch + 116;
    x.fillStyle = 'rgba(255,255,255,.07)'; rr(x, 60, py, W - 120, H - py - 100, 32); x.fill();
    x.strokeStyle = 'rgba(232,199,122,.35)'; x.lineWidth = 2; rr(x, 60, py, W - 120, H - py - 100, 32); x.stroke();
    x.textAlign = 'left'; x.fillStyle = '#f8e7b4'; x.font = '700 36px ' + SERIF;
    var y = py + 68; y += wrapText(x, '✦ ' + S2.one, 100, y, W - 200, 52, 2) + 20;
    TT.picks.forEach(function (P, k) {
      var c = P.card, txt = P.rev ? c.rv : c.up;
      x.fillStyle = '#e8c77a'; x.beginPath(); x.arc(116, y - 10, 19, 0, 7); x.fill();
      x.fillStyle = '#2a1d00'; x.font = '700 24px ' + CINZEL; x.textAlign = 'center'; x.fillText(String(k + 1), 116, y - 1); x.textAlign = 'left';
      x.fillStyle = '#fff'; x.font = '700 31px ' + SERIF; x.fillText(TA.POS[k].k + ' · ' + fullName(c) + (P.rev ? ' (역)' : ''), 150, y);
      x.fillStyle = '#ddd6f6'; x.font = '500 28px ' + SANS;
      y += 44 + wrapText(x, txt[1], 150, y + 44, W - 250, 40, 2) + 20;
    });
    x.textAlign = 'center'; x.fillStyle = 'rgba(214,205,246,.62)'; x.font = '500 23px ' + SANS;
    x.fillText('재미로 보는 타로예요 · 라이더-웨이트-스미스 타로(1909) · 매번 새로 섞어요', W / 2, H - 58);
    cv.end = y + 4; return cv;
  }
  function shareTarot(S2, kakao) {
    var text = tarotText(S2), fname = '오늘의타로_' + (tname() || '고객') + '_' + T.y + pad(T.m) + pad(T.d) + '.png';
    Promise.all([fontsReady()].concat(TT.picks.map(function (p) { return p.img || cardImg(p.card.id); }))).then(function (r) {
      return toBlob(makeTarotImage(S2, r.slice(1)));
    }).then(function (blob) {
      var file = new File([blob], fname, { type: 'image/png' });
      if (navigator.canShare && navigator.canShare({ files: [file] })) return navigator.share(kakao ? { files: [file], text: text, title: '오늘의 타로' } : { files: [file] });
      var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = fname; document.body.appendChild(a); a.click(); a.remove();
      if (kakao) return copy(text).then(function () { toast('이미지를 저장하고 글을 복사했어요 · 카톡에 이미지와 함께 붙여 넣으세요'); });
      toast('이미지를 저장했어요');
    }).catch(function (e) { if (e && e.name !== 'AbortError') copy(text).then(function () { toast('공유가 안 돼서 내용을 복사했어요'); }); });
  }
  function tarotText(S2) {
    var nm = tname() || '고객', t = '[오늘의 타로] ' + nm + '님 · ' + T.m + '월 ' + T.d + '일\n\n';
    TT.picks.forEach(function (p, k) { var c = p.card; t += (k + 1) + '. ' + TA.POS[k].k + ' : ' + fullName(c) + ' (' + (p.rev ? '역방향' : '정방향') + ')\n   ' + (p.rev ? c.rv[1] : c.up[1]) + '\n'; });
    return t + '\n✦ ' + S2.one + '\n\n재미로 보는 타로예요 :)';
  }
  async function resetAndShuffle() {
    if (TT.lock) return; TT.lock = true;
    $('tsum').classList.remove('on'); $('reads').innerHTML = '';
    for (var i = 0; i < 4; i++) { $('slab' + i).classList.remove('on'); }
    TT.picks.forEach(function (p) { p.el.classList.remove('flip'); });
    await wait(TT.picks.length ? 450 : 0);
    TT.cards.forEach(function (el, i) { el.classList.remove('sp', 'picked', 'dim', 'glow'); el.style.zIndex = ''; el.removeAttribute('data-k'); el.style.transitionDuration = '.5s'; setT(el, stackPos(i)); });
    await wait(520);
    TT.cards.forEach(function (el) { var fc = el.querySelector('.fc'); el.style.transitionDuration = ''; fc.innerHTML = ''; fc.className = 'fc face'; fc.removeAttribute('role'); fc.removeAttribute('aria-label'); });
    TT.picks = []; TT.phase = 'idle'; TT.lock = false;
    shuffle();
  }

  route();
})();
