# 인수 시험 세트 만들기 — 파이썬 판이 만든 정답(PDF · 요약)을 입력과 나란히 적는다. 자바 쪽 `Main --selftest <폴더>` 가 이것과 견준다(파이썬 없이).
# 사용 : python3 golden/make_selftest.py <출력 폴더> <입력.json …>
#        <이름>.json(입력 그대로) · <이름>.expected.pdf(파이썬 판 완성본) · <이름>.expected.json(요약)
# 담보 식별표(GA_CODE_MAP)는 준 대로 쓰고, 썼는지 여부를 요약의 code_map 에 적는다(자바 쪽이 같은 조건으로 돈다).
# 입력에 개인정보가 있으면 정답 PDF 에도 그대로 찍힌다 — 실제 설계에서 만든 입력은 먼저 가짜 값으로 바꾼다. 세트에는 정보계 담보명 · 코드가 들어 있어 사내 자료다(저장소에 넣지 않는다).
import sys, os, re, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'proposal_smart'))
import ga_v2 as GV, ga_proposal as GP, code_input as CI, pipeline, api
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SEC = re.compile(r' · [\d.]+초$', re.M)      # 로그 넷째 줄 끝의 처리 시간
def summary(p, pdf):
    try:
        o, log, info = GV.build(p, pdf)
        rid = GP.RID
        return dict(ok=True, pages=info['pages'], care=info['care'], detail_pages=info['detail_pages'], riders=info['riders'],
                    matched=sum(1 for r in rid if r.get('matched')), product=GP.PRODUCT, premium=GP.PREMIUM, warn=info['warn'],
                    log=SEC.sub('', open(log, encoding='utf-8').read()))
    except pipeline.DesignUnreadable as e: return dict(ok=False, error_type='DesignUnreadable', error=str(e))
n = 0
for f in sys.argv[2:]:
    nm = os.path.splitext(os.path.basename(f))[0]; txt = open(f, encoding='utf-8-sig').read()
    open(os.path.join(OUT, nm + '.json'), 'w', encoding='utf-8').write(txt)
    pdf = os.path.join(OUT, nm + '.expected.pdf')
    try: res = summary(CI.parse(txt), pdf)
    except CI.InputError as e: res = dict(ok=False, error_type='InputError', error=str(e))
    res['version'] = api.VERSION; res['code_map'] = bool(CI.code_map())
    lg = os.path.join(OUT, nm + '.expected_log.txt')
    if os.path.exists(lg): os.remove(lg)
    if not res['ok'] and os.path.exists(pdf): os.remove(pdf)
    json.dump(res, open(os.path.join(OUT, nm + '.expected.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n += 1; print('%-28s %s' % (nm, ('%d쪽' % res['pages']) if res['ok'] else '만들지 않음(%s)' % res['error_type']), flush=True)
GV.close_browser()
print('시험 세트 %d건 → %s' % (n, OUT))
