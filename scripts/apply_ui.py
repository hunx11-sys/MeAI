# -*- coding: utf-8 -*-
"""
영업지원도구 공통 스타일 끼워 넣기 — ui/meai-ui.css → 각 화면 <style id="meai-ui">

하는 일
  1) 각 HTML 의 <head> 맨 앞에 <style id="meai-ui">(공통 색 · 글꼴 · 초점 · 움직임 규칙)를 넣거나 바꿔 끼운다.
     화면 자체 스타일이 뒤에 오므로 화면별 모양은 그대로 우선한다(공통 토큰을 가져다 쓰는 구조).
  2) <html data-tool="…"> 로 그 도구의 강조색(마스코트 색)을 정한다.
  3) 인터넷판 글꼴(Pretendard) 링크가 없으면 넣는다 — 폐쇄망 배포판은 build_package.py 가 빼고 파일 안에 심는다.
  4) 특약검색기 안에 들어 있는 보상시뮬레이터(SIMSRC, base64)에도 같은 일을 한다(강조색 eco).

실행 : python3 scripts/apply_ui.py     (같은 내용이면 파일을 건드리지 않는다)
"""
import base64, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = io.open(os.path.join(ROOT, 'ui', 'meai-ui.css'), encoding='utf-8').read()
FONT_LINK = ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/'
             'pretendardvariable-dynamic-subset.min.css">')
PAGES = {'index.html': 'home', 'tool.html': 'merry', 'products.html': 'rara', 'prompts.html': 'indi',
         '명패생성기.html': 'tata', '통합치료비.html': 'zizi', 'stats.html': 'home'}


def inject(s, tool):
    css = re.sub(r'\s*\n\s*', '\n', CSS.strip())
    block = '<style id="meai-ui">\n' + css + '\n</style>'
    if '<style id="meai-ui">' in s:
        s = re.sub(r'<style id="meai-ui">.*?</style>', lambda m: block, s, count=1, flags=re.S)
    else:
        m = re.search(r'<head[^>]*>', s)
        if not m or m.start() > 600: raise SystemExit('문서 앞쪽에서 <head> 를 못 찾음')
        s = s[:m.end()] + '\n' + block + s[m.end():]
    m = re.search(r'<html\b[^>]*>', s)
    tag = m.group(0)
    nt = re.sub(r'\sdata-tool="[^"]*"', '', tag)
    nt = nt[:-1] + ' data-tool="%s">' % tool
    s = s[:m.start()] + nt + s[m.end():]
    if 'pretendardvariable-dynamic-subset' not in s:
        k = s.index('</style>', s.index('<style id="meai-ui">')) + len('</style>')
        s = s[:k] + '\n' + FONT_LINK + s[k:]
    return s


def main():
    for f, tool in PAGES.items():
        p = os.path.join(ROOT, f)
        s = io.open(p, encoding='utf-8').read()
        n = inject(s, tool)
        if f == 'tool.html':
            m = re.search(r'(<script id="SIMSRC" type="text/plain">)(.*?)(</script>)', n, re.S)
            inner = base64.b64decode(m.group(2)).decode('utf-8')
            inner2 = inject(inner, 'eco')
            if inner2 != inner:
                n = n[:m.start(2)] + base64.b64encode(inner2.encode('utf-8')).decode('ascii') + n[m.end(2):]
        if n != s:
            io.open(p, 'w', encoding='utf-8').write(n)
            print('반영 :', f, '(%s)' % tool)
        else:
            print('같음 :', f)


if __name__ == '__main__':
    main()
