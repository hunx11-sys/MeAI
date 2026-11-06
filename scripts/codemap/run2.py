# -*- coding: utf-8 -*-
"""정보계 이름마다(코드 × 이름) 우리 특약에 맞춘다 — 코드 하나에 상품마다 다른 이름이 붙기 때문(예 : 한 코드에 「뇌혈관질환수술비」 · 「뇌혈관질환수술비Ⅱ」)"""
import json, pickle, collections
from match import match, RANK
import sys, os
WORK = sys.argv[1]
rows = json.load(open(os.path.join(WORK, 'rows.json'), encoding='utf-8'))
names = sorted({n for u, c, n in rows})
NR = {}
for n in names:
    lv, o, note, var = match(n)
    NR[n] = (lv, o['id'] if o else None, o['p'] if o else None, note, var)
pickle.dump(NR, open(os.path.join(WORK, 'name_res.pkl'), 'wb'))
print(len(NR), collections.Counter(v[0] for v in NR.values()))
