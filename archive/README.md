# archive — 지금 쓰지 않지만 남겨 둔 자료

대문·도구·생성기 어디에서도 부르지 않는 파일을 모아 둔 곳입니다(2026.10.06 정리).

| 파일 | 무엇 |
|---|---|
| `amtongchi_sim.html` | 암통합치료비 가입금액 시뮬레이터(정부 디자인 시스템 KRDS 화면판, 2026.09.29). 혼자 열리는 HTML — 대문에는 연결돼 있지 않음 |
| `DESIGN-nike.md` | 화면 디자인 참고 문서 |
| `AI 활용의 정점_ LLM 마스터 워크플로우.md` | LLM 활용 워크플로우 참고 문서 |

지운 지난 판(같은 날 정리) — 최신판이 있어 지웠고, GitHub 기록에서 언제든 되살릴 수 있습니다.
- `docs/MeAI_활용가이드북_v3_…_2026.09` · `docs/MeAI_활용가이드북_영업가족편_2026.09` (pdf·pptx·이미지판 6개) → 최신 `docs/MeAI_guidebook_v4_CRM_2026.10.*`
- `docs/영업지원도구6종_사내공모전.pptx` · `docs/영업지원도구6종_현장매뉴얼.pptx`(09.16) · `docs/meritz_tools6_feature_guide.pptx`(09.23) → 최신 `docs/meritz_tools6_contest_deck.pptx`
- `dist/meritz_tools_allinone_2610.zip` → 최신 `dist/영업지원도구6종.zip`

방송교안 `owner_v1`·`owner_v2` 는 최신 `owner_v3` 를 다시 만드는 재료라 남겼습니다(guidebook_v4/README.md 참고) → 2026.10.08 정리에서 지움(아래).

## 2026.10.08 정리 — 지난 판 · 중복 파일

지운 파일은 GitHub 기록에서 언제든 되살릴 수 있습니다(`git log --all -- <경로>` 로 찾아 `git checkout <커밋>^ -- <경로>`).

| 지운 파일 | 이유 · 대신 볼 파일 |
|---|---|
| `dist/보험용어사전.xlsx` (09.21, 389개) | 최신 `docs/보험용어사전_1386개_2026.09.xlsx`(1,386개). `scripts/build_glossary_xlsx.py` 를 돌리면 다시 생김 |
| `dist/ga-cell-rider-mapping.xlsx` | `dist/ga-blueprint-final.xlsx` 와 내용이 완전히 같은 복사본 |
| `dist/ga-sample-mom5105-40F-with-calc.pdf` (10.02) | 최신 샘플 `dist/ga-sample-gan31-M.pdf`(10.08) |
| `docs/guidebook_proto_sample_design.pdf` | 가이드북 생성기 시안 샘플(부르는 곳 없음) · 결과 샘플은 `docs/guidebook_proto_sample_output.pdf` |
| `docs/MeAI_broadcast_FP_2026.10_owner_v1.pptx` · `owner_v2.pptx` | 최신 `owner_v3`(+ `owner_v3_images`)의 앞 단계 |
| `docs/MeAI_CRM대문_고도화_*_2026.09` (1페이퍼 docx·pdf, 대표이사보고 pptx·pdf) | 9월 보고 자료 → 최신 `docs/MeAI_guidebook_v4_CRM_2026.10.*` |

홍보 영상 폴더(`docs/promo_15s` · `promo_15s_premium` · `promo_baki` · `promo_baki_anime`)에 4벌씩 있던 같은 글꼴(Pretendard 6종)과 도구 화면(`s1b~s6.png`)은
`docs/promo_shared/` 한 곳으로 모으고, 각 `ad.html` 이 `../promo_shared/` 를 부르게 고쳤습니다(파일 내용은 그대로 · 글꼴·그림 모두 불러와지는 것 확인).
