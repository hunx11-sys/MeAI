// 빌드: node build.js out.pptx [ONLY=1,2,3]
const fs=require('fs');
const X=require('./bcast.js'); const { S, BY, CONTENT, MISS, mmss } = X; const { L, C, W, M, T, R, head, foot } = require('./head.js');
const only=(process.env.ONLY||'').split(',').filter(Boolean).map(Number);
const pres=L.newPres(); pres.title='MeAI 홈 영업가족 방송'; pres.subject='MeAI 홈 활용 방송 대본은 발표자 노트에 있어요';
const list=S.filter(x=>!only.length||only.includes(x.no)).sort((a,b)=>a.no-b.no);
let t=0; const notes=[]; const rows=[['예상 시작','장','예상','화면','진행 메모']];
const shortCue=q=>{ let x=String(q||'').split(/(?<=[.。])\s|\n/)[0].trim(); if(x.length>46) x=x.slice(0,45)+'…'; return x; };
CONTENT.forEach(c=>{ rows.push([mmss(t),String(c.no),c.no===5?`${c.sec}초+`:`${c.sec}초`,c.screen.length>26?c.screen.slice(0,25)+'…':c.screen,shortCue(c.cue)]); t+=c.sec; });
const total=t;
list.forEach(({no,fn})=>{ fn(pres,no); const s=pres._slides[pres._slides.length-1]; const c=BY[no];
  let n; if(c){ let st=0; for(const x of CONTENT){ if(x.no===no) break; st+=x.sec; }
    n=`[예상 ${mmss(st)}–${mmss(st+c.sec)} · ${c.sec}초${no===5?' · 개발자 설명 시간 유동':''}] ${c.screen}\n진행: ${c.cue}\n\n${c.text}`; }
  else n='진행용 큐시트 · 방송 송출 제외';
  s.addNotes(n); notes.push(n); });
// 큐시트
if(!only.length || only.includes(CONTENT.length+1)){ const no=CONTENT.length+1;
  const s=head(pres,{kicker:'진행용 · 송출 제외',title:'진행 큐시트',sub:`예상 약 ${Math.round(total/60)}분 · 개발자 코너(5장)는 시간 유동 · 대본 전문은 각 장의 발표자 노트`});
  const colW=[0.95,0.42,0.72,3.3,W-2*M-5.39];
  const data=rows.map((r,ri)=>r.map(cv=>({text:String(cv),options:{fontFace:L.FONT,fontSize:9.5,bold:ri===0,color:ri===0?C.g700:C.navy,fill:{color:ri===0?C.g100:(r[1]==='4'||r[1]==='5'?C.purple50:C.white)},valign:'middle',margin:[1,4,1,4]}})));
  s.addTable(data,{x:M,y:2.1,w:W-2*M,colW,rowH:0.2,border:{type:'solid',color:C.g200,pt:0.5}});
  foot(s,no); s.addNotes('진행용 큐시트 · 방송 송출 제외'); notes.push('진행용 큐시트 · 방송 송출 제외'); }
const out=process.argv[2]||'test.pptx';
fs.writeFileSync(out.replace(/\.pptx$/,'_notes.json'), JSON.stringify(notes,null,1));
pres.writeFile({fileName:out}).then(()=>{ console.log('written',out,list.length,'slides · 예상',mmss(total)); if(L.MISSING.length) console.log('MISSING IMG',L.MISSING); if(MISS.length) console.log('MISSING ROLE',MISS); });
