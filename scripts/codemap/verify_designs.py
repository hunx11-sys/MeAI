# -*- coding: utf-8 -*-
"""설계서 담보 왕복 검증 — 「담보코드로 찾은 특약」 = 「설계서 이름으로 엔진이 찾은 특약」 인가

사내 전산은 담보를 「단위상품코드 + 담보코드」로 넘긴다. 담보 식별표(설계도 시트 4)로 찾은 특약 마스터가
생성기가 설계서 PDF 의 담보명으로 찾은 특약 마스터와 같아야, 코드로 넘겨도 같은 금액이 나온다.

  python3 verify_designs.py <작업폴더> <매핑 엑셀> <설계서 폴더> <결과 json>

설계서 담보마다
  ① 정보계 표에서 이름이 같은 줄(고지 구분자 · 띄어쓰기 · 갱신형 표기 무시)을 찾는다 — 그 설계 상품으로 추정된 단위상품코드의 줄을 먼저
  ② 그 줄(단위상품코드 + 담보코드)의 특약 마스터 = 담보 식별표와 같은 규칙으로 고른 것
  ③ 엔진이 설계서 이름으로 찾은 특약 마스터(┗ 종별 행은 부모 특약)
  ④ 판정 : 같은 ID / ID 는 다르지만 약관 자료(질병코드 · 제외코드 · 수가코드 · 분류)가 똑같음 / 다름 / 정보계에 같은 이름 없음 / 엔진이 못 찾은 담보
정보계 코드는 사내 자료다 — 결과 json 도 저장소에 넣지 않는다.
"""
import sys, os, re, json, glob, pickle, collections
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'proposal_smart')); sys.path.insert(0, os.path.join(ROOT, 'proposal_smart', 'ga_docs'))
from match import M, REC
from norm import key as nkey      # 가운뎃점 없이 견준다(norm.key · v9.11 — 글꼴을 넣지 않고 저장한 설계서 PDF 는 「·」 가 읽히지 않는다)
import matcher, pipeline, build_all as BA, ga_spec as GS, scen_engine as SE
from design_names import NOV

WORK, MAPX, DDIR, OUT = sys.argv[1:5]
rows = json.load(open(os.path.join(WORK, 'rows.json'), encoding='utf-8'))
NR = pickle.load(open(os.path.join(WORK, 'name_res.pkl'), 'rb'))
MW = openpyxl.load_workbook(MAPX, read_only=True)
def sheet_rows(ws):
    it = ws.iter_rows(values_only=True); h = next(it)
    return [dict(zip(h, r)) for r in it]
UP = {}
PRODS = {r['p'] for r in M}
for x in sheet_rows(MW['단위상품코드 추정']):
    m = re.fullmatch(r'(\S+)\(추정\)', x['추정 상품'] or '')
    if m and m.group(1) in PRODS: UP[x['단위상품코드']] = m.group(1)
MAPPED = ('정확', '세부표기', '특약단위')
nz = lambda s: re.sub(r'\s+', '', s or '')
ID = {(r['p'], r['id']): r for r in M}; BYID = collections.defaultdict(list)
for r in M: BYID[r['id']].append(r)

# 같은 알맹이 묶음(build_blueprint.canon 과 같은 규칙)
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
def pick(u, n):
    """담보 식별표(시트 4)와 같은 고르기 — (단위상품코드, 정보계 이름) → 특약 마스터 레코드"""
    lv, oid, op = NR[n][:3]
    if lv not in MAPPED: return None, lv
    r = REC[(op, oid)]; up = UP.get(u)
    same = sorted((x for x in GK[canon(r)] if x['p'] == up), key=lambda x: (('갱신형' in nz(x['n'])) != ('갱신형' in nz(n)), nz(x['n']) != nz(r['n']), len(x['n']), x['id'])) if up else []
    return (same[0] if same else r), lv
K2 = collections.defaultdict(list)
for u, c, n in rows: K2[nkey(n)].append((u, c, n))
def data_of(r): return (frozenset(r.get('k') or []), frozenset(r.get('x') or []), frozenset(r.get('hc') or []))      # 약관 자료(순서 무시). 분류 표시(c)는 화면용이라 따로 센다
def cells_of(rid):
    """GA 칸 132개 + 수술 카드 상급종합 12개의 값 — 생성기와 같은 계산(ga_spec.cell_value)"""
    GS.clear_cache(); n0 = len(SE.ISSUES); out = {}
    for c in GS.CELLS: out[c['id']] = GS.cell_value(c, rid)[0]
    for n in GS.DZ_ORDER: out['상급종합·' + n] = GS.cell_value(dict(kind='engine', sc=GS.sc_dz(n, '상급종합'), mode='first', need=None, na_if_empty=False, key='adhoc'), rid)[0]
    del SE.ISSUES[n0:]; GS.clear_cache()
    return out


res = []; tot = collections.Counter()
for pdf in sorted(glob.glob(os.path.join(DDIR, '*.pdf'))):
    base = os.path.basename(pdf); rid0 = matcher.read_proposal(pdf); line = BA.guess_line(rid0, pdf); rid = matcher.read_proposal(pdf, line=line)
    cnt = collections.Counter(); notes = []; alt = []
    for r in rid:
        child = r['name'].lstrip().startswith('┗')
        nm = re.sub(r'^[┗\s]+', '', r['name'])
        if child: em = matcher.parent_master(r.get('via') or '', line)
        else: em = matcher.match(r['name'], line)[0]
        cand = K2.get(nkey(nm)) or []
        if not cand: cnt['정보계에 같은 이름 없음'] += 1; notes.append(['정보계에 같은 이름 없음', r['name'], '', '']); alt.append(r); continue
        mine = [x for x in cand if UP.get(x[0]) == line] or cand
        if em is None:
            cnt['엔진이 못 찾은 담보(계산 제외)'] += 1; notes.append(['엔진이 못 찾은 담보(계산 제외)', r['name'], ' '.join(sorted({c for _, c, _ in mine})), '']); alt.append(r); continue
        verdicts = set(); codes = set(); worst = None
        for u, c, n in mine:
            cm, lv = pick(u, n); codes.add(c)
            if cm is None: verdicts.add('식별표에 없음(%s)' % lv)
            elif cm['id'] == em.get('id') and cm['p'] == em.get('p'): verdicts.add('같은 특약'); worst = worst or cm
            elif data_of(cm) == data_of(em): verdicts.add('ID 다름 · 약관 자료 같음'); worst = cm if (worst is None or data_of(worst) == data_of(em)) else worst
            else:
                verdicts.add('다름'); worst = cm
                df = [lab for lab, f in (('질병코드', 'k'), ('제외코드', 'x'), ('수가코드', 'hc')) if frozenset(cm.get(f) or []) != frozenset(em.get(f) or [])]
                notes.append(['다름', r['name'], c, '식별표 %s(%s) ≠ 엔진 %s(%s) · 다른 항목 : %s' % (cm['id'], cm['p'], em.get('id'), em.get('p'), ' · '.join(df))])
        v = '다름' if '다름' in verdicts else next((x for x in verdicts if x.startswith('식별표에')), None) or ('ID 다름 · 약관 자료 같음' if 'ID 다름 · 약관 자료 같음' in verdicts else '같은 특약')
        cnt[v] += 1
        if v.startswith('식별표에'): notes.append([v, r['name'], ' '.join(sorted(codes)), ''])
        # 코드 길로 찾은 특약의 약관 자료로 바꾼 담보(계산 대조용) — 여러 후보 중 엔진과 가장 다른 것으로
        alt.append(dict(r, cat=worst.get('c'), codes=worst.get('k') or [], excl=worst.get('x') or [], hc=worst.get('hc') or [], mname=worst.get('n'), sub_rec=('[' in (worst.get('n') or ''))) if worst else r)
    a, b = cells_of(rid), cells_of(alt); dif = [(k, a[k], b[k]) for k in a if a[k] != b[k]]
    cnt['계산 대조 : 칸 %d개 중 다른 칸' % len(a)] = len(dif)
    for k, x, y in dif: notes.append(['계산 다름', k, '', '설계서 이름 길 %s ≠ 담보코드 길 %s' % (x, y)])
    tot.update(cnt)
    res.append(dict(pdf=base, label=NOV.get(base, base), line=line, riders=len(rid), counts=dict(cnt), notes=notes))
    print('%-18s %-26s 담보 %3d · %s' % (base[:-4], line, len(rid), dict(cnt)), flush=True)
json.dump(dict(total=dict(tot), designs=res), open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n합계', dict(tot))
