# Api 대조 — 파이썬 api.py 와 자바 Api 를 다른 포트에 띄워 놓고 같은 요청을 보내 상태코드 · 응답 JSON 을 견준다.
# 사용 : python3 golden/cmp_api.py <파이썬 주소 http://127.0.0.1:18081> <자바 주소 http://127.0.0.1:18082> <입력.json …>
#        (두 서버는 같은 GA_CODE_MAP · 같은 자료로 띄운다. 처리 시간 · pdf_base64 는 값이 아니라 꼴만 본다)
import sys, json, re, base64, urllib.request, urllib.error
PY, JV = sys.argv[1], sys.argv[2]; files = sys.argv[3:]
class H(dict):      # 머리 이름은 대소문자를 가리지 않는다(JDK 서버는 Content-type 꼴로 보낸다)
    def __init__(self, h): dict.__init__(self, {k.lower(): v for k, v in h.items()})
    def get(self, k, d=None): return dict.get(self, k.lower(), d)
def call(base, method, path, body=None, ctype='application/json'):
    req = urllib.request.Request(base + path, data=body, method=method, headers=({'Content-Type': ctype} if body is not None else {}))
    try:
        with urllib.request.urlopen(req, timeout=900) as r: return r.status, H(r.headers), r.read()
    except urllib.error.HTTPError as e: return e.code, H(e.headers), e.read()
bad = 0; n = 0
def same(what, a, b):
    global bad, n; n += 1
    if a != b:
        bad += 1; sa, sb = json.dumps(a, ensure_ascii=False)[:300], json.dumps(b, ensure_ascii=False)[:300]; print('다름 [%s]\n   파이썬 %s\n   자바   %s' % (what, sa, sb))
def js(b):
    try: return json.loads(b.decode('utf-8'))
    except Exception: return {'_raw': b[:80].decode('latin-1')}
def norm_all(o):
    o = dict(o); pdf = base64.b64decode(o.pop('pdf_base64', '') or b''); o['_pdf_ok'] = pdf[:5] == b'%PDF-' and len(pdf) > 100000
    o['elapsed_sec'] = isinstance(o.get('elapsed_sec'), float); o['log'] = re.sub(r'[\d.]+초\n', '초\n', o.get('log', ''), 1); return o
def both(what, method, path, body=None, ctype='application/json', norm=lambda o: o, prefix=None):
    (sa, ha, ba), (sb, hb, bb) = call(PY, method, path, body, ctype), call(JV, method, path, body, ctype)
    same(what + ' 상태코드', sa, sb)
    ja, jb = js(ba), js(bb)
    if prefix:      # 틀린 JSON 의 까닭 글자(파이썬 json 모듈의 영문)는 앞 글자만
        ja['error'] = ja.get('error', '')[:ja.get('error', '').find(prefix) + len(prefix)]; jb['error'] = jb.get('error', '')[:jb.get('error', '').find(prefix) + len(prefix)]
    same(what + ' 응답', norm(ja), norm(jb))
    for h in ('Content-Type', 'Access-Control-Allow-Origin', 'Access-Control-Allow-Methods', 'Access-Control-Allow-Headers'): same(what + ' 머리 ' + h, ha.get(h), hb.get(h))
    return sa, ja, jb
sa, ja, jb = both('health', 'GET', '/health', norm=lambda o: {k: o.get(k) for k in ('ok', 'llm', 'network')})
print('health : 파이썬 %s · 자바 %s(engine=%s)' % (ja.get('version'), jb.get('version'), jb.get('engine')))
same('health 판', jb.get('version'), ja.get('version') + '-java')
for f in files:
    body = open(f, 'rb').read(); nm = f.split('/')[-1]
    both(nm + ' check', 'POST', '/v1/ga2/json/check', body)
    both(nm + ' all', 'POST', '/v1/ga2/json/all', body, norm=norm_all)
    (sa, ha, ba), (sb, hb, bb) = call(PY, 'POST', '/v1/ga2/json/pdf', body), call(JV, 'POST', '/v1/ga2/json/pdf', body)
    same(nm + ' pdf 상태코드', sa, sb); same(nm + ' pdf 머리', (ha.get('Content-Type'), ha.get('Content-Disposition')), (hb.get('Content-Type'), hb.get('Content-Disposition')))
    same(nm + ' pdf 꼴', ba[:5] == b'%PDF-', bb[:5] == b'%PDF-')
ex = json.load(open(files[0], encoding='utf-8-sig'))
def J(o): return json.dumps(o, ensure_ascii=False).encode('utf-8')
for path in ('/v1/ga2/json/check', '/v1/ga2/json/all', '/v1/ga2/json/pdf'):
    both(path + ' 틀린 JSON', 'POST', path, b'{oops', prefix='JSON 으로 읽지 못했습니다 : ')
    both(path + ' 사양 위반(schema 2)', 'POST', path, J(dict(ex, schema=2)))
    both(path + ' 담보 없음', 'POST', path, J(dict(ex, riders=[])))
    both(path + ' 2MB 초과', 'POST', path, b'{"x":"' + b'a' * (2 * 1024 * 1024 + 10) + b'"}')
    both(path + ' UTF-8 아님', 'POST', path, b'{"product":"\xff\xfe"}')
    both(path + ' 빈 본문', 'POST', path, b'')
for path in ('/v1/ga2/json/all', '/v1/ga2/json/pdf'):
    both(path + ' 담보를 하나도 못 찾음(422)', 'POST', path, J(dict(ex, riders=[{'no': 1, 'name': '세상에없는담보가나다', 'amount': 1000000}])))
both('check 담보를 하나도 못 찾음', 'POST', '/v1/ga2/json/check', J(dict(ex, riders=[{'no': 1, 'name': '세상에없는담보가나다', 'amount': 1000000}])))
both('없는 주소(json 아래)', 'POST', '/v1/ga2/json/xxx', J(ex))
both('없는 주소 POST', 'POST', '/nothing', J(ex))
both('없는 주소 GET', 'GET', '/nothing')
for base, who in ((PY, '파이썬'), (JV, '자바')):
    s, h, b = call(base, 'OPTIONS', '/v1/ga2/json/pdf'); same(who + ' OPTIONS', (s, h.get('Access-Control-Allow-Origin'), h.get('Access-Control-Allow-Methods'), h.get('Access-Control-Allow-Headers')), (204, '*', 'GET, POST, OPTIONS', 'Content-Type'))
s, h, b = call(JV, 'POST', '/v1/ga2/pdf', b'%PDF-1.4 x', 'application/pdf'); same('자바 판 PDF 주소는 400', (s, js(b).get('ok'), '담보코드 입력' in js(b).get('error', '')), (400, False, True))
s, h, b = call(JV, 'GET', '/'); same('자바 판 첫 화면', (s, 'text/html' in h.get('Content-Type', '')), (200, True))
print('\n결과 : %s — 점검 %d개' % ('전부 통과' if not bad else '다른 곳 %d' % bad, n)); sys.exit(1 if bad else 0)
