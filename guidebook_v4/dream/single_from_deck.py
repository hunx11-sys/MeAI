# 행사 PPT 의 서식(마스터·레이아웃·쪽번호·테마)을 그대로 지닌 '한 장짜리' 파일을 만든다.
# 붙여넣을 때 어떤 붙여넣기 옵션을 골라도 행사 PPT 와 같은 모양이 되게 하려는 것.
# python -I single_from_deck.py <행사 원본.pptx> <한 장.pptx(pptxgenjs)> <out.pptx>   (PPTX_SCRIPTS = pptx 스킬 scripts 폴더)
import re,sys,os,shutil,subprocess,zipfile,html
SRC,NEW,OUT=sys.argv[1:4]
SK=os.environ.get('PPTX_SCRIPTS','')
HERE=os.path.dirname(os.path.abspath(__file__))
TMP=os.path.join(os.path.dirname(os.path.abspath(OUT)),'_single_tmp.pptx')
# 1) splice_dream.py 로 원래 14~19장 자리에 이 한 장을 끼운다(레이아웃3 · 제목 자리 · 노트까지 같은 방식)
r=subprocess.run([sys.executable,'-I',os.path.join(HERE,'splice_dream.py'),SRC,NEW,TMP],capture_output=True,text=True,env=dict(os.environ))
print(r.stdout.strip()[-300:],r.stderr.strip()[-500:])
assert r.returncode==0
W=os.path.join(os.path.dirname(os.path.abspath(OUT)),'_single'); shutil.rmtree(W,ignore_errors=True)
zipfile.ZipFile(TMP).extractall(W)
def rd(p): return open(os.path.join(W,p),encoding='utf-8').read()
def wr(p,s): open(os.path.join(W,p),'w',encoding='utf-8').write(s)
# 2) 14번째 장만 남기고 목록에서 뺀 뒤 정리
pres=rd('ppt/presentation.xml'); ids=re.findall(r'<p:sldId id="\d+" r:id="rId\d+"/>',pres)
keep=ids[13]; pres=re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>','<p:sldIdLst>'+keep+'</p:sldIdLst>',pres,flags=re.S); wr('ppt/presentation.xml',pres)
r=subprocess.run([sys.executable,os.path.join(SK,'clean.py'),W],capture_output=True,text=True,cwd=SK); print(r.stdout.strip()[-200:],r.stderr.strip())
# 3) 문서 속성(장 1 · 노트 1 · 제목 목록 1)
a=rd('docProps/app.xml'); nn=len([f for f in os.listdir(os.path.join(W,'ppt/notesSlides')) if f.endswith('.xml')])
a=re.sub(r'<Slides>\d+</Slides>','<Slides>1</Slides>',a); a=re.sub(r'<Notes>\d+</Notes>','<Notes>%d</Notes>'%nn,a)
m=re.search(r'(<vt:lpstr>슬라이드 제목</vt:lpstr></vt:variant><vt:variant><vt:i4>)(\d+)(</vt:i4>)',a)
if m:
    n=int(m.group(2)); a=a[:m.start()]+m.group(1)+'1'+m.group(3)+a[m.end():]
    v=re.search(r'<vt:vector size="(\d+)" baseType="lpstr">(.*?)</vt:vector></TitlesOfParts>',a,re.S)
    items=re.findall(r'<vt:lpstr>.*?</vt:lpstr>',v.group(2),re.S); items=items[:len(items)-n]+[items[len(items)-n+13]]
    a=a[:v.start()]+'<vt:vector size="%d" baseType="lpstr">'%len(items)+''.join(items)+'</vt:vector></TitlesOfParts>'+a[v.end():]
wr('docProps/app.xml',a)
if os.path.exists(OUT): os.remove(OUT)
subprocess.run('cd "%s" && zip -qXrD "%s" "[Content_Types].xml" _rels docProps ppt'%(W,os.path.abspath(OUT)),shell=True,check=True)
os.remove(TMP); print('written',OUT)
