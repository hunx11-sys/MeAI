#!/usr/bin/env python3
"""
보험용어 사전(gloss.js) 점검 — 약관 개정 뒤에 돌리세요
- 저장소 루트에서 실행: python3 scripts/check_gloss.py
- 하는 일
  1) 약관 본문·분류표에 자주 나오는데 사전에 없는 말을 뽑아 줍니다. (새 용어 후보)
  2) 사전에는 있는데 약관 어디에도 안 나오는 말을 알려 줍니다. (없어진 용어 후보)
  3) 별칭이 검색 동의어와 어긋나지 않는지 확인합니다.
- 결과를 보고 gloss.js 의 용어를 손으로 고치면 됩니다. 자동으로 고치지는 않습니다.
- 사전은 화면을 그릴 때 얹는 방식이라, 손보지 않아도 도구는 그대로 동작합니다.
"""
import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from tooldata import inflate, deflate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
GLOSS = os.path.join(ROOT, 'gloss.js')
TOP = int(sys.argv[1]) if len(sys.argv) > 1 else 40

# ── 사전 읽기 ───────────────────────────────────────────────
src = open(GLOSS, encoding='utf-8').read()
m = re.search(r'var G = (\{.*?\});\s*\n', src, re.S)
if not m:
    sys.exit('gloss.js 에서 용어 목록을 찾지 못했습니다')
G = json.loads(m.group(1))
print(f'사전 용어 {len(G)}개')

# ── 약관 본문 읽기 ──────────────────────────────────────────
html = open(TOOL, encoding='utf-8').read()
D = inflate(json.loads(re.search(r'<script id="DATA" type="application/json">(.*?)</script>', html, re.S).group(1)))
riders, tables = D['riders'], D['tables']
print(f'약관 특약 {len(riders)}건 · 분류표 {len(tables)}건 · 버전 {D["meta"].get("version")}')

# ── 1. 사전에 없는 빈출 용어 후보 ──────────────────────────
HAN = re.compile(r'[가-힣]{3,12}')
# 조사·어미가 붙은 어절을 걸러내기 위한 꼬리 목록
TAIL = ('습니다','합니다','됩니다','하여야','하지만','으로서','으로써','에서는','에게는','까지는',
        '이라고','라고','으로','에서','에게','까지','부터','에는','과의','와의','보다','처럼',
        '하는','하지','하고','하여','되는','되며','되어','된다','한다','있는','없는','같은',
        '은','는','이','가','을','를','의','에','로','와','과','도','만','며','고','한','된','될','함','및')
VERB_END = ('하다','한다','된다','합니','됩니','하며','되며','하지','되지','하고','되고','하여','되어',
            '했다','였다','이다','이며','임','함','됨','짐','옴',
            '되','시','키','지','며','서','도','나','면','만','까','때','든','든지',
            '한','된','될','는','가','난','든','람','겨','러','려','야')
STOP = set('''있습니다 없습니다 합니다 됩니다 경우에는 때에는 이라고 다음과 각각의 대하여 관하여
하는 경우 지급합니다 지급하지 해당하는 말합니다 보험금을 계약자 회사는 피보험자 보험수익자
그러하지 아니합니다 위하여 따라서 그리고 또는 다만 이내에 이상인 이하인 한하여 하나에
특별약관 보험금 회사가 회사는 그러나 이러한 동일한 다음의 각호의 해당하 경우가 때에도'''.split())

def strip_tail(tok):
    """어절 끝의 조사·어미를 떼어 낱말만 남긴다"""
    for t in sorted(TAIL, key=len, reverse=True):
        if len(tok) - len(t) >= 3 and tok.endswith(t):
            return tok[:-len(t)]
    return tok

def looks_like_word(tok):
    if len(tok) < 3 or tok in STOP:
        return False
    if tok.endswith(VERB_END):          # 동사·형용사 활용형
        return False
    if tok[-1] in '은는이가을를의에로와과도만며고나면야겨러려다으하':   # 조사가 그대로 남은 것
        return False
    if tok.startswith(('때','그','이','저','각','다음','아니','불구','있어','없어')):
        return False
    return True

def covered(tok):
    """사전 용어가 이 낱말 안에 들어 있으면 이미 설명이 붙는 것으로 본다"""
    return any(t in tok for t in G_sorted if len(t) >= 3)

G_sorted = sorted(G, key=len, reverse=True)
G_set = set(G)

doc_freq = collections.Counter()   # 몇 개의 특약에 등장했나 (빈도보다 신뢰도 높음)
for r in riders:
    toks = set()
    for raw in HAN.findall(r.get('b') or ''):
        w = strip_tail(raw)
        if looks_like_word(w) and w not in G_set:
            toks.add(w)
    for t in toks:
        doc_freq[t] += 1

cand = [(c, t) for t, c in doc_freq.items() if c >= max(5, len(riders) // 100)]
cand = [(c, t) for c, t in cand if not covered(t)]
cand.sort(reverse=True)

print(f'\n[1] 사전에 없는 빈출 낱말 상위 {TOP}개 — 새 용어 후보')
if not cand:
    print('   없음 (사전이 약관을 충분히 덮고 있습니다)')
for c, t in cand[:TOP]:
    print(f'   {c:>4}개 특약   {t}')

# ── 2. 약관에 더 이상 안 나오는 사전 용어 ──────────────────
body_all = '\n'.join((r.get('b') or '') for r in riders)
tbl_all = '\n'.join((t.get('text') or '') for t in tables.values())
name_all = '\n'.join(r.get('n') or '' for r in riders)
haystack = body_all + tbl_all + name_all
gone = [t for t in G if t not in haystack]
print(f'\n[2] 약관 어디에도 안 나오는 사전 용어 {len(gone)}개')
print('    (질병·제도 설명용 일반 용어가 대부분이라 지우지 않아도 됩니다)')
for t in gone[:20]:
    print(f'   {t}  [{G[t]["c"]}]')
if len(gone) > 20:
    print(f'   … 외 {len(gone)-20}개')

# ── 3. 별칭 ↔ 검색 동의어 정합성 ───────────────────────────
SYN = D.get('synonyms', {})
ALIAS = D.get('aliases', {})
print(f'\n[3] 검색 동의어 {len(SYN)}개 · 별칭 {len(ALIAS)}개')
bad = [k for k in ALIAS if k in SYN]
print('   동의어와 겹치는 별칭:', bad if bad else '없음 (정상)')
# 별칭은 사전 용어 자체이거나, 어떤 용어의 별칭(a) 목록에 들어 있어야 근거가 있다
alias_pool = set()
for a in G.values():
    for one in re.split(r'[·,/]', a.get('a') or ''):
        if one.strip():
            alias_pool.add(one.strip())
no_gloss = [k for k in ALIAS if k not in G and k not in alias_pool]
if no_gloss:
    print('   사전에 근거가 없는 별칭:', no_gloss)

print('\n끝났습니다. [1] 목록에서 설명이 필요한 말을 골라 gloss.js 에 추가하세요.')
