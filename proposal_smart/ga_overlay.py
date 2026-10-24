# -*- coding: utf-8 -*-
"""GA 디자인 가안 그림 위에 글자만 얹는 지면(합성 방식 · 2026-10-23 소유자 지시 「가안에 글자만 합성」).

ga_assets/mock/<page>.jpg      : GA 가 보낸 디자인 가안(1414×2000px · 표지1 · 표지2 · 보장요약 · 암보장 · 뇌심보장 · 세부내역)
ga_assets/mock/overlay_<page>.json : 가안에서 잰 「값이 들어갈 자리」(상자 좌표 · 정렬 · 글자 크기 · 색) — 측정 에이전트가 만든 것
  {"page": "p1", "size": [1414, 2000], "fields": {"p1.ca.dx.일반암": {"box": [x1,y1,x2,y2], "align": "right", "font_px": 26, "weight": 700,
                                                                "color": "#F23A2B", "unit_font_px": 16, "unit_color": "#111111"}, ...}}
만드는 법 : 가안 그림에서 상자 자리의 견본 글자를 주변 바탕색으로 지운 「틀 그림」(tpl_<page>.png)을 만들고, 그 그림을 A4 배경으로 깔고
            상자 자리에 실제 값을 절대 위치로 얹는다(글자는 벡터라 인쇄에도 선명 · 그림은 가안 해상도 그대로).
세부내역(p4)은 줄 수가 설계서마다 달라 표는 HTML 로 그리고, 가안의 머리·꼬리만 배경으로 쓴다.
금액·판정은 ga_spec/ga_proposal 그대로다 — 이 파일은 「어디에 어떻게 보이나」만 맡는다."""
import os, json
BASE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(BASE, 'ga_assets', 'mock')
W, H = 1414, 2000                      # 가안 픽셀
MM_X, MM_Y = 210.0 / W, 297.0 / H       # px → mm
PX_PT = 0.1485 * 72 / 25.4             # 가안 1px 의 글자 크기를 pt 로 (1px = 0.1485mm)

def available():
    return os.path.isdir(MOCK) and all(os.path.exists(os.path.join(MOCK, f)) for f in ('cover1.jpg', 'p1.jpg', 'p2.jpg', 'p3.jpg', 'p4.jpg', 'overlay_p1.json'))

def spec(page):
    p = os.path.join(MOCK, 'overlay_%s.json' % page)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'page': page, 'size': [W, H], 'fields': {}}

def _bg_color(im, box, ring=3):
    """상자 둘레(ring px)의 중앙값 색 — 견본 글자를 지울 때 채우는 바탕색"""
    from PIL import Image
    import statistics
    x1, y1, x2, y2 = [int(round(v)) for v in box]
    px = []
    for x in range(max(0, x1 - ring), min(im.width, x2 + ring)):
        for y in (max(0, y1 - ring), min(im.height - 1, y2 + ring - 1)):
            px.append(im.getpixel((x, y)))
    for y in range(max(0, y1 - ring), min(im.height, y2 + ring)):
        for x in (max(0, x1 - ring), min(im.width - 1, x2 + ring - 1)):
            px.append(im.getpixel((x, y)))
    if not px: return (255, 255, 255)
    return tuple(int(statistics.median(c[i] for c in px)) for i in range(3))

def footer_box(page, sp=None):
    """꼬리 오른쪽 블록(「소속 : … | 코드 : … | 소속 : …」) 전체 상자 — ft.* 값 상자의 띠에서 왼쪽으로 첫 글자가 나오는 곳까지"""
    sp = sp if sp is not None else spec(page)['fields']
    ks = [k for k in sp if k.startswith('ft.')]
    if not ks: return None
    bs = [sp[k]['box'] for k in ks]
    y1, y2 = min(b[1] for b in bs), max(b[3] for b in bs); x2 = max(b[3 - 1] for b in bs) + 8
    from PIL import Image
    im = Image.open(os.path.join(MOCK, page + '.jpg')).convert('L'); px = im.load()
    xs = min(b[0] for b in bs)
    for x in range(600, int(xs)):
        if any(px[x, y] < 150 for y in range(int(y1), int(y2))): xs = x; break
    return [xs - 8, y1 - 2, min(W, x2 + 4), y2 + 2]

def template(page, extra_erase=None, force=False):
    """가안 그림에서 값 자리의 견본 글자를 지운 틀 그림(png) 경로. 상자마다 둘레 바탕색으로 채운다(흰 줄 · 회색 머리 · 분홍 상자 모두 됨)"""
    from PIL import Image, ImageDraw
    out = os.path.join(MOCK, 'tpl_%s.png' % page)
    src = os.path.join(MOCK, page + '.jpg')
    sp = spec(page)
    if os.path.exists(out) and not force and os.path.getmtime(out) > max(os.path.getmtime(src), os.path.getmtime(os.path.join(MOCK, 'overlay_%s.json' % page)) if os.path.exists(os.path.join(MOCK, 'overlay_%s.json' % page)) else 0):
        return out
    im = Image.open(src).convert('RGB'); d = ImageDraw.Draw(im)
    boxes = [f.get('erase') or f['box'] for f in sp['fields'].values()] + list(extra_erase or [])
    fb = footer_box(page, sp['fields'])
    if fb: boxes.append(fb)
    for b in boxes:
        x1, y1, x2, y2 = [int(round(v)) for v in b]
        d.rectangle([x1, y1, x2, y2], fill=_bg_color(im, b))
    im.save(out, optimize=True)
    return out

def page_css():
    return ('.mockpg{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;background-size:210mm 297mm;background-repeat:no-repeat;background-color:#fff}'
            '.ov{position:absolute;display:flex;align-items:center;white-space:nowrap;line-height:1;letter-spacing:-.3pt;font-family:"Pretendard","GANG","Malgun Gothic",sans-serif}'
            '.ov.l{justify-content:flex-start} .ov.r{justify-content:flex-end} .ov.c{justify-content:center} .ov i{font-style:normal;margin-left:1px}'
            '.ov.wrap{white-space:normal;line-height:1.18;word-break:keep-all;align-items:center}')

def page_open(page, cls=''):
    import pathlib
    return '<div class="page mockpg %s" style="background-image:url(\'%s\')">' % (cls, pathlib.Path(template(page)).as_uri())

def est_width(text, font_px, unit=None, unit_px=None):
    """글자 폭 어림(px · Pretendard 기준 가정값) — 한글 0.95em · 숫자·영문 0.58em · 쉼표·점 0.3em · 빈칸 0.28em"""
    w = 0.0
    for ch in text:
        if ch in ',.': w += 0.3
        elif ch == ' ': w += 0.28
        elif ch.isdigit() or ch.isascii(): w += 0.58
        else: w += 0.95
    w *= font_px
    if unit: w += (unit_px or font_px * 0.62) * 0.95 * len(unit) + 2
    return w
def fit(f, text, unit=None):
    """상자 폭에 맞게 글자 크기를 줄인 상자 사본"""
    ff = dict(f); bw = f['box'][2] - f['box'][0] - 4
    w = est_width(text, f.get('font_px', 24), unit, f.get('unit_font_px'))
    if w > bw and w > 0:
        k = max(0.55, bw / w); ff['font_px'] = f.get('font_px', 24) * k
        if f.get('unit_font_px'): ff['unit_font_px'] = f['unit_font_px'] * k
    return ff

def field_html(f, inner, cls=''):
    """상자(f) 자리에 inner(HTML)를 놓는다"""
    x1, y1, x2, y2 = f['box']
    st = 'left:%.2fmm;top:%.2fmm;width:%.2fmm;height:%.2fmm;font-size:%.2fpt;font-weight:%d;color:%s;--u:%.2fpt;--uc:%s;--na:%s' % (
        x1 * MM_X, y1 * MM_Y, (x2 - x1) * MM_X, (y2 - y1) * MM_Y, f.get('font_px', 24) * PX_PT, f.get('weight', 700), f.get('color', '#111111'),
        f.get('unit_font_px', max(12, f.get('font_px', 24) * 0.62)) * PX_PT, f.get('unit_color', '#111111'), f.get('na_color', '#C4C4C4'))
    if f.get('na_font_px'): st += ';--naf:%.2fpt' % (f['na_font_px'] * PX_PT)
    al = {'right': 'r', 'left': 'l', 'center': 'c'}.get(f.get('align', 'right'), 'r')
    return '<div class="ov %s %s" style="%s">%s</div>' % (al, cls, st, inner)

def value_html(v, f, won):
    """칸 값 → 글자 : 숫자(만원) · None(미가입 · 연한 회색) · '간병인 보내줌'(빨강 굵게) · 그 밖의 글자"""
    if v is None:
        return '<span class="na" style="color:%s;font-weight:500">미가입</span>' % f.get('na_color', '#C4C4C4')
    if isinstance(v, str):
        return '<span class="txt" style="color:#F23A2B;font-weight:800">%s</span>' % v
    unit = '<i style="font-size:%.2fpt;color:%s;font-weight:500">만원</i>' % (f.get('unit_font_px', max(12, f.get('font_px', 24) * 0.62)) * PX_PT, f.get('unit_color', '#111111'))
    return '<b class="v%s">%s%s</b>' % (' z' if abs(v) < 1e-9 else '', won(v), unit)

def text_html(s, f, unit=None, shrink_over=None):
    """표지·머리·꼬리의 글(상품명 · 피보험자 · 번호 …). 긴 상품명은 줄바꿈(shrink_over), 그 밖은 한 줄로 상자에 맞게 줄인다"""
    cls = ''
    if shrink_over and len(s) > shrink_over:
        ff = dict(f); ff['font_px'] = f.get('font_px', 24) * max(0.7, shrink_over / float(len(s))) ; cls = 'wrap'
    else:
        ff = fit(f, s, unit)
    inner = s + ('<i style="font-size:var(--u);color:var(--uc);font-weight:500">%s</i>' % unit if unit else '')
    return field_html(ff, inner, cls)

def is_light(hexcolor):
    """연한 회색(미가입 글자색)인가"""
    try:
        h = hexcolor.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception: return False
    return min(r, g, b) > 0xA8
def style_for(sp, key, v):
    """칸 값의 종류에 맞는 상자 스타일 — 가안 견본이 「미가입」(연회색 · 작은 글자)이던 칸에 숫자가 오면 같은 표의 이웃 칸(숫자 스타일)을 빌리고,
    숫자 칸에 「미가입」이 오면 이웃 미가입 칸의 글자 크기를 na_font_px 로 준다"""
    f = dict(sp[key]); light = is_light(f.get('color', '#111111'))
    pre = key.rsplit('.', 1)[0]
    sib = [(k, g) for k, g in sp.items() if k != key and k.rsplit('.', 1)[0] == pre]
    if not sib:
        pre2 = pre.rsplit('.', 1)[0]; sib = [(k, g) for k, g in sp.items() if k != key and k.startswith(pre2 + '.')]
    if v is None or isinstance(v, str):
        if not light and v is None:
            g = next((g for k, g in sib if is_light(g.get('color', ''))), None)
            f['na_font_px'] = g['font_px'] if g else f.get('font_px', 24) * 0.72
        if isinstance(v, str) and light:
            g = next((g for k, g in sib if not is_light(g.get('color', ''))), None)
            if g: f.update({k2: g[k2] for k2 in ('font_px', 'weight', 'color', 'unit_font_px', 'unit_color') if k2 in g})
        return f
    if light:                                   # 숫자가 올 자리인데 견본은 미가입 → 이웃 숫자 칸 스타일(검정 우선, 없으면 빨강)
        dark = [g for k, g in sib if not is_light(g.get('color', '')) and g.get('color', '').lower() not in ('#f23a2b', '#ee3823', '#ec3925', '#ed3925')]
        g = (dark or [g for k, g in sib if not is_light(g.get('color', ''))] or [None])[0]
        if g: f.update({k2: g[k2] for k2 in ('font_px', 'weight', 'color', 'unit_font_px', 'unit_color') if k2 in g})
    return f
