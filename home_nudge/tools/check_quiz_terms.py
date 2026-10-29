# OX 문제 은행(data/ox_bank.json)의 약관 문항을 특약검색기 약관 원문과 글자 대조한다.
#   python3 home_nudge/tools/check_quiz_terms.py          (저장소 루트의 tool.html · tool_body.js 를 읽는다)
# - check.quote : 그 상품 · 특약 본문(또는 분류표 글)에 그 구절이 그대로 있는지 (띄어쓰기 · 줄바꿈은 무시)
# - check.codes / notCodes : 분류표에 그 질병코드가 있는지 · 없는지 (질병코드는 분류표에서만 온다)
# 개발 패키지처럼 약관 원문이 없는 곳에서는 「건너뜀」으로 끝난다(실패 아님).
import json, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'scripts'))


def norm(s): return re.sub(r'\s+', '', s or '')


def main():
    bank = json.load(open(os.path.join(HERE, 'data', 'ox_bank.json'), encoding='utf-8'))
    html_p = os.path.join(REPO, 'tool.html')
    if not os.path.exists(html_p) or not os.path.exists(os.path.join(REPO, 'tool_body.js')):
        print('약관 원문(tool.html · tool_body.js)이 없어 건너뜀')
        return 0
    from tooldata import inflate
    html = open(html_p, encoding='utf-8').read()
    D = inflate(json.loads(re.search(r'<script id="DATA" type="application/json">(.*?)</script>', html, re.S).group(1)))
    riders = {}
    for r in D['riders']:
        riders.setdefault((r['p'], r['n']), []).append(r)
    tables = {}
    for t in D['tables'].values():
        tables.setdefault(t['name'], []).append(t)
    bad, n = [], 0
    for it in bank['items']:
        c = it.get('check')
        if it['cat'] == 'terms' and not c: bad.append((it['id'], '약관 문항인데 대조 근거(check)가 없음'))
        if not c: continue
        n += 1
        if 'quote' in c and 'p' in c:
            rs = riders.get((c['p'], c['n']))
            if not rs: bad.append((it['id'], '특약을 찾지 못함 : ' + c['p'] + ' ' + c['n'])); continue
            if not any(norm(c['quote']) in norm(r.get('b')) for r in rs): bad.append((it['id'], '약관 본문에 구절이 없음 : ' + c['quote']))
        if 'table' in c:
            ts = tables.get(c['table'])
            if not ts: bad.append((it['id'], '분류표를 찾지 못함 : ' + c['table'])); continue
            codes = set(x for t in ts for row in t['rows'] for x in row['codes'])
            if 'quote' in c and not any(norm(c['quote']) in norm(t.get('text')) for t in ts): bad.append((it['id'], '분류표 글에 구절이 없음 : ' + c['quote']))
            for x in c.get('codes', []):
                if x not in codes: bad.append((it['id'], c['table'] + ' 에 ' + x + ' 없음'))
            for x in c.get('notCodes', []):
                if x in codes: bad.append((it['id'], c['table'] + ' 에 ' + x + ' 가 있음(문항과 반대)'))
            if c.get('alsoTable'):
                also = set(x for t in tables.get(c['alsoTable'], []) for row in t['rows'] for x in row['codes'])
                for x in c.get('alsoCodes', []):
                    if x not in also: bad.append((it['id'], c['alsoTable'] + ' 에 ' + x + ' 없음'))
    # 모든 문항 기본 모양
    for it in bank['items']:
        if it['a'] not in ('O', 'X'): bad.append((it['id'], '답은 O 또는 X'))
        if it['cat'] not in bank['cats']: bad.append((it['id'], '없는 갈래 : ' + it['cat']))
        if not it.get('src'): bad.append((it['id'], '출처 없음'))
        if '—' in it['q'] + it['why'] + ''.join(it.get('more', [])): bad.append((it['id'], '긴 줄표'))
    ids = [it['id'] for it in bank['items']]
    if len(ids) != len(set(ids)): bad.append(('-', '같은 id 가 있음'))
    by = {}
    for it in bank['items']: by[it['cat']] = by.get(it['cat'], 0) + 1
    print('문항', len(ids), '개 ·', ' · '.join(bank['cats'][k]['label'] + ' ' + str(v) for k, v in by.items()), '· 약관 대조', n, '개')
    for b in bad: print('  실패', b[0], b[1])
    print('결과 :', '통과' if not bad else '실패 ' + str(len(bad)) + '건')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
