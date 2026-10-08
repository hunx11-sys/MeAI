# -*- coding: utf-8 -*-
"""GA 스마트 제안서(v5 · 표지 + 보장요약 + 암보장 + 뇌·심보장 + 예상 보장금액 세부내역)의 모든 칸을 **데이터**로 적은 사양 + 엔진 대조 도구.

  python3 ga_spec.py <out.json> [설계서.pdf ...]

· CELLS : ga_proposal.py 가 그리는 순서 그대로의 칸 목록. 칸마다 사례(kcd·tags·itc_events)·집계 방식·표시 조건을 적는다.
  ga_proposal 은 이 목록의 사례를 그대로 계산해 지면을 그리므로(cell_value) 지면과 사양이 어긋날 수 없다.
· run_universe() : 특약 마스터 전부를 각 칸 사례에 태워 어느 특약이 잡히는지, 왜 빠지는지(로그)를 뽑는다.
· run_design()   : 설계서 1건의 담보로 칸 값을 계산하고, 만든 GA HTML 의 숫자 순서와 대조한다.
숫자를 만들거나 추정하지 않는다 — 전부 scen_engine.pay_lines 결과(또는 설계서 가입금액)를 그대로 적는다.
GA 양식 v5(2026-10-08 GA 내부 회의 목업) : 진단금 전이암 · 뇌졸중/뇌혈관/급성심근경색/허혈성심장 · 산정특례(뇌혈관·심장) ·
주요수술 10종 명칭 변경(디스크절제술·인공관절치환술·담낭절제술·복강경 수술·경요도 전립선절제술) · 간병인 「보내줌」·미사용·간호간병 합산 · 보장요약 뇌심 열 = 진단금 / 뇌 치료 및 수술 / 심장 치료 및 수술 / 중증치료(산정특례 열 삭제 2026-10-08)."""
import sys, os, json, re, copy, collections
PS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PS)
import scen_engine as S, engine as itc, matcher, pipeline
import build_all as BA
import ga_care as CARE
won = CARE.won

BASE_T = dict(cause='질병', hosp='상급종합', room=None, days=0, grp=[], dx=None)
BG, HG = ['뇌혈관질환'], ['심장질환']

def sc(kcd, ev, **kw):
    tg = dict(BASE_T); tg.update(kw); return {'kcd': kcd, 'tags': tg, 'itc_events': copy.deepcopy(ev or [])}
def sc_dx(kcd, fam, grp=None):
    return {'kcd': kcd, 'tags': dict(dx=fam, cause='질병', grp=list(grp or [])), 'itc_events': []}
def sc_itc(kcd, key, hosp='상급종합', grp=None, fam=None, extra=None):
    tg = dict(cause='질병', hosp=hosp, room=None, days=0, grp=list(grp or []), dx=fam)
    ev = [['치료', key, '', [key]] + ([extra] if extra else [])]
    return {'kcd': kcd, 'tags': tg, 'itc_events': ev}

# ── 주요수술보장 10칸 (GA v5 명칭) — (시술명, 질병코드, 사례 조건, 통합치료비 사건). 조건의 1-5종 항목·1-7종 코드·마취는 가정값(수술분류표 근거)
#    adm='out' = 통원·당일입원 수술 가정(백내장·갑상선 고주파·맘모톰 — 신수술비[기본] 통원 세부보장 판정용), 나머지는 2일 이상 입원 수술
GA_DZ = collections.OrderedDict([
 ('백내장',      ('인공수정체 삽입',   'H25.9', dict(surg='71',   surg7='C061', grp=['백내장'], adm='out'),                       [['수술', '수정체 유화술', '', ['surg'], {'j': 1}]])),
 ('디스크',      ('디스크절제술',      'M51',   dict(surg='9',    surg7='B174', grp=['다빈도62대질병'], anes=1),                 [['수술', '추간판 절제술', '', ['surg'], {'j': 3}]])),     # 1-5종 9 척추골·추간판 관혈수술 3종 · 1-7종 B174 척추후궁절제술 및 추간판제거술
 ('무릎관절질환', ('인공관절치환술',    'M17',   dict(surg='13-2', surg7='I032', grp=['관절염,생식기질환'], anes=1),              [['수술', '슬관절 전치환술', '', ['surg', 'arthroplasty'], {'j': 2}]])),   # 1-5종 13-2 사지관절 관혈수술 2종 · 1-7종 I032 슬관절 전치환술
 ('담석증',      ('담낭절제술',        'K80.0', dict(surg='36',   surg7='H107', grp=['다빈도62대질병'], anes=1),                 [['수술', '복강경 담낭 절제', '', ['surg'], {'j': 2}]])),   # 1-5종 36 담낭 관혈수술(담석증 K80 은 2종) · 1-7종 H107 복강경 담낭절제술
 ('맹장염',      ('충수절제술',        'K35',   dict(surg='41',   surg7='G212', grp=[], anes=1),                               [['수술', '충수 절제', '', ['surg'], {'j': 2}]])),
 ('갑상선결절',   ('고주파절제술',      'D34',   dict(surg='88-2', surg7='K080', hc=['PZ612'], grp=['다빈도62대질병'], adm='out'), [['수술', '고주파절제술', '', ['surg'], {'j': 2}]])),
 ('유방양성종양', ('맘모톰',            'D24',   dict(surg='4',    surg7='J071', grp=['유방의장애'], adm='out'),                   [['수술', '맘모톰', '', ['surg'], {'j': 1}]])),
 ('자궁근종',    ('복강경 수술',       'D25.9', dict(surg='52',   surg7='N031', grp=['다빈도62대질병'], anes=1),                 [['수술', '복강경 근종절제술', '', ['surg'], {'j': 2}]])),  # 1-5종 52 자궁 관혈수술 2종 · 1-7종 N031 복강경 단순 자궁 수술(악성 제외)
 ('전립선비대증', ('경요도 전립선절제술', 'N40',  dict(surg='88-3', surg7='M022', grp=['관절염,생식기질환']),                      [['수술', '경요도 전립선절제술', '', ['surg'], {'j': 1}]])),  # 1-5종 88-3 비뇨·생식기 내시경 수술 1종 · 1-7종 M022 기타 전립선 적출술
 ('골절진단',    ('골절수술',          'S52.5', dict(cause='상해', surg='13-2', surg7='I286', grp=[]),                           [['수술', '골절 고정술', '', ['surg'], {'j': 2}]])),
])
DZ_ORDER = list(GA_DZ)
def sc_dz(name, hosp):
    proc, kcd, tg, ev = GA_DZ[name]
    return sc(kcd, ev, **dict(tg, hosp=hosp))

# ── 암 사례 ──  표적·면역 1종 = 약물 1종(치료 1개)만 받은 것(GA 2026-10-02) · two = 표적+면역 2종(2종이상 담보 포함, 3종이상 제외) · two3 = 3종
CS = {
 'robot':   sc('C16', [['수술', '로봇수술', '', ['surg', 'robot'], {'nc': 1}]], surg='C1', surg7='G081'),
 'lap':     sc('C16', [['수술', '복강경', '', ['surg']]], surg='C1', surg7='G081'),
 'open':    sc('C16', [['수술', '개복', '', ['surg']]], surg='C1', surg7='G082'),
 'endo':    sc('C16', [['수술', '내시경 절제', '', ['surg']]], surg='C2', surg7='G503'),
 'chemo':   sc('C16', [['항암', '항암약물(급여)', '', ['chemo']]], chemo=1),
 'target1': sc('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=1),
 'immune1': sc('C16', [['항암', '면역(비급여)', '', ['chemo', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=1),
 'two':     sc('C16', [['항암', '표적+면역(비급여) 2종', '', ['chemo', 'target', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=2),
 'two3':    sc('C16', [['항암', '표적+면역(비급여) 3종', '', ['chemo', 'target', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=3),
 'rad':     sc('C16', [['방사선', '항암방사선(급여)', '', ['rad']]]),
 'imrt':    sc('C16', [['방사선', '세기조절', '', ['rad', 'imrt']]]),
 'proton':  sc('C16', [['방사선', '양성자(비급여)', '', ['rad', 'proton'], {'nc': 1}]]),
 'carbon':  sc('C16', [['방사선', '중입자(비급여)', '', ['rad', 'carbon'], {'nc': 1}]]),
}
DXS = {'일반암': sc_dx('C16', 'cancer'), '유사암': sc_dx('C73', 'sim_cancer'), '전이암': sc_dx('C78.7', 'cancer')}   # 전이암 = 간 전이(C78.7) · 전이암 담보 줄만(meta_only)
# 뇌·심 진단 — 뇌졸중 : 뇌경색(I63) · 뇌혈관 : 비파열 뇌동맥류(I67.1 · 뇌졸중이 아닌 뇌혈관질환) · 급성심근경색(I21) · 허혈성심장 : 협심증(I20)
BDX = {'뇌졸중': sc_dx('I63', 'brain', BG), '뇌혈관': sc_dx('I67.1', 'brain', BG)}
HDX = {'허혈성심장': sc_dx('I20', 'heart', HG + ['허혈성심장질환']), '급성심근경색': sc_dx('I21', 'heart', HG + ['허혈성심장질환'])}
def brain_steps(hosp):
    return [('혈전용해치료', sc('I63', [['시술', '혈전용해', '', ['thromb']]], series='brain', hosp=hosp)),
            ('혈전용해+혈전제거술', sc('I63', [['시술', '혈전용해', '', ['thromb']], ['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], hosp=hosp, acts=['thrombectomy'])),
            ('코일색전술', sc('I67.1', [['시술', '코일 색전술', '', ['surg']]], surg='88-1', surg7='B016', grp=BG + ['특정31대질병'], hosp=hosp, anes=1)),
            ('개두 수술', sc('I61', [['수술', '혈종제거 개두술', '', ['surg']]], surg='59', surg7='B031', grp=BG + ['뇌졸중', '뇌출혈', '특정31대질병'], hosp=hosp, anes=1))]
def heart_steps(hosp):
    return [('혈전용해치료', sc('I21', [['시술', '혈전용해', '', ['thromb']]], series='heart', hosp=hosp)),
            ('혈전용해+혈전제거술', sc('I21', [['시술', '혈전용해', '', ['thromb']], ['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='F121', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp, acts=['thrombectomy'])),
            ('스텐트삽입술', sc('I20', [['시술', '스텐트 삽입', '', ['surg']]], surg='88-1', surg7='F133', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp)),
            ('개흉 수술', sc('I20', [['수술', '관상동맥 우회술', '', ['surg']]], surg='24', surg7='F042', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp, anes=1, anes_h=6))]
_b, _h = brain_steps('상급종합'), heart_steps('상급종합')
# 보장요약 '뇌 치료 및 수술' · '심장 치료 및 수술' (GA 2026-10-08 : 산정특례 열 삭제, 뇌·심장을 따로) — 혈전용해 / 혈전제거(기계적 혈전제거술만 · 카테터 수술 → 수술비·1-5종·기계적혈전제거술 특약·통합치료비 수술 항목 합산, 혈전용해 담보는 안 들어감) /
#   혈전용해+혈전제거(두 시술 합산 · 진단및치료비Ⅱ 특정혈전치료비도 여기) / 스텐트수술(뇌 : 경동맥 협착 I65.2 경피적 뇌혈관 수술 B026 · 심장 : 협심증 I20 관상동맥 스텐트 F133). 모두 상급종합병원 가정
_b_thrombectomy = sc('I63', [['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], hosp='상급종합', acts=['thrombectomy'])
_b_stent = sc('I65.2', [['시술', '스텐트 삽입', '', ['surg']]], surg='88-1', surg7='B026', grp=BG + ['뇌졸중', '특정31대질병'], hosp='상급종합')
_h_thrombectomy = sc('I21', [['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='F121', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp='상급종합', acts=['thrombectomy'])
P1_TX_B = [('혈전용해', _b[0][1]), ('혈전제거', _b_thrombectomy), ('혈전용해+혈전제거', _b[1][1]), ('스텐트수술', _b_stent)]
P1_TX_H = [('혈전용해', _h[0][1]), ('혈전제거', _h_thrombectomy), ('혈전용해+혈전제거', _h[1][1]), ('스텐트수술', _h[2][1])]
SEV = [('중환자실치료', 'icu'), ('부분체외순환', 'ecmo'), ('지속적신대체요법', 'crrt'), ('인공호흡기', 'vent'), ('저체온요법', 'hypo')]
EX_CA = [('암내시경', 'x_endo'), ('MRI촬영', 'x_mri'), ('PET', 'x_pet'), ('특정단일유전자', 'x_gene'), ('초음파', 'x_us'), ('CT촬영', 'x_ct'), ('특정생검조직', 'x_bio'), ('특정NGS유전자', 'x_ngs')]
EX_BH = [('MRI 촬영', 'x_mri'), ('PET', 'x_pet'), ('CT 촬영', 'x_ct')]

# ═══════════════ 칸 목록 (렌더 순서) ═══════════════
CELLS = []; KEY = {}
def add(key, page, section, row, col, kind, sc_=None, mode='first', need=None, direct=None, note='', sc_name='', na_if_empty=False):
    """key : ga_proposal 이 칸 값을 꺼내는 이름 · need : 담보명(띄어쓰기 무시)에 이 말이 모두 들어간 가입담보가 없으면 「미가입」"""
    c = dict(id='P%d-%03d' % (page, len([x for x in CELLS if x['page'] == page]) + 1), key=key, page=page, section=section, row=row, col=col,
             label=('%s · %s' % (row, col) if row else col), kind=kind, sc=sc_, sc_name=sc_name, mode=mode, need=need, direct=direct, note=note, na_if_empty=na_if_empty)
    assert key not in KEY, key
    CELLS.append(c); KEY[key] = c

# ── 1쪽 보장요약 ──
_ca1 = [('진단금', [('일반암', 'dx.일반암', DXS['일반암'], 'first', None, '일반암 진단(C16 위암)'),
                  ('유사암', 'dx.유사암', DXS['유사암'], 'first', None, '유사암 진단(C73 갑상선암)'),
                  ('전이암', 'dx.전이암', DXS['전이암'], 'meta_only', ['전이암', '진단'], '전이암 진단(C78.7 간 전이) — 담보명에 「전이암」이 든 진단비 줄만 · 일반암 진단비는 원발암에서 이미 받은 것으로 보고 제외')]),
        ('수술', [('다빈치로봇', 'sg.robot', CS['robot'], 'first', None, '위암 다빈치로봇수술(비급여)'), ('내시경', 'sg.endo', CS['endo'], 'first', None, '위암 내시경 절제'),
                 ('복강경/흉강경', 'sg.lap', CS['lap'], 'first', None, '위암 복강경수술'), ('개복/개흉', 'sg.open', CS['open'], 'first', None, '위암 개복수술')]),
        ('항암약물', [('화학항암', 'cm.chemo', CS['chemo'], 'first', None, '위암 항암약물(급여)'), ('표적항암', 'cm.target1', CS['target1'], 'first', None, '위암 표적항암(비급여, 약물 1종)'),
                   ('면역항암', 'cm.immune1', CS['immune1'], 'first', None, '위암 면역항암(비급여, 약물 1종)'),
                   ('표적(면역) 2가지 약물', 'cm.two', CS['two'], 'first', None, '위암 표적+면역항암(비급여) 약물 2종 — 항암약물·항암방사선약물·표적·면역·암통합치료비(면역항암 가정)·(2종이상)·(2종및3종이상) 담보 합산, 3종이상 담보 제외')]),
        ('항암방사선', [('항암방사선', 'rd.rad', CS['rad'], 'first', None, '위암 항암방사선(급여)'), ('세기조절', 'rd.imrt', CS['imrt'], 'first', None, '위암 세기조절방사선'),
                    ('양성자', 'rd.proton', CS['proton'], 'first', None, '위암 양성자(비급여)'), ('중입자', 'rd.carbon', CS['carbon'], 'first', None, '위암 중입자(비급여)')])]
for i in range(4):
    for h, items in _ca1:
        if i >= len(items): continue
        n, k, s_, md, need, nm = items[i]
        add('p1.ca.' + k, 1, '암보장', h, n, 'engine', s_, md, need=need, sc_name=nm, na_if_empty=(h == '진단금'))
_bh1 = [('진단금', [('뇌졸중', 'dx.뇌졸중', BDX['뇌졸중'], 'first', None, '뇌졸중 진단(I63 뇌경색)'), ('뇌혈관', 'dx.뇌혈관', BDX['뇌혈관'], 'first', None, '뇌혈관질환 진단(I67.1 비파열 뇌동맥류 · 뇌졸중이 아닌 뇌혈관질환)'),
                  ('급성심근경색', 'dx.급성심근경색', HDX['급성심근경색'], 'first', None, '급성심근경색 진단(I21)'), ('허혈성심장', 'dx.허혈성심장', HDX['허혈성심장'], 'first', None, '허혈성심장질환 진단(I20 협심증)')]),
        ('뇌 치료 및 수술', [(n, 'txb.' + n, s_, 'first', None, '뇌 · ' + n + ' · 상급종합병원') for n, s_ in P1_TX_B]),
        ('심장 치료 및 수술', [(n, 'txh.' + n, s_, 'first', None, '심장 · ' + n + ' · 상급종합병원') for n, s_ in P1_TX_H]),
        ('중증치료', [(n, 'sev.' + k, sc_itc('I63', k, grp=BG), 'itc_only', None, '뇌경색(I63) %s · 상급종합병원 · 통합치료비 항목만' % n) for n, k in SEV])]
for i in range(5):
    for h, items in _bh1:
        if i >= len(items): continue
        n, k, s_, md, need, nm = items[i]
        add('p1.bh.' + k, 1, '뇌·심보장', h, n, 'engine', s_, md, need=need, sc_name=nm, na_if_empty=(h == '진단금'))
for n in DZ_ORDER:
    add('p1.dz.' + n, 1, '주요수술보장', n, GA_DZ[n][0], 'engine', sc_dz(n, '병원'), 'first', sc_name='%s %s (%s) · 병원급' % (n, GA_DZ[n][0], GA_DZ[n][1]))
add('p1.care.hosp',   1, '간병인보장', '간병인지원(현물지원)', '병·의원(요양병원제외)', 'care', direct='hosp',   note='「간병인지원 질병입원일당(1일이상 180일한도)」 가입 → 보내줌 · 없으면 미가입(181일이상만 가입해도 미가입 · GA 결정 2026-10-08)')
add('p1.care.nh',     1, '간병인보장', '간병인지원(현물지원)', '요양병원',            'care', direct='nh',     note='「간병인지원 요양성특정질병입원일당(…)(요양병원)」 또는 「간병인지원 질병입원일당(1일이상 180일한도)」 가입 → 보내줌 · 둘 다 없으면 미가입(소유자 2026-10-08)')
add('p1.care.nurse',  1, '간병인보장', '간병인지원(현물지원)', '간호간병통합서비스 1일', 'care', direct='nurse', note='「간병인지원 질병입원일당(간호·간병통합서비스 사용추가보장)」 가입금액 + 간병인 미사용 시 입원일당(Ⅰ 가입금액 · Ⅶ 5천원 · Ⅵ 0)')
add('p1.care.unused', 1, '간병인보장', '간병인지원(현물지원)', '미사용시 1일',        'care', direct='unused', note='간병인지원 질병입원일당 담보의 설계서 금액(Ⅰ 가입금액 · Ⅶ 「또는 5천원」 · Ⅵ 금액 없음 → 0)')
add('p1.care.use_gen',   1, '간병인보장', '간병인사용(금액지원)', '간병인 1일',          'care', direct='use_gen',   note='「간병인사용 질병입원일당」(요양병원 전용·간호간병 제외) 1일이상 담보 가입금액 합')
add('p1.care.use_nh',    1, '간병인보장', '간병인사용(금액지원)', '요양병원 1일',        'care', direct='use_nh',    note='「간병인사용 질병입원일당(…)(요양병원)」 가입금액')
add('p1.care.use_nurse', 1, '간병인보장', '간병인사용(금액지원)', '간호간병통합서비스 1일', 'care', direct='use_nurse', note='「간호·간병통합서비스 사용 질병입원일당」(단독 특약) 가입금액')

# ── 2쪽 암보장 ──
for n, k in EX_CA:
    add('p2.ex.' + k, 2, '암검사(8종)', '', n, 'engine', sc_itc('C16', k, fam='cancer'), 'itc_only', sc_name='위암(C16) %s · 상급종합병원 · 통합치료비 항목만' % n)
add('p2.dx.일반암', 2, '암진단', '', '일반암', 'engine', DXS['일반암'], 'first', sc_name='일반암 진단(C16)', na_if_empty=True)
add('p2.dx.유사암', 2, '암진단', '', '유사암', 'engine', DXS['유사암'], 'first', sc_name='유사암 진단(C73)', na_if_empty=True)
add('p2.dx.전이암', 2, '암진단', '', '전이암', 'engine', DXS['전이암'], 'meta_only', need=['전이암', '진단'], sc_name='전이암 진단(C78.7) · 전이암 담보 줄만')
SG = [('내시경수술', 'endo'), ('개복·개흉수술', 'open'), ('복강경,흉강경', 'lap'), ('다빈치로봇암수술', 'robot')]
ROWS3 = (('최초 지급시', 'first'), ('반복(연 1회)', 'year'), ('수술할 때마다', 'each'))
for rl, md in ROWS3:
    for n, k in SG: add('p2.sg.%s.%s' % (k, md), 2, '암수술', rl, n, 'engine', CS[k], md, sc_name='위암 %s' % n)
CM = [('화학항암약물', 'chemo'), ('표적항암약물', 'target1'), ('면역항암약물(카티포함)', 'immune1')]
for rl, md in ROWS3[:2]:
    for n, k in CM: add('p2.cm.%s.%s' % (k, md), 2, '항암약물치료', rl, n, 'engine', CS[k], md, sc_name='위암 %s(약물 1종)' % n)
add('p2.cm.two',  2, '항암약물치료', '표적(면역) 개수별', '2가지약물', 'engine', CS['two'],  'first', sc_name='위암 표적+면역항암(비급여) 약물 2종 — 보장요약 「표적(면역) 2가지 약물」 칸과 같은 사례')
add('p2.cm.two3', 2, '항암약물치료', '표적(면역) 개수별', '3가지약물', 'engine', CS['two3'], 'first', sc_name='위암 표적+면역항암(비급여) 약물 3종 — (3종이상)·(2종및3종이상 3종 구분) 담보까지')
RD = [('항암 방사선', 'rad'), ('세기조절 방사선', 'imrt'), ('양성자 방사선', 'proton'), ('중입자 방사선', 'carbon')]
for rl, md in ROWS3[:2]:
    for n, k in RD: add('p2.rd.%s.%s' % (k, md), 2, '항암방사선치료', rl, n, 'engine', CS[k], md, sc_name='위암 %s' % n)
add('p2.rh.in',  2, '암재활치료', '연 20회', '입원 재활', 'engine', sc_itc('C16', 'rehab', fam='cancer', extra={'n': 20}), 'itc_only', sc_name='위암 재활치료 20일 · 상급종합 · 통합치료비 항목만')
add('p2.rh.out', 2, '암재활치료', '연 20회', '외래 재활', 'engine', sc_itc('C16', 'rehab', fam='cancer', extra={'n': 20}), 'itc_only', sc_name='(입원 칸과 같은 값)', note='입원·외래 구분 없이 같은 사례 값')
add('p2.dis', 2, '암후유장해', '', '3-100% 암후유장해', 'direct', direct=dict(keys=['암', '후유장해'], exclude=[]), note="담보명에 '암'과 '후유장해'가 모두 들어간 담보의 가입금액 합 — 계산 아님")

# ── 3쪽 뇌·심보장 ──
for n, k in EX_BH:
    add('p3.ex.' + k, 3, '뇌·심검사(3종)', '', n, 'engine', sc_itc('I63', k, grp=BG), 'itc_only', sc_name='뇌경색(I63) %s · 상급종합 · 통합치료비 항목만' % n)
for n, s_, nm in (('뇌혈관', BDX['뇌혈관'], '뇌혈관질환 진단(I67.1)'), ('뇌졸중', BDX['뇌졸중'], '뇌졸중 진단(I63)'), ('허혈성심장', HDX['허혈성심장'], '허혈성심장질환 진단(I20)'), ('급성심근경색', HDX['급성심근경색'], '급성심근경색 진단(I21)')):
    add('p3.dx.' + n, 3, '뇌·심진단', '', n, 'engine', s_, 'first', sc_name=nm, na_if_empty=True)
for rl, md in ROWS3:
    for i, (n, s_) in enumerate(brain_steps('상급종합')): add('p3.b%d.%s' % (i, md), 3, '뇌질환 치료 및 수술', rl, n, 'engine', s_, md, sc_name='%s · 뇌 · 상급종합' % n)
for rl, md in ROWS3:
    for i, (n, s_) in enumerate(heart_steps('상급종합')): add('p3.h%d.%s' % (i, md), 3, '심질환 치료 및 수술', rl, n, 'engine', s_, md, sc_name='%s · 심장 · 상급종합' % n)
for n, k in SEV:
    add('p3.sev.' + k, 3, '뇌·심 중증치료', '반복(연 1회)', n, 'engine', sc_itc('I63', k, grp=BG), 'itc_only', sc_name='뇌경색(I63) %s · 상급종합 · 통합치료비 항목(연간)' % n)
add('p3.rh.in',  3, '뇌·심 재활치료', '연 15회', '입원 재활', 'engine', sc_itc('I63', 'rehab', grp=BG, extra={'n': 15}), 'itc_only', sc_name='뇌경색 재활 15일 · 상급종합 · 통합치료비 항목만')
add('p3.rh.out', 3, '뇌·심 재활치료', '연 15회', '외래 재활', 'engine', sc_itc('I63', 'rehab', grp=BG, extra={'n': 15}), 'itc_only', sc_name='(입원 칸과 같은 값)')

# ═══════════════ 계산 ═══════════════
_CACHE = {}
def clear_cache(): _CACHE.clear()
def pay(riders, s_):
    """같은 사례는 한 설계서 안에서 한 번만 계산한다(ga_proposal.load 가 clear_cache). 감사 로그(S.ISSUES)는 지우지 않고 이 호출분만 돌려준다"""
    k = (id(riders), json.dumps(s_, sort_keys=True, ensure_ascii=False))
    if k in _CACHE: return _CACHE[k]
    n0 = len(S.ISSUES)
    L = S.pay_lines(riders, copy.deepcopy(s_))
    _CACHE[k] = (L, list(S.ISSUES[n0:]))
    return _CACHE[k]

def _ns(x): return re.sub(r'\s+', '', x or '')
def counts(l, mode):
    """이 지급 줄이 칸의 집계 방식(mode)에 들어가는 금액"""
    if mode == 'first': return l['amt']
    if mode == 'year': return l['amt'] if l.get('freq') != 'once' else 0
    if mode == 'each': return l.get('each', l['amt'] if l.get('freq') == 'each' else 0)
    if mode == 'itc_only': return l['amt'] if l.get('group') == '통합치료비' else 0
    if mode == 'ms_only': return l['amt'] if l.get('itc') == 'ms' else 0
    if mode == 'meta_only': return l['amt'] if '전이암' in _ns(l['name']) and '진단' in _ns(l['name']) else 0   # 전이암 진단비 줄만(전이암 치료비 제외)
    if mode == 'reg_only': return l['amt'] if l.get('rule') == 'dx_special_case' else 0     # 산정특례대상 진단비 줄만
    return 0

# 상해 통합치료비(실속형) — 엔진(pay_lines)은 이 특약을 계산하지 않고 스마트 제안서(gen2.inj_itc_pay)가 inj_itc.json 금액표로 따로 계산한다.
# GA 칸도 같은 금액표로 더한다(v8.75 · 전에는 골절 칸에서 빠져 0). 금액표에 없는 가입금액이면 계산하지 않고 로그만 남긴다(CLAUDE.md 2).
INJ_ITC = json.load(open(os.path.join(PS, 'inj_itc.json'), encoding='utf-8'))
INJ_ACT = {'MRI': 'x_mri', 'CT': 'x_ct', '골밀도': 'x_bmd', '흡인': 'aspir', '신경차단': 'block', '화상처치': 'burn', '도수정복': 'reduction',
           '창상봉합술치료(안면부,': 'suture_face', '창상봉합술치료(안면부이외': 'suture', '깁스': 'cast', '부목': 'splint', 'CRRT': 'crrt',
           '인공호흡기': 'vent', '저체온': 'hypo', '체외순환': 'ecmo', '전신마취': 'anes6', '중환자실': 'icu'}   # gen2.INJ_ACT 와 같다(재활은 GA 상해 사례에 없음)
def inj_lines(riders, s_):
    if (s_.get('tags') or {}).get('cause') != '상해': return [], []
    ev = s_.get('itc_events') or []
    acts = {k for e in ev if len(e) > 3 for k in e[3]}
    js = {int(e[4]['j']) for e in ev if len(e) > 4 and isinstance(e[4], dict) and e[4].get('j')}
    out, iss = [], []
    for r in riders:
        for k, tiers in INJ_ITC.items():
            if S.nname(k) not in (S.nname(r['name']), S.noren(r['name'])): continue
            items = tiers.get(str(int(r['man']))) if r.get('man') else None
            if not items:
                iss.append({'구분': '계산제외', '담보': r['name'], '사유': '가입금액 %s만원이 약관 지급금액표(inj_itc.json)에 없음' % r.get('man')}); continue
            parts, tot = [], 0
            for it in items:
                l = it['l']
                if it['c'].startswith('수술'): amt = it['amt'] if 'surg' in acts and int(l[0]) in js else 0
                else:
                    key = next((v for kk, v in INJ_ACT.items() if kk in l), None); amt = it['amt'] if key and key in acts else 0
                if amt: parts.append('%s %s' % (l, format(amt, ','))); tot += amt
            if tot: out.append(dict(name=r['name'], amt=float(min(tot, r['man'])), why=' · '.join(parts), rule='itc', group='통합치료비', freq='each', no=r.get('no')))
    return out, iss

def has_need(c, riders):
    if not c.get('need'): return True
    return any(all(_ns(w) in _ns(r['name']) for w in c['need']) and (r.get('man') or 0) > 0 for r in riders)

def cell_value(c, riders):
    """칸 값 — (값, 지급 줄, 로그). 값 : 숫자(만원) / None(미가입) / '보내줌' / '면책'. 근거 담보는 줄 목록(name·amt·why·rule)으로 돌려준다"""
    k = c['kind']
    if k == 'care':
        cc = CARE.cells(riders)[c['direct']]
        v, rs = cc
        lines = [dict(name=r['name'], amt=(CARE.daily(r) if c['direct'] in ('unused', 'nurse') and '간호·간병' not in r['name'] else r['man']), why='설계서 가입금액 그대로' if r['man'] else '설계서 금액란(또는 N천원)', rule='direct', dementia=r.get('dementia')) for r in rs]
        if c['direct'] in ('hosp', 'nh'): return ('보내줌' if v else None), lines, []
        return v, lines, []
    if k == 'direct':
        d = c['direct']
        rs = [r for r in riders if all(a in r['name'] for a in d['keys']) and not any(x in r['name'] for x in d.get('exclude', []))]
        return (None if not rs else sum(r['man'] for r in rs)), [dict(name=r['name'], amt=r['man'], why='가입금액 그대로', rule='direct') for r in rs], []
    L, iss = pay(riders, c['sc'])
    il, ii = inj_lines(riders, c['sc'])
    if il or ii: L, iss = L + il, iss + ii
    if c['mode'] == 'ms_only' and not any(r.get('itc') == 'ms' for r in riders): return None, L, iss
    if not has_need(c, riders): return None, L, iss
    if c.get('na_if_empty') and not any(counts(l, c['mode']) for l in L): return None, L, iss   # 진단금 칸 : 이 진단에 지급되는 가입담보가 없으면 「미가입」(v8.75 · 전에는 0)
    return float(sum(counts(l, c['mode']) for l in L)), L, iss

def tokens_of(v):
    if v is None: return ['미가입']
    if isinstance(v, str): return [v]
    return [won(v)]
def cell_tokens(c, riders):
    v, L, iss = cell_value(c, riders)
    return tokens_of(v), L, iss

# ═══════════════ 특약 마스터 우주 ═══════════════
DB = matcher.DB                      # db.json + 스마트 제안서 전용 보강 마스터(db_terms_extra.json)
DBID = {r['id']: r for r in DB['riders']}
PARENTS = {r['id'].split('-')[0] for r in DB['riders'] if re.match(r'^[^-]+-\d+$', r['id'])}
def universe():
    """특약 마스터 전체. 단 세부보장이 따로 있는 부모 특약(통81 → 통81-1·통81-2 등)은 뺀다 — 설계서에는 부모가
    「세부보장참조」 행(금액 없음)으로 실리고 금액은 세부보장 행에 붙으므로, 부모 이름으로 계산하면 세부보장과 겹친다."""
    out = []
    for rec in DB['riders']:
        if rec['id'] in PARENTS: continue
        if re.search(r'수술비\s*\(1-7종', rec['n']): continue
        name = rec['n']
        m, b, s2 = matcher.match(name)
        iid = S.itc_id(name); lsid = S.ls_id(name)
        man = 100
        if iid:
            man = min(int(k) for k in itc.AMT[itc.RM[iid]['ty']])
        elif lsid:
            t = (S.LS.get(lsid) or {}).get('tiers') or {}
            man = int(float(min(t, key=lambda x: float(x)))) if t else 100
        out.append({'no': rec['id'], 'name': name, 'man': man, 'cat': rec.get('c'), 'codes': rec.get('k') or [], 'excl': rec.get('x') or [],
                    'hc': rec.get('hc') or [], 'benefit': b, 'sub': s2, 'matched': True, 'itc': iid, 'product': rec.get('p'), 'db_id': rec['id']})
    for cause in ('질병', '상해'):
        parent = next((r for r in DB['riders'] if S.nname(r['n']) == S.nname('수술비(1-7종, 연간3회한)[%s]' % cause)), None)
        for j in range(1, 8):
            nm = '┗ 수술비[%s%d종]' % (cause, j)
            out.append({'no': 'row-%s%d' % (cause, j), 'name': nm, 'man': 100, 'cat': (parent or {}).get('c'), 'codes': (parent or {}).get('k') or [], 'excl': (parent or {}).get('x') or [],
                        'hc': [], 'benefit': None, 'sub': None, 'matched': True, 'itc': None, 'product': '설계서 종별 행', 'db_id': 'row-%s%d' % (cause, j),
                        'via': (parent or {}).get('n')})
    p15 = next((r for r in DB['riders'] if r['n'] == '수술비Ⅱ(1-5종)'), None)
    for cause in ('질병', '상해'):
        for j in range(1, 6):
            nm = '수술비Ⅱ(1-5종)[%s%d종]' % (cause, j)
            out.append({'no': 'row15-%s%d' % (cause, j), 'name': nm, 'man': 100, 'cat': (p15 or {}).get('c'), 'codes': [], 'excl': (p15 or {}).get('x') or [], 'hc': [],
                        'benefit': '%s%d종' % (cause, j), 'sub': None, 'matched': True, 'itc': None, 'product': '설계서 종별 행', 'db_id': 'row15-%s%d' % (cause, j), 'via': (p15 or {}).get('n')})
            pp = next((r for r in DB['riders'] if r['n'] == '%s 1-5종수술비(plus)(연간2회이상)' % cause), None)
            nm = '%s 1-5종수술비(plus)(연간2회이상)(%d종,연간1회한)' % (cause, j)
            out.append({'no': 'rowplus-%s%d' % (cause, j), 'name': nm, 'man': 100, 'cat': (pp or {}).get('c'), 'codes': [], 'excl': (pp or {}).get('x') or [], 'hc': [],
                        'benefit': None, 'sub': '%d종,연간1회한' % j, 'matched': True, 'itc': None, 'product': '설계서 종별 행', 'db_id': 'rowplus-%s%d' % (cause, j), 'via': (pp or {}).get('n')})
    return out

def add_design_only(uni, riders_lists):
    """설계서에는 있는데 마스터에 없는 담보명 — 규칙표만으로 계산되는 담보. 우주에 덧붙여 어느 칸에 잡히는지 함께 본다."""
    have = {S.nname(r['name']) for r in uni}
    for riders in riders_lists:
        for r in riders:
            if S.nname(r['name']) in have: continue
            have.add(S.nname(r['name']))
            iid = S.itc_id(r['name']); lsid = S.ls_id(r['name']); man = 100
            if iid: man = min(int(k) for k in itc.AMT[itc.RM[iid]['ty']])
            elif lsid:
                t = (S.LS.get(lsid) or {}).get('tiers') or {}
                man = int(float(min(t, key=lambda x: float(x)))) if t else 100
            m, _b, _s = matcher.match(r['name'])
            mid = (m or {}).get('id') or r.get('via_id')
            prod = ('설계서 표기 · 마스터 %s(%s) 매칭' % (mid, (m or DBID.get(mid) or {}).get('p', ''))) if (r.get('matched') and mid) else '설계서 담보(마스터에 없음)'
            uni.append({'no': 'design-%s' % S.nname(r['name']), 'name': r['name'], 'man': man, 'cat': r.get('cat'), 'codes': r.get('codes') or [], 'excl': r.get('excl') or [], 'hc': r.get('hc') or [],
                        'benefit': r.get('benefit'), 'sub': r.get('sub'), 'matched': r.get('matched'), 'itc': iid, 'product': prod, 'db_id': 'design-%s' % S.nname(r['name']), 'via': mid})
    return uni

def run_universe(uni):
    res = {}
    clear_cache()
    for c in CELLS:
        if c['kind'] != 'engine': continue
        L, iss = pay(uni, c['sc'])
        byno = {r['db_id']: r for r in uni}
        rows = []
        for l in L:
            r = byno.get(l.get('no')) if l.get('no') in byno else None
            rows.append(dict(name=l['name'], db_id=l.get('no'), product=(r or {}).get('product'), rule=l.get('rule'), why=l['why'], group=l['group'],
                             freq=l.get('freq'), amt=l['amt'], man=(r or {}).get('man'), each=l.get('each'), in_row=None, counted=counts(l, c['mode']) > 0,
                             itc=l.get('itc'), benefit=(r or {}).get('benefit'), sub=(r or {}).get('sub'), ncodes=len((r or {}).get('codes') or []),
                             nexcl=len((r or {}).get('excl') or []), nhc=len((r or {}).get('hc') or [])))
        res[c['id']] = dict(lines=rows, issues=iss)
    clear_cache()
    return res

# ═══════════════ 설계서 대조 ═══════════════
TOKEN_RE = re.compile(r'<b class="v[^"]*">([^<]+)<i>만원</i></b>|<span class="na">(미가입|면책)</span>|<span class="txt">(보내줌|지원가능)</span>')
def run_design(pdf, html=None):
    riders = pipeline.read_riders(pdf)
    meta = BA.auto_meta(pdf)
    cells, toks = {}, []
    clear_cache()
    for c in CELLS:
        t, L, iss = cell_tokens(c, riders)
        cells[c['id']] = dict(tokens=t, lines=[dict(name=l['name'], amt=l['amt'], why=l['why'], rule=l.get('rule'), group=l.get('group'), freq=l.get('freq'), each=l.get('each'), no=l.get('no'),
                                                 in_row=None, counted=(counts(l, c['mode']) > 0) if c['kind'] == 'engine' else True) for l in L],
                              issues=iss)
        toks += [(c['id'], x) for x in t]
    clear_cache()
    cmp = None
    if html and os.path.exists(html):
        h = open(html, encoding='utf-8').read()
        got = [a or b or c_ for a, b, c_ in TOKEN_RE.findall(h)]
        mine = [x for _, x in toks]
        cmp = dict(html_n=len(got), spec_n=len(mine), equal=(got == mine),
                   diffs=[dict(i=i, cell=toks[i][0] if i < len(toks) else None, spec=mine[i] if i < len(mine) else None, html=got[i] if i < len(got) else None)
                          for i in range(max(len(got), len(mine))) if (mine[i] if i < len(mine) else None) != (got[i] if i < len(got) else None)])
    return dict(pdf=os.path.basename(pdf), meta={k: meta.get(k) for k in ('product', 'premium', 'sex')}, nriders=len(riders),
                riders=[dict(no=r.get('no'), name=r['name'], man=r['man'], matched=r.get('matched'), via=r.get('via'), itc=r.get('itc'), cat=r.get('cat'),
                             ncodes=len(r.get('codes') or []), nexcl=len(r.get('excl') or []), nhc=len(r.get('hc') or [])) for r in riders],
                cells=cells, cmp=cmp)

def spec_dump():
    return [dict(c) for c in CELLS]

if __name__ == '__main__':
    out = sys.argv[1]
    uni = universe()
    uni = add_design_only(uni, [pipeline.read_riders(p) for p in sys.argv[2:]])
    res = dict(version=S.RULEDOC.get('_note', ''), cells=spec_dump(), universe_n=len(uni), universe=run_universe(uni),
               universe_riders=[dict(db_id=r['db_id'], name=r['name'], product=r.get('product'), man=r['man'], cat=r.get('cat'), ncodes=len(r['codes']), nexcl=len(r['excl']), nhc=len(r['hc']),
                                     benefit=r.get('benefit'), sub=r.get('sub'), itc=r.get('itc'), via=r.get('via'), matched=r.get('matched')) for r in uni], designs=[])
    for pdf in sys.argv[2:]:
        d = run_design(pdf, None)
        print(os.path.basename(pdf), 'riders', d['nriders'])
        res['designs'].append(d)
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, default=str)
    print('cells', len(CELLS), 'engine cells', sum(1 for c in CELLS if c['kind'] == 'engine'), '->', out)
