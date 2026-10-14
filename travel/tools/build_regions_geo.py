#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""일본 47개 현 경계를 여행 지역 9개로 합쳐, 홈 화면 '지역별 색 지도'용 SVG 경로를 만든다.

   사용 : python3 -I travel/tools/build_regions_geo.py <ne_10m_admin_1_states_provinces.geojson>
   원자료 : Natural Earth 1:10m Admin 1 – States, Provinces (공개 자료, public domain)
            https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_1_states_provinces.geojson
   결과 : travel/data/regions_geo.json  { "regions": { "홋카이도": {"d": SVG 경로, "label": [x, y], "bbox": [x0, y0, x1, y1]}, ... } }
   좌표는 build_japan.py 의 지도 투영(경도 125~146, 위도 30~46, 오키나와는 왼쪽 위 상자)과 같다.
   필요 : shapely (pip install shapely)"""
import json, math, os, sys

from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'data', 'regions_geo.json')

# build_japan.py 와 같은 투영
LON0, LAT1, K, COS = 125.0, 46.0, 20.0, math.cos(math.radians(38))
W, H = round((146 - LON0) * K * COS, 1), round((LAT1 - 30) * K, 1)
INSET = dict(lonMin=122.6, lonMax=128.6, latMax=27.2, latMin=23.8, x=10.0, y=10.0)

# 현 번호(ISO 3166-2:JP) → 여행 지역(가이드의 region 값과 같은 이름)
def region_of(n):
    if n == 1: return '홋카이도'
    if 2 <= n <= 7: return '도호쿠'
    if 8 <= n <= 14: return '간토'
    if 15 <= n <= 23: return '주부'
    if 24 <= n <= 30: return '간사이'
    if 31 <= n <= 35: return '주고쿠'
    if 36 <= n <= 39: return '시코쿠'
    if 40 <= n <= 46: return '규슈'
    if n == 47: return '오키나와'
    return None


def proj(lon, lat, inset):
    if inset:
        return INSET['x'] + (lon - INSET['lonMin']) * K * COS, INSET['y'] + (INSET['latMax'] - lat) * K
    return (lon - LON0) * K * COS, (LAT1 - lat) * K


def polys(geom):
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return []


def ring_path(coords, inset):
    pts = [proj(x, y, inset) for x, y in coords]
    out, last = [], None
    for x, y in pts:
        p = (round(x, 1), round(y, 1))
        if p != last:
            out.append(p)
            last = p
    if len(out) < 4:
        return ''
    return 'M' + ' '.join('%g %g' % p for p in out[:-1]) + 'Z'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    d = json.load(open(sys.argv[1], encoding='utf-8'))
    groups = {}
    for f in d['features']:
        pr = f['properties']
        if pr.get('adm0_a3') != 'JPN':
            continue
        n = int(str(pr.get('iso_3166_2', 'JP-0')).split('-')[1])
        rg = region_of(n)
        if rg:
            groups.setdefault(rg, []).append(shape(f['geometry']).buffer(0))
    out = {}
    for rg, geoms in groups.items():
        u = unary_union(geoms)
        inset = rg == '오키나와'
        keep = []
        for p in polys(u):
            c = p.representative_point()
            if inset and (c.x > INSET['lonMax'] or c.y > INSET['latMax'] + 0.1):   # 다이토 제도 등 오키나와 상자 밖 섬
                continue
            if not inset and (c.x > 141.6 and c.y < 31):      # 오가사와라 등 지도 밖 먼 섬
                continue
            if not inset and c.y < 30.2:                      # 지도 아래쪽 경계 밖
                continue
            if p.area < (0.0006 if inset else 0.004):         # 아주 작은 섬은 뺀다(점으로도 안 보임)
                continue
            keep.append(p.simplify(0.012 if inset else 0.02, preserve_topology=True))
        parts = []
        x0 = y0 = 1e9
        x1 = y1 = -1e9
        for p in keep:
            parts.append(ring_path(list(p.exterior.coords), inset))
            for x, y in p.exterior.coords:
                px, py = proj(x, y, inset)
                x0, y0, x1, y1 = min(x0, px), min(y0, py), max(x1, px), max(y1, py)
        biggest = max(keep, key=lambda p: p.area)
        lp = biggest.representative_point()
        lx, ly = proj(lp.x, lp.y, inset)
        out[rg] = {'d': ''.join(x for x in parts if x), 'label': [round(lx, 1), round(ly, 1)], 'bbox': [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)], 'parts': len(keep)}
    res = {'_source': 'Natural Earth 1:10m Admin 1 (public domain) · 현 경계를 여행 지역 9개로 합침 · build_regions_geo.py', 'w': W, 'h': H, 'regions': out}
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('지역 %d개 · %s · %.1f KB' % (len(out), ', '.join('%s %d조각' % (k, v['parts']) for k, v in out.items()), os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    main()
