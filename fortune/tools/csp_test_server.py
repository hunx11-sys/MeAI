# -*- coding: utf-8 -*-
"""웹서버판 폴더를 '가장 엄격한 보안정책(CSP)'을 걸고 띄우는 시험용 서버.
외부 접속 · 인라인 코드 · data: 주소가 하나라도 있으면 브라우저 콘솔에 CSP 위반이 빨갛게 찍힌다.

사용 : python csp_test_server.py [포트=8772] [폴더=../web] [--no-fonts]
       → http://127.0.0.1:8772/
  --no-fonts : 글꼴 파일까지 막는 정책(font-src 'none')으로 띄운다. 회사 정책이 웹 글꼴을 막아도
               화면이 깨지지 않고 기본 글꼴로 나오는지 볼 때 쓴다.
"""
import functools
import http.server
import os
import sys

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
PORT = int(ARGS[0]) if ARGS else 8772
WEB = ARGS[1] if len(ARGS) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web')
FONT = "'none'" if '--no-fonts' in sys.argv else "'self'"
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' blob:; font-src %s; "
       "connect-src 'none'; frame-ancestors 'self'; base-uri 'none'; form-action 'none'" % FONT)


class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map, **{
        '.webp': 'image/webp', '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.js': 'application/javascript', '.css': 'text/css'})

    def end_headers(self):
        # parent.html = iframe 시험용 '사내 포털' 페이지. 포털 쪽 정책에 frame-src 'self' 가 있어야 액자(iframe)를 넣을 수 있다
        self.send_header('Content-Security-Policy', CSP + ("; frame-src 'self'" if self.path.split('?')[0].endswith('parent.html') else ''))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    print('CSP:', CSP)
    print('http://127.0.0.1:%d/' % PORT)
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(H, directory=WEB)).serve_forever()
