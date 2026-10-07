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
# 1) 표지급 큰 그림: MeAI 홈(인사 ~ 추천 카드)
hero=home.crop((280,150,2600,2090)); rounded(hero,36).save(OUT+'hero_home.png')
TW,TH=1500,1154   # 1.3:1 — 큰 화면에서 그림을 크게
tiles={}
# 2) 다섯 장면 조각(3:2)
tiles['t1_reco']=fit(home.crop((300,1150,1820,2165)),TW,TH,valign='center')
gh=Image.open(CAP+'hero/bc3_general_home.png').convert('RGB')         # 2880x1800 일반대화 첫 화면(인사 · 질문 예시)
tiles['t2_chat']=gh.crop((900,250,2580,1543)).resize((TW,TH),Image.LANCZOS)
ab=Image.open(CAP+'hero/bc2_answer_bottom.png').convert('RGB')        # 1720x1078 보장분석 답(표)
tiles['t3_analysis']=fit(ab.crop((110,0,1690,1053)),TW,TH,valign='center')
ds=Image.open(CAP+'hero/dream_design_full.png').convert('RGB')        # 2880x1800 설계 요청(cap_design.mjs)
tiles['t4_design']=fit(ds.crop((940,1010,2540,1800)),TW,TH,valign='center')
# 리포트: 어두운 바탕 위 휴대폰(리포트 생성) + 카톡 도착
bg=Image.new('RGB',(TW,TH),(24,24,24)); g=np.zeros((TH,TW,3)); yy,xx=np.mgrid[0:TH,0:TW]
d=np.sqrt(((xx-TW*0.5)/TW)**2+((yy-TH*0.45)/TH)**2); a=np.clip(1-d/0.75,0,1)**2*0.55
bgarr=np.array(bg,dtype=float); gold=np.array([255,192,0]); bgarr=bgarr*(1-a[...,None])+gold*a[...,None]*0.35+bgarr*a[...,None]*0
bg=Image.fromarray(np.clip(bgarr,0,255).astype('uint8'))
ph=Image.open(CAP+'legacy/report_step3.png').convert('RGBA'); s=1060/ph.height; ph=ph.resize((round(ph.width*s),920),Image.LANCZOS)
kk=Image.open(CAP+'hero/report_kakao_crop.png').convert('RGB'); s=600/kk.width; kk=rounded(kk.resize((600,round(kk.height*s)),Image.LANCZOS),26)
bg.paste(ph,(150,(TH-ph.height)//2),ph); bg.paste(kk,(760,(TH-kk.height)//2),kk)
dr=ImageDraw.Draw(bg); cx=150+ph.width+(760-150-ph.width)//2; dr.polygon([(cx-30,TH//2-42),(cx+34,TH//2),(cx-30,TH//2+42)],fill=(255,192,0))
tiles['t5_report']=bg
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
