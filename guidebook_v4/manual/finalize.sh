#!/bin/bash
# 매뉴얼 최종 산출물: 편집용 pptx, 통이미지판 pptx, PDF(책갈피·누르면 이동하는 링크)
set -e; cd "$(dirname "$0")"
NAME=${1:-MeAI_home_manual}
B=../build
node manual.js "$NAME.pptx"
$B/render.sh "$NAME.pptx" out_final 144 >/dev/null
node $B/images_deck.js out_final "${NAME}_images.pptx"
cp out_final/$NAME.pdf "$NAME.pdf"
python3 $B/nav.py "$NAME.pdf" "$NAME.pptx.nav.json" && rm -f "$NAME.pptx.nav.json"
ls -la "$NAME.pptx" "${NAME}_images.pptx" "$NAME.pdf"
