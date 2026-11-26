#!/usr/bin/env python3
"""스마트 제안서 자바 판 — IT 인계 묶음 만들기

  python3 scripts/build_java_package.py        # → dist/smart_proposal_java_package.zip

· 먼저 proposal_java 에서 `mvn -q -B package` 를 돌려 target/smart-proposal.jar · target/lib 를 만든다(이 스크립트가 돌린다 · --no-build 면 있는 것을 쓴다).
· 묶음 안 : 실행 파일(smart-proposal.jar · lib/) · 자료(data/ — 파이썬 판 proposal_smart 의 json · ga_assets 를 **그대로** 복사 + 파이썬 판이 구운 틀 그림 tpl_*.png. 자바 쪽에 따로 둔 자료는 없다) ·
  소스(src/ — pom.xml · 자바 소스 · 옮기기 규칙 PORTING.md · 정답지 뽑는 스크립트) · 안내(README.md) · 시작 파일(start.bat · start.sh) · 예시 입력.
· 설계서 · 정답지 · 담보 식별표(code_map.json — 정보계 코드가 든 사내 자료)는 넣지 않는다.
· 개인정보 점검은 파이썬 판 묶음과 같은 규칙(build_ga_v2_package.scan)으로 하고, 하나라도 걸리면 멈춘다.
"""
import os, re, sys, zipfile, subprocess, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import build_ga_v2_package as P                                   # scan(개인정보 점검) 규칙을 같이 쓴다

PJ, PS = os.path.join(ROOT, 'proposal_java'), os.path.join(ROOT, 'proposal_smart')
OUT = os.path.join(ROOT, 'dist', 'smart_proposal_java_package.zip')
TOP = 'smart_proposal_java'
SKIP_JSON = {'cust_a.json', 'cust_b.json'}                        # 9쪽 판 시험용 가상 고객 — 자바 판이 읽지 않는다

def tracked(prefix):
    r = subprocess.run(['git', '-c', 'core.quotepath=off', 'ls-files', '--cached', '--others', '--exclude-standard', prefix], cwd=ROOT, capture_output=True, text=True, check=True)
    return [f for f in sorted(set(r.stdout.split('\n'))) if f and os.path.isfile(os.path.join(ROOT, f))]

BAKED = ('cover1', 'cover2', 'p1')                              # 틀 그림(가안 그림에서 견본 글자를 지운 것) — 파이썬 판이 굽고 저장소에는 넣지 않는다. 자바 판은 구워 둔 것을 쓴다
def bake():
    """파이썬 판 ga_overlay.template 으로 틀 그림을 굽고(이미 있으면 그대로) 경로를 돌려준다"""
    sys.path.insert(0, PS)
    import ga_overlay as OV
    return [('data/ga_assets/mock/tpl_%s.png' % k, OV.template(k)) for k in BAKED]

def data_files():
    out = []
    for f in tracked('proposal_smart'):
        rel = f[len('proposal_smart/'):]
        if '/' not in rel and rel.endswith('.json') and rel not in SKIP_JSON: out.append(rel)
        elif rel.startswith('ga_assets/'): out.append(rel)
    return out

def version():
    s = open(os.path.join(PS, 'api.py'), encoding='utf-8').read()
    return re.search(r"^VERSION\s*=\s*'([^']+)'", s, re.M).group(1)

def main():
    if '--no-build' not in sys.argv:
        subprocess.run(['mvn', '-q', '-B', 'package', '-DskipTests'], cwd=PJ, check=True)
    jar = os.path.join(PJ, 'target', 'smart-proposal.jar'); lib = os.path.join(PJ, 'target', 'lib')
    assert os.path.isfile(jar), 'jar 가 없습니다 — proposal_java 에서 mvn package'
    items = [('smart-proposal.jar', jar)]
    items += [('lib/' + n, os.path.join(lib, n)) for n in sorted(os.listdir(lib)) if n.endswith('.jar')]
    items += [('data/' + r, os.path.join(PS, r)) for r in data_files()]
    items += bake()
    for f in tracked('proposal_java'):
        rel = f[len('proposal_java/'):]
        if rel in ('README.md', 'start.bat', 'start.sh'): items.append((rel, os.path.join(ROOT, f)))
        else: items.append(('src/' + rel, os.path.join(ROOT, f)))
    items.append(('examples/code_input_example.json', os.path.join(PS, 'ga_docs', 'code_input_example.json')))
    names = [n.strip() for n in os.environ.get('GA_V2_PERSONAL', '').split(',') if n.strip()]
    bad = []
    for arc, src in items:
        if arc.startswith('lib/') or arc == 'smart-proposal.jar': continue
        for h in P.scan(arc, open(src, 'rb').read(), names): bad.append('%s : %s' % (arc, h))
    if bad:
        for b in bad[:40]: print('개인정보로 보이는 글자 :', b)
        sys.exit('개인정보 점검에 걸려 묶음을 만들지 않았습니다')
    try: commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception: commit = ''
    dirty = bool(subprocess.run(['git', 'status', '--porcelain', 'proposal_java', 'proposal_smart'], cwd=ROOT, capture_output=True, text=True).stdout.strip())
    ver = '계산 버전 : %s (파이썬 판과 같은 계산 · 자바 판)\n만든 날 : %s\n커밋 : %s%s\n' % (version(), datetime.date.today().isoformat(), commit, ' + 변경' if dirty else '')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(TOP + '/VERSION.txt', ver)
        for arc, src in items:
            zi = zipfile.ZipInfo.from_file(src, TOP + '/' + arc)
            zi.compress_type = zipfile.ZIP_DEFLATED
            if arc.endswith('.sh'): zi.external_attr = (0o755 & 0xFFFF) << 16
            z.writestr(zi, open(src, 'rb').read(), compresslevel=9)
    print('묶음 %s · 파일 %d개 · %.1fMB · 계산 %s · 커밋 %s%s' % (OUT, len(items) + 1, os.path.getsize(OUT) / 1e6, version(), commit, ' + 변경' if dirty else ''))

if __name__ == '__main__':
    main()
