# 생명보험 파헤치기 2026 교안 생성기

`docs/생명보험파헤치기2026/` 의 PPT 두 종(편집형·통이미지)을 만드는 스크립트입니다.

- `deck.js` : 메인 빌더 (`node deck.js` → `deck.pptx`)
- `lib.js` : 토스 UI 스타일 디자인 헬퍼 (색상 팔레트, 카드, 알약 라벨, 아이콘, 말풍선, 표)
- `parts/p0~p6_*.js` : 파트별 슬라이드 내용 (텍스트·통계는 여기서 수정)
- `render.sh` : LibreOffice로 PDF/PNG 렌더 (한글 자동 간격 보정 포함)

## 준비
```bash
npm install pptxgenjs sharp react react-dom react-icons
node deck.js            # deck.pptx 생성
./render.sh deck.pptx d 150   # deck.pdf + d-*.png (통이미지용)
```
통이미지 PPT는 렌더된 PNG를 슬라이드당 한 장씩 넣어 만듭니다(python-pptx).

## 통계 갱신 포인트
사망원인통계(매년 9월), 생명표(12월), 국가암등록통계(12~1월), 심뇌혈관질환 발생통계(12월),
금감원 판매채널 영업효율(4월), 한국은행 기준금리, 금감원 평균공시이율(12월). 출처는 `docs/생명보험파헤치기2026/리서치_*.md` 참고.
