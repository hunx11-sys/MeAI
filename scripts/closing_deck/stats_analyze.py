# -*- coding: utf-8 -*-
"""내려받은 사용 기록 → 결산 PPT 숫자(합계만) scripts/closing_deck/stats_2611.json
  python3 scripts/closing_deck/stats_analyze.py <rows.json>
기준 = 사용 통계 화면(stats.html)과 같음 : 도구 이름 별칭 정리(ALIAS) · 종료 도구(underwriting) 제외 · 날짜 · 시각은 한국시간."""
import calendar, collections, datetime as dt, json, os, sys
R = json.load(open(sys.argv[1]))
KST = dt.timezone(dt.timedelta(hours=9))
ALIAS = {'sim': 'simulator', 'bosang': 'simulator', 'search_sim': 'simulator', 'product': 'products', 'prompt': 'prompts', 'index': 'home', 'main': 'home'}
for r in R:
    r['T'] = dt.datetime.fromisoformat(r['created_at']).astimezone(KST); t = (r.get('tool') or '').strip(); r['tool'] = ALIAS.get(t, t)
END = dt.date(2026, 11, 25)   # 인터넷판 종료일(그 뒤 기록은 사내 노트북 파일 등 — 결산에서 뺀다)
R = [r for r in R if r['tool'] != 'underwriting' and r['T'].date() <= END]
C = collections.Counter
day = C(r['T'].date().isoformat() for r in R); mon = C(r['T'].strftime('%Y-%m') for r in R)
nh = [r for r in R if r['tool'] != 'home']
cut = dt.date(2026, 10, 21)
a = sum(v for k, v in day.items() if k <= cut.isoformat()); b = len(R) - a
last = max(day); nb = (END - cut).days
out = {'기간': [min(day), last], '누적': len(R), '운영일': len(day),
       '하루최고': day.most_common(1)[0], '하루상위10': day.most_common(10),
       '10.21까지': [a, 122, round(a / 122)], '10.22부터': [b, nb, round(b / nb)],
       '월별': sorted(mon.items()), '도구비중_대문제외': {k: round(v / len(nh) * 100, 1) for k, v in C(r['tool'] for r in nh).most_common()},
       '평일비율': round(sum(1 for r in R if r['T'].weekday() < 5) / len(R) * 100, 1),
       '시간대': sorted(C(r['T'].hour for r in R).items()),
       '질병검색': sum(1 for r in R if r['event'] in ('search', 'disease')), '특약상세': sum(1 for r in R if r['event'] == 'rider'),
       '프롬프트복사': sum(1 for r in R if r['event'] in ('copy', 'prompt_copy')),
       '질병조회상위': C((r.get('disease') or '') for r in R if r['event'] == 'disease' and r.get('disease')).most_common(10),
       '특약상세상위': C((r.get('rider_name') or '') for r in R if r['event'] == 'rider').most_common(10),
       '검색어상위': C((r.get('term') or '').strip() for r in R if r['event'] == 'search' and r.get('term')).most_common(10)}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats_2611.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ('누적', '하루최고', '10.21까지', '10.22부터')}, ensure_ascii=False))
