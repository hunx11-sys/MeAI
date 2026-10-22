# -*- coding: utf-8 -*-
"""
영업지원도구 공통 스타일 · 사이트 셸 끼워 넣기
  ui/meai-ui.css  → 각 화면 <style id="meai-ui">
  ui/meai-site.js → 각 화면 </body> 앞 <script id="meai-site">

하는 일
  1) 각 HTML 의 <head> 맨 앞에 <style id="meai-ui">(공통 색 · 글꼴 · 초점 · 움직임 · 머리 띠 규칙)를 넣거나 바꿔 끼운다.
     화면 자체 스타일이 뒤에 오므로 화면별 모양은 그대로 우선한다(공통 토큰을 가져다 쓰는 구조).
     바로 뒤에 아주 작은 <script id="meai-boot"> 를 둔다 — 첫 그림 전에 html 에 mu-js · mu-enter(들어올 때 움직임) 표시를 켠다.
  2) <html data-tool="…"> 로 그 도구의 강조색(마스코트 색)을 정한다.
  3) 인터넷판 글꼴(Pretendard) 링크가 없으면 넣는다 — 폐쇄망 배포판은 build_package.py 가 빼고 파일 안에 심는다.
  4) <body> 바로 뒤에 사이트 머리 띠(<!--mu-nav--> … <!--/mu-nav-->: #mu-nav · 휴대폰 메뉴 시트 #mu-sheet · 바탕 빛 #mu-amb)를
     넣거나 바꿔 끼운다. 링크는 보통 <a href="tool.html"> 이라 배포판의 이름 바꾸기(build_package · build_single)와
     올인원의 링크 가로채기(build_allinone NAV)가 그대로 듣는다. 지금 화면은 aria-current="page" 로 표시한다.
     사용 통계(stats.html)는 인터넷판 전용이라 머리 띠에 넣지 않는다(통계 화면 자체에는 머리 띠가 있다).
  5) </body> 바로 앞에 <script id="meai-site">(ui/meai-site.js)를 넣거나 바꿔 끼운다.
  6) 특약검색기 안에 들어 있는 보상시뮬레이터(SIMSRC, base64)에는 1) 2) 3) 5)만 한다(강조색 eco) — 머리 띠는 넣지 않고,
     meai-site.js 도 다른 화면 안(iframe)에서는 머리 띠를 쓰지 않는다.

실행 : python3 scripts/apply_ui.py     (같은 내용이면 파일을 건드리지 않는다)
규칙 : design/DESIGN-MeAI.md 「11. 사이트 셸 · 움직임」
"""
import base64, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = io.open(os.path.join(ROOT, 'ui', 'meai-ui.css'), encoding='utf-8').read()
SITE_JS = io.open(os.path.join(ROOT, 'ui', 'meai-site.js'), encoding='utf-8').read()
# 첫 그림 전에 켜는 표시 — 움직임 줄이기 설정이면 들어올 때 움직임(mu-enter)을 켜지 않는다
BOOT = ('<script id="meai-boot">(function(h){h.classList.add("mu-js");try{if(window.matchMedia&&'
        'matchMedia("(prefers-reduced-motion: reduce)").matches)return}catch(e){}h.classList.add("mu-enter");'
        'setTimeout(function(){h.classList.remove("mu-enter")},1400)})(document.documentElement)</script>')
# 글꼴 : 저장소의 Pretendard 한 파일(assets/pretendard-subset.woff2 · 가변 · 2,612자)을 처음에 한 번만 받는다.
# 예전에는 jsdelivr 의 「dynamic-subset」(글자 묶음 약 90개)을 썼는데, 휴대폰에서 아래로 내리다 새 글자가 나오면
# 그 묶음을 그때 받아 화면 전체 글자를 다시 그려 번쩍이며 끊겼다(갤럭시 크롬 · 2026-10-22 소유자 제보).
FONT_FILE = 'assets/pretendard-subset.woff2'
FONT_LINK = ('<link id="meai-font-pre" rel="preload" href="%s" as="font" type="font/woff2" crossorigin>'
             '<style id="meai-font">@font-face{font-family:"Pretendard Variable";font-weight:45 930;font-style:normal;'
             'font-display:swap;src:url(%s) format("woff2-variations"),url(%s) format("woff2")}</style>') % ((FONT_FILE,) * 3)
CDN_FONT = re.compile(r'[ \t]*<link[^>]+href="https?://cdn\.jsdelivr\.net/[^"]*pretendard[^"]*"[^>]*>\n?')
PAGES = {'index.html': 'home', 'tool.html': 'merry', 'products.html': 'rara', 'prompts.html': 'indi',
         '명패생성기.html': 'tata', '통합치료비.html': 'zizi', 'stats.html': 'home'}
# 머리 띠에서 「지금 화면」으로 표시할 칸(stats 는 머리 띠에 없으므로 빈칸)
CURRENT = {'index.html': 'home', 'tool.html': 'merry', 'products.html': 'rara', 'prompts.html': 'indi',
           '명패생성기.html': 'tata', '통합치료비.html': 'zizi', 'stats.html': ''}
# (키, 주소, 머리 띠 이름, 메뉴 시트 이름, 메뉴 시트 설명) — 순서 = 머리 띠 순서
NAV = [('home', 'index.html', '대문', '대문', '영업지원 아이템 모아 보기'),
       ('merry', 'tool.html#search', '특약검색기', '특약검색기', 'with 메리'),
       ('eco', 'tool.html#sim', '보상시뮬레이터', '보상시뮬레이터', 'with 에코'),
       ('rara', 'products.html', '상품 라인업', '상품 라인업', 'with 라라'),
       ('zizi', '통합치료비.html', '통합치료비', '통합치료비 시뮬레이터', 'with 찌지리'),
       ('indi', 'prompts.html', '프롬프트', '프롬프트 라이브러리', 'with 인디'),
       ('tata', '명패생성기.html', '명패', '명패 제작기', 'with 타타')]
ICON_MENU = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>')
ICON_X = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>')
ICON_GO = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>')


def nav_block(cur):
    """머리 띠 · 메뉴 시트 · 바탕 빛 (정적 HTML — 자바스크립트가 없어도 링크는 다 된다)"""
    def ac(k):
        return ' aria-current="page"' if k == cur else ''
    links = ''.join('<a class="mu-l mu-%s" data-k="%s" href="%s"%s><i aria-hidden="true"></i>%s</a>'
                    % (k, k, href, ac(k), name) for k, href, name, _, _ in NAV)
    curname = next((name for k, _, name, _, _ in NAV if k == cur and k != 'home'), '')
    curtag = ('<span class="mu-cur mu-%s"><i></i>%s</span>' % (cur, curname)) if curname else '<span class="mu-cur"></span>'
    items = ''.join('<li style="--i:%d"><a class="mu-si mu-%s" data-k="%s" href="%s"%s><span class="mu-dot"></span>'
                    '<span><b>%s</b><small>%s</small></span><em>지금 화면</em>%s</a></li>'
                    % (i, k, k, href, ac(k), full, desc, ICON_GO) for i, (k, href, _, full, desc) in enumerate(NAV))
    return ('<!--mu-nav-->'
            '<div id="mu-amb" aria-hidden="true"></div>'
            '<nav id="mu-nav" data-page="%s" aria-label="영업지원도구"><div class="mu-in">'
            '<a class="mu-brand" href="index.html" aria-label="MeAI 영업지원도구 대문"><span class="mu-mark" aria-hidden="true">M</span>'
            '<span class="mu-bt">MeAI<span>영업지원도구</span></span></a>%s'
            '<div class="mu-links"><span class="mu-pill" aria-hidden="true"></span>%s</div>'
            '<button type="button" class="mu-menu" aria-label="도구 메뉴 열기" aria-expanded="false" aria-controls="mu-sheet">%s</button>'
            '</div><div class="mu-prog" aria-hidden="true"></div></nav>'
            '<div id="mu-sheet" aria-hidden="true"><div class="mu-scrim"></div>'
            '<div class="mu-panel" role="dialog" aria-modal="true" aria-label="도구 메뉴"><div class="mu-grab"></div>'
            '<div class="mu-sh"><span class="mu-mark" aria-hidden="true">M</span><b>영업지원도구</b>'
            '<button type="button" class="mu-x" aria-label="메뉴 닫기">%s</button></div><ul>%s</ul></div></div>'
            '<!--/mu-nav-->') % (cur or 'stats', curtag, links, ICON_MENU, ICON_X, items)


def body_open(s):
    """진짜 <body> 여는 태그 위치 — <script> · <style> · 주석 안의 글자(명패생성기 엑셀 라이브러리의 '<body>' 문자열 등)는 건너뛴다"""
    i = 0
    while True:
        b = s.find('<body', i)
        if b < 0:
            raise SystemExit('<body> 를 못 찾음')
        skip = [(k, t) for k, t in ((s.find('<script', i), '</script>'), (s.find('<style', i), '</style>'),
                                    (s.find('<!--', i), '-->')) if 0 <= k < b]
        if skip:
            k, t = min(skip)
            e = s.find(t, k)
            if e < 0:
                raise SystemExit('닫히지 않은 ' + t)
            i = e + len(t)
            continue
        return b, s.index('>', b) + 1


def inject(s, tool, cur=None):
    css = re.sub(r'\s*\n\s*', '\n', CSS.strip())
    block = '<style id="meai-ui">\n' + css + '\n</style>' + BOOT
    s = re.sub(r'<script id="meai-boot">.*?</script>', '', s, count=1, flags=re.S)
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
    s = CDN_FONT.sub('', s)
    s = re.sub(r'<link id="meai-font-pre"[^>]*>(<style id="meai-font">.*?</style>)?', '', s, flags=re.S)
    k = s.index('</style>', s.index('<style id="meai-ui">')) + len('</style>')
    s = s[:k] + FONT_LINK + s[k:]
    # 머리 띠 (보상시뮬레이터 안쪽에는 넣지 않는다 : cur=None)
    if cur is not None:
        nb = nav_block(cur)
        if '<!--mu-nav-->' in s:
            a = s.index('<!--mu-nav-->'); b = s.index('<!--/mu-nav-->', a) + len('<!--/mu-nav-->')
            s = s[:a] + nb + s[b:]
        else:
            _, e = body_open(s)
            s = s[:e] + '\n' + nb + s[e:]
    # 움직임 · 머리 띠 동작 (</body> 바로 앞 — 문서의 마지막 </body>)
    js = '<script id="meai-site">\n' + SITE_JS.strip().replace('</script', '<\\/script') + '\n</script>'
    a = s.rfind('<script id="meai-site">\n')
    if a >= 0:
        b = s.index('</script>', a) + len('</script>')
        s = s[:a] + js + s[b:]
    else:
        k = s.rfind('</body>')
        if k < 0:
            raise SystemExit('</body> 를 못 찾음')
        s = s[:k] + js + '\n' + s[k:]
    return s


def main():
    for f, tool in PAGES.items():
        p = os.path.join(ROOT, f)
        s = io.open(p, encoding='utf-8').read()
        n = inject(s, tool, CURRENT[f])
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
