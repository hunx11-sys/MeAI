# -*- coding: utf-8 -*-
"""메리츠 GA 스마트 제안서 v2(새 양식 · 2026-11-11 회의 반영) — 설계서 PDF 를 넣으면 새 양식 PDF 를 만든다.

  python ga_v2.py 설계서.pdf [결과.pdf] [나이]      # 한 건
  python ga_v2.py 폴더                             # 폴더 안 PDF 전부 → ga_output\\<이름>_GA2.pdf
  (GA_MASK=1 이면 피보험자 · 가계약번호 · 소속 · 컨설턴트 · 전화를 가린다 — 견본 · 사외 공유용)

쪽 구성(고객에게 넘겨 보여 주는 순서)
  표지 · 보장요약(지금 GA 양식 그대로 · ga_proposal) → 치료 여정 → 암 보장 ① ② · 뇌혈관 · 심장(v41 디자인 틀 + 값)
  → 주요수술 ① ②(수술 12개 · 모든 병원 / 상급종합 · 미가입 · 1-5종 체증형) → 간병인(가입에 따라 아래 규칙) → 보장 점검
  → 보장금액 세부내역(글씨 키움 · 쪽수 자동) → 안내사항(v41 틀)

간병인 쪽 고르는 규칙(소유자 2026-11-11)
  간병인지원(현물) 담보가 있으면 「간병인 지원 가입자」 쪽 · 간병인사용(금액) 담보가 있으면 「간병인 사용 가입자」 쪽(둘 다 있으면 두 쪽)
  · 둘 다 없으면 지원 + 사용을 한 쪽에 같이 보여 주는 「간병인 보장」 쪽(니즈 환기) 하나.

금액은 전부 ga_spec(= 계산 엔진 scen_engine.pay_lines)의 칸 값 그대로다 — 이 파일은 값을 계산하지 않고 그리기만 한다(CLAUDE.md 1 · 2).
여기서 새로 더하는 것은 표시용 합(보상 예시 합계 · 재활 연 횟수 × 회당 금액 · 수술 카드 합계)뿐이고, 수술 카드 합계는 보장요약 칸 값과 같아야 한다(다르면 멈춘다).
"""
import os, sys, re, json, base64, copy, math, time, glob, atexit, pathlib, subprocess
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import fitz
import ga_proposal as GP, ga_spec as GS, ga_care as CARE, scen_engine as S, ga_overlay as OV

V2 = os.path.join(BASE, 'ga_assets', 'v2')
TPL, SLOTS, ICONS = os.path.join(V2, 'tpl.pdf'), os.path.join(V2, 'slots.json'), os.path.join(V2, 'icons')
TMP = os.path.join(BASE, 'out', 'v2tmp')
won = CARE.won
SEND = CARE.SEND

# ═══════════════ 글꼴 · 그리기 ═══════════════
def _b64(p): return base64.b64encode(open(p, 'rb').read()).decode()
_FONTS = None
def fonts_css():
    global _FONTS
    if _FONTS is None:
        _FONTS = ''.join("@font-face{font-family:P;font-weight:%d;src:url(data:font/woff2;base64,%s)}" % (w, _b64(os.path.join(BASE, 'ga_assets', 'Pretendard-%s.woff2' % n)))
                         for w, n in ((400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold')))
    return _FONTS
_PW = {}
def _page():
    """크로뮴 하나를 띄워 두고 계속 쓴다(설계서 여러 건을 돌릴 때 빠르게)"""
    if 'pg' not in _PW:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        exe = os.environ.get('GA_CHROMIUM') or ('/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') and not os.path.isdir('/opt/pw-browsers/chromium') else None)
        b = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        _PW.update(pw=pw, b=b, pg=b.new_page(viewport={'width': 794, 'height': 1123}))
        atexit.register(lambda: (_PW['b'].close(), _PW['pw'].stop()))
    return _PW['pg']
def _goto(html, name):
    os.makedirs(TMP, exist_ok=True)
    hp = os.path.join(TMP, name + '.html'); open(hp, 'w', encoding='utf-8').write(html)
    pg = _page(); pg.emulate_media(media='print'); pg.goto(pathlib.Path(hp).resolve().as_uri(), wait_until='load'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(120)
    return pg
def render_snippet(html, out_pdf, w_pt, h_pt):
    """정해진 크기(pt)의 조각 한 장 — 5열 표 · 니즈 상자 · 덧붙임 상자"""
    pg = _goto(html, 'snip')
    pg.pdf(path=out_pdf, width='%spx' % (w_pt * 4 / 3), height='%spx' % (h_pt * 4 / 3), print_background=True, prefer_css_page_size=True)
    assert len(fitz.open(out_pdf)) == 1, '조각이 두 쪽으로 넘어감 : ' + out_pdf
    return out_pdf
FIT_JS = """(gap)=>{const out=[];document.querySelectorAll('.page').forEach((pg,i)=>{
  const c=pg.querySelector('.cnt'), ft=pg.querySelector('.ft'); if(!c||!ft){out.push([i+1,1,0,0]);return}
  const W=pg.clientWidth-parseFloat(getComputedStyle(pg).paddingLeft)-parseFloat(getComputedStyle(pg).paddingRight);
  const top=c.getBoundingClientRect().top, avail=ft.getBoundingClientRect().top-top-gap;
  const fits=z=>{c.style.zoom=z;c.style.width=(W/z)+'px';let wide=false;c.querySelectorAll('table,.cards,.g2,.g4,.need,.cmp,.step,.steps,.sv,.tiles,.tile .a,.fp,.more').forEach(t=>{if(t.scrollWidth>t.clientWidth+1||t.getBoundingClientRect().right>c.getBoundingClientRect().right+1)wide=true});return !wide&&c.getBoundingClientRect().height<=avail};
  let lo=1,hi=1.6; if(!fits(1)){lo=0.7;hi=1} for(let k=0;k<14;k++){const m=(lo+hi)/2; if(fits(m))lo=m; else hi=m}
  fits(lo); out.push([i+1,+lo.toFixed(3),Math.round(c.getBoundingClientRect().height),Math.round(avail)])});return out}"""
def render_pages(html, out_pdf, name='pages'):
    """A4 쪽들(.page) — 쪽마다 본문(.cnt)을 머리 아래 ~ 바닥글 위 빈 곳에 꽉 차게(최대 1.6배, 넘치면 0.7배까지 줄임)"""
    pg = _goto(html, name)
    fit = pg.evaluate(FIT_JS, 18)
    pg.pdf(path=out_pdf, format='A4', print_background=True, prefer_css_page_size=True)
    over = [f for f in fit if f[3] and f[2] > f[3] + 1]
    return fit, over
def shrink_images(d, dpi=300):
    """그림마다(같은 그림은 한 번만) 실제 찍히는 크기 기준 300dpi 를 넘으면 2배씩 줄인다 — 투명도 유지 · 무손실(같은 그림을 쪽마다 거듭 줄이지 않게 xref 로 한 번만)"""
    seen, n = set(), 0
    for pg in d:
        for im in pg.get_images(full=True):
            xref, smask, w = im[0], im[1], im[2]
            if xref in seen: continue
            seen.add(xref)
            rects = [r for q in d for r in q.get_image_rects(xref)]
            if not rects: continue
            need = max(r.width for r in rects) / 72 * dpi; k = 0
            while w / (2 ** (k + 1)) >= need and k < 4: k += 1
            if not k: continue
            pix = fitz.Pixmap(d, xref)
            if smask: pix = fitz.Pixmap(pix, fitz.Pixmap(d, smask))
            if pix.n - pix.alpha > 3: pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.shrink(k); pg.replace_image(xref, pixmap=pix); n += 1
    return n
def dedupe_images(d):
    """같은 그림(픽셀 · 투명도 같음)이 여러 번 들어가 있으면(틀 쪽마다 로고 · 아이콘 사본) 첫 그림 하나만 가리키게 고친다 — 남는 사본은 저장(garbage)할 때 빠진다"""
    import hashlib
    seen, mp = {}, {}
    for x in range(1, d.xref_length()):
        if d.xref_get_key(x, 'Subtype')[1] != '/Image': continue
        try: pix = fitz.Pixmap(d, x)
        except Exception: continue
        sm = d.xref_get_key(x, 'SMask'); smh = ''
        if sm[0] == 'xref':
            try: smh = hashlib.md5(fitz.Pixmap(d, int(sm[1].split()[0])).samples).hexdigest()
            except Exception: continue
        h = hashlib.md5(pix.samples + repr((pix.width, pix.height, pix.n, re.sub(r'\d+ 0 R', 'R', d.xref_get_key(x, 'ColorSpace')[1]))).encode()).hexdigest() + smh
        if h in seen: mp[x] = seen[h]
        else: seen[h] = x
    if not mp: return 0
    ref = re.compile(r'/([^\s/<>\[\]()]+)\s+(\d+) 0 R')
    for x in range(1, d.xref_length()):
        for path in ('Resources/XObject', 'XObject'):
            t, v = d.xref_get_key(x, path)
            if t == 'xref':
                y = int(v.split()[0])
                for nm, r in ref.findall(d.xref_object(y, compressed=True)):
                    if int(r) in mp: d.xref_set_key(y, nm, '%d 0 R' % mp[int(r)])
            elif t == 'dict':
                for nm, r in ref.findall(v):
                    if int(r) in mp: d.xref_set_key(x, path + '/' + nm, '%d 0 R' % mp[int(r)])
    return len(mp)
def jpeg_big(d, q=88):
    """표지 · 보장요약 배경(GA 가안 그림 · 1414px)처럼 큰 불투명 그림은 JPEG 로 다시 담는다(무손실 압축으로 들어와 1장 0.4MB) — 크기만 줄고 모양은 같다"""
    done = set()
    for pg in d:
        for im in pg.get_images(full=True):
            x, smask, w = im[0], im[1], im[2]
            if x in done or smask or w < 1000 or d.xref_get_key(x, 'Filter')[1] == '/DCTDecode': continue
            done.add(x); pix = fitz.Pixmap(d, x)
            if pix.alpha or pix.n - pix.alpha != 3: continue
            pg.replace_image(x, stream=pix.tobytes('jpeg', jpg_quality=q))
    return len(done)
_ICO = {}
def ico(key, px=30):
    if key not in _ICO: _ICO[key] = _b64(os.path.join(ICONS, key + '.png'))
    return '<img src="data:image/png;base64,%s" style="width:%dpx;height:%dpx">' % (_ICO[key], px, px)

# ═══════════════ 틀(v41)에 굳힌 조각 — ga_v2_template.py 가 쓴다 ═══════════════
NEED_HEART_H = 114.0
NEED_HEART_HTML = ('<!doctype html><html><head><meta charset="utf-8"><style>%(F)s'
    '@page{size:532.5pt 114pt;margin:0}*{box-sizing:border-box}html,body{margin:0;width:532.5pt;height:114pt;overflow:hidden;font-family:P;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all}'
    '.t{display:flex;align-items:baseline;gap:9pt;height:22pt;padding-top:3pt;border-bottom:.8pt solid #BDBDC3}.t b{font-size:12.5pt;color:#1F1F22;font-weight:700}.t span{font-size:7.6pt;color:#666}'
    '.pn{margin-top:7.5pt;height:70pt;background:#F7F7F8;border:.8pt solid #E6E6EA;border-radius:8pt;display:grid;grid-template-columns:1.25fr 1fr 1fr;align-items:center;padding:0 12pt;gap:10pt}'
    '.bar{display:grid;grid-template-columns:30pt 1fr;row-gap:5pt;align-items:center;font-size:7.6pt;color:#444}'
    '.bar i{display:block;height:11pt;border-radius:2pt;background:#9FB0CF}.bar i.r{background:#2A3A54}.bar em{font-style:normal;font-size:8.3pt;font-weight:700;color:#1F1F22;margin-left:4pt;white-space:nowrap}'
    '.st{text-align:center;border-left:.8pt dashed #D0D0D6;padding-left:8pt}.st .k{font-size:7.6pt;color:#555}.st .v{font-size:19pt;font-weight:800;color:#E5432F;line-height:1.15}'
    '.st .v small{font-size:10pt}.st .s{font-size:6.9pt;color:#777}.src{font-size:5.9pt;color:#9A9AA2;margin-top:4.5pt}</style></head><body>'
    '<div class="t"><b>다시 찾아오는 심근경색</b><span>한 번의 시술로 끝나지 않는 경우가 많습니다 · 발병 후 1년 이내, 특히 3개월 안에 재발 위험이 높습니다</span></div>'
    '<div class="pn"><div><div style="font-size:7.6pt;color:#555;margin-bottom:4pt">재발 심근경색 발생 건수</div><div class="bar">'
    '<span>2013년</span><span style="display:flex;align-items:center"><i style="width:57.7pt"></i><em>1,768건</em></span>'
    '<span>2023년</span><span style="display:flex;align-items:center"><i class="r" style="width:110pt"></i><em>3,373건</em></span></div></div>'
    '<div class="st"><div class="k">재발 심근경색 10년 새</div><div class="v">+90.8<small>%%</small></div><div class="s">첫 발생 증가율(36.4%%)의 약 2.5배</div></div>'
    '<div class="st"><div class="k">발병 후 1년 안에 사망</div><div class="v">16.1<small>%%</small></div><div class="s">약 6명 중 1명 · 30일 안에는 8.9%%</div></div></div>'
    '<div class="src">[출처: 질병관리청 「2023 심뇌혈관질환 발생통계」(2025.12.31 발표 · 건강보험 청구 · 사망원인 자료) · 대한심혈관중재학회 회복 · 관리 가이드북 배포 보도(2026.11.10)]</div>'
    '</body></html>')
assert round((3373 / 1768 - 1) * 100, 1) == 90.8 and round(110 * 1768 / 3373, 1) == 57.7      # 막대 길이 = 건수 비율
NOTICE_ADD_H = 112.0
NOTICE_ADD_HTML = ('<!doctype html><html><head><meta charset="utf-8"><style>%(F)s'
    '@page{size:532.5pt 112pt;margin:0}*{box-sizing:border-box}html,body{margin:0;width:532.5pt;height:112pt;overflow:hidden;font-family:P;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all}'
    '.b{border:.8pt solid #E3E3E8;border-radius:7pt;background:#FAFAFB;padding:8pt 11pt}.b b{display:block;font-size:8.6pt;color:#1F1F22;margin:0 0 2.5pt}.b p{margin:0 0 6pt;font-size:7.3pt;line-height:1.5;color:#55555C}.b p:last-child{margin:0}'
    '</style></head><body><div class="b"><b>이번 제안서에 더한 쪽 안내</b><p>「치료 여정」 · 「보장 점검」 · 각 쪽 「보장(보상) 예시」 · 「사례로 보는 간병비 보장」 · 수술 · 간병 시나리오는 이 설계의 보장금액을 단순 합산하거나 '
    '입원일수 · 평균 간병비를 가정한 예시로, 실제 진단 · 치료 내용과 약관상 지급조건에 따라 지급 여부와 금액이 달라집니다. 일부 특약은 가입 후 1년 안에 가입금액의 50%%를 지급합니다.</p>'
    '<b>추가 출처</b><p>질병관리청 「2023 심뇌혈관질환 발생통계」(2025.12.31) — 재발 심근경색 발생 건수 · 1년 / 30일 치명률 · 대한심혈관중재학회 회복 · 관리 가이드북 배포 보도(2026.11.10) — 재발 위험 시기<br>'
    'Ferns SP 외, Stroke 2009(코일색전술 8,161건) — 코일색전술 후 재개통 비율 · 보건복지부 소개 서울대 사적 간병비 추정(2022년) — 국민 사적 간병비(연간)</p></div></body></html>')
_NH, _NA = NEED_HEART_HTML, NOTICE_ADD_HTML
del NEED_HEART_HTML, NOTICE_ADD_HTML
def _with_fonts(h): return h.replace('%(F)s', fonts_css(), 1).replace('%%', '%')
def need_heart_html(): return _with_fonts(_NH)       # 심장 쪽 맨 위 「다시 찾아오는 심근경색」(틀에 굳힌다)
def notice_add_html(): return _with_fonts(_NA)       # 안내사항 아래 「이번 제안서에 더한 쪽 안내 · 추가 출처」(틀에 굳힌다)

# ═══════════════ 한 건 읽기 → 칸 값 ═══════════════
def V(key): return GP.VAL[key][0] if key in GP.VAL else None
def LN(key): return GP.VAL[key][1] if key in GP.VAL else []
def isnum(x): return isinstance(x, (int, float)) and not isinstance(x, bool)
def adhoc(sc_, mode):
    c = dict(kind='engine', sc=sc_, mode=mode, need=None, na_if_empty=False, key='adhoc')
    return GS.cell_value(c, GP.RID)
EXTRA = {}
def load(design_pdf, age=''):
    GP.load(design_pdf, age)
    EXTRA.clear()
    for side, sc_ in (('b', GS._b_thrombectomy), ('h', GS._h_thrombectomy)):     # 기계적 혈전제거술(카테터) 단독 — 5열 표의 둘째 열(회의 2026-11-11)
        for md in ('first', 'year', 'each'):
            EXTRA['thx.%s.%s' % (side, md)] = adhoc(sc_, md)
    for n in GS.DZ_ORDER:                                                         # 수술 카드 「상급종합」 열 = 같은 사례를 상급종합병원에서
        EXTRA['dzup.' + n] = adhoc(GS.sc_dz(n, '상급종합'), 'first')
    EXTRA['care'] = care_flags()
def _raw(key):
    """(값, 지급 줄, 집계 방식)"""
    if key in EXTRA: return EXTRA[key][0], EXTRA[key][1], key.rsplit('.', 1)[-1] if key.startswith('thx.') else 'first'
    if key in ('rh_ca', 'rh_bh'):        # 재활 : 회당 금액 × 연 횟수(v41 표기 「입원 · 외래 재활(연 20회 / 연 15회)」)
        b = 'p2.rh.in' if key == 'rh_ca' else 'p3.rh.in'; r = V(b)
        return (r * (20 if key == 'rh_ca' else 15) if isnum(r) else r), LN(b), GS.KEY[b]['mode']
    c = GS.KEY.get(key)
    return V(key), LN(key), (c['mode'] if c else 'first')
def VX(key):
    """칸 값(표시용). 계산 엔진이 0 을 냈는데 그 칸에 해당하는 가입 특약이 아예 없으면(최초 지급 기준으로도 0원) 「미가입」 으로 보인다.
    0 은 「가입했지만 이 경우엔 안 나옴」(예 : 매 회 0 = 연 1회만 지급하는 특약)일 때만 남긴다"""
    if key == 'ex_ca_total': return tsum('p2.dx.일반암', 'p2.sg.robot.first', 'p2.cm.immune1.first')
    if key == 'ex_brain_total': return tsum('p3.dx.뇌졸중', 'p3.b1.first', 'p3.sev.icu')      # 예시가 「뇌경색」 → 뇌졸중(I63) 진단 칸(뇌혈관질환진단비 + 뇌졸중진단비)
    if key == 'ex_heart_total': return tsum('p3.dx.허혈성심장', 'p3.h2.first', 'p3.h2.year')
    v, L, mode = _raw(key)
    base = 'first' if mode in ('first', 'year', 'each') else mode
    if isnum(v) and abs(v) < 1e-9 and not any(GS.counts(l, base) for l in L): return None
    return v
def tsum(*keys):
    vs = [VX(k) for k in keys]; ns = [x for x in vs if isnum(x)]
    return float(sum(ns)) if ns else None

def fmt(v, unit='만'):
    """(숫자 글자, 단위) — None 은 미가입. 「1억」 처럼 만 단위가 없으면 단위를 붙이지 않는다"""
    if v is None: return None, ''
    if isinstance(v, str): return v, ''
    t = won(v); return t, ('' if t.endswith('억') else unit)
def mtxt(v, unit='만'):
    t, u = fmt(v, unit)
    return '미가입' if t is None else t + u

# ═══════════════ 간병인 가입 상태(설계서 담보 이름 · 가입금액만 읽는다 — ga_care) ═══════════════
def span(name):
    """담보가 맡는 입원 날짜(1회 입원 기준) — 담보 이름의 기간 그대로. 「181일이상」 = 180일을 넘긴 날부터 1회 입원당 185일 한도(2610 간병인지원 · 사용 181일이상 특약 제2조 공통 · tool_body 케355 · 케356 · 케361 · 통166 · 통172 …),
    「(1일이상 N일한도)」 = 1~N일(1~30일 · 1~180일). 이름에 기간이 없으면 1~180일로 본다"""
    n = _ns(name)
    if '181일' in n: return (181, 365)
    m = re.search(r'(\d+)일한도', n)
    return (1, int(m.group(1))) if m else (1, 180)
def _on(r, d): a, b = span(r['name']); return a <= d <= b
def care_flags():
    rs = CARE.norm(GP.RID)
    def names(L): return [r['name'] for r in L]
    sup180 = CARE.support(rs); supnh = CARE.support_nh(rs); supnurse = CARE.nurse_add(rs)
    dz = CARE._dz(rs)      # 질병입원일당만(상해 입원일당은 칸에 없다 — ga_care 와 같은 기준 · 사례도 질병 입원)
    sup181 = [r for r in dz if '간병인지원' in r['name'] and '181일' in r['name'] and '간호·간병' not in r['name']]
    use = {k: CARE.use(rs, k) for k in ('gen', 'nh', 'nurse')}
    use181 = [r for r in dz if '간병인사용' in r['name'] and '181일' in r['name'] and '간호·간병' not in r['name'] and '(요양병원)' not in r['name']]
    usenh181 = [r for r in rs if '간병인사용' in r['name'] and '요양성특정질병입원일당' in r['name'] and '181일' in r['name']]
    amt = lambda L: (sum(r['man'] for r in L) if L else None)
    sups = sup180 + sup181 + supnh
    f = dict(sup180=sup180, sup181=sup181, supnh=supnh, supnurse=supnurse, R=dict(gen=use['gen'], u181=use181, nh=use['nh'], unh181=usenh181),
             use_gen=amt(use['gen']), use_nh=amt(use['nh']), use_nurse=amt(use['nurse']), use181=amt(use181), usenh181=amt(usenh181),
             unused=CARE.unused(rs)[0], nh_daily=(sum(CARE.daily(r) for r in supnh) if supnh else None), nurse_add=(sum(r['man'] for r in supnurse) if supnurse else None),
             nurse_total=CARE.nurse_total(rs)[0],                     # 보장요약 칸(p1.care.nurse)과 같은 값 = 사용추가보장 + (Ⅰ형) 질병입원일당
             lim_sup=max([span(r['name'])[1] for r in sup180] or [0]), lim_gen=max([span(r['name'])[1] for r in use['gen']] or [0]), lim_nh=max([span(r['name'])[1] for r in use['nh']] or [0]),
             type1=any('(Ⅰ)' in r['name'] for r in sups), type6=any('(Ⅵ)' in r['name'] for r in sups),
             sup_names=names(sup180 + sup181 + supnh + supnurse), use_names=names(use['gen'] + use['nh'] + use['nurse'] + use181 + usenh181))
    f['has_sup'] = bool(sup180 or sup181 or supnh or supnurse)
    f['has_use'] = any(f[k] for k in ('use_gen', 'use_nh', 'use181', 'usenh181'))      # 「간병인사용」 담보로만 정한다(간호 · 간병통합서비스 입원일당만 있으면 간병인사용일당 가입이 아니다 → 함께 쪽 · 그 금액은 그 쪽에 적는다)
    f['pages'] = (['support'] if f['has_sup'] else []) + (['use'] if f['has_use'] else []) or ['none']      # 둘 다 없으면 지원 + 사용 한 쪽
    return f, [], []
def CF(): return EXTRA['care'][0]
# 하루하루 보장 — 종합병원(병원 · 의원, 요양병원 제외) / 요양병원. 값 : 숫자(사용 일당 만원) · SEND(간병인 지원) · None(보장 없음)
def use_day(cf, d, nh=False):
    L = (cf['R']['nh'] + cf['R']['unh181']) if nh else (cf['R']['gen'] + cf['R']['u181'])
    return sum(r['man'] for r in L if _on(r, d))
def sup_day(cf, d, nh=False):
    if nh: return any(_on(r, d) for r in cf['sup180'] + cf['supnh'])      # 1~180일 지원 특약은 요양병원 입원도 보장(약관 제4조 · 의료법 제3조 병원 · 의원) · 181일 이상은 요양성 특정질병(요양병원) 특약
    return any(_on(r, d) for r in cf['sup180'] + cf['sup181'])
def runs(fn, days=240):
    """하루 값이 같은 날끼리 묶기 → [(첫날, 끝날, 값)]"""
    out = []
    for d in range(1, days + 1):
        v = fn(d)
        if out and out[-1][2] == v: out[-1][1] = d
        else: out.append([d, d, v])
    return [tuple(x) for x in out]

# ═══════════════ v41 틀 위에 값 얹기 ═══════════════
_SL = None
def slots():
    global _SL
    if _SL is None: _SL = json.load(open(SLOTS, encoding='utf-8'))
    return _SL
K_BASE = 0.8125       # Pretendard : 글자 크기 1 에 대한 「상자 위 → 기준선」 거리(line-height 1 일 때) — 아래 calibrate() 로 잰 값
def _at(cx=None, x0=None, x1=None, base=0, size=10, inner='', align='center', extra=''):
    top = base - K_BASE * size
    if align == 'center': pos = 'left:%.2fpt;width:300pt;text-align:center' % (cx - 150)
    elif align == 'left': pos = 'left:%.2fpt;text-align:left' % x0
    else: pos = 'right:%.2fpt;text-align:right' % (slots()['size'][0] - x1)
    return '<div class="o" style="%s;top:%.2fpt;font-size:%.2fpt;%s">%s</div>' % (pos, top, size, extra, inner)
def amt_html(s, v):
    t, u = fmt(v)
    if t is None: return '<span style="font-size:%.2fpt;color:#AAAAAA;font-weight:600">미가입</span>' % (s['size'] * 0.755)
    if isinstance(v, str): return '<span style="color:#E5432F;font-weight:800;font-size:%.2fpt">%s</span>' % (s['size'] * 0.8, t)
    return '<b style="color:%s">%s</b>%s' % (s['color'], t, ('<span style="font-size:%.2fpt;color:%s;font-weight:600;margin-left:.4pt">%s</span>' % (s['usize'], s['ucolor'], u)) if u else '')
def who_html(sz=6.0, lab='#666666', val='#222222'):
    h = GP.HEAD; sep = '<i style="display:inline-block;width:.6pt;height:%.1fpt;background:#C9C9C9;margin:0 %.1fpt;vertical-align:-.6pt"></i>' % (sz, sz * 0.9)
    return ('<span style="color:%s">소속 : </span><b style="color:%s">%s</b>%s<span style="color:%s">코드 : </span><b style="color:%s">%s</b>%s<span style="color:%s">컨설턴트 : </span><b style="color:%s">%s</b>'
            % (lab, val, h.get('org') or '-', sep, lab, val, h.get('code') or '-', sep, lab, val, h.get('agent_name') or '-'))
def gender_line():
    sx = (GP.HEAD.get('sex') or '') or {'F': '여자', 'M': '남자'}.get(GP.META.get('sex') or '', '')
    if sx.startswith('여'): return '여성 1위 유방암'          # 2위 갑상선암은 유사암(옆 칸) — 일반암 칸 아래라 적지 않는다
    if sx.startswith('남'): return '남성 1위 전립선암 · 2위 폐암'
    return '남성 1위 전립선암 · 여성 1위 유방암'
def _paid(key, mode='first'):
    c = GS.KEY.get(key)
    return [(l['name'], GS.counts(l, mode if c is None else c['mode'])) for l in LN(key) if GS.counts(l, mode if c is None else c['mode'])]
def _short_rider(n):
    m = re.search(r'\[([^\[\]]+)\]\s*$', n); n2 = m.group(1) if m else n
    return re.sub(r'^\(\d+년갱신\)갱신형\s*|\(건강가입\)', '', n2).strip()
def dx_note(k1, k2):
    """두 진단 칸이 같은 특약(들)로만 나오면 「중복 지급 안 됨」 안내 — 다른 특약이면 쓰지 않는다(설계마다 다름)"""
    a, b = _paid(k1), _paid(k2)
    if not a or not b or sorted(a) != sorted(b): return ''
    names = ' · '.join('%s %s만원' % (_short_rider(n), won(x)) for n, x in a)
    return '※ 두 진단 항목은 동일 특약(%s)으로 보장되며, 중복하여 지급되지 않습니다.' % names
def life_note(key):
    """혈전용해 + 혈전제거 칸에 「통합치료 생활비」 가 들어 있으면 그 까닭(종류가 다른 통합치료 2회 · 약관 2-101 제2조)"""
    L = [(n, x) for n, x in _paid(key) if '생활비' in n]
    if not L: return ''
    return '※ 혈전용해 + 혈전제거술 : 종류가 다른 치료 2회라 최초 지급시 · 연간 1회 금액에 「특정순환계질환 통합치료 생활비」 %s만원(연 1회)이 더해져 있습니다.' % won(sum(x for _, x in L))
def overlay_html():
    """틀 6쪽(암① · 암② · 뇌 · 심 · 안내사항 · 세부내역 틀은 따로) 위에 얹을 값 글자 — 쪽 크기 그대로, 배경은 투명"""
    SL = slots(); W, H = SL['size']; pages = []
    for pk in ('ca1', 'ca2', 'brain', 'heart', 'notice'):
        o = []
        for s in SL['slots'][pk]:
            k = s['kind']
            if k in ('amt', 'total'):
                o.append(_at(cx=s['cx'], base=s['base'], size=s['size'], inner=amt_html(s, VX(s['key'])), extra='font-weight:800'))
            elif k == 'amt_desc':
                v = VX(s['key']); inner = amt_html(s, v) + (('<span style="font-size:%.2fpt;color:%s;font-weight:500;margin-left:2.4pt">%s</span>' % (s.get('dsize', 7.7), s.get('dcolor', '#666666'), s['desc'])) if s.get('desc') and v is not None else '')
                o.append(_at(cx=s['cx'], base=s['base'], size=s['size'], inner=inner, extra='font-weight:800'))
            elif k == 'text':
                t = {'gender_line': gender_line, 'ex_brain_dx': lambda: '뇌졸중(뇌경색)'}[s['key']]()
                o.append(_at(cx=s['cx'], base=s['base'], size=s['size'], inner='<span style="color:%s">%s</span>' % (s['color'], t), extra='font-weight:500'))
            elif k == 'note':
                t = (dx_note('p3.dx.뇌혈관', 'p3.dx.뇌졸중') if pk == 'brain' else dx_note('p3.dx.허혈성심장', 'p1.bh.dx.급성심근경색')) if s['key'] == 'dx_note' else ((GP.HEAD.get('no') or '-') + ')')
                if t: o.append(_at(x0=s['x0'], base=s['base'], size=s['size'], inner='<span style="color:%s">%s</span>' % (s['color'], t), align='left', extra='font-weight:500;white-space:nowrap'))
            elif k == 'life':
                t = life_note('p3.b1.first' if pk == 'brain' else 'p3.h1.first')
                if t: o.append(_at(x1=s['x1'], base=s['top'] + 7.0, size=6.6, inner='<span style="color:#6B6B73">%s</span>' % t, align='right', extra='white-space:nowrap'))
            elif k == 'footer':
                o.append(_at(x1=s['x1'], base=s['base'], size=s['size'], inner=who_html(s['size']), align='right', extra='white-space:nowrap;font-weight:500'))
        pages.append('<div class="pg">%s</div>' % ''.join(o))
    css = ('@page{size:%spt %spt;margin:0}html,body{margin:0;background:transparent;font-family:P;-webkit-print-color-adjust:exact;print-color-adjust:exact}'
           '.pg{position:relative;width:%spt;height:%spt;overflow:hidden;page-break-after:always}.o{position:absolute;line-height:1;white-space:nowrap;font-variant-numeric:tabular-nums;letter-spacing:-.15pt}' % (W, H, W, H))
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>' % (fonts_css(), css, ''.join(pages))

# 뇌 · 심 「치료 및 수술」 5열 표(회의 2026-11-11 : 기계적 혈전제거술 열 추가) — 칸 값은 ga_spec p3.b* · p3.h* + 혈전제거 단독(EXTRA)
BRAIN_COLS = [('혈전용해', ['thrombolysis'], '약물로 혈전을<br>녹이는 치료', 'p3.b0.%s'), ('기계적 혈전제거술', ['thrombectomy'], '카테터로 혈전을<br>직접 빼내는 시술', 'thx.b.%s'),
              ('혈전용해 + 혈전제거술', ['thrombolysis', 'thrombectomy'], '약물 투여 후<br>카테터로 제거', 'p3.b1.%s'), ('코일색전술', ['coil'], '코일로 뇌동맥류<br>파열 예방', 'p3.b2.%s'), ('개두수술', ['craniotomy'], '두개골을 여는<br>수술', 'p3.b3.%s')]
HEART_COLS = [('혈전용해', ['thrombolysis'], '약물로 혈전을<br>녹이는 치료', 'p3.h0.%s'), ('기계적 혈전제거술', ['thrombectomy'], '카테터로 혈전을<br>직접 빼내는 시술', 'thx.h.%s'),
              ('혈전용해 + 혈전제거술', ['thrombolysis', 'thrombectomy'], '약물 투여 후<br>카테터로 제거', 'p3.h1.%s'), ('스텐트삽입술', ['stent'], '스텐트로 혈관을<br>넓히는 수술', 'p3.h2.%s'), ('개흉수술', ['thoracotomy'], '가슴을 여는<br>수술', 'p3.h3.%s')]
TBL_ROWS = {'brain': (316.5, [338.2, 394.5, 429.0, 464.2, 499.5]), 'heart': (324.0, [345.8, 399.8, 434.2, 468.8, 504.0])}     # v41 줄 위치 그대로
def table_html(cols, hpt, rows_pt):
    h0, h1, h2, h3, h4 = rows_pt
    def ic(keys):
        if len(keys) == 1: return ico(keys[0], 30)
        return '<span style="position:relative;display:inline-block;width:46px;height:30px"><span style="position:absolute;left:0;top:0">%s</span><span style="position:absolute;left:16px;top:0">%s</span></span>' % (ico(keys[0], 30), ico(keys[1], 30))
    def amt(key, red):
        v = VX(key); t, u = fmt(v)
        if t is None: return '<span style="font-size:10pt;font-weight:600;color:#AAAAAA">미가입</span>'
        return '<span style="font-size:14.5pt;font-weight:800;color:%s">%s</span><span style="font-size:8pt;color:#1F1F22;font-weight:600">%s</span>' % ('#E5432F' if red else '#1F1F22', t, u)
    th = ''.join('<th>%s</th>' % c[0] for c in cols)
    r1 = ''.join('<td class="ic"><div>%s</div><div class="ds">%s</div></td>' % (ic(c[1]), c[2]) for c in cols)
    r2, r3, r4 = (''.join('<td>%s</td>' % amt(c[3] % md, md == 'first') for c in cols) for md in ('first', 'year', 'each'))
    css = fonts_css() + '''@page{size:532.5pt %spt;margin:0}*{box-sizing:border-box}html,body{margin:0;width:532.5pt;height:%spt;overflow:hidden;font-family:P;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all}
    table{width:532.5pt;border-collapse:collapse;table-layout:fixed}td,th{padding:0;text-align:center;vertical-align:middle}
    th{background:#F4F4F5;font-size:9pt;font-weight:600;color:#333;height:%spt;border-bottom:.8pt solid #D9D9DD;white-space:nowrap}
    td{border-bottom:.75pt solid #EDEDF0;font-variant-numeric:tabular-nums}td.lb{background:#FAFAFA;font-size:9.3pt;color:#444;font-weight:500}td.lb.r{color:#E5432F;font-weight:700}
    td.ic{background:#fff}.ds{font-size:7.9pt;color:#555;line-height:1.25;margin-top:2pt}''' % (hpt, hpt, h0)
    return ('<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body><table><colgroup><col style="width:63.7pt">%s</colgroup>'
            '<tr><th></th>%s</tr><tr style="height:%spt"><td class="lb"></td>%s</tr><tr style="height:%spt"><td class="lb r">최초 지급시</td>%s</tr>'
            '<tr style="height:%spt"><td class="lb">연간 1회</td>%s</tr><tr style="height:%spt"><td class="lb">매 회</td>%s</tr></table></body></html>') % (
            css, '<col>' * len(cols), th, h1, r1, h2, r2, h3, r3, h4, r4)

# ═══════════════ 새로 그리는 쪽(HTML) ═══════════════
CSS = None
def css():
    global CSS
    if CSS is None: CSS = fonts_css() + open(os.path.join(V2, 'v2.css'), encoding='utf-8').read()
    return CSS
def head(title): return '<div class="hd"><span class="ttl">%s</span></div>' % title
def foot(note): return '<div class="ft"><span>%s</span><span class="who">%s</span></div>' % (note, who_html())
def page(title, body, note): return '<div class="page">%s<div class="cnt">%s</div>%s</div>' % (head(title), body, foot(note))
def M(v, unit='만'):
    t, u = fmt(v, unit)
    return '미가입' if t is None else '%s<small>%s</small>' % (t, u) if u else t

# ── 치료 여정 ──
def stp(n, name, desc, val, sub='', cls='', opts=()):
    o = ''.join('<div class="o%s"><span>%s</span><b>%s</b></div>' % (' on' if on == 1 else (' no' if on == -1 else ''), l, v) for l, v, on in opts)
    if val == '미가입': cls += ' gap'
    return '<div class="stp %s"><div class="sn">%s</div><div class="sd">%s</div><div class="sv">%s</div><div class="ss">%s</div>%s</div>' % (
        cls, ('%s %s' % (n, name)).strip(), desc, val, sub, ('<div class="op">%s</div>' % o) if o else '')
class Txt(str): pass      # 이미 만든 표시 글자(칸 이름이 아님)
def opt(label, key_or_val, on=0):
    if isinstance(key_or_val, Txt): return (label, str(key_or_val), -1 if key_or_val == '미가입' else on)
    v = VX(key_or_val) if isinstance(key_or_val, str) else key_or_val
    t = mtxt(v) if not isinstance(v, str) else v
    return (label, t, -1 if v is None else on)
def same_all(keys):
    vs = [VX(k) for k in keys]
    if all(v is None for v in vs): return Txt('미가입')
    return Txt(('각 ' + mtxt(vs[0])) if all(v == vs[0] for v in vs) else ' · '.join(mtxt(v) for v in vs))
def lane(icon, title, case, steps):
    n = len(steps)
    return ('<div class="lane"><div class="lh">%s<b>%s</b><span>%s</span></div><div class="steps" style="grid-template-columns:repeat(%d,1fr) 1.25fr">%s</div></div>'
            % (ico(icon, 30), title, case, n - 1, ''.join(steps)))
def page_journey():
    cf = CF()
    ex = tsum('p2.ex.x_ct', 'p2.ex.x_bio')
    ca_tot = tsum('p2.dx.일반암', 'p2.sg.robot.first', 'p2.cm.immune1.first')
    rad = [VX('p2.rd.%s.first' % k) for _, k in GS.RD]; radn = [x for x in rad if isnum(x)]
    cancer = lane('cancer_general', '암 치료 여정', '폐암 진단 후 다빈치로봇 수술 · 면역항암 약물치료를 받은 경우(상급종합병원 · 가정)', [
        stp('1', '검사', 'CT + 조직검사', M(ex), '연 1회', '', [opt('내시경 · MRI · PET', same_all(['p2.ex.x_endo', 'p2.ex.x_mri', 'p2.ex.x_pet'])), opt('초음파 · CT', same_all(['p2.ex.x_us', 'p2.ex.x_ct']), 1),
                                                         opt('조직검사', 'p2.ex.x_bio', 1), opt('NGS 유전자', 'p2.ex.x_ngs')]),
        stp('2', '진단', '일반암(폐암)', M(VX('p2.dx.일반암')), '최초 1회', '', [opt('일반암', 'p2.dx.일반암', 1), opt('유사암', 'p2.dx.유사암'), opt('전이암', 'p2.dx.전이암')]),
        stp('3', '수술', '다빈치로봇 수술', M(VX('p2.sg.robot.first')), '최초 지급시', '', [opt('내시경', 'p2.sg.endo.first'), opt('개복 · 개흉', 'p2.sg.open.first'), opt('복강경 · 흉강경', 'p2.sg.lap.first'), opt('다빈치로봇', 'p2.sg.robot.first', 1)]),
        stp('4', '항암', '면역항암 약물치료', M(VX('p2.cm.immune1.first')), '최초 지급시', '', [opt('화학항암', 'p2.cm.chemo.first'), opt('표적항암', 'p2.cm.target1.first'), opt('면역항암', 'p2.cm.immune1.first', 1),
                                                         ('방사선', ('%s~%s' % (mtxt(min(radn)), mtxt(max(radn)))) if radn else '미가입', 0 if radn else -1)]),
        stp('5', '재활 · 후유장해', '입원 · 외래 재활', M(VX('rh_ca')), '연 20회 기준', 'last', [opt('재활', 'rh_ca', 1), opt('암 후유장해(3~100%)', 'p2.dis')]),
        stp('', '진단 + 수술 + 항암', '세 단계만 더해도', M(ca_tot), '검사 · 재활은 별도', 'tt')])
    b_tot = tsum('p3.dx.뇌졸중', 'p3.b1.first', 'p3.sev.icu')
    care_v, care_sub, care_opts = care_lane(cf)
    brain = lane('brain', '뇌혈관 치료 여정', '뇌경색 진단 후 혈전용해 + 혈전제거술 · 중환자실 치료를 받고 간병인을 쓴 경우(가정)', [
        stp('1', '진단', '뇌졸중(뇌경색)', M(VX('p3.dx.뇌졸중')), '최초 1회', '', [opt('뇌혈관질환(동맥류 등)', 'p3.dx.뇌혈관'), opt('검사 MRI · PET', same_all(['p3.ex.x_mri', 'p3.ex.x_pet'])), opt('검사 CT', 'p3.ex.x_ct')]),
        stp('2', '치료 · 수술', '혈전용해 + 혈전제거술', M(VX('p3.b1.first')), '최초 지급시', '', [opt('혈전용해', 'p3.b0.first'), opt('기계적 혈전제거술', 'thx.b.first'), opt('혈전용해 + 혈전제거술', 'p3.b1.first', 1),
                                                                 opt('코일색전술', 'p3.b2.first'), opt('개두수술', 'p3.b3.first')]),
        stp('3', '중증치료', '중환자실 치료', M(VX('p3.sev.icu')), '', '', [opt(n.split('(')[0], 'p3.sev.' + k, 1 if k == 'icu' else 0) for n, k in GS.SEV]),
        stp('4', '재활', '입원 · 외래 재활', M(VX('rh_bh')), '연 15회 기준'),
        stp('5', '간병', '간병인 30일', care_v, care_sub, 'last', care_opts),
        stp('', '진단 + 치료 + 중증', '세 단계만 더해도', M(b_tot), '재활 · 간병은 별도', 'tt')])
    h_tot = tsum('p3.dx.허혈성심장', 'p3.h2.first', 'p3.h2.year')
    sev_n = [VX('p3.sev.' + k) for _, k in GS.SEV]; sev_n = [x for x in sev_n if isnum(x)]
    heart = lane('heart', '심장 치료 여정', '협심증으로 스텐트를 넣고, 1년 뒤 다시 시술한 경우(가정)', [
        stp('1', '진단', '허혈성심장질환(협심증)', M(VX('p3.dx.허혈성심장')), '최초 1회', '', [opt('검사 MRI · PET', same_all(['p3.ex.x_mri', 'p3.ex.x_pet'])), opt('검사 CT', 'p3.ex.x_ct')]),
        stp('2', '수술', '스텐트 삽입술', M(VX('p3.h2.first')), '최초 지급시', '', [opt('혈전용해', 'p3.h0.first'), opt('기계적 혈전제거술', 'thx.h.first'), opt('혈전용해 + 혈전제거술', 'p3.h1.first'),
                                                         opt('스텐트삽입술', 'p3.h2.first', 1), opt('개흉수술', 'p3.h3.first')]),
        stp('3', '1년 뒤 재시술', '스텐트 삽입술', M(VX('p3.h2.year')), '연간 1회 금액', '', [opt('해마다 다시', 'p3.h2.year', 1), opt('같은 해 한 번 더', 'p3.h2.each')]),
        stp('4', '중증치료 · 재활', '필요할 때', ('최대 ' + M(max(sev_n))) if sev_n else '미가입', '', 'last', [('중환자실 · 에크모', same_all(['p3.sev.icu', 'p3.sev.ecmo']), 0), opt('재활(연 15회)', 'rh_bh')]),
        stp('', '진단 + 수술 + 재시술', '다시 시술해도', M(h_tot), '1회차 수술 기준 · 중증 · 재활 별도', 'tt')])
    gaps = journey_gaps(cf)
    strip = ('<div class="box" style="background:#F9FAFB;display:flex;gap:12px;align-items:center"><div style="flex:none;font-size:11px;font-weight:700">여정에서<br>비어 있던 곳</div>'
             '<div style="display:flex;gap:8px;flex:1">%s</div><div style="flex:none;font-size:8.6px;color:#2B5BBF;font-weight:600">뒤쪽 「보장 점검」에서<br>한 번에 확인 →</div></div>'
             % ''.join('<div class="tile no" style="flex:1"><div class="n"><i></i>%s</div><div class="a">미가입</div></div>' % g for g in gaps)) if gaps else ''
    note = ('<div class="note" style="margin:0 0 7px;font-size:9px">아프면 어떤 일이 차례로 생기고, 그때마다 내 보험에서 얼마가 나오는지 왼쪽에서 오른쪽으로 따라가 보세요. 단계 아래 목록은 그 단계에서 받을 수 있는 다른 금액이고, '
            '<b style="color:#C8102E">빨간 줄</b>이 예시로 고른 치료입니다. 점선은 지금 설계에 없는 보장입니다.</div>')
    return page('치료 여정으로 보는 내 보장', note + cancer + brain + heart + strip,
                '※ 이 설계 금액 기준 · 단계별 「최초 지급시」 금액의 단순 합산 예시입니다(상급종합병원 · 간병 30일 가정). 특약별 연간 지급한도 · 지급조건에 따라 실제 지급액은 달라집니다.')
def care_lane(cf):
    """뇌 여정 「간병」 단계 — 뇌졸중으로 종합병원에 30일 입원해 간병인을 쓴 경우(가정)"""
    o = []
    if cf['has_sup']:
        o += [('지원 · 병원 의원', SEND if cf['sup180'] else '미가입', 1 if cf['sup180'] and not cf['use_gen'] else (0 if cf['sup180'] else -1)),
              ('지원 · 요양병원', SEND if (cf['sup180'] or cf['supnh']) else '미가입', 0 if (cf['sup180'] or cf['supnh']) else -1)]
        if cf['nurse_total']: o.append(('지원 · 간호간병통합', '1일 %s만' % won(cf['nurse_total']), 0))
    if cf['has_use']:
        o += [opt('사용 · 병원 의원', cf['use_gen'], 1 if cf['use_gen'] else 0), opt('사용 · 요양병원', cf['use_nh'])]
    if cf['use_nurse']: o.append(opt('간호간병통합 일당', cf['use_nurse']))
    if not cf['has_sup'] and not cf['has_use']: o.append(('간병인 지원 · 사용', '미가입', -1))
    late = [sup_day(cf, d) or use_day(cf, d) for d in range(181, 241)]
    o.append(('병원 · 의원 181일~', ('이어서 보장' if all(late) else '일부만') if any(late) else '미가입', 0 if any(late) else -1))
    v30 = [use_day(cf, d) for d in range(1, 31)]
    if sum(v30): return M(sum(v30)), ('1일 %s만 × 30일' % won(v30[0])) if len(set(v30)) == 1 else '30일 일당 합계', o
    if all(sup_day(cf, d) for d in range(1, 31)): return SEND, '병원 · 의원 1~%d일' % cf['lim_sup'], o
    return '미가입', '병원 · 의원 간병 보장이 없어요', o
def journey_gaps(cf):
    g = []
    if VX('p2.dx.전이암') is None: g.append('암 · 전이암 진단비')
    if VX('p2.dx.유사암') is None: g.append('암 · 유사암 진단비')
    if VX('p3.dx.뇌혈관') is None and VX('p3.dx.뇌졸중') is None: g.append('뇌 · 뇌혈관질환 진단비')
    if VX('p3.dx.허혈성심장') is None and VX('p1.bh.dx.급성심근경색') is None: g.append('심장 · 허혈성심장질환 진단비')
    if not cf['has_sup'] and not cf['has_use']: g.append('뇌 · 간병인 보장')
    elif not all(sup_day(cf, d) or use_day(cf, d) for d in range(1, 241)): g.append('뇌 · 병원 의원 간병 비는 기간')
    return g[:3]

# ── 주요수술 ① ② ──
DZ_ICON = {'백내장': 's_cataract', '디스크': 's_disc', '무릎관절질환': 's_knee', '담석증': 's_gallstone', '맹장염': 's_appendix', '갑상선결절': 's_thyroid',
           '유방양성종양': 's_breast', '자궁근종': 's_uterus', '전립선비대증': 's_prostate', '치질': 's_hemorrhoid', '요로결석': 's_kidneystone', '골절진단': 's_fracture'}
DZ_SEX = {'유방양성종양': '여성', '자궁근종': '여성', '전립선비대증': '남성'}
# 질병코드 이름 : kcdnames.json(특약 마스터)에 없는 두 칸만 약관 별표 글자 그대로(코드를 만들지 않는다 · CLAUDE.md 1)
KCD_TERMS = {'M17': ('M17', '무릎관절증'),                                   # The건강한 내Mom대로 5.10.5 2610 약관 【별표1-2】 특정질병 분류표
             'N40': ('N40~N45, N47~N51', '남성 생식기관의 질환')}             # 같은 약관 관절염 · 생식기질환 분류표(131대질병수술비) — N40 단독 이름은 약관에 없어 분류 이름으로
_KN = None
def kcd_chip(code):
    global _KN
    if _KN is None: _KN = json.load(open(os.path.join(BASE, 'kcdnames.json'), encoding='utf-8'))
    c3 = code.split('.')[0]
    if c3 in KCD_TERMS: c, n = KCD_TERMS[c3]
    else: c, n = c3, _KN.get(c3) or _KN.get(code) or ''
    return '<span class="chip code">%s %s</span>' % (c, n) if n else '<span class="chip code">%s</span>' % c
CAT_ORDER = ['basic', 'six', 'upper', 's15', 's17', 's131', 's32', 'etc']
def eff_name(n, no=None):
    """「┗ 수술비[상해2종]」 처럼 부모 특약 아래 세부 줄로 실린 담보는 부모 이름(설계서 읽기의 via)을 앞에 붙여 읽는다 — 1-5종 · 1-7종 판정용"""
    if not (n or '').lstrip().startswith('┗'): return n
    r = next((r for r in GP.RID if no is not None and r.get('no') == no), None) or next((r for r in GP.RID if r['name'] == n), None)
    return ((r or {}).get('via') or '') + ' ' + n.replace('┗', '').strip()
def rid_names(): return [eff_name(r['name'], r.get('no')) for r in GP.RID if (r.get('man') or 0) > 0]
def cat_of(n):
    m = _ns(n)
    if '1-5종' in m: return 's15'
    if '1-7종' in m: return 's17'
    if '상급종합병원' in m: return 'upper'
    if '특정6대질병제외' in m: return 'six'
    if re.search(r'13[01]대', m): return 's131'
    if '32대' in m: return 's32'
    if re.fullmatch(r'질병수술비|상해수술비', re.sub(r'^\(\d+년갱신\)갱신형', '', m)): return 'basic'
    return 'etc'
def _ns(x): return re.sub(r'\s+', '', x or '')
def row_label(n, l):
    s = re.sub(r'^\(\d+년갱신\)갱신형\s*|\(건강가입\)', '', re.sub(r'\s+', ' ', n)).strip()
    if '1-5종' in s or '1-7종' in s:
        g = (re.search(r'\[(?:질병|상해)(\d종)\]', s) or [None, ''])[1] or GP.line_note(l); cause = '상해' if '상해' in s else '질병'
        return '%s 수술비 [%s%s]' % ('1-5종' if '1-5종' in s else '1-7종', cause, g)
    return s.replace('131대질병수술비', '131대 질병수술비').replace('130대질병수술비', '130대 질병수술비')
def surg_rows(name):
    """수술 하나의 줄 — (표시 이름, 범주, 모든 병원 금액, 상급종합 금액, 체증형?). 금액은 ga_spec 칸(p1.dz · 같은 사례 상급종합)의 지급 줄 그대로"""
    A = {}; order = []
    for l in LN('p1.dz.' + name):
        a = GS.counts(l, 'first')
        if not a: continue
        if l['name'] not in A: A[l['name']] = [l, 0, 0]; order.append(l['name'])
        A[l['name']][1] += a
    for l in EXTRA['dzup.' + name][1]:
        a = GS.counts(l, 'first')
        if not a: continue
        if l['name'] not in A: A[l['name']] = [l, None, 0]; order.append(l['name'])
        A[l['name']][2] += a
    full = {n: eff_name(n, A[n][0].get('no')) for n in order}
    rows = [(row_label(full[n], A[n][0]), cat_of(full[n]), A[n][1], A[n][2], '체증' in full[n]) for n in order]
    have = {cat_of(n) for n in rid_names()}
    for cat, lab in (('s15', '1-5종 수술비'), ('s17', '1-7종 수술비')):
        if cat not in have: rows.append((lab + (' [상해]' if name == '골절진단' else ''), cat, '미가입', '미가입', False))
    rows.sort(key=lambda r: CAT_ORDER.index(r[1]))
    return rows
def card(name):
    proc, kcd = GS.GA_DZ[name][0], GS.GA_DZ[name][1]
    rows = surg_rows(name); rs = ''; ta = tu = 0.0
    for lab, cat, a, u, inc in rows:
        if a == '미가입':
            rs += '<tr><td>%s</td><td colspan="2" class="na">미가입</td></tr>' % lab; continue
        tag = ''
        if cat == 's15': tag = ' <span class="cz">체증형</span>' if inc else ' <span class="cz" style="background:#F2F4F6;color:#8B95A1">체증형 미가입</span>'
        ta += a or 0; tu += u or 0
        rs += '<tr><td>%s%s</td><td class="num %s">%s</td><td class="num">%s</td></tr>' % (lab, tag, 'na' if a is None else '', '–' if a is None else won(a) + '만', won(u) + '만')
    want = V('p1.dz.' + name)
    if isnum(want) and abs(ta - want) > 0.01: raise RuntimeError('수술 카드 합계(%s)가 보장요약 칸(%s)과 다름 : %s' % (ta, want, name))
    none = not rows or all(r[2] == '미가입' for r in rows)
    if none: rs += '<tr><td colspan="3" class="na" style="text-align:center">이 수술에 나오는 보장이 없습니다</td></tr>'
    tot = lambda v: '<span style="font-size:12px;color:#A0A7B1;font-weight:600">미가입</span>' if none else '%s<small>만</small>' % won(v)
    sex = DZ_SEX.get(name)
    chips = kcd_chip(kcd) + ((' <span class="chip %s">%s</span>' % ('m' if sex == '남성' else 'f', sex)) if sex else '')
    return ('<div class="card"><div class="ch">%s<div><div class="nm">%s</div><div class="op">%s</div><div style="margin-top:2px">%s</div></div></div>'
            '<table class="rt"><tr><th>보장(특약)</th><th>모든 병원</th><th>상급종합</th></tr>%s</table>'
            '<div class="tot"><div><span>모든 병원</span><b class="num">%s</b></div><div class="up"><span>상급종합</span><b class="num">%s</b></div></div></div>') % (
            ico(DZ_ICON[name], 46), name.replace('골절진단', '골절'), proc, chips, rs, tot(ta), tot(tu))
NEED_SURG = ('<div class="need"><div><div class="k">연간 주요수술 건수</div><div class="v">215<small>만건</small></div><div class="s">전년 대비 4.8% 증가</div></div>'
             '<div><div class="k">수술 1건당 평균 진료비</div><div class="v">496<small>만</small></div><div class="s">전년 대비 9.5% 상승</div></div>'
             '<div><div class="k">수술 진료비 증가</div><div class="v">14.7<small>%</small></div><div class="s">전년 대비 · 총 10조 6,738억</div></div></div>'
             '<div class="src">[출처: 국민건강보험공단 2025년 주요수술 통계연보]</div>')
def s15_info():
    """1-5종 수술비 : (가입?, 체증형?, 질병1종 가입금액, 질병5종 가입금액) — 설계서 담보 이름 · 가입금액 그대로"""
    L = [(eff_name(r['name'], r.get('no')), r['man']) for r in GP.RID if (r.get('man') or 0) > 0]
    L = [(n, m) for n, m in L if '1-5종' in _ns(n)]
    g = lambda k: next((m for n, m in L if re.search(r'\[?질병%d종\]?' % k, _ns(n))), None)
    return bool(L), any('체증' in n for n, _ in L), g(1), g(5)
def esc():
    has, inc, a1, a5 = s15_info()
    def bars(vals, mx): return ''.join('<div style="height:%d%%"%s><span>%s만</span></div>' % (h, ' class="mx"' if i == mx else '', won(v)) for i, (h, v) in enumerate(vals))
    b1, b5 = (a1 or 20), (a5 or 100); g1 = '' if a1 else '(가정)'; g5 = '' if a5 else '(가정)'
    lead = ('이 설계는 <b>체증형</b>입니다. 같은 종 수술을 다시 받을수록 아래처럼 커집니다.' if inc else
            '이 설계는 <b>일반형</b>(회차와 관계없이 가입금액 100%)입니다. 체증형이라면 같은 종 수술을 다시 받을 때 아래처럼 커집니다.' if has else
            '이 설계에는 <b>1-5종 수술비가 없습니다</b>. 체증형에 가입하면 같은 종 수술을 다시 받을 때 아래처럼 커집니다(가입금액 가정).')
    return ('<div class="esc"><h4>1-5종 수술비 <span class="red">체증형</span> 시나리오 — 같은 종 수술을 다시 받을수록 커져요</h4><p>%s</p>' % lead +
            '<div class="g2" style="margin-top:4px"><div><div class="bars">' + bars([(50, b1), (62, b1 * 1.25), (75, b1 * 1.5), (87, b1 * 1.75), (100, b1 * 2)], 4) +
            '</div><div class="lbl"><div>1회차<br>100%%</div><div>2회차<br>125%%</div><div>3회차<br>150%%</div><div>4회차<br>175%%</div><div>5회차 이후<br>200%%</div></div>'
            '<div class="note" style="text-align:center">1 · 2 · 3종 수술(질병 1종 %s만원 기준%s)</div></div>' % (won(b1), g1) +
            '<div><div class="bars">' + bars([(50, b5), (75, b5 * 1.5), (100, b5 * 2)], 2) +
            '</div><div class="lbl"><div>1회차<br>100%%</div><div>2회차<br>150%%</div><div>3회차 이후<br>200%%</div></div>'
            '<div class="note" style="text-align:center">4 · 5종 수술(질병 5종 %s만원 기준%s)</div></div></div>' % (won(b5), g5) +
            '<div class="note">근거 : 수술비Ⅱ(1-5종)(체증형) 약관 제1조 지급금액표(질병 · 상해 각각 · 같은 종 수술 회차 기준). 막대 높이는 가입금액 대비 지급 비율입니다.</div></div>')
LEGEND = ('<div class="note" style="margin:0 0 6px">가입한 보장과 <b>가입하지 않은 보장(회색 「미가입」)</b>을 함께 보여 드립니다. 1-5종 수술비가 일반형이면 「체증형 미가입」으로 표시하고, '
          '체증형은 다음 쪽 아래 시나리오에서 볼 수 있습니다. 「상급종합」 합계는 같은 수술을 상급종합병원에서 받았을 때의 금액으로, 병원 종류에 따라 더 나오는 보장(상급종합병원 · 종합병원 질병수술비 등 · 「모든 병원」 칸 「–」)이 들어 있습니다.</div>')
def page_surg(i):
    names = GS.DZ_ORDER[i * 6:(i + 1) * 6]
    body = (NEED_SURG if i == 0 else '') + '<div class="tag">다빈도 수술별 보장금액 %s</div><div class="sec"></div>' % ('①' if i == 0 else '②') + (LEGEND if i == 0 else '')
    body += '<div class="cards">' + ''.join(card(n) for n in names) + '</div>'
    if i == 1: body += '<div style="margin-top:7px">' + esc() + '</div>'
    return page('주요수술 보장 %s' % ('①' if i == 0 else '②'), body, '※ 금액은 이 설계의 특약별 가입금액 기준입니다. 수술명 옆 질병코드는 사례 기준이며, 체증형 막대는 예시입니다.')

# ── 간병인 ──
def need_care():
    return ('<div class="need"><div><div style="display:flex;justify-content:center">%s</div><div class="k">간병인 고용 시 하루 평균</div><div class="v red">12.2<small>만</small></div></div>'
            '<div><div style="display:flex;justify-content:center">%s</div><div class="k">한 달 평균 간병비</div><div class="v red">370<small>만</small></div></div>'
            '<div><div style="display:flex;justify-content:center">%s</div><div class="k">국민 사적 간병비(연간 추정)</div><div class="v">10<small>조원</small></div></div></div>'
            '<div class="src">[출처: 보건복지부 2023년 발표 자료 · 보건복지부 소개 서울대 사적 간병비 추정(2022년) / 지역 · 환자 상태에 따라 편차가 큼]</div>') % (
            ico('caregiver', 40), ico('care_cost', 40), ico('private_care', 40))
def cov(on, k, s, v, d):
    return '<div class="cov%s"><div class="k">%s</div><div class="s">%s</div><div class="v">%s</div><div class="s">%s</div></div>' % ('' if on else ' na', k, s, v if on else '미가입', d)
GAP = '#B0B8C1'; RED = '#E8432E'; USE = '#8A9BB8'
def seg_html(rs, prefer):
    """240일 막대 — rs : [(첫날, 끝날, 값)] · prefer : 'sup'(지원 쪽 : 지원 빨강 · 사용 회청) / 'use'(사용 쪽 : 사용 빨강 · 지원 회청)"""
    h = '<div class="tl">'
    for a, b, v in rs:
        w = (b - a + 1) / 240 * 100; left = (a - 1) / 240 * 100
        if v == SEND: c, t = (RED if prefer == 'sup' else USE), '간병인 보내줌'
        elif v: c, t = (RED if prefer == 'use' else USE), '일당 %s만' % won(v)
        else: c, t = GAP, '미가입(보장 공백)'
        lab = ('%d~%d일 · %s' % (a, b, t)) if w >= 22 else ('%d~%d일' % (a, b) if w >= 9 else '')
        h += '<div class="seg" style="left:%.3f%%;width:%.3f%%;background:%s">%s</div>' % (left, w, c, lab)
    return h + '<div class="tick" style="left:0;transform:none">입원 1일</div><div class="tick" style="left:75%">180일</div><div class="tick" style="right:0;left:auto;transform:none">240일 퇴원</div></div>'
def seg_words(rs):
    def w(v): return '회사가 간병인을 보내 드립니다' if v == SEND else ('간병인을 쓴 날 일당 %s만원이 나옵니다' % won(v) if v else '간병 보장이 없습니다')
    return ' '.join('%d~%d일에는 %s.' % (a, b, w(v)) for a, b, v in rs)
def page_care_support(cf):
    hosp = bool(cf['sup180'] or cf['sup181'] or not cf['supnh'])
    nh = not hosp
    rs = runs(lambda d: SEND if sup_day(cf, d, nh) else (use_day(cf, d, nh) or None))
    title = '뇌졸중으로 종합병원에 240일 입원한 경우(가정)' if hosp else '요양성 특정질병으로 요양병원에 240일 입원한 경우(가정)'
    tiles = (cov(cf['sup180'], '병원 · 의원', '요양병원 포함 · 1회 입원 1~%d일' % (cf['lim_sup'] or 180), SEND, ('안 쓰면 입원일당 1일 %s만' % won(cf['unused'])) if cf['unused'] else '간병인 지원(현물)')
             + cov(cf['sup181'], '181일 이상 장기입원', '요양 · 정신 · 한방병원 제외', SEND, '1회 입원당 최대 185일')
             + cov(cf['supnh'], '요양병원 181일 이상', '요양성 특정질병만', SEND, ('안 쓰면 입원일당 1일 %s만 · 최대 185일' % won(cf['nh_daily'])) if cf['nh_daily'] else '1회 입원당 최대 185일')
             + cov(cf['supnurse'], '간호 · 간병통합서비스', '통합서비스 병동 이용 시', ('%s만 / 1일' % won(cf['nurse_total'])) if cf['nurse_total'] else '',
                   ('사용추가보장 %s만 + 입원일당 %s만' % (won(cf['nurse_add']), won(cf['unused']))) if cf['unused'] and cf['nurse_add'] else '사용 추가보장'))
    desc = '이 설계는 ' + seg_words(rs)
    gaps = [(a, b) for a, b, v in rs if not v]
    if gaps and hosp:
        add = []
        if any(a <= 180 for a, b in gaps): add.append('간병인지원 질병입원일당(1일이상 180일한도)')
        if any(b > 180 for a, b in gaps): add.append('간병인지원 질병입원일당(181일이상)(요양 · 정신 · 한방병원 제외)')
        desc += ' %s을(를) 더하면 빈 기간이 채워집니다.' % ' · '.join(add)
    body = need_care() + '<div class="tag">내 간병인 지원 보장 <span style="font-weight:500;font-size:10px">(현물 지원 · 회사가 간병인을 보내 드려요)</span></div><div class="sec"></div>'
    body += '<div class="g4">' + tiles + '</div>'
    body += '<div class="tag" style="margin-top:9px">이렇게 이용해요</div><div class="sec"></div><div class="step">' + ''.join('<div><span class="n">%d</span><b>%s</b>%s</div>' % (i + 1, a, b) for i, (a, b) in enumerate([
        ('입원 확정', '입원 치료가 정해지면'), ('48시간 전 신청', '원하는 날 48시간 전까지 회사로 신청 <span class="tbd">신청 전화번호 확정 필요</span>'),
        ('간병인 방문', '지원 시점부터 24시간을 1일로 간병(24시간 미만도 1일)'), ('못 보낼 때는', '회사가 간병인을 보내지 못하면 실제 쓴 간병비를 회사가 정한 한도로 지급')])) + '</div>'
    body += ('<div class="tag" style="margin-top:9px">장기입원 시나리오</div><div class="sec"></div><div class="box"><h4>%s</h4>' % title + seg_html(rs, 'sup') + '<p>%s</p></div>' % desc)
    know = []
    if cf['sup181'] or cf['supnh']:
        know.append('· 181일 이상 보장은 1회 입원당 최대 185일까지입니다%s.' % ('. 요양병원 181일 이상은 <b>요양성 특정질병</b>으로 입원한 경우만 해당합니다' if cf['supnh'] else ''))
    if cf['lim_sup'] and cf['lim_sup'] < 180: know.append('· 병원 · 의원 간병인 지원은 1회 입원당 %d일까지입니다.' % cf['lim_sup'])
    know.append('· 간호 · 간병통합서비스 병동을 쓰는 날은 간병인을 보내 드리지 않습니다%s.' % (('(대신 1일 %s만원)' % won(cf['nurse_total'])) if cf['nurse_total'] else ''))
    if cf['type1'] and not cf['type6']:
        know.append('· 회사에 신청하지 않고 임의로 간병인을 쓰면 간병비 대신 입원일당%s으로 지급합니다.' % (('(1일 %s만원)' % won(cf['unused'])) if cf['unused'] else ''))
    elif cf['type6'] and not cf['type1']:
        know.append('· 회사에 신청하지 않고 임의로 간병인을 쓰면 그 간병비는 지급하지 않습니다.')
    elif cf['type1'] and cf['type6']:
        know.append('· 회사에 신청하지 않고 임의로 간병인을 쓰면 (Ⅰ)형은 입원일당으로 지급하고 (Ⅵ)형은 지급하지 않습니다.')
    body += ('<div class="g2" style="margin-top:8px"><div class="box"><h4>공동간병인 <span class="tbd">문구 확정 필요</span></h4><p>현장 요청으로 넣는 자리입니다. 공동간병(간병인 1명이 여러 환자를 함께 돌봄) 이용 가능 여부 · 기준은 상품설명서 기준 문구로 확정해 넣습니다.</p></div>'
             '<div class="box"><h4>알아두세요</h4><p>%s</p></div></div>' % '<br>'.join(know))
    body += '<div class="note">근거 : 이 설계의 %s 특별약관(제1조 · 제2조).</div>' % ' · '.join(_short_name(n) for n in cf['sup_names'])
    return page('간병인 보장 · 간병인 지원 가입자', body, '※ 금액은 이 설계의 특약별 가입금액 기준입니다. 입원일수 · 평균 간병비는 가정값입니다.')
def _short_name(n): return re.sub(r'^\(\d+년갱신\)', '', re.sub(r'\s+', ' ', n)).strip()
def page_care_use(cf):
    tiles = (cov(cf['use_gen'], '병원 · 의원', '요양병원 제외 · 1~%d일' % (cf['lim_gen'] or 180), '%s만 / 1일' % won(cf['use_gen'] or 0), ('평균 간병비 12.2만%s' % ('보다 큰 일당' if (cf['use_gen'] or 0) > 12.2 else ' 기준')))
             + cov(cf['use181'], '181일 이상 장기입원', '요양 · 정신 · 한방병원 제외', '%s만 / 1일' % won(cf['use181'] or 0), '1회 입원당 최대 185일')
             + cov(cf['use_nh'], '요양병원', '1~%d일' % (cf['lim_nh'] or 180), '%s만 / 1일' % won(cf['use_nh'] or 0), '요양병원 입원')
             + cov(cf['use_nurse'], '간호 · 간병통합서비스', '통합서비스 병동(요양병원 제외)', '%s만 / 1일' % won(cf['use_nurse'] or 0), '통합병동 본인부담 약 2.2만*'))
    body = need_care() + '<div class="tag">내 간병인 사용 보장 <span style="font-weight:500;font-size:10px">(금액 지원 · 간병인을 쓴 날마다 일당)</span></div><div class="sec"></div><div class="g4">' + tiles + '</div>'
    hosp = any(use_day(cf, d) for d in range(1, 241))
    v30 = [use_day(cf, d, not hosp) for d in range(1, 31)]; where = '종합병원' if hosp else '요양병원'
    body += '<div class="tag" style="margin-top:9px">사례로 보는 간병비 보장</div><div class="sec"></div><div class="box">'
    if sum(v30):
        exp30 = round(12.2 * 30); got30 = sum(v30); diff = got30 - exp30
        per = ('일당 %s만 × 30일' % won(v30[0])) if len(set(v30)) == 1 else '30일 일당 합계'
        body += ('<h4>질병으로 %s에 30일 입원해 간병인을 쓴 경우(가정)</h4><div class="cmp">' % where +
                 '<div>예상 간병비<br>하루 12.2만 × 30일<div class="big">%s만</div></div><div class="muted">vs</div><div>보장 금액<br>%s<div class="big rb">%s만</div></div><div class="muted">=</div>'
                 '<div class="res">평균 간병비 대비<div class="big">%s%s만 %s</div></div></div>' % (won(exp30), per, won(got30), '+' if diff >= 0 else '-', won(abs(diff)), '여유' if diff >= 0 else '부족'))
    else:
        body += '<h4>입원 1~30일에는 간병인 사용 일당이 없습니다</h4><p>이 설계의 간병인 사용 보장은 180일을 넘긴 날부터 시작합니다. 입원 초기(1~180일) 간병비는 지금 보장으로 받을 수 없습니다.</p>'
    body += '<p class="note" style="margin-top:4px">※ 평균 간병비를 단순 적용한 계산 예시입니다. 실제 간병비와 보험금은 입원 기간 · 병원 · 지급조건(약관)에 따라 다릅니다. * 통합병동 본인부담 약 2.2만원 : 보건복지부 간호 · 간병통합서비스 안내(종합병원 6인실 1일 기준)</p></div>'
    rs = runs(lambda d: use_day(cf, d, not hosp) or (SEND if sup_day(cf, d, not hosp) else None))
    exp = round(12.2 * 240); tot = sum(v * (b - a + 1) for a, b, v in rs if isnum(v) and v)
    calc = ' + '.join('%d일 × %s만' % (b - a + 1, won(v)) for a, b, v in rs if isnum(v) and v) or '0원'
    gap = next(((a, b) for a, b, v in rs if not v), None)
    ttl = '뇌졸중으로 종합병원에 240일 입원한 경우(가정)' if hosp else '요양병원에 240일 입원한 경우(가정)'
    body += ('<div class="tag" style="margin-top:9px">장기입원 시나리오</div><div class="sec"></div><div class="box"><h4>%s</h4>' % ttl + seg_html(rs, 'use') +
             '<div class="cmp" style="margin-top:4px"><div>예상 간병비<br>12.2만 × 240일<div class="big">%s만</div></div><div class="muted">vs</div><div>지금 보장(일당)<br>%s<div class="big rb">%s만</div></div><div class="muted">=</div>'
             '<div class="res"%s>%s<div class="big"%s>%s</div></div></div>' % (won(exp), calc, won(tot), ' style="background:#FDECEE"' if gap else '', ('%d~%d일' % gap) if gap else '240일 내내',
                                                                               ' style="color:#C8102E"' if gap else '', '보장 공백' if gap else '끊김 없이') +
             ('<p class="note">회청색 칸은 간병인 지원(현물) 기간이라 일당 합계에는 넣지 않았습니다.</p>' if any(v == SEND for _, _, v in rs) else '') + '</div>')
    body += '<div class="tag" style="margin-top:9px">이렇게 청구해요</div><div class="sec"></div><div class="step">' + ''.join('<div><span class="n">%d</span><b>%s</b>%s</div>' % (i + 1, a, b) for i, (a, b) in enumerate([
        ('간병인 사용', '병원 소속 간병인 · 등록된 간병 업체 등 약관이 정한 유상 간병인(가족 간병 제외)'), ('서류 챙기기', '입원 확인서 · 간병인 사용 확인 서류(영수증 등) <span class="tbd">서류 목록 확정 필요</span>'),
        ('청구', '모바일 앱 · 홈페이지 · 고객센터'), ('일당 지급', '간병인을 쓴 날 수 × 일당')])) + '</div>'
    body += '<div class="note">근거 : 이 설계의 %s(뒤쪽 세부내역) · 간병인의 정의(약관 제4조). 평균 간병비 12.2만 · 입원일수(30일 · 240일)는 가정값.</div>' % ' · '.join(_short_name(n) for n in cf['use_names'])
    return page('간병인 보장 · 간병인 사용 가입자', body, '※ 금액은 이 설계의 특약별 가입금액 기준입니다. 입원일수 · 평균 간병비는 가정값입니다.')
def page_care_none():
    """간병인 지원 · 사용 둘 다 없을 때 — 두 방법을 한 쪽에 같이(소유자 2026-11-11)"""
    body = need_care()
    body += ('<div class="box" style="margin-bottom:8px"><h4>간호 · 간병통합서비스 병동을 이용하면? <span class="muted" style="font-weight:400;font-size:9px">(1일 기준)</span></h4>'
             '<div style="display:grid;grid-template-columns:120px 1fr;gap:4px 8px;align-items:center;font-size:9px;margin-top:4px"><span>사적 간병인 고용(하루 평균)</span><div style="display:flex;align-items:center;gap:6px"><div style="height:12px;width:80%;background:#B0B8C1;border-radius:3px"></div><b>약 12.2만원</b></div>'
             '<span>간호 · 간병통합서비스 본인부담</span><div style="display:flex;align-items:center;gap:6px"><div style="height:12px;width:14.4%;background:#E8432E;border-radius:3px"></div><b class="red">약 2.2만원</b></div></div>'
             '<p class="note">통합서비스 병동은 병상이 한정되어 원하는 시기에 이용하지 못할 수 있습니다. 두 경우 모두를 대비하는 보장이 필요합니다. [출처: 보건복지부 2023년 발표 자료(간병비) · 보건복지부 간호 · 간병통합서비스 안내(종합병원 6인실)]</p>' + (
             ('<p style="margin-top:4px;font-size:9.5px"><b>이 설계</b> : 간호 · 간병통합서비스 입원일당 <b class="red">1일 %s만원</b>(통합서비스 병동을 쓴 날) — 일반병동에서 간병인을 쓰는 날은 보장하지 않습니다.</p>' % won(CF()['use_nurse'])) if CF()['use_nurse'] else '') + '</div>')
    body += ('<div class="tag">간병 보장, 두 가지 방법이 있어요</div><div class="sec"></div><div class="g2">'
             '<div class="box"><h4>%s 간병인 <span class="red">지원</span>(현물)</h4><p>회사가 간병인을 <b>직접 보내 드려요</b>. 간병인을 구하는 수고와 비용 걱정이 없어요.<br>· 병원 · 의원 1~180일(요양병원 포함)<br>· 181일 이상 장기입원(요양 · 정신 · 한방 제외)<br>· 요양병원 181일 이상(요양성 특정질병)</p><div style="margin-top:6px"><span class="chip">이 설계 미가입</span></div></div>'
             '<div class="box"><h4>%s 간병인 <span class="red">사용</span>(금액)</h4><p>병원 소속 간병인이나 등록된 간병 업체의 간병인을 쓴 날마다 <b>정해진 일당</b>을 드려요(가족 간병은 보장하지 않아요).<br>· 병원 · 의원(요양병원 제외) · 요양병원 1~180일<br>· plus 181일 이상 장기입원(요양 · 정신 · 한방 제외)</p><div style="margin-top:6px"><span class="chip">이 설계 미가입</span></div></div></div>'
             % (ico('caregiver', 26), ico('care_cost', 26)))
    body += ('<div class="tag" style="margin-top:9px">간병 보장이 없다면</div><div class="sec"></div><div class="box"><h4>뇌졸중으로 240일 입원하면 간병비만 약 %s만원(하루 12.2만 × 240일, 가정)</h4>' % won(round(12.2 * 240)) +
             '<div class="cmp" style="margin-top:4px"><div>30일<div class="big">%s만</div></div><div class="muted">→</div><div>180일<div class="big">%s만</div></div><div class="muted">→</div><div class="res">240일<div class="big">%s만</div></div></div>' % (won(round(12.2 * 30)), won(round(12.2 * 180)), won(round(12.2 * 240))) +
             '<p class="note" style="margin-top:6px">장기입원은 180일에서 끝나지 않습니다. 181일 이상까지 이어지는 간병 보장을 함께 확인해 보세요.</p></div>')
    return page('간병인 보장', body, '※ 이 설계에는 간병인 지원 · 사용 보장이 없습니다. 입원일수 · 평균 간병비는 가정값입니다.')

# ── 보장 점검 ──
def tile(st, name, amt): return '<div class="tile%s"><div class="n"><i></i>%s</div><div class="a">%s</div></div>' % (st, name, amt)
def A(v): return M(v)
def tmax(keys):
    vs = [VX(k) for k in keys]; ns = [x for x in vs if isnum(x)]
    return max(ns) if ns else None
def page_check():
    cf = CF(); OK, PT, NO = '', ' pt', ' no'
    def T(name, v, prefix=''):
        if v is None: return (NO, name, '미가입')
        if isinstance(v, str): return (OK, name, v)
        if abs(v) < 1e-9: return (PT, name, '0만')
        return (OK, name, prefix + A(v))
    has = lambda pat: any(re.search(pat, _ns(n)) for n in rid_names())
    s15, inc, _, _ = s15_info()
    sg_max = tmax(['p2.sg.%s.first' % k for _, k in GS.SG]); cm_max = tmax(['p2.cm.chemo.first', 'p2.cm.target1.first', 'p2.cm.immune1.first', 'p2.cm.two', 'p2.cm.two3'])
    rd_max = tmax(['p2.rd.%s.first' % k for _, k in GS.RD])
    b_max = tmax(['p3.b%d.first' % i for i in range(4)] + ['thx.b.first']); h_max = tmax(['p3.h%d.first' % i for i in range(4)] + ['thx.h.first'])
    sev_max = tmax(['p3.sev.' + k for _, k in GS.SEV])
    ROWS = [
     ('암', 'cancer_general', [T('진단 · 일반암', VX('p2.dx.일반암')), T('진단 · 유사암', VX('p2.dx.유사암')), T('진단 · 전이암', VX('p2.dx.전이암')), T('수술', sg_max, '최대 '),
            T('항암약물', cm_max, '최대 '), T('항암방사선', rd_max, '최대 '), T('재활', VX('rh_ca')), T('암 후유장해', VX('p2.dis'))]),
     ('뇌혈관', 'brain', [T('진단', tmax(['p3.dx.뇌혈관', 'p3.dx.뇌졸중']), '최대 '), T('치료 · 수술', b_max, '최대 '), T('중증치료', sev_max, '항목별 최대 '), T('재활', VX('rh_bh'))]),
     ('심장', 'heart', [T('진단', tmax(['p3.dx.허혈성심장', 'p1.bh.dx.급성심근경색']), '최대 '), T('치료 · 수술', h_max, '최대 '), T('중증치료', sev_max, '항목별 최대 '), T('재활', VX('rh_bh'))]),
     ('수술', 's_knee', [(OK if has(r'^(\(\d+년갱신\)갱신형)?질병수술비$') else NO, '질병수술비', '가입' if has(r'^(\(\d+년갱신\)갱신형)?질병수술비$') else '미가입'),
            (OK if has(r'13[01]대') else NO, '130 · 131대 질병수술비', '가입' if has(r'13[01]대') else '미가입'),
            ((OK, '1-5종 수술비', '체증형') if inc else (PT, '1-5종 수술비', '일반형 <small>· 체증형 미가입</small>')) if s15 else (NO, '1-5종 수술비', '미가입'),
            (OK if has('1-7종') else NO, '1-7종 수술비', '가입' if has('1-7종') else '미가입'), (OK if has('32대') else NO, '32대 질병관혈수술비', '가입' if has('32대') else '미가입')]),
     ('간병', 'caregiver', [T('사용 · 병원 의원', cf['use_gen'], '1일 '), T('사용 · 요양병원', cf['use_nh'], '1일 '), T('사용 · 간호간병통합', cf['use_nurse'], '1일 '), T('사용 · 181일 이상', cf['use181'], '1일 '),
            T('지원 · 1~%d일' % (cf['lim_sup'] or 180), SEND if cf['sup180'] else None), T('지원 · 181일~(병원)', SEND if cf['sup181'] else None), T('지원 · 요양 181일~', SEND if cf['supnh'] else None),
            T('지원 · 간호간병통합', cf['nurse_total'] if cf['supnurse'] else None, '1일 ')]),
    ]
    n_ok = sum(1 for _, _, ts in ROWS for t in ts if t[0] == OK); n_more = sum(1 for _, _, ts in ROWS for t in ts if t[0] != OK)
    rows_html = ''.join('<div class="row"><div class="rh">%s%s</div><div class="tiles" style="grid-template-columns:repeat(%d,1fr)">%s</div></div>' % (
        ico(ic, 26), nm, min(len(ts), 4), ''.join(tile(*t) for t in ts)) for nm, ic, ts in ROWS)
    more = []
    if VX('p2.dx.전이암') is None: more.append(('전이암 진단비', '원발암에서 다른 부위로 전이됐을 때 받는 진단비입니다. 지금 설계에는 없습니다.', '암 보장 ① · 2. 암 진단'))
    if VX('p2.dx.유사암') is None: more.append(('유사암 진단비', '갑상선암 · 기타피부암 · 경계성종양 · 제자리암 진단비입니다. 지금 설계에는 없습니다.', '암 보장 ① · 2. 암 진단'))
    if any(VX(k) is None for k in ('p3.dx.뇌혈관', 'p3.dx.뇌졸중', 'p3.dx.허혈성심장', 'p1.bh.dx.급성심근경색')):
        more.append(('뇌 · 심 진단비', '뇌혈관질환 · 뇌졸중 · 허혈성심장질환 · 급성심근경색 진단 가운데 비어 있는 칸이 있습니다.', '뇌혈관 · 심장 보장 · 2. 진단'))
    if not cf['has_sup'] and not cf['has_use']: more.append(('간병인 지원 · 사용', '간병인 보장이 없습니다. 회사가 간병인을 보내 주는 지원형과 일당을 주는 사용형이 있습니다.', '간병인 보장'))
    else:
        hole = [(a, b) for a, b, v in runs(lambda d: bool(sup_day(cf, d) or use_day(cf, d))) if not v]      # 종합병원 240일 입원 가정에서 지원 · 사용 둘 다 없는 날
        if hole: more.append(('간병 비는 기간', '병원 · 의원에 오래 입원하면 %s에는 간병 보장이 없습니다. 그 기간을 채우는 간병인 지원 · 사용 보장을 확인해 보세요.' % ' · '.join('%d~%d일' % h for h in hole), '간병인 보장 · 장기입원 시나리오'))
    if s15 and not inc: more.append(('1-5종 수술비 체증형', '지금은 일반형입니다. 체증형은 같은 종 수술을 다시 받을수록 100% → 최대 200%까지 커집니다(약관 지급표).', '주요수술 보장 · 체증형 시나리오'))
    if not s15: more.append(('1-5종 수술비', '수술 종류(1~5종)에 따라 나오는 수술비입니다. 지금 설계에는 없습니다.', '주요수술 보장 ① ②'))
    if not has('1-7종') or not has('32대'): more.append(('1-7종 · 32대 질병관혈수술비', '수술 종류에 따라 더해지는 수술비입니다. 지금 설계에는 %s.' % ('둘 다 없습니다' if not has('1-7종') and not has('32대') else '하나가 없습니다'), '주요수술 보장 ① ②'))
    more = more[:4]
    body = ('<div class="sum"><div><div class="k">준비된 보장</div><div class="v" style="color:#0E7C4A">%d<small>개</small></div></div>'
            '<div><div class="k">더 살펴볼 보장</div><div class="v" style="color:#333D4B">%d<small>개</small></div></div>'
            '<div><div class="k">이 쪽은 이렇게 봐요</div><div style="font-size:8.6px;color:#4E5968;line-height:1.5;margin-top:2px">앞쪽에서 본 보장을 한 장에 모았습니다. 비어 있는 칸이 꼭 필요한 보장이라는 뜻은 아닙니다. 필요한지 함께 확인해 보세요.</div></div></div>' % (n_ok, n_more)
            + '<div class="lg"><span><i style="background:#0E7C4A"></i>준비됨</span><span><i style="background:#B25E00"></i>일부만</span><span><i style="background:#fff;border:1.5px solid #8B95A1"></i>미가입</span></div>' + rows_html
            + (('<div class="tag" style="margin-top:6px">더 살펴볼 보장</div><div class="sec"></div><div class="more">' + ''.join('<div class="mc"><span class="no_">%d</span><div><b>%s</b><p>%s</p><div class="pg">관련 쪽 : %s</div></div></div>' % (i + 1, a, b, c) for i, (a, b, c) in enumerate(more)) + '</div>') if more else ''))
    return page('보장 점검', body, '※ 금액은 이 설계 기준이며, 「최대」는 각 보장 쪽에서 가장 큰 최초 지급시 금액입니다.')

# ═══════════════ 보장금액 세부내역(글씨 키움 · 쪽 나눔 자동) ═══════════════
DETAIL_CSS = '''
@page{size:595pt 708pt;margin:0}*{box-sizing:border-box}
html,body{margin:0;font-family:P;color:#222;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all;overflow-wrap:anywhere}
.pg{width:595pt;height:708pt;overflow:hidden;position:relative;page-break-after:always}
.w{position:absolute;left:33.8pt;top:6pt;width:527.2pt}
.tab{display:inline-block;background:#EE3823;color:#fff;font-weight:800;font-size:12pt;line-height:1;padding:5.5pt 15pt 5pt;border-radius:6pt 6pt 0 0}
.tab:not(:first-child){margin-top:10pt}
table{width:100%;border-collapse:collapse;table-layout:fixed;border-top:1.5pt solid #DADADA}
th{background:#F4F4F4;white-space:nowrap;font-size:9.2pt;font-weight:500;color:#444;height:23pt;padding:0 6pt;border-bottom:.75pt solid #E6E6E6}th.r{text-align:right}
td{border-bottom:.75pt solid #E6E6E6;padding:2.3pt 6pt;vertical-align:middle}
td.k{font-size:9.6pt;line-height:1.25;padding-left:9pt;overflow-wrap:normal;word-break:keep-all}td.k small{display:block;font-size:7.6pt;color:#8B8B93;font-weight:500;margin-bottom:1pt}td.k b{font-weight:600}
td.m{text-align:right;padding-right:10pt;white-space:nowrap}td.m b{font-size:12.2pt;font-weight:800;color:#111;letter-spacing:-.2pt}td.m span{font-size:8.4pt;font-weight:500;margin-left:1.5pt}
td.m b.tx{font-size:10pt;font-weight:700}
td.m.na .pill{display:inline-block;font-size:8.6pt;color:#9A9AA2;border:.8pt dashed #C4C4C8;border-radius:9pt;padding:1.5pt 8pt}
td.n{font-size:8.7pt;font-weight:600;line-height:1.24;color:#222}td.n .sub{font-weight:500;color:#8B8B93}
td.n.none{color:#9A9AA2;font-weight:500;font-size:8.4pt}
td.ga{text-align:right;font-size:8.6pt;color:#9A9AA2;white-space:nowrap}
td.ea{text-align:right;font-size:8.9pt;font-weight:700;color:#222;white-space:nowrap;padding-right:7pt}
tbody.g tr:last-child td,tbody.g td.k,tbody.g td.m{border-bottom-color:#D2D2D6}
'''
DETAIL_COLS = '<colgroup><col style="width:102pt"><col style="width:86pt"><col><col style="width:50pt"><col style="width:66pt"></colgroup>'
DETAIL_HEAD = '<thead><tr><th>구분</th><th class="r" style="padding-right:10pt">보장금액</th><th>특약명</th><th class="r">가입금액</th><th class="r" style="padding-right:7pt">특약별 보장금액</th></tr></thead>'
DETAIL_JS = r'''
const PX = 4/3, HPX = 708*PX, root = document.getElementById('root');
let page = null, wrap = null, table = null, tab = null, report = {pages:0, groups:0, over:[]};
function newPage(){ page = document.createElement('div'); page.className = 'pg'; wrap = document.createElement('div'); wrap.className = 'w'; page.appendChild(wrap); root.appendChild(page); table = null; }
function startTable(title, cont){ tab = document.createElement('div'); tab.className = 'tab'; tab.textContent = title + (cont ? ' (이어서)' : ''); wrap.appendChild(tab);
  table = document.createElement('table'); table.dataset.sec = title; table.innerHTML = COLS + HEAD; wrap.appendChild(table); }
function over(){ return wrap.offsetTop + wrap.getBoundingClientRect().height > HPX - 2; }
newPage();
for (const sec of SECTIONS){ let placed = false;
  for (const g of sec.groups){ let made = false;
    if (!table || table.dataset.sec !== sec.title){ startTable(sec.title, placed); made = true; }
    table.insertAdjacentHTML('beforeend', g); let tb = table.lastElementChild;
    const orphan = made && !placed && wrap.children.length > 2 && (HPX - (wrap.offsetTop + wrap.getBoundingClientRect().height)) < 60*PX;
    if (over() || orphan){ tb.remove(); if (made){ table.remove(); tab.remove(); }
      newPage(); startTable(sec.title, placed); table.insertAdjacentHTML('beforeend', g); tb = table.lastElementChild;
      if (over()) report.over.push(sec.title); }
    placed = true; report.groups++; } }
report.pages = document.querySelectorAll('.pg').length;
window.REPORT = report;
'''
def _esc(t): return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def detail_groups():
    """ga_proposal.calc_sections()(보장요약 칸의 합산 계산서) → 표 묶음. 구분 보장금액 = 특약별 합(다르면 멈춘다)"""
    out = []
    for title, rows in GP.calc_sections():
        sec = dict(title=title.replace('뇌,심', '뇌 · 심'), groups=[])
        for lab, v, rs in rows:
            m = re.match(r'\[([^\]]+)\]\s*(.*)', lab); cat, item = (m.group(1), m.group(2)) if m else ('', lab)
            if isnum(v) and rs and abs(sum(a for *_, a in rs) - v) > 0.01: raise RuntimeError('세부내역 합계 불일치 : %s %s ≠ %s' % (lab, v, sum(a for *_, a in rs)))
            n = max(1, len(rs))
            k = '<td class="k" rowspan="%d"><small>%s</small><b>%s</b></td>' % (n, _esc(cat), _esc(item).replace('(', '<wbr>(').replace(',', ',<wbr>'))
            t, u = fmt(v, '만원')
            if t is None: a = '<td class="m na" rowspan="%d"><span class="pill">미가입</span></td>' % n
            elif isinstance(v, str): a = '<td class="m" rowspan="%d"><b class="tx">%s</b></td>' % (n, _esc(t))
            else: a = '<td class="m" rowspan="%d"><b>%s</b><span>%s</span></td>' % (n, t, u or '원')
            if not rs:
                g = '<tbody class="g"><tr>%s%s<td class="n none" colspan="3">이 설계에는 가입되지 않은 보장입니다</td></tr></tbody>' % (k, a)
            else:
                trs = []
                for i, (nm, note, man, amt) in enumerate(rs):
                    ga = '' if man is None else (won(man) + ('원' if won(man).endswith('억') else '만원'))
                    ea = won(amt) + ('원' if won(amt).endswith('억') else '만원')
                    nmh = _esc(nm) + (('<span class="sub"> : %s</span>' % _esc(note)) if note else '')
                    trs.append('<tr>%s<td class="n">%s</td><td class="ga">%s</td><td class="ea">%s</td></tr>' % ((k + a) if i == 0 else '', nmh, ga, ea))
                g = '<tbody class="g">%s</tbody>' % ''.join(trs)
            sec['groups'].append(g)
        out.append(sec)
    return out
def render_detail(out_pdf):
    secs = detail_groups()
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body><div id="root"></div><script>const SECTIONS=%s;const COLS=%s;const HEAD=%s;%s</script></body></html>'
            % (fonts_css(), DETAIL_CSS, json.dumps(secs, ensure_ascii=False), json.dumps(DETAIL_COLS), json.dumps(DETAIL_HEAD), DETAIL_JS))
    pg = _goto(html, 'detail'); pg.wait_for_function('window.REPORT'); rep = pg.evaluate('window.REPORT')
    pg.pdf(path=out_pdf, width='%spx' % (595 * 4 / 3), height='%spx' % (708 * 4 / 3), print_background=True, prefer_css_page_size=True)
    if rep['over']: raise RuntimeError('세부내역 한 묶음이 한 쪽을 넘음 : %s' % rep['over'])
    return rep
def detail_overlay_html(n):
    SL = slots(); W, H = SL['size']; s = {x['key']: x for x in SL['slots']['detail']}
    pn, ft = s['pageno'], s['footer']
    pages = ''.join('<div class="pg">%s%s</div>' % (_at(x1=pn['x1'], base=pn['base'], size=pn['size'], inner='<span style="color:#777">%d / %d</span>' % (i + 1, n), align='right'),
                                                     _at(x1=ft['x1'], base=ft['base'], size=ft['size'], inner=who_html(ft['size'], '#333333', '#111111'), align='right', extra='white-space:nowrap;font-weight:500')) for i in range(n))
    css = ('@page{size:%spt %spt;margin:0}html,body{margin:0;background:transparent;font-family:P;-webkit-print-color-adjust:exact;print-color-adjust:exact}'
           '.pg{position:relative;width:%spt;height:%spt;overflow:hidden;page-break-after:always}.o{position:absolute;line-height:1;white-space:nowrap}' % (W, H, W, H))
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>' % (fonts_css(), css, pages)

# ═══════════════ 표지 · 보장요약(지금 GA 양식 · ga_proposal 그대로) ═══════════════
def cover_summary_html():
    if GP.MOCK_MODE:
        return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s%s</style></head><body>%s</body></html>' % (GP._font_css(), GP.CSS, OV.page_css() + GP.MOCK_CSS, GP.p0_mock() + GP.p1_mock())
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>' % (GP._font_css(), GP.CSS, GP.p0() + GP.p1())

# ═══════════════ 묶기 ═══════════════
def title_of(pg): return pg.get_text(clip=fitz.Rect(185, 30, 450, 52)).strip()
def build(design_pdf, out_pdf=None, age=''):
    t0 = time.time(); os.makedirs(TMP, exist_ok=True)
    out_pdf = out_pdf or os.path.join(BASE, 'ga_output', GP.ascii_name(design_pdf) + '_GA2.pdf')
    os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)
    load(design_pdf, age)
    cf = CF(); tag = GP.ascii_name(design_pdf); warn = []
    # 1) 표지 · 보장요약
    p_cs = os.path.join(TMP, tag + '_cs.pdf'); _goto(cover_summary_html(), 'cs').pdf(path=p_cs, prefer_css_page_size=True, print_background=True)
    # 2) v41 틀 + 값 + 5열 표
    tpl = fitz.open(TPL); SL = slots(); order = SL['pages']
    p_ov = os.path.join(TMP, tag + '_ov.pdf'); _goto(overlay_html(), 'ov').pdf(path=p_ov, prefer_css_page_size=True, print_background=True)
    ov = fitz.open(p_ov); assert len(ov) == 5, len(ov)
    tp = fitz.open(); tp.insert_pdf(tpl, from_page=0, to_page=4)
    for i in range(5): tp[i].show_pdf_page(tp[i].rect, ov, i)
    for k, cols in (('brain', BRAIN_COLS), ('heart', HEART_COLS)):
        y0, ys = TBL_ROWS[k]; pts = [y0] + ys; hs = [round((pts[i + 1] - pts[i]) * 0.97, 2) for i in range(5)]; hh = pts[-1] - y0
        tb = render_snippet(table_html(cols, hh, hs), os.path.join(TMP, '%s_tbl_%s.pdf' % (tag, k)), 532.5, hh)
        tp[order.index(k)].show_pdf_page(fitz.Rect(31.5, y0, 564.0, pts[-1]), fitz.open(tb), 0)
    # 3) 새로 그리는 쪽
    pages = [page_journey(), page_surg(0), page_surg(1)]
    care_pages = {'support': lambda: page_care_support(cf), 'use': lambda: page_care_use(cf), 'none': page_care_none}
    pages += [care_pages[k]() for k in cf['pages']] + [page_check()]
    p_h = os.path.join(TMP, tag + '_html.pdf')
    fit, over = render_pages('<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (css(), ''.join(pages)), p_h, 'html')
    if over: warn.append('새 쪽 넘침 %s' % over)
    hd = fitz.open(p_h)
    for pg in hd:     # 로고 · 경고문 : 틀(암①)에서 그대로
        pg.show_pdf_page(fitz.Rect(30.5, 31.0, 186.0, 51.5), tpl, 0, clip=fitz.Rect(30.5, 31.0, 186.0, 51.5))
        pg.show_pdf_page(fitz.Rect(449.5, 33.0, 566.0, 50.0), tpl, 0, clip=fitz.Rect(449.5, 33.0, 566.0, 50.0))
    # 4) 세부내역
    p_d = os.path.join(TMP, tag + '_detail.pdf'); rep = render_detail(p_d); dc = fitz.open(p_d); n = len(dc)
    p_do = os.path.join(TMP, tag + '_detail_ov.pdf'); _goto(detail_overlay_html(n), 'dov').pdf(path=p_do, prefer_css_page_size=True, print_background=True); do = fitz.open(p_do)
    dt = fitz.open(); dsl = {x['key']: x for x in SL['slots']['detail']}; ct = dsl['content']
    for i in range(n):
        pg = dt.new_page(width=tpl[5].rect.width, height=tpl[5].rect.height)
        pg.show_pdf_page(pg.rect, tpl, 5); pg.show_pdf_page(fitz.Rect(0, ct['top'], 595, ct['top'] + ct['height']), dc, i); pg.show_pdf_page(pg.rect, do, i)
    # 5) 묶기 : 표지 · 요약 → 치료 여정 → 암① 암② 뇌 심 → 수술 ① ② → 간병 → 보장 점검 → 세부내역 → 안내사항
    out = fitz.open(); cs = fitz.open(p_cs)
    out.insert_pdf(cs); out.insert_pdf(hd, from_page=0, to_page=0); out.insert_pdf(tp, from_page=0, to_page=3)
    out.insert_pdf(hd, from_page=1, to_page=len(hd) - 1); out.insert_pdf(dt); out.insert_pdf(tp, from_page=4, to_page=4)
    dedupe_images(out); jpeg_big(out)
    out.save(out_pdf, garbage=3, deflate=True)
    # 점검 : 틀 쪽 제목이 그대로인가(글꼴 꼬임) · 글자층 오류
    chk = fitz.open(out_pdf); base_i = len(cs) + 1
    for j, k in enumerate(('ca1', 'ca2', 'brain', 'heart')):
        if title_of(chk[base_i + j]) != title_of(tpl[order.index(k)]): raise RuntimeError('틀 쪽 제목이 바뀜 : %s' % k)
    err = subprocess.run(['pdftotext', out_pdf, '-'], capture_output=True, text=True).stderr.strip() if shutil_which('pdftotext') else ''
    if err: warn.append('글자층 경고 : ' + err[:200])
    info = dict(design=os.path.basename(design_pdf), product=GP.PRODUCT, pages=len(chk), care=cf['pages'], detail_pages=n, warn=warn, sec=round(time.time() - t0, 1),
                riders=GP.NRID, fit=fit)
    log = os.path.splitext(out_pdf)[0] + '_log.txt'
    with open(log, 'w', encoding='utf-8') as f:
        f.write('원본 설계서 : %s\n상품 : %s\n보험료 : %s\n담보 %d건 · %d쪽 · 간병인 쪽 : %s · 세부내역 %d쪽 · %.1f초\n\n' % (info['design'], GP.PRODUCT, GP.PREMIUM, GP.NRID, info['pages'],
                ' + '.join({'support': '지원 가입자', 'use': '사용 가입자', 'none': '지원 · 사용 함께(둘 다 미가입)'}[k] for k in cf['pages']), n, info['sec']))
        f.write('[지면 경고] ' + (' / '.join(warn) if warn else '없음') + '\n\n[계산 로그 — 빈칸 · 0원의 이유]\n')
        for it in S.issues_grouped(): f.write('- [%s] %s — %s\n' % (it['구분'], it['담보'], it['사유']))
    return out_pdf, log, info
def shutil_which(x):
    import shutil; return shutil.which(x)

def calibrate():
    """K_BASE 재기 — Pretendard 글자를 top=100pt 에 놓았을 때 기준선이 어디 오는지(개발용)"""
    h = ('<!doctype html><html><head><meta charset="utf-8"><style>%s@page{size:300pt 300pt;margin:0}html,body{margin:0}.o{position:absolute;line-height:1;font-family:P;font-weight:800}</style></head>'
         '<body><div class="o" style="left:10pt;top:100pt;font-size:20pt">1,000</div></body></html>' % fonts_css())
    p = os.path.join(TMP, 'cal.pdf'); os.makedirs(TMP, exist_ok=True); render_snippet(h, p, 300, 300)
    sp = [s for b in fitz.open(p)[0].get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans']][0]
    return (sp['origin'][1] - 100) / 20

def main(argv):
    args = [a for a in argv if a.strip()]; age = ''
    if args and re.fullmatch(r'\d{1,3}세?', args[-1]): age = args.pop(); age = age if age.endswith('세') else age + '세'
    if not args: args = [os.path.join(BASE, 'ga_input')]
    files = []
    for a in args:
        if os.path.isdir(a): files += sorted(glob.glob(os.path.join(a, '*.pdf')) + glob.glob(os.path.join(a, '*.PDF')))
        elif a.lower().endswith('.pdf'): files.append(a)
    out_pdf = None
    if len(args) == 2 and args[0].lower().endswith('.pdf') and args[1].lower().endswith('.pdf') and not os.path.exists(args[1]):      # 설계서 1건 + 결과 파일 이름(이미 있는 파일이면 설계서 2건으로 본다 — 끌어다 놓은 설계서를 덮어쓰지 않게 · ga_proposal 과 같은 규칙)
        files, out_pdf = [args[0]], args[1]
    if not files: print('설계서 PDF 가 없습니다.'); return 1
    ok = 0
    for i, f in enumerate(files, 1):
        print('[%d/%d] %s' % (i, len(files), os.path.basename(f)), flush=True)
        try:
            o = out_pdf or os.path.join(BASE, 'ga_output', GP.ascii_name(f) + '_GA2.pdf')
            if not out_pdf and os.path.exists(o): o = os.path.join(BASE, 'ga_output', '%s_GA2_%s.pdf' % (GP.ascii_name(f), time.strftime('%H%M%S')))
            pdf, log, info = build(f, o, age)
            print('      → %s  (%d쪽 · 간병인 %s · 세부내역 %d쪽)%s' % (pdf, info['pages'], '+'.join(info['care']), info['detail_pages'], ('  ※ ' + ' / '.join(info['warn'])) if info['warn'] else ''), flush=True)
            ok += 1
        except Exception as ex:
            print('      ! 만들지 못했습니다 : %s: %s' % (type(ex).__name__, ex), flush=True)
    print('\n완료 %d / %d건' % (ok, len(files)))
    return 0 if ok == len(files) else 2

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
