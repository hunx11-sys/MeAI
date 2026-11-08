// 초급리더과정 60분 강의안 「사람이 남는 지점」 · MeAI로 준비하는 신인 도입 · 정착 · 코칭
// 감성 : 참고 교안(검은 바탕 · 한 장 한 메시지 · 큰 글자 · 빨간 강조 상자 · 그림을 크게) · 내용 : MeAI × FM 강의교안 중심
// node build_leader.js <작업폴더 W> <PretendardVariable.woff2> <출력폴더> [이름]
//   W/cap/index.png 는 cap_idx.js 로 먼저 찍어 둔다(영업지원도구 대문)
const { chromium } = require('playwright');
const pptxgen = require('pptxgenjs');
const fs = require('fs'), path = require('path');

const W = process.argv[2], FONT = process.argv[3], OUT = process.argv[4];
const REPO = path.resolve(__dirname, '..', '..');
const CAP = path.join(REPO, 'guidebook_v4', 'captures');
const AS = path.join(__dirname, 'assets');
const url = p => 'file://' + p;
const cap = r => url(path.join(CAP, r));

// 캡처 일부만 보이기 : 원본 크기(sw,sh) · 자를 곳(x,y,w,h) · 보일 폭 dw
function crop(src, sw, sh, x, y, w, h, dw, style) {
  const k = dw / w;
  return `<div class="crop" style="width:${Math.round(dw)}px;height:${Math.round(h * k)}px;${style || ''}"><img src="${src}" style="width:${Math.round(sw * k)}px;margin-left:${-Math.round(x * k)}px;margin-top:${-Math.round(y * k)}px"></div>`;
}

const LAW = '내부 설계사·리더 교육용 자료로 고객 및 외부에 배포·게시할 수 없습니다. MeAI 답변은 생성형 AI로 작성되어 오류가 있을 수 있으며, 보장·지급 내용은 반드시 약관과 근거자료를 확인하세요 [금융소비자보호법 제22조 준수목적].';

const CSS = `
@font-face { font-family: "P"; src: url("file://${FONT}") format("woff2-variations"); font-weight: 45 920; }
:root { --red: #E60023; --yel: #FFD43B; --g1: #A9ABB0; --g2: #6E7076; --g3: #2A2B2F; --g4: #141416; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #444; font-family: "P", sans-serif; color: #fff; word-break: keep-all; }
.slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #000; margin: 0 0 20px; }
.foot { position: absolute; left: 64px; right: 64px; bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.foot .law { font-size: 12.5px; color: #3c3d41; font-weight: 500; letter-spacing: -0.01em; }
.foot .pg { font-size: 16px; color: #55575c; font-weight: 600; }
.src { position: absolute; left: 64px; bottom: 44px; font-size: 15px; color: #5d5f64; font-weight: 500; letter-spacing: -0.01em; }
.ctr { position: absolute; left: 0; right: 0; top: 0; bottom: 80px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.kick { font-size: 28px; font-weight: 600; color: var(--g1); letter-spacing: 0.02em; }
.h0 { font-size: 132px; font-weight: 900; line-height: 1.16; letter-spacing: -0.04em; }
.h1 { font-size: 96px; font-weight: 900; line-height: 1.24; letter-spacing: -0.035em; }
.h2 { font-size: 72px; font-weight: 800; line-height: 1.36; letter-spacing: -0.03em; }
.h3 { font-size: 56px; font-weight: 700; line-height: 1.5; letter-spacing: -0.025em; }
.h4 { font-size: 40px; font-weight: 700; line-height: 1.5; letter-spacing: -0.02em; }
.p { font-size: 30px; font-weight: 500; color: var(--g1); line-height: 1.6; letter-spacing: -0.015em; }
.ps { font-size: 24px; font-weight: 500; color: var(--g1); line-height: 1.55; letter-spacing: -0.01em; }
.r { background: var(--red); color: #fff; padding: 0 0.14em; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
.y { color: var(--yel); }
.g { color: var(--g2); }
.w { color: #fff; }
.k { text-decoration: line-through; text-decoration-color: #6E7076; text-decoration-thickness: 2px; color: #6E7076; }
.crop { overflow: hidden; position: relative; }
.crop img { display: block; }
.scr { position: absolute; border-radius: 18px; overflow: hidden; box-shadow: 0 0 0 1px rgba(255,255,255,.10), 0 40px 120px rgba(0,0,0,.85), 0 0 160px rgba(255,255,255,.07); }
.spot { position: absolute; border-radius: 50%; background: radial-gradient(closest-side, rgba(255,255,255,.11), rgba(255,255,255,0)); pointer-events: none; }
.bgn { position: absolute; font-weight: 900; color: #101012; letter-spacing: -0.06em; line-height: 1; }
.line { height: 1px; background: #2A2B2F; }
.dh { position: absolute; left: 0; right: 0; top: 110px; text-align: center; font-size: 32px; font-weight: 700; color: #8E9095; letter-spacing: 0.02em; }
.diary { font-size: 64px; font-weight: 700; line-height: 1.62; letter-spacing: -0.03em; }
.tag { display: inline-block; font-size: 22px; font-weight: 700; color: var(--yel); border: 1.5px solid #4a3f12; border-radius: 999px; padding: 4px 16px; }
.num { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; background: var(--red); font-size: 32px; font-weight: 800; flex: none; }
.row { display: flex; align-items: center; }
.bub { display: inline-block; padding: 22px 34px; border-radius: 30px; font-size: 32px; font-weight: 600; line-height: 1.45; letter-spacing: -0.02em; }
`;

const S = [];
const add = (h, n, src) => S.push({ h, n, src });
const sec = (num, word, sub, small) => `
<div class="bgn" style="right:40px;top:40px;font-size:640px">${num}</div>
<div class="box" style="position:absolute;left:140px;top:300px">
  <div class="kick">PART ${num}</div>
  <div style="font-size:200px;font-weight:900;line-height:1.1;letter-spacing:-0.04em;margin-top:24px"><span class="r">${word}</span></div>
  <div class="h3" style="margin-top:44px">${sub}</div>
  <div class="p" style="margin-top:20px">${small}</div>
</div>`;

// ───────────── 오프닝 · 신인 3주 차의 일기 (0:00~0:07)
add(`
<div style="position:absolute;right:-200px;top:120px;width:1300px;height:1000px;perspective:2200px">
  <div style="transform:rotateY(-20deg) rotateX(8deg) rotateZ(-2deg);transform-origin:left center;border-radius:20px;overflow:hidden;opacity:.55">
    ${crop(cap('hero/gb5_gate_full_m.png'), 2880, 2580, 0, 0, 2880, 2100, 1300)}
  </div>
</div>
<div style="position:absolute;inset:0;background:linear-gradient(90deg,#000 36%,rgba(0,0,0,.55) 64%,rgba(0,0,0,.25) 100%),linear-gradient(0deg,#000 0%,rgba(0,0,0,0) 34%)"></div>
<div class="box kick" style="position:absolute;left:120px;top:96px;font-size:24px">26년 대전센터 초급리더과정 3차 · 2026.11.9(월) 14:00 · 청주 오스코 203호</div>
<div class="box" style="position:absolute;left:120px;top:286px">
  <div class="kick y">2027 지점장에 도전하는 팀장님께</div>
  <div style="font-size:150px;font-weight:900;line-height:1.14;letter-spacing:-0.04em;margin-top:30px">사람이 남는<br><span class="r">지점</span></div>
  <div style="font-size:40px;font-weight:600;color:#d8d9dc;margin-top:46px;letter-spacing:-0.02em">MeAI로 준비하는 신인 도입 · 정착 · 코칭</div>
</div>
<div class="box" style="position:absolute;left:120px;bottom:120px;font-size:30px;font-weight:700">세일즈혁신TF&nbsp;&nbsp;이헌수</div>`,
`[0:00 · 1분] 인사.
오전 '활동관리가 곧 리크루팅', 점심 뒤 '도전에 대한 이야기'에 이어지는 시간입니다.
내년에 지점장에 도전하실 분들께, 신인을 데려오고 남기고 키우는 일에 MeAI를 어떻게 무기로 쓰는지 60분 동안 보여 드립니다.
오늘은 실습 없이 화면으로 보여 드리고, 사무실에 돌아가 바로 열어 보시면 됩니다.`);

add(`<div class="dh">신인 3주 차의 일기</div>
<div class="ctr"><div class="box diary">팀장님이 약관을 찾아보라고 했다.<br>약관은 수백 쪽이다.<br>어디를 찾으라는 건지는<br>아무도 말해 주지 않았다.</div></div>`,
`[0:01] 천천히 읽습니다. 설명하지 않고 읽기만 합니다.
신인 3주 차, 한 사람의 일기라고 생각하고 들어 주세요.`);

add(`<div class="dh">신인 3주 차의 일기</div>
<div class="ctr"><div class="box diary">아는 사람한테 연락해 보라고 했다.<br>아는 사람한테는<br>지난주에 다 연락했다.<br>이제 누구한테 가야 하지?</div></div>`,
`[0:02] 명단 고갈. 신인이 7~8주 차에 가장 많이 멈추는 자리입니다. 여기서도 설명은 아끼고 다음 장으로.`);

add(`<div class="dh">신인 3주 차의 일기</div>
<div class="ctr"><div class="box diary">고객이 “생각해 볼게요” 했다.<br>그다음에 뭘 해야 할지 몰라서<br>나도 생각만 하다 하루가 갔다.<br><span class="y">내일은 사무실에 나갈 이유를<br>잘 모르겠다.</span></div></div>`,
`[0:03] 첫 거절. 그리고 '나올 이유'가 사라지는 순간.
"우리 지점 신인 중에 이런 일기를 쓰고 있는 사람이 있을까요?" 한 번 묻고 잠깐 멈춥니다.`);

add(`<div class="ctr"><div class="box">
  <div class="h3">신인은 실력이 없어서 떠나지 않습니다.</div>
  <div style="font-size:96px;font-weight:900;letter-spacing:-0.035em;line-height:1.3;margin:40px 0"><span class="r">갈 곳 · 할 말 · 물어볼 사람</span></div>
  <div class="h3">이 셋이 없어서 떠납니다.</div>
</div></div>`,
`[0:04] 오늘 강의의 문제 정의입니다.
갈 곳(WHERE), 할 말(HOW), 물어볼 사람(BELONG). 매니저과정의 네 가지 결핍 중 세 개입니다.
앞의 두 개는 MeAI가 상당 부분 채워 줍니다. 마지막 하나는 리더만 채웁니다.`);

add(`<div class="ctr"><div class="box h2">2027년,<br>여러분 지점의 신인은<br>3주 차에 <span class="y">어떤 일기</span>를 쓰고 있을까요?</div></div>`,
`[0:05] 오늘의 질문. 답은 강의 끝(49장)에서 다시 봅니다.
지점장이 되면 이 일기를 쓰는 사람이 한 팀이 아니라 지점 전체로 늘어납니다.`);

add(`<div class="ctr"><div class="box">
  <div class="kick">지점장의 일은 결국 세 단어입니다</div>
  <div class="row" style="justify-content:center;gap:120px;margin-top:60px">
    <div><div style="font-size:190px;font-weight:900;letter-spacing:-0.04em;line-height:1">도입</div><div class="p" style="margin-top:28px">데려오고</div></div>
    <div><div style="font-size:190px;font-weight:900;letter-spacing:-0.04em;line-height:1">정착</div><div class="p" style="margin-top:28px">남기고</div></div>
    <div><div style="font-size:190px;font-weight:900;letter-spacing:-0.04em;line-height:1">코칭</div><div class="p" style="margin-top:28px">키우는 일</div></div>
  </div>
  <div class="h4" style="margin-top:90px">오늘은 여기에 <span class="r">MeAI</span>를 무기로 붙입니다.</div>
</div></div>`,
`[0:05 · 오늘의 순서] 숫자 → 도입 → 정착 → 코칭 → 도구와 약속 → 내일 아침.
도입은 '어떻게 키워 줄 건데요?'에 화면으로 답하는 법, 정착은 첫 90일 두 개의 벽, 코칭은 하루 30분입니다.`);

add(`<div class="ctr"><div class="box">
  <div style="font-size:150px;font-weight:900;letter-spacing:-0.04em;line-height:1.2">AI는 <span class="y">What</span>,<br>리더는 <span class="r">Why</span></div>
  <div class="p" style="margin-top:56px">사실은 MeAI가 답하고, 순서와 태도는 리더가 가르칩니다.<br>리더가 더 많이 아는 게 아니라, <span class="w">어디서 찾고 무엇을 믿지 말지 아는 것.</span></div>
</div></div>`,
`[0:06] 오늘의 한 줄 메시지.
AI가 답하는 것 : 사실 확인 · 증권 해석, 화법 초안, 용어 · 통계 · 의학, 보장분석 · 요약 리포트.
리더만 하는 것 : 질문 순서와 태도, 병목 진단과 동행, 격려와 기다리기, "이건 믿지 마" 판단.
끝은 늘 "MeAI에 묻고 근거를 가져오세요, 그때 이야기해요".`);

// ───────────── 숫자 (0:07~0:12)
const person = (x, on) => `<g transform="translate(${x},0)" fill="${on ? '#FFD43B' : '#2A2B2F'}"><circle cx="40" cy="34" r="28"/><path d="M0 150 Q0 76 40 76 Q80 76 80 150 Z"/></g>`;
add(`<div class="ctr"><div class="box">
  <div class="kick">TA채널 FP 열 명 중 아홉 명</div>
  <svg width="1240" height="150" viewBox="0 0 1240 150" style="margin-top:44px">${[...Array(10)].map((_, i) => person(i * 124 + 2, i < 9)).join('')}</svg>
  <div style="font-size:250px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:40px" class="y">91.1%</div>
  <div class="h4" style="margin-top:30px">MeAI를 한 번 이상 써 봤습니다 <span class="g">(10,968명)</span></div>
</div></div>`,
`[0:07] 숫자로 먼저 납득합니다. '회사가 하라니까'로는 신인도 팀원도 안 씁니다.
이미 열 명 중 아홉 명이 써 봤습니다. 문제는 '써 봤느냐'가 아니라 '매일 쓰느냐'입니다.`,
'자료: 2026년 8월 TA채널 MeAI 사용 데이터 분석 (MeAI 활용 가이드북 p.9)');

add(`
<div class="box" style="position:absolute;left:140px;top:250px">
  <div class="kick">MeAI를 쓴 FP의 체결전환율</div>
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
`[0:08] 체결전환율 12.7% → 35.4%, 2.8배.
같은 FP의 고객끼리 비교해도 9.0% → 36.0%, 4배. 사람이 아니라 습관이 만든 차이입니다.`,
'자료: 2026년 8월 TA채널 MeAI 사용 데이터 분석 (MeAI 활용 가이드북 p.9)');

const BARS = [['미사용', 10.22, '5,987명'], ['1일', 19.81, '1,835명'], ['2~4일', 26.35, '2,487명'], ['5~9일', 38.47, '1,372명'], ['10일 이상', 55.04, '362명']];
const BC = ['#232427', '#2E2F33', '#3C3E43', '#55575D', 'var(--red)'];
add(`
<div class="box h2" style="position:absolute;left:140px;top:90px">한 달에 <span class="y">10일</span> 쓰면, 평균 가계약 <span class="r">5.4배</span></div>
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
`[0:09] 7월 MeAI 활동일별 평균 가계약. 미사용 10.22건, 10일 이상 55.04건.
MeAI 활동일은 리더가 매일 볼 수 있는 가장 쉬운 활동 지표입니다. 오전 '활동관리가 곧 리크루팅'과 같은 이야기.`,
'자료: 2026년 8월 TA채널 MeAI 사용 데이터 분석 (가이드북 p.10) · 7월 활동일별 평균 가계약(건) · 인원은 각 구간 FP 수');

const LB = [['밀착 코칭', 185, 'var(--yel)'], ['활동 관리', 120, '#D8D9DC'], ['단순 공지', 15, '#55575D'], ['방임', -28, 'var(--red)']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h2">같은 이슈, 결과는 <span class="y">+185%</span> vs <span class="r">-28%</span></div>
<div class="p" style="margin-top:10px">절판 시기 본부별 실적 증감 · 차이는 상품이 아니라 리더의 관여 방식</div></div>
<div class="box" style="position:absolute;left:180px;top:330px;width:1000px;height:620px">
  <div style="position:absolute;left:96px;right:96px;top:470px;height:2px;background:#3A3B3F"></div>
  ${LB.map(([l, v, c], i) => {
    const x = i * 250, h = Math.round(Math.abs(v) * 2.2);
    const top = v >= 0 ? 470 - h : 472;
    return `<div style="position:absolute;left:${x}px;top:${top}px;width:170px;height:${h}px;background:${c};border-radius:${v >= 0 ? '12px 12px 0 0' : '0 0 12px 12px'};${i === 0 ? 'box-shadow:0 0 90px rgba(255,212,59,.35)' : ''}"></div>
    <div style="position:absolute;left:${x - 20}px;width:210px;text-align:center;top:${v >= 0 ? top - 62 : top + h + 8}px;font-size:44px;font-weight:800;color:${v >= 0 ? (i === 0 ? '#FFD43B' : '#fff') : '#ff4d6a'}">${v > 0 ? '+' : ''}${v}%</div>
    <div style="position:absolute;left:${x - 20}px;width:210px;text-align:center;top:${v >= 0 ? 490 : 380}px;font-size:28px;font-weight:700;color:#A9ABB0">${l}</div>`;
  }).join('')}
</div>
<div class="box" style="position:absolute;left:1260px;top:430px;width:560px">
  <div class="h3" style="font-size:60px">결과를 가른 건<br><span class="r">리더의 구체적 관심</span></div>
  <div class="p" style="margin-top:30px">도구보다 리더의 관심이 먼저입니다.<br>MeAI는 그 관심을 덜 힘들게 해 줍니다.</div>
</div>`,
`[0:10] 같은 상품 이슈인데 본부별로 +185%와 -28%. 차이는 리더의 관여 방식이었습니다.
경력 FP도 이렇게 갈립니다. 신인에게 방임은 곧 탈락입니다.
지점장이 되면 이 차이가 팀 하나가 아니라 지점 전체의 차이가 됩니다.`,
'출처: 변호사선임비 · 주요치료비 절판 시기 본부별 실적 증감');

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
  <div class="kick">지점장이 되면, 한 사람에게 쓸 수 있는 코칭 시간</div>
  <div class="p" style="margin-top:22px">하루 코칭 가능 시간 2시간 ÷ 관리 인원 15명 <span class="g">(예시)</span></div>
  <div class="h3" style="margin-top:70px">이 8분을 ‘사실 확인’에 쓰면,<br>그대로 끝납니다.</div>
  <div class="h4 y" style="margin-top:40px">사실은 MeAI에게 넘기고,<br>리더의 8분은 ‘왜’에 씁니다.</div>
</div>`,
`[0:11] 지점장이 되면 같은 질문을 더 많은 사람에게 듣습니다. 09:30 "뭘 팔죠?", 11:40 "뭐라 말하죠?", 16:20 "거절당했어요".
세 질문은 전부 '사실'을 묻는 질문입니다. 사실은 MeAI가, 순서와 태도는 리더가.
2시간 ÷ 15명은 예시 숫자라고 꼭 말합니다.`);

// ───────────── PART 1 도입 (0:12~0:23)
add(sec('01', '도입', '“우리 지점 오면, 어떻게 키워 주실 건데요?”', '리크루팅 면담의 마지막 질문. 말이 아니라 화면으로 답합니다.'),
`[0:12] PART 1 도입. 리크루팅 면담에서 결국 나오는 질문입니다.
"열심히 도와줄게"는 누구나 하는 말입니다. 오늘은 보여 줄 화면을 가져갑니다.`);

add(`
<div class="box h3" style="position:absolute;left:96px;right:96px;top:110px;text-align:center;font-size:60px">신인 대부분은 ‘오고 싶어서’ 온 게 아닙니다</div>
<div class="box" style="position:absolute;left:260px;top:300px;width:620px">
  <div class="kick g">우리가 기대하는 신인</div>
  <div class="h4 k" style="margin-top:30px;line-height:1.9">명확한 소득 목표<br>스스로 시장을 찾음<br>거절에도 끄떡없음<br>알아서 매일 출근</div>
</div>
<div class="box" style="position:absolute;left:1040px;top:300px;width:660px">
  <div class="kick w">실제로 들어오는 신인</div>
  <div class="h4" style="margin-top:30px;line-height:1.9">‘일단 해볼까’로 입사<br>누구에게 갈지 모름<br>첫 거절에 무너짐<br>나올 이유가 없으면 안 나옴</div>
</div>
<div style="position:absolute;left:960px;top:310px;width:1px;height:380px;background:#2A2B2F"></div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:800px;text-align:center;font-size:44px"><span class="r">동기는 입사 조건이 아니라, 리더가 만들어 주는 결과입니다.</span></div>`,
`[0:13] 왼쪽을 기대하면 매일 실망합니다. 오른쪽이 출발점이라는 걸 받아들이는 게 지점장의 첫걸음입니다.
"왜 안 뛰어?" 전에 "뛸 곳을 줬나?"`,
'출처: 2610 신인활동관리 매니저과정 p.5');

add(`
<div class="spot" style="left:780px;top:40px;width:1400px;height:1100px"></div>
<div style="position:absolute;left:820px;top:110px;width:1100px;perspective:2400px">
  <div class="scr" style="position:relative;transform:rotateY(-12deg) rotateX(4deg);transform-origin:left center">
    ${crop(cap('hero/gb5_gate_full_m.png'), 2880, 2580, 0, 0, 2880, 2280, 1040)}
  </div>
</div>
<div style="position:absolute;left:0;top:0;bottom:0;width:900px;background:linear-gradient(90deg,#000 70%,rgba(0,0,0,0))"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(0deg,#000 30%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:270px;width:700px">
  <div class="kick y">MeAI 홈</div>
  <div class="h2" style="margin-top:26px;font-size:80px">면담에서는<br>이 화면<br><span class="r">하나면</span> 됩니다</div>
  <div class="p" style="margin-top:40px">영업포탈에서 MeAI로 들어오면<br>가장 먼저 열리는 화면입니다.</div>
</div>`,
`[0:14] MeAI 홈. 대화 카드 두 장(일반대화 · 맞춤대화), 내 고객 숫자 4개, 오늘의 추천 고객.
면담에서 후보자 폰 대신 내 폰이나 노트북으로 이 화면을 보여 줍니다. "입사하면 첫날 아침 이 화면에서 시작해요."
화면 속 이름과 숫자는 가이드북 예시입니다.`,
'자료: MeAI 활용 가이드북 p.12~15 · 화면 속 이름과 숫자는 예시');

add(`
<div class="spot" style="left:1000px;top:60px;width:900px;height:980px"></div>
<div class="scr box" style="left:1100px;top:110px;border-radius:26px">${crop(cap('hero/gb5_card_kim_z.png'), 1146, 1242, 0, 0, 1146, 1242, 700)}</div>
<div style="position:absolute;left:1068px;top:262px;width:10px;height:190px;background:var(--red);border-radius:5px;box-shadow:0 0 30px rgba(230,0,35,.8)"></div>
<div class="box" style="position:absolute;left:140px;top:250px;width:860px">
  <div class="h2" style="font-size:76px">명단이 없어도<br>첫날 연락할 사람과<br><span class="y">이유</span>가 떠 있습니다.</div>
  <div class="p" style="margin-top:44px">매일 밤 계산해 아침에 9명.<br><span class="w">카드 한 문장이 곧 고객에게 하는 첫 말입니다.</span></div>
</div>`,
`[0:15] 추천 카드 한 장. "상령일이 2주 남았고 암진단비가 1천만원뿐입니다."
왜 지금 이 고객인지가 한 문장으로 붙어 있습니다. 풀면 곧 첫 통화 멘트입니다.
태그(보장 공백 · 당월 타겟 · 이벤트 임박), 동의 칩(D-n이면 바로, '필요'면 동의부터), [MeAI 고객찾기에서 열기].`,
'자료: MeAI 활용 가이드북 p.20 · 이름과 내용은 예시');

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
</div>`,
`[0:16] 고르는 시간은 시스템이 없애고, 설득은 사람이 합니다.
리더의 질문이 "몇 통 했어요?"에서 "오늘 카드는 누구예요?"로 바뀝니다.`,
'자료: MeAI 활용 가이드북 p.6');

const wall = (file, txt, sub) => `
<div style="position:absolute;left:0;top:70px;width:1920px">${crop(url(path.join(AS, file)), 1676, 670, 0, 0, 1676, 670, 1920)}</div>
<div style="position:absolute;inset:0;background:radial-gradient(ellipse 75% 70% at 50% 40%,rgba(0,0,0,0) 40%,rgba(0,0,0,.9) 100%),linear-gradient(0deg,#000 32%,rgba(0,0,0,.6) 52%,rgba(0,0,0,0) 72%)"></div>
<div class="box" style="position:absolute;left:140px;top:640px">
  <div class="h1" style="font-size:88px">${txt}</div>
  <div class="p" style="margin-top:22px">${sub}</div>
</div>`;
add(wall('wall_stats481.jpg', '신인이 외울 통계는 <span class="y">0개</span>,<br>보여 줄 그래프는 <span class="r">481장</span>', '암 · 뇌 · 심장 · 치매 · 수술 · 장애까지. <span class="w">“OO 통계 보여줘” 한 마디면 됩니다.</span>'),
`[0:17] 질병통계 그래프 481장이 MeAI 안에 있습니다. 한 장씩 넘기지 말고 벽을 보여 주세요.
면담에서 "공부할 게 너무 많아 겁나요"라고 하면 이 장을 보여 줍니다. 외우는 게 아니라 묻는 겁니다.`,
'자료: 질병의료통계 2026 MeAI RAG판(2026-10-13) 481장 · 국가암등록통계 · HIRA 재가공');

add(wall('wall_medical223.jpg', '그릴 그림은 <span class="y">0장</span>,<br>보여 줄 그림은 <span class="r">223장</span>', '수술 · 시술 · 검사 · 치료 · 응급처치 · 재활. <span class="w">“흡인이 뭐예요?” 하면 그림으로 답합니다.</span>'),
`[0:18] 의학 그림 223장, 의학 지식 223주제. "전이암이 뭐예요?"에 그림과 카드로 답합니다.
신인이 고객 앞에서 막히는 두 가지가 용어와 의학입니다. 리더가 밤새 공부해서 알려 줄 필요가 없어졌습니다.`,
'자료: 의료기술 고객설명 그림 223장(2026-10-23 전달) · MeAI 의학지식 RAG 223주제');

const CH = ['신인교육과정 안내', '보험 기초 용어', '5대 보장자산', '상품 라인업', '태아·어린이보험', '운전자·상해·바이크', '주택·일반화재', '치아보험', '자동차보험', '암 보장', '뇌·심장혈관질환', '수술비', '입원일당·간병', '실손의료비', '후유장해·사망·배상책임', '생명보험 증권 컨설팅', '알릴의무·완전판매·보험사기', '지표관리·리스크관리', '영업활동·전산·보장분석·MeAI'];
add(`
<div class="box" style="position:absolute;left:140px;top:270px;width:820px">
  <div class="kick y">2026 스타터, MeAI 안에</div>
  <div style="font-size:250px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:24px">608<span style="font-size:130px">쪽</span></div>
  <div class="h4" style="margin-top:34px;font-weight:600">18챕터 · 신인 교재 19개가<br>장별로 MeAI에 들어 있습니다</div>
  <div class="h4" style="margin-top:44px;font-size:46px"><span class="r">교육은 MeAI가, 확인은 리더가.</span></div>
</div>
<div class="box" style="position:absolute;left:1040px;top:250px;width:800px;display:grid;grid-template-columns:1fr 1fr;gap:24px 40px">
  ${CH.map((c, i) => `<div style="font-size:27px;font-weight:600;color:#8E9095;white-space:nowrap;letter-spacing:-0.02em"><span style="color:#E60023;font-weight:800;margin-right:10px">${String(i).padStart(2, '0')}</span>${c}</div>`).join('')}
</div>`,
`[0:19] 2026년 11월 상품 기준으로 다시 짠 메리츠 스타터 18챕터 608쪽. 장별로 MeAI에 올라갔습니다.
기초용어부터 전산 활용까지. 신인이 묻는 '무엇'은 교재 기준으로 MeAI가 답하고, 리더는 확인합니다.
하루 10분 훈련표(제안) : 월 의학용어 3개 · 화 약관 한 조문 · 수 통계 한 장 · 목 테스트 질문 1문 · 금 리플레이 15분. 신인 폰의 MeAI로 하고, 리더는 금요일에 한 번만 봅니다.`,
'자료: 28_MeAI_신인교육_RAG_2026스타터 (2026-11-04)');

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:110px;text-align:center"><div class="h4 g" style="font-size:44px">“우리 지점 오면, 어떻게 키워 주실 건데요?”</div></div>
<div class="box" style="position:absolute;left:200px;right:160px;top:290px;display:flex;flex-direction:column;gap:56px">
  ${[['첫날부터 연락할 고객과 이유가 <span class="y">이렇게</span> 떠요.', 'MeAI 홈 · 추천 카드를 그 자리에서 보여 주기'], ['첫 5일은 하루 하나씩, 금요일엔 <span class="y">15분씩</span> 같이 봐요.', '첫 5일 미션 · 금요일 리플레이'], ['지표는 한 달 활동일 <span class="y">10일</span>. 가계약 5.4배로 설명할게요.', 'MeAI 활동일 = 리더가 매일 보는 지표']].map(([a, b], i) => `<div class="row" style="gap:40px;align-items:flex-start">
    <span class="num" style="margin-top:6px">${i + 1}</span><div><div class="h3" style="font-size:54px">${a}</div><div class="ps" style="margin-top:6px">${b}</div></div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:880px;text-align:center">키우는 방법이 보이는 지점에 <span class="r">사람이 모입니다.</span></div>`,
`[0:21] 리크루팅 면담 세 문장(제안). 약속은 말보다 화면과 숫자로.
위촉 첫날엔 명패 제작기로 이름만 넣고 인쇄 1분, 첫 출근 책상 위에 올려 두세요. 소속감은 첫날 만들어집니다.
오전 '활동관리가 곧 리크루팅'과 같은 이야기입니다. 2027년 리크루팅 면담에서 바로 쓰실 수 있습니다.`);

// ───────────── PART 2 정착 (0:23~0:37)
add(sec('02', '정착', '첫 90일, 두 개의 벽', '신인은 첫 거절과 명단 고갈에서 쉽게 꺾입니다. 벽이 오기 전에 화면부터 쥐여 주세요.'),
`[0:23] PART 2 정착. 도입보다 더 어려운 것이 정착입니다.`);

const PTS = [0.30, 0.58, 0.82, 0.30, 0.37, 0.45, 0.52, 0.17, 0.12, 0.10, 0.09, 0.09];
const curve = () => {
  const X = i => 40 + i * 140, Y = v => 440 - v * 400; const P = PTS.map((v, i) => [X(i), Y(v)]);
  let d = `M${P[0][0]} ${P[0][1]}`;
  for (let i = 0; i < P.length - 1; i++) { const p0 = P[i - 1] || P[i], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2] || p2; d += ` C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)} ${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)} ${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0]} ${p2[1]}`; }
  return { d, P };
};
const CV = curve();
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:88px">신인은 <span class="r">두 번</span> 꺾입니다</div>
<div class="ps" style="margin-top:12px">신인 주간 연락 수 · 개념 설명용 예시 곡선</div></div>
<svg style="position:absolute;left:180px;top:300px" width="1640" height="520" viewBox="0 0 1640 520">
  <defs><filter id="g2" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <line x1="40" y1="470" x2="1600" y2="470" stroke="#2A2B2F" stroke-width="2"/>
  ${[[0, '1주'], [3, '4주'], [7, '8주'], [11, '12주']].map(([i, t]) => `<text x="${40 + i * 140}" y="508" fill="#6E7076" font-size="24" font-weight="600" text-anchor="middle" font-family="P">${t}</text>`).join('')}
  <path d="${CV.d}" stroke="#ffffff" stroke-width="7" fill="none" filter="url(#g2)" stroke-linecap="round"/>
  ${[3, 7].map(i => `<circle cx="${CV.P[i][0]}" cy="${CV.P[i][1]}" r="20" fill="#E60023" filter="url(#g2)"/>`).join('')}
</svg>
<div class="box" style="position:absolute;left:680px;top:650px;width:380px"><div class="h4" style="font-size:38px"><span class="r">벽 ① 첫 거절</span></div><div class="ps">3~4주</div></div>
<div class="box" style="position:absolute;left:1240px;top:540px;width:420px"><div class="h4" style="font-size:38px"><span class="r">벽 ② 명단 고갈</span></div><div class="ps">7~8주</div></div>
<div class="box" style="position:absolute;left:180px;top:850px;width:760px"><div class="ps"><span class="y">MeAI</span>&nbsp; 꼬리질문 · 거절처리 문안 3개</div><div class="ps"><span class="w">리더</span>&nbsp; 거절의 재해석, 같이 복기</div></div>
<div class="box" style="position:absolute;left:1000px;top:850px;width:760px"><div class="ps"><span class="y">MeAI</span>&nbsp; 홈 추천 9명 · 그룹(상령일 · 생일 · 동의만료)</div><div class="ps"><span class="w">리더</span>&nbsp; 첫 면담부터 소개 요청</div></div>`,
`[0:24] 3~4주 첫 거절, 7~8주 명단 고갈. 지점별로 신인 주간 연락 수를 적어 보면 실제 곡선이 나옵니다.
두 벽 앞에 MeAI 화면을 미리 쥐여 주세요. 순서는 명단 고갈 해법 먼저, 그다음 첫 거절.`);

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:90px;text-align:center"><div class="h1" style="font-size:88px">명단이 마르면, 매일 아침 <span class="y">9명</span></div>
<div class="p" style="margin-top:14px">카드 3장 × 3세트 · 이유 한 문장 · 매일 밤 다시 계산해 다음 날 반영</div></div>
<div class="spot" style="left:260px;top:280px;width:1400px;height:900px"></div>
<div class="scr box" style="left:330px;top:310px;border-radius:22px">${crop(cap('hero/gb5_gate_reco3_m.png'), 2280, 1018, 0, 0, 2280, 950, 1260)}</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:965px;text-align:center;font-size:30px;font-weight:600">신인에게 카드 문장을 <span class="y">소리 내 읽게</span> 하세요. 그게 오늘의 첫 통화 멘트입니다.</div>`,
`[0:25] 벽 ② 명단 고갈의 첫 번째 해법. 오른쪽 왼쪽 화살표로 넘기면 9명.
100명 명단은 목표가 아니라 '꺼내는 방법'이고, 기존 고객은 MeAI 홈이 매일 9명씩 꺼내 줍니다.`,
'자료: MeAI 활용 가이드북 p.21 · 이름과 내용은 예시');

const GR = [['상령일 임박', '같은 보장을 더 싸게 준비할 수 있는 마지막 구간'], ['생일 임박', '축하 인사로 대화를 열고 보장 점검으로 잇기 좋은 때'], ['사전동의 만료', '만료 전에 재동의를 받아야 연락을 이어 갈 수 있음'], ['암진단비 부족', '치료비 실제 부담액 기준으로 설명하면 필요가 분명해짐']];
add(`
<div class="spot" style="left:60px;top:40px;width:900px;height:1000px"></div>
<div class="scr box" style="left:200px;top:110px;border-radius:22px">${crop(cap('hero/find_groups_z.png'), 840, 2250, 0, 0, 840, 1411, 500)}</div>
<div style="position:absolute;left:0;right:0;bottom:0;height:180px;background:linear-gradient(0deg,#000 45%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:880px;top:150px;width:960px">
  <div class="h1" style="font-size:96px">그룹 이름이<br>곧 <span class="r">연락 이유</span></div>
  <div class="p" style="margin-top:20px">고객찾기 왼쪽 · 보장 기준 10 + 영업 기회 3</div>
  <div style="margin-top:44px;display:flex;flex-direction:column;gap:22px">
    ${GR.map(([a, b]) => `<div class="row" style="gap:28px"><div style="width:230px;font-size:30px;font-weight:800;color:#FFD43B;flex:none">${a}</div><div style="font-size:28px;font-weight:600;color:#D8D9DC">${b}</div></div>`).join('')}
  </div>
  <div class="h4" style="margin-top:50px;font-size:38px">명단이 마르면 <span class="y">“그룹 하나 골라, 오늘 세 명.”</span></div>
</div>`,
`[0:27] 명단 고갈의 두 번째 해법. 고객찾기 왼쪽 그룹. 그룹 이름 자체가 연락 이유입니다.
화면 문구를 그대로 읽어도 화법이 됩니다. 한 고객이 여러 그룹에 들 수 있고, 그룹이 많을수록 할 말이 많은 고객입니다.`,
'자료: MeAI 활용 가이드북 p.32 · p.34 · 그룹 인원은 예시');

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:110px;text-align:center">
  <div class="kick">아침 조회, 리더의 첫 질문</div>
  <div class="h1" style="margin-top:22px;font-size:100px">“동의 필요한 분,<br><span class="r">몇 명</span>이에요?”</div>
</div>
<div class="spot" style="left:260px;top:420px;width:1400px;height:700px"></div>
<div class="scr box" style="left:310px;top:540px;border-radius:20px">${crop(cap('hero/gate_stats.png'), 2280, 390, 0, 0, 2280, 390, 1300)}</div>
<div class="box row" style="position:absolute;left:96px;right:96px;top:830px;justify-content:center;gap:60px">
  ${['알림톡 한 통으로 동의', '15분 안팎 반영', '맞춤대화 가능 90일', 'MeAI 홈 노출 3년 이내'].map(t => `<div class="h4 y" style="font-size:30px">${t}</div>`).join('<div class="h4 g" style="font-size:30px">·</div>')}
</div>
<div class="box ps" style="position:absolute;left:96px;right:96px;top:900px;text-align:center;font-size:26px">우회 말고 동의부터. 첫 말 : <span class="w">“보장을 정확히 보려면 동의가 필요해요, 알림톡 하나 보내 드릴게요.”</span></div>`,
`[0:29] 내 고객 숫자 4개 : 전체 · 맞춤대화 가능 · 사전조회 동의 필요 · 상품제안 가능.
"동의 필요 몇 명이야?" 이 한 마디가 조회 첫 질문입니다. 숫자 4개를 주간 보드에 적으면 동의 요청이 습관이 됩니다.
신인이 가장 자주 막히는 곳이 동의입니다. 동의가 없으면 맞춤대화가 안 열립니다.`,
'자료: MeAI 활용 가이드북 p.18 · p.46 · 숫자는 예시');

add(`<div class="ctr"><div class="box">
  <div class="kick">벽 ① 첫 거절</div>
  <div style="font-size:150px;font-weight:900;letter-spacing:-0.045em;line-height:1.2;margin-top:30px">“생각해 볼게요.”</div>
  <div class="h3 g" style="margin-top:50px">그다음 말은,</div>
  <div class="h2" style="margin-top:14px"><span class="r">꼬리질문 버튼</span>에서 나옵니다.</div>
</div></div>`,
`[0:30] 첫 거절. 신인은 '생각해 볼게요' 뒤에 뭘 해야 하는지 모릅니다. 리더는 화법을 대신 써 주는 대신 버튼을 알려 줍니다.`);

add(`
<div class="spot" style="left:20px;top:120px;width:1200px;height:900px"></div>
<div class="scr box" style="left:120px;top:250px;border-radius:22px">${crop(cap('hero/mode_pc_bottom2_z.png'), 2340, 1650, 0, 290, 1500, 700, 1000)}</div>
<div class="box" style="position:absolute;left:1240px;top:200px;width:600px">
  <div class="kick">질문 3개 이상이면 평균 가계약</div>
  <div class="y" style="font-size:230px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:20px">2.3<span style="font-size:130px">배</span></div>
  <div class="p" style="margin-top:20px">질문 1개 11.99건 → 3개 이상 27.79건<br>답 아래 버튼을 <span class="w">누르기만</span> 하면 됩니다</div>
</div>
<div class="box h4" style="position:absolute;left:120px;top:830px;font-size:40px">오후 복기 때 리더의 질문 : <span class="r">“꼬리질문 3개까지 갔어요?”</span></div>`,
`[0:31] 답 아래 질문 예시를 누르면 바로 다음 질문이 갑니다. 타이핑 없이.
'생각해 볼게요'를 들었다면 꼬리질문 → 거절처리 프롬프트로 문안 3개. 리더는 "문안 3개 중 제가 하나 골라 드릴게요."
고객 앞에서는 일반(간편) 분석, 약관을 따질 때는 상세 분석.`,
'자료: MeAI 활용 가이드북 p.56 · p.58 · 2026년 8월 TA채널 MeAI 사용 데이터 분석');

add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:84px">“이거 뭐예요?”는<br><span class="y">노란 말</span> 한 번 누르면 끝</div></div>
<div class="box" style="position:absolute;left:1180px;top:130px;width:640px"><div class="p">용어 1,511개 · 쉬운 뜻 50자<br>동의어까지 5,000여 개<br><span class="w">PC는 입력창 오른쪽 위, 모바일은 오른쪽 아래 [용어]</span></div></div>
<div class="spot" style="left:260px;top:360px;width:1400px;height:800px"></div>
<div class="scr box" style="left:310px;top:420px;border-radius:22px">${crop(cap('hero/fix_term_on.png'), 2340, 1158, 0, 0, 2340, 1000, 1300)}</div>
<div style="position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(0deg,#000 35%,rgba(0,0,0,0))"></div>`,
`[0:32] "선배님 이거 뭐예요?"가 여기서 끝납니다. 답 속 어려운 말에 노란 표시 → 누르면 쉬운 뜻.
현장에서는 고객 눈높이 뜻풀이라 그대로 읽어 주면 됩니다. 신인은 거의 휴대폰으로 씁니다.
매니저가 "[용어] 켜서 읽어 보세요" 한 마디면 '이거 뭐예요?' 10번이 0번이 됩니다.`,
'자료: MeAI 용어사전(2026-10-29 전달본 1,511개) · MeAI 활용 가이드북 p.54 · p.55');

const D5 = [['MeAI 홈 열기', '숫자 4개와 추천 카드 3장 읽기', '질문 예시 하나 눌러 보기'], ['카드에서 고객찾기', '[MeAI 고객찾기에서 열기] → 한눈에 보기 6칸', '추천 질문 눌러 보기'], ['맞춤대화 시작', '“보장분석 해줘” → 꼬리질문 2번', '부족 보장 3개 메모'], ['그룹으로 찾기', '[사전동의 만료] 그룹 확인', 'D-n 짧은 1명께 재동의 부탁'], ['리포트 보내기', '요약 리포트 발송', '좋았던 질문을 ‘나의 질문’에 저장']];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="h1">첫 5일, <span class="r">하루 하나씩</span></div><div class="p" style="margin-top:14px">가이드북 첫 5일 미션 그대로. 리더는 체크만 합니다.</div></div>
<div class="box" style="position:absolute;left:110px;right:110px;top:400px;display:grid;grid-template-columns:repeat(5,1fr)">
  ${D5.map(([t, a, b], i) => `<div style="padding:0 30px;${i ? 'border-left:1px solid #26272b' : ''}">
    <div style="font-size:26px;font-weight:800;color:${i === 0 ? '#FFD43B' : '#E60023'};letter-spacing:0.06em">DAY ${i + 1}</div>
    <div style="font-size:40px;font-weight:800;margin-top:16px;line-height:1.3;letter-spacing:-0.025em">${t}</div>
    <div class="ps" style="margin-top:28px;color:#D0D1D4">☐ ${a}</div>
    <div class="ps" style="margin-top:12px;color:#D0D1D4">☐ ${b}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:850px;text-align:center;font-size:36px">찾아가는 영업은 <span class="y">“MeAI 홈에서 영업을 시작”</span>하는 습관입니다.</div>`,
`[0:33] 신인에게 주는 첫 5일 미션. 출력해서 책상에 붙여 주세요.
DAY 3의 '보장분석 해줘'가 다음 장의 첫 계약으로 이어집니다.`,
'자료: MeAI 활용 가이드북 첫 5일 미션');

add(`
<div class="spot" style="left:0;top:80px;width:1250px;height:1000px"></div>
<div class="scr" style="left:110px;top:150px;border-radius:20px;opacity:.9">${crop(cap('hero/bc2_answer_bottom.png'), 1720, 1078, 0, 0, 1720, 560, 760)}</div>
<div class="scr box" style="left:330px;top:430px;border-radius:20px">${crop(cap('real/r09_custom_precontract.png'), 1530, 963, 0, 0, 1530, 963, 760)}</div>
<div class="box" style="position:absolute;left:1200px;top:180px;width:660px">
  <div class="kick y">첫 계약은 리더 옆에서</div>
  <div class="h2" style="margin-top:24px;font-size:70px">“보장분석<br>해줘”<br>→ <span class="r">[생성하기]</span></div>
  <div class="ps" style="margin-top:36px;font-size:26px;line-height:1.75">답은 분석 → 제안 → 다음 행동 순서로 읽기<br>표의 <span class="w">‘미가입’ 줄 1개만</span> 오늘 이야기<br>가계약은 표 확인 → 고칠 것 요청 → 생성<br><span class="w">확정 금액처럼 말하지 않기</span></div>
</div>`,
`[0:34] 맞춤대화는 '보장분석 해줘' 한 마디로 시작합니다. 가장 많이 쓰는 질문은 "가입증권 별로 핵심만 표로 요약해줘".
보장분석 답 → "이 제안대로 가계약 제안서를 만들어줘" → [생성하기]. 동행에서 돌아와 책상에서 바로 가계약까지.
신인의 첫 가계약은 리더가 옆에서 같이 합니다. 금액은 앞의 보완 제안과 다를 수 있어 확정 금액처럼 말하지 않습니다.`,
'자료: MeAI 활용 가이드북 p.53 · p.68 · 실제 MeAI 화면, 이름 가림 · 담보 · 금액은 AI 제안 예시');

add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:84px">90일, 리더는 점점 빠지고<br>신인은 점점 <span class="r">혼자</span></div></div>
<svg style="position:absolute;left:180px;top:380px" width="1560" height="400" viewBox="0 0 1560 400">
  <defs><filter id="g3" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <line x1="60" y1="360" x2="1500" y2="360" stroke="#2A2B2F" stroke-width="2"/>
  <path d="M60 60 C 500 80, 900 300, 1500 320" stroke="#E60023" stroke-width="8" fill="none" filter="url(#g3)" stroke-linecap="round"/>
  <path d="M60 330 C 500 320, 900 120, 1500 50" stroke="#FFD43B" stroke-width="8" fill="none" filter="url(#g3)" stroke-linecap="round"/>
  ${[60, 540, 1020, 1500].map(x => `<circle cx="${x}" cy="360" r="9" fill="#6E7076"/>`).join('')}
</svg>
<div class="box h4" style="position:absolute;left:1360px;top:330px;font-size:30px;color:#FFD43B">신인의 MeAI 사용</div>
<div class="box h4" style="position:absolute;left:1360px;top:705px;font-size:30px;color:#ff4d6a">리더의 관여</div>
<div class="box" style="position:absolute;left:110px;right:110px;top:790px;display:grid;grid-template-columns:repeat(4,1fr);text-align:center">
  ${[['1~2주 준비', '첫 보장분석 3건', '매일 동석'], ['3~4주 첫 출전', '첫 계약', '동행 중심'], ['2개월 확장', '첫 소개 계약', '주 2~3회 점검'], ['3개월 자립', '자립 활동 정착', '주간 리뷰']].map(([a, b, c]) => `<div><div style="font-size:32px;font-weight:800">${a}</div><div class="ps" style="margin-top:6px"><span class="y">목표</span> ${b} · <span style="color:#ff4d6a">리더</span> ${c}</div></div>`).join('')}
</div>`,
`[0:35] 90일 로드맵(개념도). 1~2주 준비(100명 명단 · 가족 보장분석 · 롤플레이) → 3~4주 첫 출전(첫 면담 동행 · 거절 재해석)
→ 2개월 확장(면담마다 소개 요청 · 생애 이벤트) → 3개월 자립(전수 터치 · 목표 스스로 설정).
90일 동안 리더의 관여는 줄고 MeAI 사용은 늘어납니다. 그게 자립입니다.`);

// ───────────── PART 3 코칭 (0:37~0:50)
add(sec('03', '코칭', '하루 30분, 답 대신 질문', '지점장이 되면 코칭할 사람이 늘어납니다. 시간을 늘리는 게 아니라 질문을 바꿉니다.'),
`[0:37] PART 3 코칭.`);

add(`<div class="ctr"><div class="box">
  <div style="font-size:130px;font-weight:900;letter-spacing:-0.045em;line-height:1.2">답을 주지 마세요.</div>
  <div class="h2 y" style="margin-top:50px">“찾아서 가져오세요. 그때 이야기해요.”</div>
  <div class="p" style="margin-top:50px">이 한 문장이 리더의 코칭입니다.<br>신인은 시키면 안 쓰고, <span class="w">보여 주면 씁니다.</span></div>
</div></div>`,
`[0:38] FMBTI 네 유형(약관 박사형 · 내가 다 해줄게형 · 숫자만형 · 조용히 지켜보기형)의 공통 처방도 이것이었습니다.
답을 주지 말고, 찾아오게 하고, 그때 이야기하기.`);

const TL = [['09:30', '조회 5분', '“동의 필요 몇 명? 오늘 카드는 누구?”', '카드 읽고 첫 말 준비'], ['11:00', '동행 전 10분', '요약 리포트에 빨간 펜 3줄', '요약 리포트 1클릭'], ['13:00', '점심 후 1분', '프롬프트 하나 단톡에, 또는 어제 답 속 용어 하나', '본인 폰으로 답'], ['15:00', '거절 복기 10분', '꼬리질문 3개까지 갔는지, 거절 사유는 어디인지', '꼬리질문 3개까지'], ['18:00', '마감 5분', '리포트 발송 수 · 동의 요청 수 · 코칭 인원', '숫자 셋 적기'], ['금요일', '리플레이 15분', '한 주 리포트 모아 자기 대화 설명, 질문 6개', '자기 대화 설명']];
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
<div class="box h4" style="position:absolute;left:96px;right:96px;top:880px;text-align:center;font-size:36px">처음에는 코칭할 신인을 <span class="y">‘오늘 3명’</span>으로 시작하세요.</div>`,
`[0:39] MeAI와 함께하는 리더의 하루 30분. 조회 5분 · 동행 전 10분 · 점심 후 1분 · 복기 10분 · 마감 5분, 그리고 금요일 15분.
오후 셋은 전부 '한 줄'입니다. 길어지면 안 합니다.`);

const CHAT = [['리더', '동의 필요 몇 명이에요? 오늘 추천 고객, 누구한테 연락해 볼 거예요?'], ['신인', '서은아 고객이요. 보상 완료 후 후속 상담이 없었대요.'], ['리더', '그 카드 문장 한번 확인해 보세요. MeAI에 뭘 물어볼 거예요?'], ['신인', '오른쪽 추천 질문이요. 입원일당 부족 고객에게 보낼 문자 문안이요.'], ['리더', '좋아요. MeAI에 넣어 보고, 요약 리포트 한번 뽑아서 봅시다.']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="kick y">09:30 조회 대본</div><div class="h1" style="margin-top:14px;font-size:84px">세 마디면 <span class="r">5분</span></div></div>
<div class="box" style="position:absolute;left:180px;right:180px;top:290px;display:flex;flex-direction:column;gap:18px">
  ${CHAT.map(([w, t]) => w === '리더'
    ? `<div class="row" style="gap:24px"><div style="width:90px;font-size:26px;font-weight:800;color:#E60023;flex:none">리더</div><div class="bub" style="background:#fff;color:#111">${t}</div></div>`
    : `<div class="row" style="gap:24px;justify-content:flex-end"><div class="bub" style="background:#1E1F22;color:#C9CACD">${t}</div><div style="width:90px;font-size:26px;font-weight:800;color:#6E7076;flex:none;text-align:right">신인</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:910px;text-align:center;font-size:34px">리더는 <span class="y">“눌러 보세요”</span>로 끝내고, 신인은 리더가 쓰는 걸 보고 따라 씁니다.</div>`,
`[0:40] 조회 대본. 답을 주지 않고 '찾아보세요'로 끝냅니다. 홈 열기 → 추천 카드 3장 읽기 → 고객찾기에서 열기 → 맞춤대화 · 리포트.
조회에서 리더가 확인하는 셋 : 동의 필요 수, 오늘 카드(9장 중 누구 · 왜), 근거 한 줄(답이 아니라 출처).
두 사람 불러 즉석 롤플레이 30초 해도 좋습니다.`,
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
  <div class="kick y">11:00 동행 전 10분</div>
  <div class="h2" style="margin-top:18px;font-size:68px">요약 리포트에<br><span class="r">빨간 펜 3줄</span></div>
  <div style="margin-top:40px;display:flex;flex-direction:column;gap:26px">
    ${[['① 순서', '잘 갖춘 것 먼저, 비어 있는 것 두 번째. 해지 얘기는 맨 뒤'], ['② 빠진 것', '가족력 · 직업 · 최근 보상. 고객 정보 다섯 칸을 채웠는지'], ['③ 하지 말 것', '‘타사보다 유리’, 확정 금액처럼 말하기, 확인 안 한 숫자']].map(([a, b]) => `<div><div style="font-size:36px;font-weight:800">${a}</div><div class="ps" style="margin-top:4px">${b}</div></div>`).join('')}
  </div>
  <div class="h4 y" style="margin-top:36px;font-size:32px">사실은 리포트에 다 있습니다. 리더는 ‘왜’만.</div>
</div>`,
`[0:42] 신인이 1클릭으로 뽑고, 리더는 읽기만 합니다. 빨간 펜 3줄이 리더의 Why입니다.
동행 전 특약이 헷갈리면 특약검색기에서 코드로 지급 조건 확인, MeAI 상세 분석으로 약관 근거까지.
리포트 보내기 전 : AI 요약에 계약별 유지 · 해지 의견이 들어갈 수 있으니 구성 요소에서 AI 요약을 끄거나 지우고 보냅니다.`,
'자료: MeAI 활용 가이드북 p.59~70 · 화면은 가이드북 예시');

const Q6 = ['이번 주 가장 잘된 터치는? 왜요?', '그때 MeAI에 뭘 먼저 물어봤어요?', '고객이 멈칫한 순간은 어디였어요?', '다시 한다면 뭘 바꿔 볼래요?', 'MeAI 답 중 안 믿은 건 뭐예요? 왜요?', '다음 주 한 가지만 고른다면요?'];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:100px;text-align:center"><div class="kick y">금요일 리플레이 15분</div><div class="h1" style="margin-top:16px;font-size:80px">신인이 <span class="r">자기 대화</span>를 설명하게</div></div>
<div class="box" style="position:absolute;left:170px;right:170px;top:400px;display:grid;grid-template-columns:1fr 1fr;gap:44px 80px">
  ${Q6.map((q, i) => `<div class="row" style="gap:28px"><div style="font-size:40px;font-weight:900;color:${i === 4 ? '#FFD43B' : '#E60023'};width:70px;flex:none">Q${i + 1}</div><div style="font-size:40px;font-weight:700;letter-spacing:-0.025em">${i === 4 ? `<span class="r">${q}</span>` : q}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:96px;right:96px;top:860px;text-align:center">평가가 아니라는 말부터. <span class="w">Q5를 말할 수 있으면 검증 습관이 생긴 겁니다.</span></div>`,
`[0:44] 고능률 FP 리플레이 인터뷰 질문을 신인 코칭용으로 바꾼 6문. 한 주 리포트 2~3개를 모아 신인이 자기 대화를 설명합니다.
리더가 가르치는 시간이 아니라 신인이 자기 생각을 말하는 15분. Q5('MeAI 답 중 안 믿은 것')가 핵심입니다.`);

const BA = [['“팀장님, 이 특약 뭐예요?”', '약관 찾아보세요.', '특약검색기에 코드 쳐 보세요. 지급금액 표 캡처해서 오면, 헷갈리는 데를 그때 이야기해요.'], ['“고객이 보험료 부담돼서 정리하재요.”', '그냥 해지하고 새로 넣어 드리세요.', '맞춤대화에 월 보험료 적고 보장분석 돌려 보세요. 유지 · 보완부터, 해지 얘기는 맨 뒤.'], ['“갑상선암 보험 왜 필요하냐는데요.”', '요즘 갑상선암 많다고 하세요.', '지식 검색에서 갑상선암 통계 그래프 뽑고, [용어] 켜서 ‘초기제외’ 눌러 보세요.'], ['“생각해 본대요.”', '다음에 또 연락해 보세요.', '꼬리질문 눌러서 문안 3개 뽑아 오세요. 제가 하나 골라 드릴게요.']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:84px">같은 질문, <span class="r">다른 대답</span></div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:270px">
  <div class="row" style="padding-bottom:14px"><div style="width:520px" class="ps">신인의 질문</div><div style="width:400px" class="ps">Before</div><div class="ps y" style="flex:1">After</div></div>
  ${BA.map(([q, b, a]) => `<div class="row" style="padding:26px 0;border-top:1px solid #222326;align-items:flex-start">
    <div style="width:520px;font-size:30px;font-weight:800;padding-right:30px">${q}</div>
    <div class="k" style="width:400px;font-size:26px;font-weight:500;padding-right:30px">${b}</div>
    <div style="flex:1;font-size:28px;font-weight:600;line-height:1.5">${a}</div></div>`).join('')}
</div>
<div class="box h4" style="position:absolute;left:96px;right:96px;top:900px;text-align:center;font-size:36px">After는 전부 <span class="y">‘찾아서 가져오세요, 그때 이야기해요’</span>로 끝납니다.</div>`,
`[0:46] Before를 먼저 읽고, After를 청중이 먼저 맞혀 보게 합니다.
리더가 더 많이 아는 게 아니라, 어디서 찾고 무엇을 믿지 말지 아는 것.`);

const RX = [['“이번 달 뭐부터 팔아요?”', '홈 [당월 영업 타겟] 그룹 + 추천 카드 9장', '“당월 타겟 그룹이 누구예요? 거기부터 해 보세요.”'], ['“질문을 어떻게 써야 할지 모르겠어요”', '질문 예시 탭 → 프롬프트 라이브러리 [실전영업]', '“쓴 질문 앞에 ‘누구에게’만 붙여 보세요.”'], ['“증권 봐도 뭐가 부족한지 몰라요”', '맞춤대화 ‘보장분석 해줘’ → 표의 ‘미가입’ 줄', '“미가입 줄 1개만 오늘 이야기해 보세요.”'], ['“고객이 보험료 부담돼서 정리하재요”', '고객 정보 ‘신규 제안 월 보험료’ 채우고 보장분석', '“해지 얘기는 맨 뒤예요. 지킬 걸 먼저 보여 드리세요.”'], ['“병 있는 고객인데 가입 돼요?”', '상품 라인업 ‘예외질환 판정’ → MeAI 상세 분석', '“판정 결과 캡처해서 오세요. 확정은 심사예요.”'], ['“생각해 본대요”', '꼬리질문 버튼 → 거절처리 프롬프트로 문안 3개', '“문안 3개 중 제가 하나 골라 드릴게요.”']];
add(`
<div class="box" style="position:absolute;left:140px;top:84px"><div class="kick y">책상에 붙이는 한 장</div><div class="h1" style="margin-top:12px;font-size:76px">신인 증상별 <span class="r">MeAI 처방전</span></div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:300px">
  <div class="row" style="padding-bottom:12px"><div style="width:520px" class="ps">신인 고민</div><div style="width:560px" class="ps">스스로 (MeAI에 시킬 것)</div><div class="ps y" style="flex:1">리더 피드백</div></div>
  ${RX.map(([a, b, c]) => `<div class="row" style="padding:19px 0;border-top:1px solid #222326">
    <div style="width:520px;font-size:27px;font-weight:800;padding-right:24px">${a}</div>
    <div style="width:560px;font-size:24px;font-weight:500;color:#C9CACD;padding-right:24px">${b}</div>
    <div style="flex:1;font-size:25px;font-weight:700;color:#FFD43B">${c}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:140px;top:930px;font-size:26px">고민 → 스스로 → 리더 피드백. <span class="w">출력해서 신인 책상에 붙여 두세요.</span></div>`,
`[0:47] 11월 처방전처럼 신인에게도 처방전이 있습니다. 고민 → MeAI에 시킬 것 → 리더 피드백.
지점장이 되면 이 한 장이 팀장들의 공통 코칭 언어가 됩니다.`);

const LANG = [['“이번 주 계약 몇 건이에요?”', '“이번 주 몇 분 만났어요? 누가 제일 반응 좋았어요?”', '결과 → 행동'], ['“OO는 벌써 3건 했는데.”', '“지난주보다 연락이 5통 늘었네요.”', '남 → 어제의 나'], ['“거절당했어요? 화법이 문제예요.”', '“거절 1건은 체결에 한 걸음. 뭐라고 했는지 같이 봐요.”', '실패 → 학습'], ['(안 나오면) 전화로 질책', '“오늘 오후 동행 되는데, 같이 갈래요?”', '질책 → 초대']];
add(`
<div class="box" style="position:absolute;left:140px;top:90px"><div class="h1" style="font-size:84px">말 한마디가<br><span class="r">사무실 온도</span>를 정합니다</div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:400px">
  ${LANG.map(([a, b, c]) => `<div class="row" style="padding:24px 0;border-top:1px solid #222326">
    <div class="k" style="width:560px;font-size:28px;font-weight:500">${a}</div>
    <div style="flex:1;font-size:32px;font-weight:700">${b}</div>
    <div class="tag" style="flex:none;margin-left:24px">${c}</div></div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:140px;top:900px">결과가 아니라 행동을 칭찬하기. <span class="w">지점장이 되면 이 말투가 지점 전체의 말투가 됩니다.</span></div>`,
`[0:49] 질책으로 끝난 날의 신인은 다음 날 안 나옵니다. 퇴근 직전 5분은 반드시 인정으로.
DO의 끝은 늘 '같이'입니다.`,
'출처: 2610 신인활동관리 매니저과정 p.37');

// ───────────── 무기와 약속 (0:50~0:55)
add(`
<div class="spot" style="left:860px;top:60px;width:1200px;height:1000px"></div>
<div style="position:absolute;left:940px;top:150px;width:900px;perspective:2400px">
  <div class="scr" style="position:relative;transform:rotateY(-10deg) rotateX(3deg);transform-origin:left center">${crop(url(path.join(W, 'cap', 'index.png')), 2880, 1800, 0, 0, 2880, 1800, 900)}</div>
</div>
<div style="position:absolute;left:0;top:0;bottom:0;width:980px;background:linear-gradient(90deg,#000 76%,rgba(0,0,0,0))"></div>
<div class="box" style="position:absolute;left:140px;top:160px;width:820px">
  <div class="kick y">영업지원도구 6종</div>
  <div class="h1" style="margin-top:20px;font-size:88px">무기는 이미<br><span class="r">여러분 손</span>에 있습니다</div>
  <div style="margin-top:44px;display:grid;grid-template-columns:1fr 1fr;gap:18px 30px">
    ${[['특약검색기', '이름 · 코드로 지급 조건 한 화면'], ['보상시뮬레이터', '질병만 누르면 보상 특약 안내'], ['상품 라인업', '가입 조건 + 예외질환 판정'], ['프롬프트 30종', 'STEP 0~7, MeAI에 붙여 넣기'], ['명패 제작기', '이름만 넣고 인쇄 1분'], ['통합치료비 시뮬', '12종을 질병 선택만으로 비교']].map(([a, b]) => `<div><div style="font-size:32px;font-weight:800">${a}</div><div class="ps" style="font-size:22px">${b}</div></div>`).join('')}
  </div>
  <div class="ps" style="margin-top:34px;font-size:24px">다 외울 필요 없습니다. <span class="w">특약검색기와 통합치료비 시뮬 둘만 먼저.</span><br><span class="y" style="white-space:nowrap">hunx11-sys.github.io/MeAI</span></div>
</div>`,
`[0:50] 세일즈혁신TF가 만든 영업지원도구 6종. 대문 하나에 여섯 개, 걱정인형 캐릭터가 안내합니다.
압축 파일은 단톡으로 공유합니다. 사실 확인은 도구, 말로 바꾸는 건 MeAI.`,
'자료: 영업지원도구 6종 사용법 (2026-09-16) · 대문 화면');

const COMBO = [['청구 설명', ['보상시뮬레이터로 지급 조건', '맞춤대화 ‘이 고객 말로 설명문’', '요약 리포트 카카오톡']], ['유병자 고객', ['상품 라인업 예외질환 판정', 'MeAI 상세 분석으로 약관 근거', '가계약 제안서 [생성하기]']], ['통합치료비 설명', ['통합치료비 시뮬 12종', '지식 검색 : 질병통계 그래프 1장', '[용어]로 ‘주요치료’ 쉬운 말']]];
add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:130px;text-align:center"><div class="h1" style="font-size:88px">도구로 <span class="y">확인</span> → MeAI로 <span class="y">말</span> → 리포트로 <span class="r">기록</span></div></div>
<div class="box" style="position:absolute;left:180px;right:180px;top:420px;display:grid;grid-template-columns:repeat(3,1fr);gap:70px">
  ${COMBO.map(([t, s]) => `<div style="border-top:3px solid #E60023;padding-top:28px"><div style="font-size:40px;font-weight:800">${t}</div>
    ${s.map((x, i) => `<div style="font-size:26px;font-weight:600;color:#C9CACD;margin-top:18px"><span style="color:#FFD43B;font-weight:800;margin-right:12px">${i + 1}</span>${x}</div>`).join('')}</div>`).join('')}
</div>
<div class="box p" style="position:absolute;left:96px;right:96px;top:860px;text-align:center">판정은 도구, 설명은 MeAI, 확정은 심사. <span class="w">신인에게는 콤보 하나씩, 주 단위로.</span></div>`,
`[0:52] 패턴은 하나. 사실 → 고객 말 → 기록. 11월 영업방향 · 상품 이슈와 같이 쓰세요.
11월 주력 담보 설명 전 1분 : 시뮬로 숫자 → MeAI 통계 그래프 → [용어]로 쉬운 말.`);

const PR = [['답변은 <span class="r">검증 후 사용</span>', '오류가 있을 수 있음. 약관 · 증권으로 확인'], ['개인정보는 입력하지 않기', '이름 · 연락처 · 주소 · 주민번호는 질문에 넣지 않음'], ['동의 없으면 보지 않기', '사전조회 동의가 없거나 철회된 고객은 막힘. 우회하지 않기'], ['자료는 밖으로 내보내지 않기', 'MeAI 답변 · 화면 캡처 · 가이드북 · 이 교안 모두. 특히 SNS 금지']];
add(`
<div class="box" style="position:absolute;left:140px;top:130px"><div class="h1" style="font-size:84px">오래 잘 쓰는 <span class="r">네 가지 약속</span></div></div>
<div class="box" style="position:absolute;left:140px;right:140px;top:340px;display:grid;grid-template-columns:1fr 1fr;gap:56px 80px">
  ${PR.map(([a, b], i) => `<div class="row" style="gap:30px;align-items:flex-start"><span class="num">${i + 1}</span><div><div style="font-size:44px;font-weight:800;letter-spacing:-0.025em">${a}</div><div class="ps" style="margin-top:6px">${b}</div></div></div>`).join('')}
</div>
<div class="box" style="position:absolute;left:140px;right:140px;top:740px;border:1px solid #2A2B2F;border-radius:20px;padding:34px 44px;text-align:center">
  <div class="kick y" style="font-size:22px">MeAI 화면 하단 안내문 원문</div>
  <div style="font-size:28px;font-weight:600;line-height:1.6;margin-top:14px;color:#D8D9DC">“MeAI의 답변은 생성형 AI를 통해 작성되어 오류가 있을 수 있으므로, 반드시 직접 근거자료를 확인하여 진위를 검증하시기 바랍니다.<br>미검증으로 인한 금융소비자보호법 등 관련 법령상 책임은 사용자에게 있습니다.”</div>
</div>`,
`[0:54] 신인에게도 첫날 읽어 주세요. 1~4번은 MeAI 화면 하단 안내문에도 있습니다.
책임은 사용자에게 있습니다. 그래서 금요일 Q5('안 믿은 답')가 중요합니다.`,
'자료: MeAI 활용 가이드북 p.85');

// ───────────── 마무리 (0:55~1:00)
add(`<div class="ctr"><div class="box">
  <div class="kick g">MeAI가 채우는 것</div>
  <div class="h1 g" style="margin-top:18px;font-size:92px">갈 곳 · 할 말 · 근거</div>
  <div class="kick" style="margin-top:90px;color:#ff4d6a">리더만 줄 수 있는 것</div>
  <div class="h1" style="margin-top:18px;font-size:110px"><span class="r">같이 할 사람</span></div>
  <div class="h2" style="margin-top:14px">출근할 명분 · 기다려 주는 시간</div>
</div></div>`,
`[0:55] 처음의 일기로 돌아갑니다. 갈 곳 · 할 말 · 물어볼 사람.
갈 곳과 할 말은 MeAI가 매일 아침 준비합니다. 같이 할 사람은 지점장만 줄 수 있습니다.`);

add(`<div class="ctr"><div class="box h1" style="font-size:100px;line-height:1.32">팀장 때 만든 루틴이,<br>지점장이 되면<br><span class="r">지점의 시스템</span>이 됩니다.</div></div>`,
`[0:56] 오늘 가져가는 무기 세 개 : 도입은 면담에서 보여 줄 한 화면, 정착은 두 벽 앞의 화면(추천 9명 · 그룹 · 꼬리질문 · 첫 5일), 코칭은 하루 30분 질문.
지점장 도전은 새로운 걸 배우는 일이 아니라, 지금 팀에서 만든 루틴을 지점 크기로 키우는 일입니다.`);

add(`
<div class="box" style="position:absolute;left:96px;right:96px;top:110px;text-align:center"><div class="kick y">내일 아침, 딱 두 마디</div></div>
<div class="box" style="position:absolute;left:96px;right:96px;top:200px;display:flex;flex-direction:column;align-items:center;gap:34px">
  <div class="bub" style="background:#fff;color:#111;font-size:64px;font-weight:800;padding:30px 60px;border-radius:60px">“동의 필요한 분, 몇 명이에요?”</div>
  <div class="bub" style="background:var(--red);color:#fff;font-size:64px;font-weight:800;padding:30px 60px;border-radius:60px">“오늘 카드는 누구부터 갈 거예요?”</div>
</div>
<div class="box" style="position:absolute;left:96px;right:96px;top:640px;text-align:center">
  <div class="h3">그리고 <span class="y">4주만</span> 기록해 보세요.</div>
  <div class="p" style="margin-top:20px">신인 활동일 · 동의 요청 수 · 금요일 리플레이 메모.<br><span class="w">그 기록이 지점장에 도전할 때 내놓을 ‘나의 육성 방식’이 됩니다.</span></div>
</div>`,
`[0:57] 내일 아침 조회에서 이 두 마디만 해 보세요. 답은 주지 말고 '찾아보세요, 그때 이야기해요'.
이번 주에는 신인(또는 팀원) 1명에게 첫 5일 미션을 출력해 주고, 금요일 15분 리플레이를 해 보세요.
팀원이 없다면 내 MeAI 홈에 먼저 물어보세요. 지점장의 루틴은 내 아침부터 시작됩니다.`);

add(`<div class="dh">2027년, 신인 3주 차의 일기</div>
<div class="ctr"><div class="box diary" style="font-size:54px">팀장님이 특약검색기에 코드를 쳐 보라고 했다. 금방 찾았다.<br>오늘 연락할 사람은 아침에 MeAI 홈에 떠 있었다.<br>“생각해 볼게요”를 들었는데, 꼬리질문으로 다음 말을 찾았다.<br>금요일에 팀장님이 내 대화를 끝까지 들어 줬다.<br><span class="y">다음 주가 기다려진다.</span></div></div>`,
`[0:58] 처음 일기의 다시 쓰기. 천천히 읽습니다.
2027년, 여러분 지점의 팀장들이 이렇게 코칭하고 있다면, 그 지점은 사람이 남는 지점입니다.`);

add(`<div class="ctr"><div class="box">
  <div class="h2" style="font-size:76px;line-height:1.5">리더는 길을 알고,<br>그 길을 가고,<br>그 길을 보여 주는 사람이다.</div>
  <div class="p" style="margin-top:40px">– 존 맥스웰 –</div>
  <div class="ps" style="margin-top:50px"><span class="y">알고</span> MeAI로 찾는 법 · <span class="y">가고</span> 동행 · <span class="y">보여 주고</span> 보여 주면 씁니다</div>
</div></div>`,
`[0:59] "A leader is one who knows the way, goes the way, and shows the way." (존 C. 맥스웰)
아는 건 MeAI에 맡기고, 같이 가고, 보여 주세요.`);

add(`<div class="ctr"><div class="box">
  <div style="font-size:150px;font-weight:900;letter-spacing:-0.045em;line-height:1.15">사람이 남는<br><span class="r">지점</span></div>
  <div class="h4" style="margin-top:60px;font-weight:600">감사합니다</div>
  <div class="p" style="margin-top:14px">세일즈혁신TF 이헌수 · 질문은 단톡으로</div>
</div></div>`,
`[1:00] 감사합니다. 2027년, 사람이 남는 지점의 지점장으로 다시 뵙길 바랍니다. 질문은 단톡으로.`);

// ───────────── 굽기
(async () => {
  const name = process.argv[5] || 'meai_leader_2611';
  const dir = path.join(OUT, name + '_slides'); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const body = S.map((s, i) => `<section class="slide">${s.h}${s.src ? `<div class="src">${s.src}</div>` : ''}<div class="foot"><span class="law">${LAW}</span><span class="pg">${i + 1}</span></div></section>`).join('\n');
  const html = `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>${CSS}</style></head><body>${body}</body></html>`;
  fs.writeFileSync(path.join(OUT, name + '.html'), html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1.5 });
  await p.goto('file://' + path.join(OUT, name + '.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
  const fontOk = await p.evaluate(() => document.fonts.check('800 40px "P"', '가'));
  const broken = await p.evaluate(() => [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src.slice(-60)));
  const over = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s, i) => {
    const R = s.getBoundingClientRect(), bad = [];
    const all = [...s.querySelectorAll('.box,.src,.foot')];
    const top = all.filter(e => !all.some(o => o !== e && o.contains(e)));
    top.forEach(e => { const r = e.getBoundingClientRect(); if (r.left < R.left + 30 || r.right > R.right - 30 || r.top < R.top + 20 || r.bottom > R.bottom - 6) bad.push('밖 ' + (e.getAttribute('class')||'').split(' ')[0] + '@' + [r.left - R.left, r.top - R.top, r.right - R.left, r.bottom - R.top].map(Math.round).join(',')); });
    for (let a = 0; a < top.length; a++) for (let c = a + 1; c < top.length; c++) { const A = top[a].getBoundingClientRect(), B = top[c].getBoundingClientRect(); if (A.left < B.right - 2 && B.left < A.right - 2 && A.top < B.bottom - 2 && B.top < A.bottom - 2) bad.push('겹침 ' + (top[a].getAttribute('class')||'').split(' ')[0] + '×' + (top[c].getAttribute('class')||'').split(' ')[0] + '@' + Math.round(A.top - R.top) + '/' + Math.round(B.top - R.top)); }
    return bad.length ? (i + 1) + ': ' + [...new Set(bad)].slice(0, 6).join(' | ') : null;
  }).filter(Boolean));
  const els = await p.$$('.slide'); const files = [];
  for (let i = 0; i < els.length; i++) { const f = path.join(dir, String(i + 1).padStart(2, '0') + '.jpg'); await els[i].screenshot({ path: f, type: 'jpeg', quality: 88 }); files.push(f); }
  await b.close();
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.title = '사람이 남는 지점 · MeAI로 준비하는 신인 도입 · 정착 · 코칭'; pres.author = '세일즈혁신TF'; pres.company = '메리츠화재'; pres.subject = '26년 대전센터 초급리더과정 3차 · 60분';
  files.forEach((f, i) => { const s = pres.addSlide(); s.background = { color: '000000' }; s.addImage({ path: f, x: 0, y: 0, w: 13.333, h: 7.5, altText: S[i].n.split('\n')[0] }); s.addNotes(S[i].n); });
  const pptx = path.join(OUT, name + '.pptx'); await pres.writeFile({ fileName: pptx });
  fs.writeFileSync(path.join(OUT, name + '_files.json'), JSON.stringify(files));
  console.log('글꼴', fontOk, '| 깨진 그림', broken.length ? broken : 0, '| 점검', over.length ? '\n' + over.join('\n') : 0, '\n| 장', files.length, '|', pptx, (fs.statSync(pptx).size / 1048576).toFixed(1) + 'MB');
})();
