# -*- coding: utf-8 -*-
"""아이콘·글꼴·로고를 공개 출처에서 내려받아 assets/ 와 icons.json 을 만든다.
   사용 : python fetch_assets.py [원본_상품설명서.pdf]
   - 아이콘 : Healthicons (npm 배포본, 무료 공개)
   - 글꼴   : 나눔고딕 3종 (SIL OFL) — 사내 표준 글꼴이 있으면 그 파일로 대체 가능
   - 로고   : 원본 상품설명서 PDF에서 추출(인자를 주면 수행)"""
import glob, io, json, os, re, shutil, subprocess, sys, tarfile, urllib.request
BASE = os.path.dirname(os.path.abspath(__file__)); AS = os.path.join(BASE, 'assets')
os.makedirs(AS, exist_ok=True)
def get(url):
    return urllib.request.urlopen(url, timeout=60).read()

# 1) 글꼴
FONTS = {'NanumGothic-Regular.ttf': 'NanumGothic-Regular',
         'NanumGothic-Bold.ttf': 'NanumGothic-Bold',
         'NanumGothic-ExtraBold.ttf': 'NanumGothic-ExtraBold'}
for fn, stem in FONTS.items():
    dst = os.path.join(AS, fn)
    if os.path.exists(dst): continue
    open(dst, 'wb').write(get('https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/%s.ttf' % stem))
    print('글꼴 :', fn)

# 2) 아이콘 (healthicons npm tarball → 필요한 것만 icons.json 으로)
NEED = ['stomach','colon','lungs','breasts','thyroid','liver','kidneys','bladder','prostate_cancer',
 'cervical_cancer','blood_cells','neurology','neuro_surgery','heart_organ','heart_cardiogram','cardiogram',
 'blood_vessel','varicose_vein','stent','defibrillator','intensive_care_unit','ventilator','oxygen_tank',
 'ambulance','hospital','hospital_symbol','physical_therapy','wheelchair','syringe','pills_3','medicine_bottle',
 'microscope','xray','radiology','ultrasound_scanner','dna','test_tubes','stethoscope','money_bag','coins',
 'calendar','chart_bar','chart_line','doctor','nurse','blood_drop','blood_bag','virus_alt','cancerous_cell_nuclei',
 'cell_nuclei','biochemistry_laboratory','implant','body','head','bandage_adhesive','blood_pressure_monitor',
 'gallbladder','intestine','tooth','star_large','pill_1','surgical_sterilization','magnifying_glass',
 'i_certificate_paper','machinery','thermometer','virus-shield','cold_chain','i_note_action',
 'i_documents_accepted','i_training_class']
icons_path = os.path.join(BASE, 'icons.json')
icons = json.load(open(icons_path, encoding='utf-8')) if os.path.exists(icons_path) else {}
if not all(n in icons for n in NEED):
    meta = json.loads(get('https://registry.npmjs.org/healthicons'))
    ver = meta['dist-tags']['latest']
    tgz = get(meta['versions'][ver]['dist']['tarball'])
    tf = tarfile.open(fileobj=io.BytesIO(tgz))
    src = {}
    for m in tf.getmembers():
        if '/icons/svg/filled/' in m.name and m.name.endswith('.svg'):
            src[os.path.basename(m.name)[:-4]] = tf.extractfile(m).read().decode('utf-8')
    for n in NEED:
        if n not in src: print('  (없음)', n); continue
        s = re.sub(r'\s(width|height)="[^"]*"', '', src[n], count=2)
        icons[n] = s.replace('fill="currentColor"', 'fill="CC"').strip().replace('\n', '')
    json.dump(icons, open(icons_path, 'w', encoding='utf-8'), ensure_ascii=False)
    print('아이콘 :', len(icons), '종 (healthicons', ver, ')')

# 3) 로고 (원본 상품설명서 PDF 1쪽에서 추출)
if len(sys.argv) > 1 and not os.path.exists(os.path.join(AS, 'logo.png')):
    from PIL import Image
    tmp = os.path.join(AS, '_tmp')
    subprocess.check_call(['pdfimages', '-png', '-f', '1', '-l', '2', sys.argv[1], tmp])
    imgs = sorted(glob.glob(tmp + '*.png'))
    # 로고 = 가로로 가장 긴 이미지 + 바로 뒤의 마스크
    i = max(range(0, len(imgs) - 1, 2), key=lambda k: Image.open(imgs[k]).width)
    im = Image.open(imgs[i]).convert('RGB'); mk = Image.open(imgs[i + 1]).convert('L')
    im.putalpha(mk); im.save(os.path.join(AS, 'logo.png'))
    for f in imgs: os.remove(f)
    print('로고 : assets/logo.png', im.size)
print('완료 — assets/ 준비됨')
