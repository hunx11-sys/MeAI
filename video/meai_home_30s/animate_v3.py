# -*- coding: utf-8 -*-
"""MeAI홈 오픈 30초 영상 v3 : 실제 MeAI 화면 캡처 + 나레이션 자막판.

- 캐릭터 장면(막막함·지지직·눈·결심)은 Canva 완성본에서 뽑은 그림을 쓴다.
- 화면 장면(영업포탈 → MeAI 홈 → 추천 고객 → 맞춤대화 → 보장분석 → 설계 → 리포트)은
  저장소의 실제 캡처(guidebook_v4/captures, 개인정보 가림 처리본)를 직접 얹어 카메라를 움직인다.
- 화면 장면 아래에는 캐릭터 말풍선 대신 짧은 나레이션 자막만 넣는다. '[글자]'는 빨간 강조.

  python animate_v3.py <Canva에서 받은 mp4> [--out 결과.mp4]
"""
import argparse
import math
import os
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from animate_v2 import (FPS, H, HERE_FONTS, RED, SR, W, back, bubble, cam, ease, flash, glitch, grab, rich,
                        shake, speed_lines)
from build_video import ffmpeg_exe

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CAP = os.path.join(ROOT, "guidebook_v4", "captures")


def pf(size, weight="Bold"):
    return ImageFont.truetype(os.path.join(HERE_FONTS, "Pretendard-%s.otf" % weight), size)


def load(rel):
    return Image.open(os.path.join(CAP, rel)).convert("RGB")


def stack(a, b):
    w = max(a.width, b.width)
    out = Image.new("RGB", (w, a.height + b.height), (255, 255, 255))
    out.paste(a, (0, 0))
    out.paste(b, (0, a.height))
    return out


# ---------------------------------------------------------------- 바탕·글자
_BG = None


def bg():
    global _BG
    if _BG is None:
        y = np.linspace(0, 1, H)[:, None, None]
        top, bot = np.array([26, 9, 13]), np.array([8, 8, 12])
        arr = np.repeat((top * (1 - y) + bot * y), W, axis=1).astype(np.uint8)
        im = Image.fromarray(arr)
        glow = Image.new("L", (W, H), 0)
        ImageDraw.Draw(glow).ellipse([-200, 300, W + 200, 1500], fill=70)
        glow = glow.filter(ImageFilter.GaussianBlur(160))
        im = Image.composite(Image.new("RGB", (W, H), (120, 14, 22)), im, glow)
        _BG = im
    return _BG.copy()


def watermark(im):
    d = ImageDraw.Draw(im, "RGBA")
    f = pf(30, "SemiBold")
    s = "세일즈혁신TF"
    d.text((W - 54 - d.textlength(s, font=f), H - 74), s, font=f, fill=(255, 255, 255, 150))
    return im


def draw_rich(d, cx, y, text, f, fg, hot, alpha=255, lh=1.32, shadow=True):
    rows = rich(text)
    for i, segs in enumerate(rows):
        tw = sum(d.textlength(s, font=f) for s, _ in segs)
        x = cx - tw / 2
        yy = y + i * f.size * lh
        for s, is_hot in segs:
            if shadow:
                d.text((x + 3, yy + 4), s, font=f, fill=(0, 0, 0, int(alpha * 0.55)))
            d.text((x, yy), s, font=f, fill=(hot if is_hot else fg) + (alpha,))
            x += d.textlength(s, font=f)


def title(im, t, step, text):
    """맨 위 : 빨간 단계 표시 + 큰 제목. 처음 0.3초 동안 살짝 내려오며 나타난다."""
    k = ease(t / 0.3)
    a = int(255 * k)
    d = ImageDraw.Draw(im, "RGBA")
    dy = -20 * (1 - k)
    if step:
        f = pf(32, "Bold")
        tw = d.textlength(step, font=f)
        d.rounded_rectangle([W / 2 - tw / 2 - 22, 118 + dy, W / 2 + tw / 2 + 22, 166 + dy], 24, fill=RED + (a,))
        d.text((W / 2 - tw / 2, 122 + dy), step, font=f, fill=(255, 255, 255, a))
    draw_rich(d, W / 2, 190 + dy, text, pf(80, "ExtraBold"), (255, 255, 255), RED, a, shadow=False)
    return im


def narration(im, t, text, t0=0.35, y=1560):
    """화면 아래 나레이션 자막 : 아래에서 살짝 떠오르며 나타난다."""
    if t < t0:
        return im
    k = ease((t - t0) / 0.35)
    d = ImageDraw.Draw(im, "RGBA")
    f = pf(54, "SemiBold")
    rows = len(rich(text))
    top = y - (rows * f.size * 1.32) / 2 + 24 * (1 - k)
    # 자막 위 가는 빨간 줄
    lw = 90 * k
    d.rounded_rectangle([W / 2 - lw / 2, top - 34, W / 2 + lw / 2, top - 28], 3, fill=RED + (int(255 * k),))
    draw_rich(d, W / 2, top, text, f, (255, 255, 255), (255, 92, 98), int(255 * k))
    return im


# ---------------------------------------------------------------- 캡처 카드(둥근 모서리 + 그림자 + 카메라)
def card(im, src, box, zoom, fx, fy, radius=26):
    """src 를 box=(x,y,w,h) 창에 보여 준다. zoom 1 = 폭 맞춤. (fx,fy)=보고 싶은 지점(0~1).
    돌려주는 map(sx,sy) 은 원본 좌표를 화면 좌표로 바꾼다."""
    x, y, w, h = box
    zmin = (h / w) * src.width / src.height      # 창 높이를 다 채우는 최소 배율
    z = max(zoom, zmin)
    vw = src.width / z
    vh = vw * h / w
    cx = min(max(fx * src.width, vw / 2), src.width - vw / 2)
    cy = min(max(fy * src.height, vh / 2), src.height - vh / 2)
    sx0, sy0 = cx - vw / 2, cy - vh / 2
    view = src.crop((int(sx0), int(sy0), int(sx0 + vw), int(sy0 + vh))).resize((w, h), Image.BICUBIC)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    sh = Image.new("L", (w + 80, h + 80), 0)
    ImageDraw.Draw(sh).rounded_rectangle([40, 52, w + 40, h + 52], radius, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    im.paste(Image.new("RGB", sh.size, (0, 0, 0)), (x - 40, y - 40), sh)
    im.paste(view, (x, y), m)

    def mp(px, py):
        return x + (px - sx0) * w / vw, y + (py - sy0) * h / vh
    return im, mp


def cursor(im, x, y, press=0.0):
    """마우스 화살표. press(0~1)만큼 눌린 모양(살짝 작아짐)."""
    s = 1.0 - 0.15 * press
    pts = [(0, 0), (0, 58), (15, 45), (26, 70), (37, 65), (26, 41), (46, 41)]
    pts = [(x + px * s * 1.2, y + py * s * 1.2) for px, py in pts]
    d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(px + 4, py + 6) for px, py in pts], fill=(0, 0, 0, 110))
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(20, 20, 26, 255), width=4)
    return im


def ripple(im, x, y, k):
    if not 0 < k < 1:
        return im
    d = ImageDraw.Draw(im, "RGBA")
    r = 20 + 110 * ease(k)
    d.ellipse([x - r, y - r, x + r, y + r], outline=RED + (int(255 * (1 - k)),), width=8)
    return im


def ring(im, x0, y0, x1, y1, t):
    """눌러 볼 단추 둘레에 숨 쉬듯 깜빡이는 빨간 테."""
    d = ImageDraw.Draw(im, "RGBA")
    p = 0.5 + 0.5 * math.sin(t * 10)
    pad = 10 + 8 * p
    d.rounded_rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], 22, outline=RED + (int(150 + 105 * p),), width=7)
    return im


# ---------------------------------------------------------------- 장면
def build(P):
    C = {
        "portal": load("hero/bc2_portal_masked.png"),
        "banner": load("hero/portal_entry_banner.png"),
        "home": load("hero/bc2_gate_full_s3_masked.png"),
        "reco": load("hero/gb5_gate_reco3_m.png"),
        "entry": load("hero/bc3_home_cards.png"),
        "custom": load("real/r06_custom_start.png"),
        "answer": stack(load("hero/bc2_answer_top.png"), load("hero/bc2_answer_bottom.png")),
        "design": load("real/r09_custom_precontract.png"),
        "report": load("real/r11_report_edit.png"),
    }

    def s_despair(t, d):
        dx, dy = shake(t, 3)
        im = cam(P[0], 1.0 + 0.10 * t / d, 0.5, 0.45, dx, dy)
        return bubble(im, 0.4, t, "이번 달 누구에게 영업하지…\n할 사람 다 한 것 같은데", (50, 170, 720, 250),
                      (560, 700), "think", 48)

    def s_portal(t, d):
        im = bg()
        im = title(im, t, "", "영업포탈")
        k = ease(t / d)
        im, _ = card(im, C["portal"], (40, 560, 1000, 560), 1.03 + 1.7 * k, 0.5 - 0.02 * k, 0.5 - 0.27 * k)
        im = narration(im, t, "늘 쓰던 영업포탈 첫 화면에서", 0.25, 1400)
        return watermark(im)

    def s_click(t, d):
        im = bg()
        im = title(im, t, "", "영업포탈")
        z = 1.9 + 0.35 * ease(t / d)
        im, mp = card(im, C["banner"], (40, 520, 1000, 560), z, 0.30, 0.62)
        bx0, by0 = mp(190, 300)
        bx1, by1 = mp(535, 356)
        tx, ty = (bx0 + bx1) / 2, (by0 + by1) / 2
        if t > 0.95:
            im = ring(im, bx0, by0, bx1, by1, t)
        mk = ease((t - 0.25) / 0.6)
        cx, cy = 980 + (tx - 980) * mk, 1350 + (ty - 1350) * mk
        press = 1.0 if 0.9 < t < 1.05 else 0.0
        im = ripple(im, tx, ty, (t - 0.92) / 0.45)
        im = cursor(im, cx, cy, press)
        im = narration(im, t, "[MeAI 홈 바로가기] 한 번이면", 0.2, 1400)
        im = flash(im, (t - 1.25) * 3.5, (255, 70, 70)) if t > 1.25 else im
        return watermark(im)

    def s_glitch(t, d):
        dx, dy = shake(t, 22, seed=2)
        im = cam(P[1], 1.06, 0.5, 0.5, dx, dy)
        if t < 0.8:
            im = glitch(im, 0.8 - t, int(t * FPS))
        im = flash(im, 0.55 - t * 1.2, (255, 60, 60))
        return bubble(im, 0.2, t, "뭐, 뭐야?!", (90, 170, 560, 220), (420, 620), "shout", 76)

    def s_home(t, d):
        im = bg()
        k = back(min(1.0, t / 0.4))
        d_ = ImageDraw.Draw(im, "RGBA")
        f = pf(int(190 * (0.7 + 0.3 * k)), "Black")
        wa, wb = d_.textlength("MeAI", font=f), d_.textlength("홈", font=f)
        x0 = W / 2 - (wa + wb + 12) / 2
        yy = 250 - f.size / 2
        d_.text((x0, yy), "MeAI", font=f, fill=(255, 255, 255))
        d_.text((x0 + wa + 12, yy), "홈", font=f, fill=RED)
        im, _ = card(im, C["home"], (40, 470, 1000, 960), 1.1 + 0.12 * ease(t / d), 0.5, 0.18 + 0.1 * ease(t / d))
        im = narration(im, t, "[MeAI 홈]이 열립니다", 0.5, 1590)
        im = flash(im, 1.0 - t * 3)
        return watermark(im)

    def s_reco(t, d):
        im = title(bg(), t, "STEP 01", "오늘의 추천 고객")
        k = ease(t / d)
        im, _ = card(im, C["reco"], (40, 440, 1000, 760), 1.6 + 0.4 * k, 0.22 + 0.56 * k, 0.5)
        im = narration(im, t, "매일 아침, MeAI가\n[연락할 고객]을 먼저 골라 줍니다", 0.4, 1520)
        return watermark(im)

    def s_custom(t, d):
        im = title(bg(), t, "STEP 02", "맞춤대화")
        ke = ease(t / 0.4)
        im, _ = card(im, C["entry"], (40, int(440 - 30 * (1 - ke)), 1000, 250), 1.2, 0.5, 0.5)
        k = ease((t - 0.3) / 0.45)
        if k > 0:
            im, mp = card(im, C["custom"], (40, int(760 + 80 * (1 - k)), 1000, 640),
                          1.6 + 0.35 * ease((t - 0.8) / 1.6), 0.6, 0.62)
        im = narration(im, t, "고객과 계약만 고르면\n바로 [맞춤대화] 시작", 0.6, 1600)
        return watermark(im)

    def s_answer(t, d):
        im = title(bg(), t, "STEP 03", "AI 보장분석")
        k = ease(t / d)
        im, _ = card(im, C["answer"], (40, 430, 1000, 1000), 1.12 + 0.18 * k, 0.5, 0.18 + 0.66 * k)
        im = narration(im, t, "가입한 보험을 정리하고\n[부족한 보장]을 한눈에 요약", 0.4, 1600)
        return watermark(im)

    def s_design(t, d):
        im = title(bg(), t, "STEP 04", "AI 설계")
        k = ease(t / 1.3)
        im, mp = card(im, C["design"], (40, 430, 1000, 960), 1.5 + 0.1 * k, 0.6 + 0.06 * k, 0.25 + 0.55 * k)
        if t > 1.1:
            x0, y0 = mp(1197, 735)
            x1, y1 = mp(1277, 779)
            im = ring(im, x0, y0, x1, y1, t)
        im = narration(im, t, "보완 설계안부터\n[가계약 생성]까지", 0.35, 1600)
        return watermark(im)

    def s_report(t, d):
        im = title(bg(), t, "STEP 05", "AI 리포트")
        k = ease(t / d)
        im, _ = card(im, C["report"], (40, 430, 1000, 960), 1.5 + 0.2 * k, 0.55, 0.3 + 0.3 * k)
        im = narration(im, t, "고객에게 드릴 [리포트]도\nPDF·Word로 바로", 0.35, 1600)
        return watermark(im)

    def s_eyes(t, d):
        im = cam(P[8], 1.0 + 0.35 * ease(t / 0.6), 0.5, 0.36)
        im = speed_lines(im, t, 110)
        im = flash(im, 0.6 - t * 2)
        return bubble(im, 0.2, t, "와…!", (640, 1420, 340, 190), (560, 1250), "shout", 80)

    def s_fist(t, d):
        dx, dy = shake(t, 26 * max(0.0, 1 - t / 0.5), seed=7)
        im = cam(P[9], 1.18 - 0.18 * ease(t / 0.35), 0.5, 0.55, dx, dy)
        im = speed_lines(im, t, 70 if t < 1.2 else 40, 9)
        im = flash(im, 0.8 - t * 2.5, (255, 220, 220))
        # 그림 속 옛 문구 띠를 진한 띠로 덮고 새 문구를 쾅 얹는다
        band = Image.new("L", (W, H), 0)
        ImageDraw.Draw(band).rectangle([0, 1385, W, 1715], fill=238)
        band = band.filter(ImageFilter.GaussianBlur(14))
        im = Image.composite(Image.new("RGB", (W, H), (12, 6, 9)), im, band)
        if t > 0.3:
            k = min(1.0, (t - 0.3) / 0.22)
            sc = 1.0 + 1.2 * (1 - ease(k))
            lay = Image.new("RGBA", (W, 360), (0, 0, 0, 0))
            draw_rich(ImageDraw.Draw(lay), W / 2, 40, "[MeAI]에서 고객추천부터\n분석, 설계까지 한번에!",
                      pf(84, "Black"), (255, 255, 255), (255, 70, 78), int(255 * min(1.0, k * 1.6)), lh=1.3)
            if sc > 1.001:
                lay = lay.resize((int(W * sc), int(360 * sc)), Image.BILINEAR)
            im = im.convert("RGBA")
            im.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(1550 - lay.height / 2)))
            im = im.convert("RGB")
            if 0.52 < t < 0.75:                         # 착지 순간 흔들림
                ex, ey = shake(t, 14, seed=11)
                im = cam(im, 1.02, 0.5 + ex / W, 0.5 + ey / H)
        return im

    def s_finale(t, d):
        im = Image.new("RGB", (W, H), (0, 0, 0))
        glow = Image.new("L", (W, H), 0)
        ImageDraw.Draw(glow).ellipse([-100, 560, W + 100, 1400], fill=int(90 * ease((t - 0.55) / 0.4)))
        im = Image.composite(Image.new("RGB", (W, H), (110, 12, 20)), im, glow.filter(ImageFilter.GaussianBlur(150)))
        d_ = ImageDraw.Draw(im, "RGBA")
        k1 = ease((t - 0.05) / 0.4)
        if k1 > 0:
            draw_rich(d_, W / 2, 760 - 18 * (1 - k1), "더 나은 세일즈를 위해,", pf(66, "SemiBold"), (235, 235, 240),
                      RED, int(255 * k1), shadow=False)
        if t > 0.55:                                    # '세일즈혁신TF'가 화면 밖에서 쿵 날아와 박힌다
            k = min(1.0, (t - 0.55) / 0.2)
            sc = 1.0 + 3.0 * (1 - ease(k)) ** 2
            f = pf(150, "Black")
            lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
            dl = ImageDraw.Draw(lay)
            tw = dl.textlength("세일즈혁신", font=f)
            tw2 = dl.textlength("TF", font=f)
            x0 = W / 2 - (tw + tw2 + 14) / 2
            a = int(255 * min(1.0, k * 1.5))
            dl.text((x0, 40), "세일즈혁신", font=f, fill=(255, 255, 255, a))
            dl.text((x0 + tw + 14, 40), "TF", font=f, fill=RED + (a,))
            if sc > 1.001:
                lay = lay.resize((int(W * sc), int(260 * sc)), Image.BILINEAR)
            im = im.convert("RGBA")
            ex, ey = shake(t, 30 * max(0.0, 1 - (t - 0.75) / 0.45), seed=13) if t > 0.75 else (0, 0)
            im.alpha_composite(lay, (int(W / 2 - lay.width / 2 + ex), int(980 - lay.height / 2 + ey)))
            im = im.convert("RGB")
            if t > 0.75:                                # 착지 : 번쩍 + 빨간 밑줄이 쓱
                im = flash(im, 0.7 - (t - 0.75) * 3)
                u = ease((t - 0.8) / 0.35)
                dd = ImageDraw.Draw(im)
                dd.rectangle([W / 2 - 330 * u, 1145, W / 2 + 330 * u, 1153], fill=RED)
        return im

    def s_end(t, d):
        im = Image.new("RGB", (W, H), (0, 0, 0))
        dd = ImageDraw.Draw(im, "RGBA")
        k1 = ease((t - 0.2) / 0.6)
        k2 = ease((t - 1.3) / 0.5)
        if k1 > 0:
            draw_rich(dd, W / 2, 640 - 20 * (1 - k1), "찾는 영업에\n작별을 고하다", pf(96, "Bold"), (255, 255, 255), RED,
                      int(255 * k1), lh=1.28, shadow=False)
        if k2 > 0:
            sc = 1.0 + 0.08 * (1 - back(min(1.0, (t - 1.3) / 0.4)))
            f = pf(int(110 * sc), "Black")
            draw_rich(dd, W / 2, 1010, "찾아가는 영업,\nMeAI홈으로", f, RED, RED, int(255 * k2), lh=1.25, shadow=False)
        return watermark(im)

    return [("despair", s_despair, 2.8), ("portal", s_portal, 1.7), ("click", s_click, 1.5),
            ("glitch", s_glitch, 1.4), ("home", s_home, 2.2), ("reco", s_reco, 2.6), ("custom", s_custom, 2.4),
            ("answer", s_answer, 2.6), ("design", s_design, 1.8), ("report", s_report, 1.8),
            ("eyes", s_eyes, 1.2), ("fist", s_fist, 2.8), ("end", s_end, 2.6), ("finale", s_finale, 2.6)]


# ---------------------------------------------------------------- 효과음
def make_audio(path, scenes):
    total = sum(d for _, _, d in scenes)
    n = int(SR * total)
    out = np.zeros(n)
    rng = np.random.default_rng(5)
    S = {}
    acc = 0.0
    for name, _, d in scenes:
        S[name] = acc
        acc += d

    def add(at, sig, g=1.0):
        i = int(at * SR)
        j = min(n, i + len(sig))
        if 0 <= i < n:
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

    def whoosh(d=0.32):
        w = rng.uniform(-1, 1, int(d * SR))
        return np.convolve(w, np.ones(10) / 10, "same") * np.sin(np.linspace(0, np.pi, len(w))) ** 2

    def boom(d=1.0):
        x = np.arange(int(d * SR)) / SR
        return np.sin(2 * np.pi * (85 - 45 * x) * x) * np.exp(-x * 3) + noise(d, 0.06) * 0.35

    # 막막함 : 초침 + 생각 풍선 + 한숨
    for k in np.arange(0, 3.0, 0.5):
        add(k, tone(2300 if int(k * 2) % 2 == 0 else 1800, 0.05, 0.008) + noise(0.05, 0.004) * 0.5, 0.4)
    add(S["despair"] + 0.4, chirp(300, 600, 0.35, 0.12), 0.22)
    add(S["despair"] + 1.9, np.convolve(rng.uniform(-1, 1, int(0.6 * SR)), np.ones(40) / 40, "same")
        * np.sin(np.linspace(0, np.pi, int(0.6 * SR))), 0.45)
    # 영업포탈 : 휙 + 마우스 이동·딸깍
    add(S["portal"] - 0.15, whoosh(), 0.45)
    add(S["click"] - 0.1, whoosh(0.25), 0.35)
    add(S["click"] + 0.92, noise(0.03, 0.003) + tone(3200, 0.03, 0.006), 0.7)   # 딸깍
    add(S["click"] + 1.0, noise(0.03, 0.003) + tone(2600, 0.03, 0.006), 0.5)
    add(S["click"] + 1.2, chirp(400, 1600, 0.3, 0.2), 0.3)
    # 지지직 + 외침
    m = int(1.0 * SR)
    st = rng.uniform(-1, 1, m) * (rng.uniform(0, 1, m // 300 + 1).repeat(300)[:m] > 0.3)
    add(S["glitch"], st, 0.4)
    add(S["glitch"] + 0.2, chirp(900, 1800, 0.18, 0.06), 0.35)
    # MeAI 홈 : 쾅 + 반짝
    add(S["home"] - 0.2, whoosh(), 0.6)
    add(S["home"], boom(1.0), 0.8)
    add(S["home"] + 0.05, tone(1568, 0.9, 0.3) * 0.5 + tone(2093, 0.9, 0.25) * 0.3, 0.5)
    # 박자(분당 128) : MeAI 홈부터 결심 직전까지
    beat = 60 / 128
    t = S["home"]
    while t < S["fist"]:
        x = np.arange(int(0.22 * SR)) / SR
        add(t, np.sin(2 * np.pi * (120 - 70 * x) * x) * np.exp(-x * 20), 0.5)
        add(t + beat / 2, noise(0.05, 0.01), 0.10)
        t += beat
    # 단계 전환 : 휙 + 자막 뜰 때 '딩'
    for nm in ("reco", "custom", "answer", "design", "report", "eyes"):
        add(S[nm] - 0.16, whoosh(0.3), 0.45)
    for nm, dt in (("reco", 0.4), ("custom", 0.6), ("answer", 0.4), ("design", 0.35), ("report", 0.35)):
        add(S[nm] + dt, tone(1319, 0.25, 0.08) * 0.6 + tone(1760, 0.25, 0.06) * 0.4, 0.22)
    for k in range(8):                                   # 맞춤대화 타자
        add(S["custom"] + 1.2 + k * 0.08, noise(0.03, 0.006), 0.16)
    add(S["answer"], chirp(300, 900, 1.2, 0.8), 0.18)   # 보장분석 훑기
    add(S["design"] + 1.1, tone(988, 0.12, 0.04), 0.35)
    add(S["design"] + 1.25, tone(1319, 0.2, 0.06), 0.35)
    for k in range(8):                                   # 리포트 출력
        add(S["report"] + k * 0.1, noise(0.06, 0.02), 0.18)
    # 눈 반짝
    add(S["eyes"] + 0.1, tone(2637, 0.6, 0.15) + tone(3136, 0.6, 0.12), 0.25)
    add(S["eyes"] + 0.2, chirp(700, 1400, 0.25, 0.1), 0.3)
    # 결심 : 쾅 + 상승음
    add(S["fist"], boom(1.4), 1.0)
    add(S["fist"] + 0.1, chirp(220, 660, 1.2, 0.6) * 0.4 + tone(523, 1.2, 0.5) * 0.3 + tone(784, 1.2, 0.5) * 0.25,
        0.6)
    # 마무리
    x = np.arange(int(1.5 * SR)) / SR
    add(S["end"] + 0.2, np.sin(2 * np.pi * 55 * x) * np.exp(-x * 1.5), 0.7)
    add(S["end"] + 1.3, boom(1.0), 0.6)
    add(S["end"] + 1.3, tone(392, 1.3, 0.6) + tone(587, 1.3, 0.6) + tone(784, 1.3, 0.5), 0.22)
    # 결심 문구 착지
    add(S["fist"] + 0.5, boom(0.6), 0.55)
    # 피날레 : 휙(날아옴) → 쿵 + 금속성 울림 + 마지막 화음
    add(S["finale"] + 0.05, chirp(500, 900, 0.3, 0.15), 0.18)
    w = whoosh(0.4)
    add(S["finale"] + 0.38, w * np.linspace(0.3, 1.0, len(w)), 0.8)
    add(S["finale"] + 0.75, boom(1.6), 1.0)
    add(S["finale"] + 0.75, noise(0.25, 0.03), 0.5)
    add(S["finale"] + 0.75, tone(110, 1.8, 0.9) * 0.8 + tone(220, 1.8, 0.6) * 0.4, 0.6)
    add(S["finale"] + 0.8, tone(523, 1.8, 0.9) + tone(659, 1.8, 0.9) + tone(784, 1.8, 0.8) + tone(1047, 1.8, 0.6),
        0.18)

    out = out / max(1e-6, np.abs(out).max()) * 0.88
    out[-int(0.7 * SR):] *= np.linspace(1, 0, int(0.7 * SR))
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((out * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "meai_home_30s_anime.mp4"))
    args = ap.parse_args()
    tmp = tempfile.mkdtemp()
    P = grab(args.src, tmp)
    scenes = build(P)
    wav = os.path.join(tmp, "sfx.wav")
    make_audio(wav, scenes)
    enc = subprocess.Popen(
        [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
         "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", args.out],
        stdin=subprocess.PIPE)
    prev = None
    for name, fn, d in scenes:
        for i in range(int(round(d * FPS))):
            t = i / FPS
            im = fn(t, d).convert("RGB")
            if prev is not None and name not in ("glitch", "home", "fist", "end", "finale") and t < 0.12:
                im = Image.blend(prev, im, 0.35 + 0.65 * t / 0.12)
            enc.stdin.write(im.tobytes())
        prev = im
        print("  %-8s %.1f초" % (name, d))
    enc.stdin.close()
    enc.wait()
    print("완성 :", args.out)


if __name__ == "__main__":
    main()
