import sys
from PIL import Image, ImageDraw, ImageFont
out=sys.argv[1]; files=sys.argv[2:]
import os
W=int(os.environ.get('MW',700)); cols=int(os.environ.get('MC',3))
ims=[]
for f in files:
    im=Image.open(f).convert('RGB'); r=W/im.width; ims.append((f.split('/')[-1],im.resize((W,int(im.height*r)))))
rows=[ims[i:i+cols] for i in range(0,len(ims),cols)]
H=sum(max(i.height for _,i in r)+30 for r in rows)
can=Image.new('RGB',(W*cols+10*(cols-1),H),'white'); d=ImageDraw.Draw(can)
try: ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
except: ft=None
y=0
for r in rows:
    x=0
    for n,i in r:
        d.text((x+5,y+3),n,fill='red',font=ft); can.paste(i,(x,y+28)); x+=W+10
    y+=max(i.height for _,i in r)+30
can.save(out); print(can.size)
