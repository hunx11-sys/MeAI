#!/bin/bash
# usage: render.sh deck.pptx prefix [dpi]  -> pptx -> odp (patched autospace) -> pdf -> png
set -e
cd "$(dirname "$0")"
SK=/root/.claude/skills/synced/d9a1f0fe-3185-43c1-bc3d-15404e2e2f87_522276b5-baa1-4dab-b0a1-db621f094787/pptx
f="$1"; pre="${2:-slide}"; dpi="${3:-70}"; base="${f%.pptx}"
rm -rf "tmp_$base"; mkdir -p "tmp_$base"
python3 $SK/scripts/office/soffice.py --headless --convert-to odp --outdir "$PWD/tmp_$base" "$PWD/$f" >/dev/null 2>&1
(cd "tmp_$base" && mkdir x && cd x && unzip -q -o "../$base.odp" && python3 - <<'PY'
import re
for fn in ['styles.xml','content.xml']:
    s=open(fn,encoding='utf-8').read()
    s=s.replace('text-autospace="ideograph-alpha"','text-autospace="none"')
    s=re.sub(r'<style:paragraph-properties(?![^>]*text-autospace)', '<style:paragraph-properties style:text-autospace="none"', s)
    s=re.sub(r'(style:font-name-(?:asian|complex)=")맑은 고딕\d+(")', r'\1맑은 고딕\2', s)
    open(fn,'w',encoding='utf-8').write(s)
PY
rm -f ../p.odp && zip -q -X -r ../p.odp mimetype && zip -q -X -r ../p.odp . -x mimetype)
python3 $SK/scripts/office/soffice.py --headless --convert-to pdf --outdir "$PWD" "$PWD/tmp_$base/p.odp" >/dev/null 2>&1
mv p.pdf "$base.pdf"
rm -f ${pre}-*.png
pdftoppm -png -r $dpi "$base.pdf" $pre
ls ${pre}-*.png | wc -l
