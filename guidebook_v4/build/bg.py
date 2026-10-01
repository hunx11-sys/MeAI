# 배경 그라데이션 이미지 만들기: 표지·파트 나눔·마무리·본문(아주 옅게). python3 bg.py → bg/*.jpg
import numpy as np
from PIL import Image
import os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'bg'); os.makedirs(D,exist_ok=True)
def hexrgb(h): return np.array([int(h[i:i+2],16) for i in (0,2,4)],dtype=np.float64)
def make(name,w,h,stops,glows,angle=0.35,q=92):
    y,x=np.mgrid[0:h,0:w]; u=x/(w-1); v=y/(h-1)
    t=np.clip(u*(1-angle)+v*angle,0,1)          # 비스듬한 선형 그라데이션
    img=np.zeros((h,w,3))
    ps=[p for p,_ in stops]; cs=[hexrgb(c) for _,c in stops]
    for k in range(3): img[...,k]=np.interp(t,ps,[c[k] for c in cs])
    ar=w/h
    for cx,cy,r,col,a in glows:                 # 부드러운 빛 번짐
        d=np.sqrt(((u-cx)*ar)**2+(v-cy)**2)/r; m=a*np.exp(-d**2*2.2)
        img=img*(1-m[...,None])+hexrgb(col)*m[...,None]
    img+=np.random.default_rng(7).normal(0,0.6,img.shape)   # 띠 무늬(banding) 방지
    Image.fromarray(np.clip(img,0,255).astype(np.uint8)).save(os.path.join(D,name+'.jpg'),quality=q,optimize=True)
W,H=2400,1350
make('cover',W,H,[(0,'0B1428'),(0.55,'0F2147'),(1,'132B5E')],[(0.88,0.08,0.75,'2F6FEA',0.55),(0.05,1.0,0.6,'4B3FC9',0.22),(0.55,0.55,0.9,'0A1630',0.15)])
make('divider',W,H,[(0,'1650C8'),(0.5,'2A72EE'),(1,'3E86F7')],[(0.9,0.05,0.7,'7FB2FF',0.35),(0.0,1.0,0.7,'0E3FA8',0.45),(0.6,0.9,0.5,'5468F0',0.18)])
make('closing',W,H,[(0,'123F B5'.replace(' ','')),(0.55,'2468E8'),(1,'3A82F6')],[(0.92,0.1,0.75,'8DBBFF',0.38),(0.05,0.95,0.7,'2A2E9E',0.35)])
make('page',1600,900,[(0,'FFFFFF'),(0.7,'FCFDFF'),(1,'F3F7FE')],[(1.0,0.0,0.55,'E6F0FF',0.55),(0.0,1.05,0.5,'F1EEFF',0.35)],angle=0.4,q=90)
for f in sorted(os.listdir(D)): print(f, os.path.getsize(os.path.join(D,f))//1024,'KB')
