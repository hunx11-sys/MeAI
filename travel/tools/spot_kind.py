#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""볼거리(spot)의 cat·이름 → 볼거리 그림(data/art_spots.json) 21종 중 하나. 조립이 볼거리마다 그림 열쇠를 정할 때 쓴다.
   자료에는 절과 신사가 모두 cat 'shrine' 하나로 들어 있어서, 이름으로 절(temple)과 신사(shrine)를 가른다.
   이름은 '·'·'+' 로 나눈 앞 토막부터 본다(예: '다이센지 절·오가미야마 신사' → 절). 한 토막 안에서는 신사 말(신사·신궁·다이샤·
   하치만구·덴만구·이나리·도리이…)이 절 말(…사·…지·…데라·…인·…도·절·대불·탑…)보다 먼저다('다케오 신사 대녹나무' → 신사).
   교회·성당·수도원은 절도 신사도 아니라 옛 거리 그림(street), 오키나와 우타키(성스러운 숲)는 숲길(forest)로 보낸다.

   두루뭉술한 cat 은 이름으로 한 번 더 가른다(한글 이름만으로 맞게 갈리도록 맞춰 두었다 — 조립은 한글 이름만 넘긴다).
   · castle : 절 이름(금각사·뵤도인 봉황당 …) → 절, 궁 터·고분·유적 → 공원, 성하마을 → 옛 거리, 금산·원폭돔 → 박물관
   · view   : 타워·빌딩·전망실 등 시내 높은 곳만 도시 전망(view). 바다·곶·등대·다리 → 바다 전망대(lookout),
              호수·연못·댐·폭포·나무·고원 → 자연(nature), 산·로프웨이·언덕·전망대 → lookout, 관람차 → 놀이공원(theme)
   · kids   : 동물원·목장 → 동물원(zoo), 수족관 → 수족관(kids), 박물관·과학관 → 박물관, 철도 → 역, 항공 → 공항,
              호빵맨·어린이의 나라 → 놀이공원, 공방·학교·체험 → 가게
   · nature : 대나무숲·길·가로수·숲·맹그로브 → 숲길(forest). 남쪽(오키나와·미야자키·가고시마)은 눈 덮인 산 그림을 피해
              산·폭포·협곡·호수·고원이라고 적힌 곳이 아니면 숲길(south=True 로 부른다 — is_south(guide))
   그 밖의 cat 은 같은 이름의 그림, 모르는 cat 은 전망(view)."""
import re

KINDS = ('temple', 'shrine', 'castle', 'museum', 'street', 'market', 'shop', 'view', 'park', 'nature', 'sea',
         'night', 'onsen', 'theme', 'kids', 'cafe', 'station', 'airport', 'zoo', 'lookout', 'forest')

# 남쪽(눈 덮인 산 그림이 어울리지 않는 곳) : 가이드의 region 또는 key
SOUTH_REGIONS = ('오키나와',)
SOUTH_KEYS = ('miyazaki', 'kagoshima')


def is_south(guide):
    """가이드 자료(dict) → spot_kind(..., south=) 에 넘길 값."""
    guide = guide or {}
    return guide.get('region') in SOUTH_REGIONS or guide.get('key') in SOUTH_KEYS


# 이름 하나하나로 정해 둔 것(규칙으로 가르기 애매한 곳). 값은 그림 열쇠. cat 과 상관없이 먼저 본다.
EXCEPTIONS = {
    '센조카쿠·오층탑': 'temple',   # 豊国神社(千畳閣) — 큰 나무 마루와 오층탑이 대표 모습이라 탑 그림이 더 맞는다
    '사이조 이나리': 'shrine',       # 最上稲荷 — 절이지만 큰 도리이로 알려진 곳
    '나카바시 다리': 'park',         # 中橋 — 다카야마 옛 거리의 붉은 다리(공원 그림의 붉은 다리)
    '반다이 다리': 'view',           # 萬代橋 — 니가타 시내 한가운데 돌다리
    '우키미도(사기이케 연못)': 'park',  # 浮見堂 — 연못 위 정자
    '아스팜 전망대': 'view',         # 青森県観光物産館アスパム — 시내 세모꼴 건물 전망층
    '아레이 가라스코지마': 'lookout',  # 구레 항구, 잠수함이 보이는 바닷가
    '우시마도 올리브원': 'lookout',    # 세토 내해가 내려다보이는 언덕
    '노란 호박(구사마 야요이)': 'museum',  # 나오시마 바닷가 미술 작품
    '구라시키 강 나룻배': 'street',    # 구라시키 미관지구 운하
    '고메즈카': 'nature',             # 아소 들판의 둥근 화산 언덕
    '오기마치 성터 전망대': 'nature',  # 시라카와고 합장촌 골짜기
    '신호타카 로프웨이': 'nature',     # 북알프스 눈 덮인 봉우리
    '아소 카도리 도미니언': 'zoo',     # 곰·원숭이 동물 공원
    '구마몬 스퀘어': 'shop',          # 구마몬 기념품·무대
    '가부시마(괭이갈매기 번식지)': 'lookout',  # 바닷가 작은 섬
    '그린피아 마키노하라': 'theme',    # 차밭 언덕의 놀이공원
    '도리이케': 'lookout',            # 미야코 시모지시마 바닷가 바위 사이 두 연못(通り池)
    '미야코지마 해중공원': 'kids',     # 바닷속 관찰 시설(수조 그림이 맞음)
}

_CHURCH = re.compile(r'교회|성당|천주당|수도원|教会|修道院|天主堂')
_GROVE = re.compile(r'우타키|御嶽')
_SHRINE = re.compile(r'신사|신궁|다이샤|타이샤|하치만구|덴만구|텐만구|도쇼구|궁|이나리|도리이|神社|神宮|大社|宮|鳥居|稲荷')
_TEMPLE_WORD = re.compile(r'데라|대불|불상|열반상|마애불|탑|칸논|관음|사찰|寺|院|堂|塔|仏|観音')
_TEMPLE_END = re.compile(r'(?:(?<!신)사|지|인|도|덴|절)$')   # …사(신사 제외)·…지·…인·…도(堂)·…덴(殿)·절
_TOK = re.compile(r'[\s()（）\[\]·・+＋/]+')

# castle
_CASTLE_TOWN = re.compile(r'성하마을|城下町')
_CASTLE_WORD = re.compile(r'성(?:$|\s|터|[()·])')   # 한글 이름에서만 본다(平城宮跡 의 城 은 성이 아니다)
_CASTLE_TEMPLE_END = re.compile(r'(?:(?<!신)사|인|당)$')   # 금각사·뵤도인·봉황당 (…도 는 '사도 금산' 때문에 뺐다)
_CASTLE_TEMPLE_JA = re.compile(r'寺|院|堂')
_RUINS = re.compile(r'궁\s?터|궁\s?유적|(?<!성)\s터|고분|유적|역사공원|宮跡|古墳|遺跡')
_MINE_MEMORIAL = re.compile(r'금산|광산|원폭|金山|鉱山|原爆')

# view
_WHEEL = re.compile(r'관람차|観覧車')
_CITY = re.compile(r'타워|빌딩|스카이트리|스카이가든|SKY|전망실|도청|청사|하루카스|힐즈|우메다|쓰텐카쿠|'
                   r'タワー|ビル|展望室|テレビ塔|ハルカス|ヒルズ|通天閣', re.I)
_SEA = re.compile(r'바다|해안|해변|비치|해협|해상|곶|자키|미사키|등대|만자모|(?:^|[\s(])다리|대교|고쿄|잔교|섬|시마나미|'
                  r'海|岬|灯台|橋|島|ビーチ|しまなみ')
_SEA_KO = re.compile(r'바다|해안|해변|비치|곶|미사키|시마나미')   # nature 에서는 한글 바닷말만(침하교·대현수교·…섬 종유동은 바다가 아님)
_WATER = re.compile(r'호수|연못|댐|폭포|협곡|계곡')
_TREE = re.compile(r'나무')
_HIGHLAND = re.compile(r'고원')
_DECK = re.compile(r'전망(?:대|소|공원)|展望台|展望所')

# kids
_ZOO = re.compile(r'동물|동식물원|몬키|원숭이|목장|마키바|사파리|動物|牧場|まきば|モンキー|サファリ')
_AQUA = re.compile(r'수족관|아쿠아|씨월드|시 파라다이스|해중|마린|水族館|アクア|シーワールド|シーパラ|海中|マリン|うみたまご', re.I)
_KIDS_THEME = re.compile(r'호빵맨|앙팡맨|어린이의 성|어린이의 나라|어린이 나라|랜드|アンパンマン|こどもの|ランド')
_PLANE = re.compile(r'항공|플라이트|航空|FLIGHT', re.I)
_RAIL = re.compile(r'철도|鉄道')
_MUSEUM = re.compile(r'박물관|과학|뮤지엄|기념관|미술관|테디베어|博物館|科学館|ミュージアム|記念館|美術館|テディベア')
_CRAFT = re.compile(r'공방|학교|체험|만들기|공예|센베이|工房|学校|体験|せんべい')
_FARM = re.compile(r'과일|따기|딸기|果')

# nature
_FOREST = re.compile(r'대나무|숲|길|가로수|우타키|산책로|맹그로브|정글|원시림|송림|마쓰바라|'
                     r'竹|並木|森|小径|御嶽|原生林|松原|マングローブ')
_DUNE = re.compile(r'사구|砂丘')
_GARDEN = re.compile(r'허브원|정원|ハーブ園|庭園')
_BOAT = re.compile(r'뱃놀이|川下り')
_SOUTH_KEEP = re.compile(r'산|야마|다케|폭포|협곡|호수|호$|고원|화구|岳|山|滝|峡|湖|高原|火口')
_SOUTH_JUNGLE = re.compile(r'크루즈|クルーズ|遊覧船')


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
        return 'forest'
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


def _tokens(name):
    return [t for t in _TOK.split(name) if t]


def _castle(name, ja, both):
    if _CASTLE_TOWN.search(both):
        return 'street'
    castle_word = _CASTLE_WORD.search(name)
    if not castle_word:
        if any(len(t) >= 2 and _CASTLE_TEMPLE_END.search(t) for t in _tokens(name)) or _CASTLE_TEMPLE_JA.search(ja):
            return 'temple'
        if _RUINS.search(both):
            return 'park'
    if _MINE_MEMORIAL.search(both):
        return 'museum'
    return 'castle'


def _view(name, ja, both):
    if _CHURCH.search(both):
        return 'street'
    if _WHEEL.search(both):
        return 'theme'
    if _CITY.search(both):
        return 'view'
    if _SEA.search(both) or _DECK.search(both):
        return 'lookout'
    if any(_seg_kind(s) == 'temple' for s in re.split(r'\s*[·・+＋/]\s*', name)):   # 니가쓰도(도다이지)·고다이도
        return 'temple'
    if _WATER.search(name) or _TREE.search(name) or _HIGHLAND.search(name):
        return 'nature'
    if any(t.endswith('성') and len(t) >= 3 for t in _tokens(name)):   # 마쓰야마성 로프웨이
        return 'castle'
    return 'lookout'   # 산·로프웨이·언덕·전망대 그리고 이름에 실마리가 없는 경치 좋은 곳


def _kids(name, ja, both):
    if _ZOO.search(both):
        return 'zoo'
    if _AQUA.search(both):
        return 'kids'
    if _KIDS_THEME.search(both):
        return 'theme'
    if _PLANE.search(both):
        return 'airport'
    if _RAIL.search(both):
        return 'station'
    if _MUSEUM.search(both):
        return 'museum'
    if _CRAFT.search(both):
        return 'shop'
    if _FARM.search(both):
        return 'park'
    return 'kids'


def _nature(name, ja, both, south):
    if any(len(t) >= 3 and re.search(r'(?:지|(?<!신)사)$', t) for t in _tokens(name)) or '寺' in ja:   # 도후쿠지·쓰텐쿄
        return 'temple'
    if re.search(r'동물원|動物園', both):
        return 'zoo'
    if _FOREST.search(both):
        return 'forest'
    if _DUNE.search(both):
        return 'sea'
    if _SEA_KO.search(name):
        return 'lookout'
    if _GARDEN.search(both) or _BOAT.search(both):
        return 'park'
    if south and (_SOUTH_JUNGLE.search(both) or not _SOUTH_KEEP.search(name)):
        return 'forest'
    return 'nature'


def spot_kind(cat, name='', name_ja='', south=False):
    """볼거리 그림 열쇠. name 은 한글 이름, name_ja 는(있으면) 일본어 이름 — 한글 이름만으로도 맞게 가르도록 규칙을 맞춰 두었다.
       south=True 면(오키나와·미야자키·가고시마, is_south(guide)) 자연 볼거리에 눈 덮인 산 그림 대신 숲길을 쓴다."""
    cat = str(cat or '').strip()
    name = str(name or '').strip()
    ja = str(name_ja or '').strip()
    if name in EXCEPTIONS:
        return EXCEPTIONS[name]
    both = name + ' ' + ja
    if cat == 'shrine':
        return shrine_or_temple(name, ja)
    if cat == 'temple':
        return 'temple'
    if cat == 'castle':
        return _castle(name, ja, both)
    if cat == 'view':
        return _view(name, ja, both)
    if cat == 'kids':
        return _kids(name, ja, both)
    if cat == 'nature':
        return _nature(name, ja, both, south)
    return cat if cat in KINDS else 'view'


def _spot_kind_v1(cat, name='', name_ja=''):
    """바꾸기 전(그림 18종) 규칙 — 아래 점검 목록에서 무엇이 바뀌었는지 보일 때만 쓴다."""
    cat = str(cat or '').strip()
    if cat == 'shrine':
        k = shrine_or_temple(name, name_ja)
        return 'nature' if k == 'forest' else k
    if cat == 'temple':
        return 'temple'
    return cat if cat in KINDS[:18] else 'view'


if __name__ == '__main__':
    import collections, glob, json, os
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'guides')
    before, after, rows, changed, diff = collections.Counter(), collections.Counter(), [], [], []
    for f in sorted(glob.glob(os.path.join(root, '*.json'))):
        g = json.load(open(f, encoding='utf-8'))
        south = is_south(g)
        for s in g.get('spots') or []:
            cat, nm, ja = s.get('cat'), s.get('name'), s.get('name_ja', '')
            old = _spot_kind_v1(cat, nm, ja)
            k = spot_kind(cat, nm, ja, south)
            before[old] += 1
            after[k] += 1
            if cat == 'shrine':
                rows.append((g['key'], nm, ja, k))
            if old != k:
                changed.append((old, k, cat, nm, g['key']))
            if spot_kind(cat, nm, south=south) != k:   # 한글 이름만 줬을 때(조립)와 다르면 알린다
                diff.append('%s(%s → %s)' % (nm, k, spot_kind(cat, nm, south=south)))
    print('그림 열쇠별 볼거리 수 (전 → 후)')
    for k in KINDS:
        print('  %-8s %3d → %3d%s' % (k, before[k], after[k], '' if before[k] == after[k] else '  (%+d)' % (after[k] - before[k])))
    print('\n── cat=shrine %d곳 ──' % len(rows))
    for city, nm, ja, k in rows:
        print('%-7s %-15s %-30s %s' % (k, city, nm, ja))
    print('\n── 바뀐 곳 %d곳 (전 → 후 | cat | 이름 | 가이드) ──' % len(changed))
    for old, k, cat, nm, key in sorted(changed, key=lambda r: (r[2], r[1], r[4])):
        print('%-7s → %-8s| %-7s| %s | %s' % (old, k, cat, nm, key))
    if diff:
        print('\n한글 이름만으로는 다르게 갈리는 곳:', ', '.join(diff))
