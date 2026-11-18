# -*- coding: utf-8 -*-
"""메리츠 GA 스마트 제안서 v2(새 양식 · 2026-11-11 회의 → 2026-11-18 회의 반영) — 설계서 PDF 를 넣으면 새 양식 PDF 를 만든다.

  python ga_v2.py 설계서.pdf [결과.pdf] [나이]      # 한 건
  python ga_v2.py 폴더                             # 폴더 안 PDF 전부 → ga_output\\<이름>_GA2.pdf
  (GA_MASK=1 이면 피보험자 · 가계약번호 · 소속 · 컨설턴트 · 전화를 가린다 — 견본 · 사외 공유용)

쪽 구성(고객에게 넘겨 보여 주는 순서 · 2026-11-18 회의 : 치료 여정 · 보장 점검 · 체증형 시나리오 · 간병 보상 예시를 덜어 냄)
  표지 · 보장요약(지금 GA 양식 그대로 · ga_proposal) → 암 보장 ① ② · 뇌혈관 · 심장(v41 디자인 틀 + 값)
  → 주요수술 ① ②(수술 12개 · 수술명 옆 모든 병원 / 상급종합 금액 + 수술비 다섯 묶음 가입 여부) → 간병인(가입에 따라 아래 규칙)
  → 보장금액 세부내역(글씨 키움 · 쪽수 자동) → 안내사항(v41 틀)

간병인 쪽 고르는 규칙(소유자 2026-11-11)
  간병인지원(현물) 담보가 있으면 「간병인 지원」 쪽 · 간병인사용(금액) 담보가 있으면 「간병인 사용」 쪽(둘 다 있으면 두 쪽)
  · 둘 다 없으면 지원 표 + 사용 표를 한 쪽에 같이 보여 주는 「간병인 보장」 쪽 하나.

금액은 전부 ga_spec(= 계산 엔진 scen_engine.pay_lines)의 칸 값 그대로다 — 이 파일은 값을 계산하지 않고 그리기만 한다(CLAUDE.md 1 · 2).
체증형 수술비도 1회차(가입금액 기준) 금액만 적고 쪽 아래 「※ 체증형 … 더 큰 금액이 지급될 수 있습니다」 주석으로 알린다(2026-11-18 회의).
여기서 새로 더하는 것은 표시용 합(보상 예시 합계 · 재활 연 횟수 × 회당 금액 · 수술 카드 합계)뿐이고, 수술 카드 합계는 보장요약 칸 값과 같아야 한다(다르면 멈춘다).
"""
import os, sys, re, json, base64, copy, math, time, glob, atexit, pathlib, subprocess
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import fitz
import ga_proposal as GP, ga_spec as GS, ga_care as CARE, scen_engine as S, ga_overlay as OV, pipeline

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
_NOTO = None
def noto_css():
    """Noto Sans KR(family N · SIL OFL · ga_assets/noto) — GA 시안 v41 · v8 본문 글꼴. 간병인 쪽과 틀 위 주석 · 고친 문구에 쓴다(2026-11-18).
    한글 11,172자 + 영문 · 숫자는 korean 묶음에, 「」 · ※ 는 작은 조각(109 · 111)에 있다. 없는 글자는 Pretendard(P)로 넘어간다"""
    global _NOTO
    if _NOTO is None:
        d = os.path.join(BASE, 'ga_assets', 'noto'); f = lambda n: _b64(os.path.join(d, 'noto-sans-kr-%s-normal.woff2' % n))
        _NOTO = ''.join("@font-face{font-family:N;font-weight:%d;src:url(data:font/woff2;base64,%s)}" % (w, f('korean-%d' % w)) for w in (400, 500, 700, 800))
        _NOTO += ''.join("@font-face{font-family:N;font-weight:%d;src:url(data:font/woff2;base64,%s);unicode-range:%s}" % (w, f(n), r)
                         for n, r in (('109-400', 'U+300C-300D'), ('111-400', 'U+203B')) for w in (400, 500, 700, 800))      # 기호 조각은 굵기마다 같은 파일(굵기별 얼굴이 있어야 그 굵기에서 골라진다)
    return _NOTO
_PW = {}
CHROME_CAND = (r'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe', r'%ProgramFiles%\Microsoft\Edge\Application\msedge.exe',
               r'%ProgramFiles%\Google\Chrome\Application\chrome.exe', r'%LocalAppData%\Google\Chrome\Application\chrome.exe',
               '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser')
def _alive():
    try: return _PW['b'].is_connected() and not _PW['pg'].is_closed()
    except Exception: return False
def _page():
    """크로뮴 하나를 띄워 두고 계속 쓴다(설계서 여러 건을 돌릴 때 빠르게). 죽어 있으면(메모리 부족 · 프로세스 종료 등) 닫고 새로 띄운다"""
    if 'pg' in _PW and not _alive(): close_browser()
    if 'pg' not in _PW:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        try:
            exe = os.environ.get('GA_CHROMIUM') or ('/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') and not os.path.isdir('/opt/pw-browsers/chromium') else None)   # ga_proposal.render 와 같은 규칙
            try:
                b = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
            except Exception:      # playwright 크로뮴을 못 받은 PC(폐쇄망) — 깔려 있는 Edge · Chrome 으로(GA_CHROMIUM 을 안 넣었을 때)
                cand = [c for c in (os.path.expandvars(x) for x in CHROME_CAND) if os.path.isfile(c)]
                if exe or not cand: raise
                b = pw.chromium.launch(executable_path=cand[0])
            pg = b.new_page(viewport={'width': 794, 'height': 1123}); pg.set_default_timeout(120000)      # 한 동작 2분 넘으면 오류(멈춘 채 붙잡지 않게)
        except Exception:
            try: pw.stop()                                    # 띄우다 실패해도 playwright 를 닫아 둔다(다음 건이 다시 띄울 수 있게)
            except Exception: pass
            raise
        _PW.update(pw=pw, b=b, pg=pg)
        if not _PW.get('atexit'): atexit.register(close_browser); _PW['atexit'] = True
    return _PW['pg']
def close_browser():
    """띄워 둔 크로뮴을 닫는다(끝날 때 · 서버 작업 스레드 안에서). 다른 스레드에서 불려 실패해도 프로그램 종료를 막지 않는다"""
    pw = _PW.pop('pw', None); b = _PW.pop('b', None); _PW.pop('pg', None)
    try:
        if b: b.close()
        if pw: pw.stop()
    except Exception:
        pass
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
FIT_JS = """(gap)=>{const P=[...document.querySelectorAll('.page')].map((pg,i)=>{
  const c=pg.querySelector('.cnt'), ft=pg.querySelector('.ft'); if(!c||!ft) return {i,z:1};
  const W=pg.clientWidth-parseFloat(getComputedStyle(pg).paddingLeft)-parseFloat(getComputedStyle(pg).paddingRight);
  const top=c.getBoundingClientRect().top, avail=ft.getBoundingClientRect().top-top-gap;
  const set=z=>{c.style.zoom=z;c.style.width=(W/z)+'px'};
  const fits=z=>{set(z);let wide=false;c.querySelectorAll('table,.cards,.g2,.need,.cv-need,.cv-steps,.cv-two').forEach(t=>{if(t.scrollWidth>t.clientWidth+1||t.getBoundingClientRect().right>c.getBoundingClientRect().right+1)wide=true});return !wide&&c.getBoundingClientRect().height<=avail};
  const zmax=parseFloat(pg.dataset.zmax||'1.6');
  let lo=1,hi=zmax; if(!fits(1)){lo=0.7;hi=1} for(let k=0;k<14&&hi>lo;k++){const m=(lo+hi)/2; if(fits(m))lo=m; else hi=m}
  set(lo); return {i,z:lo,c,avail,set,g:pg.dataset.zg||''}});
  const G={}; P.forEach(p=>{if(p.g)(G[p.g]=G[p.g]||[]).push(p)});
  Object.values(G).forEach(a=>{const z=Math.min(...a.map(p=>p.z)); a.forEach(p=>{p.z=z;p.set(z)})});
  return P.map(p=>[p.i+1,+p.z.toFixed(3),p.c?Math.round(p.c.getBoundingClientRect().height):0,p.c?Math.round(p.avail):0])}"""
def render_pages(html, out_pdf, name='pages'):
    """A4 쪽들(.page) — 쪽마다 본문(.cnt)을 머리 아래 ~ 바닥글 위 빈 곳에 맞춘다(넘치면 0.7배까지 줄이고, 남으면 data-zmax 배까지 키움).
    data-zg 가 같은 쪽끼리는 같은 배율(작은 쪽에 맞춤) — 주요수술 ① ② 카드 크기가 서로 달라지지 않게(2026-11-18)"""
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
NOTICE_ADD_H = 122.0
NOTICE_ADD_HTML = ('<!doctype html><html><head><meta charset="utf-8"><style>%(F)s'
    '@page{size:532.5pt 122pt;margin:0}*{box-sizing:border-box}html,body{margin:0;width:532.5pt;height:122pt;overflow:hidden;font-family:P;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all}'
    '.b{border:.8pt solid #E3E3E8;border-radius:7pt;background:#FAFAFB;padding:8pt 11pt}.b b{display:block;font-size:8.6pt;color:#1F1F22;margin:0 0 2.5pt}.b p{margin:0 0 6pt;font-size:7.3pt;line-height:1.5;color:#55555C}.b p:last-child{margin:0}'
    '</style></head><body><div class="b"><b>예시 금액 안내</b><p>각 쪽 「보장(보상) 예시」 는 이 설계의 보장금액을 단순 합산한 예시로, 실제 진단 · 치료 내용과 약관상 지급조건에 따라 지급 여부와 금액이 달라집니다. '
    '일부 특약은 가입 후 일정 기간(예 : 1년) 안에는 가입금액의 일부(예 : 50%%)만 지급합니다. 수술비 금액은 모두 1회차(가입금액) 기준이며, 체증형 수술비는 같은 종(같은 특약) 수술을 다시 받을 때 회차에 따라 지급률이 커져(약관 지급금액표) 예시 금액보다 더 큰 금액이 지급될 수 있습니다.</p>'
    '<b>추가 출처</b><p>질병관리청 「2023 심뇌혈관질환 발생통계」(2025.12.31) — 재발 심근경색 발생 건수 · 1년 / 30일 치명률 · 대한심혈관중재학회 회복 · 관리 가이드북 배포 보도(2026.11.10) — 재발 위험 시기<br>'
    'Ferns SP 외, Stroke 2009(코일색전술 8,161건) — 코일색전술 후 재개통 비율 · 보건복지부 소개 서울대 사적 간병비 추정(2022년) — 국민 사적 간병비(연간)</p></div></body></html>')
_NH, _NA = NEED_HEART_HTML, NOTICE_ADD_HTML
del NEED_HEART_HTML, NOTICE_ADD_HTML
def _with_fonts(h): return h.replace('%(F)s', fonts_css(), 1).replace('%%', '%')
def need_heart_html(): return _with_fonts(_NH)       # 심장 쪽 맨 위 「다시 찾아오는 심근경색」(틀에 굳힌다)
def notice_add_html(): return _with_fonts(_NA)       # 안내사항 아래 「예시 금액 안내 · 추가 출처」(틀에 굳힌다)

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
    EXTRA['sgpaid'] = {'질병': set(), '상해': set()}                                 # 수술 12개 가운데 어느 하나에라도 지급되는 묶음(원인별) — 「해당 없음」 과 「미가입」 을 가른다
    for n in GS.DZ_ORDER:
        EXTRA['sgpaid'][cause_of(n)].update(grp_of(full, cause_of(n)) for full, _, _ in surg_rows(n))
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
# 체증형 수술비 : 지면 금액은 1회차(가입금액 기준)만 적는다. 「매 회 1회차 ~ 최대」 두 줄 · 카드 「최대」 금액(v8.95 · v8.96)은
# "헷갈린다" 는 GA 의견으로 뺐고(2026-11-18 회의), 쪽 아래 주석(ESC_NOTE)으로만 알린다.
ESC_NOTE = '※ 체증형 수술비 가입 시, 상기 예시 금액보다 더 큰 금액이 지급될 수 있습니다.'
def tsum(*keys):
    vs = [VX(k) for k in keys]; ns = [x for x in vs if isnum(x)]
    return float(sum(ns)) if ns else None

def fmt(v, unit='만'):
    """(숫자 글자, 단위) — None 은 미가입. 「1억」 처럼 만 단위가 없으면 단위를 붙이지 않는다"""
    if v is None: return None, ''
    if isinstance(v, str): return v, ''
    t = won(v); return t, ('' if t.endswith('억') else unit)

# ═══════════════ 간병인 가입 상태(설계서 담보 이름 · 가입금액만 읽는다 — ga_care) ═══════════════
def span(name):
    """담보가 맡는 입원 날짜(1회 입원 기준) — 담보 이름의 기간 그대로. 「181일이상」 = 180일을 넘긴 날부터 1회 입원당 185일 한도(2610 간병인지원 · 사용 181일이상 특약 제2조 공통 · tool_body 케355 · 케356 · 케361 · 통166 · 통172 …),
    「(1일이상 N일한도)」 = 1~N일(1~30일 · 1~180일). 이름에 기간이 없으면 1~180일로 본다"""
    n = _ns(name)
    if '181일' in n: return (181, 365)
    m = re.search(r'(\d+)일한도', n)
    return (1, int(m.group(1))) if m else (1, 180)
def care_flags():
    """간병인 지원 · 사용 표(1~180일 / 181일 이상)의 칸 값 — 설계서 담보 이름 · 금액란만 읽는다(ga_care 와 같은 기준).
    1~180일 열은 보장요약 칸(ga_care.cells)과 같은 값이고, 181일 이상 열은 이름에 「181일이상」 이 든 담보를 같은 규칙으로 읽는다.
    값 : SEND(간병인 지원) · 숫자(만원/1일 · 0 은 가입했지만 그 일당이 없음) · None(미가입)"""
    rs = CARE.norm(GP.RID); dz = CARE._dz(rs)      # 질병입원일당만(상해 입원일당은 칸에 없다 — ga_care 와 같은 기준)
    is181 = lambda r: '181일' in r['name']
    def names(L): return [r['name'] for r in L]
    amt = lambda L: (sum(r['man'] for r in L) if L else None)
    def nurse(add, sp):      # 간호 · 간병통합서비스 병동 1일 = 사용추가보장 + (Ⅰ형) 간병인 미사용 입원일당(ga_care.nurse_total 과 같은 식)
        return None if not add and not sp else sum(r['man'] for r in add) + sum(CARE.daily(r) for r in sp)
    sup180 = CARE.support(rs); supnh = CARE.support_nh(rs); nadd180 = CARE.nurse_add(rs)
    sup181 = [r for r in dz if '간병인지원' in r['name'] and is181(r) and '간호·간병' not in r['name']]
    nadd181 = [r for r in dz if '간병인지원' in r['name'] and is181(r) and '간호·간병통합서비스 사용추가보장' in r['name']]
    use = {k: CARE.use(rs, k) for k in ('gen', 'nh', 'nurse')}
    use181 = [r for r in dz if '간병인사용' in r['name'] and is181(r) and '간호·간병' not in r['name'] and '(요양병원)' not in r['name']]
    usenh181 = [r for r in rs if '간병인사용' in r['name'] and '요양성특정질병입원일당' in r['name'] and is181(r)]
    unurse181 = [r for r in dz if '간호·간병통합서비스' in r['name'] and '간병인지원' not in r['name'] and is181(r)]
    sups = sup180 + sup181 + supnh
    f = dict(sup180=sup180, sup181=sup181, supnh=supnh,
             unused180=(sum(CARE.daily(r) for r in sup180) if sup180 else None), unused181=(sum(CARE.daily(r) for r in sup181) if sup181 else None),
             nurse180=nurse(nadd180, sup180), nurse181=nurse(nadd181, sup181),
             use_gen=amt(use['gen']), use_nh=amt(use['nh']), use_nurse=amt(use['nurse']), use181=amt(use181), usenh181=amt(usenh181), use_nurse181=amt(unurse181),
             lim_sup=max([span(r['name'])[1] for r in sup180] or [0]), lim_gen=max([span(r['name'])[1] for r in use['gen']] or [0]), lim_nh=max([span(r['name'])[1] for r in use['nh']] or [0]),
             type1=any('(Ⅰ)' in r['name'] for r in sups), type6=any('(Ⅵ)' in r['name'] for r in sups),
             use_esc=any('체증' in r['name'] for r in use['gen'] + use['nh'] + use181 + usenh181), use_plus=any('(plus)' in r['name'] for r in use['gen'] + use181),
             sup_names=names(sup180 + sup181 + supnh + nadd180 + nadd181), use_names=names(use['gen'] + use['nh'] + use['nurse'] + use181 + usenh181 + unurse181))
    assert f['nurse180'] == CARE.nurse_total(rs)[0] and f['unused180'] == CARE.unused(rs)[0]      # 1~180일 열 = 보장요약 칸
    f['has_sup'] = bool(sup180 or sup181 or supnh or nadd180 or nadd181)
    f['has_use'] = any(f[k] for k in ('use_gen', 'use_nh', 'use181', 'usenh181'))      # 「간병인사용」 담보로만 정한다(간호 · 간병통합서비스 입원일당만 있으면 간병인사용일당 가입이 아니다 → 함께 쪽 · 그 금액은 그 쪽 표에 적는다)
    f['inj_only'] = not f['has_sup'] and not f['has_use'] and any(re.search(r'간병인(지원|사용)', r['name']) and '상해입원일당' in r['name'] for r in rs)      # 상해 입원 간병인 담보만(표는 질병 입원 기준)
    f['pages'] = (['support'] if f['has_sup'] else []) + (['use'] if f['has_use'] else []) or ['none']      # 둘 다 없으면 지원 표 + 사용 표 한 쪽
    return f, [], []
def CF(): return EXTRA['care'][0]

# ═══════════════ v41 틀 위에 값 얹기 ═══════════════
_SL = None
def slots():
    global _SL
    if _SL is None: _SL = json.load(open(SLOTS, encoding='utf-8'))
    return _SL
K_BASE = 0.8125       # Pretendard : 글자 크기 1 에 대한 「상자 위 → 기준선」 거리(line-height 1 일 때) — 아래 calibrate() 로 잰 값
K_N = 0.8875          # Noto Sans KR 의 같은 값(calibrate('N', 400))
def _at(cx=None, x0=None, x1=None, base=0, size=10, inner='', align='center', extra='', k=K_BASE):
    top = base - k * size
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
ESC_AT = {'ca1': (801.0, 8.49), 'brain': (783.0, 7.58), 'heart': (790.5, 7.36)}      # 체증형 주석 자리(기준선 · 글자 크기 pt) — 틀의 앞 주석 줄 바로 아래
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
            elif k == 'label':      # 틀에서 지운 고정 문구를 GA 시안 v8 글자로 다시(뇌혈관 「뇌졸중 재발 비율」 → 「뇌졸중 재발률」)
                o.append(_at(x0=s['x0'], base=s['base'], size=s['size'], inner='<span style="color:%s">%s</span>' % (s['color'], s['text']), align='left', extra='font-family:N,P;font-weight:700;letter-spacing:0', k=K_N))
            elif k == 'note':
                t = (dx_note('p3.dx.뇌혈관', 'p3.dx.뇌졸중') if pk == 'brain' else dx_note('p3.dx.허혈성심장', 'p1.bh.dx.급성심근경색')) if s['key'] == 'dx_note' else ((GP.HEAD.get('no') or '-') + ')')
                if t: o.append(_at(x0=s['x0'], base=s['base'], size=s['size'], inner='<span style="color:%s">%s</span>' % (s['color'], t), align='left', extra='font-weight:500;white-space:nowrap'))
            elif k == 'life':
                t = life_note('p3.b1.first' if pk == 'brain' else 'p3.h1.first')
                if t: o.append(_at(x1=s['x1'], base=s['top'] + 7.0, size=6.6, inner='<span style="color:#6B6B73">%s</span>' % t, align='right', extra='white-space:nowrap'))
            elif k == 'footer':
                o.append(_at(x1=s['x1'], base=s['base'], size=s['size'], inner=who_html(s['size']), align='right', extra='white-space:nowrap;font-weight:500'))
        if pk in ESC_AT:      # 암 ① · 뇌혈관 · 심장 아래 체증형 주석(GA 시안 v8 자리 · 2026-11-18)
            b, z = ESC_AT[pk]; o.append(_at(x0=31.17, base=b, size=z, inner='<span style="color:#777777">%s</span>' % ESC_NOTE, align='left', extra='font-family:N,P;font-weight:400;letter-spacing:0', k=K_N))
        pages.append('<div class="pg">%s</div>' % ''.join(o))
    css = ('@page{size:%spt %spt;margin:0}html,body{margin:0;background:transparent;font-family:P;-webkit-print-color-adjust:exact;print-color-adjust:exact}'
           '.pg{position:relative;width:%spt;height:%spt;overflow:hidden;page-break-after:always}.o{position:absolute;line-height:1;white-space:nowrap;font-variant-numeric:tabular-nums;letter-spacing:-.15pt}' % (W, H, W, H))
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s%s</style></head><body>%s</body></html>' % (fonts_css(), noto_css(), css, ''.join(pages))

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
    if CSS is None: CSS = fonts_css() + noto_css() + open(os.path.join(V2, 'v2.css'), encoding='utf-8').read()
    return CSS
def head(title): return '<div class="hd"><span class="ttl">%s</span></div>' % title
def foot(note): return '<div class="ft"><span>%s</span><span class="who">%s</span></div>' % (note, who_html())
def page(title, body, note, attrs='', cls=''): return '<div class="page%s"%s>%s<div class="cnt">%s</div>%s</div>' % (cls, attrs, head(title), body, foot(note))

# ── 주요수술 ① ② — 수술명 옆 금액 + 수술비 다섯 묶음 가입 여부(2026-11-18 회의) ──
# 전에는 카드마다 지급 특약을 줄줄이 적어 설계마다 줄 수 · 글씨 크기가 달라졌다(많으면 깨알, 적으면 큼직). 이제 카드 모양을 고정한다 :
# 수술명 옆에 「모든 병원 / 상급종합」 금액(가입 수술비 합 · 1회차 기준), 아래에 수술비 다섯 묶음의 가입 / 해당 없음 / 미가입. 특약별 금액은 뒤쪽 세부내역에 있다.
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
def eff_name(n, no=None):
    """「┗ 수술비[상해2종]」 처럼 부모 특약 아래 세부 줄로 실린 담보는 부모 이름(설계서 읽기의 via)을 앞에 붙여 읽는다 — 1-5종 · 1-7종 판정용"""
    if not (n or '').lstrip().startswith('┗'): return n
    r = next((r for r in GP.RID if no is not None and r.get('no') == no), None) or next((r for r in GP.RID if r['name'] == n), None)
    return ((r or {}).get('via') or '') + ' ' + n.replace('┗', '').strip()
def rid_names(): return [eff_name(r['name'], r.get('no')) for r in GP.RID if (r.get('man') or 0) > 0]
def _ns(x): return re.sub(r'\s+', '', x or '')
# 수술비 다섯 묶음 — 특약 이름으로만 나눈다(금액 · 지급 여부는 엔진 값 그대로). 질병 수술 11개와 골절(상해)은 묶음 이름이 다르다.
SG_DZ = (('g1', '질병수술비'), ('s15', '1-5종 수술비'), ('s17', '1-7종 수술비'), ('s131', '130 · 131대 질병수술비'), ('etc', '그 외 수술 · 치료비'))
SG_INJ = (('g1', '상해수술비'), ('s15', '1-5종 수술비'), ('s17', '1-7종 수술비'), ('frac', '골절 진단 · 수술비'), ('etc', '그 외 수술 · 치료비'))
# 수술 급부를 「수술(1-5종)」 항목(수술비Ⅱ(1-5종)과 같은 【1-5종 수술분류표Ⅱ】 의 종별 정액)으로 주는 통합치료비 — 1-5종 묶음에 넣는다(2026-11-18 회의 · 약관 지급금액표 확인).
# 암 통합치료비 · 특정순환계질환 통합치료비처럼 수술 항목에 종 구분이 없는 것은 넣지 않는다(이름을 하나씩 적는다)
ITC_15 = re.compile(r'질병통합치료비|상해통합치료비|암전후관련특정질환및양성신생물통합치료비|특정순환계질환\(주요손상및질환\)통합치료비')
def cause_of(name): return '상해' if name == '골절진단' else '질병'       # 이 수술의 원인(골절만 상해) — 1-5종 · 1-7종은 질병 · 상해를 따로 가입한다
def grp_of(n, cause):
    """특약 이름 → 묶음. 질병수술비 묶음 = 질병수술비 · (특정○대질병 제외) · 종합병원 · 상급종합병원 질병수술비(상해도 같은 식).
    심한상해수술비(신경 · 장기손상 한정) · 32대질병관혈수술비 · 신수술비 · 특정 수술비 · 전신마취치료비 등은 「그 외」"""
    m = _ns(n)
    if '1-5종' in m or ITC_15.search(m): return 's15'
    if '1-7종' in m: return 's17'
    if re.search(r'13[01]대', m): return 's131' if cause == '질병' else 'etc'
    if cause == '상해' and '골절' in m: return 'frac'
    if re.search(r'(질병|상해)수술비', m) and '심한상해' not in m: return 'g1'
    return 'etc'
def surg_rows(name):
    """수술 하나에 지급되는 특약 — [(특약 이름(부모 이름 포함), 모든 병원 금액, 상급종합 금액)]. 금액은 ga_spec 칸(p1.dz · 같은 사례 상급종합)의 지급 줄 그대로(1회차)"""
    A = {}; order = []
    for i, L in ((1, LN('p1.dz.' + name)), (2, EXTRA['dzup.' + name][1])):
        for l in L:
            a = GS.counts(l, 'first')
            if not a: continue
            if l['name'] not in A: A[l['name']] = [l, 0.0, 0.0]; order.append(l['name'])
            A[l['name']][i] += a
    return [(eff_name(n, A[n][0].get('no')), A[n][1], A[n][2]) for n in order]
def sg_have(g, cause):
    """이 설계에 그 묶음의 특약이 있는가 — 12개 수술 가운데 어느 하나에라도 지급되는 특약이 있거나, 1-5종 · 1-7종은 이름에 그 글자가 있는 특약(같은 원인)"""
    if g in EXTRA['sgpaid'][cause]: return True
    inj = lambda n: bool(re.search(r'상해|골절|화상|외상', n))      # 특약 원인 — 질병 카드에는 질병 특약, 골절 카드에는 상해 특약만
    for n in rid_names():
        if inj(n) != (cause == '상해') or not re.search(r'수술|통합치료비', n): continue      # 수술 관련 특약만(진단비 · 입원일당 등은 묶음에 넣지 않는다)
        if grp_of(n, cause) == g: return True
    return False
def sg_state(name):
    """(원인, [(묶음 이름, 상태, 묶음 값)], 모든 병원 합, 상급종합 합). 상태 : on 가입(이 수술에 지급) · up 상급종합병원에서만 지급 · na 가입했지만 이 수술 예시에는 지급 없음 · no 미가입"""
    cause = cause_of(name); spec = SG_INJ if cause == '상해' else SG_DZ
    G = {g: dict(a=0.0, u=0.0, esc=False, fetus=False) for g, _ in spec}
    for full, a, u in surg_rows(name):
        x = G[grp_of(full, cause)]; x['a'] += a; x['u'] += u; x['esc'] |= '체증' in full; x['fetus'] |= '태아고급형' in full
    rows = [(lab, 'on' if G[g]['a'] > 0 else ('up' if G[g]['u'] > 0 else ('na' if sg_have(g, cause) else 'no')), G[g]) for g, lab in spec]
    return cause, rows, sum(x['a'] for x in G.values()), sum(x['u'] for x in G.values())
SG_TXT = {'on': '가입', 'up': '가입', 'na': '해당 없음', 'no': '미가입'}
def card(name):
    proc, kcd = GS.GA_DZ[name][0], GS.GA_DZ[name][1]
    cause, rows, ta, tu = sg_state(name)
    want = V('p1.dz.' + name)
    if isnum(want) and abs(ta - want) > 0.01: raise RuntimeError('수술 카드 합계(%s)가 보장요약 칸(%s)과 다름 : %s' % (ta, want, name))
    none = ta <= 0 and tu <= 0
    amt = lambda v: '<span class="na">미가입</span>' if none else '%s<small>만</small>' % won(v)
    rs = ''
    for lab, st, x in rows:
        tag = (' <i class="cz">체증형</i>' if x['esc'] else '') + (' <i class="cz b">태아고급형</i>' if x['fetus'] else '')      # 태아고급형 수술비(1-7종)는 분류표 · 제외 질병이 달라 이름을 밝힌다(소유자 2026-11-13)
        if st == 'on':      # 가입 · 지급 → 금액(모든 병원 · 상급종합에서 더 나오면 옆에 작게 · 2026-11-18 소유자)
            val = '%s만' % won(x['a']) + ((' <em>상급종합 %s만</em>' % won(x['u'])) if x['u'] > x['a'] + 0.01 else '')
        elif st == 'up': val = '<em>상급종합</em> %s만' % won(x['u'])
        else: val = SG_TXT[st]
        rs += '<div class="sg %s"><span>%s%s</span><b>%s</b></div>' % (st, lab, tag, val)
    sex = DZ_SEX.get(name)
    chips = kcd_chip(kcd) + ((' <span class="chip %s">%s</span>' % ('m' if sex == '남성' else 'f', sex)) if sex else '')
    return ('<div class="card"><div class="ch">%s<div class="cn"><div class="nm">%s</div><div class="op">%s</div></div>'
            '<div class="ca"><div><span>모든 병원</span><b class="num">%s</b></div><div class="up"><span>상급종합</span><b class="num">%s</b></div></div></div>'
            '<div class="ck">%s</div><div class="sgs">%s</div></div>') % (ico(DZ_ICON[name], 50), name.replace('골절진단', '골절'), proc, amt(ta), amt(tu), chips, rs)
NEED_SURG = ('<div class="need"><div><div class="k">연간 주요수술 건수</div><div class="v">215<small>만건</small></div><div class="s">전년 대비 4.8% 증가</div></div>'
             '<div><div class="k">수술 1건당 평균 진료비</div><div class="v">496<small>만</small></div><div class="s">전년 대비 9.5% 상승</div></div>'
             '<div><div class="k">수술 진료비 증가</div><div class="v">14.7<small>%</small></div><div class="s">전년 대비 · 총 10조 6,738억</div></div></div>'
             '<div class="src">[출처: 국민건강보험공단 2025년 주요수술 통계연보]</div>')
SG_GUIDE = ('<div class="note" style="margin:0 0 7px;font-size:9px">수술명 옆 금액은 가입한 수술비를 모두 더한 금액입니다(「상급종합」 은 같은 수술을 상급종합병원에서 받았을 때). '
            '아래 다섯 줄은 수술비 묶음별 금액(가입하지 않은 묶음은 「미가입」)이고, 특약별 금액(모든 병원 기준)은 뒤쪽 「보장금액 세부내역」 에 있습니다. 상급종합 금액에는 종합병원 · 상급종합병원 질병(상해)수술비가 더해져 있습니다.</div>')
SG_LEGEND = ('<div class="box sgl"><h4>수술비 묶음은 이렇게 나눴어요</h4><div class="sgl2">'
             '<div><b>질병수술비 · 상해수술비</b>질병(상해)수술비와 종합병원 · 상급종합병원 질병(상해)수술비</div>'
             '<div><b>1-5종 · 1-7종 수술비</b>수술 종류(종)에 따라 금액이 정해지는 수술비 · 통합치료비의 <span style="white-space:nowrap">수술(1-5종)</span> 항목</div>'
             '<div><b>130 · 131대 질병수술비</b>약관이 정한 질병으로 수술했을 때 나오는 수술비</div>'
             '<div><b>골절 진단 · 수술비</b>골절 진단비 · 골절 수술비(골절 칸에만 있음)</div>'
             '<div><b>그 외 수술 · 치료비</b>위 묶음에 들지 않는 수술 · 치료 관련 특약</div>'
             '<div style="grid-column:1/-1"><b>표시</b><i class="k on">○○만</i> 이 수술에 나오는 금액(1회차) <i class="k na">해당 없음</i> 가입했지만 이 수술 예시에는 지급 없음 <i class="k no">미가입</i> 설계에 없음</div>'
             '</div></div>')
def page_surg(i):
    names = GS.DZ_ORDER[i * 6:(i + 1) * 6]
    body = ((NEED_SURG if i == 0 else '') + '<div class="tag">다빈도 수술별 보장금액 %s</div><div class="sec"></div>' % ('①' if i == 0 else '②') + (SG_GUIDE if i == 0 else '')
            + '<div class="cards">' + ''.join(card(n) for n in names) + '</div>' + (SG_LEGEND if i == 1 else '')
            + '<div class="note" style="margin-top:6px;font-size:8.6px">%s</div>' % ESC_NOTE)
    return page('주요수술 보장 %s' % ('①' if i == 0 else '②'), body, '※ 금액은 이 설계의 특약별 가입금액 기준입니다. 수술명 옆 질병코드는 사례 기준입니다.', ' data-zg="surg" data-zmax="1.04"')

# ── 주요수술 「특약 전부」 판(GA_V2_SURG=all · 2026-11-18 회의 「수술비를 많이 넣은 설계로 다 나온 버전을 보자」 · 비교용) ──
# 다섯 묶음 대신 카드마다 그 수술에 지급되는 특약을 하나씩 모두 적는다(「그 외」 로 묶지 않음). 글씨 크기는 고정하고, 카드가 길어져
# 한 쪽에 안 들어가면 쪽을 늘린다(주요수술 ① ② ③ …) — 카드 높이를 실제로 재서(Chromium) 나눈다.
SURG_MODE = os.environ.get('GA_V2_SURG', 'group')
GRP_ORDER = ['g1', 's15', 's17', 's131', 'frac', 'etc']
def surg_lines(name):
    """수술 하나에 지급되는 특약 — [(특약 이름(부모 이름 포함), 지급 줄, 모든 병원 금액, 상급종합 금액)] · 묶음 순서로"""
    A = {}; order = []
    for i, L in ((2, LN('p1.dz.' + name)), (3, EXTRA['dzup.' + name][1])):
        for l in L:
            a = GS.counts(l, 'first')
            if not a: continue
            if l['name'] not in A: A[l['name']] = [eff_name(l['name'], l.get('no')), l, 0.0, 0.0]; order.append(l['name'])
            A[l['name']][i] += a
    cause = cause_of(name); rows = [tuple(A[n]) for n in order]
    rows.sort(key=lambda r: GRP_ORDER.index(grp_of(r[0], cause)))
    return rows
def rider_label(full, l):
    """카드 줄 이름 — 갱신 · 가입형 꼬리표를 떼고 1-5종 · 1-7종은 「1-5종 수술비 [질병2종]」 꼴로(체증형은 옆 꼬리표)"""
    s = re.sub(r'\s+', ' ', full).strip()
    s = re.sub(r'^\(\d+년갱신\)\s*', '', s); s = re.sub(r'^갱신형\s*', '', s)
    s = re.sub(r'\s*\((건강가입|통합간편가입|편한가입|31간편가입|간편가입)\)', '', s).strip()
    if '1-5종' in s or '1-7종' in s:
        g = (re.search(r'\[(?:질병|상해)(\d종)\]', s) or [None, ''])[1] or GP.line_note(l); cause = '상해' if '상해' in s else '질병'
        if '태아고급형' in s: return '태아고급형 수술비(1-7종) [%s%s]' % (cause, g)
        return '%s 수술비 [%s%s]' % ('1-5종' if '1-5종' in s else '1-7종', cause, g)
    s = re.sub(r'\s*\((25%)?체증형\)', '', s)
    return s.replace('131대질병수술비', '131대 질병수술비').replace('130대질병수술비', '130대 질병수술비')
def card_all(name):
    proc, kcd = GS.GA_DZ[name][0], GS.GA_DZ[name][1]
    rows = surg_lines(name); ta = sum(r[2] for r in rows); tu = sum(r[3] for r in rows)
    want = V('p1.dz.' + name)
    if isnum(want) and abs(ta - want) > 0.01: raise RuntimeError('수술 카드 합계(%s)가 보장요약 칸(%s)과 다름 : %s' % (ta, want, name))
    none = not rows
    amt = lambda v: '<span class="na">미가입</span>' if none else '%s<small>만</small>' % won(v)
    def m(v): return '<span class="dash">–</span>' if v <= 0 else '%s만' % won(v)
    rs = ''
    for full, l, a, u in rows:
        tag = (' <i class="cz">체증형</i>' if '체증' in full else '') + (' <i class="cz b">태아고급형</i>' if '태아고급형' in full else '')
        rs += '<tr><td>%s%s</td><td>%s</td><td>%s</td></tr>' % (_esc(rider_label(full, l)), tag, m(a), m(u))
    if none: rs = '<tr><td colspan="3" class="nn">이 설계에는 이 수술에 나오는 수술비가 없습니다</td></tr>'
    sex = DZ_SEX.get(name)
    chips = kcd_chip(kcd) + ((' <span class="chip %s">%s</span>' % ('m' if sex == '남성' else 'f', sex)) if sex else '')
    return ('<div class="card"><div class="ch">%s<div class="cn"><div class="nm">%s</div><div class="op">%s</div></div>'
            '<div class="ca"><div><span>모든 병원</span><b class="num">%s</b></div><div class="up"><span>상급종합</span><b class="num">%s</b></div></div></div>'
            '<div class="ck">%s</div><table class="rl"><tr><th>보장(특약)</th><th>모든 병원</th><th>상급종합</th></tr>%s</table></div>') % (
            ico(DZ_ICON[name], 46), name.replace('골절진단', '골절'), proc, amt(ta), amt(tu), chips, rs)
SG_GUIDE_ALL = ('<div class="note" style="margin:0 0 7px;font-size:9px">수술명 옆 금액은 가입한 수술비를 모두 더한 금액입니다(「상급종합」 은 같은 수술을 상급종합병원에서 받았을 때). '
                '아래 표는 그 수술에 나오는 특약과 특약별 금액(1회차 기준)이며, 「모든 병원」 칸의 「–」 는 종합병원 · 상급종합병원처럼 병원 종류에 따라 나오는 보장입니다.</div>')
_MEASURE_JS = """()=>{const q=s=>document.querySelector(s);
  const av=id=>{const pg=q(id),c=pg.querySelector('.cards'),ft=pg.querySelector('.ft'),nt=pg.querySelector('.note.end');
    return ft.getBoundingClientRect().top-c.getBoundingClientRect().top-nt.getBoundingClientRect().height-parseFloat(getComputedStyle(nt).marginTop)-24};
  return {h:[...document.querySelectorAll('#pm .card')].map(c=>c.getBoundingClientRect().height),a1:av('#p1'),a2:av('#p2'),gap:parseFloat(getComputedStyle(q('#pm .cards')).rowGap)}}"""
def page_surg_all():
    names = GS.DZ_ORDER; cards = [card_all(n) for n in names]
    end = '<div class="note end" style="margin-top:6px;font-size:8.6px">%s</div>' % ESC_NOTE
    head1 = NEED_SURG + '<div class="tag">다빈도 수술별 보장금액 ①</div><div class="sec"></div>' + SG_GUIDE_ALL
    head2 = lambda k: '<div class="tag">다빈도 수술별 보장금액 %s</div><div class="sec"></div>' % k
    pg = lambda i, body: '<div class="page" id="%s">%s<div class="cnt">%s</div>%s</div>' % (i, head(''), body, foot(''))
    probe = ('<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>' % css()
             + pg('p1', head1 + '<div class="cards"></div>' + end) + pg('p2', head2('②') + '<div class="cards"></div>' + end)
             + pg('pm', '<div class="cards" style="align-items:start">%s</div>' % ''.join(cards)) + '</body></html>')
    r = _goto(probe, 'surgm').evaluate(_MEASURE_JS)
    H, gap = r['h'], r['gap']; pages = [[]]; used = 0.0
    for k in range(0, len(cards), 2):       # 두 장씩 한 줄 — 줄 높이 = 둘 중 큰 카드
        h = max(H[k:k + 2]); cap = r['a1'] if len(pages) == 1 else r['a2']
        need = h + (gap if pages[-1] else 0)
        if pages[-1] and (used + need > cap or len(pages[-1]) >= 3): pages.append([]); used = 0.0; need = h      # 한 쪽 최대 3줄(6장) — 묶음판과 같은 배치, 넘치면 쪽을 더 늘린다
        pages[-1].append(k); used += need
    nums = '①②③④⑤⑥'; out = []
    for i, ks in enumerate(pages):
        body = (head1 if i == 0 else head2(nums[i])) + '<div class="cards">%s</div>' % ''.join(cards[k] + (cards[k + 1] if k + 1 < len(cards) else '') for k in ks) + end
        out.append(page('주요수술 보장 %s' % nums[i], body, '※ 금액은 이 설계의 특약별 가입금액 기준입니다. 수술명 옆 질병코드는 사례 기준입니다.', ' data-zg="surg" data-zmax="1"'))
    return out

# ── 간병인 — GA 시안 v8 표 양식(1~180일 / 181일 이상) · 보상 예시는 뺌(2026-11-18 회의) ──
def _ic(key): return '<span class="cv-ic">%s</span>' % ico(key, 34)
def need_care():
    return ('<div class="cv-h"><b>돈 많이 드는 간병비</b><span>간병비는 건강보험이 적용되지 않는 전액 본인부담</span></div>'
            '<div class="cv-need"><div>%s<div class="k">한 달 평균 간병비</div><div class="v">370<small>만</small></div></div>'
            '<div>%s<div class="k">국민 사적 간병비<small>(연간 추정)</small></div><div class="v">10<small>조원</small></div></div></div>'
            '<div class="cv-src">[출처: 보건복지부 2023년 발표 자료 · 보건복지부 소개 서울대 사적 간병비 추정(2022년) / 지역 · 환자 상태에 따라 편차가 큼]</div>') % (_ic('care_cost'), _ic('private_care'))
C_NA = '<span class="na">미가입</span>'
C_EXC = '<span class="na">보장 제외</span>'      # 간병인사용 181일 이상 특약은 요양병원을 보장하지 않는다(이름 「(요양,정신,한방병원제외)」) — 「미가입」 이 아니라 「보장 제외」(2026-11-18 회의)
def _sub(t): return '<span class="sub">(%s)</span>' % t
def c_send(on, sub=''): return ('<span class="snd">%s</span>%s' % (SEND, sub)) if on else C_NA
def c_day(v, sub=''):
    """1일 ○만 — None 은 미가입, 0 은 가입했지만 그 일당이 없음(회색 0)"""
    if v is None: return C_NA
    return '<span class="d%s">1일<b>%s</b><i>만</i></span>%s' % (' z' if abs(v) < 1e-9 else '', won(v), sub)
def _tbl(rows): return ('<table class="cv-t"><colgroup><col style="width:20%%"><col style="width:13.9%%"><col style="width:33%%"><col></colgroup>'
                        '<tr><th colspan="2">구분</th><th>1~180일</th><th>181일 이상</th></tr>%s</table>') % ''.join('<tr>%s<td>%s</td><td>%s</td></tr>' % r for r in rows)
def _lim(n): return _sub('1회 입원 %d일 한도' % n) if n and n < 180 else ''
def tbl_support(cf):
    """간병인 지원일당 표. 「공동간병인 사용 시 실손보장」 줄과 「공시금액 140,400원」 주석은 GA 시안 v8 문구 그대로다 — 약관에는 '공동간병 · 공시금액 · 실손' 이라는 말과
    금액이 없고(약관 : 회사가 간병인을 지원하지 못하거나 보험수익자가 회사 지원 간병인을 계속 원하지 않을 때, 실제 쓴 간병인 사용비용을 「회사가 정한 간병인지원비용」 한도로 지급 ·
    (Ⅰ) 제1조 ② · (Ⅵ) 제1조 ① 단서), 금액은 회사 공시 값이라 GA · 회사 자료로 확정해야 한다. 요양성 특정질병 풀이는 약관 분류표의 구분 이름으로 적는다"""
    co = '<span class="snd">실손보장</span>' + _sub('*한도 내 실손 보장'); lim = _lim(cf['lim_sup'])
    nurse = cf['nurse180']; nsub = lim
    if cf['use_nurse'] and not cf['has_use']:      # 간병인사용 담보 없이 「간호 · 간병통합서비스 사용 질병입원일당」 만 있으면 이 표에 더해 보인다(같은 날 함께 지급)
        nurse = (nurse or 0) + cf['use_nurse']; nsub = _sub('통합서비스 사용일당 %s만 포함' % won(cf['use_nurse']))
    u181, usub = cf['unused181'], ''
    if u181 is None and cf['supnh']: u181, usub = sum(CARE.daily(r) for r in cf['supnh']), _sub('요양병원 · 요양성 특정질병')
    return ('<div class="cv-tab"><b>간병인 지원일당</b><span>현물지원 · 회사가 간병인을 보내드려요</span></div>' + _tbl([
        ('<td class="l" rowspan="2">간병인 사용 시</td><td class="l">병 · 의원</td>', c_send(cf['sup180'], lim), c_send(cf['sup181'])),
        ('<td class="l">요양병원</td>', c_send(cf['sup180'], lim), c_send(cf['supnh'], _sub('요양성 특정질병 보장'))),
        ('<td class="l" colspan="2">공동간병인 사용 시</td>', (co + (lim if cf['sup180'] else '')) if cf['sup180'] else C_NA, co if (cf['sup181'] or cf['supnh']) else C_NA),
        ('<td class="l" colspan="2">간호 · 간병통합서비스 사용 시</td>', c_day(nurse, nsub), c_day(cf['nurse181'])),
        ('<td class="l" colspan="2">간병인 미사용 시</td>', c_day(cf['unused180'], lim), c_day(u181, usub))]) +
        '<div class="cv-note">※ 한도 내 실손보장: 간병인 이용한 실제 비용을 간병인 지원 공시금액 한도 내 실손 보장(2026년 기준 간병인 지원 공시금액: 140,400원)<br>'
        '※ 요양성 특정질병: 약관 분류표가 정한 치매질환 · 뇌혈관질환(뇌내출혈 · 뇌경색증 등) · 신경계질환(파킨슨병 등)</div>')
def tbl_use(cf):
    """간병인 사용일당 표"""
    g = lambda extra: _sub('요양병원 제외' + extra)
    return ('<div class="cv-tab"><b>간병인 사용일당</b><span>금액지원 · 간병인 사용일수를 계산하여 일당으로 드려요</span></div>' + _tbl([
        ('<td class="l" rowspan="2">간병인 사용 시</td><td class="l">병 · 의원</td>', c_day(cf['use_gen'], g(' · 1회 입원 %d일 한도' % cf['lim_gen'] if cf['lim_gen'] and cf['lim_gen'] < 180 else '')),
         c_day(cf['use181'], _sub('요양 · 정신 · 한방병원 제외'))),
        ('<td class="l">요양병원</td>', c_day(cf['use_nh'], _lim(cf['lim_nh'])), c_day(cf['usenh181'], _sub('요양성 특정질병 보장')) if cf['usenh181'] else C_EXC),
        ('<td class="l" colspan="2">간호 · 간병통합서비스 사용 시</td>', c_day(cf['use_nurse']), c_day(cf['use_nurse181']))]) +
        '<div class="cv-note">' + '<br>'.join(
            ['※ 간병인 사용일당: 약관이 정한 간병인(병원 소속 간병인 · 등록된 간병 업체 등 유상 간병인)을 사용한 날 수만큼 일당을 지급']
            # (plus) 특약 지급금액표 : 간병인 사용금액 1일당 7만원 이상(7만원 미만이어도 1일 8시간 이상) 100% · 그 미만 50%
            + (['※ 병 · 의원 금액은 간병인 사용금액이 1일당 7만원 이상(또는 1일 8시간 이상)인 경우 기준이며, 그 미만이면 50%를 지급'] if cf['use_plus'] else [])
            + ['※ 181일 이상 보장은 1회 입원당 최대 185일까지 지급']
            # (체증형) 지급금액표 : 계약일부터 5년 · 10년 · 20년 경과시점 이후 120% · 150% · 200%(그 입원의 최초 간병인 사용일 기준)
            + (['※ 체증형은 계약일부터 5년 · 10년 · 20년이 지나면 1일당 금액이 가입금액의 120% · 150% · 200%로 커짐(위 금액은 가입금액 기준)'] if cf['use_esc'] else [])) + '</div>')
def two_ways(cf):
    """「메리츠는 간병인 지원 · 사용 모두 가능」 — 사용 쪽 장점 칸 자리에 담백하게(2026-11-18 회의)"""
    st = lambda on: '<span class="st on">이 설계 가입</span>' if on else ''      # 미가입은 아무것도 적지 않는다(회의 2026-11-18 : 「미가입」 이 나쁜 인상을 준다)
    return ('<div class="cv-h" style="margin-top:15pt"><b>메리츠는 간병인 지원 · 사용 모두 가능</b><span>필요에 맞게 골라서 준비할 수 있어요</span></div>'
            '<div class="cv-two"><div>%s<div class="x"><small>간병인이 필요하다면</small><b>간병인 지원</b><p>회사가 간병인을 직접 보내 드려요</p></div>%s</div>'
            '<div>%s<div class="x"><small>간병비가 필요하다면</small><b>간병인 사용</b><p>간병인을 쓴 날 수만큼 일당을 드려요</p></div>%s</div></div>') % (
            _ic('caregiver'), st(cf['has_sup']), _ic('care_cost'), st(cf['has_use']))
def _short_name(n): return re.sub(r'^\(\d+년갱신\)', '', re.sub(r'\s+', ' ', n)).strip()
CARE_FOOT = '※ 금액은 이 설계의 특약별 가입금액 기준입니다.'
def page_care_support(cf):
    adv = ''.join('<div class="cv-adv"><span class="n">%d</span><span class="t">%s</span><span class="x">%s</span></div>' % (i + 1, a, b) for i, (a, b) in enumerate([      # 장점 세 줄 · 전화번호는 GA 시안 v8 문구
        ('전화 1통으로 간병인 신청', '전화 <b>1688-0090</b>으로 간편하게 신청'), ('추가 비용 없음', '물가가 올라도, 간병인 비용이 올라도 자기부담금 <b>0원</b>'), ('언제든지 간병인 교체 가능', '전화 <b>1688-0090</b>으로 교체 신청 가능')]))
    know = []
    if cf['sup181'] or cf['supnh']: know.append('181일 이상 보장은 1회 입원당 최대 185일까지입니다.')
    if cf['supnh']: know.append('요양병원 181일 이상은 요양성 특정질병으로 입원한 경우만 해당합니다.')
    if cf['lim_sup'] and cf['lim_sup'] < 180: know.append('병원 · 의원 간병인 지원은 1회 입원당 %d일까지입니다.' % cf['lim_sup'])
    know.append(('간호 · 간병통합서비스 병동을 이용하는 날은 간병인 대신 1일 %s만원을 지급합니다.' % won(cf['nurse180'])) if cf['nurse180'] else '간호 · 간병통합서비스 병동을 이용하는 날은 간병인을 보내 드리지 않습니다.')
    ask = '간병인은 원하는 날 48시간 전까지 회사로 신청해야 하며, 신청하지 않고 임의로 간병인을 쓴 경우 '      # 약관 (Ⅰ) 제1조 ⑧ · (Ⅵ) 제1조 ⑦
    if cf['type1'] and not cf['type6']: know.append(ask + '간병비 대신 입원일당%s으로 지급합니다.' % (('(1일 %s만원)' % won(cf['unused180'])) if cf['unused180'] else ''))
    elif cf['type6'] and not cf['type1']: know.append(ask + '그 간병비는 지급하지 않습니다.')
    elif cf['type1'] and cf['type6']: know.append(ask + '(Ⅰ)형은 입원일당으로 지급하고 (Ⅵ)형은 지급하지 않습니다.')
    body = (need_care() + tbl_support(cf) + '<div class="cv-h" style="margin-top:15pt"><b>간병인 지원 장점</b><span>간병인을 구하는 수고와 비용 걱정이 없어요</span></div>' + adv
            + '<div class="cv-h" style="margin-top:13pt"><b>알아두세요</b></div><ul class="cv-ul">%s</ul>' % ''.join('<li>%s</li>' % k for k in know))
    return page('간병인 보장(간병인 지원)', body, CARE_FOOT, ' data-zg="care" data-zmax="1.08"', ' nt')
def page_care_use(cf):
    steps = ''.join('<div><div class="h"><span class="n">%d</span><b>%s</b></div><p>%s</p></div>' % (i + 1, a, b) for i, (a, b) in enumerate([
        ('간병인 사용', '약관이 정한 간병인<br>(병원 소속 · 간병 업체 등)'), ('서류 준비', '입원 확인서<br>간병인 사용 영수증 등'), ('보험금 청구', '모바일 앱, 홈페이지,<br>고객센터로 청구'), ('보험금 지급', '보험금 심사 후 지급')]))
    body = (need_care() + tbl_use(cf) + '<div class="cv-h" style="margin-top:15pt"><b>청구 방법</b><span>간병인을 쓴 날 수만큼 일당으로 받으세요</span></div><div class="cv-steps">%s</div>' % steps
            + two_ways(cf) + '<div class="cv-base">근거 : 이 설계의 %s · 간병인의 정의(약관 제4조)</div>' % ' · '.join(_short_name(n) for n in cf['use_names']))
    return page('간병인 보장(간병인 사용)', body, CARE_FOOT, ' data-zg="care" data-zmax="1.08"', ' nt')
def page_care_none(cf):
    """간병인 지원 · 사용 둘 다 없을 때 — 두 표를 한 쪽에 같이(소유자 2026-11-11 · 표 양식 2026-11-18)"""
    foot = '※ 이 설계의 간병인 보장은 상해 입원에만 있습니다(위 표는 질병 입원 기준).' if cf['inj_only'] else '※ 이 설계에는 간병인 지원 · 사용 보장이 없습니다.'
    return page('간병인 보장', need_care() + tbl_support(cf) + tbl_use(cf) + two_ways(cf), foot, ' data-zg="care" data-zmax="1.08"', ' nt')

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
        p1 = GP.p1_mock(); assert p1.endswith('</div>')
        note = '<div style="position:absolute;left:33pt;top:%.2fpt;font-size:6.6pt;line-height:1;color:#777;white-space:nowrap;font-family:N,P">%s</div>' % (772.5 - K_N * 6.6, ESC_NOTE)      # 주요수술 칸 아래(v8 · 기준선 772.5pt)
        return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s%s</style></head><body>%s</body></html>' % (GP._font_css() + noto_css(), GP.CSS, OV.page_css() + GP.MOCK_CSS, GP.p0_mock() + p1[:-6] + note + '</div>')
    return '<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>' % (GP._font_css(), GP.CSS, GP.p0() + GP.p1())

# ═══════════════ 묶기 ═══════════════
def title_of(pg): return pg.get_text(clip=fitz.Rect(185, 30, 450, 52)).strip()
def build(design_pdf, out_pdf=None, age=''):
    """설계서 1건 → 새 양식 PDF · 로그. 중간 파일(설계서 내용이 든 HTML · PDF 조각)은 한 건마다 임시 폴더에 만들고 끝나면 지운다
    (서버로 돌릴 때 개인정보가 남지 않게 · GA_V2_KEEP=1 이면 남겨 둔다 — 지면 점검용)"""
    import tempfile, shutil, gc
    global TMP
    root = TMP; os.makedirs(root, exist_ok=True)
    TMP = tempfile.mkdtemp(prefix='job_%d_' % os.getpid(), dir=root)
    try:
        try:
            return _build(design_pdf, out_pdf, age)
        except pipeline.DesignUnreadable:
            raise                                             # 설계서를 못 읽은 것 — 크로뮴은 멀쩡하다(이유를 그대로 올린다 · v8.98)
        except Exception as e:
            close_browser()                                   # 실패한 건 뒤에는 크로뮴을 새로 띄운다(죽었거나 이상한 상태일 수 있다)
            if not re.search(r'closed|crash|Target|disconnected', str(e)): raise
            return _build(design_pdf, out_pdf, age)           # 크로뮴이 죽어서 난 오류면 새로 띄워 한 번 더
    finally:
        work, TMP = TMP, root
        gc.collect()                                          # 열어 둔 조각 PDF 를 닫아 윈도우에서도 지워지게
        if os.environ.get('GA_V2_KEEP') != '1': shutil.rmtree(work, ignore_errors=True)
def sweep_tmp(max_age=3600):
    """서버가 처리 중에 꺼져 남은 중간 파일(out/v2tmp/job_*)을 치운다 — 만든 지 1시간 넘은 것만(다른 프로세스가 지금 쓰는 것은 건드리지 않게)"""
    import shutil
    n = 0
    for d in glob.glob(os.path.join(TMP, 'job_*')):
        try:
            if time.time() - os.path.getmtime(d) > max_age: shutil.rmtree(d, ignore_errors=True); n += 1
        except OSError: pass
    return n
def _build(design_pdf, out_pdf=None, age=''):
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
    care_pages = {'support': page_care_support, 'use': page_care_use, 'none': page_care_none}
    pages = (page_surg_all() if SURG_MODE == 'all' else [page_surg(0), page_surg(1)]) + [care_pages[k](cf) for k in cf['pages']]
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
    # 5) 묶기 : 표지 · 요약 → 암① 암② 뇌 심 → 수술 ① ② → 간병 → 세부내역 → 안내사항(치료 여정 · 보장 점검은 2026-11-18 회의에서 뺌)
    out = fitz.open(); cs = fitz.open(p_cs)
    out.insert_pdf(cs); out.insert_pdf(tp, from_page=0, to_page=3); out.insert_pdf(hd); out.insert_pdf(dt); out.insert_pdf(tp, from_page=4, to_page=4)
    dedupe_images(out); jpeg_big(out)
    out.save(out_pdf, garbage=3, deflate=True)
    # 점검 : 틀 쪽 제목이 그대로인가(글꼴 꼬임) · 글자층 오류
    chk = fitz.open(out_pdf); base_i = len(cs)
    for j, k in enumerate(('ca1', 'ca2', 'brain', 'heart')):
        if title_of(chk[base_i + j]) != title_of(tpl[order.index(k)]): raise RuntimeError('틀 쪽 제목이 바뀜 : %s' % k)
    err = subprocess.run(['pdftotext', out_pdf, '-'], capture_output=True, text=True).stderr.strip() if shutil_which('pdftotext') else ''
    if err: warn.append('글자층 경고 : ' + err[:200])
    info = dict(design=os.path.basename(design_pdf), product=GP.PRODUCT, pages=len(chk), care=cf['pages'], detail_pages=n, warn=warn, sec=round(time.time() - t0, 1),
                riders=GP.NRID, fit=fit)
    log = os.path.splitext(out_pdf)[0] + '_log.txt'
    with open(log, 'w', encoding='utf-8') as f:
        f.write('원본 설계서 : %s\n상품 : %s\n보험료 : %s\n담보 %d건 · %d쪽 · 간병인 쪽 : %s · 세부내역 %d쪽 · %.1f초\n\n' % (info['design'], GP.PRODUCT, GP.PREMIUM, GP.NRID, info['pages'],
                ' + '.join({'support': '간병인 지원', 'use': '간병인 사용', 'none': '지원 · 사용 함께(둘 다 미가입)'}[k] for k in cf['pages']), n, info['sec']))
        f.write('[지면 경고] ' + (' / '.join(warn) if warn else '없음') + '\n\n[계산 로그 — 빈칸 · 0원의 이유]\n')
        for it in S.issues_grouped(): f.write('- [%s] %s — %s\n' % (it['구분'], it['담보'], it['사유']))
    return out_pdf, log, info
def shutil_which(x):
    import shutil; return shutil.which(x)

def calibrate(family='P', weight=800):
    """K_BASE · K_N 재기 — 글자를 top=100pt 에 놓았을 때 기준선이 어디 오는지(개발용 · calibrate('P') · calibrate('N', 400))"""
    h = ('<!doctype html><html><head><meta charset="utf-8"><style>%s%s@page{size:300pt 300pt;margin:0}html,body{margin:0}.o{position:absolute;line-height:1;font-family:%s;font-weight:%d}</style></head>'
         '<body><div class="o" style="left:10pt;top:100pt;font-size:20pt">1,000 가입</div></body></html>' % (fonts_css(), noto_css(), family, weight))
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
        o = o0 = out_pdf or os.path.join(BASE, 'ga_output', GP.ascii_name(f) + '_GA2.pdf')
        try:
            if not out_pdf and os.path.exists(o): o = os.path.join(BASE, 'ga_output', '%s_GA2_%s.pdf' % (GP.ascii_name(f), time.strftime('%H%M%S')))
            pdf, log, info = build(f, o, age); pipeline.clear_fail_note(o0, f)
            print('      → %s  (%d쪽 · 간병인 %s · 세부내역 %d쪽)%s' % (pdf, info['pages'], '+'.join(info['care']), info['detail_pages'], ('  ※ ' + ' / '.join(info['warn'])) if info['warn'] else ''), flush=True)
            ok += 1
        except pipeline.DesignUnreadable as ex:
            print('      ! 만들지 않았습니다 — %s\n        (이유를 적은 파일 : %s)' % (ex, pipeline.fail_note(o0, f, ex)), flush=True)
        except Exception as ex:
            print('      ! 만들지 못했습니다 : %s: %s' % (type(ex).__name__, ex), flush=True)
    print('\n완료 %d / %d건' % (ok, len(files)))
    return 0 if ok == len(files) else 2

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
