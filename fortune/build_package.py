"""오늘의 운세 v2 · 사내 웹서버 · 폐쇄망 탑재 패키지를 만든다 → ../dist/unse_v2_package.zip

zip 안 (모든 파일 이름은 ASCII · 윈도우 압축 풀기에서 깨지지 않게)
  unse_v2_package/
    README.md                 탑재 가이드 (docs/README_INSTALL.md)
    BLUEPRINT.md · .html · .pdf  개발 설계도 (docs/BLUEPRINT.*)
    SOURCE_ALL.md             web/ 텍스트 파일 원문 전체 (자동 생성)
    MANIFEST.txt              모든 파일 크기 · SHA-256 (자동 생성)
    web/                      서버에 올릴 폴더 (build_unse.py --web)
    unse_web.zip              web/ 압축본 (zip 안 폴더 이름 unse/)
    single/unse_saju_tarot.html  한 파일판
    server_config/            IIS · 톰캣 · nginx · 아파치 설정 예시
    tools/                    검증 도구 (verify_saju.py · csp_test_server.py · check_web.js · ref/)
    source/                   개발 원본 (fortune/ 폴더)
    LICENSES/                 글꼴 OFL · 타로 그림 출처

쓰는 법 : python3 fortune/build_package.py
설계도 HTML · PDF 는 미리 만들어 둔다 : node fortune/tools/render_doc.js fortune/docs/BLUEPRINT.md <marked> <mermaid>
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
OUT = os.path.join(ROOT, 'dist', 'unse_v2_package.zip')
NAME = 'unse_v2_package'
SKIP = {'__pycache__', '.DS_Store'}

ROLES = {
    'index.html': '화면 뼈대 (대문 · 사주 · 타로 3화면 + 카드 크게 보기 창)',
    'css/unse.css': '모든 디자인 · 애니메이션 · 인쇄(PDF) · 글꼴 선언',
    'js/ie-check.js': '익스플로러 → 엣지 안내',
    'js/fortune-text.js': '사주 운세 문구 표 (v1 과 같음)',
    'js/saju-engine.js': '사주 계산 엔진 (v1 과 같음)',
    'js/tarot-data.js': '타로 78장 데이터 (v1 과 같음)',
    'js/tarot-img.js': '카드 그림 주소 78개',
    'js/app.js': '화면 이동 · 사주 화면 · 타로 연출 · 크게 보기 · 저장/공유',
    'img/card-back.svg': '타로 카드 뒷면',
    'img/hanji.svg': '사주 화면 한지 결 무늬',
    'img/zoom.svg': '크게 보기 돋보기',
}
TAROT_NOTE = """타로 카드 그림 (web/img/tarot/00~77.webp, 한 파일판 안의 같은 그림)

출처 : 라이더-웨이트-스미스 타로 1909년 원판
       기획 Arthur Edward Waite · 그림 Pamela Colman Smith (1878~1951)
       스미스 사후 70년이 지나 공개 저작물(public domain)이다.
받은 곳 : npm 꾸러미 @cometpisces/tarot-kit-images@0.2.0 (1909년 원판 색 스캔, 300x527 PNG)
손질 : fortune/tools/prep_tarot.py (테두리 · 영문 제목띠 자르기, 286x484, 채도 +8% · 대비 +4%, WebP)
쓰지 않는 것 : 1971년 U.S. Games 재채색판 (카드 아래 저작권 표시가 있는 판)
결정 : 「죽음」 · 「소드 10」 · 맨몸 인물 카드도 원판 그대로 쓴다 (소유자 2026-10-29)

카드 뒷면 · 일월오봉 · 달 문장 · 한지 무늬 : 세일즈혁신TF 가 직접 그린 SVG
"""


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def copytree(src, dst):
    shutil.copytree(src, dst, ignore=lambda d, names: [n for n in names if n in SKIP])


def files_under(d):
    out = []
    for root, dirs, names in os.walk(d):
        dirs[:] = sorted(x for x in dirs if x not in SKIP)
        for n in sorted(names):
            if n not in SKIP:
                out.append(os.path.relpath(os.path.join(root, n), d).replace(os.sep, '/'))
    return out


def zip_dir(src, dst, arc_root):
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in files_under(src):
            z.write(os.path.join(src, rel), arc_root + '/' + rel)


def source_all(web):
    rows, body, bins = [], [], []
    for rel in files_under(web):
        p = os.path.join(web, rel)
        size = os.path.getsize(p)
        if rel.endswith(('.html', '.css', '.js', '.svg')):
            text = open(p, encoding='utf-8').read()
            rows.append('| `%s` | %d | %s B | %s |' % (rel, text.count('\n') + (0 if text.endswith('\n') else 1), format(size, ','), ROLES.get(rel, '')))
            lang = {'html': 'html', 'css': 'css', 'js': 'js', 'svg': 'xml'}[rel.rsplit('.', 1)[1]]
            body.append('## %s\n\n````%s\n%s%s````\n' % (rel, lang, text, '' if text.endswith('\n') else '\n'))
        else:
            bins.append('| `%s` | %s B | `%s` |' % (rel, format(size, ','), sha(p)))
    return ('---\ndate: 2026-10-29\ntags: [오늘의운세, 소스코드, 웹탑재]\nversion: v2\n---\n\n# 오늘의 운세 v2 · 소스코드 전체\n\n'
            '> 이 문서는 `build_package.py` 가 `web/` 폴더 파일을 그대로 묶어 자동으로 만든 것입니다. 직접 고치지 말고 원본(`source/src`)을 고친 뒤 다시 빌드하세요.\n'
            '> 구조와 동작 설명은 `BLUEPRINT.md`, 탑재 방법은 `README.md` 를 보세요.\n\n'
            '| 파일 | 줄 수 | 크기 | 역할 |\n|---|---:|---:|---|\n' + '\n'.join(rows) + '\n\n'
            '그림 · 글꼴 파일 (원문 대신 크기와 SHA-256)\n\n| 파일 | 크기 | SHA-256 |\n|---|---:|---|\n' + '\n'.join(bins) + '\n\n' + '\n'.join(body))


def main():
    for f in ('BLUEPRINT.html', 'BLUEPRINT.pdf'):
        if not os.path.exists(os.path.join(HERE, 'docs', f)):
            sys.exit('docs/%s 가 없어요 · render_doc.js 로 먼저 만드세요' % f)
    subprocess.run([sys.executable, os.path.join(HERE, 'build_unse.py')], check=True)
    with tempfile.TemporaryDirectory() as t:
        pkg = os.path.join(t, NAME)
        os.makedirs(pkg)
        subprocess.run([sys.executable, os.path.join(HERE, 'build_unse.py'), '--web', os.path.join(pkg, 'web')], check=True)
        zip_dir(os.path.join(pkg, 'web'), os.path.join(pkg, 'unse_web.zip'), 'unse')
        os.makedirs(os.path.join(pkg, 'single'))
        shutil.copy(os.path.join(ROOT, 'dist', 'unse_saju_tarot.html'), os.path.join(pkg, 'single'))
        shutil.copy(os.path.join(HERE, 'docs', 'README_INSTALL.md'), os.path.join(pkg, 'README.md'))
        for f in ('BLUEPRINT.md', 'BLUEPRINT.html', 'BLUEPRINT.pdf'):
            shutil.copy(os.path.join(HERE, 'docs', f), pkg)
        copytree(os.path.join(HERE, 'docs', 'server_config'), os.path.join(pkg, 'server_config'))
        os.makedirs(os.path.join(pkg, 'tools'))
        for f in ('verify_saju.py', 'csp_test_server.py', 'check_web.js'):
            shutil.copy(os.path.join(HERE, 'tools', f), os.path.join(pkg, 'tools'))
        copytree(os.path.join(HERE, 'tools', 'ref'), os.path.join(pkg, 'tools', 'ref'))
        copytree(HERE, os.path.join(pkg, 'source'))
        os.makedirs(os.path.join(pkg, 'LICENSES'))
        shutil.copy(os.path.join(HERE, 'assets', 'fonts', 'OFL.txt'), os.path.join(pkg, 'LICENSES', 'FONTS_OFL.txt'))
        open(os.path.join(pkg, 'LICENSES', 'TAROT_IMAGES.txt'), 'w', encoding='utf-8').write(TAROT_NOTE)
        open(os.path.join(pkg, 'SOURCE_ALL.md'), 'w', encoding='utf-8').write(source_all(os.path.join(pkg, 'web')))
        names = files_under(pkg)
        bad = [n for n in names if not n.isascii()]
        if bad:
            sys.exit('ASCII 가 아닌 파일 이름 : %s' % bad[:5])
        lines = ['오늘의 운세 v2 패키지 파일 목록 · 크기(바이트) · SHA-256', '확인 : 윈도우 certutil -hashfile <파일> SHA256 / 맥 · 리눅스 shasum -a 256 <파일>', '']
        total = 0
        for n in names:
            p = os.path.join(pkg, n)
            total += os.path.getsize(p)
            lines.append('%s  %10d  %s' % (sha(p), os.path.getsize(p), n))
        lines += ['', '파일 %d개 · 합계 %s 바이트' % (len(names), format(total, ','))]
        open(os.path.join(pkg, 'MANIFEST.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        zip_dir(pkg, OUT, NAME)
        print('%s  %.1fMB · 파일 %d개 (MANIFEST 포함)' % (os.path.relpath(OUT), os.path.getsize(OUT) / 1048576, len(names) + 1))


if __name__ == '__main__':
    main()
