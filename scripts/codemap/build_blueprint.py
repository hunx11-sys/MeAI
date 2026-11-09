# -*- coding: utf-8 -*-
"""스마트 제안서(GA 디자인판) 설계도 — 정보계 담보코드 기준 (IT개발파트 전달용)

사내 전산은 가입설계의 담보를 「단위상품코드 + 담보코드」로 가리킨다. 이 설계도는 기존 GA 설계도
(dist/ga-blueprint-final.xlsx · 담보명 기준)를 담보코드 기준으로 다시 짠 것이다.

입력
  <작업폴더>      rows.json · name_res.pkl (extract_rows.py · run2.py)
  <매핑 엑셀>     build.py 결과(담보코드 분류 · 사유 · 단위상품코드 추정)
  <GA 결과 json>  proposal_smart/ga_docs/run_spec.py 결과(칸 정의 · 마스터 전체 칸별 지급 줄 · 설계서 칸 값)
출력
  <설계도 엑셀>   정보계 코드가 들어 있어 사내 자료 — 저장소에 넣지 않는다

사용 : python3 build_blueprint.py <작업폴더> <매핑 엑셀> <GA 결과 json> <설계도 엑셀>
"""
import sys, os, re, json, pickle, collections
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'proposal_smart'))
from match import M, REC
from norm import key as nkey, strip_tags
import scen_engine as S

WORK, MAPX, RESJ, OUT = sys.argv[1:5]
rows = json.load(open(os.path.join(WORK, 'rows.json'), encoding='utf-8'))
NR = pickle.load(open(os.path.join(WORK, 'name_res.pkl'), 'rb'))
RES = json.load(open(RESJ, encoding='utf-8'))
GA = openpyxl.load_workbook(os.path.join(ROOT, 'dist', 'ga-blueprint-final.xlsx'), read_only=True)
MW = openpyxl.load_workbook(MAPX, read_only=True)
MAPPED = ('정확', '세부표기', '특약단위')
nz = lambda s: re.sub(r'\s+', '', s or '')

# ── 매핑 엑셀에서 코드 분류 ──────────────────────────────────
def sheet_rows(ws):
    it = ws.iter_rows(values_only=True); h = next(it)
    return [dict(zip(h, r)) for r in it]
CM = {r['담보코드']: r for r in sheet_rows(MW['담보코드 매핑'])}
UNITS = sheet_rows(MW['단위상품코드 추정'])

# ── 같은 알맹이 묶음(build.py 와 같은 규칙) ───────────────────
_CAN = {}
def canon(r):
    k = (r['p'], r['id'])
    if k in _CAN: return _CAN[k]
    par = REC.get((r['p'], r.get('parent'))) if r.get('parent') else None
    if par:
        P = set(par['_t']); sub = set()
        for t in r['_t']:
            if t in P: continue
            for sx in ('진단비', '치료비', '수술비', '입원일당'):
                if par['_k'].endswith(sx) and t.endswith(sx): t = t[:-len(sx)]; break
            if t and t not in P and t not in ('연간1회한', '최초1회한'): sub.add(t)   # 세부보장 이름 끝의 지급 횟수 메모는 알맹이가 아니다(특정순환계질환 통합치료 생활비[…2회이상] = […2회이상)(연간1회한)] · v8.90)
        v = canon(par) + '|' + '+'.join(sorted(sub))
    else:
        v = '+'.join(sorted(set(r['_t'])))
    _CAN[k] = v; return v
GK = collections.defaultdict(list)
for r in M: GK[canon(r)].append(r)
ID = {r['id']: r for r in M}
PRODS = ['통합간편', '케어프리', '운전자', '치아', '또또암', '또또암간편', '간편31', '내Mom대로', '내Mom같은어린이',
         'The건강한내Mom대로5.10.5', 'The건강한5.10.5', 'The좋은내Mom대로', 'The가벼운간편355', 'The좋은케어프리']
PO = {p: i for i, p in enumerate(PRODS)}

# ── 규칙 · 보상 유형 · 금액식 ────────────────────────────────
KIND_KO = {'dx': '진단비', 'surg': '수술비', 'tx': '치료비', 'day': '입원·통원일당', 'point2': '포인트적립형 치료비', 'skip': '계산 제외(조건부·제도성)',
           'care': '간병(사례 계산 대상 아님)', 'life': '사망·후유장해(사례 계산 대상 아님)', 'nonmed': '비의료(운전자·재물 등 · 사례 계산 대상 아님)',
           'itc_unknown': '통합치료비(금액표 없음)'}
VAR = re.compile(r'\[(특별조건부|계약전환용|기본계약)\]|\(출생전\)|\(\d+년갱신\)')
def ename(n):
    """엔진에 넘길 이름 — 정보계 변형 표시([특별조건부] · [계약전환용] · (출생전) · (N년갱신))와 고지 구분자를 뗀다.
       보장 알맹이는 같고(시트 9 ④) 조건 토큰(원인 · 병원 · 종 · 일수)은 그대로 남는다"""
    return re.sub(S.GOJI, '', VAR.sub('', n or '')).strip()
F4 = {}
for r in list(GA['설계도4 보상유형별 공식'].iter_rows(values_only=True))[4:]:
    if r[0]:
        m = re.search(r'\b(dx|surg|day|tx|point2|skip)\b', r[0]); F4[m.group(1) if m else r[0]] = (r[1], r[2], r[3])
K6 = {r[0]: r[1] for r in list(GA['설계도6 질병코드 판정 방식'].iter_rows(values_only=True))[4:] if r[0]}
R4 = {}
for r in list(GA['④ 특약별 산정 기준'].iter_rows(values_only=True))[1:]:
    if r[0]: R4.setdefault(nz(r[0]), r)
RL = {r[0]: r for r in list(GA['⑦ 규칙표'].iter_rows(values_only=True))[1:] if r[0]}

def rule_info(name):
    """특약명 → (규칙ID, 보상 유형, 규칙 설명, 금액 산정식, 지급 빈도, 질병코드 판정 방식, 계산 여부)"""
    iid, lsid = S.itc_id(name), S.ls_id(name)
    if iid: return ('itc', '통합치료비(약관 지급금액표)', '약관 지급금액표(product_data.json · 금액표 id %s)' % iid, F4.get('⑥ 통합치료비(약관 지급금액표 · engine.calc_rider)', ('Σ 항목 금액(가입금액 구간별 정액표)',))[0] if False else 'Σ 항목 금액(가입금액 구간별 정액표) — 연간 총액은 가입금액 한도', '연 1회 / 1회당(항목별)', '금액표 항목의 암 구분 · 질병군', 'GA 계산 대상')
    if lsid: return ('ls_monthly', '통합생활지원비(약관 월 항목표)', '약관 월 항목표(life_support.json · id %s)' % lsid, 'Σ 항목 월 지급액 — 합계는 가입금액(월 한도)까지', '연 1회', '항목별 산정특례 · 주요치료', 'GA 계산 대상')
    r = S.classify(name)
    if not r: return ('', '규칙 없음', '규칙표에 없음', '-', '-', '-', '계산 제외(규칙 없음 · 빈칸 + 로그)')
    o = r.get('opt') or {}; k = r['kind']
    if k == 'itc_unknown':
        nm = S.nname(name)
        if nm in S.INJ_KNOWN or S.noren(nm) in S.INJ_KNOWN:
            return ('inj_itc', '상해 통합치료비(약관 지급금액표)', '상해 통합치료비 금액표(inj_itc.json) — 스마트 제안서 지면에서 따로 계산 · GA 칸 없음', 'Σ 항목 금액(가입금액 구간별 정액표)', '항목별', '원인 상해', '사례 계산 대상 아님(상해 통합치료비 · 지면 별도)')
        return ('itc_unknown', '통합치료비(금액표 없음)', '약관 지급금액표(product_data.json)에 없는 통합치료비', '-', '-', '-', '계산 제외(금액표 없음 · 빈칸 + 로그)')
    kko = KIND_KO.get(k, k)
    four = R4.get(nz(name))
    if o.get('parts'):
        fml = ' · '.join('%s 가입금액의 %s%%' % (p['label'], format(p['rate'], 'g')) for p in o['parts']) + ' (구분별 · 각각 연간 1회)'
    elif four: fml = four[8]
    else: fml = (F4.get(k) or ('-',))[0]
    if four: freq = four[9]
    else:
        freq = {'once': '최초 1회', 'year': '연 1회', 'each': '받을 때마다'}.get(o.get('freq'), (F4.get(k) or ('', '', '-'))[2])
        if re.search(r'연간\d*회한|계속받는', nz(name)): freq = '연 1회(담보명)'
        elif '최초1회한' in nz(name): freq = '최초 1회(담보명)'
    kc = o.get('kcd'); kcd = ('%s — %s' % (kc, K6.get(kc, ''))) if kc else '질병코드 조건 없음(담보명 조건 · 치료행위 · 수술 종으로 판정)'
    if k in ('dx', 'surg', 'tx', 'day', 'point2'): calc = 'GA 계산 대상'
    elif k == 'skip': calc = '계산 제외(조건부 · 제도성 · 빈칸 + 로그)'
    else: calc = '사례 계산 대상 아님(%s)' % kko
    return (r['id'], kko, r.get('label', ''), fml, freq, kcd, calc)

RULE_CACHE = {}
def rinfo(name):
    name = ename(name)
    if name not in RULE_CACHE: RULE_CACHE[name] = rule_info(name)
    return RULE_CACHE[name]
RAW_MISS = collections.Counter()     # 변형 표시를 떼지 않으면 지금 엔진이 통합치료비 금액표를 못 찾는 짝(시트 9 ⑨)
for u, c, n in rows:
    if NR[n][0] in MAPPED and S.itc_id(ename(n)) and not S.itc_id(n): RAW_MISS[n] += 1

# ── 코드 → 알맹이 묶음 · GA 칸 ───────────────────────────────
names = collections.defaultdict(collections.Counter); units = collections.defaultdict(set)
for u, c, n in rows: names[c][n] += 1; units[c].add(u)
codes = sorted(names)
CODE_G = collections.defaultdict(list)      # 코드 → [(canon, 정보계 이름, 단계)]
for c in codes:
    for n in names[c]:
        lv, oid, op = NR[n][:3]
        if lv in MAPPED:
            k3 = canon(REC[(op, oid)])
            if k3 not in [x[0] for x in CODE_G[c]]: CODE_G[c].append((k3, n, lv))
G2CODES = collections.defaultdict(set)
for c, gs in CODE_G.items():
    for k3, _, _ in gs: G2CODES[k3].add(c)

# GA 마스터 전체 칸별 지급 줄(db_id) → 담보코드
ROWPAT = {}
for c in codes:
    for n in names[c]:
        s = nz(strip_tags(n))
        m = re.search(r'수술비\(1-7종[^\[]*\[(질병|상해)(\d)종\]', s) or re.fullmatch(r'(?:\[[^\]]*\])*(?:갱신형)?수술비\[(질병|상해)([1-7])종\](?:\(출생전\))?', s)
        if m: ROWPAT.setdefault('row-%s%s' % m.groups(), set()).add(c)
        m = re.search(r'수술비Ⅱ\(1-5종\)(?!\(체증형\))[^\[]*\[(질병|상해)(\d)종\]', s)
        if m: ROWPAT.setdefault('row15-%s%s' % m.groups(), set()).add(c)
        m = re.search(r'^(질병|상해)1-5종수술비\(plus\)\(연간2회이상\)\((\d)종,연간1회한\)', s)
        if m: ROWPAT.setdefault('rowplus-%s%s' % m.groups(), set()).add(c)
def codes_of_dbid(d):
    if d in ROWPAT: return ROWPAT[d]
    r = ID.get(d)
    return G2CODES.get(canon(r), set()) if r else set()
CELL_CODES = collections.defaultdict(set); CODE_CELLS = collections.defaultdict(set)
for cid, v in RES['universe'].items():
    for l in v['lines']:
        for c in codes_of_dbid(l['db_id']): CELL_CODES[cid].add(c); CODE_CELLS[c].add(cid)
CELLDEF = {c['id']: c for c in RES['cells']}

# ── 엑셀 ────────────────────────────────────────────────────
F = '맑은 고딕'
HF = Font(name=F, bold=True, color='FFFFFF', size=10); BF = Font(name=F, size=10); TF = Font(name=F, bold=True, size=14); B11 = Font(name=F, bold=True, size=11)
HFILL = PatternFill('solid', fgColor='3A3A3A'); thin = Side(style='thin', color='D0D0D0'); BRD = Border(top=thin, bottom=thin, left=thin, right=thin)
WRAP = Alignment(wrap_text=True, vertical='top'); TOP = Alignment(vertical='top')
CALCF = {'GA 계산 대상': 'E2F0D9', '계산 제외': 'EDEDED', '사례 계산': 'FFF2CC'}
wb = openpyxl.Workbook()

def sheet(title, head, data, widths, wrapcols=(), fillcol=None):
    ws = wb.create_sheet(title); ws.append(head)
    for i in range(1, len(head) + 1):
        cl = ws.cell(1, i); cl.font = HF; cl.fill = HFILL; cl.alignment = Alignment(wrap_text=True, vertical='center'); cl.border = BRD
    for row in data: ws.append(row)
    for r in ws.iter_rows(min_row=2):
        for cl in r:
            cl.font = BF; cl.border = BRD; cl.alignment = WRAP if cl.column in wrapcols else TOP
    if fillcol:
        for rr in range(2, ws.max_row + 1):
            v = str(ws.cell(rr, fillcol).value or '')
            for k, fc in CALCF.items():
                if v.startswith(k): ws.cell(rr, fillcol).fill = PatternFill('solid', fgColor=fc)
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions; ws.row_dimensions[1].height = 34
    return ws

def text_sheet(title, head, data, widths):
    ws = wb.create_sheet(title); ws.append(head)
    for i in range(1, len(head) + 1):
        cl = ws.cell(1, i); cl.font = HF; cl.fill = HFILL; cl.alignment = Alignment(wrap_text=True, vertical='center')
    for row in data: ws.append(row)
    for r in ws.iter_rows(min_row=2):
        for cl in r: cl.font = BF; cl.alignment = WRAP; cl.border = BRD
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'A2'
    return ws

# 2. 전체 흐름
FLOW = [
 ['0', '가입설계 데이터(전산)', '설계 한 건의 담보 목록을 받는다 — 담보마다 단위상품코드 · 담보코드 · 상품담보명(정보계 원문) · 가입금액. 표지용 계약 정보(상품명 · 피보험자 성별 · 나이 · 월 보험료)', '담보 목록', '3. 입력 데이터 사양', '(지금은 설계서 PDF 를 읽는다 : matcher.read_proposal · build_all)'],
 ['1', '단위상품코드', '스마트 제안서 대상 상품인지 본다. 대상 아님 : 치매간병통합케어 · 프리미엄 건강 · 간편보험(10년 뒤 2배 체증형) · 펫 · 실손 · 화재 등 → 지면을 만들지 않는다', '대상 여부', '8. 단위상품코드 → 상품', 'rules.json exclude_products'],
 ['2', '단위상품코드 + 담보코드', '담보 식별표에서 특약 마스터 ID 를 찾는다. 못 찾으면 그 담보는 계산 제외 + 로그(빈칸 원칙 · 틀린 금액 대신 빈칸)', '담보마다 특약 마스터 ID', '4. 담보 식별표', '(이번 매핑 · scripts/codemap)'],
 ['3', '특약 마스터 ID', '마스터에서 약관 질병코드(KCD) · 제외코드 · 수가코드 · 세부보장을 붙인다. 질병코드는 약관 별표에서만 온다(코드에서 만들지 않음)', '담보마다 약관 코드', '5. 담보코드별 계산 사양', 'proposal_smart/db.json · db_terms_extra.json'],
 ['4', '상품담보명(정보계)', '규칙표를 위에서부터 대조해 처음 걸리는 규칙 하나 = 보상 유형 · 질병코드 판정 방식 · 지급 빈도. 담보명에서 조건을 읽는다(원인 질병/상해 · 병원 종별 · N일한도 · N종 · 연간1회한 등). 고지 구분자 (…가입) · (N년갱신) · [기본계약] · 변형 표시([특별조건부] · [계약전환용] · (출생전)) · 띄어쓰기는 떼고 읽는다(시트 9 ⑥ ⑨)', '담보마다 규칙 · 조건 토큰', '5 · GA 설계도 ⑦ 규칙표 · 설계도5', 'scen_engine.classify · tokens · itc_id · ls_id'],
 ['5', 'GA 칸 사례 132개', '칸마다 정해진 사례(질병코드 · 치료 단계 · 병원)에 담보를 하나씩 넣어 지급 줄(금액 · 사유 · 빈도)을 만든다', '칸마다 지급 줄', '6. GA 칸 × 담보코드 · GA 설계도 ② 칸 목록 · 설계도9', 'scen_engine.pay_lines · engine(통합치료비 금액표)'],
 ['6', '지급 줄', '칸 집계 방식(최초 · 반복 · 매 회 등)으로 칸 값을 만든다. 담보가 없으면 「미가입」, 계산 제외는 빈칸', '칸 값', 'GA 설계도 설계도10', 'ga_spec.cell_value'],
 ['7', '칸 값', '지면(표지 · 1 보장요약 · 2 암보장 · 3 뇌·심보장 · 보장금액 세부내역)에 값을 얹는다. 세부내역 = 칸 값의 합산 계산서(구분 · 보장금액 · 특약명 · 가입금액 · 특약별 보장금액)', 'GA 양식 PDF', 'GA 설계도 캡처 시트', 'ga_proposal · ga_overlay'],
]
# 3. 입력 데이터 사양
SPEC = [
 ['단위상품코드', '필수', '정보계 단위상품코드(예 : 영문·숫자 5자리)', '대상 상품 확인 · 담보 식별(담보코드와 짝)', '같은 담보코드라도 단위상품코드에 따라 우리 특약이 다를 수 있다(시트 9 ①)'],
 ['담보코드', '필수', '정보계 담보코드(숫자 6자리)', '담보 식별', ''],
 ['상품담보명', '필수', '정보계 원문 그대로(고지 구분자 · [기본계약] · (N년갱신) 포함해도 된다)', '조건 토큰 읽기(원인 · 병원 종별 · 일수 한도 · 종 · 연간1회한) · 세부내역 「특약명」 표시', '엔진이 담보명에서 조건을 읽으므로 이름을 줄이거나 바꾸지 않는다'],
 ['가입금액', '필수', '원 단위(엔진은 만원으로 바꿔 쓴다)', '금액 계산 · 세부내역 「가입금액」', '통합치료비 · 생활지원비는 가입금액 구간별 금액표를 쓴다'],
 ['세부보장 행', '있으면', '설계에 「세부보장 참조」 행이 있으면 세부보장 담보코드 행을 함께 넘긴다', '세부보장별 계산(예 : 수술비(1-7종)의 질병1종~7종)', '정보계는 세부보장(종별 · 암종별)마다 코드가 따로 있다'],
 ['동일금액 다발 특약', '필수', '암종별(30종)통합암진단비(또또암 · 또또암간편) · 통합암진단비 · 26종 항암방사선및약물치료비는 세부보장 행마다 같은 가입금액으로 넘긴다(설계서와 같은 모양)', '그 암의 세부보장 하나만 지급 → 암 진단(치료) 1회 = 가입금액', '세부보장이 모두 같은 금액으로만 설계된다(예 : 3,000만원 → 30종 모두 3,000만원 · 소유자 2026-11-06). 부모 행만 금액을 넘기면 지금 엔진은 계산하지 않는다(빈칸)'],
 ['상품명 · 피보험자 성별 · 나이 · 월 보험료', '표지', '표지 표시용', '표지(2판)', 'GA 설계도 설계도1 1단계와 같다'],
]
# 9. 예외 처리 · IT 확인
EXC = [
 ['① 코드 하나에 특약 여럿', '정보계는 담보 개념마다 코드를 주고 상품마다 다른 이름을 붙인다. 예 : 한 코드가 케어프리 「뇌졸중진단비」 · 통합간편 「뇌졸중진단비Ⅱ」', '반드시 「단위상품코드 + 담보코드」 짝으로 찾는다(시트 4). 담보코드만으로 찾지 않는다', '%d개 코드' % sum(1 for c in codes if len(CODE_G.get(c, [])) >= 2)],
 ['② 이름 하나에 코드 여럿', '같은 상품담보명이 단위상품코드에 따라 다른 코드로 들어 있다', '짝으로 찾으면 문제없다', '매핑 엑셀 「이름 하나에 코드 여러 개」'],
 ['③ 세부보장 단위 코드', '정보계는 수술비 종별 · 암종별 등 세부보장마다 코드를 따로 둔다. 우리 마스터는 특약 하나 + 세부보장', '판정 단계 「특약단위」 코드는 상품담보명의 세부 표기([질병3종] 등)로 종을 읽는다 — 이름을 그대로 넘긴다', '%d개 코드' % sum(1 for c in codes if CM[c]['판정 단계'] == '③ 특약단위')],
 ['④ 변형 표시', '[특별조건부] · [계약전환용] · (출생전) · 전환용 · 「추가」 는 정보계 코드가 따로 있지만 보장 알맹이가 같다', '같은 특약 마스터 ID 로 계산한다', '시트 5 「변형 표시」'],
 ['⑤ 체증형', '스마트 제안서 · 보상시뮬레이터는 첫 보상을 예시로 보여 준다(소유자 2026-11-06)', '체증형은 같은 특약으로 계산(첫 보상 기준). 10년 뒤 2배 체증형(프리미엄 건강 · 간편보험)은 대상 아님', '분류 안 됨 50개'],
 ['⑥ 고지 구분자 · 띄어쓰기', '(맞춤간편가입) · (편한가입) 등은 고지유형 표시, [기본계약] · (N년갱신) · 앞의 갱신형 · 띄어쓰기는 이름 비교에서 뺀다. 영문 II 는 Ⅱ 로 읽는다', '엔진이 알아서 무시한다 — 정보계 원문을 그대로 넘기면 된다', ''],
 ['⑦ 매핑이 안 되는 코드', '우리 약관(14개 상품)에 없는 담보 · 대상 아닌 상품 · 제도성 특약', '계산 제외 + 로그. 지면에는 빈칸(틀린 금액이 아니라 빈칸)', '시트 7'],
 ['⑨ 인수 · 전환 표시', '[특별조건부](할증보험료법 특별약관 · 보험료만 할증) · [계약전환용] · (출생전) 은 보장이 같은 같은 특약이다(소유자 2026-11-09)', '엔진이 표시를 떼고 읽는다(v8.89 · scen_engine.VARTAG) — 정보계 원문을 그대로 넘기면 된다. 세부보장을 둥근 괄호로 적은 담보(통합항암방사선약물치료비 · 표적항암약물허가치료비Ⅲ · 통합전이암진단비)도 v8.89 부터 마스터 세부보장 이름으로 규칙을 판정한다', '금액표 못 찾는 짝 %d(v8.89 전 189)' % sum(RAW_MISS.values())],
 ['⑩ 동일금액 다발 특약', '암종별(30종)통합암진단비 · 통합암진단비 · 26종 항암방사선및약물치료비는 세부보장(암종별 · 약물/방사선별)이 모두 같은 금액으로만 설계된다(소유자 2026-11-06). 정보계도 세부보장마다 코드가 있다', '세부보장 행으로 받으면 그 암의 세부보장 하나만 계산된다 → 암 진단(치료) 1회 = 가입금액(정보계 이름으로 검증 : 30종 16개 · 통합암진단비 73개 · 26종 37개 특약 모두 한 암에 1회). 부모 행이 함께 와도 부모는 계산하지 않아 두 번 잡히지 않는다. 부모 행만 금액이 오면 빈칸 → 세부보장 행으로 넘기거나, 엔진이 부모 금액을 세부보장 전부에 펼쳐 계산하도록 보완', '3종'],
 ['⑧ 질병코드 · 금액은 만들지 않는다', '질병코드(KCD)는 약관 별표와 특약 마스터에서만, 금액은 약관 지급금액표에서만', '목록이 없으면 지급하지 않고 사유를 로그에 남긴다', 'CLAUDE.md 절대 지키는 것 1 · 2'],
 ['IT 확인 1', '단위상품코드 → 상품 대응표', '우리는 담보 구성 · 고지 구분자로 추정했다(시트 8). 시트 4 의 특약 마스터 ID 도 이 추정 상품의 같은 알맹이 특약으로 골랐다(질병코드 · 금액표는 알맹이가 같으면 같다). 정보계 공식 대응표를 받으면 바꾼다', '203개'],
 ['IT 확인 2', '담보코드 앞 세 자리의 뜻', '이름 분포로 본 추정(610 상해 · 630~635 질병 · 암 · 뇌심 · 650 화재 · 690 제도성 등)', ''],
 ['IT 확인 3', '정보계 상품담보명이 바뀔 때 알려 주는 절차', '엔진이 이름에서 조건을 읽으므로 이름이 바뀌면 다시 맞춰야 한다(scripts/codemap 을 다시 돌림)', ''],
 ['IT 확인 4', '확인 필요 코드', '이름이 비슷하지만 우리 특약과 같은지 사람이 정해야 하는 코드', '%d개 · 매핑 엑셀' % sum(1 for c in codes if CM[c]['분류'] == '확인 필요')],
]

# 4. 담보 식별표 — 같은 알맹이 묶음 안에서 단위상품코드의 (추정) 상품 레코드를 고른다
UP = {}
for x in UNITS:
    m = re.fullmatch(r'(\S+)\(추정\)', x['추정 상품'] or '')
    if m and m.group(1) in PO: UP[x['단위상품코드']] = m.group(1)
D4 = []; PICK = collections.Counter()
for u, c, n in rows:
    lv, oid, op = NR[n][:3]
    if lv in MAPPED:
        r = REC[(op, oid)]; ri = rinfo(n); up = UP.get(u)
        same = sorted((x for x in GK[canon(r)] if x['p'] == up), key=lambda x: (('갱신형' in nz(x['n'])) != ('갱신형' in nz(n)), nz(x['n']) != nz(r['n']), len(x['n']), x['id'])) if up else []   # 갱신형 여부 같은 것 → 이름 같은 것 → 짧은 이름(태아고급형 등 변형보다 기본)
        if same: r = same[0]; why = '단위상품 추정 상품의 같은 알맹이 특약'
        elif up: why = '추정 상품(%s)에 같은 알맹이 없음 — 이름이 맞은 다른 상품 특약' % up
        else: why = '단위상품 추정 상품 없음 — 이름이 맞은 특약'
        PICK[why[:12]] += 1
        D4.append([u, c, n, UP.get(u, ''), lv, r['id'], r['p'], r['n'], why, CM[c]['변형 표시(이름에 있음)'] or '', ri[0], ri[1], ri[6]])
    else:
        D4.append([u, c, n, UP.get(u, ''), lv, '', '', '', '', CM[c]['변형 표시(이름에 있음)'] or '', '', '', '계산 제외(우리 마스터에 없음 · 빈칸 + 로그) — %s' % (CM[c]['사유(분류 안 됨 · 확인 필요)'] or lv)])
print('식별표 마스터 고른 근거', PICK)
# 5. 코드별 계산 사양
D5 = []
for c in codes:
    cm = CM[c]
    if not CODE_G.get(c):
        continue
    for k3, n, lv in CODE_G[c]:
        g = sorted(GK[k3], key=lambda r: PO.get(r['p'], 99)); rep = g[0]
        ri = rinfo(n)
        D5.append([c, cm['대표 담보명(정보계)'], n, lv, rep['id'], ', '.join(dict.fromkeys(r['p'] for r in g)), rep['n'], cm['변형 표시(이름에 있음)'] or '',
                   ri[1], ri[0], ri[2], ri[3], ri[4], ri[5], ' '.join(rep.get('k') or []) or '-', ' '.join(rep.get('x') or []) or '-', ' '.join(rep.get('hc') or []) or '-',
                   len(CODE_CELLS.get(c, ())) or '', ' '.join(sorted(CODE_CELLS.get(c, ()))), ri[6]])
# 6. GA 칸 × 담보코드
MODE = {'first': '최초(사례 지급 줄 합)', 'year': '반복(연 1회 줄만)', 'each': '매 회(1회당 줄만)', 'max': '가장 큰 값', 'direct': '가입금액 그대로'}
D6 = []
for cdef in RES['cells']:
    cid = cdef['id']; cs = sorted(CELL_CODES.get(cid, ()))
    kind = {'engine': '엔진 계산'}.get(cdef['kind'], cdef['kind'])
    D6.append([cid, cdef['page'], cdef['section'], cdef['row'], cdef['col'], kind, cdef.get('sc_name') or cdef.get('note') or '', MODE.get(cdef.get('mode'), cdef.get('mode') or ''),
               len(cs) or '', ' '.join(cs) if cs else ('설계서 담보 그대로 표시 — GA 설계도 ⑨' if cdef['kind'] != 'engine' else '')])
# 7. 계산 제외 담보코드
D7 = []
for c in codes:
    cm = CM[c]
    if cm['분류'] == '매핑됨': continue
    D7.append([c, cm['대표 담보명(정보계)'], cm['분류'], cm['사유(분류 안 됨 · 확인 필요)'], cm['코드 계열(앞 3자리 · 추정)'], cm['쓰는 단위상품코드 수'],
               '확인 결과에 따라 매핑 추가' if cm['분류'] == '확인 필요' else '계산 제외 + 로그(빈칸)'])
# 8. 단위상품코드
D8 = [[u['단위상품코드'], u['담보 수'], u['우리 특약과 맞춘 담보 수'], u['맞춘 비율'], u['고지 구분자(이름에 붙은 것 · 건수)'], u['추정 상품'], u['후보를 좁힌 근거']] for u in UNITS]

# 10. 설계 예시(테스트 설계서 3건)
KEY2CODES = collections.defaultdict(set)
for u, c, n in rows: KEY2CODES[nkey(n)].add(c)
EXD = ['the-mb-40f.pdf', 'naemom-40f.pdf', 'd272600.pdf']   # 간병인지원일당(Ⅶ)이 든 설계서는 쓰지 않는다(2610 판에서 담보 삭제 · 소유자 2026-11-06)
DLABEL = {'the-mb-40f.pdf': 'The좋은 케어프리 M-Basket 여40(GA 캡처 기준 설계서)', 'naemom-40f.pdf': '내Mom대로 여40', 'd272600.pdf': '통합간편 남'}
D10a, D10b = [], []
for d in RES['designs']:
    base = os.path.basename(d['pdf'])
    if base not in EXD: continue
    lab = DLABEL[base]
    for r in d['riders']:
        nm0 = re.sub(r'^[┗\s]+', '', r['name'])
        cs = sorted(KEY2CODES.get(nkey(nm0), ()))
        ri = rinfo(nm0)
        D10a.append([lab, r['no'], r['name'], r['man'], ' '.join(cs) if cs else '(정보계 표에 같은 이름 없음)', ri[0], ri[1], ri[6]])
    for cid, v in d['cells'].items():
        cdef = CELLDEF.get(cid, {})
        ls = [l for l in v['lines'] if l.get('counted', True)]
        det = ' · '.join('%s(%s) %s' % (l['name'], ' '.join(sorted(KEY2CODES.get(nkey(re.sub(r'^[┗\s]+', '', l['name'])), ()))) or '-', format(l['amt'], 'g')) for l in ls)
        D10b.append([lab, cid, '%s · %s · %s' % (cdef.get('section', ''), cdef.get('row', ''), cdef.get('col', '')), ' / '.join(v['tokens']), det])

# 시트 만들기
sheet_map = [
 ('2. 전체 흐름', ['단계', '입력', '하는 일', '출력', '근거(이 엑셀 · GA 설계도)', '지금 엔진의 위치'], FLOW, [6, 22, 70, 22, 30, 36], 'text'),
 ('3. 입력 데이터 사양', ['항목', '필수 여부', '값', '어디에 쓰나', '주의'], SPEC, [26, 10, 46, 40, 46], 'text'),
 ('4. 담보 식별표', ['단위상품코드', '담보코드', '상품담보명(정보계 원문)', '단위상품 추정 상품', '판정 단계', '특약 마스터 ID', '상품(마스터)', '특약명(마스터)', '마스터 고른 근거', '변형 표시', '규칙ID', '보상 유형', '계산 여부'], D4, [11, 9, 56, 14, 10, 12, 14, 50, 30, 18, 18, 16, 36], (3, 8, 9, 13), 13),
 ('5. 담보코드별 계산 사양', ['담보코드', '대표 상품담보명(정보계)', '이 줄의 정보계 이름', '판정 단계', '대표 특약 마스터 ID', '같은 알맹이 상품', '특약명(마스터)', '변형 표시', '보상 유형', '규칙ID', '규칙 설명', '금액 산정식', '지급 빈도', '질병코드 판정 방식', '약관 질병코드(KCD · 별표)', '제외코드', '수가코드', 'GA 칸 수', 'GA 칸 번호', '계산 여부'],
  D5, [9, 40, 40, 10, 12, 30, 44, 16, 16, 18, 40, 34, 16, 40, 40, 18, 24, 7, 30, 26], (2, 3, 7, 11, 12, 14, 15, 17, 19, 20), 20),
 ('6. GA 칸 × 담보코드', ['칸ID', '쪽', '구역', '행', '열', '칸 종류', '칸 사례', '집계 방식', '금액이 잡히는 담보코드 수', '담보코드'], D6, [9, 5, 12, 14, 14, 10, 30, 20, 9, 90], (7, 10)),
 ('7. 계산 제외 담보코드', ['담보코드', '대표 상품담보명(정보계)', '분류', '사유', '코드 계열(추정)', '쓰는 단위상품코드 수', 'IT 처리'], D7, [9, 50, 11, 50, 18, 9, 24], (2, 4)),
 ('8. 단위상품코드 → 상품', ['단위상품코드', '담보 수', '우리 특약과 맞춘 담보 수', '맞춘 비율', '고지 구분자', '추정 상품', '추정 근거'], D8, [11, 8, 10, 9, 30, 46, 50], (5, 6, 7)),
 ('9. 예외 처리 · IT 확인', ['항목', '내용', '처리', '규모 · 위치'], EXC, [22, 60, 60, 24], 'text'),
 ('10-1. 설계 예시 담보', ['설계서', '설계서 담보 번호', '담보명(설계서)', '가입금액(만원)', '정보계 담보코드(이름이 같은 코드)', '규칙ID', '보상 유형', '계산 여부'], D10a, [28, 8, 56, 10, 30, 18, 16, 30], (3, 5)),
 ('10-2. 설계 예시 칸 값', ['설계서', '칸ID', '칸', '지면 값(만원)', '집계에 들어간 담보(담보코드) 금액'], D10b, [28, 9, 34, 14, 110], (3, 5)),
]
for title, head, data, widths, *opt in sheet_map:
    if opt and opt[0] == 'text': text_sheet(title, head, data, widths)
    else:
        wc = opt[0] if opt else (); fc = opt[1] if len(opt) > 1 else None
        sheet(title, head, data, widths, wc, fc)
for r in range(2, wb['8. 단위상품코드 → 상품'].max_row + 1): wb['8. 단위상품코드 → 상품'].cell(r, 4).number_format = '0%'

# 1. 개요
ws = wb['Sheet']; ws.title = '1. 개요·읽는 법'; wb.move_sheet(ws, offset=-(len(wb.sheetnames) - 1))
def put(r, c, v, font=BF, fill=None):
    cl = ws.cell(r, c, v); cl.font = font; cl.alignment = Alignment(wrap_text=True, vertical='top')
    if fill: cl.fill = PatternFill('solid', fgColor=fill)
    return cl
put(1, 1, '스마트 제안서(GA 디자인판) 설계도 — 정보계 담보코드 기준 · 2610 약관 · 엔진 %s' % (re.search(r"VERSION = '([^']+)'", open(os.path.join(ROOT, 'proposal_smart', 'api.py'), encoding='utf-8').read()).group(1)), TF)
INTRO = [
 '목적 : 사내 전산은 가입설계의 담보를 「단위상품코드 + 담보코드」로 가리킨다. 기존 GA 설계도(dist/ga-blueprint-final.xlsx)는 설계서 PDF 의 담보명에서 출발하므로, 같은 계산을 담보코드에서 출발하도록 다시 짠 것이 이 엑셀이다. 계산 규칙 · 칸 사례 · 금액표는 기존 설계도와 같다(바뀐 것은 담보를 찾는 열쇠).',
 '한 줄 요약 : 담보코드 → (시트 4) 특약 마스터 ID → (시트 5) 약관 질병코드 · 규칙 · 금액식 → (시트 6) GA 칸 사례에 넣어 계산 → 칸 값 → 지면. 못 찾는 담보는 계산 제외 + 로그(빈칸).',
 '읽는 순서 : 2(흐름) → 3(IT 가 넘길 데이터) → 4(담보 식별표 · IT 조회표) → 5(담보코드별 계산 사양) → 6(GA 칸별 담보코드) → 7(계산 제외) → 9(예외 · IT 확인) → 10(시험 자료 : 테스트 설계서 3건을 담보코드로 다시 쓴 것과 칸 값 · 2610 판에서 없어진 간병인지원일당(Ⅶ)이 든 설계서는 쓰지 않는다).',
 '기존 GA 설계도와 같이 본다 : 규칙표 전체(⑦) · 칸 사례 정의(② · 설계도9) · 질병코드 그룹표(설계도7) · 수술분류표(설계도8) · 통합치료비 지급금액표(⑤) · 생활지원비 항목표(⑥) · 칸 집계(설계도10).',
 '자료 : 정보계 「단위상품코드 · 담보코드 · 상품담보명」 표(24,854행 · 2026-11-06 받음) × 특약 마스터 4,976건(14개 상품 · 약관 파싱). 매핑 판정은 자동이며, 확인 필요 코드는 사람이 정한다.',
 '취급 : 정보계 담보코드는 사내 자료다. 사외로 보내지 않는다. 설계서 예시에 설계사명 · 고유번호 같은 개인정보는 넣지 않았다.',
]
r = 2
for t in INTRO: put(r, 1, t); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6); ws.row_dimensions[r].height = 58; r += 1
r += 1
put(r, 1, '집계(수식 · 각 시트를 센다)', B11); r += 1
put(r, 1, '항목', HF, '3A3A3A'); put(r, 2, '건수', HF, '3A3A3A'); r += 1
W4 = "'4. 담보 식별표'"; W5 = "'5. 담보코드별 계산 사양'"; W6 = "'6. GA 칸 × 담보코드'"; W7 = "'7. 계산 제외 담보코드'"
for lab, f in [('담보 식별표 짝(단위상품코드 + 담보코드)', '=COUNTA(%s!B:B)-1' % W4),
               ('  그중 GA 계산 대상', '=COUNTIF(%s!M:M,"GA 계산 대상")' % W4),
               ('  그중 계산 제외 · 사례 계산 대상 아님', '=COUNTA(%s!B:B)-1-COUNTIF(%s!M:M,"GA 계산 대상")' % (W4, W4)),
               ('담보코드별 계산 사양 줄(코드 × 알맹이)', '=COUNTA(%s!A:A)-1' % W5),
               ('GA 칸(엔진 계산)', '=COUNTIF(%s!F:F,"엔진 계산")' % W6),
               ('계산 제외 담보코드(우리 마스터에 없음)', '=COUNTIF(%s!C:C,"분류 안 됨")' % W7),
               ('확인 필요 담보코드', '=COUNTIF(%s!C:C,"확인 필요")' % W7)]:
    put(r, 1, lab); put(r, 2, f); r += 1
for i, w in enumerate([48, 14, 12, 12, 12, 30], 1): ws.column_dimensions[get_column_letter(i)].width = w
wb.save(OUT)
print('saved', OUT, {t: wb[t].max_row - 1 for t in wb.sheetnames})
