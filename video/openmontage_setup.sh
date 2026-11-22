#!/usr/bin/env bash
# 오픈몽타주(영상 제작 도구) 설치 · 점검 스크립트. 몇 번을 돌려도 안전하다(이미 된 단계는 건너뛴다).
#
#   bash video/openmontage_setup.sh           # 설치(없으면 받고, 있으면 건너뜀) + 지금 되는 기능 요약
#   bash video/openmontage_setup.sh --smoke   # 위 + 한국어 시험 영상 한 편을 video/out/ 에 만든다
#   bash video/openmontage_setup.sh --check   # 설치는 건드리지 않고 기능 요약만
#
# 바꿀 수 있는 값(환경변수)
#   OPENMONTAGE_DIR   설치 위치      (기본 : 이 저장소 옆의 calesthio/openmontage)
#   OPENMONTAGE_REF   받을 판(커밋)  (기본 : 아래 PINNED — 이 저장소에서 동작을 확인한 판)
#
# 오픈몽타주는 AGPL-3.0 라이선스의 남의 프로그램이다. 그 코드를 이 저장소에 복사해 넣지 않고,
# 필요할 때마다 공식 저장소에서 받아 쓴다. 이 폴더에는 우리 쪽 설정 · 보조 스크립트만 둔다.
set -euo pipefail

PINNED="2e003e65fa99a0f329478a2c1cdcf26bc481933a"   # 2026-11-15 판 · 2026-11-21 동작 확인
URL="https://github.com/calesthio/OpenMontage"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
OM="${OPENMONTAGE_DIR:-$(dirname "$REPO")/calesthio/openmontage}"
REF="${OPENMONTAGE_REF:-$PINNED}"
MODE="${1:-}"

say() { printf '\n==> %s\n' "$*"; }
note() { printf '    %s\n' "$*"; }

# ---------------------------------------------------------------- 1. 받기
get_source() {
  if git -C "$OM" rev-parse HEAD >/dev/null 2>&1; then
    local origin
    origin="$(git -C "$OM" remote get-url origin 2>/dev/null | tr 'A-Z' 'a-z')"
    case "$origin" in
      *github.com/calesthio/openmontage*) note "이미 받아 둠 : $OM" ;;
      *) echo "오류 : $OM 은 오픈몽타주 저장소가 아닙니다($origin). OPENMONTAGE_DIR 로 다른 위치를 주세요." >&2; exit 1 ;;
    esac
    return
  fi
  if [ -e "$OM" ] && [ -n "$(ls -A "$OM" 2>/dev/null)" ]; then
    echo "오류 : $OM 에 다른 파일이 있습니다. 지우지 않고 멈춥니다." >&2; exit 1
  fi
  say "오픈몽타주 받는 중 ($REF)"
  mkdir -p "$OM"
  git -C "$OM" init -q
  git -C "$OM" remote add origin "$URL"
  local try
  for try in 1 2 3 4; do
    if GIT_LFS_SKIP_SMUDGE=1 git -C "$OM" fetch -q --depth 1 origin "$REF"; then break; fi
    [ "$try" = 4 ] && { echo "오류 : 저장소를 받지 못했습니다(네트워크)." >&2; exit 1; }
    sleep $((try * 3))
  done
  GIT_LFS_SKIP_SMUDGE=1 git -C "$OM" checkout -q FETCH_HEAD
}

# ---------------------------------------------------------------- 2. 설치
install_deps() {
  local mark="$OM/.meai_setup_done"
  if [ -f "$mark" ] && [ "$(cat "$mark")" = "$(git -C "$OM" rev-parse HEAD)" ] \
     && [ -x "$OM/.venv/bin/python" ] && [ -d "$OM/remotion-composer/node_modules" ]; then
    note "설치돼 있음(건너뜀)"
    return
  fi
  say "설치 중 (파이썬 · 노드 부품 · 1분쯤)"
  (cd "$OM" && make setup) >"$OM/.meai_setup.log" 2>&1 || {
    tail -30 "$OM/.meai_setup.log" >&2
    echo "오류 : 설치 실패. 전체 기록 $OM/.meai_setup.log" >&2; exit 1
  }
  git -C "$OM" rev-parse HEAD >"$mark"
}

# ---------------------------------------------------------------- 3. 우리 쪽 설정 얹기
overlay() {
  # 화면을 찍는 브라우저 : 이미 있는 것을 쓰게 한다(내려받기 주소가 막혀 있음).
  cp "$HERE/remotion.config.ts" "$OM/remotion-composer/remotion.config.ts"
  # 둘째 엔진(HyperFrames)의 사용 통계 전송을 끈다(이 컴퓨터 설정에 저장 · env.sh 도 같은 값을 준다).
  (cd "$OM" && HYPERFRAMES_NO_TELEMETRY=1 npx --yes hyperframes telemetry disable >/dev/null 2>&1) || true
  # 우리가 얹은 파일 · 표시 파일이 오픈몽타주 쪽 변경으로 보이지 않게 한다.
  local ex="$OM/.git/info/exclude" f
  for f in .meai_setup_done .meai_setup.log remotion-composer/remotion.config.ts remotion-composer/public/meai_smoke/ \
           tools/audio/meai_korean_voice.py tools/audio/supertonic_tts.py; do
    grep -qxF "$f" "$ex" 2>/dev/null || echo "$f" >>"$ex"
  done
}

# ---------------------------------------------------------------- 4. 한글 글꼴
korean_font() {
  if [ "$(fc-list 2>/dev/null | grep -ci pretendard)" -gt 0 ]; then
    note "한글 글꼴(프리텐다드) 있음"
  else
    say "한글 글꼴(프리텐다드) 설치 중"
    local tmp fdir="$HOME/.local/share/fonts/pretendard"
    tmp="$(mktemp -d)"
    if (cd "$tmp" && npm pack pretendard@1.3.9 --silent >/dev/null 2>&1) \
       && tar -xzf "$tmp"/pretendard-*.tgz -C "$tmp" --wildcards 'package/dist/public/static/*.otf' 2>/dev/null; then
      mkdir -p "$fdir"
      cp "$tmp"/package/dist/public/static/*.otf "$fdir/"
      echo "Pretendard 1.3.9 (npm 패키지 pretendard) · SIL Open Font License 1.1 · https://github.com/orioncactus/pretendard" >"$fdir/SOURCE.txt"
    else
      note "[건너뜀] 글꼴 패키지를 받지 못했습니다. 한글이 못생긴 대체 글꼴로 나올 수 있습니다."
    fi
    rm -rf "$tmp"
  fi
  # 글꼴을 따로 지정하지 않은 글자(영문 글꼴에 없는 한글 포함)는 프리텐다드로 나오게 한다.
  local cdir="$HOME/.config/fontconfig/conf.d"
  mkdir -p "$cdir"
  cat >"$cdir/60-meai-korean.conf" <<'XML'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <alias><family>sans-serif</family><prefer><family>Pretendard</family></prefer></alias>
  <alias><family>system-ui</family><prefer><family>Pretendard</family></prefer></alias>
  <alias><family>serif</family><prefer><family>Pretendard</family></prefer></alias>
  <alias><family>Inter</family><accept><family>Pretendard</family></accept></alias>
</fontconfig>
XML
  fc-cache -f >/dev/null 2>&1 || true
}

# ---------------------------------------------------------------- 5. 배경음
music() {
  local lib="$OM/music_library"
  mkdir -p "$lib"
  # 소유자가 저장소 video/music/ 에 넣어 둔 음악이 있으면 그것부터.
  if [ -d "$HERE/music" ]; then
    find "$HERE/music" -maxdepth 1 -type f \( -name '*.mp3' -o -name '*.wav' -o -name '*.m4a' -o -name '*.flac' -o -name '*.ogg' \) \
      -exec cp -n {} "$lib/" \;
  fi
  if ! ls "$lib"/meai_* >/dev/null 2>&1; then
    say "기본 배경음 만드는 중(직접 합성 · 저작권 걱정 없음)"
    "$OM/.venv/bin/python" "$HERE/make_music.py" "$lib"
  else
    note "배경음 있음 : $(ls "$lib" | wc -l)곡"
  fi
}

# ---------------------------------------------------------------- 5-1. 한국어 내레이션
korean_voice() {
  # 오픈몽타주의 도구 폴더에 우리 도구를 얹는다(스스로 찾아 등록한다).
  cp "$HERE/korean_voice.py" "$OM/tools/audio/meai_korean_voice.py"
  cp "$HERE/overlay/supertonic_tts.py" "$OM/tools/audio/supertonic_tts.py"
  if ! "$OM/.venv/bin/python" -c "import sherpa_onnx, soundfile" >/dev/null 2>&1; then
    say "한국어 음성 엔진 설치 중(sherpa-onnx)"
    "$OM/.venv/bin/python" -m pip install -q "sherpa-onnx==2.0.2" soundfile >>"$OM/.meai_setup.log" 2>&1 \
      || { note "[건너뜀] 음성 엔진을 설치하지 못했습니다. 내레이션 없이 진행됩니다."; return; }
  fi
  # Piper : 목소리 파일이 없는데도 「가능」으로 잡혀, 음성 선택기가 자동으로 고를 때 먼저 뽑히고 실패한다.
  # 목소리 파일(~/.piper/models/*.onnx)이 없는 동안은 꺼 두고, 생기면 다시 켠다.
  if ls "$HOME/.piper/models"/*.onnx >/dev/null 2>&1; then
    [ -f "$OM/.venv/bin/piper.off" ] && mv "$OM/.venv/bin/piper.off" "$OM/.venv/bin/piper"
  else
    [ -f "$OM/.venv/bin/piper" ] && mv "$OM/.venv/bin/piper" "$OM/.venv/bin/piper.off"
  fi
  if "$OM/.venv/bin/python" "$HERE/korean_voice.py" setup >>"$OM/.meai_setup.log" 2>&1; then
    note "한국어 내레이션 준비됨(Supertonic 3 · 목소리 10종)"
  else
    note "[건너뜀] 한국어 목소리 모델을 받지 못했습니다 : $(tail -1 "$OM/.meai_setup.log")"
  fi
}

# ---------------------------------------------------------------- 5-2. 추가 도구(받아쓰기 · 장면 분석 · 실사 영상 검색 · 도표)
extras() {
  # 소유자가 2026-11-22 허용한 주소(허깅페이스 · pytorch 등)가 있어야 된다. 없으면 건너뛴다(영상은 그래도 만들 수 있다).
  local py="$OM/.venv/bin/python"
  if ! "$py" -c "import torch, transformers, faster_whisper, scenedetect, cv2, pygments" >/dev/null 2>&1; then
    say "추가 도구 설치 중(AI 엔진 CPU판 · 받아쓰기 · 장면 분석 · 30초쯤)"
    if "$py" -m pip install -q torch --index-url https://download.pytorch.org/whl/cpu >>"$OM/.meai_setup.log" 2>&1 \
       && "$py" -m pip install -q transformers faster-whisper scenedetect opencv-python-headless Pygments \
            youtube-transcript-api yt-dlp mediapipe >>"$OM/.meai_setup.log" 2>&1; then
      note "추가 도구 설치됨"
    else
      note "[건너뜀] 추가 도구를 설치하지 못했습니다(주소 허용 확인 · 기록 .meai_setup.log). 기본 영상 제작은 됩니다."
    fi
  else
    note "추가 도구 있음"
  fi
  command -v mmdc >/dev/null 2>&1 || PUPPETEER_SKIP_DOWNLOAD=1 npm install -g --silent @mermaid-js/mermaid-cli >/dev/null 2>&1 || true
  # 이 환경용 작은 보정(NASA 영상 주소를 https 로)
  "$py" "$HERE/overlay/patch_openmontage.py" "$OM" | grep -v "이미 됨" || true
}

# ---------------------------------------------------------------- 6. 기능 요약
summary() {
  say "지금 되는 기능"
  (. "$HERE/env.sh" && cd "$OM" && .venv/bin/python - <<'PY'
import logging, warnings
warnings.filterwarnings("ignore"); logging.disable(logging.CRITICAL)
from pathlib import Path
from tools.tool_registry import registry
registry.discover()
s = registry.provider_menu_summary()
rt = s.get("composition_runtimes", {})
print("    화면 합성 엔진 : " + " · ".join(f"{k} {'가능' if v else '불가'}" for k, v in rt.items()))
label = {"tts": "내레이션 음성", "music_library": "배경음(보관함)", "music_search": "배경음(인터넷 검색)",
         "image_generation": "그림 생성", "video_generation": "영상 생성(AI)", "clip_acquisition": "무료 실사 영상 찾기",
         "subtitle": "자막", "video_post": "편집 · 합치기", "character_animation": "캐릭터 애니메이션",
         "screen_capture": "화면 녹화", "avatar": "말하는 아바타"}
caps = {c.get("capability"): c for c in s.get("capabilities", [])}
for key, name in label.items():
    c = caps.get(key)
    if c:
        print(f"    {name:<14} {c.get('configured')}/{c.get('total')}")
print("    ※ 위 숫자는 「도구가 설치돼 있다」는 뜻이다. 인터넷에서 받아 오는 것(무료 실사 영상 · 배경음 검색)은")
print("      받는 주소가 이 환경의 허용 목록에 있어야 실제로 된다(video/README.md 「막혀 있는 것」).")
try:
    from tools.audio.meai_korean_voice import model_ready
    ko = model_ready()
except Exception:
    ko = False
print("    ※ 한국어 내레이션 : " + ("된다 — 음성 선택기에 preferred_provider=\"supertonic\" 로 고른다(목소리 0~9)."
                                 if ko else "안 된다 — 목소리 모델을 받지 못했다(설치 기록 .meai_setup.log)."))
print("      (Piper 는 목소리 파일을 받을 수 없어 꺼 두었다 — 자동 선택 때 잘못 뽑히지 않게.)")
PY
  ) || note "[건너뜀] 기능 요약을 만들지 못했습니다."
}

# ---------------------------------------------------------------- 7. 한국어 시험 영상
smoke() {
  say "한국어 시험 영상 만드는 중(내레이션 · 자막 · 배경음 · 2~3분)"
  local pub="$OM/remotion-composer/public/meai_smoke" out="$REPO/video/out"
  rm -rf "$pub"; mkdir -p "$pub" "$out"
  local track
  track="$(ls "$OM"/music_library/meai_calm.* 2>/dev/null | head -1)"
  (. "$HERE/env.sh" && python "$HERE/smoke_build.py" "$HERE/smoke_ko.json" "$pub" "$track") | sed 's/^/    /'
  (. "$HERE/env.sh" && cd "$OM/remotion-composer" && npx remotion render src/index.tsx Explainer \
      "$out/openmontage_smoke_ko.mp4" --props "$pub/props.json" --codec h264 --log error)
  note "완성 : $out/openmontage_smoke_ko.mp4"
  ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height \
    -of default=nw=1 "$out/openmontage_smoke_ko.mp4" | sed 's/^/    /'
}

if [ "$MODE" = "--check" ]; then
  [ -x "$OM/.venv/bin/python" ] || { echo "아직 설치되지 않았습니다. 먼저 : bash video/openmontage_setup.sh" >&2; exit 1; }
  summary
  exit 0
fi

say "오픈몽타주 준비 ($OM)"
get_source
install_deps
overlay
korean_font
music
korean_voice
extras
summary
[ "$MODE" = "--smoke" ] && smoke
printf '\n준비 끝. 영상 작업 순서 : source video/env.sh  →  cd "$OM"  →  AGENT_GUIDE.md 를 읽고 시작한다.\n(설치 위치 %s)\n' "$OM"
