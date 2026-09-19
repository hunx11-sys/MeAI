# -*- coding: utf-8 -*-
"""약관 PDF의 【별표】 질병분류표 → rules.json 의 kcd_groups

약관 뒤쪽 별표에는 '6대심장질환 분류표', '5대질환 분류표'처럼 담보가 가리키는 대상질병 목록이 있다.
이 목록이 있어야 사례의 질병코드가 그 담보의 대상인지 판정할 수 있다(코드는 약관에서만 온다).

하는 일
  ① 【별표N】 ○○ 분류표 제목을 찾고, 다음 별표 전까지를 한 덩어리로 읽는다.
  ② 덩어리에서 질병코드(I05 · I44.1 · I05~I09 · !제외코드)를 뽑는다.
  ③ 이미 rules.json 에 같은 이름의 그룹이 있으면 **대조만** 하고(검증), 없으면 새 그룹 후보로 내놓는다.
  ④ --write 를 주면 새 그룹만 추가한다. 기존 그룹은 건드리지 않는다.

번호가 매겨진 소분류(1.만성류마티스심장질환 … 4.부정맥)는 하위 그룹으로도 함께 만든다.
'○○ 분류표' → '○○', 하위는 '○○_부정맥' 꼴.

사용 : python3 scripts/import_kcd_tables.py "약관.pdf" [--write] [--only 6대심장질환]
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = os.path.join(BASE, 'proposal_smart', 'rules.json')

HEAD = re.compile(r'【\s*별\s*표\s*(\d+)\s*】\s*\n?\s*([^\n]{2,44})')
CODE = re.compile(r'(?<![A-Za-z0-9])([A-Z]\d{2}(?:\.\d+)?)\s*(?:~\s*([A-Z]?\d{2}(?:\.\d+)?))?(?![0-9])')
SUB = re.compile(r'(?:^|\n)\s*(\d)\s*\.\s*([^\n]{2,24})')
# 분류표가 아닌 별표(수술분류표·장해분류표 등)는 여기서 다루지 않는다
SKIP = re.compile(r'수술분류표|장해분류표|적립이율|기관\(organ\)|급여 항암|행위\s*급여')


def norm(nm):
    nm = re.sub(r'[.\s]+$', '', re.sub(r'\.{3,}.*$', '', nm)).strip()
    return re.sub(r'\s+', ' ', nm)


MAXPG = 3          # 분류표 한 개가 차지하는 쪽수 상한 — 더 길면 다른 표까지 삼킨 것으로 본다


def blocks(doc):
    """[(별표번호, 이름, 본문)] — 제목이 나온 쪽부터 다음 제목 전까지(최대 MAXPG 쪽).
       목차의 제목(점선 … 으로 쪽번호를 잇는 줄)은 건너뛴다."""
    marks = []
    for i in range(len(doc)):
        t = doc[i].get_text()
        for m in HEAD.finditer(t):
            raw = m.group(2)
            if '...' in raw or re.search(r'\.{3,}\s*\d+\s*$', raw):
                continue                      # 목차 줄
            marks.append((i, m.start(), m.group(1), norm(raw)))
    out = []
    for n, (pg, pos, no, nm) in enumerate(marks):
        if n + 1 < len(marks):
            end_pg, end_pos = marks[n + 1][0], marks[n + 1][1]
        else:
            end_pg, end_pos = len(doc) - 1, None
        if end_pg > pg + MAXPG:               # 다음 별표가 멀면 상한까지만
            end_pg, end_pos = pg + MAXPG, None
        buf = doc[pg].get_text()[pos:]
        for j in range(pg + 1, end_pg + 1):
            t = doc[j].get_text()
            buf += t[:end_pos] if (j == end_pg and end_pos is not None) else t
        out.append((no, nm, buf))
    return out


# 약관 모든 분류표에 공통으로 붙는 '출생전후기에 기원한 특정 병태(P00~P96) 제외' 문장 —
# 이 표의 대상질병이 아니라 공통 면책이라 코드로 잡으면 모든 그룹이 오염된다.
BOILER = re.compile(r'출생전후기[^\n]{0,60}?P00\s*~\s*P96[^\n]{0,20}')


def codes_of(text):
    """본문 → 질병코드 목록(범위는 A15~A19 표기 그대로, 제외는 !코드)"""
    text = BOILER.sub(' ', text)
    out, seen = [], set()
    for m in CODE.finditer(text):
        a, b = m.group(1), m.group(2)
        if b:
            b = b if b[0].isalpha() else a[0] + b
            e = '%s~%s' % (a, b)
        else:
            e = a
        # '제외' 가 바로 앞뒤 20자 안에 있으면 제외코드로 본다
        near = text[max(0, m.start() - 22):m.end() + 12]
        if '제외' in near:
            e = '!' + e
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def subgroups(text):
    """'1.만성류마티스심장질환 … 4.부정맥' 처럼 번호가 매겨진 소분류 → {이름: [코드]}"""
    hits = [(m.start(), m.group(1), norm(m.group(2))) for m in SUB.finditer(text)]
    # 소분류 이름이 아니라 약관 본문 줄인 경우를 걸러낸다
    hits = [h for h in hits if not re.search(r'약관|보장|진단비|지급|사유|다만|회사|피보험자|경우', h[2])]
    out = {}
    for n, (pos, no, nm) in enumerate(hits):
        end = hits[n + 1][0] if n + 1 < len(hits) else len(text)
        c = codes_of(text[pos:end])
        if c and 1 <= len(nm) <= 22:
            out[nm] = c
    return out


def main():
    import pymupdf
    if len(sys.argv) < 2:
        print(__doc__)
        return
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]
    doc = pymupdf.open(sys.argv[1])
    rd = json.load(open(RULES, encoding='utf-8'))
    have = rd['kcd_groups']

    # db.json 의 특약별 약관 KCD 와 대조해 검증한다 — 이름이 분류표와 같은 담보를 찾는다
    import collections
    DB = json.load(open(os.path.join(BASE, 'proposal_smart', 'db.json'), encoding='utf-8'))['riders']
    byname = collections.defaultdict(list)
    for r in DB:
        if r.get('k'):
            byname[re.sub(r'^갱신형', '', re.sub(r'\s+', '', r['n']))].append(r['k'])

    def crosscheck(key, codes):
        """같은 이름을 쓰는 특약의 약관 KCD 와 견줘 본다 → ('일치'|'다름'|None, 비교대상)"""
        k = re.sub(r'\s+', '', key)
        for nm, lists in byname.items():
            if nm.startswith(k) and re.match(r'^%s(진단비|진단및치료비)' % re.escape(k), nm):
                for kc in lists:
                    if set(kc) == set(codes):
                        return '일치', nm
                return '다름', nm
        return None, None

    found, same, diff = {}, [], []
    for no, nm, body in blocks(doc):
        if '분류표' not in nm or SKIP.search(nm):
            continue
        key = norm(re.sub(r'\s*분류표.*$', '', nm))
        if only and only not in key:
            continue
        c = codes_of(body)
        if not c or len(c) > 400:
            continue
        if key in have:
            (same if set(have[key]) == set(c) else diff).append((key, len(have[key]), len(c)))
            continue
        if key in found and len(found[key]) >= len(c):
            continue
        st, ref = crosscheck(key, c)
        if st == '다름':
            diff.append((key, -1, len(c)))
            continue                      # 같은 이름 담보의 약관 KCD 와 다르면 넣지 않는다
        if st == '일치':
            same.append((key, len(c), len(c)))
        found[key] = c
        for sn, sc in subgroups(body).items():
            k2 = '%s_%s' % (key, sn)
            if k2 not in have and len(sc) < len(c):
                found[k2] = sc

    print('기존 그룹과 일치 %d종 · 다름 %d종 · 새 그룹 후보 %d종' % (len(same), len(diff), len(found)))
    for k, a, b in diff[:10]:
        print('   [다름] %-28s 기존 %d개 / 약관 %d개' % (k[:28], a, b))
    for k in sorted(found, key=lambda x: -len(found[x]))[:40]:
        print('   [새로] %-30s %2d개  %s' % (k[:30], len(found[k]), ', '.join(found[k][:8])))

    if '--write' in sys.argv and found:
        have.update(found)
        json.dump(rd, open(RULES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\n저장 → rules.json · kcd_groups', len(have), '종')
    elif found:
        print('\n(미리보기 — 저장하려면 --write)')


if __name__ == '__main__':
    main()
