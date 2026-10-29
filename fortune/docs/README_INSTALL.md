---
date: 2026-10-29
tags: [오늘의운세, 웹탑재, 폐쇄망, 가이드]
projects: [05_MeAI_홈_넛지기획]
version: v2
---

# 오늘의 운세 v2 · 사내 웹페이지 · 폐쇄망 탑재 가이드

> 대문에서 **사주팔자 / 타로점**을 골라 보는 운세 페이지입니다. 정적 파일만으로 동작하고 **인터넷 연결이 없어도** 됩니다.
> 구조 · 계산식 · 연출은 `BLUEPRINT.md`(보기 좋은 판 `BLUEPRINT.pdf`), 코드 원문은 `SOURCE_ALL.md`, 파일 목록 · 해시는 `MANIFEST.txt`.

## 받은 것

| 파일 · 폴더 | 용도 |
|---|---|
| `web/` | **서버에 올릴 폴더 그대로** (index.html · css · js · img · fonts, 92개 · 약 2.6MB) |
| `unse_web.zip` | `web/` 압축본 (zip 안 폴더 이름 `unse/`) |
| `single/unse_saju_tarot.html` | **한 파일판** (3.5MB). 서버 없이 더블클릭 · 카톡 · 메일 · USB 로 전달 |
| `BLUEPRINT.md` · `.pdf` · `.html` | 개발 설계도 (화면 흐름 · 사주 계산 · 점수 공식 · 타로 · 디자인 · 보안 · 배포 · 검증 기록) |
| `SOURCE_ALL.md` | `web/` 텍스트 파일 원문 전체 (자동 생성 · 검토용) |
| `MANIFEST.txt` | 패키지 안 모든 파일의 크기 · SHA-256 (반입 심사 · 변조 확인용) |
| `server_config/` | IIS · 톰캣 · nginx · 아파치 설정 예시 (MIME · 보안정책 헤더) |
| `tools/` | 검증 도구 : 파이썬 사주 엔진 · 40,543일 대조, 엄격한 CSP 시험 서버, 자동 점검 |
| `source/` | 개발 원본 (조립 스크립트 · 원본 화면 · 그림 · 글꼴 · v1 원본) |
| `LICENSES/` | 글꼴 사용권(OFL) · 타로 그림 출처 |

## 1분 탑재

1. `unse_web.zip` 을 풀어 `unse/` 폴더를 웹서버 정적 경로에 올립니다.
   예: `https://intranet.회사.com/unse/`
2. 서버가 `.webp` · `.woff2` 를 아는지 확인합니다 (아래 '서버 설정'). 오래된 IIS 는 이 두 줄이 꼭 필요합니다.
3. 브라우저에서 `…/unse/` 를 엽니다. 끝.

빌드 · 설치 · DB · API 키가 필요 없습니다. 서버 언어(Java · .NET · PHP · Node)와 상관없이 정적 파일만 내려주면 됩니다.

### 서버 설정 체크

| 항목 | 값 |
|---|---|
| MIME | `.html` text/html · `.css` text/css · `.js` application/javascript · `.svg` image/svg+xml · **`.webp` image/webp** · **`.woff2` font/woff2** |
| 문자 인코딩 | UTF-8 (모든 텍스트 파일 UTF-8) |
| 캐시 | `index.html` 은 no-cache 권장 (나머지는 캐시해도 됨) |
| HTTPS | 권장. 휴대폰 **공유(카톡으로 보내기) · 클립보드 복사**는 HTTPS(또는 localhost)에서만 동작 |

서버별 예시 파일 : `server_config/iis-web.config`, `tomcat-web.xml`, `nginx.conf`, `apache.htaccess`

증상으로 찾기

| 증상 | 원인 |
|---|---|
| 타로 카드 앞면이 빈 크림색 | `.webp` MIME 이 없어 404 · 406 |
| 제목이 명조가 아니라 고딕 · 바탕체 | `.woff2` MIME 이 없거나 회사 정책이 글꼴을 막음 (기능은 정상) |
| 카톡으로 보내기를 누르면 글만 복사됨 | HTTP 로 열었거나 브라우저 · 웹뷰가 Web Share 미지원 |
| 익스플로러에서 안내 화면만 뜸 | 정상. 엣지로 자동 이동. 엣지도 IE 모드면 IT 에서 이 주소를 IE 모드 목록에서 빼야 함 |

## 페이지에 넣는 방법

### A. 단독 페이지 (가장 쉬움, 권장)

```html
<a href="/unse/">오늘의 운세</a>
<a href="/unse/#saju">사주 바로가기</a>
<a href="/unse/#tarot">타로 바로가기</a>
```

### B. 기존 포털 페이지 안에 끼워 넣기 (iframe)

```html
<iframe src="/unse/" title="오늘의 운세"
        width="100%" height="900" allow="clipboard-write; web-share"></iframe>
```

- `allow="web-share"` 가 있어야 iframe 안에서도 휴대폰 공유창이 열립니다.
- 운세 페이지는 `frame-ancestors 'self'` 로 같은 사이트 안에서만 끼울 수 있게 해 두었습니다. 다른 도메인 포털에 끼우려면 그 도메인을 추가합니다.
- **포털 페이지 쪽** 보안정책에도 `frame-src 'self'`(또는 `child-src`)가 있어야 액자가 열립니다. 없으면 빈 칸이 됩니다.
- 크기 · 테두리는 포털 CSS 에서 `iframe` 에 지정합니다 (인라인 `style` 속성이 막힌 포털이 많음).

### C. 사내 앱(웹뷰)

- 앱이 `web/` 을 서버 주소(https)로 띄우는 것이 가장 좋습니다.
- 앱 안에 파일로 넣고 `file:///…/index.html` 로 열면 화면 · 계산은 되지만, 브라우저 보안 규칙 때문에 **저장 이미지에 카드 그림이 빠집니다**(틀 · 이름 · 점괘는 그대로). 이 경우 `single/` 한 파일판을 넣으면 그림까지 저장됩니다.

### D. 폐쇄망 PC · 파일 전달

`single/unse_saju_tarot.html` 하나만 복사해 더블클릭합니다. 그림 · 글꼴이 파일 안에 있어 인터넷 · 서버 없이 모든 기능이 동작합니다 (PDF · 이미지 저장 포함).

> 회사 페이지의 `<div>` 안에 HTML 을 직접 붙여 넣는 방식은 권하지 않습니다. 이 페이지는 `body` 클래스와 주소 `#`(해시)로 화면을 바꾸기 때문에 기존 페이지와 충돌합니다. 꼭 필요하면 iframe(B)을 쓰세요.

## 보안 정책(CSP)

웹서버판은 인라인 `<script>` · `<style>` · `style=""` 속성, `data:` 주소, 외부 주소, `eval` 을 쓰지 않습니다. 아래 정책으로 시험해 **위반 0건 · 바깥 요청 0건**을 확인했습니다.

```
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self';
  img-src 'self' blob:; font-src 'self'; connect-src 'none';
  frame-ancestors 'self'; base-uri 'none'; form-action 'none'
```

- 회사 정책이 글꼴을 막아도(`font-src 'none'`) 기본 글꼴로 나오고 기능은 그대로입니다 (시험 완료).
- `img-src blob:` 은 '이미지로 저장' 때 만든 PNG 를 내려받는 데 씁니다.
- v1(2026-10-16) 정책과 다른 점은 `font-src 'self'` 하나입니다.

## 폐쇄망 반입 체크

| 확인 | 결과 |
|---|---|
| 외부 접속 | 없음. 같은 폴더 정적 파일만 읽음 (CDN · 웹폰트 서버 · 분석 · API · 광고 0) |
| 설치 · 실행 파일 | 없음. `.exe` · `.dll` · 매크로 없음 (`tools/` 의 파이썬 · 노드 스크립트는 검증용, 운영에 필요 없음) |
| 개인정보 | 저장 · 전송 없음 (쿠키 · localStorage · 서버 기록 없음) |
| 파일 무결성 | `MANIFEST.txt` 의 SHA-256 과 대조 (윈도우 : `certutil -hashfile 파일 SHA256`) |
| 사용권 | 글꼴 3종 SIL OFL 1.1, 타로 그림 1909년 원판 공개 저작물 (`LICENSES/`) |

## 동작 확인

### 손으로

- [ ] 대문에 오늘 날짜 · 일진이 보이고 문 2개(일월오봉 · 카드 3장)가 나타난다
- [ ] 사주 : 생년월일 칸을 누르면 숫자 키패드, `19900928` 입력 시 `1990-09-28` 로 바뀌며 결과가 나온다
- [ ] 사주 : 오행 상생 고리 그림 · 점수 고리 · 대운이 보인다, `20300505` 는 "출생 예정 D-n"
- [ ] 타로 : 카드 섞기 → 초승달 78장 → 4장 고르면 뒤집히며 **실제 카드 그림**이 보인다
- [ ] 타로 : 풀이 카드를 누르면 크게 보기 창, Esc · 닫기로 닫힌다
- [ ] 타로 : 「카톡으로 보내기」 → 공유창에 **카드 4장 + 점괘 이미지**가 붙는다 (휴대폰, HTTPS)
- [ ] 사주 : 「PDF로 저장」 → A4 한 장으로 인쇄된다
- [ ] 개발자 도구 콘솔에 빨간 CSP 오류가 없고, 네트워크 탭에 같은 폴더 파일 외 요청이 없다

### 도구로

```bash
python tools/csp_test_server.py 8772            # 엄격한 CSP 로 web/ 띄우기 → http://127.0.0.1:8772/
python tools/csp_test_server.py 8772 web --no-fonts   # 글꼴까지 막은 정책
python tools/verify_saju.py                     # 사주 계산 1936~2046 (40,543일) 파이썬 대조 · node 또는 playwright
node tools/check_web.js web                     # CSP 위반 · 바깥 요청 · iframe · 저장 이미지 자동 점검 (node + playwright)
```

## 수정 · 업데이트

원본은 `source/` (저장소 `fortune/`) 에 있고, 아래로 다시 만듭니다.

| 명령 | 결과 |
|---|---|
| `python3 fortune/build_unse.py --web <폴더>` | 웹서버판 `web/` |
| `python3 fortune/build_unse.py` | 한 파일판 `dist/unse_saju_tarot.html` |
| `python3 fortune/build_package.py` | 이 패키지 zip 전체 (설계도 · 소스 전체 · 해시 포함) |

두 판은 같은 원본에서 나오므로 내용이 항상 같습니다. 어느 부분을 고치면 되는지는 `BLUEPRINT.md` 11장을 보세요.

## 문의

세일즈혁신TF 이헌수 · 재미로 보는 콘텐츠이며 보험 권유 · 의사결정 근거로 쓰지 않습니다.
