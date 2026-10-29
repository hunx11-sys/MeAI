# -*- coding: utf-8 -*-
"""운전자보험 「변호사 현물지원」 액션 광고 18초 — 다시 만들기
   python3 docs/promo_lawyer/build.py   →  docs/lawyer_driver_ad_18s.mp4 (1920×1080 · 30fps · 효과음 + 배경음)
   필요 : node + playwright(크로미엄, render.js 가 장면을 찍는다) · numpy · ffmpeg
   장면·문구는 ad.html 의 WALLS 와 scene1 / crashScene / scene4 에서 고친다. 소리는 아래 sound() 의 시각표."""
import os, wave, shutil, subprocess, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'lawyer_driver_ad_18s.mp4')
SR, T, FPS, BPM = 44100, 18.0, 30, 140
IMPACTS = [4 + 2.4, 8 + 2.2]          # ad.html crashScene 의 Ti 와 맞춘다


def sound(path):
    N = int(SR * T); out = np.zeros(N); rng = np.random.default_rng(11)
    def add(sig, t, g=1.0):
        i = int(t * SR); j = min(N, i + len(sig))
        if 0 <= i < N: out[i:j] += g * sig[:j - i]
    def kick():
        n = int(.3 * SR); t = np.arange(n) / SR; f = 45 + 110 * np.exp(-t * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    def snare():
        n = int(.22 * SR); t = np.arange(n) / SR
        return .5 * rng.standard_normal(n) * np.exp(-t * 20) + .3 * np.sin(2 * np.pi * 200 * t) * np.exp(-t * 30)
    def hat():
        n = int(.05 * SR); t = np.arange(n) / SR; return .18 * np.diff(np.r_[0, rng.standard_normal(n)]) * np.exp(-t * 70)
    def engine(f0, f1, dur, g=1.0):   # 엔진음 : 톱니파 + 거친 배음, 회전수 f0→f1
        n = int(dur * SR); t = np.arange(n) / SR; f = f0 + (f1 - f0) * (t / dur) ** 1.6
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = .5 * (2 * ((ph / (2 * np.pi)) % 1) - 1) + .35 * np.tanh(3 * np.sin(ph * .5)) + .1 * rng.standard_normal(n)
        y = np.zeros(n); a = .25
        for i in range(1, n): y[i] = y[i - 1] + a * (s[i] - y[i - 1])
        env = np.minimum(1, t * 8) * np.minimum(1, (dur - t) * 6)
        return g * y * env
    def boom():
        n = int(1.4 * SR); t = np.arange(n) / SR
        low = np.sin(2 * np.pi * (35 + 70 * np.exp(-t * 5)) * t) * np.exp(-t * 2.5)
        return .95 * low + .5 * rng.standard_normal(n) * np.exp(-t * 6)
    def crumple(dur=1.0):  # 종이 찢기는 소리
        n = int(dur * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n)
        hp = np.diff(np.r_[0, nz]); bursts = (rng.random(n) < .004).astype(float)
        env = np.convolve(bursts, np.exp(-np.arange(800) / 120), 'same')
        return .5 * hp * np.clip(env, 0, 1) * np.exp(-t * 2.2)
    def whoosh(dur=.7):
        n = int(dur * SR); t = np.arange(n) / SR; nz = rng.standard_normal(n); y = np.zeros(n)
        for i in range(1, n): y[i] = y[i - 1] + (.05 + .4 * (t[i] / dur)) * (nz[i] - y[i - 1])
        return .6 * y * np.sin(np.pi * t / dur)
    def skid(dur=.8):
        n = int(dur * SR); t = np.arange(n) / SR
        return .25 * np.sin(2 * np.pi * (1800 + 300 * np.sin(t * 40)) * t) * np.exp(-t * 2) + .15 * rng.standard_normal(n) * np.exp(-t * 3)
    def ding():
        n = int(1.2 * SR); t = np.arange(n) / SR
        return .3 * (np.sin(2 * np.pi * 1318 * t) + .5 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 3)
    def stab(f):
        n = int(.5 * SR); t = np.arange(n) / SR
        return .3 * sum(np.sign(np.sin(2 * np.pi * f * k * t)) / k for k in (1, 1.5, 2)) * np.exp(-t * 6)

    beat = 60 / BPM
    for b in range(int(T / beat)):          # 배경 박자 (벽 돌파 직후 잠깐 쉰다)
        t = b * beat
        if any(i - .05 < t < i + .5 for i in IMPACTS) or t > 17.4: continue
        add(kick(), t, .55 if t > 1.4 else .3)
        if b % 2: add(snare(), t, .35)
        add(hat(), t + beat / 2, .7)
    add(engine(38, 60, 1.4, .35), 0)                       # 1 공회전
    add(engine(60, 150, 1.95, .6), 1.4)                    #   회전수 올리기
    add(whoosh(.8), 3.25, .9); add(engine(150, 210, .7, .6), 3.3)
    add(engine(60, 230, 1.15, .7), 4 + 1.3)                # 2 가속
    add(engine(80, 260, 1.2, .8), 8 + 1.05)                # 3 가속
    for i in IMPACTS: add(boom(), i, 1.0); add(crumple(1.3), i, 1.0); add(whoosh(.6), i + .55, .6)
    add(engine(180, 60, 2.0, .6), 12)                      # 4 감속 · 정차
    add(skid(.8), 13.7, .9); add(ding(), 15.1, 1.0)
    add(stab(220), 15.4, 1.0); add(boom(), 15.75, .6); add(stab(330), 15.75, 1.0)
    fade = int(.6 * SR); out[-fade:] *= np.linspace(1, 0, fade)
    out = np.tanh(out * 1.1); out /= np.max(np.abs(out)) * 1.05
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([out, out], 1) * 32767).astype('<i2').tobytes())


def main():
    tmp = tempfile.mkdtemp(); fr = os.path.join(tmp, 'f'); os.makedirs(fr)
    sound(os.path.join(tmp, 'sound.wav'))
    subprocess.run(['node', os.path.join(HERE, 'render.js'), fr, str(T), str(FPS)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fr, '%04d.jpg'),
                    '-i', os.path.join(tmp, 'sound.wav'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-shortest', OUT], check=True)
    shutil.rmtree(tmp); print('완료 :', os.path.abspath(OUT))


if __name__ == '__main__':
    main()
