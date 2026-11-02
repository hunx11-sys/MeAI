# flow.html(흐름 시연판)에 쓰는 글자만 담은 Pretendard 를 만들어 파일 안에 넣는다.
# 파일로 열면(file://) 브라우저가 옆 글꼴 파일을 막기 때문(도구 배포판과 같은 이유).
# 쓰는 법 : python3 scripts/build_flow_font.py      (flow.html 글을 고친 뒤 다시 돌린다 · fonttools 필요)
import base64, io, os, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'flow.html')
SRC = os.path.join(ROOT, 'assets', 'pretendard-subset.woff2')     # 도구들과 같은 원본(Pretendard 가변 · OFL)

s = open(HTML, encoding='utf-8').read()
body = re.sub(r'/\*FONT\*/.*?/\*/FONT\*/', '', s, flags=re.S)
chars = set(body) | set(''.join(chr(c) for c in range(0x20, 0x7f))) | set('▶✓·…「」→×')
font = TTFont(SRC)
opt = subset.Options(); opt.flavor = 'woff2'; opt.layout_features = ['*']; opt.notdef_outline = True
sub = subset.Subsetter(opt); sub.populate(text=''.join(sorted(chars))); sub.subset(font)
buf = io.BytesIO(); font.flavor = 'woff2'; font.save(buf)
data = base64.b64encode(buf.getvalue()).decode()
face = ('/*FONT*/@font-face { font-family: "Pretendard Variable"; font-weight: 45 930; font-style: normal; font-display: swap; '
        f'src: url(data:font/woff2;base64,{data}) format("woff2"); }}/*/FONT*/')
s = re.sub(r'/\*FONT\*/.*?/\*/FONT\*/', lambda m: face, s, count=1, flags=re.S)
open(HTML, 'w', encoding='utf-8').write(s)
miss = [c for c in chars if ord(c) > 127 and ord(c) not in font.getBestCmap()]
print(f'글자 {len(chars)}개 · 글꼴 {len(buf.getvalue()) // 1024}KB · 원본에 없는 글자 {"".join(miss) or "없음"}')
