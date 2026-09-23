#!/usr/bin/env python3
"""
분류표 행 누락·특약 보장코드 누락 보정
- 저장소 루트에서 실행: python3 scripts/fix_tables.py
- tool.html 의 DATA 블록만 고쳐 쓴다. (recover_terms.py 와 같은 방식)

약관 원문(text)에는 있는데 화면에 그리는 행 표(rows)나 특약 보장코드(k)에
빠져 있던 것을 약관대로 채운다. 원인은 두 가지였다.
  1) 범위 기호가 하이픈인 행 (H10-H13, M91-M94) — 물결(~)만 읽어 통째로 빠짐
  2) 코드 뒤에 괄호 제외 주석이 줄바꿈으로 이어지는 행 (K93 (K93.0* 제외) 등)
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')

# ── 분류표에 넣을 행 : (분류표 이름, 어느 코드 뒤에, 질병명, 코드) ──
#    anchor 가 None 이면 맨 뒤에 붙인다.
ROWS = [
 ('특정다빈도29대질병 분류표', 'H05',      '결막의 장애', ['H10~H13']),
 ('특정다빈도29대질병 분류표', 'K92',      '달리 분류된 질환에서의 기타 소화기관장애 (K93.0* 제외)', ['K93']),
 ('특정다빈도29대질병 분류표', 'M34',      '달리 분류된 질환에서의 척추병증 (M49.0* 제외)', ['M49']),
 ('특정다빈도29대질병 분류표', 'M60~M63',  '기타 연조직장애 (M74, M78 제외)', ['M70~M79']),
 ('특정다빈도29대질병 분류표', 'M89',      '연골병증', ['M91~M94']),

 ('남성특정비뇨기계질환 분류표', None, '음낭수종 및 정액류', ['N43']),
 ('남성특정비뇨기계질환 분류표', None, '고환의 염전', ['N44']),
 ('남성특정비뇨기계질환 분류표', None, '고환염 및 부고환염', ['N45']),
 ('남성특정비뇨기계질환 분류표', None, '달리 분류되지 않은 남성생식기관의 염증성 장애', ['N49']),
 ('남성특정비뇨기계질환 분류표', None, '남성생식기관의 기타 장애', ['N50']),
 ('남성특정비뇨기계질환 분류표', None, '달리 분류된 질환에서의 남성생식기관의 장애', ['N51']),
 ('남성특정비뇨기계질환 분류표', None, '편모충성 전립선염(N51.0*)', ['A59.08']),
 ('남성특정비뇨기계질환 분류표', None, '남성 생식기관의 결핵', ['A18.14']),
 ('남성특정비뇨기계질환 분류표', None, '볼거리고환염(N51.1*)', ['B26.0']),

 ('만성당뇨합병증 분류표', None, '당뇨병성 단일신경병증', ['G59.0']),
 ('만성당뇨합병증 분류표', None, '기타 당뇨병성 다발신경병증', ['G63.2']),
 ('만성당뇨합병증 분류표', None, '당뇨병성 백내장', ['H28.0']),
 ('만성당뇨합병증 분류표', None, '당뇨병성 망막병증', ['H36.0']),
 ('만성당뇨합병증 분류표', None, '당뇨병에서의 사구체장애', ['N08.3']),

 ('호흡기관련질병 분류표', '__head__', '급성 상기도감염', ['J00~J06']),
 ('호흡기관련질병 분류표', 'J45',      '폐렴', ['J12~J18']),

 ('결핵분류표', None, '다약제내성 결핵', ['U84.30']),
 ('결핵분류표', None, '광범위약제내성 결핵', ['U84.31']),

 ('화상분류표', 'T21', '손목 및 손을 제외한 어깨와 팔의 화상 및 부식', ['T22']),
 ('화상분류표', 'T23', '발목 및 발을 제외한 엉덩이 및 다리의 화상 및 부식', ['T24']),
 ('화상 분류표', 'T21', '손목 및 손을 제외한 어깨와 팔의 화상 및 부식', ['T22']),
 ('화상 분류표', 'T23', '발목 및 발을 제외한 엉덩이 및 다리의 화상 및 부식', ['T24']),
]

# ── 특약 보장코드에 채울 것 : (특약 id, 근거 분류표 이름) ──
#    그 분류표의 대상코드 중 특약에 없는 것을 약관 표기 그대로 넣는다.
RIDERS = [
 ('케219', '특정다빈도29대질병 분류표'),
 ('케220', '특정다빈도29대질병 분류표'),
 ('케219', '관절염,생식기질환 분류표'),
 ('케220', '관절염,생식기질환 분류표'),
 ('통123', '후각특정질환 분류표'),
 ('통123', '특정31대질병 분류표'),
]

CODE = re.compile(r'[A-Z]\d{2}(?:\.\d{1,2})?(?:\s*[~∼〜～\-–—]\s*[A-Z]?\d{2}(?:\.\d{1,2})?)?')


def strip_parens(s):
    out, d = [], 0
    for ch in s:
        if ch == '(':
            d += 1
        elif ch == ')':
            d = max(0, d - 1); continue
        if d == 0:
            out.append(ch)
    return ''.join(out)


def table_codes(t):
    """분류표 원문에서 대상질병 코드만 (괄호 안 제외 주석·뒤따르는 수가코드표 제외)"""
    txt = (t.get('text') or '').replace('', ' ')
    m = re.search(r'분\s*류\s*번\s*호', txt)
    if not m:
        return []
    body = txt[m.end():]
    e = re.search(r'대상질병 분류표의 분류번호와|제10차 개정 이후|\d\.\s*진단 당시의'
                  r'|주\)\s*향후|【별표|수가코드', body)
    if e:
        body = body[:e.start()]
    out = []
    for c in CODE.findall(strip_parens(body)):
        c = re.sub(r'\s*[~∼〜～\-–—]\s*', '~', c.strip())
        if c != 'P00~P96' and c not in out:
            out.append(c)
    return out


def base(c):
    return str(c).upper().split('~')[0].split('.')[0]


def expand(lst):
    s = set()
    for t in (lst or []):
        t = str(t).upper()
        m = re.match(r'^([A-Z])(\d{2})(?:\.\d+)?\s*[~∼\-]\s*([A-Z]?)(\d{2})', t)
        if m:
            l1, a, l2, b = m.group(1), int(m.group(2)), (m.group(3) or m.group(1)), int(m.group(4))
            if l1 == l2:
                s.update(f'{l1}{n:02d}' for n in range(a, b + 1))
            else:
                s.update(f'{l1}{n:02d}' for n in range(a, 100))
                s.update(f'{l2}{n:02d}' for n in range(0, b + 1))
        else:
            s.add(t.split('.')[0])
    return s


def main():
    src = open(TOOL, encoding='utf-8').read()
    m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', src, re.S)
    D = json.loads(m.group(2))
    T, R = D['tables'], {r['id']: r for r in D['riders']}

    # 1) 분류표 행 채우기
    added = 0
    for name, anchor, label, codes in ROWS:
        for t in T.values():
            if t.get('name') != name:
                continue
            rows = t.get('rows') or []
            if not rows:
                continue
            norm = lambda c: re.sub(r'\s*[~∼〜～\-–—]\s*', '~', str(c).upper().strip())
            if any(norm(c) == norm(codes[0]) for r in rows for c in (r.get('codes') or [])):
                continue                                   # 이미 있음 (코드 전체로 비교)
            row = {'label': label, 'codes': codes}
            if anchor == '__head__':
                rows.insert(0, row)
            elif anchor is None:
                rows.append(row)
            else:
                i = next((k for k, r in enumerate(rows)
                          if any(base(c) == base(anchor) for c in (r.get('codes') or []))), None)
                rows.insert(i + 1 if i is not None else len(rows), row)
            t['rows'] = rows
            added += 1
            print(f'  행 추가 · {name} (p.{t.get("page")}) : {label} {codes}')

    # 2) 특약 보장코드 채우기
    filled = 0
    for rid, tname in RIDERS:
        r = R.get(rid)
        t = next((x for x in T.values() if x.get('name') == tname and table_codes(x)), None)
        if not r or not t:
            print(f'  ! 건너뜀 {rid} / {tname}'); continue
        want = table_codes(t)
        have = expand(r.get('k'))
        add = [c for c in want if base(c) not in have]
        if not add:
            continue
        r['k'] = (r.get('k') or []) + add
        filled += len(add)
        print(f'  보장코드 추가 · {r["p"]} 「{r["n"]}」 ← {tname}')
        print(f'     {len(add)}개: {", ".join(add)}')

    out = json.dumps(D, ensure_ascii=False, separators=(',', ':'))
    open(TOOL, 'w', encoding='utf-8').write(src[:m.start(2)] + out + src[m.end(2):])
    print(f'\n분류표 행 {added}개 추가 · 특약 보장코드 {filled}개 추가')


if __name__ == '__main__':
    main()
