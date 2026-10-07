# -*- coding: utf-8 -*-
"""
같은 이름 특약끼리 질병코드·수가코드가 어긋난 것 바로잡기 (2026.10)

상품만 다른 같은 특약은 약관 별표가 같다(쪽 번호·별표 번호만 다름). 그런데 데이터에서는 26개 묶음이
서로 다른 코드를 갖고 있었다 — 한 상품만 감수 때 고쳐지고 나머지는 남았거나, 같은 코드를 다르게 적은 것.
아래는 상품마다 그 상품 약관 원문(해당 특약 쪽·연결 별표 쪽)에서 코드가 실제로 있는지 확인한 뒤 맞춘 것이다.
(근거 확인 : 각 상품 약관 PDF 텍스트에서 코드 또는 코드 범위 표기를 찾음)

실행 : python3 scripts/fix_same_terms.py [--write]
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import inflate, deflate, PAT, ROOT

TOOL = os.path.join(ROOT, 'tool.html')

BURN = 'N0011 N0012 N0053 N0054 N0057 N0058 NA055 NA056 NA057 NA058'.split()   # 화상처치(특정시술 분류표)

# (특약, 무엇을, 값, 근거)
OPS = [
    # ── 수가코드 : 같은 별표인데 한 상품만 채워져 있던 것 ──
    ('통32', 'hc_add', BURN, '상해 통합치료비(실속형) — 통합간편 약관 특정시술치료(급여) 분류표(p.849)에 화상처치 10개 있음(케12 와 같은 별표)'),
    ('통110', 'hc_add', ['MM101'], '상급종합병원·권역심뇌혈관 특정순환계 통합치료비 — 통합간편 약관 해당 쪽에 MM101 있음(케200 과 같음)'),
    ('또82', 'hc_add', ['HD020', 'HD416'], '계속받는 항암방사선약물치료비 — 또또암 약관 급여 항암방사선치료 분류표에 있음(통49·케131·또간76 과 같음)'),
    ('또128', 'hc_add', ['HD020', 'HD416'], '통합항암방사선약물치료비(최대8회한) — 또또암 약관 같은 분류표(또간92 와 같음)'),
] + [('또128-%d' % i, 'hc_add', ['HD020', 'HD416'], '세부보장 — 부모 또128 과 같은 분류표') for i in range(1, 9)] + [
    ('통131', 'hc_add', 'LALB', '암 통합치료비(기본형) — 통합간편 약관 본문이 【별표56 신경차단·파괴치료(급여)】를 지정, p.864 에 69개 코드(케204 와 같음)'),
    ('통133', 'hc_add', 'LALB', '암 통합치료비(기본형)(암중점치료기관) — 같은 별표56(p.864)'),
    ('또182', 'hc_add', 'LALB', '암 통합치료비(기본형) — 또또암 약관 【별표12 신경차단·파괴치료(급여)】 p.545'),
    ('또184', 'hc_add', 'LALB', '암 통합치료비(기본형)(암중점치료기관) — 같은 별표12(p.545)'),
    ('또91', 'hc_add', 'LALB', '암특정통증완화치료비 — 또또암 약관 본문이 【별표12 신경차단·파괴치료(급여)】 지정, p.545(케137 과 같음)'),
    # 폴립및양성종양수술(급여,1-6종) 분류표 : 세 상품 약관 별표5 글자가 같고 코드 176개
    ('통217', 'hc_add', ['Q2204'], '폴립및양성종양수술비 — 통합간편 별표5(p.1389) 구강내종양적출술(양성)-구강저병소제거 Q2204 빠져 있었음'),
    ('케316', 'hc_add', ['Q2204'], '같은 별표5(p.1405)'),
    ('또224', 'hc_set', 'POLYP', '또또암 별표5(p.698)는 다른 두 상품과 같은 176개 — 다른 별표(p.759·762)의 CZ977·N7140 등 59개가 잘못 들어가 있었음'),
    # ── 제외코드 ──
    ('또194', 'x_set', ['C44', 'C73'], '26종항암방사선및약물치료비(전이포함)(유사암제외) — 약관 문구가 통116·케216 과 같음(유사암제외)'),
    ('또간160', 'x_set', ['C44', 'C73'], '같음'),
    ('또199', 'x_set', ['C44', 'C73'], '원격전이포함 4기 통합암진단비(유사암제외) — 통238·케296 과 같은 약관 문구'),
    ('또간165', 'x_set', ['C44', 'C73'], '같음'),
    ('케317', 'x_set', ['Q00~Q99'], '갱신형 뇌정위적방사선수술비 — 케어프리 약관 제3조 ② 선천기형·변형 및 염색체이상(Q00-Q99) 보상하지 않음(통218·또225 와 같은 문구)'),
    ('또246', 'x_add', ['N96~N98'], '갱신형 질병특정비급여,신의료기술치료비(1-3종) — 또또암 약관 보상하지 않는 손해 ② (N96∼N98) 문구 있음(케333 과 같음)'),
    ('또250', 'x_add', ['N96~N98'], '(1-4종) 같음'),
    ('또210', 'x_remove', ['D32', 'D33'], '암 통합생활지원비 — 약관이 「뇌·수막의 양성신생물(D32·D33)」을 지급 대상으로 정의, 산정특례대상 분류표에도 있음'),
    # ── 보장 질병코드 ──
    ('케235', 'k_add', ['D32', 'D33'], '암 통합생활지원비 — 케어프리 약관 뇌·수막의 양성신생물(D32·D33) 정의 · 산정특례대상 분류표(통141 과 같음)'),
    ('또간147', 'k_add', ['D32', 'D33'], '같음(또또암간편 약관)'),
    ('케29', 'k_from', '운54', '신골절치료비(치아파절포함) — 케어프리 별표47 지급률표 글자가 운전자 별표11·통합간편 별표37 과 같음(점선만 다름). 코드가 비어 있었음'),
    ('치36', 'k_from', '운54', '신골절치료비(치아파절포함) — 치아 별표16 도 같은 지급률표'),
    ('또119-1', 'k_swap', ('C76~C80', 'C76'), '통합전이암진단비[림프절전이암] — 림프절전이암은 C77 만(또간84-1 과 같게). 원발암 목록의 C76~C80 범위가 C78~C80 까지 끌고 들어와 있었음'),
    ('또119-3', 'k_swap', ('C76~C80', 'C76'), '통합전이암진단비[특정전이암] — 특정전이암은 C78~C80 만(또간84-3 과 같게). C76~C80 범위가 C77 까지 끌고 들어와 있었음'),
]


def main():
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    RM = {r['id']: r for r in D['riders']}
    CN = D.get('codenames', {})
    lalb = sorted(set(RM['케204']['hc']) - set(RM['통131']['hc'])) if 'LA210' not in RM['통131']['hc'] else [c for c in RM['케204']['hc'] if c[:2] in ('LA', 'LB')]
    polyp = sorted(set(RM['통217']['hc']) | {'Q2204'})
    done = []
    for rid, op, val, why in OPS:
        r = RM[rid]
        if val == 'LALB': val = lalb
        if val == 'POLYP': val = polyp
        if op == 'hc_add':
            r['hc'] = list(r.get('hc') or []) + [c for c in val if c not in (r.get('hc') or [])]
        elif op == 'hc_set':
            r['hc'] = list(val)
        elif op == 'x_set':
            r['x'] = list(val)
        elif op == 'x_add':
            r['x'] = list(r.get('x') or []) + [c for c in val if c not in (r.get('x') or [])]
        elif op == 'x_remove':
            r['x'] = [c for c in (r.get('x') or []) if c not in val]
        elif op == 'k_add':
            aligned = len(r.get('l') or []) == len(r['k'])
            for c in val:
                if c not in r['k']:
                    r['k'].append(c)
                    if aligned: r['l'].append(CN.get(c, ''))
        elif op == 'k_from':
            src = RM[val]; r['k'] = list(src['k']); r['l'] = list(src.get('l') or [])
        elif op == 'k_swap':
            a, b = val
            if a in r['k']:
                i = r['k'].index(a); r['k'][i] = b
                if len(r.get('l') or []) > i: r['l'][i] = CN.get(b, r['l'][i])
        done.append((rid, op, why))
    for d in done: print('반영', *d)
    print('반영 %d건' % len(done))
    if '--write' in sys.argv:
        body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
        io.open(TOOL, 'w', encoding='utf-8').write(html[:m.start(2)] + body + html[m.end(2):])
        print('tool.html 저장')


if __name__ == '__main__':
    main()
