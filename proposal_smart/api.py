# -*- coding: utf-8 -*-
"""스마트 제안서 HTTP API — 프론트엔드 연동용. 파이썬 표준 라이브러리만 사용(추가 설치 없음).

    python api.py                 # http://127.0.0.1:8080
    python api.py 0.0.0.0 9000    # 호스트·포트 지정

  GET  /                      데모 화면(web/index.html) — PDF 끌어다 놓으면 결과가 보인다
  GET  /health                상태 확인            → {"ok":true, ...}
  POST /v1/proposal/pdf       원본 PDF 업로드      → 결과 PDF(application/pdf)
  POST /v1/proposal/pages.pdf 원본 PDF 업로드      → 생성 지면만 PDF
  POST /v1/proposal/pages.html 원본 PDF 업로드     → 생성 지면 HTML(그대로 화면에 띄울 수 있음)
  POST /v1/proposal/audit     원본 PDF 업로드      → 감사 로그 JSON(요약·제외 담보와 사유)
  POST /v1/proposal/riders    원본 PDF 업로드      → 인식한 담보 목록 JSON
  POST /v1/proposal/all       원본 PDF 업로드      → 위 내용을 한 번에(JSON, PDF는 base64)

업로드 방법 두 가지 모두 받는다.
  · multipart/form-data 의 file 필드 (HTML <input type=file>)
  · Content-Type: application/pdf 로 PDF 바이트를 그대로 body 에 실어 보내기 (fetch 권장)

LLM·외부 API 호출은 없다. 실행 중 외부 통신을 하지 않는다.
"""
import base64, io, json, os, re, shutil, sys, tempfile, threading, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pipeline

VERSION = 'v8.46'
MAX_BYTES = 60 * 1024 * 1024                 # 업로드 상한 60MB
LOCK = threading.Semaphore(2)                # 동시 생성 2건까지(렌더가 무거워 과부하 방지)


def _json(o):
    return json.dumps(o, ensure_ascii=False).encode('utf-8')


ASCII_NAME = {'스마트제안서.pdf': 'smart_proposal.pdf', '생성지면.pdf': 'smart_pages.pdf'}
MIME = {'.ttf': 'font/ttf', '.otf': 'font/otf', '.png': 'image/png',
        '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.css': 'text/css; charset=utf-8'}


def html_for_web(path):
    """생성 지면 HTML을 브라우저에서 바로 볼 수 있게 고친다.

    지면 HTML은 인쇄용이라 글꼴·로고를 file:/// 절대경로로 참조한다. 브라우저는 http 문서에서
    file:/// 를 읽지 못하므로 /assets/ 경로로 바꿔 준다(같은 서버가 /assets/ 를 내려준다)."""
    h = io.open(path, encoding='utf-8').read()
    return h.replace('file://' + os.path.join(BASE, 'assets') + '/', '/assets/') \
            .replace('file://' + os.path.join(BASE, 'assets'), '/assets')


def first_file(raw, boundary):
    """multipart/form-data 본문에서 첫 번째 파일 파트의 바이트를 꺼낸다.

    파이썬 3.13에서 표준 cgi 모듈이 빠졌으므로 직접 자른다. 파일 파트는 헤더에
    filename= 이 있고, 헤더와 본문은 빈 줄(CRLF CRLF)로 나뉜다."""
    sep = b'--' + boundary.encode()
    for part in raw.split(sep):
        if b'\r\n\r\n' not in part:
            continue
        head, body = part.split(b'\r\n\r\n', 1)
        if b'filename=' not in head.lower():
            continue
        return body[:-2] if body.endswith(b'\r\n') else body    # 파트 끝 CRLF 제거
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = 'SmartProposal/' + VERSION
    protocol_version = 'HTTP/1.1'

    # ── 공통 ────────────────────────────────────────────────
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send(self, code, body, ctype='application/json; charset=utf-8', fname=None):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        if fname:
            # HTTP 헤더는 latin-1 만 담을 수 있어, 한글 파일명은 RFC 5987 방식으로 함께 넣는다
            self.send_header('Content-Disposition', 'inline; filename="%s"; filename*=UTF-8\'\'%s'
                             % (ASCII_NAME.get(fname, 'result.pdf'), quote(fname)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _err(self, code, msg):
        self._send(code, _json({'ok': False, 'error': msg}), )

    def log_message(self, fmt, *a):           # 접속 로그 한 줄로
        sys.stderr.write('[api] %s - %s\n' % (self.address_string(), fmt % a))

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.send_header('Content-Length', '0'); self.end_headers()

    # ── GET ─────────────────────────────────────────────────
    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            f = os.path.join(BASE, 'web', 'index.html')
            if not os.path.exists(f):
                return self._send(200, b'<h1>Smart Proposal API</h1><p>/health</p>', 'text/html; charset=utf-8')
            return self._send(200, open(f, 'rb').read(), 'text/html; charset=utf-8')
        if path.startswith('/assets/'):
            name = os.path.basename(path)                    # 경로 조작 차단
            f = os.path.join(BASE, 'assets', name)
            if not os.path.exists(f):
                return self._err(404, 'asset not found : ' + name)
            ct = MIME.get(os.path.splitext(name)[1].lower(), 'application/octet-stream')
            return self._send(200, open(f, 'rb').read(), ct)
        if path in ('/style.css', '/extra2.css'):
            return self._send(200, open(os.path.join(BASE, path[1:]), 'rb').read(), MIME['.css'])
        if path == '/health':
            return self._send(200, _json({'ok': True, 'version': VERSION,
                                          'python': sys.version.split()[0],
                                          'llm': False, 'network': False}))
        return self._err(404, 'not found : ' + path)

    # ── POST ────────────────────────────────────────────────
    def _read_pdf(self):
        """업로드된 PDF 바이트를 돌려준다(multipart 또는 raw body)."""
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0:
            raise ValueError('본문이 비어 있습니다 — PDF를 보내 주세요')
        if n > MAX_BYTES:
            raise ValueError('업로드 상한(%dMB)을 넘었습니다' % (MAX_BYTES // 1024 // 1024))
        raw = self.rfile.read(n)
        ctype = (self.headers.get('Content-Type') or '').lower()
        if 'multipart/form-data' in ctype:
            m = re.search(r'boundary=([^;]+)', ctype)
            if not m:
                raise ValueError('multipart boundary 가 없습니다')
            data = first_file(raw, m.group(1).strip().strip('"'))
            if data is None:
                raise ValueError('file 필드에서 PDF를 찾지 못했습니다')
            return data
        return raw                            # application/pdf 등 raw 업로드

    def do_POST(self):
        path = self.path.split('?')[0]
        if not path.startswith('/v1/proposal'):
            return self._err(404, 'not found : ' + path)
        try:
            pdf = self._read_pdf()
        except Exception as e:
            return self._err(400, str(e))
        if not pdf.startswith(b'%PDF'):
            return self._err(400, 'PDF 파일이 아닙니다')

        tmp = tempfile.mkdtemp(prefix='sp_in_')
        src = os.path.join(tmp, 'source.pdf')
        open(src, 'wb').write(pdf)
        got = LOCK.acquire(timeout=180)
        if not got:
            shutil.rmtree(tmp, ignore_errors=True)
            return self._err(503, '처리 대기가 길어졌습니다 — 잠시 후 다시 시도해 주세요')
        try:
            if path == '/v1/proposal/riders':                     # 담보 인식만(빠름)
                rid = pipeline.read_riders(src)
                return self._send(200, _json({'ok': True, 'count': len(rid),
                                              'matched': sum(1 for r in rid if r.get('matched')),
                                              'riders': rid}))
            r = pipeline.build(src)
            summary = {'ok': True, 'attached': r['attached'], 'base_pages': r['base_pages'],
                       'new_pages': r['new_pages'], 'total_pages': r['total_pages'],
                       'insert_after': r['insert_after'], 'rider_count': r['rider_count'],
                       'matched': r['matched'], 'elapsed_sec': r['elapsed_sec'],
                       'meta': r['meta']}
            if path in ('/v1/proposal/pdf', '/v1/proposal'):
                body = open(r['out_pdf'], 'rb').read()
                return self._send(200, body, 'application/pdf', '스마트제안서.pdf')
            if path == '/v1/proposal/pages.pdf':
                if not r['pages_pdf']:
                    return self._err(409, '대상 담보가 없어 생성된 지면이 없습니다')
                return self._send(200, open(r['pages_pdf'], 'rb').read(), 'application/pdf', '생성지면.pdf')
            if path == '/v1/proposal/pages.html':
                return self._send(200, html_for_web(r['pages_html']).encode('utf-8'),
                                  'text/html; charset=utf-8')
            if path == '/v1/proposal/audit':
                return self._send(200, _json(dict(summary, audit=r['audit'])))
            if path == '/v1/proposal/all':
                out = dict(summary, audit=r['audit'],
                           pages_html=html_for_web(r['pages_html']),
                           pdf_base64=base64.b64encode(open(r['out_pdf'], 'rb').read()).decode())
                return self._send(200, _json(out))
            return self._err(404, 'not found : ' + path)
        except Exception as e:
            traceback.print_exc()
            return self._err(500, '생성 중 오류 : %s' % e)
        finally:
            LOCK.release()
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    os.makedirs(os.path.join(BASE, 'out'), exist_ok=True)
    srv = ThreadingHTTPServer((host, port), Handler)
    print('스마트 제안서 API %s — http://%s:%d  (Ctrl+C 로 종료)' % (VERSION, host, port))
    print('  데모 화면 : http://%s:%d/' % (host, port))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n종료')


if __name__ == '__main__':
    main()
