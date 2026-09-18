import asyncio,sys
from playwright.async_api import async_playwright

# 자동 맞춤(v8.10) — 본문(.body 632pt)보다 내용이 길면 그 쪽만 축소한다.
#   CSS zoom 으로 글자·간격을 같은 비율로 줄이고, 폭은 zoom 을 나눠 545pt 를 그대로 채운다.
#   축소 하한 0.78. 그래도 넘치면 .body 의 overflow:hidden 이 발행정보 띠 침범을 막고 아래 로그에 남는다.
FIT='''()=>{const GAP=4/0.75, MIN=0.78, out=[];
 document.querySelectorAll('.page').forEach((p,i)=>{const body=p.querySelector('.body'); const R0=body.getBoundingClientRect(); const W=R0.width, H=R0.height; let z=1;
  for(let k=0;k<6;k++){const B=body.getBoundingClientRect(); const kids=[...body.children]; if(!kids.length) break;
   const bottom=Math.max(...kids.map(e=>e.getBoundingClientRect().bottom)); const over=bottom+GAP-B.bottom; if(over<=0) break;
   const need=(B.bottom-B.top)/(bottom+GAP-B.top); z=Math.max(MIN, Math.floor(z*need*0.995*1000)/1000);
   body.style.zoom=z; body.style.width=(W/z)+'px'; body.style.height=(H/z)+'px'; if(z<=MIN) break;}   /* 폭·높이를 zoom 으로 나눠 지면 위 크기는 545×632pt 그대로 */
  if(z<1) out.push(`p${i+1} 축소 ${z}`);});
 return out;}'''
CHECK='''()=>{const o=[];document.querySelectorAll('.page').forEach((p,i)=>{const B=p.querySelector('.body').getBoundingClientRect();
 p.querySelectorAll('.body *').forEach(e=>{const r=e.getBoundingClientRect(); if(!r.width||!r.height)return;
  if(r.bottom>B.bottom+0.5||r.right>B.right+0.5) o.push(`p${i+1} 이탈 .${e.className} ${(e.innerText||'').slice(0,18)}`);
  if(e.children.length===0&&e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflow!=='visible'&&getComputedStyle(e).textOverflow!=='ellipsis') o.push(`p${i+1} 잘림 .${e.className} ${(e.innerText||'').slice(0,18)}`);});
 const kids=[...p.querryAll?[]:p.querySelectorAll('.body > *')]; const last=Math.max(...kids.map(e=>e.getBoundingClientRect().bottom)); o.push(`p${i+1} 여백 ${Math.round((B.bottom-last)*0.75)}pt`);});
 return o.slice(0,30);}'''
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':794,'height':1123})
        await pg.goto('file://'+sys.argv[1]); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
        for x in await pg.evaluate(FIT): print(' ',x)
        for x in await pg.evaluate(CHECK): print(' ',x)
        await pg.pdf(path=sys.argv[2],prefer_css_page_size=True,print_background=True); await b.close()
asyncio.run(main())
