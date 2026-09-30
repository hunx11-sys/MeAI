# 가이드북 v4 영업가족판 — 부담보 예시를 뺀 새 캡처 자르기·가리기. 원본은 final/gb5(cap_gb5.mjs, 목업 v2)
from PIL import Image, ImageDraw
import json
F='final/'; G=F+'gb5/'; H=F+'hero/'; HB='/home/user/MeAI/guidebook_v4/captures/hero/'
J=json.load(open(G+'cap_gb5.json'))
def crop(src,box,out): im=Image.open(src).convert('RGB').crop(box); im.save(out); print(out, im.size); return im
def css2px(b,ox=0,oy=0,s=2,pad=4): return (round((b['x']-ox-pad)*s), round((b['y']-oy-pad)*s), round((b['x']+b['w']-ox+pad)*s), round((b['y']+b['h']-oy+pad)*s))
jae=[J['jaeText'][0], J['jaeText2'][0]]
# 1) MeAI 홈 전체(세트 3): 정재민 카드의 이유 문장·설명(중복 보장 정리 권유로 읽힘)을 카드 바탕(흰색)으로, 최근 업데이트 날짜·시각을 페이지 바탕으로 가림
im=Image.open(G+'gb5_gate_full.png').convert('RGB'); d=ImageDraw.Draw(im)
for b in jae: d.rectangle(css2px(b),fill=(255,255,255))
dt=J['date'][0]; bg=im.getpixel((2600,320)); d.rectangle((round((dt['x']+84)*2),round((dt['y']-2)*2),round((dt['x']+dt['w']+2)*2),round((dt['y']+dt['h']+2)*2)),fill=bg)
im.save(G+'gb5_gate_full_m.png'); print('gate full masked', im.size, bg)
# 2) 오늘의 추천 고객(세트 3) 영역 — clip x150 y580
im=Image.open(G+'gb5_gate_reco3.png').convert('RGB'); d=ImageDraw.Draw(im)
for b in jae: d.rectangle(css2px(b,150,580),fill=(255,255,255))
im.save(G+'gb5_gate_reco3_m.png'); print('reco3 masked', im.size)
# 3) 세트 2·3 카드 6장(9장 장표용) — 카드 테두리 사방 6px 여유, 높이는 세트 3 카드(394px) 기준으로 통일
for n,src in ((3,G+'gb5_gate_reco3_m.png'),):
    im=Image.open(src)
    for i,b in enumerate([J['kim'],J['jae'],J['seo']]):
        x0=round((b['x']-150-6)*2); y0=round((b['y']-580-6)*2); im.crop((x0,y0,x0+round((b['w']+12)*2),y0+round((b['h']+12)*2))).save(G+f'gb5_reco3_card{i+1}.png')
print('reco3 cards', Image.open(G+'gb5_reco3_card1.png').size)
# 4) 고객찾기 펼친 카드·오른쪽 패널(서은아·박준호) — 최수영판과 같은 자리(카드 테두리 x656~1905, y398~1259)
for t in ('seo','park'):
    crop(G+f'gb5_find_{t}.png',(642,384,1920,1272),G+f'gb5_find_{t}_card.png')
    crop(G+f'gb5_find_{t}.png',(2000,140,2880,1120),G+f'gb5_find_{t}_right.png')
# 5) 맞춤대화(추천 질문으로 들어온 화면) — fix_custom_q_tight 와 같은 자리
crop(G+'gb5_custom_seo.png',(950,170,2520,1792),G+'gb5_custom_seo_tight.png')
# 6) 고객찾기 검색 추천 속성: 마지막 '부담보' 칩을 바탕색으로 지움(MeAI 홈에서 부담보 데이터를 쓰지 않음)
im=Image.open(HB+'fix_c_search_attr.png').convert('RGB'); ImageDraw.Draw(im).rectangle((612,168,758,269),fill=(255,255,255)); im.save(G+'gb5_search_attr_m.png'); print('search attr masked', im.size)
# 7) 게시판 글 상세: '2차 오픈' 문장을 뺀 화면(cap_gb5_board.mjs)을 옛 board_detail_crop 과 같은 자리에서 자르되, 아래 빈 여백(약 60px)은 덜어 냄
crop(G+'gb5_board_detail.png',(540,190,2340,1380),G+'gb5_board_detail_crop.png')
# 8) 카카오톡 리포트 캡처: 양옆 휴대폰 테두리(x0~5·x380~385 어두운 세로줄)와 오른쪽 흰 여백(x386~398)을 덜어 냄 — 1-3 쪽(p1.js) 4단계용
#    from PIL import Image
#    Image.open(HB+'report_kakao_crop.png').crop((6,0,380,334)).save(G+'gb5_kakao_clean.png')   # 399x334 -> 374x334
#    (실제 실행 경로) SP=/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad
#    Image.open(SP+'/gb5/captures/hero/report_kakao_crop.png').crop((6,0,380,334)).save(SP+'/gb5/captures/hero/gb5_kakao_clean.png')
#    결과 사방 가장자리 전부 채팅 바탕색 (171,193,209) — 테두리·흰 여백 없음
# 9) 게시판 글 상세(다시 자름, 2026.09.30 p5 수정): 7)의 1190px 은 아래를 90 CSS px 더 잘라 '이전 글·다음 글' 카드가 빠졌음(핀 5가 빈 곳을 가리킴).
#    같은 새 화면(2차 오픈 문장 뺀 것)에서 옛 board_detail_crop(1460) - 90px(45 CSS) = 1370px 높이로 다시 자름. clip (270,95) CSS · dsf 2 · 너비 900 · 높이 685 CSS.
#    옛 파일은 덮어쓰지 않고 새 이름으로 저장. p5.js 글 상세 장이 이 파일을 씀.
#    from PIL import Image
#    SP='/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad'
#    Image.open(SP+'/final/gb5/gb5_board_detail.png').convert('RGB').crop((540,190,2340,1560)).save(SP+'/gb5/captures/hero/gb5_board_detail_1370.png')   # 1800x1370
#    결과: 0..1190 행은 gb5_board_detail_crop 과 같고, 아래에 이전 글·다음 글 카드 전체가 들어옴(옛 board_detail_crop 1280..1460 행과 글자 같음)
# 10) (2026.10.02) 정재민 카드: 가림 상자 대신 예시 문장으로 채운 화면(cap_gb5_jae.mjs)으로 다시 만든다 — 날짜만 가림
import json as _j
_J=_j.load(open(G+'cap_gb5.json'))
im=Image.open(G+'gb5_gate_full_r.png').convert('RGB'); d=ImageDraw.Draw(im)
dt=_J['date'][0]; bg=im.getpixel((2600,320)); d.rectangle((round((dt['x']+84)*2),round((dt['y']-2)*2),round((dt['x']+dt['w']+2)*2),round((dt['y']+dt['h']+2)*2)),fill=bg)
im.save(G+'gb5_gate_full_m.png'); print('gate full (정재민 채움)', im.size)
im=Image.open(G+'gb5_gate_reco3_r.png').convert('RGB'); im.save(G+'gb5_gate_reco3_m.png')
for i,b in enumerate([_J['kim'],_J['jae'],_J['seo']]):
    x0=round((b['x']-150-6)*2); y0=round((b['y']-580-6)*2); im.crop((x0,y0,x0+round((b['w']+12)*2),y0+round((b['h']+12)*2))).save(G+f'gb5_reco3_card{i+1}.png')
print('reco3 (정재민 채움)', im.size)
