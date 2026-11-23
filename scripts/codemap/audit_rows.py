# -*- coding: utf-8 -*-
"""정보계 전 줄 계산 대조 — 담보 한 개짜리 설계를 줄마다 만들어 세 가지를 본다(v9.07 · 2026-11-23)

  python3 audit_rows.py <작업폴더> <code_map.json> <결과 json>

설계서 18건 검증은 그 설계에 든 담보(980개)만 본다. 전산이 담보코드로 넘기는 이름은 정보계 표의 24,854줄 전부라,
줄마다(상품 라인 × 담보명) 가입금액 1,000만원 한 담보짜리 설계를 만들어 GA 칸 132개 + 수술 카드 상급종합 12개를 계산해 대조한다.

  ① 두 길 대조   : 이름으로 찾은 특약으로 계산한 값 = 담보 식별표(code_map)의 특약 자료로 계산한 값
  ② 표기 변형    : 같은 특약의 표기 변형(갱신형 · (N년갱신) · [특별조건부] · [계약전환용] · (출생전) · (체증형,10년후2배지급) · 고지 구분자 · II/Ⅱ)끼리 값이 같다
  ③ 갱신형 불변  : 담보명에 「갱신형」 을 붙인 것과 뗀 것의 값이 같다(정보계 이름 + 특약 마스터 이름 전부)

셋 다 「다른 곳 0」 이어야 한다. 다른 곳이 나오면 결과 json 에 줄 · 칸 · 두 값을 적는다 — 약관으로 어느 쪽이 맞는지 가린다.
처음 돌렸을 때(v9.06) 찾은 것 : 통합생활지원비 항목표 기억이 메모리 주소로 구분되던 것(계산이 순서에 따라 흔들림) ·
갱신형 세트 특약의 암진단비(유사암제외) 세부보장이 유사암 칸에 들어가던 것 · 세트 특약의 진단비 가입금액이 암후유장해 칸에 더해지던 것.
정보계 코드는 사내 자료다 — 작업폴더 · 결과 json 은 저장소에 넣지 않는다.
"""
import sys, os, re, json, collections, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PS = os.path.join(ROOT, 'proposal_smart'); sys.path.insert(0, PS); os.chdir(PS)
import matcher, scen_engine as SE, code_input as CI, ga_spec as GS, pipeline   # noqa: E402

WORK, CMF, OUT = sys.argv[1:4]
CM = json.load(open(CMF, encoding='utf-8'))['map']
rows = json.load(open(os.path.join(WORK, 'rows.json'), encoding='utf-8'))
MASTER = {(r['p'], r['id']): r for r in matcher.DB['riders']}
DEFAULT = '케어프리'                       # 담보 식별표에 없는 줄의 상품 라인(build_all.guess_line 의 기본값과 같다)

def cells_of(rid):
    if not rid: return {}
    GS.clear_cache(); n0 = len(SE.ISSUES); out = {}
    for c in GS.CELLS: out[c['key']] = GS.cell_value(c, rid)[0]
    for n in GS.DZ_ORDER: out['상급종합·' + n] = GS.cell_value(dict(kind='engine', sc=GS.sc_dz(n, '상급종합'), mode='first', need=None, na_if_empty=False, key='adhoc'), rid)[0]
    del SE.ISSUES[n0:]; GS.clear_cache()
    return {k: v for k, v in out.items() if v}
LINE = [None]; CI.line_of = lambda p: LINE[0]; CI._CM = {}      # 이름 길만(담보 식별표 없이) · 상품 라인은 줄마다 정해 준다
def name_rows(line, n):
    LINE[0] = line; n0 = len(SE.ISSUES)
    try: return CI.riders(dict(product='x', riders=[dict(no=1, unit_code='', code='', name=n, amount=10000000, unused_daily=20000)]))
    except pipeline.DesignUnreadable: return []
    finally: del SE.ISSUES[n0:]
_MEMO = {}
def calc(line, n):
    k = (line, n)
    if k not in _MEMO:
        ra = name_rows(line, n); _MEMO[k] = (ra, cells_of(ra))
    return _MEMO[k]
def canon(n):
    s = re.sub(r'\s+', '', n)
    s = re.sub(r'\[(특별조건부|계약전환용|기본계약)\]', '', s); s = re.sub(r'\((?:[^()]{0,30}가입)\)', '', s); s = re.sub(r'\(\d+년갱신\)', '', s)
    s = s.replace('(출생전)', '').replace('(체증형,10년후2배지급)', ''); s = re.sub(r'^갱신형', '', s)      # 10년 뒤 2배 체증형(프리미엄) = 일반형과 같은 특약(v9.10)
    return re.sub(r'(?<![A-Za-z])(IV|III|II)(?![A-Za-z])', lambda m: {'II': 'Ⅱ', 'III': 'Ⅲ', 'IV': 'Ⅳ'}[m.group(1)], s)
def base(n):
    s = re.sub(r'\[(특별조건부|계약전환용|기본계약)\]', '', n); s = re.sub(r'\((?:[^()]{0,30}가입)\)', '', s); s = re.sub(r'\(\d+년갱신\)', '', s).replace('(출생전)', '')
    return re.sub(r'^\s*갱신형\s*', '', s.strip()).strip()

res = dict(two_path=[], variant=[], renew=[]); cnt = collections.Counter(); t0 = time.time()
# ① 두 길 대조
groups = collections.OrderedDict()
for u, c, n in rows:
    cm = CM.get('%s|%s' % (u, c))
    groups.setdefault((cm['p'] if cm else None, n, (cm['p'], cm['id']) if cm else None), []).append(1)
for (line, n, cid), uc in groups.items():
    ra, a = calc(line or DEFAULT, n)
    if not cid:
        cnt['① 담보 식별표에 없는 줄 · 이름 길 금액 ' + ('있음' if a else '없음')] += len(uc); continue
    cr = MASTER[cid]; alt = dict(cat=cr.get('c'), codes=cr.get('k') or [], excl=cr.get('x') or [], hc=cr.get('hc') or [], mname=cr.get('n'), sub_rec=('[' in (cr.get('n') or '')), matched=True)
    if ra: rb = [dict(ra[0], **alt)] + ra[1:]
    else: rb = [dict(dict(no=1, name=CI._clean(n), man=1000, amount_text='1천만원', benefit=None, sub=None, itc=SE.itc_id(n), unit_code='', code='', how='code'), **alt)]
    b = cells_of(rb)
    if a == b: cnt['① 두 길 계산 같음'] += len(uc)
    else:
        cnt['① 두 길 계산 다름'] += len(uc)
        res['two_path'].append(dict(line=line, name=n, rows=len(uc), name_rider=(ra[0].get('mname') if ra else None), code_rider=cr['n'], code_id=list(cid),
                                    cells={k: [a.get(k), b.get(k)] for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)}))
print('① 두 길 대조 · 묶음 %d · %.0f초' % (len(groups), time.time() - t0), flush=True)
# ② 표기 변형
G = collections.defaultdict(dict)
for (line, n, cid) in groups: G[(line or DEFAULT, canon(n))][n] = calc(line or DEFAULT, n)[1]
for (line, k), d in G.items():
    sigs = collections.defaultdict(list)
    for n, cells in d.items(): sigs[json.dumps(cells, sort_keys=True, ensure_ascii=False)].append(n)
    if len(sigs) > 1: res['variant'].append(dict(line=line, key=k, variants=[dict(cells=json.loads(s), names=v[:8]) for s, v in sigs.items()]))
cnt['② 특약 묶음(상품 라인 × 특약)'] = len(G); cnt['② 표기 변형끼리 계산이 다른 묶음'] = len(res['variant'])
print('② 표기 변형 · 묶음 %d · %.0f초' % (len(G), time.time() - t0), flush=True)
# ③ 갱신형 불변
seen = set(); todo = []
for (line, n, cid) in groups:
    k = (line or DEFAULT, re.sub(r'\s+', '', base(n)))
    if k not in seen: seen.add(k); todo.append((line or DEFAULT, base(n)))
for r in matcher.DB['riders']:
    k = (r['p'], re.sub(r'\s+', '', base(r['n'])))
    if k not in seen: seen.add(k); todo.append((r['p'], base(r['n'])))
for line, b in todo:
    a = calc(line, b)[1]; g = calc(line, '갱신형 ' + b)[1]
    if a != g: res['renew'].append(dict(line=line, name=b, cells={k: [a.get(k), g.get(k)] for k in sorted(set(a) | set(g)) if a.get(k) != g.get(k)}))
cnt['③ 담보(상품 라인 × 담보명)'] = len(todo); cnt['③ 갱신형 유무로 계산이 달라지는 담보'] = len(res['renew'])
print('③ 갱신형 불변 · 담보 %d · %.0f초' % (len(todo), time.time() - t0), flush=True)
bad = len(res['two_path']) + len(res['variant']) + len(res['renew'])
json.dump(dict(rows=len(rows), count=dict(cnt), **res), open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
for k in sorted(cnt): print('%7d  %s' % (cnt[k], k))
print('\n결과 : %s — 정보계 %d줄' % ('전부 통과(다른 곳 0)' if not bad else '다른 곳 %d묶음(%s)' % (bad, OUT), len(rows)))
sys.exit(1 if bad else 0)
