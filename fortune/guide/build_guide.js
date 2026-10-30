// 오늘의 운세 사용 가이드 PPT · 토스(TDS) 시각 언어 · 장마다 통이미지(글꼴이 깨지지 않게)
//   1) node fortune/guide/capture.js dist/unse_saju_tarot.html <cap 폴더>      실제 화면 캡처 (가상의 고객 · 고정 씨앗)
//   2) node fortune/guide/build_guide.js <cap 폴더> <Pretendard woff2> <Tossface ttf> <출력 폴더>
//      → <출력>/slides/NN.png (3840x2160) · unse_v2_guide.pptx · unse_v2_guide.pdf
// 글꼴 : Pretendard (npm pack pretendard@1.3.9, OFL) · 그림 글자 : 토스페이스 (github.com/toss/tossface, 판매 금지 · 자유 사용)
const { chromium } = require('playwright');
const pptxgen = require('pptxgenjs');
const fs = require('fs'), path = require('path');
const [, , CAP, FONT, FACE, OUT] = process.argv;
const R = JSON.parse(fs.readFileSync(path.join(CAP, 'rects.json'), 'utf8'));
const img = n => 'file://' + path.join(CAP, n + '.png');
const DATE = '2026년 10월';

/* ---------- 부품 ---------- */
const PW = 360, SC = PW / 390;                      // 휴대폰 화면 폭 · 캡처(390px) 대비 배율
function phone(n, opt) {
  opt = opt || {};
  const marks = (opt.marks || []).map(([key, num, dx, dy]) => {
    const r = R[n][key]; const x = 12 + (r[0] + (dx || 0)) * SC, y = 12 + (r[1] + (dy || 0)) * SC;
    return `<b class="mk" style="left:${x - 22}px;top:${y - 22}px">${num}</b>`;
  }).join('');
  return `<div class="phone" style="${opt.style || ''}"><div class="scr"><img src="${img(n)}"></div><i class="isl"></i>${marks}</div>`;
}
const chip = t => `<span class="chip">${t}</span>`;
const PH = Math.round(PW * 844 / 390) + 24, PWO = PW + 24;           // 휴대폰 바깥 크기
const panel = (x, w) => `<div class="panel" style="left:${x}px;width:${w}px"></div>`;
const at1 = () => `position:absolute;left:${1000 + (808 - PWO) / 2}px;top:${64 + (952 - PH) / 2}px`;       // 오른쪽 판 가운데
const at2 = k => `position:absolute;left:${840 + (968 - 2 * PWO - 48) / 2 + k * (PWO + 48)}px;top:${64 + (952 - PH) / 2}px`;  // 넓은 판에 둘
const asset = (e, cls) => `<span class="asset ${cls || ''}">${e}</span>`;
const step = (n, t, d) => `<div class="step"><b class="num">${n}</b><div><div class="st">${t}</div>${d ? `<div class="sd">${d}</div>` : ''}</div></div>`;
const head = (c, t, s) => `<div class="hd">${chip(c)}<h2 class="title">${t}</h2>${s ? `<p class="sub">${s}</p>` : ''}</div>`;
const foot = n => `<div class="foot"><span>오늘의 운세 사용 가이드</span><span>${String(n).padStart(2, '0')}</span></div>`;

/* ---------- 장표 ---------- */
const S = [];
const add = (html, notes) => S.push({ html, notes });

add(`<div class="slide cover">
  <div class="cv-l">
    ${chip('MeAI · 세일즈혁신TF')}
    <h1>오늘의 운세<br>사용 가이드</h1>
    <p class="cv-s">사주팔자와 타로로<br>고객과의 첫 대화를 가볍게 열어요</p>
    <div class="cv-m"><span class="info">생년월일만 있으면 30초면 끝나요</span><span class="meta">${DATE} · v2</span></div>
  </div>
  <div class="cv-r">
    ${phone('tarot_picked', { style: 'position:absolute;right:96px;top:150px;transform:scale(.86);transform-origin:top right' })}
    ${phone('gate', { style: 'position:absolute;left:96px;top:96px' })}
  </div>
</div>`, '오늘의 운세 사용 가이드예요. 이름과 생년월일만으로 사주팔자와 타로를 보고, 고객과 첫 대화를 가볍게 여는 도구예요. 오늘은 여는 법, 사주와 타로 보는 법, 보내는 법, 대화 예시와 지켜야 할 점을 차례로 안내해요.');

add(`<div class="slide">${head('한눈에 보기', '이름과 생년월일만 있으면<br>바로 볼 수 있어요')}
  <div class="row2">
    <div class="stats">
      <div class="stat"><b>30<small>초</small></b><span>입력부터 결과까지</span></div>
      <div class="stat"><b>0<small>원</small></b><span>이용료 · 문자 발송비 없음<br><em>휴대폰 공유창으로 보내요</em></span></div>
      <div class="stat"><b>0<small>건</small></b><span>저장하거나 보내는 개인정보<br><em>계산은 휴대폰 안에서만 해요</em></span></div>
    </div>
    <div class="duo">
      <div class="card big">${asset('☯️')}<div class="ct">사주팔자</div><div class="cd">생년월일로 타고난 기운을 봐요</div>
        <div class="tags"><span>여섯 글자</span><span>오행</span><span>오늘의 운세</span><span>대운</span></div></div>
      <div class="card big">${asset('🔮')}<div class="ct">타로점</div><div class="cd">78장 중 4장을 직접 골라요</div>
        <div class="tags"><span>실제 타로 그림</span><span>4장 풀이</span><span>종합 메시지</span></div></div>
    </div>
  </div>${foot(2)}</div>`, '이 도구는 서버나 외부 서비스 없이 휴대폰 브라우저 안에서 모두 계산해요. 그래서 이용료와 발송비가 없고, 입력한 이름과 생년월일은 어디에도 저장되거나 전송되지 않아요. 크게 사주팔자와 타로점 두 가지로 나뉘어요.');

add(`<div class="slide">${head('여는 방법', '받은 방법에 따라<br>이렇게 열어요')}
  <div class="row2 open">
    <div class="list">
      <div class="lr">${asset('💬')}<div><div class="lt">카카오톡 · 메일로 받은 파일</div><div class="ld">파일을 눌러 사파리 또는 크롬으로 열어요</div></div></div>
      <div class="lr">${asset('🏢')}<div><div class="lt">사내 링크</div><div class="ld">주소를 즐겨찾기에 넣어 두면 편해요<br><code>…/unse/#saju</code> · <code>…/unse/#tarot</code> 로 바로 가요</div></div></div>
      <div class="lr">${asset('💻')}<div><div class="lt">PC</div><div class="ld">파일을 더블클릭하면 엣지 · 크롬으로 열려요<br>인터넷 익스플로러는 엣지로 자동으로 넘어가요</div></div></div>
    </div>
    <div class="callout">${asset('📱', 'sm')}<div class="ct">아이폰 카카오톡에서 화면이 멈춰 있다면</div>
      <div class="cd">카카오톡 미리보기는 계산 기능을 막아요.<br>오른쪽 위 메뉴(⋯)에서 <b class="b">Safari로 열기</b>를 눌러 주세요.</div>
      <div class="info">인터넷이 없어도 동작해요</div></div>
  </div>${foot(3)}</div>`, '카카오톡이나 메일로 받은 파일은 눌러서 사파리나 크롬으로 열면 돼요. 사내 링크로 배포된 경우에는 주소를 즐겨찾기해 두세요. 주소 뒤에 #saju, #tarot을 붙이면 바로 해당 화면으로 가요. 아이폰 카카오톡 미리보기 화면에서는 계산이 막혀 있으니 Safari로 열기를 눌러 주세요.');

add(`<div class="slide">${head('대문', '처음 화면에서<br>무엇을 볼지 골라요')}
  ${panel(1000, 808)}${phone('gate', { style: at1(), marks: [['today', 1, -6, 4], ['saju', 2, 8, 10], ['tarot', 3, 8, 10]] })}
  <div class="steps" style="top:470px">
    ${step(1, '오늘 날짜와 일진', '오늘이 어떤 날인지 육십갑자로 보여 줘요')}
    ${step(2, '사주팔자', '생년월일로 타고난 기운 · 오늘의 운세 · 대운을 봐요')}
    ${step(3, '타로점', '78장 카드 중 4장을 직접 골라 메시지를 들어요')}
  </div>
  <div class="note" style="top:880px">한쪽에 넣은 이름 · 생년월일은 다른 쪽으로 그대로 이어져요</div>${foot(4)}</div>`, '처음 화면에는 오늘 날짜와 일진, 그리고 사주팔자와 타로점 두 개의 문이 있어요. 한쪽에서 넣은 이름과 생년월일은 다른 쪽으로 그대로 이어지니, 사주를 본 뒤 타로로 넘어가도 다시 입력할 필요가 없어요.');

add(`<div class="slide">${head('사주 ① 입력', '세 칸만 채우면<br>결과가 바로 나와요')}
  ${panel(1000, 808)}${phone('saju_form', { style: at1(), marks: [['nm', 1, 0, 0], ['gender', 2, 0, 0], ['bd', 3, 0, 0], ['pick', 4, 30, 0]] })}
  <div class="steps" style="top:440px">
    ${step(1, '이름', '비워 둬도 돼요. 저장 이미지에는 ‘고객’으로 나와요')}
    ${step(2, '성별', '대운이 흐르는 방향이 달라져요')}
    ${step(3, '생년월일 숫자 8자리', '19880321 을 치면 1988-03-21 로 바뀌며 바로 결과가 나와요')}
    ${step(4, '달력 아이콘', '달력에서 날짜를 골라도 돼요')}
  </div>
  <div class="note" style="top:912px">양력만 받아요 · 1936~2046년 · 출산 예정일도 돼요</div>${foot(5)}</div>`, '이름, 성별, 생년월일 세 칸을 채우면 돼요. 생년월일은 숫자 8자리만 치면 자동으로 하이픈이 들어가고 바로 결과가 나와요. 달력 아이콘으로 골라도 돼요. 양력 생일만 받으니 음력 생일은 양력으로 바꿔서 넣어 주세요. 오늘 이후 날짜를 넣으면 출산 예정 아기의 기운을 보여 줘요.');

add(`<div class="slide">${head('사주 ② 사주팔자 읽기', '여섯 글자와 오행으로<br>타고난 기운을 봐요')}
  ${panel(1000, 808)}${phone('saju_result', { style: at1(), marks: [['who', 1, -4, 0], ['me', 2, 0, 0], ['ohs', 3, 40, 30]] })}
  <div class="steps" style="top:440px">
    ${step(1, '띠와 여섯 글자', '년 · 월 · 일 세 기둥의 한자를 보여 줘요')}
    ${step(2, '일주가 바로 나예요', '금테 두른 기둥이 나를 뜻하는 일간이에요. 위의 이름은 십신이에요')}
    ${step(3, '오행 상생 고리', '동그라미가 클수록 많은 기운, 점선은 비어 있는 기운이에요')}
  </div>${foot(6)}</div>`, '결과 첫 카드에는 띠와 사주 여섯 글자가 나와요. 금테를 두른 일주가 나를 뜻하는 일간이에요. 아래 오행 상생 고리는 나무, 불, 흙, 쇠, 물 다섯 기운이 얼마나 있는지 동그라미 크기로 보여 주고, 점선 동그라미는 비어 있는 기운이에요. 고리 아래에 많은 기운과 비어 있는 기운을 한 줄로 정리해 줘요.');

add(`<div class="slide">${head('사주 ③ 오늘의 운세', '점수와 한 줄로<br>오늘을 가볍게 봐요')}
  ${panel(1000, 808)}${phone('saju_fortune', { style: at1(), marks: [['ring', 1, 0, 0], ['head', 2, 0, 0], ['meters', 3, 0, 0], ['lucky', 4, 0, 0], ['du', 5, 0, 0]] })}
  <div class="steps tight" style="top:400px">
    ${step(1, '점수와 별', '같은 사람이 같은 날 보면 늘 같은 결과가 나와요')}
    ${step(2, '오늘의 한 줄과 키워드', '대화를 시작하기 좋은 문장이에요')}
    ${step(3, '분야 점수', '재물 · 대화 · 일 · 컨디션')}
    ${step(4, '행운 색 · 숫자 · 방향', '내 사주에서 가장 적은 기운으로 정해요')}
    ${step(5, '대운', '10년 단위의 큰 흐름이에요. 지금 대운은 남색이에요')}
  </div>${foot(7)}</div>`, '두 번째 카드는 오늘의 운세예요. 점수와 별, 오늘의 한 줄과 키워드, 재물·대화·일·컨디션 네 분야 점수, 행운 색과 숫자와 방향이 나와요. 같은 사람이 같은 날 보면 늘 같은 결과가 나와요. 맨 아래 대운은 10년 단위 흐름이고, 지금 나이의 대운이 남색으로 표시돼요.');

add(`<div class="slide">${head('사주 ④ 저장 · 보내기', '결과를 이미지로<br>고객에게 보내요')}
  <div class="grid4">
    <div class="card">${asset('💬', 'sm')}<div class="ct">카톡으로 보내기</div><div class="cd">공유창에서 카카오톡을 고르면 이미지와 글이 함께 가요</div></div>
    <div class="card">${asset('📄', 'sm')}<div class="ct">PDF로 저장</div><div class="cd">A4 한 장으로 깔끔하게 인쇄돼요</div></div>
    <div class="card">${asset('✉️', 'sm')}<div class="ct">문자로 보내기</div><div class="cd">번호를 넣으면 문자 앱이 바로 열려요</div></div>
    <div class="card">${asset('🖼️', 'sm')}<div class="ct">이미지로 저장</div><div class="cd">1080×1350 이미지로 사진첩에 저장돼요</div></div>
  </div>
  ${panel(1000, 808)}<div class="shot" style="left:${1000 + (808 - 600) / 2}px;top:132px;width:600px"><img src="${img('saju_share')}"></div>
  <div class="cap" style="left:1000px;top:918px;width:808px">고객에게 가는 사주 이미지</div>${foot(8)}</div>`, '결과 아래에서 네 가지 방법으로 보낼 수 있어요. 카톡으로 보내기를 누르면 휴대폰 공유창이 열리고, 카카오톡을 고르면 오른쪽 같은 이미지와 글이 함께 가요. PDF는 A4 한 장으로 인쇄되고, 번호를 넣으면 문자로도 보낼 수 있어요. 발송 비용은 들지 않아요.');

add(`<div class="slide">${head('타로 ① 시작', '탄생 카드를 확인하고<br>카드를 섞어요')}
  ${panel(1000, 808)}${phone('tarot_form', { style: at1(), marks: [['form', 1, 0, 0], ['birth', 2, 0, 0], ['go', 3, 0, 0]] })}
  <div class="steps" style="top:470px">
    ${step(1, '이름 · 생년월일', '사주에서 넣었다면 그대로 이어져요')}
    ${step(2, '나의 탄생 카드', '생년월일 숫자를 더해 나오는 메이저 카드예요')}
    ${step(3, '카드 섞기', '78장을 세 번 섞어 초승달 모양으로 펼쳐요')}
  </div>${foot(9)}</div>`, '타로 화면에서 생년월일을 넣으면 나의 탄생 카드가 나와요. 생년월일 숫자를 모두 더해서 정해지는 메이저 카드예요. 카드 섞기를 누르면 78장을 세 번 섞은 뒤 초승달 모양으로 펼쳐요.');

add(`<div class="slide">${head('타로 ② 4장 고르기', '마음이 가는 카드를<br>차례로 4장 골라요')}
  ${panel(1000, 808)}${phone('tarot_spread', { style: at1() })}
  <div class="grid4 pos">
    <div class="card"><b class="rn">I</b><div class="ct">지금의 나</div><div class="cd">지금 내 마음과 상황</div></div>
    <div class="card"><b class="rn">II</b><div class="ct">걸림돌</div><div class="cd">조심하거나 넘어야 할 것</div></div>
    <div class="card"><b class="rn">III</b><div class="ct">도움의 열쇠</div><div class="cd">힘이 되는 태도 · 사람</div></div>
    <div class="card"><b class="rn">IV</b><div class="ct">다가올 흐름</div><div class="cd">이대로 가면 펼쳐질 모습</div></div>
  </div>
  <div class="note" style="top:916px">뽑을 때마다 새로 섞이고, 정방향과 역방향은 반반이에요</div>${foot(10)}</div>`, '펼쳐진 카드 중 마음이 가는 카드를 차례로 네 장 눌러요. 첫 장은 지금의 나, 둘째는 걸림돌, 셋째는 도움의 열쇠, 넷째는 다가올 흐름이에요. 카드는 뽑을 때마다 새로 섞이고, 정방향과 역방향은 반반 확률로 나와요. 역방향 카드는 실제 타로처럼 거꾸로 놓여요.');

add(`<div class="slide">${head('타로 ③ 풀이와 크게 보기', '한 장씩 뒤집히며<br>풀이가 나와요')}
  ${panel(840, 968)}${phone('tarot_reads', { style: at2(0) })}
  ${phone('tarot_zoom', { style: at2(1) })}
  <div class="steps" style="top:470px;width:640px">
    ${step(1, '풀이 카드', '자리 · 카드 이름 · 정방향/역방향 · 키워드 · 한두 문장')}
    ${step(2, '크게 보기', '카드 그림을 누르면 크게 볼 수 있어요. 고객에게 보여 주기 좋아요')}
  </div>
  <div class="note" style="top:820px;width:640px">카드 그림은 1909년 라이더-웨이트-스미스 원판이에요</div>${foot(11)}</div>`, '카드를 고를 때마다 한 장씩 뒤집히며 아래에 풀이가 나와요. 자리, 카드 이름, 정방향인지 역방향인지, 키워드와 한두 문장 풀이가 보여요. 카드 그림을 누르면 크게 볼 수 있어서 고객에게 화면을 보여 줄 때 좋아요. 카드 그림은 1909년 라이더-웨이트-스미스 원판이에요.');

add(`<div class="slide">${head('타로 ④ 종합 메시지 · 보내기', '네 장을 모아<br>오늘의 메시지를 줘요')}
  ${panel(840, 968)}${phone('tarot_sum', { style: at2(0) })}
  <div class="fitbox" style="${at2(1)};width:${PWO}px;height:${PH}px"><div class="shot fit"><img src="${img('tarot_share')}"></div><div class="cap2">고객에게 가는 타로 이미지</div></div>
  <div class="steps" style="top:470px;width:640px">
    ${step(1, '한 줄 메시지', '도움의 열쇠와 다가올 흐름 카드로 만들어요')}
    ${step(2, '카톡으로 보내기', '카드 4장과 점괘가 담긴 이미지가 함께 가요')}
    ${step(3, '다시 뽑기', '카드를 다시 모아 새로 섞어요')}
  </div>${foot(12)}</div>`, '네 장을 모두 고르면 종합 메시지가 나와요. 셋째 도움의 열쇠와 넷째 다가올 흐름 카드로 한 줄 메시지를 만들고, 메이저 카드 수, 역방향 수, 탄생 카드가 나왔는지에 따라 설명이 붙어요. 카톡으로 보내기를 누르면 오른쪽처럼 카드 네 장과 점괘가 담긴 이미지가 함께 가요.');

add(`<div class="slide">${head('대화 예시', '결과는 대화의<br>시작이에요')}
  <div class="chat">
    <div class="bb me">오늘 운세 재미로 한번 볼까요?<br>생년월일만 알려 주세요</div>
    <div class="bb you">88년 3월 21일이에요</div>
    <div class="bb me">오늘 83점이에요. ‘여유와 웃음이 따라오는 날, 좋아하는 일에 시간을 써 보세요’래요</div>
    <div class="bb you">오, 오늘 좀 여유 있긴 해요</div>
    <div class="bb me">요즘 맛있게 드신 거 있으세요?<br>추천 받고 싶어요</div>
  </div>
  <div class="steps" style="left:1072px;top:420px;width:720px">
    ${step(1, '재미로 가볍게 시작해요', '결과를 믿으라고 하지 않아요')}
    ${step(2, '한 줄을 질문으로 바꿔요', '‘여유 · 미식’ 키워드라면 요즘 즐거운 일을 물어요')}
    ${step(3, '고객 이야기를 들어요', '운세는 거들 뿐, 대화의 주인공은 고객이에요')}
  </div>${foot(13)}</div>`, '운세 결과는 대화를 여는 재료예요. 재미로 가볍게 권하고, 결과의 한 줄이나 키워드를 고객에게 묻는 질문으로 바꿔 보세요. 예를 들어 여유와 미식 키워드가 나왔다면 요즘 즐거운 일이나 맛있게 먹은 음식을 물어볼 수 있어요. 운세는 거들 뿐이고, 대화의 주인공은 고객이에요.');

add(`<div class="slide">${head('자주 묻는 질문', '이럴 땐 이렇게 하면 돼요')}
  <div class="faq">
    <div class="qa"><div class="q">음력 생일이에요</div><div class="a">양력으로 바꿔서 넣어요. 양력 생일만 받아요</div></div>
    <div class="qa"><div class="q">태어난 시간은요?</div><div class="a">받지 않아요. 정오에 태어났다고 보고 년 · 월 · 일 여섯 글자로 계산해요</div></div>
    <div class="qa"><div class="q">1~2월생인데 띠가 달라요</div><div class="a">사주는 입춘 기준이라 설날 기준 띠와 다를 수 있어요</div></div>
    <div class="qa"><div class="q">다시 보면 결과가 바뀌나요?</div><div class="a">사주는 같은 날 늘 같은 결과예요. 타로는 뽑을 때마다 새로 섞여요</div></div>
    <div class="qa"><div class="q">카톡에서 눌렀는데 안 돼요</div><div class="a">미리보기 화면이라 그래요. 오른쪽 위 메뉴에서 Safari · Chrome으로 열어요</div></div>
    <div class="qa"><div class="q">출산 예정일도 돼요?</div><div class="a">돼요. D-day와 태어날 아기의 기운을 보여 줘요</div></div>
  </div>${foot(14)}</div>`, '자주 받는 질문이에요. 음력 생일은 양력으로 바꿔서 넣어 주세요. 태어난 시간은 받지 않고 정오 출생으로 계산해요. 사주는 입춘 기준이라 1, 2월생은 설날 기준 띠와 다를 수 있어요. 사주는 같은 날 늘 같은 결과이고 타로는 매번 새로 섞여요. 카카오톡 미리보기에서는 동작하지 않으니 Safari나 Chrome으로 열어 주세요.');

add(`<div class="slide">${head('꼭 지켜 주세요', '즐겁게, 그리고<br>조심스럽게 써요')}
  <div class="rules">
    <div class="lr">${asset('🎈')}<div><div class="lt">재미로 보는 콘텐츠예요</div><div class="ld">결정의 근거로 쓰지 않아요</div></div></div>
    <div class="lr">${asset('🙅')}<div><div class="lt">보험 권유와 연결하지 않아요</div><div class="ld">운세 결과를 이유로 상품을 권하지 않아요</div></div></div>
    <div class="lr">${asset('🤝')}<div><div class="lt">불안을 주지 않아요</div><div class="ld">문구는 긍정 · 중립만 있어요. 사고 · 질병 · 손해를 예언하지 않아요</div></div></div>
    <div class="lr">${asset('🔒')}<div><div class="lt">개인정보를 남기지 않아요</div><div class="ld">저장 · 전송이 없어요. 결과 화면을 다른 곳에 공유할 때는 고객 동의를 받아요</div></div></div>
  </div>${foot(15)}</div>`, '꼭 지켜 주세요. 재미로 보는 콘텐츠라 결정의 근거로 쓰지 않아요. 운세 결과를 이유로 보험을 권하지 않아요. 문구는 긍정과 중립만 있고 사고나 질병, 손해를 예언하지 않아요. 도구는 개인정보를 저장하거나 전송하지 않지만, 결과 화면을 다른 곳에 공유할 때는 고객 동의를 받아 주세요.');

add(`<div class="slide end">
  ${asset('✨', 'hero')}
  <h2 class="title">생년월일 하나로<br>대화를 열어 보세요</h2>
  <div class="flow"><span><b>1</b>열기</span><i></i><span><b>2</b>사주 · 타로 고르기</span><i></i><span><b>3</b>보내기</span></div>
  <p class="sub">문의 · 세일즈혁신TF 이헌수</p>
  ${foot(16)}</div>`, '정리하면 열고, 사주나 타로를 고르고, 결과를 보내면 끝이에요. 생년월일 하나로 고객과의 대화를 가볍게 열어 보세요. 궁금한 점은 세일즈혁신TF로 문의해 주세요.');

/* ---------- 디자인 (토스 TDS 토큰) ---------- */
const CSS = `
@font-face { font-family: "Pretendard Variable"; src: url("file://${FONT}") format("woff2-variations"); font-weight: 45 920; }
@font-face { font-family: "Tossface"; src: url("file://${FACE}"); }
:root { --blue: #3182F6; --blue50: #E8F3FF; --g900: #191F28; --g800: #333D4B; --g700: #4E5968; --g600: #6B7684; --g500: #8B95A1; --g400: #B0B8C1; --g200: #E5E8EB; --g100: #F2F4F6; --g50: #F9FAFB; }
* { box-sizing: border-box; margin: 0; }
body { background: #ddd; font-family: "Pretendard Variable", "Tossface", sans-serif; color: var(--g900); word-break: keep-all; }
.slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #fff; margin: 0 0 20px; }
.hd { position: absolute; left: 112px; top: 96px; }
.chip { display: inline-flex; align-items: center; height: 46px; padding: 0 22px; border-radius: 999px; background: var(--g100); color: var(--g700); font-size: 22px; font-weight: 600; }
.title { margin-top: 28px; font-size: 64px; font-weight: 700; line-height: 1.28; letter-spacing: -0.03em; }
.sub { margin-top: 18px; font-size: 28px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.panel { position: absolute; top: 64px; height: 952px; border-radius: 48px; background: var(--g100); }
.foot { position: absolute; left: 112px; right: 112px; bottom: 44px; display: flex; justify-content: space-between; font-size: 18px; font-weight: 600; color: var(--g500); letter-spacing: -0.01em; }
.asset { display: inline-flex; align-items: center; justify-content: center; width: 96px; height: 96px; border-radius: 26px; background: var(--g100); font-family: "Tossface"; font-size: 56px; line-height: 1; flex: none; }
.asset.sm { width: 76px; height: 76px; border-radius: 22px; font-size: 44px; }
.info { display: inline-flex; align-items: center; height: 52px; padding: 0 24px; border-radius: 999px; background: var(--blue50); color: var(--blue); font-size: 24px; font-weight: 700; }
.b { color: var(--blue); font-weight: 700; }
/* 휴대폰 */
.phone { position: absolute; width: ${PW + 24}px; padding: 12px; border-radius: 62px; background: #191F28; box-shadow: 0 40px 80px rgba(25, 31, 40, .16), 0 8px 24px rgba(25, 31, 40, .10); }
.phone .scr { width: ${PW}px; height: ${Math.round(PW * 844 / 390)}px; border-radius: 50px; overflow: hidden; background: #000; }
.phone .scr img { display: block; width: 100%; height: 100%; }
.phone .isl { position: absolute; left: 50%; top: 22px; width: 92px; height: 26px; margin-left: -46px; border-radius: 16px; background: #000; }
.mk { position: absolute; width: 44px; height: 44px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 22px; font-weight: 700; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 4px #fff, 0 6px 16px rgba(49, 130, 246, .35); z-index: 3; }
/* 단계 목록 */
.steps { position: absolute; left: 112px; width: 820px; display: flex; flex-direction: column; gap: 34px; }
.steps.tight { gap: 24px; }
.step { display: flex; gap: 24px; align-items: flex-start; }
.num { flex: none; width: 48px; height: 48px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 24px; font-weight: 700; display: flex; align-items: center; justify-content: center; margin-top: 2px; }
.st { font-size: 34px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.35; }
.sd { margin-top: 6px; font-size: 25px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.note { position: absolute; left: 112px; display: inline-flex; align-items: center; min-height: 64px; padding: 14px 28px; border-radius: 20px; background: var(--g100); color: var(--g700); font-size: 24px; font-weight: 600; line-height: 1.45; }
/* 표지 */
.cover .cv-l { position: absolute; left: 112px; top: 120px; width: 760px; }
.cover h1 { margin-top: 40px; font-size: 112px; font-weight: 700; line-height: 1.16; letter-spacing: -0.035em; }
.cover .cv-s { margin-top: 36px; font-size: 36px; font-weight: 500; color: var(--g700); line-height: 1.5; letter-spacing: -0.015em; }
.cover .cv-m { position: absolute; top: 760px; display: flex; flex-direction: column; gap: 26px; align-items: flex-start; }
.cover .meta { font-size: 22px; font-weight: 600; color: var(--g500); }
.cover .cv-r { position: absolute; right: 96px; top: 64px; width: 880px; height: 952px; border-radius: 48px; background: var(--g100); overflow: hidden; }
.cover .asset.float { position: absolute; left: 40px; bottom: 40px; background: #fff; box-shadow: 0 8px 24px rgba(25, 31, 40, .08); }
/* 한눈에 */
.row2 { position: absolute; left: 112px; right: 112px; top: 420px; display: grid; grid-template-columns: 1fr 1.1fr; gap: 64px; }
.stats { display: flex; flex-direction: column; gap: 22px; }
.stat { display: grid; grid-template-columns: 200px 1fr; align-items: center; gap: 24px; padding: 28px 32px; border-radius: 28px; background: var(--g50); border: 1px solid var(--g200); }
.stat b { font-size: 84px; font-weight: 800; color: var(--blue); letter-spacing: -0.04em; line-height: 1; font-variant-numeric: tabular-nums; }
.stat b small { font-size: 40px; font-weight: 700; margin-left: 4px; color: var(--g900); }
.stat span { font-size: 28px; font-weight: 700; line-height: 1.4; }
.stat em { font-style: normal; font-size: 22px; font-weight: 500; color: var(--g600); }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.card { padding: 36px 32px; border-radius: 28px; background: #fff; border: 1px solid var(--g200); box-shadow: 0 4px 12px rgba(25, 31, 40, .04); }
.card .ct { margin-top: 22px; font-size: 32px; font-weight: 700; letter-spacing: -0.02em; }
.card .cd { margin-top: 10px; font-size: 24px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.tags { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
.tags span { height: 42px; padding: 0 18px; border-radius: 999px; background: var(--g100); color: var(--g700); font-size: 20px; font-weight: 600; display: inline-flex; align-items: center; }
/* 여는 방법 · 지켜 주세요 */
.list, .rules { display: flex; flex-direction: column; gap: 18px; }
.lr { display: flex; gap: 28px; align-items: center; padding: 26px 32px; border-radius: 28px; background: #fff; border: 1px solid var(--g200); }
.lt { font-size: 32px; font-weight: 700; letter-spacing: -0.02em; }
.ld { margin-top: 6px; font-size: 23px; font-weight: 500; color: var(--g600); line-height: 1.5; }
.ld code { font-family: inherit; font-weight: 700; color: var(--g800); background: var(--g100); padding: 2px 10px; border-radius: 8px; }
.open { top: 400px; grid-template-columns: 1.15fr .85fr; }
.callout { padding: 40px; border-radius: 32px; background: var(--g100); display: flex; flex-direction: column; align-items: flex-start; }
.callout .ct { margin-top: 24px; font-size: 32px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.35; }
.callout .cd { margin-top: 14px; font-size: 25px; font-weight: 500; color: var(--g700); line-height: 1.6; }
.callout .info { margin-top: 32px; }
.rules { position: absolute; left: 112px; right: 112px; top: 420px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
/* 2x2 카드 */
.grid4 { position: absolute; left: 112px; top: 396px; width: 840px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.grid4 .card { padding: 30px 32px; }
.grid4 .card .ct { margin-top: 18px; font-size: 30px; }
.grid4.pos { left: 112px; top: 384px; width: 820px; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid4.pos .card { padding: 28px 30px 30px; }
.rn { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 20px; background: var(--blue50); color: var(--blue); font-size: 26px; font-weight: 800; letter-spacing: 0.02em; }
.grid4.pos .card .ct { margin-top: 20px; font-size: 32px; }
.shot { position: absolute; border-radius: 28px; overflow: hidden; box-shadow: 0 30px 60px rgba(25, 31, 40, .16), 0 0 0 1px rgba(25, 31, 40, .06); }
.shot img { display: block; width: 100%; }
.fitbox { display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 22px; }
.shot.fit { position: relative; width: 100%; border-radius: 24px; }
.cap2 { font-size: 22px; font-weight: 600; color: var(--g500); }
.cap { position: absolute; text-align: center; font-size: 22px; font-weight: 600; color: var(--g500); }
/* 대화 */
.chat { position: absolute; left: 112px; top: 384px; width: 860px; height: 600px; padding: 28px 40px; border-radius: 36px; background: var(--g50); border: 1px solid var(--g200); display: flex; flex-direction: column; gap: 14px; }
.bb { max-width: 620px; padding: 16px 26px; font-size: 25px; font-weight: 500; line-height: 1.5; letter-spacing: -0.01em; }
.bb.me { align-self: flex-end; background: var(--blue); color: #fff; border-radius: 26px 26px 6px 26px; }
.bb.you { align-self: flex-start; background: var(--g200); color: var(--g900); border-radius: 26px 26px 26px 6px; }
/* 질문 */
.faq { position: absolute; left: 112px; right: 112px; top: 330px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.qa { padding: 36px 34px; border-radius: 28px; background: #fff; border: 1px solid var(--g200); min-height: 250px; }
.q { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.4; }
.q::before { content: 'Q'; display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; margin-right: 14px; border-radius: 12px; background: var(--blue50); color: var(--blue); font-size: 22px; font-weight: 800; vertical-align: 3px; }
.a { margin-top: 18px; font-size: 25px; font-weight: 500; color: var(--g600); line-height: 1.55; }
/* 마무리 */
.end { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.end .asset.hero { width: 140px; height: 140px; border-radius: 40px; font-size: 84px; margin-bottom: 8px; }
.end .title { font-size: 76px; }
.flow { display: flex; align-items: center; gap: 22px; margin-top: 56px; }
.flow span { display: inline-flex; align-items: center; gap: 14px; height: 76px; padding: 0 32px 0 18px; border-radius: 999px; background: var(--g100); font-size: 30px; font-weight: 700; }
.flow span b { display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 22px; }
.flow i { width: 40px; height: 2px; background: var(--g400); }
.end .sub { margin-top: 56px; font-size: 26px; }
`;

(async () => {
  const slidesDir = path.join(OUT, 'slides');
  fs.mkdirSync(slidesDir, { recursive: true });
  const html = `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>${CSS}</style></head><body>${S.map(s => s.html).join('\n')}</body></html>`;
  fs.writeFileSync(path.join(OUT, 'slides.html'), html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.join(OUT, 'slides.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  const fontsOk = await p.evaluate(() => [document.fonts.check('700 40px "Pretendard Variable"', '가'), document.fonts.check('40px Tossface', '🔮')]);
  const over = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s, i) => {
    const R = s.getBoundingClientRect(), bad = [];
    s.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.width && (r.right > R.right + 1 || r.bottom > R.bottom + 1 || r.left < R.left - 1)) bad.push(e.className || e.tagName); });
    return bad.length ? (i + 1) + ':' + [...new Set(bad)].slice(0, 4).join(',') : null;
  }).filter(Boolean));
  const els = await p.$$('.slide');
  const files = [];
  for (let i = 0; i < els.length; i++) {
    const f = path.join(slidesDir, String(i + 1).padStart(2, '0') + '.png');
    await els[i].screenshot({ path: f });
    files.push(f);
  }
  await b.close();
  // PPTX : 장마다 그림 한 장 (16:9 꽉 채움) + 발표자 메모
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.title = '오늘의 운세 사용 가이드';
  pres.author = '세일즈혁신TF';
  pres.company = 'MeAI';
  pres.subject = '오늘의 운세 v2 (사주팔자 · 타로) 사용 가이드';
  files.forEach((f, i) => {
    const s = pres.addSlide();
    s.background = { color: 'FFFFFF' };
    s.addImage({ path: f, x: 0, y: 0, w: 13.333, h: 7.5, altText: S[i].notes });
    s.addNotes(S[i].notes);
  });
  const pptx = path.join(OUT, 'unse_v2_guide.pptx');
  await pres.writeFile({ fileName: pptx });
  console.log('글꼴', fontsOk, '| 넘침', over.length ? over : 0, '| 장', files.length, '|', pptx, (fs.statSync(pptx).size / 1048576).toFixed(1) + 'MB');
})();
