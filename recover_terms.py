#!/usr/bin/env python3
"""
메리츠 영업지원도구(tool.html) 약관 본문 복구 스크립트
- 저장소 루트에서 실행: python3 scripts/recover_terms.py
- 입력: tool.html(내장 DATA), 약관 PDF 4종(파일명에 통합간편/케어프리/운전자/치아 포함)
- 동작: PDF에서 특약 제목("N. ○○보장 특별약관" + 제1조)을 찾아 다음 제목까지를 본문으로 다시 잘라내고,
        별표(분류표)는 두 단 배치를 유지해 재추출한 뒤 tool.html 의 DATA 를 갱신한다.
- 필요 패키지: pip install pymupdf
"""
import json, re, os, sys, glob, difflib, collections
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
PRODS = ['통합간편', '케어프리', '운전자', '치아']
PDF = {}
for prod in PRODS:
    hits = [p for p in glob.glob(os.path.join(ROOT, '**', '*.pdf'), recursive=True) if prod in os.path.basename(p)]
    if not hits:
        sys.exit(f'약관 PDF를 찾지 못했습니다: 파일명에 "{prod}" 가 들어간 PDF가 필요합니다')
    PDF[prod] = sorted(hits)[-1]
    print('PDF', prod, '->', os.path.relpath(PDF[prod], ROOT))

src = open(TOOL, encoding='utf-8').read()
_m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', src, re.S)
d = json.loads(_m.group(2))
R = d['riders']; T = d['tables']
ROMAN = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ'

# ── 페이지 텍스트 (블록 순서) ──
PAGES = {}
for prod in PRODS:
    doc = pymupdf.open(PDF[prod])
    PAGES[prod] = [doc[i].get_text() for i in range(len(doc))]
    print(prod, len(PAGES[prod]), 'pages')

# ═══════════════ 1. 특약 본문 ═══════════════
ROMAN = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ'

def norm(s):
    s = re.sub(r'[\s\u00a0\uf000]', '', s)
    return s.replace('（', '(').replace('）', ')').replace('･', '·').replace('ㆍ', '·')

def build_lines(pages):
    """페이지별 텍스트 → (page, text) 줄 목록. 바닥글 쪽번호는 제거."""
    lines = []
    for pi, t in enumerate(pages):
        ls = t.split('\n')
        # 마지막 비어있지 않은 줄이 쪽번호면 제거
        for j in range(len(ls) - 1, -1, -1):
            if ls[j].strip():
                if re.fullmatch(r'\d{1,4}', ls[j].strip()):
                    ls[j] = ''
                break
        for l in ls:
            lines.append((pi, l.rstrip()))
    return lines

SECTION_RE = re.compile(r'^\s*(?:[' + ROMAN + r']+\.\s*\S.*|제\s*\d+\s*[절관장]\b.*)$')
ART1_RE = re.compile(r'^\s*제\s*1\s*조(의\s*\d+)?\s*\([^()]*(\([^()]*\)[^()]*)*\)\s*$')
BODY_END_RE = re.compile(r'(니다\.|다\.|합니다|됩니다|:|;|\)\s*$|」|』)\s*$')

def heading_blocks(lines):
    """'제1조(' 로 시작하는 줄 앞의 제목 줄들을 묶어 (start_idx, art_idx, title) 반환."""
    blocks = []
    for i, (pi, l) in enumerate(lines):
        if not ART1_RE.match(l):
            continue
        j = i - 1; head = []
        # 제목과 제1조 사이의 안내문("＊ 이 특별약관은 … 가입 가능합니다.")은 건너뛴다
        note_end = None
        jj = j
        while jj >= 0 and jj > i - 8:
            t = lines[jj][1].strip()
            if not t: jj -= 1; continue
            if note_end is None and re.search(r'(니다|습니다|합니다|됩니다)\s*\.?\s*$', t):
                note_end = jj
            if note_end is not None and re.match(r'^[＊*※]', t):
                j = jj - 1; break
            if note_end is None and not re.search(r'(니다|습니다|합니다|됩니다)\s*\.?\s*$', t):
                break
            jj -= 1
        idxs = []
        while j >= 0 and len(head) < 7:
            t = lines[j][1].strip()
            if not t:
                j -= 1; continue
            if len(t) > 70 or re.search(r'(니다|습니다|합니다|됩니다|않습니다)\s*\.?\s*$', t) or re.match(r'^\s*[①-⑳]', t):
                break
            head.insert(0, t); idxs.insert(0, j); j -= 1
            if SECTION_RE.match(t) and '특별약관' not in t:
                break
            # 번호가 붙은 줄(예: '10. 상급종합병원', '2-1. 갱신형 …')이 제목의 첫 줄 → 여기서 멈춤
            if re.match(r'^\d+(-\d+)?\.\s*\S', t) or re.match(r'^[' + ROMAN + r']+\.\s*\S', t):
                # 바로 앞 줄이 절 표시(예: 'Ⅰ. 상해 관련 특별약관')면 그것까지 포함
                jj2 = j
                while jj2 >= 0 and not lines[jj2][1].strip(): jj2 -= 1
                if jj2 >= 0 and re.match(r'^[' + ROMAN + r']+\.\s*\S+\s*관련\s*특별약관\s*$', lines[jj2][1].strip()) and not re.match(r'^[' + ROMAN + r']', t):
                    head.insert(0, lines[jj2][1].strip()); idxs.insert(0, jj2)
                break
        if not head or '특별약관' not in ''.join(head):
            continue
        # 앞쪽 절/장 표시줄은 제목에서 제외 (예: 'Ⅰ. 상해 관련 특별약관', '제2절 보장조항')
        k = 0
        while k < len(head) - 1 and (re.match(r'^[' + ROMAN + r']+\.\s*.*관련\s*특별약관\s*$', head[k]) or re.match(r'^제\s*\d+\s*[절관장]', head[k]) or re.fullmatch(r'제2절\s*보장조항.*', head[k])):
            k += 1
        # '제2절 보장조항 2-1. …' 처럼 한 줄에 붙은 경우
        head[k] = re.sub(r'^제\s*\d+\s*절\s*보장조항\s*', '', head[k])
        head[k] = re.sub(r'^[' + ROMAN + r']+\.\s*[^0-9]*?관련\s*특별약관\s*', '', head[k])
        blocks.append({'start': idxs[k], 'bstart': idxs[0], 'art': i, 'title': ' '.join(head[k:]), 'page': lines[i][0]})
    return blocks

def title_norm(t):
    t = norm(t)
    t = re.sub(r'^[0-9]+(-[0-9]+)?[.\-]', '', t)
    t = t.replace('(통합간편가입)', '')
    t = re.sub(r'(보장)?(추가)?특별약관$', '', t)
    return t

results = {}
stats = collections.Counter()
report = []
for prod in PRODS:
    pages = PAGES[prod]
    lines = build_lines(pages)
    blocks = heading_blocks(lines)
    starts = sorted(b['bstart'] for b in blocks)
    # 별표 절 시작줄·절(節) 제목줄도 경계
    boundaries = set(starts)
    for i, (pi, l) in enumerate(lines):
        t = l.strip()
        if re.match(r'^[' + ROMAN + r']+\.\s*별표\s*$', t) or re.match(r'^(【\s*)?별표\s*1\s*[(【】\]]', t) \
           or (len(t) <= 12 and re.match(r'^제\d+절\s*[가-힣]{2,8}$', t)) \
           or (len(t) <= 30 and re.match(r'^[' + ROMAN + r']+\.\s*\S.*특별약관\s*$', t)) \
           or (len(t) <= 70 and re.match(r'^무배당\s.*(특별약관|보험)', t)):
            boundaries.add(i)
    boundaries = sorted(boundaries)
    riders = [r for r in R if r['p'] == prod]
    for r in riders:
        want = norm(r['n']); want2 = want.replace('보장', '')
        cands = [b for b in blocks if abs(b['page'] - r['pg']) <= 1]
        exact = [b for b in cands if title_norm(b['title']) in (want, want2) or title_norm(b['title']).replace('보장', '') == want2]
        best = None
        if len(exact) == 1:
            best = exact[0]; stats['exact'] += 1
        elif len(exact) > 1:
            best = min(exact, key=lambda b: abs(b['page'] - r['pg'])); stats['exact-multi'] += 1
        else:
            g = '갱신형' in want
            cont = [b for b in cands if want2 and want2 in title_norm(b['title']).replace('보장', '') and (('갱신형' in b['title']) == g)]
            if len(cont) >= 1:
                best = min(cont, key=lambda b: (abs(b['page'] - r['pg']), len(b['title']))); stats['contains'] += 1
            else:
                wa = want2.replace('(추가)', '')
                allc = [b for b in blocks if title_norm(b['title']).replace('보장', '') in (want2, wa) and (('갱신형' in b['title']) == ('갱신형' in want)) and (('추가특별약관' in norm(b['title'])) == ('(추가)' in want))]
                if allc:
                    best = min(allc, key=lambda b: abs(b['page'] - r['pg'])); stats['global'] += 1
                    report.append(f"GLOBAL {r['id']} p{r['pg']}→p{best['page']} {r['n']!r}")
            if not best:
                cands2 = [b for b in blocks if abs(b['page'] - r['pg']) <= 2]
                scored = [(difflib.SequenceMatcher(None, want2, title_norm(b['title']).replace('보장', '')).ratio(), b) for b in cands2 if ('갱신형' in b['title']) == g]
                scored.sort(key=lambda x: -x[0])
                if scored and scored[0][0] >= 0.9:
                    best = scored[0][1]; stats['fuzzy'] += 1
                    report.append(f"FUZZY {r['id']} {r['n']!r} ← {best['title']!r} ({scored[0][0]:.2f})")
        if not best:
            # 페이지 번호가 어긋난 경우: 상품 전체에서 제목이 정확히 같은 것을 찾아 가장 가까운 페이지 선택
            wa = want2.replace('(추가)', '')
            allc = [b for b in blocks if title_norm(b['title']).replace('보장', '') in (want2, wa) and (('갱신형' in b['title']) == ('갱신형' in want)) and (('추가특별약관' in norm(b['title'])) == ('(추가)' in want))]
            if allc:
                best = min(allc, key=lambda b: abs(b['page'] - r['pg']))
                if abs(best['page'] - r['pg']) <= 40 or len(allc) == 1:
                    stats['global'] += 1
                    report.append(f"GLOBAL {r['id']} p{r['pg']}→p{best['page']} {r['n']!r}")
                else:
                    best = None
        if not best:
            stats['missing'] += 1
            near = [b['title'][:50] for b in blocks if abs(b['page'] - r['pg']) <= 1]
            report.append(f"MISSING {r['id']} p{r['pg']} {r['n']!r} near={near[:3]}")
            continue
        # 본문 끝 = 다음 경계
        end = next((b for b in boundaries if b > best['art']), len(lines))
        body_lines = [lines[i][1] for i in range(best['start'], end)]
        body = '\n'.join(body_lines).strip('\n')
        body = re.sub(r'\n{2,}', '\n', body)
        results[r['id']] = {'body': body, 'title': best['title'], 'start_page': lines[best['start']][0], 'end_page': lines[end - 1][0] if end - 1 < len(lines) else None}

NEW_BODIES = results
print(dict(stats))
# 검증: 새 본문이 문장으로 끝나는가, 기존 본문 첫 부분과 일치하는가
end_ok = 0; prefix_ok = 0; longer = 0; shorter = []
for r in R:
    nb = results.get(r['id'])
    if not nb: continue
    b = nb['body']
    if re.search(r'(니다\.|다\.)\s*$', b): end_ok += 1
    old = norm(r['b'])[:80]; new = norm(b)
    if old[:60] in new[:400]: prefix_ok += 1
    if len(b) >= len(r['b']) * 0.9: longer += 1
    else: shorter.append((r['id'], r['n'], len(r['b']), len(b)))
print('extracted', len(results), 'ends-with-sentence', end_ok, 'prefix-match', prefix_ok, 'not-shorter', longer)
print('shorter examples:', shorter[:15])
import collections as _c
bad_end=[(r['id'],r['n'],results[r['id']]['body'][-70:]) for r in R if r['id'] in results and not re.search(r'(니다\.|다\.)\s*$', results[r['id']]['body'])]
print('non-sentence endings:',len(bad_end))
for b in bad_end[:25]: print('   ',b[0],b[1][:30],repr(b[2]))

print('\n'.join(l for l in report if not l.startswith('GLOBAL'))[:3000])

# ═══════════════ 2. 별표(분류표) ═══════════════

def tnorm0(s):
    s = re.sub(r'[\s\u00a0\uf000]', '', s or '')
    return s.replace('（', '(').replace('）', ')').replace('･', '·').replace('ㆍ', '·').replace('‧', '·').replace('，', ',')

def col_text(page):
    W = page.rect.width; mid = W / 2
    words = page.get_text("words")
    cols = {0: [], 1: []}
    for w in words:
        c = 0 if (w[0] + w[2]) / 2 < mid else 1
        cols[c].append(w)
    out = []
    for c in (0, 1):
        ws = sorted(cols[c], key=lambda w: (round(w[1] / 3), w[0]))
        lines = []; cur = []; cury = None
        for w in ws:
            if cury is None or abs(w[1] - cury) <= 3:
                cur.append(w); cury = w[1] if cury is None else cury
            else:
                lines.append(cur); cur = [w]; cury = w[1]
        if cur: lines.append(cur)
        for ln in lines:
            ln.sort(key=lambda w: w[0]); out.append(' '.join(w[4] for w in ln))
    return '\n'.join(out)

# 페이지별 열 순서 텍스트 (캐시)
COL = {}
for prod in PRODS:
    doc = pymupdf.open(PDF[prod])
    COL[prod] = [col_text(doc[i]) for i in range(len(doc))]

# 표를 참조하는 특약의 상품 → 표의 상품
prod_of = {}
for r in R:
    for t in r['t']:
        prod_of.setdefault(t, r['p'])

HEAD_RE = re.compile(r'^\s*[【\[]\s*별표\s*(\d+)\s*[】\]]\s*$')

def table_headings(prod):
    """(line_idx, page, no, name) 목록과 전체 줄 목록"""
    lines = []
    for pi, t in enumerate(COL[prod]):
        ls = t.split('\n')
        for j in range(len(ls) - 1, -1, -1):
            if ls[j].strip():
                if re.fullmatch(r'\d{1,4}', ls[j].strip()): ls[j] = ''
                break
        for l in ls: lines.append((pi, l))
    heads = []
    for i, (pi, l) in enumerate(lines):
        m = HEAD_RE.match(l)
        if not m: continue
        # 이름: 다음 비어있지 않은 줄 (짧은 2줄이면 이어붙임)
        j = i + 1; name = []
        while j < len(lines) and len(name) < 2:
            t = lines[j][1].strip()
            if not t: j += 1; continue
            if name and (re.match(r'^\d+\.', t) or len(t) > 40 or re.search(r'니다', t)): break
            name.append(t); j += 1
        heads.append({'idx': i, 'page': pi, 'no': int(m.group(1)), 'name': ' '.join(name)})
    return lines, heads

# 경계: 다음 별표 제목, 특약 제목(번호. …특별약관 + 제1조), 표지, 절 제목
def boundaries(lines, heads):
    b = set(h['idx'] for h in heads)
    for i, (pi, l) in enumerate(lines):
        t = l.strip()
        if (len(t) <= 70 and re.match(r'^무배당\s.*(특별약관|보험)', t)) or (len(t) <= 30 and re.match(r'^[' + ROMAN + r']+\.\s*\S.*(특별약관|별표)\s*$', t)) \
           or (len(t) <= 12 and re.match(r'^제\d+절\s*[가-힣]{2,8}$', t)) or re.match(r'^\d+(-\d+)?\.\s*\S.*(보장)?\s*특별약관\s*$', t):
            b.add(i)
    return sorted(b)

HL = {}
for prod in PRODS:
    lines, heads = table_headings(prod)
    HL[prod] = (lines, heads, boundaries(lines, heads))
    print(prod, '별표 headings:', len(heads))

def tnorm(n):
    n = tnorm0(n)
    n = re.sub(r'^별표\d+', '', n)
    return n

results = {}
stats = collections.Counter(); report = []  # tables
for tid, t in T.items():
    prod = prod_of.get(tid)
    if not prod:
        stats['no-product'] += 1; continue
    lines, heads, bnd = HL[prod]
    want = tnorm(t['name'])
    cands = [h for h in heads if tnorm(h['name']) == want]
    if not cands:
        cands = [h for h in heads if want and (want in tnorm(h['name']) or tnorm(h['name']) in want) and min(len(want), len(tnorm(h['name']))) >= 5]
        if cands: stats['contains'] += 1
    if not cands:
        # 다른 상품에서 같은 이름의 별표를 찾는다 (동일 판본 분류표)
        for p2 in PRODS:
            if p2 == prod: continue
            l2, h2, b2 = HL[p2]
            c2 = [h for h in h2 if tnorm(h['name']) == want]
            if c2:
                cands = c2; lines, heads, bnd = l2, h2, b2; stats['other-product'] += 1; break
    if not cands:
        stats['missing'] += 1; report.append(f"MISSING {tid} {t['name']!r} ({prod}, p{t.get('page')})"); continue
    pg = t.get('page') or 0
    best = min(cands, key=lambda h: abs(h['page'] - pg))
    end = next((b for b in bnd if b > best['idx']), len(lines))
    body = '\n'.join(lines[i][1] for i in range(best['idx'] + 1, end)).strip('\n')
    body = re.sub(r'\n{2,}', '\n', body)
    results[tid] = {'text': body, 'page': best['page'], 'heading': best['name']}
    stats['matched'] += 1

NEW_TABLES = results
print(dict(stats))
print('\n'.join(report))
# 비교
for tid, nt in list(results.items())[:0]: pass
longer = sum(1 for tid, nt in results.items() if len(nt['text']) >= len(T[tid]['text']) * 0.9)
print('not-shorter', longer, 'of', len(results))
for tid, nt in results.items():
    if len(nt['text']) < len(T[tid]['text']) * 0.9:
        print('  SHORTER', tid, T[tid]['name'], len(T[tid]['text']), '->', len(nt['text']), repr(nt['text'][-80:]))

# ═══════════════ 3. tool.html 반영 ═══════════════
NB=NEW_BODIES; NT=NEW_TABLES
def clean(b):
    ls=b.split('\n')
    while ls and (re.search(r'\.{6,}\s*\d*\s*$', ls[-1]) or re.match(r'^\s*무배당\s', ls[-1]) or not ls[-1].strip()):
        ls.pop()
    # 본문 끝에 세로쓰기 표에서 튄 2~4자짜리 조각 줄이 연속되면 제거
    k=len(ls)
    while k>0 and len(ls[k-1].strip())<=4 and not re.search(r'[.。]$', ls[k-1].strip()): k-=1
    if len(ls)-k>=6: ls=ls[:k]
    return '\n'.join(ls)
nb=0; tb=0; kept=[]
for r in R:
    if r['id'] in NB:
        r['b']=clean(NB[r['id']]['body']); r['pg']=NB[r['id']]['start_page']; nb+=1
for tid,nt in NT.items():
    old=T[tid]['text']; new=nt['text']
    old_ok=bool(re.search(r'(다\.|니다\.)\s*$',old.rstrip()))
    if old_ok and len(old)>len(new):
        kept.append((tid,T[tid]['name'])); continue
    T[tid]['text']=new; T[tid]['page']=nt['page']; tb+=1
d['meta']['version']='ver2609'
out=json.dumps(d,ensure_ascii=False,separators=(',',':'))
src=src[:_m.start(2)]+out+src[_m.end(2):]
open(TOOL,'w',encoding='utf-8').write(src)
ends=sum(1 for r in R if re.search(r'(다\.|니다\.)\s*$',r['b'].rstrip()))
tends=sum(1 for t in T.values() if re.search(r'(다\.|니다\.|\d)\s*$',t['text'].rstrip()))
print(f"bodies replaced {nb}/{len(R)}; ending with sentence {ends}; tables replaced {tb}/{len(T)}, kept curated {len(kept)}: {kept[:6]}")
print("body len min/median/max", min(len(r['b']) for r in R), sorted(len(r['b']) for r in R)[len(R)//2], max(len(r['b']) for r in R))
print("total DATA bytes", len(out))

