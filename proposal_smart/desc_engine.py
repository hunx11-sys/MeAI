# -*- coding: utf-8 -*-
"""2차 안전장치 — 상품설명서의 담보별 약관 요약 설명을 읽어 지급조건을 뽑는다 (v8.22).

약관 데이터(db.json)에 없는 담보·규칙표에 없는 담보가 들어오면 지금까지는 '계산 제외 + 사유 로그'로만
끝났다. 그런데 상품설명서 뒤쪽 「가입담보 및 보장내용」에는 담보마다 약관을 요약한 지급사유 문장이 있다.

    162  6대심장질환진단비   1천만원  34,180  30년/100세
    보험기간 중 6대심장질환으로 진단확정되었을 때 최초 1회한 가입금액 지급
    ※ 6대심장질환 : ① 만성류마티스심장질환 ② 심장염증질환 …

이 문장에서 읽어내는 것은 **지급 구조**뿐이다.
    · 보상 유형(진단비/수술비/입원일당/치료비)
    · 지급 횟수(최초 1회한 / 연간 1회한 / 수술 1회당 …)
    · 지급 금액(가입금액 전액 / 가입금액의 N%)
    · 1년 이내 감액 여부
    · 조건 꼬리표(병원 종별·치료행위)

**질병코드는 이 문장에서 만들지 않는다.** 코드는 약관 별표에서만 온다(모듈 대원칙).
설명문에 열거된 질병명이 이미 보유한 그룹표(g131·kcd_groups) 이름과 정확히 같을 때만 그 표를 가리킨다.

쓰임 : 1차(약관 데이터) 판정이 안 되는 담보를 버리지 않고 ①감사 로그에 지급조건을 남기고
       ②규칙표에 넣을 후보를 제안한다. 금액 계산에 바로 쓰지는 않는다(코드가 없으면 대상 판정이 불가능).
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

# ── 상품설명서에서 담보별 설명문 읽기 ─────────────────────────────
HEAD = re.compile(r'가입담보\s*및\s*보장내용')
ROW = re.compile(r'^(\d{1,3})\s{2,}(.+)$')          # '162   6대심장질환진단비'
AMT = re.compile(r'^[\d,]+\s*(원|만원)$|^\d[\d,]*(천|백|십)?만원$|^\d+억')
SKIPLINE = re.compile(r'^(\[고객용\]|계약사항|담보사항|가입담보|가입금액|보험료|납기|기본계약|선택계약|'
                      r'영업담당자|발행정보|고객콜센터|www\.|page\s*:|※ 인수지침|설계번호)')


def read_desc(pdf_path):
    """상품설명서 → {담보번호(int): {'name':…, 'desc':…}}  — 「가입담보 및 보장내용」 구간만 읽는다."""
    import pdfplumber
    out, cur, started = {}, None, False
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ''
            if HEAD.search(t.replace(' ', '')) or HEAD.search(t):
                started = True
            if not started:
                continue
            for raw in t.split('\n'):
                line = raw.rstrip()
                s = line.strip()
                if not s or SKIPLINE.match(s):
                    continue
                m = ROW.match(line) or re.match(r'^(\d{1,3})\s+([^\d\s].{2,90})$', s)
                if m and not AMT.match(m.group(2).strip()):
                    no = int(m.group(1))
                    cur = {'name': m.group(2).strip(), 'desc': ''}
                    out[no] = cur
                    continue
                if cur is None:
                    continue
                if AMT.match(s) or re.fullmatch(r'\d+\s*년\s*/\s*\d+\s*세', s) or re.fullmatch(r'[\d,]+', s):
                    continue                                   # 가입금액·보험료·납기 칸
                cur['desc'] += (' ' if cur['desc'] else '') + s
    for v in out.values():
        v['desc'] = tidy(v['desc'])
    out = split_sub(out)
    return {k: v for k, v in out.items() if v['desc']}


# 설명문 한가운데로 끼어드는 표 칸(가입금액·보험료·납기)을 걷어낸다 — PDF 열 순서 때문에 섞인다
JUNK = re.compile(r'\s*\d[\d,]*\s*(?:천|백|십)?만원\s*[\d,]*\s*\d+\s*년\s*/\s*\d+\s*세\s*|'
                  r'\s*[\d,]{3,}\s*\d+\s*년\s*/\s*\d+\s*세\s*|\s*\d+\s*년\s*/\s*\d+\s*세\s*')


def tidy(t):
    return re.sub(r'\s+', ' ', JUNK.sub(' ', t or '')).strip()


SUB = re.compile(r'┗\s*(\d{1,3})\s+([^┗]{2,})')


def split_sub(out):
    """부모 담보의 설명문 안에 '┗ 208 수술비[상해1종] …' 처럼 뭉쳐 있는 세부보장을 번호별로 나눈다."""
    add = {}
    for no, v in list(out.items()):
        if '┗' not in v['desc']:
            continue
        head = v['desc'].split('┗', 1)[0].strip()
        for m in SUB.finditer(v['desc']):
            n2 = int(m.group(1))
            body = tidy(m.group(2))
            nm = body.split(' 보험기간')[0].split(' 상해')[0][:60]
            add[n2] = {'name': nm.strip(), 'desc': body}
        v['desc'] = head
    for k, v in add.items():
        out.setdefault(k, v)
    return out


# ── 설명문 → 지급조건 ─────────────────────────────────────────
KIND_PAT = [
    ('day',  r'입원일당|입원\s*1일당|입원하였을\s*때.*1일|통원\s*1회당|통원하였을\s*때'),
    ('surg', r'수술을\s*받았을|수술\s*1회당|수술을\s*받은\s*경우|수술비'),
    ('tx',   r'치료를\s*받[았은]|치료를\s*직접적인\s*목적|치료비|생활비|생활지원비|검사를\s*받'),
    ('dx',   r'진단확정|진단이\s*확정|진단되었을'),
    ('life', r'사망한\s*경우|장해상태가\s*되었을|후유장해'),
]
FREQ_PAT = [
    ('each', r'수술\s*1회당|치료\s*1회당|1회당|매회|받을\s*때마다'),
    ('year', r'연간\s*\d*\s*회한|연간1회한|해마다|매년'),
    ('once', r'최초\s*\d*\s*회한|최초1회한|최초\s*1회'),
]
RATE = re.compile(r'가입금액의\s*(\d+(?:\.\d+)?)\s*%')
# 1년 미만 감액 — 상품마다 문형이 다르고, PDF 줄바꿈 때문에 낱말 가운데 공백이 섞인다
#   ('가 입금액의 50%' · '전일 이 전 까 지 50% 감액적용').
#   그래서 공백을 모두 지운 문자열에서 찾는다(v8.33).
CUT1Y = [re.compile(r'1년경과시점전일이전[^※]{0,40}?가입금액의(\d+(?:\.\d+)?)%'),
         re.compile(r'1년경과시점전일이전[^※]{0,40}?(\d+(?:\.\d+)?)%감액'),
         re.compile(r'1년미만시[^※]{0,20}?가입금액의(\d+(?:\.\d+)?)%')]
# 90일 미만 감액 — 1년 감액과 문형이 같고 '90일경과시점' 만 다르다(v8.34)
CUT90 = [re.compile(r'90일경과시점전일이전[^※]{0,40}?가입금액의(\d+(?:\.\d+)?)%'),
         re.compile(r'90일경과시점전일이전[^※]{0,40}?(\d+(?:\.\d+)?)%감액')]
DAYS = re.compile(r'(\d+)일\s*한도|(\d+)일을\s*한도')
HOSPS = [('상급종합병원', '상급종합'), ('종합병원', '종합'), ('요양병원', '요양')]
ACTS = [('surg', r'수술'), ('chemo', r'항암약물|항암화학'), ('rad', r'항암방사선|방사선치료'),
        ('thromb', r'혈전용해'), ('icu', r'중환자실'), ('rehab', r'재활치료'), ('anes', r'전신마취')]


def derive(desc, name=''):
    """설명문 한 줄 → 지급 구조. 확신이 없는 항목은 넣지 않는다(빈 값 = 모름)."""
    d = re.sub(r'\s+', ' ', desc or '')
    if not d:
        return {}
    body = d.split('※')[0]                                  # ※ 이후는 용어 정의라 지급조건이 아니다
    r = {}
    nm = re.sub(r'\s+', '', name or '')
    # 담보명이 보상 유형을 그대로 말해 주면 그것이 우선 — 설명문은 '치료를 직접적인 목적으로 …
    # 수술을 받은 경우'처럼 여러 유형의 말이 섞여 오답이 나기 쉽다.
    for k, pat in (('day', r'입원일당|통원일당'), ('surg', r'수술비'), ('dx', r'진단비'),
                   ('life', r'사망|후유장해'), ('tx', r'치료비|생활비|생활지원비|검사비')):
        if re.search(pat, nm):
            r['kind'] = k
            break
    if 'kind' not in r:
        for k, pat in KIND_PAT:
            if re.search(pat, body):
                r['kind'] = k
                break
    for k, pat in FREQ_PAT:
        if re.search(pat, body):
            r['freq'] = k
            break
    m = RATE.search(body)
    if m:
        r['rate'] = float(m.group(1)) / 100
    elif '가입금액' in body:
        r['rate'] = 1.0
    dz = re.sub(r'\s+', '', d)
    m = next((x for x in (p.search(dz) for p in CUT1Y) if x), None)
    if m:
        r['cut_1y'] = float(m.group(1)) / 100
    m = next((x for x in (p.search(dz) for p in CUT90) if x), None)
    if m:
        r['cut_90d'] = float(m.group(1)) / 100
    m = DAYS.search(d)
    if m:
        r['limit_days'] = int(m.group(1) or m.group(2))
    h = next((v for k, v in HOSPS if k in body), None)
    if h:
        r['hosp'] = h
    acts = [k for k, pat in ACTS if re.search(pat, body)]
    if acts:
        r['acts'] = acts
    r['text'] = body[:200]
    return r


def group_hint(desc):
    """설명문에 열거된 질병군 이름이 이미 보유한 그룹표에 그대로 있으면 그 이름을 돌려준다.
       (코드를 만들지 않는다 — 기존 약관 별표를 가리킬 뿐이다)"""
    import scen_engine as S
    d = re.sub(r'\s+', '', desc or '')
    names = set(S.G131) | set(S.RULEDOC['kcd_groups'])
    return sorted({n for n in names if n and re.sub(r'\s+', '', n) in d}, key=len, reverse=True)[:3]


def explain(r):
    """사람이 읽는 한 줄 — 감사 로그·검수 보고용"""
    if not r:
        return ''
    KN = {'dx': '진단비', 'surg': '수술비', 'day': '입원·통원일당', 'tx': '치료비', 'life': '사망·후유장해'}
    FN = {'once': '최초 1회한', 'year': '연간 1회한', 'each': '1회당'}
    p = []
    if r.get('kind'):
        p.append(KN[r['kind']])
    if r.get('freq'):
        p.append(FN[r['freq']])
    if r.get('rate') is not None:
        p.append('가입금액' + ('' if r['rate'] == 1 else '의 %g%%' % (r['rate'] * 100)))
    if r.get('cut_90d'):
        p.append('90일 이내 %g%%' % (r['cut_90d'] * 100))
    if r.get('cut_1y'):
        p.append('1년 이내 %g%%' % (r['cut_1y'] * 100))
    if r.get('hosp'):
        p.append(r['hosp'] + '병원')
    if r.get('limit_days'):
        p.append('%d일 한도' % r['limit_days'])
    return ' · '.join(p)


def attach(riders, pdf_path):
    """설계 담보 목록에 설명문 기반 2차 판정을 붙인다. 1차(약관+규칙표) 결과는 건드리지 않는다."""
    try:
        desc = read_desc(pdf_path)
    except Exception as e:                                  # 설명문을 못 읽어도 본 계산은 그대로 간다
        return riders, {'ok': False, 'err': str(e)}
    hit = 0
    for r in riders:
        d = desc.get(r.get('no'))
        if not d:
            continue
        r['desc'] = d['desc']
        r['desc2'] = derive(d['desc'], r.get('name', ''))
        hit += 1
    return riders, {'ok': True, '설명문보유': hit, '전체': len(riders)}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    import matcher, build_all, scen_engine as S
    src = sys.argv[1]
    rows = matcher.read_proposal(src)
    rows = matcher.read_proposal(src, line=build_all.guess_line(rows))
    rows, info = attach(rows, src)
    print('설명문 인식 :', info)
    miss = [r for r in rows if not r.get('matched') or S.classify(r['name']) is None]
    print('\n■ 1차(약관·규칙표) 판정이 안 된 담보 — 설명문에서 읽은 지급조건')
    for r in miss:
        e = explain(r.get('desc2') or {})
        g = group_hint(r.get('desc') or '')
        print('  %3s %-44s → %s%s' % (r.get('no'), r['name'][:44], e or '(설명문 없음)',
                                      ' | 별표 후보: ' + ', '.join(g) if g else ''))
