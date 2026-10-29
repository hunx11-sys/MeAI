# -*- coding: utf-8 -*-
"""파이썬 사주 엔진(ref/saju_engine.py · 엑셀과 같은 규칙)과 화면의 자바스크립트 엔진이
1936-01-01 ~ 2046-12-31 (40,543일) 전 기간에서 같은 결과를 내는지 검사한다.

비교 항목 : 년주 · 월주 · 일주 · 절입일 이름 · 대운수(남/여) · 순역행 · 총점 · 분야 점수 4개 · 한 줄 문구 · 대화 팁 · 띠 문장

자바스크립트 쪽 파일 (먼저 찾은 것)
  1) 웹서버판  web/js/fortune-text.js + web/js/saju-engine.js   (패키지 안에서 돌릴 때)
  2) 원본      fortune/src/engine.js                              (저장소에서 돌릴 때)

실행 : python verify_saju.py [js 폴더 또는 engine.js]
  · node 가 있으면 브라우저 없이 node 로 돌린다
  · 없으면 playwright(파이썬) + 엣지/크롬으로 돌린다  (pip install playwright)
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'ref'))
from saju_engine import pillars, fortune, daeun  # noqa: E402

START, END, TODAY = dt.date(1936, 1, 1), dt.date(2046, 12, 31), (2026, 10, 16)
RUN = """([y0,m0,d0,n,ty,tm,td]) => { const S = NZ_SAJU, out = []; const base = Date.UTC(y0, m0 - 1, d0);
  for (let k = 0; k < n; k++) { const t = new Date(base + k * 864e5), y = t.getUTCFullYear(), m = t.getUTCMonth() + 1, d = t.getUTCDate();
    const p = S.pillars(y, m, d), dm = S.daeun(p, true), df = S.daeun(p, false), f = S.fortune(y, m, d, k % 2 === 0, ty, tm, td);
    out.push([p.ys, p.yb, p.ms, p.mb, p.di, p.jieToday ? p.jieToday.name : '', dm.n, dm.fwd ? 1 : 0, df.n, f.total, f.scores.join(','), f.head, f.tip, f.ttiLine]); }
  return out; }"""


def js_source(arg):
    cands = [arg] if arg else [os.path.join(HERE, '..', 'web', 'js'), os.path.join(HERE, '..', 'src', 'engine.js')]
    for c in cands:
        if c and os.path.isdir(c) and os.path.exists(os.path.join(c, 'saju-engine.js')):
            return (open(os.path.join(c, 'fortune-text.js'), encoding='utf-8').read() + '\n' +
                    open(os.path.join(c, 'saju-engine.js'), encoding='utf-8').read()), os.path.join(c, 'saju-engine.js')
        if c and os.path.isfile(c):
            return open(c, encoding='utf-8').read(), c
    sys.exit('자바스크립트 엔진 파일을 찾지 못했어요')


def run_js(code, n):
    args = [START.year, START.month, START.day, n, *TODAY]
    node = shutil.which('node')
    if node:
        with tempfile.TemporaryDirectory() as t:
            f = os.path.join(t, 'run.js')
            open(f, 'w', encoding='utf-8').write('global.window = global;\n' + code + '\nconst run = ' + RUN + ';\n'
                                                 'process.stdout.write(JSON.stringify(run(' + json.dumps(args) + ')));\n')
            return json.loads(subprocess.run([node, f], capture_output=True, check=True).stdout.decode('utf-8')), 'node'
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel='msedge', headless=True)
        except Exception:
            b = p.chromium.launch(headless=True)
        pg = b.new_page()
        pg.set_content('<html><body></body></html>')
        pg.add_script_tag(content=code)
        out = pg.evaluate(RUN, args)
        b.close()
        return out, 'browser'


def main():
    code, src = js_source(sys.argv[1] if len(sys.argv) > 1 else None)
    n = (END - START).days + 1
    js, how = run_js(code, n)
    bad = 0
    for k in range(n):
        d = START + dt.timedelta(days=k)
        q = pillars(d.year, d.month, d.day)
        fm, nm = daeun(q, d.year, d.month, d.day, True)
        ff, nf = daeun(q, d.year, d.month, d.day, False)
        f = fortune(d.year, d.month, d.day, k % 2 == 0, *TODAY)
        py = [q['ys'], q['yb'], q['ms'], q['mb'], q['di'], q['jie_today'][2] if q['jie_today'] else '', nm, 1 if fm else 0, nf,
              f['total'], ','.join(map(str, f['scores'])), f['head'], f['tip'], f['tti_line']]
        if py != js[k]:
            bad += 1
            if bad <= 10:
                print('DIFF', d, py, js[k])
    print('엔진 %s (%s 로 실행)' % (os.path.relpath(src), how))
    print('검사 %d일 (%s ~ %s) · 불일치 %d' % (n, START, END, bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
