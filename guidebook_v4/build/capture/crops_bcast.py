# 방송판용 자르기
from PIL import Image
Image.open('final/hero/mode_pc_dropdown_z.png').crop((82,469,984,1200)).save('final/hero/bc_mode_dropdown.png')  # 모드 변경 드롭다운만
Image.open('final/hero/gate_search_kim.png').crop((0,0,1440,1168)).save('final/hero/bc_search_top.png')   # 고객 검색 팝업 윗부분('김' 입력, 회색 철회 줄 포함)
Image.open('final/hero/report_kakao_crop.png').crop((0,0,392,334)).save('final/hero/bc_kakao.png')          # 카톡 캡처 오른쪽 검은 띠 제외
# bc_choi_card_z.png · bc_choi_six_z.png 는 final/v2new/cap_bcast.mjs 로 찍음(최수영 카드 → 고객찾기 펼친 카드, dsf 3)
