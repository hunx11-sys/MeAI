# -*- coding: utf-8 -*-
"""특약검색기 데이터의 모든 특약에 진료행위(수가)코드 hc 를 붙인다 (v8.14).
   근거 : 특약이 참조하는 별표 원문 + 특약 본문에 적힌 5자리 수가코드(Q7701·QX706·CB003·R3504 …, 'R3504~R3508' 범위 포함).
   KCD(문자+2자리)와 1-7종 수술코드(문자+3자리)는 길이가 달라 섞이지 않는다. 실행 : python3 scripts/add_hc_codes.py"""
import io, json, os, re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from tooldata import inflate, deflate
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); TOOL = os.path.join(ROOT, 'tool.html')
HC = re.compile(r'\b([A-Z]{1,2}\d{3,4})\b(?:\s*[~∼]\s*([A-Z]{1,2}\d{3,4}))?')
def hcs(txt):
    out = []
    for a, b in HC.findall(txt or ''):
        if len(a) != 5: continue
        if b and len(b) == 5 and a[:-2] == b[:-2] and b[-2:].isdigit() and a[-2:].isdigit():
            for n in range(int(a[-2:]), int(b[-2:]) + 1): out.append(a[:-2] + '%02d' % n)
        else: out.append(a)
    return list(dict.fromkeys(out))
html = io.open(TOOL, encoding='utf-8').read()
m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', html, re.S); D = inflate(json.loads(m.group(2))); T = D['tables']
n = 0
for r in D['riders']:
    codes = []
    for tid in r.get('t') or []:
        if tid in T and '수술분류표' not in T[tid]['name'] and '산정특례' not in T[tid]['name']: codes += hcs(T[tid].get('text', ''))
    codes += hcs(r.get('b', ''))
    codes = list(dict.fromkeys(codes))
    if codes: r['hc'] = codes; n += 1
    elif 'hc' in r: del r['hc']
io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
print('수가코드 보유 특약', n, '/', len(D['riders']))
for key in ('대장용종제거', 'NGS', '체외충격파', '장루', '원추형'):
    for r in D['riders']:
        if key in r['n'] and not r.get('parent'): print('  ', r['p'], r['n'][:40], r.get('hc', [])[:8]); break
