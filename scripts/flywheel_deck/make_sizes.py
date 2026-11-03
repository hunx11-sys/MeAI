# 캡처 그림의 원래 크기 표(sizes.json). build_deck.js 가 자르기 · 번호 자리 계산에 쓴다
import json, glob, os, sys
from PIL import Image
W = sys.argv[1]
d = {}
for f in glob.glob(os.path.join(W, 'cap', '**', '*.png'), recursive=True) + glob.glob(os.path.join(W, 'sp', '*.png')) + glob.glob(os.path.join(W, 'ref', '*.png')):
    d[os.path.relpath(f, W)] = Image.open(f).size
json.dump(d, open(os.path.join(W, 'sizes.json'), 'w'), ensure_ascii=False, indent=0)
print(len(d), '장')
