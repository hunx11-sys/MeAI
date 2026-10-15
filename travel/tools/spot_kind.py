#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""볼거리(spot)의 cat·이름 → 볼거리 그림(data/art_spots.json) 18종 중 하나. 조립이 볼거리마다 그림 열쇠를 정할 때 쓴다.
   자료에는 절과 신사가 모두 cat 'shrine' 하나로 들어 있어서, 이름으로 절(temple)과 신사(shrine)를 가른다.
   이름은 '·'·'+' 로 나눈 앞 토막부터 본다(예: '다이센지 절·오가미야마 신사' → 절). 한 토막 안에서는 신사 말(신사·신궁·다이샤·
   하치만구·덴만구·이나리·도리이…)이 절 말(…사·…지·…데라·…인·…도·절·대불·탑…)보다 먼저다('다케오 신사 대녹나무' → 신사).
   교회·성당·수도원은 절도 신사도 아니라 옛 거리 그림(street), 오키나와 우타키(성스러운 숲)는 자연(nature)으로 보낸다.
   그 밖의 cat 은 같은 이름의 그림, 모르는 cat 은 전망(view)."""
import re

KINDS = ('temple', 'shrine', 'castle', 'museum', 'street', 'market', 'shop', 'view', 'park', 'nature', 'sea',
         'night', 'onsen', 'theme', 'kids', 'cafe', 'station', 'airport')

# 이름 하나하나로 정해 둔 것(규칙으로 가르기 애매한 곳). 값은 그림 열쇠.
EXCEPTIONS = {
    '센조카쿠·오층탑': 'temple',   # 豊国神社(千畳閣) — 큰 나무 마루와 오층탑이 대표 모습이라 탑 그림이 더 맞는다
    '사이조 이나리': 'shrine',       # 最上稲荷 — 절이지만 큰 도리이로 알려진 곳
}

_CHURCH = re.compile(r'교회|성당|천주당|수도원|教会|修道院|天主堂')
_GROVE = re.compile(r'우타키|御嶽')
_SHRINE = re.compile(r'신사|신궁|다이샤|타이샤|하치만구|덴만구|텐만구|도쇼구|궁|이나리|도리이|神社|神宮|大社|宮|鳥居|稲荷')
_TEMPLE_WORD = re.compile(r'데라|대불|불상|열반상|마애불|탑|칸논|관음|사찰|寺|院|堂|塔|仏|観音')
_TEMPLE_END = re.compile(r'(?:(?<!신)사|지|인|도|덴|절)$')   # …사(신사 제외)·…지·…인·…도(堂)·…덴(殿)·절


def _seg_kind(seg):
    """한 토막 → 'shrine' / 'temple' / ''(모름)."""
    if _SHRINE.search(seg):
        return 'shrine'
    if _TEMPLE_WORD.search(seg):
        return 'temple'
    for tok in re.split(r'[\s()（）\[\]]+', seg):
        if len(tok) >= 2 and _TEMPLE_END.search(tok) or tok == '절':
            return 'temple'
    return ''


def shrine_or_temple(name, name_ja=''):
    name = str(name or '').strip()
    if name in EXCEPTIONS:
        return EXCEPTIONS[name]
    both = name + ' ' + str(name_ja or '')
    if _CHURCH.search(both):
        return 'street'
    if _GROVE.search(both):
        return 'nature'
    for seg in re.split(r'\s*[·・+＋/]\s*', name):
        k = _seg_kind(seg)
        if k:
            return k
    # 한글 이름으로 못 가르면 일본어 이름을 같은 순서로 본다
    for seg in re.split(r'\s*[·・+＋/]\s*', str(name_ja or '')):
        k = _seg_kind(seg)
        if k:
            return k
    return 'shrine'


def spot_kind(cat, name='', name_ja=''):
    """볼거리 그림 열쇠. name 은 한글 이름, name_ja 는(있으면) 일본어 이름 — 한글 이름만으로도 맞게 가르도록 규칙을 맞춰 두었다."""
    cat = str(cat or '').strip()
    if cat == 'shrine':
        return shrine_or_temple(name, name_ja)
    if cat == 'temple':
        return 'temple'
    return cat if cat in KINDS else 'view'


if __name__ == '__main__':
    import collections, glob, json, os
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'guides')
    c, rows, diff = collections.Counter(), [], []
    for f in sorted(glob.glob(os.path.join(root, '*.json'))):
        g = json.load(open(f, encoding='utf-8'))
        for s in g.get('spots') or []:
            k = spot_kind(s.get('cat'), s.get('name'), s.get('name_ja'))
            c[k] += 1
            if s.get('cat') == 'shrine':
                rows.append((os.path.basename(f)[:-5], s.get('name'), s.get('name_ja', ''), k))
                if spot_kind('shrine', s.get('name')) != k:   # 한글 이름만 줬을 때와 다르면 알린다
                    diff.append(s.get('name'))
    for k, n in c.most_common():
        print('%-8s %3d' % (k, n))
    print('\n── cat=shrine %d곳 ──' % len(rows))
    for city, nm, ja, k in rows:
        print('%-7s %-15s %-30s %s' % (k, city, nm, ja))
    if diff:
        print('\n한글 이름만으로는 다르게 갈리는 곳:', ', '.join(diff))
