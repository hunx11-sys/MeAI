# -*- coding: utf-8 -*-
"""회사 담보코드 이름 → 우리 특약 마스터(db.json + db_terms_extra.json) 레코드 매칭"""
import json, re, sys, os, collections, difflib
from norm import strip_tags, key
R = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'proposal_smart') + os.sep
db = json.load(open(R + 'db.json', encoding='utf-8'))['riders']
ex = json.load(open(R + 'db_terms_extra.json', encoding='utf-8'))['riders']
M = [dict(r, src='db') for r in db] + [dict(r, src='extra') for r in ex]
for r in M:
    if r['src'] == 'db' and '-' in r['id']: r['parent'] = r['id'].split('-')[0]     # db.json 은 parent 를 안 싣는다 — 번호로 되살림
SPLIT = re.compile(r'[\[\]\(\),·/]+')
SUF = re.compile(r'(주요치료비|약물허가치료비|진단비|치료비|수술비|입원일당|검사비|치료|진단|수술)$')
TAIL = re.compile(r'(보장특별약관|특별약관|보장)$')
def toks(s): return [TAIL.sub('', t) or t for t in SPLIT.split(strip_tags(s)) if t]
DESC = re.compile(r'(보장)?특별약관\(.*\)$')   # 약관 제목처럼 「…보장특별약관(아토피피부염‧중이염‧축농증)」 으로 들어온 이름은 괄호 설명을 뗀다
for r in M:
    n0 = DESC.sub('', r['n']) or r['n']
    r['_k'] = key(n0); r['_t'] = toks(n0); r['_stem'] = r['_t'][0] if r['_t'] else ''
kids = collections.defaultdict(list)
for r in M:
    if r.get('parent'): kids[(r['p'], r['parent'])].append(r)
by_stem = collections.defaultdict(list); by_key = collections.defaultdict(list)
for r in M: by_stem[r['_stem']].append(r); by_key[r['_k']].append(r)

import os
FZ = int(os.environ.get('FZ', '1'))
HARD = re.compile(r'[0-9A-Za-zⅠ-Ⅹ\-~%]')
def inside(t, u):
    """t 가 낱말 u 안에 들어 있는가 — 숫자 앞뒤로 숫자가 붙으면 다른 것(9대 ⊄ 19대)"""
    i = u.find(t)
    while i >= 0:
        a = u[i - 1] if i > 0 else ''; b = u[i + len(t)] if i + len(t) < len(u) else ''
        if not ((t[0].isdigit() and a.isdigit()) or (t[-1].isdigit() and b.isdigit())): return True
        i = u.find(t, i + 1)
    return False
def covered(t, ts):
    """회사(또는 우리) 낱말 t 가 상대 낱말 묶음 ts 에 들어 있는가 — 낱말 단위로만 본다(이름 전체를 이어 붙여 보면 「비급여」가 「치료비급여」에 걸린다)"""
    t2 = SUF.sub('', t)
    for u in ts:
        if t == u or inside(t, u) or (len(t2) >= 2 and inside(t2, u)): return True
    for u in ts:
        if abs(len(u) - len(t)) <= FZ and HARD.findall(u) == HARD.findall(t) and difflib.SequenceMatcher(None, t, u).ratio() >= 0.85: return True
    return False
def csuf(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]: n += 1
    return n
def short(u, stem):
    n = csuf(u, stem)
    return u[:-n] if n >= 3 and len(u) - n >= 2 else u
REC = {(r['p'], r['id']): r for r in M}
def core(u, P):
    """우리 세부보장 낱말에서 부모 낱말과 겹치는 앞 · 뒤를 떼어 낸 알맹이(국립암센터특정소액암주요치료비 → 특정소액)"""
    best = u
    for p in P:
        a = 0
        while a < min(len(u), len(p)) and u[a] == p[a]: a += 1
        b = csuf(u, p)
        if a + b < len(u) and (a >= 2 or b >= 2):
            c = u[a:len(u) - b] if b else u[a:]
            if len(c) >= 2 and len(c) < len(best): best = c
    return best
def score(ct, ck, o):
    dc = ct[1:]; do = o['_t'][1:]; ds = [short(u, o['_stem']) for u in do]
    cc = sum(covered(t, do + ds) for t in dc) / len(dc) if dc else 1.0
    co = sum(covered(u, dc) or covered(v, dc) for u, v in zip(do, ds)) / len(do) if do else 1.0
    return cc, co
def dscore(ct, o):
    """세부보장 후보끼리 고를 때 : 부모 이름에 없는 낱말끼리 얼마나 맞나(중복암 ≠ 재등록암). 부모가 없으면 2"""
    par = REC.get((o['p'], o.get('parent'))) if o.get('parent') else None
    if not par: return sum(score(ct, None, o))
    P = set(par['_t']); dc = ct[1:]; do = o['_t'][1:]
    dcd = [t for t in dc if t not in P]; dod = [(u, short(u, o['_stem']), core(u, P)) for u in do if u not in P]
    if not dcd or not dod: return sum(score(ct, None, o))
    uu = [x for trip in dod for x in trip]
    return sum(covered(t, uu) for t in dcd) / len(dcd) + sum(any(covered(x, dcd) for x in trip) for trip in dod) / len(dod)
QUAL = re.compile(r'체증|배지급|감액|면책|전환|발생후|plus|비급여|추가$|부담보|부보장|형$|Ⅱ|Ⅲ|Ⅳ')
def groups(s):
    out = []; d = 0; st = None
    for i, ch in enumerate(s):
        if ch in '([':
            if d == 0: st = i
            d += 1
        elif ch in ')]':
            d -= 1
            if d == 0 and st is not None: out.append(s[st + 1:i]); st = None
    return out

RANK = {'정확': 0, '세부표기': 1, '특약단위': 2, '유사': 3, '없음': 9}
def gtoks(g): return [TAIL.sub('', x) or x for x in SPLIT.split(g) if x]
def judge(name, ct, o):
    cc, co = score(ct, None, o)
    do = o['_t'][1:] + [short(u, o['_stem']) for u in o['_t'][1:]]
    if cc >= 0.99 and not o.get('parent') and len(ct) - 1 > len(o['_t']) - 1:
        extra = [t for t in ct[1:] if not any(t == u or inside(t, u) for u in do)]
        if extra and not any(QUAL.search(t) for t in extra):
            if not kids.get((o['p'], o['id'])):
                return '특약단위', '회사는 세부보장(%s) 단위 코드, 우리 마스터는 특약 단위 — 특약에 붙임' % ','.join(extra), cc, co
            return '특약단위', '우리 세부보장 이름과 안 맞아(%s) 특약에 붙임 — 세부보장 확인 필요' % ','.join(extra), cc, co
    if cc == 1.0 and co == 1.0: return '세부표기', '낱말은 같고 괄호 모양 · 순서 · 띄어쓰기만 다름', cc, co
    if cc >= 0.99 and co >= 0.5:
        ours = [u for u in o['_t'][1:] if not (covered(u, ct[1:]) or covered(short(u, o['_stem']), ct[1:]))]
        q = [u for u in ours if QUAL.search(u)]
        if q: return '유사', '우리 이름에만 있는 낱말(%s) — 다른 판일 수 있음 · 확인 필요' % ','.join(q), cc, co
        return '세부표기', '회사 이름의 낱말이 모두 우리 이름에 있음(우리 쪽이 길게 씀 · 대개 세부보장 이름에 부모 이름을 다시 붙인 모양)', cc, co
    if co == 1.0:
        miss = [t for t in ct[1:] if not covered(t, do)]
        if miss and any(QUAL.search(t) for t in miss):
            return '유사', '우리 특약에 없는 낱말(%s) — 별개 특약(변형)일 수 있음' % ','.join(miss), cc, co
        if not o.get('parent') and miss:
            gs = [g for g in groups(strip_tags(name)) if all(t in gtoks(g) for t in miss)]
            if gs:
                if not kids.get((o['p'], o['id'])):
                    return '특약단위', '회사는 세부보장(%s) 단위 코드, 우리 마스터는 특약 단위 — 특약에 붙임' % ','.join(miss), cc, co
                return '특약단위', '우리 세부보장 이름과 안 맞아(%s) 특약에 붙임 — 세부보장 확인 필요' % ','.join(miss), cc, co
        return '유사', '우리 특약에 없는 낱말(%s) — 확인 필요' % ','.join(miss), cc, co
    if cc == 1.0 and len(ct) == 1 and not any(QUAL.search(u) for u in o['_t'][1:]):
        return '유사', '우리 이름에만 괄호 설명(%s)이 더 있음 — 같은 특약인지 확인' % ','.join(o['_t'][1:]), cc, co
    if cc >= 0.75 and co >= 0.75: return '유사', '낱말 %.0f%% · %.0f%% 겹침 — 확인 필요' % (cc * 100, co * 100), cc, co
    return '없음', '가장 가까운 후보 「%s」(낱말 %.0f%% · %.0f%%)' % (o['n'], cc * 100, co * 100), cc, co

def match_one(name):
    k = key(name)
    if k in by_key: return '정확', by_key[k][0], ''
    ct = toks(name)
    if not ct: return '없음', None, ''
    best = None
    for o in by_stem.get(ct[0], []):
        lv, note, cc, co = judge(name, ct, o)
        s = (-RANK[lv], round(dscore(ct, o), 4), round(cc + co, 4), 1 if o.get('parent') else 0, -len(o['_k']))
        if best is None or s > best[0]: best = (s, o, lv, note)
    if not best: return '없음', None, '이름 첫 낱말(%s)이 같은 우리 특약 없음' % ct[0]
    return best[2], best[1], best[3]

VARIANTS = [('(출생전)', '출생전 가입 변형'), ('(최초발생후전환용)', '최초발생후 전환용 변형'), ('(전환용)', '전환용 변형'),
            ('(최초암발생후)', '최초암발생후 변형'), ('(최초2대질환발생후)', '최초2대질환발생후 변형')]
def match(name):
    lv, o, note = match_one(name)
    if lv == '정확': return lv, o, note, ''
    s = strip_tags(name); var = []
    for v, lab in VARIANTS:
        if v in s: s = s.replace(v, ''); var.append(lab)
    if s.endswith('추가') and len(s) > 4: s = s[:-2]; var.append('「추가」 표기')
    if var:
        lv2, o2, note2 = match_one(s)
        if RANK[lv2] < RANK[lv]: return lv2, o2, note2, ' · '.join(var)
    return lv, o, note, ''
