/* MeAI 홈 넛지 v5 · 화법 전체 보기 (798건 찾기 · 배너 설정 · 내 화법 제출)
 * 서버에서 40건씩 받아 온다(api.listTalks). 목록에서는 설정과 상관없이 798건 전부를 볼 수 있다.
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ, I = NZ.I, esc = NZ.esc, F = NZ.fmt;
  const S = { tab: 'list', cat: '', q: '', sit: '', sort: 'rec', only: '', page: 0, items: [], total: 0, cats: null, stats: null, hot: [], sel: null };
  const SITS = ['오프닝·접근', '니즈환기', '상품설명', '반론처리', '클로징', '관계관리', '다짐·구호'];
  let ov = null, root = null, qT = 0;

  NZ.talks = {
    open(opt) {
      opt = opt || {};
      S.tab = opt.tab || 'list'; S.page = 0; S.items = []; S.sel = null;
      root = NZ.el('<div class="nz-modal nz-talks" role="document"><div class="nz-mh"><h2>화법 전체 보기</h2><span class="meta">9월 필살 화법 공모 798건 · 카테고리 14개</span>' +
        '<div class="nz-tabs" role="tablist">' + [['list', '화법 목록'], ['banner', '배너 설정'], ['submit', '내 화법 제출']].map((t) => '<button type="button" role="tab" data-tab="' + t[0] + '" aria-selected="' + (S.tab === t[0]) + '">' + t[1] + '</button>').join('') + '</div>' +
        '<button type="button" class="x" data-x aria-label="닫기">' + I.x + '</button></div><div class="nz-mb"></div></div>');
      ov = NZ.overlay(root, { label: '화법 전체 보기', skip: false });
      root.addEventListener('click', onClick);
      root.addEventListener('input', onInput);
      root.addEventListener('change', onInput);
      NZ.log('talk_library', 'open');
      draw(); load(true);
    }
  };

  function load(reset) {
    if (reset) { S.page = 0; S.items = []; }
    return NZ.api.listTalks({ cat: S.cat, q: S.q, sit: S.sit, sort: S.sort, only: S.only, page: S.page, size: 40 }).then((r) => {
      const first = !S.cats;
      S.items = S.items.concat(r.items); S.total = r.total; S.cats = r.cats; S.stats = r.stats; S.hot = r.hot;
      if (!S.sel && S.items[0]) S.sel = S.items[0];
      if (S.tab === 'list') drawList(); else if (first) draw();
    });
  }
  function draw() {
    NZ.$$('[data-tab]', root).forEach((b) => b.setAttribute('aria-selected', String(b.dataset.tab === S.tab)));
    const mb = root.querySelector('.nz-mb');
    if (S.tab === 'list') {
      NZ.html(mb, '<nav class="nz-tl-cats" aria-label="카테고리"></nav><section class="nz-tl-list"><div class="nz-tl-tools">' +
        '<div class="nz-search">' + I.search + '<input type="search" data-in="q" placeholder="화법 내용 · 이름 · 본부 · 담보로 찾기" value="' + esc(S.q) + '" aria-label="화법 찾기"></div>' +
        '<select class="nz-sel" data-in="sit" aria-label="상황"><option value="">모든 상황</option>' + SITS.map((s) => '<option' + (S.sit === s ? ' selected' : '') + '>' + s + '</option>').join('') + '</select>' +
        '<select class="nz-sel" data-in="sort" aria-label="정렬">' + [['rec', '추천순'], ['likes', '공감 많은 순'], ['used', '써봤어요 많은 순'], ['short', '짧은 화법 먼저']].map((o) => '<option value="' + o[0] + '"' + (S.sort === o[0] ? ' selected' : '') + '>' + o[1] + '</option>').join('') + '</select></div>' +
        '<div class="nz-tl-hot"></div><div class="nz-tl-items" aria-label="화법 목록"></div></section><aside class="nz-tl-detail" aria-live="polite"></aside>');
      drawList();
    } else if (S.tab === 'banner') drawBanner(mb);
    else drawSubmit(mb);
  }
  function drawList() {
    const mb = root && root.querySelector('.nz-mb'); if (!mb || S.tab !== 'list') return;
    const nav = mb.querySelector('.nz-tl-cats'), st = S.stats || { src: 798, rec: 454, block: 71, noise: 40 };
    if (S.cats && nav) {
      NZ.html(nav, '<button type="button" data-cat="" aria-pressed="' + (!S.cat && !S.only) + '">전체<span class="n">' + F.n(st.src) + '</span></button>' +
        Object.keys(S.cats).map((k) => '<button type="button" data-cat="' + k + '" aria-pressed="' + (S.cat === k) + '">' + esc(S.cats[k].name) + '<span class="n">' + S.cats[k].all + '</span></button>').join('') +
        '<div class="gap"></div>' + [['rec', '추천 화법', st.rec], ['best', '우수사례 · 한 줄 명화법', 30], ['copied', '내가 따라 쓴', ''], ['saved', '저장한', ''], ['mine', '내가 제출한', ''], ['block', '검토 필요', st.block], ['short', '짧은 응답', st.noise]]
          .map((o) => '<button type="button" data-only="' + o[0] + '" aria-pressed="' + (S.only === o[0]) + '">' + o[1] + '<span class="n">' + o[2] + '</span></button>').join(''));
    }
    const hot = mb.querySelector('.nz-tl-hot');
    NZ.html(hot, S.hot.length && !S.q && !S.cat && !S.only ? S.hot.map((t, i) => '<button type="button" data-pick="' + t.id + '"><b>현장 인기 ' + (i + 1) + '</b>' + esc(t.head.slice(0, 54)) + (t.head.length > 54 ? '…' : '') + '</button>').join('') : '');
    const list = mb.querySelector('.nz-tl-items');
    NZ.html(list, '<p class="nz-note">' + F.n(S.total) + '건' + (S.q ? ' · 「' + esc(S.q) + '」' : '') + '</p>' + S.items.map((t) => '<button type="button" class="nz-tl-item" data-pick="' + t.id + '" aria-pressed="' + !!(S.sel && S.sel.id === t.id) + '">' +
      '<div class="h">' + esc(t.head) + '</div><div class="m"><span class="nz-chip">' + esc(t.catName) + '</span>' + (t.grade === 'rec' ? '<span class="nz-chip red">추천</span>' : '') + (t.src && t.src !== 'FP 응답' ? '<span class="nz-chip gold">' + esc(t.src) + '</span>' : '') +
      (t.review === 'block' ? '<span class="nz-chip">검토 필요</span>' : '') + (t.review === 'pending' ? '<span class="nz-chip blue">검수 대기</span>' : '') + '<span>' + esc(t.author) + ' · ' + esc(t.org) + '</span><span>공감 ' + F.n(t.likes) + '</span>' + (t.copied ? '<span class="nz-chip green">' + I.check + '따라 씀</span>' : '') + '</div></button>').join('') +
      (S.items.length < S.total ? '<button type="button" class="nz-btn sec nz-more" data-more>더 보기 (' + F.n(S.total - S.items.length) + '건)</button>' : '') + (!S.items.length ? '<div class="nz-lock">찾는 화법이 없어요</div>' : ''));
    drawDetail();
  }
  function drawDetail() {
    const d = root.querySelector('.nz-tl-detail'), t = S.sel; if (!d) return;
    if (!t) { NZ.html(d, '<p class="nz-note">왼쪽 목록에서 화법을 고르세요.</p>'); return; }
    NZ.html(d, '<div class="nz-talk-h"><span class="nz-chip">' + esc(t.catName) + '</span><span class="nz-chip">' + esc(t.sit) + '</span>' + (t.quality ? '<span class="nz-chip">품질 ' + esc(t.quality) + '</span>' : '') + '</div>' +
      (t.title ? '<div class="nz-kicker">' + esc(t.title) + '</div>' : '') + '<div class="nz-talk-q">' + esc(t.head) + '</div><div class="nz-talk-by"><b>' + esc(t.author) + ' FP</b>· ' + esc(t.org) + '</div>' +
      '<p class="nz-talk-more" tabindex="0">' + esc(t.body) + '</p><div class="nz-talk-why">' + (t.why ? '<div><b>포인트</b><span>' + esc(t.why) + '</span></div>' : '') + (t.tip ? '<div><b>팁</b><span>' + esc(t.tip) + '</span></div>' : '') + '</div>' +
      (t.review === 'block' ? '<p class="nz-note">검토 필요 사유 : ' + esc(t.blockReason || '') + '</p>' : '') +
      '<div class="nz-cf split"><button type="button" class="nz-btn sec" data-copy="' + t.id + '"' + (t.review === 'block' ? ' disabled' : '') + '>따라 쓰기</button><button type="button" class="nz-btn dark" data-ask="' + t.id + '">' + I.wand + 'MeAI로 다듬기</button></div>');
  }
  function drawBanner(mb) {
    const s = NZ.home.settings, cats = S.cats || {}, on = s.tickerCats;
    NZ.html(mb, '<div class="nz-form"><p class="nz-sub">막대의 「오늘의 화법」에 어떤 화법을 띄울지 고르세요. 목록에서는 설정과 상관없이 798건 전부 볼 수 있어요.</p>' +
      '<label>보여 줄 카테고리</label><div class="nz-checks">' + Object.keys(cats).map((k) => '<label><input type="checkbox" data-bcat="' + k + '"' + (!on || on.indexOf(k) >= 0 ? ' checked' : '') + '>' + esc(cats[k].name) + '<small>' + cats[k].banner + '</small></label>').join('') + '</div>' +
      '<label>바뀌는 속도</label><div class="nz-seg" role="group">' + [[5, '5초'], [8, '8초'], [12, '12초'], [0, '끄기']].map((o) => '<button type="button" data-bspeed="' + o[0] + '" aria-pressed="' + (s.tickerSec === o[0]) + '">' + o[1] + '</button>').join('') + '</div>' +
      '<label>순서</label><div class="nz-seg" role="group">' + [['mix', '카테고리 골고루'], ['rec', '추천 먼저'], ['random', '완전 랜덤']].map((o) => '<button type="button" data-border="' + o[0] + '" aria-pressed="' + (s.tickerOrder === o[0]) + '">' + o[1] + '</button>').join('') + '</div>' +
      '<div class="nz-checks"><label><input type="checkbox" data-bopt="showBlocked"' + (s.showBlocked ? ' checked' : '') + '>검토 필요 화법도 띄우기<small>71</small></label><label><input type="checkbox" data-bopt="showShort"' + (s.showShort ? ' checked' : '') + '>짧은 응답도 띄우기<small>40</small></label></div>' +
      '<div><button type="button" class="nz-btn pri" data-bsave>설정 저장</button></div><p class="nz-note">기본값 : 검토 필요 71건 · 짧은 응답 40건을 뺀 698건이 돌아가요. 이 설정은 나에게만 적용돼요.</p></div>');
  }
  function drawSubmit(mb) {
    const cats = S.cats || {};
    NZ.html(mb, '<div class="nz-form"><p class="nz-sub">현장에서 통한 내 화법을 올려 주세요. 준법 검수를 거쳐 화법 마트에 들어가고, 채택되면 홈에 이름과 함께 올라가요.</p>' +
      '<label>카테고리<select class="nz-sel" data-f="cat">' + Object.keys(cats).map((k) => '<option value="' + k + '">' + esc(cats[k].name) + '</option>').join('') + '</select></label>' +
      '<label>상황<select class="nz-sel" data-f="sit">' + SITS.map((s) => '<option>' + s + '</option>').join('') + '</select></label>' +
      '<label>핵심 한 문장 (배너 · 따라 쓰기에 쓰여요, 80자 안쪽)<input data-f="head" maxlength="80" placeholder="예) 새로 드는 게 아니라, 지금 보험이 잘 일하는지 보는 거예요."></label>' +
      '<label>전체 화법 (450자 안쪽)<textarea data-f="body" maxlength="450" placeholder="고객에게 실제로 하는 말 그대로 적어 주세요."></textarea></label>' +
      '<p class="nz-note">고객 이름 · 연락처 · 병명 같은 개인정보, 단정 · 과장 · 확정 금액 · 타사 비교 · 절판 압박 표현은 빼 주세요. 검수에서 다듬어질 수 있어요.</p>' +
      '<div><button type="button" class="nz-btn pri" data-submit>' + I.send + '검수 보내기</button></div></div>');
  }

  function onInput(e) {
    const t = e.target, k = t.dataset.in;
    if (!k) return;
    if (k === 'q') { clearTimeout(qT); qT = setTimeout(() => { S.q = t.value.trim(); S.sel = null; NZ.log('talk_library', 'search'); load(true); }, 260); }
    else { S[k] = t.value; S.sel = null; load(true); }
  }
  function onClick(e) {
    const t = e.target.closest('button'); if (!t) return;
    if (t.hasAttribute('data-x')) return ov.close();
    if (t.dataset.tab) { S.tab = t.dataset.tab; draw(); if (S.tab === 'list' && !S.items.length) load(true); return; }
    if (t.dataset.cat != null) { S.cat = t.dataset.cat; S.only = ''; S.sel = null; load(true); return; }
    if (t.dataset.only) { S.only = S.only === t.dataset.only ? '' : t.dataset.only; S.cat = ''; S.sel = null; load(true); return; }
    if (t.dataset.pick) {
      const id = t.dataset.pick, hit = S.items.filter((x) => x.id === id)[0];
      if (hit) { S.sel = hit; drawList(); } else NZ.api.getTalk(id).then((x) => { S.sel = x; drawList(); });
      if (NZ.isMobile()) setTimeout(() => { const d = root.querySelector('.nz-tl-detail'); if (d) d.classList.add('on'); }, 30);
      return;
    }
    if (t.hasAttribute('data-more')) { S.page++; load(false); return; }
    if (t.dataset.copy) { const x = S.sel; ov.close(); NZ.log('talk_library', 'copy_start', { id: x.id }); setTimeout(() => NZ.showTalk(x), 300); return; }
    if (t.dataset.ask) { const x = S.sel; ov.close(); NZ.host && NZ.host.ask('아래 화법을 내 고객 상황에 맞게 부드럽게 다듬어 줘. 단정 · 과장 표현은 빼 줘.\n\n「' + x.head + '」', 'general'); return; }
    if (t.dataset.bspeed != null || t.dataset.border) { NZ.$$(t.dataset.bspeed != null ? '[data-bspeed]' : '[data-border]', root).forEach((b) => b.setAttribute('aria-pressed', String(b === t))); return; }
    if (t.hasAttribute('data-bsave')) {
      const cats = NZ.$$('[data-bcat]', root).filter((c) => c.checked).map((c) => c.dataset.bcat);
      const sp = root.querySelector('[data-bspeed][aria-pressed="true"]'), od = root.querySelector('[data-border][aria-pressed="true"]');
      const p = { tickerCats: cats.length === 14 ? null : cats, tickerSec: sp ? +sp.dataset.bspeed : 8, tickerOrder: od ? od.dataset.border : 'mix',
        showBlocked: root.querySelector('[data-bopt="showBlocked"]').checked, showShort: root.querySelector('[data-bopt="showShort"]').checked };
      if (!cats.length) { NZ.toast('카테고리를 하나 이상 골라 주세요'); return; }
      NZ.log('talk_library', 'banner_save');
      NZ.run(NZ.api.saveSettings(p), { quiet: true }).then(() => { NZ.ui.startTicker(); NZ.toast('배너 설정을 저장했어요'); });
      return;
    }
    if (t.hasAttribute('data-submit')) {
      const f = (k) => root.querySelector('[data-f="' + k + '"]').value.trim();
      if (f('head').length < 8) { NZ.toast('핵심 한 문장을 8자 이상 적어 주세요'); return; }
      NZ.log('talk_library', 'submit');
      NZ.api.submitTalk({ cat: f('cat'), sit: f('sit'), head: f('head'), body: f('body') }).then((r) => { NZ.toast(r.message, { icon: 'send' }); S.tab = 'list'; S.only = 'mine'; draw(); load(true); });
    }
  }
})(window);
