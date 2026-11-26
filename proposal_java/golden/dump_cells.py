# 3단계 정답지 — 칸 정의(ga_spec) · 칸 값 · 세부내역 줄(ga_proposal 자료 부분) · 정보계 전 줄 한 담보 설계
# 사용 : python3 golden/dump_cells.py <출력 폴더> <2단계 정답 폴더(cases.json 이 있는 곳)> <정보계 rows.json> <code_map.json> [spec|designs|rows …]
# 출력 : spec.json · designs_NN.json(입력 묶음을 나눠서) · rows_NN.json(정보계 전 줄 — scripts/codemap/audit_rows.py 와 같은 방식)
# 실제 설계 입력 · 정보계 이름이 들어가므로 출력은 저장소에 넣지 않는다.
import sys, os, json, re, time, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'proposal_smart'))
import matcher, scen_engine as S, code_input as CI, ga_spec as GS, ga_proposal as GP, ga_care as CARE, pipeline, build_all as BA
OUT, MDIR, ROWS, CMF = sys.argv[1:5]; ONLY = set(sys.argv[5:]) or {'spec', 'designs', 'rows'}
os.makedirs(OUT, exist_ok=True); t0 = time.time()
def W(name, o): json.dump(o, open(os.path.join(OUT, name), 'w', encoding='utf-8'), ensure_ascii=False)
def plain(o): return json.loads(json.dumps(o, ensure_ascii=False, default=lambda x: sorted(x) if isinstance(x, (set, frozenset)) else str(x)))
C = json.load(open(os.path.join(MDIR, 'cases.json'), encoding='utf-8'))
rows = json.load(open(ROWS, encoding='utf-8'))
ADHOC = lambda sc_, mode: dict(kind='engine', sc=sc_, mode=mode, need=None, na_if_empty=False, key='adhoc')

if 'spec' in ONLY:
    names = sorted({r[2] for r in rows} | {r['n'] for r in matcher.DB['riders']})
    prods = sorted({json.loads(c['text']).get('product') for c in C if c['text'].lstrip().startswith('{') and c['id'][:2] != 'B:' or c['id'].startswith('B:상품 라인')} - {None})
    scs = [c['sc'] for c in GS.CELLS if c['sc']] + [GS.sc_dz(n, h) for n in GS.DZ_ORDER for h in ('상급종합', '종합', '의원')]
    S.ISSUES.clear(); uni = GS.universe()
    sp = dict(cells=plain(GS.spec_dump()), key_order=list(GS.KEY), dz_order=GS.DZ_ORDER, ga_dz={k: list(v) for k, v in GS.GA_DZ.items()}, cs=GS.CS, dxs=GS.DXS, bdx=GS.BDX, hdx=GS.HDX,
              b_thr=GS._b_thrombectomy, b_stent=GS._b_stent, h_thr=GS._h_thrombectomy, p1_tx_b=[list(x) for x in GS.P1_TX_B], p1_tx_h=[list(x) for x in GS.P1_TX_H],
              brain=[list(x) for x in GS.brain_steps('종합')], heart=[list(x) for x in GS.heart_steps('병원')], sc_dz=[[n, h, GS.sc_dz(n, h)] for n in GS.DZ_ORDER for h in ('병원', '상급종합')],
              ca1=[[h, [[n, k, md, need, nm] for n, k, s_, md, need, nm in items]] for h, items in GS._ca1], bh1=[[h, [[n, k, md, need, nm] for n, k, s_, md, need, nm in items]] for h, items in GS._bh1],
              sev=[list(x) for x in GS.SEV], ex_ca=[list(x) for x in GS.EX_CA], ex_bh=[list(x) for x in GS.EX_BH], sg=[list(x) for x in GS.SG], rows3=[list(x) for x in GS.ROWS3], cm=[list(x) for x in GS.CM], rd=[list(x) for x in GS.RD],
              inj_act=GS.INJ_ACT, base_t=GS.BASE_T, universe=plain(uni), universe_issues=plain(S.ISSUES), parents=sorted(GS.PARENTS), dbid_n=len(GS.DBID),
              sub_label=[[n, GS._sub_label(n)] for n in names if '[' in n or '가입)' in n] + [[None, GS._sub_label(None)], ['A[A[세부]]', GS._sub_label('A[A[세부]]')], ['x]', GS._sub_label('x]')]],
              sckeys=[[s_, json.dumps(s_, sort_keys=True, ensure_ascii=False)] for s_ in scs],
              ga_product_idx=[[p, GP.ga_product_idx(p)] for p in prods + [None, '', '(무) 알파Plus보장보험2610', '(무) 메리츠 The좋은 알파Plus보장보험2610', '(무)(메리츠)암보험(세만기형)2610', '(무)메리츠암보험(연만기형)2610']],
              ascii_name=[[p, GP.ascii_name(p)] for p in ['/a/b/설계서 1.pdf', 'm28-95538.pdf', '한글만.pdf', '.hidden', 'a.b.c.PDF', '/x/123.pdf', 'no_ext', '..a', '__x__.pdf', '가-1_2.pdf', '']],
              M=[[v, b, GP.M(v, b)] for v in (None, '간병인 보내줌', '면책', 0, 0.0, 1e-10, 5, 5.5, 1000.0, 13640, 123456.0) for b in (False, True)],
              tokens_of=[[v, GS.tokens_of(v)] for v in (None, '간병인 보내줌', 0.0, 5.5, 3000.0, 13640)],
              disp_name=[[n, GP.disp_name(n)] for n in names if '26종' in n][:300] + [[' 암  진단비 ', GP.disp_name(' 암  진단비 ')]])
    W('spec.json', sp); print('spec · 칸 %d · 우주 %d · %.0f초' % (len(GS.CELLS), len(uni), time.time() - t0), flush=True)

def snapshot():
    r = dict(val={k: [v[0], plain(v[1]), plain(v[2])] for k, v in GP.VAL.items()}, rid=plain(GP.RID), nrid=GP.NRID, product=GP.PRODUCT, premium=GP.PREMIUM, who=GP.WHO, shortp=GP.SHORTP,
             head=GP.HEAD, line=GP.LINE, meta=GP.META, who_line=GP.who_line(), head_bar=GP.head_bar(), issues=plain(S.ISSUES), grouped=plain(S.issues_grouped()))
    secs = GP.calc_sections()
    r['sections'] = [[t, [[lab, v, [list(x) for x in rs], GP.calc_units((lab, v, rs))] for lab, v, rs in rws]] for t, rws in secs]
    r['F'] = {k: GP.F(GP.L(k)) for k in GP.VAL if GS.KEY[k]['kind'] == 'engine'}
    r['M'] = {k: GP.M(GP.V(k)) for k in GP.VAL}; r['tokens'] = {k: GS.tokens_of(GP.V(k)) for k in GP.VAL}
    r['notes'] = [[l.get('name'), GP.line_note(l), GP._man_of(l['name'])] for k in GP.VAL for l in GP.L(k)][:4000]
    r['dzup'] = [(lambda x: [x[0], plain(x[1]), plain(x[2])])(GS.cell_value(ADHOC(GS.sc_dz(n, '상급종합'), 'first'), GP.RID)) for n in GS.DZ_ORDER]
    r['thx'] = [(lambda x: [x[0], plain(x[1]), plain(x[2])])(GS.cell_value(ADHOC(sc_, md), GP.RID)) for sc_ in (GS._b_thrombectomy, GS._h_thrombectomy) for md in ('first', 'year', 'each')]
    r['issues_end'] = plain(S.ISSUES); r['grouped_end'] = plain(S.issues_grouped()); r['recog'] = S.recog(GP.RID)
    return r

if 'designs' in ONLY:
    R = []; part = 0; nload = 0
    def flush():
        global R, part
        W('designs_%02d.json' % part, R); part += 1; R = []
    for ci, c in enumerate(C):
        os.environ['GA_CODE_MAP'] = c['cm'] or os.path.join(OUT, '_no_such_file.json'); CI._CM = None; os.environ.pop('GA_MASK', None)
        r = dict(i=ci, id=c['id'])
        try: p = CI.parse(c['text'])
        except CI.InputError: r['skip'] = 'parse'; R.append(r); continue
        excl = '제외 상품 시험용' in c['id']
        if excl: S.RULEDOC.setdefault('exclude_products', []).append({'m': '시험용제외상품', 'nm': '시험용 제외 상품', 'why': '자체 시험'})
        try:
            GP.load(p); r.update(snapshot()); r['tag'] = GP.tag_of(p) if re.sub(r'[^A-Za-z0-9_-]+', '', p.get('design_no') or '') else None; r['label'] = GP.label_of(p); nload += 1
            if c['id'] in ('A:code_input_example', 'B:표지 항목 다 없음', 'B:글자 다듬기') or (c['id'].startswith('A:') and ci % 9 == 0):
                os.environ['GA_MASK'] = '1'; GP.load(CI.parse(c['text']), '33세'); r['mask'] = dict(head=GP.HEAD, who=GP.WHO, who_line=GP.who_line(), head_bar=GP.head_bar(), issues=plain(S.ISSUES)); os.environ.pop('GA_MASK')
        except pipeline.DesignUnreadable as e:
            r['err'] = ['DesignUnreadable', str(e)]; r['issues'] = plain(S.ISSUES)
        finally:
            if excl: S.RULEDOC['exclude_products'].pop()
        R.append(r)
        if len(R) >= 12: flush()
    if R: flush()
    W('designs_index.json', dict(parts=part, cases=len(C), loaded=nload))
    print('designs · 입력 %d건 · 계산 %d건 · 파일 %d개 · %.0f초' % (len(C), nload, part, time.time() - t0), flush=True)

if 'rows' in ONLY:
    CM = json.load(open(CMF, encoding='utf-8'))['map']
    MASTER = {(r['p'], r['id']): r for r in matcher.DB['riders']}; DEFAULT = '케어프리'
    LINE = [None]; CI.line_of = lambda p: LINE[0]; CI._CM = {}
    def cells_of(rid):
        if not rid: return None, []
        GS.clear_cache(); n0 = len(S.ISSUES); out = []
        for c in GS.CELLS: out.append(GS.cell_value(c, rid)[0])
        for n in GS.DZ_ORDER: out.append(GS.cell_value(ADHOC(GS.sc_dz(n, '상급종합'), 'first'), rid)[0])
        iss = plain(S.ISSUES[n0:]); del S.ISSUES[n0:]; GS.clear_cache()
        return out, iss
    def name_rows(line, n):
        LINE[0] = line; n0 = len(S.ISSUES)
        try: ra = CI.riders(dict(product='x', riders=[dict(no=1, unit_code='', code='', name=n, amount=10000000, unused_daily=20000)]))
        except pipeline.DesignUnreadable: ra = []
        iss = plain(S.ISSUES[n0:]); del S.ISSUES[n0:]
        return ra, iss
    def base(n):
        s = re.sub(r'\[(특별조건부|계약전환용|기본계약)\]', '', n); s = re.sub(r'\((?:[^()]{0,30}가입)\)', '', s); s = re.sub(r'\(\d+년갱신\)', '', s).replace('(출생전)', '')
        return re.sub(r'^\s*갱신형\s*', '', s.strip()).strip()
    ESC10 = re.compile(r'\(\s*체증형\s*,\s*10년후\s*2배지급\s*\)')
    groups = collections.OrderedDict()
    for u, c, n in rows:
        cm = CM.get('%s|%s' % (u, c)); groups.setdefault((cm['p'] if cm else None, n, (cm['p'], cm['id']) if cm else None), 0)
    todo = collections.OrderedDict()                      # (상품 라인, 이름) → 담보 식별표 특약들(두 길 대조용)
    for (line, n, cid) in groups:
        k = (line or DEFAULT, n); todo.setdefault(k, [])
        if cid and list(cid) not in todo[k]: todo[k].append(list(cid))
    for (line, n, cid) in list(groups):                   # 갱신형 유무 · 체증형 꼬리표 유무(이름 변형)
        b = base(n)
        for v in (b, '갱신형 ' + b) + ((re.sub(r'\s{2,}', ' ', ESC10.sub('', n)),) if ESC10.search(n) else ()):
            todo.setdefault((line or DEFAULT, v), [])
    for r in matcher.DB['riders']:                         # 특약 마스터 이름 전부(제 상품 라인으로) + 갱신형을 붙인 것
        b = base(r['n'])
        for v in (b, '갱신형 ' + b): todo.setdefault((r['p'], v), [])
    S.ISSUES.clear(); R = []; part = 0; n_all = 0
    for (line, n), cids in todo.items():
        ra, i1 = name_rows(line, n); a, i2 = cells_of(ra)
        e = dict(line=line, name=n, rows=plain(ra), i1=i1, cells=a, i2=i2, alt=[])
        for cid in cids:
            cr = MASTER[tuple(cid)]; alt = dict(cat=cr.get('c'), codes=cr.get('k') or [], excl=cr.get('x') or [], hc=cr.get('hc') or [], mname=cr.get('n'), sub_rec=('[' in (cr.get('n') or '')), matched=True)
            if ra: rb = [dict(ra[0], **alt)] + ra[1:]
            else: rb = [dict(dict(no=1, name=CI._clean(n), man=1000, amount_text='1천만원', benefit=None, sub=None, itc=S.itc_id(n), unit_code='', code='', how='code'), **alt)]
            b, i3 = cells_of(rb); e['alt'].append(dict(cid=cid, rows=plain(rb), cells=b, i3=i3))
        R.append(e); n_all += 1
        if len(R) >= 4000:
            W('rows_%02d.json' % part, R); part += 1; R = []; print('rows · %d / %d · %.0f초' % (n_all, len(todo), time.time() - t0), flush=True)
    if R: W('rows_%02d.json' % part, R); part += 1
    W('rows_index.json', dict(parts=part, groups=n_all, info_rows=len(rows), leftover_issues=len(S.ISSUES)))
    print('rows · 정보계 %d줄 → (상품 라인 × 이름) %d묶음 · 파일 %d개 · %.0f초' % (len(rows), n_all, part, time.time() - t0), flush=True)
