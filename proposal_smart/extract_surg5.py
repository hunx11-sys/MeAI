# -*- coding: utf-8 -*-
"""약관 【별표76】 1-5종 수술분류표Ⅱ PDF → surg5.json.
   사용 : python extract_surg5.py 별표76_1-5종수술분류표.pdf
   Ⅰ. 일반 질병·상해 수술(1~88항, 하위항 11-1 등 포함) · Ⅱ. 악성신생물 치료 목적 수술(C1~C3) · Ⅲ. 근치 방사선 조사(R1~R2).
   항목 안의 '단, ○○(KCD)로 인한 수술은 N종' 예외는 exceptions 로 구조화한다."""
import json, os, re, sys
def _items_from_cell(name, grades):
    """'11. 사지 절단수술 … 11-1. … 11-2. …' 처럼 하위항이 한 셀에 든 경우를 나눈다"""
    parts = re.split(r'\s(?=\d+-\d\.\s)', name)
    gs = grades.split()
    out = []
    subs = [p for p in parts if re.match(r'^\d+-\d\.', p)]
    for p, g in zip(subs, gs):
        m = re.match(r'^(\d+-\d)\.\s*(.+)$', p, re.S); out.append((m.group(1), m.group(2), int(g)))
    return out
def _exceptions(name):
    ex = []
    for m in re.finditer(r'단,\s*([^()]+?)\(한국표준질병사인분류\s*([A-Z]\d{2})\)\s*[으로]*\s*인한 수술은\s*(\d)종', name):
        ex.append({'kcd': m.group(2), 'grade': int(m.group(3)), 'why': m.group(1).strip()})
    if '대장의 용종' in name and '1종' in name: ex.append({'kcd': 'D12', 'grade': 1, 'why': '대장 용종·양성신생물 내시경 절제'}); ex.append({'kcd': 'K63.5', 'grade': 1, 'why': '대장 용종 내시경 절제'})
    return ex
def extract(pdf_path):
    import pdfplumber
    items, cat = [], None
    with pdfplumber.open(pdf_path) as pdf:
        for pi, p in enumerate(pdf.pages[:3]):
            for tb in p.extract_tables():
                for r in tb:
                    c = [(x or '').replace('\n', ' ').strip() for x in r]
                    if len(c) < 3 or c[0] == '구분': continue
                    if c[0]: cat = re.sub(r'\[.*|주\d\).*|\(.*?\)', '', re.sub(r'\s+', '', c[0]))
                    name = re.sub(r'\s+', ' ', c[1]); grade = c[2].strip()
                    if re.search(r'\d+-\d\.', name) and len(grade.split()) > 1:
                        for no, nm, g in _items_from_cell(name, grade):
                            items.append({'no': no, 'section': 'I', 'cat': cat, 'name': nm.strip(), 'grade': g, 'exceptions': _exceptions(nm)})
                        continue
                    m = re.match(r'^(\d+(?:-\d+)?)\.?\s+(.+)$', name)
                    if m and re.fullmatch(r'[1-5]', grade):
                        items.append({'no': m.group(1), 'section': 'I', 'cat': cat, 'name': m.group(2).strip(), 'grade': int(grade), 'exceptions': _exceptions(m.group(2))})
    # Ⅱ·Ⅲ (4쪽) — 표가 2단 텍스트라 항목을 직접 기술한다(약관 별표76 원문 기준)
    items += [
        {'no': 'C1', 'section': 'II', 'cat': '악성신생물치료목적의수술', 'name': '관혈적 악성신생물 근치수술 [내시경·카테터·고주파 등 경피적 수술 제외] · 복강경·흉강경 근치수술 포함(주4) · 비고형암 비관혈적 근치술(조혈모세포이식 등) 준용(주3)', 'grade': 5, 'exceptions': [{'kcd': 'C44', 'grade': 3, 'why': '기타피부암은 C1-1 3종'}]},
        {'no': 'C1-1', 'section': 'II', 'cat': '악성신생물치료목적의수술', 'name': '기타피부암(C44) 관혈적 근치수술', 'grade': 3, 'exceptions': []},
        {'no': 'C2', 'section': 'II', 'cat': '악성신생물치료목적의수술', 'name': '내시경 수술, 카테터·고주파 전극 등에 의한 악성신생물 수술 [60일 이내 2회 이상은 1회]', 'grade': 3, 'exceptions': []},
        {'no': 'C3', 'section': 'II', 'cat': '악성신생물치료목적의수술', 'name': '상기 이외의 기타 악성신생물 수술 [60일 이내 2회 이상은 1회]', 'grade': 3, 'exceptions': []},
        {'no': 'R1', 'section': 'III', 'cat': '근치방사선조사', 'name': '악성신생물 근치 방사선 조사 [5,000Rad 이상, 사이버나이프 정위적 방사선치료 포함]', 'grade': 3, 'exceptions': []},
        {'no': 'R2', 'section': 'III', 'cat': '근치방사선조사', 'name': '두개내 신생물 근치 감마나이프 정위적 방사선 치료', 'grade': 3, 'exceptions': []},
    ]
    notes = ['제자리암·경계성종양 수술은 Ⅰ(일반 질병) 항목 적용(Ⅱ 주1)', '흡인·천자·신경차단·미용성형·피임·검사목적(생검·복강경검사) 수술은 제외',
             '수술개시일부터 60일 이내 2회 이상 수술은 1회로 간주하는 항목 : 4(맘모톰 등), 53, 88, Ⅱ-2, Ⅱ-3, Ⅲ']
    return items, notes
if __name__ == '__main__':
    items, notes = extract(sys.argv[1])
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'surg5.json')
    json.dump({'source': '약관 【별표76】 1-5종 수술분류표Ⅱ', 'notes': notes, 'items': items}, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    from collections import Counter
    print('surg5.json 생성 :', dst, '| 항목', len(items), '· 종별', dict(sorted(Counter(i['grade'] for i in items).items())), '· 예외', sum(len(i['exceptions']) for i in items))
