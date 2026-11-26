# 영업지원도구 사용 통계 및 데이터 결산 PPT · 다시 만드는 법

완성본 두 벌(소유자 2026-11-25 · 장마다 통이미지 + 발표자 메모 · `.pptx` · `.pdf`)
- 부서 공유용 `dist/meai_tools_web_closing_2611_dept.*` (31장) : PART 1 성과 · 2 컨닝페이퍼가 필요했던 이유(사례 6) · 3 애용 이유 · 4 MeAI · 스마트 제안서로 이어짐 · 맺음 인사
- 영업채널 전달용 `dist/meai_tools_web_closing_2611_field.*` (25장) : 통계 · 성과만 — 「이 자료는」 장과 PART 4(MeAI · 스마트 제안서 · 개발 로드맵)를 뺌
- 만들기 : `build.py <캡처> <글꼴> <출력폴더> dept|field` (넷째 인자 없으면 dept) · 사내망 이관 참고 챕터는 소유자 지시로 뺌

인터넷 링크 폐쇄(2026-11-25)를 맞아 만든 결산 자료. 부서 공유용은 성과 · 컨닝페이퍼가 필요했던 이유 · 애용 이유 · MeAI · 스마트 제안서로 이어짐, 영업채널 전달용은 통계 · 성과만.

- 숫자 출처 : **사용 숫자 = 사용 통계 서버 익명 기록 전수 분석(2026.6.22~11.25 · 73,820건)** — `stats_fetch.py`(stats.html 의 주소 · 읽기 전용 키로 usage_logs 전체를 내려받음 · 내려받은 원본은 저장소에 올리지 않음) → `stats_analyze.py`(통계 화면과 같은 기준 · 한국시간 · 종료일 11.25 까지) → 합계만 `stats_2611.json`. 누적 73,820 · 하루 최고 11.20(금) 9,362 · 10.21 까지 33,003(하루 271) · 10.22~11.25 40,817(하루 1,166) · 11월 37,051 · 평일 96% · 9시대 31%. (2026-11-25 첫 판은 옛 집계 숫자 32,812(~10.21)를 써서 소유자가 바로잡음 — 이 세션 환경에 통계 서버 주소를 허용해 다시 분석.) 자료 규모 · 갱신 횟수 · 파일 크기 = 저장소(2026.11.25). 기대효과는 금액 없이 문구만(소유자 2026-11-25 · 6.91억 등 금액은 장표에서 뺌).
- 그래프는 `charts.py`(SVG · 바깥 라이브러리 없음). 특약 이름 글자 수 · 통합치료비 이름 수 · 특정순환계질환 통합치료비 vs (주요손상및질환) 보장 코드 · 공식 병명(금액 · 가입금액은 proposal_smart/product_data.json 지급금액표)은 빌드 때 `tool.html` 데이터에서 직접 세고(추정 없음), 약관 쪽수는 저장소 루트 약관 PDF 를 실측(케어프리 M-Basket 2610 = 1,830쪽 · 53종 합계 37,227쪽). 용어 설명은 `gloss.js` 문구 그대로.
- 소유자 2026-11-25 : 장표에 「공모전」 말을 쓰지 않는다 · 애용 이유에서 「설치 · 로그인 없이 주소 하나(인터넷)」를 뺀다(인터넷판 폐쇄 지적사항).
- 디자인 : `design/DESIGN-MeAI.md` + `DESIGN-토스.md` · 메리츠 빨강 하나 · Pretendard · 장표 글 음 · 임 개조식 · 걱정인형 2D(`ui/mascots`).

## 순서

```
W=<작업폴더>; mkdir -p $W/cap $W/font
(cd $W/font && npm pack pretendard@1.3.9 && tar xzf pretendard-1.3.9.tgz)
# 1. 화면 캡처(1440x900 @2x · 사내처럼 파일로 열어 찍는다 — github.io 로 열면 종료 화면으로 넘어간다)
#    index · tool(「뇌경색」 입력) · sim_c16(보상시뮬레이터 위암) · itc(통합치료비.html#I21) · products · prompts · nameplate
# 1-2. 사용 숫자 다시 뽑기(통계 서버 주소가 허용된 환경에서)
python3 scripts/closing_deck/stats_fetch.py $W/rows.json && python3 scripts/closing_deck/stats_analyze.py $W/rows.json
# 2. 굽기 → PPT · PDF
python3 scripts/closing_deck/build.py $W/cap $W/font/package/dist/web/variable/woff2/PretendardVariable.woff2 dist
```

`build.py` 는 굽고 나서 「넘침」을 출력한다 — 0 이어야 한다. 내용이 적은 장은 `slide(..., z=1.3)` 처럼 배율로 글자를 키워 장을 채운다(폭은 그대로).
