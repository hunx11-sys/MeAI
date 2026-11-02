# 엑셀 시트를 '엑셀 화면처럼' 그린 HTML (열 문자 · 행 번호 · 아래 시트 탭) → 캡처용
import openpyxl, html, sys
src, sheet, out, ncol, nrow, hdr_row = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
widths = [int(x) for x in sys.argv[7].split(',')]
wb = openpyxl.load_workbook(src, read_only=True)
rows = []
for i, r in enumerate(wb[sheet].iter_rows(values_only=True)):
    rows.append([('' if c is None else str(c)) for c in r][:ncol]);
    if len(rows) >= nrow: break
cols = ''.join(f'<col style="width:{w}px">' for w in [44] + widths)
head = '<tr class="ch"><th></th>' + ''.join(f'<th>{chr(65+i)}</th>' for i in range(ncol)) + '</tr>'
body = ''
for i, r in enumerate(rows):
    cls = 'hd' if i + 1 == hdr_row else ('tt' if i + 1 < hdr_row else '')
    tds = ''.join(f'<td>{html.escape(c).replace(chr(10), " ")}</td>' for c in (r + [''] * ncol)[:ncol])
    if cls == 'tt': tds = f'<td colspan="{ncol}">{html.escape(r[0][:90])}…</td>'
    body += f'<tr class="{cls}"><th>{i+1}</th>{tds}</tr>'
tabs = ''.join(f'<span class="{"on" if n == sheet else ""}">{html.escape(n)}</span>' for n in wb.sheetnames)
name = src.split('/')[-1]
doc = f'''<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url("file://{sys.argv[8]}")}}
body{{margin:0;font-family:P,sans-serif;background:#fff;width:{sum(widths)+44+2}px}}
.bar{{height:40px;display:flex;align-items:center;gap:10px;padding:0 14px;background:#107C41;color:#fff;font-size:14px;font-weight:600}}
.fx{{height:30px;white-space:nowrap;overflow:hidden;border-bottom:1px solid #D1D6DB;display:flex;align-items:center;padding:0 10px;font-size:12px;color:#4E5968;gap:12px}}
.fx b{{width:60px;border-right:1px solid #E5E8EB;color:#191F28}}
table{{border-collapse:collapse;table-layout:fixed;font-size:12.5px}}
td,th{{border:1px solid #E1E4E8;padding:5px 7px;height:22px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#191F28}}
tr.ch th,tbody th{{background:#F3F4F6;color:#6B7684;font-weight:500;text-align:center}}
tr.hd td{{background:#1F4E79;color:#fff;font-weight:700}}
tr.tt td{{font-weight:700;font-size:14px;border-color:transparent}}
.tabs{{display:flex;gap:2px;border-top:1px solid #D1D6DB;background:#F3F4F6;padding:0 8px;font-size:12px}}
.tabs span{{padding:8px 12px;color:#4E5968;white-space:nowrap}} .tabs span.on{{background:#fff;color:#107C41;font-weight:700;border-bottom:2px solid #107C41}}
</style><div class="bar">▦ {html.escape(name)}</div><div class="fx"><b>A1</b><span style="overflow:hidden;text-overflow:ellipsis">{html.escape(rows[0][0][:120])}</span></div>
<table style="width:{sum(widths)+44}px">{cols}{head}{body}</table><div class="tabs">{tabs}</div>'''
open(out, 'w', encoding='utf-8').write(doc)
