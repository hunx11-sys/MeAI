() => { const out=[];
 document.querySelectorAll('.page').forEach((pg,pi)=>{ const B=pg.querySelector('.body').getBoundingClientRect();
  pg.querySelectorAll('.body *').forEach(e=>{ const r=e.getBoundingClientRect(); if(!r.width||!r.height) return;
   if(r.bottom>B.bottom+0.5||r.right>B.right+0.5||r.left<B.left-0.5) out.push(`p${pi+1} 영역이탈 .${e.className} ${(e.innerText||'').slice(0,20)}`);
   if(e.children.length===0 && e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflow!=='visible') out.push(`p${pi+1} 글자잘림 .${e.className} ${(e.innerText||'').slice(0,20)}`); }); });
 return out.slice(0,40); }
