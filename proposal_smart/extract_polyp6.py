# -*- coding: utf-8 -*-
"""약관 【별표】 폴립및양성종양수술(급여,1-6종) 분류표 PDF → polyp6.json (진료행위코드 → 종).
   사용 : python extract_polyp6.py "../약관1.pdf" ["../약관2.pdf" ...]
   표(종 / 구 분 / 의료 행위 내용 / 진료행위코드)를 셀 단위로 읽는다. 「종」 칸은 합친 칸이라
   위 칸의 종을 아래 줄로 이어 받는다(표가 쪽·단을 넘어가면 다음 표 첫 줄에 종이 다시 찍힌다).
   여러 약관을 주면 상품마다 따로 읽고 서로 같은지 대조한다 — 다르면 멈춘다(추정하지 않는다).
   코드 형식 [A-Z]{1,2}\\d{3,4} · 종 1~6 만 채택. 같은 코드가 두 종에 나오면 멈춘다."""
import json, os, re, subprocess, sys

TITLE = '폴립및양성종양수술(급여,1-6종) 분류표'

def _pages(pdf_path):
    """분류표 제목이 있는 쪽(0부터)과 그 뒤 2쪽 — 쪽 찾기는 pdftotext(빠름), 표 읽기는 pdfplumber."""
    txt = subprocess.run(['pdftotext', '-layout', pdf_path, '-'], capture_output=True, text=True).stdout
    pages = txt.split('\f')
    hit = [i for i, t in enumerate(pages) if TITLE in re.sub(r'\s+', '', t) or TITLE.replace(' ', '') in re.sub(r'\s+', '', t)]
    # 본문의 【별표5(… 분류표)】 언급이 아니라 분류표 첫 쪽 : 「진료행위」 머리줄이 있는 쪽
    hit = [i for i in hit if '진료행위' in pages[i] and '의료 행위 내용' in pages[i] or '의료행위내용' in re.sub(r'\s+', '', pages[i])]
    return hit

def extract(pdf_path):
    import pdfplumber
    found = _pages(pdf_path)
    if not found: return None, None, None          # 이 특약이 없는 상품 약관 — 건너뛴다
    start = found[0]
    codes, rows = {}, []
    with pdfplumber.open(pdf_path) as pdf:
        for pno in range(start, min(start + 4, len(pdf.pages))):
            for tb in pdf.pages[pno].find_tables():
                data = tb.extract()
                if not data or (data[0][0] or '').replace(' ', '') != '종': continue
                g = None
                for r in data[1:]:
                    c = [(x or '').replace('\n', '').strip() for x in r]
                    if len(c) < 4: continue
                    if re.fullmatch(r'[1-6]', c[0]): g = int(c[0])
                    code = c[3].replace(' ', '')
                    if not re.fullmatch(r'[A-Z]{1,2}\d{3,4}', code): continue
                    if g is None: raise SystemExit('종 칸 없이 시작한 표 : %s 쪽 %d 코드 %s' % (pdf_path, pno + 1, code))
                    if code in codes and codes[code] != g:
                        raise SystemExit('같은 코드가 두 종에 : %s %d / %d' % (code, codes[code], g))
                    codes[code] = g
                    rows.append({'code': code, 'grade': g, 'name': c[2], 'page': pno + 1})
    return codes, rows, start + 1

if __name__ == '__main__':
    pdfs = sys.argv[1:]
    if not pdfs: raise SystemExit(__doc__)
    base, base_rows, src = None, None, []
    for p in pdfs:
        codes, rows, page = extract(p)
        if codes is None:
            print('%-70s (분류표 없음 · 건너뜀)' % os.path.basename(p)[:70]); continue
        src.append({'pdf': os.path.basename(p), 'page': page, 'codes': len(codes)})
        if base is None: base, base_rows = codes, rows
        elif codes != base:
            only_a = sorted(set(base) - set(codes)); only_b = sorted(set(codes) - set(base))
            diff = sorted(k for k in set(base) & set(codes) if base[k] != codes[k])
            raise SystemExit('분류표가 상품마다 다름 : %s | 앞에만 %s · 여기만 %s · 종 다름 %s' % (p, only_a, only_b, diff))
        print('%-70s %d쪽 · 코드 %d' % (os.path.basename(p)[:70], page, len(codes)))
    from collections import Counter
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'polyp6.json')
    json.dump({'source': '약관 【별표】 ' + TITLE + ' (진료행위코드 · 종)', 'pdfs': src,
               'rows': sorted(base_rows, key=lambda r: (r['grade'], r['code']))},
              open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('polyp6.json 생성 :', dst, '| 코드', len(base), '· 종별', dict(sorted(Counter(base.values()).items())))
