# MeAI 홈 넛지 v5 조립
#   python3 home_nudge/build.py             → dist/meai_home_nudge_v5.html  (원본 MeAI 홈 + 넛지 · 모의 서버 · 데모 메뉴, 한 파일 · 오프라인)
#   python3 home_nudge/build.py --package   → + dist/meai_home_nudge_v5_package.zip (개발 패키지 : 설계도 · API · DB · 소스 · 테스트 · 목업)
#   python3 home_nudge/build.py --names <실명 talks798.json>  → 화법 제출자 실명판(사내 시연용 · 저장소에 올리지 않는다)
import argparse, base64, hashlib, json, os, re, sys, zipfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DIST = os.path.join(REPO, 'dist')
MASCOTS = ['hello_wave', 'group_hello', 'tata_board', 'tata_ok', 'indi_idea', 'eco_think', 'rara_present', 'ziziri_stars', 'ziziri_cheer', 'success_thumbs', 'merry_ok']
NUDGE = ['src/nudge/core.js', 'src/nudge/fx.js', 'src/nudge/ui.js', 'src/nudge/cards.js', 'src/nudge/talks.js', 'src/nudge/dash.js', 'src/nudge/index.js']

def rd(p): return open(os.path.join(HERE, p), encoding='utf-8').read()
def js_safe(s): return s.replace('</script', '<\\/script').replace('<!--', '<\\!--')

def data_bundle(names=None):
    talks = json.load(open(names, encoding='utf-8')) if names else json.loads(rd('data/talks798.json'))
    d = { 'cfg': json.loads(rd('config/nudge.config.json')), 'cal': json.loads(rd('data/calendar.json')), 'quiz': json.loads(rd('data/quiz.json')),
          'talks': talks, 'seed': json.loads(rd('data/seed.json')) }
    return json.dumps(d, ensure_ascii=False, separators=(',', ':'))

def assets_bundle():
    out = {}
    for m in MASCOTS:
        p = os.path.join(REPO, 'ui', 'mascots', m + '.webp')
        out['mascots/' + m + '.webp'] = 'data:image/webp;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    return json.dumps(out, separators=(',', ':'))

BOOT = r"""
(function () {
  'use strict';
  var api = NZMock.createMockApi(window.NZ_DATA, { issueOn: 'reco.open' });   // 목업 : 추천 고객 카드를 열면 바로 세트(운영 권장값은 chat.custom)
  var host = NZHost.createDomHost({ fortuneUrl: 'unse_saju_tarot.html' });
  host.ready.then(function () { return MeAINudge.mount({ api: api, host: host }); }).then(function () { NZDemo.mount(api); });
})();
"""

def build_mockup(names=None, out=None):
    base = rd('vendor/meai_home_base_260929.html')
    assert base.count('</body>') == 1
    css = rd('src/nudge/nudge.css')
    js = [rd('src/core/rules.js'), rd('src/api/mock.js')] + [rd(p) for p in NUDGE] + [rd('src/host/dom-adapter.js'), rd('src/demo/demo.js')]
    inject = ('<!-- ===== MeAI 홈 넛지 v5 (목업) : 원본 홈 빌드 260929 위에 넛지 · 모의 서버 · 데모 메뉴를 얹음 ===== -->\n'
              '<style id="nz-style">\n' + css + '\n</style>\n'
              '<script id="nz-data">window.NZ_DATA=' + js_safe(data_bundle(names)) + ';window.NZ_ASSETS=' + assets_bundle() + ';</script>\n'
              '<script id="nz-script">\n' + js_safe('\n;\n'.join(js)) + '\n' + BOOT + '</script>\n')
    html = re.sub(r'<title>[^<]*</title>', '<title>MeAI 홈 · 넛지 플레이 v5 (목업)</title>', base, count=1)
    html = html.replace('</body>', inject + '</body>', 1)
    out = out or os.path.join(DIST, 'meai_home_nudge_v5.html')
    open(out, 'w', encoding='utf-8').write(html)
    print('목업', os.path.relpath(out, REPO), round(len(html.encode('utf-8')) / 1e6, 2), 'MB')
    return out

PKG_FILES = [
    'config/nudge.config.json', 'data/calendar.json', 'data/quiz.json', 'data/seed.json', 'data/talks798.json', 'data/talks_meta.json',
    'src/core/rules.js', 'src/api/client.js', 'src/api/mock.js', 'src/nudge/nudge.css'] + NUDGE + [
    'src/host/dom-adapter.js', 'src/host/simple-host.js', 'src/demo/demo.js', 'examples/sandbox.html', 'examples/sandbox.css', 'examples/sandbox-boot.js',
    'tests/rules.test.js', 'tests/make_vectors.js', 'tests/vectors.json',
    'tools/check_mockup.js', 'tools/check_sandbox.js', 'tools/check_a11y.js', 'tools/check_contract.py', 'tools/dump_mock.js', 'tools/shoot_docs.js', 'tools/import_talks.py', 'tools/render_doc.js']
DOCS = ['docs/BLUEPRINT.md', 'docs/BLUEPRINT.html', 'docs/BLUEPRINT.pdf', 'docs/INTEGRATION.md', 'docs/openapi.yaml', 'docs/schema.sql', 'docs/EVENTS.md', 'docs/README_PACKAGE.md'] + \
    ['docs/img/' + f for f in sorted(os.listdir(os.path.join(HERE, 'docs', 'img'))) if f.endswith('.png')]

def build_package(mock):
    out = os.path.join(DIST, 'meai_home_nudge_v5_package.zip')
    files, man = [], []
    for p in PKG_FILES + DOCS:
        fp = os.path.join(HERE, p)
        if os.path.exists(fp): files.append((fp, 'meai_home_nudge_v5/' + p))
        elif p.startswith('docs/BLUEPRINT.') and not p.endswith('.md'): print('  (없음, 건너뜀)', p)
        else: sys.exit('패키지에 넣을 파일이 없음 : ' + p)
    for m in MASCOTS:
        files.append((os.path.join(REPO, 'ui', 'mascots', m + '.webp'), 'meai_home_nudge_v5/assets/mascots/' + m + '.webp'))
        files.append((os.path.join(REPO, 'ui', 'mascots', m + '@2x.webp'), 'meai_home_nudge_v5/assets/mascots/' + m + '@2x.webp')) if os.path.exists(os.path.join(REPO, 'ui', 'mascots', m + '@2x.webp')) else None
    files.append((os.path.join(REPO, 'ui', 'mascots', 'RULES.md'), 'meai_home_nudge_v5/assets/mascots/RULES.md'))
    files.append((mock, 'meai_home_nudge_v5/mockup/meai_home_nudge_v5.html'))
    fortune = os.path.join(DIST, 'unse_saju_tarot.html')
    if os.path.exists(fortune): files.append((fortune, 'meai_home_nudge_v5/mockup/unse_saju_tarot.html'))
    readme_pkg = os.path.join(HERE, 'docs', 'README_PACKAGE.md')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for fp, arc in files:
            data = open(fp, 'rb').read()
            if arc.endswith('docs/README_PACKAGE.md'): arc = 'meai_home_nudge_v5/README_FIRST.md'
            if arc.endswith('examples/sandbox.html'): data = data.replace(b'data-asset-base="../../ui/"', b'data-asset-base="../assets/"')
            z.writestr(arc, data)
            man.append('%s  %8d  %s' % (hashlib.sha256(data).hexdigest()[:16], len(data), arc))
        z.writestr('meai_home_nudge_v5/MANIFEST.txt', 'MeAI 홈 넛지 v5 개발 패키지 · ' + datetime.date.today().isoformat() + '\n파일 ' + str(len(man)) + '개 · sha256 앞 16자리 · 바이트 · 경로\n\n' + '\n'.join(man) + '\n')
    print('패키지', os.path.relpath(out, REPO), len(man), '개 파일', round(os.path.getsize(out) / 1e6, 2), 'MB')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', action='store_true')
    ap.add_argument('--names')
    ap.add_argument('--out')
    a = ap.parse_args()
    mock = build_mockup(a.names, a.out)
    if a.package: build_package(mock)
