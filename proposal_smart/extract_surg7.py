# -*- coding: utf-8 -*-
"""약관 【별표3】 1-7종 수술분류표 PDF → surg7.json (수술코드·수술구분·수술명·종).
   사용 : python extract_surg7.py 별표3_1-7종수술분류표.pdf
   표(수술구분 / 수술명 / 수술코드 / 수술종류)를 셀 단위로 읽는다. 코드 형식 [A-Z]\\d{3}, 종 1~7 만 채택."""
import json, os, re, sys
def extract(pdf_path):
    import pdfplumber
    rows, gno, grp = [], None, None
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            for tb in p.extract_tables():
                for r in tb:
                    c = [(x or '').replace('\n', ' ').strip() for x in r]
                    if len(c) < 4 or c[0] == '수술구분': continue
                    if c[0]:
                        m = re.match(r'^(\d+)\.\s*(.+)$', c[0])
                        if m: gno, grp = int(m.group(1)), re.sub(r'\s+', '', m.group(2))
                        else: grp = re.sub(r'\s+', '', c[0])
                    if re.fullmatch(r'[A-Z]\d{3}', c[2]) and re.fullmatch(r'[1-7]', c[3]):
                        rows.append({'code': c[2], 'group_no': gno, 'group': grp, 'name': re.sub(r'\s+', ' ', c[1]), 'grade': int(c[3])})
    rows.sort(key=lambda r: r['code'])
    return rows
if __name__ == '__main__':
    rows = extract(sys.argv[1])
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'surg7.json')
    json.dump({'source': '약관 【별표3】 1-7종 수술분류표 (보장대상 수술코드 및 수술종류)', 'rows': rows}, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    from collections import Counter
    print('surg7.json 생성 :', dst, '| 수술코드', len(rows), '· 수술구분', len({r['group_no'] for r in rows}), '· 종별', dict(sorted(Counter(r['grade'] for r in rows).items())))
