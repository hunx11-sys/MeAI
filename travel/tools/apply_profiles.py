#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""도시 프로필(한눈에 보는 얼굴)을 가이드 파일에 넣는다.

   사용 : python3 -I travel/tools/apply_profiles.py <profiles.json> [가이드 폴더(기본 travel/data/guides)]

   profiles.json = { "<key>": { "vibe", "where", "known_for": [{"k":"eat|see|do","t" 또는 "text"}],
                               "best_for", "vs", "vs_key", "aliases", "color" }, ... }
   가이드 파일마다 "profile" 항목으로 저장한다(번역 도구가 vibe·where·vs·known_for 글을 함께 뽑는다).
   넣은 뒤 validate_guide.py 로 다시 점검한다."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF = os.path.join(os.path.dirname(HERE), 'data', 'guides')
ORDER = ('vibe', 'where', 'known_for', 'best_for', 'vs', 'vs_key', 'aliases', 'color')


def clean(p):
    out = {}
    for k in ORDER:
        if k not in p:
            continue
        v = p[k]
        if k == 'known_for':
            v = [{'k': x.get('k'), 'text': x.get('text', x.get('t', ''))} for x in v]
        if isinstance(v, str):
            v = v.strip().replace('—', ', ')
        out[k] = v
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    prof = json.load(open(sys.argv[1], encoding='utf-8'))
    folder = sys.argv[2] if len(sys.argv) > 2 else DEF
    done, missing = [], []
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.json') or f.startswith('_'):
            continue
        path = os.path.join(folder, f)
        g = json.load(open(path, encoding='utf-8'))
        p = prof.get(g.get('key'))
        if not p:
            missing.append(g.get('key'))
            continue
        g['profile'] = clean(p)
        open(path, 'w', encoding='utf-8').write(json.dumps(g, ensure_ascii=False, indent=1))
        done.append(g['key'])
    print('프로필 넣음 %d곳%s' % (len(done), ('  · 프로필 없음: %s' % ', '.join(missing)) if missing else ''))


if __name__ == '__main__':
    main()
