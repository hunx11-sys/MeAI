# 긴 글자 상수(CSS · JS)를 파이썬 판에서 그대로 읽어 자바 소스(Txt.java)로 적는다 — 손으로 옮겨 적지 않는다(글자 하나까지 같아야 하므로).
# 사용 : python3 golden/gen_consts.py        (파이썬 판의 CSS · JS 를 고친 뒤 다시 돌린다 → src/main/java/meai/sp/Txt.java)
import sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'proposal_smart'))
import warnings; warnings.filterwarnings('ignore')
import ga_proposal as GP, ga_v2 as GV
def lit(s):
    o = []
    for ch in s:
        c = ord(ch)
        if ch == '\\': o.append('\\\\')
        elif ch == '"': o.append('\\"')
        elif ch == '\n': o.append('\\n')
        elif ch == '\r': o.append('\\r')
        elif ch == '\t': o.append('\\t')
        elif c < 0x20 or c == 0x7f or c in (0x2028, 0x2029) or c > 0xffff: o.append(''.join('\\u%04x' % u for u in (([c] if c <= 0xffff else [0xd800 + ((c - 0x10000) >> 10), 0xdc00 + ((c - 0x10000) & 0x3ff)]))))
        else: o.append(ch)
    return '"' + ''.join(o) + '"'
def const(name, s, doc):
    parts = s.split('\n'); lines = [p + ('\n' if i < len(parts) - 1 else '') for i, p in enumerate(parts)]
    lines = [x for x in lines if x != ''] or ['']
    body = '\n            + '.join(lit(x) for x in lines)
    assert len(s.encode('utf-8')) < 60000, name      # 자바 문자열 상수 한도(65535바이트)
    return '    /** %s */\n    public static final String %s = %s;\n' % (doc, name, body)
C = [('GP_CSS', GP.CSS, 'ga_proposal.CSS'), ('GP_MOCK_CSS', GP.MOCK_CSS, 'ga_proposal.MOCK_CSS'),
     ('DETAIL_CSS', GV.DETAIL_CSS, 'ga_v2.DETAIL_CSS'), ('DETAIL_COLS', GV.DETAIL_COLS, 'ga_v2.DETAIL_COLS'), ('DETAIL_HEAD', GV.DETAIL_HEAD, 'ga_v2.DETAIL_HEAD'),
     ('DETAIL_JS', GV.DETAIL_JS, 'ga_v2.DETAIL_JS'), ('FW_JS', GV.FW_JS, 'ga_v2.FW_JS'), ('FIT_JS', GV.FIT_JS, 'ga_v2.FIT_JS'), ('CLIP_JS', GV.CLIP_JS, 'ga_v2.CLIP_JS')]
src = ('package meai.sp;\n\n/**\n * 파이썬 판의 긴 글자 상수(CSS · JS) — golden/gen_consts.py 가 파이썬 판에서 읽어 그대로 적은 파일이다.\n'
       ' * 손으로 고치지 않는다(파이썬 판을 고친 뒤 스크립트를 다시 돌린다).\n */\npublic final class Txt {\n    private Txt() {}\n\n' + '\n'.join(const(*c) for c in C) + '}\n')
out = os.path.join(HERE, '..', 'src', 'main', 'java', 'meai', 'sp', 'Txt.java')
open(out, 'w', encoding='utf-8').write(src); print('Txt.java', len(src), '글자 ·', ', '.join('%s %d' % (c[0], len(c[1])) for c in C))
