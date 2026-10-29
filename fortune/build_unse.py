"""오늘의 운세(사주 + 타로) 한 파일 조립.

  src/unse.html  화면 틀 (CSS · 화면 · 자리표)
  src/engine.js  사주 엔진 · 운세 문구 · 타로 78장 풀이 (v1 그대로, 고치지 않는다)
  src/app.js     화면 동작
  assets/tarot/00~77.webp   카드 그림 (tools/prep_tarot.py 로 만든 것)
  assets/svg/card_back.svg  카드 뒷면
  assets/fonts/*.woff2      글꼴 (tools/make_fonts.py 로 만든 것)

→ ../dist/unse_saju_tarot.html (바깥 파일을 하나도 부르지 않는 단일 HTML · 오프라인 · 메일/카톡 전달용)

쓰는 법 : python3 fortune/build_unse.py [출력 경로]
          python3 fortune/build_unse.py <출력 경로> --preview   (claude.ai 미리보기용 : 문서 틀 떼고 저장 · 보내기 버튼 숨김)
"""
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'dist', 'unse_saju_tarot.html')


def read(*p):
    return open(os.path.join(HERE, *p), encoding='utf-8').read()


def b64(path):
    return base64.b64encode(open(os.path.join(HERE, path), 'rb').read()).decode('ascii')


def fonts_css():
    faces = [('UnseSerif', 'serif-ko.woff2'), ('UnseHan', 'hanja.woff2'), ('UnseCinzel', 'cinzel.woff2')]
    css = ''
    for fam, f in faces:
        css += ('@font-face { font-family: "%s"; src: url(data:font/woff2;base64,%s) format("woff2"); font-weight: 400 900; font-style: normal; font-display: swap; }\n'
                % (fam, b64(os.path.join('assets', 'fonts', f))))
    return css


def back_uri():
    s = read('assets', 'svg', 'card_back.svg')
    s = re.sub(r'\s*\n\s*', ' ', s).replace('"', "'")
    for a, b in (('%', '%25'), ('#', '%23'), ('<', '%3C'), ('>', '%3E')):
        s = s.replace(a, b)
    return 'data:image/svg+xml,' + s


def tarot_js():
    imgs = []
    for i in range(78):
        imgs.append('"data:image/webp;base64,%s"' % b64(os.path.join('assets', 'tarot', '%02d.webp' % i)))
    return 'window.NZ_TAROT_IMG = [\n' + ',\n'.join(imgs) + '\n];'


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


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = args[0] if args else OUT
    html = read('src', 'unse.html')
    parts = {
        '/*@@FONTS@@*/': fonts_css(),
        '@@BACK@@': back_uri(),
        '/*@@ENGINE@@*/': read('src', 'engine.js'),
        '/*@@IMG@@*/': tarot_js(),
        '/*@@APP@@*/': read('src', 'app.js'),
    }
    for k, v in parts.items():
        if html.count(k) != 1:
            sys.exit('자리표 %s 가 %d번 있어요 (1번이어야 함)' % (k, html.count(k)))
        html = html.replace(k, v)
    if '</script' in parts['/*@@ENGINE@@*/'] + parts['/*@@APP@@*/']:
        sys.exit('스크립트 안에 </script 가 있어요')
    if '--preview' in sys.argv:
        html = preview(html)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(html)
    print('%s  %.2fMB' % (os.path.relpath(out), os.path.getsize(out) / 1048576))


if __name__ == '__main__':
    main()
