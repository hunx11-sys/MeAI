# -*- coding: utf-8 -*-
"""담보 식별표 → code_map.json (담보코드 입력이 쓰는 조회표)

  python3 export_code_map.py <작업폴더> <매핑 엑셀> <code_map.json>

「단위상품코드|담보코드」 → 특약 마스터 ID · 상품. 고르는 규칙은 담보코드 설계도 시트 4(담보 식별표)와 같다
(단위상품코드의 추정 상품 안에서 같은 알맹이 · 같은 갱신형 여부 특약). 판정 단계 ① 정확 ② 세부표기 ③ 특약단위만 싣는다.
**정보계 코드가 들어 있는 사내 자료다 — 저장소에 넣지 않는다.** 서버에는 환경변수 GA_CODE_MAP 으로 경로를 주거나
proposal_smart/code_map.json 으로 둔다(.gitignore). 없어도 담보코드 입력은 돈다 — 담보명으로 찾고, 이 표는 이름으로 못 찾은 담보의 보조다.
"""
import sys, os, re, json, pickle, collections, datetime
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'proposal_smart'))
from match import M, REC

def load(WORK, MAPX):
    rows = json.load(open(os.path.join(WORK, 'rows.json'), encoding='utf-8'))
    NR = pickle.load(open(os.path.join(WORK, 'name_res.pkl'), 'rb'))
    ws = openpyxl.load_workbook(MAPX, read_only=True)['단위상품코드 추정']; it = ws.iter_rows(values_only=True); h = next(it)
    PRODS = {r['p'] for r in M}; UP = {}
    for r in it:
        x = dict(zip(h, r)); m = re.fullmatch(r'(\S+)\(추정\)', x['추정 상품'] or '')
        if m and m.group(1) in PRODS: UP[x['단위상품코드']] = m.group(1)
    return rows, NR, UP
MAPPED = ('정확', '세부표기', '특약단위')
nz = lambda s: re.sub(r'\s+', '', s or '')
_CAN = {}
def canon(r):
    k = (r['p'], r['id'])
    if k in _CAN: return _CAN[k]
    par = REC.get((r['p'], r.get('parent'))) if r.get('parent') else None
    if par:
        P = set(par['_t']); sub = set()
        for t in r['_t']:
            if t in P: continue
            for sx in ('진단비', '치료비', '수술비', '입원일당'):
                if par['_k'].endswith(sx) and t.endswith(sx): t = t[:-len(sx)]; break
            if t and t not in P and t not in ('연간1회한', '최초1회한'): sub.add(t)
        v = canon(par) + '|' + '+'.join(sorted(sub))
    else: v = '+'.join(sorted(set(r['_t'])))
    _CAN[k] = v; return v
GK = collections.defaultdict(list)
for r in M: GK[canon(r)].append(r)
def pick(u, n, NR, UP):
    lv, oid, op = NR[n][:3]
    if lv not in MAPPED: return None, lv
    r = REC[(op, oid)]; up = UP.get(u)
    same = sorted((x for x in GK[canon(r)] if x['p'] == up), key=lambda x: (('갱신형' in nz(x['n'])) != ('갱신형' in nz(n)), nz(x['n']) != nz(r['n']), len(x['n']), x['id'])) if up else []
    return (same[0] if same else r), lv

if __name__ == '__main__':
    WORK, MAPX, OUT = sys.argv[1:4]
    rows, NR, UP = load(WORK, MAPX); mp = {}; clash = 0
    for u, c, n in rows:
        m, lv = pick(u, n, NR, UP)
        if not m: continue
        k = '%s|%s' % (u, c); v = dict(id=m['id'], p=m['p'], lv=lv)
        if k in mp and (mp[k]['id'], mp[k]['p']) != (v['id'], v['p']): clash += 1; continue      # 한 짝에 이름이 둘이고 특약이 다르면 먼저 것(이름으로 찾는 길이 우선이라 계산에는 영향 없음)
        mp.setdefault(k, v)
    json.dump(dict(schema=1, built=datetime.date.today().isoformat(), source_rows=len(rows), count=len(mp), note='단위상품코드|담보코드 → 특약 마스터 ID · 사내 자료(저장소에 넣지 않는다)', map=mp),
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('code_map.json · 짝 %d개(정보계 %d줄 중) · 한 짝에 특약이 둘인 것 %d · %s' % (len(mp), len(rows), clash, OUT))
