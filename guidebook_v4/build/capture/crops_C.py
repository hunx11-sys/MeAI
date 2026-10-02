# 그룹 C 자르기 기록 — python3 crops_C.py 로 다시 만들 수 있어요. (기존 파일은 덮어쓰지 않음, fix_c_* 만 만듦)
from PIL import Image, ImageDraw
F = '/tmp/claude-0/-home-user-MeAI/f5d765e8-a442-5f2c-87c4-ad64e47ba212/scratchpad/final'
H = F + '/hero'

def save(im, name):
    im.save(f'{H}/{name}.png'); print(name, im.size)

# [38] 추천 질문 → 대화 : 여백을 덜어 세로로 꽉 차게 (custom_q_crop = CSS x420~1440, dsf 2)
#   CSS x 445~1428, y 0~843 (아래 면책 문구 줄 제외) → 픽셀 ((445-420)*2, 0, (1428-420)*2, 843*2)
im = Image.open(f'{H}/custom_q_crop.png').convert('RGB')
save(im.crop((50, 0, 2016, 1686)), 'fix_c_custom_q')

# [40] [전체] 드롭다운만 : 왼쪽 '으로 설' 조각(x<66), 아래 'D-30' 칩(y>=368) 잘라냄
im = Image.open(f'{F}/find010/55_filter_dropdown_open.png').convert('RGB')
save(im.crop((66, 8, 394, 367)), 'fix_c_filter_dropdown')

# [40] 검색창 + 추천 속성만 : 왼쪽 검은 글자 조각(x<12)·아래 글자 조각(y>=281) 잘라내고 왼쪽 흰 여백 8px
im = Image.open(f'{H}/search_attr_crop.png').convert('RGB')
c = im.crop((12, 12, 1194, 281))
out = Image.new('RGB', (c.width + 8, c.height), (255, 255, 255)); out.paste(c, (8, 0))
save(out, 'fix_c_search_attr')

# [43] 게시판 윗줄(v2_board_topbar_z, 1440x64 CSS, dsf 3) : 왼쪽 [MeAI 홈]·게시판 / 오른쪽 [글씨 확대]
im = Image.open(f'{H}/v2_board_topbar_z.png').convert('RGB')
save(im.crop((16*3, 8*3, 445*3, 58*3)), 'fix_c_board_top_left')
save(im.crop((1292*3, 8*3, 1428*3, 58*3)), 'fix_c_board_top_right')

# [45] 대문 [고객 동의] 팝업만 : 팝업 경계 x48~1007, y48~531 (모서리 반지름 약 32px) 밖은 흰색으로
im = Image.open(f'{F}/gate010/12_consent_modal.png').convert('RGB')
c = im.crop((48, 48, 1008, 532))
mask = Image.new('L', c.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, c.width-1, c.height-1], radius=32, fill=255)
out = Image.new('RGB', c.size, (255, 255, 255)); out.paste(c, (0, 0), mask)
save(out, 'fix_c_consent_modal')

# [45] 고객찾기 [사전조회동의 요청하기] 버튼 + 아래 안내 두 줄 (32_right_panel_kimminsu 에서)
im = Image.open(f'{F}/find010/32_right_panel_kimminsu.png').convert('RGB')
save(im.crop((4, 560, 826, 818)), 'fix_c_consent_request_btn')
