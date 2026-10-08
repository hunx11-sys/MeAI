# -*- coding: utf-8 -*-
"""GA 스마트 제안서 「간병인보장」 칸 — 계산이 아니라 설계서 담보를 읽어 채운다(ga_proposal · ga_spec 이 같이 쓴다 · v8.74).

간병인지원(현물지원)                                      — 「간병인지원 …입원일당」 특약(Ⅰ·Ⅵ·Ⅶ …)
  · 병·의원(요양병원제외) : 간병인지원 질병입원일당(1일이상 180일한도) 가입 → 「보내줌」 · 없으면 「미가입」
  · 요양병원             : 간병인지원 요양성특정질병입원일당(…)(요양병원) 가입 → 「보내줌」 · 없으면 「미가입」
  · 미사용시 1일          : 간병인을 쓰지 않고 입원했을 때 나오는 일당 = 설계서 금액란 숫자
                           Ⅰ 은 가입금액(입원일당) · Ⅶ 은 「간병인지원 또는 5천원」의 5천원(0.5만원) · Ⅵ 은 입원일당 조항이 없어 0
                           (소유자 지시 2026-10-08 · 약관 : Ⅶ 제1조 「입원 1일당 보험가입금액을 입원일당으로 지급, 간병인 지원 시 미지급」)
  · 간호간병통합서비스 1일 : 「…(간호·간병통합서비스 사용추가보장)」 가입금액 + 위 미사용 일당
                           (간호·간병통합서비스 병동은 간병인을 부를 수 없어 입원일당이 나온다 · 둘 다 없으면 「미가입」)
간병인사용(금액지원)                                      — 「간병인사용 …입원일당」 · 「간호·간병통합서비스 사용 …입원일당」 특약(정액)
  · 간병인 1일 / 요양병원 1일 / 간호간병통합서비스 1일 : 1일이상(180일한도) 담보 가입금액 합(181일이상 담보는 같은 담보가 없을 때만)
질병입원일당만 읽는다(상해 입원일당은 칸에 없다). 치매간병통합케어 상품의 '치매주요질환입원일당'은 '질병입원일당' 자리에서 읽고 「치매한정」을 붙인다.
금액·코드를 만들지 않는다 — 설계서에 적힌 숫자만 쓴다(CLAUDE.md 2)."""
import re

def won(v):
    """만원 → '1억 3,640' / '7,000' / '5.5'(일당처럼 소수점이 있는 금액)"""
    if v is None: return ''
    if abs(v - round(v)) > 1e-6: return ('%.1f' % v).rstrip('0').rstrip('.')
    v = int(round(v))
    if v == 0: return '0'
    eok, man = divmod(v, 10000)
    if eok and man: return '%d억 %s' % (eok, format(man, ','))
    if eok: return '%d억' % eok
    return format(man, ',')

def norm(riders):
    """치매 상품 간병인 담보를 같은 칸 규칙으로 읽기 위한 이름 치환 + 표시 플래그"""
    return [dict(r, name=r['name'].replace('치매주요질환입원일당', '질병입원일당'), dementia=('치매주요질환입원일당' in r['name'])) for r in riders]

_AMT = re.compile(r'또는\s*([\d.,]+)\s*(천원|만원|원)')
def daily(r):
    """간병인지원 입원일당 담보의 「간병인 미사용 시 입원일당」(만원) — 설계서 금액란에서만 읽는다"""
    if (r.get('man') or 0) > 0: return float(r['man'])
    m = _AMT.search(re.sub(r'\s+', '', r.get('amount_text') or ''))
    if not m: return 0.0
    v = float(m.group(1).replace(',', ''))
    return v / 10 if m.group(2) == '천원' else (v / 10000 if m.group(2) == '원' else v)

def _dz(rs):  return [r for r in rs if '질병입원일당' in r['name'] and '요양성' not in r['name']]
def _d180(rs): return [r for r in rs if '181일' not in r['name']]
def support(rs):      # 간병인지원 질병입원일당(Ⅰ·Ⅵ·Ⅶ …) 1일이상 — 현물 간병인
    return _d180([r for r in _dz(rs) if '간병인지원' in r['name'] and '간호·간병' not in r['name']])
def support_nh(rs):   # 간병인지원 요양성특정질병입원일당(…)(요양병원)
    return [r for r in rs if '간병인지원' in r['name'] and '요양성특정질병입원일당' in r['name'] and '(요양병원)' in r['name']]
def nurse_add(rs):    # 간병인지원 질병입원일당(간호·간병통합서비스 사용추가보장) 1일이상
    return _d180([r for r in _dz(rs) if '간병인지원' in r['name'] and '간호·간병통합서비스 사용추가보장' in r['name']])
def use(rs, kind):    # 간병인사용(금액지원) — 1일이상 담보, 없으면 181일 담보
    dz = _dz(rs)
    if kind == 'gen':   sel = [r for r in dz if '간병인사용' in r['name'] and '(요양병원)' not in r['name'] and '간호·간병' not in r['name']]
    elif kind == 'nh':  sel = [r for r in dz if '간병인사용' in r['name'] and '(요양병원)' in r['name']]
    else:               sel = [r for r in dz if '간호·간병통합서비스' in r['name'] and '간병인지원' not in r['name']]
    a = _d180(sel)
    return a if a else sel

def unused(rs):
    sp = support(rs)
    return (sum(daily(r) for r in sp), sp) if sp else (None, [])
def nurse_total(rs):
    a = nurse_add(rs); u, sp = unused(rs)
    if not a and u is None: return None, []
    return sum(r['man'] for r in a) + (u or 0), a + sp

def cells(riders):
    """칸 값(표시용). 숫자(만원 · float) / None(미가입) / True·False(보내줌·미가입) 와 근거 담보 목록"""
    rs = norm(riders)
    u, u_rs = unused(rs); nt, nt_rs = nurse_total(rs)
    out = dict(hosp=(bool(support(rs)), support(rs)), nh=(bool(support_nh(rs)), support_nh(rs)), nurse=(nt, nt_rs), unused=(u, u_rs))
    for k in ('gen', 'nh', 'nurse'):
        sel = use(rs, k); out['use_' + k] = ((sum(r['man'] for r in sel) if sel else None), sel)
    return out

def dementia(rs): return bool(rs) and all(r.get('dementia') for r in rs)
