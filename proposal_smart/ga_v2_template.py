# -*- coding: utf-8 -*-
"""GA 스마트 제안서 v2 — 「빈 틀」 만들기(한 번만 돌린다 · 결과는 ga_assets/v2/tpl.pdf · slots.json).

  python ga_v2_template.py <v41 제안서 PDF>

GA 가 정한 v41 디자인(암 보장 ① ② · 뇌혈관 · 심장 · 안내사항 · 세부내역 머리/바닥)에서 **값 글자와 개인정보만 지운** 틀을 만들고,
지운 자리(값이 들어갈 자리)의 위치 · 글자 크기 · 색을 slots.json 에 적는다. ga_v2.py 는 이 틀 위에 설계서마다 계산한 값을 얹는다
(지금 GA 합성 모드 ga_overlay 와 같은 방식 — 디자인은 GA 가안 그대로, 값만 바뀐다).

· 원본 v41 PDF 는 실제 고객 · 설계사 정보가 들어 있어 저장소에 넣지 않는다(CLAUDE.md 6). 만든 틀에는 이름 · 소속 · 전화 · 설계번호가 남지 않게
  지우고, 마지막에 글자층을 다시 읽어 남은 것이 없는지 확인한다.
· 뇌 · 심 「치료 및 수술」 4열 표는 지우고(설계서마다 5열 표를 그린다 · 회의 2026-11-11 기계적 혈전제거술 열), 심장 맨 위 니즈는
  「다시 찾아오는 심근경색」(질병관리청 2023 심뇌혈관질환 발생통계)으로 바꿔 굳힌다. 안내사항 아래 빈 곳에 새 쪽 안내 · 추가 출처를 굳힌다.
"""
import os, sys, re, json
import fitz
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import ga_v2 as G2

OUT_PDF, OUT_SLOTS = G2.TPL, G2.SLOTS
SRC_PAGES = dict(ca1=2, ca2=3, brain=4, heart=5, notice=14, detail=8)      # v41 쪽 번호(0부터)
# 개인정보 남김 점검 — 실제 이름은 이 파일에 적지 않는다(CLAUDE.md 6). 전화 · 긴 번호 · 「소속 : / 컨설턴트 :」 뒤 글자를 모양으로 찾고,
# 원본 v41 의 이름 등은 실행할 때 환경변수 GA_V2_PERSONAL(쉼표로 구분)로 넘겨 함께 찾는다.
PERSONAL = tuple(w for w in os.environ.get('GA_V2_PERSONAL', '').split(',') if w.strip())
PERSONAL_RE = (r'01\d-?\d{3,4}-?\d{4}', r'0\d{1,2}-\d{3,4}-\d{4}', r'\d{12,}', r'(소속|컨설턴트)\s*[:：]\s*\S')

def lines(page, clip=None):
    out = []
    for b in page.get_text('dict', clip=clip)['blocks']:
        for l in b.get('lines', []):
            sp = [s for s in l['spans'] if s['text'].strip()]
            if sp: out.append(dict(bbox=fitz.Rect(l['bbox']), spans=sp, text=''.join(s['text'] for s in l['spans']).strip()))
    return out
def amount_lines(page, y0, y1, x0=0, x1=600):
    """값 줄(「1,000만」 · 「미가입」 · 「1억 2,250만」) — 띠(y0~y1) 안에서 왼쪽부터"""
    L = [l for l in lines(page) if y0 <= l['bbox'].y0 <= y1 and x0 <= l['bbox'].x0 <= x1 and re.fullmatch(r'\d+억(\s?[\d,]+만)?|[\d,]+만|미가입', re.sub(r'\s+', ' ', l['text']).strip())]
    return sorted(L, key=lambda l: l['bbox'].x0)
def style_of(l):
    """값 줄의 모양 — 숫자 글자 크기 · 색, 「만」 크기 · 색, 기준선"""
    num = [s for s in l['spans'] if re.search(r'\d', s['text'])]
    unit = [s for s in l['spans'] if '만' in s['text'] and not re.search(r'\d', s['text'])]
    n = num[0] if num else l['spans'][0]; u = unit[0] if unit else n
    return dict(size=round(n['size'], 2), color='#%06x' % n['color'], usize=round(u['size'], 2), ucolor='#%06x' % u['color'], base=round(n['origin'][1], 2))
def slot(key, l, kind='amt', **kw):
    b = l['bbox']; st = style_of(l)
    d = dict(key=key, kind=kind, cx=round((b.x0 + b.x1) / 2, 2), x0=round(b.x0, 2), x1=round(b.x1, 2), top=round(b.y0, 2), bot=round(b.y1, 2), **st)
    d.update(kw); return d

def wipe(page, rects):
    for r in rects: page.add_redact_annot(r, fill=False, cross_out=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE, text=fitz.PDF_REDACT_TEXT_REMOVE)
def inner(b, dx=0.6, dy=1.5): return fitz.Rect(b.x0 + dx, b.y0 + dy, b.x1 - dx, b.y1 - dy)
def one(page, pat, clip=None):
    L = [l for l in lines(page, clip) if re.search(pat, l['text'])]
    assert len(L) == 1, (pat, [l['text'] for l in L]); return L[0]

def build(src_pdf):
    src = fitz.open(src_pdf); out = fitz.open(); SL = {}
    def copy_page(k):
        out.insert_pdf(src, from_page=SRC_PAGES[k], to_page=SRC_PAGES[k]); return out[-1]
    def footer(pg):          # 바닥글 오른쪽 「소속 : … | 코드 : … | 컨설턴트 : …」
        l = one(pg, r'소속', fitz.Rect(400, 805, 600, 830)); b = l['bbox']; wipe(pg, [fitz.Rect(b.x0 - 1, b.y0, b.x1 + 2, b.y1)])
        return dict(key='footer', kind='footer', x1=round(b.x1, 2), base=round(l['spans'][0]['origin'][1], 2), size=round(l['spans'][0]['size'], 2))

    # ── 암 보장 ① 검사 · 진단 · 수술 ──
    pg = copy_page('ca1'); s = []
    ex = amount_lines(pg, 305, 320); assert len(ex) == 8, len(ex)
    s += [slot('p2.ex.' + k, l) for (_, k), l in zip(G2.GS.EX_CA, ex)]
    dx = amount_lines(pg, 492, 505); assert len(dx) == 3, len(dx)
    s += [slot('p2.dx.' + k, l) for k, l in zip(('일반암', '유사암', '전이암'), dx)]
    gl = one(pg, r'남성 1위 전립선암', fitz.Rect(40, 460, 200, 485))
    s.append(slot('gender_line', gl, kind='text', size=round(gl['spans'][0]['size'], 2), color='#%06x' % gl['spans'][0]['color']))
    rows = []
    for y0 in (670, 708, 745):
        r = amount_lines(pg, y0, y0 + 10, 120); assert len(r) == 4, (y0, len(r)); rows.append(r)
    for md, r in zip(('first', 'year', 'each'), rows):
        s += [slot('p2.sg.%s.%s' % (k, md), l) for (_, k), l in zip(G2.GS.SG, r)]
    wipe(pg, [inner(l['bbox']) for l in ex + dx + sum(rows, [])] + [inner(gl['bbox'], 0.4, 1.0)])
    s.append(footer(pg)); SL['ca1'] = s

    # ── 암 보장 ② 항암치료 ──
    pg = copy_page('ca2'); s = []; W = []
    r1 = amount_lines(pg, 196, 206); r2 = amount_lines(pg, 244, 252); assert len(r1) == 4 and len(r2) == 4, (len(r1), len(r2))
    s += [slot(k, l) for k, l in zip(('p2.cm.chemo.first', 'p2.cm.target1.first', 'p2.cm.immune1.first', 'p2.cm.two'), r1)]
    s += [slot(k, l) for k, l in zip(('p2.cm.chemo.year', 'p2.cm.target1.year', 'p2.cm.immune1.year', 'p2.cm.two3'), r2)]
    r3 = amount_lines(pg, 445, 455); r4 = amount_lines(pg, 492, 500); assert len(r3) == 4 and len(r4) == 4, (len(r3), len(r4))
    s += [slot('p2.rd.%s.first' % k, l) for (_, k), l in zip(G2.GS.RD, r3)] + [slot('p2.rd.%s.year' % k, l) for (_, k), l in zip(G2.GS.RD, r4)]
    rh = amount_lines(pg, 625, 635, 100, 300); ds = amount_lines(pg, 625, 635, 300); assert len(rh) == 1 and len(ds) == 1
    s += [slot('rh_ca', rh[0]), slot('p2.dis', ds[0])]
    ex = amount_lines(pg, 744, 752); tot = amount_lines(pg, 733, 740, 420); assert len(ex) == 3 and len(tot) == 1, (len(ex), len(tot))
    s += [slot(k, l) for k, l in zip(('p2.dx.일반암', 'p2.sg.robot.first', 'p2.cm.immune1.first'), ex)] + [slot('ex_ca_total', tot[0], kind='total')]
    W = r1 + r2 + r3 + r4 + rh + ds + ex + tot
    wipe(pg, [inner(l['bbox']) for l in W]); s.append(footer(pg)); SL['ca2'] = s

    # ── 뇌혈관 · 심장 ──
    for k, tbl, need in (('brain', (316.5, 499.5), None), ('heart', (324.0, 504.0), (68.5, 181.5))):
        pg = copy_page(k); s = []; W = []
        y_ex = 236 if k == 'brain' else 246
        exl = amount_lines(pg, y_ex, y_ex + 8, 40, 240); assert len(exl) == 3, (k, len(exl))
        s += [slot('p3.ex.' + kk, l) for (_, kk), l in zip(G2.GS.EX_BH, exl)]
        dxl = sorted([l for l in lines(pg) if y_ex <= l['bbox'].y0 <= y_ex + 8 and l['bbox'].x0 > 250], key=lambda l: l['bbox'].x0); assert len(dxl) == 2, (k, [l['text'] for l in dxl])
        if k == 'brain':
            dk = (('p3.dx.뇌혈관', '뇌출혈·뇌경색·뇌동맥류 등'), ('p3.dx.뇌졸중', '뇌출혈·뇌경색 등'))
        else:
            dk = (('p3.dx.허혈성심장', '협심증·급성심근경색 등'), ('p1.bh.dx.급성심근경색', ''))
        for (kk, desc), l in zip(dk, dxl):
            st = slot(kk, l, kind='amt_desc', desc=desc)
            dsp = [x for x in l['spans'] if re.search(r'[가-힣]', x['text']) and x['text'].strip() != '만']      # 설명 글자(「뇌출혈 · 뇌경색 등」) — 쉼표 · 숫자 · 「만」 제외
            if dsp: st.update(dsize=round(dsp[0]['size'], 2), dcolor='#%06x' % dsp[0]['color'])
            s.append(st)
        nt = one(pg, r'^※ 두 진단 항목은 동일 특약')
        s.append(dict(key='dx_note', kind='note', x0=round(nt['bbox'].x0, 2), base=round(nt['spans'][0]['origin'][1], 2), size=round(nt['spans'][0]['size'], 2), color='#%06x' % nt['spans'][0]['color']))
        sev = amount_lines(pg, 622, 632); assert len(sev) == 5, (k, len(sev))
        s += [slot('p3.sev.' + kk, l) for (_, kk), l in zip(G2.GS.SEV, sev)]
        rh = amount_lines(pg, 724, 733, 60, 150); assert len(rh) == 1, (k, len(rh))
        s.append(slot('rh_bh', rh[0]))
        exb = amount_lines(pg, 727, 735, 200, 440); tot = amount_lines(pg, 716, 724, 440); assert len(exb) == 3 and len(tot) == 1, (k, len(exb), len(tot))
        exk = ('p3.dx.뇌졸중', 'p3.b1.first', 'p3.sev.icu') if k == 'brain' else ('p3.dx.허혈성심장', 'p3.h2.first', 'p3.h2.year')      # 뇌 예시는 「뇌경색」 → 뇌졸중(I63) 칸
        s += [slot(kk, l) for kk, l in zip(exk, exb)] + [slot('ex_%s_total' % k, tot[0], kind='total')]
        W = exl + dxl + sev + rh + exb + tot
        if k == 'brain':      # 예시 진단 이름 「뇌혈관질환」 → 「뇌졸중(뇌경색)」(값이 뇌경색 칸이므로)
            lb = one(pg, r'^뇌혈관질환$', fitz.Rect(200, 712, 270, 730)); W.append(lb)
            s.append(slot('ex_brain_dx', lb, kind='text', size=round(lb['spans'][0]['size'], 2), color='#%06x' % lb['spans'][0]['color']))
        wipe(pg, [inner(l['bbox']) for l in W] + [inner(nt['bbox'], 0.3, 1.0), fitz.Rect(32, tbl[0] + 1, 563.5, tbl[1])] + ([fitz.Rect(31, need[0], 565, need[1])] if need else []))
        pg.draw_rect(fitz.Rect(31.5, tbl[0], 564.0, tbl[1] + 0.6), color=None, fill=(1, 1, 1), overlay=True)     # 옛 4열 표 자리(설계서마다 5열 표)
        s.append(dict(key='table', kind='table', x0=31.5, x1=564.0, top=tbl[0], bot=tbl[1]))
        s.append(dict(key='life_note', kind='life', x1=564.0, top=tbl[1] + 2.8))
        if need:
            pg.draw_rect(fitz.Rect(30, need[0] - 1, 566, need[1] + 1), color=None, fill=(1, 1, 1), overlay=True)
            npdf = os.path.join(V2TMP, 'need_heart.pdf'); G2.render_snippet(G2.need_heart_html(), npdf, 532.5, G2.NEED_HEART_H)
            pg.show_pdf_page(fitz.Rect(31.5, 68.0, 564.0, 68.0 + G2.NEED_HEART_H), fitz.open(npdf), 0)
        s.append(footer(pg)); SL[k] = s

    # ── 안내사항 ──
    pg = copy_page('notice'); s = []
    dn = one(pg, r'^\d{10,}\)$'); wipe(pg, [inner(dn['bbox'], 0.3, 1.0)])
    s.append(dict(key='dno', kind='note', x0=round(dn['bbox'].x0, 2), base=round(dn['spans'][0]['origin'][1], 2), size=round(dn['spans'][0]['size'], 2), color='#%06x' % dn['spans'][0]['color']))
    apdf = os.path.join(V2TMP, 'notice_add.pdf'); G2.render_snippet(G2.notice_add_html(), apdf, 532.5, G2.NOTICE_ADD_H)
    pg.show_pdf_page(fitz.Rect(31.5, 668.0, 564.0, 668.0 + G2.NOTICE_ADD_H), fitz.open(apdf), 0)
    s.append(footer(pg)); SL['notice'] = s

    # ── 세부내역 틀(머리 · 바닥만) ──
    dp = src[SRC_PAGES['detail']]
    tmp = fitz.open(); tmp.insert_pdf(src, from_page=SRC_PAGES['detail'], to_page=SRC_PAGES['detail']); tp = tmp[0]
    sub = [l for l in lines(tp) if l['bbox'].y0 > 780 or re.fullmatch(r'\d+ / \d+', l['text'])]
    pn = [l for l in sub if re.fullmatch(r'\d+ / \d+', l['text'])][0]; ft = [l for l in sub if l['bbox'].y0 > 780]
    wipe(tp, [fitz.Rect(l['bbox'].x0 - 1, l['bbox'].y0, l['bbox'].x1 + 1, l['bbox'].y1) for l in sub])
    fb = fitz.Rect(min(l['bbox'].x0 for l in ft) - 12, min(l['bbox'].y0 for l in ft) - 0.5, 567, max(l['bbox'].y1 for l in ft) + 0.5)
    tp.draw_rect(fb, color=None, fill=(1, 1, 1), overlay=True)      # 바닥글 칸막이(세로줄 그림)도 지운다 — 값 글자 길이가 설계서마다 달라 칸막이는 ga_v2 가 다시 그린다
    W_, H_ = dp.rect.width, dp.rect.height
    pg = out.new_page(width=W_, height=H_)
    pg.show_pdf_page(fitz.Rect(0, 0, W_, 52.2), tmp, 0, clip=fitz.Rect(0, 0, W_, 52.2))
    pg.show_pdf_page(fitz.Rect(0, 776, W_, H_), tmp, 0, clip=fitz.Rect(0, 776, W_, H_))
    s = [dict(key='pageno', kind='pageno', x1=round(pn['bbox'].x1, 2), base=round(pn['spans'][0]['origin'][1], 2), size=round(pn['spans'][0]['size'], 2)),
         dict(key='footer', kind='footer_detail', x1=round(max(l['bbox'].x1 for l in ft), 2), base=round(ft[0]['spans'][0]['origin'][1], 2), size=round(ft[0]['spans'][0]['size'], 2)),
         dict(key='content', kind='content', top=66.0, height=708.0)]
    SL['detail'] = s

    # 그림 줄이기(같은 그림은 한 번만 · 300dpi) → 저장 → 개인정보 · 값 남김 점검
    G2.shrink_images(out, dpi=220); G2.dedupe_images(out)      # 쪽마다 들어 있는 같은 로고 · 아이콘은 하나로, 아이콘(256px · 약 33pt 로 찍힘)은 128px(약 280dpi)로
    out.save(OUT_PDF, garbage=3, deflate=True)
    chk = fitz.open(OUT_PDF); txt = ''.join(p.get_text() for p in chk)
    left = [w for w in PERSONAL if w in txt] + [m.group(0) for pat in PERSONAL_RE for m in re.finditer(pat, txt)]; assert not left, ('틀에 개인정보가 남음', left)
    meta = {k: v for k, v in (chk.metadata or {}).items() if v}
    order = ['ca1', 'ca2', 'brain', 'heart', 'notice', 'detail']
    json.dump(dict(pages=order, size=[round(chk[0].rect.width, 2), round(chk[0].rect.height, 2)], slots=SL), open(OUT_SLOTS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('틀', OUT_PDF, len(chk), '쪽 ·', round(os.path.getsize(OUT_PDF) / 1e6, 2), 'MB · 자리', sum(len(v) for v in SL.values()), '· 메타', meta)

V2TMP = os.path.join(BASE, 'out', 'v2tmp')
if __name__ == '__main__':
    os.makedirs(V2TMP, exist_ok=True)
    build(sys.argv[1])
