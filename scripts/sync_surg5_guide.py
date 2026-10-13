# -*- coding: utf-8 -*-
"""1-5종 사용지침 5 판정표(proposal_smart/surg5_guide.json) → 영업지원도구(tool.html) 「수술비 비교」 창의 SC.guide

스마트 제안서 계산 엔진(scen_engine.SURG5_GUIDE)과 영업지원도구가 같은 판정표를 쓰도록, 표는 json 한 곳에서만 고치고
이 스크립트로 tool.html 에 옮겨 적는다. sync_all.py 가 1단계 전에 부른다.
실행 : python3 scripts/sync_surg5_guide.py
"""
import io, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = json.load(io.open(os.path.join(ROOT, 'proposal_smart', 'surg5_guide.json'), encoding='utf-8'))
T = os.path.join(ROOT, 'tool.html')
s = io.open(T, encoding='utf-8').read()
line = '  SC.guide=' + json.dumps(G, ensure_ascii=False, separators=(',', ':')) + ';'
if re.search(r'^  SC\.guide=.*;$', s, re.M):
    s2 = re.sub(r'^  SC\.guide=.*;$', lambda m: line, s, count=1, flags=re.M)
else:
    m = re.search(r'^  SC\.d131=.*;$', s, re.M)
    if not m: raise SystemExit('tool.html 에서 SC.d131 줄을 찾지 못했습니다')
    s2 = s[:m.end()] + '\n' + line + s[m.end():]
if s2 != s:
    io.open(T, 'w', encoding='utf-8').write(s2); print('tool.html SC.guide 갱신 (시술 %d건)' % len(G['items']))
else:
    print('tool.html SC.guide 그대로 (시술 %d건)' % len(G['items']))
