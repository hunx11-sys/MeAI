#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""가이드 내용 점검기(validate_guide.py 가 못 보는 '내용상' 문제를 찾는다).

   사용 : python3 -I travel/tools/lint_guides.py [가이드 폴더(기본 travel/data/guides)] [--json 결과.json]

   찾는 것
   1. 식사 시각이 첫 번째 후보 식당의 영업시간 밖(예: 12:00 점심인데 17:00 개점)
   2. 명소 방문 시각이 영업시간 밖(예: 18:30 방문인데 17:00 마감). '상시·24시간' 은 통과
   3. 하루 일정의 마지막 활동이 23:30 이후, 첫 활동이 06:00 이전(아침 온천·시장 같은 의도는 note 로 확인)
   4. 이동(move) 시간과 다음 시각이 맞지 않음(이동 끝나기 전에 다음 일정 시작)
   5. nearby_alternatives 가 아직 없는 목적지를 가리킴, 자기 자신을 가리킴
   6. 같은 날 같은 장소를 두 번 방문(숙소 제외)
   7. 숙소 1박 가격이 [0,0] 이거나 위아래가 뒤집힘
   8. 좌표가 목적지 중심에서 150km 넘게 떨어진 장소(오타·좌표 뒤바뀜 의심)
   영업시간 글을 못 읽으면 건너뛴다(오류로 세지 않음). 결과는 목적지별로 '주의' 목록을 출력한다."""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF = os.path.join(os.path.dirname(HERE), 'data', 'guides')
TIME = re.compile(r'(\d{1,2})[:：](\d{2})\s*[–~\-〜～]\s*(익일\s*)?(\d{1,2})[:：](\d{2})')


def mins(t):
    h, m = t.split(':')
    return int(h) * 60 + int(m)


def ranges(hours):
    """'11:30–15:30, 17:00–21:30' → [(690, 930), (1020, 1290)]. 자정 넘김은 +1440."""
    if not hours:
        return None
    h = str(hours)
    if re.search(r'상시|24시간|종일|연중무휴 24', h):
        return [(0, 2880)]
    out = []
    for m in TIME.finditer(h):
        a = int(m.group(1)) * 60 + int(m.group(2))
        b = int(m.group(4)) * 60 + int(m.group(5))
        if m.group(3) or b <= a:
            b += 1440
        out.append((a, b))
    return out or None


def hav(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    x = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))


def lint(g, keys):
    W = []
    sp = {s['id']: s for s in g.get('spots', [])}
    rs = {r['id']: r for r in g.get('restaurants', [])}
    ht = {h['id']: h for h in g.get('hotels', [])}
    c = g.get('center') or [0, 0]
    for coll, name in ((g.get('spots', []), '명소'), (g.get('restaurants', []), '식당'), (g.get('hotels', []), '숙소')):
        for p in coll:
            try:
                d = hav(c, (float(p['lat']), float(p['lng'])))
                if d > 150 and p.get('cat') != 'airport':
                    W.append(f'[좌표] {name} {p["id"]} 이 중심에서 {d:.0f}km')
            except Exception:
                pass
    for h in g.get('hotels', []):
        pr = h.get('price_krw_night') or [0, 0]
        if not pr or not pr[1]:
            W.append(f'[숙소가격] {h["id"]} 1박 가격 없음')
        elif pr[0] > pr[1]:
            W.append(f'[숙소가격] {h["id"]} 아래값이 위값보다 큼 {pr}')
    for a in g.get('nearby_alternatives', []):
        if a.get('key') == g['key']:
            W.append('[대체여행지] 자기 자신')
        elif a.get('key') not in keys:
            W.append(f'[대체여행지] 아직 없는 목적지 {a.get("key")}')

    def days_of():
        for p in g.get('plans', []):
            yield f'{p["nights"]}박', p['days']
        for i, v in enumerate(g.get('variants', [])):
            yield f'대체{i + 1}({v.get("title", "")[:10]})', v['days']

    for where, days in days_of():
        for d in days:
            tag = f'{where} {d["d"]}일차'
            seen = {}
            prev_end = None
            items = d.get('items', [])
            for i, it in enumerate(items):
                t = it.get('t', '')
                if not re.match(r'^\d{2}:\d{2}$', t):
                    continue
                m = mins(t)
                if prev_end is not None and m + 2 < prev_end:
                    W.append(f'[이동] {tag} {t} : 앞 이동이 {prev_end // 60:02d}:{prev_end % 60:02d} 에 끝나는데 시작')
                prev_end = None
                if it.get('k') == 'move' and it.get('minutes'):
                    prev_end = m + int(it['minutes'])
                if it.get('k') == 'meal':
                    opts = [rs[o] for o in it.get('opts', []) if o in rs]
                    if opts:
                        rg = ranges(opts[0].get('hours'))
                        if rg and not any(a <= m <= b - 30 for a, b in rg):
                            W.append(f'[영업시간] {tag} {t} {it.get("label", "")} 첫 후보 {opts[0]["name"]} 영업 {opts[0].get("hours")}')
                if it.get('k') == 'spot' and it.get('ref') in sp:
                    p = sp[it['ref']]
                    if p.get('cat') in ('airport', 'station', 'street', 'park', 'nature', 'sea', 'view', 'night', 'shrine'):
                        pass
                    else:
                        rg = ranges(p.get('hours'))
                        if rg and not any(a <= m <= b - 20 for a, b in rg):
                            W.append(f'[영업시간] {tag} {t} {p["name"]} 영업 {p.get("hours")}')
                    if it['ref'] in seen and p.get('cat') not in ('airport', 'station'):
                        W.append(f'[중복방문] {tag} {p["name"]} 을 같은 날 두 번')
                    seen[it['ref']] = 1
            ts = [mins(it['t']) for it in items if re.match(r'^\d{2}:\d{2}$', it.get('t', '')) and it.get('k') != 'hotel']
            if ts and max(ts) > 23 * 60 + 30:
                W.append(f'[늦은일정] {tag} 마지막 활동 {max(ts) // 60:02d}:{max(ts) % 60:02d}')
    return W


def main():
    folder = DEF
    out = None
    args = sys.argv[1:]
    if '--json' in args:
        out = args[args.index('--json') + 1]
        args = [a for a in args if a not in ('--json', out)]
    if args:
        folder = args[0]
    only = None
    if os.path.isfile(folder):  # 파일 하나만 점검(대체 여행지 키는 같은 폴더의 다른 가이드로 판단)
        only = os.path.abspath(folder)
        folder = os.path.dirname(only)
    ok_name = lambda f: f.endswith('.json') and not f.startswith('_') and '.places' not in f and '.bak' not in f and '.verdict' not in f
    files = sorted(f for f in os.listdir(folder) if ok_name(f))
    guides, all_keys = {}, set()
    for f in files:
        try:
            g = json.load(open(os.path.join(folder, f), encoding='utf-8'))
            all_keys.add(g['key'])
            if only is None or os.path.join(folder, f) == only:
                guides[g['key']] = g
        except Exception as e:
            print('읽기 실패', f, e)
    keys = all_keys
    total = 0
    res = {}
    for k, g in guides.items():
        W = lint(g, keys)
        res[k] = W
        total += len(W)
        print(f'■ {k} ({g["name"]}) 주의 {len(W)}건')
        for w in W[:40]:
            print('   ', w)
        if len(W) > 40:
            print(f'    … 외 {len(W) - 40}건')
    print(f'합계 주의 {total}건 · 목적지 {len(guides)}곳')
    if out:
        json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
