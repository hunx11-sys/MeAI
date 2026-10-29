"""타로 78장 그림 손질 — 1909년 라이더-웨이트-스미스 원판(공개 저작물)을 카드 틀에 넣을 그림으로 바꾼다.

원본 : npm 꾸러미 @cometpisces/tarot-kit-images@0.2.0 의 images/ (300x527 PNG, 1909 원판 색)
      받는 법 : npm pack @cometpisces/tarot-kit-images@0.2.0 → 압축 풀기 → package/images
      (1971년 U.S. Games 재채색판은 저작권 표시가 있어 쓰지 않는다)

하는 일
  1. 바깥 남색 테두리(6px)와 그림의 검은 외곽선(1px)을 잘라낸다
  2. 아래 영문 제목띠(메이저 · 에이스 · 궁정 카드)를 찾아 잘라낸다 — 숫자 카드(2~10)는 원판에 제목띠가 없다
  3. 모든 그림을 같은 비율(286x484)로 맞춘다 (제목띠 있는 카드는 양옆, 없는 카드는 아래를 조금 덜어냄)
  4. 색을 아주 조금만 또렷하게 (채도 +8%, 대비 +4%)
  5. WebP 로 저장 : fortune/assets/tarot/00.webp ~ 77.webp (카드 번호 = 화면 데이터의 deck id)

카드 번호 : 0~21 메이저, 22부터 완드 · 컵 · 소드 · 펜타클 순서로 14장씩 (에이스, 2~10, 시종, 기사, 여왕, 왕)

쓰는 법 : python3 fortune/tools/prep_tarot.py <package/images 폴더> [--sheet 대조표.jpg]
"""
import argparse
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets', 'tarot')

MAJOR_FILES = ['00-TheFool', '01-TheMagician', '02-TheHighPriestess', '03-TheEmpress', '04-TheEmperor',
               '05-TheHierophant', '06-TheLovers', '07-TheChariot', '08-Strength', '09-TheHermit',
               '10-WheelOfFortune', '11-Justice', '12-TheHangedMan', '13-Death', '14-Temperance',
               '15-TheDevil', '16-TheTower', '17-TheStar', '18-TheMoon', '19-TheSun', '20-Judgement',
               '21-TheWorld']
SUITS = ['Wands', 'Cups', 'Swords', 'Pentacles']   # 화면 데이터의 수트 순서와 같다
NAVY = (10, 8, 26)
EDGE = 7               # 남색 테두리 6px + 그림 외곽선 1px
TW, TH = 286, 484      # 맞출 크기 (가로:세로 = 0.591)


def files():
    out = [f + '.png' for f in MAJOR_FILES]
    for s in SUITS:
        out += ['%s%02d.png' % (s, r) for r in range(1, 15)]
    return out


def band_top(im):
    """아래 제목띠 위의 가로 검은 선 위치. 없으면 None."""
    w, h = im.size
    px = im.load()
    for y in range(h - 30, h - 90, -1):          # 아래에서 위로 훑어 가장 아래쪽 선을 찾는다
        dark = 0
        for x in range(EDGE + 3, w - EDGE - 3):
            r, g, b = px[x, y]
            if r * .3 + g * .59 + b * .11 < 95:
                dark += 1
        if dark > (w - 2 * EDGE - 6) * .86:
            # 선이 두세 줄 겹친 경우 가장 위쪽 줄까지 올라간다
            while y > 0:
                dark = sum(1 for x in range(EDGE + 3, w - EDGE - 3, 2)
                           if px[x, y - 1][0] * .3 + px[x, y - 1][1] * .59 + px[x, y - 1][2] * .11 < 95)
                if dark > (w - 2 * EDGE - 6) / 2 * .86:
                    y -= 1
                else:
                    break
            return y
    return None


def bottom_edge(im):
    """남색 테두리가 시작되는 줄(그림 맨 아래 바로 밑)."""
    w, h = im.size
    px = im.load()
    for y in range(h - 1, 0, -1):
        if px[w // 2, y] != NAVY:
            return y        # 그림 외곽선 줄
    return h


def prep(src):
    im = Image.open(src).convert('RGBA')
    bg = Image.new('RGBA', im.size, NAVY + (255,))
    bg.alpha_composite(im)
    im = bg.convert('RGB')
    w, h = im.size
    bt = band_top(im)
    bottom = bt if bt else bottom_edge(im)
    art = im.crop((EDGE, EDGE, w - EDGE, bottom))
    aw, ah = art.size
    # 같은 비율로 맞추기 (cover)
    k = max(TW / aw, TH / ah)
    nw, nh = round(aw * k), round(ah * k)
    art = art.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - TW) // 2
    y0 = 0 if nh > TH else 0        # 세로가 남으면 아래를 덜어낸다(위쪽 숫자 보존)
    art = art.crop((x0, y0, x0 + TW, y0 + TH))
    art = ImageEnhance.Color(art).enhance(1.08)
    art = ImageEnhance.Contrast(art).enhance(1.04)
    art = art.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
    return art, bt is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('images')
    ap.add_argument('--sheet', help='78장 대조표 그림 저장 경로')
    ap.add_argument('--quality', type=int, default=76)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    total, arts = 0, []
    for i, f in enumerate(files()):
        src = os.path.join(a.images, f)
        if not os.path.exists(src):
            sys.exit('없는 파일 : ' + src)
        art, band = prep(src)
        dst = os.path.join(OUT, '%02d.webp' % i)
        art.save(dst, 'WEBP', quality=a.quality, method=6)
        total += os.path.getsize(dst)
        arts.append(art)
        print('%02d %-22s 제목띠 %s  %5.1fKB' % (i, f, '있음' if band else '없음', os.path.getsize(dst) / 1024))
    print('합계 %.0fKB (%d장)' % (total / 1024, len(arts)))
    if a.sheet:
        cols, s = 13, 0.5
        cw, ch = int(TW * s), int(TH * s)
        sheet = Image.new('RGB', (cols * cw, 6 * ch), (20, 16, 40))
        for i, art in enumerate(arts):
            sheet.paste(art.resize((cw, ch)), ((i % cols) * cw, (i // cols) * ch))
        sheet.save(a.sheet, quality=82)


if __name__ == '__main__':
    main()
