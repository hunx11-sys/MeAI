# -*- coding: utf-8 -*-
"""일본 직항 여행 플래너(단일 HTML) 조립.

   travel/template_japan.html  +  travel/data/jp_airports.json(일본 공항·직항 노선)
   + travel/data/kr_airports.json(한국 출발 공항)  +  travel/data/guides/*.json(목적지 가이드, 한국어 원본)
   + travel/data/i18n/<언어>/<목적지>.json(번역 문자열)  +  travel/data/ui_strings.json(화면 글자 6개 언어)
   + travel/data/airport_names.json(공항 이름 언어별)  +  travel/data/outline.json(한국·일본 해안선, Natural Earth 공개 자료)
   + travel/vendor/leaflet.css · leaflet.js(지도 엔진, BSD 라이선스)
   →  travel/japan.html(한국어) · japan_en.html · japan_es.html · japan_zh.html · japan_yue.html · japan_ja.html

   사용 :  python3 travel/build_japan.py              (저장소 루트에서. 언어 6개 전부)
          python3 travel/build_japan.py --lang ko,en  (일부 언어만)
          python3 travel/build_japan.py --strict      (가이드 점검 오류가 하나라도 있으면 중단)
          python3 travel/build_japan.py --lang ko --no-lang-menu   (한국어 미리보기 : 언어 버튼 숨김)
          python3 travel/build_japan.py --lang ko --no-lang-menu --out dist/japan_travel_planner_ko.html   (다운로드용 한 파일)
   가이드 JSON 은 travel/tools/validate_guide.py 로 먼저 점검하고, 오류가 있는 파일은 빼고(경고만 출력) 조립한다.
   그래서 잘못된 자료는 틀린 화면이 아니라 '없는 목적지'로 나타난다.
   번역이 없는 언어의 목적지는 한국어 원문이 그대로 들어간다(조립 요약에 번역 없음으로 표시)."""
import copy, datetime, json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
GUIDES = os.path.join(DATA, 'guides')
I18N = os.path.join(DATA, 'i18n')
VENDOR = os.path.join(HERE, 'vendor')
TPL = os.path.join(HERE, 'template_japan.html')
VALID = os.path.join(HERE, 'tools', 'validate_guide.py')
sys.path.insert(0, os.path.join(HERE, 'tools'))
OUT_ART_DIR = os.environ.get('JAPAN_ARTIFACT_DIR', '')  # 아티팩트(claude.ai)용 본문만 뽑을 폴더. 비어 있으면 안 만든다
VERSION = 'v1.3'

REGIONS = ['홋카이도', '도호쿠', '간토', '주부', '간사이', '주고쿠', '시코쿠', '규슈', '오키나와']
TAGS = ['온천', '미식', '자연', '도시', '쇼핑', '아이동반', '야경', '역사', '바다', '겨울', '벚꽃', '단풍', '테마파크', '드라이브', '섬', '예술', '커피', '애니', '휴양']

# 글꼴 : 전부 오픈 폰트 라이선스(OFL). Pretendard 는 jsDelivr, Noto 는 Google Fonts
FONTS = {
    'pretendard': ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">\n'
                   '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">',
                   "'Pretendard Variable',Pretendard,'Noto Sans KR',-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif"),
    'jp': ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-jp-dynamic-subset.min.css">\n'
           '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">',
           "'Pretendard JP Variable','Pretendard JP','Noto Sans JP',-apple-system,BlinkMacSystemFont,'Hiragino Sans','Yu Gothic',sans-serif"),
    'sc': ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">\n'
           '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">',
           "'Pretendard Variable',Pretendard,'Noto Sans SC',-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif"),
    'tc': ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">\n'
           '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@400;500;700&display=swap" rel="stylesheet">',
           "'Pretendard Variable',Pretendard,'Noto Sans HK','Noto Sans TC',-apple-system,BlinkMacSystemFont,'PingFang HK','Microsoft JhengHei',sans-serif"),
}

# 상세 지도 바탕(타일) 서버 : 위에서부터 시도하고, 그림을 하나도 못 받으면 다음 서버로, 다 안 되면 약도로 바뀐다.
#   지리원 타일(일본 국토지리원 '淡色地図') : 키 없이 공개, 출처 표기 조건. 일본 영역만 그려지므로 일본 여행용에 맞다.
#   OpenStreetMap 표준 타일 : 키 없이 공개(이용 정책상 대량 사용은 별도 서버 권장).
#   CARTO 는 2025년 이후 키 없이 부르면 'API KEY REQUIRED' 그림을 돌려주므로 쓰지 않는다.
#   정식 서비스로 낼 때는 계약한 지도 서버(키 포함) 한 줄을 맨 위에 넣으면 된다.
TILES = [
    {'url': 'https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png', 'attribution': '出典: <a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank" rel="noopener">地理院タイル</a>', 'maxNativeZoom': 18},
    {'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'attribution': '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>', 'maxNativeZoom': 19},
]

# 지도 투영 : 간단한 등장방형(경도에 cos 38° 를 곱해 가로를 줄임). 자바스크립트 proj() 와 같은 식이어야 한다.
LON0, LAT1, K, COS = 125.0, 46.0, 20.0, math.cos(math.radians(38))
W, H = round((146 - LON0) * K * COS, 1), round((LAT1 - 30) * K, 1)
INSET = dict(lonMin=122.6, lonMax=128.6, latMax=27.2, latMin=23.8, x=64.0, y=8.0)   # 왼쪽 위 빈 바다에 둔다
INSET['w'] = round((INSET['lonMax'] - INSET['lonMin']) * K * COS, 1)
INSET['h'] = round((INSET['latMax'] - INSET['latMin']) * K, 1)
LABELS = [  # 지역 이름 자리(지도 좌표). 점과 겹치지 않게 바다 쪽에 둔다
    dict(t='홋카이도', x=292, y=98), dict(t='도호쿠', x=276, y=142), dict(t='간토', x=262, y=212),
    dict(t='주부', x=197, y=154, anchor='middle'), dict(t='간사이', x=168, y=258, anchor='middle'), dict(t='주고쿠', x=118, y=196, anchor='middle'),
    dict(t='시코쿠', x=136, y=276, anchor='middle'), dict(t='규슈', x=60, y=268, anchor='end'),
]


def jsonsafe(obj):
    # '<' 를 전부 \u003c 로 바꿔 <script> 블록을 데이터가 끊지 못하게 한다(JSON 으로는 같은 값)
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')


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
        out.append('M' + 'L'.join('%.1f %.1f' % (x, y) for x, y, _ in pts) + 'Z')
    return ''.join(out)


def validate(path):
    """점검기를 돌려 (통과 여부, 마지막 줄, 전체 출력) 을 돌려준다."""
    r = subprocess.run([sys.executable, '-I', VALID, path], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [''])[-1]
    return r.returncode == 0, last, r.stdout


def apply_translation(obj, tr):
    """i18n.py 의 경로 형식({"spots/0/name": "..."})으로 번역을 끼워 넣은 사본을 돌려준다. 돌려주는 값: (사본, 적용 수)"""
    g = copy.deepcopy(obj)
    n = 0
    for k, v in tr.items():
        if not isinstance(v, str) or not v.strip():
            continue
        parts = k.split('/')
        cur = g
        try:
            for part in parts[:-1]:
                cur = cur[int(part)] if isinstance(cur, list) else cur[part]
            last = parts[-1]
            if isinstance(cur, list):
                cur[int(last)] = v
            else:
                cur[last] = v
            n += 1
        except Exception:
            pass
    return g, n


def load_tr(lang, name):
    p = os.path.join(I18N, lang, name + '.json')
    if lang == 'ko' or not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('  번역 파일 읽기 실패 %s : %s' % (p, e))
        return None


ICON_BAD = re.compile(r'<\s*(script|foreignObject|image|iframe|a)\b|\bon[a-z]+\s*=|href|url\(|javascript:|<text\b', re.I)


REGION_KEYS = {'홋카이도': 'hokkaido', '도호쿠': 'tohoku', '간토': 'kanto', '주부': 'chubu', '간사이': 'kansai', '주고쿠': 'chugoku', '시코쿠': 'shikoku', '규슈': 'kyushu', '오키나와': 'okinawa'}
sys.path.insert(0, os.path.join(HERE, 'tools'))
from dish_category import dish_of  # noqa: E402


def load_svg_set(path, limit):
    """{key: svg} 묶음을 읽어 위험한 요소가 있거나 너무 큰 그림은 빼고 알린다."""
    if not os.path.exists(path):
        return {}
    out = {}
    for k, svg in json.load(open(path, encoding='utf-8')).items():
        if k.startswith('_'):
            continue
        if not isinstance(svg, str) or not svg.lstrip().startswith('<svg') or ICON_BAD.search(svg) or len(svg.encode('utf-8')) > limit:
            print('  그림 제외 %s/%s : 허용되지 않은 요소 또는 %dKB 초과' % (os.path.basename(path), k, limit // 1000))
            continue
        out[k] = svg.strip()
    return out


def load_photos():
    """travel/data/photos.json : 사용 허가가 확인된 실물 사진 목록(없으면 빈 값). 파일은 travel/img/ 아래.
       {"cities": {"kyoto": [{"file": "img/kyoto_1.webp", "credit": "촬영자", "license": "CC BY-SA 4.0", "source": "원본 주소"}]}, "spots": {...}}
       조립 때 data: 주소로 파일 안에 넣는다(한 파일로 열리게). 파일이 없으면 그 사진은 건너뛴다."""
    path = os.path.join(DATA, 'photos.json')
    if not os.path.exists(path):
        return {}
    import base64
    man = json.load(open(path, encoding='utf-8'))
    out = {}
    for group in ('cities', 'spots', 'regions', 'dishes'):
        for key, items in (man.get(group) or {}).items():
            for it in items:
                fp = os.path.join(HERE, it.get('file', ''))
                if not it.get('license') or not it.get('source') or not os.path.isfile(fp):
                    continue
                mime = 'image/webp' if fp.endswith('.webp') else 'image/jpeg'
                src = 'data:%s;base64,%s' % (mime, base64.b64encode(open(fp, 'rb').read()).decode('ascii'))
                out.setdefault(group, {}).setdefault(key, []).append({'src': src, 'credit': it.get('credit', ''), 'license': it['license'], 'source': it['source'], 'alt': it.get('alt', '')})
    return out


def local_name(g, code):
    """번역이 아직 없는 가이드의 이름 : 일본어·중국어판은 일본어 표기, 영어·스페인어판은 로마자 별칭(앞 2개)."""
    if code in ('ja', 'zh', 'yue'):
        return g.get('name_ja') or g['name']
    lat = []
    for a in (g.get('profile') or {}).get('aliases', []):
        if re.match(r'^[A-Za-z]', a):
            lat.append(a)
        else:
            break
    return ' · '.join(lat[:2]) or g['name']


def load_icons():
    """travel/data/icons.json : 목적지별 그림(SVG). 위험한 요소가 있거나 너무 크면 빼고 알린다."""
    path = os.path.join(DATA, 'icons.json')
    if not os.path.exists(path):
        return {}
    icons = json.load(open(path, encoding='utf-8'))
    out = {}
    for k, svg in icons.items():
        if k.startswith('_'):
            continue
        if not isinstance(svg, str) or not svg.lstrip().startswith('<svg') or ICON_BAD.search(svg) or len(svg.encode('utf-8')) > 4000:
            print('  그림 제외 %s : 허용되지 않은 요소 또는 4KB 초과' % k)
            continue
        out[k] = svg.strip()
    return out


def main():
    strict = '--strict' in sys.argv
    hide_lang = '--no-lang-menu' in sys.argv  # 미리보기용 : 언어 버튼 숨김
    out_dir, out_name = HERE, None
    for i, a in enumerate(sys.argv):
        if a == '--out' and i + 1 < len(sys.argv):  # 한 언어만 다른 경로·이름으로 내보낼 때 (예: --lang ko --out dist/x.html)
            out_dir, out_name = os.path.split(os.path.abspath(sys.argv[i + 1]))
    want = None
    for i, a in enumerate(sys.argv):
        if a == '--lang' and i + 1 < len(sys.argv):
            want = sys.argv[i + 1].split(',')
    ui_all = json.load(open(os.path.join(DATA, 'ui_strings.json'), encoding='utf-8'))
    langs = [l for l in ui_all['langs'] if not want or l['code'] in want]
    kr = json.load(open(os.path.join(DATA, 'kr_airports.json'), encoding='utf-8'))
    apn = json.load(open(os.path.join(DATA, 'airport_names.json'), encoding='utf-8'))
    apn.pop('_note', None)
    ap_path = os.path.join(DATA, 'jp_airports.json')
    airports = json.load(open(ap_path, encoding='utf-8')) if os.path.exists(ap_path) else {'airports': []}
    aps = airports['airports'] if isinstance(airports, dict) else airports
    outline = json.load(open(os.path.join(DATA, 'outline.json'), encoding='utf-8'))
    generated = airports.get('generated', datetime.date.today().isoformat()) if isinstance(airports, dict) else datetime.date.today().isoformat()

    # 가이드(한국어 원본) 읽기 + 점검
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
        guides[g['key']] = g

    def order_key(g):
        return (REGIONS.index(g['region']) if g['region'] in REGIONS else 99, -float(g['center'][0]))
    for i, g in enumerate(sorted(guides.values(), key=order_key)):
        g['order'] = i
    icons = load_icons()
    for key, g in guides.items():
        if key in icons:
            g['icon'] = icons[key]
    for g in guides.values():
        for r in g.get('restaurants', []):
            r['dish'] = dish_of(r.get('cuisine'), r.get('name'))
    art = {'regions': load_svg_set(os.path.join(DATA, 'art_regions.json'), 8000), 'dishes': load_svg_set(os.path.join(DATA, 'art_dishes.json'), 4000)}
    photos = load_photos()
    regions_geo = json.load(open(os.path.join(DATA, 'regions_geo.json'), encoding='utf-8'))['regions'] if os.path.exists(os.path.join(DATA, 'regions_geo.json')) else {}
    no_icon = [k for k in guides if k not in icons]
    no_prof = [k for k, g in guides.items() if not g.get('profile')]

    mapd = {
        'w': W, 'h': H, 'lon0': LON0, 'lat1': LAT1, 'k': K, 'cos': round(COS, 5), 'inset': INSET, 'labels': LABELS,
        'paths': {'japan': rings_to_path(outline['japan'], False), 'okinawa': rings_to_path(outline['japan'], True), 'korea': rings_to_path(outline['korea'], False)},
        'regions': {k: {'d': v['d'], 'label': v['label'], 'bbox': v['bbox']} for k, v in regions_geo.items()},
    }
    tpl = open(TPL, encoding='utf-8').read()
    css = open(os.path.join(VENDOR, 'leaflet.css'), encoding='utf-8').read()
    js = open(os.path.join(VENDOR, 'leaflet.js'), encoding='utf-8').read().replace('</script', '<\\/script')
    lang_links = {}
    if OUT_ART_DIR:
        links_path = os.path.join(OUT_ART_DIR, 'links.json')
        if os.path.exists(links_path):
            lang_links = json.load(open(links_path, encoding='utf-8'))

    summary = []
    for L in langs:
        code = L['code']
        ui = ui_all.get(code, ui_all['ko'])
        # 가이드 번역 적용
        tguides, missing = {}, []
        for key, g in guides.items():
            tr = load_tr(code, key)
            if tr is None:
                tguides[key] = dict(g, _ko_only=(code != 'ko'))
                if code != 'ko':
                    tguides[key]['name'] = local_name(g, code)
                if code != 'ko':
                    missing.append(key)
            else:
                tguides[key], _ = apply_translation(g, tr)
        # 공항 자료 번역(주 운항 횟수·메모·시내 교통)
        taps = aps
        tr = load_tr(code, '_airports')
        if tr is not None:
            taps, _ = apply_translation({'airports': aps}, tr)
            taps = taps['airports']
        data = {
            'version': VERSION, 'generated': generated, 'lang': code, 'hideLang': hide_lang, 'ui': ui, 'langs': ui_all['langs'], 'langLinks': lang_links,
            'regions': REGIONS, 'tags': TAGS, 'tiles': TILES, 'kr': kr, 'apnames': apn, 'airports': taps, 'guides': tguides, 'map': mapd, 'art': art, 'photos': photos, 'regionKeys': REGION_KEYS,
        }
        fonts_link, stack = FONTS.get(L.get('font', 'pretendard'), FONTS['pretendard'])
        html = (tpl.replace('/*LANG*/', L.get('html', code)).replace('/*TITLE*/', ui.get('brand', '일본 직항 여행 플래너'))
                .replace('<!--FONTS-->', fonts_link).replace('/*FONT_STACK*/', stack)
                .replace('/*LEAFLET_CSS*/', css).replace('/*LEAFLET_JS*/', js).replace('/*DATA*/', jsonsafe(data)))
        out = os.path.join(out_dir, out_name or L['file'])
        os.makedirs(out_dir, exist_ok=True)
        open(out, 'w', encoding='utf-8').write(html)
        if OUT_ART_DIR:
            os.makedirs(OUT_ART_DIR, exist_ok=True)
            inner = html.split('<title>', 1)[1]
            inner = '<title>' + inner.split('</body>', 1)[0].replace('</head>\n<body>', '')
            # 아티팩트 화면은 Google Fonts 말고 외부 글꼴 파일을 막으므로 jsDelivr(Pretendard) 줄을 뺀다(Noto Sans 로 표시)
            inner = '\n'.join(l for l in inner.split('\n') if 'cdn.jsdelivr.net/gh/orioncactus/pretendard' not in l)
            open(os.path.join(OUT_ART_DIR, L['file']), 'w', encoding='utf-8').write(inner)
        summary.append((code, L['file'], os.path.getsize(out) / 1048576, missing))

    nroutes = sum(len(a.get('routes', [])) for a in aps)
    print('조립 완료 · 일본 공항 %d개 · 직항 노선 %d건 · 목적지 가이드 %d곳%s' % (len(aps), nroutes, len(guides), (' · 건너뜀 %d' % len(skipped)) if skipped else ''))
    print('  도시 그림 %d/%d · 도시 프로필 %d/%d%s' % (len(guides) - len(no_icon), len(guides), len(guides) - len(no_prof), len(guides), ('  (그림 없음: %s)' % ','.join(no_icon[:8])) if no_icon else ''))
    print('  지역 장면 그림 %d/9 · 음식 그림 %d종 · 실물 사진 %d장 · 지역 색 지도 %d/9' % (len(art['regions']), len(art['dishes']), sum(len(v) for grp in photos.values() for v in grp.values()), len(regions_geo)))
    for code, f, mb, missing in summary:
        print('  %-4s %-16s %.1f MB%s' % (code, f, mb, ('  번역 없음 %d곳: %s' % (len(missing), ','.join(missing[:6]) + ('…' if len(missing) > 6 else ''))) if missing else ''))
    for key, g in sorted(guides.items(), key=lambda kv: kv[1]['order']):
        print('    %-16s %-14s 명소 %2d · 식당 %2d · 숙소 %d · 플랜 %s · 대체동선 %d · 해시태그 %d' % (
            key, g['name'], len(g['spots']), len(g['restaurants']), len(g['hotels']),
            '/'.join('%d박' % p['nights'] for p in g['plans']), len(g['variants']), len(g.get('highlights', []))))


if __name__ == '__main__':
    main()
