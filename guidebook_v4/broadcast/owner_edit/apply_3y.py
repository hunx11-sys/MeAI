# 방송교안(owner_v3)의 'MeAI 홈 노출 기간' 문구를 1년 → 3년으로 바꾼다(2026.10).
# 화면 5장 아래 안내 · 발표자 노트 5·11장 · 1장 표지 그림(홈 화면 맨 아래 범례 줄이 그림 속 글자라 새로 찍은 그림으로 교체)
# python apply_3y.py <in.pptx> <새 표지 그림.png(2400x2191)> <out.pptx>
import sys,zipfile,re
src,img,out=sys.argv[1:4]
zi=zipfile.ZipFile(src); zo=zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED)
n=0
for it in zi.infolist():
    data=zi.read(it.filename)
    if it.filename in ('ppt/slides/slide5.xml','ppt/notesSlides/notesSlide5.xml','ppt/notesSlides/notesSlide11.xml'):
        s=data.decode('utf-8'); c=s.count('1년'); n+=c
        s=s.replace('동의일로부터 1년 이내','동의일로부터 3년 이내').replace('동의일부터 1년 동안 보입니다','동의일부터 3년 동안 보입니다')
        assert '1년' not in s,(it.filename,'남은 1년'); data=s.encode('utf-8')
    elif it.filename=='ppt/media/image1.png':
        data=open(img,'rb').read()
    zo.writestr(it,data)
zo.close(); print('바꾼 곳',n,'→',out)
