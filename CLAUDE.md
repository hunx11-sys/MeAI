# MeAI — 작업 규칙

메리츠화재 세일즈혁신 자료 저장소. 소유자는 프로그래밍을 하지 않으니 **설명은 전문용어 없이 한국어로** 쓴다.

## 무엇이 들어 있나

| 갈래 | 위치 | 무엇 |
|---|---|---|
| **스마트 제안서 생성기** | `proposal_smart/` | 고객 설계서 PDF → 보장 지면(최대 9쪽)을 만들어 원본에 끼워 넣는다. 자세한 설명·변경 기록은 `proposal_smart/README.md` |
| GA 스마트 제안서 생성기 | `proposal_smart/ga_proposal.py` · `ga_spec.py`(칸 정의 — 지면은 이 값을 그리기만 한다) · `ga_care.py`(간병인 칸) · `ga_preview.py`(설계서 없이 지면 모양 보기) · `make_ga.bat` | 설계서 PDF → GA 양식 PDF : **표지(2판 · `GA_COVER`) · 1 보장요약(암 · 뇌심 · 주요수술 12 · 간병인) · 2 암보장 · 3 뇌·심보장 · 보장금액 세부내역(= 보장요약 칸의 합산 계산서 · 구분/보장금액/특약명/가입금액/특약별 보장금액 · 1쪽 이상, 담보가 많으면 자동으로 늘어남)**. 세부내역은 반드시 붙는다(`CALC_PAGES`, GA 확정 2026-10-02 — 빼지 않는다. 못 만들면 생성 자체가 실패한다). 칸 구성 = GA 내부 회의 목업(2026-10-08) + GA지원센터 수정사항(2026-10-22) · 지면 = **GA 디자인 가안 그림 위에 값 글자만 얹는 합성 모드**(`ga_overlay.py` · `ga_assets/mock/` 가안 6장 + 자리 좌표 `overlay_*.json` · `GA_MOCK=0` 이면 HTML 지면) · 변경 기록은 `proposal_smart/README.md` v8.74 · v8.81 · v8.82. 설계도(흐름·공식·판정 로직·칸별 매핑·특약 마스터) 최종본은 `dist/ga-blueprint-final.xlsx` · 칸별 특약 지도 `dist/ga-cell-map.html` · 다시 뽑는 순서는 `proposal_smart/ga_docs/README.md` |
| 세일즈혁신 가이드북 생성기(프로토타입) | `docs/guidebook_proto.html` | 상품설명서 PDF 를 끌어다 놓으면 담보표·설명문·Key Point·면책감액표를 묶은 가이드북을 만들어 브라우저 인쇄로 PDF 저장. 오프라인 단일 HTML(pdf.js 내장). 글 상자 창고 `scripts/guidebook_kp.json` · 틀 `scripts/guidebook_proto_template.html` · 조립 `python scripts/build_guidebook_proto.py`(pdf.js 는 파일 안의 것을 재사용). 수작업 초판은 `docs/guide_naemom_5105_2609.pdf` |
| 영업지원도구(특약검색·통합치료비 시뮬레이터) | `tool.html` · `통합치료비.html` · `index.html` 등 | 브라우저에서 바로 쓰는 단일 HTML. 디자인 규칙은 `design/DESIGN-MeAI.md`(도구별 걱정인형 강조색 하나 · 공통 토큰) — 공통 스타일 원본 `ui/meai-ui.css` 를 고치면 `python3 scripts/apply_ui.py` 로 7개 화면(+ 보상시뮬레이터 SIMSRC)에 다시 끼운다 |
| 오늘의 운세(사주 + 타로) · MeAI 홈 넛지 | `fortune/` | 이름 · 생년월일로 사주팔자 · 오늘의 운세 · 대운과 타로 4장 점괘를 보여 주는 단일 HTML(`dist/unse_saju_tarot.html`) · **사내 웹서버 · 폐쇄망 탑재 패키지 `dist/unse_v2_package.zip`**(웹서버판 · 설계도 `fortune/docs/BLUEPRINT.md` · 검증 도구, `python3 fortune/build_package.py`). 화면 틀 `fortune/src/unse.html` · 디자인 `src/unse.css` · 동작 `src/app.js` · **사주 엔진 · 문구 · 타로 풀이 `src/engine.js` 는 v1 그대로 두고 고치지 않는다**. 조립 `python3 fortune/build_unse.py`(웹서버판 `--web <폴더>` : 인라인 코드 · data: 주소 0 유지), v1 과 결과 대조 `node fortune/tools/regress_saju.js`, 엄격한 CSP 점검 `node fortune/tools/check_web.js`. 카드 그림은 1909년 라이더-웨이트-스미스 원판(공개 저작물, 1971 U.S. Games 재채색판은 쓰지 않음). 「죽음」 · 「소드 10」 · 맨몸 인물 카드도 **원판 그대로 쓴다(소유자 2026-10-29)**. 설명 · 변경 기록은 `fortune/README.md` |
| **MeAI 홈 넛지 플레이 v5**(고도화 목업 + 개발 패키지) | `home_nudge/` | 원본 MeAI 홈 빌드(`vendor/meai_home_base_260929.html`, 목업 v3 에서 넛지를 뺀 것) 위에 「오늘의 MeAI」 막대 · 내 기록 캡슐 · 버디 말풍선 · 펼침 카드 9종 · 연출 · 화법 전체 보기 · 대시보드 3종을 얹은 목업 `dist/meai_home_nudge_v5.html`(데모 메뉴) + 개발 패키지 `dist/meai_home_nudge_v5_package.zip`(설계도 `docs/BLUEPRINT.md` · API `openapi.yaml` · DB `schema.sql` · 연동 `INTEGRATION.md` · 소스 · 테스트). **보상 판정은 `src/core/rules.js` 하나가 기준**(화면 · 모의 서버 · 서버 공용, 테스트 벡터 `tests/vectors.json` · 판정 방식을 바꾸면 `make_vectors.js` 로 다시 만들고 README 에 적는다). 보상 · 한도 · 경품 숫자는 `config/nudge.config.json`(확정 전 예시). 화법 798건 `data/talks798.json` 은 **제출자 이름을 가린 판**(실명판은 저장소에 올리지 않음). 조립 `python3 home_nudge/build.py [--package]` · 점검 `node home_nudge/tests/rules.test.js` · `tools/check_mockup.js` · `check_sandbox.js`(엄격한 CSP) · `check_contract.py`(API 모양) · `check_a11y.js`. 설명 · 변경 기록 `home_nudge/README.md` |
| 비짓투재팬 VISIT to JAPAN · 일본 직항 여행 플래너(보험과 별개 프로젝트) | `travel/` | 도시 검색·도시별 그림과 위치, 출발 공항·박 수를 고르면 직항편·일정·맛집·숙소·예산·대체 플랜을 보여 주는 단일 HTML(`travel/japan.html`, 6개 언어). 자료는 `travel/data/`, 조립은 `python3 travel/build_japan.py`, 설명·점검기는 `travel/README.md` |
| 배포·보고 산출물 | `dist/` · `docs/` | 메일 발송용 묶음, 검수 보고서 |
| 디자인 문서 보관함 | `design/` | 회사별 디자인 문서(DESIGN-*.md · 토스 등). PPT·HTML·화면을 만들 때 **먼저 여기서 회사 문서를 찾아 그대로 따른다**(`.claude/skills/design-md`). 올리는 법은 `design/README.md` |

약관 원문은 **`tool_body.js`**(특약별 본문, 특약 하나가 한 줄)와 `tool.html`(분류표 `"name":"○○ 분류표"`)에 그대로 들어 있다. 약관 근거를 확인할 때는 이 두 파일을 읽는다.
본문 속 지급금액표 등은 「[표:머리줄수]」+ `|` 줄로 들어 있다(합친 칸 `^` 위 · `<` 왼쪽) — 약관 PDF 에서 본문을 다시 뽑으면 `python3 scripts/fix_body_tables.py --write --only <다시 뽑은 특약>` 로 표를 되살리고(PDF 칸 선 기준, 본문 글자는 바꾸지 않음 · 전체에 다시 돌리면 예시 도식에 빈 표가 겹친다), **이어서 `python3 scripts/fix_table_order.py --write` 로 표·「<보험가입금액 ○>」 제목을 PDF 읽는 순서(쪽 → 왼쪽 단 → 오른쪽 단)대로 옮긴다** — 두 단 조판 때문에 4,000만원 표가 8,000만원 제목 밑에 붙는 사고가 47개 특약에서 있었다(2026-10-21). `scripts/check_body_tables.py`(sync_all 0단계)가 가입금액표 자리 · 계산표(product_data.json) 대조 · 같은 이름 특약 금액을 점검한다. 또또암 · 또또암간편은 특약 `pg` 가 PDF 쪽보다 1 크다(인쇄 쪽 번호) — 쪽을 열 때는 `fix_body_tables.start_page()` 를 쓴다.
본문을 옆 파일로 뗀 것은 인터넷판 속도 때문이다(2026.09). 파이썬에서 DATA 를 고칠 때는 `scripts/tooldata.py` 의 `inflate`/`deflate` 를 쓰면 두 파일이 함께 읽히고 쓰인다. 메일·올인원 배포판은 본문을 압축해 파일 안에 다시 넣는다.
특약을 더하거나 고친 뒤에는 `python3 scripts/same_riders.py --write` 를 다시 돌린다 — 상품만 다른 같은 이름 특약을 한 카드로 묶는 표시(`sg`)·간편심사 감액 메모(`sv`)·띄어쓰기 통일을 다시 만든다. **이름이 같으면 약관 별표도 같다(소유자 확인).** 그래서 같은 이름인데 질병코드·수가코드가 다르면 그건 데이터 오류다 — 스크립트가 '확인 필요'로 출력하면 약관 별표로 바로잡는다(예 : `scripts/fix_same_terms.py`). 상품 간 실제 차이는 간편심사 감액(약관 지급표) 정도이며, 보장개시 문구 차이는 메모하지 않는다.

## 세 산출물은 함께 간다 (원천 = 약관 파싱)

세일즈북 생성기 · 스마트 제안서 · 영업지원도구 배포판은 **같은 특약 마스터**(`proposal_smart/db.json` ← `tool.html` 감수본, `proposal_smart/db_terms_extra.json` ← 약관 PDF 파싱)를 쓴다.
어느 하나의 데이터만 고치고 끝내지 않는다. 약관·tool.html·추출기 중 무엇을 바꿨든 저장소 루트에서

```
python3 scripts/sync_all.py                      # tool.html→db.json · 약관→db_terms_extra.json · 하네스 · 세일즈북 재조립 · 배포판 5종
python3 scripts/sync_all.py --designs <설계서폴더>  # + 설계서 지면 점검(H6) · 회귀 스냅샷 비교
```

를 돌려 세 산출물을 한 번에 맞춘다(약관 재추출을 뺄 때는 `--skip-terms`). 끝나면 바뀐 건수 요약이 나온다 — 질병코드가 바뀐 특약은 약관 원문으로 한 번 더 확인하고, README 변경 기록에 적는다.

## 여러 세션이 같은 저장소를 만진다

- **`main` 이 기준**이다. 소유자가 사내 노트북에서 받아 쓰는 것도 `main` 이다.
- 작업은 브랜치에서 하되 **검증이 끝나면 `main` 으로 합친다.** 브랜치에 오래 묵혀 두면 다른 세션과 갈린다.
- 시작할 때 `git fetch origin main && git log --oneline HEAD..origin/main` 으로 남이 한 일을 먼저 본다.
- `dist/` 의 보고서·검수표에 **다른 세션이 시트를 덧붙여 두는 경우가 있다.** 다시 뽑을 때 그 시트를 지우지 않는다(`export_rules_xlsx.py` 는 기존 시트를 살려 둔다).

## 절대 지키는 것

1. **질병코드(KCD)는 어떤 경우에도 코드에서 만들거나 추정하지 않는다.** 약관 별표와 특약 마스터(`db.json`)에서만 온다. 목록이 없으면 **지급하지 않고 사유를 로그에 남긴다.**
2. **금액도 추정하지 않는다.** 약관 지급금액표에 없는 가입금액·항목은 계산에서 빼고 로그에 남긴다.
3. **규칙표에 없는 담보가 와도 예외를 던지지 않는다.** 계산 제외 + 로그. 오류가 *틀린 금액* 이 아니라 *빈칸* 으로 나타나게 한다.
4. **상품명 화이트리스트로 막지 않는다.** 예외는 `rules.json > exclude_products` 에 사유와 함께 적은 정책 목록뿐이다.
5. **통계·수치는 출처를 붙이거나 '가정값'으로 표기한다.**
6. 테스트 설계서에 **설계사명·고유번호 같은 개인정보**가 있다. 사외로 나가는 캡처는 가린다.
7. 산출물 파일명은 **ASCII** 로 한다(사내 메일·윈도우 호환).
8. `scratchpad/mockup/` 계열의 현대해상 구조 목업은 **원본 일러스트를 떠온 사내 대조용**이다. 고객 배포·사외 유출 금지.
9. 커밋 메시지·PR·코드 주석에 **모델 식별자를 넣지 않는다.**
10. 약관 PDF 는 **두 단 조판**이다. 글자를 뽑으면 둘째 단이 다음 별표 뒤에 섞인다 — 별표(분류표) 코드를 셀 때는 반드시 다음 쪽까지 보고, 자동 추출 숫자만으로 "없다"고 단정하지 않는다(2026-10-02 특정순환계질환 분류표 오판 사례).
11. 치매간병통합케어보험은 스마트 제안서 제공 대상이 아니다(소유자 2026-10-02). 간병인 칸에는 「치매한정」 표시만 맞춰 두었다.
12. **케어프리 M-Basket(GA 알파Plus) ≠ The좋은 M-Basket(GA The좋은 알파Plus).** 앞은 세만기·비갱신 기반(일부 특약 갱신형), 뒤는 연만기·전 특약 갱신형인 다른 상품이다(소유자 2026-10-20). 「The좋은」이 붙은 상품을 앞 상품의 개정판으로 보지 않는다 — 상품 관계는 상품 라인업(`products.html` DATA)에서 먼저 확인한다.

## 계산을 고칠 때 (순서를 지킨다)

1. **약관 원문으로 근거를 확인한다.** 규칙표·마스터가 서로 달라 보이면 약관이 맞다. 같은 이름의 검사·치료라도 **특약마다 대상 범위가 다르다**(구간 전체 vs 수가코드 열거).
2. **고치기 전에 스냅샷을 찍는다.**
   ```
   cd proposal_smart
   python regress.py snap before <설계서PDF폴더>
   ( 코드 수정 )
   python regress.py snap after  <설계서PDF폴더>
   python regress.py diff before after
   ```
   고친 곳만 달라지고 나머지는 **쪽별 글자 차이 0쪽**이어야 한다. `이탈·잘림` 은 0 이어야 한다.
   설계서 PDF 는 **개인정보(설계사명·고유번호)가 있어 저장소에 넣지 않는다.** 소유자가 준 파일을
   세션 작업폴더에 모아 두고 그 경로를 넘긴다(지금 쓰는 7건 : 통합간편 68쪽 · 통합간편 40쪽 · 케어프리 The좋은 ·
   내Mom대로 · 또또암 · 내Mom 5.10.5 · 내Mom대로 30년납).
3. **결과가 안 바뀌어도 고친 것이 듣는지 따로 확인한다.** 테스트 설계서에 그 담보가 없으면 지면은 그대로다 — 담보를 직접 넣어 지급 경로(`scen_engine.pay_lines`)로 확인한다.
4. `api.py` 의 `VERSION` 을 올리고 **`README.md` 맨 위에 변경 기록을 추가한다.** 무엇이 왜 틀렸는지, 금액이 얼마에서 얼마로 바뀌는지 숫자로 적는다. 정상으로 확인한 것도 남겨 다시 건드리지 않게 한다.
5. 규칙표를 고쳤으면 검수표를 다시 뽑는다 — `python export_rules_xlsx.py ../dist/규칙표_KCD검수결과.xlsx` (다른 세션이 붙인 시트는 그대로 남는다)

## 새 상품·신담보·새 약관을 넣을 때 (루프 — 전부 통과할 때까지 돈다)

1. 약관 PDF 를 저장소 루트에 올린다. 소유자는 웹 업로드(파일당 25MB) 대신 GitHub 릴리스 「약관 올리는 곳」(태그 `terms-inbox`)에 여러 개를 한 번에 끌어다 놓는다 — 세션은 `python3 scripts/fetch_terms.py --write` 로 받아 온다(PDF 첫 쪽 상품명으로 같은 상품의 옛 판을 바꾸고 `db_terms_extra.json` 의 약관 이름도 고친다. 채팅 첨부 파일은 `--from <폴더>`). 스마트 제안서 전용이면 `python extract_terms_extra.py "../약관.pdf" 상품명 접두어`, 영업지원도구에도 들어가는 상품이면 `tool.html` 을 고치고 `python extract_db.py ../tool.html`.
2. 첫 쪽 상품명으로 상품라인을 못 읽으면 `build_all.guess_line` 에 한 줄 추가한다(화이트리스트가 아니라 읽기 규칙).
3. `cd proposal_smart && python harness.py --designs <설계서PDF폴더>` — H1~H6.
4. 실패 항목만 고친다 : H1 → 약관 별표·마스터 / H2 → `rules.json` 에 규칙 추가(약관 근거) / H3 → `scen_engine.GOJI`·`matcher` / H4·H5 → 핸들러·규칙 / H6 → `ga_proposal.py`·`ga_spec.py`.
5. 3번으로 돌아간다. **전부 통과**가 나와야 다음으로 간다.
6. 계산을 고쳤으면 위 「계산을 고칠 때」 2~5(regress · VERSION · README · 검수표)를 한다.
7. 올리면 GitHub Actions `proposal-harness` 가 H1~H5 를 다시 돌린다(설계서 PDF 는 저장소에 없으므로 H6 은 세션에서만).

## 어디를 고치나

| 하려는 일 | 파일 |
|---|---|
| 지급 조건·보상 유형 | `rules.json` (규칙 120줄 · 질병코드 그룹표) |
| 특약별 약관 KCD·제외코드·수가코드 | `db.json` — **직접 고치지 않는다.** `tool.html` 데이터를 바로잡고 `python extract_db.py ../tool.html` |
| 내Mom대로·내Mom같은 어린이보험·간편31 특약(스마트 제안서 전용) | `db_terms_extra.json` — **영업지원도구(tool.html 등)에 넣지 않는다**(소유자 지시). 약관 PDF 에서 `python extract_terms_extra.py "../약관.pdf" 상품명 접두어` 로 다시 뽑는다(같은 이름 특약은 db.json 감수 코드를 쓴다) |
| 통합치료비 지급금액표 | `product_data.json` / 상해는 `inj_itc.json` / 생활지원비는 `life_support.json` |
| 계산 엔진 | `scen_engine.py`(규칙 판정·핸들러) · `engine.py`(통합치료비 금액표) |
| 지면·문구·사례 | `gen2.py` |
| 약관 → 데이터 재추출 | `extract_*.py` (명령은 README 실행 요구사항 표) |
| 데이터 바꾼 뒤 세 산출물 한꺼번에 갱신 | `scripts/sync_all.py` (위 「세 산출물은 함께 간다」) |
| 신수술비[기본]·[주요수술] 분류표(수술코드 ADRG) | `surg_new.json` — `python extract_surg_new.py "../약관.pdf"` 로 다시 뽑는다 |
| 3차 안전장치(설계서 뒤쪽 표와 대조) | `verify3.py` |
| 점검 하네스(H1~H6) · GA 칸 스펙 | `harness.py` · `ga_spec.py` · `.github/workflows/proposal-harness.yml` |

`out/` 과 `assets/` 는 저장소에 올리지 않는다. 임시 파일은 저장소가 아니라 세션 작업폴더에 둔다.
