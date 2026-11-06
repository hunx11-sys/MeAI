# -*- coding: utf-8 -*-
"""정보계 담보코드 ↔ 우리 특약 마스터 매핑 엑셀 만들기

사용 : python3 build.py <작업폴더> <출력 엑셀>   (먼저 extract_rows.py · toc.py · run2.py)
"""
import json, re, pickle, collections, sys, os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = sys.argv[1]                       # 작업폴더(rows.json · name_res.pkl · terms_txt/toc.json)
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'rider_code_map.xlsx')
sys.path.insert(0, HERE)
from match import M, REC, QUAL, kids, toks, score
from norm import strip_tags, key as nkey
sys.path.insert(0, os.path.join(ROOT, 'proposal_smart'))
import scen_engine as se

rows = json.load(open(os.path.join(BASE, 'rows.json'), encoding='utf-8'))
NR = pickle.load(open(os.path.join(BASE, 'name_res.pkl'), 'rb'))
from match import RANK as _RK

# ── 회사 자료 정리 ───────────────────────────────────────────
names = collections.defaultdict(collections.Counter); units = collections.defaultdict(set); U = collections.defaultdict(list)
for u, c, n in rows:
    names[c][n] += 1; units[c].add(u)
    if c not in U[u]: U[u].append(c)
codes = sorted(names)
GOJI = re.compile(r'\((?:[^()]{0,30}가입)\)')

FAM = [('610', '상해'), ('611', '상해'), ('620', '비용손해·실손·펫'), ('621', '비용손해·실손·펫'),
       ('630', '질병·암·뇌심'), ('631', '질병·암·뇌심'), ('632', '질병·암·뇌심'), ('633', '질병·암·뇌심'), ('634', '질병·암·뇌심'), ('635', '질병·암·뇌심'),
       ('640', '간병·치매·치아·장기요양'), ('641', '간병·치매·치아·장기요양'), ('650', '화재·재물손해'), ('660', '배상책임'),
       ('680', '적립보험료'), ('690', '제도성·묶음(상위) 코드')]
FAMD = dict(FAM)
def fam(c): return FAMD.get(c[:3], '기타')

def variants(ns):
    v = []
    if any('[특별조건부]' in n for n in ns): v.append('특별조건부')
    if any('[계약전환용]' in n for n in ns): v.append('계약전환용')
    yrs = sorted({m for n in ns for m in re.findall(r'\((\d+)년갱신\)', n)}, key=int)
    if yrs: v.append('/'.join(yrs) + '년갱신')
    if any('갱신형' in n for n in ns): v.append('갱신형 이름 있음')
    if any(re.search(r'\(출생전\)', n) for n in ns): v.append('출생전')
    if any('전환용' in n and '[계약전환용]' not in n for n in ns): v.append('전환용')
    return ' · '.join(v)
def goji(ns):
    c = collections.Counter(t for n in ns for t in GOJI.findall(n))
    return ' '.join(t for t, _ in c.most_common())

# ── 우리 마스터 ──────────────────────────────────────────────
_CAN = {}
def canon(r):
    """같은 알맹이 열쇠 — 세부보장은 「부모 열쇠 | 부모 이름에 없는 세부 낱말」(암진단및치료비Ⅱ[암진단및치료비Ⅱ[암진단비]] = 암진단및치료비Ⅱ[암진단비])"""
    k = (r['p'], r['id'])
    if k in _CAN: return _CAN[k]
    par = REC.get((r['p'], r.get('parent'))) if r.get('parent') else None
    if par:
        P = set(par['_t']); sub = set()
        for t in r['_t']:
            if t in P: continue
            for sx in ('진단비', '치료비', '수술비', '입원일당'):
                if par['_k'].endswith(sx) and t.endswith(sx):
                    t = t[:-len(sx)]; break
            if t and t not in P: sub.add(t)
        sub = sorted(sub)
        v = canon(par) + '|' + '+'.join(sub)
    else:
        v = '+'.join(sorted(set(r['_t'])))
    _CAN[k] = v; return v
GK = collections.defaultdict(list)
for r in M: GK[canon(r)].append(r)
PRODS = ['통합간편', '케어프리', '운전자', '치아', '또또암', '또또암간편', '간편31', '내Mom대로', '내Mom같은어린이',
         'The건강한내Mom대로5.10.5', 'The건강한5.10.5', 'The좋은내Mom대로', 'The가벼운간편355', 'The좋은케어프리']
PFULL = {
    '통합간편': '무배당 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형)',
    '케어프리': '무배당 메리츠 케어프리보험 M-Basket2610 (GA 판매명 알파Plus보장보험 · 특약 구성 같음)',
    '운전자': '무배당 메리츠 운전자 상해 종합보험2610',
    '치아': '무배당 메리츠 치아보험 이목구비2601',
    '또또암': '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(일반심사형)',
    '또또암간편': '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(맞춤간편심사형) — 옛 이름 「간편한 암보험」',
    '간편31': '무배당 메리츠 간편31 건강보험2610',
    '내Mom대로': '무배당 내Mom대로 보장보험2610',
    '내Mom같은어린이': '무배당 내Mom같은 어린이보험2610(태아전용)',
    'The건강한내Mom대로5.10.5': '무배당 메리츠 The건강한 내Mom대로 5.10.5 보장보험2610',
    'The건강한5.10.5': '무배당 메리츠 The건강한 5.10.5 보장보험2610',
    'The좋은내Mom대로': '무배당 메리츠 The좋은 내Mom대로 보장보험2610',
    'The가벼운간편355': '무배당 The가벼운 간편355건강보험(세만기형)2610',
    'The좋은케어프리': '무배당 메리츠 The좋은 케어프리보험 M-Basket2610 (GA 판매명 The좋은 알파Plus · 케어프리와 다른 상품)',
}
PORDER = {p: i for i, p in enumerate(PRODS)}
def plist(rs): return ', '.join(sorted({r['p'] for r in rs}, key=lambda p: PORDER.get(p, 99)))

# 규칙표 보상 유형 이름(GA 설계도 ⑦)
wb0 = openpyxl.load_workbook(os.path.join(ROOT, 'dist', 'ga-blueprint-final.xlsx'), read_only=True)
KIND = {}
for r in wb0['⑦ 규칙표'].iter_rows(min_row=2, values_only=True):
    if r[0]: KIND[r[0]] = r[1]
# GA 칸(③ 칸별 특약 · 이 칸 집계에 포함 = 예)
CELL_ID = collections.defaultdict(set); CELL_KEY = collections.defaultdict(set)
for r in wb0['③ 칸별 특약(마스터 전체)'].iter_rows(min_row=2, values_only=True):
    if r[19] != '예': continue
    cid, nm, src, loc = r[0], r[7], r[9] or '', r[24] or ''
    CELL_KEY[nkey(nm)].add(cid)
    if loc and not loc.startswith(('design-', 'row')): CELL_ID[loc].add(cid)
    m = re.search(r'마스터 (\S+?)\(', src)
    if m: CELL_ID[m.group(1)].add(cid)

def rule_of(n):
    try:
        if se.itc_id(n): return 'itc', '통합치료비(약관 지급금액표)'
        if se.ls_id(n): return 'ls', '통합생활지원비(약관 월 항목표)'
        r = se.classify(n)
    except Exception as e:
        return '', '판정 오류 %s' % e
    if not r: return '', '규칙 없음(계산 제외 · 빈칸)'
    return r['id'], KIND.get(r['id']) or r.get('kind', '')

# ── 약관 목차(저장소 루트 PDF 20개) ─────────────────────────
TOCF = {1: ('The가벼운간편355', 'y'), 2: ('내Mom같은어린이', 'y'), 3: ('내Mom대로', 'y'), 4: ('The건강한5.10.5', 'y'), 5: ('The건강한내Mom대로5.10.5', 'y'),
        6: ('The좋은내Mom대로', 'y'), 7: ('The좋은 알파Plus(= The좋은케어프리)', 'y'), 8: ('The좋은케어프리', 'y'), 9: ('간편31', 'y'), 10: ('또또암간편', 'y'),
        11: ('또또암', 'y'), 12: ('치매간병통합케어(355Ⅱ간편심사형)', 'dem'), 13: ('치매간병통합케어(일반심사형)', 'dem'), 14: ('운전자', 'y'), 15: ('치아', 'y'),
        16: ('케어프리', 'y'), 17: ('통합간편(355입원,수술고지간편심사형)', 'tg'), 18: ('통합간편(일반심사형)', 'tg'), 19: ('통합간편(통합간편심사형)', 'y'), 20: ('알파Plus(= 케어프리)', 'y')}
TOCJ = json.load(open(os.path.join(BASE, 'terms_txt', 'toc.json'), encoding='utf-8'))
def tkey(t):
    t = re.sub(r'^\d+(-\d+)*\.', '', t).replace('보장특별약관', '').replace('특별약관', '')
    t = re.sub(r'보장(?=\()', '', t); t = re.sub(r'보장$', '', t)
    return nkey(t)
TOCK = collections.defaultdict(set)
for i, ls in TOCJ.items():
    for l in ls: TOCK[tkey(l)].add(int(i))
def toc_find(ns):
    hit = set()
    for n in ns:
        k = nkey(re.sub(r'\((출생전|최초발생후 ?전환용|전환용)\)', '', n)); k2 = re.sub(r'추가$', '', k)
        hit |= TOCK.get(k, set()) | TOCK.get(k2, set())
    return sorted(hit)

# ── 분류 사유 ───────────────────────────────────────────────
ADMIN = re.compile(r'특약$|특별약관|부담보|부보장|납입|대리청구|전자서명|서비스|전환특|할인|연금|단체취급|저축|자동갱신|인수|정산|기부|할증|출생전자녀가입')
def reason(c, lv, note, nm):
    ns = list(names[c]); s = ' '.join(ns)
    if c[:3] == '690' and ADMIN.search(s): return '분류 안 됨', '제도성 특약(보험금 지급 담보 아님)'
    if lv in ('정확', '세부표기', '특약단위'): return '매핑됨', ''
    if lv == '유사':
        if '10년후2배지급' in note: return '확인 필요', '변형 특약(체증형 · 10년후 2배지급) — 우리 약관에는 이 판이 없음'
        if '괄호 설명' in note: return '확인 필요', '이름 비슷(우리 이름에만 괄호 설명) — 같은 특약인지 확인'
        if QUAL.search(note.split('—')[0]): return '확인 필요', '변형 특약(감액·전환·Ⅱ/Ⅲ 등) — 같은 특약인지 확인'
        return '확인 필요', '이름 비슷(낱말 일부 다름) — 같은 특약인지 확인'
    if c[:3] == '680': return '분류 안 됨', '적립보험료 · 보너스(보장 담보 아님)'
    if '펫퍼민트' in s: return '분류 안 됨', '펫보험(펫퍼민트) — 도구 대상 아닌 상품'
    if c[:3] == '650': return '분류 안 됨', '화재 · 재물손해 — 도구 대상 아닌 상품'
    if c[:3] == '660': return '분류 안 됨', '배상책임 — 우리 약관(운전자 등)에 없는 배상책임'
    if c[:3] in ('620', '621') and re.search(r'의료비|실손|상급병실차액', s): return '분류 안 됨', '실손의료비 — 도구 대상 아닌 상품'
    if re.search(r'이륜자동차|PM 운전중|자전거', s): return '분류 안 됨', '이륜차 · PM · 자전거 전용 담보 — 우리 약관에 없음'
    if re.search(r'치매|장기요양|돌봄지원금', s): return '분류 안 됨', '치매 · 장기요양 담보 — 스마트 제안서 대상 아닌 상품(치매간병통합케어 등) 또는 판매중지로 지운 담보'
    if c[:3] in ('620', '621'): return '분류 안 됨', '운전자 비용손해(벌금 · 처리지원금 등) — 우리 운전자 약관에 없는 판'
    if re.search(r'치아|치과|임플란트', s): return '분류 안 됨', '치아 담보 — 우리 치아 약관(2601)에 없음'
    if c[:3] == '690': return '분류 안 됨', '상위(묶음) 코드 — 우리 약관에 없는 특약'
    if re.search(r'체증형|10년후2배지급', s): return '분류 안 됨', '변형 특약(체증형 등) — 우리 약관에 이 판 없음'
    if note.startswith('가장 가까운 후보'): return '분류 안 됨', '우리 약관(14개 상품)에 없는 담보 — 같은 계열 다른 판 또는 신담보'
    return '분류 안 됨', '우리 약관(14개 상품)에 없는 담보'

LVN = {'정확': '① 정확', '세부표기': '② 세부표기', '특약단위': '③ 특약단위', '유사': '④ 유사(확인)', '없음': '⑤ 없음'}

# ── 코드별 줄 ───────────────────────────────────────────────
CODE = {}
MAPPED = ('정확', '세부표기', '특약단위')
CN = {}   # 코드 → [(이름, 단계, 우리 특약)]
for c in codes:
    CN[c] = [(n,) + NR[n] for n in names[c]]
for c in codes:
    lv, oid, op, note, var, nm = min(((x[1], x[2], x[3], x[4], x[5], x[0]) for x in CN[c]), key=lambda t: (_RK[t[0]], 1 if t[4] else 0, len(t[5])))
    o = REC.get((op, oid)) if oid else None
    cls, why = reason(c, lv, note, nm)
    ns = [n for n, _ in names[c].most_common()]
    toc = toc_find(ns) if cls != '매핑됨' else []
    tocs = ', '.join(TOCF[i][0] for i in toc)
    if toc and cls != '매핑됨' and '제도성' not in why:
        kinds = {TOCF[i][1] for i in toc}
        if 'y' in kinds: why = '우리 약관에 특약으로 있는데 마스터에 없음 — 마스터 누락 의심(확인)'; cls = '확인 필요'
        elif 'tg' in kinds: why = '통합간편 다른 심사형(355 · 일반) 약관에만 있음 — 우리 마스터(통합간편심사형 약관)에 없음'
        elif 'dem' in kinds: why = '치매간병통합케어 약관에 있음 — 스마트 제안서 대상 아닌 상품'
    rep = ns[0]
    gs = []
    if cls == '매핑됨':
        for x in CN[c]:
            if x[1] in MAPPED:
                k3 = canon(REC[(x[3], x[2])])
                if k3 not in gs: gs.append(k3)
        k0 = canon(o)
        if k0 in gs: gs.remove(k0)
        gs = [k0] + gs
    g = [r for k3 in gs for r in GK[k3]]
    rid, rkind = rule_of(o['n']) if o and cls == '매핑됨' else ('', '')
    cells = set()
    if cls == '매핑됨':
        for n in ns: cells |= CELL_KEY.get(nkey(n), set())
        if lv != '특약단위' or not cells:
            for r in g: cells |= CELL_ID.get(r['id'], set())
    multi = [GK[k3][0]['n'] for k3 in gs[1:]]
    CODE[c] = dict(c=c, rep=rep, nn=len(ns), nu=len(units[c]), fam=fam(c), lv=lv, lvn=LVN[lv], cls=cls, why=why,
                   note=note, toc=tocs, mvar=var, var=variants(ns), goji=goji(ns), nm=nm,
                   oid=o['id'] if o else '', op=o['p'] if o else '', on=o['n'] if o else '',
                   gp=plist(g), gid=', '.join('%s:%s' % (r['p'], r['id']) for r in sorted(g, key=lambda r: PORDER.get(r['p'], 99))),
                   rid=rid, rkind=rkind, kcd=len(o.get('k') or []) if o and cls == '매핑됨' else '',
                   pg=o.get('pg', '') if o and cls == '매핑됨' else '', cells=' '.join(sorted(cells)), ncell=len(cells),
                   o=o, g=g, gs=gs, multi=multi)

# ── 우리 특약 → 코드 ─────────────────────────────────────────
def vtag(c):
    d = CODE[c]; t = []
    if '특별조건부' in d['var']: t.append('특조')
    if '계약전환용' in d['var']: t.append('전환')
    if d['mvar']: t.append(d['mvar'].replace(' 변형', '').replace(' 가입', ''))
    return c + ('[' + ','.join(t) + ']' if t else '')
BYK = collections.defaultdict(lambda: collections.defaultdict(list))
for c, d in CODE.items():
    if d['cls'] == '매핑됨':
        for x in CN[c]:
            if x[1] in MAPPED:
                k3 = canon(REC[(x[3], x[2])])
                if c not in BYK[k3][x[1]]: BYK[k3][x[1]].append(c)
    elif d['cls'] == '확인 필요' and d['o']: BYK[canon(d['o'])]['유사'].append(c)

# ── 단위상품코드 추정 ────────────────────────────────────────
TAGP = {'(편한가입)': ['The가벼운간편355'], '(건강가입)': ['The건강한5.10.5', 'The건강한내Mom대로5.10.5'], '(31간편가입)': ['간편31'], '(315간편가입)': ['간편31'],
        '(맞춤간편가입)': ['또또암간편'], '(통합간편가입)': ['통합간편'], '(355입원,수술고지간편가입)': ['통합간편'], '(355Ⅱ간편가입)': []}
TAGNOTE = {'(355입원,수술고지간편가입)': '통합간편 355입원·수술고지간편심사형(우리 마스터는 통합간편심사형 약관)', '(355Ⅱ간편가입)': '치매간병통합케어(355Ⅱ간편심사형) — 도구 대상 아님'}
UNTAG = ['케어프리', '운전자', '치아', '또또암', '내Mom대로', '내Mom같은어린이', 'The좋은내Mom대로', 'The좋은케어프리', '통합간편']   # 약관 목차에 고지 구분자가 없는 상품(통합간편은 일반심사형)
RENEWP = {p: sum(1 for r in M if r['p'] == p and r['n'].replace(' ', '').startswith('갱신형')) / max(1, sum(1 for r in M if r['p'] == p)) for p in PRODS}
def unit_row(u):
    cs = U[u]; ns = [n for uu, c, n in UR[u]]
    tg = collections.Counter(t for n in ns for t in GOJI.findall(n))
    dom = tg.most_common(1)[0][0] if tg and tg.most_common(1)[0][1] >= 0.5 * len(ns) else ''
    if dom: allowed = TAGP.get(dom); why = TAGNOTE.get(dom, '고지 구분자 %s' % dom if dom in TAGP else '고지 구분자 %s 를 쓰는 약관이 저장소에 없음 — 후보를 좁히지 않음' % dom)
    else: allowed = UNTAG; why = '고지 구분자 없음 — 일반심사형 상품 중에서'
    rr = [(c, n) for uu, c, n in UR[u] if NR[n][0] in MAPPED]
    mapped = sorted({c for c, n in rr})
    cov = collections.Counter()
    for c, n in rr:
        for p in {r['p'] for r in GK[canon(REC[(NR[n][2], NR[n][1])])]}: cov[p] += 1
    ren = sum(1 for n in ns if strip_tags(n) != re.sub(r'\s+', '', n) and re.sub(r'^\(\d+년갱신\)', '', n.replace('[특별조건부]', '').replace('[계약전환용]', '')).startswith('갱신형')) / len(ns) if ns else 0
    def val(p): return cov[p] / len(rr) - 0.3 * abs(ren - RENEWP.get(p, 0)) if rr else 0
    pool = [p for p in cov if allowed is None or p in allowed]
    top = sorted(pool, key=lambda p: -val(p))[:3]
    if allowed and rr and (not top or cov[top[0]] / len(rr) < 0.6):
        top = sorted(cov, key=lambda p: -val(p))[:3]; why += ' → 그 상품과 담보가 안 맞아 전체 상품에서 다시 찾음(같은 구분자를 쓰는 다른 상품일 수 있음)'
    s = ' '.join(ns)
    rate = len(mapped) / len(cs) if cs else 0
    if allowed == []:
        guess = '도구 대상 아님(추정) — ' + TAGNOTE[dom]
    elif rate < 0.3:
        if '펫퍼민트' in s: guess = '도구 대상 아님(추정) — 펫보험'
        elif re.search(r'의료비', s) and any(c[:3] in ('620', '621') for c in cs): guess = '도구 대상 아님(추정) — 실손의료비'
        elif any(c[:3] in ('650', '660') for c in cs): guess = '도구 대상 아님(추정) — 화재 · 재물 · 배상책임'
        elif re.search(r'치매|장기요양', s): guess = '도구 대상 아님(추정) — 치매 · 장기요양(치매간병통합케어 등)'
        else: guess = '도구 대상 아님(추정) — 우리 약관에 담보가 거의 없음'
    elif not top: guess = '후보 없음'
    else:
        p1 = top[0]; share = cov[p1] / len(rr)
        guess = ('%s(추정)' % p1) if share >= 0.6 else ('혼합 · 불명확(추정 1순위 %s)' % p1)
    def fmt(i):
        if i >= len(top): return ''
        p = top[i]; return '%s %d/%d' % (p, cov[p], len(rr))
    fams = collections.Counter(fam(c) for c in cs).most_common(2)
    return [u, len(cs), len(mapped), rate, ' '.join('%s %d' % x for x in tg.most_common(3)), why, '%.0f%%' % (ren * 100), guess, fmt(0), fmt(1), fmt(2),
            ', '.join('%s %d' % f for f in fams), ' · '.join(ns[:3])]
UR = collections.defaultdict(list)
for u, c, n in rows: UR[u].append((u, c, n))

# ── 엑셀 ────────────────────────────────────────────────────
F = '맑은 고딕'
HF = Font(name=F, bold=True, color='FFFFFF', size=10); BF = Font(name=F, size=10); TF = Font(name=F, bold=True, size=14)
HFILL = PatternFill('solid', fgColor='3A3A3A')
LVF = {'정확': 'E2F0D9', '세부표기': 'DDEBF7', '특약단위': 'FFF2CC', '유사': 'FCE4D6', '없음': 'EDEDED'}
CLF = {'매핑됨': 'E2F0D9', '확인 필요': 'FCE4D6', '분류 안 됨': 'EDEDED'}
thin = Side(style='thin', color='D0D0D0'); BRD = Border(top=thin, bottom=thin, left=thin, right=thin)
WRAP = Alignment(wrap_text=True, vertical='top'); TOP = Alignment(vertical='top')

wb = openpyxl.Workbook()
def sheet(title, head, data, widths, fills=None, wrapcols=()):
    ws = wb.create_sheet(title)
    ws.append(head)
    for i, h in enumerate(head, 1):
        cl = ws.cell(1, i); cl.font = HF; cl.fill = HFILL; cl.alignment = Alignment(wrap_text=True, vertical='center'); cl.border = BRD
    for row in data: ws.append(row)
    for r in ws.iter_rows(min_row=2):
        for cl in r:
            cl.font = BF; cl.border = BRD
            cl.alignment = WRAP if cl.column in wrapcols else TOP
    if fills:
        for col, mp in fills:
            for r in range(2, ws.max_row + 1):
                v = ws.cell(r, col).value
                for k2, fc in mp.items():
                    if v and str(v).endswith(k2) or v == k2:
                        ws.cell(r, col).fill = PatternFill('solid', fgColor=fc)
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 32
    return ws

# 2. 담보코드 매핑
H2 = ['담보코드', '대표 담보명(정보계)', '코드 계열(앞 3자리 · 추정)', '판정 단계', '분류', '사유(분류 안 됨 · 확인 필요)', '판정 메모',
      '이름 변형 수', '쓰는 단위상품코드 수', '변형 표시(이름에 있음)', '고지 구분자(무시함)', '판정에 쓴 이름',
      '우리 특약 ID', '우리 상품', '우리 특약명(마스터)', '이 코드가 걸린 우리 상품(코드의 모든 이름 기준)', '이 코드가 걸린 우리 특약(상품:ID)',
      '보상 유형(규칙표)', '규칙ID', '질병코드(KCD) 범위 수', '약관 쪽', 'GA 칸 수', 'GA 칸 번호', '이 코드에 걸린 우리 특약 묶음 수', '다른 이름으로 걸린 우리 특약(정보계가 같은 코드로 씀)']
D2 = []
for c in codes:
    d = CODE[c]
    D2.append([c, d['rep'], d['fam'], d['lvn'], d['cls'], d['why'], d['note'] + ((' · ' + d['mvar']) if d['mvar'] else ''),
               d['nn'], d['nu'], d['var'], d['goji'], d['nm'],
               d['oid'], d['op'], d['on'], d['gp'], d['gid'], d['rkind'], d['rid'], d['kcd'], d['pg'], d['ncell'] or '', d['cells'], len(d['gs']) or '', ' / '.join(d['multi'])])
ws2 = sheet('담보코드 매핑', H2, D2, [9, 46, 16, 12, 11, 34, 40, 8, 9, 20, 22, 40, 11, 12, 46, 30, 40, 18, 18, 9, 7, 7, 30, 9, 46],
            fills=[(4, {'정확': LVF['정확'], '세부표기': LVF['세부표기'], '특약단위': LVF['특약단위'], '유사(확인)': LVF['유사'], '없음': LVF['없음']}),
                   (5, CLF)], wrapcols=(2, 6, 7, 15, 25))

# 3. 분류 안 됨 · 확인 필요
H3 = ['담보코드', '대표 담보명(정보계)', '분류', '사유', '판정 단계', '가장 가까운 우리 특약(참고)', '우리 상품', '판정 메모', '약관 목차에 같은 이름(저장소 약관 20개)', '코드 계열(추정)', '쓰는 단위상품코드 수', '이름 변형(전부)', '체크(담당자 기입)']
D3 = []
order = {'확인 필요': 0, '분류 안 됨': 1}
for c in sorted([c for c in codes if CODE[c]['cls'] != '매핑됨'], key=lambda c: (order[CODE[c]['cls']], CODE[c]['why'], c)):
    d = CODE[c]
    D3.append([c, d['rep'], d['cls'], d['why'], d['lvn'], d['on'], d['op'], d['note'], d['toc'] or '없음', d['fam'], d['nu'], ' / '.join(n for n, _ in names[c].most_common()), ''])
ws3 = sheet('분류 안 됨·확인 필요', H3, D3, [9, 46, 11, 44, 12, 46, 12, 40, 30, 16, 9, 60, 14], fills=[(3, CLF)], wrapcols=(2, 4, 6, 8, 9, 12))
for r in range(2, ws3.max_row + 1): ws3.cell(r, 13).fill = PatternFill('solid', fgColor='FFFF00')

# 4. 우리 특약 → 담보코드
CST = collections.defaultdict(list)
for c in codes:
    for n in names[c]:
        t = toks(n)
        if t: CST[t[0]].append((c, n, t))
def nearest(r):
    best = None
    for c, n, t in CST.get(r['_stem'], []):
        cc, co = score(t, None, r); v = cc + co
        if best is None or v > best[0]: best = (v, c, n, cc, co)
    if not best: return '같은 첫 낱말의 정보계 이름 없음'
    return '%s %s (낱말 %.0f%% · %.0f%%)' % (best[1], best[2], best[3] * 100, best[4] * 100)
H4 = ['상품', '특약 ID', '특약명(마스터)', '부모 특약 ID', '보상 유형(규칙표)', '규칙ID', '정보계 코드(정확 · 세부표기)', '정보계 코드(세부보장 단위 · 특약단위)',
      '확인 필요 코드(유사)', '코드 수', '코드 상태', '가장 가까운 정보계 이름(코드 없을 때 참고)', '같은 알맹이 다른 상품']
D4 = []; NC = collections.Counter()
for r in sorted(M, key=lambda r: (PORDER.get(r['p'], 99), r['id'])):
    b = BYK.get(canon(r), {})
    a1 = sorted(set(b.get('정확', []) + b.get('세부표기', []))); a2 = sorted(set(b.get('특약단위', []))); a3 = sorted(set(b.get('유사', [])))
    rid, rk = rule_of(r['n'])
    others = sorted({x['p'] for x in GK[canon(r)]} - {r['p']}, key=lambda p: PORDER.get(p, 99))
    n = len(a1) + len(a2); near = ''
    if n: st = '코드 있음'
    else:
        ks = kids.get((r['p'], r['id']), [])
        kc = sum(1 for k in ks if any(BYK.get(canon(k), {}).get(x) for x in ('정확', '세부표기', '특약단위')))
        if ks and kc: st = '부모 특약 — 코드는 세부보장에 있음(세부 %d개 중 %d개)' % (len(ks), kc)
        else: st = '정보계 코드 못 찾음'; near = nearest(r)
    NC[st.split(' —')[0] if st.startswith('부모') else st] += 1
    D4.append([r['p'], r['id'], r['n'], r.get('parent', ''), rk, rid, ' '.join(vtag(c) for c in a1), ' '.join(vtag(c) for c in a2), ' '.join(a3),
               n, st, near, ', '.join(others)])
ws4 = sheet('우리 특약→담보코드', H4, D4, [14, 11, 50, 10, 18, 18, 40, 40, 18, 7, 26, 50, 30], wrapcols=(3, 7, 8, 11, 12),
            fills=[(11, {'코드 있음': 'E2F0D9', '못 찾음': 'FCE4D6'})])

# 5. 단위상품코드 추정
H5 = ['단위상품코드', '담보 수', '우리 특약과 맞춘 담보 수', '맞춘 비율', '고지 구분자(이름에 붙은 것 · 건수)', '후보를 좁힌 근거', '갱신형 이름 비율', '추정 상품', '추정 1순위(맞춘 이름 중 보유 수)', '2순위', '3순위', '주 코드 계열', '담보명 예']
D5 = [unit_row(u) for u in sorted(U)]
ws5 = sheet('단위상품코드 추정', H5, D5, [11, 7, 9, 8, 30, 34, 9, 36, 26, 22, 22, 30, 70], wrapcols=(5, 6, 8, 13))
for r in range(2, ws5.max_row + 1): ws5.cell(r, 4).number_format = '0%'

# 6. 이름 하나에 코드 여러 개
byname = collections.defaultdict(set)
for u, c, n in rows: byname[n].add(c)
H6 = ['정보계 담보명', '코드 수', '담보코드(판정 단계)', '같은 우리 특약으로 맞췄나']
D6 = []
for n, cs in sorted(byname.items()):
    if len(cs) < 2: continue
    cs = sorted(cs); tg = {(CODE[c]['op'], CODE[c]['oid']) for c in cs if CODE[c]['cls'] == '매핑됨'}
    same = '예(같은 특약)' if len(tg) == 1 and all(CODE[c]['cls'] == '매핑됨' for c in cs) else ('아니오 — 확인' if len(tg) > 1 else '맞춘 코드 없음/일부')
    D6.append([n, len(cs), ' '.join('%s(%s)' % (c, CODE[c]['lv']) for c in cs), same])
ws6 = sheet('이름 하나에 코드 여러 개', H6, D6, [60, 7, 60, 20], wrapcols=(1, 3))

# 6-2. 코드 하나에 우리 특약 묶음 여럿
H8 = ['담보코드', '대표 담보명(정보계)', '우리 특약 묶음 수', '정보계 이름 → 맞춘 우리 특약(상품:ID 특약명)', '판단(담당자 기입)']
D8 = []
for c in codes:
    d = CODE[c]
    if len(d['gs']) < 2: continue
    seen = []; lines2 = []
    for x in sorted(CN[c], key=lambda x: x[0]):
        if x[1] not in MAPPED: continue
        o2 = REC[(x[3], x[2])]; k3 = canon(o2)
        if (x[0], k3) in seen: continue
        seen.append((x[0], k3)); lines2.append('%s  →  %s:%s %s' % (x[0], o2['p'], o2['id'], o2['n']))
    D8.append([c, d['rep'], len(d['gs']), '\n'.join(lines2), ''])
ws8 = sheet('코드 하나에 특약 여럿', H8, D8, [9, 40, 9, 110, 18], wrapcols=(2, 4))
for r in range(2, ws8.max_row + 1): ws8.cell(r, 5).fill = PatternFill('solid', fgColor='FFFF00')

# 7. 전체 행
H7 = ['단위상품코드', '담보코드', '상품담보명(정보계 원문)', '이 이름의 판정 단계', '코드 분류', '우리 상품(이 이름과 맞춘 특약)', '우리 특약 ID']
D7 = [[u, c, n, NR[n][0], CODE[c]['cls'], NR[n][2] if NR[n][0] in MAPPED else '', NR[n][1] if NR[n][0] in MAPPED else ''] for u, c, n in rows]
ws7 = sheet('전체 행', H7, D7, [11, 9, 70, 10, 11, 14, 12])

# 1. 안내 · 집계
ws = wb['Sheet']; ws.title = '안내·집계'; wb.move_sheet(ws, offset=-(len(wb.sheetnames) - 1))
W = "'담보코드 매핑'"
_ex = sorted([c for c in codes if len(CODE[c]['gs']) >= 2 and CODE[c]['lv'] == '정확'], key=lambda c: (0 if any('Ⅱ' in GK[k3][0]['n'] for k3 in CODE[c]['gs']) else 1, c))[:2]
EX1 = ' · '.join('%s = %s' % (c, ' / '.join('%s 「%s」' % (GK[k3][0]['p'], GK[k3][0]['n']) for k3 in CODE[c]['gs'][:2])) for c in _ex)
EX2 = ' · '.join('%s 「%s」(약관 : %s)' % (c, CODE[c]['rep'], CODE[c]['toc']) for c in codes if '누락' in CODE[c]['why'])
L = []
def put(r, c, v, font=BF, fill=None):
    cl = ws.cell(r, c, v); cl.font = font; cl.alignment = Alignment(wrap_text=True, vertical='top')
    if fill: cl.fill = PatternFill('solid', fgColor=fill)
    return cl
put(1, 1, '정보계 담보코드 ↔ 스마트 제안서 특약 마스터 매핑 (2026-11-06 · 2610 약관 기준)', TF)
lines = [
    '목적 : IT개발파트가 쓰는 정보계 담보코드로 스마트 제안서 · 세일즈북 생성기 · 영업지원도구의 특약을 가리킬 수 있게, 회사 담보코드 3,536개를 우리 특약 마스터(14개 상품 · 4,976건, 약관 파싱)에 맞춘 표.',
    '원자료 : 회사 제공 「단위상품코드 · 담보코드 · 상품담보명」 표 24,854행(단위상품코드 203개). 우리 쪽 : proposal_smart/db.json(영업지원도구 감수본 6개 상품) + db_terms_extra.json(약관 PDF 파싱 8개 상품).',
    '맞추는 원칙 : 「특약 알맹이 내용이 같으면 같은 담보」. 고지 구분자 (맞춤간편가입) · (편한가입) · (355간편가입) 등과 [기본계약] · 앞의 「갱신형」 · (N년갱신) 은 무시하고 비교했다. [특별조건부] · [계약전환용] · (출생전) · 전환용 · 「추가」 는 정보계에서 코드가 따로 있어 같은 우리 특약에 붙이되 「변형 표시」 칸에 적었다.',
    '같은 알맹이 : 우리 마스터에서 이름(고지 구분자 · 갱신형 · 띄어쓰기 제외)이 같은 특약은 상품이 달라도 같은 특약으로 본다(소유자 확인 : 이름이 같으면 약관 별표도 같다). 그래서 코드 하나가 여러 상품의 특약에 걸린다 — 「같은 알맹이 보유 상품」 칸.',
    '자동 판정이다 : 이름 글자를 낱말 단위로 맞춘 결과라 ④ 유사 · ⑤ 없음은 사람이 한 번 더 봐야 한다(「분류 안 됨·확인 필요」 시트 · 노란 칸에 체크). ③ 특약단위는 회사가 세부보장(종별 · 급별 · 암종별)마다 코드를 나눈 것을 우리 특약 하나에 붙인 것이다.',
    '코드 계열(앞 3자리)의 뜻은 회사 공식 정의가 아니라 이름 분포를 보고 붙인 추정이다. 「단위상품코드 추정」 시트의 상품도 담보 구성 · 고지 구분자로 본 추정이다.',
    'GA 칸 : GA 스마트 제안서 설계도(dist/ga-blueprint-final.xlsx ③ 칸별 특약)에서 이 특약이 집계되는 칸 번호. 보상 유형 · 규칙ID 는 계산 엔진(scen_engine.classify)이 우리 특약명으로 판정한 것.',
    '중요 1 — 담보코드와 이름은 1:1 이 아니다 : 정보계는 담보 개념마다 코드를 주고, 상품마다 다른 이름을 붙인다(예 : %s). 그래서 우리 특약은 「단위상품코드 + 담보코드」 짝으로 찾는다 — 「전체 행」 시트가 짝마다 맞춘 결과다. 코드 하나에 우리 특약이 여럿 걸린 %d개는 「코드 하나에 특약 여럿」 시트, 이름 하나에 코드가 여럿인 %d개는 「이름 하나에 코드 여러 개」 시트.' % (EX1, len(D8), len(D6)),
    '중요 2 — 마스터 점검 : 약관 20개 목차와 대조해 「우리 약관에 특약으로 있는데 마스터에 없음」으로 나온 것 — %s.' % (EX2 or '없음'),
    '취급 : 정보계 담보코드는 사내 자료다. 사외로 보내지 않는다. 설계사명 · 고유번호 같은 개인정보는 이 표에 없다.',
]
r = 2
for t in lines: put(r, 1, t, Font(name=F, size=10, bold=t.startswith('중요'))); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6); ws.row_dimensions[r].height = 58 if t.startswith('중요') else 44; r += 1
r += 1
put(r, 1, '판정 단계', Font(name=F, bold=True, size=11)); r += 1
for k2, t in [('① 정확', '고지 구분자 등을 떼면 이름이 글자까지 같음'), ('② 세부표기', '낱말은 같고 괄호 모양 · 순서 · 띄어쓰기 · 줄임 표기만 다름(예 : [특정항암] = [특정항암호르몬약물허가치료비])'),
              ('③ 특약단위', '회사는 세부보장 단위 코드, 우리 마스터는 특약 단위 — 우리 특약에 붙임(예 : 수술비Ⅱ(1-5종)[질병3종] → 수술비Ⅱ(1-5종))'),
              ('④ 유사(확인)', '비슷하지만 우리에 없는 낱말이 있음 — 대개 체증형 · 10년후2배지급 같은 다른 판. 같은 특약인지 확인 필요'),
              ('⑤ 없음', '우리 약관 14개 상품에 같은 알맹이가 없음(펫 · 실손 · 화재 · 치매 상품, 제도성 특약, 우리에 없는 신담보 등)')]:
    put(r, 1, k2, BF, LVF[{'①': '정확', '②': '세부표기', '③': '특약단위', '④': '유사', '⑤': '없음'}[k2[0]]]); put(r, 2, t); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6); ws.row_dimensions[r].height = 30; r += 1
r += 1
put(r, 1, '집계(수식 · 「담보코드 매핑」 시트를 센다)', Font(name=F, bold=True, size=11)); r += 1
put(r, 1, '판정 단계', HF, '3A3A3A'); put(r, 2, '코드 수', HF, '3A3A3A'); put(r, 3, '비율', HF, '3A3A3A'); r += 1
r0 = r
for k2 in ['① 정확', '② 세부표기', '③ 특약단위', '④ 유사(확인)', '⑤ 없음']:
    put(r, 1, k2); put(r, 2, '=COUNTIF(%s!$D:$D,A%d)' % (W, r)); c3 = put(r, 3, '=B%d/$B$%d' % (r, r0 + 5)); c3.number_format = '0.0%'; r += 1
put(r, 1, '합계', Font(name=F, bold=True, size=10)); put(r, 2, '=SUM(B%d:B%d)' % (r0, r - 1), Font(name=F, bold=True, size=10)); c3 = put(r, 3, '=B%d/$B$%d' % (r, r0 + 5)); c3.number_format = '0.0%'; r += 2
put(r, 1, '분류', HF, '3A3A3A'); put(r, 2, '코드 수', HF, '3A3A3A'); put(r, 3, '비율', HF, '3A3A3A'); r += 1
r1 = r
for k2 in ['매핑됨', '확인 필요', '분류 안 됨']:
    put(r, 1, k2, BF, CLF[k2]); put(r, 2, '=COUNTIF(%s!$E:$E,A%d)' % (W, r)); c3 = put(r, 3, '=B%d/$B$%d' % (r, r0 + 5)); c3.number_format = '0.0%'; r += 1
r += 1
put(r, 1, '사유 갈래(분류 안 됨 · 확인 필요)', HF, '3A3A3A'); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4); put(r, 5, '코드 수', HF, '3A3A3A'); r += 1
for why in sorted({CODE[c]['why'] for c in codes if CODE[c]['why']}, key=lambda w: -sum(1 for c in codes if CODE[c]['why'] == w)):
    put(r, 1, why); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4); put(r, 5, '=COUNTIF(%s!$F:$F,A%d)' % (W, r)); r += 1
r += 1
put(r, 1, '코드 계열(추정)', HF, '3A3A3A'); put(r, 2, '코드 수', HF, '3A3A3A'); put(r, 3, '매핑됨', HF, '3A3A3A'); put(r, 4, '매핑 비율', HF, '3A3A3A'); r += 1
for fm in dict.fromkeys(v for _, v in FAM):
    put(r, 1, fm); put(r, 2, '=COUNTIF(%s!$C:$C,A%d)' % (W, r)); put(r, 3, '=COUNTIFS(%s!$C:$C,A%d,%s!$E:$E,"매핑됨")' % (W, r, W))
    c4 = put(r, 4, '=IF(B%d=0,0,C%d/B%d)' % (r, r, r)); c4.number_format = '0%'; r += 1
r += 1
put(r, 1, '우리 상품(짧은 이름 → 약관)', HF, '3A3A3A'); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5); put(r, 2, '약관(2026-11-06 저장소 기준)', HF, '3A3A3A'); put(r, 6, '특약 수 · 코드 붙은 특약', HF, '3A3A3A'); r += 1
for p in PRODS:
    put(r, 1, p); put(r, 2, PFULL[p]); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
    put(r, 6, '=COUNTIF(\'우리 특약→담보코드\'!$A:$A,A%d)&" · "&COUNTIFS(\'우리 특약→담보코드\'!$A:$A,A%d,\'우리 특약→담보코드\'!$J:$J,">0")' % (r, r)); r += 1
r += 1
put(r, 1, '우리 특약 코드 상태', HF, '3A3A3A'); put(r, 2, '특약 수', HF, '3A3A3A'); r += 1
for k2 in ['코드 있음', '부모 특약 — 코드는 세부보장에 있음*', '정보계 코드 못 찾음']:
    put(r, 1, k2.replace('*', '')); put(r, 2, '=COUNTIF(\'우리 특약→담보코드\'!$K:$K,"%s")' % k2); r += 1
for i, w in enumerate([30, 14, 10, 12, 10, 26], 1): ws.column_dimensions[get_column_letter(i)].width = w

wb.save(OUT)
print('saved', OUT)
print(collections.Counter(d['cls'] for d in CODE.values()), collections.Counter(d['lv'] for d in CODE.values()))
print(collections.Counter(d['why'] for d in CODE.values() if d['why']).most_common())
print('our riders', len(D4), NC); print('multi-group codes', len(D8))
