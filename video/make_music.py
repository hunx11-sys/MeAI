#!/usr/bin/env python3
"""기본 배경음 만들기 (외부에서 받아 오는 것 없이 숫자 계산만으로 합성).

오픈몽타주는 무료 음악을 인터넷(pixabay 등)에서 찾는데, 이 작업 환경에서는 그 주소가
막혀 있다. 그래서 영상에 깔 배경음이 하나도 없는 일이 없도록 잔잔한 곡 세 개를 직접
만들어 둔다. 직접 만든 소리라 저작권 걱정이 없다(가져다 쓴 음원 · 샘플 없음).

    python make_music.py <저장할 폴더> [--seconds 90]

더 좋은 음악을 쓰고 싶으면 video/music/ 폴더에 mp3 · wav 를 넣으면 된다(그쪽이 먼저 쓰인다).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100

# 음 이름 -> 주파수 (A4 = 440Hz)
_SEMI = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def hz(note: str) -> float:
    name, octave = note[:-1], int(note[-1])
    semi = _SEMI[name[0]] + (1 if "#" in name else 0) - (1 if "b" in name else 0)
    return 440.0 * 2 ** ((semi + 12 * (octave - 4)) / 12)


CHORDS = {
    "C": ["C3", "E3", "G3", "C4", "E4"],
    "G": ["G2", "D3", "G3", "B3", "D4"],
    "Am": ["A2", "E3", "A3", "C4", "E4"],
    "F": ["F2", "C3", "F3", "A3", "C4"],
    "Dm": ["D3", "A3", "D4", "F4", "A4"],
    "Em": ["E3", "B3", "E4", "G4", "B4"],
}

# 곡 이름 : (빠르기, 화음 진행, 반주 무늬, 박자 소리 크기)
TRACKS = {
    "meai_calm": (76, ["C", "Am", "F", "G"], "slow", 0.0),
    "meai_bright": (108, ["F", "C", "G", "Am"], "arp", 0.5),
    "meai_focus": (92, ["Am", "F", "C", "G"], "pulse", 0.25),
}


def _env(n: int, attack: float, release: float) -> np.ndarray:
    """천천히 켜지고 천천히 꺼지는 음량 곡선."""
    e = np.ones(n)
    a, r = min(int(attack * SR), n // 2), min(int(release * SR), n // 2)
    if a:
        e[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if r:
        e[-r:] = np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return e


def pad(freq: float, seconds: float) -> np.ndarray:
    """부드럽게 깔리는 화음 소리(살짝 어긋난 사인파 세 개)."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * freq * d * t + p) for d, p in ((1.0, 0.0), (1.004, 1.3), (0.996, 2.1)))
    y += 0.25 * np.sin(2 * np.pi * freq * 2 * t)
    return y / 3.25 * _env(n, 0.9, 1.2)


def pluck(freq: float, seconds: float = 1.2) -> np.ndarray:
    """통 튕기는 소리(금방 작아지는 사인파)."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-6 * t)
    return y * np.exp(-3.2 * t) * _env(n, 0.004, 0.05)


def kick() -> np.ndarray:
    """부드러운 박자 소리(낮게 떨어지는 사인파)."""
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    f = 95 * np.exp(-14 * t) + 42
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-11 * t)


def add(buf: np.ndarray, at: float, snd: np.ndarray, gain: float, pan: float = 0.0) -> None:
    i = int(at * SR)
    if i >= len(buf):
        return
    snd = snd[: len(buf) - i]
    buf[i : i + len(snd), 0] += snd * gain * (1 - max(pan, 0) * 0.6)
    buf[i : i + len(snd), 1] += snd * gain * (1 + min(pan, 0) * 0.6)


def render(name: str, seconds: float) -> np.ndarray:
    bpm, prog, pattern, beat_gain = TRACKS[name]
    beat = 60.0 / bpm
    bar = beat * 4
    bars = int(np.ceil(seconds / bar))
    total = bars * bar
    buf = np.zeros((int(total * SR) + SR * 3, 2))
    k = kick()
    for b in range(bars):
        notes = [hz(n) for n in CHORDS[prog[b % len(prog)]]]
        t0 = b * bar
        for j, f in enumerate(notes[:4]):
            add(buf, t0, pad(f, bar + 0.8), 0.16, pan=(-0.5, 0.5, -0.2, 0.2)[j])
        add(buf, t0, pad(notes[0] / 2, bar + 0.4), 0.12)
        if pattern == "slow":
            for step, idx in enumerate((2, 3, 4, 3)):
                add(buf, t0 + step * beat, pluck(notes[idx] * 2, 1.8), 0.11, pan=0.3 if step % 2 else -0.3)
        elif pattern == "arp":
            for step, idx in enumerate((0, 2, 3, 4, 3, 2, 4, 3)):
                add(buf, t0 + step * beat / 2, pluck(notes[idx] * 2), 0.12, pan=0.4 if step % 2 else -0.4)
        else:
            for step in range(8):
                add(buf, t0 + step * beat / 2, pluck(notes[0], 0.5), 0.10)
            for step, idx in enumerate((3, 4)):
                add(buf, t0 + step * 2 * beat + beat, pluck(notes[idx] * 2, 1.6), 0.10, pan=0.3 - 0.6 * step)
        if beat_gain and b >= 2:
            for step in range(4):
                add(buf, t0 + step * beat, k, 0.30 * beat_gain if step % 2 else 0.42 * beat_gain)
    # 울림 : 조금 늦게 따라오는 작은 소리를 좌우 엇갈리게 한 번 더 얹는다.
    d = int(beat * 0.75 * SR)
    wet = np.zeros_like(buf)
    wet[d:, 0] += buf[:-d, 1] * 0.22
    wet[d:, 1] += buf[:-d, 0] * 0.22
    buf += wet
    buf = buf[: int(seconds * SR)]
    fade = int(2.5 * SR)
    buf[:fade] *= np.linspace(0, 1, fade)[:, None]
    buf[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return buf / np.max(np.abs(buf)) * 0.7


def save(buf: np.ndarray, out: Path) -> Path:
    wav = out.with_suffix(".wav")
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((buf * 32767).astype("<i2").tobytes())
    if shutil.which("ffmpeg"):
        mp3 = out.with_suffix(".mp3")
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)]
        )
        if r.returncode == 0 and mp3.exists():
            wav.unlink()
            return mp3
    return wav


def main() -> int:
    ap = argparse.ArgumentParser(description="기본 배경음 세 곡을 합성해 저장한다.")
    ap.add_argument("out_dir")
    ap.add_argument("--seconds", type=float, default=90.0)
    a = ap.parse_args()
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in TRACKS:
        path = save(render(name, a.seconds), out_dir / name)
        print(f"  배경음 {path.name}  ({path.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
