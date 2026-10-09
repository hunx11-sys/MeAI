# -*- coding: utf-8 -*-
"""MeAI홈 오픈 30초 영상 조립기.

Higgsfield 에서 받은 장면 영상(clips/ 폴더)을 시간표대로 자르고 이어 붙인 뒤,
한글 문구·화면 그래픽·워터마크·효과음을 영상 위에 따로 얹어 MP4 하나로 만든다.
AI 가 글자를 그리지 않게 하려고 글자는 전부 여기서 그린다.

clips/ 에 없는 장면은 이 파일이 그린 임시 그림으로 채운다(미리보기).
  python build_video.py                 -> out/meai_home_30s.mp4
  python build_video.py --out a.mp4     -> 다른 이름으로
"""
import argparse
import math
import os
import random
import shutil
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, "clips")
FONT_DIR = os.path.join(HERE, "..", "..", "proposal_smart", "ga_assets")

W, H, FPS, TOTAL = 1920, 1080, 30, 30.0
RED = (232, 38, 45)
DEEP = (12, 18, 34)
WHITE = (255, 255, 255)

# 장면표 : (이름, 시작, 끝, Higgsfield 영상 파일)
SCENES = [
    ("s1", 0.0, 5.0, "s1_office.mp4"),
    ("s2", 5.0, 8.0, "s2_glitch.mp4"),
    ("s3", 8.0, 13.0, "s3_cards.mp4"),
    ("s4", 13.0, 18.0, "s4_bubbles.mp4"),
    ("s5a", 18.0, 19.6, "s5a_graph.mp4"),
    ("s5b", 19.6, 21.2, "s5b_design.mp4"),
    ("s5c", 21.2, 22.8, "s5c_report.mp4"),
    ("s5d", 22.8, 24.0, "s5d_eyes.mp4"),
    ("s6", 24.0, 27.0, "s6_fist.mp4"),
    ("s7", 27.0, 30.0, None),  # 검은 화면 + 마무리 문구(직접 그림)
]

# 화면 속 문구(고객 이름은 가린 가상 예시)
CUSTOMERS = [
    ("김○○", "40대 · 자녀 2", "어린이보험 만기"),
    ("이○○", "30대 · 신혼", "실손 단독 가입"),
    ("박○○", "50대 · 자영업", "암 진단비 부족"),
    ("최○○", "40대 · 맞벌이", "간병 보장 없음"),
    ("정○○", "60대 · 은퇴", "뇌·심 보장 공백"),
    ("강○○", "30대 · 직장인", "보험료 점검"),
    ("조○○", "40대 · 자녀 1", "갱신 도래"),
    ("윤○○", "50대 · 맞벌이", "수술비 보강"),
    ("장○○", "30대 · 임신 중", "태아보험 상담"),
]
TALKS = [
    ("김○○", "자녀분 보험 만기가 다가와요. 성인 보장으로 이어 드릴까요?"),
    ("박○○", "요즘 암 치료비를 생각하면 진단비를 한번 점검해 보세요."),
    ("정○○", "은퇴 후엔 뇌·심 보장 공백부터 먼저 채우셔야 해요."),
]


def font(size, weight="Bold"):
    return ImageFont.truetype(os.path.join(FONT_DIR, "NanumGothic-%s.ttf" % weight), size)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ffmpeg_exe():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg 를 찾지 못했습니다. pip install imageio-ffmpeg 를 먼저 하세요.")


# ---------------------------------------------------------------- Higgsfield 영상 읽기
class Clip:
    """영상 파일을 1920x1080·30fps 로 맞춰(가운데 잘라 채움) 한 장씩 꺼낸다."""

    def __init__(self, path, dur):
        self.n = int(round(dur * FPS))
        vf = "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d" % (W, H, W, H, FPS)
        self.p = subprocess.Popen(
            [ffmpeg_exe(), "-v", "error", "-i", path, "-t", "%.3f" % dur, "-vf", vf,
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE)
        self.last = Image.new("RGB", (W, H), (0, 0, 0))

    def frame(self):
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:  # 영상이 짧으면 마지막 장면을 늘린다
            self.last = Image.frombuffer("RGB", (W, H), buf)
        return self.last.copy()

    def close(self):
        self.p.stdout.close()
        self.p.wait()


# ---------------------------------------------------------------- 공통 그림 조각
def gradient(top, bottom):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - a) + np.array(bottom)[None, None, :] * a)
    return Image.fromarray(np.repeat(arr, W, axis=1).astype(np.uint8))


BG_DARK = None
BG_UI = None


def ui_bg():
    """MeAI홈 화면 바탕(검붉은 그라데이션 + 위쪽 막대)."""
    global BG_UI
    if BG_UI is None:
        im = gradient((26, 8, 12), (8, 8, 14))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, 96], fill=(18, 18, 24))
        d.rectangle([0, 92, W, 96], fill=RED)
        d.text((60, 22), "MeAI", font=font(48, "ExtraBold"), fill=RED)
        d.text((60 + d.textlength("MeAI", font=font(48, "ExtraBold")) + 4, 22), "홈",
               font=font(48, "ExtraBold"), fill=WHITE)
        for i, m in enumerate(["고객추천", "맞춤대화", "보장분석", "자동설계", "리포트"]):
            d.text((560 + i * 210, 34), m, font=font(28), fill=(200, 200, 210))
        BG_UI = im
    return BG_UI.copy()


def text_center(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def placeholder(im, label):
    """Higgsfield 영상이 아직 없을 때 화면 위쪽에 작은 안내를 단다."""
    d = ImageDraw.Draw(im, "RGBA")
    f = font(26)
    w = d.textlength(label, font=f)
    rrect(d, [40, 40, 40 + w + 40, 92], 12, fill=(0, 0, 0, 150))
    d.text((60, 52), label, font=f, fill=(255, 220, 120))


# ---------------------------------------------------------------- 장면별 임시 그림
def s1(t):
    """막막함 : 어두운 푸른 사무실, 빈 고객 명단, 초침."""
    global BG_DARK
    if BG_DARK is None:
        BG_DARK = gradient((22, 34, 62), (6, 10, 22))
    im = BG_DARK.copy()
    d = ImageDraw.Draw(im, "RGBA")
    # 빈 명단
    rrect(d, [560, 220, 1180, 940], 18, fill=(225, 230, 240, 235))
    d.text((610, 260), "고객 명단", font=font(52, "ExtraBold"), fill=(40, 50, 70))
    for i in range(9):
        y = 370 + i * 60
        d.text((612, y - 4), "%d." % (i + 1), font=font(30), fill=(120, 130, 150))
        d.line([660, y + 30, 1130, y + 30], fill=(170, 178, 195), width=2)
    # 시계
    cx, cy, r = 1480, 330, 150
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(235, 238, 245), outline=(60, 70, 90), width=8)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.line([cx + math.sin(a) * (r - 24), cy - math.cos(a) * (r - 24),
                cx + math.sin(a) * (r - 8), cy - math.cos(a) * (r - 8)], fill=(60, 70, 90), width=6)
    d.line([cx, cy, cx + math.sin(-0.5) * 70, cy - math.cos(-0.5) * 70], fill=(40, 40, 50), width=10)
    sec = math.floor(t) + 52  # 1초마다 '똑딱'
    a = sec / 60 * 2 * math.pi
    d.line([cx, cy, cx + math.sin(a) * (r - 30), cy - math.cos(a) * (r - 30)], fill=RED, width=5)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=RED)
    # 천천히 다가가는 느낌
    z = 1 + 0.04 * t / 5
    im = im.resize((int(W * z), int(H * z))).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2),
                                                    int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
    placeholder(im, "① 임시 그림 · Higgsfield 컷(s1_office) 자리")
    return im


def home_screen(t):
    """MeAI홈 첫 화면(지지직 장면 끝에 나타남)."""
    im = ui_bg()
    d = ImageDraw.Draw(im, "RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W / 2 - 520, H / 2 - 300, W / 2 + 520, H / 2 + 300], fill=RED + (110,))
    im.paste(glow.filter(ImageFilter.GaussianBlur(120)), (0, 0), glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(im)
    f = font(190, "ExtraBold")
    wa, wb = d.textlength("MeAI", font=f), d.textlength("홈", font=f)
    x = W / 2 - (wa + wb + 10) / 2
    d.text((x, 380), "MeAI", font=f, fill=RED)
    d.text((x + wa + 10, 380), "홈", font=f, fill=WHITE)
    return im


def glitch(im, amount, seed):
    """화면이 지지직 깨지는 효과(가로 줄 밀림 + 색 번짐 + 잡음)."""
    rnd = random.Random(seed)
    a = np.array(im)
    for _ in range(int(6 + 30 * amount)):
        y = rnd.randrange(0, H - 10)
        h = rnd.randrange(4, int(10 + 80 * amount))
        a[y:y + h] = np.roll(a[y:y + h], rnd.randrange(-int(200 * amount) - 1, int(200 * amount) + 1), axis=1)
    sh = int(4 + 24 * amount)
    a[:, :, 0] = np.roll(a[:, :, 0], sh, axis=1)
    a[:, :, 2] = np.roll(a[:, :, 2], -sh, axis=1)
    noise = np.random.default_rng(seed).integers(0, 255, (H // 4, W // 4, 1), dtype=np.uint8)
    noise = np.repeat(np.repeat(noise, 4, 0), 4, 1)
    a = (a * (1 - 0.35 * amount) + noise * 0.35 * amount).astype(np.uint8)
    return Image.fromarray(a)


def s2(t, base):
    """지지직 : 0~2초 깨짐이 커지고, 2초부터 빨간 빛과 함께 MeAI홈."""
    if t < 1.8:
        im = glitch(base, ease(t / 1.8), int(t * FPS))
        red = Image.new("RGB", (W, H), RED)
        im = Image.blend(im, red, 0.25 * ease(t / 1.8))
    else:
        k = (t - 1.8) / 1.2
        im = home_screen(t)
        if k < 0.35:
            im = glitch(im, 1 - k / 0.35, int(t * FPS))
        flash = Image.new("RGB", (W, H), (255, 230, 230))
        im = Image.blend(im, flash, max(0.0, 0.6 - k * 2))
    return im


def card(d, x, y, w, h, c, alpha=255):
    rrect(d, [x, y, x + w, y + h], 16, fill=(32, 32, 42, alpha), outline=RED + (alpha,), width=3)
    d.ellipse([x + 24, y + 28, x + 104, y + 108], fill=(70, 70, 86, alpha))
    d.text((x + 52, y + 46), c[0][0], font=font(36, "ExtraBold"), fill=(255, 255, 255, alpha))
    d.text((x + 124, y + 32), c[0] + " 고객", font=font(40, "ExtraBold"), fill=(255, 255, 255, alpha))
    d.text((x + 124, y + 84), c[1], font=font(28), fill=(190, 190, 205, alpha))
    rrect(d, [x + 24, y + h - 62, x + 24 + d.textlength(c[2], font=font(26)) + 32, y + h - 20], 20,
          fill=RED + (alpha,))
    d.text((x + 40, y + h - 56), c[2], font=font(26), fill=(255, 255, 255, alpha))


def s3(t):
    """고객추천 : 카드가 쏟아지다 3x3 으로 착착 정렬."""
    im = ui_bg()
    d = ImageDraw.Draw(im, "RGBA")
    text_center(d, W / 2, 130, "이번 달 추천 고객 9명", font(64, "ExtraBold"), WHITE)
    cw, ch, gx, gy = 520, 210, 40, 30
    ox, oy = (W - (cw * 3 + gx * 2)) / 2, 250
    rnd = random.Random(7)
    for i, c in enumerate(CUSTOMERS):
        tx, ty = ox + (i % 3) * (cw + gx), oy + (i // 3) * (ch + gy)
        sx, sy = rnd.uniform(-200, W), rnd.uniform(-900, -300)
        rot0 = rnd.uniform(-30, 30)
        k = ease((t - 0.15 * i) / 1.6)
        if k <= 0:
            continue
        x, y = sx + (tx - sx) * k, sy + (ty - sy) * k
        layer = Image.new("RGBA", (cw + 8, ch + 8), (0, 0, 0, 0))
        card(ImageDraw.Draw(layer), 4, 4, cw, ch, c)
        rot = rot0 * (1 - k)
        if abs(rot) > 0.3:
            layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.paste(layer, (int(x), int(y)), layer)
    # 정렬 끝나면 위에서 아래로 빛줄기
    if t > 3.2:
        y = 250 + (t - 3.2) / 1.2 * 760
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle([ox - 20, y, ox + cw * 3 + gx * 2 + 20, y + 6], fill=RED + (160,))
    return im


def s4(t):
    """맞춤대화 : 고객별로 말풍선이 생기며 대화 문장이 타자 치듯 나타난다."""
    im = ui_bg()
    d = ImageDraw.Draw(im, "RGBA")
    text_center(d, W / 2, 130, "이 고객에게는 이렇게 말하세요", font(60, "ExtraBold"), WHITE)
    for i, (name, line) in enumerate(TALKS):
        t0 = 0.3 + i * 1.4
        k = ease((t - t0) / 0.5)
        if k <= 0:
            continue
        y = 270 + i * 250
        a = int(255 * k)
        d.ellipse([200, y + 20, 330, y + 150], fill=(70, 70, 86, a))
        text_center(d, 265, y + 58, name[0], font(48, "ExtraBold"), (255, 255, 255, a))
        text_center(d, 265, y + 165, name + " 고객", font(28), (200, 200, 210, a))
        bx = 380 + (1 - k) * 60
        rrect(d, [bx, y, bx + 1340, y + 170], 34, fill=(255, 255, 255, a))
        d.polygon([(bx, y + 70), (bx - 34, y + 92), (bx + 4, y + 108)], fill=(255, 255, 255, a))
        n = int(len(line) * min(1.0, max(0.0, (t - t0 - 0.2) / 1.0)))
        d.text((bx + 50, y + 58), line[:n], font=font(44, "ExtraBold"), fill=(30, 30, 40, a))
        d.text((bx + 50, y + 16), "추천 대화", font=font(24), fill=RED + (a,))
    return im


def s5a(t):
    """보장분석 : 보장 막대가 차오른다."""
    im = ui_bg()
    d = ImageDraw.Draw(im, "RGBA")
    text_center(d, W / 2, 130, "보장분석", font(60, "ExtraBold"), WHITE)
    items = [("암", 0.9), ("뇌혈관", 0.75), ("심장", 0.8), ("수술", 0.65), ("입원", 0.7), ("간병", 0.85)]
    for i, (n, v) in enumerate(items):
        x = 300 + i * 230
        k = ease((t - 0.08 * i) / 1.0)
        rrect(d, [x, 300, x + 120, 900], 14, fill=(50, 50, 62))
        top = 900 - 600 * v * k
        rrect(d, [x, top, x + 120, 900], 14, fill=RED)
        text_center(d, x + 60, 925, n, font(34, "ExtraBold"), WHITE)
        text_center(d, x + 60, top - 52, "%d%%" % round(100 * v * k), font(32), (255, 210, 210))
    return im


def s5b(t):
    """자동설계 : 설계안 블록이 착착 쌓인다."""
    im = ui_bg()
    d = ImageDraw.Draw(im, "RGBA")
    text_center(d, W / 2, 130, "자동설계", font(60, "ExtraBold"), WHITE)
    rows = ["암 진단비 보강", "뇌·심 진단비 추가", "수술비 보장 확대", "간병인 지원 추가"]
    for i, r in enumerate(rows):
        k = ease((t - 0.22 * i) / 0.45)
        if k <= 0:
            continue
        y = 270 + i * 160 - (1 - k) * 120
        a = int(255 * k)
        rrect(d, [460, y, 1460, y + 130], 20, fill=(36, 36, 46, a), outline=RED + (a,), width=3)
        d.text((520, y + 40), r, font=font(46, "ExtraBold"), fill=(255, 255, 255, a))
        if k > 0.9:
            d.ellipse([1340, y + 33, 1404, y + 97], fill=RED)
            d.line([1356, y + 66, 1368, y + 80, 1390, y + 50], fill=WHITE, width=8)
    return im


def s5c(t):
    """리포트 : 리포트가 프린터처럼 출력된다."""
    im = ui_bg()
    d = ImageDraw.Draw(im, "RGBA")
    text_center(d, W / 2, 130, "리포트", font(60, "ExtraBold"), WHITE)
    rrect(d, [560, 240, 1360, 320], 24, fill=(60, 60, 72))
    k = ease(t / 1.3)
    h = 680 * k
    d.rectangle([620, 290, 1300, 290 + h], fill=(250, 250, 250))
    lines = ["고객 맞춤 보장 리포트", "", "■ 보장 현황", "■ 부족한 보장", "■ 추천 설계안", "■ 예상 보험금"]
    for i, s in enumerate(lines):
        y = 330 + i * 80
        if y + 50 < 290 + h and s:
            d.text((680, y), s, font=font(44 if i == 0 else 38, "ExtraBold"),
                   fill=RED if i == 0 else (50, 50, 60))
    return im


def s5d(t):
    """눈이 커진다 : Higgsfield 컷 자리(임시로 빨간 빛이 번지는 화면)."""
    im = gradient((40, 10, 16), (8, 6, 12))
    d = ImageDraw.Draw(im, "RGBA")
    r = 200 + 500 * ease(t / 1.2)
    d.ellipse([W / 2 - r, H / 2 - r * 0.5, W / 2 + r, H / 2 + r * 0.5], outline=RED + (200,), width=10)
    d.ellipse([W / 2 - 90, H / 2 - 90, W / 2 + 90, H / 2 + 90], fill=(20, 20, 26), outline=WHITE, width=8)
    placeholder(im, "⑤ 임시 그림 · Higgsfield 컷(s5d_eyes) 자리")
    return im


def s6(t):
    """결심 : Higgsfield 컷 자리(임시로 빨간 집중선)."""
    im = gradient((90, 12, 20), (20, 4, 8))
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(int(t * 10))
    for k in range(60):
        a = rnd.uniform(0, 2 * math.pi)
        d.line([W / 2 + math.cos(a) * 380, H / 2 + math.sin(a) * 260,
                W / 2 + math.cos(a) * 1400, H / 2 + math.sin(a) * 1000], fill=(255, 255, 255, 60), width=4)
    placeholder(im, "⑥ 임시 그림 · Higgsfield 컷(s6_fist) 자리")
    return im


FALLBACK = {"s1": s1, "s3": s3, "s4": s4, "s5a": s5a, "s5b": s5b, "s5c": s5c, "s5d": s5d, "s6": s6}


# ---------------------------------------------------------------- 영상 위에 얹는 글자
def overlay(im, T):
    d = ImageDraw.Draw(im, "RGBA")
    # 24~27초 「이제는 MeAI야!」(톡 튀어나오는 크기)
    if 24.6 <= T < 27.0:
        k = ease((T - 24.6) / 0.25)
        s = "이제는 MeAI야!"
        f = font(int(150 * (0.6 + 0.4 * k)), "ExtraBold")
        w = d.textlength(s, font=f)
        x, y = (W - w) / 2, H - 360 - f.size / 2
        for dx, dy in [(-6, 0), (6, 0), (0, -6), (0, 6), (-5, -5), (5, 5), (-5, 5), (5, -5)]:
            d.text((x + dx, y + dy), s, font=f, fill=(0, 0, 0, int(220 * k)))
        d.text((x, y), s, font=f, fill=(255, 255, 255, int(255 * k)))
    # 27~30초 마무리 두 줄
    if T >= 27.0:
        k1 = ease((T - 27.3) / 0.6)
        k2 = ease((T - 28.4) / 0.6)
        text_center(d, W / 2, 390 - 10 * (1 - k1), "찾는 영업에 작별을 고하다", font(84, "ExtraBold"),
                    (255, 255, 255, int(255 * k1)))
        text_center(d, W / 2, 540 - 10 * (1 - k2), "찾아가는 영업, MeAI홈으로", font(96, "ExtraBold"),
                    RED + (int(255 * k2),))
    # 영상 내내 워터마크
    f = font(30)
    s = "세일즈혁신TF"
    d.text((W - 60 - d.textlength(s, font=f), H - 70), s, font=f, fill=(255, 255, 255, 150))
    return im


# ---------------------------------------------------------------- 효과음(직접 합성 · 저작권 걱정 없음)
SR = 44100


def make_audio(path):
    n = int(SR * TOTAL)
    out = np.zeros(n)
    tt = np.arange(n) / SR
    rng = np.random.default_rng(1)

    def add(at, sig, gain=1.0):
        i = int(at * SR)
        j = min(n, i + len(sig))
        out[i:j] += sig[:j - i] * gain

    def env(d, att=0.002, dec=None):
        m = int(d * SR)
        e = np.exp(-np.arange(m) / SR / (dec or d / 4))
        a = int(att * SR)
        e[:a] *= np.linspace(0, 1, a)
        return e

    def tone(f, d, dec=None):
        x = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * f * x) * env(d, dec=dec)

    def noise(d, dec=None):
        return rng.uniform(-1, 1, int(d * SR)) * env(d, dec=dec)

    # 0~5초 초침 똑딱
    for s in range(5):
        add(s + 0.05, tone(2400, 0.05, 0.008) + noise(0.05, 0.004) * 0.5, 0.5)
        add(s + 0.55, tone(1900, 0.05, 0.008) + noise(0.05, 0.004) * 0.5, 0.35)
    # 5~7초 지지직
    m = int(2.0 * SR)
    st = rng.uniform(-1, 1, m) * (rng.uniform(0, 1, m // 400 + 1).repeat(400)[:m] > 0.35)
    add(5.0, st * np.linspace(0.2, 1, m), 0.35)
    # 6.8초 빨간 빛 '쿵' + 반짝
    x = np.arange(int(1.2 * SR)) / SR
    add(6.8, np.sin(2 * np.pi * (90 - 50 * x) * x) * np.exp(-x * 3), 0.9)
    add(6.8, tone(1320, 1.0, 0.3) * 0.25 + tone(1980, 1.0, 0.25) * 0.15)
    # 8~24초 박자(분당 120)
    for b in np.arange(8.0, 24.0, 0.5):
        add(b, np.sin(2 * np.pi * (110 - 60 * x[:int(0.25 * SR)]) * x[:int(0.25 * SR)])
            * np.exp(-x[:int(0.25 * SR)] * 18), 0.45)
        add(b + 0.25, noise(0.06, 0.012), 0.08)
    # 카드 착지 '톡'
    for i in range(9):
        add(8.0 + 0.15 * i + 1.55, tone(880 + 60 * i, 0.08, 0.02), 0.25)
    # 말풍선 '뽁'
    for i in range(3):
        add(13.0 + 0.3 + i * 1.4, tone(660, 0.15, 0.04) + tone(990, 0.15, 0.03), 0.3)
    # 빠른 전환 '휙'
    for at in (8.0, 13.0, 18.0, 19.6, 21.2):
        w = rng.uniform(-1, 1, int(0.35 * SR))
        w = np.convolve(w, np.ones(12) / 12, "same") * np.sin(np.linspace(0, np.pi, len(w)))
        add(at - 0.15, w, 0.5)
    # 눈이 커질 때 '띵'
    add(22.8, tone(1568, 1.0, 0.3), 0.3)
    # 24초 일어날 때 '쾅' / 27초 '둥'
    add(24.0, np.sin(2 * np.pi * (70 - 30 * x) * x) * np.exp(-x * 2.5) + noise(1.2, 0.08) * 0.3, 1.0)
    add(24.6, tone(523, 0.6, 0.2) + tone(784, 0.6, 0.2), 0.25)
    add(27.3, np.sin(2 * np.pi * 55 * x) * np.exp(-x * 1.5), 0.6)
    add(28.4, tone(392, 1.5, 0.6) + tone(587, 1.5, 0.6) + tone(784, 1.5, 0.5), 0.2)

    out = out / max(1e-6, np.abs(out).max()) * 0.85
    out[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((out * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- 조립
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "out", "meai_home_30s.mp4"))
    ap.add_argument("--clips", default=CLIPS)
    args = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    wav = os.path.splitext(args.out)[0] + "_sfx.wav"
    make_audio(wav)

    enc = subprocess.Popen(
        [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
         "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
         args.out],
        stdin=subprocess.PIPE)

    used = []
    prev = None  # 앞 장면 마지막 그림(지지직 장면 바탕)
    for name, a, b, fn in SCENES:
        path = os.path.join(args.clips, fn) if fn else None
        clip = Clip(path, b - a) if path and os.path.exists(path) else None
        if clip:
            used.append(fn)
        n = int(round((b - a) * FPS))
        for i in range(n):
            t = i / FPS
            T = a + t
            if name == "s7":
                im = Image.new("RGB", (W, H), (0, 0, 0))
            elif name == "s2":
                base = clip.frame() if clip else (prev or s1(4.99))
                im = s2(t, base)
            elif clip:
                im = clip.frame()
                if name == "s1":  # 어둡고 푸른 톤으로 살짝 맞춘다
                    im = Image.blend(im, Image.new("RGB", (W, H), DEEP), 0.18)
            else:
                im = FALLBACK[name](t)
            if 0.0 < T < 0.4:  # 처음 검은 화면에서 밝아지기
                im = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), im, T / 0.4)
            im = overlay(im.convert("RGB"), T)
            prev = im if name == "s1" else prev
            enc.stdin.write(im.tobytes())
        if clip:
            clip.close()
        print("  %-4s %4.1f~%4.1f초  %s" % (name, a, b, fn if clip else ("직접 그림" if not fn else "임시 그림")))

    enc.stdin.close()
    enc.wait()
    os.remove(wav)
    print("완성 :", os.path.abspath(args.out))
    print("Higgsfield 영상 사용 %d개 / 임시 그림 %d개" % (len(used), sum(1 for s in SCENES if s[3]) - len(used)))


if __name__ == "__main__":
    main()
