# 영업 플라이휠 묶음(PPT + 흐름 시연판 + 시연판이 띄우는 도구 파일)을 압축 파일 하나로 만든다.
# 쓰는 법 : python3 scripts/build_flow_kit.py            → dist/meai_flywheel_kit.zip
# 시연판(flow.html)은 옆 폴더의 도구 파일을 불러 쓰므로 저장소와 같은 폴더 구조 그대로 넣는다.
import os, sys, zipfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist', 'meai_flywheel_kit.zip')
TOP = 'meai_flywheel_kit'

FILES = [
    'flow.html', 'index.html', 'tool.html', 'tool_body.js', 'gloss.js',
    'products.html', 'prompts.html', '통합치료비.html', '명패생성기.html',
    'assets/pretendard-subset.woff2', 'assets/Pretendard-OFL.txt',
    'dist/meai_home_nudge_v5.html', 'dist/unse_saju_tarot.html',
    'dist/simple_ins_exception_guide_2610.pdf', 'dist/surgery_benefit_kcd_2610.xlsx',
    'docs/guidebook_proto.html', 'flow/README.md',
] + sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, 'flow', '*.jpg'))) \
  + sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, 'ui', 'mascots', '*.webp')))
PPT = {'PPT/meai_flywheel_deck.pptx': 'dist/meai_flywheel_deck.pptx', 'PPT/meai_flywheel_deck.pdf': 'dist/meai_flywheel_deck.pdf'}

README = """영업 플라이휠 묶음 · 세일즈혁신TF
플라이휠, 영업지원도구를 통한 영업프로세스 선순환

1. PPT 폴더
   - meai_flywheel_deck.pptx : 발표용 35장(장마다 그림 한 장 + 발표자 메모)
   - meai_flywheel_deck.pdf  : 미리보기 · 배포용

2. 흐름 시연판 : flow.html
   - 압축을 다 푼 뒤 이 폴더(meai_flywheel_kit)의 flow.html 을 크롬이나 엣지로 엽니다(더블클릭). 인터넷 없이 됩니다.
   - 가상 고객 김하늘 님의 한 바퀴(고객발굴 → 터치 → 클로징 → 계약체결 → 관리·소개 → 새 고객발굴)를
     22장면으로 넘기며, 장면마다 실제 도구 화면을 띄웁니다. 화면 안을 직접 눌러 시연합니다.
   - 아래 「다음」 · 「이전」 단추로 넘깁니다(도구 화면을 누른 뒤에는 키보드가 그 도구로 갑니다).
     「장면 목록」 · 「말할 거리」 · 「전체 화면」 단추가 위에 있습니다.
   - 폴더 안의 파일 이름이나 위치를 바꾸지 마세요. 시연판이 옆 파일을 불러 씁니다.
     (압축 프로그램 미리보기 창에서 바로 열면 옆 파일을 못 찾습니다. 꼭 압축을 푼 뒤 여세요.)

3. 함께 든 도구(시연판이 띄우는 원본 그대로)
   index.html(대문) · tool.html(특약검색기 · 보상시뮬레이터, tool_body.js 와 함께) · products.html(상품 라인업)
   통합치료비.html · prompts.html(프롬프트) · 명패생성기.html
   dist/meai_home_nudge_v5.html(MeAI 홈 넛지 목업) · dist/unse_saju_tarot.html(오늘의 운세)
   docs/guidebook_proto.html(세일즈북 생성기) · dist/simple_ins_exception_guide_2610.pdf · dist/surgery_benefit_kcd_2610.xlsx

참고
- 사내 교육 · 업무용입니다. 고객에게 배포하지 않습니다.
- 화면 속 고객 이름과 금액은 모두 예시입니다. 실제 보장과 지급금액은 약관으로 확인하세요.
- MeAI 홈 넛지는 목업, 스마트 제안서 · GA 디자인판 · 세일즈북 생성기는 프로토타입입니다.
"""

missing = [f for f in FILES + list(PPT.values()) if not os.path.exists(os.path.join(ROOT, f))]
if missing:
    sys.exit('없는 파일 : ' + ', '.join(missing))
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.writestr(f'{TOP}/README_FIRST.txt', README.replace('\n', '\r\n').encode('utf-8-sig'))
    for f in FILES:
        z.write(os.path.join(ROOT, f), f'{TOP}/{f}')
    for arc, src in PPT.items():
        z.write(os.path.join(ROOT, src), f'{TOP}/{arc}')
raw = sum(os.path.getsize(os.path.join(ROOT, f)) for f in FILES + list(PPT.values()))
print(f'{os.path.relpath(OUT, ROOT)} · 파일 {len(FILES) + len(PPT) + 1}개 · 원래 {raw / 1e6:.1f}MB → 압축 {os.path.getsize(OUT) / 1e6:.1f}MB')
