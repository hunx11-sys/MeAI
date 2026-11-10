# -*- coding: utf-8 -*-
"""세부보장이 빠진 특약에 세부보장 레코드를 채운다 (v8.90 · 2026-11-09)

정보계 담보코드는 세부보장(32대질병관혈수술비의 5대 · 9대 · 14대 · 4대질병, 다빈치로봇 암수술비의 특정암 · 암(특정암제외) 등)마다
따로 붙는다. 우리 마스터는 통합간편처럼 세부보장을 나눈 상품도 있고, 같은 특약인데 특약 하나로만 둔 상품도 있었다
(케어프리 감수본 · 약관 파싱 보강 마스터 — 약관이 「총 N개의 세부보장」 문구 없이 지급표로만 나누면 추출기가 세부보장을 못 만든다).

채우는 규칙 — 추정하지 않는다
  1. 같은 특약(이름 열쇠가 같은 특약 · 갱신형 · 가입 꼬리표 · 무감액 꼬리표 · 띄어쓰기는 뗀다)이 다른 상품에서 세부보장으로 나뉘어 있고
  2. 이 특약의 약관 본문에 그 세부보장 이름이 모두 나올 때만 같은 세부보장을 붙인다(본문이 없으면 붙이지 않는다).
  3. 질병코드 · 제외코드 · 수가코드는 본보기 세부보장의 것(감수본 우선)을 쓰되, 이 특약 자신의 코드 안에 들어 있을 때만 쓴다.
     안 들어 있으면 이 특약 자신의 코드를 그대로 물려준다(이름이 같으면 약관 별표도 같다 · 코드를 새로 만들지 않는다).
     감수본 본보기에서 다른 세부보장에는 코드가 있는데 그 세부보장만 비어 있으면(약관이 별표 대신 정의 조문으로 정한 것 — 중증화상및부식진단비 :
     체표면적 20% 이상 3도 화상 · 부식) 코드 없이 둔다(v8.92 · 금액이 아니라 빈칸).
  4. 세부보장이 일부만 있으면(있는 것이 본보기의 일부일 때만) 빠진 세부보장만 채운다(v8.92).
쓰는 곳 : scripts/fill_sub_riders.py(영업지원도구 tool.html) · extract_terms_extra.py(보강 마스터 · 약관 추출 때마다)
"""
import re, collections

GOJI_ = re.compile(r'\([^()]{1,24}가입\)')
MUGAM = re.compile(r'\((?:감액및면책기간미적용|감액기간미적용|면책기간미적용)\)')
nz = lambda s: re.sub(r'\s', '', s or '')


def fam(n):
    """같은 특약을 찾는 이름 열쇠"""
    return MUGAM.sub('', re.sub(r'^(\(\d+년갱신\))?갱신형', '', GOJI_.sub('', nz(n))))


def _label(parent, kid):
    """본보기 세부보장 이름에서 세부 라벨과 끼우는 방법 → ('bracket', 라벨) | ('insert', (앞부분, 끼울 글자)) | None"""
    p, k = nz(parent), nz(kid)
    if k.startswith(p + '[') and k.endswith(']'):
        return 'bracket', k[len(p) + 1:-1]
    i = 0
    while i < min(len(p), len(k)) and p[i] == k[i]: i += 1
    j = 0
    while j < min(len(p), len(k)) - i and p[-1 - j] == k[-1 - j]: j += 1
    if i + j == len(p) and len(k) > len(p):                      # k = p[:i] + 끼운 글자 + p[i:]
        return 'insert', (p[:i], k[i:len(k) - j])
    return None


def _core(lab):
    """약관 본문에서 찾을 라벨 알맹이 — 꼬리표 · 끝의 비/진단비 · 괄호를 뗀다"""
    t = MUGAM.sub('', GOJI_.sub('', nz(lab)))
    t = re.sub(r'(진단비|수술비|치료비|비)$', '', re.sub(r'\(최초1회한\)|\(연간1회한\)', '', t))
    t = t.replace(')(', '').strip('()')
    return t


_RG = re.compile(r'^([A-Z])(\d{2})(?:\.(\d+))?~([A-Z])(\d{2})(?:\.(\d+))?$')
def _pt(c):
    m = re.match(r'^([A-Z])(\d{2})(?:\.(\d+))?', c)
    return (m.group(1), int(m.group(2)), m.group(3) or '') if m else None
def _covers(e, c):
    """이 특약 코드 한 줄 e 가 세부 코드 c 를 포함하는가(개별 · 세분류 · 범위 A15~A19)"""
    e = e.strip(); c = c.strip()
    if e.startswith('!') or c.startswith('!'): return e == c
    if e == c or c.startswith(e + '.'): return True
    m = _RG.match(e)
    if m:
        lo, hi = (m.group(1), int(m.group(2))), (m.group(4), int(m.group(5)))
        rc = _RG.match(c); pts = [c.split('~')[0], c.split('~')[1]] if rc else [c]
        for q in pts:
            t = _pt(q)
            if not t or not (lo[0] == t[0] == hi[0] and lo[1] <= t[1] <= hi[1]): return False
        return True
    return False
def covered(sub, whole):
    """세부 코드 중 이 특약 코드(별표)에도 있는 것만 — 둘 다에 있는 코드만 쓴다(코드를 새로 만들지 않는다)"""
    return [c for c in sub if any(_covers(e, c) for e in whole)]


def plan(riders, templates, body_of):
    """riders : 채울 대상(dict · id p n k x hc c parent) · templates : 본보기 후보(같은 모양 · 세부보장 포함)
       body_of(r) → 약관 본문 글자(없으면 '') · 반환 [(부모, [새 세부 dict]), …], 로그"""
    for t in list(templates) + list(riders):                 # db.json 은 parent 를 싣지 않는다 — 번호(통55-1 → 통55)로 되살린다
        if not t.get('parent') and re.match(r'^[^-]+-\d+$', t['id']): t['parent'] = t['id'].rsplit('-', 1)[0]
    kids = collections.defaultdict(list)
    for t in templates:
        if t.get('parent'): kids[(t['p'], t['parent'])].append(t)
    have = collections.defaultdict(list)                     # 이 특약에 이미 있는 세부보장
    for r in riders:
        if r.get('parent'): have[(r['p'], r['parent'])].append(r)
    tidx = collections.defaultdict(list)
    for t in templates:
        ks = kids.get((t['p'], t['id']))
        if ks and not t.get('parent'): tidx[fam(t['n'])].append((t, sorted(ks, key=lambda x: x['id'])))
    out, log = [], []
    for r in riders:
        if r.get('parent'): continue
        ex = have.get((r['p'], r['id'])) or []                  # 세부보장이 일부만 있으면 빠진 것만 채운다(v8.92 · 신화상치료비 [중증화상및부식진단비])
        exl = [_label(r['n'], k['n']) for k in ex]
        if ex and any(l is None for l in exl): continue
        exc = {_core(l[1] if l[0] == 'bracket' else l[1][1]) for l in exl}
        nxt = max([int(k['id'].rsplit('-', 1)[1]) for k in ex if re.match(r'.*-\d+$', k['id'])] or [0]) + 1
        cands = tidx.get(fam(r['n']))
        if not cands: continue
        cands = sorted(cands, key=lambda c: (c[0].get('src') != 'db', c[0]['p'] == r['p']))   # 감수본(db) 본보기 먼저
        body = nz(body_of(r))
        if not body:
            log.append(('본문 없음 — 세부보장 안 붙임', r['p'], r['id'], r['n'])); continue
        done = False
        for tp, tks in cands:
            labs = [_label(tp['n'], k['n']) for k in tks]
            if any(l is None for l in labs): continue
            cores = [_core(l[1] if l[0] == 'bracket' else l[1][1]) for l in labs]
            if ex and not (exc < set(cores)): continue           # 있는 세부보장이 본보기의 일부일 때만(이름이 다르면 손대지 않는다)
            sib = any(t.get('k') for t in tks)                     # 본보기 세부보장 중 코드가 있는 것이 있는가
            pick = [i for i, c in enumerate(cores) if c not in exc]
            tks, labs, cores = [tks[i] for i in pick], [labs[i] for i in pick], [cores[i] for i in pick]
            miss = [c for c in cores if c and c not in body]
            if miss:
                log.append(('약관 본문에 세부보장 이름 없음 %s' % miss, r['p'], r['id'], r['n'])); continue
            new = []
            for i, (k, l) in enumerate(zip(tks, labs), nxt):
                if l[0] == 'bracket':
                    n = '%s[%s]' % (r['n'], l[1])
                else:
                    pre, ins = l[1]; rn = nz(r['n']); pos = rn.find(pre)
                    if pos < 0: new = None; break
                    n = rn[:pos + len(pre)] + ins + rn[pos + len(pre):]
                tk = k.get('k') or []; pk = r.get('k') or []
                if tk and pk:
                    kk = covered(tk, pk); how = '본보기 세부보장 %s 코드 %d개 중 이 특약 별표에도 있는 %d개' % (k['id'], len(tk), len(kk))
                    if not kk: kk = list(pk); how = '이 특약 코드 그대로(본보기 세부 코드가 이 특약 별표에 없음)'
                elif pk and k.get('src') == 'db' and sib:             # 감수본이 다른 세부보장에는 코드를 두고 이것만 비워 둠 = 약관이 별표 대신 정의 조문으로 정함
                    kk = []; how = '질병코드 없음 — 감수본 본보기 %s 처럼 약관이 별표 대신 정의 조문으로 정함(코드를 만들지 않는다)' % k['id']
                elif pk: kk = list(pk); how = '이 특약 코드 그대로(본보기 세부보장에 코드 없음 · 세부 구분은 규칙표가 이름으로 판정)'
                else: kk = list(tk); how = '본보기 세부보장 %s 코드(이 특약 코드 없음)' % k['id']
                # 제외코드 : 질병코드를 본보기 세부보장에서 가져왔으면 그 세부보장의 제외코드 그대로(같은 이름 = 같은 별표 · 32대질병 분류표처럼
                # 세부(14대 · 4대)마다 제외가 다르다 — v8.90 은 부모 제외코드를 물려 케102-4 가 4대질병 제외 M01.1 · N74 를 잃었다 · v8.92)
                xx = list(k.get('x') or []) if (tk and pk and covered(tk, pk)) else list(r.get('x') or k.get('x') or [])
                hh = [h for h in (k.get('hc') or []) if h in (r.get('hc') or [])] if (k.get('hc') and r.get('hc')) else list(r.get('hc') or [])
                kid = dict(id='%s-%d' % (r['id'], i), p=r['p'], n=n, parent=r['id'], c=k.get('c') or r.get('c'), k=kk, x=xx, hc=hh, **({'cond': k['cond']} if k.get('cond') else {}),
                           basis='세부보장 : 약관 본문의 「%s」 · 구성은 같은 이름 특약 %s(%s) · 코드는 %s' % (
                               _core(l[1] if l[0] == 'bracket' else l[1][1]), tp['id'], tp['p'], how))
                new.append((kid, k))
            if new:
                out.append((r, new)); done = True; break
        if not done and not ex and not any(x[2] == r['id'] for x in log):
            log.append(('본보기 세부보장 이름을 만들지 못함', r['p'], r['id'], r['n']))
    return out, log


def rename_plan(riders, templates):
    """세부 레코드가 부모 이름 없이 따로 파는 특약과 같은 이름으로 적힌 것(케328-1 「갱신형 갑상선질환 고주파열치료비(최초1회한)」 —
       케329 와 같은 이름) → 「부모[세부]」. 같은 특약(또238-1 「갱신형 특정질환3대치료비[갑상선질환 …]」)이 그 꼴로 적혀 있을 때만"""
    pidx = {(r['p'], r['id']): r for r in riders}
    tfam = {fam(t['n']) for t in templates}
    solo = collections.defaultdict(set)                       # 부모 · 세부가 아닌 단독 특약 이름 — 겹침 확인용
    for t in list(riders) + list(templates):
        if not t.get('parent'): solo[fam(t['n'])].add((t['p'], t['id']))
    out = []
    for r in riders:
        par = pidx.get((r['p'], r.get('parent')))
        if not par or '[' in r['n'] or nz(r['n']).startswith(nz(par['n'])): continue
        if not solo.get(fam(r['n'])): continue                # 따로 파는 특약과 이름이 겹칠 때만(헷갈림) 바꾼다
        lab = re.sub(r'^갱신형\s*', '', r['n'])
        cand = '%s[%s]' % (par['n'], lab)
        if fam(cand) in tfam: out.append((r, cand))
    return out
