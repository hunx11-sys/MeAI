# -*- coding: utf-8 -*-
"""
영업지원도구 화면 버전 표시 — ver연도.월.그 달 변경 횟수 (예 : ver2026.11.3)

정하는 법(손으로 세지 않는다 · 저장소 기록에서 센다)
  · 화면마다 그 화면 파일(특약검색기는 tool.html + tool_body.js)이 「실제로」 바뀐 커밋을 센다.
    버전 글자만 바뀐 것은 세지 않는다(버전 글자를 지우고 비교). 합치기(merge) 커밋은 빼고 센다.
  · 마지막으로 바뀐 달(한국 시간)이 버전의 연도.월, 그 달에 바뀐 횟수가 끝자리다.
    아직 커밋하지 않은 고침이 있으면 「이번 달 + 1」 로 미리 매긴다 → 커밋한 뒤 다시 돌려도 같은 번호(멱등).
  · 대문(index.html)은 사이트 전체 버전 — 일곱 화면 중 어느 것이든 바뀐 커밋을 센다.
  · 달이 바뀌면 1부터 다시. 그 달에 안 바뀐 화면은 지난 달 번호를 그대로 둔다.
표시 자리 : data-mu-ver 가 붙은 요소의 글자(없으면 처음 한 번 만들어 넣는다) · 보상시뮬레이터 머리(특약검색기와 같은 번호) ·
           상품 라인업 <title> · 맨 아래 출처 줄. DATA 안의 meta.version(데이터 판)은 건드리지 않는다.
실행 : python3 scripts/stamp_versions.py        (sync_all 이 배포판을 만들기 전에 돌린다)
       python3 scripts/stamp_versions.py --show (번호만 보기)
"""
import base64, datetime, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = {'tool.html': ['tool.html', 'tool_body.js'], 'products.html': ['products.html'], 'prompts.html': ['prompts.html'],
         '통합치료비.html': ['통합치료비.html'], '명패생성기.html': ['명패생성기.html'], 'stats.html': ['stats.html']}
SITE = sorted({f for fs in PAGES.values() for f in fs} | {'index.html'})
VER = re.compile(r'ver\d{4}(?:\.\d{2}\.\d+)?')
SIM = re.compile(r'(<script id="SIMSRC" type="text/plain">)(.*?)(</script>)', re.S)
KST = datetime.timezone(datetime.timedelta(hours=9))


def git(*a, binary=False):
    r = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True)
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace')


def norm(raw):
    """버전 글자를 지운 내용 — 이것이 같으면 「바뀌지 않음」"""
    if raw is None: return None
    s = raw.decode('utf-8', 'replace')
    m = SIM.search(s)
    if m:
        try: inner = base64.b64decode(m.group(2)).decode('utf-8', 'replace')
        except Exception: inner = m.group(2)
        s = s[:m.start(2)] + VER.sub('ver', inner) + s[m.end(2):]
    return VER.sub('ver', s)


def show(rev, path):
    r = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (rev, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def real_change(c, files):
    for f in files:
        if norm(show(c, f)) != norm(show(c + '^', f)): return True
    return False


def version(files):
    now = datetime.datetime.now(KST).strftime('%Y.%m')
    dirty = any(norm(show('HEAD', f)) != norm(open(os.path.join(ROOT, f), 'rb').read()) for f in files if os.path.exists(os.path.join(ROOT, f)))
    log = git('log', '--no-merges', '--format=%H %ct', '--', *files).split('\n')
    month, n = None, 0
    if dirty: month, n = now, 1
    for line in log:
        if not line.strip(): continue
        h, t = line.split()
        m = datetime.datetime.fromtimestamp(int(t), KST).strftime('%Y.%m')
        if month and m != month: break
        if not real_change(h, files): continue
        if month is None: month = m
        if m == month: n += 1
    return 'ver%s.%d' % (month or now, max(n, 1))


# 처음 한 번 : 버전 표시 자리 만들기(이미 있으면 그대로)
FIRST = {
    'index.html': ('<span class="k">메리츠화재 · 세일즈혁신 영업지원 아이템</span>', '<span class="mu-badge ver" data-mu-ver style="margin-left:8px">ver</span>'),
    '명패생성기.html': ('<h1>명패 제작기</h1>', '<span class="mu-badge ver" data-mu-ver>ver</span>'),
    'stats.html': ('<h1>영업지원 도구 사용 통계 <span class="sub">6개 도구 · 익명 집계</span></h1>', '<span class="mu-badge ver" data-mu-ver style="margin-left:8px">ver</span>'),
}


def stamp(page, v):
    p = os.path.join(ROOT, page)
    s = open(p, encoding='utf-8').read(); o = s
    if 'data-mu-ver' not in s:
        if page in FIRST:
            a, b = FIRST[page]
            if s.count(a) == 1: s = s.replace(a, a + b, 1)
        else:
            s = re.sub(r'<span class="ver">(ver[^<]*)</span>', r'<span class="ver" data-mu-ver>\1</span>', s, count=1)
    s = re.sub(r'(<[^>]*\bdata-mu-ver\b[^>]*>)[^<]*(<)', lambda m: m.group(1) + v + m.group(2), s)
    if page == 'products.html':
        s = re.sub(r'(<title>상품 라인업 )ver[^ <]*', lambda m: m.group(1) + v, s, count=1)
        s = re.sub(r'(교육자료-2026-71호 · <b)(?: data-mu-ver)?(>)ver[^<]*(</b>)', lambda m: m.group(1) + ' data-mu-ver' + m.group(2) + v + m.group(3), s, count=1)
    if page == 'tool.html':
        m = SIM.search(s)
        inner = base64.b64decode(m.group(2)).decode('utf-8')
        i2 = re.sub(r'(<span [^>]*>)ver[^<]*(</span></h1>)', lambda x: x.group(1) + v + x.group(2), inner, count=1)
        if i2 != inner: s = s[:m.start(2)] + base64.b64encode(i2.encode('utf-8')).decode('ascii') + s[m.end(2):]
    if s != o: open(p, 'w', encoding='utf-8').write(s)
    return s != o


def main():
    vers = {page: version(files) for page, files in PAGES.items()}
    vers['index.html'] = version(SITE)
    for page, v in vers.items():
        changed = False if '--show' in sys.argv else stamp(page, v)
        print('%-16s %s%s' % (page, v, '  (표시 고침)' if changed else ''))


if __name__ == '__main__':
    main()
