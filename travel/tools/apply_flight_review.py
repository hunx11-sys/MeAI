#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""travel/data/flight_review.json 의 보정 목록을 travel/data/jp_airports.json 에 적용한다.
   사용 : python3 travel/tools/apply_flight_review.py
   - airline_names : 항공사 이름 통일(예: 티웨이 → 트리니티항공(구 티웨이))
   - overrides     : 공항·출발지별 상태/항공사/주 횟수/신뢰도 보정. 출처가 없으면 season_note 에 그 사실을 남긴다
   - flight_minutes_default : 비행시간이 0 인 노선의 대략값"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AP = os.path.join(ROOT, 'data', 'jp_airports.json')
RV = os.path.join(ROOT, 'data', 'flight_review.json')


def main():
    d = json.load(open(AP, encoding='utf-8'))
    rv = json.load(open(RV, encoding='utf-8'))
    names = rv.get('airline_names', {})
    idx = {a['iata']: a for a in d['airports']}
    n = 0
    for a in d['airports']:
        for r in a['routes']:
            seen, out = set(), []
            for al in r['airlines']:
                al = names.get(al, al)
                if al and al not in seen:
                    seen.add(al); out.append(al)
            r['airlines'] = out
            if not r.get('flight_minutes'):
                r['flight_minutes'] = rv.get('flight_minutes_default', {}).get(a['iata'], 0)
    for o in rv.get('overrides', []):
        a = idx.get(o['iata'])
        if not a:
            print('공항 없음:', o['iata']); continue
        r = next((x for x in a['routes'] if x['from_iata'] == o['from']), None)
        if not r:
            r = {'from_iata': o['from'], 'airlines': [], 'flight_minutes': rv.get('flight_minutes_default', {}).get(a['iata'], 0), 'weekly': '', 'status': '확인필요',
                 'season_note': '', 'source_url': '', 'source_date': '', 'confidence': '낮음'}
            a['routes'].append(r)
        before = r['status']
        r['status'] = o.get('status', r['status'])
        if o.get('airlines'):
            r['airlines'] = [names.get(x, x) for x in o['airlines']]
        if o.get('weekly'):
            r['weekly'] = o['weekly']
        if o.get('confidence'):
            r['confidence'] = o['confidence']
        note = o.get('note', '')
        if note:
            r['season_note'] = note if not r.get('source_url') else (r.get('season_note', '') + ' ' + note).strip()
        r['reviewed'] = '2026-10-10 지식 기반 보정'
        n += 1
        print('  %s→%s %s → %s' % (o['from'], o['iata'], before, r['status']))
    for a in d['airports']:
        a['has_korea_direct'] = any(r['status'] in ('정기', '계절', '전세') for r in a['routes'])
        a['routes'].sort(key=lambda r: ['ICN', 'GMP', 'PUS', 'CJU', 'TAE', 'CJJ', 'MWX', 'KWJ', 'RSU', 'USN', 'KPO', 'WJU', 'YNY', 'KUV', 'HIN'].index(r['from_iata']) if r['from_iata'] in ['ICN', 'GMP', 'PUS', 'CJU', 'TAE', 'CJJ', 'MWX', 'KWJ', 'RSU', 'USN', 'KPO', 'WJU', 'YNY', 'KUV', 'HIN'] else 99)
    d['reviewed'] = rv.get('note', '')
    json.dump(d, open(AP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('보정 %d건 적용 · 한국 직항 공항 %d개' % (n, sum(1 for a in d['airports'] if a['has_korea_direct'])))


if __name__ == '__main__':
    main()
