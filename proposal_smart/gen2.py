# -*- coding: utf-8 -*-
"""메리츠 상품설명서 부가 6쪽 — 질병 단위 구성 · 현대해상 스마트제안서 정보량 + 메리츠 사례 플로우."""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import scen_engine as S
A = os.path.join(BASE, 'assets') + '/'
ICONS = json.load(open(os.path.join(BASE, 'icons.json'), encoding='utf-8'))
K = {'ca': ('#FF6B6B', '#E03131', '#FFF0F0', '#FFE3E3'), 'cv': ('#4C6EF5', '#364FC7', '#EDF2FF', '#DBE4FF'),
     'pr': ('#12B886', '#087F5B', '#E6FCF5', '#C3FAE8'), 'ms': ('#F59F00', '#D9480F', '#FFF9DB', '#FFEC99'),
     'yr': ('#7950F2', '#5F3DC4', '#F3F0FF', '#E5DBFF'), 'pk': ('#F06595', '#C2255C', '#FFF0F6', '#FFDEEB')}
DRAW = {'robot': '<rect x="9" y="14" width="30" height="24" rx="7" fill="CC"/><circle cx="18" cy="25" r="3.6" fill="#fff"/><circle cx="30" cy="25" r="3.6" fill="#fff"/><path d="M19 32h10" stroke="#fff" stroke-width="3" stroke-linecap="round"/><path d="M24 6v7M5 24v6M43 24v6" stroke="CC" stroke-width="3.4" stroke-linecap="round"/><circle cx="24" cy="5" r="3" fill="CC"/>',
 'target': '<circle cx="24" cy="24" r="17" fill="none" stroke="CC" stroke-width="3.6"/><circle cx="24" cy="24" r="9" fill="none" stroke="CC" stroke-width="3.6"/><circle cx="24" cy="24" r="3.4" fill="CC"/>',
 'immune': '<path d="M24 6l14 5.6v11.2C38 32.6 32 39.9 24 42.5 16 39.9 10 32.6 10 22.8V11.6z" fill="CC"/><path d="M17.6 23.6l4.8 4.8 8.4-8.6" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>',
 'proton': '<path d="M24 4l3.6 10.8L38 11l-3.8 10.4L45 24l-10.8 2.6L38 37l-10.4-3.8L24 44l-2.6-10.8L11 37l3.8-10.4L4 24l10.8-3.6L11 11z" fill="CC"/>',
 'limit': '<rect x="9" y="6" width="30" height="36" rx="5" fill="CC"/><path d="M16 16h16M16 24h16M16 32h10" stroke="#fff" stroke-width="3" stroke-linecap="round"/>',
 'bulb': '<path d="M24 5c-7.7 0-14 6.1-14 13.6 0 5 2.6 8.6 5.2 11.4 1.6 1.7 2.4 3 2.6 4.6h12.4c.2-1.6 1-2.9 2.6-4.6C35.4 27.2 38 23.6 38 18.6 38 11.1 31.7 5 24 5z" fill="CC"/><rect x="18" y="37" width="12" height="4" rx="2" fill="CC"/><rect x="20" y="42" width="8" height="3.6" rx="1.8" fill="CC"/>',
 'wound': '<path d="M24 6c-6 8-11 13.6-11 20a11 11 0 0022 0c0-6.4-5-12-11-20z" fill="CC"/><path d="M14 40h20" stroke="CC" stroke-width="3.4" stroke-linecap="round"/>',
 'knife': '<path d="M6 40l9-9M15 31l14-14a3 3 0 014.2 4.2L19 35z" stroke="CC" stroke-width="3.4" fill="none" stroke-linecap="round"/><path d="M30 10l8 8" stroke="CC" stroke-width="3.4" stroke-linecap="round"/>',
 'drop2': '<path d="M24 5s9 10 9 16a9 9 0 11-18 0c0-6 9-16 9-16z" fill="CC"/>'}
def svg(k, c):
    s = ICONS[k] if k in ICONS else '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">%s</svg>' % DRAW[k]
    return s.replace('CC', c)
def e(k, c='#495057'): return f'<span class="e">{svg(k,c)}</span>'
def et(k, bg, sz=22, c='#E03131'):
    return f'<span class="et" style="width:{sz}pt;height:{sz}pt;background:{bg}"><span style="width:{sz*.66:.1f}pt;height:{sz*.66:.1f}pt">{svg(k,c)}</span></span>'
def man(m):
    m = round(m)
    if m >= 10000:
        a, b = divmod(m, 10000)
        return f'{a}억' + (f' {b:,}' if b else '')
    return f'{m:,}'
def won(m):
    """금액 + 단위 — 1억처럼 만원 자리가 0이면 '원', 아니면 '만원' (v8.20 : '1억만원' 표기 오류 수정)"""
    return man(m) + ('원' if m >= 10000 and m % 10000 == 0 else '만원')
def num(m):
    """숫자 + 작은 단위 (겉 span 없이) — 표·카드 안에서 단위만 작게 쓸 때"""
    return f'{man(m)}<small>{"원" if m >= 10000 and m % 10000 == 0 else "만원"}</small>'
def big(m, c='#E03131'):
    # 지급액이 없으면 숫자 0 대신 줄표 — 가입하지 않은 칸을 0원으로 인쇄하지 않는다(v8.20)
    if m <= 0: return '<span class="z">&mdash;</span>'
    return f'<span class="n2" style="color:{c}">{num(m)}</span>'

C = json.load(open(sys.argv[1], encoding='utf-8'))
RID = C['riders']; IA = C['insert_after']; NEW = 9; TOTAL = C['base_pages'] + NEW
V3 = C.get('verify3') or []      # 3차 안전장치 — 설계서 뒤쪽 「특약 안내사항」 표와 금액 대조 결과(v8.41)
def pno(o): return o if o <= IA else o + NEW

# ══ 보장 계열 판정 (v8.4) — 설계에 없는 계열의 지면·블록은 자동으로 빠진다 ══
ATTACH_KEYS = ('cancer', 'brain', 'heart', 'itc', 'ls')      # 이 중 하나도 없으면 스마트제안서를 붙이지 않는다(운전자·치아 등 단일상품)
def coverage_flags():
    F = dict(cancer=False, brain=False, heart=False, itc=False, ls=False, surg=False, inj_surg=False, day=False, care=False, inj=False, life=False, inj_itc=False, recur=False)
    BR = ('뇌혈관', '뇌졸중', '뇌출혈', '뇌경색', '뇌질환', '뇌종양'); HT = ('심장', '심근경색', '협심증', '허혈성', '순환계')
    for r in RID:
        rl = S.classify(r['name']); kind = rl['kind'] if rl else ''; rid = rl['id'] if rl else ''
        nm = S.nname(r['name']); tk = S.tokens(nm); itc = r.get('itc') or ''; cat = r.get('cat') or ''
        med = kind in ('dx', 'surg', 'tx', 'day')
        if itc: F['itc'] = True
        if S.ls_id(r['name']): F['ls'] = True
        if itc.startswith(('ca', 'pre')) or cat in ('cancer_dx', 'cancer_tx', 'cancer_etc') or (med and ('암' in nm or 'cancer' in rid)): F['cancer'] = True
        if itc in ('circ', 'circ_top', 'ms') or cat == 'brain' or (med and any(k in nm for k in BR)): F['brain'] = True
        if itc in ('circ', 'circ_top', 'ms') or cat == 'heart' or (med and any(k in nm for k in HT)): F['heart'] = True
        if kind == 'surg' and rid not in ('surg_cancer', 'surg_cancer_sim', 'surg_brain_heart', 'surg_injury_special'):
            F['inj_surg' if tk['cause'] == '상해' else 'surg'] = True          # 일반 수술비만(암·뇌심 전용은 해당 계열 지면에서)
        if kind == 'day' and rid in ('day_basic', 'day_icu', 'day_surg_stay', 'visit_basic'): F['day'] = True
        if kind == 'care': F['care'] = True
        if rid == 'dx_recur': F['recur'] = True                 # 재진단암·재발암 담보가 있으면 폐암 사례에 재진단 단계를 붙인다(v8.12)
        if kind == 'life': F['life'] = True
        if med and tk['cause'] == '상해': F['inj'] = True
        if kind == 'itc_unknown' and (nm in S.INJ_KNOWN or S.noren(nm) in S.INJ_KNOWN): F['inj_itc'] = True
    return F
F = coverage_flags()

# ── 계약 1년 이내 감액(v8.33) ────────────────────────────────────
# 설계서의 담보별 약관 요약 설명문에서 desc_engine 이 읽어 둔 값이다.
# **계산에는 넣지 않는다** — 예시는 1년이 지난 뒤 기준으로 두고, 금액 옆에 작은 글씨로만 알린다.
# 1년 이내 지급액까지 예시로 만들면 고객이 읽기에 너무 어렵기 때문이다.
CUT = {}
for _r in RID:
    _c = (_r.get('desc2') or {}).get('cut_1y')
    if _c and 0 < _c < 1:
        CUT[S.nname(_r['name'])] = _c
CUT90 = {}
for _r in RID:
    _c = (_r.get('desc2') or {}).get('cut_90d')
    if _c and 0 < _c < 1:
        CUT90[S.nname(_r['name'])] = _c
def cutmark(name, short=False):
    """담보명 → '1년 내 50%' 작은 글씨. 감액이 없으면 빈 문자열."""
    c = CUT.get(S.nname(name))
    if not c: return ''
    v = '%g%%' % (c * 100)
    return f'<em class="ct">{v if short else "1년내 " + v}</em>'

def insured_sex():
    """피보험자 성별 : 설계서에서 읽은 값(C['sex'])이 우선, 없으면 성별 전용 담보명으로 추정, 끝내 모르면 '' (성별 중립 사례 사용)"""
    s = (C.get('sex') or '').upper()
    if s in ('M', 'F'): return s
    names = ' '.join(r['name'] for r in RID)
    if re.search(r'유방|자궁|난소|여성', names) and not re.search(r'전립선|남성|고환', names): return 'F'
    if re.search(r'전립선|남성|고환', names) and not re.search(r'유방|자궁|난소|여성', names): return 'M'
    return ''
SEX = insured_sex()
# ── 차후 검토 대상 상품(v8.34) ───────────────────────────────────
# 상품·담보 구조가 이 생성기의 계산 전제와 다른 상품은 지면을 붙이지 않고 원본을 그대로 돌려준다.
# 목록은 규칙표(rules.json > exclude_products)에 있으므로 코드를 고치지 않고 늘릴 수 있다.
def excluded_product():
    nm = re.sub(r'\s+', '', C.get('product') or '')
    for x in S.RULEDOC.get('exclude_products', []):
        if nm and re.search(x['m'], nm):
            return x
    return None
EXCL = excluded_product()
ATTACH = (EXCL is None) and any(F[k] for k in ATTACH_KEYS)
def header():
    return f'''<div class="h-t">[고객용]가입제안서</div><div class="h-p">{C['product']}</div>
 <img class="h-logo" src="file://{A}logo.png"><div class="h-bar">{C['head']}</div>'''
def footer(n):
    return f'''<div class="disc">※ 예시 금액은 이해를 돕기 위한 것으로, 실제 지급 여부와 금액은 약관 및 심사 기준(진단서·진료비세부내역서의 수가코드 등)에 따라 달라질 수 있습니다. 세부 내용은 반드시 약관을 확인하시기 바랍니다.</div>
 <div class="f-box"><div class="f-l">영업담당자</div><div class="f-v">{C['agent']}</div><div class="f-l">발행정보</div><div class="f-d">{C['issued']}</div></div>
 <div class="f-cc">고객콜센터 1566-7711</div><div class="f-url">www.meritzfire.com</div><div class="f-pg">page : {n}/{TOTAL}</div>'''
def tabhd(no, k, title, note=''):
    m, d, t, tl = K[k]
    return f'<div class="tabhd"><span class="tno" style="background:{d}">{no}</span><b style="color:{d}">{title}</b><span class="tn2">{note}</span></div>'

def Q(kcd, tags, itc=None):
    return S.pay_lines(RID, {'kcd': kcd, 'tags': tags, 'itc_events': itc or []})
def T(L, mode='first'): return S.total_by(L, mode)
def nols(L):
    """진단비 칸에서 통합생활지원비를 뺀다 — 진단확정이 아니라 산정특례 등록·치료 때 나오는 돈이라
       '진단확정 시 N만원' 칸에 섞으면 진단비를 부풀려 보이게 한다(v8.37)"""
    return [x for x in L if x.get('group') != '통합생활지원비']

# ══ 매트릭스 헬퍼 : 열 = 치료, 행 = 최초/반복/매회 ══
def matrix(k, cols, rows=('최초 지급', '반복(연 1회)', '수술할 때마다'), modes=('first', 'year', 'each'), foot=''):
    m, d, t, tl = K[k]
    head = ''.join(f'<th>{et(c["ic"],tl,26,d) if c.get("ic") else ""}<b>{c["t"]}</b><span>{c["s"]}</span></th>' for c in cols)
    body = ''
    for rn, md in zip(rows, modes):
        cells = ''.join(f'<td>{big(T(c["L"], md), d if md=="first" else "#343A40")}</td>' for c in cols)
        body += f'<tr class="{"mhl" if md=="first" else ""}"><th class="rl">{rn}</th>{cells}</tr>'
    det = ''.join(f'<td class="dt">{c.get("d","")}</td>' for c in cols)
    return f'''<table class="mx"><thead><tr><th class="rl"></th>{head}</tr></thead><tbody>{body}
      <tr class="dtr"><th class="rl">주요 지급 담보</th>{det}</tr></tbody></table>{f'<div class="mnote">{foot}</div>' if foot else ''}'''
def disp(n):
    """표시용 담보명 — 1-7종 하위 행(┗ 수술비[질병1종])은 '1종(질병 1-7종)'으로"""
    m2 = re.search(r'수술비\[(상해|질병)(\d)종\]', n.replace(' ', ''))
    if m2 and '(1-5종)' not in n: return f'{m2.group(2)}종({m2.group(1)} 1-7종)'
    return n.replace('┗', '').strip()

def det(L, n=2):
    """금액 칸 아래 '어느 담보에서 나오는지' — 큰 것 n개만 적고 나머지는 '+N개 특약'으로 줄인다(v8.37)"""
    pos = [x for x in sorted(L, key=lambda y: -y['amt']) if x['amt'] > 0]
    if not pos: return '—'
    line = [f'{disp(x["name"])[:19]} {man(x["amt"])}{cutmark(x["name"], 1)}' for x in pos[:n]]
    if len(pos) > n: line.append(f'<i>+{len(pos)-n}개 특약 {man(sum(x["amt"] for x in pos[n:]))}</i>')
    return '<br>'.join(line)

ITCK = {'x': ['x_ct']}
# ── 암 ─────────────────────────────────────────────
def cancer_cells():
    base = dict(cause='질병', hosp='상급종합', room=None, days=0, grp=[])
    def s(kcd, dx, itc, **kw):
        tg = dict(base); tg['dx'] = None; tg.update(kw)     # 진단비는 1번 블록에 따로 표기 → 치료 시 순수 보장액만
        return Q(kcd, tg, itc)
    robot = s('C16', 'cancer', [['수술', '로봇수술', '', ['surg', 'robot'], {'nc': 1}]], surg='C1', surg7='G081')   # 1-5종 : 관혈적 악성신생물 근치수술(5종)   # 복강경 위아전절제술(6종)
    lap = s('C16', 'cancer', [['수술', '복강경', '', ['surg']]], surg='C1', surg7='G081')
    open_ = s('C16', 'cancer', [['수술', '개복', '', ['surg']]], surg='C1', surg7='G082')                        # 개복 위아전절제술(6종)
    endo = s('C16', 'cancer', [['수술', '내시경 절제', '', ['surg']]], surg='C2', surg7='G503')                  # 1-5종 : 내시경 악성신생물 수술(3종)                  # 위내시경 시술(1종)
    chemo = s('C16', 'cancer', [['항암', '항암약물(급여)', '', ['chemo']]], chemo=1)
    target1 = s('C16', 'cancer', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=1)
    target2 = s('C16', 'cancer', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=2)
    immune = s('C16', 'cancer', [['항암', '면역(비급여)', '', ['chemo', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=2)
    rad = s('C16', 'cancer', [['방사선', '항암방사선(급여)', '', ['rad']]])
    imrt = s('C16', 'cancer', [['방사선', '세기조절', '', ['rad', 'imrt']]])
    proton = s('C16', 'cancer', [['방사선', '양성자(비급여)', '', ['rad', 'proton'], {'nc': 1}]])
    carbon = s('C16', 'cancer', [['방사선', '중입자(비급여)', '', ['rad', 'carbon'], {'nc': 1}]])
    sim = s('C73', 'sim_cancer', [['수술', '갑상선 절제', '', ['surg']]], surg='C1', surg7='K064')              # 갑상선암도 악성신생물 근치수술(5종)              # 주요 갑상선 악성 종양 수술(4종)
    simrobot = s('C73', 'sim_cancer', [['수술', '로봇 갑상선 절제', '', ['surg', 'robot'], {'nc': 1}]], surg='C1', surg7='K064')
    return locals()

def cancer_tx_areas():
    """가입한 암 관련 통합치료비·치료비 특약이 실제로 보장하는 치료 영역을 문장으로"""
    areas = []
    def add(x):
        if x not in areas: areas.append(x)
    for r in RID:
        if r.get('itc') and r['itc'].startswith('ca'):
            for it in S.itc.IT[S.itc.RM[r['itc']]['ty']]:
                c = it.get('c', ''); l = it['l']
                if c == '검사': add('검사')
                elif '다빈치' in l: add('로봇수술')
                elif '표적' in l: add('표적항암')
                elif '면역' in l: add('면역항암')
                elif '양성자' in l: add('양성자')
                elif '세기조절' in l: add('세기조절')
                elif '수술' in l: add('수술')
                elif '방사선' in l: add('방사선')
                elif '약물' in l: add('항암약물')
                elif c == '통증완화' or '통증' in l: add('통증완화')
                elif '재활' in l: add('재활')
        else:
            rl = S.classify(r['name'])
            if rl and rl['kind'] == 'tx' and rl['id'].startswith('tx_'):
                n = r['name']
                if '표적항암' in n: add('표적항암약물허가치료비(2종~)')
                elif '면역항암' in n: add('면역항암약물허가치료비')
                elif '항암약물치료비' in n: add('항암약물치료비')
                elif '생활비' in n: add('통합치료 생활비')
    itc_a = [a for a in areas if '치료비' not in a and '생활비' not in a][:9]; tx_a = [a for a in areas if a not in itc_a][:3]
    return ('통합치료비 : ' + ' · '.join(itc_a) if itc_a else '') + ('<br>특약 : ' + ' · '.join(tx_a) if tx_a else '') or '치료비 특약 미가입'

def page_cancer():
    c = cancer_cells(); d = K['ca'][1]
    dxrow = [('일반암', '위·대장·폐·간암 등', 'cancer', 'C16'), ('유사암', '갑상선암·기타피부암·제자리암·경계성종양', 'sim_cancer', 'C73')]
    dxcells = ''
    for t, s2, dx, kcd in dxrow:
        L = nols(Q(kcd, dict(dx=dx, cause='질병', grp=[]), []))
        dxcells += f'<div class="dxc"><b>{t}</b><span>{s2}</span>{big(T(L),d)}<em>{det(L,2)}</em></div>'
    return f'''{tabhd(1,'ca','암 진단','암으로 진단확정되면 진단비가 최초 1회 지급돼요')}
 <div class="dxs">{dxcells}
   <div class="dxc alt"><b>치료비로 보장되는 치료 영역</b><span>가입한 특약 기준 · 진단금과 별개로 치료마다 지급</span><em class="areas">{cancer_tx_areas()}</em></div></div>
 {tabhd(2,'ca','암 수술 (신의료기술 포함)','진단금을 뺀 순수 수술 보장액 · 수술할 때마다 다시 받는 금액까지')}
 {matrix('ca',[{'ic':'magnifying_glass','t':'내시경 수술','s':'급여 적용 수술','L':c['endo'],'d':det(c['endo'])},
               {'ic':'surgical_sterilization','t':'개복 · 개흉 수술','s':'급여 적용 수술','L':c['open_'],'d':det(c['open_'])},
               {'ic':'ultrasound_scanner','t':'복강경 · 흉강경','s':'급여 적용 수술','L':c['lap'],'d':det(c['lap'])},
               {'ic':'robot','t':'다빈치 로봇수술','s':'비급여(전액본인부담)','L':c['robot'],'d':det(c['robot'])}],
        foot='※ 상급종합병원에서 수술한 경우의 예시 · 유사암(갑상선암·기타피부암·제자리암·경계성종양)은 암 진단비·131대질병수술비 대상이 아니며 유사암 금액이 별도 적용돼요.')}
 {tabhd(3,'pk','항암약물치료','표적·면역 등 고가 비급여 항암치료를 해마다 다시 보장')}
 {matrix('pk',[{'ic':'syringe','t':'화학항암약물','s':'급여 적용 치료','L':c['chemo'],'d':det(c['chemo'])},
               {'ic':'target','t':'표적항암 1종','s':'비급여 · 약물 1종만 사용','L':c['target1'],'d':det(c['target1'])},
               {'ic':'target','t':'표적항암 2종 이상','s':'비급여 · 연간 약물종류 2종~','L':c['target2'],'d':det(c['target2'])},
               {'ic':'immune','t':'면역항암 + 표적','s':'비급여 · 면역관문억제제 병용','L':c['immune'],'d':det(c['immune'])}],
        rows=('최초 지급','반복(연 1회)','수술할 때마다'),
        foot='' if len(RID) > 80 else '※ 표적항암약물허가치료비(2종 및 3종 이상)는 <b>연간 표적항암제 약물종류가 2종 이상</b>일 때 지급돼요. 1종만 쓰면 통합치료비 표적항암 항목만 지급되어 두 경우를 나눠 계산했어요(면역관문억제제는 약관상 표적항암제에 포함).')}
 {tabhd(4,'yr','항암방사선치료','정상 세포 손상을 줄이는 세기조절 · 양성자치료까지')}
 {matrix('yr',[{'ic':'xray','t':'항암방사선','s':'급여 적용 치료','L':c['rad'],'d':det(c['rad'])},
               {'ic':'radiology','t':'세기조절방사선','s':'급여 적용 치료','L':c['imrt'],'d':det(c['imrt'])},
               {'ic':'proton','t':'양성자치료','s':'비급여(전액본인부담)','L':c['proton'],'d':det(c['proton'])},
               {'ic':'machinery','t':'중입자치료','s':'비급여 · 양성자 항목 미해당 · 방사선 항목 지급','L':c['carbon'],'d':det(c['carbon'])}],
)}'''

# ── 뇌·심장 ────────────────────────────────────────
def page_cv():
    b = lambda kcd, dx, itc, **kw: Q(kcd, dict(dx=None, cause='질병', hosp=kw.pop('hosp', '종합'), room=None, days=0, grp=kw.pop('grp', []), **kw), itc)   # 진단비는 카드에 따로 → 치료 시 순수 보장액
    G = ['뇌혈관질환', '뇌졸중', '특정31대질병']; H = ['심장질환', '허혈성심장질환', '특정31대질병']
    rows = []
    for k, kcd, dx, grp, cols in [
        ('cv', 'I63', 'brain', G, [('혈전용해치료만', '혈전용해제(tPA) 주사 · 수술 없음', [['시술', '혈전용해', '', ['thromb']]], None, None, None),
                                   ('혈전용해 + 혈전제거술', '두 치료를 모두 받은 경우', [['시술', '혈전용해', '', ['thromb']], ['수술', '기계적 혈전제거술', '', ['surg']]], '88-1', ['thrombectomy'], 'B027'),
                                   ('경동맥 스텐트 삽입술', '신의료기술(비관혈)', [['시술', '스텐트 삽입', '', ['surg']]], '88-1', None, 'B026'),
                                   ('개두 수술', '클립결찰술 · 개두술', [['수술', '개두술', '', ['surg']]], '59', None, 'B031')]),
        ('yr', 'I21', 'heart', H, [('혈전용해치료만', '혈전용해제 주사 · 수술 없음', [['시술', '혈전용해', '', ['thromb']]], None, None, None),
                                   ('혈전용해 + 혈전제거술', '두 치료를 모두 받은 경우', [['시술', '혈전용해', '', ['thromb']], ['수술', '기계적 혈전제거술', '', ['surg']]], '88-1', ['thrombectomy'], 'F121'),
                                   ('관상동맥 스텐트', '경피적 시술도 수술', [['시술', '스텐트 삽입', '', ['surg']]], '88-1', None, 'F121'),
                                   ('심장 개흉수술', '관상동맥 우회술 · 에크모', [['수술', '개흉 수술', '', ['surg']], ['중환자', '에크모', '', ['ecmo']]], '24', None, 'F041')])]:
        d = K[k][1]
        cells = ''
        for t, s2, itc, j, ac, j7 in cols:
            ico = {'혈전용해치료만':'drop2','혈전용해 + 혈전제거술':'drop2','경동맥 스텐트 삽입술':'stent','개두 수술':'neuro_surgery','관상동맥 스텐트':'stent','심장 개흉수술':'heart_organ'}.get(t,'stethoscope')
            cells += f'<th>{et(ico,K[k][3],26,d)}<b>{t}</b><span>{s2}</span></th>'
        r1 = ''.join(f'<td>{big(T(b(kcd,dx,c[2],surg=c[3],grp=grp,hosp="모든",acts=c[4],surg7=c[5]),"first"),d)}</td>' for c in cols)
        r2 = ''.join(f'<td>{big(T(b(kcd,dx,c[2],surg=c[3],grp=grp,hosp="상급종합",acts=c[4],surg7=c[5]),"first"),d)}</td>' for c in cols)
        r3 = ''.join(f'<td>{big(T(b(kcd,dx,c[2],surg=c[3],grp=grp,hosp="상급종합",acts=c[4],surg7=c[5]),"each"),"#343A40")}</td>' for c in cols)
        r4 = ''.join(f'<td class="dt">{det(b(kcd,dx,c[2],surg=c[3],grp=grp,hosp="상급종합",acts=c[4],surg7=c[5]))}</td>' for c in cols)
        dx_amt = T(nols(Q(kcd, dict(dx=dx, cause='질병', grp=grp), [])), 'first')
        rows.append((k, kcd, dx, cells, r1, r2, r3, r4, dx_amt, cols, grp))
    def blk(x, no):
        k, kcd, dx, cells, r1, r2, r3, r4, dxa, cols, grp = x
        d = K[k][1]; nm = '뇌혈관 질환' if dx == 'brain' else '심혈관 질환'
        icon = 'neurology' if dx == 'brain' else 'heart_organ'
        dxl = nols(Q(kcd, dict(dx=dx, cause='질병', grp=grp)))
        return f'''{tabhd(no,k,nm+' 진단 · 치료','진단금은 최초 1회 · 치료 금액은 진단금을 뺀 순수 치료 보장액')}
     <div class="cvwrap"><div class="cvdx" style="background:{K[k][2]}">{et(icon,'#fff',26,d)}<b>{('뇌경색·뇌출혈 등' if dx=='brain' else '급성심근경색·협심증 등')}</b>
        <span>진단확정 시</span>{big(dxa,d) if dxa>0 else '<span class="nop">해당 진단비 미가입</span>'}<em>{det(dxl,2) if dxa>0 else '수술·치료 담보로 보장돼요'}</em></div>
      <table class="mx cvmx"><thead><tr><th class="rl"></th>{cells}</tr></thead><tbody>
        <tr><th class="rl">모든 병원</th>{r1}</tr>
        <tr class="mhl"><th class="rl">상급종합병원</th>{r2}</tr>
        <tr><th class="rl">수술할 때마다</th>{r3}</tr>
        <tr class="dtr"><th class="rl">주요 지급 담보<br><span>상급종합 기준</span></th>{r4}</tr></tbody></table></div>'''
    L = Q('I63', dict(dx='brain', cause='질병', hosp='종합', room='2-3인실', days=14, icu=3, grp=['뇌혈관질환']),
          [['중환자', '중환자실', '', ['icu']]])
    inp = [x for x in L if x['group'] in ('입원일당', '통합치료비')]
    blocks = [x for x in rows if (x[2] == 'brain' and F['brain']) or (x[2] == 'heart' and F['heart'])]   # 없는 계열 블록은 빠진다(v8.4)
    title = '뇌혈관 · 심혈관' if F['brain'] and F['heart'] else ('뇌혈관' if F['brain'] else '심혈관')
    return f'''<div class="lg">{e('heart_organ','#364FC7')}<b>{title} 보장</b><span class="sub">진단 · 수술 · 입원 — 병원 종별 비교</span></div>
 {''.join(blk(x, i + 1) for i, x in enumerate(blocks))}
 {tabhd(len(blocks)+1,'ms',title+' 질환은 이렇게 치료해요','실제 치료 순서와 그 단계에서 지급되는 담보')}
 <div class="txflow">{tx_flow()}</div>
 <div class="mnote">※ <b>특정혈전치료비</b>는 혈전용해치료와 급여 기계적혈전제거술을 <b>모두</b> 받은 때 연간 1회 지급(한 가지만 받으면 미지급) · 진단비 최초 1회 · 수술비 수술마다 · 통합치료비는 진단금과 별개로 치료 항목마다.</div>'''

TXFLOW = [
 ('cv', 'neurology', '뇌경색 (혈관이 막힘)', 'I63',
  [('xray', '응급 CT · MRI', '증상 4.5시간 안에 병원 도착이 관건', '검사'),
   ('drop2', '혈전용해제(tPA) 주사', '막힌 혈관을 약으로 녹여요', '혈전용해'),
   ('knife', '기계적 혈전제거술', '카테터로 혈전을 직접 꺼내요', '수술'),
   ('ambulance', '중환자실 · 입원', '뇌부종·출혈 감시', '입원'),
   ('physical_therapy', '재활치료', '마비·언어 회복 훈련', '재활')]),
 ('cv', 'neurology', '뇌출혈 (혈관이 터짐)', 'I61',
  [('xray', '응급 CT', '출혈 위치·크기 확인', '검사'),
   ('stent', '코일색전술 · 클립결찰술', '동맥류를 막아 재출혈 예방', '수술'),
   ('neuro_surgery', '개두 혈종제거술', '뇌압을 낮추는 개두 수술', '수술'),
   ('ambulance', '중환자실 · 입원', '뇌압·혈압 집중 관리', '입원'),
   ('physical_therapy', '재활치료', '운동·인지 재활', '재활')]),
 ('yr', 'heart_organ', '급성 심근경색 (혈관이 막힘)', 'I21',
  [('heart_cardiogram', '심전도 · 심장효소 검사', '가슴통증 후 골든타임 2시간', '검사'),
   ('stent', '관상동맥 스텐트(PCI)', '막힌 관상동맥을 넓혀요', '수술'),
   ('heart_organ', '관상동맥 우회술(CABG)', '여러 혈관이 막혔을 때 개흉 수술', '수술'),
   ('ambulance', '중환자실 · 입원', '부정맥·심부전 감시', '입원'),
   ('physical_therapy', '심장재활', '운동 처방 · 재발 예방', '재활')]),
]
def tx_flow():
    """뇌·심 질환별 표준 치료 흐름 — 각 단계에서 지급되는 담보를 실제 설계로 계산해 표시"""
    def pay(kcd, stage):
        base = dict(cause='질병', hosp='상급종합', room=None, days=0, grp=['뇌혈관질환' if kcd[1] == '6' else '심장질환', '특정31대질병'])
        if stage == '검사': return Q(kcd, dict(base, dx='brain' if kcd[1] == '6' else 'heart'), [['검사', '검사', '', ['x_ct', 'x_mri']]])
        if stage == '혈전용해': return Q(kcd, base, [['시술', '혈전용해', '', ['thromb']]])
        if stage == '수술': return Q(kcd, dict(base, surg=3), [['수술', '수술', '', ['surg']]])
        if stage == '입원': return Q(kcd, dict(base, room='2-3인실', days=14, icu=3), [['중환자', '중환자실', '', ['icu']]])
        if stage == '재활': return Q(kcd, base, [['재활', '재활', '', ['rehab'], {'n': 10}]])
        return []
    out = ''
    for k, ic, title, kcd, steps in TXFLOW:
        if not ((kcd.startswith('I6') and F['brain']) or (kcd.startswith('I2') and F['heart'])): continue   # 없는 계열 흐름은 빠진다(v8.4)
        d = K[k][1]; tl = K[k][3]
        chips = ''
        for sic, nm, desc, stage in steps:
            L = pay(kcd, stage)
            grp = sorted({x['group'] for x in L if x['amt'] > 0})
            tag = ' · '.join(g.replace('통합치료비', '통합치료').replace('입원일당', '입원') for g in grp) or '—'
            chips += f'<div class="txs">{et(sic, tl, 18, d)}<div><b>{nm}</b><span>{desc}</span></div><em style="color:{d}">{tag}</em></div>'
        out += f'<div class="txr" style="background:{K[k][2]}"><div class="txh">{et(ic,"#fff",20,d)}<b style="color:{d}">{title}</b><span>{kcd}</span></div><div class="txsteps">{chips}</div></div>'
    return out

def _day_riders(room, hosp, cause='질병'):
    """해당 병실·병원 종별 조건을 충족하는 입원일당 담보 목록 (상급종합 = 종합병원 담보도 포함)"""
    out = []
    for r in RID:
        rl = S.classify(r['name'])
        if not rl or rl['kind'] != 'day': continue
        tk = S.tokens(S.nname(r['name']))
        if tk['visit'] or tk['icu'] or (tk['minday'] or 0) > 1: continue
        if tk['cause'] != cause or tk['room'] != room: continue
        if not S.hosp_ok(tk['hosp'], hosp): continue
        out.append((r, tk))
    return out

NOP2 = '<span class="nop2">미가입</span>'        # f-string 안 백슬래시(3.12 전용 문법) 제거 — 3.10+ 호환(v8.3)
def stay_cards(days=14, kcd='I63'):
    """입원 · 중환자실 · 간병을 4열 × 2행에 균형있게. 담보가 없는 칸은 '미가입'으로 자리를 지킨다.
       병실·병원 종별·한도일수를 담보별로 각각 계산한다(상급종합병원은 종합병원 담보도 함께 지급)."""
    base = dict(cause='질병', grp=['뇌혈관질환'], room=None, days=0)
    cells = []
    def add(ic, k, t, s2, v, on=True): cells.append({'ic': ic, 'k': k, 't': t, 's': s2, 'v': v, 'on': on})
    # ① 병실·병원 무관 일반 입원일당 (v8.4 — 종전에는 그리드에 나타나지 않았다)
    gen = _day_riders(None, '모든')
    if gen:
        tot = 0; parts = []
        for r, tk in sorted(gen, key=lambda x: -x[0]['man']):
            d = min(days, tk['limit'] or days); tot += r['man'] * d; parts.append(f'{won(r["man"])}×{d}일')
        add('hospital', 'ms', '일반 입원 · 병실 무관', ' + '.join(parts), big(tot, K['ms'][1]), tot > 0)
    # ② 병실 종류 × 병원 종별 (한도일수 개별 적용)
    for room, hosp, label in [('1인실', '상급종합', '1인실 · 상급종합병원'), ('1인실', '종합', '1인실 · 종합병원'),
                              ('2-3인실', '상급종합', '2-3인실 · 상급종합병원'), ('2-3인실', '종합', '2-3인실 · 종합병원')]:
        rs = _day_riders(room, hosp)
        tot = 0; parts = []
        for r, tk in sorted(rs, key=lambda x: -x[0]['man']):
            d = min(days, tk['limit'] or days)
            tot += r['man'] * d
            parts.append(f'{won(r["man"])}×{d}일')
        add('hospital_symbol', 'ms', label, ' + '.join(parts) if parts else '해당 병실 담보 없음',
            big(tot, K['ms'][1]), tot > 0)
    # ②-1 상해 입원(2-3인실 · 종합병원)
    rs = _day_riders('2-3인실', '종합', cause='상해'); tot = 0; parts = []
    for r, tk in sorted(rs, key=lambda x: -x[0]['man']):
        d = min(days, tk['limit'] or days); tot += r['man'] * d; parts.append(f'{won(r["man"])}×{d}일')
    add('bandage_adhesive', 'pk', '상해 입원 · 2-3인실 종합병원', ' + '.join(parts) if parts else '해당 담보 없음', big(tot, K['pk'][1]), tot > 0)
    # ③ 간병
    nm = lambda r: r['name'].replace(' ', '')
    pick = lambda key: [r for r in RID if key in nm(r) and '181일이상' not in nm(r)]
    sup = pick('간병인지원'); nano = [r for r in RID if ('간호·간병통합' in nm(r) or '간호간병통합' in nm(r)) and '181일이상' not in nm(r)]
    use = pick('간병인사용')
    add('nurse', 'pr', '간병인 지원', '회사가 간병인을 보내드려요 · 1회 입원당 180일 한도' if sup else '미가입',
        f'<span class="n2" style="color:{K["pr"][1]}">간병인 지원</span>' if sup else '', bool(sup))
    nv = max([r['man'] for r in nano] or [0])
    nd = min(days, min([S.tokens(S.nname(r['name']))['limit'] or days for r in nano] or [days]))
    add('hospital_symbol', 'cv', '간호·간병통합병실', f'하루 {won(nv)} × {nd}일' if nv else '미가입',
        big(nv * nd, K['cv'][1]), nv > 0)
    uv = max([r['man'] for r in use] or [0])
    ud = min(days, min([S.tokens(S.nname(r['name']))['limit'] or days for r in use] or [days]))
    add('nurse', 'ms', '간병인 직접 사용', f'하루 {won(uv)} × {ud}일 · 영수증 제출 시' if uv else '해당 담보 없음',
        big(uv * ud, K['ms'][1]), uv > 0)
    while len(cells) > 8:                                 # 4×2 그리드 유지 — 미가입 칸부터 뒤에서 뺀다
        off = [i for i, c in enumerate(cells) if not c['on']]
        cells.pop(off[-1] if off else len(cells) - 1)
    html = ''
    for c in cells:
        st = f'background:{K[c["k"]][2]}' if c['on'] else 'background:#F8F9FA'
        html += (f'<div class="stc" style="{st}">{et(c["ic"], "#fff" if c["on"] else "#DEE2E6", 20, K[c["k"]][1] if c["on"] else "#ADB5BD")}'
                 f'<b>{c["t"]}</b><span>{c["s"]}</span>{c["v"] if c["on"] else NOP2}</div>')
    return html

def care_cards():
    """간병인지원 / 간병인사용일당 / 간호·간병통합서비스 담보를 읽어 카드로"""
    out=[]
    def cause(n): return '상해' if '상해' in n else ('질병' if '질병' in n else '')
    def days(n):
        m=re.search(r'\((\d+)일이상\s*(\d+)일한도\)',n); 
        if m: return f'{m.group(1)}~{m.group(2)}일'
        m=re.search(r'\((\d+)일이상\)',n); return f'{m.group(1)}일 이상' if m else ''
    for r in RID:
        n=r['name'].replace(' ','')
        if '간호·간병통합' in n or '간호간병통합' in n:
            out.append(('hospital_symbol','간호·간병통합병실 입원 시',f'{cause(r["name"])} {days(r["name"])}',f'하루 {won(r["man"])}',K['yr']))
        elif '간병인사용' in n:
            out.append(('nurse','간병인 사용 시',f'{cause(r["name"])} {days(r["name"])}',f'하루 {won(r["man"])}',K['ms']))
        elif '간병인지원' in n:
            out.append(('nurse','간병인 지원 가능',f'{cause(r["name"])} {days(r["name"])} · 회사가 간병인을 보내드려요','간병인 지원',K['pr']))
    if not out: return '<div class="cc2"><span class="cnote">간병 관련 담보 미가입</span></div>'
    grp={}
    for ic,t,s2,v,k in out:
        d=grp.setdefault((t,v),{'ic':ic,'k':k,'s':[]})
        s3=s2.split(' · ')[0].strip()
        if s3 and s3 not in d['s']: d['s'].append(s3)
    html=''
    for (t,v),d in grp.items():
        html+=f'<div class="cc2" style="background:{d["k"][2]}">{et(d["ic"],"#fff",22,d["k"][1])}<div><b>{t}</b><span>{" / ".join(d["s"])}</span></div><em style="color:{d["k"][1]}">{v}</em></div>'
    return html

def itc_items():
    ids = [r for r in RID if r.get('itc') in ('circ','circ_top','ms')]
    if not ids: return '<div class="ic2">특정순환계질환 통합치료비 미가입</div>'
    r = ids[0]; out=''
    for nm, ic, keys, opt in [('혈전용해치료','drop2',['thromb'],{}),('수술(스텐트·코일 포함)','knife',['surg'],{}),
                              ('종합병원 중환자실','ambulance',['icu'],{}),('에크모(부분체외순환)','heart_organ',['ecmo'],{}),
                              ('지속적신대체요법','kidneys',['crrt'],{}),('인공호흡기(12시간초과)','ventilator',['vent'],{}),
                              ('저체온요법','thermometer',['hypo'],{}),('재활치료(1일)','physical_therapy',['rehab'],{'n':1})]:
        L = Q('I63', dict(cause='질병',grp=[],hosp='종합',room=None,days=0), [['치료',nm,'',keys,opt]])
        v = sum(x['amt'] for x in L if x['group']=='통합치료비')
        out += f'<div class="itci">{et(ic,K["yr"][3],20,K["yr"][1])}<div><b>{nm}</b>{big(v,K["yr"][1])}</div></div>'
    return out

# ── 사례 플로우 ────────────────────────────────────
FLOW = [
 dict(k='ca', ic='lungs', t='폐암', sub='진단 → 흉강경 폐절제 → 표적·면역(키트루다) 항암 → 입원', kcd='C34',
      steps=[('검사', 'microscope', '흉부 CT · PET · 조직검사', [['검사', '흉부 CT · PET · 조직검사', '', ['x_ct', 'x_pet', 'x_bio']]], dict(dx='cancer', hc=['CB003', 'CB004'])),   # NGS 유전자패널(고형암 Level I·II) 수가코드
             ('수술', 'surgical_sterilization', '흉강경 폐엽절제술', [['수술', '흉강경 폐엽절제술', '', ['surg']]], dict(surg='C1', surg7='E012', hosp='상급종합', anes=1)),
             ('항암', 'immune', '표적항암 → 키트루다(면역·비급여)', [['항암', '표적항암 · 면역항암(비급여)', '', ['chemo', 'target', 'immune'], {'nc': 1}]], dict(chemo=1, target=1, drug=2, tx_cnt=2, daycare=6, done=['surg'])),
             ('입원', 'hospital', '상급종합 1인실 10일 입원', [], dict(hosp='상급종합', room='1인실', days=10))],
      recur=('재진단', 'microscope', '첫 진단 2년 뒤 다른 부위 암 재진단', [], dict(dx='cancer', recur=True))),
 dict(k='yr', ic='heart_organ', t='급성 심근경색', sub='진단 → 스텐트 시술 → 중환자실 → 심장재활', kcd='I21',
      steps=[('진단','xray','응급 CT·심전도로 확진',[['검사','관상동맥 CT','',['x_ct']]],dict(dx='heart',grp=['심장질환'])),
             ('시술','knife','관상동맥 스텐트 삽입술(PCI)',[['시술','스텐트 삽입','',['surg']]],dict(surg='88-1',surg7='F121',grp=['심장질환','특정31대질병'],hosp='종합')),
             ('입원','ambulance','중환자실 2일 + 일반병실 7일',[['중환자','중환자실','',['icu']]],dict(hosp='종합',room='2-3인실',days=7,icu=2)),
             ('재활','physical_therapy','외래 심장재활 10회',[['재활','심장재활 10회','',['rehab'],{'n':10}]],dict())]),
 dict(k='cv', ic='neurology', t='뇌경색', sub='진단 → 혈전용해·혈전제거 → 중환자실 → 재활', kcd='I63',
      steps=[('검사', 'xray', '뇌 CT + MRI', [['진단', '뇌 CT + MRI', '', ['x_ct', 'x_mri']]], dict(dx='brain', grp=['뇌혈관질환', '뇌졸중'])),
             ('시술', 'drop2', '혈전용해제 주사(tPA)', [['시술', '혈전용해치료', '', ['thromb']]], dict()),
             ('수술', 'knife', '동맥내 기계적 혈전제거술', [['시술', '혈전제거술', '', ['surg']]], dict(surg='88-1', surg7='B027', grp=['뇌혈관질환', '뇌졸중', '특정31대질병'], hosp='종합', acts=['thrombectomy'], done=['thromb'])),
             ('입원', 'ambulance', '중환자실 3일 + 일반병실 14일', [['중환자', '중환자실', '', ['icu']], ['재활', '재활 10일', '', ['rehab'], {'n': 10}]], dict(hosp='종합', room='2-3인실', days=14, icu=3))]),
 # ── 보강 사례(v8.13) : 암·뇌·심장 중 일부 계열만 가입한 설계에서 빈 자리를 같은 계열의 다른 병으로 채운다 ──
 dict(k='ca', ic='stomach', t='위암', sub='진단 → 복강경 위아전절제 → 보조 항암 → 입원', kcd='C16', extra=True,
      steps=[('검사', 'microscope', '위내시경 · 조직검사 · 복부 CT', [['검사', '위내시경 · 조직검사 · CT', '', ['x_endo', 'x_bio', 'x_ct']]], dict(dx='cancer')),
             ('수술', 'surgical_sterilization', '복강경 위아전절제술', [['수술', '복강경 위아전절제술', '', ['surg']]], dict(surg='C1', surg7='G081', hosp='종합', anes=1)),
             ('항암', 'drop2', '수술 후 보조 항암약물치료(급여)', [['항암', '항암약물치료(급여)', '', ['chemo'], {'nc': 0}]], dict(chemo=1, done=['surg'])),
             ('입원', 'hospital', '종합병원 2-3인실 8일 입원', [], dict(hosp='종합', room='2-3인실', days=8))]),
 dict(k='ca', ic='breasts', t='유방암', sub='진단 → 유방절제술 → 방사선 → 항호르몬 치료', kcd='C50', extra=True, sex='F',
      steps=[('검사', 'microscope', '유방촬영 · 초음파 · 조직검사', [['검사', '유방촬영 · 초음파 · 조직검사', '', ['x_us', 'x_bio']]], dict(dx='cancer')),
             ('수술', 'surgical_sterilization', '유방절제술', [['수술', '유방절제술', '', ['surg']]], dict(surg='C1', surg7='J062', hosp='상급종합', anes=1)),
             ('방사선', 'immune', '수술 후 방사선치료 → 항호르몬약물', [['방사선', '방사선치료 · 호르몬', '', ['rad', 'hormone']]], dict(rad=1, hormone=1, done=['surg'])),
             ('입원', 'hospital', '상급종합 2-3인실 5일 입원', [], dict(hosp='상급종합', room='2-3인실', days=5))]),
 dict(k='ca', ic='prostate_cancer', t='전립선암', sub='진단 → 로봇 근치적 전립선절제 → 방사선 → 호르몬 치료', kcd='C61', extra=True, sex='M',
      steps=[('검사', 'microscope', 'PSA 혈액검사 · 전립선 MRI · 조직검사', [['검사', 'PSA · MRI · 조직검사', '', ['x_mri', 'x_bio']]], dict(dx='cancer')),
             ('수술', 'surgical_sterilization', '로봇 보조 근치적 전립선절제술', [['수술', '근치적 전립선절제술', '', ['surg']]], dict(surg='C1', surg7='M021', hosp='상급종합', anes=1)),
             ('방사선', 'immune', '수술 후 방사선치료 → 남성호르몬 차단(호르몬)치료', [['방사선', '방사선치료 · 호르몬', '', ['rad', 'hormone']]], dict(rad=1, hormone=1, done=['surg'])),
             ('입원', 'hospital', '상급종합 2-3인실 7일 입원', [], dict(hosp='상급종합', room='2-3인실', days=7))]),
 dict(k='ca', ic='colon', t='대장암', sub='진단 → 복강경 결장절제 → 보조 항암 → 입원', kcd='C18', extra=True, neutral=True,
      steps=[('검사', 'microscope', '대장내시경 · 조직검사 · 복부 CT', [['검사', '대장내시경 · 조직검사 · CT', '', ['x_endo', 'x_bio', 'x_ct']]], dict(dx='cancer')),
             ('수술', 'surgical_sterilization', '복강경 결장절제술(림프절절제 동반)', [['수술', '복강경 결장절제술', '', ['surg']]], dict(surg='C1', surg7='G131', hosp='종합', anes=1)),
             ('항암', 'drop2', '수술 후 보조 항암약물치료(급여)', [['항암', '항암약물치료(급여)', '', ['chemo'], {'nc': 0}]], dict(chemo=1, done=['surg'])),
             ('입원', 'hospital', '종합병원 2-3인실 8일 입원', [], dict(hosp='종합', room='2-3인실', days=8))]),
 dict(k='cv', ic='neurology', t='뇌출혈', sub='진단 → 혈종제거 개두술 → 중환자실 → 재활', kcd='I61', extra=True,
      steps=[('검사', 'xray', '응급 뇌 CT · 혈관조영', [['진단', '뇌 CT · 혈관조영', '', ['x_ct']]], dict(dx='brain', grp=['뇌혈관질환', '뇌졸중', '뇌출혈'])),
             ('수술', 'knife', '혈종제거 개두술', [['수술', '혈종제거 개두술', '', ['surg']]], dict(surg='59', surg7='B031', grp=['뇌혈관질환', '뇌졸중', '뇌출혈', '특정31대질병'], hosp='상급종합', anes=1)),
             ('입원', 'ambulance', '중환자실 5일 + 일반병실 20일', [['중환자', '중환자실', '', ['icu']]], dict(hosp='상급종합', room='2-3인실', days=20, icu=5)),
             ('재활', 'physical_therapy', '재활치료 20일', [['재활', '재활 20일', '', ['rehab'], {'n': 20}]], dict())]),
 dict(k='cv', ic='blood_vessel', t='뇌동맥류(미파열)', sub='진단 → 코일 색전술 → 입원 → 외래 추적', kcd='I67.1', extra=True,
      steps=[('검사', 'xray', '뇌 MRA · CT 혈관조영', [['진단', '뇌 MRA · CT 혈관조영', '', ['x_mri', 'x_ct']]], dict(dx='brain', grp=['뇌혈관질환'])),
             ('시술', 'knife', '뇌동맥류 코일 색전술', [['시술', '코일 색전술', '', ['surg']]], dict(surg='88-1', surg7='B016', grp=['뇌혈관질환', '특정31대질병'], hosp='상급종합', anes=1)),
             ('입원', 'hospital', '상급종합 2-3인실 5일 입원', [], dict(hosp='상급종합', room='2-3인실', days=5)),
             ('통원', 'stethoscope', '외래 추적 MRA 2회', [], dict(visits=2))]),
 dict(k='yr', ic='heart_cardiogram', t='협심증', sub='진단 → 관상동맥 스텐트 → 입원 → 심장재활', kcd='I20', extra=True,
      steps=[('진단', 'xray', '심전도 · 관상동맥 CT · 조영술', [['검사', '관상동맥 CT', '', ['x_ct']]], dict(dx='heart', grp=['심장질환', '허혈성심장질환'])),
             ('시술', 'knife', '관상동맥 스텐트 삽입술(PCI)', [['시술', '스텐트 삽입', '', ['surg']]], dict(surg='88-1', surg7='F133', grp=['심장질환', '허혈성심장질환', '특정31대질병'], hosp='종합')),
             ('입원', 'hospital', '종합병원 2-3인실 3일 입원', [], dict(hosp='종합', room='2-3인실', days=3)),
             ('재활', 'physical_therapy', '외래 심장재활 10회', [['재활', '심장재활 10회', '', ['rehab'], {'n': 10}]], dict())]),
 dict(k='yr', ic='heart_cardiogram', t='심방세동(부정맥)', sub='진단 → 고주파 전극도자절제술 → 입원 → 외래 추적', kcd='I48', extra=True,
      steps=[('진단', 'xray', '심전도 · 24시간 홀터 · 심초음파', [['검사', '심초음파', '', ['x_us']]], dict(dx='heart', grp=['심장질환'])),
             ('시술', 'knife', '고주파 전극도자절제술(3D 지도화)', [['시술', '전극도자절제술', '', ['surg']]], dict(surg='88-1', surg7='F142', grp=['심장질환', '특정31대질병'], hosp='상급종합')),
             ('입원', 'hospital', '상급종합 2-3인실 3일 입원', [], dict(hosp='상급종합', room='2-3인실', days=3)),
             ('통원', 'stethoscope', '외래 추적 · 항응고 약물 4회', [], dict(visits=4))]),
]
def pick_cases():
    """사례 카드 3장 : 가입한 계열의 대표 사례(폐암·뇌경색·심근경색)를 먼저, 빈 자리는 가입한 계열의 보강 사례로 채운다(v8.13).
       세 계열을 모두 가입했으면 종전처럼 대표 사례 3장만."""
    have = {'ca': F['cancer'], 'cv': F['brain'], 'yr': F['heart']}; order = ['ca', 'cv', 'yr']
    out = sorted([f for f in FLOW if not f.get('extra') and have[f['k']]], key=lambda f: order.index(f['k']))
    def fits(f):
        """성별 맞춤(v8.19) : sex='F'(유방암)·'M'(전립선암) 사례는 피보험자 성별이 같을 때만, neutral 사례(대장암)는 성별을 모를 때만"""
        if f.get('sex'): return f['sex'] == SEX
        if f.get('neutral'): return not SEX
        return True
    for k in order:
        for f in FLOW:
            if len(out) >= 3: break
            if f.get('extra') and f['k'] == k and have[k] and fits(f): out.append(f)
    return out
def flow_card(f):
    d = K[f['k']][1]; tl = K[f['k']][3]; acc = 0; cards = ''
    steps = f['steps'] + ([f['recur']] if f.get('recur') and F['recur'] else [])   # 재진단암 담보가 있는 설계만 5단계(v8.12)
    paid = set()          # 한 사례 안에서 '연간 1회한·최초 1회한' 담보는 한 단계에서만 센다(v8.21)
    for i, (stg, ic, nm, itc, tg) in enumerate(steps):
        tags = dict(cause='질병', grp=[], hosp='상급종합', room=None, days=0); tags.update(tg)
        L = Q(f['kcd'], tags, itc)
        once = lambda x: x.get('freq') in ('year', 'once') and x.get('group') not in ('통합치료비', '통합생활지원비')
        L = [x for x in L if not (once(x) and x['name'] in paid)]
        paid |= {x['name'] for x in L if once(x)}
        v = T(L, 'first'); acc += v
        pos = [x for x in sorted(L, key=lambda y: -y['amt']) if x['amt'] > 0]
        det2 = ''.join(f'<li><span>{disp(x["name"])[:22]}</span>{cutmark(x["name"])}<b>{man(x["amt"])}</b></li>' for x in pos[:2])
        if len(pos) > 2: det2 += f'<li class="etc"><span>+{len(pos)-2}개 특약</span><b>{man(sum(x["amt"] for x in pos[2:]))}</b></li>'
        cards += f'''<div class="fs"><div class="fb" style="background:{tl}">{e(ic,d)}</div>
          <div class="fst" style="color:{d}">STEP {i+1} · {stg}</div><div class="fn">{nm}</div>
          <div class="fv">{big(v,d)}</div><ul>{det2 or "<li>해당 담보 없음</li>"}</ul></div>'''
    return f'''<div class="fcase" style="background:{K[f['k']][2]}">
      <div class="fh">{et(f['ic'],'#fff',26,d)}<div><b style="color:{d}">{f['t']}</b><span>{f['sub']}</span></div>
      <div class="ftot"><span>합계</span>{big(acc,d)}</div></div>
      <div class="flow"><div class="fline" style="border-color:{K[f['k']][0]}"></div>{cards}</div></div>'''

# ── 다빈도 질환 ────────────────────────────────────
FREQ = [
 ('갑상선결절', 'D34', 'thyroid', '고주파 절제술', '비급여 150~300만원', dict(surg=3, surg7=1, grp=['다빈도62대질병']), [['수술', '고주파 절제', '', ['surg'], {'j': 3}]]),
 ('자궁경부이형성증', 'N87.1', 'cervical_cancer', '자궁경부 원추절제술', '급여 · 1종 수술 · 국가암검진에서 발견', dict(surg='53', surg7='N082', grp=[], hc=['R4261', 'R4262']), [['수술', '원추절제술', '', ['surg'], {'j': 1}]]),
 ('자궁근종', 'D25', 'cervical_cancer', '하이푸 · 복강경 절제', '비급여 600~1,000만원', dict(surg='52', surg7='N031', grp=['다빈도62대질병']), [['수술', '복강경 근종 절제', '', ['surg'], {'j': 2}]]),
 ('대장 용종', 'D12', 'colon', '내시경 용종절제술', '급여 · 1종 수술', dict(surg='88-2', surg7='G523', grp=['다빈도62대질병'], five_major=True, hc=['Q7701', 'Q7702', 'Q7703', 'QX706']), [['진단', '대장내시경', '', ['x_endo']], ['수술', '용종 절제', '', ['surg'], {'j': 1}]]),
 ('담석증', 'K80.0', 'gallbladder', '복강경 담낭절제술', '급여 · 2종 수술', dict(surg='36', surg7='H107', grp=['다빈도62대질병'], days=5, room='2-3인실', hosp='모든'), [['진단', '복부 CT', '', ['x_ct']], ['수술', '복강경 담낭 절제', '', ['surg'], {'j': 2}]]),
 ('백내장', 'H25.9', 'body', '수정체 유화술 + 인공수정체', '급여 · 1종 수술', dict(surg='71', surg7='C061', grp=['백내장']), [['수술', '수정체 유화술 + 인공수정체', '', ['surg'], {'j': 1}]]),
 ('디스크(추간판장애)', 'M51', 'body', '신경성형술 · 내시경 수술', '비급여 160~380만원', dict(surg='88-2', surg7='B174', grp=['다빈도62대질병']), [['수술', '내시경 추간판 수술', '', ['surg'], {'j': 2}]]),
 ('치핵', 'K64', 'intestine', '치핵절제술', '급여 · 1종 수술', dict(surg='44', surg7='G272', grp=['치핵']), [['수술', '치핵절제술', '', ['surg'], {'j': 1}]]),
 ('급성 충수염(맹장염)', 'K35', 'intestine', '복강경 충수절제술', '급여 · 2종 수술', dict(surg='41', surg7='G212', grp=[]), [['진단', '복부 CT', '', ['x_ct']], ['수술', '복강경 충수 절제', '', ['surg'], {'j': 2}]]),
 ('편도염(만성·재발)', 'J35', 'body', '편도절제술', '급여 · 1종 수술', dict(surg='17', surg7='D162', grp=['다빈도62대질병']), [['수술', '편도 절제', '', ['surg'], {'j': 1}]]),
]
def freq_rows():
    out = ''
    for nm, kcd, ic, op, note, tg, itc in FREQ:
        base = dict(cause='질병', hosp='모든', room=None, days=0, grp=[]); base.update(tg)
        L1 = Q(kcd, base, itc)
        b2 = dict(base); b2['hosp'] = '상급종합'
        L2 = Q(kcd, b2, itc)
        L1 = [x for x in L1 if x['group'] not in ('입원일당', '통원일당')]; L2 = [x for x in L2 if x['group'] not in ('입원일당', '통원일당')]
        items = ''.join(f'<span class="fi">{disp(x["name"])[:22]}{cutmark(x["name"])}<b>{man(x["amt"])}</b></span>' for x in sorted(L2, key=lambda y: -y['amt']) if x['amt'] > 0) or '<span class="fi none">해당 담보 없음</span>'
        out += f'''<div class="frow">{et(ic,K['pr'][3],30,K['pr'][1])}
          <div class="fnm"><b>{nm}</b><span>{kcd}</span><em>{op} · {note}</em></div>
          <div class="fitems">{items}</div>
          <div class="fpay"><div><span>모든 병원</span>{big(T(L1),'#087F5B')}</div><div><span>상급종합</span>{big(T(L2),'#087F5B')}</div></div></div>'''
    return out

# ── 질병코드 지도(모자이크) ────────────────────────
KN = json.load(open(os.path.join(BASE, 'kcdnames.json'), encoding='utf-8'))
PD = json.load(open(os.path.join(BASE, 'product_data.json'), encoding='utf-8'))
DBM = json.load(open(os.path.join(BASE, 'db.json'), encoding='utf-8'))['riders']

BRAIN_MASK = ['.###.', '#####', '#####', '..#..']
HEART_MASK = ['.###..###...', '############', '############', '############',
              '.##########.', '..########..', '...######...', '....####....', '.....##.....']
BRAIN_TILES = ['I60', 'I61', 'I62', 'I63', 'I64', 'I65', 'I66', 'I67', 'I68', 'I69', 'Q28', 'S06', 'G45', 'G46']
def heart_tiles():
    ex = set(BRAIN_TILES)
    out = []
    for c in PD['EMB']['c32'] + PD['EMB']['m61']:
        c3 = re.split(r'[.~]', c)[0]
        if c3[0] in 'IS' and c3 not in ex and c3 not in out: out.append(c3)
    return sorted(out) + ['Q20', 'Q21', 'Q25', 'Q26']       # 선천성 심장기형 — 산정특례에서만 보장되는 영역

def master_codes(pat):
    """특약 마스터(db.json)에서 담보명으로 약관 KCD 목록을 가져온다"""
    for r in DBM:
        if re.search(pat, r['n'].replace(' ', '')): return r['k']
    return []

def tiers(part):
    """좁은 담보 → 넓은 담보 순서. (담보명, 요약, KCD목록, 색)"""
    if part == 'brain':
        T = [('뇌출혈 진단비', 'I60~I62 · 출혈만', master_codes(r'^뇌출혈진단비'), '#C92A2A'),
             ('뇌졸중 진단비', 'I60~I63 · I65~I66', master_codes(r'^뇌졸중진단비'), '#E8590C'),
             ('뇌혈관질환 진단비', 'I60~I69 전체', master_codes(r'^뇌혈관질환진단비'), '#F08C00'),
             ('산정특례 진단비(뇌혈관)', 'I60~I67 · Q28 · S06', master_codes(r'중증질환자\(뇌혈관질환\)산정특례'), '#2B8A3E'),
             ('특정순환계질환 통합치료비', '순환계 52개 질병 · 치료 항목별', PD['EMB']['c32'], '#1971C2'),
             ('특정순환계질환(주요손상및질환) 통합치료비', '고혈압·판막·정맥 + 두개내손상 등 40개', PD['EMB']['m61'], '#6741D9')]
    else:
        T = [('급성심근경색증 진단비', 'I21~I23 · 경색만', master_codes(r'^급성심근경색증진단비'), '#C92A2A'),
             ('허혈성심장질환 진단비', 'I20~I25 · 협심증 포함', master_codes(r'^허혈성심장질환진단비'), '#E8590C'),
             ('산정특례 진단비(심장)', 'I05~I51 · Q20~Q26 등', master_codes(r'중증질환자\(심장질환\)산정특례'), '#2B8A3E'),
             ('특정순환계질환 통합치료비', '순환계 52개 질병 · 치료 항목별', PD['EMB']['c32'], '#1971C2'),
             ('특정순환계질환(주요손상및질환) 통합치료비', '고혈압·판막·정맥·흉부손상 등 40개', PD['EMB']['m61'], '#6741D9')]
    return [t for t in T if t[2]]

def joined(nm):
    """설계에 가입된 담보인지 — 가입금액을 돌려준다"""
    key = re.sub(r'[\s()]', '', nm).replace('진단비', '').replace('통합치료비', '')
    best = 0
    for r in RID:
        n = r['name'].replace(' ', '')
        if nm.startswith('뇌출혈') and '뇌출혈진단' in n: best = max(best, r['man'])
        elif nm.startswith('뇌졸중') and '뇌졸중진단' in n: best = max(best, r['man'])
        elif nm.startswith('뇌혈관질환 진단비') and '뇌혈관질환진단비' in n: best = max(best, r['man'])
        elif nm.startswith('급성심근경색') and '급성심근경색증진단' in n: best = max(best, r['man'])
        elif nm.startswith('허혈성심장질환 진단비') and '허혈성심장질환진단비' in n: best = max(best, r['man'])
        elif nm.startswith('산정특례') and '산정특례' in n and (('뇌혈관' in nm and '뇌혈관' in n) or ('심장' in nm and '심장' in n)): best = max(best, r['man'])
        elif nm.startswith('특정순환계질환 통합') and r.get('itc') in ('circ', 'circ_top'): best = max(best, r['man'])
        elif nm.startswith('특정순환계질환(주요') and r.get('itc') == 'ms': best = max(best, r['man'])
    return best

def sort_tiers(T, codes):
    return sorted(T, key=lambda t: sum(1 for c in codes if S.code_hit(t[2], c)))

HEART_GROUPS = [('류마티스', 'I00', 'I09'), ('고혈압', 'I10', 'I15'), ('허혈성', 'I20', 'I25'), ('폐성', 'I26', 'I28'),
                ('판막·심근', 'I30', 'I43'), ('부정맥·심부전', 'I44', 'I52'), ('동맥', 'I70', 'I79'),
                ('정맥', 'I80', 'I89'), ('기타', 'I95', 'I99'), ('손상', 'S25', 'S26'), ('선천', 'Q20', 'Q26')]

def dz_blocks(part, codes, T, groups=None, labeled=True):
    """담보(행) × 질병코드(열) 블록 — 아래로 갈수록 넓어지는 계단 모양으로 보장 범위를 비교"""
    tot = len(codes)
    head = ''
    if groups:
        cells = ''
        for lab, a, b in groups:
            n = sum(1 for c in codes if a <= c <= b)
            if n: cells += f'<th colspan="{n}"><span>{lab}</span></th>'
        head += f'<tr class="grp"><th class="rl"></th>{cells}<th class="gg"></th></tr>'
    if labeled:
        head += '<tr class="cd"><th class="rl"></th>' + ''.join(f'<th><b>{c}</b><span>{(KN.get(c) or "")[:5]}</span></th>' for c in codes) + '<th class="gg">보장 범위</th></tr>'
    else:
        head += '<tr class="cd"><th class="rl"></th>' + ''.join('<th></th>' for c in codes) + '<th class="gg">보장 범위</th></tr>'
    body = ''
    for nm, sm, k, col in T:
        hit = [S.code_hit(k, c) for c in codes]
        n = sum(hit); pct = round(n / tot * 100) if tot else 0
        jm = joined(nm)
        cells = ''.join(f'<td><i style="background:{col if h else "#EDEFF2"}"></i></td>' for h in hit)
        body += (f'<tr><th class="rl"><i style="background:{col}"></i><div><b>{nm}</b><span>{sm}</span>'
                 f'<em style="color:{col}">{won(jm)+" 가입" if jm else ""}</em>{"" if jm else "<em class=no>미가입</em>"}</div></th>{cells}'
                 f'<td class="gg"><b style="color:{col}">{n}</b><span>/{tot}</span><div class="bar"><u style="width:{pct}%;background:{col}"></u></div></td></tr>')
    return f'<table class="dzb {part}"><thead>{head}</thead><tbody>{body}</tbody></table>'

def gap_block(hc, no=3):
    """특정순환계질환 통합치료비 + 주요손상및질환 통합치료비 동시 가입 시 순환계 질병코드 커버율"""
    circ, ms = PD['EMB']['c32'], PD['EMB']['m61']
    out = ''
    for k, ic, title, codes in [('cv', 'neurology', '뇌혈관 질병코드', BRAIN_TILES), ('yr', 'heart_organ', '심장 · 혈관 질병코드', hc)]:
        a = sum(1 for c in codes if S.code_hit(circ, c)); b = sum(1 for c in codes if S.code_hit(ms, c) and not S.code_hit(circ, c))
        n = len(codes); rest = n - a - b
        pa, pb, pr = round(a/n*100), round(b/n*100), 100 - round(a/n*100) - round(b/n*100)
        jc, jm = joined('특정순환계질환 통합치료비'), joined('특정순환계질환(주요손상및질환) 통합치료비')
        st = ('두 담보 모두 가입' if jc and jm else ('특정순환계질환만 가입' if jc else ('주요손상및질환만 가입' if jm else '미가입')))
        out += f'''<div class="gapr" style="background:{K[k][2]}">{et(ic,'#fff',22,K[k][1])}<div class="gapt"><b style="color:{K[k][1]}">{title} {n}개</b><span>{st}</span></div>
          <div class="gapbar"><i style="width:{pa}%;background:#1971C2"></i><i style="width:{pb}%;background:#6741D9"></i><i style="width:{pr}%;background:#DEE2E6"></i></div>
          <div class="gapleg"><span><i style="background:#1971C2"></i>특정순환계질환 {a}개</span><span><i style="background:#6741D9"></i>+ 주요손상및질환 {b}개</span><span><i style="background:#DEE2E6"></i>어느 쪽도 아님 {rest}개</span></div>
          <div class="gapv"><span class="n2" style="color:{K[k][1]}">{a+b}<small>개</small></span><em>/ {n}개 · {round((a+b)/n*100)}% 커버</em></div></div>'''
    return tabhd(no, 'yr', '두 통합치료비를 함께 가입하면', '특정순환계질환(52개)과 주요손상및질환(40개)은 서로 겹치지 않아 보장 공백이 이렇게 채워져요') + f'<div class="gapwrap">{out}</div>'

def page_dzmap():
    hc = heart_tiles(); parts = []; no = 0                 # 설계에 없는 계열 블록은 빠진다(v8.4)
    if F['brain']:
        no += 1; parts.append(tabhd(no,'cv','뇌혈관 질환 — 담보별 보장 범위','한 칸이 질병코드 하나 · 아래 담보로 갈수록 보장이 넓어져요') + dz_blocks('brain', BRAIN_TILES, tiers('brain')))
    if F['heart']:
        no += 1; parts.append(tabhd(no,'yr','심장 · 혈관 질환 — 담보별 보장 범위',f'순환계 질병코드 {len(hc)}개 · 진단비는 좁고, 통합치료비는 넓어요') + dz_blocks('heart', hc, tiers('heart'), HEART_GROUPS, labeled=False))
    if any(r.get('itc') in ('circ', 'circ_top', 'ms') for r in RID):
        parts.append(gap_block(hc, no + 1))
    out = f'''{''.join(parts)}
 <div class="tip">{e('bulb','#D9480F')}<span>색칸은 <b>그 담보가 보장하는 질병</b>, 회색은 대상이 아닌 질병이에요. 진단비는 정해진 질병코드에만 <b>최초 1회</b> 지급되는 대신 금액이 크고, 통합치료비는 범위가 넓은 대신 <b>실제 받은 치료 항목마다</b> 지급돼요. 특정순환계질환 통합치료비와 주요손상및질환 통합치료비는 <b>서로 겹치지 않고 보완</b>해서 둘을 함께 가입하면 순환계 질병 대부분이 채워져요.</span></div>'''
    return out

# ── 통합치료비 한눈에 ────────────────────────────────
# 암 → 순환계 → 질병 → 상해 순. 상단 카드 줄과 아래 섹션이 같은 순서를 따른다(v8.35).
# 설계서 담보번호 순으로 두면 질병 통합치료비가 맨 앞에 오는 등 계열이 뒤섞인다.
ITC_GROUPS = [('ca', 'cancerous_cell_nuclei', '암 통합치료비', ('ca_basic', 'ca_basic_c', 'ca_lite', 'ca_lite_c', 'ca_nc2', 'ca_nc2_c', 'ca_ncm', 'ca_ncm_c')),
              ('pr', 'microscope', '암 전후 · 양성신생물 통합치료비', ('pre',)),
              ('cv', 'neurology', '특정순환계질환 통합치료비', ('circ', 'circ_top')),
              ('yr', 'heart_organ', '주요손상및질환 통합치료비', ('ms',)),
              ('ms', 'stethoscope', '질병 통합치료비', ('dz',)),
              ('pk', 'wound', '상해 통합치료비', ('inj',))]
ITC_ORDER = {i: n for n, g in enumerate(ITC_GROUPS) for i in g[3]}
LS_ROOM = 660        # 통합치료비 지면에서 본문이 쓸 수 있는 세로(pt) 어림 — 이보다 커지면 생활지원비 블록을 뺀다
ITC_SLIM = ('ms', 'pre')                       # 종수술비는 1종·5종만 예시
# 대표 사례(폐암·뇌경색·심근경색)에 해당 항목이 없는 통합치료비의 대체 사례 — 약관 대상 질병(EMB.m61 · EMB.p60)에서 고른다(v8.13)
ITC_ALT = {
 'ms': [dict(k='ms', t='외상성 뇌출혈', kcd='S06.5',
             steps=[('검사', 'xray', '응급 뇌 CT', [['진단', '뇌 CT', '', ['x_ct']]], dict(cause='상해', dx='brain', grp=['뇌혈관질환'])),
                    ('수술', 'knife', '혈종제거 개두술', [['수술', '혈종제거 개두술', '', ['surg'], {'j': 5}]], dict(cause='상해', surg='59', surg7='B122', hosp='상급종합')),
                    ('입원', 'ambulance', '중환자실 5일 + 일반병실 14일', [['중환자', '중환자실', '', ['icu']]], dict(cause='상해', hosp='상급종합', room='2-3인실', days=14, icu=5)),
                    ('재활', 'physical_therapy', '재활 10일', [['재활', '재활 10일', '', ['rehab'], {'n': 10}]], dict(cause='상해'))]),
        dict(k='ms', t='죽상경화증(하지동맥 폐쇄)', kcd='I70.2',
             steps=[('검사', 'xray', '하지 혈관 CT · 초음파', [['검사', '혈관 CT', '', ['x_ct']]], dict(grp=[])),
                    ('시술', 'knife', '말초동맥 혈관성형 · 스텐트', [['시술', '경피적 혈관 시술', '', ['surg'], {'j': 3}]], dict(surg='22', surg7='F194', hosp='종합')),
                    ('입원', 'hospital', '종합병원 2-3인실 3일', [], dict(hosp='종합', room='2-3인실', days=3))])],
 'pre': [dict(k='pr', t='담석증(급성 담낭염)', kcd='K80.0',
              steps=[('검사', 'xray', '복부 CT · 초음파', [['검사', '복부 CT', '', ['x_ct']]], dict(grp=[])),
                     ('수술', 'knife', '복강경 담낭절제술', [['수술', '복강경 담낭절제', '', ['surg'], {'j': 3}]], dict(surg='36', surg7='H101', hosp='종합')),
                     ('입원', 'hospital', '종합병원 2-3인실 5일', [], dict(hosp='종합', room='2-3인실', days=5))]),
         dict(k='pr', t='궤양성 대장염', kcd='K51',
              steps=[('검사', 'microscope', '대장내시경 · 조직검사', [['검사', '대장내시경 · 조직검사', '', ['x_endo', 'x_bio']]], dict(grp=[])),
                     ('입원', 'hospital', '종합병원 2-3인실 7일', [], dict(hosp='종합', room='2-3인실', days=7))])]}

def itc_filler(its, no):
    """통합치료비 담보가 1~2개인 설계 : ① 대표 사례의 치료 단계마다 이 담보에서 얼마가 나오는지(연간 한도 적용) ② 진단비와 무엇이 다른지"""
    out = ''
    rows = ''; skipped = []
    def row_for(r, f):
        cells = ''; tot = 0
        for stg, ic, nm2, itc, tg in f['steps']:
            tags = dict(cause='질병', grp=[], hosp='상급종합', room=None, days=0); tags.update(tg)
            v = sum(x['amt'] for x in Q(f['kcd'], tags, itc) if x['name'] == r['name']); tot += v
            cells += f'<td><span class="itcst">{stg}</span>{big(v, K[f["k"]][1]) if v else "<span class=z>—</span>"}</td>'
        if not tot: return ''
        cap = min(tot, r['man'])
        return f'<tr><th class="rl">{S.itc.RM[r["itc"]]["nm"][:18]}<br><span>{f["t"]} 사례 · 한도 {won(r["man"])}</span></th>{cells}<td class="itcsum">{big(cap, "#C92A2A")}<em>{"한도 적용" if tot > r["man"] else "연간 합계"}</em></td></tr>'
    for r in its:
        it = r['itc'] or ''
        flows = [f for f in FLOW if not f.get('extra') and (f['k'] == 'ca' if it.startswith(('ca', 'pre')) else f['k'] in ('cv', 'yr'))]
        got = ''.join(row_for(r, f) for f in flows)
        if not got:                                     # 대표 사례에 해당 항목이 없으면 그 담보의 약관 대상 질병으로 만든 대체 사례(외상성 뇌출혈·죽상경화증 / 담석증·궤양성 대장염)
            got = ''.join(row_for(r, f) for f in ITC_ALT.get(it.split('_')[0], []))
        if not got: skipped.append(S.itc.RM[it]['nm']); continue
        rows += got
    if rows:
        no += 1
        note = f'<div class="mnote">※ {" · ".join(dict.fromkeys(skipped))}는 대표 사례(폐암·뇌경색·심근경색)에 해당 치료 항목이 없어 표에서 제외 — 위 항목표를 참고하세요.</div>' if skipped else ''
        out += tabhd(no, 'pr', '치료 단계마다 통합치료비에서 얼마가 나오나', '대표 사례의 단계별 지급액 · 항목별 연간 1회 · 연간 한도까지') + f'<table class="mx itcflow"><tbody>{rows}</tbody></table>{note}'
    no += 1
    out += tabhd(no, 'ms', '진단비와 무엇이 다른가', '통합치료비를 처음 보는 고객에게 설명하는 순서') + '''<div class="why4">
      <div><b>① 진단 1회가 아니라 치료마다</b>진단비는 진단확정 시 한 번. 통합치료비는 검사·수술·항암·재활 등 <b>실제 받은 치료 항목마다</b> 약관 금액을 지급.</div>
      <div><b>② 연간 한도는 해마다 새로</b>한 해에 받은 금액의 합계가 가입금액(연간 한도)까지. 다음 해가 되면 <b>한도가 다시 채워짐</b> — 치료가 길어질수록 유리.</div>
      <div><b>③ 항목별 지급 빈도</b>검사·주요치료는 항목별 연간 1회, 수술은 수술할 때마다, 재활·입원 항목은 1일 1회. 같은 항목을 한 해에 여러 번 받아도 1회분.</div>
      <div><b>④ 치료가 많은 암일수록 더 많이</b>수술·항암·방사선·재활을 오래 여러 번 받는 암, 표적·면역항암처럼 <b>치료비가 많이 드는 암</b>일수록 항목이 쌓여 지급액이 커짐 — 정액 진단비와 달리 <b>실제 치료 부담에 비례</b>하는 구조.</div></div>'''
    return out

def itc_name(r):
    """담보 → (표시 이름, 한 줄 설명). 상해 통합치료비는 금액표가 따로라 별도 처리(v8.35)"""
    if r['itc'] == 'inj':
        return r['name'], '다쳤을 때 검사·수술·주요치료·재활을 항목별로 보장해요'
    m = S.itc.RM[r['itc']]
    return m['nm'], m.get('about', '')

def itc_amounts(r):
    """담보 → [(항목 라벨, 금액, 분류, 지급빈도키)] — 약관 지급금액표에서"""
    if r['itc'] == 'inj':
        _r, items = inj_itc_rider()
        for it in (items or []):
            p = 'd' if '재활' in it['l'] else ('o' if it.get('c', '').startswith('수술') else 'y')
            yield it['l'], it['amt'], it.get('c', ''), p
        return
    ty = S.itc.RM[r['itc']]['ty']
    amts = S.itc.AMT[ty].get(str(r['man']))
    for it, a in zip(S.itc.IT[ty], amts or []):
        if a <= 0: continue
        if r['itc'] in ITC_SLIM and it.get('j') in (2, 3, 4): continue
        yield it['l'], a, it.get('c', ''), it.get('p', 'y')

# ── 통합생활지원비 (v8.36) ─────────────────────────────────────────
# 통합치료비와 헷갈리기 쉬워 지면에서도 분명히 갈라 놓는다.
#   통합치료비   : 치료 항목마다 · **연간** 한도(가입금액) · 해마다 새로
#   통합생활지원비 : 산정특례 등록·치료 항목마다 · **월간** 한도(가입금액) · 달마다 새로
# 금액은 약관 항목표(life_support.json)를 그대로 쓴다 — 구간이 없으면 만들지 않고 로그만 남긴다.
LS_GRP = [('산정특례', 'limit', '산정특례로 등록되면', '국민건강보험 산정특례에 등록될 때 · 등록 1건마다'),
          ('주요치료', 'syringe', '주요치료를 받으면', '전신마취 · 중환자실 · 항암 · 혈전용해 등'),
          ('재활치료', 'bandage_adhesive', '재활치료를 받으면', '전문 · 전문 외 재활치료')]
LS_K = {'ca_ls': 'ca', 'two_ls': 'cv', 'dz_ls': 'ms', 'inj_ls': 'pk'}

_LS_CACHE = []
def ls_riders():
    """설계의 통합생활지원비 담보 → [(담보, id, 항목표, 근거)]
       항목표와 근거 판정은 계산과 같은 것을 쓴다(scen_engine.ls_items) — 지면과 금액이 갈리지 않게."""
    if _LS_CACHE: return _LS_CACHE[0]
    out = []
    for r in RID:
        rid = S.ls_id(r['name'])
        if not rid: continue
        items, src = S.ls_items(r)
        if items: out.append((r, rid, items, src))
    out.sort(key=lambda x: (['ca_ls', 'two_ls', 'dz_ls', 'inj_ls'].index(x[1]), -x[0]['man']))
    _LS_CACHE.append(out)
    return out

def ls_bookname(f):
    """약관 파일명 → 지면에 쓸 이름 (무배당·확장자·괄호 사족 정리)"""
    n = re.sub(r'\.pdf$', '', f or '', flags=re.I)
    n = re.sub(r'^무배당\s*', '', n)
    n = re.sub(r'\s*약관$', ' 약관', n)
    return n.strip()

def ls_src(rid):
    """이 담보 금액표의 출처 약관 — 같은 표가 여러 상품 약관에 있으므로 **이 설계 상품의 약관**을 고른다."""
    v = S.LS.get(rid) or {}
    srcs = v.get('srcs') or ([{'src': v.get('src'), 'page': v.get('page')}] if v.get('src') else [])
    if not srcs: return None
    pn = re.sub(r'\s+', '', C.get('product') or '')
    for x in srcs:                                        # 파일명의 한글 토막이 상품명에 들어 있으면 그 약관
        for tok in re.findall(r'[가-힣A-Za-z-]{4,}', re.sub(r'\s+', '', x['src'] or '')):
            if tok in ('무배당', '메리츠', '약관') or tok not in pn: continue
            return (x['src'], x['page'])
    return (srcs[0]['src'], srcs[0]['page'])

def lsl(label):
    """항목 라벨을 칸에 맞게 — 꼬리의 '산정특례(대상) 등록'은 묶음 이름에 이미 있다"""
    return re.sub(r'\\s*산정특례\\s*(대상)?\\s*등록\\s*$', '', label or '').strip()

LS_MINI_H = 0          # 아래 ls_mini() 가 채운다(지면 높이 어림값 · pt)

def ls_mini():
    """통합생활지원비 간추린 블록 — 통합치료비 지면 맨 아래에 **자리가 남을 때만** 붙인다.

    통합생활지원비는 가입하는 설계가 드물고, 가입해도 담보가 한둘이다.
    통합치료비를 많이 넣어 지면이 꽉 찬 설계에서는 이 블록을 통째로 뺀다(가로 지면을 억지로 줄이지 않는다).
    금액 계산은 이 블록과 무관하게 사례·매트릭스에 그대로 들어간다.
    """
    global LS_MINI_H
    rs = ls_riders()
    if not rs:
        LS_MINI_H = 0
        return ''
    GN = {'산정특례': '산정특례 등록', '주요치료': '주요치료', '재활치료': '재활치료'}
    rows = ''; h = 26
    for r, rid, items, _src in rs:
        k = LS_K.get(rid, 'ms')
        chips = ''
        for g in ('산정특례', '주요치료', '재활치료'):
            its = [x for x in items if x['grp'] == g]
            if not its: continue
            chips += f'<span class="lsmg" style="color:{K[k][1]}">{GN[g]}</span>'
            chips += ''.join(f'<span class="lsmi"><b>{lsl(x["label"])}</b>{num(x["amt"])}</span>' for x in its)
        n = len(items) + 3
        h += max(26, -(-n // 5) * 15 + 8)
        cut = '<em class="ct">계약 1년 이내 50%</em>' if any(x['amt_pre'] < x['amt'] for x in items) else ''
        rows += (f'<div class="lsmr"><div class="lsmn" style="background:{K[k][2]}"><b>{r["name"]}</b>'
                 f'<span>한 달 한도 {won(r["man"])}</span>{cut}</div><div class="lsmc">{chips}</div></div>')
    srcn = ls_srcnote(rs)
    h += 26 if srcn else 0
    LS_MINI_H = h
    return (f'<div class="lsmini"><div class="lsmh">{e("coins","#0B7285")}<b>통합생활지원비 — 치료 항목마다 <u>매달</u> 나오는 생활비</b>'
            f'<span>진단만으로는 나오지 않아요 · 산정특례 등록·치료를 받은 <b>달</b>마다 항목별 금액 · 한 달 합계는 <b>가입금액</b>까지</span></div>'
            f'{rows}{srcn}</div>')

def ls_srcnote(rs):
    """지면에는 한 줄만 — 어느 약관·어느 쪽에서 왔는지는 고객에게 필요한 정보가 아니다.
       상세 출처(상품설명서 / 약관·쪽수)는 감사 로그에 남겨 운영·검수에서 확인한다(v8.38)."""
    for r, rid, _t, k in rs:
        if k == 'paper':
            S.log('금액근거', r['name'], '이 상품설명서의 담보별 지급금액 표 그대로')
        elif k == 'book':
            x = ls_src(rid)
            if x: S.log('금액근거', r['name'], '상품설명서에 항목표가 없어 같은 담보의 %s p.%d 지급금액표 기준(서로 다른 상품 약관에서 같은 표임을 대조)' % (ls_bookname(x[0]), x[1]))
    return '<div class="mnote">※ 자세한 특약의 이해는 해당 상품의 약관 참조 확인 바랍니다.</div>' if rs else ''

def v3note():
    """설계서 뒤쪽 「특약 안내사항」 표와 대조한 결과 한 줄 — 모두 맞을 때만 적는다(v8.41)"""
    ok = [x for x in V3 if x.get('일치') is True]
    bad = [x for x in V3 if x.get('일치') is False]
    if bad:
        return ('<div class="mnote">※ 이 설계서 뒤쪽 「특약 안내사항」 표와 금액이 다른 담보가 있어요 — '
                + ' · '.join(x['담보'][:24] for x in bad[:2]) + '. 약관을 확인해 주세요.</div>')
    if not ok:
        return ''
    pg = ' · '.join('p.%d' % n for n in sorted({x['쪽'] for x in ok}))
    return ('<div class="mnote">※ 위 금액은 이 설계서 뒤쪽 「특약 안내사항」 표(%s · 담보 %d개)와 '
            '항목·금액·연간 한도까지 모두 같은지 확인했어요.</div>' % (pg, len(ok)))

def page_itc():
    its = [r for r in RID if r.get('itc')]
    _ir, _ii = inj_itc_rider()                  # 상해 통합치료비는 itc 키가 없어 따로 끌어온다
    if _ir and _ii:
        _ir = dict(_ir); _ir['itc'] = 'inj'; its = its + [_ir]
    if not its:
        return '<div class="ic2">통합치료비 담보 미가입</div>'
    its.sort(key=lambda r: (ITC_ORDER.get(r['itc'], 99), -r['man']))    # 암 → 순환계 → 질병 → 상해
    total = sum(r['man'] for r in its)
    ck = lambda r: K[next((g[0] for g in ITC_GROUPS if r['itc'] in g[3]), 'pr')]
    top = ''.join(f'<div class="itcr" style="background:{ck(r)[2]}">'
                  f'<b>{itc_name(r)[0]}</b><span>{itc_name(r)[1]}</span>{big(r["man"], ck(r)[1])}</div>' for r in its)
    sections = ''; no = 0; hh = []
    for k, ic, title, ids in ITC_GROUPS:
        rs = [r for r in its if r['itc'] in ids]
        if not rs: continue
        items = {}
        for r in rs:
            for lbl, a, c, p in itc_amounts(r):
                key = re.sub(r'\((급여|비급여[^)]*)\)', '', lbl).strip()
                d = items.setdefault(key, {'amt': 0, 'c': c, 'p': p, 'nc': '비급여' in lbl, 'n': 0})
                d['amt'] += a; d['n'] += 1
        srt = sorted(items.items(), key=lambda x: -x[1]['amt'])
        cards = ''; chips = ''
        for n_i, (key, d) in enumerate(srt):
            freq = {'y': '연간 1회', 'o': '받을 때마다', 'd': '1일 1회'}.get(d['p'], '연간 1회')
            if n_i < (10 if k == 'ca' else 5):
                sub = f'{d["c"]} · {"비급여" if d["nc"] else "급여"} · {freq}' + (' · 합산' if d['n'] > 1 else '')
                cards += f'<div class="itci2"><b>{key[:15]}</b><span>{sub}</span>{big(d["amt"],K[k][1])}</div>'
            else:
                chips += f'<span class="itcchip"><b>{key[:14]}</b>{won(d["amt"])}</span>'
        cap = sum(r['man'] for r in rs)
        hh.append(26 + -(-min(len(srt), 10 if k == 'ca' else 5) // 5) * 40 + (17 if chips else 0))   # 이 묶음이 차지하는 세로 어림(pt)
        no += 1
        sections += f'''<div class="itcsec">{tabhd(no, k, title, f'가입 {len(rs)}개 · 연간 한도 합계 {won(cap)} · 항목별 약관 금액(1년 경과 후)')}
          <div class="itcgrid">{cards}</div>{f'<div class="itcchips">{chips}</div>' if chips else ''}</div>'''
    extra = itc_filler(its, no) if len(its) <= 2 else ''       # 통합치료비가 1~2개뿐이면 남는 지면을 치료 흐름·설명으로 채운다(v8.13)
    h = 50 + sum(hh) + 44 + (240 if extra else 0)              # 지면 높이 어림(pt) — 아래 블록을 붙일 자리가 있는지 보는 용도
    lsm = ls_mini() if not extra else ''
    if lsm and h + LS_MINI_H > LS_ROOM:                        # 통합치료비가 많아 자리가 없으면 통째로 뺀다(v8.37)
        for r, _rid, _it, _k in ls_riders():
            S.log('지면생략', r['name'], '통합치료비 지면에 자리가 없어 항목표는 싣지 않음(금액 계산에는 그대로 들어감)')
        lsm = ''
    return f'''<div class="itctop"><div class="itcrs">{top}</div><div class="itctot"><span>통합치료비 연간 한도 합계</span>{big(total,'#C92A2A')}<em>해마다 새로 적용 · 담보별 한도는 각각</em></div></div>
 {sections}{extra}{lsm}
 {v3note()}
 <div class="tip">{e('bulb','#D9480F')}<span>통합치료비는 <b>진단금과 별개</b>로 실제 받은 치료 항목마다 지급돼요. 검사·주요치료는 <b>항목별 연간 1회</b>, 수술은 <b>수술할 때마다</b>, 재활은 <b>1일 1회</b>이고, 한 해 합계는 가입금액까지 · <b>해마다 새로</b> 적용돼요. 계약 후 1년 이내에는 항목 금액과 연간 한도가 50%로 적용되는 담보가 있어요.</span></div>'''

# ── 수술비 세부보장 ────────────────────────────────
def page_surg():
    """모든 수술비를 종(1~5종)·원인·병원 종별로 합산 표기 + 연간 2회 이상(plus) 별도"""
    d = K['pr'][1]; tl = K['pr'][3]
    # 이 표는 **1-5종 수술분류표로 종을 가려 지급하는 담보만** 합산한다(v8.27).
    # 종과 무관하게 정액으로 나오는 질병·상해수술비, 질병군 수술비(131대 등)를 섞으면
    # 1종부터 5종까지 금액이 똑같아져 '종별 지급금액' 표의 뜻이 사라진다. 그것들은 아래에 따로 적는다.
    G5RULE = ('surg_grade_1_5',)
    def S5(j, cause, hosp, cnt=1):
        L = Q('Z99', dict(cause=cause, surg=j, hosp=hosp, grp=[], surg_cnt=cnt),
              [['수술', '%d종 수술' % j, '', ['surg'], {'j': j}]])
        return [x for x in L if x.get('rule') in G5RULE or x.get('group') == '통합치료비']
    def FLAT(cause, hosp):
        """종과 무관하게 나오는 수술비(정액) — 위 표 금액에 더해진다"""
        L = Q('Z99', dict(cause=cause, surg=1, hosp=hosp, grp=[], surg_cnt=1), [])
        return [x for x in L if x.get('rule') not in G5RULE and x.get('group') != '통합치료비']
    cols = ''.join(f'<th>{et(ic,tl,24,d)}<b>{j}종 수술</b><span>{s2}</span></th>'
                   for j, ic, s2 in [(1, 'bandage_adhesive', '내시경·간단 수술'), (2, 'syringe', '복강경·관혈 수술'),
                                     (3, 'knife', '내시경·카테터 암수술 · 갑상선'), (4, 'surgical_sterilization', '위·간·장 개복 절제'),
                                     (5, 'heart_organ', '암 근치수술 · 이식 · 개두 · 심장')])
    def row(label, cause, hosp, cnt=1, hl=False):
        vals = [T(S5(j, cause, hosp, cnt)) for j in range(1, 6)]
        if not any(vals): return ''                      # 1-5종 담보가 없는 원인은 빈 줄을 만들지 않는다(v8.27)
        cells = ''.join(f'<td>{big(v,d if hl else "#343A40")}</td>' for v in vals)
        return f'<tr class="{"mhl" if hl else ""}"><th class="rl">{label}</th>{cells}</tr>'
    dc = '질병' if F['surg'] else '상해'
    detail = ''.join(f'<td class="dt">{det(S5(j,dc,"상급종합"))}</td>' for j in range(1, 6))
    parts = []; no = 0                                    # 설계에 없는 블록은 빠진다(v8.4)
    if F['day'] or F['care']:
        no += 1; parts.append(tabhd(no,'ms','입원 · 간병','14일 입원 예시 · 상급종합병원은 종합병원 담보도 함께 지급 · 한도일수 담보별 적용') + f'<div class="stay">{stay_cards()}</div>')
    if F['surg'] or F['inj_surg']:
        no += 1
        trs = (row('질병 · 모든 병원', '질병', '모든') + row('질병 · 상급종합병원', '질병', '상급종합', hl=True) if F['surg'] else '') + \
              (row('상해 · 모든 병원', '상해', '모든') + row('상해 · 상급종합병원', '상해', '상급종합', hl=not F['surg']) if F['inj_surg'] else '')
        fl = []
        for cz, on in (('질병', F['surg']), ('상해', F['inj_surg'])):
            if not on: continue
            L = FLAT(cz, '상급종합'); v = T(L)
            if v > 0: fl.append(f'<b>{cz} {man(v)}만원</b> ({det(L, 4).replace("<br>", " · ")})')
        fnote = ('<div class="mnote"><b>종과 상관없이 더해지는 수술비</b> — 상급종합 기준 ' + ' / '.join(fl) +
                 '. 위 표 금액에 <b>더해</b> 지급돼요.</div>') if fl else ''
        gnote = '<div class="mnote">※ 131대(130대)질병수술비 등 질병군 담보는 아래와 같이 <b>위 금액에 더해</b> 지급돼요.</div>'
        if trs:                                          # 1-5종 담보가 있을 때만 종별 표를 그린다(v8.27)
            parts.append(tabhd(no,'pr','수술 종별 지급금액 — 1-5종 수술비 계열','약관 [1-5종 수술분류표Ⅱ]로 종을 가려 지급하는 담보만 · 수술할 때마다 다시 지급') + f'''
 <table class="mx"><thead><tr><th class="rl"></th>{cols}</tr></thead><tbody>{trs}
   <tr class="dtr"><th class="rl">주요 지급 담보<br><span>{dc} · 상급종합</span></th>{detail}</tr></tbody></table>
 <div class="mnote">※ 같은 수술로 1-5종 수술비는 가장 높은 종 1가지만 지급돼요. 질병 통합치료비도 1-5종 분류표를 쓰므로 함께 넣었어요.</div>{fnote}{gnote}''')
        else:
            parts.append(tabhd(no,'pr','수술비 — 수술 종과 상관없이 정액 지급','이 설계에는 1-5종 수술분류표로 종을 가리는 담보가 없어요') + fnote + gnote)
    pc = plus_cards()
    if pc:
        no += 1; parts.append(tabhd(no,'pr','연간 2회 이상 수술하면 — 1-5종 수술비(plus)','한 해에 두 번째 수술부터 가장 높은 종 기준으로 연간 1회 더') + f'<div class="plus5">{pc}</div>')
    gs = group_surg()
    if gs:
        no += 1; parts.append(tabhd(no,'cv','질병군별 추가 수술비','해당 질병으로 진단확정되고 수술하면 위 수술비에 더해 지급') + f'<div class="gsurg">{gs}</div>')
    return ''.join(parts) + g17_block(no + 1)

def g17_block(no=5):
    """1-7종 수술비(약관 별표30 기준) 종별 가입금액 — 가입한 설계에만 표시"""
    rows = {}
    for r in RID:
        rl = S.classify(r['name'])
        if not rl or rl['id'] not in ('surg_grade_1_7', 'surg_grade_1_7_row'): continue
        tk = S.tokens(S.nname(r['name']))
        if tk['gj'] and tk['cause']: rows.setdefault(tk['cause'], {})[tk['gj']] = max(rows.get(tk['cause'], {}).get(tk['gj'], 0), r['man'])
    if not rows: return ''
    out = ''
    for cause, k in [('질병', 'pr'), ('상해', 'ms')]:
        if cause not in rows: continue
        cells = ''.join('<div class="pc"><b>%d종</b>%s</div>' % (j, big(rows[cause].get(j, 0), K[k][1]) if rows[cause].get(j) else '<span class="z">미가입</span>') for j in range(1, 8))
        out += f'<div class="prow p7"><span style="color:{K[k][1]}">{cause} 수술</span>{cells}</div>'
    ex = ''
    if S.SURG7:                                        # 분류표(surg7.json) 종별 대표 수술 — 데이터에서 읽는다(v8.5)
        pick = {7: ['A010', 'B031', 'F041'], 6: ['G071', 'E012', 'J062'], 5: ['G091', 'B027', 'H043'], 4: ['H107', 'F121', 'K064'],
                3: ['G212', 'I032', 'I282'], 2: ['B174', 'N031', 'C091'], 1: ['C061', 'G272', 'G523']}
        parts = []
        for j in range(1, 8):
            nm = [re.sub(r'\(.*?\)|,.*$', '', S.SURG7[c]['name']).strip()[:14] for c in pick[j] if c in S.SURG7]
            if nm: parts.append(f'<b>{j}종</b> ' + '·'.join(nm))
        ex = '<div class="mnote">※ 종별 대표 수술(1-7종 수술분류표 630개 수술코드 기준) — ' + ' &nbsp;/&nbsp; '.join(parts) + '</div>'
    return tabhd(no, 'cv', '1-7종 수술비 — 종별 지급금액(1-7종 수술분류표 기준)', '1-5종 수술분류표와 종이 달라요 · 위 표·다빈도·사례의 종은 분류표 수술코드로 판정') + f'<div class="plus5">{out}</div>{ex}'

def plus_cards():
    """1-5종 수술비(plus) 종별 가입금액 — 질병 · 상해 각각. 가입 담보가 없으면 빈 문자열(블록 생략, v8.4)"""
    if not any('1-5종수술비(plus)' in r['name'].replace(' ', '') for r in RID): return ''
    out = ''
    for cause, k in [('질병', 'pr'), ('상해', 'ms')]:
        cells = ''
        for j in range(1, 6):
            v = 0
            for r in RID:
                nm2 = r['name'].replace(' ', '')
                if '1-5종수술비(plus)' in nm2 and cause in nm2 and ('(%d종' % j) in nm2: v = max(v, r['man'])
            cells += '<div class="pc"><b>%d종</b>%s</div>' % (j, big(v, K[k][1]) if v else '<span class="z">미가입</span>')
        out += f'<div class="prow"><span style="color:{K[k][1]}">{cause} 수술</span>{cells}</div>'
    return out

def group_surg():
    """131/130대질병수술비 등 질병군 담보를 그룹명과 함께 표기"""
    it = []
    for r in RID:
        nm2 = r['name'].replace(' ', '')
        if '대질병수술비' in nm2 or '5대질환' in nm2 or '32대질병' in nm2:
            g = (r.get('benefit') or r.get('sub') or '').strip()
            if not g:                                     # 세부 특약에 바로 매칭된 행 : [세부보장]을 먼저, 없으면 (괄호) (v8.11)
                m2 = re.search(r'\[([^\[\]]+)\]', r['name']) or re.search(r'\(([^()]+)\)', r['name'])
                g = m2.group(1) if m2 else r['name']
            if not g.strip(): g = re.sub(r'\d+대질병수술비|수술비', '', r['name']).strip('()[] ') or r['name']
            it.append((g, r['man']))
    if not it: return ''
    it.sort(key=lambda x: -x[1])
    return ''.join(f'<div class="gs"><b>{g[:16]}</b>{big(v,K["cv"][1])}</div>' for g, v in it)

# ── 담보 전체 (질병 단위 태그) ─────────────────────
TAGRULE = [('암', ['cancer_dx', 'cancer_tx', 'cancer_etc']), ('뇌·심장', ['brain', 'heart']),
           ('통합치료비', ['integrated']), ('수술', ['surgery', 'special', 'disease_etc']),
           ('입원·간병', ['hospital', 'nursing']), ('상해·사망', ['death', 'disability', 'injury'])]
def tag_of(r):
    c = r.get('cat') or ''
    for nm, cats in TAGRULE:
        if c in cats: return nm
    if r.get('itc'): return '통합치료비'
    for kw, nm in [('암', '암'), ('뇌', '뇌·심장'), ('심장', '뇌·심장'), ('입원', '입원·간병'), ('간병', '입원·간병'), ('수술', '수술'), ('상해', '상해·사망')]:
        if kw in r['name']: return nm
    return '기타'
CARE_USE = ('요양제외', '요양병원', '하루')          # 간병인사용일당 표기 순서
def _care_sum():
    """간병 관련 담보 요약 — 간병인지원(현물) · 간호간병통합 · 간병인사용(요양병원 구분별)

    간병인사용일당은 간병인지원일당과 동시에 설계할 수 없고, 보통
    (요양병원제외) · (요양병원) 두 담보를 금액을 달리해 한 세트로 가입한다(v8.29).
    """
    nm = lambda r: r['name'].replace(' ', '')
    isnano = lambda n: ('간호·간병통합' in n or '간호간병통합' in n)
    sup = any('간병인지원' in nm(r) for r in RID)
    nano = max([r['man'] for r in RID if isnano(nm(r))] or [0])
    # 간병인지원일당은 '간병인 현물 지원'과 '가입금액만큼의 입원일당' 중 하나를 고르는 구조다
    #   (약관 제1항 입원 1일당 가입금액 지급 · 제2항 간병인을 원하면 그 대신 간병인을 보내고 제1항은 지급하지 않음).
    # Ⅶ형처럼 간병인만 보내는 담보는 가입금액이 0으로 찍히므로, 0이 아닐 때만 '미사용 시' 금액을 밝힌다.
    # 같은 간병인지원이어도 (간호·간병통합서비스 사용추가보장)형은 간호·간병통합서비스를 쓴 날에만
    # 지급하는 담보라(약관 제1조) 이 금액에서 뺀다 — 그쪽은 nano 로 따로 센다.
    supday = max([r['man'] for r in RID if '간병인지원' in nm(r) and not isnano(nm(r))] or [0])
    use = {}
    for r in RID:
        n = nm(r)
        if '간병인사용' not in n: continue
        k = '요양제외' if re.search(r'요양[^)]*병원제외', n) else ('요양병원' if '(요양병원)' in n else '하루')
        use[k] = max(use.get(k, 0), r['man'])       # 상해·질병 같은 금액이라 큰 쪽 하나만 쓴다
    return sup, supday, nano, use

def summary_cards():
    """3대 진단 · 수술 · 입원/간병 한눈 요약 (질병 단위 합산금액)"""
    ca = T(Q('C16', dict(dx='cancer', cause='질병', grp=[]), []))
    cv = T(Q('I63', dict(dx='brain', cause='질병', grp=['뇌혈관질환']), []))
    ht = T(Q('I21', dict(dx='heart', cause='질병', grp=['심장질환']), []))
    sg = T(Q('Z99', dict(cause='질병', surg=5, hosp='상급종합', grp=[]), []))
    day = T(Q('Z99', dict(cause='질병', hosp='상급종합', room='1인실', days=1, grp=[]), []))
    sup, supday, nano, use = _care_sum()
    # ── 간병 카드(v8.30) ──────────────────────────────────────────────
    # 큰 자리는 '간병을 누가·얼마로 받는가'만 쓴다 : 간병인지원(현물) > 간병인사용(요양 구분별 두 줄).
    # 간호·간병통합병실은 두 담보 어느 쪽과도 세트로 설계하는 일이 많아 큰 자리를 차지하면 안 된다
    #   → 아래 작은 글씨로만 적는다(간병인지원·간병인사용이 둘 다 없을 때만 큰 자리로 올라온다).
    # 일반 입원일당은 소제목이 금액까지 말하므로 큰 자리에서 되풀이하지 않는다
    #   → 간병 담보가 하나도 없는 설계에서만 '조건(소제목) + 금액(큰 자리)' 꼴로 쓴다.
    MS = K['ms'][1]
    one = lambda t: f'<span class="n2" style="color:{MS}">{t}</span>'
    DAYC = '상급종합병원 1인실 하루 기준'
    s2 = (f'{DAYC} {won(day)}' if day else '입원일당 미가입')      # 간병 담보가 큰 자리를 쓸 때의 소제목
    usebox = False
    if sup:
        care = one('간병인 지원')
    elif use:                                        # v8.29 — 요양병원 제외 / 요양병원을 각각 한 줄로
        usebox = True
        rows = ''.join(f'<i>{k}</i><u>{num(use[k])}</u>' for k in CARE_USE if use.get(k))
        care = f'<span class="crh">간병인사용</span><span class="cr2" style="color:{MS}">{rows}</span>'
    elif nano:
        care = one(f'하루 {won(nano)}')
    else:                                            # 간병 담보가 없는 설계 — 다른 카드처럼 조건(소제목) + 금액(큰 자리)
        care, s2 = (big(day, MS) if day else one('미가입')), (DAYC if day else '입원일당 미가입')
    caresub = []
    if sup: caresub.append('간병인지원' + (f'(미사용 시 하루 {won(supday)})' if supday else ''))
    if use and not usebox: caresub.append('간병인사용 ' + ' · '.join(f'{k} {won(use[k])}' for k in CARE_USE if use.get(k)))
    if nano: caresub.append(f'간호간병통합병실 {won(nano)}')
    dxnote = lambda v: '진단비 합산' if v > 0 else '진단비 미가입 · 수술·치료 담보로 보장'
    cards = [(F['cancer'], 'cancerous_cell_nuclei', 'ca', '암 진단', '암(유사암제외) 진단확정 시', big(ca, K['ca'][1]), dxnote(ca)),
             (F['brain'], 'neurology', 'cv', '뇌혈관 질환', '뇌경색·뇌출혈 진단확정 시', big(cv, K['cv'][1]), dxnote(cv)),
             (F['heart'], 'heart_organ', 'yr', '심혈관 질환', '급성심근경색 진단확정 시', big(ht, K['yr'][1]), dxnote(ht)),
             (F['surg'] or F['inj_surg'], 'knife', 'pr', '수술', '질병 5종 수술 1회(상급종합)', big(sg, K['pr'][1]), '모든 수술비 합산'),
             (F['day'] or F['care'], 'nurse', 'ms', '입원 · 간병',
              s2, care,
              ' · '.join(caresub) or ('간병인을 직접 고용한 날 지급' if use else ('간병 담보 미가입' if day else '입원일당 · 간병 담보 미가입')))]
    cards = [c for c in cards if c[0]]                   # 설계에 없는 계열 카드는 빠진다(v8.4)
    html = ''
    for on, ic, k, t, s2, v, note in cards:
        # 아이콘과 이름을 한 줄로(v8.31) — 카드가 위아래로 짧아진다
        html += (f'<div class="sc" style="background:{K[k][2]}">'
                 f'<div class="sh">{et(ic,"#fff",19,K[k][1])}<b>{t}</b></div>'
                 f'<span>{s2}</span>{v}<em>{note}</em></div>')
    return f'<div class="sum5" style="grid-template-columns:repeat({max(len(cards),1)},1fr)">{html}</div>'

def page_all():
    g = {}
    for r in RID: g.setdefault(tag_of(r), []).append(r)
    blocks = ''
    for nm, _ in TAGRULE + [('기타', [])]:
        rs = g.get(nm) or []
        if not rs: continue
        k = {'암': 'ca', '뇌·심장': 'cv', '통합치료비': 'yr', '수술': 'pr', '입원·간병': 'ms', '상해·사망': 'pk'}.get(nm, 'pr')
        d = K[k][1]
        cut = 30 if len(RID) <= 80 else 19
        items = ''.join(f'<span class="al"><i>{r["no"]}</i>{r["name"][:cut]}<b>{man(r["man"])}</b>{cutmark(r["name"], 1)}</span>' for r in sorted(rs, key=lambda x: (x.get('no') or 0)))
        blocks += f'''<div class="ablk"><div class="ah" style="color:{d}"><span class="adot" style="background:{d}"></span>{nm}<em>{len(rs)}개 · 합계 {won(sum(x["man"] for x in rs))}</em></div><div class="ag">{items}</div></div>'''
    return f'''{blocks}
 <div class="tip">{e('bulb','#D9480F')}<span>{'<b>가입금액 뒤 회색 %% 표시</b>는 계약 1년이 지나기 전에는 그 비율만 지급된다는 뜻이에요(%d개 담보). · ' % len(CUT) if CUT else ''}<b>지급 기준 요약</b> · 진단비는 최초 1회 · 수술비는 수술할 때마다(1~5종은 동시 수술 시 가장 높은 종 1가지) · 통합치료비는 항목별 연간 1회, 연간 한도는 가입금액까지 해마다 새로 적용 · 입원일당은 병원 종별·병실 종류·한도일수 조건 충족 시 지급 · 131대질병수술비 등 일반 질병 담보는 <b>암·유사암에는 지급되지 않아요</b>.</span></div>'''

# 사례 지면 주석 — 통합생활지원비는 '달' 단위 담보라 단계별 계산의 한계를 밝혀 둔다(v8.37)
LSNOTE = ('<div class="mnote">※ 통합생활지원비는 <b>산정특례 등록·치료를 받은 달</b>마다 항목별로 지급되고, 한 달 합계는 가입금액까지예요. '
          '위 표는 단계마다 그 달의 지급액을 적은 것이라, 여러 단계가 <b>같은 달</b>에 몰리면 그 달 합계는 가입금액까지로 줄어요. '
          '전신마취는 <b>기본(급여)</b> 금액으로만 계산했어요 — 수술이 4시간·6시간 이상이면 더 커져요.</div>') if F['ls'] else ''

_BUILD = [
 lambda: f'''<div class="lg">{e('coins','#E03131')}<b>{C['insured'] if C['insured'].endswith('고객님') else C['insured'] + ' 고객님'} 보장 한장요약</b><span class="sub">가입 담보 {len(RID)}개 · 월 보험료 {C['premium']} · 3대 진단 · 수술 · 입원/간병 요약</span></div>
 {summary_cards()}<div class="{'dense' if len(RID) > 80 else ''}">{page_all()}</div>''',
 lambda: f'''<div class="lg">{e('cancerous_cell_nuclei','#E03131')}<b>암 세부보장</b><span class="sub">진단 · 수술 · 항암약물 · 방사선 — 어느 담보에서 얼마가 나오는지</span></div>
 {page_cancer()}''',
 page_cv,
 lambda: f'''<div class="lg">{e('neurology','#364FC7')}<b>뇌·심혈관 질병코드 지도</b><span class="sub">담보마다 어디까지 보장되는지 질병코드로 한눈에</span></div>
 {page_dzmap()}''',
 lambda: f'''<div class="lg">{e('money_bag','#C92A2A')}<b>통합치료비 한눈에</b><span class="sub">암 · 뇌심장 · 암전후 통합치료비 — 치료 항목별로 얼마가 나오는지</span></div>
 {page_itc()}''',
 lambda: f'''<div class="lg">{e('knife','#087F5B')}<b>수술비 · 입원일당 세부보장</b><span class="sub">모든 수술비 합산 · 종별 · 병원 종별 비교 · 입원 · 간병</span></div>
 {page_surg()}''',
 lambda: f'''<div class="lg">{e('stethoscope','#087F5B')}<b>다빈도 질환 수술 시뮬레이션</b><span class="sub">건강검진·일상에서 자주 생기는 질환 10종 · 병원 종별 비교</span></div>
 <div class="frows">{freq_rows()}</div>
 <div class="tip">{e('bulb','#D9480F')}<span>수술 종(1~5종)은 약관 [1-5종 수술분류표Ⅱ] 기준이며, 비급여 치료비는 병원·술식에 따라 달라지는 실제 치료비 범위(참고용)예요. 표시 금액은 해당 수술 1회 기준 지급 예시예요.</span></div>
 <div class="mnote">※ 질환 선정 근거 : 주요수술 통계연보(국민건강보험공단, 2023) 다빈도 수술 · 국가암등록통계(2023) · 수술 종은 약관 별표 수술코드로 판정 — 상세 근거표(scenario_sources) 별첨</div>''',
 lambda: f'''<div class="lg">{e('money_bag','#5F3DC4')}<b>사례로 보는 치료비 보장</b><span class="sub">치료 단계별로 어느 담보에서 얼마가 나오는지</span></div>
 {''.join(flow_card(f) for f in pick_cases())}
 {LSNOTE}
 <div class="mnote">※ 조건부 담보는 보수적으로 계산 — 표적항암약물허가치료비는 연간 약물종류 2종 이상(폐암 사례 : 표적항암제 → 키트루다), 특정혈전치료비는 두 치료를 모두 받은 단계에서만.</div>
 <div class="mnote">※ 사례 근거 : 사망원인통계(국가데이터처, 2024) · 국가암등록통계(2023) · 치료 단계는 국가암정보센터·대한심장학회·대한뇌졸중학회 진료지침 · 입원일수는 예시 — 상세 근거표(scenario_sources) 별첨</div>''',
]
# 6쪽 : 상해·사고
INJ = [('교통사고 두개내손상', 'S06', 'wound', dict(cause='상해', surg='59', surg7='B122', hosp='종합', room='2-3인실', days=20, icu=3, grp=[]),
        [['진단', 'CT + MRI', '', ['x_ct', 'x_mri']], ['수술', '개두술', '', ['surg'], {'j': 5}], ['중환자', '중환자실', '', ['icu']], ['재활', '재활 10일', '', ['rehab'], {'n': 10}]]),
       ('손목 골절 · 관절 고정술', 'S62', 'body', dict(cause='상해', surg='13-2', surg7='I286', hosp='종합', room='2-3인실', days=5, grp=[]), []),
       ('열린 상처 · 창상봉합술', 'T14', 'bandage_adhesive', dict(cause='상해', surg=1, surg7='X060', hosp='종합', room=None, days=0, grp=[]), []),
       ('화상 · 피부이식수술', 'T30', 'wound', dict(cause='상해', surg='2', surg7='Y020', hosp='종합', room='2-3인실', days=7, grp=[]), [])]
INJ_ITC = json.load(open(os.path.join(BASE, 'inj_itc.json'), encoding='utf-8'))
INJ_ACT = {'MRI': 'x_mri', 'CT': 'x_ct', '골밀도': 'x_bmd', '흡인': 'aspir', '신경차단': 'block', '화상처치': 'burn', '도수정복': 'reduction',
           '창상봉합술치료(안면부,': 'suture_face', '창상봉합술치료(안면부이외': 'suture', '깁스': 'cast', '부목': 'splint', 'CRRT': 'crrt',
           '인공호흡기': 'vent', '저체온': 'hypo', '체외순환': 'ecmo', '전신마취': 'anes6', '중환자실': 'icu', '입원상해재활': 'rehab_in', '외래상해재활': 'rehab_out'}
def inj_itc_rider():
    for r in RID:
        for k, tiers in INJ_ITC.items():
            if S.nname(k) in (S.nname(r['name']), S.noren(r['name'])) and str(r['man']) in tiers: return r, tiers[str(r['man'])]
    return None, None
def inj_itc_pay(items, acts, surg=None, rehab=0):
    """상해 통합치료비 — 시나리오 행위(acts)·수술 종·재활 일수로 항목별 지급액 계산"""
    out = []
    for it in items:
        l = it['l']
        if it['c'].startswith('수술'):
            j = int(l[0]);  amt = it['amt'] if surg == j else 0
        elif '재활' in l: amt = it['amt'] * rehab if ('rehab_in' in acts if '입원' in l else 'rehab_out' in acts) else 0
        else:
            key = next((v for k, v in INJ_ACT.items() if k in l), None)
            amt = it['amt'] if key and key in acts else 0
        if amt: out.append((l, amt))
    return out
INJ_CASES = [('교통사고 두개내손상', 'ambulance', ['x_ct', 'x_mri', 'icu', 'vent', 'anes6', 'rehab_in'], 5, 10, '검사 → 개두수술(5종) → 중환자실·인공호흡기 → 입원 재활 10일'),
             ('손목 골절 · 관절 고정술', 'body', ['x_ct', 'reduction', 'cast'], 2, 0, '도수정복 후 고정술(2종) · 깁스'),
             ('열린 상처 · 창상봉합술', 'bandage_adhesive', ['suture', 'aspir'], 1, 0, '창상봉합술(1종) · 흡인·절개'),
             ('화상 · 피부이식수술', 'wound', ['burn', 'rehab_out'], 1, 5, '화상처치 · 피부이식(1종) · 외래 재활 5회')]
def inj_itc_block(no=2):
    r, items = inj_itc_rider()
    if not r: return ''
    cards = ''
    for nm, ic, acts, j, rh, desc in INJ_CASES:
        pays = inj_itc_pay(items, set(acts), j, rh)
        tot = sum(a for _, a in pays)
        chips = ''.join(f'<span class="fi">{l[:16]}<b>{man(a)}</b></span>' for l, a in sorted(pays, key=lambda x: -x[1])[:6])
        cards += f'''<div class="frow">{et(ic,K['yr'][3],22,K['yr'][1])}<div class="fnm"><b>{nm}</b><em>{desc}</em></div>
          <div class="fitems">{chips or '<span class="fi none">해당 항목 없음</span>'}</div><div class="fpay"><div><span>통합치료비</span>{big(tot,K['yr'][1])}</div></div></div>'''
    top = ''.join(f'<span class="itcchip"><b>{it["l"][:14]}</b>{won(it["amt"])}</span>' for it in sorted(items, key=lambda x: -x['amt'])[:10])
    return (tabhd(no, 'yr', '상해 통합치료비 항목별 내역', f'위 사고 예시 합계에 들어간 금액의 내역 · {r["name"]} {won(r["man"])} · 약관 지급금액표 · 검사·주요치료 연간 1회, 수술은 수술마다, 재활 1일 1회')
            + f'<div class="frows">{cards}</div><div class="itcchips">{top}</div>')

# ── 체증형 담보 — 수술 회차가 늘수록 지급액이 올라간다(v8.33) ──────────────
# 약관(예 : 통합간편 p227 암수술비(25%체증형) · p1660 뇌혈관질환수술비Ⅱ(25%체증형))
#   1년 경과 후 1회차 100% → 2회차 125% → 3회차 150% → 4회차 175% → 5회차 이후 200%
# 담보명의 '(25%체증형)' 에서 체증폭을 읽으므로 상품이 달라도 그대로 쓴다.
ESC = re.compile(r'\((\d+(?:\.\d+)?)%체증형\)')
def esc_rows():
    out = []
    for r in RID:
        m = ESC.search(r['name'].replace(' ', ''))
        if m and r['man'] > 0:
            nm = re.sub(r'\s*\(\s*\d+(?:\.\d+)?\s*%\s*체증형\s*\)', '', r['name']).strip()
            out.append((nm, float(m.group(1)), r['man']))
    return sorted(out, key=lambda x: -x[2])[:3]

def esc_block(no):
    """체증형 담보 — 회차별 지급 비율 한 줄 + 해당 담보 목록 한 줄 (마지막 지면, v8.33)"""
    rs = esc_rows()
    if not rs: return ''
    pct = rs[0][1]
    LB = ['1회차', '2회차', '3회차', '4회차', '5회차~']
    cells = ''.join('<div class="pc"><b>%s</b><span class="n2" style="color:%s">%g<small>%%</small></span></div>'
                    % (LB[i], K['pr'][1], 100 + pct * i) for i in range(5))
    who = ' · '.join('%s <b>%s</b>' % (nm[:20], won(m0)) for nm, _, m0 in rs)
    return (tabhd(no, 'pr', '수술을 또 받으면 더 올라가요 — 체증형 담보',
                  '같은 담보라도 수술 회차가 늘수록 지급액이 커져요') +
            f'<div class="plus5"><div class="prow esc"><span>지급 비율</span>{cells}</div></div>'
            f'<div class="mnote">※ 이 설계의 체증형 담보 — {who} · 가입금액에 위 비율을 곱해 지급해요'
            f'(계약 1년이 지나기 전에는 그 절반).</div>')


# 보장 시작 안내 칸(v8.34) — 문구를 고정하지 않고 이 설계에서 실제로 감액이 걸린 담보 수를 센다.
# 90일 미만 감액은 걸린 담보가 없으면 칸 자체가 빠진다(암 단독상품 등).
def _tl_cards():
    out = [('계약 즉시', '상해·수술·입원일당 등은 기다리는 기간 없이 1회 보험료를 받은 때부터 보장 (아래 감액은 적용될 수 있어요)', '#EDF2FF')]
    if CUT90:
        r90 = max(set(CUT90.values()), key=list(CUT90.values()).count)
        out.append(('90일 전 %g%%' % (r90 * 100),
                    f'이 설계에서 {len(CUT90)}개 담보는 계약 90일이 지나기 전에 진단·수술을 받으면 가입금액의 {r90 * 100:g}%만 지급돼요',
                    '#FFF5F5'))
    out.append(('90일 후', '암 진단비·암 수술비·암 입원일당·항암치료비 등 암 담보는 계약일부터 90일이 지난 다음날부터 보장', '#FFF0F0'))
    out.append(('1년 경과 전 50%',
                (f'이 설계에서 {len(CUT)}개 담보는 계약 1년 이내 가입금액의 50%만 지급 — 담보 목록과 지급 예시에 <b>1년 내 50%</b>로 표시했어요'
                 if CUT else '일부 담보는 계약 1년 이내 가입금액의 50%만 지급돼요'), '#F3F0FF'))
    out.append(('1년 경과 후 100%', '1년이 지나면 약관 금액 전액 지급 · 연간 한도도 해마다 새로 적용', '#E6FCF5'))
    return out
TL = _tl_cards()


def inj_itc_by_case():
    """사고 유형 → 상해 통합치료비 지급액. 이 담보는 금액표가 따로(inj_itc.json) 있어
       규칙표 계산(pay_lines)에 잡히지 않으므로, 사고 예시 합계에 직접 더해 준다(v8.40)."""
    r, items = inj_itc_rider()
    if not r or not items: return {}, ''
    return ({nm: sum(a for _l, a in inj_itc_pay(items, set(acts), j, rh))
             for nm, _ic, acts, j, rh, _d in INJ_CASES}, r['name'])

def page_inj():
    rows = ''
    iby, inm = inj_itc_by_case()
    for nm, kcd, ic, tg, itc in INJ:
        L = [x for x in Q(kcd, tg, itc) if x['group'] not in ('입원일당', '통원일당')]
        ia = iby.get(nm, 0)
        pos = [(disp(x['name'])[:22] + cutmark(x['name']), x['amt']) for x in L if x['amt'] > 0]
        if ia: pos.append(('상해 통합치료비', ia))
        items = ''.join(f'<span class="fi">{l}<b>{man(a)}</b></span>' for l, a in sorted(pos, key=lambda y: -y[1])) or '<span class="fi none">해당 담보 없음</span>'
        rows += f'''<div class="frow">{et(ic,K['ms'][3],22,K['ms'][1])}<div class="fnm"><b>{nm}</b><span>{kcd}</span><em>상해 치료 예시</em></div>
          <div class="fitems">{items}</div><div class="fpay"><div><span>지급 합계</span>{big(T(L) + ia,'#D9480F')}</div></div></div>'''
    dth = [r for r in RID if '사망' in r['name'] or '후유장해' in r['name']]
    dcard = ''.join(f'<div class="dcard"><b>{r["name"][:26]}</b>{big(r["man"],"#C2255C")}</div>' for r in dth)
    parts = []; no = 0                                    # 설계에 없는 블록은 빠진다(v8.4)
    if F['inj']:
        no += 1; parts.append(tabhd(no,'ms','상해 사고 치료 예시','자주 생기는 사고 유형별로 · 어느 담보에서 얼마가 나오는지') + f'<div class="frows">{rows}</div>')
    ib = inj_itc_block(no + 1)
    if ib: no += 1; parts.append(ib)
    if dcard:
        no += 1; parts.append(tabhd(no,'pk','사망 · 후유장해','상해로 사망하거나 장해가 남았을 때') + f'<div class="dcards">{dcard}</div>')
    return f'''<div class="lg">{e('wound','#D9480F')}<b>상해 · 사고와 사망 · 후유장해</b><span class="sub">다치거나 사고가 났을 때</span></div>
 {''.join(parts)}
 {esc_block(no+1)}
 {tabhd(no+1+(1 if esc_rows() else 0),'cv','보장은 언제부터 시작되나요?','담보별 보장 시작 시점')}
 <div class="tlx" style="grid-template-columns:repeat({len(TL)},1fr)">{''.join(f'<div class="tlc" style="background:{b2}"><b>{t}</b><span>{d2}</span></div>' for t,d2,b2 in TL)}</div>
 <div class="tip">{e('bulb','#D9480F')}<span>상해 담보는 <b>급격하고 우연한 외래의 사고</b>로 인한 경우에만 지급돼요. 질병 담보와 상해 담보는 각각 별도로 지급되며, 같은 사고로 여러 수술을 받으면 1-5종 수술비는 가장 높은 종 1가지만 지급돼요.</span></div>'''
_BUILD.append(page_inj)
# 지면별 표시 조건 — 설계에 없는 계열의 지면은 빠지고, 쪽번호는 실제 생성 쪽수로 매긴다(v8.4)
PAGE_COND = [('보장 한장요약', True),
             ('암 세부보장', F['cancer']),
             ('뇌혈관 · 심혈관 보장', F['brain'] or F['heart']),
             ('뇌·심혈관 질병코드 지도', F['brain'] or F['heart']),
             ('통합치료비 한눈에', F['itc']),
             ('수술비 · 입원일당 세부보장', F['surg'] or F['inj_surg'] or F['day'] or F['care']),
             ('다빈도 질환 수술 시뮬레이션', F['surg']),
             ('사례로 보는 치료비 보장', F['cancer'] or F['brain'] or F['heart']),
             ('상해 · 사고와 사망 · 후유장해', F['inj'] or F['life'] or F['inj_itc'])]
P, SKIPPED = [], []
for (title, cond), fn in zip(PAGE_COND, _BUILD):
    if ATTACH and cond: P.append(fn())
    else: SKIPPED.append(title)
NEW = len(P); TOTAL = C['base_pages'] + NEW

css = open(os.path.join(BASE, 'style.css'), encoding='utf-8').read().replace('__A__', A) + open(os.path.join(BASE, 'extra2.css'), encoding='utf-8').read()
html = '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (
    css, ''.join(f'<section class="page">{header()}<div class="body">{b}</div>{footer(IA+1+i)}</section>' for i, b in enumerate(P)))
open(sys.argv[2], 'w', encoding='utf-8').write(html)
A = S.audit(RID)
A['생성쪽수'] = NEW; A['첨부'] = bool(P); A['제외지면'] = SKIPPED; A['보장계열'] = F
if EXCL: A['제외상품'] = {'상품': EXCL.get('nm') or EXCL['m'], '사유': EXCL['why']}
# 2차 안전장치(v8.22) : 1차(약관+규칙표)로 계산하지 못한 담보에 상품설명서 요약에서 읽은 지급조건을 붙인다
try:
    import desc_engine as DE
    _out = [x['담보'] for x in S.ISSUES]
    A['2차판정'] = [{'담보': r['name'], 'no': r.get('no'), '설명문기준': DE.explain(r.get('desc2') or {}),
                    '별표후보': DE.group_hint(r.get('desc') or '')}
                   for r in RID if r.get('desc2') and r['name'] in _out and DE.explain(r.get('desc2') or {})]
    A['설명문인식'] = C.get('desc_info') or {}
except Exception as _e:
    A['2차판정'] = []
# 3차 안전장치(v8.41) — 설계서 뒤쪽 「특약 안내사항」 표와 우리 금액표를 대조한 결과.
# 출처가 다른 세 번째 눈이라, 다르면 사람이 약관을 다시 봐야 한다는 뜻이다.
A['3차대조'] = V3
for _v in V3:
    if _v.get('오류'):
        S.log('3차대조', '-', '설계서 뒤쪽 표를 읽지 못함 — %s' % _v['오류'][:80]); continue
    if _v.get('일치') is True:
        S.log('3차대조', _v['담보'], '설계서 뒤쪽 특약 안내사항 표(p.%d · %s 기준)와 항목 %d개·연간 한도까지 모두 일치'
              % (_v['쪽'], _v.get('기준', '-'), _v['항목수']))
    elif _v.get('일치') is None:
        S.log('3차대조', _v['담보'], _v.get('사유') or '대조하지 못함')
    else:
        _d = _v.get('차이') or []
        S.log('3차대조', _v['담보'], '설계서 뒤쪽 표(p.%d)와 다름 — %s%s' % (
            _v['쪽'],
            ' · '.join('%s 설계서 %g / 우리 %s' % (k, v, '없음' if o is None else '%g' % o) for k, v, o in _d[:3]),
            ' 외 %d건' % (len(_d) - 3) if len(_d) > 3 else ''))

A['피보험자성별'] = {'M': '남', 'F': '여'}.get(SEX, '미확인(성별 중립 사례)'); A['사례'] = [f['t'] for f in pick_cases()] if P else []
print('ok', len(P), '쪽 · 담보', A['담보수'], '건', A['구조별'])
if not P: print('  [미첨부] 암·뇌·심장·통합치료비 계열 담보가 없어 스마트제안서를 만들지 않습니다(단일상품 등)')
elif SKIPPED: print('  [제외 지면]', ' / '.join(SKIPPED))
if A['미분류']: print('  [미분류]', ' / '.join(A['미분류'][:10]))
for x in S.ISSUES[:10]: print('  [%s] %s — %s' % (x['구분'], x['담보'][:34], x['사유']))
json.dump({'요약': A, '로그': S.ISSUES}, open(os.path.splitext(sys.argv[2])[0] + '_audit.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
