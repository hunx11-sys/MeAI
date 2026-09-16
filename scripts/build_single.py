#!/usr/bin/env python3
"""
낱개 HTML 배포판 만들기 — 압축파일을 못 보낼 때
- 저장소 루트에서 실행: python3 scripts/build_single.py
- 결과: dist/single/ 안에 HTML 6개. 그 외 파일은 없습니다.

사내 메일이 압축파일(zip)을 아예 막는 경우에 씁니다.
압축 없이 HTML 만 보내려면 파일 하나가 혼자서도 돌아가야 하므로,
따로 있던 부품(gloss.js·글꼴)을 각 HTML 안에 넣어 자립형으로 만듭니다.

파일 이름은 영문으로 바꿉니다. 한글 이름은 메일을 거치며 깨지는 일이 흔합니다.
'🏠 대문' 버튼만 같은 폴더에 6개가 다 있어야 동작하고,
그 밖의 기능은 파일 하나만 있어도 전부 됩니다.
"""
import base64, importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('bp', os.path.join(ROOT, 'scripts', 'build_package.py'))
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

OUTDIR = os.path.join(ROOT, 'dist', 'single')

# 대문 이름을 먼저 바꿔 둔다. 그래야 bp.offline() 이 tool.html 안에 base64 로
# 들어 있는 보상시뮬레이터의 '🏠 대문' 링크까지 같은 이름으로 맞춰 준다.
# (겉의 글자만 바꾸면 base64 안쪽은 손이 닿지 않아 링크가 깨진다)
bp.HOME = 'home.html'

# 저장소 파일 → 보낼 이름 (메일에서 안 깨지도록 영문으로)
NAMES = {
    'index.html':      'home.html',
    'tool.html':       'tool.html',
    'products.html':   'products.html',
    'prompts.html':    'prompts.html',
    '명패생성기.html':  'nameplate.html',
    '통합치료비.html':  'care.html',
}


def inline_gloss(s, gloss, log):
    """<script src="gloss.js"> 를 내용째로 바꿔 파일 하나로 만든다"""
    tag = '<script src="gloss.js"></script>'
    if tag not in s:
        return s
    # 자바스크립트 안에 '</script' 라는 글자가 있으면 거기서 HTML 이 끊긴다. 막아 둔다.
    safe = gloss.replace('</script', '<\\/script')
    s = s.replace(tag, '<script>\n/* 보험용어 사전 (gloss.js 를 파일 안에 넣음) */\n'
                       + safe + '\n</script>', 1)
    log.append(f'  보험용어 사전을 파일 안에 넣음 ({len(gloss) // 1024:,}KB)')
    return s


def relink(s, log):
    """대문이 부르는 도구 링크를 보낼 이름으로 맞춘다 (대문 링크는 bp 가 이미 처리)"""
    n = 0
    for src, dst in NAMES.items():
        if src == dst or src == 'index.html':
            continue
        k = s.count(f'href="{src}"')
        if k:
            s = s.replace(f'href="{src}"', f'href="{dst}"')
            n += k
    if n:
        log.append(f'  도구 링크 {n}곳을 보낼 이름으로 맞춤')
    return s


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    for f in os.listdir(OUTDIR):
        os.remove(os.path.join(OUTDIR, f))

    gloss = open(os.path.join(ROOT, 'gloss.js'), encoding='utf-8').read()
    font_b64 = base64.b64encode(open(bp.FONT, 'rb').read()).decode('ascii')

    total = 0
    for src, out in NAMES.items():
        log = []
        s = open(os.path.join(ROOT, src), encoding='utf-8').read()
        s = bp.offline(out, s, log, font_b64)
        s = inline_gloss(s, gloss, log)
        s = relink(s, log)

        # 남의 파일을 부르는 곳이 없어야 한다 (글꼴·사전·CDN 이 전부 안에 들어갔는지)
        bad = re.findall(r'<script[^>]+src="(?!data:)[^"]+"|'
                         r'<link[^>]+rel="stylesheet"[^>]*href="(?!data:)[^"]+"', s)
        if bad:
            sys.exit(f'{out}: 아직 바깥 파일을 부릅니다 → {bad[:3]}')

        p = os.path.join(OUTDIR, out)
        open(p, 'w', encoding='utf-8').write(s)
        n = os.path.getsize(p)
        total += n
        print(f'{src}  →  {out}')
        for line in log:
            print(line)
        print(f'  -> {n / 1024 / 1024:.1f} MB')

    # 서로 부르는 링크가 실제로 있는 파일을 가리키는지 확인.
    # tool.html 안에 base64 로 든 보상시뮬레이터도 풀어서 같이 본다.
    made = set(os.listdir(OUTDIR))
    for f in sorted(made):
        s = open(os.path.join(OUTDIR, f), encoding='utf-8').read()
        parts = [(f, s)]
        m = re.search(r'<script id="SIMSRC"[^>]*>(.*?)</script>', s, re.S)
        if m:
            parts.append((f + ' 안의 보상시뮬레이터',
                          base64.b64decode(m.group(1).strip()).decode('utf-8')))
        for who, text in parts:
            for href in set(re.findall(r'href="([^"#?]+\.html)[^"]*"', text)):
                if href not in made:
                    sys.exit(f'{who}: 없는 파일을 가리킵니다 → {href}')

    print(f'\ndist/single/ · HTML {len(made)}개 · 합계 {total / 1024 / 1024:.1f} MB · 링크 확인 완료')
    print("각 파일은 혼자서도 동작합니다. 같은 폴더에 두면 '🏠 대문' 버튼도 됩니다.")


if __name__ == '__main__':
    main()
