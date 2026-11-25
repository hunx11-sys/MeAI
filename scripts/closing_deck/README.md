# 영업지원도구 인터넷판 운영 결산 PPT · 다시 만드는 법

완성본 : `dist/meai_tools_web_closing_2611.pptx`(25장 · 장마다 통이미지 + 발표자 메모) · `.pdf`

인터넷판(깃허브 주소) 종료(2026-11-25)를 맞아 만든 결산 자료. 용도 두 가지 — **내부 성과 보고**(PART 1 성과 · PART 2 애용 이유)와 **사내망 이관 IT 참고**(PART 3 구조 · 갱신 흐름 · 바꿀 바깥 연결 · 사용 기록 이어받기 · 보안 · 운영 요청).

- 숫자 출처 : **사용 숫자 = 사용 통계 서버 익명 기록 전수 분석(2026.6.22~11.25 · 73,820건)** — `stats_fetch.py`(stats.html 의 주소 · 읽기 전용 키로 usage_logs 전체를 내려받음 · 내려받은 원본은 저장소에 올리지 않음) → `stats_analyze.py`(통계 화면과 같은 기준 · 한국시간 · 종료일 11.25 까지) → 합계만 `stats_2611.json`. 누적 73,820 · 하루 최고 11.20(금) 9,362 · 10.21 까지 33,003(하루 271) · 10.22~11.25 40,817(하루 1,166) · 11월 37,051 · 평일 96% · 9시대 31%. (2026-11-25 첫 판은 공모전 때 숫자 32,812(~10.21)를 써서 소유자가 바로잡음 — 이 세션 환경에 통계 서버 주소를 허용해 다시 분석.) 자료 규모 · 갱신 횟수 · 파일 크기 = 저장소(2026.11.25). 기대효과 6.91억 = 공모전 산식 가정값.
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
