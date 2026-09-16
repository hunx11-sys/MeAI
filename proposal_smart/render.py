import asyncio,sys
from playwright.async_api import async_playwright
CHECK='''()=>{const o=[];document.querySelectorAll('.page').forEach((p,i)=>{const B=p.querySelector('.body').getBoundingClientRect();
 p.querySelectorAll('.body *').forEach(e=>{const r=e.getBoundingClientRect(); if(!r.width||!r.height)return;
  if(r.bottom>B.bottom+0.5||r.right>B.right+0.5) o.push(`p${i+1} 이탈 .${e.className} ${(e.innerText||'').slice(0,18)}`);
  if(e.children.length===0&&e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflow!=='visible') o.push(`p${i+1} 잘림 .${e.className} ${(e.innerText||'').slice(0,18)}`);});
 const last=[...p.querySelectorAll('.body > *')].pop(); o.push(`p${i+1} 여백 ${Math.round((B.bottom-last.getBoundingClientRect().bottom)*0.75)}pt`);});
 return o.slice(0,25);}'''
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':794,'height':1123})
        await pg.goto('file://'+sys.argv[1]); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
        for x in await pg.evaluate(CHECK): print(' ',x)
        await pg.pdf(path=sys.argv[2],prefer_css_page_size=True,print_background=True); await b.close()
asyncio.run(main())
