#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""위키미디어 공용(Wikimedia Commons)에서 '사용 허가가 분명한' 실물 사진 후보를 모아 travel/img/ 에 작게 저장하고
   travel/data/photos_candidates.json 에 출처·촬영자·사용 허가를 적는다.

   사용 : python3 travel/tools/fetch_photos.py [목적지key ...] [--per-spot 1] [--spots 3]
   필요 : 인터넷에서 commons.wikimedia.org · upload.wikimedia.org 에 닿아야 한다(클라우드 환경의 네트워크 허용 목록).
          Pillow(WebP 저장)

   고르는 규칙
   - 사용 허가 : 퍼블릭 도메인, CC0, CC BY, CC BY-SA 만(비영리 NC·변경 금지 ND 는 뺀다). 촬영자와 허가 이름을 꼭 남긴다.
   - 사진만(지도·도표·로고·표지판·문서 스캔 제외), 가로 1,200px 이상, 가로 사진 우선.
   - 도시 대표 사진 1장(꼭 볼 곳 중 첫째) + 꼭 볼 곳 사진 몇 장. 검색어는 명소의 일본어 이름과 영어 별칭.
   - 사진은 가로 3:2 로 가운데를 잘라 대표 720×480, 명소 480×320 WebP 로 줄인다(한 장 20~60KB).

   이 스크립트는 '후보'만 만든다. 사람(또는 검수 에이전트)이 사진이 정말 그 장소인지, 예쁜지 보고
   photos_candidates.json 에서 골라 photos.json 으로 옮겨야 앱에 들어간다(build_japan.py 가 photos.json 만 읽는다)."""
import io, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
IMG = os.path.join(ROOT, 'img')
API = 'https://commons.wikimedia.org/w/api.php'
UA = 'MeAI-travel-planner/1.3 (photo credits kept; contact: repository owner)'
OK_LICENSE = re.compile(r'^(cc0|public domain|pd\b|pd-|cc by(-sa)? ?[0-9.]*( [a-z]{2,})?$|cc-by(-sa)?-[0-9.]+)', re.I)
BAD_TITLE = re.compile(r'map|diagram|logo|sign|plan|chart|svg|scan|document|poster|stamp|flag|emblem|seal|coat of arms|地図|案内', re.I)


def api(params):
    q = dict(params, format='json', formatversion='2')
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(q), headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip_html(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(s or ''))).strip()


def search(term, n=12):
    d = api({'action': 'query', 'generator': 'search', 'gsrsearch': term + ' filetype:bitmap', 'gsrnamespace': 6, 'gsrlimit': n,
             'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': 1280})
    out = []
    for p in (d.get('query') or {}).get('pages', []):
        ii = (p.get('imageinfo') or [{}])[0]
        md = ii.get('extmetadata') or {}
        lic = strip_html((md.get('LicenseShortName') or {}).get('value'))
        if ii.get('mime') not in ('image/jpeg', 'image/png', 'image/webp'):
            continue
        if not OK_LICENSE.search(lic) or re.search(r'\bNC\b|\bND\b|non-?commercial|no ?deriv', lic, re.I):
            continue
        if BAD_TITLE.search(p.get('title', '')):
            continue
        w, h = ii.get('width', 0), ii.get('height', 0)
        if w < 1200 or h < 600:
            continue
        out.append({'title': p['title'], 'thumb': ii.get('thumburl'), 'w': w, 'h': h, 'license': lic,
                    'credit': strip_html((md.get('Artist') or {}).get('value')) or strip_html((md.get('Credit') or {}).get('value')),
                    'source': ii.get('descriptionurl'), 'desc': strip_html((md.get('ImageDescription') or {}).get('value'))[:200],
                    'landscape': w >= h * 1.2})
    out.sort(key=lambda x: (not x['landscape'], -min(x['w'], 4000)))
    return out


def save(url, path, size):
    from PIL import Image
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        im = Image.open(io.BytesIO(r.read())).convert('RGB')
    W, H = size
    s = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * s)), max(H, round(im.height * s))), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im.crop((x, y, x + W, y + H)).save(path, 'WEBP', quality=72, method=6)
    return os.path.getsize(path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    n_spots = int(sys.argv[sys.argv.index('--spots') + 1]) if '--spots' in sys.argv else 3
    os.makedirs(IMG, exist_ok=True)
    out_path = os.path.join(DATA, 'photos_candidates.json')
    cand = json.load(open(out_path, encoding='utf-8')) if os.path.exists(out_path) else {'cities': {}, 'spots': {}}
    keys = args or sorted(f[:-5] for f in os.listdir(os.path.join(DATA, 'guides')) if f.endswith('.json'))
    for key in keys:
        g = json.load(open(os.path.join(DATA, 'guides', key + '.json'), encoding='utf-8'))
        en = [a for a in (g.get('profile') or {}).get('aliases', []) if re.match(r'^[A-Za-z]', a)][:1]
        musts = [s for s in g['spots'] if s.get('must') and s.get('cat') not in ('airport', 'station', 'hotel')][:n_spots + 1]
        for i, s in enumerate(musts):
            terms = [s.get('name_ja', ''), (s.get('name_ja', '') + ' ' + (en[0] if en else '')).strip()]
            found = []
            for t in terms:
                if not t:
                    continue
                try:
                    found = search(t)
                except Exception as e:
                    print('  검색 실패', key, t, e)
                    found = []
                if found:
                    break
                time.sleep(0.5)
            if not found:
                print('  후보 없음', key, s['name'])
                continue
            best = found[0]
            group, size = ('cities', (720, 480)) if i == 0 else ('spots', (480, 320))
            fn = 'img/%s_%s.webp' % (key, 'hero' if i == 0 else s['id'])
            try:
                kb = save(best['thumb'], os.path.join(ROOT, fn), size) / 1024
            except Exception as e:
                print('  내려받기 실패', key, s['name'], e)
                continue
            item = {'file': fn, 'spot': s['id'], 'alt': s['name'], 'credit': best['credit'], 'license': best['license'], 'source': best['source'],
                    'commons_title': best['title'], 'desc': best['desc'], 'others': [x['source'] for x in found[1:4]]}
            cand[group].setdefault(key, [x for x in cand[group].get(key, []) if x.get('spot') != s['id']]).append(item)
            print('  %s %s ← %s (%s, %.0fKB)' % (key, s['name'], best['title'], best['license'], kb))
            time.sleep(0.5)
        json.dump(cand, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('후보 저장 :', out_path)


if __name__ == '__main__':
    main()
