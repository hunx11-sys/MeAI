# -*- coding: utf-8 -*-
"""일본 직항 여행 플래너(단일 HTML) 조립.

   travel/template_japan.html  +  travel/data/jp_airports.json(일본 공항·직항 노선)
   + travel/data/kr_airports.json(한국 출발 공항)  +  travel/data/guides/*.json(목적지 가이드)
   + travel/data/outline.json(한국·일본 해안선, Natural Earth 공개 자료)
   + travel/vendor/leaflet.css · leaflet.js(지도 엔진, BSD 라이선스)
   →  travel/japan.html

   사용 :  python3 travel/build_japan.py            (저장소 루트에서)
          python3 travel/build_japan.py --strict   (가이드 점검 오류가 하나라도 있으면 중단)
   가이드 JSON 은 travel/tools/validate_guide.py 로 먼저 점검하고, 오류가 있는 파일은 빼고(경고만 출력) 조립한다.
   그래서 잘못된 자료는 틀린 화면이 아니라 '없는 목적지'로 나타난다."""
import datetime, io, json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
GUIDES = os.path.join(DATA, 'guides')
VENDOR = os.path.join(HERE, 'vendor')
TPL = os.path.join(HERE, 'template_japan.html')
OUT = os.path.join(HERE, 'japan.html')
OUT_ART = os.environ.get('JAPAN_ARTIFACT_OUT', '')  # 아티팩트(claude.ai)용 본문만 뽑을 경로. 비어 있으면 안 만든다
VALID = os.path.join(HERE, 'tools', 'validate_guide.py')
VERSION = 'v1.0'

REGIONS = ['홋카이도', '도호쿠', '간토', '주부', '간사이', '주고쿠', '시코쿠', '규슈', '오키나와']
TAGS = ['온천', '미식', '자연', '도시', '쇼핑', '아이동반', '야경', '역사', '바다', '겨울', '벚꽃', '단풍', '테마파크', '드라이브', '섬', '예술', '커피', '애니', '휴양']

# 지도 투영 : 간단한 등장방형(경도에 cos 38° 를 곱해 가로를 줄임). 자바스크립트 proj() 와 같은 식이어야 한다.
LON0, LAT1, K, COS = 125.0, 46.0, 20.0, math.cos(math.radians(38))
W, H = round((146 - LON0) * K * COS, 1), round((LAT1 - 30) * K, 1)
INSET = dict(lonMin=122.6, lonMax=128.6, latMax=27.2, latMin=23.8, x=10.0, y=10.0)   # 왼쪽 위 빈 바다에 둔다
INSET['w'] = round((INSET['lonMax'] - INSET['lonMin']) * K * COS, 1)
INSET['h'] = round((INSET['latMax'] - INSET['latMin']) * K, 1)
LABELS = [  # 지역 이름 자리(지도 좌표). 점과 겹치지 않게 바다 쪽에 둔다
    dict(t='홋카이도', x=292, y=98), dict(t='도호쿠', x=276, y=142), dict(t='간토', x=262, y=212),
    dict(t='주부', x=197, y=154, anchor='middle'), dict(t='간사이', x=168, y=258, anchor='middle'), dict(t='주고쿠', x=118, y=196, anchor='middle'),
    dict(t='시코쿠', x=136, y=276, anchor='middle'), dict(t='규슈', x=60, y=268, anchor='end'),
]


def jsonsafe(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def project(lon, lat):
    if lat < INSET['latMax'] and INSET['lonMin'] <= lon <= INSET['lonMax']:
        return INSET['x'] + (lon - INSET['lonMin']) * K * COS, INSET['y'] + (INSET['latMax'] - lat) * K, True
    return (lon - LON0) * K * COS, (LAT1 - lat) * K, False


def rings_to_path(rings, want_inset):
    out = []
    for r in rings:
        lats = [p[1] for p in r]
        is_inset = max(lats) < 28
        if is_inset != want_inset:
            continue
        pts = [project(p[0], p[1]) for p in r]
        if want_inset and not all(p[2] for p in pts):
            continue
        d = 'M' + 'L'.join('%.1f %.1f' % (x, y) for x, y, _ in pts) + 'Z'
        out.append(d)
    return ''.join(out)


def validate(path):
    """점검기를 돌려 (통과 여부, 마지막 줄) 을 돌려준다."""
    r = subprocess.run([sys.executable, '-I', VALID, path], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [''])[-1]
    return r.returncode == 0, last, r.stdout


def main():
    strict = '--strict' in sys.argv
    kr = json.load(open(os.path.join(DATA, 'kr_airports.json'), encoding='utf-8'))
    ap_path = os.path.join(DATA, 'jp_airports.json')
    airports = json.load(open(ap_path, encoding='utf-8')) if os.path.exists(ap_path) else {'airports': []}
    aps = airports['airports'] if isinstance(airports, dict) else airports
    outline = json.load(open(os.path.join(DATA, 'outline.json'), encoding='utf-8'))

    guides, skipped = {}, []
    for f in sorted(os.listdir(GUIDES)) if os.path.isdir(GUIDES) else []:
        if not f.endswith('.json') or f.startswith('_'):
            continue
        p = os.path.join(GUIDES, f)
        ok, last, full = validate(p)
        if not ok:
            skipped.append((f, last))
            print('  건너뜀 %s : %s' % (f, last))
            if strict:
                print(full)
                sys.exit(1)
            continue
        g = json.load(open(p, encoding='utf-8'))
        g['order'] = len(guides)
        guides[g['key']] = g

    # 목적지가 있는 지역 순서로 정렬(홋카이도 → 오키나와, 같은 지역은 위도 높은 순)
    def order_key(g):
        return (REGIONS.index(g['region']) if g['region'] in REGIONS else 99, -float(g['center'][0]))
    for i, g in enumerate(sorted(guides.values(), key=order_key)):
        g['order'] = i

    data = {
        'version': VERSION,
        'generated': airports.get('generated', datetime.date.today().isoformat()) if isinstance(airports, dict) else datetime.date.today().isoformat(),
        'regions': REGIONS, 'tags': TAGS,
        'kr': kr, 'airports': aps, 'guides': guides,
        'map': {
            'w': W, 'h': H, 'lon0': LON0, 'lat1': LAT1, 'k': K, 'cos': round(COS, 5),
            'inset': INSET, 'labels': LABELS,
            'paths': {
                'japan': rings_to_path(outline['japan'], False),
                'okinawa': rings_to_path(outline['japan'], True),
                'korea': rings_to_path(outline['korea'], False),
            },
        },
    }
    tpl = open(TPL, encoding='utf-8').read()
    css = open(os.path.join(VENDOR, 'leaflet.css'), encoding='utf-8').read()
    js = open(os.path.join(VENDOR, 'leaflet.js'), encoding='utf-8').read().replace('</script', '<\\/script')
    html = tpl.replace('/*LEAFLET_CSS*/', css).replace('/*LEAFLET_JS*/', js).replace('/*DATA*/', jsonsafe(data))
    open(OUT, 'w', encoding='utf-8').write(html)
    if OUT_ART:
        # 아티팩트는 문서 머리말을 자기가 붙이므로 <title> 부터 </body> 앞까지만 준다
        inner = html.split('<title>', 1)[1]
        inner = '<title>' + inner.split('</body>', 1)[0].replace('</head>\n<body>', '')
        open(OUT_ART, 'w', encoding='utf-8').write(inner)
        print('아티팩트용 → %s' % OUT_ART)
    nroutes = sum(len(a.get('routes', [])) for a in aps)
    print('조립 완료 → %s (%.1f MB)' % (os.path.relpath(OUT), os.path.getsize(OUT) / 1048576))
    print('  일본 공항 %d개 · 직항 노선 %d건 · 목적지 가이드 %d곳%s' % (len(aps), nroutes, len(guides), (' · 건너뜀 %d' % len(skipped)) if skipped else ''))
    for key, g in sorted(guides.items(), key=lambda kv: kv[1]['order']):
        print('    %-16s %-14s 명소 %2d · 식당 %2d · 숙소 %d · 플랜 %s · 대체동선 %d' % (
            key, g['name'], len(g['spots']), len(g['restaurants']), len(g['hotels']),
            '/'.join('%d박' % p['nights'] for p in g['plans']), len(g['variants'])))


if __name__ == '__main__':
    main()
