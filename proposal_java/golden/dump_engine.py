# -*- coding: utf-8 -*-
"""자바 판 1단계 정답지 — engine.py · scen_engine.py 가 내는 결과를 그대로 적는다.

사용 : python3 golden/dump_engine.py <출력 폴더> [정보계 rows.json] [설계서 PDF …]
  · 출력 폴더는 저장소 밖(세션 작업폴더)에 둔다 — 설계서 · 정보계 표에서 나온 자료다.
  · 자바 쪽은 src/test/java/meai/sp/GoldenEngine.java 가 같은 입력(inputs.json · names.json · funcs.json)을 읽어 계산하고 견준다.
파이썬 원본은 고치지 않고 그대로 부른다. 입력(담보 · 사례)은 JSON 으로 한 번 왕복시킨 것으로 계산한다(자바가 읽는 것과 같은 꼴).
"""
import sys, os, json, copy, re, glob, collections, time
HERE = os.path.dirname(os.path.abspath(__file__))
PS = os.path.normpath(os.path.join(HERE, '..', '..', 'proposal_smart'))
sys.path.insert(0, PS)
import warnings; warnings.filterwarnings('ignore')
import scen_engine as S, engine as itc

def rt(x): return json.loads(json.dumps(x, ensure_ascii=False))
def W(out, name, obj):
    with open(os.path.join(out, name), 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False)
    print('  %s  %.1fMB' % (name, os.path.getsize(os.path.join(out, name)) / 1e6), flush=True)

def rule_view(r):
    """classify 결과 — 규칙표의 한 줄(컴파일한 패턴은 빼고 전부)"""
    return None if r is None else {k: v for k, v in r.items() if k not in ('_m', '_x')}

# ── (a) 이름만 받는 함수 ─────────────────────────────────
def dump_names(out, rows_json):
    names = []
    seen = set()
    def add(n):
        if isinstance(n, str) and n not in seen: seen.add(n); names.append(n)
    if rows_json and os.path.exists(rows_json):
        for r in json.load(open(rows_json, encoding='utf-8')): add(r[2])
    for f in ('db.json', 'db_terms_extra.json'):
        for r in json.load(open(os.path.join(PS, f), encoding='utf-8')).get('riders') or []: add(r.get('n'))
    for k in list(itc.RM): add(itc.RM[k]['nm'])
    for k in S.ITC_MAP: add(k)
    for k in json.load(open(os.path.join(PS, 'inj_itc.json'), encoding='utf-8')): add(k)
    extra = ['', ' ', '┗ 수술비[질병3종]', '갱신형 암진단비(유사암제외)(통합간편가입)[기본계약]', '[특별조건부]갱신형 뇌졸중진단비Ⅱ(편한가입)', '(출생전)질병수술비', '질병 통합생활지원비(맞춤 간편가입)',
             '갱신형 2대질환 통합생활지원비', '상해 통합생활지원비', '암 통합생활지원비', '특정순환계질환통합치료비Ⅱ[특정순환계질환 통합치료비](통합간편가입)',
             '질병입원일당(1일이상 180일한도)(요양병원제외)', '상급종합병원 질병수술비(1-5종)[질병2종]', '수술비Ⅱ(1-5종)[상해4종]', '질병1인실입원일당(종합병원)(1일이상 30일한도)',
             '질병2-3인실입원일당(상급종합병원)(1일이상30일한도)', '중환자실입원일당(4일이상)', '질병수술비(특정6대질병및혀유착증제외)', '질병수술비(특정5대질병제외)', '통원일당(plus)', '재해골절진단비']
    for n in extra: add(n)
    S._CC.clear()
    res = []
    for n in names:
        nm = S.nname(n)
        res.append({'classify': rule_view(S.classify(n)), 'nname': nm, 'noren': S.noren(n), 'tokens': S.tokens(nm), 'itc_id': S.itc_id(n), 'ls_id': S.ls_id(n),
                    'amt': [[a, S.amt_to_man(a)] for a in re.findall(S.AMT_RE, n)]})
    amts = ['5천만원', '1억5천만원', '1억 5,000만원', '3천5백만원', '1,000만원', '2억원', '1억', '간병인지원', '5,000원', '5000원', '', None, '10만원', '1백만원', '3십만원', '2천5백만', '1억2천3백4십5만원',
            '만원', '원', '7천원', '1억 원', '12억3천만원', '0만원', '5 천 만 원', '1.5만원', '삼천만원', '30000000', '3만', '2억5,000만원', '1천', '5백', '9십', '1억1만원']
    W(out, 'names.json', {'names': names, 'res': res, 'amt': [[a, S.amt_to_man(a)] for a in amts],
                          'GOJI': S.GOJI, 'AMT_RE': S.AMT_RE, 'ITC_NORM': S._ITC_NORM, 'INJ_KNOWN': sorted(S.INJ_KNOWN), 'G131': S.G131, 'G131X': S.G131X,
                          'C13N': S._C13N, 'DB_PRODUCTS': S.DB_PRODUCTS, 'nrules': len(S.RULES)})
    return names

# ── 낱 함수 ──────────────────────────────────────────────
def dump_funcs(out, names, kcds):
    F = {}
    codes = sorted(set(list(itc.KCD) + list(itc.DZ) + kcds + ['C16', 'C73', 'C44.9', 'C61', 'C98', 'C97', 'D05.1', 'D09', 'D45', 'D46.2', 'D47', 'D47.1', 'D47.2', 'D47.3', 'D47.9', 'D37.1', 'D48', 'D32', 'D33.0', 'D12.6', 'D24',
                                                           'I63', 'I63.9', 'I21', 'I20', 'I67.1', 'G45', 'S06', 'S06.5', 'S25', 'S52.5', 'K80.0', 'M51', 'M51.1', 'N40', 'Q26.3', 'K62.7', 'F32', 'O80', 'E66', 'N39.3', 'K23.0', '', 'X', 'c16']))
    F['codes'] = codes
    F['cancer_cls'] = [itc.cancer_cls(c) for c in codes] + [itc.cancer_cls(None)]
    F['is_cancer'] = [S.is_cancer(c) for c in codes]
    F['cover'] = {r['id']: [itc.cover(r, c) for c in codes] for r in itc.RIDERS}
    F['disease_name'] = [itc.disease_name(c) for c in codes]
    F['groups_for'] = [sorted(itc.groups_for(c)) for c in codes]
    combo = {r['id']: int(min(itc.AMT[r['ty']], key=int)) for r in itc.RIDERS}
    F['combo'] = combo
    F['shown_ids'] = [itc.shown_ids(combo, c) for c in codes]
    F['item_label'] = {r['id']: [itc.item_label(r['id'], i) for i in range(len(itc.IT[r['ty']]))] for r in itc.RIDERS}
    # calc_rider — 시뮬레이터 질병별 경로 전부 × 통합치료비 전 특약 × 가입금액 구간 × 1년 이내 여부
    paths = []
    for d in itc.D['DZ']:
        for p in d.get('P') or []: paths.append([d['c'], rt({'e': p['e']})])
    paths.append(['C16', {'e': [['치료', '재활', '', ['rehab'], {'n': 12}], ['치료', '재활', '', ['rehab'], {'n': 12}], ['치료', '면역', '', ['immune'], {'nc': 1}], ['치료', '로봇', '', ['robot'], {'nc': 1}],
                                ['검사', '내시경', '', ['x_endo', 'x_ct', 'nope'], {'no': {'CB': ['x_endo'], 'all': ['x_ct']}, 'nor': {'x_endo': '사유'}}], ['수술', 's', '', ['surg'], {'j': 3}], ['수술', 's', '', ['surg']]]}])
    paths.append(['C61', {'e': [['치료', '로봇', '', ['robot'], {'nc': 1}], ['치료', '표적', '', ['target', 'immune']], ['수술', 's', '', ['surg'], {'j': 5, 'nc': 1}], ['치료', '재활', '', ['rehab']]]}])
    paths.append(['S06.5', {'e': [['수술', '개두', '', ['surg'], {'j': 5}], ['치료', '중환자실', '', ['icu', 'vent', 'crrt', 'anes6']], ['치료', '재활', '', ['rehab'], {'n': 40}]]}])
    paths.append(['I63', {'e': [['치료', '혈전용해', '', ['thromb']], ['수술', 's', '', ['surg'], {'j': 4}], ['수술', 's', '', ['surg'], {'j': 4}], ['치료', '재활', '', ['rehab'], {'n': 10}], ['치료', '재활', '', ['rehab'], {'n': 10}]]}])
    F['paths'] = paths
    cr = []
    for r in itc.RIDERS:
        for tier in list(itc.AMT[r['ty']]):
            for w in (False, True):
                for pi, (c, p) in enumerate(paths):
                    cr.append([r['id'], int(tier), pi, w, None, itc.calc_rider(r['id'], int(tier), c, copy.deepcopy(p), w)])
        for pi in (0, len(paths) - 3, len(paths) - 2):
            c, p = paths[pi]
            cr.append([r['id'], int(min(itc.AMT[r['ty']], key=int)), pi, True, ['anes6', 'icu', 'surg'], itc.calc_rider(r['id'], int(min(itc.AMT[r['ty']], key=int)), c, copy.deepcopy(p), True, skip_keys=['anes6', 'icu', 'surg'])])
        for bad in ('7', 2000.0, 99999):
            try: itc.calc_rider(r['id'], bad, 'C16', {'e': []}); cr.append([r['id'], bad, 0, False, None, 'no error'])
            except KeyError as ex: cr.append([r['id'], bad, 0, False, None, 'KeyError'])
    F['calc_rider'] = cr
    F['calc_all'] = [[c, itc.calc_all(combo, c, copy.deepcopy(p))] for c, p in paths[:40]]
    # code_hit · excluded — 마스터 목록(약관 표기 그대로) × 사례 질병코드
    lists = []
    seen = set()
    for f in ('db.json', 'db_terms_extra.json'):
        for r in json.load(open(os.path.join(PS, f), encoding='utf-8')).get('riders') or []:
            for key in ('k', 'x'):
                l = r.get(key) or []
                t = json.dumps(l, ensure_ascii=False)
                if l and t not in seen: seen.add(t); lists.append(l)
    for g, l in S.KCDG.items():
        if isinstance(l, list) and l and all(isinstance(x, str) for x in l): lists.append(l)
    for g, l in S.G131.items(): lists.append(l)
    lists += [['A15~A19', '!A17', 'Q26.0~Q26.4', ' I63 ', 'C16.1'], ['!N74.0', 'N70~N77'], []]
    hk = sorted(set(kcds + ['C16', 'C16.1', 'C73', 'D05.1', 'D12.6', 'D24', 'D25.9', 'D34', 'H25.9', 'I20', 'I21', 'I63', 'I67.1', 'I60', 'G45.9', 'K35', 'K64', 'K80.0', 'M17', 'M51', 'N20.0', 'N40', 'S52.5', 'S06',
                           'Q26.3', 'Q26', 'A17', 'A18.0', 'N74.0', 'N74', 'N75', 'K62.7', 'J35', 'N60', 'M50', 'I', 'F32', 'T31.2']))
    F['hit_kcds'] = hk; F['hit_lists'] = lists
    F['code_hit'] = [''.join('1' if S.code_hit(l, k) else '0' for k in hk) for l in lists]
    F['spans'] = [S.spans_brain_heart(l) for l in lists]
    F['hosp_ok'] = [[n, h, S.hosp_ok(n, h)] for n in (None, '', '의원', '병원', '종합', '상급종합', '요양') for h in (None, '모든', '의원', '병원', '종합', '상급종합', '요양', '기타')]
    s5 = list(S.SURG5) + ['999', 1, 3, None]
    F['surg5'] = [[x, k, S.surg5_grade(x, k), S.surg5_name(x)] for x in s5 for k in (None, 'K80.0', 'D12.6', 'C44.9', 'I63')]
    s7 = list(S.SURG7)[::7] + ['b016', 'ZZZZ', 2, 7, None]
    F['surg7'] = [[x, S.surg7_grade(x), S.surg7_name(x), S.surg7_group(x)] for x in s7]
    tgs = [{'surg': j} for j in s5] + [{'open': 1}, {'open': 0, 'surg': 'C1'}, {}, {'surg': 'C2'}, {'open': None, 'surg': '88-1'}]
    F['surg_open'] = [[t, S.surg_open(t)] for t in tgs]
    c13 = list(S.C13['groups']) + list(S.C13.get('alias') or {}) + ['위암', '없는암', None, '간암(전이포함)', '폐 암']
    F['c13_codes'] = [[n, S.c13_codes(n)] for n in c13]
    labs = list(S.G131) + ['다빈도61대질병', '다빈도62대질병', '다빈도64대질병', '다빈도 61대 질병', '유방의장애', '편도염', '없는군', None, '']
    F['g131_key'] = [[l, S.g131_key(l)] for l in labs]
    texts = ['유사암제외', '암(유사암제외)', '기타피부암 및 갑상선암', '갑상선암', '기타피부암', '유사암', '갑상선암및전립선암포함', '', None, '암진단비', '유사암(기타피부암)제외'] + [n for n in names if '암' in n][::40]
    ck = ['C16', 'C73', 'C44.9', 'D05.1', 'D45', 'D37.1', 'I63', 'D47.2']
    F['scope_texts'] = texts; F['scope_kcds'] = ck
    F['cancer_scope_ok'] = [''.join('1' if S.cancer_scope_ok(t, k) else '0' for k in ck) for t in texts]
    F['ls_tier'] = [[rid, m, S.ls_tier(rid, m)] for rid in list(S.LS) + ['none'] for m in (10, 20, 30, 50, 100, 100.0, 7, 0.5)] if S.LS else []
    try:
        import desc_engine as DE
        descs = ['', None, '- 중증질환자(암) 산정특례 : 100만원 (등록당 1회) - 종합병원 전신마취치료(급여) : 50.5만원(치료 1회당) · 전문재활치료(급여) : 1,000만원 (1일 1회) ※ 주석 - 항목 : 10만원(월 1회)',
                 '· 항암약물치료 : 30만원（월 1회） - 항암약물치료 : 40만원(월 1회) - 영 : 0만원(월 1회)']
        F['life_items'] = [[d, DE.life_items(d)] for d in descs]
    except Exception as ex:
        F['life_items'] = []
    W(out, 'funcs.json', F)

# ── (b) 지급 계산 ────────────────────────────────────────
MUT = [
    ('base', {}, None),
    ('종합', {'hosp': '종합'}, None),
    ('병원', {'hosp': '병원'}, None),
    ('요양30일', {'hosp': '요양', 'days': 30}, None),
    ('1인실10일', {'days': 10, 'room': '1인실', 'icu': 5}, None),
    ('200일통원', {'days': 200, 'visits': 3, 'daycare': 2, 'room': '2-3인실'}, None),
    ('상해5일', {'cause': '상해', 'days': 5}, None),
    ('마취6h', {'anes': 1, 'anes_h': 6, 'icu': 8, 'surg_cnt': 2}, None),
    ('마취4h약3', {'anes': 1, 'anes_h': 4, 'drug': 3, 'tx_cnt': 3, 'hosp': '종합'}, None),
    ('비급여재진단', {'drug': 2, 'nc': 1, 'recur': 1}, None),
    ('1년이내', {'drug': 1}, 'within1y'),
    ('건선5대관혈', {'psor_light_days': 30, 'psor_drug_days': 100, 'psor_inj': 3, 'five_major': 1, 'open': 1}, None),
    ('비관혈통원', {'open': 0, 'adm': 'out', 'hosp': None}, None),
    ('종정수', {}, 'intgrade'),
    ('행위추가', {'acts': ['thromb', 'crrt', 'vent'], 'done': ['rad']}, 'events'),
]
def mutate(s, tags, special):
    s = copy.deepcopy(s)
    s['tags'].update(copy.deepcopy(tags))
    if special == 'within1y': s['within1y'] = True
    if special == 'intgrade':
        if s['tags'].get('surg'): s['tags']['surg'] = 2
        s['tags']['surg7'] = 5
    if special == 'events':
        s.setdefault('itc_events', [])
        s['itc_events'] += [['치료', '재활', '', ['rehab'], {'n': 40}], ['검사', '검사', '', ['x_mri', 'x_ct', 'x_endo', 'immune'], {'nc': 1, 'no': {'CB': ['x_endo'], 'all': ['x_ct']}, 'nor': {'x_endo': '사유'}}]]
    return s

def run_bundle(out, bid, riders, scs, idxs):
    riders = rt(riders)
    S.ISSUES.clear()
    calls = []
    for i in idxs:
        n0 = len(S.ISSUES)
        s = copy.deepcopy(scs[i])
        L = S.pay_lines(riders, s)
        calls.append({'sc': i, 'lines': L, 'first': S.total_by(L, 'first'), 'year': S.total_by(L, 'year'), 'each': S.total_by(L, 'each'), 'total': S.total(L),
                      'issues': list(S.ISSUES[n0:]), 'sc_after': s})
    res = {'id': bid, 'calls': calls, 'recog': S.recog(riders), 'audit': S.audit(riders), 'issues_grouped': S.issues_grouped(), 'n_issues': len(S.ISSUES)}
    return rt(res)

def main(argv):
    only = os.environ.get('DUMP_ONLY')            # 'head' 면 이름 · 낱 함수만 다시 뽑는다
    out = argv[0]; os.makedirs(out, exist_ok=True)
    rows_json = argv[1] if len(argv) > 1 else None
    pdfs = argv[2:]
    t0 = time.time()
    import ga_spec as GS, pipeline
    base = [rt(c['sc']) for c in GS.CELLS if c['kind'] == 'engine']
    base_ids = [c['id'] for c in GS.CELLS if c['kind'] == 'engine']
    print('이름 함수', flush=True)
    names = dump_names(out, rows_json)
    print('낱 함수', flush=True)
    dump_funcs(out, names, sorted({s['kcd'] for s in base}))
    if only == 'head': return
    # 사례 : 칸 사례(base) + 조건을 바꾼 것 + 시뮬레이터 질병 경로
    scs, meta = [], []
    for mi, (mn, tags, sp) in enumerate(MUT):
        for bi, s in enumerate(base):
            scs.append(mutate(s, tags, sp)); meta.append([base_ids[bi], mn])
    n_cell = len(base)
    path_from = len(scs)
    for d in itc.D['DZ']:
        dc = itc.cancer_cls(d['c'])
        fam = 'cancer' if dc == 'major' else ('sim_cancer' if dc else ('brain' if d['c'].startswith('I6') else ('heart' if d['c'][:2] in ('I2',) else None)))
        for pi, p in enumerate(d.get('P') or []):
            scs.append(rt({'kcd': d['c'], 'tags': dict(cause='질병', hosp='상급종합', room=None, days=7, grp=[], dx=fam, surg=('33' if any('surg' in e[3] for e in p['e']) else None)), 'itc_events': p['e']}))
            meta.append(['DZ:' + d['c'], 'path%d' % pi])
    scs = rt(scs)
    uni = GS.universe()
    designs = {}
    for p in pdfs:
        try: designs['design:' + os.path.splitext(os.path.basename(p))[0]] = pipeline.read_riders(p)
        except Exception as ex: print('  ! 설계서를 못 읽음', p, ex)
    uni = GS.add_design_only(uni, list(designs.values()))
    uni_itc = [r for r in uni if r.get('itc') or S.ls_id(r['name'])]
    # 가상 담보 — 마스터에 없는 담보 · 금액표에 없는 가입금액 · 설명문 있는 통합생활지원비 · 소수 가입금액
    synth = [
        {'no': 1, 'name': '없는담보진단비', 'man': 100, 'matched': False, 'codes': [], 'excl': [], 'hc': []},
        {'no': 2, 'name': '암 통합치료비(기본형)', 'man': 1234, 'matched': True, 'itc': 'ca_basic', 'codes': [], 'excl': []},
        {'no': 3, 'name': '질병 통합치료비', 'man': 2000.0, 'matched': True, 'itc': 'dz', 'codes': [], 'excl': []},
        {'no': 4, 'name': '암 통합생활지원비', 'man': 100, 'matched': True, 'codes': [], 'excl': [], 'desc': '- 중증질환자(암) 산정특례 : 100만원 (등록당 1회) - 암(유사암제외) 항암약물치료(급여) : 50만원(월 1회) - 종합병원 전신마취치료(급여) : 30만원(치료 1회당)'},
        {'no': 5, 'name': '암 통합생활지원비', 'man': 7, 'matched': True, 'codes': [], 'excl': []},
        {'no': 6, 'name': '질병입원일당(1일이상 180일한도)', 'man': 0.5, 'matched': False, 'codes': [], 'excl': []},
        {'no': 7, 'name': '질병수술비', 'man': 30, 'matched': False, 'codes': [], 'excl': ['K64', 'F00~F99']},
        {'no': 8, 'name': '수술비(1-7종, 연간3회한)[질병4-7종]', 'man': 100, 'matched': True, 'codes': [], 'excl': []},
        {'no': 9, 'name': '뇌혈관질환수술비', 'man': 500, 'matched': False, 'codes': [], 'excl': []},
        {'no': 10, 'name': '암진단비(유사암제외)', 'man': 0, 'matched': True},
        {'no': 11, 'name': '암진단비(유사암제외)', 'man': None, 'matched': True},
        {'no': 12, 'name': '척추질병수술비(연간1회한)(관혈,비관혈)', 'man': 33, 'matched': False, 'codes': ['M51', 'M50'], 'excl': []},
        {'no': 13, 'name': '갱신형 건선특정치료비', 'man': 15, 'matched': False, 'codes': ['M51'], 'hc': ['PZ612'], 'excl': []},
        {'no': 14, 'name': '특정순환계질환(주요손상및질환) 통합치료비', 'man': 2000, 'matched': True, 'itc': 'ms', 'codes': [], 'excl': []},
        {'no': 15, 'name': '상해 통합생활지원비', 'man': 20, 'matched': True, 'codes': [], 'excl': []},
        {'no': 16, 'name': '2대질환 통합생활지원비', 'man': 20, 'matched': True, 'codes': [], 'excl': []},
        {'no': 17, 'name': '질병 통합생활지원비', 'man': 20, 'matched': True, 'codes': [], 'excl': []},
    ]
    bundles = collections.OrderedDict()
    bundles['universe'] = uni
    bundles['universe_itc'] = uni_itc
    bundles.update(designs)
    bundles['synth'] = synth
    all_idx = list(range(len(scs)))
    plan = collections.OrderedDict()
    plan['universe'] = list(range(path_from))                    # 특약 전수 × (칸 사례 + 조건을 바꾼 것)
    plan['universe_itc'] = list(range(path_from, len(scs)))      # 통합치료비 · 통합생활지원비 × 시뮬레이터 질병 경로
    for k in designs: plan[k] = all_idx
    plan['synth'] = all_idx
    W(out, 'inputs.json', {'bundles': rt(bundles), 'scs': scs, 'sc_meta': meta, 'plan': plan, 'n_cell': n_cell})
    # 왕복 확인 — JSON 으로 왕복시킨 입력과 원래 입력의 결과가 같은가(설계 한 건 · 전수 일부)
    chk = 0
    for bid in list(designs)[:3] + ['synth']:
        for i in range(0, len(scs), 97):
            S.ISSUES.clear(); a = S.pay_lines(bundles[bid], copy.deepcopy(scs[i]))
            S.ISSUES.clear(); b = S.pay_lines(rt(bundles[bid]), copy.deepcopy(scs[i]))
            assert rt(a) == rt(b), (bid, i); chk += 1
    print('왕복 확인 %d개 같음' % chk, flush=True)
    for bid, riders in bundles.items():
        t1 = time.time()
        res = run_bundle(out, bid, riders, scs, plan[bid])
        nl = sum(len(c['lines']) for c in res['calls'])
        W(out, 'out_%s.json' % re.sub(r'[^A-Za-z0-9_.-]', '_', bid), res)
        print('%s : 담보 %d · 사례 %d · 지급 줄 %d · 로그 %d · %.0f초' % (bid, len(riders), len(plan[bid]), nl, res['n_issues'], time.time() - t1), flush=True)
    print('끝 %.0f초' % (time.time() - t0))

if __name__ == '__main__':
    main(sys.argv[1:])
