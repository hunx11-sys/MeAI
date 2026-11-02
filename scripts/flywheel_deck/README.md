# MeAI 영업 플라이휠 PPT · 다시 만드는 법

완성본 : `dist/meai_flywheel_deck.pptx`(35장 · 장마다 통이미지 + 발표자 메모) · `dist/meai_flywheel_deck.pdf`

고객발굴 → 터치 → 클로징 → 계약체결 → 관리·소개 → 새 고객발굴 플라이휠을 보조도구 13종의 실제 화면으로 설명하는 장표다.
영업 6단계 앞과 뒤쪽 정리(07 바퀴를 굴리는 힘) 앞에 간지 7장이 들어간다(`sect()` : 번호 · 이름 · 목표 한 줄 · 그 구간 도구와 쪽수 · 지금 단계를 칠한 바퀴 · 걱정인형). 간지 아래에는 발표 진척도 막대(`prog()` : 도입 · 영업 6단계 · 정리 8구간, 구간 길이는 장 수에 비례, 지나온 구간 연한 빨강 · 지금 구간 진한 빨강과 「지금 여기」 · 오른쪽 진행률 %)가 붙는다. 쪽수와 막대는 굽는 마지막에 자동으로 채운다.
MeAI 홈 사용 매뉴얼 · MeAI 활용 가이드북 v4, MeAI 통계(사용 통계 화면 · 넛지 대시보드 · 헤비유저 숫자), 의학용어 그림과 해설 PPT 는 넣지 않았다(소유자 2026-11-02).

- 디자인 : `design/DESIGN-토스.md`(흰 바탕 · 차가운 회색 · 한 화면 한 강조색 · 둥근 카드 · 1px 선 · Pretendard) + `design/DESIGN-MeAI.md`(메리츠 빨강 `#C8102E` · 굵기 400/600/700 · 걱정인형 2D)
- 말투 : 장표 글은 음 · 임으로 끝내는 개조식(소유자 요청, 토스 해요체 대신). 긴 줄표 없음
- 숫자 : 모두 도구 화면 · 저장소 자료에서 확인한 값
- 사람 이름 : 운세 「김하늘」 · 명패 명단 · 넛지 고객은 가상. 스마트 제안서는 `proposal_smart/cust_a.json`(설계사 정보 가린 예시), GA 는 `ga_preview.py` 가정값(번호는 0 으로 가림)

## 순서 (작업 폴더 W 하나에 캡처를 모은다)

```
W=<작업폴더>; mkdir -p $W/cap/nz $W/cap/unse $W/cap/gb $W/sp $W/ref $W/out
# 0. 도구 : pptxgenjs · Pretendard
(cd $W && mkdir node && cd node && npm init -y && npm install pptxgenjs@3.12.0 && npm pack pretendard@1.3.9 && tar xzf pretendard-1.3.9.tgz)
# 1. 영업지원도구 화면 (1440x900 @2x)
node capture/cap_ts.js $W/cap ; node capture/cap_tool2.js $W/cap ; node capture/cap_tool3.js $W/cap ; node capture/cap_ts.js $W/cap
node capture/cap_sim3.js $W/cap ; node capture/cap_zz2.js $W/cap ; node capture/cap_pr.js $W/cap ; node capture/cap_pr3.js $W/cap
node capture/cap_pm2.js $W/cap ; node capture/cap_idx.js $W/cap
node capture/cap_np.js $W/cap <가상 명단.xlsx>        # 첫 줄 : 이름 · 소속 · 기타
# 2. MeAI 홈 넛지 · 운세 · 세일즈북
node capture/shoot_nz.js $W/cap/nz
node ../../fortune/guide/capture.js $PWD/../../dist/unse_saju_tarot.html $W/cap/unse
node capture/cap_gb2.js $W/cap/gb
# 3. 스마트 제안서 · GA 미리보기 (페이지마다)
(cd ../../proposal_smart && python3 gen2.py cust_a.json $W/sp/cust_a.html)   # <head> 에 <base href="…/proposal_smart/"> 를 넣고 깨진 로고는 숨김
node capture/cap_sp.js $W/sp/cust_a.html $W/sp sp_p
(cd ../../proposal_smart && python3 ga_preview.py $W/sp/ga_preview.pdf)        # 파이썬 playwright 가 없으면 HTML 만 남는다 → 그 HTML 을 찍음
VW=794 node capture/cap_sp.js $W/sp/ga_preview.html $W/sp ga_p
# 4. 참고자료 : 예외질환 PDF · 엑셀 두 개(수술비 정리표는 시트 두 장)
pdftoppm -r 110 -png -f 1 -l 4 ../../dist/simple_ins_exception_guide_2610.pdf $W/ref/exg
pdftoppm -r 110 -png -f 1 -l 4 ../../docs/simple_exception_disease_manual_2610.pdf $W/ref/exm
python3 xl_view.py ../../dist/surgery_benefit_kcd_2610.xlsx '1-7종 대표질병' $W/ref/xl_surg.html 7 16 2 70,130,80,50,280,70,200 <Pretendard-Regular.woff2>
python3 xl_view.py ../../dist/surgery_benefit_kcd_2610.xlsx '1-5종II' $W/ref/xl_s15.html 5 16 2 90,50,330,60,360 <Pretendard-Regular.woff2>
python3 xl_view.py ../../dist/simple_exception_disease_2610.xlsx '경우의 수(신기준)' $W/ref/xl_ex.html 6 16 1 50,120,170,230,50,230 <Pretendard-Regular.woff2>
node shot_el.js $W/ref/xl_surg.html $W/ref/xl_surg.png body ; node shot_el.js $W/ref/xl_s15.html $W/ref/xl_s15.png body ; node shot_el.js $W/ref/xl_ex.html $W/ref/xl_ex.png body
# 5. 크기 표 → 굽기 → PDF
python3 make_sizes.py $W
node build_deck.js $W $W/node/package/dist/web/variable/woff2/PretendardVariable.woff2 $W/out meai_flywheel
python3 make_pdf.py $W/out/meai_flywheel_files.json $W/out/meai_flywheel.pdf
```

- `build_deck.js` 는 굽고 나서 「글꼴 · 깨진 그림 · 넘침 · 글 상자 겹침」을 출력한다. 모두 0 이어야 한다.
- 캡처 위 빨간 번호의 자리는 캡처 css 좌표로 적혀 있다. 도구 화면 배치가 바뀌면 `montage.py` 로 장표를 모아 보고 자리를 고친다.
