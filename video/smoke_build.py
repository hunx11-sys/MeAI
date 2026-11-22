#!/usr/bin/env python3
"""한국어 시험 영상의 재료 만들기 : 장면마다 내레이션을 합성하고, 그 길이에 맞춰 장면 시간 · 자막을 채운다.

    python video/smoke_build.py <smoke_ko.json> <remotion public 폴더 안의 작업 폴더> [배경음 파일]

결과 : 작업 폴더에 narration.wav · props.json (Remotion 의 Explainer 가 읽는 형식)
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import korean_voice as kv  # noqa: E402

TAIL = 1.2  # 마지막 문장 뒤 여유(초)


def main() -> int:
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    work = Path(sys.argv[2])
    music = Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
    work.mkdir(parents=True, exist_ok=True)
    rel = work.name  # public/ 아래 상대 경로의 첫 마디

    script = "\n".join(c["narration"] for c in spec["cuts"])
    res = kv.synthesize(script, work / "narration.wav", voice=spec.get("voice", 0), speed=spec.get("speed", 1.0))
    segs = res["segments"]

    # 장면마다 자기 문장들이 차지하는 구간을 찾는다(문장 순서 = 장면 순서).
    cuts, i = [], 0
    for n, c in enumerate(spec["cuts"]):
        count = len(kv.split_sentences(c["narration"]))
        mine = segs[i : i + count]
        i += count
        start = 0.0 if n == 0 else mine[0]["start"] - 0.15
        cut = {k: v for k, v in c.items() if k != "narration"}
        cut["in_seconds"] = round(start, 2)
        cuts.append(cut)
    for n, cut in enumerate(cuts):
        cut["out_seconds"] = cuts[n + 1]["in_seconds"] if n + 1 < len(cuts) else round(res["duration_seconds"] + TAIL, 2)

    audio = {"narration": {"src": f"{rel}/narration.wav", "volume": 1.0}}
    if music and music.is_file():
        shutil.copy(music, work / f"music{music.suffix}")
        audio["music"] = {"src": f"{rel}/music{music.suffix}", "volume": 0.12, "fadeInSeconds": 1.0, "fadeOutSeconds": 2.0}
    props = {
        "theme": spec.get("theme", "clean-professional"),
        "cuts": cuts,
        "overlays": [],
        "captions": kv.word_captions(segs),
        "captionStyle": {"wordsPerPage": 7, "fontSize": 44},
        "audio": audio,
    }
    (work / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"내레이션 {res['duration_seconds']}초 · 문장 {len(segs)}개 · 장면 {len(cuts)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
