# 소유자 방송교안(owner_v1, 23장)에 '감이 아니라 데이터로 고른 고객' 장을 8장 뒤에 끼운다.
# python splice.py <owner.pptx> <new_slide.pptx> <out.pptx>
import re,sys,os,shutil,subprocess,zipfile,html
SRC,NEW,OUT=sys.argv[1:4]
SK=os.environ.get('PPTX_SCRIPTS','')  # add_slide.py 가 있는 폴더(pptx 스킬 scripts)
W=os.path.join(os.path.dirname(os.path.abspath(OUT)),'_splice'); shutil.rmtree(W,ignore_errors=True)
zipfile.ZipFile(SRC).extractall(W)
def rd(p): return open(os.path.join(W,p),encoding='utf-8').read()
def wr(p,s): open(os.path.join(W,p),'w',encoding='utf-8').write(s)
# 1) 새 빈 장(레이아웃 1)을 8장 뒤에
r=subprocess.run(['python3',SK+'/add_slide.py',W,'slideLayout1.xml','--after','slide8.xml'],capture_output=True,text=True,cwd=SK); print(r.stdout.strip(),r.stderr.strip())
nf=re.search(r'slides/(slide\d+\.xml)',r.stdout).group(1); nn=int(re.search(r'\d+',nf).group(0))
# 2) 내용: 새로 만든 장의 cSld 를 통째로
nz=zipfile.ZipFile(NEW); nsl=nz.read('ppt/slides/slide1.xml').decode('utf-8')
csld=re.search(r'<p:cSld.*?</p:cSld>',nsl,re.S).group(0).replace('<p:cSld name="Slide 1">','<p:cSld>')
x=rd('ppt/slides/'+nf); x=re.sub(r'<p:cSld.*?</p:cSld>',lambda m:csld,x,flags=re.S); wr('ppt/slides/'+nf,x)
# 3) 발표자 노트: 8장 노트 틀을 복사해 본문·쪽번호만 바꿈
nt='notesSlide%d.xml'%nn
tpl=rd('ppt/notesSlides/notesSlide8.xml'); wr('ppt/notesSlides/'+nt,tpl)
wr('ppt/notesSlides/_rels/'+nt+'.rels',rd('ppt/notesSlides/_rels/notesSlide8.xml.rels').replace('slide8.xml',nf))
rel=rd('ppt/slides/_rels/%s.rels'%nf)
rel=rel.replace('</Relationships>','<Relationship Id="rId99" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/%s"/></Relationships>'%nt)
wr('ppt/slides/_rels/%s.rels'%nf,rel)
ct=rd('[Content_Types].xml')
ct=ct.replace('</Types>','<Override PartName="/ppt/notesSlides/%s" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>'%nt)
wr('[Content_Types].xml',ct)
# 순서: 위치 → 파일
pres=rd('ppt/presentation.xml'); prel=rd('ppt/_rels/presentation.xml.rels')
rmap={}
for m in re.finditer(r'<Relationship [^>]*>',prel):
    a=m.group(0); i=re.search(r'Id="([^"]+)"',a).group(1); t=re.search(r'Target="([^"]+)"',a).group(1); rmap[i]=t
order=[os.path.basename(rmap[r]) for r in re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"/>',pres)]
assert order[8]==nf and len(order)==24, order
def notes_of(sf):
    return re.search(r'notesSlides/(notesSlide\d+\.xml)',rd('ppt/slides/_rels/%s.rels'%sf)).group(1)
# 노트 본문 읽기/쓰기(본문 상자 하나 · 글자 덩이 하나)
def nget(p):
    x=rd('ppt/notesSlides/'+p); b=re.findall(r'<p:txBody>.*?</p:txBody>',x,re.S)[0]
    ts=re.findall(r'<a:t>([^<]*)</a:t>',b); assert len(ts)==1,(p,len(ts)); return html.unescape(ts[0])
def nset(p,txt,num=None):
    x=rd('ppt/notesSlides/'+p); b=re.findall(r'<p:txBody>.*?</p:txBody>',x,re.S)[0]
    nb=re.sub(r'<a:t>[^<]*</a:t>',lambda m:'<a:t>'+html.escape(txt,quote=False)+'</a:t>',b,count=1)
    x=x.replace(b,nb)
    if num is not None: x=re.sub(r'(type="slidenum">.*?<a:t>)\d+(</a:t>)',lambda m:m.group(1)+str(num)+m.group(2),x,flags=re.S)
    wr('ppt/notesSlides/'+p,x)
NEWSEC=90
new_text=("[예상 00:00–00:00 · %d초] 데이터로 고른 고객 · 추천 원리와 고객찾기 기본 순서\n"%NEWSEC+
"진행: 8장 끝('다만 추천 고객부터 보시길 권합니다')을 받아 바로 시작. 왼쪽 회색 칸 → 파란 칸 순서로 짚고, '전반적으로 타겟률이 높습니다'에서 파란 띠를 가리키며 또렷이. 비교 수치는 말하지 않음(확인된 수치 없음 · 수치를 쓰려면 5장 발표자 노트 '확인할 것' 8대로 출처를 받은 뒤). 오른쪽 도식은 1→4를 위에서 아래로 손으로 훑기만(순서를 보여 주는 그림이라 막대 길이는 읽지 않음). 목업 고객찾기 목록은 이름순 예시라 기본 순서를 시연으로 보여 주지 않고 이 장의 도식으로만 설명. 마지막 문장 뒤 10장(챕터 칩 '2 고르기')으로 넘김.\n\n"
"이유는 하나입니다. 감이 아니라 데이터로 고른 고객이기 때문입니다.\n"
"감으로 고르면 생각나는 고객, 최근에 연락한 고객부터 찾게 됩니다. 긴 목록을 넘기다 보면 누구에게, 왜, 언제 연락할지를 매번 혼자 정해야 합니다.\n"
"오늘의 추천 고객은 다릅니다. 계약, 동의, 상령일, 생일, CRM 데이터를 매일 밤 계산해서, 지금 연락할 이유가 있는 고객을 AI가 골라 둡니다. 이유도 한 문장으로 붙여 둡니다. 그래서 감으로 고객에게 다가갈 때보다 전반적으로 타겟률이 높습니다.\n"
"고객찾기도 마찬가지입니다. MeAI 고객찾기의 고객 목록은 기본 설정이 보유 고객 중 타겟 가능성이 높은 순서입니다. 맨 위 고객부터 보시면 됩니다.\n"
"추천 카드부터, 고객찾기 목록은 위에서부터. 고르는 일은 데이터가 먼저 해 둡니다. 그럼 고객찾기 화면을 열어 보겠습니다.")
nset(nt,new_text,9)
# 4) 옛 번호 → 새 번호(노트 속 'N장' 참조). 소유자가 지운 옛 20장은 '앞 장'으로.
MAP={9:10,11:12,12:13,13:14,14:15,16:16,17:18,18:19,19:20,22:22}
txt={}
for pos,sf in enumerate(order,1):
    if sf==nf: continue
    p=notes_of(sf); t=nget(p)
    t=re.sub(r"20장 끝\('[^']*'\)을 받아","앞 장 끝을 받아",t) if pos==21 else t
    t=re.sub(r'(?<!\d)(\d{1,2})장(?=[ (에으끝캡첫탭자시의])',lambda m:(str(MAP.get(int(m.group(1)),int(m.group(1))))+'장'),t)
    txt[pos]=(p,t)
def rep(pos,a,b):
    p,t=txt[pos]; assert t.count(a)==1,(pos,a,t.count(a)); txt[pos]=(p,t.replace(a,b))
# 8장: 끝말과 넘김
rep(8,"마지막 문장 뒤 다음 장(챕터 칩 '2 고르기')으로 넘김. '두 번째 걸음, 고르기' 안내는 10장 첫 문장에서 함.","마지막 문장 뒤 다음 장(9장 · 데이터로 고른 고객)으로 넘김. '두 번째 걸음, 고르기' 안내는 10장 첫 문장에서 함.")
rep(8,"오늘 연락할 분이 아니면 그룹에서 직접 고르셔도 됩니다. 그 방법이 다음 순서입니다.","오늘 연락할 분이 아니면 그룹에서 직접 고르셔도 됩니다. 다만 추천 고객부터 보시길 권합니다.")
# 10장(옛 9장): 목록 기본 순서 한 문장
rep(10,"2번, 카드를 누르면 '이 고객 한눈에 보기' 여섯 칸이 펼쳐집니다.","2번, 가운데 고객 목록. 기본 순서가 타겟 가능성 높은 순이라 위에서부터 보시면 됩니다. 카드를 누르면 '이 고객 한눈에 보기' 여섯 칸이 펼쳐집니다.")
rep(10,"검색 줄과 태그 색은 화면으로만.","검색 줄과 태그 색은 화면으로만. ②의 '위에서부터'는 목록을 손으로 위에서 아래로 훑기만(캡처 속 목록 순서와 이름은 예시라 짚지 않음).")
rep(10,"· 85초]","· 95초]")
# 5장: 확인할 것 8 · 말씀 포인트 2줄
rep(5,"목업을 직접 열어 추천 세트 1을 띄우지 않는다(첫 카드가 쓸 수 없는 예시).\n■ 말씀 포인트",
 "목업을 직접 열어 추천 세트 1을 띄우지 않는다(첫 카드가 쓸 수 없는 예시).\n8) 타겟률 비교: 9장 '감으로 고를 때보다 전반적으로 타겟률이 높다'를 받칠 비교 수치가 있는지. 있으면 기간·대상·출처와 함께 받아 9장에 넣고, 없으면 수치 없이 말한다. 고객찾기 목록 기본 순서(보유 고객 중 타겟 가능성 높은 순)를 두 분 설명에 넣을지도 정한다.\n■ 말씀 포인트")
rep(5,"(가이드북 v4 74쪽 자주 묻는 질문)",
 "(가이드북 v4 74쪽 자주 묻는 질문)\n- \"오늘의 추천 고객은 데이터 기반 AI 추천이라, 감으로 고객에게 다가갈 때보다 전반적으로 타겟률이 높습니다.\" (소유자 안내 · 2026.10 · 비교 수치는 두 분 확인 뒤에만)\n- \"고객찾기 목록은 기본 설정이 보유 고객 중 타겟 가능성이 높은 고객 순입니다.\" (소유자 안내 · 2026.10 · 목업 목록은 이름순 예시)")
# 5) 시간표 다시 계산(각 장 초는 그대로, 시작·끝만 이어 붙임)
def mmss(s): return '%02d:%02d'%(s//60,s%60)
allt={}
for pos,sf in enumerate(order,1):
    allt[pos]=(nt,new_text) if sf==nf else txt[pos]
st=0
for pos in range(1,25):
    p,t=allt[pos]; m=re.match(r'\[예상 \d\d:\d\d–\d\d:\d\d · (\d+)초',t); assert m,(pos,t[:40]); sec=int(m.group(1))
    t=t[:m.start()]+'[예상 %s–%s · %d초'%(mmss(st),mmss(st+sec),sec)+t[m.end():]; st+=sec
    nset(p,t,pos)
print('total',mmss(st))
# 6) 화면 쪽번호(오른쪽 아래 고정 글자): 9장 뒤는 +1
for pos,sf in enumerate(order,1):
    if pos<=9: continue
    x=rd('ppt/slides/'+sf); old=pos-1; hit=0
    def fix(m):
        global hit
        sp=m.group(0); off=re.search(r'<a:off x="(\d+)" y="(\d+)"',sp)
        if off and int(off.group(2))>6.3*914400 and re.search(r'<a:t>%d</a:t>'%old,sp):
            hit+=1; return sp.replace('<a:t>%d</a:t>'%old,'<a:t>%d</a:t>'%pos)
        return sp
    x=re.sub(r'<p:sp>.*?</p:sp>',fix,x,flags=re.S); assert hit==1,(pos,sf,hit); wr('ppt/slides/'+sf,x)
# 7) 문서 속성의 장 수
a=rd('docProps/app.xml').replace('<Slides>23</Slides>','<Slides>24</Slides>').replace('<Notes>23</Notes>','<Notes>24</Notes>')
a=a.replace('<vt:lpstr>슬라이드 제목</vt:lpstr></vt:variant><vt:variant><vt:i4>23</vt:i4>','<vt:lpstr>슬라이드 제목</vt:lpstr></vt:variant><vt:variant><vt:i4>24</vt:i4>')
a=a.replace('<vt:vector size="27" baseType="lpstr">','<vt:vector size="28" baseType="lpstr">').replace('</vt:vector></TitlesOfParts>','<vt:lpstr>PowerPoint 프레젠테이션</vt:lpstr></vt:vector></TitlesOfParts>')
wr('docProps/app.xml',a)
if os.path.exists(OUT): os.remove(OUT)
subprocess.run('cd "%s" && zip -qXrD "%s" "[Content_Types].xml" _rels docProps ppt'%(W,os.path.abspath(OUT)),shell=True,check=True)
print('written',OUT)
