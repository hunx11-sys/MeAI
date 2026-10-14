#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""식당의 cuisine(음식 종류) 글 → 음식 그림 23종 중 하나. 조립(build_japan.py)이 식당마다 dish 값을 붙일 때 쓴다.
   앞에 있는 규칙이 먼저 맞는다(예: '오키나와 소바' 는 소바보다 먼저). 맞는 것이 없으면 teishoku(정식·향토 요리)."""
import re

RULES = [
    ('okinawa_soba', r'오키나와\s*소바|야에야마\s*소바|소키'),
    ('takoyaki', r'다코야키|타코야키'),
    ('okonomiyaki', r'오코노미야키|몬자|야키소바|히로시마풍'),
    ('ramen', r'라멘|라면|쓰케멘|츠케멘|짬뽕|탄탄면'),
    ('sushi', r'초밥|스시|니기리|가키노하즈시'),
    ('unagi', r'장어|히쓰마부시|우나기'),
    ('tempura', r'덴푸라|튀김|덴동|텐동'),
    ('katsu', r'돈가스|돈카츠|카쓰|가쓰(?!오)|커틀릿|멘치|구시카쓰|치킨난반'),
    ('udon', r'우동|기시멘'),
    ('soba', r'소바'),
    ('seafood', r'해산물|해물|활어|사시미|생선|(^|[·\s(])굴|(^|[·\s(])게|대게|털게|가리비|가쓰오|다타키|오징어|노케동|성게|연어|참치|복어|시장 식당'),
    ('beef', r'와규|소고기|스테이크|야키니쿠|고베규|히다규|아카우시|흑우|바사시|말고기|철판|규카쓰'),
    ('hotpot', r'나베|샤브|스키야키|오뎅|전골|모쓰|미즈타키'),
    ('grill', r'야키토리|꼬치|숯불|이자카야|징기스칸|지도리|로바타|바비큐|포장마차|야타이'),
    ('gyoza', r'교자|만두|중화|부타만|딤섬|찐빵|타이피엔'),
    ('curry', r'카레'),
    ('western', r'양식|오므라이스|햄버거|햄버그|버거|프렌치|이탈리안|파스타|피자|함박'),
    ('wagashi', r'화과자|말차|녹차|찻집|당고|경단|모찌|떡|양갱|다이후쿠|단팥'),
    ('dessert', r'디저트|파르페|푸딩|케이크|크레페|아이스|젤라토|과일|카스텔라|양과자|빙수|소프트'),
    ('cafe', r'카페|커피|베이커리|빵|브런치|티룸'),
    ('snack', r'간식|길거리|주먹밥|오니기리|푸드코트|편의점|타이야키|센베이|고로케|직판|도로역|시장$'),
    ('drink', r'사케|시음|맥주|와인|양조|(^|[·\s(])바($|[·\s)])'),
    ('teishoku', r'.'),
]
_C = [(k, re.compile(p)) for k, p in RULES]


def dish_of(cuisine, name=''):
    s = str(cuisine or '') or str(name or '')
    for k, rx in _C:
        if rx.search(s):
            return k
    return 'teishoku'


if __name__ == '__main__':
    import collections, glob, json, os, sys
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'guides')
    c, ex = collections.Counter(), collections.defaultdict(list)
    for f in glob.glob(os.path.join(root, '*.json')):
        g = json.load(open(f, encoding='utf-8'))
        for r in g['restaurants']:
            k = dish_of(r.get('cuisine'), r.get('name'))
            c[k] += 1
            if len(ex[k]) < 12:
                ex[k].append(r.get('cuisine'))
    for k, n in c.most_common():
        print('%-13s %3d  %s' % (k, n, ' / '.join(ex[k])))
