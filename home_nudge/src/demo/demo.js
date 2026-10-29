/* MeAI 홈 넛지 v5 · 데모 메뉴 (목업 시연 전용. 실제 화면에는 들어가지 않는다)
 * 왼쪽 아래 「데모 메뉴」 : 데모 시계 바꾸기 · 보는 사람 바꾸기 · 연출 바로 보기 · 행운 존 · 운영 설정 바꿔 보기 · 처음 상태로
 */
(function (G) {
  'use strict';
  const NZ = G.__NZ, I = NZ.I, esc = NZ.esc, F = NZ.fmt;
  const TIMES = [
    ['2026-10-29', '08:50', '목 08:50 · 퀴즈 열리기 전'], ['2026-10-29', '09:12', '목 09:12 · 아침(처음)'], ['2026-10-29', '12:10', '목 12:10 · 점심'],
    ['2026-10-29', '14:05', '목 14:05 · 오후 피버 ×2'], ['2026-10-29', '16:20', '목 16:20 · 끊김 위기'], ['2026-10-30', '12:30', '금 12:30 · 추첨 날'], ['2026-10-30', '17:05', '금 17:05 · 추첨 발표 · 리캡'], ['2026-11-02', '08:50', '월 08:50 · 새 회차']
  ];
  const PEOPLE = [['fp', '일반 FP (최현아)'], ['rookie', '신인 FP · 첫 7일 여정'], ['leader', '지점장 · 본부 현황'], ['hq', '본사 데이터 담당']];
  const SHOW = [['stamp', '출석 도장'], ['quest', '미션 달성'], ['mission', '일일 미션'], ['allclear', '올클리어'], ['slot', '슬롯머신'], ['draw', '추첨 당첨(예시)'], ['streak', '20영업일 연속'], ['first', '첫 경험(신인)'], ['badge', '배지'], ['recap', '주간 리캡'], ['rankup', '순위 상승']];
  const FUN = [['roulette', 'CRM 룰렛'], ['cslot', '고객 슬롯'], ['challenge', 'OX 챌린지'], ['tarot', '오늘의 타로'], ['scratch', '스크래치'], ['fortune-card', '오늘의 운세'], ['bingo', '빙고 축하'], ['fever', '나만의 피버']];
  let api, box, persona = 'fp';

  function render() {
    const h = NZ.home, cfg = api.demo.cfg();
    const pressed = (b) => ' aria-pressed="' + !!b + '"';
    NZ.html(box.querySelector('.panel'),
      '<h5>데모 시계</h5><div class="clock">' + F.md(h.today) + ' ' + h.hm + ' <small>· 정한 시각부터 실제 시간처럼 흘러요</small></div>' +
      '<div class="g">' + TIMES.map((t, i) => '<button type="button" data-t="' + i + '">' + t[2] + '</button>').join('') + '</div>' +
      '<h5>보는 사람</h5><div class="g">' + PEOPLE.map((p) => '<button type="button" data-p="' + p[0] + '"' + pressed(persona === p[0]) + '>' + p[1] + '</button>').join('') + '</div>' +
      '<h5>연출 바로 보기</h5><div class="g">' + SHOW.map((s) => '<button type="button" data-s="' + s[0] + '">' + s[1] + '</button>').join('') + '</div>' +
      '<h5>행운 존 (v5.1)</h5><div class="g">' + FUN.map((s) => '<button type="button" data-f="' + s[0] + '">' + s[1] + '</button>').join('') + '<button type="button" data-refill>오늘 기회 다시 채우기 · 스크래치 +1</button></div>' +
      '<h5>운영 설정 바꿔 보기 (본사 관리 화면 값)</h5>' +
      '<div class="g"><button type="button" data-issue="reco.open"' + pressed(cfg.lotto.issueOn === 'reco.open') + '>로또 : 고객 열 때 (목업)</button><button type="button" data-issue="chat.custom"' + pressed(cfg.lotto.issueOn === 'chat.custom') + '>로또 : 맞춤대화 때 (권장)</button></div>' +
      '<div class="g"><button type="button" data-alt="0"' + pressed(!cfg.labels.useAltLottoName) + '>명칭 MeAI 로또</button><button type="button" data-alt="1"' + pressed(cfg.labels.useAltLottoName) + '>명칭 MeAI 행운번호</button><button type="button" data-quiz>퀴즈 OX ↔ 객관식</button></div>' +
      '<h5>기타</h5><div class="g"><button type="button" data-reset>처음 상태로</button><button type="button" data-sound' + pressed(h.settings.sound) + '>' + (h.settings.sound ? I.sound + ' 소리 켜짐' : I.mute + ' 소리 꺼짐') + '</button></div>' +
      '<p class="nz-note">데모 메뉴는 시연용이에요. 사람 이름 · 당첨 · 조직 숫자는 모두 예시예요.</p>');
  }
  function sampleDraw() {
    const L = NZ.home.lotto, sets = L.sets.length ? L.sets.map((s) => ({ no: s.no, nums: s.nums })) : [{ no: 1, nums: [4, 11, 23, 29, 36, 42] }, { no: 2, nums: [8, 15, 17, 30, 31, 45] }];
    const base = sets[0].nums.slice(0, 3), pool = []; for (let i = 1; i <= 45; i++) if (sets.every((s) => s.nums.indexOf(i) < 0)) pool.push(i);
    const draw = base.concat(pool.sort(() => Math.random() - 0.5).slice(0, 3)).sort((a, b) => a - b);
    return { lotto: L, draw: draw, sets: sets, example: true, seed: L.commit };
  }
  function show(k) {
    box.classList.remove('open');
    const R = ['come', 'learn', 'sell'];
    if (k === 'stamp') { NZ.ui.open('attend', 'pin'); setTimeout(() => NZ.ui.stampAnim(), 300); return; }
    if (k === 'quest') return NZ.fx.questClear({ title: '추천 고객 1명 열기', ring: R[2], n: 2, total: 5 });
    if (k === 'mission') return NZ.fx.play([{ type: 'mission' }], [], {});
    if (k === 'allclear') return NZ.fx.play([{ type: 'allclear' }], [], {});
    if (k === 'slot') { const n = []; while (n.length < 6) { const x = 1 + Math.floor(Math.random() * 45); if (n.indexOf(x) < 0) n.push(x); } return NZ.fx.slot({ nums: n.sort((a, b) => a - b), nth: NZ.home.lotto.sets.length + 1 }); }
    if (k === 'draw') return NZ.acts['lotto-draw'](null, null, sampleDraw());
    if (k === 'streak') return NZ.fx.play([{ type: 'streak', days: 20, badge: '횃불' }], [], {});
    if (k === 'first') return NZ.fx.play([{ type: 'first', kind: 'reco.open', title: '첫 추천 고객 열기', text: 'MeAI가 고른 오늘의 고객을 처음 열었어요.' }], [], {});
    if (k === 'badge') return NZ.fx.play([{ type: 'badge', label: '척척박사', desc: '퀴즈 5번 연속 정답' }], [], {});
    if (k === 'rankup') return NZ.fx.play([{ type: 'rankup', from: 3, to: 2 }], [], {});
    if (k === 'recap') return api.getRecap().then((rc) => NZ.fx.recap(rc));
  }
  function onClick(e) {
    const t = e.target.closest('button'); if (!t) return;
    if (t.classList.contains('open')) { box.classList.toggle('open'); if (box.classList.contains('open')) render(); return; }
    const d = t.dataset;
    if (d.t != null) { const x = TIMES[+d.t]; NZ.ui.close(true); api.demo.setTime(x[0], x[1]).then((h) => { NZ.setHome(h); render(); NZ.toast('데모 시계를 <b>' + x[2] + '</b>로 옮겼어요'); }); return; }
    if (d.p) {
      persona = d.p; NZ.ui.close(true);
      api.demo.persona(d.p).then((h) => { NZ.setHome(h); render(); if (d.p === 'leader') NZ.dash.open('org'); if (d.p === 'hq') NZ.dash.open('hq'); if (d.p === 'rookie') NZ.toast('신인 FP 보기 · 리그 자리에 <b>첫 7일 여정</b>이 나와요'); });
      return;
    }
    if (d.s) return show(d.s);
    if (d.f) {
      box.classList.remove('open');
      if (d.f === 'bingo') { const b = NZ.home.fun.bingo; return NZ.fx.play([{ type: 'bingo', lines: [0], fresh: [0], count: Math.max(1, b.count + 1), filled: Math.min(9, b.filled + 1) }], [], {}); }
      if (d.f === 'fever') return NZ.fx.play([{ type: 'fever', min: 30, mult: 2, until: NZ.home.serverTime + 1800000 }], [], {});
      return NZ.fun.go(d.f);
    }
    if (d.refill != null) return api.demo.refillFun().then((h) => { NZ.setHome(h); render(); NZ.toast('오늘의 행운 존 기회를 다시 채웠어요 · 스크래치 복권 1장'); });
    if (d.issue) return api.demo.setIssueOn(d.issue).then((h) => { NZ.setHome(h); render(); NZ.toast(d.issue === 'reco.open' ? '추천 고객 카드를 열면 바로 세트가 나와요(목업 시연용)' : '추천 고객과 맞춤대화를 시작하면 세트가 나와요(운영 권장)'); });
    if (d.alt != null) return api.demo.setAltName(d.alt === '1').then((h) => { NZ.setHome(h); render(); });
    if (d.quiz != null) return api.demo.swapQuiz().then((h) => { NZ.setHome(h); render(); NZ.toast('오늘의 퀴즈를 바꿨어요'); });
    if (d.reset != null) { NZ.ui.close(true); return api.demo.reset().then((h) => { NZ.setHome(h); render(); NZ.toast('처음 상태로 되돌렸어요'); }); }
    if (d.sound != null) return api.saveSettings({ sound: !NZ.home.settings.sound }).then((r) => { NZ.setHome(r.home); render(); NZ.sfx.ding(); });
  }
  G.NZDemo = {
    mount(a) {
      api = a;
      box = NZ.el('<div class="nz nz-demo"><button type="button" class="open" aria-haspopup="dialog">' + I.play + '데모 메뉴</button><div class="panel" role="dialog" aria-label="데모 메뉴"></div></div>');
      document.body.appendChild(box);
      box.addEventListener('click', onClick);
      document.addEventListener('pointerdown', (e) => { if (box.classList.contains('open') && !box.contains(e.target) && !e.target.closest('.nz-layer')) box.classList.remove('open'); }, true);
      NZ.onChange(() => { if (box.classList.contains('open')) render(); });
    }
  };
})(window);
