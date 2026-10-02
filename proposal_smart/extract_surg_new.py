# -*- coding: utf-8 -*-
"""신수술분류표 추출 — 약관 PDF 의 【별표 신수술분류표[기본]】·【별표 질병 신수술분류표[주요수술]】·【별표 상해 신수술분류표[주요수술]】 → surg_new.json
  python extract_surg_new.py "../무배당 메리츠 The건강한 내Mom대로 5.10.5 보장보험2607약관.pdf"

· [기본] : 보장대상 수술코드(ADRG) 목록. 1-7종 수술분류표(surg7.json)와 코드가 같은지 함께 적는다.
· [주요수술] : 수술코드 → 수술종류(장기이식 · 개두및두부 · 개흉 · 개복 · 각막조직피부이식및조직재건 · 경피적). 질병·상해 표를 따로 둔다.
· 코드·종류는 표에서만 읽는다. 조문 안의 예시 코드(“B601” 등 따옴표 속)는 표가 아니므로 뺀다.
약관이 2단 조판이라 글자 순서가 섞일 수 있어, 코드 바로 뒤에 수술종류 글자가 오는 줄만 인정하고 못 읽은 코드는 로그에 남긴다(추정하지 않는다)."""
import sys, os, re, json, collections
import pymupdf
BASE = os.path.dirname(os.path.abspath(__file__))
TYPES = [('장기이식', r'장기\s*이식\s*수\s*술'), ('개두및두부', r'개두\s*및\s*두부\s*수술'), ('개흉', r'개흉\s*수술'), ('개복', r'개복\s*수술'),
         ('각막조직피부이식및조직재건', r'각막'), ('경피적', r'경피적\s*수술')]

def text_of(pdf):
    d = pymupdf.open(pdf)
    return '\n'.join('\n=== PAGE %d ===\n' % (i + 1) + d[i].get_text() for i in range(len(d)))

def segment(t, title_re):
    """목차·조문 참조가 아닌 별표 본문 머리글부터 다음 【별표 머리글 전까지"""
    for x in re.finditer(title_re, t):
        if '....' in t[x.end():x.end() + 160]: continue
        if '라 함은' in t[max(0, x.start() - 80):x.start()] or '에서 정한' in t[x.end():x.end() + 40]: continue
        s = t[x.start():x.start() + 400000]; m = re.search(r'\n【별표', s[40:])
        s = s[:m.start() + 40] if m else s
        s = re.sub(r'“[^”]*”', ' ', s)                       # 조문 예시 코드(“B601”) 제거
        s = re.sub(r'=== PAGE \d+ ===', '', s); s = re.sub(r'\n\d{3}\n', '\n', s)
        return s
    return None

def parse_basic(t):
    s = segment(t, r'【별표[^】\n]{0,24}】\s*\n?\s*신수술분류표\s*\[기본\]')
    return sorted(set(re.findall(r'(?<![A-Z0-9])[A-Z]\d{3}(?![0-9])', s))) if s else None

def parse_major(t, kind):
    s = segment(t, r'【별표[^】\n]{0,24}】\s*\n?\s*' + kind + r'\s*신수술분류표\s*\[주요수술\]')
    if not s: return None, None
    toks = s.split('\n'); res = {}; un = []
    for i, tok in enumerate(toks):
        c = tok.strip()
        if not re.fullmatch(r'[A-Z]\d{3}', c): continue
        after = ' '.join(x.strip() for x in toks[i + 1:i + 4])
        typ = next((n for n, p in TYPES if re.match(r'\s*' + p, after)), None)
        if typ: res[c] = typ
        else: un.append((c, after[:30]))
    return res, un

if __name__ == '__main__':
    pdf = sys.argv[1]
    t = text_of(pdf)
    basic = parse_basic(t)
    dz, un_dz = parse_major(t, '질병')
    inj, un_inj = parse_major(t, '상해')
    s7 = {r['code'] for r in json.load(open(os.path.join(BASE, 'surg7.json'), encoding='utf-8'))['rows']}
    out = {'source': os.path.basename(pdf), 'note': '신수술비 특약(수술코드당 연간3회한) 판정용 — [기본]은 코드 목록, [주요수술]은 코드→수술종류. extract_surg_new.py 로 생성',
           'basic': basic, 'basic_vs_surg7': {'only_basic': sorted(set(basic) - s7), 'only_surg7': sorted(s7 - set(basic))},
           'major': {'질병': dz, '상해': inj}, 'unresolved': {'질병': un_dz, '상해': un_inj}}
    json.dump(out, open(os.path.join(BASE, 'surg_new.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('[기본] 코드 %d · surg7 과 차이 : 기본에만 %s · surg7에만 %s' % (len(basic), out['basic_vs_surg7']['only_basic'][:5], out['basic_vs_surg7']['only_surg7'][:5]))
    for k, d, u in (('질병', dz, un_dz), ('상해', inj, un_inj)):
        print('[주요수술 %s] 코드 %d %s · 못 읽은 코드 %d %s' % (k, len(d), dict(collections.Counter(d.values())), len(u), u[:4]))
