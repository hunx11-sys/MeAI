# -*- coding: utf-8 -*-
"""담보코드 입력(code_input.py) 점검 — 설계서 PDF · 정보계 표 없이 도는 자체 시험(묶음 안에서도 실행)

  python3 check_code_input.py          # 「결과 : 전부 통과」 여야 한다(종료코드 0)

보는 것 : 입력 점검(잘못된 JSON · 빠진 항목 · 금액 꼴) · 상품명 → 상품 라인 · 1-7종 수술비 두 꼴(부모 이름 있음 / 없음)이 같은 계산 ·
고지 구분자 · (N년갱신) · [기본계약] 이 붙어도 같은 계산 · 금액 0 · 부모 줄 · 같은 담보 두 번 · 간병인지원(현물) · 모르는 담보(빈칸 + 로그) ·
전부 모르는 담보(멈춤) · 담보 식별표로 찾기(이름으로 못 찾았을 때) · 예시 입력(ga_docs/code_input_example.json)으로 칸 계산
"""
import os, sys, json, copy, tempfile
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import code_input as CI, scen_engine as S, ga_spec as GS, pipeline

N = [0, 0]
def ok(name, cond, msg=''):
    N[0] += 1
    if not cond: N[1] += 1; print('실패 %s %s' % (name, msg))
def bad(name, obj, want):
    try: CI.parse(obj); ok(name, False, '— 받아들여짐')
    except CI.InputError as e: ok(name, want in str(e), '— 이유 글이 다름 : %s' % e)
EX = json.load(open(os.path.join(BASE, 'ga_docs', 'code_input_example.json'), encoding='utf-8'))
def mk(**kw):
    d = copy.deepcopy(EX); d.update(kw); return d
def rows(d):
    S.ISSUES.clear(); GS.clear_cache(); return CI.riders(CI.parse(d))
def cells(rid):
    GS.clear_cache(); return {c['key']: GS.cell_value(c, rid)[0] for c in GS.CELLS}

# 1. 입력 점검
bad('JSON 아님', '{not json', 'JSON')
bad('맨 바깥이 목록', '[]', '{ }')
bad('담보 없음', mk(riders=[]), 'riders')
bad('상품명 없음', mk(product=''), 'product')
bad('schema 2', mk(schema=2), 'schema')
bad('담보명 없음', mk(riders=[{'no': 1, 'amount': 1}]), 'name')
bad('금액이 글자', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': '많이'}]), '금액')
bad('금액 음수', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': -1}]), '범위')
bad('나이가 글자', mk(insured={'name': 'x', 'sex': 'M', 'age': '마흔'}), 'age')
p = CI.parse(mk(premium='123,450원', insured={'name': '홍길동', 'sex': '여', 'age': '45세'}))
ok('금액 · 성별 · 나이 표기 받기', p['premium'] == 123450 and p['insured']['sex'] == 'F' and p['insured']['age'] == '45')

# 2. 상품명 → 상품 라인(설계서 PDF 와 같은 규칙)
for prod, line in [('(무) 메리츠 통합간편건강보험(연만기형)2610(355입원,수술고지간편심사형)', '통합간편'), ('(무) 내Mom대로 보장보험2610 (해약환급금지급형)', '내Mom대로'),
                   ('(무) 메리츠 The건강한 내Mom대로 5.10.5 보장보험2610', 'The건강한내Mom대로5.10.5'), ('(무) 메리츠 The건강한 5.10.5 보장보험2610', 'The건강한5.10.5'),
                   ('(무) 메리츠 The좋은 내Mom대로 보장보험2610', 'The좋은내Mom대로'), ('(무) The가벼운 간편355건강보험(세만기형)2610', 'The가벼운간편355'),
                   ('(무) 메리츠 간편31 건강보험2610', '간편31'), ('(무) 내Mom같은 어린이보험2610(태아전용)', '내Mom같은어린이'),
                   ('(무) 메리츠 The좋은 알파Plus보장보험2610', 'The좋은케어프리'), ('(무) 알파Plus보장보험2610', '케어프리'), ('(무) 메리츠 케어프리보험 M-Basket2610', '케어프리')]:
    got = CI.line_of(CI.parse(mk(product=prod, riders=[{'no': 1, 'name': '질병수술비', 'amount': 200000}])))
    ok('상품 라인 %s' % line, got == line, '— %s → %s' % (prod, got))
ok('상품명으로 못 정하면 고지 구분자(통합간편가입)로', CI.line_of(CI.parse(mk(product='(무) 이름을 모르는 상품'))) == '통합간편')

# 3. 담보 줄
R = rows(EX); by = {r['no']: r for r in R}
ok('예시 담보 수', len(R) == 14, '— %d' % len(R))
ok('1-7종(부모 이름 있는 꼴) → ┗ 줄 + 부모 특약', by[9]['name'] == '┗ 수술비[질병3종]' and by[9]['via'] == '수술비(1-7종, 연간3회한)[질병1-3종]' and by[9]['matched'] and by[9]['man'] == 50)
ok('1-7종(부모 이름 없는 꼴) → ┗ 줄 + 부모 특약', by[10]['name'] == '┗ 수술비[상해2종]' and by[10]['via'] == '수술비(1-7종, 연간3회한)[상해1-3종]' and by[10]['matched'])
ok('고지 구분자 떼기', by[1]['name'] == '암진단비(유사암제외)' and by[1]['matched'] and by[1]['how'] == 'name')
ok('간병인지원(현물) : 금액 0 · 미사용 일당 글자', by[13]['man'] == 0 and by[13]['amount_text'] == '간병인지원 또는 2만원' and by[13]['matched'])
ok('모르는 담보 : 계산 제외(멈추지 않음)', by[14]['matched'] is False and by[14]['how'] is None)
base = cells(R)
ok('예시 입력 칸 계산', base['p1.ca.dx.일반암'] == 3000 and base['p1.dz.백내장'] and base['p1.dz.골절진단'], '— 일반암 %s · 백내장 %s · 골절 %s' % (base['p1.ca.dx.일반암'], base['p1.dz.백내장'], base['p1.dz.골절진단']))
ok('모르는 담보는 칸에 들어가지 않음', not any(l.get('no') == 14 for c in GS.CELLS for l in GS.cell_value(c, R)[1]))
# 이름 꼴이 달라도 같은 계산
alt = copy.deepcopy(EX)
for r in alt['riders']:
    if r['no'] in (7, 8, 9): r['name'] = r['name'].replace('수술비(1-7종, 연간3회한)', '수술비')      # 부모 이름 없는 꼴로
    if r['no'] == 10: r['name'] = '수술비(1-7종, 연간3회한)[상해2종](통합간편가입)'                    # 부모 이름 있는 꼴로
    if r['no'] in (1, 3): r['name'] = '[기본계약]' + r['name'].replace('(통합간편가입)', '(편한가입)')
ok('1-7종 두 꼴 · 고지 구분자가 달라도 칸 값 같음', cells(rows(alt)) == base)
# 금액 0 · 부모 줄 · 중복
extra = copy.deepcopy(EX); n0 = len(EX['riders'])
extra['riders'] += [{'no': 21, 'name': '수술비(1-7종, 연간3회한)[질병4-7종](통합간편가입)', 'amount': 1000000}, {'no': 22, 'name': '질병수술비(통합간편가입)', 'amount': 0},
                    {'no': 5, 'name': '질병수술비(통합간편가입)', 'amount': 200000}]
R2 = rows(extra)
ok('부모 줄 · 금액 0 · 같은 담보 두 번은 건너뜀', len(R2) == 14 and cells(R2) == base, '— %d줄' % len(R2))
ok('건너뛴 까닭이 로그에', sum(1 for i in S.ISSUES if '부모 줄' in i['사유'] or '가입금액이 0' in i['사유'] or '두 번' in i['사유']) == 3)
# 전부 모르는 담보 → 멈춤(빈 제안서를 만들지 않는다)
try: rows(mk(riders=[{'no': 1, 'name': '세상에 없는 담보 가', 'amount': 1000000}, {'no': 2, 'name': '세상에 없는 담보 나', 'amount': 1000000}])); ok('전부 모르는 담보 → 멈춤', False)
except pipeline.DesignUnreadable: ok('전부 모르는 담보 → 멈춤', True)

# 4. 담보 식별표(단위상품코드 + 담보코드)로 찾기 — 이름으로 못 찾았을 때만
tmp = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8')
json.dump({'schema': 1, 'map': {'X0000|000099': {'id': '통95', 'p': '통합간편'}}}, tmp); tmp.close()
os.environ['GA_CODE_MAP'] = tmp.name; CI._CM = None
R3 = rows(mk(riders=EX['riders'][:4] + [{'no': 99, 'unit_code': 'X0000', 'code': '000099', 'name': '질병 수술 보장(정보계에서 이름이 바뀐 경우)', 'amount': 200000}]))
r99 = next(r for r in R3 if r['no'] == 99)
ok('이름으로 못 찾으면 담보 식별표로', r99['matched'] and r99['how'] == 'code' and r99['mname'] == '질병수술비', '— %s' % {k: r99.get(k) for k in ('matched', 'how', 'mname')})
os.environ.pop('GA_CODE_MAP'); CI._CM = None; os.unlink(tmp.name)
ok('담보 식별표가 없어도 돈다', len(rows(EX)) == 14)

# 5. v9.07 에 찾아 고친 계산 오류 — 다시 생기지 않게(정보계 전 줄 계산 대조 scripts/codemap/audit_rows.py 가 찾은 것)
def one(product, name, won=10000000):
    return rows(dict(schema=1, product=product, riders=[{'no': 1, 'name': name, 'amount': won}]))
KEY = {c['key']: c for c in GS.CELLS}
for pre in ('', '갱신형 '):
    for nm in ('암치료,후유장해및진단비[암진단비(유사암제외)]', '암후유장해및진단비[암진단비(유사암제외)]'):
        c = cells(one('무배당 메리츠 The좋은 케어프리보험 M-Basket2610', pre + nm))
        ok('세트 특약 암진단비(유사암제외) — 일반암 칸에만(%s%s)' % (pre, nm[:10]), c['p1.ca.dx.일반암'] == 1000 and not c['p1.ca.dx.유사암'] and not c['p2.dx.유사암'] and not c['p2.dis'],
           '— 일반암 %s · 유사암 %s · 암후유장해 %s' % (c['p1.ca.dx.일반암'], c['p1.ca.dx.유사암'], c['p2.dis']))
c = cells(rows(dict(schema=1, product='무배당 The가벼운 간편355건강보험(세만기형)2610', riders=[
    {'no': 1, 'name': '암치료,후유장해및진단비[암후유장해(3-100%)](편한가입)', 'amount': 50000000}, {'no': 2, 'name': '암치료,후유장해및진단비[암80%이상후유장해](편한가입)', 'amount': 1000000},
    {'no': 3, 'name': '암치료,후유장해및진단비[암진단비(유사암제외)](편한가입)', 'amount': 30000000}, {'no': 4, 'name': '암치료,후유장해및진단비[항암약물치료비](편한가입)', 'amount': 20000000}])))
ok('암후유장해 칸 = 후유장해 세부보장만(진단비 · 항암치료비 가입금액은 더하지 않음)', c['p2.dis'] == 5100, '— %s' % c['p2.dis'])
# 통합생활지원비 : 담보를 만들었다 지워도(같은 메모리 주소가 다시 쓰여도) 제 항목표가 나온다
A = cells(one('무배당 메리츠 통합간편건강보험(세만기형)2610', '암 통합생활지원비(월간한도)(통합간편가입)')); B = cells(one('무배당 메리츠 통합간편건강보험(세만기형)2610', '2대질환 통합생활지원비(월간한도)(통합간편가입)'))
same = True
for i in range(60):
    x = cells(one('무배당 메리츠 통합간편건강보험(세만기형)2610', ('암' if i % 2 else '2대질환') + ' 통합생활지원비(월간한도)(통합간편가입)'))
    same = same and x == (A if i % 2 else B)
ok('통합생활지원비 — 번갈아 60번 계산해도 같은 값', same and A != B and any(A.values()) and any(B.values()))
# 만들지 않는 상품 정책(rules.json > exclude_products) — 목록에 올린 상품은 GA 길에서도 멈춘다.
# v9.09 부터 프리미엄 건강 · 간편보험은 목록에서 뺐다(소유자 2026-11-23 「프리미엄을 반영한다고 가정」) → 장치는 시험용 이름으로 확인한다
import ga_proposal as GP
S.RULEDOC.setdefault('exclude_products', []).append({'m': '시험용제외상품', 'nm': '시험용 제외 상품', 'why': '자체 시험'})
try: GP.load(CI.parse(mk(product='무배당 메리츠 시험용 제외상품2610'))); ok('정책 목록에 올린 상품 → 멈춤', False)
except pipeline.DesignUnreadable as e: ok('정책 목록에 올린 상품 → 멈춤', '만들지 않는' in str(e))
S.RULEDOC['exclude_products'].pop()
# 신상품 신담보(약관 검수 전) — 일반 규칙에 걸려 계산되지 않는다
for prod, nm in (('무배당 올케어 꽉 채운 수술비보험(세만기형)2610(일반고지형)', '종합병원 전신마취(1시간초과) 수술비(1-7종,연간3회한)[질병]'), ('무배당 올케어 꽉 채운 뇌심보험(세만기형)2610(일반심사형)', '중증뇌경색증진단비')):
    try: v = cells(one(prod, nm))
    except pipeline.DesignUnreadable: v = {}
    ok('검수 전 신담보는 빈칸(%s)' % nm[:12], not any(v.values()), '— %s' % {k: x for k, x in v.items() if x})
ok('새 상품 라인 읽기', CI.line_of(CI.parse(mk(product='무배당 올케어 꽉 채운 수술비보험(세만기형)2610(통합간편고지형)'))) == '올케어수술비' and CI.line_of(CI.parse(mk(product='(무) Only You 통합보험2610(355간편고지형)'))) == 'OnlyYou통합간편')

# 6. v9.08 신담보 1차 검수(약관 조문 · 별표 대조) — 계산을 붙인 담보는 제 칸에만, 조건부 담보는 빈칸
PB, PO, PG = '무배당 올케어 꽉 채운 뇌심보험(세만기형)2610(일반심사형)', '(무) Only You 통합보험2610(355간편고지형)', '무배당 올케어 꽉 채운 골키퍼 건강보험2610(일반심사형)'
def only(c, *keys): return {k for k, v in c.items() if v} == set(keys)
c = cells(one(PB, '뇌경색증진단비')); ok('뇌경색증진단비 — 뇌졸중 진단 칸에만', only(c, 'p1.bh.dx.뇌졸중', 'p3.dx.뇌졸중') and c['p1.bh.dx.뇌졸중'] == 1000, '— %s' % {k: v for k, v in c.items() if v})
c = cells(one(PB, '뇌혈관질환관혈수술비(연간1회한)')); ok('뇌혈관질환 관혈수술비 — 개두수술 칸에만(코일색전술 · 개흉 아님)', c['p1.bh.txb.개두수술'] == 1000 and not c['p1.bh.txb.코일색전술'] and not c['p1.bh.txh.개흉수술'])
c = cells(one(PB, '심장관련질환관혈수술비(연간1회한)')); ok('심장관련질환 관혈수술비 — 개흉수술 칸에만(스텐트 · 개두 아님)', c['p1.bh.txh.개흉수술'] == 1000 and not c['p1.bh.txh.스텐트삽입술'] and not c['p1.bh.txb.개두수술'])
c = cells(one(PB, '혈전용해치료비Ⅲ(연간1회한)')); ok('혈전용해치료비Ⅲ — 뇌 · 심 혈전용해 칸', c['p1.bh.txb.혈전용해'] == 1000 and c['p1.bh.txh.혈전용해'] == 1000 and not c['p1.bh.txb.혈전제거'])
c = cells(one(PB, '기계적혈전제거술(카테터법)치료비Ⅲ(급여, 연간1회한)')); ok('기계적혈전제거술Ⅲ — 혈전제거 칸', c['p1.bh.txb.혈전제거'] == 1000 and not c['p1.bh.txb.혈전용해'])
c = cells(one(PO, '치핵수술비(355간편가입)')); ok('치핵수술비 — 치질 칸에만', only(c, 'p1.dz.치질') and c['p1.dz.치질'] == 1000, '— %s' % {k: v for k, v in c.items() if v})
c = cells(one(PO, '관절염,생식기질환수술비(355간편가입)')); ok('관절염,생식기질환수술비 — 무릎관절 · 전립선 칸에만(자궁근종 D25 아님)', only(c, 'p1.dz.무릎관절질환', 'p1.dz.전립선비대증'), '— %s' % {k: v for k, v in c.items() if v})
c = cells(one(PO, '백내장수술비(355간편가입)')); ok('백내장수술비 — 백내장 칸에만', only(c, 'p1.dz.백내장'))
c = cells(one(PO, '유방의장애수술비(355간편가입)')); ok('유방의장애수술비 — 유방양성종양(D24) 칸에는 지급 없음', not any(c.values()))
rO = one(PO, '관절염,생식기질환수술비(355간편가입)'); ok('관절염,생식기질환 분류표 — 제외코드(A18.01 · A18.17 · N74.0 · N74.1 · M01.1 · M14.2)가 대상 코드에 없음',
   set(rO[0]['excl']) >= {'A18.01', 'A18.17', 'N74.0', 'N74.1', 'M01.1', 'M14.2'} and not ({'A18.01', 'A18.17', 'N74.0', 'N74.1'} & set(rO[0]['codes'])))
rH = one(PO, '치핵수술비(355간편가입)'); ok('치핵 분류표 — 대상 K64 · 「제외 -」 의 O87.2 · O22.4 는 제외코드', rH[0]['codes'] == ['K64'] and set(rH[0]['excl']) == {'O87.2', 'O22.4'})
dsk = lambda **tg: (lambda s: (s['tags'].update(tg), s)[1])(copy.deepcopy(GS.sc_dz('디스크', '병원')))
amt = lambda rid, s: sum(l["amt"] for l in S.pay_lines(rid, s))
rS = one(PG, '갱신형 척추질병수술비(연간1회한)(관혈,비관혈)')
ok('척추질병수술비(관혈,비관혈) — 관혈 100% · 비관혈 50%', amt(rS, dsk()) == 1000 and amt(rS, dsk(open=False)) == 500, '— %s · %s' % (amt(rS, dsk()), amt(rS, dsk(open=False))))
rJ = one(PG, '갱신형 상급종합병원 관절질환수술비(연간1회한)'); kn = lambda h: copy.deepcopy(GS.sc_dz('무릎관절질환', h))
ok('상급종합병원 관절질환수술비 — 상급종합에서만', amt(rJ, kn('상급종합')) == 1000 and not amt(rJ, kn('종합')) and not amt(rJ, kn('병원')))
rD = one(PG, '갱신형 호흡기질병입원일당(1일이상180일한도)', 20000); adm = lambda k, d: GS.sc(k, [], cause='질병', hosp='병원', days=d)
ok('호흡기질병입원일당 — 호흡기질병 입원에만(일반 입원일당 규칙으로 새지 않음)', amt(rD, adm('J18', 10)) == 20 and not amt(rD, adm('C16', 10)), '— %s · %s' % (amt(rD, adm('J18', 10)), amt(rD, adm('C16', 10))))
for nm in ('중증뇌경색증진단비', '중등증이상허혈성심장질환진단비', '2대질환 중증치료비(급여,연간1회한)[2대질환 지속적신대체요법(CRRT)치료비(급여,연간1회한)]', '뇌경색증진단 응급환자 응급실내원비(연간1회한)'):
    try: v = cells(one(PB, nm))
    except pipeline.DesignUnreadable: v = {}
    ok('조건부 신담보는 빈칸(%s)' % nm[:14], not any(v.values()), '— %s' % {k: x for k, x in v.items() if x})
try: v = cells(one(PG, '갱신형 회복기재활의료기관 골반대퇴골절입원일당(1일이상30일한도)'))
except pipeline.DesignUnreadable: v = {}
ok('회복기재활의료기관 입원일당은 빈칸(의료기관 지정 여부를 사례로 알 수 없음)', not any(v.values()))

# 7. v9.09 프리미엄 건강 · 간편보험(가정 반영) — 10년 뒤 2배 체증형은 같은 이름 일반형과 같은 칸 · 같은 금액(가입금액 기준)
PH, PE = '무배당 메리츠 프리미엄 건강보험2610', '무배당 메리츠 프리미엄 간편보험2610'
ok('프리미엄 상품 라인 읽기', CI.line_of(CI.parse(mk(product=PH))) == '프리미엄건강' and CI.line_of(CI.parse(mk(product=PE))) == '프리미엄간편')
try: GP.load(CI.parse(mk(product=PH))); ok('프리미엄 건강보험 → 만든다(제작 제외 목록에서 뺌)', True)
except pipeline.DesignUnreadable as e: ok('프리미엄 건강보험 → 만든다(제작 제외 목록에서 뺌)', False, '— %s' % e)
T10 = '(체증형,10년후2배지급)'
for prod, base in ((PH, '암진단비(유사암제외)'), (PH, '유사암진단비'), (PH, '질병수술비'), (PH, '암수술비(유사암제외)'), (PE, '뇌졸중진단비Ⅱ(355간편가입)'), (PE, '혈전용해치료비Ⅱ(뇌졸중)(연간1회한)(355간편가입)')):
    esc = base.replace('(355간편가입)', '') + T10 + ('(355간편가입)' if '(355간편가입)' in base else '')
    ra, rb = one(prod, base), one(prod, esc); a, b = cells(ra), cells(rb)
    ok('체증형(10년 뒤 2배) = 일반형과 같은 칸 · 같은 금액(%s)' % base[:14], a == b and any(a.values()) and rb[0]['matched'] and rb[0]['codes'] == ra[0]['codes'] and rb[0]['excl'] == ra[0]['excl'],
       '— 일반 %s · 체증 %s' % ({k: v for k, v in a.items() if v}, {k: v for k, v in b.items() if v}))
c = cells(rows(dict(schema=1, product=PH, riders=[{'no': 1, 'name': '암진단비(유사암제외)', 'amount': 10000000}, {'no': 2, 'name': '암진단비(유사암제외)' + T10, 'amount': 20000000}])))
ok('일반형 + 체증형 같이 가입 → 가입금액 합(체증형은 10년 경과 전 100% 기준)', c['p1.ca.dx.일반암'] == 3000, '— %s' % c['p1.ca.dx.일반암'])

# 진단금 둘째 줄 「계약 10년 후 진단 시」(v9.10) = 칸 금액 + 체증형 지급액(체증형만 2배 · 일반형은 그대로) · 체증형이 없는 칸에는 없음
import ga_v2 as G2
G2.load(CI.parse(mk(product=PH, riders=[{'no': 1, 'name': '암진단비(유사암제외)', 'amount': 30000000}, {'no': 2, 'name': '암진단비(유사암제외)' + T10, 'amount': 20000000},
    {'no': 3, 'name': '유사암진단비', 'amount': 6000000}, {'no': 4, 'name': '뇌혈관질환진단비Ⅱ', 'amount': 10000000}, {'no': 5, 'name': '뇌졸중진단비Ⅱ' + T10, 'amount': 10000000},
    {'no': 6, 'name': '질병수술비' + T10, 'amount': 200000}])))
ok('10년 후 금액 : 일반형 3,000 + 체증형 2,000 → 7,000(칸 전체 2배 아님)', G2.V('p1.ca.dx.일반암') == 5000 and G2.dx10('p1.ca.dx.일반암') == 7000 and G2.dx10('p2.dx.일반암') == 7000, '— %s' % G2.dx10('p1.ca.dx.일반암'))
ok('10년 후 금액 : 체증형이 없는 칸(유사암 · 뇌혈관)에는 적지 않음', G2.dx10('p1.ca.dx.유사암') is None and G2.dx10('p1.bh.dx.뇌혈관') is None and G2.dx10_sum('p1.ca.dx.유사암') is None)
ok('10년 후 금액 : 뇌졸중 = 뇌혈관질환진단비 1,000 + 뇌졸중진단비(체증형) 1,000 → 3,000', G2.dx10('p1.bh.dx.뇌졸중') == 3000 and G2.dx10('p3.dx.뇌졸중') == 3000)
ok('10년 후 표기는 진단금 칸에만(수술 칸은 주석만)', G2.dx10_sum('p1.ca.sg.endo') is None and G2.has_esc10())
ok('둘째 줄 글귀에 「최대」 를 쓰지 않는다', '최대' not in G2.dx10_text(7000) + G2.dx10_text(7000, long=False) and G2.dx10_text(7000) == '계약 10년 후 진단 시 7,000만')

print('\n결과 : %s — 점검 %d개 · 실패 %d' % ('전부 통과' if not N[1] else '실패', N[0], N[1]))
sys.exit(1 if N[1] else 0)
