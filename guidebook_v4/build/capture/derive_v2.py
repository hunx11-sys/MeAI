# 새 목업(v2) 캡처에서 가이드북용 잘라낸 그림을 다시 만든다. 원래 자르기 좌표 그대로(derive_history.txt 참고).
from PIL import Image
F='final/'; H=F+'hero/'
def crop(src,box,dst): im=Image.open(src); im.crop(box).save(dst); print('crop', dst, Image.open(dst).size)
# 추천 카드 9장 (gate_reco1~3, clip x150 y580 dsf2)
for n in (1,2,3):
    im=Image.open(H+f'gate_reco{n}.png')
    for i,px in enumerate((160,539,917)):
        x0=(px-150+3)*2; y0=(634-580-6)*2; x1=(px-150+362-3)*2; y1=y0+(372+12)*2
        im.crop((x0,y0,x1,y1)).save(H+f'reco{n}_card{i+1}.png')
print('reco cards', Image.open(H+'reco1_card1.png').size)
# 카드 줌 (화살표 숨김판)
Image.open(F+'gate010/28_zoom_card_choi.png').save(H+'gate_card_z.png'); Image.open(F+'gate010/29_zoom_card_ai_ribbon.png').save(H+'gate_card_ai_z.png')
# 게시판 목록/상세
crop(H+'board_full.png',(540,170,2340,1710),H+'board_list_crop.png')
crop(H+'board_detail.png',(540,190,2340,1650),H+'board_detail_crop.png')   # css x270..1170, y95..825 (화면 1440x900 안)
# 추천 질문 클릭 결과 / 최수영 오른쪽 패널
crop(F+'find010/65_custom_question_result.png',(840,0,2880,1800),H+'custom_q_crop.png')
crop(F+'gate010/25_find_from_card_choi.png',(2000,140,2880,1120),H+'find_right_choi.png')
# 검색 관련
crop(F+'find010/44_search_recommended_attributes.png',(0,0,1200,300),H+'search_attr_crop.png')
crop(F+'find010/46_search_cancer_suggest.png',(20,0,1200,470),H+'search_suggest_crop.png')
crop(F+'gate010/15_consent_toast.png',(150,70,970,180),H+'consent_toast_crop.png')
crop(F+'gate020/08_search_no_result.png',(0,0,1488,900),H+'search_noresult_crop.png')
# 고객 그룹 합성
a=Image.open(H+'find_groups_z.png'); b=Image.open(H+'find_left_opp_top_z.png')
W=a.width+b.width+40; Hh=max(a.height,b.height); c=Image.new('RGB',(W,Hh),(249,250,251)); c.paste(a,(0,0)); c.paste(b,(a.width+40,0)); c.save(H+'find_groups_both.png'); print('groups both', c.size)
# 맞춤대화 시작 화면
im=Image.open(F+'gate010/22_custom_chat_after_select.png'); im.crop((0,0,2880,2580)).save(H+'custom_start_full.png')
crop(H+'custom_start_full.png',(640,30,2560,1120),H+'custom_start_crop.png')

# 카카오톡 알림톡: 이름 세 곳을 넉넉히 가림(설계사·고객 이름)
from PIL import ImageDraw
im=Image.open(F+'legacy/report_step4.png').convert('RGB'); im=im.crop((8,388,407,722)); d=ImageDraw.Draw(im)
for box in [(64,108,152,129),(111,129,190,147),(163,180,228,199)]: d.rectangle(box,fill=(235,235,235))
im.save(H+'report_kakao_crop.png')
# 영업포탈 진입점(소유자 제공 그림 67e96ce4-image.png): 번호 원 온전히, 상태줄 제외
# crop('portal_entry_full',(8,140,1625,1022)); crop('portal_entry_banner',(392,240,1160,450),2); crop('portal_entry_crm',(415,650,1160,1000),2)
# 태그 색 장 카드 확대
im=Image.open(H+'find_card_z.png'); im.crop((0,0,1300,470)).save(H+'v2_card_tags_z.png')
