# -*- coding: utf-8 -*-
"""MeAI홈 오픈 30초 영상 v2 : Canva 완성본(장당 5초, 55초)을 애니메이션처럼 다시 편집한다.

- 장마다 정지 화면 한 장을 뽑아, 줌·흔들림·번쩍임·화면 전환으로 움직임을 준다.
- 말풍선(말·외침·생각)을 톡 튀어나오게 얹고, 화면 장면에는 캐릭터 얼굴 아이콘을 붙인다.
- 효과음은 직접 합성한다(저작권 걱정 없음). 총 30초, 세로 1080x1920.

  python animate_v2.py <Canva에서 받은 mp4> [--out 결과.mp4]
"""
import argparse
import math
import os
import random
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from build_video import FONT_DIR, ffmpeg_exe

HERE_FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

W, H, FPS = 1080, 1920, 30
RED = (232, 38, 45)
SR = 44100


def font(size, weight="ExtraBold"):
    return ImageFont.truetype(os.path.join(FONT_DIR, "NanumGothic-%s.ttf" % weight), size)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def back(x):
    """살짝 넘쳤다 돌아오는 튕김(말풍선 팝업용)."""
    x = min(max(x, 0.0), 1.0)
    c = 2.2
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


# ---------------------------------------------------------------- 원본에서 장면 뽑기
def grab(src, tmp):
    plates = []
    for i in range(11):
        p = os.path.join(tmp, "p%02d.png" % i)
        subprocess.run([ffmpeg_exe(), "-v", "error", "-y", "-ss", "%.2f" % (i * 5 + 2.5), "-i", src,
                        "-frames:v", "1", p], check=True)
        plates.append(Image.open(p).convert("RGB").resize((W, H)))
    return plates


# ---------------------------------------------------------------- 카메라
def cam(im, zoom=1.0, cx=0.5, cy=0.5, dx=0, dy=0):
    """zoom 배 확대해 (cx,cy) 지점을 가운데로, dx/dy 만큼 흔든다."""
    zw, zh = int(W * zoom), int(H * zoom)
    big = im.resize((zw, zh), Image.BILINEAR) if zoom != 1.0 else im
    x = int(cx * zw - W / 2 + dx)
    y = int(cy * zh - H / 2 + dy)
    x = max(0, min(zw - W, x)) if zoom >= 1 else x
    y = max(0, min(zh - H, y)) if zoom >= 1 else y
    return big.crop((x, y, x + W, y + H))


def shake(t, amp, freq=28, seed=0):
    r = random.Random(int(t * freq) + seed * 1000)
    return r.uniform(-amp, amp), r.uniform(-amp, amp)


def flash(im, a, color=(255, 255, 255)):
    if a <= 0:
        return im
    return Image.blend(im, Image.new("RGB", (W, H), color), min(1.0, a))


def glitch(im, amount, seed):
    rnd = random.Random(seed)
    a = np.array(im)
    for _ in range(int(6 + 26 * amount)):
        y = rnd.randrange(0, H - 10)
        h = rnd.randrange(4, int(10 + 90 * amount))
        a[y:y + h] = np.roll(a[y:y + h], rnd.randrange(-int(220 * amount) - 1, int(220 * amount) + 1), axis=1)
    sh = int(4 + 22 * amount)
    a[:, :, 0] = np.roll(a[:, :, 0], sh, axis=1)
    a[:, :, 2] = np.roll(a[:, :, 2], -sh, axis=1)
    return Image.fromarray(a)


def speed_lines(im, t, alpha=90, seed=3):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rnd = random.Random(int(t * 12) + seed)
    for _ in range(46):
        a = rnd.uniform(0, 2 * math.pi)
        r0 = rnd.uniform(520, 700)
        d.line([W / 2 + math.cos(a) * r0, H / 2 + math.sin(a) * r0 * 1.3,
                W / 2 + math.cos(a) * 1500, H / 2 + math.sin(a) * 1900], fill=(255, 255, 255, alpha),
               width=rnd.randint(3, 9))
    im = im.convert("RGBA")
    im.alpha_composite(lay)
    return im.convert("RGB")


def reveal(im, base, box, k, direction="up"):
    """box 영역을 k(0~1)만큼만 보이게 하고 나머지는 base 로 덮는다(차오르기·출력 효과)."""
    x0, y0, x1, y1 = box
    out = im.copy()
    cover = base.crop(box)
    hgt = y1 - y0
    if direction == "up":   # 아래에서 위로 차오름
        cut = int(hgt * (1 - k))
        if cut > 0:
            out.paste(cover.crop((0, 0, x1 - x0, cut)), (x0, y0))
    else:                   # 위에서 아래로 출력
        cut = int(hgt * k)
        if cut < hgt:
            out.paste(cover.crop((0, cut, x1 - x0, hgt)), (x0, y0 + cut))
    return out


# ---------------------------------------------------------------- 말풍선
def rich(text):
    """'[강조]' 표시한 글자는 빨간색으로. 줄마다 (글자, 강조여부) 조각 목록을 돌려준다."""
    out = []
    for line in text.split("\n"):
        segs, hot, buf = [], False, ""
        for ch in line:
            if ch in "[]":
                if buf:
                    segs.append((buf, hot))
                buf, hot = "", ch == "["
            else:
                buf += ch
        if buf:
            segs.append((buf, hot))
        out.append(segs)
    return out


STYLE = {
    #        바탕색            글자색          강조색      글꼴 굵기
    "say":   ((255, 255, 255), (26, 26, 34), RED, "Bold"),
    "shout": (RED, (255, 255, 255), (255, 232, 120), "Black"),
    "think": ((246, 247, 252), (70, 72, 86), RED, "SemiBold"),
}


def bubble(im, t0, t, text, box, tail, kind="say", size=58, face=None):
    """t0 에 부드럽게 튀어나오는 말풍선. box=(x,y,w,h) 풍선 자리, tail=(x,y) 꼬리가 가리키는 곳."""
    if t < t0:
        return im
    p = min(1.0, (t - t0) / 0.32)
    sc = 0.6 + 0.4 * back(p)
    alpha = min(1.0, p * 2.2)
    x, y, w, h = box
    bg, fg, hot, wt = STYLE[kind]
    pad = 60
    lay = Image.new("RGBA", (w + pad * 2, h + pad * 2 + 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ox, oy = pad, pad
    rad = min(h // 2, 64)
    tx, ty = tail
    below = ty > y + h
    bx = min(max(tx, x + rad + 30), x + w - rad - 30) - x + ox
    # 꼬리(작은 삼각형) : 얼굴 아이콘이 옆에 있으면 왼쪽, 아니면 위·아래
    left = tx < x and y - 120 <= ty <= y + h + 160
    if kind == "think":
        for j, r in enumerate([16, 10]):
            cx_ = bx + (tx - x + ox - bx) * (0.35 + 0.35 * j)
            cy_ = (oy + h + 26 + 30 * j) if below else (oy - 26 - 30 * j)
            d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=bg + (255,))
    elif left:
        my = oy + min(max(ty - y, rad), h - rad)
        d.polygon([(ox + 4, my - 24), (ox + 4, my + 24), (ox - 40, my + 6)], fill=bg + (255,))
    else:
        tip_x = bx + (tx - x + ox - bx) * 0.45
        if below:
            d.polygon([(bx - 26, oy + h - 4), (bx + 26, oy + h - 4), (tip_x, oy + h + 46)], fill=bg + (255,))
        else:
            d.polygon([(bx - 26, oy + 4), (bx + 26, oy + 4), (tip_x, oy - 46)], fill=bg + (255,))
    d.rounded_rectangle([ox, oy, ox + w, oy + h], rad, fill=bg + (255,))
    if kind == "say":   # 왼쪽 빨간 포인트 막대
        d.rounded_rectangle([ox + 26, oy + h * 0.28, ox + 34, oy + h * 0.72], 4, fill=RED + (255,))
    # 그림자
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.45)))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    base = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    base.alpha_composite(sh, (0, 14))
    base.alpha_composite(lay)
    d = ImageDraw.Draw(base)
    # 글자
    f = ImageFont.truetype(os.path.join(HERE_FONTS, "Pretendard-%s.otf" % wt), size)
    rows = rich(text)
    lh = size * 1.32
    top = oy + h / 2 - lh * len(rows) / 2 + size * 0.1
    for i, segs in enumerate(rows):
        tw = sum(d.textlength(sg, font=f) for sg, _ in segs)
        cx0 = ox + w / 2 - tw / 2 + (10 if kind == "say" else 0)
        for sg, isHot in segs:
            d.text((cx0, top + i * lh), sg, font=f, fill=(hot if isHot else fg) + (255,))
            cx0 += d.textlength(sg, font=f)
    if kind == "shout":
        base = base.rotate(-4, resample=Image.BICUBIC, center=(ox + w / 2, oy + h / 2))
    # 크기·투명도 애니메이션 (풍선 가운데 기준, 살짝 위로 떠오름)
    bw, bh = base.size
    nw, nh = max(1, int(bw * sc)), max(1, int(bh * sc))
    base = base.resize((nw, nh), Image.BILINEAR)
    if alpha < 1:
        base.putalpha(base.getchannel("A").point(lambda v: int(v * alpha)))
    cx, cy = x + w / 2, y + h / 2 + 18 * (1 - ease(p))
    px = int(cx - (ox + w / 2) * sc)
    py = int(cy - (oy + h / 2) * sc)
    im = im.convert("RGBA")
    if face is not None:
        fk = 0.6 + 0.4 * back(min(1.0, (t - t0) / 0.26))
        fs = max(1, int(face.width * fk))
        fc = face.resize((fs, fs), Image.BILINEAR)
        im.alpha_composite(fc, (int(tx - fs / 2), int(ty - fs / 2)))
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.paste(base, (px, py), base)
    im.alpha_composite(full)
    return im.convert("RGB")


def make_face(eyes_plate):
    """눈이 커진 장면에서 얼굴만 동그랗게 잘라 아이콘으로 쓴다(흰 테 + 빨간 테 + 그림자)."""
    n = 176
    face = eyes_plate.crop((170, 360, 930, 1120)).resize((n, n), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse([0, 0, n - 1, n - 1], fill=255)
    face.putalpha(m)
    out = Image.new("RGBA", (n + 40, n + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([14, 22, n + 26, n + 34], fill=(0, 0, 0, 120))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.ellipse([12, 12, n + 28, n + 28], fill=RED + (255,))
    d.ellipse([16, 16, n + 24, n + 24], fill=(255, 255, 255, 255))
    out.alpha_composite(face.resize((n - 4, n - 4)), (22, 22))
    return out


# ---------------------------------------------------------------- 장면 연출
def build_scenes(P):
    face = make_face(P[8])
    dark = Image.new("RGB", (W, H), (20, 8, 11))
    black = Image.new("RGB", (W, H), (0, 0, 0))

    def s_despair(t, d):
        z = 1.0 + 0.10 * t / d
        dx, dy = shake(t, 3)
        im = cam(P[0], z, 0.5, 0.45, dx, dy)
        im = bubble(im, 0.5, t, "고객 명단이…\n또 텅 비었네", (90, 190, 620, 250), (560, 700), "think", 56)
        im = bubble(im, 2.3, t, "휴…", (720, 1260, 240, 140), (640, 1060), "say", 58)
        return im

    def s_glitch(t, d):
        dx, dy = shake(t, 22, seed=2)
        im = cam(P[1], 1.06, 0.5, 0.5, dx, dy)
        if t < 0.9:
            im = glitch(im, 0.9 - t, int(t * FPS))
        im = flash(im, 0.55 - t * 1.2, (255, 60, 60))
        im = bubble(im, 0.25, t, "뭐, 뭐야?!", (90, 170, 560, 220), (420, 620), "shout", 76)
        return im

    def s_home(t, d):
        z = 1.25 - 0.25 * ease(t / 0.5) - 0.04 * t
        im = cam(P[2], max(1.0, z), 0.5, 0.5 + 0.06 * ease((t - 0.8) / 1.4))
        im = flash(im, 1.0 - t * 3)
        im = bubble(im, 0.9, t, "[MeAI홈]이\n열렸다!", (330, 1560, 520, 210), (220, 1665), "say", 56, face)
        return im

    def s_reco(t, d):
        z = 1.0 + 0.15 * ease(t / 1.2)
        im = cam(P[3], z, 0.5, 0.38)
        im = bubble(im, 0.9, t, "오늘 연락할 고객,\n[MeAI]가 먼저 골라줬어!", (250, 1630, 780, 210), (150, 1735), "say", 50,
                    face)
        return im

    def s_custom(t, d):
        z = 1.0 + 0.22 * ease(t / 1.4)
        im = cam(P[4], z, 0.5, 0.45 + 0.05 * ease(t / 2))
        im = bubble(im, 0.8, t, "계약만 고르면\n[맞춤대화] 바로 시작!", (250, 1600, 780, 220), (150, 1710), "say", 50,
                    face)
        return im

    def s_analysis(t, d):
        k = ease(t / 0.8)
        im = reveal(P[5], dark, (60, 480, 1020, 1300), k, "up")
        im = cam(im, 1.08 - 0.08 * ease(t / 0.3), 0.5, 0.45)
        im = bubble(im, 0.55, t, "부족한 보장이\n[한눈에]!", (330, 1640, 560, 200), (220, 1740), "say", 52, face)
        return im

    def s_design(t, d):
        im = P[6].copy()
        rows = [(100, 480, 980, 660), (100, 690, 980, 870), (100, 900, 980, 1080), (100, 1110, 980, 1290)]
        for i, (x0, y0, x1, y1) in enumerate(rows):
            if t < 0.12 + 0.17 * i:
                im.paste(dark.crop((x0, y0, x1, y1)), (x0, y0))
        if t < 0.9:
            im.paste(dark.crop((0, 1400, W, 1560)), (0, 1400))
        return cam(im, 1.04 - 0.04 * ease(t / 0.4), 0.5, 0.45)

    def s_report(t, d):
        k = ease(t / 0.9)
        im = reveal(P[7], dark, (40, 560, 1040, 1185), k, "down")
        if t < 0.9:
            im.paste(dark.crop((0, 1240, W, 1380)), (0, 1240))
        dx, dy = shake(t, 4 if t < 0.9 else 0, seed=5)
        im = cam(im, 1.05, 0.5, 0.45, dx, dy)
        im = bubble(im, 0.9, t, "[리포트]까지 끝!", (330, 1500, 520, 170), (220, 1585), "say", 54, face)
        return im

    def s_eyes(t, d):
        z = 1.0 + 0.35 * ease(t / 0.6)
        im = cam(P[8], z, 0.5, 0.36)
        im = speed_lines(im, t, 110)
        im = flash(im, 0.6 - t * 2)
        im = bubble(im, 0.25, t, "와…!", (640, 1420, 340, 190), (560, 1250), "shout", 80)
        return im

    def s_fist(t, d):
        dx, dy = shake(t, 26 * max(0.0, 1 - t / 0.5), seed=7)
        z = 1.18 - 0.18 * ease(t / 0.35)
        im = cam(P[9], z, 0.5, 0.55, dx, dy)
        im = speed_lines(im, t, 70 if t < 1.2 else 40, 9)
        im = flash(im, 0.8 - t * 2.5, (255, 220, 220))
        return im

    def s_end(t, d):
        im = P[10].copy()
        a1 = ease((t - 0.2) / 0.6)
        im.paste(black.crop((0, 560, W, 900)), (0, 560)) if a1 <= 0 else None
        if 0 < a1 < 1:
            part = Image.blend(black.crop((0, 560, W, 900)), P[10].crop((0, 560, W, 900)), a1)
            im.paste(part, (0, 560))
        a2 = ease((t - 1.4) / 0.5)
        if a2 < 1:
            seg = Image.blend(black.crop((0, 960, W, 1320)), P[10].crop((0, 960, W, 1320)), max(0, a2))
            im.paste(seg, (0, 960))
        sc = 1.0 + 0.06 * (1 - ease((t - 1.4) / 0.35)) if t > 1.4 else 1.0
        return cam(im, sc, 0.5, 0.58) if sc > 1 else im

    # (함수, 길이) : 합계 30초
    return [(s_despair, 3.4), (s_glitch, 1.8), (s_home, 2.6), (s_reco, 3.0), (s_custom, 3.0),
            (s_analysis, 1.5), (s_design, 1.4), (s_report, 1.6), (s_eyes, 1.3), (s_fist, 3.4), (s_end, 7.0)]


# ---------------------------------------------------------------- 효과음
def make_audio(path, scenes):
    total = sum(d for _, d in scenes)
    n = int(SR * total)
    out = np.zeros(n)
    rng = np.random.default_rng(3)
    starts = np.cumsum([0] + [d for _, d in scenes])

    def add(at, sig, g=1.0):
        i = int(at * SR)
        j = min(n, i + len(sig))
        if i < n:
            out[i:j] += sig[:j - i] * g

    def env(d, dec):
        m = int(d * SR)
        e = np.exp(-np.arange(m) / SR / dec)
        a = min(m, int(0.003 * SR))
        e[:a] *= np.linspace(0, 1, a)
        return e

    def tone(f, d, dec):
        x = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * f * x) * env(d, dec)

    def chirp(f0, f1, d, dec):
        x = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * (f0 + (f1 - f0) * x / d / 2) * x) * env(d, dec)

    def noise(d, dec):
        return rng.uniform(-1, 1, int(d * SR)) * env(d, dec)

    def whoosh(d=0.35):
        w = rng.uniform(-1, 1, int(d * SR))
        w = np.convolve(w, np.ones(10) / 10, "same") * np.sin(np.linspace(0, np.pi, len(w))) ** 2
        return w

    def boom(d=1.0):
        x = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * (85 - 45 * x) * x) * np.exp(-x * 3) + noise(d, 0.06) * 0.35

    def pop():
        return chirp(500, 1500, 0.12, 0.04)

    s = starts
    # 막막함 : 초침 + 한숨
    for k in np.arange(0, 3.4, 0.5):
        add(k, tone(2300 if int(k * 2) % 2 == 0 else 1800, 0.05, 0.008) + noise(0.05, 0.004) * 0.5, 0.4)
    add(s[0] + 0.5, chirp(300, 600, 0.35, 0.12), 0.25)            # 생각 풍선
    add(s[0] + 2.3, np.convolve(rng.uniform(-1, 1, int(0.6 * SR)), np.ones(40) / 40, "same")
        * np.sin(np.linspace(0, np.pi, int(0.6 * SR))), 0.5)       # 한숨
    # 지지직 + 외침
    m = int(1.0 * SR)
    st = rng.uniform(-1, 1, m) * (rng.uniform(0, 1, m // 300 + 1).repeat(300)[:m] > 0.3)
    add(s[1], st, 0.4)
    add(s[1] + 0.25, chirp(900, 1800, 0.18, 0.06), 0.35)
    # 홈 등장 : 휙 + 쾅 + 반짝
    add(s[2] - 0.2, whoosh(), 0.6)
    add(s[2], boom(1.0), 0.8)
    add(s[2] + 0.05, tone(1568, 0.9, 0.3) * 0.5 + tone(2093, 0.9, 0.25) * 0.3, 0.5)
    # 박자(분당 128) : 홈부터 결심 직전까지
    beat = 60 / 128
    t = s[2]
    while t < s[9]:
        x = np.arange(int(0.22 * SR)) / SR
        add(t, np.sin(2 * np.pi * (120 - 70 * x) * x) * np.exp(-x * 20), 0.5)
        add(t + beat / 2, noise(0.05, 0.01), 0.10)
        t += beat
    # 장면 전환 휙
    for i in (3, 4, 5, 6, 7, 8):
        add(s[i] - 0.18, whoosh(0.3), 0.45)
    # 말풍선 뽁
    for at in (s[2] + 0.9, s[3] + 0.9, s[4] + 0.8, s[5] + 0.55, s[7] + 0.9):
        add(at, pop(), 0.35)
    # 맞춤대화 타자
    for k in range(10):
        add(s[4] + 1.2 + k * 0.09, noise(0.03, 0.006), 0.18)
    # 보장분석 차오름
    add(s[5], chirp(300, 900, 0.8, 0.5), 0.25)
    # 자동설계 체크 4번
    for i in range(4):
        add(s[6] + 0.12 + 0.17 * i, tone(988 + 120 * i, 0.12, 0.04), 0.35)
    # 리포트 출력
    for k in range(9):
        add(s[7] + k * 0.1, noise(0.06, 0.02), 0.2)
    add(s[7] + 0.9, tone(1319, 0.5, 0.2), 0.3)
    # 눈 반짝
    add(s[8], whoosh(0.25), 0.5)
    add(s[8] + 0.1, tone(2637, 0.6, 0.15) + tone(3136, 0.6, 0.12), 0.25)
    add(s[8] + 0.25, chirp(700, 1400, 0.25, 0.1), 0.3)
    # 결심 : 쾅 + 상승음
    add(s[9], boom(1.4), 1.0)
    add(s[9] + 0.1, chirp(220, 660, 1.2, 0.6) * 0.4 + tone(523, 1.2, 0.5) * 0.3 + tone(784, 1.2, 0.5) * 0.25, 0.6)
    # 마무리 : 둥, 그리고 두 번째 줄에서 화음
    x = np.arange(int(1.5 * SR)) / SR
    add(s[10] + 0.2, np.sin(2 * np.pi * 55 * x) * np.exp(-x * 1.5), 0.7)
    add(s[10] + 1.4, boom(1.0), 0.6)
    add(s[10] + 1.4, tone(392, 2.5, 1.0) + tone(587, 2.5, 1.0) + tone(784, 2.5, 0.8), 0.22)

    out = out / max(1e-6, np.abs(out).max()) * 0.88
    out[-int(0.8 * SR):] *= np.linspace(1, 0, int(0.8 * SR))
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((out * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- 조립
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out",
                                                  "meai_home_30s_v2.mp4"))
    args = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    tmp = tempfile.mkdtemp()
    P = grab(args.src, tmp)
    scenes = build_scenes(P)
    wav = os.path.join(tmp, "sfx.wav")
    make_audio(wav, scenes)
    enc = subprocess.Popen(
        [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
         "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", args.out],
        stdin=subprocess.PIPE)
    prev = None
    for si, (fn, d) in enumerate(scenes):
        for i in range(int(round(d * FPS))):
            t = i / FPS
            im = fn(t, d)
            if prev is not None and si not in (1, 9, 10) and t < 0.12:   # 짧은 휙 전환(잔상)
                im = Image.blend(prev, im, 0.4 + 0.6 * t / 0.12)
            enc.stdin.write(im.tobytes())
        prev = im
        print("  장면 %2d  %.1f초" % (si + 1, d))
    enc.stdin.close()
    enc.wait()
    print("완성 :", os.path.abspath(args.out))


if __name__ == "__main__":
    main()
