// PART 06 현장 실천 · 정리 · 출처
module.exports = function(pres, L, N, pg){
  const {T,W,H,M,CW} = L;
  pres.addSection({ title:'06 현장 실천' });
  const P = ()=>`${String(pg.n++).padStart(2,'0')} / ${N}`;
  let s = pres.addSlide({ masterName:'INK', sectionTitle:'06 현장 실천' }); P();
  L.divider(s, 5, '현장 실천', '상담 화법 세 문장, 입원 전 안내 다섯 가지, 그리고 정리');

  // 화법
  s = pres.addSlide({ masterName:'LIGHT', sectionTitle:'06 현장 실천' }); L.kicker(s,'상담 화법 세 문장',P());
  L.title(s, '세 문장이면 된다. 「입원이 줄어든다」로 열고, 「입원은 고객이 정하지 못한다」로 이어, 「치료 행위를 보장받자」로 닫는다');
  const msgs=[['설계사','혹시 백내장이나 정맥류 수술 받으신 분 주변에 계세요? 요즘은 수술하고 그날 집에 가는 게 보통이에요. 주요수술 평균 입원이 5.6일, 백내장은 1.1일이에요.','you'],
              ['고객','그래도 입원하면 입원비는 나오는 거 아니에요?','me'],
              ['설계사','입원했는지는 병원 침대가 아니라 약관이 정해요. 작년 대법원에서 백내장 입원 137명이 전부 통원으로 판정됐고, 올해는 정맥류 이틀 입원도 통원이 됐어요. 그래서 요즘 설계는 「며칠 입원했나」가 아니라 「무슨 치료를 받았나」로 해요.','you'],
              ['고객','그럼 뭘 봐야 해요?','me'],
              ['설계사','수술비, 치료비, 통원일당이에요. 입원을 했든 안 했든 수술을 했으면 수술비, 항암을 받았으면 치료비, 외래를 다녔으면 통원일당. 고객님 증권에서 이 세 칸부터 같이 볼게요.','you']];
  let y=2.55;
  msgs.forEach((m)=>{ const me=m[2]==='me'; const w=me?3.6:6.4; const x=me?M+6.8-w+3.6-3.6+0.0:M; const xx = me ? M+6.4-w : M; const h = me?0.55:(m[1].length>90?0.95:0.75);
    s.addShape('roundRect',{x:xx,y,w,h,fill:{color:me?T.blue:T.bg3},line:{color:me?T.blue:T.bg3},rectRadius:0.16});
    L.txt(s,m[1],{x:xx+0.22,y,w:w-0.44,h,fontSize:10.5,color:me?'FFFFFF':T.fg,valign:'middle',lineSpacingMultiple:1.3,align:me?'right':'left'});
    y += h+0.1; });
  // 오른쪽 : 세 문장 카드
  const kx=M+6.9, kw=CW-6.9;
  const three=[['열기','입원이 줄어든다','주요수술 5.6일 · 백내장 1.1일 · 로봇수술 8배'],['잇기','입원은 고객이 정하지 못한다','대법원 2025.1 백내장 · 2026.6 정맥류 · 당사 9월 심사 강화'],['닫기','치료 행위를 보장받자','수술비 · 치료비 · 통원일당, 증권의 세 칸']];
  three.forEach((a,i)=>{ const yy=2.55+i*1.12; L.card(s,kx,yy,kw,1.0,i===2?'blue':'white'); L.chip(s,kx+0.28,yy+0.2,a[0],i===2?'wb':'b'); L.txt(s,a[1],{x:kx+1.1,y:yy+0.14,w:kw-1.3,h:0.4,fontSize:14,bold:true,color:i===2?'FFFFFF':T.fg,valign:'middle'}); L.txt(s,a[2],{x:kx+0.28,y:yy+0.58,w:kw-0.5,h:0.35,fontSize:9.5,color:i===2?'DCEBFF':T.fg2}); });
  L.note(s, '주: 화법 속 수치는 3부·2부 출처와 같다(건보공단 2025 주요수술 통계연보 · 대법원 2024다305643 · 대법원 2026다202566 · 쿠키뉴스 2026.9.14). 고객 앞에서 「보험사기」라는 말은 쓰지 않는다');

  // 입원 전 안내 5가지
  s = pres.addSlide({ masterName:'ALT', sectionTitle:'06 현장 실천' }); L.kicker(s,'입원 전 안내 다섯 가지',P());
  L.title(s, '고객이 입원하기 전에 전화로 알려 줄 다섯 가지. 이 다섯이 지켜지면 통원 판정은 줄고, 판정을 받아도 다툴 근거가 남는다');
  const five=[['병원 종류를 먼저 묻는다','요양병원 · 정신병원 · 한방병원이면 입원일당 특약 정의에서 빠질 수 있다. 상급종합·종합병원이면 전용 일당이 있다'],
              ['「왜 입원이 필요한지」를 의사에게 묻게 한다','합병증 위험, 마취 종류, 당일 귀가가 어려운 이유. 이 대답이 진료기록에 남아야 한다(사례 6의 402만원)'],
              ['입원 중 외출·외박을 하지 않는다','「의사의 관리 하에 치료에 전념」이 약관 요건이다. 외출 기록은 실질적 입원을 부정하는 근거가 된다'],
              ['양쪽·두 부위를 나눠 입원하지 않는다','하지정맥류 대법원 판결의 핵심. 같은 날 통원으로 가능한 치료를 이틀로 나누면 형식적 입원이 된다'],
              ['입원이 아니어도 나오는 특약을 같이 청구한다','수술비 · 치료비 · 통원일당 · 낮병동입원일당 · 응급실내원비. 통원 판정이 나도 이 특약들은 그대로 산다']];
  five.forEach((a,i)=>{ const yy=2.55+i*0.66; L.card(s,M,yy,CW,0.58,'white'); L.numDot(s,M+0.25,yy+0.14,i+1,T.blue,0.3); L.txt(s,a[0],{x:M+0.7,y:yy,w:4.3,h:0.58,fontSize:12.5,bold:true,valign:'middle'}); L.txt(s,a[1],{x:M+5.1,y:yy,w:CW-5.4,h:0.58,fontSize:10,color:T.fg2,valign:'middle',lineSpacingMultiple:1.25}); });
  L.take(s, '다섯 가지의 공통점은 「기록」이다. 입원이 맞다면 기록이 지켜 주고, 입원이 아니라면 기록이 미리 말해 준다');
  L.note(s, '출처: 당사 약관 「입원」 정의 · 대법원 2026다202566 · 연합 2026.5.12(402만원 판결) · 데일리메디 2026(한방병원). 안내 문구는 교안의 제안이며 보상 안내 공식 문서가 아니다');

  // 정리 (INK)
  s = pres.addSlide({ masterName:'INK', sectionTitle:'06 현장 실천' }); L.kicker(s,'정리',P(),true);
  L.txt(s, '네 문장을 들고 나간다', { x:M, y:1.15, w:8, h:0.7, fontSize:34, bold:true, color:'FFFFFF', charSpacing:-2 });
  const four=[['1','입원은 줄고 심사는 는다','의료기술 · 건보 재정 · 실손 손해율 · 제도, 네 힘이 한 방향이다'],['2','입원은 결과이지 선택이 아니다','백내장 · 정맥류 · 하이푸 · 줄기세포 주사, 고객이 정한 입원은 통원이 됐다'],['3','실손은 얇아지고, 정액은 넓어진다','5세대 비중증 50% 자기부담, 1·2세대 전환 할인. 비운 자리는 수술비·치료비가 채운다'],['4','「며칠 입원」이 아니라 「무슨 치료」','입원일당은 무거운 입원용으로 세 조건과 함께, 수술비·치료비·통원일당은 앞자리로']];
  four.forEach((a,i)=>{ const w=(CW-0.75)/4, x=M+i*(w+0.25), y=2.15; L.card(s,x,y,w,3.0,'ink2'); L.txt(s,a[0],{x:x+0.3,y:y+0.25,w:1,h:0.6,fontSize:40,bold:true,color:T.blue,charSpacing:-2}); L.txt(s,a[1],{x:x+0.3,y:y+1.0,w:w-0.6,h:0.8,fontSize:15,bold:true,color:'FFFFFF',lineSpacingMultiple:1.25}); L.txt(s,a[2],{x:x+0.3,y:y+1.85,w:w-0.6,h:1.0,fontSize:10.5,color:'B9C2CF',lineSpacingMultiple:1.35}); });
  L.take(s, '오늘 할 일 하나. 고객 증권 세 장을 꺼내 「입원일당」 칸과 「수술비·치료비·통원일당」 칸을 나란히 적어 본다', true);

  // 출처
  s = pres.addSlide({ masterName:'LIGHT', sectionTitle:'06 현장 실천' }); L.kicker(s,'출처와 한계',P());
  L.title(s, '출처와 한계. 모든 수치는 아래 자료의 보도·발표값이며, 원문을 직접 열어 확인하지 못한 항목은 「원문 확인 권장」으로 둔다', { fontSize:20 });
  const left=[['판례·감독','서울고법 2021나2013354(2022.1.20, 대법원 2022.6.16 확정) · 대법원 2024다305643(2025.1.23) · 대법원 2026다202566(2026.6.11) · 대법원 2004도6557(2006.1.12) · 금감원 보도자료 2025.3.10, 2025.9.8 · 금감원 금융민원 동향 2026.4.21 · 금감원 제2차 금융소비자보호 토론회 2025.11.18 · 금감원 행정지도 2026.6.22'],
              ['제도·정책','보험사기방지특별법 개정(2024.8.14 시행) · 심평원 공고 2024-193호 · 금융위 보도자료 2025.1.9, 2026.5(5세대), 2026.5.5(전환 할인), 2026.9.11 · 보건복지부 2026.6(도수치료 관리급여) · 건정심 2025.8.28, 2026.9.8, 2026.6.25'],
              ['통계','금감원 2025년 실손 사업실적(잠정) 2026.6.3 · 보험연구원(비급여 상위 항목) · 건보공단 2025년 주요수술 통계연보 · 건보공단 중장기 재무관리계획(2026.10.13 보도) · 국회예산정책처 2025.8 · 보건복지부 OECD 보건통계 2026 분석 · OECD Health at a Glance 2025 · 금감원 보험사기 적발 실적']];
  left.forEach((a,i)=>{ const yy=2.3+i*1.15; L.card(s,M,yy,7.2,1.05,'soft'); L.txt(s,a[0],{x:M+0.25,y:yy+0.12,w:1.3,h:0.3,fontSize:11,bold:true,color:T.blueDark}); L.txt(s,a[1],{x:M+1.5,y:yy+0.1,w:5.5,h:0.9,fontSize:8.8,color:T.fg,lineSpacingMultiple:1.3}); });
  L.card(s, M+7.45, 2.3, CW-7.45, 3.45, 'rd');
  L.txt(s, '한계 · 추정 표기 항목', { x:M+7.7, y:2.45, w:4, h:0.3, fontSize:12, bold:true, color:T.red });
  L.txt(s, [
    {text:'조사 방식: 검색 엔진이 돌려준 기사·보도자료 요약을 근거로 했고 원문 전문을 직접 연 항목은 없다. 교육 전 핵심 수치는 원문 URL을 한 번 연다', options:{bullet:true, breakLine:true}},
    {text:'실손 표준약관 본문의 「6시간」 문구 유무는 미확인. 6시간은 복지부 고시(낮병동)와 판례에서 온 기준으로 설명했다', options:{bullet:true, breakLine:true}},
    {text:'심평원 입원적정성 심사의 전국 「부적정 판정 비율」은 공개 통계가 없다', options:{bullet:true, breakLine:true}},
    {text:'하이푸 1심 선고일, 402만원 판결의 수술명, 한방병원 판결 선고일은 보도에 없다', options:{bullet:true, breakLine:true}},
    {text:'5세대 통원 「하루 20만원」, 전환 할인 11월 세부 약관은 최종 발표로 확인한다', options:{bullet:true, breakLine:true}},
    {text:'5부 잠재력 별점과 4부 상담 세 갈래는 이 교안의 가정값이다', options:{bullet:true}},
  ], { x:M+7.7, y:2.8, w:CW-7.95, h:2.9, fontSize:9.5, color:T.fg, paraSpaceAfter:5, lineSpacingMultiple:1.25 });
  L.note(s, '당사 자료: 특약 약관 원문(tool_body.js) · 특약 마스터(proposal_smart/db.json, 1,765개) · 디자인은 첨부 「55 PLAN 부산센터 교육」 HTML의 토큰(Pretendard · #3182F6 · #191F28 · 24px 카드)을 따랐다');
};
