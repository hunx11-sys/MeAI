# -*- coding: utf-8 -*-
"""담보코드 입력 — 전산이 넘기는 담보 목록(JSON)을 「설계서 PDF 를 읽은 것」 과 같은 모양으로 바꾼다(v9.06).

사내 전산은 가입설계의 담보를 「단위상품코드 + 담보코드 + 상품담보명 + 가입금액」 으로 가지고 있다. 이 모듈은 그 목록을
설계서 읽기(matcher.read_proposal)가 내는 담보 줄과 똑같은 꼴로 만든다. 그 뒤의 계산(scen_engine · ga_spec) · 지면(ga_v2)은
설계서 PDF 로 들어왔을 때와 한 글자도 다르지 않다 — 계산 길이 하나뿐이다.

입력(JSON) — schema 1
{
  "schema": 1,
  "design_no": "가계약번호",                       # 표지 · 머리줄
  "product": "(무) 메리츠 ○○보험2610 (…)",          # 상품명 원문(상품 라인 판정 · 표지)
  "premium": 95530,                                 # 월 보험료(원)
  "insured": {"name": "홍길동", "sex": "M", "age": 28},      # sex : M / F · age : 보험나이
  "agent": {"org": "○○본부", "code": "12345", "name": "김메리", "mobile": "010-0000-0000", "tel": "02-0000-0000"},
  "riders": [
    {"no": 1, "unit_code": "A1234", "code": "630123", "name": "상품담보명(정보계 원문 그대로)", "amount": 10000000},
    {"no": 2, "unit_code": "A1234", "code": "630456", "name": "수술비(1-7종, 연간3회한)[질병3종](편한가입)", "amount": 300000},
    {"no": 3, "unit_code": "A1234", "code": "640001", "name": "간병인지원 질병입원일당(Ⅰ)(1일이상 180일한도)", "amount": 0, "unused_daily": 20000}
  ]
}
· name   : 정보계 상품담보명 원문. 고지 구분자((○○가입)) · [기본계약] · (N년갱신) · [특별조건부] 가 붙어 있어도 된다 — 엔진이 뗀다.
           엔진은 담보명에서 조건(원인 · 병원 종별 · 종 · 일수 · 연간1회한)을 읽으므로 **이름을 줄이거나 바꾸지 않는다.**
· amount : 가입금액(원). 금액이 없는 부모 줄(「세부보장 참조」)은 넘기지 않아도 되고, 넘겨도 계산하지 않는다.
· 1-7종 수술비 세부보장은 종마다 한 줄씩(이름에 [질병3종] · [상해1종]). 「수술비[질병3종]」 처럼 부모 이름이 없는 꼴도 받는다.
· 간병인지원 입원일당(현물) : amount 0, 「간병인 미사용 시 입원일당」 이 있으면 unused_daily(원).

담보 찾기 : ① 담보명으로 특약 마스터를 찾는다(설계서 PDF 와 같은 길) → ② 못 찾으면 담보 식별표(단위상품코드 + 담보코드 → 특약 마스터 ID ·
code_map.json · 사내 자료라 저장소에 없음 · 환경변수 GA_CODE_MAP 또는 이 폴더)로 찾는다 → ③ 그래도 없으면 계산 제외 + 로그(빈칸).
둘 다 찾았는데 약관 자료(질병코드 · 제외코드 · 수가코드)가 다르면 ①을 쓰고 로그에 남긴다.
"""
import os, re, json, time
import scen_engine as S, matcher, build_all as BA

BASE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = 1

class InputError(ValueError):
    """입력 JSON 이 사양과 다름 — 메시지는 호출한 쪽에 그대로 보여 줄 쉬운 말"""

# ── 담보 식별표(있으면) ──
_CM = None
def code_map():
    """{'단위상품코드|담보코드': {'id': 특약 마스터 ID, 'p': 상품}} — scripts/codemap/export_code_map.py 가 만든다. 없으면 빈 표(이름으로만 찾는다)"""
    global _CM
    if _CM is None:
        p = os.environ.get('GA_CODE_MAP') or os.path.join(BASE, 'code_map.json')
        _CM = {}
        if os.path.exists(p):
            d = json.load(open(p, encoding='utf-8')); _CM = d.get('map') or {}
            _CM['_meta'] = {k: v for k, v in d.items() if k != 'map'}
    return _CM
_REC = None
def master(p, i):
    global _REC
    if _REC is None:
        _REC = {}
        for f in ('db.json', 'db_terms_extra.json'):
            fp = os.path.join(BASE, f)
            if os.path.exists(fp):
                for r in json.load(open(fp, encoding='utf-8')).get('riders') or []: _REC[(r.get('p'), r['id'])] = r
    return _REC.get((p, i))

# ── 입력 점검 ──
def _txt(v, n=200): return re.sub(r'\s+', ' ', str(v if v is not None else '')).strip()[:n]
def _won(v, where):
    if v is None or v == '': return 0
    if isinstance(v, bool): raise InputError('%s : 금액은 숫자(원)여야 합니다' % where)
    if isinstance(v, (int, float)): w = v
    else:
        s = re.sub(r'[,\s원]', '', str(v))
        if not re.fullmatch(r'\d+(\.\d+)?', s): raise InputError('%s : 금액 「%s」 을 숫자(원)로 읽지 못했습니다' % (where, _txt(v, 30)))
        w = float(s)
    if w < 0 or w > 1e11: raise InputError('%s : 금액 %s 원이 범위를 벗어났습니다' % (where, _txt(v, 30)))
    return int(round(w))
def parse(obj):
    """입력 JSON → 점검한 dict. 사양과 다르면 InputError"""
    if isinstance(obj, (bytes, str)):
        try: obj = json.loads(obj)
        except Exception as e: raise InputError('JSON 으로 읽지 못했습니다 : %s' % e)
    if not isinstance(obj, dict): raise InputError('맨 바깥은 { } 여야 합니다')
    if obj.get('schema') not in (None, SCHEMA): raise InputError('schema %s 는 지원하지 않습니다(지금 %d)' % (obj.get('schema'), SCHEMA))
    rs = obj.get('riders')
    if not isinstance(rs, list) or not rs: raise InputError('riders(담보 목록)가 비어 있습니다')
    if len(rs) > 2000: raise InputError('riders 가 %d개 — 한 설계의 담보로는 너무 많습니다' % len(rs))
    ins = obj.get('insured') or {}; ag = obj.get('agent') or {}
    if not isinstance(ins, dict) or not isinstance(ag, dict): raise InputError('insured · agent 는 { } 여야 합니다')
    sex = _txt(ins.get('sex'), 4).upper()
    sex = {'M': 'M', 'F': 'F', '남': 'M', '여': 'F', '남자': 'M', '여자': 'F', '1': 'M', '2': 'F'}.get(sex, '')
    age = _txt(ins.get('age'), 6).replace('세', '')
    if age and not re.fullmatch(r'\d{1,3}', age): raise InputError('insured.age 「%s」 는 숫자(보험나이)여야 합니다' % age)
    out = dict(schema=SCHEMA, design_no=_txt(obj.get('design_no'), 40), product=_txt(obj.get('product'), 200), premium=_won(obj.get('premium'), 'premium'),
               insured=dict(name=_txt(ins.get('name'), 30), sex=sex, age=age),
               agent=dict(org=_txt(ag.get('org'), 40), code=_txt(ag.get('code'), 20), name=_txt(ag.get('name'), 20), mobile=_txt(ag.get('mobile'), 20), tel=_txt(ag.get('tel'), 20)),
               riders=[])
    if not out['product']: raise InputError('product(상품명)가 없습니다 — 상품 라인을 정하는 데 씁니다')
    for i, r in enumerate(rs, 1):
        if not isinstance(r, dict): raise InputError('riders %d번째 : { } 여야 합니다' % i)
        nm = _txt(r.get('name'), 160)
        if not nm: raise InputError('riders %d번째 : name(상품담보명)이 없습니다' % i)
        no = r.get('no', i)
        if not (isinstance(no, int) and not isinstance(no, bool)) and not re.fullmatch(r'\d{1,6}', str(no)): raise InputError('riders %d번째 : no 「%s」 는 숫자여야 합니다' % (i, _txt(no, 20)))
        out['riders'].append(dict(no=int(no), unit_code=_txt(r.get('unit_code'), 20), code=_txt(r.get('code'), 20), name=nm,
                                  amount=_won(r.get('amount'), 'riders %d번째 amount' % i), unused_daily=_won(r.get('unused_daily'), 'riders %d번째 unused_daily' % i)))
    return out

# ── 상품 라인 ──
def line_of(p):
    """특약 마스터의 상품 라인 — 설계서 PDF 와 같은 규칙(build_all.line_from_head · 상품명 글자)"""
    ln = BA.line_from_head(re.sub(r'\s+', '', p['product']))      # 상품명이 먼저다(넘겨받은 글자 그대로)
    if ln: return ln
    if any('통합간편가입' in r['name'] for r in p['riders']): return '통합간편'      # 상품명으로 못 정했을 때만 고지 구분자를 본다(build_all.guess_line 과 같은 보조 규칙)
    return '케어프리'

# ── 담보 줄 ──
def man_of(won):
    """원 → 만원. 만원 단위면 정수(설계서 읽기와 같은 꼴), 아니면 소수"""
    return won // 10000 if won % 10000 == 0 else won / 10000.0
def won_text(won):
    """세부내역 「가입금액」 표기용 — 설계서 글자 꼴(1천만원 · 30만원). 계산에는 쓰지 않는다"""
    m = man_of(won)
    if not m: return '%s원' % format(won, ',') if won else ''
    if isinstance(m, float): return '%s만원' % ('%.1f' % m).rstrip('0').rstrip('.')
    eok, r = divmod(m, 10000); cheon, r = divmod(r, 1000); baek, man = divmod(r, 100)
    s = ('%d억' % eok if eok else '') + ('%d천' % cheon if cheon else '') + ('%d백' % baek if baek else '') + ('%d' % man if man else '')
    return s + ('만원' if (cheon or baek or man) else '원')
G17 = re.compile(r'^(?P<pre>(?:\(\d+년갱신\))?\s*(?:갱신형\s*)?)수술비\s*(?:\(1-7종[^\[\]]*\))?\s*\[(?P<c>질병|상해)(?P<g>[1-7])종\]\s*(?:\(출생전\))?$')
def _clean(n): return re.sub(S.GOJI, '', n).replace('[기본계약]', '').strip()
def _row(no, name, won, line, unit, code, text=None):
    """설계서 읽기(matcher.read_proposal)가 만드는 줄과 같은 꼴 + 어떻게 찾았는지(how)"""
    m, b, s2 = matcher.match(name, line); how = 'name' if m else None
    cm = code_map().get('%s|%s' % (unit, code)) if unit and code else None
    if cm:
        cr = master(cm.get('p'), cm.get('id'))
        if cr and not m: m, how = cr, 'code'
        elif cr and m and (set(cr.get('k') or []), set(cr.get('x') or []), set(cr.get('hc') or [])) != (set(m.get('k') or []), set(m.get('x') or []), set(m.get('hc') or [])):
            S.log('검토필요', name, '담보 식별표의 특약(%s · %s)과 이름으로 찾은 특약(%s · %s)의 약관 자료가 다름 — 이름으로 찾은 것으로 계산' % (cm.get('id'), cm.get('p'), m.get('id'), m.get('p')))
    return {'no': no, 'name': _clean(name), 'man': man_of(won), 'amount_text': text if text is not None else won_text(won), 'cat': (m or {}).get('c'),
            'codes': (m or {}).get('k') or [], 'excl': (m or {}).get('x') or [], 'hc': (m or {}).get('hc') or [], 'benefit': b, 'sub': s2, 'matched': bool(m),
            'itc': S.itc_id(name), 'sub_rec': bool(m and '[' in (m.get('n') or '')), 'mname': (m or {}).get('n'), 'unit_code': unit, 'code': code, 'how': how}
def riders(p):
    """점검한 입력 → 담보 줄(설계서 읽기와 같은 꼴). p['_line'] 에 상품 라인을 적어 둔다"""
    line = p['_line'] = line_of(p); out = []; seen = set()
    for r in p['riders']:
        nm, won = r['name'], r['amount']; base = _clean(nm)
        if matcher.GRADE_RANGE.search(base.replace(' ', '')):      # 종 범위 부모 줄([질병4-7종]) — 금액은 종별 줄에 있다
            S.log('검토필요', nm, '종 범위 부모 줄 — 종별 세부 줄만 계산(이 줄은 건너뜀)'); continue
        k = (r['no'], S.nname(nm))
        if k in seen: S.log('검토필요', nm, '같은 번호 · 같은 이름 담보가 두 번 들어옴 — 한 번만 계산'); continue
        seen.add(k)
        g = G17.match(base)
        if g:
            # 1-7종 수술비 종별 줄 — 설계서는 「수술비(1-7종, 연간3회한)[질병1-3종] 세부보장참조」 부모 줄 아래 「┗ 수술비[질병3종] 30만원」 으로 적는다.
            # 정보계는 「수술비(1-7종, 연간3회한)[질병3종]」 또는 「수술비[질병3종]」 한 줄이다 → 설계서와 같은 꼴(┗ 줄 + 부모 특약)로 바꾼다
            if not won: S.log('검토필요', nm, '가입금액이 0 — 계산하지 않음'); continue
            pre = re.sub(r'\(\d+년갱신\)\s*', '', g.group('pre')).strip(); pre = (pre + ' ') if pre else ''
            pname = '%s수술비(1-7종, 연간3회한)[%s%s종]' % (pre, g.group('c'), '1-3' if int(g.group('g')) <= 3 else '4-7')
            child = '┗ %s수술비[%s%s종]' % (pre, g.group('c'), g.group('g'))
            row = {'no': r['no'], 'name': child, 'man': man_of(won), 'amount_text': won_text(won), 'cat': None, 'codes': [], 'excl': [], 'hc': [], 'benefit': '%s%s종' % (g.group('c'), g.group('g')),
                   'sub': None, 'matched': False, 'itc': S.itc_id(child), 'sub_rec': False, 'mname': None, 'unit_code': r['unit_code'], 'code': r['code'], 'how': None}
            row = matcher._link(row, {'name': pname, 'm': matcher.parent_master(pname, line)}, child)
            row['how'] = 'name' if row.get('matched') else None
            out.append(row); continue
        if '간병인지원' in base and '사용추가보장' not in base:      # 현물(간병인을 보내 줌) — 설계서 금액 칸은 「간병인지원」 또는 「간병인지원 또는 2만원」(미사용 시 입원일당)
            ud = r['unused_daily'] or won
            out.append(_row(r['no'], nm, 0, line, r['unit_code'], r['code'], text='간병인지원' + ((' 또는 ' + won_text(ud)) if ud else ''))); continue
        if not won:
            S.log('검토필요', nm, '가입금액이 0 — 부모 줄(세부보장 참조)이거나 금액이 빠진 담보 · 계산하지 않음'); continue
        out.append(_row(r['no'], nm, won, line, r['unit_code'], r['code']))
    if not out or S.recog(out)['계산제외'] >= len(out):
        import pipeline
        raise pipeline.DesignUnreadable('담보 %d건을 받았지만 특약 마스터 · 규칙표에서 하나도 찾지 못했습니다(상품 : %s). 아직 등록하지 않은 상품 · 약관이거나 담보명이 정보계 원문과 다를 수 있습니다.' % (len(p['riders']), p['product']))
    return out

# ── 표지 · 머리줄 ──
def meta(p):
    """build_all.auto_meta 와 같은 열쇠"""
    return dict(insured=p['insured']['name'] or '고객', premium=(format(p['premium'], ',') + '원') if p['premium'] else '', product=p['product'],
                head='', agent=' '.join(x for x in (p['agent']['org'], p['agent']['name']) if x), issued='', sex=p['insured']['sex'])
def head(p, age=''):
    """ga_proposal.ga_head 와 같은 열쇠 — 넘겨받은 글자 그대로(없으면 빈칸 + 로그)"""
    ins, ag = p['insured'], p['agent']; a = age or ins['age']
    if a and not a.endswith('세'): a += '세'
    h = dict(name=ins['name'], sex={'F': '여자', 'M': '남자'}.get(ins['sex'], ''), age=a, no=p['design_no'], agent=' '.join(x for x in (ag['org'], ag['name']) if x),
             org=ag['org'], agent_name=ag['name'], mobile=ag['mobile'], tel=ag['tel'], code=ag['code'])
    missing = [k for k, v in (('피보험자 이름', h['name']), ('성별', h['sex']), ('보험나이', h['age']), ('가계약번호', h['no']), ('컨설턴트 소속', h['org']), ('컨설턴트 이름', h['agent_name'])) if not v]
    if missing: S.ISSUES.append({'구분': '표지', '담보': '-', '사유': '입력에 없는 표지 항목 : ' + ' · '.join(missing) + ' (빈칸 「-」으로 둠)'})
    return h
def tag(p):
    """산출물 파일 이름용(ASCII)"""
    a = re.sub(r'[^A-Za-z0-9_-]+', '', p.get('design_no') or '')
    return 'code_' + (a[-24:] if a else time.strftime('%Y%m%d_%H%M%S'))
def label(p): return '담보코드 입력 · 가계약번호 %s · 담보 %d건' % (p.get('design_no') or '-', len(p['riders']))
