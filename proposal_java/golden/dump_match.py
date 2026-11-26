# 2단계 정답지 — 담보 알아보기(matcher) · 상품 라인(build_all) · 담보코드 입력(code_input) · 간병인 칸(ga_care)
# 사용 : python3 golden/dump_match.py <출력 폴더> <정보계 rows.json> <입력 JSON 폴더> [code_map.json]
# 출력 : names.json(이름 × 상품 라인 매칭) · cases.json(입력 묶음 — dump_cells.py 도 쓴다) · inputs.json(입력별 담보 줄 · 표지 · 간병인 칸) · funcs.json(낱 함수)
# 정보계 이름 · 실제 설계 입력이 들어가므로 출력은 저장소에 넣지 않는다.
import sys, os, json, re, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'proposal_smart')); sys.path.insert(0, HERE)
import matcher, scen_engine as S, code_input as CI, build_all as BA, ga_care as CARE, pipeline
import cases
OUT, ROWS, INDIR = sys.argv[1:4]; CMF = sys.argv[4] if len(sys.argv) > 4 else ''
os.makedirs(OUT, exist_ok=True); t0 = time.time()
def W(name, o): json.dump(o, open(os.path.join(OUT, name), 'w', encoding='utf-8'), ensure_ascii=False)
def plain(o): return json.loads(json.dumps(o, ensure_ascii=False))

C = cases.build(INDIR, CMF, OUT); W('cases.json', C)

# ── 이름 × 상품 라인 ──
rows = json.load(open(ROWS, encoding='utf-8'))
names = []; seen = set()
def addn(n):
    if n not in seen: seen.add(n); names.append(n)
for r in rows: addn(r[2])
for r in matcher.DB['riders']: addn(r['n'])
for c in C:
    try: o = json.loads(c['text'])
    except Exception: continue
    if isinstance(o, dict) and isinstance(o.get('riders'), list):
        for r in o['riders']:
            if isinstance(r, dict) and isinstance(r.get('name'), str): addn(r['name'])
EXTRA = ['', ' ', '[', ']', '수술비[', '암진단비(', '()', '[]', '(()', '갱신형', '갱신형 ', '┗ 수술비[질병3종]', '┗수술비[상해1종](출생전)', '암진단비(유사암제외)[특별조건부]', '(20년갱신)갱신형 암진단비(유사암제외)(통합간편가입)',
         '무릎인대파열·연골손상수술비', '무릎인대파열연골손상수술비', '간호ㆍ간병통합서비스 사용 질병입원일당(1일이상 180일한도)', '다빈치로봇 암수술비(특정암)', '4대양성종양진단비Ⅱ(대장 양성종양및특정용종)',
         '통합암 주요치료비(특정소액암)(연간1회한, 10년간)', '원격전이포함 4기 통합암진단비(유사암제외)(특정소액암)', '32대질병관혈수술비[5대질병]', '갱신형 32대질병관혈수술비[5대질병]', '세상에 없는 담보', 'x' * 300]
for n in EXTRA: addn(n)
lines = [None] + sorted({r['p'] for r in matcher.DB['riders']})
S.ISSUES.clear()
res = dict(lines=lines, names=names, base=[matcher.base(n) for n in names], match=[], issues=[])
for ln in lines:
    n0 = len(S.ISSUES); col = []
    for n in names:
        m, b, s = matcher.match(n, ln)
        col.append([('%s|%s' % (m.get('p'), m['id'])) if m else None, b, s])
    res['match'].append(col); res['issues'].append(plain(S.ISSUES[n0:]))
    print('매칭 · 상품 라인 %s · %.0f초' % (ln, time.time() - t0), flush=True)
pm_names = [n for n in names if matcher.GRADE_RANGE.search(n.replace(' ', '')) or re.search(r'수술비\s*\(1-7종', n)]
for pre in ('', '갱신형 '):
    for c in ('질병', '상해'):
        for g in ('1-3', '4-7'): pm_names.append('%s수술비(1-7종, 연간3회한)[%s%s종]' % (pre, c, g))
res['pm_names'] = pm_names
res['pm'] = [[(lambda m: ('%s|%s' % (m.get('p'), m['id'])) if m else None)(matcher.parent_master(n, ln)) for n in pm_names] for ln in lines]
res['trail'] = [[n, [list(x) for x in matcher._trail_groups(matcher.base(n))], matcher._last_bracket(matcher.base(n)), sorted(matcher._labtoks(n))] for n in names[::37] + EXTRA]
W('names.json', res)
print('이름 %d개 × 상품 라인 %d · 부모 줄 이름 %d개' % (len(names), len(lines), len(pm_names)), flush=True)

# ── 낱 함수 ──
heads = set()
for c in C:
    try: o = json.loads(c['text'])
    except Exception: continue
    if isinstance(o, dict) and isinstance(o.get('product'), str): heads.add(re.sub(r'\s+', '', o['product']))
try:
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts', 'codemap'))
    import products as PR
    for v in getattr(PR, 'TERMS', {}).values():
        if isinstance(v, str): heads.add(re.sub(r'\s+', '', v))
except Exception as e: print('products.py 못 읽음 :', e)
import glob
for f in glob.glob(os.path.join(HERE, '..', '..', '*약관*.pdf')): heads.add(re.sub(r'\s+', '', os.path.basename(f)))
heads |= {'', 'onlyyou통합보험', 'ONLYYOU통합보험355간편', '(무)내Mom대로보장보험', '내Mom대로보장보험', 'The좋은알파Plus', 'The좋은케어프리보험', '올케어보장꽉채운암보험맞춤간편', '프리미엄간편보험프리미엄건강보험'}
heads = sorted(heads)
wons = [None, 0, 0.0, 1, 5, 0.5, 5.5, 5.55, 5.449999, 0.04, 100, 1000, 9999, 10000, 10001, 13640, 136400, 20000, 123456789, 2.0000001, 2.999999, 1e-7, 7000.0, 12345.6, -5, -12345, -0.5]
wtxt = [0, 1, 500, 5000, 9999, 10000, 12345, 15000, 20000, 100000, 300000, 990000, 1000000, 1230000, 10000000, 15000000, 35000000, 100000000, 150000000, 1234560000, 10000000000, 100000000000, 123456789]
F = dict(line_from_head=[[h, BA.line_from_head(h)] for h in heads],
         guess_line=[[rs, BA.guess_line(rs)] for rs in ([{'name': '질병수술비'}], [{'name': '질병수술비(통합간편가입)'}, {'name': 'x'}], [])],
         won=[[v, CARE.won(v)] for v in wons], canon=[[n, CARE.canon(n)] for n in names if '간병' in n][:400] + [[None, CARE.canon(None)]],
         man_of=[[w, CI.man_of(w)] for w in wtxt], won_text=[[w, CI.won_text(w)] for w in wtxt],
         clean=[[n, CI._clean(n)] for n in names[::23]], g17=[[n, bool(CI.G17.match(CI._clean(n)))] for n in names if '종]' in n],
         txt=[[v, n, CI._txt(v, n)] for v, n in [(None, 5), ('  a  b\n\tc  ', 200), ('가나다라마바사', 3), (123, 2), (1.5, 10), (True, 10), ([1, 'a'], 20), ({'a': 1}, 20), ('', 3), (0, 3)]])
W('funcs.json', F)

# ── 입력 묶음 : parse → 담보 줄 → 표지 · 간병인 칸 ──
def err(e): return [type(e).__name__, str(e)]
R = []
for c in C:
    os.environ.pop('GA_CODE_MAP', None)
    if c['cm']: os.environ['GA_CODE_MAP'] = c['cm']
    else: os.environ['GA_CODE_MAP'] = os.path.join(OUT, '_no_such_file.json')      # 프로그램 폴더에 code_map.json 이 있더라도 쓰지 않게
    CI._CM = None; S.ISSUES.clear()
    r = dict(id=c['id'])
    try: p = CI.parse(c['text'])
    except CI.InputError as e:
        r['parse_err'] = err(e); R.append(r); continue
    r['parse'] = plain(p); r['line'] = CI.line_of(p); r['label'] = CI.label(p); r['tag'] = CI.tag(p) if p.get('design_no') and re.sub(r'[^A-Za-z0-9_-]+', '', p['design_no']) else None
    r['meta'] = CI.meta(p)
    try: rid = CI.riders(p)
    except pipeline.DesignUnreadable as e:
        r['riders_err'] = err(e); r['issues1'] = plain(S.ISSUES); R.append(r); continue
    r['riders'] = plain(rid); r['p_line'] = p['_line']; r['issues1'] = plain(S.ISSUES); r['recog'] = S.recog(rid)
    n0 = len(S.ISSUES); r['head'] = CI.head(p); r['head_age'] = CI.head(p, '33'); r['issues2'] = plain(S.ISSUES[n0:])
    nr = CARE.norm(rid); r['norm'] = plain(nr); r['daily'] = [CARE.daily(x) for x in nr]
    r['care'] = {k: [v[0], plain(v[1])] for k, v in CARE.cells(rid).items()}
    r['care_sets'] = dict(support=plain(CARE.support(nr)), support_nh=plain(CARE.support_nh(nr)), nurse_add=plain(CARE.nurse_add(nr)), use_gen=plain(CARE.use(nr, 'gen')), dz=plain(CARE._dz(nr)),
                          unused=[CARE.unused(nr)[0], plain(CARE.unused(nr)[1])], nurse_total=[CARE.nurse_total(nr)[0], plain(CARE.nurse_total(nr)[1])], dementia=CARE.dementia(nr))
    R.append(r)
W('inputs.json', R)
print('입력 %d건(틀린 입력 %d · 멈춤 %d) · %.0f초 → %s' % (len(R), sum(1 for r in R if 'parse_err' in r), sum(1 for r in R if 'riders_err' in r), time.time() - t0, OUT))
