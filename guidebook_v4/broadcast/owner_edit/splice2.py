# 소유자 방송교안 v2(24장)에 '동의가 없어도, 첫 연락 준비는 MeAI가' 장을 12장(동의 상태) 뒤에 끼워 v3(25장)를 만든다.
# python splice2.py <owner_v2.pptx> <new_slide.pptx> <out.pptx>     (PPTX_SCRIPTS = pptx 스킬 scripts 폴더)
import re,sys,os,shutil,subprocess,zipfile,html
SRC,NEW,OUT=sys.argv[1:4]
SK=os.environ.get('PPTX_SCRIPTS','')
POS=13; NEWSEC=110
W=os.path.join(os.path.dirname(os.path.abspath(OUT)),'_splice2'); shutil.rmtree(W,ignore_errors=True)
zipfile.ZipFile(SRC).extractall(W)
def rd(p): return open(os.path.join(W,p),encoding='utf-8').read()
def wr(p,s): open(os.path.join(W,p),'w',encoding='utf-8').write(s)
def order():
    pres=rd('ppt/presentation.xml'); prel=rd('ppt/_rels/presentation.xml.rels'); rmap={}
    for a in re.findall(r'<Relationship [^>]*>',prel): rmap[re.search(r'Id="([^"]+)"',a).group(1)]=re.search(r'Target="([^"]+)"',a).group(1)
    return [os.path.basename(rmap[r]) for r in re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"/>',pres)]
before=order(); assert len(before)==24
def notes_of(sf): return re.search(r'notesSlides/(notesSlide\d+\.xml)',rd('ppt/slides/_rels/%s.rels'%sf)).group(1)
def nget(p):
    x=rd('ppt/notesSlides/'+p); b=re.findall(r'<p:txBody>.*?</p:txBody>',x,re.S)[0]
    ts=re.findall(r'<a:t>([^<]*)</a:t>',b); assert len(ts)==1,(p,len(ts)); return html.unescape(ts[0])
def nset(p,txt,num=None):
    x=rd('ppt/notesSlides/'+p); b=re.findall(r'<p:txBody>.*?</p:txBody>',x,re.S)[0]
    nb=re.sub(r'<a:t>[^<]*</a:t>',lambda m:'<a:t>'+html.escape(txt,quote=False)+'</a:t>',b,count=1); x=x.replace(b,nb)
    if num is not None: x=re.sub(r'(type="slidenum">.*?<a:t>)\d+(</a:t>)',lambda m:m.group(1)+str(num)+m.group(2),x,flags=re.S)
    wr('ppt/notesSlides/'+p,x)
# 기존 장 노트를 먼저 읽어 둠(옛 위치 기준)
old_txt={pos:(notes_of(sf),nget(notes_of(sf))) for pos,sf in enumerate(before,1)}
# 1) 새 빈 장을 12장 뒤에
r=subprocess.run(['python3',SK+'/add_slide.py',W,'slideLayout1.xml','--after',before[POS-2]],capture_output=True,text=True,cwd=SK); print(r.stdout.strip(),r.stderr.strip())
nf=re.search(r'slides/(slide\d+\.xml)',r.stdout).group(1); nn=int(re.search(r'\d+',nf).group(0))
nz=zipfile.ZipFile(NEW); nsl=nz.read('ppt/slides/slide1.xml').decode('utf-8'); nrel=nz.read('ppt/slides/_rels/slide1.xml.rels').decode('utf-8')
csld=re.search(r'<p:cSld.*?</p:cSld>',nsl,re.S).group(0).replace('<p:cSld name="Slide 1">','<p:cSld>')
x=rd('ppt/slides/'+nf); x=re.sub(r'<p:cSld.*?</p:cSld>',lambda m:csld,x,flags=re.S); wr('ppt/slides/'+nf,x)
# 그림: 새 장의 그림을 media 로 옮기고 관계를 새 장 것으로
nt='notesSlide%d.xml'%nn
def fixrel(m):
    a=m.group(0); t=re.search(r'Target="([^"]+)"',a).group(1)
    if '/image' in a:
        src='ppt/media/'+os.path.basename(t); dst='image_s%d_%s'%(nn,os.path.basename(t).replace('image-',''))
        open(os.path.join(W,'ppt/media',dst),'wb').write(nz.read(src)); return a.replace(t,'../media/'+dst)
    if '/slideLayout' in a: return a.replace(t,'../slideLayouts/slideLayout1.xml')
    if '/notesSlide' in a: return a.replace(t,'../notesSlides/'+nt)
    raise SystemExit('unknown rel '+a)
wr('ppt/slides/_rels/%s.rels'%nf,re.sub(r'<Relationship [^>]*/>',fixrel,nrel))
# 노트 틀은 기존 8장 노트를 복사
wr('ppt/notesSlides/'+nt,rd('ppt/notesSlides/'+notes_of(before[7])))
wr('ppt/notesSlides/_rels/'+nt+'.rels',re.sub(r'slide\d+\.xml',nf,rd('ppt/notesSlides/_rels/%s.rels'%notes_of(before[7]))))
ct=rd('[Content_Types].xml'); ct=ct.replace('</Types>','<Override PartName="/ppt/notesSlides/%s" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>'%nt); wr('[Content_Types].xml',ct)
after=order(); assert after[POS-1]==nf and len(after)==25, after
new_text=("[예상 00:00–00:00 · %d초] 동의 전 연락 준비 · 일반대화 최적화 프롬프트 자동 세팅\n"%NEWSEC+
"진행: 12장 끝('이번 달 알림톡 보낼 고객입니다')을 받아 '그럼 동의를 받기 전에는…'으로 시작. 왼쪽 캡처 핀 ①(파란 질문 상자) → ②(성명·연락처 문구) → ③(빨간 [사전조회동의 요청하기]) 순서로 짚고, 오른쪽 위 조건 칩 세 개를 왼쪽부터, 아래 네 칸을 STEP 1→4로. 질문 속 '#암진단비 부족'은 지금 보고 있는 그룹, '#50대'는 고객 나이, '#보유'는 고객 유형에서 자동으로 들어가는 값. 시연 없이 캡처로만 설명(목업 탭은 14장 시연용으로 그대로 둠 · 목업 일반대화 답은 고정 예시라 전송해 보이지 않음). 마지막 문장 뒤 14장('세 번째 걸음, 묻기입니다')으로.\n\n"
"그럼 동의를 받기 전에는 아무것도 못 할까요? 아닙니다. 동의가 없어도 첫 연락 준비는 MeAI가 돕습니다.\n"
"김민수 고객처럼 사전조회동의가 필요한 고객을 고객찾기에서 누르면, 오른쪽에 파란 일반대화 질문이 자동으로 세팅됩니다. 일반대화에 맞춘 최적화 프롬프트입니다.\n"
"1번, 질문에는 고객 그룹, 나이대, 보유·가망·이관이 들어 있습니다. 암진단비 부족, 50대, 보유. 이 조건의 고객에게 보낼 안내 문자를 3~4줄로, 부담스럽지 않은 톤으로 써 달라는 질문입니다.\n"
"2번, 끝에 '고객 성명·연락처는 넣지 말 것'이 붙어 있습니다. 이름 대신 조건으로 묻는 일반대화라서, 보장 내역을 읽는 맞춤대화와 달리 동의 전에도 쓸 수 있습니다.\n"
"누르면 일반대화 입력창에 이 문장이 채워집니다. 전송만 누르면 안내 문자 초안이 나옵니다. 내용을 확인하고 내 말투로 다듬어 연락하세요.\n"
"3번, 연락하면서 [사전조회동의 요청하기]로 동의까지 받으면, 그다음은 맞춤대화입니다.\n"
"동의 전엔 일반대화로 다가가고, 동의 후엔 맞춤대화로 깊게.")
# 2) 노트 속 'N장' 참조: 13 이상은 +1 (새 장이 13장)
txt={}
for pos,(p,t) in old_txt.items():
    t=re.sub(r'(?<!\d)(\d{1,2})장(?=[ (에으끝캡첫탭자시의])',lambda m:str(int(m.group(1))+(1 if int(m.group(1))>=POS else 0))+'장',t)
    txt[pos if pos<POS else pos+1]=(p,t)
txt[POS]=(nt,new_text)
def rep(pos,a,b):
    p,t=txt[pos]; assert t.count(a)==1,(pos,a,t.count(a)); txt[pos]=(p,t.replace(a,b))
rep(12,"다음 장은 '세 번째 걸음, 묻기입니다'로 이어진다.","다음 장(13장 · 동의 전 연락 준비)은 '그럼 동의를 받기 전에는…'으로 이어진다.")
rep(14,"12장 끝을 받아 '세 번째 걸음, 묻기입니다'","13장 끝을 받아 '세 번째 걸음, 묻기입니다'")
rep(21,"고객찾기의 파란 일반대화 추천 질문을 누르면","13장에서 본 고객찾기의 파란 일반대화 추천 질문을 누르면")
# 3) 예상 시각 다시 이어 붙이기
def mmss(s): return '%02d:%02d'%(s//60,s%60)
st=0
for pos in range(1,26):
    p,t=txt[pos]; m=re.match(r'\[예상 \d\d:\d\d–\d\d:\d\d · (\d+)초',t); assert m,(pos,t[:40]); sec=int(m.group(1))
    t=t[:m.start()]+'[예상 %s–%s · %d초'%(mmss(st),mmss(st+sec),sec)+t[m.end():]; st+=sec; nset(p,t,pos)
print('total',mmss(st))
# 4) 화면 쪽번호: 13장 뒤 +1
for pos,sf in enumerate(after,1):
    if pos<=POS: continue
    x=rd('ppt/slides/'+sf); old=pos-1; hit=[0]
    def fix(m):
        sp=m.group(0); off=re.search(r'<a:off x="(\d+)" y="(\d+)"',sp)
        if off and int(off.group(2))>6.3*914400 and re.search(r'<a:t>%d</a:t>'%old,sp): hit[0]+=1; return sp.replace('<a:t>%d</a:t>'%old,'<a:t>%d</a:t>'%pos)
        return sp
    x=re.sub(r'<p:sp>.*?</p:sp>',fix,x,flags=re.S); assert hit[0]==1,(pos,sf,hit); wr('ppt/slides/'+sf,x)
# 5) 문서 속성
a=rd('docProps/app.xml').replace('<Slides>24</Slides>','<Slides>25</Slides>').replace('<Notes>24</Notes>','<Notes>25</Notes>')
a=a.replace('<vt:lpstr>슬라이드 제목</vt:lpstr></vt:variant><vt:variant><vt:i4>24</vt:i4>','<vt:lpstr>슬라이드 제목</vt:lpstr></vt:variant><vt:variant><vt:i4>25</vt:i4>')
a=a.replace('<vt:vector size="28" baseType="lpstr">','<vt:vector size="29" baseType="lpstr">').replace('</vt:vector></TitlesOfParts>','<vt:lpstr>PowerPoint 프레젠테이션</vt:lpstr></vt:vector></TitlesOfParts>')
wr('docProps/app.xml',a)
if os.path.exists(OUT): os.remove(OUT)
subprocess.run('cd "%s" && zip -qXrD "%s" "[Content_Types].xml" _rels docProps ppt'%(W,os.path.abspath(OUT)),shell=True,check=True)
print('written',OUT)
