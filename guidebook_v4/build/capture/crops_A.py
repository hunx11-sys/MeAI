# 그룹 A 새 그림 만들기 (다시 만들 때: python3 crops_A.py)
# [10] 01 '대문 열기' — 대문 '내 고객 찾기' 숫자 줄(gate_stats, dsf 2)을 2줄로 나눠 붙여 크게 보이게 함.
#   원본 좌표(gate_stats.png 픽셀): 제목 '내 고객 찾기' x88~273 y82~117 / 구분선 y224~225 색(238,239,242)
#   숫자 4개 y278~306 : ①내 전체 고객 x88~324 ②맞춤대화 가능 x394~638 ③사전조회 동의 필요 x707~1012 ④상품제안 가능 x1081~1316
#   → 1줄 = ①② , 2줄 = ③④ (확대·축소 없이 원본 픽셀 그대로 옮겨 붙임)
from PIL import Image, ImageDraw
HERO = '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero'
src = Image.open(f'{HERO}/gate_stats.png').convert('RGB')
title = src.crop((80, 74, 300, 126))      # '내 고객 찾기'
row1  = src.crop((80, 266, 646, 318))     # ① 내 전체 고객 342명 · ② 맞춤대화 가능 137명
row2  = src.crop((699, 266, 1324, 318))   # ③ 사전조회 동의 필요 186명 · ④ 상품제안 가능 84명
W, Hh = 706, 292
out = Image.new('RGB', (W, Hh), (255, 255, 255))
out.paste(title, (40, 34))
d = ImageDraw.Draw(out)
d.rectangle((48, 108, W - 48, 109), fill=(238, 239, 242))
out.paste(row1, (40, 136))
out.paste(row2, (40, 206))
out.save(f'{HERO}/fix_gate_stats_2row.png')
print('saved fix_gate_stats_2row.png', out.size)

# [7] 2번·[10] 03 — 고객찾기 펼친 카드 윗부분(이름·이유 문장·태그 줄). v2_card_tags_z 에서 카드의 검은 테두리(위 y12~14, 왼쪽 x24~26)를 빼고 안쪽만.
tags = Image.open(f'{HERO}/v2_card_tags_z.png').convert('RGB').crop((40, 32, 1300, 456))
tags.save(f'{HERO}/fix_card_tags_clean.png')
print('saved fix_card_tags_clean.png', tags.size)
