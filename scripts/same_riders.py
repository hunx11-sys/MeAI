# -*- coding: utf-8 -*-
"""
상품이 달라도 같은 특약 묶기 — 특약검색기·보상시뮬레이터에서 한 카드로 보이게 표시를 달아 둔다

1) 띄어쓰기만 다른 이름 바로잡기
   또또암·또또암간편 약관은 특약명이 띄어쓰기 없이 뽑혀(예: 암주요치료비(연간1회한,10년간))
   통합간편·케어프리의 같은 특약(암 주요치료비(연간1회한, 10년간))과 다른 특약처럼 보였다.
   글자가 띄어쓰기 말고는 똑같을 때만, 띄어쓰기가 있는 표기(여러 상품에서 가장 많이 쓴 것)로 맞춘다.
   스마트 제안서는 담보명을 띄어쓰기 없이 맞추므로(matcher.base · scen_engine.nname) 영향이 없다.

2) 이름이 같으면 같은 특약 (소유자 확인 2026.10)
   상품만 다른 같은 이름 특약은 약관 별표가 같다(별표 번호·쪽만 다름). 그래서 한 카드로 묶는다.
   세부보장은 부모 이름이 같고 세부 이름이 같을 때 같은 특약(또또암의 '부모[세부]' 표기도 [ ] 안으로 비교).
   · 질병코드가 다르면 그건 데이터 오류다 — 묶음마다 보장·제외 질병코드와 수가코드를 실제로 덮는 범위로
     대조해(C40~C41 = C40·C41) 다르면 '확인 필요'로 출력한다. 출력이 나오면 약관 별표로 데이터를 바로잡는다
     (scripts/fix_same_terms.py 가 그렇게 고친 기록).
   · 간편심사 상품의 감액(예 : 통합간편 「계약일부터 1년 경과시점 전일 이전 50%」)은 약관 지급표에 실제로
     적힌 차이라, 카드는 묶되 그 상품 태그 옆에 적는다(sv). 보장개시 문구 정도의 차이는 적지 않는다.

데이터에 다는 표시 (tool.html DATA 의 특약마다)
   sg : 묶음 번호 — 같은 sg 끼리 한 카드
   sv : 이 상품만의 지급 메모(예 : 가입 1년 내 50%)

실행 : python3 scripts/same_riders.py            (결과만 보기)
       python3 scripts/same_riders.py --write    (tool.html 에 반영)
특약 데이터를 고친 뒤(새 상품·약관 개정)에는 다시 돌린다.
"""
import collections, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import inflate, deflate, PAT, ROOT

TOOL = os.path.join(ROOT, 'tool.html')
ORDER = ['통합간편', '케어프리', '운전자', '치아', '또또암', '또또암간편']   # 대표 카드로 앞세울 순서


def nk(n): return re.sub(r'\s+', '', n or '')


# ── 질병코드 목록이 실제로 덮는 범위 비교 (표기 차이 무시) ──
def _expand(t):
    """한 표기 → 비교용 코드들(범위는 풀어서). 'C40~C41' → C40,C41 · 'Q26.0~Q26.4' → Q26.0..Q26.4"""
    t = t.strip().replace('∼', '~')
    if '~' not in t: return [t]
    a, b = t.split('~')
    if not b[0].isalpha(): b = a[0] + b
    if '.' not in a and '.' not in b:
        if a[0] != b[0]: return [a, b]
        return ['%s%02d' % (a[0], i) for i in range(int(a[1:3]), int(b[1:3]) + 1)]
    a3, b3 = a.split('.')[0], b.split('.')[0]
    if a3 == b3 and '.' in a and '.' in b:
        x, y = a.split('.')[1], b.split('.')[1]
        w = max(len(x), len(y))
        return ['%s.%0*d' % (a3, len(x) if len(x) == len(y) else 1, i) for i in range(int(x), int(y) + 1)] if len(x) == len(y) else [a, b]
    return [a, b]


def covers(toks, code):
    c3 = code.split('.')[0]
    for t in toks:
        for e in _expand(t):
            if e == code or ('.' not in e and e == c3) or ('.' in e and code.startswith(e)): return True
    return False


def same_codes(a, b):
    """두 코드 목록이 덮는 범위가 같은가 — 두 목록에 나온 코드를 하나씩 서로 대조"""
    probe = {e for t in list(a) + list(b) for e in _expand(t)}
    return all(covers(a, c) == covers(b, c) for c in probe)


def red_note(r):
    """간편심사 등 감액 — 약관 지급표의 '계약일부터 ○ 경과시점 전일 이전 … ○%' (구간이 여럿이면 모두)"""
    b = re.sub(r'\s+', '', r.get('b') or '')
    i = b.find('제1조'); j = b.find('제2조(', i + 3)
    s = b[i:j] if i >= 0 and j > i else b[:4000]
    periods = []
    for p in re.findall(r'계약일부터(\d+(?:년|일))경과시점전일이전', s):
        if p not in periods: periods.append(p)
    if not periods: return ''
    k = s.find('계약일부터%s경과시점전일이전' % periods[0])
    pct = [int(v) for v in re.findall(r'보험가입금액의(\d+)%', s[k:k + 3000])]
    n = len(periods)
    for i in range(len(pct) - n):          # 감액이 실제로 있는 첫 줄 : ○% … → 100%
        w = pct[i:i + n + 1]
        if w[-1] == 100 and all(v < 100 for v in w[:-1]) and w[:-1] == sorted(w[:-1]):
            return '가입 ' + ' · '.join('%s 내 %d%%' % (p, v) for p, v in zip(periods, w)) + ' 지급'
    return '가입 %s 내 감액' % ' · '.join(periods)


def main():
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    R = D['riders']; RM = {r['id']: r for r in R}
    for r in R:
        for f in ('sg', 'sv', 'sd'): r.pop(f, None)

    # 1) 띄어쓰기만 다른 이름
    by = collections.defaultdict(list)
    for r in R: by[nk(r['n'])].append(r)
    renamed = []
    for k, v in by.items():
        spells = collections.Counter(r['n'] for r in v)
        if len(spells) < 2: continue
        spaced = [s for s in spells if re.search(r'\s', s)] or list(spells)
        best = sorted(spaced, key=lambda s: (-spells[s], min(ORDER.index(r['p']) for r in v if r['n'] == s)))[0]
        for r in v:
            if r['n'] != best:
                renamed.append((r['id'], r['n'], best)); r['n'] = best
    # 1-2) 또또암 두 상품의 세부보장 '부모[세부]' — 앞의 부모 부분도 같은 띄어쓰기로
    #      (이름 모양 자체는 그대로 둔다 : 스마트 제안서가 설계서의 '부모[세부]' 표기를 이 이름으로 찾는다)
    for r in R:
        par = RM.get(r.get('parent'))
        if not par: continue
        pk, n = nk(par['n']), r['n']
        if not nk(n).startswith(pk + '[') or n.startswith(par['n'] + '['): continue
        i = c = 0
        while c < len(pk):
            if not n[i].isspace(): c += 1
            i += 1
        new = par['n'] + n[i:].lstrip()
        if nk(new) == nk(n) and new != n:
            renamed.append((r['id'], n, new)); r['n'] = new

    # 2) 같은 이름 = 같은 특약
    def key(r):
        par = RM.get(r.get('parent'))
        if not par: return nk(r['n'])
        pk, n = nk(par['n']), nk(r['n'])
        if n.startswith(pk + '[') and n.endswith(']'): n = n[len(pk) + 1:-1]
        return pk + '›' + n
    groups = collections.defaultdict(list)
    for r in R: groups[key(r)].append(r)
    sg_n = merged = 0; check = []
    for k, v in groups.items():
        if len({r['p'] for r in v}) < 2: continue
        v = sorted(v, key=lambda r: ORDER.index(r['p']) if r['p'] in ORDER else 99)
        # 한 상품에 같은 이름이 둘 이상이면(부모가 다른 세부 등) 상품마다 첫 것만 묶는다
        seen, c = set(), []
        for r in v:
            if r['p'] not in seen: seen.add(r['p']); c.append(r)
        sg_n += 1; merged += len(c)
        for r in c: r['sg'] = 's%d' % sg_n
        notes = {r['id']: red_note(r) for r in c}
        if len(set(notes.values())) > 1:
            for r in c:
                if notes[r['id']]: r['sv'] = notes[r['id']]
        base = c[0]
        for r in c[1:]:
            for f in ('k', 'x'):
                if not same_codes(base.get(f) or [], r.get(f) or []):
                    check.append((k, f, base['id'], r['id']))
            if set(base.get('hc') or []) != set(r.get('hc') or []):
                check.append((k, 'hc', base['id'], r['id']))

    print('띄어쓰기 바로잡은 특약명 %d건' % len(renamed))
    for x in renamed[:8]: print('   %s  %s  →  %s' % x)
    print('여러 상품에 같은 이름 : 묶음 %d개(특약 %d건) · 감액 메모 %d건' % (sg_n, merged, sum(1 for r in R if r.get('sv'))))
    print('질병코드·수가코드가 어긋난 같은 특약(확인 필요) %d건' % len(check))
    for x in check[:30]: print('   확인 필요 :', x)
    if '--write' in sys.argv:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 저장')


if __name__ == '__main__':
    main()
