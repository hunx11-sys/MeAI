#!/usr/bin/env python3
"""
메일 첨부가 막힐 때 쓰는 대체 파일 만들기
- 저장소 루트에서 실행: python3 scripts/build_mail.py
- 먼저 build_package.py 를 돌려 dist/영업지원도구6종_폐쇄망.zip 이 있어야 합니다.
- 결과: dist/메일발송용/ 안에 세 가지

사내 메일이 첨부를 막는 방식은 보통 둘 중 하나입니다.
  ① 확장자로 막는다  (zip·html·js 는 무조건 거른다)
  ② 압축을 풀어 안을 검사한다  (안에 html 이 있으면 거른다)
①에는 '확장자를 바꾼 파일'이, ②에는 '암호를 건 압축'이 통합니다.
어느 쪽인지 모르니 둘 다 만들어 두고, 되는 것을 쓰면 됩니다.
"""
import os, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'dist', '영업지원도구6종_폐쇄망.zip')
OUTDIR = os.path.join(ROOT, 'dist', '메일발송용')
EXT = 'meai'                 # 어떤 메일에서도 막지 않는, 흔하지 않은 확장자
PW = 'meritz2026'            # 검사기를 피하려는 용도일 뿐, 보안용 암호가 아닙니다

RENAMED = os.path.join(OUTDIR, f'영업지원도구6종.{EXT}')
LOCKED = os.path.join(OUTDIR, '영업지원도구6종_암호.zip')

BODY = """[메일 본문 예시 — 그대로 복사해서 쓰세요]

제목: [세일즈혁신TF] 영업지원도구 6종 — 내부망 PC용 (설치 불필요)

안녕하세요. 세일즈혁신TF 이헌수입니다.
영업지원도구 6종(특약검색 · 보상시뮬레이터 · 상품 라인업 · 프롬프트 라이브러리 ·
명패 제작기 · 통합치료비 시뮬레이터)을 내부망 PC에서 바로 쓰실 수 있도록
한 묶음으로 보내 드립니다. 설치 없이 파일만 열면 됩니다.

■ 쓰는 법 (3단계)
1. 첨부파일을 바탕화면에 내려받습니다.
2. 파일 이름 끝을 「.{ext}」에서 「.zip」으로 바꿉니다.
   (파일에 오른쪽 클릭 → 이름 바꾸기 → 맨 뒤 {ext} 를 지우고 zip 입력 → Enter)
   "확장자를 바꾸면 사용할 수 없게 될 수도 있습니다" 라고 물으면 [예] 를 누르세요.
3. 그 파일에 오른쪽 클릭 → 압축 풀기 → 나온 폴더에서
   「영업지원도구_대문.html」을 두 번 누르면 열립니다.

■ 알아두실 점
- 인터넷 없이 동작합니다. 회사 밖으로 나가는 통신은 하나도 없습니다.
- 인터넷 익스플로러에서는 열리지 않습니다. 크롬 또는 엣지로 열어 주세요.
- 푼 파일들은 반드시 한 폴더에 같이 두셔야 합니다. (서로를 부릅니다)
- 자주 쓰시면 「영업지원도구_대문.html」을 즐겨찾기에 넣어 두세요.

문의 주시면 도와 드리겠습니다. 감사합니다.


[위 방법이 막히면 — 암호 걸린 압축본을 대신 보내세요]

제목: [세일즈혁신TF] 영업지원도구 6종 — 내부망 PC용 (암호: 본문 참조)

첨부한 「영업지원도구6종_암호.zip」을 내려받아 압축을 풀어 주세요.
암호는 {pw} 입니다.
압축이 풀리면 「영업지원도구_대문.html」을 두 번 누르면 됩니다.
(윈도우 기본 압축 기능으로는 암호 압축이 안 풀립니다.
 알집·반디집·7-Zip 중 아무거나로 풀어 주세요.)
"""

HOWTO = """메일 첨부가 막힐 때 — 보내는 분용 안내

사내 메일이 첨부를 막는 방식은 보통 둘 중 하나입니다.
어느 쪽인지 모르니 두 가지를 다 만들어 두었습니다. 위에서부터 하나씩 시도해 보세요.

──────────────────────────────────────────────
1순위  영업지원도구6종.{ext}
──────────────────────────────────────────────
  압축파일의 확장자만 바꾼 것입니다. 내용은 그대로입니다.
  'zip 은 안 된다'처럼 확장자로 막는 메일은 이걸로 통과합니다.
  받는 분이 이름 끝을 .zip 으로 바꾼 뒤 압축을 풀면 됩니다.
  → 받는 분께 보낼 안내문은 「메일본문.txt」에 그대로 적어 두었습니다.

──────────────────────────────────────────────
2순위  영업지원도구6종_암호.zip     (암호: {pw})
──────────────────────────────────────────────
  압축 안에 든 파일 하나하나에 암호를 걸었습니다.
  메일 검사기가 압축을 풀어 안을 들여다보는 방식이면 이걸로 통과합니다.
  (검사기가 열 수 없으니 그냥 지나갑니다)
  받는 분은 알집·반디집·7-Zip 으로 풀면서 암호를 넣으면 됩니다.
  윈도우 기본 압축 기능으로는 안 풀리니, 본문에 꼭 적어 주세요.
  ※ 암호는 검사기를 피하려는 용도일 뿐 보안 장치가 아닙니다.
     본문에 그대로 적어 보내셔도 됩니다.

──────────────────────────────────────────────
둘 다 막히면
──────────────────────────────────────────────
  '압축파일 자체를 막는' 메일입니다. 이때는 메일로는 방법이 없습니다.
  사내 그룹웨어 자료실이나 부서 공용 폴더에 올리고
  링크나 경로만 메일로 보내는 방법을 담당 부서에 요청해 보세요.
  급하시면 USB 로 전달하고, 받으신 분이 폴더째 복사해 쓰셔도 됩니다.

두 파일의 내용물은 완전히 같습니다. {n}개 파일 · 원본 {size}
"""


def mark_utf8(path):
    """압축 안의 한글 파일 이름이 윈도우에서 깨지지 않게 표시를 달아 준다.

    zip 명령은 이름을 UTF-8 로 넣으면서도 'UTF-8 입니다' 표시(0x800)를 달지 않는다.
    그러면 알집·반디집이 한글 코드(CP949)로 잘못 읽어 이름이 깨진다.
    지역 헤더와 목록 양쪽의 표시를 켜 준다.
    """
    with zipfile.ZipFile(path) as z:
        locals_ = [i.header_offset for i in z.infolist()]
        count = len(locals_)
    b = bytearray(open(path, 'rb').read())

    def turn_on(pos):
        f = int.from_bytes(b[pos:pos + 2], 'little')
        b[pos:pos + 2] = (f | 0x800).to_bytes(2, 'little')

    for off in locals_:
        assert b[off:off + 4] == b'PK\x03\x04', '지역 헤더를 찾지 못했습니다'
        turn_on(off + 6)

    eocd = b.rfind(b'PK\x05\x06')
    assert eocd > 0, '압축 목록 끝을 찾지 못했습니다'
    cd = int.from_bytes(b[eocd + 16:eocd + 20], 'little')
    for _ in range(count):
        assert b[cd:cd + 4] == b'PK\x01\x02', '압축 목록을 찾지 못했습니다'
        turn_on(cd + 8)
        n = int.from_bytes(b[cd + 28:cd + 30], 'little')
        e = int.from_bytes(b[cd + 30:cd + 32], 'little')
        c = int.from_bytes(b[cd + 32:cd + 34], 'little')
        cd += 46 + n + e + c
    open(path, 'wb').write(b)


def main():
    if not os.path.exists(SRC):
        sys.exit('dist/영업지원도구6종_폐쇄망.zip 이 없습니다. '
                 '먼저 python3 scripts/build_package.py 를 실행하세요.')
    shutil.rmtree(OUTDIR, ignore_errors=True)
    os.makedirs(OUTDIR)

    with zipfile.ZipFile(SRC) as z:
        names = z.namelist()

    # 1순위 — 확장자만 바꾼 같은 파일
    shutil.copy2(SRC, RENAMED)
    print(f'{os.path.basename(RENAMED)}  (원본과 같은 파일, 확장자만 {EXT})')

    # 2순위 — 파일마다 암호를 건 압축
    tmp = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(SRC) as z:
            z.extractall(tmp)
        # '.' 로 넣으면 이름이 './파일' 이 되어 압축 푼 모양이 달라진다. 이름을 그대로 나열한다.
        r = subprocess.run(['zip', '-q', '-9', '-e', '-P', PW, LOCKED] + names,
                           cwd=tmp, capture_output=True, text=True)
        if r.returncode:
            sys.exit('암호 압축 실패: ' + (r.stderr or r.stdout))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    mark_utf8(LOCKED)

    # 암호가 실제로 걸렸는지 확인
    with zipfile.ZipFile(LOCKED) as z:
        enc = [i.filename for i in z.infolist() if i.flag_bits & 0x1]
        if len(enc) != len(z.infolist()):
            sys.exit('암호가 걸리지 않은 파일이 있습니다')
        z.setpassword(PW.encode())
        z.read('사용법.txt')          # 암호로 실제로 열리는지 확인
    print(f'{os.path.basename(LOCKED)}  (파일 {len(enc)}개 전부 암호 걸림 · 암호 {PW})')

    size = f'{os.path.getsize(SRC)/1024/1024:.1f}MB'
    open(os.path.join(OUTDIR, '메일본문.txt'), 'w', encoding='utf-8').write(
        BODY.format(ext=EXT, pw=PW))
    open(os.path.join(OUTDIR, '보내는분_읽어주세요.txt'), 'w', encoding='utf-8').write(
        HOWTO.format(ext=EXT, pw=PW, n=len(names), size=size))
    print('메일본문.txt · 보내는분_읽어주세요.txt  (복사해서 쓰실 안내문)')

    for f in sorted(os.listdir(OUTDIR)):
        p = os.path.join(OUTDIR, f)
        print(f'  {f:34} {os.path.getsize(p)/1024/1024:5.1f} MB')


if __name__ == '__main__':
    main()
