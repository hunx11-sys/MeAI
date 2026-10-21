# -*- coding: utf-8 -*-
"""
약관 본문 「가입금액별 지급표」 점검 — sync_all.py 가 매번 돌린다 (2026-10-21)

왜 : 두 단 조판 약관을 뽑다가 「<보험가입금액 4,000만원>」 다음에 바로 「<보험가입금액 8,000만원>」이 오고
     4,000만원 표가 8,000만원 밑에 붙는 일이 47개 특약에서 있었다(scripts/fix_table_order.py 로 바로잡음).
     같은 일이 다시 생기면 여기서 막는다.

점검
  1) 가입금액 제목마다 그 밑(다음 제목 · 다음 항 전)에 지급표가 하나 이상 있는가
  2) 가입금액이 큰 제목일수록 같은 줄의 지급금액이 같거나 커지는가(작아지면 표가 뒤섞인 것)
  3) 통합간편 특약의 표 금액 = 스마트 제안서 · 통합치료비 시뮬레이터 계산표(proposal_smart/product_data.json AMT)
  4) 같은 이름 특약(상품만 다름)의 가입금액별 금액이 서로 같은가 — 이름이 같으면 약관도 같다

실행 : python3 scripts/check_body_tables.py      (문제가 있으면 종료코드 1)
"""
import io, json, os, re, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import inflate, PAT, ROOT

# 약관 PDF 원본에 표가 없는 것(지어 넣지 않는다) — 특약 id : {제목 금액(만원) : 사유}
KNOWN_MISSING = {
    '통137': {3000: '통합간편 2607(통합간편심사형) 약관 629쪽 — 「<보험가입금액 3,000만원>」 제목만 있고 표가 없음(약관 인쇄본 누락). '
                    '같은 특약 케어프리 약관(케214)에는 250만원/500만원 표가 있음'},
}


def nk(t): return re.sub(r'\s+', '', t or '')


def tier_of(h):
    t = nk(h).replace(',', '')
    if '월간' in t:
        m = re.search(r'(\d+)만원', t); return ('월', int(m.group(1))) if m else None
    m = re.search(r'(\d+)억(?:(\d+)천)?', t)
    if m and '만원' not in t: return int(m.group(1)) * 10000 + int(m.group(2) or 0) * 1000
    m = re.search(r'(?:(\d+)억)?(\d+)만원', t)
    return (int(m.group(1) or 0) * 10000 + int(m.group(2))) if m else None


def amounts(body):
    """가입금액표 묶음들 — 항마다 따로(한 특약에 ⑤항 · ⑥항처럼 가입금액표가 두 벌인 것이 있다)
       → [{제목 금액 : [지급금액…]}, …], [{제목 금액 : 표 수}, …]"""
    sets, ntabs, cur = [], [], None
    L = body.split('\n'); i = 0; fresh = True
    while i < len(L):
        l = L[i]
        if l.strip().startswith('<보험가입금액'):
            if fresh: sets.append(collections.OrderedDict()); ntabs.append(collections.Counter()); fresh = False
            cur = tier_of(l); sets[-1].setdefault(cur, []); i += 1; continue
        if re.match(r'\s*[①-⑳]|제\d+조', l): cur = None; fresh = True
        if l.startswith('[표:'):
            hdr = int(re.sub(r'\D', '', l) or 1); j = i + 1 + hdr
            if cur is not None and '대상질병' in L[i + 1]: cur = None
            if cur is not None: ntabs[-1][cur] += 1
            while j < len(L) and '|' in L[j]:
                v = L[j].split('|')[-1].replace(' ', '').replace(',', '')
                if cur is not None and re.fullmatch(r'\d+만원', v): sets[-1][cur].append(int(v[:-2]))
                j += 1
            i = j; continue
        i += 1
    return sets, ntabs


def main():
    html = io.open(os.path.join(ROOT, 'tool.html'), encoding='utf-8').read()
    D = inflate(json.loads(re.search(PAT, html, re.S).group(2)))
    bad = []
    by_name = collections.defaultdict(list)
    for r in D['riders']:
        if r.get('parent') or '<보험가입금액' not in (r.get('b') or ''): continue
        sets, ntabs = amounts(r['b'])
        by_name[nk(r['n'])].append((r, sets))
        for out, ntab in zip(sets, ntabs):
            # 1) 제목 밑 표
            for t in out:
                if not ntab[t] and t not in KNOWN_MISSING.get(r['id'], {}):
                    bad.append('%s %s : 「%s」 제목 밑에 지급표가 없음' % (r['id'], r['n'], t))
            # 2) 금액이 작아지면 뒤섞인 것
            seq = [(t, v) for t, v in out.items() if v and isinstance(t, int)]
            for (t1, a), (t2, b) in zip(seq, seq[1:]):
                if t2 > t1 and len(a) == len(b) and any(y < x for x, y in zip(a, b)):
                    bad.append('%s %s : %s → %s 에서 지급금액이 작아짐(표가 뒤섞였을 수 있음)' % (r['id'], r['n'], t1, t2))
    # 3) 계산표와 같은가
    P = json.load(open(os.path.join(ROOT, 'proposal_smart', 'product_data.json'), encoding='utf-8'))
    ty2nm = {}
    for x in P['RIDERS']: ty2nm.setdefault(x['ty'], x['nm'])
    n3 = 0
    for ty, tab in P['AMT'].items():
        rs = [(r, o) for r, o in by_name.get(nk(ty2nm.get(ty)), []) if r['p'] == '통합간편']
        if not rs: continue
        r, sets = rs[0]
        out = sets[0] if sets else {}                               # 계산표는 첫 벌(기본 지급표)
        for tier, vals in tab.items():
            got = out.get(int(tier))
            if got == [] and int(tier) in KNOWN_MISSING.get(r['id'], {}): continue
            n3 += 1
            if got != vals:
                bad.append('%s %s %s만원 : 약관 표 %s ≠ 계산표 %s' % (r['id'], r['n'], tier, got, vals))
    # 4) 같은 이름 특약끼리
    for nm, lst in by_name.items():
        base = next(((r, o) for r, o in lst if r['p'] == '통합간편'), lst[0])
        for r, sets in lst:
            for si, o in enumerate(sets):
              if si >= len(base[1]): break
              for t, v in o.items():
                bv = base[1][si].get(t)
                if v and bv and v != bv:
                    bad.append('%s(%s) ↔ %s(%s) %s : 같은 이름인데 금액이 다름' % (r['id'], r['p'], base[0]['id'], base[0]['p'], t))
    print('가입금액표 특약 %d개 · 계산표 대조 %d건 · 알려진 약관 누락 %d건'
          % (sum(len(v) for v in by_name.values()), n3, sum(len(v) for v in KNOWN_MISSING.values())))
    for b in bad: print('  ✖', b)
    if bad:
        print('문제 %d건 — scripts/fix_table_order.py 로 표 자리를 바로잡고 약관 PDF 로 확인하세요' % len(bad))
        sys.exit(1)
    print('✓ 이상 없음')


if __name__ == '__main__':
    main()
