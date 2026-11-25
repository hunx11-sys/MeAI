# -*- coding: utf-8 -*-
"""영업지원도구 인터넷판 운영 결산 PPT — 성과 · 컨닝페이퍼가 필요했던 이유 · 애용 이유 · MeAI · 스마트 제안서로 이어짐

  python3 scripts/closing_deck/build.py <캡처 폴더> <PretendardVariable.woff2> [출력 폴더=dist]
    → dist/meai_tools_web_closing_2611.pptx · .pdf  (장마다 통이미지 + 발표자 메모 · 1600x900 화면을 2배로 찍음)

캡처 폴더 : index · tool · sim_c16 · itc · products · prompts · nameplate (1440x900 @2x, 사내처럼 파일로 열어 찍음)
숫자 출처 : 사용 숫자 = 사용 통계 서버 익명 기록 전수 분석(2026.6.22~11.25 · 73,820건 · scripts/closing_deck/stats_2611.json · 다시 뽑기 stats_fetch.py → stats_analyze.py).
            특약 이름 · 보장 코드 · 질병명 = tool.html 데이터를 그 자리에서 셈 · 약관 쪽수 = 저장소 루트 약관 PDF 실측.
            자료 규모 · 갱신 횟수 · 파일 크기 = 저장소(2026.11.25). 기대효과 = 내부 추정 산식의 가정값.
그래프 : charts.py(SVG · 바깥 라이브러리 없음)
디자인 : design/DESIGN-MeAI.md + DESIGN-토스.md · 장표 글은 음 · 임 개조식(소유자 덱 규칙)
"""
import base64, collections, glob, html, io, json, os, re, sys
import fitz
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Emu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import charts as C, same_riders
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

# ── 숫자 원천 ────────────────────────────────────────────
ST = json.load(open(os.path.join(HERE, 'stats_2611.json'), encoding='utf-8'))
DAYS = ST['일별']
_m = re.search(same_riders.PAT, io.open(os.path.join(ROOT, 'tool.html'), encoding='utf-8').read(), re.S)
TD = json.loads(_m.group(2)); RID = TD['riders']; CN = TD['codenames']
PN = sorted({r['n'] for r in RID if '[' not in r['n']})            # 특약 이름(세부보장 제외)
ALLN = sorted({r['n'] for r in RID})
P20 = [n for n in PN if len(n) >= 20]
AVG = sum(map(len, PN)) / len(PN)
LONG = max(ALLN, key=len)
def rider(nm): return next(r for r in RID if r['n'] == nm)
PAGES = sorted(((fitz.open(f).page_count, os.path.basename(f)) for f in glob.glob(os.path.join(ROOT, '*.pdf'))), reverse=True)
PTOT = sum(p for p, _ in PAGES)
SRC_U = '사용 숫자 : 사용 통계 서버 익명 기록 전수 분석(2026.6.22~11.25 · 73,820건 · 사람 수가 아니라 조회 · 검색 · 클릭 건수 · 종료 도구 기록 제외 · 시각은 한국시간)'
GL = '쉬운 설명 : 영업지원도구 보험용어 사전(gloss.js) 문구 그대로'

# ── 1. 표지 ────────────────────────────────────────────────
full('''<div class="sl" style="padding:0;background:#fff">
  <div style="position:absolute;inset:0;background:radial-gradient(46%% 60%% at 12%% 10%%,rgba(200,16,46,.09),transparent 70%%),radial-gradient(40%% 50%% at 92%% 20%%,rgba(109,91,214,.08),transparent 70%%),radial-gradient(50%% 50%% at 70%% 100%%,rgba(242,183,5,.08),transparent 70%%)"></div>
  <div style="position:absolute;left:100px;top:150px;width:820px">
    <span class="tag">2026.6.22 ~ 2026.11.25 · 157일</span>
    <div style="margin-top:28px;font-size:68px;font-weight:700;letter-spacing:-.035em;line-height:1.2">MeAI 영업지원도구<br><span class="em">인터넷판 운영 결산</span></div>
    <div style="margin-top:26px;font-size:25px;color:#4E5968;line-height:1.5">성과 · 영업 컨닝페이퍼가 필요했던 이유<br>MeAI · 스마트 제안서로 이어진 자산</div>
    <div style="margin-top:34px;width:560px">%s<div style="display:flex;justify-content:space-between;font-size:14px;color:#8B95A1;margin-top:6px"><span>6.22 하루 204건</span><span>11.20 하루 9,362건</span></div></div>
    <div style="margin-top:30px;font-size:19px;color:#6B7684">2026. 11　세일즈혁신TF</div>
  </div>
  <img src="%s" style="position:absolute;right:56px;bottom:0;width:640px;height:auto">
</div>''' % (C.spark(DAYS, 560, 90), doll('group_hello.webp')),
'MeAI 영업지원도구 인터넷판 운영 결산 보고를 시작하겠습니다. 6월 22일부터 11월 25일까지 157일 동안 운영한 영업지원도구의 성과와, 현장에 왜 이런 컨닝페이퍼가 필요했는지, 그리고 이 도구에서 만든 자산이 MeAI 와 회사 정식 전산용 스마트 제안서로 어떻게 이어지고 있는지 정리했습니다. 표지의 작은 그래프는 하루 사용 건수의 흐름입니다.')

# ── 2. 이 자료는 ───────────────────────────────────────────
slide('''<div class="row" style="gap:20px">
  <div class="card" style="flex:1"><span class="tag">용도 1</span><div class="h3" style="margin-top:16px">내부 성과 보고</div>
    <div class="p">157일 사용 성과(그래프)<br>컨닝페이퍼가 필요했던 현장 문제 6가지<br>현장이 애용한 이유 · 기대효과(가정값)</div></div>
  <div class="card" style="flex:1"><span class="tag">용도 2</span><div class="h3" style="margin-top:16px">이어지는 자산</div>
    <div class="p">MeAI 에 반영 · 정교화한 구성 요소<br>정식 전산용 스마트 제안서와 같은 원천<br>(특약 마스터 · 질병코드 · 계산 규칙)</div></div>
</div>
<div class="card w" style="margin-top:22px;display:flex;gap:20px;align-items:center">
  <span class="dot">!</span>
  <div><div class="h3" style="font-size:21px">2026.11.25 인터넷 링크 폐쇄</div>
  <div class="p" style="margin-top:6px">개발은 계속하며 MeAI 홈에 이식해 사내 정식 서비스로 전환 예정</div></div>
</div>''',
'이 자료는 두 가지 용도로 만들었습니다. 첫째는 내부 성과 보고입니다. 157일 동안의 사용 성과와, 왜 현장에 영업용 컨닝페이퍼가 필요했는지, 현장이 왜 이 도구를 애용했는지를 담았습니다. 둘째는 이 도구에서 만든 자산이 MeAI 와 회사 정식 전산용 스마트 제안서로 이어지고 있다는 점입니다. 인터넷 링크는 11월 25일 폐쇄했고, 개발은 계속해서 MeAI 홈에 이식할 예정입니다.',
'00 · 이 자료는', '성과 보고와 이어지는 자산을 한 권으로', '', '', '', z=1.45)

# ── 3. 한 장 요약 ─────────────────────────────────────────
def tile(n, u, lab, red=False, w='1'):
    return '<div class="card" style="flex:%s;min-height:150px"><div class="num%s">%s<small>%s</small></div><div class="lab">%s</div></div>' % (w, ' r' if red else '', n, u, lab)
slide('''<div class="row">%s%s%s%s</div>
<div class="card w" style="margin-top:18px;padding:22px 28px"><div style="display:flex;justify-content:space-between;align-items:baseline"><div class="h3" style="font-size:20px">하루 사용 건수 157일</div>
<div style="font-size:15px;color:#6B7684">10.21까지 하루 평균 <b style="color:#191F28">271건</b> → 10.22부터 <b class="em">1,166건(4.3배)</b></div></div>
<div style="margin-top:8px">%s</div></div>''' % (
    tile('73,820', '건', '누적 사용(157일)', True), tile('9,362', '건', '하루 최고(11.20 금)', True),
    tile('37,051', '건', '11월 한 달 · 전체의 절반'), tile('0', '원', '개발 · 서버 · 라이선스'),
    C.spark(DAYS, 1330, 260)),
'한 장으로 요약하면 이렇습니다. 인터넷판 157일 동안 누적 사용이 73,820건이고, 종료 직전인 11월 20일 금요일에는 하루 9,362건이 쓰였습니다. 11월 한 달에만 37,051건으로 전체 사용의 절반이 몰렸고, 비용은 0원입니다. 아래 그래프가 157일 하루 사용 건수인데, 10월 21일까지 하루 평균 271건이던 것이 10월 22일부터는 1,166건으로 4.3배가 됐습니다. 사용 건수는 로그인 없는 익명 기록이라 사람 수가 아니라 사용 건수입니다.',
'00 · 한 장 요약', '157일 · 누적 7만 3천 건 · 하루 최고 9천 건', '', SRC_U, '', z=1.05)

# ── 간지 ──────────────────────────────────────────────────
def section(no, title, sub, mascot, notes):
    full('''<div class="sl" style="padding:0;background:#F7F8FA">
  <div style="position:absolute;left:110px;top:300px">
    <div style="font-size:22px;font-weight:700;color:#C8102E">PART %s</div>
    <div style="margin-top:14px;font-size:64px;font-weight:700;letter-spacing:-.035em">%s</div>
    <div style="margin-top:18px;font-size:24px;color:#4E5968">%s</div></div>
  <img src="%s" style="position:absolute;right:140px;top:220px;height:440px;width:auto">
  <div class="foot"><span>MeAI 영업지원도구 인터넷판 운영 결산 · 세일즈혁신TF</span><span>@@N@@</span></div></div>''' % (no, title, sub, doll(mascot)), notes)

section('1', '157일의 성과', '얼마나 쓰였고, 무엇을 찾았나', 'success_thumbs.webp', '첫 번째로 157일 동안의 성과를 그래프로 보겠습니다. 얼마나 쓰였고, 언제 쓰였고, 현장이 무엇을 찾았는지입니다.')

# ── 운영 흐름(일별 그래프) ─────────────────────────────────
MK = [('2026-06-22', '6.22 공개', 0), ('2026-07-15', '7월 첫 성수기 · 한 달 1만 건', 1), ('2026-09-15', '9월 6개 상품 전수 감사 325건', 0),
      ('2026-10-22', '10.22 일곱 화면 통일', 1), ('2026-11-01', '11.1 2610 약관', 2), ('2026-11-12', '11.12 질병 검색 사전', 3),
      ('2026-11-20', '11.20 하루 9,362건', 4), ('2026-11-25', '11.25 종료 · 누적 73,820건', 0)]
slide('<div class="card w" style="padding:18px 20px 10px">%s</div>' % C.daily(DAYS, 1400, 560, MK),
'운영 흐름을 하루 단위 그래프로 보겠습니다. 회색 막대가 하루 사용 건수, 빨간 선이 누적입니다. 6월 22일 공개 뒤 7월에 한 달 1만 건을 넘기며 퍼졌고, 9월에는 현장 제보로 6개 상품 전수 감사를 해 325건을 바로잡았습니다. 10월 22일 일곱 화면을 한 사이트로 통일하고 11월 1일 2610 약관을 반영하면서 누적 선이 가파르게 꺾입니다. 11월 12일과 13일에는 하루 4천 건대, 11월 20일 금요일에는 하루 9,362건을 기록했고, 11월 25일 종료 시점 누적은 73,820건입니다.',
'PART 1 · 운영 흐름', '10월 말부터 누적 선이 가파르게 꺾임', '', SRC_U + ' · 날짜 : 저장소 기록', 'PART 1')

# ── 월별 + 쓰임새 ─────────────────────────────────────────
MON = [('6월', 2110, 9), ('7월', 10278, 31), ('8월', 5641, 31), ('9월', 8216, 30), ('10월', 10524, 31), ('11월', 37051, 25)]
mx = max(v for _, v, _ in MON)
bars = ''.join('<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:400px">'
               '<div style="font-size:19px;font-weight:700;font-variant-numeric:tabular-nums;color:%s">%s</div>'
               '<div style="margin-top:8px;width:70%%;height:%dpx;border-radius:12px 12px 4px 4px;background:%s"></div>'
               '<div style="margin-top:10px;font-size:18px;font-weight:600">%s</div><div style="font-size:14px;color:#6B7684">하루 %s건</div></div>'
               % ('#C8102E' if v == mx else '#4E5968', format(v, ','), max(8, int(v / mx * 300)), '#C8102E' if v == mx else '#D1D6DB', m, format(round(v / d), ','))
               for m, v, d in MON)
USE = [('질병 · 검색으로 찾기', 19483, '#C8102E'), ('특약 상세 · 약관 본문', 7499, '#6D5BD6'), ('MeAI 프롬프트 복사', 1137, '#F2B705')]
slide('''<div class="row" style="gap:22px;align-items:stretch">
<div class="card w" style="flex:1.4"><div class="h3" style="font-size:21px">월별 사용 <span class="tag g" style="vertical-align:middle">6월은 22일부터 · 11월은 25일까지</span></div>
<div style="display:flex;gap:8px;margin-top:10px">%s</div></div>
<div class="card w" style="flex:1"><div class="h3" style="font-size:21px">무엇을 했나(주요 동작)</div>
<div style="display:flex;justify-content:center;margin-top:18px">%s</div><div style="margin-top:14px">%s</div></div></div>''' % (
    bars, C.donut(USE, 250, '28,119', '찾기 → 근거 → MeAI'), C.legend([(n, format(v, ','), c) for n, v, c in USE], '건')),
'월별로 보면 7월에 한 달 1만 건을 넘긴 뒤, 11월에는 25일 만에 37,051건으로 하루 평균 1,482건이 쓰였습니다. 오른쪽은 주요 동작입니다. 질병이나 검색어로 찾아본 것이 19,483건, 약관 본문까지 열어 본 특약 상세조회가 7,499건, MeAI 프롬프트 복사가 1,137건입니다. 찾고, 근거를 확인하고, MeAI 로 이어 가는 흐름으로 쓰였습니다.',
'PART 1 · 사용 성과', '11월에 한 달 37,051건 · 전체 사용의 절반', '', SRC_U, 'PART 1', z=1.0)

# ── 언제 · 어떻게 ────────────────────────────────────────
HR = [('%d' % h, v) for h, v in ST['시간대']]
WD = list(zip(['월', '화', '수', '목', '금', '토', '일'], ST['요일']))
SHARE = [('특약검색기', 43.2, '#C73D1C'), ('보상시뮬레이터', 25.7, '#23874C'), ('상품 라인업', 13.5, '#F2B705'), ('통합치료비', 12.5, '#6D5BD6'), ('프롬프트', 3.9, '#A23A91'), ('명패', 1.3, '#2563C9')]
slide('''<div class="row" style="gap:20px;align-items:stretch">
<div class="card w" style="flex:1.35"><div class="h3" style="font-size:20px">시간대별 <span class="em">오전 9시 한 시간에 31%%</span></div>%s
<div class="h3" style="font-size:20px;margin-top:12px">요일별 <span class="em">평일 96%%</span> · 금요일 최다</div>%s</div>
<div class="card w" style="flex:1"><div class="h3" style="font-size:20px">도구별 비중 <span class="tag g" style="vertical-align:middle">대문 제외 50,215건</span></div>
<div style="display:flex;justify-content:center;margin-top:16px">%s</div><div style="margin-top:10px">%s</div></div></div>''' % (
    C.vbars(HR, 780, 210, hi=(9,), every=3), C.vbars(WD, 780, 190, hi=(4,)),
    C.donut(SHARE, 240, '6종', '도구'), C.legend([(n, v, c) for n, v, c in SHARE], '%', 16)),
'언제, 어떻게 쓰였는지입니다. 왼쪽 위 시간대 그래프를 보면 오전 9시 한 시간에 전체의 31%가 몰립니다. 출근 직후 그날 상담을 준비하는 도구로 쓰였다는 뜻입니다. 요일로는 96%가 평일이고 금요일이 가장 많습니다. 오른쪽 도구별 비중은 대문을 빼고 특약검색기 43%, 보상시뮬레이터 26%, 상품 라인업과 통합치료비가 각각 13% 안팎입니다.',
'PART 1 · 언제 · 어떻게', '평일 아침 9시, 상담 준비 도구로 쓰였음', '', SRC_U, 'PART 1', z=1.16)

# ── 무엇을 찾았나 ────────────────────────────────────────
DZ = [('위암', 1354), ('유방암', 699), ('갑상선암', 470), ('협심증', 416), ('폐암', 416), ('대장암', 330)]
DZC = ['C16', 'C50', 'C73', 'I20', 'C34', 'C18~C20']
RD = [('특정순환계질환 통합치료비', 779), ('상해 통합치료비(실속형)', 502), ('암 통합치료비(기본형)', 346), ('특정순환계질환(주요손상및질환) 통합치료비', 269), ('암 통합치료 생활비(연간 통합치료 2회이상)', 200), ('암 통합치료비Ⅱ(비급여(전액본인부담 포함))', 156)]
slide('''<div class="row" style="gap:22px;align-items:stretch">
  <div class="card w" style="flex:1"><span class="tag">많이 찾은 질병(질병 조회 건수)</span><div style="margin-top:8px">%s</div></div>
  <div class="card w" style="flex:1.25"><span class="tag">상세조회 상위 특약</span> <span style="font-size:17px;font-weight:700;margin-left:8px">상위 8개 중 <span class="em">7개</span>가 통합치료비 계열</span><div style="margin-top:8px">%s</div></div></div>
<div class="card" style="margin-top:18px;font-size:18px;line-height:1.6"><b>직접 친 검색어 1위 「대장용종」</b> · 공식 병명(결장의 용종)과 달라 못 찾던 말 → 일상 병명 사전으로 해결 · 그다음 뇌경색 · 위암 · 운전자 · 간병인 · 당뇨 · 치매</div>''' % (
    C.hbars(DZ, lw=110, fs=18, h=24, hi=1, sub=DZC), C.hbars(RD, color='#6D5BD6', lw=330, fs=16, h=22, hi=6)),
'현장이 무엇을 찾았는지입니다. 질병 조회는 위암이 1,354건으로 가장 많고, 유방암, 갑상선암, 협심증, 폐암, 대장암 순입니다. 오른쪽 상세조회 상위 특약은 8개 중 7개가 통합치료비 계열이라 통합치료비 시뮬레이터를 따로 만든 근거가 됐습니다. 직접 친 검색어 1위는 대장용종이었는데, 공식 병명이 결장의 용종이라 찾지 못하던 말이어서 일상 병명 사전으로 해결했습니다.',
'PART 1 · 무엇을 찾았나', '위암 · 통합치료비 · 대장용종', '', SRC_U, 'PART 1', z=1.18)

# ── 도구 6종 ────────────────────────────────────────────
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

# ── 자료 규모 ───────────────────────────────────────────
DATA = [('1,149', '종', '특약(6개 상품) · 세부보장 포함 1,842건', 'merry_ok.webp'), ('293', '개', '약관 분류표(별표) · 특약마다 질병코드 연결', 'tata_board.webp'),
        ('1,302', '개', '공식 질병명(코드명)', 'indi_idea.webp'), ('185', '개', '일상 병명 사전 · 동의어 100묶음 · 별칭 30', 'eco_point.webp'),
        ('907', '개', '보험용어 쉬운 설명', 'rara_present.webp'), ('50', '종', '장기상품 라인업 · 간편보험 5유형 판정', 'success_thumbs.webp'),
        ('272', '개', 'MeAI 프롬프트', 'rara_mic.webp'), ('13', '종', '통합치료비 특약 금액표(암 9 · 뇌심 4)', 'eco_doctor.webp')]
grid = ''.join('<div class="card" style="width:calc(25%% - 14px);padding:22px 24px;min-height:170px;position:relative;overflow:hidden"><div class="num" style="font-size:46px">%s<small>%s</small></div><div class="lab" style="font-size:16px;padding-right:70px">%s</div>'
               '<img src="%s" style="position:absolute;right:-6px;bottom:-8px;height:86px;width:auto;opacity:.95"></div>' % (a, b, c, doll(m)) for a, b, c, m in DATA)
slide('<div style="display:flex;flex-wrap:wrap;gap:18px">%s</div>' % grid,
'도구 안에 담긴 자료 규모입니다. 6개 상품의 특약 1,149종을 세부보장까지 1,842건, 약관 분류표 293개와 공식 질병명 1,302개를 담았습니다. 일상 병명 사전 185개와 보험용어 쉬운 설명 907개, 장기상품 50종, MeAI 프롬프트 272개, 통합치료비 13종의 금액표가 들어 있습니다. 이 자료가 뒤에서 보실 MeAI 와 스마트 제안서로 이어지는 자산입니다.',
'PART 1 · 담긴 자료', '약관 원문을 그대로 옮긴 영업 자료 자산', '', '저장소 기록(2026.11.25) · tool.html 데이터 · gloss.js · ui/meai-lex.js · products · prompts · 통합치료비 화면', 'PART 1', z=1.22)

# ══ PART 2 · 컨닝페이퍼가 필요했던 이유 ═══════════════════
section('2', '왜 컨닝페이퍼가 필요했나', '바쁜 상담 중에 약관을 펼칠 수 없는 현장', 'indi_idea.webp',
'두 번째로, 현장에 왜 이런 영업 컨닝페이퍼가 필요했는지 실제 사례로 보겠습니다. 약관은 방대해지고, 특약 이름은 길고 비슷해졌고, 읽는 데 배경지식까지 필요해졌습니다. 바쁜 영업활동과 상담 도중에 빠르고 쉽게 볼 무언가가 필요했습니다. 한 장에 사례 하나씩 보겠습니다.')

# 사례 1 · 방대한 약관
PG = [(re.sub(r'^무배당\s*(메리츠\s*)?|약관\.pdf$|\(세만기형\)', '', f).strip(), p) for p, f in PAGES if '알파Plus' not in f][:8]
slide('''<div class="row" style="gap:22px;align-items:stretch">
<div class="card" style="flex:.85;display:flex;flex-direction:column;justify-content:center;text-align:center">
  <div style="font-size:18px;color:#4E5968">케어프리보험 M-Basket 2610 약관 한 권</div>
  <div class="num r" style="font-size:96px;margin-top:6px">%s<small style="font-size:32px">쪽</small></div>
  <div style="margin:14px auto 0;display:flex;align-items:flex-end;gap:4px;height:120px">%s</div>
  <div style="margin-top:14px;font-size:17px;color:#4E5968">판매 약관 %d종을 모두 합치면 <b class="em">%s쪽</b></div></div>
<div class="card w" style="flex:1.25"><div class="h3" style="font-size:20px">약관 쪽수 상위 8개 <span class="tag g" style="vertical-align:middle">2610 판 PDF · GA 판매명 알파Plus 는 같은 약관이라 뺌</span></div>%s</div></div>
<div class="card w" style="margin-top:18px;display:flex;gap:18px;align-items:center"><span class="tag" style="flex:none">사례</span>
<div style="font-size:18px;line-height:1.6">고객 「갑상선암도 진단비 나와요?」 → 특약 본문(특별약관) 찾고 → 뒤쪽 별표에서 질병코드 표까지 오가야 답이 나옴 · 두 단 조판이라 표가 다음 쪽으로 넘어감 · <b>상담 자리에서 펼쳐 볼 수 있는 분량이 아님</b></div></div>''' % (
    format(PAGES[0][0], ','), ''.join('<i style="display:block;width:26px;height:%dpx;border-radius:3px;background:%s"></i>' % (60 + 9 * k, '#C8102E' if k == 6 else '#E5E8EB') for k in range(7)),
    len(PAGES), format(PTOT, ','), C.hbars(PG, lw=330, fs=15, h=20, hi=2)),
'첫 번째 사례는 방대한 약관입니다. 케어프리보험 M-Basket 2610 약관 PDF 한 권이 1,830쪽으로 2천 쪽에 가깝고, 지금 판매 약관 53종을 모두 합치면 3만 7천 쪽이 넘습니다. 고객이 갑상선암도 진단비가 나오느냐고 물으면, 특별약관 본문을 찾고 뒤쪽 별표의 질병코드 표까지 오가야 답이 나옵니다. 약관이 두 단으로 짜여 있어 표가 다음 쪽으로 넘어가는 일도 많습니다. 상담 자리에서 펼쳐 볼 수 있는 분량이 아닙니다.',
'PART 2 · 사례 1 방대한 약관', '약관 한 권이 2천 쪽에 가까움', '', '쪽수 : 저장소 루트 약관 PDF(2610 판 등 %d종) 실측 · 2026.11.25' % len(PAGES), 'PART 2', z=1.1)

# 사례 2 · 긴 특약 이름
LB = collections.Counter(min(len(n) // 5 * 5, 50) for n in PN)
LBI = [('%d~' % k if k < 50 else '50~', LB.get(k, 0)) for k in range(0, 55, 5)]
slide('''<div class="row" style="gap:22px;align-items:stretch">
<div class="card w" style="flex:1.2"><div class="h3" style="font-size:20px">특약 이름 글자 수 분포 <span class="tag g" style="vertical-align:middle">6개 상품 · 특약 %d개(세부보장 제외)</span></div>
%s<div style="font-size:15px;color:#6B7684;text-align:center">글자 수(띄어쓰기 포함) · 빨간 막대 = 20자 이상</div></div>
<div style="flex:.8;display:flex;flex-direction:column;gap:16px">%s%s</div></div>
<div class="card" style="margin-top:18px"><span class="tag">사례 · 실제 이름(세부보장 포함 가장 긴 것 %d자)</span>
<div style="margin-top:12px;font-size:20px;line-height:1.55;font-weight:600;letter-spacing:-.01em">%s</div></div>''' % (
    len(PN), C.vbars(LBI, 800, 270, hi=tuple(range(4, 11)), top_label=False, fs=14),
    tile('%d' % round(len(P20) / len(PN) * 100), '%', '20자가 넘는 특약 · %d개 중 %d개' % (len(PN), len(P20)), True),
    tile('%.1f' % AVG, '자', '특약 이름 평균 글자 수'), len(LONG), e(LONG)),
'두 번째 사례는 긴 특약 이름입니다. 6개 상품 특약 %d개의 이름 글자 수를 세어 보면 평균 %.1f자이고, 절반에 가까운 %d개가 20자를 넘습니다. 아래는 세부보장까지 포함해 가장 긴 실제 이름으로 %d자입니다. 갱신형, 비급여, 전액본인부담, 연간1회한 같은 조건이 괄호로 겹겹이 붙습니다. 고객 앞에서 이 이름을 읽고 무엇을 보장하는지 바로 설명하기는 어렵습니다.' % (len(PN), AVG, len(P20), len(LONG)),
'PART 2 · 사례 2 긴 특약 이름', '특약 둘 중 하나는 이름이 20자를 넘음', '', '특약 이름 : 특약검색기 데이터(tool.html · 6개 상품 · 2026.11.25) 전수 집계', 'PART 2', z=1.04)

# 사례 3 · 배경지식
PARTS3 = [('암', '#C8102E', None), (' 통합치료비', '#6D5BD6', '통합치료비'), ('Ⅱ', '#8B95A1', None), ('(', '#8B95A1', None), ('비급여', '#23874C', '비급여'),
          ('(', '#8B95A1', None), ('전액본인부담', '#F2B705', '전액본인부담'), (' 포함), ', '#8B95A1', None), ('암중점치료기관', '#2563C9', '암중점치료기관'),
          ('(', '#8B95A1', None), ('상급종합병원', '#A23A91', '상급종합병원'), (' 포함))', '#8B95A1', None)]
GD = {'통합치료비': '실제로 치료를 받을 때마다 주는 보험금이에요.', '비급여': '건강보험이 적용되지 않아 환자가 전부 내야 하는 치료예요.',
      '전액본인부담': '건강보험 항목이긴 하지만 환자가 100% 내는 경우예요.', '암중점치료기관': '암 진료를 집중적으로 하는 병원이에요.',
      '상급종합병원': '중증 질환의 마지막 치료를 맡는 큰 병원이에요.'}
GN = {'통합치료비': '진단비가 한 번이라면, 치료비는 치료할 때마다 반복해서 나올 수 있어요.', '비급여': '병원마다 가격이 달라요. 최신 치료 상당수가 여기에 속해요.',
      '전액본인부담': '급여도 비급여도 아닌 중간 지대라 담보에서 따로 다뤄요.', '암중점치료기관': '일부 담보는 이 병원에서 치료받을 때 조건이 붙어요.',
      '상급종합병원': '전국 47개소가 지정돼 있고, 여러 담보의 보장 조건이 돼요.'}
nm = ''.join('<span style="color:%s;%s">%s</span>' % (c, 'border-bottom:4px solid %s;padding-bottom:2px' % c if k else '', e(t)) for t, c, k in PARTS3)
gc = ''.join('<div class="card" style="flex:1;padding:20px 20px;border-top:5px solid %s"><div style="font-size:19px;font-weight:700;color:%s">%s</div><div style="margin-top:8px;font-size:16px;line-height:1.5">%s</div><div style="margin-top:6px;font-size:14px;color:#6B7684;line-height:1.5">%s</div></div>'
             % (c, c, k, GD[k], GN[k]) for _, c, k in PARTS3 if k)
slide('''<div class="card w" style="text-align:center;padding:30px 20px"><div style="font-size:15px;color:#6B7684">사례 · 상세조회 6위 특약 이름 하나</div>
<div style="margin-top:14px;font-size:34px;font-weight:700;letter-spacing:-.02em;line-height:1.5">%s</div>
<div style="margin-top:12px;font-size:17px;color:#4E5968">이 이름 하나를 읽으려면 <b class="em">용어 5개</b>를 알아야 함 · 어느 병원에서, 어떤 진료비를, 몇 번 받는지가 이름에 다 들어 있음</div></div>
<div class="row" style="gap:14px;margin-top:20px">%s</div>''' % (nm, gc),
'세 번째 사례는 배경지식입니다. 상세조회 6위였던 암 통합치료비Ⅱ 비급여 전액본인부담 포함 암중점치료기관 상급종합병원 포함이라는 이름 하나를 읽으려면 통합치료비, 비급여, 전액본인부담, 암중점치료기관, 상급종합병원 다섯 가지 용어를 알아야 합니다. 아래 설명은 영업지원도구 용어 사전에 넣어 둔 쉬운 설명을 그대로 옮긴 것입니다. 급여와 비급여의 차이, 어떤 병원이 암중점치료기관인지, 통합치료비가 진단비와 어떻게 다른지를 모르면 이 특약을 설명할 수 없습니다. 그래서 도구에서는 용어에 밑줄을 긋고 누르면 쉬운 설명이 뜨게 했습니다.',
'PART 2 · 사례 3 배경지식', '이름 하나에 용어 5개 · 비급여 · 전액본인부담 · 암중점치료기관', '', GL + ' · 특약 이름 : 특약검색기 데이터 · 상세조회 순위 : 사용 통계', 'PART 2', z=1.3)

# 사례 4 · 비슷한 이름, 다른 범위
BR = [('뇌출혈진단비', '#C8102E'), ('뇌졸중진단비', '#6D5BD6'), ('뇌혈관질환진단비', '#2563C9')]
ICD = ['I%d' % k for k in range(60, 70)]
hd = ''.join('<th style="text-align:center;padding:10px 4px;font-size:15px">%s<div style="font-weight:400;font-size:12px;color:#6B7684;line-height:1.3;margin-top:4px">%s</div></th>' % (c, e(CN.get(c, ''))) for c in ICD)
rw = ''.join('<tr><td style="font-weight:700;white-space:nowrap;color:%s;font-size:18px">%s<div style="font-size:13px;color:#6B7684;font-weight:400">%d개 코드</div></td>%s</tr>' % (
    col, n, len(rider(n)['k']), ''.join('<td style="text-align:center;padding:8px 4px"><span style="display:inline-block;width:38px;height:38px;border-radius:10px;background:%s"></span></td>' % (col if c in rider(n)['k'] else '#F2F4F6') for c in ICD)) for n, col in BR)
slide('''<table style="table-layout:fixed"><tr><th style="width:190px">특약</th>%s</tr>%s</table>
<div class="row" style="margin-top:18px;gap:18px"><div class="card w" style="flex:1.3;display:flex;gap:16px;align-items:center"><span class="tag" style="flex:none">사례</span><div style="font-size:18px;line-height:1.55">「뇌경색(I63)인데 뇌출혈진단비 나오죠?」 → <b class="em">안 나옴</b> · 뇌졸중진단비 · 뇌혈관질환진단비에서 나옴 · 이름이 비슷해 「뇌 쪽은 다 된다」 오안내 위험</div></div>
<div class="card" style="flex:.7;text-align:center"><div class="num" style="font-size:44px">%d<small>개</small></div><div class="lab" style="font-size:15px;margin-top:4px">「뇌혈관질환수술비」 한 이름의 변형(갱신형 · 25%%체증형 · 감액기간미적용 등)</div></div></div>''' % (
    hd, rw, sum(1 for n in PN if re.sub(r'^갱신형\s*|\s*\((감액기간미적용|25%체증형)\)', '', n).replace(' ', '') == '뇌혈관질환수술비')),
'네 번째 사례는 이름은 비슷한데 범위가 다른 특약입니다. 뇌출혈진단비, 뇌졸중진단비, 뇌혈관질환진단비는 이름이 비슷하지만 약관 분류표의 질병코드 범위가 다릅니다. 표에서 색칠된 칸이 보장 코드입니다. 뇌경색 I63 은 뇌출혈진단비에서는 나오지 않고, 뇌졸중진단비와 뇌혈관질환진단비에서 나옵니다. 이름만 보고 뇌 쪽은 다 된다고 안내하면 오안내가 됩니다. 같은 뇌혈관질환수술비 한 이름에도 갱신형, 체증형, 감액기간 미적용 같은 변형이 여럿입니다.',
'PART 2 · 사례 4 비슷한 이름', '뇌출혈 · 뇌졸중 · 뇌혈관 — 이름은 비슷, 보장 코드는 다름', '', '보장 코드 : 약관 분류표(별표) → 특약검색기 데이터 그대로(추정 없음) · 질병명 : 공식 코드명 · 변형 수 : 특약 이름 전수 집계', 'PART 2', z=1.12)

# 사례 5 · 통합치료비 16종
ITN = [n for n in PN if '통합치료비' in n]
GRP = [('암', '#C8102E', [n for n in ITN if n.startswith('암')]), ('뇌 · 심장(특정순환계)', '#6D5BD6', [n for n in ITN if '순환계' in n]),
       ('상해 · 질병', '#23874C', [n for n in ITN if n.startswith('상해') or n.startswith('질병')])]
gcols = ''.join('<div class="card" style="flex:%s;padding:20px 22px"><div style="display:flex;align-items:center;gap:10px"><i style="width:14px;height:14px;border-radius:4px;background:%s"></i><b style="font-size:19px">%s</b><span class="tag g">%d개</span></div>%s</div>'
                % ('1.45' if i == 0 else '1', c, g, len(L), ''.join('<div style="margin-top:9px;font-size:15px;line-height:1.4;padding:8px 12px;border-radius:10px;background:#fff;border:1px solid #EEF0F2">%s</div>' % e(n) for n in L)) for i, (g, c, L) in enumerate(GRP))
slide('<div class="row" style="gap:16px;align-items:flex-start">%s</div>' % gcols,
'다섯 번째 사례는 통합치료비입니다. 같은 통합치료비라는 말이 들어간 특약만 %d개입니다. 암 쪽만 해도 기본형, 실속형, 주요치료, Ⅱ, 그리고 비급여와 암중점치료기관 조건이 조합되어 이름이 갈라집니다. 앞에서 본 것처럼 상세조회 상위 8개 중 7개가 통합치료비 계열이었습니다. 현장이 가장 많이 헷갈려 하고 가장 많이 찾아본 특약이라, 치료 과정만 고르면 금액이 나오는 통합치료비 시뮬레이터를 따로 만들었습니다.' % len(ITN),
'PART 2 · 사례 5 통합치료비', '「통합치료비」 이름만 %d가지 · 상세조회 상위 8개 중 7개' % len(ITN), '', '특약 이름 : 특약검색기 데이터(6개 상품 · 세부보장 제외) · 상세조회 순위 : 사용 통계', 'PART 2', z=1.08)

# 사례 6 · 일상 병명 ≠ 공식 병명
TERMS = [(t, v) for t, v in ST['검색어상위']]
slide('''<div class="row" style="gap:22px;align-items:stretch">
<div class="card" style="flex:1;display:flex;flex-direction:column;justify-content:center">
  <span class="tag" style="align-self:flex-start">사례 · 검색어 1위</span>
  <div style="margin-top:22px;display:flex;align-items:center;gap:20px">
    <div style="padding:18px 26px;border-radius:16px;background:#fff;border:2px solid #191F28;font-size:34px;font-weight:700">대장용종</div>
    <div style="font-size:30px;color:#B0B8C1">→</div>
    <div><div style="padding:10px 18px;border-radius:12px;background:#FDECEE;font-size:22px;font-weight:700;color:#A50D26">결장의 용종 <span style="font-weight:500;font-size:16px">K63.5</span></div>
    <div style="margin-top:10px;padding:10px 18px;border-radius:12px;background:#FDECEE;font-size:22px;font-weight:700;color:#A50D26">직장용종 <span style="font-weight:500;font-size:16px">K62.1</span></div></div></div>
  <div style="margin-top:24px;font-size:18px;line-height:1.6;color:#4E5968">현장 · 고객이 쓰는 말은 「대장용종」 · 약관 · 질병분류의 공식 병명은 「결장의 용종」 · 「직장용종」 → <b style="color:#191F28">글자가 달라 검색이 안 됨</b><br>위 · 십이지장 용종, 초성(ㅇㅁ · ㅇㅁㅈㄹ)으로 치는 경우도 많음</div></div>
<div class="card w" style="flex:1"><div class="h3" style="font-size:20px">직접 친 검색어 상위 10</div>%s</div></div>
<div class="card w" style="margin-top:18px;font-size:18px">해결 · 일상 병명 사전 <b class="em">185개</b>(흔히 쓰는 병명 → 공식 병명 글자로만 연결 · 질병코드는 넣지 않음) · 초성 검색 · 질병코드 직접 검색</div>''' % C.hbars(TERMS, lw=150, fs=17, h=20, hi=1),
'여섯 번째 사례는 일상 병명과 공식 병명의 차이입니다. 직접 친 검색어 1위는 대장용종이었습니다. 그런데 약관과 질병분류의 공식 병명은 결장의 용종, 직장용종이라 글자가 달라 검색이 되지 않았습니다. 오른쪽 상위 10 검색어에는 초성으로 친 검색어도 여럿 보입니다. 그래서 흔히 쓰는 병명을 공식 병명 글자로 잇는 일상 병명 사전 185개를 만들었고, 초성 검색과 질병코드 직접 검색도 붙였습니다.',
'PART 2 · 사례 6 일상 병명', '고객이 말하는 병명 ≠ 약관에 적힌 병명', '', SRC_U + ' · 공식 병명 : 특약검색기 코드명 · 사전 : ui/meai-lex.js', 'PART 2', z=1.16)

# 그래서 · 컨닝페이퍼
PROB = [('약관 1,830쪽', '한 권이 2천 쪽에 가까움'), ('이름 평균 %.1f자' % AVG, '둘 중 하나는 20자 넘음'), ('용어 5개', '이름 하나 읽는 데'),
        ('비슷한 이름', '보장 코드는 다름'), ('통합치료비 %d종' % len(ITN), '가장 헷갈리는 특약'), ('일상 병명', '공식 병명과 글자가 다름')]
pl = ''.join('<div style="display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid #EEF0F2"><span class="dot" style="width:32px;height:32px;font-size:15px;border-radius:9px">%d</span><b style="font-size:18px;width:150px;flex:none">%s</b><span style="font-size:15px;color:#6B7684">%s</span></div>' % (i + 1, a, b) for i, (a, b) in enumerate(PROB))
SOL = [('아무렇게나 쳐도 찾음', '병명 · 코드 · 초성 · 일상 병명'), ('한 화면에 근거까지', '약관 원문 · 별표 · 질병코드'), ('어려운 건 숫자로', '보상 10단계 · 통합치료비 1년 금액'), ('용어는 누르면 설명', '쉬운 설명 907개')]
sl = ''.join('<div class="card" style="padding:16px 20px;margin-top:%dpx;background:#fff"><b style="font-size:19px">%s</b><div style="font-size:15px;color:#6B7684;margin-top:4px">%s</div></div>' % (0 if i == 0 else 12, a, b) for i, (a, b) in enumerate(SOL))
slide('''<div class="row" style="gap:20px;align-items:stretch">
<div class="card w" style="flex:1.45"><span class="tag g">현장 문제</span><div style="margin-top:8px">%s</div></div>
<div style="width:70px;display:grid;place-items:center;font-size:44px;color:#C8102E">→</div>
<div class="card" style="flex:1;background:#FDECEE;border-color:#F8D3D9"><span class="tag" style="background:#fff">영업 컨닝페이퍼</span><div style="margin-top:14px">%s</div></div>
<div style="width:70px;display:grid;place-items:center;font-size:44px;color:#C8102E">→</div>
<div class="card" style="flex:.8;display:flex;flex-direction:column;justify-content:center;text-align:center"><div style="font-size:18px;color:#4E5968">상담 중 확인 시간</div>
<div style="margin-top:10px;font-size:30px;font-weight:700;color:#8B95A1;text-decoration:line-through">10분</div><div class="num r" style="font-size:74px">30<small>초</small></div>
<div style="margin-top:10px"><span class="tag g">가정값</span></div><div style="margin-top:14px;font-size:16px;color:#4E5968">「확인하고 연락드릴게요」 → 그 자리에서 답</div></div></div>''' % (pl, sl),
'그래서 필요했던 것이 영업 컨닝페이퍼입니다. 2천 쪽 가까운 약관, 평균 20자가 넘는 특약 이름, 이름 하나에 용어 다섯 개, 비슷하지만 범위가 다른 이름, 통합치료비 여러 종, 일상 병명과 공식 병명의 차이. 이 여섯 가지 문제를 아무렇게나 쳐도 찾고, 한 화면에 근거까지 보여 주고, 어려운 것은 숫자로, 용어는 누르면 설명하는 방식으로 풀었습니다. 상담 중 확인 시간을 10분에서 30초로 줄인다는 것이 목표였고, 이 숫자는 내부 추정 가정값입니다.',
'PART 2 · 그래서', '상담 중 30초 안에 꺼내 보는 영업 컨닝페이퍼', '', '확인 시간 10분 → 30초 : 내부 추정 가정값 · 나머지 숫자는 앞 장 출처 그대로', 'PART 2', z=1.2)

# ══ PART 3 · 애용 이유 ═══════════════════════════════════
section('3', '현장이 애용한 이유', '왜 공식 배포 없이도 퍼졌나', 'merry_ok.webp', '세 번째로, 현장이 이 도구를 왜 애용했는지 보겠습니다. 공식 배포나 교육이 없었는데도 영업가족끼리 소개하며 퍼졌습니다.')

WHY = [('고객 앞에서 바로 답함', '병명 · 코드 · 초성 · 일상 병명 무엇으로 쳐도 찾음 · 「확인하고 연락드릴게요」 대신 그 자리에서 답', '질병 · 검색 19,483건', 19483),
       ('약관 원문이 근거', '특약 본문 · 별표 · 질병코드를 원문 그대로 보여 줌 · 설계사마다 다르던 설명이 같아짐', '상세조회 7,499건', 7499),
       ('보장 공백이 눈에 보임', '질병 하나로 진단~사망 단계별 건수 · 0건인 단계가 곧 공백 · 추가 제안이 권유가 아닌 설명이 됨', '보상시뮬레이터 26%', None),
       ('가장 어려운 통합치료비를 숫자로', '치료 과정만 고르면 특약별 1년 금액 · 0원인 이유까지 문장으로', '상세조회 상위 8개 중 7개', None),
       ('어려운 용어를 바로 풀어 줌', '비급여 · 전액본인부담 · 암중점치료기관 등 보험용어에 밑줄 · 누르면 쉬운 설명 한 줄', '쉬운 설명 907개', None),
       ('IT 개발 버퍼링 없이 즉각 신규 정보 반영', '오류는 즉각 수정 · 신담보 · 약관 개정도 바로 반영', '갱신 78회 · 감사 325건', None)]
cards = ''.join('<div class="card" style="width:calc(33.33%% - 14px);padding:24px 26px;display:flex;flex-direction:column"><div style="display:flex;gap:14px;align-items:center"><span class="dot">%d</span><div class="h3" style="font-size:21px">%s</div></div>'
                '<div class="p" style="font-size:16px;flex:1">%s</div><div style="margin-top:14px"><span class="tag">%s</span></div></div>' % (i + 1, t, d, g) for i, (t, d, g, _) in enumerate(WHY))
slide('<div style="display:flex;flex-wrap:wrap;gap:18px 20px">%s</div>' % cards,
'현장이 애용한 이유를 여섯 가지로 정리했습니다. 첫째, 고객 앞에서 바로 답할 수 있습니다. 둘째, 약관 원문이 근거라 설명이 설계사마다 달라지지 않습니다. 셋째, 보상시뮬레이터로 보장 공백이 눈에 보여 추가 제안이 설명이 됩니다. 넷째, 가장 어려운 통합치료비를 숫자로 보여 줍니다. 다섯째, 비급여나 암중점치료기관 같은 어려운 용어를 누르면 쉬운 설명이 바로 뜹니다. 여섯째, IT 개발 버퍼링 없이 새 정보가 즉각 반영됩니다. 오류는 즉각 수정하고, 신담보와 약관 개정도 바로 반영합니다. 아래 꼬리표는 각 이유를 뒷받침하는 숫자입니다.',
'PART 3 · 애용 이유', '현장이 이 도구를 계속 연 여섯 가지 이유', '', '근거 숫자는 사용 통계 서버 익명 기록 전수 분석(2026.6.22~11.25) · 저장소 기록', 'PART 3', z=1.2)

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
'PART 3 · 상담 장면 변화', '「확인하고 연락드릴게요」가 사라짐', '', '도구 화면 기능 기준(2026.11.25)', 'PART 3', z=1.22)

def screen(capname, kick, title, pts, notes, src):
    li = ''.join('<div style="display:flex;gap:16px;margin-top:30px"><span class="dot" style="width:40px;height:40px;font-size:18px;border-radius:12px">%d</span><div style="font-size:23px;line-height:1.5;color:#333D4B">%s</div></div>' % (i + 1, p) for i, p in enumerate(pts))
    slide('<div class="row" style="gap:40px;align-items:flex-start"><div class="shot" style="width:900px"><img src="%s"></div><div style="flex:1">%s</div></div>' % (cap(capname), li),
          notes, kick, title, '', src, 'PART 3')
screen('tool', 'PART 3 · 화면으로 보면 ①', '특약검색기 : 아무렇게나 쳐도 찾음',
       ['「뇌경색」만 쳐도 질병코드 · 연관 질병 · 연관 특약 자동완성', '초성(ㄱㅅㅅㅇ) · 일상 병명(대장용종 → 결장의 용종)도 찾음', '카드를 열면 약관 원문 · 별표 · 사각지대 · 상위호환까지'],
       '특약검색기 화면입니다. 뇌경색만 쳐도 질병코드와 연관 질병, 연관 특약이 바로 뜹니다. 초성이나 대장용종 같은 일상 병명으로도 찾고, 카드를 열면 약관 원문과 별표, 이 특약이 못 막는 사각지대와 상위호환 특약까지 보여 줍니다.', '화면 : 특약검색기(2026.11.25 판)')
screen('sim_c16', 'PART 3 · 화면으로 보면 ②', '보상시뮬레이터 : 보장 흐름이 한눈에',
       ['위암 → 받을 수 있는 특약 328개(상품별 704건)', '진단 · 검사 · 수술 · 입원 … 사망 10단계 건수', '예상 수술종류 · MeAI 조회 프롬프트 복사'],
       '보상시뮬레이터 화면입니다. 위암을 고르면 6개 상품에서 받을 수 있는 특약 328개, 상품별로 704건을 진단부터 사망까지 10단계로 나눠 보여 줍니다. 0건인 단계가 곧 보장 공백이라 추가 제안의 근거가 됩니다.', '화면 : 보상시뮬레이터(2026.11.25 판 · 위암 C16)')
screen('itc', 'PART 3 · 화면으로 보면 ③', '통합치료비 시뮬레이터 : 어려운 특약을 숫자로',
       ['질병과 치료 과정을 고르면 특약별 1년 금액 합계', '치료 단계마다 어느 특약에서 얼마 · 0원이면 이유', '가입금액별 비교 · 1년 이내 감액 · 5년 치료 계획'],
       '통합치료비 시뮬레이터 화면입니다. 질병과 치료 과정을 고르면 특약별로 1년 동안 받는 금액이 합산되고, 치료 단계마다 어느 특약에서 얼마가 나오는지, 안 나오면 왜인지 문장으로 나옵니다.', '화면 : 통합치료비 시뮬레이터(2026.11.25 판 · 급성 심근경색 · 기본 조합)')

EF = [('업무효율', 2.63, '#C8102E'), ('매출증진', 2.28, '#6D5BD6'), ('신담보 전파 절감', 1.0, '#F2B705'), ('민원 리스크 감소', 1.0, '#23874C')]
slide('''<div class="row" style="gap:22px;align-items:stretch">
 <div class="card" style="flex:1"><div class="h3">데이터를 믿을 수 있는 이유</div>
  <div class="p" style="font-size:17px">· 메리츠화재 상품 공시실 판매 약관(2610 판) 내려받아 원문 파싱<br>· 질병코드 · 금액은 추정하지 않음 · 없으면 빈칸<br>· 2026.9 전수 감사 325건 바로잡음<br>· 약관이 바뀌면 같은 스크립트로 다시 대조<br>· 표 · 사전 · 같은 이름 특약 자동 점검</div>
  <div class="h3" style="margin-top:22px">운영 방식</div>
  <div class="p" style="font-size:17px">· 개발 · 서버 · 라이선스 0원<br>· 오류 즉각 수정 · 신담보 즉각 반영(갱신 78회)<br>· 고객 개인정보 받지도 저장하지도 않음</div></div>
 <div class="card w" style="flex:1.1"><div class="h3">연간 기대효과 <span class="tag g" style="vertical-align:middle">가정값</span></div>
  <div style="display:flex;gap:24px;align-items:center;margin-top:18px">%s<div style="flex:1">%s</div></div>
  <div class="p" style="font-size:15px;margin-top:16px">내부 추정 산식(1인 월 상담 3건 · 확인 시간 10분 → 30초 · 3,667명 등) · 통합치료비 시뮬레이터 효과 미포함</div></div>
</div>''' % (C.donut(EF, 250, '6.91억', '연간 · 가정값'), C.legend([(n, v, c) for n, v, c in EF], '억', 18)),
'데이터를 믿을 수 있는 이유와 운영 방식, 기대효과입니다. 모든 데이터는 메리츠화재 상품 공시실에서 판매 약관을 내려받아 원문을 그대로 파싱한 것이고, 질병코드와 금액은 추정하지 않고 없으면 빈칸으로 둡니다. 9월 전수 감사에서 325건을 바로잡았습니다. 비용은 0원이고, 오류는 즉각 수정하고 새 정보는 즉각 반영합니다. 연간 기대효과는 내부 추정 산식으로 계산한 가정값으로 약 6.91억원이며, 업무효율 2.63억, 매출증진 2.28억, 신담보 전파 절감과 민원 리스크 감소가 각 1억입니다. 통합치료비 시뮬레이터 효과는 넣지 않았습니다.',
'PART 3 · 신뢰와 운영', '메리츠화재 상품 공시실 약관을 내려받아 원문 파싱 · 추정 없음', '', '기대효과 : 내부 추정 산식(1인 월 상담 3건 · 확인 시간 10분 → 30초 · 3,667명 등) · 모두 가정값', 'PART 3', z=1.36)

# ══ PART 4 · MeAI · 스마트 제안서로 이어짐 ═══════════════
section('4', 'MeAI · 스마트 제안서로', '도구에서 다듬은 자산이 정식 서비스로', 'rara_present.webp',
'네 번째로, 이 영업지원도구를 만들며 쌓은 구성 요소와 소스가 지금 MeAI 에 어떻게 반영되고 더 정교해졌는지, 그리고 회사 정식 전산으로 들어가게 개발 중인 스마트 제안서에 어떻게 쓰이고 있는지 보겠습니다.')

MA = [('보험용어 사전', '388 → 1,386개', '약관 실제 용례 · KCD 분류번호 표기 · 1,386개 전부 중요도 순위', 'MeAI 참고 · 도구 밑줄 설명 907개', '#C8102E'),
      ('MeAI 프롬프트', '272개 + 자동 생성', '영업 단계별 라이브러리 · 도구 결과(질병 · 특약 · 보장 공백)로 조회 프롬프트 자동 생성', '도구 → MeAI 복사 1,137건', '#6D5BD6'),
      ('간편보험 예외질환', '심사 매뉴얼 · 가이드라인', '경우의 수 엑셀 → MeAI 참고자료(RAG)용 문서로 정리(10.16 시행 기준)', 'MeAI 참고자료(RAG) 문서', '#23874C'),
      ('상품 · 보상 데이터', 'JSON + 판정 규칙 문서', '6개 상품 특약 · 질병코드 · 보상 판정 규칙을 AI 가 바로 읽는 꼴로 반출', '다른 AI 대화에서 그대로 사용', '#F2B705'),
      ('수술비 보상 규칙', '1-5종 · 1-7종 · N대 · KCD 로직', '130대 · 131대질병수술비 · 1-5종 수술분류표Ⅱ(99줄) · 1-7종 분류표의 보장 질병코드 · 수술행위를 약관 별표와 대조해 규칙화', 'MeAI 이식 · 수술비 질문 판정 기준', '#2563C9'),
      ('MeAI 홈 넛지', '목업 + 개발 패키지 v5', '오늘의 MeAI · 화법 798건 · 보상 판정 엔진 · 설계도 · API · DB', 'MeAI 홈 고도화 제안 · 이식 예정', '#A23A91')]
mcards = ''.join('<div class="card" style="width:calc(33.33%% - 14px);padding:22px 24px;border-top:5px solid %s"><div style="font-size:15px;font-weight:700;color:%s">%s</div><div class="h3" style="font-size:23px;margin-top:6px">%s</div>'
                 '<div class="p" style="font-size:15px;margin-top:8px">%s</div><div style="margin-top:12px;font-size:14px;color:#191F28;background:#fff;border:1px solid #EEF0F2;border-radius:8px;padding:7px 10px">→ %s</div></div>' % (c, c, a, b, d, u) for a, b, d, u, c in MA)
slide('<div style="display:flex;flex-wrap:wrap;gap:18px 20px">%s</div>' % mcards,
'영업지원도구를 만들며 쌓은 것 가운데 MeAI 에 반영하고 더 정교하게 다듬은 구성 요소는 여섯 가지입니다. 첫째, 보험용어 사전은 388개에서 1,386개로 늘렸고 약관 실제 용례와 질병분류 번호, 중요도 순위를 붙였습니다. 둘째, MeAI 프롬프트는 272개 라이브러리에 더해 도구 결과로 조회 프롬프트를 자동으로 만들어 주며, 실제로 1,137번 복사됐습니다. 셋째, 간편보험 예외질환 심사 매뉴얼과 가이드라인을 MeAI 참고자료용 문서로 정리했습니다. 넷째, 6개 상품 특약과 질병코드, 보상 판정 규칙을 AI 가 바로 읽는 꼴로 반출했습니다. 다섯째, 수술비 1-5종, 1-7종, 130대와 131대 같은 N대 질병수술비의 보상 규칙과 질병코드 판정 로직을 약관 별표와 대조해 만든 뒤 MeAI 에 이식했고, 여섯째, MeAI 홈 넛지 목업과 개발 패키지를 만들었습니다.',
'PART 4 · MeAI 에 반영한 것', '도구에서 만든 구성 요소 · 소스 6가지가 MeAI 로', '', '저장소 기록 : 용어사전 2026.9.21~28 · 반출 파일 9.21 · 수술비 보상 규칙 11.3(dist/surgery_benefit_kcd_2611.xlsx) · 예외질환 10.16 · 10.22 · 홈 넛지 v5 10.29 · 복사 건수는 사용 통계', 'PART 4', z=1.3)

GLO = [('9.21', 388), ('9.21', 653), ('9.21', 1076), ('9.21', 1138), ('9.21', 1243), ('9.22', 1280), ('9.22', 1316), ('9.22', 1386)]
GLO = [('%d차' % (i + 1), v) for i, (_, v) in enumerate(GLO)]
slide('''<div class="row" style="gap:22px;align-items:stretch">
<div class="card w" style="flex:1.2"><div class="h3" style="font-size:20px">보험용어 사전 · 판을 거듭하며 정교화 <span class="tag g" style="vertical-align:middle">2026.9.21~22</span></div>%s
<div style="font-size:15px;color:#6B7684;line-height:1.6">약관 별표 · 메디컬 용어 → 현장 방언 · 특약 약어 → 메디컬 개념 105개 → KCD 분류번호 표기 · 치매 · 간병 → 감수 데이터 → 치매간병 · 또또암 약관</div></div>
<div class="card" style="flex:.8"><div class="h3" style="font-size:20px">도구 → MeAI 로 이어지는 흐름</div>
<div style="margin-top:16px;display:flex;flex-direction:column;gap:10px">%s</div></div></div>''' % (
    C.line(GLO, 800, 380, '개'),
    '<div style="font-size:16px;color:#6B7684;text-align:center">▼</div>'.join('<div style="padding:14px 18px;border-radius:14px;background:#fff;border:1px solid #EEF0F2"><b style="font-size:18px">%s</b><div style="font-size:15px;color:#6B7684;margin-top:3px">%s</div></div>' % x for x in
        [('도구에서 찾기', '질병 · 특약 · 보장 공백 확인'), ('프롬프트 자동 생성', '찾은 결과가 질문 문장에 들어감'), ('MeAI 에 붙여 넣기', '고객 맞춤 설명 · 보장분석 문장'), ('MeAI 가 참고하는 자료', '용어 사전 · 예외질환 문서 · 보상 데이터')])),
'정교화가 어떻게 이루어졌는지 보험용어 사전을 예로 보겠습니다. 388개로 시작해 약관 별표와 메디컬 용어, 현장 방언과 특약 약어, 메디컬 개념, 질병분류 번호 표기, 치매와 간병, 새 약관까지 판을 거듭하며 1,386개가 됐습니다. 오른쪽은 도구와 MeAI 가 이어지는 흐름입니다. 도구에서 질병과 특약, 보장 공백을 찾으면 그 결과가 들어간 질문 문장이 자동으로 만들어지고, MeAI 에 붙여 넣어 고객 맞춤 설명을 받습니다. MeAI 가 참고하는 자료로도 용어 사전과 예외질환 문서, 보상 데이터를 넘겼습니다.',
'PART 4 · 정교화', '용어 388 → 1,386개 · 도구 결과가 MeAI 질문이 됨', '', '저장소 기록 : 보험용어사전 판별 개수(docs/보험용어사전_1386개_2026.09.xlsx) · 프롬프트 연결 : MeAI 가이드북 PART 7', 'PART 4', z=1.12)

SRC4 = [('약관 PDF', '판매 약관 %d종 · %s쪽' % (len(PAGES), format(PTOT, ','))), ('특약 마스터', '특약 본문 · 별표 · 금액표'), ('질병코드 원장', '약관 분류표 그대로 · 추정 없음'), ('계산 규칙', '지급 조건 · 보상 유형 판정')]
OUT3 = [('영업지원도구', '상담 중 컨닝페이퍼 · 157일 73,820건', '#C73D1C', False), ('스마트 제안서', '회사 정식 전산 탑재 개발 중 · GA · TA · PA 모두 시행', '#C8102E', True), ('세일즈북 생성기', '상품설명서 → 영업 가이드북', '#6D5BD6', False)]
src_html = ''.join('<div style="padding:14px 18px;border-radius:14px;background:#fff;border:1px solid #E5E8EB;margin-top:%dpx"><b style="font-size:18px">%s</b><div style="font-size:14px;color:#6B7684;margin-top:2px">%s</div></div>' % (0 if i == 0 else 10, a, b) for i, (a, b) in enumerate(SRC4))
out_html = ''.join('<div style="padding:18px 22px;border-radius:16px;margin-top:%dpx;%s"><b style="font-size:21px;color:%s">%s</b><div style="font-size:15px;color:#4E5968;margin-top:4px">%s</div></div>' % (
    0 if i == 0 else 12, 'background:#FDECEE;border:2px solid #C8102E' if hi else 'background:#fff;border:1px solid #E5E8EB', c, a, b) for i, (a, b, c, hi) in enumerate(OUT3))
SPX = [('24', '개', '스마트 제안서 특약 마스터 상품'), ('24,854', '줄', '정보계 담보코드 전 줄 계산 대조'), ('889', '곳', '프리미엄 건강 설계 1건 인쇄 검증 통과')]
slide('''<div class="row" style="gap:18px;align-items:stretch">
<div class="card" style="flex:.9"><span class="tag g">같은 원천</span><div style="margin-top:12px">%s</div></div>
<div style="width:60px;display:grid;place-items:center;font-size:40px;color:#C8102E">→</div>
<div style="flex:1.15">%s</div>
<div style="flex:.85;display:flex;flex-direction:column;gap:12px">%s
<div class="card w" style="padding:16px 18px;font-size:15px;line-height:1.55">IT 인계 묶음 · 담보코드 입력 API(설계서 없이 담보 목록으로 제안서) 준비 완료</div></div></div>''' % (
    src_html, out_html, ''.join('<div class="card" style="padding:16px 20px"><div class="num" style="font-size:38px">%s<small style="font-size:18px">%s</small></div><div class="lab" style="font-size:14px;margin-top:4px">%s</div></div>' % x for x in SPX)),
'마지막으로 스마트 제안서입니다. 영업지원도구를 만들며 쌓은 원천, 즉 약관 PDF에서 뽑은 특약 마스터와 질병코드 원장, 계산 규칙은 영업지원도구만 쓰는 것이 아닙니다. 같은 원천을 스마트 제안서와 세일즈북 생성기가 함께 씁니다. 특히 스마트 제안서는 회사 정식 전산에 들어가도록 개발 중이며, GA, TA, PA 부문 모두 시행합니다. 스마트 제안서용 특약 마스터는 24개 상품으로 넓혔고, 정보계 담보코드 24,854줄을 한 줄씩 계산해 대조했으며, 프리미엄 건강보험 실제 설계 한 건으로 인쇄된 값 889곳을 검증했습니다. IT 인계 묶음과 설계서 없이 담보 목록만으로 제안서를 만드는 담보코드 입력 방식도 준비돼 있습니다. 현장 도구에서 다듬은 데이터가 그대로 정식 전산의 기반이 되고 있습니다.',
'PART 4 · 스마트 제안서', '같은 특약 마스터 · 질병코드 · 계산 규칙이 정식 전산 스마트 제안서로', '', '작업 규칙 문서(CLAUDE.md) · proposal_smart/README.md(v9.06 담보코드 입력 · v9.07 전 줄 대조 · v9.09~ 프리미엄) · 2026.11.25 기준', 'PART 4', z=1.4)


SPM = [('특약 마스터(1,149종)', '특약검색기 데이터 감수본 → db.json', '모든 칸 계산의 원천 · 담보 이름 맞추기'),
       ('질병코드 원장(약관 별표)', '특약마다 질병코드 · 제외 코드', '암 · 뇌혈관 · 심장 칸의 지급 판정'),
       ('통합치료비 금액표 13종', '통합치료비 시뮬레이터와 같은 표', '보장요약 · 암 · 뇌심 쪽 치료비 금액'),
       ('수술비 종(1-5종 · 1-7종 · 130대)', '수술비 비교 · 분류표 정리', '주요수술 카드 다섯 줄'),
       ('같은 이름 특약 정리 · 띄어쓰기 규칙', '상품만 다른 같은 특약을 한 카드로', '설계서 담보명 → 특약 찾기'),
       ('전수 감사 · 자동 점검', '9월 325건 바로잡음 · 표 · 금액 점검', '점검 하네스 · 인쇄 검증(값 = 지면)')]
tr = ''.join('<tr><td style="font-weight:700">%s</td><td style="color:#6B7684">%s</td><td style="text-align:center;color:#C8102E;font-size:22px">→</td><td style="font-weight:600">%s</td></tr>' % x for x in SPM)
slide('<table><tr><th style="width:30%%">영업지원도구에서 만들고 다듬은 것</th><th style="width:30%%">도구에서는</th><th style="width:6%%"></th><th>스마트 제안서에서는</th></tr>%s</table>'
      '<div class="card" style="margin-top:20px;font-size:18px;line-height:1.6">현장 도구에서 매일 쓰이며 검증된 데이터 → <b class="em">회사 정식 전산 스마트 제안서의 계산 기반</b> · 약관이 바뀌면 한 번 고쳐 세 곳(도구 · 제안서 · 세일즈북)이 함께 바뀜</div>' % tr,
'영업지원도구에서 만들고 다듬은 것이 스마트 제안서에서 어디에 쓰이는지 하나씩 보겠습니다. 특약 1,149종의 마스터는 특약검색기 데이터를 감수한 것으로, 제안서 모든 칸 계산의 원천입니다. 약관 별표에서 옮긴 질병코드 원장은 암, 뇌혈관, 심장 칸의 지급 판정에 쓰입니다. 통합치료비 시뮬레이터와 같은 금액표가 제안서의 치료비 금액이 되고, 수술비 종 정리는 주요수술 카드의 다섯 줄이 됩니다. 같은 이름 특약 정리는 설계서 담보명으로 특약을 찾는 데, 전수 감사와 자동 점검은 제안서 점검과 인쇄 검증으로 이어졌습니다. 현장에서 매일 쓰이며 검증된 데이터가 정식 전산의 계산 기반이 되는 것이고, 약관이 바뀌면 한 번 고쳐 세 곳이 함께 바뀝니다.',
'PART 4 · 스마트 제안서에 쓰이는 곳', '도구에서 다듬은 데이터 → 정식 전산 스마트 제안서의 계산 기반', '', '작업 규칙 문서(CLAUDE.md 「세 산출물은 함께 간다」 · 「어디를 고치나」) · proposal_smart/README.md · 2026.11.25 기준', 'PART 4', z=1.18)

# ── 24. 맺음 ─────────────────────────────────────────────
full('''<div class="sl" style="padding:0;background:#fff">
  <div style="position:absolute;inset:0;background:radial-gradient(50%% 60%% at 50%% 0%%,rgba(200,16,46,.07),transparent 70%%)"></div>
  <div style="position:absolute;left:0;right:0;top:200px;text-align:center">
    <div style="font-size:60px;font-weight:700;letter-spacing:-.03em;line-height:1.3">그동안 영업지원도구를<br><span class="em">사랑해주셔서</span> 감사합니다.</div></div>
  <div style="position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:center;align-items:flex-end;gap:26px">%s</div>
</div>''' % ''.join('<img src="%s" style="height:%dpx;width:auto">' % (doll(f), h) for f, h in
                    [('merry_ok.webp', 190), ('eco_point.webp', 190), ('rara_present.webp', 190), ('indi_idea.webp', 190), ('tata_ok.webp', 190), ('ziziri_cheer.webp', 150)]),
'그동안 영업지원도구를 사랑해 주셔서 감사합니다.')

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
