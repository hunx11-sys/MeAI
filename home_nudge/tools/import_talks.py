# 화법 798건 가져오기 : v3 목업(MeAIHome 넛지 목업 HTML) 안의 window.NZ_TALKS 를 꺼내 data/talks798.json 으로 만든다.
# 제출자 이름은 기본으로 가운데 글자를 가린다(저장소에 실명을 두지 않는다). 실명이 필요한 사내 시연판은 --keep-names 로 따로 만들고 저장소에 올리지 않는다.
# 쓰는 법 : python3 home_nudge/tools/import_talks.py <v3목업.html> [--out home_nudge/data/talks798.json] [--keep-names]
import json, sys, os, argparse, random

def mask(n):
    n = (n or '').strip()
    if len(n) <= 1: return n
    if len(n) == 2: return n[0] + '○'
    if len(n) > 4: return n[0] + '○○'   # 별명 · 긴 이름은 앞 글자만
    return n[0] + '○' * (len(n) - 2) + n[-1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', 'data', 'talks798.json'))
    ap.add_argument('--keep-names', action='store_true')
    a = ap.parse_args()
    s = open(a.src, encoding='utf-8').read()
    i = s.find('window.NZ_TALK_CATS = '); j = s.find(';\n', i)
    cats = json.loads(s[i + len('window.NZ_TALK_CATS = '):j])
    i = s.find('window.NZ_TALKS = '); j = s.find('];', i) + 1
    src = json.loads(s[i + len('window.NZ_TALKS = '):j])
    stat = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'talks_meta.json'), encoding='utf-8'))
    rnd = random.Random(798)
    items = []
    dash = lambda v, sep=', ': v.replace(' \u2014 ', sep).replace('\u2014', sep.strip() or ',') if isinstance(v, str) else v   # 화면 글에는 긴 줄표를 쓰지 않는다
    for t in src:
        t = dict(t, short=dash(t['short']), full=dash(t['full']), point=dash(t.get('point', '')), tip=dash(t.get('tip', '')), why=dash(t.get('why', ''), ' · '), title=dash(t.get('title', '')))
        o = {
            'id': 't-%03d' % t['id'], 'cat': t['c'], 'sit': t['sit'], 'tags': t.get('tags') or [],
            'head': t['short'].strip(), 'body': t['full'].strip(), 'why': t.get('point', ''), 'tip': t.get('tip', ''),
            'author': t['name'] if a.keep_names else mask(t['name']), 'org': t.get('branch', ''),
            'grade': t.get('grade', 'C'), 'q': t.get('q', 3), 'grade_rec': bool(t.get('rec')), 'review': 'block' if t.get('lv') == 'block' else 'ok',
            'noise': bool(t.get('noise')), 'src': t.get('src', ''), 'seasonal': bool(t.get('seas')),
        }
        o['grade'] = 'rec' if t.get('rec') else 'normal'
        o['quality'] = t.get('grade', 'C')
        del o['grade_rec']
        if t.get('title'): o['title'] = t['title']
        if t.get('lv') == 'block': o['blockReason'] = t.get('why', '준법 검토 필요')
        # 공감 · 써봤어요 숫자는 화면 시연용 예시(품질 등급을 따라 결정적으로 만든다)
        base = {'S': 180, 'A': 110, 'B': 70, 'C': 40, 'D': 12}.get(o['quality'], 30)
        o['likes'] = int(base * (0.6 + rnd.random() * 0.8)); o['used'] = int(o['likes'] * (0.15 + rnd.random() * 0.35))
        items.append(o)
    out = {
        '$comment': '오늘의 화법 데이터 : 9월 필살 화법 공모 798건 전부(화법 마트 정리본, 2026-10-06). 제출자 이름은 가운데를 가렸다' + ('(실명판 · 저장소에 올리지 않는다)' if a.keep_names else '') + '. AI 정리 · 준법 검토 초안이며 오픈 전 준법 담당 부서 최종 확인 필요. likes · used 는 시연용 예시 숫자.',
        'stats': stat['stats'], 'cats': stat['cats'], 'items': items,
    }
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('OK', len(items), '건 →', a.out, '(실명)' if a.keep_names else '(이름 가림)')

if __name__ == '__main__':
    main()
