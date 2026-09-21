# -*- coding: utf-8 -*-
"""스마트 제안서 생성 파이프라인 — 함수 한 번 호출로 끝나는 진입점(API·배치 공용).

    from pipeline import build
    r = build('원본_상품설명서.pdf')
    r['attached']    # 지면을 붙였는지(대상 담보가 없으면 False)
    r['out_pdf']     # 원본 + 생성 지면이 합쳐진 PDF
    r['pages_pdf']   # 생성 지면만 담은 PDF
    r['pages_html']  # 생성 지면 HTML(프론트엔드 미리보기용)
    r['audit']       # 감사 로그(요약·제외 담보와 사유)

build_all.py(명령행 실행)와 같은 로직이며, 호출마다 별도 작업폴더를 쓰므로 동시 호출에 안전하다.
LLM·외부 API를 쓰지 않는다 — 전부 규칙표와 약관 데이터에 따른 계산이다.
"""
import json, os, shutil, subprocess, sys, time, uuid

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import build_all as BA                      # auto_meta · last_cover_page · page_count · guess_line
import matcher
from build_pdf import merge

OUT = os.path.join(BASE, 'out')


def _work():
    d = os.path.join(OUT, 'job_%s_%s' % (time.strftime('%Y%m%d_%H%M%S'), uuid.uuid4().hex[:6]))
    os.makedirs(d, exist_ok=True)
    return d


def read_riders(src_pdf):
    """원본 PDF의 가입담보리스트에서 담보 목록만 뽑는다(지면 생성 없이 인식 결과만 볼 때)."""
    rows = matcher.read_proposal(src_pdf)
    return matcher.read_proposal(src_pdf, line=BA.guess_line(rows))


def build(src_pdf, cust=None, workdir=None, keep=True):
    """원본 PDF → 스마트 제안서 지면 생성 → 삽입. 산출물 경로와 감사 로그를 돌려준다.

    cust : customer.json 내용(dict). 생략하면 원본 PDF에서 메타·담보를 자동 인식한다.
    keep : False면 작업폴더를 지운다(산출물은 미리 복사해 둘 것).
    """
    src_pdf = os.path.abspath(src_pdf)
    if not os.path.exists(src_pdf):
        raise FileNotFoundError(src_pdf)
    w = workdir or _work()
    t0 = time.time()

    c = dict(cust) if cust else BA.auto_meta(src_pdf)
    if not c.get('riders'):
        c['riders'] = read_riders(src_pdf)
    c['src'] = os.path.basename(src_pdf)
    try:                                   # 2차 안전장치(v8.22) : 상품설명서의 담보별 약관 요약을 읽어 붙인다
        import desc_engine
        c['riders'], c['desc_info'] = desc_engine.attach(c['riders'], src_pdf)
    except Exception as e:
        c['desc_info'] = {'ok': False, 'err': str(e)}
    try:                                   # 3차 안전장치(v8.41) : 설계서 뒤쪽 「특약 안내사항」 표와 금액 대조
        import verify3
        c['verify3'] = verify3.compare(c['riders'], src_pdf)
    except Exception as e:
        c['verify3'] = [{'오류': str(e)}]
    c['insert_after'] = BA.last_cover_page(src_pdf)
    c['base_pages'] = BA.page_count(src_pdf)

    cust_path = os.path.join(w, 'customer.json')
    html = os.path.join(w, 'pages.html')
    pages_pdf = os.path.join(w, 'pages.pdf')
    out_pdf = os.path.join(w, 'result.pdf')
    json.dump(c, open(cust_path, 'w', encoding='utf-8'), ensure_ascii=False)

    subprocess.check_call([sys.executable, os.path.join(BASE, 'gen2.py'), cust_path, html])
    audit = json.load(open(os.path.splitext(html)[0] + '_audit.json', encoding='utf-8'))
    new = audit['요약'].get('생성쪽수') or 0

    r = {'attached': bool(new), 'audit': audit, 'workdir': w,
         'meta': {k: v for k, v in c.items() if k != 'riders'},
         'riders': c['riders'], 'rider_count': len(c['riders']),
         'matched': sum(1 for x in c['riders'] if x.get('matched')),
         'insert_after': c['insert_after'], 'base_pages': c['base_pages'],
         'new_pages': new, 'pages_html': html}
    if audit['요약'].get('제외상품'):     # 제작 대상에서 뺀 상품 — 왜 안 붙였는지 호출한 쪽에 알린다
        r['excluded'] = audit['요약']['제외상품']

    if not new:                              # 대상 담보 없는 설계(운전자·치아 등) → 원본 그대로
        shutil.copyfile(src_pdf, out_pdf)
        r.update(out_pdf=out_pdf, pages_pdf=None, total_pages=c['base_pages'])
    else:
        # 지면 검사 결과(축소·이탈·잘림·여백)를 감사 로그로 올린다(v8.48).
        # 예전에는 화면에만 찍혀, 다른 크로미엄 판에서 글자가 겹쳐도 호출한 쪽은 알 수 없었다.
        out = subprocess.run([sys.executable, os.path.join(BASE, 'render.py'), html, pages_pdf],
                             check=True, capture_output=True, text=True).stdout
        lay = [x.strip() for x in out.splitlines() if x.strip()]
        audit['요약']['지면검사'] = lay
        bad = [x for x in lay if '이탈' in x or '잘림' in x]
        if bad:
            audit['로그'].append({'구분': '지면넘침', '담보': '-',
                                 '사유': '지면에서 글자가 틀 밖으로 나갔습니다 — ' + ' / '.join(bad[:3])})
            r['layout_warn'] = bad
        json.dump(audit, open(os.path.splitext(html)[0] + '_audit.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        total = merge(src_pdf, pages_pdf, out_pdf, insert_after=c['insert_after'], new=new)
        r.update(out_pdf=out_pdf, pages_pdf=pages_pdf, total_pages=total)

    r['elapsed_sec'] = round(time.time() - t0, 1)
    if not keep:
        shutil.rmtree(w, ignore_errors=True)
        r['workdir'] = None
    return r


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('사용법 : python pipeline.py 원본_상품설명서.pdf [결과.pdf]'); sys.exit(1)
    res = build(sys.argv[1])
    if len(sys.argv) > 2:
        shutil.copyfile(res['out_pdf'], sys.argv[2]); res['out_pdf'] = sys.argv[2]
    print(json.dumps({k: v for k, v in res.items() if k not in ('riders', 'audit')},
                     ensure_ascii=False, indent=2))
    print('계산 제외 %d건 · 총 %d쪽' % (len(res['audit']['로그']), res['total_pages']))
