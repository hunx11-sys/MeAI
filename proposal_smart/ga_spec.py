# -*- coding: utf-8 -*-
"""GA 제안서(ga2.py) 5쪽의 모든 칸을 **데이터**로 옮긴 사양 + 엔진 대조 도구.

  python3 ga_spec.py <out.json> [설계서.pdf ...]

· CELLS : ga2.py 가 그리는 순서 그대로의 칸 목록. 칸마다 사례(kcd·tags·itc_events)·집계 방식·표시 필터를 적는다.
· run_universe() : 특약 마스터(db.json 1,758건) 전부를 각 칸 사례에 태워 어느 특약이 잡히는지, 왜 빠지는지(로그)를 뽑는다.
· run_design()   : 설계서 1건의 담보로 칸 값을 계산하고, 배포한 GA HTML 의 숫자 순서와 대조한다.
숫자를 만들거나 추정하지 않는다 — 전부 scen_engine.pay_lines 결과를 그대로 적는다.
"""
import sys, os, json, re, copy, collections
PS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PS)
import scen_engine as S, engine as itc, matcher, pipeline
import build_all as BA

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

# ── ga2.py GA_DZ 그대로 ──
GA_DZ = {
 '백내장': ('인공수정체 삽입', 'H25.9', dict(surg='71', surg7='C061', grp=['백내장']), [['수술', '수정체 유화술', '', ['surg'], {'j': 1}]]),
 '디스크': ('신경성형술', 'M51', dict(surg='88-2', surg7='B182', grp=['다빈도62대질병']), [['수술', '신경성형술', '', ['surg'], {'j': 2}]]),
 '치질': ('치핵절제술', 'K64', dict(surg='44', surg7='G272', grp=['치핵']), [['수술', '치핵절제술', '', ['surg'], {'j': 1}]]),
 '담석증': ('복강경수술', 'K80.0', dict(surg='36', surg7='H107', grp=['다빈도62대질병'], anes=1), [['진단', '복부 CT', '', ['x_ct']], ['수술', '복강경 담낭 절제', '', ['surg'], {'j': 2}]]),
 '충수염': ('충수절제술', 'K35', dict(surg='41', surg7='G212', grp=[], anes=1), [['수술', '충수 절제', '', ['surg'], {'j': 2}]]),
 '갑상선 결절': ('고주파절제술', 'D34', dict(surg='88-2', surg7='K080', hc=['PZ612'], grp=['다빈도62대질병']), [['수술', '고주파절제술', '', ['surg'], {'j': 2}]]),
 '유방양성종양': ('맘모톰', 'D24', dict(surg='4', surg7='J071', grp=['유방의장애']), [['수술', '맘모톰', '', ['surg'], {'j': 1}]]),
 '자궁근종': ('하이푸', 'D25.9', dict(surg='53', hc=['RZ566'], grp=['다빈도62대질병']), [['수술', '고강도초음파집속술', '', ['surg'], {'j': 1}]]),
 '전립선절제술': ('복강경수술', 'N40', dict(surg='50', surg7='M022', grp=['관절염,생식기질환'], anes=1), [['수술', '복강경 전립선절제', '', ['surg'], {'j': 2}]]),
 '골절진단': ('골절수술', 'S52.5', dict(cause='상해', surg='13-2', surg7='I286', grp=[]), [['수술', '골절 고정술', '', ['surg'], {'j': 2}]]),
}
def sc_dz(name, hosp):
    proc, kcd, tg, ev = GA_DZ[name]
    return sc(kcd, ev, **dict(tg, hosp=hosp))

# ── 암 사례 (mk2.C 그대로) ──
CS = {
 'robot':  sc('C16', [['수술', '로봇수술', '', ['surg', 'robot'], {'nc': 1}]], surg='C1', surg7='G081'),
 'lap':    sc('C16', [['수술', '복강경', '', ['surg']]], surg='C1', surg7='G081'),
 'open':   sc('C16', [['수술', '개복', '', ['surg']]], surg='C1', surg7='G082'),
 'endo':   sc('C16', [['수술', '내시경 절제', '', ['surg']]], surg='C2', surg7='G503'),
 'chemo':  sc('C16', [['항암', '항암약물(급여)', '', ['chemo']]], chemo=1),
 'target': sc('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=2),
 'immune': sc('C16', [['항암', '면역(비급여)', '', ['chemo', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=2),
 'cart':   sc('C16', [['항암', '카티(비급여)', '', ['chemo', 'target', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=1),
 # 1쪽 전용 : 표적·면역 약물 1종(치료 1개) — (2종및3종이상) 담보 제외 (GA 요청 2026-10)
 'target1': sc('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=1),
 'immune1': sc('C16', [['항암', '면역(비급여)', '', ['chemo', 'immune'], {'nc': 1}]], chemo=1, target=1, drug=1),
 'rad':    sc('C16', [['방사선', '항암방사선(급여)', '', ['rad']]]),
 'imrt':   sc('C16', [['방사선', '세기조절', '', ['rad', 'imrt']]]),
 'proton': sc('C16', [['방사선', '양성자(비급여)', '', ['rad', 'proton'], {'nc': 1}]]),
 'carbon': sc('C16', [['방사선', '중입자(비급여)', '', ['rad', 'carbon'], {'nc': 1}]]),
}
def sc_tg(d):   # ga2.p4 tg(d) / p2 t3
    return sc('C16', [['항암', '표적(비급여)', '', ['chemo', 'target'], {'nc': 1}]], chemo=1, target=1, drug=d)
DXS = {'일반암': sc_dx('C16', 'cancer'), '소액암': sc_dx('C50', 'cancer'), '고액암': sc_dx('C25', 'cancer'), '유사암': sc_dx('C73', 'sim_cancer')}
BDX = {'뇌경색': sc_dx('I63', 'brain', BG), '뇌출혈': sc_dx('I61', 'brain', BG)}
HDX = {'허혈성': sc_dx('I20', 'heart', HG + ['허혈성심장질환']), '급성심근경색': sc_dx('I21', 'heart', HG + ['허혈성심장질환'])}
def brain_steps(hosp):    # ga2.p3 Ls('brain') · mk2.vsurg b 목록과 같다
    return [('혈전용해치료', sc('I63', [['시술', '혈전용해', '', ['thromb']]], series='brain', hosp=hosp)),
            ('혈전용해+혈전제거술', sc('I63', [['시술', '혈전용해', '', ['thromb']], ['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], hosp=hosp, acts=['thrombectomy'])),
            ('스텐트·코일색전술', sc('I67.1', [['시술', '코일 색전술', '', ['surg']]], surg='88-1', surg7='B016', grp=BG + ['특정31대질병'], hosp=hosp, anes=1)),
            ('개두 수술', sc('I61', [['수술', '혈종제거 개두술', '', ['surg']]], surg='59', surg7='B031', grp=BG + ['뇌졸중', '뇌출혈', '특정31대질병'], hosp=hosp, anes=1))]
def heart_steps(hosp):    # ga2.p3 Ls('heart')
    return [('혈전용해치료', sc('I21', [['시술', '혈전용해', '', ['thromb']]], series='heart', hosp=hosp)),
            ('혈전용해+혈전제거술', sc('I21', [['시술', '혈전용해', '', ['thromb']], ['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='F121', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp, acts=['thrombectomy'])),
            ('관상동맥스텐트', sc('I20', [['시술', '스텐트 삽입', '', ['surg']]], surg='88-1', surg7='F133', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp)),
            ('개흉 수술', sc('I20', [['수술', '관상동맥 우회술', '', ['surg']]], surg='24', surg7='F042', grp=HG + ['허혈성심장질환', '특정31대질병'], hosp=hosp, anes=1, anes_h=6))]
# p1 '치료 및 수술' — mk2.vsurg('상급종합') : b2[0] 혈전용해 · b2[1] 혈전제거 · b2[2] 코일색전술 · h2[1] 스텐트
_b, _h = brain_steps('상급종합'), heart_steps('상급종합')
P1_TX = [('혈전용해', _b[0][1]), ('혈전제거', _b[1][1]), ('코일색전술', _b[2][1]), ('스텐트수술', _h[2][1])]

# ═══════════════ 칸 목록 (렌더 순서) ═══════════════
CELLS = []
def add(page, section, row, col, kind, sc_=None, mode='first', filt=None, filt_kcd=None, direct=None, note='', label=None, sc_name='', part=1):
    CELLS.append(dict(id='P%d-%03d' % (page, len([c for c in CELLS if c['page'] == page]) + 1), page=page, section=section, row=row, col=col,
                      label=label or ('%s · %s' % (row, col) if row else col), kind=kind, sc=sc_, sc_name=sc_name, mode=mode,
                      filt=filt, filt_kcd=filt_kcd, direct=direct, note=note, part=part))

# ── 1쪽 ──
_kv1 = [('진단금', [('일반암', DXS['일반암'], '일반암 진단(C16 위암)'), ('소액암', DXS['소액암'], '소액암 진단(C50 유방암)'), ('고액암', DXS['고액암'], '고액암 진단(C25 췌장암)'), ('유사암', DXS['유사암'], '유사암 진단(C73 갑상선암)')]),
        ('수술', [('다빈치로봇', CS['robot'], '위암 다빈치로봇수술(비급여)'), ('내시경', CS['endo'], '위암 내시경 절제'), ('복강경,흉강경', CS['lap'], '위암 복강경수술'), ('개복,개흉', CS['open'], '위암 개복수술')]),
        ('항암약물', [('화학항암', CS['chemo'], '위암 항암약물(급여)'), ('표적항암', CS['target1'], '위암 표적항암(비급여, 약물 1종)'), ('면역항암', CS['immune1'], '위암 면역항암(비급여, 약물 1종)'), ('카티항암', CS['cart'], '위암 카티(CAR-T) 항암(비급여, 약물 1종)')]),
        ('항암방사선', [('항암방사선', CS['rad'], '위암 항암방사선(급여)'), ('세기조절', CS['imrt'], '위암 세기조절방사선'), ('양성자', CS['proton'], '위암 양성자(비급여)'), ('중입자', CS['carbon'], '위암 중입자(비급여)')])]
for i in range(4):
    for h, items in _kv1:
        n, s_, nm = items[i]
        add(1, '암보장', h, n, 'engine', s_, 'first', sc_name=nm)
_sev1 = [('중환자실치료', 'icu'), ('부분에크모', 'ecmo'), ('지속적신대체요법', 'crrt'), ('인공호흡기', 'vent'), ('저체온요법', 'hypo')]
_kv2 = [('진단금', [('뇌출혈', BDX['뇌출혈'], '뇌출혈 진단(I61)'), ('뇌경색', BDX['뇌경색'], '뇌경색 진단(I63)'), ('급성심근', HDX['급성심근경색'], '급성심근경색 진단(I21)'), ('허혈성', HDX['허혈성'], '허혈성심장질환 진단(I20 협심증)')]),
        ('치료 및 수술', [(n, s_, n + '(상급종합병원)') for n, s_ in P1_TX]),
        ('중증치료', [(n, sc_itc('I63', k, grp=BG), '뇌경색(I63) %s · 상급종합병원 · 통합치료비 항목만' % n) for n, k in _sev1]),
        ('산정특례', [('뇌경색', None, ''), ('뇌동맥류', None, ''), ('협심증', None, ''), ('부정맥', None, '')])]
for i in range(5):
    for h, items in _kv2:
        if i >= len(items): continue
        n, s_, nm = items[i]
        if h == '산정특례': add(1, '뇌·심보장', h, n, 'fixed', note='ga2.py 가 0 으로 고정해 둔 칸 — 산정특례 등록 진단비는 계산하지 않고 항상 0 표시')
        elif h == '중증치료': add(1, '뇌·심보장', h, n, 'engine', s_, 'itc_only', sc_name=nm)
        else: add(1, '뇌·심보장', h, n, 'engine', s_, 'first', sc_name=nm)
DZ_ORDER = ['백내장', '디스크', '치질', '담석증', '충수염', '갑상선 결절', '유방양성종양', '자궁근종', '전립선절제술', '골절진단']
for n in DZ_ORDER:
    add(1, '국내주요수술', n, GA_DZ[n][0], 'engine', sc_dz(n, '병원'), 'first', sc_name='%s %s (%s) · 병원급' % (n, GA_DZ[n][0], GA_DZ[n][1]))
add(1, '간병인입원보장', '간병인지원', '간병인 지원', 'text', direct=dict(any=['간병인지원']), note="가입담보 중 '간병인지원'이 들어간 담보(가입금액>0)가 하나라도 있으면 '지원가능', 없으면 '미가입'")
add(1, '간병인입원보장', '간병인지원', '간병인 미사용', 'direct', direct=dict(keys=['간병인지원', '질병입원일당(Ⅵ)'], exclude=['181일']), note='담보명에 두 말이 모두 들어간 담보의 가입금액(일당) 합 · 181일 담보 제외')
add(1, '간병인입원보장', '간병인지원', '요양병원', 'text', direct=dict(any=['간병인지원']), note="간병인 지원 칸과 같은 판정('간병인지원' 담보 가입 시 지원가능)")
add(1, '간병인입원보장', '간병인지원', '간호간병', 'care2', direct=dict(keys=['간병인지원', '질병입원일당(간호·간병']), note='1~180일 담보 가입금액 · 181일 담보 가입금액을 나란히 표시')
add(1, '간병인입원보장', '간병인사용', '간병인', 'care_use', direct=dict(use='gen'), note="담보명에 '간병인사용'·'질병입원일당'이 들어간 담보(요양병원 전용 '(요양병원)' 담보·간호·간병 담보 제외)의 가입금액 — 1~180일 · 181일~ 두 줄(v8.65 : 전에는 '(요양병원제외)'의 '요양'에 걸려 미가입)")
add(1, '간병인입원보장', '간병인사용', '요양병원', 'care_use', direct=dict(use='nh'), note="'간병인사용 …질병입원일당(…)(요양병원)' 담보의 가입금액(v8.65 : 전에는 가입만 되어 있으면 '지원가능' 문구)")
add(1, '간병인입원보장', '간병인사용', '간호간병', 'care_use', direct=dict(use='nurse'), note="단독 특약 '간호·간병통합서비스 사용 질병입원일당'(간병인지원형 제외)의 가입금액 — 1~180일 · 181일~(v8.65)")

# ── 2쪽 ──
_ex2 = [('암 내시경검사', 'x_endo'), ('MRI 촬영검사', 'x_mri'), ('PET검사', 'x_pet'), ('특정단일 유전자검사', 'x_gene'), ('초음파검사', 'x_us'), ('CT 촬영검사', 'x_ct'), ('특정생검 조직검사', 'x_bio'), ('특정NGS 유전자검사', 'x_ngs')]
for n, k in _ex2:
    add(2, '암검사(8종)', '', n, 'engine', sc_itc('C16', k, fam='cancer'), 'itc_only', sc_name='위암(C16) %s · 상급종합병원 · 통합치료비 항목만' % n)
add(2, '암진단', '', '일반암', 'engine', DXS['일반암'], 'first', sc_name='일반암 진단(C16)')
add(2, '암진단', '', '유사암', 'engine', DXS['유사암'], 'first', sc_name='유사암 진단(C73)')
_sg = [('내시경수술', 'endo'), ('개복·개흉수술', 'open'), ('복강경,흉강경', 'lap'), ('다빈치로봇암수술', 'robot')]
for rl, md in (('최초 지급시', 'first'), ('반복(연 1회)', 'year'), ('수술할 때마다', 'each')):
    for n, k in _sg: add(2, '암수술', rl, n, 'engine', CS[k], md, sc_name='위암 %s' % n)
add(2, '항암약물', '최초 지급시', '화학항암치료', 'engine', CS['chemo'], 'first', sc_name='위암 항암약물(급여)')
add(2, '항암약물', '최초 지급시', '표적항암치료', 'engine', CS['target'], 'first', sc_name='위암 표적항암(비급여, 약물 2종)')
add(2, '항암약물', '최초 지급시', '면역항암치료(카티포함)', 'engine', CS['immune'], 'first', sc_name='위암 면역항암(비급여, 약물 2종)')
add(2, '항암약물', '최초 지급시', '갯수별 약물치료 2가지', 'engine', CS['target'], 'first', sc_name='위암 표적항암(비급여) · 연간 약물 2종', note='표적항암치료 칸과 같은 사례(약물 2종)')
add(2, '항암약물', '반복(연 1회)', '화학항암치료', 'engine', CS['chemo'], 'year', sc_name='위암 항암약물(급여)')
add(2, '항암약물', '반복(연 1회)', '표적항암치료', 'engine', CS['target'], 'year', sc_name='위암 표적항암(비급여, 약물 2종)')
add(2, '항암약물', '반복(연 1회)', '면역항암치료(카티포함)', 'engine', CS['immune'], 'year', sc_name='위암 면역항암(비급여, 약물 2종)')
add(2, '항암약물', '반복(연 1회)', '갯수별 약물치료 3가지', 'engine', sc_tg(3), 'first', sc_name='위암 표적항암(비급여) · 연간 약물 3종', note="행 이름은 '반복(연 1회)'이지만 실제로는 약물 3종 사례의 **최초** 합계를 넣는다(ga2.py p2)")
_rd = [('항암방사선', 'rad'), ('세기조절 방사선', 'imrt'), ('양성자 방사선', 'proton'), ('중입자 방사선', 'carbon')]
for rl, md in (('최초 지급시', 'first'), ('반복(연 1회)', 'year')):
    for n, k in _rd: add(2, '항암방사선', rl, n, 'engine', CS[k], md, sc_name='위암 %s' % n)
add(2, '재활치료', '연 20회', '입원 암재활치료', 'engine', sc_itc('C16', 'rehab', fam='cancer', extra={'n': 20}), 'itc_only', sc_name='위암 재활치료 20일 · 상급종합 · 통합치료비 항목만')
add(2, '재활치료', '연 20회', '외래 암재활치료', 'engine', sc_itc('C16', 'rehab', fam='cancer', extra={'n': 20}), 'itc_only', sc_name='(입원 칸과 같은 값)', note='입원·외래 구분 없이 같은 사례 값을 두 칸에 넣는다')
add(2, '암후유장해', '', '3-100% 암후유장해', 'direct', direct=dict(keys=['암', '후유장해'], exclude=[]), note="담보명에 '암'과 '후유장해'가 모두 들어간 담보의 가입금액 합 — 계산 아님")

# ── 3쪽 ──
for n, k in (('MRI 촬영검사', 'x_mri'), ('PET검사', 'x_pet'), ('CT 촬영검사', 'x_ct')):
    add(3, '검사(3종)', '', n, 'engine', sc_itc('I63', k, grp=BG), 'itc_only', sc_name='뇌경색(I63) %s · 상급종합 · 통합치료비 항목만' % n)
add(3, '뇌질환 진단·치료', '진단', '뇌혈관', 'engine', BDX['뇌경색'], 'first', sc_name='뇌경색 진단(I63)')
add(3, '뇌질환 진단·치료', '진단', '뇌출혈', 'engine', BDX['뇌출혈'], 'first', sc_name='뇌출혈 진단(I61)')
for rl, hosp, md in (('모든 병원', '병원', 'first'), ('상급종합병원', '상급종합', 'first'), ('수술할 때마다', '상급종합', 'each')):
    for n, s_ in brain_steps(hosp): add(3, '뇌질환 진단·치료', rl, n, 'engine', s_, md, sc_name='%s · %s' % (n, hosp))
add(3, '심질환 진단·치료', '진단', '허혈성', 'engine', HDX['허혈성'], 'first', sc_name='허혈성심장질환 진단(I20)')
add(3, '심질환 진단·치료', '진단', '급성심근경색', 'engine', HDX['급성심근경색'], 'first', sc_name='급성심근경색 진단(I21)')
for rl, hosp, md in (('모든 병원', '병원', 'first'), ('상급종합병원', '상급종합', 'first'), ('수술할 때마다', '상급종합', 'each')):
    for n, s_ in heart_steps(hosp): add(3, '심질환 진단·치료', rl, n, 'engine', s_, md, sc_name='%s · %s' % (n, hosp))
_sk = [('중환자실 치료', 'icu'), ('부분에크모치료', 'ecmo'), ('지속적신대체요법', 'crrt'), ('인공호흡기치료', 'vent'), ('저체온요법치료', 'hypo')]
for rl, hosp in (('모든 병원', '병원'), ('상급종합병원', '상급종합')):
    for n, k in _sk: add(3, '뇌심 중증치료', rl, n, 'engine', sc_itc('I63', k, hosp=hosp, grp=BG), 'itc_only', sc_name='뇌경색(I63) %s · %s · 통합치료비 항목만' % (n, hosp))
add(3, '재활치료', '연 15회', '입원 재활치료', 'engine', sc_itc('I63', 'rehab', grp=BG, extra={'n': 15}), 'itc_only', sc_name='뇌경색 재활 15일 · 상급종합 · 통합치료비 항목만')
add(3, '재활치료', '연 15회', '외래 재활치료', 'engine', sc_itc('I63', 'rehab', grp=BG, extra={'n': 15}), 'itc_only', sc_name='(입원 칸과 같은 값)')

# ── 4쪽 ──
R, O = CS['robot'], CS['open']
_p4a = [('질병수술비', (['질병수술비'], ['131대', '130대', '척추질병'])), ('1-5종수술비', (['1-5종'], ['상해'])), ('암수술비', (['암수술비'], ['다빈치'])),
        ('암통합치료비', (['암 통합치료비(기본형)', '암 통합치료비(실속형)'], [])), ('비급여암통합치료비', (['통합치료비Ⅱ(비급여', '통합치료비(주요치료)(비급여'], [])), ('다빈치로봇암수술비', (['다빈치'], []))]
for n, f in _p4a: add(4, '다빈치로봇암수술', '담보', n, 'engine', R, 'row', filt=f, sc_name='위암 다빈치로봇수술(비급여)')
add(4, '다빈치로봇암수술', '총 보장', '최초', 'engine', R, 'first', filt=('ANY', [f for _, f in _p4a]), sc_name='위암 다빈치로봇수술(비급여)')
add(4, '다빈치로봇암수술', '총 보장', '매 회', 'engine', R, 'each', filt=('ANY', [f for _, f in _p4a]), sc_name='위암 다빈치로봇수술(비급여)')
_p4b = [('질병수술비', (['질병수술비'], ['131대', '130대', '척추질병'])), ('1-5종수술비', (['1-5종'], ['상해'])), ('1-7종수술비', (['┗ 수술비', '수술비(1-7종'], ['상해'])), ('암수술비', (['암수술비'], ['다빈치'])),
        ('암통합치료비', (['암 통합치료비(기본형)', '암 통합치료비(실속형)'], [])), ('비급여암통합치료비', (['통합치료비Ⅱ(비급여', '통합치료비(주요치료)(비급여'], []))]
for n, f in _p4b: add(4, '개복수술', '담보', n, 'engine', O, 'row', filt=f, sc_name='위암 개복수술')
add(4, '개복수술', '총 보장', '최초', 'engine', O, 'first', filt=('ANY', [f for _, f in _p4b]), sc_name='위암 개복수술')
add(4, '개복수술', '총 보장', '매 회', 'engine', O, 'each', filt=('ANY', [f for _, f in _p4b]), sc_name='위암 개복수술')
T1, T2, T3 = sc_tg(1), sc_tg(2), sc_tg(3)
# 총 보장 = 표에 있는 담보행만 합산(v8.65 · 보수적) — ga_proposal.P4_TARGET 과 같은 행 필터
_P4C = [(['항암방사선약물치료비'], ['26종', '기타피부암']), (['26종'], []), (['암 통합치료비(기본형)', '암 통합치료비(실속형)'], []), (['통합치료비Ⅱ(비급여', '통합치료비(주요치료)(비급여'], []),
        (['암진단및치료비Ⅱ[표적', '암치료,후유장해및진단비[표적'], []), (['표적항암약물허가치료비'], ['연간 약물종류', '암진단및치료비', '후유장해및진단비']), (['연간 약물종류'], [])]
add(4, '표적항암치료비', '담보', '항암방사선약물치료비', 'engine', T2, 'row', filt=(['항암방사선약물치료비'], ['26종', '기타피부암']), sc_name='위암 표적항암(비급여) 약물 2종')
add(4, '표적항암치료비', '담보', '26종항암방사선약물', 'engine', T2, 'row', filt=(['26종'], []), sc_name='위암 표적항암(비급여) 약물 2종')
add(4, '표적항암치료비', '담보', '암통합치료비', 'engine', T2, 'row', filt=(['암 통합치료비(기본형)', '암 통합치료비(실속형)'], []), sc_name='위암 표적항암(비급여) 약물 2종')
add(4, '표적항암치료비', '담보', '비급여암통합치료비', 'engine', T2, 'row', filt=(['통합치료비Ⅱ(비급여', '통합치료비(주요치료)(비급여'], []), sc_name='위암 표적항암(비급여) 약물 2종')
add(4, '표적항암치료비', '담보', '암진단비 및 치료비(치료비) 2가지', 'engine', T2, 'row', filt=(['암진단및치료비Ⅱ[표적', '암치료,후유장해및진단비[표적'], []), sc_name='위암 표적항암(비급여) 약물 2종')
add(4, '표적항암치료비', '담보', '암진단비 및 치료비(치료비) 3가지', 'engine', T3, 'row', filt=(['암진단및치료비Ⅱ[표적', '암치료,후유장해및진단비[표적'], []), sc_name='위암 표적항암(비급여) 약물 3종', part=2)
add(4, '표적항암치료비', '담보', '표적항암약물치료비', 'engine', T2, 'row', filt=(['표적항암약물허가치료비'], ['연간 약물종류', '암진단및치료비', '후유장해및진단비']), sc_name='위암 표적항암(비급여) 약물 2종')
add(4, '표적항암치료비', '담보', '표적항암약물치료비(연간약물종류) 1가지', 'engine', T1, 'row', filt=(['연간 약물종류'], []), sc_name='위암 표적항암(비급여) 약물 1종')
add(4, '표적항암치료비', '담보', '표적항암약물치료비(연간약물종류) 2가지', 'engine', T2, 'row', filt=(['연간 약물종류'], []), sc_name='위암 표적항암(비급여) 약물 2종', part=2)
add(4, '표적항암치료비', '담보', '표적항암약물치료비(연간약물종류) 3가지', 'engine', T3, 'row', filt=(['연간 약물종류'], []), sc_name='위암 표적항암(비급여) 약물 3종', part=3)
add(4, '표적항암치료비', '총 보장', '최초(약물 1가지)', 'engine', T1, 'first', filt=('ANY', _P4C), sc_name='위암 표적항암(비급여) 약물 1종')
add(4, '표적항암치료비', '총 보장', '2가지', 'engine', T2, 'first', filt=('ANY', _P4C), sc_name='위암 표적항암(비급여) 약물 2종')
add(4, '표적항암치료비', '총 보장', '3가지', 'engine', T3, 'first', filt=('ANY', _P4C), sc_name='위암 표적항암(비급여) 약물 3종')

# ── 5쪽 (뇌·심장 치료 세부내역 · ga2.p_bh 와 같은 사례·줄 구분) ──
BH_ROWS = {
 'thromb': ('혈전용해치료비', r'혈전용해치료비'),
 'mech':   ('혈전제거·특정혈전치료비', r'기계적혈전제거|특정혈전치료비'),
 'two':    ('2대질환 치료비(주요치료비·최대두배)', r'2대질환.*주요치료비|최대두배받는2대질환치료비'),
 'bhsurg': ('뇌·심장 수술비(뇌혈관·허혈성심장·131대·5대질환 등)', r'뇌혈관질환수술비|허혈성심장질환수술비|심장질환수술비|뇌출혈수술비|뇌졸중수술비|뇌동맥류|5대질환|32대질병|13[01]대질병수술비'),
 'dzsurg': ('질병수술비', r'^(\(\d+년갱신\))?(갱신형)?(상급종합병원|종합병원)?질병수술비'),
 'g15':    ('1-5종수술비', r'1-5종'),
 'g17':    ('1-7종수술비', r'1-7종|┗수술비'),
 'itc':    ('특정순환계질환 통합치료비', None),
 'etc':    ('산정특례·생활지원비·전신마취 등', None),
}
def bh_group(name, grp=None):
    n = re.sub(r'\s+', '', name or '')
    for k in ('thromb', 'mech', 'two', 'bhsurg', 'dzsurg', 'g15', 'g17'):
        if re.search(BH_ROWS[k][1], n) and not (k == 'thromb' and re.search(BH_ROWS['mech'][1], n)): return k
    if grp == '통합치료비': return 'itc'
    return 'etc'
BH_CASES = {
 1: ('혈전용해치료', [('뇌경색 혈전용해', sc('I63', [['시술', '혈전용해', '', ['thromb']]], series='brain')),
                   ('급성심근경색 혈전용해', sc('I21', [['시술', '혈전용해', '', ['thromb']]], series='heart'))], ['thromb', 'two', 'itc'], ('first', 'year')),
 2: ('수술(비관혈)', [('뇌경색 기계적 혈전제거술', sc('I63', [['시술', '혈전제거술', '', ['surg']]], surg='88-1', surg7='B027', grp=BG + ['뇌졸중', '특정31대질병'], acts=['thrombectomy'])),
                   ('급성심근경색 관상동맥 스텐트', sc('I21', [['시술', '스텐트 삽입', '', ['surg']]], surg='88-1', surg7='F133', grp=HG + ['허혈성심장질환', '특정31대질병']))],
     ['bhsurg', 'dzsurg', 'g15', 'g17', 'two', 'itc'], ('first', 'each')),
 3: ('수술(관혈)', [('뇌출혈 개두술', sc('I61', [['수술', '혈종제거 개두술', '', ['surg']]], surg='59', surg7='B031', grp=BG + ['뇌졸중', '뇌출혈', '특정31대질병'], anes=1)),
                 ('협심증 관상동맥 우회술', sc('I20', [['수술', '관상동맥 우회술', '', ['surg']]], surg='24', surg7='F042', grp=HG + ['허혈성심장질환', '특정31대질병'], anes=1, anes_h=6))],
     ['bhsurg', 'dzsurg', 'g15', 'g17', 'two', 'itc'], ('first', 'each')),
}
_TOT = {'first': '최초', 'year': '다음 해(반복)', 'each': '매 회'}
for no, (title, cases, keys, tots) in BH_CASES.items():
    for k in keys:
        for side, (nm_, s_) in zip(('뇌', '심장'), cases):
            add(5, title, BH_ROWS[k][0], side, 'engine', s_, 'row', filt=('BH', k), sc_name='%s · 상급종합병원' % nm_)
    for md in tots:
        for side, (nm_, s_) in zip(('뇌', '심장'), cases):
            add(5, title, '총 보장 ' + _TOT[md], side, 'engine', s_, md, filt=('BHS', keys), sc_name='%s · 상급종합병원' % nm_)
BH_SEV = [('중환자실 치료', 'icu'), ('부분에크모(ECMO)', 'ecmo'), ('지속적신대체요법(CRRT)', 'crrt'), ('인공호흡기(12시간 초과)', 'vent'), ('저체온요법', 'hypo')]
def bh_sev(kcd, grp, keys):
    return sc(kcd, [['치료', k, '', [k]] for k in keys], grp=grp, icu=(1 if 'icu' in keys else 0))
for lab, k in BH_SEV:
    add(5, '중환자실·에크모 등 중증치료', lab, '뇌', 'engine', bh_sev('I63', BG, [k]), 'first', sc_name='뇌경색 %s · 상급종합병원' % lab)
    add(5, '중환자실·에크모 등 중증치료', lab, '심장', 'engine', bh_sev('I21', HG, [k]), 'first', sc_name='급성심근경색 %s · 상급종합병원' % lab)
_all = [k for _, k in BH_SEV]
add(5, '중환자실·에크모 등 중증치료', '총 보장 모두 받을 때', '뇌', 'engine', bh_sev('I63', BG, _all), 'first', sc_name='뇌경색 중증치료 5항목 모두 · 상급종합병원(통합치료비 연간 한도 적용)')
add(5, '중환자실·에크모 등 중증치료', '총 보장 모두 받을 때', '심장', 'engine', bh_sev('I21', HG, _all), 'first', sc_name='급성심근경색 중증치료 5항목 모두 · 상급종합병원(통합치료비 연간 한도 적용)')

# ── 6쪽 (주요 수술비 세부내역) ──
KEY5 = {'질병수술비': (['질병수술비'], ['특정5대질병 제외', '131대', '130대', '척추질병']), '질병수술비(특정5대제외)': (['특정5대질병 제외'], []), '1-5종수술비': (['1-5종'], ['상해']),
        '1-7종수술비': (['┗ 수술비', '수술비(1-7종'], ['상해']), '131대수술비': (['131대', '130대'], [])}
for n, tpl in (('백내장', ['질병수술비', '1-5종수술비', '1-7종수술비', '131대수술비']),
               ('디스크', ['질병수술비', '질병수술비(특정5대제외)', '1-5종수술비', '1-7종수술비', '131대수술비']),
               ('치질', ['질병수술비', '1-5종수술비', '1-7종수술비', '131대수술비']),
               ('담석증', ['질병수술비', '질병수술비(특정5대제외)', '1-5종수술비', '1-7종수술비', '131대수술비'])):
    kcd = GA_DZ[n][1]
    for t in tpl: add(6, n, '담보', t, 'engine', sc_dz(n, '상급종합'), 'row', filt=KEY5[t], filt_kcd=kcd, sc_name='%s %s · 상급종합' % (n, GA_DZ[n][0]))
    add(6, n, '총 보장', '모든병원', 'engine', sc_dz(n, '병원'), 'first', sc_name='%s %s · 병원급' % (n, GA_DZ[n][0]))
    add(6, n, '총 보장', '상급병원', 'engine', sc_dz(n, '상급종합'), 'first', sc_name='%s %s · 상급종합' % (n, GA_DZ[n][0]))

# ═══════════════ 계산 ═══════════════
def won(v):
    if v == 0: return '0'
    eok, man = divmod(int(v), 10000)
    if eok and man: return '%d억 %s' % (eok, format(man, ','))
    if eok: return '%d억' % eok
    return format(man, ',')

def pay(riders, s_):
    S.ISSUES.clear()
    L = S.pay_lines(riders, copy.deepcopy(s_))
    return L, list(S.ISSUES)

def _ns(x): return re.sub(r'\s+', '', x or '')
def in_filt(name, filt, grp=None):
    if filt and filt[0] == 'BH': return bh_group(name, grp) == filt[1]
    if filt and filt[0] == 'BHS': return bh_group(name, grp) in filt[1]            # 뇌·심장 총 보장 — 표에 있는 줄만(v8.65)
    if filt and filt[0] == 'ANY': return any(in_filt(name, f, grp) for f in filt[1])   # 암치료 총 보장 — 표의 담보행 중 하나(v8.65)
    keys, ex = filt
    n = _ns(name)
    return any(_ns(k) in n for k in keys) and not any(_ns(x) in n for x in ex)

def counts(l, mode):
    """이 지급 줄이 칸의 집계 방식(mode)에 들어가는 금액"""
    if mode in ('first', 'row'): return l['amt']
    if mode == 'year': return l['amt'] if l.get('freq') != 'once' else 0
    if mode == 'each': return l.get('each', l['amt'] if l.get('freq') == 'each' else 0)
    if mode == 'itc_only': return l['amt'] if l.get('group') == '통합치료비' else 0
    return 0

def cell_tokens(c, riders):
    """ga2.py 가 그 칸에 찍는 표시(숫자 문자열 또는 미가입/면책/지원가능) 목록과 지급 줄"""
    k = c['kind']
    if k == 'fixed': return ['0'], [], []
    if k == 'text':
        ok = any(all(a in r['name'] for a in c['direct']['any']) and r['man'] > 0 for r in riders)
        return ['지원가능' if ok else '미가입'], [], []
    if k == 'direct':
        d = c['direct']
        rs = [r for r in riders if all(a in r['name'] for a in d['keys']) and not any(x in r['name'] for x in d.get('exclude', []))]
        return (['미가입'] if not rs else [won(sum(r['man'] for r in rs))]), [dict(name=r['name'], amt=r['man'], why='가입금액 그대로', rule='direct') for r in rs], []
    if k == 'care_use':                                   # ga_proposal.p1 care_use 와 같은 판정(v8.65)
        u = c['direct']['use']
        rs = [r for r in riders if '질병입원일당' in r['name'] and '요양성' not in r['name']]
        if u == 'gen': rs = [r for r in rs if '간병인사용' in r['name'] and '(요양병원)' not in r['name'] and '간호·간병' not in r['name']]
        elif u == 'nh': rs = [r for r in rs if '간병인사용' in r['name'] and '(요양병원)' in r['name']]
        else: rs = [r for r in rs if '간호·간병통합서비스' in r['name'] and '간병인지원' not in r['name']]
        if not rs: return ['미가입'], [], []
        a = [r for r in rs if '181일' not in r['name']]; b = [r for r in rs if '181일' in r['name']]
        toks = [won(sum(r['man'] for r in a)), won(sum(r['man'] for r in b))] if b else [won(sum(r['man'] for r in a))]
        return toks, [dict(name=r['name'], amt=r['man'], why='가입금액 그대로', rule='direct') for r in a + b], []
    if k == 'care2':
        d = c['direct']
        a = [r for r in riders if all(x in r['name'] for x in d['keys']) and '181일' not in r['name']]
        b = [r for r in riders if all(x in r['name'] for x in d['keys'] + ['181일'])]
        if not a and not b: return ['미가입'], [], []
        av = sum(r['man'] for r in a) if a else 0; bv = sum(r['man'] for r in b) if b else None
        toks = [won(av), won(bv)] if bv is not None else [won(av)]
        return toks, [dict(name=r['name'], amt=r['man'], why='가입금액 그대로', rule='direct') for r in a + b], []
    L, iss = pay(riders, c['sc'])
    if c['mode'] == 'row':
        keys, ex = c['filt']
        if c['filt'][0] == 'BH':      # 뇌·심장 세부내역 줄 — 가입 여부는 그 줄 담보(통합치료비는 금액표 특약)가 설계서에 있는지
            k = c['filt'][1]
            rs = riders if k == 'etc' else [r for r in riders if (r.get('itc') if k == 'itc' else bh_group(r['name']) == k) and r['man'] > 0
                                             and not (k in ('g15', 'g17') and '상해' in r['name'])]   # 질병 사례 — 상해 전용 종수술비만 있으면 미가입(v8.65)
        else:
            rs = [r for r in riders if in_filt(r['name'], c['filt'])]
        if not rs: return (['미가입'] if c.get('part', 1) == 1 else []), L, iss    # 여러 값을 한 칸에 찍는 경우(2가지/3가지) '미가입'은 한 번만
        v = int(round(sum(l['amt'] for l in L if in_filt(l['name'], c['filt'], l.get('group')))))
        if v == 0 and c['filt_kcd'] and all(S.excluded(r, c['filt_kcd']) for r in rs): return ['면책'], L, iss
        return [won(v)], L, iss
    if c.get('filt'): L = [l for l in L if in_filt(l['name'], c['filt'], l.get('group'))]   # 표에 있는 줄만 합산하는 총 보장(v8.65)
    return [won(int(round(sum(counts(l, c['mode']) for l in L))))], L, iss

# ═══════════════ 특약 마스터 우주 ═══════════════
DB = matcher.DB                      # db.json(6개 상품) + 스마트 제안서 전용 보강 마스터(내Mom대로·내Mom같은 어린이보험, db_terms_extra.json)
DBID = {r['id']: r for r in DB['riders']}
PARENTS = {r['id'].split('-')[0] for r in DB['riders'] if re.match(r'^[^-]+-\d+$', r['id'])}
def universe():
    """특약 마스터 전체. 단 세부보장이 따로 있는 부모 특약(통81 → 통81-1·통81-2 등)은 뺀다 — 설계서에는 부모가
    「세부보장참조」 행(금액 없음)으로 실리고 금액은 세부보장 행에 붙으므로, 부모 이름으로 계산하면 세부보장과 겹친다."""
    out = []
    for rec in DB['riders']:
        if rec['id'] in PARENTS: continue
        if re.search(r'수술비\s*\(1-7종', rec['n']): continue      # 1-7종 부모(통74·케68·케95 등) — 설계서는 ┗ 종별 행으로 계산(아래에서 추가)
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
    # 설계서에만 나오는 1-7종 종별 행(┗ 수술비[질병N종]) — 부모 특약의 마스터를 물린다(matcher._link 와 같음)
    for cause in ('질병', '상해'):
        parent = next((r for r in DB['riders'] if S.nname(r['n']) == S.nname('수술비(1-7종, 연간3회한)[%s]' % cause)), None)
        for j in range(1, 8):
            nm = '┗ 수술비[%s%d종]' % (cause, j)
            out.append({'no': 'row-%s%d' % (cause, j), 'name': nm, 'man': 100, 'cat': (parent or {}).get('c'), 'codes': (parent or {}).get('k') or [], 'excl': (parent or {}).get('x') or [],
                        'hc': [], 'benefit': None, 'sub': None, 'matched': True, 'itc': None, 'product': '설계서 종별 행', 'db_id': 'row-%s%d' % (cause, j),
                        'via': (parent or {}).get('n')})
    # 1-5종 수술비의 종별 행 — 마스터는 '수술비Ⅱ(1-5종)' 한 줄이지만 설계서는 [질병1종]~[상해5종] 10줄로 적는다(설계서 표기 그대로 추가)
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
    """설계서에는 있는데 마스터(db.json)에 없는 담보명 — 규칙표만으로 계산되는 담보. 우주에 덧붙여 어느 칸에 잡히는지 함께 본다."""
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
    for c in CELLS:
        if c['kind'] != 'engine': continue
        L, iss = pay(uni, c['sc'])
        byno = {r['db_id']: r for r in uni}
        rows = []
        for l in L:
            r = byno.get(l.get('no')) if l.get('no') in byno else None
            # pay_lines 는 rider 의 'no' 를 그대로 싣는다 — 여기서는 db_id 를 no 에 넣어 두었으므로 그대로 찾는다
            rows.append(dict(name=l['name'], db_id=l.get('no'), product=(r or {}).get('product'), rule=l.get('rule'), why=l['why'], group=l['group'],
                             freq=l.get('freq'), amt=l['amt'], man=(r or {}).get('man'), each=l.get('each'),
                             in_row=(in_filt(l['name'], c['filt'], l.get('group')) if c['mode'] == 'row' else None), counted=counts(l, c['mode']) > 0,
                             itc=l.get('itc'), benefit=(r or {}).get('benefit'), sub=(r or {}).get('sub'), ncodes=len((r or {}).get('codes') or []),
                             nexcl=len((r or {}).get('excl') or []), nhc=len((r or {}).get('hc') or [])))
        res[c['id']] = dict(lines=rows, issues=iss)
    return res

# ═══════════════ 설계서 대조 ═══════════════
def run_design(pdf, html=None):
    riders = pipeline.read_riders(pdf)
    meta = BA.auto_meta(pdf)
    cells, toks = {}, []
    for c in CELLS:
        t, L, iss = cell_tokens(c, riders)
        cells[c['id']] = dict(tokens=t, lines=[dict(name=l['name'], amt=l['amt'], why=l['why'], rule=l.get('rule'), group=l.get('group'), freq=l.get('freq'), each=l.get('each'), no=l.get('no'),
                                                 in_row=(in_filt(l['name'], c['filt'], l.get('group')) if c['mode'] == 'row' else None), counted=(counts(l, c['mode']) > 0) if c['kind'] == 'engine' else True) for l in L],
                              issues=iss)
        toks += [(c['id'], x) for x in t]
    cmp = None
    if html and os.path.exists(html):
        h = open(html, encoding='utf-8').read()
        got = re.findall(r'<b class="v[^"]*">([^<]+)<i>만원</i></b>|<span class="na">(미가입|면책)</span>|<span class="txt">(지원가능)</span>', h)
        got = [a or b or c_ for a, b, c_ in got]
        mine = [x for _, x in toks]
        cmp = dict(html_n=len(got), spec_n=len(mine), equal=(got == mine),
                   diffs=[dict(i=i, cell=toks[i][0] if i < len(toks) else None, spec=mine[i] if i < len(mine) else None, html=got[i] if i < len(got) else None)
                          for i in range(max(len(got), len(mine))) if (mine[i] if i < len(mine) else None) != (got[i] if i < len(got) else None)])
    return dict(pdf=os.path.basename(pdf), meta={k: meta.get(k) for k in ('product', 'premium', 'sex')}, nriders=len(riders),
                riders=[dict(no=r.get('no'), name=r['name'], man=r['man'], matched=r.get('matched'), via=r.get('via'), itc=r.get('itc'), cat=r.get('cat'),
                             ncodes=len(r.get('codes') or []), nexcl=len(r.get('excl') or []), nhc=len(r.get('hc') or [])) for r in riders],
                cells=cells, cmp=cmp)

def spec_dump():
    out = []
    for c in CELLS:
        d = {k: v for k, v in c.items() if k != 'sc'}
        d['sc'] = c['sc']
        out.append(d)
    return out

if __name__ == '__main__':
    out = sys.argv[1]
    uni = universe()
    uni = add_design_only(uni, [pipeline.read_riders(p) for p in sys.argv[2:]])
    res = dict(version=S.RULEDOC.get('_note', ''), cells=spec_dump(), universe_n=len(uni), universe=run_universe(uni),
               universe_riders=[dict(db_id=r['db_id'], name=r['name'], product=r.get('product'), man=r['man'], cat=r.get('cat'), ncodes=len(r['codes']), nexcl=len(r['excl']), nhc=len(r['hc']),
                                     benefit=r.get('benefit'), sub=r.get('sub'), itc=r.get('itc'), via=r.get('via'), matched=r.get('matched')) for r in uni], designs=[])
    HTML = {'mom-40.pdf': 'deliver_mom40/tonghap40-ga-style.html', 'the510-44f.pdf': 'deliver_the510/the510-ga-style.html', 'mom5105-40.pdf': 'deliver_mom5105/mom5105-ga-style.html',
            'u355.pdf': 'ga_check/u355-ga.html', 'light355.pdf': 'ga_check/light355-ga.html', 'mom-new-40.pdf': 'ga_check/momnew-ga.html'}   # 대조 기준 = ga_proposal.py(실제 생성기) 지면(v8.65)
    SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for pdf in sys.argv[2:]:
        h = os.path.join(SP, HTML.get(os.path.basename(pdf), ''))
        d = run_design(pdf, h)
        print(os.path.basename(pdf), 'riders', d['nriders'], 'cmp', (d['cmp'] or {}).get('equal'), (d['cmp'] or {}).get('html_n'), (d['cmp'] or {}).get('spec_n'), 'diffs', len((d['cmp'] or {}).get('diffs') or []))
        for x in ((d['cmp'] or {}).get('diffs') or [])[:15]: print('   ', x)
        res['designs'].append(d)
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, default=str)
    print('cells', len(CELLS), 'engine cells', sum(1 for c in CELLS if c['kind'] == 'engine'), '->', out)
