# -*- coding: utf-8 -*-
"""
영업지원도구 「상품 히스토리」 → 엑셀
원천 : tool.html 의 <script id="HISTORY"> (계통별 출시 · 개정 · 판매중지 기록) — 화면과 같은 자료를 그대로 옮긴다.
실행 : python3 scripts/export_history_xlsx.py [출력.xlsx]   (기본 dist/product_history_2611.xlsx)
"""
import io, json, os, re, sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist', 'product_history_2611.xlsx')
F = 'Malgun Gothic'
HEAD = PatternFill('solid', fgColor='C73D1C')
ZEBRA = PatternFill('solid', fgColor='FDF6F3')
TAG = {'출시': 'E8F6EE', '개정': 'EBF1FC', '판매중지': 'FDECEE', '시작': 'E8F6EE', '변경': 'EBF1FC'}
THIN = Side(style='thin', color='E5E8EB')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
COLS = [('계통', 20), ('시기', 10), ('구분', 10), ('담보 · 상품', 42), ('내용', 90), ('부르는 이름(별칭)', 30), ('질문 키워드', 18)]


def load():
    s = io.open(os.path.join(ROOT, 'tool.html'), encoding='utf-8').read()
    return json.loads(re.search(r'<script id="HISTORY"[^>]*>(.*?)</script>', s, re.S).group(1))


def rows_of(g):
    ev = sorted(g['events'], key=lambda e: (str(e.get('ds') or ''), e.get('n', '')))
    return [[g['name'], e.get('d', ''), e.get('e', ''), e.get('n', ''), e.get('note', ''),
             ', '.join(e.get('syn') or []), e.get('q', '')] for e in ev]


def table(ws, rows, r0=1):
    for c, (h, w) in enumerate(COLS, 1):
        x = ws.cell(r0, c, h); x.font = Font(name=F, bold=True, color='FFFFFF', size=11); x.fill = HEAD
        x.alignment = Alignment(horizontal='center', vertical='center'); x.border = BOX
        ws.column_dimensions[get_column_letter(c)].width = w
    for i, row in enumerate(rows, r0 + 1):
        for c, v in enumerate(row, 1):
            x = ws.cell(i, c, v); x.font = Font(name=F, size=10); x.border = BOX
            x.alignment = Alignment(vertical='top', wrap_text=True, horizontal='center' if c in (2, 3) else 'left')
            if (i - r0) % 2 == 0: x.fill = ZEBRA
        k = row[2]
        if k in TAG: ws.cell(i, 3).fill = PatternFill('solid', fgColor=TAG[k]); ws.cell(i, 3).font = Font(name=F, size=10, bold=True)
    ws.freeze_panes = ws.cell(r0 + 1, 1)
    ws.auto_filter.ref = 'A%d:%s%d' % (r0, get_column_letter(len(COLS)), r0 + len(rows))
    ws.row_dimensions[r0].height = 24


def main():
    H = load()
    wb = Workbook(); ws = wb.active; ws.title = '안내'
    allrows = [r for g in H['groups'] for r in rows_of(g)]
    info = [('영업지원도구 상품 히스토리', True),
            ('기준 : 영업지원도구(특약검색기) 「📜 상품 히스토리」 자료 · 마지막 반영 %s' % H.get('updated', ''), False),
            ('계통 %d개 · 기록 %d건 — 출시 · 개정 · 판매중지를 시기 순서로 정리했어요.' % (len(H['groups']), len(allrows)), False),
            ('', False)]
    for i, (t, b) in enumerate(info, 1):
        x = ws.cell(i, 1, t); x.font = Font(name=F, size=16 if b else 11, bold=b)
    ws.cell(5, 1, '계통').font = Font(name=F, bold=True); ws.cell(5, 2, '기록 수').font = Font(name=F, bold=True); ws.cell(5, 3, '기간').font = Font(name=F, bold=True)
    for i, g in enumerate(H['groups'], 6):
        rs = rows_of(g); ds = [r[1] for r in rs if r[1]]
        ws.cell(i, 1, g['name']); ws.cell(i, 2, len(rs)); ws.cell(i, 3, '%s ~ %s' % (ds[0], ds[-1]) if ds else '')
        for c in (1, 2, 3): ws.cell(i, c).font = Font(name=F, size=11)
    n = 6 + len(H['groups']) + 1
    ws.cell(n, 1, '※ 참고용입니다. 실제 보장 내용 · 지급 조건은 해당 상품 약관을 확인하세요.').font = Font(name=F, size=10, color='6B7684')
    ws.column_dimensions['A'].width = 34; ws.column_dimensions['B'].width = 10; ws.column_dimensions['C'].width = 22
    table(wb.create_sheet('전체'), allrows)
    for g in H['groups']:
        name = re.sub(r'[\\/*?:\[\]]', '·', g['name'])[:31]
        table(wb.create_sheet(name), rows_of(g))
    wb.save(OUT)
    print('%s · 계통 %d · 기록 %d' % (os.path.relpath(OUT, ROOT), len(H['groups']), len(allrows)))


if __name__ == '__main__':
    main()
