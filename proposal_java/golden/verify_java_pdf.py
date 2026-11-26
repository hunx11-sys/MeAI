# 인쇄 검증(자바 판 PDF) — 파이썬 판 verify_v2.py 의 「완성 PDF 의 글자를 다시 읽어 계산 값과 대조」 를 자바가 만든 PDF 에 그대로 돌린다.
# 계산 값은 파이썬 판이 같은 입력으로 낸 것(G.load), 읽는 PDF 만 자바 것이다 — verify_v2 의 점검 함수는 고치지 않고 그대로 부른다.
# 사용 : python3 golden/verify_java_pdf.py <입력 JSON 폴더> <자바 출력 폴더> [이름 …]
#        자바 출력 폴더 = <이름>.java.pdf · <이름>.java.json(GoldenHtml 이 남긴 info) / 입력 = <입력 JSON 폴더>/<이름>.json(없으면 proposal_smart/ga_docs/<이름>.json)
#        담보 식별표는 정답지를 뽑을 때와 같게(GA_CODE_MAP)
import sys, os, json, glob, warnings
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); PS = os.path.join(HERE, '..', '..', 'proposal_smart'); sys.path.insert(0, PS)
import verify_v2 as VV, ga_v2 as G, code_input as CI
IN, JD = sys.argv[1], sys.argv[2]
names = sys.argv[3:] or sorted(os.path.basename(f)[:-len('.java.pdf')] for f in glob.glob(os.path.join(JD, '*.java.pdf')))
cur = {}
def java_build(design, out_pdf=None, age=''):
    G.load(design, age)                      # 파이썬 판 계산 값(대조의 기준)
    return cur['pdf'], None, cur['info']     # 읽는 PDF · 쪽 정보는 자바 판 것
G.build = java_build
bad = 0; tot = 0; nb = 0
for nm in names:
    f = os.path.join(IN, nm + '.json')
    if not os.path.exists(f): f = os.path.join(PS, 'ga_docs', nm + '.json')
    cur['pdf'] = os.path.join(JD, nm + '.java.pdf'); cur['info'] = json.load(open(os.path.join(JD, nm + '.java.json'), encoding='utf-8'))
    try:
        C, info = VV.verify(CI.parse(open(f, encoding='utf-8-sig').read()), None)
        tot += C.n; nb += len(C.bad); bad += bool(C.bad)
        print('%s %-32s %2d쪽 · 대조 %4d곳 · 다른 곳 %d' % ('통과' if not C.bad else '실패', nm, info['pages'], C.n, len(C.bad)), flush=True)
        for b in C.bad[:12]: print('      ' + b)
    except Exception as ex:
        bad += 1; print('오류 %s : %s: %s' % (nm, type(ex).__name__, ex), flush=True)
print('\n결과 : %s — 설계 %d건 · 대조 %d곳 · 다른 곳 %d' % ('전부 통과' if not bad else '실패 %d건' % bad, len(names), tot, nb))
sys.exit(1 if bad else 0)
