# -*- coding: utf-8 -*-
"""
약관 전수 감사(2026.09) 결과 반영 — 검증을 통과한 지적만 tool.html 데이터에 넣는다

입력 : 감사 결과 JSON (지적 목록, 각 지적은 반박 검증에서 confirmed / corrected 된 것)
    [{"id": "통215", "target": "rider", "k_add": [...], "k_remove": [...], "x_add": [...], "x_remove": [...],
      "t_add": [...], "t_remove": [...], "table_rows_add": [{"label":..,"codes":[..]}], "table_codes_remove": [...],
      "evidence_page": 1370, "product": "통합간편", "summary_ko": "..."}, ...]

안전장치
  · 새로 넣는 질병코드(k_add · x_add · table_rows_add)는 근거로 댄 약관 쪽(앞뒤 1쪽 포함) 원문에
    그 코드 글자가 실제로 있어야 한다. 없으면 그 지적 전체를 넣지 않고 사유를 남긴다(코드를 만들지 않는다).
  · 범위 표기(C00~C14)는 원문에 범위 그대로 있거나 양 끝 코드가 있어야 한다.
  · 빼는 것(k_remove · x_remove · t_remove)은 근거 확인 없이 적용하되 목록에 남긴다.

실행 : python3 scripts/fix_audit.py <결과.json> <약관PDF텍스트폴더> [--write]
       약관PDF텍스트폴더 = 상품별 쪽 텍스트 JSON(tong/care/drv/tooth/tt/ttg.json)이 있는 곳
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import inflate, deflate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
KEY = {'통합간편': 'tong', '케어프리': 'care', '운전자': 'drv', '치아': 'tooth', '또또암': 'tt', '또또암간편': 'ttg'}
OFF = {'통합간편': 1, '케어프리': 1, '운전자': 1, '치아': 1, '또또암': 0, '또또암간편': 0}


def main():
    src, pdfdir = sys.argv[1], sys.argv[2]
    fixes = json.load(open(src, encoding='utf-8'))
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', html, re.S)
    D = inflate(json.loads(m.group(2)))
    T, R = D['tables'], D['riders']
    RM = {r['id']: r for r in R}
    CN = D.get('codenames', {})
    PDF = {}

    def page_text(p, pg):
        if p not in PDF: PDF[p] = json.load(open(os.path.join(pdfdir, KEY[p] + '.json')))
        P = PDF[p]; i = pg - 1 + OFF[p]
        return re.sub(r'\s+', '', ''.join(P[max(0, i - 1):i + 2]))

    def seen(code, txt):
        c = code.lstrip('!').replace('∼', '~')
        if '~' in c:
            a, b = c.split('~')
            return c in txt or c.replace('~', '∼') in txt or (a in txt and b in txt)
        return c in txt

    def product_of(f):
        if f.get('product'): return f['product']
        if f['target'] == 'rider': return RM[f['id']]['p']
        us = [r['p'] for r in R if f['id'] in r.get('t', [])]
        return us[0] if us else None

    applied, skipped = [], []
    for f in fixes:
        tid = f['id']
        p = product_of(f)
        if (f['target'] == 'rider' and tid not in RM) or (f['target'] == 'table' and tid not in T):
            skipped.append((tid, '대상 없음')); continue
        adds = list(f.get('k_add') or []) + list(f.get('x_add') or []) + [c for row in (f.get('table_rows_add') or []) for c in row['codes']]
        txt = page_text(p, int(f['evidence_page'])) if adds else ''
        bad = [c for c in adds if not seen(c, txt)]
        if bad:
            skipped.append((tid, '근거 쪽 원문에 없는 코드 %s' % bad)); continue
        if f['target'] == 'rider':
            r = RM[tid]; k = list(r.get('k') or []); l = list(r.get('l') or []); aligned = len(k) == len(l)
            for c in f.get('k_remove') or []:
                if c in k:
                    i = k.index(c); k.pop(i)
                    if aligned: l.pop(i)
            for c in f.get('k_add') or []:
                if c not in k:
                    k.append(c)
                    if aligned: l.append(CN.get(c, ''))
            r['k'] = k
            if aligned: r['l'] = l
            x = [c for c in (r.get('x') or []) if c not in (f.get('x_remove') or [])]
            for c in f.get('x_add') or []:
                if c not in x: x.append(c)
            r['x'] = x
            t = [c for c in (r.get('t') or []) if c not in (f.get('t_remove') or [])]
            for c in f.get('t_add') or []:
                if c in T and c not in t: t.append(c)
            r['t'] = t
        else:
            tb = T[tid]; rows = tb.setdefault('rows', [])
            rm = set(f.get('table_codes_remove') or [])
            if rm:
                for row in rows: row['codes'] = [c for c in row['codes'] if c not in rm]
                tb['rows'] = rows = [row for row in rows if row['codes']]
            have = {c for row in rows for c in row['codes']}
            for row in f.get('table_rows_add') or []:
                cs = [c for c in row['codes'] if c not in have]
                if cs: rows.append({'label': row['label'], 'codes': cs}); have |= set(cs)
        applied.append((tid, f.get('kind'), f.get('summary_ko', '')[:80]))

    for a in applied: print('반영', *a)
    for s in skipped: print('보류', *s)
    print('반영 %d건 · 보류 %d건' % (len(applied), len(skipped)))
    if '--write' in sys.argv:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 저장')


if __name__ == '__main__':
    main()
