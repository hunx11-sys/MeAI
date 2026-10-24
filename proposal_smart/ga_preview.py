# -*- coding: utf-8 -*-
"""GA 지면 미리보기 — 설계서 PDF 없이 담보 목록을 직접 넣어 지면(HTML·PDF)을 만든다(지면 모양 점검용 · 금액은 계산 엔진 그대로).

  python ga_preview.py <결과.pdf> [--cover 2] [--design 설계서.pdf]

설계서 PDF 가 있으면 그대로 읽고(ga_proposal.build 와 같다), 없으면 특약 마스터(ga_spec.universe)에서 이름으로 고른 담보 묶음(SAMPLE)을
가입금액과 함께 넣는다. 가입금액은 **점검용 가정값**이다 — 고객에게 나가는 지면이 아니다. 표지 이름·번호도 가짜(GA 가안 표기 그대로)다."""
import os, sys, re
BASE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, BASE)
import ga_proposal as G, ga_spec as GS, scen_engine as S

# (담보명에 들어갈 말, 가입금액 만원) — 마스터에서 이름이 가장 짧게 맞는 것 하나
SAMPLE = [('암진단비(유사암제외)', 3000), ('유사암진단비', 600), ('전이암진단비', 1000), ('암수술비(유사암제외)', 500), ('암 통합치료비(기본형)', 5000),
          ('항암약물치료비', 1000), ('항암방사선치료비', 1000), ('표적항암약물허가치료비', 2000), ('특정면역항암약물허가치료비', 2000),
          ('뇌졸중진단비', 1000), ('뇌혈관질환진단비', 1000), ('허혈성심장질환진단비', 1000), ('급성심근경색증진단비', 1000),
          ('특정순환계질환 통합치료비', 5000), ('뇌혈관질환수술비', 500), ('허혈성심장질환수술비', 500), ('질병수술비', 30), ('수술비Ⅱ(1-5종)', 100),
          ('130대질병수술비', 100), ('골절진단비', 30), ('상해수술비', 50), ('골절수술비', 50), ('상해 통합치료비(실속형)', 500),
          ('간병인지원 질병입원일당(Ⅰ)(1일이상 180일한도)', 1), ('간병인사용 질병입원일당(1일이상 180일한도)(요양병원)', 10), ('암 후유장해', 10000)]

def sample_riders():
    uni = GS.universe()
    out, seen = [], set()
    for key, man in SAMPLE:
        k = S.nname(key)
        cands = sorted((r for r in uni if k in S.nname(r['name']) and r['name'] not in seen and not r['name'].startswith('┗')), key=lambda r: len(r['name']))
        if not cands: print('  (표본에 없음)', key); continue
        r = dict(cands[0]); r['man'] = man; r['no'] = len(out) + 1; seen.add(r['name']); out.append(r)
        if '1-5종' in key:                           # 설계서처럼 종별 행도 같이
            for j in range(1, 6):
                rr = dict(next(x for x in uni if x['name'] == '수술비Ⅱ(1-5종)[질병%d종]' % j)); rr['man'] = man; rr['no'] = len(out) + 1; out.append(rr)
    return out

def load_sample(cover=1):
    S.ISSUES.clear(); GS.clear_cache()
    G.RID = sample_riders(); G.NRID = len(G.RID)
    G.PRODUCT = '(무)The건강한메리츠내Mom대로5.10.5보장보험 2607 4.0'; G.PREMIUM = '100,000원'; G.SHORTP = 'The건강한 내Mom대로 5.10.5'; G.WHO = '고객님'
    G.HEAD = dict(name='민메리', sex='여자', age='20세', no='124200068202610162', org='메리츠대리점(서울)', agent_name='민타타', mobile='010-1234-5678', tel='02-1234-5678', code='124200068', agent='')
    G.COVER = cover
    G.VAL = {c['key']: GS.cell_value(c, G.RID) for c in GS.CELLS}

if __name__ == '__main__':
    args = sys.argv[1:]
    cover = int(args[args.index('--cover') + 1]) if '--cover' in args else 1
    design = args[args.index('--design') + 1] if '--design' in args else None
    out = args[0]
    if design:
        G.COVER = cover; h = G.html(design)
    else:
        load_sample(cover); h = G.html_loaded()
    hp = os.path.splitext(out)[0] + '.html'; open(hp, 'w', encoding='utf-8').write(h)
    warn = G.render(hp, out)
    print('쪽수', len(re.findall(r'<div class="page', h)), '· 지면 경고', warn or '없음', '→', out)
