# 자바 판 옮기기 규칙 (proposal_java)

파이썬 판(`proposal_smart/` · GA 스마트 제안서 새 양식 v2)을 자바로 **그대로** 옮긴 것이다.
목표는 하나 — **같은 입력에 파이썬 판과 글자 하나까지 같은 결과.** 그래서 「자바답게 다시 짜기」 를 하지 않고, 파이썬 함수와 1:1 로 옮긴다.
계산을 고칠 때는 파이썬 판을 먼저 고치고(검증 포함), 같은 함수를 여기서 똑같이 고친 뒤 정답지 대조를 다시 돌린다.

## 범위

- 입력 : **담보코드 입력(JSON)** 만 — `proposal_smart/code_input.py` 사양 그대로. 설계서 PDF 읽기(pdfplumber 표 읽기)는 옮기지 않는다(전산 연결은 JSON 으로 한다 · 표 읽기를 다른 부품으로 다시 짜면 「같은 결과」 를 보장할 수 없다).
- 출력 : 같은 PDF(표지 · 보장요약 → 암 ① ② · 뇌혈관 · 심장 → 주요수술 ① ② → 간병인 → 세부내역 → 안내사항) · 계산 로그 · API `/v1/ga2/json/pdf` · `/all` · `/check` · `/health`.
- 자료(특약 마스터 · 규칙 · 금액표 · 분류표 · 지면 틀 · 글꼴)는 **파이썬 판 파일을 그대로 읽는다**(`Py.BASE` — 개발 때는 `../proposal_smart`, 묶음에서는 `data/`). 자료를 자바 쪽에 따로 두지 않는다.

## 짝

| 파이썬 | 자바(`meai.sp`) | 비고 |
|---|---|---|
| `engine.py`(as itc) | `Engine` | 통합치료비 금액표 |
| `scen_engine.py`(as S) | `ScenEngine` | 규칙 판정 · 지급 줄 |
| `desc_engine.py` | `DescEngine` | `life_items` 만(통합생활지원비 설명문 항목표 — scen_engine.ls_items 가 부른다). 설명문을 PDF 에서 읽는 부분은 옮기지 않는다 |
| `matcher.py` | `Matcher_` | 담보 알아보기(이름 → 특약 마스터) — `read_proposal` 등 PDF 읽기는 뺀다. 이름이 `java.util.regex.Matcher` 와 겹쳐 밑줄 |
| `build_all.py` | `BuildAll` | `line_from_head` · `guess_line` 만 |
| `pipeline.py` | `Pipeline` | `DesignUnreadable` 등 JSON 길에 쓰는 것만 |
| `code_input.py` | `CodeInput` | 입력 JSON → 담보 줄 |
| `ga_care.py` | `GaCare` | 간병인 칸 |
| `ga_spec.py` | `GaSpec` | 칸 정의 · 칸 값 |
| `ga_proposal.py`(as GP) | `GaProposal` | 자료 부분(VAL · 세부내역 계산 · 머리 정보) — 옛 6쪽 지면은 ga_v2 가 쓰는 것만 |
| `ga_overlay.py`(as OV) | `GaOverlay` | ga_v2 가 쓰는 것만(틀 그림 굽기는 뺌) |
| `ga_v2.py` | `GaV2` | HTML 만들기 · PDF 조립 |
| `ga_v2.py` 의 그리기 · 조립 | `Render` · `PdfKit` | HTML → 브라우저 → PDF 조각(`Render`) · 틀 위 합성 · 묶기(`PdfKit` — Apache PDFBox). ga_v2 의 `_page` · `_goto` · `render_*` · `_build` 1)~5) |
| (Playwright 가 하던 일) | `Cdp` | 깔려 있는 Chromium · Edge · Chrome 을 직접 띄워 DevTools 프로토콜로 조종 — **바깥 부품 없음**(JDK 내장 WebSocket + `Json`). 아래 「브라우저 조종」 |
| `api.py` | `Api` | HTTP(JDK 내장 서버) |
| — | `SelfTest` | 인수 시험(`Main --selftest`) — 아래 「인수 시험」 |
| — | `Main` | 명령줄 |
| — | `Py` · `Json` | 언어 차이를 맞추는 공통 도구 |
| (CSS · JS 글자) | `Txt` | `golden/gen_consts.py` 가 파이썬 판에서 읽어 적는 긴 글자 상수 — 손으로 고치지 않는다 |

## 옮기는 법

1. **함수 이름은 파이썬 그대로**(snake_case 유지). 모듈 전역 변수도 같은 이름의 `static` 필드. 파이썬 줄과 자바 줄을 나란히 놓고 볼 수 있어야 한다.
2. **자료 꼴은 파이썬 그대로**
   - dict → `Map<String,Object>`(반드시 `LinkedHashMap` — 넣은 순서가 결과에 나온다) · list/tuple → `List<Object>`(`ArrayList`) · set → `LinkedHashSet` 또는 `HashSet`(차례가 결과에 나오면 파이썬 쪽이 정렬하는지 확인)
   - int → `Long` · float → `Double` · bool → `Boolean` · None → `null` · str → `String`
   - **int 와 float 를 섞지 않는다.** 파이썬에서 `1` 과 `1.0` 은 찍히는 글자가 다르다(`'%s' % 1.0` = `1.0`). 사전에 넣는 값은 파이썬과 같은 꼴(Long / Double)로 넣고, 셈은 `Py.add` · `Py.mul` · `Py.sum`(꼴 유지) 또는 꼴을 아는 곳에서는 `long` · `double` 로 직접.
3. **언어 차이는 `Py` 로만 맞춘다** — 직접 `String.format` · `Math.round` · `String.matches` · `replaceAll` · `split` 을 쓰지 않는다.
   - 정규식 : `Py.re(pat)` · `Py.search` · `Py.match`(앞에서부터) · `Py.fullmatch` · `Py.sub`(바꿀 글자는 파이썬 꼴 `\1`) · `Py.findall` · `Py.resplit`. 패턴 글자는 파이썬 것을 **그대로** 복사한다(자바 꼴로 손으로 바꾸지 않는다 — `Py.toJavaRegex` 가 한다).
   - 서식 : `Py.fmt("%s · %d건", a, n)` · 천 단위 `Py.comma` · `str()` → `Py.str` · float 글자 → `Py.repr`
   - 반올림 : `round(x)` → `Py.round(x)`(반은 짝수로) · `round(x, n)` → `Py.round(x, n)` · `int(x)` → `Py.toInt`
   - 참 · 거짓 : `if x:` → `Py.truthy(x)` · `a or b` → `Py.or(a, b)` · `d.get(k)` → `Py.get(d, k)` · `d.get(k, v)` → `Py.get(d, k, v)`
   - 같음 · 차례 : `==` → `Py.eq`(수 · 목록 · 사전) / 문자열끼리는 `equals` · `sorted(xs, key=…)` → `Py.sorted`(안정 정렬)
   - 문자열 : `strip()` → `Py.strip` · `split()` → `Py.split(s)` · `s[a:b]` → `Py.slice`
4. 모듈을 읽을 때 한 번 하는 일(JSON 읽기 · 색인 만들기)은 `static { }` 블록에, 파이썬과 같은 차례로.
5. 주석은 파이썬 것을 다 옮기지 않아도 된다. 함수 위에 「파이썬 `모듈.함수`」 만 알 수 있으면 된다(이름이 같으니 대개 필요 없다). 모델 식별자 · 정보계 코드 번호를 적지 않는다.
6. 예외 : 파이썬이 던지는 곳에서 같은 뜻의 예외를 던진다(`ValueError` → `IllegalArgumentException` · `InputError` · `DesignUnreadable` 은 같은 이름의 클래스).

## 정답지 대조(단계마다 「다른 곳 0」 이어야 다음으로)

정답지는 파이썬 판이 낸 결과다. 설계서 · 정보계 표에서 나온 것이라 **저장소에 넣지 않는다**(세션 작업폴더). 뽑는 스크립트(`golden/*.py`)와 견주는 자바 프로그램(`src/test/java/meai/sp/Golden*.java`)만 저장소에 둔다.

| 단계 | 파이썬이 내는 것 | 자바가 같아야 하는 것 |
|---|---|---|
| 0 | `golden/py_selftest.py` | `PySelfTest` — Py · Json 의 글자 꼴 |
| 1 | `golden/dump_engine.py` | `GoldenEngine` — 이름 분류 · 특약 전수 × 칸 사례의 지급 줄 · 로그 |
| 2 | `golden/dump_match.py` | `GoldenMatch` — 정보계 이름 × 상품 라인 매칭 · 입력 JSON → 담보 줄 |
| 3 | `golden/dump_cells.py` | `GoldenCells` — 설계별 칸 값 · 정보계 전 줄 한 담보 설계 칸 값 |
| 4 | `golden/dump_html.py` | `GoldenHtml` — 쪽별 HTML 글자 그대로 |
| 5 | 파이썬 판 PDF | 완성 PDF 쪽별 글자 · 인쇄 검증 |

2 · 3단계 돌리는 법(정답지는 세션 작업폴더 `<G>` 에) :

```
python3 golden/dump_match.py <G>/match <정보계 rows.json> <입력 JSON 폴더> [code_map.json]      # 입력 묶음은 golden/cases.py 가 만든다(실제 설계 입력 + 틀린 입력 · 가장자리 값 + 담보 하나짜리 설계)
python3 golden/dump_cells.py <G>/cells <G>/match <정보계 rows.json> <code_map.json>              # spec · designs · rows(정보계 전 줄 — scripts/codemap/audit_rows.py 와 같은 방식 · 약 3분)
java -Xmx4g -cp target/classes:target/test-classes meai.sp.GoldenMatch <G>/match
java -Xmx8g -cp target/classes:target/test-classes meai.sp.GoldenCells <G>/cells <G>/match [spec] [designs] [rows]
```

견주기는 `src/test/java/meai/sp/G.java` 하나가 한다(값 · 열쇠 차례 · 정수/소수 꼴까지). 틀린 JSON 의 영문 까닭 글자(파이썬 json 모듈이 내는 글)만 앞 글자로 견준다.

4 · 5단계 돌리는 법(정답지 `<G>` · 입력 JSON 폴더 `<IN>` · 자바 결과 폴더 `<J>` — 모두 세션 작업폴더) :

```
python3 golden/gen_consts.py                                                    # 긴 CSS · JS 상수(Txt.java)를 파이썬 판에서 다시 적는다 — 파이썬 판의 CSS · JS 를 고쳤을 때
GA_CODE_MAP=<code_map.json> python3 golden/dump_html.py <G>/html <IN>/*.json     # 파이썬 판이 브라우저에 넘기는 HTML · info · 로그 · 칸 값 + 완성 PDF(1건 6~20초)
python3 golden/cases_html.py <정보계 rows.json> <IN2>                            # 실제 설계에 없는 갈래(간병인 181일 · plus · 체증형 · 상해 간병인만 · 10년 뒤 2배 · 상품 라인 안 맞음 · 머리 정보 없음 · 큰 금액)를 덮는 덧입력
GA_CODE_MAP=<code_map.json> java -Xmx4g -cp "target/classes:target/test-classes:$(cat target/cp.txt)" meai.sp.GoldenHtml <G>/html <IN> <J> [이름 …]   # 쪽별 HTML 글자 그대로 + info · 로그 · EXTRA · 칸 값 · 담보 줄 → <J>/<이름>.java.pdf
python3 golden/cmp_pdf.py <G>/html <J>                                           # 완성 PDF : 쪽수 · 낱말 좌표 · 72dpi 픽셀
GA_CODE_MAP=<code_map.json> python3 golden/verify_java_pdf.py <IN> <J>           # 인쇄 검증 : 자바 PDF 의 글자를 다시 읽어 파이썬 판 계산 값과 대조(verify_v2 의 점검 함수 그대로)
python3 golden/dump_master_rows.py <G>/master_rows.json && java … meai.sp.GoldenMasterRows <G>/master_rows.json      # 설계도용 master_rows
python3 golden/cmp_api.py http://127.0.0.1:18081 http://127.0.0.1:18082 <입력.json …>   # 파이썬 api.py(18081)와 자바 `Main serve`(18082)를 띄워 놓고 같은 요청의 상태코드 · 응답 JSON
```

GA_MASK=1 로 뽑은 정답지는 `GoldenHtml` 도 GA_MASK=1 로 돌린다. `GoldenHtml` 의 견주기가 실제로 잡는지는 정답지를 일부러 틀리게 한 사본으로 확인한다.

자바 판에 없는 것(일부러) : 설계서 PDF 읽기 · GA_MOCK=0(가안 그림 없이 전부 HTML 로 그리는 예전 방식 — `GaV2.cover_summary_html` 이 오류로 알린다) · 틀 그림 굽기(`ga_overlay.template` 의 PIL 그리기 — 자료 폴더의 `ga_assets/mock/tpl_*.png` 를 그대로 쓴다) · `calibrate` · `shrink_images`.

## 브라우저 조종(`Cdp` — Playwright 를 쓰지 않는다)

파이썬 판은 Playwright 로 크로뮴을 조종한다. 자바 판은 Playwright for Java 를 쓰지 않고(딸린 `driver-bundle` 이 198MB 이고 실행 때 node 실행 파일을 임시 폴더에 풀어 돌린다 — 사내망 반입 · 보안 프로그램에 걸리기 쉽다) `Cdp` 가 같은 일을 직접 한다. 딸린 부품은 PDFBox 계열뿐이다(`target/lib` 약 3.7MB).

- 띄우기 : 실행 파일 + Playwright 1.49 의 기본 스위치(`chromiumSwitches`) + `--headless` · `--hide-scrollbars` · `--mute-audio` · `--blink-settings=…` · `--no-sandbox` + `--user-data-dir=<임시 프로필>` · `--remote-debugging-port=0` · `--no-startup-window` — 목록은 `Cdp.SWITCHES`. 조종 주소는 프로필 폴더의 `DevToolsActivePort` 에서 읽는다.
- 쪽 : 새 브라우저 컨텍스트 → 쪽 → 초점 흉내 · 뷰포트 794×1123(배율 1) · 기본 글꼴 가족(운영체제별 — Playwright `defaultFontFamilies`) · 매체(인쇄 + 색 구성 light · 움직임 no-preference · 강제 색 none).
- PDF : `Page.printToPDF` 에 Playwright `crPdf` 와 같은 인자(종이 크기는 인치 = px ÷ 96 · A4 = 8.27 × 11.7 · 여백 0 · 배율 1 · 꼬리표 없음).
- 브라우저 찾기 : `GA_CHROMIUM` → `/opt/pw-browsers/chromium`(파일이면) → `Render.CHROME_CAND`(윈도우 Edge · Chrome · 리눅스 흔한 경로) → PATH(`chromium` · `google-chrome` · `msedge` …). 없으면 `GA_CHROMIUM` 을 넣으라고 알린다.
- 끝 : 프로그램이 끝날 때(그냥 끝나든 · 오류든 · 종료 신호든) 종료 훅이 브라우저를 닫고 임시 프로필을 지운다. 한 동작 120초(`Cdp.TIMEOUT_MS`) 넘으면 오류.
- **이 부분을 고치면 반드시** 4 · 5단계 대조를 전부 다시 돌려 `cmp_pdf.py` 가 「다른 픽셀 0」 인지 본다(스위치 하나 · 기다림 하나가 글자 자리를 바꿀 수 있다). 파이썬 판이 Playwright 판을 올리면 `SWITCHES` · 글꼴 표를 그 판의 것으로 다시 맞춘다.

## 인수 시험(`Main --selftest` — 파이썬 없이)

받는 쪽(IT)이 「받은 묶음이 정답과 같은 결과를 내는지」 확인하는 명령이다.

```
python3 golden/make_selftest.py <세트 폴더> <입력.json …>      # (TF) 파이썬 판으로 정답을 만든다 : <이름>.json · <이름>.expected.pdf · <이름>.expected.json
java -jar smart-proposal.jar --selftest <세트 폴더> [이름 …]   # (받는 쪽) 입력마다 PDF 를 만들어 <세트 폴더>/out/ 에 두고 견준다 → 「결과 : 전부 통과 — N건 · N쪽」 · 종료코드 0 / 1
```

견주는 것 : ① 요약(쪽수 · 간병인 쪽 · 세부내역 쪽수 · 담보 수 · 인식 수 · 상품 · 보험료 · 경고 · 계산 로그 글자 — 처리 시간만 뺌) ② 쪽수 · 쪽 크기 ③ 쪽별 글자(두 PDF 를 같은 방법(PDFBox)으로 읽어 공백을 지운 글자가 같은지 + 글자마다 자리 0.5pt 안). 정답이 「만들지 않음」(입력 사양 위반 · 담보를 하나도 못 찾음)이면 같은 까닭 글자로 멈추는지.
정답을 담보 식별표 없이 만들었으면(요약의 `code_map:false`) 시험도 식별표 없이 돈다.
세트를 만들 때 : 실제 설계에서 나온 입력은 **이름 · 가계약번호 · 소속 · 설계사 · 전화를 가짜 값으로 바꾼 뒤** 만든다(정답 PDF 에 그대로 찍힌다). 세트에는 정보계 담보명 · 단위상품코드 · 담보코드가 들어 있어 사내 자료다 — 저장소에 넣지 않는다.

빠른 컴파일 `./build.sh`(javac) · 정식 묶음 `mvn -q -B package`.
