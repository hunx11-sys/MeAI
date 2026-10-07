# 메리츠드림 행사 PPT(41장)의 MeAI 장(14~19장, 6장)을 dream_meai.js 로 만든 4장으로 바꿔 끼운다.
# python -I splice_dream.py <행사.pptx> <dream_meai.pptx> <out.pptx>     (PPTX_SCRIPTS = pptx 스킬 scripts 폴더)
# - 새 장은 행사 PPT 의 slideLayout3(Main Message Only)로 만들고, 제목은 원래 14장 제목 자리(placeholder)를 그대로 쓴다.
# - 그림·도형·노트(발표 대본)는 dream_meai.pptx 에서 가져온다. 나머지 35장은 손대지 않는다.
import re,sys,os,shutil,subprocess,zipfile,html
SRC,NEW,OUT=sys.argv[1:4]
SK=os.environ.get('PPTX_SCRIPTS','')
FIRST,LAST=14,19      # 바꿀 장(원래 번호)
W=os.path.join(os.path.dirname(os.path.abspath(OUT)),'_splice_dream'); shutil.rmtree(W,ignore_errors=True)
zipfile.ZipFile(SRC).extractall(W)
def rd(p): return open(os.path.join(W,p),encoding='utf-8').read()
def wr(p,s): open(os.path.join(W,p),'w',encoding='utf-8').write(s)
def text(x): return html.unescape(''.join(re.findall(r'<a:t>([^<]*)</a:t>',x)))
def order():
    pres=rd('ppt/presentation.xml'); prel=rd('ppt/_rels/presentation.xml.rels'); rmap={}
    for a in re.findall(r'<Relationship [^>]*>',prel): rmap[re.search(r'Id="([^"]+)"',a).group(1)]=re.search(r'Target="([^"]+)"',a).group(1)
    return [os.path.basename(rmap[r]) for r in re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"/>',pres)]
def title_of(sf):
    t=re.search(r'<p:sp>(?:(?!</p:sp>).)*?<p:ph type="title"/>.*?</p:sp>',rd('ppt/slides/'+sf),re.S); return text(t.group(0)) if t else ''
before=order(); assert len(before)==41,len(before)
# 바꿀 장이 맞는지 제목으로 확인
want={14:'MeAI는 타사에 없는',15:'보장분석부터 제안까지',16:'일하는 방식의 변화',17:'고객 추천 기능',18:'MeAI는 이미 차이',19:'MeAI는 이미 차이'}
for pos,w in want.items(): assert w in title_of(before[pos-1]),(pos,title_of(before[pos-1]))
assert 'MeAI' not in title_of(before[19]) and 'TA의 성장' in title_of(before[19])
# 제목 자리 틀: 원래 14장 제목 placeholder (모양·위치는 레이아웃을 따름)
tsp=re.search(r'<p:sp>(?:(?!</p:sp>).)*?<p:ph type="title"/>.*?</p:sp>',rd('ppt/slides/'+before[FIRST-1]),re.S).group(0)
tsp=re.sub(r'<a:extLst>.*?</a:extLst>','',tsp,count=1,flags=re.S)       # creationId 는 장마다 달라야 하므로 뺌
def title_sp(t):
    body='<a:p><a:r><a:rPr lang="ko-KR" altLang="en-US" dirty="0"/><a:t>%s</a:t></a:r></a:p>'%html.escape(t,quote=False)
    return re.sub(r'(<a:lstStyle/>).*(</p:txBody>)',lambda m:m.group(1)+body+m.group(2),tsp,flags=re.S)
nz=zipfile.ZipFile(NEW)
nslides=sorted([n for n in nz.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)],key=lambda n:int(re.search(r'\d+',os.path.basename(n)).group(0)))
assert len(nslides)==4,nslides
used=set(os.listdir(os.path.join(W,'ppt/notesSlides')))
def free_notes():
    i=1
    while 'notesSlide%d.xml'%i in used: i+=1
    used.add('notesSlide%d.xml'%i); return 'notesSlide%d.xml'%i
NOTES_TMPL=rd('ppt/notesSlides/notesSlide1.xml')
prev=before[FIRST-2]; made=[]; titles=[]
for k,ns in enumerate(nslides,1):
    r=subprocess.run([sys.executable,os.path.join(SK,'add_slide.py'),W,'slideLayout3.xml','--after',prev],capture_output=True,text=True,cwd=SK)
    print(r.stdout.strip(),r.stderr.strip())
    nf=re.search(r'slides/(slide\d+\.xml)',r.stdout).group(1); made.append(nf); prev=nf
    src=nz.read(ns).decode('utf-8'); srel=nz.read(ns.replace('slides/','slides/_rels/')+'.rels').decode('utf-8')
    tree=re.search(r'<p:spTree>(.*)</p:spTree>',src,re.S).group(1)
    head=re.match(r'\s*<p:nvGrpSpPr>.*?</p:grpSpPr>',tree,re.S).group(0); rest=tree[len(head):]
    # 미리보기 제목 상자는 빼고 그 글자를 제목 자리로
    tprev=re.search(r'<p:sp>(?:(?!</p:sp>).)*?name="TITLE_PREVIEW".*?</p:sp>',rest,re.S)
    t=text(tprev.group(0)) if tprev else ''
    if tprev: rest=rest.replace(tprev.group(0),'',1)
    titles.append(t or 'PowerPoint 프레젠테이션')
    body=(title_sp(t) if t else '')+rest
    n=[1]
    def renum(m): n[0]+=1; return '<p:cNvPr id="%d"'%n[0]
    body=re.sub(r'<p:cNvPr id="\d+"',renum,body)
    x=rd('ppt/slides/'+nf)
    x=re.sub(r'<p:spTree>.*</p:spTree>',lambda m:'<p:spTree>'+head+body+'</p:spTree>',x,flags=re.S)    # 바탕은 레이아웃(검정) 그대로
    wr('ppt/slides/'+nf,x)
    # 관계: 그림은 media 로 복사, 레이아웃은 3번, 노트는 새로
    nt=free_notes(); rels=[]
    for a in re.findall(r'<Relationship [^>]*/>',srel):
        rid=re.search(r'Id="([^"]+)"',a).group(1); tgt=re.search(r'Target="([^"]+)"',a).group(1)
        if '/image' in a:
            dst='dream_meai_%d_%s'%(k,os.path.basename(tgt).replace('image-',''))
            open(os.path.join(W,'ppt/media',dst),'wb').write(nz.read('ppt/media/'+os.path.basename(tgt)))
            rels.append(a.replace(tgt,'../media/'+dst))
        elif '/slideLayout' in a: rels.append(a.replace(tgt,'../slideLayouts/slideLayout3.xml'))
        elif '/notesSlide' in a: rels.append(a.replace(tgt,'../notesSlides/'+nt))
        else: raise SystemExit('unknown rel '+a)
    wr('ppt/slides/_rels/%s.rels'%nf,'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(rels)+'</Relationships>')
    # 노트(발표 대본)
    nsrc=nz.read(re.search(r'notesSlides/(notesSlide\d+\.xml)',srel).group(0).replace('notesSlides/','ppt/notesSlides/')).decode('utf-8')
    ntxt=[html.unescape(s) for s in re.findall(r'<a:t>([^<]*)</a:t>',nsrc) if s.strip() and not s.strip().isdigit()]
    paras=''.join('<a:p><a:r><a:rPr lang="ko-KR" altLang="en-US" dirty="0"/><a:t>%s</a:t></a:r></a:p>'%html.escape(p,quote=False) for p in ntxt)
    nx=re.sub(r'(<p:ph type="body"[^>]*/>.*?<a:lstStyle/>).*?(</p:txBody>)',lambda m:m.group(1)+paras+m.group(2),NOTES_TMPL,count=1,flags=re.S)
    wr('ppt/notesSlides/'+nt,nx)
    wr('ppt/notesSlides/_rels/%s.rels'%nt,'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/%s"/><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/></Relationships>'%nf)
    ct=rd('[Content_Types].xml')
    ct=ct.replace('</Types>','<Override PartName="/ppt/notesSlides/%s" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>'%nt)
    if 'Extension="png"' not in ct: ct=ct.replace('</Types>','<Default Extension="png" ContentType="image/png"/></Types>')
    wr('[Content_Types].xml',ct)
# 원래 14~19장을 목록에서 빼고 남은 부속 파일 정리
pres=rd('ppt/presentation.xml'); prel=rd('ppt/_rels/presentation.xml.rels')
for sf in before[FIRST-1:LAST]:
    rid=[re.search(r'Id="([^"]+)"',a).group(1) for a in re.findall(r'<Relationship [^>]*>',prel) if re.search(r'Target="slides/%s"'%re.escape(sf),a)][0]
    pres,c=re.subn(r'<p:sldId id="\d+" r:id="%s"/>'%rid,'',pres); assert c==1
wr('ppt/presentation.xml',pres)
r=subprocess.run([sys.executable,os.path.join(SK,'clean.py'),W],capture_output=True,text=True,cwd=SK); print(r.stdout.strip()[-600:],r.stderr.strip())
after=order(); assert len(after)==39 and after[FIRST-1:FIRST+3]==made,(len(after),after[FIRST-1:FIRST+3],made)
assert after[:FIRST-1]==before[:FIRST-1] and after[FIRST+3:]==before[LAST:]
# 문서 속성(장 수 · 제목 목록)
a=rd('docProps/app.xml'); nn=len(re.findall(r'notesSlide\d+\.xml',' '.join(os.listdir(os.path.join(W,'ppt/notesSlides')))))
a=re.sub(r'<Slides>\d+</Slides>','<Slides>39</Slides>',a); a=re.sub(r'<Notes>\d+</Notes>','<Notes>%d</Notes>'%nn,a)
m=re.search(r'(<vt:lpstr>슬라이드 제목</vt:lpstr></vt:variant><vt:variant><vt:i4>)(\d+)(</vt:i4>)',a)
if m and int(m.group(2))==41:
    a=a[:m.start()]+m.group(1)+'39'+m.group(3)+a[m.end():]
    v=re.search(r'<vt:vector size="(\d+)" baseType="lpstr">(.*?)</vt:vector></TitlesOfParts>',a,re.S)
    items=re.findall(r'<vt:lpstr>.*?</vt:lpstr>',v.group(2),re.S); base=len(items)-41
    items=items[:base+FIRST-1]+['<vt:lpstr>%s</vt:lpstr>'%html.escape(t,quote=False) for t in titles]+items[base+LAST:]
    a=a[:v.start()]+'<vt:vector size="%d" baseType="lpstr">'%len(items)+''.join(items)+'</vt:vector></TitlesOfParts>'+a[v.end():]
wr('docProps/app.xml',a)
if os.path.exists(OUT): os.remove(OUT)
subprocess.run('cd "%s" && zip -qXrD "%s" "[Content_Types].xml" _rels docProps ppt'%(W,os.path.abspath(OUT)),shell=True,check=True)
print('written',OUT,'| new slides',made,'| titles',titles)
