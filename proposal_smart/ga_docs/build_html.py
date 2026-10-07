# -*- coding: utf-8 -*-
"""data.json + tpl.html + 캡처(p1~p6.jpg) → 오프라인 단일 HTML
  python3 build_html.py <data.json> <캡처폴더> <out.html> [캡처 설계서 이름]"""
import os, sys, os, base64
D, CAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
label = sys.argv[4] if len(sys.argv) > 4 else 'The건강한 5.10.5 여44 설계서'
here = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(here, 'tpl.html'), encoding='utf-8').read()
t = t.replace('(The건강한 5.10.5 여44 설계서)', '(%s)' % label)
d = open(D, encoding='utf-8').read().replace('</', '<\\/')
h = t.replace('__DATA__', d)
imgs = {i: 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(CAP, 'p%d.jpg' % i), 'rb').read()).decode() for i in range(1, 7)}
js = "const IMG=" + str({str(k): v for k, v in imgs.items()}).replace("'", '"') + ";"
old = '<img src="p\'+st.p+\'.jpg"'
assert old in h, 'tpl img tag'
h = h.replace(old, '<img src="\'+IMG[st.p]+\'"')
h = h.replace("const D=JSON.parse(document.getElementById('DATA').textContent);", js + "\nconst D=JSON.parse(document.getElementById('DATA').textContent);")
doc = '<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
i = h.index('<div class="wrap">')
open(OUT, 'w', encoding='utf-8').write(doc + h[:i] + '</head><body>\n' + h[i:] + '\n</body></html>\n')
print('saved', OUT, os.path.getsize(OUT) // 1024, 'KB')
