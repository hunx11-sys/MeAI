# 흐름 시연판 · `flow.html`

「플라이휠, 영업지원도구를 통한 영업프로세스 선순환」을 **실제 도구 화면으로** 보여 주는 한 장짜리 시연판이다.
가상 고객 김하늘 님(1988년생 여성)의 한 바퀴(고객발굴 → 터치 → 클로징 → 계약체결 → 관리·소개 → 새 고객발굴)를 22장면으로 따라가며,
장면마다 저장소에 있는 도구 HTML 을 그대로 띄운다. PPT(`dist/meai_flywheel_deck.pptx`)와 같은 순서 · 같은 말투(음·임)다.

## 여는 법
- 저장소(MeAI 폴더) 맨 위의 `flow.html` 을 크롬이나 엣지로 연다(더블클릭). 인터넷이 없어도 된다.
- **폴더째 있어야 한다.** 시연판이 옆에 있는 `tool.html` · `products.html` · `통합치료비.html` · `prompts.html` · `명패생성기.html` · `index.html` · `dist/` · `docs/` · `ui/mascots/` · `flow/` 를 불러 쓴다.
- 넘기기 : 아래 「다음」 · 「이전」, 키보드 → ← (화면 안 도구를 누른 뒤에는 키보드가 그 도구로 가므로 단추를 쓴다)
- 위 단계 칩 · 아래 진척 막대를 누르면 그 단계 첫 장면으로 간다. 「장면 목록」 · 「말할 거리」(N 키) · 「전체 화면」
- 주소 끝 `#s=9` 처럼 장면 번호를 붙여 열면 그 장면에서 시작한다.

## 장면 (SCENES 배열 하나만 고치면 된다)
| 구간 | 장면 | 띄우는 것 |
|---|---|---|
| 시작 | 대문 | `index.html` |
| 1 고객발굴 | 추천 고객 · CRM 룰렛 · 프롬프트 「고객발굴」 | `dist/meai_home_nudge_v5.html` (목업) · `prompts.html` |
| 2 터치 | 오늘의 운세(휴대폰 틀) · 오늘의 화법 | `dist/unse_saju_tarot.html#saju` · 홈 넛지 |
| 3 클로징 | 특약검색기 · 보상시뮬레이터 · 통합치료비 · 스마트 제안서 9쪽 · GA 디자인판 · 세일즈북 · 수술비 정리표 | `tool.html#search` · `tool.html#sim` · `통합치료비.html#C16` · `flow/sp_*.jpg` · `flow/ga_*.jpg` · `docs/guidebook_proto.html` · `flow/xl_*.jpg` + 엑셀 받기 |
| 4 계약체결 | 상품 라인업 · 예외질환 판정 · 가이드라인 PDF | `products.html` · `products.html?ex#ex` · `dist/simple_ins_exception_guide_2610.pdf` |
| 5 관리·소개 | 청구 안내 · 프롬프트 「사후관리」 · 갱신 연락 | `tool.html#sim` · `prompts.html` · 홈 넛지 |
| 6 새 고객발굴 | 명패 제작기 · 다시 1단계 | `명패생성기.html` · 홈 넛지 |
| 정리 | 한 바퀴 요약 | (시연판 안에서 그림) |

- 도구 파일은 **고치지 않는다.** 도구가 이미 알아듣는 주소 해시(`#sim` · `#ex` · `#C16` · `#saju`/`#tarot` · 넛지 `#/mg-gate-010`)와
  postMessage(특약검색기 `meai-open-rider` 로 「암진단비(유사암제외)」 약관 열기 · 보상시뮬레이터 안쪽 틀에 `meai-sim-query` 로 질병 넣기)만 쓴다.
- 같은 파일은 틀 하나를 계속 쓴다(장면을 오가도 도구 안 상태가 남는다). `products.html` 은 처음 열 때만 `#ex` 를 읽어서 예외질환 판정 장면은 `?ex` 를 붙여 따로 띄운다.
- 데스크톱 도구는 1440×900 화면을 줄여서, 운세는 390×844 휴대폰 틀로 띄운다. 다음 장면의 도구는 지금 장면이 다 뜬 뒤 미리 불러 둔다.

## 그림 · 글꼴
- `flow/sp_01~09.jpg` : 스마트 제안서 9쪽(`proposal_smart/cust_a.json` 예시 고객 · 설계사 정보 가림)
- `flow/ga_01~05.jpg` : GA 디자인판 미리보기(`ga_preview.py` 가정값 · 가계약 · 코드 번호는 0 으로 가림)
- `flow/xl_s15.jpg` · `xl_surg.jpg` : 수술비 3종 정리표 시트 화면
- 글꼴 : 파일로 열면 브라우저가 옆 글꼴 파일을 막아서, 시연판에 쓰는 글자만 담은 Pretendard 를 파일 안에 넣었다.
  **글을 고쳤으면 `python3 scripts/build_flow_font.py` 를 다시 돌린다**(fonttools 필요 · 원본 `assets/pretendard-subset.woff2`).
- 화면 속 사람 이름 · 금액은 모두 예시다. 홈 넛지는 목업이고, 스마트 제안서 · GA 디자인판 · 세일즈북은 프로토타입이다.
