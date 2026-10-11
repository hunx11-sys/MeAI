#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""가이드 JSON 번역 도구.

   추출 : python3 -I travel/tools/i18n.py extract <guide.json> <strings.json>
           → 번역할 한국어 문자열만 {"경로": "글"} 로 뽑는다(아이디·좌표·시각·URL·일본어 이름은 뺀다. 한글이 없는 글도 뺀다)
   검사 : python3 -I travel/tools/i18n.py check <strings.json> <translated.json> <언어코드>
           → 경로가 빠졌거나 비었거나, 한글이 남아 있거나, 줄표(—)가 있으면 알려 준다. 문제 없으면 OK
   적용 : python3 -I travel/tools/i18n.py apply <guide.json> <translated.json> <out.json>
           → 번역을 끼워 넣은 사본을 만든다(없는 경로는 한국어 그대로)
   공항 자료(jp_airports.json)도 같은 명령으로 다룬다(weekly·season_note·notes·city_access 만 뽑힌다)."""
import json, re, sys

# 번역 대상 필드(이 이름의 문자열 값만 뽑는다)
FIELDS = {'name', 'area', 'tagline', 'intro', 'season_notes', 'getting_around', 'transport_pass', 'mode', 'to', 'note', 'desc', 'access',
          'hours', 'closed', 'tip', 'kid_tip', 'cuisine', 'signature', 'tips', 'pts', 'title', 'theme', 'summary', 'label', 'kicker', 't_notice',
          'text', 'per', 'basis', 'checks', 'reason', 'when_text', 'highlights', 'weekly', 'season_note', 'notes'}
SKIP = {'id', 'key', 'name_ja', 'name_en', 'maps_q', 'sources', 'source_url', 'iata', 'from_iata', 'airports', 'airlines', 'cat', 'tier', 'when',
        'tags', 'region', 'prefecture', 'generated', 'status', 'confidence', 'source_date', 'reviewed', 'name_ko', 'city_ko', 'prefecture_ko', 'region_key'}
HANGUL = re.compile('[가-힣]')


def walk(obj, path, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP:
                continue
            p = f'{path}/{k}' if path else k
            if k == 'notice' and isinstance(v, dict):
                if isinstance(v.get('t'), str) and HANGUL.search(v['t']):
                    out[p + '/t'] = v['t']
                continue
            if isinstance(v, str):
                if k in FIELDS and HANGUL.search(v):
                    out[p] = v
            else:
                walk(v, p, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f'{path}/{i}'
            if isinstance(v, str):
                if path.split('/')[-1] in FIELDS and HANGUL.search(v):
                    out[p] = v
            else:
                walk(v, p, out)


def set_path(obj, path, value):
    parts = path.split('/')
    cur = obj
    for part in parts[:-1]:
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    last = parts[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    cmd = sys.argv[1]
    if cmd == 'extract':
        g = json.load(open(sys.argv[2], encoding='utf-8'))
        out = {}
        walk(g, '', out)
        json.dump(out, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('추출 %d개 → %s' % (len(out), sys.argv[3]))
    elif cmd == 'check':
        src = json.load(open(sys.argv[2], encoding='utf-8'))
        tr = json.load(open(sys.argv[3], encoding='utf-8'))
        lang = sys.argv[4] if len(sys.argv) > 4 else 'en'
        errs = []
        for k, v in src.items():
            t = tr.get(k)
            if t is None:
                errs.append('빠짐: %s' % k); continue
            if not isinstance(t, str) or not t.strip():
                errs.append('비었음: %s' % k); continue
            if lang != 'ko' and HANGUL.search(t):
                errs.append('한글 남음: %s = %s' % (k, t[:40]))
            if '—' in t:
                errs.append('줄표(—): %s' % k)
        extra = [k for k in tr if k not in src]
        if extra:
            errs.append('원본에 없는 경로 %d개 (예: %s)' % (len(extra), extra[:3]))
        for e in errs[:200]:
            print('오류:', e)
        if errs:
            print('오류 %d건' % len(errs)); sys.exit(1)
        print('OK (%d개)' % len(src))
    elif cmd == 'apply':
        g = json.load(open(sys.argv[2], encoding='utf-8'))
        tr = json.load(open(sys.argv[3], encoding='utf-8'))
        n = 0
        for k, v in tr.items():
            if isinstance(v, str) and v.strip():
                try:
                    set_path(g, k, v); n += 1
                except Exception:
                    print('경로 없음:', k)
        json.dump(g, open(sys.argv[4], 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('적용 %d개 → %s' % (n, sys.argv[4]))
    else:
        print(__doc__); sys.exit(2)


if __name__ == '__main__':
    main()
