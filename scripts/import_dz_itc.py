# -*- coding: utf-8 -*-
"""약관 PDF → 질병 통합치료비 지급금액표 (product_data.json 의 RIDERS/IT/AMT 에 'DZ' 로 추가)

질병 통합치료비는 다른 통합치료비와 같은 '항목별 지급금액표' 구조인데, 수술 항목이 1-5종 수술분류표를
그대로 쓴다(1종수술 … 5종수술). 가입금액 구간마다 표가 따로 있고 계약일부터 1년 경과 전에는 절반이다.

구간-표 짝짓기는 페이지 좌표로 하지 않는다(2단 조판이라 어긋난다).
대신 **금액 크기로 정렬해서 배정**한다 — 가입금액이 크면 항목 금액도 크다는 약관의 성질을 이용한다.
배정 후에는 표 개수·항목 수·단조 증가를 검증하고, 하나라도 어긋나면 쓰지 않는다.

사용 : python3 scripts/import_dz_itc.py "약관.pdf" [--write]
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PD = os.path.join(BASE, 'proposal_smart', 'product_data.json')

TITLE = re.compile(r'\d+\.\s*질병\s*통합치료비[^\n]{0,20}보장\s*특별약관')
MARK = re.compile(r'보험가입금액\s*([\d,]+)\s*만원')

# 약관 항목명 → 엔진 치료키. 엔진이 이미 쓰는 키를 그대로 쓴다(상해 통합치료비와 같은 항목들).
KEY = [
    (r'MRI촬영', 'x_mri', '검사'), (r'CT촬영', 'x_ct', '검사'), (r'양전자단층촬영|PET', 'x_pet', '검사'),
    (r'흡인.*천자.*절개', 'aspir', '주요치료'), (r'신경차단', 'block', '주요치료'), (r'도수정복', 'reduction', '주요치료'),
    (r'창상봉합.*안면부이외', 'suture', '주요치료'), (r'창상봉합.*안면부', 'suture_face', '주요치료'),
    (r'지속적신대체요법|CRRT', 'crrt', '주요치료'), (r'인공호흡기', 'vent', '주요치료'),
    (r'저체온', 'hypo', '주요치료'), (r'부분체외순환', 'ecmo', '주요치료'),
    (r'전신마취.*6시간', 'anes6', '주요치료'),
]
SURG = re.compile(r'([1-5])종수술')


def won(s):
    """'2만 5천원' → 2.5 · '150만원' → 150 · '1,000만원' → 1000 (단위: 만원)"""
    t = re.sub(r'[\s,]', '', s or '')
    m = re.fullmatch(r'(?:(\d+)만)?(?:(\d+)천)?원?', t)
    if not m or not any(m.groups()):
        return None
    return (int(m.group(1) or 0)) + (int(m.group(2) or 0)) / 10


def keyof(label):
    for pat, k, c in KEY:
        if re.search(pat, label):
            return k, c, None
    m = SURG.search(label)
    if m:
        return 'surg', '수술(1-5종)', int(m.group(1))
    return None, None, None


def grab(page):
    """이 쪽의 통합치료항목 표를 [{키: (1년이내, 1년이후)}] 로"""
    out = []
    try:
        tabs = page.find_tables()
    except Exception:
        return out
    for t in tabs.tables:
        rows = [[re.sub(r'\s+', ' ', (c or '').replace('\n', '')).strip() for c in r] for r in t.extract()]
        if not rows or '통합치료항목' not in (rows[0][0] or ''):
            continue
        got = {}
        # 금액 열은 상품에 따라 1개(감액 구분 없음) 또는 2개(1년 경과 전/후)다
        for r in rows:
            if len(r) < 4:
                continue
            k, c, j = keyof(r[1])
            if not k:
                continue
            a1 = won(r[3])
            a2 = won(r[4]) if len(r) > 4 else None
            if a1 is None and a2 is None:
                continue
            if a2 is None:
                a1, a2 = a1, a1                     # 감액 구분이 없는 표 → 전/후 같은 금액
            elif a1 is None:
                a1 = a2
            got[(k, j)] = (a1, a2, c, r[2])
        if got:
            out.append(got)
    return out


def main():
    import pymupdf
    if len(sys.argv) < 2:
        print(__doc__)
        return
    doc = pymupdf.open(sys.argv[1])
    start = None
    for i in range(len(doc)):
        t = re.sub(r'\s+', ' ', doc[i].get_text())
        if TITLE.search(t) and '제1조(보험금의 지급사유)' in t:
            start = i
            break
    if start is None:
        print('질병 통합치료비 특별약관을 찾지 못했습니다.')
        return

    tiers, tables = [], []
    for i in range(start, min(start + 6, len(doc))):
        t = doc[i].get_text()
        # 2단 조판이라 제목 쪽에 표가 없을 수 있다 → 표를 한 장이라도 모은 뒤에만 다음 특약에서 멈춘다
        if tables and i > start and re.search(r'\d+\.\s*[^\n]{2,60}보장\s*특별약관', t):
            break
        for m in MARK.finditer(re.sub(r'\s+', ' ', t)):
            v = int(m.group(1).replace(',', ''))
            if v >= 1000 and v not in tiers:
                tiers.append(v)
        tables += grab(doc[i])
    tiers.sort()

    # 표를 '검사+수술' 과 '주요치료' 로 나눈 뒤, 각각 대표 금액 순으로 정렬해 구간에 배정한다
    surv = [g for g in tables if any(k == 'surg' for k, _ in g)]
    main_ = [g for g in tables if ('crrt', None) in g]
    surv.sort(key=lambda g: g[('surg', 1)][1])
    main_.sort(key=lambda g: g[('crrt', None)][1])
    print('구간', tiers, '| 검사·수술 표', len(surv), '| 주요치료 표', len(main_))
    bad = []
    if not (len(tiers) == len(surv) == len(main_)):
        bad.append('구간 수와 표 개수가 다름')

    merged = {}
    for n, (a, b) in enumerate(zip(surv, main_)):
        if n >= len(tiers):
            break
        g = dict(a); g.update(b)
        merged[tiers[n]] = g
    for n in range(1, len(tiers)):
        if tiers[n] not in merged or tiers[n - 1] not in merged:
            continue
        for k in merged[tiers[n]]:
            if k in merged[tiers[n - 1]] and merged[tiers[n]][k][1] < merged[tiers[n - 1]][k][1]:
                bad.append('%s 구간의 %s 금액이 앞 구간보다 작음' % (tiers[n], k))
                break

    # 항목 순서 고정 → IT / AMT
    order = []
    for k, c in [('x_mri', '검사'), ('x_ct', '검사'), ('x_pet', '검사')]:
        order.append((k, None, c))
    for j in range(1, 6):
        order.append(('surg', j, '수술(1-5종)'))
    for pat, k, c in KEY:
        if c == '주요치료':
            order.append((k, None, c))
    LBL = {'x_mri': 'MRI촬영(급여)', 'x_ct': 'CT촬영(급여)', 'x_pet': '양전자단층촬영(PET)(급여)',
           'aspir': '특정시술치료(흡인,천자,절개)(급여)', 'block': '특정시술치료(신경차단술)(급여)',
           'reduction': '특정시술치료(도수정복술)(급여)', 'suture_face': '창상봉합술치료(안면부,표재성)(급여)',
           'suture': '창상봉합술치료(안면부이외,표재성)(급여)', 'crrt': '지속적신대체요법(CRRT)(급여)',
           'vent': '인공호흡기치료(12시간초과)(급여)', 'hypo': '저체온요법치료(급여)',
           'ecmo': '부분체외순환치료(급여)', 'anes6': '종합병원 전신마취치료(6시간이상)(급여)'}
    IT, AMT = [], {}
    for k, j, c in order:
        it = {'k': k, 'l': (LBL.get(k) or ('%d종수술' % j)), 'c': c, 'p': 'y'}
        if j:
            it['j'] = j
        IT.append(it)
    for tv in tiers:
        g = merged.get(tv) or {}
        row = []
        for k, j, c in order:
            v = g.get((k, j))
            row.append(v[1] if v else 0)
        if 0 in row:
            bad.append('%s만원 구간에 값이 빠진 항목이 있음' % tv)
        AMT[str(tv)] = row

    print('항목', len(IT), '개 · 구간별 금액')
    for tv in tiers:
        print('  %5d만원 :' % tv, AMT[str(tv)])
    if bad:
        print('\n[검증실패]', ' · '.join(sorted(set(bad))))
        print('→ 저장하지 않습니다.')
        return

    if '--write' in sys.argv:
        d = json.load(open(PD, encoding='utf-8'))
        d['IT']['DZ'] = IT
        d['AMT']['DZ'] = AMT
        d['RIDERS'] = [r for r in d['RIDERS'] if r['id'] != 'dz']
        d['RIDERS'].append({'id': 'dz', 'g': 'dz', 'ty': 'DZ', 'nm': '질병 통합치료비', 'sh': '질병 통합',
                            'tiers': tiers, 'half': 1, 'wait': 0, 'pg': '약관 질병 통합치료비 특별약관',
                            'about': '검사·1-5종 수술·주요치료를 질병 전반에 걸쳐 항목별로 보장해요'})
        json.dump(d, open(PD, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('\n저장 →', PD)
    else:
        print('\n(미리보기 — 저장하려면 --write)')


if __name__ == '__main__':
    main()
