# -*- coding: utf-8 -*-
"""담보코드 입력 검증 — 「설계서 PDF 로 넣은 결과」 = 「담보 목록(JSON)으로 넣은 결과」 인가

  python3 verify_code_input.py <작업폴더> <매핑 엑셀> <설계서 폴더> <결과 폴더> [--pdf]

설계서마다
  ① PDF 로 읽어 계산(기준)
  ② 그 설계의 담보를 정보계 표의 줄(단위상품코드 · 담보코드 · **정보계 원문 이름**)로 바꾼 입력 JSON 을 만든다 — 이름 꼴 두 가지로
       row  : 1-7종 수술비를 「수술비[질병3종]」(부모 이름 없는 꼴)로
       full : 1-7종 수술비를 「수술비(1-7종, 연간3회한)[질병3종]」(부모 이름 있는 꼴)로  ← 정보계에 두 꼴이 다 있다
  ③ 입력 JSON 으로 계산 → 칸 값 132개 + 혈전제거 단독 6 + 수술 카드 상급종합 12 + 수술 카드 다섯 줄 + 간병인 표 + 표지 항목을 ①과 대조
  ④ (--pdf) 입력 JSON 으로 PDF 를 만들고 인쇄 검증(verify_v2) + ①로 만든 PDF 와 쪽마다 글자 대조
담보 식별표(code_map.json)를 쓴 경우 · 안 쓴 경우 둘 다 본다(GA_CODE_MAP). 결과 폴더의 입력 JSON 은 정보계 코드 · 개인정보가 있어 저장소에 넣지 않는다.
"""
import sys, os, re, json, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); PS = os.path.join(ROOT, 'proposal_smart')
sys.path.insert(0, HERE); sys.path.insert(0, PS)
from norm import key as nkey
import export_code_map as X

WORK, MAPX, DDIR, OUT = sys.argv[1:5]; MAKE_PDF = '--pdf' in sys.argv
os.makedirs(OUT, exist_ok=True)
rows, NR, UP = X.load(WORK, MAPX)
K2 = collections.defaultdict(list)
for u, c, n in rows: K2[nkey(n)].append((u, c, n))
os.chdir(PS)
import ga_v2 as G, code_input as CI, verify_v2 as V
GP, GS = G.GP, G.GS

def payload_of(style):
    """지금 읽어 둔 설계(GP)를 정보계 줄로 바꾼 입력 JSON"""
    line = GP.LINE; h = GP.HEAD; rs = []; miss = []
    for r in GP.RID:
        nm = re.sub(r'^[┗\s]+', '', r['name']); cand = K2.get(nkey(nm)) or []
        mine = [x for x in cand if UP.get(x[0]) == line]
        # 같은 알맹이 줄이 여럿이면 설계서 글자와 가장 가까운 줄 — 갱신형 여부 · (N년갱신) · 글자(고지 구분자 빼고)가 같은 것 먼저
        _g = lambda t: re.sub(r'\([^()]*가입\)|\[기본계약\]|\s', '', t)
        _rk = lambda x: (_g(x[2]) != _g(nm), ('갱신형' in x[2]) != ('갱신형' in nm), (re.findall(r'\(\d+년갱신\)', x[2]) != re.findall(r'\(\d+년갱신\)', nm)), x)
        if mine: u, c, n = sorted(mine, key=_rk)[0]
        elif cand:      # 이 상품으로 추정된 단위상품코드에는 같은 이름 줄이 없음 — 코드는 다른 단위상품의 것을 빌리되 이름은 설계서 글자로(다른 상품의 고지 구분자 · 갱신 주기가 섞이지 않게)
            u, c, _ = sorted(cand, key=_rk)[0]; n = r['name'].replace('┗', '').strip(); miss.append(r['name'])
        else: u, c, n = '', '', r['name'].replace('┗', '').strip(); miss.append(r['name'])
        if r['name'].lstrip().startswith('┗') and style == 'full':      # 정보계의 다른 꼴 「수술비(1-7종, 연간3회한)[질병3종](…가입)」 — 통합간편 줄에 실제로 있는 꼴을 모든 설계에 적용해 본다
            gk = re.search(r'(질병|상해)\d종', n.replace(' ', '')).group(0); tail = ''.join(re.findall(r'\([^()]*가입\)', n))
            n = ('갱신형 ' if '갱신형' in n else '') + '수술비(1-7종, 연간3회한)[%s]%s' % (gk, tail)
        ud = 0; won = int(round(float(r['man']) * 10000))
        if '간병인지원' in nm and '사용추가보장' not in nm:
            m = re.search(r'또는\s*([\d.,]+)\s*(천원|만원|원)', re.sub(r'\s+', '', r.get('amount_text') or ''))
            if m: v = float(m.group(1).replace(',', '')); ud = int(v * {'천원': 1000, '만원': 10000, '원': 1}[m.group(2)])
            won = 0
        rs.append(dict(no=int(r['no']), unit_code=u, code=c, name=n, amount=won, **({'unused_daily': ud} if ud else {})))
    prem = int(re.sub(r'[^\d]', '', GP.PREMIUM or '') or 0)
    return dict(schema=1, design_no=h.get('no') or '', product=GP.PRODUCT, premium=prem,
                insured=dict(name=h.get('name') or '', sex={'여자': 'F', '남자': 'M'}.get(h.get('sex') or '', ''), age=(h.get('age') or '').replace('세', '')),
                agent=dict(org=h.get('org') or '', code=h.get('code') or '', name=h.get('agent_name') or '', mobile=h.get('mobile') or '', tel=h.get('tel') or ''), riders=rs), miss

def snap():
    d = {k: (repr(v[0]), sorted(round(GS.counts(l, 'first'), 4) for l in v[1])) for k, v in GP.VAL.items()}
    d.update({k: (repr(v[0]), sorted(round(GS.counts(l, 'first'), 4) for l in v[1])) for k, v in G.EXTRA.items() if isinstance(v, tuple) and k != 'care'})
    for n in GS.DZ_ORDER:
        rs, ta, tu = G.card_rows(n); d['카드·' + n] = (repr((ta, tu)), [(r[0], r[1], r[2], r[3], tuple(t[1] for t in r[4])) for r in rs])
    cf = G.CF(); d['간병인'] = (repr({k: v for k, v in cf.items() if k not in ('sup_names', 'use_names', 'sup180', 'sup181', 'supnh')}), [len(cf['sup180']), len(cf['sup181']), len(cf['supnh'])])
    d['표지'] = (repr({k: GP.HEAD.get(k) for k in ('name', 'sex', 'age', 'no', 'org', 'agent_name', 'code', 'mobile', 'tel')}), [GP.PRODUCT, GP.PREMIUM, GP.who_line(), GP.LINE])
    d['미가입 줄'] = (repr(G.EXTRA.get('unj')), [])
    return d

res = []; bad = 0
for pdf in sorted(glob.glob(os.path.join(DDIR, '*.pdf'))):
    nm = os.path.splitext(os.path.basename(pdf))[0]
    G.load(pdf); base = snap(); nrid = len(GP.RID); line = GP.LINE; r = dict(design=nm, line=line, riders=nrid, styles={})
    pays = {}
    for style in ('row', 'full'):
        G.load(pdf); pays[style], miss = payload_of(style)
        json.dump(pays[style], open(os.path.join(OUT, '%s_%s.json' % (nm, style)), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for style in ('row', 'full'):
        p = CI.parse(json.dumps(pays[style], ensure_ascii=False)); G.load(p); cur = snap()
        dif = [(k, base[k], cur[k]) for k in base if base[k] != cur.get(k)]
        how = collections.Counter(x.get('how') or '못 찾음' for x in GP.RID)
        r['styles'][style] = dict(diff=len(dif), riders=len(GP.RID), borrowed=len(miss), how=dict(how), names_changed=sum(1 for a, b in zip(pays[style]['riders'], pays['row']['riders']) if a['name'] != b['name']),
                                  detail=[(k, str(a)[:160], str(b)[:160]) for k, a, b in dif[:8]])
        bad += bool(dif)
    line_out = '%s %-16s %-24s 담보 %3d · 대조 %d곳 · 다른 곳 row %d / full %d · full 꼴로 바꾼 이름 %d · 찾은 길 %s' % (
        '통과' if not any(v['diff'] for v in r['styles'].values()) else '실패', nm, line, nrid, len(base), r['styles']['row']['diff'], r['styles']['full']['diff'], r['styles']['full']['names_changed'], r['styles']['full']['how'])
    if MAKE_PDF:
        p = CI.parse(json.dumps(pays['full'], ensure_ascii=False)); o = os.path.join(OUT, nm + '_code_GA2.pdf')
        C, info = V.verify(p, o); r['print'] = dict(checks=C.n, bad=C.bad[:10], pages=info['pages']); bad += bool(C.bad)
        line_out += ' · 인쇄 검증 %d곳 · 다른 곳 %d' % (C.n, len(C.bad))
        ref = os.path.join(OUT, '..', 'pdfpath', nm + '_GA2.pdf')
        if os.path.exists(ref):
            import fitz
            a, b = fitz.open(o), fitz.open(ref); ns = lambda t: re.sub(r'\s+', '', t)
            dp = [i + 1 for i in range(min(len(a), len(b))) if ns(a[i].get_text()) != ns(b[i].get_text())]
            r['pdf_pages_diff'] = dp + ([-1] if len(a) != len(b) else []); line_out += ' · PDF 길과 글자 다른 쪽 %s' % (dp or '없음')
    print(line_out, flush=True)
    for st, v in r['styles'].items():
        for d in v['detail'][:4]: print('      [%s] %s : %s  ≠  %s' % (st, d[0], d[1][:90], d[2][:90]))
    for b_ in (r.get('print') or {}).get('bad', [])[:5]: print('      [인쇄] ' + b_[:200])
    res.append(r)
json.dump(res, open(os.path.join(OUT, 'verify_code_input.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n결과 : %s — 설계 %d건' % ('전부 통과' if not bad else '실패 %d' % bad, len(res)))
G.close_browser()
sys.exit(1 if bad else 0)
