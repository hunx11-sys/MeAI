# 실제 MeAI 운영 화면 캡처(소유자 제공 PPT 11장) → 가이드북용 정리
#  - 브라우저 제목줄·주소창(접속 토큰이 보임)을 잘라 냄
#  - 실제 이름(담당 고객 · 리포트의 이름 · 담당 FP)은 회색 막대로 가림
#  - 왼쪽 메뉴 '관리자 화면 접속'(관리자 계정에만 보임)과 사내 업무 제목 한 줄('…판촉물…')은 바탕색으로 지움
#  - 요약 리포트 편집 화면의 리포트 본문(타사명·'해지 검토' 문장이 있음)은 흐리게 — 왼쪽 설정 패널과 머리글만 또렷이
#  - 맞춤대화 시작 화면(6번)의 계약 가입기간·납입 횟수·납입률은 줄 바탕색으로 지움(이름을 가려도 다시 알아볼 수 있는 조합)
#  - 보장분석 답(8번) 소제목의 '리모델링'(갈아타기 권유로 읽힐 수 있음)은 흰색으로 지움
#  - 10번(증권별 해지/유지 판단)은 쓰지 않음 — 해지·전환 권유로 읽힐 수 있어 가이드북 원칙상 제외
# python prep_real.py <캡처 PNG 폴더(s01_0.png …)> <출력 폴더>
import sys, os
from PIL import Image, ImageDraw, ImageFilter
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
NAMES = {1:'r01_general_home', 2:'r02_prompt_lib_reco', 3:'r03_prompt_lib_recent', 4:'r04_general_answer', 5:'r05_report_select',
         6:'r06_custom_start', 7:'r07_custom_info', 8:'r08_custom_answer', 9:'r09_custom_precontract', 11:'r11_report_edit'}
GRAY = (229,231,235)
def bar(im, box):
    ImageDraw.Draw(im).rounded_rectangle(box, radius=6, fill=GRAY)
for n, name in NAMES.items():
    im = Image.open(os.path.join(SRC, 's%02d_0.png' % n)).convert('RGB')
    if 6 <= n <= 10: bar(im, (20, 214, 142, 252))                  # 왼쪽 위 '담당 고객 ○○○님'
    if n == 11:   # 리포트 '이름' · 성별 · 연령 · '담당 FP'
        for b in ((519, 184, 562, 206), (608, 184, 624, 206), (669, 184, 728, 206), (791, 184, 836, 206)): bar(im, b)
    def wipe(box):  # 왼쪽 메뉴 바탕색으로 덮기
        c = im.getpixel((12, box[1]+12)); ImageDraw.Draw(im).rectangle(box, fill=c)
    if n in (1,2,3,4): wipe((24, 284, 176, 312))                   # '관리자 화면 접속'(잘라 내기 전 좌표 y+62)
    if n in (1,2,3): wipe((24, 705, 286, 730))                     # '직업·연령별 판촉물 …' 대화 제목
    if n == 4: wipe((24, 749, 286, 774))
    if 6 <= n <= 9: wipe((24, 491, 176, 517))
    if n in (1,2,3): wipe((24, 425+62, 286, 446+62))                # 사내 캠페인 대화 제목 한 줄
    if n == 4: wipe((24, 469+62, 286, 490+62))
    if n == 8: ImageDraw.Draw(im).rectangle((529, 311, 588, 329), fill=(255,255,255))   # '리모델링' 소제목 단어
    if n == 11:
        box = (458, 405, 1132, 959); im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(6)), box[:2])
    if n <= 10: im = im.crop((0, 62, im.width, im.height))       # 브라우저 제목줄·주소창(토큰) 잘라 냄
    if n == 6:   # 계약 세 줄의 가입기간 · 납입 횟수 · 납입률(잘라 낸 뒤 좌표)
        d = ImageDraw.Draw(im); pink = im.getpixel((560, 700))
        for dy in (0, 97, 194):
            d.rectangle((579, 711+dy, 730, 729+dy), fill=pink); d.rectangle((1090, 697+dy, 1157, 717+dy), fill=pink); d.rectangle((1210, 696+dy, 1247, 713+dy), fill=pink)
    im.save(os.path.join(OUT, name + '.png'))
    print(name, im.size)
