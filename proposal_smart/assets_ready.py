# -*- coding: utf-8 -*-
"""assets/ 준비 — 글꼴·로고가 없는 PC(사내 노트북에 zip 으로 받은 경우 등)에서도 생성이 멈추지 않게 한다.

· 글꼴 : assets/ 에 나눔고딕이 없으면 ga_assets/ 의 같은 파일(SIL OFL 무료 글꼴)을 복사한다.
         예전에는 fetch_assets.py 로 인터넷에서 받아야 했고, 없으면 build_pdf 가 「Can't open file …NanumGothic-Regular.ttf」 로 멈췄다.
· 로고 : assets/logo.png 가 없고 설계서 PDF 가 주어지면 그 PDF 1~2쪽에서 가로로 가장 긴 그림(메리츠 로고)을 꺼낸다.
         fetch_assets.py 는 poppler(pdfimages)가 필요해 윈도우에서 안 됐다 — 여기서는 이미 설치되는 pymupdf 로 뽑는다.
"""
import os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
AS = os.path.join(BASE, 'assets')
GA = os.path.join(BASE, 'ga_assets')
FONTS = ('NanumGothic-Regular.ttf', 'NanumGothic-Bold.ttf', 'NanumGothic-ExtraBold.ttf')


def fonts():
    os.makedirs(AS, exist_ok=True)
    for f in FONTS:
        dst = os.path.join(AS, f)
        if not os.path.exists(dst) and os.path.exists(os.path.join(GA, f)):
            shutil.copyfile(os.path.join(GA, f), dst)


def logo(src_pdf):
    dst = os.path.join(AS, 'logo.png')
    if os.path.exists(dst) or not src_pdf or not os.path.exists(src_pdf):
        return
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    from PIL import Image
    import io
    doc = fitz.open(src_pdf)
    best = None
    for pno in range(min(2, len(doc))):
        for im in doc[pno].get_images(full=True):
            xref, smask, w, h = im[0], im[1], im[2], im[3]
            if w < 200 or w < h * 2:                      # 로고는 가로로 긴 그림
                continue
            if best is None or w > best[2]:
                best = (xref, smask, w)
    if not best:
        return
    xref, smask, _ = best
    base = Image.open(io.BytesIO(doc.extract_image(xref)['image'])).convert('RGB')
    if smask:
        mk = Image.open(io.BytesIO(doc.extract_image(smask)['image'])).convert('L')
        if mk.size == base.size:
            base.putalpha(mk)
    base.save(dst)


def ensure(src_pdf=None):
    """글꼴은 늘, 로고는 설계서가 있을 때 준비한다. 실패해도 생성은 계속한다(로고 없이 나온다)."""
    try:
        fonts()
    except Exception as e:
        print('  (글꼴 준비 실패 : %s)' % e)
    try:
        logo(src_pdf)
    except Exception as e:
        print('  (로고 추출 실패 : %s)' % e)
