// 오늘의 운세 v2 · 사내 공모전 제출 PPT (10/14 「오늘의 사주」 공모전 설계도 PPT 구성을 이어받음)
//   표지 · 한 장 요약 · AS-IS · TO-BE · 사용 흐름(사주 · 타로) · v1→v2 · 전체 구조 · 계산 로직(사주 · 타로) · 저장·보내기 ·
//   추가 비용 0원 · 기대 효과 · 개인정보·사내 탑재 · 검증 · 한계·다음 단계
// 쓰는 법 : node fortune/guide/build_contest.js <cap 폴더> <Pretendard woff2> <Tossface ttf> <출력 폴더>
//   cap 폴더 = capture.js 결과 + v1 비교 캡처(v1_saju_result · v1_tarot_picked, capture_v1.js)
const path = require('path');
const [, , CAP, FONT, FACE, OUT] = process.argv;
const { img, phone, chip, panel, asset, step, head, foot, PWO, PH, build } = require('./deck_kit')({ CAP, FONT, FACE, FOOT: '오늘의 운세 v2 · 사내 공모전 제출 · 세일즈혁신TF 이헌수' });
const TAROT = n => 'file://' + path.join(__dirname, '..', 'assets', 'tarot', String(n).padStart(2, '0') + '.webp');

/* 작은 부품 */
const mini = (n, x, y, s) => phone(n, { style: `position:absolute;left:${x}px;top:${y}px;transform:scale(${s});transform-origin:top left` });
const cap = (x, y, w, n, t, d) => `<div class="fcap" style="left:${x}px;top:${y}px;width:${w}px"><b class="num">${n}</b><div><div class="ft">${t}</div><div class="fd">${d}</div></div></div>`;
const card = (cls, inner) => `<div class="card ${cls || ''}">${inner}</div>`;
const tcard = (id, name, rev) => `<div class="tcard${rev ? ' rev' : ''}"><img src="${TAROT(id)}"><span>${name}</span></div>`;

const S = [];
const add = (html, notes) => S.push({ html, notes });

/* 1 표지 */
add(`<div class="slide cover">
  <div class="cv-l">
    ${chip('사내 공모전 · 세일즈혁신TF')}
    <h1 class="ch1">오늘의 운세,<br>재미있게 고객<br>터치해요</h1>
    <p class="cv-s">이름과 생년월일만 넣으면 사주팔자와 타로가 나오고,<br>카톡 · PDF · 문자로 바로 보내는 웹 도구예요</p>
    <div class="cv-chips"><span class="info">추가 비용 0원</span><span class="gchip">서버 없음</span><span class="gchip">폐쇄망 탑재</span><span class="gchip">실제 타로 카드 78장</span></div>
    <div class="cv-meta">제작 세일즈혁신TF 이헌수 · 2026. 10. · v2</div>
  </div>
  <div class="cv-r">
    ${phone('tarot_picked', { style: 'position:absolute;right:96px;top:150px;transform:scale(.86);transform-origin:top right' })}
    ${phone('gate', { style: 'position:absolute;left:96px;top:96px' })}
  </div>
</div>`, '오늘의 운세 v2를 소개드리겠습니다. 이름과 생년월일만 넣으면 사주팔자와 타로가 나오고, 카톡과 PDF, 문자로 바로 보낼 수 있는 웹 도구입니다. 10월 14일 제출한 오늘의 사주를 사주와 타로가 함께 있는 도구로 넓히고, 디자인을 실제 타로 카드 수준으로 끌어올렸으며, 사내 웹서버와 폐쇄망에 올릴 수 있도록 다듬었습니다. 추가 비용은 여전히 0원입니다.');

/* 2 한 장 요약 */
add(`<div class="slide">${head('한 장 요약', '휴대폰 안에서 계산부터<br>보내기까지 끝나요')}
  <div class="tiles">
    <div class="tile blue"><span class="tl">추가 비용</span><b>0<small>원</small></b><span class="td">서버 · API · 구독료 · 문자비가 없어요</span></div>
    <div class="tile"><span class="tl">바깥 요청 · 저장하는 개인정보</span><b>0<small>건</small></b><span class="td">계산은 모두 휴대폰 안에서 끝나요</span></div>
    <div class="tile"><span class="tl">실제 타로 카드</span><b>78<small>장</small></b><span class="td">1909년 원판 그림 · 정역 풀이 156개</span></div>
    <div class="tile"><span class="tl">검증</span><b>40,543<small>일</small></b><span class="td">1936~2046년 엑셀 엔진과 전부 일치</span></div>
  </div>
  <div class="does"><span class="dl">하는 일</span>
    <span class="dc">이름 · 성별 · 생년월일 입력</span><i>→</i><span class="dc">사주팔자 · 오늘의 운세 · 대운</span><i>→</i><span class="dc">타로 4장 · 종합 메시지</span><i>→</i><span class="dc">PDF · 이미지 · 카톡 · 문자</span></div>
  ${foot(2)}</div>`, '한 장으로 요약하면 이렇습니다. 서버와 외부 API, 구독료, 문자 발송비가 없어 추가 비용이 0원입니다. 계산이 모두 휴대폰 안에서 끝나기 때문에 바깥으로 나가는 요청도, 저장하는 개인정보도 없습니다. 타로는 1909년 원판 그림을 쓴 실제 카드 78장이고, 사주 계산은 엑셀 엔진과 1936년부터 2046년까지 40,543일을 하루도 빠짐없이 대조해 모두 일치했습니다.');

/* 3 AS-IS */
add(`<div class="slide">${head('AS-IS · 문제점', '고객과 첫 대화를 열기가<br>생각보다 어려워요')}
  <div class="probs">
    ${card('', `${asset('💬', 'sm')}<div class="ct">첫 대화 계기가 부족해요</div><div class="cd">바로 보장 이야기를 꺼내면 고객이 부담을 느끼고, 사전조회동의까지 이어지기 어려워요</div>`)}
    ${card('', `${asset('💸', 'sm')}<div class="ct">운세 콘텐츠에 매년 비용이 들어요</div><div class="cd">고객 관리용 외부 사주 서비스에 연 약 500만원이 들고 있어요<sup>*</sup></div>`)}
    ${card('', `${asset('🔐', 'sm')}<div class="ct">고객 정보를 밖으로 보내야 해요</div><div class="cd">외부 사이트에 이름 · 생년월일을 넣는 방식은 개인정보 관리 부담이 있어요</div>`)}
    ${card('', `${asset('📮', 'sm')}<div class="ct">결과를 전하기가 번거로워요</div><div class="cd">화면을 캡처해 따로 보내야 하고, 기기마다 보이는 모양도 달라요</div>`)}
  </div>
  <p class="fn">* 공모전 제출글(2026-10-14) 기준 추정치예요</p>
  ${foot(3)}</div>`, '먼저 문제점입니다. 첫째, 고객과 첫 대화를 열 계기가 부족합니다. 처음 만나거나 오랜만에 연락하는 고객에게 바로 보장 이야기를 꺼내면 부담을 느끼고 사전조회동의 요청까지 이어지기 어렵습니다. 둘째, 고객 관리용 외부 사주 서비스에 연 약 500만원이 들고 있습니다. 셋째, 외부 사이트에 고객 이름과 생년월일을 입력하는 방식은 개인정보 관리 측면에서 부담이 있습니다. 넷째, 결과를 화면 캡처로 따로 보내야 해 번거롭습니다.');

/* 4 TO-BE */
add(`<div class="slide">${head('TO-BE · 개선 방안', '계산부터 전달까지<br>자체 도구 하나로 해결해요')}
  <div class="sols">
    ${card('', `<b class="num">1</b><div class="ct">절기를 천문 공식으로 직접 계산해요</div><div class="cd">입춘 기준 년주 · 절기 기준 월주 · 60갑자 일주 · 대운까지. 매년 살 데이터가 없어요</div>`)}
    ${card('', `<b class="num">2</b><div class="ct">오늘 일진과 사주로 운세를 만들어요</div><div class="cd">재물 · 대화 · 일 · 컨디션 점수와 문구. 같은 고객은 같은 날 늘 같은 결과예요</div>`)}
    ${card('', `<b class="num">3</b><div class="ct">실제 타로 카드로 4장을 골라요</div><div class="cd">1909년 원판 그림 78장 · 정방향과 역방향 풀이 156개 · 종합 메시지</div>`)}
    ${card('', `<b class="num">4</b><div class="ct">휴대폰 기본 기능으로 보내요</div><div class="cd">PDF · 이미지 · 카톡 공유 · 문자. 발송비가 없어요</div>`)}
    ${card('', `<b class="num">5</b><div class="ct">고객 정보가 밖으로 나가지 않아요</div><div class="cd">계산은 휴대폰 안에서만. 사내 웹서버 · 폐쇄망에도 그대로 올려요</div>`)}
    ${card('soft', `<div class="ct">문구 원칙</div><div class="cd">재미로 보는 운세 · 긍정과 중립 표현만 · 사고 · 질병 · 손해를 예언하지 않아요 · 보험 권유와 연결하지 않아요</div>`)}
  </div>
  ${foot(4)}</div>`, '개선 방안입니다. 사주 계산부터 결과 전달까지 자체 제작한 도구 하나로 해결했습니다. 첫째, 태양 위치로 절기 시각을 직접 계산해 년주, 월주, 일주와 대운을 세웁니다. 매년 갱신할 데이터가 없습니다. 둘째, 오늘 일진과 고객 사주의 관계로 네 분야 점수와 문구를 만듭니다. 셋째, v2에서는 실제 타로 카드 78장으로 4장을 골라 풀이와 종합 메시지를 줍니다. 넷째, 보내기는 휴대폰 기본 기능을 써서 발송비가 없습니다. 다섯째, 계산이 휴대폰 안에서만 일어나 고객 정보가 밖으로 나가지 않고, 사내 웹서버와 폐쇄망에도 그대로 올릴 수 있습니다. 문구는 긍정과 중립 표현만 쓰고 보험 권유와 연결하지 않습니다.');

/* 5 사용 흐름 · 사주 */
const S4 = .7, W4 = Math.round(PWO * S4), G4 = 96, X4 = 112 + (1696 - (4 * W4 + 3 * G4)) / 2, Y4 = 286, CY = Y4 + Math.round(PH * S4) + 24;
const row4 = (names) => names.map((n, k) => mini(n, X4 + k * (W4 + G4), Y4, S4)).join('');
const caps4 = (items) => items.map(([t, d], k) => cap(X4 + k * (W4 + G4), CY, W4, k + 1, t, d)).join('');
add(`<div class="slide">${head('사용 흐름 · 사주', '입력하는 순간 바로 결과가 나와요')}
  ${row4(['saju_form', 'saju_result', 'saju_fortune'])}
  <div class="shot" style="left:${X4 + 3 * (W4 + G4)}px;top:${Y4 + 40}px;width:${W4}px"><img src="${img('saju_share')}"></div>
  ${caps4([['입력', '이름 · 성별 · 생년월일 8자리'], ['사주팔자', '세 기둥 · 십신 · 오행 상생 고리'], ['오늘의 운세', '점수 · 별 · 한 줄 · 행운 · 대운'], ['저장 · 보내기', '카톡 · PDF · 문자 · 이미지']])}
  ${foot(5)}</div>`, '사주 쪽 실제 사용 흐름입니다. 이름과 성별을 고르고 생년월일 숫자 여덟 자리를 넣는 순간 결과가 나옵니다. 첫 카드는 사주 세 기둥과 십신, 오행 상생 고리이고, 두 번째 카드는 오늘의 운세 점수와 한 줄 문구, 행운 색과 숫자, 방향, 그리고 대운입니다. 마지막으로 오른쪽 같은 이미지를 카톡이나 PDF, 문자로 보냅니다.');

/* 6 사용 흐름 · 타로 */
add(`<div class="slide">${head('사용 흐름 · 타로', '카드를 섞고 4장을 고르면 풀이가 나와요')}
  ${row4(['tarot_form', 'tarot_spread', 'tarot_picked', 'tarot_sum'])}
  ${caps4([['탄생 카드', '생년월일로 나의 메이저 카드'], ['카드 섞기', '78장을 섞어 초승달로 펼쳐요'], ['4장 고르기', '한 장씩 뒤집히며 풀이가 나와요'], ['종합 메시지', '한 줄 점괘 · 카톡으로 보내기']])}
  ${foot(6)}</div>`, 'v2에서 추가된 타로 흐름입니다. 생년월일을 넣으면 나의 탄생 카드가 나오고, 카드를 섞으면 78장이 초승달 모양으로 펼쳐집니다. 마음이 가는 카드를 차례로 네 장 고르면 한 장씩 뒤집히며 풀이가 나오고, 마지막에 네 장을 묶은 종합 메시지와 함께 카톡으로 보낼 수 있습니다.');

/* 7 v1 → v2 */
const S2 = .66, W2 = Math.round(PWO * S2), H2 = Math.round(PH * S2), GA = 72, GP = 136, X2 = 112 + (1696 - (4 * W2 + 2 * GA + GP)) / 2, Y2 = 300;
const px = k => X2 + k * W2 + (k >= 1 ? GA : 0) + (k >= 2 ? GP : 0) + (k >= 3 ? GA : 0);
add(`<div class="slide">${head('v2 디자인 고도화', '같은 고객 · 같은 카드, 이렇게 달라졌어요')}
  ${mini('v1_tarot_picked', px(0), Y2, S2)}${mini('tarot_picked', px(1), Y2, S2)}${mini('v1_saju_result', px(2), Y2, S2)}${mini('saju_result', px(3), Y2, S2)}
  <i class="arr" style="left:${px(0) + W2}px;top:${Y2 + H2 / 2 - 24}px;width:${GA}px">→</i><i class="arr" style="left:${px(2) + W2}px;top:${Y2 + H2 / 2 - 24}px;width:${GA}px">→</i>
  ${[['v1 · 10/16', 0, ''], ['v2 · 10/29', 1, ' now'], ['v1 · 10/16', 2, ''], ['v2 · 10/29', 3, ' now']].map(([t, k, c]) => `<span class="ver${c}" style="left:${px(k)}px;top:${Y2 + H2 + 16}px;width:${W2}px">${t}</span>`).join('')}
  <div class="chg"><span>이모지 카드 → 1909년 원판 타로 그림 78장</span><span>카드 크게 보기</span><span>일월오봉 · 한지 바탕</span><span>오행 숫자 칸 → 상생 고리</span><span>명조 · 한자 글꼴</span><span class="keep">계산 · 문구는 그대로</span></div>
  ${foot(7)}</div>`, 'v2에서 무엇이 달라졌는지 같은 고객, 같은 카드로 비교했습니다. 왼쪽 두 화면이 타로입니다. v1은 이모지로 그린 카드였는데, v2는 1909년 라이더-웨이트-스미스 원판 그림을 크림색 테두리와 한글 이름판으로 다듬어 실제 타로 카드처럼 보입니다. 오른쪽 두 화면은 사주입니다. 오행 분포를 숫자 칸 대신 상생 고리 그림으로 보여 주고, 일월오봉과 한지 바탕, 명조 한자로 품격을 높였습니다. 계산과 문구는 v1과 한 글자도 바뀌지 않았습니다.');

/* 8 전체 구조 */
add(`<div class="slide">${head('전체 구조', '모든 계산이 휴대폰 안에서 끝나요')}
  <div class="arch"><div class="al">사용자 휴대폰 · 브라우저</div>
    <div class="mods">
      ${card('mod', `<b class="num">1</b><div class="ct">입력 화면</div><div class="cd">이름 · 성별<br>생년월일</div>`)}<i class="ar">→</i>
      <div class="eng">${card('mod', `<b class="num">2</b><div class="ct">사주 엔진</div><div class="cd">절기 시각 · 기둥 · 대운<br>십신 · 지지 관계 → 점수 · 문구</div>`)}
      ${card('mod', `<b class="num">3</b><div class="ct">타로 엔진</div><div class="cd">78장 섞기 · 정역<br>4자리 풀이 · 종합 메시지</div>`)}</div><i class="ar">→</i>
      ${card('mod', `<b class="num">4</b><div class="ct">결과 화면</div><div class="cd">기둥 · 오행 고리 · 운세<br>카드 · 풀이 · 크게 보기</div>`)}
    </div>
    <div class="outs"><span class="ol">출력</span><span class="oc"><b>PDF 저장</b>인쇄 기능 → PDF</span><span class="oc"><b>이미지</b>캔버스로 직접 그림</span><span class="oc"><b>카톡 보내기</b>휴대폰 공유창</span><span class="oc"><b>문자 보내기</b>문자 앱 열기</span></div>
  </div>
  <div class="nouse"><div class="nt">쓰지 않는 것</div>
    ${['서버 · 호스팅 비용', '사주 API · 구독료', '데이터베이스', '유료 문자 · 알림톡', '외부 글꼴 · 그림 서버', '개인정보 저장'].map(t => `<div class="nr"><span>${t}</span><b>✕</b></div>`).join('')}
  </div>
  ${foot(8)}</div>`, '전체 구조입니다. 큰 상자가 사용자의 휴대폰 브라우저이고, 모든 처리가 이 안에서 일어납니다. 입력 화면에서 받은 값이 사주 엔진과 타로 엔진으로 들어가고, 결과 화면이 이를 그립니다. 출력은 인쇄 기능을 쓴 PDF, 캔버스로 직접 그린 이미지, 휴대폰 공유창을 쓴 카톡, 문자 앱으로 나갑니다. 오른쪽처럼 서버, 외부 사주 API, 데이터베이스, 유료 문자, 외부 글꼴이나 그림 서버를 하나도 쓰지 않고 개인정보도 저장하지 않습니다.');

/* 9 계산 로직 · 사주 */
add(`<div class="slide">${head('계산 로직 · 사주', '절기를 직접 계산해 기둥을 세우고<br>네 가지 운을 매겨요')}
  <div class="fx4">
    ${card('fx', `<div class="fl">년주</div><div class="fv">입춘 기준</div><div class="cd">태양 황경 315°가 되는 순간을 계산해요. 입춘 전 출생은 전년도</div>`)}
    ${card('fx', `<div class="fl">월주</div><div class="fv">12절 기준</div><div class="cd">월간 = (년간 % 5) × 2 + 2 + 달 순서</div>`)}
    ${card('fx', `<div class="fl">일주</div><div class="fv">(율리우스일 + 49) % 60</div><div class="cd">2000-01-01 = 戊午 로 검산</div>`)}
    ${card('fx', `<div class="fl">대운</div><div class="fv">절기까지 날수 ÷ 3</div><div class="cd">양년 남 · 음년 여 순행, 10년마다 한 칸</div>`)}
  </div>
  <div class="score">
    <div class="fl">오늘의 운세 점수</div>
    <div class="eq"><span class="b0">70</span><i>+</i><span>십신</span><i>+</i><span>일지 관계</span><i>+</i><span>띠 관계 × 0.6</span><i>+</i><span>오행 보정</span><i>+</i><span>개인 변동 ±4</span></div>
    <div class="sr"><span>각 분야 55 ~ 98점</span><span>총점 = 재물 30% + 대화 25% + 일 25% + 컨디션 20%</span><span>90↑ ★5 · 82↑ ★4 · 72↑ ★3</span><span class="bl">같은 사람 · 같은 날 = 같은 결과</span></div>
  </div>
  ${foot(9)}</div>`, '사주 계산 로직입니다. 사주는 1월 1일이 아니라 절기로 해와 달이 바뀝니다. 그래서 천문 공식으로 태양의 위치를 계산해 절기 시각을 직접 구합니다. 년주는 입춘, 월주는 12절을 기준으로 하고, 일주는 율리우스일에 49를 더해 60으로 나눈 나머지로 정해 2000년 1월 1일 무오일로 검산됩니다. 대운은 절기까지 날수를 3으로 나눈 나이에 시작합니다. 오늘의 운세는 기본 70점에 십신, 일지 관계, 띠 관계, 오행 보정, 개인 변동을 더해 네 분야 점수를 만들고, 가중 평균으로 총점과 별을 정합니다. 같은 사람이 같은 날 보면 늘 같은 결과가 나옵니다.');

/* 10 계산 로직 · 타로 */
add(`<div class="slide">${head('계산 로직 · 타로', '78장을 매번 새로 섞고<br>4장으로 이야기를 만들어요')}
  <div class="tc4">${tcard(10, '운명의 수레바퀴')}${tcard(48, '컵 여왕', true)}${tcard(8, '힘')}${tcard(50, '소드 에이스')}</div>
  <div class="grid6">
    ${card('', `<div class="ct">78장 · 풀이 156개</div><div class="cd">메이저 22장 + 마이너 56장(완드 · 컵 · 소드 · 펜타클 × 14) · 정방향과 역방향 풀이</div>`)}
    ${card('', `<div class="ct">공정한 무작위</div><div class="cd">섞을 때마다 보안 난수로 78장 순서를 정해요. 정방향과 역방향은 반반</div>`)}
    ${card('', `<div class="ct">4자리 스프레드</div><div class="cd">지금의 나 · 걸림돌 · 도움의 열쇠 · 다가올 흐름</div>`)}
    ${card('', `<div class="ct">탄생 카드</div><div class="cd">생년월일 숫자를 더해 22 이하가 될 때까지 다시 더해요 (22 → 0 바보)</div>`)}
    ${card('', `<div class="ct">종합 메시지</div><div class="cd">메이저 수 · 같은 수트 · 역방향 수 · 탄생 카드로 문장을 조합해요</div>`)}
    ${card('', `<div class="ct">카드 그림</div><div class="cd">1909년 라이더-웨이트-스미스 원판 (공개 저작물) · 한글 이름판</div>`)}
  </div>
  ${foot(10)}</div>`, '타로 로직입니다. 메이저 22장과 마이너 56장, 모두 78장에 정방향과 역방향 풀이 156개가 있습니다. 섞을 때마다 보안 난수로 78장 순서를 정하기 때문에 어느 위치를 눌러도 매번 새 결과가 나오고, 정방향과 역방향은 반반 확률입니다. 네 장은 지금의 나, 걸림돌, 도움의 열쇠, 다가올 흐름 자리에 놓이고, 메이저 카드 수와 같은 수트, 역방향 수, 탄생 카드가 나왔는지로 종합 메시지를 만듭니다. 카드 그림은 저작권이 끝난 1909년 원판을 씁니다.');

/* 11 저장 · 보내기 */
add(`<div class="slide">${head('저장 · 보내기', '휴대폰에 이미 있는 기능을 빌려 써서<br>비용이 없어요')}
  <div class="grid4">
    ${card('', `${asset('📄', 'sm')}<div class="ct">PDF로 저장</div><div class="cd">브라우저 인쇄 · A4 한 장 2단</div>`)}
    ${card('', `${asset('🖼️', 'sm')}<div class="ct">이미지로 저장</div><div class="cd">캔버스로 직접 그린 공유 카드</div>`)}
    ${card('', `${asset('💬', 'sm')}<div class="ct">카톡으로 보내기</div><div class="cd">휴대폰 공유창 · 이미지와 글을 함께</div>`)}
    ${card('', `${asset('✉️', 'sm')}<div class="ct">문자로 보내기</div><div class="cd">번호와 내용이 채워진 문자 앱</div>`)}
  </div>
  <p class="fn" style="top:972px">번호만으로 카톡을 직접 보내려면 알림톡(사업자 · 서버 · 건당 비용)이 필요해서 쓰지 않았어요</p>
  ${panel(1000, 808)}
  <div class="share2"><figure><img src="${img('saju_share')}"><figcaption>사주 이미지</figcaption></figure><figure><img src="${img('tarot_share')}"><figcaption>타로 이미지</figcaption></figure></div>
  ${foot(11)}</div>`, '저장과 보내기입니다. 네 가지 모두 휴대폰에 이미 있는 기능을 빌려 써서 비용이 들지 않습니다. PDF는 브라우저 인쇄 기능으로 A4 한 장에 정리되고, 이미지는 외부 캡처 도구 없이 캔버스에 직접 그립니다. 카톡 보내기는 휴대폰 공유창을 열어 이미지와 글을 함께 넘기고, 문자는 번호와 내용이 채워진 채 문자 앱이 열립니다. 오른쪽이 실제로 고객에게 가는 사주와 타로 이미지입니다. 번호만으로 카톡을 바로 보내는 알림톡은 사업자 등록과 서버, 건당 비용이 들어 쓰지 않았습니다.');

/* 12 추가 비용 0원 */
add(`<div class="slide blue">${head('추가 비용', '만들 때도, 쓸 때도 0원이에요')}
  <div class="zero">
    ${[['서버 · 호스팅', '휴대폰 안에서 계산 · 사내 웹서버엔 정적 파일만'], ['사주 API · 만세력 데이터', '천문 공식으로 직접 계산'], ['알림톡 · 문자 발송비', '사용자 카톡 공유 · 문자 앱'], ['글꼴 · 카드 그림', '무료 공개 글꼴 · 1909년 공개 저작물 그림'], ['매년 데이터 갱신', '절기 자동 계산이라 필요 없음']].map(([t, d]) => `<div class="zr"><b>${t}</b><span>${d}</span><em>0원</em></div>`).join('')}
  </div>
  <p class="zfn">배포는 파일을 그대로 전달하거나, 사내 웹서버에 폴더째 올려 링크로 나눠요</p>
  ${foot(12)}</div>`, '가장 강조드리고 싶은 부분입니다. 이 도구는 만들 때도, 운영할 때도 추가 비용이 0원입니다. 보통 이런 도구는 서버와 호스팅, 사주 API나 만세력 데이터, 알림톡과 문자 발송비, 유료 글꼴과 그림, 매년 데이터 갱신에 돈이 듭니다. 이 도구는 계산을 휴대폰 안에서 하고, 절기를 천문 공식으로 계산하며, 사용자의 카톡 공유와 문자 앱을 쓰고, 무료 공개 글꼴과 저작권이 끝난 1909년 카드 그림을 써서 다섯 가지 모두 0원입니다.');

/* 13 기대 효과 */
add(`<div class="slide">${head('기대 효과', '비용은 줄이고<br>고객 접점은 늘려요')}
  <div class="eff">
    <div class="q1"><div class="fl">정량 효과 · 연환산</div><div class="big">연 약 <b>500</b>만원 절감<sup>*</sup></div>
      <div class="qr"><span>A</span><div><b>외부 사주 콘텐츠 비용 대체</b><em>연 약 500만원 → 0원</em></div></div>
      <div class="qr"><span>B</span><div><b>추가 운영 비용</b><em>서버 · API · 발송비 · 데이터 갱신 0원</em></div></div>
      <div class="meas"><b>시범 운영에서 잴 것</b> 사용 건수 · 사전조회동의 요청과 획득 · 설계사 설문</div>
      <p class="qfn">* 공모전 제출글(10/14) 기준 추정치예요. 사전조회동의 증가 효과는 근거가 없어 금액에 넣지 않았어요</p>
    </div>
    <div class="q2"><div class="fl">정성 효과</div>
      ${step(1, '대화가 부드럽게 시작돼요', '「오늘 운세 한번 보실래요?」로 가볍게 말을 걸어요')}
      ${step(2, '고객 접점이 늘어요', '생일 · 명절 · 연초에 운세 카드를 보내요')}
      ${step(3, '개인정보가 안전해요', '저장하거나 밖으로 보내지 않아요')}
      ${step(4, '누구나 바로 써요', '설치 없이 휴대폰 · PC 에서 열려요')}
      ${step(5, '자체 기술로 넓혀요', '같은 엔진을 MeAI 홈 넛지 · 만세력 엑셀에도 써요')}
    </div>
  </div>
  ${foot(13)}</div>`, '기대 효과입니다. 정량적으로는 고객 관리용 외부 사주 콘텐츠 비용 연 약 500만원을 자체 도구로 대체해 0원으로 만들고, 서버와 API, 발송비, 데이터 갱신 같은 추가 운영 비용도 없습니다. 500만원은 10월 14일 제출글 기준 추정치이고, 사전조회동의 증가 효과는 근거가 없어 금액에 넣지 않았으며 시범 운영에서 측정하겠습니다. 정성적으로는 고객과의 대화가 부드럽게 시작되고, 생일이나 명절에 보낼 연락 거리가 생기며, 개인정보가 안전하고, 누구나 설치 없이 바로 쓸 수 있습니다. 같은 엔진을 MeAI 홈 넛지와 만세력 엑셀에도 쓰고 있어 다른 도구로 쉽게 넓힐 수 있습니다.');

/* 14 개인정보 · 사내 탑재 */
add(`<div class="slide">${head('개인정보 · 사내 탑재', '입력한 정보는<br>휴대폰 밖으로 나가지 않아요')}
  <div class="priv"><div class="nt">개인정보</div>
    ${['저장하지 않아요', '서버로 보내지 않아요', '화면을 닫으면 사라져요', '보내기는 사용자가 직접 받는 사람을 고를 때만'].map(t => `<div class="pr"><b>✓</b><span>${t}</span></div>`).join('')}
  </div>
  <div class="dep">
    ${card('', `${asset('🏢', 'sm')}<div class="ct">웹서버판</div><div class="cd">정적 파일 92개 · 2.6MB<br>사내 웹서버에 폴더째 올려요</div>`)}
    ${card('', `${asset('🪟', 'sm')}<div class="ct">포털 안에 끼우기</div><div class="cd">기존 사내 화면 안에<br>액자(iframe)로 넣어요</div>`)}
    ${card('', `${asset('💾', 'sm')}<div class="ct">한 파일판</div><div class="cd">3.5MB 파일 하나<br>폐쇄망 PC · 카톡 전달</div>`)}
  </div>
  <div class="csp"><b>가장 엄격한 보안정책(CSP)</b><span>위반 0건</span><span>바깥 요청 0건</span><span>글꼴 차단 정책에서도 정상</span></div>
  <p class="fn" style="left:780px;top:960px">탑재 패키지 : 설계도 · 소스 전체 · 검증 도구 · 서버 설정 예시(IIS · 톰캣 · nginx · 아파치) · 파일 해시</p>
  ${foot(14)}</div>`, '개인정보와 사내 탑재입니다. 입력한 이름과 생년월일은 저장하지 않고, 서버로 보내지 않으며, 화면을 닫으면 사라집니다. 보내기는 사용자가 직접 받는 사람을 고를 때만 일어납니다. v2는 사내 웹서버에 그대로 올리는 웹서버판, 기존 사내 화면에 액자로 끼우는 방식, 폐쇄망 PC나 카톡으로 전달하는 한 파일판 세 가지로 쓸 수 있습니다. 웹서버판은 가장 엄격한 보안정책을 건 시험에서 위반과 바깥 요청이 0건이었고, 설계도와 소스, 검증 도구, 서버 설정 예시를 묶은 탑재 패키지도 준비했습니다.');

/* 15 검증 */
add(`<div class="slide">${head('검증', '두 엔진을 40,543일 전부 맞춰 봤어요')}
  <div class="ver5">
    ${[['40,543일', '엑셀 엔진 vs 화면 엔진', '1936~2046년 · 년 · 월 · 일주 · 절입 · 대운 · 점수 · 문구 전부 일치'],
       ['240건', 'v1 화면 vs v2 화면', '날짜 120개 × 남녀 · 사주 결과 차이 0'],
       ['戊午 · 甲戌', '기준일 검산', '2000-01-01 · 1900-01-01 통용 만세력과 같음'],
       ['6분 · 1분', '입춘 시각 오차', '한국천문연구원 공표 대비 (2024년 · 2025년)'],
       ['0건', '보안정책 위반 · 바깥 요청', '엄격한 CSP · 포털 액자 · 글꼴 차단 · 화면 폭 320~1100px']].map(([v, t, d]) => `<div class="vr"><b>${v}</b><div><div class="vt">${t}</div><div class="vd">${d}</div></div><i>✓</i></div>`).join('')}
  </div>
  ${foot(15)}</div>`, '검증 결과입니다. 사주 계산 로직은 엑셀용 파이썬 엔진과 화면용 자바스크립트 엔진 두 벌이고, 1936년부터 2046년까지 40,543일 각각에 대해 년, 월, 일주, 절입일, 남녀 대운, 점수, 문구를 모두 비교해 하나도 다르지 않았습니다. 디자인을 바꾼 v2 화면도 v1 화면과 240건을 대조해 결과 차이가 없었습니다. 기준일 검산은 통용 만세력과 같고, 입춘 시각은 한국천문연구원 공표와 2024년 6분, 2025년 1분 차이입니다. 사내 탑재용 웹서버판은 가장 엄격한 보안정책에서 위반과 바깥 요청이 0건이었습니다.');

/* 16 한계 · 다음 단계 */
add(`<div class="slide">${head('한계 · 다음 단계', '알고 쓰면 더 좋아요')}
  <div class="lim"><div class="nt dark">한계</div>
    ${[['양력만 받아요', '음력 생일은 양력으로 바꿔 넣어요'], ['태어난 시간은 받지 않아요', '정오 출생으로 보고 여섯 글자로 계산해요'], ['절기 당일 출생', '시각에 따라 달라질 수 있다는 안내가 떠요'], ['카드 그림은 원판 그대로', '「죽음」 등 1909년 그림을 그대로 써요']].map(([t, d]) => `<div class="lr2"><b>${t}</b><span>${d}</span></div>`).join('')}
  </div>
  <div class="nxt"><div class="nt">다음 단계</div>
    ${step(1, '실제 기기 확인', '아이폰 · 갤럭시 · 카카오톡 앱 안에서 공유와 PDF')}
    ${step(2, '사내 웹서버 탑재', '탑재 패키지 준비 완료 · 링크로 배포')}
    ${step(3, '준법 확인', '고객에게 보여 줄 용도라면 사전 확인')}
    ${step(4, '시범 운영 측정', '사용 건수 · 사전조회동의 · 설계사 설문')}
  </div>
  ${foot(16)}</div>`, '끝으로 한계와 다음 단계입니다. 양력 생일만 받고, 태어난 시간은 받지 않아 정오 출생으로 계산하며, 절기 당일 출생자에게는 안내 문구가 나옵니다. 카드 그림은 1909년 원판을 그대로 씁니다. 다음 단계는 네 가지입니다. 실제 아이폰과 갤럭시, 카카오톡 앱 안에서 공유와 PDF를 확인하고, 준비된 탑재 패키지로 사내 웹서버에 올려 링크로 배포하며, 고객에게 보여 줄 용도라면 준법 확인을 받고, 시범 운영에서 사용 건수와 사전조회동의, 설계사 설문을 측정하겠습니다. 감사합니다.');

/* 공모전 장표 전용 디자인 (deck_kit 의 토스 토큰 위에) */
const CSS2 = `
.ch1 { margin-top: 40px; font-size: 96px; font-weight: 700; line-height: 1.18; letter-spacing: -0.035em; }
.cover .cv-s { margin-top: 32px; font-size: 30px; }
.cv-chips { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 40px; }
.gchip { display: inline-flex; align-items: center; height: 52px; padding: 0 22px; border-radius: 999px; background: var(--g100); color: var(--g700); font-size: 22px; font-weight: 600; }
.cv-meta { margin-top: 40px; font-size: 22px; font-weight: 600; color: var(--g500); }
.tiles { position: absolute; left: 112px; right: 112px; top: 400px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.tile { display: flex; flex-direction: column; padding: 36px 34px; border-radius: 28px; background: var(--g50); border: 1px solid var(--g200); min-height: 330px; }
.tile .tl { font-size: 22px; font-weight: 600; color: var(--g600); }
.tile b { margin-top: 26px; font-size: 92px; font-weight: 800; letter-spacing: -0.045em; line-height: 1; font-variant-numeric: tabular-nums; }
.tile b small { margin-left: 6px; font-size: 40px; font-weight: 700; }
.tile .td { margin-top: auto; padding-top: 24px; font-size: 23px; font-weight: 500; color: var(--g600); line-height: 1.45; }
.tile.blue { background: var(--blue); border-color: var(--blue); color: #fff; }
.tile.blue .tl, .tile.blue .td { color: rgba(255, 255, 255, .86); }
.does { position: absolute; left: 112px; right: 112px; top: 800px; display: flex; align-items: center; gap: 14px; padding: 26px 30px; border-radius: 24px; background: var(--g100); }
.does .dl { font-size: 22px; font-weight: 700; color: var(--g600); margin-right: 8px; }
.does .dc { padding: 12px 20px; border-radius: 14px; background: #fff; font-size: 23px; font-weight: 700; }
.does i { font-style: normal; font-size: 26px; color: var(--g400); }
.probs { position: absolute; left: 112px; right: 112px; top: 400px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.probs .card { min-height: 340px; }
.probs .card .cd { font-size: 24px; }
sup { font-size: .6em; color: var(--g500); }
.fn { position: absolute; left: 112px; top: 880px; font-size: 21px; font-weight: 500; color: var(--g500); }
.sols { position: absolute; left: 112px; right: 112px; top: 380px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.sols .card { position: relative; padding: 32px 32px 34px; min-height: 260px; }
.sols .card .num { position: static; margin-bottom: 18px; }
.sols .card .ct { margin-top: 0; font-size: 29px; }
.sols .card.soft { background: var(--blue50); border-color: var(--blue50); }
.sols .card.soft .ct { color: var(--blue); }
.fcap { position: absolute; display: flex; gap: 14px; align-items: flex-start; }
.fcap .num { width: 40px; height: 40px; font-size: 20px; }
.fcap .ft { font-size: 27px; font-weight: 700; letter-spacing: -0.02em; }
.fcap .fd { margin-top: 4px; font-size: 21px; font-weight: 500; color: var(--g600); line-height: 1.45; }
.arr { position: absolute; font-style: normal; text-align: center; font-size: 44px; font-weight: 700; color: var(--g400); }
.ver { position: absolute; text-align: center; font-size: 22px; font-weight: 700; color: var(--g600); }
.ver::before { content: ''; }
.ver.now { color: var(--blue); }
.chg { position: absolute; left: 112px; right: 112px; top: 940px; display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; }
.chg span { display: inline-flex; align-items: center; height: 46px; padding: 0 20px; border-radius: 999px; background: var(--g100); color: var(--g800); font-size: 21px; font-weight: 600; }
.chg span.keep { background: var(--blue50); color: var(--blue); font-weight: 700; }
.arch { position: absolute; left: 112px; top: 320px; width: 1230px; height: 680px; padding: 32px; border-radius: 32px; border: 1px solid var(--g200); background: var(--g50); }
.arch .al { font-size: 22px; font-weight: 700; color: var(--g600); }
.mods { display: flex; align-items: center; gap: 14px; margin-top: 22px; }
.mods .ar { font-style: normal; font-size: 32px; color: var(--g400); }
.mods .card.mod { width: 250px; padding: 26px 24px; }
.mods .card.mod .ct { margin-top: 14px; font-size: 26px; }
.mods .card.mod .cd { font-size: 20px; }
.mods .card.mod .num { width: 40px; height: 40px; font-size: 20px; }
.eng { display: flex; flex-direction: column; gap: 14px; }
.eng .card.mod { width: 330px; }
.outs { display: flex; align-items: center; gap: 12px; margin-top: 26px; }
.outs .ol { font-size: 22px; font-weight: 700; color: var(--g600); margin-right: 6px; }
.outs .oc { flex: 1; padding: 18px 20px; border-radius: 18px; background: #fff; border: 1px solid var(--g200); font-size: 19px; font-weight: 500; color: var(--g600); }
.outs .oc b { display: block; font-size: 23px; color: var(--g900); margin-bottom: 4px; }
.nouse { position: absolute; left: 1370px; top: 320px; width: 438px; height: 680px; padding: 34px 30px; border-radius: 32px; background: var(--g900); color: #fff; }
.nt { font-size: 26px; font-weight: 700; margin-bottom: 18px; }
.nr { display: flex; justify-content: space-between; align-items: center; padding: 18px 4px; border-bottom: 1px solid rgba(255, 255, 255, .12); font-size: 24px; font-weight: 600; }
.nr b { color: #FF8A8A; font-size: 24px; }
.fx4 { position: absolute; left: 112px; top: 400px; width: 1696px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.card.fx { padding: 30px 30px 32px; }
.fl { font-size: 22px; font-weight: 700; color: var(--g600); }
.fv { margin-top: 14px; font-size: 32px; font-weight: 800; color: var(--blue); letter-spacing: -0.02em; line-height: 1.3; }
.card.fx .cd { margin-top: 14px; font-size: 22px; }
.score { position: absolute; left: 112px; right: 112px; top: 700px; padding: 32px 36px; border-radius: 28px; background: var(--g100); }
.eq { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; margin-top: 18px; }
.eq span { padding: 12px 20px; border-radius: 14px; background: #fff; font-size: 25px; font-weight: 700; }
.eq span.b0 { background: var(--blue); color: #fff; }
.eq i { font-style: normal; font-size: 26px; font-weight: 700; color: var(--g500); }
.sr { display: flex; flex-wrap: wrap; gap: 10px 28px; margin-top: 22px; font-size: 22px; font-weight: 600; color: var(--g700); }
.sr .bl { color: var(--blue); }
.tc4 { position: absolute; right: 112px; top: 92px; display: flex; gap: 18px; }
.tcard { width: 132px; padding: 8px 8px 0; border-radius: 10px; background: linear-gradient(160deg, #fcf6e6, #ead9b2); box-shadow: 0 0 0 1px rgba(125, 95, 34, .35), 0 12px 24px rgba(25, 31, 40, .18); display: flex; flex-direction: column; align-items: center; }
.tcard img { display: block; width: 116px; height: 196px; object-fit: cover; box-shadow: 0 0 0 1px rgba(42, 31, 14, .55); }
.tcard span { height: 30px; display: flex; align-items: center; font-size: 15px; font-weight: 700; color: #2a1f0e; letter-spacing: -0.03em; white-space: nowrap; }
.tcard.rev { transform: rotate(180deg); }
.grid6 { position: absolute; left: 112px; right: 112px; top: 400px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.grid6 .card { padding: 32px; min-height: 250px; }
.grid6 .card .ct { margin-top: 0; font-size: 30px; }
.share2 { position: absolute; left: 1000px; top: 64px; width: 808px; height: 952px; display: flex; align-items: center; justify-content: center; gap: 28px; }
.share2 figure { margin: 0; width: 340px; display: flex; flex-direction: column; align-items: center; gap: 16px; }
.share2 img { width: 340px; border-radius: 20px; box-shadow: 0 24px 48px rgba(25, 31, 40, .16), 0 0 0 1px rgba(25, 31, 40, .06); }
.share2 figcaption { font-size: 21px; font-weight: 600; color: var(--g500); }
.slide.blue { background: var(--blue); color: #fff; }
.slide.blue .chip { background: rgba(255, 255, 255, .16); color: #fff; }
.slide.blue .foot { color: rgba(255, 255, 255, .7); }
.zero { position: absolute; left: 112px; right: 112px; top: 330px; display: flex; flex-direction: column; gap: 14px; }
.zr { display: grid; grid-template-columns: 520px 1fr 140px; align-items: center; padding: 26px 36px; border-radius: 22px; background: rgba(255, 255, 255, .12); }
.zr b { font-size: 32px; font-weight: 700; }
.zr span { font-size: 24px; font-weight: 500; color: rgba(255, 255, 255, .85); }
.zr em { font-style: normal; text-align: right; font-size: 40px; font-weight: 800; }
.zfn { position: absolute; left: 112px; top: 960px; font-size: 22px; font-weight: 500; color: rgba(255, 255, 255, .85); }
.eff { position: absolute; left: 112px; right: 112px; top: 380px; display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
.q1 { padding: 38px 40px; border-radius: 32px; background: var(--g50); border: 1px solid var(--g200); }
.big { margin-top: 16px; font-size: 48px; font-weight: 800; letter-spacing: -0.03em; }
.big b { color: var(--blue); font-size: 80px; }
.qr { display: flex; gap: 18px; align-items: center; margin-top: 22px; }
.qr > span { width: 44px; height: 44px; border-radius: 14px; background: var(--blue50); color: var(--blue); font-size: 22px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex: none; }
.qr b { display: block; font-size: 26px; font-weight: 700; }
.qr em { display: block; font-style: normal; margin-top: 2px; font-size: 22px; font-weight: 500; color: var(--g600); }
.meas { margin-top: 26px; padding: 18px 22px; border-radius: 18px; background: #fff; border: 1px solid var(--g200); font-size: 21px; font-weight: 500; color: var(--g700); line-height: 1.5; }
.meas b { color: var(--g900); margin-right: 8px; }
.qfn { margin-top: 18px; font-size: 18px; font-weight: 500; color: var(--g500); line-height: 1.5; }
.q2 { display: flex; flex-direction: column; gap: 22px; padding: 38px 40px; border-radius: 32px; border: 1px solid var(--g200); }
.q2 .st { font-size: 28px; } .q2 .sd { font-size: 22px; margin-top: 2px; }
.q2 .num { width: 42px; height: 42px; font-size: 21px; }
.priv { position: absolute; left: 112px; top: 400px; width: 620px; padding: 36px 34px 26px; border-radius: 32px; background: var(--g900); color: #fff; }
.pr { display: flex; gap: 16px; align-items: center; padding: 18px 0; border-bottom: 1px solid rgba(255, 255, 255, .12); font-size: 25px; font-weight: 600; line-height: 1.4; }
.pr b { color: #5DE09E; font-size: 26px; }
.dep { position: absolute; left: 780px; right: 112px; top: 400px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.dep .card { padding: 30px; min-height: 300px; }
.dep .card .ct { font-size: 28px; }
.dep .card .cd { font-size: 22px; }
.csp { position: absolute; left: 780px; right: 112px; top: 740px; display: flex; flex-wrap: wrap; align-items: center; gap: 12px; padding: 24px 28px; border-radius: 24px; background: var(--blue50); }
.csp b { font-size: 24px; color: var(--blue); margin-right: 10px; }
.csp span { padding: 10px 18px; border-radius: 999px; background: #fff; font-size: 21px; font-weight: 700; color: var(--g800); }
.ver5 { position: absolute; left: 112px; right: 112px; top: 330px; display: flex; flex-direction: column; gap: 14px; }
.vr { display: grid; grid-template-columns: 320px 1fr 60px; align-items: center; gap: 24px; padding: 24px 34px; border-radius: 24px; background: #fff; border: 1px solid var(--g200); }
.vr > b { font-size: 46px; font-weight: 800; color: var(--blue); letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
.vt { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; }
.vd { margin-top: 4px; font-size: 22px; font-weight: 500; color: var(--g600); }
.vr > i { font-style: normal; width: 48px; height: 48px; border-radius: 50%; background: #03B26C; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 800; }
.lim { position: absolute; left: 112px; top: 330px; width: 820px; }
.nt.dark { color: var(--g900); }
.lr2 { padding: 24px 28px; margin-bottom: 14px; border-radius: 22px; background: var(--g50); border: 1px solid var(--g200); }
.lr2 b { display: block; font-size: 28px; font-weight: 700; }
.lr2 span { display: block; margin-top: 6px; font-size: 22px; font-weight: 500; color: var(--g600); }
.nxt { position: absolute; left: 1000px; right: 112px; top: 330px; display: flex; flex-direction: column; gap: 28px; padding: 36px 38px; border-radius: 32px; background: var(--blue50); }
.nxt .nt { color: var(--blue); margin-bottom: 0; }
`;

build(S, { OUT, name: 'unse_v2_contest', title: '오늘의 운세 v2 · 사내 공모전', subject: '오늘의 운세 v2 (사주팔자 · 타로) 사내 공모전 제출 설계도', extraCss: CSS2 });
