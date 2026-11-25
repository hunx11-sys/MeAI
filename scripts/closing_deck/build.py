# -*- coding: utf-8 -*-
"""영업지원도구 인터넷판 운영 결산 PPT — 성과 · 애용 이유 · 사내망 이관(IT) 참고

  python3 scripts/closing_deck/build.py <캡처 폴더> <PretendardVariable.woff2> [출력 폴더=dist]
    → dist/meai_tools_web_closing_2611.pptx · .pdf  (장마다 통이미지 + 발표자 메모 · 1600x900 화면을 2배로 찍음)

캡처 폴더 : index · tool · sim_c16 · itc · products · prompts · nameplate (1440x900 @2x, 사내처럼 파일로 열어 찍음)
숫자 출처 : 사용 숫자 = 사용 통계 대시보드 익명 집계(2026.6.22~10.21 · 공모전 제출 PPT docs/meritz_tools6_contest_deck_2610 과 같은 값).
            자료 규모 · 갱신 횟수 · 파일 크기 = 저장소(2026.11.25). 기대효과 = 공모전 산식의 가정값.
디자인 : design/DESIGN-MeAI.md + DESIGN-토스.md · 장표 글은 음 · 임 개조식(소유자 덱 규칙)
"""
import base64, html, json, os, sys
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Emu

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAP, FONT = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'dist')
NAME = 'meai_tools_web_closing_2611'
W, H = 1600, 900

def uri(path, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(open(path, 'rb').read()).decode())
def doll(name): return uri(os.path.join(ROOT, 'ui', 'mascots', name), 'image/webp')
def cap(name): return uri(os.path.join(CAP, name + '.png'), 'image/png')
e = html.escape

CSS = '''
@font-face{font-family:P;src:url(%s) format("woff2");font-weight:45 930}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1600px;height:900px;overflow:hidden;background:#fff;font-family:P,sans-serif;color:#191F28;word-break:keep-all;-webkit-font-smoothing:antialiased}
.sl{position:relative;width:1600px;height:900px;padding:64px 80px 0}
.kick{font-size:18px;font-weight:600;color:#C8102E;letter-spacing:0}
.ttl{margin-top:10px;font-size:42px;line-height:1.28;font-weight:700;letter-spacing:-.025em}
.lead{margin-top:12px;font-size:20px;line-height:1.55;color:#4E5968}
.foot{position:absolute;left:80px;right:80px;bottom:28px;display:flex;justify-content:space-between;font-size:13px;color:#8B95A1}
.foot b{color:#C8102E;font-weight:600}
.src{position:absolute;left:80px;right:80px;bottom:56px;font-size:13px;color:#6B7684}
.body{margin-top:36px}
.row{display:flex;gap:20px}
.card{background:#F9FAFB;border:1px solid #EEF0F2;border-radius:20px;padding:26px 28px}
.card.w{background:#fff;border-color:#E5E8EB}
.num{font-size:56px;font-weight:700;letter-spacing:-.03em;line-height:1.1;font-variant-numeric:tabular-nums}
.num small{font-size:24px;font-weight:500;color:#4E5968;margin-left:4px;letter-spacing:0}
.num.r{color:#C8102E}
.lab{margin-top:10px;font-size:17px;color:#4E5968;line-height:1.5}
.h3{font-size:24px;font-weight:700;letter-spacing:-.015em;line-height:1.35}
.p{margin-top:10px;font-size:17px;line-height:1.6;color:#4E5968}
.tag{display:inline-flex;align-items:center;height:30px;padding:0 12px;border-radius:8px;background:#FDECEE;color:#A50D26;font-size:14px;font-weight:600}
.tag.g{background:#F2F4F6;color:#4E5968}
.dot{display:inline-grid;place-items:center;width:40px;height:40px;border-radius:12px;background:#C8102E;color:#fff;font-weight:700;font-size:19px;flex:none}
table{border-collapse:collapse;width:100%%;font-size:17px}
th{background:#F9FAFB;color:#4E5968;font-weight:600;text-align:left;padding:13px 16px;border-bottom:1px solid #D1D6DB;font-size:15px}
td{padding:13px 16px;border-bottom:1px solid #F2F4F6;line-height:1.45;vertical-align:top}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.shot{border-radius:16px;border:1px solid #E5E8EB;box-shadow:0 12px 32px rgba(15,23,42,.10);overflow:hidden;background:#fff}
.shot img{display:block;width:100%%}
.em{color:#C8102E}
.bar{height:14px;border-radius:999px;background:#F2F4F6;overflow:hidden;display:flex}
.bar i{display:block;height:100%%}
'''

S = []   # (html, 메모)
def slide(body, notes, kick='', title='', lead='', src='', part='', z=1.0):
    head = ''
    if title:
        head = '<div class="kick">%s</div><div class="ttl">%s</div>%s' % (kick, title, '<div class="lead">%s</div>' % lead if lead else '')
    foot = '<div class="foot"><span>MeAI 영업지원도구 인터넷판 운영 결산 · 세일즈혁신TF</span><span><b>%s</b>　@@N@@</span></div>' % part
    srch = '<div class="src">%s</div>' % src if src else ''
    bz = ' style="width:%dpx;zoom:%s"' % (round(1440 / z), z) if z != 1.0 else ''      # 내용이 적은 장은 글자를 키워 장을 채운다(폭은 그대로 1440)
    S.append(('<div class="sl">%s<div class="body"%s>%s</div>%s%s</div>' % (head, bz, body, srch, foot), notes))

def full(body, notes):
    S.append((body, notes))

# ── 1. 표지 ────────────────────────────────────────────────
full('''<div class="sl" style="padding:0;background:#fff">
  <div style="position:absolute;inset:0;background:radial-gradient(46%% 60%% at 12%% 10%%,rgba(200,16,46,.09),transparent 70%%),radial-gradient(40%% 50%% at 92%% 20%%,rgba(109,91,214,.08),transparent 70%%),radial-gradient(50%% 50%% at 70%% 100%%,rgba(242,183,5,.08),transparent 70%%)"></div>
  <div style="position:absolute;left:100px;top:170px;width:800px">
    <span class="tag">2026.6.22 ~ 2026.11.25 · 157일</span>
    <div style="margin-top:28px;font-size:68px;font-weight:700;letter-spacing:-.035em;line-height:1.2">MeAI 영업지원도구<br><span class="em">인터넷판 운영 결산</span></div>
    <div style="margin-top:26px;font-size:26px;color:#4E5968;line-height:1.5">성과 · 현장이 애용한 이유 · 사내망 이관 참고자료</div>
    <div style="margin-top:56px;font-size:19px;color:#6B7684">2026. 11　세일즈혁신TF</div>
  </div>
  <img src="%s" style="position:absolute;right:56px;bottom:0;width:660px;height:auto">
</div>''' % doll('group_hello.webp'),
'MeAI 영업지원도구 인터넷판 운영 결산 보고를 시작하겠습니다. 6월 22일부터 11월 25일까지 157일 동안 깃허브 주소로 운영한 영업지원도구의 성과와, 현장이 이 도구를 왜 애용했는지, 그리고 사내망으로 옮길 때 IT에 전달할 내용을 한 번에 정리했습니다.')

# ── 2. 이 자료는 ───────────────────────────────────────────
slide('''<div class="row" style="gap:24px">
  <div class="card" style="flex:1"><span class="tag">용도 1</span><div class="h3" style="margin-top:16px">내부 성과 보고</div>
    <div class="p">공식 배포 · 교육 없이 현장에서 퍼진 사용 성과<br>현장이 애용한 이유와 상담 장면 변화<br>데이터 규모 · 운영 방식 · 기대효과(가정값)</div></div>
  <div class="card" style="flex:1"><span class="tag">용도 2</span><div class="h3" style="margin-top:16px">사내망 이관 IT 참고</div>
    <div class="p">지금 구조(서버 없는 정적 파일) · 파일 목록<br>데이터 갱신 흐름 · 점검 도구<br>사내망에서 바꿔야 할 바깥 연결 · 사용 기록 이어받기</div></div>
</div>
<div class="card w" style="margin-top:24px;display:flex;gap:20px;align-items:center">
  <span class="dot">!</span>
  <div><div class="h3" style="font-size:21px">2026.11.25 인터넷판(깃허브 주소) 종료</div>
  <div class="p" style="margin-top:6px">회사 리스크진단파트 의견(외부 깃허브 주소가 피싱 사이트로 오인될 수 있음) 반영 · 주소로 들어오면 종료 인사 화면 표시 · 개발은 계속하며 MeAI 홈에 이식해 사내 정식 서비스로 전환 예정</div></div>
</div>''',
'이 자료는 두 가지 용도로 만들었습니다. 첫째는 내부 성과 보고입니다. 공식 배포나 교육 없이 현장에서 퍼진 사용 성과와, 현장이 왜 이 도구를 애용했는지를 담았습니다. 둘째는 사내망 이관 때 IT에 전달할 참고자료입니다. 지금 구조와 데이터 갱신 흐름, 사내망에서 바꿔야 할 부분을 정리했습니다. 인터넷판은 리스크진단파트 의견에 따라 11월 25일 종료했고, 개발은 계속해서 MeAI 홈에 이식할 예정입니다.',
'00 · 이 자료는', '성과 보고와 IT 이관 참고를 한 권으로', '', '', '', z=1.32)

# ── 3. 한 장 요약 ─────────────────────────────────────────
def tile(n, u, lab, red=False, w='1'):
    return '<div class="card" style="flex:%s;min-height:178px"><div class="num%s">%s<small>%s</small></div><div class="lab">%s</div></div>' % (w, ' r' if red else '', n, u, lab)
slide('''<div class="row">%s%s%s</div><div class="row" style="margin-top:20px">%s%s%s%s</div>''' % (
    tile('32,812', '건', '누적 사용 · 122일 집계(6.22~10.21)', True), tile('2,000', '건+', '하루 최고 사용(10.21)'), tile('269', '건', '하루 평균 사용(122일)'),
    tile('157', '일', '인터넷판 운영(6.22~11.25)'), tile('1,149', '종', '특약 · 세부보장 포함 1,842건'), tile('78', '회', '화면 · 데이터 갱신(9.15~)'), tile('0', '원', '개발 · 서버 · 라이선스', True)),
'한 장으로 요약하면 이렇습니다. 사용 통계를 집계한 122일 동안 누적 사용이 32,812건, 하루 평균 269건이었고, 10월 21일에는 하루 사용이 2,000건을 넘었습니다. 인터넷판은 157일 운영했고, 6개 상품의 특약 1,149종을 세부보장까지 1,842건 담았습니다. 저장소 기록으로 9월 15일 이후에만 화면과 데이터를 78번 고쳤고, 개발 · 서버 · 라이선스 비용은 0원입니다. 사용 건수는 로그인 없는 익명 집계라 사람 수가 아니라 사용 건수입니다.',
'00 · 한 장 요약', '공식 배포 없이 157일, 현장이 직접 퍼뜨린 도구', '', '사용 숫자 : 사용 통계 대시보드 익명 집계(2026.6.22~10.21 · 사람 수가 아니라 조회 · 검색 · 클릭 건수) · 자료 규모 · 갱신 횟수 : 저장소 기록(2026.11.25)', '', z=1.22)

# ── 4. 간지 ──────────────────────────────────────────────
def section(no, title, sub, mascot, notes):
    full('''<div class="sl" style="padding:0;background:#F7F8FA">
  <div style="position:absolute;left:110px;top:300px">
    <div style="font-size:22px;font-weight:700;color:#C8102E">PART %s</div>
    <div style="margin-top:14px;font-size:64px;font-weight:700;letter-spacing:-.035em">%s</div>
    <div style="margin-top:18px;font-size:24px;color:#4E5968">%s</div></div>
  <img src="%s" style="position:absolute;right:140px;top:220px;height:440px;width:auto">
  <div class="foot"><span>MeAI 영업지원도구 인터넷판 운영 결산 · 세일즈혁신TF</span><span>@@N@@</span></div></div>''' % (no, title, sub, doll(mascot)), notes)

section('1', '157일의 성과', '얼마나 쓰였고, 무엇을 찾았나', 'success_thumbs.webp', '첫 번째로 157일 동안의 성과를 보겠습니다. 얼마나 쓰였고, 현장이 무엇을 찾았는지입니다.')

# ── 5. 타임라인 ──────────────────────────────────────────
TL = [('2026.6.22', '인터넷판 공개 · 사용 기록 시작', '주소 하나로 공유 · 설치 · 로그인 없음'),
      ('2026.9', '6개 상품 전수 감사', '현장 제보로 시작 · 325건 바로잡음'),
      ('2026.9.15', '지금 저장소로 이전', '이후 화면 · 데이터 갱신 78회 기록'),
      ('2026.10.21', '하루 사용 2,000건 돌파', '공모전 제출 · 누적 32,812건'),
      ('2026.10.22', '7개 화면 한 사이트로 통일', '공통 메뉴 · 디자인 · 휴대폰 최적화'),
      ('2026.11.1', '2610 약관 반영', '신담보 반영 · 판매중지 담보 정리'),
      ('2026.11.13~19', '질병 검색 사전 · 통합치료비Ⅱ', '대장용종 → 결장의 용종 등 185개'),
      ('2026.11.25', '인터넷판 종료', '종료 인사 화면 · 사내망 이관 준비')]
rows = ''.join('<div style="display:flex;gap:22px;align-items:flex-start;padding:13px 0;border-bottom:1px solid #F2F4F6">'
               '<div style="width:170px;flex:none;font-size:18px;font-weight:700;color:%s;font-variant-numeric:tabular-nums">%s</div>'
               '<div style="flex:1;font-size:19px;font-weight:600">%s</div><div style="width:520px;flex:none;font-size:17px;color:#6B7684">%s</div></div>'
               % ('#C8102E' if i in (0, 3, 7) else '#4E5968', d, t, s) for i, (d, t, s) in enumerate(TL))
slide(rows,
'운영 흐름입니다. 6월 22일 인터넷판을 공개하면서 사용 기록을 시작했고, 9월에는 현장 제보로 시작한 6개 상품 전수 감사에서 325건을 바로잡았습니다. 10월 21일에 하루 사용 2,000건을 넘었고, 다음 날 일곱 개 화면을 한 사이트로 통일했습니다. 11월 1일에 2610 약관을 반영했고, 11월 중순에는 일상 병명으로도 찾는 질병 검색 사전과 특정순환계질환 통합치료비Ⅱ를 넣었습니다. 그리고 11월 25일 인터넷판을 종료했습니다.',
'PART 1 · 운영 흐름', '6월 공개부터 11월 종료까지', '', '날짜 : 공모전 제출 PPT(2610) · 저장소 기록 · 작업 규칙 문서', 'PART 1', z=1.26)

# ── 6. 사용 성과 ─────────────────────────────────────────
slide('''<div class="row">%s%s%s</div>
<div class="card w" style="margin-top:22px">
  <div class="h3" style="font-size:21px">도구별 사용 비중</div>
  <div class="bar" style="margin-top:18px;height:22px"><i style="width:32%%;background:#C73D1C"></i><i style="width:30%%;background:#23874C"></i><i style="width:38%%;background:#D1D6DB"></i></div>
  <div style="display:flex;gap:36px;margin-top:14px;font-size:17px;color:#4E5968">
    <span><b style="color:#C73D1C">특약검색기 32%%</b></span><span><b style="color:#23874C">보상시뮬레이터 30%%</b></span><span>나머지 4개 도구 38%%</span>
    <span style="margin-left:auto">두 도구가 사용의 <b style="color:#191F28">60%% 이상</b></span></div>
</div>''' % (tile('14,049', '건', '검색 · 질병 · 특약을 찾아본 횟수', True), tile('5,240', '건', '특약 상세조회 · 약관 본문까지 열어 봄'), tile('5,076', '건', '도구를 연 횟수')),
'사용 내용을 나눠 보면, 검색이 14,049건으로 가장 많고, 약관 본문까지 열어 본 특약 상세조회가 5,240건, 도구를 연 횟수가 5,076건입니다. 찾고, 근거를 열어 보는 사용이 대부분이라는 뜻입니다. 도구별로는 특약검색기 32%, 보상시뮬레이터 30%로 두 도구가 전체 사용의 60% 이상을 차지했습니다.',
'PART 1 · 사용 성과', '찾고, 약관 근거를 열어 보는 데 쓰였음', '', '사용 통계 대시보드 익명 집계(2026.6.22~10.21 · 122일) · 10.22~11.25 수치는 사용 통계 화면에서 최종 확정 필요', 'PART 1', z=1.28)

# ── 7. 무엇을 찾았나 ─────────────────────────────────────
slide('''<div class="row" style="gap:24px">
  <div class="card" style="flex:1"><span class="tag">상세조회 상위 특약</span>
    <div style="margin-top:20px;font-size:64px;font-weight:700;letter-spacing:-.03em">8개 중 <span class="em">7개</span></div>
    <div class="p" style="font-size:19px">가 <b style="color:#191F28">통합치료비 계열</b><br>가장 어렵고 가장 많이 찾는 특약 → 통합치료비 시뮬레이터를 따로 만든 근거</div></div>
  <div class="card" style="flex:1"><span class="tag">많이 검색한 질병</span>
    <table style="margin-top:14px;font-size:19px"><tr><td style="width:56px;font-weight:700;color:#C8102E">1</td><td>위 · 대장 등 소화기암</td></tr>
    <tr><td style="font-weight:700;color:#C8102E">2</td><td>양성종양</td></tr><tr><td style="font-weight:700;color:#C8102E">3</td><td>기타 뇌혈관질환</td></tr><tr><td style="font-weight:700;color:#C8102E">4</td><td>유방암</td></tr></table></div>
</div>
<div class="card w" style="margin-top:22px;font-size:19px;line-height:1.6"><b>사용 통계가 다음 도구를 가리켰음</b> · 많이 찾는 것을 먼저 쉽게 만드는 방식으로 화면을 고쳐 옴(통합치료비 시뮬레이터 · 수술비 비교 · 질병 검색 사전)</div>''',
'현장이 무엇을 찾았는지도 사용 통계로 보입니다. 가장 많이 상세조회된 특약 상위 8개 중 7개가 통합치료비 계열이었습니다. 가장 어렵고 가장 많이 찾는 특약이라 통합치료비 시뮬레이터를 따로 만들었습니다. 많이 검색한 질병은 위 · 대장 같은 소화기암, 양성종양, 기타 뇌혈관질환, 유방암 순이었습니다. 이렇게 사용 통계를 보고 다음에 고칠 것을 정해 왔습니다.',
'PART 1 · 무엇을 찾았나', '현장이 가장 많이 찾은 것은 통합치료비와 소화기암', '', '사용 통계 대시보드 익명 집계(2026.9 집계 · 공모전 제출 PPT 와 같은 값)', 'PART 1', z=1.24)

# ── 8. 도구 6종 ─────────────────────────────────────────
TOOLS = [('tool', '특약검색기', '병명 · 코드 · 초성 · 일상 병명으로 특약 찾기 · 약관 원문 · 보장 분석'),
         ('sim_c16', '보상시뮬레이터', '질병 하나로 진단~사망 10단계 받을 수 있는 특약 정리'),
         ('itc', '통합치료비 시뮬레이터', '통합치료비 13종 · 치료 과정별 1년 받는 금액'),
         ('products', '상품 라인업', '장기상품 50종 · 알릴의무 · 간편보험 예외질환 판정'),
         ('prompts', '프롬프트 라이브러리', 'MeAI 질문 272개 · 영업 단계별 한 번에 복사'),
         ('nameplate', '명패 제작기', '엑셀 명단 한 장 → 삼각대 명패 · 라벨 인쇄')]
cells = ''.join('<div style="width:calc(33.33%% - 20px)"><div class="shot" style="height:196px"><img src="%s" style="height:100%%;width:auto;min-width:100%%;object-fit:cover;object-position:top"></div>'
                '<div style="margin-top:12px;font-size:20px;font-weight:700">%s</div><div style="margin-top:4px;font-size:15px;color:#6B7684;line-height:1.45">%s</div></div>'
                % (cap(f), t, d) for f, t, d in TOOLS)
slide('<div style="display:flex;flex-wrap:wrap;gap:26px 30px">%s</div>' % cells,
'도구 여섯 가지를 한 장에 모았습니다. 특약검색기, 보상시뮬레이터, 통합치료비 시뮬레이터가 상담 중 즉답을 맡고, 상품 라인업은 상품 선택과 간편보험 판정, 프롬프트 라이브러리는 MeAI 질문, 명패 제작기는 행사 준비를 맡습니다. 여기에 사용 통계 화면까지 일곱 개 화면이 대문 하나에서 이어집니다.',
'PART 1 · 도구 6종', '상담 전 · 중 · 후를 여섯 도구가 나눠 맡음', '', '화면 : 2026.11.25 저장소 판(사내 파일로 연 화면)', 'PART 1')

# ── 9. 자료 규모 ─────────────────────────────────────────
DATA = [('1,149', '종', '특약(6개 상품) · 세부보장 포함 1,842건'), ('293', '개', '약관 분류표(별표) · 특약마다 질병코드 연결'),
        ('1,302', '개', '공식 질병명(코드명)'), ('185', '개', '일상 병명 사전 · 동의어 100묶음 · 별칭 30'),
        ('907', '개', '보험용어 쉬운 설명'), ('50', '종', '장기상품 라인업 · 간편보험 5유형 판정'),
        ('272', '개', 'MeAI 프롬프트'), ('13', '종', '통합치료비 특약 금액표(암 9 · 뇌심 4)')]
grid = ''.join('<div class="card" style="width:calc(25%% - 14px);padding:24px 26px;min-height:150px"><div class="num" style="font-size:44px">%s<small>%s</small></div><div class="lab" style="font-size:16px">%s</div></div>' % d for d in DATA)
slide('<div style="display:flex;flex-wrap:wrap;gap:18px">%s</div>' % grid,
'도구 안에 담긴 자료 규모입니다. 6개 상품의 특약 1,149종을 세부보장까지 1,842건, 약관 분류표 293개와 공식 질병명 1,302개를 담았습니다. 일상 병명 사전 185개와 보험용어 쉬운 설명 907개, 장기상품 50종, MeAI 프롬프트 272개, 통합치료비 13종의 금액표가 들어 있습니다. 이 자료는 사내망으로 옮길 때 그대로 넘어가는 자산입니다.',
'PART 1 · 담긴 자료', '약관 원문을 그대로 옮긴 영업 자료 자산', '', '저장소 기록(2026.11.25) · tool.html 데이터 · gloss.js · ui/meai-lex.js · products · prompts · 통합치료비 화면', 'PART 1', z=1.3)

# ── 10. 간지 2 ──────────────────────────────────────────
section('2', '현장이 애용한 이유', '왜 공식 배포 없이도 퍼졌나', 'merry_ok.webp', '두 번째로, 현장이 이 도구를 왜 애용했는지 보겠습니다. 공식 배포나 교육이 없었는데도 영업가족끼리 주소를 주고받으며 퍼졌습니다.')

# ── 11. 애용 이유 6 ─────────────────────────────────────
WHY = [('고객 앞에서 바로 답함', '병명 · 코드 · 초성 · 일상 병명 무엇으로 쳐도 찾음 · 「확인하고 연락드릴게요」 대신 그 자리에서 답', '검색 14,049건'),
       ('약관 원문이 근거', '특약 본문 · 별표 · 질병코드를 원문 그대로 보여 줌 · 설계사마다 다르던 설명이 같아짐', '상세조회 5,240건'),
       ('보장 공백이 눈에 보임', '질병 하나로 진단~사망 단계별 건수 · 0건인 단계가 곧 공백 · 추가 제안이 권유가 아닌 설명이 됨', '보상시뮬레이터 30%'),
       ('가장 어려운 통합치료비를 숫자로', '치료 과정만 고르면 특약별 1년 금액 · 0원인 이유까지 문장으로', '상세조회 상위 8개 중 7개'),
       ('설치 · 로그인 없이 주소 하나', 'PC · 휴대폰 같은 화면 · 즐겨찾기 하나로 끝 · 사내망엔 파일 하나', '공식 배포 0 · 입소문 확산'),
       ('현장 제보가 바로 반영', 'TF 가 기획 · 데이터 · 개발을 직접 해 오류 · 신담보를 당일 반영 · 약관 개정도 즉시', '갱신 78회 · 감사 325건')]
cards = ''.join('<div class="card" style="width:calc(33.33%% - 14px);padding:24px 26px;display:flex;flex-direction:column"><div style="display:flex;gap:14px;align-items:center"><span class="dot">%d</span><div class="h3" style="font-size:21px">%s</div></div>'
                '<div class="p" style="font-size:16px;flex:1">%s</div><div style="margin-top:14px"><span class="tag">%s</span></div></div>' % (i + 1, t, d, g) for i, (t, d, g) in enumerate(WHY))
slide('<div style="display:flex;flex-wrap:wrap;gap:18px 20px">%s</div>' % cards,
'현장이 애용한 이유를 여섯 가지로 정리했습니다. 첫째, 고객 앞에서 바로 답할 수 있습니다. 병명이든 코드든 초성이든 찾아 주니 확인하고 연락드리겠다는 말이 사라졌습니다. 둘째, 약관 원문이 근거라 설명이 설계사마다 달라지지 않습니다. 셋째, 보상시뮬레이터로 보장 공백이 눈에 보여 추가 제안이 설명이 됩니다. 넷째, 가장 어려운 통합치료비를 숫자로 보여 줍니다. 다섯째, 설치나 로그인 없이 주소 하나로 휴대폰에서도 됩니다. 여섯째, 현장 제보가 당일 반영됩니다. 오른쪽 아래 꼬리표는 각 이유를 뒷받침하는 사용 숫자입니다.',
'PART 2 · 애용 이유', '현장이 이 도구를 계속 연 여섯 가지 이유', '', 'TF 분석 · 근거 숫자는 사용 통계 대시보드(2026.6.22~10.21) · 저장소 기록', 'PART 2', z=1.2)

# ── 12. 상담 장면 변화 ───────────────────────────────────
QA = [('갑상선암도 진단비 나와요?', '약관 찾아보고 연락', 'C73 검색 한 번 · 약관 근거와 함께 즉답', '특약검색기'),
      ('위암이면 뭘 받을 수 있어요?', '가입 특약 목록을 읽으며 짐작', '진단~사망 단계별로 빠짐없이', '보상시뮬레이터'),
      ('통합치료비는 얼마나 나와요?', '즉답 불가', '치료 과정 고르면 1년 합계', '통합치료비'),
      ('당뇨 있어도 가입돼요?', '심사 넣어 보고 연락', '간편보험 5유형 판정 · 대안 안내', '상품 라인업'),
      ('뇌졸중이면 다 되는 거죠?', '「네」(오안내 위험)', '빠진 질병을 코드로 보여 줌', '특약검색기'),
      ('이 병원도 상급종합이에요?', '검색해 보고 연락', '상급종합 지도에서 바로', '특약검색기'),
      ('보장분석 정리해 주세요', '직접 작성', '결과 + 프롬프트로 MeAI 문장', '프롬프트')]
tr = ''.join('<tr><td style="font-weight:600">%s</td><td style="color:#8B95A1">%s</td><td>%s</td><td><span class="tag g">%s</span></td></tr>' % q for q in QA)
slide('<table><tr><th style="width:30%%">고객 질문</th><th style="width:22%%">예전</th><th>지금</th><th style="width:15%%">쓰는 도구</th></tr>%s</table>' % tr,
'상담 장면이 이렇게 바뀌었습니다. 갑상선암 진단비 질문에는 코드 검색 한 번으로 약관 근거와 함께 답하고, 위암 보상 전체는 단계별로 빠짐없이 보여 줍니다. 통합치료비 금액, 당뇨 고객의 가입 가능 여부, 뇌졸중 보장 범위, 상급종합병원 여부까지 예전에는 확인하고 연락드리던 질문들을 이제는 상담 자리에서 화면을 보여 주며 답합니다.',
'PART 2 · 상담 장면 변화', '「확인하고 연락드릴게요」가 사라짐', '', '도구 화면 기능 기준(2026.11.25)', 'PART 2', z=1.22)

# ── 13~15. 화면으로 보는 이유 ─────────────────────────────
def screen(capname, kick, title, pts, notes, src):
    li = ''.join('<div style="display:flex;gap:16px;margin-top:30px"><span class="dot" style="width:40px;height:40px;font-size:18px;border-radius:12px">%d</span><div style="font-size:23px;line-height:1.5;color:#333D4B">%s</div></div>' % (i + 1, p) for i, p in enumerate(pts))
    slide('<div class="row" style="gap:40px;align-items:flex-start"><div class="shot" style="width:900px"><img src="%s"></div><div style="flex:1">%s</div></div>' % (cap(capname), li),
          notes, kick, title, '', src, 'PART 2')
screen('tool', 'PART 2 · 화면으로 보면 ①', '특약검색기 : 아무렇게나 쳐도 찾음',
       ['「뇌경색」만 쳐도 질병코드 · 연관 질병 · 연관 특약 자동완성', '초성(ㄱㅅㅅㅇ) · 일상 병명(대장용종 → 결장의 용종)도 찾음', '카드를 열면 약관 원문 · 별표 · 사각지대 · 상위호환까지'],
       '특약검색기 화면입니다. 뇌경색만 쳐도 질병코드와 연관 질병, 연관 특약이 바로 뜹니다. 초성이나 대장용종 같은 일상 병명으로도 찾고, 카드를 열면 약관 원문과 별표, 이 특약이 못 막는 사각지대와 상위호환 특약까지 보여 줍니다. 검색 14,049건의 대부분이 여기서 나왔습니다.', '화면 : 특약검색기(2026.11.25 판)')
screen('sim_c16', 'PART 2 · 화면으로 보면 ②', '보상시뮬레이터 : 보장 흐름이 한눈에',
       ['위암 → 받을 수 있는 특약 328개(상품별 704건)', '진단 · 검사 · 수술 · 입원 … 사망 10단계 건수', '예상 수술종류 · MeAI 조회 프롬프트 복사'],
       '보상시뮬레이터 화면입니다. 위암을 고르면 6개 상품에서 받을 수 있는 특약 328개, 상품별로 704건을 진단부터 사망까지 10단계로 나눠 보여 줍니다. 0건인 단계가 곧 보장 공백이라 추가 제안의 근거가 됩니다.', '화면 : 보상시뮬레이터(2026.11.25 판 · 위암 C16)')
screen('itc', 'PART 2 · 화면으로 보면 ③', '통합치료비 시뮬레이터 : 어려운 특약을 숫자로',
       ['질병과 치료 과정을 고르면 특약별 1년 금액 합계', '치료 단계마다 어느 특약에서 얼마 · 0원이면 이유', '가입금액별 비교 · 1년 이내 감액 · 5년 치료 계획'],
       '통합치료비 시뮬레이터 화면입니다. 질병과 치료 과정을 고르면 특약별로 1년 동안 받는 금액이 합산되고, 치료 단계마다 어느 특약에서 얼마가 나오는지, 안 나오면 왜인지 문장으로 나옵니다. 가장 많이 상세조회된 통합치료비를 누구나 같은 결과로 설명하게 해 줍니다.', '화면 : 통합치료비 시뮬레이터(2026.11.25 판 · 급성 심근경색 · 기본 조합)')

# ── 16. 신뢰 · 운영 · 기대효과 ────────────────────────────
slide('''<div class="row" style="gap:24px">
 <div class="card" style="flex:1.05"><div class="h3">데이터를 믿을 수 있는 이유</div>
  <div class="p" style="font-size:17px">· 판매 약관 원문(2610 판)에서 그대로 옮김<br>· 질병코드 · 금액은 추정하지 않음 · 없으면 빈칸<br>· 2026.9 전수 감사 325건 바로잡음<br>· 약관이 바뀌면 같은 스크립트로 다시 대조<br>· 표 · 사전 · 같은 이름 특약 자동 점검</div></div>
 <div class="card" style="flex:1"><div class="h3">운영 방식</div>
  <div class="p" style="font-size:17px">· 개발 · 서버 · 라이선스 0원<br>· 기획 · 데이터 · 개발 · 운영을 TF 가 직접<br>· 오류 · 신담보 당일 반영(갱신 78회)<br>· 고객 개인정보 받지도 저장하지도 않음</div></div>
 <div class="card" style="flex:1"><div class="h3">연간 기대효과 <span class="tag g" style="vertical-align:middle">가정값</span></div>
  <div class="num r" style="margin-top:12px;font-size:48px">6.91<small>억원</small></div>
  <div class="p" style="font-size:15px">업무효율 2.63억 · 매출증진 2.28억 · 신담보 전파 절감 1억 · 민원 리스크 감소 1억(공모전 산식 · 통합치료비 효과 미포함)</div></div>
</div>''',
'데이터를 믿을 수 있는 이유와 운영 방식, 기대효과입니다. 모든 데이터는 판매 약관 원문에서 그대로 옮겼고, 질병코드와 금액은 추정하지 않고 없으면 빈칸으로 둡니다. 9월 전수 감사에서 325건을 바로잡았고 약관이 바뀌면 같은 스크립트로 다시 대조합니다. 비용은 0원이고 TF가 직접 운영해 당일 반영이 됩니다. 연간 기대효과는 공모전 때 계산한 가정값으로 약 6.91억원이며, 통합치료비 시뮬레이터 효과는 넣지 않았습니다.',
'PART 2 · 신뢰와 운영', '약관 원문 · 추정 없음 · TF 직접 운영', '', '기대효과 : 공모전 제출 PPT 산식(1인 월 상담 3건 · 확인 시간 10분 → 30초 · 3,667명 등) · 모두 가정값', 'PART 2', z=1.36)

# ── 17. 간지 3 ──────────────────────────────────────────
section('3', '사내망 이관 참고', 'IT 에 전달할 구조 · 갱신 · 바꿀 곳', 'tata_board.webp', '세 번째는 사내망으로 옮길 때 IT에 전달할 내용입니다. 지금 구조와 데이터 갱신 흐름, 사내망에서 바꿔야 할 곳을 정리했습니다.')

# ── 18. 지금 구조 ─────────────────────────────────────────
FILES = [('index.html', '대문(도구 7개 입구)', '0.4MB'), ('tool.html', '특약검색기 + 보상시뮬레이터(안에 내장) · 특약 목록 · 분류표', '7.9MB'),
         ('tool_body.js', '약관 본문(특약 하나가 한 줄 · 화면을 띄운 뒤 불러옴)', '17MB'), ('통합치료비.html', '통합치료비 시뮬레이터 · 금액표 내장', '0.3MB'),
         ('products.html · prompts.html', '상품 라인업 · 프롬프트 라이브러리', '0.3MB씩'), ('명패생성기.html', '명패 제작기(엑셀 읽기 내장)', '1.0MB'),
         ('stats.html', '사용 통계 대시보드', '0.3MB'), ('gloss.js · ui/ · assets/', '용어 907개 · 공통 디자인 · 질병 사전 · 글꼴', '0.6MB')]
tr = ''.join('<tr><td style="font-weight:600;white-space:nowrap">%s</td><td>%s</td><td class="n">%s</td></tr>' % f for f in FILES)
slide('''<div class="row" style="gap:28px;align-items:flex-start">
<div style="flex:1.45"><table><tr><th>파일</th><th>역할</th><th style="text-align:right">크기</th></tr>%s</table></div>
<div style="flex:1"><div class="card"><div class="h3" style="font-size:21px">서버 없는 정적 파일</div>
<div class="p" style="font-size:16px">· 웹서버에 파일만 올리면 동작(데이터베이스 · 프로그램 설치 없음)<br>· 데이터는 HTML 안 JSON + 옆 파일 1개<br>· 화면끼리는 보통 링크(&lt;a href&gt;)로 이동<br>· 바깥 라이브러리 없이 직접 작성(글꼴도 동봉)</div></div>
<div class="card" style="margin-top:16px"><div class="h3" style="font-size:21px">배포판 2종(이미 있음)</div>
<div class="p" style="font-size:16px">· 낱개 6개 : dist/single/ (영문 파일명 · 본문 압축 내장)<br>· 올인원 1개 : 17.8MB 한 파일 · 인터넷 없이 동작</div></div></div></div>''' % tr,
'지금 구조입니다. 서버나 데이터베이스 없이 정적 파일만으로 돌아갑니다. 웹서버에 파일을 올리기만 하면 됩니다. 가장 큰 파일은 특약검색기 tool.html과 약관 본문 tool_body.js이고, 본문은 화면을 먼저 띄운 뒤 불러와 첫 화면이 빠릅니다. 사내망용으로는 영문 파일명의 낱개 배포판 6개와 파일 하나짜리 올인원이 이미 있어, 그대로 시험 탑재할 수 있습니다.',
'PART 3 · 지금 구조', '웹서버에 올리기만 하면 되는 정적 파일 묶음', '', '파일 크기 : 저장소(2026.11.25) · 배포판은 scripts/build_package.py · build_allinone.py 로 만듦', 'PART 3', z=1.12)

# ── 19. 데이터 갱신 흐름 ──────────────────────────────────
STEP = [('약관 PDF', '판매 약관 새 판 · 신상품'), ('추출 · 감수', '특약 본문 · 별표 · 질병코드 · 금액표'), ('데이터 반영', 'tool.html 데이터 · tool_body.js'),
        ('자동 점검', '표 · 금액 · 같은 이름 특약 · 사전 · 하네스'), ('배포판 조립', '낱개 6개 · 올인원 · 버전 표기')]
flow = ''.join('<div style="flex:1;text-align:center"><div class="card" style="padding:24px 16px;min-height:150px"><div style="font-size:15px;font-weight:700;color:#C8102E">%d단계</div><div class="h3" style="margin-top:8px;font-size:21px">%s</div><div class="p" style="font-size:15px">%s</div></div></div>%s'
               % (i + 1, t, d, '<div style="align-self:center;font-size:28px;color:#B0B8C1">→</div>' if i < 4 else '') for i, (t, d) in enumerate(STEP))
slide('''<div class="row" style="gap:12px;align-items:stretch">%s</div>
<div class="card w" style="margin-top:26px"><div class="h3" style="font-size:20px">한 번에 맞추는 명령(저장소 루트)</div>
<div style="margin-top:12px;font-family:Consolas,monospace;font-size:17px;background:#F2F4F6;border-radius:10px;padding:14px 18px">python3 scripts/sync_all.py　　# 약관 → 데이터 · 점검 · 세일즈북 · 배포판 5종을 한 번에</div>
<div class="p" style="font-size:16px">세 산출물(영업지원도구 · 스마트 제안서 · 세일즈북)이 같은 특약 마스터를 씀 · 이관 뒤에도 갱신은 이 흐름을 그대로 쓰는 것을 권장</div></div>''' % flow,
'데이터 갱신 흐름입니다. 약관 PDF가 나오면 특약 본문과 별표, 질병코드, 금액표를 뽑아 감수하고, 데이터 파일에 반영한 뒤 자동 점검을 거쳐 배포판을 조립합니다. 이 전 과정이 명령 하나로 돌아갑니다. 영업지원도구와 스마트 제안서, 세일즈북이 같은 특약 마스터를 쓰기 때문에, 사내망으로 옮긴 뒤에도 갱신은 이 흐름을 그대로 쓰고 결과 파일만 올리는 방식을 권장합니다.',
'PART 3 · 데이터 갱신', '약관이 바뀌면 같은 흐름으로 다시 만듦', '', '절차 : 작업 규칙 문서(CLAUDE.md) · scripts/sync_all.py · scripts/update_terms_2610.py', 'PART 3', z=1.36)

# ── 20. 바깥 연결 ────────────────────────────────────────
EXT = [('사용 기록 전송', '모든 화면', '외부 Supabase 저장소(usage_logs)에 익명 사용 기록 전송', '사내 수집 주소로 바꾸거나 끔', True),
       ('사용 통계 그래프', 'stats.html', 'Chart.js 를 바깥 주소(CDN)에서 불러옴', '파일을 같이 올림'),
       ('이모지 글꼴', '통합치료비', '토스페이스 글꼴을 바깥 주소(CDN)에서 불러옴', '없으면 기기 이모지로 보임(동작 영향 없음)'),
       ('공공 사이트 링크', '특약검색기', '식약처 의약품안전나라 · 심평원 바로가기 링크', '사내망에서 막히면 안내 문구'),
       ('카카오톡 바깥 브라우저', '모든 화면', '카톡 안에서 열면 휴대폰 기본 브라우저로 다시 엶', '사내 앱이면 무관'),
       ('인터넷판 종료 규칙', '모든 화면', 'github.io 주소일 때만 종료 인사 화면으로 넘김', '사내 주소에선 동작 안 함 · 그대로 둬도 됨')]
tr = ''.join('<tr><td style="font-weight:600;%s">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % ('color:#C8102E' if len(x) > 4 else '', x[0], x[1], x[2], x[3]) for x in EXT)
slide('<table><tr><th style="width:17%%">항목</th><th style="width:13%%">화면</th><th>지금 하는 일</th><th style="width:28%%">사내망에서</th></tr>%s</table>' % tr,
'사내망에 올릴 때 확인할 바깥 연결입니다. 가장 중요한 것은 첫 줄입니다. 모든 화면이 익명 사용 기록을 외부 Supabase 저장소로 보내고 있어, 사내 수집 주소로 바꾸거나 꺼야 합니다. 사용 통계 그래프 라이브러리는 파일로 같이 올리면 되고, 통합치료비의 이모지 글꼴은 없어도 기기 이모지로 보여 동작에 영향이 없습니다. 인터넷판 종료 규칙은 github.io 주소에서만 동작하므로 사내 주소에서는 그대로 두어도 됩니다.',
'PART 3 · 바꿀 곳', '사내망에서 확인할 바깥 연결 6가지', '', '저장소 화면 파일 검사(2026.11.25) · 그 밖의 바깥 주소 호출 없음', 'PART 3', z=1.2)

# ── 21. 사용 기록 이어받기 ────────────────────────────────
EV = [('특약검색기', 'open · tab · search · rider · disease · history · prompt_copy'), ('통합치료비', 'open · disease · path · combo · matrix'),
      ('상품 라인업', 'open · view · search · filter'), ('프롬프트', 'open · search · copy'), ('대문 · 명패', 'open · click')]
tr = ''.join('<tr><td style="font-weight:600;width:24%%">%s</td><td style="font-family:Consolas,monospace;font-size:16px">%s</td></tr>' % x for x in EV)
slide('''<div class="row" style="gap:28px;align-items:flex-start"><div style="flex:1.3"><table><tr><th>화면</th><th>남기는 동작(event)</th></tr>%s</table></div>
<div style="flex:1"><div class="card"><div class="h3" style="font-size:21px">기록 한 줄의 모양</div>
<div style="margin-top:12px;font-family:Consolas,monospace;font-size:15px;background:#fff;border:1px solid #E5E8EB;border-radius:10px;padding:14px 16px;line-height:1.7">tool · event · term<br>disease · rider_name · product<br>(+ 기록 시각)</div>
<div class="p" style="font-size:16px">· 로그인 없음 · 사람을 알 수 없는 익명 기록<br>· 검색어 · 질병 · 특약 이름만 남김<br>· 사용 통계 화면(stats.html)이 이 기록을 집계</div></div></div></div>
<div class="card w" style="margin-top:18px;font-size:18px">요청 : 사내 수집 저장소에 <b>같은 이름의 칸</b>을 두면 화면 코드 한 줄(주소)만 바꿔 통계를 이어 쓸 수 있음 · 인터넷판 기록(6.22~11.25)은 최종 수치 확정 후 보관</div>''' % tr,
'사용 기록을 사내로 이어받는 방법입니다. 화면마다 열기, 검색, 특약 조회 같은 동작을 남기고, 한 줄에는 도구 이름, 동작, 검색어, 질병, 특약 이름, 상품만 들어갑니다. 로그인이 없어 사람을 알 수 없는 익명 기록입니다. 사내 수집 저장소에 같은 이름의 칸을 만들어 주시면, 화면 코드에서 주소 한 줄만 바꿔 지금 통계 화면을 그대로 이어 쓸 수 있습니다.',
'PART 3 · 사용 기록', '같은 칸 이름이면 주소 한 줄로 이어 쓸 수 있음', '', '화면 코드의 logEvent 호출 · 사용 통계 화면(stats.html) 기준(2026.11.25)', 'PART 3', z=1.2)

# ── 22. 보안 · 운영 요청 ──────────────────────────────────
slide('''<div class="row" style="gap:24px">
 <div class="card" style="flex:1"><div class="h3">보안 · 개인정보</div><div class="p" style="font-size:17px">· 고객 이름 · 연락처 등 개인정보를 받지 않음<br>· 명패 명단 엑셀은 브라우저 안에서만 읽고 어디에도 보내지 않음<br>· 로그인 · 쿠키 없음 · 저장은 기기 안(즐겨찾기 · 최근 본 특약 · 조합)<br>· 입력 칸은 검색 · 필터뿐 · 결제 · 계정 화면 없음</div></div>
 <div class="card" style="flex:1"><div class="h3">이관 뒤 운영 요청</div><div class="p" style="font-size:17px">· <b style="color:#191F28">TF 가 직접 갱신할 수 있는 경로 유지</b> · 당일 반영이 애용 이유<br>· 약관 개정 때 데이터 파일만 바꿔 올리는 절차<br>· 화면 아래 버전 표기(ver연도.월.횟수)로 판 확인<br>· 오류 제보 창구 = 세일즈혁신TF</div></div>
 <div class="card" style="flex:1"><div class="h3">확인 필요(IT 협의)</div><div class="p" style="font-size:17px">· 올릴 위치(MeAI 홈 메뉴 · 사내 웹서버 경로)<br>· 사용 기록 수집 저장소<br>· 글자 깨짐 없는 사내 브라우저 범위(크롬 · 엣지 · 삼성 인터넷)<br>· 최대 파일 17MB 전송 허용</div></div>
</div>''',
'보안과 운영 요청입니다. 이 도구는 고객 개인정보를 받지 않고, 명패 명단 엑셀도 브라우저 안에서만 읽습니다. 로그인과 쿠키가 없고 입력 칸은 검색과 필터뿐입니다. 이관 뒤에는 TF가 직접 갱신할 수 있는 경로를 꼭 유지해 주셨으면 합니다. 당일 반영이 현장이 애용한 이유였기 때문입니다. 올릴 위치, 사용 기록 저장소, 지원 브라우저, 큰 파일 전송은 IT와 협의가 필요합니다.',
'PART 3 · 보안과 운영', '개인정보 없음 · TF 직접 갱신 유지 요청', '', '저장소 화면 기능 기준(2026.11.25)', 'PART 3', z=1.34)

# ── 23. 로드맵 ───────────────────────────────────────────
RM = [('지금', '인터넷판 종료(11.25)', '종료 인사 화면 · 사내 노트북 · 배포판으로 개발 계속'),
      ('이관', 'MeAI 홈에 이식', '사내 웹서버 탑재 · 사용 기록 사내 수집 · 메뉴 연결'),
      ('정식 서비스', '사내 정식 서비스', 'MeAI 질문 바로 넣기 · 전 채널(GA · TA · PA) 표준 도구'),
      ('이어서', '고도화', '신담보 당일 반영 유지 · 보장 공백 진단 · 사용 통계로 화면 개선')]
cols = ''.join('<div class="card" style="flex:1;padding:26px 24px"><span class="tag%s">%s</span><div class="h3" style="margin-top:16px;font-size:22px">%s</div><div class="p" style="font-size:16px">%s</div></div>' % ('' if i < 2 else ' g', a, b, c) for i, (a, b, c) in enumerate(RM))
slide('<div class="row" style="gap:18px">%s</div><div class="card w" style="margin-top:24px;font-size:18px;line-height:1.6"><b>남은 확인</b> · 인터넷판 최종 사용 수치(10.22~11.25 포함) 확정 · 이관 일정 · 사용 기록 저장소 · 올릴 위치</div>' % cols,
'앞으로의 순서입니다. 인터넷판은 종료했지만 사내 노트북과 배포판으로 개발은 계속합니다. 다음 단계로 MeAI 홈에 이식해 사내 웹서버에 올리고, 사용 기록도 사내에서 모읍니다. 이후 사내 정식 서비스로 전 채널의 표준 도구가 되는 것이 목표입니다. 남은 확인 사항은 인터넷판 최종 사용 수치 확정과 이관 일정, 사용 기록 저장소, 올릴 위치입니다.',
'PART 3 · 앞으로', '인터넷판 종료 → MeAI 홈 이식 → 사내 정식 서비스', '', '', 'PART 3', z=1.42)

# ── 24. 맺음 ─────────────────────────────────────────────
full('''<div class="sl" style="padding:0;background:#fff">
  <div style="position:absolute;inset:0;background:radial-gradient(50%% 60%% at 50%% 0%%,rgba(200,16,46,.07),transparent 70%%)"></div>
  <div style="position:absolute;left:0;right:0;top:120px;text-align:center">
    <div style="font-size:52px;font-weight:700;letter-spacing:-.03em;line-height:1.3">그동안 영업지원도구를<br><span class="em">사랑해주셔서</span> 감사합니다.</div>
    <div style="margin-top:26px;font-size:22px;color:#4E5968;line-height:1.7">영업지원도구는 MeAI홈에 이식하여 사내 정식 서비스로 찾아뵐 예정입니다.<br>영업활동에 많은 도움이 되도록 노력하겠습니다.</div>
    <div style="margin-top:22px;font-size:18px;color:#6B7684">-세일즈혁신TF 이헌수 배상-</div></div>
  <div style="position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:center;align-items:flex-end;gap:26px">%s</div>
</div>''' % ''.join('<img src="%s" style="height:%dpx;width:auto">' % (doll(f), h) for f, h in
                    [('merry_ok.webp', 190), ('eco_point.webp', 190), ('rara_present.webp', 190), ('indi_idea.webp', 190), ('tata_ok.webp', 190), ('ziziri_cheer.webp', 150)]),
'마지막으로 현장에 드린 인사를 그대로 옮깁니다. 그동안 영업지원도구를 사랑해 주셔서 감사합니다. 영업지원도구는 MeAI 홈에 이식해 사내 정식 서비스로 찾아뵐 예정이고, 영업활동에 많은 도움이 되도록 계속 노력하겠습니다. 감사합니다.')

# ── 굽기 ────────────────────────────────────────────────
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(CAP, '..', 'slides'); os.makedirs(tmp, exist_ok=True)
css = CSS % uri(FONT, 'font/woff2')
pngs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') else None)
    pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=2)
    over = []
    for i, (body, _) in enumerate(S, 1):
        doc = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (css, body.replace('@@N@@', '%d / %d' % (i, len(S))))
        f = os.path.join(tmp, 's%02d.html' % i); open(f, 'w', encoding='utf-8').write(doc)
        pg.goto('file://' + f); pg.wait_for_timeout(250)
        bad = pg.evaluate("()=>{const r=[];document.querySelectorAll('.sl *').forEach(e=>{const b=e.getBoundingClientRect();if(b.width&&(b.right>1601||b.bottom>901)&&!e.closest('img'))r.push(e.tagName+':'+(e.textContent||'').slice(0,20))});return r.slice(0,3)}")
        if bad: over.append((i, bad))
        png = os.path.join(tmp, 's%02d.png' % i); pg.screenshot(path=png); pngs.append(png)
    b.close()
print('넘침', over or '0')

prs = Presentation(); prs.slide_width = Emu(12192000); prs.slide_height = Emu(6858000)
for png, (_, notes) in zip(pngs, S):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_picture(png, 0, 0, prs.slide_width, prs.slide_height)
    s.notes_slide.notes_text_frame.text = notes
prs.core_properties.title = 'MeAI 영업지원도구 인터넷판 운영 결산'; prs.core_properties.author = '세일즈혁신TF'
prs.save(os.path.join(OUT, NAME + '.pptx'))
from PIL import Image
ims = [Image.open(x).convert('RGB') for x in pngs]
ims[0].save(os.path.join(OUT, NAME + '.pdf'), save_all=True, append_images=ims[1:], resolution=200)
print('%d장 → %s.pptx · .pdf' % (len(S), os.path.join(OUT, NAME)))
