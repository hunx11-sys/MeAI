# -*- coding: utf-8 -*-
"""정보계 담보코드 표(엑셀 · 단위상품코드 / 담보코드 / 상품담보명) → rows.json

엑셀 글자가 _x0036_ · _x0020_ 같은 꼴로 들어 있어 원래 글자로 되돌린다.
사용 : python3 extract_rows.py <정보계 엑셀> <작업폴더>
"""
import sys, os, re, json
import openpyxl
X = re.compile(r'_x([0-9A-Fa-f]{4})_')
def dec(v): return X.sub(lambda m: chr(int(m.group(1), 16)), str(v)).strip() if v is not None else ''
src, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
ws = openpyxl.load_workbook(src, read_only=True).worksheets[0]
rows = []
for i, r in enumerate(ws.iter_rows(values_only=True)):
    if i == 0: continue
    u, c, n = (dec(x) for x in r[:3])
    if c and n: rows.append([u, c, n])
json.dump(rows, open(os.path.join(work, 'rows.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(rows), 'rows', len({c for _, c, _ in rows}), 'codes', len({u for u, _, _ in rows}), 'units')
