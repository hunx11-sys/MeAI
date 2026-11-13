#!/usr/bin/env python3
"""GA 스마트 제안서 새 양식(v2) 생성 프로그램 — IT 인계 묶음 만들기

  python3 scripts/build_ga_v2_package.py        # → dist/ga_v2_generator_package.zip

· 저장소 proposal_smart 폴더에서 git 이 관리하는 파일(+ 아직 올리지 않은 새 파일, .gitignore 제외)만 담는다
  — out/ · assets/ · ga_input 의 설계서 · ga_output 결과물 · __pycache__ 는 들어가지 않는다.
· 맨 위에 README_IT.md(= proposal_smart/ga_docs/IT_GA_V2.md)와 VERSION.txt(계산 버전 · 만든 날 · 커밋)를 둔다.
· 개인정보 점검 : 담는 글자 파일 · PDF 글자층에서 전화번호(예시 번호 010-0000-0000 · 010-1234-5678 · 02-1234-5678 제외) ·
  12자리 이상 숫자(설계번호) · 「컨설턴트 : 이름」 꼴을 찾고, 환경변수 GA_V2_PERSONAL(쉼표 구분)로 넘긴 이름도 찾는다. 하나라도 있으면 멈춘다.
· 설계서 PDF(개인정보)는 넣지 않는다 — 시험은 받는 쪽 설계서로 한다.
"""
import os, re, sys, io, zipfile, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PS = os.path.join(ROOT, 'proposal_smart')
OUT = os.path.join(ROOT, 'dist', 'ga_v2_generator_package.zip')
TOP = 'ga_v2_generator'
TEXT = ('.py', '.json', '.md', '.txt', '.html', '.css', '.js', '.bat', '.sh')
OK_PHONES = {'010-0000-0000', '02-0000-0000', '010-1234-5678', '02-1234-5678'}
PHONE = re.compile(r'(?<![\d-])0\d{1,2}-\d{3,4}-\d{4}(?![\d-])')
LONGNUM = re.compile(r'(?<![\d.])\d{12,}(?![\d.])')
AGENT = re.compile(r'컨설턴트\s*[:：]\s*[가-힣]{2,4}(?![가-힣])')

def files():
    r = subprocess.run(['git', '-c', 'core.quotepath=off', 'ls-files', '--cached', '--others', '--exclude-standard', 'proposal_smart'],
                       cwd=ROOT, capture_output=True, text=True, check=True)
    out = []
    for f in sorted(set(r.stdout.split('\n'))):
        if not f or not os.path.isfile(os.path.join(ROOT, f)): continue
        rel = f[len('proposal_smart/'):]
        if rel.startswith(('ga_input/', 'ga_output/', 'out/', 'assets/')) and not rel.endswith('README.txt'): continue
        out.append(rel)
    return out

def scan(rel, data, names):
    hits = []
    ext = os.path.splitext(rel)[1].lower()
    if ext in TEXT:
        t = data.decode('utf-8', 'ignore')
    elif ext == '.pdf':
        import fitz
        t = ''.join(p.get_text() for p in fitz.open(stream=data, filetype='pdf'))
    else:
        return hits
    hits += [m for m in PHONE.findall(t) if m not in OK_PHONES]
    if ext == '.pdf': hits += LONGNUM.findall(t)
    hits += [m for m in AGENT.findall(t) if not re.search(r'컨설턴트\s*[:：]\s*(○○○|이름|성명)', m)]
    hits += [n for n in names if n in t]
    return hits

def main():
    sys.path.insert(0, PS)
    ver = re.search(r"VERSION = '([^']+)'", open(os.path.join(PS, 'api.py'), encoding='utf-8').read()).group(1)
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(['git', 'status', '--porcelain', 'proposal_smart'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    names = [w.strip() for w in os.environ.get('GA_V2_PERSONAL', '').split(',') if w.strip()]
    fl = files(); bad = []
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in fl:
            data = open(os.path.join(PS, rel), 'rb').read()
            h = scan(rel, data, names)
            if h: bad.append((rel, sorted(set(h))[:5]))
            z.writestr('%s/%s' % (TOP, rel), data)
        for d in ('ga_input', 'ga_output', 'out'):
            z.writestr('%s/%s/' % (TOP, d), b'')
        z.writestr('%s/README_IT.md' % TOP, open(os.path.join(PS, 'ga_docs', 'IT_GA_V2.md'), 'rb').read())
        z.writestr('%s/VERSION.txt' % TOP, ('GA 스마트 제안서 새 양식(v2) 생성 프로그램\n계산 버전 : %s\n만든 날 : %s\n저장소 커밋 : %s%s\n'
                   % (ver, datetime.date.today().isoformat(), commit, ' (+ 아직 올리지 않은 변경 포함)' if dirty else '')).encode('utf-8'))
    if bad:
        for b in bad: print('개인정보로 보이는 글자 :', b)
        sys.exit('개인정보 점검에 걸려 묶음을 만들지 않았습니다')
    open(OUT, 'wb').write(buf.getvalue())
    print('묶음', OUT, '· 파일 %d개 · %.1fMB · 계산 %s · 커밋 %s%s' % (len(fl) + 2, os.path.getsize(OUT) / 1e6, ver, commit, ' + 변경' if dirty else ''))

if __name__ == '__main__':
    main()
