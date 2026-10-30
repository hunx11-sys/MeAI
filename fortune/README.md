# 오늘의 운세 (사주 + 타로) v2

이름과 생년월일만 넣으면 **사주팔자 · 오늘의 운세 · 대운**과 **타로 4장 점괘**를 보여 주는 한 파일짜리 화면이다.
설계사가 고객에게 카톡 · 문자로 보내는 재미용 도구(MeAI 홈 넛지). 입력한 정보는 휴대폰 밖으로 나가지 않는다.

- 한 파일판 : `dist/unse_saju_tarot.html` (약 3.5MB, 바깥 파일을 하나도 부르지 않음 · 오프라인 · 더블클릭 · 카톡 전달)
- **사내 웹서버 · 폐쇄망 탑재 패키지** : `dist/unse_v2_package.zip` (웹서버판 `web/` · 한 파일판 · 개발 설계도 · 소스 전체 · 검증 도구 · 서버 설정 예시 · 파일 해시)
- 개발 설계도 : `fortune/docs/BLUEPRINT.md` (보기 좋은 판 `.pdf` · `.html`), 탑재 가이드 : `fortune/docs/README_INSTALL.md`
- v1 원본 : `fortune/legacy/unse_v1_261016.html` (구글 드라이브 `261016_오늘의운세_사주타로.html` 과 같은 파일)

## 사내 웹서버 · 폐쇄망 탑재 패키지 (2026-10-29)

`dist/unse_v2_package.zip` 을 IT 담당자에게 넘긴다. 안의 `README.md` 가 탑재 가이드다.
- **웹서버판** `web/` : 정적 파일 92개 · 약 2.6MB. 인라인 스크립트 · 스타일 · `style` 속성 · `data:` 주소 · 외부 주소 0 →
  가장 엄격한 보안정책(`default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' blob:; font-src 'self'`)에서 위반 0 · 바깥 요청 0,
  글꼴을 막은 정책에서도 동작, 포털 iframe 안에서도 동작 (`tools/check_web.js`)
- 계산 파일(`fortune-text.js` · `saju-engine.js` · `tarot-data.js`)은 v1 웹 패키지(2026-10-16)와 본문이 같다
- 웹판 폴더를 서버 없이 파일로 열면 저장 이미지에서 카드 그림만 빠진다(브라우저 규칙) → 서버 없는 PC 는 한 파일판

## 사내 공모전 제출 PPT (2026-10-30)

`dist/unse_v2_contest.pptx` (16장 · 장마다 통이미지 · 발표 원고는 발표자 메모) · `dist/unse_v2_contest.pdf` · 양식 칸별 제출 글 `fortune/docs/CONTEST_FORM_v2.md`
- 10/14 「오늘의 사주」 공모전 설계도 PPT(14장)의 순서와 말투를 이어받음 : 표지 · 한 장 요약 · AS-IS · TO-BE · 사용 흐름(사주 · 타로) · **v1 → v2 비교** · 전체 구조 · 계산 로직(사주 · 타로) · 저장·보내기 · 추가 비용 0원 · 기대 효과 · 개인정보 · 사내 탑재 · 검증 · 한계 · 다음 단계
- 「연 약 500만원」은 10/14 제출 글 기준 추정치라 장표에 별표로 밝혀 둠(근거 자료 확인 필요)
- 다시 만들기 : `capture.js` + `capture_v1.js`(비교용 v1 화면) → `node fortune/guide/build_contest.js <cap> <Pretendard> <Tossface> <출력>` (공통 부품 `deck_kit.js`)

## 사용 가이드 PPT (2026-10-30)

`dist/unse_v2_guide.pptx` (16장 · 장마다 통이미지라 어느 PC 에서도 글꼴이 깨지지 않음 · 발표자 메모 포함) · `dist/unse_v2_guide.pdf` (같은 내용)
- 디자인 : `design/DESIGN-토스.md` (흰 바탕 · 토스 블루 하나 · 둥근 카드 · 1px 선 · 해요체 · Pretendard · 토스페이스 그림 글자)
- 구성 : 표지 · 한눈에 보기 · 여는 방법 · 대문 · 사주 4장(입력 · 사주팔자 읽기 · 오늘의 운세 · 보내기) · 타로 4장(시작 · 4장 고르기 · 풀이와 크게 보기 · 종합 메시지) · 대화 예시 · 자주 묻는 질문 · 꼭 지켜 주세요 · 마무리
- 다시 만들기 : `node fortune/guide/capture.js <한 파일판> <cap>` → `node fortune/guide/build_guide.js <cap> <PretendardVariable.woff2> <TossFaceFontMac.ttf> <출력>`
  (Pretendard : `npm pack pretendard@1.3.9` · 토스페이스 : github.com/toss/tossface 릴리스 · pptxgenjs 필요)

## v2 에서 바뀐 것 (2026-10-29)

| 화면 | v1 | v2 |
|---|---|---|
| 타로 카드 앞면 | 이모지 · 기호 | **1909년 라이더-웨이트-스미스 원판 그림 78장** + 크림색 테두리 · 금박 선 · 한글 이름판(명조) |
| 타로 카드 뒷면 | 단순한 달 무늬 | 남색 바탕 금선 해 · 달 · 별 문양 (180도 돌려도 같은 실제 타로 뒷면 방식) |
| 타로 결과 | 작은 기호 카드 | 풀이마다 실제 카드, 누르면 **크게 보기** 창, 종합 메시지에 4장 나란히 |
| 타로 저장 이미지 | 기호 카드 | 실제 카드 4장(역방향은 거꾸로) + 금테 |
| 사주 머리 | 보라 그러데이션 | 밤하늘 + **일월오봉**(달 · 해 · 다섯 봉우리 · 물결) 금선 그림 |
| 사주 기둥 | 색 네모 | 한지색 패 + 명조 한자 + 오행 표시(火·金), 일주는 금테 |
| 오행 분포 | 숫자 다섯 칸 | **상생 고리 그림**(木→火→土→金→水 화살표, 동그라미 크기 = 개수, 가운데 일간) |
| 바탕 · 글꼴 | 시스템 글꼴 | 대문 · 타로 = 밤하늘, 사주 = 한지 / 고운바탕(한글) · Noto Serif KR(한자) · Cinzel(로마 숫자) |
| 대문 | 그러데이션 문 두 개 | 금색 달 문장, 사주 문 = 일월오봉 + 「四柱八字」 낙관, 타로 문 = 실제 카드 3장 부채꼴 |

**계산 · 문구는 하나도 바꾸지 않았다.** 사주 엔진 · 운세 문구 · 타로 풀이는 `src/engine.js` 에 v1 그대로 옮겼고,
`tools/regress_saju.js` 로 v1 과 v2 의 사주 칸 값을 날짜 120개 × 남녀 = 240건 대조해 **다른 칸 0건**을 확인했다
(기둥 글자 · 십신 · 절기 경고 · 운세 문구 · 점수 · 행운 · 대운). 일간 설명 문장의 긴 줄표만 쉼표로 바꿨다.

함께 고친 것
- 타로 무대 뒤 보랏빛 광채가 화면 폭의 120%로 그려져 휴대폰에서 가로로 28px 흔들리던 것(v1 부터 있던 문제)
- 접근성 : 작은 글씨 대비 4.5:1 이상으로(오행 0개 이름표 · 바닥글 · 입력 안내), 뒤로 버튼 44px,
  **키보드만으로도 타로 진행**(카드 자리에서 Enter = 섞기 · 한 장 뽑기), 크게 보기 창은 Esc 로 닫힘
- 움직임 줄이기 설정이면 섞기 · 뒤집기 연출을 끈다

## 파일

| 파일 | 하는 일 |
|---|---|
| `src/unse.html` | 화면 틀 (화면 · 그림 조각). 자리표 `<!--@@HEAD@@-->` · `<!--@@SCRIPTS@@-->` |
| `src/unse.css` | 디자인. 자리표 `@@FONT_*@@` · `@@BACK@@` · `@@HANJI@@` · `@@ZOOM@@` (웹판 = 파일 주소, 한 파일판 = data: 주소) |
| `src/ie-check.js` | 익스플로러 → 엣지 안내 |
| `src/engine.js` | 사주 엔진 · 운세 문구(`NZ_FTEXT`) · 타로 78장 풀이(`NZ_TAROT`). **v1 그대로, 고치지 않는다** |
| `src/app.js` | 화면 동작 (사주 그리기 · 타로 섞기/뽑기 · 크게 보기 · 저장 이미지 · 공유) |
| `assets/tarot/00~77.webp` | 카드 그림 (번호 = deck id : 0~21 메이저, 22부터 완드 · 컵 · 소드 · 펜타클 14장씩) |
| `assets/svg/card-back.svg` · `hanji.svg` · `zoom.svg` | 카드 뒷면 · 한지 무늬 · 돋보기 |
| `assets/fonts/*.woff2` · `OFL.txt` | 글꼴 3종(필요한 글자만) · 사용권 |
| `build_unse.py` | 조립 : 기본 = 한 파일판, `--web <폴더>` = 웹서버판(정적 파일 92개, 인라인 코드 · data: 주소 0), `--preview` = claude.ai 미리보기 |
| `build_package.py` | 탑재 패키지 zip (`dist/unse_v2_package.zip`) |
| `docs/` | 개발 설계도 · 탑재 가이드 · 서버 설정 예시(IIS · 톰캣 · nginx · 아파치) |
| `tools/prep_tarot.py` | 카드 그림 손질 (테두리 · 영문 제목띠 자르기, 같은 비율로, WebP) |
| `tools/make_fonts.py` | 글꼴 줄이기 (화면에 새 한자가 들어가면 다시 돌린다) |
| `tools/regress_saju.js` | v1 화면과 사주 결과 대조 (240건) |
| `tools/verify_saju.py` · `tools/ref/` | 파이썬 사주 엔진(엑셀과 같은 규칙)과 1936~2046 40,543일 대조 |
| `tools/csp_test_server.py` · `tools/check_web.js` | 가장 엄격한 보안정책(CSP)으로 웹판 띄우기 · 자동 점검(위반 · 바깥 요청 · iframe · 저장 이미지) |
| `tools/render_doc.js` | 설계도 마크다운 → HTML · PDF (흐름 그림 포함) |

## 다시 만드는 순서

```
python3 fortune/build_unse.py                      # 한 파일판 (화면 · 문구만 고쳤을 때는 이것만)
node fortune/tools/regress_saju.js $PWD/fortune/legacy/unse_v1_261016.html $PWD/dist/unse_saju_tarot.html
python3 fortune/build_unse.py --web /tmp/web && node fortune/tools/check_web.js /tmp/web   # 웹판 · 엄격한 CSP 점검
python3 fortune/tools/verify_saju.py               # 계산을 고쳤다면 40,543일 대조
python3 fortune/build_package.py                   # 탑재 패키지 zip (설계도를 고쳤다면 render_doc.js 먼저)
```

카드 그림을 다시 뽑을 때 : `npm pack @cometpisces/tarot-kit-images@0.2.0` → 압축을 풀고
`python3 fortune/tools/prep_tarot.py <package/images>`. 글꼴은 github.com/google/fonts 에서 원본 ttf 를 받아
`python3 fortune/tools/make_fonts.py <ttf 폴더>`.

## 그림 · 글꼴 출처

- 타로 그림 : 라이더-웨이트-스미스 타로(1909, 아서 에드워드 웨이트 기획 · 파멜라 콜먼 스미스 그림). 스미스가 1951년에 세상을 떠나
  사후 70년이 지난 공개 저작물이다. 1909년 원판 색을 쓴 npm 꾸러미 `@cometpisces/tarot-kit-images@0.2.0` 에서 받았다.
  **1971년 U.S. Games 재채색판(카드 아래 ⓒ 표시가 있는 판)은 쓰지 않는다.**
- 원판 그대로라 「죽음」(해골) · 「소드 10」 · 「소드 3」 · 「탑」 · 「악마」, 몇몇 카드의 맨몸 인물 그림이 들어 있다.
  **소유자 결정(2026-10-29) : 원판 그대로 쓴다.** 순한 그림으로 바꾸거나 가리지 않는다.
- 카드 뒷면 · 일월오봉 · 달 문장 : 직접 그린 SVG.
- 글꼴 : 고운바탕 · Noto Serif KR · Cinzel (모두 SIL Open Font License 1.1, `assets/fonts/OFL.txt`).
