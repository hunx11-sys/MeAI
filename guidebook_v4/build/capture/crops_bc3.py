# 방송판 v3 추가 캡처 자르기 — 일반대화·맞춤대화 화면 설명 장(12~14장). 원본은 final/hero(cap_bc3.mjs)·final/gate010, dsf 2
from PIL import Image
F='final/'; H=F+'hero/'
def crop(src,box,out): im=Image.open(src).crop(box); im.save(out); print(out, im.size)
crop(H+'bc2_gate_s3_top.png',(300,170,2580,680),H+'bc3_home_cards.png')          # MeAI 홈 인사 문구 + 대화 카드 두 장(날짜는 이미 가림)
crop(H+'bc3_general_home.png',(0,0,2520,1800),H+'bc3_general_crop.png')          # 일반대화 첫 화면(오른쪽 빈 여백만 덜어 냄)
crop(H+'bc3_general_home.png',(50,50,300,140),H+'bc3_home_btn.png')              # 왼쪽 위 [MeAI 홈] 버튼
crop(F+'gate010/17_search_popup.png',(0,0,1504,1130),H+'bc3_popup_top.png')      # 고객 검색 창 위쪽(제목·검색칸·첫 줄들, 이름은 목업 예시)
# 방송 점검 반영: 12장 썸네일 — 고객 검색 창 상자만(1.47:1), 추천 카드 길(3번)은 김민수 오른쪽 패널(동의 전이라 일반대화 추천 질문만 보임)
crop(H+'bc3_popup_top.png',(32,32,1472,1014),H+'bc3_popup_modal.png')
crop(H+'bc2_find_km_masked.png',(2030,160,2860,600),H+'bc3_find_km_right.png')
