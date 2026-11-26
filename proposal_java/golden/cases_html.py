# 4단계 정답지의 덧입력 — 실제 설계 20건에 없는 갈래(간병인 181일 · plus · 체증형 · 상해 간병인만 · 10년 뒤 2배 · 모르는 상품 · 긴 상품명 · 머리 정보 없음 · 큰 금액)를 일부러 만든다.
# 사용 : python3 golden/cases_html.py <정보계 rows.json> <출력 폴더>      → <출력 폴더>/syn_*.json (담보코드 입력 JSON)
# 담보 이름은 정보계 표에서 고른다(사내 자료 — 출력은 저장소에 넣지 않는다).
import sys, os, json, re
rows = json.load(open(sys.argv[1], encoding='utf-8')); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
names = sorted({r[2] for r in rows})
def pick(*pats, n=3, no=()):
    out = []
    for nm in names:
        if all(re.search(p, nm) for p in pats) and not any(re.search(p, nm) for p in no): out.append(nm)
        if len(out) >= n: break
    return out
TH = '(무) 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형) (해약환급금미지급형)'
CF = '무배당 메리츠 케어프리보험 M-Basket2610'
PH, PE = '무배당 메리츠 프리미엄 건강보험2610', '무배당 메리츠 프리미엄 간편보험2610'
def design(product, rs, **kw):
    d = dict(schema=1, design_no=kw.pop('no', 'SYN-0001'), product=product, premium=kw.pop('premium', 98760),
             insured=kw.pop('insured', {'name': '홍길동', 'sex': 'F', 'age': 52}), agent=kw.pop('agent', {'org': '시험본부', 'code': '00000', 'name': '김메리', 'mobile': '010-0000-0000', 'tel': '02-0000-0000'}),
             riders=[dict(no=i + 1, unit_code='', code='', name=n, amount=a, **x) for i, (n, a, x) in enumerate(rs)])
    d.update(kw); return d
def R(ns, amt, **x): return [(n, amt, x) for n in ns]
base = R(pick(r'^암진단비\(유사암제외\)\(통합간편가입\)$', n=1) + pick(r'^뇌졸중진단비', r'통합간편가입', n=1) + pick(r'^질병수술비\(통합간편가입\)$', n=1) + pick(r'^상해수술비\(통합간편가입\)$', n=1), 10000000)
C = {}
C['care181'] = design(TH, base + R(pick(r'간병인사용', r'181일', n=4) + pick(r'간병인사용', r'질병입원일당', r'1일이상', n=3, no=(r'181일',)), 70000))
C['care_plus_esc'] = design(TH, base + R(pick(r'간병인사용', r'\(plus\)', n=2) + pick(r'간병인사용', r'체증', n=3), 50000))
C['care_sup181'] = design(TH, base + [(n, 0, {'unused_daily': 20000}) for n in pick(r'간병인지원', r'질병입원일당', n=3) + pick(r'간병인지원', r'181일', n=2) + pick(r'간병인지원', r'요양성', n=2)]
                          + R(pick(r'간병인지원', r'사용추가보장', n=2), 30000))
C['care_inj_only'] = design(TH, base + R(pick(r'간병인(지원|사용)', r'상해입원일당', n=3), 50000))
C['care_nurse_only'] = design(TH, base + R(pick(r'간호.?간병통합서비스', r'질병입원일당', n=2, no=(r'간병인',)), 30000))
C['prem_easy_esc10'] = design(PE, R(pick(r'체증형,10년후2배지급', r'진단비', n=6) + pick(r'체증형,10년후2배지급', r'수술비', n=3), 20000000) + R(pick(r'^암진단비\(유사암제외\)', n=1), 30000000))
C['prem_health_mix'] = design(PH, R(pick(r'체증형,10년후2배지급', n=8), 15000000) + R(pick(r'^(갱신형 )?뇌혈관질환진단비', n=2) + pick(r'허혈성심장질환진단비', n=2), 25000000))
C['unknown_product'] = design('무배당 메리츠 처음보는상품보험2699', base + R(pick(r'1-5종', r'질병', n=3) + pick(r'131대질병수술비', n=2), 3000000))
C['big_amounts'] = design(CF, R(pick(r'^암진단비\(유사암제외\)$', n=1) + pick(r'^뇌혈관질환진단비$', n=1) + pick(r'^허혈성심장질환진단비$', n=1), 150000000)
                          + R(pick(r'^질병수술비$', n=1) + pick(r'^상해수술비$', n=1) + pick(r'골절진단비', n=2), 12345) + R(pick(r'통합치료비', n=4), 50000000) + R(pick(r'수술비Ⅱ\(1-5종\)\(체증형\)', n=3) + pick(r'25%체증형', n=4), 5000000))
C['bare_head'] = dict(schema=1, product='(무) 메리츠 The건강한 내Mom대로 5.10.5 보장보험2610 (해약환급금미지급형(납입후50%))(납입면제 2형)(건강고지형(8년))(아주아주 긴 꼬리표가 붙은 상품명 시험)',
                      riders=[dict(name=n, amount=a) for n, a, _ in base + R(pick(r'신수술비', n=4) + pick(r'생활지원비', n=3) + pick(r'태아', r'수술비', n=2), 1000000)])
C['one_rider'] = design(TH, R(pick(r'^유사암진단비', r'통합간편가입', n=1), 5000000), insured={'name': '', 'sex': 'M'}, agent={})
C['line_mismatch'] = design(TH, R(pick(r'자동차사고부상', n=3) + pick(r'벌금', n=2) + pick(r'변호사선임비용', n=2) + pick(r'^골절진단비', n=1) + pick(r'^상해수술비$', n=1), 3000000))      # 설계 담보가 상품 라인 마스터에 거의 없음 → 미가입 줄을 싣지 않는 길
for k, v in C.items():
    json.dump(v, open(os.path.join(OUT, 'syn_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('syn_%-18s 담보 %d' % (k, len(v['riders'])))
