# -*- coding: utf-8 -*-
"""담보명 정규화·매칭 + 상품설명서 가입담보리스트(표) 읽기"""
import collections, json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import scen_engine as S
DB = json.load(open(os.path.join(BASE, 'db.json'), encoding='utf-8'))
GOJI = S.GOJI                        # 고지유형 꼬리표는 rules.json goji_tags 한 곳에서만 관리(v8.3)
_A = '(?:' + S.AMT_RE + ')'          # 가입금액 표기(1억5천만원·3천5백만원·1억 등 전부)
RENEW = r'\((?:\d+년)?갱신\)'          # 설계서 표기 (20년갱신) → 마스터의 '갱신형'과 맞추기 위해 제거
def base(n): return re.sub(r'\s+', '', re.sub(RENEW, '', re.sub(GOJI, '', n)).replace('[기본계약]', '').replace('┗', ''))
PRE_REN = r'^갱신형'                  # 설계서 '갱신형 ○○' ↔ 마스터 '○○' 표기 차이(v8.20) — 양방향으로 한 번씩 다시 찾는다
INDEX = collections.defaultdict(list)
BRACK = collections.defaultdict(list)   # 부모 이름 → 세부급부([○○]) 레코드 — 설계서가 세부를 (○○) 괄호로 적는 경우 대비
for r in DB['riders']:
    k = base(r['n']); INDEX[k].append(r)
    if k.endswith(']'): BRACK[re.sub(r'\[[^\[\]]+\]$', '', k)].append(r)

CHILD = collections.defaultdict(list)    # 부모 id → 세부보장 레코드(id 가 '부모-n')(v8.61)
for r in DB['riders']:
    if '-' in r['id']: CHILD[r['id'].rsplit('-', 1)[0]].append(r)
_norm = lambda s: re.sub(r'[\s․·,]', '', s or '')

def _trail_groups(n):
    """이름 끝의 균형 잡힌 괄호 그룹을 뒤에서부터 떼어 낸다 → [(부모 후보, 꼬리 라벨), ...]
       '갱신형다빈치로봇암수술비(암(특정암제외))' → [('갱신형다빈치로봇암수술비', '암(특정암제외)')]"""
    out, rest = [], n
    while rest.endswith(')'):
        depth, i = 0, len(rest) - 1
        while i >= 0:
            if rest[i] == ')': depth += 1
            elif rest[i] == '(':
                depth -= 1
                if depth == 0: break
            i -= 1
        if i < 0: break
        out.append((rest[:i], rest[i + 1:-1])); rest = rest[:i]
    return out

def _sub_pick(n, line):
    """설계서가 세부급부를 (○○) 괄호로 적은 담보 → 마스터의 그 세부보장 레코드(부모[○○] 또는 '○○진단비' 같은 자식)(v8.61).
       전에는 부모 레코드로 매칭되어 부모의 KCD·제외코드를 받았다 — 「다빈치로봇 암수술비(특정암)」이 모든 암 코드를,
       「4대양성종양진단비Ⅱ(대장 양성종양및특정용종)」이 4개 세부 코드를 전부 갖게 되어 한 진단에 세부 여러 개가 함께 지급됐고,
       「암 주요치료비(…)(암(유사암제외))」는 부모(제외코드 없음)로 매칭되어 갑상선암에도 지급됐다.
       라벨은 완전 일치를 먼저, 그다음 앞부분 일치('대장양성종양및특정용종' ↔ '대장양성종양및특정용종진단비')로 본다."""
    for parent, lab in _trail_groups(n):
        ps = INDEX.get(parent) or []
        if not ps:                                        # 설계서 'Ⅱ' 꼬리 등 표기 차이 — 앞부분이 같은 가장 긴 이름
            ks = [k for k in INDEX if k and (parent.startswith(k) or k.startswith(parent)) and any(CHILD.get(r['id']) for r in INDEX[k])]
            if ks: ps = INDEX[max(ks, key=len)]
        if line: ps = [r for r in ps if r['p'] == line] or ps
        kids = [k for r in ps for k in CHILD.get(r['id'], [])]
        if not kids: continue
        key = _norm(lab)
        def label(k):
            bk = base(k['n'])
            return _norm(re.search(r'\[([^\[\]]+)\]$', bk).group(1)) if bk.endswith(']') else _norm(bk)
        for test in (lambda l: l == key, lambda l: l.startswith(key)):
            hit = [k for k in kids if test(label(k))]
            if hit: return hit, lab
    return None, None

def _find(n, line):
    """정규화된 담보명 하나로 마스터를 찾는다. 반환 (후보목록, 대괄호세부, 끝괄호꼬리)"""
    b = s = None
    pick = lambda k: ([r for r in INDEX.get(k, []) if r['p'] == line] or INDEX.get(k, []))
    c = pick(n)
    if not c and '[' in n:
        b = re.search(r'\[([^\[\]]+)\]', n).group(1); c = pick(re.sub(r'\[[^\[\]]+\]', '', n))
    if not c:                           # (세부) 괄호 표기 → 세부보장 레코드(v8.61)
        hit, lab = _sub_pick(n, line)
        if hit: return hit, lab, None
    if not c and re.search(r'\([^()]+\)$', n):
        s = re.search(r'\(([^()]+)\)$', n).group(1); c = pick(re.sub(r'\([^()]+\)$', '', n))
    if not c: c = pick(re.sub(r'\([^()]*\)', '', n))
    if not c:                           # 설계서는 세부급부를 (특정소액암)처럼 괄호로, 마스터는 [특정소액암 …]처럼 대괄호로 적는 경우
        for g in re.findall(r'\(([^()]+)\)', n):
            cand = [r for r in BRACK.get(n.replace('(%s)' % g, '', 1), []) if g in base(r['n']).rsplit('[', 1)[-1]]
            if line: cand = [r for r in cand if r['p'] == line] or cand
            if cand: c, b = [cand[0]], g; break
    if not c:
        ks = [k for k in INDEX if k and (n.startswith(k) or k.startswith(n))]
        if ks: c = pick(max(ks, key=len))
    return c, b, s

def match(name, line=None):
    n = base(name)
    c, b, s = _find(n, line)
    if not c:                           # 정확히 일치하는 이름이 없을 때만 갱신형 표기를 떼거나 붙여 다시 찾는다
        alt = re.sub(PRE_REN, '', n) if re.match(PRE_REN, n) else '갱신형' + n
        c, b, s = _find(alt, line)
    return (c[0] if c else None), b, s

# ── 부모 담보 행(금액 칸이 '세부보장참조')과 그 아래 ┗ 세부 행 연결 (v8.61) ──────────────────
# 설계서는 1-7종 수술비를 「수술비(1-7종, 연간3회한)[질병1-3종]  세부보장참조」 부모 행과
# 「┗ 수술비[질병1종] 30만원」… 종별 세부 행으로 나눠 적는다. 마스터(db.json)에는 부모 특약
# (통74·통2·케68·케95·케2·케3·운61 「수술비(1-7종, 연간3회한)[질병/상해]」)만 있고 종별 행은 없다 —
# 약관 제1조 지급금액표의 「질병1종 수술비보장 보험가입금액 … 질병7종 …」 줄이 그 세부 행이다.
# 그래서 세부 행은 늘 미매칭으로 집계됐고(the510 137/151 · tonghap 113/127 · mom-new 57/74),
# 실제로는 규칙 surg_grade_1_7_row 가 잡아 지급 계산이 되고 있었다. 부모 행의 마스터를 세부 행에
# 물려 약관 근거(제외코드 x 포함)를 붙이고 matched=True · via=부모담보명 으로 표시한다.
SUBREF = re.compile(r'세부\s*보장\s*참조')
GRADE_RANGE = re.compile(r'\[(상해|질병)\d-\d종\]')      # [질병1-3종] · [상해4-7종] → 마스터 표기 [질병] · [상해]
def parent_master(name, line=None):
    """부모 행 담보명 → 마스터 레코드. 종 범위 표기를 마스터 표기로 바꿔 찾는다. 없으면 None"""
    m, _b, _s = match(GRADE_RANGE.sub(lambda g: '[%s]' % g.group(1), name), line)
    return m
def _link(row, parent, name):
    """┗ 세부 행에 부모 마스터를 물린다. 부모가 없거나 부모도 마스터에 없으면 그대로(matched False)"""
    if not parent or not parent.get('m') or not name.lstrip().startswith('┗'): return row
    pm = parent['m']
    row.update(cat=pm.get('c'), codes=pm.get('k') or [], excl=pm.get('x') or [], hc=pm.get('hc') or [],
               matched=True, via=parent['name'], via_id=pm.get('id'))
    return row
def read_proposal(pdf_path, line=None, max_pages=None):
    """가입담보리스트 표(세부보장 표 포함)를 셀 단위로 읽는다. 담보사항 상세 구간이 시작되기 전까지만 읽고,
       담보명 기준으로 중복을 없앤다(부모 담보의 '세부보장 참조' 행은 금액이 없어 제외)."""
    import pdfplumber
    rows, seen, no_seq = [], set(), 0
    parent = None                                   # 가장 최근의 '세부보장참조' 부모 행(v8.61) — 세부 행이 다음 쪽으로 넘어가도 유지
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages[:max_pages] if max_pages else pdf.pages
        for p in pages:
            t = p.extract_text() or ''
            if '가입담보 및 보장내용' in t.replace(' ', '') or '가입담보및보장내용' in t.replace(' ', ''): break   # 담보사항 상세 시작
            for tb in p.extract_tables():
                for r in tb:
                    cells = [(c or '').replace('\n', '') for c in r]
                    idx = [i for i, c in enumerate(cells) if re.fullmatch(r'\d{1,3}', c.strip())]
                    if not idx or idx[0] + 3 >= len(cells): continue
                    i = idx[0]; no = int(cells[i]); name = cells[i+1].strip(); amt = cells[i+2].strip()
                    if not name or len(name) > 110 or '보험기간' in name: continue
                    am = re.match(_A, amt)
                    if not am:
                        if SUBREF.search(amt):                                                # 부모 행(금액 없음) — 아래 ┗ 세부 행의 약관 근거로 쓴다(v8.61)
                            parent = {'name': re.sub(GOJI, '', name).strip(), 'm': parent_master(name, line)}
                        elif '원' in amt and len(name) >= 3 and '보험료' not in name:      # 번호·담보명은 있는데 금액을 못 읽은 행 → 로그(v8.3)
                            S.log('검토필요', name, '가입금액 표기 "%s" 인식 실패 — 담보 리스트에서 제외 (금액 파서 보강 필요)' % amt)
                        continue
                    if not name.lstrip().startswith('┗'): parent = None                  # ┗ 가 아닌 일반 행이 오면 부모 구간이 끝난 것
                    key = (no, S.nname(name))            # 번호+담보명 — 갱신주기만 다른 같은 이름 담보가 병합되지 않게(v8.3)
                    if key in seen: continue
                    seen.add(key); m, b, s2 = match(name, line); no_seq += 1
                    row = {'no': no, 'name': re.sub(GOJI, '', name).replace('[기본계약]', '').strip(),
                           'man': S.amt_to_man(am.group(0)), 'amount_text': amt, 'cat': (m or {}).get('c'),
                           'codes': (m or {}).get('k') or [], 'excl': (m or {}).get('x') or [], 'hc': (m or {}).get('hc') or [], 'benefit': b, 'sub': s2, 'matched': bool(m),
                           'itc': S.itc_id(name)}
                    rows.append(row if m else _link(row, parent, name))
            if '세부보장' in t:                                    # 세부보장 표 : 번호+담보명이 한 셀에 있고 이름이 셀 경계에서 잘리므로 텍스트로 읽는다
                lines = [x.strip() for x in t.split('\n')]
                k = 0
                while k < len(lines):
                    mm = re.match(r'^(\d{1,3})\s+(.+?\[.+?)(?:\s+' + _A + r'.*)?$', lines[k])
                    if mm and '세부보장' not in lines[k] and '참조' not in lines[k] and '/' not in lines[k]:
                        no, name = int(mm.group(1)), mm.group(2); amt = ''; j = k + 1
                        am0 = re.search(_A, lines[k][len(mm.group(0).rstrip()):] or lines[k].replace(name, '', 1))
                        if am0: amt = am0.group(0)
                        while j < len(lines) and j <= k + 4:
                            am = re.search(_A, lines[j])
                            if am and not amt: amt = am.group(0)                           # 금액 줄(행 라벨이 앞에 붙기도 함)
                            elif not am and (name.count('[') > name.count(']') or name.count('(') > name.count(')')):
                                name += lines[j]                                                   # 잘린 이름 이어붙이기
                            j += 1
                        name = re.sub(r'\s+', ' ', name).strip()
                        key = (no, S.nname(name))
                        if amt and key not in seen and '[' in name and name.count('[') == name.count(']'):
                            seen.add(key); mt, b, s2 = match(name, line)
                            rows.append({'no': no, 'name': re.sub(GOJI, '', name).replace('[기본계약]', '').strip(),
                                         'man': S.amt_to_man(amt), 'amount_text': amt, 'cat': (mt or {}).get('c'),
                                         'codes': (mt or {}).get('k') or [], 'excl': (mt or {}).get('x') or [], 'benefit': b, 'sub': s2, 'matched': bool(mt),
                                         'itc': S.itc_id(name)})
                    k += 1
    return rows
