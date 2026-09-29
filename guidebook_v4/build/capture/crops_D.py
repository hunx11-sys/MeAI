# 그룹 D(parts/p6.js) 새 그림 만들기 — 다시 만들 때: python3 crops_D.py
# 모든 좌표는 원본 PNG 픽셀. (CSS 좌표 = PNG 픽셀 / dsf)
from PIL import Image
F = '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final'
HERO = F + '/hero'

def crop(src, box, name):
    im = Image.open(src).convert('RGB').crop(box)
    im.save(f'{HERO}/{name}.png')
    print('saved', name, im.size)

# [49] 맞춤대화 시작 화면(custom_start_full, dsf 2)을 위·아래 두 장으로 나눠 크게.
#   위 = 왼쪽 메뉴(담당 고객) + 고객 정보 입력 카드 : CSS x0~1265, y12~532 (카드 그림자 끝 y520, 메뉴 '기존 보험 분석 프로세스' 끝 y520)
#   아래 = 총 보험료·약관DB 범례·담보 버튼·[전체 선택]·첫 상품 줄 : CSS x424~1262, y688~1109 (첫 상품 분홍 줄 y1011~1109)
#   아래 그림 왼쪽에 핀 자리(글자 시작 x490 앞 66px 여백)를 남김
crop(f'{HERO}/custom_start_full.png', (0, 24, 2530, 1064), 'fix_custom_top')
crop(f'{HERO}/custom_start_full.png', (848, 1376, 2524, 2218), 'fix_custom_bottom')

# [50] 답변 읽는 법 — term/36_pc_tall_full_off.png(dsf 2) 에서 다시 자름.
#   예전 term_answer_top/bottom 은 clip x465 라 왼쪽 여백이 25px 뿐 → 핀이 글자를 가림. x420 부터 잘라 핀 자리를 만든다.
#   위 : CSS y75~681 (표 윗선 y691 전에서 끊음) / 아래 : CSS y683~1222 (표 윗선 y691 포함 ~ 아이콘 줄 끝 y1198)
crop(f'{F}/term/36_pc_tall_full_off.png', (840, 150, 2560, 1362), 'fix_answer_top')
crop(f'{F}/term/36_pc_tall_full_off.png', (840, 1366, 2560, 2444), 'fix_answer_bottom')

# [51] 용어 말풍선 — term/08_pc_tooltip_cancer_diag_chat.png 에서 말풍선 오른쪽 끝(x739)에 맞춰 자름.
#   오른쪽 x740 부터 굵은 제목의 '지만,' 이 시작되므로 740 에서 끊고, 첫 줄은 '…8,000만 원이'(끝 x739) 낱말 끝.
#   둘째 줄('…이어지면 부담이')은 낱말 중간에서 잘리므로 뺌(첫 줄 끝 y630, 둘째 줄 시작 y652).
#   자른 뒤 오른쪽에 흰 여백 12px 을 덧붙임(왼쪽 여백 12px 과 맞춤, 테두리가 '원이'의 '이'를 덮지 않게)
im = Image.open(f'{F}/term/08_pc_tooltip_cancer_diag_chat.png').convert('RGB').crop((185, 410, 740, 644))
pad = Image.new('RGB', (im.width + 12, im.height), (255, 255, 255)); pad.paste(im, (0, 0))
pad.save(f'{HERO}/fix_term_tooltip.png'); print('saved fix_term_tooltip', pad.size)
#   용어 켠 답변(term_pc_on_full, dsf 3) : 예전 term_pc_on_z(CSS 480,280,780x420)는 맨 위 구분선(y288)과
#   맨 아래 표 윗선(y691) 조각이 들어감 → CSS y296~682 로 다시 자름.
crop(f'{HERO}/term_pc_on_full.png', (1440, 888, 3780, 2046), 'fix_term_on')

# [53] 모드 안내줄 — mode/24_pc_zoom_mode_notice.png(2340x189) 가운데 글자 부분만(양옆 선은 조금만)
crop(f'{F}/mode/24_pc_zoom_mode_notice.png', (600, 34, 1740, 154), 'fix_mode_notice')

# [57] 모바일 고객 목록 — 오른쪽 끝 x701~704 에 뒤 화면 화살표 조각 → 폭 700 으로(5px 안쪽)
crop(f'{HERO}/mobile_customer_list.png', (0, 0, 700, 1370), 'fix_mobile_customer_list')
