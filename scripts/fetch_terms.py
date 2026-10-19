# -*- coding: utf-8 -*-
"""
새 약관 PDF 한꺼번에 받아 오기 — GitHub 「약관 올리는 곳」(릴리스) → 저장소 루트

왜 : 웹 화면에서 파일 올리기는 파일당 25MB 제한이 있고 하나씩 올리기 번거롭다.
     릴리스(Releases)는 파일당 2GB까지, 여러 개를 한 번에 끌어다 놓을 수 있다.

소유자가 할 일 (처음 한 번)
  1) https://github.com/hunx11-sys/MeAI/releases/new
  2) 「Choose a tag」 칸에 terms-inbox 입력 → Create new tag
  3) 제목 : 약관 올리는 곳 → 아래 상자에 약관 PDF 를 모두 끌어다 놓기 → Publish release
  다음부터는 https://github.com/hunx11-sys/MeAI/releases/tag/terms-inbox → 연필(Edit) → 끌어다 놓기 → Update release

세션이 할 일
  python3 scripts/fetch_terms.py            (받아서 비교만)
  python3 scripts/fetch_terms.py --write    (저장소 루트에 반영 : 같은 상품의 옛 판은 지운다)
  python3 scripts/fetch_terms.py --from <폴더> [--write]   (릴리스 대신 폴더의 PDF — 채팅에 첨부된 파일 등)
  반영한 뒤에는 python3 scripts/sync_all.py 로 세 산출물을 다시 맞춘다(약관 재추출 포함).

파일 이름은 믿지 않는다(릴리스는 한글·공백을 바꿔 버린다). PDF 첫 쪽의 「(무) 상품명 / 판 번호 / (심사형)」을 읽어
저장소의 이름 규칙 「무배당 상품명판번호(심사형)약관.pdf」으로 다시 붙이고, 같은 상품·심사형의 기존 파일과 짝짓는다.
"""
import glob, hashlib, io, json, os, re, shutil, sys, tempfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = 'hunx11-sys/MeAI'
TAG = 'terms-inbox'


def title_of(path):
    """PDF 첫 쪽 → (상품명, 판번호, 심사형, 판매버전, 판매개시)"""
    import pymupdf
    d = pymupdf.open(path)
    lines = [l.strip() for l in d[0].get_text().split('\n') if l.strip()]
    sale = re.search(r'판매버전\s*([\d.]+)', ' '.join(lines))
    start = re.search(r'판매개시\s*([\d.\s]+\d)', ' '.join(lines))
    i = next((k for k, l in enumerate(lines) if l.startswith('(무)')), None)
    if i is None:
        return None
    name, ver, kind = lines[i][3:].strip(), '', ''
    k = i + 1
    while k < len(lines) and not ver:
        m = re.match(r'^(.*?)\s*(\d{4})$', lines[k])
        if m:
            name = (name + ' ' + m.group(1)).strip(); ver = m.group(2)
        else:
            name = (name + ' ' + lines[k]).strip()
        k += 1
    if k < len(lines) and re.match(r'^\(.*심사형\)$', lines[k]):
        kind = lines[k]
    name = re.sub(r'\s+', ' ', name)
    return name, ver, kind, sale.group(1) if sale else '', re.sub(r'\s+', '', start.group(1)) if start else ''


def std_name(t):
    name, ver, kind = t[:3]
    return '무배당 %s%s%s약관.pdf' % (name, ver, kind)


def key(t):
    return re.sub(r'\s+', '', t[0]) + '|' + t[2]       # 같은 상품 = 상품명 + 심사형 (판 번호는 바뀔 수 있다)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def from_release(tmp):
    api = 'https://api.github.com/repos/%s/releases/tags/%s' % (REPO, TAG)
    try:
        rel = json.load(urllib.request.urlopen(api, timeout=30))
    except Exception as e:
        sys.exit('「약관 올리는 곳」(릴리스 %s)을 찾지 못했습니다 : %s\n  소유자가 이 파일 맨 위 안내대로 한 번 만들어 두어야 합니다.' % (TAG, e))
    out = []
    for a in rel.get('assets', []):
        if not a['name'].lower().endswith('.pdf'):
            continue
        p = os.path.join(tmp, '%d.pdf' % a['id'])
        print('  받는 중', a['name'], '%.1fMB' % (a['size'] / 1e6), flush=True)
        with urllib.request.urlopen(a['browser_download_url'], timeout=600) as r, open(p, 'wb') as f:
            shutil.copyfileobj(r, f)
        out.append((a['name'], p))
    return out


def main():
    write = '--write' in sys.argv
    tmp = tempfile.mkdtemp(prefix='terms_')
    if '--from' in sys.argv:
        src = sys.argv[sys.argv.index('--from') + 1]
        got = [(f, os.path.join(src, f)) for f in sorted(os.listdir(src)) if f.lower().endswith('.pdf')]   # 점으로 시작하는 이름도
    else:
        got = from_release(tmp)
    if not got:
        sys.exit('받을 약관 PDF 가 없습니다.')
    have = {}
    for p in glob.glob(os.path.join(ROOT, '*.pdf')):
        t = title_of(p)
        if t: have[key(t)] = (p, t)
    rows = []
    for orig, p in got:
        t = title_of(p)
        if not t:
            rows.append(('확인 필요', orig, '첫 쪽에서 「(무) 상품명」을 못 읽음 — 약관 PDF 가 맞는지 확인', None, None)); continue
        new = os.path.join(ROOT, std_name(t))
        old = have.get(key(t))
        if old and sha(old[0]) == sha(p):
            rows.append(('같음', std_name(t), '이미 같은 파일이 있음', None, None)); continue
        what = ('새 판' if old else '새 상품') + (' : 판매버전 %s(%s) → %s(%s)' % (old[1][3], old[1][4], t[3], t[4]) if old else ' : 판매버전 %s(%s)' % (t[3], t[4]))
        rows.append(('반영' if write else '반영 예정', std_name(t), what, p, old[0] if old else None))
    renamed = {}
    for st, nm, why, p, oldp in rows:
        print('%-6s %s  — %s' % (st, nm, why))
        if write and p:
            if oldp and os.path.abspath(oldp) != os.path.abspath(os.path.join(ROOT, nm)):
                os.remove(oldp); print('       옛 파일 지움 :', os.path.basename(oldp))
                renamed[os.path.basename(oldp)] = nm
            shutil.copyfile(p, os.path.join(ROOT, nm))
    # 스마트 제안서 보강 마스터가 약관 파일 이름을 적어 두므로(meta.sources) 새 이름으로 바꿔 둔다
    ex = os.path.join(ROOT, 'proposal_smart', 'db_terms_extra.json')
    if write and renamed and os.path.exists(ex):
        d = json.load(open(ex, encoding='utf-8'))
        src = d.get('meta', {}).get('sources') or {}
        hit = {k: renamed[v] for k, v in src.items() if v in renamed}
        if hit:
            src.update(hit)
            json.dump(d, open(ex, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            print('db_terms_extra.json 약관 이름 고침 :', ', '.join('%s → %s' % (k, v) for k, v in hit.items()))
    n = sum(1 for r in rows if r[3])
    print('\n바뀐 약관 %d개' % n + ('' if write else ' — 반영하려면 --write'))
    if write and n:
        print('다음 : python3 scripts/sync_all.py  (스마트 제안서 보강 약관 재추출 · 하네스 · 세일즈북 · 배포판)')
        print('       영업지원도구 상품(통합간편·케어프리·운전자·치아·또또암)이 바뀌었으면 특약 변경분을 tool.html 에 반영한 뒤')
        print('       same_riders.py --write · fix_body_tables.py --write 를 돌리고 sync_all 을 한다(CLAUDE.md).')
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
