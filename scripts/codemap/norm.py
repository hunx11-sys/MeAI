# -*- coding: utf-8 -*-
import re
GOJI = re.compile(r'\((?:[^()]{0,30}가입)\)')
def strip_tags(s):
    s = (s or '').replace(' ', ' ')
    s = re.sub(r'\[(특별조건부|계약전환용|기본계약)\]', '', s)
    s = GOJI.sub('', s)
    s = re.sub(r'\(\d+년갱신\)', '', s)
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'^갱신형', '', s)
    s = re.sub(r'(?<![A-Za-z])(IV|III|II)(?![A-Za-z])', lambda m: {'II': 'Ⅱ', 'III': 'Ⅲ', 'IV': 'Ⅳ'}[m.group(1)], s)   # 정보계가 Ⅱ 를 영문 II 로도 씀
    s = s.replace('ㆍ', '·').replace('․', '·').replace('（', '(').replace('）', ')').replace('，', ',')
    return s
def key(s):
    # 가운뎃점도 지운다(2026-11-24) — 정보계 「구내폭발파열손해」 ↔ 약관 「구내폭발․파열손해」 처럼 점 유무만 다른 이름(설계서 쪽 matcher.base 와 같은 기준)
    return re.sub(r'[\[\]()·]', '', strip_tags(s))
