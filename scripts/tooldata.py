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

약관 본문은 tool_body.js 로 따로 둔다 (2026.09 — 인터넷 버전 속도)
  tool.html 의 DATA 에는 목록·질병코드·분류표만 남기고, 본문("b")은 옆 파일 tool_body.js 에 싣는다.
  브라우저는 화면을 먼저 띄운 뒤 tool_body.js 를 불러 본문을 채운다(23MB → 첫 화면 6MB).
  inflate() 는 DATA 에 본문이 없으면 tool_body.js 에서 읽어 채우고,
  deflate() 는 본문을 떼어 tool_body.js 에 다시 쓴다 — 그래서 이 두 함수를 쓰는 스크립트는 그대로 동작한다.
  DATA 를 정규식으로 직접 읽는 스크립트는 본문 없이 목록만 보게 된다(질병코드·분류표 추출에는 충분).
  메일·올인원 배포판은 pack_html() 로 본문을 압축해 파일 안(BODYZ)에 다시 넣는다.

실행 : python3 scripts/tooldata.py        (DATA 안에 본문이 있으면 tool_body.js 로 떼어 내고, 풀었을 때 원래와 같은지 전부 대조)
"""
import base64, gzip, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY = os.path.join(ROOT, 'tool_body.js')
_CALL = '__MEAI_BODY_LOAD__('


def read_bodies(path=BODY):
    s = io.open(path, encoding='utf-8').read()
    return json.loads(s[s.index(_CALL) + len(_CALL):s.rindex(')')])


def write_bodies(B, path=BODY):
    """특약 하나가 한 줄 — 고친 특약만 변경 기록에 잡힌다"""
    lines = ',\n'.join(json.dumps(k, ensure_ascii=False) + ':' + json.dumps(v, ensure_ascii=False) for k, v in B.items())
    txt = ('/* 특약검색기(tool.html) 약관 본문 — tool.html 이 화면을 띄운 뒤 불러 채운다.\n'
           '   직접 고치지 말고 scripts/tooldata.py 의 inflate/deflate 를 쓰는 스크립트로 고친다. */\n'
           + _CALL + '{\n' + lines + '\n});\n')
    if not os.path.exists(path) or io.open(path, encoding='utf-8').read() != txt:
        io.open(path, 'w', encoding='utf-8').write(txt)


def inflate(D):
    if not any('b' in r for r in D['riders']) and os.path.exists(BODY):
        B = read_bodies()
        for r in D['riders']:
            if r['id'] in B: r['b'] = B[r['id']]
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
    B = {r['id']: r.pop('b') for r in D['riders'] if 'b' in r}
    if B: write_bodies(B)
    return D


def pack_html(s):
    """배포판용 : tool.html 글에 약관 본문을 gzip 으로 압축해 BODYZ 로 넣는다(파일 하나로 동작)"""
    m = re.search(PAT, s, re.S)
    if not m or '__MEAI_BODY__' not in s or 'id="BODYZ"' in s:
        return s, 0
    D = json.loads(m.group(2))
    B = {r['id']: r.pop('b') for r in D['riders'] if 'b' in r}
    if not B and os.path.exists(BODY): B = read_bodies()
    z = base64.b64encode(gzip.compress(json.dumps(B, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return s[:m.start(2)] + data + m.group(3) + '\n<script id="BODYZ" type="text/plain">' + z + '</script>' + s[m.end(3):], len(B)


PAT = r'(<script id="DATA" type="application/json">)(.*?)(</script>)'

if __name__ == '__main__':
    TOOL = os.path.join(ROOT, 'tool.html')
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    before = json.dumps(D, ensure_ascii=False, sort_keys=True)
    body = json.dumps(deflate(json.loads(before)), ensure_ascii=False, separators=(',', ':'))
    # 되돌렸을 때 한 글자라도 다르면 저장하지 않는다 (본문은 방금 쓴 tool_body.js 에서 다시 읽어 대조)
    again = json.dumps(inflate(json.loads(body)), ensure_ascii=False, sort_keys=True)
    if again != before: sys.exit('풀었을 때 원래와 다름 — 저장하지 않음')
    new = html[:m.start(2)] + body + html[m.end(2):]
    io.open(TOOL, 'w', encoding='utf-8').write(new)
    print('tool.html %.1fMB → %.1fMB · 약관 본문 tool_body.js %.1fMB' % (len(html.encode()) / 1e6, len(new.encode()) / 1e6, os.path.getsize(BODY) / 1e6))
