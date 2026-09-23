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

def _find(n, line):
    """정규화된 담보명 하나로 마스터를 찾는다. 반환 (후보목록, 대괄호세부, 끝괄호꼬리)"""
    b = s = None
    pick = lambda k: ([r for r in INDEX.get(k, []) if r['p'] == line] or INDEX.get(k, []))
    c = pick(n)
    if not c and '[' in n:
        b = re.search(r'\[([^\[\]]+)\]', n).group(1); c = pick(re.sub(r'\[[^\[\]]+\]', '', n))
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
def read_proposal(pdf_path, line=None, max_pages=None):
    """가입담보리스트 표(세부보장 표 포함)를 셀 단위로 읽는다. 담보사항 상세 구간이 시작되기 전까지만 읽고,
       담보명 기준으로 중복을 없앤다(부모 담보의 '세부보장 참조' 행은 금액이 없어 제외)."""
    import pdfplumber
    rows, seen, no_seq = [], set(), 0
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
                        if '원' in amt and len(name) >= 3 and '보험료' not in name:      # 번호·담보명은 있는데 금액을 못 읽은 행 → 로그(v8.3)
                            S.log('검토필요', name, '가입금액 표기 "%s" 인식 실패 — 담보 리스트에서 제외 (금액 파서 보강 필요)' % amt)
                        continue
                    key = (no, S.nname(name))            # 번호+담보명 — 갱신주기만 다른 같은 이름 담보가 병합되지 않게(v8.3)
                    if key in seen: continue
                    seen.add(key); m, b, s2 = match(name, line); no_seq += 1
                    rows.append({'no': no, 'name': re.sub(GOJI, '', name).replace('[기본계약]', '').strip(),
                                 'man': S.amt_to_man(am.group(0)), 'amount_text': amt, 'cat': (m or {}).get('c'),
                                 'codes': (m or {}).get('k') or [], 'excl': (m or {}).get('x') or [], 'hc': (m or {}).get('hc') or [], 'benefit': b, 'sub': s2, 'matched': bool(m),
                                 'itc': S.itc_id(name)})
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
