# 4 · 5단계 정답지 — 파이썬 판이 브라우저에 넘기는 HTML 을 쪽 묶음마다 그대로 받아 적는다(+ 칸 값 · 간병인 판정 · 로그 · 완성 PDF)
# 사용 : python3 golden/dump_html.py <출력 폴더> <입력.json ...>      (입력 = 담보코드 입력 JSON · code_input 사양)
# 출력 : <출력 폴더>/<입력 이름>.golden.json · <입력 이름>.pdf · fonts.json(글꼴 CSS 는 커서 한 번만 따로)
import sys, os, json, hashlib, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'proposal_smart'))
import ga_v2 as GV, ga_proposal as GP, code_input as CI, scen_engine as S
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FONTS, NOTO = GV.fonts_css(), GV.noto_css()
json.dump(dict(fonts_css=FONTS, noto_css=NOTO, fonts_md5=hashlib.md5(FONTS.encode()).hexdigest(), noto_md5=hashlib.md5(NOTO.encode()).hexdigest()),
          open(os.path.join(OUT, 'fonts.json'), 'w', encoding='utf-8'), ensure_ascii=False)
def strip(h): return h.replace(NOTO, '@@NOTO@@').replace(FONTS, '@@FONTS@@') if NOTO else h.replace(FONTS, '@@FONTS@@')
cap = []
_goto0 = GV._goto
def _goto(html, name):
    cap.append([name, strip(html)]); return _goto0(html, name)
GV._goto = _goto
def plain(o):
    try: return json.loads(json.dumps(o, ensure_ascii=False, default=lambda x: sorted(x) if isinstance(x, (set, frozenset)) else str(x)))
    except Exception as e: return 'dump 실패 : %s' % e
for f in sys.argv[2:]:
    nm = os.path.splitext(os.path.basename(f))[0]; del cap[:]; t0 = time.time()
    txt = open(f, encoding='utf-8-sig').read()
    try:
        p = CI.parse(txt); pdf = os.path.join(OUT, nm + '.pdf')
        o, log, info = GV.build(p, pdf)
        info = dict(info); info.pop('sec', None)
        res = dict(ok=True, htmls=[list(x) for x in cap], info=plain(info), log=open(log, encoding='utf-8').read(),
                   val={k: [plain(v[0]), plain(v[1])] for k, v in GP.VAL.items()}, extra=plain({k: v for k, v in GV.EXTRA.items()}),
                   rid=plain(GP.RID), product=GP.PRODUCT, premium=GP.PREMIUM, nrid=GP.NRID, issues=plain(S.issues_grouped()))
    except (CI.InputError, Exception) as e:
        res = dict(ok=False, error_type=type(e).__name__, error=str(e), htmls=[list(x) for x in cap])
    json.dump(res, open(os.path.join(OUT, nm + '.golden.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('%-34s %s %.0f초 · html %d개' % (nm, 'ok' if res['ok'] else '실패 ' + res.get('error', '')[:60], time.time() - t0, len(cap)), flush=True)
GV.close_browser()
