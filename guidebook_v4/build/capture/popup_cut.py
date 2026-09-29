# 고객 검색 팝업(cap_popup.mjs 로 css clip x346,y38 dsf2 캡처) → 팝업 상자만 남기고, 안내문과 페이지 번호 사이 빈 띠를 줄인다.
# 결과 좌표: 원점 css (360,40). css y 989.5 아래는 185(검색 전)/183('김' 입력) 만큼 위로 당겨짐.
import numpy as np
from PIL import Image
H='final/hero/'
for name in ['gate_search','gate_search_kim']:
    im=Image.open(H+name+'.png').convert('RGB'); c=im.crop((28,4,1468,2424)); a=np.asarray(c).astype(int)
    flat=(a.std(axis=(1,2))<2.0); best=(0,0); run=None
    for y,f in enumerate(flat):
        if f and run is None: run=y
        if (not f) and run is not None:
            if y-run>best[1]-best[0]: best=(run,y)
            run=None
    cut0,cut1=best[0]+40,best[1]-40
    top=c.crop((0,0,c.width,cut0)); bot=c.crop((0,cut1,c.width,c.height))
    out=Image.new('RGB',(c.width,top.height+bot.height),'white'); out.paste(top,(0,0)); out.paste(bot,(0,top.height)); out.save(H+name+'.png')
