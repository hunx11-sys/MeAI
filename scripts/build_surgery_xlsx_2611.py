# -*- coding: utf-8 -*-
"""
수술비 4종(130대 · 131대질병수술비 · 1-5종 수술분류표Ⅱ · 1-7종 수술분류표) — 보장 KCD · 수술행위 정리 엑셀 (2611판)

2610 약관(2026-10-31 개정)을 기준으로 다시 만든다. 앞 판(scripts/build_surgery_xlsx.py → dist/surgery_benefit_kcd_2610.xlsx)은 그대로 둔다.

원천
  · 특약 마스터 : tool.html(영업지원도구 · 감수본) + proposal_smart/db_terms_extra.json(스마트 제안서 보강 · 약관 파싱)
  · 수술비 비교 표 : tool.html 의 SC.detail(1-5종Ⅱ 99줄) · SC.d17(1-7종 계통·해설) · SC.d131(131대 대상질병 356줄)
  · 대표 질병 : docs/surgery_rep_diseases.json (검수본 · WHO ICD-10 대조) — 새 질병코드는 만들지 않는다.
    130대 · 131대 시트의 예시는 이 파일의 질병 중 그 줄의 KCD 범위 안에 드는 것만 골라 붙인다.
  · 약관 PDF(저장소 루트, 상품마다 2610 판 하나) — 목차에서 특약 · 별표 쪽을 찾고, 별표를 직접 읽어 마스터와 대조한다.
    (두 단 조판 : 왼쪽 단 → 오른쪽 단 순서로 읽고, 별표는 다음 별표 머리까지 여러 쪽을 이어 읽는다)

실행 : python3 scripts/build_surgery_xlsx_2611.py [출력.xlsx]   (기본 dist/surgery_benefit_kcd_2611.xlsx)
       대조에서 어긋난 것이 있으면 「약관 대조」 시트와 화면에 '확인 필요' 로 나온다(마스터는 고치지 않는다).
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import PAT, inflate, ROOT
from same_riders import _expand, covers, red_note
import pymupdf
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist', 'surgery_benefit_kcd_2611.xlsx')
OLD = os.path.join(ROOT, 'dist', 'surgery_benefit_kcd_2610.xlsx')
BUILD_DATE = '2026-11-03'
FONT = 'Arial'
HEAD = PatternFill('solid', fgColor='0B7C6F')
NOTE = PatternFill('solid', fgColor='E6F6F2')
WARN = PatternFill('solid', fgColor='FFF4E5')
THIN = Side(style='thin', color='D5DCE4')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# ── 상품 : (표시명, 마스터 상품키, 마스터 출처, 약관 파일, 비고) ──
TOOL, EXTRA = '영업지원도구(tool.html)', '스마트 제안서 보강(db_terms_extra.json)'
PRODUCTS = [
    ('케어프리 M-Basket', '케어프리', TOOL, '무배당 메리츠 케어프리보험 M-Basket2610약관.pdf', '세만기 · 비갱신 기반(일부 갱신형)'),
    ('알파Plus(GA)', '케어프리', TOOL, '무배당 알파Plus보장보험2610약관.pdf', 'GA 판매명 — 케어프리 M-Basket 과 특약 구성 같음'),
    ('통합간편(통합간편심사형)', '통합간편', TOOL, '무배당 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형)약관.pdf', ''),
    ('통합간편(일반심사형)', '통합간편', TOOL, '무배당 메리츠 통합간편건강보험(세만기형)2610(일반심사형)약관.pdf', '2610 에 약관 추가(영업지원도구 마스터는 통합간편 하나로 씀)'),
    ('통합간편(355입원·수술고지간편심사형)', '통합간편', TOOL, '무배당 메리츠 통합간편건강보험(세만기형)2610(355입원,수술고지간편심사형)약관.pdf', '2610 에 약관 추가(영업지원도구 마스터는 통합간편 하나로 씀)'),
    ('운전자 상해 종합', '운전자', TOOL, '무배당 메리츠 운전자 상해 종합보험2610약관.pdf', ''),
    ('또또암(일반심사형)', '또또암', TOOL, '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(일반심사형)약관.pdf', '이 4종 수술비 특약은 없음 — 통합치료비가 1-5종Ⅱ를 수술 정의로 씀'),
    ('또또암간편(맞춤간편심사형)', '또또암간편', TOOL, '무배당 메리츠 또 걸려도 또 받는 암보험(세만기형)2610(맞춤간편심사형)약관.pdf', '이 4종 수술비 특약 없음'),
    ('The좋은 케어프리 M-Basket', 'The좋은케어프리', EXTRA, '무배당 메리츠 The좋은 케어프리보험 M-Basket2610약관.pdf', '연만기 · 전 특약 갱신형(케어프리 M-Basket 과 다른 상품)'),
    ('The좋은 알파Plus(GA)', 'The좋은케어프리', EXTRA, '무배당 메리츠 The좋은 알파Plus보장보험2610약관.pdf', 'GA 판매명 — The좋은 케어프리와 특약 구성 같음'),
    ('The건강한 5.10.5', 'The건강한5.10.5', EXTRA, '무배당 메리츠 The건강한 5.10.5 보장보험2610약관.pdf', ''),
    ('The건강한 내Mom대로 5.10.5', 'The건강한내Mom대로5.10.5', EXTRA, '무배당 메리츠 The건강한 내Mom대로 5.10.5 보장보험2610약관.pdf', ''),
    ('내Mom대로', '내Mom대로', EXTRA, '무배당 내Mom대로 보장보험2610약관.pdf', ''),
    ('내Mom같은 어린이(태아전용)', '내Mom같은어린이', EXTRA, '무배당 내Mom같은 어린이보험2610(태아전용)약관.pdf', '내Mom같은 어린이 태아고급형 수술비(1-7종)는 「1-7종 수술분류표Ⅱ」(선천기형 수술 10개 더함) · 일반 수술비(1-7종)는 「1-7종 수술분류표」'),
    ('The좋은 내Mom대로', 'The좋은내Mom대로', EXTRA, '무배당 메리츠 The좋은 내Mom대로 보장보험2610약관.pdf', ''),
    ('The가벼운 간편355', 'The가벼운간편355', EXTRA, '무배당 The가벼운 간편355건강보험(세만기형)2610약관.pdf', ''),
    ('간편31', '간편31', EXTRA, '무배당 메리츠 간편31 건강보험2610약관.pdf', ''),
]
P131 = '무배당 메리츠 케어프리보험 M-Basket2610약관.pdf'          # 131대 · 1-5종Ⅱ · 1-7종 근거 쪽의 기준 약관
P130 = '무배당 메리츠 통합간편건강보험(세만기형)2610(통합간편심사형)약관.pdf'   # 130대 근거 쪽의 기준 약관
P17X = '무배당 내Mom같은 어린이보험2610(태아전용)약관.pdf'         # 1-7종 수술분류표Ⅱ(태아고급형)

KIND_ORDER = ['130대', '131대', '1-5종Ⅱ', '1-7종', '1-5종Ⅱ(참고 · 통합치료비 수술 정의)']
SUBTABLES = ['심장질환', '뇌혈관질환', '특정31대질병', '다빈도6[12]대질병', '유방의장애', '편도염', '특정다빈도29대질병',
             '후각특정질환', '관절염[,ㆍ·․]생식기질환', '치핵', '백내장']


# ───────────────────────── 약관 PDF ─────────────────────────
class Pdf:
    def __init__(self, fn):
        self.fn = fn
        self.doc = pymupdf.open(os.path.join(ROOT, fn))
        self._c, self._r = {}, {}
        self._toc = None

    def n(self):
        return len(self.doc)

    def text(self, n):
        """1부터 세는 쪽 · 두 단 조판 → 왼쪽 단, 오른쪽 단 순서"""
        if n not in self._c:
            p = self.doc[n - 1]; w = p.rect.width
            bl = [b for b in p.get_text('blocks') if b[6] == 0]
            bl.sort(key=lambda b: (0 if b[0] < w / 2 - 5 else 1, b[1], b[0]))
            self._c[n] = '\n'.join(b[4] for b in bl)
        return self._c[n]

    def raw(self, n):
        if n not in self._r:
            self._r[n] = self.doc[n - 1].get_text()
        return self._r[n]

    def toc(self):
        """목차 : 특약 [(번호, 이름, 인쇄쪽)] · 별표 {번호: (이름, 인쇄쪽)}"""
        if self._toc is None:
            riders, bp = [], {}
            last = 0
            for i in range(1, min(90, self.n()) + 1):
                t = self.raw(i)
                if '....' not in t: continue
                last = i
                t = re.sub(r'\n(?!\d+(?:-\d+)?\.\s|\s*【)', ' ', t)
                for m in re.finditer(r'(\d+(?:-\d+)?)\.\s*((?:(?!\.{3}).)*?특별약관)[^.\n]{0,60}?\.{3,}\s*(\d+)', t):
                    riders.append((m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip(), int(m.group(3))))
                for m in re.finditer(r'【별표\s*([^】]+?)】\s*((?:(?!\.{3}).)*?)\s*\.{3,}\s*(\d+)', t):
                    bp.setdefault(m.group(1).strip(), (re.sub(r'\s+', ' ', m.group(2)).strip(), int(m.group(3))))
            self._toc = (riders, bp, last)
        return self._toc

    def bpyo(self, name_re):
        """이름이 맞는 별표 → (번호, 이름, 시작 PDF쪽, 끝 PDF쪽, 인쇄쪽 차이)"""
        riders, bp, last = self.toc()
        cands = [(k, v) for k, v in bp.items() if re.search(name_re, v[0])]
        if not cands: return None
        k, (nm, pp) = cands[0]
        start = None
        for n in range(max(last + 1, pp - 2), min(self.n(), pp + 6) + 1):
            if '【별표%s】' % k in self.text(n).replace(' ', ''):
                start = n; break
        if start is None: return None
        nxt = sorted(v[1] for v in bp.values() if v[1] > pp)
        end = min(self.n(), (nxt[0] + start - pp) if nxt else start + 6)
        return k, nm, start, max(start, end), start - pp

    def body(self, num, start, end):
        """별표 글 — 머리부터 다음 별표 머리 앞까지(여러 쪽)"""
        txt = '\n'.join(self.text(n) for n in range(start, end + 1))
        m = re.search(r'【별표\s*' + re.escape(num) + r'\s*】', txt)
        txt = txt[m.start():] if m else txt
        m = re.search(r'【별표\s*[^】(]+】', txt[5:])
        return txt[:m.start() + 5] if m else txt

    def rider_text(self, no, name, printed):
        """목차의 특약 → (PDF쪽, 본문 — 다음 특약 머리 앞까지)"""
        key = re.sub(r'\s+', '', name)[:12]
        for n in range(max(1, printed - 1), min(self.n(), printed + 5) + 1):
            s = re.sub(r'\s+', '', self.text(n))
            i = s.find(no + '.' + key)
            if i < 0: continue
            body = s[i:] + ''.join(re.sub(r'\s+', '', self.text(j)) for j in range(n + 1, min(self.n(), n + 6) + 1))
            # 다음 특약 머리 — 같은 본문을 같이 쓰는 바로 옆 특약(「2-149. … 2-150. 갱신형 …」)은 건너뛴다
            for m in re.finditer(r'\d+(?:-\d+)?\.(?:(?!제\d+조).){2,80}?특별약관(?:＊[^제]{0,90})?제1조\(', body[len(no) + 20:]):
                if m.start() > 400: return n, body[:len(no) + 20 + m.start()]
            return n, body[:12000]
        return None, ''


_PDF = {}
def pdf(fn):
    if fn not in _PDF: _PDF[fn] = Pdf(fn)
    return _PDF[fn]


# ───────────────────────── 마스터 ─────────────────────────
def load():
    html = io.open(os.path.join(ROOT, 'tool.html'), encoding='utf-8').read()
    D = inflate(json.loads(re.search(PAT, html, re.S).group(2)))
    blk = html[html.index('/* === 수술비 비교'):]
    SC, _ = json.JSONDecoder().raw_decode(blk[blk.index('var SC = ') + 9:])
    d17 = json.loads(re.search(r'SC\.d17=(\[.*?\]);\n', blk).group(1))
    d131 = json.loads(re.search(r'SC\.d131=(\[.*?\]);\n', blk).group(1))
    EX = json.load(io.open(os.path.join(ROOT, 'proposal_smart', 'db_terms_extra.json'), encoding='utf-8'))
    R = json.load(io.open(os.path.join(ROOT, 'docs', 'surgery_rep_diseases.json'), encoding='utf-8'))
    return D, SC, d17, d131, EX, R


def norm_tok(t):
    t = t.strip().replace('∼', '~')
    return re.sub(r'(?<=\d)-(?=[A-Z]?\d)', '~', t)


TOK = re.compile(r'(?<![A-Z0-9])([A-Z]\d{2}(?:\.\d{1,2})?)(?:\s*[†\*\+])?(?:\s*[∼~\-]\s*([A-Z]?\d{2}(?:\.\d{1,2})?))?')
def toks(t):
    t = re.sub(r'제\s*20\d\d\s*-\s*\d+\s*호', '', t)
    out = set()
    for m in TOK.finditer(t):
        a, b = m.group(1), m.group(2)
        out.add(norm_tok(a + ('~' + (b if b[0].isalpha() else a[0] + b) if b else '')))
    return out - {'P00~P96'}


def reduce_note(body):
    """특약 지급표의 감액 구간 — 두 단 표가 섞여 읽히므로 「경과시점」 구간과 100% 미만 지급률을 짧은 구간부터 짝지음"""
    if not body: return ''
    k = body.find('제3조(')
    s = body[:k] if k > 0 else body[:6000]
    per = sorted(set(re.findall(r'계약일부터(\d+)(일|년)경과시점', s)), key=lambda x: int(x[0]) * (365 if x[1] == '년' else 1))
    if not per: return '감액 없음'
    i = s.find('지급금액')
    seq = [float(x) for x in re.findall(r'의(\d+(?:\.\d+)?)%', s[i if i >= 0 else 0:])]
    head = seq[:len(per) + 1]
    if len(head) == len(per) + 1 and head == sorted(head) and head[-1] == 100:
        low = head[:-1]
    else:
        low = sorted({v for v in seq if v < 100})
        if len(low) != len(per):
            return '감액 구간 %s — 지급표 직접 확인' % ' · '.join(a + b for a, b in per)
    out = ' · '.join('가입 %s%s 내 %s%%' % (a, b, ('%g' % p)) for (a, b), p in zip(per, low)) + ' 지급'
    return out + (' (체증형 : 1회차 기준)' if '회차' in s else '')


def kind_of(name):
    if '1-7종' in name: return '1-7종'
    if '1-5종' in name or '1~5종' in name: return '1-5종Ⅱ'
    if '131대질병수술비' in name.replace(' ', ''): return '131대'
    if '130대질병수술비' in name.replace(' ', ''): return '130대'
    return None


def nname(s):
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'\((편한|건강|31간편|통합간편|355입원,수술고지간편)가입\)', '', s)
    return re.sub(r'(보장)?특별약관$', '', s)


# ───────────────────────── 대조(약관 PDF ↔ 마스터) ─────────────────────────
def t17(D, tid='34700df0f3'):
    T, g = [], None
    for l in D['tables'][tid]['text'].split('\n'):
        mg = re.match(r'■\s*(\d+)\.\s*(.*)', l)
        if mg: g = (int(mg.group(1)), mg.group(2).strip())
        mm = re.match(r'\s*\[([A-Z]\d{3})\]\s*(.*?)\s*→\s*(\d)종', l)
        if mm: T.append((g, mm.group(1), mm.group(2), int(mm.group(3))))
    return T


def pdf17(P, start, end, num):
    """1-7종 별표 : 수술코드 → (종, PDF쪽). 표 칸이 「코드\\n종」으로 읽힌다(쪽 글자 그대로).
    첫 쪽은 이 별표 머리부터, 끝 쪽은 다음 별표 머리 앞까지만 읽는다(앞뒤 별표의 수가코드가 섞이지 않게)"""
    out = {}
    for n in range(start, end + 1):
        t = P.raw(n)
        if n == start:
            m = re.search(r'【별표\s*' + re.escape(num) + r'\s*】', t)
            if m: t = t[m.start():]
        m = re.search(r'【별표\s*[^】(]+】', t[5:] if n == start else t)
        if m:
            t = t[:m.start() + (5 if n == start else 0)]
        for c, j in re.findall(r'\b([A-Z]\d{3})\s*\n?\s*([1-7])\s*(?:\n|$)', t):
            out.setdefault(c, (int(j), n))
    return out


def pdf15(P, start):
    """1-5종 수술분류표Ⅱ : 표 칸에서 (계통, 수술명 칸 글, [종...], PDF쪽)"""
    rows, n, done = [], start, False
    while not done and n < start + 8:
        p = P.doc[n - 1]; W = p.rect.width
        for t in sorted(p.find_tables().tables, key=lambda t: (0 if t.bbox[0] < W / 2 - 5 else 1, t.bbox[1])):
            data = t.extract()
            hdr = ' '.join(c or '' for c in data[0])
            if not re.search(r'수술\s*종류|수술명|방사선', hdr): continue
            for r in data[1:]:
                cells = [(c or '').strip() for c in r]
                if len(cells) < 2: continue
                name, jong = cells[-2], cells[-1]
                if not re.fullmatch(r'[1-5](\s+[1-5])*', jong): continue
                rows.append({'grp': cells[0] if len(cells) > 2 else '', 'name': name, 'jong': jong.split(), 'page': n})
            if '방사선' in hdr: done = True
        n += 1
    return rows


def split15(rows):
    """표 줄(11 · 13 · 88 · Ⅱ-1 처럼 종이 여럿인 칸)을 하위 항목으로 나눠 99줄로"""
    out = []
    for r in rows:
        txt = r['name']
        if len(r['jong']) == 1:
            out.append((txt, r['jong'][0], r['page'], r['grp'])); continue
        parts = re.split(r'\n(?=\s*(?:\d+-\d+\.|1-1\.))', txt)
        head, subs = parts[0], parts[1:]
        if len(subs) != len(r['jong']):
            subs = [''] * len(r['jong'])
        for s, j in zip(subs, r['jong']):
            out.append(((head + '\n' + s).strip(), j, r['page'], r['grp']))
    return out


def clean(s):
    s = re.sub(r'(?<=[가-힣\w,·(])\n(?=[가-힣\w)])', '', s)   # 칸 안 줄바꿈 이어 붙임
    s = re.sub(r'[ \t]*\n[ \t]*', '\n', s)
    return re.sub(r'[ \t]{2,}', ' ', s).strip()


# ───────────────────────── 엑셀 ─────────────────────────
def sheet(wb, title, headers, rows, widths, note=None, warn_col=None):
    ws = wb.create_sheet(title)
    r0 = 1
    if note:
        c = ws.cell(1, 1, note)
        c.font = Font(name=FONT, size=10, color='1F3B4D'); c.fill = NOTE
        c.alignment = Alignment(wrap_text=True, vertical='center')
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
        ws.row_dimensions[1].height = max(30, 14 * (1 + int(len(note) * 1.9 / max(40, sum(widths)))) + 8)
        r0 = 2
    for j, h in enumerate(headers, 1):
        c = ws.cell(r0, j, h)
        c.font = Font(name=FONT, bold=True, color='FFFFFF'); c.fill = HEAD; c.border = BOX
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[r0].height = 32
    for i, row in enumerate(rows, r0 + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v)
            c.font = Font(name=FONT, size=10); c.border = BOX
            c.alignment = Alignment(vertical='top', wrap_text=True)
        if warn_col is not None and isinstance(row[warn_col], str) and (row[warn_col] == '확인 필요' or '⚠' in row[warn_col]):
            for j in range(1, len(row) + 1): ws.cell(i, j).fill = WARN
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(r0 + 1, 3 if len(headers) > 6 else 1)
    ws.auto_filter.ref = '%s:%s%d' % (ws.cell(r0, 1).coordinate, get_column_letter(len(headers)), r0 + len(rows))
    print_fit(ws, r0)
    return ws


def print_fit(ws, head_row=None):
    """인쇄 : 가로 · 폭 맞춤 · 머리줄 반복"""
    ws.page_setup.orientation = 'landscape'; ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.page_margins.left = ws.page_margins.right = 0.3
    if head_row: ws.print_title_rows = '%d:%d' % (head_row, head_row)


def main():
    D, SC, d17, d131, EX, R = load()
    by = {r['id']: r for r in D['riders']}
    exby = {r['id']: r for r in EX['riders']}
    T = t17(D)
    T17 = {c: j for g, c, nm, j in T}
    issues = []      # (구분, 내용, 근거) — 확인 필요
    checks = []      # 약관 대조 시트 줄

    def subs(pid):
        return [r for r in D['riders'] if r.get('parent') == pid]
    def grp_of(r):
        return re.sub(r'.*\[|\]$', '', r['n'])
    S131 = {grp_of(r): r for r in subs('케219')}
    S130 = {grp_of(r): r for r in subs('통123')}
    def cov(r, p, c):
        return covers(r['k'], c) and not covers(r.get('x') or [], c) and not covers(p.get('x') or [], c)
    def judge13(code, S, P):
        """130 · 131대 지급 판단 — (O/X/조건부, 보장군)"""
        hit = [k for k, r in S.items() if cov(r, P, code)]
        if hit:
            part = [x for r in S.values() for x in (r.get('x') or []) + (P.get('x') or []) if x.startswith(code + '.')]
            return ('조건부' if part else 'O'), ', '.join(hit) + ((' — 하위코드 %s 제외' % ', '.join(sorted(set(part)))) if part else '')
        partial = sorted({k for k, r in S.items() for t in r['k'] if norm_tok(t).startswith(code + '.')})
        if partial: return '조건부', ', '.join(partial) + ' — 일부 하위코드만'
        return 'X', ''

    # ── 1) 약관 목차 → 상품별 탑재 + 별표 대조 ──
    sc15 = [r[3].rstrip('종') for r in SC['detail']]
    tool_tables = {D['tables'][r['t'][0]]['name']: D['tables'][r['t'][0]]['text'] for r in subs('케219') + subs('통123')}
    rowsp, used_master = [], set()
    bp_ref = {}      # 상품표시명 → {표: (별표번호, 시작, 끝, 인쇄차이)}
    for disp, pkey, src, fn, pnote in PRODUCTS:
        if not os.path.exists(os.path.join(ROOT, fn)):
            issues.append(('약관 파일', '%s 약관 파일이 저장소에 없음 : %s' % (disp, fn), '')); continue
        P = pdf(fn)
        riders, bp, last = P.toc()
        refs = {}
        # 1-7종
        b17 = P.bpyo(r'^1-7종\s*수술분류표$')
        if b17:
            num, nm, s, e, off = b17
            got = pdf17(P, s, e, num)
            miss = sorted(set(T17) - set(got)); extra = sorted(set(got) - set(T17))
            diff = sorted(c for c in T17 if c in got and got[c][0] != T17[c])
            res = '일치' if not (miss or extra or diff) else '확인 필요'
            det = '수술코드 %d개 · 종 일치' % len(got) if res == '일치' else '빠짐 %s · 더 있음 %s · 종 다름 %s' % (miss, extra, diff)
            if miss:
                for c in miss:
                    # 약관 인쇄 오류 확인 : 앞 코드 다음 줄 글자
                    prev = [x for x in T17 if x < c][-1]
                    pg = got.get(prev, (0, s))[1]
                    snip = re.search(re.escape(prev) + r'\s*\n\s*\d\s*\n(?:.*\n){1,4}?\s*(\S{1,5})\s*\n\s*(\d)', P.raw(pg))
                    issues.append(('약관 인쇄', '%s 약관 1-7종 수술분류표 : 수술코드 %s 칸이 「%s」 로 인쇄됨(다른 약관 14권은 %s · %d종). 마스터는 고치지 않음'
                                   % (disp, c, snip.group(1) if snip else '?', c, T17[c]), 'PDF %d쪽(인쇄 %d쪽)' % (pg, pg - off)))
                det += ' — 빠진 코드는 약관 인쇄 오류(아래 「확인 필요」)'
            checks.append((disp, '1-7종 수술분류표', '별표%s' % num, '%d~%d' % (s, e), len(got), res, det))
            refs['1-7종'] = (num, s, e, off)
        b17x = P.bpyo(r'^1-7종\s*수술분류표\s*Ⅱ')
        if b17x:
            num, nm, s, e, off = b17x
            got = pdf17(P, s, e, num)
            extra = sorted(set(got) - set(T17))
            same = all(got[c][0] == T17[c] for c in T17 if c in got) and set(T17) <= set(got)
            checks.append((disp, '1-7종 수술분류표Ⅱ(내Mom같은 어린이 태아고급형 수술비(1-7종) 전용)', '별표%s' % num, '%d~%d' % (s, e), len(got),
                           '참고(별도 표)', '1-7종 630개와 같고 %d개 더 있음 : %s' % (len(extra), ', '.join('%s(%d종)' % (c, got[c][0]) for c in extra)) if same else '확인 필요'))
            refs['1-7종Ⅱ'] = (num, s, e, off, {c: got[c] for c in extra})
        # 1-5종Ⅱ
        b15 = P.bpyo(r'^1[-~]5종\s*수술분류표\s*Ⅱ')
        if b15:
            num, nm, s, e, off = b15
            rows15 = pdf15(P, s)
            js = [j for r in rows15 for j in r['jong']]
            res = '일치' if js == sc15 else '확인 필요'
            checks.append((disp, '1-5종 수술분류표Ⅱ', '별표%s' % num, '%d~%d' % (s, rows15[-1]['page'] if rows15 else s), len(js), res,
                           '수술 항목 %d줄 · 종 일치' % len(js) if res == '일치' else '종 순서가 다름 — 표를 직접 확인'))
            refs['1-5종Ⅱ'] = (num, s, rows15[-1]['page'] if rows15 else s, off, rows15)
        # 130 · 131대 세부 분류표
        has13 = [x for x in riders if kind_of(x[1]) in ('130대', '131대')]
        if has13:
            S, Pr = (S131, by['케219']) if kind_of(has13[0][1]) == '131대' else (S130, by['통123'])
            ok, det, tot = True, [], 0
            for sub in SC_SUB_ORDER(S):
                r = S[sub]
                tn = D['tables'][r['t'][0]]['name']
                b = P.bpyo('^' + re.sub(r'[,ㆍ·․]', '[,ㆍ·․]', tn.replace(' 분류표', '')) + r'\s*분류표$')
                if not b:
                    ok = False; det.append('%s 별표 못 찾음' % tn); continue
                num, nm, s, e, off = b
                A = toks(P.body(num, s, e))
                tt = tool_tables.get(tn, '')
                sp = sorted(set(re.findall(r'\b[A-Z] \d \d\b', tt)))
                if sp and (tn, 'sp') not in SEEN_ONLY:
                    SEEN_ONLY.add((tn, 'sp'))
                    issues.append(('영업지원도구 글', '「%s」 분류표 글(tool.html tables)에 질병코드가 %s 처럼 띄어 쓰여 있음 — 화면 검색에 안 걸릴 수 있음. 특약 마스터 k 목록은 정상(코드 빠짐 없음)' % (tn, ' · '.join("'%s'" % x for x in sp)), '표시 문제'))
                Bt = toks(re.sub(r'\b([A-Z]) (\d) (\d)\b', r'\1\2\3', tt))
                K = {norm_tok(x) for x in r['k']}; X = {norm_tok(x) for x in (r.get('x') or []) + (Pr.get('x') or [])}
                a_not_k = sorted(t for t in A if not covers(list(K), _expand(t)[0]) and t not in X
                                 and not re.match(r'A18|O22\.4|O87\.2', t))     # 결핵 원인코드 · 임신 치핵은 분류표 안 「제외」 문구
                k_not_a = sorted(t for t in K if not covers(list(A), _expand(t)[0]))
                tot += len(A)
                refs[sub] = (num, s, e, off)
                if a_not_k or k_not_a or (A - Bt - {'E10~E14'}):
                    ok = False; det.append('%s : 약관만 %s · 마스터만 %s' % (sub, a_not_k + sorted(A - Bt), k_not_a))
            checks.append((disp, '%s 세부 분류표 11개' % kind_of(has13[0][1]), ', '.join('별표%s' % refs[k][0] for k in SC_SUB_ORDER(S) if k in refs),
                           '', tot, '일치' if ok else '확인 필요', '세부 분류표 11개의 질병코드 = 특약 마스터(%s 세부보장 k/x)' % ('케219' if S is S131 else '통123') if ok else ' / '.join(det)))
        bp_ref[disp] = refs

        # 목차의 특약 → 마스터 짝
        mlist = [r for r in (D['riders'] if src == TOOL else EX['riders']) if r['p'] == pkey and not r.get('parent')]
        mmap = {}
        for r in mlist:
            mmap.setdefault(nname(r['n']), r)
        for no, name, printed in riders:
            kd = kind_of(name)
            if not kd or '수술' not in name: continue
            pg, body = P.rider_text(no, name, printed)
            m = mmap.get(nname(name))
            if m: used_master.add(m['id'])
            ref = sorted(set(re.findall(r'【별표[^】]*?(?:수술분류표Ⅱ?)\)?】', body)))
            ex = sorted(set('%s~%s' % (a, b if b[0].isalpha() else a[0] + b) for a, b in re.findall(r'\(([A-Z]\d{2})[∼~]([A-Z]?\d{2})\)', body)))
            rn = reduce_note(body)
            gb = '갱신형' if name.startswith('갱신형') else '비갱신형'
            note = []
            if '태아고급형' in name: note.append('내Mom같은 어린이 태아고급형 수술비(1-7종) — 1-7종 수술분류표Ⅱ(선천기형 수술코드 10개 더함)'
                                            + (' · 선천기형(Q00~Q99) 제외 없음(일반 1-7종[질병]과 다름)' if '[질병]' in name.replace(' ', '') else ''))
            if kd == '1-7종' and '[질병]' in name.replace(' ', '') and ex:
                note.append('습관성 유산·불임(N96~N98)은 보장개시 2년 후 발생분 보상')
            if m and src == EXTRA and kd == '1-7종' and '[질병]' in name.replace(' ', ''):
                mx = sorted(norm_tok(x) for x in (m.get('x') or []))
                if mx != sorted(norm_tok(x) for x in ex):
                    issues.append(('마스터(보강)', '%s %s(%s) : 약관 제외 KCD %s ↔ db_terms_extra.json x %s' % (disp, m['n'], m['id'], ', '.join(ex) or '없음', mx or '[] (비어 있음)'),
                                   'PDF %s쪽' % pg))
                    note.append('⚠ 마스터 제외코드와 다름(안내 시트 「확인 필요」)')
            if kd in ('130대', '131대'):
                subs_ = [v for k_, v in refs.items() if k_ in (S131 if kd == '131대' else S130)]
                ref = ['세부 분류표 11개 : ' + ' · '.join('별표%s' % v[0] for v in subs_)] if subs_ else []
            rowsp.append([kd, disp, fn, no, name, pg, gb, ', '.join(r.strip('【】') for r in ref), ', '.join(ex), rn,
                          m['id'] if m else '(마스터에 없음)', m['n'] if m else '', src if m else '', (m.get('sv') or '') if m else '', ' · '.join(note + ([pnote] if pnote and kd and pkey != '내Mom같은어린이' else []))])
            if not m:
                issues.append(('마스터 없음', '%s 약관 %s. %s — %s 에 같은 이름 특약 없음' % (disp, no, name, '영업지원도구' if src == TOOL else 'db_terms_extra.json'), 'PDF %s쪽' % pg))
        # 마스터에만 있는 특약
        names_pdf = {nname(x[1]) for x in riders}
        for r in mlist:
            if kind_of(r['n']) and '수술' in r['n'] and nname(r['n']) not in names_pdf:
                if (disp, r['id']) in SEEN_ONLY: continue
                SEEN_ONLY.add((disp, r['id']))
                if disp.startswith(('알파Plus', 'The좋은 알파', '통합간편(일반', '통합간편(355')): continue
                issues.append(('마스터에만', '%s : 마스터 %s %s 이(가) 2610 약관 목차에 없음' % (disp, r['id'], r['n']), fn))

    # 1-5종Ⅱ 를 수술 정의로 쓰는 다른 담보(통합치료비 등) — 영업지원도구
    t15 = {k for k, t in D['tables'].items() if re.search(r'1-5종\s*수술분류표Ⅱ', t.get('name', ''))}
    for r in D['riders']:
        if r.get('parent') or kind_of(r['n']): continue
        if set(r.get('t') or []) & t15:
            disp = {'케어프리': '케어프리 M-Basket', '통합간편': '통합간편(통합간편심사형)', '운전자': '운전자 상해 종합', '또또암': '또또암(일반심사형)'}.get(r['p'], r['p'])
            rowsp.append([KIND_ORDER[4], disp, '', '', r['n'], r.get('pg', ''), '갱신형' if r['n'].startswith('갱신형') else '비갱신형', '1-5종 수술분류표Ⅱ', '', '',
                          r['id'], r['n'], TOOL, r.get('sv') or '', '통합치료비의 「수술」 정의가 1-5종 수술분류표Ⅱ (쪽은 영업지원도구 pg)'])
    rowsp.append([KIND_ORDER[4], '안심되는 치매간병통합케어보험(일반 · 355Ⅱ간편)', '', '', '보장(통합치료) 안의 수술 정의 — 1-5종 수술분류표Ⅱ', '', '', '1-5종 수술분류표Ⅱ', '', '',
                  '', '', '', '', '스마트 제안서 제공 대상 아님(소유자 2026-10-02) · 분류표만 대조'])
    rowsp.sort(key=lambda z: (KIND_ORDER.index(z[0]), [p[0] for p in PRODUCTS].index(z[1]) if z[1] in [p[0] for p in PRODUCTS] else 99, int(z[5]) if str(z[5]).isdigit() else 0))

    # 1-5종Ⅱ 분류표만 있는 상품(치매간병 등)도 대조
    for fn in ['무배당 메리츠 안심되는 치매간병통합케어보험2610(일반심사형)약관.pdf', '무배당 메리츠 안심되는 치매간병통합케어보험2610(355Ⅱ간편심사형)약관.pdf']:
        if not os.path.exists(os.path.join(ROOT, fn)): continue
        P = pdf(fn); b15 = P.bpyo(r'^1[-~]5종\s*수술분류표\s*Ⅱ')
        if b15:
            num, nm, s, e, off = b15
            js = [j for r in pdf15(P, s) for j in r['jong']]
            checks.append(('치매간병(%s)' % ('일반' if '일반' in fn else '355Ⅱ간편'), '1-5종 수술분류표Ⅱ', '별표%s' % num, str(s), len(js),
                           '일치' if js == sc15 else '확인 필요', '수술 항목 %d줄 · 종 일치' % len(js) if js == sc15 else '종 순서가 다름'))

    # ── 2) 1-5종Ⅱ 시트 (기준 : 케어프리 M-Basket 별표) ──
    num15, s15, e15, off15, rows15 = bp_ref['케어프리 M-Basket']['1-5종Ⅱ']
    flat = split15(rows15)
    assert len(flat) == len(SC['detail']), '1-5종Ⅱ 줄 수 %d ≠ %d' % (len(flat), len(SC['detail']))
    rep_rows = []
    rows15x = []
    for i, (r, (txt, j, pg, g)) in enumerate(zip(SC['detail'], flat), 1):
        assert r[3].rstrip('종') == j
        it = R['1-5종'].get('5-' + r[1], {})
        ex_ = '\n'.join('%s (%s)' % (d['name'], d['kcd']) for d in it.get('diseases', []))
        memo = ' / '.join(d['note'] for d in it.get('diseases', []) if d.get('note'))
        sec = 'Ⅲ. 방사선 조사' if r[1].startswith('III') else ('Ⅱ. 악성신생물 치료 목적' if r[1].startswith('II') else 'Ⅰ. 일반 질병·상해 치료 목적')
        rows15x.append([i, sec, r[0], r[1].replace('II', 'Ⅱ').replace('ⅡI', 'Ⅲ'), clean(txt), '%s종' % j, r[4], ex_, memo,
                        '케어프리 M-Basket 2610 별표%s · %d쪽(PDF %d)' % (num15, pg - off15, pg)])
    notes15 = [
        ['주1)', '근골(筋骨) 수술에서 발정술(拔釘術) 등 내고정물 제거술은 제외 · 치(齒)·치은·치근·치조골의 처치, 임플란트 등 치과 처치 및 수술에 수반하는 것도 제외'],
        ['주2)', '1~87항 수술 중 내시경(Fiberscope)·카테터(Catheter) 등에 의한 경피적 수술은 88항 적용. 다만 복강경·흉강경 수술은 해당 부위(1~87항) 수술로 적용'],
        ['시각기', '약물 주입술은 제외'],
        ['88항', '검사·처치·약물주입요법은 포함하지 않음 · 수술개시일부터 60일 이내 2회 이상은 1회로 간주(이후 같은 기준으로 반복 지급)'],
        ['Ⅱ 주1)', '제자리암·경계성종양 수술은 「Ⅰ. 일반 질병 및 상해치료 목적의 수술」 적용'],
        ['Ⅱ 주2)', '카테터를 이용한 흡인·천자·약물주입요법은 포함하지 않음'],
        ['Ⅱ 주3)', '비고형암의 비관혈적 근치술은 관혈적 악성신생물 근치수술(5종)에 준해 인정 — 조혈모세포이식은 일련의 과정(추출·필터링·배양·제거·주입)을 1회로 · 약물 투여용 시술(중심정맥삽관 등)만 하면 5종 아님'],
        ['Ⅱ 주4)', 'Ⅱ 항목에서 복강경·흉강경 수술은 1. 또는 3. 으로 적용'],
        ['사용지침 1', '「수술」 = 의사·치과의사·한의사가 치료 목적으로 의료기관에서 1-5종 수술분류표Ⅱ 에 정한 행위(신의료기술평가위원회가 인정한 최신 수술기법 포함). 흡인·천자·적제 등의 조치 및 신경 BLOCK 제외'],
        ['사용지침 5', '분류표에 없는 첨단 수술 : 신의료기술평가위원회 인정 최신 수술기법은 동일 부위 수술로 봄(60일 내 2회 이상은 1회) · 내시경·경피적이면 88항(악성신생물은 Ⅱ-2) 우선'],
        ['사용지침 8', '지급 제외 : 흡인 · 천자 · 신경차단 · 미용성형 목적 · 피임 목적(불임술 후 가임 목적 포함) · 검사·진단 목적(생검·복강경검사 등) · 분류표에 없는 시술'],
        ['특약 본문', '수술비Ⅱ(1-5종) · 질병/상해 1-5종수술비(plus)는 특약 본문에 질병코드(KCD) 제외 조항이 없음 — 선천기형(Q)도 수술 술식이 표에 있으면 지급(1-7종[질병]과 다름). 담석증(K80) 36항 → 2종 · 유방의 비대(N62) 3항 → 1종처럼 표 안의 질병별 예외만 있음'],
    ]

    # ── 3) 1-7종 시트 ──
    num17, s17, e17, off17 = bp_ref['케어프리 M-Basket']['1-7종']
    got17 = pdf17(pdf(P131), s17, e17, num17)
    info = {}
    for r in d17:
        for part in r['code'].split(','):
            a, _, b = part.strip().partition('~')
            for gg, c, nm, j in T:
                if (c == a) if not b else (c[0] == a[0] and a <= c <= b): info[c] = r
    rows17 = []
    for gg, c, nm, j in T:
        it = R['1-7종'].get('7-%03d' % gg[0], {})
        ex_ = '\n'.join('%s (%s)' % (d['name'], d['kcd']) for d in it.get('diseases', []))
        pg = got17.get(c, (0, 0))[1]
        rows17.append([gg[0], gg[1], c, nm, '%d종' % j, info.get(c, {}).get('sys', ''), ex_,
                       '케어프리 M-Basket 2610 별표%s · %d쪽(PDF %d)' % (num17, pg - off17, pg) if pg else '별표%s' % num17])
    if '1-7종Ⅱ' in bp_ref.get('내Mom같은 어린이(태아전용)', {}):
        numx, sx, ex_, offx, extra17 = bp_ref['내Mom같은 어린이(태아전용)']['1-7종Ⅱ']
        Px = pdf(P17X)
        for c, (j, pg) in sorted(extra17.items()):
            nm, grp = '', ''
            for t in Px.doc[pg - 1].find_tables().tables:
                g = None
                for r in t.extract():
                    cc = [re.sub(r'\s+', ' ', x or '').strip() for x in r]
                    if len(cc) >= 4:
                        if cc[0]: g = cc[0]
                        if cc[2] == c: nm, grp = cc[1], g
            mg = re.match(r'(\d+)\.\s*(.*)', grp or '')
            rows17.append([int(mg.group(1)) if mg else '', (mg.group(2) if mg else grp) + ' [1-7종 수술분류표Ⅱ 전용 · 내Mom같은 어린이 태아고급형 수술비(1-7종)]', c, nm, '%d종' % j, '', '',
                           '내Mom같은 어린이 2610 별표%s(1-7종 수술분류표Ⅱ) · %d쪽(PDF %d) — 내Mom같은 어린이 태아고급형 수술비(1-7종)만' % (numx, pg - offx, pg)])
    n17 = len(T); n17x = len(rows17) - n17

    # ── 4) 131대 · 130대 질병 시트 ──
    allrep = {}
    for part in ('1-5종', '1-7종'):
        for it in R[part].values():
            for d in it['diseases']:
                allrep.setdefault(d['kcd'], d['name'])
    def grpname(g):
        g = re.sub(r'\s*\(.*?\)\s*', '', g).replace('수술비보장', '').replace('․', '·').strip()
        return g
    def row_codes(r):
        k = r['kcd']
        main = re.split(r'[\(\n]', k)[0]
        mtoks = [norm_tok(x) for x in re.findall(r'[A-Z]\d{2}(?:\.\d{1,2})?(?:\s*[∼~\-]\s*[A-Z]?\d{2}(?:\.\d{1,2})?)?', main)]
        exc = []
        for seg in re.findall(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)', k + ' ' + r['dis']):
            if '제외' in seg or '제외' in k:
                exc += re.findall(r'[A-Z]\d{2}(?:\.\d{1,2})?', seg) if '제외' in seg else []
        if '제외 -' in r['dis'] or '제외 ' in r['dis'][:3]:
            exc += re.findall(r'[A-Z]\d{2}(?:\.\d{1,2})?', r['dis'].split('제외', 1)[1])
        return mtoks, sorted(set(exc))
    def build13(S, Pr, label, disp, drop):
        rows = []
        refs = bp_ref[disp]
        P = pdf(dict((p[0], p[3]) for p in PRODUCTS)[disp])
        for r in d131:
            g = grpname(r['grp'])
            if label == '130대': g = g.replace('다빈도62대', '다빈도61대')
            mt, exc = row_codes(r)
            if drop and any(t in drop for t in mt): continue
            sub = [k for k in S if k.replace(',', '·') == g.replace(',', '·')]
            sub = sub[0] if sub else None
            ex = []
            for kcd, name in sorted(allrep.items()):
                if mt and covers(mt, kcd) and not covers(exc, kcd) and sub and cov(S[sub], Pr, kcd):
                    ex.append('%s (%s)' % (name, kcd))
            memo = []
            star = re.search(r'[†\*\+]', r['kcd'] + r['dis'])
            if star: memo.append('이중분류 코드(†원인 · *증상) — 분류번호를 함께 받을 수 있으면 대상(분류표 주)')
            if 'H35.0' in r['kcd'] or 'H35.0' in r['dis']: memo.append('H35.0 은 고혈압성(특정31대)과 그 밖 배경망막병증(다빈도)이 한 코드 — 상병명으로 판단')
            if 'H30' in r['kcd']: memo.append('H35.3(황반변성)은 이 줄에서 빼고 「황반변성」 줄로 보장')
            if any(t in ('M50', 'M51') for t in mt): memo.append('131대만 보장 — 130대(다빈도61대)에는 없음')
            if any(t.startswith('H') for t in mt) or '망막' in r['dis'] or '녹내장' in r['dis']:
                memo.append('눈질환 레이저 수술 포함(녹내장·당뇨병성 망막병증 등 · 60일 내 2회 이상은 1회 · 다래끼·선천성 제외)')
            ref = refs.get(sub)
            pg = ''
            if ref:
                num, s, e, off = ref[:4]
                first = (mt or re.findall(r'[A-Z]\d{2}(?:\.\d{1,2})?', r['kcd']) or [''])[0].split('~')[0]
                for n in range(s, e + 1):
                    if first and re.search(re.escape(first).replace('\\.', '\\.') + r'(?!\d)', P.text(n)):
                        pg = n; break
                pg = '%s 별표%s · %d쪽(PDF %d)' % (disp, num, (pg or s) - off, pg or s)
            rows.append([len(rows) + 1, g, clean(r['dis']), re.sub(r'\s*\n\s*', ' ', r['kcd']).strip(), ', '.join(exc), '\n'.join(ex[:3]),
                         '\n'.join(memo), pg])
        return rows
    rows131 = build13(S131, by['케219'], '131대', '케어프리 M-Basket', None)
    rows130 = build13(S130, by['통123'], '130대', '통합간편(통합간편심사형)', {'M50', 'M51'})

    # ── 5) 한눈에 비교 ──
    k5, k7 = {}, {}
    for it, v in R['1-5종'].items():
        for d in v['diseases']: k5.setdefault(d['kcd'], []).append((it, d))
    for it, v in R['1-7종'].items():
        for d in v['diseases']: k7.setdefault(d['kcd'], []).append((it, d))
    det15 = {('5-' + r[1]): r for r in SC['detail']}
    grp17 = {}
    for gg, c, nm, j in T: grp17.setdefault('7-%03d' % gg[0], [gg[1], []])[1].append(j)
    def judge7(c):
        a, n = c[0], int(c[1:3])
        if a in 'ST': return 'O', '상해 — 1-7종[상해] 특약'
        if a == 'Q': return 'X', '1-7종[질병] 선천기형(Q00~Q99) 제외 — 내Mom같은 어린이 태아고급형 수술비(1-7종)[질병]은 선천기형 제외 없음(1-7종 수술분류표Ⅱ 수술이면 지급)'
        if a == 'F' and n >= 4: return 'X', '정신 및 행동장애(F04~F99) 제외'
        if a == 'K' and n <= 8: return 'X', '치과질환(K00~K08) 제외'
        if a == 'P': return 'X', '출생전후기 병태(P00~P96) 제외'
        if a == 'N' and 96 <= n <= 98: return '조건부', '보장개시 2년 지난 뒤 발생한 습관성 유산·불임(N96~N98)만'
        return 'O', ''
    def jr(js):
        js = sorted(set(js)); return '%d종' % js[0] if len(js) == 1 else '%d~%d종' % (js[0], js[-1])
    rowsx = []
    for kcd in sorted(set(k5) & set(k7)):
        name = k5[kcd][0][1]['name']
        items5 = sorted({it for it, d in k5[kcd]}, key=lambda s: list(R['1-5종']).index(s))
        s5 = '\n'.join('%s %s' % (it[2:].replace('II', 'Ⅱ').replace('ⅡI', 'Ⅲ'), det15[it][2]) for it in items5 if it in det15)
        j5 = jr([int(det15[it][3][0]) for it in items5 if it in det15])
        p5 = 'O' + (' (상해 1-5종 · 수술비Ⅱ 상해)' if kcd[0] in 'ST' else '')
        items7 = sorted({it for it, d in k7[kcd]})
        s7 = '\n'.join('%s %s' % (int(it[2:]), grp17[it][0]) for it in items7 if it in grp17)
        j7 = jr([j for it in items7 if it in grp17 for j in grp17[it][1]])
        p7, n7 = judge7(kcd)
        a1, g1 = judge13(kcd, S131, by['케219'])
        a0, g0 = judge13(kcd, S130, by['통123'])
        note = [n7] if n7 else []
        if a1 == 'O' and a0 == 'X': note.append('131대만(추간판장애 M50·M51)')
        note += [d['note'] for it, d in k5[kcd] + k7[kcd] if d.get('note')]
        rowsx.append([name, kcd, s5, j5, p5, s7, j7, p7, a0, g0, a1, g1, ' / '.join(dict.fromkeys(note))])

    # ── 6) 안내 ──
    wb = Workbook(); wb.remove(wb.active)
    sheet(wb, '한눈에 비교',
          ['대표 질병', 'KCD', '1-5종Ⅱ 수술 항목', '1-5종Ⅱ 종', '1-5종Ⅱ 지급', '1-7종 수술구분', '1-7종 종', '1-7종 지급',
           '130대 지급', '130대 보장군', '131대 지급', '131대 보장군', '비고'],
          rowsx, [30, 9, 34, 9, 12, 34, 9, 10, 9, 22, 9, 22, 40],
          '대표 질병(docs/surgery_rep_diseases.json 중 1-5종 · 1-7종 예시에 모두 나오는 %d개)마다 4종 수술비가 나오는지 한 줄로 비교. '
          'O = 지급 대상 · X = 약관상 지급 안 함 · 조건부 = 일부 하위코드나 조건만. 1-5종Ⅱ · 1-7종은 「수술」로 지급(질병이 같아도 실제 수술 항목 · 수술코드로 판단), '
          '130대 · 131대는 「질병코드」로 지급(지정 질병으로 수술해야 함 · 암(C) 미보장). 130 · 131대는 계약일부터 1년 안 50%%. 종은 그 질병에 흔한 수술 항목 기준 — 실제 종은 받은 수술로 정해짐' % len(rowsx))
    sheet(wb, '130대 질병', ['순번', '세부보장(보장군)', '대상질병(약관 표기)', 'KCD 범위', '제외 코드', '대표 질병 예시(KCD)', '수술 조건 · 메모', '근거(약관 별표 · 쪽)'],
          rows130, [6, 18, 42, 22, 18, 34, 40, 34],
          '130대질병수술비 — 통합간편 · The가벼운 간편355 · 간편31(갱신형). 「130대질병」으로 진단확정되고 그 치료를 직접 목적으로 수술하면 수술 1회당 지급(세부보장 11개 · 계약일부터 1년 안 50%%). '
          '같은 날 같은 질병 수술은 1회 · 흡인·천자·신경차단·미용·피임·검사 목적 수술 제외. 131대와 차이는 다빈도61대에 추간판장애(M50 · M51)가 없는 것뿐(약관 별표 대조). 제외 코드 N39.3 · N39.4 · K23.0 · M74 · M78 은 어느 세부보장에도 없음. '
          '대표 질병 예시는 검수된 대표 질병 목록 중 이 줄의 KCD 안에 드는 것(최대 3개).')
    sheet(wb, '131대 질병', ['순번', '세부보장(보장군)', '대상질병(약관 표기)', 'KCD 범위', '제외 코드', '대표 질병 예시(KCD)', '수술 조건 · 메모', '근거(약관 별표 · 쪽)'],
          rows131, [6, 18, 42, 22, 18, 34, 40, 34],
          '131대질병수술비 — 케어프리 M-Basket(비갱신 · 갱신형) · The좋은 케어프리 · The건강한 5.10.5 · The건강한 내Mom대로 · 내Mom대로 · 내Mom같은 어린이 · The좋은 내Mom대로. '
          '「131대질병」으로 진단확정되고 그 치료를 직접 목적으로 수술하면 수술 1회당 지급(세부보장 11개 · 계약일부터 1년 안 50%%). 같은 날 같은 질병 수술은 1회 · 흡인·천자·신경차단·미용·피임·검사 목적 수술 제외 · '
          '녹내장·당뇨병성 망막병증 등 눈질환 레이저 수술 포함. 질병코드는 제9차 KCD(통계청 고시 제2025-299호, 2026.1.1 시행) 기준.')
    sheet(wb, '1-5종Ⅱ 수술행위', ['순번', '구분', '계통', '번호', '수술행위(별표 원문)', '종', '약관 조건 요약', '대표 질병 예시(KCD)', '예시 메모', '근거(약관 별표 · 쪽)'],
          rows15x, [6, 16, 12, 7, 52, 6, 34, 34, 26, 30],
          '1-5종 수술분류표Ⅱ — 수술 술식 기준 · 급여/비급여 무관 · 질병·상해 공통(수술비Ⅱ(1-5종) · 질병/상해 1-5종수술비(plus) · 통합치료비 수술). 종이 높을수록 지급액이 큼. '
          '수술행위 칸은 약관 표 글 그대로(칸 안 줄바꿈만 이음). 88항 · 11 · 13 · Ⅱ-1 은 하위 항목마다 한 줄. 아래 각주는 「1-5종 각주·지침」 시트. 같은 표가 상품마다 별표 번호만 다르게 실림(「약관 대조」 시트)')
    sheet(wb, '1-5종 각주·지침', ['구분', '약관 내용'], notes15, [14, 120])
    sheet(wb, '1-7종 수술행위', ['구분번호', '수술구분', '수술코드(ADRG)', '수술행위(약관 수술명)', '종', '계통(참고)', '대표 질병 예시(KCD · 수술구분별)', '근거(약관 별표 · 쪽)'],
          rows17, [8, 30, 11, 46, 6, 14, 40, 34],
          '1-7종 수술분류표 — 건강보험 급여 수술(KDRG ADRG 수술코드) 기준 · 비급여 제외 · ADRG 2·3번째 자리 60~99 · Error DRG(961·962·963·990·999) · 960 DRG 제외. '
          '일반 수술비(1-7종)[질병] 특약은 정신(F04~F99) · 치과(K00~K08) · 선천기형(Q00~Q99) · 출생전후기(P00~P96) 질병의 수술을 보상하지 않음(습관성 유산·불임 N96~N98 은 보장개시 2년 후 발생분만). '
          '맨 아래 %d줄은 「내Mom같은 어린이 태아고급형 수술비(1-7종)」가 쓰는 「1-7종 수술분류표Ⅱ」에만 있는 수술코드 — 이 특약[질병]은 선천기형(Q00~Q99)을 제외하지 않음(정신 · 치과 · 출생전후기 · N96~N98 제외는 같음 · 약관 2-148 · 2-149 제5조).' % n17x)
    sheet(wb, '상품별 탑재', ['수술비 종류', '상품', '약관 파일', '약관 번호', '특약명(약관 목차)', 'PDF 쪽', '갱신형 여부', '쓰는 분류표(특약 본문)', 'KCD 제외(특약 본문)',
                           '감액(약관 지급표에서 읽음)', '마스터 id', '마스터 특약명', '마스터 출처', '간편심사 감액 메모(sv)', '비고'],
          rowsp, [12, 22, 30, 8, 40, 7, 9, 26, 26, 22, 10, 32, 22, 22, 36],
          '2610 약관 목차에서 이 4종 수술비 특약을 찾고 본문을 읽어 채움. 감액 = 특약 지급표의 「계약일부터 ○ 경과시점 전일 이전 ○%」 · sv = 영업지원도구 간편심사 감액 메모. '
          '마스터 id 는 영업지원도구(tool.html) 또는 스마트 제안서 보강(db_terms_extra.json)의 같은 이름 특약(가입유형 표시 「(○○가입)」 은 빼고 비교). 맨 아래는 1-5종Ⅱ를 수술 정의로 쓰는 통합치료비(참고)', warn_col=14)
    sheet(wb, '약관 대조', ['상품', '분류표', '별표', 'PDF 쪽', '항목 수', '결과', '내용'],
          checks, [26, 22, 34, 10, 8, 10, 70],
          '2610 약관 PDF 의 별표를 직접 읽어(두 단 · 다음 쪽까지) 영업지원도구 마스터와 대조한 결과(%s 생성). 1-7종 = 수술코드별 종 · 1-5종Ⅱ = 항목별 종 · 130/131대 = 세부 분류표 11개의 질병코드' % BUILD_DATE,
          warn_col=5)

    # 앞 판(2610 엑셀)과 비교 — 상품별 탑재
    chg = []
    if os.path.exists(OLD):
        ow = load_workbook(OLD, read_only=True)
        old = [r for r in ow['상품별 탑재'].iter_rows(min_row=2, values_only=True) if r and r[0]]
        okey = {(r[0].replace('1-5종Ⅱ', '1-5종Ⅱ'), re.sub(r'\s+', '', r[1]), nname(r[2])): r[3] for r in old}
        new = {}
        p2key = {p[0]: p[1] for p in PRODUCTS}
        for r in rowsp:
            if r[0] not in KIND_ORDER[:4] or r[10].startswith('('): continue
            new[(r[0], re.sub(r'\s+', '', p2key.get(r[1], r[1])), nname(r[11]))] = r[10]
        add = sorted(set(new) - set(okey)); rem = sorted(set(okey) - set(new))
        idc = sorted(k for k in set(new) & set(okey) if new[k] != okey[k])
        chg.append(('상품별 탑재 — 새로 잡힌 특약 %d' % len(add), '; '.join('%s %s %s(%s)' % (k[0], k[1], k[2], new[k]) for k in add)))
        chg.append(('상품별 탑재 — 빠진 특약 %d' % len(rem), '; '.join('%s %s %s(%s)' % (k[0], k[1], k[2], okey[k]) for k in rem) or '없음'))
        chg.append(('상품별 탑재 — id 만 바뀜 %d' % len(idc), '; '.join('%s %s : %s → %s' % (k[1], k[2], okey[k], new[k]) for k in idc) or '없음'))
        o17 = sum(1 for r in ow['1-7종'].iter_rows(min_row=3, values_only=True) if r and r[2])
        o15 = sum(1 for r in ow['1-5종II'].iter_rows(min_row=3, values_only=True) if r and r[2])
        o131 = sum(1 for r in ow['131대 대상질병'].iter_rows(min_row=3, values_only=True) if r and r[1])
        chg.append(('분류표 내용', '1-7종 수술코드 %d → %d(+ 1-7종Ⅱ 전용 %d) · 1-5종Ⅱ %d → %d줄 · 131대 대상질병 %d → %d줄 — 코드 · 종 · 질병코드 바뀐 것 없음(2610 약관 대조 「약관 대조」 시트)'
                    % (o17, n17, n17x, o15, len(rows15x), o131, len(rows131))))

    ws = wb.create_sheet('안내', 0)
    ws.column_dimensions['A'].width = 26; ws.column_dimensions['B'].width = 14; ws.column_dimensions['C'].width = 110
    L = [('수술비 4종 — 130대 · 131대질병수술비 · 1-5종 수술분류표Ⅱ · 1-7종 수술분류표 : 보장 KCD · 수술행위 정리 (2611판)', None, None),
         ('목적', '', '영업 현장에서 「이 질병 · 이 수술이면 어느 수술비가 나오나」를 한 파일에서 찾도록 정리. 130대 · 131대는 질병코드(KCD)로, 1-5종Ⅱ는 수술 술식으로, 1-7종은 급여 수술코드(ADRG)로 지급한다.'),
         ('기준 약관', '2610', '2026-10-31 개정 · 판매개시 2026.10.31 (저장소 루트의 상품별 최신 판). 질병코드는 제9차 KCD(통계청 고시 제2025-299호, 2026.1.1 시행)'),
         ('만든 날', BUILD_DATE, '생성 : python3 scripts/build_surgery_xlsx_2611.py — 앞 판 dist/surgery_benefit_kcd_2610.xlsx 는 그대로 둠'),
         (None, None, None), ('기준 약관 파일', None, None)]
    for disp, pkey, src, fn, pnote in PRODUCTS:
        kinds = sorted({r[0] for r in rowsp if r[1] == disp and r[0] in KIND_ORDER[:4]}, key=KIND_ORDER.index)
        L.append((disp, ' · '.join(kinds) or '-', fn + (' — ' + pnote if pnote else '')))
    L += [(None, None, None), ('시트', '줄 수', '내용')]
    shs = [('한눈에 비교', len(rowsx), '대표 질병별 130대 · 131대 · 1-5종Ⅱ · 1-7종 지급(O/X/조건부) · 종 — 먼저 여기서 찾고, 자세한 근거는 아래 시트'),
           ('130대 질병', len(rows130), '130대질병수술비 대상질병 줄(약관 분류표) · KCD 범위 · 제외 코드 · 대표 질병 · 근거 쪽'),
           ('131대 질병', len(rows131), '131대질병수술비 대상질병 줄(약관 분류표) · KCD 범위 · 제외 코드 · 대표 질병 · 근거 쪽'),
           ('1-5종Ⅱ 수술행위', len(rows15x), '1-5종 수술분류표Ⅱ 항목(별표 원문) · 종 · 대표 질병 · 근거 쪽'),
           ('1-5종 각주·지침', len(notes15), '1-5종Ⅱ 각주 · 사용 지침 · 지급 제외 수술'),
           ('1-7종 수술행위', len(rows17), '1-7종 수술코드(ADRG) %d개 + 1-7종 수술분류표Ⅱ 전용 %d개 · 종 · 대표 질병(수술구분별) · 근거 쪽' % (n17, n17x)),
           ('상품별 탑재', len(rowsp), '상품마다 이 4종 수술비 특약 — 약관 번호 · 쪽 · 갱신형 · 분류표 · KCD 제외 · 감액 · 마스터 id'),
           ('약관 대조', len(checks), '상품마다 2610 약관 별표를 직접 읽어 마스터와 대조한 결과')]
    L += [(a, b, c) for a, b, c in shs]
    L += [(None, None, None), ('읽는 법', None, None),
          ('지급 판단', 'O / X / 조건부', 'O = 약관상 지급 대상 · X = 지급하지 않음(제외 질병 · 대상 아님) · 조건부 = 하위코드 일부만 대상이거나 기간 조건이 있음. 실제 지급은 진단서 상병코드 · 받은 수술 · 수술코드와 약관 조건으로 판단'),
          ('종', '', '1-5종Ⅱ는 수술 항목의 종, 1-7종은 수술코드의 종(한눈에 비교는 그 질병에 흔한 수술구분의 종 범위). 같은 질병이라도 받은 수술이 다르면 종이 다르다'),
          ('대표 질병', '참고용', '약관에 적힌 목록이 아니라 「이 수술을 흔히 받는 질병」 예시(docs/surgery_rep_diseases.json — 의학 자료 · KDRG 분류 확인 · WHO ICD-10 대조 검수본). 이 판에서 새 질병코드는 만들지 않았고, 130 · 131대 시트에는 그 줄 KCD 범위 안에 드는 예시만 붙였다'),
          ('근거 쪽', '', '「○쪽(PDF n)」 = 약관에 인쇄된 쪽 번호와 PDF 파일의 쪽 번호. 같은 분류표는 상품마다 별표 번호만 다름(「약관 대조」 시트)'),
          ('주의', '', '이 파일은 영업 참고 자료다. 보험금 지급 여부의 최종 판단은 약관 원문과 회사 심사 기준을 따른다. 고객 설명 · 사외 배포 전에는 해당 상품 약관 원문을 확인한다'),
          (None, None, None), ('2610 약관 대조 결과(%s)' % BUILD_DATE, None, None)]
    ok = sum(1 for c in checks if c[5] == '일치'); bad = [c for c in checks if c[5] == '확인 필요']
    L.append(('대조', '%d건 일치' % ok, '1-7종(수술코드 630개 · 종) · 1-5종Ⅱ(99줄 · 종) · 130/131대(세부 분류표 11개 질병코드)를 상품별 2610 약관 PDF 와 마스터에서 따로 읽어 비교. 확인 필요 %d건' % len(bad)))
    L.append(('130대 vs 131대', '차이 2코드', '다빈도62대(131대) − 다빈도61대(130대) = 추간판장애 M50 · M51 뿐. 나머지 세부 분류표 10개는 질병코드가 같음'))
    new10 = [r for r in D['riders'] if r.get('new') == '2610' and kind_of(r['n']) and not r.get('parent')]
    L.append(('2610 신설 특약', '%d개' % len(new10), '영업지원도구에 2610 신설로 표시된 것 : ' + ' · '.join('%s %s(%s)' % (r['p'], r['n'], r['id']) for r in new10)
              + '. 보강 마스터 상품(The좋은 · The건강한 · 내Mom 계열 · The가벼운 · 간편31)은 판 표시가 없어 아래 「앞 판과 달라진 것」에 앞 판 엑셀에 없던 특약으로 적음'))
    L.append(('분류표 문구', '', '케어프리 계열 131대의 관절염·생식기질환 분류표에 「다음의 상병 이외의 출생전후기 질병(P00~P96)은 포함되지 않습니다」 문장이 있음 — 영업지원도구에 저장된 분류표 글(이전 판에서 옮김)에는 없음(2610 에서 붙은 것으로 보임). 통합간편 계열 130대 약관의 뇌혈관 · 관절염 · 백내장 분류표에는 이 문장이 없음. 질병코드 목록은 모두 같음'))
    L += [(None, None, None), ('앞 판(2610 엑셀)과 달라진 것', None, None)]
    L += [(a, '', b) for a, b in chg]
    L.append(('시트 구성', '', '「한눈에 비교」 새로 만듦 · 130대 / 131대 질병 시트를 따로 나누고 제외 코드 · 대표 질병 · 근거 쪽을 붙임 · 1-5종Ⅱ 수술행위를 약관 표 글 그대로 · 1-7종에 근거 쪽과 1-7종Ⅱ 전용 코드 · 상품별 탑재에 약관 번호 · 쪽 · 갱신형 · KCD 제외 · 감액 · 「약관 대조」 시트'))
    L += [(None, None, None), ('확인 필요(데이터 — 이 파일에서는 고치지 않음)', None, None)]
    for a, b, c in issues:
        L.append((a, c, b))
    if not issues: L.append(('', '', '없음'))
    for i, (a, b, c) in enumerate(L, 1):
        for j, v in enumerate((a, b, c), 1):
            if v is None: continue
            cell = ws.cell(i, j, v); cell.font = Font(name=FONT, size=10); cell.alignment = Alignment(wrap_text=True, vertical='top')
        if a and b is None and c is None:
            ws.cell(i, 1).font = Font(name=FONT, size=14 if i == 1 else 11, bold=True, color='0B7C6F')
        if a == '시트' and b == '줄 수':
            for j in range(1, 4):
                ws.cell(i, j).font = Font(name=FONT, bold=True, color='FFFFFF'); ws.cell(i, j).fill = HEAD
        if c and isinstance(c, str):
            ws.row_dimensions[i].height = max(15, 14 * (1 + len(c) // 95))
    ws.merge_cells('A1:C1'); ws.row_dimensions[1].height = 24
    print_fit(ws)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print(OUT)
    for w in wb.worksheets:
        print('  %-14s %d줄' % (w.title, w.max_row))
    for c in checks:
        if c[5] != '일치': print('  [대조]', c)
    for x in issues: print('  [확인 필요]', x)


SEEN_ONLY = set()
def SC_SUB_ORDER(S):
    return list(S.keys())


if __name__ == '__main__':
    main()
