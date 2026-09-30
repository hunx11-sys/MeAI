# 방송판 v2(영업가족용) 추가 캡처 자르기 — 원본은 final/gate010·find010 (목업 v2, dsf 2)
from PIL import Image
F='final/'; H=F+'hero/'
def crop(src,box,out): im=Image.open(src).crop(box); im.save(out); print(out, im.size)
crop(F+'gate010/23_general_chat_home.png',(930,300,2480,1450),H+'bc2_general_home.png')        # 일반대화 첫 화면: 인사·탭 3개·질문 예시·개인정보 안내
crop(F+'find010/65_custom_question_result.png',(940,1370,2520,1680),H+'bc2_custom_input.png')   # 맞춤대화 입력창: 질문 예시 [보장분석 해줘] + 직접 입력한 질문
crop(F+'gate010/23_general_chat_home.png',(40,40,560,400),H+'bc2_left_menu.png')                 # 왼쪽 위 [MeAI 홈] · 약관 검색 · 사용 가이드
crop(F+'find010/64_general_question_result.png',(960,1380,2520,1680),H+'bc2_general_input.png')  # 고객찾기 일반대화 추천 질문을 눌렀을 때 입력창에 채워진 안내 문자 요청
crop(F+'find010/40_consent_request_popup.png',(30,28,995,520),H+'bc2_consent_popup.png')        # 사전조회동의 요청 팝업(빈 칸 · 휴대폰 번호 입력 안내)
crop(H+'bc2_gate_full_s3.png',(280,1150,2600,2160),H+'bc2_gate_reco_s3.png')                 # MeAI 홈 오늘의 추천 고객(세트 3) 부분
from PIL import ImageDraw
# 영업포탈 진입점 그림: 접속 ID·시각, 프로필·직책 사다리, 통장·수수료·직책 칸, CRM 첫 줄 연락처를 옅은 회색으로 가림
im=Image.open(H+'portal_entry_full.png').convert('RGB'); d=ImageDraw.Draw(im)
for b in [(1215,40,1515,66),(1150,108,1535,308),(412,322,1138,428),(785,612,915,634),(1155,362,1530,426)]: d.rectangle(b,fill=(242,244,247))
im.save(H+'bc2_portal_masked.png'); print(H+'bc2_portal_masked.png', im.size)
# MeAI 홈(세트 3) 위쪽: 범례 빼고, 최근 업데이트 날짜·시각은 바탕색으로 가림
im=Image.open(H+'bc2_gate_full_s3.png').convert('RGB').crop((0,0,2880,2150)); d=ImageDraw.Draw(im)
bg=im.getpixel((2600,320)); d.rectangle((2244,298,2514,350),fill=bg)
im.save(H+'bc2_gate_s3_top.png'); print(H+'bc2_gate_s3_top.png', im.size, bg)
# 고객찾기(김민수 펼침): 오른쪽 위 최근 업데이트 시각 가림
im=Image.open(H+'bc2_find_km_full.png').convert('RGB'); d=ImageDraw.Draw(im); d.rectangle((2362,27,2851,99),fill=(255,255,255)); im.save(H+'bc2_find_km_masked.png'); print('find masked', im.size)
crop(H+'find_right_z.png',(0,0,1320,900),H+'bc2_find_right_top.png')            # 고객찾기 오른쪽 패널 위쪽(추천 질문 두 장까지)
crop(H+'fix_answer_top.png',(0,210,1720,1212),H+'bc2_answer_top.png')           # 답변 위쪽: 목업 날짜 줄 제외
crop(F+'hero/term_pc_input_z.png',(30,470,1840,580),H+'bc2_disclaimer.png')      # 입력창 아래 안내문 두 줄(화면 그대로)
crop(H+'bc2_general_home.png',(40,1080,870,1135),H+'bc2_privacy_line.png')    # '개인정보를 입력하지 마세요' 안내 한 줄
crop(F+'find010/32_right_panel_kimminsu.png',(0,560,830,810),H+'bc2_km_consent_btn.png')   # 김민수 오른쪽 패널: [사전조회동의 요청하기] 버튼과 안내
crop(F+'find010/08_left_groups_opportunity.png',(0,250,528,736),H+'bc2_groups_opp.png')     # 고객 그룹 영업 기회 탭(상령일·생일·사전동의 만료)
# 표지용 MeAI 홈 전체(세트 3): 최근 업데이트 날짜·시각 가림
im=Image.open(H+'bc2_gate_full_s3.png').convert('RGB'); d=ImageDraw.Draw(im); d.rectangle((2244,298,2514,350),fill=im.getpixel((2600,320))); im.save(H+'bc2_gate_full_s3_masked.png'); print('cover masked', im.size)
# 리포트 1단계 휴대폰 화면: '해지/유지 판단' 질문 예시 글자를 지움(해지 권유로 읽히지 않게)
im=Image.open(F+'legacy/report_step1.png').convert('RGB'); d=ImageDraw.Draw(im); from collections import Counter; bgc=Counter(im.getpixel((x,y)) for x in range(30,350) for y in range(528,566)).most_common(1)[0][0]; d.rectangle((60,533,337,561),fill=bgc); im.save(H+'bc2_report_step1.png'); print('report1', im.size, bgc)
crop(H+'bc_mode_dropdown.png',(30,40,880,250),H+'bc2_mode_simple.png')           # 모드 선택: '간편 분석' 줄만
# 답 아래 질문 버튼(휴대폰): 2·3번 버튼 글자를 지움(전환·정리 권유로 읽히지 않게)
from collections import Counter
im=Image.open(F+'mode/54_mo_zoom_examples.png').convert('RGB'); d=ImageDraw.Draw(im)
for (y1,y2) in [(348,452),(534,641)]:
    bgc=Counter(im.getpixel((x,y)) for x in range(120,1000,7) for y in range(y1,y2,3)).most_common(1)[0][0]
    d.rectangle((160,y1,1010,y2),fill=bgc)
im.save(H+'bc2_mo_examples.png'); print('mo examples', im.size)
