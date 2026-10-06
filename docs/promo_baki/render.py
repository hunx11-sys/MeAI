import os,sys
from playwright.sync_api import sync_playwright
D=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium',args=['--allow-file-access-from-files'])
    pg=b.new_page(viewport={'width':1080,'height':1920})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+D+'/ad.html'); pg.wait_for_timeout(800)
    for i in range(900):
        pg.evaluate('t=>render(t)',i/30)
        pg.locator('#v').screenshot(path=D+'/frames/%04d.jpg'%i,type='jpeg',quality=92)
    print('errors',errs[:3]); b.close()
