# -*- coding: utf-8 -*-
"""통합치료비 지급금액 계산 엔진 (시뮬레이터 ver2609 로직 1:1 포팅).
약관 지급금액표(product_data.json)만을 근거로 계산하며, 어떤 금액도 추정하지 않는다."""
import json, os, re
BASE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(BASE, 'product_data.json'), encoding='utf-8'))
RIDERS = D['RIDERS']; RM = {r['id']: r for r in RIDERS}
IT = D['IT']; AMT = D['AMT']
KCD = dict(D['EMB']['kcd']); C32 = D['EMB']['c32']; M61 = D['EMB']['m61']; P60 = D['EMB']['p60']
DZ = {d['c']: d for d in D['DZ']}

def cancer_cls(code):
    m = re.match(r'^([CD])(\d{2})(?:\.(\d+))?', code or '')
    if not m: return None
    n = int(m.group(2)); s = m.group(3); t = m.group(1)
    if t == 'C':
        if n > 97: return None
        if n == 44: return 'skin'
        if n == 73: return 'thy'
        return 'major'
    if n <= 9: return 'cis'
    if n in (45, 46): return 'major'
    if n == 47 and s and s[0] in '1345': return 'major'      # 별표3 : D47.1·3·4·5 = 악성신생물
    if 37 <= n <= 48: return 'bord'
    return None

def _in_list(lst, code):
    part = False
    for e in lst:
        if code == e or code.startswith(e + '.') or (len(e) == 3 and code[:3] == e): return 'yes'
        if e.startswith(code + '.'): part = True
    return 'part' if part else 'no'

def cover(rider, code):
    ty = rider['ty']
    if ty in ('CB', 'CL', 'C2', 'CM'):
        if code == 'D47': return 'part'
        return 'yes' if cancer_cls(code) else 'no'
    return {'PR': lambda: _in_list(P60, code), 'CV': lambda: _in_list(C32, code),
            'MS': lambda: _in_list(M61, code)}.get(ty, lambda: 'no')()

def _ev_keys(ev):
    """비급여 면역항암약물허가치료를 받으면 비급여 표적항암약물허가치료도 함께 인정."""
    k = ev[3]
    if 'immune' in k and 'target' not in k:
        i = k.index('immune'); return k[:i] + ['target'] + k[i:]
    return k

def calc_rider(rider_id, tier, code, path, within_1y=False):
    """path = {'e': [ [단계, 치료명, 설명, [치료키], {옵션}], ... ]}
       옵션 : nc(비급여) · j(1-5종) · n(재활 일수)"""
    r = RM[rider_id]; items = IT[r['ty']]; A = AMT[r['ty']][str(tier)]
    res = {'id': rider_id, 'tier': tier, 'cov': cover(r, code), 'lines': [],
           'raw': 0, 'total': 0, 'cap': 0, 'capped': False}
    if res['cov'] == 'no': return res
    dc = cancer_cls(code)
    sp = bool(re.match(r'^C(73|61)', code))                       # 특정암(로봇수술 금액 구분)
    inj = (r['ty'] == 'MS' and bool(re.match(r'^S(06|25|26)', code)))   # 주요손상
    f = 0.5 if (r['half'] and within_1y and not inj) else 1        # 1년 이내 감액
    used = {}; rehab = 0
    for ei, ev in enumerate(path['e']):
        o = ev[4] if len(ev) > 4 else {}
        for k in _ev_keys(ev):
            cands = [(i, it) for i, it in enumerate(items) if it['k'] == k]
            if not cands:
                res['lines'].append({'ei': ei, 'k': k, 'amt': 0, 'why': 'none'}); continue
            el = [(i, it) for i, it in cands
                  if (not it.get('cl') or dc in it['cl'])
                  and ('sp' not in it or bool(it['sp']) == sp)
                  and (not it.get('j') or it['j'] == o.get('j'))]
            if not el:
                res['lines'].append({'ei': ei, 'k': k, 'i': cands[0][0], 'amt': 0, 'why': 'cls'}); continue
            i, it = el[0]
            if it.get('nc') and not o.get('nc'):
                res['lines'].append({'ei': ei, 'k': k, 'i': i, 'amt': 0, 'why': 'nc'}); continue
            base = A[i] * f
            if it['p'] == 'y':                                     # 연간 1회
                if used.get(i): res['lines'].append({'ei': ei, 'k': k, 'i': i, 'amt': 0, 'why': 'once'})
                else: used[i] = 1; res['lines'].append({'ei': ei, 'k': k, 'i': i, 'amt': base})
            elif it['p'] == 'o':                                   # 수술 1회당
                res['lines'].append({'ei': ei, 'k': k, 'i': i, 'amt': base})
            else:                                                  # 재활 : 1일 1회 · 연간 한도
                req = o.get('n', 1); n = max(0, min(req, it['max'] - rehab)); rehab += n
                res['lines'].append({'ei': ei, 'k': k, 'i': i, 'amt': base * n, 'n': n,
                                     'req': req, 'max': it['max'], 'why': 'max' if n < req else ''})
    res['raw'] = sum(l['amt'] for l in res['lines'])
    res['cap'] = tier * (0.5 if (r['half'] and within_1y) else 1)   # 연간 총 지급 한도
    res['total'] = min(res['raw'], res['cap'])
    res['capped'] = res['raw'] > res['cap']
    return res

def groups_for(code): return {r['g'] for r in RIDERS if cover(r, code) != 'no'}
def shown_ids(combo, code):
    g = groups_for(code)
    return [rid for rid in (r['id'] for r in RIDERS) if rid in combo and RM[rid]['g'] in g]
def calc_all(combo, code, path, within_1y=False):
    return {rid: calc_rider(rid, combo[rid], code, path, within_1y) for rid in shown_ids(combo, code)}
def item_label(rider_id, idx): return IT[RM[rider_id]['ty']][idx]['l']
def disease(code): return DZ.get(code)
def disease_name(code):
    d = DZ.get(code)
    return d['n'] if d else (KCD.get(code) or KCD.get(code[:3]) or code)
