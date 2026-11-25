# -*- coding: utf-8 -*-
"""결산 PPT 그래프 부품 — 숫자를 받아 SVG · HTML 조각을 돌려준다(바깥 라이브러리 없음)."""
import datetime as dt, math

RED, INK, SUB, LINE, GRAY = '#C8102E', '#191F28', '#6B7684', '#E5E8EB', '#D1D6DB'
fmt = lambda v: format(v, ',')


def daily(days, w, h, marks=(), top=3):
    """일별 막대 + 누적 선(오른쪽 눈금) · marks = [(날짜, 글, 높이단)]"""
    L, R, T, B = 64, 78, 170, 40
    n = len(days); vals = [v for _, v in days]; mx = max(vals)
    ymax = 10000 if mx <= 10000 else math.ceil(mx / 1000) * 1000
    cum, c = [], 0
    for v in vals: c += v; cum.append(c)
    cmax = math.ceil(cum[-1] / 10000) * 10000
    bw = (w - L - R) / n
    X = lambda i: L + i * bw
    Y = lambda v: T + (h - T - B) * (1 - v / ymax)
    YC = lambda v: T + (h - T - B) * (1 - v / cmax)
    hot = sorted(range(n), key=lambda i: -vals[i])[:top]
    o = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" style="display:block">' % (w, h, w, h)]
    for g in range(0, ymax + 1, 2000):
        o.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>' % (L, w - R, Y(g), Y(g), '#F2F4F6'))
        o.append('<text x="%d" y="%.1f" font-size="13" fill="%s" text-anchor="end">%s</text>' % (L - 10, Y(g) + 4, SUB, fmt(g)))
    for g in range(0, cmax + 1, cmax // 4):
        o.append('<text x="%d" y="%.1f" font-size="13" fill="%s">%s</text>' % (w - R + 10, YC(g) + 4, RED, fmt(g)))
    o.append('<text x="%d" y="%d" font-size="13" fill="%s" text-anchor="end">하루 건수</text>' % (L - 10, T - 16, SUB))
    o.append('<text x="%d" y="%d" font-size="13" fill="%s">누적</text>' % (w - R + 10, T - 16, RED))
    for i, v in enumerate(vals):
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.5" fill="%s"/>' % (X(i) + .6, Y(v), max(1, bw - 1.2), h - B - Y(v), RED if i in hot else '#C9CED6'))
    pts = ' '.join('%.1f,%.1f' % (X(i) + bw / 2, YC(v)) for i, v in enumerate(cum))
    o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round" opacity=".9"/>' % (pts, RED))
    d0 = dt.date.fromisoformat(days[0][0])
    for i, (d, _) in enumerate(days):
        if d.endswith('-01') or i == 0:
            o.append('<text x="%.1f" y="%d" font-size="14" fill="%s" font-weight="600">%d월</text>' % (X(i), h - B + 24, INK, int(d[5:7])))
    idx = {d: i for i, (d, _) in enumerate(days)}
    for d, t, lv in marks:
        i = idx[d]; x = X(i) + bw / 2; y = 30 + lv * 26
        o.append('<line x1="%.1f" x2="%.1f" y1="%d" y2="%.1f" stroke="#8B95A1" stroke-dasharray="3 3" stroke-width="1"/>' % (x, x, y + 6, h - B))
        anc = 'end' if x > w - 520 else 'start'
        o.append('<circle cx="%.1f" cy="%d" r="4" fill="%s"/><text x="%.1f" y="%d" font-size="14" fill="%s" font-weight="600" text-anchor="%s">%s</text>' % (x, y + 2, RED, x + (-8 if anc == 'end' else 8), y + 7, INK, anc, t))
    o.append('</svg>')
    return ''.join(o)


def spark(days, w, h):
    """작은 면 그래프(표지 · 요약용)"""
    vals = [v for _, v in days]; mx = max(vals); n = len(vals)
    pts = ['%.1f,%.1f' % (i * w / (n - 1), h - 4 - (h - 8) * v / mx) for i, v in enumerate(vals)]
    return ('<svg width="%d" height="%d" viewBox="0 0 %d %d" style="display:block"><defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1">'
            '<stop offset="0" stop-color="%s" stop-opacity=".28"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient></defs>'
            '<polygon points="0,%d %s %d,%d" fill="url(#g)"/><polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/></svg>'
            % (w, h, w, h, RED, RED, h, ' '.join(pts), w, h, ' '.join(pts), RED))


def donut(parts, size, center='', sub='', thick=46):
    """parts = [(이름, 값, 색)]"""
    r = (size - thick) / 2; C = 2 * math.pi * r; tot = sum(v for _, v, _ in parts); acc = 0
    o = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" style="display:block;transform:rotate(-90deg)">' % (size, size, size, size)]
    for _, v, c in parts:
        L = C * v / tot
        o.append('<circle cx="%s" cy="%s" r="%.1f" fill="none" stroke="%s" stroke-width="%d" stroke-dasharray="%.2f %.2f" stroke-dashoffset="%.2f"/>' % (size / 2, size / 2, r, c, thick, max(0, L - 3), C - max(0, L - 3), -acc))
        acc += L
    o.append('</svg>')
    return ('<div style="position:relative;width:%dpx;height:%dpx;flex:none">%s<div style="position:absolute;inset:0;display:grid;place-items:center;text-align:center">'
            '<div><div style="font-size:%dpx;font-weight:700;letter-spacing:-.03em">%s</div><div style="font-size:15px;color:%s">%s</div></div></div></div>'
            % (size, size, ''.join(o), size // 7, center, SUB, sub))


def legend(parts, unit='%', fs=17):
    return ''.join('<div style="display:flex;align-items:center;gap:10px;margin:7px 0;font-size:%dpx"><i style="width:14px;height:14px;border-radius:4px;background:%s;flex:none"></i>'
                   '<span style="flex:1">%s</span><b style="font-variant-numeric:tabular-nums">%s%s</b></div>' % (fs, c, n, v, unit) for n, v, c in parts)


def hbars(items, color=RED, lw=260, fs=17, h=26, hi=1, sub=None):
    """가로 막대 · items = [(이름, 값)] · 위에서 hi 개만 진하게"""
    mx = max(v for _, v in items)
    o = []
    for i, (n, v) in enumerate(items):
        c = color if i < hi else '#C9CED6'
        s = '<div style="font-size:13px;color:%s;margin-top:2px">%s</div>' % (SUB, sub[i]) if sub else ''
        o.append('<div style="display:flex;align-items:center;gap:14px;margin:9px 0"><div style="width:%dpx;flex:none;font-size:%dpx;line-height:1.3">%s%s</div>'
                 '<div style="flex:1;display:flex;align-items:center;gap:10px"><i style="display:block;height:%dpx;width:%.1f%%;border-radius:6px;background:%s"></i>'
                 '<b style="font-size:%dpx;font-variant-numeric:tabular-nums;white-space:nowrap">%s</b></div></div>' % (lw, fs, n, s, h, max(1.5, v / mx * 82), c, fs, fmt(v) if isinstance(v, int) else v))
    return ''.join(o)


def vbars(items, w, h, hi=(), unit='', every=1, fs=13, top_label=True):
    """세로 막대 SVG · items = [(이름, 값)]"""
    L, B, T = 6, 30, 30
    n = len(items); mx = max(v for _, v in items); bw = (w - 2 * L) / n
    o = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" style="display:block">' % (w, h, w, h)]
    for i, (k, v) in enumerate(items):
        bh = (h - B - T) * v / mx; x = L + i * bw
        c = RED if i in hi else '#C9CED6'
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s"/>' % (x + bw * .14, h - B - bh, bw * .72, bh, c))
        if i % every == 0 or i in hi:
            o.append('<text x="%.1f" y="%d" font-size="%d" fill="%s" text-anchor="middle">%s</text>' % (x + bw / 2, h - B + 20, fs, INK if i in hi else SUB, k))
        if top_label and (i in hi):
            o.append('<text x="%.1f" y="%.1f" font-size="%d" font-weight="700" fill="%s" text-anchor="middle">%s%s</text>' % (x + bw / 2, h - B - bh - 8, fs + 3, RED, fmt(v), unit))
    o.append('</svg>')
    return ''.join(o)


def line(points, w, h, unit=''):
    """꺾은선 SVG · points = [(이름, 값)] · 모든 점에 값 표시"""
    L, R, T, B = 40, 40, 40, 36
    n = len(points); mx = max(v for _, v in points)
    X = lambda i: L + (w - L - R) * i / (n - 1)
    Y = lambda v: T + (h - T - B) * (1 - v / mx)
    pts = ' '.join('%.1f,%.1f' % (X(i), Y(v)) for i, (_, v) in enumerate(points))
    o = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" style="display:block">' % (w, h, w, h),
         '<polygon points="%.1f,%d %s %.1f,%d" fill="%s" opacity=".08"/>' % (X(0), h - B, pts, X(n - 1), h - B, RED),
         '<polyline points="%s" fill="none" stroke="%s" stroke-width="3.5" stroke-linejoin="round"/>' % (pts, RED)]
    for i, (k, v) in enumerate(points):
        last = i == n - 1
        o.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" stroke="#fff" stroke-width="2"/>' % (X(i), Y(v), 7 if last else 5, RED))
        o.append('<text x="%.1f" y="%.1f" font-size="%d" font-weight="700" fill="%s" text-anchor="middle">%s%s</text>' % (X(i), Y(v) - 14, 20 if last else 15, RED if last else INK, fmt(v), unit))
        o.append('<text x="%.1f" y="%d" font-size="13" fill="%s" text-anchor="middle">%s</text>' % (X(i), h - 10, SUB, k))
    o.append('</svg>')
    return ''.join(o)
