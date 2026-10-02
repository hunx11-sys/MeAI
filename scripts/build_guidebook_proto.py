# -*- coding: utf-8 -*-
"""가이드북 생성기(오프라인 단일 HTML) 조립.
   scripts/guidebook_proto_template.html + pdf.js + 특약 마스터(db.json·db_terms_extra.json) + 질병코드 이름
   + Key Point 창고(scripts/guidebook_kp.json) + 내장 샘플 2건 → docs/guidebook_proto.html

   사용 : python scripts/build_guidebook_proto.py <pdfjs-dist 압축 푼 폴더>
          (pdfjs-dist 는 npm pack pdfjs-dist@4.10.38 로 받는다. build/pdf.min.mjs · build/pdf.worker.min.mjs · cmaps/ 를 쓴다)
   pdf.js 폴더를 주지 않으면 docs/guidebook_proto.html 안에 들어 있던 것을 다시 쓴다(글 상자·마스터만 바꿀 때)."""
import base64, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PS = os.path.join(ROOT, 'proposal_smart')
OUT = os.path.join(ROOT, 'docs', 'guidebook_proto.html')
TPL = os.path.join(ROOT, 'scripts', 'guidebook_proto_template.html')


def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode('ascii')


def jsonsafe(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def main():
    pdfjs_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if pdfjs_dir:
        main_b64 = b64(os.path.join(pdfjs_dir, 'build', 'pdf.min.mjs'))
        worker_b64 = b64(os.path.join(pdfjs_dir, 'build', 'pdf.worker.min.mjs'))
        cm_dir = os.path.join(pdfjs_dir, 'cmaps')
        cmaps = {f[:-6]: b64(os.path.join(cm_dir, f)) for f in sorted(os.listdir(cm_dir))
                 if f.endswith('.bcmap') and re.match(r'^(KSC|UniKS|Adobe-Korea)', f)}
    else:
        old = open(OUT, encoding='utf-8').read()
        g = lambda i: re.search(r'<script type="text/plain" id="%s">([^<]*)</script>' % i, old).group(1)
        main_b64, worker_b64 = g('pdfjs-main'), g('pdfjs-worker')
        cmaps = json.loads(re.search(r'<script type="application/json" id="cmaps">(.*?)</script>', old, re.S).group(1))

    db = json.load(open(os.path.join(PS, 'db.json'), encoding='utf-8'))
    ex = json.load(open(os.path.join(PS, 'db_terms_extra.json'), encoding='utf-8'))
    rules = json.load(open(os.path.join(PS, 'rules.json'), encoding='utf-8'))
    riders = [{'n': r['n'], 'p': r['p'], 'c': r.get('c'), 'k': r.get('k') or [], 'x': r.get('x') or []}
              for r in db['riders'] + ex['riders']]
    master = {'products': db['meta']['products'] + ex['meta']['products'], 'goji_tags': rules['goji_tags'], 'riders': riders}
    kcd = json.load(open(os.path.join(PS, 'kcdnames.json'), encoding='utf-8'))
    kp = json.load(open(os.path.join(ROOT, 'scripts', 'guidebook_kp.json'), encoding='utf-8'))

    samples = []
    for f, age, sex in (('cust_a.json', '40', '남'), ('cust_b.json', '40', '여')):
        c = json.load(open(os.path.join(PS, f), encoding='utf-8'))
        samples.append({'src': c.get('src', f), 'insured': c['insured'], 'premium': c['premium'], 'product': c['product'],
                        'head': c['head'], 'age': age, 'sex': sex,
                        'riders': [{'no': r['no'], 'name': r['name'], 'man': r['man']} for r in c['riders']]})

    today = datetime.date.today()
    meta = {'built': today.isoformat(), 'ym': '%d년 %d월' % (today.year, today.month),
            'products': master['products'], 'riders': len(riders), 'kp': len(kp['kp'])}

    icons = json.load(open(os.path.join(PS, 'icons.json'), encoding='utf-8'))          # Healthicons SVG 71개 — 아이콘 타일
    font_b64 = b64(os.path.join(ROOT, 'assets', 'pretendard-subset.woff2'))                 # Pretendard 부분집합(한글 2,351자) — 없는 글자는 맑은 고딕으로
    html = open(TPL, encoding='utf-8').read()
    for k, v in (('__ICONS__', jsonsafe(icons)), ('__FONT_B64__', font_b64)):              # 틀에 자리가 있을 때만 넣는다
        html = html.replace(k, v)
    for k, v in (('__PDFJS_MAIN__', main_b64), ('__PDFJS_WORKER__', worker_b64), ('__CMAPS__', jsonsafe(cmaps)),
                 ('__MASTER__', jsonsafe(master)), ('__KCDNAMES__', jsonsafe(kcd)), ('__KP__', jsonsafe(kp)),
                 ('__SAMPLES__', jsonsafe(samples)), ('__BUILDMETA__', jsonsafe(meta))):
        assert k in html, k
        html = html.replace(k, v)
    open(OUT, 'w', encoding='utf-8').write(html)
    print('완료 :', OUT, '%.1f MB' % (os.path.getsize(OUT) / 1e6), '· 특약', len(riders), '· Key Point', len(kp['kp']), '· cmap', len(cmaps))


if __name__ == '__main__':
    main()
