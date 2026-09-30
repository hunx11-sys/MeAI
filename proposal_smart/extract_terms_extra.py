# -*- coding: utf-8 -*-
"""스마트 제안서 전용 특약 마스터 보강 — 약관 PDF → db_terms_extra.json (v8.66)

영업지원도구(특약검색기 tool.html · 보상시뮬레이터 등)에는 넣지 않는다. db.json 은 tool.html 에서만 뽑으므로
그대로 두고, 이 파일은 matcher 가 db.json 과 함께 읽는다(소유자 지시 2026-09-30 : 내Mom대로·내Mom같은 어린이보험은
스마트 제안서 고도화·오류 제거 목적의 약관 파싱만).

  python extract_terms_extra.py "약관.pdf" 상품표시명 id접두어 [상품명패턴]   (여러 상품은 한 번씩 — 같은 상품은 교체)

scripts/import_terms.py(또또암 때 쓴 추출기)의 절단 규칙을 그대로 쓰고, 이 두 약관의 새 별표 표기를 다룬다.
  · 별표 표기 【별표-질병40(대장 양성종양및특정용종 분류표)】 — 번호가 '공통·상해·질병' 갈래별이라 **번호(갈래+숫자)로** 부록 표에 잇는다.
  · 세부보장(①②…)마다 제3조에서 자기 별표를 따로 가리킨다 → 세부 레코드는 **자기 구간의 별표 코드만**(없으면 부모 코드).
  · 수가코드(hc) : 연결된 별표·본문의 5자리 진료행위코드(scripts/add_hc_codes.py 와 같은 규칙).
  · 제외코드(x) : 별표 안 '(… 제외)' 괄호의 코드 + 특약 본문에서 '제외'가 들어간 문장의 괄호 코드. 그 밖의 추정은 하지 않는다.
원칙 : 코드는 약관 원문에서만 옮긴다. 표를 못 찾으면 k 를 비워 두고(계산 제외 + 로그) 목록에 남긴다.
"""
import io, json, os, re, sys, hashlib, collections
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, '..', 'scripts'))
import import_terms as IT                                   # build_lines · heading_blocks · title_norm · subs_of · category · NONKCD · JUNK
OUT = os.path.join(BASE, 'db_terms_extra.json')

HEAD = re.compile(r'\s*【\s*별\s*표\s*-?\s*([가-힣]*)\s*(\d+)\s*】\s*')
REF = re.compile(r'【\s*별\s*표\s*-?\s*([가-힣]*)\s*(\d+)\s*(?:[(（]((?:[^()（）】]|[(（][^()（）】]*[)）])*)[)）])?\s*】')
CODE = re.compile(r'(?<![A-Za-z0-9])([A-Z]\d{2}(?:\.\d{1,2})?)(?:\s*[~∼～]\s*([A-Z]?\d{2}(?:\.\d{1,2})?))?(?![0-9])')
HC = re.compile(r'\b([A-Z]{1,2}\d{3,4})\b(?:\s*[~∼]\s*([A-Z]{1,2}\d{3,4}))?')
GOJI = re.compile(r'\([^()]{1,24}가입\)')                    # 담보명 꼬리표 — scen_engine.GOJI 와 같은 형태
CIRC = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'

def nz(s): return re.sub(r'[\s ]', '', s or '')
JUNKSUB = re.compile(r'청구서|증명서|제출|회사양식|위생관리|성형수술|^\d+\.|[一-龥]|등의\s*조치|[「【“]|한다|이하|말한다|정한다')

def kcds(txt):
    """표·본문 텍스트 → (코드목록, 제외코드목록). '(… 제외)' 괄호 안 코드는 제외코드로."""
    t = re.sub(r'([A-Z]\d{2}\.)\s*\n\s*(\d)', r'\1\2', txt)          # 'C78.' + 줄바꿈 + '4'
    # 【○○ 예시】 블록(원발부위 기준 예시 등)의 코드는 설명용 — 다음 번호 항목·다음 【 까지 뺀다
    t = re.sub(r'【[^】]*예\s*시[^】]*】.*?(?=\n\s*\d+\.\s|\n\s*【|\Z)', ' ', t, flags=re.S)
    ex = []
    for m in re.finditer(r'[(（]([^()（）]{0,120}?)제외\s*[)）]', t):
        for a, b in CODE.findall(m.group(1)): ex.append(a + ('~' + (b if b[0].isalpha() else a[0] + b) if b else ''))
    t2 = re.sub(r'[(（][^()（）]{0,120}?제외\s*[)）]', ' ', t)
    # 표 머리글의 범위 안내 문장('다만, 다음의 상병 이외의 출생전후기 질병(P00~P96)은 포함되지 않습니다')은 대상 코드가 아니다
    t2 = re.sub(r'[^.。]{0,200}(?:포함되지\s*않|포함하지\s*않|보상하지\s*않|지급하지\s*않|해당하지\s*않|아니합니다|제외합니다|제외됩니다|출생전후기)[^.。]{0,60}[.。]', ' ', t2.replace('\n', ' '))
    k = []
    for a, b in CODE.findall(t2):
        c = a + ('~' + (b if b[0].isalpha() else a[0] + b) if b else '')
        if c not in k: k.append(c)
    return k, list(dict.fromkeys(ex))

def hcs(txt):
    out = []
    for a, b in HC.findall(txt or ''):
        if len(a) != 5: continue
        if b and len(b) == 5 and a[:-2] == b[:-2] and b[-2:].isdigit() and a[-2:].isdigit():
            for n in range(int(a[-2:]), int(b[-2:]) + 1): out.append(a[:-2] + '%02d' % n)
        else: out.append(a)
    return list(dict.fromkeys(out))

def appendix(lines, starts):
    """줄 단독의 【별표-갈래N】 제목부터 다음 제목(또는 다음 특약 시작)까지 표 하나.
       약관은 [본문][부록][갱신형 본문][부록]… 처럼 부록이 여러 번 온다 → 사이에 특약 시작이 끼면 다른 부록(구역)으로 나눈다.
       반환 : [(구역시작줄, 구역끝줄, {갈래N: [표…]})] (목차 줄은 제목 뒤에 점선·쪽번호가 붙어 제외된다)"""
    heads = [i for i, (pi, l) in enumerate(lines) if HEAD.fullmatch(l)]
    starts = sorted(starts); regions = []
    def next_start(i):
        for s in starts:
            if s > i: return s
        return len(lines)
    cur = None
    for n, i in enumerate(heads):
        if cur is None or next_start(cur['last']) < i:
            cur = {'a': i, 'last': i, 'tabs': {}}; regions.append(cur)
        cur['last'] = i
        m = HEAD.fullmatch(lines[i][1]); key = m.group(1) + m.group(2)
        j = min(heads[n + 1] if n + 1 < len(heads) else len(lines), next_start(i))
        name, k = [], i + 1
        while k < j and len(name) < 2:
            tt = lines[k][1].strip()
            if tt: name.append(tt)
            k += 1
            if name and re.search(r'(표|계산|비용|종류|목록)$', name[-1]): break
        txt = '\n'.join(l for _, l in lines[k:j])
        cur['tabs'].setdefault(key, []).append({'key': key, 'name': ' '.join(name), 'page': lines[i][0] + 1, 'text': txt})
        cur['b'] = j
    return [(r['a'], r['b'], r['tabs']) for r in regions]

def pick(tabs, key, name):
    c = tabs.get(key) or []
    if len(c) <= 1: return c[0] if c else None
    nn = nz(name).replace('분류표', '')
    for e in c:
        en = nz(e['name']).replace('분류표', '')
        if nn and en and (nn in en or en in nn): return e
    return c[0]

def is_kcd_table(e):
    return not any(x in nz(e['name']) for x in IT.NONKCD) and bool(kcds(e['text'])[0])

NEG = re.compile(r'제외|포함되지\s*않|보상하지\s*않|지급하지\s*않')
def refs_of(txt, tabs):
    """본문 → [(표, 문장)] (줄바꿈으로 끊긴 【별표\n-공통2(…)】 도 잇는다)"""
    flat = re.sub(r'\s*\n\s*', '', txt)
    out, seen = [], set()
    for sent in re.split(r'(?<=[다음])\.', flat):
        for m in REF.finditer(sent):
            e = pick(tabs, m.group(1) + m.group(2), m.group(3) or '')
            if e and (id(e), sent) not in seen: seen.add((id(e), sent)); out.append((e, sent))
    return out

def cover(pairs):
    """[(표, 문장)] → (대상 코드, 제외 코드, 쓴 표). 코드는 약관 표·문장 원문에서만.
       · 문장이 표를 가리키면서 코드를 직접 적었으면('…분류표 중 분류번호 C44') 그 코드만 대상
       · 문장에 제외·포함되지 않 등이 있으면 : 문장에 적힌 코드는 제외코드, 표는 '표 바로 뒤 30자 안에서 제외'면 표 전체가 제외
       · 그 밖은 표 전체가 대상"""
    k, x, used = [], [], []
    add = lambda L, cs: L.extend(c for c in cs if c not in L)
    for e, sent in pairs:
        if not is_kcd_table(e): continue
        s0 = REF.sub(' ', sent)
        sc = [a + ('~' + (b if b[0].isalpha() else a[0] + b) if b else '') for a, b in CODE.findall(s0)]
        tk, tx = kcds(e['text'])
        neg = NEG.search(sent)
        m = REF.search(sent); tail = sent[m.end():m.end() + 30] if m else ''
        if neg and not sc and NEG.search(tail) and '중' not in tail[:8]:
            add(x, tk)                                   # '【별표…】에 해당하는 질병은 제외'
        elif sc and not neg:
            add(k, sc)                                   # '…분류표 중 C44'
        else:
            add(k, tk); add(x, tx)
            if neg: add(x, sc)
        used.append(e)
    return k, x, used

def body_x(txt):
    """특약 본문의 '제외' 문장 괄호 코드 — 예) '… 질병(N08.3 제외)' · '기타피부암(C44) 및 갑상선암(C73)은 제외'"""
    ex = []
    flat = re.sub(r'\s*\n\s*', ' ', txt)
    for sent in re.split(r'(?<=다)\.\s', flat):
        if '제외' not in sent: continue
        for m in re.finditer(r'[(（]\s*([A-Z]\d{2}(?:\.\d{1,2})?(?:\s*[~∼～,]\s*[A-Z]?\d{2}(?:\.\d{1,2})?)*)\s*(?:제외)?\s*[)）]', sent):
            for a, b in CODE.findall(m.group(1)): ex.append(a + ('~' + (b if b[0].isalpha() else a[0] + b) if b else ''))
    return list(dict.fromkeys(ex))

def sub_chunks(body_lines, labels):
    """제3조(세부보장에 관한 사항)의 ①②… 구간 — 세부보장마다 [시작, 끝) 줄 위치. 못 찾으면 None"""
    pos = []
    for i, lab in enumerate(labels):
        c = CIRC[i] if i < len(CIRC) else None
        key = nz(lab)[:6]
        hits = [j for j, l in enumerate(body_lines) if c and l.strip().startswith(c) and key and key in nz(l)]
        pos.append(hits[-1] if hits else None)                # 제1조 목록이 아닌 제3조 본문(마지막으로 나오는 곳)
    if any(p is None for p in pos) or pos != sorted(pos): return None
    return [(p, pos[i + 1] if i + 1 < len(pos) else len(body_lines)) for i, p in enumerate(pos)]

# 특약 분류(c) — db.json categories 와 같은 id. import_terms.category 는 암보험용이라 '수술비·입원일당'을 암으로 보냈다(v8.66)
_CATS = [(r'통합치료비', 'integrated'), (r'유사암|암.*진단|진단.*암|전이암', 'cancer_dx'), (r'암.*(수술|입원|통원)', 'cancer_etc'), (r'암|항암|표적|면역|양성자|중입자|호르몬', 'cancer_tx'),
         (r'뇌|혈전', 'brain'), (r'심장|허혈|심근|부정맥|순환계', 'heart'), (r'신부전|신장', 'kidney'), (r'치매|장기요양', 'dementia'), (r'치아|임플란트', 'dental'),
         (r'자동차|운전|교통', 'driving'), (r'벌금|변호사|소송|법률', 'legal'), (r'배상', 'liability'), (r'화재|재물|가전', 'property'),
         (r'골절|화상|깁스', 'fracture'), (r'후유장해|장해', 'disability'), (r'사망', 'death'), (r'간병|간호', 'care'), (r'수술', 'surgery'), (r'입원|통원|응급', 'admission')]
def category(n):
    for p, c in _CATS:
        if re.search(p, n): return c
    return 'specific'

def tid(product, e): return 'X' + hashlib.md5((product + '|' + e['key'] + '|' + str(e['page'])).encode('utf-8')).hexdigest()[:10]

def parse(path, product, prefix):
    d = pymupdf.open(path); pages = [d[i].get_text() for i in range(len(d))]
    lines = IT.build_lines(pages)
    blocks = IT.heading_blocks(lines)
    regs = appendix(lines, [b['bstart'] for b in blocks])
    riders, log = [], []
    alltabs = {}
    for a, z, tb in regs:
        for kk, v in tb.items(): alltabs.setdefault(kk, []).extend(v)
    for bi, b in enumerate(blocks):
        if any(a <= b['bstart'] < z for a, z, _ in regs): continue          # 부록(별표) 안의 '제1조'는 특약이 아니다
        nxt = [r for r in regs if r[0] > b['bstart']]
        if not nxt: continue
        tabs, app_a = nxt[0][2], nxt[0][0]                                  # 이 특약 뒤에 오는 부록(같은 구역)
        title = IT.title_norm(b['title'])
        title = GOJI.sub('', title); title = re.sub(r'보장$', '', title).strip()
        if not title or len(title) > 70 or IT.JUNK.search(title) or re.search(r'다\.|^부터', title): continue
        end = min(blocks[bi + 1]['bstart'] if bi + 1 < len(blocks) else len(lines), app_a)
        body_lines = [l for _, l in lines[b['bstart']:end]]
        body = '\n'.join(body_lines)
        if '지급사유' not in body[:8000] and '보장의 범위' not in body[:3000]: continue
        P = refs_of(body, tabs)
        R = list({id(e): e for e, _ in P}.values())
        k, x, _u = cover(P)
        x += [c for c in body_x(body) if c not in x]
        hc = []
        for e in R:
            if '수술분류표' not in e['name'] and '산정특례' not in e['name']: hc += hcs(e['text'])
        hc = list(dict.fromkeys(hc + hcs(body)))
        rid = '%s%d' % (prefix, len([r for r in riders if not r.get('parent')]) + 1)
        r = {'id': rid, 'p': product, 'n': title, 'c': category(title), 'pg': b['page'] + 1, 'k': k, 'x': x,
             't': [tid(product, e) for e in R], 'hc': hc, 'src': [e['key'] + ' ' + e['name'] for e in R]}
        riders.append(r)
        if not k and not re.search(r'사망|후유장해|상해|골절|화상|입원일당|수술비\(1-|1-5종|1-7종|수술비Ⅱ|질병수술비|납입|지원금|배상|벌금|변호사|소송|치아', title):
            log.append(('KCD 없음', rid, title, r['src']))
        m_sub = re.search(r'총\s*(\d+)\s*개\s*(의)?\s*세부\s*보장', body)
        n_sub = int(m_sub.group(1)) if m_sub else 0
        if not n_sub: continue
        labels, how = IT.subs_of(body_lines, n_sub)
        if len(labels) != n_sub:
            log.append(('세부 개수 불일치 %d/%d' % (len(labels), n_sub), rid, title, labels[:6])); labels = labels[:n_sub]
        ch = sub_chunks(body_lines, labels) if how == 'enum' else None
        for i, lab in enumerate(labels, 1):
            lab = GOJI.sub('', lab).strip()
            if JUNKSUB.search(lab): continue                          # 보험금 청구서류 목록 등이 세부보장으로 잡힌 것
            lab = re.split(r'\s*:\s*|\s*보장\s*:', lab)[0].strip()      # '화상진단비보장 : 화상으로 진단확정시 …' → '화상진단비'
            lab = re.sub(r'보장$', '', lab).strip()
            sk, sx, st, shc, ssrc = k, x, r['t'], hc, r['src']
            if ch:
                seg = '\n'.join(body_lines[ch[i - 1][0]:ch[i - 1][1]])
                SP = refs_of(seg, tabs); SR = list({id(e): e for e, _ in SP}.values())
                a_, b_, u_ = cover(SP)
                if u_:
                    sk, sx = a_, b_
                    sx += [c for c in body_x(seg) if c not in sx]
                    st = [tid(product, e) for e in SR]; ssrc = [e['key'] + ' ' + e['name'] for e in SR]
                    shc = list(dict.fromkeys([h for e in SR if '수술분류표' not in e['name'] for h in hcs(e['text'])] + hcs(seg)))
            riders.append({'id': '%s-%d' % (rid, i), 'p': product, 'n': '%s[%s]' % (title, lab), 'c': category('%s[%s]' % (title, lab)) if r['c'] == category(title) else r['c'], 'pg': r['pg'],
                           'k': sk, 'x': sx, 't': st, 'hc': shc, 'src': ssrc, 'parent': rid})
    return riders, alltabs, log

def settle(riders):
    """감수(監修)된 특약 마스터(db.json)에 같은 이름 특약이 있으면 그 코드(k·x·hc)를 쓴다 — 메리츠 특약은 상품이 달라도
       같은 이름이면 같은 약관 조문·별표를 쓴다(원문 대조 : 같은 이름 668건 중 469건이 파싱 결과와 완전 일치, 나머지는
       파서의 한계 — 암종 구분 열이 있는 표·'분류표 중 C44' 같은 정의 조문). 마스터에 없는 특약만 파싱 코드를 쓰고 근거(별표)를 남긴다."""
    sys.path.insert(0, BASE)
    GJ = re.compile(r'\([^()]{1,24}가입\)')
    key = lambda n: re.sub(r'^갱신형', '', re.sub(r'\s', '', GJ.sub('', n or '')))
    db = json.load(open(os.path.join(BASE, 'db.json'), encoding='utf-8'))['riders']
    idx = collections.defaultdict(list)
    for r in db: idx[key(r['n'])].append(r)
    ex_idx = collections.defaultdict(list)                           # 먼저 추출한 다른 보강 상품(같은 약관 문구)의 파싱 결과 — KCD 를 못 뽑은 특약의 보조 근거
    if os.path.exists(OUT):
        for r in json.load(open(OUT, encoding='utf-8'))['riders']:
            if r.get('k') and r['p'] != (riders[0]['p'] if riders else ''): ex_idx[key(r['n'])].append(r)
    n_m = 0
    for r in riders:
        if not r['k'] and ex_idx.get(key(r['n'])):
            o = ex_idx[key(r['n'])][0]
            r.update(k=list(o['k']), x=list(o.get('x') or []), hc=list(o.get('hc') or r['hc']), src=o.get('src') or [])
            r['basis_from'] = '%s %s(같은 이름 특약 약관 p.%s)' % (o['p'], o['id'], o.get('pg'))
        c = idx.get(key(r['n']))
        if c:
            best = c[0]
            r.update(k=list(best.get('k') or []), x=list(best.get('x') or []), hc=list(best.get('hc') or []), c=best.get('c') or r['c'],
                     basis='마스터 %s(%s) 같은 이름 특약' % (best['id'], best['p']))
            n_m += 1
        else:
            r['basis'] = ('약관 p.%s 파싱 : %s' % (r['pg'], ' · '.join(r.get('src') or []) or '별표 없음')) + ((' · 코드는 ' + r.pop('basis_from')) if r.get('basis_from') else '')
    return n_m

if __name__ == '__main__':
    if len(sys.argv) < 4: sys.exit(__doc__)
    path, product, prefix = sys.argv[1:4]
    riders, tabs, log = parse(path, product, prefix)
    n_m = settle(riders)
    print('감수 마스터와 같은 이름 %d건은 마스터 코드 · 나머지 %d건은 약관 파싱 코드' % (n_m, len(riders) - n_m))
    db = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {'meta': {}, 'riders': []}
    db['riders'] = [r for r in db['riders'] if r['p'] != product] + riders
    db['meta'] = {'note': '스마트 제안서 전용 특약 마스터(영업지원도구 미반영) — extract_terms_extra.py 로 약관 PDF 에서 추출',
                  'products': sorted({r['p'] for r in db['riders']}), 'prodcount': dict(collections.Counter(r['p'] for r in db['riders'])),
                  'sources': dict((db.get('meta') or {}).get('sources') or {}, **{product: os.path.basename(path)})}
    json.dump(db, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    par = [r for r in riders if not r.get('parent')]
    print('%s : 특약 %d · 세부 %d · 별표 %d · KCD 보유 %d · 제외코드 보유 %d · 수가코드 보유 %d' % (
        product, len(par), len(riders) - len(par), sum(len(v) for v in tabs.values()), sum(1 for r in riders if r['k']),
        sum(1 for r in riders if r['x']), sum(1 for r in riders if r['hc'])))
    for x in log: print('  [%s] %s %s %s' % x)
