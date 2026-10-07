# 메리츠드림 MeAI 장 그림 재료: 화면 조각(둥근 모서리) · 금빛 번짐 · 리포트 휴대폰 합성
# python assets.py <재료폴더>   → hero_home · t1~t5 · glow_*.png  (원본 캡처는 guidebook_v4/captures)
import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
CAP=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','captures')+'/'
OUT=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else 'assets')+'/'; os.makedirs(OUT,exist_ok=True)
def rounded(im, r):
    im=im.convert('RGBA'); m=Image.new('L',im.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,im.width-1,im.height-1),r,fill=255)
    im.putalpha(m); return im
def fit(im, W, H, bg=(255,255,255), valign='bottom'):
    # 비율이 다르면 빈 칸을 흰색으로 채워 W:H 로 맞춤(잘라 내지 않음)
    s=min(W/im.width, H/im.height); im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
    c=Image.new('RGB',(W,H),bg); y=(H-im.height) if valign=='bottom' else (H-im.height)//2; c.paste(im.convert('RGB'),((W-im.width)//2,y)); return c
home=Image.open(CAP+'hero/gb5_gate_full_m.png').convert('RGB')        # 2880x2580 (css 1440x1290, dsf2)
# 1) 표지급 큰 그림: MeAI 홈(인사 ~ 추천 카드 · 넘김 점까지)
hero=home.crop((280,150,2600,2150)); rounded(hero,36).save(OUT+'hero_home.png')
# 2) 다섯 장면 조각 — 세로형(1.70 x 2.15 in). 장면마다 '멀리서도 알아보는 것' 하나만 크게(글자는 장표의 살아 있는 글로)
TW,TH=1200,1518; APP=(247,248,250)
tiles={}
def canvas(bg=APP): return Image.new('RGB',(TW,TH),bg)
def put(c,im,w,y=None):  # 가로 w 로 맞춰 가운데에(y 없으면 세로도 가운데)
    s=w/im.width; im=im.resize((w,round(im.height*s)),Image.LANCZOS)
    if y is None: y=(TH-im.height)//2
    c.paste(im,((TW-w)//2,y)); return y+im.height
# 01 추천 고객 카드 한 장(빨간 'AI 추천 고객' 띠 · 이유 한 문장)
kim=Image.open(CAP+'hero/gb5_card_kim_z.png').convert('RGB')
c=canvas(); put(c,kim,1080); tiles['t1_reco']=c
# 02 홈의 두 입구: 인사 + 일반대화(흰) / 맞춤대화(검정) 카드
hc=Image.open(CAP+'hero/bc3_home_cards.png').convert('RGB')             # 2280x510
c=canvas(); y=put(c,hc.crop((566,18,1123,92)),900,330)                   # '무엇을 도와드릴까요?'
y=put(c,hc.crop((20,230,1123,493)),1080,y+110); put(c,hc.crop((1155,230,2258,493)),1080,y+50); tiles['t2_chat']=c
# 03 보장분석 표: '이 돈이 나와요 | 지금 상태' 두 칸, 미가입 칸을 빨갛게
ab=Image.open(CAP+'hero/bc2_answer_bottom.png').convert('RGB')         # 1720x1078
tb=ab.crop((647,17,1660,410)).copy(); px=tb.load()
for (y0,y1) in [(158,232),(236,310)]:                                  # 미가입 두 줄(지금 상태 칸)
    for yy in range(y0,y1):
        for xx in range(506,1008):
            r,g,b_=px[xx,yy]
            if r<140 and g<140 and b_<140: px[xx,yy]=(222,30,38)       # 글자는 빨강
            elif r>235 and g>235 and b_>235: px[xx,yy]=(253,234,234)   # 바탕은 연한 빨강
c=canvas((255,255,255)); put(c,tb,1140,300); tiles['t3_analysis']=c   # 아래 빈 곳에 '미가입 2건'(장표 글)
# 04 맞춤대화 속 담당 고객(김도윤님 · 동의 79일 남음) — 설계 요청 말풍선은 장표의 글로 얹음
ds=Image.open(CAP+'hero/dream_design_full.png').convert('RGB')         # 2880x1800 (cap_design.mjs)
c=canvas((255,255,255)); put(c,ds.crop((60,222,585,430)),740,170); tiles['t4_design']=c   # 아래에 설계 요청 말풍선(장표 글)
# 05 카카오톡 알림톡 도착(가린 칸 그대로)
kk=Image.open(CAP+'hero/gb5_kakao_clean.png').convert('RGB')           # 374x334
kb=kk.getpixel((4,kk.height//2)); c=canvas(kb); put(c,kk,1160); tiles['t5_report']=c
for k,v in tiles.items(): rounded(v,40).save(OUT+k+'.png')
# 3) 금빛 번짐(투명 PNG) — 큰 그림·큰 숫자 뒤에 깔기
def glow(W,H,cx,cy,r,alpha,name,color=(255,192,0)):
    yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt(((xx-cx)/W)**2+((yy-cy)/H)**2)/r; a=np.clip(np.exp(-d**2*2.6)*alpha,0,1)
    # 가장자리에서 완전히 0이 되게(네모 테두리가 보이지 않게)
    ex=np.clip(np.minimum(xx,W-1-xx)/(W*0.18),0,1); ey=np.clip(np.minimum(yy,H-1-yy)/(H*0.18),0,1); a=a*(ex*ey)**1.5
    arr=np.zeros((H,W,4),dtype=np.uint8); arr[...,0]=color[0]; arr[...,1]=color[1]; arr[...,2]=color[2]; arr[...,3]=(a*255).astype('uint8')
    Image.fromarray(arr,'RGBA').save(OUT+name)
glow(1600,1000,800,500,0.55,0.55,'glow_wide.png')
glow(1000,1000,500,500,0.5,0.6,'glow_round.png')
print('ok', {k:v.size for k,v in tiles.items()}, hero.size)
