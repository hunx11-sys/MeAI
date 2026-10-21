# 디자인 문서 보관함 (design/)

PPT · HTML · 영상 · 화면을 만들 때 참고하는 **회사별 디자인 문서**를 모아 두는 곳이다.
Claude Code 는 디자인 작업을 받으면 이 폴더를 먼저 본다(`.claude/skills/design-md/SKILL.md`).

## 올리는 방법 (소유자)
1. https://github.com/hunx11-sys/MeAI/upload/main/design 를 연다
2. claude.ai 프로젝트 「PPT x Design.md」의 파일(DESIGN-*.md · 토스 · 배달의민족 등 텍스트)을 **한꺼번에 끌어다 놓는다**
3. 아래 「Commit changes」 → 끝. 다음 작업부터 바로 쓴다

## 파일 이름 규칙
- 영문 회사 : `DESIGN-<회사>.md` (예 : `DESIGN-apple.md`)
- 한글 회사 : `DESIGN-<회사>.md` 또는 원래 이름 그대로(`토스.txt` 등) — 세션이 첫 줄 · 제목으로 회사를 알아본다
- 회사 이름 → 파일 찾기 : `ls design/` 후 이름에 회사가 들어간 파일

## 지금 있는 것
- `DESIGN-nike.md` — 나이키
