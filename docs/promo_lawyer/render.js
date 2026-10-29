// 장면 그리기 : node render.js <프레임폴더> [초=18] [fps=30]  →  0000.jpg …
const {chromium}=require('playwright'),path=require('path');
(async()=>{const [dir,T='18',F='30']=process.argv.slice(2);const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.join(__dirname,'ad.html'));await p.evaluate(()=>window.ready);
for(let i=0;i<Math.round(T*F);i++){await p.evaluate(t=>render(t),i/F);
  await p.locator('#v').screenshot({path:path.join(dir,String(i).padStart(4,'0')+'.jpg'),type:'jpeg',quality:92})}
await b.close()})();
