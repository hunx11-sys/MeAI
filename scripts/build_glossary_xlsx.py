#!/usr/bin/env python3
"""
보험용어사전 엑셀 만들기
- 저장소 루트에서 실행: python3 scripts/build_glossary_xlsx.py
- 결과: dist/보험용어사전.xlsx

gloss.js 의 뜻풀이와 tool.html 의 약관 데이터를 맞대어, 용어마다
'약관이나 특약 이름에서 실제로 이렇게 쓰인다' 는 예시를 한 줄씩 붙인다.
뜻이 같은 말(계약자·보험계약자·가입자)은 한 줄로 묶고 나머지는 별칭 칸으로 보낸다.

약관이 개정되면 recover_terms.py 를 먼저 돌린 뒤 이 스크립트를 다시 돌리면 된다.
"""
import collections, datetime, json, os, re, unicodedata
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from tooldata import inflate, deflate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist', '보험용어사전.xlsx')
NO_EX = '약관에는 안 나오는 일반 용어'
ENDS = ('합니다.', '입니다.', '됩니다.', '한다.', '말합니다.', '같습니다.', '없습니다.')

# ── 자료 읽기 ──────────────────────────────────────────────
html = open(os.path.join(ROOT, 'tool.html'), encoding='utf-8').read()
D = inflate(json.loads(re.search(r'<script id="DATA" type="application/json">(.*?)</script>', html, re.S).group(1)))
G = json.loads(re.search(r'var G = (\{.*?\});\s*\n',
                         open(os.path.join(ROOT, 'gloss.js'), encoding='utf-8').read(), re.S).group(1))
riders, tables = D['riders'], D['tables']


def clean(t):
    """PDF 에서 온 제어문자·글꼴 전용문자를 없애 읽을 수 있는 글로 만든다"""
    t = t.replace('', ' ')
    t = ''.join(' ' if (unicodedata.category(c)[0] == 'C' and c != '\n') else c for c in t)
    return re.sub(r'[ \t]+', ' ', t)


BODY = {r['id']: clean(r.get('b') or '') for r in riders}


# ── 같은 뜻풀이를 쓰는 말끼리 한 줄로 묶는다 ────────────────
def headword(names):
    """대표로 내세울 말 : 약관에 실제로 쓰이는 정식 표현을 앞세운다"""
    def score(t):
        used = sum(1 for r in riders if t in (r.get('n') or '')) * 50 \
             + min(sum(1 for r in riders if t in (r.get('b') or '')), 200)
        # 약관에 안 나오는 말끼리는 '풀어 쓴 설명'보다 정식 낱말을 고른다
        formal = (' ' not in t) + (not t[0].isdigit()) + (not re.search(r'[은는이가을를]$', t))
        return (used, formal, len(t))
    return sorted(names, key=score, reverse=True)[0]


# ── 예시 한 줄 찾기 ────────────────────────────────────────
def trim(s, term):
    """약관 문장을 사람이 읽을 만한 한 줄로 다듬는다. 낱말 중간에서 끊지 않는다."""
    s = re.sub(r'\s+', ' ', s).strip()
    i = s.find(term)
    if i < 0:
        return ''
    a, b = 0, len(s)
    if len(s) > 95:                       # 길면 용어 앞뒤로만 남긴다
        a, b = max(0, i - 34), min(len(s), i + len(term) + 50)
    head = ''
    if a > 0 or not re.match(r'^(회사|이|제\d|\d|[「【])', s):
        sp = s.find(' ', a)
        if 0 <= sp < i:
            a, head = sp + 1, '…'
    tail, seg = '', s[a:b]
    if not seg.rstrip().endswith(ENDS):
        sp = seg.rfind(' ')
        if sp > (i - a) + len(term):
            seg = seg[:sp]
        tail = '…'
    seg = seg.strip(' ,·')
    return head + seg + tail if term in seg else ''


def name_example(term):
    """특약 이름에 그대로 들어간 경우 — 가장 좋은 예시"""
    hits = [r for r in riders if term in (r.get('n') or '')]
    if not hits:
        return None
    r = min(hits, key=lambda x: len(x['n']))
    extra = f' · 이 말이 들어간 특약 {len(hits)}건' if len(hits) > 1 else ''
    return (f'{r["p"]} 「{r["n"]}」', f'특약 이름{extra}')


def body_example(term):
    """약관 본문에서 그 용어가 들어간 짧은 문장 하나"""
    best = None
    for r in riders:
        body = BODY[r['id']]
        i = body.find(term)
        if i < 0:
            continue
        st = max(body.rfind('\n', 0, i), body.rfind('. ', 0, i) + 1, 0)
        en = len(body)
        for e in ENDS:                    # 가장 가까운 문장 끝
            j = body.find(e, i)
            if j > 0:
                en = min(en, j + len(e))
        j = body.find('\n', i)
        if j > 0:
            en = min(en, j)
        s = body[st:en]
        if s.count('(') > s.count(')'):   # 열린 괄호로 끝나지 않게
            s = s[:s.rfind('(')]
        s = trim(s, term)
        if len(s) < 15:
            continue
        if best is None or len(s) < len(best[0]):
            best = (s, r)
        if len(s) < 55:
            break
    if not best:
        return None
    s, r = best
    return (s, f'약관 본문 · {r["p"]} 「{r["n"]}」')


def table_example(term):
    for k, t in tables.items():
        txt = clean(t.get('text') or '')
        if term not in txt:
            continue
        for line in txt.split('\n'):
            line = line.strip()
            if term in line and 4 <= len(line) <= 80:
                return (line, f'분류표 · {t.get("name") or k}')
    return None


def loose_example(term):
    """띄어쓰기·가운뎃점만 다른 경우까지 찾는다 (최경증치매 ↔ 최경증 치매)"""
    pat = re.compile(r'[\s·]*'.join(map(re.escape, term)))
    for r in riders:
        if pat.search(r.get('n') or ''):
            return (f'{r["p"]} 「{r["n"]}」', '특약 이름')
    for r in riders:
        body = BODY[r['id']]
        m = pat.search(body)
        if not m:
            continue
        st = max(body.rfind('\n', 0, m.start()), 0)
        en = len(body)
        for e in ENDS:
            j = body.find(e, m.end())
            if j > 0:
                en = min(en, j + len(e))
        j = body.find('\n', m.start())
        if j > 0:
            en = min(en, j)
        seg = re.sub(r'\s+', ' ', body[st:en]).strip()
        if 15 <= len(seg) <= 110:
            return (seg, f'약관 본문 · {r["p"]} 「{r["n"]}」')
    return None


def build_rows():
    by_def = collections.defaultdict(list)
    for t, v in G.items():
        by_def[(v.get('d'), v.get('c'))].append(t)

    rows = []
    for (d, c), names in by_def.items():
        head = headword(names)
        alias = [n for n in names if n != head]
        ex = None
        for t in [head] + alias:          # 대표어로 못 찾으면 별칭으로도 찾아본다
            ex = name_example(t) or body_example(t) or table_example(t)
            if ex:
                break
        if ex is None:                    # 띄어쓰기만 다른 경우까지
            for t in [head] + alias:
                ex = loose_example(t)
                if ex:
                    break
        rows.append({'term': head, 'cat': c or '', 'def': d or '',
                     'tip': G[head].get('n') or '', 'alias': ' · '.join(alias),
                     'ex': ex[0] if ex else '', 'src': ex[1] if ex else NO_EX})
    rows.sort(key=lambda r: (r['cat'], r['term']))
    return rows


# ── 엑셀 쓰기 ──────────────────────────────────────────────
F = '맑은 고딕'                            # 한글 문서의 기본 서체
NAVY, BLUE, LGRAY, LINE = '1B3A5C', '3182F6', 'F2F4F6', 'D1D6DB'
head_fill = PatternFill('solid', fgColor=NAVY)
band_fill = PatternFill('solid', fgColor='F7F9FC')
thin = Side(style='thin', color=LINE)
box = Border(left=thin, right=thin, top=thin, bottom=thin)

COLS = [('번호', 6), ('분류', 13), ('용어', 20), ('쉬운 뜻', 58),
        ('알아두기', 44), ('다르게 부르는 말', 22),
        ('약관·특약에서 이렇게 쓰여요', 50), ('예시를 가져온 곳', 40)]


def sheet_dict(wb, rows):
    ws = wb.active
    ws.title = '보험용어사전'
    for i, (name, w) in enumerate(COLS, 1):
        c = ws.cell(1, i, name)
        c.font = Font(name=F, bold=True, color='FFFFFF', size=10.5)
        c.fill = head_fill
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 32

    for n, r in enumerate(rows, start=1):
        vals = [n, r['cat'], r['term'], r['def'], r['tip'], r['alias'], r['ex'], r['src']]
        for i, v in enumerate(vals, 1):
            c = ws.cell(n + 1, i, v)
            c.font = Font(name=F, size=10, bold=(i == 3),
                          color='8B95A1' if i == 8 else '191F28')
            c.alignment = Alignment(vertical='top', wrap_text=(i >= 4),
                                    horizontal='center' if i in (1, 2) else 'left')
            c.border = box
            if n % 2 == 0:
                c.fill = band_fill
        ws.row_dimensions[n + 1].height = 30

    last = len(rows) + 1
    ws.freeze_panes = 'C2'                # 번호·분류·용어는 늘 보이게
    ws.auto_filter.ref = f'A1:H{last}'
    ws.sheet_view.showGridLines = False
    return last


def sheet_summary(wb, rows, last):
    """개수는 손으로 적지 않고 수식으로 센다. 표를 고치면 따라 바뀐다."""
    ws = wb.create_sheet('분류별 개수')
    cats = sorted({r['cat'] for r in rows})
    for i, name in enumerate(['분류', '용어 수', '약관 예시가 있는 것', '예시 비율'], 1):
        c = ws.cell(1, i, name)
        c.font = Font(name=F, bold=True, color='FFFFFF', size=10.5)
        c.fill = head_fill
        c.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 26

    for i, cat in enumerate(cats, start=2):
        ws.cell(i, 1, cat)
        ws.cell(i, 2, f'=COUNTIF(보험용어사전!$B$2:$B${last},$A{i})')
        ws.cell(i, 3, f'=COUNTIFS(보험용어사전!$B$2:$B${last},$A{i},'
                      f'보험용어사전!$H$2:$H${last},"<>{NO_EX}")')
        ws.cell(i, 4, f'=IFERROR($C{i}/$B{i},0)')
        ws.cell(i, 4).number_format = '0.0%'
        for j in range(1, 5):
            ws.cell(i, j).font = Font(name=F, size=10)
            ws.cell(i, j).border = box
            ws.cell(i, j).alignment = Alignment(horizontal='left' if j == 1 else 'center')

    t = len(cats) + 2
    ws.cell(t, 1, '합계')
    ws.cell(t, 2, f'=SUM(B2:B{t - 1})')
    ws.cell(t, 3, f'=SUM(C2:C{t - 1})')
    ws.cell(t, 4, f'=IFERROR($C{t}/$B{t},0)')
    ws.cell(t, 4).number_format = '0.0%'
    for j in range(1, 5):
        ws.cell(t, j).font = Font(name=F, bold=True, size=10)
        ws.cell(t, j).border = box
        ws.cell(t, j).fill = PatternFill('solid', fgColor=LGRAY)
        if j > 1:
            ws.cell(t, j).alignment = Alignment(horizontal='center')
    for col, w in zip('ABCD', (16, 10, 18, 10)):
        ws.column_dimensions[col].width = w
    ws.sheet_view.showGridLines = False


def sheet_howto(wb):
    ws = wb.create_sheet('사용법·출처')
    m = D['meta']
    pc = m.get('prodcount', {})
    prod = ' · '.join(f'{k} {v}건' for k, v in pc.items())
    lines = [
        ('제목', '보험용어사전'),
        ('', ''),
        ('h', '이 파일은'),
        ('', '약관에 나오는 어려운 보험용어를 현장에서 바로 읽을 수 있게 풀어 쓴 사전입니다.'),
        ('', '말마다 그 말이 실제 약관이나 특약 이름에서 어떻게 쓰이는지 한 줄씩 붙였습니다.'),
        ('', ''),
        ('h', '찾는 방법'),
        ('', '· 첫 줄의 ▼ 를 눌러 분류(암·뇌심장·치아 등)로 걸러 보세요.'),
        ('', '· 특정 낱말은 Ctrl+F 로 찾으세요. 「다르게 부르는 말」 칸도 같이 찾습니다.'),
        ('', '· 「용어」 칸까지 화면에 고정돼 있어 오른쪽으로 넘겨도 무슨 말인지 보입니다.'),
        ('', ''),
        ('h', '칸 설명'),
        ('', '쉬운 뜻 ............... 고객에게 그대로 말해도 되는 표현으로 풀어 썼습니다.'),
        ('', '알아두기 .............. 현장에서 자주 헷갈리는 점, 놓치기 쉬운 조건입니다.'),
        ('', '다르게 부르는 말 ...... 같은 뜻인데 약관·현장에서 달리 부르는 말입니다.'),
        ('', '약관·특약에서 이렇게 쓰여요 ... 실제 특약 이름 또는 약관 문장에서 그대로 가져왔습니다.'),
        ('', '                               … 표시는 문장 앞뒤를 줄였다는 뜻입니다.'),
        ('', ''),
        ('h', '출처'),
        ('', '· 용어 뜻풀이 : 「메리츠 인보험 마스터북」을 바탕으로 정리'),
        ('', f'· 예시 문장 : 영업지원도구 특약검색 내장 약관 데이터 {m.get("version")}'),
        ('', f'            ({prod}, 특약 {m.get("total")}건)'),
        ('', '· 원본 약관 : 통합간편 2607, 케어프리 M-Basket 2607, 운전자 2608, 치아 2601'),
        ('', ''),
        ('h', '알아두실 점'),
        ('', '· 예시는 약관 원문에서 기계로 뽑아 붙인 것입니다. 실제 보장 여부와 지급금액은'),
        ('', '  반드시 약관 원문을 확인하세요.'),
        ('', f'· 「예시를 가져온 곳」이 "{NO_EX}"인 줄은, 약관에 그 낱말이'),
        ('', '  직접 나오지는 않지만 상담할 때 쓰는 의학·제도 용어입니다.'),
        ('', '· 상품이 개정되면 약관이 바뀝니다. 이 파일은 위에 적은 판을 기준으로 만들었습니다.'),
        ('', ''),
        ('', f'만든 날짜 : {datetime.date.today().isoformat()}   ·   세일즈혁신TF {m.get("contact", "")}'),
    ]
    for i, (kind, text) in enumerate(lines, start=1):
        c = ws.cell(i, 1, text)
        if kind == '제목':
            c.font = Font(name=F, bold=True, size=18, color=NAVY)
        elif kind == 'h':
            c.font = Font(name=F, bold=True, size=11.5, color=BLUE)
        else:
            c.font = Font(name=F, size=10.5, color='333D4B')
        c.alignment = Alignment(vertical='center')
    ws.column_dimensions['A'].width = 104
    ws.sheet_view.showGridLines = False


def main():
    rows = build_rows()
    wb = Workbook()
    last = sheet_dict(wb, rows)
    sheet_summary(wb, rows, last)
    sheet_howto(wb)
    wb.move_sheet('사용법·출처', offset=-2)   # 열었을 때 안내가 먼저 보이게
    wb.active = 1                             # 기본 선택은 사전 시트
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print(f'-> {os.path.relpath(OUT, ROOT)} · 표제어 {len(rows)}개 '
          f'· 분류 {len({r["cat"] for r in rows})}개 '
          f'· 약관 예시 있음 {sum(1 for r in rows if r["ex"])}개')


if __name__ == '__main__':
    main()
