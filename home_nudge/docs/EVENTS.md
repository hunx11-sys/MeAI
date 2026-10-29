# 사용 기록 정의 (MeAI 홈 넛지 v5)

두 갈래로 모은다.

| 갈래 | 어디서 | 무엇 | 표 |
|---|---|---|---|
| **행동(사실)** | 넛지 서버 규칙 엔진 | 출석 · 퀴즈 · 화법 · 추천 고객 · 대화 · 공지 · 동의 요청 · 응원 · 보상 | `nz_day` · `nz_ledger` · `nz_quiz_answer` · `nz_talk_copy` · `nz_lotto_set` … |
| **화면 사용** | 넛지 모듈 `NZ.log(el, action, meta)` → `POST /logs` | 어떤 칸을 올렸나/눌렀나 · 연출을 건너뛰었나 · 설정을 바꿨나 | `nz_event_log` |

## 1. 화면 사용 기록 모양

```json
{ "ts": 1793236320000, "el": "dock_quiz", "action": "open_hover", "meta": {}, "v": "5.0.0" }
```

서버가 붙이는 것 : `user_hash`(사번 해시) · `org_hq` · `org_branch` · `org_team` · `session_id` · `client`(pc/mobile · 브라우저) · 받은 시각.
**보내지 않는 것** : 질문 원문 · 고객 이름 · 따라 쓴 글 · 입력칸 내용 · 화면 캡처.

## 2. 화면 사용 기록 목록

| el | action | meta | 뜻 |
|---|---|---|---|
| `home` | `view` | – | 넛지가 붙은 홈을 봄 |
| `dock_<칸>` | `open_hover` · `open_pin` | – | 막대 칸(quest · attend · quiz · talk · lotto · league · journey · wallet · more)의 카드를 엿봄 · 고정해 엶 |
| `header_dash` | `click` | – | 머리 띠 MeAI 대시보드 |
| `go` | `<target>` | – | 「하러 가기」 · 버디 단추 등으로 원래 기능 이동 (attend · quiz · reco · board · custom · consent · fortune · dash · draw · recap …) |
| `buddy` | `show` · `cta` · `dismiss` | `{id}` | 버디 말풍선 보임 · 단추 누름 · 닫음 |
| `attend` | `stamp` | – | 출석 도장 단추 |
| `quiz` | `answer` · `explained` | `{id}` | 퀴즈 답 · 해설 다 읽음 |
| `ask_meai` | `click` | `{from}` | MeAI에게 더 묻기(퀴즈 등) |
| `talk` | `next` · `copy_done` · `react_like` · `react_save` · `react_used` · `ask_meai` | `{id, on}` | 화법 카드 |
| `talk_library` | `open` · `search` · `copy_start` · `banner_save` · `submit` | `{id}` | 화법 전체 보기 |
| `lotto` | `draw_view` | – | 당첨번호 발표 봄 |
| `league` | `scope` · `cheer` | `{s}` | 리그 범위 전환 · 응원 |
| `settings` | `<키>` | `{v}` | 넛지 설정 바꿈 (fx · sound · buddy · hideRank · tickerSec …) |
| `fortune` | `copy` | – | 운세 안부 문구 복사 |
| `dash` | `open` · `tab` · `csv` | `{tab}` | 대시보드 |
| `host_<kind>` | `event` | `{c}` | 홈에서 report 한 행동(reco.open · chat.custom …). 고객 id 는 보내지 않고 있음/없음만 |

## 3. 행동(서버) 종류

| kind | 누가 보냄 | 불 켬 | 퀘스트 | 로또 |
|---|---|:-:|:-:|:-:|
| `attend` | 넛지 모듈 | ✓ | attend | |
| `quiz.answer` · `quiz.explained` | 넛지 모듈 | | quiz | |
| `talk.copy` | 넛지 모듈 | | talk_copy | |
| `reco.open` | 홈 report · 추천 서비스 | ✓ | reco_open · age_up_3 | (목업 설정일 때) |
| `chat.custom` | 홈 report + **대화 서버 간 이벤트** | ✓ | chat_custom | ✓ (운영 권장) |
| `chat.general` | 홈 report + 대화 서버 | ✓ | | |
| `notice.read` | 홈 report + 게시판 | | notice_read | |
| `consent.request` | 홈 report + 알림톡 | | consent_req | |
| `fortune.send` | 넛지 모듈 | | fortune_send | |
| `cheer.send` | 넛지 모듈 | | | |
| `dash.open` | 넛지 모듈 | | (첫 7일 여정) | |

## 4. 대시보드가 쓰는 집계 (`nz_agg_daily`)

일 · 조직(본부 · 지점 · 팀) 단위 : 출근 인원 · 홈 방문 · 출석 · 불 켠 사람 · 퀴즈 참여/정답 · 화법 따라 쓰기/저장 · 추천 고객 노출/열람 · 맞춤대화 · 일반대화 · 세트 발급 · 응모권 · 막대 칸별 열람 · 연출 건너뛰기 비율 · 설정 끈 비율.
**5명 미만 조직 칸은 대시보드에 보이지 않는다**(개인 특정 방지).
