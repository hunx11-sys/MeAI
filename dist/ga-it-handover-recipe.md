# GA 스마트 제안서 — IT 개발파트 인수인계 레시피

작성 : 세일즈혁신TF · 2026-10-23 · 생성기 버전 v8.82
함께 보는 문서 : `ga-system-it-handover-guide.docx`(개발 방향·원칙·검수 기준·유지보수) · `ga-blueprint-final.xlsx`(설계도 · 칸별 담보 매핑 · 특약 마스터) · `ga-cell-map.html`(칸별 특약 지도)

---

## 1. 한 장 요약 — 무엇이 어떻게 돌아가나

```
가입설계서 PDF ──읽기──▶ 담보 목록(담보명 · 가입금액)
                          │  matcher.py / pipeline.py / build_all.py
                          ▼
                 특약 마스터와 짝 맞추기 (db.json · db_terms_extra.json : 약관 별표 질병코드 · 수가코드)
                          │
                          ▼
   132개 칸 사례(ga_spec.py CELLS : 질병코드 · 치료 · 병원 종별 가정값)마다
   계산 엔진(scen_engine.py · 규칙표 rules.json 120줄 · 통합치료비 금액표 product_data.json 등)이
   「이 담보가 이 사례에서 얼마를 지급하나」를 계산 ──▶ 칸 값 = 지급액 합 (집계 방식 first/year/each/itc_only…)
                          │
                          ▼
   지면 : GA 디자인 가안 그림(ga_assets/mock/*.jpg) 위에 값 글자만 얹음(ga_overlay.py · 좌표 overlay_*.json)
          + 세부내역(보장요약 칸의 합산 계산서)은 HTML 표 ──▶ Chromium(Playwright)으로 PDF
```

- **금액·질병코드를 만들어 내는 코드는 없다.** 전부 약관 별표(마스터)와 약관 지급금액표에서만 온다. 모르면 빈칸 + 로그.
- **칸의 정의는 데이터(`ga_spec.CELLS`)다.** 지면은 그 값을 그리기만 한다 → 디자인을 바꿔도 계산은 안 변한다.
- **판정 규칙은 표(`rules.json`)다.** 신담보가 오면 코드가 아니라 규칙 한 줄을 더한다.

## 2. 파일 지도 (무엇을 어디서 고치나)

| 층 | 파일 | 역할 | 바뀌는 때 |
|---|---|---|---|
| 입력 읽기 | `pipeline.py` `matcher.py` `build_all.py` | 설계서 PDF 에서 담보명·가입금액·피보험자·상품명 읽기, 마스터 매칭(`guess_line` : 첫 쪽 상품명으로 상품 라인) | 설계서 양식이 바뀔 때 |
| 원재료 | `db.json`(1,765) `db_terms_extra.json`(2,590) | 특약 마스터 : 특약별 약관 질병코드(k) · 제외코드(x) · 수가코드(hc) — **직접 고치지 않는다**(약관 PDF → `extract_db.py` / `extract_terms_extra.py`) | 상품 개정 |
| 원재료 | `product_data.json` `inj_itc.json` `life_support.json` `cancer_day.json` | 통합치료비 · 상해 통합치료비 · 통합생활지원비 · 암 통합입통원일당 지급금액표 | 상품 개정 |
| 원재료 | `surg5.json` `surg7.json` `surg_new.json` `g131.json` | 1-5종 · 1-7종 · 신수술비 분류표, 130/131대 질병군표 | 약관 별표 변경 |
| 판단 규칙 | `rules.json` | 담보명 → 보상 유형(진단비/수술비/치료비/통합치료비/일당/계산제외) · 지급 조건 · 질병코드 판정 방식 · 사유 문구. 먼저 맞는 규칙이 이긴다 | 신담보 · GA 결정 |
| 계산 엔진 | `scen_engine.py` `engine.py` | `pay_lines(담보목록, 사례)` → 지급 줄(담보명 · 금액 · 사유 · 규칙 id). `engine.py` 는 통합치료비 금액표 계산 | 공식 자체가 바뀔 때만 |
| 칸 정의 | `ga_spec.py` | `CELLS` 132칸(1쪽 53 · 2쪽 42 · 3쪽 37) : 사례(kcd · 치료 · 병원) · 집계 방식 · 표시 조건. `GA_DZ`(주요수술 12) · `CS`(암 사례) · `brain_steps/heart_steps` | GA 칸 구성 변경 |
| 간병인 칸 | `ga_care.py` | 계산 없이 설계서 담보를 읽어 「간병인 보내줌」·미사용 일당 등 결정 | GA 결정 |
| 지면 | `ga_proposal.py` `ga_overlay.py` | 표지 2판 · 1~3쪽(가안 그림 + 값 글자) · 세부내역(HTML 표) · PDF 렌더 · 감사 로그 | 디자인 변경 |
| 지면 자산 | `ga_assets/mock/*.jpg` `overlay_*.json` `Pretendard-*.woff2` | 가안 6장, 칸 자리 좌표(1414×2000px 기준), 글꼴(OFL) | 디자인 변경 |
| 점검 | `harness.py` `regress.py` `verify3.py` | H1~H6 자동 점검 · 고치기 전후 비교 · 설계서 뒤쪽 표 대조 | 매 변경 |
| 실행 | `make_ga.bat` `api.py`(`/v1/ga/pdf`) `ga_preview.py` | 윈도우 드래그 실행 · HTTP 서비스 · 설계서 없이 지면 확인 | — |

## 3. 칸 하나가 채워지는 순서 (예 : 보장요약 「암보장 › 진단금 › 일반암」)

1. `ga_spec.CELLS` 에서 칸 `p1.ca.dx.일반암` : 사례 = 위암 C16 진단, 집계 = `first`(최초 지급 1회분), `na_if_empty`(지급 담보가 없으면 「미가입」).
2. 설계서 담보 70건을 `scen_engine.pay_lines(riders, 사례)` 에 넣는다. 담보마다 `rules.json` 을 위에서부터 훑어 처음 맞는 규칙으로 보상 유형을 정한다(예 : `암진단비(유사암제외)` → `dx_cancer_major`).
3. 규칙의 질병코드 판정(`kcd` : major / codes / g131 / hc …)으로 C16 이 대상인지 본다 — 코드 목록은 마스터(`db.json k`)에서만.
4. 지급 줄이 모이면 칸의 집계 방식으로 더한다 : `first` 는 각 줄의 최초 지급액 합, `year` 는 연 1회 이상 반복되는 줄만, `each` 는 1회당 금액, `itc_only` 는 통합치료비 줄만.
5. 세부내역 쪽에 그 칸의 「구분 / 보장금액 / 특약명 / 가입금액 / 특약별 보장금액」을 그대로 적는다 — **지면의 숫자와 세부내역의 합이 항상 같다**(같은 지급 줄).

설계도 엑셀 `설계도3·4·6·10` 시트와 `③ 칸별 특약(마스터 전체)` 시트에 이 순서가 칸별로 풀어져 있다. `ga-cell-map.html` 은 칸을 누르면 그 칸에 들어올 수 있는 특약 전부와 설계서별 계산 특약을 보여 준다.

## 4. 실행 레시피

```
pip install -r requirements.txt            # pdfplumber pymupdf pypdf reportlab pillow openpyxl playwright
python -m playwright install chromium       # 지면 → PDF 렌더(한 번만)

python ga_proposal.py 설계서.pdf [결과.pdf] [나이]     # 한 건. GA_COVER=1|2 표지 판 · GA_MOCK=0 이면 가안 그림 없이 HTML 지면
python ga_proposal.py <폴더>                           # 폴더 안 PDF 전부 → ga_output/
python harness.py --designs <설계서폴더>              # H1~H6 점검(전부 통과가 합격)
python regress.py snap before <폴더> / snap after <폴더> / diff before after   # 고치기 전후 비교(쪽별 글자 차이 0)
python ga_preview.py 결과.pdf --cover 2               # 설계서 없이 지면 모양 확인(표본 담보)
```

결과 : `<이름>_GA.pdf` + `<이름>_GA_log.txt`(계산 제외 · 빈칸 사유 · 표지에서 못 읽은 항목 · 지면 경고). `api.py` 를 띄우면 `POST /v1/ga/pdf`(PDF) · `/v1/ga/all`(PDF + 감사 로그 JSON).

## 5. 사내 전산 이식 시 바꿔야 할 접점

| 지금(TF 생성기) | 사내 시스템에서 | 비고 |
|---|---|---|
| 설계서 PDF 를 글자로 읽어 담보·가입금액 추출 | 설계 시스템에서 **담보 코드·가입금액·피보험자·가계약번호를 데이터로** 받기 | PDF 읽기(`pipeline/matcher`)가 통째로 빠진다. 담보명 → 마스터 매칭도 담보 코드로 바로 |
| 약관 PDF 파싱 → `db.json` 등 | 상품·담보 코드 마스터 + **약관 별표 질병코드 · 지급금액표 DB** | 별표가 사내에 데이터로 있는지가 1번 확인 사항 |
| `rules.json` 파일 | 규칙 관리 화면(표) | 현업이 개발 없이 고칠 수 있어야 함 |
| `ga_spec.CELLS` | 칸 정의 테이블 | GA 디자인 변경 시 여기만 |
| Chromium 렌더 | 사내 PDF 렌더러 또는 동일 방식 | 가안 그림(JPG) 위 좌표 글자 얹기 — 좌표는 1414×2000px 비율 기준 |
| 로그 파일 | 감사 로그 테이블 | 「계산 제외 · 사유」가 반드시 남아야 함 |

**합격 기준** : 기준 설계서(현재 5건, 추가 예정)를 넣었을 때 132칸 전부가 TF 생성기 결과와 같고 세부내역 금액도 같다(설계도 엑셀 `⑩ 설계서 검증` · `⑪ 설계서 칸별 특약 금액` 시트가 정답지).

## 6. 절대 지킬 것 (코드로 강제되어 있음 — 이식 후에도 유지)

1. 질병코드(KCD)·금액을 코드에서 만들거나 추정하지 않는다 — 목록 없으면 지급 0 + 사유 로그.
2. 규칙표에 없는 담보가 와도 예외를 던지지 않는다 — 계산 제외 + 로그(오류는 틀린 금액이 아니라 빈칸으로).
3. 상품명 화이트리스트로 막지 않는다 — 예외는 `rules.json > exclude_products` 사유 목록뿐.
4. 세부내역(합산 계산서)은 반드시 붙는다(`CALC_PAGES`) — 못 만들면 생성 자체가 실패한다.
5. 설계서에는 개인정보(설계사명·고유번호)가 있다 — 저장·로그 범위를 따로 정한다.

## 7. 2026-10-31 상품개정 선반영(개정안 v6.0 기준 · 정식 약관으로 재확인 필요)

특정순환계질환 통합치료비Ⅱ(기존 표와 동일 → 별칭 · 주요치료Ⅱ N회이상 규칙) · 항암방사선/약물치료비Ⅱ(세부보장 6개 규칙) · 암 통합입통원일당(계산 제외 + 금액표 `cancer_day.json`) · 장기요양돌봄지원금(계산 제외) · 1-5종 체증형(기존 규칙 그대로) · 암보험 신상품 2종 표지 이름. 자세한 것은 `proposal_smart/README.md` v8.81.

## 8. 아직 정해지지 않은 것 (GA·현업 결정 대기)

- 표지 기본 판(1 또는 2) · 꼬리줄 「코드」 값(가계약번호 앞 9자리 여부) · 꼬리 셋째 이름표 「컨설턴트」
- 항암Ⅱ 기본 사례(수술 후 항암 여부) · 암 통합입통원일당 칸 위치
- 표지 그림·로고 고해상도 원본(지금은 가안 JPG 1414×2000)
