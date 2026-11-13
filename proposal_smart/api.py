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
  POST /v1/ga/pdf             원본 PDF 업로드      → GA 양식 스마트 제안서 6쪽 PDF
  POST /v1/ga/all             원본 PDF 업로드      → GA PDF(base64) + 감사 로그 + 인식 담보 + 로그 텍스트 JSON
  POST /v1/ga2/pdf            원본 PDF 업로드      → GA 스마트 제안서 새 양식(v2 · 2026-11-11 회의) PDF(15~19쪽)
  POST /v1/ga2/all            원본 PDF 업로드      → 새 양식 PDF(base64) + 간병인 쪽 선택 · 쪽수 · 계산 로그 · 인식 담보 JSON

업로드 방법 두 가지 모두 받는다.
  · multipart/form-data 의 file 필드 (HTML <input type=file>)
  · Content-Type: application/pdf 로 PDF 바이트를 그대로 body 에 실어 보내기 (fetch 권장)

LLM·외부 API 호출은 없다. 실행 중 외부 통신을 하지 않는다.
"""
import base64, glob, io, json, os, re, shutil, sys, tempfile, threading, time, traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pipeline

VERSION = 'v8.99'
MAX_BYTES = 60 * 1024 * 1024                 # 업로드 상한 60MB
LOCK = threading.Semaphore(2)                # 생성 요청은 2건까지 받아 두고(1건 처리 + 1건 대기) 나머지는 180초 기다린 뒤 503
GA_LOCK = threading.Lock()                   # 실제 생성은 한 번에 한 건 — 설계서 상태 · 계산 로그(scen_engine.ISSUES)를 모듈 안에 두므로 9쪽 · GA · 새 양식 모두 이 잠금으로 줄을 선다
GA2_TIMEOUT = int(os.environ.get('GA2_TIMEOUT', '600'))   # 새 양식 1건 제한 시간(초)
GA2_STATE = {'broken': False}                # 새 양식 작업이 제한 시간을 넘겨 멈추면 True — /health 가 503 을 돌려 재시작을 알린다
TMP_PREFIX = 'sp_in_%d_' % os.getpid()


def sweep(max_age=3600):
    """처리 중에 서버가 꺼져 남은 업로드 · 중간 파일(설계서 내용)을 치운다 — 만든 지 1시간 넘은 것만(다른 프로세스가 지금 쓰는 것은 그대로)"""
    n = 0
    for d in glob.glob(os.path.join(tempfile.gettempdir(), 'sp_in_*')):
        try:
            if time.time() - os.path.getmtime(d) > max_age: shutil.rmtree(d, ignore_errors=True); n += 1
        except OSError: pass
    try:
        import ga_v2; n += ga_v2.sweep_tmp(max_age)
    except Exception: pass
    return n
GA2_WORKER = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ga2')   # 새 양식(v2)은 크로뮴 하나를 띄워 두고 같은 스레드에서만 쓴다(playwright 규칙)
CARE_NM = {'support': '간병인 지원 가입자', 'use': '간병인 사용 가입자', 'none': '간병인 지원 · 사용 함께(둘 다 미가입)'}


def ga2_build(src, out):
    """새 양식 한 건 — 작업 스레드(GA2_WORKER) 안에서만 부른다"""
    import ga_v2, ga_proposal
    with GA_LOCK:
        pdf, log, info = ga_v2.build(src, out)
        rid = ga_proposal.RID
        return dict(info=info, log=io.open(log, encoding='utf-8').read(), premium=ga_proposal.PREMIUM,
                    riders=rid, matched=sum(1 for r in rid if r.get('matched')), body=open(out, 'rb').read())


def _json(o):
    return json.dumps(o, ensure_ascii=False).encode('utf-8')


ASCII_NAME = {'스마트제안서.pdf': 'smart_proposal.pdf', '생성지면.pdf': 'smart_pages.pdf', 'ga_proposal.pdf': 'ga_proposal.pdf', 'ga2_proposal.pdf': 'ga2_proposal.pdf'}
MIME = {'.ttf': 'font/ttf', '.otf': 'font/otf', '.png': 'image/png',
        '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.css': 'text/css; charset=utf-8'}


def html_for_web(path):
    """생성 지면 HTML을 브라우저에서 바로 볼 수 있게 고친다.

    지면 HTML은 인쇄용이라 글꼴·로고를 file:/// 절대경로로 참조한다. 브라우저는 http 문서에서
    file:/// 를 읽지 못하므로 /assets/ 경로로 바꿔 준다(같은 서버가 /assets/ 를 내려준다)."""
    h = io.open(path, encoding='utf-8').read()
    import pathlib
    h = h.replace(pathlib.Path(BASE, 'assets').as_uri() + '/', '/assets/')      # 윈도우·한글 폴더 주소(gen2 A_URI)
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
            if GA2_STATE['broken']:
                return self._send(503, _json({'ok': False, 'version': VERSION, 'error': '새 양식 작업이 멈춰 있습니다 — 서버를 다시 켜 주세요'}))
            return self._send(200, _json({'ok': True, 'version': VERSION,
                                          'python': sys.version.split()[0],
                                          'llm': False, 'network': False,
                                          'formats': {'proposal': '/v1/proposal/*', 'ga': '/v1/ga/*', 'ga2': '/v1/ga2/*'}}))
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
        if not (path.startswith('/v1/proposal') or path.startswith('/v1/ga')):          # /v1/ga · /v1/ga2
            return self._err(404, 'not found : ' + path)
        try:
            pdf = self._read_pdf()
        except Exception as e:
            return self._err(400, str(e))
        if pipeline.not_pdf(pdf[:4096]):                    # 사내 보안(DRM)으로 잠긴 파일이면 그렇게 알려 준다(v8.98)
            return self._err(400, pipeline.not_pdf(pdf[:4096]))

        sweep()
        tmp = tempfile.mkdtemp(prefix=TMP_PREFIX)
        src = os.path.join(tmp, 'source.pdf')
        open(src, 'wb').write(pdf)
        got = LOCK.acquire(timeout=180)
        if not got:
            shutil.rmtree(tmp, ignore_errors=True)
            return self._err(503, '처리 대기가 길어졌습니다 — 잠시 후 다시 시도해 주세요')
        try:
            if path in ('/v1/ga2/pdf', '/v1/ga2/all'):            # GA 새 양식 v2(ga_v2.py) — 작업 스레드에서(그 안에서 GA_LOCK)
                if GA2_STATE['broken']:
                    return self._err(503, '새 양식 작업이 멈춰 있습니다 — 서버를 다시 켜 주세요')
                try:
                    r = GA2_WORKER.submit(ga2_build, src, os.path.join(tmp, 'ga2_proposal.pdf')).result(timeout=GA2_TIMEOUT)
                except FutTimeout:
                    GA2_STATE['broken'] = True
                    return self._err(504, '처리 시간이 %d초를 넘었습니다 — 지면을 그리는 크로뮴이 멈춘 것으로 보입니다. 서버를 다시 켜 주세요' % GA2_TIMEOUT)
                if path == '/v1/ga2/pdf':
                    return self._send(200, r['body'], 'application/pdf', 'ga2_proposal.pdf')
                i = r['info']
                return self._send(200, _json({'ok': True, 'format': 'ga2', 'product': i['product'], 'premium': r['premium'],
                                              'pages': i['pages'], 'detail_pages': i['detail_pages'],
                                              'care_pages': i['care'], 'care_pages_ko': [CARE_NM[k] for k in i['care']],
                                              'rider_count': i['riders'], 'matched': r['matched'], 'warn': i['warn'],
                                              'elapsed_sec': i['sec'], 'log': r['log'], 'riders': r['riders'],
                                              'pdf_base64': base64.b64encode(r['body']).decode()}))
            if not GA_LOCK.acquire(timeout=180):                 # 9쪽 · 기존 GA 도 새 양식과 같은 줄(계산 로그가 섞이지 않게)
                return self._err(503, '처리 대기가 길어졌습니다 — 잠시 후 다시 시도해 주세요')
            try:
                return self._gen(path, src, tmp)
            finally:
                GA_LOCK.release()
        except pipeline.DesignUnreadable as e:            # 설계서를 못 읽음(그림 PDF · DRM · 다른 문서) — 빈 제안서 대신 이유(v8.98)
            if e.__cause__ is not None:                      # 깨진 PDF 로 본 원래 오류는 서버 로그에 남긴다(원인 추적용)
                traceback.print_exception(type(e.__cause__), e.__cause__, e.__cause__.__traceback__)
            return self._err(422, '설계서를 읽지 못해 만들지 않았습니다 — %s' % e)
        except Exception as e:
            traceback.print_exc()
            return self._err(500, '생성 중 오류 : %s' % (e or type(e).__name__))
        finally:
            LOCK.release()
            shutil.rmtree(tmp, ignore_errors=True)

    def _gen(self, path, src, tmp):
        """9쪽 지면 · 기존 GA 6쪽 — GA_LOCK 안에서만 부른다"""
        if path in ('/v1/ga/pdf', '/v1/ga/all'):              # GA 양식 v5(표지·보장요약·암·뇌심 + 세부내역 · ga_proposal.py)
            import ga_proposal
            out = os.path.join(tmp, 'ga_proposal.pdf')
            _pdf, log, warn = ga_proposal.build(src, out)
            body = open(out, 'rb').read()
            if path == '/v1/ga/pdf':
                return self._send(200, body, 'application/pdf', 'ga_proposal.pdf')
            a = ga_proposal.AUDIT
            return self._send(200, _json({'ok': True, 'rider_count': ga_proposal.NRID, 'matched': a['요약']['마스터매칭'],
                                          'recog': a['요약']['인식'], 'new_pages': 6, 'elapsed_sec': a['요약']['처리시간'],
                                          'product': ga_proposal.PRODUCT, 'premium': ga_proposal.PREMIUM, 'warn': warn,
                                          'audit': a, 'riders': ga_proposal.RID,
                                          'log': io.open(log, encoding='utf-8').read(),
                                          'pdf_base64': base64.b64encode(body).decode()}))
        if path == '/v1/proposal/riders':                     # 담보 인식만(빠름)
            rid = pipeline.read_checked(src, allow_unmatched=True)   # 못 읽는 파일 · 담보 0건이면 다른 단추와 같은 422 이유(v8.98)
            return self._send(200, _json({'ok': True, 'count': len(rid),
                                          'matched': sum(1 for r in rid if r.get('matched')),
                                          'recog': pipeline.S.recog(rid),        # 마스터 / 부모연결 / 규칙만 / 계산제외(v8.61)
                                          'riders': rid}))
        job = os.path.join(tmp, 'job'); os.makedirs(job, exist_ok=True)
        r = pipeline.build(src, workdir=job)          # 작업 폴더를 요청 임시 폴더 안에 — 응답 뒤 함께 지운다(설계서 내용이 out/ 에 쌓이지 않게)
        summary = {'ok': True, 'attached': r['attached'], 'base_pages': r['base_pages'],
                   'new_pages': r['new_pages'], 'total_pages': r['total_pages'],
                   'insert_after': r['insert_after'], 'rider_count': r['rider_count'],
                   'matched': r['matched'], 'recog': r.get('recog'), 'elapsed_sec': r['elapsed_sec'],
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


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    os.makedirs(os.path.join(BASE, 'out'), exist_ok=True)
    import assets_ready; assets_ready.fonts()         # 글꼴이 없는 PC(zip 으로 받은 경우) — ga_assets 의 나눔고딕을 assets/ 로
    n = sweep()
    if n: print('지난번에 처리 중 남은 임시 파일 %d개를 지웠습니다' % n)
    srv = ThreadingHTTPServer((host, port), Handler)
    print('스마트 제안서 API %s — http://%s:%d  (Ctrl+C 로 종료)' % (VERSION, host, port))
    print('  데모 화면 : http://%s:%d/' % (host, port))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n종료')
    finally:
        try:
            import ga_v2
            GA2_WORKER.submit(ga_v2.close_browser).result(timeout=20)     # 띄워 둔 크로뮴은 그 스레드에서 닫는다
        except Exception:
            pass
        GA2_WORKER.shutdown(wait=False)


if __name__ == '__main__':
    main()
