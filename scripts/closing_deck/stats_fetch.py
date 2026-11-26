# -*- coding: utf-8 -*-
"""사용 통계 서버(usage_logs) 전체 기록 내려받기 — 결산 PPT 숫자의 원천
  python3 scripts/closing_deck/stats_fetch.py <저장할 rows.json>
주소 · 읽기 전용 익명 키는 stats.html 에 있는 것을 읽어 쓴다(이 파일에 적지 않는다). 내려받은 기록은 저장소에 올리지 않는다(검색어 원문)."""
import json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s = open(os.path.join(ROOT, 'stats.html'), encoding='utf-8').read()
url, key = re.search(r"url:\s*'([^']+)'\s*,\s*key:\s*'([^']+)'", s).groups()
base = url + '/rest/v1/usage_logs?select=created_at,tool,event,term,rider_name,disease&order=created_at.asc'
rows, f, P = [], 0, 1000
while True:
    req = urllib.request.Request(base, headers={'apikey': key, 'Authorization': 'Bearer ' + key, 'Range-Unit': 'items', 'Range': '%d-%d' % (f, f + P - 1)})
    part = json.load(urllib.request.urlopen(req, timeout=60)); rows += part
    if len(part) < P: break
    f += P
json.dump(rows, open(sys.argv[1], 'w'), ensure_ascii=False)
print('기록 %d건 · %s ~ %s' % (len(rows), rows[0]['created_at'][:10], rows[-1]['created_at'][:10]))
