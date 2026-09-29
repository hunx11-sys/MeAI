#!/bin/sh
# 스마트 제안서 생성 서버 (맥 · 리눅스)
cd "$(dirname "$0")" || exit 1
echo "================================================================"
echo " 스마트 제안서 자동 생성 - 서버 시작"
echo "================================================================"
command -v python3 >/dev/null 2>&1 || { echo "[오류] python3 가 없습니다. Python 3.10 이상을 설치하세요."; exit 1; }
echo "[1/3] 필요한 패키지를 확인합니다 (처음 한 번만 몇 분 걸립니다)"
python3 -m pip install --disable-pip-version-check -q -r requirements.txt || exit 1
echo "[2/3] PDF 렌더용 브라우저를 확인합니다"
python3 -m playwright install chromium || exit 1
echo "[3/3] 서버를 켭니다 — 브라우저로 http://127.0.0.1:8080 에 접속하세요 (종료 Ctrl+C)"
( sleep 4; (command -v open >/dev/null && open http://127.0.0.1:8080/) || (command -v xdg-open >/dev/null && xdg-open http://127.0.0.1:8080/) ) >/dev/null 2>&1 &
exec python3 api.py
