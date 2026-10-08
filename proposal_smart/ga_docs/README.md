# GA 설계도 엑셀 · 칸별 특약 지도(HTML) 다시 뽑기

GA 지면 구성이나 계산이 바뀌면 이 순서대로 돌린다. 설계서 PDF(개인정보)는 저장소 밖 폴더에 둔다. 설계서 파일명은 `build_ga_xlsx.DNAME`·`build_data.DN` 에 적힌 이름(gan31-M · the510-44f · mom-40 · mom5105-40 · mom-new-40 · u355 · light355)으로 맞춘다. v8.74(GA v5 양식)부터 캡처 기준 설계서는 간편31(gan31-M).

```
cd proposal_smart/ga_docs
python run_spec.py <결과.json> <html폴더> <설계서.pdf ...>          # 설계서마다 GA 지면 HTML + 칸 스펙 결과(전 칸 일치 확인)
python build_ga_xlsx.py <결과.json> ../../dist/ga-blueprint-final.xlsx                                   # ①~⑫ 시트
python build_ga_visual.py <결과.json> <html폴더>/gan31-M-ga.html gan31-M.pdf ../../dist/ga-blueprint-final.xlsx   # 캡처 시트(표지 · 1~3쪽 · 세부내역) + <html폴더>/_visual/p1~p3.jpg
python build_ga_blueprint.py <결과.json> ../../dist/ga-blueprint-final.xlsx                              # 설계도 1~12 시트
python build_data.py <결과.json> <data.json>
python build_html.py <data.json> <html폴더>/_visual ../../dist/ga-cell-map.html "간편31 남 설계서(GA 테스트)"
cp ../../dist/ga-blueprint-final.xlsx ../../dist/ga-cell-rider-mapping.xlsx
```

- `build_ga_xlsx.py` 는 엑셀을 새로 만든다. **⑫ 검수 메모처럼 손으로 적은 시트는 이전 파일에서 다시 복사해 넣는다** — 이전 엑셀을 먼저 복사해 두고, blueprint 뒤에 `restore_memo.py`(아래)를 돌린다(2026-10-02 · 2026-10-08 에 그렇게 했다).

```python
# restore_memo.py <이전.xlsx> <새.xlsx> : 「⑫ 검수 메모」 시트의 값·서식·열 너비를 그대로 옮긴다(openpyxl)
```
- 결과 json 은 30MB 가까이 되므로 저장소에 넣지 않는다.
