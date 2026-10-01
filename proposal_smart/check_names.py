"""담보명 꼬리표 점검 — 특약 마스터 전 담보 × 상품 꼬리표·갱신형·상품라인 변형(약 10만 건)을 읽혀
   ① 오류(멈춤)가 없는지 ② 꼬리표만 다른 같은 특약이 똑같이 판정되는지(마스터·KCD·제외코드·세부·통합치료비·규칙) 확인한다.
   python check_names.py   (새 상품 꼬리표가 나오면 SUF 에 넣어 다시 돌린다)"""
import sys, re, json, collections, traceback
sys.path.insert(0, '.')
import matcher, scen_engine as S
DB = matcher.DB                                  # db.json + 스마트 제안서 전용 보강 마스터(db_terms_extra.json)
SUF = ['', '(통합간편가입)', '(건강가입)', '(편한가입)', '(355입원,수술고지간편가입)', '(355간편가입)', '(맞춤간편가입)', '(간편가입)', '(일반고지형)', '(새상품간편가입)']
PRE = ['', '갱신형 ']
LINES = [None, '통합간편', '케어프리', '내Mom대로', '내Mom같은어린이']
def row(name, line):
    m, b, s2 = matcher.match(name, line)
    nm = re.sub(matcher.GOJI, '', name).replace('[기본계약]', '').strip()
    rule = None
    try:
        rr = S.classify(S.nname(nm)); rule = rr['id'] if rr else None
    except Exception as ex:
        rule = 'ERR:%s' % ex
    return dict(name=S.nname(re.sub(r'^갱신형\s*', '', nm)), id=(m or {}).get('id'), codes=tuple(sorted((m or {}).get('k') or [])),
                excl=tuple(sorted((m or {}).get('x') or [])), b=b, s=s2, itc=S.itc_id(name), rule=rule)
bad, err, n = [], [], 0
for r in DB['riders']:
    base = r['n']
    for line in LINES:
        ref = None
        for pre in PRE:
            for suf in SUF:
                name = pre + base + suf; n += 1
                try:
                    x = row(name, line)
                except Exception:
                    err.append((name, traceback.format_exc().splitlines()[-1])); continue
                key = (x['codes'], x['excl'], x['b'], x['s'], x['itc'], x['rule'])
                if suf == '':
                    if pre == '': ref = key
                    continue
                if key != ref and pre == '':
                    bad.append((line, base, suf, ref, key))
print('검사한 담보명 변형', n, '· 오류', len(err), '· 꼬리표에 따라 판정이 달라진 것', len(bad))
for e in err[:5]: print('  ERR', e)
c = collections.Counter(b[2] for b in bad); print('  꼬리표별', c.most_common())
for b in bad[:8]: print('  DIFF', b[0], '|', b[1][:50], '|', b[2], '\n     ', str(b[3])[:150], '\n  →  ', str(b[4])[:150])
