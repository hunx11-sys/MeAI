# -*- coding: utf-8 -*-
"""약관 PDF → 통합생활지원비 지급금액표(life_support.json)

통합생활지원비(암·2대질환·질병·상해)는 통합치료비와 같은 '항목별 지급금액표' 구조다.
  · 가입금액(= 월간 총 지급금액) 구간마다 표가 따로 있다.
  · 항목은 산정특례 / 주요치료 / 재활치료 세 묶음.
  · 2대질환·질병은 '계약일부터 1년 경과시점' 전/후로 금액이 다르다(전 = 절반).
  · 월간 총 지급금액은 가입금액을 한도로 한다.

사용 : python3 scripts/import_life_support.py "약관.pdf" [--write]
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'proposal_smart', 'life_support.json')

# 담보 id ← 약관 특별약관 제목
RIDERS = [
    ('ca_ls', r'암\s*통합생활지원비\(월간한도\)'),
    ('two_ls', r'2대질환\s*통합생활지원비\(월간한도\)'),
    ('dz_ls', r'질병\s*통합생활지원비\([^)]*\)\(월간한도\)'),
    ('inj_ls', r'상해\s*통합생활지원비\(월간한도\)'),
]
MARK = re.compile(r'보험가입금액\s*:\s*월간\s*총\s*지급금액\s*([\d,]+)\s*만원')
NUM = re.compile(r'([\d,.]+)\s*만원')


def man(s):
    """'1,000만원' → 1000 · '0.5만원' → 0.5 · 없으면 None"""
    m = NUM.search((s or '').replace(' ', ''))
    if not m:
        return None
    return float(m.group(1).replace(',', ''))


def clean(s):
    return re.sub(r'\s+', ' ', (s or '').replace('\n', '')).strip()


def col_of(rect, width):
    """2단 조판 — 왼쪽 단이면 0, 오른쪽 단이면 1"""
    return 0 if (rect[0] + rect[2]) / 2 < width / 2 else 1


def grp_of(cell, label):
    """항목 묶음 — 표의 세로 병합 칸이 비어 나오는 경우가 많아 항목명으로도 판정한다."""
    c = re.sub(r'\s', '', cell or '')
    if '산정특례' in c or '산정특례' in label: return '산정특례'
    if '재활' in c or '재활치료' in label: return '재활치료'
    return '주요치료'


def parse_tables(page):
    """페이지의 표를 (열, y, 항목dict) 로 돌려준다."""
    out = []
    try:
        tabs = page.find_tables()
    except Exception:
        return out
    for t in tabs.tables:
        rows = [[clean(c) for c in r] for r in t.extract()]
        if not rows or not any('통합생활지원치료항목' in (r[0] or '') + (r[1] if len(r) > 1 else '') for r in rows[:2]):
            continue
        # 열 개수로 1년 경과 전/후 분리 여부 판단
        twocol = any('1년' in c for r in rows[:2] for c in r)
        items, grp, prev = [], '', None
        # 헤더 행 수는 표마다 다르다(1년 경과 전/후 구분이 있으면 2행) → 행 수로 자르지 않고
        # '금액이 읽히는 행'만 데이터로 본다. 예전에는 rows[2:] 로 잘라 첫 항목이 사라졌다.
        for r in rows:
            g = r[0] or grp
            if r[0]:
                grp = r[0]
            label = clean(r[1] if len(r) > 1 else '')
            if not label or '통합생활지원치료항목' in label or '지급금액' in label:
                continue
            cnt = clean(r[2] if len(r) > 2 else '')
            a1 = man(r[3] if len(r) > 3 else '')
            a2 = man(r[4] if len(r) > 4 else '') if twocol else None
            if a1 is None and prev is not None:
                # 재활치료처럼 여러 항목이 금액 칸을 합쳐 쓰는 경우 → 바로 위 항목 금액을 따른다
                cnt, a1, a2 = prev['cnt'], prev['amt_pre'], prev['amt']
            if a1 is None:
                continue
            it = {'grp': grp_of(g, label), 'label': label, 'cnt': cnt,
                  'amt': (a2 if a2 is not None else a1), 'amt_pre': (a1 if a2 is not None else a1)}
            items.append(it)
            prev = it
        if items:
            out.append((col_of(t.bbox, page.rect.width), t.bbox[1], items))
    return out


def parse_rider(doc, start, rid, title_re):
    """특별약관 본문을 읽어 가입금액 구간별 항목표를 만든다.

    구간-표 짝짓기는 **사람이 읽는 순서**(쪽 → 단 → 위에서 아래)로 한다.
    금액 크기로 정렬해 짝짓던 예전 방식은, 2대질환처럼 '제2항(상해로 인한 경우)' 표가
    한 벌 더 붙는 약관에서 구간을 한 칸씩 밀어 잘못 붙였다.
    같은 구간에 같은 묶음(산정특례/주요치료) 표가 두 번 나오면 **먼저 나온 표**를 쓴다.
    """
    seq = []                                        # (쪽, 단, y, 종류, 값)
    for i in range(start, min(start + 8, len(doc))):
        page = doc[i]
        text = page.get_text()
        if seq and i > start and re.search(r'\d+\.\s*[^\n]{2,60}보장\s*특별약관', text):
            break                                  # 다음 특별약관 시작
        w = page.rect.width
        for r in page.search_for('월간 총 지급금액'):
            line = page.get_textbox([r[0] - 200, r[1] - 2, r[2] + 200, r[3] + 2])
            mm = MARK.search(re.sub(r'\s+', ' ', line))
            if mm:
                seq.append((i, col_of(r, w), r[1], 'mark', int(mm.group(1).replace(',', ''))))
        for c, y, items in parse_tables(page):
            seq.append((i, c, y, 'tab', items))
    seq.sort(key=lambda x: (x[0], x[1], x[2]))
    tiers, cur = {}, None
    for _, _, _, kind, v in seq:
        if kind == 'mark':
            cur = str(v)
            tiers.setdefault(cur, [])
            continue
        if cur is None:
            continue
        have = set(x['grp'] for x in tiers[cur])
        if any(x['grp'] in have for x in v):        # 같은 묶음이 이미 있으면 뒤 표는 버린다
            continue
        tiers[cur] += v
    return {k: v for k, v in tiers.items() if v}


def nice(pat):
    """정규식 제목 → 사람이 읽는 담보명"""
    return re.sub(r'\\s\*', ' ', pat).replace('\\', '').replace('[^)]*', '…')


def verify(tiers):
    """짝지은 구간표가 믿을 만한지 — 구간마다 묶음이 다 있어야 하고, 항목 수가 같아야 하며,
       가입금액이 커질 때 **같은 항목**의 금액이 줄어들면 안 된다."""
    bad = []
    ks = sorted(tiers, key=lambda x: int(x))
    for k in ks:
        g = set(it['grp'] for it in tiers[k])
        if '산정특례' not in g or '주요치료' not in g:
            bad.append('%s만원 구간에 %s 표가 없음' % (k, ' · '.join(sorted({'산정특례', '주요치료'} - g))))
    n = {k: len(v) for k, v in tiers.items()}
    if n and len(set(n.values())) > 1:
        bad.append('구간마다 항목 수가 다름(%s)' % ' / '.join('%s:%d' % (k, n[k]) for k in ks))
    key = lambda it: re.sub(r'\s', '', it['label'])
    prev = None
    for k in ks:
        cur = {key(it): it['amt'] for it in tiers[k]}
        if prev:
            drop = [l for l in cur if l in prev[1] and cur[l] < prev[1][l]]
            if drop:
                bad.append('%s만원 구간 금액이 %s만원 구간보다 작은 항목 %d개(%s)'
                           % (k, prev[0], len(drop), drop[0][:20]))
        prev = (k, cur)
    return bad


def main():
    import pymupdf
    if len(sys.argv) < 2:
        print(__doc__)
        return
    src = sys.argv[1]
    doc = pymupdf.open(src)
    found = {}
    for rid, pat in RIDERS:
        rx = re.compile(r'\d+\.\s*' + pat + r'[^\n]{0,30}보장\s*특별약관')
        start = None
        for i in range(len(doc)):
            t = re.sub(r'\s+', ' ', doc[i].get_text())
            # 목차·면책표에도 같은 제목이 나오므로 '제1조(보험금의 지급사유)' 가 이어지는 쪽만 본문으로 본다
            if rx.search(t) and '제1조(보험금의 지급사유)' in t:
                start = i
                break
        if start is None:
            continue
        tiers = parse_rider(doc, start, rid, pat)
        if not tiers:
            continue
        # 같은 구간에 같은 항목이 두 번 들어간 경우 정리
        for k, items in tiers.items():
            seen, uniq = set(), []
            for it in items:
                key = re.sub(r'\s', '', it['label'])
                if key in seen:
                    continue
                seen.add(key)
                uniq.append(it)
            tiers[k] = uniq
        warn = verify(tiers)
        found[rid] = {'nm': nice(pat), 'src': os.path.basename(src), 'page': start + 1,
                      'srcs': [{'src': os.path.basename(src), 'page': start + 1}],
                      'verified': not warn, 'warn': warn, 'tiers': tiers}
        if warn:
            print('   [검증실패] ' + ' · '.join(warn))
        print('■ %-8s p%-5d 구간 %s' % (rid, start + 1, ' / '.join('%s만원:%d항목' % (k, len(v)) for k, v in sorted(tiers.items(), key=lambda x: int(x[0])))))

    if '--write' in sys.argv:
        old = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
        # 같은 담보가 여러 상품 약관에 있다 — 금액표가 같은지 교차 대조하고, 출처는 약관마다 모아 둔다.
        # 약관마다 띄어쓰기가 조금씩 달라(예 '종합병원 중환자실치료' / '종합병원중환자실치료')
        # 공백을 지운 뒤 (묶음·항목명·지급횟수·금액) 이 같은지로 대조한다.
        def norm(tiers):
            return {k: sorted((it['grp'], re.sub(r'\s', '', it['label']), re.sub(r'\s', '', it['cnt'] or ''),
                               it['amt'], it['amt_pre']) for it in v) for k, v in tiers.items()}
        for rid, v in found.items():
            prev = old.get(rid)
            if prev and norm(prev.get('tiers') or {}) == norm(v['tiers']):
                srcs = prev.get('srcs') or [{'src': prev.get('src'), 'page': prev.get('page')}]
                for x in v['srcs']:
                    if x not in srcs: srcs.append(x)
                v['srcs'] = srcs
                v['src'], v['page'] = srcs[0]['src'], srcs[0]['page']
            elif prev:
                v['warn'] = (v.get('warn') or []) + ['다른 약관(%s)과 금액표가 다름 — 상품별로 따로 확인 필요' % prev.get('src')]
                v['verified'] = False
                print('   [교차대조] %s : %s 와 금액표가 다릅니다' % (rid, prev.get('src')))
        old.update(found)
        json.dump(old, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\n저장 →', OUT, '· 담보', len(old), '종')
    else:
        print('\n(미리보기 — 저장하려면 --write)')
        for rid, v in found.items():
            k = sorted(v['tiers'], key=lambda x: int(x))[-1]
            print('\n%s · 가입 %s만원 구간' % (rid, k))
            for it in v['tiers'][k]:
                print('   %-6s %-34s %-16s %s만원' % (it['grp'], it['label'][:34], it['cnt'][:16], it['amt']))


if __name__ == '__main__':
    main()
