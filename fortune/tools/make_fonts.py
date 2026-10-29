"""오늘의 운세 글꼴 3종을 필요한 글자만 남겨 woff2 로 만든다 (파일 안에 심을 용도).

  serif-ko.woff2 : 고운바탕 Bold — 한글 제목 · 카드 이름 · 사람 이름. 자주 쓰는 한글 2,350자(KS X 1001) + 화면 글에 나오는 한글 전부
  hanja.woff2    : Noto Serif KR 700 — 사주 한자(甲乙丙… 子丑寅… 木火土金水 四柱八字). 화면 · 엔진 파일에 나오는 한자만
  cinzel.woff2   : Cinzel 700 — 로마 숫자 · 영문 카드 이름 (MeAI · TAROT 등)

세 글꼴 모두 SIL Open Font License 1.1 (fortune/assets/fonts/OFL.txt). 원본은 github.com/google/fonts 의
  ofl/gowunbatang/GowunBatang-Bold.ttf · ofl/notoserifkr/NotoSerifKR[wght].ttf · ofl/cinzel/Cinzel[wght].ttf

쓰는 법 : python3 fortune/tools/make_fonts.py <원본 ttf 폴더>
화면 글(src/*.html · src/*.js)에 새 한자가 들어가면 다시 돌린다.
"""
import glob
import io
import os
import re
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
OUT = os.path.join(ROOT, 'assets', 'fonts')
PUNCT = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~·‘’“”…「」『』~→←↑↓★☆✦×'


def ksx2350():
    out = []
    for b1 in range(0xB0, 0xC9):
        for b2 in range(0xA1, 0xFF):
            try:
                out.append(bytes([b1, b2]).decode('euc-kr'))
            except UnicodeDecodeError:
                pass
    return ''.join(out)


def source_text():
    s = ''
    for f in glob.glob(os.path.join(ROOT, 'src', '*')):
        s += open(f, encoding='utf-8').read()
    return s


def build(src, text, out, wght=None):
    f = TTFont(src)
    if wght is not None and 'fvar' in f:
        f = instancer.instantiateVariableFont(f, {'wght': wght})
    opt = subset.Options()
    opt.flavor = 'woff2'
    opt.layout_features = ['*']
    opt.name_IDs = ['*']
    opt.notdef_outline = True
    ss = subset.Subsetter(opt)
    ss.populate(text=text)
    ss.subset(f)
    buf = io.BytesIO()
    f.flavor = 'woff2'
    f.save(buf)
    open(out, 'wb').write(buf.getvalue())
    cmap = f.getBestCmap()
    print('%-14s %6.1fKB  글자 %d' % (os.path.basename(out), len(buf.getvalue()) / 1024, len(cmap)))
    return cmap


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    txt = source_text()
    hangul = ''.join(sorted(set(re.findall('[가-힣]', txt))))
    hanja = ''.join(sorted(set(re.findall('[一-鿿]', txt))))
    build(os.path.join(d, 'GowunBatang-Bold.ttf'), ksx2350() + hangul + PUNCT, os.path.join(OUT, 'serif-ko.woff2'))
    cm = build(os.path.join(d, 'NotoSerifKR[wght].ttf'), hanja, os.path.join(OUT, 'hanja.woff2'), 700)
    miss = [c for c in hanja if ord(c) not in cm]
    if miss:
        print('한자 글꼴에 없는 글자 :', ''.join(miss))
    build(os.path.join(d, 'Cinzel[wght].ttf'), PUNCT, os.path.join(OUT, 'cinzel.woff2'), 700)
    print('한자 %d자 : %s' % (len(hanja), hanja))


if __name__ == '__main__':
    main()
