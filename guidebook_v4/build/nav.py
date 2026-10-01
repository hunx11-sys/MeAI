#!/usr/bin/env python3
# PDF 에 책갈피(파트 > 쪽 제목)와 누르면 그 쪽으로 가는 링크를 넣는다. 슬라이드 모양은 그대로.
# 사용: python3 nav.py <책.pdf> <책.pptx.nav.json>   (nav.json 은 deck.js 가 만든다)
#  - 책갈피: 1단 = 표지 · 읽는 법 · 목차 · PART 0n · 한 장 요약 · 마무리 / 2단 = 파트 안 각 쪽 제목
#  - 링크: lib.link() 로 적은 자리 · 쪽 위 'PART n' 머리글 → 그 파트 첫 쪽 · 꼬리말 → 목차(3쪽)
#          · 본문 속 'PART n' 글자 → 그 파트 첫 쪽
import json, os, re, sys

import pymupdf

SLIDE_W = 13.333  # 인치 (LAYOUT_WIDE)
TOC_PAGE = 3


def clean(t):
    return re.sub(r'\s+', ' ', str(t or '').replace('\n', ' ')).strip()


def main(pdf_path, json_path):
    d = json.load(open(json_path, encoding='utf8'))
    parts = {k: int(v) for k, v in (d.get('parts') or {}).items()}
    doc = pymupdf.open(pdf_path)
    N = doc.page_count
    if d.get('pages') != N:
        print(f'nav.py: 주의 — nav.json 쪽 수 {d.get("pages")} ≠ PDF 쪽 수 {N}')

    nav = {}
    for e in d.get('nav') or []:
        nav.setdefault(int(e['pageNo']), {}).update({k: v for k, v in e.items() if v not in (None, '')})

    # ── 책갈피
    part_start = {v: k for k, v in parts.items() if re.fullmatch(r'\d\d', k)}  # 파트 묶음은 '01'~'09' 키만
    sum_page = parts.get('sum')
    toc, in_part = [], False
    for p in range(1, N + 1):
        e = nav.get(p, {})
        title = clean(e.get('title'))
        if p in part_start or re.fullmatch(r'\d\d', str(e.get('part', ''))):
            num = part_start.get(p) or e['part']
            toc.append([1, f'PART {num} · {title}' if title else f'PART {num}', p]); in_part = True
        elif sum_page and p == sum_page:
            toc.append([1, '한 장 요약', p]); in_part = False
        elif 'kickerW' in e and in_part:          # base() 쪽: 파트 안이면 2단
            toc.append([2, title or f'{p}쪽', p])
        elif e:                                    # 표지·읽는 법·목차·마무리처럼 파트 밖 쪽
            toc.append([1, title or f'{p}쪽', p]); in_part = False
        elif p == N:                               # 기록 없는 마지막 쪽 = 마무리
            toc.append([1, '마무리', p]); in_part = False
        else:
            toc.append([2 if in_part else 1, f'{p}쪽', p])
    doc.set_toc(toc)

    # ── 링크
    counts = {'links': 0, 'kicker': 0, 'footer': 0, 'text': 0, 'skipped': 0}
    placed = {}  # 쪽 번호 → 이미 링크를 넣은 영역(겹치면 본문 검색 링크는 건너뜀)

    def goto(pno, rect, target, kind):
        try:
            t = int(target)
        except (TypeError, ValueError):
            counts['skipped'] += 1; return
        if not (1 <= pno <= N and 1 <= t <= N):
            counts['skipped'] += 1; return
        doc[pno - 1].insert_link({'kind': pymupdf.LINK_GOTO, 'from': rect, 'page': t - 1,
                                  'to': pymupdf.Point(0, 0), 'zoom': 0})
        placed.setdefault(pno, []).append(rect)
        counts[kind] += 1

    def inch_rect(page, x, y, w, h):
        s = page.rect.width / SLIDE_W
        return pymupdf.Rect(x * s, y * s, (x + w) * s, (y + h) * s)

    for L in d.get('links') or []:
        pno = int(L['pageNo'])
        if 1 <= pno <= N:
            goto(pno, inch_rect(doc[pno - 1], L['x'], L['y'], L['w'], L['h']), L['target'], 'links')
        else:
            counts['skipped'] += 1

    for p, e in nav.items():
        m = re.match(r'^PART (\d)', e.get('kicker') or '')
        if m and 'kickerW' in e and 1 <= p <= N:
            goto(p, inch_rect(doc[p - 1], 0.6, 0.42, float(e['kickerW']), 0.28), parts.get('0' + m.group(1)), 'kicker')

    for p in range(TOC_PAGE + 1, N + 1):
        goto(p, inch_rect(doc[p - 1], 0.6, 7.08, 4.6, 0.25), TOC_PAGE, 'footer')

    for p in range(TOC_PAGE + 1, N + 1):
        page = doc[p - 1]
        top = 0.75 * page.rect.width / SLIDE_W   # 머리글(0.42~0.7in)은 위에서 이미 링크함
        for n in range(1, 10):
            target = parts.get('0' + str(n))
            if not target or target == p:
                continue
            for r in page.search_for('PART ' + str(n)):
                if r.y0 < top:
                    continue
                if any(r.intersects(q) for q in placed.get(p, [])):
                    continue
                goto(p, r, target, 'text')

    tmp = pdf_path + '.navtmp'
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, pdf_path)
    total = counts['links'] + counts['kicker'] + counts['footer'] + counts['text']
    print(f"nav.py: 책갈피 {len(toc)}개 · 링크 {total}개 (지정 {counts['links']} · 머리글 {counts['kicker']} · "
          f"꼬리말 {counts['footer']} · 본문 PART {counts['text']}) · 건너뜀 {counts['skipped']}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('사용: python3 nav.py <책.pdf> <책.pptx.nav.json>')
    main(sys.argv[1], sys.argv[2])
