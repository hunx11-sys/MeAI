# -*- coding: utf-8 -*-
"""
새 상품 약관 PDF → 특약검색기(tool.html) 데이터 추가 (v8.12 · 또 걸려도 또 받는 암보험 2종)

  python3 scripts/import_terms.py "약관.pdf" 상품표시명 id접두어 [--write]

동작 (recover_terms.py 와 같은 절단 규칙)
  1) 특약 제목("2-1. ○○보장" 또는 "N. ○○ 특별약관") + 제1조 위치로 특약 본문을 자른다.
  2) 본문에서 【별표N(이름)】 참조를 찾고, 부록의 【별표N】 원문을 이름으로 연결해 질병코드(KCD)를 뽑는다.
     - 구분(암종) 열이 있는 표는 특약 본문의 "○○ 진단시" 목록(암종구분)을 어휘로 삼아 그룹별 코드로 나눈다.
     - 의약품명·수가코드·장해분류표·적립이율·소송비용 표는 KCD 표가 아니므로 코드에 쓰지 않는다.
  3) "총 N개 세부보장" 특약은 ①②… 목록 또는 암종구분 목록으로 세부 특약을 만든다(부모담보명[세부]).
  4) --write 가 있으면 tool.html DATA 에 특약·별표를 추가하고 상품 버튼을 붙인다. 없으면 결과만 출력.
원칙 : 코드는 약관 별표에서만 옮긴다. 표를 못 찾으면 k 는 비워 두고(계산 제외 + 로그) 목록에 남긴다.
"""
import io, json, os, re, sys, hashlib, collections
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
ROMAN = 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ'

# ── recover_terms.py 의 절단 함수 재사용(제목에 '특별약관'이 없는 "2-1. ○○ 보장" 형식도 허용) ──
_src = io.open(os.path.join(ROOT, 'scripts', 'recover_terms.py'), encoding='utf-8').read()
_funcs = _src[_src.index('def norm(s):'):_src.index('results = {}')]
_funcs = _funcs.replace("if not head or '특별약관' not in ''.join(head):",
                        "if not head or ('특별약관' not in ''.join(head) and not re.match(r'^\\d+-\\d+\\.', head[0])):")
_ns = {'re': re, 'ROMAN': ROMAN}; exec(_funcs, _ns)
norm, build_lines, heading_blocks, title_norm = _ns['norm'], _ns['build_lines'], _ns['heading_blocks'], _ns['title_norm']

CODE = re.compile(r'^[A-Z]\d{2}(\.\d{1,2})?$')
CODE_HEAD = re.compile(r'^[A-Z]\d{2}\.$')          # 'C78.' + 다음 줄 '4'  (줄바꿈으로 끊긴 코드)
NONKCD = ('장해', '의약품', '성분명', '수가코드', '진료행위', '적립이율', '소송', '인지액', '송달료', '자동차의 종류', '항구토제',
          '항암방사선치료 분류표', '항암약물 분류표', '신경차단', '용종제거수술', '장루', '수술분류표', '신의료기술치료', '말기간경화', '말기폐질환')
FALLBACK = {'다빈치로봇': ['암(특정암제외)', '특정암'], '표적항암약물허가치료비Ⅲ': ['특정표적항암약물허가치료', '특정면역항암약물허가치료'],
            '신의료기술치료비': ['1종 근골 및 하지정맥류질환', '2종 기타질환', '3종 로봇보조', '4종 여성 비뇨생식기질환']}
# 약관 제2절 2-1(암종별(30종)통합암진단비) 지급금액표의 암종구분 30개 — 표 파싱 어휘 보강용(원문 p.86~87)
LABELS30 = ['입술,혀 및 구강암', '주침샘,편도,인두 및 구강기타암', '특정소화기암Ⅱ', '위암', '결장암', '직장암', '간 및 간내 담관암', '췌장암',
            '특정호흡기 및 흉곽내기관의 암', '폐암', '뼈 및 관절연골암', '피부의 악성흑색종', '중피성 및 연조직암', '자궁체부 및 특정여성생식기암', '난소암',
            '특정남성생식기관암', '비뇨기관(신장,방광,요관) 암', '눈,뇌 및 중추신경계통의 기타부분의 암', '부신 및 기타내분비선암', '4대특정암', '호지킨림프종',
            '특정비호지킨림프종', '비소포성림프종', 'T/NK세포림프종', '악성면역증식성질환', '골수형성이상증후군', '골수증식성질환', '백혈병 및 전이암', '백혈병',
            '유방 및 전립선암', '외음,질 및 자궁경부암']
LABELS30 += [x + '(전이포함)' for x in LABELS30]
JUNK = re.compile(r'전자서명|이륜자동차|기타제도성|^자동갱신$|사업본부|양육연금|지정대리청구|특별조건부|장애인전용|납입유예|보장제한부인수|민사소송법률비용')

def nz(s): return re.sub(r'[\s ]', '', s)

def read_pdf(path):
    d = pymupdf.open(path)
    return [d[i].get_text() for i in range(len(d))]

# ── 부록 별표 ──
def parse_appendix(lines):
    """【별표N】 이 한 줄에 단독으로 있는 곳부터 다음 별표까지를 표 하나로. 이름은 다음 줄(들)."""
    heads = [i for i, (pi, l) in enumerate(lines) if re.fullmatch(r'\s*【\s*별표\s*\d+\s*】\s*', l)]
    tables = {}
    for n, i in enumerate(heads):
        j = heads[n + 1] if n + 1 < len(heads) else len(lines)
        # 이름 : 다음 비어있지 않은 줄, '1.' 또는 '약관에' 로 시작하는 본문 전까지 최대 3줄
        k = i + 1; name = []
        while k < j and len(name) < 3:
            t = lines[k][1].strip()
            if not t: k += 1; continue
            if re.match(r'^(1\.|약관에|이\s*표|※)', t): break
            name.append(t); k += 1
            if re.search(r'(표|계산|비용|인지액|송달료|성분명|종류)$', t): break
        nm = nz(''.join(name))
        if not nm or nm in tables: continue
        txt = '\n'.join(l for _, l in lines[k:j])
        tables[nm] = {'name': ' '.join(name), 'page': lines[i][0] + 1, 'text': txt}
    return tables

def find_table(tables, ref):
    if ref in tables: return ref
    r0 = ref.replace('분류표', '')
    for nm in tables:
        n0 = nm.replace('분류표', '')
        if r0 and n0 and (r0 == n0 or r0.startswith(n0) or n0.startswith(r0)): return nm
    return None

def code_lines(txt):
    """줄 목록에서 (index, code) — 'C78.' + '4' 처럼 끊긴 코드는 합친다"""
    ls = [l.strip() for l in txt.split('\n')]
    out = []; i = 0
    while i < len(ls):
        t = ls[i]
        if CODE.fullmatch(t): out.append((i, t))
        elif CODE_HEAD.fullmatch(t) and i + 1 < len(ls) and re.fullmatch(r'\d{1,2}', ls[i + 1]):
            out.append((i, t + ls[i + 1])); ls[i + 1] = ''
        i += 1
    return ls, out

def parse_rows(txt):
    """구분 열이 없는 표 : 코드 앞 줄(들)을 질병명으로"""
    ls, codes = code_lines(txt); rows = []; prev = -1
    for i, c in codes:
        lab = ' '.join(x for x in ls[prev + 1:i] if x and not re.match(r'^(구분|대\s*상\s*질\s*병|분류|번호)$', x))[-60:]
        rows.append({'label': lab.strip() or c, 'codes': [c]}); prev = i
    return rows

def parse_group_rows(txt, labels):
    """구분(암종) 열이 있는 표 : labels(특약 본문의 암종구분 어휘)로 그룹 경계를 잡는다"""
    vocab = {nz(x): x for x in labels}
    ls, codes = code_lines(txt); rows = []; prev = -1; cur = None
    for i, c in codes:
        seg = [x for x in ls[prev + 1:i] if x and not re.match(r'^(구분|대\s*상\s*질\s*병|분류|번호)$', x)]
        # 앞쪽 조각을 이어 붙여 어휘와 맞으면 그룹 라벨
        hit = None
        for st in range(len(seg)):
            for cut in range(len(seg), st, -1):
                cand = nz(''.join(seg[st:cut]))
                if cand in vocab: hit = (st, cut, vocab[cand]); break
            if hit: break
        if hit: cur = hit[2]; seg = seg[hit[1]:]
        rows.append({'label': ' '.join(seg).strip() or c, 'codes': [c], 'g': cur}); prev = i
    return rows

def table_id(product, name): return 'T' + hashlib.md5((product + '|' + name).encode('utf-8')).hexdigest()[:10]

# ── 특약 ──
CAT = [('통합치료비', 'integrated'), ('진단비', 'cancer_dx'), ('수술비', 'cancer_etc'), ('입원일당', 'cancer_etc'), ('통원일당', 'cancer_etc'),
       ('치료비', 'cancer_tx'), ('사망', 'death'), ('후유장해', 'disability'), ('검사비', 'cancer_tx'), ('보험료납입지원', 'etc'),
       ('생활비', 'cancer_tx'), ('생활지원비', 'cancer_tx'), ('호스피스', 'cancer_tx'), ('보존비', 'cancer_tx')]
def category(n):
    if '암' not in n and ('진단비' in n): return 'specific'
    for k, c in CAT:
        if k in n: return c
    return 'etc'

def subs_of(body_lines, n_sub):
    """세부보장 이름 : ①②… 열거(제1조 보장의 범위) 또는 '○○ 진단시' 암종구분 목록"""
    joined = '\n'.join(body_lines)
    enum = re.findall(r'^\s*[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]\s*(.+?)(?=\n\s*[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]|\n제\d+조|\n\s*$)', joined[:4000], re.M | re.S)
    enum = [re.sub(r'\s+', ' ', e).strip() for e in enum]
    enum = [re.sub(r'\((맞춤간편가입|통합간편가입|간편가입)\)$', '', e).strip() for e in enum if len(e) < 90]
    if n_sub and len(enum) >= n_sub: return enum[:n_sub], 'enum'
    # 암종구분 : "… 진단시" (여러 줄에 걸친 것은 이어 붙임)
    labs = []; buf = []; in_ex = False
    for l in body_lines:
        t = l.strip()
        if not t: continue
        if '【' in t: in_ex = True                          # 【보험금 지급예시 …】 안의 '… 진단시' 는 암종구분이 아니다
        if '】' in t: in_ex = False; buf = []; continue
        if in_ex: continue
        buf.append(t)
        if '진단시' in t:                                   # '… 진단시' / '… 진단시암종구분별' (붙어 나온 경우)
            buf[-1] = t.split('진단시')[0].strip()
            lab = ' '.join(x for x in buf[-3:] if x).strip()
            # 표 머리·금액 조각 제거
            lab = re.sub(r'.*(이후|이전|지급\)|지급금액|%)\s*', '', lab).strip()
            lab = re.sub(r'^[\s\-·•:：,.)]+', '', lab)
            if lab and lab not in labs and 2 <= len(lab) < 40 and '예시' not in lab: labs.append(lab)
            buf = []
        elif len(buf) > 3: buf = buf[-3:]
    return labs, 'dx'

def import_pdf(path, product, prefix):
    pages = read_pdf(path); lines = build_lines(pages)
    blocks = heading_blocks(lines)
    tables = parse_appendix(lines)
    riders = []; log = []
    for bi, b in enumerate(blocks):
        title = title_norm(b['title'])
        title = re.sub(r'\((맞춤간편가입|통합간편가입|간편가입)\)', '', title)
        title = re.sub(r'보장$', '', title).strip()
        if not title or len(title) > 60 or JUNK.search(title): continue
        end = blocks[bi + 1]['bstart'] if bi + 1 < len(blocks) else len(lines)
        body_lines = [l for _, l in lines[b['bstart']:end]]
        # 부록 시작에서 끊기
        for k, l in enumerate(body_lines):
            if re.fullmatch(r'\s*【\s*별표\s*\d+\s*】\s*', l): body_lines = body_lines[:k]; break
        body = '\n'.join(body_lines)
        if '지급사유' not in body[:6000] and '보장의 범위' not in body[:3000]: continue
        refs = [nz(m) for m in re.findall(r'【\s*별\s*표\s*\d+\s*[(（]([^】]+?)[)）]\s*】', body)]
        refs = list(dict.fromkeys(refs))
        refs = [find_table(tables, r) or r for r in refs]
        tids, k, l = [], [], []
        kcd_tabs = [r for r in refs if r in tables and not any(x in r for x in NONKCD) and len(code_lines(tables[r]['text'])[1]) >= 1]
        m_sub = re.search(r'총\s*(\d+)\s*개\s*(의)?\s*세부\s*보장', body)
        n_sub = int(m_sub.group(1)) if m_sub else 0
        sub_labels, how = subs_of(body_lines, n_sub) if n_sub else ([], None)
        if not n_sub:
            dx_labels, _ = subs_of(body_lines, 0)
            if len(dx_labels) >= 5 and any(r in tables and re.search(r'^\s*구분\s*$', tables[r]['text'], re.M) for r in refs):
                sub_labels, how, n_sub = dx_labels, 'dx', len(dx_labels)
        if n_sub and not sub_labels:                      # ①목록도 진단시 목록도 없는 세부보장 → 알려진 계열만
            for key, labs in FALLBACK.items():
                if key in title: sub_labels, how = labs[:n_sub], 'fallback'; break
        grouped = None
        for r in kcd_tabs:
            tb = tables[r]; tid = table_id(product, r)
            if 'rows' not in tb or (how == 'dx' and not any(row.get('g') for row in tb['rows']) and re.search(r'^\s*구분\s*$', tb['text'], re.M)):
                if n_sub and how == 'dx' and re.search(r'^\s*구분\s*$', tb['text'], re.M):
                    tb['rows'] = parse_group_rows(tb['text'], sub_labels + [x for x in LABELS30 if x not in sub_labels])
                    for row in tb['rows']:                    # 표에서 실제로 쓰인 그룹은 세부보장 목록에도 넣는다
                        if row.get('g') and row['g'] not in sub_labels: sub_labels.append(row['g'])
                else:
                    tb['rows'] = parse_rows(tb['text'])
            if any(row.get('g') for row in tb['rows']): grouped = tb
            for row in tb['rows']:
                for c in row['codes']:
                    if c not in k: k.append(c); l.append(row['label'])
            tids.append(tid)
        rid = '%s%d' % (prefix, len(riders) + 1)
        r = {'id': rid, 'p': product, 'n': title, 'c': category(title), 'pg': b['page'] + 1, 'b': body, 'k': k, 'l': l, 'x': [],
             't': tids, 's': [], 'st': '', 'src_tables': refs}
        riders.append(r)
        if not k and '사망' not in title and '후유장해' not in title:
            log.append(('KCD 표 없음', title, [(r, r in tables) for r in refs]))
        if n_sub:
            if len(sub_labels) != n_sub: log.append(('세부 개수 불일치 %d/%d' % (len(sub_labels), n_sub), title, sub_labels[:5]))
            for i, lab in enumerate(sub_labels, 1):
                sk, sl = k, l
                if grouped:
                    sk = [c for row in grouped['rows'] if row.get('g') == lab for c in row['codes']]
                    sl = [row['label'] for row in grouped['rows'] if row.get('g') == lab for c in row['codes']]
                    if not sk: log.append(('그룹 코드 없음', title + '[' + lab + ']', ''))
                s = dict(r); s.update({'id': '%s-%d' % (rid, i), 'n': '%s[%s]' % (title, lab), 'k': sk, 'l': sl, 'parent': rid})
                if grouped is None: s['cond'] = lab
                riders.append(s)
    used = {t for r in riders for t in r['t']}
    tabs = {table_id(product, nm): {'name': tb['name'], 'page': tb['page'], 'rows': tb.get('rows') or [], 'text': tb['text']}
            for nm, tb in tables.items() if table_id(product, nm) in used}
    return riders, tabs, log

if __name__ == '__main__':
    if len(sys.argv) < 4: sys.exit(__doc__)
    path, product, prefix = sys.argv[1:4]; write = '--write' in sys.argv
    riders, tabs, log = import_pdf(path, product, prefix)
    parents = [r for r in riders if not r.get('parent')]
    print('%s : 특약 %d (세부 %d) · 별표 %d · KCD 보유 %d' % (product, len(parents), len(riders) - len(parents), len(tabs), sum(1 for r in riders if r['k'])))
    for r in parents: print('  %-6s p%-4d %-56s k=%-3d t=%d%s' % (r['id'], r['pg'], r['n'][:56], len(r['k']), len(r['t']), '  세부 %d' % sum(1 for s in riders if s.get('parent') == r['id']) if any(s.get('parent') == r['id'] for s in riders) else ''))
    for x in log: print('  [%s] %s %s' % x)
    if write:
        html = io.open(TOOL, encoding='utf-8').read()
        m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', html, re.S)
        D = json.loads(m.group(2))
        D['riders'] = [r for r in D['riders'] if r['p'] != product]        # 같은 상품 재실행 시 교체
        for r in riders: r.pop('src_tables', None)
        D['riders'] += riders; D['tables'].update(tabs)
        if product not in D['meta']['products']: D['meta']['products'].append(product)
        D['meta']['total'] = len(D['riders']); D['meta']['prodcount'] = dict(collections.Counter(r['p'] for r in D['riders']))
        for c in D.get('categories', []):
            if isinstance(c, dict) and 'id' in c: c['count'] = sum(1 for r in D['riders'] if r.get('c') == c['id'])
        html = html[:m.start(2)] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):]
        btn = '<button data-p="%s">%s</button>' % (product, product)
        if btn not in html:
            html = html.replace('<button data-p="치아">치아</button>', '<button data-p="치아">치아</button>\n      ' + btn, 1)
        io.open(TOOL, 'w', encoding='utf-8').write(html)
        print('tool.html 반영 : 특약 %d · 별표 %d' % (len(D['riders']), len(D['tables'])))
