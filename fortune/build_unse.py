"""오늘의 운세(사주 + 타로) 조립. 같은 원본에서 세 가지 판을 만든다.

  src/unse.html     화면 틀 (자리표 <!--@@HEAD@@--> · <!--@@SCRIPTS@@-->)
  src/unse.css      디자인 (자리표 @@FONT_*@@ · @@BACK@@ · @@HANJI@@ · @@ZOOM@@)
  src/ie-check.js   익스플로러 → 엣지 안내
  src/engine.js     사주 엔진 · 운세 문구 · 타로 78장 풀이 (v1 그대로, 고치지 않는다)
  src/app.js        화면 동작
  assets/tarot/00~77.webp · assets/svg/*.svg · assets/fonts/*.woff2

판
  (기본)       ../dist/unse_saju_tarot.html  한 파일판. 그림 · 글꼴을 파일 안에 넣음. 카톡 · 메일 · USB · 폐쇄망 PC 더블클릭
  --preview    claude.ai 미리보기용 (문서 틀을 떼고 저장 · 보내기 버튼 숨김)
  --web <폴더>  웹서버판. 정적 파일로 나눔 (인라인 스크립트 · 인라인 스타일 · data: 주소 · 외부 주소 0)
               → 가장 엄격한 보안정책(CSP)을 건 사내 웹서버 · 폐쇄망에 그대로 올린다

쓰는 법 : python3 fortune/build_unse.py [출력 경로]
          python3 fortune/build_unse.py <출력 경로> --preview
          python3 fortune/build_unse.py --web <폴더>
"""
import base64
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'dist', 'unse_saju_tarot.html')
VERSION = 'v2 · 2026-10-29'
FONTS = {'@@FONT_SERIF@@': 'serif-ko.woff2', '@@FONT_HAN@@': 'hanja.woff2', '@@FONT_CINZEL@@': 'cinzel.woff2'}
SVGS = {'@@BACK@@': 'card-back.svg', '@@HANJI@@': 'hanji.svg', '@@ZOOM@@': 'zoom.svg'}


def read(*p):
    return open(os.path.join(HERE, *p), encoding='utf-8').read()


def b64(*p):
    return base64.b64encode(open(os.path.join(HERE, *p), 'rb').read()).decode('ascii')


def svg_uri(name):
    s = read('assets', 'svg', name).strip()
    s = re.sub(r'\s*\n\s*', ' ', s).replace('"', "'")
    for a, b in (('%', '%25'), ('#', '%23'), ('<', '%3C'), ('>', '%3E')):
        s = s.replace(a, b)
    return 'data:image/svg+xml,' + s


def fill(text, table):
    for k, v in table.items():
        if k not in text:
            sys.exit('자리표 %s 가 없어요' % k)
        text = text.replace(k, v)
    if '@@' in text:
        sys.exit('채우지 못한 자리표 : %s' % re.findall(r'@@\w+@@', text))
    return text


def split_engine():
    """engine.js 를 v1 웹 패키지와 같은 세 파일(문구 · 사주 엔진 · 타로 데이터)로 나눈다. 내용은 한 글자도 바꾸지 않는다."""
    e = read('src', 'engine.js')
    i1 = e.index('/* =====================================================================\n   사주(년·월·일주)')
    i2 = e.index('/* =====================================================================\n   타로 78장')
    parts = [('fortune-text.js', '사주 운세 문구 표 window.NZ_FTEXT', e[:i1]),
             ('saju-engine.js', '사주 계산 엔진 window.NZ_SAJU', e[i1:i2]),
             ('tarot-data.js', '타로 78장 데이터 window.NZ_TAROT', e[i2:])]
    assert ''.join(p[2] for p in parts) == e
    return parts


def header(desc):
    return '/* 오늘의 운세 %s (사주팔자·타로) · 세일즈혁신TF · 빌드: fortune/build_unse.py --web */\n/* %s */\n' % (VERSION, desc)


def tarot_js_inline():
    return 'window.NZ_TAROT_IMG = [\n' + ',\n'.join('"data:image/webp;base64,%s"' % b64('assets', 'tarot', '%02d.webp' % i) for i in range(78)) + '\n];'


def check_scripts(*codes):
    for c in codes:
        if '</script' in c:
            sys.exit('스크립트 안에 </script 가 있어요')


PREVIEW_CSS = ('<style>/* 미리보기 판 : 미리보기 창은 인쇄 · 내려받기 · 공유 · 문자를 막으므로 그 버튼을 숨긴다 */\n'
               '.send, .t-btns #tShare, .t-btns #tImg, .t-hint { display: none !important; }</style>\n')


def preview(html):
    """claude.ai 미리보기(아티팩트)용 : 바깥 문서 틀은 게시할 때 씌워지므로 떼고, 동작하지 않는 버튼을 숨긴다."""
    for tag in ('<!DOCTYPE html>\n', '<html lang="ko">\n', '<head>\n', '</head>\n', '</body>\n', '</html>\n'):
        if html.count(tag) != 1:
            sys.exit('미리보기 판 : %r 가 %d번 있어요' % (tag, html.count(tag)))
        html = html.replace(tag, '')
    html = html.replace('<body class="v-gate">\n', PREVIEW_CSS + '<script>document.documentElement.lang = "ko"; document.body.className = "v-gate";</script>\n', 1)
    return html


def build_single(out, is_preview=False):
    table = {k: 'data:font/woff2;base64,' + b64('assets', 'fonts', f) for k, f in FONTS.items()}
    table.update({k: svg_uri(f) for k, f in SVGS.items()})
    css = fill(read('src', 'unse.css'), table)
    ie, eng, app, img = read('src', 'ie-check.js'), read('src', 'engine.js'), read('src', 'app.js'), tarot_js_inline()
    check_scripts(ie, eng, app)
    html = read('src', 'unse.html')
    html = fill(html, {'<!--@@HEAD@@-->': '<script>\n' + ie + '</script>\n<style>\n' + css + '</style>',
                       '<!--@@SCRIPTS@@-->': '<script>' + eng + '</script>\n<script>' + img + '</script>\n<script>' + app + '</script>'})
    if is_preview:
        html = preview(html)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(html)
    print('%s  %.2fMB' % (os.path.relpath(out), os.path.getsize(out) / 1048576))


def build_web(d):
    if os.path.exists(d):
        shutil.rmtree(d)
    for sub in ('css', 'js', 'img/tarot', 'fonts'):
        os.makedirs(os.path.join(d, sub))
    w = lambda rel, text: open(os.path.join(d, rel), 'w', encoding='utf-8', newline='\n').write(text)
    table = {k: '../fonts/' + f for k, f in FONTS.items()}
    table.update({k: '../img/' + f for k, f in SVGS.items()})
    w('css/unse.css', '/* 오늘의 운세 %s · 디자인 (빌드: fortune/build_unse.py --web) */\n' % VERSION + fill(read('src', 'unse.css'), table))
    w('js/ie-check.js', header('익스플로러로 열리면 엣지로 다시 열기 · <head> 에서 가장 먼저 읽는다') + read('src', 'ie-check.js'))
    names = []
    for name, desc, code in split_engine():
        w('js/' + name, header(desc) + code.strip() + '\n')
        names.append(name)
    w('js/tarot-img.js', header('타로 카드 그림 주소 window.NZ_TAROT_IMG (deck id 0~77 → img/tarot/00~77.webp)') +
      "window.NZ_TAROT_IMG = (function () { var a = [], i; for (i = 0; i < 78; i++) a.push('img/tarot/' + (i < 10 ? '0' : '') + i + '.webp'); return a; })();\n")
    w('js/app.js', header('화면 이동 · 사주 화면 · 타로 연출 · 크게 보기 · 저장/공유') + read('src', 'app.js'))
    for f in SVGS.values():
        shutil.copy(os.path.join(HERE, 'assets', 'svg', f), os.path.join(d, 'img', f))
    for i in range(78):
        shutil.copy(os.path.join(HERE, 'assets', 'tarot', '%02d.webp' % i), os.path.join(d, 'img', 'tarot', '%02d.webp' % i))
    for f in FONTS.values():
        shutil.copy(os.path.join(HERE, 'assets', 'fonts', f), os.path.join(d, 'fonts', f))
    scripts = names + ['tarot-img.js', 'app.js']
    html = fill(read('src', 'unse.html'), {
        '<!--@@HEAD@@-->': '<script src="js/ie-check.js"></script>\n<link rel="stylesheet" href="css/unse.css">',
        '<!--@@SCRIPTS@@-->': '\n'.join('<script src="js/%s"></script>' % s for s in scripts)})
    w('index.html', html)
    n, size = 0, 0
    for root, _, files in os.walk(d):
        for f in files:
            n += 1
            size += os.path.getsize(os.path.join(root, f))
    print('%s/  파일 %d개 · %.2fMB' % (os.path.relpath(d), n, size / 1048576))


def main():
    if '--web' in sys.argv:
        i = sys.argv.index('--web')
        if i + 1 >= len(sys.argv):
            sys.exit('--web 뒤에 폴더를 적어 주세요')
        build_web(sys.argv[i + 1])
        return
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    build_single(args[0] if args else OUT, '--preview' in sys.argv)


if __name__ == '__main__':
    main()
