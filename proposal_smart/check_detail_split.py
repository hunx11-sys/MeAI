# -*- coding: utf-8 -*-
"""세부내역 쪽 나눔 점검 — 설계서 PDF 없이 도는 자체 시험(크로뮴만 있으면 된다 · 묶음 안에서도 실행)

  python3 check_detail_split.py          # 「결과 : 전부 통과」 여야 한다(종료코드 0)

「보장금액 세부내역」 의 한 묶음(구분 하나 + 그 특약 줄들)이 한 쪽보다 길면 줄 단위로 나눠 다음 쪽에 잇는다(v9.09 — 그 전에는 생성이 멈췄다).
가짜 계산서(특약 줄 수만 다른 묶음)를 조판기(ga_v2.render_detail)에 넣고, 나온 PDF 를 인쇄 검증기(verify_v2.v_detail)로 다시 읽는다.
보는 것 : 짧은 묶음은 예전처럼 통째로(표시 없음) · 긴 묶음은 나뉨(줄이 빠지거나 겹치지 않고 순서 그대로 · 쪽 밖으로 넘친 글자 없음) ·
세 쪽 이상에 걸치는 묶음 · 마지막 조각에 한 줄만 남지 않음 · 이어지는 조각의 표시(「(이어서)」 · 「앞 쪽과 같은 금액」 · 「다음 쪽에 이어짐」) ·
검증기가 틀린 지면을 잡는가(이어지는 조각의 금액이 다름 · 이어짐 표시가 없음 · 줄이 빠짐)
"""
import os, sys, shutil, tempfile, warnings
warnings.simplefilter('ignore')
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import fitz
import ga_v2 as G, verify_v2 as V

N = [0, 0]
def ok(name, cond, msg=''):
    N[0] += 1
    if not cond: N[1] += 1; print('실패 %s %s' % (name, msg))

LONG = '갱신형표적항암약물허가치료비(연간약물종류개수별)(비급여(전액본인부담포함))(연간1회한)[표적항암약물허가치료비(연간 약물종류 개수별)(비급여 (전액본인부담 포함))(연간1회한)[%d종이상]]'
def group(lab, n, base, long=False):
    """특약 줄 n개짜리 묶음 — 줄마다 금액이 달라(순서 · 빠짐 · 겹침이 금액 열에서 드러나게) · 구분 보장금액 = 줄 합"""
    rs = [((LONG % (i + 1)) if long else '시험특약%d' % (base + i), '세부 보장' if i % 5 == 0 else '', 1000 + i, base + i) for i in range(n)]
    return (lab, sum(a for *_, a in rs), rs)
def run(sections, js=None):
    """가짜 계산서 → 세부내역 PDF → (조판 보고, 쪽들, 검증 결과)"""
    keep = (G.GP.calc_sections, G.DETAIL_JS, G.TMP)
    G.TMP = tempfile.mkdtemp(prefix='detail_split_'); G.GP.calc_sections = lambda: sections
    if js: G.DETAIL_JS = js
    try:
        p = os.path.join(G.TMP, 'detail.pdf'); rep = G.render_detail(p); d = fitz.open(stream=open(p, 'rb').read(), filetype='pdf'); C = V.Check(); V.v_detail(list(d), C)
        return rep, d, C
    finally:
        shutil.rmtree(G.TMP, ignore_errors=True); G.GP.calc_sections, G.DETAIL_JS, G.TMP = keep
def inside(d): return all(w[3] <= pg.rect.height + 0.5 for pg in d for w in pg.get_text('words'))
def count(d, t): return sum(pg.get_text().count(t) for pg in d)

# 1. 짧은 묶음뿐 — 나누지 않는다(표시 없음 · 예전과 같은 길)
S1 = [('암 보장 세부 내역', [group('[진단] 짧은 묶음 %d' % i, 3, 100 * i) for i in range(1, 30)] + [('[진단] 없는 보장', None, [])])]
rep, d, C = run(S1)
ok('짧은 묶음 : 나눔 없음', rep['split'] == [] and not count(d, G.DETAIL_CONT) and not count(d, G.DETAIL_MORE), '— %s' % rep['split'])
ok('짧은 묶음 : 인쇄 검증 통과 · 쪽 밖 글자 없음', not C.bad and inside(d) and len(d) == rep['pages'], '— %s' % C.bad[:3])

# 2. 한 쪽을 넘는 묶음(앞뒤에 보통 묶음) — 나뉘어 이어진다
S2 = [('암 보장 세부 내역', [group('[진단] 앞 묶음', 4, 100), group('[항암약물] 표적(면역) 2가지 약물', 40, 2000, long=True), group('[항암방사선] 뒤 묶음', 3, 300)]),
      ('뇌 · 심 보장 세부 내역', [group('[진단] 다음 구역', 2, 500)])]
rep, d, C = run(S2)
sp = rep['split']
ok('긴 묶음 : 나뉨', len(sp) == 1 and len(sp[0]['parts']) >= 2 and sum(sp[0]['parts']) == 40, '— %s' % sp)
ok('긴 묶음 : 인쇄 검증 통과(줄 순서 · 빠짐 · 겹침 없음 · 조각 금액 같음)', not C.bad, '— %s' % C.bad[:3])
ok('긴 묶음 : 쪽 밖 글자 없음', inside(d) and len(d) == rep['pages'])
k = len(sp[0]['parts']) - 1 if sp else -1
ok('긴 묶음 : 이어짐 표시 수', count(d, G.DETAIL_CONT) == k and count(d, G.DETAIL_MORE) == k, '— %d · %d ≠ %d' % (count(d, G.DETAIL_CONT), count(d, G.DETAIL_MORE), k))
ok('긴 묶음 : 뒤 묶음이 마지막 조각과 같은 쪽에 이어짐', any(G.DETAIL_CONT in pg.get_text() and '뒤 묶음' in pg.get_text() for pg in d))

# 3. 세 쪽 이상에 걸치는 묶음 · 가운데 조각은 두 표시를 다 단다
rep, d, C = run([('암 보장 세부 내역', [group('[항암약물] 아주 긴 묶음', 150, 1000)])])
sp = rep['split']
ok('아주 긴 묶음 : 세 조각 이상', len(sp) == 1 and len(sp[0]['parts']) >= 3 and sum(sp[0]['parts']) == 150, '— %s' % sp)
ok('아주 긴 묶음 : 인쇄 검증 통과 · 쪽 밖 글자 없음', not C.bad and inside(d), '— %s' % C.bad[:3])
ok('아주 긴 묶음 : 가운데 조각에 두 표시', any(G.DETAIL_CONT in pg.get_text() and G.DETAIL_MORE in pg.get_text() for pg in d))

# 4. 마지막 조각에 한 줄만 남지 않는다(줄 수를 하나씩 늘려 가며)
tail = []; first = []
for n in range(34, 46):
    rep, d, C = run([('암 보장 세부 내역', [group('[수술] 줄 수 %d' % n, n, 1000)])])
    ok('줄 수 %d : 인쇄 검증 통과' % n, not C.bad and inside(d), '— %s' % C.bad[:2])
    for s in rep['split']:
        tail.append(s['parts'][-1]); first.append(s['parts'][0]); ok('줄 수 %d : 마지막 조각 두 줄 이상' % n, s['parts'][-1] >= 2 and sum(s['parts']) == n, '— %s' % s['parts'])
ok('줄 수 34~45 : 나뉘는 경우와 안 나뉘는 경우가 모두 시험됨', 0 < len(tail) < 12, '— 마지막 조각 줄 수 %s' % tail)
ok('줄 수 34~45 : 한 줄만 남을 자리에서 앞 조각이 한 줄을 넘겨줌', len(first) >= 2 and first[0] == max(first) - 1 and tail[0] == 2, '— 첫 조각 %s · 마지막 조각 %s' % (first, tail))

# 5. 검증기가 틀린 지면을 잡는가(조판 스크립트를 일부러 망가뜨려 본다)
def broken(old, new):
    assert G.DETAIL_JS.count(old) == 1, old
    return run(S2, G.DETAIL_JS.replace(old, new))[2]
C = broken("'\"' + rs + g.m + (mark", "'\"' + rs + (cont ? g.m.replace(/\\d/, '9') : g.m) + (mark")
ok('검증기 : 이어지는 조각의 금액이 다르면 잡는다', bool(C.bad))
C = broken("(cont ? '<i>' + CONT + '</i>' : '')", "''")
ok('검증기 : 「앞 쪽과 같은 금액」 표시가 없으면 잡는다(금액이 두 번 더해진 것처럼 읽힘)', bool(C.bad))
C = broken("(cont ? '<i class=\"ct\">' + KCONT + '</i>' : '')", "''")
ok('검증기 : 구분 칸의 「(이어서)」 가 없으면 잡는다', bool(C.bad))
C = broken("for (let i = i0; i < i1; i++) h +=", "for (let i = i0; i < i1; i++) if (!(i0 > 0 && i === i0 + 1)) h +=")
ok('검증기 : 이어지는 조각에서 줄이 빠지면 잡는다', bool(C.bad))

G.close_browser()
print('\n결과 : %s — 점검 %d개 · 실패 %d' % ('전부 통과' if not N[1] else '실패', N[0], N[1]))
sys.exit(1 if N[1] else 0)
