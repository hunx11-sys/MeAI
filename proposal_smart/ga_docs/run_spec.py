# -*- coding: utf-8 -*-
"""저장소 ga_proposal(현재 버전)로 설계서별 GA 지면 HTML 을 만들고, 저장소 ga_spec 으로 칸 스펙 결과 json 을 뽑는다.
  python3 run_spec.py <out.json> <html폴더> <설계서.pdf ...>
결과 json 구조는 ga_spec.py __main__ 과 같다(build_ga_xlsx · build_ga_visual · build_ga_blueprint · viewer 가 그대로 읽는다)."""
import os, sys, os, json, time
PS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, PS); os.chdir(PS)
import ga_proposal as G, ga_spec as GS, pipeline, scen_engine as S

out, hdir, pdfs = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(hdir, exist_ok=True)
uni = GS.universe()
uni = GS.add_design_only(uni, [pipeline.read_riders(p) for p in pdfs])
res = dict(version=S.RULEDOC.get('_note', ''), cells=GS.spec_dump(), universe_n=len(uni), universe=GS.run_universe(uni),
           universe_riders=[dict(db_id=r['db_id'], name=r['name'], product=r.get('product'), man=r['man'], cat=r.get('cat'), ncodes=len(r['codes']), nexcl=len(r['excl']), nhc=len(r['hc']),
                                 benefit=r.get('benefit'), sub=r.get('sub'), itc=r.get('itc'), via=r.get('via'), matched=r.get('matched')) for r in uni], designs=[])
for p in pdfs:
    t0 = time.time()
    base = os.path.splitext(os.path.basename(p))[0]
    hp = os.path.join(hdir, base + '-ga.html')
    h = G.html(p); open(hp, 'w', encoding='utf-8').write(h)
    d = GS.run_design(p, hp); d['pdf'] = os.path.basename(p); d['html'] = hp
    c = d['cmp'] or {}
    print(os.path.basename(p), 'riders', d['nriders'], 'cmp', c.get('equal'), c.get('html_n'), c.get('spec_n'), 'diffs', len(c.get('diffs') or []), '%.0fs' % (time.time() - t0), flush=True)
    res['designs'].append(d)
json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print('saved', out, 'designs', len(res['designs']), 'cells', len(res['cells']))
