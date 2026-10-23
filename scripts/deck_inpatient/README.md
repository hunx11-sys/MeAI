# 입원적정성 교안 PPT 생성기

`dist/inpatient_adequacy_lecture.pptx`(40장)를 만드는 스크립트. 디자인은 첨부 「55 PLAN 부산센터 교육」 HTML 의 토큰(Pretendard · 파랑 #3182F6 · 먹색 #191F28 · 둥근 카드)을 그대로 옮겼다.

- `lib.js` 스타일 도우미(머리띠 · 제목 · 카드 · 칩 · 통계 · 표 · 흐름 상자 · 한 줄 정리 · 부 구분)
- `parts/p0.js ~ p6.js` 슬라이드 내용(도입 · 1부~6부)
- `build.js` 조립. 다시 뽑는 법 :

```
cd scripts/deck_inpatient
npm install pptxgenjs@3.12.0        # 처음 한 번
node build.js                        # → ../../dist/inpatient_adequacy_lecture.pptx
```

글꼴은 Pretendard 를 쓴다. 보는 PC 에 Pretendard 가 없으면 맑은 고딕으로 대체되어 글자 폭이 조금 달라진다(`npm pack pretendard@1.3.9` 로 받을 수 있다).
수치의 출처는 각 장 아래 「출처」 줄과 마지막 장 「출처와 한계」에 있다. 별점(5부)과 상담 세 갈래(4부)는 교안의 가정값이다.
