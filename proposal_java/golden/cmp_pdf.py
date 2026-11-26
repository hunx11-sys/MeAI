# 5단계 정답지 대조(PDF) — 자바 판이 만든 PDF 를 파이썬 판 PDF 와 놓고 견준다
#   ① 쪽수 · 쪽 크기  ② 쪽별 글자(낱말 차례 · 좌표 0.5pt 안)  ③ 배율(fit) · 경고  ④ 쪽 그림(72dpi) 픽셀 차이  ⑤ 파일 크기
# 사용 : python3 golden/cmp_pdf.py <정답지 폴더> <자바 출력 폴더> [이름 …] [--png <다른 쪽 그림을 둘 폴더>]
#        정답지 폴더 = <이름>.golden.json · <이름>.pdf(dump_html.py) / 자바 출력 폴더 = <이름>.java.pdf · <이름>.java.json(GoldenPdf)
# 통과 기준 : ① ② ③ 다른 곳 0 · ④ 쪽마다 「다른 픽셀(채널 차이 > PIX_TOL)」 0  · ⑤ 는 참고(자바 판이 파이썬 판의 SIZE_MAX 배 이하)
import sys, os, json, glob
import fitz, numpy as np
TOL_PT = 0.5        # 낱말 좌표 허용 차이(pt)
PIX_TOL = 2         # 한 픽셀의 채널 차이가 이보다 크면 「다른 픽셀」(JPEG 로 다시 담는 바탕 그림의 계산 끝자리 차이 ±1~2 만 봐준다)
SIZE_MAX = 1.25
args = sys.argv[1:]; png = None
if '--png' in args: i = args.index('--png'); png = args[i + 1]; del args[i:i + 2]
GD, JD = args[0], args[1]
names = args[2:] or sorted(os.path.basename(f)[:-len('.java.pdf')] for f in glob.glob(os.path.join(JD, '*.java.pdf')))
def words(pg): return [(w[4], w[0], w[1], w[2], w[3]) for w in pg.get_text('words')]
bad_all = 0; tot = dict(n=0, pages=0, words=0, maxpix=0, bigpix=0)
for nm in names:
    g = json.load(open(os.path.join(GD, nm + '.golden.json'), encoding='utf-8')); j = json.load(open(os.path.join(JD, nm + '.java.json'), encoding='utf-8'))
    pa, pb = os.path.join(GD, nm + '.pdf'), os.path.join(JD, nm + '.java.pdf')
    a, b = fitz.open(pa), fitz.open(pb); bad = []
    if len(a) != len(b): bad.append('쪽수 %d ≠ %d' % (len(a), len(b)))
    if j['fit'] != g['info']['fit']: bad.append('fit 다름 : 자바 %s · 파이썬 %s' % (j['fit'], g['info']['fit']))
    if j['warn'] != g['info']['warn']: bad.append('경고 다름 : 자바 %s · 파이썬 %s' % (j['warn'], g['info']['warn']))
    nw = 0; mx = 0; big = 0; worst = (0, 0); dmax = 0.0
    for i in range(min(len(a), len(b))):
        x, y = a[i], b[i]
        if abs(x.rect.width - y.rect.width) > 0.01 or abs(x.rect.height - y.rect.height) > 0.01: bad.append('%d쪽 크기 %s ≠ %s' % (i + 1, tuple(x.rect), tuple(y.rect)))
        wa, wb = words(x), words(y); nw += len(wa)
        if [w[0] for w in wa] != [w[0] for w in wb]:
            k = next((k for k in range(min(len(wa), len(wb))) if wa[k][0] != wb[k][0]), min(len(wa), len(wb)))
            bad.append('%d쪽 글자 다름(낱말 %d ≠ %d) — %d번째 : 파이썬 %r · 자바 %r' % (i + 1, len(wa), len(wb), k, wa[k][0] if k < len(wa) else None, wb[k][0] if k < len(wb) else None))
        else:
            d = max([max(abs(p[q] - r[q]) for q in range(1, 5)) for p, r in zip(wa, wb)] or [0]); dmax = max(dmax, d)
            if d > TOL_PT:
                k = next(k for k, (p, r) in enumerate(zip(wa, wb)) if max(abs(p[q] - r[q]) for q in range(1, 5)) > TOL_PT)
                bad.append('%d쪽 글자 자리 다름 %.2fpt — %r 파이썬 %s · 자바 %s' % (i + 1, d, wa[k][0], [round(v, 2) for v in wa[k][1:]], [round(v, 2) for v in wb[k][1:]]))
        ia = x.get_pixmap(dpi=72, alpha=False); ib = y.get_pixmap(dpi=72, alpha=False)
        if (ia.width, ia.height) != (ib.width, ib.height): bad.append('%d쪽 그림 크기 다름' % (i + 1)); continue
        A = np.frombuffer(ia.samples, np.uint8).reshape(ia.height, ia.width, 3).astype(np.int16); B = np.frombuffer(ib.samples, np.uint8).reshape(ib.height, ib.width, 3).astype(np.int16)
        D = np.abs(A - B).max(axis=2); m = int(D.max()); nb = int((D > PIX_TOL).sum())
        if m > worst[0]: worst = (m, i + 1)
        mx = max(mx, m); big += nb
        if nb:
            ys, xs = np.nonzero(D > PIX_TOL)
            bad.append('%d쪽 픽셀 다름 %d개(가장 큰 차이 %d · 자리 x %d~%d · y %d~%d)' % (i + 1, nb, m, xs.min(), xs.max(), ys.min(), ys.max()))
            if png:
                os.makedirs(png, exist_ok=True); ia.save(os.path.join(png, '%s_p%02d_py.png' % (nm, i + 1))); ib.save(os.path.join(png, '%s_p%02d_java.png' % (nm, i + 1)))
    sa, sb = os.path.getsize(pa), os.path.getsize(pb)
    if sb > sa * SIZE_MAX: bad.append('파일 크기 %.2fMB > 파이썬 %.2fMB × %.2f' % (sb / 1048576, sa / 1048576, SIZE_MAX))
    tot['n'] += 1; tot['pages'] += len(a); tot['words'] += nw; tot['maxpix'] = max(tot['maxpix'], mx); tot['bigpix'] += big
    print('%-32s %s · %d쪽 · 낱말 %d(자리 차이 최대 %.3fpt) · 픽셀 최대 차이 %d(%d쪽) · 크기 파이썬 %.2fMB → 자바 %.2fMB' % (nm, '같음' if not bad else '다름', len(a), nw, dmax, mx, worst[1], sa / 1048576, sb / 1048576))
    for x in bad[:12]: print('      ! ' + x)
    bad_all += len(bad)
print('\n결과 : %s — %d건 · %d쪽 · 낱말 %d개 · 다른 픽셀 %d개(가장 큰 채널 차이 %d)' % ('전부 통과(다른 곳 0)' if not bad_all else '다른 곳 %d' % bad_all, tot['n'], tot['pages'], tot['words'], tot['bigpix'], tot['maxpix']))
sys.exit(0 if not bad_all else 1)
