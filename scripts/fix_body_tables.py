# -*- coding: utf-8 -*-
"""
약관 본문 속 표 되살리기 — 특약검색기·보상시뮬레이터 「약관 본문」 탭 (2026.10)

무엇이 문제였나
  약관 본문은 PDF 글자를 위에서 아래로 뽑은 것이라, 지급금액표 같은 표가 칸마다 한 줄씩 흩어져
  「연간 / 1회한 / 5만원 / 10만원 …」처럼 세로로 늘어서 있었다(9월 중순 판은 표로 묶었지만
  합쳐진 칸 · 두 줄짜리 머리칸을 몰라 칸이 밀리고, 좁은 칸의 줄바꿈이 「급 여」 · 「수 술( 1- 5 종)」로 남았다).

어떻게 고치나
  1) 약관 PDF 의 특약 쪽(pg)부터 다음 특약 쪽까지 표를 PDF 의 칸 선으로 찾는다(pymupdf find_tables).
  2) 표의 칸 글자를 순서대로 이은 것(띄어쓰기 무시)이 본문에 그대로 있으면 그 자리를 표로 바꾼다.
     본문에 그대로 없으면(감수 때 손본 곳 등) 건드리지 않는다 — 글자를 새로 만들지 않는다.
  3) 칸 안 줄바꿈은 줄이 칸 끝까지 찼으면 붙이고(「급」+「여」→「급여」), 덜 찼으면 띄운다.
  4) 합쳐진 칸은 「^」(위 칸과 합침) · 「<」(왼쪽 칸과 합침)로 적고, 화면(tool.html fmtClause)이
     rowspan · colspan 으로 그린다. 머리줄 수는 「[표:2]」처럼 표 시작 줄에 적는다.

실행 : python3 scripts/fix_body_tables.py            (결과만 보기)
       python3 scripts/fix_body_tables.py --write    (tool.html · tool_body.js 에 반영)
       python3 scripts/fix_body_tables.py --write --only 통N269,통131   (특약 몇 개만)
본문을 PDF 에서 다시 뽑은 뒤(recover_terms.py · import_terms.py)에는 이 스크립트를 다시 돌린다.
"""
import collections, glob, io, json, os, re, sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import inflate, deflate, PAT, ROOT

TOOL = os.path.join(ROOT, 'tool.html')


def pdf_for(prod):
    """상품 → 약관 PDF (recover_terms.py · import_terms.py 와 같은 파일)"""
    names = [p for p in glob.glob(os.path.join(ROOT, '*.pdf'))]
    base = lambda p: os.path.basename(p)
    if prod == '또또암':
        c = [p for p in names if '또 받는 암보험' in base(p)]
    elif prod == '또또암간편':
        c = [p for p in names if '또 받는 간편한 암보험' in base(p)]
    elif prod == '치아':
        c = [p for p in names if '치아보험' in base(p)]
    else:
        c = [p for p in names if prod in base(p)]
    return sorted(c)[-1] if c else None


def nk(s):
    return re.sub(r'\s+', '', s or '')


# ── 표 하나 읽기 : 칸 격자 · 합친 칸 · 칸 글자 ──
def read_table(page, tb, usage=None):
    rows = tb.rows
    R, C = len(rows), tb.col_count
    raw = tb.extract()
    # 열·행 경계
    xs = sorted({round(c[0], 1) for r in rows for c in r.cells if c} | {round(tb.bbox[2], 1)})
    ys = [r.bbox[1] for r in rows] + [rows[-1].bbox[3]]

    plines = page_lines(page)
    grid = [[None] * C for _ in range(R)]
    for i, r in enumerate(rows):
        for j, c in enumerate(r.cells):
            if c is None:
                continue
            x0, y0, x1, y1 = c
            cs = max(1, sum(1 for e in xs if x0 + 1 < e < x1 - 1) + 1)
            rs = max(1, sum(1 for e in ys[1:-1] if y0 + 1 < e < y1 - 1) + 1)
            grid[i][j] = {'txt': cell_text(plines, c, usage), 'raw': raw[i][j] or '', 'rs': rs, 'cs': cs}
    # 덮인 칸 표시
    cover = [[None] * C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            g = grid[i][j]
            if not g:
                continue
            for di in range(g['rs']):
                for dj in range(g['cs']):
                    if (di or dj) and i + di < R and j + dj < C:
                        cover[i + di][j + dj] = '^' if di else '<'
    return grid, cover


def page_lines(page):
    """쪽의 글자 줄 : [[(글자, x0, y0, x1, y1), …], …] — 칸 나누기는 글자 하나씩"""
    out = []
    for b in page.get_text('rawdict')['blocks']:
        for ln in b.get('lines', []):
            cs = [(c['c'], *c['bbox']) for sp in ln['spans'] for c in sp['chars']]
            if cs:
                out.append(cs)
    return out


class Usage:
    """약관 전체에서 두 글자+두 글자가 붙어 쓰였는지 띄어 쓰였는지 센 것 — 칸 안 줄바꿈 판정에 쓴다"""
    def __init__(self, doc):
        self.j, self.s = collections.Counter(), collections.Counter()
        for page in doc:
            for ln in page.get_text().split('\n'):
                t = re.sub(r'\s+', ' ', ln.strip())
                if len(t) < 14: continue                    # 표 칸 같은 짧은 줄은 빼고 문장 줄만 센다
                for k in range(len(t) - 3):
                    w = t[k:k + 4]
                    if ' ' not in w: self.j[w] += 1
                for k in range(len(t) - 4):
                    w = t[k:k + 5]
                    if w[2] == ' ' and ' ' not in w[:2] + w[3:]: self.s[w] += 1

    def space(self, a, b):
        """a 끝 두 글자와 b 앞 두 글자 사이 : True(띄움) · False(붙임) · None(모름)"""
        if len(a) < 2 or len(b) < 2: return None
        j, s = self.j[a[-2:] + b[:2]], self.s[a[-2:] + ' ' + b[:2]]
        if j == s: return None
        return s > j


def cell_text(plines, bbox, usage=None):
    """칸 안 글자 — 줄바꿈 자리를 붙일지 띄울지 : 약관 안 쓰임 → 칸 폭(줄이 찼으면 붙임)"""
    x0, y0, x1, y1 = bbox
    lines = []
    for cs in plines:
        sel = [c for c in cs if x0 - .5 <= (c[1] + c[3]) / 2 <= x1 + .5 and y0 - .5 <= (c[2] + c[4]) / 2 <= y1 + .5]
        while sel and not sel[-1][0].strip(): sel.pop()
        while sel and not sel[0][0].strip(): sel.pop(0)
        if sel:
            lines.append(sel)
    lines.sort(key=lambda l: (round(l[0][2], 0), l[0][1]))
    texts = [re.sub(r'\s+', ' ', ''.join(c[0] for c in l)) for l in lines]
    if not texts:
        return ''
    if len(texts) > 1 and all(len(t.replace(' ', '')) <= 2 for t in texts):
        return ''.join(t.replace(' ', '') for t in texts)          # 좁은 칸 세로쓰기(검/사 · 주/요/치/료)
    out = texts[0]
    for k in range(1, len(texts)):
        prev, t = lines[k - 1], texts[k]
        a = out
        sp = None
        if re.match(r'[가-힣]', a[-1:]) and re.match(r'\d', t):
            sp = True                                                # 연간 + 1회한
        elif usage:
            sp = usage.space(a, t)
        if sp is None:
            if t[:1] in ')]」』,.':
                sp = False
            else:
                w = prev[-1][3] - prev[0][1]
                cw = w / max(1, len(prev))
                sp = (x1 - x0) - w > cw * 1.1 + 1.5                  # 줄이 덜 찼으면 낱말 끝에서 넘긴 것
        out = a + (' ' if sp else '') + t
    return out.strip()


def table_lines(grid, cover):
    R, C = len(grid), len(grid[0])
    # 머리줄 : 첫 줄 칸이 아래로 합쳐진 만큼 (최대 3)
    head = max([g['rs'] for g in grid[0] if g] or [1])
    head = min(head, 3, R - 1) if R > 1 else 1
    out = ['[표:%d]' % head]
    for i in range(R):
        cells = []
        for j in range(C):
            if cover[i][j]:
                cells.append(cover[i][j])
            elif grid[i][j]:
                cells.append(grid[i][j]['txt'].replace('|', '｜') or ' ')
            else:
                cells.append(' ')
        out.append(' | '.join(cells))
    return out


def stream(grid):
    return ''.join(nk(g['raw']) for row in grid for g in row if g)


# ── 본문 안에서 표 자리 찾기 (띄어쓰기 무시 글자 흐름) ──
def norm_map(b):
    chars, pos = [], []
    for i, ch in enumerate(b):
        if not ch.isspace():
            chars.append(ch); pos.append(i)
    return ''.join(chars), pos


def replace_tables(b, tables):
    """tables : [(stream, lines)] → 새 본문, 바꾼 수"""
    hits = []
    s, pos = norm_map(b)
    for st, lines in tables:
        if len(st) < 6:
            continue
        k = -1
        start = 0
        while True:
            k = s.find(st, start)
            if k < 0:
                break
            a, z = pos[k], pos[k + len(st) - 1] + 1
            if not any(a < hz and z > ha for ha, hz, _ in hits):
                break
            start = k + 1
        if k < 0:
            continue
        hits.append((a, z, lines))
    if not hits:
        return b, 0
    hits.sort()
    out, last = [], 0
    for a, z, lines in hits:
        # 줄 단위로 넓힌다(넓히는 곳이 빈칸뿐일 때만)
        la = b.rfind('\n', 0, a) + 1
        if b[la:a].strip():
            la = a
        lz = b.find('\n', z)
        lz = len(b) if lz < 0 else lz
        if b[z:lz].strip():
            lz = z
        pre = b[last:la]
        out.append(pre if not pre or pre.endswith('\n') else pre + '\n')
        out.append('\n'.join(lines))
        tail_nl = '\n' if lz < len(b) and not b[lz:lz + 1] == '\n' else ''
        out.append(tail_nl)
        last = lz
    out.append(b[last:])
    return ''.join(out), len(hits)


def main():
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    R = D['riders']
    RM = {r['id']: r for r in R}
    old = {r['id']: r.get('b') for r in R}
    by_prod = collections.defaultdict(list)
    for r in R:
        if r.get('pg') is not None and r.get('b'):
            by_prod[r['p']].append(r)
    stat = collections.Counter()
    changed = {}
    for prod, rs in by_prod.items():
        f = pdf_for(prod)
        if not f:
            print('약관 PDF 없음 :', prod); continue
        doc = pymupdf.open(f)
        usage = Usage(doc)
        pgs = sorted({r['pg'] for r in rs})
        cache = {}

        def tables_on(pi):
            if pi not in cache:
                lst = []
                if 0 <= pi < len(doc):
                    page = doc[pi]
                    try:
                        found = page.find_tables().tables
                    except Exception:
                        found = []
                    # 읽는 순서 : 왼쪽 단 위→아래, 오른쪽 단 위→아래
                    mid = page.rect.width / 2
                    found.sort(key=lambda t: (t.bbox[0] >= mid - 5, t.bbox[1]))
                    for tb in found:
                        if tb.col_count < 2 or tb.row_count < 2:
                            continue
                        g, cv = read_table(page, tb, usage)
                        cells = [x for row in g for x in row if x]
                        if sum(1 for x in cells if not x['txt']) > len(cells) * .25:
                            continue                        # 빈칸이 많은 것 = 【예시】 기간 도식(선 그림) — 표가 아니다
                        lst.append((stream(g), table_lines(g, cv)))
                cache[pi] = lst
            return cache[pi]

        seen_body = {}
        for r in sorted(rs, key=lambda r: r['pg']):
            if only and r['id'] not in only:
                continue
            par = RM.get(r.get('parent'))
            if par is not None and old.get(par['id']) == r['b']:
                continue                                    # 세부보장 : 부모 본문을 그대로 쓴다(아래에서 따라감)
            nxt = next((p for p in pgs if p > r['pg']), r['pg'] + 3)
            tabs = []
            for pi in range(r['pg'], min(nxt, r['pg'] + 12) + 1):
                tabs += tables_on(pi)
            stat['특약'] += 1
            if not tabs:
                continue
            nb, n = replace_tables(r['b'], tabs)
            if n:
                stat['표 넣은 특약'] += 1; stat['표'] += n
                changed[r['id']] = nb
    # 반영 (세부보장은 부모 본문을 따라감)
    for r in R:
        if r['id'] in changed:
            r['b'] = changed[r['id']]
    for r in R:
        par = RM.get(r.get('parent'))
        if par is not None and par['id'] in changed and old.get(par['id']) == old.get(r['id']):
            r['b'] = par['b']; stat['세부보장 따라감'] += 1
    print(dict(stat))
    for rid in list(changed)[:3]:
        print('──', rid, RM[rid]['n'])
    if '--write' in sys.argv:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html · tool_body.js 저장')
    return RM, changed


if __name__ == '__main__':
    main()
