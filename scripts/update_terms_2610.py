# -*- coding: utf-8 -*-
"""
2610 약관(2026-10-31 개정 · 판매개시 2026.10.31) → 영업지원도구(tool.html · tool_body.js) 반영

  python3 scripts/update_terms_2610.py            (결과만 출력)
  python3 scripts/update_terms_2610.py --write    (tool.html · tool_body.js 에 반영 → 이어서 아래 순서)
      python3 scripts/fix_body_tables.py --write --only <출력된 특약 id 목록>     # 다시 뽑은 본문의 표 되살리기
      python3 scripts/fix_table_order.py --write
      python3 scripts/same_riders.py --write
      python3 scripts/sync_all.py --designs <설계서폴더>

하는 일(상품마다 : 통합간편 · 케어프리 · 운전자 · 또또암)
  1) 새 약관을 import_terms.import_pdf 로 자르고(특약 제목 · 본문 · 별표 코드), 옛 약관도 같은 방법으로 잘라 둔다.
  2) 이미 있는 특약은 이름으로 짝을 맞춰 쪽 번호(pg)를 새 약관 쪽으로 옮긴다. 본문 글자가 옛 약관과 다르면(개정) 새 본문으로 바꾼다
     (표는 fix_body_tables --only 로 되살린다). 글자가 같으면 감수본 본문(표 복원본)을 그대로 둔다. 질병코드(k·x·hc)는 감수본을 건드리지 않는다.
  3) 새 약관에만 있는 특약(신담보)은 특약 · 세부보장 · 별표를 더한다. 코드는 별표에서만 옮긴다(import_terms 규칙).
  4) 새 약관에 없는 특약은 지우지 않고 ex 에 사유를 적어 둔다(※ 케어프리 장기요양급여금 3종은 소유자 지시(2026-11-02)로 지움 — 판매중지 담보는 지워도 된다 · 통합간편 간병인(Ⅶ) 18종은 이전 판 테스트 설계서가 쓰므로 남김) — 2607 판으로 가입한
     계약의 설계서는 그대로 읽혀야 하고(틀린 금액이 아니라 빈칸 원칙), 상품 히스토리에도 남긴다.
  5) 상품만 쓰는 별표의 쪽 번호도 새 약관 쪽으로. 버전 ver2612 → ver2613 · 상품 히스토리(HISTORY · 보상시뮬레이터 사본) 에 신설 · 삭제 기록.
※ 신설 특약의 질병코드는 import_pdf 파싱값이라 **반드시 같은 이름 · 같은 별표의 감수본과 대조해 바꾼다**(2026-11-02 : 암통합입통원일당이 악성신생물 분류표를 30개만 읽어 틀렸던 것 → 암직접치료입원일당(Ⅱ) 코드로). 표가 「<해당보장 보험가입금액 …>」 꼴이면 fix_body_tables 가 못 잡으므로 칸 글자를 표로 되살린다.
비갱신 · 갱신형 특약이 한 본문을 같이 쓰는 「X / 갱신형 X」 제목은 import_pdf 가 뒤 제목만 읽으므로, 앞 이름(X)은 「갱신형X」 레코드에서 쪽 · 본문을 받는다.
"""
import base64, collections, io, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import import_terms as IT
from tooldata import inflate, deflate, PAT

TOOL = os.path.join(ROOT, 'tool.html')
PRODS = [  # 상품, id 접두어, 새 약관, 옛 약관
    ('통합간편', '통', '무배당 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형)약관.pdf', '무배당 메리츠 통합간편건강보험(세만기형)2607(통합간편심사형)약관.pdf'),
    ('케어프리', '케', '무배당 메리츠 케어프리보험 M-Basket2610약관.pdf', '무배당 메리츠 케어프리보험 M-Basket2607약관.pdf'),
    ('운전자', '운', '무배당 메리츠 운전자 상해 종합보험2610약관.pdf', '무배당 메리츠 운전자 상해 종합보험2608약관.pdf'),
    ('또또암', '또', '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(일반심사형)약관.pdf', '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2607약관 (1).pdf'),
    # 또또암간편 : 「또 걸려도 또 받는 간편한 암보험(세만기형)」 2607 → 2610 에서 상품명이 「또 걸려도 또 받는 암보험(세만기형)(맞춤간편심사형)」 으로 바뀜(보장 구성 그대로 · 소유자 2026-11-02)
    ('또또암간편', '또간', '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(맞춤간편심사형)약관.pdf', '무배당 메리츠 또 걸려도 또 받는 간편한 암보험(세만기형)2607약관.pdf'),
]
RENEW = set()                  # 갱신형 이름으로 바꿀 상품 — 없음. 또또암간편의 2610 약관은 연만기형(맞춤간편심사형)이라 이름에 갱신형이 붙지만, 세만기형과 특약이 같으므로(소유자 2026-11-02) 이름은 세만기형(비갱신) 그대로 두고 쪽·본문만 맞춘다
DELETE_MISSING = True          # 새 약관에 없는 특약은 지운다(소유자 2026-11-02 · 전에는 ex 표시)
GOJI = re.compile(r'\([^()]{1,24}가입\)')
EX_NOTE = '2610 약관(2026.10.31)에서 빠짐(판매중지) — 이전 판 계약 조회용으로 남겨 둠'


def key(n):
    n = re.sub(r'[\s ]', '', n or '')
    n = GOJI.sub('', n).replace('(통합간편가입)', '')
    n = re.sub(r'보장특별약관\(.*\)$', '', n)                  # 케어프리 2610 「안전사고피해치료비보장특별약관(폭력치료비,…)」 = 안전사고피해치료비
    n = re.sub(r'\[(.*)\]$', lambda m: '[' + re.sub(r'[\s,]', '', m.group(1)) + ']', n)
    return n.replace('․', '·').replace('ㆍ', '·')


def nz(s): return re.sub(r'\s+', '', s or '')


CACHE = os.environ.get('UPD_CACHE')          # 자르기 결과를 접어 두는 폴더(점검을 여러 번 돌릴 때 · 선택)
def parse(product, prefix, pdf):
    import pickle, hashlib
    cp = CACHE and os.path.join(CACHE, hashlib.md5((product + pdf).encode()).hexdigest() + '.pkl')
    if cp and os.path.exists(cp): return pickle.load(open(cp, 'rb'))
    riders, tabs, log = IT.import_pdf(os.path.join(ROOT, pdf), product, prefix)
    pages = IT.read_pdf(os.path.join(ROOT, pdf))
    alltabs = IT.parse_appendix(IT.build_lines(pages))
    out = (riders, tabs, log, {nz(v['name']): v['page'] for v in alltabs.values()})
    if cp: pickle.dump(out, open(cp, 'wb'))
    return out


def main(write):
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    by_t = collections.defaultdict(set)
    for r in D['riders']:
        for t in r['t']: by_t[t].add(r['p'])
    refresh, added, retired, moved = [], [], [], 0
    summary = {}
    only_p = sys.argv[sys.argv.index('--product') + 1] if '--product' in sys.argv else None
    for P, pre, new_pdf, old_pdf in PRODS:
        if only_p and P != only_p: continue
        print('\n■', P, '←', new_pdf)
        new, new_tabs, log, new_tab_pages = parse(P, pre, new_pdf)
        old, _, _, _ = parse(P, pre, old_pdf)
        new_par = {key(r['n']): r for r in new if not r.get('parent')}
        old_par = {key(r['n']): r for r in old if not r.get('parent')}
        mine = [r for r in D['riders'] if r['p'] == P]
        parents = [r for r in mine if not r.get('parent')]
        kids = collections.defaultdict(list)
        for r in mine:
            if r.get('parent'): kids[r['parent']].append(r)
        matched, n_ref, n_ret = set(), 0, 0
        unseen = []; gone_ids = set(); renamed = []
        for r in parents:
            k = key(r['n'])
            n_r = new_par.get(k) or new_par.get('갱신형' + k)        # 「X / 갱신형 X」 한 본문 — 앞 이름은 갱신형 레코드에서
            if not n_r:
                if not (old_par.get(k) or old_par.get('갱신형' + k)):       # 옛 약관에서도 못 읽는 제목(재물손해 특약 등 절단 규칙 밖) → 그대로 둔다
                    unseen.append((P, r['id'], r['n'])); continue
                if DELETE_MISSING:
                    gone_ids.add(r['id']); gone_ids.update(c['id'] for c in kids[r['id']])
                elif not r.get('ex'):
                    r['ex'] = EX_NOTE
                    for c in kids[r['id']]: c['ex'] = EX_NOTE
                retired.append((P, r['id'], r['n'])); n_ret += 1
                continue
            matched.add(key(n_r['n']))
            if P in RENEW and key(n_r['n']).startswith('갱신형') and not nz(r['n']).startswith('갱신형'):
                old_n = r['n']; r['n'] = '갱신형 ' + old_n
                for c in kids[r['id']]: c['n'] = '갱신형 ' + c['n']
                renamed.append((r['id'], old_n, r['n']))
            o_r = old_par.get(k) or old_par.get('갱신형' + k)
            if int(r['pg']) != n_r['pg']:
                r['pg'] = n_r['pg']; moved += 1
                for c in kids[r['id']]: c['pg'] = n_r['pg']
            # 본문 : 옛 약관과 새 약관을 같은 방법으로 자른 글자가 다르면 개정 → 새 본문(표는 fix_body_tables 가 되살린다)
            if o_r is None or nz(o_r['b']) != nz(n_r['b']):
                r['b'] = n_r['b']
                for c in kids[r['id']]: c['b'] = n_r['b']
                refresh.append(r['id']); refresh.extend(c['id'] for c in kids[r['id']]); n_ref += 1
            r.pop('ex', None)
        # 신담보
        nums = [int(re.sub(r'\D', '', r['id'].split('-')[0]) or 0) for r in mine]
        nxt = max(nums) + 1
        last = max(i for i, r in enumerate(D['riders']) if r['p'] == P)
        new_rows = []; skipped = []
        for k, n_r in new_par.items():
            if k in matched or k in {key(x['n']) for x in parents}: continue
            if P in RENEW and re.sub(r'^갱신형', '', k) in {re.sub(r'^갱신형', '', key(x['n'])) for x in parents}: continue
            if k in old_par or re.sub(r'^갱신형', '', k) in old_par:        # 옛 약관에도 있던 제목인데 감수본에 없음 → 절단 규칙이 만든 조각(일반조항 · 절 제목) — 더하지 않는다
                skipped.append((P, n_r['n'])); continue
            rid = '%s%d' % (pre, nxt); nxt += 1
            par = dict(n_r, id=rid); par.pop('src_tables', None); par['new'] = '2610'
            new_rows.append(par)
            for i, s in enumerate([x for x in new if x.get('parent') == n_r['id']], 1):
                c = dict(s, id='%s-%d' % (rid, i), parent=rid); c.pop('src_tables', None); c['new'] = '2610'
                new_rows.append(c)
            added.append((P, rid, n_r['n'], len(n_r['k']), sum(1 for x in new if x.get('parent') == n_r['id'])))
        D['riders'][last + 1:last + 1] = new_rows
        if gone_ids:
            D['riders'] = [x for x in D['riders'] if x['id'] not in gone_ids]
        if renamed: print('   갱신형 이름으로 바꿈 %d건 (예 : %s → %s)' % (len(renamed), renamed[0][1], renamed[0][2]))
        for t, tb in new_tabs.items():
            if any(t in r['t'] for r in new_rows) and t not in D['tables']:
                D['tables'][t] = tb
        # 상품만 쓰는 별표의 쪽 번호
        for t, ps in by_t.items():
            if ps == {P} and t in D['tables']:
                pg = new_tab_pages.get(nz(D['tables'][t]['name']))
                if pg and int(D['tables'][t]['page']) != pg:
                    D['tables'][t]['page'] = pg if isinstance(D['tables'][t]['page'], int) else str(pg)
        summary[P] = (len(parents), n_ref, n_ret, len([x for x in new_rows if not x.get('parent')]))
        print('  기존 특약 %d · 본문 개정 %d · 판매중지 %d · 신설 %d' % summary[P])
        for x in unseen: print('   ? 약관 절단 규칙 밖(그대로 둠) :', x[1], x[2])
        for x in skipped: print('   - 옛 약관에도 있던 조각(더하지 않음) :', x[1])
        for x in log:
            if x[0].startswith('KCD') and any(key(x[1]) == key(a[2]) for a in added if a[0] == P): print('   !', x[0], x[1])
    print('\n■ 신설 특약')
    for a in added: print('  %s %-7s %-60s k=%d 세부 %d' % a)
    print('■ 판매중지(%s)' % ('삭제' if DELETE_MISSING else 'ex 표시'))
    for x in retired: print('  %s %-7s %s' % x)
    print('■ 본문 개정(표 되살리기 대상) %d건 (세부 포함)' % len(refresh))
    print('   --only ' + ','.join(refresh + [r['id'] for r in D['riders'] if r.get('new') == '2610']))
    print('■ 쪽 번호 옮김 %d건' % moved)
    used_t = {t for r in D['riders'] for t in r['t']}
    for t in [t for t in D['tables'] if t not in used_t]: del D['tables'][t]
    # 집계 · 버전
    D['meta']['total'] = len(D['riders'])
    D['meta']['prodcount'] = dict(collections.Counter(r['p'] for r in D['riders']))
    D['meta']['version'] = 'ver2613'
    for c in D.get('categories', []):
        if isinstance(c, dict) and 'id' in c: c['count'] = sum(1 for r in D['riders'] if r.get('c') == c['id'])
    if not write:
        print('\n(쓰지 않음 — 반영하려면 --write)'); return
    html = html[:m.start(2)] + json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[m.end(2):]
    html = html.replace('<span class="ver">ver2612</span>', '<span class="ver">ver2613</span>', 1)
    # 상품 히스토리 — 계통별 그룹에 나눠 넣는다(소유자 2026-11-02 : 따로 묶음을 만들지 않고 암통합치료비 · 뇌심 · 치매 계통에)
    def ev(n, e, hl, note, syn, q): return {'d': '2026.10', 'ds': 20261031, 'e': e, 'hl': hl, 'n': n, 'note': note, 'q': q, 'syn': syn}
    NEW_EVENTS = [
        ('암통합치료비 계통', ev('암 통합입통원일당 신설', '신설', 'good', '2610 약관(2026.10.31)부터 통합간편·케어프리(알파Plus)·또또암 등에 탑재. 암통합입통원일당(직접치료,요양병원입원포함) · (직접치료)(암중점치료기관(상급종합병원포함)) 2종. 암 직접치료 입원(요양병원 제외)·암 요양병원 입원(연간 90일 한도)·암 직접치료 통원 일당을 한 특약으로, 가입금액 500/1,000/2,000만원에 따라 입원 3/5/10 · 요양병원 1/2/2 · 통원 3/5/10만원(1년 미만 50%). 연간 총 지급액은 가입금액 한도.', ['암통합입통원일당', '암 통합입통원일당', '암입통원일당'], '암통합입통원일당')),
        ('뇌심(순환계)치료비 계통', ev('특정순환계질환 통합치료비Ⅱ 신설', '신설', 'good', '2610 약관(2026.10.31)부터 탑재. 통합치료항목(검사 MRI·PET·CT / 주요치료 혈전용해·CRRT·인공호흡기·저체온·부분체외순환·종합병원 중환자실·수술 / 재활)과 한도별 금액은 기존 특정순환계질환 통합치료비와 같고, 세부보장으로 「연간 주요치료Ⅱ 3회이상 / 4회이상(연간1회한)」 추가지급이 붙음. 이름 끝 Ⅱ 로 구분.', ['특정순환계질환통합치료비Ⅱ', '순환계 통합치료비2', '특정순환계 통합치료비Ⅱ'], '특정순환계질환통합치료비Ⅱ')),
        ('치매보험 계통', ev('장기요양급여금 3종 판매중지(케어프리 계열)', '판매중단', 'bad', '케어프리 M-Basket · The좋은 케어프리(알파Plus) 2610 약관(2026.10.31)에서 장기요양급여금(1-4등급 · 1-2등급 · 1등급) 빠짐. 특약검색기에는 이전 판 계약 조회용으로 남김.', ['장기요양급여금'], '장기요양급여금')),
    ]
    DROP_GROUPS = ('상해진단·치료비 계통', '2026.10.31 개정(2610) 신설·판매중지')      # 상해진단·치료비 계통은 소유자 지시로 뺀다(2026-11-02)
    def fix_hist(H):
        H['groups'] = [g for g in H['groups'] if g['name'] not in DROP_GROUPS]
        by = {g['name']: g for g in H['groups']}
        for gname, e in NEW_EVENTS:
            g = by[gname]; g['events'] = [x for x in g['events'] if x['n'] != e['n']] + [e]
        H['updated'] = '2026.10.31'
        return H
    h = re.search(r'(<script id="HISTORY" type="application/json">)(.*?)(</script>)', html, re.S)
    H = fix_hist(json.loads(h.group(2)))
    html = html[:h.start(2)] + json.dumps(H, ensure_ascii=False, separators=(',', ':')) + html[h.end(2):]
    sm = re.search(r'(<script id="SIMSRC" type="text/plain">)(.*?)(</script>)', html, re.S)
    if sm:
        sim = base64.b64decode(sm.group(2)).decode('utf-8')
        h2 = re.search(r'(<script id="HISTORY" type="application/json">)(.*?)(</script>)', sim, re.S)
        if h2:
            H2 = fix_hist(json.loads(h2.group(2)))
            sim = sim[:h2.start(2)] + json.dumps(H2, ensure_ascii=False) + sim[h2.end(2):]
            html = html[:sm.start(2)] + base64.b64encode(sim.encode('utf-8')).decode('ascii') + html[sm.end(2):]
    io.open(TOOL, 'w', encoding='utf-8').write(html)
    print('tool.html · tool_body.js 반영 : 특약 %d · 별표 %d' % (D['meta']['total'], len(D['tables'])))


if __name__ == '__main__':
    main('--write' in sys.argv)
