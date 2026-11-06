# -*- coding: utf-8 -*-
"""특약 마스터 이름의 띄어쓰기 점검 — 약관 PDF 의 줄바꿈 자리에 끼어든 띄어쓰기(「주요치 료비」 「연 간1회한」)를 찾는다

이름 속 띄어쓴 곳마다 그 상품 약관 원문(같은 줄 안)을 본다.
  · 약관이 같은 줄에서 띄어 씀            → 약관 표기 그대로(오류 아님)
  · 약관(또는 정보계 이름)이 붙여 씀       → 오류(줄바꿈이 끼어듦) — 띄어쓰기를 빼는 것을 제안
  · 둘 다 안 보임                          → 판단 보류
비교 · 계산은 띄어쓰기를 지우고 하므로 매핑 · 지급 판정에는 영향이 없다. 화면 · 설계도에 보이는 이름의 문제다.

사용 : python3 spacing.py <작업폴더> <결과 엑셀>   (작업폴더에 terms_txt/ — toc.py 가 만든 약관 글자 · rows.json 은 있으면 참고)
"""
import sys, os, re, json, collections
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from match import M

WORK, OUT = sys.argv[1], sys.argv[2]
TXT = os.path.join(WORK, 'terms_txt')
IDX = dict(l.split(' ', 1) for l in open(os.path.join(TXT, 'index.txt'), encoding='utf-8').read().strip().split('\n'))
FILEP = {'통합간편': '(통합간편심사형)', '케어프리': '케어프리보험 M-Basket', '운전자': '운전자 상해', '치아': '치아보험', '또또암': '(일반심사형)약관', '또또암간편': '(맞춤간편심사형)',
         '간편31': '간편31', '내Mom대로': '무배당 내Mom대로', '내Mom같은어린이': '내Mom같은', 'The건강한내Mom대로5.10.5': 'The건강한 내Mom대로', 'The건강한5.10.5': 'The건강한 5.10.5',
         'The좋은내Mom대로': 'The좋은 내Mom대로', 'The가벼운간편355': 'The가벼운', 'The좋은케어프리': 'The좋은 케어프리'}
def pfile(p):
    k = FILEP[p]
    hits = [i for i, f in IDX.items() if k in f and (p != '또또암' or '또 걸려도' in f) and (p != '케어프리' or 'The좋은' not in f)]
    return hits[0] if hits else None
TEXT = {}
def text(p):
    i = pfile(p)
    if i not in TEXT:
        t = open(os.path.join(TXT, '%s.txt' % i), encoding='utf-8', errors='ignore').read()
        TEXT[i] = re.sub(r'[ \t ]+', ' ', t)
    return TEXT[i]
CORP = ''
if os.path.exists(os.path.join(WORK, 'rows.json')):
    CORP = '\n'.join(sorted({n for _, _, n in json.load(open(os.path.join(WORK, 'rows.json'), encoding='utf-8'))}))

DL = r'[\s\[\]\(\),·/]'
def frag(s, i, d):
    j = i
    if d < 0:
        while j > 0 and not re.match(DL, s[j - 1]): j -= 1
        return s[j:i]
    while j < len(s) and not re.match(DL, s[j]): j += 1
    return s[i:j]

BAD, KEEP, HOLD = [], collections.Counter(), collections.Counter()
for r in M:
    n = r['n']; t = text(r['p']); fix = []
    for m in re.finditer(r' +', n):
        i, j = m.start(), m.end(); L = frag(n, i, -1); R = frag(n, j, 1)
        if not L or not R: continue
        sp, jo = L + ' ' + R, L + R
        if sp in t: KEEP[(r['p'], sp)] += 1; continue
        if jo in t or (CORP and jo in CORP and sp not in CORP):
            fix.append((i, j, sp, jo, '약관' if jo in t else '정보계'))
        else: HOLD[(r['p'], sp)] += 1
    if fix:
        s = n
        for i, j, *_ in sorted(fix, reverse=True): s = s[:i] + s[j:]
        BAD.append([r['p'], r['id'], '영업지원도구 감수본(tool.html → db.json)' if r['src'] == 'db' else '약관 파싱 보강 마스터(db_terms_extra.json)',
                    n, s, ' · '.join('「%s」→「%s」' % (a, b) for _, _, a, b, _ in fix), ' · '.join(sorted({e for *_, e in fix}))])

wb = openpyxl.Workbook(); F = '맑은 고딕'
def sheet(ws, head, data, widths):
    ws.append(head)
    for c in ws[1]: c.font = Font(name=F, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='3A3A3A'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for row in data: ws.append(row)
    for row in ws.iter_rows(min_row=2):
        for c in row: c.font = Font(name=F, size=10); c.alignment = Alignment(wrap_text=True, vertical='top')
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions
ws = wb.active; ws.title = '고칠 이름'
sheet(ws, ['상품', '특약 ID', '어디 이름', '지금 이름', '고친 이름(제안)', '잘못 끼어든 띄어쓰기', '근거(붙여 쓴 표기를 찾은 곳)'], BAD, [16, 11, 26, 60, 60, 40, 12])
sheet(wb.create_sheet('약관 표기 그대로'), ['상품', '띄어쓴 곳', '건수'], [[p, sp, c] for (p, sp), c in KEEP.most_common()], [16, 50, 8])
sheet(wb.create_sheet('판단 보류'), ['상품', '띄어쓴 곳', '건수'], [[p, sp, c] for (p, sp), c in HOLD.most_common()], [16, 50, 8])
wb.save(OUT)
print('고칠 이름', len(BAD), '(띄어쓰기', sum(row[5].count('→') for row in BAD), '곳) · 약관 표기 그대로', sum(KEEP.values()), '· 판단 보류', sum(HOLD.values()))
print(collections.Counter((row[0], row[2][:6]) for row in BAD).most_common())
