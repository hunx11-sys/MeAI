# pptxgenjs 로 만든 파일의 문단 속 중복 <a:pPr> 정리(규격 맞춤). python -I tidy_pptx.py in.pptx out.pptx
import sys,re,zipfile
def one_ppr(xml):
    def fix(m):
        p=m.group(0); i=p.find('<a:r>')
        if i<0: return p
        return p[:i]+re.sub(r'<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>','',p[i:],flags=re.S)
    return re.sub(r'<a:p>.*?</a:p>',fix,xml,flags=re.S)
zi=zipfile.ZipFile(sys.argv[1]); zo=zipfile.ZipFile(sys.argv[2],'w',zipfile.ZIP_DEFLATED)
for it in zi.infolist():
    d=zi.read(it.filename)
    if re.fullmatch(r'ppt/slides/slide\d+\.xml',it.filename): d=one_ppr(d.decode('utf-8')).encode('utf-8')
    zo.writestr(it,d)
zo.close(); print('written',sys.argv[2])
