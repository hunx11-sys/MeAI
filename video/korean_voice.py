#!/usr/bin/env python3
"""한국어 내레이션(무료 · 이 컴퓨터 안에서 합성 · 키 없음).

쓰는 것
  - 목소리 모델 : Supertonic 3 (수퍼톤 · 한국어 포함 31개 언어 · 모델 라이선스 OpenRAIL-M)
  - 합성 엔진   : sherpa-onnx (Apache-2.0 · 파이썬 패키지)

모델을 받는 길
  원래 보관소(huggingface.co)는 이 작업 환경에서 막혀 있다. 그래서 같은 모델을 sherpa-onnx 용으로
  바꿔 노드 패키지 저장소(npm)에 올려 둔 재포장본(@3sln/donki-lle-voice-multi 세 묶음 · 0.1.1)을 받는다.
  패키지 안의 프로그램은 실행하지 않는다 — 글자로 적힌 데이터 조각만 읽어 원래 파일로 되돌리고,
  아래 SHA256 값(2026-11-22 처음 받았을 때의 값)과 같은지 확인한 뒤에만 쓴다. 다르면 멈춘다.

쓰는 법 (오픈몽타주 파이썬으로 실행 : source video/env.sh 뒤)
  python video/korean_voice.py setup                      # 모델 받기(한 번 · 20초쯤)
  python video/korean_voice.py say "읽을 문장" -o out.wav   # 합성 (--voice 0~9 · --speed 1.0 · --srt 자막.srt)
  python video/korean_voice.py say --file 대본.txt -o out.mp3 --json 구간.json
  python video/korean_voice.py voices -o 폴더               # 목소리 10종 견본
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

NPM_VERSION = "0.1.1"
NPM_PACKAGES = (
    "@3sln/donki-lle-voice-multi",
    "@3sln/donki-lle-voice-multi-2",
    "@3sln/donki-lle-voice-multi-3",
)
# 파일 : (크기, SHA256) — 되돌린 파일이 이 값과 다르면 쓰지 않는다.
MODEL_FILES = {
    "duration_predictor.onnx": (3700147, "c3eb91414d5ff8a7a239b7fe9e34e7e2bf8a8140d8375ffb14718b1c639325db"),
    "text_encoder.onnx": (36416150, "c7befd5ea8c3119769e8a6c1486c4edc6a3bc8365c67621c881bbb774b9902ff"),
    "vector_estimator.onnx": (78400833, "20cd86fa5c6effedfda0e7cffe5b0569ca401c440a0c3a1d72bf39286c0db3fd"),
    "vocoder.onnx": (25991073, "e923d60f53f95eb1ce235f1dc33ec56d9c057823c96fa6f8acf98f32b0da6152"),
    "tts.json": (8253, "42078d3aef1cd43ab43021f3c54f47d2d75ceb4e75f627f118890128b06a0d09"),
    "unicode_indexer.bin": (262144, "8402ca48e5189a8950138580b0fff64db6f072f24ac07cd54ba8b2fbb9883b30"),
    "voice.bin": (517168, "67d5209b0ee8ce6c74105ffbe12fe6a7628aea3b4ba2fcb308a4a67938a93ce8"),
}

# 목소리 번호. 남녀 구분은 견본의 음높이를 재서 추정한 것이다(0~4 : 177~252Hz · 5~9 : 93~150Hz, 2026-11-22).
VOICES = {
    0: "여성 1", 1: "여성 2(높은 음)", 2: "여성 3", 3: "여성 4", 4: "여성 5(낮은 음)",
    5: "남성 1(높은 음)", 6: "남성 2(낮은 음)", 7: "남성 3", 8: "남성 4", 9: "남성 5(낮은 음)",
}
DEFAULT_VOICE = 0
DEFAULT_STEPS = 8          # 재포장본이 적어 둔 값
SENTENCE_PAUSE = 0.35      # 문장 사이 쉼(초)


def model_dir() -> Path:
    return Path(os.environ.get("MEAI_TTS_DIR") or Path.home() / ".cache" / "meai_tts" / "supertonic3")


def model_ready(d: Path | None = None) -> bool:
    d = d or model_dir()
    return all((d / n).is_file() and (d / n).stat().st_size == size for n, (size, _) in MODEL_FILES.items())


# ----------------------------------------------------------------------------- 모델 받기
def _read_member(tar: tarfile.TarFile, name: str) -> str:
    f = tar.extractfile(tar.getmember(name))
    if f is None:
        raise RuntimeError(f"패키지 안에 {name} 이 없습니다.")
    return f.read().decode("ascii")


def setup(force: bool = False) -> Path:
    """npm 에서 받아 원래 파일로 되돌린다. 이미 있으면 아무것도 하지 않는다."""
    d = model_dir()
    if model_ready(d) and not force:
        return d
    if not shutil.which("npm"):
        raise RuntimeError("npm 이 없어 목소리 모델을 받을 수 없습니다.")
    with tempfile.TemporaryDirectory() as tmp:
        tars: dict[str, tarfile.TarFile] = {}
        for pkg in NPM_PACKAGES:
            r = subprocess.run(["npm", "pack", f"{pkg}@{NPM_VERSION}", "--silent"], cwd=tmp, capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(f"{pkg} 를 받지 못했습니다 : {r.stderr.strip()[:300]}")
            tgz = Path(tmp) / (pkg.lstrip("@").replace("/", "-") + f"-{NPM_VERSION}.tgz")
            tars[pkg] = tarfile.open(tgz, "r:gz")
        try:
            voice_js = _read_member(tars[NPM_PACKAGES[0]], "package/voice.js")
            manifest = json.loads(voice_js[voice_js.index("{"): voice_js.rindex("}") + 1])
            out: dict[str, bytes] = {}
            for name, info in manifest["files"].items():
                if name not in MODEL_FILES:
                    raise RuntimeError(f"처음 보는 파일이 들어 있습니다 : {name}")
                buf = bytearray()
                for part in info["parts"]:
                    m = re.fullmatch(r"(@3sln/donki-lle-voice-multi(?:-\d)?)@[\d.]+/(c/\d+\.js)", part)
                    if not m or m.group(1) not in tars:
                        raise RuntimeError(f"조각 이름을 읽을 수 없습니다 : {part}")
                    text = _read_member(tars[m.group(1)], "package/" + m.group(2))
                    mm = re.fullmatch(r'\s*export default "([A-Za-z0-9+/=]*)";\s*', text)
                    if not mm:
                        raise RuntimeError(f"조각이 데이터 한 줄 모양이 아닙니다(실행 코드일 수 있어 쓰지 않음) : {part}")
                    buf += base64.b64decode(mm.group(1))
                out[name] = bytes(buf)
        finally:
            for t in tars.values():
                t.close()
    for name, (size, sha) in MODEL_FILES.items():
        data = out.get(name)
        if data is None:
            raise RuntimeError(f"{name} 이 패키지에 없습니다.")
        got = hashlib.sha256(data).hexdigest()
        if len(data) != size or got != sha:
            raise RuntimeError(
                f"{name} 이 처음 받았을 때와 다릅니다(크기 {len(data)} · {got[:12]}…). 바뀐 파일은 쓰지 않습니다."
            )
    d.mkdir(parents=True, exist_ok=True)
    for name, data in out.items():
        (d / name).write_bytes(data)
    (d / "SOURCE.txt").write_text(
        "Supertonic 3 (Supertone Inc.) · 모델 라이선스 OpenRAIL-M · 원본 huggingface.co/Supertone/supertonic-3\n"
        f"받은 곳 : npm {', '.join(NPM_PACKAGES)} @ {NPM_VERSION} (sherpa-onnx 용 변환 재포장본)\n",
        encoding="utf-8",
    )
    return d


# ----------------------------------------------------------------------------- 합성
_ENGINE = None


def _engine():
    global _ENGINE
    if _ENGINE is None:
        import sherpa_onnx

        d = setup()
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                supertonic=sherpa_onnx.OfflineTtsSupertonicModelConfig(
                    duration_predictor=str(d / "duration_predictor.onnx"),
                    text_encoder=str(d / "text_encoder.onnx"),
                    vector_estimator=str(d / "vector_estimator.onnx"),
                    vocoder=str(d / "vocoder.onnx"),
                    tts_json=str(d / "tts.json"),
                    unicode_indexer=str(d / "unicode_indexer.bin"),
                    voice_style=str(d / "voice.bin"),
                ),
                num_threads=min(4, os.cpu_count() or 2),
                provider="cpu",
            )
        )
        if not cfg.validate():
            raise RuntimeError("목소리 모델 설정이 맞지 않습니다.")
        _ENGINE = sherpa_onnx.OfflineTts(cfg)
    return _ENGINE


def split_sentences(text: str) -> list[str]:
    """문장 단위로 나눈다(자막 구간이 된다). 빈 줄 · 줄바꿈 · 마침표류 뒤에서 끊는다."""
    text = re.sub(r"[*_#`>]+", " ", text)                 # 마크다운 기호
    parts: list[str] = []
    for line in re.split(r"\n+", text):
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        parts += [s.strip() for s in re.split(r"(?<=[.!?。…])\s+", line) if s.strip()]
    return parts


def synthesize(
    text: str,
    output_path: str | Path,
    voice: int = DEFAULT_VOICE,
    speed: float = 1.0,
    lang: str = "ko",
    steps: int = DEFAULT_STEPS,
    pause: float = SENTENCE_PAUSE,
) -> dict:
    """문장마다 합성해 이어 붙인다. 구간(문장 · 시작 · 끝 초)을 함께 돌려준다."""
    import numpy as np
    import sherpa_onnx
    import soundfile as sf

    sentences = split_sentences(text)
    if not sentences:
        raise ValueError("읽을 글이 없습니다.")
    if voice not in VOICES:
        raise ValueError(f"목소리 번호는 0~9 입니다(받은 값 {voice}).")
    tts = _engine()
    sr = tts.sample_rate
    chunks, segments, cursor = [], [], 0.0
    gap = np.zeros(int(pause * sr), dtype=np.float32)
    for i, sentence in enumerate(sentences):
        g = sherpa_onnx.GenerationConfig()
        g.sid, g.speed, g.num_steps, g.extra = int(voice), float(speed), int(steps), {"lang": lang}
        audio = tts.generate(sentence, g)
        samples = np.asarray(audio.samples, dtype=np.float32)
        if samples.size == 0:
            raise RuntimeError(f"소리가 만들어지지 않았습니다 : {sentence[:30]}")
        dur = samples.size / sr
        segments.append({"index": i + 1, "text": sentence, "start": round(cursor, 3), "end": round(cursor + dur, 3)})
        chunks.append(samples)
        cursor += dur
        if i < len(sentences) - 1:
            chunks.append(gap)
            cursor += pause
    wave = np.concatenate(chunks)
    peak = float(np.abs(wave).max())
    if peak > 0:
        wave = wave / peak * 0.89          # 소리가 작게 나와서 크기를 맞춘다
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() == ".wav":
        sf.write(str(out), wave, sr, subtype="PCM_16")
    else:
        tmp = out.with_suffix(".tmp.wav")
        sf.write(str(tmp), wave, sr, subtype="PCM_16")
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-b:a", "192k", str(out)], capture_output=True, text=True)
        tmp.unlink(missing_ok=True)
        if r.returncode != 0:
            raise RuntimeError(f"소리 파일 변환 실패 : {r.stderr.strip()[:300]}")
    return {
        "output": str(out),
        "sample_rate": sr,
        "duration_seconds": round(wave.size / sr, 3),
        "voice": voice,
        "voice_label": VOICES[voice],
        "speed": speed,
        "language": lang,
        "segments": segments,
    }


def write_srt(segments: list[dict], path: str | Path) -> None:
    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

    lines = []
    for s in segments:
        lines += [str(s["index"]), f"{ts(s['start'])} --> {ts(s['end'])}", s["text"], ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def word_captions(segments: list[dict]) -> list[dict]:
    """화면 자막(낱말 단위)용 구간. 문장 시간은 정확하고, 문장 안 낱말 시간은 글자 수로 나눈 어림값이다."""
    words = []
    for seg in segments:
        parts = seg["text"].split()
        total = sum(len(w) for w in parts) or 1
        t, span = seg["start"], seg["end"] - seg["start"]
        for i, w in enumerate(parts):
            d = span * len(w) / total
            item = {"word": w, "startMs": int(round(t * 1000)), "endMs": int(round((t + d) * 1000))}
            if i == len(parts) - 1:
                item["pageBreakAfter"] = True
            words.append(item)
            t += d
    return words


# ----------------------------------------------------------------------------- 명령줄
def main() -> int:
    ap = argparse.ArgumentParser(description="한국어 내레이션(무료 · 로컬 합성)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("setup", help="목소리 모델 받기")
    s.add_argument("--force", action="store_true")
    y = sub.add_parser("say", help="글을 읽어 소리 파일로")
    y.add_argument("text", nargs="?")
    y.add_argument("--file")
    y.add_argument("-o", "--output", required=True)
    y.add_argument("--voice", type=int, default=DEFAULT_VOICE)
    y.add_argument("--speed", type=float, default=1.0)
    y.add_argument("--lang", default="ko")
    y.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    y.add_argument("--srt")
    y.add_argument("--json")
    y.add_argument("--captions", help="화면 자막용 낱말 구간(json)도 쓴다")
    v = sub.add_parser("voices", help="목소리 10종 견본 만들기")
    v.add_argument("-o", "--output", required=True)
    v.add_argument("--text", default="안녕하세요. 한국어 내레이션 견본입니다. 마음에 드는 목소리 번호를 알려 주세요.")
    a = ap.parse_args()

    if a.cmd == "setup":
        d = setup(force=a.force)
        print(f"목소리 모델 준비됨 : {d}")
        return 0
    if a.cmd == "say":
        text = Path(a.file).read_text(encoding="utf-8") if a.file else (a.text or "")
        res = synthesize(text, a.output, voice=a.voice, speed=a.speed, lang=a.lang, steps=a.steps)
        if a.srt:
            write_srt(res["segments"], a.srt)
        if a.captions:
            Path(a.captions).write_text(json.dumps(word_captions(res["segments"]), ensure_ascii=False, indent=1), encoding="utf-8")
        if a.json:
            Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{res['output']}  {res['duration_seconds']}초  목소리 {a.voice}({res['voice_label']})  문장 {len(res['segments'])}개")
        return 0
    if a.cmd == "voices":
        out = Path(a.output)
        for sid, label in VOICES.items():
            res = synthesize(a.text, out / f"voice_{sid}.wav", voice=sid)
            print(f"  {sid} {label:<12} {res['duration_seconds']}초")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
