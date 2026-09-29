# -*- coding: utf-8 -*-
"""HTML → PDF 렌더 + 원본 상품설명서에 삽입 + 쪽번호 재부여 + 레이아웃 자동검사.
사용 : python build_pdf.py customer.json 원본상품설명서.pdf 출력.pdf"""
import asyncio, io, json, os, subprocess, sys
BASE=os.path.dirname(os.path.abspath(__file__))
CHECK=open(os.path.join(BASE,'overflow_check.js'),encoding='utf-8').read()

async def html_to_pdf(html_path, pdf_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':794,'height':1123})
        await pg.goto('file://'+os.path.abspath(html_path)); await pg.evaluate('document.fonts.ready')
        await pg.wait_for_timeout(300)
        issues=await pg.evaluate(CHECK)
        await pg.pdf(path=pdf_path, prefer_css_page_size=True, print_background=True)
        await b.close()
    return issues

def merge(orig, insert_pdf, out, insert_after=3, new=6):
    import pdfplumber
    from pypdf import PdfReader
    from pypdf import PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('NG', os.path.join(BASE,'assets','NanumGothic-Regular.ttf')))
    pl=pdfplumber.open(orig); ro=PdfReader(orig); rs=PdfReader(insert_pdf); w=PdfWriter()
    total=len(ro.pages)+new
    def renumber(i):
        p=ro.pages[i]; pp=pl.pages[i]; H=float(pp.height)
        words=[x for x in pp.extract_words() if x['text'].endswith('/%d'%len(ro.pages))]
        if not words: return p
        x=words[0]; orig_no=i+1; new_no=orig_no if orig_no<=insert_after else orig_no+new
        buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=(float(pp.width),H))
        c.setFillColorRGB(1,1,1); c.rect(x['x0']-0.8,H-x['bottom']-1.2,(x['x1']-x['x0'])+2.5,(x['bottom']-x['top'])+2.2,stroke=0,fill=1)
        c.setFillColorRGB(0.259,0.259,0.259); c.setFont('NG',7)
        c.drawString(x['x0'],H-x['bottom']+0.75,'%d/%d'%(new_no,total)); c.save(); buf.seek(0)
        p.merge_page(PdfReader(buf).pages[0]); return p
    for i in range(insert_after): w.add_page(renumber(i))
    for p in rs.pages: w.add_page(p)
    for i in range(insert_after,len(ro.pages)): w.add_page(renumber(i))
    with open(out,'wb') as f: w.write(f)
    return total

if __name__=='__main__':
    cust=sys.argv[1]; orig=sys.argv[2]; out=sys.argv[3]
    os.makedirs(os.path.join(BASE,'out'),exist_ok=True)
    html=os.path.join(BASE,'out','smart.html'); pdf=os.path.join(BASE,'out','smart.pdf')
    subprocess.check_call([sys.executable, os.path.join(BASE,'gen2.py'), cust, html])
    issues=asyncio.run(html_to_pdf(html,pdf))
    if issues:
        print('[레이아웃 경고]'); [print(' ',x) for x in issues]
    from pypdf import PdfReader as _R
    n=merge(orig,pdf,out,json.load(open(cust,encoding='utf-8')).get('insert_after',3),new=len(_R(pdf).pages))
    print('생성 완료 :',out,'총',n,'쪽')
