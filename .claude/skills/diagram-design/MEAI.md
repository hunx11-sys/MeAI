# 도식 디자인 스킬 · MeAI 적용 안내

원본 : github.com/cathrynlavery/diagram-design (MIT · 2026-11-25 기준 v2.6.179 · 커밋 b228c5d) — 사용권은 `LICENSE` · 아이콘 사용권은 `THIRD_PARTY_LICENSES.md`.

## 무엇을 하나

「○○ 도식 그려줘」 「구조도」 「흐름도」 「플라이휠 그림」 「간트 차트」 같은 요청을 받으면, 그림 하나가 든 **HTML 파일 하나**(인터넷 없이도 열림)로 도식을 그린다. 52종(구조도 · 흐름도 · 순서도 · 타임라인 · 스윔레인 · 4분면 · 고리(플라이휠) · 피라미드/깔때기 · 막대 · 폭포 · 트리맵 · 히트맵 · 간트 · 산키 · 피시본 · 고객 여정 · 서비스 블루프린트 등)을 고르는 표는 `SKILL.md` §3.

## MeAI 에 맞춘 것

- **색 · 글꼴은 `design/DESIGN-MeAI.md` 를 따른다** — `references/style-guide.md` 맨 위 「MeAI skin」 상자. 강조색은 메리츠 빨강 `#C8102E` 하나(도식 하나에 1~2곳만), 회색은 토스 회색, 글꼴은 Pretendard(없으면 Noto Sans KR · 맑은 고딕). 원본의 영문 세리프 제목 · 기울임 주석은 쓰지 않는다.
- 다른 회사 디자인으로 그려 달라고 하면(「토스처럼」 등) `design/` 의 그 문서 값으로 바꿔 그린다(design-md 스킬).
- 한글 글씨는 12px 미만으로 줄이지 않는다 — 안 들어가면 말을 줄인다.
- 숫자 · 통계를 도식에 넣을 때는 출처나 「가정값」 을 붙인다(CLAUDE.md 절대 지키는 것 5).
- 질병코드 · 금액을 도식에 새로 지어 넣지 않는다(CLAUDE.md 1 · 2).

## 명령(빗금 명령)

원본의 `/doctor` 는 Claude Code 자체 명령과 이름이 겹쳐 모두 `diagram-` 을 앞에 붙였다.

| 명령 | 하는 일 |
|---|---|
| `/diagram-doctor` | 도식 도구가 돌 준비가 됐는지 점검(읽기만) |
| `/diagram-export <파일.html>` | 도식을 SVG · PNG · PDF 로 내보내기 |
| `/diagram-import-mermaid` · `-drawio` · `-excalidraw` · `-plantuml` | 다른 도구로 그린 도식을 이 디자인으로 다시 그리기 |
| `/diagram-profile` | 디자인 묶음(프로필) 저장 · 불러오기 |

## 점검

```
cd .claude/skills/diagram-design
python3 scripts/self_check.py <도식.html>     # 접근성 · 한 파일 · 화면 밖 글씨 · 상자 넘침
python3 scripts/verify_geometry.py <도식.html> # 선 규칙(대각선 · 겹침 · 상자 관통)
```

PNG 미리보기 `scripts/export_png.py` 는 파이썬 Playwright 가 필요하다. 이 환경에는 Node 판만 있으니 Node 로 캡처한다(`require('playwright')`).

견본 : `docs/diagrams/meai_flywheel_loop.html`(영업 플라이휠 고리 도식 · 2026-11-25 · 두 점검 통과).

## 원본을 새로 받을 때

원본 저장소의 `skills/diagram-design/` 를 이 폴더에 덮어쓰고 `commands/*.md` 를 `.claude/commands/diagram-*.md` 로 다시 넣는다(경로 `skills/diagram-design` → `.claude/skills/diagram-design`). **덮어쓴 뒤 `references/style-guide.md` 의 MeAI 색 · 글꼴과 이 파일, `SKILL.md` 맨 위 안내 줄을 다시 넣는다**(덮어쓰면 원본 기본색으로 돌아간다).
