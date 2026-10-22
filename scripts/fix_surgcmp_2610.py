# -*- coding: utf-8 -*-
"""
특약검색기 「수술비 비교」 ⑥ 131대 상세(SC.d131) 글자를 약관 분류표대로 바로잡는다 (2026-10-20)

코드 대조(특약 마스터 케219 세부보장 11개 ↔ 화면 표) 결과 보장 범위는 모두 같고, 아래는 표시 글자만 고친다.
  · 다빈도62대 「맥락막 및 망막의 장애 H30-H36」 : 제외 3가지를 코드로 밝히고, H35.3 은 바로 위 「황반변성」 줄로 보장됨을 적음
  · 특정31대 B05.2 「수두에서의 폐렴」 → 약관 「폐렴이 합병된 홍역」 · B01.2 「수두폐렴」 · A48.1 「레지오넬라병」
  · 괄호 잘림 2줄(톡소포자충간염 · 볼거리수막염) · A83-A86 제외 코드 줄바꿈
⑤ 1-7종 상세(SC.d17) : 수술코드 630개 · 구분 266개 · 종은 약관 4권(케어프리 · 운전자 · 통합간편 2종) PDF 와 모두 일치.
  다만 수술코드가 하나뿐인 줄의 이름을 줄이면서 지급 조건이 빠진 것이 있어(「치료적」 자궁소파술 · 「재원기간 2일 이상」 ·
  「개심술 미동반」 · 구분명만 보면 난관결찰도 되는 것처럼 보이던 N121 등) 그런 줄은 약관 수술코드 이름을 그대로 쓴다.

실행 : python3 scripts/fix_surgcmp_2610.py [--write]
"""
import io, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, 'tool.html')

FIX = [  # (찾을 줄 : dis 로 고를 조건, kcd) → 바꿀 값
    (lambda r: r['kcd'] == 'H30-H36',
     {'dis': '맥락막 및 망막의 장애 — 단, 아래 질병은 제외 ① 배경망막병증 및 망막혈관변화 중 고혈압성 망막병증(H35.0 중 해당 상병 → 특정31대) '
             '② 황반 및 후극부의 변성(H35.3 → 위 「황반 및 후극부의 변성」 줄로 보장) ③ 당뇨병의 망막병증(H36.0 → 특정31대)',
      'kcd': 'H30-H36 (H35.0 일부 · H35.3 · H36.0 제외)'}),
    (lambda r: r['kcd'] == 'B05.2†', {'dis': '폐렴이 합병된 홍역(J17.1*)'}),
    (lambda r: r['kcd'] == 'B01.2†', {'dis': '수두폐렴(J17.1*)'}),
    (lambda r: r['kcd'] == 'A48.1', {'dis': '레지오넬라병'}),
    (lambda r: r['dis'] == '톡소포자충간염(K77.0*', {'dis': '톡소포자충간염(K77.0*)'}),
    (lambda r: r['dis'] == '볼거리수막염(G02.0*', {'dis': '볼거리수막염(G02.0*)'}),
    (lambda r: r['kcd'].startswith('A83-A86'), {'kcd': 'A83-A86 (A85.0†, A85.1† 제외)'}),
]


def spacing(t):
    """약관 PDF 에서 줄이 붙으며 생긴 띄어쓰기만 다듬는다(글자는 그대로)"""
    for a, b in [('설치술또는', '설치술 또는'), ('치료를위한', '치료를 위한'), ('비뇨기질환의', '비뇨기 질환의'), ('비뇨기계시술', '비뇨기계 시술'),
                 ('심흉부수술(', '심흉부 수술('), ('피부이식혹은', '피부이식 혹은'), ('및약물', '및 약물'), ('제거 및전환술', '제거 및 전환술'),
                 ('수술및', '수술 및'), ('의경우', '의 경우'), ('외상치료목적의', '외상 치료목적의'), ('주요시술', '주요 시술'),
                 ('유방질환에', '유방 질환에'), ('장치미사용', '장치 미사용'), ('대사장애절단술', '대사장애 절단술'), ('대사장애수족부', '대사장애 수족부'),
                 ('요도신생물', '요도 신생물'), ('유산후', '유산 후'), ('관련자궁', '관련 자궁'), ('시험적거치술', '시험적 거치술'),
                 ('질환의신경', '질환의 신경'), ('질환의시험적', '질환의 시험적'), ('질환의경피적', '질환의 경피적'), ('남성생식기계시술', '남성생식기계 시술'),
                 ('관절수술', '관절 수술'), ('대퇴부수술', '대퇴부 수술'), ('비골수술', '비골 수술'), ('농양수술', '농양 수술'), ('탈장수술', '탈장 수술'),
                 ('협착증수술', '협착증 수술'), ('을위한', '을 위한'), ('를위한', '를 위한'), ('협착을위한방사선하', '협착을 위한 방사선하'),
                 ('위한방사선하', '위한 방사선하'), ('위한체외', '위한 체외'), ('에대한', '에 대한'), ('미세혈관조직이식', '미세혈관 조직이식'),
                 ('종양절제술', '종양 절제술'), ('또는절제술', '또는 절제술'), ('피판 및피부이식', '피판 및 피부이식'), ('골 및 관절수술', '골 및 관절 수술')]:
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()


def names17(html):
    """1-7종 별표 정리본(케어프리 표) → 수술코드 : 약관 이름"""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    from tooldata import PAT
    D = json.loads(re.search(PAT, html, re.S).group(2))
    x = D['tables']['34700df0f3']['text']
    return {mm.group(1): spacing(mm.group(2)) for mm in re.finditer(r'\[([A-Z]\d{3})\]\s*(.*?)\s*→\s*(\d)종', x)}


DESC17 = {'N121': '복강경 수술 — 구분 이름(239. 복강경수술 및 기타난관 결찰술)과 달리 보장 코드는 N121 하나뿐'}


def main(write):
    html = io.open(TOOL, encoding='utf-8').read()
    m = re.search(r'(SC\.d131=)(\[.*?\])(;\n)', html)
    rows = json.loads(m.group(2))
    for cond, new in FIX:
        hit = [r for r in rows if cond(r)]
        if len(hit) != 1:
            if any(all(r.get(k) == v for k, v in new.items()) for r in rows): continue      # 이미 고침
            sys.exit('맞는 줄 %d개 : %s' % (len(hit), new))
        hit[0].update(new); print('고침 :', hit[0]['dis'][:40], hit[0]['kcd'])
    html = html[:m.start(2)] + json.dumps(rows, ensure_ascii=False) + html[m.end(2):]
    T = names17(html)
    m = re.search(r'(SC\.d17=)(\[.*?\])(;\n)', html)
    d17 = json.loads(m.group(2))
    n = lambda t: re.sub(r'[\s∙·ㆍ,]', '', t)
    k = 0
    for r in d17:
        if r['code'] in T and n(r['name']) != n(T[r['code']]):
            r['name'] = T[r['code']]; k += 1
        if r['code'] in DESC17: r['desc'] = DESC17[r['code']]
    print('1-7종 이름을 약관 수술코드 이름으로 :', k, '줄')
    if write:
        html = html[:m.start(2)] + json.dumps(d17, ensure_ascii=False) + html[m.end(2):]
        io.open(TOOL, 'w', encoding='utf-8').write(html)
        print('tool.html 저장')


if __name__ == '__main__':
    main('--write' in sys.argv)
