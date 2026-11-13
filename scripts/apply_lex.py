# -*- coding: utf-8 -*-
"""
질병 검색 사전(ui/meai-lex.js) 끼워 넣기 — 특약검색기와 보상시뮬레이터가 같은 사전을 쓴다

  ui/meai-lex.js  →  tool.html 의 <script id="meai-lex">  (DATA 바로 뒤)
                  →  tool.html 안 보상시뮬레이터(SIMSRC, base64) 의 <script id="meai-lex">  (본 스크립트 바로 앞)

사전은 「일상 병명 · 신체부위 말 → 공식 병명 글자」만 갖는다. 질병코드는 하나도 없다 —
코드는 언제나 DATA.codenames(공식 KCD 코드 → 병명) · DATA.synonyms(감수된 묶음)에서 나온다.
사전을 고친 뒤 :
    node scripts/check_lex.js        (값마다 공식 병명에서 1개 이상 찾아지는지 — 실패하면 끼우지 않는다)
    python3 scripts/apply_lex.py     (같은 내용이면 파일을 건드리지 않는다)
"""
import base64, io, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
JS = io.open(os.path.join(ROOT, 'ui', 'meai-lex.js'), encoding='utf-8').read().strip()
if '</script' in JS.lower():
    sys.exit('meai-lex.js 안에 </script 글자가 있으면 끼울 수 없습니다')
BLOCK = '<script id="meai-lex">\n' + JS + '\n</script>'
OLD = re.compile(r'<script id="meai-lex">.*?</script>', re.S)


def put(html, before):
    """이미 있으면 바꿔 끼우고, 없으면 before 글자 바로 앞에 넣는다"""
    if OLD.search(html):
        return OLD.sub(lambda m: BLOCK, html, count=1)
    i = html.index(before)
    return html[:i] + BLOCK + '\n' + html[i:]


def main():
    r = subprocess.run(['node', os.path.join(ROOT, 'scripts', 'check_lex.js')], capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
    if r.returncode != 0:
        print(r.stdout); sys.exit('사전 점검 실패 — 끼우지 않았습니다')
    s = io.open(TOOL, encoding='utf-8').read()
    n = s
    # 1) 특약검색기 : DATA 스크립트 바로 뒤
    if not OLD.search(n[:n.index('<script id="SIMSRC"')]):
        d = n.index('<script id="DATA"'); e = n.index('</script>', d) + len('</script>')
        n = n[:e] + '\n' + BLOCK + n[e:]
    else:
        head, tail = n[:n.index('<script id="SIMSRC"')], n[n.index('<script id="SIMSRC"'):]
        n = OLD.sub(lambda m: BLOCK, head, count=1) + tail
    # 2) 보상시뮬레이터(SIMSRC) : 본 스크립트(const __RAW) 앞
    m = re.search(r'(<script id="SIMSRC" type="text/plain">)(.*?)(</script>)', n, re.S)
    inner = base64.b64decode(m.group(2).strip()).decode('utf-8')
    i2 = put(inner, '<script>\nconst __RAW=')
    if i2 != inner:
        n = n[:m.start(2)] + base64.b64encode(i2.encode('utf-8')).decode('ascii') + n[m.end(2):]
    if n != s:
        io.open(TOOL, 'w', encoding='utf-8').write(n)
        print('tool.html 에 질병 검색 사전을 끼웠습니다(특약검색기 · 보상시뮬레이터)')
    else:
        print('바뀐 것 없음')


if __name__ == '__main__':
    main()
