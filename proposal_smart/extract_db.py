# -*- coding: utf-8 -*-
"""특약검색기(tool.html)에 내장된 DATA(JSON) → 특약 마스터 db.json 생성.
   사용 : python extract_db.py ../tool.html
   tool.html 데이터가 갱신되면(질병코드 보정·신담보) 이 스크립트 한 번으로 마스터를 맞춘다.
   약관 본문(b·s·st·l·x)은 지면 생성에 쓰지 않으므로 제외하고 id·p·n·c·pg·k·t 만 남긴다."""
import json, os, re, sys
KEEP = ('id', 'p', 'n', 'c', 'pg', 'k', 't')
def extract(html_path):
    html = open(html_path, encoding='utf-8').read()
    m = re.search(r'<script id="DATA" type="application/json">(.*?)</script>', html, re.S)
    if not m: raise SystemExit('tool.html 에서 <script id="DATA"> 를 찾지 못했습니다')
    d = json.loads(m.group(1))
    return {'meta': d['meta'], 'categories': d['categories'],
            'riders': [{k: r.get(k, [] if k in ('k', 't') else None) for k in KEEP} for r in d['riders']]}
if __name__ == '__main__':
    db = extract(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tool.html'))
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.json')
    old = json.load(open(dst, encoding='utf-8')) if os.path.exists(dst) else None
    json.dump(db, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    ch = 0
    if old:
        om = {r['id']: r for r in old['riders']}
        ch = sum(1 for r in db['riders'] if om.get(r['id']) != r)
    print('db.json 생성 :', dst, '| 특약', len(db['riders']), '· KCD 보유', sum(1 for r in db['riders'] if r['k']), '· 변경', ch, '건')
