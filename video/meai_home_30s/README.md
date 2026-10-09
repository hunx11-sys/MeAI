# MeAI홈 오픈 30초 영상

Higgsfield 로 **사람이 나오는 장면만** 만들고, 글자가 들어가는 것은 전부 이 폴더의 조립기가 영상 위에 따로 얹습니다.
AI 영상은 한글을 깨뜨려 그리기 때문입니다.

| 누가 만드나 | 무엇 |
|---|---|
| Higgsfield | 사무실 설계사(0~5초), 모니터 지지직(5~8초), 눈이 커짐(22.8~24초), 주먹 쥐고 일어남(24~27초) |
| 조립기(`build_video.py`) | MeAI홈 화면 그래픽(고객 카드 3×3, 말풍선, 보장 그래프, 설계안, 리포트), 「이제는 MeAI야!」, 마무리 두 줄, 「세일즈혁신TF」 워터마크, 효과음(직접 합성이라 저작권 걱정 없음) |

## 순서

1. Higgsfield 에서 아래 **0번 인물 사진**을 먼저 만든다(같은 사람이 모든 장면에 나오게 하려고).
2. 1~4번 장면을 그 사진을 넣고 **이미지 → 영상**으로 만든다. 길이는 5초, 화면 비율 16:9.
3. 받은 영상 파일 이름을 표대로 바꿔 `clips` 폴더에 넣는다.
4. `make_video.bat` 를 두 번 누른다 → `out\meai_home_30s.mp4` 완성.
   (영상 파일을 이 대화창에 올려 주셔도 제가 조립해 드립니다.)

영상이 5초보다 길어도 조립기가 앞에서부터 필요한 만큼만 자릅니다. 짧으면 마지막 장면을 멈춰 늘립니다.
없는 장면은 임시 그림으로 채우니, 하나씩 넣어 가며 확인해도 됩니다.

## Higgsfield 프롬프트

모든 프롬프트 끝에 붙어 있는 `no text...` 줄은 **지우지 마세요.** 글자·로고를 그리지 못하게 막는 줄입니다.
인물(성별·나이)은 예시이니 바꾸셔도 됩니다.

### 0. 인물 사진 (이미지 생성, Soul 등)

```
Photorealistic portrait of a Korean man in his late 20s, a rookie insurance sales agent,
short black hair, white dress shirt with sleeves rolled up, navy tie loosened, slightly tired face,
sitting at an office desk with a computer monitor, cinematic lighting, 16:9.
no text, no letters, no logos, no watermark
```

### 1. 막막함 → `s1_office.mp4` (0~5초에 씀)

```
Early morning in a dim corporate office, cold blue color grade. The young agent sits at his desk
staring at a blank paper list and an empty spreadsheet on the monitor, then grabs his hair with both
hands in frustration and slumps. Slow push-in camera, shallow depth of field, a wall clock in the
background, moody and quiet.
no text, no letters, no numbers on screen, no logos, no subtitles, no watermark
```

### 2. 지지직 → `s2_glitch.mp4` (5~8초에 씀, 앞 3초)

```
Close-up of the office computer monitor in a dark blue room. The screen flickers, distorts with
digital glitch and static noise, then bursts into a strong red glow that lights up the agent's face.
Fast, dramatic, cinematic.
no text, no letters, no logos, no user interface text, no subtitles, no watermark
```

조립기가 이 영상 위에 지지직 효과를 더 얹고, 끝 1초에 「MeAI홈」 화면을 직접 띄웁니다.

### 3. 눈이 커진다 → `s5d_eyes.mp4` (22.8~24초에 씀, 앞 1.2초)

```
Extreme close-up of the young agent's face lit by red and white light from a monitor. His eyes
widen in amazement, eyebrows rise, a small surprised smile. Quick slow-motion, cinematic.
no text, no letters, no logos, no subtitles, no watermark
```

### 4. 결심 → `s6_fist.mp4` (24~27초에 씀, 앞 3초)

```
The young agent clenches his fist with determination and stands up from his office chair, confident
energetic expression, the office now warm and bright with red accent light behind him. Low-angle
camera, dynamic push-in, heroic mood.
no text, no letters, no logos, no subtitles, no watermark
```

화면 아래쪽 3분의 1에 「이제는 MeAI야!」가 얹히니, 얼굴이 화면 가운데~위쪽에 오는 영상을 고르세요.

### (선택) 화면 장면도 Higgsfield 로 하고 싶다면

8~22.8초의 MeAI홈 화면 장면은 조립기 그래픽이 한글을 정확하게 보여 줘서 그대로 두기를 권합니다.
그래도 바꾸려면 아래 이름으로 넣으면 그 장면만 Higgsfield 영상으로 바뀝니다(대신 그 장면의 한글 화면은 빠집니다).
`s3_cards.mp4`(8~13초) · `s4_bubbles.mp4`(13~18초) · `s5a_graph.mp4` · `s5b_design.mp4` · `s5c_report.mp4`(각 1.6초)

## 시간표

| 시간 | 장면 | 화면 | 글자(조립기가 얹음) |
|---|---|---|---|
| 0~5초 | 막막함 | Higgsfield ① | 없음 |
| 5~8초 | 지지직 | Higgsfield ② + 지지직 효과 → MeAI홈 화면 | 「MeAI홈」 |
| 8~13초 | 고객추천 | 카드가 쏟아져 3×3 정렬 | 「이번 달 추천 고객 9명」, 카드 9장(이름은 김○○처럼 가림) |
| 13~18초 | 맞춤대화 | 말풍선 3개가 타자 치듯 | 「이 고객에게는 이렇게 말하세요」, 대화 문장 3줄 |
| 18~22.8초 | 보장분석 → 자동설계 → 리포트 | 1.6초씩 3컷 | 각 화면 제목 |
| 22.8~24초 | 눈이 커짐 | Higgsfield ③ | 없음 |
| 24~27초 | 결심 | Higgsfield ④ | 「이제는 MeAI야!」(24.6초부터) |
| 27~30초 | 마무리 | 검은 화면 | 흰 글씨 「찾는 영업에 작별을 고하다」 → 빨간 글씨 「찾아가는 영업, MeAI홈으로」 |
| 내내 | 워터마크 | | 오른쪽 아래 「세일즈혁신TF」 |

문구를 바꾸려면 `build_video.py` 위쪽의 `CUSTOMERS`(고객 카드)·`TALKS`(대화 문장), 아래쪽 `overlay`(결심·마무리 문구·워터마크)를 고칩니다.
보장분석 화면의 % 숫자는 연출용 가상값입니다. 글꼴은 저장소의 나눔고딕(`proposal_smart/ga_assets`)을 씁니다.

## 주의

- 화면 속 고객 이름·사연은 **가상 예시**입니다. 실제 고객 정보를 넣지 마세요.
- Higgsfield 영상에 소리가 들어 있어도 쓰지 않고, 조립기가 만든 효과음으로 바꿉니다.
- `clips/` 의 영상과 `out/` 의 결과물은 용량 때문에 저장소에 올라가지 않습니다.

## v2 애니메이션판 (2026.10.09)

Canva 완성본(장당 5초, 55초)을 받아 30초 애니메이션처럼 다시 편집합니다.

```
python animate_v2.py <Canva에서 받은 mp4> --out ../../dist/meai_home_30s_anime.mp4
```

- 장마다 정지 화면을 뽑아 줌·흔들림·번쩍임·글리치·집중선·차오르기(보장분석)·한 줄씩 체크(자동설계)·출력(리포트)으로 움직입니다.
- 말풍선은 메신저 앱처럼 그림자 있는 둥근 풍선(외침은 빨간 풍선, 생각은 연회색 풍선), 화면 장면에는 캐릭터 얼굴 아이콘이 붙습니다. `[글자]`로 감싼 말은 빨간색 강조입니다.
- 글꼴은 Pretendard(`fonts/`, SIL 오픈 폰트 라이선스, `fonts/LICENSE.txt`)입니다.
- 효과음은 직접 합성(초침·한숨·지지직·쾅·휙·뽁·타자·체크·출력·반짝·분당 128 박자)이라 저작권 걱정이 없습니다.
- 장면 길이 : 3.4 · 1.8 · 2.6 · 3.0 · 3.0 · 1.5 · 1.4 · 1.6 · 1.3 · 3.4 · 7.0초 (합계 30초)

## v3 실제 화면 + 나레이션판 (2026.10.09)

```
python animate_v3.py <Canva에서 받은 mp4> --out ../../dist/meai_home_30s_anime.mp4
```

- 화면 장면은 저장소의 실제 캡처(`guidebook_v4/captures`, 가이드북용 가림 처리본)를 영상에 바로 얹습니다. 임의 그래픽(막대그래프·체크 목록)은 모두 뺐습니다.
- 흐름 : 막막함("이번 달 누구에게 영업하지… 할 사람 다 한 것 같은데") → 영업포탈 → [MeAI 홈 바로가기] 클릭 → 지지직 → MeAI 홈 → STEP 01 오늘의 추천 고객 → 02 맞춤대화 → 03 AI 보장분석(가입 보험 정리·요약 답) → 04 AI 설계(가계약 생성) → 05 AI 리포트 → 눈 → 결심(「MeAI에서 고객추천부터 분석, 설계까지 한번에!」) → 마무리 → 피날레(「더 나은 세일즈를 위해,」 + 「세일즈혁신TF」가 쿵 날아와 박힘)
- 화면 장면에는 캐릭터 말풍선 대신 아래 나레이션 자막만 넣습니다. 말풍선은 캐릭터 장면(막막함·지지직·눈)에만 있습니다.
- 영업포탈 화면은 진입 안내 자료 캡처라 번호 표시(①~⑥)와 점선이 함께 보입니다.

## v4 실사 숏폼드라마판 (2026.10.09)

```
python animate_v4.py <고민·모니터 실사 영상> <놀람·주먹 실사 영상> --out ../../dist/meai_home_30s_drama.mp4
```

- 캐릭터 그림 대신 소유자가 준 실사 영상 2개(Gemini 생성)를 씁니다. 원본 영상은 `clips/`에 두면 되고 저장소에는 올리지 않습니다.
- 흐름 : 책상에서 고민(위쪽 타이핑 「이번 달 누구에게 영업하지… / 할 사람 다 한 것 같은데」) → 모니터로 다가가며 암전 → 영업포탈 → [MeAI 홈 바로가기] → MeAI 홈 → STEP 01~05 실제 화면 → 암전 → 놀람(「와… 이게 MeAI로 다 된다고?」) → 미소 → 주먹(「MeAI에서 고객추천부터 / 분석, 설계까지 한번에!」) → 마무리 → 세일즈혁신TF 피날레
- 실사 장면 : 차가운 색(고민)·따뜻한 색(놀람 이후), 가장자리 어둡게, 필름 결. 말풍선 없이 위쪽에 한 글자씩 찍히는 글자와 '탁탁' 타자 소리.
- 실사 영상 오른쪽 아래의 반짝이 표시는 Gemini가 AI 생성 영상에 넣는 표시라 지우지 않았습니다.
