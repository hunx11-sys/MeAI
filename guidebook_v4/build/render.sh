#!/bin/bash
# 사용: ./render.sh deck.pptx outdir [dpi]  → outdir/deck.pdf, outdir/s-NN.jpg
set -e
PPTX=$(realpath "$1"); OUT=$(realpath -m "$2"); DPI=${3:-96}
mkdir -p "$OUT"; rm -f "$OUT"/s-*.jpg
NAME=$(basename "$PPTX" .pptx)
timeout 600 soffice -env:UserInstallation=file://${LO_PROFILE:-/root/lo_profile} --headless --norestore --convert-to odp --outdir "$OUT" "$PPTX" >/dev/null 2>&1
python3 - "$OUT/$NAME.odp" "$OUT/${NAME}_fixed.odp" <<'PY'
import re,zipfile,sys
src,dst=sys.argv[1],sys.argv[2]
zin=zipfile.ZipFile(src); zout=zipfile.ZipFile(dst,'w')
for item in zin.infolist():
    data=zin.read(item.filename)
    if item.filename in ('content.xml','styles.xml'):
        s=data.decode('utf8')
        s=s.replace('style:text-autospace="ideograph-alpha"','style:text-autospace="none"')
        s=re.sub(r'<style:paragraph-properties(?![^>]*text-autospace)', '<style:paragraph-properties style:text-autospace="none"', s)
        s=re.sub(r'(<style:default-style style:family="(?:paragraph|graphic|presentation)">)(?!<style:paragraph-properties)', r'\1<style:paragraph-properties style:text-autospace="none"/>', s)
        data=s.encode('utf8')
    zout.writestr(item, data, compress_type=zipfile.ZIP_STORED if item.filename=='mimetype' else zipfile.ZIP_DEFLATED)
zout.close()
PY
timeout 900 soffice -env:UserInstallation=file://${LO_PROFILE:-/root/lo_profile} --headless --norestore --convert-to pdf --outdir "$OUT" "$OUT/${NAME}_fixed.odp" >/dev/null 2>&1
mv "$OUT/${NAME}_fixed.pdf" "$OUT/$NAME.pdf"
pdftoppm -jpeg -r "$DPI" "$OUT/$NAME.pdf" "$OUT/s"
ls "$OUT"/s-*.jpg | wc -l
