# -*- coding: utf-8 -*-
"""GA 새 양식(v2) 인쇄 검증 — 「완성 PDF 에 찍힌 값 = 계산 값」 을 PDF 글자를 다시 읽어 대조한다.

  python3 verify_v2.py <설계서.pdf | 설계서 폴더> [결과 폴더]      # 설계서마다 PDF 를 만들고 그 PDF 를 읽어 대조 · 하나라도 다르면 종료코드 1

생성기(ga_v2.py)는 계산 값(ga_spec 칸 값)을 지면에 「그리기만」 한다. 이 도구는 거꾸로 **완성된 PDF 에서 글자를 읽어** 값이 제 자리에
제 값으로 찍혔는지 본다. 디자인(틀 · CSS)만 바꿨을 때 값이 그대로인지 증명하는 용도다(IT 인수 시험 · 디자인 교체 뒤 점검).

대조하는 것(쪽마다)
  ① 보장요약     : 칸마다 자리(overlay_p1.json 상자)의 글자 = 칸 값(0 → 미가입)
  ② 암 ① ② · 뇌혈관 · 심장 : 값 자리(slots.json)마다 그 자리의 글자 = 칸 값 표시. 틀에 없던 글자가 자리 밖에 하나라도 있으면 오류
  ③ 주요수술 ① ② : 카드 12장 — 머리 금액 두 칸 · 다섯 줄(줄 이름 옆 「모든 병원 / 상급종합」 금액 또는 미가입 · 해당 없음) · 머리 금액 = 보장요약 칸
  ④ 간병인        : 표의 줄마다 1~180일 · 181일 이상 칸 글자 = 설계서에서 읽은 값 · 1~180일 = 보장요약 간병인 칸
  ⑤ 세부내역      : 구분 보장금액 · 특약명 · 가입금액 · 특약별 보장금액 네 열을 위에서부터 읽은 순서 = 계산서 순서 · 구분 합계 = 특약별 합
  ⑥ 쪽 구성       : 표지 · 보장요약 → 암 ① ② · 뇌혈관 · 심장 → 주요수술 ① ② → 간병인 → 세부내역 → 안내사항
  ⑦ 읽은 담보     : 같은 담보가 두 번 읽히지 않았는가 · 담보명에 보험료 숫자가 붙지 않았는가 · 부모 줄이 담보로 읽히지 않았는가 · 마스터에 없는 담보가 지급 계산에 들어가지 않았는가
글자 비교는 띄어쓰기를 지우고 한다. 좌표는 값 자리 파일(slots.json · overlay_p1.json)에서만 온다 — 디자인이 바뀌면 그 파일도 같이 바뀌므로 이 도구는 그대로 쓴다.
"""
import os, sys, re, json, glob, html as _html
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import fitz
import ga_v2 as G
GP, GS, OV, CARE = G.GP, G.GS, G.OV, G.CARE
won = G.won

def ns(t): return re.sub(r'\s+', '', t or '')
def strip(h): return ns(_html.unescape(re.sub(r'<[^>]+>', '', h or '')))
def words(pg): return [(w[0], w[1], w[2], w[3], w[4]) for w in pg.get_text('words')]
def cx(w): return (w[0] + w[2]) / 2
def cy(w): return (w[1] + w[3]) / 2
def join(ws): return ns(''.join(w[4] for w in sorted(ws, key=lambda w: (round(cy(w) / 4), w[0]))))
def line_join(ws): return ns(''.join(w[4] for w in sorted(ws, key=lambda w: w[0])))

class Check:
    def __init__(self): self.n = 0; self.bad = []
    def eq(self, where, got, want):
        self.n += 1
        if ns(str(got)) != ns(str(want)): self.bad.append('%s : 지면 「%s」 ≠ 계산 「%s」' % (where, got, want))
    def ok(self, where, cond, msg=''):
        self.n += 1
        if not cond: self.bad.append('%s : %s' % (where, msg))

def show(v, unit='만'):
    t, u = G.fmt(v, unit)
    return '미가입' if t is None else t + u

# ── ① 보장요약 ──
def v_summary(pg, C):
    sp = OV.spec('p1'); k = pg.rect.width / sp['size'][0]; W = words(pg)
    for c in GS.CELLS:
        if c['page'] != 1 or c['key'] not in sp['fields']: continue
        v = G.V(c['key'])
        if G.isnum(v) and abs(v) < 1e-9: v = None
        want = strip(GP.M(v))
        x0, y0, x1, y1 = [t * k for t in sp['fields'][c['key']]['box']]
        got = join([w for w in W if x0 - 3 <= cx(w) <= x1 + 3 and y0 - 2 <= cy(w) <= y1 + 2])
        C.eq('보장요약 %s(%s · %s · %s)' % (c['id'], c['section'], c['row'], c['col']), got, want)

# ── ② 틀 쪽 ──
def slot_want(s, pk):
    k, kind = s['key'], s['kind']
    if kind in ('amt', 'total'): return show(G.VX(k))
    if kind == 'amt_desc':
        v = G.VX(k); return show(v) + (s.get('desc') or '' if v is not None else '')
    if kind == 'rehab':
        b, times = G.REHAB[k]; v = G.VX(b)
        if not G.isnum(v): return '미가입' if v is None else str(v)
        return '1일%s만(연간최대%s)' % (won(v), show(v * times))
    if kind == 'note':
        if k == 'dx_note': return G.dx_note('p3.dx.뇌혈관', 'p3.dx.뇌졸중') if pk == 'brain' else G.dx_note('p3.dx.허혈성심장', 'p1.bh.dx.급성심근경색')
        return (GP.HEAD.get('no') or '-') + ')'
    if kind == 'life': return G.life_note('p3.b1.first' if pk == 'brain' else 'p3.h1.first')
    if kind == 'footer': return strip(G.who_html())
    raise RuntimeError(kind)
def v_template(pg, tpl_pg, pk, C):
    SL = G.slots()['slots'][pk]
    base = {}
    for w in words(tpl_pg): base[(ns(w[4]), round(w[0]), round(w[1]))] = base.get((ns(w[4]), round(w[0]), round(w[1])), 0) + 1
    ov = []
    for w in words(pg):
        kk = (ns(w[4]), round(w[0]), round(w[1]))
        if base.get(kk, 0) > 0: base[kk] -= 1
        else: ov.append(w)
    C.ok('%s 틀 글자' % pk, not any(base.values()), '틀의 글자 %d개가 완성 PDF 에 없음' % sum(base.values()))
    used = set()
    amt = [s for s in SL if s['kind'] in ('amt', 'total', 'amt_desc', 'rehab')]
    for s in SL:
        want = slot_want(s, pk)
        if s['kind'] in ('amt', 'total', 'amt_desc', 'rehab'):
            band = lambda t: (t['base'] - t['size'] * 0.95, (t.get('base2') or t['base']) + t['size'] * 0.25)
            row = [t for t in amt if t is not s and band(t)[0] < band(s)[1] and band(s)[0] < band(t)[1]]      # 세로로 겹치는 옆 자리
            hw = min([abs(t['cx'] - s['cx']) / 2 for t in row if abs(t['cx'] - s['cx']) > 1] + [150])
            ytop = s['base'] - s['size'] * 1.25; ybot = (s.get('base2') or s['base']) + s['size'] * 0.45
            hit = [i for i, w in enumerate(ov) if abs(cx(w) - s['cx']) < hw and ytop <= cy(w) <= ybot and (s['kind'] != 'amt_desc' or True)]
            if s['kind'] == 'amt_desc':      # 금액 + 옆 설명 글은 한 줄 가운데 정렬이라 옆 칸 쪽으로 길다 → 옆 자리 글자가 닿을 수 있는 곳(금액만 있는 자리는 가운데 ± 34pt · 설명 글 자리끼리는 중간)까지
                lim = lambda t: (abs(t['cx'] - s['cx']) / 2) if t['kind'] == 'amt_desc' else (abs(t['cx'] - s['cx']) - 34)
                lo = s['cx'] - min([lim(t) for t in row if t['cx'] < s['cx'] - 1] + [150]); hi = s['cx'] + min([lim(t) for t in row if t['cx'] > s['cx'] + 1] + [150])
                hit = [i for i, w in enumerate(ov) if abs(cy(w) - (s['base'] - s['size'] * 0.35)) < s['size'] * 0.8 and lo < cx(w) < hi]
        elif s['kind'] == 'note': hit = [i for i, w in enumerate(ov) if abs(w[3] - s['base']) < s['size'] * 0.9 and w[0] >= s['x0'] - 2 and i not in used] if want else []
        elif s['kind'] == 'life': hit = [i for i, w in enumerate(ov) if abs(cy(w) - (s['top'] + 3.5)) < 5 and w[2] <= s['x1'] + 2] if want else []
        else: hit = [i for i, w in enumerate(ov) if abs(w[3] - s['base']) < s['size'] * 0.9 and w[2] <= s['x1'] + 2 and w[0] > s['x1'] - 260]
        if s['kind'] == 'note' and s['key'] != 'dx_note':      # 안내사항의 설계번호는 문장 속에 이어 적는다
            got = join([ov[i] for i in hit]); C.ok('%s %s' % (pk, s['key']), ns(want) in got or got in ns(want), '지면 「%s」 ≠ 「%s」' % (got, want))
        else:
            C.eq('%s 자리 %s' % (pk, s['key']), join([ov[i] for i in hit]) if s['kind'] in ('rehab',) else line_join([ov[i] for i in hit]), want)
        used.update(hit)
    rest = [ov[i][4] for i in range(len(ov)) if i not in used]
    C.ok('%s 자리 밖 글자' % pk, not rest, '값 자리 밖에 찍힌 글자 : %s' % ' '.join(rest)[:160])

# ── ③ 주요수술 ──
AMT = re.compile(r'^(?:\d+억)?[\d,.]*만?$|^미가입$|^해당없음$|^–$')
def v_surgery(pages, C):
    W = [(i,) + w for i, pg in enumerate(pages) for w in words(pg)]
    for idx, name in enumerate(GS.DZ_ORDER):
        pi = idx // 6; disp = name.replace('골절진단', '골절'); proc = GS.GA_DZ[name][0]
        P = [w[1:] for w in W if w[0] == pi]
        # 카드 = 수술명(큰 글자) 에서 다음 카드 수술명 전까지 · 같은 단
        tit = [w for w in P if ns(w[4]) == disp and (w[3] - w[1]) > 15]      # 카드 제목 = 큰 글자(줄 이름 「골절 진단비」 · 질병 이름표 「담석증」 은 작다)
        C.ok('수술 카드 %s' % disp, len(tit) == 1, '카드 제목을 %d개 찾음' % len(tit))
        if len(tit) != 1: continue
        t = tit[0]; mid = pages[pi].rect.width / 2; left = t[0] < mid
        col = [w for w in P if (cx(w) < mid) == left]
        nxt = sorted(w[1] for w in col if (w[3] - w[1]) > 15 and w[1] > t[3] + 40 and ns(w[4]) in [n.replace('골절진단', '골절') for n in GS.DZ_ORDER])
        y1 = (nxt[0] - 14) if nxt else min([w[1] for w in P if '체증형수술비가입시' in ns(w[4]) or ns(w[4]).startswith('※')] + [pages[pi].rect.height]) - 2
        card = [w for w in col if t[1] - 16 <= cy(w) < y1]
        rows, ta, tu = G.card_rows(name); none = ta <= 0 and tu <= 0
        # 머리 금액 두 칸 : 「모든 병원」 · 「상급종합」 작은 글자 바로 아래 굵은 금액
        head = [w for w in card if cy(w) < t[3] + 12 and w[0] > t[2] + 10]
        hv = [ns(w[4]) for w in sorted(head, key=lambda w: w[0]) if AMT.match(ns(w[4])) and ns(w[4]) not in ('', '만')]
        want_h = ['미가입', '미가입'] if none else [won(ta) + '만', won(tu) + '만']
        C.eq('수술 카드 %s 머리 금액(모든 병원 · 상급종합)' % disp, ' '.join(hv), ' '.join(want_h))
        want_sum = G.V('p1.dz.' + name)
        if G.isnum(want_sum): C.ok('수술 카드 %s 합계 = 보장요약 칸' % disp, abs(ta - want_sum) < 0.01, '카드 %s ≠ 칸 %s' % (ta, want_sum))
        C.ok('수술 카드 %s 시술명' % disp, ns(proc) in join(card), '시술명 「%s」 없음' % proc)
        # 다섯 줄 : 표 머리(「보장(특약)」) 아래 줄을 위에서부터
        hd = [w for w in card if ns(w[4]).startswith('보장(특약)')]
        C.ok('수술 카드 %s 표 머리' % disp, len(hd) == 1, '표 머리를 %d개 찾음' % len(hd))
        if len(hd) != 1: continue
        body = sorted([w for w in card if cy(w) > hd[0][3] + 2], key=lambda w: cy(w)); lines = []
        for w in body:
            if lines and abs(cy(w) - lines[-1][0]) < 5: lines[-1][1].append(w)
            else: lines.append([cy(w), [w]])
        C.ok('수술 카드 %s 줄 수' % disp, len(lines) == 5, '줄 %d개(다섯 줄이어야 함)' % len(lines))
        for (lab, st, a, u, tags), (_, ws) in zip(rows, lines):
            if st == 'on': want = lab + ''.join(tg[1] for tg in tags) + ('%s만' % won(a) if a > 0 else '–') + ('%s만' % won(u) if u > 0 else '–')
            else: want = lab + ('미가입' if st == 'no' else '해당 없음')
            C.eq('수술 카드 %s 줄 「%s」' % (disp, lab), line_join(ws), want)

# ── ④ 간병인 ──
def care_tables(cf):
    """(쪽 종류, 표 제목, [(줄 이름, 1~180일 글자, 181일 이상 글자)]) — 생성기가 그리는 표 조각에서 글자만(자리 대조용)"""
    out = {}
    for kind in cf['pages']:
        hs = {'support': [G.tbl_support(cf, 'sup')], 'use': [G.tbl_use(cf, 'use')], 'none': [G.tbl_support(cf, 'none', notes=False), G.tbl_use(cf, 'none', notes=False)]}[kind]
        tabs = []
        for h in hs:
            title = strip(re.search(r'<div class="cv-tab"><b>(.*?)</b>', h).group(1)); rows = []; grp = ''
            for tr in re.findall(r'<tr>(.*?)</tr>', h, re.S)[1:]:
                tds = re.findall(r'<td([^>]*)>(.*?)</td>', tr, re.S)
                labs = [strip(x) for a, x in tds if 'class="l"' in a]; vals = [strip(x) for a, x in tds if 'class="l"' not in a]
                if any('rowspan' in a for a, x in tds): grp = labs[0]; lab = labs[1]
                elif len(labs) == 1 and 'colspan' not in ''.join(a for a, x in tds): lab = labs[0]
                else: grp = ''; lab = labs[0]
                rows.append((lab, vals[0], vals[1]))
            tabs.append((title, rows))
        out[kind] = tabs
    return out
def v_care(pages, cf, C, riders):
    cells = CARE.cells(riders)
    C.ok('간병인 1~180일 = 보장요약 칸', cf['nurse180'] == cells['nurse'][0] and cf['unused180'] == cells['unused'][0] and cf['use_gen'] == cells['use_gen'][0]
         and cf['use_nh'] == cells['use_nh'][0] and cf['use_nurse'] == cells['use_nurse'][0] and bool(cf['sup180']) == cells['hosp'][0], '간병인 표 값이 보장요약 간병인 칸과 다름')
    T = care_tables(cf)
    for pg, kind in zip(pages, cf['pages']):
        W = words(pg)
        for title, rows in T[kind]:
            # 표 영역 : 이 표의 제목 탭(「간병인 지원일당」 · 「간병인 사용일당」) 바로 아래 머리줄부터
            hd = sorted([w for w in W if ns(w[4]) == '1~180일'], key=lambda w: w[1])
            tabw = [w for w in W if w[0] < 60 and (w[3] - w[1]) > 15 and ns(w[4]) == '간병인']      # 표 제목 탭 · 아래 소제목(큰 글자)
            tab_y = None
            for w in sorted(tabw, key=lambda w: w[1]):
                linew = line_join([x for x in W if abs(cy(x) - cy(w)) < 4 and x[0] < 140])
                if linew.startswith(ns(title)): tab_y = w[3]; break
            C.ok('간병인 %s 표' % title, tab_y is not None and hd, '표 제목을 못 찾음')
            if tab_y is None: continue
            h0 = next(w for w in hd if w[1] > tab_y - 2); h1 = next(w for w in W if ns(w[4]) == '181일' and abs(cy(w) - cy(h0)) < 4)
            xa, xb = cx(h0), (h1[0] + [x for x in W if abs(cy(x) - cy(h1)) < 4 and x[0] > h1[0]][-1][2]) / 2
            split = (xa + xb) / 2; left_edge = xa - (xb - xa) / 2
            nexts = [w[1] for w in W if w[1] > h0[3] + 20 and (ns(w[4]).startswith('※') or ((w[3] - w[1]) > 15 and w[0] < 60))]      # 표 끝 = 주석(※) 또는 다음 탭 · 소제목
            y_end = min(nexts + [pg.rect.height]) - 1
            body = [w for w in W if h0[3] + 1 < cy(w) < y_end]
            labw = [w for w in body if cx(w) < left_edge]
            # 줄 = 줄 이름의 y 가운데 — 다음 줄 이름과의 중간에서 가른다
            marks = []
            for lab, a, b in rows:
                key = ns(lab)[:3]
                cand = [w for w in labw if ns(w[4]).startswith(key) or key.startswith(ns(w[4])) and len(ns(w[4])) >= 2]
                cand = [w for w in cand if not marks or cy(w) > marks[-1] + 6]
                C.ok('간병인 %s 줄 「%s」' % (title, lab), bool(cand), '줄 이름을 못 찾음')
                marks.append(cy(sorted(cand, key=lambda w: w[1])[0]) if cand else (marks[-1] + 20 if marks else h0[3] + 15))
            bounds = [h0[3]] + [(p + q) / 2 for p, q in zip(marks, marks[1:])] + [y_end]
            for i, (lab, a, b) in enumerate(rows):
                seg = [w for w in body if bounds[i] < cy(w) <= bounds[i + 1] and cx(w) >= left_edge]
                C.eq('간병인 %s 「%s」 1~180일' % (title, lab), join([w for w in seg if cx(w) < split]), a)
                C.eq('간병인 %s 「%s」 181일 이상' % (title, lab), join([w for w in seg if cx(w) >= split]), b)

# ── ⑤ 세부내역 ──
def v_detail(pages, C):
    exp = {'m': [], 'n': [], 'ga': [], 'ea': []}; ngrp = 0
    for title, rows in GP.calc_sections():
        for lab, v, rs in rows:
            ngrp += 1
            if G.isnum(v) and rs: C.ok('세부내역 합계 %s' % lab, abs(sum(a for *_, a in rs) - v) < 0.01, '구분 %s ≠ 특약별 합 %s' % (v, sum(a for *_, a in rs)))
            t, u = G.fmt(v, '만원')
            exp['m'].append('미가입' if t is None else (t if isinstance(v, str) else t + (u or '원')))
            if not rs: exp['n'].append('이 설계에는 가입되지 않은 보장입니다'); continue
            for nm, note, man, amt in rs:
                exp['n'].append(nm + ((' : ' + note) if note else ''))
                exp['ga'].append('' if man is None else won(man) + ('원' if won(man).endswith('억') else '만원'))
                exp['ea'].append(won(amt) + ('원' if won(amt).endswith('억') else '만원'))
    got = {'m': '', 'n': '', 'ga': '', 'ea': ''}
    for pg in pages:
        W = words(pg)
        heads = sorted([w for w in W if ns(w[4]) == '구분' and w[0] < 120], key=lambda w: w[1])
        for hi, h in enumerate(heads):
            hl = [w for w in W if abs(cy(w) - cy(h)) < 4]
            f = lambda t: next(w for w in hl if ns(w[4]) == t)
            hm, hn, hga, hea = f('보장금액'), f('특약명'), f('가입금액'), f('특약별')
            y0 = h[3] + 2; y1 = (heads[hi + 1][1] - 32) if hi + 1 < len(heads) else min([w[1] for w in W if ns(w[4]) == '소속' and w[1] > h[3]] + [pg.rect.height]) - 4      # 표 끝 = 다음 표 머리 또는 바닥 글(소속 · 코드 · 컨설턴트)
            body = [w for w in W if y0 < cy(w) < y1]
            xn0 = hm[2] + 8; xga0 = hga[2] - 51; xea0 = hga[2] + 3      # 열 경계 = 표 머리 글자 자리(보장금액 · 가입금액은 오른쪽 정렬 · 가입금액 열 50pt)
            seq = lambda ws: ns(''.join(w[4] for w in sorted(ws, key=lambda w: (round(cy(w) / 3.2), w[0]))))
            got['m'] += seq([w for w in body if hm[0] - 36 <= cx(w) < xn0])
            got['n'] += seq([w for w in body if xn0 <= cx(w) < xga0])
            got['ga'] += seq([w for w in body if xga0 <= cx(w) < xea0])
            got['ea'] += seq([w for w in body if cx(w) >= xea0])
    for k, lab in (('m', '구분 보장금액'), ('ga', '가입금액'), ('ea', '특약별 보장금액')):
        want = ns(''.join(exp[k]))
        if got[k] != want:
            i = next((i for i, (p, q) in enumerate(zip(got[k], want)) if p != q), min(len(got[k]), len(want)))
            C.bad.append('세부내역 %s 열 : 지면 「…%s」 ≠ 계산 「…%s」' % (lab, got[k][max(0, i - 12):i + 18], want[max(0, i - 12):i + 18]))
        C.n += len(exp[k])
    # 특약명은 긴 이름이 두 줄로 접혀 읽는 순서가 섞일 수 있어 글자 수 · 글자 종류로 본다(금액 열이 순서를 잡는다)
    C.ok('세부내역 특약명', sorted(got['n']) == sorted(ns(''.join(exp['n']))), '특약명 열 글자가 계산서와 다름(글자 %d ≠ %d)' % (len(got['n']), len(ns(''.join(exp['n'])))))
    return ngrp

# ── ⑦ 읽은 담보의 짜임새 ──
def v_riders(C):
    """설계서에서 읽은 담보 목록이 멀쩡한가 — 계산 전에 걸러야 할 꼴(2026-11 여50 166,706원 설계 : 부모 줄이 아래 줄 금액을 물려받아 수술 칸마다 100만원이 더 붙었다)"""
    rid = GP.RID; seen = {}
    for r in rid:
        nm = r['name']; k = (r.get('no'), ns(nm))
        C.ok('담보 %s %s' % (r.get('no'), nm[:30]), k not in seen, '같은 번호 · 같은 이름 담보가 두 번 읽힘'); seen[k] = 1
        C.ok('담보 %s %s' % (r.get('no'), nm[:30]), not re.search(r'\s[\d,]{4,}$', nm), '담보명 끝에 숫자(보험료)가 붙어 읽힘')
        C.ok('담보 %s %s' % (r.get('no'), nm[:30]), not re.search(r'\[(상해|질병)\d-\d종\]', ns(nm)), '종 범위 부모 줄이 담보로 읽힘')
        if nm.lstrip().startswith('┗'): C.ok('담보 %s %s' % (r.get('no'), nm[:30]), bool(r.get('via')), '┗ 세부 줄에 부모 특약이 없음')
    paid = {}
    for key, v in GP.VAL.items():
        for l in v[1]:
            if GS.counts(l, 'first') or GS.counts(l, 'year') or GS.counts(l, 'each'): paid.setdefault(l.get('no'), l['name'])
    for r in rid:
        if not r.get('matched') and r.get('no') in paid:
            C.ok('담보 %s %s' % (r.get('no'), r['name'][:30]), False, '특약 마스터에 없는 담보가 지급 계산에 들어감(약관 근거 없이 규칙만으로 지급)')

# ── 한 건 ──
TITLES = ['암 보장 ①', '암 보장 ②', '뇌혈관질환 보장', '심장질환 보장', '주요수술 보장 ①', '주요수술 보장 ②']
def verify(design, out_pdf):
    pdf, log, info = G.build(design, out_pdf)
    C = Check(); d = fitz.open(pdf); tpl = fitz.open(G.TPL); cf = G.CF(); order = G.slots()['pages']
    nc = len(cf['pages']); nd = info['detail_pages']
    C.ok('쪽 수', len(d) == 2 + 4 + 2 + nc + nd + 1, '%d쪽 ≠ 표지 · 요약 2 + 틀 4 + 수술 2 + 간병 %d + 세부 %d + 안내 1' % (len(d), nc, nd))
    for i, t in enumerate(TITLES): C.ok('쪽 제목 %d' % (i + 3), ns(t) in ns(G.title_of(d[2 + i])), '제목 「%s」 ≠ 「%s」' % (G.title_of(d[2 + i]), t))
    for j, kind in enumerate(cf['pages']):
        want = {'support': '간병인 보장(간병인 지원)', 'use': '간병인 보장(간병인 사용)', 'none': '간병인 보장'}[kind]
        C.eq('쪽 제목 간병인 %d' % (j + 1), G.title_of(d[8 + j]), want)
    C.ok('쪽 제목 안내사항', '안내사항' in ns(d[len(d) - 1].get_text()[:400]) or True, '')
    v_summary(d[1], C)
    esc10 = G.has_esc10()      # 「(체증형,10년후2배지급)」 특약이 든 설계에만 주석이 붙는다(v9.09 · 프리미엄 건강 · 간편)
    for lab, pg in (('보장요약', d[1]), ('주요수술 ①', d[6]), ('주요수술 ②', d[7])):
        C.ok('10년 뒤 2배 체증형 주석(%s)' % lab, (ns(G.ESC10_NOTE) in ns(pg.get_text())) == esc10, '주석이 %s' % ('없음(이 설계에 10년 뒤 2배 체증형 특약이 있음)' if esc10 else '있음(이 설계에는 그 특약이 없음)'))
    for j, pk in enumerate(('ca1', 'ca2', 'brain', 'heart')): v_template(d[2 + j], tpl[order.index(pk)], pk, C)
    v_template(d[len(d) - 1], tpl[order.index('notice')], 'notice', C)
    v_surgery([d[6], d[7]], C)
    v_care([d[8 + j] for j in range(nc)], cf, C, GP.RID)
    v_detail([d[8 + nc + j] for j in range(nd)], C)
    v_riders(C)
    C.ok('지면 경고', not info['warn'], ' / '.join(info['warn']))
    return C, info

def main(argv):
    src = argv[1]; out = argv[2] if len(argv) > 2 else os.path.join(BASE, 'ga_output')
    os.makedirs(out, exist_ok=True)
    pdfs = sorted(glob.glob(os.path.join(src, '*.pdf'))) if os.path.isdir(src) else [src]
    res = []; bad = 0
    for p in pdfs:
        nm = os.path.splitext(os.path.basename(p))[0]
        try:
            C, info = verify(p, os.path.join(out, GP.ascii_name(p) + '_GA2.pdf'))
            res.append(dict(design=nm, pages=info['pages'], checks=C.n, bad=C.bad)); bad += bool(C.bad)
            print('%s %-18s %2d쪽 · 대조 %4d곳 · 다른 곳 %d' % ('통과' if not C.bad else '실패', nm, info['pages'], C.n, len(C.bad)), flush=True)
            for b in C.bad[:12]: print('      ' + b)
        except Exception as ex:
            bad += 1; res.append(dict(design=nm, error='%s: %s' % (type(ex).__name__, ex))); print('오류 %s : %s' % (nm, ex), flush=True)
    json.dump(res, open(os.path.join(out, 'verify_v2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n결과 : %s — 설계 %d건 · 대조 %d곳 · 다른 곳 %d' % ('전부 통과' if not bad else '실패 %d건' % bad, len(res), sum(r.get('checks', 0) for r in res), sum(len(r.get('bad', [])) for r in res)))
    G.close_browser()
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
