# -*- coding: utf-8 -*-
"""
영업지원도구(tool.html) 특약 이름의 잘못 끼어든 띄어쓰기를 그 상품 약관으로 바로잡는다 (2026-11-06)

특약 이름(n)과 세부보장 이름(cond)을 고친다. 규칙은 scripts/name_spacing.py — 약관이 같은 줄에서 붙여 쓴 곳(「주요치료비」)만 띄어쓰기를 빼고,
약관도 띄어 쓴 곳(「암 주요치료비」)은 그대로 둔다. 본문 · 질병코드 · 분류표는 건드리지 않는다.

실행 : python3 scripts/fix_name_spacing.py            (바뀔 이름만 보기)
       python3 scripts/fix_name_spacing.py --write    (tool.html 에 반영 → 이어서 same_riders.py --write · sync_all.py)
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'proposal_smart'))
from tooldata import inflate, deflate, PAT, ROOT
from name_spacing import flat, unbreak
import pymupdf
from extract_terms_extra import col_text

TOOL = os.path.join(ROOT, 'tool.html')
FIELDS = ('n', 'cond')   # 특약 이름 · 세부보장 이름(화면에 보이는 「cond」)
PDF = {   # 영업지원도구 상품 → 저장소 루트 약관(상품마다 최신 판 하나)
    '통합간편': '무배당 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형)약관.pdf',
    '케어프리': '무배당 메리츠 케어프리보험 M-Basket2610약관.pdf',
    '운전자': '무배당 메리츠 운전자 상해 종합보험2610약관.pdf',
    '치아': '무배당 메리츠 치아보험 이목구비2601약관.pdf',
    '또또암': '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(일반심사형)약관.pdf',
    '또또암간편': '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(맞춤간편심사형)약관.pdf',
}


def main():
    write = '--write' in sys.argv
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    TXT = {}
    for p, f in PDF.items():
        path = os.path.join(ROOT, f)
        if not os.path.exists(path): sys.exit('약관 없음 : %s' % f)
        d = pymupdf.open(path); TXT[p] = flat([col_text(d[i]) for i in range(len(d))])
    ALL = '\n'.join(TXT.values())   # 같은 특약을 다른 상품 약관이 띄어 쓰면(케어프리 「임대차보증금 법률비용」) 약관 표기로 보고 둔다 — same_riders.py 가 같은 특약을 그 표기로 맞춘다
    ch = []
    for r in D['riders']:
        t = TXT.get(r['p'])
        if t is None: continue
        for f in FIELDS:
            if not isinstance(r.get(f), str): continue
            if f == 'cond' and re.sub(r'\s', '', r[f]) not in re.sub(r'\s', '', r['n']): continue   # 사람이 쓴 설명문(「화상 치료 목적 수술」)은 두고, 이름을 옮겨 적은 것만
            new, fx = unbreak(r[f], t, ALL)
            if fx: ch.append((r['p'], r['id'] + ('' if f == 'n' else ' (%s)' % f), r[f], new, fx)); r[f] = new
    for p, i, a, b, fx in ch:
        print('%s %s : %s\n      → %s   (%s)' % (p, i, a, b, ' · '.join('「%s」→「%s」' % x for x in fx)))
    print('바로잡을 이름 %d건 · 띄어쓰기 %d곳' % (len(ch), sum(len(x[4]) for x in ch)))
    if write and ch:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 에 반영 — 이어서 python3 scripts/same_riders.py --write · python3 scripts/sync_all.py')


if __name__ == '__main__':
    main()
