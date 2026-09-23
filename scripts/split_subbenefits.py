#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
특약검색기(tool.html) 데이터 보정 — 세부보장 분리 · 동의어 보강 · 카테고리 정정 (ver2609 → ver2610)
- 저장소 루트에서 실행: python3 scripts/split_subbenefits.py
- 근거: 스마트 제안서 실설계 검수(2026-09-18)에서 확인된 오류. 모든 질병코드는 tool.html 이 이미
  가지고 있는 약관 별표(tables)에서만 가져오며, 새로 추측해 넣는 코드는 없다.

고치는 것
 1) 약관은 세부보장이 여럿(질병코드가 서로 다름)인데 마스터에는 부모 1건으로 뭉쳐 있던 담보 7개 군을
    세부보장 단위 담보로 분리해 추가한다(부모는 그대로 둔다).
      기계적혈전제거술Ⅱ(뇌졸중/특정심장질환) · 암 통합치료 생활비(암/유사암) · 통합암 주요치료비 6종 ·
      암 주요치료비 2종 · 특정호르몬약물허가치료비 2종 · 4대양성종양진단비 4종 · 특정질환3대치료비 3종
 2) 통합외상치료비(권역외상센터) 카테고리 불일치(integrated/specific 혼재) → specific 으로 통일.
    이 담보는 손상중증도점수(ISS) 기준이라 질병코드 목록이 없는 것이 맞다.
 3) 동의어(synonyms)에 약관 별표 「암종별(13종)」 암종명과 통합암 그룹명을 추가 — 기존 병명 검색 결과가
    넓어지지 않도록, 기존 키를 부분문자열로 포함하는 이름은 넣지 않는다.
 4) 보상시뮬레이터 benefitKind(): 부모 담보명이 아니라 [세부급부] 이름으로 급부 종류를 정한다.
    (예: 뇌혈관질환진단및치료비[혈전용해치료비] → '진단'이 아니라 '치료')
 5) 통합치료비.html 의 EMB.syn 에도 3)과 같은 암종명을 추가한다.
"""
import io, json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')
ITC = os.path.join(ROOT, '통합치료비.html')
C13 = os.path.join(ROOT, 'proposal_smart', 'cancer13.json')

html = io.open(TOOL, encoding='utf-8').read()
m = re.search(r'(<script id="DATA" type="application/json">)(.*?)(</script>)', html, re.S)
D = json.loads(m.group(2))
R, T = D['riders'], D['tables']
byid = {r['id']: r for r in R}

def tcodes(tid, g=None):
    """표의 코드·질병명 (그룹 g 지정 시 그 그룹 행만). 중복 코드는 한 번만."""
    seen = collections.OrderedDict()
    for row in T[tid]['rows']:
        if g and row.get('g') != g: continue
        for c in row['codes']:
            seen.setdefault(c, row['label'])
    return list(seen), list(seen.values())

def tbl(rider, name_part):
    """담보가 참조하는 표 중 이름에 name_part 가 들어간 표 id"""
    for tid in rider['t']:
        if tid in T and name_part in T[tid]['name']: return tid
    raise SystemExit('표 없음: %s ← %s' % (name_part, rider['n']))

def sub(parent, idx, name, tids, codes, labels, x=None):
    r = dict(parent)
    r.update({'id': '%s-%d' % (parent['id'], idx), 'n': name, 'k': codes, 'l': labels,
              'x': list(x or []), 't': list(tids), 'parent': parent['id']})
    return r

QUASI = ['C44', 'C73']                       # 기타피부암·갑상선암 (약관 본문 정의 표)
new = []                                     # (부모 id, [신규 레코드])

# ── 1) 기계적혈전제거술(카테터법)치료비Ⅱ → (뇌졸중) / (특정심장질환) ──
for r in R:
    if re.match(r'^기계적혈전제거술\(카테터법\)치료비Ⅱ', r['n']):
        heart, brain = tbl(r, '특정심장질환'), tbl(r, '뇌졸중')
        base = r['n'].replace('치료비Ⅱ ', '치료비Ⅱ')                 # '치료비Ⅱ (급여…' → '치료비Ⅱ(급여…'
        subs = []
        for i, (tag, tid) in enumerate([('뇌졸중', brain), ('특정심장질환', heart)], 1):
            k, l = tcodes(tid)
            subs.append(sub(r, i, base.replace('치료비Ⅱ', '치료비Ⅱ(%s)' % tag, 1), [tid], k, l))
        new.append((r['id'], subs))

# ── 2) 암 통합치료 생활비 → 암(유사암제외) / 유사암 ──
for r in R:
    if r['n'].startswith('암 통합치료 생활비'):
        mal, cis, bord = tbl(r, '악성신생물'), tbl(r, '제자리'), tbl(r, '행동양식')
        k1, l1 = tcodes(mal)
        k2, l2 = tcodes(cis); k3, l3 = tcodes(bord)
        tail = r['n'][len('암 통합치료 생활비'):]
        new.append((r['id'], [
            sub(r, 1, '암(유사암제외) 통합치료 생활비' + tail, [mal], k1, l1, x=QUASI),
            sub(r, 2, '유사암 통합치료 생활비' + tail, [cis, bord], QUASI + k2 + k3,
                ['기타 피부의 악성 신생물', '갑상선의 악성 신생물'] + l2 + l3)]))

# ── 3) 통합암 주요치료비 → 세부 6종 (그룹 표 g 기준 + 기타피부암·갑상선암) ──
for r in R:
    if re.search(r'통합암 주요 ?치료비', r['n']):
        gt = tbl(r, '통합암(유사암제외)')
        subs = []
        for i, g in enumerate(['특정소액암', '특정소화기암', '15대특정암', '10대특정암', '4대고액암'], 1):
            k, l = tcodes(gt, g)
            if not k: raise SystemExit('그룹 없음 %s in %s' % (g, gt))
            subs.append(sub(r, i, re.sub(r'통합암 주요 ?치료비', g + ' 주요치료비', r['n'], 1), [gt], k, l))
        subs.append(sub(r, 6, re.sub(r'통합암 주요 ?치료비', '기타피부암 및 갑상선암 주요치료비', r['n'], 1),
                        [tbl(r, '기타피부암')], QUASI, ['기타 피부의 악성 신생물', '갑상선의 악성 신생물']))
        new.append((r['id'], subs))

# ── 4) 암 주요치료비 → 암(유사암제외) / 기타피부암 및 갑상선암 ──
for r in R:
    if re.search(r'(^|센터 )암 주요치료비', r['n']):
        mal = tbl(r, '악성신생물'); k, l = tcodes(mal)
        new.append((r['id'], [
            sub(r, 1, re.sub(r'(^|센터 )암 주요치료비', r'\g<1>암(유사암제외) 주요치료비', r['n'], 1), [mal], k, l, x=QUASI),
            sub(r, 2, re.sub(r'(^|센터 )암 주요치료비', r'\g<1>기타피부암 및 갑상선암 주요치료비', r['n'], 1), [],
                QUASI, ['기타 피부의 악성 신생물', '갑상선의 악성 신생물'])]))

# ── 5) 특정호르몬약물허가치료비 → 특정항암호르몬 / 갑상선암수술후호르몬 ──
for r in R:
    if '특정호르몬약물허가치료비' in r['n']:
        mal = tbl(r, '악성신생물'); k, l = tcodes(mal)
        new.append((r['id'], [
            sub(r, 1, r['n'].replace('특정호르몬약물허가치료비', '특정항암호르몬약물허가치료비'), [mal], k, l, x=QUASI),
            sub(r, 2, r['n'].replace('특정호르몬약물허가치료비', '갑상선암수술후호르몬약물허가치료비'), [], ['C73'], ['갑상선의 악성 신생물'])]))

# ── 6) 4대양성종양진단비 → 부위별 4종 (각 표) ──
for r in R:
    if '4대양성종양진단비' in r['n']:
        pre = '갱신형 ' if r['n'].startswith('갱신형') else ''
        subs = []
        for i, (nm, part) in enumerate([('대장 양성종양및특정용종진단비', '대장'), ('위,십이지장,소화계통 양성종양및특정용종진단비', '위,십이지장'),
                                        ('중이,호흡계통,흉곽내기관 양성종양진단비', '중이'), ('골,관절연골 양성종양진단비', '골,관절연골')], 1):
            tid = tbl(r, part); k, l = tcodes(tid)
            subs.append(sub(r, i, pre + nm, [tid], k, l))
        new.append((r['id'], subs))

# ── 7) 갱신형 특정질환3대치료비 → 3종 (각 표) ──
for r in R:
    if '특정질환3대치료비' in r['n']:
        pre = '갱신형 ' if r['n'].startswith('갱신형') else ''
        subs = []
        for i, (nm, part) in enumerate([('갑상선질환 고주파열치료비(최초1회한)', '갑상선'), ('유방병변 진공보조장치이용절제치료비(최초1회한)', '유방'),
                                        ('자궁근종 고강도초음파집속술치료비(최초1회한)', '자궁근종')], 1):
            tid = tbl(r, part); k, l = tcodes(tid)
            subs.append(sub(r, i, pre + nm, [tid], k, l))
        new.append((r['id'], subs))

# 부모 바로 뒤에 삽입
out = []
addmap = dict(new)
for r in R:
    out.append(r)
    for s in addmap.get(r['id'], []): out.append(s)
D['riders'] = out
added = sum(len(v) for v in addmap.values())

# ── 카테고리 정정 ──
fixed_cat = 0
for r in D['riders']:
    if r['n'] == '통합외상치료비(권역외상센터)' and r['c'] != 'specific':
        r['c'] = 'specific'; fixed_cat += 1

# ── 동의어 보강 ──
syn = D['synonyms']; existing = list(syn.keys())
def safe(term): return not any((e in term) or (term in e) for e in existing) and term not in syn
c13 = json.load(open(C13, encoding='utf-8'))['groups']
cand = collections.OrderedDict()
for g, codes in c13.items(): cand[g] = codes
for tid in ['4332f66356', '67c9525310']:                       # 통합암 그룹(원발형·전이포함형)
    for row in T[tid]['rows']:
        if row.get('g'): cand.setdefault(row['g'], []).extend(c for c in row['codes'] if c not in cand.get(row['g'], []))
added_syn, skipped_syn = [], []
for term, codes in cand.items():
    (added_syn if safe(term) else skipped_syn).append(term)
    if safe(term): syn[term] = list(dict.fromkeys(codes))

# ── 메타·카운트 ──
D['meta']['version'] = 'ver2610'
D['meta']['total'] = len(D['riders'])
pc = collections.Counter(r['p'] for r in D['riders']); D['meta']['prodcount'] = dict(pc)
cc = collections.Counter(r['c'] for r in D['riders'])
for c in D['categories']:
    if isinstance(c, dict) and 'count' in c: c['count'] = cc.get(c['id'], 0)

html = html[:m.start(2)] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):]

# ── benefitKind : 세부급부 우선 ──
old = "function benefitKind(n){\n  for(let i=0;i<BEN.length;i++) if(n.indexOf(BEN[i][0])>=0) return BEN[i][1];\n  return '기타';\n}"
new_fn = ("function benefitKind(n){\n"
          "  /* [세부급부]가 있으면 그 이름으로 정한다 — 부모 담보명(진단및치료비 등)의 낱말이 선점하지 않게(ver2610) */\n"
          "  const m=/\\[([^\\]]+)\\]/.exec(n); const s=m?m[1]:n;\n"
          "  for(let i=0;i<BEN.length;i++) if(s.indexOf(BEN[i][0])>=0) return BEN[i][1];\n"
          "  for(let i=0;i<BEN.length;i++) if(n.indexOf(BEN[i][0])>=0) return BEN[i][1];\n"
          "  return '기타';\n}")
assert old in html, 'benefitKind 원문 불일치'
html = html.replace(old, new_fn, 1)
html = html.replace('ver2609', 'ver2610')
io.open(TOOL, 'w', encoding='utf-8').write(html)

# ── 통합치료비.html EMB.syn 보강 ──
h2 = io.open(ITC, encoding='utf-8').read()
m2 = re.search(r'(<script>const EMB=)(\{.*?\})(;</script>)', h2, re.S)
E = json.loads(m2.group(2)); ex2 = list(E['syn'].keys()); n2 = 0
for term in added_syn:
    if not any((e in term) or (term in e) for e in ex2) and term not in E['syn']:
        E['syn'][term] = syn[term]; n2 += 1
h2 = h2[:m2.start(2)] + json.dumps(E, ensure_ascii=False, separators=(',', ':')) + h2[m2.end(2):]
io.open(ITC, 'w', encoding='utf-8').write(h2)

print('세부보장 분리 : 부모 %d건 → 신규 %d건 추가 · 총 담보 %d건' % (len(addmap), added, len(D['riders'])))
print('상품별 :', dict(pc))
print('카테고리 정정 : 통합외상치료비 %d건 → specific' % fixed_cat)
print('동의어 추가 %d개 : %s' % (len(added_syn), ', '.join(added_syn)))
print('동의어 보류 %d개(기존 병명과 겹침) : %s' % (len(skipped_syn), ', '.join(skipped_syn)))
print('통합치료비.html syn 추가 %d개' % n2)
for pid, subs in new:
    print('  %-6s %s' % (pid, byid[pid]['n'][:46]))
    for s in subs: print('         └ %-64s k%-3d x%s' % (s['n'][:64], len(s['k']), s['x']))
