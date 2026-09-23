# -*- coding: utf-8 -*-
"""특약검색기(tool.html) 내장 약관 원문 → 질병코드 그룹표(rules.json kcd_groups) 재생성·검증 (v8.50)

    python extract_kcd_groups.py ../tool.html          # 대조만 — 어디가 다른지 보여준다
    python extract_kcd_groups.py ../tool.html --write  # 다른 그룹만 약관대로 고쳐 rules.json 에 쓴다

무엇을 읽나
  ① 「○○ 분류표」 별표 원문(name 이 '<그룹명> 분류표' 인 항목)  → 그 그룹의 대상 코드·제외 코드
  ② 「질병수술비(특정N대질병제외)」 특약 본문 제3조 ④항의 표     → 특정2대·5대·6대질병 그룹

어떻게 읽나 (v8.8 의 텍스트 추출이 놓친 것 세 가지를 고친다)
  · 범위 기호를 ~ 만 읽어 ∼(U+223C)·-(하이픈) 범위가 양 끝 두 코드로 쪼개졌다 → 세 기호를 모두 범위로 읽는다
  · '(N08.3 제외)' 같은 괄호 안 코드만 제외(!)이고 표 본문 코드는 대상인데, 제외 표시가 대상 코드에 붙었다
    → 괄호 안 '제외' 절의 코드만 제외로 읽는다
  · 한 표 안의 다른 절에서 대상으로 적힌 코드는 제외로 두지 않는다 (예 32대질병 : 결핵 절의 N74.0 은 대상,
    생식기 절의 (N74.0제외) 는 그 절 안의 제외 — 표 전체로는 대상)
같은 분류표가 상품·갱신형별로 여러 번 실려 있으므로 모두 읽어 일치하는 결과만 쓰고, 다르면 보고한다.

질병코드는 이 파일이 만들어내지 않는다 — 약관 원문에 적힌 코드·범위를 그대로 옮긴다.
특정5대·6대질병의 ① '대장의 용종 또는 양성신생물의 내시경적 절제술' 은 코드가 아닌 치료행위 조건이라
scen_engine 의 사례 태그(five_major)와 특약 마스터(db.json)가 쓰는 대리 코드 D12·K63.5 를 같이 둔다.
"""
import collections, io, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CODE = re.compile(r'(?<![A-Z0-9])([A-Z]\d{2}(?:\.\d{1,2})?)(?![0-9])')
RNG = re.compile(r'([A-Z]\d{2}(?:\.\d{1,2})?)\s*[~∼\-–]\s*([A-Z]\d{2}(?:\.\d{1,2})?)')
EXCL = re.compile(r'\((?:[^()]|\([^()]*\))*?제\s*외\s*\)')

# 분류표 이름으로 읽는 그룹 (rules.json 의 그룹명 → tool.html 의 분류표 name)
TABLE_GROUPS = ['6대심장질환', '16대특정암', '32대질병', '5대고액치료비암', '관절염,생식기질환',
                '급성심근경색증대상질병', '뇌졸중대상질병', '뇌출혈', '악성신생물(암)', '알츠하이머치매',
                '요양성특정질병', '유방암', '전이암', '제자리신생물', '중증질환자(심장질환) 산정특례대상',
                '충수염(맹장염)', '특정심장질환', '행동양식 불명 또는 미상의 신생물', '허혈성심장질환',
                '희귀난치성 7대질환',
                # v8.51 추가 — 담보는 마스터에 코드를 갖고 있어 계산에는 쓰이지 않지만,
                # 검수표에서 약관 코드를 바로 볼 수 있게 그룹표에도 둔다
                '중증질환자(뇌혈관질환) 산정특례대상', '특정순환계질환',
                '특정순환계질환(주요손상및질환)']
# 특약 본문 제3조 ④항으로 읽는 그룹 → 담보명
CLAUSE_GROUPS = {'특정2대질병': '질병수술비(특정2대질병제외)',
                 '특정5대질병': '질병수술비(특정5대질병제외)',
                 '특정6대질병': '질병수술비(특정6대질병제외)'}
POLYP_PROXY = ['D12', 'K63.5']         # ① 대장 용종·양성신생물 내시경적 절제술 의 대리 코드


TRAILERS = ('대상질병 분류표의 분류번호와 다르나', '【별표59-2】', '주) 향후', '※ 한국표준질병')


def segment(t):
    """표 본문만 남긴다 : 뒤따르는 보일러플레이트(트레일러 · 각주 예시) 앞까지.
    머리글에는 코드가 없고, '출생전후기 질병(P00~P96)은 포함되지 않습니다' 만 코드 모양이라 지운다.
    (머리글 '분류번호' 는 세로로 쪼개져 인쇄된 사본이 있어 시작점으로 쓰지 않는다)"""
    t = re.sub(r'\(\s*P00\s*[~∼\-–]\s*P96\s*\)', ' ', t)
    ends = [t.find(x) for x in TRAILERS if t.find(x) >= 0]
    if ends: t = t[:min(ends)]
    return t


def parse_table(text):
    """분류표 원문 → (대상 목록, 제외 목록). 범위는 'A15~A19' 로 정규화."""
    t = text.replace('\\n', ' ').replace('\n', ' ')
    t = re.sub(r'[†*+]', '', t)
    t = segment(t)
    excl = []
    while True:
        m = EXCL.search(t)
        if not m: break
        excl += CODE.findall(m.group(0))
        t = t[:m.start()] + ' ' + t[m.end():]
    ranges = []
    for a, b in RNG.findall(t):
        if a[0] != b[0]:
            raise ValueError('범위 표기가 이상함 %s~%s' % (a, b))
        if '.' in a or '.' in b:
            # 세분류 범위(Q26.0~Q26.4) 는 판정기가 범위로 못 읽으므로 코드 하나씩 펼친다
            pa, da = a.split('.'); pb, db = b.split('.')
            if pa != pb or len(da) != 1 or len(db) != 1:
                raise ValueError('범위 표기가 이상함 %s~%s' % (a, b))
            ranges += ['%s.%d' % (pa, i) for i in range(int(da), int(db) + 1)]
        else:
            ranges.append('%s~%s' % (a, b))
    t = RNG.sub(' ', t)
    singles = CODE.findall(t)
    seen = collections.OrderedDict()
    for c in ranges + singles: seen[c] = 1
    targets = list(seen)
    plain = set(singles)
    final_excl = []
    for c in excl:
        if c in plain or c in final_excl: continue      # 다른 절에서 대상으로 적힌 코드는 제외 아님
        final_excl.append(c)
    return targets, final_excl


def entries(T, name):
    """tool.html 에서 "name":"<name>" 인 JSON 항목을 전부 뽑는다."""
    out = []
    for m in re.finditer(r'"name":"%s"' % re.escape(name), T):
        s = T.rfind('{', 0, m.start()); depth = 0
        for j in range(s, len(T)):
            if T[j] == '{': depth += 1
            elif T[j] == '}':
                depth -= 1
                if depth == 0:
                    try: out.append(json.loads(T[s:j + 1]))
                    except Exception: pass
                    break
    return out


def clause_codes(T, rider_name):
    """「질병수술비(특정N대질병제외)」 특약 본문 제3조 ④항 표의 코드."""
    res = []
    n = re.search(r'특정(\d)대질병', rider_name).group(1)
    for m in re.finditer(r'"n":"질병수술비\(특정%s대질병\s*제외\)"' % n, T):
        b = T[m.end():m.end() + 60000]
        e = b.find('"st":'); b = b[:e]
        k = re.search(r'④\s*회사는[^④]{0,120}특정\d대질병의\s*질병수술비에\s*대[^④]{0,40}보상\s*하지\s*않습니다', b.replace('\\n', ' '))
        if not k: continue
        seg = b.replace('\\n', ' ')[k.end():]
        seg = seg[:seg.find('제4조(')]
        codes = list(collections.OrderedDict((c, 1) for c in CODE.findall(seg)))
        if '대장의 용종' in seg: codes = POLYP_PROXY + codes
        res.append(tuple(codes))
    return res


def cover(lst):
    """목록을 (3자리 코드 집합, 세분류 코드 집합, 제외 집합)으로 펼쳐 비교한다."""
    c3, sub, ex = set(), set(), set()
    for e in lst:
        e = e.strip()
        if e.startswith('!'): ex.add(e[1:].strip()); continue
        m = re.match(r'^([A-Z])(\d{2})~([A-Z])(\d{2})$', e)
        if m:
            for i in range(int(m.group(2)), int(m.group(4)) + 1): c3.add('%s%02d' % (m.group(1), i))
        elif '.' in e: sub.add(e)
        else: c3.add(e)
    return c3, sub, ex


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    T = io.open(sys.argv[1], encoding='utf-8', errors='replace').read()
    p = os.path.join(BASE, 'rules.json')
    doc = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    KG = doc['kcd_groups']
    derived = collections.OrderedDict()

    for g in TABLE_GROUPS:
        es = entries(T, g + ' 분류표')
        got = collections.Counter()
        for e in es:
            try: tg, ex = parse_table(e.get('text', ''))
            except ValueError as v: print('  ! %s p.%s : %s' % (g, e.get('page'), v)); continue
            got[(tuple(tg), tuple(ex))] += 1
        if not got:
            print('%-30s 분류표 없음' % g); continue
        (tg, ex), n = got.most_common(1)[0]
        derived[g] = list(tg) + ['!' + c for c in ex]
        if len(got) > 1:
            print('%-30s 사본 %d개 중 %d개만 일치 — 나머지는 다르게 읽힘 (인쇄 어긋남 사본)' % (g, len(es), n))
            for (tg2, ex2), n2 in got.most_common()[1:]:
                a, b = cover(list(tg)), cover(list(tg2))
                print('      %d개 사본 : 코드 차이 %s / 제외 차이 %s' % (n2, sorted(a[0] ^ b[0]) + sorted(a[1] ^ b[1]), sorted(a[2] ^ b[2])))

    for g, rn in CLAUSE_GROUPS.items():
        got = collections.Counter(clause_codes(T, rn))
        if not got:
            print('%-30s 특약 본문 ④항 없음' % g); continue
        codes, n = got.most_common(1)[0]
        derived[g] = list(codes)
        if len(got) > 1: print('%-30s 사본이 서로 다름 : %s' % (g, dict(got)))

    print('\n== 규칙표(rules.json) 와 대조 ==')
    changed = collections.OrderedDict()
    for g, new in derived.items():
        cur = KG.get(g, [])
        a, b = cover(cur), cover(new)
        if a == b:
            print('  일치   %-30s %d항목' % (g, len(new))); continue
        changed[g] = new
        print('  ** 다름 %-30s 현재 %d항목 → 약관 %d항목' % (g, len(cur), len(new)))
        if b[0] - a[0]: print('        빠진 코드 %d개 : %s' % (len(b[0] - a[0]), ' '.join(sorted(b[0] - a[0]))))
        if a[0] - b[0]: print('        약관에 없는 코드 : %s' % ' '.join(sorted(a[0] - b[0])))
        if b[1] ^ a[1]: print('        세분류 차이 : 약관에만 %s / 규칙표에만 %s' % (sorted(b[1] - a[1]), sorted(a[1] - b[1])))
        if b[2] ^ a[2]: print('        제외(!) 차이 : 약관 %s / 규칙표 %s' % (sorted(b[2]), sorted(a[2])))

    if '--write' in sys.argv and changed:
        for g, new in changed.items(): KG[g] = new
        json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\nrules.json 갱신 : %s' % ', '.join(changed))
    elif changed:
        print('\n(대조만 수행 — 반영하려면 --write)')
    else:
        print('\n모든 그룹이 약관과 일치')


if __name__ == '__main__':
    main()
