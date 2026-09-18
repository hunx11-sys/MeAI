# 스마트 제안서 생성 API — 프론트엔드 연동 가이드

> proposal_smart v8.9 · AI추진파트 세일즈혁신TF
> **LLM·외부 API를 쓰지 않습니다.** 규칙표(rules.json)와 약관 데이터(JSON)에 따른 계산만 수행하며,
> 실행 중 외부 네트워크 통신이 없습니다. 같은 PDF를 넣으면 항상 같은 결과가 나옵니다.

## 1. 서버 띄우기

가장 쉬운 방법 — 폴더 안의 실행 파일을 두 번 누르면 설치·실행·브라우저 열기까지 한 번에 됩니다.

| 운영체제 | 실행 파일 |
|---|---|
| 윈도우 | `start_windows.bat` |
| 맥 · 리눅스 | `start.sh` |

직접 명령으로 실행할 때는 아래와 같습니다.

```bash
pip install -r requirements.txt
python -m playwright install chromium     # HTML → PDF 렌더 (최초 1회)

python api.py                             # http://127.0.0.1:8080
python api.py 0.0.0.0 9000                # 호스트·포트 지정
```

추가 패키지 설치가 없습니다 — API 서버는 **파이썬 표준 라이브러리(http.server)** 로만 만들었습니다.
브라우저에서 `http://127.0.0.1:8080/` 를 열면 연동 데모 화면이 나옵니다(PDF를 끌어다 놓으면 결과가 보임).

> **주의** — `web/index.html` 파일을 탐색기에서 직접 열면 동작하지 않습니다(서버가 없어 `Failed to fetch`).
> 반드시 서버를 띄운 뒤 **주소창에 `http://127.0.0.1:8080`** 을 입력해 접속하세요.
> 파일로 열었을 때는 화면 위에 그 안내가 표시되며, 'API 주소'를 입력하고 '연결 확인'을 누르면 그 상태로도 사용할 수 있습니다.

## 2. 엔드포인트

| 메서드 | 경로 | 요청 | 응답 |
|---|---|---|---|
| GET | `/health` | — | `{"ok":true,"version":"v8.9","llm":false,"network":false}` |
| GET | `/` | — | 연동 데모 화면(HTML) |
| GET | `/assets/<파일>` | — | 지면이 쓰는 글꼴·로고(미리보기용 정적 파일) |
| POST | `/v1/proposal/pdf` | 상품설명서 PDF | **결과 PDF**(원본 + 생성 지면) `application/pdf` |
| POST | `/v1/proposal/pages.pdf` | 상품설명서 PDF | 생성 지면만 담은 PDF |
| POST | `/v1/proposal/pages.html` | 상품설명서 PDF | 생성 지면 HTML — `<iframe>`에 그대로 띄울 수 있음 |
| POST | `/v1/proposal/audit` | 상품설명서 PDF | 요약 + 감사 로그 JSON |
| POST | `/v1/proposal/riders` | 상품설명서 PDF | 인식한 담보 목록 JSON (생성 없이 빠르게 확인) |
| POST | `/v1/proposal/all` | 상품설명서 PDF | 요약 + 감사로그 + 지면 HTML + 결과 PDF(base64) 한 번에 |

업로드 방식은 두 가지 모두 받습니다.

- `Content-Type: application/pdf` + PDF 바이트를 body 에 그대로 (fetch 권장)
- `multipart/form-data` 의 `file` 필드 (HTML `<input type="file">` 그대로)

CORS는 개발 편의를 위해 모두 열어 두었습니다(`Access-Control-Allow-Origin: *`).
운영 배포 시에는 `api.py` 의 `_cors()` 에서 사내 도메인으로 좁혀 주세요.

## 3. 호출 예

### 결과 PDF 받아 화면에 띄우기

```js
const API = 'http://127.0.0.1:8080';

const blob = await fetch(`${API}/v1/proposal/pdf`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/pdf' },
  body: file,                       // <input type="file"> 의 File 객체
}).then(r => { if (!r.ok) throw new Error('생성 실패'); return r.blob(); });

viewer.src = URL.createObjectURL(blob);
```

### 요약·지면·PDF 한 번에 받기

```js
const d = await fetch(`${API}/v1/proposal/all`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/pdf' },
  body: file,
}).then(r => r.json());

d.total_pages     // 65      결과 PDF 전체 쪽수
d.new_pages       // 9       생성한 지면 수 (0이면 대상 담보 없음)
d.insert_after    // 43      원본 43쪽 뒤에 삽입
d.rider_count     // 151     인식한 담보 수
d.matched         // 133     특약 마스터와 매칭된 담보 수
d.attached        // true    지면을 붙였는지
d.elapsed_sec     // 31.7    처리 시간
d.meta            // 피보험자·보험료·상품명·계약사항 등 PDF에서 읽은 값
d.audit           // 감사 로그(요약·제외 담보와 사유)
d.pages_html      // 생성 지면 HTML (iframe srcdoc 으로 바로 사용)
d.pdf_base64      // 결과 PDF (base64)
```

### 응답 예 — `/v1/proposal/audit`

```json
{
  "ok": true, "attached": true,
  "base_pages": 56, "new_pages": 9, "total_pages": 65, "insert_after": 43,
  "rider_count": 151, "matched": 133, "elapsed_sec": 31.7,
  "meta": { "insured": "고객님", "premium": "669,590원", "product": "(무)메리츠 The건강한 …" },
  "audit": {
    "요약": { "담보수": 151, "구조별": { "dx": 14, "surg": 56, "tx": 48, "day": 11, "care": 9,
                                        "itc": 5, "itc_unknown": 1, "life": 6, "nonmed": 1 },
              "미분류": [], "규칙수": 66, "생성쪽수": 9, "첨부": true, "제외지면": [] },
    "로그": [ { "구분": "KCD없음", "담보": "…", "사유": "…" } ]
  }
}
```

## 4. 응답 코드

| 코드 | 뜻 | 프론트 처리 제안 |
|---|---|---|
| 200 | 정상 | — |
| 400 | PDF가 아니거나 본문이 빔 | 파일 형식 안내 |
| 409 | 대상 담보가 없어 생성 지면이 없음(`pages.pdf` 요청 시) | "스마트 제안서 대상 아님" 안내 후 원본 제공 |
| 503 | 동시 처리 대기 초과 | 재시도 안내 |
| 500 | 생성 중 오류 | 오류 메시지 노출 + 원본 PDF 제공 권장 |

`attached: false` 는 오류가 아닙니다 — 운전자·치아보험처럼 암·뇌·심장·통합치료비 담보가 없는 설계는
지면을 만들지 않고 원본을 그대로 돌려줍니다.

## 5. 성능과 운영 시 고려사항

- 1건 처리에 **약 30초**(원본 56쪽 + 생성 9쪽 = 65쪽). 담보 수가 많으면 더 걸립니다.
- 동시 처리는 기본 **2건**으로 제한했습니다(`api.py` 의 `LOCK = threading.Semaphore(2)`).
  PDF 렌더가 메모리를 쓰므로 서버 사양에 맞춰 조정하세요.
- 요청 상한은 60MB(`MAX_BYTES`)입니다.
- 화면에서 바로 기다리게 하지 말고 **작업 등록 → 완료 알림** 형태를 권합니다.
  프론트에서 폴링이 필요하면 작업 큐는 IT개발파트 표준 방식에 맞춰 붙이는 것이 좋습니다.
- 업로드된 PDF와 작업 폴더는 처리 후 임시 폴더에서 정리됩니다(`out/job_…`는 확인용으로 남습니다 —
  운영에서는 `pipeline.build(..., keep=False)` 로 호출하세요).

## 6. 파이썬에서 직접 쓰기 (API 없이)

```python
from pipeline import build

r = build('원본_상품설명서.pdf')
r['out_pdf']      # 결과 PDF 경로
r['pages_html']   # 생성 지면 HTML 경로
r['audit']        # 감사 로그
r['attached']     # 지면을 붙였는지
```

배치에서 쓰려면 `python pipeline.py 원본.pdf 결과.pdf` 로도 실행됩니다.
