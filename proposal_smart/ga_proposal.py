# -*- coding: utf-8 -*-
"""메리츠 GA 스마트 제안서(v5 양식) — 설계서 PDF 를 넣으면 GA 양식 PDF 를 만든다.

  python ga_proposal.py 설계서.pdf [결과.pdf] [나이]        # 한 건
  python ga_proposal.py 폴더                                 # 폴더 안 PDF 전부 → 폴더\ga_output\
  윈도우 : make_ga.bat 에 설계서 PDF 를 끌어다 놓는다(여러 개 가능). 그냥 실행하면 ga_input 폴더의 PDF 를 모두 만든다.

· 쪽 구성(GA 내부 회의 목업 2026-10-08) : 표지(탑재상품) · 1 보장요약(암 · 뇌심 · 주요수술 10 · 간병인) · 2 암보장 · 3 뇌·심보장 ·
  4~ 예상 보장금액 세부내역(= 합산 계산서 · 최소 3쪽 · 반드시 붙는다 — CALC_PAGES)
· 칸의 정의(사례 · 집계 방식 · 표시 조건)는 전부 ga_spec.CELLS 에 있고, 이 파일은 그 값을 꺼내 그리기만 한다(지면 = 사양).
· 금액은 전부 계산 엔진(scen_engine.pay_lines)에 이 설계서의 가입 특약을 넣어 얻는다. 사례 조건(질병코드·수술 분류·병원 종별·
  마취시간·약물 종수)은 가정값이다. 코드·금액을 여기서 만들지 않는다(CLAUDE.md 1·2). 간병인 칸만 설계서 가입금액을 그대로 읽는다(ga_care).
· 캐릭터는 GA 가안 이미지에서 잘라 넣었다(ga_assets). 사내 테스트용.
"""
import os, sys, re, base64, glob, json, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pipeline, build_all as BA, scen_engine as S, ga_spec as GS, ga_care as CARE          # noqa: E402

VERSION = (re.search(r"VERSION\s*=\s*'([^']+)'", open(os.path.join(BASE, 'api.py'), encoding='utf-8').read()) or [None, ''])[1]
BRAND = '메리츠 스마트 제안서'          # 「당사만의 고유명칭」 자리 — GA 가 정하면 여기만 바꾼다(미정 2026-10-08)
won = CARE.won
# 표지 「탑재상품」(GA 명칭 그대로 · GA 메모 2026-10-08) — 설계서 상품명을 읽는 규칙이지 화이트리스트가 아니다(목록 밖 상품도 그대로 만든다 · CLAUDE.md 4)
GA_PRODUCTS = [('(무)메리츠The건강한내Mom대로5.10.5보장보험', r'The건강한\s*내Mom대로\s*5\.10\.5'),
               ('(무)메리츠The건강한5.10.5보장보험', r'The건강한\s*5\.10\.5'),
               ('(무)알파Plus보장보험', r'(?<!The좋은)\s*(알파\s*Plus|케어프리보험\s*M-?\s*Basket)'),          # 알파Plus = 케어프리 M-Basket(GA 명칭이 다를 뿐 같은 상품 · 소유자 2026-10-08)
               ('(무)메리츠The좋은알파Plus보장보험', r'The좋은\s*(알파|케어프리)'),
               ('(무)내Mom같은어린이보험(태아전용포함)', r'내Mom같은'),
               ('(무)내Mom대로보장보험', r'^(?!.*(The좋은|5\.10\.5)).*내Mom대로\s*보장보험'),
               ('(무)메리츠The좋은내Mom대로보장보험2607', r'The좋은\s*내Mom대로'),
               ('(무)메리츠통합간편건강보험(연,세만기형)', r'^(?!.*355).*통합간편건강보험'),
               ('(무)메리츠통합간편건강보험(연,세만기형)2607(355입원,수술고지간편심사형)', r'통합간편건강보험.*355'),
               ('(무)The가벼운간편355건강보험(세만기형)', r'가벼운\s*간편\s*355'),
               ('(무)메리츠간편31건강보험2607', r'간편\s*31'),
               ('(무)메리츠또걸려도또받는암보험(연,세만기형)', r'또\s*걸려도\s*또\s*받는\s*암보험'),
               ('(무)메리츠또걸려도또받는간편한암보험(연,세만기형)', r'또\s*걸려도\s*또\s*받는\s*간편한\s*암보험')]
def ga_product_idx(product):
    p = re.sub(r'\s+', '', product or '')
    hits = [i for i, (_, pat) in enumerate(GA_PRODUCTS) if re.search(pat.replace(r'\s*', ''), p)]
    if not hits: return None
    # 더 구체적인 이름(긴 패턴)이 이기도록 — The건강한내Mom대로5.10.5 는 The건강한5.10.5 에도 걸린다
    return max(hits, key=lambda i: len(GA_PRODUCTS[i][1]))

# ───────── 설계서 읽기 + 공통 계산(한 건마다 load() 가 다시 채운다) ─────────
RID, META, WHO, PRODUCT, PREMIUM, NRID, SHORTP = [], {}, '', '', '', 0, ''
VAL = {}                                        # 칸 key → (값, 지급 줄, 로그)  — ga_spec.cell_value
AUDIT = {}                                      # 마지막 build 의 감사 로그(요약·계산 제외 사유) — 웹 화면 「감사 로그」 탭
def load(design_pdf, age=''):
    """설계서 한 건을 읽어 모든 칸 값을 채운다"""
    global RID, META, WHO, PRODUCT, PREMIUM, NRID, SHORTP, VAL
    S.ISSUES.clear(); GS.clear_cache()
    RID = pipeline.read_riders(design_pdf)
    META = BA.auto_meta(design_pdf)
    sex = META.get('sex') or ''
    # 나이는 설계서 본문에서 추정하지 않는다(만기·갱신 나이가 섞여 잘못 읽힘) — 넘겨받은 값만 쓴다
    WHO = '고객님 (%s%s)' % ({'F': '여', 'M': '남'}.get(sex, ''), (' · ' + age) if age else '')
    PRODUCT = re.sub(r'\s+', ' ', META.get('product', '') or '').replace('( ', '(').strip()
    PREMIUM = META.get('premium', '') or ''
    NRID = len(RID)
    SHORTP = (re.split(r'보장보험|건강보험|암보험', PRODUCT)[0].replace('(무) 메리츠 ', '').replace('(무)메리츠', '').strip() or PRODUCT).replace('%', '%%')
    VAL = {c['key']: GS.cell_value(c, RID) for c in GS.CELLS}
def V(key): return VAL[key][0]
def L(key): return VAL[key][1]
def F(lines): return int(round(S.total_by(lines, 'first')))

def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
CH = {k: b64(os.path.join(BASE, 'ga_assets', 'char_%s.png' % k)) for k in ('p1', 'p4', 'p5')}

def M(v, big=False):
    """칸 값 표시 — 숫자(만원) · None(미가입) · '보내줌' · '면책'"""
    if v is None: return '<span class="na">미가입</span>'
    if isinstance(v, str): return '<span class="txt">%s</span>' % v if v == '보내줌' else '<span class="na">%s</span>' % v
    return '<b class="v%s%s">%s<i>만원</i></b>' % (' z' if abs(v) < 1e-9 else '', ' big' if big else '', won(v))
def _ns(x): return re.sub(r'\s+', '', x or '')

# ───────── 조각 ─────────
def hl(t): return '<h2><span>%s</span></h2>' % t
def hd(title, char='p1'):
    return '<div class="hd"><span class="brand">%s</span><span class="bar"></span><span class="ttl">%s</span></div><img class="char" src="%s">' % (BRAND, title, CH[char])
def kv(cols):
    """cols : (머리, [(표시이름, 칸 key), ...]) — 줄 i 마다 열을 가로지르며 그린다(ga_spec 칸 순서와 같다)"""
    n = max(len(r) for _, r in cols)
    th = ''.join('<th>%s</th>' % h for h, _ in cols)
    trs = ''
    for i in range(n):
        trs += '<tr>' + ''.join(('<td><span>%s</span>%s</td>' % (r[i][0], M(V(r[i][1])))) if i < len(r) else '<td></td>' for _, r in cols) + '</tr>'
    return '<table class="kv"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (th, trs)
def grid(head, rows, cls='g'):
    th = ''.join('<th>%s</th>' % h for h in head)
    trs = ''.join('<tr>' + ''.join(('<td class="lab">%s</td>' if i == 0 else '<td>%s</td>') % c for i, c in enumerate(r)) + '</tr>' for r in rows)
    return '<table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (cls, th, trs)
def foot():
    return ('<div class="ft">사내 비교용 · GA 스마트 제안서 양식(2026-10-08 목업)에 메리츠 설계서(%s · %s · 담보 %d건 · %s)를 넣은 것 · 금액은 메리츠 스마트 제안서 계산 엔진(%s) 계산값 · '
            '병원 종별 · 마취시간 · 연간 약물 종수는 가정값 · 감액기간·면책기간 미반영 · 실제 지급은 약관과 심사 기준에 따름</div>'
            % (SHORTP, WHO, NRID, PREMIUM, VERSION))

# ───────── 표지 ─────────
def p0():
    idx = ga_product_idx(PRODUCT)
    lis = ''.join('<li%s>%s</li>' % (' class="on"' if i == idx else '', n) for i, (n, _) in enumerate(GA_PRODUCTS))
    box = ('<div class="cv-box"><b>이 제안서가 분석한 가입설계서</b><div>%s</div><div>%s · 월 보험료 %s · 가입 담보 %d건 · 작성 %s</div>%s</div>'
           % (PRODUCT, WHO, PREMIUM or '-', NRID, time.strftime('%Y-%m-%d'), '' if idx is not None else '<div class="warn">탑재상품 목록에 없는 상품 — 그대로 계산했습니다(목록은 표시용)</div>'))
    body = ('<div class="cv-brand">meritz</div><h1 class="cv-title">메리츠<br>스마트 제안서</h1>'
            '<div class="cv-prod"><h3>※탑재상품</h3><ul>%s</ul></div>%s<div class="cv-ga">GA지원센터</div>' % (lis, box))
    return '<div class="page cover">%s%s</div>' % (body, foot())

# ───────── 1쪽 보장요약 ─────────
LBL = {'표적(면역) 2가지 약물': '표적(면역)<br>2가지약물', '혈전용해+혈전제거': '혈전용해+<br>혈전제거', '복강경/흉강경': '복강경/<br>흉강경'}   # 칸 이름 표시용 줄바꿈(사양의 이름은 그대로)
EXL = {'특정단일유전자': '특정<br>단일유전자', '특정생검조직': '특정<br>생검조직', '특정NGS유전자': '특정<br>NGS유전자', '면역항암약물(카티포함)': '면역항암약물<br>(카티포함)'}
def dem_of(key):
    rs = L(key); return '<small class="dem">치매한정</small>' if rs and all(l.get('dementia') for l in rs) else ''
def p1():
    cancer = kv([(h, [(LBL.get(n, n), 'p1.ca.' + k) for n, k, *_ in items]) for h, items in GS._ca1])
    bh = kv([(h, [(LBL.get(n, n), 'p1.bh.' + k) for n, k, *_ in items]) for h, items in GS._bh1])
    def cell(n):
        return '<td><b>%s</b><em>%s</em>%s</td>' % (n, GS.GA_DZ[n][0], M(V('p1.dz.' + n)))
    dz = '<table class="dz"><tr>%s</tr><tr>%s</tr></table>' % (''.join(cell(n) for n in GS.DZ_ORDER[:5]), ''.join(cell(n) for n in GS.DZ_ORDER[5:]))
    def cv(k, day=False):
        return ('<small class="d1">1일</small> ' if day and V(k) is not None else '') + M(V(k)) + dem_of(k)
    care = ('<table class="care"><tr><th colspan="2">간병인지원 <small>(현물지원)</small></th></tr>'
            '<tr><td>병·의원 <small>(요양병원제외)</small></td><td>%s</td></tr><tr><td>요양병원</td><td>%s</td></tr>'
            '<tr><td>간호간병통합서비스</td><td>%s</td></tr><tr><td>미사용시</td><td>%s</td></tr>'
            '<tr><th colspan="2">간병인사용 <small>(금액지원)</small></th></tr>'
            '<tr><td>간병인</td><td>%s</td></tr><tr><td>요양병원</td><td>%s</td></tr><tr><td>간호간병통합서비스</td><td>%s</td></tr></table>'
            % (cv('p1.care.hosp'), cv('p1.care.nh'), cv('p1.care.nurse', True), cv('p1.care.unused', True),
               cv('p1.care.use_gen', True), cv('p1.care.use_nh', True), cv('p1.care.use_nurse', True)))
    body = (hd('고객님의 보장요약') + hl('암보장') + cancer + hl('뇌·심보장') + bh
            + '<div class="two"><div class="l">' + hl('주요수술보장') + dz + '</div><div class="r">' + hl('간병인보장') + care + '</div></div>')
    return '<div class="page">%s%s</div>' % (body, foot())

# ───────── 2쪽 암보장 ─────────
def p2():
    ex = '<table class="g eight"><tr>%s</tr><tr>%s</tr></table>' % (''.join('<th>%s</th>' % EXL.get(n, n) for n, _ in GS.EX_CA), ''.join('<td>%s</td>' % M(V('p2.ex.' + k)) for _, k in GS.EX_CA))
    dxb = ('<div class="dxbig three"><div><span>일반암</span><em>위, 대장, 폐, 간, 뼈암 등</em>%s</div>'
           '<div><span>유사암</span><em>갑상선암, 기타피부암, 경계성종양, 제자리암</em>%s</div>'
           '<div><span>전이암</span><em>원발암에서 다른 부위로 전이</em>%s</div></div>'
           % (M(V('p2.dx.일반암'), True), M(V('p2.dx.유사암'), True), M(V('p2.dx.전이암'), True)))
    sg = grid([''] + [n for n, _ in GS.SG], [[rl] + [M(V('p2.sg.%s.%s' % (k, md))) for _, k in GS.SG] for rl, md in GS.ROWS3])
    cm = grid([''] + [EXL.get(n, n) for n, _ in GS.CM], [[rl] + [M(V('p2.cm.%s.%s' % (k, md))) for _, k in GS.CM] for rl, md in GS.ROWS3[:2]], 'g cm')
    side = ('<table class="g side"><thead><tr><th colspan="2">표적(면역)<br>개수별 항암약물</th></tr></thead>'
            '<tbody><tr><td class="lab">2가지약물</td><td>%s</td></tr><tr><td class="lab">3가지약물</td><td>%s</td></tr></tbody></table>' % (M(V('p2.cm.two')), M(V('p2.cm.two3'))))
    rd = grid([''] + [n for n, _ in GS.RD], [[rl] + [M(V('p2.rd.%s.%s' % (k, md))) for _, k in GS.RD] for rl, md in GS.ROWS3[:2]])
    rh = grid(['', '입원 재활', '외래 재활'], [['연 20회', M(V('p2.rh.in')), M(V('p2.rh.out'))]])
    body = (hd('암보장', 'p4') + hl('암검사(8종)') + ex + hl('암진단') + dxb + hl('암수술') + sg
            + hl('항암약물치료') + '<div class="two cmrow"><div class="l">' + cm + '</div><div class="r">' + side + '</div></div>'
            + hl('항암방사선치료') + rd
            + '<div class="two"><div class="l">' + hl('암재활치료') + rh + '</div><div class="r">' + hl('암후유장해')
            + '<div class="dxbig one"><div><span>3-100%% 암후유장해</span>%s</div></div></div></div>' % M(V('p2.dis')))
    return '<div class="page roomy">%s%s</div>' % (body, foot())

# ───────── 3쪽 뇌·심보장 ─────────
def p3():
    ex = '<table class="g eight three"><tr>%s</tr><tr>%s</tr></table>' % (''.join('<th>%s</th>' % n for n, _ in GS.EX_BH), ''.join('<td>%s</td>' % M(V('p3.ex.' + k)) for _, k in GS.EX_BH))
    sub = {'뇌혈관': '지주막하출혈, 뇌경색, 뇌혈관질환, 비파열 뇌동맥류 등', '뇌졸중': '지주막하출혈, 뇌경색 등', '허혈성심장': '급성심근경색, 협심증 등', '급성심근경색': '급성심근경색 등'}
    dxb = '<div class="dxbig four">%s</div>' % ''.join('<div><span>%s</span><em>%s</em>%s</div>' % (n, sub[n], M(V('p3.dx.' + n), True)) for n in ('뇌혈관', '뇌졸중', '허혈성심장', '급성심근경색'))
    bs, hs = GS.brain_steps('상급종합'), GS.heart_steps('상급종합')
    gb = grid([''] + [n.replace('+', '+<br>') for n, _ in bs], [[rl] + [M(V('p3.b%d.%s' % (i, md))) for i in range(4)] for rl, md in GS.ROWS3])
    gh = grid([''] + [n.replace('+', '+<br>') for n, _ in hs], [[rl] + [M(V('p3.h%d.%s' % (i, md))) for i in range(4)] for rl, md in GS.ROWS3])
    sev = grid([''] + [n for n, _ in GS.SEV], [['반복(연 1회)'] + [M(V('p3.sev.' + k)) for _, k in GS.SEV]])
    rh = grid(['', '입원 재활', '외래 재활'], [['연 15회', M(V('p3.rh.in')), M(V('p3.rh.out'))]])
    body = (hd('뇌·심보장', 'p5') + hl('뇌·심검사(3종)') + ex + hl('뇌·심진단') + dxb + hl('뇌질환 치료 및 수술') + gb + hl('심질환 치료 및 수술') + gh
            + hl('뇌·심 중증치료') + sev + '<div class="two"><div class="l">' + hl('뇌·심 재활치료') + rh + '</div><div class="r"></div></div>')
    return '<div class="page roomy">%s%s</div>' % (body, foot())

# ───────── 예상 보장금액 세부내역(합산 계산서 · 맨 뒤 · 반드시 붙는다) ─────────
def _man_of(name):
    """지급 줄 이름과 같은 설계 담보의 가입금액(만원) — 못 찾으면 None"""
    for r in RID:
        if _ns(r['name']) == _ns(name) or _ns(r['name']).replace('치매주요질환입원일당', '질병입원일당') == _ns(name):
            return r['man'] if r['man'] or '간병인지원' not in r['name'] else CARE.daily(r)   # 간병인지원 「간병인지원 또는 N만원」 — 금액란 숫자(현물 담보는 가입금액 0 으로 읽힘)
    return None
def _wn(v):
    """계산서용 숫자 — 1쪽 값 표시(b.v)와 다른 표기를 써서 지면 대조(ga_spec)가 칸 수를 잘못 세지 않게 한다"""
    return '<span class="cn">%s</span>' % (won(v) if not isinstance(v, str) else v)
def calc_row(c):
    """칸 하나 → (항목, 값, 특약 줄 html). 그 칸의 집계 방식으로 실제 합산된 줄만 적는다(줄마다 지급 조건을 작게)"""
    v, lines, _ = VAL[c['key']]
    if c['kind'] == 'engine':
        used = [(l, GS.counts(l, c['mode'])) for l in lines]; used = [(l, a) for l, a in used if a]
    else:
        used = [(l, l['amt']) for l in lines]
    lab = '%s · %s' % (c['row'], c['col']) if c['row'] else c['col']
    if v is None:
        body = '<span class="cnone">미가입 — %s</span>' % (c.get('note') or c.get('sc_name') or '해당 담보 없음')
    elif not used:
        body = '<span class="cnone">합산된 특약 없음(가입 담보 중 이 사례에 지급되는 것이 없음) — %s</span>' % (c.get('sc_name') or '')
    else:
        parts = []
        for l, a in used:
            m = _man_of(l['name'])
            parts.append('<div><span class="nm">%s<em>%s</em></span><span class="mn">%s</span><span class="am">%s</span></div>'
                         % (l['name'], (l.get('why') or ''), ('가입 ' + won(m)) if m is not None else '', won(a)))
        body = ''.join(parts)
    return (lab, v, body)
def calc_table(title, rows):
    trs = ''.join('<tr><td class="lab">%s</td><td class="sum">%s</td><td class="ls">%s</td></tr>' % (lab, _wn(v) if v is not None else '', body) for lab, v, body in rows)
    return hl(title) + ('<table class="calc"><thead><tr><th>칸</th><th>표시 금액(만원)</th><th>합산된 설계 특약 · 지급 조건 · 가입금액 · 지급액(만원)</th></tr></thead><tbody>%s</tbody></table>' % trs)
CALC_DESC = ('<p class="cdesc">보장요약 쪽 각 칸의 금액이 이 설계서의 어떤 특약을 더해 나온 것인지 적었습니다. 지급액은 사례 조건(질병코드 · 병원 종별 · 수술 분류 · 약물 종수)으로 계산 엔진이 낸 값이고, '
             '가입금액은 설계서 그대로입니다. 줄마다 작은 글씨는 지급 조건(최초 1회 · 연간 1회 · 산정특례 등록 등)입니다. 가입 후 1~2년의 감액기간·면책기간은 반영하지 않은 금액입니다(설계서 뒤쪽 안내사항 참조). '
             '표적·면역항암은 약물 1종(치료 1개)만 받은 것으로, 「표적(면역) 2가지 약물」은 표적+면역 2종(3종이상 담보 제외)으로 계산합니다. '
             '암보장·뇌·심보장 쪽의 「반복(연 1회)」·「수술할 때마다」 줄은 같은 특약 줄의 연간·1회당 금액입니다.</p>')
def calc_sections():
    C = GS.KEY
    def keys(ks): return [calc_row(C[k]) for k in ks]
    ca = ['p1.ca.' + k for _, items in GS._ca1 for _, k, *_ in items]
    bh = ['p1.bh.' + k for _, items in GS._bh1 for _, k, *_ in items]
    dz = ['p1.dz.' + n for n in GS.DZ_ORDER]
    care = ['p1.care.' + k for k in ('hosp', 'nh', 'nurse', 'unused', 'use_gen', 'use_nh', 'use_nurse')]
    p2x = ['p2.ex.' + k for _, k in GS.EX_CA] + ['p2.cm.two3', 'p2.rh.in', 'p2.dis']
    p3x = ['p3.ex.' + k for _, k in GS.EX_BH] + ['p3.b2.first', 'p3.b3.first', 'p3.h0.first', 'p3.h1.first', 'p3.h3.first', 'p3.rh.in']
    return [('보장요약 · 암보장', keys(ca)), ('보장요약 · 뇌·심보장', keys(bh)), ('보장요약 · 주요수술보장 (병원급 가정)', keys(dz)),
            ('보장요약 · 간병인보장 (계산 없이 설계서 금액 그대로)', keys(care)),
            ('암보장 쪽 · 보장요약에 없는 칸 (암검사 · 3가지약물 · 재활 · 후유장해)', keys(p2x)),
            ('뇌·심보장 쪽 · 보장요약에 없는 칸 (검사 · 코일색전술 · 개두 · 심장 혈전용해/혈전제거 · 개흉 · 재활)', keys(p3x))]

CALC_PAGES = 3      # 세부내역(합산 계산서) 최소 쪽수 — 고정 규칙(GA 확정 2026-10-02) : 보장요약의 금액 근거가 반드시 붙는다(담보가 많으면 쪽이 늘어난다)
CALC_BUDGET = 72    # 한 쪽에 들어가는 분량(단위 : 글줄 1 ≈ 3.4mm). 줄 수는 특약명+조건 글자 수로 어림한다(한 줄 약 52자). 넘치면 render 의 '이탈·겹침' 경고로 잡힌다
_LINE_CH = 52       # 세부내역 특약 칸 한 줄에 들어가는 글자 수(가정 · 6.9pt 나눔고딕 · 칸 폭 약 100mm)
def calc_units(row):
    lab, v, body = row
    import math
    n = 0.6                                       # 칸 머리·여백
    for m in re.finditer(r'<span class="nm">(.*?)<em>(.*?)</em></span>', body):
        txt = re.sub(r'<[^>]+>', '', m.group(1)); why = re.sub(r'<[^>]+>', '', m.group(2))
        n += max(1, math.ceil((len(txt) + 0.85 * len(why) + 2) / _LINE_CH))
    if '<span class="nm">' not in body: n += max(1, math.ceil(len(re.sub(r'<[^>]+>', '', body)) / 90))
    return n + 0.3 * max(0, math.ceil(len(lab) / 14) - 1)
def calc_paginate(sections, desc):
    """구역(제목, 줄들)을 순서대로 쪽에 담는다 — 한 쪽 분량(CALC_BUDGET)을 넘으면 다음 쪽으로 넘기고 구역 제목에 (이어서)를 붙인다"""
    pages, cur, used = [], [], 5 + 7
    for title, rows in sections:
        i = 0
        while i < len(rows):
            if used + 3 + calc_units(rows[i]) > CALC_BUDGET and cur:
                pages.append(cur); cur, used = [], 5
            chunk, u = [], 3
            while i < len(rows) and used + u + calc_units(rows[i]) <= CALC_BUDGET:
                u += calc_units(rows[i]); chunk.append(rows[i]); i += 1
            if not chunk:                       # 줄 하나가 한 쪽을 넘는 경우 — 그대로 싣고 경고에 맡긴다
                chunk = [rows[i]]; u += calc_units(rows[i]); i += 1
            cont = (cur and cur[-1][0].split(' (이어서')[0] == title) or (not cur and pages and pages[-1][-1][0].split(' (이어서')[0] == title)
            cur.append((title + (' (이어서)' if cont else ''), chunk)); used += u
    if cur: pages.append(cur)
    out = []
    for n, pg in enumerate(pages):
        body = hd('예상 보장금액 세부내역 %d/%d' % (n + 1, len(pages))) + (desc if n == 0 else '')
        body += ''.join(calc_table(t, rows) for t, rows in pg)
        out.append('<div class="page calcpg">%s%s</div>' % (body, foot()))
    return out

CSS = '''
@page{size:A4;margin:0} *{box-sizing:border-box} body{margin:0;font-family:"GANG","NanumGothic","Malgun Gothic",sans-serif;color:#111}
.page{width:210mm;height:297mm;padding:12mm 13mm 12mm 14mm;page-break-after:always;position:relative;overflow:hidden;background:#fff}
.hd{display:flex;align-items:center;gap:8pt;margin:0 0 10pt;height:26pt} .hd .brand{font-size:15pt;font-weight:900;letter-spacing:-.6pt;color:#111} .hd .bar{width:2.5pt;height:16pt;background:#E8352B;border-radius:1pt}
.hd .ttl{font-size:15pt;font-weight:900;letter-spacing:-.6pt;color:#111} .char{position:absolute;top:6mm;right:13mm;height:27mm}
h2{font-size:11.5pt;margin:9pt 0 5pt;display:inline-block;font-weight:900} h2 span{background:linear-gradient(transparent 40%,#FFE94D 40%);padding:0 4pt;border-radius:2pt}
table{border-collapse:collapse;width:100%;table-layout:fixed} th,td{font-size:9.4pt;padding:0 6pt;height:23pt;border-bottom:1px solid #D6D6D6;white-space:nowrap;overflow:hidden}
th{background:#E9E9E9;font-weight:800;color:#222;text-align:center;height:21pt} td{text-align:center} .g th{white-space:normal;line-height:1.2} .lab{text-align:left;color:#444;white-space:nowrap;font-size:9pt}
.g th:first-child{background:#fff} .g.cm th:first-child{width:18%} .eight th:first-child{background:#E9E9E9}
.roomy th,.roomy td{height:26pt} .roomy h2{margin:13pt 0 7pt} .roomy .eight th{height:30pt} .roomy .eight td{height:32pt} .roomy .dxbig div{min-height:52pt;padding:11pt 12pt}
.kv td{width:25%;text-align:left;border-right:1px solid #EEE} .kv td:last-child{border-right:0} .kv td span{display:inline-block;width:auto;max-width:60%;color:#333;font-size:8.6pt;white-space:normal;word-break:keep-all;line-height:1.1;vertical-align:middle;letter-spacing:-.2pt} .kv th{font-size:9.6pt;letter-spacing:-.3pt} .kv td b{float:right;font-size:10pt;line-height:22pt} .kv td b i{line-height:1} .kv td .na{float:right;line-height:22pt}
b.v{font-weight:900;color:#111;font-size:10.5pt;white-space:nowrap} b.v i{font-style:normal;font-weight:500;font-size:8pt;color:#666;margin-left:1pt}
b.v.z{color:#9A9A9A} b.v.big{font-size:17pt;color:#C12027} b.v.big i{font-size:9.5pt}
small{font-size:8pt;color:#555} .na{color:#999;font-size:9pt} .txt{font-weight:800;color:#C12027}
.two{display:flex;gap:14pt;align-items:flex-start} .two .l{flex:1} .two .r{width:31%} .two.cmrow{align-items:stretch;gap:10pt} .two.cmrow .r{width:24%}
.dz td{text-align:center;vertical-align:top;border:1px solid #D6D6D6;width:20%;padding:6pt 3pt;height:auto;white-space:normal} .dz td b{display:block;font-size:10pt;font-weight:900}
.dz td em{display:block;font-style:normal;color:#666;font-size:8pt;margin:3pt 0 6pt} .dz td b.v{display:inline}
.care th{text-align:left;background:#E9E9E9} .care th small{font-weight:700;color:#444;font-size:7.6pt} .care td{text-align:left;height:21pt;font-size:9pt} .care td:last-child{text-align:right} .care td small{font-size:7pt} .care small.d1{color:#777;margin-right:2pt}
.care small.dem{display:block;color:#C12027;font-weight:700;font-size:6.4pt;text-align:right;line-height:1}
.eight th{font-size:8.2pt;line-height:1.25;white-space:normal;height:28pt} .eight td{padding:0 2pt;height:28pt} .three th,.three td{width:33.3%}
.dxbig{display:flex;gap:10pt} .dxbig div{flex:1;background:#FBE9E9;padding:9pt 11pt;border-radius:3pt;min-height:46pt}
.dxbig span{font-weight:900;font-size:12pt;margin-right:6pt} .dxbig em{font-style:normal;color:#555;font-size:7.6pt;display:block;margin-top:2pt} .dxbig b.v{float:right;margin-top:-18pt} .dxbig.one div{background:#F2F2F2;min-height:0;white-space:nowrap} .dxbig.one b.v{margin-top:0} .dxbig.one span{font-size:11pt} .dxbig.one .na{float:right;line-height:1.6}
.dxbig.four div{padding:8pt 8pt} .dxbig.four span{font-size:11pt} .dxbig.four em{font-size:6.8pt;min-height:16pt} .dxbig.four b.v{float:none;display:block;text-align:right;margin-top:2pt;font-size:16pt}
.dxbig.three em{min-height:9pt} .dxbig.three b.v{float:none;display:block;text-align:right;margin-top:2pt} .dxbig.three .na,.dxbig.four .na{display:block;text-align:right;margin-top:6pt;font-size:11pt}
.side th{height:auto;padding:4pt 4pt;line-height:1.2} .side td{height:22pt;padding:0 4pt;text-align:right} .side td.lab{text-align:left;font-size:8.6pt;width:52%}
.ft{position:absolute;left:14mm;right:13mm;bottom:6mm;font-size:6.4pt;color:#888;border-top:1px solid #DDD;padding-top:3pt}
.cover{padding:16mm 16mm 14mm 18mm} .cv-brand{position:absolute;top:9mm;right:14mm;color:#E8352B;font-weight:900;font-size:14pt;letter-spacing:-.5pt;font-family:Arial,sans-serif}
.cv-title{font-size:46pt;line-height:1.1;font-weight:900;letter-spacing:-2pt;margin:40mm 0 0} .cv-prod{margin-top:40mm} .cv-prod h3{font-size:13pt;margin:0 0 6pt;font-weight:900}
.cv-prod ul{list-style:none;margin:0;padding:0;columns:1} .cv-prod li{font-size:9.6pt;line-height:1.75;color:#333} .cv-prod li.on{font-weight:900;color:#C12027} .cv-prod li.on:after{content:" ◀ 이 설계서";font-size:8pt;color:#C12027}
.cv-box{margin-top:10mm;background:#F6F6F6;border-radius:4pt;padding:8pt 11pt;font-size:8.6pt;color:#333;line-height:1.5} .cv-box b{display:block;font-size:9pt;margin-bottom:2pt} .cv-box .warn{color:#C12027;font-weight:700}
.cv-ga{position:absolute;right:16mm;bottom:17mm;font-size:12pt;font-weight:900}
.calcpg .hd{margin-bottom:4pt} .calcpg .cdesc{padding-right:26mm;min-height:17mm} .calcpg h2{display:block;max-width:150mm;white-space:normal} .calcpg .char{height:20mm;top:7mm} .calcpg .hd .brand,.calcpg .hd .ttl{font-size:13pt} .calcpg h2{font-size:9.6pt;margin:6pt 0 3pt} .cdesc{font-size:7.2pt;color:#555;margin:0 0 4pt;line-height:1.35}
.calc th{font-size:7.2pt;height:14pt;padding:0 4pt} .calc td{font-size:6.9pt;height:auto;padding:1.5pt 4pt;white-space:normal;vertical-align:top;border-bottom:1px solid #E2E2E2;line-height:1.28}
.calc th:nth-child(1){width:19%} .calc th:nth-child(2){width:9%} .calc td.lab{text-align:left;font-size:7.2pt;font-weight:800;color:#222} .calc td.sum{text-align:right} .calc td.ls{text-align:left}
.calc .cn{font-weight:900;font-size:8.4pt} .calc .cnone{color:#888}
.calc .ls div{display:flex;gap:4pt;align-items:baseline} .calc .nm{flex:1;min-width:0;white-space:normal;line-height:1.2} .calc .nm em{font-style:normal;color:#888;font-size:6pt;margin-left:3pt} .calc .mn{width:14%;color:#666;text-align:right;white-space:nowrap} .calc .am{width:9%;text-align:right;font-weight:800;white-space:nowrap}
'''

def _font_css():
    """ga_assets(없으면 assets)의 나눔고딕을 파일로 붙인다 — 둘 다 없으면 PC 글꼴(맑은 고딕)로 나온다"""
    import pathlib
    a = pathlib.Path(BASE, 'ga_assets')
    if not (a / 'NanumGothic-Regular.ttf').exists(): a = pathlib.Path(BASE, 'assets')
    css = ''
    for f, w in (('NanumGothic-Regular.ttf', 400), ('NanumGothic-Bold.ttf', 700), ('NanumGothic-ExtraBold.ttf', 800)):
        if (a / f).exists():
            css += "@font-face{font-family:GANG;src:url('%s');font-weight:%d}" % ((a / f).as_uri(), w)
    if (a / 'NanumGothic-ExtraBold.ttf').exists():
        css += "@font-face{font-family:GANG;src:url('%s');font-weight:900}" % (a / 'NanumGothic-ExtraBold.ttf').as_uri()
    return css

def html(design_pdf, age=''):
    load(design_pdf, age)
    calc = calc_paginate(calc_sections(), CALC_DESC)
    # 세부내역(계산서)은 선택이 아니다 — 못 만들면 지면 전체를 내지 않는다(금액의 근거가 빠진 제안서가 나가지 않게)
    if len(calc) < CALC_PAGES or any('class="page calcpg"' not in c for c in calc):
        raise RuntimeError('예상 보장금액 세부내역(합산 계산서)이 %d쪽 이상 만들어지지 않았습니다(%d쪽)' % (CALC_PAGES, len(calc)))
    pages = [p0(), p1(), p2(), p3()] + calc
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>' % (_font_css(), CSS, ''.join(pages))
FIXED_PAGES = 4     # 표지 · 보장요약 · 암보장 · 뇌·심보장 (그 뒤에 세부내역 CALC_PAGES 쪽 이상)

CHECK = """()=>{const o=[];document.querySelectorAll('.page').forEach((p,i)=>{const B=p.getBoundingClientRect();const ft=p.querySelector('.ft');const F=ft?ft.getBoundingClientRect():null;
 p.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(!r.width||!r.height)return;
  if(r.bottom>B.bottom+0.5||r.right>B.right+0.5) o.push('p'+(i+1)+' 이탈 '+(e.innerText||'').slice(0,20));
  else if(F&&!ft.contains(e)&&e!==ft&&!e.querySelector('.ft')&&r.bottom>F.top-1&&r.top<F.top) o.push('p'+(i+1)+' 겹침(하단 주석) '+(e.innerText||'').slice(0,20));});});
 return o.slice(0,20);}"""

def render(html_path, pdf_path):
    import pathlib
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 794, 'height': 1123})
        pg.goto(pathlib.Path(html_path).resolve().as_uri()); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        warn = pg.evaluate(CHECK)
        pg.pdf(path=pdf_path, prefer_css_page_size=True, print_background=True); b.close()
    return warn

def ascii_name(path):
    """산출물 파일명은 ASCII(CLAUDE.md 7) — 한글 파일명은 영문·숫자만 남기고, 없으면 design"""
    stem = os.path.splitext(os.path.basename(path))[0]
    a = re.sub(r'[^A-Za-z0-9_-]+', '_', stem).strip('_')
    if not re.search(r'[A-Za-z]', a):            # 한글 이름 → design_숫자 (원래 이름은 로그 첫 줄에 남는다)
        a = 'design' + ('_' + a if a else '')
    return a

def build(design_pdf, out_pdf=None, age='', keep_html=False):
    """설계서 한 건 → GA 제안서 PDF. 반환 (결과 PDF, 로그 파일, 레이아웃 경고)"""
    t0 = time.time()
    out_pdf = out_pdf or os.path.join(os.path.dirname(os.path.abspath(design_pdf)), 'ga_output', ascii_name(design_pdf) + '_GA.pdf')
    os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)
    h = html(design_pdf, age)
    hp = os.path.splitext(out_pdf)[0] + '.html'
    open(hp, 'w', encoding='utf-8').write(h)
    warn = render(hp, out_pdf)
    if not keep_html: os.remove(hp)
    rc = S.recog(RID)
    global AUDIT
    lg = [dict(구분=it['구분'], 담보=it['담보'], 사유=it['사유'], 담보목록=it.get('담보목록', [it['담보']])) for it in S.issues_grouped()]
    lg += [dict(구분='지면넘침', 담보='-', 사유=w, 담보목록=[]) for w in warn]
    AUDIT = {'요약': {'담보수': NRID, '마스터매칭': sum(1 for r in RID if r.get('matched')), '인식': {k: v for k, v in rc.items() if not k.endswith('목록')},
                    '계산제외목록': rc['계산제외목록'], '구조별': S.audit(RID)['구조별'], '생성쪽수': FIXED_PAGES + len(re.findall(r'class="page calcpg"', h)), '지면검사': warn,
                    '상품': PRODUCT, '보험료': PREMIUM, '계산엔진': VERSION, '처리시간': round(time.time() - t0, 1)},
             '로그': lg}
    log = os.path.splitext(out_pdf)[0] + '_log.txt'
    with open(log, 'w', encoding='utf-8') as f:
        f.write('원본 설계서 : %s\n상품 : %s\n보험료 : %s\n담보 %d건 · 인식 : 마스터 %d · 부모연결 %d · 규칙만 %d · 계산제외 %d\n계산 엔진 %s · %.1f초\n\n'
                % (os.path.basename(design_pdf), PRODUCT, PREMIUM, NRID, rc['마스터'], rc['부모연결'], rc['규칙만'], rc['계산제외'], VERSION, time.time() - t0))
        if rc['계산제외목록']: f.write('[계산제외 담보] ' + ' · '.join(rc['계산제외목록']) + '\n\n')
        f.write('[지면 경고] ' + (' / '.join(warn) if warn else '없음') + '\n\n[계산 로그 — 빈칸·0원의 이유]\n')
        for it in S.issues_grouped():
            f.write('- [%s] %s — %s\n' % (it['구분'], it['담보'], it['사유']))
    return out_pdf, log, warn

def main(argv):
    args = [a for a in argv if a.strip()]
    age = ''
    if args and re.fullmatch(r'\d{1,3}세?', args[-1]):
        age = args.pop(); age = age if age.endswith('세') else age + '세'
    if not args:
        args = [os.path.join(BASE, 'ga_input')]
    files = []
    for a in args:
        if os.path.isdir(a): files += sorted(glob.glob(os.path.join(a, '*.pdf')) + glob.glob(os.path.join(a, '*.PDF')))
        elif a.lower().endswith('.pdf'): files.append(a)
    out_pdf = None
    if len(args) == 2 and args[0].lower().endswith('.pdf') and args[1].lower().endswith('.pdf') and not os.path.exists(args[1]):
        files, out_pdf = [args[0]], args[1]
    if not files:
        print('설계서 PDF 가 없습니다. PDF 를 끌어다 놓거나 ga_input 폴더에 넣어 주세요.'); return 1
    ok = 0
    for i, f in enumerate(files, 1):
        print('[%d/%d] %s' % (i, len(files), os.path.basename(f)), flush=True)
        try:
            o = out_pdf or os.path.join(BASE, 'ga_output', ascii_name(f) + '_GA.pdf')
            if not out_pdf and os.path.exists(o):
                o = os.path.join(BASE, 'ga_output', '%s_GA_%s.pdf' % (ascii_name(f), time.strftime('%H%M%S')))
            pdf, log, warn = build(f, o, age)
            print('      → %s  (담보 %d건 · %s)%s' % (pdf, NRID, SHORTP.replace('%%', '%'), ('  ※ 지면 경고 %d건 — 로그 확인' % len(warn)) if warn else ''), flush=True)
            ok += 1
        except Exception as ex:
            print('      ! 만들지 못했습니다 : %s: %s' % (type(ex).__name__, ex), flush=True)
    print('\n완료 %d / %d건 · 결과 폴더 : %s' % (ok, len(files), os.path.join(BASE, 'ga_output') if not out_pdf else os.path.dirname(os.path.abspath(out_pdf))))
    return 0 if ok == len(files) else 2

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
