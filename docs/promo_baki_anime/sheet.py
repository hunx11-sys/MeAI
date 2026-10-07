import sys
from playwright.sync_api import sync_playwright
from PIL import Image
D=sys.argv[1]; ts=[float(x) for x in sys.argv[2].split(',')]
W,H=360,640; sh=Image.new('RGB',(W*min(6,len(ts)),H*((len(ts)+5)//6)),'white')
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium'); pg=b.new_page(viewport={'width':1080,'height':1920})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+D+'/ad.html'); pg.wait_for_timeout(600)
    for k,t in enumerate(ts):
        pg.evaluate('t=>render(t)',t); pg.wait_for_timeout(250); pg.locator('#v').screenshot(path=D+'/_f.png')
        sh.paste(Image.open(D+'/_f.png').resize((W,H)),((k%6)*W,(k//6)*H))
    print(errs[:3])
sh.save(D+'/sheet.jpg',quality=85)
