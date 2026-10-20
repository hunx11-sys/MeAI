# -*- coding: utf-8 -*-
"""
2026-10-19 약관 개정 — 자동차사고 변호사선임비용(Ⅲ) 에 「변호사선임 현물급부」 선택 추가 → 영업지원도구(tool.html) 반영

대상 : 케392(케어프리 M-Basket) · 운133(운전자 상해 종합보험). 통합간편에는 이 특약이 없다(소유자 확인).
근거 : 10-19 개정 약관(The건강한 5.10.5 2607, 1007~1011쪽)의 같은 이름 특약 — 이름이 같으면 약관도 같다(CLAUDE.md).
       The좋은 케어프리 M-Basket 2607 약관(1589쪽~)도 글자까지 같다.
       케어프리 M-Basket 4.0 · 운전자 2608 3.0(둘 다 2026.10.19 판매) 약관도 받아 옛 판과 대조했다 — 바뀐 글은 이 특약뿐이고,
       그 뒤 특약들의 쪽이 밀렸다(운전자 화재·배상책임 27개 +1~2쪽 · 케어프리 가전제품 고장수리비용 3개 +2쪽). 별표 쪽은 그대로.

바뀌는 것 (개정 전 → 개정 후)
  · 이름 : 자동차사고 변호사선임비용(Ⅲ) → 자동차사고 변호사선임비용(Ⅲ)(변호사선임 현물급부 선택가능)
  · 제3조(변호사선임 현물급부의 정의) · 제4조(…제공, 지급절차 및 안내 등) · 제5조(…제공에 관한 세부규정) 신설
  · 그 뒤 조 번호 3→6, 4→7, 5→8, 6→9, 7→10 (제2조 ⑩ 의 「제3조(보험금을 지급하지 않는 사유)」 인용도 제6조로)
  · 비례분담 「보장대상 변호사선임비용」 정의에 「또는 현물급부 제공금액을 합산한 금액」 추가 · 현물급부 분담 예시 추가
각 상품 본문의 줄바꿈 · 준용규정(운전자는 보통약관 조문 제외 문구)은 그대로 둔다.

실행 : python3 scripts/rev_lawyer3_2610.py [--write]
"""
import base64, io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tooldata import PAT, inflate, deflate, ROOT

TOOL = os.path.join(ROOT, 'tool.html')
IDS = ['케392', '운133']
NEW_NAME = '자동차사고 변호사선임비용(Ⅲ)(변호사선임 현물급부 선택가능)'

ART345 = '''제3조(변호사선임 현물급부의 정의)
① 이 특별약관에서「변호사선임 현물급부」라 함은 피보
험자에게 이 특별약관의 보험기간 중 제1조(보험금의 지
급사유)에서 정한 지급사유가 발생하여 피보험자가 회사
에 변호사선임 현물급부 제공을 요청하는 경우 회사가 제
공하는 현물급부로서, 해당 사고의 변호를 위한 변호사선
임을 제휴회사가 직접 피보험자에게 제공하는 것을 말합
니다.
② 제1항의 제휴회사라 함은 회사와「변호사선임 현물급
부」업무협약을 체결하고「변호사선임 현물급부」의 제공
의무를 지는 자를 말합니다.
③ 이 특별약관에서 피보험자가 회사에 변호사선임 현물
급부 제공을 요청하는 경우「변호사선임 현물급부」또는
제5조(변호사선임 현물급부 지급에 관한 세부규정) 제2항
및 제3항에 따라 지급하는 금액을 보험금이라 합니다.
제4조(변호사선임 현물급부의 제공, 지급절차 및 안내
등)
①「변호사선임 현물급부」는 제휴회사에서 직접 피보험
자에게 제공되며, 그 법률서비스의 제공 품질 등에 대한
책임은 제휴회사에 있습니다. 또한, 이 특별약관에서 정
하지 않은「변호사선임 현물급부」관련 세부사항은 회사
와 제휴회사간 별도로 정한 운영약관을 따르며, 그 운영
약관은 회사와 제휴회사간 정한 방법에 따라「변호사선임
현물급부」를 요청한 피보험자에게 제공됩니다.
② 제휴회사는 피보험자에게 보험기간 중에 제1조(보험금
의 지급사유)에서 정한 지급사유가 발생한 경우「변호사
선임 현물급부」를 피보험자에게 제공합니다.
③「변호사선임 현물급부」에서 제공하는 내용, 제공기준
및 이용절차 등을 회사의 인터넷 홈페이지 등을 통하여
공시합니다.
④ 제휴회사는 제2항의「변호사선임 현물급부」제공 시,
제공 서비스 내용 및 이용절차를 피보험자에게 알려드립
니다.
⑤ 피보험자는 이미 제공된「변호사선임 현물급부」의 전
부 또는 일부에 대하여 회사에 반환 청구할 수 없습니다.
제5조(변호사선임 현물급부 제공에 관한 세부규정)
①「변호사선임 현물급부」는 제1조(보험금의 지급사유)
가 발생한 시점에 현물급부 제공을 요청한 피보험자가 이
특별약관의 변호사선임비용에 대하여 보험금을 지급할 유
효한 계약(각종 공제계약을 포함합니다)이 당사(보험업감
독규정 제1-2조(정의)에서 정한 장기손해보험에 한함)와
체결한 계약 외에는 없는 경우에 한하여 제공됩니다.
② 제1항에 따라「변호사선임 현물급부」가 제공된 경우,
회사의 인터넷 홈페이지에 공시된 금액(이하「현물급부
제공금액」이라 합니다)을 지급된 보험금으로 봅니다.
③ 제1항에도 불구하고 회사 또는 제휴회사의 원인으로
「변호사선임 현물급부」의 제공이 불가할 수 있으며 이
경우, 회사는 이 특별약관에서 정한 바에 따라 변호사선
임비용을 보험금으로 지급합니다.
④ 피보험자가 회사에 변호사선임비용에 대하여 보험금을
지급할 다수 계약(각종 공제계약을 포함합니다)을 가입하
여 그 중 두 개 이상이 유효한 경우에도「변호사선임 현
물급부」는 1사고당 1회에 한하여 제공합니다.
⑤ 제1항에 따라 회사에「변호사선임 현물급부」를 요청
한 동일한 사유로 피보험자가 임의로 당사와 제휴되지 않
은 다른 법무법인 등과 변호사선임 계약을 체결한 경우에
는 제3조(변호사선임 현물급부의 정의)에 해당하지 않습
니다.
⑥ 제1항에도 불구하고 변호사선임비용에 대하여 보상할
다수 계약(각종 공제계약을 포함합니다)이 체결되어 있는
경우에는「현물급부 제공금액」을 보장대상 변호사선임비
용에 포함하여 제7조(보험금의 비례분담)에서 정한 바에
따릅니다.
⑦ 이 특별약관에 따른「변호사선임 현물급부」의 경우에
는 가지급 보험금을 지급하지 않습니다.
'''

EXAMPLE2 = ''' - 피보험자가 제휴회사로부터 현물급부를 제공받고 회
사가 제휴회사에 지급한 변호사선임 현물급부 비용
(「현물급부 제공금액」)이 500만원 일 때
   (단 계약1, 계약2 모두 당사 계약인 경우)
  ① 계약1:
     보상한도 500만원
     피보험자부담 공제금액 = 0원
     보상책임액 = 500만원
  ② 계약2:
     보상한도 500만원
     피보험자부담 공제금액 = 0원
     보상책임액 = 500만원
   이 경우, 피보험자는 회사로부터 1회의 변호사선임
현물급부를 제공받으며, 각 계약별 보상책임액 비율
에 따라 다음과 같이 분담하여 처리합니다.
     → 계약1 : 250만원 보상
(500만원 – 0원)
×
500
 = 250만원
500 + 500
     → 계약2 : 250만원 보상
(500만원 – 0원)
×
500
 = 250만원
500 + 500
'''

HIST_EVENT = {
    'd': '2026.10', 'ds': 20261019, 'e': '현물급부', 'hl': 'good',
    'n': '변호사선임비용(Ⅲ) 현물급부 선택 도입',
    'note': '자동차사고 변호사선임비용(Ⅲ) → 「(변호사선임 현물급부 선택가능)」 개정(2026.10.19 약관). '
            '보험금 대신 회사 제휴 법무법인이 변호사를 직접 선임해 주는 현물급부를 고를 수 있음 — 1사고당 1회 · '
            '홈페이지 공시 「현물급부 제공금액」을 지급 보험금으로 봄 · 다른 회사 변호사 담보가 없을 때만 제공 · '
            '제공이 불가하면 보험금으로 지급 · 현물급부는 가지급 없음.',
    'q': '변호사선임비용', 'syn': ['변호사선임비용', '현물급부', '변호사선임 현물급부'],
}
HIST_GROUP = '운전자비용담보 계통'


def flex(t):
    """줄바꿈·띄어쓰기가 상품마다 달라도 같은 글로 찾는다"""
    return r'\s*'.join(re.escape(c) for c in re.sub(r'\s+', '', t))


def sub1(pat, rep, s, n=None, what=''):
    out, k = re.subn(pat, rep, s)
    if n is not None and k != n:
        sys.exit('%s : %d곳(기대 %d)' % (what or pat[:40], k, n))
    return out


def revise(b):
    if '현물급부' in b:
        return b                                                      # 이미 반영
    b = sub1(r'^(\d+\. 자동차사고 변호사선임비용\(Ⅲ\))보장', r'\1\n(변호사선임 현물급부 선택가능)보장', b, 1, '제목')
    # 뒤 조부터 번호를 민다(이름이 서로 달라 겹치지 않는다)
    for old, new, n in [('제7조(준용규정)', '제10조(준용규정)', 1),
                        ('제6조(특별약관의 소멸)', '제9조(특별약관의 소멸)', 1),
                        ('제5조(보험금의 청구)', '제8조(보험금의 청구)', 1),
                        ('제4조(보험금의 비례분담)', '제7조(보험금의 비례분담)', 1),
                        ('제3조(보험금을 지급하지 않는 사유)', '제6조(보험금을 지급하지 않는 사유)', 2)]:   # 조 제목 + 제2조 ⑩ 인용
        b = sub1(flex(old), lambda m, new=new: re.sub(r'제\d+조', new.split('(')[0], m.group(0), 1), b, n, old)
    b = sub1(r'(?m)^(?=' + flex('제6조(보험금을 지급하지 않는 사유)') + r'\n회사는)', lambda m: ART345, b, 1, '제3~5조 삽입')
    b = sub1(flex('부담한 금액(단, 보험금을 지급하지 않는 사유에 해당하는 금액은 제외)'),
             lambda m: '부담한 금액 또는 현물급부 제공금액을 합산한 금액\n(단, 보험금을 지급하지 않는 사유에 해당하는 금액\n은 제외)',
             b, 1, '보장대상 변호사선임비용')
    b = sub1(r'(?m)^(?=' + flex('③ 피보험자가 다른 계약에 대하여 보험금 청구를 포기한') + ')', lambda m: EXAMPLE2, b, 1, '분담 예시')
    return b


def add_hist(H):
    g = next(g for g in H['groups'] if g['name'] == HIST_GROUP)
    g['events'] = [e for e in g['events'] if e.get('ds') != HIST_EVENT['ds'] or e.get('n') != HIST_EVENT['n']] + [HIST_EVENT]
    return H


PDFS = {'운전자': '무배당 메리츠 운전자 상해 종합보험2608약관.pdf', '케어프리': '무배당 메리츠 케어프리보험 M-Basket2607약관.pdf'}
FROM = {'운전자': 362, '케어프리': 1879}          # 이 쪽 뒤의 특약만 밀렸다


def printed_pages(path):
    """인쇄된 쪽 번호 → 그 쪽 글자(띄어쓰기 없앰)"""
    import pymupdf
    P = {}
    for pg in pymupdf.open(path):
        t = pg.get_text(); n = re.findall(r'(?m)^\s*(\d{1,4})\s*$', t)
        if n: P[int(n[-1])] = P.get(int(n[-1]), '') + re.sub(r'\s+', '', t)
    return P


def fix_pages(D):
    """새 판 약관에서 특약 제목이 있는 쪽으로 pg 를 옮긴다 — 세부보장은 부모와 같은 만큼"""
    moved = {}
    for P, f in PDFS.items():
        pages = printed_pages(os.path.join(ROOT, f))
        for r in D['riders']:
            if r['p'] != P or r.get('parent') or r.get('pg') is None or int(r['pg']) <= FROM[P]: continue
            key, pg = re.sub(r'\s+', '', r['n'])[:18], int(r['pg'])
            if key in pages.get(pg, ''): continue
            cand = [q for q in range(pg, pg + 8) if key in pages.get(q, '')]
            if not cand: sys.exit('%s %s : 새 약관에서 쪽을 못 찾음' % (r['id'], r['n']))
            moved[r['id']] = cand[0] - pg
            r['pg'] = cand[0]
        for r in D['riders']:
            if r['p'] == P and r.get('parent') in moved and r.get('pg') is not None:
                r['pg'] = int(r['pg']) + moved[r['parent']]
    print('쪽 번호 옮김 : 특약 %d건 (%s)' % (len(moved), ', '.join('%s %+d' % kv for kv in moved.items())))


def main(write):
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(PAT, html, re.S)
    D = inflate(json.loads(m.group(2)))
    by = {r['id']: r for r in D['riders']}
    for i in IDS:
        r = by[i]
        old = r['b']
        r['b'] = revise(old)
        r['n'] = NEW_NAME
        print('%s %s : 본문 %d → %d자 · %s' % (i, r['p'], len(old), len(r['b']),
              ' '.join(re.findall(r'(?m)^제\d+조', r['b'].split('특별약관', 1)[1]))))
    fix_pages(D)
    if not write:
        print(by[IDS[1]]['b'][:200]); return
    html = html[:m.start(2)] + json.dumps(deflate(D), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[m.end(2):]
    hp = r'(<script id="HISTORY" type="application/json">)(.*?)(</script>)'
    h = re.search(hp, html, re.S)
    H = add_hist(json.loads(h.group(2)))
    H['updated'] = '2026.10.20'
    html = html[:h.start(2)] + json.dumps(H, ensure_ascii=False, separators=(',', ':')) + html[h.end(2):]
    # 보상시뮬레이터(SIMSRC, base64) 안의 상품 히스토리 사본에도 같은 항목
    sm = re.search(r'(<script id="SIMSRC" type="text/plain">)(.*?)(</script>)', html, re.S)
    sim = base64.b64decode(sm.group(2)).decode('utf-8')
    h2 = re.search(hp, sim, re.S)
    H2 = add_hist(json.loads(h2.group(2)))
    H2['updated'] = H['updated']
    sim = sim[:h2.start(2)] + json.dumps(H2, ensure_ascii=False) + sim[h2.end(2):]
    html = html[:sm.start(2)] + base64.b64encode(sim.encode('utf-8')).decode('ascii') + html[sm.end(2):]
    io.open(TOOL, 'w', encoding='utf-8').write(html)
    print('tool.html · tool_body.js 반영')


if __name__ == '__main__':
    main('--write' in sys.argv)
