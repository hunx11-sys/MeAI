#!/usr/bin/env python3
"""서울중앙본부 정보미팅 「초기 실손 고객, 두 가지 할인 제도」 교육 영상 — 다시 뽑기.

오픈몽타주 파이썬으로 실행한다(저장소 루트에서) :

    bash video/openmontage_setup.sh                       # 세션마다 한 번(새 세션은 자동)
    source video/env.sh
    python video/projects/seoul-info-silson/make.py v3                      # 그대로 다시 뽑기
    python video/projects/seoul-info-silson/make.py v3 --resynth options    # 그 장면 내레이션만 새로 만들기
    python video/projects/seoul-info-silson/make.py v3 --resynth all        # 모든 장면 새로 만들기
    python video/projects/seoul-info-silson/make.py v3 --no-render          # 화면만 만들고 장면 사진으로 확인

고치는 곳
  - 말(내레이션) · 자막 : script.json — 문장마다 ["화면 자막", "읽기용 글(숫자는 한글로)"].
    글을 바꾼 장면은 --resynth <장면 id> 로 내레이션을 다시 만든다(바꾸지 않은 장면은 소유자가 들어 본 소리를 그대로 쓴다).
  - 화면 : build_html.py 의 SCENES(장면별 HTML) · CSS.
  - 목소리 번호 · 빠르기 : script.json 의 voice · speed(바꾸면 --resynth all).

결과 : video/out/seoul_info_silson_discount_<태그>.mp4 (저장소에는 올리지 않는다) · 렌더 약 10분.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OM = Path(os.environ.get("OM") or REPO.parent / "calesthio" / "openmontage")
PID = "seoul-info-silson-discount"
WS = OM / "projects" / PID / "hyperframes"
OUT = REPO / "video" / "out"
GSAP = "gsap@3.13.0"
FONTS = ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]


def run(cmd: list[str], **kw) -> None:
    subprocess.run(cmd, check=True, **kw)


def prepare_assets() -> None:
    a = WS / "assets"
    (a / "fonts").mkdir(parents=True, exist_ok=True)
    for p in (HERE / "assets").glob("*.png"):
        shutil.copy(p, a / p.name)
    fdir = Path.home() / ".local/share/fonts/pretendard"
    for w in FONTS:
        shutil.copy(fdir / f"Pretendard-{w}.otf", a / "fonts" / f"Pretendard-{w}.otf")
    if not (a / "gsap.min.js").is_file():
        with tempfile.TemporaryDirectory() as tmp:
            run(["npm", "pack", GSAP, "--silent"], cwd=tmp, stdout=subprocess.DEVNULL)
            with tarfile.open(next(Path(tmp).glob("gsap-*.tgz"))) as t:
                f = t.extractfile("package/dist/gsap.min.js")
                (a / "gsap.min.js").write_bytes(f.read())
    if not (a / "bgm.mp3").is_file():
        with tempfile.TemporaryDirectory() as tmp:
            run([sys.executable, str(REPO / "video/make_music.py"), tmp, "--seconds", "320"], stdout=subprocess.DEVNULL)
            shutil.copy(Path(tmp) / "meai_calm.mp3", a / "bgm.mp3")
    hj = WS / "hyperframes.json"
    if not hj.is_file():
        hj.write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                                  "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                                  "media": {"autoProxy": True}}, indent=2), encoding="utf-8")


def resynth(spec: dict, timing: dict, ids: set[str]) -> None:
    """고른 장면의 내레이션을 오픈몽타주 음성 도구(supertonic)로 다시 만들고 시간표를 고친다."""
    sys.path.insert(0, str(OM))
    os.chdir(OM)
    from tools.tool_registry import registry
    from tools.audio.meai_korean_voice import split_sentences

    registry.discover()
    sel = registry._tools["tts_selector"]
    old = {s["id"]: s for s in timing["scenes"]}
    new_scenes = []
    for sc in spec["scenes"]:
        if sc["id"] not in ids and sc["id"] in old:
            new_scenes.append(old[sc["id"]])
            continue
        wav = WS / "assets" / f"{sc['id']}.wav"
        say = "\n".join(l[1] for l in sc["lines"])
        r = sel.execute({"text": say, "preferred_provider": "supertonic", "voice": spec["voice"], "speed": spec["speed"],
                         "language_code": "ko", "output_path": str(wav)})
        if not r.success:
            raise SystemExit(f"내레이션 실패({sc['id']}) : {r.error}")
        segs, lines, i = r.data["segments"], [], 0
        for show, sy in sc["lines"]:
            n = len(split_sentences(sy))
            g = segs[i : i + n]
            i += n
            lines.append({"show": show, "start": g[0]["start"], "end": g[-1]["end"]})
        run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "160k", str(HERE / "audio" / f"{sc['id']}.mp3")])
        new_scenes.append({"id": sc["id"], "wav": f"audio/{sc['id']}.mp3", "dur": r.data["audio_duration_seconds"], "lines": lines})
        print(f"  새 내레이션 {sc['id']} {r.data['audio_duration_seconds']}초")
    timing["scenes"] = new_scenes
    (HERE / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")


def place_audio(timing: dict, fresh: set[str]) -> None:
    for s in timing["scenes"]:
        if s["id"] in fresh:
            continue
        run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / s["wav"]), str(WS / "assets" / f"{s['id']}.wav")])


def check_script(spec: dict, timing: dict) -> None:
    ids_s = [s["id"] for s in spec["scenes"]]
    ids_t = [s["id"] for s in timing["scenes"]]
    if ids_s != ids_t:
        raise SystemExit(f"script.json 과 timing.json 의 장면이 다릅니다 → 바뀐 장면을 --resynth 하세요.\n  {ids_s}\n  {ids_t}")
    for s, t in zip(spec["scenes"], timing["scenes"]):
        if [l[0] for l in s["lines"]] != [l["show"] for l in t["lines"]]:
            raise SystemExit(f"「{s['id']}」 장면 글이 바뀌었습니다 → --resynth {s['id']} 로 내레이션을 다시 만드세요.")


def main() -> int:
    ap = argparse.ArgumentParser(description="실손 할인 교육 영상 다시 뽑기")
    ap.add_argument("tag", help="판 이름(예 v3) — 결과 파일 이름에 붙는다")
    ap.add_argument("--resynth", default="", help="내레이션을 새로 만들 장면 id(쉼표) 또는 all")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()

    spec = json.loads((HERE / "script.json").read_text(encoding="utf-8"))
    timing = json.loads((HERE / "timing.json").read_text(encoding="utf-8"))
    WS.mkdir(parents=True, exist_ok=True)
    prepare_assets()
    ids = {s["id"] for s in spec["scenes"]} if a.resynth == "all" else {x for x in a.resynth.split(",") if x}
    if ids:
        resynth(spec, timing, ids)
    check_script(spec, timing)
    place_audio(timing, ids)
    run([sys.executable, str(HERE / "build_html.py"), str(HERE / "timing.json"), str(WS)])
    run(["npx", "--yes", "hyperframes@0.9.79", "lint"], cwd=WS, stdout=subprocess.DEVNULL)

    if a.no_render:
        sc = json.loads((WS / "index.html").read_text(encoding="utf-8").split("window.__SCENES__ = ", 1)[1].split(";\n", 1)[0])
        at = ",".join(f"{x['start'] + x['len'] - 1.3:.2f}" for x in sc)
        run(["npx", "--yes", "hyperframes@0.9.79", "snapshot", "--at", at, "--no-end"], cwd=WS)
        print("장면 사진 :", WS / ".hyperframes/artifacts/snapshots")
        return 0

    sys.path.insert(0, str(OM))
    os.chdir(OM)
    from tools.tool_registry import registry

    registry.discover()
    final = OM / "projects" / PID / "renders" / f"final_{a.tag}.mp4"
    r = registry._tools["hyperframes_compose"].execute({"operation": "render_existing", "workspace_path": str(WS),
                                                         "output_path": str(final), "quality": "standard", "fps": 30})
    if not r.success:
        raise SystemExit(f"렌더 실패 : {r.error}")
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"seoul_info_silson_discount_{a.tag}.mp4"
    shutil.copy(final, dst)
    print(f"완성 : {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
