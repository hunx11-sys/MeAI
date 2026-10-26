# 인수인계 : 비짓투재팬 틀로 다른 나라 가이드 만들기

> 새 세션은 이 문서를 먼저 읽고 시작한다. 저장소 규칙은 루트 `CLAUDE.md`, 앱 설명·변경 기록은 `travel/README.md`.
> 작성 2026-10-24 · 기준 판 : 비짓투재팬 v1.5 (`main` 커밋 67d15a6 이후)

## 1. 지금 있는 것 (일본판)

- **인터넷 주소** : https://hunx11-sys.github.io/MeAI/travel/ → `travel/japan.html`. `main` 에 올리면 깃허브 페이지가 몇 분 뒤 자동 게시한다.
- **영업지원도구 6종과 주소가 겹치면 안 된다.** 영업지원도구는 저장소 맨 위(`index.html`, `tool.html` 등)에 있다. 여행 앱은 모두 `travel/` 아래에만 둔다. 새 나라도 `travel/` 아래 새 파일(예 : `travel/taiwan.html`)이나 새 폴더로 만든다.
- **한 파일 앱**이다. 틀 `travel/template_japan.html`(CSS+JS 전부)에 자료를 끼워 넣어 조립한다.
  - 조립 명령 : `python3 travel/build_japan.py --lang ko --no-lang-menu`
  - 다운로드판 : 같은 명령에 `--out dist/visit_to_japan_ko_v1.5.html` 을 붙인다.
  - 2026-10-26부터 옵션 없이 돌려도 한국어만 만든다(다른 언어는 서비스하지 않음, 화면 파일도 내림).
- **화면 흐름** : 첫 화면(포털) → 며칠 → 출발 공항 → 지역 색 지도 → 지역 확대 → 도시 화면(탭 5개 : 일정·맛집·볼거리·숙소·준비) + 아래에서 올라오는 창(시트).
- **소유자 결정 사항** (바꾸지 않는다)
  - 한국어만 만든다. 다른 언어는 보류. 그래서 언어 버튼을 감췄다.
  - 숫자는 자료에서 세거나 '가정값'으로 표시한다. 금액·시간을 지어내지 않는다.
  - 환율 처음 값은 100엔=850원(가정값)이다. 자료 금액은 900원 기준이고 화면에서 다시 계산한다(`FX_BASE` · `FX_DEFAULT`).
  - 카카오톡으로 열면 한 번 자동으로 바깥 브라우저로 넘긴다(`kakaoOut`). 앱 안 브라우저는 '가벼운 모드'로 무거운 효과만 끈다.
  - 산출물 파일 이름은 영문(ASCII)으로 한다.

## 2. 자료 구조 (새 나라도 같은 모양으로)

| 파일 | 내용 | 새 나라에서 |
|---|---|---|
| `data/kr_airports.json` | 한국 출발 공항 | 그대로 쓴다 |
| `data/jp_airports.json` | 일본 공항 + 한국발 직항 노선(`routes` : `from_iata`, `status` 정기/계절/전세/운휴/확인필요, `flight_minutes`, `airlines`, `weekly`) | 그 나라 공항 파일 새로(`<cc>_airports.json`) |
| `data/guides/<도시>.json` | 도시 하나(아래 목록) | 도시마다 새로 |
| `data/art_regions.json` | 지역 장면 그림 9장(직접 그린 SVG) | 지역 수만큼 새로 |
| `data/art_dishes.json` · `art_spots.json` · `art_hotels.json` | 음식 33·볼거리 21·숙소 6종 그림 | 볼거리·숙소는 거의 재사용, 음식은 그 나라 것 추가 |
| `data/icons.json` | 도시 얼굴 그림(100×100 SVG, 4KB 이하) | 도시마다 새로 |
| `data/regions_geo.json` · `outline.json` | 지역 색 지도·해안선(Natural Earth 공개 자료, `tools/build_regions_geo.py`) | 그 나라 것으로 다시 뽑는다 |
| `data/ui_strings.json` (`ko`) | 화면 글자 | 「일본」이 들어간 문구를 나라별로 바꿀 수 있게 |

**가이드 JSON 의 맨 위 키** : key, name, name_ja, region, prefecture, airports(첫 번째 = 1일차 도착 공항), home_airports(선택), center, zoom, bbox, tagline, intro, tags, best_months, season_notes, recommended_nights, pace, airport_access, getting_around, transport_pass, spots, restaurants, hotels, plans(2·3·4박), variants(대체 동선), bplan(비 올 때 등), nearby_alternatives, checks, sources, highlights, profile, generated. 좌표를 주소로 어림했으면 `coords_approx: true` 를 둔다(그러면 구글 지도는 이름으로 찾는다).
**일정 한 줄** : `{k: spot|meal|hotel|move, t: '10:30', ref: <장소 id>, note}`. 식당 후보는 `chosenR` 가 고른다.

**점검기** : `tools/validate_guide.py`(형식·좌표·거리) · `tools/lint_guides.py`(문구). 오류가 있는 가이드는 조립에서 빠진다. 틀린 화면이 아니라 '없는 도시'로 나타나게 하기 위해서다. `validate_guide.py` 의 `KEYS` 에 새 도시 키를 넣어야 한다.
**분류기** : `tools/dish_category.py`(식당 → 음식 그림), `tools/spot_kind.py`(볼거리 → 그림).

## 3. 다른 나라로 넓히는 길 (권장 순서)

1. **틀을 나라와 무관하게 만든다.** 지금 일본에 묶인 곳은 아래와 같다. 이것들을 `data/countries/<cc>.json` 같은 나라 설정으로 빼는 게 첫 작업이다.
   - `build_japan.py` 의 `REGIONS` · `REGION_KEYS` · `TAGS` · 지도 투영 상수(`LON0`, `LAT1`, `K`, `INSET`, 오키나와 상자)
   - 파일 이름 `jp_airports.json` · `japan.html`
   - 지도 타일(`TILES` : 일본 국토지리원 → OSM)
   - 엔화(`FX_BASE` · `FX_DEFAULT` · `yenW` · '100엔=' 문구)
   - `ui_strings` 의 '일본'·'34 cities of Japan'·`doc_title`
   - `og.png` · `tools/og_card.html`
   - 지역 큰 지도의 이름표 자리(`pillLayout` 은 자동이지만 나라 모양에 맞춰 시험 필요)
2. **나라 하나로 작게 시작한다.** 도시 3~5곳, 직항이 많은 곳이 좋다(예 : 대만 타이베이·가오슝·타이중, 베트남 다낭·나트랑·하노이·호찌민, 태국 방콕·치앙마이·푸껫).
3. 자료는 일본 때처럼 만든다 : 조사 → 작성 → 사실 확인·일정 검토 → 고침. 노선·운항 요일은 항공사·공항 공식 자료로 확인하고, 확인 못 한 것은 `status: 확인필요` 로 둔다. 확인필요는 직항으로 세지 않는다.
4. 조립 → 점검(5장) → `main` 에 합치기 → 주소 안내.

## 4. 꼭 지킬 디자인·동작 규칙 (v1.5에서 정한 것)

- 포털 디자인(Supanova 규칙을 앱 안 CSS/JS 로 옮김)이다. 외부 스크립트는 더하지 않는다. Leaflet 은 `vendor/` 안에 있다.
- **휴대폰 끊김 방지** : 스크롤하며 떠오르는 효과는 첫 화면에만 쓴다. 터치 기기에서는 뒤 흐림(backdrop-filter)을 끈다. `html.lite`(앱 안 브라우저)·동작 줄이기·`.still`('움직임 멈추기' 단추)을 모두 존중한다. 움직임은 위치·투명도만 바꾼다.
- **작은 글자·터치 기준** : 탭 44px 이상, 글자 12px 이상, 가로 넘침 0. 320·390·430 폭에서 잰다.
- **지도** : 일정 지도 창은 [구글 지도 | 동선 지도] 두 가지다(처음엔 구글 지도).
  - 동선 지도 : 흐르는 점, 방향 화살표, 따라가는 화살표(Web Animations), 번호 핀 벌리기(`spreadPins`).
  - 구글 지도 : 키 없는 `maps.google.com/maps?q=..&output=embed` 를 쓴다. 장소를 바꿀 때는 iframe 을 새로 끼운다. 주소만 바꾸면 방문 기록이 쌓여 '뒤로'가 창을 닫지 못한다.
  - 구글 길찾기는 공식 `dir/?api=1` 주소를 쓴다. 휴대폰은 5곳까지라 그 단위로 나눈다.
- 공유 미리보기(`og:*` 태그, `og.png` 1200×630)와 홈 화면 아이콘(`icon-180.png`)을 나라별로 만든다. 짧은 주소 `index.html` 에도 같은 태그를 둔다.

## 5. 점검 도구 (`travel/tools/qa/v15/`)

모두 Playwright(`/opt/node22/lib/node_modules/playwright`, 크로미움 `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`)로 돈다. 일본 도시 이름·경로가 박혀 있으니, 새 나라에 맞게 고쳐 쓴다.

| 파일 | 하는 일 | 실행 |
|---|---|---|
| `sweep.js` | 모든 도시×박 수×대체 동선×일차×탭 + 시트(약 6,700장면) : 오류·가로 넘침 | `node sweep.js <html> 390` (약 30~40분) |
| `flow.js` | 첫 흐름(며칠→출발→지도→도시→탭→뒤로) | `node flow.js <html> <출력폴더>` |
| `fx.js` | 환율 시트 | `node fx.js <html> <출력폴더>` |
| `metrics.js` | 44px 탭·12px 글자·지도 겹침 | `RM=1 node metrics.js <html> 320` (동작 줄이기로 재야 떠오르는 도중 크기를 잘못 세지 않음) |
| `theme.js` · `kakao.js` | 테마 바둑판, 카카오톡 흉내 | `node kakao.js <html>` |
| `map.js` · `map2.js` | 지도 창 두 가지·움직임·빨리 닫기·작은 폰 높이 | `node map.js <html> <tile.png 있는 폴더>` |
| `scrollshot.js` | 내려가며 화면 찍기 | `node scrollshot.js <html> <경로> <출력접두> 390 4` |

이 클라우드 환경은 지도 타일·구글 지도가 막혀 있다. 그래서 `map.js` 처럼 타일을 `tile.png` 로 대신 채워 시험한다. 실제 표시는 소유자 휴대폰으로 확인받는다.

## 6. 남은 일·주의

- 아사히카와 1일차 '공항에서 20분' 문구(지금은 신치토세 도착이라 2시간)와 하코다테 가이드 말투(해라체)는 예전부터 있던 자료 문제다. 아직 안 고쳤다.
- 다른 언어 화면 파일(`japan_en/es/zh/yue/ja.html`)은 2026-10-26 내렸다(한국어만 서비스). 번역 자료 `data/i18n/` 는 남아 있다.
- **구글 지도를 바탕 전체로 쓰기** : 구글 지도 위에 우리 동선을 직접 그리려면 소유자의 구글 지도 API 키가 필요하다(Google Cloud 프로젝트 + 결제 수단 등록, 'Maps JavaScript API' 사용 설정, 키를 `https://hunx11-sys.github.io/*` 로만 쓰게 제한). 키를 받으면 동선 지도의 Leaflet 을 구글 지도 엔진으로 바꾸고 같은 동선·화살표를 구글 지도 위에 그린다. 구글 타일을 키 없이 가져다 쓰는 것은 구글 규정 위반이라 하지 않는다.
- 작업 브랜치에서 하고, 검증이 끝나면 `main` 에 합친다. 시작할 때 `git fetch origin main && git log --oneline HEAD..origin/main` 으로 다른 세션이 한 일을 먼저 본다.
