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
import json, os, re, shutil, subprocess, sys, time, uuid

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import build_all as BA                      # auto_meta · last_cover_page · page_count · guess_line
import matcher
import scen_engine as S                     # recog : 담보 인식 상태 집계(v8.61)
from build_pdf import merge

OUT = os.path.join(BASE, 'out')


def _work():
    d = os.path.join(OUT, 'job_%s_%s' % (time.strftime('%Y%m%d_%H%M%S'), uuid.uuid4().hex[:6]))
    os.makedirs(d, exist_ok=True)
    return d


def read_riders(src_pdf):
    """원본 PDF의 가입담보리스트에서 담보 목록만 뽑는다(지면 생성 없이 인식 결과만 볼 때)."""
    rows = matcher.read_proposal(src_pdf)
    return matcher.read_proposal(src_pdf, line=BA.guess_line(rows, src_pdf))


# ── 설계서를 못 읽었을 때 : 빈 제안서(0원 · 「-」 투성이)를 만들지 않고 이유를 알려 멈춘다(v8.98) ──
class DesignUnreadable(ValueError):
    """설계서에서 계산할 담보를 하나도 읽지 못함. 메시지는 화면 · 명령창에 그대로 보여 줄 쉬운 말"""


_DRM = (b'fasoo', b'scdsa', b'drmone', b'markany', b'document safer', b'softcamp', b'drm')


def fail_note(out_pdf, src_pdf, msg):
    """만들지 않은 이유를 결과 PDF 자리 옆에 글 파일로 남긴다(끌어다 놓기로 돌려 명령창을 못 본 사람용) — 파일 이름은 영문(…_FAILED.txt)"""
    p = os.path.splitext(os.path.abspath(out_pdf))[0] + '_FAILED.txt'
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8-sig') as fh:          # BOM — 윈도우 메모장이 한글을 깨뜨리지 않게
        fh.write('원본 설계서 : %s\n만들지 않은 이유 : %s\n' % (os.path.basename(src_pdf), msg))
    return p


def not_pdf(head):
    """파일 앞부분(바이트)이 PDF 가 아니면 이유 문장, PDF 면 빈 문자열"""
    if b'%PDF' in head[:1024]: return ''
    drm = any(m in head[:4096].lower() for m in _DRM)
    return ('PDF 파일이 아닙니다%s. 보안을 푼(복호화한) 설계서 PDF 를 넣어 주세요.'
            % (' — 사내 보안 프로그램(DRM)으로 잠긴 파일로 보입니다' if drm else ''))


def check_file(src_pdf):
    """읽기 전에 파일 자체를 본다 — PDF 가 아님(사내 보안 DRM 으로 잠긴 파일 등) · 깨진 PDF · 암호 PDF"""
    m = not_pdf(open(src_pdf, 'rb').read(4096))
    if m: raise DesignUnreadable(m)
    import pymupdf
    try:
        d = pymupdf.open(src_pdf)
    except Exception as e:
        raise DesignUnreadable('PDF 를 열 수 없습니다(파일이 깨졌을 수 있습니다 · %s). 설계 시스템에서 설계서를 다시 받아 넣어 주세요.' % type(e).__name__)
    with d:
        if d.needs_pass:
            raise DesignUnreadable('암호가 걸린 PDF 입니다. 암호를 푼 설계서 PDF 를 넣어 주세요.')


def check_riders(src_pdf, riders):
    """담보를 읽은 뒤 — 하나도 못 읽었거나, 읽었어도 특약 마스터에서 하나도 못 찾았으면 이유를 골라 멈춘다
    (한 건이라도 찾으면 그대로 간다 : 못 찾은 담보는 지금처럼 「계산 제외 + 로그」)"""
    if riders and S.recog(riders)['계산제외'] < len(riders):      # 마스터 · 부모연결 · 규칙만 중 하나라도 있으면 계산할 것이 있다
        return
    if riders:
        prod = re.sub(r'\s+', ' ', (BA.auto_meta(src_pdf).get('product') or '')).strip()
        raise DesignUnreadable('담보 %d건을 읽었지만 특약 마스터 · 규칙표에서 하나도 찾지 못했습니다%s. 아직 등록하지 않은 상품 · 약관일 수 있습니다 — 개발 담당에게 이 설계서를 보내 주세요.'
                               % (len(riders), (' (상품 : %s)' % prod) if prod else ''))
    import pymupdf
    with pymupdf.open(src_pdf) as d:
        n = len(d)
        t = re.sub(r'\s+', '', ''.join(p.get_text() for p in d))
    if len(t) < 100:
        raise DesignUnreadable('글자가 없는 그림 PDF 입니다(%d쪽 · 읽은 글자 %d자) — 스캔본 · 화면 캡처 · 「그림으로 인쇄」 · 보안 출력본은 읽지 못합니다. '
                               '설계 시스템에서 「PDF 저장(다운로드)」으로 받은 원본 설계서를 넣어 주세요.' % (n, len(t)))
    if '가입담보리스트' not in t:                    # 가입설계서마다 있는 표 제목(설계서 63건 확인 · 이미 만든 제안서 · 상품설명서에는 없다)
        raise DesignUnreadable('메리츠화재 가입설계서가 아닌 문서로 보입니다(「가입담보리스트」 표가 없음). 청약서 · 상품설명서만 따로 받은 파일 · 이미 만든 제안서 · '
                               '다른 회사 설계서나, 사내 보안 프로그램이 내용을 가린 파일은 읽지 못합니다 — 가입설계서 원본 PDF 를 넣어 주세요.')
    raise DesignUnreadable('설계서의 「가입담보리스트」 표에서 담보 줄을 하나도 읽지 못했습니다(설계서 양식이 바뀌었을 수 있습니다). 개발 담당에게 이 설계서를 보내 주세요.')


def build(src_pdf, cust=None, workdir=None, keep=True):
    """원본 PDF → 스마트 제안서 지면 생성 → 삽입. 산출물 경로와 감사 로그를 돌려준다.

    cust : customer.json 내용(dict). 생략하면 원본 PDF에서 메타·담보를 자동 인식한다.
    keep : False면 작업폴더를 지운다(산출물은 미리 복사해 둘 것).
    """
    src_pdf = os.path.abspath(src_pdf)
    if not os.path.exists(src_pdf):
        raise FileNotFoundError(src_pdf)
    import assets_ready                    # 글꼴·로고가 없는 PC 에서도 멈추지 않게(assets/ 가 저장소에 없다)
    assets_ready.ensure(src_pdf)
    w = workdir or _work()
    t0 = time.time()

    check_file(src_pdf)                    # PDF 가 아님(DRM) · 깨짐 · 암호 → 이유를 알려 멈춘다(v8.98)
    c = dict(cust) if cust else BA.auto_meta(src_pdf)
    if not c.get('riders'):
        c['riders'] = read_riders(src_pdf)
        check_riders(src_pdf, c['riders'])  # 담보를 하나도 못 읽음(그림 PDF · 다른 문서) → 빈 지면 대신 이유(v8.98)
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
         'recog': S.recog(c['riders']),      # 마스터 / 부모연결 / 규칙만 / 계산제외 — matched 는 앞 둘의 합(v8.61)
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
        # 어느 크로미엄 판으로 찍었는지 남긴다(v8.49). 현장에서 지면이 이상하다는 말이 나오면
        # 생성 PC와 현장 PC의 판을 바로 맞춰 볼 수 있다.
        ver = [x[9:] for x in lay if x.startswith('RENDERER ')]
        lay = [x for x in lay if not x.startswith('RENDERER ')]
        audit['요약']['렌더러'] = ver[0] if ver else '알 수 없음'
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
