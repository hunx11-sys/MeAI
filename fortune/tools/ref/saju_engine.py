# -*- coding: utf-8 -*-
"""사주(년·월·일주) + 오늘의 운세 엔진 — 엑셀 빌드용 원본 로직.
브라우저용 saju.js 와 같은 규칙·같은 해시를 쓴다 (verify_saju.py 로 전 기간 일치 검사).
- 시각 기준: 한국 표준시(UTC+9). 생년월일만 받으므로 '정오 출생'으로 가정해 절입일을 판정한다.
- 년주: 입춘 기준 / 월주: 12절 기준 / 일주: 율리우스일 기준(2000-01-01 = 戊午)
- 절기 시각: 태양 황경 계산(Meeus 저정밀식, 오차 수 분~15분 수준)
"""
import math, datetime as dt


def rnd(x): return math.floor(x + 0.5)  # JS Math.round 와 같은 반올림

STEM = "甲乙丙丁戊己庚辛壬癸"; STEM_K = "갑을병정무기경신임계"
BR = "子丑寅卯辰巳午未申酉戌亥"; BR_K = "자축인묘진사오미신유술해"
ANIMAL = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
EL = ["목", "화", "토", "금", "수"]
EL_H = ["木", "火", "土", "金", "水"]
BR_EL = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]
TERMS24 = ["춘분", "청명", "곡우", "입하", "소만", "망종", "하지", "소서", "대서", "입추", "처서", "백로",
           "추분", "한로", "상강", "입동", "소설", "대설", "동지", "소한", "대한", "입춘", "우수", "경칩"]  # 황경 0,15,...,345
# 월을 여는 12절 (황경, 월지 index: 寅=2 ...)
JIE = [(315, 2, "입춘"), (345, 3, "경칩"), (15, 4, "청명"), (45, 5, "입하"), (75, 6, "망종"), (105, 7, "소서"),
       (135, 8, "입추"), (165, 9, "백로"), (195, 10, "한로"), (225, 11, "입동"), (255, 0, "대설"), (285, 1, "소한")]
KST = 9 / 24


def stem_el(s): return s // 2
def gz(i): return STEM[i % 10] + BR[i % 12]
def gz_k(i): return STEM_K[i % 10] + BR_K[i % 12]
def gz_index(s, b):
    for i in range(60):
        if i % 10 == s and i % 12 == b: return i


def jd_from_date(y, m, d, frac=0.5):
    """그레고리력 날짜 → 율리우스일 (frac 0.5 = 정오, UT 기준 값을 넣으면 UT)"""
    if m <= 2: y -= 1; m += 12
    a = y // 100; b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5 + frac


def sun_lon(jd):
    T = (jd - 2451545.0) / 36525
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    M = math.radians(357.52911 + 35999.05029 * T - 0.0001537 * T * T)
    C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M) + (0.019993 - 0.000101 * T) * math.sin(2 * M) + 0.000289 * math.sin(3 * M)
    om = math.radians(125.04 - 1934.136 * T)
    return (L0 + C - 0.00569 - 0.00478 * math.sin(om)) % 360


def term_jd(year, lon):
    """year 해에 태양 황경이 lon 이 되는 순간의 JD(UT). 대략 날짜에서 뉴턴법."""
    # 황경 0(춘분)≈3/20 기준 대략 위치
    days = ((lon - 0) % 360) * 365.2422 / 360
    jd = jd_from_date(year, 3, 20, 0.5) + days
    if lon >= 285:  # 소한(285)~경칩(345)은 해당 연도 1~3월
        jd -= 365.2422
    for _ in range(50):
        diff = ((lon - sun_lon(jd) + 180) % 360) - 180
        jd += diff * 365.2422 / 360
        if abs(diff) < 1e-7: break
    return jd


def jd_to_kst(jd):
    j = jd + 0.5 + KST; Z = int(j); F = j - Z
    a = int((Z - 1867216.25) / 36524.25); A = Z + 1 + a - a // 4
    B = A + 1524; C = int((B - 122.1) / 365.25); D = int(365.25 * C); E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E) + F
    m = E - 1 if E < 14 else E - 13; y = C - 4716 if m > 2 else C - 4715
    d = int(day); secs = round((day - d) * 86400)
    return dt.datetime(y, m, d) + dt.timedelta(seconds=secs)


_CACHE = {}
def jie_list(year):
    """해당 연도 + 앞뒤 해의 12절 (KST datetime, 월지, 이름) 시간순"""
    if year in _CACHE: return _CACHE[year]
    out = []
    for y in (year - 1, year, year + 1):
        for lon, b, nm in JIE:
            out.append((jd_to_kst(term_jd(y, lon)), b, nm, y))
    out.sort(); _CACHE[year] = out
    return out


def terms24(year):
    """그해 24절기 (KST)"""
    res = []
    for k in range(24):
        lon = k * 15; nm = TERMS24[k]
        res.append((jd_to_kst(term_jd(year, lon)), nm, lon))
    return sorted(res)


def pillars(y, m, d):
    """생년월일(양력) → dict. 정오 출생 가정."""
    noon = dt.datetime(y, m, d, 12)
    js = jie_list(y)
    prev = [t for t in js if t[0] <= noon][-1]
    nxt = [t for t in js if t[0] > noon][0]
    ipchun = [t for t in js if t[2] == "입춘" and t[3] == y][0][0]
    sy = y if noon >= ipchun else y - 1
    ys = (sy - 4) % 10; yb = (sy - 4) % 12
    mb = prev[1]; mi = (mb - 2) % 12
    ms = ((ys % 5) * 2 + 2 + mi) % 10
    di = int(jd_from_date(y, m, d, 0.5) + 49) % 60
    on_day = [t for t in js if t[0].date() == dt.date(y, m, d)]
    return dict(sy=sy, ys=ys, yb=yb, ms=ms, mb=mb, ds=di % 10, db=di % 12, di=di,
                prev_jie=prev, next_jie=nxt, jie_today=on_day[0] if on_day else None)


def daeun(p, y, m, d, male):
    """대운 순역·대운수(만 나이, 3일=1년)"""
    yang_year = p["ys"] % 2 == 0
    fwd = (yang_year and male) or (not yang_year and not male)
    noon = dt.datetime(y, m, d, 12)
    span = (p["next_jie"][0] - noon) if fwd else (noon - p["prev_jie"][0])
    days = span.total_seconds() / 86400
    n = max(1, min(10, rnd(days / 3)))
    return fwd, n


def daeun_list(p, fwd, n, count=10):
    mi = gz_index(p["ms"], p["mb"]); out = []
    for k in range(1, count + 1):
        i = (mi + (k if fwd else -k)) % 60
        out.append((n + (k - 1) * 10, i))
    return out


def counts(p):
    c = [0] * 5
    for s in (p["ys"], p["ms"], p["ds"]): c[stem_el(s)] += 1
    for b in (p["yb"], p["mb"], p["db"]): c[BR_EL[b]] += 1
    return c


# ---------------------------------------------------------------- 관계 표
TEN = [["비견", "겁재"], ["식신", "상관"], ["편재", "정재"], ["편관", "정관"], ["편인", "정인"]]
def ten_god(d, o):
    rel = (stem_el(o) - stem_el(d)) % 5
    return TEN[rel][0 if (d % 2) == (o % 2) else 1]

SIX_HAP = [{0, 1}, {2, 11}, {3, 10}, {4, 9}, {5, 8}, {6, 7}]
SAM = [{8, 0, 4}, {2, 6, 10}, {5, 9, 1}, {11, 3, 7}]
HYEONG = [{2, 5}, {5, 8}, {8, 2}, {1, 10}, {10, 7}, {7, 1}, {0, 3}]
SELF_HYEONG = {4, 6, 9, 11}
HAE = [{0, 7}, {1, 6}, {2, 5}, {3, 4}, {8, 11}, {9, 10}]
WONJIN = [{0, 7}, {1, 6}, {2, 9}, {3, 8}, {4, 11}, {5, 10}]
PA = [{0, 9}, {1, 4}, {2, 11}, {3, 6}, {5, 8}, {7, 10}]
REL_SCORE = {"충": -6, "육합": 8, "반합": 6, "형": -4, "원진": -3, "해": -3, "파": -2, "같음": 3, "무난": 0}


def br_rel(t, p):
    s = {t, p}
    if abs(t - p) == 6: return "충"
    if t != p and s in SIX_HAP: return "육합"
    if t != p and any(s <= g for g in SAM): return "반합"
    if (t != p and s in HYEONG) or (t == p and t in SELF_HYEONG): return "형"
    if t != p and s in WONJIN: return "원진"
    if t != p and s in HAE: return "해"
    if t != p and s in PA: return "파"
    if t == p: return "같음"
    return "무난"


# ---------------------------------------------------------------- 점수 로직
CATS = ["재물", "대화", "일", "컨디션"]
TEN_MOD = {  # 재물, 대화, 일(영업), 컨디션
    "비견": (-2, 6, 4, 6), "겁재": (-5, 3, 6, 4), "식신": (6, 8, 4, 8), "상관": (4, 10, 2, 0), "편재": (10, 5, 6, 2),
    "정재": (12, 3, 5, 4), "편관": (2, -2, 8, -3), "정관": (4, 4, 10, 2), "편인": (-2, 0, 4, 5), "정인": (2, 6, 6, 8)}
WEIGHT = (0.3, 0.25, 0.25, 0.2)
BASE = 70; LO = 55; HI = 98
COLORS = ["초록", "빨강", "노랑", "흰색", "남색"]
COLOR_HEX = ["#2f9e62", "#e0402f", "#e0a800", "#9aa3ad", "#2b4a8b"]
NUMBERS = ["3, 8", "2, 7", "5, 10", "4, 9", "1, 6"]
DIRS = ["동쪽", "남쪽", "가운데", "서쪽", "북쪽"]


def fnv(s):
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch); h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def lucky_el(c, ds):
    """가장 적은 오행. 같으면 나를 돕는 쪽(인성→비겁→식상→재성→관성) 순서로"""
    me = stem_el(ds); order = [(me + 4) % 5, me, (me + 1) % 5, (me + 2) % 5, (me + 3) % 5]
    mn = min(c)
    return [e for e in order if c[e] == mn][0]


def fortune(y, m, d, male, ty, tm, td):
    """생년월일 + 성별 + 오늘 날짜 → 운세 dict"""
    from fortune_text import TEXT  # 문구 표
    p = pillars(y, m, d); t = pillars(ty, tm, td)
    c = counts(p); god = ten_god(p["ds"], t["ds"])
    r_day = br_rel(t["db"], p["db"]); r_year = br_rel(t["db"], p["yb"])
    te = stem_el(t["ds"])
    bal = 6 if c[te] == 0 else (-4 if c[te] >= 3 else 2)
    bal_k = "채움" if c[te] == 0 else ("넘침" if c[te] >= 3 else "보통")
    key = "%04d%02d%02d|%s|%04d%02d%02d" % (y, m, d, "M" if male else "F", ty, tm, td)
    h = fnv(key)
    sc = []
    for i in range(4):
        jit = ((h >> (i * 5)) % 9) - 4
        v = BASE + TEN_MOD[god][i] + REL_SCORE[r_day] + rnd(REL_SCORE[r_year] * 0.6) + bal + jit
        sc.append(max(LO, min(HI, v)))
    total = (30 * sc[0] + 25 * sc[1] + 25 * sc[2] + 20 * sc[3] + 50) // 100  # 가중 평균 반올림을 정수로 (소수 오차로 .5가 갈리는 것 방지)
    stars = 5 if total >= 90 else 4 if total >= 82 else 3 if total >= 72 else 2
    le = lucky_el(c, p["ds"])
    pick = lambda arr, salt: arr[(h >> salt) % len(arr)]
    return dict(p=p, t=t, counts=c, god=god, r_day=r_day, r_year=r_year, bal=bal_k, scores=sc, total=total, stars=stars,
                lucky_el=le, color=COLORS[le], number=NUMBERS[le], direction=DIRS[le],
                head=pick(TEXT["head"][god], 3), day_line=pick(TEXT["day_rel"][r_day], 7),
                tti_line=TEXT["tti_rel"][r_year].format(a=ANIMAL[p["yb"]], b=ANIMAL[t["db"]]),
                bal_line=TEXT["bal"][bal_k].format(e=EL[te]), tip=pick(TEXT["tip"][god], 11),
                keys=TEXT["keys"][god], hash=h)
