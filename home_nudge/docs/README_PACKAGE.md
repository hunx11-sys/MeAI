# MeAI 홈 넛지 플레이 v5 · 개발 패키지 (먼저 읽기) · v5.1 행운 존 포함

> 세일즈혁신TF · 2026-10-29 · 받는 사람 : MeAI 홈 화면 개발 · 넛지 서버 개발 · 데이터 담당
> 이 묶음 하나로 **화면을 눈으로 보고(목업) → 규칙을 맞추고(규칙 엔진 · 테스트) → 서버를 만들고(API · DB) → 홈에 붙인다(연동)**.

## 0. 5분 안에 보기

1. `mockup/meai_home_nudge_v5.html` 을 크롬 · 엣지로 연다(더블클릭, 인터넷 필요 없음). 실제 MeAI 홈(2026-09-29 빌드) 위에 넛지를 얹은 목업이다.
2. 인사말 아래 **「오늘의 MeAI」 막대**의 칸에 마우스를 올려 보고(0.2초 뒤 카드), 눌러서 고정해 본다. 출석 도장 → 퀴즈 → 추천 고객 카드 열기(슬롯머신) → 화법 따라 쓰기 순서가 한 바퀴다.
3. 막대 끝 **「행운 존」** : CRM 룰렛 · 추천 고객 슬롯 · OX 스피드 챌린지 · 오늘의 타로 · 스크래치 복권 · 오늘의 운세 · 영업 빙고 · 피버 타임(데모 시계 14:05).
4. 왼쪽 아래 **「데모 메뉴」** : 데모 시계(금 17:05 추첨 발표 · 리캡), 보는 사람(신인 · 지점장 · 본사), 연출 바로 보기, 운영 설정(로또 발급 시점 · 명칭)을 바꿔 본다.
5. 설계도 `docs/BLUEPRINT.pdf`(또는 `.md`). 행운 존은 1-2장 · 3-11장.

## 1. 무엇이 들어 있나

| 폴더 · 파일 | 누가 | 무엇 |
|---|---|---|
| `docs/BLUEPRINT.*` | 모두 | 설계도 : 화면 · 규칙 · 구조 · API · DB · 배치 · 추첨 공정성 · 대시보드 · 보안 · 추진 단계 |
| `docs/INTEGRATION.md` | 홈 화면 개발 | 홈 React 에 자리 4곳 · 이벤트 5개 붙이는 방법(예시 코드) |
| `docs/openapi.yaml` | 서버 개발 | API 명세 (OpenAPI 3.0, 검사기 통과) |
| `docs/schema.sql` | 서버 · DBA | 표 35개 (행운 존 9개 포함 · PostgreSQL 16 에 실제로 만들어 확인 · 오라클 바꿀 곳 주석) |
| `docs/EVENTS.md` | 데이터 | 사용 기록 정의 · 집계 |
| `config/nudge.config.json` | 운영 | 보상 · 한도 · 퀘스트 · 로또 · 배지 · 버디 문구 (예시값, 코드 수정 없이 바꿈) |
| `src/core/rules.js` | 서버 개발 | **규칙 엔진 기준 구현** (보상 판정 전부). 서버 언어로 옮기고 `tests/vectors.json` 으로 맞춘다 |
| `src/nudge/` · `src/api/client.js` · `src/host/simple-host.js` | 홈 화면 개발 | 넛지 화면 모듈 (바닐라 JS · 라이브러리 0 · 엄격한 CSP 통과) · 행운 존은 `fun.js` |
| `src/vendor/unse-engine.js` · `assets/tarot/` | 홈 화면 개발 | 오늘의 운세 엔진(사주 · 타로 풀이 · 원본 그대로, 고치지 않는다) · 타로 메이저 22장(1909 원판) |
| `src/api/mock.js` | 화면 개발 | 서버 없이 화면을 만드는 모의 서버 (`client.js` 와 같은 함수 · 같은 응답) |
| `examples/sandbox.html` | 화면 개발 | 원본 홈 없이 모듈만 붙여 보는 연습 화면 (가장 엄격한 CSP) |
| `tests/` · `tools/` | 모두 | 규칙 테스트 · 목업/연습 화면/API 약속 점검 |
| `data/` | 참고 | 예시 데이터 (퀴즈 7 · **OX 문제 은행 39**(약관 원문 대조 18) · 화법 798건(제출자 이름 가림) · 목업 달력 · 예시 조직 · 예시 고객 14명) |
| `assets/mascots/` | 화면 | 걱정인형 그림 + 사용 규칙 (`RULES.md` : 비율 유지 · 색 변경 금지 · 홍보파트 협의) |
| `mockup/` | 모두 | 고도화 목업 · 오늘의 운세(행운 존 → 오늘의 운세 → 전체 운세) |
| `MANIFEST.txt` | IT | 파일 목록 · 해시 |

## 2. 순서대로 하기

### 화면 개발

```
cd meai_home_nudge_v5
python -m http.server 8080          # 아무 정적 서버
# 브라우저 : http://localhost:8080/examples/sandbox.html   (모의 서버로 모듈만 동작)
node tools/check_sandbox.js         # 가장 엄격한 CSP 에서 위반 · 오류 · 바깥 요청 0 확인 (playwright 필요)
```

그다음 `docs/INTEGRATION.md` 대로 홈에 자리 4곳과 `report` 5곳을 붙이고, 서버가 준비되면 `NZMock.createMockApi(...)` 를 `NZClient.createHttpApi('/api/nudge/v1')` 로 바꾼다.

### 서버 개발

```
node tests/rules.test.js            # 기준 구현 112건 통과 확인 (행운 존 포함)
python3 tools/check_contract.py     # 모의 서버 응답 ↔ openapi.yaml 모양 대조 (pip install openapi-spec-validator)
```

1. `docs/schema.sql` 로 표를 만든다.
2. `src/core/rules.js` 의 `evaluate` 를 서버 언어로 옮긴다(판정 순서 BLUEPRINT 6장). 서버 단위 테스트에서 `tests/vectors.json` 의 입력을 넣어 **같은 출력**이 나오는지 본다(날짜 · SHA-256 · 추첨 · 확률 · 채점 · 보상 시나리오 · 보호권).
3. `docs/openapi.yaml` 대로 API 를 만든다. 응답 모양은 모의 서버 `home()` 과 같아야 한다(`tools/dump_mock.js` 로 견본을 뽑아 비교).
4. 배치 9개(BLUEPRINT 8장)와 서버 간 이벤트(`/internal/events`)를 붙인다.

## 3. 정할 것 (개발 전에 사업부서 확인)

1. 경품 예산 · 처리 기준(단가 · 당첨 인원 · 제세공과금) → `config` 의 `lotto.tiers` · `coffeeDraw` · 행운 존 운 응모권 한도 `fun.ticketCapDaily`
1-2. 행운 존 확률 · 경품(룰렛 · 슬롯 · 스크래치 가중치) · 피버 시간대 · 안부 문구의 준법 의견 → `config` 의 `fun` · `fever`
2. 「로또」 명칭 · 연출의 준법 의견 → `labels.useAltLottoName`(「MeAI 행운번호」)
3. 1차 파일럿 본부 · 지점, 화법 제출자 실명 표시 여부(본인 동의)
4. 영업일 달력 · 근태(휴가 · 교육) 연동 방식, 대화 서버 간 이벤트 연동 방식

## 4. 주의

- 목업 속 사람 이름 · 조직 · 숫자 · 당첨은 모두 **예시**다. 출처가 붙은 사용량(헤비유저 · 침투율)만 실제 분석값이다.
- 화법 798건은 AI 정리 · 준법 검토 **초안**이다. 오픈 전 준법 담당 부서 최종 확인이 필요하다.
- 목업 · 패키지는 사내 검토용이다. 외부에 제공 · 게시하지 않는다.
