#!/usr/bin/env python3
"""인수가이드(월간 xlsx) → MeAI 인수가이드 RAG 레코드 · 검증 질문 채점.

설계서 : docs/meai_rag/uw_guide_rag_design_2612.md
쓰는 법 :
    python3 -I scripts/uw_guide/parse_uw_guide.py <인수가이드.xlsx> <출력 폴더> [--repo .]

- 인수가이드 원본(대외비 · 교육용)과 출력 레코드는 저장소에 넣지 않는다(이 스크립트만 둔다).
- 숫자는 원본 셀에서만 온다. 병합 범위 밖으로 값을 끌어오지 않고, 빈칸은 「공란」으로 남긴다.
- 끝에 검증 질문(정답 셀)을 채점해 「전부 통과」 여부를 찍는다. 개정판을 바꿔 넣을 때마다 돌린다.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import warnings
import zipfile
from dataclasses import dataclass, field, asdict

warnings.filterwarnings("ignore")
import openpyxl  # noqa: E402
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI  # noqa: E402

# ─────────────────────────────── 1. 셀 읽기 ───────────────────────────────

GRAY_TINT = -0.0499893185216834  # 「해당 없음」 칸에 칠한 회색(테마 0 · 5% 어둡게)


@dataclass
class Cell:
    sheet: str
    ref: str
    raw: object            # 원본 값(숫자 · 글자 · None)
    text: str              # 현재 유효 글자(취소선 글자는 뺀 것)
    struck: list           # 취소선이 그어진 글자 조각(폐지된 값)
    merged: str | None     # 이 칸이 속한 병합 범위(A1:B2), 없으면 None
    anchor: str | None     # 병합 범위의 첫 칸(값이 실제로 들어 있는 칸)
    gray: bool             # 회색 칠(해당 없음 표시)
    numfmt: str


class Book:
    """병합 · 취소선 · 회색 칠 · 그림 위치까지 한 번에 읽어 둔다."""

    def __init__(self, path: str):
        self.path = path
        self.wb = openpyxl.load_workbook(path)
        self.wb_rt = openpyxl.load_workbook(path, rich_text=True)
        self.sha = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
        self.merge_of: dict[str, dict[tuple, tuple]] = {}
        for ws in self.wb.worksheets:
            m = {}
            for rg in ws.merged_cells.ranges:
                for r in range(rg.min_row, rg.max_row + 1):
                    for c in range(rg.min_col, rg.max_col + 1):
                        m[(r, c)] = (str(rg), (rg.min_row, rg.min_col))
            self.merge_of[ws.title] = m
        self.hidden = {ws.title for ws in self.wb.worksheets if ws.sheet_state != "visible"}
        self.drawings = read_drawings(path)

    def cell(self, sheet: str, ref: str) -> Cell:
        """병합 범위 안이면 범위 첫 칸의 값을 돌려준다(범위 밖으로는 절대 넘기지 않는다)."""
        ws, wr = self.wb[sheet], self.wb_rt[sheet]
        col, row = re.match(r"([A-Z]+)(\d+)", ref).groups()
        r, c = int(row), CI(col)
        mg = self.merge_of[sheet].get((r, c))
        ar, ac = mg[1] if mg else (r, c)
        src = ws.cell(ar, ac)
        rich = wr.cell(ar, ac).value
        text, struck = split_strike(rich, src.font.strike if src.font else False)
        fill = ws.cell(r, c).fill
        gray = bool(fill is not None and fill.fill_type == "solid"
                    and getattr(fill.fgColor, "type", "") == "theme"
                    and fill.fgColor.theme == 0 and abs((fill.fgColor.tint or 0) - GRAY_TINT) < 1e-6)
        return Cell(sheet, ref, src.value, text, struck, mg[0] if mg else None,
                    f"{L(ac)}{ar}" if mg else None, gray, src.number_format or "")


def split_strike(rich, cell_strike: bool):
    """서식 있는 글자에서 취소선 조각을 떼어 낸다.
    - 자기 서식이 없는 조각(맨 글자)은 칸 글꼴의 취소선을 따른다.
    - 자기 서식이 있는 조각은 그 서식만 본다(칸 전체에 취소선이 있어도 조각에 취소선이 없으면 현재 값 · 업계한도!F101)."""
    if rich is None:
        return "", []
    if isinstance(rich, (int, float)):
        return ("" if cell_strike else fmt_num(rich)), ([fmt_num(rich)] if cell_strike else [])
    if isinstance(rich, str):
        return ("" if cell_strike else rich), ([rich] if cell_strike else [])
    live, dead = [], []
    for part in rich:
        if isinstance(part, str):
            (dead if cell_strike else live).append(part)
        else:
            st = bool(part.font.strike) if part.font is not None else cell_strike
            if st and not part.text.strip():   # 취소선이 걸린 줄바꿈 · 공백은 글자 배치라 남긴다
                st = False
            (dead if st else live).append(part.text)
    return "".join(live), [d for d in dead if d.strip()]


def fmt_num(v):
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)


# ─────────────────────────────── 2. 그림 · 도형 ───────────────────────────────

def read_drawings(path: str) -> dict[str, list[dict]]:
    """시트별 그림 · 도형의 자리(from/to 칸 + 칸 안 오프셋)와 도형 글자, 그림 파일 지문."""
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    wbx = z.read("xl/workbook.xml").decode()
    rels = z.read("xl/_rels/workbook.xml.rels").decode()
    rid2t = {}
    for a in re.findall(r"<Relationship ([^>]+)/>", rels):
        rid2t[re.search(r'Id="([^"]+)"', a).group(1)] = re.search(r'Target="([^"]+)"', a).group(1)
    out: dict[str, list[dict]] = {}
    for name, rid in re.findall(r'<sheet name="([^"]+)"[^>]*r:id="(rId\d+)"', wbx):
        sh = rid2t[rid].split("/")[-1]
        rp = f"xl/worksheets/_rels/{sh}.rels"
        if rp not in names:
            continue
        for d in re.findall(r'Target="\.\./drawings/(drawing\d+\.xml)"', z.read(rp).decode()):
            x = z.read(f"xl/drawings/{d}").decode()
            dmap = {}
            drr = f"xl/drawings/_rels/{d}.rels"
            if drr in names:
                for a in re.findall(r"<Relationship ([^>]+)/>", z.read(drr).decode()):
                    dmap[re.search(r'Id="([^"]+)"', a).group(1)] = re.search(r'Target="([^"]+)"', a).group(1).split("/")[-1]
            for m in re.finditer(r"<xdr:(twoCellAnchor|oneCellAnchor)[^>]*>(.*?)</xdr:\1>", x, re.S):
                body = m.group(2)

                def pos(tag):
                    mm = re.search(rf"<xdr:{tag}>(.*?)</xdr:{tag}>", body, re.S)
                    if not mm:
                        return None
                    g = lambda t: int(re.search(rf"<xdr:{t}>(-?\d+)</xdr:{t}>", mm.group(1)).group(1))
                    return {"col": g("col") + 1, "colOff": g("colOff"), "row": g("row") + 1, "rowOff": g("rowOff")}

                imgs = [dmap.get(e, e) for e in re.findall(r'r:embed="([^"]+)"', body)]
                sha = [hashlib.sha256(z.read(f"xl/media/{i}")).hexdigest()[:12] for i in imgs if f"xl/media/{i}" in names]
                texts = ["".join(re.findall(r"<a:t>([^<]*)</a:t>", p)) for p in re.findall(r"<a:p>(.*?)</a:p>", body, re.S)]
                out.setdefault(name, []).append({
                    "name": re.findall(r'<xdr:cNvPr [^>]*name="([^"]*)"', body)[:1],
                    "from": pos("from"), "to": pos("to"), "images": imgs, "image_sha": sha,
                    "text": " / ".join(t for t in texts if t.strip()),
                })
    return out


# ─────────────────────────────── 3. 글자 → 값 ───────────────────────────────

O_MARKS = {"○", "O", "o", "◯", "●"}
DASHES = {"-", "\u2013", "\u2014", "\u2500", "ㅡ"}  # 하이픈 · 짧은/긴 줄표 · 가로줄
NO_WORDS = ("가입불가", "불가", "미탑재", "X", "×")


def classify(cell: Cell) -> str:
    """O(가능 표시) · DASH(대시) · NO(명시적 불가) · BLANK_GRAY(회색 빈칸 = 해당 없음) · BLANK(그냥 빈칸) · VALUE."""
    t = (cell.text or "").strip()
    if not t:
        return "BLANK_GRAY" if cell.gray else "BLANK"
    if t in O_MARKS:
        return "O"
    if t in DASHES:
        return "DASH"
    if t in ("X", "×") or t in ("불가", "가입불가", "미탑재"):
        return "NO"
    return "VALUE"


UNIT = {"억": 10000, "천": 1000, "백": 100}


def parse_manwon(s) -> float | None:
    """금액 글자를 만원 단위 숫자로. 750→750 · 1천→1000 · 1.5천→1500 · 2천만→2000 · 5만→5 · 1백만→100 · 1억3천만→13000.
    단위가 없는 맨 숫자는 그 표의 단위(만원)로 본다. 표마다 근거 셀을 따로 남긴다."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    t = str(s).strip().replace(",", "").replace(" ", "")
    t = re.sub(r"원$", "", t)
    if not t:
        return None
    if re.fullmatch(r"\d+(\.\d+)?", t):
        return float(t)
    m = re.fullmatch(r"((?:\d+(?:\.\d+)?[억천백])+)(\d+)?만?", t)
    if m:
        total = sum(float(n) * UNIT[u] for n, u in re.findall(r"(\d+(?:\.\d+)?)([억천백])", m.group(1)))
        return total + (float(m.group(2)) if m.group(2) else 0)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)만", t)
    if m:
        return float(m.group(1))
    return None


# ─────────────────────────────── 4. 추출기 ───────────────────────────────

def rec(**kw):
    return {k: v for k, v in kw.items() if v is not None}


def ev(c: Cell):
    """근거 : 시트!칸(병합이면 범위) + 원문."""
    e = {"cell": f"{c.sheet}!{c.ref}", "text": c.text}
    if c.merged:
        e["merged"] = c.merged
    if c.struck:
        e["struck"] = c.struck
    return e


def extract_lineup(bk: Book):
    """상품list : 상품 · 유형(연만기 · 세만기 · 무해지) · 납입면제 사유. 병합된 납입면제(H12:H23)는 그 범위 행에만 붙인다."""
    sh, out = "상품list", []
    for r in range(4, 42):
        grp, c_name, d_name = bk.cell(sh, f"B{r}"), bk.cell(sh, f"C{r}"), bk.cell(sh, f"D{r}")
        if not (c_name.text or d_name.text):
            continue
        # C:D 가 병합이면 한 이름, 아니면 C=상품군 · D=세부 플랜(통합간편 3.N.5)
        if c_name.merged and c_name.merged.startswith(f"C") and ":D" in c_name.merged and c_name.merged.split(":")[0][1:] == c_name.merged.split(":")[1][1:]:
            name, variant = c_name.text, None
        else:
            name, variant = c_name.text, (d_name.text or None)
        flags = {}
        for col, key in (("E", "연만기"), ("F", "세만기"), ("G", "무해지")):
            cc = bk.cell(sh, f"{col}{r}")
            flags[key] = {"mark": classify(cc), "evidence": ev(cc)}
        wv = bk.cell(sh, f"H{r}")
        out.append(rec(kind="lineup", line=grp.text.replace("\n", ""), product=name.replace("\n", " "), variant=variant,
                       flags=flags, waiver_reasons=(wv.text or None), waiver_mark=classify(wv),
                       evidence=[ev(grp), ev(c_name)] + ([ev(d_name)] if variant else []) + [ev(wv)]))
    return out


CANCER_COLS = "HIJKLMNOPQRSTUVW"


def cancer_headers(bk: Book):
    """통치 2~4행 : 1층 약칭(암통치(기본형)) · 2층 정식명(암통합치료비(기본형)) · 3층 가입구간. 병합 범위로 열 → 담보를 잇는다."""
    sh, cols = "통치", {}
    for col in CANCER_COLS:
        a, b, t = bk.cell(sh, f"{col}2"), bk.cell(sh, f"{col}3"), bk.cell(sh, f"{col}4")
        cols[col] = {"short": a.text, "formal": b.text, "tier": t.text, "tier_manwon": parse_manwon(t.text),
                     "short_cell": a.anchor or a.ref, "gray_header": a.gray}
    return cols


RIDER_KEY = {"암통치(기본형)": "CANCER_ITC_BASIC", "암통치(실속형)": "CANCER_ITC_LITE",
             "비통치(기본형)": "CANCER_ITC_NONPAY", "비통치(업셀링용)": "CANCER_ITC_NONPAY_MAJOR",
             "비통치II(고급형)": "CANCER_ITC_NONPAY2"}


def extract_cancer_pay(bk: Book):
    """통치!A1:W34 → 담보·형 × 가입구간 × 치료항목(× 세부대상) 한 줄씩. 빈칸도 「공란」 레코드로 남긴다(전 항목 질문에서 누락을 막는다)."""
    sh, hdr, out = "통치", cancer_headers(bk), []
    for r in range(5, 34):
        cat, item, sub, freq = bk.cell(sh, f"A{r}"), bk.cell(sh, f"B{r}"), bk.cell(sh, f"D{r}"), bk.cell(sh, f"G{r}")
        if not item.text:
            continue
        # B 가 B:F 로 병합돼 있으면 세부대상 없음(항목 하나), 아니면 D 가 세부대상(암 / 유사암 …)
        has_sub = not (item.merged and item.merged.split(":")[1].startswith("F"))
        sub_txt = sub.text if has_sub else None
        for col in CANCER_COLS:
            v = bk.cell(sh, f"{col}{r}")
            h = hdr[col]
            kind = classify(v)
            out.append(rec(kind="pay_cancer", rider=RIDER_KEY.get(h["short"], h["short"]), rider_short=h["short"],
                           rider_formal=h["formal"], tier=h["tier"], tier_manwon=h["tier_manwon"],
                           category=cat.text.replace("\n", ""), item=item.text, target=sub_txt,
                           freq=freq.text.replace("\n", "") or None, row_order=r,
                           value_state=kind, amount_manwon=parse_manwon(v.text) if kind == "VALUE" else None,
                           evidence=[ev(v), ev(item)] + ([ev(sub)] if sub_txt else []) + [ev(freq)]))
    # 면책 · 감액(34행) : 담보 병합 범위째로
    for col in CANCER_COLS:
        c = bk.cell(sh, f"{col}34")
        out.append(rec(kind="exclusion", rider=RIDER_KEY.get(hdr[col]["short"]), tier=hdr[col]["tier"],
                       text=c.text, evidence=[ev(c)]))
    return out


SUN2_TIER_COL = {"F": None, "H": None, "I": None, "J": None, "K": None}  # 48행 머리에서 채운다


def extract_sun2(bk: Book):
    """통치!A43:K65 (순통치Ⅱ). 오른쪽 L:W(질병통치 · 치단비/생활비)는 읽지 않는다.
    가입구간 열은 48행 머리(F:G=1억 · H · I · J · K)를, 63~65행 합산 블록은 C~G 열(2천→1억 오름차순)을 따로 쓴다."""
    sh, out = "통치", []
    tiers = {}
    for col in "FHIJK":
        h = bk.cell(sh, f"{col}48")
        tiers[col] = (h.text, parse_manwon(h.text), h)
    cat = None
    for r in range(49, 63):
        a, b, e = bk.cell(sh, f"A{r}"), bk.cell(sh, f"B{r}"), bk.cell(sh, f"E{r}")
        if not b.text:
            continue
        cat = a.text.replace("\n", "")
        for col in "FHIJK":
            v = bk.cell(sh, f"{col}{r}")
            name, man, hc = tiers[col]
            kind = classify(v)
            out.append(rec(kind="pay_sun2", rider="CIRC_ITC2", rider_short="순통치Ⅱ", tier=name, tier_manwon=man,
                           category=cat, item=b.text, freq=e.text.replace("\n", "") or None, row_order=r,
                           value_state=kind, amount_raw=v.text or None,
                           amount_manwon=parse_manwon(v.text.split("\n")[0]) if kind == "VALUE" else None,
                           evidence=[ev(v), ev(b), ev(e), ev(hc)]))
    # 63~65행 : 가입금액 · 합산기준(계산) · 가입한도
    for col in "CDEFG":
        t, s = bk.cell(sh, f"{col}63"), bk.cell(sh, f"{col}64")
        out.append(rec(kind="uw_basis", rider="CIRC_ITC2", scope="통치 표 하단 합산기준(계산)",
                       tier=t.text, tier_manwon=parse_manwon(t.text), recognized_manwon=parse_manwon(s.text),
                       evidence=[ev(t), ev(s), ev(bk.cell(sh, "A64")), ev(bk.cell(sh, "C65")), ev(bk.cell(sh, "H63"))]))
    return out


def extract_cancer_uw(bk: Book):
    """통치!A35:W41 : 가입금액 → 합산기준(계산)금액 · 가입한도, 합산 규칙(자기계약 · 업계)."""
    sh, hdr, out = "통치", cancer_headers(bk), []
    for col in CANCER_COLS:
        t, s, lim = bk.cell(sh, f"{col}36"), bk.cell(sh, f"{col}37"), bk.cell(sh, f"{col}38")
        out.append(rec(kind="uw_basis", rider=RIDER_KEY.get(hdr[col]["short"]), scope="통치 암통치 인수지침",
                       tier=t.text, tier_manwon=parse_manwon(t.text), recognized_manwon=parse_manwon(s.text),
                       policy_limit_text=lim.text, policy_limit_manwon=parse_manwon(lim.text),
                       evidence=[ev(t), ev(s), ev(lim)]))
    for r in (40, 41):
        g, own, members, ind = (bk.cell(sh, f"{c}{r}") for c in "ADHQ")
        out.append(rec(kind="agg_rule", scope="당사(자기계약) 증권/누적", group=g.text.replace("\n", ""),
                       limit_text=own.text, members_text=members.text, evidence=[ev(g), ev(own), ev(members)]))
        if r == 40:
            out.append(rec(kind="agg_rule", scope="업계", group="암주치·암통치 업계",
                           limit_text=ind.text, struck=ind.struck or None, evidence=[ev(ind)]))
    return out


def parse_tier_map(text: str):
    """「①1억:2천 ②8천:2천 … ⑤2천:4백」 · 「①1억-2천 ④3천/2천-7백」 → {가입금액: 인정금액}(만원)."""
    res = {}
    for left, right in re.findall(r"[①-⑳]?\s*([\d.억천백만/]+)\s*[:\-]\s*([\d.억천백만]+)", text):
        val = parse_manwon(right)
        for one in left.split("/"):
            k = parse_manwon(one)
            if k is not None and val is not None:
                res[k] = val
    return res


def extract_recognition_sources(bk: Book):
    """순통치(Ⅱ) 인정금액(합산 환산) 근거 세 곳을 「적용 대상」과 함께 따로 저장한다."""
    out = []
    c = bk.cell("신담보 (2)", "I11")
    out.append(rec(kind="recognition", rider="CIRC_ITC(Ⅱ)", scope="당사 2대주요치료비군 합산",
                   applies_to=bk.cell("신담보 (2)", "D11").text, limit_text=bk.cell("신담보 (2)", "G11").text,
                   tier_map=parse_tier_map(c.text),
                   evidence=[ev(bk.cell("신담보 (2)", "B11")), ev(bk.cell("신담보 (2)", "D11")), ev(bk.cell("신담보 (2)", "G11")), ev(c)]))
    c = bk.cell("업계한도", "H26")
    lim = bk.cell("업계한도", "F26")
    out.append(rec(kind="recognition", rider="CIRC_ITC(Ⅱ)", scope="업계(타사 포함) 순통치 합산",
                   applies_to=c.text.split("\n")[0], limit_text=lim.text, limit_struck=lim.struck or None,
                   tier_map=parse_tier_map(c.text.split("인정기준합산")[-1]),
                   evidence=[ev(bk.cell("업계한도", "B26")), ev(lim), ev(c)]))
    m = {}
    for col in "CDEFG":
        m[parse_manwon(bk.cell("통치", f"{col}63").text)] = parse_manwon(bk.cell("통치", f"{col}64").text)
    out.append(rec(kind="recognition", rider="CIRC_ITC2", scope="통치 순통치Ⅱ 표 하단(① 순통치 자체 · ② 순통치+2주치 겸용으로 표기)",
                   applies_to=bk.cell("통치", "H63").text, limit_text=bk.cell("통치", "C65").text, tier_map=m,
                   evidence=[ev(bk.cell("통치", "C63")), ev(bk.cell("통치", "C64")), ev(bk.cell("통치", "H63")), ev(bk.cell("통치", "C65"))]))
    c = bk.cell("업계한도", "D21")
    out.append(rec(kind="recognition", rider="CANCER_ITC_*", scope="업계 암통치 합산 인정기준",
                   applies_to=bk.cell("업계한도", "H19").text, limit_text=bk.cell("업계한도", "F19").text,
                   limit_struck=bk.cell("업계한도", "F19").struck or None, text=c.text,
                   evidence=[ev(bk.cell("업계한도", "F19")), ev(bk.cell("업계한도", "H19")), ev(c)]))
    return out


def extract_company_cum(bk: Book):
    """당사누적!B138:K157 암통합치료비 : 가입금액 · 누적(인정금액) · 한도 + 합산한도 글."""
    sh, out, rider = "당사누적", [], None
    for r in range(139, 158):
        c = bk.cell(sh, f"C{r}")
        if c.text:
            rider = c.text
        e, f, g = bk.cell(sh, f"E{r}"), bk.cell(sh, f"F{r}"), bk.cell(sh, f"G{r}")
        if not e.text:
            continue
        out.append(rec(kind="company_cum", rider_text=rider, tier=e.text, tier_manwon=parse_manwon(e.text),
                       recognized_text=f.text, recognized_manwon=parse_manwon(f.text),
                       policy_limit_text=g.text, evidence=[ev(c), ev(e), ev(f), ev(g)]))
    h = bk.cell(sh, "H139")
    out.append(rec(kind="agg_rule", scope="당사 증권/누적 합산한도", text=h.text, evidence=[ev(h)]))
    return out


def kv_block(bk: Book, sheet: str, rows, label_col: str, value_cols: list[str]):
    """상세 시트 위쪽 「상품명 · 종류 · 보험기간 · 납입면제…」 표 → 열(상품)별 키-값."""
    out = []
    for r in rows:
        lab = bk.cell(sheet, f"{label_col}{r}")
        if not lab.text:
            continue
        for vc in value_cols:
            v = bk.cell(sheet, f"{vc}{r}")
            if v.text or v.struck:
                out.append(rec(kind="product_attr", sheet=sheet, key=lab.text.strip().replace("\n", ""), column=vc,
                               value=v.text, struck=v.struck or None, evidence=[ev(lab), ev(v)]))
    return out


def extract_product_details(bk: Book):
    out = []
    out += kv_block(bk, "5.10.5", range(3, 14), "C", ["G", "L"])
    out += kv_block(bk, "통합상품", range(3, 10), "C", ["F", "I", "L"])
    out += kv_block(bk, "통합간편", range(3, 16), "C", ["E"])
    # 통합간편 종/형 구분표(J6:P10) : 「1형」 · 「1종」 의 뜻이 상품마다 다르다
    for r in (6, 7, 8):
        for k, v in (("K", "L"), ("N", "O")):
            kc, vc = bk.cell("통합간편", f"{k}{r}"), bk.cell("통합간편", f"{v}{r}")
            if kc.text:
                out.append(rec(kind="variant_code", sheet="통합간편", code=kc.text, meaning=vc.text,
                               axis="해약환급금" if k == "K" else "납입면제", evidence=[ev(kc), ev(vc)]))
    for r in (9, 10):
        kc, vc = bk.cell("통합간편", f"J{r}"), bk.cell("통합간편", f"L{r}")
        out.append(rec(kind="waiver_reason", sheet="통합간편", waiver_type=kc.text, reasons=vc.text, evidence=[ev(kc), ev(vc)]))
    for r in (4, 5, 6):
        kc, vc = bk.cell("가벼운355,31보험", f"J{r}"), bk.cell("가벼운355,31보험", f"K{r}")
        if kc.text:
            axis = bk.cell("가벼운355,31보험", f"I{r}").text.strip()
            out.append(rec(kind="variant_code", sheet="가벼운355,31보험(간편한31)", code=kc.text, meaning=vc.text,
                           axis=axis, evidence=[ev(kc), ev(vc)]))
    return out


def extract_new_riders(bk: Book):
    sh, out = "신담보 (2)", []
    for r in range(8, 13):
        b = bk.cell(sh, f"B{r}")
        if not b.text or (b.anchor and b.anchor != f"B{r}"):
            continue
        d, g, i = (bk.cell(sh, f"{c}{r}") for c in "DGI")
        out.append(rec(kind="new_rider", group="순통치Ⅱ", name=b.text, operation=d.text, limit_text=g.text,
                       note=i.text, evidence=[ev(b), ev(d), ev(g), ev(i)]))
    return out


def resolve_badges(bk: Book):
    """통치 머리의 「선지급」 그림 → 바로 오른쪽 담보(왼쪽 붙임)와 바로 왼쪽 담보(끝 붙임) 두 후보를 함께 남긴다."""
    out = []
    hdr = cancer_headers(bk)
    for d in bk.drawings.get("통치", []):
        if not d["images"]:
            continue
        f, t = d["from"], d["to"]
        right = bk.cell("통치", f"{L(t['col'])}2")
        left = bk.cell("통치", f"{L(f['col'])}2")
        out.append(rec(kind="badge", label="선지급(그림)", image=d["images"][0], image_sha=d["image_sha"][0] if d["image_sha"] else None,
                       anchor=f"{L(f['col'])}{f['row']}:{L(t['col'])}{t['row']}",
                       candidate_start_of=right.text or None, candidate_end_of=left.text or None))
    return out


# ─────────────────────────────── 5. 조회(숫자 결정) ───────────────────────────────

class Store:
    def __init__(self, records):
        self.r = records

    def pay(self, rider, tier_manwon, kinds=("pay_cancer", "pay_sun2")):
        rows = [x for x in self.r if x["kind"] in kinds and x["rider"] == rider and x.get("tier_manwon") == tier_manwon]
        return sorted(rows, key=lambda x: x["row_order"])

    def tiers(self, rider):
        return sorted({x["tier_manwon"] for x in self.r if x["kind"] in ("pay_cancer", "pay_sun2") and x["rider"] == rider})

    def riders_with_tier(self, tier_manwon, kinds=("pay_cancer",)):
        out = []
        for x in self.r:
            if x["kind"] in kinds and x.get("tier_manwon") == tier_manwon and x["value_state"] == "VALUE":
                if x["rider"] not in out:
                    out.append(x["rider"])
        return out


# ─────────────────────────────── 6. 약관 대조(저장소 마스터) ───────────────────────────────

def cross_check_terms(store: Store, repo: str):
    """통치 지급표 ↔ 약관에서 뽑은 금액표(proposal_smart/product_data.json). 다르면 목록으로 돌려준다."""
    p = os.path.join(repo, "proposal_smart", "product_data.json")
    if not os.path.exists(p):
        return {"skipped": "product_data.json 없음"}
    d = json.load(open(p))
    res = {"checked": 0, "diff": []}
    # 암통치 기본형(CB) : 약관 항목 순서 → 통치 행
    cb_rows = [23, 24, 25, 26, 27, 28, 29, 30, 5, 6, 7, 8, 9, 10, 11, 18, 19, 20, 21, 22, 31, 32]
    cl_rows = [5, 6, 7, 8, 9, 10, 20, 21, 22]
    cv_rows = [49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
    for ty, rider, rows, kind in (("CB", "CANCER_ITC_BASIC", cb_rows, "pay_cancer"),
                                  ("CL", "CANCER_ITC_LITE", cl_rows, "pay_cancer"),
                                  ("CV", "CIRC_ITC2", cv_rows, "pay_sun2")):
        for tier, amts in d["AMT"][ty].items():
            t = float(tier)
            got = {x["row_order"]: x for x in store.pay(rider, t, kinds=(kind,))}
            for i, row in enumerate(rows):
                x = got.get(row)
                v = x.get("amount_manwon") if x else None
                if ty == "CV" and row == 59 and v is not None:  # 순통치 재활 칸 「30」 = 1일 2만 × 연 15회
                    v = v / 15
                res["checked"] += 1
                if v != float(amts[i]):
                    res["diff"].append({"ty": ty, "tier": tier, "row": row, "sheet": v, "terms": amts[i]})
    return res


# ─────────────────────────────── 7. 검증 질문(정답 셀) ───────────────────────────────

def checks(bk: Book, store: Store, recs):
    C = lambda s, r: bk.cell(s, r)
    Q = []

    def q(no, question, got, want, cells):
        Q.append({"no": no, "q": question, "ok": got == want, "got": got, "want": want, "cells": cells})

    q(1, "The 건강한 5.10.5 무해지 표시", classify(C("상품list", "G5")), "O", ["상품list!G5"])
    q(2, "The 건강한 5.10.5 연만기 표시(공란=표시 없음)", classify(C("상품list", "E5")), "BLANK", ["상품list!E5"])
    q(3, "The 건강한 5.10.5 무해지 10년납", "무해지 10년납 가입불가" in C("5.10.5", "G6").text, True, ["5.10.5!G6"])
    q(4, "알파Plus 무해지 납기", C("통합상품", "I6").text.split("\n")[0], "20/25/30년납", ["통합상품!I4", "통합상품!I6"])
    q(5, "통합간편 세만기 2형 납기", "2형 20/30년납" in C("통합간편", "E8").text, True, ["통합간편!E8", "통합간편!K7", "통합간편!L7"])
    q(6, "통합간편 납입면제2형 사유", C("통합간편", "L10").text, "납입면제 1형 + 중증화상및 부식 추가", ["통합간편!J10", "통합간편!L10"])
    q(7, "통합간편 「1종」 = 납입면제미적용형", C("통합간편", "O7").text, "납입면제미적용형", ["통합간편!N7", "통합간편!O7"])
    q(8, "간편31 「1종」 = 보험료 납입면제형(통합간편과 반대)", C("가벼운355,31보험", "K4").text, "보험료 납입면제형", ["가벼운355,31보험!J4", "가벼운355,31보험!K4"])
    basic8 = store.pay("CANCER_ITC_BASIC", 8000)
    q(9, "암통치 기본형 8천 : 행 수(공란 포함) · 값 있는 행", (len(basic8), sum(x["value_state"] == "VALUE" for x in basic8)), (29, 23), ["통치!I5:I33"])
    q(10, "암통치 기본형 8천 표적항암약물허가치료", next(x["amount_manwon"] for x in basic8 if x["row_order"] == 20), 2000.0, ["통치!I20", "통치!G20"])
    q(11, "암통치 기본형 가입구간(5천 없음)", store.tiers("CANCER_ITC_BASIC"), [4000.0, 8000.0, 10000.0], ["통치!H4:J4"])
    lite5 = store.pay("CANCER_ITC_LITE", 5000)
    q(12, "암통치 실속형 5천 내시경검사 = 회색 공란(해당 없음 · 기본형 값 끌어오지 않음)", next(x["value_state"] for x in lite5 if x["row_order"] == 23), "BLANK_GRAY", ["통치!M23"])
    s5 = store.pay("CIRC_ITC2", 5000)
    q(13, "순통치Ⅱ 5천 혈전용해", [(x["amount_manwon"], x["freq"]) for x in s5 if x["row_order"] == 52][0], (1000.0, "연1회"), ["통치!I52", "통치!E52"])
    q(14, "순통치Ⅱ 5천 수술", [(x["amount_manwon"], x["freq"]) for x in s5 if x["row_order"] == 58][0], (1000.0, "수술당"), ["통치!I58", "통치!E58"])
    q(15, "순통치Ⅱ 5천 외래재활 = 회색 아닌 공란(I59 를 아래로 끌어오지 않음 → 약관 대조 대상)", [x["value_state"] for x in s5 if x["row_order"] == 60][0], "BLANK", ["통치!I59", "통치!I60"])
    q(16, "순통치Ⅱ 생활비 3회 = 병합 F61:K61 → 5천 열도 1천만", [x["amount_manwon"] for x in s5 if x["row_order"] == 61][0], 1000.0, ["통치!F61:K61", "통치!E61:E62"])
    right = {C("통치", f"{c}52").text for c in "UVW"}
    sun_vals = {x.get("amount_raw") for x in recs if x["kind"] == "pay_sun2"}
    q(17, "순통치Ⅱ 레코드에 오른쪽 질병통치(U52:W52) 숫자 없음", bool(right & sun_vals), False, ["통치!U52:W52"])
    rec_src = {x["scope"]: x.get("tier_map", {}) for x in recs if x["kind"] == "recognition"}
    q(18, "순통치 2천 인정금액 : 통치 하단 / 신담보(2) / 업계한도",
      (rec_src["통치 순통치Ⅱ 표 하단(① 순통치 자체 · ② 순통치+2주치 겸용으로 표기)"].get(2000.0),
       rec_src["당사 2대주요치료비군 합산"].get(2000.0), rec_src["업계(타사 포함) 순통치 합산"].get(2000.0)),
      (700.0, 400.0, 700.0), ["통치!C63:C64", "'신담보 (2)'!I11", "업계한도!H26"])
    q(19, "업계 암통치 한도 : 취소선 5.1천만 → 현재 3건", (C("업계한도", "F19").text.strip(), C("업계한도", "F19").struck), ("→ 3건", ["5.1천만"]), ["업계한도!F19"])
    q(20, "암통치 기본형 4천 합산기준 : 통치 = 당사누적", (C("통치", "H37").text, C("당사누적", "F139").text), ("1천", "1천"), ["통치!H37", "당사누적!F139"])
    q(21, "선지급 그림 4개", len([x for x in recs if x["kind"] == "badge"]), 4, ["통치 그림 1~4(G2:H3 · J2:K3 · N2:O3 · T2:U3)"])
    q(22, "5.10.5 「보험료 가벼운 납입형」 = 취소선(삭제)", C("5.10.5", "G8").struck, ["보험료 가벼운 납입형"], ["5.10.5!G8"])
    f101 = C("업계한도", "F101")
    q(23, "업계 민사소송법률비용 : 칸 전체 취소선이어도 조각 서식 우선", (f101.struck, f101.text.replace("\n", " ").split()),
      (["2건(당사1건) "], ["25.09.01변경", "민사+급발진", "5.5천(당사1건)"]), ["업계한도!F101"])
    return Q


# ─────────────────────────────── 8. 실행 ───────────────────────────────

def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, outdir = argv[1], argv[2]
    repo = argv[argv.index("--repo") + 1] if "--repo" in argv else "."
    os.makedirs(outdir, exist_ok=True)
    bk = Book(src)
    recs = []
    for fn in (extract_lineup, extract_cancer_pay, extract_cancer_uw, extract_sun2, extract_recognition_sources,
               extract_company_cum, extract_product_details, extract_new_riders, resolve_badges):
        recs += fn(bk)
    for x in recs:
        x["source_version"] = {"file": os.path.basename(src), "sha256_16": bk.sha}
    store = Store(recs)
    with open(os.path.join(outdir, "records.jsonl"), "w") as f:
        for x in recs:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    meta = {"sha256_16": bk.sha, "hidden_sheets": sorted(bk.hidden),
            "counts": {k: sum(1 for x in recs if x["kind"] == k) for k in sorted({x["kind"] for x in recs})}}
    terms = cross_check_terms(store, repo)
    Q = checks(bk, store, recs)
    meta["terms_cross_check"] = terms
    meta["checks"] = Q
    json.dump(meta, open(os.path.join(outdir, "report.json"), "w"), ensure_ascii=False, indent=1)
    print(f"원본 지문 {bk.sha} · 숨긴 시트(색인 제외) {sorted(bk.hidden)}")
    print("레코드 :", meta["counts"])
    print(f"약관 대조 : {terms.get('checked')}칸 · 다른 곳 {len(terms.get('diff', []))}")
    for d in terms.get("diff", [])[:10]:
        print("   다름", d)
    for x in Q:
        print(("  통과 " if x["ok"] else "  실패 ") + f"Q{x['no']:02d} {x['q']} → {x['got']}" + ("" if x["ok"] else f" (기대 {x['want']})"))
    bad = [x for x in Q if not x["ok"]] + terms.get("diff", [])
    print("전부 통과" if not bad else f"실패 {len(bad)}건")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
