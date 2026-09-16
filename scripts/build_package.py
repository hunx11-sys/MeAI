#!/usr/bin/env python3
"""
영업지원도구 6종 내부망(폐쇄망) 배포판 만들기
- 저장소 루트에서 실행: python3 scripts/build_package.py
- 결과: dist/영업지원도구6종_폐쇄망.zip

폐쇄망 PC는 사내 랜에 붙어 있어 브라우저는 "온라인"이라고 판단하지만
바깥 인터넷은 막혀 있습니다. 그래서 바깥으로 나가는 요청이 하나라도 남아 있으면
글꼴이 안 나오거나 화면이 몇 초씩 멈춥니다. 이 스크립트는 그 요청을 전부 없앱니다.

  1) 대문(index.html) → 「영업지원도구_대문.html」로 이름 변경, 각 도구의 '🏠 대문' 링크도 맞춤
  2) 글꼴: 바깥 CDN 링크를 빼고, 같이 넣은 pretendard-subset.woff2 를 쓰도록 바꿈
  3) 사용 통계 전송(logEvent)을 끔 — 폐쇄망에서는 나가지도 않고, 보안 검토에도 걸림
  4) 대문의 '사용 통계' 링크 제거 — 통계 화면은 인터넷이 있어야 동작하므로 뺌
  5) 바깥 주소가 남았는지 마지막에 스스로 검사하고, 남아 있으면 만들다 멈춤
"""
import os, re, sys, base64, zipfile, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = '영업지원도구_대문.html'
TOOLS = ['tool.html', 'products.html', 'prompts.html', '명패생성기.html', '통합치료비.html']
ASSETS = [('gloss.js', 'gloss.js')]
FONT = os.path.join(ROOT, 'assets', 'pretendard-subset.woff2')

# 사내 메일이 첨부 안을 검사해서 막는 일이 있다. 통과했던 판과 같은 모양
# (.html · .js · .txt 만 들어 있는 압축)을 유지하려고, 글꼴을 따로 넣지 않고
# 글꼴이 필요한 쪽(통합치료비)의 CSS 안에 base64 로 심는다.
# 그래도 막히면 글꼴을 아예 빼고 맑은 고딕으로 두는 판을 쓰면 된다.
BUILDS = [('영업지원도구6종.zip', True),
          ('영업지원도구6종_기본글꼴.zip', False)]

FONT_CSS = ('<style id="offline-font">'
            '/* Pretendard (SIL OFL 1.1, (c) Kil Hyung-jin) — 파일 안에 넣어 두었습니다. '
            '인터넷이 필요 없습니다. */'
            '@font-face{{font-family:"Pretendard Variable";font-weight:45 920;font-style:normal;'
            'font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2-variations")}}'
            '</style>\n')

OFFMARK = 'return; /* 폐쇄망 배포판: 사용 통계 전송 안 함 */'

# 바깥으로 나가는 요청이 되는 것만 잡는다. (본문 속 참고 링크 <a href>는 눌러야 열리므로 제외)
OUTBOUND = re.compile(
    r'<link[^>]+href="https?://|'
    r'<script[^>]+src="https?://|'
    r'@import\s+url\(\s*[\'"]?https?://|'
    r'src\s*:\s*url\(\s*[\'"]?https?://|'
    r'fetch\(\s*[\'"]https?://', re.I)

README = """메리츠 세일즈혁신 영업지원도구 6종 — 내부망(폐쇄망) 배포판
만든 날짜: {date}

■ 설치
1. 이 압축파일을 원하는 폴더에 통째로 풉니다.
   (파일이 서로를 부르므로 반드시 같은 폴더에 두세요)
2. 「영업지원도구_대문.html」을 더블클릭하면 크롬 또는 엣지에서 대문이 열립니다.
3. 대문에서 원하는 도구를 누르고, 각 도구의 '🏠 대문' 버튼으로 돌아옵니다.
   자주 쓰시면 대문을 즐겨찾기에 넣거나 바탕화면에 바로가기를 만들어 두세요.

■ 들어 있는 도구 6종
- 특약검색 ............................. tool.html
- 보상시뮬레이터 ....................... tool.html (같은 파일의 두 번째 탭)
- 상품 라인업 · 예외질환 판정 .......... products.html
- MeAI 영업가족 프롬프트 라이브러리 .... prompts.html
- 명패 제작기 .......................... 명패생성기.html
- 통합치료비 시뮬레이터 ................ 통합치료비.html

■ 폐쇄망용으로 손본 점
- 바깥 인터넷으로 나가는 요청을 전부 없앴습니다.
  (검사 결과는 아래 '자동 검사' 항목을 보세요)
- 압축 안에는 html·js·txt 만 들어 있습니다. 글꼴도 파일이 아니라
  화면 파일 안에 심어 두어, 사내 메일 검사에 걸릴 만한 파일이 없습니다.
- 사용 통계 전송을 껐습니다. 이 배포판은 밖으로 아무것도 보내지 않습니다.
- 대문의 '사용 통계' 링크를 뺐습니다. 통계 화면은 인터넷이 있어야 동작합니다.
- 이모지는 윈도우 기본 이모지로 나옵니다. (토스 전용 이모지는 인터넷이 필요해 뺐습니다)

■ 알아두기
- 약관 본문·분류표·상품 데이터는 모두 파일 안에 들어 있어 인터넷 없이 동작합니다.
- 약관 본문의 보험용어에 점선 밑줄이 있습니다.
  PC는 마우스를 올리면, 휴대폰은 누르면 쉬운 설명이 나옵니다. (용어 {gloss}개)
- 즐겨찾기·최근 본 특약은 그 PC의 브라우저에만 저장됩니다.
  다른 PC로 옮기거나 브라우저 기록을 지우면 사라집니다.
- 본문 속 약관 원문 링크(식약처·심평원)는 인터넷이 있어야 열립니다.
  폐쇄망에서는 눌러도 열리지 않으며, 그 외 기능에는 영향이 없습니다.
- 인터넷 익스플로러(IE)에서는 동작하지 않습니다. 크롬 또는 엣지를 쓰세요.

■ 자동 검사
{report}

문의: 세일즈혁신TF 이헌수
"""


def offline(name, s, log, font_b64=None):
    """한 파일을 폐쇄망용으로 손본다"""
    # 1) 바깥 글꼴 CDN 링크 제거
    n = 0
    for pat in (r'[ \t]*<link[^>]+href="https?://cdn\.jsdelivr\.net[^"]*"[^>]*>\n?',
                r'[ \t]*<link[^>]+rel="preconnect"[^>]*href="https?://[^"]*"[^>]*>\n?'):
        s, k = re.subn(pat, '', s)
        n += k
    if n:
        log.append(f'  글꼴 CDN 링크 {n}개 제거')

    # 2) 글꼴을 쓰도록 만든 쪽에만 @font-face 를 심는다.
    #    닫는 </head> 뒤가 아니라 여는 <head> 바로 뒤에 넣는다.
    #    명패생성기에 들어 있는 엑셀 라이브러리가 자바스크립트 문자열 안에
    #    "</head>" 를 갖고 있어, 닫는 쪽을 기준으로 잡으면 그 문자열이 깨진다.
    if font_b64 and 'Pretendard Variable' in s:
        m = re.search(r'<head[^>]*>', s)
        if not m or m.start() > 400:
            sys.exit(f'{name}: 문서 맨 앞에서 <head> 를 찾지 못했습니다')
        s = s[:m.end()] + '\n' + FONT_CSS.format(b64=font_b64) + s[m.end():]
        log.append(f'  글꼴을 파일 안에 심음 ({len(font_b64)//1024:,}KB)')

    # 3) 사용 통계 전송 끄기 (정의가 여러 개면 전부)
    k = len(re.findall(r'function logEvent\s*\([^)]*\)\s*\{', s))
    if k:
        s = re.sub(r'(function logEvent\s*\([^)]*\)\s*\{)', r'\1 ' + OFFMARK, s)
        log.append(f'  사용 통계 전송 끔 ({k}곳)')

    # 4) 대문 링크 이름 맞추기
    k = s.count('href="index.html"')
    if k:
        s = s.replace('href="index.html"', f'href="{HOME}"')
        log.append(f'  대문 링크 {k}곳 교체')

    # 5) 통계 화면 링크 제거 (대문에만 있음)
    s, k = re.subn(r'<br><a href="stats\.html"[^>]*>[^<]*</a>', '', s)
    if k:
        log.append('  사용 통계 링크 제거')

    # 6) 보상시뮬레이터는 tool.html 안에 base64 로 통째로 들어 있다.
    #    글자 그대로 치환하면 닿지 않으므로, 풀어서 같은 손질을 하고 다시 넣는다.
    m = re.search(r'(<script id="SIMSRC"[^>]*>)(.*?)(</script>)', s, re.S)
    if m:
        inner = base64.b64decode(m.group(2).strip()).decode('utf-8')
        sub = []
        inner = offline('SIMSRC(보상시뮬레이터)', inner, sub, font_b64)
        for line in sub:
            log.append('  └' + line)
        enc = base64.b64encode(inner.encode('utf-8')).decode('ascii')
        s = s[:m.start(2)] + enc + s[m.end(2):]
        globals().setdefault('_INNER', {})['SIMSRC'] = inner   # 검사용
    return s


def build(outname, with_font):
    """압축 하나를 만든다. with_font 가 False 면 글꼴을 빼고 맑은 고딕에 맡긴다."""
    out = os.path.join(ROOT, 'dist', outname)
    font_b64 = None
    if with_font:
        font_b64 = base64.b64encode(open(FONT, 'rb').read()).decode('ascii')

    gloss = open(os.path.join(ROOT, 'gloss.js'), encoding='utf-8').read()
    gloss_n = gloss.count('":{"d":"') or gloss.count('"d":')

    print(f'\n■ {outname}')
    pages, leftovers, fonted = {}, [], []
    for src, name in [('index.html', HOME)] + [(t, t) for t in TOOLS]:
        log = []
        s = offline(name, open(os.path.join(ROOT, src), encoding='utf-8').read(),
                    log, font_b64)
        print(f'  {name}')
        for line in log:
            print('  ' + line)
            if '심음' in line:
                fonted.append(name)
        for who, text in [(name, s)] + [(f'{name} 안의 {k}', v)
                                        for k, v in globals().get('_INNER', {}).items()]:
            hits = sorted({m.group(0)[:48] for m in OUTBOUND.finditer(text)})
            # 통계 전송 함수가 하나라도 살아 있으면 안 된다
            defs = len(re.findall(r'function logEvent\s*\([^)]*\)\s*\{', text))
            if defs != text.count(OFFMARK):
                hits.append(f'사용 통계 전송 함수 {defs}개 중 일부가 살아 있음')
            if 'cdn.jsdelivr.net' in text:
                hits.append('cdn.jsdelivr.net 참조가 남아 있음')
            if hits:
                leftovers.append((who, hits))
        globals().pop('_INNER', None)
        pages[name] = s

    if leftovers:
        print('\n  바깥으로 나가는 요청이 남아 있습니다 — 만들다 멈춥니다')
        for name, hits in leftovers:
            for h in hits:
                print(f'    {name}: {h}')
        sys.exit(1)

    font_line = ('- 글꼴: Pretendard 를 파일 안에 심었습니다 '
                 f'({", ".join(fonted)}). 인터넷이 필요 없습니다.\n'
                 '  Pretendard (c) Kil Hyung-jin, SIL Open Font License 1.1'
                 if fonted else
                 '- 글꼴: 윈도우 기본 글꼴(맑은 고딕)로 나옵니다. 따로 넣은 글꼴이 없습니다.')
    report = (f'- 바깥으로 나가는 요청: 0건\n'
              f'  (HTML {len(pages)}개 + tool.html 안에 들어 있는 보상시뮬레이터까지 검사)\n'
              f'- 사용 통계 전송 함수: 전부 꺼짐 (남아 있는 주소는 호출되지 않는 문자열)\n'
              f'{font_line}')

    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, text in pages.items():
            z.writestr(name, text)
        for src, name in ASSETS:
            z.write(os.path.join(ROOT, src), name)
        z.writestr('사용법.txt', README.format(
            date=datetime.date.today().isoformat(), gloss=gloss_n, report=report))

    # 사내 메일 검사를 생각해, 들어 있는 파일 종류를 확인해 둔다
    with zipfile.ZipFile(out) as z:
        kinds = sorted({os.path.splitext(n)[1] or '(없음)' for n in z.namelist()})
    print(f'  -> dist/{outname}  {os.path.getsize(out)/1024/1024:.1f} MB '
          f'· 파일 종류 {" ".join(kinds)}')
    return out


def main():
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    for outname, with_font in BUILDS:
        build(outname, with_font)


if __name__ == '__main__':
    main()
