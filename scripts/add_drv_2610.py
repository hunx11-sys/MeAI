# -*- coding: utf-8 -*-
"""
운전자 상해 종합보험 2608 개정(판매버전 2.0 · 2026.10.1 판매개시) → 특약검색기(tool.html) 반영

  python3 scripts/add_drv_2610.py            (결과만 출력)
  python3 scripts/add_drv_2610.py --write    (tool.html · tool_body.js 에 반영)

구버전(판매버전 1.0)과 새 약관을 글자 단위로 대조한 결과 바뀐 것은 아래뿐이다.
  - 특약 1개 신설 : 81. 상해진단및치료비보장 특별약관 (세부보장 6개, 약관 p.242~244)
  - 별표 2개 신설 : 【별표56】 중증도별 상해분류표(p.528) · 【별표57】 근골 주요처치및수술(급여) 분류표(p.530)
  - 그 뒤 쪽수가 밀림 : 특약 p.242~436 +3 · p.437(장해분류표)~579 +4 · 그 뒤 +12 (새 목차와 대조해 확인)
질병코드는 별표56 에서, 수가코드는 별표57 에서만 옮긴다(코드를 만들거나 추정하지 않는다).
PDF 가 2단 편집이라 글 상자를 왼쪽 단 → 오른쪽 단 순서로 읽는다.
"""
import base64, hashlib, io, json, os, re, sys, collections
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from tooldata import inflate, deflate, PAT

PDF = os.path.join(ROOT, '무배당 메리츠 운전자 상해 종합보험2608약관 (1).pdf')
TOOL = os.path.join(ROOT, 'tool.html')
P = '운전자'
RID = '운176'
TITLE = '상해진단및치료비'
PG = 242                       # 약관 목차 쪽수


def nz(s): return re.sub(r'[\s ]', '', s)
def table_id(name): return 'T' + hashlib.md5((P + '|' + nz(name)).encode('utf-8')).hexdigest()[:10]


def shift(p):
    """구버전 약관 쪽수 → 새 약관 쪽수"""
    q = int(p)
    if q < 242: return q
    if q < 437: return q + 3
    if q < 580: return q + 4
    return q + 12


def column_blocks(doc, i):
    """한 쪽의 글 상자를 왼쪽 단 → 오른쪽 단, 위 → 아래 순서로. 쪽번호 상자는 뺀다."""
    p = doc[i]; W = p.rect.width
    bl = [b for b in p.get_text('blocks') if b[4].strip() and not (b[1] > p.rect.height - 60 and re.fullmatch(r'\s*\d{1,3}\s*', b[4]))]
    L = sorted([b for b in bl if b[0] < W / 2 - 5], key=lambda b: (b[1], b[0]))
    R = sorted([b for b in bl if b[0] >= W / 2 - 5], key=lambda b: (b[1], b[0]))
    return [b[4].rstrip('\n') for b in L + R]


def page_of(doc, pat, start=0):
    for i in range(start, doc.page_count):
        if re.search(pat, doc[i].get_text(), re.M): return i
    raise SystemExit('PDF 에서 찾지 못함 : ' + pat)


def build(doc):
    # ── 특약 본문 ──
    i0 = page_of(doc, r'^\s*81\.\s*상해진단및치료비보장 특별약관\s*$', 200)
    blocks = []
    for i in range(i0, i0 + 4):
        for t in column_blocks(doc, i):
            if re.match(r'^\s*Ⅲ\.\s*질병 관련 특별약관', t): break
            blocks.append(t)
        else: continue
        break
    body = '\n'.join(blocks)
    body = body[body.index('81. 상해진단및치료비보장 특별약관'):]
    # 세부보장 이름 줄('· …(급' + '여,연간1회한)')이 단 폭 때문에 끊긴 것만 이어 붙인다
    ls = body.split('\n'); out = []
    for t in ls:
        if out and re.match(r'^\s*[·①②③④⑤⑥]', out[-1]) and not out[-1].rstrip().endswith(')') and len(t) < 20:
            out[-1] = out[-1].rstrip() + t.strip()
        else: out.append(t)
    body = '\n'.join(out)
    assert '총 6개의 세부보장' in body and '제6조(준용규정)' in body

    # ── 별표56 · 별표57 ──
    a = page_of(doc, r'^\s*【별표56】\s*$', 400)
    z = page_of(doc, r'^\s*Ⅹ\.\s*인용 법', a)
    txt = []
    for i in range(a, z + 1): txt += column_blocks(doc, i)
    txt = '\n'.join(txt)
    t56 = txt[txt.index('【별표56】'):txt.index('【별표57】')]
    t57 = txt[txt.index('【별표57】'):txt.index('Ⅹ. 인용')]

    # 별표56 : 중증도(경증및기타·중등증·중증)별 KCD
    s = t56[t56.index('번호') + 2:]
    s = s[:s.index('대상상병 분류표의')] if '대상상병 분류표의' in s else s
    parts = re.split(r'(?<![A-Z0-9])([ST]\d{2})(?![0-9.])', s)
    rows56, sev = [], '경증및기타'
    for k in range(0, len(parts) - 1, 2):
        seg = re.sub(r'\s+', ' ', parts[k]).strip()
        for key, val in (('경증 및 기타', '경증및기타'), ('경증및기타', '경증및기타'), ('중등증', '중등증'), ('중증', '중증')):
            if seg.startswith(key): sev = val; seg = seg[len(key):].strip(); break
        seg = re.sub(r'^(경증|및|기타)\s+', '', seg)
        rows56.append({'g': sev, 'label': seg, 'codes': [parts[k + 1]]})
    # 별표57 : 수가코드
    s = t57[t57.index('코드') + 2:]
    parts = re.split(r'(?<![A-Za-z0-9])([A-Z]{1,2}[A-Z0-9]\d{3})(?![0-9])', s)
    rows57 = [{'label': re.sub(r'\s+', ' ', parts[k]).strip(), 'codes': [parts[k + 1]]} for k in range(0, len(parts) - 1, 2)]
    for a_, b_ in zip(rows57, rows57[1:]):      # 이름 꼬리가 코드 뒤 줄로 밀린 경우('…-전방고정-' + '요추-복잡 …') 되돌려 붙인다
        if a_['label'].endswith(('-', ',')) and ' ' in b_['label']:
            head, rest = b_['label'].split(' ', 1)
            a_['label'] += head; b_['label'] = rest
    for r in rows57: r['label'] = re.sub(r'-\s+', '-', r['label'])

    def clean(t, head):
        t = re.sub(r'^\s*【별표\d+】\s*\n', '', t).strip()
        return t
    return body, rows56, clean(t56, '별표56'), rows57, clean(t57, '별표57')


def main(write):
    doc = pymupdf.open(PDF)
    body, rows56, text56, rows57, text57 = build(doc)

    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    if any(r['id'] == RID for r in D['riders']): sys.exit('%s 이미 있음 — 다시 넣지 않는다' % RID)
    cn = D['codenames']

    # 질병명은 KCD 표준 이름(codenames)을 쓰고, 없으면 약관 표 글자를 쓴다
    for r in rows56: r['label'] = cn.get(r['codes'][0]) or r['label']
    SEV = ['경증및기타', '중등증', '중증']
    by_sev = {g: [r for r in rows56 if r['g'] == g] for g in SEV}
    n56 = {g: len(v) for g, v in by_sev.items()}
    assert n56 == {'경증및기타': 66, '중등증': 42, '중증': 23}, n56
    hc = [r['codes'][0] for r in rows57]
    assert len(hc) == 419 and len(set(hc)) == 419, len(hc)
    for c in ('N0601', 'N2463', 'N0981', 'N1901', 'N0762', 'N0574', 'N0733'):   # 약관 지급 예시에 나온 수가코드
        assert c in hc, c

    # ── 구버전 이후 쪽수 밀림 ──
    only_drv = collections.defaultdict(set)
    for r in D['riders']:
        for t in r['t']: only_drv[t].add(r['p'])
    moved_r = moved_t = 0
    for r in D['riders']:
        if r['p'] == P and r.get('pg') is not None:
            new = shift(r['pg'])
            if new != int(r['pg']): r['pg'] = new; moved_r += 1
    for t, ps in only_drv.items():
        if ps == {P} and t in D['tables']:
            tb = D['tables'][t]; new = shift(tb['page'])
            if new != int(tb['page']): tb['page'] = new if isinstance(tb['page'], int) else str(new); moved_t += 1

    # ── 별표 2개 ──
    T56, T57 = table_id('중증도별 상해분류표'), table_id('근골 주요처치및수술(급여) 분류표')
    D['tables'][T56] = {'name': '중증도별 상해분류표', 'page': 528,
                        'rows': [{'g': {'경증및기타': '경증및기타 상해', '중등증': '중등증 상해', '중증': '중증 상해'}[r['g']], 'label': r['label'], 'codes': r['codes']} for r in rows56],
                        'text': text56}
    D['tables'][T57] = {'name': '근골 주요처치및수술(급여) 분류표', 'page': 530, 'rows': rows57, 'text': text57}

    # ── 특약 + 세부보장 6개 ──
    allk = [r['codes'][0] for r in rows56]
    alll = [r['label'] for r in rows56]
    kw = ['골절', '화상', '상해진단비', '중증도별 상해', '근골 주요처치', '상해수술비']
    parent = {'id': RID, 'p': P, 'n': TITLE, 'c': 'dx_tx', 'pg': PG, 'b': body, 'k': allk, 'l': alll, 'x': [],
              't': [T56, T57], 's': kw, 'st': ['diagnosis', 'surgery'], 'hc': hc}
    subs = []
    for i, g in enumerate(SEV, 1):
        subs.append({'id': '%s-%d' % (RID, i), 'n': '%s[%s 상해진단비(연간1회한)]' % (TITLE, '경증및기타' if g == '경증및기타' else g),
                     'k': [r['codes'][0] for r in by_sev[g]], 'l': [r['label'] for r in by_sev[g]],
                     't': [T56], 'st': 'diagnosis', 'cond': '%s 상해 진단확정 · 연간 1회' % g})
    for i, g in enumerate(SEV, 4):
        subs.append({'id': '%s-%d' % (RID, i), 'n': '%s[%s 상해 근골 주요처치및수술비(급여,연간1회한)]' % (TITLE, g),
                     'k': [r['codes'][0] for r in by_sev[g]], 'l': [r['label'] for r in by_sev[g]],
                     't': [T56, T57], 'st': 'surgery', 'hc': hc,
                     'cond': '%s 상해 진단확정 + 근골 주요처치및수술(급여, 별표57 수가코드) · 연간 1회' % g})
    new = [parent]
    for s in subs:
        r = {'id': s['id'], 'p': P, 'n': s['n'], 'c': 'dx_tx', 'pg': PG, 'b': body, 'k': s['k'], 'l': s['l'], 'x': [],
             't': s['t'], 's': kw, 'st': s['st'], 'parent': RID, 'cond': s['cond']}
        if 'hc' in s: r['hc'] = s['hc']
        new.append(r)
    last = max(i for i, r in enumerate(D['riders']) if r['p'] == P)
    D['riders'][last + 1:last + 1] = new

    # 중증도 이름으로도 검색되게 (코드는 별표56 그대로)
    for g in SEV: D['synonyms'][g + '상해'] = [r['codes'][0] for r in by_sev[g]]

    # ── 집계 · 버전 ──
    D['meta']['total'] = len(D['riders'])
    D['meta']['prodcount'] = dict(collections.Counter(r['p'] for r in D['riders']))
    D['meta']['version'] = 'ver2612'
    for c in D.get('categories', []):
        if isinstance(c, dict) and 'id' in c: c['count'] = sum(1 for r in D['riders'] if r.get('c') == c['id'])

    tops = sum(1 for r in D['riders'] if not r.get('parent'))
    print('본문 %d자 · 별표56 %s · 별표57 수가코드 %d' % (len(body), n56, len(hc)))
    print('쪽수 고침 : 특약 %d건 · 별표 %d건' % (moved_r, moved_t))
    print('전체 %d건(특약 %d · 세부 포함) · 운전자 %d' % (D['meta']['total'], tops, D['meta']['prodcount'][P]))
    if not write: return
    html = html[:m.start(2)] + json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[m.end(2):]
    html = html.replace('<span class="ver">ver2611</span>', '<span class="ver">ver2612</span>', 1)
    # 상품 히스토리
    h = re.search(r'(<script id="HISTORY" type="application/json">)(.*?)(</script>)', html, re.S)
    H = json.loads(h.group(2))
    H['updated'] = '2026.10.01'
    H['groups'] = [g for g in H['groups'] if g['name'] != '상해진단·치료비 계통']
    H['groups'].append({'name': '상해진단·치료비 계통', 'events': [{
        'd': '2026.10', 'ds': 20261001, 'e': '신설', 'hl': 'good', 'n': '상해진단및치료비 신설',
        'note': '운전자 상해 종합보험(2608) 판매버전 2.0(2026.10.1 판매개시)에 탑재. 별표56 중증도별 상해분류표로 경증및기타·중등증·중증 '
                '상해진단비 3종, 같은 중증도 상해로 별표57 근골 주요처치및수술(급여, 수가코드 419개)을 받으면 근골 주요처치및수술비 3종 — 세부보장마다 연간1회.',
        'q': '상해진단및치료비', 'syn': ['상해진단및치료비', '상해진단비', '근골 주요처치및수술비', '중증도별 상해']}]})
    html = html[:h.start(2)] + json.dumps(H, ensure_ascii=False, separators=(',', ':')) + html[h.end(2):]
    # 보상시뮬레이터(SIMSRC, base64) 안의 상품 히스토리 사본에도 같은 항목
    sm = re.search(r'(<script id="SIMSRC" type="text/plain">)(.*?)(</script>)', html, re.S)
    sim = base64.b64decode(sm.group(2)).decode('utf-8')
    h2 = re.search(r'(<script id="HISTORY" type="application/json">)(.*?)(</script>)', sim, re.S)
    H2 = json.loads(h2.group(2))
    H2['groups'] = [g for g in H2['groups'] if g['name'] != '상해진단·치료비 계통'] + [H['groups'][-1]]
    sim = sim[:h2.start(2)] + json.dumps(H2, ensure_ascii=False) + sim[h2.end(2):]
    html = html[:sm.start(2)] + base64.b64encode(sim.encode('utf-8')).decode('ascii') + html[sm.end(2):]
    io.open(TOOL, 'w', encoding='utf-8').write(html)
    print('tool.html · tool_body.js 반영')


if __name__ == '__main__':
    main('--write' in sys.argv)
