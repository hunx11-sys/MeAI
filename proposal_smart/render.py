import asyncio,sys
from playwright.async_api import async_playwright

# 자동 맞춤(v8.48) — 본문 틀(.body 545×632pt)보다 내용이 길면 그 쪽만 줄인다.
#   줄이는 것은 **본문 안의 겉싸개(.fit)뿐**이고, 잘라내는 틀(.body)은 손대지 않는다.
#   그래서 아무리 줄여도 발행정보 띠·주석 자리를 침범할 수 없다.
#
#   예전에는 .body 에 CSS zoom 을 걸고 left/top/width/height 를 zoom 으로 나눠 되돌렸다.
#   그런데 zoom 은 크로미엄 128 에서 표준 동작으로 바뀐 속성이라, 그보다 낮은 판에서는
#   되돌리기가 거꾸로 먹어 **틀 자체가 810pt 로 늘어나** 내용이 주석·발행정보 위로 겹쳤다.
#   transform:scale 은 배치에 영향을 주지 않고 판마다 동작이 같아 이런 일이 생기지 않는다.
FIT='''()=>{const GAP=4/0.75, MIN=0.78, out=[];
 document.querySelectorAll('.page').forEach((p,i)=>{const body=p.querySelector('.body'); if(!body) return;
  const fit=body.querySelector(':scope > .fit'); if(!fit) return;
  const B=body.getBoundingClientRect(); const W=B.width, H=B.height; let z=1;
  for(let k=0;k<6;k++){const h=fit.getBoundingClientRect().height; if(h+GAP<=H) break;
   z=Math.max(MIN, Math.floor(z*(H/(h+GAP))*0.995*1000)/1000);
   fit.style.width=(W/z)+'px'; fit.style.transform='scale('+z+')'; if(z<=MIN) break;}
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
        print('RENDERER chromium/'+b.version)   # 어느 판으로 찍었는지 감사 로그에 남긴다(v8.49)
        await pg.goto('file://'+sys.argv[1]); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
        for x in await pg.evaluate(FIT): print(' ',x)
        for x in await pg.evaluate(CHECK): print(' ',x)
        await pg.pdf(path=sys.argv[2],prefer_css_page_size=True,print_background=True); await b.close()
asyncio.run(main())
