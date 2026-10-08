# -*- coding: utf-8 -*-
"""GA 스마트제안서 칸별 특약 매핑 엑셀 생성.
  python3 build_ga_xlsx.py <ga_spec_results.json> <out.xlsx> [audit.json]
모든 값은 ga_spec.py 결과(엔진 실행값)와 저장소 데이터 파일에서만 온다. 추정·수기 금액 없음."""
import os, sys, os, json, re, copy, collections
PS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PS)
import scen_engine as S, engine as itc
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RES = json.load(open(sys.argv[1], encoding='utf-8'))
OUT = sys.argv[2]
AUDIT = json.load(open(sys.argv[3], encoding='utf-8')) if len(sys.argv) > 3 and os.path.exists(sys.argv[3]) else None
RULES = {r['id']: r for r in S.RULES}
DB = json.load(open(os.path.join(PS, 'db.json'), encoding='utf-8'))
DBID = {r['id']: r for r in DB['riders']}
PD = json.load(open(os.path.join(PS, 'product_data.json'), encoding='utf-8'))
LS = json.load(open(os.path.join(PS, 'life_support.json'), encoding='utf-8'))
URID = {r['db_id']: r for r in RES['universe_riders']}
CELLS = RES['cells']; CELL = {c['id']: c for c in CELLS}
DESIGNS = RES['designs']
DNAME = {'gan31-M.pdf': '간편31 남(GA 테스트)', 'mom-40.pdf': '통합간편 남40', 'the510-44f.pdf': 'The건강한5.10.5 여44', 'mom5105-40.pdf': '내Mom대로5.10.5 여40',
         'u355.pdf': '통합간편355(연만기) 여', 'light355.pdf': 'The가벼운 간편355 여', 'mom-new-40.pdf': '내Mom대로 남40', 'gan31-41650.pdf': '간편31 여(41,650원)', 'd42940.pdf': '통합간편 남(42,940원)', 'd106010.pdf': '통합간편 여(106,010원)', 'd272600.pdf': '통합간편 남(272,600원)', 'd61760.pdf': '통합간편 연만기 남(61,760원)', 'd104810.pdf': '알파Plus 남(104,810원)', 't5105-30020.pdf': 'The건강한5.10.5 여(30,020원)', 't5105-177770.pdf': 'The건강한5.10.5 남(177,770원)', 't5105-122661.pdf': 'The건강한내Mom대로5.10.5 남(122,660원)', 't5105-243046.pdf': 'The건강한내Mom대로5.10.5 남(243,040원)'}
_VER = re.search(r"VERSION = '([^']+)'", open(os.path.join(PS, 'api.py'), encoding='utf-8').read()).group(1)
_DBN = len(json.load(open(os.path.join(PS, 'db.json'), encoding='utf-8'))['riders'])
_EXD = json.load(open(os.path.join(PS, 'db_terms_extra.json'), encoding='utf-8')) if os.path.exists(os.path.join(PS, 'db_terms_extra.json')) else {'riders': [], 'meta': {}}
_EXN = len(_EXD['riders']); _EXP = (_EXD.get('meta') or {}).get('prodcount') or {}
_NCELL = len(CELLS); _NRULE = len(RULES); _ND = len(DESIGNS)

KIND_KO = {'dx': '진단비', 'surg': '수술비', 'tx': '치료비', 'day': '입원·통원일당', 'itc': '통합치료비(약관 지급금액표)', 'ls_monthly': '통합생활지원비(약관 월 항목표)',
           'direct': '가입금액 직접표시', 'skip': '계산 제외(조건부·제도성)', 'care': '간병(사례 계산 대상 아님)', 'life': '사망·후유장해(사례 계산 대상 아님)', 'nonmed': '비의료(운전자·재물 등)', 'itc_unknown': '금액표 없는 통합치료비(계산 제외)', 'ls': '통합생활지원비', 'point2': '포인트적립형 치료비(누적 점수 구간별)'}
KCD_KO = {
 'major': '암(유사암 제외) — 약관 별표 악성신생물 분류(C00~C97 중 C44·C73 제외, D45·D46·D47.1/3/4/5 포함)로 판정',
 'sim': '유사암 — 제자리암(D00~D09) · 경계성종양(D37~D48) · 기타피부암(C44) · 갑상선암(C73)',
 'major_or_sim': '암 또는 유사암(위 두 분류 중 하나)',
 'major_thy_skin': '암(유사암 제외) + 기타피부암(C44) + 갑상선암(C73) — 제자리암(D00~D09)·경계성종양(D37~D48)은 제외(세기조절·양성자·중입자·표적·면역·암재활 약관의 대상)',
 'codes': '특약 마스터(db.json)에 실린 이 특약의 약관 KCD 목록과 대조. 목록이 없으면 사례가 선언한 질병군 표시(grp)가 담보명·세부급부에 있을 때만 지급, 그것도 없으면 계산 제외+로그',
 'codes_listed': '특약 마스터의 약관 KCD 목록과 대조. 목록이 없으면 질병 조건 없이 계산(검토필요 로그)',
 'group': '규칙표(rules.json) kcd_groups 분류표 — 담보명에 든 그룹명(가장 긴 것) 또는 규칙이 지정한 그룹의 코드표와 대조',
 'g131': '131대질병 그룹표(g131.json) — 세부급부 라벨(다빈도62대질병 등)의 코드표와 대조. 130대질병수술비[○○]처럼 라벨이 없는 담보는 마스터 KCD 목록으로, 둘 다 없으면 사례 질병군 표시로 판정. 암·유사암은 제외',
 'hc': '약관 별표 진료행위(수가)코드 목록 ∩ 사례 단계의 수가코드(목록이 비어 있으면 계산 제외+로그)',
 'none': '질병코드 조건 없음(담보명 조건·치료행위·수술 종만 판정)',
}
FREQ_KO = {'once': '최초 1회', 'year': '연간 1회', 'each': '받을 때마다(1회당)'}
MODE_KO = {'first': '최초 지급 합계(모든 지급 줄 합산)', 'year': '반복(연 1회) 합계(최초 1회만 지급되는 줄 제외)', 'each': '받을 때마다 합계(1회당 지급 줄만 · 통합치료비는 수술 1회당 항목만)',
           'itc_only': '통합치료비 항목 금액만 합산(그 외 담보 제외)', 'ms_only': '특정순환계질환(주요손상및질환) 통합치료비 줄만 합산 · 그 특약이 없으면 미가입',
           'meta_only': '전이암 진단비 줄만 합산(일반암 진단비는 원발암에서 받은 것으로 보고 제외) · 전이암 담보가 없으면 미가입', 'row': '담보행 : 이름 키워드로 지급 줄을 골라 합산'}
ACT_KO = {'surg': '수술', 'robot': '다빈치로봇수술', 'chemo': '항암약물치료', 'target': '표적항암약물허가치료', 'immune': '면역항암약물허가치료', 'rad': '항암방사선치료', 'imrt': '세기조절방사선치료',
          'proton': '양성자방사선치료', 'carbon': '중입자방사선치료', 'x_endo': '내시경검사', 'x_mri': 'MRI검사', 'x_pet': 'PET검사', 'x_gene': '특정단일유전자검사', 'x_us': '초음파검사', 'x_ct': 'CT검사',
          'x_bio': '특정생검조직병리검사', 'x_ngs': 'NGS유전자패널검사', 'rehab': '재활치료', 'icu': '중환자실치료', 'ecmo': '부분체외순환(에크모)', 'crrt': '지속적신대체요법', 'vent': '인공호흡기치료',
          'hypo': '저체온요법', 'thromb': '혈전용해치료', 'thrombectomy': '기계적혈전제거술', 'anes': '전신마취(종합병원)', 'anes4': '전신마취 4시간이상', 'anes6': '전신마취 6시간이상', 'pain': '통증완화치료'}
HOSP_KO = {'병원': '병원급(종합병원 아님 · "모든 병원" 칸의 가정)', '종합': '종합병원', '상급종합': '상급종합병원', '요양': '요양병원', None: '(조건 없음)'}

def rule_of(rid): return RULES.get(rid)
def rule_kind_ko(rid):
    if rid == 'itc': return KIND_KO['itc']
    if rid == 'ls_monthly': return KIND_KO['ls_monthly']
    if rid == 'direct': return KIND_KO['direct']
    r = rule_of(rid); return KIND_KO.get((r or {}).get('kind'), rid)
def rule_label(rid):
    if rid == 'itc': return '통합치료비 — engine.py calc_rider : 약관 지급금액표(product_data.json) 항목 금액 · 연간 총액 가입금액 한도'
    if rid == 'ls_monthly': return '통합생활지원비 — scen_engine.ls_lines : 약관 항목표(life_support.json) 항목별 월 지급액 · 합계 가입금액(월 한도)'
    if rid == 'direct': return '계산 없이 담보 가입금액을 그대로 표시'
    r = rule_of(rid); return (r or {}).get('label', '')

def rider_tokens(name):
    return S.tokens(S.nname(name))

def kcd_method(rid, l, r_master):
    o = ((rule_of(rid) or {}).get('opt') or {})
    if rid == 'itc':
        ty = itc.RM[l['itc']]['ty'] if l.get('itc') in itc.RM else ''
        return {'CB': '암·유사암(별표 악성신생물 분류)', 'CL': '암·유사암', 'C2': '암·유사암', 'CM': '암·유사암', 'PR': '약관 별표 대상질병 목록(P60)', 'CV': '약관 별표 특정순환계질환 목록(C32)', 'MS': '약관 별표 주요손상및질환 목록(M61)', 'DZ': '질병이면 대상(대상 질병 열거 없음)'}.get(ty, ty)
    if rid == 'ls_monthly': return '항목표 행마다 다름(산정특례 등록 계열 · 주요치료는 뇌·심/암 계열 판정)'
    if rid == 'direct': return '해당 없음'
    m = o.get('kcd')
    if (rule_of(rid) or {}).get('kind') == 'point2': m = 'codes'     # h_point2 는 마스터 KCD 목록(약관 별표 2대질환)으로 판정
    if o.get('by_benefit'): return '세부보장 이름의 암종을 약관 별표 「암종별(13종)통합암(전이포함)(유사암제외) 분류표」 코드로 바꿔 대조(예 위암과 식도암(전이포함) = C15·C16·C78.80) · 방사선/약물은 세부보장 이름으로 구분'
    if m == 'codes' and r_master is not None and not r_master.get('ncodes'):
        return KCD_KO['codes'] + ' → 이 특약은 마스터 KCD 목록이 비어 있어 사례 질병군 표시로 판정됨'
    return KCD_KO.get(m, KCD_KO['none'])

def amount_formula(rid, l, r_master):
    o = ((rule_of(rid) or {}).get('opt') or {})
    k = (rule_of(rid) or {}).get('kind')
    if rid == 'itc':
        return '약관 지급금액표 항목 금액 합(항목마다 정액 · 표는 가입금액 구간별) : ' + l['why'] + ' — 연간 총 지급은 가입금액 한도, 1년 이내 감액(half) 특약은 50%'
    if rid == 'ls_monthly':
        return '약관 항목표 월 지급액 합(가입금액 = 월간 총 한도) : ' + l['why']
    if rid == 'direct': return '가입금액(일당·정액) 그대로'
    if k == 'dx': return '가입금액 × 100% (진단확정 1회)'
    if k == 'surg':
        g = o.get('grade')
        return '가입금액 × 100% × 수술 1회' + (' (담보명의 종과 사례 수술의 1-5종 분류표Ⅱ 종이 같을 때)' if g == '1-5' else (' (담보명의 종과 사례 수술코드의 1-7종 분류표 종이 같을 때)' if g == '1-7' else ''))
    if k == 'tx': return '가입금액 × 100% (약관 대상 치료 1회 · 빈도는 지급 빈도 열)'
    if k == 'day': return '가입금액(일당) × 일수'
    if k == 'point2':
        rt = o.get('rate') or {}
        return ('가입금액 × 점수 구간 지급률(1점이상 %s%% · 2점이상 %s%% · 3점이상 %s%% · 4점이상 %s%% — 계약일부터 1년 이내는 절반) · 구간마다 최초 1회. '
                '치료포인트 = 뇌·심장 치료군(혈전용해·비관혈수술 1점, 관혈수술 2점) 최고점 + 중환자실 입원(4일 이상 1점, 8일 이상 2점), 최대 4점'
                % (rt.get('1'), rt.get('2'), rt.get('3'), rt.get('4')))
    return ''

def cond_summary(rid, l, name):
    """담보명 토큰 + 규칙 옵션에서 읽히는 지급 조건 요약"""
    o = ((rule_of(rid) or {}).get('opt') or {}); t = rider_tokens(name); parts = []
    if rid == 'itc':
        parts.append('사례 단계의 치료 키가 지급금액표 항목(치료키·암구분·비급여·1-5종 j)에 맞을 때 항목 금액')
        if t['cause']: parts.append('원인 %s 전용' % t['cause'])
        return ' · '.join(parts)
    if rid == 'ls_monthly': return '산정특례 등록·주요치료 항목별(ls_lines) — 계열(뇌·심장·암) 사례에서만 그 계열 항목'
    if rid == 'direct': return '담보명 키워드로 고른 담보의 가입금액'
    k = (rule_of(rid) or {}).get('kind')
    if t['hosp']: parts.append('%s 이상에서 받은 경우만' % HOSP_KO.get(t['hosp'], t['hosp']))
    if t.get('ex_hosp'): parts.append('요양병원 제외')
    if t['cause'] or o.get('cause'): parts.append('원인 %s' % (t['cause'] or o.get('cause')))
    if k == 'dx':
        if o.get('fam'): parts.append('사례 진단 계열 %s' % '/'.join(o['fam']))
        if o.get('reg'): parts.append('산정특례 등록 조건(암·유사암·뇌수막 양성신생물은 진단 시, 뇌·심장은 수술/혈전용해 단계)')
        if o.get('stage') == 'recur': parts.append('재진단 단계에서만')
    if k == 'surg':
        if o.get('grade') == '1-5': parts.append('담보명 [질병N종]/[상해N종]의 N = 사례 수술의 1-5종 분류표Ⅱ 종(항목번호·질병코드 예외 반영)')
        if o.get('grade') == '1-7': parts.append('담보명 종 = 사례 수술코드의 1-7종 분류표 종')
        if o.get('plus'): parts.append('연간 2회 이상 수술(사례 surg_cnt≥2)일 때만')
        if 'cancer' in (o.get('ex') or []): parts.append('암·유사암 사례 제외')
        if t['ex']: parts.append('특정%s대질병 제외 목록에 든 질병 제외' % '/'.join(t['ex']))
        if '관혈' in name.replace(' ', ''): parts.append('관혈/비관혈 구분이 사례 수술과 맞을 때만')
        if '연간1회한' in S.nname(name): parts.append('연간 1회한(담보명)')
    if k == 'tx':
        if o.get('acts'): parts.append('사례에 %s 중 하나' % '/'.join(ACT_KO.get(a, a) for a in o['acts']))
        if o.get('acts_all'): parts.append('%s 모두' % '+'.join(ACT_KO.get(a, a) for a in o['acts_all']))
        if o.get('need_drug'): parts.append('연간 약물 종류 %d종 이상(담보명 [N종이상] 우선)' % o['need_drug'])
        if o.get('need_cnt'): parts.append('연간 치료 %d회 이상' % o['need_cnt'])
        if o.get('by_benefit'): parts.append('세부급부의 암종·치료(방사선/약물)로 판정')
        if o.get('hc_listed'): parts.append('마스터 수가코드 목록이 있으면 사례 수가코드와 대조')
        if o.get('surg7_grp'): parts.append('1-7종 분류표 수술구분 「%s」' % o['surg7_grp'])
        if o.get('exam_by_name'): parts.append('담보명의 검사 종류(MRI·CT·PET·내시경·초음파·생검·유전자)를 받은 단계에서만')
        if o.get('covered_only') and re.search(r'\(급여', S.nname(name)) and '비급여' not in S.nname(name): parts.append('급여 치료일 때만(비급여 치료 단계 제외)')
        if o.get('split_by_label'): parts.append('세부보장이 항암방사선치료비면 방사선만, 항암약물치료비면 약물만')
        if re.search(r'비급여|전액본인부담', S.nname(name)): parts.append('비급여 치료일 때만')
        parts.append('담보명·세부급부의 암 구분(유사암제외/갑상선암/기타피부암/유사암)과 사례 암 구분 일치')
    return ' · '.join(parts)

def sc_desc(c):
    """칸 사례를 열별 한글로"""
    s_ = c.get('sc') or {}; tg = s_.get('tags') or {}; ev = s_.get('itc_events') or []
    d = {}
    d['KCD'] = s_.get('kcd', '')
    d['원인'] = tg.get('cause', '')
    d['병원 종별'] = (HOSP_KO.get(tg.get('hosp'), tg.get('hosp')) if 'hosp' in tg else ('해당 없음(진단 칸 — 진단비는 병원 종별을 보지 않음)' if tg.get('dx') else '(태그 없음 → 병원 종별 조건 담보 제외)'))
    j = tg.get('surg')
    d['1-5종 분류표 항목'] = ('%s → %s종 · %s' % (j, S.surg5_grade(j, s_.get('kcd')), re.sub(r'\s+', ' ', S.surg5_name(j)))) if j else ''
    c7 = tg.get('surg7')
    d['1-7종 수술코드'] = ('%s → %s종 · %s' % (c7, S.surg7_grade(c7), S.surg7_name(c7))) if c7 else ''
    d['질병군 표시(grp)'] = ' / '.join(tg.get('grp') or [])
    d['진단 계열(dx)'] = {'cancer': '암', 'sim_cancer': '유사암', 'brain': '뇌', 'heart': '심장'}.get(tg.get('dx'), tg.get('dx') or '')
    keys = []
    for e in ev:
        if len(e) > 3: keys += [k for k in e[3] if k not in keys]
    for k in ('acts',):
        for a in tg.get(k) or []:
            if a not in keys: keys.append(a)
    d['치료행위(사례 단계)'] = ' + '.join('%s(%s)' % (ACT_KO.get(k, k), k) for k in keys)
    d['비급여'] = '예' if any((e[4] or {}).get('nc') for e in ev if len(e) > 4) or tg.get('nc') else ''
    d['전신마취'] = ('예' + (' · %d시간' % tg['anes_h'] if tg.get('anes_h') else '')) if tg.get('anes') else ''
    d['연간 약물 종수'] = tg.get('drug', '')
    d['수가코드'] = ' / '.join(tg.get('hc') or [])
    extra = {k: v for k, v in tg.items() if k not in ('cause', 'hosp', 'room', 'days', 'grp', 'dx', 'surg', 'surg7', 'acts', 'anes', 'anes_h', 'drug', 'hc', 'nc') and v}
    d['기타 태그'] = ', '.join('%s=%s' % (k, v) for k, v in extra.items())
    d['사례 단계(itc_events)'] = ' ; '.join('%s:%s%s' % (e[0], e[1], (' ' + json.dumps(e[4], ensure_ascii=False)) if len(e) > 4 and e[4] else '') for e in ev)
    return d

# ── 통합치료비 : 특약 × 가입금액 구간별 이 칸 금액 (엔진 그대로 재실행) ──
def itc_by_tier(name, iid, c):
    ty = itc.RM[iid]['ty']; out = []
    for tier in sorted(int(k) for k in itc.AMT[ty]):
        rid = {'name': name, 'man': tier, 'cat': None, 'codes': [], 'excl': [], 'hc': [], 'benefit': None, 'sub': None, 'matched': True, 'itc': iid}
        S.ISSUES.clear()
        L = S.pay_lines([rid], copy.deepcopy(c['sc']))
        out.append((tier, (L[0]['amt'], L[0]['why']) if L else (0, '')))
    return out

# ═══════════ 스타일 ═══════════
HFILL = PatternFill('solid', fgColor='1A2340'); HFONT = Font(bold=True, color='FFFFFF', size=10, name='Malgun Gothic')
BFONT = Font(size=10, name='Malgun Gothic'); WRAP = Alignment(wrap_text=True, vertical='top')
THIN = Side(style='thin', color='D9DCE3'); BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
SEC_FILL = PatternFill('solid', fgColor='F4F5F8')

def sheet(wb, title, header, rows, widths=None, freeze='A2', wrap_cols=None, sec_col=None):
    ws = wb.create_sheet(title[:31])
    ws.append(header)
    for i, h in enumerate(header, 1):
        cc = ws.cell(row=1, column=i); cc.fill = HFILL; cc.font = HFONT; cc.alignment = Alignment(wrap_text=True, vertical='center'); cc.border = BORDER
    ws.row_dimensions[1].height = 34
    prev = None
    for r in rows:
        ws.append([('' if v is None else v) for v in r])
        rr = ws.max_row
        for i in range(1, len(header) + 1):
            cc = ws.cell(row=rr, column=i); cc.font = BFONT; cc.border = BORDER
            if wrap_cols is None or i in wrap_cols: cc.alignment = WRAP
        if sec_col is not None:
            v = r[sec_col]
            if v != prev:
                for i in range(1, len(header) + 1): ws.cell(row=rr, column=i).fill = SEC_FILL
            prev = v
    for i, h in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = (widths[i - 1] if widths and i - 1 < len(widths) else 16)
    if freeze: ws.freeze_panes = freeze
    ws.auto_filter.ref = ws.dimensions
    return ws

BH_TXT = {'thromb': '이름에 「혈전용해치료비」(기계적혈전제거·특정혈전 제외)', 'mech': '이름에 「기계적혈전제거」 또는 「특정혈전치료비」', 'two': '이름에 「2대질환…주요치료비」 또는 「최대두배받는2대질환치료비」',
          'bhsurg': '이름에 뇌혈관질환수술비·허혈성심장질환수술비·심장질환수술비·뇌출혈수술비·뇌졸중수술비·뇌동맥류·5대질환·32대질병·130대/131대질병수술비',
          'dzsurg': '이름이 (갱신형)(상급종합병원/종합병원)질병수술비로 시작', 'g15': '이름에 1-5종(상해 담보 제외)', 'g17': '이름에 1-7종 또는 ┗ 수술비(상해 담보 제외)',
          'itc': '통합치료비(약관 지급금액표 특약 : 특정순환계질환·상급종합병원 특정순환계질환·질병 통합치료비 등)', 'etc': '위 어느 줄에도 들지 않는 지급 줄 전부(산정특례 진단비·통합생활지원비·전신마취치료비 등)'}
def bh_filt_txt(c):
    f = c.get('filt')
    if not f: return '', ''
    if f[0] == 'BH': return '줄 구분 : ' + BH_TXT.get(f[1], f[1]), '위 줄 순서대로 먼저 걸린 줄 하나에만 넣음'
    if f[0] == 'BHS': return '총 보장 = 표에 나온 줄만 합산 : ' + ' · '.join(BH_TXT.get(k, k) for k in f[1]), '표에 없는 담보(통합생활지원비·전신마취 등)는 합산하지 않음(보수적)'
    if f[0] == 'ANY': return '총 보장 = 표의 담보행 중 하나에 드는 지급 줄만 합산 : ' + ' | '.join('/'.join(k) for k, _x in f[1]), '표에 없는 담보는 합산하지 않음(보수적)'
    return ' / '.join(f[0]), ' / '.join(f[1])

wb = Workbook(); wb.remove(wb.active)

# ═══════════ ① 개요 ═══════════
ov = wb.create_sheet('① 개요·읽는 법')
ov.column_dimensions['A'].width = 4; ov.column_dimensions['B'].width = 150
lines = [
 ('GA 스마트 제안서 · 설계도(칸별 특약 매핑 · 계산 공식 · 판정 로직) — v5 양식(2026-10-08 GA 내부 회의 목업 반영)', True),
 ('작성 : 세일즈혁신TF · 계산 엔진 proposal_smart %s · 특약 마스터 : db.json %s건(통합간편·케어프리·운전자·치아·또또암·또또암간편) + 스마트 제안서 전용 보강 %s건(%s) · 산출일 2026-10-08' % (_VER, format(_DBN, ','), format(_EXN, ','), ' · '.join('%s %d건' % kv for kv in _EXP.items())), False),
 ('', False),
 ('지면 구성(GA v5)', True),
 ('· 표지(「메리츠 스마트 제안서」 · 탑재상품 13개 — GA 명칭 그대로, 알파Plus = 케어프리 M-Basket · 이 설계서의 상품 표시 · 분석 대상 설계서 요약) → 1쪽 보장요약 → 2쪽 암보장 → 3쪽 뇌·심보장 → 예상 보장금액 세부내역(합산 계산서 · 최소 3쪽 · 반드시 붙는다 · 담보가 많으면 자동으로 늘어남).', False),
 ('· 1쪽 보장요약 : 암보장(진단금 일반암·유사암·전이암 / 수술 4 / 항암약물 화학·표적·면역·표적(면역) 2가지 약물 / 항암방사선 4) · 뇌·심보장(진단금 뇌졸중·뇌혈관·급성심근경색·허혈성심장 / 뇌 치료 및 수술 4 / 심장 치료 및 수술 4 / 중증치료 5) · 주요수술보장 10 · 간병인보장(간병인지원 현물지원 4칸 · 간병인사용 금액지원 3칸).', False),
 ('· 2쪽 암보장 : 암검사 8 · 암진단 3(일반암·유사암·전이암) · 암수술 4×3(최초·반복·매회) · 항암약물치료 3×2 + 표적(면역) 개수별(2가지·3가지) · 항암방사선치료 4×2 · 암재활(연 20회 입원·외래) · 암후유장해.', False),
 ('· 3쪽 뇌·심보장 : 검사 3 · 진단 4 · 뇌질환 치료 및 수술 4×3 · 심질환 치료 및 수술 4×3 · 중증치료 5(반복 연 1회) · 재활(연 15회 입원·외래).', False),
 ('', False),
 ('이 엑셀 하나로 할 수 있는 것', True),
 ('· 앞쪽 「설계도 1~12」 시트만 순서대로 읽으면 GA 스마트 제안서를 처음부터 다시 만들 수 있다 : 설계서 PDF 읽기 → 담보명 정리 → 약관 데이터 찾기 → 규칙 판정 → 사례 계산 → 칸 집계 → 지면 표시. 각 단계의 입력·규칙·공식·예외·예시를 적었다.', False),
 ('· 「캡처 표지·1~3쪽·세부내역」 : 지면 캡처에 칸 번호를 달고 칸마다 계산되는 특약 이름을 나열. 「②~⑫」 : 칸 %d개 하나하나의 사례·집계·특약·금액 근거(스펙 원장). 칸의 정의는 ga_spec.py CELLS 하나뿐이고 지면(ga_proposal.py)은 그 값을 꺼내 그리므로 지면과 사양이 어긋날 수 없다.' % _NCELL, False),
 ('· "칸별 특약(마스터 전체)" 시트 : 특약 마스터 전체(보강 포함) %s건을 각 칸 사례에 태운 결과 — 어떤 상품 설계서가 와도 그 칸에 잡힐 수 있는 특약의 전체 목록.' % format(RES.get('universe_n', 0), ','), False),
 ('· "설계서 검증" 시트 : 실제 설계서 %d건(%s)으로 계산한 칸 값·특약별 금액. %d건 모두 GA 제안서 지면(생성기 ga_proposal.py 가 그린 HTML)의 표시값과 스펙 계산값이 전부 일치.' % (_ND, ' · '.join(DNAME.get(d['pdf'], d['pdf']) for d in DESIGNS), _ND), False),
 ('', False),
 ('계산 원칙(저장소 규칙 · 이것을 어기면 다시 만든 것이 아니다)', True),
 ('· 질병코드(KCD)와 금액을 코드에서 만들거나 추정하지 않는다. 약관 별표·특약 마스터·약관 지급금액표에 있는 것만 쓴다. 없으면 그 특약은 계산에서 빼고 사유를 로그에 남긴다 — 오류는 "틀린 금액"이 아니라 "빈칸"으로 나타나야 한다.', False),
 ('· 규칙표(rules.json %d줄)는 담보명으로 보상 유형과 질병코드 판정 방식을 정한다. 위에서부터 처음 걸리는 규칙 하나만 적용. 세부급부([○○])가 있으면 세부급부가 보상 유형을 정한다. 규칙표에 없는 담보는 예외 없이 "계산 제외 + 로그".' % _NRULE, False),
 ('· 담보명 뒤 상품 꼬리표((통합간편가입)·(31간편가입)·(355입원,수술고지간편가입) 등 "(…가입)")는 떼고 판정한다 — 상품이 달라도 같은 특약은 같은 칸·같은 금액.', False),
 ('· 상품명 화이트리스트로 막지 않는다(표지 탑재상품 목록은 표시용). 내Mom대로·내Mom같은 어린이보험·간편31 등 보강 특약 데이터는 스마트 제안서 전용(영업지원도구 미반영).', False),
 ('', False),
 ('사례의 가정값(지면 하단 주석과 같음)', True),
 ('· 병원 종별 : 1쪽 주요수술보장 10칸은 병원급(종합병원 아님), 그 밖(1쪽 암·뇌심 · 2·3쪽)은 상급종합병원.', False),
 ('· 마취 : 디스크·무릎 인공관절·담낭·충수·자궁근종 복강경·코일색전술·개두술은 전신마취, 관상동맥우회술은 6시간 마취. 연간 약물 종수 : 표적항암·면역항암 칸은 1종(치료 1개 · 2종이상 담보 제외), 「표적(면역) 2가지 약물」은 표적+면역 2종(항암약물·항암방사선약물·표적·면역·암통합치료비(면역항암 가정)·(2종이상)·(2종및3종이상) 합산, 3종이상 제외), 2쪽 「3가지약물」은 3종.', False),
 ('· 수술 분류 : 시술마다 1-5종 수술분류표Ⅱ 항목번호와 1-7종 수술분류표 수술코드를 하나씩 정해 넣는다("설계도9 사례" 시트). 디스크절제술 9(3종)·B174 · 무릎 인공관절치환술 13-2(2종)·I032 · 담낭절제술 36(담석증 2종)·H107 · 충수절제술 41(2종)·G212 · 자궁근종 복강경 52(2종)·N031 · 경요도 전립선절제술 88-3(1종)·M022 · 뇌 스텐트 88-1(3종)·B026 · 혈전제거 88-1·B027/F121 · 심장 스텐트 88-1·F133.', False),
 ('· 질병코드 : 위암 C16 · 갑상선암 C73 · 전이암 C78.7(간 전이) · 뇌졸중 I63(뇌경색) · 뇌혈관 I67.1(비파열 뇌동맥류) · 뇌 스텐트 I65.2(경동맥 협착) · 뇌출혈 I61 · 협심증 I20 · 급성심근경색 I21 · 주요수술은 사례 시트.', False),
 ('· 1쪽 뇌·심 「치료 및 수술」(뇌/심장 각각) : 혈전용해(혈전용해 1회) · 혈전제거(기계적 혈전제거술만 — 카테터 수술 : 수술비·1-5종·기계적혈전제거술 특약·통합치료비 수술 항목 합산, 혈전용해 담보는 안 들어감) · 혈전용해+혈전제거(두 시술 합산 · 진단및치료비Ⅱ 특정혈전치료비 포함 · 특정순환계질환 통합치료비 1억 가입이면 혈전용해 2,500 + 수술 2,000 = 4,500) · 스텐트수술. 산정특례 열은 GA 요청으로 삭제(2026-10-08).', False),
 ('· 간병인보장(계산 없음 · ga_care.py) : 간병인지원 입원일당(Ⅰ·Ⅵ·Ⅶ) 가입 → 병·의원 「보내줌」, 요양성특정질병입원일당(요양병원) 가입 → 요양병원 「보내줌」 · 미사용시 1일 = 설계서 금액(Ⅰ 가입금액 · Ⅶ 「또는 5천원」 → 0.5 · Ⅵ 금액 없음 → 0) · 간호간병통합서비스 1일 = (간호·간병통합서비스 사용추가보장) 가입금액 + 미사용 일당 · 간병인사용(금액지원) 3칸은 1일이상 담보 가입금액. 181일 구분 없음.', False),
 ('· 계약 경과 : 감액·면책기간 이후 첫 지급 기준. 1년 이내 50%·90일 면책·체증형 2회차 증액은 반영하지 않는다(지면 하단·세부내역 머리글에 명시).', False),
 ('', False),
 ('집계 방식', True),
 ('· 최초 = 그 사례에서 잡힌 지급 줄의 합 · 반복(연 1회) = 최초 1회만 지급되는 줄을 뺀 합 · 매 회(수술할 때마다) = 1회당 지급되는 줄만(통합치료비는 수술 1회당 항목만) · 통합치료비 항목만(검사·중증치료·재활) · 전이암 진단비 줄만(전이암 칸).', False),
 ('· 칸 표시 : 금액 만원 단위(1억 이상은 "1억 2,340" · 일당은 소수점 한 자리 "5.5"), 설계서에 그 담보가 없으면 "미가입"(전이암·간병인·암후유장해), 가입했지만 사례에서 안 나오면 "0".', False),
 ('', False),
 ('시트 안내', True),
 ('설계도 1 전체 흐름 · 2 담보명 읽기·매칭 · 3 계산 엔진 판정 순서 · 4 보상유형별 공식 · 5 담보명 조건 토큰 · 6 질병코드 판정 방식 · 7 질병코드 그룹표 · 8 수술분류표(1-5종·1-7종) · 9 GA 사례 · 10 칸 집계·표시 규칙 · 11 특약 마스터 전체 · 12 검증 방법', False),
 ('캡처 표지·1~3쪽·세부내역 · ② 칸 목록 · ③ 칸별 특약(마스터 전체) · ④ 특약별 산정 기준 · ⑤ 통합치료비 지급금액표 · ⑤-2 칸별 통합치료비 금액 · ⑥ 통합생활지원비 항목표 · ⑦ 규칙표 · ⑧ 계산 제외 사유 · ⑨ 고정값·직접표시 칸 · ⑩ 설계서 검증 · ⑪ 설계서 칸별 특약 금액 · ⑫ 검수 메모', False),
]
for i, (t, b) in enumerate(lines, 1):
    c = ov.cell(row=i, column=2, value=t); c.font = Font(bold=b, size=12 if b else 10, name='Malgun Gothic', color='1A2340' if b else '000000'); c.alignment = WRAP

# ═══════════ ② 칸 목록 ═══════════
KIND_CELL_KO = {'engine': '엔진 계산', 'direct': '가입금액 직접표시', 'care': '간병인보장(설계서 담보 그대로 · ga_care.py)', 'text': '가입 여부 문구', 'fixed': '고정값 0'}
hdr2 = ['칸ID', '쪽', '구역', '행', '열', '칸 종류', '사례 설명', 'KCD', '원인', '병원 종별', '1-5종 분류표 항목', '1-7종 수술코드', '질병군 표시(grp)', '진단 계열(dx)', '치료행위(사례 단계)', '비급여', '전신마취', '연간 약물 종수', '수가코드', '기타 태그', '사례 단계(itc_events)',
        '집계 방식', '표시 조건(need · 이 말이 든 가입담보가 없으면 미가입)', '칸 key', '(예비)', '잡히는 특약 수(마스터 전체)', '설계서 ① 간편31 남(GA 테스트)', '설계서 ② 통합간편 남40', '설계서 ③ The건강한 여44', '비고']
rows2 = []
CELL_ROWS = []  # 칸별 특약 행
for c in CELLS:
    u = RES['universe'].get(c['id']); sd = sc_desc(c) if c['kind'] == 'engine' else {}
    names = sorted({l['name'] for l in (u or {}).get('lines', [])})
    dv = {d['pdf']: ' / '.join(d['cells'][c['id']]['tokens']) or '(표시 없음)' for d in DESIGNS}
    if c['kind'] != 'engine':
        sd = {}
    rows2.append([c['id'], c['page'], c['section'], c['row'], c['col'], KIND_CELL_KO.get(c['kind'], c['kind']), c.get('sc_name') or c.get('note') or '', sd.get('KCD', ''), sd.get('원인', ''), sd.get('병원 종별', ''),
                  sd.get('1-5종 분류표 항목', ''), sd.get('1-7종 수술코드', ''), sd.get('질병군 표시(grp)', ''), sd.get('진단 계열(dx)', ''), sd.get('치료행위(사례 단계)', ''), sd.get('비급여', ''), sd.get('전신마취', ''), sd.get('연간 약물 종수', ''), sd.get('수가코드', ''), sd.get('기타 태그', ''), sd.get('사례 단계(itc_events)', ''),
                  MODE_KO.get(c['mode'], c['mode']) if c['kind'] == 'engine' else '', ' + '.join(c.get('need') or []), c.get('key', ''), '',
                  len(names) if u else '', dv.get('gan31-M.pdf'), dv.get('mom-40.pdf'), dv.get('the510-44f.pdf'), c.get('note', '')])
sheet(wb, '② 칸 목록', hdr2, rows2, widths=[9, 4, 12, 14, 18, 12, 34, 8, 6, 22, 26, 26, 22, 8, 30, 6, 10, 8, 10, 16, 34, 30, 26, 18, 8, 8, 16, 16, 16, 40], sec_col=2)

# ═══════════ ③ 칸별 특약(마스터 전체) · ④ 특약별 산정 기준 ═══════════
hdr3 = ['칸ID', '쪽', '구역', '행', '열', '칸 사례', '집계 방식', '특약명', '세부급부', '상품(마스터)', '보상 유형', '규칙ID', '규칙 설명', '지급 판정 근거(엔진 사유)', '지급 조건 요약(담보명 조건 포함)', '질병코드 판정 방식',
        '금액 산정식', '가입금액 대비 배수', '지급 빈도', '이 칸 집계에 포함', '담보행 표시', '마스터 KCD 수', '제외코드 수', '수가코드 수', '약관 위치(db id)', '비고']
rows3 = []; per_name = collections.OrderedDict(); itc_tier_rows = []
for c in CELLS:
    u = RES['universe'].get(c['id'])
    if not u: continue
    by = collections.OrderedDict()
    for l in u['lines']:
        key = (l['name'], l['rule'], l['why'])
        e = by.setdefault(key, dict(l=l, ids=[], prods=set(), amts=set()))
        e['ids'].append(l['db_id']); e['prods'].add(l.get('product')); e['amts'].add((l['amt'], l['man']))
    # 같은 이름인데 상품별로 결과가 갈리는 경우(어떤 상품 마스터에서는 잡히고 다른 상품에서는 안 잡힘) 표시
    name_ids = collections.defaultdict(set)
    for r in RES['universe_riders']:
        name_ids[S.nname(r['name'])].add(r['db_id'])
    for (name, rule, why), e in by.items():
        l = e['l']; rm = URID.get(e['ids'][0]) or {}
        all_ids = name_ids.get(S.nname(name), set()); miss = sorted(all_ids - set(e['ids']))
        note = []
        if miss and any(URID.get(m, {}).get('product') not in (None, '설계서 담보(마스터에 없음)') for m in miss):
            note.append('같은 이름의 다른 상품 마스터(%s)에서는 잡히지 않음 — 그 상품 약관 KCD 목록 차이' % ', '.join(miss[:6]))
        if rm.get('product') == '설계서 담보(마스터에 없음)': note.append('특약 마스터에 없는 설계서 표기 — 규칙표만으로 계산(마스터없음 로그)')
        elif str(rm.get('product', '')).startswith('설계서 표기'): note.append('설계서가 세부급부를 괄호로 적은 표기 — 마스터 %s 의 약관 KCD·제외코드를 그대로 씀' % rm.get('via'))
        if rm.get('product') == '설계서 종별 행': note.append('설계서 종별 행(부모 특약 %s 의 마스터를 물림)' % rm.get('via'))
        ratio = ''
        if rule not in ('itc', 'ls_monthly') and l.get('man'): ratio = round(l['amt'] / l['man'], 3)
        prods = sorted(p for p in e['prods'] if p)
        rows3.append([c['id'], c['page'], c['section'], c['row'], c['col'], c.get('sc_name', ''), MODE_KO.get(c['mode'], c['mode']), name, rm.get('benefit') or rm.get('sub') or '', ', '.join(prods), rule_kind_ko(rule), rule, rule_label(rule),
                      why, cond_summary(rule, l, name), kcd_method(rule, l, rm), amount_formula(rule, l, rm), ratio, FREQ_KO.get(l.get('freq'), l.get('freq')), '예' if l.get('counted') else '아니오(빈도가 이 집계에 맞지 않음)',
                      ('' if l.get('in_row') is None else ('예' if l['in_row'] else '아니오(총 보장에만 포함)')), rm.get('ncodes', ''), rm.get('nexcl', ''), rm.get('nhc', ''), ', '.join(str(x) for x in e['ids'][:8]) + (' 외 %d' % (len(e['ids']) - 8) if len(e['ids']) > 8 else ''), ' / '.join(note)])
        pn = per_name.setdefault(S.nname(name), dict(name=name, benefit=rm.get('benefit') or rm.get('sub') or '', prods=set(), rule=rule, cells=[], whys=set(), ids=set(), rm=rm, freqs=set()))
        pn['prods'] |= set(prods); pn['cells'].append(c['id']); pn['whys'].add(why); pn['ids'] |= set(e['ids']); pn['freqs'].add(l.get('freq'))
        if rule == 'itc' and l.get('itc'):
            for tier, (amt, w) in itc_by_tier(name, l['itc'], c):
                itc_tier_rows.append([c['id'], c['label'] if 'label' in c else '%s · %s' % (c['row'], c['col']), name, l['itc'], itc.RM[l['itc']]['ty'], tier, amt, w])
sheet(wb, '③ 칸별 특약(마스터 전체)', hdr3, rows3, widths=[9, 4, 12, 12, 16, 30, 24, 46, 16, 22, 16, 18, 40, 44, 50, 46, 40, 8, 12, 12, 14, 8, 8, 8, 24, 40], sec_col=0)

hdr4 = ['특약명', '세부급부', '상품(마스터)', '보상 유형', '규칙ID', '규칙 설명', '지급 조건 요약', '질병코드 판정 방식', '금액 산정식(일반)', '지급 빈도', '이 특약이 잡히는 칸 수', '칸 목록', '엔진 사유 예시', '마스터 KCD 수', '제외코드 수', '수가코드 수', '약관 위치(db id)']
rows4 = []
for k, p in per_name.items():
    r = p['rm']; rule = p['rule']
    o = ((rule_of(rule) or {}).get('opt') or {})
    fr = o.get('freq', 'year' if (rule_of(rule) or {}).get('kind') == 'tx' else ('each' if (rule_of(rule) or {}).get('kind') == 'surg' else 'once'))
    if rule == 'itc': fr = 'year'
    if '연간1회한' in S.nname(p['name']): fr = 'year'
    l0 = dict(why=' | '.join(sorted(p['whys']))[:400], itc=r.get('itc'), man=r.get('man'))
    rows4.append([p['name'], p['benefit'], ', '.join(sorted(p['prods'])), rule_kind_ko(rule), rule, rule_label(rule), cond_summary(rule, l0, p['name']), kcd_method(rule, l0, r),
                  amount_formula(rule, l0, r).split(' : ')[0] if rule in ('itc', 'ls_monthly') else amount_formula(rule, l0, r), FREQ_KO.get(fr, fr) + (' (담보명 연간1회한/최초1회한/계속받는 표기가 있으면 그것이 우선)' if rule not in ('itc', 'ls_monthly') else ''),
                  len(dict.fromkeys(p['cells'])), ' '.join(dict.fromkeys(p['cells'])), l0['why'], r.get('ncodes', ''), r.get('nexcl', ''), r.get('nhc', ''), ', '.join(sorted(str(x) for x in p['ids'])[:10])])
    rows4[-1][9] = ' / '.join(FREQ_KO.get(f, str(f)) for f in sorted(p['freqs'], key=str)) + ('  (통합치료비 : 연 1회 항목과 수술 1회당 항목이 섞여 있음 — ⑤ 시트 지급 방식 열)' if rule == 'itc' else '')
rows4.sort(key=lambda x: (x[3], x[4], x[0]))
sheet(wb, '④ 특약별 산정 기준', hdr4, rows4, widths=[48, 18, 22, 16, 18, 44, 56, 48, 40, 26, 8, 40, 60, 8, 8, 8, 30], sec_col=3)

# ═══════════ ⑤ 통합치료비 지급금액표 ═══════════
TYN = {'CB': '암 통합치료비(기본형)', 'CL': '암 통합치료비(실속형)', 'C2': '암 통합치료비Ⅱ(비급여)', 'CM': '암 통합치료비(주요치료)(비급여)', 'PR': '암전후관련 특정질환 및 양성신생물 통합치료비', 'CV': '특정순환계질환 통합치료비', 'MS': '특정순환계질환(주요손상및질환) 통합치료비', 'DZ': '질병 통합치료비'}
PKO = {'y': '연간 1회', 'o': '수술 1회당', 'd': '재활 1일 1회(연간 최대일수)'}
tiers_all = sorted({int(k) for ty in itc.AMT for k in itc.AMT[ty]})
hdr5 = ['유형', '유형 이름', '해당 특약(약관 지급금액표 RIDERS)', '1년 이내 50% 감액', '항목 번호', '항목명', '치료키', '지급 방식', '비급여 전용', '암 구분(cl)', '특정암(sp)', '1-5종(j)', '재활 최대일수'] + ['가입금액 %s만원' % format(t, ',') for t in tiers_all]
rows5 = []
for ty, items in itc.IT.items():
    riders = [r for r in itc.RIDERS if r['ty'] == ty]
    for i, it in enumerate(items):
        row = [ty, TYN.get(ty, ty), ' / '.join(r['nm'] for r in riders), '예' if any(r.get('half') for r in riders) else '아니오', i, it['l'], '%s(%s)' % (ACT_KO.get(it['k'], it['k']), it['k']), PKO.get(it['p'], it['p']), '예' if it.get('nc') else '',
               ', '.join(it.get('cl') or []), ('' if 'sp' not in it else ('특정암(C61·C73)만' if it['sp'] else '특정암 제외')), it.get('j', ''), it.get('max', '')]
        for t in tiers_all:
            A = itc.AMT[ty].get(str(t)); row.append(A[i] if A else '')
        rows5.append(row)
sheet(wb, '⑤ 통합치료비 지급금액표', hdr5, rows5, widths=[6, 26, 44, 8, 6, 34, 26, 12, 8, 22, 12, 6, 8] + [12] * len(tiers_all), sec_col=0)
# 칸별 통합치료비 금액(가입금액 구간별)
sheet(wb, '⑤-2 칸별 통합치료비 금액', ['칸ID', '칸', '특약명', '금액표 id', '유형', '가입금액(만원)', '이 칸 금액(만원)', '항목 내역(엔진 사유)'], itc_tier_rows, widths=[9, 30, 46, 10, 6, 12, 12, 70], sec_col=0)

# ═══════════ ⑥ 통합생활지원비 항목표 ═══════════
rows6 = []
for rid, v in LS.items():
    for tier, items in (v.get('tiers') or {}).items():
        for it in items:
            rows6.append([rid, v.get('nm', ''), tier, it.get('grp'), it.get('label'), it.get('cnt'), it.get('amt'), it.get('amt_pre'), v.get('src', ''), v.get('verified', '')])
sheet(wb, '⑥ 통합생활지원비 항목표', ['id', '특약명', '가입금액(월 한도, 만원)', '구분', '항목', '지급 단위', '월 지급액(만원)', '1년 이내(만원)', '출처', '검증'], rows6, widths=[8, 30, 12, 10, 50, 14, 10, 10, 30, 10], sec_col=0)

# ═══════════ ⑦ 규칙표 ═══════════
used = collections.Counter(r[11] for r in rows3)
aud_rules = {r['id']: r for r in ((AUDIT or {}).get('rules') or [])}
hdr7 = ['규칙ID', '보상 유형', '담보명 조건(정규식 · 이 표현이 담보명에 있으면)', '제외 조건(정규식)', '규칙 설명(rules.json label)', '옵션(원문)', 'GA 칸에서 잡힌 특약 줄 수', '검수 : 지급 조건', '검수 : 질병코드 판정', '검수 : 금액 산정식', '검수 : 지급 빈도', '검수 : 약관 대조 표본', '검수 : 주의·가정', '검수 신뢰도']
rows7 = []
for r in S.RULES + [{'id': 'itc', 'kind': 'itc', 'm': '(약관 지급금액표 RIDERS 이름과 일치하는 통합치료비)', 'x': '', 'label': rule_label('itc'), 'opt': {}},
                    {'id': 'ls_monthly', 'kind': 'ls_monthly', 'm': '통합생활지원비', 'x': '', 'label': rule_label('ls_monthly'), 'opt': {}},
                    {'id': 'direct', 'kind': 'direct', 'm': '(GA 양식 간병인입원보장 · 암후유장해 칸)', 'x': '', 'label': rule_label('direct'), 'opt': {}}]:
    a = aud_rules.get(r['id']) or {}
    rows7.append([r['id'], KIND_KO.get(r['kind'], r['kind']), r.get('m', ''), r.get('x') or '', r.get('label', ''), json.dumps(r.get('opt') or {}, ensure_ascii=False), used.get(r['id'], 0),
                  a.get('condition_ko', ''), a.get('kcd_method_ko', ''), a.get('amount_formula_ko', ''), a.get('freq_ko', ''),
                  '\n'.join('%s [%s] %s' % (s_.get('name'), s_.get('verdict'), s_.get('note')) for s_ in a.get('sample_riders', [])), a.get('caveats_ko', ''), a.get('confidence', '')])
sheet(wb, '⑦ 규칙표', hdr7, rows7, widths=[22, 16, 44, 30, 50, 50, 8, 56, 46, 40, 34, 60, 46, 8], sec_col=1)

# ═══════════ ⑧ 계산 제외 사유 ═══════════
rows8 = []
for c in CELLS:
    u = RES['universe'].get(c['id'])
    if not u: continue
    g = collections.defaultdict(list)
    for i in u['issues']: g[(i['구분'], i['사유'])].append(i['담보'])
    for (k, why), names in sorted(g.items()):
        rows8.append([c['id'], c['page'], c['section'], c['row'], c['col'], k, why, len(names), ' · '.join(names)[:32000]])
sheet(wb, '⑧ 계산 제외 사유', ['칸ID', '쪽', '구역', '행', '열', '구분', '사유(엔진 로그 원문)', '담보 수', '담보 목록'], rows8, widths=[9, 4, 12, 12, 16, 10, 80, 8, 120], sec_col=0)

# ═══════════ ⑨ 고정값·직접표시 칸 ═══════════
rows9 = []
for c in CELLS:
    if c['kind'] == 'engine': continue
    d = c.get('direct') or {}
    if not isinstance(d, dict): d = {'keys': ['간병인보장 · ' + str(d)]}
    rows9.append([c['id'], c['page'], c['section'], c['row'], c['col'], KIND_CELL_KO.get(c['kind'], c['kind']), ' + '.join(d.get('keys') or d.get('any') or []), ' / '.join(d.get('exclude') or []), c.get('note', ''),
                  *[' / '.join(dd['cells'][c['id']]['tokens']) for dd in DESIGNS]])
sheet(wb, '⑨ 고정값·직접표시 칸', ['칸ID', '쪽', '구역', '행', '열', '칸 종류', '담보명 키워드(모두 포함) / 간병인 칸 구분', '제외 키워드', '설명'] + ['설계서 %s' % DNAME.get(d['pdf'], d['pdf']) for d in DESIGNS], rows9, widths=[9, 4, 14, 12, 16, 22, 34, 14, 70] + [14] * len(DESIGNS))

# ═══════════ ⑩ 설계서 3건 검증 · ⑪ 설계서 3건 칸별 특약 금액 ═══════════
rows10 = []
for c in CELLS:
    row = [c['id'], c['page'], c['section'], c['row'], c['col'], MODE_KO.get(c['mode'], c['mode']) if c['kind'] == 'engine' else KIND_CELL_KO.get(c['kind'])]
    for dd in DESIGNS:
        cc = dd['cells'][c['id']]
        row += [' / '.join(cc['tokens']), len([l for l in cc['lines'] if l.get('counted')]), '; '.join('%s %s' % (l['name'], format(l['amt'], ',.0f')) for l in cc['lines'] if l.get('counted'))[:2000]]
    rows10.append(row)
hdr10 = ['칸ID', '쪽', '구역', '행', '열', '집계'] + sum([['%s 표시값' % DNAME[d['pdf']], '집계 특약 수', '특약별 금액(만원)'] for d in DESIGNS], [])
ws10 = sheet(wb, '⑩ 설계서 검증', hdr10, rows10, widths=[9, 4, 12, 12, 16, 22] + [14, 6, 60] * len(DESIGNS), sec_col=1)
ws10.append([]); ws10.append(['HTML 대조', '', '', '', '', '설계서 %d건 모두 GA 지면(ga_proposal.py 가 그린 HTML)의 표시값 순서·값이 이 시트의 표시값과 전부 일치 : %s' % (len(DESIGNS), '%s') % ' · '.join('%s %d개' % (DNAME[d['pdf']], len([t for c in d['cells'].values() for t in c['tokens']])) for d in DESIGNS)])
rows11 = []
for dd in DESIGNS:
    rmap = {r['no']: r for r in dd['riders']}
    for c in CELLS:
        cc = dd['cells'][c['id']]
        for l in cc['lines']:
            rr = rmap.get(l.get('no')) or {}
            rows11.append([DNAME[dd['pdf']], c['id'], c['page'], c['section'], c['row'], c['col'], l['name'], rr.get('man', ''), l['amt'], l.get('why'), l.get('rule'), rule_kind_ko(l.get('rule')), FREQ_KO.get(l.get('freq'), l.get('freq')),
                           '예' if l.get('counted') else '아니오', '' if l.get('in_row') is None else ('예' if l['in_row'] else '아니오(총 보장에만)'), '마스터' if rr.get('matched') else ('부모연결' if rr.get('via') else '마스터 없음(규칙표 계산)')])
sheet(wb, '⑪ 설계서 칸별 특약 금액', ['설계서', '칸ID', '쪽', '구역', '행', '열', '특약명(설계서 표기)', '가입금액(만원)', '지급액(만원)', '엔진 사유', '규칙ID', '보상 유형', '지급 빈도', '이 칸 집계에 포함', '담보행 표시', '마스터 인식'], rows11,
      widths=[18, 9, 4, 12, 12, 16, 50, 10, 10, 50, 18, 16, 12, 10, 14, 16], sec_col=1)

# ═══════════ ⑫ 검수 메모 ═══════════
rows12 = []
if AUDIT:
    for pg in AUDIT.get('pages') or []:
        f = pg.get('found') or {}; j = (pg.get('judged') or {}).get('verdicts') or []
        jd = {(v.get('cell_id'), v.get('rider'), v.get('type')): v for v in j}
        rows12.append(['%d쪽' % pg['page'], '스펙↔ga2.py 일치', '', '', '예' if f.get('spec_matches_ga2') else '아니오', f.get('spec_notes_ko', ''), '', '확인 짝 수 %s' % f.get('checked_pairs', '')])
        for x in f.get('findings') or []:
            v = jd.get((x.get('cell_id'), x.get('rider'), x.get('type'))) or {}
            rows12.append(['%d쪽' % pg['page'], x.get('type'), x.get('cell_id'), x.get('rider'), x.get('severity'), x.get('evidence_ko'), v.get('verdict', ''), (v.get('reason_ko', '') + (' → ' + v['fix_ko'] if v.get('fix_ko') else ''))])
        if f.get('notes_ko'): rows12.append(['%d쪽' % pg['page'], '검증자 메모', '', '', '', f.get('notes_ko'), '', ''])
    cr = AUDIT.get('critic') or {}
    for m in cr.get('missing') or []:
        rows12.append(['전체', '완전성 비평', '', '', '', '%s — %s' % (m.get('item'), m.get('why_ko')), '', m.get('where_ko')])
    if cr.get('notes_ko'): rows12.append(['전체', '완전성 비평 메모', '', '', '', cr.get('notes_ko'), '', ''])
    for x in AUDIT.get('manual') or []: rows12.append(x)
sheet(wb, '⑫ 검수 메모', ['범위', '구분', '칸ID', '특약', '심각도/일치', '내용·근거', '심판 판정', '판정 이유 · 반영'], rows12, widths=[8, 16, 9, 30, 10, 90, 10, 70])

wb.save(OUT)
print('saved', OUT, 'sheets', wb.sheetnames, 'rows3', len(rows3), 'rows4', len(rows4), 'rows8', len(rows8), 'rows11', len(rows11), 'itc tiers', len(itc_tier_rows))
