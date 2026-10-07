# GA 설계도 엑셀 · 칸별 특약 지도(HTML) 다시 뽑기

GA 1쪽 구성이나 계산이 바뀌면 이 순서대로 돌린다. 설계서 PDF(개인정보)는 저장소 밖 폴더에 둔다.

```
cd proposal_smart/ga_docs
python run_spec.py <결과.json> <html폴더> <설계서.pdf ...>          # 설계서마다 GA 지면 HTML + 칸 스펙 결과(전 칸 일치 확인)
python build_ga_xlsx.py <결과.json> ../../dist/ga-blueprint-final.xlsx                                   # ①~⑫ 시트
python build_ga_visual.py <결과.json> <html폴더>/the510-44f-ga.html the510-44f.pdf ../../dist/ga-blueprint-final.xlsx   # 캡처 시트(1쪽 · 합산 계산서 · 2~6쪽) + <html폴더>/_visual/p1~p6.jpg
python build_ga_blueprint.py <결과.json> ../../dist/ga-blueprint-final.xlsx                              # 설계도 1~12 시트
python build_data.py <결과.json> <data.json>
python build_html.py <data.json> <html폴더>/_visual ../../dist/ga-cell-map.html
cp ../../dist/ga-blueprint-final.xlsx ../../dist/ga-cell-rider-mapping.xlsx
```

- `build_ga_xlsx.py` 는 엑셀을 새로 만든다. **⑫ 검수 메모처럼 손으로 적은 시트는 이전 파일에서 다시 복사해 넣는다**(2026-10-02 에 그렇게 했다).
- 결과 json 은 30MB 가까이 되므로 저장소에 넣지 않는다.
