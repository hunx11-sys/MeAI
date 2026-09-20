# -*- coding: utf-8 -*-
"""설계 담보 전체(진단비·수술비·입원일당·치료비·통합치료비)에 대한 사례별 보상 계산 엔진 v3.1 (모듈 v8.3).

  ▣ 판정 근거는 두 가지뿐이다.
     ① 담보명   : rules.json 규칙표(보상구조) + 담보명 토큰(상해/질병·병원 종별·병실·한도일수·종·제외질병)
     ② 약관 KCD : db.json 의 특약별 KCD 목록 · g131.json 그룹표 · 별표3 암분류 로직(engine.cancer_cls)
     ※ KCD 목록은 어떤 경우에도 코드에서 생성·추정하지 않는다.
  ▣ 규칙표에 없는 담보가 들어와도 예외를 던지지 않는다. 계산에서 제외하고 ISSUES 에 사유를 남긴다.
     (운영 원칙 : 미매칭 담보 = 제외 + 로그)
"""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import engine as itc            # 통합치료비 약관 지급금액표 엔진

# ══ 가입금액 표기 → 만원 (v8.3 : 억·천·백·십·만 조합 전부 처리, 원 단위는 0) ═══════════
# 설계서 표기 예 : 5천만원 · 1억5천만원 · 1억 5,000만원 · 3천5백만원 · 1,000만원 · 2억원 · 1억 · 간병인지원
AMT_RE = (r'간병인지원'
          r'|(?=\d)(?:\d[\d,]*억\s*)?(?:\d[\d,]*천)?(?:\d[\d,]*백)?(?:\d[\d,]*십)?(?:\d[\d,]*)?만원'
          r'|\d[\d,]*억\s*(?:\d[\d,]*천)?(?:\d[\d,]*백)?(?:\d[\d,]*십)?(?:\d[\d,]*만)?원?')
_AMT_FULL = re.compile(r'(?:(\d+)억)?(?:(\d+)천)?(?:(\d+)백)?(?:(\d+)십)?(\d+)?(만)?원?')
def amt_to_man(s):
    """'1억5천만원' → 15000. 해석 불가·원 단위(5,000원)·현물(간병인지원)은 0."""
    s = re.sub(r'[\s,]', '', s or '')
    m = _AMT_FULL.fullmatch(s)
    if not m or not any(m.groups()[:5]): return 0
    eok, cheon, baek, sip, man = (int(g) if g else 0 for g in m.groups()[:5])
    if not (eok or cheon or baek or sip or m.group(6)): return 0      # '5000원' 같은 원 단위 → 만원 미만 취급
    return eok * 10000 + cheon * 1000 + baek * 100 + sip * 10 + man

# ══ 규칙표 ══════════════════════════════════════════════════════════
RULEDOC = json.load(open(os.path.join(BASE, 'rules.json'), encoding='utf-8'))
RULES = RULEDOC['rules']
for _r in RULES:
    _r['_m'] = re.compile(_r['m'])
    _r['_x'] = re.compile(_r['x']) if _r.get('x') else None
KCDG = RULEDOC['kcd_groups']
FIVE_MAJOR = KCDG['특정5대질병']                      # 특정5대질병(대장용종·백내장·후각특정질환·특정피부질환·혈관종)

G131 = json.load(open(os.path.join(BASE, 'g131.json'), encoding='utf-8'))
SYN = json.load(open(os.path.join(BASE, 'product_data.json'), encoding='utf-8'))['EMB']['syn']   # 암종명 → KCD
G131['유방의장애'] = ['N60', 'N61', 'N62', 'N63', 'N64', 'D24']; G131['편도염'] = ['J03', 'J35']

# ══ 1-7종 수술분류표 (약관 별표3, extract_surg7.py 로 생성) — 수술코드 → 종 (v8.5) ═══════════
SURG7 = {}
_p7 = os.path.join(BASE, 'surg7.json')
if os.path.exists(_p7): SURG7 = {r['code']: r for r in json.load(open(_p7, encoding='utf-8'))['rows']}
def surg7_grade(x):
    """사례의 1-7종 표기 : 정수(종) 그대로, 수술코드('F121' 등)는 분류표에서 종을 찾는다. 모르면 None."""
    if x is None or isinstance(x, int): return x
    r = SURG7.get(str(x).upper()); return r['grade'] if r else None
def surg7_name(x):
    r = SURG7.get(str(x).upper()) if isinstance(x, str) else None
    return r['name'] if r else ''
def surg7_group(x):
    """수술코드 → 분류표의 수술구분 이름(예 B016 → '뇌동맥류수술'). 모르면 ''."""
    r = SURG7.get(str(x).upper()) if isinstance(x, str) else None
    return (r.get('group') or '') if r else ''

# ══ 1-5종 수술분류표Ⅱ (약관 별표76, extract_surg5.py 로 생성) — 항목번호 → 종, 질병코드 예외 (v8.6) ═══
SURG5 = {}
_p5 = os.path.join(BASE, 'surg5.json')
if os.path.exists(_p5): SURG5 = {i['no']: i for i in json.load(open(_p5, encoding='utf-8'))['items']}
def surg5_grade(x, kcd=None):
    """사례의 1-5종 표기 : 정수(종) 그대로, 항목번호('33'·'88-1'·'C1' 등)는 분류표에서 종을 찾고
       '단, ○○(KCD)로 인한 수술은 N종' 예외(담석증 K80→2종, 대장 용종 D12→1종, 기타피부암 C44→3종 등)를 질병코드로 적용한다."""
    if x is None or isinstance(x, int): return x
    it = SURG5.get(str(x))
    if not it: return None
    for e in it.get('exceptions') or []:
        if kcd and (kcd == e['kcd'] or kcd.startswith(e['kcd'])): return e['grade']
    return it['grade']
def surg5_name(x):
    it = SURG5.get(str(x)) if isinstance(x, str) else None
    return it['name'] if it else ''

# 고지유형 꼬리표 — rules.json goji_tags 한 곳에서만 관리(v8.3). matcher.py 도 이 GOJI 를 가져다 쓴다.
GOJI = r'\((?:%s)\)' % '|'.join(re.escape(t) for t in RULEDOC['goji_tags'])
def nname(n):
    """고지유형 꼬리표·공백 제거 — 규칙표 매칭에 쓰는 정규화 담보명"""
    return re.sub(r'\s+', '', re.sub(GOJI, '', n or '').replace('[기본계약]', '').replace('┗', ''))

# ══ 통합치료비 식별 (v8.3 : 약관 지급금액표 RIDERS 에서 자동 생성 + 보조 별칭) ═══════════
ITC_MAP = {r['nm']: r['id'] for r in itc.RIDERS}
ITC_MAP.update({'암 통합치료비(주요치료)(비급여(전액본인부담 포함))': 'ca_ncm'})
_ITC_NORM = {nname(k): v for k, v in ITC_MAP.items()}
def noren(n):
    """설계서의 '갱신형' 접두어를 뗀 이름 — 약관 지급금액표는 갱신 여부를 구분하지 않는다(v8.20)"""
    return re.sub(r'^갱신형', '', nname(n))
def itc_id(name):
    """약관 지급금액표가 있는 통합치료비면 그 id, 아니면 None(→ 규칙표 itc_unknown 이 계산 제외+로그)"""
    return _ITC_NORM.get(nname(name)) or _ITC_NORM.get(noren(name))
# ══ 통합생활지원비 식별 (v8.36) ════════════════════════════════════════════════
# 통합생활지원비는 통합치료비와 구조가 다르다 — 산정특례 등록·치료 항목마다 **월** 단위로 지급하고
# 가입금액은 '월간 총 지급금액 한도'다. 정액 치료비로 계산하면 진단만으로 가입금액 전액이 잡히므로
# 사례 계산에서는 빼고(rules.json ls_monthly), 지면에는 약관 항목표(life_support.json)를 그대로 보여준다.
LS = {}
if os.path.exists(os.path.join(BASE, 'life_support.json')):
    LS = json.load(open(os.path.join(BASE, 'life_support.json'), encoding='utf-8'))
_LS_PAT = [('two_ls', '2대질환'), ('inj_ls', '상해'), ('dz_ls', '질병'), ('ca_ls', '암')]
def ls_id(name):
    """통합생활지원비면 그 id(ca_ls·two_ls·dz_ls·inj_ls), 아니면 None"""
    nm = noren(name)
    if '통합생활지원비' not in nm: return None
    head = nm.split('통합생활지원비')[0]
    for rid, key in _LS_PAT:
        if key in head and rid in LS: return rid
    return None
def ls_tier(rid, man):
    """가입금액(월간 총 지급금액) → 약관 항목표. 구간이 없으면 None — 금액을 추정하지 않는다."""
    t = (LS.get(rid) or {}).get('tiers') or {}
    return t.get(str(int(man))) or t.get(str(man))

INJ_KNOWN = set()                                     # 상해 통합치료비 : gen2 가 inj_itc.json 으로 별도 계산
if os.path.exists(os.path.join(BASE, 'inj_itc.json')):
    INJ_KNOWN = {nname(k) for k in json.load(open(os.path.join(BASE, 'inj_itc.json'), encoding='utf-8'))}

# 담보 → 항목표. 근거는 두 가지이며 순서가 정해져 있다.
#   ① 이 설계서 상품설명서의 담보 설명문에 실린 항목표 — 1순위(그 상품·그 가입금액의 실제 표)
#   ② 약관 지급금액표(life_support.json) — 설명문이 없을 때. 단 서로 다른 상품 약관에서
#      같은 표임을 대조한 담보만 쓴다. 확인하지 못한 금액은 만들지 않는다.
_LS_ITEMS = {}
def ls_items(r):
    """담보 → (항목표, 근거) · 근거는 'paper'(상품설명서) · 'book'(약관) · None(없음)"""
    key = id(r)
    if key in _LS_ITEMS: return _LS_ITEMS[key]
    rid = ls_id(r['name'])
    res = ([], None)
    if rid:
        v = LS.get(rid) or {}
        book = ls_tier(rid, r['man'])
        try:
            import desc_engine as DE
            paper = DE.life_items(r.get('desc') or '')
        except Exception:
            paper = []
        if paper and book:
            k = lambda xs: sorted((re.sub(r'\s', '', x['label']), x['amt']) for x in xs)
            if k(paper) != k(book):
                log('교차대조', r['name'], '상품설명서 설명문과 약관 지급금액표의 항목·금액이 달라 설명문 기준으로 표시함')
        if paper: res = (paper, 'paper')
        elif book and len(v.get('srcs') or []) >= 2: res = (book, 'book')
        elif book: log('근거부족', r['name'], '이 상품 약관·설명문에서 항목표를 확인하지 못해 계산·지면에서 제외 (다른 상품 약관 1곳에만 있어 대조 불가)')
        else: log('금액표없음', r['name'], '가입금액 %g만원 구간의 항목표가 설명문에도 약관에도 없어 계산·지면에서 제외' % r['man'])
    _LS_ITEMS[key] = res
    return res

# 사례 단계 → 통합생활지원비 항목. 약관 항목명을 그대로 읽어 맞춘다.
#   · 전신마취는 **기본(급여)만** 인정한다 — 4시간·6시간 이상 여부는 사례로 단정할 수 없다(과소 계산 쪽으로).
#   · 산정특례 등록 시점은 **질환마다 다르다**(약관 별표87~89 · 본인일부부담금 산정특례 기준).
#       암·유사암·뇌수막 양성신생물 : 등록된 암환자가 **등록일로부터 5년간** → 사실상 진단과 함께.
#                                    그래서 진단 단계에서 지급하고, 진단비 칸에도 함께 센다.
#       뇌혈관질환 : 그 상병의 치료를 위하여 【별표88-2】의 **수술을 받은 경우** 최대 30일.
#                    그 목록에 **경피적뇌혈관약물성형술(M6599 · 동맥내 혈전용해)** 이 들어 있고,
#                    수술을 받지 않아도 뇌경색은 24시간 이내 내원·NIHSS 5점 이상이면 등록된다.
#                    → **혈전용해치료도 등록 사유로 본다.**
#       심장질환   : 그 상병의 치료를 위하여 【별표89-2】의 수술 **또는 【별표89-3】의 약제** 투여 최대 30일.
#                    그 약제가 **Alteplase · Tenecteplase · Urokinase 주사제** — 전부 혈전용해제다.
#                    → **혈전용해치료만 받아도 등록**된다(약관 명시).
#     → 뇌·심장은 진단만으로 등록되지 않으므로 **수술·시술·혈전용해 단계**에서 지급하고
#       진단비 칸에는 넣지 않는다. 산정특례는 '등록당' 지급이라 한 사례에서 한 번만 센다(gen2.flow_card).
#   · 희귀질환·중증난치·중증화상·중증외상 산정특례는 사례로 단정하지 않는다.
def _ls_evkeys(sc):
    ks = set()
    for ev in (sc.get('itc_events') or []):
        if len(ev) > 3: ks |= set(ev[3] or [])
    return ks

def ls_lines(r, sc):
    """이 사례 단계에서 통합생활지원비가 얼마 나오는지 → [(항목명, 금액)] · 합계는 월간 한도(가입금액)까지"""
    items, src = ls_items(r)
    if not items: return [], False
    tg = sc.get('tags') or {}
    ks = _ls_evkeys(sc)
    code = sc.get('kcd') or ''
    dc = itc.cancer_cls(code)
    dx = tg.get('dx') or ''
    grp = tg.get('grp') or []
    # 계열 판정 — 진단 태그·질병군 말고 'series' 로도 본다.
    # 혈전용해 같은 단계는 질병군 태그를 달면 그 그룹의 다른 담보까지 지급되어 버리므로,
    # 계산에 영향을 주지 않는 표시 태그를 따로 둔다.
    ser = tg.get('series') or ''
    brain = (dx == 'brain') or (ser == 'brain') or ('뇌혈관질환' in grp)
    heart = (dx == 'heart') or (ser == 'heart') or ('심장질환' in grp)
    anes = bool(tg.get('anes'))                       # 전신마취 수술인지는 사례에 명시된 것만 본다
    surgstep = bool(tg.get('surg')) or ('surg' in ks)  # 이 단계에서 수술·시술을 받았는지
    icu = bool(tg.get('icu')) or ('icu' in ks)
    chemo = bool(tg.get('chemo')) or ('chemo' in ks)
    rad = bool(tg.get('rad')) or ('rad' in ks)
    thromb = ('thromb' in ks)
    rehab = ('rehab' in ks)
    regstep = surgstep or thromb                      # 뇌·심장 산정특례 등록 사유(수술 또는 혈전용해)
    got = []
    for it in items:
        lb = re.sub(r'\s', '', it['label'])
        amt = it['amt']
        if amt <= 0: continue
        hit = False
        if it['grp'] == '산정특례':
            if '유사암' in lb and '제외' not in lb: hit = bool(dx) and (dc in ('cis', 'thy', 'skin'))
            elif '암(' in lb or lb.startswith('중증질환자(암'): hit = bool(dx) and (dc == 'major')
            elif '뇌·수막' in lb or '뇌·수막의양성신생물' in lb: hit = bool(dx) and bool(re.match(r'^D3[23]', code))
            elif '뇌혈관' in lb: hit = brain and regstep       # 수술 또는 혈전용해로 등록(별표88-2 M6599)
            elif '심장' in lb: hit = heart and regstep         # 수술 또는 혈전용해제 투여로 등록(별표89-2·89-3)
            else: hit = False                          # 희귀·중증난치·중증화상·중증외상 — 사례로 단정하지 않는다
        elif '전신마취' in lb:
            hit = anes and ('시간이상' not in lb)
        elif '중환자실' in lb:
            hit = icu
        elif '항암방사선' in lb:
            hit = rad and _ls_cancer_row(lb, dc)
        elif '항암약물' in lb:
            hit = chemo and _ls_cancer_row(lb, dc)
        elif '혈전용해' in lb:
            hit = thromb
        elif '재활' in lb:
            hit = rehab and '전문재활' in lb and '전문외' not in lb and '외래' not in lb
        if hit: got.append((it['label'], amt, it['grp']))
    tot = sum(a for _l, a, _g in got)
    if tot <= r['man']: return got, False
    # 월간 총 지급금액 한도 — 한 달에 받는 합계는 가입금액까지
    out, left = [], r['man']
    for l, a, g in sorted(got, key=lambda x: -x[1]):
        if left <= 0: break
        out.append((l, min(a, left), g)); left -= min(a, left)
    return out, True

def _ls_cancer_row(lb, dc):
    """'암(유사암제외) 항암…' / '유사암 항암…' 행 가리기"""
    if lb.startswith('유사암'): return dc in ('cis', 'thy', 'skin')
    if '암(유사암제외)' in lb: return dc == 'major'
    return dc is not None

ISSUES = []                                           # 미분류·검토필요 로그(운영 점검용)
def log(kind, name, reason):
    it = {'구분': kind, '담보': name, '사유': reason}
    if it not in ISSUES: ISSUES.append(it)

_CC = {}
_XSUB = re.compile(r'\[[^\]]*(진단비|치료비|수술비|입원일당|통원일당)[^\]]*\]')
_SUBN = re.compile(r'\[([^\[\]]+)\]$')


def _rule_for(nm):
    for r in RULES:
        if not r['_m'].search(nm): continue
        if r['_x'] and r['_x'].search(nm): continue
        # 부모 담보명에 '사망·후유장해'가 섞여 있어도 세부급부가 진단비·치료비 등 계산 대상이면
        # 사망·후유장해 규칙을 건너뛴다 — 예) 암후유장해및진단비[암진단비(유사암제외)] (v8.8)
        if r['kind'] == 'life' and _XSUB.search(nm): continue
        return r
    return None


def classify(name):
    """담보명 → 규칙(rules.json). 없으면 None.

    세부급부가 있는 담보(부모[세부])는 **세부급부가 보상 유형을 정한다**(v8.23).
    '암치료,후유장해및진단비[표적항암약물허가치료비…]' 처럼 부모 이름만 보면 진단비로 읽히지만
    실제 지급 대상은 세부급부(치료비)다. 부모 이름만 보고 단정하지 않는다.
    다만 부모 규칙이 세부급부명으로 암종·치료를 다시 읽는 구조(by_benefit)면 부모를 그대로 둔다.
    """
    nm = nname(name)
    if nm in _CC: return _CC[nm]
    hit = _rule_for(nm)
    m = _SUBN.search(nm)
    if m:
        sub = _rule_for(m.group(1))
        if sub and (hit is None or (not (hit.get('opt') or {}).get('by_benefit') and sub['kind'] != hit['kind'])):
            hit = sub
    _CC[nm] = hit
    return hit

# ══ 담보명 토큰 ════════════════════════════════════════════════════
HOSP = [('상급종합병원', '상급종합'), ('요양병원', '요양'), ('종합병원', '종합')]
def tokens(nm):
    t = {}
    t['cause'] = '상해' if ('상해' in nm or '재해' in nm) else ('질병' if '질병' in nm else None)
    t['ex_hosp'] = '요양' if '요양병원제외' in nm else None            # '(요양병원제외)' 는 요양병원 입원을 빼는 조건이지 요양병원 요구가 아니다(v8.12)
    _nm = nm.replace('요양병원제외', '')
    t['hosp'] = next((v for k, v in HOSP if k in _nm), None)
    t['room'] = '1인실' if ('1인실' in nm and '2-3인실' not in nm) else ('2-3인실' if '2-3인실' in nm else None)
    m = re.search(r'(\d+)일한도', nm);        t['limit'] = int(m.group(1)) if m else None
    m = re.search(r'\((\d+)일이상', nm);      t['minday'] = int(m.group(1)) if m else None
    m = re.search(r'[\[(](상해|질병)?(\d)종[,\])]', nm)
    t['gkind'] = m.group(1) if m else None;   t['gj'] = int(m.group(2)) if m else None
    t['icu'] = '중환자실' in nm
    t['visit'] = '통원' in nm
    t['plus'] = '(plus)' in nm
    t['ex'] = re.findall(r'특정(\d)대질병제외', nm)
    return t

# ══ KCD 판정 ═══════════════════════════════════════════════════════

HRANK = {'의원': 0, '병원': 1, '종합': 2, '상급종합': 3}
def hosp_ok(need, have):
    """담보가 요구하는 병원 종별(need)을 사례의 병원(have)이 충족하는지.
       상급종합병원 = 종합병원 중에서 보건복지부장관이 지정 → 종합병원 조건도 함께 충족한다."""
    if not need: return True
    if need == '요양' or have == '요양': return need == have
    if have in (None, '모든'): return False
    return HRANK.get(have, 0) >= HRANK.get(need, 0)

def is_cancer(kcd):
    """암·유사암(제자리암 포함) 여부 — 131/130대질병수술비 등 일반 질병 담보 대상에서 제외"""
    return bool(itc.cancer_cls(kcd))

RNG = re.compile(r'^([A-Z])(\d{2})~([A-Z])(\d{2})$')
def code_hit(codes, kcd):
    """약관 KCD 목록(개별코드·세분류·범위표기 A15~A19·제외표기 !N74.0 모두 지원) 대조"""
    if not codes: return False
    c3 = kcd.split('.')[0]
    m3 = re.match(r'^([A-Z])(\d{2})', c3)
    for e in codes:                                   # 제외 코드가 먼저 (v8.6 : 131대질병 그룹표 '(N74.0제외)' 등)
        if e.startswith('!'):
            x = e[1:].strip()
            if kcd == x or kcd.startswith(x + '.') or (len(x) == 3 and c3 == x): return False
    for e in codes:
        e = e.strip()
        if e.startswith('!'): continue
        if kcd == e or kcd.startswith(e + '.') or c3 == e or e.startswith(kcd + '.'): return True
        r = RNG.match(e)
        if r and m3 and r.group(1) == m3.group(1) == r.group(3) and int(r.group(2)) <= int(m3.group(2)) <= int(r.group(4)):
            return True
    return False

def excluded(r, kcd):
    """특약 마스터의 제외코드(x : 보상하지 않는 질병 — 질병수술비의 치핵·비만·정신질환·선천기형 등)에 해당하면 True (v8.7)"""
    ex = r.get('excl') or []
    return bool(ex) and code_hit(ex, kcd)

_p13 = os.path.join(BASE, 'cancer13.json')
C13 = json.load(open(_p13, encoding='utf-8')) if os.path.exists(_p13) else {'groups': {}, 'alias': {}}
_C13N = {re.sub(r'[\s()·,]|전이포함', '', k): v for k, v in C13['groups'].items()}
for _a, _t in (C13.get('alias') or {}).items():
    _C13N.setdefault(re.sub(r'[\s()·,]|전이포함', '', _a), C13['groups'][_t])
def c13_codes(name):
    """세부급부 암종명 → 약관 별표 「암종별(13종)통합암(전이포함)(유사암제외) 분류표」 질병코드"""
    return _C13N.get(re.sub(r'[\s()·,]|전이포함', '', name or ''))

def g131_key(label):
    l = re.sub(r'[\s․·,]', '', label or '')
    l = re.sub(r'다빈도\d+대질병', '다빈도64대질병', l)
    for k in G131:
        if re.sub(r'[\s․·,]', '', k) == l: return k
    return None

def _pn(s): return re.sub(r'[\s․·,]', '', s or '')
def grp_hit(nm, sc, r=None):
    """약관 KCD 목록이 없는 담보 : 사례가 선언한 질병군(grp)이 담보명·세부급부에 들어 있으면 대상으로 본다."""
    lab = _pn((r or {}).get('benefit') or (r or {}).get('sub') or '')
    for g in sc['tags'].get('grp') or []:
        g = _pn(g)
        if g and (g in _pn(nm) or g == lab): return True
    return False

DXFAM = {'cancer': '암', 'sim_cancer': '암', 'brain': '뇌', 'heart': '심장'}
def sub_ok(r, kcd):
    """세부급부/하위그룹 라벨이 뇌·심장 질병군을 가리키면 그 계열 코드에만 지급 (마스터가 뇌·심 코드를 한 목록에 묶어 둔 경우 대비)"""
    lab = ((r.get('sub') or '') + (r.get('benefit') or '') + r.get('name', '')).replace(' ', '')
    brain = any(k in lab for k in ('뇌졸중', '뇌혈관', '뇌출혈', '뇌경색'))
    heart = any(k in lab for k in ('심장질환', '허혈성', '심근경색', '협심증'))
    if brain and not heart: return kcd.startswith('I6') or kcd.startswith('G45')
    if heart and not brain: return kcd.startswith('I2') or kcd.startswith('I5') or kcd.startswith('I4')
    return True
def kcd_ok(mode, r, sc, nm, o=None):
    """mode : major / sim / major_or_sim / codes / g131 / group / hc / none
       o    : 규칙 opt — 'grp' 가 있으면 담보명에서 찾지 않고 그 그룹표를 쓴다(v8.25)"""
    kcd = sc['kcd']
    if mode in (None, 'none'): return True
    if mode == 'hc':                                        # 약관 별표의 진료행위(수가)코드 ∩ 사례 단계의 수가코드(v8.14)
        return bool(set(r.get('hc') or []) & set(sc['tags'].get('hc') or []))
    if mode == 'major': return itc.cancer_cls(kcd) == 'major'
    if mode == 'sim': return itc.cancer_cls(kcd) in ('cis', 'bord', 'thy', 'skin')
    if mode == 'major_or_sim': return bool(itc.cancer_cls(kcd))
    if mode == 'g131':
        key = g131_key(r.get('benefit') or r.get('sub') or '')
        if key: return code_hit(G131[key], kcd)
        return grp_hit(nm, sc, r)
    if mode == 'group':
        key = (o or {}).get('grp')                          # 규칙이 그룹표를 직접 지정한 경우
        if not key:
            # 담보명에 들어 있는 그룹명 중 가장 긴 것 — '10대특정암(전이포함)'이 '10대특정암'보다 우선(v8.8)
            _n = nm.replace(' ', '')
            key = max((g for g in KCDG if not g.startswith('_') and g.replace(' ', '') in _n), key=len, default=None)   # 그룹명 띄어쓰기 무시(v8.12)
        lst = KCDG.get(key) if key else None
        if not lst:
            log('KCD없음', r['name'], f'{key or "세부급부"} 분류표가 규칙표에 없어 지급 판정 제외 (약관 별표 보강 필요)'); return False
        return code_hit(lst, kcd)
    if mode == 'codes':
        if not sub_ok(r, kcd): return False
        if r.get('codes'): return code_hit(r['codes'], kcd)
        if grp_hit(nm, sc, r): return True
        log('KCD없음', r['name'], '특약 마스터에 약관 KCD 목록이 없어 지급 판정 제외 (마스터 보강 필요)')
        return False
    return False

# ══ 구조별 지급 계산 ═══════════════════════════════════════════════
def _acts(sc, with_done=False):
    a = set(sc['tags'].get('acts') or [])
    if with_done: a |= set(sc['tags'].get('done') or [])
    for ev in sc.get('itc_events') or []:
        if len(ev) > 3: a.update(ev[3])
    if sc['tags'].get('surg'): a.add('surg')
    if 'immune' in a: a.add('target')      # 면역항암 치료 시 표적항암약물허가치료 합산(약관)
    return a

def h_dx(r, o, sc, nm, t):
    tg = sc['tags']
    dx = tg.get('dx')
    if not dx and o.get('cause') != '상해': return []
    if o.get('fam') and DXFAM.get(dx) not in o['fam']: return []
    if o.get('cause') and tg.get('cause') != o['cause']: return []
    if bool(tg.get('recur')) != (o.get('stage') == 'recur'): return []     # 재진단 단계에서는 재진단암 진단비만, 첫 진단 단계에서는 그 밖의 진단비만(v8.12)
    if not kcd_ok(o.get('kcd'), r, sc, nm, o): return []
    return [(r['man'], o.get('why', '진단확정'), o.get('group', '진단비'), o.get('freq', 'once'))]

def h_surg(r, o, sc, nm, t):
    tg = sc['tags']; j = tg.get('surg')
    if 'surg' not in _acts(sc): return []
    cause = t['cause'] or o.get('cause')
    if cause and tg.get('cause', '질병') != cause: return []
    if not hosp_ok(t['hosp'], tg.get('hosp')): return []
    if o.get('grade') == '1-5':
        if not t['gj']: return []
        if t['gkind'] and t['gkind'] != tg.get('cause', '질병'): return []
        j5 = surg5_grade(j, sc['kcd'])                   # 정수 또는 분류표 항목번호(v8.6)
        if j5 is None:
            log('검토필요', r['name'], '1-5종 수술분류표에 없는 항목 %s — 계산 제외' % j); return []
        if t['gj'] != j5: return []
        if o.get('plus') and tg.get('surg_cnt', 1) < 2: return []
    elif o.get('grade') == '1-7':
        g7 = surg7_grade(tg.get('surg7'))                # 정수 또는 분류표 수술코드(v8.5)
        if g7 is None:
            log('검토필요', r['name'], ('1-7종 수술분류표에 없는 수술코드 %s — 계산 제외' % tg.get('surg7')) if tg.get('surg7')
                else '1-7종 수술분류표 종 구분이 사례에 없어 계산 제외')
            return []
        if t['gj'] and t['gj'] != g7: return []
    elif not j: return []
    if 'cancer' in (o.get('ex') or []) and is_cancer(sc['kcd']): return []
    for g in t['ex']:                                   # 특정N대질병 제외 담보
        if g != '5': log('검토필요', r['name'], '특정%s대질병 제외목록 미확정 — 특정5대질병 기준으로 판정' % g)
        if tg.get('five_major') or code_hit(FIVE_MAJOR, sc['kcd']): return []
    if not kcd_ok(o.get('kcd'), r, sc, nm, o): return []
    why = o.get('why', '수술 1회').replace('{j}', str(t['gj'] or surg5_grade(j, sc['kcd']) or '')).replace(
        '{g}', (r.get('benefit') or r.get('sub') or '').strip())
    return [(r['man'], why, o.get('group', '수술비'), o.get('freq', 'each'))]

def h_day(r, o, sc, nm, t):
    tg = sc['tags']; mode = o.get('mode', 'day')
    if t['cause'] and tg.get('cause') != t['cause']: return []
    if t.get('ex_hosp') and tg.get('hosp') == t['ex_hosp']: return []
    if not hosp_ok(t['hosp'], tg.get('hosp')): return []
    if t['room'] and tg.get('room') != t['room']: return []
    if o.get('need_surg') and not tg.get('surg'): return []
    if not kcd_ok(o.get('kcd'), r, sc, nm, o): return []
    if mode == 'daycare':                                # 낮병동 입원(급여) 1일당 — 사례 태그 daycare 일수(v8.12)
        n = tg.get('daycare', 0)
        if not n: return []
        n = min(n, t['limit'] or n)
        return [(r['man'] * n, '낮병동 입원 %d일 × %d만원' % (n, r['man']), o.get('group', '입원일당'), 'each')]
    if mode == 'visit':
        n = tg.get('visits', 0)
        if not n: return []
        n = min(n, t['limit'] or n)
        return [(r['man'] * n, '통원 %d회 × %d만원' % (n, r['man']), o.get('group', '통원일당'), 'each')]
    if mode == 'icu' or t['icu']:
        d = tg.get('icu', 0)
        if not d: return []
        return [(r['man'] * d, '중환자실 %d일' % d, o.get('group', '입원일당'), 'each')]
    days = tg.get('days', 0)
    if not days: return []
    if t['minday'] and days < t['minday']: return []
    d = min(days, t['limit'] or days)
    if t['minday'] and t['minday'] > 1: d = max(0, min(days - t['minday'] + 1, t['limit'] or days))
    if not d: return []
    return [(r['man'] * d, '입원 %d일 × %d만원' % (d, r['man']), o.get('group', '입원일당'), 'each')]

def h_tx(r, o, sc, nm, t):
    tg = sc['tags']
    need = set(o.get('acts') or [])
    if o.get('by_benefit'):                                   # 세부급부명으로 치료행위·암종 결정 (26종 항암방사선및약물치료비 등)
        b = (r.get('benefit') or '')
        if not b: log('검토필요', r['name'], '세부급부(암종·치료)가 없는 부모 담보 — 계산 제외'); return []
        need = {'rad'} if '방사선' in b else ({'chemo'} if '약물' in b else need)
        inner = re.search(r'치료비\((.+)\)$', b)
        raw = inner.group(1) if inner else b
        codes = c13_codes(raw)                                    # 약관 별표 「암종별(13종)」 분류표 우선(v8.8)
        if not codes:                                             # 표에 없는 암종명은 기존 코드 사전으로 보조 판정
            kinds = re.split(r'과|및|,|·', re.sub(r'\(전이포함\)', '', raw))
            codes = [c for k in kinds for kk, cs in SYN.items() if kk == k.strip() for c in cs]
        if not codes:
            log('KCD없음', r['name'], f'세부급부 암종 "{raw}"이 약관 별표 「암종별(13종)」 분류표·코드 사전에 없어 계산 제외'); return []
        if not code_hit(codes, sc['kcd']): return []
    # 약관 별표 1-7종 수술분류표의 **수술구분**으로 가리는 담보(예 '뇌동맥류수술' = B011~B018).
    # 담보명·설명문에서 질병코드를 만들지 않고, 사례 단계에 적힌 수술코드가 그 구분에 드는지만 본다(v8.39).
    if o.get('surg7_grp') and surg7_group(tg.get('surg7')) != o['surg7_grp']: return []
    if need and not (need & _acts(sc)): return []
    allneed = set(o.get('acts_all') or [])          # 둘 다 받아야 지급되는 담보(예: 혈전용해 + 기계적혈전제거술)
    if allneed and not allneed <= _acts(sc, True): return []
    if o.get('need_cnt') and tg.get('tx_cnt', 0) < o['need_cnt']: return []
    nd = o.get('need_drug')
    m2 = re.search(r'[\[(](\d)종(?:및\d종)?이상', nm)                       # [1종이상]·(2종및3종이상) 담보명 표기 우선
    if m2: nd = int(m2.group(1))
    if nd and tg.get('drug', 0) < nd: return []                                 # 연간 약물종류 개수 조건
    if not need and not tg.get('dx') and o.get('kcd') != 'hc': return []     # 수가코드 담보는 진단 단계가 아니어도 해당 시술이 있으면 지급(v8.14)
    # 비급여(전액본인부담) 전용 담보는 그 치료의 비용이 비급여일 때만 지급한다(약관 '비급여(전액본인부담 포함)
    # ○○치료의 정의' — 진료비 세부내역서의 해당 비용이 비급여·전액본인부담인 경우). 급여 치료 예시에는 넣지 않는다.
    if re.search(r'비급여|전액본인부담', nm) and not tg.get('nc'): return []
    if t['cause'] and tg.get('cause') != t['cause']: return []
    if not hosp_ok(t['hosp'], tg.get('hosp')): return []
    if re.search(r'유사암|기타피부암|갑상선암', nm) and '제외' not in nm:        # 유사암 전용 치료비는 유사암에만
        if itc.cancer_cls(sc['kcd']) not in ('cis', 'bord', 'thy', 'skin'): return []
    if not kcd_ok(o.get('kcd'), r, sc, nm, o): return []
    freq = o.get('freq', 'year')
    if '계속받는' in nm or '연간1회한' in nm: freq = 'year'
    elif '최초1회한' in nm: freq = 'once'
    return [(r['man'], o.get('why', '약관 대상 치료'), o.get('group', '치료비'), freq)]

HANDLER = {'dx': h_dx, 'surg': h_surg, 'day': h_day, 'tx': h_tx}

# ══ 진입점 ═════════════════════════════════════════════════════════
def pay_lines(riders, sc):
    """riders : 설계 담보 목록(dict : name, man, cat, codes, benefit, sub, itc)
       sc     : {'kcd','tags',...}  →  [{'name','amt','why','group','no','freq'}]"""
    out = []
    sc.setdefault('itc_events', [])
    # 사례 단계가 비급여(전액본인부담)인지 태그로 옮긴다 — 지금까지는 통합치료비 엔진만 이 표시를 보고
    # 일반 치료비 담보는 못 봐서, '비급여 암 주요치료비'가 급여 치료 예시에도 더해지고 있었다(v8.27)
    if any((e[4] or {}).get('nc') for e in sc['itc_events'] if len(e) > 4):
        sc['tags'] = dict(sc['tags']); sc['tags']['nc'] = 1
    for r in riders:
        try:
            if (r.get('man') or 0) <= 0: continue
            n = r['name']; nm = nname(n)
            if excluded(r, sc['kcd']): continue         # 약관 제외코드(보상하지 않는 질병)에 해당 — 지급 없음(v8.7)
            # 1) 통합치료비 — 약관 지급금액표 엔진에 위임
            if r.get('itc'):
                if not sc.get('itc_events'): continue
                # 담보명이 원인을 못박은 통합치료비(질병 통합치료비·상해 통합치료비)는 그 원인일 때만(v8.27)
                _c = tokens(nm)['cause']
                if _c and sc['tags'].get('cause') != _c: continue
                try:
                    res = itc.calc_rider(r['itc'], r['man'], sc['kcd'], {'e': sc['itc_events']}, sc.get('within1y', False))
                except KeyError:
                    log('금액표없음', n, '가입금액 %s만원이 약관 지급금액표에 없어 계산 제외 (설계 금액 확인 필요)' % r['man'])
                    continue
                if res['total'] > 0:
                    det = ' · '.join('%s %s' % (itc.item_label(r['itc'], l['i']), format(l['amt'], ',.0f'))
                                     for l in res['lines'] if l['amt'] > 0)
                    ea = sum(l['amt'] for l in res['lines'] if l['amt'] > 0
                             and itc.IT[itc.RM[r['itc']]['ty']][l['i']]['p'] == 'o')
                    out.append({'name': n, 'amt': res['total'], 'why': det + ('  (연간 한도 적용)' if res['capped'] else ''),
                                'group': '통합치료비', 'no': r.get('no'), 'freq': 'year',
                                'each': min(ea, res['cap']), 'rule': 'itc', 'itc': r['itc']})
                continue
            # 2) 통합생활지원비 — 산정특례 등록·치료 항목마다 월 단위 지급(가입금액 = 월간 한도)
            if ls_id(n):
                lines, capped = ls_lines(r, sc)
                if lines:
                    _sp = sum(a for _l, a, g in lines if g == '산정특례')
                    out.append({'name': n, 'amt': sum(a for _l, a, _g in lines), 'group': '통합생활지원비',
                                'why': ' · '.join('%s %s' % (l, format(a, ',.0f')) for l, a, _g in lines)
                                       + ('  (월간 한도 적용)' if capped else ''),
                                'no': r.get('no'), 'freq': 'year', 'rule': 'ls_monthly',
                                # 산정특례는 '등록당' 지급 — 한 사례에서 두 단계에 걸쳐 세지 않도록 따로 싣는다
                                'sp': _sp, 'ls_rest': [(l, a) for l, a, g in lines if g != '산정특례']})
                continue
            # 3) 규칙표 판정
            rule = classify(n)
            if rule is None:
                log('미분류', n, '규칙표에 해당 담보 유형이 없어 계산 제외 (rules.json 보강 필요)')
                continue
            if rule['kind'] == 'itc_unknown':            # 금액표 미연동 통합치료비 — 정액 치료비로 오계산되지 않게 제외(v8.3)
                if nm not in INJ_KNOWN and noren(nm) not in INJ_KNOWN:
                    log('금액표없음', n, '약관 지급금액표(product_data.json RIDERS)에 없는 통합치료비 — 계산 제외 (금액표 보강 필요)')
                continue
            if rule['kind'] == 'skip' and (rule.get('opt') or {}).get('log'):
                log('조건부', n, rule['opt']['log']); continue   # 병기·상태 조건이 붙어 사례로 단정할 수 없는 담보(v8.21)
            h = HANDLER.get(rule['kind'])
            if h is None: continue                       # care·life·nonmed·skip = 사례 계산 대상 아님
            for amt, why, grp, freq in h(r, rule.get('opt') or {}, sc, nm, tokens(nm)):
                if amt > 0:
                    out.append({'name': n, 'amt': amt, 'why': why, 'group': grp, 'no': r.get('no'),
                                'freq': freq, 'rule': rule['id']})
        except Exception as ex:                          # 어떤 담보가 와도 생성이 중단되지 않게 한다
            log('오류', r.get('name', '?'), '%s: %s' % (type(ex).__name__, ex))
    return out

def total(lines): return sum(l['amt'] for l in lines)
def total_by(lines, mode):
    """mode: 'first' 최초 지급 / 'year' 반복(연간 1회) / 'each' 수술할 때마다"""
    s = 0
    for l in lines:
        if mode == 'first': s += l['amt']
        elif mode == 'year': s += l['amt'] if l.get('freq') != 'once' else 0
        else: s += l.get('each', l['amt'] if l.get('freq') == 'each' else 0)
    return s

def audit(riders):
    """설계 담보 전체를 규칙표에 대조한 결과 — 인계·운영 점검용"""
    by, un = {}, []
    for r in riders:
        if r.get('itc'):
            by['itc'] = by.get('itc', 0) + 1; continue
        rule = classify(r['name'])
        if rule is None:
            un.append(r['name']); by['미분류'] = by.get('미분류', 0) + 1
        else:
            by[rule['kind']] = by.get(rule['kind'], 0) + 1
    return {'담보수': len(riders), '구조별': by, '미분류': un, '규칙수': len(RULES)}
