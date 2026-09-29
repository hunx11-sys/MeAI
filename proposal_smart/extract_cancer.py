# -*- coding: utf-8 -*-
"""특약검색기(tool.html) 내장 약관 원문 → 암 분류표 재생성·검증 (v8.8)

    python extract_cancer.py ../tool.html          # 검증만
    python extract_cancer.py ../tool.html --write  # rules.json 의 암 그룹까지 갱신

① 통합암 그룹 10종(특정소액암·특정소화기암·15대/14대특정암·10대특정암·4대고액암, 원발/전이포함)
   → tool.html 의 구조화 데이터({"label","codes","g"})에서 그대로 추출 → rules.json kcd_groups
② 암종별(13종) 분류표(cancer13.json) → 약관 원문 텍스트와 대조해 검증만 수행
   (구분 셀이 표 중간에 걸쳐 인쇄되어 자동 분할이 불가능하므로 표는 파일로 관리하고 코드 누락·중복만 점검)
"""
import collections, json, io, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CANCER = ['특정소액암', '특정소화기암', '15대특정암', '10대특정암', '4대고액암',
          '특정소액암(전이포함)', '특정소화기암(전이포함)', '14대특정암(전이포함)',
          '10대특정암(전이포함)', '4대고액암(전이포함)']
ITEM = re.compile(r'\{"label":"([^"]{1,160})","codes":\[([^\]]{0,300})\],"g":"([^"]{1,40})"\}')


def groups_from_tool(path):
    t = io.open(path, encoding='utf-8', errors='replace').read()
    g = collections.OrderedDict()
    for m in ITEM.finditer(t):
        cs = tuple(c.strip().strip('"') for c in m.group(2).split(',') if c.strip())
        g.setdefault(m.group(3), collections.OrderedDict())[(m.group(1), cs)] = 1
    out = collections.OrderedDict()
    for k, v in g.items():
        seen = collections.OrderedDict()
        for (_, cs) in v:
            for c in cs: seen[c] = 1
        out[k] = list(seen)
    return out, t


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    src = sys.argv[1]
    got, raw = groups_from_tool(src)
    print('추출한 그룹 %d종' % len(got))
    miss = [k for k in CANCER if k not in got]
    for k in CANCER:
        if k in got: print('  %-18s %2d개' % (k, len(got[k])))
    if miss: print('  [경고] 추출 실패:', miss)

    # 암종별(13종) 표 검증
    p13 = os.path.join(BASE, 'cancer13.json')
    if os.path.exists(p13):
        c13 = json.load(open(p13, encoding='utf-8'))['groups']
        flat = [c for cs in c13.values() for c in cs]
        dup = [c for c, n in collections.Counter(flat).items() if n > 1]
        i = raw.find('암종별(13종)통합암')
        txt = re.sub(r'\s', '', raw[i:i + 9000]) if i >= 0 else ''
        nf = [c for c in set(flat) if txt and c not in txt]
        db = json.load(open(os.path.join(BASE, 'db.json'), encoding='utf-8'))
        par = next((r for r in db['riders'] if r['n'].startswith('26종 항암방사선및약물치료비 (전이포함)')), None)
        print('\n암종별(13종) 표 : 구분 %d개 · 코드 %d개(중복 제외 %d개)'
              % (len(c13), len(flat), len(set(flat))))
        print('  약관 원문에 없는 코드 :', nf or '없음')
        print('  두 구분에 겹치는 코드 :', dup or '없음', '(C79.81 은 약관상 남·여 생식기관 양쪽 표기)')
        if par:
            a, b = set(flat), set(par['k'])
            print('  특약 마스터 26종 담보 코드와 대조 : 표에만 %s · 마스터에만 %s'
                  % (sorted(a - b) or '없음', sorted(b - a) or '없음'))

    if '--write' in sys.argv:
        p = os.path.join(BASE, 'rules.json')
        doc = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        for k in CANCER:
            if k in got: doc['kcd_groups'][k] = got[k]
        json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\nrules.json 갱신 완료')
    else:
        print('\n(검증만 수행 — 반영하려면 --write)')


if __name__ == '__main__':
    main()
