# -*- coding: utf-8 -*-
"""메리츠 GA 스마트 제안서(6쪽) — 설계서 PDF 를 넣으면 GA 양식 PDF 를 만든다.

  python ga_proposal.py 설계서.pdf [결과.pdf] [나이]        # 한 건
  python ga_proposal.py 폴더                                 # 폴더 안 PDF 전부 → 폴더\ga_output\
  윈도우 : make_ga.bat 에 설계서 PDF 를 끌어다 놓는다(여러 개 가능). 그냥 실행하면 ga_input 폴더의 PDF 를 모두 만든다.

· 쪽 구성 : 1 보장 한눈에 · 1-①②③ 합산 계산서(1쪽 칸별 특약) · 2 암 세부 · 3 뇌심 세부 · 4 암치료 세부내역 · 5 뇌·심장 치료 세부내역 · 6 주요 수술비 세부내역
· 금액은 전부 계산 엔진(scen_engine.pay_lines)에 이 설계서의 가입 특약을 넣어 얻는다. 사례 조건(질병코드·수술 분류·병원 종별·
  마취시간·약물 종수)은 아래 정의 그대로이며 가정값이다. 코드·금액을 여기서 만들지 않는다(CLAUDE.md 1·2).
· 캐릭터는 GA 가안 이미지에서 잘라 넣었다(ga_assets). 사내 테스트용.
"""
import os, sys, re, base64, glob, json, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pipeline, build_all as BA, scen_engine as S          # noqa: E402

VERSION = (re.search(r"VERSION\s*=\s*'([^']+)'", open(os.path.join(BASE, 'api.py'), encoding='utf-8').read()) or [None, ''])[1]
BG, HG = ['뇌혈관질환'], ['심장질환']
BASE_T = dict(cause='질병', hosp='상급종합', room=None, days=0, grp=[], dx=None)

def won(v):
    """만원 단위 정수 → '1억 3,640' / '7,000'"""
    v = int(round(v or 0))
    if v == 0: return '0'
    eok, man = divmod(v, 10000)
    if eok and man: return '%d억 %s' % (eok, format(man, ','))
    if eok: return '%d억' % eok
    return format(man, ',')

# ───────── 설계서 읽기 + 공통 계산(한 건마다 load() 가 다시 채운다) ─────────
RID, META, WHO, PRODUCT, PREMIUM, NRID, SHORTP = [], {}, '', '', '', 0, ''
C, DX, BDX, HDX, BDXL, HDXL = {}, {}, [], [], [], []
AUDIT = {}                                      # 마지막 build 의 감사 로그(요약·계산 제외 사유) — 웹 화면 「감사 로그」 탭
def Q(kcd, tags, itc=None):
    return S.pay_lines(RID, {'kcd': kcd, 'tags': tags, 'itc_events': itc or []})
def s(kcd, itc, **kw):
    tg = dict(BASE_T); tg.update(kw); return Q(kcd, tg, itc)
def F(L): return int(round(S.total_by(L, 'first')))
def Y(L): return int(round(S.total_by(L, 'year')))
def E(L): return int(round(S.total_by(L, 'each')))
def dx(kcd, fam, grp=None):
    return Q(kcd, dict(dx=fam, cause='질병', grp=grp or []), [])
def vdx(kcd, fam, grp): return F(dx(kcd, fam, grp))
def vsurgL(hosp):
    b = [(s('I63', [['시술', '혈전용해', '', ['thromb']]], series='brain', hosp=hosp)),
         (s('I63', [['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], hosp=hosp, acts=['thrombectomy'])),             # 혈전제거술만(카테터 수술) — GA 2026-10-02
         (s('I63', [['시술', '혈전용해', '', ['thromb']], ['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], hosp=hosp, acts=['thrombectomy'])),   # 혈전용해 + 혈전제거 합산(코일색전술 칸 대체)
         (s('I67.1', [['시술', '코일 색전술', '', ['surg']]], surg='88-1', surg7='B016', grp=BG + ['특정31대질병'], hosp=hosp, anes=1)),
         (s('I61', [['수술', '혈종제거 개두술', '', ['surg']]], surg='59', surg7='B031', grp=BG + ['뇌졸중', '뇌출혈', '특정31대질병'], hosp=hosp, anes=1))]
    h = [(s('I21', [['시술', '혈전용해', '', ['thromb']]], series='heart', hosp=hosp)),
         (s('I20', [['시술', '스텐트 삽입', '', ['surg']]], surg='88-1', surg7='F133', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp)),
         (s('I48', [['시술', '전극도자절제술', '', ['surg']]], surg='88-1', surg7='F142', grp=HG + ['특정31대질병'], hosp=hosp)),
         (s('I20', [['수술', '관상동맥 우회술', '', ['surg']]], surg='24', surg7='F042', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp, anes=1, anes_h=6))]
    return b, h
def vsurg(hosp):
    b, h = vsurgL(hosp); return [F(x) for x in b], [F(x) for x in h]

def load(design_pdf, age=''):
    """설계서 한 건을 읽어 공통 계산값을 채운다"""
    global RID, META, WHO, PRODUCT, PREMIUM, NRID, SHORTP, C, DX, BDX, HDX, BDXL, HDXL
    S.ISSUES.clear()
    RID = pipeline.read_riders(design_pdf)
    META = BA.auto_meta(design_pdf)
    sex = META.get('sex') or ''
    # 나이는 설계서 본문에서 추정하지 않는다(만기·갱신 나이가 섞여 잘못 읽힘) — 넘겨받은 값만 쓴다
    WHO = '고객님 (%s%s)' % ({'F': '여', 'M': '남'}.get(sex, ''), (' · ' + age) if age else '')
    PRODUCT = re.sub(r'\s+', ' ', META.get('product', '') or '').replace('( ', '(').strip()
    PREMIUM = META.get('premium', '') or ''
    NRID = len(RID)
    SHORTP = (re.split(r'보장보험|건강보험', PRODUCT)[0].replace('(무) 메리츠 ', '').strip() or PRODUCT).replace('%', '%%')
    C = {}
    C['robot'] = s('C16', [['수술', '로봇수술', '', ['surg', 'robot'], {'nc': 1}]], surg='C1', surg7='G081')
    C['lap'] = s('C16', [['수술', '복강경', '', ['surg']]], surg='C1', surg7='G081')
    C['open'] = s('C16', [['수술', '개복', '', ['surg']]], surg='C1', surg7='G082')
    C['endo'] = s('C16', [['수술', '내시경 절제', '', ['surg']]], surg='C2', surg7='G503')
    C['chemo'] = s('C16', [['항암', '항암약물(급여)', '', ['chemo']]], chemo=1)
    C['target'] = s('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=2)
    C['immune'] = s('C16', [['항암', '면역(비급여)', '', ['chemo', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=2)
    # 1쪽 「보장 한눈에」 는 표적·면역 모두 약물 1종(치료 1개)만 받은 것으로 계산한다 — (2종및3종이상)·2종이상 담보는 2쪽 '갯수별 약물' 칸에서만 (GA 요청 2026-10)
    C['target1'] = s('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=1)
    C['immune1'] = s('C16', [['항암', '면역(비급여)', '', ['chemo', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=1)
    # 1쪽 4번째 칸 : 표적+면역 약물 2종을 같은 해 받은 사례 — 항암약물·표적·면역·(2종및3종이상) 담보가 모두 합산된다(GA 요청 2026-10-02 · 카티 칸 대체)
    C['two'] = s('C16', [['항암', '표적+면역(비급여) 2종', '', ['chemo', 'target', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=2)
    C['cart'] = s('C16', [['항암', '카티(비급여)', '', ['chemo', 'target', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=1)
    C['rad'] = s('C16', [['방사선', '항암방사선(급여)', '', ['rad']]])
    C['imrt'] = s('C16', [['방사선', '세기조절', '', ['rad', 'imrt']]])
    C['proton'] = s('C16', [['방사선', '양성자(비급여)', '', ['rad', 'proton'], {'nc': 1}]])
    C['carbon'] = s('C16', [['방사선', '중입자(비급여)', '', ['rad', 'carbon'], {'nc': 1}]])
    DX = {'일반암': dx('C16', 'cancer'), '소액암': dx('C50', 'cancer'), '고액암': dx('C25', 'cancer'), '유사암': dx('C73', 'sim_cancer')}
    BDXL = [dx('I63', 'brain', BG), dx('I67.1', 'brain', BG), dx('I65', 'brain', BG), dx('I61', 'brain', BG)]
    HDXL = [dx('I20', 'heart', HG + ['허혈성심장질환']), dx('I21', 'heart', HG + ['허혈성심장질환']), dx('I48', 'heart', HG), dx('I49', 'heart', HG)]
    BDX = [F(x) for x in BDXL]; HDX = [F(x) for x in HDXL]

def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
CH = {k: b64(os.path.join(BASE, 'ga_assets', 'char_%s.png' % k)) for k in ('p1', 'p4', 'p5')}

def M(v, big=False):
    v = int(round(v)) if v else 0
    return '<b class="v%s%s">%s<i>만원</i></b>' % (' z' if v == 0 else '', ' big' if big else '', won(v))

def itc_itemL(kcd, key, hosp='상급종합', grp=None, fam=None, extra=None):
    tg = dict(cause='질병', hosp=hosp, room=None, days=0, grp=grp or [], dx=fam)
    ev = [['치료', key, '', [key]] + ([extra] if extra else [])]
    return [l for l in Q(kcd, tg, ev) if l.get('group') == '통합치료비']
def itc_item(kcd, key, hosp='상급종합', grp=None, fam=None, extra=None):
    return int(sum(l['amt'] for l in itc_itemL(kcd, key, hosp, grp, fam, extra)))
# 1쪽 뇌·심 4열 : 「특정순환계질환(주요손상및질환) 통합치료비」(엔진 itc 'ms' · 대상 : 고혈압·판막·동맥경화·심정지·외상성 뇌출혈 등 61개) 항목 사례 4개 — 산정특례 칸 대체(GA 2026-10-02)
#   이 특약 줄만 합산한다. 1-5종 종 번호(j)는 1-5종 수술분류표Ⅱ 항목(59 개두술 5종 · 26 심장내 관혈수술 5종 · 22 혈관관혈수술 3종) 기준 가정값.
MS_CASES = [('외상성뇌출혈 수술', dict(kcd='S06.5', ev=[['수술', '혈종제거 개두술', '', ['surg'], {'j': 5}]], tg=dict(cause='상해', surg='59', surg7='B031', anes=1))),
            ('판막질환 수술', dict(kcd='I35', ev=[['수술', '판막치환술', '', ['surg'], {'j': 5}]], tg=dict(surg='26', anes=1))),
            ('동맥경화 수술', dict(kcd='I70', ev=[['수술', '혈관 우회술', '', ['surg'], {'j': 3}]], tg=dict(surg='22', anes=1))),
            ('심정지 중환자실', dict(kcd='I46.9', ev=[['치료', '중환자실', '', ['icu']], ['치료', '부분에크모', '', ['ecmo']]], tg=dict()))]
def msL(case):
    return [l for l in s(case['kcd'], case['ev'], **case['tg']) if l.get('itc') == 'ms']
def ms_has(): return any(r.get('itc') == 'ms' for r in RID)

def rider_man(*keys, exclude=()):
    rs = [r for r in RID if all(k in r['name'] for k in keys) and not any(x in r['name'] for x in exclude)]
    return sum(r['man'] for r in rs) if rs else None

# GA 가안의 시술명 그대로 — 계산 조건(수술 분류표 코드)
GA_DZ = {
 '백내장': ('인공수정체 삽입', 'H25.9', dict(surg='71', surg7='C061', grp=['백내장']), [['수술', '수정체 유화술', '', ['surg'], {'j': 1}]]),
 '디스크': ('신경성형술', 'M51', dict(surg='88-2', surg7='B182', grp=['다빈도62대질병']), [['수술', '신경성형술', '', ['surg'], {'j': 2}]]),
 '치질': ('치핵절제술', 'K64', dict(surg='44', surg7='G272', grp=['치핵']), [['수술', '치핵절제술', '', ['surg'], {'j': 1}]]),
 '담석증': ('복강경수술', 'K80.0', dict(surg='36', surg7='H107', grp=['다빈도62대질병'], anes=1), [['진단', '복부 CT', '', ['x_ct']], ['수술', '복강경 담낭 절제', '', ['surg'], {'j': 2}]]),
 '충수염': ('충수절제술', 'K35', dict(surg='41', surg7='G212', grp=[], anes=1), [['수술', '충수 절제', '', ['surg'], {'j': 2}]]),
 '갑상선 결절': ('고주파절제술', 'D34', dict(surg='88-2', surg7='K080', hc=['PZ612'], grp=['다빈도62대질병']), [['수술', '고주파절제술', '', ['surg'], {'j': 2}]]),   # 보상 확인 : 1-5종 2종(경피적 수술 88-2) · 1-7종 기타 갑상선 수술 1종
 '유방양성종양': ('맘모톰', 'D24', dict(surg='4', surg7='J071', grp=['유방의장애']), [['수술', '맘모톰', '', ['surg'], {'j': 1}]]),
 '자궁근종': ('하이푸', 'D25.9', dict(surg='53', hc=['RZ566'], grp=['다빈도62대질병']), [['수술', '고강도초음파집속술', '', ['surg'], {'j': 1}]]),   # 보상 확인 : 자궁 평활근종(D25.9) 초음파유도하 고강도초음파집속술(RZ566) — 131대(다빈도62대) · 1-5종 1종(53 경질적 자궁 수술)
 '전립선절제술': ('복강경수술', 'N40', dict(surg='50', surg7='M022', grp=['관절염,생식기질환'], anes=1), [['수술', '복강경 전립선절제', '', ['surg'], {'j': 2}]]),
 '골절진단': ('골절수술', 'S52.5', dict(cause='상해', surg='13-2', surg7='I286', grp=[]), [['수술', '골절 고정술', '', ['surg'], {'j': 2}]]),
}
def dzL(name, hosp):
    proc, kcd, tg, itc = GA_DZ[name]
    return s(kcd, itc, **dict(tg, hosp=hosp))

def _ns(x): return re.sub(r'\s+', '', x or '')
def hit(name, keys, exclude=()):
    """담보행 필터 — 띄어쓰기를 지우고 비교한다(또또암 '암통합치료비(기본형)' · 케226 '특정5대 질병 제외' 표기 차이)"""
    n = _ns(name)
    return any(_ns(k) in n for k in keys) and not any(_ns(x) in n for x in exclude)
def rowsum(L, keys, exclude=()):
    return int(sum(l['amt'] for l in L if hit(l['name'], keys, exclude)))
def has(keys, exclude=()):
    return any(all(k in r['name'] for k in ([keys] if isinstance(keys, str) else [])) or any(k in r['name'] for k in (keys if isinstance(keys, (list, tuple)) else [keys]))
               and not any(x in r['name'] for x in exclude) for r in RID)

# ───────── 조각 ─────────
def hl(t): return '<h2><span>%s</span></h2>' % t
def kv(cols):
    n = max(len(r) for _, r in cols)
    th = ''.join('<th>%s</th>' % h for h, _ in cols)
    trs = ''.join('<tr>' + ''.join(('<td><span>%s</span>%s</td>' % (r[i][0], M(r[i][1]) if r[i][1] is not None else '<b class="v z"><span class="na">미가입</span></b>')) if i < len(r) else '<td></td>' for _, r in cols) + '</tr>' for i in range(n))
    return '<table class="kv"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (th, trs)
def grid(head, rows):
    th = ''.join('<th>%s</th>' % h for h in head)
    trs = ''.join('<tr>' + ''.join(('<td class="lab">%s</td>' if i == 0 else '<td>%s</td>') % c for i, c in enumerate(r)) + '</tr>' for r in rows)
    return '<table class="g"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (th, trs)
def foot():
    return ('<div class="ft">사내 비교용 · GA 가안 양식에 메리츠 설계서(%s · %s · 담보 %d건 · %s)를 넣은 것 · 금액은 메리츠 스마트 제안서 계산 엔진(%s) 계산값 · '
            '병원 종별 · 마취시간 · 연간 약물 종수는 가정값 · 실제 지급은 약관과 심사 기준에 따름</div>'
            % (SHORTP, WHO, NRID, PREMIUM, VERSION))

# ───────── 1쪽 ─────────
def p1():
    cancer = kv([('진단금', [(k, F(v)) for k, v in DX.items()]),
                 ('수술', [('다빈치로봇', F(C['robot'])), ('내시경', F(C['endo'])), ('복강경,흉강경', F(C['lap'])), ('개복,개흉', F(C['open']))]),
                 ('항암약물', [('화학항암', F(C['chemo'])), ('표적항암', F(C['target1'])), ('면역항암', F(C['immune1'])), ('표적/면역 2종', F(C['two']))]),
                 ('항암방사선', [('항암방사선', F(C['rad'])), ('세기조절', F(C['imrt'])), ('양성자', F(C['proton'])), ('중입자', F(C['carbon']))])])
    b2, h2 = vsurg('상급종합')
    sev = [('중환자실치료', itc_item('I63', 'icu', grp=BG)), ('부분에크모', itc_item('I63', 'ecmo', grp=BG)),
           ('지속적신대체요법', itc_item('I63', 'crrt', grp=BG)), ('인공호흡기', itc_item('I63', 'vent', grp=BG)), ('저체온요법', itc_item('I63', 'hypo', grp=BG))]
    bh = kv([('진단금', [('뇌출혈', BDX[3]), ('뇌경색', BDX[0]), ('급성심근', HDX[1]), ('허혈성', HDX[0])]),
             ('치료 및 수술', [('혈전용해', b2[0]), ('혈전제거', b2[1]), ('혈전용해+혈전제거', b2[2]), ('스텐트수술', h2[1])]),
             ('중증치료', sev),
             ('주요손상·질환 통합치료비', [(n, F(msL(c)) if ms_has() else None) for n, c in MS_CASES])])
    order = ['백내장', '디스크', '치질', '담석증', '충수염', '갑상선 결절', '유방양성종양', '자궁근종', '전립선절제술', '골절진단']
    def cell(n):
        proc = GA_DZ[n][0]; v = F(dzL(n, '병원'))
        return '<td><b>%s</b><em>%s</em>%s</td>' % (n, proc, M(v))
    dz = '<table class="dz"><tr>%s</tr><tr>%s</tr></table>' % (''.join(cell(n) for n in order[:5]), ''.join(cell(n) for n in order[5:]))
    def cv(*k, exclude=()):
        v = rider_man(*k, exclude=exclude); return '<span class="na">미가입</span>' if v is None else M(v)
    def care2(*k):
        a = rider_man(*k, exclude=('181일',)); b = rider_man(*k, '181일')
        if a is None and b is None: return '<span class="na">미가입</span>'
        return '%s <small>1~180일</small><br>%s <small>181일~</small>' % (M(a or 0), M(b or 0)) if b is not None else M(a or 0)   # 두 줄 — 한 줄이면 칸을 넘는다
    # 간병인지원 일당을 가입했으면 간병인 지원 · 요양병원 모두 '지원가능'(문구 통일)
    joined = any('간병인지원' in r['name'] and r['man'] > 0 for r in RID)
    ok = '<span class="txt">지원가능</span>'; na = '<span class="na">미가입</span>'
    # 간병인사용(실손·정액형) 일당 — 질병입원일당만. 이름 속 '(요양병원제외)'를 요양병원 일당으로 오인하지 않게 괄호 표기로 가른다.
    #   간병인 : 간병인사용 질병입원일당(요양병원 전용 제외) · 요양병원 : 간병인사용 …(요양병원) · 간호간병 : 간호·간병통합서비스 사용 질병입원일당(단독 특약)
    def use_rs(kind):
        rs = [r for r in RID if '질병입원일당' in r['name'] and '요양성' not in r['name']]
        if kind == 'gen': return [r for r in rs if '간병인사용' in r['name'] and '(요양병원)' not in r['name'] and '간호·간병' not in r['name']]
        if kind == 'nh': return [r for r in rs if '간병인사용' in r['name'] and '(요양병원)' in r['name']]
        return [r for r in rs if '간호·간병통합서비스' in r['name'] and '간병인지원' not in r['name']]
    def care_use(kind):
        rs = use_rs(kind)
        if not rs: return '<span class="na">미가입</span>'
        a = [r['man'] for r in rs if '181일' not in r['name']]; b = [r['man'] for r in rs if '181일' in r['name']]
        if b: return '%s <small>1~180일</small><br>%s <small>181일~</small>' % (M(sum(a)), M(sum(b)))
        return M(sum(a))
    care = ('<table class="care"><tr><th colspan="2">간병인지원</th></tr>'
            '<tr><td>간병인 지원</td><td>%s</td></tr>'
            '<tr><td>간병인 미사용</td><td>%s</td></tr><tr><td>요양병원</td><td>%s</td></tr><tr><td>간호간병</td><td>%s</td></tr>'
            '<tr><th colspan="2">간병인사용</th></tr>'
            '<tr><td>간병인</td><td>%s</td></tr><tr><td>요양병원</td><td>%s</td></tr><tr><td>간호간병</td><td>%s</td></tr></table>'
            % (ok if joined else na, cv('간병인지원', '질병입원일당(Ⅵ)', exclude=('181일',)), ok if joined else na,
               care2('간병인지원', '질병입원일당(간호·간병'),
               care_use('gen'), care_use('nh'), care_use('nurse')))
    body = ('<img class="char p1" src="%s"><h1>고객님의 메리츠 보장 한눈에!</h1>' % CH['p1']
            + hl('암보장') + cancer + hl('뇌·심보장') + bh
            + '<div class="two"><div class="l">' + hl('국내주요수술') + dz + '</div><div class="r">' + hl('간병인입원보장') + care + '</div></div>')
    return '<div class="page">%s%s</div>' % (body, foot())

# ───────── 1쪽 합산 계산서(1쪽 바로 뒤) ─────────
def _man_of(name):
    """지급 줄 이름과 같은 설계 담보의 가입금액(만원) — 못 찾으면 None"""
    for r in RID:
        if _ns(r['name']) == _ns(name): return r['man']
    return None
def _wn(v):
    """계산서용 숫자 — 1쪽 값 표시(b.v)와 다른 표기를 써서 지면 대조(ga_spec)가 1쪽 칸 수를 잘못 세지 않게 한다"""
    return '<span class="cn">%s</span>' % won(v)
def calc_rows(label, L, note=''):
    """한 칸 → (항목, 합계, 특약 줄 html). 합산에 들어간 줄(최초 지급) 전부를 적는다"""
    tot = F(L)
    if not L:
        body = '<span class="cnone">합산된 특약 없음%s</span>' % ((' — ' + note) if note else '')
    else:
        parts = []
        for l in L:
            m = _man_of(l['name'])
            why = (l.get('why') or '') if l.get('rule') == 'itc' else ''
            parts.append('<div><span class="nm">%s</span><span class="mn">%s</span><span class="am">%s</span>%s</div>'
                         % (l['name'], ('가입 ' + won(m)) if m is not None else '', won(l['amt']), ('<small>%s</small>' % why) if why else ''))
        body = ''.join(parts)
    return (label, tot, body)
def calc_table(title, rows):
    trs = ''
    for lab, tot, body in rows:
        trs += '<tr><td class="lab">%s</td><td class="sum">%s</td><td class="ls">%s</td></tr>' % (lab, _wn(tot) if tot is not None else '', body)
    return hl(title) + ('<table class="calc"><thead><tr><th>항목</th><th>1쪽 금액(만원)</th><th>합산된 설계 특약 · 가입금액 · 지급액(만원)</th></tr></thead><tbody>%s</tbody></table>' % trs)
def p1calc():
    """1쪽 「보장 한눈에」 각 칸이 어떤 설계 특약의 합산인지 — 2쪽 분량(암·뇌심 / 국내주요수술·간병인)"""
    tgt = calc_rows('항암약물 · 표적항암 (약물 1종)', C['target1'])
    cancer = [calc_rows('진단금 · ' + k, v) for k, v in DX.items()]
    cancer += [calc_rows('수술 · 다빈치로봇', C['robot']), calc_rows('수술 · 내시경', C['endo']), calc_rows('수술 · 복강경,흉강경', C['lap']), calc_rows('수술 · 개복,개흉', C['open'])]
    cancer += [calc_rows('항암약물 · 화학항암', C['chemo']), tgt, calc_rows('항암약물 · 면역항암 (약물 1종)', C['immune1']), calc_rows('항암약물 · 표적/면역 2종 (항암약물+표적+면역+2종 담보)', C['two'])]
    cancer += [calc_rows('항암방사선 · 항암방사선', C['rad']), calc_rows('항암방사선 · 세기조절', C['imrt']), calc_rows('항암방사선 · 양성자', C['proton']), calc_rows('항암방사선 · 중입자', C['carbon'])]
    b2, h2 = vsurgL('상급종합')
    bh = [calc_rows('진단금 · 뇌출혈', BDXL[3]), calc_rows('진단금 · 뇌경색', BDXL[0]), calc_rows('진단금 · 급성심근', HDXL[1]), calc_rows('진단금 · 허혈성', HDXL[0]),
          calc_rows('치료 및 수술 · 혈전용해', b2[0]), calc_rows('치료 및 수술 · 혈전제거 (혈전제거술만 · 카테터)', b2[1]), calc_rows('치료 및 수술 · 혈전용해+혈전제거 (합산)', b2[2]), calc_rows('치료 및 수술 · 스텐트수술', h2[1])]
    for lab, key in (('중환자실치료', 'icu'), ('부분에크모', 'ecmo'), ('지속적신대체요법', 'crrt'), ('인공호흡기', 'vent'), ('저체온요법', 'hypo')):
        bh.append(calc_rows('중증치료 · ' + lab + ' (통합치료비 항목만)', itc_itemL('I63', key, grp=BG)))
    for n, c in MS_CASES:
        bh.append(calc_rows('주요손상·질환 통합치료비 · %s (%s)' % (n, c['kcd']), msL(c), note='특정순환계질환(주요손상및질환) 통합치료비 미가입' if not ms_has() else ''))
    desc = '<p class="cdesc">1쪽 각 칸의 금액이 이 설계서의 어떤 특약을 더해 나온 것인지 적었습니다. 지급액은 사례 조건(질병코드 · 병원 종별 · 수술 분류 · 약물 종수)으로 계산 엔진이 낸 값이며, 가입금액은 설계서 그대로입니다. 표적·면역항암은 약물 1종(치료 1개)만 받은 것으로 계산합니다.</p>'

    order = ['백내장', '디스크', '치질', '담석증', '충수염', '갑상선 결절', '유방양성종양', '자궁근종', '전립선절제술', '골절진단']
    dz = [calc_rows('%s · %s (%s · 병원급)' % (n, GA_DZ[n][0], GA_DZ[n][1]), dzL(n, '병원')) for n in order]
    # 간병인입원보장 — 계산이 아니라 가입금액 그대로. 어떤 담보를 읽었는지 적는다
    def rs_rows(lab, rs, mode='sum'):
        if not rs: return (lab, 0, '<span class="cnone">해당 담보 미가입</span>')
        body = ''.join('<div><span class="nm">%s</span><span class="mn"></span><span class="am">%s</span></div>' % (r['name'], won(r['man'])) for r in rs)
        return (lab, sum(r['man'] for r in rs), body)
    def pick(*keys, exclude=()):
        return [r for r in RID if all(k in r['name'] for k in keys) and not any(x in r['name'] for x in exclude)]
    joined = [r for r in RID if '간병인지원' in r['name'] and r['man'] > 0]
    care = [('간병인지원 · 간병인 지원 / 요양병원 (지원가능 여부)', None,
             ('<span class="cnone">지원가능 — 아래 간병인지원 담보가 가입되어 있음</span>' + ''.join('<div><span class="nm">%s</span><span class="mn"></span><span class="am">%s</span></div>' % (r['name'], won(r['man'])) for r in joined)) if joined else '<span class="cnone">미가입</span>'),
            rs_rows('간병인지원 · 간병인 미사용 (일당)', pick('간병인지원', '질병입원일당(Ⅵ)', exclude=('181일',))),
            rs_rows('간병인지원 · 간호간병 (1~180일 / 181일~)', pick('간병인지원', '질병입원일당(간호·간병')),
            rs_rows('간병인사용 · 간병인 (1~180일 / 181일~)', [r for r in RID if '질병입원일당' in r['name'] and '요양성' not in r['name'] and '간병인사용' in r['name'] and '(요양병원)' not in r['name'] and '간호·간병' not in r['name']]),
            rs_rows('간병인사용 · 요양병원', [r for r in RID if '질병입원일당' in r['name'] and '간병인사용' in r['name'] and '(요양병원)' in r['name']]),
            rs_rows('간병인사용 · 간호간병 (1~180일 / 181일~)', [r for r in RID if '질병입원일당' in r['name'] and '간호·간병통합서비스' in r['name'] and '간병인지원' not in r['name']])]
    return calc_paginate([('암보장', cancer), ('뇌·심보장', bh), ('국내주요수술', dz), ('간병인입원보장 (계산 없이 가입금액 그대로)', care)], desc)

# ───────── 2쪽 ─────────
def p2():
    exams = [('암<br>내시경검사', 'x_endo'), ('MRI<br>촬영검사', 'x_mri'), ('PET검사', 'x_pet'), ('특정단일<br>유전자검사', 'x_gene'),
             ('초음파검사', 'x_us'), ('CT<br>촬영검사', 'x_ct'), ('특정생검<br>조직검사', 'x_bio'), ('특정NGS<br>유전자검사', 'x_ngs')]
    ex = '<table class="g eight"><tr>%s</tr><tr>%s</tr></table>' % (''.join('<th>%s</th>' % a for a, _ in exams), ''.join('<td>%s</td>' % M(itc_item('C16', k, fam='cancer')) for _, k in exams))
    dxb = ('<div class="dxbig"><div><span>일반암</span><em>위, 대장, 폐, 간, 췌장 등</em>%s</div>'
           '<div><span>유사암</span><em>갑상선암, 기타피부암, 제자리암, 경계성종양</em>%s</div></div>' % (M(F(DX['일반암']), True), M(F(DX['유사암']), True)))
    ks = ('endo', 'open', 'lap', 'robot')
    sg = grid(['', '내시경수술', '개복·개흉수술', '복강경,흉강경', '다빈치로봇암수술'],
              [['최초 지급시'] + [M(F(C[k])) for k in ks], ['반복(연 1회)'] + [M(Y(C[k])) for k in ks], ['수술할 때마다'] + [M(E(C[k])) for k in ks]])
    t3 = s('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=3)
    cm = grid(['', '화학항암치료', '표적항암치료', '면역항암치료<br><u>(카티포함)</u>', '갯수별 약물치료<br><u>(표적, 면역)</u>'],
              [['최초 지급시', M(F(C['chemo'])), M(F(C['target'])), M(F(C['immune'])), '<small>2가지치료</small> ' + M(F(C['target']))],
               ['반복(연 1회)', M(Y(C['chemo'])), M(Y(C['target'])), M(Y(C['immune'])), '<small>3가지치료</small> ' + M(F(t3))]])
    kr = ('rad', 'imrt', 'proton', 'carbon')
    rd = grid(['', '항암방사선', '세기조절 방사선', '양성자 방사선', '중입자 방사선'],
              [['최초 지급시'] + [M(F(C[k])) for k in kr], ['반복(연 1회)'] + [M(Y(C[k])) for k in kr]])
    rh = itc_item('C16', 'rehab', fam='cancer', extra={'n': 20})
    dis = rider_man('암', '후유장해')
    body = ('<h1>치료과정에 따른 암세부보장</h1>' + hl('암검사(8종)') + ex + hl('암진단') + dxb + hl('암수술') + sg + hl('항암약물') + cm + hl('항암방사선') + rd
            + '<div class="two"><div class="l">' + hl('재활치료') + grid(['', '입원<br>암재활치료', '외래<br>암재활치료'], [['연 20회', M(rh), M(rh)]]) + '</div>'
            + '<div class="r">' + hl('암후유장해') + '<div class="dxbig one"><div><span>3-100%% 암후유장해</span>%s</div></div></div></div>' % ('<span class="na">미가입</span>' if dis is None else M(dis)))
    return '<div class="page">%s%s</div>' % (body, foot())

# ───────── 3쪽 ─────────
def p3():
    ex = '<table class="g eight three"><tr>%s</tr><tr>%s</tr></table>' % (''.join('<th>%s</th>' % a for a in ('MRI 촬영검사', 'PET검사', 'CT 촬영검사')),
                                                                         ''.join('<td>%s</td>' % M(itc_item('I63', k, grp=BG)) for k in ('x_mri', 'x_pet', 'x_ct')))
    def Ls(kind, hosp):
        if kind == 'brain':
            return [s('I63', [['시술', '혈전용해', '', ['thromb']]], series='brain', hosp=hosp),
                    s('I63', [['시술', '혈전용해', '', ['thromb']], ['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], hosp=hosp, acts=['thrombectomy']),
                    s('I67.1', [['시술', '코일 색전술', '', ['surg']]], surg='88-1', surg7='B016', grp=BG + ['특정31대질병'], hosp=hosp, anes=1),
                    s('I61', [['수술', '혈종제거 개두술', '', ['surg']]], surg='59', surg7='B031', grp=BG + ['뇌졸중', '뇌출혈', '특정31대질병'], hosp=hosp, anes=1)]
        return [s('I21', [['시술', '혈전용해', '', ['thromb']]], series='heart', hosp=hosp),
                s('I21', [['시술', '혈전용해', '', ['thromb']], ['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='F121', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp, acts=['thrombectomy']),
                s('I20', [['시술', '스텐트 삽입', '', ['surg']]], surg='88-1', surg7='F133', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp),
                s('I20', [['수술', '관상동맥 우회술', '', ['surg']]], surg='24', surg7='F042', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp, anes=1, anes_h=6)]
    def block(kind):
        if kind == 'brain':
            dxs = [('뇌혈관', BDX[0]), ('뇌출혈', BDX[3])]; cols = ['혈전용해치료', '혈전용해+<br>혈전제거술', '스텐트<br>코일색전술', '개두 수술']
        else:
            dxs = [('허혈성', HDX[0]), ('급성심근경색', HDX[1])]; cols = ['혈전용해치료', '혈전용해+<br>혈전제거술', '관상동맥스텐트', '개흉 수술']
        a, t = Ls(kind, '병원'), Ls(kind, '상급종합')
        right = grid([''] + cols, [['모든 병원'] + [M(F(L)) for L in a], ['상급종합병원'] + [M(F(L)) for L in t], ['수술할 때마다'] + [M(E(L)) for L in t]])
        left = ''.join('<div><span>%s</span>%s</div>' % (n, M(v, True)) for n, v in dxs)
        return '<div class="vas"><div class="dxl">%s</div>%s</div>' % (left, right)
    sk = [('중환자실 치료', 'icu'), ('부분에크모치료', 'ecmo'), ('지속적신대체요법', 'crrt'), ('인공호흡기치료', 'vent'), ('저체온요법치료', 'hypo')]
    sev = grid([''] + [a for a, _ in sk], [['모든 병원'] + [M(itc_item('I63', k, hosp='병원', grp=BG)) for _, k in sk], ['상급종합병원'] + [M(itc_item('I63', k, grp=BG)) for _, k in sk]])
    rh = itc_item('I63', 'rehab', grp=BG, extra={'n': 15})
    body = ('<h1>치료과정에 따른 뇌심세부보장</h1>' + hl('검사(3종)') + ex + hl('뇌질환 진단·치료') + block('brain') + hl('심질환 진단·치료') + block('heart')
            + hl('뇌심 중증치료') + sev + '<div class="two"><div class="l">' + hl('재활치료') + grid(['', '입원 재활치료', '외래 재활치료'], [['연 15회', M(rh), M(rh)]]) + '</div><div class="r"></div></div>')
    return '<div class="page">%s%s</div>' % (body, foot())

# ───────── 4쪽 ─────────
def det(rows, tots, note=''):
    """rows : (담보명, 값 html) · tots : (라벨, 값)"""
    tb = ''.join('<tr><td>%s</td><td class="amt">%s</td></tr>' % (a, v) for a, v in rows)
    tt = ''.join('<div><span>%s</span>%s</div>' % (a, v) for a, v in tots)
    return ('<div class="det"><table class="g"><thead><tr><th>담보</th><th>보장금액</th></tr></thead><tbody>%s</tbody></table>'
            '<div class="tot"><h4>총 보장</h4>%s%s</div></div>' % (tb, tt, ('<p>%s</p>' % note) if note else ''))
def amt_cell(L, keys, exclude=(), kcd=None):
    rs = [r for r in RID if hit(r['name'], keys, exclude)]
    if not rs: return '<span class="na">미가입</span>'
    v = rowsum(L, keys, exclude)
    if v == 0 and kcd and all(S.excluded(r, kcd) for r in rs): return '<span class="na">면책</span>'
    return M(v)
CONSERV = '*위 수치는 표의 예시금액 합산으로 표 외에 가입한 담보 총합의 보상금액은 더 클 수 있습니다.'
def row_lines(L, specs):
    """표의 담보행(specs : (keys, exclude) 목록) 중 하나에라도 드는 지급 줄 — 총 보장은 표에 나온 것만 보수적으로 합산(v8.65)"""
    return [l for l in L if any(hit(l['name'], k, x) for k, x in specs)]
P4_SURG = {'질병수술비': (['질병수술비'], ('131대', '130대', '척추질병')), '1-5종수술비': (['1-5종'], ('상해',)), '1-7종수술비': (['┗ 수술비', '수술비(1-7종'], ('상해',)),
           '암수술비': (['암수술비'], ('다빈치',)), '암통합치료비': (['암 통합치료비(기본형)', '암 통합치료비(실속형)'], ()),
           '비급여암통합치료비': (['통합치료비Ⅱ(비급여', '통합치료비(주요치료)(비급여'], ()), '다빈치로봇암수술비': (['다빈치'], ())}
P4_TARGET = [('항암방사선약물치료비', (['항암방사선약물치료비'], ('26종', '기타피부암'))), ('26종항암방사선약물', (['26종'], ())),
             ('암통합치료비', (['암 통합치료비(기본형)', '암 통합치료비(실속형)'], ())), ('비급여암통합치료비', (['통합치료비Ⅱ(비급여', '통합치료비(주요치료)(비급여'], ())),
             ('암진단비 및 치료비(치료비)', (['암진단및치료비Ⅱ[표적', '암치료,후유장해및진단비[표적'], ())),
             ('표적항암약물치료비', (['표적항암약물허가치료비'], ('연간 약물종류', '암진단및치료비', '후유장해및진단비'))),
             ('표적항암약물치료비<small>(연간약물종류)</small>', (['연간 약물종류'], ()))]
def p4():
    R = C['robot']
    ka = ['질병수술비', '1-5종수술비', '암수술비', '암통합치료비', '비급여암통합치료비', '다빈치로봇암수술비']
    Ra = row_lines(R, [P4_SURG[k] for k in ka])
    a = det([(k, amt_cell(R, *P4_SURG[k])) for k in ka],
            [('최초 :', M(F(Ra), True)), ('매 회 :', M(E(Ra), True))], '*암수술비(체증형) 5회이상 수술시 최대 2배보장<br>' + CONSERV)
    O = C['open']
    kb = ['질병수술비', '1-5종수술비', '1-7종수술비', '암수술비', '암통합치료비', '비급여암통합치료비']
    Ob = row_lines(O, [P4_SURG[k] for k in kb])
    b = det([(k, amt_cell(O, *P4_SURG[k])) for k in kb],
            [('최초 :', M(F(Ob), True)), ('매 회 :', M(E(Ob), True))], '*암수술비(체증형) 5회이상 수술시 최대 2배보장<br>' + CONSERV)
    tg = lambda d: s('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=d)
    T1, T2, T3 = tg(1), tg(2), tg(3)
    K = dict(P4_TARGET)
    two3 = lambda L2, L3, keys, ex=(): ('<small>2가지</small> %s <small>3가지</small> %s' % (M(rowsum(L2, keys, ex)), M(rowsum(L3, keys, ex)))) if any(hit(r['name'], keys, ex) for r in RID) else '<span class="na">미가입</span>'
    yk = K['표적항암약물치료비<small>(연간약물종류)</small>'][0]
    c = det([('항암방사선약물치료비', amt_cell(T2, *K['항암방사선약물치료비'])), ('26종항암방사선약물', amt_cell(T2, *K['26종항암방사선약물'])),
             ('암통합치료비', amt_cell(T2, *K['암통합치료비'])), ('비급여암통합치료비', amt_cell(T2, *K['비급여암통합치료비'])),
             ('암진단비 및 치료비(치료비)', two3(T2, T3, *K['암진단비 및 치료비(치료비)'])),
             ('표적항암약물치료비', amt_cell(T2, *K['표적항암약물치료비'])),
             ('표적항암약물치료비<small>(연간약물종류)</small>', ('<small>1가지</small> %s <small>2가지</small> %s <small>3가지</small> %s' % (M(rowsum(T1, yk)), M(rowsum(T2, yk)), M(rowsum(T3, yk)))) if any(hit(r['name'], yk) for r in RID) else '<span class="na">미가입</span>')],
            [('최초 :', M(F(row_lines(T1, list(K.values()))), True)), ('2가지 :', M(F(row_lines(T2, list(K.values()))), True)), ('3가지 :', M(F(row_lines(T3, list(K.values()))), True))], CONSERV)
    body = '<img class="char p4" src="%s"><h1>암치료 세부내역</h1>' % CH['p4'] + hl('다빈치로봇암수술') + a + hl('개복수술') + b + hl('표적항암치료비') + c
    return '<div class="page">%s%s</div>' % (body, foot())

# ───────── 뇌·심장 치료 세부내역 (암치료 세부내역과 같은 틀 · 뇌/심장 두 열) ─────────
# 사례는 3쪽과 같은 조건(상급종합병원). 담보 줄은 지급 줄 이름으로 묶고, 어느 줄에도 안 드는 담보는 '그 밖' 줄에 모아 합계가 총 보장과 맞게 한다.
BH_ROWS = {
 'thromb': ('혈전용해치료비', r'혈전용해치료비'),
 'mech':   ('혈전제거·특정혈전치료비', r'기계적혈전제거|특정혈전치료비'),
 'two':    ('2대질환 치료비<small>(주요치료비·최대두배)</small>', r'2대질환.*주요치료비|최대두배받는2대질환치료비'),
 'bhsurg': ('뇌·심장 수술비<small>(뇌혈관·허혈성심장·131대·5대질환 등)</small>', r'뇌혈관질환수술비|허혈성심장질환수술비|심장질환수술비|뇌출혈수술비|뇌졸중수술비|뇌동맥류|5대질환|32대질병|13[01]대질병수술비'),
 'dzsurg': ('질병수술비', r'^(\(\d+년갱신\))?(갱신형)?(상급종합병원|종합병원)?질병수술비'),
 'g15':    ('1-5종수술비', r'1-5종'),
 'g17':    ('1-7종수술비', r'1-7종|┗수술비'),
 'itc':    ('특정순환계질환 통합치료비', None),          # 통합치료비(순환계·질병) — 지급 줄 group 으로 판정
 'etc':    ('산정특례·생활지원비·전신마취 등', None),     # 위 줄에 안 드는 모든 지급 줄
}
BH_SEC = {
 1: ('혈전용해치료', ('뇌경색<small>혈전용해</small>', '급성심근경색<small>혈전용해</small>'), ['thromb', 'two', 'itc'],
     lambda: [s('I63', [['시술', '혈전용해', '', ['thromb']]], series='brain'),
              s('I21', [['시술', '혈전용해', '', ['thromb']]], series='heart')]),
 # 시술만의 사례(v8.65) — 전에는 뇌 쪽만 혈전용해+혈전제거술이라 위 「혈전용해치료」 칸과 겹치고, 심장(스텐트만)과 혈전용해치료비가 1,000 / 0 으로 어긋났다
 2: ('수술(비관혈) · 혈관 안 시술', ('뇌경색<small>기계적 혈전제거술</small>', '급성심근경색<small>관상동맥 스텐트</small>'), ['bhsurg', 'dzsurg', 'g15', 'g17', 'two', 'itc'],
     lambda: [s('I63', [['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], acts=['thrombectomy']),
              s('I21', [['시술', '스텐트 삽입', '', ['surg']]], surg='88-1', surg7='F133', grp=HG + ['허혈성심장질환', '특정31대질병'])]),
 3: ('수술(관혈) · 개두·개흉', ('뇌출혈<small>개두술</small>', '협심증<small>관상동맥 우회술</small>'), ['bhsurg', 'dzsurg', 'g15', 'g17', 'two', 'itc'],
     lambda: [s('I61', [['수술', '혈종제거 개두술', '', ['surg']]], surg='59', surg7='B031', grp=BG + ['뇌졸중', '뇌출혈', '특정31대질병'], anes=1),
              s('I20', [['수술', '관상동맥 우회술', '', ['surg']]], surg='24', surg7='F042', grp=HG + ['허혈성심장질환', '특정31대질병'], anes=1, anes_h=6)]),
}
BH_SEV = [('중환자실 치료', 'icu'), ('부분에크모(ECMO)', 'ecmo'), ('지속적신대체요법(CRRT)', 'crrt'), ('인공호흡기(12시간 초과)', 'vent'), ('저체온요법', 'hypo')]
def bh_sev_case(kcd, grp, keys):
    return s(kcd, [['치료', k, '', [k]] for k in keys], grp=grp, icu=(1 if 'icu' in keys else 0))
def bh_group(l):
    n = _ns(l['name'])
    for k in ('thromb', 'mech', 'two', 'bhsurg', 'dzsurg', 'g15', 'g17'):
        if re.search(BH_ROWS[k][1], n) and not (k == 'thromb' and re.search(BH_ROWS['mech'][1], n)): return k
    if l.get('group') == '통합치료비': return 'itc'
    return 'etc'
def bh_joined(k):
    if k == 'etc': return True
    if k == 'itc': return any(r.get('itc') and r['man'] > 0 for r in RID)
    return any(re.search(BH_ROWS[k][1], _ns(r['name'])) and r['man'] > 0 and not (k in ('g15', 'g17') and '상해' in r['name']) for r in RID)   # 질병 사례 칸 — 상해 전용 종수술비만 있으면 미가입(v8.65)
def det2(cols, rows, tots, note=''):
    """cols : (뇌 열 이름, 심장 열 이름) · rows : (담보, 뇌 값, 심장 값) · tots : (라벨, 뇌 값, 심장 값)"""
    tb = ''.join('<tr><td>%s</td><td class="amt">%s</td><td class="amt">%s</td></tr>' % r for r in rows)
    tt = ('<table class="tt"><tr><th></th><th>뇌</th><th>심장</th></tr>%s</table>'
          % ''.join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % t for t in tots))
    return ('<div class="det bh"><table class="g"><thead><tr><th>담보</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table>'
            '<div class="tot"><h4>총 보장</h4>%s%s</div></div>' % (cols[0], cols[1], tb, tt, ('<p>%s</p>' % note) if note else ''))
def bh_section(no):
    title, cols, keys, mk = BH_SEC[no]
    Lb, Lh = mk()
    def v(L, k):
        if not bh_joined(k): return '<span class="na">미가입</span>'
        return M(int(round(sum(l['amt'] for l in L if bh_group(l) == k))))
    rows = [(BH_ROWS[k][0], v(Lb, k), v(Lh, k)) for k in keys]
    Lb = [l for l in Lb if bh_group(l) in keys]; Lh = [l for l in Lh if bh_group(l) in keys]   # 총 보장은 표에 나온 줄만(v8.65 · 보수적)
    if no == 1:
        tots = [('최초', M(F(Lb)), M(F(Lh))), ('다음 해', M(Y(Lb)), M(Y(Lh)))]
        note = '*다음 해 = 최초 1회 담보(혈전용해치료비Ⅱ 등)를 뺀 연간 반복분'
    else:
        tots = [('최초', M(F(Lb)), M(F(Lh))), ('매 회', M(E(Lb)), M(E(Lh)))]
        note = '*매 회 = 수술 1회당 담보만(연간·최초 1회 담보 제외)'
    return hl(title) + det2(cols, rows, tots, note + '<br>' + CONSERV)
def p_bh():
    sev_rows = []
    for lab, k in BH_SEV:
        a = int(sum(l['amt'] for l in bh_sev_case('I63', BG, [k])))
        b = int(sum(l['amt'] for l in bh_sev_case('I21', HG, [k])))
        sev_rows.append((lab, M(a), M(b)))
    allk = [k for _, k in BH_SEV]
    La, Lh = bh_sev_case('I63', BG, allk), bh_sev_case('I21', HG, allk)
    sev = hl('중환자실·에크모 등 중증치료') + det2(('뇌경색<small>상급종합병원</small>', '급성심근경색<small>상급종합병원</small>'), sev_rows, [('모두 받을 때', M(F(La)), M(F(Lh)))],
                                            '*같은 해 여러 항목을 받으면 통합치료비 연간 한도(가입금액)까지')
    body = ('<img class="char p4" src="%s"><h1>뇌·심장 치료 세부내역</h1>' % CH['p4']
            + bh_section(1) + bh_section(2) + bh_section(3) + sev)
    return '<div class="page">%s%s</div>' % (body, foot())

# ───────── 5쪽 ─────────
def p5():
    out = ''
    for n, tpl in (('백내장', ['질병수술비', '1-5종수술비', '1-7종수술비', '131대수술비']),
                   ('디스크', ['질병수술비', '질병수술비(특정5대제외)', '1-5종수술비', '1-7종수술비', '131대수술비']),
                   ('치질', ['질병수술비', '1-5종수술비', '1-7종수술비', '131대수술비']),
                   ('담석증', ['질병수술비', '질병수술비(특정5대제외)', '1-5종수술비', '1-7종수술비', '131대수술비'])):
        kcd = GA_DZ[n][1]; La, Lt = dzL(n, '병원'), dzL(n, '상급종합')
        KEY = {'질병수술비': (['질병수술비'], ('특정5대질병 제외', '131대', '130대', '척추질병')), '질병수술비(특정5대제외)': (['특정5대질병 제외'], ()), '1-5종수술비': (['1-5종'], ('상해',)),
               '1-7종수술비': (['┗ 수술비', '수술비(1-7종'], ('상해',)), '131대수술비': (['131대', '130대'], ())}   # 통합간편은 130대질병수술비(v8.63)
        rows = [(t, amt_cell(Lt, KEY[t][0], KEY[t][1], kcd)) for t in tpl]
        out += hl(n) + det(rows, [('모든병원 :', M(F(La), True)), ('상급병원 :', M(F(Lt), True))])
    body = '<img class="char p5" src="%s"><h1>주요 수술비 세부내역</h1>' % CH['p5'] + out
    return '<div class="page">%s%s</div>' % (body, foot())

CSS = '''
@page{size:A4;margin:0} *{box-sizing:border-box} body{margin:0;font-family:"GANG","NanumGothic","Malgun Gothic",sans-serif;color:#111}
.page{width:210mm;height:297mm;padding:13mm 13mm 12mm 14mm;page-break-after:always;position:relative;overflow:hidden;background:#fff}
h1{font-size:25pt;font-weight:900;margin:2pt 0 12pt;letter-spacing:-.8pt}
h2{font-size:13.5pt;margin:12pt 0 6pt;display:inline-block;font-weight:900} h2 span{background:linear-gradient(transparent 42%,#FFE94D 42%);padding:0 3pt}
.char{position:absolute;top:9mm;right:14mm;height:31mm} .char.p4,.char.p5{height:30mm}
table{border-collapse:collapse;width:100%;table-layout:fixed} th,td{font-size:9.8pt;padding:0 6pt;height:24pt;border-bottom:1px solid #D6D6D6;white-space:nowrap;overflow:hidden}
th{background:#E4E4E4;font-weight:800;color:#222;text-align:center;height:22pt} td{text-align:center} .g th{white-space:normal;line-height:1.2} .lab{text-align:left;color:#444;white-space:nowrap;font-size:9pt}
.g th:first-child{background:#fff}
.kv td{width:25%;text-align:left;border-right:1px solid #EEE} .kv td:last-child{border-right:0} .kv td span{display:inline-block;width:42%;color:#333} .kv td b{float:right;font-size:10pt;line-height:24pt} .kv td b i{line-height:1}
b.v{font-weight:900;color:#111;font-size:11pt;white-space:nowrap} b.v i{font-style:normal;font-weight:500;font-size:8pt;color:#666;margin-left:1pt}
b.v.z{color:#9A9A9A} b.v.big{font-size:19pt;color:#C12027} b.v.big i{font-size:10pt}
small{font-size:8pt;color:#555} .na{color:#999;font-size:9pt}
.two{display:flex;gap:14pt;align-items:flex-start} .two .l{flex:1} .two .r{width:31%}
.dz td{text-align:center;vertical-align:top;border:1px solid #D6D6D6;width:20%;padding:7pt 4pt;height:auto;white-space:normal} .dz td b{display:block;font-size:10.5pt;font-weight:900}
.dz td em{display:block;font-style:normal;color:#666;font-size:8.4pt;margin:3pt 0 7pt} .dz td b.v{display:inline}
.care th{text-align:left;background:#E4E4E4} .care td{text-align:left;height:22pt} .care td:last-child{text-align:right} .care .txt{font-weight:800} .care small{font-size:6.6pt}
.eight th{font-size:8.4pt;line-height:1.25;white-space:normal;height:30pt} .eight td{padding:0 2pt;height:30pt} .three th,.three td{width:33.3%}
.dxbig{display:flex;gap:12pt} .dxbig div{flex:1;background:#FBE9E9;padding:11pt 13pt;border-radius:3pt}
.dxbig span{font-weight:900;font-size:13pt;margin-right:8pt} .dxbig em{font-style:normal;color:#555;font-size:8.6pt} .dxbig b.v{float:right} .dxbig.one div{background:#F2F2F2}
.vas{display:flex;gap:10pt;align-items:stretch} .dxl{width:22%;padding:4pt 6pt} .dxl div{margin-bottom:9pt} .dxl span{display:block;font-size:11pt;font-weight:800;color:#222}
.dxl b.v{float:none} .vas table{flex:1}
.det{display:flex;gap:12pt;align-items:flex-start;margin-bottom:6pt} .det table{flex:1} .det .amt{text-align:right;white-space:normal;height:auto;padding:4pt 6pt} .det td{white-space:normal;height:auto;padding:4pt 6pt}
.det .tot{width:34%;background:#F3F3F3;padding:10pt 12pt;border-radius:3pt;min-height:70pt} .det .tot h4{margin:0 0 6pt;font-size:10.5pt;text-align:center;font-weight:900}
.det .tot div{display:flex;justify-content:space-between;align-items:baseline;margin:4pt 0} .det .tot span{font-size:11pt;font-weight:900} .det .tot p{margin:6pt 0 0;font-size:7.6pt;color:#555}
.ft{position:absolute;left:14mm;right:13mm;bottom:6mm;font-size:6.4pt;color:#888;border-top:1px solid #DDD;padding-top:3pt}
.det.bh .tot{width:35%;padding:9pt 8pt} .det.bh th{font-size:9pt;line-height:1.15} .det.bh th small{display:block;font-size:7pt;font-weight:600;color:#666}
.det.bh th:nth-child(2),.det.bh th:nth-child(3){width:21%} .det.bh td{padding:2.6pt 6pt;font-size:9.2pt} .det.bh td:first-child{text-align:left} .det.bh td small{font-size:6.6pt;color:#777;margin-left:2pt}
.tt{width:100%;border-collapse:collapse;table-layout:fixed} .tt th,.tt td{border:0;height:auto;padding:2pt 0;font-size:8.6pt;background:none;white-space:nowrap}
.tt th{color:#666;font-weight:700;text-align:right} .tt td{text-align:right} .tt td:first-child,.tt th:first-child{text-align:left;width:17%;font-weight:900;font-size:9pt;color:#222} .tt td{overflow:visible;padding-left:4pt}
.tt b.v{font-size:9.6pt;letter-spacing:-.3pt} .tt b.v i{font-size:6.4pt}
.calcpg h1{font-size:17pt;margin:0 0 4pt} .calcpg h2{font-size:10.5pt;margin:7pt 0 3pt} .cdesc{font-size:7.6pt;color:#555;margin:0 0 4pt;line-height:1.35}
.calc th{font-size:7.4pt;height:14pt;padding:0 4pt} .calc td{font-size:7pt;height:auto;padding:1.6pt 4pt;white-space:normal;vertical-align:top;border-bottom:1px solid #E2E2E2;line-height:1.3}
.calc th:nth-child(1){width:19%} .calc th:nth-child(2){width:9%} .calc td.lab{text-align:left;font-size:7.4pt;font-weight:800;color:#222} .calc td.sum{text-align:right} .calc td.ls{text-align:left}
.calc .cn{font-weight:900;font-size:8.6pt} .calc .cnone{color:#888}
.calc .ls div{display:flex;gap:4pt;align-items:baseline} .calc .nm{flex:1;min-width:0;white-space:normal;line-height:1.2} .calc .mn{width:14%;color:#666;text-align:right;white-space:nowrap} .calc .am{width:9%;text-align:right;font-weight:800;white-space:nowrap}
.calc .ls small{display:block;width:100%;font-size:6.2pt;color:#888;margin-top:-1pt} .calc .ls div:has(small){flex-wrap:wrap}
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

CALC_PAGES = 3      # 1쪽 뒤 합산 계산서 최소 쪽수 — 고정 규칙(GA 확정 2026-10-02) : 「보장 한눈에」 뒤에는 반드시 이 계산서가 붙는다(담보가 많으면 쪽이 늘어난다)
CALC_BUDGET = 84    # 계산서 한 쪽에 들어가는 분량(단위 : 특약 줄 1 · 항목 머리 1 · 통합치료비 내역 0.8 · 구역 제목 3). 설계서 3건(담보 66·127·151)으로 맞춘 값 — 넘치면 render 의 '이탈' 경고로 잡힌다
def calc_units(row):
    lab, tot, body = row
    return 1 + max(1, body.count('<div><span class="nm">')) + 0.8 * body.count('<small>') + body.count('cnone')
def calc_paginate(sections, desc):
    """구역(제목, 줄들)을 순서대로 쪽에 담는다 — 한 쪽 분량(CALC_BUDGET)을 넘으면 다음 쪽으로 넘기고 구역 제목에 (이어서)를 붙인다"""
    pages, cur, used = [], [], 4 + 2
    for title, rows in sections:
        i = 0
        while i < len(rows):
            if used + 3 + calc_units(rows[i]) > CALC_BUDGET and cur:
                pages.append(cur); cur, used = [], 4
            chunk, u = [], 3
            while i < len(rows) and used + u + calc_units(rows[i]) <= CALC_BUDGET:
                u += calc_units(rows[i]); chunk.append(rows[i]); i += 1
            if not chunk:                       # 줄 하나가 한 쪽을 넘는 경우 — 그대로 싣고 경고에 맡긴다
                chunk = [rows[i]]; u += calc_units(rows[i]); i += 1
            cur.append((title + (' (이어서)' if cur and cur[-1][0].split(' (')[0] == title.split(' (')[0] or (pages and pages[-1][-1][0].split(' (')[0] == title.split(' (')[0] and not cur) else ''), chunk)); used += u
    if cur: pages.append(cur)
    circ = '①②③④⑤⑥⑦⑧⑨⑩'
    out = []
    for n, pg in enumerate(pages):
        body = '<h1>「보장 한눈에」 합산 계산서 %s</h1>' % (circ[n] if n < len(circ) else n + 1) + (desc if n == 0 else '')
        body += ''.join(calc_table(t, rows) for t, rows in pg)
        out.append('<div class="page calcpg">%s%s</div>' % (body, foot()))
    return out
def html(design_pdf, age=''):
    load(design_pdf, age)
    calc = p1calc()
    # 계산서는 선택이 아니다 — 못 만들면 지면 전체를 내지 않는다(1쪽 금액의 근거가 빠진 제안서가 나가지 않게)
    if len(calc) < CALC_PAGES or any('class="page calcpg"' not in c for c in calc):
        raise RuntimeError('「보장 한눈에」 합산 계산서가 %d쪽 이상 만들어지지 않았습니다(%d쪽)' % (CALC_PAGES, len(calc)))
    pages = [p1()] + calc + [p2(), p3(), p4(), p_bh(), p5()]
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>' % (_font_css(), CSS, ''.join(pages))

CHECK = """()=>{const o=[];document.querySelectorAll('.page').forEach((p,i)=>{const B=p.getBoundingClientRect();
 p.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(!r.width||!r.height)return;
  if(r.bottom>B.bottom+0.5||r.right>B.right+0.5) o.push('p'+(i+1)+' 이탈 '+(e.innerText||'').slice(0,20));});});
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
                    '계산제외목록': rc['계산제외목록'], '구조별': S.audit(RID)['구조별'], '생성쪽수': 6 + len(re.findall(r'class="page calcpg"', h)), '지면검사': warn,
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
