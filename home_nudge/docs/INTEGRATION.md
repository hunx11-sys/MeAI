# MeAI 홈에 넛지 붙이기 (홈 화면 개발 담당용)

> 원본 홈 코드를 크게 바꾸지 않는다. **자리 4곳 · 카드 표시 2개 · 이벤트 5개 · 이동 함수 2개**만 더한다.
> 넛지 모듈은 바닐라 JS 라 React 상태와 섞이지 않는다. 모듈이 그린 부품을 홈이 만든 빈 자리에 꽂는 구조다.

## 1. 파일 넣기

배포 묶음(빌드 도구 없이 순서대로 이어 붙인 두 파일이면 된다)

```
meai-nudge.css   = src/nudge/nudge.css
unse-engine.js   = src/vendor/unse-engine.js  (오늘의 운세 엔진 · 사주 · 타로 풀이 원본 그대로 · meai-nudge.js 보다 먼저)
meai-nudge.js    = src/api/client.js + src/nudge/core.js + fx.js + ui.js + cards.js + fun.js + talks.js + dash.js + index.js + src/host/simple-host.js
assets/mascots/  = 걱정인형 그림 (hello_wave · tata_board · …)
assets/tarot/    = 타로 메이저 아르카나 22장 00~21.webp (1909 원판 · 오늘의 타로)
```

- 홈 `index.html` 에 `<link rel="stylesheet" href="/static/nudge/meai-nudge.css">` 와 `<script src="/static/nudge/unse-engine.js" defer></script><script src="/static/nudge/meai-nudge.js" defer></script>`. 인라인 코드가 없어 지금 CSP 그대로 쓸 수 있다(`script-src 'self'`).
- 모의 서버(`src/api/mock.js` + `src/core/rules.js`)는 **개발 · 시연에서만** 넣는다. 운영 묶음에는 넣지 않는다.

## 2. 자리 만들기 (홈 컴포넌트)

```jsx
// 홈 머리 띠 : 오른쪽 그룹 맨 앞
<div className="flex items-center gap-8">
  <div id="nz-slot-cap" />                 {/* ① 내 기록 캡슐 + MeAI 대시보드 */}
  <FontScaleToggle />                      {/* 원래 있던 글씨 확대 */}
  <ConsentButton /><BoardButton />
</div>

// 인사말 영역 : position: relative 필요 (버디가 오른쪽 위에 뜬다)
<section className="relative mt-32">
  <h1><em>{user.name}</em>님 안녕하세요, 무엇을 도와드릴까요?</h1>
  <div id="nz-slot-buddy" />               {/* ③ 버디 말풍선 */}
  <div id="nz-slot-dock" />                {/* ④ 오늘의 MeAI 막대 (높이 +84px) */}
  <Subtitle /><ChatCards /><FindCustomerCard />
</section>

// 오늘의 추천 고객
<h2>오늘의 추천 고객 <span id="nz-slot-rechint" /></h2>
{recos.map((c) => (
  <article key={c.id} data-nz-reco={c.id} data-name={c.name} data-tags={c.tags.join(',')} onClick={() => openReco(c)}>
    …
    <div className="consent-row"><ConsentChip c={c} /><span data-nz-badge /></div>  {/* ⑥ 배지 자리 */}
  </article>
))}
```

- `data-nz-reco` 에는 **추천 서비스의 고객 id** 를 그대로 넣는다(넛지 서버가 오늘 추천 목록과 대조해 세트를 준다).
- 자리 div 는 비어 있어야 한다. React 가 그 안을 다시 그리지 않도록 자식 없이 둔다(모듈이 채움).
- 추천 고객 카드가 바뀌면(넘김 · 새로 고침) `MeAINudge.render()` 를 한 번 불러 배지를 다시 붙인다.

## 3. 붙이기 (앱 시작 때 한 번)

```js
// 예) HomePage 의 useEffect(() => { … }, [])
import { useEffect } from 'react';
useEffect(() => {
  const api = NZClient.createHttpApi('/api/nudge/v1', { headers: () => ({ 'X-CSRF-TOKEN': csrf() }), onAuth: () => location.reload() });
  const host = NZSimpleHost.createSimpleHost({
    onGo: (target) => nudgeGo(target),          // 아래 4장
    onAsk: (text, mode) => openGeneralChat({ prefill: text })   // MeAI에게 더 묻기 · MeAI로 다듬기
  });
  MeAINudge.mount({ api, host, assetBase: '/static/nudge/assets/' });   // 타로 그림은 assetBase + 'tarot/00.webp' (따로 두면 tarotBase)
}, []);
```

- `mount` 는 한 번만 한다(두 번 불러도 무시). 홈을 떠났다 돌아오면 자리 div 가 새로 생기므로 `host.attach` 가 다시 꽂는다. 홈 컴포넌트 `useEffect` 에서 `MeAINudge.render()` 를 부르면 된다.
- 글씨 확대는 `html.gate-fontscale-off` 클래스를 넛지 CSS 가 그대로 따른다(추가 작업 없음).

## 4. 넛지 → 원래 기능 (`host.go`)

| target | 할 일 |
|---|---|
| `reco` | 오늘의 추천 고객 영역으로 스크롤 + 카드 강조 |
| `custom` | 맞춤대화 시작(고객 고르기 팝업) |
| `general` | 일반대화 열기 |
| `board` | 게시판 열기 |
| `consent` | 고객 동의(사전조회동의 알림톡) 팝업 |
| `find` | MeAI 고객찾기 |
| `fortune` | 오늘의 운세 전체 페이지(사내 웹서버 `unse/`). 권장 : `MeAINudge._nz.fun.openFrame('/unse/', '오늘의 운세')` 로 홈 위 덮개 안에 띄우기(같은 출처면 CSP `frame-src 'self'`) · 또는 새 창 |
| (v5.1) `roulette` · `cslot` · `challenge` · `tarot` · `scratch` · `fortune-card` · `fun` | 넛지 모듈이 스스로 처리(행운 존 게임 덮개). 홈은 할 일 없음 |
| `home` | 홈으로 |

`host.ask(text)` : 일반대화를 열고 입력칸에 `text` 를 **넣기만** 한다(보내기는 사람이 누른다).

## 5. 홈 → 넛지 이벤트 (`MeAINudge.report`)

| 언제 | 호출 | 비고 |
|---|---|---|
| 추천 고객 카드를 열었을 때 | `MeAINudge.report('reco.open', { customerId })` | 같은 고객은 하루 한 번만 센다(서버) |
| 맞춤대화 질문이 **실제로 나갔을 때** | `MeAINudge.report('chat.custom', { customerId })` | 로또 발급 기준(운영 권장). 대화 서버도 서버 간 이벤트로 같은 `idem` 을 보낸다 |
| 일반대화 질문이 나갔을 때 | `MeAINudge.report('chat.general')` | |
| 게시판 공지를 열었을 때 | `MeAINudge.report('notice.read', { ref: noticeId })` | 새 공지 1건 읽기 퀘스트 |
| 사전조회동의 알림톡을 보냈을 때 | `MeAINudge.report('consent.request', { customerId })` | 교체용 퀘스트 |

- (v5.1) 행운 존 : 홈이 따로 report 할 것은 없다. 룰렛 · 슬롯 고객 후보는 넛지 서버가 CRM 에서 받는다(`crm_sync`). 문자 · 알림톡 발송 시스템이 있으면 발송 사실을 서버 간 이벤트 `{ kind: 'crm.done', customerId, ref }` 로 보내 화면 신고를 확정한다.
- 서버 간 이벤트(확정) : 대화 서버 · 게시판 · 알림톡이 넛지 서버 `POST /api/nudge/v1/internal/events` 로 `{ userId, kind, customerId, ref, idem, ts }` 를 보낸다(서버 인증서 · 내부망). 화면 `report` 와 `idem` 이 같으면 한 번만 센다. 화면 `report` 만 오고 서버 간 이벤트가 끝내 안 오면(10분) 로또 세트는 「확인 대기」로 두고 추첨에서 뺀다(운영 정책으로 선택).

## 6. 확인

1. `examples/sandbox.html` 을 웹서버로 열어(예 : `home_nudge` 폴더에서 `python -m http.server`) 모듈만 먼저 돌려 본다.
2. `node tools/check_sandbox.js` : 가장 엄격한 CSP 에서 위반 · 오류 · 바깥 요청 0.
3. 홈에 붙인 뒤 1440×900 에서 기본 4요소가 첫 화면에 보이는지, 막대 칸 올림/누름/Esc 가 되는지 본다.
4. 운영 전환 : `createMockApi` 를 쓰는 곳이 남아 있지 않은지 확인한다(`grep -r createMockApi`).
