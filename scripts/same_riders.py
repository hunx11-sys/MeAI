# -*- coding: utf-8 -*-
"""
상품이 달라도 같은 특약 묶기 — 특약검색기·보상시뮬레이터에서 한 카드로 보이게 표시를 달아 둔다

1) 띄어쓰기만 다른 이름 바로잡기
   또또암·또또암간편 약관은 특약명이 띄어쓰기 없이 뽑혀(예: 암주요치료비(연간1회한,10년간))
   통합간편·케어프리의 같은 특약(암 주요치료비(연간1회한, 10년간))과 다른 특약처럼 보였다.
   글자가 띄어쓰기 말고는 똑같을 때만, 띄어쓰기가 있는 표기(여러 상품에서 가장 많이 쓴 것)로 맞춘다.
   스마트 제안서는 담보명을 띄어쓰기 없이 맞추므로(matcher.base · scen_engine.nname) 영향이 없다.

2) 묶어도 되는지 약관으로 판정
   이름이 같아도 상품마다 약관이 다를 수 있다(간편심사 상품의 1년 감액, 케어프리의 15세 미만 규정 등).
   아래가 모두 같을 때만 같은 특약으로 묶는다.
     · 보장 질병코드(k) · 제외코드(x) · 수가코드(hc)
     · 약관 본문의 지급비율(보험가입금액의 ○%) 모음 — 두 약관 모두 % 로 적었을 때만 비교
     · 감액기간(○년경과시점) · 90일 대기기간(보장개시일)
   15세 미만 보장개시 규정만 다르면 묶되, 그 상품 태그 옆에 적는다(성인 기준 지급 조건은 같다).
   하나라도 다르면 묶지 않고, 카드에 무엇이 다른지 적는다.

데이터에 다는 표시 (tool.html DATA 의 특약마다)
   sg : 묶음 번호 — 같은 sg 끼리 한 카드
   sv : 이 상품만의 메모(묶음 안에서 다른 점)
   sd : 같은 이름인데 약관이 달라 따로 둔 특약 [[id, 다른 점], …]

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


def feat(r):
    b = re.sub(r'\s+', '', r.get('b') or '')
    return {
        'codes': tuple(tuple(sorted(r.get(f) or [])) for f in ('k', 'x', 'hc')),
        # 감액 : 「계약일부터 1년(90일) 경과시점」 전에는 일부만 지급
        'red': tuple(sorted(set(re.findall(r'(\d+(?:년|일))경과시점', b)))),
        # 대기 : 보장개시일을 계약일부터 90일 지난 날로 정함(그 전 진단은 보장 안 함)
        'wait': bool(re.search(r'보장개시일[^.]{0,80}90일|90일[^.]{0,60}보장개시', b)),
        'pct': tuple(sorted(set(re.findall(r'보험가입금액의(\d+)%', b)), key=int)),
        'age15': '15세미만' in b,
    }


HARD = ('codes', 'red', 'wait', 'pct')     # 다르면 묶지 않는다


def same(fa, fb):
    """지급비율은 두 약관 모두 '보험가입금액의 ○%' 로 적었을 때만 비교한다
    (금액표를 % 없이 적은 약관이 있어, 적는 방식 차이로 갈라지지 않게)"""
    for h in HARD:
        if h == 'pct' and not (fa['pct'] and fb['pct']): continue
        if fa[h] != fb[h]: return False
    return True


def diff_text(a, fa, b, fb):
    """a 카드에 적을 문구 — b(다른 상품)와 무엇이 다른지"""
    out = []
    if fa['codes'] != fb['codes']: out.append('보장 질병코드 범위가 다름')
    if fa['red'] != fb['red']:
        if fa['red'] and not fb['red']: out.append('이 상품은 가입 %s 내 감액' % '·'.join(fa['red']))
        elif fb['red'] and not fa['red']: out.append('%s는 가입 %s 내 감액' % (b['p'], '·'.join(fb['red'])))
        else: out.append('감액기간이 다름')
    if fa['wait'] != fb['wait']:
        out.append('이 상품은 90일 보장개시(대기) 규정' if fa['wait'] else '%s는 90일 보장개시(대기) 규정' % b['p'])
    if fa['pct'] and fb['pct'] and fa['pct'] != fb['pct'] and fa['red'] == fb['red']: out.append('지급비율이 다름')
    if fa['age15'] != fb['age15']: out.append('15세 미만 규정이 다름')
    return ' · '.join(out) or '약관 조건이 다름'


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

    # 1-2) 또또암 두 상품은 세부보장 이름을 '부모[세부]' 로 적는다 — 앞의 부모 부분도 같은 띄어쓰기로
    #      (이름 모양 자체는 그대로 둔다 : 스마트 제안서가 설계서의 '부모[세부]' 표기를 이 이름으로 찾는다)
    for r in R:
        par = RM.get(r.get('parent'))
        if not par: continue
        pk, n = nk(par['n']), r['n']
        if not nk(n).startswith(pk + '[') or n.startswith(par['n'] + '['): continue
        i = c = 0
        while c < len(pk):                       # 띄어쓰기를 빼고 부모 이름만큼 글자를 센 자리
            if not n[i].isspace(): c += 1
            i += 1
        new = par['n'] + n[i:].lstrip()
        if nk(new) == nk(n) and new != n:
            renamed.append((r['id'], n, new)); r['n'] = new

    # 2) 묶음 판정 — 세부보장은 부모 이름이 같고, 세부 이름(부모[세부] 꼴이면 [ ] 안)이 같아야 같은 특약
    def key(r):
        par = RM.get(r.get('parent'))
        if not par: return nk(r['n'])
        pk, n = nk(par['n']), nk(r['n'])
        if n.startswith(pk + '[') and n.endswith(']'): n = n[len(pk) + 1:-1]
        return pk + '›' + n
    groups = collections.defaultdict(list)
    for r in R: groups[key(r)].append(r)
    F = {r['id']: feat(r) for r in R}
    sg_n = merged = split = 0
    for k, v in groups.items():
        if len({r['p'] for r in v}) < 2: continue
        v = sorted(v, key=lambda r: ORDER.index(r['p']) if r['p'] in ORDER else 99)
        clusters = []
        for r in v:
            for c in clusters:
                f0 = F[c[0]['id']]
                if r['p'] not in {x['p'] for x in c} and same(F[r['id']], f0):
                    c.append(r); break
            else:
                clusters.append([r])
        for c in clusters:
            if len(c) > 1:
                sg_n += 1; merged += len(c)
                for r in c: r['sg'] = 's%d' % sg_n
                ages = {F[r['id']]['age15'] for r in c}
                if len(ages) > 1:
                    for r in c:
                        if F[r['id']]['age15']: r['sv'] = '15세 미만 보장개시 별도 규정'
        if len(clusters) > 1:
            for c in clusters:
                for r in c:
                    others = [o for c2 in clusters if c2 is not c for o in c2 if o['p'] != r['p']]
                    if others:
                        r['sd'] = [[o['id'], diff_text(r, F[r['id']], o, F[o['id']])] for o in others]
                        split += 1

    print('띄어쓰기 바로잡은 특약명 %d건' % len(renamed))
    for x in renamed[:12]: print('   %s  %s  →  %s' % x)
    print('여러 상품에 같은 이름 : 묶음 %d개(특약 %d건) · 약관이 달라 따로 둔 특약 %d건' % (sg_n, merged, split))
    ex = [r for r in R if r.get('sd')][:10]
    for r in ex: print('   따로 :', r['id'], r['p'], r['n'][:30], '|', r['sd'][0][1])
    if '--write' in sys.argv:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 저장')


if __name__ == '__main__':
    main()
