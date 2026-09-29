#!/bin/bash
# 최종 산출물: 편집용 pptx, PDF(Pretendard 렌더), 이미지판 pptx
set -e
cd "$(dirname "$0")"
NAME=${1:-MeAI_guidebook_v4_CRM_2026.10}
node deck.js "$NAME.pptx"
./render.sh "$NAME.pptx" out_final 144 >/dev/null
node images_deck.js out_final "${NAME}_images.pptx"
cp out_final/$NAME.pdf "$NAME.pdf"
python3 /root/.claude/skills/synced/d9a1f0fe-3185-43c1-bc3d-15404e2e2f87_522276b5-baa1-4dab-b0a1-db621f094787/pptx/scripts/office/validate.py "$NAME.pptx" | tail -1
python3 /root/.claude/skills/synced/d9a1f0fe-3185-43c1-bc3d-15404e2e2f87_522276b5-baa1-4dab-b0a1-db621f094787/pptx/scripts/office/validate.py "${NAME}_images.pptx" | tail -1
ls -la "$NAME.pptx" "${NAME}_images.pptx" "$NAME.pdf"
