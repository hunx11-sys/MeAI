# 마지막 손질
from PIL import Image
Image.open('final/gate020/08_search_no_result.png').crop((24,24,1464,900)).save('final/hero/fix_noresult_popup.png')  # 팝업 흰 상자만(뒤 화면 조각 제거)
