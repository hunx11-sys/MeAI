# -*- coding: utf-8 -*-
"""GA 스마트 제안서 v2 — 「빈 틀」 만들기(한 번만 돌린다 · 결과는 ga_assets/v2/tpl.pdf · slots.json).

  python ga_v2_template.py <GA 최종 시안 PDF(V5_6_19)> <앞 판 tpl.pdf> <앞 판 slots.json>

GA 최종 시안(2026-11-20 · 16쪽)에서 **값 글자와 개인정보만 지운** 틀을 만들고, 지운 자리(값이 들어갈 자리)의 위치 · 글자 크기 · 색을
slots.json 에 적는다. ga_v2.py 는 이 틀 위에 설계서마다 계산한 값을 얹는다(디자인은 GA 시안 그대로, 값만 바뀐다).

시안 PDF 의 쪽 구조(직접 확인 · 2026-11-20)
  · 암 보장 ① ②(3 · 4쪽) = 앞 판 결과물 위에 GA 가 덧칠한 것(내용 흐름이 둘 — 첫째는 앞 판 결과물, 둘째가 덧칠 : 흰 상자 + 새 글자 + 새 아이콘).
    → 앞 판 틀(값이 이미 지워져 있다)에서 덧칠에 가려지는 글자 · 그림을 지우고, 시안의 **덧칠 층만** 떼어 얹는다(가려진 옛 글자가 글자층에 남지 않게).
  · 뇌혈관 · 심장(5 · 6쪽) = GA 가 통째로 새로 그린 쪽(내용 흐름 하나) → 값 글자 · 바닥글 이름만 지우고 그대로 쓴다. 5열 표 · 니즈 상자도 시안 것.
  · 안내사항(16쪽) · 세부내역 머리/바닥 = 앞 판과 같다 → 앞 판 틀 쪽을 그대로 옮긴다.
  · 보장요약(2쪽) · 주요수술(7 · 8쪽) · 간병인(9~11쪽)은 틀을 쓰지 않는다(ga_proposal 합성 · ga_v2 가 HTML 로 그린다).

· 시안 PDF · 앞 판 v41 PDF 는 실제 설계사 정보가 들어 있어 저장소에 넣지 않는다(CLAUDE.md 6). 만든 틀에는 이름 · 소속 · 전화 · 설계번호가 남지 않게
  지우고, 마지막에 글자층을 다시 읽어 남은 것 · 가려진 글자가 없는지 확인한다.
"""
import os, sys, re, json
import fitz
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import ga_v2 as G2

OUT_PDF, OUT_SLOTS = G2.TPL, G2.SLOTS
SRC = dict(ca1=2, ca2=3, brain=4, heart=5)      # 시안 쪽 번호(0부터)
OLD = dict(ca1=0, ca2=1, notice=4, detail=5)    # 앞 판 틀 쪽 번호
# 개인정보 남김 점검 — 실제 이름은 이 파일에 적지 않는다(CLAUDE.md 6). 전화 · 긴 번호 · 「소속 : / 컨설턴트 :」 뒤 글자를 모양으로 찾고,
# 시안의 이름 등은 실행할 때 환경변수 GA_V2_PERSONAL(쉼표로 구분)로 넘겨 함께 찾는다.
PERSONAL = tuple(w for w in os.environ.get('GA_V2_PERSONAL', '').split(',') if w.strip())
PERSONAL_RE = (r'01\d-?\d{3,4}-?\d{4}', r'0\d{1,2}-\d{3,4}-\d{4}', r'\d{12,}', r'(소속|컨설턴트)\s*[:：]\s*\S')
VAL_RE = r'\d+억(\s?[\d,]+만)?|[\d,]+만|미가입'

def lines(page, clip=None):
    out = []
    for b in page.get_text('dict', clip=clip)['blocks']:
        for l in b.get('lines', []):
            sp = [s for s in l['spans'] if s['text'].strip()]
            if sp: out.append(dict(bbox=fitz.Rect(l['bbox']), spans=sp, text=re.sub(r'\s+', ' ', ''.join(s['text'] for s in l['spans'])).strip()))
    return out
def val_lines(page, y0, y1, x0=0, x1=600):
    """값 줄(「1,000만」 · 「미가입」) — 띠(y0~y1) 안에서 왼쪽부터"""
    L = [l for l in lines(page) if y0 <= l['bbox'].y0 <= y1 and x0 <= l['bbox'].x0 <= x1 and re.fullmatch(VAL_RE, l['text'])]
    return sorted(L, key=lambda l: l['bbox'].x0)
def slot(key, l, size, color, usize=8.0, ucolor='#1f1f22', kind='amt', **kw):
    """값 자리 — 시안의 견본 글자가 금액이면 그 기준선 · 크기를, 「미가입」 이면 금액 기준선을 1.3pt 아래로(가운데가 같게) 잡는다"""
    b = l['bbox']; sp = l['spans'][0]; isnum = bool(re.search(r'\d', l['text']))
    base = round(sp['origin'][1], 2)
    d = dict(key=key, kind=kind, cx=round((b.x0 + b.x1) / 2, 2), top=round(b.y0, 2), size=size, color=color, usize=usize, ucolor=ucolor,
             base=base if isnum else round(base + 1.3, 2), nbase=round(base - 1.3, 2) if isnum else base, ff='N')
    d.update(kw); return d
def wipe(page, rects, images=False):
    for r in rects: page.add_redact_annot(r, fill=False, cross_out=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE if images else fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE, text=fitz.PDF_REDACT_TEXT_REMOVE)
def inner(b, dx=0.6, dy=1.5): return fitz.Rect(b.x0 + dx, b.y0 + dy, b.x1 - dx, b.y1 - dy)
def one(page, pat, clip=None):
    L = [l for l in lines(page, clip) if re.search(pat, l['text'])]
    assert len(L) == 1, (pat, [l['text'] for l in L]); return L[0]
def hidden_text(page):
    """뒤에 그린 칠 · 그림에 가려 보이지 않는 글자(글자층에만 남는 것)"""
    log = page.get_bboxlog(); cover = [(i, fitz.Rect(b)) for i, (t, b) in enumerate(log) if t in ('fill-path', 'fill-image', 'fill-shade')]
    out = []
    for sp in page.get_texttrace():
        r = fitz.Rect(sp['bbox']); t = ''.join(chr(c[0]) for c in sp['chars'])
        if t.strip() and any(i > sp['seqno'] and (c & r).get_area() > 0.8 * r.get_area() for i, c in cover): out.append(t)
    return ''.join(out)

def patch_layer(src, pno):
    """시안 쪽의 덧칠 층(둘째 내용 흐름)만 남긴 한 쪽 문서 — 쓰지 않는 글꼴 · 그림은 자원 목록에서 뺀다"""
    tmp = fitz.open(); tmp.insert_pdf(src, from_page=pno, to_page=pno); pg = tmp[0]
    cs = pg.get_contents(); assert len(cs) == 2, cs
    s = tmp.xref_stream(cs[1])
    used = dict(Font=set(m.decode() for m in re.findall(rb'/([^\s/\[\]<>()]+)\s+[-\d.]+\s+Tf', s)),
                XObject=set(m.decode() for m in re.findall(rb'/([^\s/\[\]<>()]+)\s+Do', s)),
                ExtGState=set(m.decode() for m in re.findall(rb'/([^\s/\[\]<>()]+)\s+gs', s)))
    res = []
    for cat, names in used.items():
        ent = []
        for n in sorted(names):
            t, v = tmp.xref_get_key(pg.xref, 'Resources/%s/%s' % (cat, n)); assert t == 'xref', (cat, n, t, v)
            ent.append('/%s %s' % (n, v))
        res.append('/%s << %s >>' % (cat, ' '.join(ent)))
    for cat in ('ColorSpace', 'Pattern', 'Shading', 'Properties'):
        t, v = tmp.xref_get_key(pg.xref, 'Resources/' + cat)
        if t not in ('null', 'undefined'): res.append('/%s %s' % (cat, v))
    tmp.xref_set_key(pg.xref, 'Contents', '%d 0 R' % cs[1])
    tmp.xref_set_key(pg.xref, 'Resources', '<< %s >>' % ' '.join(res))
    tmp = fitz.open('pdf', tmp.tobytes(garbage=3, deflate=True))
    # 덧칠을 여러 번 한 자리 — 먼저 쓴 글자가 나중 덧칠에 가려져 있다. 가려진 글자 묶음(BT … ET)은 내용 흐름에서 뺀다
    if not hidden_text(tmp[0]): return tmp
    pg = tmp[0]; cx = pg.get_contents()[0]; st = tmp.xref_stream(cx)
    segs = list(re.finditer(rb'\bBT\b.*?\bET\b', st, re.S)); log = pg.get_bboxlog()
    ti = [i for i, (t, _) in enumerate(log) if t == 'fill-text']; assert len(segs) == len(ti) and all(b' Tf' in m.group(0) for m in segs), (len(segs), len(ti))
    cover = [(i, fitz.Rect(b)) for i, (t, b) in enumerate(log) if t in ('fill-path', 'fill-image', 'fill-shade')]
    hid = [m for m, i in zip(segs, ti) if any(j > i and (c & fitz.Rect(log[i][1])).get_area() > 0.8 * fitz.Rect(log[i][1]).get_area() for j, c in cover)]
    for m in reversed(hid): st = st[:m.start()] + st[m.end():]
    if hid: tmp.update_stream(cx, st); tmp = fitz.open('pdf', tmp.tobytes(garbage=3, deflate=True))
    assert not hidden_text(tmp[0])
    return tmp
def cover_rects(page):
    """덧칠 층의 칠한 상자(옛 글자 · 옛 아이콘을 가리는 칠 — 흰색 · 표 머리 회색)"""
    return [fitz.Rect(d['rect']) for d in page.get_drawings() if d.get('type') in ('f', 'fs') and d.get('fill') and d['rect'].get_area() > 30]
def rehab_slot(pg, key, clip, ff):
    """재활 칸 「1일 2만 / (연간 최대 30만)」(시안의 새 표기 — 회당 금액 + 연 최대)"""
    a = one(pg, r'^1일\s*[\d,]+만$', clip); b = one(pg, r'^\(연간 최대 [\d,]+만\)$', clip)
    num = [s for s in a['spans'] if re.fullmatch(r'[\d,]+', s['text'].strip())][0]; pre = a['spans'][0]
    return [a, b], dict(key=key, kind='rehab', cx=round((a['bbox'].x0 + a['bbox'].x1) / 2, 2), base=round(num['origin'][1], 2), base2=round(b['spans'][0]['origin'][1], 2),
                        size=round(num['size'], 2), psize=round(pre['size'], 2), color='#%06x' % num['color'], size2=round(b['spans'][0]['size'], 2), color2='#%06x' % b['spans'][0]['color'], ff=ff)

def build(src_pdf, old_tpl, old_slots):
    src = fitz.open(src_pdf); old = fitz.open(old_tpl); OS = json.load(open(old_slots, encoding='utf-8'))['slots']
    out = fitz.open(); SL = {}

    # ── 암 보장 ① ② : 앞 판 틀 + 시안 덧칠 층 ──
    for k in ('ca1', 'ca2'):
        pl = patch_layer(src, SRC[k]); pp = pl[0]
        drop = []
        if k == 'ca2':      # 덧칠 속 견본 값(재활 「1일 2만 (연간 최대 40만)」)은 지우고 자리만 적는다
            drop, rh = rehab_slot(pp, 'rh_ca', fitz.Rect(100, 600, 300, 670), 'N')
            wipe(pp, [fitz.Rect(l['bbox'].x0 - 1, l['bbox'].y0, l['bbox'].x1 + 1, l['bbox'].y1) for l in drop])
        assert not re.search(r'\d만|미가입', re.sub(r'약 [\d~,]+천만|[\d~]+천만|연 약 \d천만원?', '', pp.get_text())), ('덧칠 층에 값 글자가 남음', k)
        out.insert_pdf(old, from_page=OLD[k], to_page=OLD[k]); pg = out[-1]
        wr = cover_rects(pp)
        wipe(pg, wr, images=True)                                   # 덧칠에 가려지는 옛 글자 · 옛 아이콘은 틀에서 지운다(글자층 · 파일에 남지 않게)
        pg.show_pdf_page(pg.rect, pl, 0)
        s = [x for x in OS[k] if x['key'] not in ('gender_line', 'rh_ca')]      # 「남성 1위 …」 줄은 시안에서 고정 문구가 됨 · 재활은 새 표기
        if k == 'ca2': s.append(rh)
        SL[k] = s

    # ── 뇌혈관 · 심장 : 시안 쪽 그대로(값 · 바닥글 이름만 지움) ──
    for k in ('brain', 'heart'):
        out.insert_pdf(src, from_page=SRC[k], to_page=SRC[k]); pg = out[-1]; s = []; W = []
        allv = [l for l in lines(pg) if re.fullmatch(VAL_RE, l['text'])]
        rows = {}
        for l in allv: rows.setdefault(round(l['bbox'].y0 / 6), []).append(l)
        R = [sorted(v, key=lambda l: l['bbox'].x0) for _, v in sorted(rows.items()) if len(v) == 5]; assert len(R) == 5, (k, [len(v) for v in rows.values()])
        exdx, t1, t2, t3, sev = R
        s += [slot('p3.ex.' + kk, l, 14.5, '#1f1f22') for (_, kk), l in zip(G2.GS.EX_BH, exdx[:3])]
        dk = ((('p3.dx.뇌혈관', '뇌출혈·뇌경색·뇌동맥류 등'), ('p3.dx.뇌졸중', '뇌출혈·뇌경색 등')) if k == 'brain' else (('p3.dx.허혈성심장', '협심증·급성심근경색 등'), ('p1.bh.dx.급성심근경색', '')))
        s += [slot(kk, l, 14.5, '#e5432f', kind='amt_desc', desc=desc, dsize=7.7, dcolor='#666666') for (kk, desc), l in zip(dk, exdx[3:])]
        cols = G2.BRAIN_COLS if k == 'brain' else G2.HEART_COLS
        for md, r in zip(('first', 'year', 'each'), (t1, t2, t3)):
            s += [slot(c % md, l, 14.5, '#e5432f' if md == 'first' else '#1f1f22') for c, l in zip(cols, r)]
        s += [slot('p3.sev.' + kk, l, 14.5, '#e5432f') for (_, kk), l in zip(G2.GS.SEV, sev)]
        ybot = sev[0]['bbox'].y1
        low = sorted([l for l in allv if l['bbox'].y0 > ybot + 20], key=lambda l: l['bbox'].x0)
        tot = [l for l in low if l['spans'][0]['size'] > 17]; ex = [l for l in low if l['spans'][0]['size'] <= 17]; assert len(tot) == 1 and len(ex) == 3, (k, len(tot), len(ex))
        exk = ('p3.dx.뇌졸중', 'p3.b1.first', 'p3.sev.icu') if k == 'brain' else ('p3.dx.허혈성심장', 'p3.h2.first', 'p3.h2.year')      # 뇌 예시 「뇌경색」 → 뇌졸중(I63) 칸
        s += [slot(kk, l, 14.5, '#1f1f22') for kk, l in zip(exk, ex)]
        s.append(slot('ex_%s_total' % k, tot[0], 20.0, '#2b3a55', usize=11.0, ucolor='#2b3a55', kind='total'))
        rl, rh = rehab_slot(pg, 'rh_bh', fitz.Rect(30, ybot + 20, 200, 800), 'N'); s.append(rh)
        # 설계마다 달라 값처럼 얹는 주석 두 줄의 자리(시안에는 견본이 없다 — 표 아래 빈 띠)
        s.append(dict(key='dx_note', kind='note', x0=31.2, base=round(exdx[0]['bbox'].y1 + 16.5, 2), size=6.4, color='#777777'))
        s.append(dict(key='life_note', kind='life', x1=564.0, top=round(t3[0]['bbox'].y1 + 9.5, 2)))
        ft = one(pg, r'소속', fitz.Rect(380, 790, 600, 835)); fb = ft['bbox']
        s.append(dict(key='footer', kind='footer', x1=round(fb.x1, 2), base=round(ft['spans'][0]['origin'][1], 2), size=round(ft['spans'][0]['size'], 2)))
        W = exdx + t1 + t2 + t3 + sev + low + rl
        wipe(pg, [inner(l['bbox']) for l in W] + [fitz.Rect(fb.x0 - 1, fb.y0, fb.x1 + 2, fb.y1)])
        SL[k] = s

    # ── 안내사항 · 세부내역 틀 : 앞 판 그대로 ──
    for k in ('notice', 'detail'):
        out.insert_pdf(old, from_page=OLD[k], to_page=OLD[k]); SL[k] = OS[k]

    G2.shrink_images(out, dpi=220); G2.dedupe_images(out)
    out.save(OUT_PDF, garbage=4, deflate=True)
    chk = fitz.open(OUT_PDF); txt = ''.join(p.get_text() for p in chk)
    left = [w for w in PERSONAL if w in txt] + [m.group(0) for pat in PERSONAL_RE for m in re.finditer(pat, txt)]; assert not left, ('틀에 개인정보가 남음', left)
    for i, k in enumerate(('ca1', 'ca2', 'brain', 'heart')):
        h = hidden_text(chk[i]); assert not h, ('가려진 글자가 남음', k, h[:80])
        v = re.findall(r'[\d,]+만(?!원|건)|미가입', re.sub(r'약 ?[\d~,]+천만원?|[\d~]+천만|연 ?약 ?\d천만원?', '', chk[i].get_text())); assert not v, ('값 글자가 남음', k, v)
    order = ['ca1', 'ca2', 'brain', 'heart', 'notice', 'detail']
    json.dump(dict(pages=order, size=[round(chk[0].rect.width, 2), round(chk[0].rect.height, 2)], slots=SL), open(OUT_SLOTS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('틀', OUT_PDF, len(chk), '쪽 ·', round(os.path.getsize(OUT_PDF) / 1e6, 2), 'MB · 자리', sum(len(v) for v in SL.values()))

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3])
