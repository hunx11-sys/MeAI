// 서울중앙본부 정보미팅(월요 시사조회) 「의료보험 개혁에 나선 일본」 · 권혁준 양식(검은 바탕 · 가운데 큰 글자 · 빨간 강조 상자 · 노란 숫자 · 위 제목 밑줄)
// 내용 : 소유자 본부 단톡 시사조회(슈카월드 소개 자료) + 확인한 출처로 숫자를 바로잡음. 사진 · 영상 화면은 쓰지 않고 그래프를 새로 그림
// node build_info_japan.js <작업폴더 W> <PretendardVariable.woff2> <출력폴더> [이름]
const { build } = require('./kit');

const FONT = process.argv[3], OUT = process.argv[4];
const LAW = '내부 정보미팅용 자료로 고객 및 외부에 배포·게시할 수 없습니다. 일본 본인부담 개편은 건의 단계로 확정되지 않았습니다. 수치는 각 장의 출처를 확인하세요 [금융소비자보호법 제21조 준수목적].';

const CSS = `
:root { --yel: #FFC21A; --red: #F2131B; }
.tt { position: absolute; left: 96px; right: 96px; top: 80px; text-align: center; }
.tt .ttx { font-size: 60px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.3; }
.tt .ttl { width: 620px; height: 2px; background: #7d7d7d; margin: 26px auto 0; }
.tt .tts { font-size: 28px; font-weight: 600; color: #bdbdbd; margin-top: 24px; letter-spacing: -0.01em; }
.say { font-size: 46px; font-weight: 700; line-height: 1.8; letter-spacing: -0.02em; }
.dot { width: 24px; height: 24px; border-radius: 50%; background: #262626; }
`;

const S = [];
const add = (h, n, src) => S.push({ h, n, src });
const tt = (t, s) => `<div class="box tt"><div class="ttx">${t}</div><div class="ttl"></div>${s ? `<div class="tts">${s}</div>` : ''}</div>`;
const grid = (lit, color) => `<div style="display:grid;grid-template-columns:repeat(10,24px);gap:10px;justify-content:center">${[...Array(100)].map((_, i) => `<div class="dot" style="${i >= 100 - lit ? `background:${color};box-shadow:0 0 14px ${color}` : ''}"></div>`).join('')}</div>`;
const donut = (pct, color, label, sub) => `<div style="text-align:center">
  <div style="position:relative;width:400px;height:400px;margin:0 auto;border-radius:50%;background:conic-gradient(${color} 0 ${pct}%, #262626 ${pct}% 100%);box-shadow:0 0 120px ${color}33">
    <div style="position:absolute;inset:70px;border-radius:50%;background:#000;display:flex;flex-direction:column;align-items:center;justify-content:center">
      <div style="font-size:110px;font-weight:900;letter-spacing:-0.05em;line-height:1;color:${color}">${pct}<span style="font-size:56px">%</span></div></div></div>
  <div style="font-size:40px;font-weight:800;margin-top:34px">${label}</div><div class="ps" style="margin-top:6px">${sub}</div></div>`;

// ───────────── 0:00 표지 · 문 열기
add(`
<div style="position:absolute;right:-300px;top:50%;width:1060px;height:1060px;margin-top:-530px;border-radius:50%;background:radial-gradient(circle at 38% 38%,#ff3b3b,#c4000f 62%,#7a0008);box-shadow:0 0 260px rgba(255,20,20,.45)"></div>
<div style="position:absolute;inset:0;background:linear-gradient(90deg,#000 40%,rgba(0,0,0,.45) 72%,rgba(0,0,0,.05))"></div>
<div class="box" style="position:absolute;left:140px;top:250px;width:1100px">
  <div class="kick y">월요 시사조회 · 정보미팅</div>
  <div style="font-size:150px;font-weight:900;line-height:1.12;letter-spacing:-0.045em;margin-top:30px">의료보험 개혁에<br>나선 <span class="r">일본</span></div>
  <div style="font-size:44px;font-weight:700;color:#d8d8d8;margin-top:46px;letter-spacing:-0.02em">10년 뒤 한국, 그리고 우리 고객의 이야기</div>
</div>
<div class="box" style="position:absolute;left:140px;bottom:110px;font-size:28px;font-weight:700">서울중앙본부 · 2026년 11월</div>`,
`[0:00 · 30초] 인사. 오늘 월요 시사조회는 일본 뉴스 하나입니다. 참고 자료는 슈카월드 영상, 숫자는 일본 후생노동성 · 통계청 · 기획예산처 발표로 다시 확인했습니다.`);

add(`<div class="ctr"><div class="box say">세계에서 가장 나이 든 나라, 일본이<br><span class="r">“어르신 병원비 본인부담을 10%에서 30%로”</span><br>올리자는 이야기를 꺼냈습니다.<br><span class="y">우리와 제도가 꼭 닮은 나라의 이야기입니다.</span></div></div>`,
`[0:30] 오늘 이야기 한 줄. 일본에서 '노인 의료비 본인부담을 현역 세대와 같은 30%로'라는 건의가 나왔습니다. 아직 확정이 아니라 건의 단계라는 것도 함께 말씀드립니다.`);

// ───────────── 0:01 일본 : 얼마나 늙었나 · 얼마나 쓰나
add(`${tt('만 65세 이상 인구 비중', '100명 중 몇 명이 어르신일까')}
<div class="box" style="position:absolute;left:180px;right:180px;top:330px;display:grid;grid-template-columns:repeat(3,1fr)">
  ${[['일본', 30, '#F2131B'], ['한국', 20, '#FFC21A'], ['선진국 평균', 19, '#8c8c8c']].map(([a, n, c]) => `<div style="text-align:center">${grid(n, c)}
    <div style="font-size:110px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:36px;color:${c}">${n}<span style="font-size:56px">%</span></div>
    <div style="font-size:36px;font-weight:800;margin-top:12px">${a}</div></div>`).join('')}
</div>
<div class="box" style="position:absolute;left:96px;right:96px;top:910px;text-align:center;font-size:40px;font-weight:800"><span class="r">열 명 중 세 명이 어르신인 나라, 일본</span></div>`,
`[0:01] 점 하나가 한 사람입니다. 일본은 100명 중 30명, 한국은 20명(2024년 12월 초고령사회 진입), 선진국 평균은 19명.`,
'출처: 슈카월드 소개 자료(일본 · 선진국 평균) · 행정안전부 주민등록 인구 통계(한국 2024.12, 65세 이상 20%)');

add(`<div class="ctr"><div class="box">
  <div class="kick">2025년도 일본 의료비</div>
  <div class="y" style="font-size:250px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:30px">49.2<span style="font-size:130px">조 엔</span></div>
  <div class="h3" style="margin-top:44px">약 420조 원 · 전년보다 2.6% 증가 · 1인당 약 40만 엔</div>
  <div style="margin-top:44px;font-size:64px;font-weight:900"><span class="r">사상 최고치</span></div>
</div></div>`,
`[0:02] 일본 의료비가 1년에 49조 2천억 엔, 우리 돈 약 420조 원. 5년 연속 늘어 사상 최고입니다.
(슈카월드 화면은 '예상된다'로 소개했지만, 8월 28일 후생노동성 발표로 이미 확인된 숫자입니다.)`,
'출처: 일본 후생노동성 2025년도 개산의료비 속보(2026.8.28 발표) · 원화 환산은 슈카월드 기준');

add(`${tt('그 돈은 누가 쓸까', '일본 의료비 중 어르신이 쓰는 몫')}
<div class="box" style="position:absolute;left:260px;right:260px;top:330px;display:grid;grid-template-columns:1fr 1fr;gap:120px">
  ${donut(60, '#F2131B', '65세 이상', '전체 의료비 중')}
  ${donut(40, '#FFC21A', '그중 75세 이상만', '전체 의료비 중')}
</div>
<div class="box" style="position:absolute;left:96px;right:96px;top:930px;text-align:center;font-size:40px;font-weight:800">의료비 <span class="r">열 중 여섯</span>은 65세 이상이 씁니다</div>`,
`[0:03] 인구의 30%가 의료비의 60%를 씁니다. 그중 75세 이상만 40%.`,
'출처: 일본 후생노동성 국민의료비(연령별) · 슈카월드 소개 자료');

add(`
<div class="box" style="position:absolute;left:140px;top:250px;width:820px">
  <div class="kick">75세 이상 어르신 한 사람의 1년 의료비</div>
  <div class="y" style="font-size:250px;font-weight:900;letter-spacing:-0.05em;line-height:1;margin-top:30px">약 4<span style="font-size:140px">배</span></div>
  <div class="h3" style="margin-top:40px;font-size:48px">75세 미만의 3.8배</div>
  <div class="p" style="margin-top:22px">끌어올린 원인 하나, <span class="w">항암제 같은 고가 의약품 사용 증가</span><br>(일본 후생노동성 담당자 설명)</div>
</div>
<div class="box" style="position:absolute;right:220px;top:180px;width:560px;height:760px">
  <div style="position:absolute;bottom:90px;left:40px;width:190px;height:${Math.round(560 * 26.1 / 98.9)}px;background:#333;border-radius:14px 14px 0 0"></div>
  <div style="position:absolute;bottom:90px;left:330px;width:190px;height:560px;background:var(--red);border-radius:14px 14px 0 0;box-shadow:0 0 100px rgba(242,19,27,.5)"></div>
  <div class="h4" style="position:absolute;left:0;width:270px;text-align:center;bottom:${90 + Math.round(560 * 26.1 / 98.9) + 14}px;color:#9a9a9a">26만 1천 엔</div>
  <div class="h4" style="position:absolute;left:290px;width:270px;text-align:center;bottom:664px">98만 9천 엔</div>
  <div class="ps" style="position:absolute;left:0;width:270px;text-align:center;bottom:36px">75세 미만</div>
  <div class="ps w" style="position:absolute;left:290px;width:270px;text-align:center;bottom:36px">75세 이상</div>
</div>`,
`[0:04] 75세가 넘으면 한 사람이 1년에 98만 9천 엔, 75세 미만의 약 4배(정확히 3.8배)를 씁니다.
(슈카월드 화면에는 '65~75세 미만의 4배'로 나왔지만, 원 보도는 '75세 미만 전체'와 비교한 숫자입니다.)`,
'출처: 일본 후생노동성 2025년도 개산의료비 · 교도통신 · 지지통신 보도(2026.8)');

const PY = [[1970, 7000], [1995, 8700], [2025, 7300], [2040, 6200]];
const px = y => 120 + (y - 1970) * 20, py = v => 560 - (v - 5600) * 0.16;
add(`${tt('그런데 일하는 사람은 줄어듭니다', '일본 15~64세 인구(생산가능인구)')}
<svg style="position:absolute;left:220px;top:300px" width="1600" height="620" viewBox="0 0 1600 620">
  <defs><filter id="g" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <line x1="100" y1="580" x2="1560" y2="580" stroke="#2c2c2c" stroke-width="2"/>
  <path d="M${px(1970)} ${py(7000)} C ${px(1980)} ${py(8000)}, ${px(1988)} ${py(8700)}, ${px(1995)} ${py(8700)} C ${px(2003)} ${py(8700)}, ${px(2012)} ${py(8200)}, ${px(2025)} ${py(7300)}" stroke="#fff" stroke-width="7" fill="none" filter="url(#g)" stroke-linecap="round"/>
  <path d="M${px(2025)} ${py(7300)} C ${px(2030)} ${py(6950)}, ${px(2035)} ${py(6560)}, ${px(2040)} ${py(6200)}" stroke="#F2131B" stroke-width="7" fill="none" stroke-dasharray="16 12" filter="url(#g)" stroke-linecap="round"/>
  ${PY.map(([y, v], i) => `<circle cx="${px(y)}" cy="${py(v)}" r="13" fill="${i === 3 ? '#F2131B' : '#FFC21A'}"/>
  <text x="${px(y) + [0, 0, 26, 0][i]}" y="${py(v) + [70, -32, -30, 66][i]}" fill="${i === 3 ? '#ff4d55' : '#fff'}" font-size="40" font-weight="800" text-anchor="${['middle', 'middle', 'start', 'middle'][i]}" font-family="P">${v.toLocaleString()}만</text>
  <text x="${px(y)}" y="615" fill="#8c8c8c" font-size="26" font-weight="600" text-anchor="middle" font-family="P">${y}${i === 3 ? ' 전망' : ''}</text>`).join('')}
</svg>
<div class="box" style="position:absolute;left:880px;top:520px;font-size:30px;font-weight:700;color:#bdbdbd">30년 동안 <span class="w">-1,400만</span></div>
<div class="box" style="position:absolute;left:1340px;top:700px;font-size:30px;font-weight:700;color:#ff4d55">15년 동안 -1,100만</div>
<div class="box" style="position:absolute;left:96px;right:96px;top:950px;text-align:center;font-size:40px;font-weight:800"><span class="r">쓰는 사람은 늘고, 내는 사람은 줄고</span></div>`,
`[0:05] 정점이던 1995년 8,700만 명에서 30년 동안 1,400만 명이 줄었고, 2040년까지 15년 동안 1,100만 명이 더 줄어듭니다.
의료비는 세금과 보험료로 내는데, 내는 사람이 줄어드는 겁니다.`,
'출처: 일본 총무성 인구추계 · 국립사회보장 · 인구문제연구소 장래추계(2040) · 슈카월드 소개 자료 · 1970년은 어림값');

const CP = [['70세 미만', 30], ['70~74세', 20], ['75세 이상', 10]];
add(`${tt('일본 의료보험, 한국과 닮은 구조', '세금과 보험료로 운영하는 국민건강보험 · 병원비 중 내 돈으로 내는 몫')}
<div class="box" style="position:absolute;left:360px;right:360px;top:380px;height:500px;display:grid;grid-template-columns:repeat(3,1fr);gap:80px;align-items:end">
  ${CP.map(([a, v], i) => `<div style="text-align:center"><div class="y" style="font-size:84px;font-weight:900;letter-spacing:-0.04em">${v}%</div>
    <div style="height:${v * 11}px;margin-top:16px;background:${i === 2 ? 'var(--red)' : '#3a3a3a'};border-radius:12px 12px 0 0;${i === 2 ? 'box-shadow:0 0 90px rgba(242,19,27,.45)' : ''}"></div>
    <div style="font-size:34px;font-weight:800;margin-top:18px">${a}</div></div>`).join('')}
</div>
<div class="box" style="position:absolute;left:96px;right:96px;top:930px;text-align:center;font-size:30px;font-weight:600;color:#d0d0d0">나이가 많을수록 내 돈은 적게, 나머지는 나라가 <span class="g">(75세 이상도 소득이 많으면 20~30%)</span></div>`,
`[0:06] 일본도 우리처럼 세금과 보험료로 굴러가는 국민건강보험입니다. 일하는 세대는 30%, 70~74세는 20%, 75세 이상은 10%만 냅니다.`,
'출처: 일본 후생노동성 · 슈카월드 소개 자료');

// ───────────── 0:07 일본이 꺼낸 카드
add(`<div class="ctr"><div class="box">
  <div class="h2">그래서 일본 재무성 쪽이 꺼낸 카드</div>
  <div style="font-size:220px;font-weight:900;letter-spacing:-0.05em;line-height:1.1;margin-top:50px"><span class="r">원칙 30%</span></div>
  <div class="p" style="margin-top:40px">70세 이상도 일하는 세대와 똑같이</div>
</div></div>`,
`[0:07] 재무성 자문기구인 재정제도심의회가 '70세 이상도 가능한 한 빨리 원칙 30%'를 건의했습니다.`,
'출처: 일본 재정제도심의회(재무성 자문기구) 건의 보도(2026.4.28 · 6.26)');

const TB = [['70세 미만', '30%', '30%'], ['70~74세', '20%', '원칙 30%'], ['75세 이상', '10%', '원칙 30%'], ['70세 이상 외래 특례(본인부담 상한)', '있음', '폐지']];
add(`${tt('노인 진료비 우대를 없애자는 건의')}
<div class="box" style="position:absolute;left:260px;right:260px;top:300px">
  <div class="row" style="padding-bottom:18px;font-size:28px;font-weight:700;color:#9a9a9a"><div style="flex:1">항목</div><div style="width:300px">지금</div><div style="width:360px;padding-left:40px">재무성 쪽 건의</div></div>
  ${TB.map(([a, b, c]) => `<div class="row" style="padding:30px 0;border-top:1px solid #2c2c2c;font-size:40px;font-weight:700">
    <div style="flex:1">${a}</div><div style="width:300px;color:#bdbdbd">${b}</div><div style="width:360px;padding-left:40px;color:${c === '30%' ? '#fff' : '#FFC21A'};font-weight:900">${c}</div></div>`).join('')}
  <div style="position:absolute;right:-24px;top:50px;bottom:-12px;width:400px;border:5px solid var(--red);border-radius:10px;box-shadow:0 0 60px rgba(242,19,27,.35)"></div>
</div>`,
`[0:08] 핵심은 70~74세 20%, 75세 이상 10%를 원칙 30%로. 70세 이상에만 있던 외래 본인부담 상한 특례도 없애자는 겁니다.
연말 예산 편성 과정에서 결론을 내기로 했고, 아직 확정은 아닙니다.`,
'출처: 일본 재정제도심의회 건의 보도(2026.4.28 · 6.26) · 일본 정부 「경제재정운영 기본방침 2026」 보도 · 슈카월드 소개 자료');

add(`${tt('같은 병원비 100만 엔이라면', '75세 이상 어르신이 내 돈으로 내는 몫')}
<div class="box" style="position:absolute;left:360px;top:330px;width:760px;height:600px">
  <div style="position:absolute;bottom:90px;left:60px;width:220px;height:${Math.round(470 / 3)}px;background:#3a3a3a;border-radius:14px 14px 0 0"></div>
  <div style="position:absolute;bottom:90px;left:420px;width:220px;height:470px;background:var(--red);border-radius:14px 14px 0 0;box-shadow:0 0 100px rgba(242,19,27,.5)"></div>
  <div class="h3" style="position:absolute;left:20px;width:300px;text-align:center;bottom:${90 + Math.round(470 / 3) + 14}px;color:#bdbdbd">10만 엔</div>
  <div class="h3" style="position:absolute;left:380px;width:300px;text-align:center;bottom:574px">30만 엔</div>
  <div class="ps" style="position:absolute;left:20px;width:300px;text-align:center;bottom:36px;font-size:28px">지금 10%</div>
  <div class="ps w" style="position:absolute;left:380px;width:300px;text-align:center;bottom:36px;font-size:28px">건의대로 30%</div>
</div>
<div class="box" style="position:absolute;left:1240px;top:440px">
  <div class="y" style="font-size:260px;font-weight:900;letter-spacing:-0.05em;line-height:1">3<span style="font-size:150px">배</span></div>
  <div class="h4" style="margin-top:30px">같은 치료, 내 돈은 세 배</div>
</div>`,
`[0:09] 단순 계산 예시입니다. 병원비 100만 엔이면 지금은 10만 엔, 건의대로라면 30만 엔. 실제로는 본인부담 상한 제도가 있어 이보다 적을 수 있습니다.`,
'단순 계산 예시 (본인부담 상한 · 소득 구분은 넣지 않음)');

add(`<div class="ctr"><div class="box">
  <div class="h1" style="font-size:110px">나이가 아니라,<br><span class="r">낼 수 있는 만큼</span></div>
  <div class="p" style="margin-top:50px">일하는 세대의 부담을 덜고, 나이 대신 소득에 따라 본인부담을 정하자.<br>재무성 쪽이 내세운 원칙입니다.</div>
</div></div>`,
`[0:10] '응능부담', 나이가 아니라 부담 능력(소득)에 따라 내자는 원칙입니다.`,
'출처: 일본 재정제도심의회 건의 보도 · 슈카월드 소개 자료');

add(`<div class="ctr"><div class="box">
  <div class="h2">물론, 쉽지 않습니다.</div>
  <div style="margin-top:50px;display:flex;flex-direction:column;gap:30px;font-size:38px;font-weight:700;line-height:1.5">
    <div><span class="g">2025년 11월</span> 후생노동상 <span class="w">“일률 30%는 현실적이지 않다”</span></div>
    <div><span class="g">2026년 4월 · 6월</span> 재무성 쪽, 다시 <span class="y">“가능한 한 빨리 원칙 30%”</span></div>
    <div><span class="g">2026년 연말</span> 예산 편성 과정에서 결론</div>
  </div>
  <div style="margin-top:60px;font-size:64px;font-weight:900"><span class="r">어르신 유권자가 많은 나라에서도 꺼낼 만큼 급하다는 뜻</span></div>
</div></div>`,
`[0:11] 어르신 표가 많은 나라에서 노인 부담을 올리자는 말은 정치적으로 가장 어려운 말입니다. 그런데도 또 꺼냈다는 것, 그만큼 재정이 급하다는 뜻입니다.`,
'출처: 교도통신 보도(2025.11.11) · 일본 재정제도심의회 건의 보도(2026.4.28 · 6.26)');

add(`<div class="ctr"><div class="box">
  <div style="font-size:72px;font-weight:800;line-height:1.55;letter-spacing:-0.03em">“공적 의료보험을 지키고<br>다음 세대에 넘기려면,<br>끊임없는 개혁이 필요하다.”</div>
  <div class="p" style="margin-top:40px">– 우에노 겐이치로, 일본 후생노동상 –</div>
</div></div>`,
`[0:11] 일본 정부도 '의료보험을 지킬 수 있을지'를 공개적으로 걱정하고 있습니다.
(슈카월드 화면의 '10월 30일 발언'은 원문을 찾지 못해, 확인된 3월 국회 발언으로 바꿨습니다.)`,
'출처: 일본 참의원 후생노동위원회 소신 표명 보도(2026.3)');

// ───────────── 0:12 한국
add(`
<div class="bgn" style="left:50%;top:50%;font-size:520px;transform:translate(-50%,-50%);color:#0b0b0b">2035</div>
<div class="ctr"><div class="box h1" style="font-size:110px;line-height:1.3">그리고 이건,<br><span class="r">10년 뒤 한국</span>의 이야기입니다</div></div>`,
`[0:12] 이제 한국 이야기입니다.`);

const KR = [[2014, 12.70], [2015, 13.15], [2016, 13.53], [2017, 14.21], [2018, 14.76], [2019, 15.48], [2020, 16.39], [2021, 17.14], [2022, 18.02], [2023, 18.96], [2024, 20.0]];
const KF = [[2024, 20.0], [2030, 25.5], [2040, 34.4], [2050, 40.1], [2060, 43.8], [2070, 46.4]];
const kx = y => 100 + (y - 2014) * 25.5, ky = v => 600 - v * 10.6;
const lab = [[2014, 12.7, '12.7%', '#fff'], [2024, 20.0, '20% 초고령사회', '#FFC21A'], [2030, 25.5, '25.5%', '#fff'], [2040, 34.4, '34.4%', '#fff'], [2070, 46.4, '46.4%', '#ff4d55']];
add(`${tt('한국은 더 빨리 늙어 갑니다', '65세 이상 인구 비중 · 실선은 실제, 점선은 전망')}
<svg style="position:absolute;left:180px;top:290px" width="1640" height="660" viewBox="0 0 1640 660">
  <defs><filter id="k" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <line x1="80" y1="${ky(30)}" x2="1560" y2="${ky(30)}" stroke="#F2131B" stroke-width="3" stroke-dasharray="10 10" opacity=".8"/>
  <text x="1560" y="${ky(30) - 16}" fill="#ff4d55" font-size="28" font-weight="800" text-anchor="end" font-family="P">30% = 지금의 일본</text>
  <line x1="80" y1="610" x2="1560" y2="610" stroke="#2c2c2c" stroke-width="2"/>
  <polyline points="${KR.map(([y, v]) => `${kx(y)},${ky(v)}`).join(' ')}" stroke="#fff" stroke-width="7" fill="none" filter="url(#k)" stroke-linejoin="round" stroke-linecap="round"/>
  <polyline points="${KF.map(([y, v]) => `${kx(y)},${ky(v)}`).join(' ')}" stroke="#FFC21A" stroke-width="7" fill="none" stroke-dasharray="16 12" filter="url(#k)" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="${kx(2035)}" cy="${ky(30)}" r="22" fill="none" stroke="#F2131B" stroke-width="6" filter="url(#k)"/>
  <text x="${kx(2035) + 34}" y="${ky(30) + 56}" fill="#fff" font-size="32" font-weight="800" font-family="P">2035년 무렵</text>
  ${lab.map(([y, v, t, c]) => `<circle cx="${kx(y)}" cy="${ky(v)}" r="11" fill="${c}"/><text x="${kx(y) + (y === 2024 ? 22 : 0)}" y="${ky(v) + (y === 2024 ? 50 : -26)}" fill="${c}" font-size="32" font-weight="800" text-anchor="${y === 2070 ? 'end' : y === 2024 ? 'start' : 'middle'}" font-family="P">${t}</text>`).join('')}
  ${[2014, 2024, 2030, 2040, 2050, 2060, 2070].map(y => `<text x="${kx(y)}" y="646" fill="#8c8c8c" font-size="24" font-weight="600" text-anchor="middle" font-family="P">${y}</text>`).join('')}
</svg>`,
`[0:13] 한국은 2014년 12.7%에서 10년 만에 20%, 2024년 12월 초고령사회에 들어섰습니다. 2030년 25.5%, 2040년 34.4%. 2030년대 중반이면 지금의 일본(30%)이 됩니다.`,
'출처: 행정안전부 주민등록 인구(2014~2024) · 통계청 장래인구추계(2030~2070, 연합뉴스 그래픽) · 2035년 무렵은 2030 · 2040 전망 사이 어림');

add(`<div class="ctr"><div class="box say" style="font-size:48px">엔화라는 국제 통화를 쓰고,<br>해외에 쌓아 둔 순자산도 많은 일본조차<br><span class="r">고령인구 30% 앞에서 의료보험을 손봅니다.</span><br><span class="y">한국은 2030년 25.5%. 같은 고민이 더 일찍 올 수 있습니다.</span></div></div>`,
`[0:13] 본부 의견입니다. 일본은 국제 통화와 큰 해외 순자산을 가진 나라인데도 30%에서 손을 댑니다. 우리는 그보다 이른 시점에 같은 고민을 할 수 있습니다.`,
'※ 본부 의견 · 한국 수치는 통계청 장래인구추계');

add(`<div class="ctr"><div class="box">
  <div class="kick">언론 보도</div>
  <div style="font-size:84px;font-weight:900;line-height:1.35;letter-spacing:-0.035em;margin-top:30px">‘모두의 성장’ 821조 예산 중<br><span class="r">4050 · 직장인 · 주부</span> 몫 적었다</div>
  <div class="p" style="margin-top:44px">2027년 정부 예산안 총지출 820.9조 원, 역대 최대 (올해 본예산보다 93조 원, 12.8% 증가)</div>
  <div class="h3 y" style="margin-top:44px">나라 살림이 커져도, 우리 고객의 몫은 크지 않습니다</div>
</div></div>`,
`[0:14] 역대 최대 예산이지만, 우리 고객의 중심인 4050 · 직장인 · 주부 몫은 적다는 기사입니다.
(참고 : 같은 예산안의 총수입은 880.8조 원 전망이라 '세수 600조, 221조 적자'로 말하면 틀립니다. 그 숫자는 쓰지 않습니다.)`,
'출처: 2027년도 예산안(2026.9.1 국무회의 의결) 보도 · 기사 제목은 본부 단톡 공유 기사');

// ───────────── 0:15 우리는
add(`<div class="ctr"><div class="box h1" style="font-size:100px;line-height:1.35">그럼 우리 FP님들은<br>어떤 마음으로<br><span class="y">고객을 만나야</span> 할까요?</div></div>`,
`[0:15] 잠깐 멈추고 질문을 던집니다.`);

add(`<div class="ctr"><div class="box h1" style="font-size:104px;line-height:1.4">내가 권하지 않으면,<br>내 고객의 노후 병원비는<br><span class="r">누가 준비합니까</span></div></div>`,
`[0:15] 나라가 다 해 주는 시대는 점점 끝나 갑니다. 내가 권하지 않으면, 내 고객의 노후는 내 고객 혼자 감당해야 합니다.`);

const THREE = [['간병', '오래 살수록 길어지는 돌봄의 시간', '나라 몫이 줄어도 가족이 다 떠안지 않게'], ['실손', '내 돈으로 내는 병원비의 기본 방패', '본인부담이 오를수록 더 중요해지는 보장'], ['암', '고가 항암제가 의료비를 끌어올립니다', '치료비와 생활비를 함께 준비']];
add(`${tt('사명감으로 권할 세 가지')}
<div class="box" style="position:absolute;left:180px;right:180px;top:340px;display:grid;grid-template-columns:repeat(3,1fr);gap:80px">
  ${THREE.map(([a, b, c], i) => `<div style="text-align:center"><div class="y" style="font-size:40px;font-weight:900">0${i + 1}</div>
    <div style="font-size:170px;font-weight:900;letter-spacing:-0.05em;line-height:1.1;margin-top:10px">${i === 1 ? `<span class="r">${a}</span>` : a}</div>
    <div style="font-size:32px;font-weight:800;margin-top:40px;line-height:1.45">${b}</div><div class="ps" style="margin-top:12px;font-size:26px">${c}</div></div>`).join('')}
</div>`,
`[0:16] 사명감을 갖고 간병 · 실손 · 암을 권합시다. 오늘 일본 이야기의 세 갈래(오래 산다 · 내 돈이 늘어난다 · 고가 항암제)와 그대로 이어집니다.`);

add(`${tt('고객에게는 <span class="r">겁</span>이 아니라 <span class="y">준비</span>를')}
<div class="box" style="position:absolute;left:220px;right:220px;top:300px">
  <div class="kick y">이렇게 말해 보세요</div>
  <div class="bub" style="background:#fff;color:#111;font-size:38px;line-height:1.6;margin-top:18px;padding:34px 46px">“고객님, 일본은 어르신 병원비 본인부담을 10%에서 30%로 올리자는 이야기까지 나왔어요. 우리나라도 제도가 비슷하고 더 빨리 나이 들어 가니까, 지금 보장을 한번 같이 점검해 두시면 좋겠어요.”</div>
  <div class="kick" style="margin-top:56px;color:#ff4d55">이렇게는 말하지 않기</div>
  <div style="margin-top:16px;display:flex;flex-direction:column;gap:14px;font-size:32px;font-weight:700">
    <div><span class="k">“한국도 곧 30%가 돼요”</span> <span class="g">일본도 아직 건의 단계, 단정하면 안 됨</span></div>
    <div><span class="k">“나라 믿지 마세요”</span> <span class="g">불안을 키우는 말보다 준비를 돕는 말</span></div>
  </div>
</div>`,
`[0:17] 고객 앞에서는 공포가 아니라 준비로 말합니다. 불확실한 일을 단정해서 말하는 것은 부당권유가 될 수 있습니다(금융소비자보호법 제21조).`,
'근거: 금융소비자보호법 제21조(부당권유행위 금지 : 불확실한 사항에 대한 단정적 판단 제공 금지)');

add(`<div class="ctr"><div class="box">
  <div style="font-size:130px;font-weight:900;letter-spacing:-0.045em;line-height:1.25"><span class="r">지금 바로,</span><br><span class="r">내 고객 보장분석부터!</span></div>
  <div class="p" style="margin-top:56px">MeAI 맞춤대화 <span class="w">“보장분석 해줘”</span> 한 마디로 시작</div>
</div></div>`,
`[0:18] 오늘 상담 고객 한 분, 보장분석부터. 고맙습니다.`);

build(S, { FONT, OUT, name: process.argv[5] || 'seoul_info_japan_2611', LAW, css: CSS, title: '의료보험 개혁에 나선 일본 · 10년 뒤 한국, 그리고 우리 고객의 이야기', subject: '서울중앙본부 정보미팅(월요 시사조회) · 2026.11' });
