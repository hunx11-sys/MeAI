# -*- coding: utf-8 -*-
"""칸별 특약 지도(HTML) 데이터 — ga_spec 결과 json → data.json
  python3 build_data.py <ga_spec_results.json> <data.json>"""
import os, re as _re
VER=_re.search(r"VERSION = '([^']+)'", open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'api.py'),encoding='utf-8').read()).group(1)
import json, re, sys, collections
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scen_engine as S
R=json.load(open(sys.argv[1]))
RULES={r['id']:r for r in S.RULES}
KIND={'dx':'진단비','surg':'수술비','tx':'치료비','day':'입원·통원 일당','point2':'포인트적립형 치료비','skip':'계산 제외','care':'간병','life':'사망·후유장해','nonmed':'비의료','itc_unknown':'금액표 없음'}
PAGES={1:'보장요약',2:'암보장',3:'뇌·심보장'}
DN={'gan31-M.pdf':'간편31 남(GA 테스트)','mom-40.pdf':'통합간편 남40','the510-44f.pdf':'The건강한 5.10.5 여44','mom5105-40.pdf':'내Mom대로 5.10.5 여40','u355.pdf':'통합간편355 여','light355.pdf':'가벼운 간편355 여','mom-new-40.pdf':'내Mom대로 남40','gan31-41650.pdf':'간편31 여(41,650원)','d42940.pdf':'통합간편 남(42,940원)','d106010.pdf':'통합간편 여(106,010원)','d272600.pdf':'통합간편 남(272,600원)','d61760.pdf':'통합간편 연만기 남(61,760원)','d104810.pdf':'알파Plus 남(104,810원)','t5105-30020.pdf':'The건강한5.10.5 여(30,020원)','t5105-177770.pdf':'The건강한5.10.5 남(177,770원)','t5105-122661.pdf':'The건강한내Mom대로5.10.5 남(122,660원)','t5105-243046.pdf':'The건강한내Mom대로5.10.5 남(243,040원)'}
order=['gan31-M.pdf','the510-44f.pdf','mom-40.pdf','mom5105-40.pdf','mom-new-40.pdf','u355.pdf','light355.pdf','gan31-41650.pdf','d42940.pdf','d106010.pdf','d272600.pdf','d61760.pdf','d104810.pdf','t5105-30020.pdf','t5105-177770.pdf','t5105-122661.pdf','t5105-243046.pdf']
D={d['pdf']:d for d in R['designs']}
designs=[{'k':p,'l':DN[p],'prod':re.sub(r'\(무\)\s*','',D[p]['meta'].get('product','')).split('(해약')[0][:60]} for p in order if p in D]
names=[]; NI={}
def ni(n):
    if n not in NI: NI[n]=len(names); names.append(n)
    return NI[n]
prods=[]; PI={}
def pi(p):
    p=p or '-'
    if p not in PI: PI[p]=len(prods); prods.append(p)
    return PI[p]
rules={}
def rk(rid):
    if not rid: return ''
    if rid not in rules:
        if rid=='itc': rules[rid]=['통합치료비','약관 지급금액표 항목 금액 합 · 연간 총액은 가입금액 한도']
        elif rid=='ls_monthly': rules[rid]=['통합생활지원비','약관 월 항목표 합 · 월 한도 = 가입금액']
        elif rid=='direct': rules[rid]=['가입금액 표시','설계서 가입금액(또는 금액란의 「또는 N천원」)을 그대로 표시']
        else:
            r=RULES.get(rid) or {}; rules[rid]=[KIND.get(r.get('kind'),r.get('kind','')), r.get('label','')]
    return rid
TAGK={'cause':'원인','hosp':'병원','dx':'진단','surg':'1-5종 항목','surg7':'1-7종 코드','anes':'전신마취','anes_h':'마취시간','drug':'연간 약물 종수','icu':'중환자실 일수','nc':'비급여','days':'입원일수','series':'계열','open':'관혈','acts':'치료행위','hc':'수가코드','within1y':'1년 이내'}
def scdesc(sc):
    if not sc: return None
    tg=sc.get('tags') or {}
    st=[ '%s %s'%(e[0],e[1]) for e in sc.get('itc_events') or []]
    tags=['%s %s'%(TAGK.get(a,a), ','.join(b) if isinstance(b,list) else b) for a,b in tg.items() if b not in (None,'',[],0) and a not in ('grp','five_major','done')]
    return {'kcd':sc.get('kcd'),'steps':st,'tags':tags,'grp':tg.get('grp') or []}
MODE={'first':'최초 지급 합계','year':'반복(연 1회) — 최초 1회 담보 제외','each':'매 회 — 1회당 지급 담보만','itc_only':'통합치료비 항목만','meta_only':'전이암 진단비 줄만(일반암 진단비 제외)','ms_only':'특정순환계질환(주요손상및질환) 통합치료비 줄만'}
def filt_txt(f):
    if not f: return ''
    if f[0]=='BH': return '줄 : '+f[1]
    if f[0]=='BHS': return '표에 나온 줄만 합산'
    if f[0]=='ANY': return '표의 담보행에 드는 담보만 합산'
    keys,ex=f; return '이름에 '+' / '.join(keys)+(' (제외 : '+' / '.join(ex)+')' if ex else '')
FREQ={'once':'최초 1회','year':'연 1회','each':'1회당'}
cells=[]
for c in R['cells']:
    cid=c['id']
    vals=[]; dls=[]; iss=[]
    for p in order:
        dc=D[p]['cells'].get(cid) or {}
        vals.append(' / '.join(dc.get('tokens') or []))
        ls=[l for l in dc.get('lines') or [] if l.get('counted') and l.get('in_row') is not False and l.get('amt')]
        dls.append([[ni(l['name']), round(l['amt'],1), l.get('why') or '', rk(l.get('rule')), FREQ.get(l.get('freq'),'')] for l in ls])
        iss.append(['[%s] %s — %s'%(x.get('구분',''),x.get('담보',''),x.get('사유','')) for x in (dc.get('issues') or [])[:12]])
    u=(R['universe'].get(cid) or {}).get('lines') or []
    agg=collections.OrderedDict()
    for l in u:
        if not(l.get('counted') and l.get('in_row') is not False and l.get('amt')): continue
        k=l['name']; agg.setdefault(k,[set(),l.get('rule')]); agg[k][0].add(pi(l.get('product')))
    uni=[[ni(k),sorted(v[0]),rk(v[1])] for k,v in agg.items()]
    cells.append({'id':cid,'n':int(cid.split('-')[1]),'p':c['page'],'sec':c['section'],'row':c['row'] if c['row']!=c['section'] else '','col':c['col'],'kind':c['kind'],
      'sc':c.get('sc_name') or '','scd':scdesc(c.get('sc')),'mode':MODE.get(c['mode'],c['mode']) if c['kind']=='engine' else '설계서 가입금액 그대로(계산 없음)','filt':'','note':c.get('note') or '',
      'v':vals,'dl':dls,'iss':iss,'u':uni})
data={'designs':designs,'pages':PAGES,'names':names,'prods':prods,'rules':rules,'cells':cells,'meta':{'ver':VER,'cells':len(cells),'master':len(R['universe_riders'])}}
s=json.dumps(data,ensure_ascii=False,separators=(',',':'))
open(sys.argv[2],'w').write(s); print(len(s)//1024,'KB', len(names), len(prods), len(rules))
