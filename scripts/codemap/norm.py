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
    return re.sub(r'[\[\]()]', '', strip_tags(s))
