# -*- coding: utf-8 -*-
"""
세부보장 레코드에 빠진 제외 질병코드(x)를 부모 특약 것으로 채운다 (v8.92 · 2026-11-10)

약관이 「…아래의 질병 특정 비급여,신의료기술치료비에 대하여는 보상하지 않습니다」 처럼 특약 전체(모든 세부보장)에 대해
제외 질병을 정했는데, 세부보장 레코드(또246-1 「…[1종 근골 및 하지정맥류질환]」 등)에는 제외코드가 비어 있었다.
같은 특약 케어프리(케333-n)는 세부보장에도 같은 제외코드가 있다 — 이름이 같으면 약관 별표도 같다.

채우는 조건(셋 다) — 추정하지 않는다
  1. 세부보장의 제외코드가 비어 있고 부모 특약에는 있다
  2. 부모 특약 약관 본문에 「아래의 <특약 이름 알맹이>에 대하여는 보상하지 않」 문구가 있다(특약 전체에 대한 제외)
  3. 부모 제외코드를 그대로 쓴다(코드를 새로 만들지 않는다)

실행 : python3 scripts/fix_sub_excl.py           (바뀔 것만 보기)
       python3 scripts/fix_sub_excl.py --write   (tool.html 에 반영 → 이어서 same_riders.py --write · sync_all.py)
보강 마스터(db_terms_extra.json)는 같은 이름 감수본 코드를 쓰므로 sync_all 의 약관 재추출 때 따라 바뀐다.
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tooldata import inflate, deflate, PAT, ROOT

TOOL = os.path.join(ROOT, 'tool.html')
nz = lambda s: re.sub(r'\s', '', s or '')


def core(n):
    """특약 이름 알맹이 — 갱신형 · 끝 괄호(1-3종, 연간1회한) · 가입 꼬리표를 뗀다"""
    t = re.sub(r'^(\(\d+년갱신\))?갱신형', '', nz(n))
    t = re.sub(r'\[.*\]$', '', t)
    while re.search(r'\([^()]*\)$', t): t = re.sub(r'\([^()]*\)$', '', t)
    return t


def main():
    write = '--write' in sys.argv
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    by = {r['id']: r for r in D['riders']}
    n = 0
    for r in D['riders']:
        P = by.get(r.get('parent'))
        if not P or r.get('x') or not P.get('x'): continue
        body = nz(P.get('b') or '')
        c = core(P['n'])
        if not c or ('아래의' + c + '에대하여는보상하지않') not in body: continue
        print('  %-8s %s  제외코드 %d줄 ← %s (약관 「아래의 %s에 대하여는 보상하지 않습니다」)' % (r['id'], r['n'], len(P['x']), P['id'], c))
        r['x'] = list(P['x']); n += 1
    print('세부보장 제외코드 채움 %d건' % n)
    if write and n:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 에 반영 — 이어서 python3 scripts/same_riders.py --write · python3 scripts/sync_all.py')


if __name__ == '__main__':
    main()
