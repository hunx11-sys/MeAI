#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""직항 노선 조사 워크플로의 결과(JSON)를 travel/data/jp_airports.json 으로 정리한다.

   사용 : python3 travel/tools/merge_flights.py <워크플로 결과.json> [출력 경로]

   결과 JSON 의 모양 : {"regions":[{"region_key","airports":[...]}], "krSweep":{"routes":[...]},
                       "verified":[{"iata","verdicts":[...],"missing_routes":[...]}], "gaps":[...], "gapVerdicts":[...]}
   정리 규칙(회의론자 판정을 반영한다) :
     확인  → 조사값 유지(정정값이 있으면 상태·횟수를 정정값으로)
     의심  → 상태를 '확인필요' 로 바꾼다(지우지 않는다)
     반박  → 그 항공사를 노선에서 뺀다. 항공사가 하나도 안 남으면 노선 상태를 '운휴' 로 둔다(화면에서는 숨겨짐)
     missing_routes · gaps(한국 공항별 조사에만 있던 노선) 은 판정이 '확인' 이면 추가, '의심' 이면 '확인필요' 로 추가, '반박' 이면 넣지 않는다.
   출처 URL 은 노선마다 남긴다. 근거 없는 노선을 만들어 넣지 않는다."""
import json, os, sys, datetime

ORDER = ['ICN', 'GMP', 'PUS', 'CJU', 'TAE', 'CJJ', 'MWX', 'KWJ', 'RSU', 'USN', 'KPO', 'WJU', 'YNY', 'KUV', 'HIN']
STATUS_RANK = {'정기': 0, '계절': 1, '전세': 2, '확인필요': 3, '운휴': 9}


def norm_air(s):
    s = (s or '').strip()
    rep = {'제주에어': '제주항공', 'Jeju Air': '제주항공', 'Korean Air': '대한항공', 'Asiana': '아시아나항공', '아시아나': '아시아나항공',
           'Jin Air': '진에어', 'T\'way': '티웨이항공', 'Tway': '티웨이항공', '티웨이': '티웨이항공', 'Air Busan': '에어부산', 'Air Seoul': '에어서울',
           'Eastar Jet': '이스타항공', '이스타': '이스타항공', 'Aero K': '에어로케이', 'Air Premia': '에어프레미아', 'Peach': '피치항공', '피치': '피치항공',
           'ANA': 'ANA', 'JAL': 'JAL', '전일본공수': 'ANA', '일본항공': 'JAL', 'Jetstar Japan': '젯스타재팬', 'Spring Japan': '스프링재팬'}
    return rep.get(s, s)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    src = json.load(open(sys.argv[1], encoding='utf-8'))
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'jp_airports.json')
    airports = {}
    for rg in src.get('regions', []) or []:
        for a in rg.get('airports', []):
            a = dict(a)
            a['routes'] = [dict(r, airlines=[norm_air(x) for x in r.get('airlines', [])]) for r in a.get('routes', [])]
            if a['iata'] in airports:
                airports[a['iata']]['routes'] += a['routes']
            else:
                airports[a['iata']] = a
    log = []

    def find_route(a, frm):
        for r in a['routes']:
            if r['from_iata'] == frm:
                return r
        return None

    # 1) 공항별 회의론자 판정 반영
    for v in src.get('verified', []) or []:
        a = airports.get(v.get('iata'))
        if not a:
            continue
        for vd in v.get('verdicts', []):
            r = find_route(a, vd.get('from_iata'))
            if not r:
                continue
            al = norm_air(vd.get('airline'))
            if vd.get('verdict') == '반박':
                if al in r['airlines']:
                    r['airlines'].remove(al)
                    log.append('반박 %s→%s %s : %s' % (vd['from_iata'], a['iata'], al, vd.get('reason', '')))
                if not r['airlines']:
                    r['status'] = '운휴'
                    r['season_note'] = (r.get('season_note', '') + ' ' + vd.get('reason', '')).strip()
            elif vd.get('verdict') == '의심':
                if r['status'] != '운휴':
                    r['status'] = '확인필요'
                r['season_note'] = (r.get('season_note', '') + ' ' + vd.get('reason', '')).strip()
                log.append('의심 %s→%s %s : %s' % (vd['from_iata'], a['iata'], al, vd.get('reason', '')))
            else:  # 확인
                if vd.get('corrected_status') and vd['corrected_status'] != r['status']:
                    log.append('정정 %s→%s 상태 %s→%s' % (vd['from_iata'], a['iata'], r['status'], vd['corrected_status']))
                    r['status'] = vd['corrected_status']
                if vd.get('corrected_weekly'):
                    r['weekly'] = vd['corrected_weekly']
                if vd.get('source_url') and not r.get('source_url'):
                    r['source_url'] = vd['source_url']
                r['verified'] = True
        for m in v.get('missing_routes', []):
            if not m.get('source_url'):
                continue
            r = find_route(a, m['from_iata'])
            if r:
                for al in m.get('airlines', []):
                    al = norm_air(al)
                    if al not in r['airlines']:
                        r['airlines'].append(al)
                        log.append('추가 항공사 %s→%s %s' % (m['from_iata'], a['iata'], al))
                if r['status'] == '운휴':
                    r['status'] = m.get('status', '확인필요')
            else:
                a['routes'].append({'from_iata': m['from_iata'], 'airlines': [norm_air(x) for x in m.get('airlines', [])], 'flight_minutes': m.get('flight_minutes', 0),
                                    'weekly': m.get('weekly', ''), 'status': m.get('status', '확인필요'), 'season_note': '검증 단계에서 추가',
                                    'source_url': m.get('source_url', ''), 'source_date': '', 'confidence': '보통'})
                log.append('추가 노선 %s→%s %s' % (m['from_iata'], a['iata'], '/'.join(m.get('airlines', []))))

    # 2) 한국 공항별 조사에만 있던 노선(gaps) 은 빈틈 검증 판정에 따라 추가
    gv = {}
    for v in src.get('gapVerdicts', []) or []:
        for vd in v.get('verdicts', []):
            gv.setdefault((vd.get('from_iata'), v.get('iata')), []).append(vd)
    for g in src.get('gaps', []) or []:
        a = airports.get(g.get('to_iata'))
        if not a:
            log.append('빈틈 %s→%s : 공항 자료 없음, 건너뜀' % (g.get('from_iata'), g.get('to_iata')))
            continue
        vds = gv.get((g['from_iata'], g['to_iata']), [])
        verdicts = [x.get('verdict') for x in vds]
        if not vds or all(x == '반박' for x in verdicts):
            log.append('빈틈 %s→%s : %s, 넣지 않음' % (g['from_iata'], g['to_iata'], '판정 없음' if not vds else '반박'))
            continue
        status = g.get('status', '확인필요')
        if '확인' not in verdicts:
            status = '확인필요'
        else:
            cs = [x.get('corrected_status') for x in vds if x.get('verdict') == '확인' and x.get('corrected_status')]
            if cs:
                status = cs[0]
        src_url = g.get('source_url') or next((x.get('source_url') for x in vds if x.get('source_url')), '')
        r = find_route(a, g['from_iata'])
        if r:
            for al in g.get('airlines', []):
                al = norm_air(al)
                if al not in r['airlines']:
                    r['airlines'].append(al)
            if STATUS_RANK.get(status, 5) < STATUS_RANK.get(r['status'], 5):
                r['status'] = status
        else:
            a['routes'].append({'from_iata': g['from_iata'], 'airlines': [norm_air(x) for x in g.get('airlines', [])], 'flight_minutes': 0,
                                'weekly': g.get('weekly', ''), 'status': status, 'season_note': g.get('note', ''), 'source_url': src_url,
                                'source_date': '', 'confidence': '보통'})
        log.append('빈틈 추가 %s→%s %s (%s)' % (g['from_iata'], g['to_iata'], '/'.join(g.get('airlines', [])), status))

    # 3) 정리 : 같은 출발지 노선 합치기, 출처 없는 노선은 확인필요, 비행시간 0 은 같은 공항 다른 노선 값으로 채움
    for a in airports.values():
        merged = {}
        for r in a['routes']:
            k = r['from_iata']
            if k in merged:
                m = merged[k]
                for al in r['airlines']:
                    if al not in m['airlines']:
                        m['airlines'].append(al)
                if STATUS_RANK.get(r['status'], 5) < STATUS_RANK.get(m['status'], 5):
                    m['status'], m['weekly'] = r['status'], r['weekly'] or m['weekly']
                if not m.get('source_url') and r.get('source_url'):
                    m['source_url'] = r['source_url']
                if not m.get('flight_minutes') and r.get('flight_minutes'):
                    m['flight_minutes'] = r['flight_minutes']
            else:
                merged[k] = r
        rs = list(merged.values())
        known = [r['flight_minutes'] for r in rs if r.get('flight_minutes')]
        for r in rs:
            if not r.get('source_url') and r['status'] in ('정기', '계절', '전세'):
                r['status'] = '확인필요'
                log.append('출처 없음 → 확인필요 %s→%s' % (r['from_iata'], a['iata']))
            if not r.get('flight_minutes') and known:
                r['flight_minutes'] = int(sum(known) / len(known))
            r['airlines'] = [x for x in r['airlines'] if x]
        rs.sort(key=lambda r: (ORDER.index(r['from_iata']) if r['from_iata'] in ORDER else 99))
        a['routes'] = rs
        a['has_korea_direct'] = any(r['status'] in ('정기', '계절', '전세') for r in rs)
    out = {'generated': datetime.date.today().isoformat(), 'note': '회의론자 검증을 거친 조사값. 확인필요 = 근거가 약하거나 판정이 엇갈림. 운휴 = 화면에 숨김',
           'airports': sorted(airports.values(), key=lambda a: a['iata'])}
    json.dump(out, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n_direct = sum(1 for a in out['airports'] if a['has_korea_direct'])
    n_routes = sum(len([r for r in a['routes'] if r['status'] != '운휴']) for a in out['airports'])
    print('공항 %d개 (한국 직항 %d개) · 노선 %d건 → %s' % (len(out['airports']), n_direct, n_routes, out_path))
    for l in log:
        print('  ' + l)


if __name__ == '__main__':
    main()
