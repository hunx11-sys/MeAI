#!/bin/bash
# QA용 렌더: out_qa/s-NN.jpg (96dpi) + z-NN.jpg (160dpi 고해상도)
set -e; cd "$(dirname "$0")"
./render.sh MeAI_guidebook_v4.pptx out_qa 96 >/dev/null
pdftoppm -jpeg -r 160 out_qa/MeAI_guidebook_v4.pdf out_qa/z
ls out_qa/s-*.jpg | wc -l; ls out_qa/z-*.jpg | wc -l
