# 영상 작업용 환경값. 실행하지 말고 불러온다 :   source video/env.sh
# (명령을 새로 칠 때마다 다시 불러와야 한다. 셸 상태가 다음 명령으로 넘어가지 않기 때문이다.)

_meai_video_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
_meai_repo="$(cd "$_meai_video_dir/.." && pwd)"

# 오픈몽타주가 설치된 곳
export OM="${OPENMONTAGE_DIR:-$(dirname "$_meai_repo")/calesthio/openmontage}"

# 오픈몽타주 전용 파이썬(무료 음성 프로그램 piper 포함)을 먼저 찾게 한다.
[ -d "$OM/.venv/bin" ] && export PATH="$OM/.venv/bin:$PATH"

# 화면을 찍는 브라우저 : 캡처 전용 브라우저를 쓴다.
# 이걸 지정하지 않으면 둘째 엔진(HyperFrames)이 느린 방식으로 돈다(4초 영상 85초 → 지정하면 6초, 2026-11-21 측정).
if [ -x /opt/pw-browsers/chromium_headless_shell ]; then
  export OPENMONTAGE_CHROME=/opt/pw-browsers/chromium_headless_shell
  export PUPPETEER_EXECUTABLE_PATH="$OPENMONTAGE_CHROME"
  export CHROME_PATH="$OPENMONTAGE_CHROME"
fi

# 사용 통계를 바깥으로 보내지 않는다.
export HYPERFRAMES_NO_TELEMETRY=1
export DO_NOT_TRACK=1

# 배경음 보관함(설치 스크립트가 기본 3곡을 만들어 두고, video/music/ 의 파일을 복사해 둔다)
export MUSIC_LIBRARY_DIR="$OM/music_library"

# 완성본을 두는 곳(소유자가 앱에서 열 수 있는 위치 · 저장소에는 올리지 않는다)
export MEAI_VIDEO_OUT="$_meai_repo/video/out"

unset _meai_video_dir _meai_repo
