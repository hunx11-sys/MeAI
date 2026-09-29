# -*- coding: utf-8 -*-
"""
약관 전수 감사(2026.09) — 자동 변환이 안 되는 수정(수가코드·별표 쪽번호·행 이름·본문 잘림·빠진 특약)

실행 순서 : python3 scripts/fix_audit.py docs/audit2609/ops_auto.json <PDF텍스트폴더> --write
            python3 scripts/fix_audit2609_manual.py <PDF텍스트폴더> [--write]

원칙
  · 수가코드(hc)를 넣을 때도 근거 쪽(앞 8쪽~뒤 5쪽) 원문에 그 코드 글자가 있어야 넣는다. 없으면 보류.
  · 행 이름은 질병코드 이름표(codenames, KCD 명칭)로 바꾼다 — 코드 한 개짜리 행만. 여러 코드 행은 감사자가
    원문에서 옮긴 이름을 쓴다.
  · 본문(b)은 지정한 글자를 정확히 찾았을 때만 자른다/붙인다. 세부보장이 부모 본문을 같이 쓰면 함께 고친다.
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import inflate, deflate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
KEY = {'통합간편': 'tong', '케어프리': 'care', '운전자': 'drv', '치아': 'tooth', '또또암': 'tt', '또또암간편': 'ttg'}
OFF = {'통합간편': 1, '케어프리': 1, '운전자': 1, '치아': 1, '또또암': 0, '또또암간편': 0}

LA = ('LA210 LA321 LA322 LA222 LA223 LA224 LA225 LA226 LA227 LA228 LA330 LA340 LA341 LA232 LA233 LA234 LA241 LA242 '
      'LA243 LA244 LA245 LA247 LA248 LA249 LA346 LA347 LA270 LA271 LA272 LA273 LA274 LA275 LA276 LA251 LA253 LA352 '
      'LA353 LA354 LA355 LA356 LA357 LA358 LA359 LA261 LA264 LA265 LA361 LA362 LA366 LA367').split()
LB = 'LB310 LB320 LB331 LB333 LB334 LB335 LB336 LB341 LB342 LB343 LB344 LB345 LB346 LB351 LB353 LB354 LB355 LB412 LB413'.split()

# (특약, 근거 쪽들, 더할 코드, 뺄 코드, 통째로 둘 코드(None=안 바꿈), 세부까지?)
HC = [
    ('통49', [800], ['HD412'], [], None, False),
    ('통154', [800], ['HD412'], [], None, False),
    ('통218', [1376], [], [], ['HD113', 'HD114', 'HD115'], False),       # HD110·HD111·HZ271 은 약관이 '보장하지 않는' 예시
    ('케317', [1392], [], [], ['HD113', 'HD114', 'HD115'], False),
    ('또225', [685], [], [], ['HD113', 'HD114', 'HD115'], False),
    ('케12', [934], 'N0011 N0012 N0053 N0054 N0057 N0058 NA055 NA056 NA057 NA058'.split(), [], None, False),
    ('케137', [906], LA + LB, [], None, False),
    ('케204', [630, 906], LA + LB, [], None, False),
    ('케205', [643, 906], LA + LB, [], None, False),
    ('또간148', [296, 466], LA + LB, [], None, False),
    ('또간150', [321, 466], LA + LB, [], None, False),
    ('운96', [510], 'N0304 N0305 N0306 N0307 N0309 N0318 N0319 N0981 N0982 N0983 N0984 N0985 N0986 N0731 N0732 N0733 N0734 N0735 N0736 N0737 N0738 N0739'.split(), [], None, False),
    ('운100', [510], 'N0444 N0445 N0446 N0447 N0466 N0468 N0469 N1460 N1466 N1469 N2461 N2462 N2463 N2464 N2465 N2466 N2467 N2468 N2469 N2470'.split(), [], None, False),
    ('운97', [511], 'N0691 N0692 N0693 N0694 N0695'.split(), [], None, False),
    ('운98', [511, 512], ('N3710 N2070 N3716 N2076 N3717 N1711 N2077 N4710 N3711 N2079 N3712 N3719 N4716 N2078 N3718 N2716 N4717 N3715 '
                          'N1715 N0711 N4719 N2071 N2710 N4711 N3713 N4718 N2717 N3720 N3714 N2711 N2072 N4712 N2719 N2718 N2075 N3726 '
                          'N0715 N4715 N4720 N0719 N1721 N2712 N2074 N2073 N3727 N4713 N4714 N4726 N3721 N1725 N2715 N2713 N2714 N3729 '
                          'N3722 N4721 N4727 N3728 N3725 N4729 N4722 N3723 N4728 N3724 N4725 N4724 N4723 N1714 N1717 N0714 N0717 N1724 '
                          'N1727 U4950').split(), [], None, False),
    ('운99', [513], 'S4593 S4594 S4595 S4596 S4799'.split(), [], None, False),
    ('운86', [508], LA, [], None, False),
    ('운172', [499], 'MY762 MY763 O0972 O1292 O1332 O1333 Q2272 Q2382 Q2383 Q7611 Q7612 Q7670 Q7720 S4891 S4892 S4895 S4930 S4972 S4990'.split(), [], None, False),
    ('운101', [509], [], [], 'S0021 SA021 S0022 SA022 S0027 SA027 S0028 SA028 S0029 SA029 S0030 SA030 S0031 SA031 S0032 SA032 S0037 SA037 S0038 SA038 S0039 SA039 S0040 SA040'.split(), False),
    ('운102', [509], [], [], 'SB021 SC021 SB022 SC022 SB029 SC029 SB030 SC030 SB031 SC031 SB032 SC032 SB039 SC039 SB040 SC040'.split(), False),
    ('운103-3', [281], [], [], 'N0630 N0641 N0642 N0643 N0644 N0645 N0761 N0762 N0763 N0764 N0765'.split(), False),
    ('운103-5', [283], [], [], [], False),                             # 깁스 : 수가코드 조건 없음
    ('또238-1', [738], [], ['RZ566'], None, False),
    ('또238-2', [739], [], ['PZ612', 'RZ566'], None, False),
    ('또238-3', [740], [], ['PZ612'], None, False),
    ('또간200', [573], [], [], [], True),                               # 다빈치·유방재건 수가코드가 잘못 들어감
    ('또간204', [573], [], [], [], True),
    ('또간172', [573], [], [], [], True),
    ('또간176', [573], [], [], [], True),
    ('또간76', [453], ['HD416', 'HD020'], [], None, False),
    ('또간92', [453], ['HD416', 'HD020'], [], None, True),
]

# 별표 쪽번호 바로잡기 (감사자가 원문에서 확인한 실제 시작 쪽)
PAGES = {'f7248ee66d': 849, 'ee19195384': 933, '34700df0f3': 852, '44ce4f3cec': 1359, 'b82fb3db24': 809,
         'abababd894': 924, 'care6noe01': 1075, 'unspine13': 466, 'b83171496e': 866, 'e8506c930c': 1806,
         '6eb0162f6e': 802, 'ec8beacf51': 854, 'tong31dae01': 852, '29f7051456': 864, 'd692ad46a7': 1501,
         '7aea7acb17': 926, '1a622d7611': 937, '553fd71d47': 935, '02ec19e1b5': 896}
# 원문(text)이 다른 별표 것으로 들어가 있던 표 → 바로잡은 쪽에서 다시 읽는다
RETEXT = {'f7248ee66d': '통합간편', 'ee19195384': '케어프리'}

# 행 이름 : 코드 한 개짜리 행을 KCD 이름으로 (행 이름이 옆 행과 뒤섞이거나 번호·머리글이 붙은 표)
RELABEL = ['2acb4ac9be', '3b62cab43b', 'a31a02f391', '01c21e4e78', '300e57212c', '1c5c522faf', 'ab695a3cb9', 'ec0d78275c',
           'bb2ac0a0e5', '2bf398f340', '332a1ad035', 'f35de35bbf', 'ed46a522a7', 'aaef718384', '7aea7acb17',
           'Te100fe5c77', 'T1fa80366a1', 'Tf3d20df87d', 'Tbdb394836e', 'T6f80468d74', 'T92352c6c39', 'Tc7c4d9706e',
           'T5b272d8711', 'T5511e2d244', 'T9ecc606af9', 'Ta0b16f3eba', 'T78d6862004', 'T0ccbf20434', 'T30d103a740',
           'T439d0960d4', 'T439319a277', 'T0718411f63', 'T9c2455597b', 'T94abda0734', 'T7239901f27', 'T3f9058b6f4',
           'T58576fa801', 'Tf130125c61', 'T2d6310db70', 'T908073ba87', 'T41a447098a', 'Tcec5e2dd6a', 'Tacbc9a1b50',
           'T18cb3eb986', 'Ta5bd62e3b7', 'Tef81c73d70', 'Te8b348b753', 'T89b0e90314']
# 여러 코드 행 · 이름표에 없는 코드 : 감사자가 원문에서 옮긴 이름
LABELS = {
    '1c5c522faf': {'J40': '급성인지 만성인지 명시되지 않은 기관지염'},
    '55c2a58b3b': {'U84.3': '항결핵제 내성(U84.3) 및 결핵(A15~A19) 산정특례 등록자', 'A15': '항결핵제 내성(U84.3) 및 결핵(A15~A19) 산정특례 등록자'},
    '703531b117': {'A18.3': '장, 복막 및 장간막림프절의 결핵성 장애', 'K93.0': '장, 복막 및 장간막림프절의 결핵성 장애'},
    '7a68805f7d': {},
    'b01a206bc8': {'K64': '치핵 및 항문주위 정맥 혈전증'},
    'T439d0960d4': {'I97.2': '유방절제후림프부종증후군'},
    'T92352c6c39': {'G62.8': '기타 명시된 다발신경병증'},
    'T7239901f27': {'C77': '림프절의 이차성 및 상세불명의 악성 신생물 (림프절 전이암)', 'C78': '호흡 및 소화기관의 이차성 악성 신생물 (특정 전이암)',
                    'C79': '기타 및 상세불명 부위의 이차성 악성 신생물 (특정 전이암)', 'C80': '부위의 명시가 없는 악성 신생물 (특정 전이암)'},
    'T908073ba87': {'C77': '림프절의 이차성 및 상세불명의 악성 신생물 (림프절 전이암)', 'C78': '호흡 및 소화기관의 이차성 악성 신생물 (특정 전이암)',
                    'C79': '기타 및 상세불명 부위의 이차성 악성 신생물 (특정 전이암)', 'C80': '부위의 명시가 없는 악성 신생물 (특정 전이암)'},
    'a31a02f391': {'C80': '부위의 명시가 없는 악성 신생물'},
}
# 문장 조각이 행 이름으로 들어간 잡음 행 (코드는 다른 행에 이미 있음)
DROP_ROWS = {'b83171496e': ['에서 '], '51e7fed75a': ['에서 '], '0075b9c569': ['에서 '],
             'c676a7711b': ['급성 심근경색증 후 특정 현존합병증']}
# 다음 쪽으로 넘어가 빠진 코드를 같은 행에 붙인다 (근거 쪽)
ROW_APPEND = [('7a68805f7d', 'T31.1', ['T31.7', 'T31.8', 'T31.9'], 1290, '통합간편')]

# 본문(b) 고치기 : (특약, 종류, 인자...)
TEXT = [
    ('통102', 'move', '  2. 100병상 이상 300병상 이하인 경우에는', '에 전속하지 아니한 전문의를 둘 수 있다.\n', '통101', '  1. 100개 이상의 병상을 갖출 것\n'),
    ('통105', 'move', '내과·외과·소아청소년과·산부인과 중 3개', '에 전속하지 아니한 전문의를 둘 수 있다.\n', '통104', '  2. 100병상 이상 300병상 이하인 경우에는\n'),
    ('케43', 'move', '업무의 위탁 절차 등에 관하여 필요한 사항은 보\n건복지부령으로 정한다.\n', None, '케43', '⑤ 상급종합병원 지정·재지정의 기준·절차 및 평가\n'),
    ('운54', 'cut', '[별표1]응급증상 및 이에 준하는 증상\n', '등에 이물이 들어가 제거술이 필요한 환자\n'),
    ('통227', 'after', '제3조(준용규정)\n이 특별약관에 정하지 않은 사항은 제1절 일반조항을 따\n릅니다.'),
    ('통226', 'after', '제2조(준용규정)\n이 특별약관에 정하지 않은 사항은 제1절 일반조항을 따\n릅니다.'),
    ('케395', 'after', '제2조(준용규정)\n이 특별약관에 정하지 않은 사항은 제1절 일반조항을 따\n릅니다.'),
    ('운168', 'after', '제2조(준용규정)\n이 특별약관에 정하지 않은 사항은 제1절 일반조항을 따\n릅니다.'),
    ('운153', 'before', '3-1. 건물소유자의 종업원배상책임 부보장'),
    ('운159', 'before_last', '기타 특별약관'),
    ('또32', 'before_last', '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2607'),
    ('또218', 'before_last', 'Ⅲ. 상해 및 질병 관련 특별약관'),
    ('또간32', 'before_last', '무배당 메리츠 또 걸려도 또 받는 간편한'),
    ('또간136', 'append_pdf', '국가암관리', '사업본부 및 그 밖에 필요한 기구를 둔다.', 263),
    ('케245', 'insert_pdf', '마. 출혈 : 계속되는 각혈, 지혈이 안되는 출혈,\n', '급성 위장관 출혈', '제거술이 필요한 환자', 779),
]


def main():
    pdfdir = sys.argv[1]
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', html, re.S)
    D = inflate(json.loads(m.group(2)))
    T, R = D['tables'], D['riders']
    RM = {r['id']: r for r in R}
    CN = D.get('codenames', {})
    PDF = {}

    def pages(p, pg, back=8, fwd=6):
        if p not in PDF: PDF[p] = json.load(open(os.path.join(pdfdir, KEY[p] + '.json')))
        P = PDF[p]; i = pg - 1 + OFF[p]
        return '\n'.join(P[max(0, i - back):i + fwd])

    def hc_ranges(flat):
        """약관의 수가코드 범위 표기(LA222~LA228)를 낱개로 푼다"""
        out = set()
        for a, b in re.findall(r'([A-Z]{2}\d{3})[~∼]([A-Z]{2}\d{3})', flat):
            if a[:2] == b[:2] and int(b[2:]) >= int(a[2:]):
                out.update('%s%03d' % (a[:2], i) for i in range(int(a[2:]), int(b[2:]) + 1))
        return out

    log, hold = [], []

    # 1) 수가코드
    for rid, pgs, add, rm, setv, subs_too in HC:
        r = RM[rid]
        need = add + (setv or [])
        flat = re.sub(r'\s+', '', ''.join(pages(r['p'], pg) for pg in pgs))
        bad = [c for c in need if c not in flat and c not in hc_ranges(flat)]
        if bad: hold.append((rid, '수가코드 근거 없음 %s' % bad)); continue
        targets = [r] + ([x for x in R if x.get('parent') == rid] if subs_too else [])
        for x in targets:
            hc = list(setv) if setv is not None else list(x.get('hc') or [])
            hc = [c for c in hc if c not in rm]
            for c in add:
                if c not in hc: hc.append(c)
            x['hc'] = hc
        log.append((rid, '수가코드 %s' % ('%d개로 정리' % len(targets[0]['hc']))))

    # 2) 별표 쪽번호 · 원문
    for tid, pg in PAGES.items():
        if tid in T:
            old = T[tid].get('page'); T[tid]['page'] = pg; log.append((tid, '쪽 %s → %s' % (old, pg)))
    for tid, p in RETEXT.items():
        t = T[tid]; txt = pages(p, t['page'], back=0, fwd=3)
        key = re.sub(r'\s+', '', t['name'])[:8]
        mm = re.search(r'\s*'.join(map(re.escape, key)), txt)
        if not mm: hold.append((tid, '원문 제목 못 찾음')); continue
        body = txt[mm.start():]
        e = re.search(r'【\s*별\s*표\s*\d', body[10:])
        t['text'] = body[:e.start() + 10] if e else body
        log.append((tid, '원문 다시 읽음 %d자' % len(t['text'])))

    # 3) 행 이름 · 잡음 행 · 이어 붙이기
    for tid in RELABEL:
        if tid not in T: continue
        n = 0
        for row in T[tid].get('rows', []):
            cs = row['codes']
            if len(cs) == 1 and CN.get(cs[0]) and row['label'] != CN[cs[0]]:
                row['label'] = CN[cs[0]]; n += 1
        log.append((tid, '행 이름 %d개 교정' % n))
    for tid, mp in LABELS.items():
        for row in T.get(tid, {}).get('rows', []):
            if row['codes'] and row['codes'][0] in mp: row['label'] = mp[row['codes'][0]]
    for tid, prefs in DROP_ROWS.items():
        rows = T[tid]['rows']; before = len(rows)
        T[tid]['rows'] = [row for row in rows if not any(row['label'].startswith(pf) for pf in prefs)]
        log.append((tid, '잡음 행 %d개 삭제' % (before - len(T[tid]['rows']))))
    for tid, first, codes, pg, p in ROW_APPEND:
        flat = re.sub(r'\s+', '', pages(p, pg))
        if any(c not in flat for c in codes): hold.append((tid, '이어 붙일 코드 근거 없음')); continue
        for row in T[tid]['rows']:
            if row['codes'] and row['codes'][0] == first:
                row['codes'] += [c for c in codes if c not in row['codes']]
        log.append((tid, '%s 행에 %s 추가' % (first, ','.join(codes))))

    # 4) 본문
    def with_subs(rid, old):
        return [RM[rid]] + [x for x in R if x.get('parent') == rid and x.get('b') == old]

    for op in TEXT:
        rid, kind = op[0], op[1]; r = RM[rid]; b = r['b']; new = None
        if kind == 'move':
            a, z, dst, anchor = op[2], op[3], op[4], op[5]
            i = b.find(a); j = b.find(z, i) + len(z) if z else i + len(a)
            if i < 0 or (z and j < len(z)): hold.append((rid, '옮길 글 못 찾음')); continue
            seg = b[i:j]; new = b[:i] + b[j:]
            if dst == rid:
                k = new.find(anchor)
                if k < 0: hold.append((rid, '붙일 자리 못 찾음')); continue
                new = new[:k + len(anchor)] + seg + new[k + len(anchor):]
            else:
                d = RM[dst]; k = d['b'].find(anchor)
                if k < 0: hold.append((dst, '붙일 자리 못 찾음')); continue
                for x in with_subs(dst, d['b']):
                    x['b'] = d['b'][:k + len(anchor)] + seg + d['b'][k + len(anchor):]
        elif kind == 'cut':
            i = b.find(op[2]); j = b.find(op[3], i)
            if i < 0 or j < 0: hold.append((rid, '자를 글 못 찾음')); continue
            new = b[:i] + b[j + len(op[3]):]
        elif kind == 'after':
            i = b.find(op[2])
            if i < 0: hold.append((rid, '끝 문장 못 찾음')); continue
            new = b[:i + len(op[2])]
        elif kind == 'before':
            i = b.find(op[2])
            if i < 0: hold.append((rid, '자를 글 못 찾음')); continue
            new = b[:i].rstrip()
        elif kind == 'before_last':
            i = b.rfind(op[2])
            if i < 0: hold.append((rid, '자를 글 못 찾음')); continue
            new = b[:i].rstrip()
        elif kind == 'append_pdf':
            tail, add, pg = op[2], op[3], op[4]
            if not b.rstrip().endswith(tail): hold.append((rid, '끝이 예상과 다름')); continue
            if re.sub(r'\s', '', tail + add) not in re.sub(r'\s+', '', pages(r['p'], pg)): hold.append((rid, '원문에 없음')); continue
            new = b.rstrip() + add
        elif kind == 'insert_pdf':
            anchor, s0, s1, pg = op[2], op[3], op[4], op[5]
            src = pages(r['p'], pg, back=0, fwd=1)
            i0 = src.find(s0); i1 = src.find(s1, i0)
            k = b.find(anchor)
            if i0 < 0 or i1 < 0 or k < 0: hold.append((rid, '넣을 글·자리 못 찾음')); continue
            new = b[:k + len(anchor)] + src[i0:i1 + len(s1)] + '\n' + b[k + len(anchor):].lstrip(' ')
        if new is not None:
            for x in with_subs(rid, b): x['b'] = new
            log.append((rid, '본문 %s (%d → %d자)' % (kind, len(b), len(new))))

    # 5) 빠진 특약 : 또또암간편 2-35 항암중입자방사선치료비(맞춤간편가입) — 약관 265쪽, 비갱신형
    if not any(x['p'] == '또또암간편' and x['n'] == '항암중입자방사선치료비' for x in R):
        P = PDF.setdefault('또또암간편', json.load(open(os.path.join(pdfdir, 'ttg.json'))))
        txt = '\n'.join(P[264:267])
        i = txt.find('2-35.'); j = txt.find('2-36.', i)
        tmpl = RM['또간208']   # 같은 약관 문구의 갱신형 — 질병코드·별표는 약관 제1조가 같다(암(유사암제외)·기타피부암·갑상선암)
        body = txt[i:j].rstrip()
        if i < 0 or j < 0 or '「암(유사암제외)」' not in body or '「기타피부암」' not in body:
            hold.append(('또간(2-35)', '약관 본문 못 찾음'))
        else:
            new = {'id': '또간223', 'p': '또또암간편', 'n': '항암중입자방사선치료비', 'c': tmpl['c'], 'pg': 265, 'b': body,
                   'k': list(tmpl['k']), 'l': list(tmpl.get('l') or []), 'x': list(tmpl.get('x') or []), 't': list(tmpl['t']),
                   's': [], 'st': tmpl.get('st', '')}
            at = next(n for n, x in enumerate(R) if x['id'] == '또간143')
            R.insert(at, new)
            log.append(('또간223', '빠진 특약 추가 (약관 265쪽, %d자)' % len(body)))
            meta = D['meta']
            if isinstance(meta.get('prodcount'), dict): meta['prodcount']['또또암간편'] = meta['prodcount'].get('또또암간편', 0) + 1

    for a in log: print('반영', *a)
    for h in hold: print('보류', *h)
    print('반영 %d · 보류 %d' % (len(log), len(hold)))
    if '--write' in sys.argv:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 저장')


if __name__ == '__main__':
    main()
