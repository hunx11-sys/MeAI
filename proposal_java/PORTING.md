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
| `matcher.py` | `Matcher_` | 담보 알아보기(이름 → 특약 마스터) — `read_proposal` 등 PDF 읽기는 뺀다. 이름이 `java.util.regex.Matcher` 와 겹쳐 밑줄 |
| `build_all.py` | `BuildAll` | `line_from_head` · `guess_line` 만 |
| `pipeline.py` | `Pipeline` | `DesignUnreadable` 등 JSON 길에 쓰는 것만 |
| `code_input.py` | `CodeInput` | 입력 JSON → 담보 줄 |
| `ga_care.py` | `GaCare` | 간병인 칸 |
| `ga_spec.py` | `GaSpec` | 칸 정의 · 칸 값 |
| `ga_proposal.py`(as GP) | `GaProposal` | 자료 부분(VAL · 세부내역 계산 · 머리 정보) — 옛 6쪽 지면은 ga_v2 가 쓰는 것만 |
| `ga_overlay.py`(as OV) | `GaOverlay` | ga_v2 가 쓰는 것만 |
| `ga_v2.py` | `GaV2` | HTML 만들기 · PDF 조립 |
| `api.py` | `Api` | HTTP(JDK 내장 서버) |
| — | `Main` | 명령줄 |
| — | `Py` · `Json` | 언어 차이를 맞추는 공통 도구 |

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

빠른 컴파일 `./build.sh`(javac) · 정식 묶음 `mvn -q -B package`.
