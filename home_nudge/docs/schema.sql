-- MeAI 홈 넛지 v5 · DB 표 정의 (PostgreSQL 14 기준)
-- 오라클로 옮길 때 : TEXT → VARCHAR2(4000)/CLOB, JSONB → CLOB(IS JSON), BOOLEAN → NUMBER(1), BIGSERIAL → IDENTITY, TIMESTAMPTZ → TIMESTAMP WITH TIME ZONE
-- 약속 : 날짜(biz_day)는 한국 시간 'YYYY-MM-DD' 의 DATE, 시각은 TIMESTAMPTZ. 주(week_id)는 ISO 주 'YYYY-Www'. 사용자 id 는 사내 사번 체계(user_id).
-- 보상 계산 규칙은 src/core/rules.js 가 기준이다. 이 표들은 그 상태를 나눠 담은 것이다.

-- ───────────────────────────── 사용자 상태 ─────────────────────────────
CREATE TABLE nz_user_state (
  user_id        VARCHAR(20) PRIMARY KEY,
  shields        SMALLINT    NOT NULL DEFAULT 0,          -- 보호권 장수 (최대 cfg.streak.shieldMax)
  shield_month   CHAR(7),                                  -- 마지막으로 보호권을 채운 달 'YYYY-MM'
  best_streak    INTEGER     NOT NULL DEFAULT 0,
  quiz_combo     INTEGER     NOT NULL DEFAULT 0,          -- 퀴즈 연속 정답
  prepared_day   DATE,                                     -- 그날 준비(prepareDay)를 마친 날
  settings       JSONB       NOT NULL DEFAULT '{}',        -- fx · sound · hideRank · buddy · tickerSec · tickerCats · tickerOrder · showBlocked · showShort
  join_month     SMALLINT,                                 -- 입사 차월 스냅숏 (신인 여정)
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE nz_day (                                      -- 하루 기록 (rules.dayRec)
  user_id        VARCHAR(20) NOT NULL,
  biz_day        DATE        NOT NULL,
  lit            BOOLEAN     NOT NULL DEFAULT FALSE,       -- 그날 불이 켜졌나
  attend         BOOLEAN     NOT NULL DEFAULT FALSE,
  shield         BOOLEAN     NOT NULL DEFAULT FALSE,       -- 보호권으로 메운 날
  xp             INTEGER     NOT NULL DEFAULT 0,
  lotto_cnt      SMALLINT    NOT NULL DEFAULT 0,           -- 그날 받은 세트 (하루 상한 비교)
  quiz_done      BOOLEAN     NOT NULL DEFAULT FALSE,
  talk_copied    BOOLEAN     NOT NULL DEFAULT FALSE,
  mission        BOOLEAN     NOT NULL DEFAULT FALSE,       -- 3개 달성 보상 받음
  allclear       BOOLEAN     NOT NULL DEFAULT FALSE,
  kinds          JSONB       NOT NULL DEFAULT '{}',        -- 행동별 횟수 {"reco.open":2,"chat.custom":1,…}
  tags           JSONB       NOT NULL DEFAULT '{}',        -- 태그별 횟수 {"reco.open:age_up":1}
  xp_count       JSONB       NOT NULL DEFAULT '{}',        -- XP 하루 상한 비교용 횟수
  PRIMARY KEY (user_id, biz_day)
);

CREATE TABLE nz_day_reco (                                 -- 그날 연 추천 고객 (같은 고객 하루 1번 · 세트 발급 여부)
  user_id        VARCHAR(20) NOT NULL,
  biz_day        DATE        NOT NULL,
  customer_id    VARCHAR(40) NOT NULL,
  opened_at      TIMESTAMPTZ NOT NULL,
  lotto_issued   BOOLEAN     NOT NULL DEFAULT FALSE,
  PRIMARY KEY (user_id, biz_day, customer_id)
);

CREATE TABLE nz_quest_done (
  user_id        VARCHAR(20) NOT NULL,
  biz_day        DATE        NOT NULL,
  quest_id       VARCHAR(30) NOT NULL,
  done_at        TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (user_id, biz_day, quest_id)
);

CREATE TABLE nz_week (                                     -- 주 기록 (리그 · 패스 · 응모권)
  user_id        VARCHAR(20) NOT NULL,
  week_id        CHAR(8)     NOT NULL,                     -- '2026-W44'
  org_branch     VARCHAR(20) NOT NULL,                     -- 리그 묶음 (그 주 소속 스냅숏)
  xp             INTEGER     NOT NULL DEFAULT 0,
  xp_reached_at  TIMESTAMPTZ,                              -- 같은 XP 면 먼저 도달한 사람이 위
  tickets        INTEGER     NOT NULL DEFAULT 0,           -- 이번 주 커피 응모권
  perfect        BOOLEAN     NOT NULL DEFAULT FALSE,       -- 개근 보너스 받음
  pass_steps     JSONB       NOT NULL DEFAULT '{}',        -- {"0": 시각, "1": 시각 …}
  frame          VARCHAR(10),                              -- gold · mvp
  prev_rank      SMALLINT,
  PRIMARY KEY (user_id, week_id)
);
CREATE INDEX nz_week_league ON nz_week (week_id, org_branch, xp DESC, xp_reached_at);

-- ───────────────────────────── 보상 원장 (모든 보상은 여기만 본다) ─────────────────────────────
CREATE TABLE nz_ledger (
  id             BIGSERIAL   PRIMARY KEY,
  user_id        VARCHAR(20) NOT NULL,
  ts             TIMESTAMPTZ NOT NULL,
  biz_day        DATE        NOT NULL,
  week_id        CHAR(8)     NOT NULL,
  type           VARCHAR(10) NOT NULL CHECK (type IN ('ticket', 'lotto', 'shield', 'badge')),
  amount         INTEGER     NOT NULL,                     -- 보호권 사용은 음수
  rule           VARCHAR(30) NOT NULL,                     -- attend · attend.perfect · quiz.correct · talk.copy · quest.mission · quest.allclear · lotto.issue · pass.N · shield.monthly · shield.use · badge.<id>
  label          VARCHAR(60) NOT NULL,
  ref            VARCHAR(60),                              -- 퀴즈 id · 화법 id · 고객 id · 주 id …
  idem           VARCHAR(64),                              -- 화면이 보낸 멱등 키
  config_ver     VARCHAR(20) NOT NULL                      -- 그때의 설정 버전 (정산 근거)
);
CREATE UNIQUE INDEX nz_ledger_idem ON nz_ledger (user_id, idem, rule) WHERE idem IS NOT NULL;
CREATE INDEX nz_ledger_user_day ON nz_ledger (user_id, biz_day);
CREATE INDEX nz_ledger_week_type ON nz_ledger (week_id, type);

CREATE TABLE nz_idem (                                     -- 멱등 응답 보관 (24시간)
  user_id        VARCHAR(20) NOT NULL,
  idem           VARCHAR(64) NOT NULL,
  response       JSONB       NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, idem)
);

CREATE TABLE nz_badge (
  user_id        VARCHAR(20) NOT NULL,
  badge_id       VARCHAR(30) NOT NULL,
  earned_at      TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (user_id, badge_id)
);
CREATE TABLE nz_counter (                                  -- 누적 횟수 (배지 · counter 형)
  user_id        VARCHAR(20) NOT NULL,
  key            VARCHAR(30) NOT NULL,                     -- talk.copy · reco.open · cheer.send
  value          INTEGER     NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, key)
);
CREATE TABLE nz_first (                                    -- 첫 경험 (신인 여정)
  user_id        VARCHAR(20) NOT NULL,
  kind           VARCHAR(30) NOT NULL,
  at             TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (user_id, kind)
);
CREATE TABLE nz_seen (                                     -- 본 것 (추첨 결과 · 리캡 · 공지)
  user_id        VARCHAR(20) NOT NULL,
  kind           VARCHAR(10) NOT NULL,                     -- draw · recap · notice
  key            VARCHAR(40) NOT NULL,
  at             TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (user_id, kind, key)
);
CREATE TABLE nz_buddy_dismiss (
  user_id        VARCHAR(20) NOT NULL,
  biz_day        DATE        NOT NULL,
  buddy_id       VARCHAR(20) NOT NULL,
  PRIMARY KEY (user_id, biz_day, buddy_id)
);
CREATE TABLE nz_cheer (                                    -- 응원 (하루 3번 · 한 사람에 1번)
  from_user      VARCHAR(20) NOT NULL,
  to_user        VARCHAR(20) NOT NULL,
  biz_day        DATE        NOT NULL,
  at             TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (from_user, to_user, biz_day)
);
CREATE INDEX nz_cheer_to ON nz_cheer (to_user, at DESC);

-- ───────────────────────────── 로또(행운번호) · 커피 추첨 ─────────────────────────────
CREATE TABLE nz_lotto_round (
  round_id       CHAR(8)     PRIMARY KEY,                  -- '2026-W44'
  label          VARCHAR(20) NOT NULL,                     -- '10월 5주차'
  pool           SMALLINT    NOT NULL DEFAULT 45,
  pick           SMALLINT    NOT NULL DEFAULT 6,
  opened_at      TIMESTAMPTZ NOT NULL,
  cutoff_at      TIMESTAMPTZ NOT NULL,                     -- 금 16:00
  draw_at        TIMESTAMPTZ NOT NULL,                     -- 금 17:00
  seed_commit    CHAR(64)    NOT NULL,                     -- SHA-256(seed) : 회차를 열 때 공개
  seed           CHAR(64),                                 -- 추첨 뒤에만 채움 (그전에는 별도 비밀 저장소)
  numbers        SMALLINT[],                               -- 당첨번호 6개 (오라클 : VARCHAR2 '4,6,12,24,39,42')
  drawn_at       TIMESTAMPTZ,
  set_count      INTEGER
);
CREATE TABLE nz_lotto_set (
  id             BIGSERIAL   PRIMARY KEY,
  round_id       CHAR(8)     NOT NULL REFERENCES nz_lotto_round,
  user_id        VARCHAR(20) NOT NULL,
  nums           SMALLINT[]  NOT NULL,                     -- 오름차순 6개
  issued_at      TIMESTAMPTZ NOT NULL,
  customer_id    VARCHAR(40) NOT NULL,                     -- 어떤 추천 고객 영업으로 받았나
  source_kind    VARCHAR(20) NOT NULL,                     -- chat.custom (운영) · reco.open
  confirmed      BOOLEAN     NOT NULL DEFAULT TRUE,        -- 서버 간 이벤트로 확정됐나 (INTEGRATION 5장)
  ledger_id      BIGINT      REFERENCES nz_ledger
);
CREATE INDEX nz_lotto_set_round_user ON nz_lotto_set (round_id, user_id);
CREATE TABLE nz_lotto_win (
  set_id         BIGINT      PRIMARY KEY REFERENCES nz_lotto_set,
  round_id       CHAR(8)     NOT NULL,
  user_id        VARCHAR(20) NOT NULL,
  match_cnt      SMALLINT    NOT NULL,
  tier_match     SMALLINT    NOT NULL,                     -- 3 · 4 · 5
  prize          VARCHAR(40) NOT NULL,
  selected       BOOLEAN     NOT NULL,                     -- 등수 인원 상한 안에 뽑혔나
  notified_at    TIMESTAMPTZ,
  sent_at        TIMESTAMPTZ                               -- 경품 발송 완료
);
CREATE TABLE nz_coffee_draw (
  week_id        CHAR(8)     NOT NULL,
  user_id        VARCHAR(20) NOT NULL,
  tickets        INTEGER     NOT NULL,
  won            BOOLEAN     NOT NULL DEFAULT FALSE,
  prize          VARCHAR(40),
  notified_at    TIMESTAMPTZ,
  PRIMARY KEY (week_id, user_id)
);

-- ───────────────────────────── 퀴즈 · 퀘스트 일정 ─────────────────────────────
CREATE TABLE nz_quiz (
  quiz_id        VARCHAR(30) PRIMARY KEY,
  publish_date   DATE        UNIQUE,                       -- 하루 1문제
  type           VARCHAR(10) NOT NULL CHECK (type IN ('ox', 'choice')),
  category       VARCHAR(20) NOT NULL,                     -- 신상품 · 영업 이슈 · 상품 상식 · MeAI 활용
  question       TEXT        NOT NULL,
  options        JSONB,                                    -- 객관식 보기
  answer         VARCHAR(5)  NOT NULL,                     -- 'O' · 'X' · 보기 번호(0부터)
  explain        JSONB       NOT NULL,                     -- 세 줄 해설
  source         TEXT        NOT NULL,                     -- 출처 (없으면 등록 불가)
  ask            TEXT,                                     -- MeAI에게 더 묻기 질문
  status         VARCHAR(10) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'rejected', 'published')),
  created_by     VARCHAR(20) NOT NULL,
  reviewed_by    VARCHAR(20),                              -- 준법 검수자
  reviewed_at    TIMESTAMPTZ,
  review_note    TEXT
);
CREATE TABLE nz_quiz_answer (
  quiz_id        VARCHAR(30) NOT NULL REFERENCES nz_quiz,
  user_id        VARCHAR(20) NOT NULL,
  choice         VARCHAR(5)  NOT NULL,
  correct        BOOLEAN     NOT NULL,
  explained      BOOLEAN     NOT NULL DEFAULT FALSE,
  answered_at    TIMESTAMPTZ NOT NULL,
  org_hq         VARCHAR(20), org_branch VARCHAR(20), org_team VARCHAR(20),   -- 지점별 참여율 · 정답률 (전달 도달 지도)
  PRIMARY KEY (quiz_id, user_id)
);
CREATE TABLE nz_quest_schedule (
  biz_day        DATE        PRIMARY KEY,
  quest_ids      JSONB       NOT NULL,                     -- 5개 ["attend","quiz","chat_custom","consent_req","talk_copy"]
  set_by         VARCHAR(20) NOT NULL,
  set_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ───────────────────────────── 화법 마트 ─────────────────────────────
CREATE TABLE nz_talk (
  talk_id        VARCHAR(20) PRIMARY KEY,                  -- 't-001' ~ 't-798' · 제출분 'my-…'
  cat            CHAR(1)     NOT NULL,                     -- A ~ N
  sit            VARCHAR(10) NOT NULL,                     -- 오프닝·접근 · 니즈환기 · 상품설명 · 반론처리 · 클로징 · 관계관리 · 다짐·구호
  tags           JSONB       NOT NULL DEFAULT '[]',        -- 담보 태그
  head           VARCHAR(200) NOT NULL,                    -- 핵심 문장 (배너 · 따라 쓰기)
  body           TEXT        NOT NULL,                     -- 전체 화법 (450자 안쪽)
  why            TEXT, tip TEXT, title VARCHAR(100),
  author_user_id VARCHAR(20),                              -- 제출자 (화면에는 가린 이름)
  author_name    VARCHAR(40),
  org            VARCHAR(60),
  grade          VARCHAR(10) NOT NULL DEFAULT 'normal',    -- rec · normal
  quality        CHAR(1),                                  -- S A B C D
  review         VARCHAR(10) NOT NULL DEFAULT 'pending' CHECK (review IN ('ok', 'fixed', 'block', 'pending')),
  block_reason   TEXT,
  noise          BOOLEAN     NOT NULL DEFAULT FALSE,       -- 짧은 응답 (배너 기본 제외)
  src            VARCHAR(20) NOT NULL DEFAULT 'FP 응답',    -- FP 응답 · 우수사례20선 · 한줄명화법 · 상시 공모
  seasonal       BOOLEAN     NOT NULL DEFAULT FALSE,
  show_real_name BOOLEAN     NOT NULL DEFAULT FALSE,       -- 실명 표시 동의 (준법 확인 뒤)
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX nz_talk_cat ON nz_talk (cat, grade);
CREATE TABLE nz_talk_reaction (
  talk_id        VARCHAR(20) NOT NULL REFERENCES nz_talk,
  user_id        VARCHAR(20) NOT NULL,
  type           VARCHAR(5)  NOT NULL CHECK (type IN ('like', 'save', 'used')),
  at             TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (talk_id, user_id, type)
);
CREATE TABLE nz_talk_copy (
  talk_id        VARCHAR(20) NOT NULL REFERENCES nz_talk,
  user_id        VARCHAR(20) NOT NULL,
  at             TIMESTAMPTZ NOT NULL,
  ok_chars       SMALLINT    NOT NULL,                     -- copyScore 결과 (서버 재채점)
  total_chars    SMALLINT    NOT NULL,
  rewarded       BOOLEAN     NOT NULL                      -- 그날 응모권 받은 1번째인가
);
CREATE INDEX nz_talk_copy_user ON nz_talk_copy (user_id, at DESC);

-- ───────────────────────────── 운영 설정 · 사용 기록 · 집계 ─────────────────────────────
CREATE TABLE nz_config (                                   -- config/nudge.config.json 의 버전 이력
  version        VARCHAR(20) PRIMARY KEY,
  body           JSONB       NOT NULL,
  note           TEXT,
  set_by         VARCHAR(20) NOT NULL,
  set_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  active         BOOLEAN     NOT NULL DEFAULT FALSE        -- 하나만 TRUE
);

CREATE TABLE nz_event_log (                                -- 화면 사용 기록 (docs/EVENTS.md) · 일 단위 파티션 · 13개월 보관
  id             BIGSERIAL,
  received_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  ts             TIMESTAMPTZ NOT NULL,
  user_hash      CHAR(64)    NOT NULL,                     -- 사번 해시 (원장과 조인할 때만 키 테이블로 복원, 본사 데이터 담당 권한)
  org_hq         VARCHAR(20), org_branch VARCHAR(20), org_team VARCHAR(20),
  session_id     VARCHAR(40),
  el             VARCHAR(40) NOT NULL,
  action         VARCHAR(40) NOT NULL,
  meta           JSONB       NOT NULL DEFAULT '{}',
  client         VARCHAR(40),
  version        VARCHAR(10)
) PARTITION BY RANGE (ts);

CREATE TABLE nz_agg_daily (                                -- 대시보드 집계 (5명 미만 조직 칸은 화면에서 숨김)
  day            DATE        NOT NULL,
  org_level      VARCHAR(6)  NOT NULL CHECK (org_level IN ('all', 'hq', 'branch', 'team')),
  org_code       VARCHAR(20) NOT NULL,
  headcount      INTEGER, visitors INTEGER, attend INTEGER, lit INTEGER,
  quiz_join      INTEGER, quiz_ok INTEGER, talk_copy INTEGER, talk_save INTEGER,
  reco_shown     INTEGER, reco_open INTEGER, chat_custom INTEGER, chat_general INTEGER,
  lotto_sets     INTEGER, tickets INTEGER, fx_skip INTEGER, fx_off_users INTEGER,
  dock_views     JSONB,                                    -- 막대 칸별 열람
  PRIMARY KEY (day, org_level, org_code)
);
-- 표 26개 : user_state · day · day_reco · quest_done · week · ledger · idem · badge · counter · first · seen · buddy_dismiss · cheer ·
--           lotto_round · lotto_set · lotto_win · coffee_draw · quiz · quiz_answer · quest_schedule · talk · talk_reaction · talk_copy · config · event_log · agg_daily
