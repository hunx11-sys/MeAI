// MeAI × FM 90분 강의교안 · FM님을 더 슬기롭게, 편안하게, 즐겁게 (FM WORKSHOP ONE WAY · 2026.11.10)
// 내용 : 기존 MeAI × FM 강의교안(261110) PART 1~8 그대로 · 감성 : 참고 교안(검은 바탕 · 한 장 한 메시지 · 큰 글자 · 빨간 강조 · 그림을 크게)
// node build_fm.js <작업폴더 W> <PretendardVariable.woff2> <출력폴더> [이름]
//   W/cap 에 cap_tools.js 로 index · tool_search · tool_map · tool_history · tool_sim · itc 를 먼저 찍어 둔다
const path = require('path');
const { url, cap, asset, crop, sec, build } = require('./kit');

const W = process.argv[2], FONT = process.argv[3], OUT = process.argv[4];
const LAW = '내부 설계사·매니저 교육용 자료로 고객 및 외부에 배포·게시할 수 없습니다. MeAI 답변은 생성형 AI로 작성되어 오류가 있을 수 있으며, 보장·지급 내용은 반드시 약관과 근거자료를 확인하세요 [금융소비자보호법 제22조 준수목적].';
const tcap = n => url(path.join(W, 'cap', n + '.png'));

const S = [];
const add = (h, n, src) => S.push({ h, n, src });
const kv = (a, b) => `<div><div style="font-size:30px;font-weight:800;letter-spacing:-0.02em">${a}</div><div class="ps" style="margin-top:4px">${b}</div></div>`;
const list = (items, gap) => `<div style="display:flex;flex-direction:column;gap:${gap || 22}px">${items.map(([a, b]) => kv(a, b)).join('')}</div>`;
const numList = (items, gap) => `<div style="display:flex;flex-direction:column;gap:${gap || 22}px">${items.map(([a, b], i) => `<div class="row" style="gap:22px;align-items:flex-start"><span class="num" style="width:48px;height:48px;font-size:24px;margin-top:2px">${i + 1}</span>${kv(a, b)}</div>`).join('')}</div>`;
const hero = (img, sw, sh, cy, ch, dw, left, top, deg) => `
<div class="spot" style="left:${left - 120}px;top:${top - 100}px;width:${dw + 300}px;height:${Math.round(ch * dw / sw) + 300}px"></div>
<div style="position:absolute;left:${left}px;top:${top}px;width:${dw}px;perspective:2400px">
  <div class="scr" style="position:relative;transform:rotateY(${deg || -10}deg) rotateX(3deg);transform-origin:left center">${crop(img, sw, sh, 0, cy, sw, ch, dw)}</div>
</div>`;

// ───────────── 00 오프닝 · 어느 매니저의 하루 (0:00~0:08)
add(`
<div style="position:absolute;right:-200px;top:120px;width:1300px;height:1000px;perspective:2200px">
  <div style="transform:rotateY(-20deg) rotateX(8deg) rotateZ(-2deg);transform-origin:left center;border-radius:20px;overflow:hidden;opacity:.55">
    ${crop(cap('hero/term_pc_full.png'), 2880, 1800, 0, 0, 2880, 1800, 1300)}
  </div>
</div>
<div style="position:absolute;inset:0;background:linear-gradient(90deg,#000 36%,rgba(0,0,0,.55) 64%,rgba(0,0,0,.25) 100%),linear-gradient(0deg,#000 0%,rgba(0,0,0,0) 34%)"></div>
<div class="box kick" style="position:absolute;left:120px;top:96px;font-size:24px">FM WORKSHOP ONE WAY · 2026.11.10</div>
<div class="box" style="position:absolute;left:120px;top:286px">
  <div class="kick y">매니저 관리역량 · MeAI 활용한 신인관리 Tool · 90분</div>
  <div style="font-size:170px;font-weight:900;line-height:1.1;letter-spacing:-0.04em;margin-top:30px">MeAI <span class="r">×</span> FM</div>
  <div style="font-size:46px;font-weight:700;color:#d8d9dc;margin-top:50px;letter-spacing:-0.02em">FM님을 더 <span class="y">슬기롭게</span>, <span class="y">편안하게</span>, <span class="y">즐겁게</span></div>
</div>
<div class="box" style="position:absolute;left:120px;bottom:120px;font-size:30px;font-weight:700">세일즈혁신TF&nbsp;&nbsp;이헌수</div>`,
`[0:00 · 1분] 가볍게 인사. 오늘 90분 뒤에 매니저님의 아침 조회 첫 마디가 바뀝니다.
MeAI에 대해 궁금한 부분은 언제든 편하게 말씀해 주세요.`);

const day = (t, q) => `<div class="dh">어느 매니저의 하루</div>
<div class="ctr"><div class="box"><div class="y" style="font-size:64px;font-weight:800;letter-spacing:-0.02em">${t}</div>
<div style="font-size:104px;font-weight:900;letter-spacing:-0.04em;line-height:1.3;margin-top:30px">${q}</div></div></div>`;
add(day('09:30', '“매니저님,<br>이번 달 뭐 팔아요?”'), `[0:01] 천천히, 설명 없이 읽습니다. 이번 달 영업방향, 신담보가 뭔지, 누구한테 먼저 가야 하는지.`);
add(day('11:40', '“매니저님,<br>이 특약 뭐예요?”'), `[0:01] 특약 이름은 아는데 고객 말로 설명이 안 됩니다. 용어가 어렵습니다.`);
add(day('16:20', '“매니저님…<br>거절당했어요.”'), `[0:02] '생각해 볼게요' 뒤에 뭘 해야 하는지 모릅니다. 다음 연락이 두렵습니다.`);
add(`<div class="dh">어느 매니저의 하루</div>
<div class="ctr"><div class="box"><div class="y" style="font-size:64px;font-weight:800">18:00</div>
<div class="diary" style="margin-top:30px;font-size:72px">오늘 몇 번 대답했을까.<br>그런데 왜 내일도<br>같은 질문을 들을까.</div></div></div>`,
`[0:02] 세 질문은 전부 '사실'을 묻는 질문입니다. 그래서 매일 다시 옵니다.`);

add(`<div class="ctr"><div class="box">
  <div class="h2">답을 주면, 질문은 내일 또 옵니다.</div>
  <div style="font-size:92px;font-weight:900;letter-spacing:-0.035em;line-height:1.3;margin-top:50px"><span class="r">찾는 법을 주면, 질문이 줄어듭니다.</span></div>
</div></div>`,
`[0:03] 오늘 90분의 결론을 먼저 말합니다. 사실은 MeAI가, 순서와 태도는 매니저가.`);

const seg = (i, n, r, on) => {
  const a0 = -90 + i * (360 / n) + 1.4, a1 = -90 + (i + 1) * (360 / n) - 1.4, rad = d => d * Math.PI / 180;
  const p = a => [320 + r * Math.cos(rad(a)), 320 + r * Math.sin(rad(a))];
  const [x0, y0] = p(a0), [x1, y1] = p(a1);
  return `<path d="M${x0.toFixed(1)} ${y0.toFixed(1)} A${r} ${r} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}" stroke="${on ? '#E60023' : '#2A2B2F'}" stroke-width="46" fill="none"${on ? ' filter="url(#gl)"' : ''}/>`;
};
add(`
<div class="box" style="position:absolute;left:150px;top:200px;width:640px;height:640px">
  <svg width="640" height="640" viewBox="0 0 640 640"><defs><filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  ${[...Array(15)].map((_, i) => seg(i, 15, 270, i === 0)).join('')}</svg>
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:190px;font-weight:900;letter-spacing:-0.05em">8<span style="font-size:110px;margin-top:40px">분</span></div>
</div>
<div class="box" style="position:absolute;left:900px;top:250px;width:900px">
  <div class="kick">매니저가 한 사람에게 쓸 수 있는 코칭 시간</div>
  <div class="p" style="margin-top:22px">하루 코칭 가능 시간 2시간 ÷ 관리 인원 15명 <span class="g">(예시)</span></div>
  <div class="h3" style="margin-top:70px">이 시간이 턱없이 부족한 사람도 있고,<br>한 사람에게 1시간 넘게 쓸 때도 있습니다.</div>
  <div class="h4 y" style="margin-top:40px">그래서 ‘사실 확인’은 MeAI에게 넘깁니다.</div>
</div>`,
`[0:03] 2시간 ÷ 15명은 예시 숫자라고 꼭 말합니다. 매니저님 지점의 숫자로 바꿔서 물어보세요.`);

add(`<div class="ctr"><div class="box">
  <div style="font-size:150px;font-weight:900;letter-spacing:-0.04em;line-height:1.2">AI는 <span class="y">What</span>,<br>매니저는 <span class="r">Why</span></div>
  <div class="p" style="margin-top:56px">매니저가 더 많이 아는 게 아니라, <span class="w">어디서 찾고 무엇을 믿지 말지 아는 것.</span><br>끝은 늘 “MeAI에 묻고 근거를 가져오세요, 그때 이야기해요”.</div>
</div></div>`,
`[0:04] 한 줄 메시지.
AI가 답하는 것 : 사실 확인 · 증권 해석, 화법 초안 · 문안, 용어 뜻 · 통계 · 의학, 보장분석 · 요약 리포트.
매니저만 하는 것 : 질문 순서 · 태도, 병목 진단 · 동행, 격려 · 기다리기, "이건 믿지 마" 판단.`);

add(`<div class="ctr"><div class="box">
  <div class="kick">90분 동안 드리고 싶은 약속</div>
  <div class="row" style="justify-content:center;gap:100px;margin-top:60px;align-items:flex-start">
    ${[['슬기롭게', 'PART 1~4', '신인이 묻는 ‘무엇’은<br>MeAI가 먼저 답하게'], ['편안하게', 'PART 5~6', '하루 30분 루틴과<br>도구 6종으로 손을 덜기'], ['즐겁게', 'PART 7~8', '실습 · 오래 쓰는 약속<br>내일 아침 첫 마디']].map(([a, b, c], i) => `<div><div style="font-size:150px;font-weight:900;letter-spacing:-0.04em;line-height:1">${i === 1 ? `<span class="r">${a}</span>` : a}</div><div class="kick y" style="margin-top:34px">${b}</div><div class="p" style="margin-top:10px">${c}</div></div>`).join('')}
  </div>
</div></div>`,
`[0:05] 세 갈래로 안내합니다. 슬기롭게(숫자 · MeAI 홈 · 대화와 자료 · 2026 스타터), 편안하게(하루 30분 · 도구 6종), 즐겁게(실습 · 약속 · 내일 아침).`);

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:110px;text-align:center"><div class="h1" style="font-size:84px">해당되면 <span class="r">손</span> 한번 들어 주세요</div><div class="p" style="margin-top:12px">평가가 아니라 워밍업입니다. 세 문항 모두 강의 끝에서 답이 나옵니다.</div></div>
<div class="box" style="position:absolute;left:150px;right:150px;top:420px;display:grid;grid-template-columns:repeat(3,1fr);gap:70px">
  ${[['지난주 너무 바빠서 신인에게<br><span class="y">“약관 찾아봐”</span>라고 말한 적 있다', '오늘 답 → 약관 검색 + 특약검색기'], ['<span class="y">“매니저님, 이거 뭐예요?”</span>를<br>하루 10번 이상 듣는다', '오늘 답 → [용어] 버튼 하나로 뜻풀이'], ['위촉식 · 시상식 <span class="y">명패</span>를<br>한글 파일로 손수 만든 적 있다', '오늘 답 → 명패 제작기, 명단 올리고 1분']].map(([q, a], i) => `<div style="border-top:3px solid #E60023;padding-top:30px"><div style="font-size:30px;font-weight:900;color:#E60023">Q${i + 1}</div><div style="font-size:40px;font-weight:800;line-height:1.45;margin-top:18px;letter-spacing:-0.025em">${q}</div><div class="ps" style="margin-top:26px">${a}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:880px;text-align:center;font-size:34px">셋 다 O 이신 분, 오늘 90분이 앞으로 삶의 질이 늘어나는 전환점이 될 겁니다.</div>`,
`[0:06] 손 든 사람 수를 세며 분위기 띄우기. 답은 강의 안에 다 나옵니다(Q1 → 64장, Q2 → 35장, Q3 → 68장).`);

const FMB = [['약관 박사형', '“그건 약관 제3조 2항에…”<br>신인은 끄덕끄덕, 다음 날 싹 까먹음', '답 대신 특약검색기 코드 하나.<br>찾는 법을 가르치면 신인이 박사가 됩니다'], ['내가 다 해줄게형', '설계도 문안도 매니저 손.<br>신인은 구경만, 매니저는 늘 야근', '‘보장분석 해줘’는 신인 손가락으로.<br>매니저는 빨간 펜 3줄'], ['숫자만형', '“몇 통 했어요?”만 묻고<br>왜 안 됐는지는 안 물음', '“오늘 카드는 누구예요? 왜요?”<br>추천 카드가 이유를 적어 둡니다'], ['조용히 지켜보기형', '믿고 맡기는 중.<br>신인은 혼자 헤매다 찾아옴', '금요일 15분 리플레이.<br>가르치지 말고 자기 대화를 설명하게']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="kick y">재미로 보는 FMBTI</div><div class="h1" style="font-size:80px;margin-top:12px">나는 어떤 매니저일까</div></div>
<div class="box" style="position:absolute;left:110px;right:110px;top:350px;display:grid;grid-template-columns:repeat(4,1fr);gap:40px">
  ${FMB.map(([a, b, c]) => `<div><div style="font-size:44px;font-weight:900;letter-spacing:-0.03em">${a}</div><div class="ps" style="margin-top:18px;font-size:23px">${b}</div><div style="font-size:24px;font-weight:700;color:#FFD43B;margin-top:22px;line-height:1.55">${c}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:840px;text-align:center;font-size:40px">네 유형의 공통 처방 : <span class="r">답을 주지 말고, 찾아오게 하고, 그때 이야기하기.</span></div>`,
`[0:07] 유형은 농담, 처방은 진담. 마음속으로 나는 어떤 유형인지 생각해 보시게 합니다.`);

// ───────────── PART 1 숫자 (0:08~0:16)
add(sec('01', '숫자', '숫자가 먼저 말합니다', '‘회사가 하라니까’로 답하면 신인은 안 씁니다. 매니저님이 먼저 납득하는 숫자 네 개.'), `[0:08] PART 1.`);

const person = (x, on) => `<g transform="translate(${x},0)" fill="${on ? '#FFD43B' : '#2A2B2F'}"><circle cx="40" cy="34" r="28"/><path d="M0 150 Q0 76 40 76 Q80 76 80 150 Z"/></g>`;
add(`<div class="ctr"><div class="box">
  <div class="kick">TA채널 FP 열 명 중 아홉 명</div>
  <svg width="1240" height="150" viewBox="0 0 1240 150" style="margin-top:44px">${[...Array(10)].map((_, i) => person(i * 124 + 2, i < 9)).join('')}</svg>
  <div style="font-size:250px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:40px" class="y">91.1%</div>
  <div class="h4" style="margin-top:30px">MeAI를 한 번 이상 써 봤습니다 <span class="g">(10,968명)</span></div>
</div></div>`,
`[0:09] 숫자는 가이드북 그대로. 이미 열 명 중 아홉 명이 써 봤습니다. 문제는 '매일 쓰느냐'입니다.`,
'자료: 2026년 8월 TA채널 MeAI 사용 데이터 분석 (MeAI 활용 가이드북 p.9)');

add(`
<div class="box" style="position:absolute;left:140px;top:250px">
  <div class="kick">MeAI를 쓴 경우, 체결전환율</div>
  <div style="font-size:260px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:30px">2.8<span style="font-size:150px">배</span></div>
  <div class="h4" style="margin-top:56px;font-weight:600">같은 FP의 고객끼리 비교해도 <span class="y">4배</span> <span class="g">(9.0% → 36.0%)</span></div>
  <div class="p" style="margin-top:8px">고객 탓이 아니라 습관 차이입니다.</div>
</div>
<div class="box" style="position:absolute;right:200px;top:190px;width:560px;height:720px">
  <div style="position:absolute;bottom:80px;left:40px;width:190px;height:${Math.round(560 * 12.7 / 35.4)}px;background:#2A2B2F;border-radius:14px 14px 0 0"></div>
  <div style="position:absolute;bottom:80px;left:330px;width:190px;height:560px;background:var(--red);border-radius:14px 14px 0 0;box-shadow:0 0 90px rgba(230,0,35,.45)"></div>
  <div class="h4" style="position:absolute;left:40px;width:190px;text-align:center;bottom:${80 + Math.round(560 * 12.7 / 35.4) + 14}px;color:#8E9095">12.7%</div>
  <div class="h4" style="position:absolute;left:330px;width:190px;text-align:center;bottom:654px">35.4%</div>
  <div class="ps" style="position:absolute;left:40px;width:190px;text-align:center;bottom:30px">미활용</div>
  <div class="ps w" style="position:absolute;left:330px;width:190px;text-align:center;bottom:30px">활용</div>
</div>`,
`[0:10] 체결전환율 12.7% → 35.4%. 같은 FP의 고객끼리도 9.0% → 36.0%.
MeAI를 하루 1번 이상 꾸준히 쓰는 습관이 영업 빈도 · 보장분석 · 상세설계로 이어지는 선순환을 만듭니다.`,
'자료: 2026년 8월 TA채널 MeAI 사용 데이터 분석 (MeAI 활용 가이드북 p.9)');

const Q3 = [['질문 1개', 11.99], ['2개', 17.02], ['3개 이상', 27.79]];
add(`
<div class="box" style="position:absolute;left:140px;top:250px;width:780px">
  <div class="kick">많이 질문할수록, 평균 가계약</div>
  <div class="y" style="font-size:260px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:30px">2.3<span style="font-size:150px">배</span></div>
  <div class="h4" style="margin-top:56px;font-weight:600">신인이 <span class="r">세 번 묻게</span> 하는 것이 매니저의 일</div>
  <div class="p" style="margin-top:8px">뒤에 나오는 꼬리질문 버튼과 이어집니다.</div>
</div>
<div class="box" style="position:absolute;right:160px;top:190px;width:760px;height:720px">
  ${Q3.map(([l, v], i) => { const h = Math.round(560 * v / 27.79), x = 30 + i * 250; return `<div style="position:absolute;bottom:80px;left:${x}px;width:180px;height:${h}px;background:${i === 2 ? 'var(--yel)' : i ? '#3C3E43' : '#2A2B2F'};border-radius:14px 14px 0 0;${i === 2 ? 'box-shadow:0 0 90px rgba(255,212,59,.35)' : ''}"></div>
  <div class="h4" style="position:absolute;left:${x - 20}px;width:220px;text-align:center;bottom:${80 + h + 14}px;color:${i === 2 ? '#fff' : '#8E9095'}">${v.toFixed(2)}건</div>
  <div class="ps" style="position:absolute;left:${x - 20}px;width:220px;text-align:center;bottom:30px;${i === 2 ? 'color:#fff' : ''}">${l}</div>`; }).join('')}
</div>`,
`[0:11] 질문 1개 11.99건 → 2개 17.02건 → 3개 이상 27.79건(평균 가계약).
'질문 3개 이상 2.3배'는 PART 3의 꼬리질문 버튼과 이어집니다. 신인이 세 번 묻게 하는 것이 매니저의 일.`,
'자료: 2026년 8월 TA채널 MeAI 사용 데이터 분석 (MeAI 활용 가이드북 p.9)');

const BARS = [['미사용', 10.22, '5,987명'], ['1일', 19.81, '1,835명'], ['2~4일', 26.35, '2,487명'], ['5~9일', 38.47, '1,372명'], ['10일 이상', 55.04, '362명']];
const BC = ['#232427', '#2E2F33', '#3C3E43', '#55575D', 'var(--red)'];
add(`
<div class="box h2" style="position:absolute;left:140px;top:90px">한 달에 <span class="y">10일</span> 이상 쓰면, 평균 가계약 <span class="r">5.4배</span></div>
<div class="box" style="position:absolute;left:220px;top:300px;width:1480px;height:600px">
  ${BARS.map(([l, v, c], i) => {
    const h = Math.round(440 * v / 55.04), x = i * 300;
    return `<div style="position:absolute;left:${x}px;bottom:110px;width:200px;height:${h}px;background:${BC[i]};border-radius:12px 12px 0 0;${i === 4 ? 'box-shadow:0 0 100px rgba(230,0,35,.5)' : ''}"></div>
    <div style="position:absolute;left:${x}px;width:200px;text-align:center;bottom:${110 + h + 14}px;font-size:40px;font-weight:800;color:${i === 4 ? '#fff' : '#8E9095'}">${v.toFixed(2)}</div>
    <div style="position:absolute;left:${x - 20}px;width:240px;text-align:center;bottom:48px;font-size:28px;font-weight:700;color:${i === 4 ? '#fff' : '#8E9095'}">${l}</div>
    <div style="position:absolute;left:${x - 20}px;width:240px;text-align:center;bottom:10px;font-size:20px;color:#55575c">${c}</div>`;
  }).join('')}
</div>
<div class="box p" style="position:absolute;left:140px;top:930px;font-size:28px">신인에게 10일은 2주입니다. <span class="w">매일 아침 MeAI 홈을 여는 것만으로 활동일이 쌓입니다.</span> · 매출 보유율도 1.8배 (53.1% → 94.8%)</div>`,
`[0:12] 7월 MeAI 활동일별 비교. MeAI 홈을 아침마다 여는 습관이 곧 활동입니다.`,
'자료: 2026년 8월 TA채널 MeAI 사용 데이터 분석 (가이드북 p.10) · 7월 활동일별 평균 가계약(건) · 인원은 각 구간 FP 수');

const FIND = [['누구에게', '목록을 뒤져 내가 고름', 'MeAI 홈이 오늘의 추천 고객을 보여 줌'], ['왜 지금', '명분을 스스로 만듦', '“상령일이 2주 남았고…” 이유가 붙음'], ['첫 마디', '고민하다 미룸', '카드의 이유 문장이 곧 첫 말'], ['다음 행동', '메뉴를 찾아 헤맴', '[MeAI 고객찾기에서 열기] → 맞춤대화']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:120px;text-align:center">
  <div class="h1 g" style="font-size:84px">찾는 영업에서</div>
  <div class="h1" style="font-size:84px;margin-top:8px"><span class="r">찾아가는 영업</span>으로</div>
</div>
<div class="box" style="position:absolute;left:250px;right:250px;top:470px">
  ${FIND.map(([a, b, c]) => `<div class="row" style="padding:22px 0;border-top:1px solid #222326">
    <div style="width:200px;font-size:28px;font-weight:700;color:#FFD43B">${a}</div>
    <div class="k" style="width:420px;font-size:28px;font-weight:500">${b}</div>
    <div style="width:70px;font-size:28px;color:#55575c">→</div>
    <div style="flex:1;font-size:30px;font-weight:700">${c}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:880px;text-align:center;font-size:34px">매니저 질문이 <span class="g">“몇 통 했어요?”</span>에서 <span class="y">“오늘 카드는 누구예요?”</span>로 바뀝니다.</div>`,
`[0:14] 어제까지는 신인이 고름 : 엑셀 열고 전화번호부 넘기고 고르다 하루가 감. 매니저는 "연락 몇 통 했어요?"
오늘부터는 홈이 고름 : 추천 카드 한 문장이 고객에게 첫 말. 발굴은 시스템, 설득은 사람.`,
'자료: MeAI 활용 가이드북 p.6');

// ───────────── PART 2 MeAI 홈 (0:16~0:32)
add(sec('02', 'MeAI 홈', '매일 아침 여는 문', '가이드북 화면 그대로, 매니저가 아침 조회에서 같이 보는 순서로 갑니다. 화면 속 이름 · 숫자는 예시.'), `[0:16] PART 2. 홈 6구역 · 숫자 4개 · 추천 카드 9장 · 고객찾기 · 동의 90일.`);

add(`
<div class="spot" style="left:780px;top:40px;width:1400px;height:1100px"></div>
<div style="position:absolute;left:820px;top:110px;width:1100px;perspective:2400px">
  <div class="scr" style="position:relative;transform:rotateY(-12deg) rotateX(4deg);transform-origin:left center">
    ${crop(cap('hero/gb5_gate_full_m.png'), 2880, 2580, 0, 0, 2880, 2280, 1040)}
  </div>
</div>
<div style="position:absolute;left:0;top:0;bottom:0;width:900px;background:linear-gradient(90deg,#000 70%,rgba(0,0,0,0))"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(0deg,#000 30%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:170px;width:700px">
  <div class="kick y">영업포탈에서 MeAI로 들어오면 가장 먼저</div>
  <div class="h2" style="margin-top:22px;font-size:76px">MeAI 홈 한 화면에<br><span class="r">오늘 연락할 고객</span></div>
  <div style="margin-top:44px">${numList([['대화 카드 두 장', '일반대화는 바로 질문 창, 맞춤대화는 고객 검색부터'], ['내 고객 숫자 4개', '전체 · 맞춤대화 가능 · 사전조회 동의 필요 · 상품제안 가능'], ['오늘의 추천 고객', '연락할 이유가 붙은 카드 3장 × 3세트'], ['매일 새로', '고객 데이터와 추천 결과는 매일 새로 계산해 다음 날 반영']], 18)}</div>
</div>`,
`[0:17] MeAI 홈 6구역 : 인사 + 최근 업데이트, 대화 카드 두 장, 내 고객 숫자 4개, 오늘의 추천 고객, 범례 · 오른쪽 위 버튼(태그 색 · 동의 상태 · 글씨 확대 · 고객 동의 · 게시판).
사전조회 동의도 홈에서 바로 보낼 수 있습니다.`,
'자료: MeAI 활용 가이드북 p.12 · 화면 속 이름과 숫자는 예시');

const STEP = [['고객 데이터', '계약 · 동의 · 상령일 · 생일 · CRM'], ['매일 밤 계산', '추천 고객과 고객찾기 그룹을 매일 자동으로 다시 계산'], ['오늘의 추천 9명', '3명 × 3세트로 MeAI 홈에 표시'], ['점수 대신 이유 한 문장', '왜 지금 이 고객인지 한 문장과 태그로, 동의 상태 칩도 함께'], ['고객찾기에서 열기', '카드 버튼으로 이동, 동의 고객은 바로 맞춤대화 시작']];
add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="h1" style="font-size:80px">매일 밤 계산하고,<br>아침엔 <span class="y">이유 한 문장</span>과 함께</div></div>
<div style="position:absolute;left:200px;right:200px;top:520px;height:3px;background:linear-gradient(90deg,#3A3B3F,#E60023 70%,#3A3B3F)"></div>
<div class="box" style="position:absolute;left:100px;right:100px;top:496px;display:grid;grid-template-columns:repeat(5,1fr)">
  ${STEP.map(([a, b], i) => `<div style="text-align:center;padding:0 16px">
    <div style="width:50px;height:50px;border-radius:50%;margin:0 auto;background:${i === 3 ? '#E60023' : '#fff'};box-shadow:0 0 0 8px #000,0 0 30px ${i === 3 ? 'rgba(230,0,35,.7)' : 'rgba(255,255,255,.35)'}"></div>
    <div style="font-size:22px;font-weight:800;color:#6E7076;margin-top:24px;letter-spacing:0.08em">STEP ${i + 1}</div>
    <div style="font-size:${i === 3 ? 36 : 32}px;font-weight:800;margin-top:8px;line-height:1.3;${i === 3 ? 'color:#ff4d6a' : ''}">${a}</div>
    <div class="ps" style="margin-top:12px;font-size:22px">${b}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:880px;text-align:center;font-size:40px">발굴은 시스템, <span class="r">설득은 사람.</span> 고르는 시간을 없애고 만나는 일에 집중.</div>`,
`[0:19] 고객찾기 그룹은 두 갈래 : 보장 기준(예: 암진단비 부족) · 영업 기회(예: 상령일 임박).
결과는 다음 날 반영되고, 기준 시각은 화면의 '최근 업데이트'. 홈 노출은 사전조회 동의일로부터 3년 이내, 맞춤대화는 동의일부터 90일.`,
'자료: MeAI 활용 가이드북 p.8');

const N4 = [['342', '내 전체 고객', '보유 · 가망 · 이관을 모두 더한 수', '#fff'], ['137', '맞춤대화 가능', '동의일부터 90일이 지나지 않은 고객. 지금 바로 시작', '#fff'], ['186', '사전조회 동의 필요', '동의가 없거나 만료된 고객. 동의 알림톡부터', '#ff4d6a'], ['84', '상품제안 가능', '상품 소개에 동의한 고객. ‘AI 추천 고객’ 리본', '#fff']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="kick">아침 조회는 숫자 4개로 시작</div><div class="h1" style="margin-top:16px;font-size:88px">“동의 필요한 분,<br><span class="r">몇 명</span>이에요?”</div></div>
<div class="box" style="position:absolute;left:120px;right:120px;top:520px;display:grid;grid-template-columns:repeat(4,1fr);gap:40px">
  ${N4.map(([n, a, b, c]) => `<div style="border-top:2px solid ${c === '#fff' ? '#2A2B2F' : '#E60023'};padding-top:26px"><div style="font-size:120px;font-weight:900;letter-spacing:-0.05em;line-height:1;color:${c}">${n}<span style="font-size:48px;margin-left:4px">명</span></div><div style="font-size:32px;font-weight:800;margin-top:18px">${a}</div><div class="ps" style="margin-top:8px;font-size:22px">${b}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:96px;right:96px;top:900px;text-align:center;font-size:28px">숫자 4개를 주간 보드에 적으면 <span class="w">동의 요청이 습관</span>이 됩니다.</div>`,
`[0:20] 매니저의 첫 질문은 "동의가 필요한 분이 몇 명이에요?" 상품제안 가능 = 'AI 추천 고객' 리본.
숫자는 가이드북 예시입니다.`,
'자료: MeAI 활용 가이드북 p.18 · 숫자는 예시');

add(`
<div class="spot" style="left:1000px;top:60px;width:900px;height:980px"></div>
<div class="scr box" style="left:1100px;top:110px;border-radius:26px">${crop(cap('hero/gb5_card_kim_z.png'), 1146, 1242, 0, 0, 1146, 1242, 700)}</div>
<div style="position:absolute;left:1068px;top:262px;width:10px;height:190px;background:var(--red);border-radius:5px;box-shadow:0 0 30px rgba(230,0,35,.8)"></div>
<div class="box" style="position:absolute;left:140px;top:200px;width:880px">
  <div class="kick y">추천 카드 읽는 법</div>
  <div class="h2" style="font-size:84px;margin-top:20px">카드 한 문장<br>= <span class="r">고객에게 첫 말</span></div>
  <div style="margin-top:44px">${list([['이름 · 나이 · 유형 · 담당', '유형은 보유 · 가망 · 이관 중 하나'], ['이유 한 문장', '왜 지금 이 고객인지. 풀면 곧 첫 말'], ['태그 · 동의 칩', '보장 공백 · 당월 타겟 · 이벤트 임박 / D-n이면 바로, ‘필요’면 동의부터']], 20)}</div>
</div>`,
`[0:22] "상령일이 2주 남았고 암진단비가 1천만원뿐입니다." 신인에게 카드 문장을 읽게 하세요.
고객에게 연락하기 전 단서를 MeAI가 제공해 줍니다. [MeAI 고객찾기에서 열기]를 한 번 누르면 고객찾기의 그 고객 카드로 바로 이동.`,
'자료: MeAI 활용 가이드북 p.20 · 이름과 내용은 예시');

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:90px;text-align:center"><div class="h1" style="font-size:88px">카드 3장 × 세트 3개, 매일 아침 <span class="y">9명</span></div>
<div class="p" style="margin-top:14px">오른쪽 · 왼쪽 화살표로 넘기기 · 매일 새로, 다음 날 반영</div></div>
<div class="spot" style="left:260px;top:280px;width:1400px;height:900px"></div>
<div class="scr box" style="left:330px;top:310px;border-radius:22px">${crop(cap('hero/gb5_gate_reco3_m.png'), 2280, 1018, 0, 0, 2280, 950, 1260)}</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:900px;text-align:center;font-size:34px">신인 미션 : 아침에 9장 다 읽고 1명에게 연락. 매니저 질문 : <span class="y">“9장 중 누구부터? 왜요?”</span></div>`,
`[0:23] 오른쪽 왼쪽 화살표를 눌러서 매일 선정되는 9명의 추천 고객을 볼 수 있습니다.
카드를 누르면 고객찾기의 그 고객으로 바로 이동합니다.`,
'자료: MeAI 활용 가이드북 p.21 · 이름과 내용은 예시');

add(`
<div class="spot" style="left:60px;top:200px;width:1300px;height:900px"></div>
<div class="scr box" style="left:110px;top:300px;border-radius:20px">${crop(cap('hero/find_full.png'), 2880, 1800, 0, 0, 2880, 1800, 1080)}</div>
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:80px">고르고 → 펼쳐 보고 → MeAI 대화, <span class="r">세 번 클릭</span></div></div>
<div class="box" style="position:absolute;left:1260px;top:320px;width:580px">${numList([['왼쪽 · 고객 그룹', '보장 기준 / 영업 기회 탭 + 신규 등록 고객'], ['가운데 · 고객 카드', '그룹 설명 문구 + 카드, 누르면 펼쳐짐'], ['오른쪽 · 패널', '추천 질문 + [보장분석] + [이 고객으로 맞춤대화 시작]'], ['위 · 검색 · 글씨 확대', '이름 또는 조건(예: 암진단비)으로 검색']], 24)}</div>`,
`[0:24] 고객찾기는 왼쪽에서 오른쪽으로. 고르고, 펼쳐 보고, MeAI 대화. 세 번 클릭입니다.`,
'자료: MeAI 활용 가이드북 p.31 · 이름과 숫자는 예시');

const GR = [['암진단비 부족', '치료비 실제 부담액을 기준으로 설명하면 필요가 분명해집니다'], ['뇌진단비 부족', '뇌질환은 재활 · 간병 기간이 길어 진단비가 곧 생활비 대체 수단'], ['지원일당 없음', '간병비는 하루 단위로 나가는 실지출, 일당이 없으면 부담이 그대로'], ['상령일 임박', '같은 보장을 더 싸게 준비할 수 있는 마지막 구간'], ['생일 임박', '축하 인사로 대화를 열고 자연스럽게 보장 점검으로'], ['사전동의 만료', '만료 전에 재동의를 받아야 이후에도 연락을 이어 갈 수 있음']];
add(`
<div class="spot" style="left:60px;top:40px;width:900px;height:1000px"></div>
<div class="scr box" style="left:200px;top:110px;border-radius:22px">${crop(cap('hero/find_groups_z.png'), 840, 2250, 0, 0, 840, 1411, 500)}</div>
<div class="box" style="position:absolute;left:860px;top:110px;width:980px">
  <div class="h1" style="font-size:88px">그룹 이름이<br>곧 <span class="r">연락 이유</span></div>
  <div class="p" style="margin-top:16px">보장 기준 10 + 영업 기회 3 · 화면 문구를 그대로 읽어도 화법이 됩니다</div>
  <div style="margin-top:36px;display:flex;flex-direction:column;gap:18px">
    ${GR.map(([a, b]) => `<div class="row" style="gap:28px"><div style="width:220px;font-size:28px;font-weight:800;color:#FFD43B;flex:none">${a}</div><div style="font-size:26px;font-weight:600;color:#D8D9DC">${b}</div></div>`).join('')}
  </div>
</div>`,
`[0:26] 고객의 유형에 따라 그룹이 정해져 있어서 손쉽게 영업 타겟을 선정하고 교육할 수 있습니다.
한 고객이 여러 그룹에 들 수 있고, 그룹 수가 많을수록 할 말이 많은 고객입니다. 주력 담보 부족 그룹부터.
그룹 하나 골라 영업 포인트 강의하기, 본부 교육에서 강의 주제 선정하기에도 씁니다.`,
'자료: MeAI 활용 가이드북 p.32 · p.34 · 그룹 인원은 예시');

add(`
<div class="spot" style="left:20px;top:120px;width:1300px;height:900px"></div>
<div class="scr box" style="left:110px;top:260px;border-radius:22px">${crop(cap('hero/find_card_z.png'), 1944, 1185, 0, 0, 1944, 1185, 1060)}</div>
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:80px">펼치면 여섯 칸, <span class="r">부족 금액</span>이 곧 제안 크기</div></div>
<div class="box" style="position:absolute;left:1260px;top:300px;width:580px">${list([['이유 한 문장', '“암진단비가 1천만원대에 머물러 있습니다.”'], ['사전조회동의 D-n', '만료(90일)까지 남은 날. 만료면 ‘필요’, 철회면 ‘철회’'], ['태그 (우선순위 순)', '보라 = 당월 타겟. 부족 그룹은 그룹마다 색이 다름'], ['점선 칸 · 미확인', '자료가 없으면 ‘미확인’. 추정하지 않음']], 26)}</div>`,
`[0:28] 이 고객 한눈에 보기 여섯 칸 : 가입한 보험 · 보험료 납입 · 접촉기회 · 부족 금액 · 담보 두 칸.
자료가 없으면 '미확인'. 추정하지 않습니다.`,
'자료: MeAI 활용 가이드북 p.35~37 · 이름과 숫자는 예시');

add(`
<div class="spot" style="left:60px;top:40px;width:1000px;height:1000px"></div>
<div class="scr box" style="left:190px;top:110px;border-radius:22px">${crop(cap('hero/find_right_z.png'), 1320, 1440, 0, 0, 1320, 1440, 760)}</div>
<div class="box" style="position:absolute;left:1060px;top:150px;width:780px">
  <div class="kick y">오른쪽 패널에서 다음 행동</div>
  <div class="h2" style="margin-top:20px;font-size:64px">카드 문장은 고객에게 첫 말,<br>추천 질문은 <span class="r">MeAI에게 첫 질문</span></div>
  <div style="margin-top:40px">${numList([['MeAI에 이렇게 물어보세요', '일반대화 · 맞춤대화용 추천 질문 2개. 누르면 입력창에 채워짐 → 전송'], ['[보장분석]', '영업포탈 보장분석 화면으로'], ['[이 고객으로 맞춤대화 시작]', '고객 타겟팅이 끝난 상태로 맞춤대화 진입']], 22)}</div>
</div>`,
`[0:29] 누르고, 고르고, 보내기. 클릭으로 모두 됩니다.`,
'자료: MeAI 활용 가이드북 p.38 · 이름과 질문 문장은 예시');

add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="h1" style="font-size:88px">동의는 <span class="r">알림톡 한 통</span>으로</div><div class="p" style="margin-top:12px">맞춤대화는 보장 내역을 읽고 답변합니다. 그래서 사전조회 동의가 먼저</div></div>
<div class="spot" style="left:60px;top:300px;width:1000px;height:760px"></div>
<div class="scr box" style="left:150px;top:380px;border-radius:22px">${crop(cap('hero/fix_c_consent_modal.png'), 960, 484, 0, 0, 960, 484, 800)}</div>
<div class="box" style="position:absolute;left:1100px;top:340px;width:740px;display:grid;grid-template-columns:1fr 1fr;gap:40px 40px">
  ${[['90일', '맞춤대화 가능 · 동의일부터'], ['15분 안팎', '동의 후 반영'], ['3년 이내', 'MeAI 홈 노출 · 동의일부터'], ['D-n', '칩의 숫자 = 남은 날']].map(([a, b]) => `<div><div class="y" style="font-size:84px;font-weight:900;letter-spacing:-0.04em;line-height:1">${a}</div><div class="ps" style="margin-top:10px">${b}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:870px;text-align:center;font-size:34px">첫 말 : <span class="y">“보장을 정확히 보려면 동의가 필요해요, 알림톡 하나 보내 드릴게요.”</span></div>`,
`[0:30] 어디서 : 고객찾기 [사전조회동의 요청하기] · 홈 [고객 동의] → 휴대폰 번호 입력 → 보내기.
만료 전에는 [사전동의 만료] 그룹에서 미리 재요청. 철회하면 즉시 회색, 정보를 볼 수 없습니다.`,
'자료: MeAI 활용 가이드북 p.46');

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:110px;text-align:center"><div class="h1" style="font-size:88px">맞춤대화로 가는 <span class="r">두 길</span></div><div class="p" style="margin-top:12px">이름을 알면 검색, 고민이면 추천 카드</div></div>
<div class="box" style="position:absolute;left:200px;right:200px;top:380px;display:grid;grid-template-columns:1fr 1fr;gap:90px">
  <div style="border-top:3px solid #3A3B3F;padding-top:30px"><div class="kick g">길 1</div><div style="font-size:52px;font-weight:900;margin-top:10px">이름을 알면</div><div class="p" style="margin-top:20px">홈 [맞춤대화] 카드 → 고객 검색 팝업<br>→ 이름 한 글자 → [맞춤대화]</div></div>
  <div style="border-top:3px solid #E60023;padding-top:30px"><div class="kick y">길 2</div><div style="font-size:52px;font-weight:900;margin-top:10px">누구부터 할지 고민이면</div><div class="p" style="margin-top:20px">추천 카드 → [MeAI 고객찾기에서 열기]<br>→ [이 고객으로 맞춤대화 시작]</div></div>
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:820px;text-align:center;font-size:44px">신인은 <span class="r">길 2부터.</span> 고민하는 시간이 0이 됩니다.</div>`,
`[0:31] 두 길의 차이 : 길 1은 연락할 고객이 이미 정해진 날, 길 2는 "오늘 누구에게 연락할까?"가 고민인 날. 둘 다 그 고객의 맞춤대화로 이어지고, 동의가 살아 있어야 열립니다.`,
'자료: MeAI 활용 가이드북 p.29');

// ───────────── PART 3 대화 · 자료 (0:32~0:50)
add(sec('03', '대화', '대화 한 번에, 자료 참고까지', '신인이 가장 어려워하는 두 가지, 고객 눈높이와 의학 용어. 용어 · 통계 · 의학 그림이 대화 안에 있습니다.'), `[0:32] PART 3.`);

add(`
<div class="box" style="position:absolute;left:180px;right:180px;top:170px;display:grid;grid-template-columns:1fr 1fr;gap:100px">
  <div><div style="font-size:120px;font-weight:900;letter-spacing:-0.04em;line-height:1">일반대화</div><div class="h4" style="margin-top:24px;font-size:36px">무엇이든 물어보는 창</div>
  <div class="p" style="margin-top:30px;line-height:1.9">상품 · 특약 개념 질문 · 약관 지식<br>통계 그래프 · 의학 지식 · [용어] 풀이<br>자사 · 타사 보장 비교 (공부용)<br>고객 설득 화법 만들기</div></div>
  <div><div style="font-size:120px;font-weight:900;letter-spacing:-0.04em;line-height:1"><span class="r">맞춤대화</span></div><div class="h4" style="margin-top:24px;font-size:36px">고객 1명에 맞춘 보장분석부터 설계까지</div>
  <div class="p" style="margin-top:30px;line-height:1.9">고객 선택 → 보장분석<br>부족 보장 · 제안 우선순위<br>상세설계 · 가계약 요청<br>요약 리포트 → 출력 또는 저장</div></div>
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:850px;text-align:center;font-size:40px">둘의 차이는 <span class="y">‘고객을 정했느냐’</span> 하나뿐입니다.</div>`,
`[0:33] [용어] 풀이 · 통계 그래프 · 의학 지식 · 일반/상세 모드는 두 대화 모두에서 됩니다(가이드북 p.49).
들어가는 곳 : 일반대화는 MeAI 홈 [일반대화] 카드 · 모바일 [MeAI 일반대화] · 영업포탈 CRM 리스트, 맞춤대화는 홈 [맞춤대화] 카드 · 고객찾기 · 모바일 [MeAI] · CRM 리스트.`,
'자료: MeAI 활용 가이드북 p.49');

add(hero(cap('real/r01_general_home.png'), 1531, 963, 0, 963, 1000, 870, 200) + `
<div style="position:absolute;left:0;top:0;bottom:0;width:930px;background:linear-gradient(90deg,#000 82%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:160px;width:660px">
  <div class="kick y">MeAI 홈 → [일반대화] 카드</div>
  <div class="h2" style="margin-top:20px;font-size:80px">고르거나,<br>말하듯 <span class="r">묻거나</span></div>
  <div style="margin-top:40px">${list([['질문 예시 탭 3개', '보장비교 · 지식 검색 · 자주하는 질문 → 누르면 바로 시작'], ['[질문 더보기]', '프롬프트 라이브러리(뒤에서)'], ['개인정보 안내', '이름 · 연락처 · 주소 · 주민번호 · 계좌번호는 넣지 않음'], ['[상품 선택] · 약관 검색', '상품을 골라 두면 그 기준으로 답 · 약관 원문 찾기']], 18)}</div>
</div>`,
`[0:34] 신인에게 첫 1주는 '질문 예시 누르기'만 시키세요. 타이핑은 그다음.
예시 질문의 타사 비교는 공부용입니다.`,
'자료: MeAI 활용 가이드북 p.62 · 실제 MeAI 화면, 이름 가림');

add(hero(cap('real/r07_custom_info.png'), 1530, 963, 0, 963, 1000, 870, 200) + `
<div style="position:absolute;left:0;top:0;bottom:0;width:930px;background:linear-gradient(90deg,#000 82%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:140px;width:660px">
  <div class="kick y">맞춤대화 시작</div>
  <div class="h2" style="margin-top:20px;font-size:76px"><span class="r">‘보장분석 해줘’</span><br>한 마디로 시작</div>
  <div style="margin-top:40px">${list([['고객 정보 다섯 칸', '직업 · 병력 · 가족력 · 신규 제안 월 보험료 · 메모. 아는 것만 적어도 답이 달라짐'], ['선택 계약 총 보험료', '“지금 매달 이만큼 내고 계세요”로 시작'], ['첫 질문은 버튼 하나', '입력창 위 [보장분석 해줘] → 전체 그림부터'], ['지킬 것', '이름 · 연락처 · 주민번호 넣지 않음. 다른 사람의 건강정보는 이름 없이']], 18)}</div>
</div>`,
`[0:36] 동행 전에 신인에게 다섯 칸을 채우게 하면 상담 준비가 끝납니다.
아직 정보를 모른다면 [입력하지 않고 넘어가기]를 눌러도 괜찮습니다. 약관DB 점 색 · 담보 칩 9개 : 파랑이 아니면 답이 부정확할 수 있음.`,
'자료: MeAI 활용 가이드북 p.52 · p.65 · p.66 · 실제 MeAI 화면, 이름 가림');

add(`
<div class="spot" style="left:0;top:80px;width:1250px;height:1000px"></div>
<div class="scr" style="left:110px;top:150px;border-radius:20px">${crop(cap('hero/bc2_answer_top.png'), 1720, 1002, 0, 0, 1720, 1002, 820)}</div>
<div class="scr box" style="left:300px;top:560px;border-radius:20px">${crop(cap('hero/bc2_answer_bottom.png'), 1720, 1078, 0, 0, 1720, 560, 820)}</div>
<div class="box" style="position:absolute;left:1220px;top:150px;width:640px">
  <div class="kick y">맞춤대화 답 읽는 법</div>
  <div class="h2" style="margin-top:20px;font-size:68px">분석 → 제안 →<br><span class="r">다음 행동</span></div>
  <div style="margin-top:40px">${numList([['한 줄 결론', '오늘 상담 주제'], ['잘 갖춰진 것', '먼저 칭찬할 보장'], ['비어 있는 것', '표의 ‘미가입’ 줄이 제안 포인트'], ['이제 하면 되는 일', '다음 액션 한 줄']], 18)}</div>
</div>
<div class="box ps" style="position:absolute;left:1220px;top:900px;width:640px;font-size:24px"><span class="y">TIP</span> 가장 많이 쓰는 질문 <span class="w">“가입증권 별로 핵심만 표로 요약해줘”</span></div>`,
`[0:38] 상담 순서에 맞춘 답변 구성입니다.
더 자연스러운 말투를 원하면 "일반 분석", 분석 포인트를 짚고 싶으면 "상세 분석"을 쓰세요.`,
'자료: MeAI 활용 가이드북 p.53 · 금액은 예시');

add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:84px">“이거 뭐예요?”는<br><span class="y">노란 말</span> 한 번 누르면 끝</div></div>
<div class="box" style="position:absolute;left:1180px;top:130px;width:640px"><div class="p">용어 1,511개 · 쉬운 뜻 50자 · 9등급<br>동의어까지 5,000여 개<br><span class="w">PC는 입력창 오른쪽 위 [용어]</span></div></div>
<div class="spot" style="left:260px;top:360px;width:1400px;height:800px"></div>
<div class="scr box" style="left:310px;top:420px;border-radius:22px">${crop(cap('hero/fix_term_on.png'), 2340, 1158, 0, 0, 2340, 1000, 1300)}</div>
<div style="position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(0deg,#000 35%,rgba(0,0,0,0))"></div>`,
`[0:40] 어려운 말에 노란 표시 → 누르면 쉬운 뜻 → 다시 누르면 원래대로. 답 끝 [용어 설명 N]에서 목록으로 한 번에.
현장에서는 고객 눈높이 뜻풀이라 그대로 읽어 주면 됩니다. '이거 뭐예요?' 10번이 0번으로. 매니저는 "[용어] 켜서 읽어 보세요" 한 마디.
워밍업 Q2의 답입니다.`,
'자료: MeAI 용어사전(2026-10-29 전달본 1,511개) · MeAI 활용 가이드북 p.54');

const phone = (img, h, left, top) => `<div class="box" style="position:absolute;left:${left}px;top:${top}px;padding:12px;border-radius:52px;background:#1A1B1E;box-shadow:0 0 0 1px rgba(255,255,255,.12),0 40px 120px rgba(0,0,0,.8)"><div style="border-radius:42px;overflow:hidden">${crop(img, 1155, 2415, 0, 0, 1155, 2415, Math.round(h * 1155 / 2415))}</div></div>`;
add(`
<div class="spot" style="left:960px;top:20px;width:900px;height:1060px"></div>
${phone(cap('hero/term_mo_phone.png'), 800, 1010, 110)}
${phone(cap('hero/term_mo_phone_2.png'), 800, 1450, 110)}
<div class="box" style="position:absolute;left:140px;top:200px;width:820px">
  <div class="kick y">휴대폰으로도 똑같이</div>
  <div class="h2" style="margin-top:20px;font-size:80px">모바일은<br><span class="r">오른쪽 아래 [용어]</span></div>
  <div style="margin-top:44px">${list([['위치만 다름', 'PC는 입력창 오른쪽 위, 모바일은 오른쪽 아래'], ['켜고 끄기', '한 번 누르면 표시, 다시 누르면 원래대로'], ['점심 1분 퀴즈', '어제 답 속 용어 하나, “이거 고객 말로 하면?”']], 22)}</div>
</div>`,
`[0:41] 신인은 거의 휴대폰으로 씁니다. 휴대폰으로도 MeAI는 완벽하게 호환됩니다.`,
'자료: MeAI 활용 가이드북 p.55');

const wall = (file, txt, sub) => `
<div style="position:absolute;left:0;top:70px;width:1920px">${crop(asset(file), 1676, 670, 0, 0, 1676, 670, 1920)}</div>
<div style="position:absolute;inset:0;background:radial-gradient(ellipse 75% 70% at 50% 40%,rgba(0,0,0,0) 40%,rgba(0,0,0,.9) 100%),linear-gradient(0deg,#000 32%,rgba(0,0,0,.6) 52%,rgba(0,0,0,0) 72%)"></div>
<div class="box" style="position:absolute;left:140px;top:640px">
  <div class="h1" style="font-size:88px">${txt}</div>
  <div class="p" style="margin-top:22px">${sub}</div>
</div>`;
add(wall('wall_stats481.jpg', '이 그래프가 전부 MeAI 안에,<br>질병통계 그래프 <span class="r">481장</span>', '암 · 뇌 · 심장 · 치매 · 수술 · 장애까지. 신인이 외울 통계는 0개, <span class="w">물어볼 통계는 481장.</span>'),
`[0:42] 한 장씩 넘기지 말고 벽을 보여 주세요. "이게 다 MeAI 안에 있습니다" 한 마디.
환자 수 · 연령 · 성별 · 10년 추이까지.`,
'자료: 질병의료통계 2026 MeAI RAG판(2026-10-13) 481장 전부 · 국가암등록통계 · HIRA 재가공');

add(`
<div class="spot" style="left:60px;top:160px;width:1300px;height:900px"></div>
<div class="scr box" style="left:120px;top:300px;border-radius:22px">${crop(asset('fm_stats_example.jpg'), 868, 504, 0, 0, 868, 504, 1060)}</div>
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:80px"><span class="y">“OO 통계 보여줘”</span> 한 마디면<br>그래프가 옵니다</div></div>
<div class="box" style="position:absolute;left:1260px;top:330px;width:580px">${list([['어디서', '[지식 검색] 탭 예시, 또는 그냥 질문. 일반대화 · 맞춤대화 어디서나'], ['무엇이', '암 · 뇌 · 심장 · 치매 · 수술 481장. 환자 수 · 연령 · 성별 · 10년 추이'], ['신인에게', '그래프 하나 + 문장 하나'], ['매니저', '“그 통계 어디서 났어요?” → 출처 줄을 읽게 하기']], 26)}</div>`,
`[0:43] 통계를 외울 필요가 없습니다. 고객 앞에서 MeAI에 묻고 그래프를 보여 주면 됩니다.
예시 그래프 : "암환자 10명 중 7명은 5년 이상 생존합니다(5년 상대생존율 73.7%)".`,
'자료: MeAI 지식 검색 화면 · 질병의료통계 2026 MeAI RAG(2026-10-13) · 국가암등록통계 · HIRA 재가공');

add(wall('wall_medical223.jpg', '이 그림이 전부 MeAI 안에,<br>의학 그림 <span class="r">223장</span>', '절개 · 흡인 · 천자부터 내시경 · 복강경 · 피부이식까지. 신인이 그릴 그림은 0장, <span class="w">보여 줄 그림은 223장.</span>'),
`[0:44] 그림은 이미 MeAI에 들어가 있습니다. 폰으로 바로 시연해도 좋습니다.`,
'자료: 261023_Knowledge_Resources.pdf 223장 전부(의료기술 고객설명 그림, 2026-10-23) · MeAI 탑재 완료');

add(`
<div class="spot" style="left:60px;top:160px;width:1300px;height:900px"></div>
<div class="scr box" style="left:120px;top:300px;border-radius:22px">${crop(asset('fm_medical_example.jpg'), 868, 504, 0, 0, 868, 504, 1060)}</div>
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:80px"><span class="y">“전이암이 뭐예요?”</span>에<br>그림과 카드로 답합니다</div></div>
<div class="box" style="position:absolute;left:1260px;top:330px;width:580px">${list([['카드 한 장의 구성', '정의 · 언제 · 왜 · 어떻게 · 헷갈리는 용어 비교 · FAQ · 보험 상담 메모'], ['그림으로', '‘전이암이 뭐예요?’ 의학 그림 223장이 탑재'], ['신인에게', '답 끝 ‘보험 상담 메모’가 곧 상담 포인트'], ['매니저', '“그 치료가 우리 담보 어디에 걸려요?” 의학 → 약관 연결']], 26)}</div>`,
`[0:44] 의학 용어를 외우는 교육이 아니라, MeAI에 물어서 고객 말로 바꾸는 훈련입니다.`,
'자료: MeAI 의학지식 RAG(2026-10-29, 223주제) · 의료기술 고객설명 그림 223장(2026-10-23 전달)');

const SIX = [['5,000여 개', '용어 풀이', '쉬운 뜻 50자 · 동의어 · 9등급'], ['481장', '질병통계 그래프', '암 · 뇌 · 심장 · 치매 · 수술'], ['223주제', '의학 지식 카드', '정의 · 과정 · 비교 · FAQ + 그림'], ['19개', '2026 스타터 교재', '신인 케어링 교재 장별 PDF'], ['30종', '프롬프트 라이브러리', 'STEP 0~7, 잘 만든 질문'], ['2모드', '일반 · 상세 분석', '고객 앞에선 일반, 약관 따질 땐 상세']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:80px">‘그게 뭐예요?’의 답,<br>대부분 <span class="r">이미 안에</span> 있습니다</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:420px;display:grid;grid-template-columns:repeat(3,1fr);gap:50px 60px">
  ${SIX.map(([a, b, c]) => `<div><div class="y" style="font-size:96px;font-weight:900;letter-spacing:-0.045em;line-height:1">${a}</div><div style="font-size:32px;font-weight:800;margin-top:14px">${b}</div><div class="ps" style="margin-top:4px">${c}</div></div>`).join('')}
</div>`,
`[0:45] 신인이 묻는 '무엇'은 여기서 끝납니다. 매니저는 찾는 법만 가르치면 됩니다.`,
'자료: 09 MeAI 용어사전(2026-10-29 전달본 1,511개) · 07 질병통계 RAG(481장) · 18 의학지식 RAG(223주제 242장) · 28 2026 스타터 RAG(19개) · 프롬프트 라이브러리 30종');

add(`
<div class="spot" style="left:20px;top:120px;width:1200px;height:900px"></div>
<div class="scr box" style="left:120px;top:250px;border-radius:22px">${crop(cap('hero/mode_pc_bottom2_z.png'), 2340, 1650, 0, 290, 1500, 700, 1000)}</div>
<div class="box" style="position:absolute;left:1240px;top:180px;width:600px">
  <div class="kick">답 아래 꼬리질문 3개</div>
  <div class="y" style="font-size:230px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:20px">2.3<span style="font-size:130px">배</span></div>
  <div class="p" style="margin-top:20px">질문 3개 이상이면 평균 가계약 2.3배<br><span class="w">타이핑 없이 누르기만</span></div>
  <div class="ps" style="margin-top:26px"><span class="w">일반 분석</span> 고객 상담 · 용어를 일상 언어로<br><span class="w">상세 분석</span> 정밀 검토 · 지급 조건 · 약관 근거</div>
</div>
<div class="box h4" style="position:absolute;left:120px;top:830px;font-size:40px">오후 복기 때 매니저의 질문 : <span class="r">“꼬리질문 써 보셨어요?”</span></div>`,
`[0:46] 질문마다 일반 · 상세 선택, 다음 질문은 버튼으로. 고객 앞에서는 일반(간편) 분석, 약관을 따질 때는 상세 분석.`,
'자료: MeAI 활용 가이드북 p.56 · p.58 · 2026년 8월 TA채널 MeAI 사용 데이터 분석');

add(hero(cap('real/r02_prompt_lib_reco.png'), 1531, 963, 0, 963, 1000, 870, 200) + `
<div style="position:absolute;left:0;top:0;bottom:0;width:930px;background:linear-gradient(90deg,#000 82%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:160px;width:660px">
  <div class="kick y">MeAI 홈 → [일반대화] → [질문 더보기]</div>
  <div class="h2" style="margin-top:20px;font-size:80px">잘 만든 질문을<br><span class="r">골라 쓰기</span></div>
  <div style="margin-top:40px">${list([['탭 3개', '추천 · 최신 · 나의 질문(저장해 둔 질문)'], ['갈래 4개', '실전영업 · 상품지식 · 배경지식 · 업무지원. 처음이면 [실전영업]'], ['미리보기', '무엇을 묻는 질문인지 먼저 확인'], ['[이 질문 사용하기]', '그대로 MeAI에게 물음. 직접 쓸 필요 없음']], 18)}</div>
</div>`,
`[0:47] 신인이 '뭘 물어야 할지 모르겠어요' 할 때 보내는 곳입니다.
질문 속 판단(예: 전이암 분류)은 상품 · 약관마다 다릅니다 → 약관으로 확인.`,
'자료: MeAI 활용 가이드북 p.63 · 실제 MeAI 화면, 이름 가림');

add(hero(cap('real/r09_custom_precontract.png'), 1530, 963, 0, 963, 1000, 870, 200) + `
<div style="position:absolute;left:0;top:0;bottom:0;width:930px;background:linear-gradient(90deg,#000 82%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:150px;width:660px">
  <div class="kick y">보장분석 답 → “이 제안대로 가계약 제안서를 만들어줘”</div>
  <div class="h2" style="margin-top:20px;font-size:72px">설계안에서<br>가계약까지,<br><span class="r">[생성하기]</span> 한 번</div>
  <div style="margin-top:40px">${list([['가계약 제안서 표', '담보와 가입금액. 실제 가계약 생성 뒤 조건이 바뀔 수 있음'], ['고치고 싶으면', '목표 보험료 · 담보별 금액을 입력창에 쓰면 다시 만듦'], ['[생성하기]', '실제 가계약 생성. 최대 5분, 그동안 MeAI 사용 불가'], ['금액', '앞의 보완 제안과 다를 수 있음. 확정 금액처럼 말하지 않기']], 18)}</div>
</div>`,
`[0:48] 동행에서 돌아와 책상에서 바로 가계약까지. 신인 첫 달의 벽이 낮아집니다.
매니저 : 신인의 첫 가계약을 여기서 같이. 표 확인 → 고칠 것 요청 → 생성.`,
'자료: MeAI 활용 가이드북 p.68 · 실제 MeAI 화면, 이름 가림 · 담보 · 금액은 AI 제안 예시');

add(`
<div class="spot" style="left:960px;top:40px;width:960px;height:1040px"></div>
<div class="box" style="position:absolute;left:1060px;top:140px;padding:12px;border-radius:48px;background:#1A1B1E;box-shadow:0 0 0 1px rgba(255,255,255,.12),0 40px 120px rgba(0,0,0,.8)"><div style="border-radius:38px;overflow:hidden">${crop(cap('hero/bc2_report_step1.png'), 416, 846, 0, 0, 416, 846, 360)}</div></div>
<div style="position:absolute;left:1460px;top:470px;font-size:64px;color:#E60023;font-weight:900">→</div>
<div class="scr box" style="left:1540px;top:330px;border-radius:24px">${crop(cap('hero/gb5_kakao_clean.png'), 374, 334, 0, 0, 374, 334, 330)}</div>
<div class="box" style="position:absolute;left:140px;top:170px;width:860px">
  <div class="kick y">휴대폰 하나로 발송까지</div>
  <div class="h2" style="margin-top:20px;font-size:76px">요약 리포트,<br><span class="r">네 단계</span>로 고객 카톡까지</div>
  <div style="margin-top:44px">${numList([['요약 생성', '대화 화면 상단 [요약 생성]'], ['선택 → 편집하기', '넣을 답변만 체크, 내부용은 빼기'], ['리포트 생성하기', '카카오톡으로 링크 전송'], ['알림톡 도착', '[요약리포트 확인하기] · 7일간 열람']], 18)}</div>
  <div class="ps" style="margin-top:30px">PC는 PDF · Word 저장 · 보내기 전 숫자 · 약관 근거 · 개인정보 확인</div>
</div>`,
`[0:49] 매니저에게 리포트는 브리핑 종이입니다. 신인이 1클릭으로 뽑고, 매니저는 읽습니다.
'AI로 생성된 보조자료' 표시는 지우지 않습니다.`,
'자료: MeAI 활용 가이드북 p.59 · p.70 · 이름과 일부 글자는 가림');

add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="h1" style="font-size:84px">직접 물을 땐<br><span class="y">“누구에게</span> + <span class="r">무엇을”</span></div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:420px">
  <div class="kick g">전</div>
  <div class="k" style="font-size:44px;font-weight:700;margin-top:10px">“실손 설명해줘”</div>
  <div class="kick y" style="margin-top:40px">후</div>
  <div style="font-size:40px;font-weight:700;line-height:1.55;margin-top:10px;letter-spacing:-0.02em">“<span class="y">3세대 실손 가입한 50대 고객에게</span>, 4세대와 비교해서 자기부담과 비급여 한도의 차이를 <span class="g">표 1개로</span> 정리하고, 유지가 유리한 경우 3가지를 <span class="g">구어체로</span> 알려줘. <span style="color:#ff4d6a">자료에 없으면 추정하지 말고 ‘확인필요’로 표시해</span>”</div>
</div>
<div class="box p" style="position:absolute;left:140px;top:880px">신인 질문을 고쳐 주는 법 : <span class="w">앞에 ‘누구에게’만 붙이게 하세요.</span> 휴대폰은 마이크로 말해도 됩니다.</div>`,
`[0:49] 한 줄만 바꿔도 답변의 수준이 달라집니다. 누구에게 · 무엇을 · 형식 추가(표로 · 구어체로 · 카톡 6줄로) · 안전장치 한 마디.
안 맞으면 "더 쉽게" · "표로 다시" 한 마디.`,
'자료: MeAI 활용 가이드북 p.80');

// ───────────── PART 4 2026 스타터 (0:50~0:58)
add(sec('04', '스타터', '2026 스타터가 MeAI 안에', '신인 케어링 교재가 MeAI 안에 들어갔습니다. 교육 · 훈련도 MeAI가 받아 줍니다.'), `[0:50] PART 4.`);

const CH = ['신인교육과정 안내', '보험 기초 용어', '5대 보장자산', '상품 라인업', '태아·어린이보험', '운전자·상해·바이크', '주택·일반화재', '치아보험', '자동차보험', '암 보장', '뇌·심장혈관질환', '수술비', '입원일당·간병', '실손의료비', '후유장해·사망·배상책임', '생명보험 증권 컨설팅', '알릴의무·완전판매·보험사기', '지표관리·리스크관리', '영업활동·전산·보장분석·MeAI'];
add(`
<div class="box" style="position:absolute;left:140px;top:270px;width:820px">
  <div class="kick y">2026년 11월 기준 메리츠 스타터</div>
  <div style="font-size:250px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:24px">608<span style="font-size:130px">쪽</span></div>
  <div class="h4" style="margin-top:34px;font-weight:600">18챕터 · 신인 교재 19개가<br>장별로 MeAI에 들어 있습니다</div>
  <div class="h4" style="margin-top:44px;font-size:46px"><span class="r">교육은 MeAI가, 확인은 매니저가.</span></div>
</div>
<div class="box" style="position:absolute;left:1040px;top:250px;width:800px;display:grid;grid-template-columns:1fr 1fr;gap:24px 40px">
  ${CH.map((c, i) => `<div style="font-size:27px;font-weight:600;color:#8E9095;white-space:nowrap;letter-spacing:-0.02em"><span style="color:#E60023;font-weight:800;margin-right:10px">${String(i).padStart(2, '0')}</span>${c}</div>`).join('')}
</div>`,
`[0:51] 신인 케어링 교안을 2026년 11월 상품 기준으로 재구성 · 또또암 등 바뀐 담보 이름 반영 · 수수료 자료 제외.
4:3 PPT + PDF, 걱정인형 캐릭터, 장마다 MeAI 실습. 01~17장 끝마다 'MeAI로 이어서 공부해요' 실습 장.`,
'자료: 28_MeAI_신인교육_RAG_2026스타터 (2026-11-04)');

const TR = [['의학용어 훈련', '하루 용어 3개. 답 속 노란 말을 [용어]로 열고, 고객 말로 바꿔 말해 보기', '“전이암을 고객에게 한 문장으로” → 의학 지식 카드의 ‘보험 상담 메모’까지'], ['약관 읽기 훈련', '약관 검색으로 조문을 찾고, 상세 분석으로 근거 줄 확인. 숫자는 약관으로 되묻기', '“이 특약 지급 조건을 약관 근거와 함께” → 답 끝 근거 한 줄 읽기'], ['나만의 단어사전', '이번 주 물었던 용어 10개를 신인 노트에. 쉬운 뜻은 MeAI 풀이 그대로, 내 말 한 줄 추가', '금요일 리플레이에서 3개 발표. 12차월이면 신인 사전 한 권'], ['통계 한 장 화법', '지식 검색으로 그래프 1장 → 문장 1개. 출처 줄까지 읽기', '“암 생존율 통계 보여줘” → “암환자 10명 중 7명은 5년 이상 생존합니다”']];
add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="kick y">MeAI가 보조하는 신인 훈련</div><div class="h1" style="font-size:76px;margin-top:14px">네 가지 훈련을 <span class="r">MeAI가 받아</span> 줍니다</div></div>
<div class="box" style="position:absolute;left:120px;right:120px;top:350px;display:grid;grid-template-columns:repeat(4,1fr);gap:46px">
  ${TR.map(([a, b, c], i) => `<div style="border-top:3px solid ${i % 2 ? '#3A3B3F' : '#E60023'};padding-top:26px"><div style="font-size:26px;font-weight:900;color:#E60023">${i + 1}</div><div style="font-size:40px;font-weight:900;margin-top:8px;letter-spacing:-0.03em">${a}</div><div class="ps" style="margin-top:18px">${b}</div><div style="font-size:23px;font-weight:700;color:#FFD43B;margin-top:22px;line-height:1.55">${c}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:880px;text-align:center;font-size:34px">넷 다 <span class="y">‘신인이 MeAI에 물어서 자기 말로 바꾸는’</span> 훈련입니다.</div>`,
`[0:53] 매니저는 메뉴만 정해 주고, 훈련은 신인 폰에서. 확인은 금요일 리플레이에서.`,
'자료: MeAI 용어사전 1,511개 · 의학지식 RAG 223주제 · 질병통계 RAG 481장 · 약관 검색(가이드북 p.62) · 훈련 메뉴는 제안');

const WK = [['월', '의학용어 3개', '[용어] 켜고 어제 답 속 노란 말 3개 → 고객 말로', '단어사전 3줄'], ['화', '약관 한 조문', '약관 검색 → 조문 → 상세 분석으로 근거 줄', '근거 한 줄 캡처'], ['수', '통계 한 장', '지식 검색 ‘OO 통계 보여줘’ → 그래프 1 + 문장 1', '그래프 캡처 + 문장'], ['목', '테스트 질문 1문', '테스트 질문 99 중 하나를 본인 폰으로 묻고 답 확인', 'O / △ / X 한 글자'], ['금', '리플레이 15분', '한 주 리포트 2~3개 + 단어사전 10개 중 3개 발표', '다음 주 한 가지']];
add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="h1" style="font-size:84px">하루 <span class="r">10분</span>, 월~금 다섯 메뉴</div><div class="p" style="margin-top:12px">신인 폰의 MeAI로. 매니저는 금요일에 한 번만 봅니다. (제안)</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:330px">
  ${WK.map(([d, a, b, c]) => `<div class="row" style="padding:24px 0;border-top:1px solid #222326">
    <div style="width:110px;font-size:56px;font-weight:900;color:${d === '금' ? '#FFD43B' : '#E60023'}">${d}</div>
    <div style="width:340px;font-size:34px;font-weight:800">${a}</div>
    <div style="flex:1;font-size:26px;font-weight:500;color:#C9CACD;padding-right:30px">${b}</div>
    <div style="width:300px;font-size:26px;font-weight:700;color:#FFD43B">${c}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:140px;top:930px;font-size:26px">훈련표는 출력해 단어사전 노트 첫 장에. <span class="w">12차월이면 노트가 신인 사전이 됩니다.</span></div>`,
`[0:54] 요일 · 분은 제안값입니다. 지점 조회 시간에 맞게 바꾸세요.`,
'자료: 세일즈혁신TF 제안 · 테스트 질문 99 (261104_MeAI_신인교육RAG_테스트질문세트.xlsx)');

const MAP = [['1~3차월', '기초', '신인 케어링 교육', '질문 예시 누르기 · [용어] 켜기 · 추천 카드 읽기'], ['4~6차월', '상품', '실전 상품 상담', '프롬프트 라이브러리 [실전영업] · 맞춤대화 ‘보장분석 해줘’ · 꼬리질문 3개'], ['7~9차월', '컨설팅', '설계와 제안', '상세 분석 모드 · 가계약 제안서 · 요약 리포트 발송'], ['10~12차월', '자립', '스스로 루틴', '그룹 루틴(상령일 · 생일 · 사전동의 만료) · 나의 질문 저장']];
add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="kick y">12차월 성장 지도 (제안)</div><div class="h1" style="font-size:76px;margin-top:14px">차월마다 <span class="r">MeAI에서 할 것 하나</span></div></div>
<div style="position:absolute;left:180px;right:180px;top:478px;height:3px;background:linear-gradient(90deg,#3A3B3F,#FFD43B);box-shadow:0 0 20px rgba(255,212,59,.4)"></div>
<div class="box" style="position:absolute;left:120px;right:120px;top:456px;display:grid;grid-template-columns:repeat(4,1fr)">
  ${MAP.map(([a, b, c, d], i) => `<div style="text-align:center;padding:0 24px">
    <div style="width:48px;height:48px;border-radius:50%;margin:0 auto;background:${i === 3 ? '#FFD43B' : '#fff'};box-shadow:0 0 0 8px #000,0 0 26px rgba(255,255,255,.35)"></div>
    <div style="font-size:30px;font-weight:800;color:#FFD43B;margin-top:26px">${a}</div>
    <div style="font-size:64px;font-weight:900;margin-top:6px;letter-spacing:-0.03em">${b}</div>
    <div class="ps" style="margin-top:8px">${c}</div>
    <div style="font-size:24px;font-weight:600;color:#D8D9DC;margin-top:18px;line-height:1.55">${d}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:900px;text-align:center;font-size:34px">매니저님은 차월마다 ‘이번 달 MeAI에서 할 것 하나’만 정해 주면 됩니다.</div>`,
`[0:56] 차월에 맞춰 스타터 장과 MeAI 기능을 짝지으면 코칭 계획이 됩니다. 차월 구분과 짝은 제안값, 지점 사정에 맞게 바꾸세요.`);

// ───────────── PART 5 하루 30분 (0:58~1:10)
add(sec('05', '30분', '매니저님의 하루, 30분의 코칭시간', '조회 5분 · 방문 전 10분 · 점심 후 1분 · 복기 10분 · 마감 5분. 금요일 15분.'), `[0:58] PART 5. 오늘의 핵심.`);

add(`<div class="ctr"><div class="box">
  <div style="font-size:130px;font-weight:900;letter-spacing:-0.045em;line-height:1.2">답을 주지 마세요.</div>
  <div class="h2 y" style="margin-top:50px">“찾아서 가져오세요. 그때 이야기해요.”</div>
  <div class="p" style="margin-top:50px">이 한 문장이 매니저의 코칭입니다.<br>신인은 시키면 안 쓰고, <span class="w">보여 주면 씁니다.</span></div>
</div></div>`,
`[0:58] FMBTI 네 유형의 공통 처방이었습니다.`);

const TL = [['09:30', '조회 5분', '“동의 필요 몇 명? 오늘 카드는 누구?” 답 대신 ‘찾아보세요’', '카드 읽고 첫 말 준비'], ['11:00', '방문 전 10분', '신인이 뽑은 요약 리포트에 빨간 펜 3줄', '요약 리포트 1클릭'], ['13:00', '점심 후 1분', '추천 프롬프트 하나 단톡에, 또는 어제 답 속 용어 하나', '본인 폰으로 답'], ['15:00', '거절 복기 10분', '꼬리질문 3개까지 갔는지, 거절 사유는 어디인지', '꼬리질문 3개까지'], ['18:00', '마감 5분', '리포트 발송 수 · 동의 요청 수 · 코칭 인원 확인', '숫자 셋 적기'], ['금요일', '리플레이 15분', '한 주 리포트 모아 신인이 자기 대화를 설명하게, 질문 6개', '자기 대화 설명']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="h1">하루 <span class="r">30분</span>, 그리고 금요일 15분</div><div class="p" style="margin-top:12px">시간은 예시입니다. 지점 조회 시간에 맞게 바꾸세요.</div></div>
<div style="position:absolute;left:150px;right:150px;top:432px;height:3px;background:linear-gradient(90deg,#3A3B3F,#E60023 50%,#3A3B3F);box-shadow:0 0 24px rgba(230,0,35,.6)"></div>
<div class="box" style="position:absolute;left:80px;right:80px;top:410px;display:grid;grid-template-columns:repeat(6,1fr)">
  ${TL.map(([t, a, b, c], i) => `<div style="padding:0 18px;text-align:center">
    <div style="width:46px;height:46px;border-radius:50%;margin:0 auto;background:${i === 5 ? '#FFD43B' : '#fff'};box-shadow:0 0 0 8px #000,0 0 30px rgba(255,255,255,.4)"></div>
    <div style="font-size:34px;font-weight:800;color:#FFD43B;margin-top:26px">${t}</div>
    <div style="font-size:32px;font-weight:800;margin-top:6px">${a}</div>
    <div class="ps" style="margin-top:14px;font-size:22px;color:#C9CACD;min-height:102px">${b}</div>
    <div style="font-size:20px;font-weight:600;color:#6E7076;margin-top:12px">신인 · ${c}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:880px;text-align:center;font-size:36px">처음에는 코칭할 신인을 <span class="y">‘오늘 3명’</span>으로 시작해 보세요.</div>`,
`[0:59] MeAI와 함께하는 하루 30분, 그리고 금요일 15분. 매니저님 하루에 맞게 활용해 보세요.`);

const CHAT = [['매니저', '동의 필요 몇 명이에요? 오늘 추천 고객, 누구한테 연락해 볼 거예요?'], ['신인', '서은아 고객이요. 보상 완료 후 후속 상담이 없었대요.'], ['매니저', '그 카드 문장 한번 확인해 보세요. MeAI에 뭘 물어볼 것 있어요?'], ['신인', '오른쪽 추천 질문이요. 입원일당 부족 고객에게 보낼 문자 문안이요.'], ['매니저', '좋아요. MeAI에 넣어 보고, 요약 리포트 한번 뽑아서 봅시다.']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="kick y">09:30 조회 대본</div><div class="h1" style="margin-top:14px;font-size:84px">세 마디면 <span class="r">5분</span></div></div>
<div class="box" style="position:absolute;left:180px;right:180px;top:290px;display:flex;flex-direction:column;gap:18px">
  ${CHAT.map(([w, t]) => w === '매니저'
    ? `<div class="row" style="gap:24px"><div style="width:110px;font-size:26px;font-weight:800;color:#E60023;flex:none">매니저</div><div class="bub" style="background:#fff;color:#111">${t}</div></div>`
    : `<div class="row" style="gap:24px;justify-content:flex-end"><div class="bub" style="background:#1E1F22;color:#C9CACD">${t}</div><div style="width:90px;font-size:26px;font-weight:800;color:#6E7076;flex:none;text-align:right">신인</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:910px;text-align:center;font-size:34px">매니저는 <span class="y">“눌러 보세요”</span>로 끝내고, 신인은 매니저가 쓰는 걸 보고 따라 씁니다.</div>`,
`[1:00] 답을 주지 않고 '찾아보세요'로 끝냅니다. 이름은 가이드북 예시.
조회에서 매니저가 확인하는 셋 : 동의 필요 수(홈 숫자 4개 중 하나) · 오늘 카드(9장 중 누구, 왜) · 근거 한 줄(답이 아니라 출처).
흐름 : 홈 열기 → 추천 카드 3장 읽기 → 고객찾기에서 열기 → 맞춤대화 · 리포트(가이드북 p.72). 시키면 안 쓰고, 보여 주면 씁니다.`,
'자료: MeAI 활용 가이드북 p.72 · 이름은 가이드북 예시');

add(`
<div class="spot" style="left:20px;top:100px;width:1100px;height:1000px"></div>
<div class="scr box" style="left:110px;top:220px;border-radius:22px">${crop(cap('hero/bc2_answer_top.png'), 1720, 1002, 0, 0, 1720, 1002, 980)}</div>
<svg style="position:absolute;left:121px;top:231px" width="980" height="593" viewBox="0 0 860 520">
  <path d="M60 155 C 260 148, 480 160, 700 150" stroke="#E60023" stroke-width="9" fill="none" stroke-linecap="round" opacity=".92"/>
  <path d="M40 300 C 120 286, 160 330, 70 336" stroke="#E60023" stroke-width="8" fill="none" stroke-linecap="round" opacity=".92"/>
  <path d="M60 470 C 280 462, 520 476, 760 464" stroke="#E60023" stroke-width="9" fill="none" stroke-linecap="round" opacity=".92"/>
</svg>
<div class="box" style="position:absolute;left:1180px;top:150px;width:680px">
  <div class="kick y">11:00 방문 전 10분</div>
  <div class="h2" style="margin-top:18px;font-size:68px">요약 리포트에<br><span class="r">빨간 펜 3줄</span></div>
  <div style="margin-top:40px;display:flex;flex-direction:column;gap:26px">
    ${[['① 순서', '잘 갖춘 것 먼저, 비어 있는 것 두 번째. 해지 얘기는 맨 뒤'], ['② 빠진 것', '리포트에 없는 것 하나. 가족력 · 직업 · 최근 보상. 다섯 칸을 채웠는지'], ['③ 하지 말 것', '‘타사보다 유리’ 같은 비교 문장, 확정 금액처럼 말하기, 약관 확인 안 한 숫자']].map(([a, b]) => `<div><div style="font-size:36px;font-weight:800">${a}</div><div class="ps" style="margin-top:4px">${b}</div></div>`).join('')}
  </div>
  <div class="h4 y" style="margin-top:36px;font-size:32px">코칭의 핵심은 매니저님의 ‘Why’입니다.</div>
</div>`,
`[1:01] 신인이 원 클릭으로 뽑고, 매니저는 읽기만.
동행 전 특약이 헷갈리면 : 특약검색기에서 특약 코드로 지급 조건 확인. MeAI 상세 분석으로 약관 근거까지.
리포트 보내기 전 : AI 요약에 계약별 유지 · 해지 의견이 들어갈 수 있음 → 구성 요소에서 AI 요약 끄기.`,
'자료: MeAI 활용 가이드북 p.59~70 · 화면은 가이드북 예시');

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="h1" style="font-size:84px">오후 셋은 전부 <span class="r">한 줄</span></div><div class="p" style="margin-top:12px">문제를 만들지 않고, 사유를 분류하고, 한 줄만 남깁니다. 길어지면 안 합니다.</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:380px;display:grid;grid-template-columns:repeat(3,1fr);gap:70px">
  ${[['13:00', '점심 후 1분 퀴즈', '이번 달 영업과 관련한 문제를 단톡에. 신인은 본인 폰 MeAI로 오픈북 가능', '예 : 11월에 영업거리는 뭐가 있을까요?'], ['15:00', '거절 복기 10분', '‘생각해 볼게요’ 뒤에 뭘 했는지. 꼬리질문 3개까지 갔는지. [실전영업] 거절처리 질문으로 다음 멘트 3개', '첫 말 / 니즈 환기 / 설명 / 금액 / 마감 중 어디'], ['18:00', '마감 5분', '숫자 셋 : 리포트 발송 수 · 동의 요청 수 · 맞춤대화 수. 내일 아침 추천 9명은 홈이 다시 계산', '신인이 적고 매니저는 읽기만']].map(([t, a, b, c]) => `<div><div class="y" style="font-size:96px;font-weight:900;letter-spacing:-0.04em;line-height:1">${t}</div><div style="font-size:40px;font-weight:800;margin-top:20px">${a}</div><div class="ps" style="margin-top:16px">${b}</div><div style="font-size:22px;font-weight:700;color:#ff4d6a;margin-top:16px">${c}</div></div>`).join('')}
</div>`,
`[1:03] 점심 1분 · 거절 복기 10분 · 마감 5분.`);

const Q6 = ['이번 주 가장 잘된 터치는? 왜요?', '그때 MeAI에 뭘 먼저 물어봤어요?', '고객이 멈칫한 순간은 어디였어요?', '다시 한다면 뭘 바꿔 볼래요?', 'MeAI 답 중 안 믿은 건 뭐예요? 왜요?', '다음 주 한 가지만 고른다면요?'];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="kick y">금요일 리플레이 15분</div><div class="h1" style="margin-top:16px;font-size:80px">신인이 <span class="r">자기 대화</span>를 설명하게</div></div>
<div class="box" style="position:absolute;left:170px;right:170px;top:400px;display:grid;grid-template-columns:1fr 1fr;gap:44px 80px">
  ${Q6.map((q, i) => `<div class="row" style="gap:28px"><div style="font-size:40px;font-weight:900;color:${i === 4 ? '#FFD43B' : '#E60023'};width:70px;flex:none">Q${i + 1}</div><div style="font-size:40px;font-weight:700;letter-spacing:-0.025em">${i === 4 ? `<span class="r">${q}</span>` : q}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:96px;right:96px;top:860px;text-align:center">매니저가 가르치는 시간이 아니라 신인이 자기 생각을 말하는 15분. <span class="w">Q5를 말할 수 있으면 검증 습관이 생긴 겁니다.</span></div>`,
`[1:05] 고능률자의 영업 흐름을 그대로 FM님의 코칭에 녹였습니다. 한 주 리포트를 모아, 신인이 자기 대화를 설명하게.`);

const RX = [['“이번 달 뭐부터 팔아요?”', '홈 [당월 영업 타겟] 그룹 + 추천 카드 9장', '“담당 고객 중 당월 타겟 그룹이 누구예요? 거기부터 해 보세요.”'], ['“질문을 어떻게 써야 할지 모르겠어요”', '질문 예시 탭 → 프롬프트 라이브러리 [실전영업]', '“쓴 질문 앞에 ‘누구에게’만 붙여 보세요.”'], ['“증권 봐도 뭐가 부족한지 몰라요”', '맞춤대화 ‘보장분석 해줘’ → 표의 ‘미가입’ 줄', '“미가입 줄 1개만 오늘 이야기해 보세요.”'], ['“고객이 보험료 부담돼서 정리하재요”', '고객 정보 ‘신규 제안 월 보험료’ 채우고 보장분석', '“해지 얘기는 맨 뒤예요. 지킬 걸 먼저 보여 드리세요.”'], ['“병 있는 고객인데 가입 돼요?”', '상품 라인업 ‘예외질환 판정’ → MeAI 상세 분석', '“판정 결과 캡처해서 오세요. 확정은 심사예요.”'], ['“생각해 본대요”', '꼬리질문 버튼 → 거절처리 프롬프트로 문안 3개', '“문안 3개 중 제가 하나 골라 드릴게요.”']];
add(`
<div class="box" style="position:absolute;left:140px;top:84px"><div class="kick y">책상에 붙이는 한 장</div><div class="h1" style="margin-top:12px;font-size:76px">신인 증상별 <span class="r">MeAI 처방전</span></div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:300px">
  <div class="row" style="padding-bottom:12px"><div style="width:520px" class="ps">신인 고민</div><div style="width:560px" class="ps">스스로 (MeAI에 시킬 것)</div><div class="ps y" style="flex:1">FM님 피드백</div></div>
  ${RX.map(([a, b, c]) => `<div class="row" style="padding:19px 0;border-top:1px solid #222326">
    <div style="width:520px;font-size:27px;font-weight:800;padding-right:24px">${a}</div>
    <div style="width:560px;font-size:24px;font-weight:500;color:#C9CACD;padding-right:24px">${b}</div>
    <div style="flex:1;font-size:25px;font-weight:700;color:#FFD43B">${c}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:140px;top:930px;font-size:26px">고민 → 스스로 → FM님 피드백. <span class="w">신인 책상에 출력해서 붙여 두세요.</span></div>`,
`[1:06] 11월 처방전처럼, 신인에게도 처방전이 있습니다.`);

const D5 = [['MeAI 홈 열기', '숫자 4개와 추천 카드 3장 읽기', '일반대화 질문 예시 하나 눌러 보기'], ['카드에서 고객찾기', '[MeAI 고객찾기에서 열기] → 한눈에 보기 6칸', '추천 질문 눌러 보기'], ['맞춤대화 시작', '“보장분석 해줘” → 꼬리질문 2번', '부족 보장 3개 메모'], ['그룹으로 찾기', '[사전동의 만료] 그룹 확인', 'D-n 짧은 1명께 재동의 부탁'], ['리포트 보내기', '요약 리포트 발송', '좋았던 질문을 ‘나의 질문’에 저장']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="h1">첫 5일, <span class="r">하루 하나씩</span></div><div class="p" style="margin-top:14px">가이드북의 첫 5일 미션 그대로. FM님은 체크만 합니다.</div></div>
<div class="box" style="position:absolute;left:110px;right:110px;top:400px;display:grid;grid-template-columns:repeat(5,1fr)">
  ${D5.map(([t, a, b], i) => `<div style="padding:0 30px;${i ? 'border-left:1px solid #26272b' : ''}">
    <div style="font-size:26px;font-weight:800;color:${i === 0 ? '#FFD43B' : '#E60023'};letter-spacing:0.06em">DAY ${i + 1}</div>
    <div style="font-size:40px;font-weight:800;margin-top:16px;line-height:1.3;letter-spacing:-0.025em">${t}</div>
    <div class="ps" style="margin-top:28px;color:#D0D1D4">☐ ${a}</div>
    <div class="ps" style="margin-top:12px;color:#D0D1D4">☐ ${b}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:850px;text-align:center;font-size:36px">찾아가는 영업으로, <span class="y">“MeAI 홈에서 영업을 시작”</span></div>`,
`[1:08] 신인에게 주는 미션. 출력해서 책상에 붙여 주세요.`,
'자료: MeAI 활용 가이드북 첫 5일 미션');

const SC = [['자동차보험 만기 9일 전', '카드 읽기 → 고객찾기 6칸 → ‘보장분석 해줘’ 운전자 보장 빈 곳 → 리포트 카카오톡', '“만기가 9일 뒤예요. 갱신 안내 드리면서 운전자 보장도 같이 봐 드릴게요.”', '“자동차보험만 있고 운전자보험이 없는 고객에게 운전자 보장이 필요한 이유를 쉽게 설명해줘”'], ['동의 만료 전 재동의', '가입설계동의가 이달 말 만료 → 연장 부탁 + 보장 점검 약속 → 신담보 기준 빈 곳 → 점검 결과 발송', '“이달 말 동의가 만료돼 연장 부탁드려요. 새로 나온 보장도 봐 드릴게요.”', '“최근 신담보 기준으로 이 고객 보장의 빈 곳을 알려줘”'], ['AI 추천 고객, 상령일 2주 전', '암진단비 1천만원뿐 · 동의 필요 → 알림톡 → 15분 뒤 ‘보장분석 해줘’ → 인상 전 가입 이점 리포트', '“2주 뒤 보험 나이가 올라가요. 그 전에 점검하려고 동의 알림톡 보내요.”', '“상령일 전에 암진단비를 늘려야 하는 이유를 쉽게 설명해줘”']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="kick y">가이드북 시나리오 1~3</div><div class="h1" style="margin-top:12px;font-size:76px">카드 한 장이 <span class="r">계약까지</span> 가는 길</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:330px;display:grid;grid-template-columns:repeat(3,1fr);gap:60px">
  ${SC.map(([a, b, c, d]) => `<div style="border-top:3px solid #E60023;padding-top:26px"><div style="font-size:38px;font-weight:900;letter-spacing:-0.03em">${a}</div><div class="ps" style="margin-top:14px;font-size:22px">${b}</div><div class="kick y" style="margin-top:26px;font-size:20px">첫 말 → 고객에게</div><div style="font-size:28px;font-weight:700;margin-top:8px;line-height:1.5">${c}</div><div class="kick g" style="margin-top:22px;font-size:20px">MeAI에게 첫 질문</div><div class="ps" style="margin-top:6px;font-size:22px">${d}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:920px;text-align:center;font-size:32px">셋 다 <span class="y">‘카드 읽기 → 동의 / 고객찾기 → 맞춤대화 → 리포트’</span> 네 칸입니다.</div>`,
`[1:09] 이름과 숫자는 예시입니다.`,
'자료: MeAI 활용 가이드북 p.73~75 · 이름과 숫자는 예시');

// ───────────── PART 6 도구 6종 (1:10~1:20)
add(sec('06', '도구', '도구 6종으로 손을 덜기', 'MeAI와 짝으로 활용하는 영업지원도구. 사실 확인은 도구, 말로 바꾸는 건 MeAI.'), `[1:10] PART 6.`);

add(`
<div class="spot" style="left:860px;top:60px;width:1200px;height:1000px"></div>
<div style="position:absolute;left:940px;top:150px;width:900px;perspective:2400px">
  <div class="scr" style="position:relative;transform:rotateY(-10deg) rotateX(3deg);transform-origin:left center">${crop(tcap('index'), 2880, 1800, 0, 0, 2880, 1800, 900)}</div>
</div>
<div style="position:absolute;left:0;top:0;bottom:0;width:980px;background:linear-gradient(90deg,#000 76%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:160px;width:820px">
  <div class="kick y">대문 하나에 여섯 개, 캐릭터 6명이 안내</div>
  <div class="h1" style="margin-top:20px;font-size:88px">무기는 이미<br><span class="r">FM님 손</span>에 있습니다</div>
  <div style="margin-top:44px;display:grid;grid-template-columns:1fr 1fr;gap:18px 30px">
    ${[['특약검색기', '보장 내용 · 지급 조건 한 화면'], ['보상시뮬레이터', '질병만 누르면 보상 특약 안내'], ['상품 라인업', '가입 조건 + 예외질환 판정 50종'], ['프롬프트 30종', 'STEP 0~7, MeAI에 붙여 넣기'], ['명패 제작기', '이름 · 소속만 넣으면 인쇄 파일'], ['통합치료비 시뮬', '12종을 질병 선택만으로 비교']].map(([a, b]) => `<div><div style="font-size:32px;font-weight:800">${a}</div><div class="ps" style="font-size:22px">${b}</div></div>`).join('')}
  </div>
  <div class="ps" style="margin-top:34px;font-size:24px">여섯 개를 다 외울 필요 없습니다. <span class="w">특약검색기와 통합치료비 시뮬 둘만 먼저.</span><br><span class="y" style="white-space:nowrap">hunx11-sys.github.io/MeAI</span></div>
</div>`,
`[1:11] 대문 하나에 여섯 개. 압축 파일은 단톡으로 공유합니다.`,
'자료: 영업지원도구 6종 사용법 (2026-09-16) · 대문 화면');

add(hero(tcap('tool_search'), 2880, 1800, 0, 1800, 1000, 870, 200) + `
<div style="position:absolute;left:0;top:0;bottom:0;width:930px;background:linear-gradient(90deg,#000 82%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:180px;width:660px">
  <div class="kick y">특약검색기 · 워밍업 Q1의 답</div>
  <div class="h2" style="margin-top:20px;font-size:84px">“약관 찾아봐”<br>대신 <span class="r">“코드 쳐 봐”</span></div>
  <div style="margin-top:44px">${list([['검색', '특약 이름 · 코드 · 키워드'], ['위쪽 버튼 4개', '표적항암 종류 · 수술비 비교 · 상급종합 지도 · 상품 히스토리'], ['방문 전', '헷갈리는 특약을 신인이 직접 찾게. 지급금액 표 캡처해서 오기']], 22)}</div>
</div>`,
`[1:13] 약관을 찾아볼 필요 없이 손쉽게. 사실 확인은 도구, 말로 바꾸는 건 MeAI.`,
'자료: 영업지원도구 특약검색기 ver2613 화면');

add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="kick y">특약검색기 위쪽 버튼</div><div class="h1" style="margin-top:12px;font-size:76px">병원 등급 · 옛 상품명, <span class="r">버튼 하나</span></div></div>
<div class="spot" style="left:40px;top:300px;width:1000px;height:760px"></div>
<div class="scr box" style="left:120px;top:300px;border-radius:20px">${crop(tcap('tool_map'), 2880, 1800, 261, 45, 2358, 1300, 820)}</div>
<div class="spot" style="left:900px;top:300px;width:1000px;height:760px"></div>
<div class="scr box" style="left:1000px;top:300px;border-radius:20px">${crop(tcap('tool_history'), 2880, 1800, 681, 45, 1518, 1300, 560)}</div>
<div class="box" style="position:absolute;left:120px;top:780px;width:820px"><div style="font-size:32px;font-weight:800">상급종합 지도</div><div class="ps" style="margin-top:6px">제5기 상급종합병원 47 · 암중점치료기관 16 · 권역심뇌혈관 15 · 권역외상 17</div><div style="font-size:24px;font-weight:700;color:#FFD43B;margin-top:10px">“그 병원이 상급종합이에요? 지도에서 확인해 보세요”</div></div>
<div class="box" style="position:absolute;left:1000px;top:780px;width:820px"><div style="font-size:32px;font-weight:800">상품 히스토리</div><div class="ps" style="margin-top:6px">출시 · 개정 · 판매중단을 월별로, 동의어를 누르면 특약 검색까지</div><div style="font-size:24px;font-weight:700;color:#FFD43B;margin-top:10px">“그 담보 언제 바뀐 거예요? 히스토리에서 찾아보세요”</div></div>`,
`[1:14] 지급 조건의 '병원 등급'을 신인이 추정하지 않게 합니다. 옛 이름으로 묻는 고객, 새 이름으로 답하는 신인, 그 사이를 히스토리가 메웁니다.
예 : '스타터 교재에 있던 그 담보, 지금 이름이 뭐예요?'(테스트 질문 99의 '최신화' 유형).`,
'자료: 영업지원도구 특약검색기 ver2613 · 상급종합 지도 · 상품 히스토리(2026.10.31 기준)');

add(hero(tcap('tool_sim'), 2880, 1800, 0, 1800, 1000, 870, 200) + `
<div style="position:absolute;left:0;top:0;bottom:0;width:930px;background:linear-gradient(90deg,#000 82%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:180px;width:660px">
  <div class="kick y">보상시뮬레이터 · 특약검색기 둘째 탭</div>
  <div class="h2" style="margin-top:20px;font-size:76px">“이 병이면<br>어떤 특약에서<br><span class="r">나와요?”</span></div>
  <div style="margin-top:40px">${list([['어떻게', '질병명 · KCD코드 · 초성으로 검색, 또는 자주 찾는 질병 칩'], ['꼭 붙이는 말', '실제 지급 여부 · 한도 · 금액은 약관상 지급사유와 인수심사, 실제 가입내역에 따라 최종 결정']], 22)}</div>
</div>`,
`[1:16] 청구 설명 콤보의 첫 칸. 시뮬레이터로 특약을 찾고, 특약검색기로 조건을 보고, MeAI로 말을 만듭니다.
신인에게 : 동행 전 고객 병력 한 줄 → 시뮬레이터 → 해당 특약 → 특약검색기로 조건 확인 → MeAI로 고객 말.`,
'자료: 영업지원도구 보상시뮬레이터 ver2609 · 화면 안내문 원문');

add(hero(tcap('itc'), 2880, 1800, 0, 1800, 1000, 870, 200) + `
<div style="position:absolute;left:0;top:0;bottom:0;width:930px;background:linear-gradient(90deg,#000 82%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:200px;width:660px">
  <div class="kick y">통합치료비 시뮬레이션</div>
  <div class="h2" style="margin-top:20px;font-size:80px">12종 통합치료비,<br><span class="r">질병 선택</span>만으로</div>
  <div style="margin-top:44px">${list([['고르기 → 표', '질병 · 치료 선택 → 12종 지급 한 표. 고객 앞에 표 한 장'], ['조합해서', '시뮬로 숫자 → MeAI 통계 그래프 → [용어]로 쉬운 말'], ['확정은 약관', '시뮬 숫자는 조건 예시. 지급은 약관 기준']], 22)}</div>
</div>`,
`[1:17] 숫자 → 그림 → 쉬운 말 순서로 설명하면 고객이 알아듣습니다. 2610 주력 담보용 콤보.`,
'자료: 영업지원도구 통합치료비 시뮬레이션 화면');

add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="h1" style="font-size:84px">나머지 셋, <span class="r">한 번씩</span> 열어 보기</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:360px;display:grid;grid-template-columns:repeat(3,1fr);gap:70px">
  ${[['상품 라인업', '& 예외질환 판정', '상품별 가입 조건 한 화면 + 예외질환 판정 50종. 유병자 고객은 판정 → MeAI 상세 분석 → 확정은 심사'], ['프롬프트 라이브러리', '30종 · STEP 0~7', 'MeAI에 원클릭 복사해서 활용하기. 번호로 찾아 붙여 넣기'], ['명패 제작기', '워밍업 Q3의 답', '엑셀 명단 올리고 테마 고르고 인쇄. 신인 위촉식 명패를 첫 출근 선물로. 행사 끝나면 명단 파일 삭제']].map(([a, b, c]) => `<div style="border-top:3px solid #E60023;padding-top:28px"><div style="font-size:48px;font-weight:900;letter-spacing:-0.03em">${a}</div><div class="kick y" style="margin-top:10px;font-size:24px">${b}</div><div class="p" style="margin-top:24px;font-size:27px">${c}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:140px;top:860px">예외질환 판정 시뮬레이터로 간편보험의 예외질환 입원 · 수술 인수 여부를 확인할 수 있습니다.</div>`,
`[1:18] 상품 라인업 · 프롬프트 라이브러리 · 명패 제작기. 한 번씩 열어 보기만 해도 충분합니다.`,
'자료: 영업지원도구 6종 화면');

const COMBO = [['청구 설명', ['보상시뮬레이터로 지급 조건', '맞춤대화 ‘이 고객 말로 설명문’', '요약 리포트 카카오톡'], '“이 병이면 얼마 나와요?”를 고객용 설명 한 장으로'], ['유병자 고객', ['상품 라인업 예외질환 판정', 'MeAI 상세 분석으로 약관 근거', '가계약 제안서 [생성하기]'], '판정은 도구, 설명은 MeAI, 확정은 심사'], ['통합치료비 설명', ['통합치료비 시뮬 12종', '지식 검색 : 질병통계 그래프 1장', '[용어]로 ‘주요치료’ 쉬운 말'], '2610 주력 담보를 숫자 → 그림 → 쉬운 말 순서로']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:130px;text-align:center"><div class="h1" style="font-size:88px">도구로 <span class="y">확인</span> → MeAI로 <span class="y">말</span> → 리포트로 <span class="r">기록</span></div></div>
<div class="box" style="position:absolute;left:180px;right:180px;top:400px;display:grid;grid-template-columns:repeat(3,1fr);gap:70px">
  ${COMBO.map(([t, s, b]) => `<div style="border-top:3px solid #E60023;padding-top:28px"><div style="font-size:40px;font-weight:800">${t}</div>
    ${s.map((x, i) => `<div style="font-size:26px;font-weight:600;color:#C9CACD;margin-top:18px"><span style="color:#FFD43B;font-weight:800;margin-right:12px">${i + 1}</span>${x}</div>`).join('')}<div class="ps" style="margin-top:22px">${b}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:96px;right:96px;top:880px;text-align:center">11월 영업방향 및 상품 이슈와 같이 활용해 보세요.</div>`,
`[1:19] 패턴은 같습니다. 사실 → 고객 말 → 기록.`);

// ───────────── PART 7 실습 (1:20~1:27)
add(sec('07', '실습', '한번 해봅시다, MeAI', '2인 1조, 코칭 대화 Before/After, 오래 잘 쓰는 약속. 본인 폰으로, 고객 실명 · 연락처 입력 금지.'), `[1:20] PART 7.`);

const BA = [['“매니저님, 이 특약 뭐예요?”', '약관 찾아보세요.', '특약검색기에 코드 쳐 보세요. 지급금액 표 캡처해서 오시면, 어디가 헷갈리는지 그때 이야기해요.'], ['“고객이 보험료 부담돼서 정리하재요.”', '그냥 해지하고 새로 넣어 드리세요.', '맞춤대화에 월 보험료 적고 보장분석 돌려 보세요. 유지 · 보완부터요. 해지 얘기는 맨 뒤예요.'], ['“갑상선암 보험 왜 필요하냐는데요.”', '요즘 갑상선암 많다고 하세요.', '지식 검색에서 갑상선암 통계 그래프 뽑고, [용어] 켜서 ‘초기제외’ 눌러 보세요. 그래프 하나, 문장 하나면 돼요.'], ['“생각해 본대요.”', '다음에 또 연락해 보세요.', '꼬리질문 눌러서 문안 3개 뽑아 오세요. 제가 하나 골라 드릴게요.']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:84px">같은 질문, <span class="r">다른 대답</span></div><div class="p" style="margin-top:10px">매니저가 더 많이 아는 게 아니라, 어디서 찾고 무엇을 믿지 말지 아는 것</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:310px">
  <div class="row" style="padding-bottom:14px"><div style="width:520px" class="ps">신인의 질문</div><div style="width:400px" class="ps">Before</div><div class="ps y" style="flex:1">After</div></div>
  ${BA.map(([q, b, a]) => `<div class="row" style="padding:24px 0;border-top:1px solid #222326;align-items:flex-start">
    <div style="width:520px;font-size:30px;font-weight:800;padding-right:30px">${q}</div>
    <div class="k" style="width:400px;font-size:26px;font-weight:500;padding-right:30px">${b}</div>
    <div style="flex:1;font-size:27px;font-weight:600;line-height:1.5">${a}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:920px;text-align:center;font-size:34px">After는 전부 <span class="y">‘찾아서 가져오세요, 그때 이야기해요’</span>로 끝납니다.</div>`,
`[1:20] Before를 먼저 읽고, After를 청중이 먼저 맞혀 보게 합니다.`);

const PR3 = [['A', '이번달 영업방향', '일반대화', '추천 프롬프트 하나를 골라 눌러 보고, 요약 리포트를 카카오톡으로 발송해 보기'], ['B', '보장분석 요청 고객', '맞춤대화', '고객 1명 선택 → 프롬프트 라이브러리에서 마음에 드는 질문 → 꼬리질문 → 요약 리포트 생성'], ['C', '통계 · 용어로 설명', '지식 검색 · [용어]', '‘갑상선암 보험 왜 필요해요? 요즘 낫는다던데’ → ‘갑상선암 통계자료 보여줘’ → [용어] 켜서 ‘초기제외’ → 그래프 하나 + 한 문장']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="kick y">2인 1조 실습 7분</div><div class="h1" style="margin-top:12px;font-size:76px">본인 폰 MeAI로. 매니저 역할은 <span class="r">질문만</span></div><div class="p" style="margin-top:10px">조별 30초 발표 · 고객 실명 · 연락처 입력 금지 · 답변 근거 한 줄 확인</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:400px;display:grid;grid-template-columns:repeat(3,1fr);gap:60px">
  ${PR3.map(([k, a, b, c]) => `<div style="border-top:3px solid #E60023;padding-top:26px"><div class="row" style="gap:18px"><div style="font-size:72px;font-weight:900;color:#E60023;line-height:1">${k}</div><div class="tag">${b}</div></div><div style="font-size:42px;font-weight:900;margin-top:20px;letter-spacing:-0.03em">${a}</div><div class="ps" style="margin-top:18px;font-size:25px">${c}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:140px;top:900px">모바일 MeAI는 <span class="w">목소리로 입력</span>하는 것도 가능합니다. 편하게 사용해 보세요.</div>`,
`[1:22] 2인 1조, 한 사람은 신인, 한 사람은 매니저. 매니저 역할은 답을 주지 말고 질문만.
7분 뒤 조별 30초 발표 : 어떤 질문을 눌렀고, 답 중 무엇을 믿지 않았는지.`);

const PR = [['답변은 <span class="r">검증 후 사용</span>', '오류가 있을 수 있음. 약관 · 증권으로 확인'], ['개인정보 입력 금지', '이름 · 연락처 · 주소 · 주민번호는 질문에 넣지 않음'], ['동의 없으면 보지 않기', '사전조회동의가 없거나 철회된 고객은 막힘'], ['자료 외부 반출 금지', 'MeAI 답변 · 화면 캡처 · 가이드북 · 이 교안, 외부 제공 · 배포 · 게시 모두 금지']];
add(`
<div class="box" style="position:absolute;left:140px;top:130px"><div class="h1" style="font-size:84px">오래 잘 쓰는 <span class="r">네 가지 약속</span></div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:340px;display:grid;grid-template-columns:1fr 1fr;gap:56px 80px">
  ${PR.map(([a, b], i) => `<div class="row" style="gap:30px;align-items:flex-start"><span class="num">${i + 1}</span><div><div style="font-size:44px;font-weight:800;letter-spacing:-0.025em">${a}</div><div class="ps" style="margin-top:6px">${b}</div></div></div>`).join('')}
</div>
<div class="box" style="position:absolute;left:140px;right:140px;top:740px;border:1px solid #2A2B2F;border-radius:20px;padding:34px 44px;text-align:center">
  <div class="kick y" style="font-size:22px">화면 하단 안내문 원문</div>
  <div style="font-size:28px;font-weight:600;line-height:1.6;margin-top:14px;color:#D8D9DC">“MeAI의 답변은 생성형 AI를 통해 작성되어 오류가 있을 수 있으므로, 반드시 직접 근거자료를 확인하여 진위를 검증하시기 바랍니다.<br>미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다.”</div>
</div>`,
`[1:25] 1~4번은 MeAI 화면 하단 안내문에도 있습니다. 특히 사내자료를 SNS에 올리면 안 됩니다.`,
'자료: MeAI 활용 가이드북 p.85');

// ───────────── PART 8 내일 아침 (1:27~1:30)
const ONE = [['찾기', 'MeAI 홈 · 오늘의 추천 고객', '카드 문장 = 고객에게 첫 말'], ['고르기', '고객찾기 · 한눈에 보기 6칸', '‘사전조회동의 필요’면 [사전조회동의 요청하기]'], ['묻기', '맞춤대화 “보장분석 해줘”', '답 아래 꼬리질문 버튼으로 이어 묻기'], ['연락하기', '요약 리포트 · 카톡', '숫자 · 약관 근거 확인 뒤 내 말로 발송']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="kick y">PART 08 · 한 장 요약</div><div class="h1" style="margin-top:14px;font-size:84px">MeAI 홈, <span class="r">이 한 장</span>이면 시작</div></div>
<div class="box" style="position:absolute;left:120px;right:120px;top:380px;display:grid;grid-template-columns:repeat(4,1fr);gap:30px">
  ${ONE.map(([a, b, c], i) => `<div style="position:relative;padding:0 10px"><div style="font-size:26px;font-weight:900;color:#E60023">${i + 1}</div><div style="font-size:84px;font-weight:900;letter-spacing:-0.04em;line-height:1.1;margin-top:6px">${a}</div><div style="font-size:26px;font-weight:700;color:#FFD43B;margin-top:16px">${b}</div><div class="ps" style="margin-top:8px">${c}</div>${i < 3 ? '<div style="position:absolute;right:-26px;top:60px;font-size:48px;color:#3A3B3F;font-weight:900">→</div>' : ''}</div>`).join('')}
</div>
<div class="box row" style="position:absolute;left:96px;right:96px;top:760px;justify-content:center;gap:70px">
  ${[['90일', '맞춤대화 가능'], ['3년 이내', 'MeAI 홈 노출'], ['15분 안팎', '동의 반영'], ['9명', '오늘의 추천 고객']].map(([a, b]) => `<div style="text-align:center"><div class="y" style="font-size:56px;font-weight:900;letter-spacing:-0.03em">${a}</div><div class="ps">${b}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:96px;right:96px;top:930px;text-align:center;font-size:26px">이 장을 출력해 신인 책상 옆에. 지킬 것 : 개인정보 넣지 않기 · 답변은 검증 후 사용 · 동의 없으면 보지 않기 · 자료 외부 반출 금지</div>`,
`[1:27] 뽑아서 신인 책상 옆에. 동의 칩 → 다음 행동 : 사전조회동의 D-n이면 바로 [이 고객으로 맞춤대화 시작], '필요'면 [사전조회동의 요청하기] → 15분 안팎 반영, '철회'면 회색 · 정보를 볼 수 없음 · 새 동의부터.`,
'자료: MeAI 활용 가이드북 p.12 · p.30 · p.46 · p.47 · p.59 · p.85');

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:110px;text-align:center"><div class="kick y">내일 아침 09:30 조회, 딱 두 마디</div></div>
<div class="box" style="position:absolute;left:96px;right:96px;top:200px;display:flex;flex-direction:column;align-items:center;gap:34px">
  <div class="bub" style="background:#fff;color:#111;font-size:64px;font-weight:800;padding:30px 60px;border-radius:60px">“동의 필요한 분, 몇 명이에요?”</div>
  <div class="bub" style="background:var(--red);color:#fff;font-size:64px;font-weight:800;padding:30px 60px;border-radius:60px">“오늘 카드는 누구예요?”</div>
</div>
<div class="box" style="position:absolute;left:96px;right:96px;top:640px;display:grid;grid-template-columns:1fr 1fr;gap:60px;padding:0 160px">
  <div><div class="h4" style="font-size:36px">이번 주 점심</div><div class="p" style="margin-top:8px">영업퀴즈 하나 골라 단톡에 공유</div></div>
  <div><div class="h4" style="font-size:36px">금요일 15분</div><div class="p" style="margin-top:8px">리포트 세 개 모아 방문 피드백 면담 · 우수사례 공유</div></div>
</div>
<div class="box p" style="position:absolute;left:96px;right:96px;top:880px;text-align:center">답 대신 <span class="y">‘찾아보세요’</span>.</div>`,
`[1:28] MeAI 홈 열고 "동의 필요 몇 명이에요? 오늘 카드는 누구예요?" 두 마디. 답 대신 '찾아보세요'.`);

add(`
<div class="box" style="position:absolute;left:140px;top:100px"><div class="kick y">이후 16:30 「교육내용 현장 적용 방법 논의」</div><div class="h1" style="margin-top:14px;font-size:80px">들고 갈 <span class="r">질문 두 개</span></div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:380px;display:flex;flex-direction:column;gap:60px">
  <div class="row" style="gap:40px;align-items:flex-start"><div style="font-size:64px;font-weight:900;color:#E60023;line-height:1">Q1</div><div style="font-size:44px;font-weight:700;line-height:1.5;letter-spacing:-0.025em">우리 지점 신인 중 사전조회 동의가 없는 고객이 가장 많은 사람은 누구이고, 이번 주에 알림톡 몇 통을 보낼 수 있을까?</div></div>
  <div class="row" style="gap:40px;align-items:flex-start"><div style="font-size:64px;font-weight:900;color:#FFD43B;line-height:1">Q2</div><div style="font-size:44px;font-weight:700;line-height:1.5;letter-spacing:-0.025em">매니저 하루 30분 중 나에게 맞는 코칭 루틴으로 바꾼다면 어떻게 바꿔야 할까?</div></div>
</div>
<div class="box p" style="position:absolute;left:140px;top:880px">두 질문을 적어서 나가시면 됩니다.</div>`,
`[1:28] 이후 16:30 과정에서 이 두 질문으로 현장 적용을 논의합니다.`);

add(`<div class="dh">한 달 뒤, 어느 매니저의 하루</div>
<div class="ctr"><div class="box diary" style="font-size:52px">09:30 “동의 필요한 분 몇 명?” 신인이 숫자를 먼저 말했다.<br>11:40 “이 특약 뭐예요?” 대신 특약검색기 캡처를 들고 왔다.<br>16:20 거절당한 신인이 꼬리질문 문안 3개를 뽑아 왔다.<br><span class="y">18:00 오늘은 대답보다 질문을 더 많이 했다.</span></div></div>`,
`[1:29] 처음 '어느 매니저의 하루'의 다시 쓰기. 천천히 읽습니다.`);

add(`<div class="ctr"><div class="box">
  <div style="font-size:170px;font-weight:900;letter-spacing:-0.045em;line-height:1.1">MeAI <span class="r">×</span> FM</div>
  <div style="font-size:48px;font-weight:700;color:#d8d9dc;margin-top:50px;letter-spacing:-0.02em">FM님을 더 <span class="y">슬기롭게</span>, <span class="y">편안하게</span>, <span class="y">즐겁게</span></div>
  <div class="h4" style="margin-top:60px;font-weight:600">감사합니다</div>
  <div class="p" style="margin-top:10px">세일즈혁신TF 이헌수</div>
</div></div>`,
`[1:30] 감사합니다.`);

// ───────────── 굽기
build(S, { FONT, OUT, name: process.argv[5] || 'meai_fm_2611', LAW, title: 'MeAI × FM · FM님을 더 슬기롭게, 편안하게, 즐겁게', subject: 'FM WORKSHOP ONE WAY · 2026.11.10 · 90분' });
