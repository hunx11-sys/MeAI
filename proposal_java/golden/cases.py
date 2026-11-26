# 2 · 3단계 정답지의 입력 묶음 — dump_match.py · dump_cells.py 가 같이 쓴다.
# 사용 : cases.build(<입력 JSON 폴더>, <담보 식별표 code_map.json 또는 ''>, <출력 폴더>) → [{id, text, cm}]
#   text = 입력 JSON 글자 그대로(틀린 JSON 도 있다) · cm = '' (담보 식별표 없음) 또는 식별표 파일 경로
# 실제 설계에서 나온 입력(개인정보)과 정보계 코드가 들어가므로 출력은 저장소에 넣지 않는다.
import os, sys, json, copy, glob
HERE = os.path.dirname(os.path.abspath(__file__)); PS = os.path.join(HERE, '..', '..', 'proposal_smart')
EX = json.load(open(os.path.join(PS, 'ga_docs', 'code_input_example.json'), encoding='utf-8'))
def mk(**kw):
    d = copy.deepcopy(EX); d.update(kw); return d
def J(o): return json.dumps(o, ensure_ascii=False)
TH = '무배당 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형)'
PB, PO, PG = '무배당 올케어 꽉 채운 뇌심보험(세만기형)2610(일반심사형)', '(무) Only You 통합보험2610(355간편고지형)', '무배당 올케어 꽉 채운 골키퍼 건강보험2610(일반심사형)'
PH, PE = '무배당 메리츠 프리미엄 건강보험2610', '무배당 메리츠 프리미엄 간편보험2610'
T10 = '(체증형,10년후2배지급)'
def one(product, name, won=10000000): return dict(schema=1, product=product, riders=[{'no': 1, 'name': name, 'amount': won}])

def build(inputs_dir, code_map, out_dir):
    C = []
    def add(i, text, cm=''): C.append(dict(id=i, text=text if isinstance(text, str) else J(text), cm=cm))
    # A. 실제 설계 20건 × 이름 꼴 2가지 + 예시 — 담보 식별표 없이 / 있이
    files = sorted(glob.glob(os.path.join(inputs_dir, '*_full.json')) + glob.glob(os.path.join(inputs_dir, '*_row.json')))
    for f in files + [os.path.join(PS, 'ga_docs', 'code_input_example.json')]:
        nm = os.path.splitext(os.path.basename(f))[0]; t = open(f, encoding='utf-8-sig').read()
        add('A:' + nm, t)
        if code_map: add('A:' + nm + '@cm', t, code_map)
    # B. 입력 점검 — 틀린 입력 · 가장자리 값(check_code_input.py 1 · 3 · 4 의 경우 + 더)
    R1 = [{'no': 1, 'name': '질병수술비', 'amount': 200000}]
    B = [('JSON 아님', '{not json'), ('맨 바깥이 목록', '[]'), ('맨 바깥이 글자', '"x"'), ('맨 바깥이 수', '3'), ('빈 글자', ''),
         ('담보 없음', mk(riders=[])), ('담보가 사전', mk(riders={})), ('담보 열쇠 없음', {k: v for k, v in EX.items() if k != 'riders'}),
         ('상품명 없음', mk(product='')), ('상품명 공백뿐', mk(product='  \n ')), ('상품명 None', mk(product=None)),
         ('schema 2', mk(schema=2)), ('schema 글자', mk(schema='1')), ('schema 1.0', mk(schema=1.0)), ('schema true', mk(schema=True)), ('schema null', mk(schema=None)), ('schema 목록', mk(schema=[1])),
         ('담보명 없음', mk(riders=[{'no': 1, 'amount': 1}])), ('담보가 글자', mk(riders=['x'])), ('담보명이 수', mk(riders=[{'no': 1, 'name': 123, 'amount': 100000}])),
         ('담보명이 사전', mk(riders=[{'no': 1, 'name': {}, 'amount': 100000}])),
         ('금액이 글자', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': '많이'}])), ('금액 음수', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': -1}])),
         ('금액 너무 큼', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': 1e12}])), ('금액 true', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': True}])),
         ('금액 목록', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': [1]}])), ('금액 쉼표 글자', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': '1,234,000원'}])),
         ('금액 소수', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': 1234500.5}])), ('금액 소수 글자', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': ' 250 000.5 '}])),
         ('금액 반올림 짝수', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': 200000.5}, {'no': 2, 'name': '상해수술비', 'amount': 200001.5}])),
         ('금액 5천원', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': 5000}, {'no': 2, 'name': '상해수술비', 'amount': 12345}, {'no': 3, 'name': '암진단비(유사암제외)', 'amount': 150000000}])),
         ('금액 빈 글자', mk(riders=R1 + [{'no': 2, 'name': '상해수술비', 'amount': ''}])), ('금액 null', mk(riders=R1 + [{'no': 2, 'name': '상해수술비', 'amount': None}])),
         ('미사용일당 글자', mk(riders=R1 + [{'no': 2, 'name': '갱신형 간병인지원 질병입원일당(Ⅰ)(1일이상 180일한도)', 'amount': 0, 'unused_daily': '2만'}])),
         ('나이가 글자', mk(insured={'name': 'x', 'sex': 'M', 'age': '마흔'})), ('나이 수', mk(insured={'name': 'x', 'sex': 'M', 'age': 45})), ('나이 0', mk(insured={'name': 'x', 'sex': 'M', 'age': 0})),
         ('나이 4자리', mk(insured={'name': 'x', 'sex': 'M', 'age': '1234'})), ('나이 소수', mk(insured={'name': 'x', 'sex': 'M', 'age': 45.0})),
         ('표기 받기', mk(premium='123,450원', insured={'name': '홍길동', 'sex': '여', 'age': '45세'})),
         ('성별 꼴', mk(insured={'name': ' 홍  길동 ', 'sex': 'f', 'age': ' 7 '})), ('성별 수', mk(insured={'name': '김', 'sex': 1, 'age': '30'})), ('성별 모름', mk(insured={'name': '김', 'sex': 'male', 'age': '30'})),
         ('insured 목록', mk(insured=[1])), ('insured 0', mk(insured=0)), ('insured 글자', mk(insured='x')), ('agent 글자', mk(agent='x')), ('agent 없음', {k: v for k, v in EX.items() if k != 'agent'}),
         ('insured 없음', {k: v for k, v in EX.items() if k != 'insured'}), ('표지 항목 다 없음', dict(product=EX['product'], riders=EX['riders'])),
         ('보험료 없음', mk(premium=None)), ('보험료 빈 글자', mk(premium='')), ('보험료 음수', mk(premium=-5)), ('보험료 글자', mk(premium='십만원')), ('보험료 소수', mk(premium=95530.5)),
         ('번호 글자', mk(riders=[{'no': 'abc', 'name': '질병수술비', 'amount': 200000}])), ('번호 소수', mk(riders=[{'no': 3.0, 'name': '질병수술비', 'amount': 200000}])),
         ('번호 글자 수', mk(riders=[{'no': '007', 'name': '질병수술비', 'amount': 200000}])), ('번호 null', mk(riders=[{'no': None, 'name': '질병수술비', 'amount': 200000}])),
         ('번호 true', mk(riders=[{'no': True, 'name': '질병수술비', 'amount': 200000}])), ('번호 음수', mk(riders=[{'no': -5, 'name': '질병수술비', 'amount': 200000}])),
         ('번호 없음', mk(riders=[{'name': '질병수술비', 'amount': 200000}, {'name': '상해수술비', 'amount': 200000}])), ('번호 7자리', mk(riders=[{'no': '1234567', 'name': '질병수술비', 'amount': 200000}])),
         ('글자 다듬기', mk(design_no=' AB-12 / 가나_다  ' + 'x' * 60, product=' (무)  메리츠\n통합간편건강보험(세만기형)2610 ', riders=[{'no': 1, 'name': '  질병수술비 \t (통합간편가입) ', 'amount': 200000, 'unit_code': ' U 1 ', 'code': 123}])),
         ('담보명 길다', mk(riders=[{'no': 1, 'name': '질병수술비' + '가' * 300, 'amount': 200000}] + R1[:0] + [{'no': 2, 'name': '상해수술비', 'amount': 100000}])),
         ('가계약번호 없음', mk(design_no='')), ('가계약번호 한글', mk(design_no='가나다')), ('가계약번호 수', mk(design_no=20261125001)),
         ('담보 2001개', mk(riders=[{'no': i, 'name': '질병수술비', 'amount': 200000} for i in range(2001)])),
         ('대괄호가 안 닫힌 이름', mk(riders=R1 + [{'no': 2, 'name': '암진단비[유사암제외', 'amount': 1000000}, {'no': 3, 'name': '수술비[', 'amount': 1000000}, {'no': 4, 'name': '](', 'amount': 1000000}, {'no': 5, 'name': '()', 'amount': 1000000}, {'no': 6, 'name': '암진단비(유사암제외))', 'amount': 1000000}, {'no': 7, 'name': '((암))', 'amount': 1000000}, {'no': 8, 'name': '[질병3종]', 'amount': 100000}])),
         ('전부 모르는 담보', mk(riders=[{'no': 1, 'name': '세상에 없는 담보 가', 'amount': 1000000}, {'no': 2, 'name': '세상에 없는 담보 나', 'amount': 1000000}])),
         ('전부 금액 0', mk(riders=[{'no': 1, 'name': '질병수술비', 'amount': 0}])),
         ('부모 줄 · 금액 0 · 중복', mk(riders=EX['riders'] + [{'no': 21, 'name': '수술비(1-7종, 연간3회한)[질병4-7종](통합간편가입)', 'amount': 1000000}, {'no': 22, 'name': '질병수술비(통합간편가입)', 'amount': 0}, {'no': 5, 'name': '질병수술비(통합간편가입)', 'amount': 200000}])),
         ('1-7종 꼴', mk(riders=[{'no': 1, 'name': '(20년갱신) 갱신형 수술비[질병3종]', 'amount': 300000}, {'no': 2, 'name': '갱신형 수술비(1-7종, 연간3회한)[상해7종](통합간편가입)', 'amount': 5000000},
                                {'no': 3, 'name': '수술비[질병1종](출생전)', 'amount': 100000}, {'no': 4, 'name': '수술비[질병4종]', 'amount': 0}, {'no': 5, 'name': '[기본계약]수술비(1-7종, 연간3회한)[질병5종][특별조건부]', 'amount': 1000000},
                                {'no': 6, 'name': '수술비Ⅱ(1-5종)[질병2종]', 'amount': 500000}, {'no': 7, 'name': '수술비 [ 상해 3종 ]', 'amount': 250000}, {'no': 8, 'name': '(3년갱신)수술비(1-7종,연간3회한)[상해4종](편한가입)', 'amount': 1234000}])),
         ('간병인 꼴', mk(product=TH, riders=[{'no': 1, 'name': '갱신형 간병인지원 질병입원일당(Ⅰ)(1일이상 180일한도)(통합간편가입)', 'amount': 0, 'unused_daily': 20000},
                                {'no': 2, 'name': '갱신형 간병인지원 질병입원일당(Ⅵ)(1일이상 180일한도)(통합간편가입)', 'amount': 0}, {'no': 3, 'name': '갱신형 간병인지원 질병입원일당(Ⅰ)(181일이상)(통합간편가입)', 'amount': 30000},
                                {'no': 4, 'name': '갱신형 간병인지원 질병입원일당(간호간병통합서비스사용추가보장)(1일이상180일한도)(통합간편가입)', 'amount': 15000},
                                {'no': 5, 'name': '갱신형 간병인사용 질병입원일당(1일이상 180일한도)(요양병원제외)(통합간편가입)', 'amount': 150000}, {'no': 6, 'name': '갱신형 간병인사용 질병입원일당(1일이상 180일한도)(요양병원)(통합간편가입)', 'amount': 50000},
                                {'no': 7, 'name': '간호ㆍ간병통합서비스 사용 질병입원일당(1일이상 180일한도)(통합간편가입)', 'amount': 70000}, {'no': 8, 'name': '간호간병통합서비스 사용 질병입원일당(181일이상)(요양,정신,한방병원제외)(통합간편가입)', 'amount': 70000},
                                {'no': 9, 'name': '갱신형 간병인지원 요양성특정질병입원일당(1일이상 180일한도)(요양병원)(통합간편가입)', 'amount': 0, 'unused_daily': 5000}, {'no': 10, 'name': '질병수술비(통합간편가입)', 'amount': 200000}])),
         ('간병인 지원만 · 미사용 5천', mk(product=TH, riders=[{'no': 1, 'name': '갱신형 간병인지원 질병입원일당(Ⅶ)(1일이상 180일한도)(통합간편가입)', 'amount': 5000}, {'no': 2, 'name': '질병수술비(통합간편가입)', 'amount': 200000}])),
         ('간병인 없음', mk(product=TH, riders=[{'no': 2, 'name': '질병수술비(통합간편가입)', 'amount': 200000}])),
         ('가운뎃점 있음', mk(product=TH, riders=[{'no': i + 1, 'name': n, 'amount': 70000} for i, n in enumerate(['간호·간병통합서비스 사용 질병입원일당(1일이상 180일한도)(통합간편가입)', '간호·간병통합서비스 사용 질병입원일당(181일이상)(요양,정신,한방병원제외)(통합간편가입)'])])),
         ('가운뎃점 없음', mk(product=TH, riders=[{'no': i + 1, 'name': n, 'amount': 70000} for i, n in enumerate(['간호간병통합서비스사용질병입원일당(1일이상180일한도)(통합간편가입)', '간호간병통합서비스 사용 질병입원일당(181일이상)(요양,정신,한방병원제외)(통합간편가입)'])])),
         ('고지 구분자만(상품명 모름)', mk(product='(무) 이름을 모르는 상품')), ('상품명 모름 · 구분자 없음', mk(product='(무) 이름을 모르는 상품', riders=R1)),
         ('제외 상품 시험용 이름', mk(product='무배당 메리츠 시험용 제외상품2610')),
         ]
    alt = copy.deepcopy(EX)
    for r in alt['riders']:
        if r['no'] in (7, 8, 9): r['name'] = r['name'].replace('수술비(1-7종, 연간3회한)', '수술비')
        if r['no'] == 10: r['name'] = '수술비(1-7종, 연간3회한)[상해2종](통합간편가입)'
        if r['no'] in (1, 3): r['name'] = '[기본계약]' + r['name'].replace('(통합간편가입)', '(편한가입)')
    B.append(('이름 꼴 바꿈', alt))
    for n, o in B: add('B:' + n, o)
    for prod in ['(무) 메리츠 통합간편건강보험(연만기형)2610(355입원,수술고지간편심사형)', '(무) 내Mom대로 보장보험2610 (해약환급금지급형)', '(무) 메리츠 The건강한 내Mom대로 5.10.5 보장보험2610', '(무) 메리츠 The건강한 5.10.5 보장보험2610',
                 '(무) 메리츠 The좋은 내Mom대로 보장보험2610', '(무) The가벼운 간편355건강보험(세만기형)2610', '(무) 메리츠 간편31 건강보험2610', '(무) 내Mom같은 어린이보험2610(태아전용)', '(무) 메리츠 The좋은 알파Plus보장보험2610',
                 '(무) 알파Plus보장보험2610', '(무) 메리츠 케어프리보험 M-Basket2610', '무배당 올케어 꽉 채운 수술비보험(세만기형)2610(통합간편고지형)', '(무) Only You 통합보험2610(355간편고지형)', '(무) onlyyou 통합보험2610', PH, PE,
                 '(무) 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(맞춤간편심사형)', '무배당 올케어 보장 꽉 채운 암보험(세만기형)2610(맞춤간편심사형)', '무배당 올케어 꽉 채운 뇌심보험(연만기형)2610(맞춤간편심사형)', '무배당 메리츠 성공파트너 종합보험2610', '무배당 메리츠 상해안심보험2610', '(무) 메리츠 운전자 상해 종합보험2610', '(무) 메리츠 이목구비 치아보험2601']:
        add('B:상품 라인 ' + prod, mk(product=prod, riders=R1))
    # 담보 식별표로 찾기(이름으로 못 찾았을 때만) — 시험용 식별표
    tmp = os.path.join(out_dir, 'tmp_code_map.json')
    json.dump({'schema': 1, 'note': '시험용', 'map': {'X0000|000099': {'id': '통95', 'p': '통합간편'}, 'X0000|000098': {'id': '통1', 'p': '통합간편'}, 'X0000|000097': {'id': '없는id', 'p': '통합간편'}}}, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    add('B:시험용 식별표', mk(riders=EX['riders'][:4] + [{'no': 99, 'unit_code': 'X0000', 'code': '000099', 'name': '질병 수술 보장(정보계에서 이름이 바뀐 경우)', 'amount': 200000},
                                                       {'no': 98, 'unit_code': 'X0000', 'code': '000098', 'name': '질병수술비(통합간편가입)', 'amount': 200000}, {'no': 97, 'unit_code': 'X0000', 'code': '000097', 'name': '어디에도 없는 담보', 'amount': 200000},
                                                       {'no': 96, 'unit_code': '', 'code': '000099', 'name': '단위상품코드가 없는 줄', 'amount': 200000}]), tmp)
    # C. 담보 하나짜리 설계(check_code_input.py 5~10 의 사례)
    S1 = [('무배당 메리츠 The좋은 케어프리보험 M-Basket2610', pre + nm, 10000000) for pre in ('', '갱신형 ') for nm in ('암치료,후유장해및진단비[암진단비(유사암제외)]', '암후유장해및진단비[암진단비(유사암제외)]')]
    S1 += [(TH, n, 10000000) for n in ('암 통합생활지원비(월간한도)(통합간편가입)', '2대질환 통합생활지원비(월간한도)(통합간편가입)')]
    S1 += [('무배당 올케어 꽉 채운 수술비보험(세만기형)2610(일반고지형)', '종합병원 전신마취(1시간초과) 수술비(1-7종,연간3회한)[질병]', 10000000), (PB, '중증뇌경색증진단비', 10000000)]
    S1 += [(PB, n, 10000000) for n in ('뇌경색증진단비', '뇌혈관질환관혈수술비(연간1회한)', '심장관련질환관혈수술비(연간1회한)', '혈전용해치료비Ⅲ(연간1회한)', '기계적혈전제거술(카테터법)치료비Ⅲ(급여, 연간1회한)',
                                       '중등증이상허혈성심장질환진단비', '2대질환 중증치료비(급여,연간1회한)[2대질환 지속적신대체요법(CRRT)치료비(급여,연간1회한)]', '뇌경색증진단 응급환자 응급실내원비(연간1회한)')]
    S1 += [(PO, n, 10000000) for n in ('치핵수술비(355간편가입)', '관절염,생식기질환수술비(355간편가입)', '백내장수술비(355간편가입)', '유방의장애수술비(355간편가입)')]
    S1 += [(PG, '갱신형 척추질병수술비(연간1회한)(관혈,비관혈)', 10000000), (PG, '갱신형 상급종합병원 관절질환수술비(연간1회한)', 10000000), (PG, '갱신형 호흡기질병입원일당(1일이상180일한도)', 20000),
           (PG, '갱신형 회복기재활의료기관 골반대퇴골절입원일당(1일이상30일한도)', 10000000)]
    for prod, base in ((PH, '암진단비(유사암제외)'), (PH, '유사암진단비'), (PH, '질병수술비'), (PH, '암수술비(유사암제외)'), (PE, '뇌졸중진단비Ⅱ(355간편가입)'), (PE, '혈전용해치료비Ⅱ(뇌졸중)(연간1회한)(355간편가입)')):
        S1 += [(prod, base, 10000000), (prod, base.replace('(355간편가입)', '') + T10 + ('(355간편가입)' if '(355간편가입)' in base else ''), 10000000)]
    for i, (prod, nm, won) in enumerate(S1): add('C:%02d %s' % (i, nm[:40]), one(prod, nm, won))
    M = [('암후유장해 세트', dict(schema=1, product='무배당 The가벼운 간편355건강보험(세만기형)2610', riders=[{'no': 1, 'name': '암치료,후유장해및진단비[암후유장해(3-100%)](편한가입)', 'amount': 50000000}, {'no': 2, 'name': '암치료,후유장해및진단비[암80%이상후유장해](편한가입)', 'amount': 1000000},
                                {'no': 3, 'name': '암치료,후유장해및진단비[암진단비(유사암제외)](편한가입)', 'amount': 30000000}, {'no': 4, 'name': '암치료,후유장해및진단비[항암약물치료비](편한가입)', 'amount': 20000000}])),
         ('일반형 + 체증형', dict(schema=1, product=PH, riders=[{'no': 1, 'name': '암진단비(유사암제외)', 'amount': 10000000}, {'no': 2, 'name': '암진단비(유사암제외)' + T10, 'amount': 20000000}])),
         ('체증형 여럿', mk(product=PH, riders=[{'no': 1, 'name': '암진단비(유사암제외)', 'amount': 30000000}, {'no': 2, 'name': '암진단비(유사암제외)' + T10, 'amount': 20000000}, {'no': 3, 'name': '유사암진단비', 'amount': 6000000},
                                {'no': 4, 'name': '뇌혈관질환진단비Ⅱ', 'amount': 10000000}, {'no': 5, 'name': '뇌졸중진단비Ⅱ' + T10, 'amount': 10000000}, {'no': 6, 'name': '질병수술비' + T10, 'amount': 200000}])),
         ('상해진단및치료비', dict(schema=1, product=TH, riders=[{'no': i + 1, 'name': '상해진단및치료비[%s](통합간편가입)' % n, 'amount': a} for i, (n, a) in enumerate(
             [('경증및기타 상해진단비(연간1회한)', 30000), ('중등증 상해진단비(연간1회한)', 200000), ('중증 상해진단비(연간1회한)', 3000000), ('중등증 상해 근골 주요처치및수술비(급여,연간1회한)', 500000)])] + [{'no': 9, 'name': '상해진단및치료비(통합간편가입)', 'amount': 100000}])),
         ('항암치료비Ⅱ', dict(schema=1, product=TH, riders=[{'no': i + 1, 'name': n, 'amount': 10000000} for i, n in enumerate(
             ['%s[%s,%s%s](통합간편가입)' % (t_, ca, ca, su) for t_ in ('항암방사선치료비Ⅱ', '항암약물치료비Ⅱ') for ca in ('암(유사암제외)', '기타피부암', '갑상선암') for su in ('수술후제외', '수술후')])])),
         ('상해 통합치료비', dict(schema=1, product=TH, insured={'name': '김', 'sex': 'F', 'age': '40'}, riders=[{'no': 1, 'name': '상해 통합치료비(실속형)(통합간편가입)', 'amount': 15000000}, {'no': 2, 'name': '갱신형 상해 통합치료비(실속형)(통합간편가입)', 'amount': 12340000},
                                {'no': 3, 'name': '골절(치아파절제외)진단비Ⅱ(통합간편가입)', 'amount': 300000}, {'no': 4, 'name': '상해수술비(통합간편가입)', 'amount': 500000}])),
         ]
    for n, o in M: add('C:' + n, o)
    return C
