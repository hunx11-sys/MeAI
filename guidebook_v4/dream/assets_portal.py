# 메리츠드림 '기존 영업포탈 vs MeAI' 장 그림 재료
# python assets_portal.py <재료폴더>
#  - 영업포탈 실제 화면(captures/portal, 이름·사번·계약번호는 가린 것)을 흐리고 어둡게(옛 방식)
#  - MeAI 맞춤대화 한 화면(captures/hero/term_pc_full.png)
import sys, os
from PIL import Image, ImageEnhance, ImageDraw
HERE=os.path.dirname(os.path.abspath(__file__)); CAP=os.path.join(HERE,'..','captures')
OUT=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else 'assets'); os.makedirs(OUT,exist_ok=True)
def rounded(im,r):
    im=im.convert('RGBA'); m=Image.new('L',im.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,im.width-1,im.height-1),r,fill=255); im.putalpha(m); return im
for n in ['L1_customer','L8_contract','L9_claim','L4_product','L6_design_cover']:
    im=Image.open(os.path.join(CAP,'portal',n+'.png')).convert('RGB')
    im=ImageEnhance.Color(im).enhance(0.2); im=ImageEnhance.Brightness(im).enhance(0.48)
    d=ImageDraw.Draw(im); d.rectangle((0,0,im.width-1,im.height-1),outline=(90,90,90),width=3)
    im.save(os.path.join(OUT,n+'_dim.png'))
m=Image.open(os.path.join(CAP,'hero','term_pc_full.png')).convert('RGB')   # 2880x1800 맞춤대화(보장분석 답)
rounded(m,40).save(os.path.join(OUT,'meai_one_screen.png'))
print('ok',OUT)
