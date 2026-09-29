# -*- coding: utf-8 -*-
"""
또또암 · 또또암간편 분류표 복구와 특약 보장코드 재구성

무엇이 틀렸나
  약관 PDF 에서 표를 읽을 때 「질병명 줄 + 코드 줄」이 어긋나, 표 첫 줄의 코드(대개 C00~C14 같은
  구간 코드)가 이름 쪽에 붙어 사라졌다. 그 결과
    · 악성신생물(암) 분류표 : 21줄 → 8줄(C50·C97·D45·D46·D47.x 만 남음)
    · 통합암(유사암제외) 분류표 : C00~C14 · C74~C75 · C77~C80 빠짐
    · 산정특례대상 분류표 : C00~C97 · D00~D09 · D37~D48 빠짐
  이 표를 쓰는 암 특약 300여 개가 위암·폐암·대장암 등을 '보장 안 함'으로 보고 있었다.

어떻게 고치나 (코드는 약관에서만 온다)
  ① 표 : 같은 회사·같은 고시(제9차 KCD, 2025-299호) 판 표가 케어프리 약관에 정상으로 읽혀 있다.
         그 행을 가져오되 **또또암 약관 원문(text)에서 뽑은 코드 집합과 같을 때만** 쓴다.
  ② 특약 : 각 특약 약관의 지급사유(제1조·세부보장)에 적힌 대상 이름으로 범위를 정한다.
         「암」→ 분류표 전체 / 「암(유사암제외)」→ 전체 + 제외 C44·C73 /
         「암(특정암제외)」→ 제외 C73·C61 / 「계속암·재진단암(기타피부암,갑상선암,전립선암제외)」→ 제외 C44·C73·C61 /
         「기타피부암」C44 · 「갑상선암」C73 · 「유사암」C44·C73 · 「전립선암」C61 · 「소액암」(약관 제4조 열거)
         한 특약이 여러 대상을 따로 지급하면(예: 암(유사암제외) 100% + 기타피부암·갑상선암 20%) 합친다.
  ③ 세부보장 특약(부모[세부]) 은 세부 이름에 대상이 있으면 그것만, 없으면 부모를 따른다.
     통합암 세부(특정소액암·특정소화기암 …)는 분류표의 암구분 줄만 갖는다.

실행 : python3 scripts/fix_ttam.py [--write]
"""
import io, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from tooldata import inflate, deflate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
html = io.open(TOOL, encoding='utf-8').read()
m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', html, re.S)
D = inflate(json.loads(m.group(2)))
T, R = D['tables'], D['riders']
RM = {r['id']: r for r in R}
CN = D.get('codenames', {})

CODE = re.compile(r'(?<![A-Za-z0-9])([A-Z]\d{2}(?:\.\d{1,2})?)(?:\s*[∼~\-–]\s*([A-Z])?(\d{2}(?:\.\d{1,2})?))?(?![0-9])')


def expand(a, letter, b):
    if not b: return [a]
    L = a[0]
    if letter and letter != L: return [a]
    if '.' in a or '.' in b: return [a, (letter or L) + b]
    s, e = int(a[1:3]), int(b[:2])
    if e < s or e - s > 99: return [a]
    return ['%s%02d' % (L, i) for i in range(s, e + 1)]


def ex(codes):
    out = set()
    for c in codes:
        mm = CODE.match(c)
        if mm: out.update(expand(*mm.groups()))
    return out


def text_codes(txt):
    return {c for line in txt.split('\n') for mm in CODE.finditer(line) for c in expand(*mm.groups())}


# ── ① 표 복구 ─────────────────────────────────────────────
# (고칠 표, 본보기 표, 또또암 원문에 없는데 본보기에 있어도 되는 코드와 그 이유)
FIX_TABLES = [
    ('T68a1b462d8', 'bfb12825c6', set(), ''),
    ('T547a01a6dc', 'bfb12825c6', set(), ''),
    ('Tfb9e3690a1', 'aaef718384', set(), ''),
    # 또또암간편 통합암표의 4대고액암 블록(C23·C24·C25·C40·C41)은 PDF 쪽 순서 때문에
    # 바로 뒤 악성신생물 분류표(T547a01a6dc) 원문 끝에 붙어 있다 — 약관에 있는 코드다.
    ('T7a8500f794', 'aaef718384', {'C23', 'C24', 'C25', 'C40', 'C41'}, '4대고액암 블록이 이웃 표 원문에 붙어 있음'),
    ('Tfed5fb1387', '2bcaa7b45c', set(), ''),
    ('Tfcfb424836', '2bcaa7b45c', set(), ''),
]
if len(T['T68a1b462d8']['rows']) >= 21:
    sys.exit('이미 적용된 tool.html 입니다 (악성신생물 분류표 21줄). 원본에 다시 돌릴 때만 쓴다.')
OLD_ROWS = {}
for tid, src, allow, why in FIX_TABLES:
    own = text_codes(T[tid]['text'])
    rows = [dict(r) for r in T[src]['rows']]
    # 본보기 표 끝의 중복 줄(D33 두 번) 정리
    seen, uniq = set(), []
    for r in rows:
        key = tuple(r['codes'])
        if key in seen: continue
        seen.add(key); uniq.append(r)
    new = ex(c for r in uniq for c in r['codes'])
    lack = own - new
    extra = new - own - allow
    # 또또암간편 산정특례 원문에는 이웃 전이암 표의 C77·C79.x 가 섞여 있다 → 그건 표 밖 코드라 무시
    lack -= {c for c in lack if tid == 'Tfcfb424836' and c[:3] in ('C77', 'C79')}
    if lack or extra:
        sys.exit('표 %s : 약관 원문과 다름  원문에만 %s / 본보기에만 %s' % (tid, sorted(lack), sorted(extra)))
    OLD_ROWS[tid] = [c for r in T[tid]['rows'] for c in r['codes']]
    T[tid]['rows'] = uniq
    print('표 복구 %s %s : %d줄 → %d줄' % (tid, T[tid]['name'], len(OLD_ROWS[tid]), len(uniq)))

MAL = {'또또암': 'T68a1b462d8', '또또암간편': 'T547a01a6dc'}
ITG = {'또또암': 'Tfb9e3690a1', '또또암간편': 'T7a8500f794'}
SJT = {'또또암': 'Tfed5fb1387', '또또암간편': 'Tfcfb424836'}
BROKEN = set(OLD_ROWS)

# ── ② 지급대상 판정 ───────────────────────────────────────
SOAEK = None  # 소액암 : 약관 제4조가 열거 (C50·C53·C54·C61·C67) — 특약 원문에서 읽는다


def soaek_codes(b):
    f = re.sub(r'\s+', '', b)
    mm = re.search(r'「소액암」이라함은(.{0,400}?)이특별약관에서', f)
    if not mm: return None
    return set(re.findall(r'C\d\d', mm.group(1).split('분류번호', 1)[-1]))


def pay_text(r):
    f = re.sub(r'\s+', '', r['b'])
    # 지급사유는 '세부규정' 또는 '…의 정의' 조문 앞까지. 세부보장형은 그런 조문이 없어 끝까지 읽되
    # 정의 문장(「X」이라 함은 … 말합니다)은 지운다 — 정의만 있고 지급하지 않는 대상이 섞이지 않게
    mm = re.search(r'제\d+조\((?:보험금지급에관한세부규정|.{0,40}?정의)', f)
    f = f[:mm.start()] if mm else f
    return re.sub(r'(?:이|이상의)?특별약관에(?:서|있어서?)「[^」]+」(?:이)?라함은.*?(?:말합니다|총칭합니다)\.', '', f)


def decide(s, b):
    """s : 지급사유 문구(공백 없음). → (전체 쓰나, 제외코드 교집합, 개별코드)"""
    alls, spec, only = [], set(), None
    s = s.replace('암(유사임제외)', '암(유사암제외)')          # 약관 오탈자(또또암간편 세기조절)
    rules = [
        (r'암\(유사암및소액암제외\)', ('A', {'C44', 'C73'})),
        # 계속암·재진단암은 그 자체가 지급대상이다. 같은 문단의 「암(유사암제외)」(=첫번째암)는 대기기간 기준일 뿐
        (r'(?:계속암|재진단암)\(기타피부암,갑상선암,전립선암제외\)', ('O', {'C44', 'C73', 'C61'})),
        (r'재발암및잔여암\(기타피부암,갑상선암제외\)', ('O', {'C44', 'C73'})),
        (r'암\(특정암제외\)', ('A', {'C73', 'C61'})),
        (r'통합암\(유사암제외\)', None),
        (r'암\(유사암제외\)', ('A', {'C44', 'C73'})),
        (r'암진단비\(유사암제외\)', ('A', {'C44', 'C73'})),
        (r'\(유사암(?:및소액암)?제외\)', None),          # '암수술비(유사암제외)' 같은 담보명 꼬리 — 유사암 지급 아님
        (r'「특정암」|^\[특정암\]', ('S', {'C73', 'C61'})),
        (r'(?<!특정)소액암', ('S', 'SOAEK')),
        (r'원격전이포함4기기타피부암및갑상선암', ('S', {'C44', 'C73'})),
        (r'기타피부암', ('S', {'C44'})),
        (r'갑상선암', ('S', {'C73'})),
        (r'유사암', ('S', {'C44', 'C73'})),
        (r'전립선암', ('S', {'C61'})),
        (r'「암」', ('A', set())),
    ]
    for pat, act in rules:
        if re.search(pat, s):
            s = re.sub(pat, '', s)
            if not act: continue
            kind, v = act
            if v == 'SOAEK':
                v = soaek_codes(b) or set()
                if not v: raise SystemExit('소액암 정의를 약관에서 못 읽음 : ' + b[:40])
            if kind == 'O': only = v
            else: (alls.append(v) if kind == 'A' else spec.update(v))
    if only is not None: return (True, only, set())
    if not alls and not spec: return None
    excl = set.intersection(*alls) - spec if alls else set()
    return (bool(alls), excl, spec)


def sub_part(r):
    P = RM[r['parent']]
    n = re.sub(r'\s+', '', r['n'])
    return n[len(re.sub(r'\s+', '', P['n'])):] if n.startswith(re.sub(r'\s+', '', P['n'])) else n


def decide_section(r):
    """세부 이름에 대상이 없으면(예: [암후유장해(3-100%)]) 부모 약관에서 그 세부보장 문단을 찾아 읽는다"""
    nm = re.sub(r'\(맞춤간편가입\)', '', sub_part(r)).strip('[]')
    nm = re.sub(r'^.*\[', '', nm).rstrip(']')
    f = pay_text(RM[r['parent']])
    hits = list(re.finditer(re.escape(nm), f))
    # 세부보장 조문(「①○○[세부]1.(보험금의지급사유)…」)이 있으면 그것을 먼저 읽는다 — 앞의 목록(제1조)은 이름뿐
    hits.sort(key=lambda mm: 0 if '보험금의지급사유' in f[mm.end():mm.end() + 30] else 1)
    for mm in hits:
        if re.match(r'\]*(?:\(맞춤간편가입\))?\]*(?:[②③④⑤⑥⑦⑧⑨⑩]|제\d+조)', f[mm.end():]): continue
        seg = f[mm.start():]
        nx = re.search(r'[②③④⑤⑥⑦⑧⑨⑩]', seg[len(nm):])
        seg = seg[:len(nm) + (nx.start() if nx else 1500)]
        if '지급' in seg and len(seg) > len(nm) + 40:
            d = decide(seg[len(nm):], RM[r['parent']]['b'])
            if d: return d
    return None


DEC = {}


def decision(r):
    if r['id'] in DEC: return DEC[r['id']]
    d = None
    if r.get('parent'):
        d = decide(sub_part(r), r['b'])
        if d is None: d = decide_section(r)
        if d is None and ITG[r['p']] not in r['t']: d = decision(RM[r['parent']])
    else:
        d = decide(pay_text(r), r['b'])
    DEC[r['id']] = d
    return d


GROUPS = ['특정소액암', '특정소화기암', '15대특정암', '10대특정암', '4대고액암']

# 약관이 대상 이름 대신 '산정특례 대상 암'으로 정한 특약 : 중증질환자(암) 산정특례 = C00~C97 전체
FORCE_ALL = {'또86'}

aff = [r for r in R if r['p'] in MAL and set(r.get('t', [])) & BROKEN]
report = []
for r in aff:
    p = r['p']
    old_k, old_l, old_x = list(r['k']), list(r.get('l', [])), list(r.get('x', []))
    aligned = len(old_k) == len(old_l)
    other = set()
    for t in r['t']:
        if t not in BROKEN: other |= ex(c for row in T[t].get('rows', []) for c in row['codes'])
    broken_old = set()
    for t in r['t']:
        if t in BROKEN: broken_old |= set(OLD_ROWS[t])
    keep = [(c, old_l[i] if aligned else None) for i, c in enumerate(old_k)
            if not (c in broken_old and not (ex([c]) & other))]
    pos = next((i for i, c in enumerate(old_k) if c in broken_old), len(old_k))
    pos = sum(1 for c in old_k[:pos] if not (c in broken_old and not (ex([c]) & other)))

    add = []   # (code, label)
    xs = set(old_x)
    note = ''
    # 통합암 분류표
    if ITG[p] in r['t']:
        rows = T[ITG[p]]['rows']
        if r.get('parent'):
            sp = sub_part(r)
            g = next((g for g in GROUPS if g in sp), None)
            if g: rows = [x for x in rows if x.get('g') == g]
            else: rows = []
        add += [(c, x['label']) for x in rows for c in x['codes']]
    # 악성신생물 분류표
    if MAL[p] in r['t']:
        d = decision(r) if r['id'] not in FORCE_ALL and r.get('parent') not in FORCE_ALL else (True, set(), set())
        if d is None and r.get('parent') and ITG[p] in r['t']: d = (False, set(), set())   # 통합암 세부 : 악성표 몫 없음
        if ITG[p] in r['t'] and d and d[0]:
            d = (False, set(), d[2])      # 통합암 특약의 '암' 범위는 통합암 분류표가 정한다
        if d is None:
            note = '지급대상 이름을 못 찾음 → 분류표 전체(제외 없음)로 둠'
            d = (True, set(), set())
        use_all, excl, spec = d
        if use_all:
            add += [(c, x['label']) for x in T[MAL[p]]['rows'] for c in x['codes']]
            xs |= excl
        else:
            add += [(c, CN.get(c, '')) for c in sorted(spec)]
    # 산정특례 분류표
    if SJT[p] in r['t']:
        add += [(c, x['label']) for x in T[SJT[p]]['rows'] for c in x['codes']]
    have = {c for c, _ in keep}
    ins = []
    for c, l in add:
        if c in have: continue
        have.add(c); ins.append((c, l))
    new = keep[:pos] + ins + keep[pos:]
    r['k'] = [c for c, _ in new]
    if aligned: r['l'] = [l or CN.get(c, '') for c, l in new]
    r['x'] = sorted(xs)
    a, b = ex(old_k), ex(r['k'])
    report.append((r['id'], r['n'], len(b - a), sorted(a - b)[:10], r['x'], note))

for rid, n, plus, minus, x, note in report:
    print('%-9s +%-3d -%-22s x=%-18s %s %s' % (rid, plus, ','.join(minus), ','.join(x), n[:50], note))
print('특약', len(report))

# ── ③ 개별 보정 (약관 PDF 원문 대조) ─────────────────────────
def organ_rows(txt):
    """기관(organ)분류표 : '번호. 기관명' 뒤에 오는 분류번호 줄을 모은다. C81-C96 은 구간, (C26.1제외)는 제외표시"""
    rows, cur = [], None
    for ln in txt.split('\n'):
        s = ln.strip()
        mm = re.match(r'^(\d{1,2})\.\s*(.*)', s)
        if mm and 1 <= int(mm.group(1)) <= 49 and not re.match(r'^\d+\.\s*(약관|진단)', s):
            cur = {'label': mm.group(2), 'codes': [], 'n': int(mm.group(1))}; rows.append(cur); continue
        if cur is None: continue
        if re.match(r'^(주\d\)|구분|2\.\s)', s): cur = None; continue
        if re.match(r'^[(A-Z]', s) and re.search(r'[A-Z]\d\d', s):
            for part in re.findall(r'\(?[A-Z]\d\d(?:\.\d+)?(?:-[A-Z]\d\d)?(?:제\s*외)?\)?', s):
                if '제' in part or part.startswith('('):
                    cur.setdefault('excl', []).append(re.sub(r'[()제외\s]', '', part))
                else:
                    cur['codes'].append(part.replace('-', '~'))
        elif not cur['codes']:
            cur['label'] += ' ' + s
    return rows


def fix_individual():
    out = []
    # (a) 기관(organ)분류표 49줄 재구성 (또또암 p.539~541)
    tid = 'T75feeb29ec'
    rows = organ_rows(T[tid]['text'])
    got = sorted({r['n'] for r in rows})
    if got != list(range(1, 50)): sys.exit('기관분류표 번호가 1~49 가 아님 : %s' % got)
    T[tid]['rows'] = [{'label': re.sub(r'\s+', ' ', r['label']).strip(), 'codes': r['codes'],
                       **({'excl': r['excl']} if r.get('excl') else {})} for r in sorted(rows, key=lambda r: r['n'])]
    out.append('기관(organ)분류표 39줄(뒤섞임) → 49줄')
    # (b) 갑상선암및기타피부암의전이암(림프절등전이제외)진단비
    #     「갑상선암」C73·「기타피부암」C44 진단 뒤, 다른 기관으로 전이된 암(이차성 C78·C79, 부위불명 C80)
    #     — 림프절 전이(C77)는 담보명에서 제외. 통합간편 같은 담보(통65)와 같은 판정
    for rid in ('또71',):
        r = RM[rid]
        r['k'] = ['C44', 'C73', 'C78', 'C79', 'C80']
        r['l'] = [CN.get(c, '') for c in r['k']]
        r['x'] = ['C77']
        out.append('%s %s → C44·C73·C78·C79·C80 (제외 C77)' % (rid, r['n']))
    # (c) 말기폐질환 분류표 (p.558) — 표 행이 0줄. 원문 코드와 같은 케어프리 표 행을 쓴다
    tid, src = 'T8722aab64d', '17150dba4d'
    own = {c for c in text_codes(T[tid]['text']) if not c.startswith('P')}   # 출생전후기(P00~P96)는 '포함하지 않는다'는 문장
    new = ex(c for x in T[src]['rows'] for c in x['codes'])
    if own != new: sys.exit('말기폐질환 표가 원문과 다름 %s' % sorted(own ^ new))
    T[tid]['rows'] = [dict(x) for x in T[src]['rows']]
    for r in R:
        if tid in r.get('t', []):
            r['k'] = [c for x in T[tid]['rows'] for c in x['codes']]
            r['l'] = [x['label'] for x in T[tid]['rows'] for c in x['codes']]
            out.append('%s %s → 말기폐질환 코드 %d개' % (r['id'], r['n'], len(r['k'])))
    # (d) 말기신부전증진단비 — 약관 제3조가 'N18(만성콩팥병)' 을 직접 적음
    for r in R:
        if r['p'] in MAL and re.sub(r'\s', '', r['n']) == '말기신부전증진단비' and not r['k']:
            if 'N18' not in re.sub(r'\s', '', r['b']): sys.exit('말기신부전 N18 근거 없음')
            r['k'], r['l'] = ['N18'], [CN.get('N18', '만성 콩팥병')]
            out.append('%s %s → N18 (약관 제3조)' % (r['id'], r['n']))
    # (e) 암전후관련 특정질환 및 양성신생물 분류표 (p.578~580)
    #     줄 끝에 붙은 코드(B17.0·N87.2·D35.6)와 별표 기호(G02.1*·I39.8*)를 놓쳤고,
    #     p.580 의 양성신생물(식도·위…·간,폐·중추신경계) 블록은 이웃 별표48(표적항암제) 원문으로 넘어가 있었다.
    tid = 'T9c2455597b'
    ADD = [('만성 B형간염에서의 급성 델타(중복)감염', 'B17.0'), ('칸디다수막염', 'G02.1'), ('칸디다심내막염', 'I39.8'),
           ('달리 분류되지 않은 중증 자궁경부이형성', 'N87.2'), ('대동맥소체및기타부신경절의 양성신생물', 'D35.6'),
           ('식도의 양성 신생물', 'D13.0'), ('위의 양성신생물', 'D13.1'), ('십이지장의 양성 신생물', 'D13.2'),
           ('기타 및 상세불명 부분 소장의 양성 신생물', 'D13.3'), ('부위불명의 소화계통의 양성 신생물', 'D13.9'),
           ('췌장의 양성 신생물', 'D13.6'), ('내분비췌장의 양성 신생물', 'D13.7'), ('중이 및 호흡계통의 양성 신생물', 'D14'),
           ('간의 양성신생물', 'D13.4'), ('간외담관의 양성 신생물', 'D13.5'), ('수막의 양성신생물', 'D32'),
           ('뇌 및 중추신경계통의 기타 부분의 양성 신생물', 'D33'), ('뇌하수체의 양성 신생물', 'D35.2'),
           ('두개인두관의 양성 신생물', 'D35.3'), ('송과선의 양성 신생물', 'D35.4'), ('심장의 양성신생물', 'D15.1')]
    src_txt = re.sub(r'\s+', '', T[tid]['text'] + T['T1b08eb2a69']['text'])
    have = ex(c for x in T[tid]['rows'] for c in x['codes'])
    added = []
    for lab, c in ADD:
        if c in have: continue
        if c not in src_txt: sys.exit('암전후 %s 가 약관 원문에 없음' % c)
        T[tid]['rows'].append({'label': lab, 'codes': [c]}); added.append((c, lab))
    for r in R:
        if tid in r.get('t', []):
            for c, lab in added:
                if c not in r['k']:
                    r['k'].append(c)
                    if len(r.get('l', [])) == len(r['k']) - 1: r['l'].append(lab)
            out.append('%s %s → 코드 %d개 추가 %s' % (r['id'], r['n'], len(added), ','.join(c for c, _ in added)))
    # (f) 암종별(13종)통합암(전이포함) 분류표 — 26종항암방사선및약물치료비(전이포함)(유사암제외)
    #     또또암 p.547 : 「후복막 및 복막의 이차성 악성 C78.6」 이 한 줄에 붙어 C78.6 을 놓침
    #     또또암간편 p.469~470 : 표 뒷부분(C79.2~C77)이 이웃 산정특례 분류표 원문으로 넘어가 빠짐
    FIX13 = {'T94abda0734': [('후복막 및 복막의 이차성 악성 신생물', 'C78.6')],
             'Tacbc9a1b50': [('피부의 이차성 악성 신생물', 'C79.2'), ('골 및 골수의 이차성 악성 신생물', 'C79.5'),
                             ('부신의 이차성 악성 신생물', 'C79.7'), ('기타 명시된 부위의 이차성 악성 신생물', 'C79.88'),
                             ('상세불명 부위의 이차성 악성 신생물', 'C79.9'), ('림프절의 이차성 및 상세불명의 악성 신생물', 'C77')]}
    for tid, adds in FIX13.items():
        near = re.sub(r'\s+', '', T[tid]['text'] + T['Tfcfb424836']['text'])
        have = ex(c for x in T[tid]['rows'] for c in x['codes'])
        added = []
        for lab, c in adds:
            if c in have: continue
            if c not in near: sys.exit('%s %s 약관 원문 없음' % (tid, c))
            T[tid]['rows'].append({'label': lab, 'codes': [c]}); added.append((c, lab))
        for r in R:
            if tid in r.get('t', []):
                for c, lab in added:
                    if c not in r['k']:
                        r['k'].append(c)
                        if len(r.get('l', [])) == len(r['k']) - 1: r['l'].append(lab)
                out.append('%s %s → %s 추가' % (r['id'], r['n'], ','.join(c for c, _ in added)))
    # (g) 항암방사선치료후5대중증합병증 분류표 (p.549) — 폐렴 항목 괄호 속 별표(*) 코드 J17.1·J17.2·J17.3 을 놓침
    #     (같은 표의 짝 코드 B25.0·B05.2·B01.2·B58.3·B48.5 는 이미 있음. 암전후 표와 같은 기준으로 넣는다)
    tid = 'T6f80468d74'
    adds = [('달리 분류된 바이러스질환에서의 폐렴', 'J17.1'), ('달리 분류된 진균증에서의 폐렴', 'J17.2'),
            ('달리 분류된 기생충증에서의 폐렴', 'J17.3')]
    have = ex(c for x in T[tid]['rows'] for c in x['codes'])
    added = []
    for lab, c in adds:
        if c in have: continue
        if c + '*' not in re.sub(r'\s+', '', T[tid]['text']): sys.exit('%s 원문 없음' % c)
        T[tid]['rows'].append({'label': CN.get(c, lab), 'codes': [c]}); added.append((c, CN.get(c, lab)))
    for r in R:
        if tid in r.get('t', []):
            for c, lab in added:
                if c not in r['k']:
                    r['k'].append(c)
                    if len(r.get('l', [])) == len(r['k']) - 1: r['l'].append(lab)
            if added: out.append('%s %s → %s 추가' % (r['id'], r['n'], ','.join(c for c, _ in added)))
    # (h) 원격전이포함4기통합암진단비(유사암제외) — 연결된 분류표·코드가 하나도 없었다.
    #     약관 제2조 표가 【별표3(통합암(유사암제외)분류표)의 특정소액암】… 을 직접 가리킨다 → 그 표, 세부는 암구분 줄
    for r in R:
        if r['p'] in ITG and re.sub(r'\s', '', r['n']).startswith('원격전이포함4기통합암진단비(유사암제외)') and not r['k']:
            if '별표3(통합암(유사암제외)분류표)' not in re.sub(r'\s', '', r['b']): sys.exit('%s 별표3 근거 없음' % r['id'])
            rows = T[ITG[r['p']]]['rows']
            if r.get('parent'):
                g = next((g for g in GROUPS if g in re.sub(r'\s', '', sub_part(r))), None)
                if not g: sys.exit('%s 암구분 못 찾음' % r['id'])
                rows = [x for x in rows if x.get('g') == g]
            r['t'] = [ITG[r['p']]]
            r['k'] = [c for x in rows for c in x['codes']]
            r['l'] = [x['label'] for x in rows for c in x['codes']]
            out.append('%s %s → 통합암 분류표 코드 %d개' % (r['id'], r['n'], len(r['k'])))
    return out


for line in fix_individual(): print('개별 :', line)

if '--write' in sys.argv:
    body = json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':'))
    html = html[:m.start(2)] + body + html[m.end(2):]
    io.open(TOOL, 'w', encoding='utf-8').write(html)
    print('tool.html 저장')
