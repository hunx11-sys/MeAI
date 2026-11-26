# Py.java 자체 시험용 정답 — 파이썬이 내는 글자를 그대로 적어 둔다
import json, re, sys, random
random.seed(7)
nums=[0.1,1.0,1e16,1e15,123456789012345680.0,1e-5,0.0001,2.675,1/3,5e-324,1.7976931348623157e308,100.0,0.5,2.5,3.5,-0.5,1e22,1e23,4.35,0.30000000000000004,95530.0,1234.5]+[random.uniform(-1e6,1e6) for _ in range(200)]+[random.random()*10**random.randint(-20,20) for _ in range(200)]
out={'repr':[[x,repr(x)] for x in nums],
     'round0':[[x,round(x)] for x in nums if abs(x)<1e15],
     'round1':[[x,round(x,1)] for x in nums if abs(x)<1e12],
     'round2':[[x,round(x,2)] for x in nums if abs(x)<1e12],
     'fmt':[]}
F=[('%s',[1.0]),('%s',[10]),('%d',[3.7]),('%5d|',[42]),('%-5d|',[42]),('%05d',[-42]),('%.1f',[2.25]),('%.1f',[2.35]),('%.2f',[2.675]),('%.0f',[0.5]),('%.0f',[1.5]),('%8.2f|',[3.14159]),
   ('%s%%',[50]),('%s · %s',['가',None]),('%r',['a']),('%g',[0.0001]),('%g',[100000.0]),('%g',[1e6]),('%g',[1234567.0]),('%g',[0.5]),('%.3g',[1234.5]),('%x',[255]),('%+d',[5]),('%.2f',[-0.001]),('%s',[True]),('%s',[[1,'a',2.0]]),('%s',[{'a':1}]),('%.4spt',['abcdefg']),('%.2fpt',[30.5]),('%.2f',[1e-9]),('%d건',[True])]
for f,a in F: out['fmt'].append([f,a,f%tuple(a)])
for x in nums[:120]:
    for f in ('%.1f','%.2f','%.3f','%g','%s','%.0f','%d'):
        if f=='%d' and abs(x)>1e15: continue
        out['fmt'].append([f,[x],f%x])
out['commaF']=[[x,format(x,',.0f'),format(x,',.2f')] for x in [0,5,999.5,1000.5,1234567.891,2.5,3.5,-1234.5,50.0,100,1e9]]
out['fmtG']=[[x,format(x,'g')] for x in [10,25,50.0,12.5,0.5,100,33.333333333,1e-5,123456789]]
out['minmax']=[[a,b,min(a,b),max(a,b)] for a,b in [(1,1.0),(1.0,1),(2,3),(3.5,2),(0,-1),(0,0.0),(100,100)]]
out['comma']=[[x,format(x,',')] for x in [0,999,1000,-1234567,12345.5,1000000.0]]
R=[(r'a[b[c]+',  'xab[cx'),(r'(?P<n>\d+)-(?P=n)','12-12 3-4'),(r'x{2}y{','xxy{'),(r'[]a]+','a]]b'),(r'\d+\Z','ab12'),(r'[^\[\]]+','a[b]c'),(r'\w+','가나 abc_1 ①'),(r'\s+','a　b\xa0c'),(r'.+','ab\r\ncd'),(r'^b','a\nb'),(r'a|b{1,2}c','bbc a'),(r'[a&&b]','a&b'),(r'(a)|(b)','ab'),(r'\((?:\d+년)?갱신\)','암진단비(20년갱신)(갱신)'),(r'[·ㆍ․‧∙•・]','간호·간병'),(r'{a}','{a}')]
out['re']=[[p,s,[m.group(0) for m in re.finditer(p,s)],re.findall(p,s),re.sub(p,'<\\g<0>>',s)] for p,s in R]
out['sub']=[[r'(\d+)(원)',r'\2\1\\n',s:='금액 300원 4원',re.sub(r'(\d+)(원)',r'\2\1\\n',s)],[r'x*','-','abxd',re.sub(r'x*','-','abxd')],[r'\s+','','a b\tc',re.sub(r'\s+','','a b\tc')]]
out['split']=[[p,s,re.split(p,s)] for p,s in [(r'[,/]','a,b/c'),(r'\s*·\s*','가 · 나·다'),(r'(,)','a,b'),(r'x','xaxbx')]]
out['str']=[[v,str(v)] for v in [None,True,False,1,1.5,'a',[1,'a',None,2.0],{'k':[1,2]},"it's",'q"q']]
out['json']=[[v,json.dumps(v),json.dumps(v,ensure_ascii=False),json.dumps(v,ensure_ascii=False,separators=(',',':')),json.dumps(v,ensure_ascii=False,indent=1)] for v in [{'가':[1,2.0,None,True,'a"b\n'],'b':{}, 'c':[]},[],{},[1.5e-7,1e16,'\x7f',' ']]]
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False)
