# -*- coding: utf-8 -*-
"""스마트 제안서 · GA 스마트 제안서 점검 하네스 — 새 상품·신담보·새 약관이 들어와도 오류 없이 칸에 들어가는지 한 번에 본다.

  python harness.py                      # H1~H5 (설계서 PDF 없이 · 저장소만으로) — 자동 점검(CI)이 돌리는 것
  python harness.py --designs <폴더>      # + H6 : 폴더의 설계서 PDF 마다 GA 지면을 만들어 칸 스펙과 대조(개인정보 PDF 는 저장소 밖)
  python harness.py --full               # H3 를 꼬리표 10종 × 상품라인 5종 전수로(약 10분)

점검 항목 (하나라도 실패면 종료코드 1)
  H1 특약 마스터 무결성   db.json + db_terms_extra.json : id·이름 중복, 질병코드 표기 형식(A00 · A00.0 · A00~A09 · !A00)
  H2 규칙 판정           모든 특약이 통합치료비 금액표 · 통합생활지원비 항목표 · 규칙표 중 하나로 판정되는지(미분류 0)
  H3 담보명 꼬리표        같은 특약에 상품 꼬리표((…가입))·갱신형을 붙여도 마스터·질병코드·규칙 판정이 같은지
  H4 GA 칸 전수 계산      마스터 전 특약(실제 가입금액 구간)을 GA 칸 사례 전부에 넣어 계산 — 오류 0 · 근거 없는 지급 0
  H5 금액 상식           지급 줄 금액이 가입금액(통합치료비·생활지원비는 연·월 한도)을 넘지 않는지 · 음수·NaN 없음
  H6 설계서 대조(선택)     설계서마다 GA 지면 생성 오류 0 · 칸 넘침 0 · 지면 표시값 = 칸 스펙 계산값(전 칸) · 1쪽 뒤 합산 계산서 3쪽 존재
결과 : out/harness_report.json (+ 화면 요약)."""
import sys, os, re, json, math, time, collections, argparse, traceback
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
os.chdir(BASE)
import scen_engine as S, matcher, engine as itc

ap = argparse.ArgumentParser(); ap.add_argument('--designs'); ap.add_argument('--full', action='store_true')
A = ap.parse_args()
REPORT = collections.OrderedDict(); FAIL = []
def res(key, ok, summary, items=None, warn=False):
    REPORT[key] = {'ok': ok, 'warn': warn, 'summary': summary, 'items': (items or [])[:200]}
    if not ok: FAIL.append(key)
    print('%s %-28s %s' % ('통과' if ok else '실패', key, summary))
    for it in (items or [])[:8]: print('      ·', str(it)[:180])

DB = matcher.DB['riders']
# ── H1 ─────────────────────────────────────────────
KCD = re.compile(r'^!?[A-Z]\d{2}(\.\d{1,2})?(~[A-Z]?\d{2}(\.\d{1,2})?)?$')
ids = collections.Counter(r['id'] for r in DB)
bad = ['%s 질병코드 형식 %s' % (r['id'], c) for r in DB for c in (r.get('k') or []) + (r.get('x') or []) if not KCD.match(c.strip())]
dup = ['id 중복 %s ×%d' % (i, n) for i, n in ids.items() if n > 1]
noname = ['%s 이름 없음' % r['id'] for r in DB if not (r.get('n') or '').strip()]
res('H1 특약 마스터 무결성', not (bad or dup or noname), '특약 %d건 · 형식 오류 %d · id 중복 %d · 이름 없음 %d' % (len(DB), len(bad), len(dup), len(noname)), dup + noname + bad)

# ── H2 ─────────────────────────────────────────────
un = []
for r in DB:
    nm = r['n']
    if S.itc_id(nm) or S.ls_id(nm): continue
    if S.classify(S.nname(nm)) is None: un.append('%s %s %s' % (r['id'], r['p'], nm))
res('H2 규칙 판정', not un, '규칙 미분류 %d건 / %d' % (len(un), len(DB)), un)

# ── H3 ─────────────────────────────────────────────
SUF = ['', '(통합간편가입)', '(편한가입)', '(355입원,수술고지간편가입)', '(새상품간편가입)'] + (['(건강가입)', '(355간편가입)', '(맞춤간편가입)', '(간편가입)', '(일반고지형)'] if A.full else [])
LINES = [None] + (sorted({r['p'] for r in DB}) if A.full else [])
def sig(name, line):
    m, b, s2 = matcher.match(name, line)
    nm = re.sub(matcher.GOJI, '', name).replace('[기본계약]', '').strip()
    rr = S.classify(S.nname(nm))
    return (tuple(sorted((m or {}).get('k') or [])), tuple(sorted((m or {}).get('x') or [])), b, s2, S.itc_id(name), (rr or {}).get('id'))
diff, err, n = [], [], 0
for r in DB:
    for line in LINES:
        ref = None
        for suf in SUF:
            n += 1
            try:
                k = sig(r['n'] + suf, line)
            except Exception as ex:
                err.append('%s%s : %s' % (r['n'], suf, ex)); continue
            if suf == '': ref = k
            elif k != ref: diff.append('%s | %s | %s' % (line, r['n'], suf))
res('H3 담보명 꼬리표', not (diff or err), '이름 변형 %d건 · 오류 %d · 꼬리표에 따라 판정이 달라진 것 %d' % (n, len(err), len(diff)), err + diff)

# ── H4 · H5 ────────────────────────────────────────
import ga_spec as GS
uni = GS.universe()
cells = [c for c in GS.CELLS if c['kind'] == 'engine' and c.get('sc')]
S.ISSUES.clear(); errs4, over, paid = [], [], collections.Counter()
t0 = time.time()
for c in cells:
    try:
        L = S.pay_lines(uni, json.loads(json.dumps(c['sc'])))
    except Exception as ex:
        errs4.append('%s 사례 계산 멈춤 : %s' % (c['id'], ex)); continue
    for l in L:
        paid[l['name']] += 1
        a = l.get('amt')
        rr = next((u for u in uni if u['name'] == l['name']), None); man = (rr or {}).get('man') or 0
        if a is None or (isinstance(a, float) and math.isnan(a)) or a < 0: over.append('%s %s 금액 %s' % (c['id'], l['name'], a))
        elif l.get('rule') not in ('itc', 'ls_monthly') and (S.classify(S.nname(l['name'])) or {}).get('kind') != 'day' and man and a > man * 2 + 1e-6:
            over.append('%s %s 지급 %s > 가입금액 %s×2' % (c['id'], l['name'], a, man))
        elif l.get('rule') in ('itc', 'ls_monthly') and man and a > man + 1e-6:
            over.append('%s %s 지급 %s > 한도 %s' % (c['id'], l['name'], a, man))
eo = [ '%s — %s' % (i['담보'], i['사유']) for i in S.ISSUES if i['구분'] == '오류']
res('H4 GA 칸 전수 계산', not (errs4 or eo), '특약 %d건 × 칸 사례 %d개 (%.0f초) · 오류 %d · 지급이 잡힌 특약 %d' % (len(uni), len(cells), time.time() - t0, len(errs4) + len(eo), len(paid)), errs4 + eo)
lg = collections.Counter(i['구분'] for i in S.ISSUES)
REPORT['H4 로그 구분'] = dict(lg)
res('H5 금액 상식', not over, '한도 초과·음수 %d건' % len(over), over)

# ── H6 ─────────────────────────────────────────────
if A.designs:
    import ga_proposal as G
    out = os.path.join(BASE, 'out', 'harness'); os.makedirs(out, exist_ok=True)
    rows, bad6 = [], []
    for f in sorted(os.listdir(A.designs)):
        if not f.lower().endswith('.pdf'): continue
        p = os.path.join(A.designs, f)
        try:
            G.load(p, ''); h = G.html(p); hp = os.path.join(out, f + '.html'); open(hp, 'w', encoding='utf-8').write(h)
            d = GS.run_design(p, hp); c = d['cmp'] or {}
            unm = [r['name'] for r in d['riders'] if not r['matched']]
            ok = bool(c.get('equal'))
            pg = re.findall(r'<div class="page( calcpg)?">', h)                         # 쪽 순서 : 1쪽 → 계산서 3쪽 → 2~6쪽
            if pg[:1 + G.CALC_PAGES] != [''] + [' calcpg'] * G.CALC_PAGES or len(pg) != 6 + G.CALC_PAGES:
                ok = False; bad6.append('%s 1쪽 뒤 합산 계산서 %d쪽이 없음 (쪽 구성 %s)' % (f, G.CALC_PAGES, [x.strip() or 'p' for x in pg]))
            rows.append('%s : 담보 %d · 미매칭 %d · 지면=스펙 %s (%s/%s)' % (f, d['nriders'], len(unm), '일치' if ok else '불일치', c.get('html_n'), c.get('spec_n')))
            if not ok: bad6.append('%s 칸 불일치 %s' % (f, (c.get('diffs') or [])[:3]))
            if unm: rows.append('   미매칭 : ' + ' · '.join(unm[:6]))
        except Exception as ex:
            bad6.append('%s 생성 오류 %s' % (f, traceback.format_exc().splitlines()[-1]))
    res('H6 설계서 대조', not bad6, '설계서 %d건 · 실패 %d' % (len([1 for r in rows if not r.startswith('   ')]), len(bad6)), bad6 + rows)

os.makedirs(os.path.join(BASE, 'out'), exist_ok=True)
json.dump(REPORT, open(os.path.join(BASE, 'out', 'harness_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n결과 :', '전부 통과' if not FAIL else '실패 %d개 — %s' % (len(FAIL), ', '.join(FAIL)))
sys.exit(1 if FAIL else 0)
