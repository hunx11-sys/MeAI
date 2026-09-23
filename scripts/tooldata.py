# -*- coding: utf-8 -*-
"""
특약검색기(tool.html) 내장 DATA 읽기·쓰기 도우미 — 세부보장 약관 본문 중복 저장 없애기

세부보장 특약(예: 암종별(30종)통합암진단비[위암])은 부모 특약의 약관 전문을 그대로 쓴다.
예전에는 세부마다 같은 전문을 한 부씩 복사해 두어 파일의 40%(약 17MB)가 같은 글이었다.
지금은 부모와 글자까지 같은 본문이면 세부 쪽 "b" 를 지우고 "bp":1 (= 부모 본문을 씀) 만 남긴다.
브라우저는 tool.html 이 열릴 때 부모 본문을 다시 채워 넣으므로 화면·검색은 전과 같다.

DATA 를 읽고 고치는 파이썬 스크립트는 이 두 함수를 쓴다.
    D = inflate(json.loads(...))      # 읽은 직후 : 세부 본문을 부모에서 채움
    json.dumps(deflate(D), ...)       # 쓰기 직전 : 부모와 같은 세부 본문을 다시 비움

실행 : python3 scripts/tooldata.py        (tool.html 을 한 번 압축하고, 풀었을 때 원래와 같은지 전부 대조)
"""
import io, json, os, re, sys


def inflate(D):
    by = {r['id']: r for r in D['riders']}
    for r in D['riders']:
        if r.pop('bp', None):
            r['b'] = by[r['parent']]['b']
    return D


def deflate(D):
    by = {r['id']: r for r in D['riders']}
    for r in D['riders']:
        p = by.get(r.get('parent'))
        if p is not None and r.get('b') and r['b'] == p.get('b'):
            del r['b']
            r['bp'] = 1
    return D


PAT = r'(<script id="DATA" type="application/json">)(.*?)(</script>)'

if __name__ == '__main__':
    TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tool.html')
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    before = json.dumps(D, ensure_ascii=False, sort_keys=True)
    body = json.dumps(deflate(json.loads(before)), ensure_ascii=False, separators=(',', ':'))
    # 되돌렸을 때 한 글자라도 다르면 저장하지 않는다
    again = json.dumps(inflate(json.loads(body)), ensure_ascii=False, sort_keys=True)
    if again != before: sys.exit('풀었을 때 원래와 다름 — 저장하지 않음')
    new = html[:m.start(2)] + body + html[m.end(2):]
    io.open(TOOL, 'w', encoding='utf-8').write(new)
    n = sum(1 for r in json.loads(body)['riders'] if r.get('bp'))
    print('세부보장 %d건 본문을 부모와 공유 · tool.html %.1fMB → %.1fMB' % (n, len(html.encode()) / 1e6, len(new.encode()) / 1e6))
