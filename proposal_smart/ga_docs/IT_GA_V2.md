# GA 스마트 제안서 새 양식(v2) 생성 프로그램 — IT 인계 안내

세일즈혁신TF · 2026-11-13 · 계산 버전은 `api.py` 의 `VERSION`(이 묶음을 만든 판은 맨 아래 `VERSION.txt`)

설계서(상품설명서) PDF 한 건을 올리면 그 자리에서 읽고 계산해 **GA 스마트 제안서 새 양식 PDF(15~19쪽)** 를 돌려주는 프로그램입니다.
2026-11-11 회의에서 정한 「영업용 풀버전」 양식입니다.
웹 서버(HTTP API + 업로드 화면)와 명령줄 두 가지로 돌릴 수 있습니다.
LLM · 외부 API 호출이 없고, 실행 중에 바깥 인터넷을 쓰지 않습니다.

---

## 1. 처리 흐름

```
PDF 업로드
 → ① 설계서 읽기      ga_proposal.load · pipeline / pdfplumber · PyMuPDF
                       피보험자 · 상품명 · 보험료 · 가입담보표(담보명 · 가입금액)
 → ② 담보 인식        matcher.py
                       특약 마스터 db.json(영업지원도구 감수본) + db_terms_extra.json(약관 PDF 파싱)
 → ③ 지급 계산        scen_engine.py + rules.json(지급 규칙) + ga_spec.py(칸 정의 · 사례)
                       칸마다 「어느 특약에서 얼마」 지급 줄을 만든다
 → ④ 지면 그리기      ga_v2.py
                       HTML → Chromium(playwright) PDF + v41 디자인 틀(ga_assets/v2/tpl.pdf) 위에 값 합성
 → PDF + 계산 로그(빈칸 · 0원이 된 이유)
```

### 쪽 구성

1. 표지 · 보장요약
2. 치료 여정
3. 암 보장 ① ② · 뇌혈관 · 심장
4. 주요수술 ① ②
5. 간병인 쪽 — 아래 규칙대로 고른다
   - 간병인지원 담보 → 「지원 가입자」 쪽
   - 간병인사용 담보 → 「사용 가입자」 쪽
   - 둘 다 있으면 두 쪽
   - 둘 다 없으면 지원 + 사용을 함께 보여 주는 쪽
6. 보장 점검
7. 보장금액 세부내역 — 담보 수에 따라 3~7쪽
8. 안내사항

### 금액 원칙

다음 세 가지는 바꾸지 말아 주세요(저장소 `CLAUDE.md`).

- **질병코드 · 금액을 추정하지 않습니다.** 약관 별표 · 지급금액표에 없으면 계산에서 빼고 로그에 남깁니다. 틀린 금액 대신 빈칸이 나옵니다.
- 지면 금액은 계산 엔진 칸 값 그대로입니다.
- 아래 두 경우에는 PDF를 만들지 않고 오류로 멈춥니다.
  - 수술 카드 합계 ≠ 보장요약 칸
  - 세부내역 구분 합계 ≠ 특약별 합

---

## 2. 들어 있는 것

| 위치 | 무엇 |
|---|---|
| `api.py` | HTTP 서버(파이썬 표준 라이브러리) · 업로드 화면 `/` · API `/v1/ga2/*`(새 양식) · `/v1/ga/*`(기존 GA 6쪽) · `/v1/proposal/*`(9쪽 지면) |
| `web/index.html` | 업로드 화면(PDF 끌어다 놓기 → 「GA 새 양식 생성」) |
| `ga_v2.py` | 새 양식 생성기(명령줄로도 실행) |
| `ga_v2_template.py` | v41 디자인 → 빈 틀(`tpl.pdf`) · 값 자리(`slots.json`)를 다시 만들 때만 씀. 원본 v41 PDF 는 개인정보가 있어 넣지 않음 |
| `ga_proposal.py` · `ga_spec.py` · `ga_care.py` · `ga_overlay.py` | 설계서 읽기 · 칸 정의 · 간병인 칸 · 표지/보장요약(기존 GA 양식 공용) |
| `scen_engine.py` · `matcher.py` · `engine.py` · `pipeline.py` | 계산 엔진 · 담보 인식 · 통합치료비 금액표 |
| `db.json` · `db_terms_extra.json` · `rules.json` · `*.json` | 특약 마스터 · 지급 규칙 · 금액표 · 분류표 |
| `ga_assets/` | 글꼴(Pretendard · 나눔고딕, SIL OFL) · GA 가안 그림 · 새 양식 틀 `v2/` · 아이콘 |
| `start_windows.bat` · `start.sh` · `start_offline.bat` | 서버 켜기(설치 확인 포함) |
| `make_ga2.bat` | 서버 없이 PDF 를 끌어다 놓아 바로 만들기(윈도우) |
| `harness.py` | 점검 하네스 H1~H5(마스터 · 규칙 · 칸 전수 계산 점검, 약 1분) |
| `API.md` · `README.md` | API 전체 설명 · 변경 기록(버전별 무엇을 왜 바꿨는지) |

약관 별표 원본(`source/`)은 넣지 않았습니다. 분류표를 다시 뽑는 `extract_*.py` 는 저장소에서 TF 가 돌립니다. 실행에는 필요 없습니다.

---

## 3. 설치

### 준비물

- **Python 3.10 ~ 3.13**(3.11 권장)
- 패키지 : `pip install -r requirements.txt`
  - pdfplumber · PyMuPDF · pypdf · reportlab · playwright · pillow
- PDF 를 그리는 Chromium : `python -m playwright install chromium`
  - 폐쇄망이면 이 단계 대신 PC 에 깔린 **Edge · Chrome** 을 씁니다.
  - 환경변수 `GA_CHROMIUM=<msedge.exe 경로>` 를 주면 세 양식(새 양식 · 기존 GA 6쪽 · 9쪽) 모두 그 브라우저를 씁니다. `start_offline.bat` · `make_ga_offline.bat` 이 경로를 넣어 줍니다.
  - `GA_CHROMIUM` 없이도 **새 양식**은 기본 설치 경로의 Edge · Chrome 을 찾아 씁니다. 기존 GA 6쪽 · 9쪽은 `GA_CHROMIUM` 이 있어야 합니다.
- 인터넷이 없는 PC 에서 패키지를 설치하는 방법(`start_offline.bat` 이 이 목록 그대로 설치합니다)
  1. 인터넷 되는 PC 에서 아래 명령으로 `wheels` 폴더를 만듭니다.
     ```
     python -m pip download pdfplumber "pymupdf<1.26" pypdf reportlab playwright pillow openpyxl -d wheels --platform win_amd64 --only-binary=:all: --python-version 3.11
     ```
  2. `wheels` 폴더를 묶음 폴더 안에 옮겨 두고 `start_offline.bat` 을 실행합니다. 직접 설치할 때는 아래 명령입니다.
     ```
     python -m pip install --no-index --find-links wheels pdfplumber "pymupdf<1.26" pypdf reportlab playwright pillow openpyxl
     ```

### 자원

| 항목 | 값 |
|---|---|
| 1건 처리 시간 | 약 15~35초(담보 수에 따라. 시험 18건 10~25초) |
| 메모리 | 1건 처리 중 약 0.8GB(파이썬) + Chromium 약 0.2~0.4GB |
| 결과 PDF | 1건 약 5.5MB |
| 디스크 | 결과를 저장하지 않습니다. 업로드 · 중간 파일은 건마다 임시 폴더에 만들고 끝나면 지웁니다(아래 6) |

---

## 4. 실행

### 웹 서버(업로드 화면 + API)

```
python api.py                    # http://127.0.0.1:8080
python api.py 0.0.0.0 8080       # 다른 PC 에서 접속하게
```

1. 브라우저에서 `http://<서버>:8080/` 을 엽니다.
2. PDF 를 끌어다 놓습니다.
3. **「GA 새 양식 생성」** 을 누릅니다.
4. 20초 안팎이면 다음이 보입니다.
   - 미리보기 · 쪽수 · 간병인 쪽 · 인식 담보 · 계산 로그
   - PDF 내려받기

윈도우는 `start_windows.bat` 을 두 번 누르면 됩니다(맥 · 리눅스 `start.sh`).

### 명령줄

```
python ga_v2.py 설계서.pdf 결과.pdf     # 한 건
python ga_v2.py 폴더                     # 폴더 안 PDF 전부 → ga_output\<이름>_GA2.pdf + _log.txt
GA_MASK=1 python ga_v2.py 설계서.pdf     # 피보험자 · 설계번호 · 소속 · 컨설턴트 · 전화를 가린 견본
```

---

## 5. API — 새 양식

요청은 두 방식 모두 받습니다.

- `Content-Type: application/pdf` 로 PDF 바이트를 본문에 그대로
- `multipart/form-data` 의 `file` 필드

업로드 상한은 60MB 입니다.

| 주소 | 응답 |
|---|---|
| `POST /v1/ga2/pdf` | 새 양식 PDF(`application/pdf`, `ga2_proposal.pdf`) |
| `POST /v1/ga2/all` | JSON(아래) |
| `GET /health` | `{"ok":true,"version":…,"formats":{…}}` |

### `/v1/ga2/all` 응답

| 필드 | 뜻 |
|---|---|
| `ok` | `true` |
| `format` | `"ga2"` |
| `product` · `premium` | 상품명 · 월 보험료(설계서에서 읽은 글자) |
| `pages` · `detail_pages` | 전체 쪽수 · 세부내역 쪽수 |
| `care_pages` | 고른 간병인 쪽. `"support"` · `"use"` · `"none"` 중 하나 또는 둘 |
| `care_pages_ko` | `care_pages` 의 한글 이름 |
| `rider_count` · `matched` | 설계서에서 읽은 담보 수 · 특약 마스터와 맞춘 수 |
| `riders` | 인식 담보 목록. `no` · `name` · `man`(가입금액 만원) · `matched` 등 |
| `warn` | 지면 경고(넘침 · 글자층 오류). 정상이면 `[]` |
| `elapsed_sec` | 처리 시간(초) |
| `log` | 계산 로그 텍스트. 빈칸 · 0원이 된 담보와 그 이유 |
| `pdf_base64` | 결과 PDF |

### 오류 응답

모든 오류는 JSON `{"ok":false,"error":"…"}` 로 옵니다.

| 코드 | 뜻 |
|---|---|
| 400 | PDF 가 아님(사내 보안 DRM 으로 잠긴 파일이면 그렇게 알려 줌) · 본문 없음 · 60MB 넘음 |
| 422 | 설계서를 읽지 못해 만들지 않음(v8.98) — 글자가 없는 그림 PDF(스캔 · 캡처) · 깨진 · 암호 PDF · 가입설계서가 아닌 문서 · 담보를 하나도 못 찾음. `error` 에 이유와 할 일이 쉬운 말로 들어 있으니 화면에 그대로 보여 주세요 |
| 503 | 대기가 180초를 넘음, 또는 새 양식 작업이 멈춰 재시작이 필요한 상태 |
| 504 | 새 양식 1건이 600초(환경변수 `GA2_TIMEOUT` 로 바꿈)를 넘김(지면을 그리는 크로뮴이 멈춘 것으로 봄). 그 뒤로 `/health` 가 503 이 되니 서버를 다시 켜 주세요 |
| 500 | 생성 중 오류. 수술 카드 · 세부내역 합계 점검에 걸린 경우를 포함하며, 메시지에 이유가 들어 있음 |

### 호출 예

```
curl -X POST -H "Content-Type: application/pdf" --data-binary @설계서.pdf http://127.0.0.1:8080/v1/ga2/pdf -o 결과.pdf
curl -F "file=@설계서.pdf" http://127.0.0.1:8080/v1/ga2/all
```

```js
const r = await fetch(API + '/v1/ga2/all',
  { method: 'POST', headers: { 'Content-Type': 'application/pdf' }, body: file });
const d = await r.json();
// d.pages, d.care_pages, d.log, d.pdf_base64
```

---

## 6. 운영할 때 알아 둘 것

- **동시 처리**
  - 서버 프로세스 하나에서 생성은 **한 번에 1건**씩입니다(새 양식 · 기존 GA 6쪽 · 9쪽 모두 같은 줄). 동시에 들어오면 차례로 처리하고, 2건까지 받아 두며, 180초 넘게 기다리면 503 입니다.
  - 설계서 상태와 계산 로그를 모듈 안에 두기 때문이고, 새 양식은 지면을 그리는 Chromium 을 하나 띄워 두고 같은 작업 스레드에서만 씁니다(playwright 규칙).
  - 처리량을 늘리려면 **프로세스를 여러 개(포트마다 하나) 띄우고 앞에 부하분산**을 두세요. 프로세스마다 메모리 약 1GB 를 잡아 주세요.
- **상태 확인 · 재시작**
  - `GET /health` 는 정상이면 200, 새 양식 작업이 600초를 넘겨 멈춘 뒤에는 503(`ok:false`)입니다. 부하분산 · 서비스 관리자가 이것을 보고 프로세스를 다시 켜게 해 주세요.
  - Chromium 이 처리 중에 죽으면 새로 띄워 그 건을 한 번 더 만듭니다.
- **개인정보**
  - 설계서에는 고객 · 설계사 정보가 있습니다.
  - 업로드 파일은 건마다 임시 폴더(운영체제 임시 폴더의 `sp_in_*`)에 두고 응답 뒤 지웁니다. 9쪽 지면 작업 폴더도 그 안에 만듭니다.
  - 새 양식 중간 파일(HTML · PDF 조각)은 `out/v2tmp/job_*` 에 만들고 끝나면 지웁니다. `GA_V2_KEEP=1` 이면 남겨 두며, 지면 점검용입니다.
  - 처리 중에 서버가 꺼져 남은 것은 서버를 켤 때와 요청이 올 때 「만든 지 1시간 넘은 것」 을 지웁니다.
  - 서버는 결과를 저장하지 않습니다.
- **인증 · CORS**
  - `api.py` 에는 인증이 없고, CORS 는 모든 출처(`*`)를 허용합니다.
  - 사내망 안에서만 열고, 필요한 인증 · 허용 출처는 앞단(게이트웨이 · 리버스 프록시)이나 `api.py` 의 `_cors` 에서 맞춰 주세요.
- **로그** : 접속 로그는 표준 오류 출력에 한 줄씩 나옵니다. 계산 로그는 응답의 `log` 에 들어 있습니다.
- **미리보기** : 업로드 화면의 미리보기는 브라우저의 PDF 뷰어로 보여 줍니다(Edge · Chrome 기본 기능).
- **넣는 파일** : 설계 시스템에서 「PDF 저장(다운로드)」으로 받은 **가입설계서 원본 PDF** 입니다(첫머리에 「가입담보리스트」 표가 있는 것).
  - 스캔본 · 화면 캡처 · 「그림으로 인쇄」 한 PDF, 사내 보안(DRM)으로 잠긴 파일, 청약서 · 상품설명서만 따로 받은 파일은 글자를 읽지 못합니다.
  - v8.97 까지는 이런 파일도 멈추지 않고 금액이 모두 「0만원」 · 이름이 「-」 인 빈 제안서를 만들었습니다. **v8.98 부터는 만들지 않고 이유를 알려 줍니다**(API 422 · 명령줄은 결과 폴더에 `…_FAILED.txt`).
  - 설계서에서 담보를 한 건이라도 계산할 수 있으면 지금처럼 만들고, 못 찾은 담보만 계산 로그에 「계산 제외」 로 남깁니다.

---

## 7. 약관 · 데이터가 바뀔 때

- 특약 마스터 · 지급 규칙은 저장소(`main`)에서 관리합니다.
- 약관 판이 바뀌면 TF 가 저장소에서 `python3 scripts/sync_all.py` 로 마스터를 갱신하고 점검을 통과시킵니다.
- 그다음 **이 묶음을 다시 만들어 드립니다.** 저장소 루트에서 `python3 scripts/build_ga_v2_package.py` 를 실행합니다.
- 변경 내용은 `README.md` 맨 위 변경 기록에 버전별로 있습니다.

### 받은 뒤 점검

- `python harness.py` — H1~H5 가 「전부 통과」 여야 합니다.
- 업로드 화면에서 설계서 한 건을 만들어 보세요.
  - 계산 로그 4번째 줄(「담보 N건 · N쪽 · 간병인 쪽 : …」)의 쪽수 · 간병인 쪽이 화면과 같은지 봅니다.
  - `[지면 경고] 없음` 인지 봅니다.

---

## 8. 아직 정해지지 않은 것(지면에 「확정 필요」 로 표시됨)

- 간병인 지원 쪽 : 신청 전화번호 · 공동간병인 문구
- 간병인 사용 쪽 : 청구 서류 목록
- 「연간 1회」 줄 체증형 범위 표시 여부 · 미가입 칸 표시(새 쪽 「미가입」 / 보장요약 「0만원」) 통일 — GA 확인 중
