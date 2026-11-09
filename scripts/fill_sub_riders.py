# -*- coding: utf-8 -*-
"""
영업지원도구(tool.html) 감수본에 빠진 세부보장 레코드를 채운다 (v8.90 · 2026-11-09)

정보계 담보코드는 세부보장마다 따로 붙는다. 케어프리 32대질병관혈수술비 · 5대질환수술비 · 전이암진단비 · 통합암진단비 등은
약관이 세부보장으로 나누는데 감수본에는 특약 하나로만 있어서, 담보코드가 다른 상품(통합간편 통55-n 등)의 세부보장으로만 이어졌다.
규칙은 proposal_smart/sub_fill.py — 같은 이름 특약이 다른 상품에서 세부보장으로 나뉘어 있고 이 특약 약관 본문에 그 세부보장 이름이
모두 있을 때만 붙인다. 질병코드는 본보기 세부 코드 중 이 특약 별표에도 있는 것만(코드를 새로 만들지 않는다).
또 세부 레코드가 따로 파는 특약과 같은 이름으로 적힌 것(케328-1 「갱신형 갑상선질환 고주파열치료비(최초1회한)」 = 케329)은
또또암(또238-n)처럼 「부모[세부]」 로 바꾼다.

실행 : python3 scripts/fill_sub_riders.py            (바뀔 것만 보기)
       python3 scripts/fill_sub_riders.py --write    (tool.html 에 반영 → 이어서 same_riders.py --write · sync_all.py)
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'proposal_smart'))
from tooldata import inflate, deflate, PAT, ROOT
import sub_fill as SF

TOOL = os.path.join(ROOT, 'tool.html')
EXTRA = os.path.join(ROOT, 'proposal_smart', 'db_terms_extra.json')


def main():
    write = '--write' in sys.argv
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    R = D['riders']
    tr = [dict(r, src='db') for r in R]
    ex = [dict(r, src='extra') for r in json.load(open(EXTRA, encoding='utf-8'))['riders']] if os.path.exists(EXTRA) else []
    plan, log = SF.plan(tr, tr + ex, lambda r: r.get('b') or '')
    by = {r['id']: r for r in R}
    n_add = 0
    for par, new in sorted(plan, key=lambda x: -R.index(by[x[0]['id']])):
        P = by[par['id']]
        recs = []
        for kid, tk in new:
            rec = {'c': kid['c'], 'id': kid['id'], 'l': [], 'n': kid['n'], 'p': P['p'], 'parent': P['id'], 'pg': P.get('pg'),
                   's': list(P.get('s') or []), 'st': P.get('st'), 't': list(P.get('t') or []), 'k': kid['k'], 'x': kid['x']}
            if kid['hc']: rec['hc'] = kid['hc']
            tl = dict(zip(tk.get('k') or [], tk.get('l') or [])) if len(tk.get('k') or []) == len(tk.get('l') or []) else {}
            rec['l'] = [tl[c] for c in kid['k'] if c in tl] if tl and all(c in tl for c in kid['k']) else list(P.get('l') or [])
            for f in ('sv', 'b'):
                if P.get(f): rec[f] = P[f]
            if tk.get('cond'): rec['cond'] = tk['cond']
            recs.append(rec)
            print('  + %-9s %s   [%s]' % (rec['id'], rec['n'], kid['basis'].split('코드는 ')[-1]))
        i = R.index(P); R[i + 1:i + 1] = recs; n_add += len(recs)
    ren = SF.rename_plan(tr, tr + ex)
    sib = set()
    for r, cand in ren: sib.add(r['parent'])
    for r in R:                                              # 같은 부모의 다른 세부도 같은 꼴로(케328-2 · 케328-3)
        if r.get('parent') in sib and '[' not in r['n']:
            par = by[r['parent']]
            new = '%s[%s]' % (par['n'], re.sub(r'^갱신형\s*', '', r['n']))
            print('  ~ %-9s %s → %s' % (r['id'], r['n'], new)); r['n'] = new
    for x in log:
        if not x[0].startswith('본문 없음'): print('  ! %s %s %s %s' % x)
    print('세부보장 채움 %d건(특약 %d개) · 이름 바꿈 %d건' % (n_add, len(plan), sum(1 for r in R if r.get('parent') in sib)))
    if write and (n_add or sib):
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 에 반영 — 이어서 python3 scripts/same_riders.py --write · python3 scripts/sync_all.py')


if __name__ == '__main__':
    main()
