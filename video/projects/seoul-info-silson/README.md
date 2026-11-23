# 서울중앙본부 정보미팅 교육 영상 : 「초기 실손 고객, 두 가지 할인 제도 한눈에」

- 원본 자료 : 메리츠 스탠다드 세일즈북 「실손 계약전환 할인 · 선택형 할인특약 Q&A」 6쪽(소유자가 2026-11-22 채팅으로 준 PDF · 원본 PDF 는 저장소에 넣지 않음)
- 출처 표기 : 금융위·금감원 「실손 계약전환 할인·선택형 할인특약 제도 관련 Q&A」(2026.11) 참조
- 사내 교육용입니다. 외부 배포·게시 금지(화면 아래 띠에도 적혀 있음). 내레이션은 AI 음성이라고 표기함.

## 판

| 판 | 날짜 | 내용 |
|---|---|---|
| v1 | 2026-11-22 | 4분 53초 · 장면 11개 · 남성 7번 목소리(1.1배) · 자막 · 배경음 |
| v2 | 2026-11-23 | 내용 · 목소리는 v1 그대로. 지금 설명 중인 항목 강조 · 장 표시 · 진행 막대 · 화면이 천천히 다가오는 움직임 · 표지 캐릭터 테두리 정리. 소유자가 발음 확인(2026-11-23 「괜찮아」) |

완성 영상 파일은 저장소에 올리지 않는다(`video/out/` · 세션이 끝나면 사라짐). 받은 파일은 소유자가 보관한다.

## 다시 뽑기

```bash
bash video/openmontage_setup.sh          # 세션마다 한 번(새 세션은 자동)
source video/env.sh
python video/projects/seoul-info-silson/make.py v3                    # 그대로 다시
python video/projects/seoul-info-silson/make.py v3 --resynth options  # 글을 바꾼 장면만 내레이션 새로
python video/projects/seoul-info-silson/make.py v3 --no-render        # 화면만 만들어 장면 사진으로 확인(1분)
```

렌더까지 약 10분. 결과는 `video/out/seoul_info_silson_discount_v3.mp4`.

## 파일

| 파일 | 무엇 |
|---|---|
| `script.json` | 대본. 문장마다 `["화면 자막", "읽기용 글"]` — 읽기용 글은 숫자를 한글로 풀어 씀(「이천십삼 년」). 목소리 번호 `voice` · 빠르기 `speed` |
| `timing.json` | 장면별 내레이션 길이 · 문장 시작/끝(초). 내레이션을 새로 만들면 자동으로 바뀜 |
| `audio/*.mp3` | 소유자가 들어 본(확인한) 장면별 내레이션. 글을 안 바꾼 장면은 이 소리를 그대로 씀 |
| `build_html.py` | 화면(장면 11개 · 디자인 · 움직임)을 만드는 스크립트. 화면을 고치려면 여기 `SCENES` · `CSS` |
| `assets/` | 원본 PDF 에서 잘라 낸 캐릭터 · 그림 · 로고 |
| `make.py` | 재료 정리 → (필요하면) 내레이션 → 화면 → 점검 → 렌더를 한 번에 |
| `decision_log.json` | 고른 것과 이유(진행 방식 · 엔진 · 목소리 · 길이 등) |

## 장면 (id · 내용)

`intro` 표지 · `target` 할인 대상 · `systems` 두 제도 · `options` 옵션 1~3 · `option1` 옵션1이 맞는 고객 · `compare` 60대 여성 월 보험료 비교 · `male40` 40대 남성 3년 절감액 · `limits` 할인이 끊기는 경우 · `cases` CASE 1~3 · `withdraw` 청약철회 · CASE 4~6 · `outro` 상담 전 확인할 것
