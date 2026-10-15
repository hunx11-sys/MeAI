#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""식당의 cuisine(음식 종류) 글 → 음식 그림 27종 중 하나. 조립(build_japan.py)이 식당마다 dish 값을 붙일 때 쓴다.
   앞에 있는 규칙이 먼저 맞는다(예: '오키나와 소바' 는 소바보다 먼저, '두부 가쓰' 는 두부보다 돈가스가 먼저,
   '해산물 덮밥'·'장어덮밥'·'덴동' 은 덮밥보다 해산물·장어·덴푸라가 먼저). 맞는 것이 없으면 teishoku(정식·향토 요리)."""
import re

RULES = [
    ('okinawa_soba', r'오키나와\s*소바|야에야마\s*소바|다케토미\s*소바|소키'),
    ('takoyaki', r'다코야키|타코야키|아카시야키'),
    ('okonomiyaki', r'오코노미야키|몬자|야키소바|히로시마풍'),
    ('ramen', r'라멘|라면|쓰케멘|츠케멘|짬뽕|탄탄면'),
    ('sushi', r'초밥|스시|니기리|즈시'),
    ('unagi', r'장어|히쓰마부시|우나기'),
    ('tempura', r'덴푸라|튀김|덴동|텐동|덴무스'),
    ('katsu', r'돈가스|돈카츠|카쓰|가쓰(?!오)|커틀릿|멘치|구시카쓰|치킨난반'),
    ('udon', r'우동|기시멘'),
    ('soba', r'소바'),
    ('somen', r'소면|소멘|냉면'),
    ('tofu', r'두부|유도후|유바(?!리)'),
    ('seafood', r'해산물|해물|활어|사시미|생선|(^|[·\s(])굴|(^|[·\s(])게(?!이)|대게|털게|가리비|가쓰오|다타키|오징어|노케동|성게|연어|참치|복어|시장 식당'
                r'|새우|민물고기|송어|은어|히메마스'),
    ('beef', r'와규|소고기|스테이크|야키니쿠|고베규|히다규|아카우시|흑우|바사시|말고기|철판|규카쓰|규탄|사가규|바라야키|로스트비프'),
    ('hotpot', r'나베|샤브|샤부|스키야키|오뎅|전골|모쓰|미즈타키|온천\s*찜|지옥찜|증기\s*찜|아구\s*돼지'),  # 아구 돼지는 샤부샤부로 먹는 곳이 대부분
    ('grill', r'야키토리|꼬치|숯불|이자카야|징기스칸|지도리|로바타|바비큐|포장마차|야타이|닭구이|데바사키|코친|호네쓰키도리|게이찬|덴가쿠|주점'),
    ('gyoza', r'교자|만두|중화|부타만|딤섬|찐빵|타이피엔|광둥|중국'),
    ('curry', r'카레'),
    ('western', r'양식|오므라이스|햄버거|햄버그|버거|프렌치|이탈리안|파스타|피자|함박|핫도그|소시지|샌드위치|델리|스파게티'),
    ('donburi', r'덮밥|가마메시|가마솥밥|다이메시|에비메시|마부시'),
    ('kaiseki', r'가이세키|석식|역\s*도시락|에키벤|교토 요리|싯포쿠|료테이|갓포'),
    ('wagashi', r'화과자|말차|녹차|찻집|당고|경단|모찌|떡|양갱|다이후쿠|단팥|오하기'),
    ('dessert', r'디저트|파르페|푸딩|케이크|크레페|아이스|젤라토|과일|카스텔라|양과자|빙수|소프트|도넛'),
    ('cafe', r'카페|커피|베이커리|빵|브런치|티룸'),
    ('snack', r'간식|길거리|주먹밥|오니기리|푸드코트|편의점|타이야키|센베이|고로케|직판|도로역|시장$'
              r'|계란말이|달걀말이|다시마키|고헤이모치|어묵|가마보코|식당가|테마거리|먹거리|장터|휴게소'),
    ('drink', r'사케|시음|맥주|와인|양조|(^|[·\s(])바($|[·\s)])|시드르'),
    ('teishoku', r'.'),
]
_C = [(k, re.compile(p)) for k, p in RULES]


def _match(s):
    for k, rx in _C:
        if rx.search(s):
            return k
    return 'teishoku'


# 대표 메뉴(signature)로 다시 볼 때 빼는 것 : 곁들이 간식·디저트·음료가 그림을 정하면 어긋난다(예: 당고지루 → 화과자)
_SIDE = {'teishoku', 'wagashi', 'dessert', 'cafe', 'drink', 'snack'}


def dish_of(cuisine, name='', signature=''):
    k = _match(str(cuisine or '') or str(name or ''))
    if k == 'teishoku' and signature:
        # '향토 요리'처럼 넓은 음식 종류는 대표 메뉴를 앞에서부터 하나씩 본다
        for part in re.split(r'[·,、/]', str(signature)):
            k2 = _match(part)
            if k2 not in _SIDE:
                return k2
    return k


if __name__ == '__main__':
    import collections, glob, json, os, sys
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'guides')
    c, ex = collections.Counter(), collections.defaultdict(list)
    for f in glob.glob(os.path.join(root, '*.json')):
        g = json.load(open(f, encoding='utf-8'))
        for r in g['restaurants']:
            k = dish_of(r.get('cuisine'), r.get('name'), r.get('signature'))
            c[k] += 1
            if len(ex[k]) < 12:
                ex[k].append(r.get('cuisine'))
    for k, n in c.most_common():
        print('%-13s %3d  %s' % (k, n, ' / '.join(ex[k])))
