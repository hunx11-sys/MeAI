#!/usr/bin/env python3
"""서울중앙본부 정보미팅 · 실손 할인 제도 교육 영상 — HyperFrames 화면(index.html) 만들기.

    python build_html.py <timing.json> <workspace 폴더>

장면 시간은 내레이션 길이(timing.json)로 정한다. 화면 요소는 data-in="문장번호"(그 문장이 시작될 때 등장)와
data-fx(등장 방식)만 적어 두고, 아래 스크립트가 GSAP 타임라인으로 바꾼다.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

LEAD, TAIL = 0.7, 0.9          # 장면 시작 후 말 시작까지 · 말 끝난 뒤 장면 끝까지
CHAPTERS = {"target": "할인 대상 고객", "systems": "두 가지 할인 제도", "options": "선택형 특약 옵션", "option1": "옵션1이 맞는 고객",
            "compare": "월 보험료 비교", "male40": "40대 남성 3년 절감액", "limits": "할인이 끊기는 경우", "cases": "사례 CASE 1~3",
            "withdraw": "청약철회 · CASE 4~6", "outro": "상담 전 확인할 것"}
SOURCE = "출처: 금융위·금감원 「실손 계약전환 할인·선택형 할인특약 제도 관련 Q&A」(2026.11) 참조"

e = html.escape


def hd(t1: str, t2: str, sub: str = "") -> str:
    return (
        '<div class="hd">'
        '<div class="kicker">메리츠 스탠다드 세일즈북</div>'
        f'<h1 class="t1" data-in="0" data-fx="up">{t1}</h1>'
        f'<h2 class="t2" data-in="0" data-fx="up" data-d="0.12">{t2}</h2>'
        + (f'<p class="sub" data-in="0" data-fx="fade" data-d="0.3">{sub}</p>' if sub else "")
        + "</div>"
    )


def char(src: str, cls: str = "") -> str:
    return f'<img class="char {cls}" src="assets/{src}" alt="" data-in="0" data-fx="char">'


def alert(text: str, at: int) -> str:
    return f'<div class="alert" data-in="{at}" data-fx="up"><span class="bang">!</span><span>{text}</span></div>'


# ----------------------------------------------------------------------------- 장면별 화면
SCENES: dict[str, str] = {}

SCENES["intro"] = f"""
<div class="intro">
  <div class="intro-txt">
    <div class="meet" data-in="0" data-fx="up">서울중앙본부 정보미팅</div>
    <div class="kicker big">메리츠 스탠다드 세일즈북</div>
    <h1 class="t1 xl" data-in="0" data-fx="up" data-d="0.15">초기 실손 고객,</h1>
    <h2 class="t2 xl" data-in="0" data-fx="up" data-d="0.3">두 가지 할인 제도 한눈에</h2>
    <div class="pills">
      <span class="pill red" data-in="1" data-fx="pop">제도 ① 계약전환 할인</span>
      <span class="pill navy" data-in="1" data-fx="pop" data-d="0.25">제도 ② 선택형 할인특약</span>
    </div>
  </div>
  <img class="char hero" src="assets/char1.png" alt="" data-in="0" data-fx="char">
</div>
"""

SCENES["target"] = f"""
{hd("할인 대상 고객,", "증권의 가입일부터 확인", "초기 실손 고객의 보험료를 줄여 주는 두 제도의 대상입니다.")}
{char("char1.png")}
<div class="body">
  <div class="card target">
    <span class="pill red sm" data-in="0" data-fx="pop" data-d="0.4">할인 대상 고객</span>
    <div class="mega" data-in="1" data-fx="up"><b class="red">2013년 3월</b> 이전 가입</div>
    <div class="mega-sub" data-in="1" data-fx="up" data-d="0.2"><span class="hl">재가입 조건 없는</span> 1·2세대 실손</div>
    <div class="count" data-in="2" data-fx="pop">대상 약 <b class="red">1,630만 명</b></div>
    <div class="era">
      <div class="seg navy-bg" data-in="3" data-fx="left"><b>1세대</b> ~2009.9</div>
      <div class="seg red-bg" data-in="3" data-fx="left" data-d="0.2"><b>2세대</b> 2009.10~2013.3</div>
      <div class="cut" data-in="3" data-fx="fade" data-d="0.4"><span>2013.3 기준</span></div>
      <div class="seg gray-bg" data-in="3" data-fx="left" data-d="0.5">2013.4 이후 가입 : 대상 아님</div>
    </div>
  </div>
</div>
"""

SCENES["systems"] = f"""
{hd("두 가지 할인 제도", "고객이 선택합니다")}
<div class="body">
  <div class="two">
    <div class="card sys" data-grp="sys" data-in="1" data-fx="up">
      <span class="pill red sm">제도 ①</span>
      <div class="sys-name">계약전환 할인</div>
      <div class="sys-desc">5세대 실손으로 전환하면</div>
      <div class="sys-big red">3년간 50% 할인</div>
      <div class="sys-note" data-in="2" data-fx="fade">'26.11월부터 6개월 시행 후 연장 검토</div>
    </div>
    <div class="card sys" data-grp="sys" data-in="3" data-fx="up">
      <span class="pill navy sm">제도 ②</span>
      <div class="sys-name">선택형 할인특약</div>
      <div class="sys-desc">기존 실손에서 일부 보장만 제외</div>
      <div class="sys-big navy">최대 약 37% 할인</div>
      <div class="sys-note">별도 안내 전까지 계속 시행</div>
    </div>
  </div>
  <div class="chips3" data-in="3" data-fx="up" data-d="0.6">
    <div><span>고객이 선택하는 제도</span><b class="red">의무 가입 아님</b></div>
    <div><span>가입 후 최대 6개월</span><b class="red">청약철회 가능</b></div>
    <div><span>철회하면</span><b class="red">재신청·재가입 제한</b></div>
  </div>
  {alert('두 제도 모두 <b class="red">의무가 아니며</b>, 보험료가 줄어드는 만큼 <b class="red">보장도 줄어듭니다.</b>', 4)}
</div>
"""

def opt_row(n: int, color: str, title: str, desc: str, pct: str, width: int, at: int) -> str:
    return f"""
    <div class="opt" data-grp="opt" data-in="{at}" data-fx="up">
      <div class="ob {color}-bg"><small>옵션</small>{n}</div>
      <div class="ot"><b>{title}</b><span>{desc}</span></div>
      <div class="obar"><i class="{color}-bg" style="width:{width}%" data-in="{at}" data-fx="grow" data-d="0.3"></i></div>
      <div class="opct {color}">{pct}</div>
    </div>"""

SCENES["options"] = f"""
{hd("옵션별로 무엇이 빠지고", "얼마나 할인되나", "보장에서 빼는 항목에 따라 할인율이 달라집니다. (옵션 하나만 가입 시)")}
<img class="icon" src="assets/icon2.png" alt="" data-in="0" data-fx="char">
<div class="body">
  <div class="card opts">
    {opt_row(1, "red", "근골격계 물리치료 면책", "도수치료·체외충격파·비급여 주사제 <em>· 관리급여 치료는 급여 부분도 보장 제외</em>", "15~20%", 72, 1)}
    {opt_row(2, "orange", "비급여 MRI/MRA 면책", "비급여 MRI·MRA 보장 제외", "2~4%", 14, 3)}
    {opt_row(3, "navy", "자기부담률 20% 적용", "급여·비급여 모두 자기부담 20%", "9~17%", 60, 4)}
    <div class="optall" data-in="5" data-fx="pop">옵션 1~3 모두 가입 시 <span>1세대 <b class="red">약 37%</b></span><span>2세대 <b class="red">약 27%</b></span></div>
  </div>
</div>
"""

SCENES["option1"] = f"""
{hd("옵션 1,", "이런 고객에게 맞습니다")}
{char("char5.png")}
<div class="body">
  <div class="card o1">
    <div class="o1-who" data-in="0" data-fx="fade">1세대 60대 여성 · 연 보험료 216만 원 기준</div>
    <div class="o1-row">
      <div class="o1-box pink" data-in="0" data-fx="up" data-d="0.3"><span>옵션1 가입 시 절감액</span><b class="red">연 43.2만</b><small>216만 원 × 약 20%</small></div>
      <div class="gt" data-in="1" data-fx="fade">&gt;</div>
      <div class="o1-box blue" data-in="1" data-fx="up"><span>도수치료 등으로 받을 예상 보험금(연)</span><b class="navy">절감액보다 적다면</b></div>
    </div>
    <div class="o1-say" data-in="1" data-fx="pop" data-d="0.6"><b class="red">옵션1 가입</b>을 권할 만합니다</div>
  </div>
  <div class="chips4" data-in="2" data-fx="up">
    <div>옵션은 골라서 가입<small>(조합 7가지)</small></div><div>가입 후<small>옵션 추가 불가</small></div>
    <div>해지는<small>옵션 전체만 가능</small></div><div>해지 후<small>재가입 불가</small></div>
  </div>
  {alert('할인율은 <b class="red">5년 후부터 매년 조정(±25% 이내)</b>되며, 회사·상품별로 다릅니다.', 3)}
</div>
"""

def bar(label: str, sub: str, cls: str, val: str, pct: str, w: float, at: int, d: float = 0) -> str:
    pct_html = f'<span class="pp {cls}-bg">{pct}</span>' if pct else ""
    return f"""
      <div class="br" data-in="{at}" data-fx="up" data-d="{d}">
        <div class="bl"><b>{label}</b>{f"<small>{sub}</small>" if sub else ""}</div>
        <div class="bt"><i class="{cls}-bg" style="width:{w:.1f}%" data-in="{at}" data-fx="grow" data-d="{d + 0.15}"></i><span class="bv {cls}">{val}</span>{pct_html}</div>
      </div>"""

def W(v: int) -> float:
    return v / 176982 * 62

SCENES["compare"] = f"""
{hd("바꾸면 얼마나", "줄어드나?", "60대 여성 기준, 제도별 월 보험료를 비교했습니다.")}
<img class="icon" src="assets/icon3.png" alt="" data-in="0" data-fx="char">
<div class="body">
  <div class="card cmp">
    <div class="grp">
      <span class="tag dark">1세대</span>
      {bar("현재", "", "gray", "176,982원", "", W(176982), 1)}
      {bar("계약전환 할인", "전환 후 3년간", "red", "21,620원", "-87.8%", W(21620), 2)}
      {bar("5세대 전환", "", "orange", "43,241원", "-75.6%", W(43241), 2, 0.5)}
      {bar("선택형 특약", "옵션 1~3 모두", "navy", "111,499원", "-37.0%", W(111499), 2, 0.8)}
    </div>
    <div class="grp">
      <span class="tag dark">2세대</span>
      {bar("현재", "", "gray", "126,773원", "", W(126773), 3)}
      {bar("계약전환 할인", "전환 후 3년간", "red", "21,620원", "-82.9%", W(21620), 3, 0.3)}
      {bar("5세대 전환", "", "orange", "43,241원", "-65.9%", W(43241), 3, 0.6)}
      {bar("선택형 특약", "옵션 1~3 모두", "navy", "92,544원", "-27.0%", W(92544), 3, 0.9)}
    </div>
    <div class="foot" style="text-align:right" data-in="1" data-fx="fade">※ 6개 대형 손보사 기준 예시 · 회사별, 연령 증가 등에 따라 실제 보험료는 달라질 수 있음</div>
  </div>
</div>
"""

SCENES["male40"] = f"""
{hd("40대 남성이", "계약전환 할인을 받으면")}
{char("char1.png")}
<div class="body">
  <div class="card m40">
    <div class="m40-l">
      <div class="col" data-in="0" data-fx="up"><div class="cb gray-bg" style="height:290px" data-in="0" data-fx="rise"><b>7.8만</b></div><span>1세대 (월)</span></div>
      <div class="m40-mid" data-in="0" data-fx="fade" data-d="0.8">월 7만 원 절감</div>
      <div class="col" data-in="0" data-fx="up" data-d="0.4"><div class="cb red-bg" style="height:34px" data-in="0" data-fx="rise" data-d="0.4"><b class="out">0.8만</b></div><span>전환할인 (월)</span></div>
    </div>
    <div class="m40-r">
      <div class="m40-h">3년간 절감액</div>
      <div class="yrs">
        <div data-in="1" data-fx="pop"><span>1년차</span><b>84만</b></div>
        <div data-in="1" data-fx="pop" data-d="0.2"><span>2년차</span><b>84만</b></div>
        <div data-in="1" data-fx="pop" data-d="0.4"><span>3년차</span><b>84만</b></div>
      </div>
      <div class="sum" data-in="1" data-fx="pop" data-d="0.8">합계 <b>약 252만 원</b></div>
      <div class="foot sm">※ 1세대 월 7.8만 원, 5세대 1.6만 원 기준 · 비중증 비급여 이용이 적은 고객에게 적합</div>
    </div>
  </div>
  {alert('연간 보험료가 <b class="red">예상 보험금보다 많다면</b> 할인 제도를 검토하세요.', 2)}
</div>
"""

def lim(icon: str, title: str, tag: str, tagcls: str, text: str, at: int) -> str:
    return f"""<div class="lim" data-grp="lim" data-in="{at}" data-fx="up"><div class="li">{icon}</div><div><div class="lt">{title} <span class="tg {tagcls}-bg">{tag}</span></div><p>{text}</p></div></div>"""

SCENES["limits"] = f"""
{hd("할인이 안 되거나", "끊기는 경우", "가입 전에 꼭 안내해야 할 할인 제한 사항입니다.")}
{char("char4.png")}
<div class="body">
  <div class="lims">
    {lim("✕", "같은 증권의 다른 담보 해지", "전환할인", "red", '전환 신청일 <b>전후</b>로 일부만 해지해도 <b class="red">할인 미적용·종료</b>', 1)}
    {lim("↓", "같은 증권의 담보 가입금액 감액", "전환할인", "red", '감액도 표준약관상 <b>해지</b>로 봅니다. 하나만 감액해도 <b class="red">할인 미적용·종료</b>', 2)}
    {lim("↩", "전환 후 청약철회", "전환할인", "red", '기존 계약으로 돌아가지만 <b class="red">전환 할인은 다시 받을 수 없음</b>', 3)}
    {lim("3Y", "전환 후 3년 경과", "전환할인", "red", '할인은 3년까지만, 이후에는 5세대 보험료를 <b>전액</b>', 4)}
    {lim("①", "선택형 특약 철회·해지", "선택형", "navy", '<b class="red">다시 가입할 수 없고</b>, 옵션 추가·일부 해지도 불가 · 10년납 등 납입이 끝난 계약은 가입 제한 가능', 5)}
    <div class="lim yel" data-in="2" data-fx="pop" data-d="1.2"><div>기존 계약인지는 <b class="red">실손과 증권번호가 같은지</b>로 판단합니다.</div></div>
  </div>
</div>
"""

def pol(title: str, items: list[tuple[str, str]], at: int, d: float = 0) -> str:
    boxes = "".join(f'<div class="pb {c}">{t}</div>' for t, c in items)
    return f'<div class="pol" data-in="{at}" data-fx="up" data-d="{d}"><div class="pt">{title}</div><div class="pbs">{boxes}</div></div>'

def case(n: int, title: str, body: str, res: str, resc: str, mark: str, why: str, at: int) -> str:
    return f"""<div class="case" data-grp="case" data-in="{at}" data-fx="up">
      <div class="ch"><span class="cn">CASE {n}</span>{title}</div>
      <div class="cbdy">{body}</div>
      <div class="cres {resc}" data-in="{at}" data-fx="pop" data-d="1.2"><i>{mark}</i><b>{res}</b><small>{why}</small></div>
    </div>"""

SCENES["cases"] = f"""
{hd("이렇게 하면", "할인이 사라집니다", "같은 증권의 담보를 줄이거나 해지하면 할인이 적용되지 않습니다.")}
<div class="body">
  <div class="card ex" data-in="0" data-fx="up">
    <div class="ex-l"><b>예시 고객</b><small>(가상)</small><span class="red">증권 A의 실손을 5세대로 계약전환</span></div>
    {pol("증권 A (2008년 종합보험)", [('실손 → 5세대<small>할인 50%</small>', 'hot'), ('암진단비<small>3,000만</small>', ''), ('질병<small>입원일당</small>', '')], 0, 0.3)}
    {pol("증권 B (운전자보험)", [('운전자<small>담보</small>', '')], 0, 0.6)}
  </div>
  <div class="cases">
    {case(1, "암진단비 감액", '같은 증권 A의 암진단비 <s>3,000만</s> → <b>1,000만</b>', "할인 종료", "bad", "✕", "감액도 해지로 봄", 1)}
    {case(2, "입원일당 특약만 해지", '전환 신청 직전 같은 증권 A의 <b>입원일당</b> 해지', "할인 미적용", "bad", "✕", "일부 해지도 해당", 2)}
    {case(3, "운전자보험 해지", '따로 가입한 <b>증권 B</b>(운전자보험) 해지', "할인 유지", "good", "✓", "증권번호가 다름", 3)}
  </div>
  {alert('같은 증권이면 <b class="red">감액이나 일부 해지만 해도 할인이 끝납니다.</b>', 4)}
</div>
"""

SCENES["withdraw"] = f"""
{hd("철회·해지 전에", "꼭 한 번 더 확인", "청약철회는 가능한 기간이 정해져 있고, 철회하면 다시 가입하기 어렵습니다.")}
{char("char6.png")}
<div class="body">
  <div class="card tl">
    <div class="tl-h">01 청약철회 가능 기간</div>
    <div class="tl-bar">
      <div class="tb green-bg" data-in="1" data-fx="left">조건 없이 철회 가능</div>
      <div class="tb orange-bg" data-in="1" data-fx="left" data-d="0.4">보험사고가 없으면 철회 가능</div>
      <div class="tb gray-bg dim" data-in="2" data-fx="left">철회 불가</div>
    </div>
    <div class="tl-ticks"><span>가입</span><span>3개월</span><span>6개월</span></div>
    <div class="mk mk4" data-in="3" data-fx="pop"><b>CASE 4</b> 전환 2개월 차 철회 → <span class="green">철회 가능 (전환 할인 재신청 불가)</span></div>
    <div class="mk mk5" data-in="5" data-fx="pop"><b>CASE 5</b> 4개월 차, 보험금 청구 이력 → <span class="red">보험사고가 있어 철회 불가</span></div>
  </div>
  <div class="flow" data-in="3" data-fx="up" data-d="0.5">
    <div class="fb">1세대 실손</div><i>→</i><div class="fb red-bg w">5세대 전환<small>할인 50%</small></div><i>→</i>
    <div class="fb yel">2개월 차 청약철회</div><i>→</i><div class="fb green-bg w">1세대 실손으로 복귀</div><i>→</i><div class="fb pink red">전환 할인 재신청 불가</div>
  </div>
  <div class="c6" data-in="6" data-fx="up">
    <b>CASE 6 · 선택형 특약은 처음 고른 옵션 그대로</b>
    <span>가입할 때 <em class="ob1">옵션①</em> 선택</span><span>나중에 옵션 추가 → <b class="red">추가 불가</b></span><span>전체 해지 후 재가입 → <b class="red">재가입 불가</b></span>
  </div>
</div>
"""

SCENES["outro"] = f"""
{hd("상담 전", "확인할 것")}
{char("char6.png")}
<div class="body">
  <div class="checks">
    <div data-grp="chk" data-in="1" data-fx="up"><em>1</em>같은 증권의<br>다른 담보</div>
    <div data-grp="chk" data-in="1" data-fx="up" data-d="0.9"><em>2</em>최근 3년 보험료와<br>받은 보험금</div>
    <div data-grp="chk" data-in="1" data-fx="up" data-d="2.6"><em>3</em>도수치료·MRI<br>이용 횟수</div>
    <div data-grp="chk" data-in="1" data-fx="up" data-d="4.0"><em>4</em>철회·재가입 제한<br>안내 여부</div>
  </div>
  {alert('두 제도 모두 <b class="red">의무가 아니며</b>, 보험료가 줄어드는 만큼 <b class="red">보장도 줄어듭니다.</b>', 2)}
  <div class="bye" data-in="3" data-fx="pop">고객에게 맞는지 먼저 확인하고 안내해 주세요 <small>보상은 약관을 참조 부탁드립니다.</small></div>
</div>
"""

CSS = r"""
@font-face{font-family:"Pretendard";src:url("assets/fonts/Pretendard-Regular.otf") format("opentype");font-weight:400;font-style:normal}
@font-face{font-family:"Pretendard";src:url("assets/fonts/Pretendard-Medium.otf") format("opentype");font-weight:500;font-style:normal}
@font-face{font-family:"Pretendard";src:url("assets/fonts/Pretendard-SemiBold.otf") format("opentype");font-weight:600;font-style:normal}
@font-face{font-family:"Pretendard";src:url("assets/fonts/Pretendard-Bold.otf") format("opentype");font-weight:700;font-style:normal}
@font-face{font-family:"Pretendard";src:url("assets/fonts/Pretendard-ExtraBold.otf") format("opentype");font-weight:800;font-style:normal}
@font-face{font-family:"Pretendard";src:url("assets/fonts/Pretendard-Black.otf") format("opentype");font-weight:900;font-style:normal}
:root{--red:#E2352E;--navy:#2D4A8C;--orange:#CF6A2A;--green:#2E9E5B;--gray:#BEB8B6;--ink:#1F1D20;--muted:#6E6668;--bg:#FBEFEF;--card:#FFFFFF;--pinks:#FDE6E4;--blues:#E9EEF8;--yel:#FFF1BF}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:var(--bg);font-family:"Pretendard",sans-serif;color:var(--ink);letter-spacing:-0.02em}
#root{position:relative;width:1920px;height:1080px;overflow:hidden}
#bgfill{position:absolute;inset:0;background:linear-gradient(180deg,#FBEFEF 0%,#FBEFEF 45%,#FAEAEA 100%)}
.red{color:var(--red)}.navy{color:var(--navy)}.orange{color:var(--orange)}.green{color:var(--green)}.gray{color:#8d8583}
.red-bg{background:var(--red);color:#fff}.navy-bg{background:var(--navy);color:#fff}.orange-bg{background:var(--orange);color:#fff}.green-bg{background:var(--green);color:#fff}.gray-bg{background:var(--gray);color:#fff}
.scene{position:absolute;inset:0;width:1920px;height:1080px}
.hd{position:absolute;left:110px;top:58px;width:1250px}
.kicker{font-size:24px;font-weight:600;color:#4b4547;margin-bottom:8px}
.t1{font-size:76px;font-weight:900;line-height:1.08;letter-spacing:-0.035em}
.t2{font-size:66px;font-weight:900;line-height:1.12;color:var(--red);letter-spacing:-0.035em}
.sub{font-size:27px;font-weight:500;color:#3d3739;margin-top:12px}
.char{position:absolute;right:130px;top:30px;width:310px;height:auto;-webkit-mask-image:radial-gradient(ellipse 72% 72% at 50% 50%,#000 72%,transparent 100%);mask-image:radial-gradient(ellipse 72% 72% at 50% 50%,#000 72%,transparent 100%)}
.icon{position:absolute;right:110px;top:40px;width:400px;height:auto;-webkit-mask-image:radial-gradient(ellipse 50% 50% at 50% 50%,#000 62%,transparent 100%);mask-image:radial-gradient(ellipse 50% 50% at 50% 50%,#000 62%,transparent 100%)}
.body{position:absolute;left:110px;right:110px;top:292px;height:552px;display:flex;flex-direction:column;gap:20px}
.card{background:var(--card);border-radius:28px;box-shadow:0 10px 30px rgba(190,60,60,.10)}
.pill{display:inline-block;border-radius:999px;font-weight:800;font-size:30px;padding:12px 30px}
.pill.red{background:var(--red);color:#fff}.pill.navy{background:var(--navy);color:#fff}
.pill.sm{font-size:24px;padding:8px 22px}
.alert{display:flex;align-items:center;gap:22px;background:#fff;border:2px solid #F3C6C3;border-radius:22px;padding:18px 32px;font-size:31px;font-weight:800}
.alert .bang{flex:none;width:50px;height:50px;border-radius:50%;border:4px solid var(--red);color:var(--red);display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:900}
.foot{font-size:20px;color:#7a7173;font-weight:500}.foot.sm{font-size:19px}
/* persistent */
#footer{position:absolute;left:0;right:0;bottom:0;height:62px;background:linear-gradient(90deg,#BF2C27,#C62F29 60%,#BB2A25);display:flex;align-items:center;padding:0 40px;gap:28px;color:#fff}
#footer img{height:44px;width:auto}
#footer .mid{font-size:19px;font-weight:600;opacity:.95}
#footer .rt{margin-left:auto;font-size:18px;font-weight:600;letter-spacing:.06em;opacity:.9}
.chap{position:absolute;left:104px;top:15px;font-size:21px;font-weight:700;color:#5a5254;background:rgba(255,255,255,.85);border-radius:999px;padding:5px 18px}.chap b{color:var(--red);font-weight:900}
.drift{position:absolute;inset:0;transform-origin:50% 45%}
#prog{position:absolute;left:0;right:0;top:0;height:7px;background:rgba(226,53,46,.12)}#progfill{display:block;width:100%;height:7px;background:var(--red);transform-origin:left center}
#edu{position:absolute;right:60px;top:26px;border:2px solid var(--red);color:var(--red);font-size:22px;font-weight:800;padding:4px 14px;background:#fff;border-radius:4px}
#src{position:absolute;left:110px;bottom:72px;font-size:18px;color:#6b6365;font-weight:500}
.cap{position:absolute;left:50%;bottom:112px;transform:translateX(-50%);width:max-content;max-width:1560px;background:rgba(255,255,255,.96);border-radius:18px;padding:14px 30px;font-size:33px;line-height:1.38;font-weight:700;color:#1f1d20;text-align:center;box-shadow:0 6px 20px rgba(0,0,0,.10)}
/* intro */
.intro{position:absolute;inset:0}
.intro-txt{position:absolute;left:130px;top:190px;width:1100px}
.meet{display:inline-block;background:var(--ink);color:#fff;font-size:30px;font-weight:800;padding:10px 26px;border-radius:12px;margin-bottom:26px}
.kicker.big{font-size:30px}
.t1.xl{font-size:112px}.t2.xl{font-size:96px;margin-top:6px}
.pills{display:flex;gap:20px;margin-top:46px}
.char.hero{right:150px;top:170px;width:560px;-webkit-mask-image:radial-gradient(ellipse 50% 50% at 50% 48%,#000 55%,transparent 98%);mask-image:radial-gradient(ellipse 50% 50% at 50% 48%,#000 55%,transparent 98%)}
/* target */
.card.target{flex:1;padding:34px 60px;display:flex;flex-direction:column;align-items:center;border:3px solid #EF8E89}
.mega{font-size:96px;font-weight:900;letter-spacing:-0.045em;margin-top:10px;line-height:1.05}
.mega-sub{font-size:52px;font-weight:900;margin-top:4px}
.hl{background:linear-gradient(180deg,transparent 52%,#FFE680 52%)}
.count{font-size:34px;font-weight:700;margin-top:14px}.count b{font-size:48px;font-weight:900}
.era{position:relative;display:flex;gap:14px;width:100%;margin-top:26px;margin-bottom:40px}
.seg{border-radius:12px;font-size:27px;font-weight:600;padding:16px 0;text-align:center}
.seg.navy-bg{flex:0 0 22%}.seg.red-bg{flex:0 0 28%}.seg.gray-bg{flex:1;color:#6f6869;background:#E4DFDD}
.cut{position:relative;width:4px;border-left:4px dashed var(--ink)}
.cut span{position:absolute;top:auto;bottom:-46px;left:-80px;width:160px;text-align:center;background:var(--ink);color:#fff;font-size:20px;font-weight:800;border-radius:8px;padding:4px 0}
/* systems */
.two{display:flex;gap:28px;flex:1}
.card.sys{flex:1;padding:28px 30px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.sys-name{font-size:44px;font-weight:900;margin-top:12px}.sys-desc{font-size:26px;color:var(--muted);margin-top:6px}
.sys-big{font-size:74px;font-weight:900;letter-spacing:-0.04em;margin-top:6px}.sys-note{font-size:23px;color:var(--muted);margin-top:6px}
.chips3{display:flex;background:#fff;border-radius:22px;box-shadow:0 8px 24px rgba(190,60,60,.08)}
.chips3 div{flex:1;display:flex;flex-direction:column;align-items:center;padding:16px 0;font-size:25px;font-weight:700}
.chips3 div+div{border-left:2px dashed #eadcdc}.chips3 b{font-size:27px;font-weight:900;margin-top:2px}
/* options */
.card.opts{flex:1;padding:28px 40px;display:flex;flex-direction:column;justify-content:center;gap:20px}
.opt{display:flex;align-items:center;gap:26px}
.ob{flex:none;width:96px;height:96px;border-radius:18px;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:46px;font-weight:900;line-height:1}
.ob small{font-size:18px;font-weight:700;margin-bottom:4px}
.ot{flex:0 0 760px;display:flex;flex-direction:column}.ot b{font-size:36px;font-weight:900}.ot span{font-size:21px;color:var(--muted);margin-top:4px}.ot em{font-style:normal;color:var(--red);font-weight:700}
.obar{flex:1;height:40px;background:#FCE3E1;border-radius:999px;overflow:hidden;display:flex}
.obar i{display:block;height:40px;border-radius:999px;transform-origin:left center}
.opct{flex:0 0 190px;font-size:50px;font-weight:900;letter-spacing:-0.04em}
.optall{margin-top:6px;background:#FDEDEC;border-radius:18px;padding:18px 0;text-align:center;font-size:32px;font-weight:800}
.optall span{margin-left:46px;font-size:28px}.optall b{font-size:50px;font-weight:900;margin-left:8px}
/* option1 */
.card.o1{padding:26px 40px 22px;display:flex;flex-direction:column;align-items:center}
.o1-who{font-size:26px;color:var(--muted);font-weight:700}
.o1-row{display:flex;align-items:center;gap:36px;margin-top:14px}
.o1-box{width:600px;height:150px;border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.o1-box.pink{background:var(--pinks)}.o1-box.blue{background:var(--blues)}
.o1-box span{font-size:25px;font-weight:700;color:#3d3739}.o1-box b{font-size:52px;font-weight:900}.o1-box small{font-size:20px;color:var(--muted)}
.gt{font-size:70px;font-weight:900;color:var(--red)}
.o1-say{font-size:34px;font-weight:800;margin-top:14px}
.chips4{display:flex;background:#fff;border-radius:22px;box-shadow:0 8px 24px rgba(190,60,60,.08)}
.chips4 div{flex:1;text-align:center;padding:16px 0;font-size:26px;font-weight:800;display:flex;flex-direction:column}
.chips4 div+div{border-left:2px dashed #eadcdc}.chips4 small{font-size:24px;font-weight:600;color:#3d3739}
/* compare */
.card.cmp{flex:1;padding:16px 44px 12px;display:flex;flex-direction:column;justify-content:space-around}
.grp{display:flex;flex-direction:column;gap:6px}
.tag{display:inline-block;align-self:flex-start;border-radius:8px;font-size:24px;font-weight:900;padding:4px 16px;margin-bottom:2px}.tag.dark{background:var(--ink);color:#fff}
.br{display:flex;align-items:center;gap:22px}
.bl{flex:0 0 250px;text-align:right;display:flex;flex-direction:column}.bl b{font-size:26px;font-weight:800}.bl small{font-size:18px;color:var(--muted)}
.bt{flex:1;display:flex;align-items:center;gap:16px;height:38px}
.bt i{display:block;height:38px;border-radius:0 10px 10px 0;transform-origin:left center}
.bv{font-size:32px;font-weight:900;white-space:nowrap}.bv.gray{color:var(--ink)}
.pp{font-size:22px;font-weight:800;border-radius:8px;padding:3px 12px}
/* male40 */
.card.m40{flex:1;display:flex;padding:26px 50px;gap:50px;align-items:center}
.m40-l{flex:0 0 640px;display:flex;align-items:flex-end;justify-content:center;gap:40px;height:100%;padding-bottom:10px;border-bottom:4px solid #e4dcdc}
.col{display:flex;flex-direction:column;align-items:center;gap:10px}.col>span{font-size:24px;font-weight:800}
.cb{width:170px;border-radius:12px 12px 0 0;display:flex;align-items:flex-start;justify-content:center;transform-origin:center bottom;position:relative}
.cb b{font-size:40px;font-weight:900;margin-top:14px}.cb b.out{position:absolute;top:-62px;color:var(--red)}
.m40-mid{font-size:30px;font-weight:900;color:var(--red);margin-bottom:200px}
.m40-r{flex:1;display:flex;flex-direction:column;gap:16px}
.m40-h{font-size:28px;font-weight:800}
.yrs{display:flex;gap:16px}.yrs div{flex:1;background:var(--pinks);border-radius:16px;padding:14px 0;text-align:center;display:flex;flex-direction:column}
.yrs span{font-size:22px;font-weight:700}.yrs b{font-size:46px;font-weight:900;color:var(--red)}
.sum{background:var(--red);color:#fff;border-radius:18px;text-align:center;font-size:34px;font-weight:800;padding:18px 0}.sum b{font-size:54px;font-weight:900;margin-left:14px}
/* limits */
.lims{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:1fr;gap:16px}
.lim{background:#fff;border-radius:22px;padding:18px 26px;display:flex;gap:20px;align-items:center;box-shadow:0 8px 22px rgba(190,60,60,.08)}
.li{flex:none;width:74px;height:74px;border-radius:50%;background:var(--pinks);color:var(--red);display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:900}
.lt{font-size:31px;font-weight:900}.lim p{font-size:23px;line-height:1.4;margin-top:6px;color:#2c2829}
.tg{font-size:18px;font-weight:800;border-radius:6px;padding:3px 10px;vertical-align:middle;margin-left:6px}
.lim.yel{background:var(--yel);justify-content:center;font-size:29px;font-weight:800;text-align:center}
/* cases */
.card.ex{display:flex;align-items:center;gap:30px;padding:16px 34px}
.ex-l{flex:0 0 330px;display:flex;flex-direction:column;font-size:30px}.ex-l b{font-size:30px}.ex-l small{font-size:20px;color:var(--muted)}.ex-l span{font-size:24px;font-weight:800}
.pol{border:3px solid var(--ink);border-radius:16px;padding:10px 14px}
.pol+.pol{border-color:#9b9496}
.pt{font-size:21px;font-weight:800;margin-bottom:6px}
.pbs{display:flex;gap:10px}
.pb{min-width:170px;border:2px solid #d9d2d2;border-radius:12px;padding:8px 12px;text-align:center;font-size:24px;font-weight:800;display:flex;flex-direction:column}
.pb small{font-size:18px;font-weight:700}.pb.hot{border-color:var(--red);background:#FDECEB;color:var(--red)}
.cases{display:flex;gap:22px;flex:1}
.case{flex:1;background:#fff;border-radius:22px;padding:18px 24px;display:flex;flex-direction:column;gap:10px;box-shadow:0 8px 22px rgba(190,60,60,.08)}
.ch{font-size:29px;font-weight:900;display:flex;align-items:center;gap:12px}
.cn{background:var(--ink);color:#FFD34D;font-size:20px;font-weight:900;border-radius:8px;padding:4px 10px}
.cbdy{font-size:24px;line-height:1.45;flex:1}.cbdy s{color:#9a9293}
.cres{border-radius:16px;border:3px solid;display:flex;flex-direction:column;align-items:center;padding:8px 0}
.cres i{font-style:normal;font-size:30px;font-weight:900}.cres b{font-size:34px;font-weight:900}.cres small{font-size:19px;color:#5b5355}
.cres.bad{border-color:#F0A19D;background:#FFF5F4;color:var(--red)}.cres.good{border-color:#8fd1a8;background:#F1FBF4;color:var(--green)}
/* withdraw */
.char.sm{width:250px}
.card.tl{padding:16px 40px 16px;position:relative;height:250px}
.tl-h{font-size:28px;font-weight:900}
.tl-bar{display:flex;margin-top:62px;height:54px;border-radius:10px;overflow:hidden}
.tb{display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:800;transform-origin:left center}
.tb.green-bg{flex:0 0 38%}.tb.orange-bg{flex:0 0 38%}.tb.dim{flex:1;background:#D3CDCB;color:#fff}
.tl-ticks{position:relative;height:30px;font-size:21px;font-weight:800}
.tl-ticks span{position:absolute;top:6px}.tl-ticks span:nth-child(1){left:0}.tl-ticks span:nth-child(2){left:calc(38% - 30px)}.tl-ticks span:nth-child(3){left:calc(76% - 30px)}
.mk{position:absolute;top:66px;font-size:20px;font-weight:700;background:#fff;border:2px solid var(--ink);border-radius:10px;padding:4px 12px;white-space:nowrap}
.mk4{left:150px}.mk5{left:820px;border-color:var(--red)}
.mk{top:58px}.mk4{top:58px}
.flow{display:flex;align-items:center;gap:10px}
.fb{flex:1;background:#ECE8E7;border-radius:14px;text-align:center;padding:14px 4px;font-size:24px;font-weight:800;display:flex;flex-direction:column;justify-content:center;min-height:86px}
.fb small{font-size:18px}.fb.red-bg{background:var(--red);color:#fff}.fb.green-bg{background:var(--green);color:#fff}.fb.yel{background:var(--yel)}.fb.pink{background:var(--pinks)}
.flow i{font-style:normal;font-size:30px;color:#9c9496;font-weight:900}
.c6{background:#fff;border-radius:20px;padding:16px 28px;display:flex;align-items:center;gap:26px;font-size:24px;font-weight:700;box-shadow:0 8px 22px rgba(190,60,60,.08)}
.c6>b{font-size:25px;font-weight:900}.c6 span{background:#FDF0EF;border-radius:12px;padding:10px 16px}
.ob1{font-style:normal;background:var(--red);color:#fff;border-radius:8px;padding:2px 10px;font-weight:900}
/* outro */
.checks{display:flex;gap:20px;flex:1}
.checks div{flex:1;background:#fff;border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-size:31px;font-weight:800;line-height:1.35;box-shadow:0 8px 22px rgba(190,60,60,.08)}
.checks em{font-style:normal;width:64px;height:64px;border-radius:50%;background:var(--red);color:#fff;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:900;margin-bottom:14px}
.bye{text-align:center;font-size:34px;font-weight:900}.bye small{display:block;font-size:22px;font-weight:600;color:var(--muted);margin-top:4px}
"""

FX = r"""
const SC = window.__SCENES__;
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
const ease = "power3.out";
for (const sc of SC) {
  const root = document.getElementById(sc.id);
  tl.fromTo(root, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: "power1.out" }, sc.start);
  tl.to(root, { opacity: 0, duration: 0.4, ease: "power1.in" }, sc.start + sc.len - 0.42);
  const drift = root.querySelector(".drift");
  tl.fromTo(drift, { scale: 1 }, { scale: 1.018, duration: sc.len, ease: "none" }, sc.start);
  const groups = {};
  root.querySelectorAll("[data-in]").forEach((el) => {
    const k = parseInt(el.dataset.in, 10);
    const base = k === 0 ? sc.start + 0.25 : sc.start + sc.lead + sc.lines[Math.min(k, sc.lines.length - 1)] - 0.2;
    const t = base + parseFloat(el.dataset.d || "0");
    const fx = el.dataset.fx || "up";
    if (el.dataset.grp) (groups[el.dataset.grp] = groups[el.dataset.grp] || []).push({ el, t });
    if (fx === "up") tl.fromTo(el, { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: 0.6, ease }, t);
    else if (fx === "fade") tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.6 }, t);
    else if (fx === "pop") tl.fromTo(el, { opacity: 0, scale: 0.86 }, { opacity: 1, scale: 1, duration: 0.55, ease: "back.out(1.6)" }, t);
    else if (fx === "left") tl.fromTo(el, { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.6, ease }, t);
    else if (fx === "grow") tl.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "power2.out" }, t);
    else if (fx === "rise") tl.fromTo(el, { scaleY: 0 }, { scaleY: 1, duration: 0.9, ease: "power2.out" }, t);
    else if (fx === "char") {
      tl.fromTo(el, { opacity: 0, y: 40, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease }, t);
      const breathe = Math.max(0, Math.floor((sc.len - 1.5) / 3) - 1);
      tl.to(el, { y: -10, duration: 1.5, ease: "sine.inOut", yoyo: true, repeat: breathe * 2 + 1 }, t + 0.8);
    }
  });
  const restore = sc.start + sc.len - 2.4;
  for (const g of Object.values(groups)) {
    g.sort((a, b) => a.t - b.t);
    for (let i = 1; i < g.length; i++) {
      const prev = g.slice(0, i).map((x) => x.el);
      tl.to(prev, { opacity: 0.42, duration: 0.45, ease: "power1.out" }, g[i].t + 0.1);
    }
    const last = g[g.length - 1].t;
    if (g.length > 1 && restore > last + 1.2) tl.to(g.map((x) => x.el), { opacity: 1, duration: 0.5 }, restore);
  }
}
tl.fromTo("#progfill", { scaleX: 0 }, { scaleX: 1, duration: window.__TOTAL__, ease: "none" }, 0);
for (const c of window.__CAPS__) {
  const el = document.getElementById(c.id);
  tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.2 }, c.start);
}
tl.to("#bgm", { volume: 0, duration: 2.5 }, window.__TOTAL__ - 2.6);
window.__timelines["main"] = tl;
"""


def main() -> int:
    timing = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    ws = Path(sys.argv[2])
    t = 0.0
    scenes_js, caps_js, sections, audios, caps = [], [], [], [], []
    for i, sc in enumerate(timing["scenes"]):
        lead = 1.2 if i == 0 else LEAD
        length = round(lead + sc["dur"] + TAIL, 3)
        sid = f"s-{sc['id']}"
        chap = ""
        if sc["id"] in CHAPTERS:
            chap = f'<div class="chap"><b>{i:02d}</b> / {len(timing["scenes"]) - 1:02d} · {CHAPTERS[sc["id"]]}</div>'
        sections.append(
            f'<section id="{sid}" class="clip scene" data-start="{t:.3f}" data-duration="{length:.3f}" data-track-index="1">'
            f'{chap}<div class="drift">{SCENES[sc["id"]]}</div></section>'
        )
        audios.append(
            f'<audio id="vo-{sc["id"]}" src="assets/{sc["id"]}.wav" data-start="{t + lead:.3f}" '
            f'data-duration="{sc["dur"]:.3f}" data-track-index="10" data-volume="1"></audio>'
        )
        for j, ln in enumerate(sc["lines"]):
            cs = t + lead + ln["start"]
            nxt = sc["lines"][j + 1]["start"] if j + 1 < len(sc["lines"]) else sc["dur"] + 0.4
            cd = max(0.5, (lead + nxt) - (lead + ln["start"]) - 0.05)
            cid = f"cap-{sc['id']}-{j}"
            caps.append(
                f'<div id="{cid}" class="clip cap" data-start="{cs:.3f}" data-duration="{cd:.3f}" data-track-index="2">{e(ln["show"])}</div>'
            )
            caps_js.append({"id": cid, "start": round(cs, 3)})
        scenes_js.append({"id": sid, "start": round(t, 3), "len": length, "lead": lead, "lines": [ln["start"] for ln in sc["lines"]]})
        t += length
    total = round(t + 0.3, 3)
    doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>실손 할인 제도 교육</title>
<script src="assets/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-duration="{total}" data-fps="30">
<div id="bgfill"></div>
{''.join(sections)}
{''.join(caps)}
<div id="prog"><i id="progfill"></i></div>
<div id="edu">교육용</div>
<div id="src">{e(SOURCE)}</div>
<div id="footer"><img src="assets/logo.png" alt="meritz 메리츠화재"><span class="mid">내부 설계사 교육용 · 외부 배포·게시 금지 · 보상은 약관을 참조 부탁드립니다 · 내레이션은 AI 음성</span><span class="rt">MERITZ STANDARD SALES BOOK</span></div>
{''.join(audios)}
<audio id="bgm" src="assets/bgm.mp3" data-start="0" data-duration="{total}" data-track-index="11" data-volume="0.07"></audio>
</div>
<script>
window.__SCENES__ = {json.dumps(scenes_js)};
window.__CAPS__ = {json.dumps(caps_js)};
window.__TOTAL__ = {total};
{FX}
</script>
</body>
</html>
"""
    (ws / "index.html").write_text(doc, encoding="utf-8")
    (ws / "hyperframes.json").write_text(json.dumps({"name": "seoul-info-silson-discount"}), encoding="utf-8") if not (ws / "hyperframes.json").exists() else None
    print(f"index.html : 장면 {len(sections)}개 · 자막 {len(caps)}개 · 길이 {total}초 ({total/60:.2f}분)")
    print(json.dumps([(s["id"], s["start"]) for s in scenes_js], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
