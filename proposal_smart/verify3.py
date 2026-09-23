# -*- coding: utf-8 -*-
"""3차 안전장치 — 상품설명서 뒤쪽 「○○ 특약 안내사항」 표로 금액을 되짚는다 (v8.41).

상품설명서 뒤에는 통합치료비처럼 구조가 복잡한 특약의 **항목별 지급금액 표**가 그대로 실려 있다.

    통합치료항목            지급횟수     지급금액
    검사   암 내시경검사(급여)   연간 1회한    5만원
    …
    연간 총 지급액 한도                    1억원
    ─ 암 통합치료비(기본형) 특약 안내사항 ─

1차(약관 지급금액표)·2차(담보별 요약 설명문)와 **출처가 다른 세 번째 눈**이다.
여기서 하는 일은 대조뿐이다 — 금액을 새로 만들지 않고, 우리 표와 설계서 표가
항목·금액·연간 한도까지 같은지 확인해 감사 로그에 남긴다.
다르면 '3차대조' 로 남겨 사람이 약관을 다시 보게 한다.

사용 : python3 verify3.py 상품설명서.pdf
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
HEAD = re.compile(r'([^\n]{4,60}?)\s*특약\s*안내사항')
MAN = re.compile(r'([\d,.]+)\s*(억)?\s*([\d,]*)\s*만?원')


def man(s):
    """'1억원' → 10000 · '3,000만원' → 3000 · '0.5만원' → 0.5 · 없으면 None"""
    t = re.sub(r'\s+', '', s or '')
    m = re.fullmatch(r'([\d,]+)억(?:([\d,]+)만원)?', t)
    if m:
        return int(m.group(1).replace(',', '')) * 10000 + (int(m.group(2).replace(',', '')) if m.group(2) else 0)
    m = re.fullmatch(r'([\d,.]+)만원', t)
    return float(m.group(1).replace(',', '')) if m else None


def norm(label):
    """항목명 정규화 — 표기 차이(선지급 ▶ · 비급여 접두어 · 입원/외래 구분)를 지운다"""
    t = re.sub(r'\s+', '', label or '')
    t = t.replace('▶', '')
    t = re.sub(r'^비급여\(전액본인부담포함\)', '', t)
    t = re.sub(r'^(입원·외래|입원및외래|입원|외래)', '', t)
    t = t.replace('검사검사', '검사')          # 설계서 표기 흔들림(골밀도검사검사)
    return t


def read_tables(src):
    """상품설명서 → {담보명: {'items': {정규화항목: 금액}, 'raw': [(항목, 횟수, 금액)], 'cap': 연간한도, 'page': 쪽}}"""
    import pymupdf
    out = {}
    doc = pymupdf.open(src)
    for i, page in enumerate(doc):
        text = page.get_text()
        m = HEAD.search(text)
        if not m:
            continue
        nm = m.group(1).strip()
        if not nm or '안내' in nm:
            continue
        items, raw, cap = {}, [], None
        try:
            tabs = page.find_tables().tables
        except Exception:
            continue
        for t in tabs:
            rows = [[re.sub(r'\s+', ' ', str(c or '')).strip() if c not in (None, 'None') else '' for c in r]
                    for r in t.extract()]
            if not rows or not any('통합치료항목' in ''.join(r) for r in rows[:2]):
                continue
            hd = rows[0]
            ci = {h: n for n, h in enumerate(hd)}
            i_amt = ci.get('지급금액', len(hd) - 1)
            i_cnt = ci.get('지급횟수', i_amt - 1)
            # 항목명은 '통합치료항목' 칸에서만 읽는다 — '통합치료항목별 대상질병' 칸을 항목명으로
            # 잘못 읽으면 '암(유사암제외)' 같은 질병명이 항목으로 잡힌다.
            i_end = next((n for h, n in ci.items() if '대상질병' in h), i_cnt)
            for r in rows[1:]:
                a = man(r[i_amt] if i_amt < len(r) else '')
                # 항목명 : 지급횟수 칸 앞의 셀 중 마지막으로 값이 있는 것(묶음명은 맨 앞 칸)
                lbl = next((c for c in reversed(r[:i_end]) if c), '')
                if '연간 총 지급액 한도' in re.sub(r'\s+', ' ', ''.join(r)):
                    cap = cap or a or man(' '.join(x for x in r if x))
                    continue
                if a is None or not lbl:
                    continue
                cnt = r[i_cnt] if i_cnt < len(r) else ''
                items[norm(lbl)] = a
                raw.append((lbl, cnt, a))
        if items:
            out[nm] = {'items': items, 'raw': raw, 'cap': cap, 'page': i + 1}
    return out


def ours(rider):
    """우리가 계산 근거로 쓰는 항목표 → {정규화항목: 금액} · 없으면 None"""
    import scen_engine as S
    rid = S.itc_id(rider['name'])
    if rid:
        r = S.itc.RM[rid]
        amts = S.itc.AMT[r['ty']].get(str(rider['man']))
        if not amts:
            return None
        return {norm(it['l']): a for it, a in zip(S.itc.IT[r['ty']], amts) if a > 0}
    inj = json.load(open(os.path.join(BASE, 'inj_itc.json'), encoding='utf-8'))
    for k, tiers in inj.items():
        if S.nname(k) in (S.nname(rider['name']), S.noren(rider['name'])):
            its = tiers.get(str(rider['man']))
            if its:
                return {norm(it['l']): it['amt'] for it in its}
    return None


def compare(riders, src, log=None):
    """설계 담보 ↔ 설계서 뒤쪽 표 대조 → [{담보, 쪽, 항목수, 일치, 차이, 한도}]"""
    import scen_engine as S
    try:
        tab = read_tables(src)
    except Exception as e:
        return [{'오류': '%s: %s' % (type(e).__name__, e)}]
    key = lambda n: S.noren(n)
    byname = {key(k): v for k, v in tab.items()}
    out = []
    for r in riders:
        t = byname.get(key(r['name']))
        if not t:
            continue
        mine = ours(r)
        if mine is None:
            out.append({'담보': r['name'], '쪽': t['page'], '항목수': len(t['items']),
                        '일치': None, '차이': [], '사유': '우리 금액표에 이 가입금액 구간이 없어 대조하지 못함'})
            if log: log('3차대조', r['name'], '설계서 뒤쪽 특약 안내사항 표(p.%d)는 있으나 우리 금액표에 가입금액 %g만원 구간이 없어 대조 못함' % (t['page'], r['man']))
            continue
        # 안내표를 **1년 경과 전(감액) 기준**으로 싣는 담보가 있다(예 암 통합치료비Ⅱ : 표 375 / 약관 750).
        # 우리 표는 1년 경과 후 기준이므로, 두 기준 모두로 맞춰 보고 하나라도 맞으면 일치로 본다.
        cut = (r.get('desc2') or {}).get('cut_1y')
        best, base = None, 1.0
        for f in ([1.0, cut] if cut and 0 < cut < 1 else [1.0]):
            d = []
            for k, v in t['items'].items():
                if k not in mine:
                    d.append((k, v, None))
                elif abs(mine[k] * f - v) > 1e-9:
                    d.append((k, v, mine[k] * f))
            if best is None or len(d) < len(best):
                best, base = d, f
        diff = best
        only = [k for k in mine if k not in t['items']]
        capok = (t['cap'] is None) or (abs(t['cap'] - r['man'] * base) < 1e-9)
        out.append({'담보': r['name'], '쪽': t['page'], '항목수': len(t['items']),
                    '일치': (not diff and not only and capok), '차이': diff,
                    '우리만': only, '한도': (t['cap'], r['man'] * base),
                    '기준': ('1년 경과 후' if base == 1.0 else '1년 경과 전(%g%% 감액)' % (base * 100))})
        if log and (diff or only or not capok):
            log('3차대조', r['name'],
                '설계서 뒤쪽 표(p.%d)와 다름 — %s%s%s' % (
                    t['page'],
                    ' · '.join('%s 설계서 %g / 우리 %s' % (k, v, '없음' if o is None else '%g' % o) for k, v, o in diff[:3]),
                    (' · 설계서 표에 없는 항목 %d개' % len(only)) if only else '',
                    (' · 연간 한도 설계서 %s / 가입금액 %g' % (t['cap'], r['man'])) if not capok else ''))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    sys.path.insert(0, BASE)
    import matcher, build_all, desc_engine as DE
    src = sys.argv[1]
    rows = matcher.read_proposal(src)
    rows = matcher.read_proposal(src, line=build_all.guess_line(rows))
    rows, _info = DE.attach(rows, src)          # 1년 이내 감액 여부(cut_1y)가 있어야 안내표 기준을 가린다
    res = compare(rows, src)
    if not res:
        print('설계서 뒤쪽에 「특약 안내사항」 표가 없습니다.'); return
    for x in res:
        if '오류' in x:
            print('오류 :', x['오류']); continue
        mark = '일치' if x['일치'] else ('대조못함' if x['일치'] is None else '다름')
        print('■ %-44s p%-4d 항목 %2d개  %s  (안내표 %s 기준)' % (x['담보'][:44], x['쪽'], x['항목수'], mark, x.get('기준', '-')))
        for k, v, o in x.get('차이', []):
            print('     %-40s 설계서 %8s / 우리 %s' % (k[:40], format(v, ',g'), '없음' if o is None else format(o, ',g')))
        for k in x.get('우리만', []):
            print('     %-40s 설계서 표에 없음' % k[:40])
        if x.get('한도') and x['한도'][0] is not None and abs(x['한도'][0] - x['한도'][1]) > 1e-9:
            print('     연간 총 지급액 한도 설계서 %g / 가입금액 %g' % x['한도'])


if __name__ == '__main__':
    main()
