#!/bin/bash
# 방송판 최종 산출물: 편집용 pptx(노트 포함), 통이미지판 pptx(노트 포함), PDF
set -e; cd "$(dirname "$0")"
NAME=${1:-MeAI_broadcast_30min_2026.10}
node bcast.js "$NAME.pptx"
../build/render.sh "$NAME.pptx" out_final 144 >/dev/null
node images_deck_notes.js out_final "${NAME}_notes.json" "${NAME}_images.pptx"
cp out_final/$NAME.pdf "$NAME.pdf"
V=${VALIDATE:-validate.py}
python3 $V "$NAME.pptx" | tail -1; python3 $V "${NAME}_images.pptx" | tail -1
ls -la "$NAME.pptx" "${NAME}_images.pptx" "$NAME.pdf"
