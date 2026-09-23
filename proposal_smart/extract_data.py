# -*- coding: utf-8 -*-
"""통합치료비 시뮬레이터 HTML → product_data.json 생성.
   사용 : python extract_data.py 통합치료비시뮬레이터.html
   (약관 금액표·질병 시나리오·보장 KCD 원장을 시뮬레이터에서 그대로 옮겨온다)"""
import json, re, sys, os

def js_to_py(src, i=0, env=None):
    """JS 객체/배열 리터럴 → 파이썬 값 (주석·후행쉼표·미인용 키 처리)"""
    def ws(i):
        while i < len(src):
            if src[i] in ' \t\r\n,': i += 1
            elif src.startswith('//', i): i = src.find('\n', i) + 1
            elif src.startswith('/*', i): i = src.find('*/', i) + 2
            else: break
        return i
    def val(i):
        i = ws(i); c = src[i]
        if c == '{':
            o = {}; i += 1
            while True:
                i = ws(i)
                if src[i] == '}': return o, i + 1
                if src[i] in '\'"':
                    q = src[i]; j = src.index(q, i + 1); k = src[i+1:j]; i = j + 1
                else:
                    j = i
                    while src[j] not in ':': j += 1
                    k = src[i:j].strip(); i = j
                i = src.index(':', i) + 1
                v, i = val(i); o[k] = v
        if c == '[':
            a = []; i += 1
            while True:
                i = ws(i)
                if src[i] == ']': return a, i + 1
                v, i = val(i); a.append(v)
        if c in '\'"':
            q = c; out = []; i += 1
            while src[i] != q:
                if src[i] == '\\': out.append(src[i+1]); i += 2
                else: out.append(src[i]); i += 1
            return ''.join(out), i + 1
        m = re.match(r'-?\d+(\.\d+)?([eE]-?\d+)?', src[i:])
        if m: t = m.group(0); return (float(t) if ('.' in t or 'e' in t.lower()) else int(t)), i + len(t)
        for lit, py in (('true', True), ('false', False), ('null', None)):
            if src.startswith(lit, i): return py, i + len(lit)
        m = re.match(r'[A-Za-z_$][A-Za-z0-9_$]*', src[i:])          # 미리 선언된 상수 참조
        if m and env is not None and m.group(0) in env:
            return env[m.group(0)], i + len(m.group(0))
        raise ValueError('parse error at %d : %r' % (i, src[i:i+40]))
    return val(i)[0]

def grab(src, name, env=None):
    m = re.search(r'(?:\bconst\s+|,\s*)%s\s*=\s*' % name, src)
    if not m: raise KeyError(name)
    return js_to_py(src, m.end(), env)

if __name__ == '__main__':
    html = open(sys.argv[1], encoding='utf-8').read()
    env = {}
    for k in ('ALLC', 'MAL', 'SIM', 'MIN'):                        # IT 정의가 참조하는 질병분류 상수
        try: env[k] = grab(html, k, env)
        except KeyError: pass
    out = {k: grab(html, k, env) for k in ('EMB', 'AMT', 'RIDERS', 'IT', 'GLOSS', 'DZ', 'CHIPS', 'DEFAULT_COMBO')}
    out.update(env)
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_data.json')
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    print('product_data.json 생성 :', dst,
          '| 특약', len(out['RIDERS']), '· 질병 시나리오', len(out['DZ']), '· KCD', len(out['EMB']['kcd']))
