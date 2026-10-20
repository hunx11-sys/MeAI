# -*- coding: utf-8 -*-
"""
v8.78 되돌림 — 다빈도61대(130대) · 다빈도62대(131대)의 황반변성(H35.3)은 보장이다

약관 분류표에 「시각질환 · 황반변성 · 황반 및 후극부의 변성 · H35.3」이 따로 한 줄로 들어 있다
(케어프리 M-Basket 약관 938쪽 다빈도62대 · 통합간편 약관 다빈도61대 분류표 같은 자리).
바로 아래 「맥락막 및 망막의 장애 H30-H36 — 단, 아래질병은 제외 ② 황반 및 후극부의 변성(H35.3)」은
앞 줄과 겹치지 않게 빼 둔 것일 뿐이다. v8.78 에서 이 제외 문구만 보고 H35.3 을 x 로 옮긴 것을 원래대로 돌린다.
(H35.0 중 고혈압성 망막병증 · H36.0 당뇨병성 망막병증 제외는 그대로 — 둘 다 특정31대 쪽에 있다)

실행 : python3 scripts/fix_h353_2610.py [--write]
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import PAT, inflate, deflate, ROOT

TOOL = os.path.join(ROOT, 'tool.html')
# 특약 id → (k 안 자리, 세부보장이면 l 라벨) — v8.78 직전 tool.html 과 같은 자리
FIX = {'통123': (72, None), '통123-4': (91, '황반변성 황반 및 후극부의 변성'),
       '케219': (133, None), '케219-4': (49, '황반 및 후극부의 변성'),
       '케220': (133, None), '케220-4': (49, '황반 및 후극부의 변성')}


def main(write):
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    by = {r['id']: r for r in D['riders']}
    for i, (pos, lab) in FIX.items():
        r = by[i]
        if 'H35.3' in r['k']:
            print(i, '이미 보장'); continue
        r['x'] = [c for c in r['x'] if c != 'H35.3']
        r['k'].insert(pos, 'H35.3')
        if lab is not None:
            r['l'].insert(pos, lab)
        print('%s %s : H35.3 보장으로 · k %d · x %s' % (i, r['n'], len(r['k']), r['x']))
    if write:
        html = html[:m.start(2)] + json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[m.end(2):]
        io.open(TOOL, 'w', encoding='utf-8').write(html)
        print('tool.html 저장')


if __name__ == '__main__':
    main('--write' in sys.argv)
