// MeAI 홈 영업가족 방송 PPT — 대본·화면 글자는 content.json(장별), 배치는 이 파일.
// 사용: node bcast.js out.pptx   (CAPTURES 로 캡처 폴더, CONTENT 로 대본 파일 지정 가능)
const path = require('path'); const fs = require('fs');
const K = require('./head.js'); const { L, C, W, H, M, T, R, foot, head, badge, pin, item, bar, note2, src, chipX } = K;

const F = process.env.CAPTURES || path.join(__dirname,'..','captures');
const HERO=n=>`${F}/hero/${n}.png`, AG=(d,n)=>`${F}/${d}/${n}.png`, LEG=n=>`${F}/legacy/${n}.png`;
const CONTENT = JSON.parse(fs.readFileSync(process.env.CONTENT || path.join(__dirname,'content.json'),'utf8'));
const BY = {}; CONTENT.forEach(s=>BY[s.no]=s);
const MISS=[];
// 장 no 의 화면 글자 role → 글자
function B(no, role, dflt){ const s=BY[no]; const b=s && s.copy.blocks.find(x=>x.role===role); if(!b){ if(dflt===undefined) MISS.push(`${no}:${role}`); return dflt===undefined?`[${role}]`:dflt; } return b.text; }
function CP(no){ return BY[no].copy; }
const mmss = t=>`${String(Math.floor(t/60)).padStart(2,'0')}:${String(t%60).padStart(2,'0')}`;
const S=[]; // {no, fn}
const add=(no,fn)=>S.push({no,fn});

// 1 표지
add(1,(pres,no)=>{ const s=pres.addSlide(); s.background={color:C.navy};
  chipX(s,{x:M+0.2,y:0.95,text:B(1,'chip'),fill:'2B3340',color:'FFFFFF',size:14});
  T(s,B(1,'title-line1')+'\n'+B(1,'title-line2'),{x:M+0.2,y:1.65,w:6.6,h:2.2,fontSize:46,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.1});
  T(s,B(1,'sub'),{x:M+0.2,y:4.0,w:6.4,h:0.5,fontSize:22,bold:true,color:C.blue100,valign:'middle'});
  T(s,B(1,'tagline'),{x:M+0.2,y:4.6,w:6.4,h:0.45,fontSize:18,color:'FFFFFF',transparency:25,valign:'middle'});
  T(s,B(1,'byline'),{x:M+0.2,y:5.95,w:6,h:0.35,fontSize:14,color:'FFFFFF',transparency:30});
  L.img(s,HERO('bc2_gate_full_s3_masked'),{x:7.25,y:0.8,w:5.5,h:5.6,valign:'middle',align:'right'});
  T(s,B(1,'caption'),{x:7.25,y:6.45,w:5.5,h:0.3,fontSize:12,color:'FFFFFF',transparency:35,align:'right',valign:'middle'});
  foot(s,no,true); });

// 2 순서
add(2,(pres,no)=>{ const c=CP(2); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub});
  const y0=2.15; R(s,{x:M,y:y0,w:W-2*M,h:0.9,fill:C.g50,line:null,radius:0.14});
  let x=M+0.3; const lw=chipX(s,{x,y:y0+0.24,text:B(2,'lead-label'),fill:C.navy,color:'FFFFFF',size:14,h:0.42}); x+=lw+0.3;
  T(s,B(2,'lead1-title'),{x,y:y0,w:2.3,h:0.9,fontSize:19,bold:true,color:C.navy,valign:'middle'}); x+=L.textW(B(2,'lead1-title'),19)+0.25;
  T(s,'›',{x,y:y0,w:0.35,h:0.9,fontSize:24,color:C.g400,align:'center',valign:'middle'}); x+=0.5;
  T(s,B(2,'lead2-title'),{x,y:y0,w:2.3,h:0.9,fontSize:19,bold:true,color:C.purple,valign:'middle'}); x+=L.textW(B(2,'lead2-title'),19)+0.3;
  s.addText([{text:B(2,'lead2-guest'),options:{bold:true,color:C.navy,fontSize:16,fontFace:L.FONT,breakLine:true}},{text:B(2,'lead2-desc'),options:{color:C.g600,fontSize:14,fontFace:L.FONT}}],{x,y:y0,w:W-M-x-0.2,h:0.9,isTextBox:true,margin:0,valign:'middle'});
  T(s,B(2,'steps-label'),{x:M,y:3.2,w:4,h:0.36,fontSize:14,bold:true,color:C.g600,valign:'middle'});
  const gap=0.22, cw=(W-2*M-gap*3)/4;
  [1,2,3,4].forEach((k,i)=>{ const x=M+i*(cw+gap), y=3.62, h=2.1, on=k===3;
    R(s,{x,y,w:cw,h,fill:on?C.blue:C.white,line:on?null:C.g200,radius:0.16,shadow:!on});
    T(s,B(2,`item${k}-title`),{x:x+0.3,y:y+0.2,w:cw-0.5,h:0.55,fontSize:24,bold:true,color:on?'FFFFFF':C.navy,valign:'middle'});
    T(s,B(2,`item${k}-tag`),{x:x+0.3,y:y+0.75,w:cw-0.5,h:0.36,fontSize:14,bold:true,color:on?C.blue100:C.blue,valign:'middle'});
    T(s,B(2,`item${k}-desc`),{x:x+0.3,y:y+1.15,w:cw-0.5,h:0.8,fontSize:14.5,color:on?'FFFFFF':C.g600,valign:'top',lineSpacingMultiple:1.2});
    if(on){ const p=B(2,'item3-pill',''); if(p){ const pw=L.textW(p,14)+0.45; R(s,{x:x+cw-pw-0.2,y:y-0.2,w:pw,h:0.4,fill:'FFFFFF',line:C.blue,lw:1.25,radius:0.2}); T(s,p,{x:x+cw-pw-0.2,y:y-0.2,w:pw,h:0.4,fontSize:14,bold:true,color:C.blue,align:'center',valign:'middle'}); } } });
  bar(s,{y:5.95,h:0.85,label:B(2,'bar-label'),text:B(2,'bar-text'),size:20});
  foot(s,no); });

// 3 왜 MeAI 홈인가
add(3,(pres,no)=>{ const c=CP(3); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub});
  const gap=0.22, cw=(W-2*M-gap*2)/3, y=2.2, h=2.45;
  [[B(3,'item1-title'),B(3,'item1-desc')],[B(3,'item2-title'),B(3,'item2-desc')]].forEach((it,i)=>{ const x=M+i*(cw+gap); R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.16});
    const m=it[0].match(/^([\d.]+%)\s*(.*)$/)||[null,it[0],''];
    s.addText([{text:m[1],options:{fontSize:72,bold:true,color:C.red,fontFace:L.FONT}},{text:'  '+m[2],options:{fontSize:24,bold:true,color:C.red,fontFace:L.FONT}}],{x:x+0.35,y:y+0.2,w:cw-0.5,h:1.3,isTextBox:true,margin:0,valign:'middle'});
    T(s,it[1],{x:x+0.35,y:y+1.6,w:cw-0.5,h:0.5,fontSize:19,bold:true,color:C.navy,valign:'middle'}); });
  const x3=M+2*(cw+gap); R(s,{x:x3,y,w:cw,h,fill:C.navy,line:null,radius:0.16});
  T(s,B(3,'item3-title'),{x:x3+0.4,y:y+0.3,w:cw-0.7,h:1.15,fontSize:24,bold:true,color:'FFFFFF',valign:'middle',lineSpacingMultiple:1.25});
  T(s,B(3,'item3-desc'),{x:x3+0.4,y:y+1.5,w:cw-0.7,h:0.8,fontSize:15,color:C.blue100,valign:'top',lineSpacingMultiple:1.25});
  T(s,B(3,'source-1'),{x:M,y:y+h+0.05,w:W-2*M,h:0.28,fontSize:12,color:C.g500,align:'right',valign:'middle'});
  const by=5.1, bh=1.2; R(s,{x:M,y:by,w:W-2*M,h:bh,fill:C.blue50,line:null,radius:0.16});
  T(s,B(3,'bar-label'),{x:M+0.35,y:by,w:2.2,h:bh,fontSize:18,bold:true,color:C.blue,valign:'middle'});
  const bw=(W-2*M-2.8)/2;
  [1,2].forEach((k,i)=>{ const bx=M+2.6+i*bw; T(s,B(3,`bar-item${k}-title`),{x:bx,y:by+0.18,w:bw-0.2,h:0.5,fontSize:23,bold:true,color:C.navy,valign:'middle'}); T(s,B(3,`bar-item${k}-desc`),{x:bx,y:by+0.66,w:bw-0.2,h:0.4,fontSize:15.5,color:C.g700,valign:'middle'}); });
  src(s,B(3,'source-2'),6.45);
  foot(s,no); });


// 4 개발자 초대
add(4,(pres,no)=>{ const c=CP(4); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,kcolor:C.purple});
  const cw=3.15, gap=0.22, y=2.2, h=2.55;
  [B(4,'card1'),B(4,'card2')].forEach((t,i)=>{ const x=M+i*(cw+gap); const [nm,team]=t.split(' · ');
    R(s,{x,y,w:cw,h,fill:C.white,line:C.g200,radius:0.2,shadow:true});
    s.addShape('ellipse',{x:x+cw/2-0.5,y:y+0.3,w:1.0,h:1.0,fill:{color:i?C.blue:C.purple},line:{color:'FFFFFF',width:0}});
    T(s,nm.slice(0,1),{x:x+cw/2-0.5,y:y+0.3,w:1.0,h:1.0,fontSize:30,bold:true,color:'FFFFFF',align:'center',valign:'middle'});
    T(s,nm,{x,y:y+1.42,w:cw,h:0.58,fontSize:30,bold:true,color:C.navy,align:'center',valign:'middle'});
    T(s,team||'',{x,y:y+1.98,w:cw,h:0.4,fontSize:17,bold:true,color:i?C.blue:C.purple,align:'center',valign:'middle'}); });
  R(s,{x:M,y:4.95,w:2*cw+gap,h:0.62,fill:C.blue50,line:null,radius:0.14});
  T(s,B(4,'intro'),{x:M+0.25,y:4.95,w:2*cw+gap-0.4,h:0.62,fontSize:15.5,bold:true,color:C.navy,valign:'middle'});
  const x=M+2*cw+gap+0.45, w=W-M-x; R(s,{x,y,w,h:3.37,fill:C.navy,line:null,radius:0.2});
  T(s,B(4,'q-label'),{x:x+0.35,y:y+0.22,w:w-0.6,h:0.42,fontSize:16,bold:true,color:C.blue100,valign:'middle'});
  [1,2,3].forEach((k,i)=>{ const qy=y+0.75+i*0.86; T(s,B(4,`q${k}-title`),{x:x+0.35,y:qy,w:w-0.6,h:0.4,fontSize:18,bold:true,color:'FFFFFF',valign:'middle'});
    T(s,B(4,`q${k}-desc`).replace(/\n/g,' '),{x:x+0.35,y:qy+0.38,w:w-0.6,h:0.38,fontSize:14,color:C.blue100,valign:'top'}); });
  bar(s,{y:5.95,h:0.8,text:B(4,'bar-text'),size:19,tone:'blue'});
  foot(s,no); });

// 5 MeAI 홈이 움직이는 방식
add(5,(pres,no)=>{ const c=CP(5); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,kcolor:C.purple});
  const x=M, w=6.75, y0=2.1, rh=0.74, gp=0.1;
  [1,2,3,4,5].forEach((k,i)=>{ const y=y0+i*(rh+gp), hi=k===4, last=k===5;
    R(s,{x:x+0.62,y,w:w-0.62,h:rh,fill:hi?C.blue50:C.white,line:hi?null:C.g200,radius:0.14});
    badge(s,x,y+(rh-0.46)/2,k,{color:C.navy});
    if(i<4) s.addShape('line',{x:x+0.23,y:y+rh/2+0.25,w:0,h:rh+gp-0.5,line:{color:C.blue,width:1.5,endArrowType:'triangle'}});
    const tt=B(5,`step${k}-title`), pill=B(5,`step${k}-pill`,'');
    T(s,tt,{x:x+0.85,y:y+0.06,w:w-1.1,h:0.36,fontSize:17,bold:true,color:last?C.blue:C.navy,valign:'middle'});
    if(pill) chipX(s,{x:x+0.85+L.textW(tt,17)+0.2,y:y+0.08,text:pill,fill:C.purple50,color:C.purple,size:12,h:0.3});
    T(s,B(5,`step${k}-desc`),{x:x+0.85,y:y+0.4,w:w-1.1,h:0.3,fontSize:14,color:C.g600,valign:'middle'}); });
  const gx=7.65, gw=W-M-gx; const g=L.img(s,HERO('bc2_gate_reco_s3'),{x:gx,y:2.1,w:gw,h:2.35,valign:'top',align:'right'});
  pin(s,g,1030,962,3,{dsf:1,d:0.4}); pin(s,g,24,300,4,{dsf:1,d:0.4});
  T(s,B(5,'caption'),{x:gx,y:g.y+g.h+0.05,w:gw,h:0.28,fontSize:12,color:C.g500,align:'right',valign:'middle'});
  const qy=4.95; R(s,{x:gx,y:qy,w:gw,h:1.35,fill:C.navy,line:null,radius:0.16});
  T(s,B(5,'q-label'),{x:gx+0.3,y:qy+0.12,w:gw-0.5,h:0.34,fontSize:14,bold:true,color:C.blue100,valign:'middle'});
  T(s,[B(5,'q1'),B(5,'q2'),B(5,'q3')].join('\n'),{x:gx+0.3,y:qy+0.45,w:gw-0.5,h:0.85,fontSize:14.5,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.15});
  T(s,B(5,'note'),{x:M,y:6.38,w:W-2*M,h:0.28,fontSize:12.5,color:C.g700,valign:'middle'});
  src(s,B(5,'source'),6.66);
  foot(s,no); });


// 6 MeAI 홈 가는 문
add(6,(pres,no)=>{ const c=CP(6); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:0});
  const g=L.img(s,HERO('bc2_portal_masked'),{x:M,y:2.1,w:7.6,h:4.1,valign:'top',align:'left'});
  const k=g.scale; s.addShape('roundRect',{x:g.x+1005*k,y:g.y+598*k,w:133*k,h:146*k,fill:{type:'none'},line:{color:C.blue,width:3},rectRadius:0.05});
  R(s,{x:M,y:g.y+g.h+0.12,w:7.6,h:0.42,fill:C.g100,line:null,radius:0.12}); T(s,B(6,'bar-text'),{x:M+0.25,y:g.y+g.h+0.12,w:7.2,h:0.42,fontSize:15,color:C.g700,valign:'middle'});
  const x=8.5, w=W-M-x;
  T(s,B(6,'group1-title'),{x,y:2.05,w,h:0.42,fontSize:19,bold:true,color:C.blue,valign:'middle'});
  chipX(s,{x,y:2.52,text:B(6,'pill'),fill:C.blue50,color:C.blue,size:14,h:0.38});
  const row=(t,d,y)=>{ T(s,t,{x,y,w,h:0.38,fontSize:16.5,bold:true,color:C.navy,valign:'middle'}); if(d) T(s,d,{x:x+L.textW(t,16.5)+0.15,y,w:w-L.textW(t,16.5)-0.15,h:0.38,fontSize:14,color:C.g600,valign:'middle'}); };
  row(B(6,'item3-title'),B(6,'item3-desc'),3.02);
  R(s,{x:x-0.1,y:3.48,w:w+0.1,h:1.62,fill:C.blue50,line:null,radius:0.14});
  T(s,B(6,'item4-title'),{x:x+0.1,y:3.55,w:w-0.2,h:0.38,fontSize:16.5,bold:true,color:C.blue,valign:'middle'});
  T(s,B(6,'item4-desc'),{x:x+0.1,y:3.93,w:w-0.2,h:0.55,fontSize:14,color:C.g700,valign:'top',lineSpacingMultiple:1.1});
  T(s,B(6,'item4-key'),{x:x+0.1,y:4.5,w:w-0.2,h:0.55,fontSize:14.5,bold:true,color:C.navy,valign:'top',lineSpacingMultiple:1.1});
  row(B(6,'item5-title'),'',5.2);
  T(s,B(6,'group2-title'),{x,y:5.68,w,h:0.36,fontSize:16,bold:true,color:C.g600,valign:'middle'});
  T(s,B(6,'group2-desc'),{x,y:6.02,w,h:0.52,fontSize:13.5,color:C.g600,valign:'top',lineSpacingMultiple:1.1});
  T(s,B(6,'note'),{x:M,y:6.72,w:7.6,h:0.26,fontSize:12,color:C.g500,valign:'middle'});
  foot(s,no); });

// 7 MeAI 홈 한 화면
add(7,(pres,no)=>{ const c=CP(7); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:0});
  const g=L.img(s,HERO('bc2_gate_s3_top'),{x:M,y:2.05,w:6.2,h:4.62,valign:'top',align:'left'});
  const o={dsf:2}; pin(s,g,60,120,1,o); pin(s,g,60,266,2,o); pin(s,g,60,491,3,o); pin(s,g,60,601,4,o); pin(s,g,880,52,5,o);
  const k=2*g.scale; const box=(x1,y1,x2,y2)=>s.addShape('roundRect',{x:g.x+x1*k,y:g.y+y1*k,w:(x2-x1)*k,h:(y2-y1)*k,fill:{type:'none'},line:{color:C.blue,width:1.75},rectRadius:0.05});
  box(938,16,1290,62); box(685,1043,755,1067); box(1028,144,1288,180);
  const x=6.95, w=W-M-x; const ys=[2.05,2.85,3.9,4.7,5.75];
  [1,2,3,4,5].forEach((n,i)=>{ const d=B(7,`item${n}-desc`); item(s,{x,y:ys[i],w,n,title:B(7,`item${n}-title`),desc:d,ts:19,ds:14.5,dh:d.includes('\n')?0.58:0.34}); });
  note2(s,M,g.y+g.h+0.02,6.2,B(7,'note'),'left');
  foot(s,no); });

// 8 추천 카드 한 장(김민수)
add(8,(pres,no)=>{ const c=CP(8); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:0});
  const g=L.img(s,HERO('fix_reco3_card1'),{x:1.05,y:2.1,w:3.4,h:3.45,valign:'top',align:'left'});
  const ph=818, pw=712; const py=f=>g.y+g.h*f;
  [[1,0.11],[2,0.24],[3,0.64],[4,0.725],[5,0.89]].forEach(([n,f])=>badge(s,g.x-0.48,py(f)-0.2,n,{d:0.4,size:14}));
  const bx=(x1,y1,x2,y2)=>s.addShape('roundRect',{x:g.x+g.w*x1,y:g.y+g.h*y1,w:g.w*(x2-x1),h:g.h*(y2-y1),fill:{type:'none'},line:{color:C.blue,width:1.75},rectRadius:0.04});
  bx(0.08,0.19,0.93,0.305); bx(0.06,0.695,0.38,0.755);
  const L1=4.75, L2=9.05, cw1=4.1, cw2=W-M-L2;
  item(s,{x:L1,y:2.1,w:cw1,n:1,title:B(8,'item1-title').replace(/^①\s*/,''),desc:B(8,'item1-desc'),ts:18,ds:14,dh:0.6});
  item(s,{x:L1,y:3.3,w:cw1,n:2,title:B(8,'item2-title').replace(/^②\s*/,''),desc:B(8,'item2-desc'),ts:18,ds:14,dh:0.6});
  item(s,{x:L1,y:4.5,w:cw1,n:3,title:B(8,'item3-title').replace(/^③\s*/,''),ts:18});
  const pills=CP(8).blocks.filter(b=>b.role==='pill').map(b=>b.text);
  const pc=[[C.blue50,C.blue],[C.red50,C.red],[C.purple50,C.purple]]; let px=L1+0.1;
  pills.forEach((t,i)=>{ px+=chipX(s,{x:px,y:4.98,text:t.replace(/\s*\(.*\)$/,''),fill:pc[i][0],color:pc[i][1],size:11.5,h:0.32})+0.08; });
  T(s,B(8,'item3-desc'),{x:L1+0.1,y:5.36,w:cw1+0.4,h:0.3,fontSize:13.5,color:C.g600,valign:'middle'});
  item(s,{x:L2,y:2.1,w:cw2,n:4,title:B(8,'item4-title').replace(/^④\s*/,''),desc:B(8,'item4-desc'),ts:18,ds:14,dh:0.6,color:C.red});
  item(s,{x:L2,y:3.3,w:cw2,n:5,title:B(8,'item5-title').replace(/^⑤\s*/,''),desc:B(8,'item5-desc'),ts:18,ds:14,dh:0.6});
  R(s,{x:L2,y:4.5,w:cw2,h:0.95,fill:C.g100,line:null,radius:0.14}); T(s,B(8,'note-right'),{x:L2+0.25,y:4.5,w:cw2-0.4,h:0.95,fontSize:14,color:C.g700,valign:'middle',lineSpacingMultiple:1.15});
  bar(s,{y:5.78,h:0.62,label:B(8,'bar-label'),text:B(8,'bar-text'),size:16.5});
  s.addText([{text:B(8,'repeat-chip')+'   ',options:{bold:true,color:C.g600,fontSize:13,fontFace:L.FONT}},{text:B(8,'repeat-line'),options:{bold:true,color:C.blue,fontSize:13.5,fontFace:L.FONT}}],{x:M,y:6.47,w:8.2,h:0.3,isTextBox:true,margin:0,valign:'middle'});
  T(s,B(8,'caption'),{x:8.9,y:6.47,w:W-M-8.9,h:0.3,fontSize:11,color:C.g500,align:'right',valign:'middle'});
  foot(s,no); });


// 9 고객찾기 세 단(김민수)
add(9,(pres,no)=>{ const c=CP(9); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:1});
  const g=L.img(s,HERO('bc2_find_km_masked'),{x:M,y:2.08,w:6.7,h:4.19,valign:'top',align:'left'});
  const px=(fx)=>g.x+g.w*fx, py=(fy)=>g.y+g.h*fy;
  const zone=(x1,y1,x2,y2,dash)=>s.addShape('roundRect',{x:px(x1),y:py(y1),w:g.w*(x2-x1),h:g.h*(y2-y1),fill:{type:'none'},line:{color:C.blue,width:dash?1.25:2,dashType:dash?'dash':'solid'},rectRadius:0.05});
  zone(0.01,0.07,0.20,0.92); zone(0.228,0.22,0.662,0.70); zone(0.70,0.09,0.99,0.54); zone(0.24,0.45,0.65,0.68,true);
  badge(s,px(0.10)-0.21,py(0.07)-0.21,1,{d:0.42,size:15}); badge(s,px(0.228)-0.21,py(0.22)-0.21,2,{d:0.42,size:15}); badge(s,px(0.70)-0.21,py(0.09)-0.21,3,{d:0.42,size:15});
  s.addShape('line',{x:px(0.71),y:py(0.475),w:g.w*0.275,h:0,line:{color:C.red,width:2.5}});
  let xx=M; xx+=chipX(s,{x:xx,y:g.y+g.h+0.12,text:B(9,'pill'),fill:C.purple50,color:C.purple,size:12.5,h:0.36})+0.2;
  T(s,B(9,'note'),{x:xx,y:g.y+g.h+0.12,w:6.9-(xx-M),h:0.36,fontSize:14,color:C.g600,valign:'middle'});
  const x=7.6, w=W-M-x;
  [1,2,3].forEach((n,i)=>item(s,{x,y:2.08+i*1.0,w,n,title:B(9,`item${n}-title`).replace(/^[①②③]\s*/,''),desc:B(9,`item${n}-desc`),ts:18,ds:13.5,dh:0.5}));
  const by=5.12, bh=1.6; R(s,{x,y:by,w,h:bh,fill:C.g50,line:null,radius:0.14});
  T(s,B(9,'box-title'),{x:x+0.25,y:by+0.1,w:w-0.4,h:0.36,fontSize:15,bold:true,color:C.navy,valign:'middle'});
  T(s,[1,2,3,4].map(k=>B(9,`box-row${k}`)).join('\n'),{x:x+0.25,y:by+0.46,w:w-0.4,h:1.1,fontSize:13,color:C.g700,valign:'top',lineSpacingMultiple:1.18});
  T(s,B(9,'caption'),{x:M,y:6.78,w:W-2*M,h:0.24,fontSize:11,color:C.g500,valign:'middle'});
  foot(s,no); });

// 10 그룹 설명 = 화법
add(10,(pres,no)=>{ const c=CP(10); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:1});
  const lx=M, lw=7.05;
  const lg=B(10,'pin-legend').replace(/[①②]/g,'').split(/\s{2,}/).map(t=>t.trim()).filter(Boolean);
  s.addShape('line',{x:lx,y:2.24,w:0.45,h:0,line:{color:C.blue,width:3}}); T(s,lg[0]||'',{x:lx+0.55,y:2.08,w:2.2,h:0.32,fontSize:14,bold:true,color:C.g700,valign:'middle'});
  R(s,{x:lx+2.6,y:2.12,w:0.45,h:0.24,fill:'FFE066',line:null,radius:0.04}); T(s,lg[1]||'',{x:lx+3.15,y:2.08,w:3,h:0.32,fontSize:14,bold:true,color:C.g700,valign:'middle'});
  const one=(file,y,marks,lab,txt)=>{ const g=L.img(s,AG('find010',file),{x:lx,y,w:lw,h:1.3,valign:'top',align:'left',shadow:false});
    s.addShape('roundRect',{x:g.x,y:g.y,w:g.w,h:g.h,fill:{type:'none'},line:{color:C.g300,width:1},rectRadius:0.06}); const k=g.scale;
    marks.u.forEach(([x1,x2,yy])=>s.addShape('line',{x:g.x+x1*k,y:g.y+yy*k,w:(x2-x1)*k,h:0,line:{color:C.blue,width:2.5}}));
    marks.h.forEach(([x1,x2,y1,y2])=>s.addShape('rect',{x:g.x+x1*k,y:g.y+y1*k,w:(x2-x1)*k,h:(y2-y1)*k,fill:{color:'FFE066',transparency:55},line:{color:'FFE066',width:0}}));
    const by=g.y+g.h+0.08; R(s,{x:lx,y:by,w:lw,h:0.5,fill:C.blue50,line:null,radius:0.12});
    const cw=chipX(s,{x:lx+0.15,y:by+0.08,text:lab,fill:C.blue,color:'FFFFFF',size:12.5,h:0.34});
    T(s,txt,{x:lx+0.3+cw,y:by,w:lw-cw-0.45,h:0.5,fontSize:17,bold:true,color:C.navy,valign:'middle'}); return by+0.5; };
  let y=one('11_group_brain_header',2.45,{u:[[32,591,154]],h:[[600,1245,117,152],[28,279,165,200]]},B(10,'bubble1-label'),B(10,'bubble1-text'));
  one('21_group_birthday_header',y+0.2,{u:[[31,367,154]],h:[[375,1261,117,152],[28,123,165,200]]},B(10,'bubble2-label'),B(10,'bubble2-text'));
  const x=7.95, w=W-M-x;
  T(s,B(10,'when-head'),{x,y:2.05,w,h:0.4,fontSize:19,bold:true,color:C.navy,valign:'middle'});
  [1,2,3,4].forEach((k,i)=>{ const ry=2.48+i*0.8, on=k===1; R(s,{x,y:ry,w,h:0.74,fill:C.white,line:on?C.purple:C.g200,lw:on?1.5:0.75,radius:0.12});
    const chip=B(10,`when${k}-chip`); const cwid=chipX(s,{x:x+0.12,y:ry+0.15,text:chip,fill:on?C.purple50:C.g100,color:on?C.purple:C.g700,size:12,h:0.34});
    T(s,B(10,`when${k}-title`),{x:x+0.25+Math.max(cwid,1.15),y:ry+0.04,w:w-1.5,h:0.3,fontSize:15,bold:true,color:C.navy,valign:'middle'});
    T(s,B(10,`when${k}-desc`).replace(/\n/g,' · '),{x:x+0.25+Math.max(cwid,1.15),y:ry+0.33,w:w-1.5,h:0.4,fontSize:11.5,lineSpacingMultiple:1.0,color:C.g600,valign:'middle'}); });
  R(s,{x,y:5.72,w,h:0.62,fill:C.g50,line:null,radius:0.12});
  T(s,B(10,'tip').replace(/\n/g,' ')+'\n'+B(10,'multi').replace(/\n/g,' '),{x:x+0.2,y:5.72,w:w-0.3,h:0.62,fontSize:11.5,color:C.g700,valign:'middle',lineSpacingMultiple:1.15});
  T(s,B(10,'note'),{x:M,y:6.4,w:W-2*M,h:0.26,fontSize:12,color:C.g600,valign:'middle'});
  T(s,B(10,'caption'),{x:M,y:6.68,w:W-2*M,h:0.24,fontSize:11,color:C.g500,valign:'middle'});
  foot(s,no); });

// 11 동의 상태
add(11,(pres,no)=>{ const c=CP(11); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:1});
  const rows=[[1,C.blue,C.blue50],[2,C.red,C.red50],[3,C.g600,C.g100]];
  rows.forEach(([k,col,bg],i)=>{ const y=2.15+i*1.12, h=1.0;
    R(s,{x:M,y,w:W-2*M,h,fill:C.white,line:C.g200,radius:0.14});
    chipX(s,{x:M+0.25,y:y+h/2-0.22,text:B(11,`row${k}-chip`),fill:bg,color:col,size:15,h:0.44});
    if(k===1){ const g=L.img(s,AG('gate020','31_row_normal_zoom'),{x:2.75,y:y+0.12,w:5.9,h:0.76,valign:'middle',align:'left',shadow:false}); pin(s,g,1110,117,1,{dsf:1,d:0.34}); }
    if(k===2){ const g=L.img(s,HERO('fix_c_consent_request_btn'),{x:2.75,y:y+0.12,w:3.1,h:0.76,valign:'middle',align:'left',shadow:false}); pin(s,g,-40,129,2,{dsf:1,d:0.34,color:C.red});
      T(s,'→',{x:g.x+g.w+0.05,y,w:0.35,h,fontSize:20,color:C.g400,align:'center',valign:'middle'});
      L.img(s,HERO('bc2_consent_popup'),{x:g.x+g.w+0.45,y:y+0.1,w:2.0,h:0.8,valign:'middle',align:'left',shadow:false}); }
    if(k===3){ const g=L.img(s,AG('gate020','34_row_revoked_zoom'),{x:2.75,y:y+0.12,w:5.9,h:0.76,valign:'middle',align:'left',shadow:false}); pin(s,g,1110,117,3,{dsf:1,d:0.34,color:C.g600}); }
    T(s,B(11,`row${k}-title`),{x:8.9,y:y+0.1,w:W-M-8.9-0.15,h:0.42,fontSize:17,bold:true,color:C.navy,valign:'middle'});
    const d=B(11,`row${k}-desc`); const parts=d.split('\n');
    s.addText(parts.map((t,j)=>({text:t,options:{fontSize:13.5,color:(j===1&&k===2)?C.blue:C.g600,bold:(j===1&&k===2),fontFace:L.FONT,breakLine:j<parts.length-1}})),{x:8.9,y:y+0.5,w:W-M-8.9-0.15,h:0.45,isTextBox:true,margin:0,valign:'top'}); });
  T(s,B(11,'note'),{x:M,y:5.5,w:W-2*M,h:0.3,fontSize:14,color:C.g700,valign:'middle'});
  bar(s,{y:5.9,h:0.72,label:B(11,'bar-label'),text:B(11,'bar-text'),size:16.5});
  T(s,B(11,'caption'),{x:M,y:6.7,w:W-2*M,h:0.26,fontSize:11,color:C.g500,align:'right',valign:'middle'});
  foot(s,no); });


// 12 질문은 고르는 것
add(12,(pres,no)=>{ const c=CP(12); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:2});
  const gap=0.24, cw=(W-2*M-gap*3)/4, cy=2.9, ch=2.1;
  const col=(i,title,pill,file,pins,desc)=>{ const x=M+i*(cw+gap);
    R(s,{x,y:2.05,w:cw,h:3.72,fill:C.g50,line:null,radius:0.16});
    T(s,title,{x:x+0.2,y:2.12,w:cw-0.3,h:0.38,fontSize:17,bold:true,color:C.navy,valign:'middle'});
    if(pill) chipX(s,{x:x+0.2,y:2.52,text:pill,fill:C.blue50,color:C.blue,size:11.5,h:0.3});
    let g=null; if(file){ g=L.img(s,file,{x:x+0.15,y:cy,w:cw-0.3,h:ch,valign:'middle',align:'center',shadow:false}); pins.forEach(([px,py,n])=>pin(s,g,px,py,n,{dsf:1,d:0.34,color:C.red})); }
    T(s,desc,{x:x+0.2,y:5.05,w:cw-0.3,h:0.68,fontSize:12.5,color:C.g700,valign:'top',lineSpacingMultiple:1.12}); return {x,g}; };
  col(0,B(12,'item1-title'),B(12,'item1-pill'),HERO('bc2_general_home'),[[60,585,1]],B(12,'item1-desc'));
  col(1,B(12,'item2-title'),B(12,'item2-pill'),HERO('bc2_find_right_top'),[[1240,220,2]],B(12,'item2-desc'));
  col(2,B(12,'item3-title'),B(12,'item3-pill'),HERO('bc2_mo_examples'),[[40,215,3]],B(12,'item3-desc'));
  const c4=col(3,B(12,'item4-title'),'',null,[],B(12,'item4-desc'));
  const g4=L.img(s,AG('term','35_pc_message_actions'),{x:c4.x+0.4,y:3.0,w:cw-0.8,h:1.1,valign:'middle',align:'center',shadow:false}); pin(s,g4,275,18,4,{dsf:1,d:0.34,color:C.red});
  T(s,B(12,'item4-note'),{x:c4.x+0.2,y:4.25,w:cw-0.4,h:0.6,fontSize:12,color:C.g600,valign:'top',lineSpacingMultiple:1.12});
  const by=5.88, bh=0.8; R(s,{x:M,y:by,w:W-2*M,h:bh,fill:C.purple50,line:null,radius:0.16});
  T(s,B(12,'bar-label'),{x:M+0.3,y:by,w:2.6,h:bh,fontSize:14,bold:true,color:C.purple,valign:'middle'});
  const vals=[11.99,17.02,27.79], mx=27.79; ['bar-1','bar-2','bar-3'].forEach((r,i)=>{ const bx=M+2.85+i*2.05, hh=0.5*vals[i]/mx;
    R(s,{x:bx,y:by+bh-0.1-hh,w:0.34,h:hh,fill:i===2?C.purple:'B9A8F5',line:null,radius:0.04});
    T(s,B(12,r),{x:bx+0.42,y:by+0.1,w:i===2?1.95:1.62,h:bh-0.2,fontSize:13,bold:i===2,color:C.navy,valign:'bottom'}); });
  T(s,B(12,'bar-big'),{x:W-M-2.75,y:by+0.02,w:1.35,h:bh-0.04,fontSize:32,bold:true,color:C.purple,valign:'middle'});
  T(s,B(12,'bar-sub'),{x:W-M-1.5,y:by,w:1.35,h:bh,fontSize:12.5,color:C.g700,valign:'middle'});
  T(s,B(12,'source'),{x:M,y:6.72,w:9.2,h:0.26,fontSize:11,color:C.g500,valign:'middle'});
  T(s,B(12,'caption'),{x:W-M-3.2,y:6.72,w:3.2,h:0.26,fontSize:11,color:C.g500,align:'right',valign:'middle'});
  foot(s,no); });

// 13 보장분석 해줘
add(13,(pres,no)=>{ const c=CP(13); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:2});
  const g=L.img(s,HERO('custom_start_crop'),{x:M,y:1.85,w:5.4,h:2.95,valign:'top',align:'left'});
  [[390,516,1],[390,640,2],[390,722,3],[1500,910,4]].forEach(([px,py,n])=>pin(s,g,px,py,n,{dsf:1,d:0.36}));
  const k=g.scale; s.addShape('roundRect',{x:g.x+1555*k,y:g.y+865*k,w:235*k,h:90*k,fill:{type:'none'},line:{color:C.red,width:2},rectRadius:0.04});
  const x=6.35, w=W-M-x;
  chipX(s,{x,y:1.85,text:B(13,'section-a'),fill:C.navy,color:'FFFFFF',size:13,h:0.36});
  [1,2,3,4].forEach((n,i)=>{ const iy=2.32+i*0.62, d=B(13,`item${n}-desc`);
    badge(s,x,iy+0.03,n,{d:0.36,size:13}); T(s,B(13,`item${n}-title`),{x:x+0.48,y:iy,w:2.35,h:0.42,fontSize:15.5,bold:true,color:C.navy,valign:'middle'});
    T(s,d,{x:x+2.85,y:iy-0.04,w:w-2.85,h:0.5,fontSize:12,color:C.g600,valign:'middle',lineSpacingMultiple:1.0}); });
  R(s,{x,y:4.8,w,h:0.62,fill:C.g50,line:null,radius:0.12}); T(s,B(13,'note'),{x:x+0.2,y:4.8,w:w-0.3,h:0.62,fontSize:12,color:C.g700,valign:'middle',lineSpacingMultiple:1.1});
  const g2=L.img(s,HERO('bc2_custom_input'),{x:M,y:5.2,w:5.4,h:1.1,valign:'top',align:'left'});
  const k2=g2.scale; s.addShape('roundRect',{x:g2.x+40*k2,y:g2.y+83*k2,w:238*k2,h:67*k2,fill:{type:'none'},line:{color:C.red,width:2},rectRadius:0.04});
  pin(s,g2,300,116,5,{dsf:1,d:0.34}); pin(s,g2,1420,185,6,{dsf:1,d:0.34});
  chipX(s,{x,y:5.55,text:B(13,'section-b'),fill:C.navy,color:'FFFFFF',size:13,h:0.36});
  [5,6].forEach((n,i)=>{ const iy=5.98+i*0.4; badge(s,x,iy+0.02,n,{d:0.32,size:12}); T(s,B(13,`item${n}-title`),{x:x+0.42,y:iy,w:2.4,h:0.36,fontSize:14.5,bold:true,color:C.navy,valign:'middle'});
    T(s,B(13,`item${n}-desc`),{x:x+2.85,y:iy,w:w-2.85,h:0.36,fontSize:12.5,color:C.g600,valign:'middle'}); });
  T(s,B(13,'bar-label')+'  '+B(13,'bar-text'),{x:M,y:6.42,w:5.6,h:0.5,fontSize:12,bold:true,color:C.purple,valign:'middle',lineSpacingMultiple:1.05});
  T(s,B(13,'caption')+' · '+B(13,'source'),{x:M,y:6.84,w:W-2*M,h:0.22,fontSize:10,color:C.g500,valign:'middle'});
  foot(s,no); });

// 14 답 읽는 순서
add(14,(pres,no)=>{ const c=CP(14); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:2});
  T(s,B(14,'caption'),{x:M,y:2.05,w:8,h:0.3,fontSize:13,color:C.g600,valign:'middle'});
  const ga=L.img(s,HERO('bc2_answer_top'),{x:M,y:2.4,w:6.0,h:2.95,valign:'top',align:'left'});
  const gb=L.img(s,HERO('fix_answer_bottom'),{x:6.8,y:2.4,w:W-M-6.8,h:2.95,valign:'top',align:'left'});
  const bx=(g,x1,y1,x2,y2,col)=>s.addShape('roundRect',{x:g.x+x1*g.scale,y:g.y+y1*g.scale,w:(x2-x1)*g.scale,h:(y2-y1)*g.scale,fill:{type:'none'},line:{color:col,width:2},rectRadius:0.04});
  bx(ga,60,470,1680,820,C.green); bx(gb,1150,172,1658,330,C.red); bx(gb,60,610,560,675,C.blue);
  pin(s,ga,60,280,1,{dsf:1,d:0.36,color:C.navy}); pin(s,ga,60,500,2,{dsf:1,d:0.36,color:C.green}); pin(s,gb,1110,250,3,{dsf:1,d:0.36,color:C.red}); pin(s,gb,60,640,4,{dsf:1,d:0.36,color:C.blue});
  const cols=[C.navy,C.green,C.red,C.blue], gap=0.18, cw=(W-2*M-gap*3)/4, y=5.5;
  [1,2,3,4].forEach((n,i)=>{ const x=M+i*(cw+gap); R(s,{x,y,w:cw,h:0.68,fill:C.white,line:cols[i],lw:1.25,radius:0.12});
    badge(s,x+0.12,y+0.13,n,{d:0.4,color:cols[i],size:14});
    T(s,B(14,`item${n}-title`),{x:x+0.62,y:y+0.05,w:cw-0.7,h:0.32,fontSize:14.5,bold:true,color:C.navy,valign:'middle'});
    T(s,B(14,`item${n}-desc`),{x:x+0.62,y:y+0.36,w:cw-0.7,h:0.28,fontSize:12,color:C.g600,valign:'middle'});
    if(i<3) T(s,'›',{x:x+cw-0.02,y,w:gap+0.04,h:0.68,fontSize:18,color:C.g400,align:'center',valign:'middle'}); });
  R(s,{x:M,y:6.3,w:8.3,h:0.5,fill:C.blue50,line:null,radius:0.12});
  s.addText([{text:B(14,'pill')+'  ',options:{bold:true,color:C.blue,fontSize:13.5,fontFace:L.FONT}},{text:B(14,'pill-desc'),options:{color:C.g700,fontSize:12,fontFace:L.FONT}}],{x:M+0.2,y:6.3,w:8.0,h:0.5,isTextBox:true,margin:0,valign:'middle'});
  T(s,B(14,'note')+'\n'+B(14,'source'),{x:9.05,y:6.3,w:W-M-9.05,h:0.5,fontSize:10.5,color:C.g500,align:'right',valign:'middle'});
  foot(s,no); });


// 15 직접 묻는 공식
add(15,(pres,no)=>{ const c=CP(15); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:2});
  const ws=[3.05,2.75,2.75,3.0], pg=0.19; let x=M; const y=2.08, h=1.32;
  const sty=[[C.blue50,C.blue,null],[C.white,C.navy,C.navy],[C.white,C.g600,C.g300],[C.yellow50,'B7791F',null]];
  [1,2,3,4].forEach((k,i)=>{ const w=ws[i], st=sty[i];
    R(s,{x,y,w,h,fill:st[0],line:st[2],lw:k===3?1:1.25,radius:0.14});
    T(s,B(15,`formula-${k}-label`),{x:x+0.2,y:y+0.1,w:w-0.3,h:0.34,fontSize:14,bold:true,color:st[1],valign:'middle'});
    T(s,B(15,`formula-${k}`),{x:x+0.2,y:y+0.46,w:w-0.3,h:0.8,fontSize:13.5,bold:k<3,color:C.navy,valign:'top',lineSpacingMultiple:1.12});
    x+=w; if(i<3){ T(s,'+',{x,y,w:pg,h,fontSize:20,bold:true,color:C.g400,align:'center',valign:'middle'}); x+=pg; } });
  T(s,B(15,'compare-label'),{x:M,y:3.55,w:8,h:0.36,fontSize:16,bold:true,color:C.navy,valign:'middle'});
  const cy=3.97, chh=1.25; R(s,{x:M,y:cy,w:3.9,h:chh,fill:C.g100,line:null,radius:0.14});
  chipX(s,{x:M+0.2,y:cy+0.14,text:B(15,'before-title'),fill:C.g600,color:'FFFFFF',size:12,h:0.3});
  T(s,B(15,'before-q'),{x:M+0.2,y:cy+0.48,w:3.5,h:0.38,fontSize:16,bold:true,color:C.g700,valign:'middle'});
  T(s,B(15,'before-result'),{x:M+0.2,y:cy+0.86,w:3.5,h:0.32,fontSize:13,color:C.g600,valign:'middle'});
  T(s,'›',{x:M+3.9,y:cy,w:0.4,h:chh,fontSize:28,color:C.blue,align:'center',valign:'middle'});
  const ax=M+4.3, aw=W-M-ax; R(s,{x:ax,y:cy,w:aw,h:chh,fill:C.white,line:C.blue,lw:1.5,radius:0.14});
  chipX(s,{x:ax+0.2,y:cy+0.14,text:B(15,'after-title'),fill:C.blue,color:'FFFFFF',size:12,h:0.3});
  T(s,B(15,'after-q'),{x:ax+0.2,y:cy+0.46,w:aw-0.35,h:0.4,fontSize:14.5,bold:true,color:C.navy,valign:'middle'});
  T(s,B(15,'after-result'),{x:ax+0.2,y:cy+0.86,w:aw-0.35,h:0.32,fontSize:13.5,bold:true,color:C.blue,valign:'middle'});
  const by=5.4; R(s,{x:M,y:by,w:W-2*M,h:1.18,fill:C.g50,line:null,radius:0.14});
  const g=L.img(s,AG('mode','43_mo_zoom_input'),{x:M+0.25,y:by+0.1,w:2.9,h:0.8,valign:'top',align:'left',shadow:false});
  pin(s,g,875,15,1,{dsf:1,d:0.26,color:C.red}); pin(s,g,983,225,2,{dsf:1,d:0.26,color:C.red});
  T(s,B(15,'caption'),{x:M+0.2,y:by+0.88,w:2.9,h:0.26,fontSize:11,color:C.g500,align:'center',valign:'middle'});
  const bts=CP(15).blocks.filter(b=>b.role==='bar-text').map(b=>b.text);
  T(s,bts.join('\n'),{x:M+3.4,y:by,w:W-2*M-3.6,h:1.18,fontSize:15.5,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.35});
  T(s,B(15,'source'),{x:M,y:6.66,w:W-2*M,h:0.26,fontSize:11,color:C.g500,valign:'middle'});
  foot(s,no); });

// 16 고객에게 보낼 말 초안
add(16,(pres,no)=>{ const c=CP(16); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:2});
  R(s,{x:M,y:2.05,w:W-2*M,h:1.85,fill:C.g50,line:null,radius:0.16});
  T(s,B(16,'item1-title'),{x:M+0.25,y:2.15,w:3.1,h:0.4,fontSize:17,bold:true,color:C.navy,valign:'middle'});
  T(s,B(16,'item1-desc'),{x:M+0.25,y:2.57,w:3.1,h:0.62,fontSize:13,color:C.g700,valign:'top',lineSpacingMultiple:1.12});
  const g=L.img(s,HERO('bc2_general_input'),{x:M+3.5,y:2.18,w:W-2*M-3.7,h:1.25,valign:'top',align:'left',shadow:false});
  const k=g.scale, ul=(x1,x2,yy,col)=>s.addShape('line',{x:g.x+x1*k,y:g.y+yy*k,w:(x2-x1)*k,h:0,line:{color:col,width:2.5}});
  ul(60,480,100,C.blue); ul(1280,1495,100,C.purple); ul(62,458,143,C.purple); ul(461,857,143,C.red);
  const lg=[['pin-1',C.blue],['pin-2',C.purple],['pin-3',C.red]]; let lx=M+0.25;
  lg.forEach(([r,col],i)=>{ badge(s,lx,3.5,i+1,{d:0.3,color:col,size:11}); T(s,B(16,r),{x:lx+0.38,y:3.47,w:3.2,h:0.36,fontSize:13,bold:true,color:C.g700,valign:'middle'}); lx+=0.38+L.textW(B(16,r),13)+0.45; });
  const lx2=M, lw2=6.2;
  T(s,B(16,'item2-title'),{x:lx2,y:4.02,w:lw2,h:0.38,fontSize:17,bold:true,color:C.navy,valign:'middle'});
  [1,2].forEach((k2,i)=>{ const by=4.45+i*0.88; R(s,{x:lx2,y:by,w:lw2,h:0.8,fill:C.white,line:C.blue,lw:1.25,radius:0.14});
    T(s,B(16,`bubble-${k2}-label`),{x:lx2+0.2,y:by+0.06,w:2,h:0.26,fontSize:12,bold:true,color:C.g600,valign:'middle'});
    T(s,B(16,`bubble-${k2}`),{x:lx2+0.2,y:by+0.3,w:lw2-0.35,h:0.48,fontSize:13.5,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.05}); });
  const rx=7.05, rw=W-M-rx;
  T(s,B(16,'item3-group'),{x:rx,y:4.02,w:3,h:0.38,fontSize:17,bold:true,color:C.navy,valign:'middle'});
  const ct=B(16,'chip'); chipX(s,{x:W-M-L.textW(ct,12)-0.4,y:4.06,text:ct,fill:C.red50,color:C.red,size:12,h:0.3});
  const hw=(rw-0.2)/2;
  L.img(s,HERO('bc2_mode_simple'),{x:rx,y:4.5,w:hw,h:0.9,valign:'middle',align:'center',shadow:false});
  L.img(s,HERO('fix_term_tooltip'),{x:rx+hw+0.2,y:4.45,w:hw,h:0.85,valign:'middle',align:'center',shadow:false});
  T(s,B(16,'caption'),{x:rx+hw+0.2,y:5.28,w:hw,h:0.22,fontSize:10.5,color:C.g500,align:'center',valign:'middle'});
  [[3,rx],[4,rx+hw+0.2]].forEach(([k3,xx])=>{ T(s,B(16,`item${k3}-title`),{x:xx,y:5.5,w:hw,h:0.32,fontSize:15,bold:true,color:C.navy,valign:'middle'}); T(s,B(16,`item${k3}-desc`),{x:xx,y:5.82,w:hw,h:0.46,fontSize:11.5,color:C.g600,valign:'top',lineSpacingMultiple:1.05}); });
  bar(s,{y:6.3,h:0.42,text:B(16,'bar-text'),size:14,tone:'yellow'});
  T(s,B(16,'source'),{x:M,y:6.76,w:W-2*M,h:0.24,fontSize:10.5,color:C.g500,valign:'middle'});
  foot(s,no); });

// 17 이렇게는 묻지 마세요
add(17,(pres,no)=>{ const c=CP(17); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:2});
  const gap=0.14, cw=(W-2*M-gap)/2, ch=1.48;
  [1,2,3,4].forEach((k,i)=>{ const x=M+(i%2)*(cw+gap), y=2.05+Math.floor(i/2)*(ch+gap);
    R(s,{x,y,w:cw,h:ch,fill:C.white,line:C.g200,radius:0.14,shadow:true});
    T(s,B(17,`item${k}-title`),{x:x+0.25,y:y+0.1,w:cw-0.4,h:0.38,fontSize:16.5,bold:true,color:C.navy,valign:'middle'});
    const bad=B(17,`item${k}-bad`).replace(/^✕\s*/,''), good=B(17,`item${k}-good`).replace(/^○\s*/,'');
    s.addText([{text:'✕  ',options:{bold:true,color:C.red,fontSize:15,fontFace:L.FONT}},{text:bad,options:{color:C.g600,fontSize:13.5,fontFace:L.FONT}}],{x:x+0.25,y:y+0.5,w:cw-0.4,h:0.34,isTextBox:true,margin:0,valign:'middle'});
    const gl=good.split('\n');
    s.addText([{text:'○  ',options:{bold:true,color:C.green,fontSize:15,fontFace:L.FONT}},{text:gl.join(' · '),options:{bold:true,color:C.navy,fontSize:14,fontFace:L.FONT}}],{x:x+0.25,y:y+0.86,w:cw-0.4,h:0.5,isTextBox:true,margin:0,valign:'top'});
    });
  const dy=5.2; T(s,B(17,'caption'),{x:M,y:dy,w:6,h:0.26,fontSize:11.5,color:C.g500,valign:'middle'});
  L.img(s,HERO('bc2_disclaimer'),{x:M,y:dy+0.28,w:W-2*M,h:0.52,valign:'top',align:'left',round:false,shadow:false});
  const by=6.1; R(s,{x:M,y:by,w:W-2*M,h:0.5,fill:C.g100,line:null,radius:0.12});
  const cwid=chipX(s,{x:M+0.15,y:by+0.08,text:B(17,'band-label'),fill:C.navy,color:'FFFFFF',size:12.5,h:0.34});
  T(s,B(17,'band-text'),{x:M+0.35+cwid,y:by,w:W-2*M-cwid-0.5,h:0.5,fontSize:14.5,bold:true,color:C.navy,valign:'middle'});
  T(s,B(17,'source'),{x:M,y:6.68,w:W-2*M,h:0.24,fontSize:10.5,color:C.g500,valign:'middle'});
  foot(s,no); });


// 21 첫 5일
add(21,(pres,no)=>{ const c=CP(21); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:3});
  const gap=0.2, cw=(W-2*M-gap*4)/5;
  [1,2,3,4,5].forEach((d,i)=>{ const x=M+i*(cw+gap), y=2.2, h=3.55, on=i===0;
    R(s,{x,y,w:cw,h,fill:on?C.blue:C.white,line:on?null:C.g200,radius:0.16,shadow:!on});
    T(s,B(21,`day${d}-label`),{x:x+0.25,y:y+0.22,w:cw-0.4,h:0.36,fontSize:14,bold:true,color:on?C.blue100:C.blue,valign:'middle'});
    T(s,B(21,`day${d}-title`),{x:x+0.25,y:y+0.62,w:cw-0.35,h:0.8,fontSize:20,bold:true,color:on?'FFFFFF':C.navy,valign:'top',lineSpacingMultiple:1.1});
    [1,2].forEach((k,j)=> T(s,B(21,`day${d}-check-${k}`),{x:x+0.25,y:y+1.5+j*0.98,w:cw-0.35,h:0.9,fontSize:14.5,color:on?'FFFFFF':C.g700,valign:'top',lineSpacingMultiple:1.2})); });
  bar(s,{y:6.0,h:0.78,label:B(21,'bar-label'),text:B(21,'bar-text'),size:20});
  foot(s,no); });

// 22 마무리
add(22,(pres,no)=>{ const s=pres.addSlide(); s.background={color:C.blue};
  T(s,B(22,'watermark'),{x:W-6.2,y:0.8,w:5.6,h:2.4,fontSize:120,bold:true,color:'FFFFFF',transparency:82,align:'right',valign:'top'});
  T(s,CP(22).kicker,{x:M+0.2,y:0.55,w:4,h:0.36,fontSize:14,bold:true,color:C.blue100,valign:'middle'});
  let cx=M+0.2; ['1 찾기','2 고르기','3 묻기','4 터치하기'].forEach(t=>{ cx+=chipX(s,{x:cx,y:0.98,text:t,fill:'1B64DA',color:'FFFFFF',size:14,h:0.4})+0.14; });
  T(s,B(22,'title-line1')+'\n'+B(22,'title-line2'),{x:M+0.2,y:1.6,w:9,h:2.4,fontSize:52,bold:true,color:'FFFFFF',valign:'top',lineSpacingMultiple:1.12});
  T(s,B(22,'sub'),{x:M+0.2,y:4.1,w:9,h:0.55,fontSize:24,color:'FFFFFF',valign:'middle'});
  cx=M+0.2; [B(22,'chip-1'),B(22,'chip-2')].forEach(t=>{ cx+=chipX(s,{x:cx,y:4.9,text:t,fill:'1B64DA',color:'FFFFFF',size:15,h:0.5})+0.2; });
  T(s,B(22,'thanks'),{x:M+0.2,y:5.55,w:W-2*M-0.4,h:0.36,fontSize:15,color:'FFFFFF',transparency:15,valign:'middle'});
  T(s,B(22,'note'),{x:M+0.2,y:6.08,w:W-2*M-0.4,h:0.55,fontSize:11.5,color:'FFFFFF',transparency:10,valign:'middle',lineSpacingMultiple:1.2});
  foot(s,no,true); });


// 18 김민수 시연
add(18,(pres,no)=>{ const c=CP(18); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:3});
  const gap=0.28, cw=(W-2*M-gap*3)/4, py=2.12, ph=2.72;
  [1,2,3,4].forEach((k,i)=>{ const x=M+i*(cw+gap); R(s,{x,y:py,w:cw,h:ph,fill:C.g100,line:null,radius:0.16});
    T(s,B(18,`item${k}-place`),{x:x+0.15,y:py+0.06,w:cw-0.3,h:0.3,fontSize:12.5,bold:true,color:C.blue,valign:'middle'});
    if(i<3) T(s,'›',{x:x+cw,y:py+ph/2-0.3,w:gap,h:0.6,fontSize:24,color:C.g400,align:'center',valign:'middle'}); });
  const X=i=>M+i*(cw+gap);
  const g1=L.img(s,HERO('fix_reco3_card1'),{x:X(0)+0.15,y:py+0.38,w:cw-0.3,h:ph-0.48,valign:'middle',align:'center',shadow:false});
  s.addShape('roundRect',{x:g1.x+45*g1.scale,y:g1.y+572*g1.scale,w:221*g1.scale,h:48*g1.scale,fill:{type:'none'},line:{color:C.red,width:1.75},rectRadius:0.03});
  const g2=L.img(s,HERO('bc2_km_consent_btn'),{x:X(1)+0.12,y:py+0.45,w:cw-0.24,h:0.78,valign:'top',align:'center',shadow:false});
  T(s,'↓',{x:X(1),y:g2.y+g2.h,w:cw,h:0.28,fontSize:14,color:C.g400,align:'center',valign:'middle'});
  L.img(s,HERO('bc2_consent_popup'),{x:X(1)+0.2,y:g2.y+g2.h+0.3,w:cw-0.4,h:1.25,valign:'top',align:'center',shadow:false});
  const x3=X(2); chipX(s,{x:x3+0.2,y:py+0.45,text:B(18,'item3-chip'),fill:C.white,color:C.g700,size:12,h:0.32});
  T(s,B(18,'item3-bubble-label'),{x:x3+0.2,y:py+0.9,w:cw-0.4,h:0.3,fontSize:13,bold:true,color:C.blue,valign:'middle'});
  R(s,{x:x3+0.15,y:py+1.22,w:cw-0.3,h:1.32,fill:C.white,line:C.blue,lw:1.25,radius:0.14});
  T(s,B(18,'item3-bubble'),{x:x3+0.3,y:py+1.22,w:cw-0.55,h:1.32,fontSize:14.5,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.18});
  const g4=L.phone(s,LEG('report_step3'),{x:X(3)+0.2,y:py+0.4,w:1.25,h:ph-0.5}); 
  T(s,B(18,'item4-caption'),{x:X(3)+1.5,y:py+ph-0.62,w:cw-1.6,h:0.5,fontSize:11,color:C.g500,valign:'bottom'});
  [1,2,3,4].forEach((k,i)=>{ const x=X(i); badge(s,x,5.0,k,{d:0.38,size:13});
    T(s,B(18,`item${k}-title`),{x:x+0.46,y:4.97,w:cw-0.46,h:0.42,fontSize:15.5,bold:true,color:C.navy,valign:'middle'});
    T(s,B(18,`item${k}-desc`),{x:x+0.46,y:5.38,w:cw-0.46,h:0.5,fontSize:12,color:C.g600,valign:'top',lineSpacingMultiple:1.05}); });
  bar(s,{y:5.98,h:0.62,label:B(18,'bar-label'),text:B(18,'bar-text'),size:16});
  T(s,B(18,'note'),{x:M,y:6.66,w:W-2*M,h:0.26,fontSize:11,color:C.g500,valign:'middle'});
  foot(s,no); });

// 19 첫 마디·첫 질문 짝
add(19,(pres,no)=>{ const c=CP(19); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:3});
  const cw=[2.95,5.2,3.78], gx=0.1, x0=M, xs=[x0,x0+cw[0]+gx,x0+cw[0]+cw[1]+2*gx];
  [1,2,3].forEach((k,i)=>{ R(s,{x:xs[i],y:2.1,w:cw[i],h:0.38,fill:C.g100,line:null,radius:0.1}); T(s,B(19,`table-head-${k}`),{x:xs[i]+0.15,y:2.1,w:cw[i]-0.2,h:0.38,fontSize:14,bold:true,color:C.g700,valign:'middle'}); });
  const rows=[{th:HERO('fix_reco3_card1'),box:[45,572,266,620]},{th:HERO('reco1_card2'),box:[45,522,284,568]},{th:HERO('bc2_groups_opp'),box:[16,240,510,340]}];
  rows.forEach((r,i)=>{ const k=i+1, y=2.56+i*1.18, h=1.1;
    [0,1,2].forEach(j=>R(s,{x:xs[j],y,w:cw[j],h,fill:i===0?C.g50:C.white,line:i===0?null:C.g200,radius:0.12}));
    const g=L.img(s,r.th,{x:xs[0]+0.1,y:y+0.07,w:0.95,h:0.96,valign:'middle',align:'center',shadow:false,round:false});
    s.addShape('rect',{x:g.x+r.box[0]*g.scale,y:g.y+r.box[1]*g.scale,w:(r.box[2]-r.box[0])*g.scale,h:(r.box[3]-r.box[1])*g.scale,fill:{type:'none'},line:{color:C.red,width:1.25}});
    badge(s,xs[0]-0.12,y-0.1,k,{d:0.34,size:12});
    T(s,B(19,`row${k}-title`),{x:xs[0]+1.12,y:y+0.1,w:cw[0]-1.2,h:0.36,fontSize:15,bold:true,color:C.navy,valign:'middle'});
    T(s,B(19,`row${k}-desc`),{x:xs[0]+1.12,y:y+0.46,w:cw[0]-1.2,h:0.3,fontSize:12,color:C.g600,valign:'middle'});
    const chip=B(19,`row${k}-chip`,''); if(chip) chipX(s,{x:xs[0]+1.12,y:y+0.76,text:chip,fill:C.red50,color:C.red,size:11.5,h:0.28});
    const ft=B(19,`row${k}-first-tag`,''); 
    if(ft){ chipX(s,{x:xs[1]+0.15,y:y+0.08,text:ft,fill:C.g100,color:C.g700,size:11.5,h:0.28});
      T(s,B(19,`row${k}-first`),{x:xs[1]+0.15,y:y+0.4,w:cw[1]-0.3,h:0.66,fontSize:13.5,color:C.g700,valign:'top',lineSpacingMultiple:1.12}); }
    else T(s,B(19,`row${k}-first`),{x:xs[1]+0.15,y,w:cw[1]-0.3,h,fontSize:14.5,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.15});
    const qt=B(19,`row${k}-question-tag`,''); let qy=y+0.1, qh=h-0.2;
    if(qt){ T(s,qt,{x:xs[2]+0.15,y:y+0.06,w:cw[2]-0.3,h:0.26,fontSize:11.5,bold:true,color:C.blue,valign:'middle'}); qy=y+0.34; qh=h-0.42; }
    R(s,{x:xs[2]+0.12,y:qy,w:cw[2]-0.24,h:qh,fill:C.white,line:C.blue,lw:1,radius:0.1});
    T(s,B(19,`row${k}-question`),{x:xs[2]+0.25,y:qy,w:cw[2]-0.45,h:qh,fontSize:13,bold:true,color:C.navy,valign:'middle',lineSpacingMultiple:1.1}); });
  bar(s,{y:6.14,h:0.5,text:B(19,'bar-text'),size:16});
  T(s,B(19,'note'),{x:M,y:6.7,w:W-2*M,h:0.26,fontSize:11,color:C.g500,valign:'middle'});
  foot(s,no); });

// 20 요약 리포트
add(20,(pres,no)=>{ const c=CP(20); const s=head(pres,{kicker:c.kicker,title:c.title,sub:c.sub,ch:3});
  const st=[HERO('bc2_report_step1'),LEG('report_step2'),LEG('report_step3'),HERO('bc_kakao')];
  const pins=[[275,129],[65,285],[205,758],[40,240]];
  const gap=0.3, cw=(W-2*M-gap*3)/4;
  st.forEach((f,i)=>{ const x=M+i*(cw+gap); let g;
    if(i<3) g=L.phone(s,f,{x,y:2.08,w:cw,h:3.2}); else g=L.img(s,f,{x,y:2.5,w:cw,h:2.4,valign:'top',align:'center'});
    pin(s,g,pins[i][0],pins[i][1],i+1,{dsf:1,d:0.38});
    if(i===1) s.addShape('roundRect',{x:g.x+20*g.scale,y:g.y+733*g.scale,w:376*g.scale,h:54*g.scale,fill:{type:'none'},line:{color:C.red,width:1.5},rectRadius:0.03});
    T(s,B(20,`item${i+1}-title`),{x,y:5.35,w:cw,h:0.36,fontSize:15.5,bold:true,color:C.navy,valign:'middle'});
    T(s,B(20,`item${i+1}-desc`),{x,y:5.7,w:cw,h:0.46,fontSize:12,color:C.g600,valign:'top',lineSpacingMultiple:1.05});
    if(i<3) T(s,'›',{x:x+cw+0.02,y:3.4,w:gap-0.04,h:0.6,fontSize:24,color:C.g400,align:'center',valign:'middle'}); });
  const pt=B(20,'pill'); const pw=L.textW(pt,12.5)+0.4; R(s,{x:W-M-pw,y:2.08,w:pw,h:0.34,fill:C.white,line:C.blue,lw:1.25,radius:0.17}); T(s,pt,{x:W-M-pw,y:2.08,w:pw,h:0.34,fontSize:12.5,bold:true,color:C.blue,align:'center',valign:'middle'});
  T(s,B(20,'caption'),{x:W-M-4,y:4.98,w:4,h:0.26,fontSize:11,color:C.g500,align:'right',valign:'middle'});
  bar(s,{y:6.28,h:0.48,text:B(20,'bar-text'),size:14.5,tone:'yellow'});
  foot(s,no); });

module.exports = { S, add, B, CP, BY, CONTENT, MISS, HERO, AG, LEG, F, mmss };
