# -*- coding: utf-8 -*-
"""폴립및양성종양수술(급여,1-6종) 분류표 추출 — 약관 PDF 의 【별표 폴립및양성종양수술(급여,1-6종) 분류표】 → polyp6.json

  python extract_polyp6.py "../무배당 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형)약관.pdf"

· 「갱신형 폴립및양성종양수술비(1-6종)(급여,연간1회한)」 은 수술 종(1~6종)마다 금액이 다르다(제1조 : 종별 보험가입금액의 100%).
  설계서에는 [1종] ~ [6종] 여섯 줄로 실린다. 사례의 진료행위(수가)코드가 몇 종인지 알아야 그 줄 하나만 지급할 수 있다.
· 종은 표의 칸 선(pdfplumber 표 추출)으로만 읽는다 — 글자 순서로 짐작하지 않는다(약관은 두 단 조판 · CLAUDE.md 10).
  표의 「종」 칸은 합쳐진 칸이라 첫 줄에만 숫자가 있고, 쪽 · 단이 바뀌면 다시 적혀 있다(그 표의 첫 줄에 숫자가 없으면 멈춘다).
· 점검(하나라도 어긋나면 저장하지 않고 멈춘다)
    ① 코드가 겹치지 않는다  ② 읽는 순서(쪽 → 왼쪽 단 → 오른쪽 단)대로 종이 1 → 6 으로만 커진다
    ③ 특약 마스터(db.json)의 이 특약 수가코드 목록과 코드 집합이 똑같다
"""
import sys, os, re, json
import pdfplumber
BASE = os.path.dirname(os.path.abspath(__file__))
TITLE = '폴립및양성종양수술(급여,1-6종)분류표'

def extract(pdf):
    rows = []; pages = []
    with pdfplumber.open(pdf) as p:
        start = None
        for i in range(len(p.pages) - 1, -1, -1):                 # 별표는 책 뒤쪽 — 뒤에서부터 표 머리글(「종 | 구 분 | 의료 행위 내용 | 진료행위코드」)이 있는 쪽을 찾는다
            t = re.sub(r'\s+', '', p.pages[i].extract_text() or '')
            if TITLE in t and '진료행위코드에해당하는의료행위' in t: start = i; break
        if start is None: raise SystemExit('분류표 머리글을 못 찾음 : ' + TITLE)
        for k in range(start, min(start + 12, len(p.pages))):
            pg = p.pages[k]; got = 0
            for tb in sorted(pg.find_tables(), key=lambda t: (t.bbox[0] > pg.width / 2, t.bbox[1])):
                d = tb.extract()
                if not d or [re.sub(r'\s+', '', c or '') for c in d[0]] != ['종', '구분', '의료행위내용', '진료행위코드']: continue
                g = None
                for r in d[1:]:
                    if r[0]: g = int(r[0])
                    if g is None: raise SystemExit('%d쪽 표의 첫 줄에 종이 없음 : %s' % (k + 1, r))
                    code = re.sub(r'\s+', '', r[3] or '')
                    if not re.fullmatch(r'[A-Z]{1,2}\d{3,4}[A-Z]?', code): raise SystemExit('%d쪽 코드 꼴이 아님 : %s' % (k + 1, r))
                    rows.append(dict(code=code, grade=g, name=re.sub(r'\s+', '', r[2] or ''), page=k + 1)); got += 1
            if got: pages.append(k + 1)
            elif rows: break
    return rows, pages

def main(pdf):
    rows, pages = extract(pdf)
    codes = [r['code'] for r in rows]; gs = [r['grade'] for r in rows]
    assert len(codes) == len(set(codes)), '코드가 겹침'
    assert all(a <= b for a, b in zip(gs, gs[1:])) and set(gs) == {1, 2, 3, 4, 5, 6}, '종이 읽는 순서대로 커지지 않음'
    db = json.load(open(os.path.join(BASE, 'db.json'), encoding='utf-8'))['riders']
    ex = json.load(open(os.path.join(BASE, 'db_terms_extra.json'), encoding='utf-8'))['riders']
    ms = [r for r in db + ex if '폴립및양성종양수술비' in r['n'].replace(' ', '') and r.get('hc')]
    bad = [r['id'] for r in ms if set(r['hc']) != set(codes)]
    assert ms and not bad, '특약 마스터 수가코드와 다름 : %s' % bad
    out = dict(_note='폴립및양성종양수술(급여,1-6종) 분류표 — 진료행위(수가)코드 → 종. extract_polyp6.py 가 약관 표의 칸 선으로 읽은 것(손으로 고치지 않는다)',
               source=os.path.basename(pdf), pages=pages, count=len(rows), by_grade={str(g): gs.count(g) for g in range(1, 7)},
               masters=sorted(r['id'] for r in ms), grades={r['code']: r['grade'] for r in rows}, rows=rows)
    json.dump(out, open(os.path.join(BASE, 'polyp6.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('polyp6.json · 코드 %d개 · 종별 %s · %s쪽 · 같은 목록을 쓰는 마스터 특약 %d건' % (len(rows), out['by_grade'], pages, len(ms)))

if __name__ == '__main__':
    main(sys.argv[1])
