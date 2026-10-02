# 그룹 E 가 새로 만든 자르기 그림. 다시 만들 때: python3 crops_E.py
from PIL import Image
H = '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final/hero/'

# [62] 시나리오 3 추천 카드(김민수): 기존 reco3_card1(712x768)은 카드 아래 테두리가 잘려 있었음.
# reco3_card1 과 같은 원본(gate_reco3.png)·같은 왼쪽 위(26,96)에서, 카드 아래 테두리(y=894) + 20px 까지 자름
# (reco1_card1 도 카드 아래 테두리 + 20px 로 끝남 → 60장과 여백이 같아짐).
Image.open(H+'gate_reco3.png').crop((26, 96, 738, 914)).save(H+'fix_reco3_card1.png')

# [59] 03 '고객찾기에서 열기' 카드: find_card_z(1944x1185, 가로로 긴 그림)는 카드 폭에 맞추면 높이가 1.5in 뿐이라
# 위아래가 비었음. 이유 문장 전체(오른쪽 끝 x=1250)와 한눈에 보기 앞 두 줄(4칸, 칸 오른쪽 테두리 x=1244)까지만 남겨
# 세로 비율을 높인 그림(1198x1062).
Image.open(H+'find_card_z.png').crop((68, 48, 1266, 1110)).save(H+'fix_find_card_left.png')
