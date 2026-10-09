# -*- coding: utf-8 -*-
"""MeAI홈 오픈 30초 영상 v4 : 실사 숏폼드라마판.

- 캐릭터 그림 대신 실사 영상 두 개(책상에서 고민 → 모니터 / 놀람 → 미소 → 주먹)를 쓴다.
- 실사 모니터 클로즈업에서 천천히 다가가며 암전 → 실제 MeAI 화면 캡처로 넘어간다.
- 실사 장면에는 말풍선 대신 화면 위쪽에 글자가 '타닥타닥' 타이핑되듯 나온다(타자 소리 포함).
- 화면 장면·마무리·피날레는 v3(animate_v3.py)의 연출을 그대로 쓴다.

  python animate_v4.py <고민·모니터 영상> <놀람·주먹 영상> [--out 결과.mp4]
"""
import argparse
import os
import subprocess
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import animate_v3 as v3
from animate_v2 import FPS, H, RED, SR, W, ease, flash
from build_video import ffmpeg_exe

ROOT = v3.ROOT


# ---------------------------------------------------------------- 실사 영상 읽기
class Seg:
    """영상의 [ss, ss+dur) 구간을 1080x1920·30fps 로 맞춰 한 장씩 꺼낸다."""

    def __init__(self, path, ss, dur):
        vf = "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d" % (W, H, W, H, FPS)
        self.p = subprocess.Popen([ffmpeg_exe(), "-v", "error", "-ss", "%.3f" % ss, "-i", path, "-t", "%.3f" % dur,
                                   "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = Image.new("RGB", (W, H))

    def frame(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3:
            self.last = Image.frombuffer("RGB", (W, H), b).copy()
        return self.last.copy()


# ---------------------------------------------------------------- 드라마 색감
_VIG = None


def vignette():
    global _VIG
    if _VIG is None:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([-260, -200, W + 260, H + 200], fill=255)
        _VIG = m.filter(ImageFilter.GaussianBlur(220))
    return _VIG


def grade(im, mood="cool", seed=0):
    """대비를 살짝 올리고 분위기 색을 입힌 뒤 가장자리를 어둡게, 필름 결을 약간."""
    a = np.asarray(im).astype(np.float32)
    a = (a - 128) * 1.08 + 128
    if mood == "cool":
        a *= np.array([0.94, 0.99, 1.07])
    else:
        a *= np.array([1.05, 1.0, 0.95])
    g = np.random.default_rng(seed).normal(0, 5, (H // 2, W // 2, 1))
    a += np.repeat(np.repeat(g, 2, 0), 2, 1)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    dark = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.55)
    return Image.composite(im, dark, vignette())


def zoom(im, z, cx=0.5, cy=0.5):
    if z <= 1.0:
        return im
    zw, zh = int(W * z), int(H * z)
    big = im.resize((zw, zh), Image.BILINEAR)
    x = int(min(max(cx * zw - W / 2, 0), zw - W))
    y = int(min(max(cy * zh - H / 2, 0), zh - H))
    return big.crop((x, y, x + W, y + H))


def black(im, a):
    return Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), min(1.0, max(0.0, a))) if a > 0 else im


# ---------------------------------------------------------------- 위쪽 타이핑 글자
CPS = 15          # 1초에 찍히는 글자 수


def typed(text, t, t0):
    n = int(max(0.0, t - t0) * CPS)
    return text[:n], n >= len(text)


def type_overlay(im, t, lines, t0=0.3, size=62, top=200):
    """lines 를 위쪽에 한 글자씩 찍는다. '[강조]'는 빨간색. 끝에서 커서가 깜빡인다."""
    full = "\n".join(lines)
    plain = full.replace("[", "").replace("]", "")
    shown, done = typed(plain, t, t0)
    if not shown and t < t0:
        return im
    # 강조 표시를 보이는 글자 수만큼만 되살린다
    out, k = "", 0
    for ch in full:
        if ch in "[]":
            out += ch
            continue
        if k >= len(shown):
            break
        out += ch
        k += 1
    if out.count("[") > out.count("]"):
        out += "]"
    im = im.convert("RGBA")
    shade = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade).rectangle([0, 0, W, top + 300], fill=150)
    shade = shade.filter(ImageFilter.GaussianBlur(90))
    im.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), shade)
    d = ImageDraw.Draw(im)
    f = v3.pf(size, "Bold")
    rows = v3.rich(out)
    lh = size * 1.4
    for i, segs in enumerate(rows):
        x = 70
        y = top + i * lh
        for s, hot in segs:
            d.text((x + 2, y + 3), s, font=f, fill=(0, 0, 0, 160))
            d.text((x, y), s, font=f, fill=(RED if hot else (255, 255, 255)) + (255,))
            x += d.textlength(s, font=f)
        last_x, last_y = x, y
    if rows and (not done or int(t * 2.5) % 2 == 0):
        d.rectangle([last_x + 8, last_y + 6, last_x + 13, last_y + size + 4], fill=(255, 255, 255, 230))
    return im.convert("RGB")


# ---------------------------------------------------------------- 장면
def build(clip_a, clip_b):
    screens = {name: fn for name, fn, _ in v3.build([Image.new("RGB", (W, H))] * 11)}

    def live(path, ss, dur, fn):
        seg = {"s": None}

        def f(t, d):
            if seg["s"] is None:
                seg["s"] = Seg(path, ss, dur)
            return v3.watermark(fn(seg["s"].frame(), t, d))
        return f

    def a_worry(fr, t, d):
        im = grade(zoom(fr, 1.0 + 0.05 * t / d, 0.5, 0.4), "cool", int(t * FPS))
        im = black(im, 1 - t / 0.35) if t < 0.35 else im
        return type_overlay(im, t, ["이번 달 누구에게 영업하지…", "할 사람 다 한 것 같은데"], 0.35)

    def a_monitor(fr, t, d):
        im = grade(zoom(fr, 1.0 + 0.35 * ease(t / d), 0.48, 0.42), "cool", 99 + int(t * FPS))
        return black(im, (t - (d - 0.55)) / 0.5)          # 모니터로 다가가며 암전

    def from_black(name, dur_in=0.35):
        fn = screens[name]

        def f(t, d):
            return black(fn(t, d), 1 - t / dur_in) if t < dur_in else fn(t, d)
        return f

    def to_black(name, dur_out=0.35):
        fn = screens[name]

        def f(t, d):
            im = fn(t, d)
            return black(im, (t - (d - dur_out)) / dur_out)
        return f

    def b_wow(fr, t, d):
        im = grade(fr, "warm", 300 + int(t * FPS))
        im = black(im, 1 - t / 0.3) if t < 0.3 else im
        return type_overlay(im, t, ["와… 이게 [MeAI]로 다 된다고?"], 0.25)

    def b_smile(fr, t, d):
        im = grade(zoom(fr, 1.0 + 0.04 * t / d), "warm", 400 + int(t * FPS))
        return type_overlay(im, t + 10, ["와… 이게 [MeAI]로 다 된다고?"], 0.25)   # 글자는 이미 다 찍힌 상태

    def b_fist(fr, t, d):
        im = grade(fr, "warm", 500 + int(t * FPS))
        im = flash(im, 0.35 - t * 1.5, (255, 240, 235)) if t < 0.25 else im
        return type_overlay(im, t, ["[MeAI]에서 고객추천부터", "분석, 설계까지 한번에!"], 0.15, 64)

    A, B = clip_a, clip_b
    return [
        ("worry", live(A, 0.15, 4.6, a_worry), 4.6),
        ("monitor", live(A, 7.6, 1.8, a_monitor), 1.8),
        ("portal", from_black("portal"), 1.3),
        ("click", screens["click"], 1.3),
        ("home", screens["home"], 1.8),
        ("reco", screens["reco"], 2.0),
        ("custom", screens["custom"], 1.8),
        ("answer", screens["answer"], 2.0),
        ("design", screens["design"], 1.5),
        ("report", to_black("report"), 1.4),
        ("wow", live(B, 0.1, 1.9, b_wow), 1.9),
        ("smile", live(B, 2.1, 1.5, b_smile), 1.5),
        ("fist", live(B, 5.8, 2.8, b_fist), 2.8),
        ("end", screens["end"], 2.0),
        ("finale", screens["finale"], 2.3),
    ]


# ---------------------------------------------------------------- 소리
def make_audio(path, scenes):
    total = sum(d for _, _, d in scenes)
    n = int(SR * total)
    out = np.zeros(n)
    rng = np.random.default_rng(9)
    S, acc = {}, 0.0
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

    def key():                       # 타자 한 번 '탁'
        k = noise(0.035, 0.005) * 0.8 + tone(rng.uniform(1700, 2600), 0.035, 0.004) * 0.5
        return k

    def typing(at, text, t0, gain=0.5):
        plain = "\n".join(text).replace("[", "").replace("]", "")
        for i, ch in enumerate(plain):
            if ch.strip():
                add(at + t0 + i / CPS + rng.uniform(-0.008, 0.008), key(), gain * rng.uniform(0.7, 1.0))

    # 사무실 공기(낮은 웅웅거림) : 실사 장면 바닥에 깔기
    def room(d):
        r = np.convolve(rng.uniform(-1, 1, int(d * SR)), np.ones(400) / 400, "same")
        return r / (np.abs(r).max() + 1e-6)

    add(S["worry"], room(S["portal"]), 0.08)
    add(S["wow"], room(S["end"] - S["wow"]), 0.06)
    # 고민 : 시계 초침 + 타이핑 + 한숨
    for k in np.arange(0.4, S["monitor"], 1.0):
        add(k, tone(2100, 0.04, 0.007) + noise(0.04, 0.004) * 0.4, 0.18)
    typing(S["worry"], ["이번 달 누구에게 영업하지…", "할 사람 다 한 것 같은데"], 0.35)
    # 모니터로 다가감 → 암전 : 낮게 깔리는 상승음 + 둥
    add(S["monitor"], chirp(90, 240, 1.8, 1.5), 0.35)
    add(S["portal"] - 0.05, boom(1.2), 0.6)
    # 화면 장면 : 휙, 딸깍, 쾅, 딩, 박자
    add(S["click"] - 0.1, whoosh(0.25), 0.35)
    add(S["click"] + 0.92, noise(0.03, 0.003) + tone(3200, 0.03, 0.006), 0.7)
    add(S["click"] + 1.0, noise(0.03, 0.003) + tone(2600, 0.03, 0.006), 0.5)
    add(S["home"] - 0.2, whoosh(), 0.6)
    add(S["home"], boom(1.0), 0.8)
    add(S["home"] + 0.05, tone(1568, 0.9, 0.3) * 0.5 + tone(2093, 0.9, 0.25) * 0.3, 0.5)
    beat = 60 / 128
    t = S["home"]
    while t < S["report"] + 1.1:
        x = np.arange(int(0.22 * SR)) / SR
        add(t, np.sin(2 * np.pi * (120 - 70 * x) * x) * np.exp(-x * 20), 0.5)
        add(t + beat / 2, noise(0.05, 0.01), 0.10)
        t += beat
    for nm in ("reco", "custom", "answer", "design", "report"):
        add(S[nm] - 0.16, whoosh(0.3), 0.45)
    for nm, dt in (("reco", 0.4), ("custom", 0.6), ("answer", 0.4), ("design", 0.35), ("report", 0.35)):
        add(S[nm] + dt, tone(1319, 0.25, 0.08) * 0.6 + tone(1760, 0.25, 0.06) * 0.4, 0.22)
    for k in range(6):
        add(S["custom"] + 1.0 + k * 0.08, noise(0.03, 0.006), 0.15)
    add(S["design"] + 1.1, tone(1319, 0.2, 0.06), 0.3)
    for k in range(6):
        add(S["report"] + k * 0.1, noise(0.06, 0.02), 0.16)
    # 놀람 : 반짝 + 타이핑
    add(S["wow"] + 0.05, tone(2637, 0.7, 0.2) + tone(3136, 0.7, 0.16), 0.2)
    typing(S["wow"], ["와… 이게 MeAI로 다 된다고?"], 0.25)
    # 주먹 : 쾅 + 상승음 + 타이핑
    add(S["fist"], boom(1.2), 0.85)
    add(S["fist"] + 0.1, chirp(220, 660, 1.2, 0.6) * 0.4 + tone(523, 1.2, 0.5) * 0.3, 0.5)
    typing(S["fist"], ["MeAI에서 고객추천부터", "분석, 설계까지 한번에!"], 0.15, 0.45)
    # 마무리·피날레 (v3 와 같음)
    x = np.arange(int(1.5 * SR)) / SR
    add(S["end"] + 0.2, np.sin(2 * np.pi * 55 * x) * np.exp(-x * 1.5), 0.7)
    add(S["end"] + 1.3, boom(0.8), 0.5)
    add(S["finale"] + 0.05, chirp(500, 900, 0.3, 0.15), 0.18)
    w = whoosh(0.4)
    add(S["finale"] + 0.38, w * np.linspace(0.3, 1.0, len(w)), 0.8)
    add(S["finale"] + 0.75, boom(1.5), 1.0)
    add(S["finale"] + 0.75, noise(0.25, 0.03), 0.5)
    add(S["finale"] + 0.75, tone(110, 1.5, 0.9) * 0.8 + tone(220, 1.5, 0.6) * 0.4, 0.6)
    add(S["finale"] + 0.8, tone(523, 1.5, 0.9) + tone(659, 1.5, 0.9) + tone(784, 1.5, 0.8) + tone(1047, 1.5, 0.6),
        0.18)

    out = out / max(1e-6, np.abs(out).max()) * 0.88
    out[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((out * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip_a", help="책상에서 고민 → 모니터 클로즈업 영상")
    ap.add_argument("clip_b", help="놀람 → 미소 → 주먹 영상")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "meai_home_30s_drama.mp4"))
    args = ap.parse_args()
    scenes = build(args.clip_a, args.clip_b)
    wav = os.path.join(tempfile.mkdtemp(), "sfx.wav")
    make_audio(wav, scenes)
    enc = subprocess.Popen(
        [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
         "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "25",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", args.out],
        stdin=subprocess.PIPE)
    prev = None
    for name, fn, d in scenes:
        for i in range(int(round(d * FPS))):
            t = i / FPS
            im = fn(t, d).convert("RGB")
            if prev is not None and name in ("reco", "custom", "answer", "design", "report", "smile") and t < 0.12:
                im = Image.blend(prev, im, 0.35 + 0.65 * t / 0.12)
            enc.stdin.write(im.tobytes())
        prev = im
        print("  %-8s %.1f초" % (name, d))
    enc.stdin.close()
    enc.wait()
    print("완성 :", args.out)


if __name__ == "__main__":
    main()
