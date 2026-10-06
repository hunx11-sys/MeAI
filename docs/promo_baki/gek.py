# 극화체 렌더러 : SVG(음영층·먹선층) → 음영을 펜 빗금으로 바꾸고 먹선을 얹는다
import numpy as np, os, sys
from PIL import Image, ImageFilter
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
def shot(svgs, scale=2):
    """svgs: {name: (w,h,shade_svg, ink_svg)} → name_shade.png, name_ink.png"""
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        for name,(w,h,shade,ink) in svgs.items():
            pg=b.new_page(viewport={'width':w,'height':h},device_scale_factor=scale)
            for kind,body,bg in (('shade',shade,'#fff'),('ink',ink,'transparent')):
                pg.set_content(f'<html><body style="margin:0;background:{bg}"><svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg></body></html>')
                pg.screenshot(path=f'{HERE}/_{name}_{kind}.png',omit_background=(kind=='ink'))
            pg.close()
        b.close()
def hatch(name, out, a1=32, a2=-48, sp=13, mask_from_shade=True):
    sh=np.asarray(Image.open(f'{HERE}/_{name}_shade.png').convert('RGBA')).astype(float)
    alpha_bg = (sh[...,:3].min(-1)>=254.5)   # 순백 = 빛
    d=1-sh[...,:3].mean(-1)/255.0               # 어두움 0..1
    H,W=d.shape; yy,xx=np.mgrid[0:H,0:W].astype(float)
    rng=np.random.default_rng(1)
    wob=np.asarray(Image.fromarray((rng.random((H//40+2,W//40+2))*255).astype('uint8')).resize((W,H),Image.BICUBIC)).astype(float)/255*2.2
    def lines(ang,spacing,width):
        a=np.deg2rad(ang); u=(xx*np.cos(a)+yy*np.sin(a)+wob)%spacing
        return np.abs(u-spacing/2) < width/2
    w1=np.clip((d-.06)/.5,0,1)*sp*.7
    w2=np.clip((d-.42)/.45,0,1)*sp*.60
    w3=np.clip((d-.70)/.25,0,1)*sp*.55
    ink=lines(a1,sp,w1)|lines(a2,sp,w2)|lines(88,sp*1.15,w3)|(d>.9)
    img=np.full((H,W),255,np.uint8); img[ink]=12
    rgb=Image.fromarray(img).convert('RGBA')
    inkl=Image.open(f'{HERE}/_{name}_ink.png').convert('RGBA')
    rgb.alpha_composite(inkl)
    rgb.convert('RGB').save(out)
