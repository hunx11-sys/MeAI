# -*- coding: utf-8 -*-
"""고친 뒤 무엇이 달라졌는지 확인하는 회귀 점검 (v8.54).

README 의 모든 변경 기록이 근거로 대는 「실설계 N건 재생성 · 쪽별 글자 차이 0쪽」을
이 스크립트 하나로 한다. 고치기 **전에** 한 번, **후에** 한 번 찍어 비교한다.

    python regress.py snap before  설계서폴더        # 고치기 전 상태 저장
    ( 코드 수정 )
    python regress.py snap after   설계서폴더        # 고친 뒤 상태 저장
    python regress.py diff before after             # 무엇이 달라졌는지

설계서폴더 : 실제 상품설명서 PDF 가 든 폴더(하위 폴더까지 찾는다).
저장 위치  : out/regress/<이름>.json  (저장소에 올리지 않는다 — .gitignore out/)

무엇을 비교하나
  · 생성 지면을 포함한 **쪽별 글자** — 한 글자라도 다르면 그 쪽을 찍어 보여 준다
  · 감사 로그(미분류·검토필요·금액표없음 등)의 증감
  · 담보 인식 건수 · 생성 쪽수 · 글자 이탈/잘림 경고

읽는 법 : 고친 곳만 달라지고 나머지가 그대로여야 한다. 의도하지 않은 쪽이 달라졌으면
          그 쪽을 열어 확인한다. '이탈·잘림' 은 0 이어야 한다(글자가 지면을 넘쳤다는 뜻).
"""
import glob, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'out', 'regress')


def _pages(pdf):
    import pdfplumber
    with pdfplumber.open(pdf) as d:
        return [re.sub(r'\s+', '', p.extract_text() or '') for p in d.pages]


def snap(name, folder):
    sys.path.insert(0, BASE)
    import pipeline
    os.makedirs(OUT, exist_ok=True)
    pdfs = sorted(f for f in glob.glob(os.path.join(folder, '**', '*.pdf'), recursive=True))
    if not pdfs:
        print('설계서 PDF 를 찾지 못했습니다 :', folder); sys.exit(1)
    res = {}
    for f in pdfs:
        key = os.path.splitext(os.path.basename(f))[0]
        try:
            r = pipeline.build(f)
        except Exception as ex:
            print('  ! %-28s 생성 실패 %s: %s' % (key[:28], type(ex).__name__, ex))
            res[key] = {'오류': '%s: %s' % (type(ex).__name__, ex)}
            continue
        lay = r['audit']['요약'].get('지면검사') or []
        res[key] = {'pages': _pages(r['out_pdf']), 'audit': r['audit'],
                    'matched': r['matched'], 'riders': r['rider_count'], 'recog': r.get('recog'),
                    'made': r['audit']['요약'].get('생성쪽수'),
                    'warn': [x for x in lay if '이탈' in x or '잘림' in x]}
        print('  %-28s 생성 %s쪽 · 인식 %d/%d (%s) · 이탈잘림 %d'
              % (key[:28], res[key]['made'], r['matched'], r['rider_count'], _recog_s(r.get('recog')), len(res[key]['warn'])), flush=True)
    p = os.path.join(OUT, name + '.json')
    json.dump(res, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    print('저장 %s · 설계 %d건' % (p, len(res)))


def _recog_s(rc):
    """인식 집계 한 줄 — 마스터·부모연결·규칙만·계산제외(v8.61). 옛 스냅샷(집계 없음)은 '-'"""
    if not rc: return '-'
    return '마스터 %(마스터)d·부모연결 %(부모연결)d·규칙만 %(규칙만)d·계산제외 %(계산제외)d' % rc


def _logs(a):
    L = (a or {}).get('로그') or []
    return {json.dumps(x, ensure_ascii=False, sort_keys=True) for x in L}


def diff(before, after):
    A = json.load(open(os.path.join(OUT, before + '.json'), encoding='utf-8'))
    B = json.load(open(os.path.join(OUT, after + '.json'), encoding='utf-8'))
    only = set(A) ^ set(B)
    if only: print('한쪽에만 있는 설계 :', ', '.join(sorted(only)))
    bad = 0
    for k in sorted(set(A) & set(B)):
        a, b = A[k], B[k]
        if a.get('오류') or b.get('오류'):
            print('### %-26s 생성 실패 — 전 %s / 후 %s' % (k[:26], a.get('오류', '정상'), b.get('오류', '정상'))); bad += 1; continue
        pa, pb = a['pages'], b['pages']
        d = [i + 1 for i, (x, y) in enumerate(zip(pa, pb)) if x != y]
        gone, new = _logs(a['audit']) - _logs(b['audit']), _logs(b['audit']) - _logs(a['audit'])
        flag = d or gone or new or b['warn'] or a['matched'] != b['matched'] or len(pa) != len(pb) or a.get('recog') != b.get('recog')
        bad += bool(flag)
        print('### %-26s 쪽 %d→%d · 글자다른쪽 %s · 인식 %d/%d→%d/%d · 이탈잘림 %d · 로그 -%d/+%d'
              % (k[:26], len(pa), len(pb), d or '없음', a['matched'], a['riders'], b['matched'], b['riders'],
                 len(b['warn']), len(gone), len(new)))
        if a.get('recog') != b.get('recog'):
            print('    인식 상태 : %s → %s' % (_recog_s(a.get('recog')), _recog_s(b.get('recog'))))
        for x in sorted(gone)[:5]: print('    - 사라진 로그 :', x[:150])
        for x in sorted(new)[:5]:  print('    + 새 로그     :', x[:150])
        for i in d[:3]:
            x, y = pa[i - 1], pb[i - 1]
            j = next((n for n in range(min(len(x), len(y))) if x[n] != y[n]), 0)
            print('    p%-3d 전 …%s' % (i, x[max(0, j - 40):j + 90]))
            print('    p%-3d 후 …%s' % (i, y[max(0, j - 40):j + 90]))
        for w in b['warn'][:3]: print('    ! 지면 경고 :', w)
    print('\n달라진(또는 경고 있는) 설계 %d건 / %d건' % (bad, len(set(A) & set(B))))


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'snap': snap(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'diff': diff(sys.argv[2], sys.argv[3])
    else: print(__doc__); sys.exit(1)
