# 여행 플래너 모바일 개편(v2) 인수인계 — 2026-10-15 00시(UTC) 중단

## 현재 상태(2026-10-15 저녁 갱신)
- v2 틀은 조립·점검 끝(아래 '다음에 할 것' 1·2·5번 대부분 완료). 한국어판만 갱신한다(소유자 지시 : 다른 언어는 당분간 손대지 않음).
- 끝난 것 : 단계형 화면 · 환율 바꾸기 · 시각 검수 1차 반영(지도 알약 바다 쪽 자동 배치, 지역 확대·오키나와 두 칸, 음식 그림 27종, 하위 탭 한 줄 머리 등 — README 변경 기록 'v1.4 다듬기').
- 점검 스크립트(세션 작업폴더용) : 전 장면 훑기 · 흐름(뒤로 가기) · 환율 · 지표(44px·12px·지도 겹침). 같은 내용을 다시 만들 때는 `tools/qa/` 의 옛 스크립트를 새 주소에 맞춰 쓴다.
- 남은 것 : 실물 사진(이 세션도 upload.wikimedia.org 가 403), 다른 언어판 v2 다시 조립(소유자가 원할 때), main 병합(소유자가 말할 때).

소유자 요청(2026-10-14): 글씨가 많고 복잡하다 → 박 수부터 고르는 단계형, 크고 지역별 색이 다른 지도, 지역·음식 실물 사진 또는 연상되는 예쁜 그림. 캔바·피그마 등 커넥터 활용.

## 끝난 것
- 설계안 3개(단계형 · 지도 중심 · 피드형) : `proposal_*.md`. **단계형(proposal_wizard.md)을 기본으로 채택**하고 바꾼 점:
  - 주소는 `?` 대신 빗금 : `#home` `#from` `#map` `#map/<kansai…>` `#all` `#search` `#<도시>[/n3][/v1][/d2][/food|spot|hotel|prep]` (예전 `#kyoto` 도 열림)
  - '모든 도시 한눈에 보기'(`#all`, 테마 칩) 추가 — 33곳 비교용
  - 오키나와 상자를 동해 북쪽 빈 바다(x 64, y 8)로 옮기고 큰 지도는 한국을 빼고 x 50~331 만 보여 줌
- 지역 색 지도 자료 `data/regions_geo.json`(Natural Earth 현 경계 합침, `tools/build_regions_geo.py`)
- 지역 장면 그림 9장 `data/art_regions.json`, 음식 그림 23종 `data/art_dishes.json`(직접 그림), 식당 → 음식 그림 분류 `tools/dish_category.py`
- 실물 사진 자리 : `data/photos.json` 이 있으면 조립 때 파일 안에 넣고 촬영자 표기(없으면 그림). 후보 수집기 `tools/fetch_photos.py`(위키미디어 공용, 퍼블릭 도메인·CC0·CC BY·CC BY-SA 만)
- 틀(`template_japan.html`)을 v2 로 **다시 씀(아직 조립·점검 안 함)** : 화면 S1 며칠 → S2 출발(처음 한 번) → S3 큰 색 지도 + 지역 카드 3×3 → S4 지역 확대 + 도시 카드 → S5 도시(대표 그림 + 요약 알약 + 아래 탭 5개 : 일정·맛집·볼거리·숙소·준비) + 검색 화면 + 바텀 시트(박 수·출발 공항·식당 고르기·큰 지도·이 일정은·플랜 B·소개·항공편·장소/식당/숙소 자세히·직항 없음). 화면 글자 키 약 95개를 6개 언어로 `data/ui_strings.json` 에 넣음
- 이전(v1.3) 틀 : 이 문서를 넣은 커밋의 바로 앞 커밋에 있다(`git log -- travel/docs/ux_v2/HANDOFF.md` 로 커밋을 찾고 `git show <그 커밋>~1:travel/template_japan.html`)
- 조립된 `travel/japan*.html` 과 `dist/japan_travel_planner_ko_v1.3.html` 은 **아직 v1.3**(새 틀로 다시 조립하지 않음)

## 다음에 할 것(순서대로)
1. `python3 travel/build_japan.py --lang ko --out <작업폴더>/t/japan.html` 로 조립 → 헤드리스 크로미움(아이폰 13)으로 열어 자바스크립트 오류부터 잡는다. 새 틀은 아직 한 번도 실행하지 않았다.
2. 화면별 캡처 점검(390·320 폭) : `tools/qa/` 의 스크립트는 v1.3 화면용이라 새 주소(#home·#from·#map·#map/<지역>·#<도시>/<탭>)에 맞게 고쳐 쓴다. 목표 수치는 proposal_wizard.md 12장 끝 표(첫 화면 글자 100자 안, 교토 첫 일정 600px 안, 44px 미만 탭 0, 12px 미만 글자 0, 가로 넘침 0, 뒤로 가기 순서).
3. 실물 사진 : 새 세션에서 `curl -sI https://upload.wikimedia.org/` 가 되면 `python3 travel/tools/fetch_photos.py` → `data/photos_candidates.json` → 사진을 직접 보고(그 장소가 맞는지·예쁜지) 골라 `data/photos.json` 으로 옮김 → 다시 조립. 아직 403 이면 소유자에게 환경 네트워크 허용(commons.wikimedia.org, upload.wikimedia.org)을 다시 확인 요청.
4. 피그마 : 스타터 요금제라 월 MCP 호출 한도(6회)를 이미 다 씀. 캔바 그림 생성은 200px 미리보기만 받아져 앱에 못 넣음(전체 크기는 canva.com 이 막혀 있음).
5. 다각도 검수(첫 사용자·시각·접근성·문구·기능 버그·번역판) → 고치기 → `qa3`(전 화면)·뒤로 가기 점검 → 6개 언어 조립 → 다운로드 파일 v1.4(`dist/japan_travel_planner_ko_v1.4.html`, `--no-lang-menu`), 아티팩트 갱신, README 변경 기록 v1.4.
6. main 병합은 소유자가 말할 때만.
