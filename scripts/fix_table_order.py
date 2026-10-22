# -*- coding: utf-8 -*-
"""
약관 본문 속 표 · 가입금액 제목의 자리 바로잡기 (2026-10-21)

무엇이 문제였나
  약관 PDF 는 두 단 조판이라, 본문 글을 뽑을 때 왼쪽 단 아래쪽과 오른쪽 단 위쪽이 섞였다. 그 위에 표를 되살리면서
  (fix_body_tables.py) 표가 「본문에서 표 글자가 나오던 자리」에 들어가, 통합치료비 · 통합생활지원비 계열에서
  「<보험가입금액 4,000만원>」 바로 다음에 「<보험가입금액 8,000만원>」이 오고 4,000만원 표가 8,000만원 제목 밑에,
  1억원 표가 ⑤항(대상질병) 뒤에 붙는 일이 생겼다(소유자 발견 — 통합간편 암 통합치료비(기본형)).

어떻게 고치나 (글자는 하나도 만들지 않는다 — 있는 덩어리를 옮기기만)
  1) 약관 PDF 의 특약 쪽들을 「쪽 → 왼쪽 단 → 오른쪽 단 → 위에서 아래」 순서로 읽어,
     표 · 가입금액 제목 하나하나 바로 앞에 오는 「글 줄」을 찾는다.
  2) 본문에서 표 덩어리([표:N] + | 줄)와 「<보험가입금액 …>」 제목 줄을 모두 떼어 낸 뒤,
     PDF 순서대로 「바로 앞 글 줄」 다음에 다시 끼운다(앞 글 줄은 본문 위에서 아래로 차례로 찾는다).
  3) 옮기기 전과 뒤의 글 줄 · 표 덩어리 묶음이 똑같은지 대조 — 하나라도 다르면 그 특약은 건드리지 않는다.
  PDF 에서 짝을 못 찾은 표 · 제목은 원래 자리 근처에 그대로 둔다(로그).

실행 : python3 scripts/fix_table_order.py                 (바뀌는 특약 목록만)
       python3 scripts/fix_table_order.py --show 통131      (한 특약의 바뀐 차례 보기)
       python3 scripts/fix_table_order.py --write           (tool.html · tool_body.js 에 반영)
"""
import collections, io, json, os, re, sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import inflate, deflate, PAT, ROOT
from fix_body_tables import pdf_for, read_table, table_lines, Usage, start_page

TOOL = os.path.join(ROOT, 'tool.html')
HEAD = re.compile(r'^\s*<보험가입금액[^>]*>\s*$')


def nk(s):
    """비교용 : 띄어쓰기 · 항 번호(①…) · PDF 의 항 번호 특수 글자를 뺀다"""
    s = re.sub(r'[-①-⑳]', '', s or '')
    return re.sub(r'\s+', '', s)


def blocks(body):
    """본문 → [('txt', 줄) | ('tab', [줄…]) | ('head', 줄)]"""
    L = body.split('\n'); out = []; i = 0
    while i < len(L):
        if L[i].startswith('[표:'):
            j = i + 1
            while j < len(L) and '|' in L[j]: j += 1
            out.append(('tab', L[i:j])); i = j; continue
        out.append(('head' if HEAD.match(L[i]) else 'txt', L[i])); i += 1
    return out


def pdf_sequence(doc, pages, usage):
    """PDF 읽는 순서 : [('txt', 글) | ('tab', 표 줄들) | ('head', 글)]"""
    seq = []
    for pi in pages:
        if not 0 <= pi < len(doc): continue
        page = doc[pi]; mid = page.rect.width / 2
        items = []
        try:
            found = page.find_tables().tables
        except Exception:
            found = []
        boxes = []
        for tb in found:
            if tb.col_count < 2 or tb.row_count < 2: continue
            g, cv = read_table(page, tb, usage)
            items.append((tb.bbox[0] >= mid - 5, tb.bbox[1], 'tab', table_lines(g, cv)))
            boxes.append(tb.bbox)
        for b in page.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                x0, y0, x1, y1 = ln['bbox']
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if not t or re.fullmatch(r'\d{1,4}', t): continue
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                if any(bx[0] - 1 <= cx <= bx[2] + 1 and bx[1] - 1 <= cy <= bx[3] + 1 for bx in boxes): continue
                items.append((x0 >= mid - 5, y0, 'head' if HEAD.match(t) else 'txt', t))
        # 한 단 쪽(치아보험 등)은 위에서 아래로만 — 가운데를 가로지르는 글 줄이 많으면 한 단이다
        cross = sum(1 for bl in page.get_text('dict')['blocks'] for ln in bl.get('lines', [])
                    if ln['bbox'][0] < mid - 15 and ln['bbox'][2] > mid + 15)
        lines_n = sum(1 for it in items if it[2] != 'tab')
        if lines_n and cross > lines_n * .3:
            items = [(False,) + it[1:] for it in items]
        items.sort(key=lambda it: (it[0], it[1]))
        seq += [(k, v) for _, _, k, v in items]
    return seq


def tkey(lines):
    return nk('\n'.join(lines[1:]))


def reorder(body, seq):
    """본문의 표 · 제목을 PDF 순서대로 옮긴다 → (새 본문, 옮긴 수, 못 찾은 것)"""
    B = blocks(body)
    movable = [b for b in B if b[0] in ('tab', 'head')]
    if not movable: return body, 0, []
    pool = collections.defaultdict(list)                      # 본문에 있는 표 · 제목 (같은 것이 여럿일 수 있다)
    for b in movable:
        pool[(b[0], tkey(b[1]) if b[0] == 'tab' else nk(b[1]))].append(b)
    # PDF 순서에서 「앞 글(이어 붙인 30글자 이상) → 그 뒤에 오는 표 · 제목 묶음」
    groups, prev, last, cur = [], '', '', []
    for k, v in seq:
        if k == 'txt':
            if cur: groups.append(((prev, last), cur)); cur = []
            prev = (prev + nk(v))[-200:]; last = nk(v)
        else:
            key = (k, tkey(v) if k == 'tab' else nk(v))
            if pool.get(key): cur.append(pool[key].pop(0))
    if cur: groups.append(((prev, last), cur))
    placed = {id(b) for _, g in groups for b in g}
    if not placed: return body, 0, []
    # 옮길 것만 떼어 낸 본문(글 줄 + 못 찾은 표 · 제목은 그대로)
    rest = [b for b in B if id(b) not in placed]
    # 본문 글 줄을 이어 붙인 글(띄어쓰기 · 항 번호 뺌)과 줄마다 끝나는 자리
    stream, ends = '', {}
    for j, b in enumerate(rest):
        if b[0] == 'txt':
            stream += nk(b[1]); ends[len(stream)] = j
    out, pos, at, miss = [], 0, 0, []
    def find(t, need_unique):
        hits = []
        st = stream.find(t, at)
        while st != -1:
            e = st + len(t)
            if e in ends and ends[e] >= pos - 1: hits.append((ends[e], e))
            st = stream.find(t, st + 1)
        if not hits or (need_unique and len(hits) > 1): return None
        return hits[0]
    for gi, ((tail, last), g) in enumerate(groups):
        if not tail:                                              # 표가 맨 앞(앞 글 없음)
            out += g; continue
        hit = None
        # 1) 앞 글 덩어리 : 30글자로 찾아 겹치면 늘려서 하나로 좁힌다
        for L in (30, 60, 100, 150, 200):
            if len(tail) < 12: break
            t = tail[-L:]
            h = find(t, need_unique=(len(t) == L and L < 200))
            if h: hit = h; break
            if not find(t, need_unique=False): break
        # 2) 바로 앞 한 줄만(본문 글 줄 순서가 PDF 와 조금 다른 곳) — 한 곳으로 좁혀질 때만
        if hit is None and len(last) >= 10:
            hit = find(last, need_unique=True)
        if hit is None:
            # 3) 앞 글을 못 찾으면(표 옆 세로 머리글 등) 바로 앞 무리에 붙여 표끼리의 순서를 지킨다
            if out and any(b[0] != 'txt' for b in out):
                out += g; continue
            return body, 0, [tail[-30:]]
        k, e = hit
        if k + 1 < pos:                                            # 순서가 거꾸로 — 이 특약은 그대로
            return body, 0, ['순서 거꾸로']
        out += rest[pos:k + 1] + g; pos = k + 1; at = e
    out += rest[pos:]
    # 대조 : 글 줄 · 표 · 제목 묶음이 그대로인가
    sig = lambda bs: collections.Counter((b[0], '\n'.join(b[1]) if b[0] == 'tab' else b[1]) for b in bs)
    if sig(out) != sig(B):
        return body, 0, ['대조 불일치']
    nb = '\n'.join('\n'.join(b[1]) if b[0] == 'tab' else b[1] for b in out)
    moved = sum(1 for x, y in zip(out, B) if x is not y)
    return nb, (moved if nb != body else 0), []


def main():
    write = '--write' in sys.argv
    show = sys.argv[sys.argv.index('--show') + 1] if '--show' in sys.argv else None
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    R = D['riders']; RM = {r['id']: r for r in R}
    old = {r['id']: r.get('b') for r in R}
    by_prod = collections.defaultdict(list)
    for r in R:
        if r.get('pg') is not None and r.get('b') and ('[표:' in r['b'] or '<보험가입금액' in r['b']):
            by_prod[r['p']].append(r)
    allpg = collections.defaultdict(set)
    for r in R:
        if r.get('pg') is not None: allpg[r['p']].add(r['pg'])
    changed, log = {}, collections.Counter()
    for prod, rs in by_prod.items():
        f = pdf_for(prod)
        if not f: print('약관 PDF 없음 :', prod); continue
        doc = pymupdf.open(f); usage = Usage(doc)
        pgs = sorted(allpg[prod])
        for r in rs:
            par = RM.get(r.get('parent'))
            if par is not None and old.get(par['id']) == r['b']: continue
            nxt = next((p for p in pgs if p > r['pg']), r['pg'] + 3)
            seq = pdf_sequence(doc, range(start_page(doc, r), min(nxt, r['pg'] + 14) + 1), usage)
            nb, n, miss = reorder(r['b'], seq)
            if miss: log['그대로(' + str(miss[0])[:12] + ')'] += 1
            if n:
                changed[r['id']] = nb; log['고침'] += 1
                print('고침 %-8s %-6s %s' % (r['id'], r['p'], r['n']))
            if show == r['id']:
                for b in blocks(nb):
                    if b[0] != 'txt' or re.match(r'[①-⑳]|제\d+조', b[1]):
                        print('   ', b[0], (b[1][1] if b[0] == 'tab' else b[1])[:70])
    for r in R:
        if r['id'] in changed: r['b'] = changed[r['id']]
    k = 0
    for r in R:
        par = RM.get(r.get('parent'))
        if par is not None and par['id'] in changed and old.get(par['id']) == old.get(r['id']):
            r['b'] = par['b']; k += 1
    print(dict(log), '· 세부보장 따라감', k)
    if write:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body.replace('</', '<\\/') + html[m.end(2):])
        print('tool.html · tool_body.js 저장')


if __name__ == '__main__':
    main()
