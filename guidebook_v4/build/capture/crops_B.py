# 그룹 B 새 그림 만들기 (다시 만들 때: python3 crops_B.py)  — 원본 파일은 건드리지 않고 fix_*.png 로만 저장
from PIL import Image
F = '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final'
HERO = f'{F}/hero'

# [13] 롤링배너 왼쪽 부분 확대(③ 원 + '영업기회·고객확보 MeAI 홈 에서' + [MeAI 홈 바로가기] 버튼). 원본 portal_entry_banner.png(1536x420)
im = Image.open(f'{HERO}/portal_entry_banner.png').convert('RGB').crop((0, 0, 690, 420))
im.save(f'{HERO}/fix_banner_left_z.png'); print('fix_banner_left_z', im.size)

# [22] 대문 범례 확대본(gate_legend_z.png 3420x450)의 오른쪽 빈 여백을 잘라 내용만(글자 끝 x2698) → 같은 폭에서 더 크게 보이게
im = Image.open(f'{HERO}/gate_legend_z.png').convert('RGB').crop((0, 0, 2750, 450))
im.save(f'{HERO}/fix_legend_tight.png'); print('fix_legend_tight', im.size)

# [28] 2번 '고객찾기 · 펼친 카드' — 1·3번과 같은 고객(최수영)의 펼친 카드만. 원본 gate010/25_find_from_card_choi.png(2880x2580, dsf2)
#   카드 검은 테두리 x656~1905, y398~1259 → 사방 14px 여유
im = Image.open(f'{F}/gate010/25_find_from_card_choi.png').convert('RGB').crop((642, 384, 1920, 1272))
im.save(f'{HERO}/fix_find_card_choi.png'); print('fix_find_card_choi', im.size)

# [28] 4번 '맞춤대화 화면' — custom_q_crop.png(2040x1800)에서 오른쪽 빈 여백과 위 버튼 줄을 빼고
#   계약 리스트 + '이번 대화에서 활용될 ○○님의 보험 가입 내역' 문장 + 추천 질문 입력창까지만 → 같은 폭에서 글자가 더 크게
im = Image.open(f'{HERO}/custom_q_crop.png').convert('RGB').crop((110, 170, 1680, 1792))
im.save(f'{HERO}/fix_custom_q_tight.png'); print('fix_custom_q_tight', im.size)
