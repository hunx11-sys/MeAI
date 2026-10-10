#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""여행 가이드 JSON 점검기.
사용: python3 -I validate_guide.py <guide.json> [--places]
  --places : 장소 조사 단계 파일(plans/variants/bplan 없음)을 점검
문제가 있으면 줄마다 출력하고 종료코드 1, 없으면 OK."""
import json, sys, math, re

TAGS = {'미식','온천','자연','도시','쇼핑','아이동반','야경','역사','바다','겨울','벚꽃','단풍','테마파크','드라이브','섬','예술','커피','애니','휴양'}
CATS = {'shrine','castle','view','nature','park','street','market','onsen','theme','museum','sea','night','shop','kids','cafe','station','airport','hotel','food'}
TIERS = {'1순위','가성비','감각파','플렉스','온천','가족'}
KEYS = {'sapporo','hakodate','asahikawa','sendai','aomori','tokyo','hakone_kamakura','nagoya','takayama','shizuoka','niigata','toyama','kanazawa','osaka','kyoto','nara','kobe','hiroshima','okayama','yonago','takamatsu','matsuyama','kochi','fukuoka','kitakyushu','nagasaki','kumamoto','oita','kagoshima','miyazaki','saga','okinawa','ishigaki'}
ID_RE = re.compile(r'^[a-z][a-z0-9_]*$')
TIME_RE = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')

def hav(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    path = sys.argv[1]; places_only = '--places' in sys.argv
    errs, warns = [], []
    E = errs.append; W = warns.append
    try:
        g = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        print('JSON 읽기 실패:', e); sys.exit(1)
    req = ['key','name','name_ja','region','prefecture','airports','center','zoom','bbox','tagline','intro','tags','best_months','season_notes','recommended_nights','pace','airport_access','getting_around','transport_pass','spots','restaurants','hotels','checks','sources','generated']
    if not places_only:
        req += ['plans','variants','bplan','nearby_alternatives']
    for k in req:
        if k not in g: E(f'필수 항목 없음: {k}')
    if errs:
        for e in errs: print('오류:', e)
        sys.exit(1)
    if g['key'] not in KEYS: E(f'key 가 목록에 없음: {g["key"]}')
    for t in g['tags']:
        if t not in TAGS: E(f'tags 에 허용되지 않은 값: {t}')
    if not (3 <= len(g['tags']) <= 6): W(f'tags 는 3~6개 권장 (지금 {len(g["tags"])})')
    if g.get('pace') not in {'느긋','보통','빡빡'}: E('pace 는 느긋/보통/빡빡 중 하나')
    bb = g['bbox']
    if not (isinstance(bb, list) and len(bb) == 4 and bb[0] < bb[2] and bb[1] < bb[3]): E('bbox 는 [minLat,minLng,maxLat,maxLng]')
    ids = {}
    def chk_place(p, kind, i):
        pid = p.get('id', '')
        if not ID_RE.match(pid): E(f'{kind}[{i}] id 형식 오류: {pid!r}')
        if pid in ids: E(f'id 중복: {pid} ({ids[pid]} 와 {kind})')
        ids[pid] = kind
        for k in ('name','name_ja','area','lat','lng'):
            if k not in p: E(f'{kind} {pid}: {k} 없음')
        try:
            la, lo = float(p['lat']), float(p['lng'])
            if not (bb[0]-0.3 <= la <= bb[2]+0.3 and bb[1]-0.3 <= lo <= bb[3]+0.3): E(f'{kind} {pid}: 좌표가 bbox 밖 ({la},{lo})')
            if not (24 <= la <= 46 and 122 <= lo <= 146): E(f'{kind} {pid}: 좌표가 일본 밖')
        except Exception: E(f'{kind} {pid}: 좌표 숫자 아님')
    for i, s in enumerate(g['spots']):
        chk_place(s, 'spot', i)
        if s.get('cat') not in CATS: E(f'spot {s.get("id")}: cat 허용값 아님: {s.get("cat")}')
        for k in ('desc','duration_min','access','hours','closed','fee_yen','tip','kid_tip','must'):
            if k not in s: E(f'spot {s.get("id")}: {k} 없음')
    for i, r in enumerate(g['restaurants']):
        chk_place(r, 'restaurant', i)
        for k in ('cuisine','signature','price_level','desc','hours','closed','tips','reserve','maps_q'):
            if k not in r: E(f'restaurant {r.get("id")}: {k} 없음')
        if r.get('price_level') not in (1,2,3): E(f'restaurant {r.get("id")}: price_level 은 1~3')
    for i, h in enumerate(g['hotels']):
        chk_place(h, 'hotel', i)
        for k in ('tier','price_krw_night','desc','pts','maps_q'):
            if k not in h: E(f'hotel {h.get("id")}: {k} 없음')
        if h.get('tier') not in TIERS: E(f'hotel {h.get("id")}: tier 허용값 아님: {h.get("tier")}')
    if not any(s.get('cat') == 'airport' for s in g['spots']): E('cat "airport" 인 spot 이 없음(공항 도착·출발을 ref 로 연결해야 함)')
    if len(g['spots']) < 12: W(f'spots 가 적음 ({len(g["spots"])})')
    if len(g['restaurants']) < 8: W(f'restaurants 가 적음 ({len(g["restaurants"])})')
    if len(g['hotels']) < 3: W(f'hotels 가 적음 ({len(g["hotels"])})')
    for a in g['airport_access']:
        for k in ('airport','mode','to','minutes','fare_yen','note'):
            if k not in a: E(f'airport_access: {k} 없음')
    if places_only:
        report(errs, warns); return
    def chk_days(days, nights, where):
        if len(days) != nights + 1: E(f'{where}: days 길이 {len(days)} ≠ nights+1 ({nights+1})')
        for di, d in enumerate(days):
            for k in ('d','label','title','kicker','note','notice','items'):
                if k not in d: E(f'{where} day{di+1}: {k} 없음')
            if d.get('d') != di + 1: E(f'{where} day{di+1}: d 값이 {d.get("d")}')
            nt = d.get('notice') or {}
            if not isinstance(nt, dict) or nt.get('k') not in ('', 'warn'): E(f'{where} day{di+1}: notice.k 는 "" 또는 "warn"')
            last = -1; meals = 0; prev_ll = None
            for ii, it in enumerate(d.get('items', [])):
                k = it.get('k')
                if k not in ('move','spot','meal','hotel','free'): E(f'{where} day{di+1} item{ii+1}: k 허용값 아님 {k}')
                t = it.get('t', '')
                if not TIME_RE.match(t): E(f'{where} day{di+1} item{ii+1}: t 형식 오류 {t!r}')
                else:
                    m = int(t[:2])*60 + int(t[3:])
                    if m < last: E(f'{where} day{di+1} item{ii+1}: 시각이 거꾸로 감 ({t})')
                    last = m
                if k in ('spot','hotel'):
                    ref = it.get('ref')
                    if ref not in ids: E(f'{where} day{di+1} item{ii+1}: ref 가 없는 id {ref!r}')
                    elif k == 'spot' and ids[ref] not in ('spot','hotel'): E(f'{where} day{di+1} item{ii+1}: spot 항목이 {ids[ref]} 를 가리킴 ({ref})')
                    elif k == 'hotel' and ids[ref] != 'hotel': E(f'{where} day{di+1} item{ii+1}: hotel 항목이 {ids[ref]} 를 가리킴 ({ref})')
                    if ref in ids:
                        p = next((x for x in g['spots'] + g['hotels'] if x['id'] == ref), None)
                        if p:
                            ll = (float(p['lat']), float(p['lng']))
                            if prev_ll and hav(prev_ll, ll) > 80: W(f'{where} day{di+1} item{ii+1}: 직전 장소에서 {hav(prev_ll, ll):.0f}km 떨어짐 ({ref})')
                            prev_ll = ll
                if k == 'meal':
                    meals += 1
                    opts = it.get('opts') or []
                    if not opts: E(f'{where} day{di+1} item{ii+1}: meal 에 opts 없음')
                    for o in opts:
                        if ids.get(o) != 'restaurant': E(f'{where} day{di+1} item{ii+1}: opts 의 {o!r} 가 restaurants id 가 아님')
                    if 'label' not in it: E(f'{where} day{di+1} item{ii+1}: meal 에 label 없음')
                    rl = [next(x for x in g['restaurants'] if x['id'] == o) for o in opts if ids.get(o) == 'restaurant']
                    if rl: prev_ll = (float(rl[0]['lat']), float(rl[0]['lng']))
                if k == 'move':
                    for kk in ('mode','text','minutes'):
                        if kk not in it: E(f'{where} day{di+1} item{ii+1}: move 에 {kk} 없음')
            if meals < 1: E(f'{where} day{di+1}: meal 항목이 없음')
            elif meals < 2 and 0 < di < len(days) - 1: W(f'{where} day{di+1}: 식사가 1끼뿐')
    nights_seen = set()
    for pi, p in enumerate(g['plans']):
        for k in ('nights','days_n','title','theme','summary','days','budget','checks'):
            if k not in p: E(f'plans[{pi}]: {k} 없음')
        n = p.get('nights')
        if n in nights_seen: E(f'plans: nights={n} 가 두 번')
        nights_seen.add(n)
        if p.get('days_n') != (n or 0) + 1: E(f'plans[{pi}]: days_n ≠ nights+1')
        chk_days(p.get('days', []), n or 0, f'plans[{pi}]({n}박)')
        b = p.get('budget') or {}
        for k in ('per','flight_krw','hotel_krw','food_krw','transport_krw','entry_krw','shopping_krw','total_krw','basis'):
            if k not in b: E(f'plans[{pi}] budget: {k} 없음')
        try:  # budget_sum : 합계가 항목 합과 5% 넘게 다르면 주의
            def rng(v): return (v[0], v[1]) if isinstance(v, list) else (v, v)
            lo = sum(rng(b[k])[0] for k in ('flight_krw','hotel_krw','food_krw','transport_krw','entry_krw','shopping_krw'))
            hi = sum(rng(b[k])[1] for k in ('flight_krw','hotel_krw','food_krw','transport_krw','entry_krw','shopping_krw'))
            tl, th = rng(b['total_krw'])
            if abs(tl - lo) > max(lo * 0.05, 1) or abs(th - hi) > max(hi * 0.05, 1): W(f'plans[{pi}] budget: total {tl}~{th} 이 항목 합 {lo}~{hi} 과 다름')
        except Exception: W(f'plans[{pi}] budget: 금액 형식이 이상함')
    if 2 not in nights_seen or 3 not in nights_seen: E('plans 에 2박과 3박이 모두 있어야 함')
    for n in g['recommended_nights']:
        if n not in nights_seen: W(f'recommended_nights 의 {n}박 플랜이 없음')
    if len(g['variants']) < 2: W(f'variants 는 2개 이상 권장 (지금 {len(g["variants"])})')
    for vi, v in enumerate(g['variants']):
        for k in ('for_nights','title','theme','summary','days'):
            if k not in v: E(f'variants[{vi}]: {k} 없음')
        chk_days(v.get('days', []), v.get('for_nights', 0), f'variants[{vi}]')
    for bi, b in enumerate(g['bplan']):
        for k in ('title','desc','ref','maps_q','when'):
            if k not in b: E(f'bplan[{bi}]: {k} 없음')
        if b.get('ref') and b['ref'] not in ids: E(f'bplan[{bi}]: ref 가 없는 id {b["ref"]!r}')
    if len(g['bplan']) < 4: W(f'bplan 은 4개 이상 권장 (지금 {len(g["bplan"])})')
    for ai, a in enumerate(g['nearby_alternatives']):
        if a.get('key') not in KEYS: E(f'nearby_alternatives[{ai}]: key 가 목록에 없음 {a.get("key")!r}')
        if a.get('key') == g['key']: E('nearby_alternatives 에 자기 자신')
        if 'reason' not in a: E(f'nearby_alternatives[{ai}]: reason 없음')
    report(errs, warns)

def report(errs, warns):
    for w in warns: print('주의:', w)
    for e in errs: print('오류:', e)
    if errs:
        print(f'오류 {len(errs)}건 · 주의 {len(warns)}건'); sys.exit(1)
    print(f'OK (주의 {len(warns)}건)')

if __name__ == '__main__':
    main()
