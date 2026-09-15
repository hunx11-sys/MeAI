#!/usr/bin/env python3
"""
영업지원도구 6종 오프라인 배포판 만들기
- 저장소 루트에서 실행: python3 scripts/build_package.py
- 결과: dist/영업지원도구6종.zip
- 대문(index.html)은 「영업지원도구_대문.html」로 이름을 바꾸고, 각 도구의 '🏠 대문' 링크도 그 이름으로 맞춘다.
- 인터넷 없는 사내망 PC에서 압축만 풀면 대문 → 6종 도구가 파일 링크로 열린다.
"""
import os, sys, zipfile, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = '영업지원도구_대문.html'
TOOLS = ['tool.html', 'products.html', 'prompts.html', '명패생성기.html', '통합치료비.html']
OUT = os.path.join(ROOT, 'dist', '영업지원도구6종.zip')

README = f"""메리츠 세일즈혁신 영업지원도구 6종 (오프라인 배포판)
만든 날짜: {datetime.date.today().isoformat()}

■ 사용법
1. 이 압축파일을 원하는 폴더에 풉니다. (파일 6개가 같은 폴더에 있어야 합니다)
2. 「영업지원도구_대문.html」을 더블클릭하면 크롬/엣지에서 대문이 열립니다.
3. 대문에서 원하는 도구를 누르면 됩니다. 각 도구의 '🏠 대문' 버튼으로 돌아옵니다.

■ 들어 있는 도구
- 특약검색 / 보상시뮬레이터 ......... tool.html (한 파일에 탭 2개)
- 상품 라인업 ........................... products.html
- MeAI 영업가족 프롬프트 라이브러리 ..... prompts.html
- 명패 제작기 ........................... 명패생성기.html
- 통합치료비 시뮬레이터 ................. 통합치료비.html

■ 알아두기
- 인터넷이 없어도 모든 기능이 동작합니다. (약관 본문·분류표는 파일 안에 들어 있습니다)
- 통합치료비 화면의 전용 글꼴만 인터넷이 있을 때 적용되고, 없으면 맑은 고딕으로 표시됩니다.
- 약관 원문 링크(식약처·심평원)는 인터넷이 있어야 열립니다.
- 즐겨찾기·최근 본 특약은 이 PC의 브라우저에만 저장됩니다.
- 사용 통계 전송은 인터넷이 없으면 자동으로 건너뜁니다.
"""

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
        z.writestr(HOME, home)
        for f in TOOLS:
            s = open(os.path.join(ROOT, f), encoding='utf-8').read()
            n = s.count('href="index.html"')
            s = s.replace('href="index.html"', f'href="{HOME}"')
            print(f'{f}: 대문 링크 {n}곳 교체')
            z.writestr(f, s)
        z.writestr('사용법.txt', README)
    print('->', os.path.relpath(OUT, ROOT), f'{os.path.getsize(OUT)/1024/1024:.1f} MB')

if __name__ == '__main__':
    main()
