# -*- coding: utf-8 -*-
"""저장소 루트 약관 PDF 의 특약 목차(「2-153.암진단비(유사암제외)보장특별약관 …」) → terms_txt/toc.json · index.txt

분류 안 된 정보계 코드가 우리 약관에 특약으로 있는지(= 마스터 누락 의심) 대조할 때 쓴다. pdftotext 가 있어야 한다.
사용 : python3 toc.py <작업폴더>
"""
import sys, os, re, json, glob, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
work = os.path.join(sys.argv[1], 'terms_txt'); os.makedirs(work, exist_ok=True)
pdfs = sorted(glob.glob(os.path.join(ROOT, '*.pdf')))
toc = {}; idx = []
for i, f in enumerate(pdfs, 1):
    out = os.path.join(work, '%d.txt' % i)
    if not os.path.exists(out): subprocess.run(['pdftotext', '-q', f, out], check=False)
    idx.append('%d %s' % (i, os.path.basename(f)))
    lines = [re.sub(r'\s+', '', l) for l in open(out, encoding='utf-8', errors='ignore').read().split('\n')]
    tl = []
    for j, l in enumerate(lines):
        if '특별약관' in l and re.match(r'^\d+(-\d+)*\.', l): tl.append(re.sub(r'\.{3,}.*$', '', l))
        elif '특별약관' in l and j > 0 and re.match(r'^\d+(-\d+)*\.', lines[j - 1]) and '특별약관' not in lines[j - 1]:
            tl.append(re.sub(r'\.{3,}.*$', '', lines[j - 1] + l))
    toc[str(i)] = sorted(set(tl))
    print(i, os.path.basename(f), len(tl))
json.dump(toc, open(os.path.join(work, 'toc.json'), 'w', encoding='utf-8'), ensure_ascii=False)
open(os.path.join(work, 'index.txt'), 'w', encoding='utf-8').write('\n'.join(idx) + '\n')
