/* MeAI 홈 넛지 v5 · 펼침 카드 (오늘의 루틴 · 출석 · 퀴즈 · 화법 · 로또 · 리그 · 첫 7일 여정 · 지갑 · 더보기)
 * 카드 = { title, wide, render(home) → HTML, mount(box, home), update(box, home), act(name, el) }
 * 카드는 서버 요약(home)만 보고 그린다. 행동은 NZ.run(NZ.api.○○()) 으로 보내고 결과(새 home)로 다시 그린다.
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ, I = NZ.I, esc = NZ.esc, F = NZ.fmt;
  const C = NZ.cards = {};
  const head = (icon, title, meta, icCls) => '<div class="nz-ch"><span class="nz-ic' + (icCls ? ' ' + icCls : '') + '">' + icon + '</span><h3>' + title + '</h3>' + (meta ? '<span class="meta">' + meta + '</span>' : '') + '</div>';
  const GO = { 'chat.custom': 'reco', 'reco.open': 'reco', 'talk.copy': 'talk', 'quiz.answer': 'quiz', attend: 'attend' };
  const sw = (key, on, label) => '<button type="button" class="nz-sw" role="switch" aria-checked="' + !!on + '" aria-label="' + esc(label) + '" data-act="set" data-key="' + key + '" data-val="' + (!on) + '"></button>';
  const seg = (key, val, opts) => '<div class="nz-seg" role="group">' + opts.map((o) => '<button type="button" aria-pressed="' + (String(val) === String(o[0])) + '" data-act="set" data-key="' + key + '" data-val="' + o[0] + '">' + o[1] + '</button>').join('') + '</div>';
  const flameBig = '<svg viewBox="0 0 64 72" aria-hidden="true"><path class="f1" d="M33.5 2c1.6 10.2-3.6 16-8.6 21.6C19.6 29.6 13 36 13 47.4 13 60 22 70 32 70s19-9.5 19-21.6c0-6.6-2.4-11-5.4-15-.6 4.4-2.8 7.6-6.4 9.4 1-12.8-3-25.8-5.7-40.8z"/><path class="f2" d="M32.5 30.5c-3.6 4.6-9 8.8-9 17.4 0 6.4 4 12.2 9.3 12.2s9.2-5.4 9.2-11.6c0-4.2-1.6-7-3.6-9.6-.6 2.6-2 4.4-4.2 5.4.6-5-.4-9.6-1.7-13.8z"/><path class="f3" d="M32.4 45c-2 2.4-3.6 4-3.6 7 0 2.4 1.6 4.2 3.7 4.2s3.6-1.8 3.6-4.3c0-2.6-1.4-4.4-3.7-6.9z"/></svg>';

  // ═════ ① 오늘의 루틴 ═════
  C.quest = {
    title: '오늘의 루틴',
    render(h) {
      const q = h.quests, R = h.quests.rings;
      const leg = ['come', 'learn', 'sell'].map((k) => '<div data-v="c:' + R[k].color + '"><i></i>' + R[k].label + '<span>' + R[k].done + ' / ' + R[k].total + '</span></div>').join('');
      const list = q.items.map((it) => '<li class="' + (it.done ? 'done' : '') + '" data-v="c:' + R[it.ring].color + '"><span class="dot">' + (it.done ? I.check : '') + '</span>' +
        '<span class="t">' + esc(it.title) + '<small>' + esc(R[it.ring].label + (it.note ? ' · ' + it.note : '')) + '</small></span>' +
        (it.done ? '<span class="pg">완료</span>' : '<span class="pg">' + it.progress + '/' + it.target + '</span><button type="button" class="nz-btn sm sec" data-go="' + esc(it.go) + '">하러 가기</button>') + '</li>').join('');
      return head(I.ring, '오늘의 루틴', F.md(h.today) + ' · 매일 새로') +
        '<div class="nz-cb"><div class="nz-routine"><div class="big">' + NZ.ui.ringSvg(q, 112) + '<div class="c"><b>' + q.done + '/' + q.total + '</b></div></div><div class="nz-legend">' + leg + '</div></div>' +
        '<div class="nz-steps"><div class="' + (q.mission ? 'done' : '') + '"><b>' + q.need + '개 · 일일 미션</b>커피 응모권 +1' + (q.mission ? ' · 받음' : '') + '</div><div class="' + (q.allclear ? 'done' : '') + '"><b>' + q.total + '개 · 올클리어</b>응모권 +2 더' + (q.allclear ? ' · 받음' : '') + '</div></div>' +
        '<ul class="nz-qlist">' + list + '</ul></div>' +
        '<div class="nz-cf"><p class="nz-note">퀘스트는 본사가 그 주에 밀고 싶은 영업 행동으로 바꿔 걸 수 있어요.' + (q.next ? ' <b>' + F.md(q.next.date) + (q.next.changed ? ' 교체 미션' : '') + '</b> : ' + q.next.titles.map(esc).join(' · ') : '') + '</p></div>';
    }
  };

  // ═════ ② 출석 · 연속 기록 ═════
  C.attend = {
    title: '출석 · 연속 기록',
    render(h) {
      const s = h.streak, w = h.week, done = h.attendedToday;
      const dows = ['월', '화', '수', '목', '금'];
      const stamps = w.days.map((d, i) => '<div class="d" data-day="' + d.day + '"><span class="s ' + (d.state === 'stamp' ? '' : d.state) + '">' + (d.state === 'stamp' ? '<span class="nz-seal">출석<br>' + (+d.day.slice(5, 7)) + '.' + (+d.day.slice(8, 10)) + '</span>' : '') + '</span>' + dows[i] + '</div>').join('');
      const msg = !h.bizDay ? '오늘은 쉬는 날이에요. 연속 기록은 그대로 이어져요.'
        : !s.current && !done ? '첫 도장을 찍으면 연속 기록이 시작돼요. 출석 · 추천 고객 · 대화 중 하나면 그날 불이 켜져요.'
        : done ? '벌써 <b>' + s.current + '영업일째</b> 고객을 찾아가고 있어요.'
        : s.todayLit ? '추천 고객 · 대화로 오늘 불이 켜졌어요. 도장까지 찍으면 응모권 +1.'
        : s.atRisk ? '아직 오늘 불이 꺼져 있어요. 도장 한 번이면 <b>' + s.nextStreak + '영업일째</b>로 이어져요.'
        : '오늘 도장 찍고 <b>' + s.nextStreak + '영업일째</b> 이어가세요.';
      const nb = s.nextBadge, toNext = nb ? nb.n - s.current : 0;
      const minis = s.last10.map((x) => '<i class="' + x.state + '" title="' + esc(F.md(x.day)) + '"></i>').join('');
      return head(I.flame, '출석 · 연속 기록', esc(w.label), '') +
        '<div class="nz-cb"><div class="nz-streak"><div class="nz-flame' + (s.todayLit ? ' lit' : ' off') + '">' + flameBig + '</div><div><div class="n">' + s.current + '<small>영업일 연속</small></div><p>' + msg + '</p></div></div>' +
        '<div class="nz-stamps">' + stamps + '</div>' +
        '<div class="nz-rowinfo">' + I.ticket.replace('<svg', '<svg class="gold"') + '<span>이번 주 영업일을 모두 출석하면 <b>응모권 +3</b></span><span class="r"><b>' + w.attended + '</b> / ' + w.bizDays + (w.perfect ? ' · 받음' : '') + '</span></div>' +
        (nb ? '<div class="nz-rowinfo">' + I.medal + '<span>다음 배지 <b>「' + esc(nb.label) + '」</b> ' + nb.n + '영업일까지 ' + toNext + '일</span><span class="r"><span class="nz-bar"><i data-v="p:' + (s.current / nb.n).toFixed(3) + '"></i></span></span></div>' : '') +
        '<div class="nz-rowinfo">' + I.shield + '<span>보호권 <b>' + s.shields + '장</b> · 휴가 · 교육으로 빈 영업일을 자동으로 메워요</span></div>' +
        '<div class="nz-kicker">최근 10영업일<span class="r">최고 ' + s.best + '일 · 전사 상위 ' + s.topPercent + '% <span class="nz-ex">예시</span></span></div><div class="nz-minis">' + minis + '</div>' +
        '<p class="nz-note">출석 도장이 아니어도 추천 고객을 열거나 대화를 하면 그날 불이 켜져요. 주말 · 공휴일은 쉬어도 이어져요.</p></div>' +
        '<div class="nz-cf">' + (done ? '<button type="button" class="nz-btn sec wide" disabled>' + I.check + '오늘 출석 완료</button><button type="button" class="nz-btn ghost" data-act="dash">내 기록 전체</button>'
          : h.bizDay ? '<button type="button" class="nz-btn pri wide" data-act="attend" data-autofocus>출석 도장 찍기 <span class="plus">' + I.ticket + ' +1</span></button>' : '<button type="button" class="nz-btn sec wide" disabled>오늘은 쉬는 날이에요</button>') + '</div>';
    }
  };
  NZ.acts.attend = () => { NZ.log('attend', 'stamp'); return NZ.run(NZ.api.attend()); };
  NZ.acts.dash = () => { NZ.ui.close(true); NZ.dash && NZ.dash.open(); };

  // ═════ ③ 오늘의 퀴즈 ═════
  const markO = (c) => '<svg class="mk" viewBox="0 0 100 100" aria-hidden="true"><circle class="draw" cx="50" cy="50" r="36" fill="none" stroke="' + c + '" stroke-width="12" stroke-linecap="round" transform="rotate(-90 50 50)"/></svg>';
  const markX = (c) => '<svg class="mk" viewBox="0 0 100 100" aria-hidden="true"><path class="draw" d="M22 22l56 56" fill="none" stroke="' + c + '" stroke-width="12" stroke-linecap="round"/><path class="draw" d="M78 22L22 78" fill="none" stroke="' + c + '" stroke-width="12" stroke-linecap="round"/></svg>';
  const bigO = '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="16" fill="none" stroke="currentColor" stroke-width="6"/></svg>';
  const bigX = '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M11 11l26 26M37 11L11 37" stroke="currentColor" stroke-width="6" stroke-linecap="round"/></svg>';
  C.quiz = {
    title: '오늘의 퀴즈',
    render(h) {
      const q = h.quiz;
      let body = '', foot = '';
      if (!q.open) {
        body = '<div class="nz-lock">' + I.lock.replace('<svg', '<svg class="lk"') + '오늘의 퀴즈는<b>9시</b>에 열려요<br>' + F.left(q.openAt - h.serverTime) + ' 남았어요</div>';
      } else if (!q.answered) {
        body = '<p class="nz-q">' + esc(q.question) + '</p>' + (q.type === 'ox'
          ? '<div class="nz-ox"><button type="button" class="o" data-act="quiz-ans" data-v="O" aria-label="O, 맞다" data-autofocus>' + bigO + '</button><button type="button" class="x" data-act="quiz-ans" data-v="X" aria-label="X, 아니다">' + bigX + '</button></div>'
          : '<div class="nz-opts">' + q.options.map((o, i) => '<button type="button" data-act="quiz-ans" data-v="' + i + '"><i>' + (i + 1) + '</i>' + esc(o) + '</button>').join('') + '</div>') +
          '<p class="nz-note">맞히면 <b>커피 응모권 +1</b> · 틀려도 해설을 읽으면 퀘스트 인정' + (q.combo ? ' · 지금 연속 정답 <b>' + q.combo + '</b>' : '') + '</p>';
      } else {
        const ok = q.correct, ans = q.type === 'ox' ? q.answer : (+q.answer + 1) + '번';
        body = '<div class="nz-qres ' + (ok ? 'ok' : 'no') + '">' + (q.type === 'ox' ? (q.answer === 'O' ? markO(ok ? '#0e9b67' : '#9fa4ad') : markX(ok ? '#0e9b67' : '#9fa4ad')) : markO(ok ? '#0e9b67' : '#9fa4ad')) +
          '<div><h4>' + (ok ? '정답이에요 · 답은 ' + ans : '아쉬워요 · 답은 ' + ans) + '</h4><p>' + (ok ? '커피 응모권 +1 · 연속 정답 ' + q.combo : q.explained ? '해설을 읽어 퀘스트로 인정됐어요' : '아래 해설을 읽으면 퀘스트로 인정돼요') + '</p></div></div>' +
          '<p class="nz-sub">' + esc(q.question) + '</p>' +
          (q.type === 'choice' ? '<div class="nz-opts">' + q.options.map((o, i) => '<button type="button" disabled class="' + (String(i) === String(q.answer) ? 'ans' : '') + (String(i) === String(q.choice) ? ' mine' + (q.correct ? '' : ' wrong') : '') + '"><i>' + (i + 1) + '</i>' + esc(o) + '</button>').join('') + '</div>' : '') +
          '<div class="nz-kicker">세 줄 해설</div><ul class="nz-exp">' + q.explain.map((x) => '<li>' + esc(x) + '</li>').join('') + '</ul><p class="nz-src">출처 · ' + esc(q.source) + '</p>' +
          (q.stats ? '<div class="nz-stat2"><div><small>우리 지점 정답률</small><b>' + q.stats.branchRate + '%</b><div class="nz-bar green"><i data-v="p:' + q.stats.branchRate / 100 + '"></i></div></div><div><small>전사 정답률 · ' + F.n(q.stats.participants) + '명 참여</small><b>' + q.stats.companyRate + '%</b><div class="nz-bar ink"><i data-v="p:' + q.stats.companyRate / 100 + '"></i></div></div></div><p class="nz-note">지점별 참여율 · 정답률로 신상품 · 이슈가 어디까지 닿았는지 봐요 <span class="nz-ex">예시 숫자</span></p>' : '');
        foot = '<div class="nz-cf">' + (!ok && !q.explained ? '<button type="button" class="nz-btn pri wide" data-act="quiz-explain" data-autofocus>해설 다 읽었어요 · 퀘스트 인정</button>' : '') +
          '<button type="button" class="nz-btn ' + (!ok && !q.explained ? 'sec' : 'dark wide') + '" data-act="ask" data-q="' + esc(q.ask || '') + '">' + I.send + 'MeAI에게 더 묻기</button></div>';
      }
      return head(I.quiz, '오늘의 퀴즈', esc(q.category) + ' · 매일 9시', '') + '<div class="nz-cb">' + body + '</div>' + foot;
    }
  };
  NZ.acts['quiz-ans'] = (t) => { const q = NZ.home.quiz; NZ.log('quiz', 'answer', { id: q.id }); return NZ.run(NZ.api.answerQuiz(q.id, t.dataset.v), { from: t }); };
  NZ.acts['quiz-explain'] = () => { const q = NZ.home.quiz; NZ.log('quiz', 'explained', { id: q.id }); return NZ.run(NZ.api.explainQuiz(q.id)); };
  NZ.acts.ask = (t) => { const q = t.dataset.q || ''; NZ.log('ask_meai', 'click', { from: NZ.ui.current() }); NZ.ui.close(true); NZ.host && NZ.host.ask(q, 'general'); };

  // ═════ ④ 오늘의 화법 (따라 쓰기) ═════
  const cache = {};
  NZ.talkCache = cache;
  const SIG = /[0-9a-zㄱ-ㆎ가-힣一-鿿]/;
  let cur = null, composing = false;
  function talkNow(h) { return cur || (h.talk.today); }
  function tgtSpans(text, typed) {
    const T = text.split(''), Y = (typed || '').toLowerCase().split('').filter((c) => SIG.test(c));
    let k = 0, last = '';
    return T.map((ch) => {
      if (!SIG.test(ch.toLowerCase())) return '<span class="' + last + '">' + esc(ch) + '</span>';
      const y = Y[k], cls = y == null ? (k === Y.length ? 'cur' : '') : y === ch.toLowerCase() ? 'ok' : (composing && k === Y.length - 1 ? '' : 'ng');
      k++; last = cls === 'cur' ? '' : cls;
      return '<span class="' + cls + '">' + esc(ch) + '</span>';
    }).join('');
  }
  function score(text, typed) {
    const T = text.toLowerCase().split('').filter((c) => SIG.test(c)), Y = (typed || '').toLowerCase().split('').filter((c) => SIG.test(c));
    let ok = 0; for (let i = 0; i < Math.min(T.length, Y.length); i++) if (T[i] === Y[i]) ok++;
    return { ok: ok, total: T.length, typed: Y.length, done: Y.length >= T.length && ok / T.length >= 0.95 };
  }
  C.talk = {
    title: '오늘의 화법',
    wide: true,
    render(h) {
      const t = talkNow(h), copied = t.copied;
      const chips = '<span class="nz-chip">' + esc(t.catName) + '</span><span class="nz-chip">' + esc(t.sit) + '</span>' + (t.grade === 'rec' ? '<span class="nz-chip red">추천</span>' : '') +
        (t.src && t.src !== 'FP 응답' ? '<span class="nz-chip gold">' + esc(t.src) + '</span>' : '') + (t.review === 'block' ? '<span class="nz-chip">검토 필요</span>' : '') + (t.tags || []).slice(0, 2).map((x) => '<span class="nz-chip blue">' + esc(x) + '</span>').join('');
      return head(I.quote, '오늘의 화법', '9월 필살 화법 공모 ' + F.n(h.talk.total) + '건', '') +
        '<div class="nz-cb"><div class="nz-talk-h">' + chips + '</div>' + (t.title ? '<div class="nz-kicker">' + esc(t.title) + '</div>' : '') +
        '<div class="nz-talk-q">' + esc(t.head) + '</div>' +
        '<div class="nz-talk-by"><b>' + esc(t.author) + ' FP</b>· ' + esc(t.org) + ' · 9월 필살 화법 공모</div>' +
        '<button type="button" class="nz-btn ghost" data-act="talk-more" aria-expanded="false">' + I.chev + '전체 화법 · 포인트 · 팁 보기</button>' +
        '<div class="nz-more-box" hidden><p class="nz-talk-more" tabindex="0">' + esc(t.body) + '</p><div class="nz-talk-why">' + (t.why ? '<div><b>포인트</b><span>' + esc(t.why) + '</span></div>' : '') + (t.tip ? '<div><b>팁</b><span>' + esc(t.tip) + '</span></div>' : '') + '</div></div>' +
        '<div class="nz-react"><button type="button" data-act="talk-react" data-t="like" aria-pressed="' + !!t.liked + '">' + (t.liked ? I.heartF : I.heart) + '공감 ' + F.n(t.likes) + '</button>' +
        '<button type="button" data-act="talk-react" data-t="save" aria-pressed="' + !!t.saved + '">' + I.bookmark + (t.saved ? '저장함' : '저장') + '</button>' +
        '<button type="button" class="used" data-act="talk-react" data-t="used" aria-pressed="' + !!t.usedByMe + '">' + I.hand + '고객에게 써봤어요 ' + F.n(t.usedCount) + '</button></div>' +
        (t.review === 'block' ? '<p class="nz-note">준법 검토가 필요한 화법이라 따라 쓰기 · 배너에서 빠져 있어요. 사유 : ' + esc(t.blockReason || '') + '</p>' :
          '<div class="nz-copy' + (copied ? ' done' : '') + '"><div class="nz-kicker">' + (copied ? I.check + ' 따라 쓰기 완료' : '따라 쓰기') + '<span class="r">띄어쓰기 · 문장부호는 틀려도 괜찮아요</span></div>' +
          '<div class="tgt" aria-hidden="true">' + tgtSpans(t.head, '') + '</div>' +
          '<label class="nz-sr" for="nz-copy-in">위 문장을 그대로 따라 써 보세요</label><textarea id="nz-copy-in" rows="2" placeholder="위 문장을 그대로 따라 써 보세요" spellcheck="false" autocomplete="off"></textarea>' +
          '<div class="meter"><span class="nz-bar green"><i data-v="p:0"></i></span><span class="pc">0%</span><span>' + (h.talk.copiedToday ? '오늘 응모권은 받았어요 · 연습은 얼마든지' : '완성하면 <b>응모권 +1</b> (하루 1번)') + '</span></div></div>') +
        '<p class="nz-note">AI 정리 · 준법 검토 초안 · 오픈 전 준법 담당 부서 최종 확인 필요 · 공감 · 써봤어요 숫자는 예시</p></div>' +
        '<div class="nz-cf split"><div><button type="button" class="nz-btn ghost" data-act="talk-next">' + I.refresh + '다른 화법</button><button type="button" class="nz-btn ghost" data-act="talk-all">전체 ' + F.n(h.talk.total) + '</button></div>' +
        '<button type="button" class="nz-btn dark" data-act="ask-talk">' + I.wand + 'MeAI로 다듬기</button></div>';
    },
    mount(box, h) {
      const t = talkNow(h), ta = box.querySelector('textarea'); if (!ta) return;
      const wrap = box.querySelector('.nz-copy'), tgt = wrap.querySelector('.tgt'), bar = wrap.querySelector('.nz-bar i'), pc = wrap.querySelector('.pc');
      let sent = false;
      const upd = () => {
        const sc = score(t.head, ta.value);
        wrap.setAttribute('data-busy', ta.value ? '1' : '0');
        tgt.innerHTML = tgtSpans(t.head, ta.value);
        const p = sc.total ? Math.min(1, sc.ok / sc.total) : 0;
        bar.style.setProperty('--p', p.toFixed(3)); pc.textContent = Math.round(p * 100) + '%';
        if (sc.done && !sent && !composing) {
          sent = true; ta.readOnly = true; wrap.classList.add('done'); NZ.log('talk', 'copy_done', { id: t.id });
          NZ.run(NZ.api.copyTalk(t.id, ta.value), { from: wrap }).then(() => { wrap.setAttribute('data-busy', '0'); cur = Object.assign({}, t, { copied: true }); cache[t.id] = cur; NZ.ui.refreshPop(true); });
        }
      };
      ta.addEventListener('compositionstart', () => { composing = true; });
      ta.addEventListener('compositionend', () => { composing = false; upd(); });
      ta.addEventListener('input', upd);
      ta.addEventListener('paste', (e) => { e.preventDefault(); NZ.toast('붙여 넣기 대신 한 글자씩 따라 써 보세요'); });
    },
    update(box, h) { /* 따라 쓰는 중에는 카드를 다시 그리지 않는다 */ },
    opened(box, h) {
      const tk = NZ.ui.tickTalk();
      if (!cur && tk && tk.id !== h.talk.today.id) loadTalk(tk.id);
    },
    closed() { composing = false; },
    act(name, t) {
      const h = NZ.home, tk = talkNow(h);
      if (name === 'talk-more') { const b = t.parentElement.querySelector('.nz-more-box'); b.hidden = !b.hidden; t.setAttribute('aria-expanded', String(!b.hidden)); return; }
      if (name === 'talk-next') { const nx = NZ.ui.nextTalk(); NZ.log('talk', 'next'); if (nx) loadTalk(nx.id); return; }
      if (name === 'talk-all') { NZ.ui.close(true); NZ.talks && NZ.talks.open(); return; }
      if (name === 'ask-talk') { NZ.log('talk', 'ask_meai', { id: tk.id }); NZ.ui.close(true); NZ.host && NZ.host.ask('아래 화법을 내 고객 상황에 맞게 부드럽게 다듬어 줘. 단정 · 과장 표현은 빼 줘.\n\n「' + tk.head + '」', 'general'); return; }
      if (name === 'talk-react') {
        const type = t.dataset.t, on = t.getAttribute('aria-pressed') !== 'true';
        NZ.log('talk', 'react_' + type, { id: tk.id, on: on });
        NZ.api.reactTalk(tk.id, type, on).then((r) => { cur = r.talk; cache[r.talk.id] = r.talk; if (r.home) NZ.setHome(r.home); else NZ.ui.refreshPop(true); });
      }
    }
  };
  function loadTalk(id) {
    if (cache[id]) { cur = cache[id]; NZ.ui.refreshPop(true); return; }
    NZ.api.getTalk(id).then((t) => { cache[id] = t; cur = t; if (NZ.ui.current() === 'talk') NZ.ui.refreshPop(true); });
  }
  NZ.showTalk = (t) => { cur = t; cache[t.id] = t; NZ.ui.go('talk'); };
  NZ.acts['ask-talk'] = (t) => C.talk.act('ask-talk', t);

  // ═════ ⑤ 로또(행운번호) ═════
  C.lotto = {
    title: '로또',
    render(h) {
      const L = h.lotto, drawn = L.phase === 'drawn', now = h.serverTime;
      const cdT = L.phase === 'collect' ? L.cutoffAt : L.drawAt;
      const rows = L.sets.length ? L.sets.map((s) => '<div class="row' + (s.prize ? ' win' : '') + '"><span class="no">' + s.no + '번</span>' + s.nums.map((n) => NZ.ball(n, 'sm' + (drawn ? (L.draw.indexOf(n) >= 0 ? ' hit' : ' dim') : ''))).join('') +
        (drawn ? '<span class="res">' + s.match + '개' + (s.prize ? ' · ' + esc(s.prize) : '') + '</span>' : '<span class="who">' + esc(s.customer) + '</span>') + '</div>').join('')
        : '<div class="empty">이번 주 세트가 아직 없어요. 추천 고객을 열어 첫 세트를 받아 보세요.</div>';
      const odds = L.odds;
      const tiers = '<table class="nz-tiers"><thead><tr><th>일치</th><th>1세트 확률</th><th>선물 (예시)</th></tr></thead><tbody>' + L.tiers.map((t) => '<tr><td>' + t.match + '개' + (t.match >= 5 ? ' 이상' : '') + '</td><td>' + F.pct(t.match === 3 ? odds.p3 - odds.p4 : t.match === 4 ? odds.p4 - odds.p5 : odds.p5, t.match >= 5 ? 3 : 2) + '</td><td>' + esc(t.prize) + '</td></tr>').join('') + '</tbody></table>';
      return head(I.lotto, esc(L.name), esc(L.label) + ' 회차', '') +
        '<div class="nz-cb"><div class="nz-lhead"><div><div class="k">이번 주 내 세트</div><b>' + L.sets.length + '세트</b>' + (L.nextRoundSets ? '<div class="k">다음 회차 ' + L.nextRoundSets + '세트</div>' : '') + '</div>' +
        '<div class="cd"><div class="k">' + (drawn ? '추첨 완료 · 금 17:00' : L.phase === 'closed' ? '응모 마감 · 17시 추첨까지' : '응모 마감(금 16:00)까지') + '</div><b>' + (drawn ? '결과 발표' : F.left(cdT - now)) + '</b></div></div>' +
        (drawn ? '<div class="nz-kicker">이번 주 당첨번호</div><div class="nz-balls on">' + L.draw.map((n) => NZ.ball(n)).join('') + '</div>' : '') +
        '<div class="nz-kicker">내 번호<span class="r">오늘 ' + L.todayIssued + ' / ' + L.dailyMax + '세트</span></div><div class="nz-sets">' + rows + '</div>' +
        '<p class="nz-note">받는 법 : ' + (L.issueOn === 'reco.open' ? '오늘의 추천 고객을 열면' : '오늘의 추천 고객과 맞춤대화를 하면') + ' 1세트 · 하루 ' + L.dailyMax + '세트 · 같은 고객은 하루 1번. 월~금 모으고 <b>금요일 17시</b> 발표</p>' +
        '<div class="nz-odds"><div class="hot"><small>지금 ' + L.sets.length + '세트면</small><b>' + F.pct(odds.mine) + '</b><small>3개 이상 맞을 확률</small></div><div><small>주 10세트를 모으면</small><b>' + F.pct(odds.ten) + '</b><small>약 ' + Math.round(1 / odds.ten) + '주에 1번 · 번호 35개면 ' + F.pct(odds.ten35) + '</small></div></div>' +
        tiers +
        '<div class="nz-kicker">지난주 (' + esc(L.last.label) + ')<span class="r">내 ' + L.last.sets + '세트 · 최고 ' + L.last.best + '개 일치' + (L.last.prize ? ' · ' + esc(L.last.prize) : '') + '</span></div><div class="nz-balls on">' + L.last.nums.map((n) => NZ.ball(n, 'sm')).join('') + '</div>' +
        '<div class="nz-fair">' + I.shield + '<span>공정한 추첨 : 회차를 열 때 추첨 씨앗의 지문(SHA-256) <code>' + esc(L.commit.slice(0, 20)) + '…</code> 을 먼저 공개하고, 추첨 뒤 씨앗을 공개해요. 누구나 같은 번호가 나오는지 다시 계산해 볼 수 있어요.</span></div>' +
        '<p class="nz-note">확률은 조합 계산값 · 선물 종류 · 인원은 확정 전 예시 · 명칭은 준법 검토 뒤 확정(대체 이름 「MeAI 행운번호」)</p></div>' +
        '<div class="nz-cf">' + (drawn ? '<button type="button" class="nz-btn pri wide" data-act="lotto-draw" data-autofocus>' + I.play + '당첨번호 발표 보기</button>' : '<button type="button" class="nz-btn pri wide" data-go="reco">추천 고객 보러 가기</button>') + '</div>';
    }
  };
  NZ.acts['lotto-draw'] = (t, e, sample) => {
    const L = NZ.home.lotto;
    if (!sample && L.phase !== 'drawn') { NZ.toast('추첨은 금요일 17시예요. ' + F.left(L.drawAt - NZ.home.serverTime) + ' 남았어요'); return; }
    NZ.ui.close(true);
    NZ.log('lotto', 'draw_view');
    if (sample) return NZ.fx.draw(sample);
    NZ.fx.draw({ lotto: L, draw: L.draw, sets: L.sets, seed: L.seed });
    NZ.run(NZ.api.markDrawSeen(L.round), { quiet: true });
  };

  // ═════ ⑥ 리그 · 주간 패스 ═════
  let scope = 'branch', other = null;
  C.league = {
    title: '지점 리그 · 주간 패스',
    wide: true,
    render(h) {
      const L = h.league, hide = h.settings.hideRank;
      const segs = '<div class="nz-seg" role="group" aria-label="보기 범위">' + [['branch', '지점 리그'], ['hq', '본부 안 지점'], ['company', '전사 본부']].map((s) => '<button type="button" data-act="league-scope" data-s="' + s[0] + '" aria-pressed="' + (scope === s[0]) + '">' + s[1] + '</button>').join('') + '</div>';
      let body = '';
      const pass = L.pass, maxXp = pass[pass.length - 1].xp, p = Math.min(1, L.xp / maxXp);
      const passBox = '<div class="nz-pass"><div class="top">이번 주<b>' + F.n(L.xp) + ' XP</b><span class="r">' + (L.nextPass ? '다음 보상까지 <b>' + (L.nextPass.xp - L.xp) + ' XP</b>' : '이번 주 패스 완주') + '</span></div>' +
        '<div class="nz-track"><div class="ln"><i data-v="p:' + p.toFixed(3) + '"></i></div>' + pass.map((m) => '<span class="nd' + (m.reached ? ' on' : '') + '" data-v="x:' + (m.xp / maxXp).toFixed(3) + '">' + (m.reached ? I.check : '') + '<small>' + m.xp + '</small></span>').join('') + '</div>' +
        '<div class="nx">' + (L.nextPass ? '다음 : <b>' + esc(L.nextPass.label) + '</b> (' + L.nextPass.xp + ' XP)' : '골드 · MVP 테두리가 이번 주 리그 이름에 붙어요') + '</div></div>';
      if (scope === 'branch') {
        if (hide) body = passBox + '<p class="nz-sub">순위를 숨겼어요. 주간 패스만 보여요. 「더보기 → 넛지 설정」에서 다시 켤 수 있어요.</p>';
        else {
          const list = L.list.map((x) => '<li class="' + (x.me ? 'me' : '') + '"><span class="rk' + (x.rank <= L.goldCut ? ' g' : '') + '">' + x.rank + '</span><span class="nm">' + esc(x.name) + (x.me ? ' (나)' : '') + (x.frame ? '<span class="fr' + (x.frame === 'mvp' ? ' mvp' : '') + '">' + (x.frame === 'mvp' ? 'MVP' : '골드') + '</span>' : '') + '</span>' +
            '<span class="tr ' + (x.trend > 0 ? 'up' : x.trend < 0 ? 'dn' : 'eq') + '">' + (x.trend > 0 ? '▲' + x.trend : x.trend < 0 ? '▼' + (-x.trend) : '–') + '</span><span class="xp">' + F.n(x.xp) + '</span>' +
            (x.me ? '<span class="ch"></span>' : '<button type="button" class="ch" data-act="cheer" data-id="' + esc(x.id) + '" aria-pressed="' + x.cheered + '" aria-label="' + esc(x.name) + '님 응원하기"' + (x.cheered || L.cheersLeft <= 0 ? ' disabled' : '') + '>' + (x.cheered ? I.heartF : I.clap) + '</button>') + '</li>' + (x.rank === L.goldCut ? '<li class="cut" aria-hidden="true"></li>' : '')).join('');
          body = passBox + '<div class="nz-kicker">' + esc(L.branch) + ' 리그 · ' + L.total + '명<span class="r">3위까지 골드 배지 · 응원 ' + L.cheersLeft + '번 남음</span></div><ul class="nz-lg">' + list + '</ul>' +
            (L.hint ? '<div class="nz-hint">' + I.trophy + '<span>' + (L.rank - 1) + '위까지 <b>' + L.gap + ' XP</b> · ' + esc(L.hint.label) + ' 한 번이면 역전 (+' + L.hint.xp + ')</span><button type="button" class="nz-btn" data-go="' + (GO[L.hint.kind] || 'reco') + '">하러 가기</button></div>' : '<div class="nz-hint">' + I.star + '<span>지점 <b>1위</b> · 이번 주 리그를 이끄는 중이에요</span></div>') +
            (L.cheersReceived.length ? '<div class="nz-cheers">' + L.cheersReceived.map((c) => '<span class="nz-chip red">' + I.clap + esc(c.from) + '님이 응원했어요 · ' + esc(c.at.slice(5)) + '</span>').join('') + '</div>' : '');
        }
        const T = h.team, C2 = h.compare, mx = Math.max(C2.me, C2.branchAvg, C2.nonUser);
        body += '<div class="nz-team"><div class="t">' + I.users + '<b>' + esc(T.branch) + ' ' + esc(T.title) + '</b> · ' + esc(T.metric) + '<span class="r">' + F.n(T.value) + ' / ' + F.n(T.target) + '</span></div><div class="nz-bar gold"><i data-v="p:' + Math.min(1, T.value / T.target).toFixed(3) + '"></i></div><p class="nz-note">개인 대신 지점이 함께 채우는 목표 · ' + T.joined + '/' + T.members + '명 참여 <span class="nz-ex">예시</span></p></div>' +
          '<div class="nz-cmp"><p class="nz-bigline">MeAI를 안 쓰는 동료보다 <b>' + C2.ratio + '배</b> 더 하고 있어요</p>' +
          [['me', '나', C2.me], ['av', '지점 평균', C2.branchAvg], ['no', '미사용 동료', C2.nonUser]].map((r) => '<div class="r ' + r[0] + '"><span>' + r[1] + '</span><span class="nz-bar"><i data-v="p:' + (r[2] / mx).toFixed(3) + '"></i></span><b>' + r[2] + '</b></div>').join('') +
          '<p class="nz-note">' + esc(C2.metric) + ' · 참고용 비교이며 인과를 뜻하지 않아요 <span class="nz-ex">예시 숫자</span></p></div>';
      } else {
        body = other && other.scope === scope ? '<div class="nz-kicker">' + (scope === 'hq' ? esc(h.user.hq) + ' 안 지점 순위' : '전사 본부 순위') + '<span class="r">' + esc(other.unit) + '</span></div><ul class="nz-lg">' +
          other.list.map((x) => '<li class="' + (x.mine ? 'me' : '') + '"><span class="rk' + (x.rank <= 3 ? ' g' : '') + '">' + x.rank + '</span><span class="nm">' + esc(x.name) + (x.region ? ' <small class="nz-note">' + esc(x.region) + '</small>' : '') + '</span><span class="xp">' + x.value + '</span></li>').join('') + '</ul><p class="nz-note">개인이 아니라 조직 단위로만 보여요 <span class="nz-ex">예시 숫자</span></p>' : '<div class="nz-lock">불러오는 중…</div>';
      }
      return head(I.trophy, '지점 리그 · 주간 패스', esc(L.weekLabel) + ' · 매주 월요일 새로', '') + '<div class="nz-cb">' + segs + '<div class="nz-kicker"></div>' + body + '</div>' +
        '<div class="nz-cf split"><p class="nz-note">동료 이름은 가운데를 가리고 나만 실명으로 보여요 · 평가 지표로 쓰지 않아요</p><button type="button" class="nz-btn ghost" data-act="set" data-key="hideRank" data-val="' + (!h.settings.hideRank) + '">' + (h.settings.hideRank ? '순위 보이기' : '순위 숨기기') + '</button></div>';
    },
    act(name, t) {
      if (name === 'league-scope') {
        scope = t.dataset.s; NZ.log('league', 'scope', { s: scope });
        if (scope !== 'branch' && !(other && other.scope === scope)) NZ.api.getLeague(scope).then((r) => { other = r; NZ.ui.refreshPop(true); });
        NZ.ui.refreshPop(true);
      }
    },
    closed() { scope = 'branch'; }
  };
  NZ.acts.cheer = (t) => { NZ.log('league', 'cheer'); return NZ.run(NZ.api.cheer(t.dataset.id), { from: t }); };

  // ═════ ⑥' 첫 7일 여정 (신인) ═════
  C.journey = {
    title: '첫 7일 여정',
    render(h) {
      const ob = h.onboarding, dn = ob.steps.filter((x) => x.done).length;
      const GOS = { attend: 'attend', quiz: 'quiz', 'reco.open': 'reco', 'chat.custom': 'reco', 'talk.copy': 'talk', 'consent.request': 'consent', 'dash.open': 'dash' };
      return head(I.route, '첫 7일 여정', '입사 ' + ob.joinMonth + '개월차') +
        '<div class="nz-cb"><p class="nz-sub">처음 일곱 가지를 해 보면 MeAI 홈이 손에 익어요. 처음 할 때마다 한 번씩 축하해 드려요.</p><div class="nz-kicker">' + dn + ' / ' + ob.steps.length + ' 완료</div>' +
        '<ul class="nz-journey">' + ob.steps.map((x, i) => '<li class="' + (x.done ? 'done' : '') + '"><span class="d">' + (x.done ? I.check : i + 1) + '</span><span><b>' + esc(x.title) + '</b><small>' + esc(x.text) + '</small></span>' + (x.done ? '' : '<button type="button" class="nz-btn sm sec" data-go="' + GOS[x.kind] + '">해 보기</button>') + '</li>').join('') + '</ul></div>' +
        '<div class="nz-cf"><button type="button" class="nz-btn sec wide" data-open="quest">오늘의 루틴 보기</button></div>';
    }
  };

  // ═════ 지갑 (머리 띠 캡슐) ═════
  C.wallet = {
    title: '내 MeAI 지갑',
    render(h) {
      const W = h.wallet, co = W.coffee;
      const chance = 1 - Math.pow(1 - co.winners / co.poolAssumed, W.tickets);
      const feed = W.today.length ? W.today.map((g) => '<li><span class="tm">' + F.hm(g.ts) + '</span><span>' + esc(g.label) + '</span><span class="am ' + ({ ticket: 't', lotto: 'l', shield: 's', badge: 'b' }[g.type] || '') + '">' +
        ({ ticket: '응모권 +' + g.amount, lotto: '+' + g.amount + '세트', shield: (g.amount > 0 ? '보호권 +' : '보호권 ') + g.amount, badge: '배지' }[g.type] || '') + '</span></li>').join('') : '<li><span>아직 오늘 받은 보상이 없어요. 출석 도장부터 찍어 볼까요?</span></li>';
      return head(I.ticket, '내 MeAI 지갑', esc(h.week.label)) +
        '<div class="nz-cb"><div class="nz-wal"><div>' + I.ticket.replace('<svg', '<svg class="gold"') + '<small>커피 응모권 (이번 주)</small><b>' + W.tickets + '장</b></div><div>' + I.lotto + '<small>' + esc(h.labels.lotto) + '</small><b>' + W.sets + '세트</b></div><div>' + I.shield + '<small>보호권</small><b>' + W.shields + '장</b></div></div>' +
        '<div class="nz-rowinfo">' + I.gift + '<span>금요일 17:00 커피 추첨 · 응모권 1장 = 1번 응모 · 당첨 ' + co.winners + '명</span><span class="r">내 기대 확률 <b>' + F.pct(chance) + '</b></span></div>' +
        '<p class="nz-note">기대 확률은 이번 주 전체 응모권 약 ' + F.n(co.poolAssumed) + '장을 가정한 계산값이에요 <span class="nz-ex">가정값</span></p>' +
        '<div class="nz-kicker">오늘 받은 보상</div><ul class="nz-feed">' + feed + '</ul></div>' +
        '<div class="nz-cf"><button type="button" class="nz-btn dark wide" data-act="dash">' + I.dash + '내 기록 전체 보기 · 배지 ' + W.badges + '개</button></div>';
    }
  };

  // ═════ 더보기 : 오늘의 운세 보내기 · 넛지 설정 ═════
  const FORTUNE_MSG = '고객님, 오늘 운세 한번 보실래요? 이름과 생년월일만 넣으면 사주와 타로로 오늘 하루를 알려 줘요. 재미로 가볍게 보세요.';
  C.more = {
    title: '더보기',
    render(h) {
      const s = h.settings;
      return head(I.dots, '더보기', '') +
        '<div class="nz-cb"><div class="nz-fort"><span class="moon" aria-hidden="true"></span><div><b>오늘의 운세로 안부 건네기</b><p>사주 · 타로를 고객에게 보내 대화를 가볍게 열어요. 입력한 정보는 고객 휴대폰 밖으로 나가지 않아요.</p></div></div>' +
        '<div class="nz-tpl">' + esc(FORTUNE_MSG) + '</div><div class="nz-row2"><button type="button" class="nz-btn sec" data-act="fortune-copy">' + I.copy + '안부 문구 복사</button><button type="button" class="nz-btn dark" data-go="fortune">' + I.moon + '운세 열어 보기</button></div>' +
        '<div class="nz-kicker">넛지 설정 · 나에게만 적용</div><div class="nz-set">' +
        '<div class="row"><div><b>축하 연출</b><small>도장 · 슬롯 · 미션 달성 화면</small></div>' + seg('fx', s.fx, [['full', '화려하게'], ['simple', '간단히'], ['off', '끄기']]) + '</div>' +
        '<div class="row"><div><b>소리</b><small>도장 · 슬롯 · 정답 효과음</small></div>' + sw('sound', s.sound, '소리') + '</div>' +
        '<div class="row"><div><b>버디 말풍선</b><small>인사말 옆 한 줄 안내</small></div>' + sw('buddy', s.buddy, '버디 말풍선') + '</div>' +
        '<div class="row"><div><b>리그 순위 보이기</b><small>끄면 주간 패스만 보여요</small></div>' + sw('hideRank', !s.hideRank, '리그 순위') + '</div>' +
        '<div class="row"><div><b>화법 한 줄 바꾸기</b><small>막대의 오늘의 화법</small></div>' + seg('tickerSec', s.tickerSec, [[5, '5초'], [8, '8초'], [12, '12초'], [0, '끄기']]) + '</div>' +
        '</div><p class="nz-note">화면을 가리는 팝업은 없어요 · 연출은 누르면 바로 넘어가요 · 이 설정은 다른 사람에게 영향이 없어요</p></div>';
    }
  };
  NZ.acts['fortune-copy'] = () => {
    const done = () => { NZ.toast('안부 문구를 복사했어요. 카톡 · 문자에 붙여 넣어 보내 보세요', { icon: 'copy' }); NZ.log('fortune', 'copy'); NZ.run(NZ.api.event('fortune.send', {}), { quiet: true }); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(FORTUNE_MSG).then(done, done); else done();
  };
  NZ.acts.set = (t) => {
    let k = t.dataset.key, v = t.dataset.val;
    if (v === 'true' || v === 'false') v = v === 'true';
    else if (/^\d+$/.test(v)) v = +v;
    if (k === 'hideRank' && t.classList.contains('nz-sw')) v = !v; // 스위치는 「보이기」라 반대로 저장
    const p = {}; p[k] = v;
    NZ.log('settings', k, { v: v });
    document.documentElement.classList.toggle('nz-calm', k === 'fx' ? v === 'off' : document.documentElement.classList.contains('nz-calm'));
    if (k === 'sound' && v) setTimeout(() => NZ.sfx.ding(), 50);
    return NZ.run(NZ.api.saveSettings(p), { quiet: true }).then(() => { if (k === 'tickerSec') NZ.ui.startTicker(); });
  };
})(window);
