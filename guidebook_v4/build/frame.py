"""캡처 PNG 에 둥근 모서리 + 얇은 테두리를 입힌다. 사용: python3 frame.py in.png out.png [radius_px] [border_hex]"""
import sys
from PIL import Image, ImageDraw
def frame(src, dst, radius=28, border='D1D6DB', bw=2, maxw=2400):
    im = Image.open(src).convert('RGBA')
    if im.size[0] > maxw:
        r = maxw / im.size[0]; im = im.resize((maxw, int(im.size[1]*r)), Image.LANCZOS); radius = max(8, int(radius*r))
    w, h = im.size
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w-1, h-1], radius=radius, fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, w-1, h-1], radius=radius, outline='#'+border, width=bw)
    out.save(dst)
    return dst
if __name__ == '__main__':
    a = sys.argv
    frame(a[1], a[2], int(a[3]) if len(a) > 3 else 28, a[4] if len(a) > 4 else 'D1D6DB', 2, int(a[5]) if len(a) > 5 else 2400)
    print('ok', a[2])
