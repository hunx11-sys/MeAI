#!/usr/bin/env python3
"""
다른 Claude 대화에서 그대로 쓸 수 있는 반출 파일 만들기
- 저장소 루트에서 실행: python3 scripts/build_export.py
- 결과: export/메리츠_상품보상데이터.json  (데이터)
        export/메리츠_보상메커니즘.md      (읽는 법·판정 규칙)

약관 본문(13MB)은 빼고, 상품·특약·분류표 코드·동의어만 담는다.
본문이 필요하면 tool.html 의 DATA 블록을 직접 쓰면 된다.
"""
import base64, datetime, json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, 'export')
JSON_OUT = os.path.join(OUTDIR, '메리츠_상품보상데이터.json')


def load(path, sid='DATA'):
    s = open(os.path.join(ROOT, path), encoding='utf-8').read()
    return json.loads(re.search(
        rf'<script id="{sid}" type="application/json">(.*?)</script>', s, re.S).group(1))


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    D = load('tool.html')
    P = load('products.html')

    # 특약 : 약관 본문(b)만 뺀다
    riders = [{k: v for k, v in r.items() if k != 'b'} for r in D['riders']]
    # 분류표 : 원문 대신 행(질병명+코드)만
    tables = {k: {'name': t.get('name'), 'page': t.get('page'), 'rows': t.get('rows') or []}
              for k, t in D['tables'].items()}

    out = {
        '_about': {
            '무엇인가': '메리츠화재 장기인보험 상품·특약·질병코드 데이터 (영업지원도구에서 반출)',
            '같이 보는 문서': '메리츠_보상메커니즘.md — 이 데이터를 어떻게 읽고 판정하는지',
            '기준 약관': '통합간편 2607(세만기형·통합간편심사형) · 케어프리 M-Basket 2607 · 운전자 2608 · 치아 2601',
            '데이터 판': D['meta'].get('version'),
            '만든 날짜': datetime.date.today().isoformat(),
            '뺀 것': '약관 본문 전문(13MB). 코드 판정에는 필요 없어 제외했다.',
            '주의': '보장 여부·지급금액의 최종 판단은 약관 원문이다. 이 데이터는 설계·상담 보조용이다.',
        },
        'meta': D['meta'],
        'stages': [
            {'key': 'diagnosis', 'label': '진단 시'}, {'key': 'test', 'label': '검사 시'},
            {'key': 'surgery', 'label': '수술 시'}, {'key': 'hospital', 'label': '입원 시'},
            {'key': 'outpatient', 'label': '통원 시'}, {'key': 'treatment', 'label': '치료 시'},
            {'key': 'care', 'label': '간병·요양 시'}, {'key': 'disability', 'label': '후유장해 시'},
            {'key': 'death', 'label': '사망 시'}, {'key': 'etc', 'label': '기타 보장'},
        ],
        'categories': D['categories'],
        'products': P.get('products', []),
        'duty_types': P.get('dtypes', []),
        'std_rules': P.get('std', []),
        'riders': riders,
        'tables': tables,
        'codenames': D['codenames'],
        'synonyms': D['synonyms'],
        'aliases': D.get('aliases', {}),
        'chips': D.get('chips', []),
    }
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    n = os.path.getsize(JSON_OUT)
    print(f'-> export/{os.path.basename(JSON_OUT)}  {n/1024/1024:.1f} MB')
    print(f'   상품 {len(out["products"])} · 특약 {len(riders)} · 분류표 {len(tables)} '
          f'· 코드명 {len(out["codenames"])} · 동의어 {len(out["synonyms"])} · 별칭 {len(out["aliases"])}')
    return out


if __name__ == '__main__':
    main()
