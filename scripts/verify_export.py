#!/usr/bin/env python3
"""
반출 파일 검증 — 문서(메리츠_보상메커니즘.md)만 보고 구현했을 때
도구·검수보고서와 같은 답이 나오는지 확인한다.
- 저장소 루트에서 실행: python3 scripts/verify_export.py
- 먼저 build_export.py 로 export/ 를 만들어 두어야 한다.
"""
# MD 문서만 보고 구현했을 때 도구와 같은 답이 나오는지 확인한다
import json, re
DB=json.load(open('/home/user/MeAI/export/메리츠_상품보상데이터.json',encoding='utf-8'))
R=DB['riders']; SYN=DB['synonyms']; AL=DB['aliases']

RANGE=re.compile(r'^([A-Z])(\d{2})(?:\.\d+)?\s*[~∼〜～\-–—]\s*([A-Z]?)(\d{2})')
def range_has(tok, code):
    tok=tok.upper(); m=RANGE.match(tok)
    if not m: return tok.split('.')[0]==code or tok==code
    l1,a,l2,b=m.group(1),int(m.group(2)),(m.group(3) or m.group(1)),int(m.group(4))
    cm=re.match(r'^([A-Z])(\d{2})', code)
    if not cm: return False
    L,n=cm.group(1),int(cm.group(2))
    if L<l1 or L>l2: return False
    if l1==l2: return a<=n<=b
    if L==l1: return n>=a
    if L==l2: return n<=b
    return True

def list_has(k, code, x):
    code=code.upper()
    if x and code in [c.upper() for c in x]: return False
    return any(range_has(t, code) or t.upper().split('.')[0]==code for t in (k or []))

def expand(lst, drop_sub):
    s=set()
    for t0 in (lst or []):
        t=str(t0).upper().strip()
        if drop_sub and '.' in t and not RANGE.match(t): continue
        m=RANGE.match(t)
        if m:
            l1,a,l2,b=m.group(1),int(m.group(2)),(m.group(3) or m.group(1)),int(m.group(4))
            if l1==l2: s.update(f'{l1}{n:02d}' for n in range(a,b+1))
            else:
                s.update(f'{l1}{n:02d}' for n in range(a,100)); s.update(f'{l2}{n:02d}' for n in range(0,b+1))
        else: s.add(t.split('.')[0])
    return s

def eff(r):
    K=expand(r.get('k'), False)
    return K - expand(r.get('x'), True)

def cov(r,c):
    C=str(c).upper().split('.')[0]
    if C not in eff(r): return 'n'
    return 'p' if any('.' in str(t).upper() and str(t).upper().split('.')[0]==C for t in (r.get('x') or [])) else 'y'

def is_quasi(c):
    C=str(c).upper().split('.')[0]
    if C in ('C44','C73'): return True
    m=re.match(r'^D(\d{2})$', C)
    return bool(m) and (int(m.group(1))<=9 or 37<=int(m.group(1))<=48)

def syn_codes(q):
    out=[]
    for k,v in SYN.items():
        if q in k: out+=v
    for k,v in AL.items():
        if q in k: out+=v
    return out

def search(q):
    qn=q.replace(' ','').lower(); hit=[]
    codes=syn_codes(q)
    for r in R:
        if qn and qn in r['n'].replace(' ','').lower(): hit.append((r,'이름')); continue
        if any(qn in str(s).replace(' ','').lower() for s in (r.get('s') or [])): hit.append((r,'태그')); continue
        if any(qn in str(l).replace(' ','').lower() for l in (r.get('l') or [])): hit.append((r,'질병명')); continue
        if re.match(r'^[A-Za-z]\d', q) and list_has(r.get('k'), q.upper(), r.get('x')): hit.append((r,'코드')); continue
        if codes and any(list_has(r.get('k'), c, r.get('x')) for c in codes): hit.append((r,'동의어')); continue
    return hit

EXC=re.compile(r'치아|치과|치조골|보철|임플란트|크라운|배상책임|벌금|변호사|법률|화재|가전|재물|운전|자동차|교통|면허|생활지원|산정특례')
def gen_kind(r):
    """문서 3.5 절 그대로 구현"""
    if (r.get('k') or []) or (r.get('s') or []): return None
    n=re.sub(r'\s+','',r.get('n') or '').replace('(치아파절및치아탈구제외)','')
    n=re.sub(r'\(특정\d+대질병제외\)','',n)
    if EXC.search(n): return None
    dz=('질병' in n) and not re.search(r'특정|대질병|요양성|다빈도|성인병|여성|남성',n)
    inj=('상해' in n) and not re.search(r'특정|골절|화상|깁스|성형|중대한',n)
    if dz and not inj: return 'dz'
    if inj and not dz: return 'inj'
    return None

def commons(kind):
    return [r for r in R if gen_kind(r)==kind]

print('═══ 검수보고서에 적힌 결과가 재현되는가 ═══\n')
# 1) 신장암 C64
h=[r for r,_ in search('신장암') if '통합암진단비' in r['n']]
print(f'① 신장암 → 통합암진단비 계열 {len(h)}건 (보고서: 9건 정확일치)')
print('   예:', '; '.join(r['n'][:34] for r in h[:3]))
# 2) 갑상선암
h=[r for r,_ in search('갑상선암')]
names=[r['n'] for r in h]
for want in ['유사암수술비','보험료납입지원','암직접치료입원일당']:
    print(f'② 갑상선암 → 「{want}」 포함: {any(want in n for n in names)}')
# 3) 협심증
h=[r['n'] for r,_ in search('협심증')]
for want in ['MRI','32대질병관혈수술비']:
    print(f'③ 협심증 → 「{want}」 포함: {any(want in n for n in h)}')
# 4) 위암 공통특약
print(f'④ 위암(질병코드) → 모든 질병 공통 특약 {len(commons("dz"))}건 (보고서: 120건)')
print(f'⑤ 골절(S·T 코드) → 모든 상해 공통 특약 {len(commons("inj"))}건 (보고서: 137건)')
# 6) C50 는 암진단비(유사암 및 소액암 제외) 에 안 잡혀야
tgt=[r for r in R if '암진단비(유사암 및 소액암 제외)' in r['n']]
print(f'⑥ 암진단비(유사암 및 소액암 제외) {len(tgt)}건 · C50 보장? '
      + str([cov(r,'C50') for r in tgt]) + '  (n 이어야 정상)')
# 7) 유사암 판정
print('⑦ 유사암 판정 : C44', is_quasi('C44'), '· C73', is_quasi('C73'),
      '· D47.1', is_quasi('D47.1'), '← 소수점을 떼고 보므로 True. 바로잡는 곳은 문서 4장 예외 2번')
# 8) 범위 기호 3종
print('⑧ 범위 기호 :', [range_has('I20∼I25','I21'), range_has('N17-N19','N18'), range_has('C00~C14','C07')],
      '(셋 다 True 여야 함)')
