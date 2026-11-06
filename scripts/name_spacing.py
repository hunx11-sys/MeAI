# -*- coding: utf-8 -*-
"""
특약 이름에 약관 줄바꿈 자리로 끼어든 띄어쓰기 바로잡기 (2026-11-06)

약관 PDF 에서 특약 이름을 뽑을 때, 이름이 두 줄에 걸치면 줄과 줄을 띄어쓰기로 이어 붙여
「주요치 료비」 「연 간1회한」 「1 0년간」 「체 증형」 「갑상 선암」 같은 이름이 생겼다.

판정 규칙 — 이름 속 띄어쓴 곳마다 그 상품 약관 글자(같은 줄 안)를 본다.
   · 약관이 같은 줄에서 띄어 씀(「암 주요치료비」)   → 그대로 둔다(약관 표기)
   · 약관이 붙여 씀(「주요치료비」)                  → 띄어쓰기를 뺀다
   · 둘 다 안 보임                                   → 그대로 둔다
비교 · 계산은 띄어쓰기를 지우고 하므로(matcher.base · scen_engine.nname) 지급 판정에는 영향이 없다.

쓰는 곳
   proposal_smart/extract_terms_extra.py : 약관에서 뽑은 특약 · 세부보장 이름에 바로 적용(보강 마스터)
   scripts/fix_name_spacing.py           : 영업지원도구(tool.html) 데이터 이름을 그 상품 약관으로 바로잡기
"""
import re

_DL = re.compile(r'[\s\[\]\(\),·/]')


def flat(pages):
    """쪽 글자 목록 → 한 덩어리(줄은 줄바꿈으로 나누고, 줄 안의 여러 칸 띄어쓰기는 한 칸으로)"""
    return '\n'.join(re.sub(r'[ \t ]+', ' ', l).strip() for p in pages for l in p.split('\n'))


def _frag(s, i, d):
    j = i
    if d < 0:
        while j > 0 and not _DL.match(s[j - 1]): j -= 1
        return s[j:i]
    while j < len(s) and not _DL.match(s[j]): j += 1
    return s[i:j]


def unbreak(name, text, keep=None, ref=None):
    """약관 글자 text 기준으로 이름의 잘못 끼어든 띄어쓰기를 뺀다 → (고친 이름, [(띄어쓴 곳, 붙인 곳)])
       keep : 띄어쓴 표기가 여기(다른 상품 약관 등)에 있으면 약관 표기로 보고 그대로 둔다
       ref  : 붙여 쓴 표기를 이 글자(감수본 특약 이름 등)에서도 찾는다 — 띄어쓴 표기가 ref 에 없을 때만"""
    s, fixes = name or '', []
    for _ in range(6):
        changed = False
        for m in list(re.finditer(r' +', s))[::-1]:          # 뒤에서부터 — 앞쪽 자리 번호가 흔들리지 않게
            i, j = m.start(), m.end()
            L, R = _frag(s, i, -1), _frag(s, j, 1)
            if not L or not R: continue
            sp, jo = L + ' ' + R, L + R
            if sp in text or (keep and sp in keep): continue
            if jo not in text and not (ref and jo in ref and sp not in ref): continue
            s = s[:i] + s[j:]; fixes.append((sp, jo)); changed = True
        if not changed: break
    return s, fixes
