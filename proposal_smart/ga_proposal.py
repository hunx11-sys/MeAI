# -*- coding: utf-8 -*-
"""메리츠 GA 스마트 제안서(v5 양식) — 설계서 PDF 를 넣으면 GA 양식 PDF 를 만든다.

  python ga_proposal.py 설계서.pdf [결과.pdf] [나이]        # 한 건
  python ga_proposal.py 폴더                                 # 폴더 안 PDF 전부 → 폴더\ga_output\
  윈도우 : make_ga.bat 에 설계서 PDF 를 끌어다 놓는다(여러 개 가능). 그냥 실행하면 ga_input 폴더의 PDF 를 모두 만든다.

· 쪽 구성(GA 내부 회의 목업 2026-10-08 · GA지원센터 수정사항 2026-10-22) : 표지(상품명 · 피보험자 · 가계약번호 · 월 보험료 · 컨설턴트 · 탑재상품) ·
  1 보장요약(암 · 뇌심 · 주요수술 12 · 간병인) · 2 암보장 · 3 뇌·심보장 · 4~ 예상 보장금액 세부내역(= 보장요약 칸의 합산 계산서 · 반드시 붙는다 — CALC_PAGES)
· 칸의 정의(사례 · 집계 방식 · 표시 조건)는 전부 ga_spec.CELLS 에 있고, 이 파일은 그 값을 꺼내 그리기만 한다(지면 = 사양).
· 금액은 전부 계산 엔진(scen_engine.pay_lines)에 이 설계서의 가입 특약을 넣어 얻는다. 사례 조건(질병코드·수술 분류·병원 종별·
  마취시간·약물 종수)은 가정값이다. 코드·금액을 여기서 만들지 않는다(CLAUDE.md 1·2). 간병인 칸만 설계서 가입금액을 그대로 읽는다(ga_care).
· 캐릭터는 GA 가안 이미지에서 잘라 넣었다(ga_assets). 사내 테스트용.
"""
import os, sys, re, base64, glob, json, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pipeline, build_all as BA, scen_engine as S, ga_spec as GS, ga_care as CARE, ga_overlay as OV   # noqa: E402

VERSION = (re.search(r"VERSION\s*=\s*'([^']+)'", open(os.path.join(BASE, 'api.py'), encoding='utf-8').read()) or [None, ''])[1]
BRAND = '메리츠 스마트 제안서'          # 「당사만의 고유명칭」 자리 — GA 가 정하면 여기만 바꾼다(미정 2026-10-08)
won = CARE.won
# 표지 「탑재상품」(GA 명칭 그대로 · GA 메모 2026-10-08) — 설계서 상품명을 읽는 규칙이지 화이트리스트가 아니다(목록 밖 상품도 그대로 만든다 · CLAUDE.md 4)
GA_PRODUCTS = [('(무)메리츠The건강한내Mom대로5.10.5보장보험', r'The건강한\s*(메리츠)?\s*내Mom대로\s*5\.10\.5'),
               ('(무)메리츠The건강한5.10.5보장보험', r'The건강한\s*5\.10\.5'),
               ('(무)알파Plus보장보험', r'(?<!The좋은)\s*(알파\s*Plus|케어프리보험\s*M-?\s*Basket)'),          # 알파Plus = 케어프리 M-Basket(GA 명칭이 다를 뿐 같은 상품 · 소유자 2026-10-08)
               ('(무)메리츠The좋은알파Plus보장보험', r'The좋은\s*(알파|케어프리)'),
               ('(무)내Mom같은어린이보험(태아전용포함)', r'내Mom같은'),
               ('(무)내Mom대로보장보험', r'^(?!.*(The좋은|5\.10\.5)).*내Mom대로\s*보장보험'),
               ('(무)메리츠The좋은내Mom대로보장보험2607', r'The좋은\s*내Mom대로'),
               ('(무)메리츠통합간편건강보험(연,세만기형)', r'^(?!.*355).*통합간편건강보험'),
               ('(무)메리츠통합간편건강보험(연,세만기형)2607(355입원,수술고지간편심사형)', r'통합간편건강보험.*355'),
               ('(무)The가벼운간편355건강보험(세만기형)', r'가벼운\s*간편\s*355'),
               ('(무)메리츠간편31건강보험2607', r'간편\s*31'),
               ('(무)메리츠또걸려도또받는암보험(연,세만기형)', r'또\s*걸려도\s*또\s*받는\s*암보험'),
               ('(무)메리츠또걸려도또받는간편한암보험(연,세만기형)', r'또\s*걸려도\s*또\s*받는\s*간편한\s*암보험'),
               # 2026-10-31 개정 : 또걸려도 2종 판매중지 → (무)(메리츠) 암보험(세만기형)·(연만기형)2610 신상품(개정안 v6.0 상품List 1118·1119). 옛 이름은 기존 설계서를 위해 남긴다
               ('(무)(메리츠)암보험(세만기형)2610', r'^\(무\)\(?메리츠\)?암보험\(세만기형\)'),
               ('(무)(메리츠)암보험(연만기형)2610', r'^\(무\)\(?메리츠\)?암보험\(연만기형\)')]
def ga_product_idx(product):
    p = re.sub(r'\s+', '', product or '')
    hits = [i for i, (_, pat) in enumerate(GA_PRODUCTS) if re.search(pat.replace(r'\s*', ''), p)]
    if not hits: return None
    # 더 구체적인 이름(긴 패턴)이 이기도록 — The건강한내Mom대로5.10.5 는 The건강한5.10.5 에도 걸린다
    return max(hits, key=lambda i: len(GA_PRODUCTS[i][1]))

# ───────── 설계서 읽기 + 공통 계산(한 건마다 load() 가 다시 채운다) ─────────
RID, META, WHO, PRODUCT, PREMIUM, NRID, SHORTP = [], {}, '', '', '', 0, ''
HEAD = {}                                       # 표지·1쪽 머리줄 : 피보험자 이름·성별·보험나이·가계약번호·컨설턴트(설계서에 적힌 글자만 · 못 읽으면 빈칸)
def ga_head(design_pdf, age=''):
    """설계서 앞쪽 글자에서 GA 표지에 적는 항목을 읽는다(GA 2026-10-22 : 상품명 · 피보험자(이름, 성별, 보험나이) · 가계약번호 · 월 보험료 · 컨설턴트).
    글자 그대로 적힌 것만 읽고 추정하지 않는다 — 없으면 빈칸으로 두고 로그에 남긴다(보험나이는 넘겨받은 값이 우선 · 설계서에 「○○세」로 명시된 것만 보조로 읽는다)"""
    import pdfplumber
    with pdfplumber.open(design_pdf) as pdf:
        t = '\n'.join((pg.extract_text() or '') for pg in pdf.pages[:3])
    def g(pat, d=''):
        m = re.search(pat, t); return m.group(1).strip() if m else d
    name = META.get('insured') or ''
    if name in ('', '고객'): name = ''
    sex = {'F': '여자', 'M': '남자'}.get(META.get('sex') or '', '')      # 가안 표기 「민메리 (여자, 20세)」
    ag = age or g(r'보험나이\s*[:：]?\s*(\d{1,3})\s*세') or g(r'피보험자\s*\S+\s*\(\s*(?:남|여)\s*[,·]\s*(\d{1,3})\s*세')
    if ag and not ag.endswith('세'): ag += '세'
    no = g(r'가계약번호\s*[:：]?\s*([A-Za-z0-9][A-Za-z0-9-]{4,})')
    agent = re.sub(r'\s+', ' ', META.get('agent') or '').strip()          # 설계서 「영업담당자 … 발행정보」 사이 글자 그대로(예비)
    # 설계서 표지(1쪽)에 「소속 ○○ / 컨설턴트 ○○ / 휴대전화 / 전화번호 / 가계약번호」 가 글자로 적혀 있다(2026-10-23 설계서 5건 확인) — 그 글자를 그대로 읽는다
    org = g(r'소\s*속\s+(\S+)'); agent_name = g(r'컨설턴트\s+([가-힣]{2,6})')
    mobile = g(r'휴대전화\s*[:：]?\s*(01[016789]-?\d{3,4}-?\d{4})') or g(r'(01[016789]-?\d{3,4}-?\d{4})')
    tel = g(r'전화번호\s*[:：]?\s*(0\d{1,2}-?\d{3,4}-?\d{4})') or g(r'(?<!\d)(0(?:2|[3-6]\d)-?\d{3,4}-?\d{4})(?!\d)')
    code = g(r'(?:설계사|모집인|컨설턴트|대리점)\s*코드\s*[:：]?\s*(\d{5,})')          # 「코드」가 가계약번호 앞 9자리인지는 GA 확인 전 — 글자로 적힌 것만
    if not (org and agent_name) and agent:                                        # 1쪽에 없으면 「영업담당자」 줄에서 어림(소속 글자 · 2~5자 이름)
        rest = re.sub(r'0\d{1,2}-?\d{3,4}-?\d{4}', ' ', agent).split()
        org = org or next((w for w in rest if re.search(r'대리점|지점|본부|사업단|지사|센터|보험|GA', w)), rest[0] if rest else '')
        agent_name = agent_name or next((w for w in rest if w != org and re.fullmatch(r'[가-힣]{2,5}', w)), '')
    missing = [k for k, v in (('피보험자 이름', name), ('성별', sex), ('보험나이', ag), ('가계약번호', no), ('컨설턴트 소속', org), ('컨설턴트 이름', agent_name), ('휴대전화', mobile), ('코드', code)) if not v]
    if missing: S.ISSUES.append({'구분': '표지', '담보': '-', '사유': '설계서에서 읽지 못한 표지 항목 : ' + ' · '.join(missing) + ' (빈칸 「-」으로 둠)'})
    return dict(name=name, sex=sex, age=ag, no=no, agent=agent, org=org, agent_name=agent_name, mobile=mobile, tel=tel, code=code)
VAL = {}                                        # 칸 key → (값, 지급 줄, 로그)  — ga_spec.cell_value
AUDIT = {}                                      # 마지막 build 의 감사 로그(요약·계산 제외 사유) — 웹 화면 「감사 로그」 탭
def load(design_pdf, age=''):
    """설계서 한 건을 읽어 모든 칸 값을 채운다"""
    global RID, META, WHO, PRODUCT, PREMIUM, NRID, SHORTP, VAL, HEAD
    S.ISSUES.clear(); GS.clear_cache()
    RID = pipeline.read_riders(design_pdf)
    META = BA.auto_meta(design_pdf)
    sex = META.get('sex') or ''
    # 나이는 설계서 본문에서 추정하지 않는다(만기·갱신 나이가 섞여 잘못 읽힘) — 넘겨받은 값만 쓴다
    WHO = '고객님 (%s%s)' % ({'F': '여', 'M': '남'}.get(sex, ''), (' · ' + age) if age else '')
    PRODUCT = re.sub(r'\s+', ' ', META.get('product', '') or '').replace('( ', '(').strip()
    PREMIUM = META.get('premium', '') or ''
    NRID = len(RID)
    SHORTP = (re.split(r'보장보험|건강보험|암보험', PRODUCT)[0].replace('(무) 메리츠 ', '').replace('(무)메리츠', '').strip() or PRODUCT).replace('%', '%%')
    HEAD = ga_head(design_pdf, age)
    VAL = {c['key']: GS.cell_value(c, RID) for c in GS.CELLS}
def who_line():
    """「민메리 (여자, 20세)」 — 읽은 것만"""
    inner = ', '.join(x for x in (HEAD.get('sex'), HEAD.get('age')) if x)
    return ((HEAD.get('name') or '') + ((' (%s)' % inner) if inner else '')).strip() or '-'
def head_bar():
    """1쪽 머리줄(GA 2026-10-22) : 상품명 · 피보험자(이름, 성별, 보험나이) · 월 보험료 · 가계약번호"""
    return ('<div class="hb"><span><em>상품명</em>%s</span><span><em>피보험자</em>%s</span><span><em>월 보험료</em>%s</span><span><em>가계약번호</em>%s</span></div>'
            % (PRODUCT or '-', who_line(), PREMIUM or '-', HEAD.get('no') or '-'))
def V(key): return VAL[key][0]
def L(key): return VAL[key][1]
def F(lines): return int(round(S.total_by(lines, 'first')))

def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
def asset_uri(name):
    """ga_assets 의 그림(표지 일러스트 · 로고)을 파일 주소로 — 없으면 None(그 자리는 CSS 로 그린다)"""
    import pathlib
    p = pathlib.Path(BASE, 'ga_assets', name)
    return p.as_uri() if p.exists() else None
COVER = int(os.environ.get('GA_COVER', '1') or 1)      # 표지 판 : 1 = 연한 붉은 도형(GA 가안 표지1) · 2 = 방패·하트 일러스트(표지2 · ga_assets/cover_art2.png 가 있으면 그 그림)

def M(v, big=False):
    """칸 값 표시 — 숫자(만원) · None(미가입) · '간병인 보내줌' · '면책'"""
    if v is None: return '<span class="na">미가입</span>'
    if isinstance(v, str): return '<span class="txt">%s</span>' % v if v == CARE.SEND else '<span class="na">%s</span>' % v
    return '<b class="v%s%s">%s<i>만원</i></b>' % (' z' if abs(v) < 1e-9 else '', ' big' if big else '', won(v))
def _ns(x): return re.sub(r'\s+', '', x or '')

# ───────── 조각 (GA 디자인 가안 2026-10-23 그대로) ─────────
NOTICE = '예시 금액은 이해를 돕기 위한 금액으로<br>실제보험금은 다르게 지급될 수 있음'
FOOT_L = '※ 예시 금액은 이해를 돕기 위한 최대 보장 금액으로 실제 보험금은 다르게 지급될 수 있습니다.'
def logo(cls=''):
    """「meritz 메리츠화재」 — 공식 로고 그림(ga_assets/logo_meritz.png)이 있으면 그것, 없으면 글자로"""
    u = asset_uri('logo_meritz.png')
    if u: return '<img class="logo %s" src="%s" alt="meritz 메리츠화재">' % (cls, u)
    return '<span class="logo %s"><b>meritz</b><span>메리츠화재</span></span>' % cls
def ph(title):
    """쪽 머리 : 로고 · 「스마트 제안서」 · 쪽 이름 · 오른쪽 주의 문구"""
    return ('<div class="ph">%s<span class="sp">스마트 제안서</span><span class="bar"></span><span class="ttl">%s</span>'
            '<span class="warn"><i>!</i>%s</span></div>' % (logo(), title, NOTICE))
def sec(bold, rest='', cls=''):
    """빨간 제목 탭 — 「암 보장」(암 굵게) · 「1. 암 검사 (연1회)」 처럼 번호·보조 글자는 rest 로"""
    return '<div class="sec %s"><span class="tab"><b>%s</b>%s</span></div>' % (cls, bold, (' ' + rest) if rest else '')
def foot():
    """쪽 아래 : 안내 문구 · 소속 · 코드 · 컨설턴트 (설계서에서 읽은 글자만 · 못 읽으면 「-」) · 계산 엔진 버전(사내 확인용 · 아주 작게)"""
    r = '<span>소속 : %s</span><span>코드 : %s</span><span>컨설턴트 : %s</span>' % (HEAD.get('org') or '-', HEAD.get('code') or '-', HEAD.get('agent_name') or '-')
    return '<div class="ft"><span class="fl">%s</span><span class="fr">%s<em>계산 %s · 담보 %d건</em></span></div>' % (FOOT_L, r, VERSION, NRID)
def info_table(cover=False):
    """상품명 · 피보험자 · (가계약 번호 | 월 보험료) 표 — 표지는 3줄(가계약 번호 포함), 1쪽은 2줄(설계번호는 표 위 오른쪽)"""
    prem = '<b class="prem">%s<i>원</i></b>' % PREMIUM.replace('원', '') if PREMIUM else '-'
    if cover:
        return ('<table class="info"><tr><th>상 품 명</th><td colspan="3" class="pn">%s</td></tr>'
                '<tr><th>피보험자</th><td>%s</td><th>가계약 번호</th><td>%s</td></tr>'
                '<tr><th>월 보험료</th><td colspan="3">%s</td></tr></table>' % (PRODUCT or '-', who_line(), HEAD.get('no') or '-', prem))
    return ('<div class="dno">설계번호 : %s</div><table class="info p1"><tr><th>상 품 명</th><td colspan="3" class="pn">%s</td></tr>'
            '<tr><th>피보험자</th><td>%s</td><th>월 보험료</th><td>%s</td></tr></table>' % (HEAD.get('no') or '-', PRODUCT or '-', who_line(), prem))
def kv(cols, red_first=False):
    """cols : (머리, [(표시이름, 칸 key), ...]) — 줄 i 마다 열을 가로지르며 그린다(ga_spec 칸 순서와 같다)"""
    n = max(len(r) for _, r in cols)
    th = ''.join('<th>%s</th>' % h for h, _ in cols)
    trs = ''
    for i in range(n):
        trs += '<tr>' + ''.join(('<td><span>%s</span>%s</td>' % (r[i][0], M(V(r[i][1])))) if i < len(r) else '<td class="e"></td>' for _, r in cols) + '</tr>'
    return '<table class="kv"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (th, trs)
def grid(head, rows, cls='g'):
    """첫 열 = 줄 이름(최초 지급시는 빨강) · 나머지 = 값"""
    th = ''.join('<th>%s</th>' % h for h in head)
    trs = ''
    for ri, r in enumerate(rows):
        cl = ' class="first"' if (ri == 0 and len(rows) > 1 and r[0] == '최초 지급시') else ''
        trs += '<tr%s>' % cl + ''.join(('<td class="lab">%s</td>' if i == 0 else '<td>%s</td>') % c for i, c in enumerate(r)) + '</tr>'
    return '<table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (cls, th, trs)

# ───────── 표지 ─────────
def p0():
    idx = ga_product_idx(PRODUCT)
    notice = ('<div class="cv-note"><i>!</i><div>본 제안서상 예시 금액은 이해를 돕기 위한 금액으로 실제 보험금이 다르게 지급될 수 있습니다.<br>'
              '자세한 사항은 해당 상품의 약관 및 보험증권을 꼭 참조하시기 바랍니다.<br>본 제안서의 설계번호와 체결된 계약의 번호가 다른 경우 보장 금액은 달라질 수 있습니다</div></div>')
    warn = '' if idx is not None else '<div class="cv-warn">탑재상품 목록(13개)에 없는 상품 — 그대로 계산했습니다</div>'
    if COVER == 2:
        u = asset_uri('cover_art2.png')
        art = '<img class="art2" src="%s">' % u if u else ('<div class="art2css"><div class="shield"><div class="heart"></div></div><div class="cross"><i></i><i></i></div>'
                                                             '<div class="doc"><i></i><i></i><i></i></div><div class="ball r1"></div><div class="ball r2"></div><div class="ball w1"></div><div class="ball w2"></div><div class="ball w3"></div></div>')
    else:
        u = asset_uri('cover_art1.png')
        art = '<img class="art1img" src="%s">' % u if u else ART1_SVG
    contact = ('<div class="cv-contact"><div><em>소　　속</em><b>%s</b></div><div><em>휴대전화</em><b>%s</b></div>'
               '<div><em>컨설턴트</em><b>%s</b></div><div><em>전화번호</em><b>%s</b></div></div>'
               % (HEAD.get('org') or '-', HEAD.get('mobile') or '-', (HEAD.get('agent_name') + '님') if HEAD.get('agent_name') else '-', HEAD.get('tel') or '-'))
    body = ('%s<div class="cv-tag">내 보험의 가치를 한눈에 보는</div><h1 class="cv-title">메리츠 <span>스마트 제안서</span></h1>%s%s%s%s%s'
            % (art, info_table(True), notice, warn, contact, logo('cv-logo')))
    return '<div class="page cover">%s</div>' % body

# 표지1 배경 도형 — GA 가안(표지1)의 연한 붉은 「M」 띠를 벡터로 옮긴 것. 원본 그림(ga_assets/cover_art1.png)이 오면 그 그림을 쓴다.
# 좌표는 가안 그림(1414×2000px)을 A4(210×297mm)에 맞춘 값. 띠는 둥근 모서리의 평행사변형 4개, 반투명 겹침(multiply)으로 겹치는 곳이 진해진다.
ART1_SVG = '''<svg class="art1" viewBox="0 0 1414 2000" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
<defs>
 <linearGradient id="gA" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#FFF1F0"/><stop offset=".55" stop-color="#FDD7D4"/><stop offset="1" stop-color="#F9B9B4"/></linearGradient>
 <linearGradient id="gB" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#FFEAE8"/><stop offset="1" stop-color="#F8B4AE"/></linearGradient>
 <linearGradient id="gC" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF4F3"/><stop offset="1" stop-color="#FBD0CC"/></linearGradient>
 <filter id="sf" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="2.5"/></filter>
</defs>
<!-- GA 가안 표지1 : 오른쪽 아래에 메리츠 「M」 모양의 연한 붉은 띠 4개(비스듬히 오른쪽 위로 올라감 · 둥근 모서리 · 반투명 겹침) -->
<g filter="url(#sf)" style="mix-blend-mode:multiply" opacity=".72">
 <!-- 오른쪽 위 세로 띠(M 의 오른 기둥 · 지면 밖으로 이어짐) -->
 <path d="M1232 605 Q1232 560 1278 560 L1500 560 L1500 1060 L1300 1060 Q1232 1060 1232 992 Z" fill="url(#gC)" opacity=".75"/>
 <!-- 큰 띠 : 왼쪽 아래(500,1480) → 오른쪽 위 -->
 <path d="M482 1446 Q452 1414 484 1384 L1226 760 Q1262 730 1292 762 L1500 980 L1500 1210 L740 1690 Q708 1716 680 1686 Z" fill="url(#gA)" opacity=".85"/>
 <!-- 아래 띠 : (820,1720) → 오른쪽 위 -->
 <path d="M814 1726 Q784 1696 814 1666 L1420 1150 L1500 1150 L1500 1420 L954 1890 Q922 1916 894 1886 Z" fill="url(#gB)" opacity=".8"/>
 <!-- M 가운데 사선(큰 띠에서 오른쪽 아래로 꺾여 내려오는 짧은 띠) -->
 <path d="M1040 1012 L1226 860 Q1258 836 1286 866 L1330 918 Q1356 950 1324 976 L1136 1130 Q1104 1156 1076 1126 L1030 1070 Q1008 1040 1040 1012 Z" fill="url(#gA)" opacity=".7"/>
</g>
</svg>'''

# ───────── 1쪽 보장요약 ─────────
LBL = {'표적(면역) 2가지 약물': '표적(면역)<br>2가지약물', '혈전용해+혈전제거': '<small>혈전용해+혈전제거</small>', '복강경/흉강경': '복강경, 흉강경', '개복/개흉': '개복, 개흉',
       'CRRT(지속적신대체요법)': 'CRRT<br><small>(지속적신대체요법)</small>'}   # 칸 이름 표시용(사양의 이름은 그대로)
EXL = {'특정단일유전자': '특정 단일유전자', '특정생검조직': '특정 생검조직', '특정NGS유전자': '특정 NGS유전자', '면역항암(카티포함)': '면역항암<small>(카티포함)</small>',
       'PET(양전자단층촬영)': 'PET<small>(양전자단층촬영)</small>', 'CRRT(지속적신대체요법)': 'CRRT<small>(지속적신대체요법)</small>'}
def dem_of(key):
    rs = L(key); return '<small class="dem">치매한정</small>' if rs and all(l.get('dementia') for l in rs) else ''
def p1():
    cancer = kv([(h, [(LBL.get(n, n), 'p1.ca.' + k) for n, k, *_ in items]) for h, items in GS._ca1])
    bh = kv([(h, [(LBL.get(n, n), 'p1.bh.' + k) for n, k, *_ in items]) for h, items in GS._bh1])
    def cell(n):
        side = '<small class="side">일측</small>' if n == '백내장' else ''
        return '<td><b>%s</b><em>%s</em><div class="val">%s%s</div></td>' % (n, GS.GA_DZ[n][0], side, M(V('p1.dz.' + n)))
    dz = '<table class="dz">%s</table>' % ''.join('<tr>%s</tr>' % ''.join(cell(n) for n in GS.DZ_ORDER[i:i + 4]) for i in range(0, len(GS.DZ_ORDER), 4))   # 12칸 4×3(GA 2026-10-22)
    def cv(k): return M(V(k)) + dem_of(k)
    care = ('<table class="care"><tr><th colspan="2">간병인지원입원일당<span>(현물지원)</span></th></tr>'
            '<tr><td>병원, 의원<small>(요양병원 제외)</small></td><td>%s</td></tr><tr><td>요양병원</td><td>%s</td></tr>'
            '<tr><td>간호간병통합서비스</td><td>%s</td></tr><tr><td>미사용시</td><td>%s</td></tr>'
            '<tr><th colspan="2">간병인사용입원일당<span>(금액지원)</span></th></tr>'
            '<tr><td>병원, 의원<small>(요양병원 제외)</small></td><td>%s</td></tr><tr><td>요양병원</td><td>%s</td></tr><tr><td>간호간병통합서비스</td><td>%s</td></tr></table>'
            % (cv('p1.care.hosp'), cv('p1.care.nh'), cv('p1.care.nurse'), cv('p1.care.unused'), cv('p1.care.use_gen'), cv('p1.care.use_nh'), cv('p1.care.use_nurse')))
    body = (ph('보장 요약') + info_table() + sec('암', '보장') + cancer + sec('뇌,심', '보장') + bh
            + '<div class="two"><div class="l">' + sec('주요수술', '보장') + dz + '</div><div class="r">' + sec('간병인', '보장') + care + '</div></div>')
    return '<div class="page">%s%s</div>' % (body, foot())

# ───────── 2쪽 암보장 ─────────
def p2():
    ex = '<table class="g eight"><tr>%s</tr><tr>%s</tr></table>' % (''.join('<th>%s</th>' % EXL.get(n, n) for n, _ in GS.EX_CA), ''.join('<td>%s</td>' % M(V('p2.ex.' + k)) for _, k in GS.EX_CA))
    dxb = ('<div class="dxbig"><div><span>일반암</span>%s<em>위, 대장, 폐, 간암 등</em></div>'
           '<div><span>유사암</span>%s<em>갑상선암, 기타피부암, 경계성종양, 제자리암</em></div>'
           '<div><span>전이암</span>%s<em>원발암에서 다른 부위로 전이</em></div></div>'
           % (M(V('p2.dx.일반암'), True), M(V('p2.dx.유사암'), True), M(V('p2.dx.전이암'), True)))
    sg = grid([''] + [n for n, _ in GS.SG], [[rl] + [M(V('p2.sg.%s.%s' % (k, md))) for _, k in GS.SG] for rl, md in GS.ROWS3])
    # 항암약물치료 : 화학 · 표적 · 면역 + 넷째 열 「표적(면역) 개수별」(2가지약물 / 3가지약물 — GA 가안)
    cm_rows = [[rl] + [M(V('p2.cm.%s.%s' % (k, md))) for _, k in GS.CM] for rl, md in GS.ROWS3[:2]]
    cm_rows[0].append('<small class="pre">2가지약물</small>' + M(V('p2.cm.two'))); cm_rows[1].append('<small class="pre">3가지약물</small>' + M(V('p2.cm.two3')))
    cm = grid([''] + [EXL.get(n, n) for n, _ in GS.CM] + ['표적(면역) 개수별'], cm_rows)
    rd = grid([''] + [n for n, _ in GS.RD], [[rl] + [M(V('p2.rd.%s.%s' % (k, md))) for _, k in GS.RD] for rl, md in GS.ROWS3[:2]])
    rh = grid(['', '입원 재활', '외래 재활'], [['연 20회', M(V('p2.rh.in')), M(V('p2.rh.out'))]])
    dis = grid(['3~100% 암후유장해'], [[M(V('p2.dis'))]], 'g one')
    body = (ph('암 보장') + sec('1. 암 검사', '<small>(연1회)</small>') + ex + sec('2. 암 진단') + dxb + sec('3. 암 수술') + sg
            + sec('4. 항암약물치료') + cm + sec('5. 항암방사선치료') + rd
            + '<div class="two"><div class="l"><div class="r2">' + sec('6. 암 재활치료') + rh + '</div></div><div class="r"><div class="r2">' + sec('7. 암 후유장해') + dis + '</div></div></div>')
    return '<div class="page roomy">%s%s</div>' % (body, foot())

# ───────── 3쪽 뇌·심보장 ─────────
def p3():
    ex = '<table class="g eight three"><tr>%s</tr><tr>%s</tr></table>' % (''.join('<th>%s</th>' % EXL.get(n, n) for n, _ in GS.EX_BH), ''.join('<td>%s</td>' % M(V('p3.ex.' + k)) for _, k in GS.EX_BH))
    sub = {'뇌혈관': '뇌출혈, 뇌경색, 뇌혈관, 뇌동맥류 등', '뇌졸중': '뇌출혈, 뇌경색 등', '허혈성심장': '급성심근경색, 협심증 등'}   # 문구 · 3칸 GA 2026-10-22
    dxb = '<div class="dxbig">%s</div>' % ''.join('<div><span>%s</span>%s<em>%s</em></div>' % (n, M(V('p3.dx.' + n), True), sub[n]) for n in ('뇌혈관', '뇌졸중', '허혈성심장'))
    bs, hs = GS.brain_steps('상급종합'), GS.heart_steps('상급종합')
    gb = grid([''] + [n for n, _ in bs], [[rl] + [M(V('p3.b%d.%s' % (i, md))) for i in range(4)] for rl, md in GS.ROWS3])
    gh = grid([''] + [n for n, _ in hs], [[rl] + [M(V('p3.h%d.%s' % (i, md))) for i in range(4)] for rl, md in GS.ROWS3])
    sev = grid([''] + [EXL.get(n, n) for n, _ in GS.SEV], [['반복(연1회)'] + [M(V('p3.sev.' + k)) for _, k in GS.SEV]], 'g sev')
    rh = grid(['', '입원 재활', '외래 재활'], [['연 15회', M(V('p3.rh.in')), M(V('p3.rh.out'))]])
    body = (ph('뇌,심 보장') + sec('1. 뇌, 심 검사', '<small>(연1회)</small>') + ex + sec('2. 뇌, 심 진단') + dxb + sec('3. 뇌질환 치료 및 수술') + gb
            + sec('4. 심질환 치료 및 수술') + gh + sec('5. 뇌,심 중증치료') + sev + sec('6. 뇌,심 재활치료') + rh)
    return '<div class="page roomy">%s%s</div>' % (body, foot())

# ───────── 보장금액 세부내역(보장요약 칸의 합산 계산서 · 맨 뒤 · 반드시 붙는다) ─────────
def _man_of(name):
    """지급 줄 이름과 같은 설계 담보의 가입금액(만원) — 못 찾으면 None"""
    for r in RID:
        if _ns(r['name']) == _ns(name) or _ns(r['name']).replace('치매주요질환입원일당', '질병입원일당') == _ns(name):
            return r['man'] if r['man'] or '간병인지원' not in r['name'] else CARE.daily(r)   # 간병인지원 「간병인지원 또는 N만원」 — 금액란 숫자(현물 담보는 가입금액 0 으로 읽힘)
    return None
def _wn(v):
    """계산서용 숫자 — 1쪽 값 표시(b.v)와 다른 표기를 써서 지면 대조(ga_spec)가 칸 수를 잘못 세지 않게 한다"""
    if v is None: return '<span class="cna">미가입</span>'
    return '<span class="cn">%s<i>만원</i></span>' % won(v) if not isinstance(v, str) else '<span class="cn txt">%s</span>' % v
def disp_name(name):
    """세부내역 특약명 — 26종 항암방사선및약물치료비의 꼬리 [세부급부명]은 뗀다(특정 암만 보장되는 듯한 오해 · GA 2026-10-22)"""
    n = re.sub(r'\s+', ' ', name).strip()
    if n.startswith('26종'): n = re.sub(r'\s*\[[^\[\]]*(\([^()]*\))*[^\[\]]*\]\s*$', '', n)
    return n
def line_note(l):
    """담보명 옆 연한 글자 — 몇 종(1-5종 · 1-7종 수술비) · 통합치료비/통합생활지원비는 어느 항목에서 나왔나(금액 숫자는 뺀다). 그 밖에는 적지 않는다(GA 2026-10-22)"""
    why = l.get('why') or ''; rule = l.get('rule') or ''
    if l.get('group') == '통합치료비' or rule in ('itc', 'ls_monthly'):
        items = [re.sub(r'\s*[\d,.]+\s*$', '', p).strip() for p in re.split(r'\s·\s', why.split('(연간 한도')[0])]
        return ', '.join(x for x in items if x)
    m = re.search(r'(\d)종', why) if rule.startswith('surg_grade') else None
    return m.group(0) if m else ''
def calc_row(c):
    """칸 하나 → (구분, 값, [(특약명, 메모, 가입금액, 지급액)]). 그 칸의 집계 방식으로 실제 합산된 줄만 적는다"""
    v, lines, _ = VAL[c['key']]
    if c['kind'] == 'engine':
        used = [(l, GS.counts(l, c['mode'])) for l in lines]; used = [(l, a) for l, a in used if a]
    else:
        used = [(l, l['amt']) for l in lines]
    lab = '[%s] %s' % (c['row'], c['col']) if c['row'] else c['col']
    lab = lab.replace('[진단금]', '[진단금]').replace('(현물지원)', '').replace('(금액지원)', '')
    rows = [(disp_name(l['name']), line_note(l), _man_of(l['name']), a) for l, a in used] if v is not None else []
    return (lab, v, rows)
def calc_table(title, rows):
    trs = ''
    for lab, v, rs in rows:
        n = max(1, len(rs))
        first = '<td class="lab" rowspan="%d">%s</td><td class="sum" rowspan="%d">%s</td>' % (n, lab, n, _wn(v))
        if not rs:
            trs += '<tr>%s<td class="nm"></td><td class="mn"></td><td class="am"></td></tr>' % first
            continue
        for i, (nm, note, man, amt) in enumerate(rs):
            trs += ('<tr>%s<td class="nm"><b>%s</b>%s</td><td class="mn">%s</td><td class="am">%s</td></tr>'
                    % (first if i == 0 else '', nm, (' <em>: %s</em>' % note) if note else '', (won(man) + '만원') if man is not None else '', won(amt) + '만원'))
    return sec(title) + ('<table class="calc"><thead><tr><th>구분</th><th>보장금액</th><th>특 약 명</th><th>가입금액</th><th>특약별 보장금액</th></tr></thead><tbody>%s</tbody></table>' % trs)
def calc_sections():
    """세부내역은 보장요약(1쪽) 칸만(GA 2026-10-22 · 암·뇌심 쪽까지 넣으면 중복이 많아진다)"""
    C = GS.KEY
    def keys(ks): return [calc_row(C[k]) for k in ks]
    ca = ['p1.ca.' + k for _, items in GS._ca1 for _, k, *_ in items]
    bh = ['p1.bh.' + k for _, items in GS._bh1 for _, k, *_ in items]
    dz = ['p1.dz.' + n for n in GS.DZ_ORDER]
    care = ['p1.care.' + k for k in ('hosp', 'nh', 'nurse', 'unused', 'use_gen', 'use_nh', 'use_nurse')]
    return [('암 보장 세부 내역', keys(ca)), ('뇌,심 보장 세부 내역', keys(bh)), ('주요수술 보장 세부 내역', keys(dz)), ('간병인 보장 세부 내역', keys(care))]

CALC_PAGES = 1      # 세부내역(합산 계산서) 최소 쪽수 — 반드시 붙는다(GA 확정 2026-10-02). 2026-10-22 부터 보장요약 칸만 적으므로 1쪽 이상(담보가 많으면 늘어난다)
CALC_BUDGET = 54    # 한 쪽에 들어가는 분량(단위 : 특약 한 줄 ≈ 4.3mm · 쪽 본문 약 245mm). 넘치면 render 의 '이탈·겹침' 경고로 잡힌다
_LINE_CH = 46       # 세부내역 특약명 칸 한 줄 글자 수(가정 · 7pt Pretendard · 칸 폭 약 88mm)
def calc_units(row):
    import math
    lab, v, rs = row
    n = 0.15
    if not rs: return n + 1
    for nm, note, man, amt in rs:
        n += max(1, math.ceil((len(nm) + (len(note) + 3 if note else 0)) / _LINE_CH))
    return n + 0.3 * max(0, math.ceil(len(lab) / 14) - 1)
def calc_paginate(sections):
    """구역(제목, 줄들)을 순서대로 쪽에 담는다 — 한 쪽 분량(CALC_BUDGET)을 넘으면 다음 쪽으로 넘기고 구역 제목에 (이어서)를 붙인다"""
    pages, cur, used = [], [], 0
    for title, rows in sections:
        i = 0
        while i < len(rows):
            if used + 4 + calc_units(rows[i]) > CALC_BUDGET and cur:
                pages.append(cur); cur, used = [], 0
            chunk, u = [], 4
            while i < len(rows) and used + u + calc_units(rows[i]) <= CALC_BUDGET:
                u += calc_units(rows[i]); chunk.append(rows[i]); i += 1
            if not chunk:                       # 줄 하나가 한 쪽을 넘는 경우 — 그대로 싣고 경고에 맡긴다
                chunk = [rows[i]]; u += calc_units(rows[i]); i += 1
            cont = (cur and cur[-1][0].split(' (이어서')[0] == title) or (not cur and pages and pages[-1][-1][0].split(' (이어서')[0] == title)
            cur.append((title + (' (이어서)' if cont else ''), chunk)); used += u
    if cur: pages.append(cur)
    out = []
    for n, pg in enumerate(pages):
        body = ph('보장금액 세부내역' + (' <small>%d/%d</small>' % (n + 1, len(pages)) if len(pages) > 1 else ''))
        body += ''.join(calc_table(t, rows) for t, rows in pg)
        out.append('<div class="page calcpg">%s%s</div>' % (body, foot()))
    return out

RED = '#F23A2B'
CSS = '''
@page{size:A4;margin:0} *{box-sizing:border-box} body{margin:0;font-family:"Pretendard","GANG","Malgun Gothic",sans-serif;color:#111;letter-spacing:-.2pt}
.page{width:210mm;height:297mm;padding:11mm 12mm 14mm 12mm;page-break-after:always;position:relative;overflow:hidden;background:#fff}
/* 쪽 머리 */
.ph{display:flex;align-items:center;gap:7pt;height:9mm;margin-bottom:5mm} .logo{display:inline-flex;align-items:baseline;gap:3pt;white-space:nowrap} .logo b{font-size:17pt;font-weight:800;color:RED;letter-spacing:-1.2pt;font-family:"Pretendard",Arial,sans-serif} .logo span{font-size:11.5pt;font-weight:700;color:#111}
img.logo{height:7.5mm} .ph .sp{font-size:15pt;font-weight:800;color:RED;margin-left:6pt;letter-spacing:-.6pt} .ph .bar{width:1px;height:14pt;background:#C9C9C9;margin:0 3pt}
.ph .ttl{font-size:15.5pt;font-weight:800;color:#111;letter-spacing:-.6pt} .ph .ttl small{font-size:9pt;font-weight:600;color:#777;margin-left:4pt}
.ph .warn{margin-left:auto;display:flex;gap:4pt;align-items:center;font-size:6.6pt;color:#666;line-height:1.3;text-align:left}
.ph .warn i,.cv-note i{display:inline-block;width:10pt;height:10pt;border-radius:50%;background:RED;color:#fff;font-style:normal;font-weight:900;font-size:7.5pt;text-align:center;line-height:10pt;flex:0 0 auto}
/* 정보표 */
.dno{text-align:right;font-size:7.5pt;color:#444;margin:0 0 2pt} .info{width:100%;border-collapse:collapse;border-top:1.5px solid RED;margin-bottom:4mm} .info th,.info td{height:9.5mm;border-bottom:1px solid #E6E6E6;padding:0 9pt;font-size:10.5pt;text-align:left;white-space:nowrap}
.info th{background:#F4F4F4;color:#555;font-weight:500;width:18%;letter-spacing:.3pt} .info td{font-weight:500} .info td b.prem{color:RED;font-size:14.5pt;font-weight:700} .info td b.prem i{font-style:normal;font-size:9pt;color:#111;font-weight:500;margin-left:1pt}
.info.p1 th,.info.p1 td{height:9mm;font-size:10pt} .info td.pn{white-space:normal;word-break:keep-all;line-height:1.2;font-size:9.6pt;padding-top:2pt;padding-bottom:2pt} .cover .info td.pn{font-size:10.5pt}
/* 제목 탭 */
.sec{border-bottom:2px solid #DADADA;margin:5.5mm 0 0;height:8.6mm;position:relative} .sec .tab{position:absolute;left:0;bottom:-2px;background:RED;color:#fff;border-radius:3.5pt 3.5pt 0 0;padding:0 11pt;height:8.6mm;line-height:8.6mm;font-size:12.5pt;font-weight:500;letter-spacing:-.4pt;white-space:nowrap}
.sec .tab b{font-weight:800} .sec .tab small{font-size:8.5pt;font-weight:500;margin-left:2pt} .roomy .sec{margin-top:7mm}
/* 표 공통 */
table{border-collapse:collapse;width:100%;table-layout:fixed} th,td{font-size:9.6pt;padding:0 6pt;height:8.3mm;border-bottom:1px solid #E6E6E6;white-space:nowrap;overflow:hidden}
th{background:#F4F4F4;font-weight:500;color:#444;text-align:center;height:8mm} td{text-align:center} .g th:first-child{background:#F4F4F4} .g th small{font-size:7pt;color:#777}
.lab{text-align:left;color:#333;white-space:nowrap;font-size:9.4pt;padding-left:12pt} tr.first .lab{color:RED} tr.first b.v{color:RED}
.g tbody b.v{color:#111} .g td small.pre{font-size:7.6pt;color:#555;margin-right:4pt;vertical-align:1pt}
.roomy th,.roomy td{height:9.6mm} .roomy .eight th{height:8.8mm} .roomy .eight td{height:9.6mm}
.kv th{height:8.6mm;font-size:10.5pt} .kv td{width:25%;text-align:left;border-right:1px solid #ECECEC;height:8.9mm;padding:0 7pt 0 9pt} .kv td:last-child{border-right:0} .kv td.e{border-right:0}
.kv td span{display:inline-block;max-width:58%;color:#222;font-size:9.6pt;white-space:normal;word-break:keep-all;line-height:1.1;vertical-align:middle;font-weight:500} .kv td span small{font-size:8.2pt;letter-spacing:-.5pt} .kv td b.v,.kv td .na,.kv td .txt{float:right;line-height:8.9mm}
b.v{font-weight:700;color:RED;font-size:12pt;white-space:nowrap;letter-spacing:-.4pt} b.v i{font-style:normal;font-weight:500;font-size:8.6pt;color:#111;margin-left:1pt;letter-spacing:0}
b.v.z{color:#9A9A9A} b.v.big{font-size:19pt} b.v.big i{font-size:10pt}
small{font-size:7.5pt;color:#777} .na{color:#C4C4C4;font-size:9.6pt;font-weight:500} .txt{font-weight:800;color:RED;font-size:10pt}
.two{display:flex;gap:5mm;align-items:flex-start} .two .l{flex:1} .two .r{width:40%} .r2 .sec{margin-top:5.5mm}
/* 주요수술 12칸 */
.dz td{text-align:center;vertical-align:top;border:1px solid #E6E6E6;width:25%;padding:7pt 3pt 6pt;height:auto;white-space:normal;background:#fff} .dz tr:nth-child(odd) td{background:#F7F7F7}
.dz td b{display:block;font-size:10.5pt;font-weight:600;color:#222} .dz td em{display:block;font-style:normal;color:#888;font-size:7.2pt;margin:1pt 0 7pt} .dz .val{height:8mm;line-height:8mm} .dz b.v{display:inline;color:#111;font-size:14pt} .dz small.side{font-size:6.8pt;color:#999;margin-right:3pt}
/* 간병인 */
.care th{text-align:left;background:#F4F4F4;height:8mm;font-size:9.6pt;color:#333;font-weight:500;padding-left:9pt} .care th span{color:#777;margin-left:1pt} .care td{text-align:left;height:7.6mm;font-size:9.4pt;padding-left:9pt;color:#222;font-weight:500} .care td:last-child{text-align:right;padding-right:6pt} .care td small{font-size:7.4pt;color:#888}
.care b.v{color:#111;font-size:10.5pt} .care small.dem{display:block;color:RED;font-weight:700;font-size:6.4pt;text-align:right;line-height:1}
/* 2·3쪽 */
.eight th{font-size:9pt;white-space:nowrap;height:8mm;padding:0 2pt;background:#F4F4F4} .eight th small{font-size:6pt;color:#777} .eight td{padding:0 2pt} .eight b.v{color:#111;font-size:11pt} .three th,.three td{width:33.3%}
.dxbig{display:flex;gap:4pt;margin-top:0} .dxbig div{flex:1;background:#FBF1F0;padding:7pt 11pt 6pt;min-height:19mm;position:relative}
.dxbig span{font-weight:600;font-size:13pt;color:#222} .dxbig em{font-style:normal;color:#666;font-size:7.6pt;display:block;margin-top:3pt} .dxbig b.v{position:absolute;right:11pt;top:6pt} .dxbig .na{position:absolute;right:11pt;top:8pt;font-size:11pt}
.g.one th{height:9.2mm} .g.sev th{font-size:9pt}
.ft{position:absolute;left:12mm;right:12mm;bottom:7mm;font-size:7pt;color:#555;border-top:1px solid #DADADA;padding-top:5pt;display:flex;justify-content:space-between;align-items:baseline}
.ft .fr span{margin-left:8pt;padding-left:8pt;border-left:1px solid #D0D0D0;font-weight:600;color:#333} .ft .fr span:first-child{border:0} .ft .fr em{font-style:normal;color:#BBB;font-size:5.5pt;margin-left:8pt}
/* 표지 */
.cover{padding:0} .cv-tag{position:absolute;left:12mm;top:35mm;font-size:19pt;font-weight:300;color:#222;letter-spacing:-.6pt} .cv-title{position:absolute;left:11mm;top:45mm;margin:0;font-size:50pt;font-weight:800;letter-spacing:-2.8pt;color:#111;white-space:nowrap} .cv-title span{color:RED}
.cover .info{position:absolute;left:12mm;top:74mm;width:186mm} .cover .info th,.cover .info td{height:12mm;font-size:11.5pt} .cover .info th{width:18%} .cover .info td b.prem{font-size:17pt}
.cv-note{position:absolute;left:12mm;top:115mm;display:flex;gap:6pt;align-items:flex-start;font-size:7.6pt;color:#555;line-height:1.45} .cv-note i{margin-top:2pt}
.cv-warn{position:absolute;left:12mm;top:132mm;color:RED;font-weight:700;font-size:8pt}
.cv-contact{position:absolute;left:12mm;bottom:17mm;display:grid;grid-template-columns:auto auto;gap:4pt 24pt;font-size:11pt} .cv-contact em{font-style:normal;color:#666;margin-right:10pt;letter-spacing:1pt;display:inline-block;min-width:38pt} .cv-contact b{font-weight:600;color:#111}
.logo.cv-logo{position:absolute;right:12mm;bottom:18mm} .logo.cv-logo b{font-size:27pt} .logo.cv-logo span{font-size:17pt;font-weight:700} img.logo.cv-logo{height:10mm}
/* 표지1 : 연한 붉은 도형(GA 가안을 CSS 로 옮긴 것) */
.art1{position:absolute;inset:0;overflow:hidden;z-index:0} .art1 .s{position:absolute;border-radius:16mm;background:linear-gradient(135deg,rgba(255,225,222,.55),rgba(255,150,140,.28));filter:blur(.3mm);mix-blend-mode:multiply}
.art1 .a{width:150mm;height:60mm;left:70mm;top:170mm;transform:rotate(-32deg)} .art1 .b{width:140mm;height:55mm;left:95mm;top:120mm;transform:rotate(-32deg);opacity:.8} .art1 .c{width:120mm;height:48mm;left:120mm;top:222mm;transform:rotate(-32deg);opacity:.7} .art1 .d{width:90mm;height:36mm;left:140mm;top:88mm;transform:rotate(-32deg);opacity:.55}
.cover>*:not(.art1):not(.art1img):not(.art2):not(.art2css){z-index:1} svg.art1{position:absolute;left:0;top:0;width:210mm;height:297mm;z-index:0;overflow:visible} img.art1img{position:absolute;left:0;top:0;width:210mm;height:297mm;z-index:0}
/* 표지2 : 방패·하트 일러스트 — 원본 그림(ga_assets/cover_art2.png)이 없으면 CSS 로 비슷하게 */
img.art2{position:absolute;left:55mm;top:130mm;width:140mm} .art2css{position:absolute;left:0;top:0;width:210mm;height:297mm;z-index:0}
.art2css .shield{position:absolute;left:100mm;top:150mm;width:72mm;height:84mm;background:linear-gradient(160deg,#fff,#EDEDED);border-radius:36mm 36mm 50% 50%/30mm 30mm 60% 60%;box-shadow:0 8mm 14mm rgba(0,0,0,.08),inset 0 -3mm 6mm rgba(0,0,0,.05);transform:rotate(-8deg)}
.art2css .heart{position:absolute;left:21mm;top:22mm;width:30mm;height:30mm;background:#F23A2B;transform:rotate(-45deg);border-radius:0 0 2mm 0;box-shadow:inset -3mm -3mm 6mm rgba(0,0,0,.12)} .art2css .heart:before,.art2css .heart:after{content:"";position:absolute;width:30mm;height:30mm;background:#F23A2B;border-radius:50%} .art2css .heart:before{left:-15mm;top:0} .art2css .heart:after{left:0;top:-15mm}
.art2css .cross{position:absolute;left:66mm;top:190mm;width:40mm;height:40mm;background:rgba(255,205,200,.6);border-radius:8mm;transform:rotate(-10deg)} .art2css .cross i{position:absolute;left:14mm;top:6mm;width:12mm;height:28mm;background:#F23A2B;border-radius:2mm} .art2css .cross i+i{transform:rotate(90deg)}
.art2css .doc{position:absolute;left:150mm;top:200mm;width:36mm;height:40mm;background:rgba(255,205,200,.6);border-radius:7mm;transform:rotate(8deg)} .art2css .doc i{position:absolute;left:8mm;width:20mm;height:3mm;background:#F8B8B2;border-radius:2mm} .art2css .doc i:nth-child(1){top:11mm} .art2css .doc i:nth-child(2){top:18mm} .art2css .doc i:nth-child(3){top:25mm;width:13mm}
.art2css .ball{position:absolute;border-radius:50%;box-shadow:inset -2mm -2mm 5mm rgba(0,0,0,.15),0 3mm 6mm rgba(0,0,0,.08)} .art2css .ball.r1{left:166mm;top:142mm;width:18mm;height:18mm;background:#F23A2B} .art2css .ball.r2{left:104mm;top:232mm;width:16mm;height:16mm;background:#F23A2B}
.art2css .ball.w1{left:80mm;top:176mm;width:10mm;height:10mm;background:#F3F3F3} .art2css .ball.w2{left:180mm;top:168mm;width:16mm;height:16mm;background:#F3F3F3} .art2css .ball.w3{left:138mm;top:240mm;width:14mm;height:14mm;background:#F3F3F3}
/* 세부내역 */
.calcpg .sec{margin-top:4.5mm;height:7.6mm} .calcpg .sec .tab{height:7.6mm;line-height:7.6mm;font-size:11.5pt;font-weight:800} .calcpg .sec .tab b{font-weight:800}
.calc th{font-size:8pt;height:7mm;padding:0 4pt;background:#F4F4F4;color:#444} .calc td{font-size:7.2pt;height:auto;padding:2.2pt 5pt;white-space:normal;vertical-align:middle;border-bottom:1px solid #E6E6E6;line-height:1.3}
.calc th:nth-child(1){width:20%} .calc th:nth-child(2){width:13.5%} .calc th:nth-child(3){width:44.5%} .calc th:nth-child(4){width:9%} .calc th:nth-child(5){width:13%}
.calc td.lab{text-align:left;font-size:8.4pt;font-weight:500;color:#222;padding-left:8pt;white-space:normal;word-break:keep-all;line-height:1.2} .calc td.sum{text-align:center;white-space:normal;word-break:keep-all;line-height:1.15;padding-left:2pt;padding-right:2pt} .calc .cn{font-weight:700;font-size:10pt;color:#111} .calc .cn i{font-style:normal;font-size:7pt;font-weight:500;margin-left:1pt} .calc .cna{color:#C4C4C4;font-size:8.6pt;font-weight:500}
.calc td.nm{text-align:left;color:#222} .calc td.nm b{font-weight:600} .calc td.nm em{font-style:normal;color:#999;font-size:6.8pt} .calc td.mn{text-align:right;color:#999;white-space:nowrap} .calc td.am{text-align:right;color:#222;font-weight:600;white-space:nowrap}
'''.replace('RED', RED)

def _font_css():
    """ga_assets 의 Pretendard(디자인 가안 글꼴 · OFL) 와 나눔고딕을 파일로 붙인다 — 없으면 PC 글꼴(맑은 고딕)로 나온다"""
    import pathlib
    css = ''
    a = pathlib.Path(BASE, 'ga_assets')
    for f, w in (('Pretendard-Regular.woff2', 400), ('Pretendard-Medium.woff2', 500), ('Pretendard-SemiBold.woff2', 600), ('Pretendard-Bold.woff2', 700), ('Pretendard-ExtraBold.woff2', 800)):
        if (a / f).exists():
            css += "@font-face{font-family:Pretendard;src:url('%s') format('woff2');font-weight:%d}" % ((a / f).as_uri(), w)
    if not (a / 'NanumGothic-Regular.ttf').exists(): a = pathlib.Path(BASE, 'assets')
    for f, w in (('NanumGothic-Regular.ttf', 400), ('NanumGothic-Bold.ttf', 700), ('NanumGothic-ExtraBold.ttf', 800)):
        if (a / f).exists():
            css += "@font-face{font-family:GANG;src:url('%s');font-weight:%d}" % ((a / f).as_uri(), w)
    return css

# ───────── 가안 합성 모드(2026-10-23 소유자 지시) : GA 디자인 가안 그림을 배경으로 깔고 값 글자만 얹는다 — ga_overlay ─────────
def _ov_cells(page):
    """그 쪽의 칸 값들을 사양 순서(ga_spec.CELLS)대로 얹는다 — 지면 대조(TOKEN_RE)가 칸 순서로 세므로 순서가 중요하다"""
    sp = OV.spec(page)['fields']; out = []
    for c in GS.CELLS:
        if c['page'] != {'p1': 1, 'p2': 2, 'p3': 3}[page]: continue
        if c['key'] not in sp: out.append('<!-- 자리 없음 %s -->' % c['key']); continue
        v = V(c['key']); f = OV.style_for(sp, c['key'], v)
        if isinstance(v, (int, float)): f = OV.fit(f, won(v), '만원')
        elif isinstance(v, str): f = OV.fit(f, v)
        out.append(OV.field_html(f, M(v), 'val'))
    return ''.join(out)
def _ov_text(sp, key, text, unit=None, shrink_over=None):
    f = sp.get(key)
    return OV.text_html(text, f, unit, shrink_over) if (f and text) else ''
def _ov_footer(sp, page='p1'):
    """꼬리 「소속 : ○ | 코드 : ○ | 컨설턴트 : ○」 — 가안의 그 블록을 지우고(ga_overlay.footer_box) 한 줄로 다시 쓴다(값이 길어도 겹치지 않게 · 셋째 이름표는 가안의 「소속」 오타 대신 「컨설턴트」)"""
    fb = OV.footer_box(page, sp)
    if not fb: return ''
    f0 = sp.get('ft.org') or {}
    f = dict(box=fb, align='right', font_px=f0.get('font_px', 19), weight=500, color=f0.get('color', '#111111'))
    sep = '<i style="display:inline-block;width:1px;height:.9em;background:#C9C9C9;margin:0 10px;vertical-align:-1px"></i>'
    inner = ('<span style="font-weight:500;color:#333">소속 : </span><b style="font-weight:700">%s</b>%s<span style="font-weight:500;color:#333">코드 : </span><b style="font-weight:700">%s</b>%s<span style="font-weight:500;color:#333">컨설턴트 : </span><b style="font-weight:700">%s</b>'
             % (HEAD.get('org') or '-', sep, HEAD.get('code') or '-', sep, HEAD.get('agent_name') or '-'))
    txt = '소속 : %s  코드 : %s  컨설턴트 : %s' % (HEAD.get('org') or '-', HEAD.get('code') or '-', HEAD.get('agent_name') or '-')
    return OV.field_html(OV.fit(f, txt + '      '), inner)
def p0_mock():
    page = 'cover2' if COVER == 2 else 'cover1'
    sp = OV.spec(page)['fields']
    prem = (PREMIUM or '').replace('원', '')
    body = (_ov_text(sp, 'cv.product', PRODUCT or '-', shrink_over=44) + _ov_text(sp, 'cv.insured', who_line()) + _ov_text(sp, 'cv.contract_no', HEAD.get('no') or '-')
            + _ov_text(sp, 'cv.premium', prem or '-', '원' if prem else None) + _ov_text(sp, 'cv.org', HEAD.get('org') or '-')
            + _ov_text(sp, 'cv.consultant', (HEAD.get('agent_name') + '님') if HEAD.get('agent_name') else '-') + _ov_text(sp, 'cv.mobile', HEAD.get('mobile') or '-') + _ov_text(sp, 'cv.tel', HEAD.get('tel') or '-'))
    return OV.page_open(page, 'cover') + body + '</div>'
def p1_mock():
    sp = OV.spec('p1')['fields']; prem = (PREMIUM or '').replace('원', '')
    body = (_ov_text(sp, 'hdr.dno', '설계번호 : ' + (HEAD.get('no') or '-')) + _ov_text(sp, 'hdr.product', PRODUCT or '-', shrink_over=52) + _ov_text(sp, 'hdr.insured', who_line())
            + _ov_text(sp, 'hdr.premium', prem or '-', '원' if prem else None) + _ov_cells('p1') + _ov_footer(sp))
    return OV.page_open('p1') + body + '</div>'
def p2_mock():
    sp = OV.spec('p2')['fields']; return OV.page_open('p2', 'roomy') + _ov_cells('p2') + _ov_footer(sp, 'p2') + '</div>'
def p3_mock():
    sp = OV.spec('p3')['fields']; return OV.page_open('p3', 'roomy') + _ov_cells('p3') + _ov_footer(sp, 'p3') + '</div>'
P4_BAND = (160, 1838)     # 가안 세부내역 쪽에서 머리 아래 ~ 꼬리 줄 위(px · 꼬리 글자는 1864~1904) — 이 사이를 지우고 HTML 표를 그린다
def calc_mock_pages():
    pages = calc_paginate(calc_sections())      # 기존 쪽 나눔(class="page calcpg")을 그대로 쓰되 배경·머리·꼬리만 가안으로
    sp = OV.spec('p1')['fields']                # 꼬리 자리는 1쪽과 같다
    import pathlib
    sp4 = dict(sp); 
    tpl = OV.template('p4', extra_erase=[[0, P4_BAND[0], OV.W, P4_BAND[1]]] + ([OV.footer_box('p4', sp)] if OV.footer_box('p4', sp) else []))
    out = []
    for i, pg in enumerate(pages):
        body = pg[pg.index('<div class="sec'):pg.rindex('<div class="ft">')]
        out.append('<div class="page calcpg mockpg" style="background-image:url(\'%s\')"><div class="calcbody">%s</div>%s%s</div>'
                   % (pathlib.Path(tpl).as_uri(), body, _ov_footer(sp, 'p4'), ('<div class="ov r pno" style="left:150mm;top:%.2fmm;width:48mm;height:6mm;font-size:8pt;color:#777">%d / %d</div>' % (118 * OV.MM_Y, i + 1, len(pages))) if len(pages) > 1 else ''))
    return out
MOCK_MODE = OV.available() and os.environ.get('GA_MOCK', '1') != '0'     # 가안 그림·측정 좌표가 있으면 합성 모드(GA_MOCK=0 이면 전부 HTML 로 그리는 예전 방식)

def html(design_pdf, age=''):
    load(design_pdf, age)
    return html_loaded()
def html_loaded():
    """load() 가 끝난 상태에서 지면 HTML 만 만든다(설계서 없이 담보 목록을 직접 넣어 보는 점검용으로도 쓴다)"""
    calc = calc_paginate(calc_sections())
    # 세부내역(계산서)은 선택이 아니다 — 못 만들면 지면 전체를 내지 않는다(금액의 근거가 빠진 제안서가 나가지 않게)
    if len(calc) < CALC_PAGES or any('class="page calcpg"' not in c for c in calc):
        raise RuntimeError('보장금액 세부내역(합산 계산서)이 %d쪽 이상 만들어지지 않았습니다(%d쪽)' % (CALC_PAGES, len(calc)))
    if MOCK_MODE:
        calc = calc_mock_pages()
        pages = [p0_mock(), p1_mock(), p2_mock(), p3_mock()] + calc
        return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s%s</style></head><body>%s</body></html>' % (_font_css(), CSS, OV.page_css() + MOCK_CSS, ''.join(pages))
    pages = [p0(), p1(), p2(), p3()] + calc
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>' % (_font_css(), CSS, ''.join(pages))
MOCK_CSS = ('.mockpg{padding:0} .ov b.v{font-size:inherit;color:inherit;font-weight:inherit;letter-spacing:-.4pt} .ov b.v i{font-size:var(--u);color:var(--uc);font-weight:500;margin-left:1px}'
            '.ov .na{color:var(--na,#C4C4C4);font-weight:500;font-size:var(--naf,inherit)} .ov .txt{color:#F23A2B;font-weight:800;font-size:inherit} .ov b.v.z{color:#9A9A9A}'
            '.calcpg.mockpg .calcbody{position:absolute;left:12mm;top:%.2fmm;width:186mm} .calcpg.mockpg .calcbody .sec:first-child{margin-top:0}' % (P4_BAND[0] * OV.MM_Y + 2))
FIXED_PAGES = 4     # 표지 · 보장요약 · 암보장 · 뇌·심보장 (그 뒤에 세부내역 CALC_PAGES 쪽 이상)

CHECK = """()=>{const o=[];document.querySelectorAll('.page').forEach((p,i)=>{const B=p.getBoundingClientRect();const ft=p.querySelector('.ft');const F=ft?ft.getBoundingClientRect():null;
 p.querySelectorAll('*').forEach(e=>{if(e.closest('.art1,.art1img,.art2css'))return; const r=e.getBoundingClientRect(); if(!r.width||!r.height)return;
  if(r.bottom>B.bottom+0.5||r.right>B.right+0.5) o.push('p'+(i+1)+' 이탈 '+(e.innerText||'').slice(0,20));
  else if(F&&!ft.contains(e)&&e!==ft&&!e.querySelector('.ft')&&r.bottom>F.top-1&&r.top<F.top) o.push('p'+(i+1)+' 겹침(하단 주석) '+(e.innerText||'').slice(0,20));});});
 return o.slice(0,20);}"""

def render(html_path, pdf_path):
    import pathlib
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        exe = os.environ.get('GA_CHROMIUM') or ('/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') and not os.path.isdir('/opt/pw-browsers/chromium') else None)
        b = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()      # 미리 깔린 크로뮴이 있으면 그것(세션 환경) · 없으면 playwright 기본
        pg = b.new_page(viewport={'width': 794, 'height': 1123})
        pg.goto(pathlib.Path(html_path).resolve().as_uri()); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        warn = pg.evaluate(CHECK)
        pg.pdf(path=pdf_path, prefer_css_page_size=True, print_background=True); b.close()
    return warn

def ascii_name(path):
    """산출물 파일명은 ASCII(CLAUDE.md 7) — 한글 파일명은 영문·숫자만 남기고, 없으면 design"""
    stem = os.path.splitext(os.path.basename(path))[0]
    a = re.sub(r'[^A-Za-z0-9_-]+', '_', stem).strip('_')
    if not re.search(r'[A-Za-z]', a):            # 한글 이름 → design_숫자 (원래 이름은 로그 첫 줄에 남는다)
        a = 'design' + ('_' + a if a else '')
    return a

def build(design_pdf, out_pdf=None, age='', keep_html=False):
    """설계서 한 건 → GA 제안서 PDF. 반환 (결과 PDF, 로그 파일, 레이아웃 경고)"""
    t0 = time.time()
    out_pdf = out_pdf or os.path.join(os.path.dirname(os.path.abspath(design_pdf)), 'ga_output', ascii_name(design_pdf) + '_GA.pdf')
    os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)
    h = html(design_pdf, age)
    hp = os.path.splitext(out_pdf)[0] + '.html'
    open(hp, 'w', encoding='utf-8').write(h)
    warn = render(hp, out_pdf)
    if not keep_html: os.remove(hp)
    rc = S.recog(RID)
    global AUDIT
    lg = [dict(구분=it['구분'], 담보=it['담보'], 사유=it['사유'], 담보목록=it.get('담보목록', [it['담보']])) for it in S.issues_grouped()]
    lg += [dict(구분='지면넘침', 담보='-', 사유=w, 담보목록=[]) for w in warn]
    AUDIT = {'요약': {'담보수': NRID, '마스터매칭': sum(1 for r in RID if r.get('matched')), '인식': {k: v for k, v in rc.items() if not k.endswith('목록')},
                    '계산제외목록': rc['계산제외목록'], '구조별': S.audit(RID)['구조별'], '생성쪽수': FIXED_PAGES + len(re.findall(r'class="page calcpg"', h)), '지면검사': warn,
                    '상품': PRODUCT, '보험료': PREMIUM, '계산엔진': VERSION, '처리시간': round(time.time() - t0, 1)},
             '로그': lg}
    log = os.path.splitext(out_pdf)[0] + '_log.txt'
    with open(log, 'w', encoding='utf-8') as f:
        f.write('원본 설계서 : %s\n상품 : %s\n보험료 : %s\n담보 %d건 · 인식 : 마스터 %d · 부모연결 %d · 규칙만 %d · 계산제외 %d\n계산 엔진 %s · %.1f초\n\n'
                % (os.path.basename(design_pdf), PRODUCT, PREMIUM, NRID, rc['마스터'], rc['부모연결'], rc['규칙만'], rc['계산제외'], VERSION, time.time() - t0))
        if rc['계산제외목록']: f.write('[계산제외 담보] ' + ' · '.join(rc['계산제외목록']) + '\n\n')
        f.write('[지면 경고] ' + (' / '.join(warn) if warn else '없음') + '\n\n[계산 로그 — 빈칸·0원의 이유]\n')
        for it in S.issues_grouped():
            f.write('- [%s] %s — %s\n' % (it['구분'], it['담보'], it['사유']))
    return out_pdf, log, warn

def main(argv):
    args = [a for a in argv if a.strip()]
    age = ''
    if args and re.fullmatch(r'\d{1,3}세?', args[-1]):
        age = args.pop(); age = age if age.endswith('세') else age + '세'
    if not args:
        args = [os.path.join(BASE, 'ga_input')]
    files = []
    for a in args:
        if os.path.isdir(a): files += sorted(glob.glob(os.path.join(a, '*.pdf')) + glob.glob(os.path.join(a, '*.PDF')))
        elif a.lower().endswith('.pdf'): files.append(a)
    out_pdf = None
    if len(args) == 2 and args[0].lower().endswith('.pdf') and args[1].lower().endswith('.pdf') and not os.path.exists(args[1]):
        files, out_pdf = [args[0]], args[1]
    if not files:
        print('설계서 PDF 가 없습니다. PDF 를 끌어다 놓거나 ga_input 폴더에 넣어 주세요.'); return 1
    ok = 0
    for i, f in enumerate(files, 1):
        print('[%d/%d] %s' % (i, len(files), os.path.basename(f)), flush=True)
        try:
            o = out_pdf or os.path.join(BASE, 'ga_output', ascii_name(f) + '_GA.pdf')
            if not out_pdf and os.path.exists(o):
                o = os.path.join(BASE, 'ga_output', '%s_GA_%s.pdf' % (ascii_name(f), time.strftime('%H%M%S')))
            pdf, log, warn = build(f, o, age)
            print('      → %s  (담보 %d건 · %s)%s' % (pdf, NRID, SHORTP.replace('%%', '%'), ('  ※ 지면 경고 %d건 — 로그 확인' % len(warn)) if warn else ''), flush=True)
            ok += 1
        except Exception as ex:
            print('      ! 만들지 못했습니다 : %s: %s' % (type(ex).__name__, ex), flush=True)
    print('\n완료 %d / %d건 · 결과 폴더 : %s' % (ok, len(files), os.path.join(BASE, 'ga_output') if not out_pdf else os.path.dirname(os.path.abspath(out_pdf))))
    return 0 if ok == len(files) else 2

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
