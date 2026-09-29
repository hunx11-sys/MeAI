# -*- coding: utf-8 -*-
"""특약검색기(tool.html)에 내장된 DATA(JSON) → 특약 마스터 db.json 생성.
   사용 : python extract_db.py ../tool.html
   tool.html 데이터가 갱신되면(질병코드 보정·신담보) 이 스크립트 한 번으로 마스터를 맞춘다.
   약관 본문(b·s·st·l)은 지면 생성에 쓰지 않으므로 제외하고 id·p·n·c·pg·k·x·t 를 남긴다(x = 제외코드)."""
import json, os, re, sys
KEEP = ('id', 'p', 'n', 'c', 'pg', 'k', 'x', 't', 'hc')      # x = 제외코드(보상하지 않는 질병) — v8.7부터 엔진이 적용
def extract(html_path):
    html = open(html_path, encoding='utf-8').read()
    m = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', html, re.S)
    if not m: raise SystemExit('tool.html 에서 <script id="DATA"> 를 찾지 못했습니다')
    d = json.loads(m.group(1))
    return {'meta': d['meta'], 'categories': d['categories'],
            'riders': [{k: r.get(k, [] if k in ('k', 'x', 't', 'hc') else None) for k in KEEP} for r in d['riders']]}
if __name__ == '__main__':
    db = extract(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tool.html'))
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.json')
    old = json.load(open(dst, encoding='utf-8')) if os.path.exists(dst) else None
    json.dump(db, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    ch, changed = 0, []
    if old:
        om = {r['id']: r for r in old['riders']}
        for r in db['riders']:
            o = om.get(r['id'])
            if o == r: continue
            ch += 1
            # 무엇이 달라졌는지(새 특약 / 코드·제외코드·수가코드·이름) — 개정 검수 때 사람이 볼 범위가 이 목록이다(v8.61)
            what = '신규' if o is None else '·'.join(lbl for key, lbl in (('k', 'KCD'), ('x', '제외코드'), ('hc', '수가코드'), ('n', '이름'), ('c', '분류'))
                                                    if o.get(key) != r.get(key)) or '기타'
            changed.append({'id': r['id'], 'p': r['p'], 'n': r['n'], 'what': what})
        gone = [{'id': i, 'p': o['p'], 'n': o['n'], 'what': '삭제'} for i, o in om.items() if i not in {r['id'] for r in db['riders']}]
        changed += gone; ch += len(gone)
    print('db.json 생성 :', dst, '| 특약', len(db['riders']), '· KCD 보유', sum(1 for r in db['riders'] if r['k']), '· 변경', ch, '건')
    if changed:
        outdir = os.path.join(os.path.dirname(dst), 'out'); os.makedirs(outdir, exist_ok=True)
        lst = os.path.join(outdir, 'db_changed.json')
        json.dump(changed, open(lst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('바뀐 특약 목록(개정 검수 대상) :', lst)
        for c in changed[:30]: print('  [%s] %s %s — %s' % (c['what'], c['id'], c['n'], c['p']))
        if len(changed) > 30: print('  … 외 %d건 (목록 파일 참조)' % (len(changed) - 30))
