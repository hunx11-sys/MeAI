# -*- coding: utf-8 -*-
"""
특약검색기(tool.html) 데이터 보정 2차 — 남은 세부보장 특약 전부 분리 (ver2610 → ver2611)

약관 본문에 "이 특별약관은 아래의 총 N개의 세부보장으로 구성" 이라고 적힌 특약 가운데
아직 세부 특약으로 나뉘지 않은 55건(30계열)을 약관이 정한 세부보장 이름 그대로 나눈다.
설계서 표기 규칙(부모담보명[세부보장명])에 맞춰 세부 특약 이름을 만들고, 질병코드는

  · 세부보장마다 별표가 다른 것(131/130대질병수술비 11종 · 통합골절치료비 · 32대질병관혈수술비 ·
    질병 특정 비급여신의료기술치료비) → 그 세부보장의 별표(분류표) 코드만
  · 세부보장이 '조건'으로 나뉘는 것(당화혈색소 % · 약물 종수 · 관혈/비관혈 · 중증도 · 점수 · 시술 종류)
    → 부모 특약 코드 그대로 + cond(조건 문구)

원칙 : 코드는 약관 별표·본문에서만 옮기고 추정하지 않는다. 별표가 행 표로 없으면 원문(text)에서
코드를 뽑고, 그것도 없으면 131대질병 그룹표(g131.json · 약관 엑셀 기반)를 쓴다.
실행 : python3 scripts/split_subbenefits2.py   (저장소 루트, 1회)
"""
import io, json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
G131 = json.load(io.open(os.path.join(ROOT, 'proposal_smart', 'g131.json'), encoding='utf-8'))

html = io.open(TOOL, encoding='utf-8').read()
m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', html, re.S)
D = json.loads(m.group(2))
R, T = D['riders'], D['tables']
done_parents = {r['parent'] for r in R if r.get('parent')}

CODE = re.compile(r'\b([A-Z]\d{2}(?:\.\d{1,2})?)(?:\s*[∼~\-–]\s*([A-Z])?(\d{2}(?:\.\d{1,2})?))?')

def expand(m_):
    """'I20∼I25' → I20..I25 · 'N17-N19' → N17..N19 · 단일 코드는 그대로"""
    a, letter, b = m_.group(1), m_.group(2), m_.group(3)
    if not b: return [a]
    L = a[0];
    if letter and letter != L: return [a]
    try:
        s, e = int(a[1:3]), int(b[:2])
    except ValueError:
        return [a]
    if '.' in a or '.' in b or e < s or e - s > 40: return [a]
    return ['%s%02d' % (L, i) for i in range(s, e + 1)]

def tcodes(tid):
    seen = collections.OrderedDict()
    for row in T[tid]['rows']:
        for c in row['codes']: seen.setdefault(c, row['label'])
    return list(seen), list(seen.values())

def text_codes(txt):
    seen = collections.OrderedDict()
    txt = re.sub(r'출생전후기\s*질병\s*\(P00\s*[~∼]\s*P96\)', '', txt)   # 줄이 나뉘어 있어도 제외 문장은 통째로 지운다
    for line in txt.split('\n'):
        if '포함되지' in line or '제외' in line: continue      # "출생전후기 질병(P00~P96)은 포함되지 않습니다" 같은 제외 문장
        for mm in CODE.finditer(line):
            for c in expand(mm): seen.setdefault(c, re.sub(r'\s+', ' ', line.split(mm.group(0))[0]).strip()[:40] or c)
    return list(seen), list(seen.values())

def tbl(rider, part):
    for tid in rider.get('t') or []:
        if tid in T and part in T[tid]['name']: return tid
    return None

G131MAP = {'심장질환': '심장질환', '뇌혈관질환': '뇌혈관질환', '특정31대질병': '특정31대질병', '다빈도61대질병': '다빈도64대질병',
           '다빈도62대질병': '다빈도64대질병', '특정다빈도29대질병': '특정다빈도29대질병', '후각특정질환': '후각특정질환',
           '관절염,생식기질환': '관절염․생식기질환', '치핵': '치핵', '백내장': '백내장'}

def table_codes(rider, part):
    """세부보장의 별표 코드 : 행 표 → 원문 코드 → g131 그룹표 순서"""
    tid = tbl(rider, part)
    if tid and T[tid]['rows']: return tcodes(tid), [tid]
    if tid and T[tid].get('text'):
        k, l = text_codes(T[tid]['text'])
        if k: return (k, l), [tid]
    g = G131MAP.get(part)
    if g and g in G131: return (list(G131[g]), [g] * len(G131[g])), ([tid] if tid else [])
    return None, ([tid] if tid else [])          # 별표가 치료 목록(KCD 없음)인 경우 → 호출 쪽에서 부모 코드 사용

def section_codes(rider, part, head):
    """한 별표 원문 안의 [5대질병] 같은 절(節)만 골라 코드를 뽑는다(32대질병관혈수술비)"""
    tid = tbl(rider, part); txt = T[tid].get('text', '')
    i = txt.find('[%s]' % head)
    if i < 0: raise SystemExit('절 없음: %s' % head)
    j = txt.find('\n[', i + 1); sec = txt[i:j if j > 0 else None]
    k, l = text_codes(sec)
    if not k: raise SystemExit('절 코드 없음: %s' % head)
    return (k, l), [tid]

QUASI = ['C44', 'C73']
new = []; log = []

def sub(parent, idx, label, kl, tids=None, x=None, cond=None):
    r = dict(parent)
    r.update({'id': '%s-%d' % (parent['id'], idx), 'n': '%s[%s]' % (parent['n'], label), 'k': list(kl[0]), 'l': list(kl[1]),
              'x': list(x if x is not None else (parent.get('x') or [])), 't': list(tids if tids is not None else (parent.get('t') or [])),
              'parent': parent['id']})
    if cond: r['cond'] = cond
    return r

def par(r): return (r.get('k') or [], r.get('l') or [])

def add(r, subs):
    new.append((r['id'], subs)); log.append((r['p'], r['n'], len(subs)))

for r in R:
    if r.get('parent') or r['id'] in done_parents: continue
    b = r.get('b') or ''
    mm = re.search(r'총\s*(\d+)\s*개의\s*세부\s*보장', b)
    if not mm: continue
    n, nm = int(mm.group(1)), r['n']
    subs = []

    # ── 131/130대질병수술비 : 별표 11종 → 세부 11개 ──
    if re.search(r'13[01]대질병수술비', nm):
        for i, tid in enumerate([t for t in r['t'] if t in T], 1):
            part = T[tid]['name'].replace(' 분류표', '').strip()
            kl, tids = table_codes(r, part)
            if not kl: raise SystemExit('별표 코드 없음: %s ← %s' % (part, r['n']))
            subs.append(sub(r, i, part, kl, tids))
    elif nm == '통합골절치료비':
        a, ta = table_codes(r, '치아파절제외'); g, tg = table_codes(r, '골절분류표Ⅱ')
        if not a or not g: raise SystemExit('골절 별표 코드 없음')
        for i, (lab, kl, tids) in enumerate([('골절(치아파절제외) 철심제거수술비(급여,연간1회한)', a, ta), ('골절(치아파절제외) 부목치료비(급여,연간1회한)', a, ta),
                                             ('골절탈구 도수정복술치료비(급여,연간1회한)', a, ta), ('골절수술비Ⅱ', g, tg), ('깁스치료비', g, tg)], 1):
            subs.append(sub(r, i, lab, kl, tids))
    elif '신의료기술치료비' in nm:
        spec = [('1종 근골 및 하지정맥류질환', '근골'), ('2종 기타질환', '기타질환'), ('3종 로봇보조', None), ('4종 여성 비뇨생식기질환', '여성')][:n]
        for i, (lab, part) in enumerate(spec, 1):
            kl, tids = table_codes(r, part) if part else (None, [])
            # 별표가 KCD 표가 아니라 '치료 목록'이라 코드가 없다 → 부모 코드(없음) + 조건. 어떤 치료가 해당되는지는 별표 t 로 연결
            subs.append(sub(r, i, lab, kl or par(r), tids, cond='%s 비급여·신의료기술치료 — 별표 치료 목록 기준 · 연간 1회' % lab))
    elif nm.startswith('32대질병관혈수술비'):
        for i, head in enumerate(['5대질병', '9대질병', '14대질병', '4대질병'], 1):
            kl, tids = section_codes(r, '32대질병', head); subs.append(sub(r, i, head + '관혈수술비', kl, tids))
    elif '최대두배받는2대질환치료비' in nm:
        for i in range(1, 5): subs.append(sub(r, i, '%d점이상' % i, par(r), cond='2대질환치료포인트 누적 %d점 이상 · 최초 1회' % i))
    elif nm.startswith('신화상치료비'):
        subs = [sub(r, 1, '화상진단비', par(r), cond='심재성 2도 이상 화상 · 1사고당 1회'), sub(r, 2, '화상수술비', par(r), cond='화상 치료 목적 수술'),
                sub(r, 3, '중증화상및부식진단비', par(r), cond='약관 제6조 중증화상 및 부식 기준 · 최초 1회')]
    elif nm.startswith('상해특정급여시술치료비') or nm.startswith('질병특정급여시술치료비'):
        acts = ['흡인,천자,절개,배액,배농', '신경차단술', '화상처치', '도수정복술', '단순창상봉합술', '기타시술'] if nm.startswith('상해') else \
               ['흡인,천자,절개,배액,배농', '신경차단술', '도수정복술', '단순창상봉합술', '기타시술']
        for i, a in enumerate(acts, 1): subs.append(sub(r, i, a + ',연간1회한', par(r), cond='진료행위 구분 [%s] · 연간 1회' % a))
    elif re.search(r'^5대질환.*수술비', nm):
        subs = [sub(r, 1, '관혈', par(r), cond='관혈수술 · 각 질병당 연간 1회'), sub(r, 2, '비관혈', par(r), cond='비관혈수술 · 각 질병당 연간 1회')]
    elif '특정순환계질환 통합치료 생활비' in nm:
        subs = [sub(r, 1, '연간 통합치료 2회이상', par(r), cond='연간 통합치료 2회 이상 · 연간 1회'), sub(r, 2, '연간 통합치료 3회이상', par(r), cond='연간 통합치료 3회 이상 · 연간 1회')]
    elif '다빈치로봇 암수술비' in nm:
        subs = [sub(r, 1, '암(특정암제외)', par(r), cond='최초 1회 · 180일/1년 경과 구분 지급'), sub(r, 2, '특정암', par(r), cond='약관 별표 특정암 · 최초 1회')]
    elif '표적항암약물허가치료비Ⅲ' in nm:
        subs = [sub(r, 1, '특정표적항암약물허가치료', par(r), cond='비급여 특정표적항암약물 · 최초 1회'), sub(r, 2, '특정면역항암약물허가치료', par(r), cond='비급여 특정면역항암약물 · 최초 1회')]
    elif '연간 약물종류 개수별' in nm:
        for i in range(1, 4): subs.append(sub(r, i, '%d종이상' % i, par(r), cond='연간 표적항암제 약물종류 %d종 이상 · 연간 1회' % i))
    elif nm == '암진단및치료비Ⅱ':
        subs = [sub(r, 1, '암진단비(유사암제외)', par(r), x=QUASI), sub(r, 2, '항암약물치료비', par(r)),
                sub(r, 3, '표적항암약물허가치료비(비급여(전액본인부담 포함))(연간1회한)(2종및3종이상)', par(r), cond='연간 표적항암제 약물종류 2종 이상')]
    elif re.match(r'^뇌혈관질환진단및치료비(Ⅱ)?$', nm):
        s = 'Ⅱ' if nm.endswith('Ⅱ') else ''
        subs = [sub(r, 1, '뇌혈관질환진단비' + s, par(r)), sub(r, 2, '뇌혈관질환 특정혈전치료비(연간1회한)', par(r), cond='혈전용해치료 + 급여 기계적혈전제거술(카테터법) 모두 · 연간 1회')]
    elif re.match(r'^허혈성심장질환진단및치료비(Ⅱ)?$', nm):
        s = 'Ⅱ' if nm.endswith('Ⅱ') else ''
        subs = [sub(r, 1, '허혈성심장질환진단비' + s, par(r)), sub(r, 2, '허혈성심장질환 특정혈전치료비(연간1회한)', par(r), cond='혈전용해치료 + 급여 기계적혈전제거술(카테터법) 모두 · 연간 1회')]
    elif nm == '암후유장해및진단비':
        subs = [sub(r, 1, '암진단비(유사암제외)', par(r), x=QUASI), sub(r, 2, '암후유장해(3-100%)', par(r), cond='장해분류표 3~100% 장해'), sub(r, 3, '암80%이상후유장해', par(r), cond='장해분류표 80% 이상 장해')]
    elif nm == '암치료,후유장해및진단비':
        subs = [sub(r, 1, '암진단비(유사암제외)', par(r), x=QUASI), sub(r, 2, '항암약물치료비', par(r)),
                sub(r, 3, '표적항암약물허가치료비(비급여(전액본인부담 포함))(연간1회한)(2종및3종이상)', par(r), cond='연간 표적항암제 약물종류 2종 이상'),
                sub(r, 4, '암후유장해(3-100%)', par(r), cond='장해분류표 3~100% 장해'), sub(r, 5, '암80%이상후유장해', par(r), cond='장해분류표 80% 이상 장해')]
    elif nm == '당뇨병진단비Ⅱ':
        for i, p in enumerate(['7.0', '9.0', '11.0'], 1): subs.append(sub(r, i, '당화혈색소 %s%%이상' % p, par(r), cond='당화혈색소 %s%% 이상 당뇨병Ⅱ 진단 · 최초 1회' % p))
    elif nm.startswith('고혈압(원발성)대상질병진단비'):
        for i, lab in enumerate(['고혈압(원발성)', '중등증이상 고혈압(원발성)', '중증고혈압(원발성)'], 1): subs.append(sub(r, i, lab, par(r), cond=lab + ' 진단 · 최초 1회'))
    elif nm.startswith('이상지질혈증'):
        for i, lab in enumerate(['이상지질혈증(고지혈증포함)', '중등증이상 이상지질혈증(고지혈증포함)', '중증 이상지질혈증(고지혈증포함)'], 1): subs.append(sub(r, i, lab, par(r), cond=lab + ' 진단 · 최초 1회'))
    elif nm == '통합상해진단비':
        i = 0
        for site in ['머리 및 목', '복부 및 등', '어깨 및 팔', '손목 및 손', '엉덩이 및 다리', '발목 및 발', '기타']:
            for sev in (['경증', '중등증', '중증'] if site != '기타' else ['', '중등증', '중증']):
                i += 1; lab = '%s의 %s상해진단비(연간1회한)' % (site, sev) if site != '기타' else '기타의 %s상해진단비(연간1회한)' % sev
                subs.append(sub(r, i, lab, par(r), cond='부위 %s · %s · 연간 1회' % (site, sev or '경증 및 기타')))
    elif nm.endswith('통합교통상해진단비'):
        for i, lab in enumerate(['경증및기타,연간1회한', '중등증,연간1회한', '중증,연간1회한'], 1): subs.append(sub(r, i, lab, par(r), cond='교통상해 · ' + lab.split(',')[0] + ' · 연간 1회'))
    elif '신치아보철치료비보장' in nm:
        subs = [sub(r, 1, '치아보철치료비', par(r), cond='영구치 발거 후 보철(틀니·브릿지·임플란트)'), sub(r, 2, '재식립 임플란트치료비', par(r), cond='임플란트 재식립')]
    else:
        print('[미처리]', r['id'], nm, n); continue
    if len(subs) != n: print('[개수 불일치] %s %s 약관 %d · 생성 %d' % (r['id'], nm, n, len(subs)))
    add(r, subs)

# ── 부모 바로 뒤에 삽입 ──
addmap = dict(new); out = []
for r in R:
    out.append(r)
    for s in addmap.get(r['id'], []): out.append(s)
D['riders'] = out
added = sum(len(v) for v in addmap.values())

# ── 메타 ──
D['meta']['version'] = 'ver2611'; D['meta']['total'] = len(D['riders'])
D['meta']['prodcount'] = dict(collections.Counter(r['p'] for r in D['riders']))
for c in D.get('categories', []):
    if isinstance(c, dict) and 'id' in c: c['count'] = sum(1 for r in D['riders'] if r.get('c') == c['id'])

html = html[:m.start(2)] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):]
html = html.replace('ver2610', 'ver2611')
io.open(TOOL, 'w', encoding='utf-8').write(html)
print('분리 특약 %d건 → 세부 %d개 · 전체 %d건' % (len(new), added, len(D['riders'])))
for p, nm, k in log: print('  %s · %s → %d' % (p, nm, k))
