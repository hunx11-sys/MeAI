# -*- coding: utf-8 -*-
"""영업지원도구 6종 15초 팝아트 광고 — 다시 만들기
   python3 docs/promo_15s/build.py   →  docs/meai_tools6_popart_15s.mp4 (1080×1920 · 30fps · 160BPM 음악)
   필요 : playwright(크로미엄) · numpy · imageio-ffmpeg(pip install imageio-ffmpeg)
   장면·문구는 ad.html 의 TOOLS 와 hook/turn/tool/grid/end 함수에서 고친다. 캐릭터 그림은 pop_*.png(걱정인형 스티커)."""
import os, wave, shutil, subprocess, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'meai_tools6_popart_15s.mp4')
SR, T, BEAT = 44100, 15.0, 60 / 160


def music(path):
    N = int(SR * T); out = np.zeros(N); rng = np.random.default_rng(7)
    def add(sig, t, g=1.0):
        i = int(t * SR); j = min(N, i + len(sig))
        if i < N: out[i:j] += g * sig[:j - i]
    def kick():
        n = int(.35 * SR); t = np.arange(n) / SR; f = 48 + 120 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * np.exp(-t * 9) + 0.3 * np.tanh(4 * np.sin(ph)) * np.exp(-t * 30)
    def snare():
        n = int(.25 * SR); t = np.arange(n) / SR; nz = np.convolve(rng.standard_normal(n), [1, -0.9], 'same')
        return 0.55 * nz * np.exp(-t * 18) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    def hat(o=False):
        n = int((.12 if o else .05) * SR); nz = np.diff(np.concatenate([[0], rng.standard_normal(n)])); t = np.arange(n) / SR
        return 0.25 * nz * np.exp(-t * (20 if o else 70))
    def bass(f, dur):
        n = int(dur * SR); t = np.arange(n) / SR; s = 0.6 * (2 * ((t * f) % 1) - 1) + 0.3 * np.sign(np.sin(np.pi * f * t))
        y = np.zeros(n)
        for i in range(1, n): y[i] = y[i - 1] + 0.12 * (s[i] - y[i - 1])
        return y * np.minimum(1, np.exp(-t * 3)) * np.minimum(1, t * 200)
    def impact():
        n = int(.9 * SR); t = np.arange(n) / SR
        return 0.9 * np.sin(2 * np.pi * (40 + 60 * np.exp(-t * 6)) * t) * np.exp(-t * 3.5) + 0.35 * rng.standard_normal(n) * np.exp(-t * 7)
    def riser(dur):
        n = int(dur * SR); t = np.arange(n) / SR; f = 300 + 2500 * (t / dur) ** 2
        return (0.25 * rng.standard_normal(n) + 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * (t / dur) ** 2
    def blip(f):
        n = int(.12 * SR); t = np.arange(n) / SR; return 0.35 * np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 25)
    T0, T1, T2, T3 = 4 * BEAT, 6 * BEAT, 30 * BEAT, 35 * BEAT
    roots = [55, 55, 65.41, 49]
    for b in range(int(T / BEAT)):
        t = b * BEAT
        if t < T0:
            if b % 2 == 0: add(kick(), t, .7)
            add(blip(880 if b % 2 else 660), t, .5); continue
        add(kick(), t)
        if b % 2: add(snare(), t, .9)
        add(hat(), t, .8); add(hat(True), t + .5 * BEAT, .8)
        add(bass(roots[(b // 4) % 4] * 2, BEAT * .45), t + BEAT * .5, .55)
        if T2 <= t < T3: add(hat(True), t + .25 * BEAT, .6)
    add(riser(T0), 0, .9)
    for tt in [T0] + [T1 + i * 4 * BEAT for i in range(6)] + [T2, T3]: add(impact(), tt, 1.0 if tt in (T0, T3) else .7)
    fade = int(.4 * SR); out[-fade:] *= np.linspace(1, 0, fade)
    out = np.tanh(out * 0.9); out /= np.max(np.abs(out)) * 1.05
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([out, out], 1) * 32767).astype('<i2').tobytes())


def main():
    from playwright.sync_api import sync_playwright
    import imageio_ffmpeg
    tmp = tempfile.mkdtemp(); fr = os.path.join(tmp, 'f'); os.makedirs(fr)
    music(os.path.join(tmp, 'music.wav'))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium') if os.path.exists('/opt/pw-browsers/chromium') else None)
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto('file://' + os.path.join(HERE, 'ad.html')); pg.wait_for_timeout(800)
        for i in range(int(T * 30)):
            pg.evaluate('t=>render(t)', i / 30)
            pg.locator('#v').screenshot(path=os.path.join(fr, '%04d.jpg' % i), type='jpeg', quality=95)
        b.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(fr, '%04d.jpg'),
                    '-i', os.path.join(tmp, 'music.wav'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', OUT], check=True)
    shutil.rmtree(tmp); print('완료 :', os.path.abspath(OUT))


if __name__ == '__main__':
    main()
