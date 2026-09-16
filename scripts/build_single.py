#!/usr/bin/env python3
"""
낱개 HTML 배포판 만들기 — 압축파일을 못 보낼 때
- 저장소 루트에서 실행: python3 scripts/build_single.py
- 결과: dist/낱개/ 안에 HTML 6개. 그 외 파일은 없습니다.

사내 메일이 압축파일(zip)을 아예 막는 경우에 씁니다.
압축 없이 HTML 파일만 보내려면 파일 하나가 혼자서도 돌아가야 하므로,
따로 있던 부품(gloss.js·글꼴)을 각 HTML 안에 넣어 자립형으로 만듭니다.

'🏠 대문' 버튼만 같은 폴더에 6개가 다 있어야 동작하고,
그 밖의 기능은 파일 하나만 있어도 전부 됩니다.
"""
import importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('bp', os.path.join(ROOT, 'scripts', 'build_package.py'))
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

OUTDIR = os.path.join(ROOT, 'dist', '낱개')


def inline_gloss(s, gloss, log):
    """<script src="gloss.js"> 를 내용째로 바꿔 파일 하나로 만든다"""
    tag = '<script src="gloss.js"></script>'
    if tag not in s:
        return s
    # 자바스크립트 안에 '</script' 라는 글자가 있으면 거기서 HTML 이 끊긴다. 막아 둔다.
    safe = gloss.replace('</script', '<\\/script')
    s = s.replace(tag, '<script>\n/* 보험용어 사전 (gloss.js 를 파일 안에 넣음) */\n'
                       + safe + '\n</script>', 1)
    log.append(f'  보험용어 사전을 파일 안에 넣음 ({len(gloss)//1024:,}KB)')
    return s


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    for f in os.listdir(OUTDIR):
        os.remove(os.path.join(OUTDIR, f))

    gloss = open(os.path.join(ROOT, 'gloss.js'), encoding='utf-8').read()
    import base64
    font_b64 = base64.b64encode(open(bp.FONT, 'rb').read()).decode('ascii')

    total = 0
    for src, name in [('index.html', bp.HOME)] + [(t, t) for t in bp.TOOLS]:
        log = []
        s = open(os.path.join(ROOT, src), encoding='utf-8').read()
        s = bp.offline(name, s, log, font_b64)
        s = inline_gloss(s, gloss, log)
        bp.globals().pop('_INNER', None) if hasattr(bp, 'globals') else None

        # 남의 파일을 불러오는 곳이 없어야 한다 (글꼴·사전·CDN 전부 안에 들어갔는지)
        bad = re.findall(r'<script[^>]+src="(?!data:)[^"]+"|'
                         r'<link[^>]+rel="stylesheet"[^>]*href="(?!data:)[^"]+"', s)
        if bad:
            sys.exit(f'{name}: 아직 바깥 파일을 부릅니다 → {bad[:3]}')

        p = os.path.join(OUTDIR, name)
        open(p, 'w', encoding='utf-8').write(s)
        n = os.path.getsize(p)
        total += n
        print(f'{name}')
        for line in log:
            print(line)
        print(f'  -> {n/1024/1024:.1f} MB')

    print(f'\ndist/낱개/ · HTML {len(bp.TOOLS)+1}개 · 합계 {total/1024/1024:.1f} MB')
    print('각 파일은 혼자서도 동작합니다. 같은 폴더에 두면 \'🏠 대문\' 버튼도 됩니다.')


if __name__ == '__main__':
    main()
